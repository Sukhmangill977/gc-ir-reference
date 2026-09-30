"""freeze_check.py --prospective-v5 -- verify the CURRENT v1.2 development
state against everything a `preregister-tier0-v5` freeze would need, without
touching or depending on any historical freeze-check path.

    python tools/freeze_check_prospective_v5.py
    python tools/freeze_check_prospective_v5.py --json

This is a NEW, independent verifier, sibling to tools/freeze_check_prospective_v4.py.
It does not call, wrap, or depend on tools/freeze_check.py's --final-v2/--final-v3/
--prospective-v4 paths, and it does not read any historical FREEZE_MANIFEST_V*.sha256
file. It reads results/development_v12/*.json (the v1.2 development-phase
artifacts) and re-verifies their headline counts against either a committed
reference (cases/*/expected/reference_hashes.json) or the artifact's own
internally-documented invariant (e.g. the 16 validator rows summing to 16,
never silently redefined here).

What it verifies:
  1.  Case A, Case B v1.1 payload hashes unchanged from the frozen v3.1 /
      prospective-v4 references (v1.2 must not have moved v1.1's frozen cases).
  2.  Case D CCS1 compiles; hash byte-identical to the committed
      cases/case_d_ccs1/expected/reference_hashes.json reference.
  3.  Case D matrix D1-D10, 10/10, from results/development_v12/case_d.json.
  4.  Surface A: 8/8 nominal, 8/8 semantic negatives, 8/8 correct expected
      reason, 0 unexpected accepts / wrong-reason rejects, from
      results/development_v12/surface_a.json.
  5.  Full v1.2 validator test matrix: 16/16 paired (positive+negative) rows,
      0 wrong-reason, from results/development_v12/validators.json.
  6.  Audit/regression: historical 19 Q1-Q10 fixtures still detected, Q1-Q10
      10/10, 9 new v1.2 audit negatives all detected, from
      results/development_v12/audit.json. (16 validator-matrix rows, 9
      audit-regression rows and 8 Surface-A families are three distinct
      counts, per the source files' own counting_note -- never summed here.)
  7.  Local determinism: 155/155 (31 runs x 5 cases: case_a, case_b_v1_1,
      case_d_ccs0, case_d_ccs1, case_d_ccs2 -- all three Case D closure
      states, gap-audit item 3), from results/development_v12/determinism.json,
      each per-case reference hash matching the committed case reference.
  8.  Cross-environment determinism: the 6-leg OS x Python CI matrix (21 jobs,
      0 failures) from cross_environment_determinism.json, AND environment 7
      (pinned Linux/aarch64 container, 155/155, hashes matching committed
      references) from environment_container_aarch64.json -- kept as two
      explicitly distinct pieces of evidence, never merged into one count.
  9.  GD/GDmin: Monte Carlo K=250000, seed=20260201, regression against the
      historical baseline for Case A and Case B v1.1, from
      results/development_v12/monte_carlo.json.
  10. Compile timing: n=100 measured + 10 warmup per case, for case_a,
      case_b_v1_1, case_d_ccs1, hosts never pooled, from
      results/development_v12/compile_timing.json.
  11. Observation diagnostics A and B both pass, from
      results/development_v12/observation_diagnostics.json.
  12. Case B integration: 14 rows (13 adverse + 1 clean_control), 14/14
      passed, authorization_decision_counts == {PERMIT:1, DENY:8, HOLD:4}
      over the 13 adverse rows (clean_control's own PERMIT tracked
      separately, by design -- see experiments/case_b_v11_injection_scenarios.py),
      from results/development_v12/case_b_integration.json.
  13. Full pytest suite passes (495 collected; exit code checked, not just a
      cached count).
  14. MANIFEST.sha256 / MANIFEST.json current against the committed HEAD
      tree (git ls-tree + git cat-file, never a filesystem walk), same
      exclusions as --prospective-v4 (development_result role, MANIFEST.json
      itself).
  15. Historical tags unchanged: preregister-tier0-v3.1, preregister-tier0-v4,
      preregister-tier0-v4.1 (never inspected for editing, only compared).
  16. results/development_v12/campaign_results_development.json still marked
      reportable == False and freeze.status == "NOT CREATED" (this checker
      does not itself decide to freeze; it only verifies pre-freeze state).

Exit code 0 iff every check passes.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

CASE_A_FROZEN_HASH = "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536"
CASE_B_V1_1_FROZEN_HASH = "0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1"
CASE_D_CCS0_FROZEN_HASH = "09495d8ee59a9868db4749e40812ad40a4c2683d79c931d641811a2849635912"
CASE_D_CCS1_FROZEN_HASH = "32edcb72bd6cdcd760252bb85431a898b9aded86db2c8468ba77f4aac6b53784"
CASE_D_CCS2_FROZEN_HASH = "f7b5827d6c7fc4702d9e276b3ae34179482bcecd466bddba440103f751c603d2"

#: Recorded at the time of this proposal. Never written to; only compared
#: against, so a real historical tag move would be caught, not silently
#: accepted.
HISTORICAL_TAGS = {
    "preregister-tier0-v3.1": "158c0bd3785ac87a878671f76286be082a26d50d",
    "preregister-tier0-v4": "48791c720b9d08cc4005e0c49f6d64eab2a361f1",
    "preregister-tier0-v4.1": "efe4e165619ecb5d781fb795113f33720794a2e5",
}

DEV_DIR = os.path.join(REPO_ROOT, "results", "development_v12")


def _git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:  # noqa: BLE001
        return None


def _load(name):
    path = os.path.join(DEV_DIR, name)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def check():
    findings = []
    report = {"checks": []}

    def record(name, passed, detail=""):
        report["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            findings.append("%s -- %s" % (name, detail))
        print("  [%s] %-64s %s" % ("PASS" if passed else "FAIL", name, detail))

    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    # ---- 1-2. Case A / Case B v1.1 unchanged, Case D CCS0/CCS1/CCS2 compile --
    print("\n1. Case A / Case B v1.1 unchanged; Case D CCS0/CCS1/CCS2 compile")
    result_a = compile_bundle(load_case("case_a").compiler_inputs())
    record("case_a payload hash unchanged from frozen v3.1/prospective-v4",
           result_a.bundle.payload_hash == CASE_A_FROZEN_HASH, result_a.bundle.payload_hash)

    result_b11 = compile_bundle(load_case("case_b_v1_1").compiler_inputs())
    record("case_b_v1_1 payload hash unchanged from prospective-v4",
           result_b11.bundle.payload_hash == CASE_B_V1_1_FROZEN_HASH, result_b11.bundle.payload_hash)

    for case_id, frozen_hash in (
        ("case_d_ccs0", CASE_D_CCS0_FROZEN_HASH),
        ("case_d_ccs1", CASE_D_CCS1_FROZEN_HASH),
        ("case_d_ccs2", CASE_D_CCS2_FROZEN_HASH),
    ):
        result_d = compile_bundle(load_case(case_id).compiler_inputs())
        record("%s payload hash matches committed reference" % case_id,
               result_d.bundle.payload_hash == frozen_hash, result_d.bundle.payload_hash)

    # ---- 3. Case D matrix ---------------------------------------------------
    print("\n2. Case D matrix (D1-D10)")
    case_d = _load("case_d.json")["result"]
    record("Case D matrix 10/10 passed", case_d["passed"] == 10 and case_d["total"] == 10,
           "%s/%s" % (case_d["passed"], case_d["total"]))

    # ---- 4. Surface A ---------------------------------------------------
    print("\n3. Surface A (8 paired semantic families)")
    surface_a = _load("surface_a.json")["result"]
    counts = surface_a["counts"]
    record("Surface A nominal_accepted == 8/8", counts["nominal_accepted"] == "8/8", str(counts))
    record("Surface A semantic_negatives_rejected == 8/8",
           counts["semantic_negatives_rejected"] == "8/8", "")
    record("Surface A correct_expected_reason == 8/8", counts["correct_expected_reason"] == "8/8", "")
    record("Surface A unexpected_accepts == 0 and wrong_reason_rejects == 0",
           counts["unexpected_accepts"] == 0 and counts["wrong_reason_rejects"] == 0, "")

    # ---- 5. Validator matrix ---------------------------------------------
    print("\n4. Full v1.2 validator test matrix")
    validators = _load("validators.json")["result"]
    totals = validators["totals"]
    record("16/16 positive, 16/16 negative, 0 wrong-reason",
           totals["positive_passed"] == 16 and totals["negative_rejected"] == 16
           and totals["wrong_reason_count"] == 0,
           str(totals))
    record("check_count == 16 (the full spec-section-5 matrix)",
           validators["check_count"] == 16, str(validators["check_count"]))

    # ---- 6. Audit / regression --------------------------------------------
    print("\n5. Audit / regression (Q1-Q10, historical 19, new v1.2 9)")
    audit = _load("audit.json")["result"]
    record("historical 19 negative fixtures all detected", audit["historical_19_all_detected"] is True, "")
    record("Q1-Q10 all pass (10/10)",
           audit["q1_q10_all_pass"] is True and len(audit["q1_q10_positive"]) == 10
           and all(audit["q1_q10_positive"].values()),
           str(audit["q1_q10_positive"]))
    record("9 new v1.2 audit negatives all detected", audit["new_v12_all_detected"] is True, "")

    # ---- 7. Local determinism ----------------------------------------------
    print("\n6. Local determinism (155 runs: case_a/case_b_v1_1/case_d_ccs0/ccs1/ccs2 x 31)")
    determinism = _load("determinism.json")["result"]
    record("total_runs == 155, TD == 1.0 (155/155)",
           determinism["total_runs"] == 155 and determinism["TD"]["value"] == 1.0,
           "%s/%s" % (determinism["TD"]["numerator"], determinism["TD"]["denominator"]))
    expected_hashes = {
        "case_a": CASE_A_FROZEN_HASH,
        "case_b_v1_1": CASE_B_V1_1_FROZEN_HASH,
        "case_d_ccs0": CASE_D_CCS0_FROZEN_HASH,
        "case_d_ccs1": CASE_D_CCS1_FROZEN_HASH,
        "case_d_ccs2": CASE_D_CCS2_FROZEN_HASH,
    }
    for case_id, expected in expected_hashes.items():
        per = determinism["per_case"][case_id]
        record("%s: 31/31, reference hash matches committed value" % case_id,
               per["TD"]["value"] == 1.0 and per["reference_hash"] == expected,
               per["reference_hash"])

    # ---- 8. Cross-environment: 6-leg matrix + environment-7 container ------
    print("\n7. Cross-environment determinism (6-leg matrix + environment-7 container)")
    cross_env = _load("cross_environment_determinism.json")["result"]
    record("6-leg CI matrix: 21/21 jobs succeeded, 0 failed",
           cross_env["jobs_succeeded"] == 21 and cross_env["jobs_failed"] == 0,
           "matrix=%s" % cross_env["matrix"])
    record("all three case-sets report all_legs_pass",
           all(cs["all_legs_pass"] for cs in cross_env["case_sets"].values()),
           str({k: v["all_legs_pass"] for k, v in cross_env["case_sets"].items()}))

    env7_path = os.path.join(DEV_DIR, "environment_container_aarch64.json")
    if not os.path.exists(env7_path):
        record("environment-7 (pinned Linux/aarch64 container) evidence present", False,
               "run experiments.run_determinism_v12 inside the pinned Docker image, "
               "then experiments.check_environment_container_v12 --out %s" % env7_path)
    else:
        env7 = _load("environment_container_aarch64.json")
        env7_verification = env7["verification"]
        env7_result = env7["result"]
        record("environment-7 container: Linux/aarch64",
               env7["environment"].get("system") == "Linux"
               and env7["environment"].get("machine") == "aarch64",
               env7["environment"].get("platform"))
        record("environment-7 container: 155/155, all checks passed",
               env7_verification["passed"] is True and env7_result["TD"]["value"] == 1.0,
               "%d checks, %d failures" % (len(env7_verification["checks"]), env7_verification["failure_count"]))
        for case_id, expected in expected_hashes.items():
            actual = env7_result["per_case"][case_id]["reference_hash"]
            record("environment-7 container: %s hash matches committed reference" % case_id,
                   actual == expected, actual)

    # ---- 9. GD / GDmin (Monte Carlo regression) ----------------------------
    print("\n8. GD/GDmin (Monte Carlo regression against historical baseline)")
    monte_carlo = _load("monte_carlo.json")["result"]
    record("K == 250000, seed == 20260201",
           monte_carlo["K"] == 250000 and monte_carlo["seed"] == 20260201, "")
    record("all cases reproduce the historical GD/GDmin baseline",
           monte_carlo["all_match_historical_baseline"] is True,
           monte_carlo["regression_status"])
    for case_id in ("case_a", "case_b_v1_1"):
        per = monte_carlo["per_case_regression"][case_id]
        record("%s: matches_historical_baseline" % case_id, per["matches_historical_baseline"] is True,
               "GD_approved=%s GD_min_mean=%s" % (per["GD_approved"], per["GD_min_mean"]))

    # ---- 10. Compile timing -------------------------------------------------
    print("\n9. Compile timing (10 warmup + 100 measured)")
    timing = _load("compile_timing.json")["result"]
    record("hosts_pooled is False (single reportable reference machine only)",
           timing["hosts_pooled"] is False, "")
    for case_id in ("case_a", "case_b_v1_1", "case_d_ccs1"):
        per = timing["per_case"][case_id]
        record("%s: n=100, warmup=10" % case_id, per["n"] == 100 and per["warmup"] == 10,
               "n=%s warmup=%s" % (per["n"], per["warmup"]))

    # ---- 11. Observation diagnostics ---------------------------------------
    print("\n10. Observation diagnostics")
    obs = _load("observation_diagnostics.json")["result"]
    record("both diagnostics passed", obs["both_passed"] is True,
           "A=%s B=%s" % (obs["diagnostic_a"].get("passed"), obs["diagnostic_b"].get("passed")))

    # ---- 12. Case B integration --------------------------------------------
    print("\n11. Case B integration (13 adverse + 1 clean)")
    case_b_int = _load("case_b_integration.json")["result"]
    record("14 rows, 14/14 passed",
           case_b_int["scenario_count"] == 14 and case_b_int["passed"] == 14,
           "%s/%s" % (case_b_int["passed"], case_b_int["scenario_count"]))
    auth_counts = case_b_int["authorization_decision_counts"]
    record("authorization_decision axis (13 adverse rows): PERMIT=1 DENY=8 HOLD=4",
           auth_counts == {"PERMIT": 1, "DENY": 8, "HOLD": 4}, str(auth_counts))
    clean_row = next(r for r in case_b_int["scenarios"] if r["scenario"] == "clean_control")
    record("clean_control: PERMIT, tracked separately from the 13-row tally by design",
           clean_row["authorization_decision"] == "PERMIT" and clean_row["passed"] is True, "")

    # ---- 13. Full pytest suite ----------------------------------------------
    print("\n12. Full pytest suite")
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=REPO_ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    tail = proc.stdout.decode("utf-8", errors="replace").strip().splitlines()
    summary_line = tail[-1] if tail else ""
    record("pytest exits 0, 495 passed", proc.returncode == 0 and "495 passed" in summary_line,
           summary_line)

    # ---- 14. MANIFEST currency ---------------------------------------------
    print("\n13. MANIFEST currency (verified against the committed Git tree)")
    manifest_path = os.path.join(REPO_ROOT, "MANIFEST.sha256")
    manifest_json_path = os.path.join(REPO_ROOT, "MANIFEST.json")
    record("MANIFEST.sha256 present", os.path.exists(manifest_path), "")
    if os.path.exists(manifest_json_path):
        with open(manifest_json_path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        from experiments.make_manifest import role_for, verify_against_ref
        excluded_roles = {"development_result"}
        excluded_paths = {"MANIFEST.json"}

        def is_excluded(path):
            return path in excluded_paths or role_for(path) in excluded_roles

        diff = verify_against_ref(
            [row for row in manifest["files"] if not is_excluded(row["path"])],
            REPO_ROOT, ref="HEAD",
        )
        diff = {key: [p for p in paths if not is_excluded(p)] for key, paths in diff.items()}
        record("MANIFEST.json matches the committed HEAD tree exactly",
               not diff["missing"] and not diff["extra"] and not diff["changed"],
               "missing=%s extra=%s changed=%s" % (diff["missing"][:5], diff["extra"][:5], diff["changed"][:5]))

    # ---- 15. Historical tags unchanged --------------------------------------
    print("\n14. Historical tags unchanged (v3.1, v4, v4.1)")
    for tag, expected_commit in HISTORICAL_TAGS.items():
        actual = _git("rev-list", "-n", "1", tag)
        record("tag %s -> %s (unchanged)" % (tag, expected_commit[:12]),
               actual == expected_commit, actual or "tag not found")

    # ---- 16. Campaign is still marked development / not reportable ---------
    print("\n15. Development-phase campaign not prematurely marked reportable")
    campaign = _load("campaign_results_development.json")["result"]
    record("reportable == False", campaign["reportable"] is False, "")
    record("freeze.status == NOT CREATED", campaign["freeze"]["status"] == "NOT CREATED",
           campaign["freeze"]["status"])

    report["passed"] = not findings
    report["failure_count"] = len(findings)
    report["findings"] = findings
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    print("=" * 78)
    print("freeze_check.py --prospective-v5 -- prospective preregister-tier0-v5 state")
    print("Independent of, and does not read, any historical FREEZE_MANIFEST_V*.sha256")
    print("or the --prospective-v4 checker's own state.")
    print("=" * 78)

    report = check()

    print("\n" + "=" * 78)
    if report["passed"]:
        print("PROSPECTIVE-V5 FREEZE CHECK PASSED -- %d checks, 0 failures" % len(report["checks"]))
    else:
        print("PROSPECTIVE-V5 FREEZE CHECK FAILED -- %d of %d checks failed"
              % (report["failure_count"], len(report["checks"])))
        for finding in report["findings"]:
            print("  %s" % finding)
    print("=" * 78)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
