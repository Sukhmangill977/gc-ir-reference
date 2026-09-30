"""Record a machine-readable result for `make ieee-check-v5`.

    python tools/record_ieee_check_v5_result.py --stages 4 --status PASSED

Writes results/final_v5/ieee_check_v5_result.json -- a separate file from
results/development/ieee_check_result.json and
results/development/ieee_check_v4_result.json, both left untouched. Called
as the final line of the Makefile's `ieee-check-v5` recipe.

Reaching this script at all already means every prior stage in the recipe
exited zero (each Makefile recipe line is a separate shell and `make` stops
at the first non-zero exit), so there is no partial-failure state to record
beyond "not yet run" (file absent) and "last run passed" (file present,
status PASSED).
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STAGE_NAMES = [
    "environment",
    "full test suite (pytest, all suites)",
    "prospective-v5 freeze check (Surface A, Case D CCS0/CCS1/CCS2, validator "
    "matrix, Q1-Q10, historical + new negative fixtures, 155-run local "
    "determinism, cross-environment CI + container, GD/GDmin Monte Carlo, "
    "compile timing, observation diagnostics, Case B integration, MANIFEST "
    "working-tree self-consistency, historical tags unchanged)",
    "manuscript-number verifier (paper.docx against results/final_v5/campaign_results.json)",
]


def _git_head():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception:  # noqa: BLE001 -- best-effort provenance, never fatal
        return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stages", type=int, default=len(STAGE_NAMES))
    parser.add_argument("--status", default="PASSED")
    args = parser.parse_args(argv)

    result = {
        "check": "ieee-check-v5",
        "scope": "prospective preregister-tier0-v5 state plus manuscript verification "
                 "(NOT a historical freeze check; NOT the v1.2.0 release itself)",
        "status": args.status,
        "stage_count": args.stages,
        "stages": STAGE_NAMES[: args.stages],
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": _git_head(),
    }

    out_dir = os.path.join(REPO_ROOT, "results", "final_v5")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ieee_check_v5_result.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("recorded ieee-check-v5 result -> %s" % out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
