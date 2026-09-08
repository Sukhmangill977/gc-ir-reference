"""Run the six temporal-traceability audit queries (manuscript Section VIII).

    python -m experiments.run_traceability [--final]

Two passes per case:

**Clean pass.**  Every query must return an empty set over the committed
fixtures.  "Empty result sets demonstrate linkage and temporal-integrity
completeness under the declared data model.  They do not, by themselves,
establish legal compliance, semantic correctness, or control effectiveness."

**Negative-control pass.**  For each query, a deliberately corrupted projection
is built and the query must *fire*.  A query that never fires proves nothing, so
a clean pass alone would be weak evidence.  Each negative control names the
single defect it introduces.
"""

from __future__ import annotations

import argparse
import copy
import json
import os

from experiments.common import (
    CASES,
    REPO_ROOT,
    add_common_args,
    phase_of,
    load_case_bundle,
    read_json,
    write_csv,
    write_result,
)


def _fixtures(case_id):
    lifecycle_dir = os.path.join(REPO_ROOT, "cases", case_id, "lifecycle")
    return {
        "registry": read_json(os.path.join(lifecycle_dir, "lifecycle_registry.json")),
        "receipts": read_json(os.path.join(lifecycle_dir, "receipts.json"))["receipts"],
        "actuations": read_json(os.path.join(lifecycle_dir, "actuations.json"))["actuations"],
        "negative": read_json(os.path.join(lifecycle_dir, "negative", "fixtures.json")),
    }


def _project(case, inputs, bundle, registry_doc, receipts, actuations,
             assessment=None, dispositions=None, predicates=None, invariants=None):
    from gcir import traceability as tr
    from gcir.coverage import classify_risks
    from gcir.lifecycle import LifecycleRegistry

    assessment = assessment or inputs.assessment
    registry = LifecycleRegistry(
        registry_doc, keyring=case.keyring,
        authorized_key_ids=registry_doc["authorized_signing_keys"],
    )
    connection = tr.open_projection()
    projected = copy.copy(bundle)
    if dispositions is not None or predicates is not None:
        payload = dict(bundle.payload)
        if dispositions is not None:
            payload["dispositions"] = dispositions
        if predicates is not None:
            payload["predicates"] = predicates
        projected = type(bundle)(payload=payload, payload_hash=bundle.payload_hash,
                                 envelope=bundle.envelope)
    tr.build_projection(
        connection, assessment, projected,
        invariants if invariants is not None else inputs.invariants,
        registry, receipts, actuations, case.keyring,
        classify_risks(assessment, inputs.cstar_profile),
    )
    return connection


def clean_pass(case_id):
    from gcir import traceability as tr

    case, inputs, result = load_case_bundle(case_id)
    fixtures = _fixtures(case_id)
    connection = _project(case, inputs, result.bundle, fixtures["registry"],
                          fixtures["receipts"], fixtures["actuations"])
    return tr.run_all(connection)


def negative_controls(case_id):
    """One corrupted projection per query; each must make its query fire."""
    from gcir import traceability as tr
    from gcir.models import Assessment

    case, inputs, result = load_case_bundle(case_id)
    fixtures = _fixtures(case_id)
    bundle = result.bundle
    negative = fixtures["negative"]
    controls = []

    def record(query_id, label, defect, connection):
        outcome = tr.run_query(connection, query_id)
        controls.append(
            {
                "case": case_id,
                "query_id": query_id,
                "control_label": label,
                "defect_introduced": defect,
                "detected": not outcome["empty"],
                "row_count": outcome["row_count"],
                "rows": outcome["rows"][:5],
            }
        )

    # Q1: an obligation that no risk disposes.
    assessment = Assessment(
        metadata=inputs.assessment.metadata,
        system_profile=inputs.assessment.system_profile,
        obligations=inputs.assessment.obligations + [
            dict(inputs.assessment.obligations[0], obligation_id="ORPHAN-OBLIGATION-01")
        ],
        risk_register=inputs.assessment.risk_register,
        risk_analysis=inputs.assessment.risk_analysis,
    )
    record("Q1", "orphan obligation",
           "an obligation added to O that no register row cites",
           _project(case, inputs, bundle, fixtures["registry"], fixtures["receipts"],
                    fixtures["actuations"], assessment=assessment))

    # Q2: a risk with no disposition record.
    record("Q2", "risk with no disposition",
           "one RuntimeDisposition record removed from the projection",
           _project(case, inputs, bundle, fixtures["registry"], fixtures["receipts"],
                    fixtures["actuations"], dispositions=bundle.dispositions[1:]))

    # Q2 (second form): a risk with two dispositions.
    record("Q2", "risk with two dispositions",
           "a duplicate disposition row for one risk",
           _project(case, inputs, bundle, fixtures["registry"], fixtures["receipts"],
                    fixtures["actuations"],
                    dispositions=bundle.dispositions + [
                        dict(bundle.dispositions[0], record_type="AcceptedRiskDisposition")
                    ]))

    # Q3: an orphan predicate whose origin resolves to nothing.
    orphan = copy.deepcopy(bundle.predicates[0])
    orphan["gcir_id"] = "GCIR-ORPHAN-001"
    orphan["origin"] = dict(orphan["origin"], origin_id="R-DOES-NOT-EXIST")
    orphan["requirement_ref"] = dict(orphan["requirement_ref"], risk_id="R-DOES-NOT-EXIST")
    record("Q3", "orphan predicate",
           "a predicate whose origin_id resolves to no register row and no invariant",
           _project(case, inputs, bundle, fixtures["registry"], fixtures["receipts"],
                    fixtures["actuations"], predicates=bundle.predicates + [orphan]))

    # Q4a: a receipt taken after the registry-effective retirement.
    record("Q4", "post-retirement receipt",
           "a receipt whose decision_time is after the signed retirement's effective_time",
           _project(case, inputs, bundle, fixtures["registry"],
                    fixtures["receipts"] + [negative["q4_post_retirement_receipt"]],
                    fixtures["actuations"]))

    # Q4b: a receipt citing a bundle hash that does not bind.
    record("Q4", "wrong bundle hash",
           "a receipt citing a bundle_hash that is not H(b.payload)",
           _project(case, inputs, bundle, fixtures["registry"],
                    fixtures["receipts"] + [negative["q4_wrong_bundle_hash_receipt"]],
                    fixtures["actuations"]))

    # Q5a: an actuation with no receipt.
    record("Q5", "actuation with no receipt",
           "an actuation record whose receipt_id is null",
           _project(case, inputs, bundle, fixtures["registry"], fixtures["receipts"],
                    fixtures["actuations"] + [negative["q5_orphan_actuation"]]))

    # Q5b: a receipt committed after actuation.
    record("Q5", "commit after actuation",
           "a receipt whose evidence_commit_time is later than the actuation_time",
           _project(case, inputs, bundle, fixtures["registry"],
                    fixtures["receipts"] + [negative["q5_late_commit_receipt"]],
                    fixtures["actuations"] + [negative["q5_late_commit_actuation"]]))

    # Q6: a registry record signed outside authorized_signing_keys.
    rogue_registry = copy.deepcopy(fixtures["registry"])
    rogue_registry["entries"].append(negative["q6_unauthorized_registry_entry"])
    record("Q6", "unauthorized registry signature",
           "a revocation record signed by a key absent from authorized_signing_keys",
           _project(case, inputs, bundle, rogue_registry, fixtures["receipts"],
                    fixtures["actuations"]))

    return controls


def run(final):
    from gcir import traceability as tr

    tr.write_sql_file(os.path.join(REPO_ROOT, "queries", "traceability.sql"))

    payload = {"clean": {}, "negative_controls": {}, "query_catalogue": {
        qid: {"title": q["title"], "detects": q["detects"]}
        for qid, q in sorted(tr.QUERIES.items())
    }}
    csv_rows = []
    all_clean_empty = True
    all_detected = True

    for case_id in CASES:
        clean = clean_pass(case_id)
        payload["clean"][case_id] = clean
        for qid in sorted(clean):
            outcome = clean[qid]
            all_clean_empty = all_clean_empty and outcome["empty"]
            csv_rows.append({
                "case": case_id, "pass": "clean", "query_id": qid,
                "control_label": "", "row_count": outcome["row_count"],
                "expected": "empty",
                "outcome": "PASS" if outcome["empty"] else "FAIL",
            })
        print("%s clean: %s" % (case_id, {q: clean[q]["row_count"] for q in sorted(clean)}))

        controls = negative_controls(case_id)
        payload["negative_controls"][case_id] = controls
        for control in controls:
            all_detected = all_detected and control["detected"]
            csv_rows.append({
                "case": case_id, "pass": "negative_control",
                "query_id": control["query_id"],
                "control_label": control["control_label"],
                "row_count": control["row_count"], "expected": "non-empty",
                "outcome": "PASS" if control["detected"] else "FAIL",
            })
        detected = sum(1 for c in controls if c["detected"])
        print("%s negative controls: %d/%d detected" % (case_id, detected, len(controls)))
        for control in controls:
            if not control["detected"]:
                print("   NOT DETECTED: %s / %s" % (control["query_id"], control["control_label"]))

    payload["summary"] = {
        "all_clean_queries_empty": all_clean_empty,
        "all_negative_controls_detected": all_detected,
        "queries_implemented": sorted(tr.QUERIES),
        "interpretation": (
            "Empty result sets on the clean fixtures demonstrate linkage and "
            "temporal-integrity completeness UNDER THE DECLARED DATA MODEL. They do "
            "not establish legal compliance, semantic correctness, or control "
            "effectiveness. The negative controls establish that each query can in "
            "fact detect the violation it exists to detect."
        ),
    }
    write_result(final, "traceability_queries", payload)
    write_csv(final, "traceability_queries.csv",
              ["case", "pass", "query_id", "control_label", "row_count",
               "expected", "outcome"], csv_rows)
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args(argv)
    payload = run(phase_of(args))
    ok = (payload["summary"]["all_clean_queries_empty"]
          and payload["summary"]["all_negative_controls_detected"])
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
