"""Monte Carlo rating-robustness analysis, run explicitly for Case A and
Case B v1.1 (prospective v4, runbook item G) -- paired the same way
run_determinism_case_b_v11.py pairs Case A alongside Case B v1.1, so Case A's
figures here are a FRESH re-run (not a citation of the historical
results/development/monte_carlo_summary.json, which is left untouched and
unmodified -- Case A "must not move": this run is also the mechanism that
would catch it if it did).

Case B v1.1 shares the identical six risks, ratings, and consequence
descriptors with the historical Case B (only its ACS/predicate structure
differs), so this is expected to reproduce the historical Case B figures --
but reproduced, not assumed. This reuses the exact same specification
(K=250,000, seed=20260201, preregistration/monte_carlo_distributions_v1.json),
the same gcir.coverage.approved_gate_vector / residual_scores machinery, run
through the real compiled bundles.

Writes results/development/monte_carlo_summary_case_b_v11.json /
monte_carlo_per_risk_case_b_v11.csv -- separate from the historical
monte_carlo_summary.json, which is left untouched.

    python -m experiments.run_monte_carlo_case_b_v11
    python -m experiments.run_monte_carlo_case_b_v11 --phase final_v5 --output results/final_v5

Phase is always EXPLICIT, never inferred from git state (gap-audit item 5):
with no ``--phase``, behavior is byte-for-byte the historical default. Passing
``--phase``/``--output`` bypasses experiments.common.write_result's legacy
final/final_v2/final_v3-only directory resolution (no notion of "final_v5")
and writes directly to the given directory with the given phase label.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments import run_monte_carlo as v10  # noqa: E402
from experiments.common import environment, read_json, write_csv, write_result  # noqa: E402

CASES = ("case_a", "case_b_v1_1")

#: Historical reference figures this run must reproduce, not assume.
HISTORICAL = {
    "case_a": {"max_FP_heat": 0.321268, "mcse": 0.000934, "risk_id": "R-06",
               "GD_approved": 3, "GD_min_mean": 3.226356},
    "case_b_v1_1": {"max_FP_heat": 0.317980, "mcse": 0.000931, "risk_id": "B-01",
                     "GD_approved": 4, "GD_min_mean": 0.0},
}


def run(draws=250000, final="development", phase_override=None, output_override=None):
    spec = read_json(v10.SPEC_PATH)
    payload = {
        "cases": list(CASES),
        "note": (
            "Case A is re-run here explicitly, paired with Case B v1.1, exactly "
            "as experiments/run_determinism_case_b_v11.py pairs them for "
            "determinism -- this is fresh evidence, not a citation of the "
            "historical monte_carlo_summary.json (untouched). Case B v1.1 "
            "shares the historical Case B's six risks and rating distributions "
            "exactly; this run REPRODUCES the historical Case B figures through "
            "the real Case B v1.1 compiled bundle rather than assuming them "
            "unchanged (runbook item G)."
        ),
        "specification": spec,
        "provenance_warning": spec["provenance"]["statement"],
        "per_case": {},
    }

    per_risk_rows = []
    for case_id in CASES:
        analysis = v10.analyse_case(case_id, draws, spec, spec["perturbation_rule"], spec["seed"])
        payload["per_case"][case_id] = analysis
        per_risk_rows.extend(analysis["per_risk"])
        print(
            "%s  K=%d  seed=%d  max FP_heat=%.6f (%s, MCSE %.6f)  max FP_C*=%.6f  "
            "E[gate changes]=%.4f  C* changes observed=%d  GD_approved=%d  GD_min_mean=%.6f"
            % (case_id, draws, spec["seed"], analysis["max_FP_heat"]["value"],
               analysis["max_FP_heat"]["risk_id"], analysis["max_FP_heat"]["mcse"],
               analysis["max_FP_cstar"], analysis["expected_gate_changes_per_register_heatmap"],
               analysis["cstar_membership_changes_observed"], analysis["GD_approved"],
               analysis["GD_min_mean"])
        )

    csv_fieldnames = ["case", "risk_id", "approved_L", "approved_I", "approved_score",
                      "approved_gate", "heatmap_gate_approved", "FP_heat", "FP_heat_mcse",
                      "FP_cstar", "distance_to_threshold"]

    if phase_override is not None:
        # Explicit phase/output (gap-audit item 5): bypasses
        # experiments.common.write_result's legacy final/final_v2/final_v3-only
        # directory resolution, which has no notion of e.g. "final_v5".
        import csv as csv_module

        os.makedirs(output_override, exist_ok=True)
        document = {
            "result_name": "monte_carlo_summary_case_b_v11",
            "phase": phase_override,
            "phase_note": ("DEVELOPMENT result. Not a reportable number."
                            if phase_override == "development" else
                            "%s result, produced under the named phase; not inferred "
                            "from git state." % phase_override),
            "environment": environment(),
            "result": payload,
        }
        json_path = os.path.join(output_override, "monte_carlo_summary_case_b_v11.json")
        with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")

        csv_path = os.path.join(output_override, "monte_carlo_per_risk_case_b_v11.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv_module.DictWriter(handle, fieldnames=csv_fieldnames)
            writer.writeheader()
            for row in per_risk_rows:
                writer.writerow(row)
    else:
        write_result(final, "monte_carlo_summary_case_b_v11", payload)
        write_csv(final, "monte_carlo_per_risk_case_b_v11.csv", csv_fieldnames, per_risk_rows)

    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default=None,
                         help="explicit phase label (e.g. final_v5); default preserves the "
                              "historical development-only behavior unchanged")
    parser.add_argument("--output", default=None,
                         help="directory to write into when --phase is given "
                              "(required together with --phase)")
    args = parser.parse_args(argv)

    if args.phase and not args.output:
        parser.error("--phase requires --output")

    payload = run(phase_override=args.phase, output_override=args.output)
    all_match = True
    for case_id, expected in HISTORICAL.items():
        analysis = payload["per_case"][case_id]
        matches = (
            analysis["max_FP_heat"]["risk_id"] == expected["risk_id"]
            and abs(analysis["max_FP_heat"]["value"] - expected["max_FP_heat"]) < 1e-6
            and abs(analysis["max_FP_heat"]["mcse"] - expected["mcse"]) < 1e-5
            and analysis["GD_approved"] == expected["GD_approved"]
            and abs(analysis["GD_min_mean"] - expected["GD_min_mean"]) < 1e-6
        )
        all_match = all_match and matches
        print(
            "%s matches historical figures (FP_heat=%.6f risk=%s MCSE=%.6f "
            "GD_approved=%d GD_min_mean=%.6f): %s"
            % (case_id, expected["max_FP_heat"], expected["risk_id"], expected["mcse"],
               expected["GD_approved"], expected["GD_min_mean"],
               "YES -- REPRODUCED, not assumed" if matches else "NO -- DRIFT, investigate; STOP, do not update the expected value")
        )
    return 0 if all_match else 1


if __name__ == "__main__":
    raise SystemExit(main())
