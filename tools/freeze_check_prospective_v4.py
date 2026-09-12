"""freeze_check.py --prospective-v4 -- verify the CURRENT v1.1 development
state against everything a `preregister-tier0-v4` freeze would need, without
touching or depending on any historical freeze-check path.

    python tools/freeze_check_prospective_v4.py
    python tools/freeze_check_prospective_v4.py --json

This is a NEW, independent verifier (runbook item 1). It does not call, wrap,
or depend on tools/freeze_check.py's --final-v2/--final-v3 historical paths,
and it does not read any of the old preregistration/FREEZE_MANIFEST_V*.sha256
files (see the "historical drift" section below for why those are
independently, pre-existingly broken -- and why that breakage cannot leak
into this checker, because this checker never reads them).

What it verifies:
  1.  Case A compiles; hash byte-identical to the frozen v3.1 reference.
  2.  Case A generator-reproducibility (regenerating from tools/build_cases.py
      reproduces the committed fixture exactly).
  3.  Case B v1.1 compiles; 9 ACS, 9 risk-derived + 3 invariant predicates.
  4.  Case B v1.1 full governance provenance chain (every ACS).
  5.  Case C compiles; schema v1.1; C* reversibility qualifier genuinely
      active (not the historical materiality-only workaround).
  6.  Canonical Q1-Q10, 10/10, for Case A, Case B (historical), Case B v1.1,
      Case C.
  7.  All 19 negative fixtures individually detected by their targeted query.
  8.  Auxiliary checks A1-A4 (Case B v1.1's real applicability).
  9.  All 13 Case B v1.1 injection scenarios assert the exact category
      outcome (not just non-externalization), with the authorization/release
      axes kept independent and safe_state uncorrupted.
  10. Determinism: recorded Case A / Case B v1.1 TD=1.000 (62/62), read from
      the dedicated results/development/determinism_summary_case_b_v11.json
      this generation's own harness writes (not the historical Case B run).
  11. Monte Carlo: recorded Case B v1.1 figures match K=250000, seed=20260201,
      and the historical FP_heat/MCSE values (reproduced, not assumed).
  12. Dependency lock (requirements.lock) and Dockerfile present.
  13. MANIFEST.sha256 / MANIFEST.json current (regenerable, non-empty,
      covers the new case_b_v1_1 / case_c trees).
  14. Historical tags unchanged (their tag->commit mapping matches the
      recorded values from prior sessions; never inspects, edits, or writes
      any historical FREEZE_MANIFEST_V*.sha256 or preregister-tier0-v3.1
      material).

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
CASE_B_HISTORICAL_HASH = "2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce"

#: Recorded at the time of this proposal (see docs/PROPOSED_FREEZE_V4_MANIFEST.md).
#: Never written to; only compared against, so a real historical tag move
#: would be caught, not silently accepted.
HISTORICAL_TAGS = {
    "preregister-tier0-v3.1": "158c0bd3785ac87a878671f76286be082a26d50d",
    "v1.0.5": None,  # resolved via git if present; not required to exist locally
}


def _git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:  # noqa: BLE001
        return None


def check():
    findings = []
    report = {"checks": [], "notes": []}

    def record(name, passed, detail=""):
        report["checks"].append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            findings.append("%s -- %s" % (name, detail))
        print("  [%s] %-64s %s" % ("PASS" if passed else "FAIL", name, detail))

    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle, sign_bundle
    from gcir import audit_queries, auxiliary_checks, negative_fixtures
    from gcir.provenance import ProvenanceError, verify_acs_provenance

    # ---- 1-2. Case A ------------------------------------------------------
    print("\n1. Case A isolation")
    case_a = load_case("case_a")
    result_a = compile_bundle(case_a.compiler_inputs())
    record("case_a payload hash byte-identical to frozen v3.1",
           result_a.bundle.payload_hash == CASE_A_FROZEN_HASH,
           result_a.bundle.payload_hash)
    record("case_a schema_version is 1.0 (uses no v1.1 field)",
           result_a.bundle.payload["schema_version"] == "1.0", "")

    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for sub in ("cases", "catalog", "invariants", "keys"):
            os.makedirs(os.path.join(tmp, sub), exist_ok=True)
        gen = subprocess.run(
            [sys.executable, "-m", "tools.build_cases", "--repo-root", tmp],
            cwd=REPO_ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )
        gen_ok = gen.returncode == 0
        record("tools.build_cases regenerates case_a without error", gen_ok,
               gen.stderr.decode("utf-8")[-300:] if not gen_ok else "")
        if gen_ok:
            import filecmp
            committed = os.path.join(REPO_ROOT, "cases", "case_a",
                                      "inputs", "invariant_register.json")
            regenerated = os.path.join(tmp, "cases", "case_a",
                                        "inputs", "invariant_register.json")
            same = filecmp.cmp(committed, regenerated, shallow=False)
            record("case_a generator-reproducibility (invariant_register.json)",
                   same, "regenerated tree matches committed fixture byte-for-byte")

    # ---- 3-4. Case B v1.1 ---------------------------------------------------
    print("\n2. Case B v1.1")
    case_b = load_case("case_b")
    result_b_hist = compile_bundle(case_b.compiler_inputs())
    record("case_b (historical, 6 ACS) payload hash unchanged",
           result_b_hist.bundle.payload_hash == CASE_B_HISTORICAL_HASH,
           result_b_hist.bundle.payload_hash)

    case_b11 = load_case("case_b_v1_1")
    result_b11 = compile_bundle(case_b11.compiler_inputs())
    stats = result_b11.statistics
    record("case_b_v1_1 acs_count == 9", stats["acs_count"] == 9, str(stats["acs_count"]))
    record("case_b_v1_1 risk_derived_predicate_count == 9",
           stats["risk_derived_predicate_count"] == 9, str(stats["risk_derived_predicate_count"]))
    record("case_b_v1_1 compiler_invariant_predicate_count == 3",
           stats["compiler_invariant_predicate_count"] == 3, str(stats["compiler_invariant_predicate_count"]))
    record("case_b_v1_1 total predicate_count == 12",
           stats["predicate_count"] == 12, str(stats["predicate_count"]))
    record("case_b_v1_1 disposition count == 6 (unchanged risk cardinality)",
           len(result_b11.bundle.dispositions) == 6, str(len(result_b11.bundle.dispositions)))

    try:
        prov_records = verify_acs_provenance(case_b11.documents, result_b11.bundle)
        record("case_b_v1_1 full ACS provenance chain (all 9 ACS)",
               all(r["complete"] for r in prov_records),
               "%d/9 complete" % sum(1 for r in prov_records if r["complete"]))
    except ProvenanceError as exc:
        record("case_b_v1_1 full ACS provenance chain (all 9 ACS)", False, str(exc)[:300])

    # ---- 5. Case C -----------------------------------------------------
    print("\n3. Case C")
    case_c = load_case("case_c")
    result_c = compile_bundle(case_c.compiler_inputs())
    record("case_c compiles (schema v1.1)",
           result_c.bundle.payload["schema_version"] == "1.1", result_c.bundle.payload_hash)
    rule = case_c.compiler_inputs().cstar_profile.document["classification_rules"]["physical_harm_to_person"]
    record("case_c C* reversibility qualifier genuinely active (not materiality-only)",
           rule.get("required_reversibility") == ["irreversible", "requires_intervention"],
           str(rule.get("required_reversibility")))
    cstar_ids = {row["risk_id"] for row in result_c.bundle.payload["coverage_matrix"]["c_star_coverage"]}
    record("case_c C-08/C-10 (reversible) excluded from C* by the real qualifier",
           "C-08" not in cstar_ids and "C-10" not in cstar_ids, str(sorted(cstar_ids)))

    # ---- 6. Canonical Q1-Q10 --------------------------------------------
    print("\n4. Canonical Q1-Q10 (real, not adapter-only)")
    for case, case_id, result in ((case_a, "case_a", result_a), (case_b, "case_b", result_b_hist),
                                   (case_b11, "case_b_v1_1", result_b11), (case_c, "case_c", result_c)):
        bundle = result.bundle
        sign_bundle(bundle, case.keyring, case.parameters["bundle_signing_key"],
                    signing_time="2026-09-13T00:00:00Z")
        catalog_doc = case.compiler_inputs().catalog.canonical_document()
        results = audit_queries.run_all_audit_queries(bundle, catalog_document=catalog_doc)
        passing = sum(1 for passed, _ in results.values() if passed)
        record("%s: Q1-Q10 %d/10" % (case_id, passing), passing == 10,
               "" if passing == 10 else str({q: d for q, (p, d) in results.items() if not p}))

    # ---- 7. Negative fixtures --------------------------------------------
    print("\n5. Negative fixtures (19 across all 10 queries)")
    fixtures = negative_fixtures.get_negative_fixtures(result_a.bundle)
    catalog_doc = case_a.compiler_inputs().catalog.canonical_document()
    detected = 0
    for name, bad_bundle in fixtures.items():
        target = negative_fixtures.FIXTURE_TARGET_QUERY[name]
        results = audit_queries.run_all_audit_queries(bad_bundle, catalog_document=catalog_doc)
        passed, _ = results[target]
        if not passed:
            detected += 1
    record("negative fixtures detected by their targeted query", detected == len(fixtures),
           "%d/%d" % (detected, len(fixtures)))
    record("negative fixture count == 19", len(fixtures) == 19, str(len(fixtures)))
    record("negative fixtures cover all 10 queries",
           set(negative_fixtures.FIXTURE_TARGET_QUERY.values()) == {"Q%d" % i for i in range(1, 11)}, "")

    # ---- 8. Auxiliary A1-A4 -----------------------------------------------
    print("\n6. Auxiliary checks A1-A4")
    release_tuple = {"subject": "transaction_agent", "action": "release_payment",
                      "resource": "payment_instruction", "destination": "payment_rail"}
    a1_passed, _ = auxiliary_checks.a1_actor_scope_revocation_validity(
        [{"actor_id": "x", "action_tuple": release_tuple, "authorization_time": "2026-03-10T14:00:00Z"}],
        [{"actor_id": "x", "scope": [release_tuple], "effective_time": "2026-03-10T13:00:00Z", "authority": "a"}],
    )
    record("A1 (applicable to Case B v1.1) detects a revoked actuation", a1_passed is False, "")
    not_applicable = auxiliary_checks.run_all_auxiliary_checks({})
    record("A2/A3/A4 report NOT_APPLICABLE (never silent PASS) when evidence is absent",
           all(not_applicable[k][0] and "NOT_APPLICABLE" in not_applicable[k][1][0] for k in ("A2", "A3", "A4")), "")

    # ---- 9. 13 Case B v1.1 injections -------------------------------------
    print("\n7. Case B v1.1: 13 injection scenarios")
    from experiments.case_b_v11_injection_scenarios import run as run_injections
    injection_report = run_injections(result_b11.bundle)
    injection_rows = [r for r in injection_report["scenarios"] if r["scenario"] != "clean_control"]
    record("13/13 injection scenarios assert exact category outcome",
           injection_report["failed"] == 0 and len(injection_rows) == 13,
           "%d/%d passed (%d injection rows + clean_control)"
           % (injection_report["passed"], injection_report["scenario_count"], len(injection_rows)))
    auth_counts = injection_report["authorization_decision_counts"]
    rel_counts = injection_report["release_decision_counts"]
    record("authorization_decision axis: PERMIT=1 DENY=8 HOLD=4",
           auth_counts == {"PERMIT": 1, "DENY": 8, "HOLD": 4}, str(auth_counts))
    record("release_decision axis: ALLOW_RELEASE=12 BLOCK_RELEASE=1",
           rel_counts == {"ALLOW_RELEASE": 12, "BLOCK_RELEASE": 1}, str(rel_counts))
    toctou = next(r for r in injection_report["scenarios"] if r["scenario"] == "toctou")
    record("toctou: safe_state stays False despite BLOCK_RELEASE (item 3)",
           toctou["safe_state"] is False and toctou["authorization_decision"] == "PERMIT", "")

    # ---- 10. Determinism (Case B v1.1's own harness) ----------------------
    print("\n8. Determinism (Case A + Case B v1.1, this generation's own harness)")
    det_path = os.path.join(REPO_ROOT, "results", "development", "determinism_summary_case_b_v11.json")
    if not os.path.exists(det_path):
        record("determinism_summary_case_b_v11.json present", False,
               "run `python -m experiments.run_determinism_case_b_v11` first")
    else:
        with open(det_path, encoding="utf-8") as fh:
            det = json.load(fh)["result"]
        record("TD == 1.000 over 62 runs (Case A + Case B v1.1, NOT reused from historical Case B)",
               det["TD"]["value"] == 1.0 and det["total_runs"] == 62,
               "TD=%s total_runs=%s" % (det["TD"]["value"], det["total_runs"]))
        record("case_a reference hash matches frozen v3.1",
               det["per_case"]["case_a"]["reference_hash"] == CASE_A_FROZEN_HASH, "")
        record("case_b_v1_1 reference hash matches this session's compiled hash",
               det["per_case"]["case_b_v1_1"]["reference_hash"] == result_b11.bundle.payload_hash, "")

    # ---- 11. Monte Carlo (Case A + Case B v1.1, this generation's own harness) --
    print("\n9. Monte Carlo (Case A + Case B v1.1, reproduced not assumed)")
    mc_path = os.path.join(REPO_ROOT, "results", "development", "monte_carlo_summary_case_b_v11.json")
    if not os.path.exists(mc_path):
        record("monte_carlo_summary_case_b_v11.json present", False,
               "run `python -m experiments.run_monte_carlo_case_b_v11` first")
    else:
        with open(mc_path, encoding="utf-8") as fh:
            mc = json.load(fh)["result"]
        record("K == 250000, seed == 20260201",
               mc["specification"]["draws_K"] == 250000 and mc["specification"]["seed"] == 20260201, "")

        case_a_mc = mc["per_case"]["case_a"]
        record("Case A max FP_heat unchanged (0.321268, R-06) -- Case A must not move",
               case_a_mc["max_FP_heat"]["risk_id"] == "R-06"
               and abs(case_a_mc["max_FP_heat"]["value"] - 0.321268) < 1e-6,
               str(case_a_mc["max_FP_heat"]))
        record("Case A GD_approved == 3 (heat-map comparator, unchanged)",
               case_a_mc["GD_approved"] == 3, str(case_a_mc["GD_approved"]))

        analysis = mc["per_case"]["case_b_v1_1"]
        record("max FP_heat reproduces historical Case B (0.317980, B-01)",
               analysis["max_FP_heat"]["risk_id"] == "B-01"
               and abs(analysis["max_FP_heat"]["value"] - 0.317980) < 1e-6,
               str(analysis["max_FP_heat"]))
        record("MCSE reproduces historical Case B (0.000931)",
               abs(analysis["max_FP_heat"]["mcse"] - 0.000931) < 1e-6, "")
        record("FP_C* == 0 (structural, re-verified not assumed)",
               analysis["max_FP_cstar"] == 0.0, "")
        record("GD_approved == 4, GD_min_mean == 0.0 (heat-map comparator, unchanged "
               "from historical Case B -- ACS restructuring proven not to affect "
               "rating-sampling machinery)",
               analysis["GD_approved"] == 4 and analysis["GD_min_mean"] == 0.0,
               "GD_approved=%s GD_min_mean=%s" % (analysis["GD_approved"], analysis["GD_min_mean"]))

    # ---- 12. dependency lock / Dockerfile ----------------------------------
    print("\n10. Dependency lock and Dockerfile")
    record("requirements.lock present", os.path.exists(os.path.join(REPO_ROOT, "requirements.lock")), "")
    record("Dockerfile present", os.path.exists(os.path.join(REPO_ROOT, "Dockerfile")), "")

    # ---- 13. MANIFEST -------------------------------------------------------
    # Self-consistency against the CURRENT working tree, not a diff against
    # the last commit -- this is a prospective, not-yet-committed freeze, so
    # "current" means "matches disk right now," not "matches HEAD."
    print("\n11. MANIFEST currency (verified against the committed Git tree, not a filesystem walk)")
    manifest_path = os.path.join(REPO_ROOT, "MANIFEST.sha256")
    manifest_json_path = os.path.join(REPO_ROOT, "MANIFEST.json")
    record("MANIFEST.sha256 present", os.path.exists(manifest_path), "")
    if os.path.exists(manifest_json_path):
        with open(manifest_json_path, encoding="utf-8") as fh:
            manifest = json.load(fh)
        record("MANIFEST covers case_b_v1_1 (case_b_input role)",
               any("case_b_v1_1" in f["path"] for f in manifest["files"]), "")
        record("MANIFEST covers case_c (case_c_input role)",
               any(f["role"] == "case_c_input" for f in manifest["files"]), "")

        # Verified against Git's own committed tree (git ls-tree + git
        # cat-file), NOT a second filesystem walk -- comparing two
        # filesystem walks against each other is exactly what let the
        # preregister-tier0-v4 MANIFEST defect through undetected (both
        # walks were wrong the same way, on the same locally-dirty disk).
        # See docs/V4_MANIFEST_DEFECT_REPORT.json.
        #
        # Excludes the same two self-mutating categories `make
        # verify-manifest` already excludes: development_result files carry
        # a run_completed_utc timestamp that changes on every re-run
        # regardless of scientific content, and MANIFEST.json is
        # self-referential (it lists its own manifest_sha256, which
        # necessarily moves each time the manifest itself is rewritten).
        from experiments.make_manifest import verify_against_ref
        excluded_roles = {"development_result"}
        excluded_paths = {"MANIFEST.json"}
        diff = verify_against_ref(
            [row for row in manifest["files"]
             if row["role"] not in excluded_roles and row["path"] not in excluded_paths],
            REPO_ROOT, ref="HEAD",
        )
        # A path that legitimately belongs to an excluded role/path is not a
        # real "missing" finding just because it was filtered out above.
        diff["missing"] = [p for p in diff["missing"]
                            if p not in excluded_paths]
        record("MANIFEST.json matches the committed HEAD tree exactly "
               "(git ls-tree + git cat-file, excluding development_result/MANIFEST.json)",
               not diff["missing"] and not diff["extra"] and not diff["changed"],
               "missing=%s extra=%s changed=%s" % (diff["missing"][:5], diff["extra"][:5], diff["changed"][:5]))
        report["manifest_file_count"] = manifest["file_count"]
        report["manifest_root_hash"] = manifest["manifest_sha256"]
        report["manifest_roles"] = manifest["roles"]

    # ---- 14. Historical tags unchanged ------------------------------------
    print("\n12. Historical tags unchanged (never inspected for editing, only compared)")
    for tag, expected_commit in HISTORICAL_TAGS.items():
        actual = _git("rev-list", "-n", "1", tag)
        if expected_commit is None:
            record("tag %s exists" % tag, actual is not None, actual or "not found locally")
        else:
            record("tag %s -> %s (unchanged)" % (tag, expected_commit[:12]),
                   actual == expected_commit, actual or "tag not found")

    report["passed"] = not findings
    report["failure_count"] = len(findings)
    report["findings"] = findings
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    print("=" * 78)
    print("freeze_check.py --prospective-v4 -- prospective preregister-tier0-v4 state")
    print("Independent of, and does not read, any historical FREEZE_MANIFEST_V*.sha256.")
    print("=" * 78)

    report = check()

    print("\n" + "=" * 78)
    if report["passed"]:
        print("PROSPECTIVE-V4 FREEZE CHECK PASSED -- %d checks, 0 failures" % len(report["checks"]))
    else:
        print("PROSPECTIVE-V4 FREEZE CHECK FAILED -- %d of %d checks failed"
              % (report["failure_count"], len(report["checks"])))
        for finding in report["findings"]:
            print("  %s" % finding)
    print("=" * 78)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
