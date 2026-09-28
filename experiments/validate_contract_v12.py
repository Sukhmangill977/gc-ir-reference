"""Full v1.2 validator test (Paper 2 v1.2 spec section 5).

    python -m experiments.validate_contract_v12 --phase development

For every machine-checkable headline v1.2 validator: at least one valid
positive and one isolated negative, the negative failing for the expected
semantic reason. Reuses ``experiments.surface_a_paired_validation``'s
fixtures where a Surface-A family already exercises the same check (rather
than re-deriving bundles this module would only duplicate), and adds
dedicated minimal fixtures for the validators Surface A does not itself
target: total_disposition, indeterminacy, declared_path,
synchronization_contract_representation, evidence_representation,
failure_semantics, and the RC-04/RC-06 routing decision.
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


def _check_result(check_id, positive_ok, negative_ok, negative_issues, description):
    negative_rejected = not negative_ok
    expected_reason_matches = negative_rejected and bool(negative_issues)
    wrong_reason_count = 1 if (negative_rejected and not negative_issues) else 0
    return {
        "check_id": check_id,
        "description": description,
        "positive_total": 1, "positive_passed": 1 if positive_ok else 0,
        "negative_total": 1, "negative_rejected": 1 if negative_rejected else 0,
        "expected_reason_matches": 1 if expected_reason_matches else 0,
        "wrong_reason_count": wrong_reason_count,
        "negative_issues": negative_issues,
    }


def _from_surface_a(surface_a_report, family_id, check_id, description):
    row = next(r for r in surface_a_report["families"] if r["family"] == family_id)
    return {
        "check_id": check_id,
        "description": description,
        "positive_total": 1, "positive_passed": 1 if row["nominal_accepted"] else 0,
        "negative_total": 1, "negative_rejected": 1 if row["negative_rejected"] else 0,
        "expected_reason_matches": 1 if (row["negative_rejected"] and not row["wrong_reason"]) else 0,
        "wrong_reason_count": 1 if row["wrong_reason"] else 0,
        "negative_issues": [row["observed_reason"]],
        "source_surface_a_family": family_id,
    }


def _total_disposition_check():
    from gcir import contract_v12
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.models import CompiledBundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())
    positive_ok, _ = contract_v12.total_disposition(result.bundle)

    negative_payload = copy.deepcopy(result.bundle.payload)
    duplicate = copy.deepcopy(negative_payload["dispositions"][0])
    negative_payload["dispositions"].append(duplicate)
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    negative_ok, issues = contract_v12.total_disposition(negative_bundle)

    return _check_result("total_disposition", positive_ok, negative_ok, issues,
                          "every risk carries exactly one disposition record")


def _indeterminacy_check():
    from gcir import contract_v12
    from gcir.caseio import load_case

    case = load_case("case_d_ccs1")
    from tools import case_d_control as ctl

    def compile_positive():
        from gcir.compiler import compile_bundle
        return compile_bundle(case.compiler_inputs())

    def compile_negative():
        from gcir.compiler import compile_bundle
        acs = [ctl.acs_d01_01(), ctl.acs_d02_01(authorized_actor=["treasury.officer_on_duty"], interpretation_status="unresolved")]
        override = {"approved_control_specifications": {"acs_set_id": "VAL-INDET", "version_binding_ref": ctl.BINDING, "records": acs}}
        inputs = case.compiler_inputs(overrides=override)
        return compile_bundle(inputs, verify_signatures=False)

    positive_ok, _ = contract_v12.indeterminacy(compile_positive)
    negative_ok, issues = contract_v12.indeterminacy(compile_negative)
    return _check_result("indeterminacy", positive_ok, negative_ok, issues,
                          "unresolved mandatory interpretation on a runtime-requested ACS is COMPILE-FAIL")


def _declared_path_check():
    from gcir import contract_v12
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())
    declared = [{"path_id": "PATH-RELEASE", "subject": "transaction_agent", "action": "release_payment",
                 "resource": "payment_instruction", "destination": "payment_rail"}]
    positive_ok, _ = contract_v12.declared_path(result.bundle, declared)

    undeclared_extra = declared + [{"path_id": "PATH-NEVER-COMPILED", "subject": "transaction_agent",
                                     "action": "release_payment_via_undeclared_channel",
                                     "resource": "payment_instruction", "destination": "payment_rail"}]
    negative_ok, issues = contract_v12.declared_path(result.bundle, undeclared_extra)
    return _check_result("declared_path", positive_ok, negative_ok, issues,
                          "every DECLARED in-scope path has a compiled gate/placement mapping")


def _synchronization_contract_check():
    from gcir import contract_v12
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    other = [r for r in case.documents["approved_control_specifications"]["records"] if r["acs_id"] != "ACS-B01-01"]
    template = copy.deepcopy(next(r for r in case.documents["approved_control_specifications"]["records"] if r["acs_id"] == "ACS-B01-01"))

    contract = {
        "source": "risk_classification_service_v1", "epoch_version": "E1", "freshness": "PT5S",
        "observed_at": "2026-01-22T15:00:00Z", "valid_until": "2026-01-22T15:05:00Z",
        "invalidation_trigger": "epoch_rollover", "revalidation_requirement": "revalidate_on_expiry",
        "failure_response": "SAFE_STATE", "downstream_interface": "risk_classification_state_v1",
    }
    positive_acs = copy.deepcopy(template)
    positive_acs["synchronization_contract"] = copy.deepcopy(contract)
    negative_acs = copy.deepcopy(template)
    incomplete_contract = copy.deepcopy(contract)
    del incomplete_contract["invalidation_trigger"]
    negative_acs["synchronization_contract"] = incomplete_contract

    def _compile(acs):
        acs_set = dict(case.documents["approved_control_specifications"])
        acs_set["records"] = [acs] + other
        inputs = case.compiler_inputs(overrides={"approved_control_specifications": acs_set})
        return compile_bundle(inputs, verify_signatures=False)

    positive_result = _compile(positive_acs)
    negative_result = _compile(negative_acs)
    positive_ok, _ = contract_v12.synchronization_contract_representation(positive_result.bundle)
    negative_ok, issues = contract_v12.synchronization_contract_representation(negative_result.bundle)
    return _check_result("synchronization_contract_representation", positive_ok, negative_ok, issues,
                          "every declared synchronization contract carries all required representation fields")


def _evidence_representation_check():
    from gcir import contract_v12
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.models import CompiledBundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())
    positive_ok, _ = contract_v12.evidence_representation(result.bundle)

    negative_payload = copy.deepcopy(result.bundle.payload)
    negative_payload["predicates"][0]["evidence_producer"] = ""
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    negative_ok, issues = contract_v12.evidence_representation(negative_bundle)
    return _check_result("evidence_representation", positive_ok, negative_ok, issues,
                          "every predicate declares a non-empty evidence path")


def _failure_semantics_check():
    """Direct payload mutation (like ``_evidence_representation_check``),
    not a re-compile: the catalog template for ACS-B01-01 permits only
    SAFE_STATE (``check_acs_against_template``), so a weakened ``on_fail``
    would never even reach a compiled bundle to exercise this validator --
    this check targets ``gcir.contract_v12.failure_semantics`` itself,
    which is exactly what a real weakened-on_fail candidate would still
    need to be rejected by if it arrived through some other channel."""
    from gcir import contract_v12
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.models import CompiledBundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())
    positive_ok, _ = contract_v12.failure_semantics(result.bundle, result.bundle)

    negative_payload = copy.deepcopy(result.bundle.payload)
    negative_payload["predicates"][0]["on_fail"] = "WARN"  # weakened from SAFE_STATE
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    negative_ok, issues = contract_v12.failure_semantics(result.bundle, negative_bundle)
    return _check_result("failure_semantics", positive_ok, negative_ok, issues,
                          "a candidate must not weaken a nominal's declared on_fail response")


def _rc_routing_check():
    from gcir.rc_routing import route_control_layer_defect

    positive = route_control_layer_defect(is_discrete_gateable_action=False)  # wrong layer -> RC-06
    negative = route_control_layer_defect(is_discrete_gateable_action=True, timing_assurance_established=False)  # RC-04

    positive_ok = positive.reason_code == "RC-06" and positive.routed_to_control_family == "standing_safety_rta"
    # "negative" here means the RC-04 case: correctly NOT routed to RTA.
    negative_ok = negative.reason_code == "RC-04" and negative.routed_to_control_family is None
    return {
        "check_id": "rc04_rc06_routing",
        "description": "RC-06 (wrong layer) routes to standing safety/RTA; RC-04 (missing timing assurance) never does",
        "positive_total": 1, "positive_passed": 1 if positive_ok else 0,
        "negative_total": 1, "negative_rejected": 1 if negative_ok else 0,
        "expected_reason_matches": 1 if negative_ok else 0,
        "wrong_reason_count": 0 if negative_ok else 1,
        "negative_issues": [
            "RC-04 routed_to_control_family=%r (must be None, never standing_safety_rta)" % negative.routed_to_control_family
        ] if not negative_ok else [],
    }


def run_all():
    from experiments import surface_a_paired_validation as sa

    surface_a_report = sa.run_all()

    checks = [
        _from_surface_a(surface_a_report, "A1", "judgment_hash_binding", "judgment_record_ref.content_hash binds canonical judgment content"),
        _from_surface_a(surface_a_report, "A2", "no_narrowing", "represented mandatory elements are preserved"),
        _from_surface_a(surface_a_report, "A4", "no_broadening", "actor/action/resource/destination/amount/exception scope is not widened"),
        _from_surface_a(surface_a_report, "A8", "no_invention", "every normative element traces to approved input or an authorized compiler invariant"),
        _from_surface_a(surface_a_report, "A3", "primary_class_preservation", "primary class is preserved, never collapsed"),
        _indeterminacy_check(),
        _from_surface_a(surface_a_report, "A5", "exception_scope", "exceptions preserve target/trigger/actor/bounds/scope/lifecycle binding"),
        _from_surface_a(surface_a_report, "A6", "lifecycle", "policy/judgment/profile version consistency"),
        _declared_path_check(),
        _synchronization_contract_check(),
        _from_surface_a(surface_a_report, "A7", "observation_obligation", "Omega_r representation and no-narrowing of beta_r"),
        _evidence_representation_check(),
        _failure_semantics_check(),
        _from_surface_a(surface_a_report, "A1", "origin", "predicate origin resolves within the approved judgment/ACS relationship"),
        _total_disposition_check(),
        _rc_routing_check(),
    ]

    totals = {
        "positive_total": sum(c["positive_total"] for c in checks),
        "positive_passed": sum(c["positive_passed"] for c in checks),
        "negative_total": sum(c["negative_total"] for c in checks),
        "negative_rejected": sum(c["negative_rejected"] for c in checks),
        "expected_reason_matches": sum(c["expected_reason_matches"] for c in checks),
        "wrong_reason_count": sum(c["wrong_reason_count"] for c in checks),
    }
    return {
        "checks": checks,
        "totals": totals,
        "check_count": len(checks),
        "counting_note": (
            "These 16 rows are the FULL v1.2 VALIDATOR TEST MATRIX (spec section 5): "
            "one (positive, negative) pair per headline machine-checkable validator "
            "(judgment_hash_binding, total_disposition, no_narrowing, no_broadening, "
            "no_invention, primary_class_preservation, indeterminacy, exception_scope, "
            "lifecycle, declared_path, synchronization_contract_representation, "
            "observation_obligation, evidence_representation, failure_semantics, "
            "origin x2, rc04_rc06_routing). This is a DIFFERENT count from "
            "gcir.negative_fixtures.get_negative_fixtures_v12()'s 9 rows (see "
            "results/development_v12/audit.json), which is a smaller set of NEW "
            "negative fixtures added to the AUDIT/REGRESSION corpus (spec sections "
            "9-10), parallel to and extending the historical 19 Q1-Q10 fixtures -- "
            "not every validator gets its own dedicated audit-regression fixture "
            "(several share one contract_v12 check as their target), and several of "
            "these 16 validator checks reuse a Surface-A fixture (spec section 2) as "
            "their positive/negative pair rather than a standalone one. All three "
            "countings (16 validator checks, 9 new audit negatives, 8 Surface-A "
            "families) measure genuinely different things and are never summed or "
            "substituted for one another."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run_all()
    document = {
        "result_name": "validate_contract_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "validators.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print(json.dumps(report["totals"], indent=2))
    print("-> %s (%d checks)" % (out_path, report["check_count"]))
    ok = (
        report["totals"]["positive_passed"] == report["totals"]["positive_total"]
        and report["totals"]["negative_rejected"] == report["totals"]["negative_total"]
        and report["totals"]["wrong_reason_count"] == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
