"""Compare every CI platform's Case D CCS0/CCS1/CCS2 determinism summary
against their committed reference hashes (Paper 2 v1.2 spec section 8:
cross-environment determinism, recommended but secondary to the local
per-case result).

    python -m experiments.check_ci_agreement_case_d downloaded/

Sibling of experiments/check_ci_agreement_case_b_v11.py, retargeted at Case D
-- kept as its own module and its own workflow job pair so neither the
historical (Case A + Case B) nor the prospective-v4 (Case A + Case B v1.1)
checker, job, or evidence is ever touched. Each matrix leg uploads the
determinism.json written by experiments/run_determinism_v12.py's
``--cases case_d_ccs0 case_d_ccs1 case_d_ccs2`` invocation; this script
asserts every leg reproduced TD = 1.0 for all three CCS states and the
reference hash committed in each cases/case_d_ccs<N>/expected/reference_hashes.json
(gap-audit item 3: CCS0/CCS2 must not be absent from Case D determinism/CI).
"""

from __future__ import annotations

import argparse
import glob
import os

from experiments.common import REPO_ROOT, read_json

CASES = ("case_d_ccs0", "case_d_ccs1", "case_d_ccs2")


def committed_hashes():
    return {
        case_id: read_json(os.path.join(
            REPO_ROOT, "cases", case_id, "expected", "reference_hashes.json"
        ))["payload_hash"]
        for case_id in CASES
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="directory the artifacts were downloaded into")
    parser.add_argument("--out", default=None, help="write a CI_STATUS_CASE_D.md here")
    args = parser.parse_args(argv)

    expected = committed_hashes()
    for case_id, h in expected.items():
        print("Committed %s reference hash: %s" % (case_id, h))
    print()

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
        leg_ok = td == 1.0
        for case_id in CASES:
            per_case = summary["per_case"].get(case_id)
            if per_case is None:
                leg_ok = False
                rows.append({"leg": leg, "case": case_id, "expected": expected[case_id],
                             "actual": None, "matched": False, "TD": td})
                continue
            actual = per_case["reference_hash"]
            matched = actual == expected[case_id]
            leg_ok = leg_ok and matched
            rows.append({"leg": leg, "case": case_id, "expected": expected[case_id],
                         "actual": actual, "matched": matched, "TD": td})
        ok = ok and leg_ok
        print("%-40s TD=%s  %s" % (leg, td, "OK" if leg_ok else "MISMATCH <<<"))

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write("# Cross-platform agreement: Case D (CCS0, CCS1, CCS2)\n\n")
            handle.write("| leg | case | TD | reference hash matches |\n|---|---|---|---|\n")
            for row in rows:
                handle.write("| %s | %s | %s | %s |\n"
                              % (row["leg"], row["case"], row["TD"], "yes" if row["matched"] else "NO"))
            handle.write("\nOverall: %s\n" % ("PASS" if ok else "FAIL"))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
