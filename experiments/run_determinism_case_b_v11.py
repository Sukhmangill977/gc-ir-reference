"""Translation determinism, run explicitly for Case A and Case B v1.1
(runbook item 4).

This is NOT a re-labeling of the historical experiments/run_determinism.py
output (which covers Case A and the historical six-ACS Case B and writes
results/development/determinism_runs.csv / determinism_summary.json -- left
untouched by this script). This reuses that module's actual matrix-building
and single-run execution functions, but targets Case B v1.1 explicitly and
writes to separately named files so neither run's evidence overwrites the
other's.

Same frozen 31-run-per-case design as the historical experiment: 10 repeat,
10 row_shuffle, 5 key_shuffle, 3 locale, 3 timezone = 31 per case, 62 total.

    python -m experiments.run_determinism_case_b_v11
    python -m experiments.run_determinism_case_b_v11 --phase final_v5 --output results/final_v5

Phase is always EXPLICIT, never inferred from git state (gap-audit item 5):
with no ``--phase``, behavior is byte-for-byte the historical default
(writes results/development/determinism_summary_case_b_v11.json via
experiments.common.write_result, phase="development", exactly as before).
Passing ``--phase``/``--output`` bypasses that legacy final/final_v2/final_v3
directory resolution (which has no notion of "final_v5") and writes directly
to the given directory with the given phase label -- e.g. for the actual
final v1.2.0 campaign, run this from a CLEAN checkout
(git status --porcelain empty) with --phase final_v5, so the recorded
git_describe has no "-dirty" suffix because the tree really is clean, not
because the suffix was edited out after the fact.

    python -m experiments.run_determinism_case_b_v11
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments import run_determinism as v10  # noqa: E402
from experiments.common import environment, write_csv, write_result  # noqa: E402

CASES = ("case_a", "case_b_v1_1")


def run(runs_per_case=v10.TOTAL_RUNS_PER_CASE, final="development",
        phase_override=None, output_override=None):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.metrics import translation_determinism

    matrix = v10.build_matrix(runs_per_case)
    rows = []
    per_case = {}

    for case_id in CASES:
        case = load_case(case_id)
        reference = compile_bundle(case.compiler_inputs()).bundle.payload_hash
        per_case[case_id] = {"reference_hash": reference, "runs": 0, "matches": 0}

        for index, entry in enumerate(matrix, start=1):
            run_id = "%s-%03d" % (case_id, index)
            if entry["clean_process"]:
                digest = v10.run_in_subprocess(case_id, entry)
                locale_applied = entry["locale"]
                execution = "clean_process"
            else:
                digest, locale_applied = v10.run_in_process(case_id, entry)
                execution = "in_process"

            fingerprint = v10._environment_fingerprint(entry, execution)
            matched = digest == reference
            per_case[case_id]["runs"] += 1
            per_case[case_id]["matches"] += 1 if matched else 0
            rows.append({
                "run_id": run_id, "case": case_id, "stratum": entry["stratum"],
                "permutation": entry["label"], "numeric_form": entry["numeric_form"],
                "environment_fingerprint": fingerprint,
                "permutation_spec": json.dumps(entry["spec"], sort_keys=True),
                "permutation_seed": entry["permutation_seed"], "environment": execution,
                "python_hash_seed": entry["python_hash_seed"], "locale": locale_applied,
                "timezone": entry["timezone"], "hash": digest, "reference_hash": reference,
                "pass": "PASS" if matched else "FAIL",
            })
            print("  %s %-12s %-16s %-14s %-18s %s"
                  % (run_id, entry["stratum"], entry["label"], entry["locale"],
                     entry["timezone"], "PASS" if matched else "FAIL <<<"))

    overall_matches = sum(1 for row in rows if row["pass"] == "PASS")
    td_by_case = {
        case_id: translation_determinism(
            [row["hash"] for row in rows if row["case"] == case_id],
            per_case[case_id]["reference_hash"],
        )["TD"]
        for case_id in CASES
    }

    summary = {
        "cases": list(CASES),
        "note": (
            "Case A here is the SAME frozen historical case, run again through "
            "this explicit Case-B-v1.1-paired harness rather than reused from "
            "experiments/run_determinism.py's output, per runbook item 4. Case "
            "B v1.1 evidence here is NEW -- it is not a relabeling of the "
            "historical six-ACS Case B's determinism run."
        ),
        "runs_per_case": runs_per_case,
        "total_runs": len(rows),
        "matches": overall_matches,
        "TD": {
            "value": overall_matches / len(rows) if rows else None,
            "numerator": overall_matches, "denominator": len(rows),
        },
        "per_case": {
            case_id: {
                "reference_hash": per_case[case_id]["reference_hash"],
                "runs": per_case[case_id]["runs"],
                "matches": per_case[case_id]["matches"],
                "TD": td_by_case[case_id],
            }
            for case_id in CASES
        },
        "failures": [row for row in rows if row["pass"] == "FAIL"],
    }

    fieldnames = ["run_id", "case", "stratum", "permutation", "numeric_form",
                  "environment_fingerprint", "permutation_spec", "permutation_seed",
                  "environment", "python_hash_seed", "locale", "timezone", "hash",
                  "reference_hash", "pass"]

    if phase_override is not None:
        # Explicit phase/output (gap-audit item 5): bypasses
        # experiments.common.write_result's legacy final/final_v2/final_v3-only
        # directory resolution, which has no notion of e.g. "final_v5".
        import csv as csv_module

        os.makedirs(output_override, exist_ok=True)
        document = {
            "result_name": "determinism_summary_case_b_v11",
            "phase": phase_override,
            "phase_note": ("DEVELOPMENT result. Not a reportable number."
                            if phase_override == "development" else
                            "%s result, produced under the named phase; not inferred "
                            "from git state." % phase_override),
            "environment": environment(),
            "result": summary,
        }
        json_path = os.path.join(output_override, "determinism_summary_case_b_v11.json")
        with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")

        csv_path = os.path.join(output_override, "determinism_runs_case_b_v11.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv_module.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
    else:
        csv_path = write_csv(final, "determinism_runs_case_b_v11.csv", fieldnames, rows)
        write_result(final, "determinism_summary_case_b_v11", summary)

    print("\nTD = %s (%d/%d)  ->  %s" % (summary["TD"]["value"], overall_matches, len(rows), csv_path))
    return summary


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

    summary = run(phase_override=args.phase, output_override=args.output)
    return 0 if summary["TD"]["value"] == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
