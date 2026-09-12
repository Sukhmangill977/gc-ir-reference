"""Compare every CI platform's Case A + Case B v1.1 determinism summary
against the committed prospective-v4 reference hashes.

    python -m experiments.check_ci_agreement_case_b_v11 downloaded/

Sibling of experiments/check_ci_agreement.py, retargeted at the prospective
v4 state (Case A + Case B v1.1) instead of the historical (Case A + Case B)
pair -- kept as a separate module so the historical checker, its workflow
job, and its historical evidence are never touched. Each matrix leg uploads
its determinism_summary_case_b_v11.json (written by
experiments/run_determinism_case_b_v11.py); this script asserts every leg
reported TD = 1.0 and the same reference hashes committed in
cases/case_a/expected/reference_hashes.json and
cases/case_b_v1_1/expected/reference_hashes.json.

Do not cite the historical (v2-era) cross-platform run as evidence for this
prospective v4 state (runbook item F) -- this script and its own workflow
job are the v4-specific replication.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

from experiments.common import REPO_ROOT, read_json


def committed_hashes():
    return {
        "case_a": read_json(os.path.join(
            REPO_ROOT, "cases", "case_a", "expected", "reference_hashes.json"
        ))["canonical_payload_sha256"],
        "case_b_v1_1": read_json(os.path.join(
            REPO_ROOT, "cases", "case_b_v1_1", "expected", "reference_hashes.json"
        ))["payload_hash"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="directory the artifacts were downloaded into")
    parser.add_argument("--out", default=None, help="write a CI_STATUS_CASE_B_V11.md here")
    args = parser.parse_args(argv)

    committed = committed_hashes()
    print("Committed prospective-v4 reference hashes:")
    for case, digest in sorted(committed.items()):
        print("  %-14s %s" % (case, digest))
    print("")

    pattern = os.path.join(args.root, "*", "determinism_summary_case_b_v11.json")
    paths = sorted(glob.glob(pattern))
    if not paths:
        print("no determinism_summary_case_b_v11.json artifacts found under %r" % args.root)
        return 1

    rows = []
    ok = True
    for path in paths:
        leg = os.path.basename(os.path.dirname(path))
        summary = read_json(path)
        summary = summary.get("result", summary)
        td = summary["TD"]["value"]
        leg_ok = td == 1.0
        for case, expected in committed.items():
            actual = summary["per_case"][case]["reference_hash"]
            matched = actual == expected
            leg_ok = leg_ok and matched
            rows.append({
                "leg": leg, "case": case, "expected": expected, "actual": actual,
                "matched": matched, "TD": td,
            })
        ok = ok and leg_ok
        print("%-40s TD=%s  %s" % (leg, td, "OK" if leg_ok else "MISMATCH <<<"))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write("# Cross-platform agreement: Case A + Case B v1.1 (prospective v4)\n\n")
            handle.write("| leg | case | TD | reference hash matches |\n|---|---|---|---|\n")
            for row in rows:
                handle.write("| %s | %s | %s | %s |\n" % (
                    row["leg"], row["case"], row["TD"], "yes" if row["matched"] else "NO"))
            handle.write("\nOverall: %s\n" % ("PASS" if ok else "FAIL"))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
