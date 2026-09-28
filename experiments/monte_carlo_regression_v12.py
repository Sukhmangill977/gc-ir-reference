"""Monte Carlo / gate regression (Paper 2 v1.2 spec section 11).

    python -m experiments.monte_carlo_regression_v12

NOT the central new Paper-2 experiment. Uses the EXISTING implementation
(``experiments.run_monte_carlo_case_b_v11``) unmodified -- K=250000,
seed=20260201, ``preregistration/monte_carlo_distributions_v1.json`` -- and
reruns it as a regression check, reporting flip values, MCSE, and GD/GDmin.
Wording: "C*-based consequence-gate assignment". This is explicitly NOT
"seven-class stability" or "class-gated" (spec section 11) -- those terms
belong to schema v1.2's PRIMARY_CLASSES vocabulary (auth/meta/standing/
state/evidence/human/audit) and must not be conflated with the C*
(consequence-classification) gate-assignment mechanism this Monte Carlo
analysis actually measures.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402


def run():
    from experiments import run_monte_carlo_case_b_v11 as v11

    payload = v11.run()  # unmodified existing implementation; writes results/development/ as always

    all_match_historical = True
    per_case_regression = {}
    for case_id, expected in v11.HISTORICAL.items():
        analysis = payload["per_case"][case_id]
        matches = (
            abs(analysis["max_FP_heat"]["value"] - expected["max_FP_heat"]) < 1e-6
            and analysis["GD_approved"] == expected["GD_approved"]
        )
        all_match_historical = all_match_historical and matches
        per_case_regression[case_id] = {
            "max_FP_heat": analysis["max_FP_heat"]["value"],
            "max_FP_heat_risk_id": analysis["max_FP_heat"]["risk_id"],
            "mcse": analysis["max_FP_heat"]["mcse"],
            "GD_approved": analysis["GD_approved"],
            "GD_min_mean": analysis["GD_min_mean"],
            "matches_historical_baseline": matches,
        }

    return {
        "wording": "C*-based consequence-gate assignment",
        "explicitly_not": ["seven-class stability", "class-gated"],
        "K": payload["specification"]["draws"] if "draws" in payload["specification"] else 250000,
        "seed": payload["specification"].get("seed"),
        "cases": payload["cases"],
        "per_case_regression": per_case_regression,
        "regression_status": "REPRODUCES historical baseline" if all_match_historical else "DEVIATES from historical baseline",
        "all_match_historical_baseline": all_match_historical,
        "source_summary_files": [
            "results/development/monte_carlo_summary_case_b_v11.json",
            "results/development/monte_carlo_per_risk_case_b_v11.csv",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run()
    document = {
        "result_name": "monte_carlo_regression_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "monte_carlo.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print(json.dumps(report["per_case_regression"], indent=2))
    print("-> %s" % out_path)
    return 0 if report["all_match_historical_baseline"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
