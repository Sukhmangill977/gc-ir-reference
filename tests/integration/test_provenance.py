"""Full governance-to-predicate provenance chain (risk -> obligation(s) ->
signed judgment selection/approval -> disposition -> ACS -> compiled
predicate), verified for every ACS in every case -- not asserted in prose
alone. See src/gcir/provenance.py for exactly what is and is not checked.

Runbook item 2: the three new Case B v1.1 ACS records (ACS-B01-02,
ACS-B01-03, ACS-B02-02) must have this chain exactly like every historical
ACS -- there is no separate, weaker acceptance path for them.
"""

from __future__ import annotations

import copy

import pytest

from gcir.provenance import ProvenanceError, verify_acs_provenance


def test_case_a_every_acs_has_complete_provenance(case_a):
    case, _, result = case_a
    records = verify_acs_provenance(case.documents, result.bundle)
    assert records, "no ACS records found"
    for r in records:
        assert r["complete"], r


def test_case_b_historical_every_acs_has_complete_provenance(case_b):
    case, _, result = case_b
    records = verify_acs_provenance(case.documents, result.bundle)
    assert len(records) == 6
    for r in records:
        assert r["complete"], r


def test_case_b_v1_1_every_acs_has_complete_provenance(case_b_v1_1):
    case, _, result = case_b_v1_1
    records = verify_acs_provenance(case.documents, result.bundle)
    assert len(records) == 9
    for r in records:
        assert r["complete"], r


def test_case_c_every_acs_has_complete_provenance(case_c):
    case, _, result = case_c
    records = verify_acs_provenance(case.documents, result.bundle)
    assert len(records) == 13
    for r in records:
        assert r["complete"], r


#: The three ACS runbook item 2 specifically requires provenance for.
NEW_V11_ACS_IDS = ("ACS-B01-02", "ACS-B01-03", "ACS-B02-02")


def test_the_three_new_v1_1_acs_have_full_provenance_not_just_prose(case_b_v1_1):
    """The exact per-field table runbook item 2 asks for, for each of the
    three new ACS: risk_id, obligation_refs, judgment selection/approval
    (selector, approver, approval_time), disposition linkage, and the
    resulting compiled predicate id."""
    case, _, result = case_b_v1_1
    records = {r["acs_id"]: r for r in verify_acs_provenance(case.documents, result.bundle)}

    expected_risk = {"ACS-B01-02": "B-01", "ACS-B01-03": "B-01", "ACS-B02-02": "B-02"}
    for acs_id in NEW_V11_ACS_IDS:
        record = records[acs_id]
        assert record["complete"] is True
        assert record["risk_id"] == expected_risk[acs_id]
        assert record["obligation_refs"], "%s must cite at least one obligation" % acs_id
        assert record["selected_by"], "%s missing a named judgment selector" % acs_id
        assert record["approver"], "%s missing a named judgment approver" % acs_id
        assert record["approval_time"], "%s missing an approval_time" % acs_id
        assert record["approval_forum"], "%s missing an approving forum" % acs_id
        assert record["gcir_id"].startswith("GCIR-B0"), "%s has no compiled predicate id" % acs_id


def test_the_three_new_acs_have_distinct_semantic_purpose_and_own_gcir_id(case_b_v1_1):
    """No two of the three new ACS collapse onto the same compiled predicate
    -- each is its own genuinely distinct control, not a relabeling."""
    case, _, result = case_b_v1_1
    records = {r["acs_id"]: r for r in verify_acs_provenance(case.documents, result.bundle)}
    gcir_ids = {records[acs_id]["gcir_id"] for acs_id in NEW_V11_ACS_IDS}
    assert len(gcir_ids) == 3, "each new ACS must compile to its own distinct predicate"

    # Evaluation basis differs across the three -- direct evidence they are
    # not merely the same check copy-pasted under new ids.
    bases = {
        p["evaluation_basis"] for p in result.bundle.predicates
        if p.get("acs_id") in NEW_V11_ACS_IDS
    }
    assert bases == {"deterministic_lookup", "human_attestation"}, (
        "ACS-B01-02 must be deterministic_lookup; ACS-B01-03/ACS-B02-02 must be human_attestation"
    )


# ---------------------------------------------------------------------------
# Negative regression: an ACS WITHOUT provenance must be caught, not silently
# accepted (runbook item 2: "Add tests that fail if an ACS exists without
# this provenance").
# ---------------------------------------------------------------------------


def test_an_acs_with_no_judgment_selection_is_rejected(case_b_v1_1):
    case, _, result = case_b_v1_1
    documents = copy.deepcopy(case.documents)
    documents["judgment_record"]["selections"] = [
        s for s in documents["judgment_record"]["selections"] if s["acs_id"] != "ACS-B01-02"
    ]
    with pytest.raises(ProvenanceError, match="ACS-B01-02"):
        verify_acs_provenance(documents, result.bundle)


def test_an_acs_with_no_judgment_approval_is_rejected(case_b_v1_1):
    case, _, result = case_b_v1_1
    documents = copy.deepcopy(case.documents)
    documents["judgment_record"]["approvals"] = [
        a for a in documents["judgment_record"]["approvals"] if a["acs_id"] != "ACS-B01-03"
    ]
    with pytest.raises(ProvenanceError, match="ACS-B01-03"):
        verify_acs_provenance(documents, result.bundle)


def test_an_acs_not_named_in_its_risks_disposition_is_rejected(case_b_v1_1):
    case, _, result = case_b_v1_1
    documents = copy.deepcopy(case.documents)
    for d in documents["dispositions"]["records"]:
        if d["risk_id"] == "B-02":
            d["acs_ids"] = [a for a in d["acs_ids"] if a != "ACS-B02-02"]
    with pytest.raises(ProvenanceError, match="ACS-B02-02"):
        verify_acs_provenance(documents, result.bundle)


def test_an_acs_citing_a_nonexistent_obligation_is_rejected(case_b_v1_1):
    case, _, result = case_b_v1_1
    documents = copy.deepcopy(case.documents)
    for acs in documents["approved_control_specifications"]["records"]:
        if acs["acs_id"] == "ACS-B01-02":
            acs["obligation_refs"] = ["OBLIGATION-DOES-NOT-EXIST"]
    with pytest.raises(ProvenanceError, match="ACS-B01-02"):
        verify_acs_provenance(documents, result.bundle)


def test_an_acs_citing_a_nonexistent_risk_is_rejected(case_b_v1_1):
    case, _, result = case_b_v1_1
    documents = copy.deepcopy(case.documents)
    for acs in documents["approved_control_specifications"]["records"]:
        if acs["acs_id"] == "ACS-B02-02":
            acs["risk_id"] = "B-DOES-NOT-EXIST"
    with pytest.raises(ProvenanceError, match="ACS-B02-02"):
        verify_acs_provenance(documents, result.bundle)
