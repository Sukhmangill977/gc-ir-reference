"""Compute the Section XI-B metric family from the compiled artifacts.

    python -m experiments.run_metrics [--final]

Every value is derived from the bundle and the assessment.  Nothing is
hardcoded, and the two RQ5 metrics (SNR, DF) are reported as DEFERRED with a
reason rather than given a number.
"""

from __future__ import annotations

import argparse
import json
import os

from experiments.common import (
    CASES,
    REPO_ROOT,
    add_common_args,
    load_case_bundle,
    results_dir,
    write_csv,
    write_result,
)


def run(final):
    from gcir.metrics import compute_all, rq5_deferred_metrics

    per_case = {}
    for case_id in CASES:
        case, inputs, result = load_case_bundle(case_id)
        invariant_ids = [inv["invariant_id"] for inv in inputs.invariants]
        metrics = compute_all(
            inputs.assessment,
            result.bundle,
            invariant_ids,
            case.parameters["declared_heatmap_threshold"],
        )
        metrics["payload_hash"] = result.bundle.payload_hash
        metrics["statistics"] = result.statistics
        per_case[case_id] = metrics

    payload = {
        "per_case": per_case,
        "notes": {
            "RCY": "Descriptive, not a quality target. Forcing it toward 1 would "
                   "incorrectly encourage non-runtime risks to be translated into "
                   "unsuitable predicates.",
            "OPR": "Required 0. This is a compiler guarantee over Phi-produced "
                   "bundles; it extends to a deployment only under the runtime "
                   "acceptance condition of Section VI-F.",
            "GD": "Both GD sums run over ALL register rows, non-runtime dispositions "
                  "included: those rows carry ratings but no gate, and excluding them "
                  "would understate divergence at low thresholds.",
            "TD": "Measured separately by experiments/run_determinism.py.",
            "SNR_DF": "RQ5 outcomes. Deferred; no participant data exists.",
        },
    }
    write_result(final, "metrics", payload)

    # Human-readable table, generated -- never typed by hand.
    rows = []
    for case_id in CASES:
        metrics = per_case[case_id]
        for name in ("DC", "RCY", "NDR", "OPR", "ODC", "PTC", "CV"):
            entry = metrics[name]
            rows.append(
                {
                    "case": case_id,
                    "metric": name,
                    "value": "" if entry["value"] is None else "%.4f" % entry["value"],
                    "numerator": entry["numerator"],
                    "denominator": entry["denominator"],
                    "definition": entry["definition"],
                }
            )
        rows.append({
            "case": case_id, "metric": "GD(T_H)",
            "value": str(metrics["GD"]["value"]),
            "numerator": metrics["GD"]["value"],
            "denominator": len(metrics["gate_vector"]),
            "definition": "GD at declared T_H = %d" % metrics["GD"]["declared_threshold"],
        })
        rows.append({
            "case": case_id, "metric": "GD_min",
            "value": str(metrics["GD_min"]["value"]),
            "numerator": metrics["GD_min"]["value"],
            "denominator": len(metrics["gate_vector"]),
            "definition": "minimum over all candidate scalar thresholds",
        })
    for name, entry in sorted(rq5_deferred_metrics().items()):
        rows.append({
            "case": "both", "metric": name, "value": "DEFERRED",
            "numerator": "", "denominator": "", "definition": entry["definition"],
        })

    write_csv(final, "metrics.csv",
              ["case", "metric", "value", "numerator", "denominator", "definition"],
              rows)

    for case_id in CASES:
        metrics = per_case[case_id]
        print("%s  DC=%.4f RCY=%.4f NDR=%.4f OPR=%.4f ODC=%.4f PTC=%.4f CV=%.4f "
              "GD(%d)=%d GD_min=%d"
              % (case_id, metrics["DC"]["value"], metrics["RCY"]["value"],
                 metrics["NDR"]["value"], metrics["OPR"]["value"],
                 metrics["ODC"]["value"], metrics["PTC"]["value"],
                 metrics["CV"]["value"], metrics["GD"]["declared_threshold"],
                 metrics["GD"]["value"], metrics["GD_min"]["value"]))
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args(argv)
    run(args.final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
