"""Case B v1.1: thirteen injection scenarios, asserting the exact category
outcome per runbook item 3/4 -- not merely non-externalization.

Every row records, and this module asserts:

    scenario, target predicate, injected outcome,
    authorization_decision, release_decision, next_authorization_effect,
    safe_state, externalization, reason, expected, actual, PASS/FAIL

This supersedes the historical experiments/case_b_injection_scenarios.py for
the frozen six-ACS Case B (untouched, still targets GCIR-B0001..B0006 /
GCIR-INV-VERSION against the published L-DREA family) with a version
retargeted to Case B v1.1's real nine-ACS / twelve-predicate structure.  The
thirteen scenario *names* are kept for continuity with the manuscript's
adversarial-attack-family / ASB-scenario-family framing, but several are
retargeted onto the schema-v1.1 mechanisms (state binding, concurrence,
POST_AUTH_PRE_ACTUATION) that did not exist for the frozen bundle to exercise.
This retargeting is a scenario-design choice, not a claim of correspondence to
the external L-DREA artifact -- see cases/case_b/ldrea_traceability.json for
the real correspondence classification, which this module does not extend.

Development-generation artifact; not part of the frozen preregister-tier0-v3.1
campaign.

    python -m experiments.case_b_v11_injection_scenarios
"""

from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from gcir.caseio import load_case  # noqa: E402
from gcir.compiler import compile_bundle  # noqa: E402
from gcir.precedence_v11 import resolve_phase_aware  # noqa: E402


def _gcir_id_for_acs(bundle, acs_id):
    for p in bundle.predicates:
        if p.get("acs_id") == acs_id:
            return p["gcir_id"]
    raise KeyError(acs_id)


def _clean_evaluations(bundle):
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    for acs_id in ("ACS-B01-03", "ACS-B02-02"):
        gid = _gcir_id_for_acs(bundle, acs_id)
        evaluations[gid] = {"outcome": "pass", "concurrence_attestations": 1}
    return evaluations


#: (scenario_name, target_acs_id, injected_evaluation_override,
#:  expected_authorization_decision, expected_release_decision,
#:  expected_next_authorization_effect, reason)
_ALLOW = "ALLOW_RELEASE"
_BLOCK = "BLOCK_RELEASE"
_NONE = "NONE"

SCENARIOS = [
    (
        "missing_predicate", "ACS-B01-01",
        {"outcome": "unknown"}, "HOLD", _ALLOW, _NONE,
        "Permit-binding evidence absent/indeterminate, with a declared escalation route -- HOLD, not a silent permit.",
    ),
    (
        "corrupted_input", "ACS-B01-02",
        {"outcome": "unknown"}, "HOLD", _ALLOW, _NONE,
        "Risk-classification evidence corrupted/unavailable, escalation route declared -- HOLD.",
    ),
    (
        "network_partition_or_delay", "ACS-B04-01",
        {"outcome": "unknown"}, "HOLD", _ALLOW, _NONE,
        "Sanctions screening service unreachable -- indeterminacy with escalation, HOLD; service failure is never read as clearance.",
    ),
    (
        "session_intent_compromise", "ACS-B01-01",
        {"outcome": "pass", "state_digest_match": False}, "HOLD", _ALLOW, _NONE,
        "World state changed mid-session (state-binding mismatch) -- HOLD, forcing re-authorization (INV-STATE-BINDING default).",
    ),
    (
        "toctou", "ACS-B06-01",
        {"outcome": "fail"}, "PERMIT", _BLOCK, _NONE,
        "Receipt-chain check is POST_AUTH_PRE_ACTUATION: authorization was correctly PERMIT on the pre-authorization conditions; release is blocked, not retroactively denied -- exactly the TOCTOU-guarding distinction.",
    ),
    (
        "replay_attack", "ACS-B05-01",
        {"outcome": "fail"}, "DENY", _ALLOW, _NONE,
        "Permit already redeemed / transaction hash already seen -- known failure, DENY.",
    ),
    (
        "payload_mutation", "ACS-B01-01",
        {"outcome": "fail"}, "DENY", _ALLOW, _NONE,
        "Bound hash does not match the mutated transaction payload -- known failure, DENY.",
    ),
    (
        "concurrency_conflict", "ACS-B01-03",
        {"outcome": "unknown", "concurrence_attestations": 0, "concurrence_window_expired": True}, "DENY", _ALLOW, _NONE,
        "Enhanced-approval concurrence window expired unsatisfied -- concurrence_expiry_response is fixed DENY, never an evaluator timeout.",
    ),
    (
        "adaptive_attacker", "ACS-B01-02",
        {"outcome": "fail"}, "DENY", _ALLOW, _NONE,
        "Risk classification resolves to a known-prohibited class -- known failure, DENY.",
    ),
    (
        "identity_provenance_deception", "ACS-B04-01",
        {"outcome": "fail"}, "DENY", _ALLOW, _NONE,
        "Counterparty resolves to a restricted-party match -- known failure, DENY.",
    ),
    (
        "runtime_infrastructure_drift", "INV-VERSION",
        {"outcome": "fail"}, "DENY", _ALLOW, _NONE,
        "Runtime fingerprint diverges from M.version_binding -- known failure, DENY.",
    ),
    (
        "economic_logic_fragility", "ACS-B02-02",
        {"outcome": "unknown", "concurrence_attestations": 0, "concurrence_window_expired": True}, "DENY", _ALLOW, _NONE,
        "Delegated escalation-tier approval denied/expired for an above-ordinary-limit amount -- DENY.",
    ),
    (
        "cross_entity_fraud_propagation", "ACS-B02-01",
        {"outcome": "fail"}, "DENY", _ALLOW, _NONE,
        "Amount exceeds the absolute authority ceiling -- known failure, unconditional DENY (no escalation route on this ACS).",
    ),
]


def _target_gcir_id(bundle, target):
    if target.startswith("INV-"):
        for p in bundle.predicates:
            if p["origin"]["origin_type"] == "compiler_invariant" and p["origin"]["origin_id"] == target:
                return p["gcir_id"]
        raise KeyError(target)
    return _gcir_id_for_acs(bundle, target)


def run(bundle):
    from gcir.models import safe_state_of

    rows = []
    for name, target, override, expected_auth, expected_release, expected_next_auth, reason in SCENARIOS:
        gid = _target_gcir_id(bundle, target)
        evaluations = _clean_evaluations(bundle)
        evaluations[gid] = override
        verdict = resolve_phase_aware(bundle, evaluations)

        externalization = not verdict["externalization_blocked"]
        # safe_state is asserted as a pure function of authorization_decision
        # ALONE here too, independently of gcir.precedence_v11's own internal
        # assertion -- this is the external, report-facing confirmation of the
        # same invariant (item 3): release_decision must never feed back into
        # it, whatever expected_release is for this row.
        expected_safe_state = safe_state_of(expected_auth)
        passed = (
            verdict["authorization_decision"] == expected_auth
            and verdict["release_decision"] == expected_release
            and verdict["next_authorization_effect"] == expected_next_auth
            and verdict["safe_state"] == expected_safe_state
            and externalization is False
        )
        rows.append({
            "scenario": name,
            "target_predicate": gid,
            "target_acs_or_invariant": target,
            "injected_outcome": override,
            "authorization_decision": verdict["authorization_decision"],
            "release_decision": verdict["release_decision"],
            "next_authorization_effect": verdict["next_authorization_effect"],
            "safe_state": verdict["safe_state"],
            "release_safe": verdict["release_safe"],
            "externalization_blocked": verdict["externalization_blocked"],
            "externalization": externalization,
            "reason": reason,
            "expected": {
                "authorization_decision": expected_auth,
                "release_decision": expected_release,
                "next_authorization_effect": expected_next_auth,
                "safe_state": expected_safe_state,
            },
            "actual": {
                "authorization_decision": verdict["authorization_decision"],
                "release_decision": verdict["release_decision"],
                "next_authorization_effect": verdict["next_authorization_effect"],
                "safe_state": verdict["safe_state"],
            },
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
        })

    # Clean control: nothing injected -> PERMIT / ALLOW_RELEASE / NONE, no externalization concern (externalization *may* occur).
    clean_verdict = resolve_phase_aware(bundle, _clean_evaluations(bundle))
    clean_row = {
        "scenario": "clean_control",
        "authorization_decision": clean_verdict["authorization_decision"],
        "release_decision": clean_verdict["release_decision"],
        "next_authorization_effect": clean_verdict["next_authorization_effect"],
        "safe_state": clean_verdict["safe_state"],
        "expected": {"authorization_decision": "PERMIT", "release_decision": "ALLOW_RELEASE", "next_authorization_effect": "NONE"},
        "passed": (
            clean_verdict["authorization_decision"] == "PERMIT"
            and clean_verdict["release_decision"] == "ALLOW_RELEASE"
            and clean_verdict["safe_state"] is False
        ),
    }
    rows.append(clean_row)

    injection_rows = rows[:-1]  # exclude clean_control from the 13-row tally

    # Two INDEPENDENT axes, tallied separately and never merged into one
    # "decision" count (runbook item 7): authorization_decision is always
    # exactly one of {PERMIT, DENY, HOLD}; release_decision (meaningful only
    # when authorization_decision == PERMIT) is separately one of
    # {ALLOW_RELEASE, BLOCK_RELEASE}. BLOCK_RELEASE is a release-axis outcome
    # of a PERMIT authorization, not a fourth peer authorization decision, and
    # must never be added to or substituted into the authorization tally.
    authorization_decision_counts = {
        "PERMIT": sum(1 for r in injection_rows if r["authorization_decision"] == "PERMIT"),
        "DENY": sum(1 for r in injection_rows if r["authorization_decision"] == "DENY"),
        "HOLD": sum(1 for r in injection_rows if r["authorization_decision"] == "HOLD"),
    }
    release_decision_counts = {
        "ALLOW_RELEASE": sum(1 for r in injection_rows if r["release_decision"] == "ALLOW_RELEASE"),
        "BLOCK_RELEASE": sum(1 for r in injection_rows if r["release_decision"] == "BLOCK_RELEASE"),
    }
    assert sum(authorization_decision_counts.values()) == len(injection_rows) == 13
    assert sum(release_decision_counts.values()) == len(injection_rows) == 13

    return {
        "scenario_count": len(rows),
        "passed": sum(1 for r in rows if r["passed"]),
        "failed": sum(1 for r in rows if not r["passed"]),
        "authorization_decision_counts": authorization_decision_counts,
        "release_decision_counts": release_decision_counts,
        # Deprecated flat aliases, retained only for callers that read the
        # old field names; authorization_decision_counts/release_decision_counts
        # above are authoritative and must be used for any report text.
        "deny_count": authorization_decision_counts["DENY"],
        "hold_count": authorization_decision_counts["HOLD"],
        "permit_count": authorization_decision_counts["PERMIT"],
        "block_release_count": release_decision_counts["BLOCK_RELEASE"],
        "zero_externalization": all(not r.get("externalization", False) for r in injection_rows),
        "scenarios": rows,
        "claim_boundary": (
            "Decision-level injections against the compiled Case B v1.1 predicate "
            "set. Each of the 13 rows asserts the exact authorization_decision, "
            "release_decision, and next_authorization_effect its category "
            "requires -- not merely that no externalization occurs (runbook item "
            "3/4). authorization_decision (PERMIT/DENY/HOLD) and release_decision "
            "(ALLOW_RELEASE/BLOCK_RELEASE) are two INDEPENDENT axes, never summed "
            "together or reported as one combined tally: a scenario counted under "
            "BLOCK_RELEASE is also counted under its own authorization_decision "
            "(PERMIT, for the one such row this suite exercises) -- it is not a "
            "fourth peer authorization outcome alongside PERMIT/DENY/HOLD. "
            "safe_state is asserted as a pure function of authorization_decision "
            "alone (models.safe_state_of); release_decision and "
            "next_authorization_effect never feed back into it (runbook item 3) -- "
            "see release_safe / externalization_blocked for the release-axis "
            "equivalents, reported separately per scenario. Scenario-to-predicate "
            "targeting here is a development-generation design choice retargeting "
            "the manuscript's 13 named families onto Case B v1.1's real nine-ACS "
            "structure; it does not extend or supersede "
            "cases/case_b/ldrea_traceability.json's correspondence classification "
            "against the external L-DREA artifact for the historical six-ACS bundle."
        ),
    }


def main(argv=None):
    case = load_case("case_b_v1_1")
    inputs = case.compiler_inputs()
    result = compile_bundle(inputs)
    report = run(result.bundle)
    print(json.dumps(report, indent=2, default=str))
    auth = report["authorization_decision_counts"]
    rel = report["release_decision_counts"]
    print(
        "\n%d/%d scenarios passed\n"
        "  authorization_decision (13 rows, one axis): PERMIT=%d DENY=%d HOLD=%d\n"
        "  release_decision       (13 rows, independent axis): ALLOW_RELEASE=%d BLOCK_RELEASE=%d\n"
        "  (BLOCK_RELEASE is a release-axis outcome of a PERMIT authorization, "
        "never a fourth peer authorization decision)"
        % (
            report["passed"], report["scenario_count"],
            auth["PERMIT"], auth["DENY"], auth["HOLD"],
            rel["ALLOW_RELEASE"], rel["BLOCK_RELEASE"],
        )
    )
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
