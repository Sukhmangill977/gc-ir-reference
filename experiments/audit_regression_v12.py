"""Audit regression (Paper 2 v1.2 spec sections 9-10).

    python -m experiments.audit_regression_v12 --phase development

Retains the existing Q1-Q10 audit queries and the historical 19 targeted
negative fixtures; adds the new v1.2 negatives. Verifies: valid artifacts
pass, historical negatives are still detected, new negatives are detected
for their expected reason. Keeps ODC/OPR/PTC/CV/C_path as distinct metrics
-- never substituting one for another.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402


def _q1_q10_positive():
    from gcir.audit_queries import run_all_audit_queries
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle, sign_bundle

    case = load_case("case_b_v1_1")
    inputs = case.compiler_inputs()
    result = compile_bundle(inputs)
    parameters = case.parameters
    bundle = sign_bundle(result.bundle, case.keyring, parameters["bundle_signing_key"], parameters["compile_time"])
    catalog_document = case.documents["control_derivation_catalog"]
    results = run_all_audit_queries(bundle, catalog_document=catalog_document)
    return {qid: ok for qid, (ok, _detail) in results.items()}, bundle, catalog_document


def _historical_19_negatives(clean_bundle, catalog_document):
    from gcir import audit_queries, negative_fixtures

    fixtures = negative_fixtures.get_negative_fixtures(clean_bundle)
    rows = []
    for name, mutated_bundle in fixtures.items():
        target = negative_fixtures.FIXTURE_TARGET_QUERY[name]
        results = audit_queries.run_all_audit_queries(mutated_bundle, catalog_document=catalog_document)
        ok, detail = results[target]
        rows.append({"fixture": name, "target_query": target, "detected": not ok, "detail": detail if not isinstance(detail, tuple) else str(detail)})
    return rows


def _new_v12_negatives(v12_bundle):
    from gcir import contract_v12, negative_fixtures
    from gcir.caseio import load_case

    case = load_case("case_d_ccs1")
    inputs = case.compiler_inputs()

    checks = {
        "judgment_hash_binding": lambda n, c: contract_v12.judgment_hash_binding(c, expected_judgment=inputs.judgment),
        "no_narrowing": contract_v12.no_narrowing,
        "no_broadening": contract_v12.no_broadening,
        "no_invention": contract_v12.no_invention,
        "primary_class_preservation": contract_v12.primary_class_preservation,
        "exception_scope": contract_v12.exception_scope,
        "lifecycle": lambda n, c: contract_v12.lifecycle(c, expected_judgment_version="9.9-nonexistent"),
        "synchronization_contract_representation": lambda n, c: contract_v12.synchronization_contract_representation(c),
    }
    pairs = negative_fixtures.get_negative_fixtures_v12(v12_bundle)
    rows = []
    for name, (nominal, candidate) in pairs.items():
        target = negative_fixtures.FIXTURE_TARGET_CHECK_V12[name]
        ok, issues = checks[target](nominal, candidate)
        rows.append({"fixture": name, "target_check": target, "detected": not ok, "issues": issues})
    return rows


def _metrics_distinct():
    from gcir import metrics as metrics_mod
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    inputs = case.compiler_inputs()
    result = compile_bundle(inputs)
    invariant_ids = [i["invariant_id"] for i in inputs.invariants]
    computed = metrics_mod.compute_all(inputs.assessment, result.bundle, invariant_ids, declared_threshold=15)

    declared_paths = [{"path_id": "PATH-RELEASE", "subject": "transaction_agent", "action": "release_payment",
                        "resource": "payment_instruction", "destination": "payment_rail"}]
    c_path = metrics_mod.c_path_metric(result.bundle, declared_paths)

    return {
        "ODC": computed["ODC"]["value"], "OPR": computed["OPR"]["value"],
        "PTC": computed["PTC"]["value"], "CV": computed["CV"]["value"],
        "C_path": c_path["C_path"]["value"],
        "note": "Five distinct metrics, kept separate; never substituted for one another (spec section 10).",
    }


def run():
    q_positive, clean_bundle, catalog_document = _q1_q10_positive()
    historical_rows = _historical_19_negatives(clean_bundle, catalog_document)

    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    v12_case = load_case("case_d_ccs1")
    v12_bundle = compile_bundle(v12_case.compiler_inputs()).bundle
    new_rows = _new_v12_negatives(v12_bundle)

    metrics = _metrics_distinct()

    return {
        "q1_q10_positive": q_positive,
        "q1_q10_all_pass": all(q_positive.values()),
        "historical_19_negatives": historical_rows,
        "historical_19_all_detected": len(historical_rows) == 19 and all(r["detected"] for r in historical_rows),
        "new_v12_negatives": new_rows,
        "new_v12_all_detected": len(new_rows) == 9 and all(r["detected"] for r in new_rows),
        "metrics": metrics,
        "counting_note": (
            "These 9 rows are gcir.negative_fixtures.get_negative_fixtures_v12()'s "
            "AUDIT/REGRESSION corpus (spec sections 9-10): new negative fixtures "
            "added alongside the historical 19 Q1-Q10 fixtures above, each targeting "
            "exactly one gcir.contract_v12 check. This is a DIFFERENT count from "
            "experiments.validate_contract_v12's 16 validator test-matrix rows (see "
            "results/development_v12/validators.json), which is the full spec-section-5 "
            "positive/negative pair per headline validator (several validators share "
            "no dedicated audit-regression fixture here, e.g. indeterminacy and "
            "declared_path are exercised only in the validator matrix, not as a "
            "committed audit fixture). Never sum or substitute one count for the other."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run()
    document = {
        "result_name": "audit_regression_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "audit.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print("Q1-Q10 all pass: %s" % report["q1_q10_all_pass"])
    print("historical 19 all detected: %s" % report["historical_19_all_detected"])
    print("new v1.2 (9) all detected: %s" % report["new_v12_all_detected"])
    print(json.dumps(report["metrics"], indent=2))
    print("-> %s" % out_path)
    ok = report["q1_q10_all_pass"] and report["historical_19_all_detected"] and report["new_v12_all_detected"]
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
