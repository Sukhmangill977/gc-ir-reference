"""Auxiliary checks A1-A4 (schema v1.1).

These formalize four runtime-enforcement ideas the manuscript describes
(actor-scope revocation, safety-layer intervention correlation, delegation
containment, and human-response coverage for advisory permits) that an
earlier draft of this artifact used as the literal definition of canonical
Q7-Q10, before a documented correction (``docs/V1_0_4_SCIENTIFIC_RECONCILIATION_AUDIT.md``)
replaced Q7-Q10 with the structural-integrity queries in ``gcir.audit_queries``.
That correction stands: A1-A4 are auxiliary checks over runtime evidence, never
a replacement for canonical Q1-Q10, and they are versioned and reported
separately from them everywhere in this codebase.

Every check below operates on plain evidence records (dicts matching
``schemas/actor_scope_revocation.schema.json`` etc.), not on the compiled
bundle payload -- exactly like ``gcir.lifecycle``'s ``valid_at``, these are
runtime-side checks over signed records that live outside the hashed payload.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .temporal import parse_time


# ---------------------------------------------------------------------------
# A1: actor-scope revocation validity
# ---------------------------------------------------------------------------


def _tuple_key(action_tuple: Dict[str, str]) -> Tuple[str, str, str, str]:
    return (
        action_tuple["subject"],
        action_tuple["action"],
        action_tuple["resource"],
        action_tuple["destination"],
    )


def a1_actor_scope_revocation_validity(
    actuations: List[Dict[str, Any]],
    revocations: List[Dict[str, Any]],
) -> Tuple[bool, List[str]]:
    """A1: no ``AuthorizedActuation`` proceeded under an actor-scope tuple that
    was already revoked at its ``authorization_time``.

    ``actuations``: ``{"actor_id", "action_tuple", "authorization_time"}``.
    ``revocations``: ``ActorScopeRevocation`` records (``actor_id``, ``scope``
    -- a list of action tuples, ``effective_time``).

    A revocation withdraws one actor's authority over one scope from one
    effective time without touching the compiled bundle (Section VI-F); this
    check is the mechanical query the manuscript names for that withdrawal.
    """
    by_actor: Dict[str, List[Dict[str, Any]]] = {}
    for revocation in revocations:
        by_actor.setdefault(revocation["actor_id"], []).append(revocation)

    issues = []
    for actuation in actuations:
        actor_id = actuation["actor_id"]
        tuple_key = _tuple_key(actuation["action_tuple"])
        authorization_time = parse_time(actuation["authorization_time"])
        for revocation in by_actor.get(actor_id, []):
            if tuple_key not in {_tuple_key(t) for t in revocation["scope"]}:
                continue
            if authorization_time >= parse_time(revocation["effective_time"]):
                issues.append(
                    "actuation by %s over %s authorized at %s, at or after "
                    "revocation %s effective at %s"
                    % (actor_id, tuple_key, actuation["authorization_time"],
                       revocation.get("record_type", "ActorScopeRevocation"),
                       revocation["effective_time"])
                )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# A2: SafetyEvent standing-origin / correlation validity
# ---------------------------------------------------------------------------


def a2_safety_event_correlation_validity(
    safety_events: List[Dict[str, Any]],
    declared_safety_layers: List[str],
    bundle_payload_hash: str,
) -> Tuple[bool, List[str]]:
    """A2: every SafetyEvent carries standing origin, cites a declared safety
    layer, and correlates to the bundle actually in force.

    A SafetyEvent is never gated by the authorization layer -- it is logged
    with standing authority (INV-SAFETY-RECOVERY) and audited post-event
    (Section VI-B, VIII).  This check verifies the record itself is
    well-formed evidence of that standing intervention, not that the
    intervention was "permitted" (it never needs permission).
    """
    issues = []
    for event in safety_events:
        event_id = event.get("safety_event_id", "<unknown>")
        if event.get("origin") != "INV-SAFETY-RECOVERY":
            issues.append("%s: origin=%r, expected INV-SAFETY-RECOVERY (standing authority)" % (event_id, event.get("origin")))
        if event.get("safety_layer_id") not in declared_safety_layers:
            issues.append(
                "%s: safety_layer_id %r is not among the declared safety layers %s"
                % (event_id, event.get("safety_layer_id"), declared_safety_layers)
            )
        if event.get("correlated_bundle_hash") != bundle_payload_hash:
            issues.append(
                "%s: correlated_bundle_hash %s does not match the authorization "
                "state in force (%s)"
                % (event_id, event.get("correlated_bundle_hash"), bundle_payload_hash)
            )
    return len(issues) == 0, issues


def a2_missing_safety_correlation(
    interventions: List[Dict[str, Any]],
    safety_events: List[Dict[str, Any]],
    recording_window_seconds: float,
) -> Tuple[bool, List[str]]:
    """The companion post-event obligation: every declared intervention has a
    signed SafetyEvent recorded within its declared window; a missing
    correlation places HOLD on the next ordinary authorization in the
    affected scope (Section VIII) -- this function reports which
    interventions are missing that correlation, which is the input to that
    HOLD, not the HOLD decision itself (that belongs to the runtime
    authority, out of this artifact's scope)."""
    correlated_at = {
        event.get("correlated_permit_id"): parse_time(event["effective_time"])
        for event in safety_events
        if event.get("correlated_permit_id")
    }
    issues = []
    for intervention in interventions:
        permit_id = intervention.get("correlated_permit_id")
        event_time = correlated_at.get(permit_id)
        intervention_time = parse_time(intervention["effective_time"])
        if event_time is None:
            issues.append(
                "intervention at %s (permit %s) has no correlated SafetyEvent"
                % (intervention["effective_time"], permit_id)
            )
        elif (event_time - intervention_time).total_seconds() > recording_window_seconds:
            issues.append(
                "intervention at %s (permit %s) correlated at %s, exceeding the "
                "%ss recording window"
                % (intervention["effective_time"], permit_id, event_time, recording_window_seconds)
            )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# A3: delegation / child-permit containment
# ---------------------------------------------------------------------------


def a3_delegation_containment(child: Dict[str, Any], parent: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """A3 (INV-DELEGATION-NARROWING): a child permit's ``(scope, validity,
    actions)`` composite is contained on every component in the parent's, and
    strictly smaller on at least one -- an identical child is not a delegation."""
    issues = []
    child_scope, parent_scope = set(child["scope"]), set(parent["scope"])
    child_actions, parent_actions = set(child["actions"]), set(parent["actions"])

    if not child_scope.issubset(parent_scope):
        issues.append("child scope %s is not contained in parent scope %s" % (sorted(child_scope), sorted(parent_scope)))
    if not child_actions.issubset(parent_actions):
        issues.append("child actions %s are not contained in parent actions %s" % (sorted(child_actions), sorted(parent_actions)))

    child_from = parse_time(child["validity"]["effective_from"])
    parent_from = parse_time(parent["validity"]["effective_from"])
    child_until = child["validity"].get("effective_until")
    parent_until = parent["validity"].get("effective_until")
    if child_from < parent_from:
        issues.append("child validity starts %s before parent validity starts %s" % (child["validity"]["effective_from"], parent["validity"]["effective_from"]))
    if parent_until is not None:
        if child_until is None or parse_time(child_until) > parse_time(parent_until):
            issues.append("child validity does not end at or before parent validity end %s" % parent_until)

    if issues:
        return False, issues

    strictly_smaller = (
        child_scope < parent_scope
        or child_actions < parent_actions
        or child_from > parent_from
        or (parent_until is not None and (child_until is None or parse_time(child_until) < parse_time(parent_until)))
        or (parent_until is None and child_until is not None)
    )
    if not strictly_smaller:
        return False, ["child composite (scope, validity, actions) equals the parent's -- an identical child is not a delegation (INV-DELEGATION-NARROWING)"]
    return True, []


# ---------------------------------------------------------------------------
# A4: HumanResponse coverage for advisory permits
# ---------------------------------------------------------------------------


def a4_human_response_coverage(
    predicates: List[Dict[str, Any]],
    issued_permits: List[Dict[str, Any]],
    human_responses: List[Dict[str, Any]],
) -> Tuple[bool, List[str]]:
    """A4: every permit issued under a predicate declaring
    ``response_policy = REQUIRED`` has a corresponding HumanResponse record.

    ``issued_permits``: ``{"permit_id", "gcir_id"}`` -- which predicate
    authorized each permit.  Routine advisory telemetry whose predicate
    declares OPTIONAL or NONE never needs a HumanResponse (Section V design
    commitment 8); only REQUIRED is checked here.
    """
    required_gcir_ids = {p["gcir_id"] for p in predicates if p.get("response_policy") == "REQUIRED"}
    responded_permit_ids = {r["permit_id"] for r in human_responses}

    issues = []
    for permit in issued_permits:
        if permit["gcir_id"] not in required_gcir_ids:
            continue
        if permit["permit_id"] not in responded_permit_ids:
            issues.append(
                "permit %s (issued under %s, response_policy=REQUIRED) has no "
                "HumanResponse record" % (permit["permit_id"], permit["gcir_id"])
            )
    return len(issues) == 0, issues


def run_all_auxiliary_checks(evidence: Dict[str, Any]) -> Dict[str, Tuple[bool, Any]]:
    """Run A1-A4 over a supplied evidence bundle.

    ``evidence`` keys used, all optional (a check whose evidence is absent is
    reported as ``(True, ["NOT_APPLICABLE: no evidence supplied"])``, never
    silently skipped and never silently passed without a marker):
      actuations, actor_scope_revocations,
      safety_events, declared_safety_layers, bundle_payload_hash,
      delegation_child, delegation_parent,
      predicates, issued_permits, human_responses
    """
    results = {}

    if "actuations" in evidence and "actor_scope_revocations" in evidence:
        results["A1"] = a1_actor_scope_revocation_validity(
            evidence["actuations"], evidence["actor_scope_revocations"]
        )
    else:
        results["A1"] = (True, ["NOT_APPLICABLE: no actuation/revocation evidence supplied"])

    if "safety_events" in evidence and "declared_safety_layers" in evidence and "bundle_payload_hash" in evidence:
        results["A2"] = a2_safety_event_correlation_validity(
            evidence["safety_events"], evidence["declared_safety_layers"], evidence["bundle_payload_hash"]
        )
    else:
        results["A2"] = (True, ["NOT_APPLICABLE: no safety-event evidence supplied"])

    if "delegation_child" in evidence and "delegation_parent" in evidence:
        results["A3"] = a3_delegation_containment(evidence["delegation_child"], evidence["delegation_parent"])
    else:
        results["A3"] = (True, ["NOT_APPLICABLE: no delegation evidence supplied"])

    if "predicates" in evidence and "issued_permits" in evidence and "human_responses" in evidence:
        results["A4"] = a4_human_response_coverage(
            evidence["predicates"], evidence["issued_permits"], evidence["human_responses"]
        )
    else:
        results["A4"] = (True, ["NOT_APPLICABLE: no human-response evidence supplied"])

    return results
