"""Case C -- supervised-autonomy surgical assistant, compiled for the first
time this generation. See docs/CASE_C_STATUS.md for the exact claim boundary
and scope reductions relative to the manuscript's Tables V-VI.

Development-generation artifact (schema v1.1); not part of the frozen
preregister-tier0-v3.1 campaign.
"""

from __future__ import annotations

import json
import os

from gcir import audit_queries, auxiliary_checks
from gcir.compiler import sign_bundle
from gcir.precedence_v11 import resolve_phase_aware
from gcir.validation import validate_document

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_case_is_marked_synthetic():
    with open(os.path.join(REPO_ROOT, "cases", "case_c", "inputs", "assessment.json")) as fh:
        assessment = json.load(fh)
    assert assessment["case_class"] == "synthetic"


def test_structure_matches_the_manuscript_tables_v_vi(case_c):
    _, _, result = case_c
    stats = result.statistics
    assert stats["risk_count"] == 16
    assert stats["acs_count"] == 13
    assert stats["predicate_count"] == 16
    assert stats["risk_derived_predicate_count"] == 13
    assert stats["compiler_invariant_predicate_count"] == 3


def test_thirteen_runtime_three_nonruntime_dispositions(case_c):
    _, _, result = case_c
    bundle = result.bundle
    runtime = sorted(d["risk_id"] for d in bundle.dispositions if d["record_type"] == "RuntimeDisposition")
    nonruntime = {d["risk_id"]: (d["reason_code"], d["routed_to_control_family"]) for d in bundle.dispositions if d["record_type"] == "NonRuntimeDisposition"}
    assert runtime == ["C-01", "C-02", "C-03", "C-04", "C-05", "C-08", "C-09", "C-10", "C-11", "C-12", "C-13", "C-14", "C-15"]
    assert nonruntime == {
        "C-06": ("RC-06", "runtime_safety"),
        "C-07": ("RC-06", "runtime_safety"),
        "C-16": ("RC-03", "human_process"),
    }


def test_c06_c07_are_cstar_by_severity_but_exempt_from_coverage_via_rc06(case_c):
    """The AD-1/RC-06 carve-out this generation adds to verify_cv: a
    continuous-control hazard may be C*-eligible by kind/materiality while
    declaring no hazardous action path, without that being a coverage
    failure -- exactly the manuscript's "correctly ungated although the
    threshold rule would gate it" claim for C-06."""
    _, _, result = case_c
    coverage = {row["risk_id"]: row for row in result.bundle.payload["coverage_matrix"]["c_star_coverage"]}
    assert coverage["C-06"]["c_star"] == 1
    assert coverage["C-06"]["covered"] is True
    assert "RC-06" in coverage["C-06"]["exemption"]
    assert coverage["C-07"]["c_star"] == 1
    assert coverage["C-07"]["covered"] is True


def test_seven_runtime_rows_are_cstar_classified(case_c):
    _, _, result = case_c
    coverage = {row["risk_id"] for row in result.bundle.payload["coverage_matrix"]["c_star_coverage"] if "exemption" not in row}
    assert coverage == {"C-01", "C-02", "C-03", "C-04", "C-05", "C-09", "C-12"}


def test_bundle_validates_against_schema(case_c):
    _, _, result = case_c
    validate_document(result.bundle.payload, "bundle.schema.json", label="case_c bundle")


def test_hash_matches_reference(case_c):
    _, _, result = case_c
    with open(os.path.join(REPO_ROOT, "cases", "case_c", "expected", "reference_hashes.json")) as fh:
        reference = json.load(fh)
    assert result.bundle.payload["schema_version"] == "1.1"
    assert result.bundle.payload_hash == reference["payload_hash"]


def test_canonical_q1_q10_all_pass_when_signed(case_c):
    case, inputs, result = case_c
    sign_bundle(result.bundle, case.keyring, case.parameters["bundle_signing_key"], signing_time="2026-03-02T09:05:00Z")
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


def _clean_evaluations(bundle):
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    gid_c04 = _gcir_id_for_acs(bundle, "ACS-C04-01")
    evaluations[gid_c04] = {"outcome": "pass", "concurrence_attestations": 2}
    return evaluations


def test_clean_control_permits(case_c):
    _, _, result = case_c
    bundle = result.bundle
    verdict = resolve_phase_aware(bundle, _clean_evaluations(bundle))
    assert verdict["decision"] == "PERMIT"
    assert verdict["safe_state"] is False


def test_c02_state_binding_mismatch_holds(case_c):
    """Energy delivered outside the authorized world state (Section XI, C-02):
    a digest mismatch at the boundary is HOLD, not a silent permit."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C02-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "pass", "state_digest_match": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "HOLD"


def test_c04_concurrence_pending_holds(case_c):
    """Control transfer without both parties' attestation (C-04): pending
    2-of-2 concurrence is HOLD."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C04-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "unknown", "concurrence_attestations": 1, "concurrence_window_expired": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "HOLD"


def test_c04_concurrence_expiry_denies(case_c):
    """C-04: a releasing attestation with no receiving one when the window
    closes is DENY (concurrence_expiry_response), not a pending transfer."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C04-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "unknown", "concurrence_attestations": 1, "concurrence_window_expired": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "DENY"


def test_c14_evaluation_timeout_holds(case_c):
    """C-14: the independent deadline watchdog expiring is HOLD, never a
    partial permit."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C14-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "pass", "timed_out": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "HOLD"


def test_c15_post_event_audit_excluded_from_authorization(case_c):
    """C-15's safety-event correlation check is POST_EVENT_AUDIT: it never
    gates the intervention it audits."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C15-01")
    assert bundle.gate_map[gid].get("permit_eligible") is False
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "PERMIT"


def test_c01_known_contraindication_denies(case_c):
    """C-01: a known contraindicated instrument-procedure combination is a
    known failure -- DENY, not HOLD."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C01-01")
    evaluations = _clean_evaluations(bundle)
    evaluations[gid] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "DENY"


# ---------------------------------------------------------------------------
# Auxiliary checks A1-A4, exercised with Case C's own actors/permits
# ---------------------------------------------------------------------------


def test_a1_actor_scope_revocation_over_case_c_actuation():
    from tools.case_c_data import ACTIVATE_INSTRUMENT

    actuations = [{"actor_id": "surgeon.primary", "action_tuple": ACTIVATE_INSTRUMENT, "authorization_time": "2026-03-05T10:00:00Z"}]
    revocations = [{
        "record_type": "ActorScopeRevocation", "actor_id": "surgeon.primary",
        "scope": [ACTIVATE_INSTRUMENT], "effective_time": "2026-03-05T09:00:00Z",
    }]
    passed, issues = auxiliary_checks.a1_actor_scope_revocation_validity(actuations, revocations)
    assert passed is False


def test_a2_safety_event_correlates_to_case_c_bundle(case_c):
    _, _, result = case_c
    events = [{
        "safety_event_id": "SE-C-1", "safety_layer_id": "force_envelope",
        "origin": "INV-SAFETY-RECOVERY", "correlated_bundle_hash": result.bundle.payload_hash,
        "effective_time": "2026-03-05T10:00:00Z",
    }]
    passed, issues = auxiliary_checks.a2_safety_event_correlation_validity(
        events, ["force_envelope", "instrument_interlock"], result.bundle.payload_hash
    )
    assert passed is True


def test_a3_delegated_subtask_containment():
    """C-12: delegated subtask exceeds delegation scope -- a child wider than
    its parent is rejected."""
    parent = {"scope": ["procedure_field:step_6"], "actions": ["enter_autonomous_subtask"],
              "validity": {"effective_from": "2026-03-05T09:00:00Z", "effective_until": "2026-03-05T11:00:00Z"}}
    wider_child = {"scope": ["procedure_field:step_6", "procedure_field:step_7"], "actions": ["enter_autonomous_subtask"],
                   "validity": {"effective_from": "2026-03-05T09:00:00Z", "effective_until": "2026-03-05T11:00:00Z"}}
    passed, issues = auxiliary_checks.a3_delegation_containment(wider_child, parent)
    assert passed is False

    narrower_child = {"scope": ["procedure_field:step_6"], "actions": ["enter_autonomous_subtask"],
                       "validity": {"effective_from": "2026-03-05T09:30:00Z", "effective_until": "2026-03-05T10:30:00Z"}}
    passed, issues = auxiliary_checks.a3_delegation_containment(narrower_child, parent)
    assert passed is True


def test_a4_human_response_required_for_c08_guidance(case_c):
    """C-08's PRESENT_GUIDANCE predicate declares response_policy=REQUIRED."""
    _, _, result = case_c
    bundle = result.bundle
    gid = _gcir_id_for_acs(bundle, "ACS-C08-01")
    predicate = next(p for p in bundle.predicates if p["gcir_id"] == gid)
    assert predicate.get("response_policy") == "REQUIRED"

    permits = [{"permit_id": "PERMIT-C08-1", "gcir_id": gid}]
    passed, issues = auxiliary_checks.a4_human_response_coverage(bundle.predicates, permits, [])
    assert passed is False

    responses = [{"permit_id": "PERMIT-C08-1", "response": "followed", "responder": "surgeon.primary", "response_time": "2026-03-05T10:01:00Z"}]
    passed, issues = auxiliary_checks.a4_human_response_coverage(bundle.predicates, permits, responses)
    assert passed is True
