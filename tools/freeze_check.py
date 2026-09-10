"""freeze_check.py -- one-command reproduction of the frozen reported numbers.

    python tools/freeze_check.py            # check against the committed references
    python tools/freeze_check.py --json     # machine-readable
    python tools/freeze_check.py --final-v3 # check the final_v3 campaign's files
    python tools/freeze_check.py --final-v2 # check the final_v2 campaign's files

This is the entry point the artifact-runs memo names.  It is a **thin
compatibility wrapper**: it adds no freeze logic of its own.  The authoritative
implementations live where they already were and are simply called from here --

    experiments/verify_freeze.py   frozen-file / ancestry verification
    experiments/verify_hashes.py   committed reference canonical payload hashes
    src/gcir/metrics.py            DC, RCY, NDR, OPR, ODC, PTC, CV
    src/gcir/coverage.py           GD(T_H), GD_min
    experiments/run_determinism.py TD

-- so there is exactly one definition of each check, and this file cannot drift
away from it.

What it verifies, in one run:

  1. Both cases compile, and their canonical payload hashes equal the committed
     reference values.
  2. The thirteen frozen reported numbers recompute from the compiled artifacts.
  3. The frozen-file manifest still matches the freeze commit, and no frozen file
     changed between the freeze and the campaign.
  4. The Case B -> L-DREA traceability mapping still verifies against the
     external artifact of record.

Exit code 0 means every check passed.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)


#: The reported numbers this script reproduces.  The memo calls them "the
#: thirteen frozen numbers"; they are enumerated here so the count is auditable
#: rather than asserted.
FROZEN_NUMBERS = (
    ("case_a", "DC"), ("case_a", "RCY"), ("case_a", "NDR"), ("case_a", "OPR"),
    ("case_a", "ODC"), ("case_a", "PTC"), ("case_a", "CV"),
    ("case_a", "GD"), ("case_a", "GD_min"),
    ("case_b", "CV"), ("case_b", "GD"), ("case_b", "GD_min"),
    ("both", "TD"),
)


def _newest_freeze_tag():
    """The most recent ``preregister-tier0-*`` tag reachable from HEAD."""
    import subprocess

    described = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "--match", "preregister-tier0-*"],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    if described.returncode == 0 and described.stdout.strip():
        return described.stdout.decode("utf-8").strip()
    return "preregister-tier0-v2.2"


def _load_result(directory, name):
    path = os.path.join(directory, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        blob = json.load(handle)
    return blob.get("result", blob)


def check(results_dir):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.metrics import compute_all

    findings = []
    report = {"checks": [], "numbers": {}, "results_dir": results_dir}

    def record(name, passed, detail=""):
        report["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            findings.append("%s -- %s" % (name, detail))
        print("  [%s] %-58s %s" % ("PASS" if passed else "FAIL", name, detail))

    # ---- 1. compile both cases and check the committed reference hashes ----
    print("\n1. Case compilation and committed reference hashes")
    compiled = {}
    for case_id in ("case_a", "case_b"):
        case = load_case(case_id)
        inputs = case.compiler_inputs()
        result = compile_bundle(inputs)
        compiled[case_id] = (case, inputs, result)

        reference_path = os.path.join(
            REPO_ROOT, "cases", case_id, "expected", "reference_hashes.json")
        with open(reference_path, encoding="utf-8") as handle:
            expected = json.load(handle)["canonical_payload_sha256"]
        actual = result.bundle.payload_hash
        record("%s canonical payload hash" % case_id, actual == expected,
               actual if actual == expected else "%s != %s" % (actual, expected))
        report.setdefault("payload_hashes", {})[case_id] = actual

    # ---- 2. the frozen reported numbers ----------------------------------
    print("\n2. Frozen reported numbers")
    metrics = {}
    for case_id, (case, inputs, result) in compiled.items():
        metrics[case_id] = compute_all(
            inputs.assessment, result.bundle,
            [inv["invariant_id"] for inv in inputs.invariants],
            case.parameters["declared_heatmap_threshold"],
        )

    for case_id, name in FROZEN_NUMBERS:
        if case_id == "both":
            continue
        entry = metrics[case_id][name]
        value = entry["value"]
        report["numbers"]["%s.%s" % (case_id, name)] = value
        if name in ("GD", "GD_min"):
            record("%s %s = %s" % (case_id, name, value), value is not None,
                   "over %d register rows" % len(metrics[case_id]["gate_vector"]))
        else:
            record("%s %s = %.4f (%s/%s)"
                   % (case_id, name, value, entry["numerator"], entry["denominator"]),
                   value is not None, entry.get("required", ""))

    # required values
    record("case_a DC = 1.000 (release admissible)",
           metrics["case_a"]["DC"]["value"] == 1.0, "")
    record("case_a OPR = 0.000 (no orphan predicates)",
           metrics["case_a"]["OPR"]["value"] == 0.0, "")
    record("case_a CV = 1.000 (C* coverage complete)",
           metrics["case_a"]["CV"]["value"] == 1.0, "")
    record("case_b CV = 1.000 (C* coverage complete)",
           metrics["case_b"]["CV"]["value"] == 1.0, "")

    # ---- 3. TD, from the campaign's own result file -----------------------
    print("\n3. Translation determinism")
    determinism = _load_result(results_dir, "determinism_summary.json")
    if determinism is None:
        record("TD result file present", False,
               "no determinism_summary.json in %s -- run the determinism experiment"
               % os.path.relpath(results_dir, REPO_ROOT))
    else:
        td = determinism["TD"]["value"]
        report["numbers"]["both.TD"] = td
        record("TD = %s (%d/%d runs)"
               % (td, determinism["TD"]["numerator"], determinism["TD"]["denominator"]),
               td == 1.0, str(determinism.get("stratum_breakdown", "")))
        for case_id in ("case_a", "case_b"):
            per = determinism["per_case"][case_id]
            record("%s determinism reference hash matches the compiled bundle" % case_id,
                   per["reference_hash"] == report["payload_hashes"][case_id],
                   per["reference_hash"])

    print("\n   (%d frozen numbers enumerated)" % len(FROZEN_NUMBERS))

    # ---- 4. frozen-file / ancestry verification ---------------------------
    print("\n4. Frozen-file and ancestry verification")
    from experiments import verify_freeze as vf

    # Resolve the governing freeze tag rather than hardcoding one: a hardcoded
    # default goes stale the moment a freeze is incremented, and this file is
    # itself frozen, so it must not need editing when that happens.
    tag = os.environ.get("GCIR_FREEZE_TAG") or _newest_freeze_tag()
    freeze_commit = vf.git("rev-list", "-n", "1", tag)
    if freeze_commit is None:
        record("freeze tag %r exists" % tag, False,
               "not found; freeze verification skipped")
    else:
        code = vf.main(["--tag", tag, "--results", results_dir])
        record("verify_freeze (%s)" % tag, code == 0,
               "see the block above for detail")

    # ---- 5. Case B -> L-DREA traceability --------------------------------
    print("\n5. Case B -> L-DREA traceability")
    mapping_path = os.path.join(REPO_ROOT, "cases", "case_b", "ldrea_traceability.json")
    if not os.path.exists(mapping_path):
        record("ldrea_traceability.json present", False, mapping_path)
    else:
        with open(mapping_path, encoding="utf-8") as handle:
            mapping = json.load(handle)
        record("every mapping row verified",
               mapping["summary"]["failed"] == 0,
               "%d rows: %s" % (mapping["summary"]["rows"],
                                mapping["summary"]["by_correspondence"]))
        record("mapped Case B bundle hash matches the compiled bundle",
               mapping["summary"]["case_b_bundle_hash"] == report["payload_hashes"]["case_b"],
               mapping["summary"]["case_b_bundle_hash"])

    report["passed"] = not findings
    report["failure_count"] = len(findings)
    report["findings"] = findings
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", default=None,
                        help="results directory to read TD from "
                             "(default: results/final_v3 if present, else results/final_v2, else results/final)")
    parser.add_argument("--final-v3", action="store_true",
                        help="shorthand for --results results/final_v3")
    parser.add_argument("--final-v2", action="store_true",
                        help="shorthand for --results results/final_v2")
    parser.add_argument("--json", action="store_true", help="emit JSON on stdout")
    args = parser.parse_args(argv)

    if args.results:
        results_dir = args.results
    elif args.final_v3:
        results_dir = os.path.join(REPO_ROOT, "results", "final_v3")
    elif args.final_v2:
        results_dir = os.path.join(REPO_ROOT, "results", "final_v2")
    else:
        candidate = os.path.join(REPO_ROOT, "results", "final_v3")
        if os.path.isdir(candidate):
            results_dir = candidate
        else:
            candidate = os.path.join(REPO_ROOT, "results", "final_v2")
            results_dir = candidate if os.path.isdir(candidate) else os.path.join(
                REPO_ROOT, "results", "final")

    print("=" * 78)
    print("freeze_check.py -- GC-IR reference implementation")
    print("reading determinism results from: %s"
          % os.path.relpath(results_dir, REPO_ROOT))
    print("=" * 78)

    report = check(results_dir)

    print("\n" + "=" * 78)
    if report["passed"]:
        print("FREEZE CHECK PASSED -- %d checks, 0 failures"
              % len(report["checks"]))
    else:
        print("FREEZE CHECK FAILED -- %d of %d checks failed"
              % (report["failure_count"], len(report["checks"])))
        for finding in report["findings"]:
            print("  %s" % finding)
    print("=" * 78)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
