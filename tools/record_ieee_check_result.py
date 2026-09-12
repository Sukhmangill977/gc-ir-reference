"""Record a machine-readable result for `make ieee-check`.

    python tools/record_ieee_check_result.py --stages 8 --status PASSED

Writes results/development/ieee_check_result.json. Called as the final line
of the Makefile's `ieee-check` recipe, after every preceding stage's own
recipe line has already exited zero (each Makefile recipe line is a separate
shell and `make` stops at the first non-zero exit -- so reaching this script
at all already means every prior stage passed; there is no partial-failure
state to record here beyond "not yet run" (file absent) and "last run
passed" (file present with status PASSED)).

This closes the gap runbook item 8.B names: `tools/show_results.py` printed
the fixed string "no recorded machine-readable result" for ieee-check
unconditionally, because no stage of ieee-check had ever written one.
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
    "test suites",
    "recompile Case A and Case B",
    "committed reference payload hashes",
    "freeze verification",
    "paper-facing results vs results/final_v2/",
    "traceability audit queries and negative controls",
    "manifest currency",
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
        "check": "ieee-check",
        "status": args.status,
        "stage_count": args.stages,
        "stages": STAGE_NAMES[: args.stages],
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": _git_head(),
    }

    out_dir = os.path.join(REPO_ROOT, "results", "development")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ieee_check_result.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("recorded ieee-check result -> %s" % out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
