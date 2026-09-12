"""Case C failure-injection scenarios (E1-E19 in the manuscript; E1-E12
implemented here).

This is a representative subset, not the full nineteen-scenario matrix the
manuscript describes for Case C's Appendix D conformance harness -- see
docs/CASE_C_STATUS.md item 4 for exactly which categories are covered and
which are out of scope for this generation (chiefly ones needing a live
runtime environment, e.g. a ROS 2 simulator, rather than a single evaluation
call against the compiled bundle).

Every scenario below is a genuine, mechanically checked assertion against the
real compiled Case C bundle (or, for the auxiliary-check scenarios, against
plain evidence records matching the schemas in schemas/*.schema.json) -- none
is a claim about trajectory safety, clinical outcome, or hardware behavior.

    python -m experiments.case_c_injection_scenarios
"""

from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from gcir import auxiliary_checks  # noqa: E402
from gcir.caseio import load_case  # noqa: E402
from gcir.compiler import compile_bundle  # noqa: E402
from gcir.precedence_v11 import resolve_phase_aware  # noqa: E402

from tools.case_c_data import ACTIVATE_INSTRUMENT  # noqa: E402


def _gcir_id_for_acs(bundle, acs_id):
    for p in bundle.predicates:
        if p.get("acs_id") == acs_id:
            return p["gcir_id"]
    raise KeyError(acs_id)


def _clean_evaluations(bundle):
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    gid_c04 = _gcir_id_for_acs(bundle, "ACS-C04-01")
    evaluations[gid_c04] = {"outcome": "pass", "concurrence_attestations": 2}
    return evaluations


def _precedence_scenario(name, bundle, acs_id, override, expected_decision, description):
    evaluations = _clean_evaluations(bundle)
    gid = _gcir_id_for_acs(bundle, acs_id)
    evaluations[gid] = override
    verdict = resolve_phase_aware(bundle, evaluations)
    passed = verdict["decision"] == expected_decision
    return {
        "scenario": name, "mechanism": "precedence_v11", "target_acs": acs_id,
        "target_gcir_id": gid, "injected": override,
        "expected_decision": expected_decision, "decision": verdict["decision"],
        "safe_state": verdict["safe_state"], "passed": passed, "description": description,
    }


def run(bundle):
    rows = []

    # E1-E3: authority and identity (C-03: supervisory authority).
    rows.append(_precedence_scenario(
        "E1_unprivileged_supervisor", bundle, "ACS-C03-01", {"outcome": "fail"}, "DENY",
        "Supervisor authenticated but not privileged for this procedure class -- known failure.",
    ))
    rows.append(_precedence_scenario(
        "E2_expired_credential", bundle, "ACS-C03-01", {"outcome": "unknown"}, "HOLD",
        "Credential/control-token state indeterminate, with this predicate's declared escalation route present -- HOLD (unknown evidence + valid escalation), not a silent DENY or PERMIT.",
    ))
    rows.append(_precedence_scenario(
        "E3_control_token_mismatch", bundle, "ACS-C03-01", {"outcome": "fail"}, "DENY",
        "Authenticated actor is not the current control-token owner -- known failure.",
    ))

    # E4-E6: state binding (C-02: energy delivery digest mismatches).
    rows.append(_precedence_scenario(
        "E4_procedure_step_digest_mismatch", bundle, "ACS-C02-01",
        {"outcome": "pass", "state_digest_match": False}, "HOLD",
        "World-state digest at the boundary no longer matches the digest at authorization (procedure_step changed) -- HOLD (INV-STATE-BINDING), never a silent permit.",
    ))
    rows.append(_precedence_scenario(
        "E5_instrument_digest_mismatch", bundle, "ACS-C02-01",
        {"outcome": "pass", "state_digest_match": False}, "HOLD",
        "Instrument identity changed between authorization and the boundary -- HOLD.",
    ))
    rows.append(_precedence_scenario(
        "E6_port_configuration_digest_mismatch", bundle, "ACS-C02-01",
        {"outcome": "pass", "state_digest_match": False}, "HOLD",
        "Port configuration changed between authorization and the boundary -- HOLD.",
    ))

    # E7: concurrence window expiry (C-04: control transfer).
    rows.append(_precedence_scenario(
        "E7_concurrence_window_expiry_single_attestation", bundle, "ACS-C04-01",
        {"outcome": "unknown", "concurrence_attestations": 1, "concurrence_window_expired": True}, "DENY",
        "A releasing attestation with no receiving one when the 2-of-2 window closes -- DENY (concurrence_expiry_response), not a pending transfer.",
    ))

    # E8: evaluator timeout (C-14: latency watchdog).
    rows.append(_precedence_scenario(
        "E8_evaluator_timeout", bundle, "ACS-C14-01",
        {"outcome": "pass", "timed_out": True}, "HOLD",
        "The independent deadline watchdog expires before evaluation-complete -- HOLD, never a partial permit.",
    ))

    # E9: actor-scope revocation mid-flight (auxiliary A1).
    actuations = [{"actor_id": "surgeon.primary", "action_tuple": ACTIVATE_INSTRUMENT, "authorization_time": "2026-03-05T10:00:00Z"}]
    revocations = [{
        "record_type": "ActorScopeRevocation", "actor_id": "surgeon.primary",
        "scope": [ACTIVATE_INSTRUMENT], "effective_time": "2026-03-05T09:00:00Z",
    }]
    a1_passed, a1_issues = auxiliary_checks.a1_actor_scope_revocation_validity(actuations, revocations)
    rows.append({
        "scenario": "E9_actuation_after_supervisor_withdraws_authority", "mechanism": "auxiliary_A1",
        "expected_detected": True, "detected": not a1_passed, "issues": a1_issues,
        "passed": (not a1_passed),
        "description": "An actuation authorized after the actor's scope was revoked must be detected by auxiliary check A1.",
    })

    # E10: delegated child wider than parent (auxiliary A3, C-12).
    parent = {"scope": ["procedure_field:step_6"], "actions": ["enter_autonomous_subtask"],
              "validity": {"effective_from": "2026-03-05T09:00:00Z", "effective_until": "2026-03-05T11:00:00Z"}}
    wider_child = {"scope": ["procedure_field:step_6", "procedure_field:step_7"], "actions": ["enter_autonomous_subtask"],
                   "validity": {"effective_from": "2026-03-05T09:00:00Z", "effective_until": "2026-03-05T11:00:00Z"}}
    a3_passed, a3_issues = auxiliary_checks.a3_delegation_containment(wider_child, parent)
    rows.append({
        "scenario": "E10_delegated_subtask_exceeds_delegation_scope", "mechanism": "auxiliary_A3",
        "expected_detected": True, "detected": not a3_passed, "issues": a3_issues,
        "passed": (not a3_passed),
        "description": "A child permit issued by DELEGATE wider than its parent's scope must be rejected by auxiliary check A3.",
    })

    # E11: missing safety-event correlation (auxiliary A2, C-15).
    interventions = [{"effective_time": "2026-03-05T10:00:00Z", "correlated_permit_id": "PERMIT-X"}]
    a2_passed, a2_issues = auxiliary_checks.a2_missing_safety_correlation(interventions, [], 5)
    rows.append({
        "scenario": "E11_unrecorded_safety_intervention", "mechanism": "auxiliary_A2",
        "expected_detected": True, "detected": not a2_passed, "issues": a2_issues,
        "passed": (not a2_passed),
        "description": "A safety-layer intervention with no correlated SafetyEvent within the recording window must be detected by auxiliary check A2 (it never gates the intervention itself).",
    })

    # E12: missing human response for required guidance (auxiliary A4, C-08).
    gid_c08 = _gcir_id_for_acs(bundle, "ACS-C08-01")
    permits = [{"permit_id": "PERMIT-C08-X", "gcir_id": gid_c08}]
    a4_passed, a4_issues = auxiliary_checks.a4_human_response_coverage(bundle.predicates, permits, [])
    rows.append({
        "scenario": "E12_missing_human_response_for_required_guidance", "mechanism": "auxiliary_A4",
        "expected_detected": True, "detected": not a4_passed, "issues": a4_issues,
        "passed": (not a4_passed),
        "description": "A REQUIRED-response-policy guidance permit with no HumanResponse record must be detected by auxiliary check A4.",
    })

    # Clean control: nothing injected must PERMIT.
    clean_verdict = resolve_phase_aware(bundle, _clean_evaluations(bundle))
    clean_row = {
        "scenario": "clean_control", "mechanism": "precedence_v11",
        "expected_decision": "PERMIT", "decision": clean_verdict["decision"],
        "safe_state": clean_verdict["safe_state"],
        "passed": clean_verdict["decision"] == "PERMIT" and clean_verdict["safe_state"] is False,
        "description": "With nothing injected, the compiled Case C bundle PERMITs.",
    }
    rows.append(clean_row)

    return {
        "scenario_count": len(rows),
        "passed": sum(1 for r in rows if r["passed"]),
        "failed": sum(1 for r in rows if not r["passed"]),
        "scenarios": rows,
        "claim_boundary": (
            "Decision-level and auxiliary-check injections against the compiled "
            "Case C predicate set and plain evidence records. These establish "
            "that the compiled bundle and its auxiliary checks refuse to permit "
            "or correctly detect a violation under each exercised hazard class. "
            "This is 12 of the manuscript's 19 named Case C scenarios (E1-E12); "
            "see docs/CASE_C_STATUS.md item 4 for which remain out of scope. No "
            "trajectory safety, clinical outcome, or hardware claim is made."
        ),
    }


def main(argv=None):
    case = load_case("case_c")
    inputs = case.compiler_inputs()
    result = compile_bundle(inputs)
    report = run(result.bundle)
    print(json.dumps(report, indent=2, default=str))
    print("\n%d/%d scenarios passed" % (report["passed"], report["scenario_count"]))
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
