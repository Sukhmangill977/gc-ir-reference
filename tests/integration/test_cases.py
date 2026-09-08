"""Integration tests: the two case artifacts as the manuscript describes them.

These assert the *structural* facts the manuscript states about each case
(row counts, disposition counts, gate sources, C* membership).  They deliberately
do NOT assert any measured numeric result -- DC, GD, TD and the Monte Carlo
values are measured by the experiments and reported from the result files, never
pinned in a test.  A test that pinned a measurement would make the measurement
unfalsifiable.
"""

import json
import os

import pytest


# ---------------------------------------------------------------------------
# Case A -- Section IX
# ---------------------------------------------------------------------------


def test_case_a_has_sixteen_register_rows(case_a):
    """'Rows R-01-R-14 correspond one-to-one to the fourteen-row source register;
    R-15 and R-16 are register extensions.'"""
    _, inputs, _ = case_a
    ids = sorted(r["risk_id"] for r in inputs.assessment.risk_register)
    assert ids == ["R-%02d" % i for i in range(1, 17)]


def test_case_a_disposition_counts(case_a):
    """'Dispositions: 13 runtime, 3 non-runtime, 0 accepted, 0 unresolved.'"""
    _, _, result = case_a
    counts = {}
    for record in result.bundle.dispositions:
        counts[record["record_type"]] = counts.get(record["record_type"], 0) + 1
    assert counts.get("RuntimeDisposition") == 13
    assert counts.get("NonRuntimeDisposition") == 3
    assert counts.get("AcceptedRiskDisposition", 0) == 0
    assert counts.get("UnresolvedDisposition", 0) == 0


def test_case_a_is_declared_synthetic(case_a, repo_root):
    """Section XII: 'Case A is synthetic (fully specified and reproducible, but
    not a deployed system).'"""
    with open(os.path.join(repo_root, "cases", "case_a", "inputs", "assessment.json"),
              encoding="utf-8") as handle:
        assessment = json.load(handle)
    assert assessment["case_class"] == "synthetic"


def test_case_a_non_runtime_reason_codes(case_a):
    """R-14 RC-01, R-15 RC-03, R-16 RC-01 (Section IX)."""
    _, _, result = case_a
    codes = {
        record["risk_id"]: record["reason_code"]
        for record in result.bundle.dispositions
        if record["record_type"] == "NonRuntimeDisposition"
    }
    assert codes == {"R-14": "RC-01", "R-15": "RC-03", "R-16": "RC-01"}


def test_case_a_c_star_membership(case_a):
    """The Section IX table marks R-05, R-06, R-08, R-09, R-10 and R-13 as C*."""
    from gcir.coverage import classify_risks

    _, inputs, _ = case_a
    flags = classify_risks(inputs.assessment, inputs.cstar_profile)
    assert sorted(rid for rid, flag in flags.items() if flag == 1) == [
        "R-05", "R-06", "R-08", "R-09", "R-10", "R-13"
    ]


def test_case_a_gate_sources_match_the_manuscript_table(case_a):
    """C*-selected gates stay distinguishable from mandatory gates created for
    other approved reasons (Section VII-A)."""
    _, _, result = case_a
    by_risk = {}
    for predicate in result.bundle.predicates:
        if predicate["origin"]["origin_type"] != "risk_derived":
            continue
        by_risk.setdefault(predicate["origin"]["origin_id"], set()).add(
            (predicate["gate_type"], predicate["gate_source"])
        )

    for risk_id in ("R-05", "R-06", "R-08", "R-09", "R-10", "R-13"):
        assert ("mandatory", "C_STAR") in by_risk[risk_id], risk_id
    for risk_id in ("R-01", "R-02", "R-03", "R-07", "R-11"):
        assert by_risk[risk_id] == {("mandatory", "OTHER_MANDATORY")}, risk_id
    # R-04 is weighted + advisory; R-12 is advisory. Neither is a gate.
    assert all(gate != "mandatory" for gate, _ in by_risk["R-04"])
    assert all(gate != "mandatory" for gate, _ in by_risk["R-12"])


def test_case_a_r04_yields_a_weighted_and_an_advisory_predicate(case_a):
    """Section IX: R-04 is 'runtime * weighted + advisory'."""
    _, _, result = case_a
    gates = sorted(
        p["gate_type"] for p in result.bundle.predicates
        if p["origin"]["origin_id"] == "R-04"
    )
    assert gates == ["advisory", "weighted"]


def test_case_a_predicate_multiplicity(case_a):
    """'One risk may produce zero, one, or several predicates.'"""
    _, _, result = case_a
    per_risk = {}
    for predicate in result.bundle.predicates:
        if predicate["origin"]["origin_type"] == "risk_derived":
            per_risk.setdefault(predicate["origin"]["origin_id"], []).append(predicate)

    assert len(per_risk["R-04"]) == 2
    assert len(per_risk["R-07"]) == 2
    assert len(per_risk["R-09"]) == 2
    assert len(per_risk["R-01"]) == 1
    for risk_id in ("R-14", "R-15", "R-16"):
        assert risk_id not in per_risk  # zero predicates, still dispositioned


def test_case_a_mandatory_role_is_recorded_and_distinguishable(case_a):
    _, _, result = case_a
    roles = {p["gcir_id"]: p["mandatory_role"] for p in result.bundle.predicates}
    assert "decisive" in roles.values()
    assert "supporting" in roles.values()
    for predicate in result.bundle.predicates:
        if predicate["gate_type"] == "mandatory":
            assert predicate["mandatory_role"] == "decisive"


def test_case_a_r09_predicates_are_structural_not_semantic(case_a):
    """Section IX R-09 note: 'the predicate never judges whether prose "sounds
    like" advice ... Its catalog template tests structure.'"""
    _, _, result = case_a
    r09 = [p for p in result.bundle.predicates if p["origin"]["origin_id"] == "R-09"]
    assert r09
    for predicate in r09:
        assert predicate["evaluation_basis"] == "structural_check"
        assert "human-factors" in predicate["warrant_boundary"] or \
               "does not establish" in predicate["warrant_boundary"]


def test_case_a_r08_warrant_boundary_disclaims_substantive_review(case_a):
    """Section III Step 2 / Section V: human_attestation tests the presence and
    validity of the signed artifact, not the quality of the judgment."""
    _, _, result = case_a
    r08 = next(p for p in result.bundle.predicates if p["origin"]["origin_id"] == "R-08")
    assert r08["evaluation_basis"] == "human_attestation"
    assert "substantive" in r08["warrant_boundary"]
    assert "R-12" in r08["warrant_boundary"]


# ---------------------------------------------------------------------------
# Case B -- Section X
# ---------------------------------------------------------------------------


def test_case_b_has_six_rows_all_runtime_all_mandatory(case_b):
    _, inputs, result = case_b
    ids = sorted(r["risk_id"] for r in inputs.assessment.risk_register)
    assert ids == ["B-0%d" % i for i in range(1, 7)]

    counts = {}
    for record in result.bundle.dispositions:
        counts[record["record_type"]] = counts.get(record["record_type"], 0) + 1
    assert counts == {"RuntimeDisposition": 6}

    risk_derived = [p for p in result.bundle.predicates
                    if p["origin"]["origin_type"] == "risk_derived"]
    assert len(risk_derived) == 6
    assert all(p["gate_type"] == "mandatory" for p in risk_derived)


def test_case_b_gate_sources_are_four_cstar_and_two_other(case_b):
    """Section X: 'four by C*, two by other approved mandatory policy'."""
    _, _, result = case_b
    sources = [p["gate_source"] for p in result.bundle.predicates
               if p["origin"]["origin_type"] == "risk_derived"]
    assert sources.count("C_STAR") == 4
    assert sources.count("OTHER_MANDATORY") == 2


def test_case_b_b04_is_gated_by_class_at_the_bottom_of_the_register(case_b):
    """Section X: 'at s = 5 -- the bottom of the register ... the gate's
    justification is its class, not its score' (L=1, I=5)."""
    _, inputs, result = case_b
    row = inputs.assessment.analysis_index["B-04"]
    assert row["likelihood_residual"] == 1
    assert row["impact_residual"] == 5

    scores = {rid: a["likelihood_residual"] * a["impact_residual"]
              for rid, a in inputs.assessment.analysis_index.items()}
    assert scores["B-04"] == 5
    assert scores["B-04"] == min(scores.values())

    predicate = next(p for p in result.bundle.predicates
                     if p["origin"]["origin_id"] == "B-04")
    assert predicate["gate_type"] == "mandatory"
    assert predicate["gate_source"] == "C_STAR"


def test_case_b_authority_matrix_admits_exactly_one_external_action(case_b):
    """Section X: 'the authority matrix admits exactly one external action
    (release_payment) with bound parameters'."""
    _, inputs, _ = case_b
    hazardous = [entry for entry in inputs.assessment.authority_matrix.values()
                 if entry.hazardous]
    assert len(hazardous) == 1
    assert hazardous[0].tuple_.action == "release_payment"
    assert set(hazardous[0].parameter_schema) == {"transaction_hash", "currency", "rail"}


def test_case_b_is_declared_a_forensic_reconstruction(case_b, repo_root):
    """Section X and Section XII state this openly; the artifact must not imply
    prospective production evidence."""
    with open(os.path.join(repo_root, "cases", "case_b", "inputs", "assessment.json"),
              encoding="utf-8") as handle:
        assessment = json.load(handle)
    assert assessment["case_class"] == "forensic_reconstruction"
    assert "reconstructed retrospectively" in assessment["metadata"]["method"]


# ---------------------------------------------------------------------------
# Both cases
# ---------------------------------------------------------------------------


def test_bundle_payload_hash_is_reproducible(any_case):
    from gcir.canonicalization import hash_payload

    _, _, result = any_case
    assert hash_payload(result.bundle.payload) == result.bundle.payload_hash
    assert len(result.bundle.payload_hash) == 64


def test_recompiling_gives_the_same_hash(any_case):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case, _, result = any_case
    again = compile_bundle(load_case(case.case_id).compiler_inputs())
    assert again.bundle.payload_hash == result.bundle.payload_hash


def test_catalog_and_cstar_profile_are_inside_the_bundle_hash(any_case):
    """Section IV-B: the catalog is 'included in the compiled-bundle hash'.

    The hash is over the catalog's *canonical projection* -- entries sorted by
    (event_type, template_id), signature envelope stripped -- so that an
    equivalent authoring order cannot change the bundle hash (Section VI-C).
    """
    from gcir.canonicalization import hash_payload

    case, inputs, result = any_case
    payload = result.bundle.payload
    assert payload["catalog_ref"]["content_hash"] == hash_payload(
        inputs.catalog.canonical_document())
    assert payload["cstar_profile_ref"]["content_hash"] == hash_payload(
        inputs.cstar_profile.canonical_document())
    assert payload["catalog_ref"]["version"] == inputs.catalog.version
    assert payload["catalog_ref"]["catalog_id"] == inputs.catalog.catalog_id


def test_bundle_inherits_the_assessment_version_binding(any_case):
    """Section III Step 1: 'Compilation output inherits this binding.'"""
    _, inputs, result = any_case
    assert (result.bundle.payload["version_binding"]["binding_id"]
            == inputs.assessment.version_binding["binding_id"])
    for predicate in result.bundle.predicates:
        assert predicate["version_binding_ref"] == inputs.assessment.version_binding["binding_id"]


def test_committed_case_tree_matches_the_generator(repo_root, tmp_path):
    """The committed JSON is the artifact of record; the generator must
    reproduce it byte-for-byte."""
    import filecmp
    import subprocess
    import sys

    target = tmp_path / "regen"
    (target / "cases").mkdir(parents=True)
    (target / "catalog").mkdir()
    (target / "invariants").mkdir()
    (target / "keys").mkdir()
    subprocess.run(
        [sys.executable, "-m", "tools.build_cases", "--repo-root", str(target)],
        cwd=repo_root, check=True, stdout=subprocess.DEVNULL,
    )
    for case_id in ("case_a", "case_b"):
        for relative in ("inputs/assessment.json",
                         "inputs/control_derivation_catalog.json",
                         "inputs/cstar_profile.json",
                         "inputs/invariant_register.json",
                         "judgment/judgment_record.json",
                         "dispositions/dispositions.json",
                         "acs/approved_control_specifications.json"):
            committed = os.path.join(repo_root, "cases", case_id, relative)
            regenerated = os.path.join(str(target), "cases", case_id, relative)
            assert filecmp.cmp(committed, regenerated, shallow=False), relative
