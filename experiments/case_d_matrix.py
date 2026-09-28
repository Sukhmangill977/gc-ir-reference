"""Case D matrix: D1-D10 (Paper 2 v1.2 spec section 4).

    python -m experiments.case_d_matrix --phase development

Development-generation artifact; not part of any frozen preregister-tier0
campaign. Writes to ``results/development_v12/case_d.json`` by default.

Every row below inspects the REAL compiled output of ``cases/case_d_ccs0``,
``cases/case_d_ccs1`` and ``cases/case_d_ccs2`` (built by
``tools/build_case_d.py``) through the unmodified ``gcir.compiler.compile_bundle``,
plus, for the two controlled negatives (D7/D8), a candidate ACS set mutated
from CCS1's real approved ACS-D02-01 and re-compiled -- never a hand-shaped
stand-in bundle.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402
from tools import case_d_control as ctl  # noqa: E402


def _compile(case_id, overrides=None, verify_signatures=True):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case(case_id)
    inputs = case.compiler_inputs(overrides=overrides or {})
    return compile_bundle(inputs, verify_signatures=verify_signatures)


def _acs_set_override(acs_records, acs_set_id):
    return {"acs_set_id": acs_set_id, "version_binding_ref": ctl.BINDING, "records": acs_records}


def d1_unresolved_interpretation():
    """D1: N4 (ACS-D02-01's emergency-authority interpretation) is material
    and unresolved while emergency-capable compilation (D-02 runtime) is
    requested. Expected: COMPILE-FAIL / release-inadmissible."""
    from gcir import contract_v12
    from gcir.caseio import load_case

    case = load_case("case_d_ccs1")
    acs_records = [ctl.acs_d01_01(), ctl.acs_d02_01(
        authorized_actor=["treasury.officer_on_duty"], interpretation_status="unresolved",
    )]
    override = {"approved_control_specifications": _acs_set_override(acs_records, "D-CASE-D-CCS1-D1")}

    def compile_attempt():
        inputs = case.compiler_inputs(overrides=override)
        from gcir.compiler import compile_bundle
        return compile_bundle(inputs, verify_signatures=False)

    compiled_ok, notes = contract_v12.indeterminacy(compile_attempt)
    observed = "COMPILE-FAIL/release-inadmissible" if not compiled_ok else "compiled"
    return {
        "id": "D1", "description": "unresolved interpretation while emergency-capable compile requested",
        "expected": "COMPILE-FAIL/release-inadmissible",
        "observed": observed,
        "passed": not compiled_ok,
        "notes": notes,
    }


def d2_emergency_path_disabled():
    """D2: emergency-exception path explicitly disabled; ordinary scope
    remains enabled. Expected: CCS0 compiles."""
    try:
        result = _compile("case_d_ccs0")
        observed = "compiled"
        passed = True
    except Exception as exc:  # noqa: BLE001
        observed = "COMPILE-FAIL: %s" % exc
        passed = False
        result = None
    return {
        "id": "D2", "description": "emergency-exception path explicitly disabled",
        "expected": "CCS0 compiles",
        "observed": observed, "passed": passed,
        "payload_hash": result.bundle.payload_hash if result else None,
    }


def d3_ordinary_path_inspection():
    """D3: inspect CCS0. Expected: no emergency-authority prerequisite, no
    emergency-evidence prerequisite, ordinary requirements preserved."""
    result = _compile("case_d_ccs0")
    ordinary = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D01-01")
    ordinary_attrs = {c["attribute"] for c in ordinary["context_conditions"]}
    emergency_attrs = {"emergency_event_active", "officer_authority_valid", "evidence_fresh"}
    no_emergency_prereq = ordinary_attrs.isdisjoint(emergency_attrs)
    gate_entry = result.bundle.gate_map[ordinary["gcir_id"]]
    ordinary_preserved = (
        gate_entry["gate_type"] == "mandatory"
        and gate_entry["mandatory_role"] == "decisive"
        and ordinary["on_fail"] == "SAFE_STATE"
    )
    passed = no_emergency_prereq and ordinary_preserved
    return {
        "id": "D3", "description": "ordinary CCS0 path inspection",
        "expected": "no emergency-authority/evidence prerequisite; ordinary requirements preserved",
        "observed": {
            "ordinary_condition_attributes": sorted(ordinary_attrs),
            "no_emergency_prerequisite": no_emergency_prereq,
            "ordinary_requirements_preserved": ordinary_preserved,
        },
        "passed": passed,
    }


def d4_emergency_request_under_ccs0():
    """D4: an emergency request is outside CCS0's applicability (no compiled
    exception predicate exists to evaluate it under). Expected: HOLD /
    escalation to the declared non-runtime governance treatment -- NOT a
    DENY (an emergency claim is not evaluated as a known failure)."""
    from gcir.precedence_v11 import resolve_phase_aware

    result = _compile("case_d_ccs0")
    ordinary = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D01-01")
    evaluations = {ordinary["gcir_id"]: {"outcome": "unknown"}}
    verdict = resolve_phase_aware(result.bundle, evaluations)
    accepted_disposition = next(
        d for d in result.bundle.dispositions if d["risk_id"] == "D-02"
    )
    passed = verdict["authorization_decision"] == "HOLD" and accepted_disposition["record_type"] == "AcceptedRiskDisposition"
    return {
        "id": "D4", "description": "emergency request evaluated under CCS0 (no compiled exception path)",
        "expected": "HOLD / escalation to the declared non-runtime governance treatment, never DENY",
        "observed": {
            "authorization_decision": verdict["authorization_decision"],
            "reason": verdict["reason"],
            "d02_disposition": accepted_disposition["record_type"],
            "d02_declared_non_runtime_treatment": accepted_disposition["rationale"],
        },
        "passed": passed,
    }


def d5_signed_resolution():
    """D5: J_D resolves "authorized officer" = Treasury Officer credential.
    Expected: CCS1 compiles."""
    result = _compile("case_d_ccs1")
    exception_pred = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D02-01")
    resolved_actor = exception_pred["exception"]["authorized_actor"]
    passed = resolved_actor == ["treasury.officer_on_duty"]
    return {
        "id": "D5", "description": "signed resolution of authorized officer = Treasury Officer credential",
        "expected": "CCS1 compiles with exception.authorized_actor == ['treasury.officer_on_duty']",
        "observed": {"compiled": True, "authorized_actor": resolved_actor},
        "passed": passed,
        "payload_hash": result.bundle.payload_hash,
    }


def d6_exception_confined():
    """D6: ValidEmergencyException = EmergencyEvent AND
    EmergencyOfficerAuthorityValid AND EmergencyEvidenceFresh, active only
    inside the exception path -- never an ordinary-transfer prerequisite."""
    result = _compile("case_d_ccs1")
    exception_pred = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D02-01")
    ordinary_pred = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D01-01")
    exception_attrs = {c["attribute"] for c in exception_pred["context_conditions"]}
    ordinary_attrs = {c["attribute"] for c in ordinary_pred["context_conditions"]}
    expected_attrs = {"emergency_event_active", "officer_authority_valid", "evidence_fresh"}
    all_three_present = expected_attrs.issubset(exception_attrs)
    confined = ordinary_attrs.isdisjoint(expected_attrs)
    passed = all_three_present and confined
    return {
        "id": "D6", "description": "exception remains conditional and confined to the exception path",
        "expected": "all three conditions active only on ACS-D02-01, never on ACS-D01-01",
        "observed": {
            "exception_condition_attributes": sorted(exception_attrs),
            "ordinary_condition_attributes": sorted(ordinary_attrs),
            "all_three_present": all_three_present,
            "confined_to_exception_path": confined,
        },
        "passed": passed,
    }


def d7_exception_broadening_negative():
    """D7: widen the exception (add an unauthorized actor with no backing
    judgment) or remove a required condition. Expected: rejection for
    exception/no-broadening."""
    from gcir import contract_v12
    from gcir.caseio import load_case

    nominal_result = _compile("case_d_ccs1")
    case = load_case("case_d_ccs1")

    widened_acs = [
        ctl.acs_d01_01(),
        ctl.acs_d02_01(authorized_actor=["treasury.officer_on_duty", "external.unverified_party"]),
    ]
    override = {"approved_control_specifications": _acs_set_override(widened_acs, "D-CASE-D-CCS1-D7")}
    inputs = case.compiler_inputs(overrides=override)
    from gcir.compiler import compile_bundle
    candidate_result = compile_bundle(inputs, verify_signatures=False)

    ok_broadening, issues_broadening = contract_v12.no_broadening(nominal_result.bundle, candidate_result.bundle)
    ok_exception, issues_exception = contract_v12.exception_scope(nominal_result.bundle, candidate_result.bundle)
    rejected = (not ok_broadening) or (not ok_exception)
    return {
        "id": "D7", "description": "exception broadening negative (unauthorized actor added, no backing judgment)",
        "expected": "rejection for exception/no-broadening",
        "observed": {"no_broadening_ok": ok_broadening, "issues": issues_broadening + issues_exception},
        "passed": rejected,
    }


def d8_narrowing_negative():
    """D8: remove one mandatory represented element (drop the freshness
    condition and the exception's parameter_bounds). Expected: rejection
    for disposition/no-narrowing."""
    from gcir import contract_v12
    from gcir.caseio import load_case

    nominal_result = _compile("case_d_ccs1")
    case = load_case("case_d_ccs1")

    narrowed = ctl.acs_d02_01(authorized_actor=["treasury.officer_on_duty"])
    narrowed["context_conditions"] = narrowed["context_conditions"][:2]  # drop evidence_fresh
    del narrowed["exception"]["parameter_bounds"]
    narrowed_acs = [ctl.acs_d01_01(), narrowed]
    override = {"approved_control_specifications": _acs_set_override(narrowed_acs, "D-CASE-D-CCS1-D8")}
    inputs = case.compiler_inputs(overrides=override)
    from gcir.compiler import compile_bundle
    candidate_result = compile_bundle(inputs, verify_signatures=False)

    ok, issues = contract_v12.no_narrowing(nominal_result.bundle, candidate_result.bundle)
    return {
        "id": "D8", "description": "narrowing negative (dropped condition + dropped exception.parameter_bounds)",
        "expected": "rejection for disposition/no-narrowing",
        "observed": {"no_narrowing_ok": ok, "issues": issues},
        "passed": not ok,
    }


def d9_policy_change():
    """D9: new policy 4.3 / new J' widens the authorized actor set to
    include the analyst + ETA-2 tier. Expected: CCS2 produced with a
    changed canonical payload hash, and CCS1's judgment reference no longer
    current for CCS2's state."""
    from gcir import contract_v12

    ccs1 = _compile("case_d_ccs1")
    ccs2 = _compile("case_d_ccs2")
    hash_changed = ccs1.bundle.payload_hash != ccs2.bundle.payload_hash
    ccs1_version = ccs1.bundle.payload["judgment_record_ref"]["version"]
    ccs2_version = ccs2.bundle.payload["judgment_record_ref"]["version"]
    # CCS1's OLD judgment reference is checked against CCS2's now-current
    # version: it is correctly flagged stale.
    lifecycle_ok, lifecycle_issues = contract_v12.lifecycle(
        ccs1.bundle, expected_judgment_version=ccs2_version
    )
    old_ref_stale = (not lifecycle_ok) and (ccs1_version != ccs2_version)
    passed = hash_changed and old_ref_stale
    return {
        "id": "D9", "description": "policy 4.3 / J' widens the authorized actor set (new, separately authorized judgment)",
        "expected": "CCS2 produced; changed canonical payload hash; old policy/J reference no longer current",
        "observed": {
            "ccs1_hash": ccs1.bundle.payload_hash, "ccs2_hash": ccs2.bundle.payload_hash,
            "hash_changed": hash_changed,
            "ccs1_judgment_version": ccs1_version, "ccs2_judgment_version": ccs2_version,
            "ccs1_ref_stale_for_ccs2_state": old_ref_stale,
            "lifecycle_issues": lifecycle_issues,
        },
        "passed": passed,
    }


def d10_deterministic_canonical_compilation():
    """D10: permissible order/key-order change only. Expected: identical
    Phi_core canonical payload hash."""
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    reference = _compile("case_d_ccs1")

    case = load_case("case_d_ccs1")
    reordered_acs = list(reversed(case.documents["approved_control_specifications"]["records"]))
    reordered_acs_set = dict(case.documents["approved_control_specifications"])
    reordered_acs_set["records"] = reordered_acs
    override = {"approved_control_specifications": reordered_acs_set}
    inputs = case.compiler_inputs(overrides=override)
    reordered_result = compile_bundle(inputs, verify_signatures=False)

    passed = reference.bundle.payload_hash == reordered_result.bundle.payload_hash
    return {
        "id": "D10", "description": "row-order-only permutation of CCS1's ACS records",
        "expected": "identical Phi_core canonical payload hash",
        "observed": {
            "reference_hash": reference.bundle.payload_hash,
            "reordered_hash": reordered_result.bundle.payload_hash,
        },
        "passed": passed,
    }


def run_all():
    rows = [
        d1_unresolved_interpretation(),
        d2_emergency_path_disabled(),
        d3_ordinary_path_inspection(),
        d4_emergency_request_under_ccs0(),
        d5_signed_resolution(),
        d6_exception_confined(),
        d7_exception_broadening_negative(),
        d8_narrowing_negative(),
        d9_policy_change(),
        d10_deterministic_canonical_compilation(),
    ]
    passed = sum(1 for r in rows if r["passed"])
    return {
        "rows": rows,
        "passed": passed,
        "total": len(rows),
        "claim_boundary": (
            "Case D exercises the governance-to-control translation side only "
            "(Paper 2 v1.2 spec, final scientific boundary): whether a compiled "
            "artifact preserves origin, disposition, primary class, scope, "
            "exception semantics, lifecycle, and deterministic canonical "
            "lowering. It does not evaluate 'may this action externalize now' "
            "at runtime, which remains prior L-DREA work."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run_all()
    document = {
        "result_name": "case_d_matrix", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }

    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "case_d.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print(json.dumps(report, indent=2, default=str))
    print("\n%d/%d Case D outcomes passed -> %s" % (report["passed"], report["total"], out_path))
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
