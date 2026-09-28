"""Case D: D1-D10 (Paper 2 v1.2 spec section 4).

Development-generation artifact; not part of any frozen preregister-tier0
campaign. See docs/CASE_B_V1_1_RATIONALE.md-style provenance note: this is a
new, prospectively designed case, not a reconstruction.
"""

from __future__ import annotations

import json
import os

from experiments import case_d_matrix

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_all_three_ccs_variants_are_marked_synthetic():
    for case_id in ("case_d_ccs0", "case_d_ccs1", "case_d_ccs2"):
        with open(os.path.join(REPO_ROOT, "cases", case_id, "inputs", "assessment.json")) as fh:
            assessment = json.load(fh)
        assert assessment["case_class"] == "synthetic"


def test_ccs0_ordinary_gate_present_and_decisive(case_d_ccs0):
    _, _, result = case_d_ccs0
    ordinary = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D01-01")
    assert ordinary["mandatory_role"] == "decisive"
    assert result.bundle.gate_map[ordinary["gcir_id"]]["gate_type"] == "mandatory"


def test_ccs0_d02_is_accepted_not_runtime(case_d_ccs0):
    _, _, result = case_d_ccs0
    d02 = next(d for d in result.bundle.dispositions if d["risk_id"] == "D-02")
    assert d02["record_type"] == "AcceptedRiskDisposition"
    assert "manual_governance_process" in d02["rationale"]


def test_ccs1_both_risks_runtime_and_exception_confined(case_d_ccs1):
    _, _, result = case_d_ccs1
    acs_ids = {p["acs_id"] for p in result.bundle.predicates}
    assert {"ACS-D01-01", "ACS-D02-01"}.issubset(acs_ids)

    ordinary = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D01-01")
    exception = next(p for p in result.bundle.predicates if p["acs_id"] == "ACS-D02-01")
    ordinary_attrs = {c["attribute"] for c in ordinary["context_conditions"]}
    exception_attrs = {c["attribute"] for c in exception["context_conditions"]}
    assert ordinary_attrs.isdisjoint(exception_attrs)
    assert exception["exception"]["authorized_actor"] == ["treasury.officer_on_duty"]


def test_ccs2_widens_actor_set_and_changes_the_hash(case_d_ccs1, case_d_ccs2):
    _, _, ccs1 = case_d_ccs1
    _, _, ccs2 = case_d_ccs2
    exception_ccs2 = next(p for p in ccs2.bundle.predicates if p["acs_id"] == "ACS-D02-01")
    assert "payments.analyst_eta2_tier" in exception_ccs2["exception"]["authorized_actor"]
    assert ccs1.bundle.payload_hash != ccs2.bundle.payload_hash


def test_d1_through_d10_all_pass():
    report = case_d_matrix.run_all()
    failures = [row for row in report["rows"] if not row["passed"]]
    assert not failures, "Case D rows failed: %s" % json.dumps(failures, indent=2, default=str)
    assert report["passed"] == report["total"] == 10
