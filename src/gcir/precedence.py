"""Policy conflict and precedence (manuscript Section VI-D).

    mandatory failure  >  mandatory pass  >  weighted/advisory result

    "No weighted or advisory result may override a mandatory failure.  Conflicts
     among applicable mandatory policies are themselves indeterminate and produce
     SAFE_STATE unless a unique precedence relation is present in the approved
     policy metadata."

This module is a *static* resolver over a compiled bundle plus a set of condition
outcomes.  It is not a runtime enforcement engine -- the manuscript is explicit
that enforcement belongs to the consuming authority and is not restated here.
What is implemented is exactly the precedence semantics Phi must be able to
guarantee about the bundles it emits.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import PrecedenceError, safe_state_of

#: Ordered strongest-first.  Index is the precedence rank.
PRECEDENCE_ORDER = ("mandatory_failure", "mandatory_pass", "weighted_or_advisory")

OUTCOMES = ("pass", "fail", "unknown")


def classify_outcome(predicate, gate_entry, outcome):
    """Map a (gate type, condition outcome) pair onto a precedence class.

    ``unknown`` is resolved through the predicate's own ``on_unknown``, which for
    a mandatory gate the compiler has already forced to ``fail``.
    """
    if outcome not in OUTCOMES:
        raise PrecedenceError(
            "outcome %r is outside {pass, fail, unknown}" % outcome,
            code="OUTCOME_UNKNOWN",
        )
    gate_type = gate_entry["gate_type"]

    if outcome == "unknown":
        resolved = _resolve_unknown(predicate)
    else:
        resolved = outcome

    if gate_type == "mandatory":
        return "mandatory_failure" if resolved == "fail" else "mandatory_pass"
    return "weighted_or_advisory"


def _resolve_unknown(predicate):
    """A predicate's declared ``on_unknown`` for its strictest condition."""
    responses = {c["on_unknown"] for c in predicate["context_conditions"]}
    if "fail" in responses:
        return "fail"
    if "warn" in responses:
        return "pass"
    return "pass"


def resolve(bundle, outcomes):
    """Resolve a decision over ``{gcir_id: outcome}`` and return a verdict.

    Returns a dict with ``decision`` in {PERMIT, DENY, HOLD}, where:
    - PERMIT: all mandatory conditions satisfied, safe_state=false
    - DENY: mandatory failure (known fail or no escalation), safe_state=true
    - HOLD: unknown evidence + valid escalation route, safe_state=true
    Also includes exact_outcome (alias), escalation_route (if HOLD).
    """
    gate_map = bundle.gate_map
    predicates = {p["gcir_id"]: p for p in bundle.predicates}

    classified = []
    for gcir_id in sorted(outcomes):
        predicate = predicates.get(gcir_id)
        if predicate is None:
            raise PrecedenceError(
                "outcome supplied for unknown predicate %r" % gcir_id,
                code="UNKNOWN_PREDICATE",
            )
        klass = classify_outcome(predicate, gate_map[gcir_id], outcomes[gcir_id])
        classified.append(
            {
                "gcir_id": gcir_id,
                "gate_type": gate_map[gcir_id]["gate_type"],
                "gate_source": gate_map[gcir_id]["gate_source"],
                "outcome": outcomes[gcir_id],
                "precedence_class": klass,
                "policy_id": predicate.get("policy_id"),
            }
        )

    failures = [c for c in classified if c["precedence_class"] == "mandatory_failure"]
    if failures:
        conflict = _mandatory_conflict(failures, classified, bundle)
        if conflict is not None:
            decision = "DENY"
            return {
                "decision": decision,
                "exact_outcome": decision,
                "safe_state": safe_state_of(decision),
                "deciding_class": "indeterminate_mandatory_conflict",
                "reason": conflict,
                "contributions": classified,
            }

        # Classify failure as DENY or HOLD
        decision = _classify_exact_outcome(failures, classified, predicates)
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

        # If HOLD, include escalation route
        if decision == "HOLD":
            for failure in failures:
                pred = predicates[failure["gcir_id"]]
                if pred.get("escalation"):
                    result["escalation_route"] = pred["escalation"]["route"]
                    result["escalation_sla_hours"] = pred["escalation"].get("sla_hours")
                    break

        return result

    # No mandatory failure: PERMIT
    advisory = [
        c for c in classified if c["precedence_class"] == "weighted_or_advisory"
    ]
    decision = "PERMIT"
    return {
        "decision": decision,
        "exact_outcome": decision,
        "safe_state": safe_state_of(decision),
        "deciding_class": "mandatory_pass",
        "reason": "no mandatory gate failed; %d weighted/advisory result(s) do not "
        "override a mandatory pass" % len(advisory),
        "contributions": classified,
    }


def _classify_exact_outcome(failures, classified, predicates):
    """Classify mandatory failure as DENY or HOLD.

    HOLD: Unknown evidence + valid escalation route exists
    DENY: Known failure (outcome='fail') OR no escalation route
    """
    for failure in failures:
        if failure["outcome"] == "unknown":
            pred = predicates.get(failure["gcir_id"])
            if pred and pred.get("escalation"):
                return "HOLD"
    return "DENY"


def _mandatory_conflict(failures, classified, bundle):
    """Detect an indeterminate conflict among applicable mandatory policies.

    A conflict exists when two mandatory predicates in the same declared
    ``conflict_group`` disagree (one fails, one passes) and the approved policy
    metadata supplies no unique precedence relation over that group.
    """
    predicates = {p["gcir_id"]: p for p in bundle.predicates}
    groups = {}
    for entry in classified:
        if entry["gate_type"] != "mandatory":
            continue
        group = predicates[entry["gcir_id"]].get("conflict_group")
        if group is None:
            continue
        groups.setdefault(group, []).append(entry)

    metadata = bundle.payload.get("policy_metadata", {}).get("precedence", {})
    for group in sorted(groups):
        members = groups[group]
        classes = {m["precedence_class"] for m in members}
        if len(classes) < 2:
            continue
        rule = metadata.get(group)
        if rule is None or not _is_unique_total_order(rule, [m["gcir_id"] for m in members]):
            return (
                "mandatory policies in conflict_group %r disagree and the approved "
                "policy metadata supplies no unique precedence relation over %s"
                % (group, sorted(m["gcir_id"] for m in members))
            )
    return None


def _is_unique_total_order(rule, members):
    """A precedence relation is usable only if it totally orders the members with
    no ties."""
    order = rule.get("order")
    if not isinstance(order, list):
        return False
    if len(order) != len(set(order)):
        return False
    return set(members).issubset(set(order))
