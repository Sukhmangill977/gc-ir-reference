"""Case B v1.1: nine Approved Control Specifications (B-01: 3, B-02: 2,
B-03..B-06: 1 each), per manuscript Section X / Table II's literal
specification. See docs/CASE_B_V1_1_RATIONALE.md for full provenance.

Development-generation artifact; not part of the frozen preregister-tier0-v3.1
campaign. The historical cases/case_b/ (six ACS) is untouched.
"""

from __future__ import annotations

import json
import os

from gcir import audit_queries
from gcir.compiler import sign_bundle
from gcir.precedence_v11 import resolve_phase_aware

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_six_risks_six_dispositions_nine_acs(case_b_v1_1, case_b):
    """Disposition count (per-risk) is unchanged at 6; ACS count is 9 because
    B-01 and B-02 now each carry more than one signed specification, not
    because any risk was re-disposed."""
    _, _, result_v11 = case_b_v1_1
    _, _, result_v10 = case_b
    assert result_v11.statistics["risk_count"] == result_v10.statistics["risk_count"] == 6
    assert len(result_v11.bundle.dispositions) == len(result_v10.bundle.dispositions) == 6
    assert result_v11.statistics["acs_count"] == 9
    assert result_v10.statistics["acs_count"] == 6


def test_b01_disposition_names_three_acs_ids(case_b_v1_1):
    _, _, result = case_b_v1_1
    disp = next(d for d in result.bundle.dispositions if d["risk_id"] == "B-01")
    assert disp["record_type"] == "RuntimeDisposition"
    assert sorted(disp["acs_ids"]) == ["ACS-B01-01", "ACS-B01-02", "ACS-B01-03"]


def test_b02_disposition_names_two_acs_ids(case_b_v1_1):
    _, _, result = case_b_v1_1
    disp = next(d for d in result.bundle.dispositions if d["risk_id"] == "B-02")
    assert sorted(disp["acs_ids"]) == ["ACS-B02-01", "ACS-B02-02"]


def test_predicate_counts_are_nine_risk_derived_three_invariant(case_b_v1_1):
    """This compiler emits exactly one CompiledPredicate per ACS (Section
    VI-A); nine ACS therefore means nine risk-derived predicates, not six.
    The frozen v3.1 Case B's own '6 risk-derived' figure describes its own
    six-ACS fixture, not a constraint this nine-ACS design must reproduce."""
    _, _, result = case_b_v1_1
    stats = result.statistics
    assert stats["risk_derived_predicate_count"] == 9
    assert stats["compiler_invariant_predicate_count"] == 3
    assert stats["predicate_count"] == 12


def test_no_acs_disappears_during_compilation(case_b_v1_1):
    """Every one of the nine ACS ids must be cited by exactly one compiled
    risk-derived predicate."""
    _, _, result = case_b_v1_1
    bundle = result.bundle
    acs_ids_in_dispositions = set()
    for d in bundle.dispositions:
        if d["record_type"] == "RuntimeDisposition":
            acs_ids_in_dispositions.update(d["acs_ids"])
    acs_ids_in_predicates = {
        p["acs_id"] for p in bundle.predicates if p["origin"]["origin_type"] == "risk_derived"
    }
    assert acs_ids_in_dispositions == acs_ids_in_predicates
    assert len(acs_ids_in_predicates) == 9


def test_schema_version_is_1_1(case_b_v1_1):
    _, _, result = case_b_v1_1
    assert result.bundle.payload["schema_version"] == "1.1"


def test_hash_genuinely_differs_from_case_b_v10(case_b_v1_1, case_b):
    _, _, result_v11 = case_b_v1_1
    _, _, result_v10 = case_b
    assert result_v11.bundle.payload_hash != result_v10.bundle.payload_hash
    with open(os.path.join(REPO_ROOT, "cases", "case_b_v1_1", "expected", "reference_hashes.json")) as fh:
        reference = json.load(fh)
    assert result_v11.bundle.payload_hash == reference["payload_hash"]


def test_case_a_is_byte_identical_to_the_frozen_hash(case_a):
    """Case A isolation check (runbook item 8.D): if this ever fails, stop --
    something leaked across cases. Do not update this expected value without
    first finding the leak."""
    _, _, result = case_a
    assert result.bundle.payload_hash == "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536"
    assert result.bundle.payload["schema_version"] == "1.0"


def test_primary_metrics_match_expected(case_b_v1_1):
    from gcir import metrics

    case, inputs, result = case_b_v1_1
    invariant_ids = [i["invariant_id"] for i in inputs.invariants]
    m = metrics.compute_all(inputs.assessment, result.bundle, invariant_ids, declared_threshold=15)
    assert m["DC"]["value"] == 1.0
    assert m["RCY"]["value"] == 1.0
    assert m["NDR"]["value"] == 0.0
    assert m["OPR"]["value"] == 0.0
    assert m["ODC"]["value"] == 1.0 and m["ODC"]["numerator"] == 6 and m["ODC"]["denominator"] == 6
    assert m["PTC"]["value"] == 1.0
    assert m["CV"]["value"] == 1.0 and m["CV"]["numerator"] == 4 and m["CV"]["denominator"] == 4
    assert m["GD"]["value"] == 4
    assert sorted(r["risk_id"] for r in m["GD"]["divergent_rows"]) == ["B-03", "B-04", "B-05", "B-06"]


def test_canonical_q1_q10_all_pass_when_signed(case_b_v1_1):
    case, inputs, result = case_b_v1_1
    sign_bundle(result.bundle, case.keyring, case.parameters["bundle_signing_key"], signing_time="2026-02-16T09:05:00Z")
    results = audit_queries.run_all_audit_queries(
        result.bundle, catalog_document=inputs.catalog.canonical_document()
    )
    failures = {q: d for q, (passed, d) in results.items() if not passed}
    assert failures == {}, failures


def _gcir_id_for_acs(bundle, acs_id):
    for p in bundle.predicates:
        if p.get("acs_id") == acs_id:
            return p["gcir_id"]
    raise AssertionError("no predicate for acs_id %r" % acs_id)


def _gcir_id_for_invariant(bundle, invariant_id):
    for p in bundle.predicates:
        if p["origin"]["origin_type"] == "compiler_invariant" and p["origin"]["origin_id"] == invariant_id:
            return p["gcir_id"]
    raise AssertionError("no predicate for invariant %r" % invariant_id)


def _clean_evaluations(bundle):
    """All-pass evaluations, with the two concurrence-bearing predicates
    (ACS-B01-03, ACS-B02-02) pre-satisfied."""
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    for acs_id in ("ACS-B01-03", "ACS-B02-02"):
        gid = _gcir_id_for_acs(bundle, acs_id)
        evaluations[gid] = {"outcome": "pass", "concurrence_attestations": 1}
    return evaluations


def test_clean_control_permits(case_b_v1_1):
    _, _, result = case_b_v1_1
    verdict = resolve_phase_aware(result.bundle, _clean_evaluations(result.bundle))
    assert verdict["authorization_decision"] == "PERMIT"
    assert verdict["release_decision"] == "ALLOW_RELEASE"
    assert verdict["safe_state"] is False


def test_acs_b01_01_state_binding_mismatch_holds(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B01-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "pass", "state_digest_match": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "HOLD"
    assert verdict["safe_state"] is True


def test_acs_b01_02_known_prohibited_class_denies(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B01-02")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "DENY"


def test_acs_b01_03_enhanced_approval_pending_holds(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B01-03")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "unknown", "concurrence_attestations": 0, "concurrence_window_expired": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "HOLD"


def test_acs_b01_03_enhanced_approval_expiry_denies(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B01-03")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "unknown", "concurrence_attestations": 0, "concurrence_window_expired": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "DENY"


def test_acs_b02_01_absolute_ceiling_breach_denies_unconditionally(case_b_v1_1):
    """The hard ceiling has no escalation path -- breaching it is DENY
    regardless of the escalation tier's state."""
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B02-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "DENY"


def test_acs_b02_02_escalation_expiry_denies(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B02-02")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "unknown", "concurrence_attestations": 0, "concurrence_window_expired": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "DENY"


def test_acs_b03_01_evaluation_timeout_holds(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B03-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "pass", "timed_out": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "HOLD"


def test_acs_b05_01_replay_via_state_binding_holds(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B05-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "pass", "state_digest_match": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "HOLD"


def test_acs_b06_01_post_auth_failure_blocks_release_not_authorization(case_b_v1_1):
    """B-06 (receipt chain) is POST_AUTH_PRE_ACTUATION: authorization stays
    PERMIT (the pre-authorization conditions really were satisfied) but
    release is blocked -- the exact TOCTOU-guarding distinction runbook item 3
    asks for."""
    _, _, result = case_b_v1_1
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-B06-01")
    assert bundle.gate_map[gid].get("permit_eligible") is False
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "PERMIT"
    assert verdict["release_decision"] == "BLOCK_RELEASE"
    assert verdict["next_authorization_effect"] == "NONE"  # Case B has no POST_EVENT_AUDIT predicate


def test_inv_evidence_commit_is_post_auth_pre_actuation(case_b_v1_1):
    _, _, result = case_b_v1_1
    bundle = result.bundle
    predicate = next(p for p in bundle.predicates if p["origin"].get("origin_id") == "INV-EVIDENCE-COMMIT")
    assert predicate["enforcement_phase"] == "POST_AUTH_PRE_ACTUATION"
    gid = predicate["gcir_id"]
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["authorization_decision"] == "PERMIT"
    assert verdict["release_decision"] == "BLOCK_RELEASE"
