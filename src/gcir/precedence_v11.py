"""Phase-aware precedence resolution over a schema-v1.1 bundle.

This module is additive to ``gcir.precedence``: ``resolve()`` there remains the
correct resolver for a bundle that uses no v1.1 field, and is what
``resolve_phase_aware`` here delegates to for the ordinary case.  What this
module adds is exactly what a v1.1 predicate can now declare that ``resolve()``
has no vocabulary for:

  * ``enforcement_phase`` -- only PRE_AUTHORIZATION and BOUNDARY_REVALIDATION
    predicates contribute to the authorization decision; a
    POST_AUTH_PRE_ACTUATION predicate can still block release without changing
    the authorization decision itself (Section VI-A step 9).
  * ``evaluation_latency_bound`` / ``on_evaluation_timeout`` -- an evaluator
    that does not signal completion inside its bound resolves HOLD, never a
    partial permit, regardless of what outcome its condition would otherwise
    have produced.
  * ``state_binding`` -- a digest mismatch between authorization time and the
    execution boundary is HOLD (INV-STATE-BINDING), independent of the
    predicate's own pass/fail outcome.
  * ``concurrence_policy`` -- all-or-nothing N-of-M attestation with a fixed
    DENY-on-expiry response; partial concurrence never accrues.

``safe_state`` is computed exactly once, via ``gcir.models.safe_state_of``, at
the point each branch below returns -- there is no second place in this module
where a decision and its safe_state could fall out of step.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from . import precedence as precedence_v10
from .models import CONCURRENCE_EXPIRY_FIXED_RESPONSE, PrecedenceError, safe_state_of

#: Evaluation-entry keys this resolver understands, beyond the v1.0
#: ``{"outcome": "pass"|"fail"|"unknown"}``.  All are optional; a predicate
#: that declares no v1.1 field never looks at them.
_EVALUATION_KEYS = (
    "outcome",
    "timed_out",
    "state_digest_match",
    "concurrence_attestations",
    "concurrence_window_expired",
)


def _phase_of(predicate):
    """A predicate with no declared ``enforcement_phase`` is PRE_AUTHORIZATION
    (v1.0 backward compatibility -- see ``models.PERMIT_ELIGIBLE_PHASES``)."""
    return predicate.get("enforcement_phase") or "PRE_AUTHORIZATION"


def _special_case_outcome(predicate, evaluation):
    """Resolve the v1.1-specific overrides for one predicate's evaluation.

    Returns ``None`` if no v1.1 mechanism on this predicate overrides the
    ordinary outcome (the caller then falls back to the plain
    ``evaluation["outcome"]``), or a tuple
    ``(effective_outcome, forced_class, note)`` where ``forced_class`` is one
    of ``None`` (let normal mandatory/weighted classification apply to
    ``effective_outcome``), ``"HOLD"`` or ``"DENY"`` (the class is forced
    regardless of gate type, because these are compiler-invariant-style
    conditions that apply uniformly).
    """
    bound = predicate.get("evaluation_latency_bound")
    if bound is not None and evaluation.get("timed_out"):
        return (
            "unknown",
            "HOLD",
            "evaluator did not signal completion within evaluation_latency_bound "
            "(%s %s); on_evaluation_timeout = HOLD, never a partial permit"
            % (bound["value"], bound["unit"]),
        )

    binding = predicate.get("state_binding")
    if binding is not None and evaluation.get("state_digest_match") is False:
        mismatch_response = binding.get("mismatch_response", "HOLD")
        return (
            "unknown" if mismatch_response == "HOLD" else "fail",
            mismatch_response,
            "state digest at the execution boundary does not match the digest at "
            "authorization time over %s (INV-STATE-BINDING); signed policy "
            "response is %s%s"
            % (
                binding["attributes"], mismatch_response,
                "" if mismatch_response == "HOLD" else " (explicit signed override, not the HOLD default)",
            ),
        )

    policy = predicate.get("concurrence_policy")
    if policy is not None:
        attestations = evaluation.get("concurrence_attestations", 0)
        if attestations >= policy["n_required"]:
            return ("pass", None, None)
        if evaluation.get("concurrence_window_expired"):
            return (
                "fail",
                CONCURRENCE_EXPIRY_FIXED_RESPONSE,
                "concurrence window expired with %d/%d attestations; "
                "concurrence_expiry_response is fixed DENY, never an evaluator "
                "timeout" % (attestations, policy["n_required"]),
            )
        return (
            "unknown",
            "HOLD",
            "concurrence pending: %d/%d attestations, window not yet expired"
            % (attestations, policy["n_required"]),
        )

    return None


def resolve_phase_aware(bundle, evaluations):
    """Resolve a v1.1-aware decision over ``{gcir_id: evaluation}``.

    ``evaluation`` is either the v1.0 shape ``{"outcome": "pass"|"fail"|"unknown"}``
    or additionally carries any of ``_EVALUATION_KEYS``.  Returns the same
    verdict shape as ``gcir.precedence.resolve`` (``decision`` in
    ``{PERMIT, DENY, HOLD}``, ``safe_state = decision != PERMIT``), plus:

      * ``release_blocked`` (bool) and ``release_block_reason`` -- set when
        authorization is PERMIT but a POST_AUTH_PRE_ACTUATION predicate's
        evaluation failed: interlock release is blocked without the
        authorization decision itself becoming DENY (PERMIT does not force
        execution; Section II).
      * ``excluded_from_authorization`` -- the gcir_ids of POST_AUTH_PRE_ACTUATION
        and POST_EVENT_AUDIT predicates that were evaluated but never entered
        the authorization aggregate.
    """
    predicates_by_id = {p["gcir_id"]: p for p in bundle.predicates}
    gate_map = bundle.gate_map

    pre_auth_outcomes: Dict[str, str] = {}
    forced: Dict[str, Dict[str, Any]] = {}
    post_auth_ids: List[str] = []
    post_event_ids: List[str] = []

    for gcir_id, evaluation in evaluations.items():
        predicate = predicates_by_id.get(gcir_id)
        if predicate is None:
            raise PrecedenceError(
                "evaluation supplied for unknown predicate %r" % gcir_id,
                code="UNKNOWN_PREDICATE",
            )
        phase = _phase_of(predicate)

        if phase == "POST_AUTH_PRE_ACTUATION":
            post_auth_ids.append(gcir_id)
            continue
        if phase == "POST_EVENT_AUDIT":
            post_event_ids.append(gcir_id)
            continue

        # PRE_AUTHORIZATION or BOUNDARY_REVALIDATION: contributes to PERMIT.
        special = _special_case_outcome(predicate, evaluation)
        if special is not None:
            effective_outcome, forced_class, note = special
            pre_auth_outcomes[gcir_id] = effective_outcome
            if forced_class is not None:
                forced[gcir_id] = {"class": forced_class, "note": note}
        else:
            pre_auth_outcomes[gcir_id] = evaluation["outcome"]

    # Resolve the authorization stage.  Reuse gcir.precedence's classification
    # for anything not forced by a v1.1 mechanism above, so PRE_AUTHORIZATION /
    # BOUNDARY_REVALIDATION predicates without any v1.1 field behave exactly as
    # they did under the v1.0 resolver.
    classified = []
    for gcir_id in sorted(pre_auth_outcomes):
        predicate = predicates_by_id[gcir_id]
        gate_entry = gate_map[gcir_id]
        if gcir_id in forced:
            klass = (
                "mandatory_failure"
                if gate_entry["gate_type"] == "mandatory"
                else "weighted_or_advisory"
            )
        else:
            klass = precedence_v10.classify_outcome(
                predicate, gate_entry, pre_auth_outcomes[gcir_id]
            )
        classified.append(
            {
                "gcir_id": gcir_id,
                "gate_type": gate_entry["gate_type"],
                "gate_source": gate_entry["gate_source"],
                "outcome": pre_auth_outcomes[gcir_id],
                "precedence_class": klass,
                "forced": forced.get(gcir_id),
            }
        )

    failures = [c for c in classified if c["precedence_class"] == "mandatory_failure"]
    if failures:
        # A forced-DENY (expired concurrence) or forced-HOLD (timeout/state
        # mismatch) among the failures decides the outcome outright: these are
        # compiler-invariant-style conditions, not ordinary evidence the
        # unknown/escalation heuristic below should re-derive.
        forced_denies = [f for f in failures if f["forced"] and f["forced"]["class"] == "DENY"]
        forced_holds = [f for f in failures if f["forced"] and f["forced"]["class"] == "HOLD"]
        if forced_denies:
            decision = "DENY"
            reason = "; ".join(
                "%s: %s" % (f["gcir_id"], f["forced"]["note"]) for f in forced_denies
            )
        elif forced_holds:
            decision = "HOLD"
            reason = "; ".join(
                "%s: %s" % (f["gcir_id"], f["forced"]["note"]) for f in forced_holds
            )
        else:
            decision = precedence_v10._classify_exact_outcome(
                failures, classified, predicates_by_id
            )
            reason = "mandatory gate(s) %s failed" % ", ".join(
                sorted(f["gcir_id"] for f in failures)
            )
        result = {
            "decision": decision,
            "exact_outcome": decision,
            "safe_state": safe_state_of(decision),
            "deciding_class": "mandatory_failure",
            "reason": reason,
            "contributions": classified,
        }
        if decision == "HOLD":
            for failure in failures:
                if failure["forced"] and failure["forced"]["class"] == "HOLD":
                    result["escalation_route"] = None
                    result["escalation_sla_hours"] = None
                    break
                pred = predicates_by_id[failure["gcir_id"]]
                if pred.get("escalation"):
                    result["escalation_route"] = pred["escalation"]["route"]
                    result["escalation_sla_hours"] = pred["escalation"].get("sla_hours")
                    break
    else:
        decision = "PERMIT"
        result = {
            "decision": decision,
            "exact_outcome": decision,
            "safe_state": safe_state_of(decision),
            "deciding_class": "mandatory_pass",
            "reason": "no mandatory gate failed in the PRE_AUTHORIZATION / "
            "BOUNDARY_REVALIDATION aggregate",
            "contributions": classified,
        }

    # --- Three independent axes, never collapsed into one another or into a
    # fourth peer decision (Section VI-A step 9 / VIII):
    #
    #   authorization_decision  in {PERMIT, DENY, HOLD}   -- exactly precedence's
    #                                                          existing vocabulary
    #   release_decision        in {ALLOW_RELEASE, BLOCK_RELEASE} -- set by a
    #                                                          POST_AUTH_PRE_ACTUATION
    #                                                          predicate; meaningful
    #                                                          only when authorization
    #                                                          itself was PERMIT
    #   next_authorization_effect in {NONE, HOLD_NEXT_AUTH} -- set by a
    #                                                          POST_EVENT_AUDIT
    #                                                          predicate; a record of
    #                                                          the event, not a gate on
    #                                                          the event it audits
    #
    # ``decision``/``exact_outcome`` are kept as aliases of
    # ``authorization_decision`` for callers written against the v1.0-shaped
    # resolver (gcir.precedence.resolve returns the same three keys).
    result["authorization_decision"] = result["decision"]

    result["release_decision"] = "ALLOW_RELEASE"
    result["release_block_reason"] = None
    if result["authorization_decision"] == "PERMIT":
        for gcir_id in sorted(post_auth_ids):
            evaluation = evaluations[gcir_id]
            outcome = evaluation.get("outcome")
            if outcome != "pass":
                result["release_decision"] = "BLOCK_RELEASE"
                result["release_block_reason"] = (
                    "POST_AUTH_PRE_ACTUATION predicate %s did not pass (outcome=%r); "
                    "interlock release is blocked. Authorization was correctly "
                    "PERMIT and is not retroactively DENY; PERMIT does not force "
                    "execution (Section II)." % (gcir_id, outcome)
                )
                break
    # Backward-compatible alias for existing callers/tests.
    result["release_blocked"] = result["release_decision"] == "BLOCK_RELEASE"

    result["next_authorization_effect"] = "NONE"
    result["next_authorization_effect_reason"] = None
    for gcir_id in sorted(post_event_ids):
        evaluation = evaluations[gcir_id]
        outcome = evaluation.get("outcome")
        if outcome != "pass":
            predicate = predicates_by_id[gcir_id]
            result["next_authorization_effect"] = "HOLD_NEXT_AUTH"
            result["next_authorization_effect_reason"] = (
                "POST_EVENT_AUDIT predicate %s did not pass (outcome=%r): %s. "
                "This never gates the event it audits; it places HOLD on the "
                "next ordinary authorization in the affected scope."
                % (gcir_id, outcome, predicate.get("decision_semantics", ""))
            )
            break

    result["excluded_from_authorization"] = sorted(post_auth_ids + post_event_ids)

    # ``safe_state`` is, and remains, a pure function of authorization_decision
    # alone (models.safe_state_of) -- release_decision and
    # next_authorization_effect must never feed back into it. A TOCTOU-style
    # scenario (PERMIT correctly granted, release then blocked) is the load-
    # bearing case this asserts: safe_state stays False, because the
    # authorization itself was correct; the externalization-preventing work is
    # release_decision's job, reported separately below.
    assert result["safe_state"] == safe_state_of(result["authorization_decision"]), (
        "safe_state must be a pure function of authorization_decision; got "
        "safe_state=%r for authorization_decision=%r"
        % (result["safe_state"], result["authorization_decision"])
    )

    # Two clearly-named, non-overloaded companions to safe_state (never merged
    # into it): whether the release axis itself is in a non-permissive state,
    # and whether externalization is in fact prevented this decision. Both are
    # independent of, and may disagree with, authorization safe_state -- that
    # disagreement (safe_state=False, release_safe=True) is exactly what a
    # correct PERMIT-then-BLOCK_RELEASE case looks like.
    result["release_safe"] = result["release_decision"] != "ALLOW_RELEASE"
    result["externalization_blocked"] = (
        result["authorization_decision"] != "PERMIT" or result["release_decision"] != "ALLOW_RELEASE"
    )
    return result
