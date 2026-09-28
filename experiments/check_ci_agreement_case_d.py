"""Compare every CI platform's Case D CCS1 determinism summary against the
committed reference hash (Paper 2 v1.2 spec section 8: cross-environment
determinism, recommended but secondary to the 93-run local result).

    python -m experiments.check_ci_agreement_case_d downloaded/

Sibling of experiments/check_ci_agreement_case_b_v11.py, retargeted at Case D
CCS1 -- kept as its own module and its own workflow job pair so neither the
historical (Case A + Case B) nor the prospective-v4 (Case A + Case B v1.1)
checker, job, or evidence is ever touched. Each matrix leg uploads the
determinism.json written by experiments/run_determinism_v12.py's
``--cases case_d_ccs1`` invocation; this script asserts every leg reproduced
TD = 1.0 and the reference hash committed in
cases/case_d_ccs1/expected/reference_hashes.json.
"""

from __future__ import annotations

import argparse
import glob
import os

from experiments.common import REPO_ROOT, read_json


def committed_hash():
    return read_json(os.path.join(
        REPO_ROOT, "cases", "case_d_ccs1", "expected", "reference_hashes.json"
    ))["payload_hash"]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="directory the artifacts were downloaded into")
    parser.add_argument("--out", default=None, help="write a CI_STATUS_CASE_D.md here")
    args = parser.parse_args(argv)

    expected = committed_hash()
    print("Committed Case D CCS1 reference hash: %s\n" % expected)

    pattern = os.path.join(args.root, "*", "determinism.json")
    paths = sorted(glob.glob(pattern))
    if not paths:
        print("no determinism.json artifacts found under %r" % args.root)
        return 1

    rows = []
    ok = True
    for path in paths:
        leg = os.path.basename(os.path.dirname(path))
        summary = read_json(path)
        summary = summary.get("result", summary)
        td = summary["TD"]["value"]
        actual = summary["per_case"]["case_d_ccs1"]["reference_hash"]
        matched = actual == expected
        leg_ok = (td == 1.0) and matched
        ok = ok and leg_ok
        rows.append({"leg": leg, "expected": expected, "actual": actual, "matched": matched, "TD": td})
        print("%-40s TD=%s  %s" % (leg, td, "OK" if leg_ok else "MISMATCH <<<"))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write("# Cross-platform agreement: Case D CCS1\n\n")
            handle.write("| leg | TD | reference hash matches |\n|---|---|---|\n")
            for row in rows:
                handle.write("| %s | %s | %s |\n" % (row["leg"], row["TD"], "yes" if row["matched"] else "NO"))
            handle.write("\nOverall: %s\n" % ("PASS" if ok else "FAIL"))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
