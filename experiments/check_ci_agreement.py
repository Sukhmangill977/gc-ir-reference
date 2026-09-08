"""Compare every CI platform's determinism summary against the committed hashes.

    python -m experiments.check_ci_agreement downloaded/

Used by the ``cross-platform-agreement`` job.  Each matrix leg uploads its
``determinism_summary.json``; this script asserts that every leg reported
``TD = 1.0`` and the same reference canonical payload hash as the value committed
in ``cases/<case>/expected/reference_hashes.json``.

If this passes, the supportable wording is "deterministic across the tested
supported environments".  It is never "platform independent": three runner images
are not the set of all environments.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

from experiments.common import REPO_ROOT, read_json

CASES = ("case_a", "case_b")


def committed_hashes():
    return {
        case: read_json(os.path.join(
            REPO_ROOT, "cases", case, "expected", "reference_hashes.json"
        ))["canonical_payload_sha256"]
        for case in CASES
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", help="directory the artifacts were downloaded into")
    parser.add_argument("--out", default=None, help="write a CI_STATUS.md here")
    args = parser.parse_args(argv)

    committed = committed_hashes()
    print("Committed reference hashes:")
    for case, digest in sorted(committed.items()):
        print("  %-8s %s" % (case, digest))
    print("")

    pattern = os.path.join(args.root, "*", "determinism_summary.json")
    paths = sorted(glob.glob(pattern))
    problems = []
    rows = []

    for path in paths:
        leg = os.path.basename(os.path.dirname(path))
        blob = read_json(path)
        result = blob["result"]
        env = blob["environment"]
        td = result["TD"]["value"]
        if td != 1.0:
            problems.append("%s: TD = %s (%d/%d)"
                            % (leg, td, result["TD"]["numerator"],
                               result["TD"]["denominator"]))
        for case in CASES:
            actual = result["per_case"][case]["reference_hash"]
            if actual != committed[case]:
                problems.append("%s: %s hash %s != committed %s"
                                % (leg, case, actual, committed[case]))
        rows.append({
            "leg": leg,
            "platform": env["platform"],
            "python": env["python_version"],
            "TD": td,
            "runs": result["TD"]["denominator"],
            "case_a": result["per_case"]["case_a"]["reference_hash"],
            "case_b": result["per_case"]["case_b"]["reference_hash"],
        })
        print("  %-46s TD=%-5s runs=%-4d %s %s"
              % (leg, td, result["TD"]["denominator"],
                 rows[-1]["case_a"][:16], rows[-1]["case_b"][:16]))

    if not paths:
        problems.append("no determinism summaries were found under %r" % args.root)

    if args.out:
        lines = [
            "# Cross-platform determinism -- CI status",
            "",
            "Measured by `.github/workflows/determinism.yml`. Each matrix leg compiles",
            "both cases and runs the determinism experiment; this table is generated",
            "from the uploaded result files.",
            "",
            "| CI leg | platform | python | TD | runs | Case A hash | Case B hash |",
            "|---|---|---|---|---|---|---|",
        ]
        for row in rows:
            lines.append("| %s | %s | %s | %s | %d | `%s` | `%s` |"
                         % (row["leg"], row["platform"], row["python"], row["TD"],
                            row["runs"], row["case_a"], row["case_b"]))
        lines += [
            "",
            "Committed reference hashes:",
            "",
            "| case | canonical payload SHA-256 |",
            "|---|---|",
        ]
        for case, digest in sorted(committed.items()):
            lines.append("| %s | `%s` |" % (case, digest))
        lines += [
            "",
            "**Supportable wording:** deterministic across the tested supported",
            "environments. **Not** platform independence -- three runner images are not",
            "the set of all environments (manuscript Section XII, determinism scope).",
            "",
        ]
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(lines))
        print("\nwrote %s" % args.out)

    if problems:
        print("\nFAILED:")
        for problem in problems:
            print("  %s" % problem)
        return 1
    print("\nAll %d platform/python combinations agree with the committed reference "
          "hashes." % len(paths))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
