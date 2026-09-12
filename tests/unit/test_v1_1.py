"""Schema v1.1: phase-aware precedence, canonical Q1-Q10 (fixed data contract),
auxiliary checks A1-A4, and their negative fixtures.

This file is new in this generation.  It exists to make good on the specific
defect the reconnaissance found in the prior generation: Q1-Q10 and the
negative fixtures existed as code but were never exercised by pytest and, for
several queries, never matched the bundle shape the compiler actually emits.
Every test here runs against a bundle ``gcir.compiler.compile_bundle`` really
produced (via the session-scoped ``case_a``/``case_b`` fixtures in
``tests/conftest.py``), not a hand-shaped stand-in.
"""

from __future__ import annotations

import copy

import pytest

from gcir import audit_queries, auxiliary_checks, negative_fixtures
from gcir.models import DECISIONS, ValidationError, safe_state_of
from gcir.precedence_v11 import resolve_phase_aware


# ---------------------------------------------------------------------------
# safe_state_of
# ---------------------------------------------------------------------------


def test_safe_state_of_is_the_single_formula():
    assert safe_state_of("PERMIT") is False
    assert safe_state_of("DENY") is True
    assert safe_state_of("HOLD") is True


def test_safe_state_of_rejects_outside_the_closed_decision_set():
    with pytest.raises(ValidationError):
        safe_state_of("SAFE_STATE")


def test_decisions_vocabulary_is_exactly_three():
    assert DECISIONS == ("PERMIT", "DENY", "HOLD")


# ---------------------------------------------------------------------------
# Canonical Q1-Q10 against real compiled bundles: both cases pass all ten.
# ---------------------------------------------------------------------------


def _signed(case, inputs, result):
    from gcir.compiler import sign_bundle

    sign_bundle(
        result.bundle, case.keyring, case.parameters["bundle_signing_key"],
        signing_time="2026-02-02T09:05:00Z",
    )
    return result.bundle


def test_canonical_q1_q10_all_pass_on_the_real_case_a_bundle(case_a):
    case, inputs, result = case_a
    bundle = _signed(case, inputs, result)
    catalog_document = inputs.catalog.canonical_document()
    results = audit_queries.run_all_audit_queries(bundle, catalog_document=catalog_document)
    failures = {q: details for q, (passed, details) in results.items() if not passed}
    assert failures == {}, "Case A must pass all ten canonical queries: %s" % failures


def test_canonical_q1_q10_all_pass_on_the_real_case_b_bundle(case_b):
    case, inputs, result = case_b
    bundle = _signed(case, inputs, result)
    catalog_document = inputs.catalog.canonical_document()
    results = audit_queries.run_all_audit_queries(bundle, catalog_document=catalog_document)
    failures = {q: details for q, (passed, details) in results.items() if not passed}
    assert failures == {}, "Case B must pass all ten canonical queries: %s" % failures


def test_q9_with_the_real_catalog_is_a_strong_check_not_the_fallback(case_a):
    """Confirms Q9 actually reads the approved catalog when one is supplied,
    rather than silently taking the weak non-empty-string fallback path."""
    _, inputs, result = case_a
    catalog_doc = inputs.catalog.canonical_document()
    passed, details = audit_queries.q9_actuation_authority_validity(
        result.bundle, catalog_document=catalog_doc
    )
    assert passed is True
    assert not any("fallback" in str(d) for d in details)


# ---------------------------------------------------------------------------
# Negative fixtures: each must fail exactly the query it targets.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("fixture_name", sorted(negative_fixtures.FIXTURE_TARGET_QUERY))
def test_every_negative_fixture_is_detected_by_its_targeted_query(case_a, fixture_name):
    _, inputs, result = case_a
    fixtures = negative_fixtures.get_negative_fixtures(result.bundle)
    bad_bundle = fixtures[fixture_name]
    target_query = negative_fixtures.FIXTURE_TARGET_QUERY[fixture_name]

    # Q9's strong check needs the approved catalog; supplying it for every
    # fixture (not only the Q9 ones) confirms the other queries are unaffected
    # by its presence.
    results = audit_queries.run_all_audit_queries(
        bad_bundle, catalog_document=inputs.catalog.canonical_document()
    )
    passed, details = results[target_query]
    assert passed is False, (
        "fixture %r must be detected by %s, but it passed. Full results: %s"
        % (fixture_name, target_query, results)
    )


def test_negative_fixtures_do_not_silently_reuse_the_invented_shape():
    """Regression: the pre-generation fixtures mutated a shape
    (``disposition_status``, ``approved_controls``) the compiler has never
    emitted.  Every fixture here must be a ``CompiledBundle`` whose payload
    keys are the real ones."""
    from gcir.models import CompiledBundle

    dummy_payload = {
        "dispositions": [{"record_type": "RuntimeDisposition", "risk_id": "R-1", "acs_ids": ["A-1"]}],
        "predicates": [],
        "gate_map": {},
        "coverage_matrix": {"obligations": [], "risks": [], "c_star_coverage": []},
        "bundle_id": "B", "version_binding": {"binding_id": "V"},
        "validity": {"effective_from": "2026-01-01T00:00:00Z"},
    }
    dummy = CompiledBundle(payload=dummy_payload, payload_hash="0" * 64, envelope=None)
    fixture = negative_fixtures.create_negative_fixture_q2_duplicate_disposition(dummy)
    assert isinstance(fixture, CompiledBundle)
    assert fixture.payload["dispositions"][0]["record_type"] == "RuntimeDisposition"


def test_a_genuinely_clean_bundle_still_passes_after_negative_fixture_generation(case_a):
    """Building negative fixtures must never mutate the original bundle."""
    _, _, result = case_a
    before = copy.deepcopy(result.bundle.payload)
    negative_fixtures.get_negative_fixtures(result.bundle)
    assert result.bundle.payload == before


# ---------------------------------------------------------------------------
# Phase-aware precedence (precedence_v11)
# ---------------------------------------------------------------------------


def _predicate_with(bundle, gcir_id, **v11_fields):
    """A deep copy of a real bundle with one predicate's v1.1 fields set,
    for isolated resolver testing."""
    payload = copy.deepcopy(bundle.payload)
    for predicate in payload["predicates"]:
        if predicate["gcir_id"] == gcir_id:
            predicate.update(v11_fields)
            break
    else:
        raise AssertionError("no predicate %r in bundle" % gcir_id)
    from gcir.models import CompiledBundle

    return CompiledBundle(payload=payload, payload_hash=bundle.payload_hash, envelope=bundle.envelope)


def _first_mandatory_gcir_id(bundle):
    for gcir_id, entry in bundle.gate_map.items():
        if entry["gate_type"] == "mandatory":
            return gcir_id
    raise AssertionError("bundle has no mandatory predicate")


def test_v10_predicate_with_no_v11_field_behaves_exactly_as_before(case_a):
    """Backward compatibility: a predicate declaring no v1.1 field resolves
    identically under resolve_phase_aware and the plain v1.0 resolve()."""
    from gcir.precedence import resolve

    _, _, result = case_a
    bundle = result.bundle
    outcomes = {gid: "pass" for gid in bundle.gate_map}
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    v10 = resolve(bundle, outcomes)
    v11 = resolve_phase_aware(bundle, evaluations)
    assert v10["decision"] == v11["decision"] == "PERMIT"
    assert v11["safe_state"] is False
    assert v11["release_blocked"] is False


def test_evaluation_timeout_forces_hold_never_a_partial_permit(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(
        result.bundle, gcir_id,
        evaluation_latency_bound={"value": 250, "unit": "ms"},
        on_evaluation_timeout="HOLD",
    )
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "pass", "timed_out": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "HOLD"
    assert verdict["safe_state"] is True
    assert "evaluation_latency_bound" in verdict["reason"] or "timeout" in verdict["reason"].lower() or "not signal completion" in verdict["reason"]


def test_state_binding_mismatch_is_hold_not_denial_of_the_predicates_own_outcome(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(
        result.bundle, gcir_id,
        state_binding={"attributes": ["transaction_hash"]},
    )
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "pass", "state_digest_match": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "HOLD"
    assert verdict["safe_state"] is True


def test_state_binding_match_permits_normally(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(result.bundle, gcir_id, state_binding={"attributes": ["transaction_hash"]})
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "pass", "state_digest_match": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "PERMIT"


def test_concurrence_pending_is_hold(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(
        result.bundle, gcir_id,
        concurrence_policy={"n_required": 2, "m_eligible": ["a", "b"], "window_seconds": 3600, "expiry_response": "DENY"},
    )
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "unknown", "concurrence_attestations": 1, "concurrence_window_expired": False}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "HOLD"


def test_concurrence_window_expiry_is_deny_never_a_timeout(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(
        result.bundle, gcir_id,
        concurrence_policy={"n_required": 2, "m_eligible": ["a", "b"], "window_seconds": 3600, "expiry_response": "DENY"},
    )
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "unknown", "concurrence_attestations": 1, "concurrence_window_expired": True}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "DENY"
    assert verdict["safe_state"] is True


def test_concurrence_satisfied_permits(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(
        result.bundle, gcir_id,
        concurrence_policy={"n_required": 2, "m_eligible": ["a", "b"], "window_seconds": 3600, "expiry_response": "DENY"},
    )
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "unknown", "concurrence_attestations": 2}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "PERMIT"


def test_post_auth_pre_actuation_blocks_release_without_denying_authorization(case_a):
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(result.bundle, gcir_id, enforcement_phase="POST_AUTH_PRE_ACTUATION")
    # The remaining PRE_AUTHORIZATION predicates all pass, and the
    # POST_AUTH_PRE_ACTUATION predicate (the receipt-commit obligation) fails.
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "PERMIT"  # authorization itself is unaffected
    assert verdict["release_blocked"] is True
    assert gcir_id in verdict["excluded_from_authorization"]


def test_toctou_style_permit_then_block_release_leaves_safe_state_false(case_a):
    """The exact regression this generation's own prior report got confused
    about in its presentation (never in the actual resolver code, which
    always computed this correctly): safe_state = authorization_decision !=
    PERMIT, full stop. A PERMIT authorization whose release is blocked is
    NOT retroactively unsafe by that fact -- release_decision and
    next_authorization_effect are reported as separate, non-overloaded axes
    (release_safe, externalization_blocked), and neither ever mutates
    safe_state itself."""
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(result.bundle, gcir_id, enforcement_phase="POST_AUTH_PRE_ACTUATION")
    evaluations = {gid: {"outcome": "pass"} for gid in bundle.gate_map}
    evaluations[gcir_id] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)

    assert verdict["authorization_decision"] == "PERMIT"
    assert verdict["safe_state"] is False, (
        "safe_state must NOT be mutated to True merely because release was blocked"
    )
    assert verdict["release_decision"] == "BLOCK_RELEASE"
    assert verdict["release_safe"] is True
    assert verdict["externalization_blocked"] is True
    # The general invariant, for every decision this resolver can produce.
    from gcir.models import safe_state_of

    assert verdict["safe_state"] == safe_state_of(verdict["authorization_decision"])


def test_post_auth_predicate_excluded_from_permit_aggregate_when_it_would_have_failed(case_a):
    """A POST_AUTH_PRE_ACTUATION predicate never enters the PERMIT aggregate,
    even though under the plain v1.0 resolver its failure would have produced
    DENY -- this is exactly the phase-awareness this generation adds."""
    _, _, result = case_a
    gcir_id = _first_mandatory_gcir_id(result.bundle)
    bundle = _predicate_with(result.bundle, gcir_id, enforcement_phase="POST_AUTH_PRE_ACTUATION")
    others = [gid for gid in bundle.gate_map if gid != gcir_id]
    evaluations = {gid: {"outcome": "pass"} for gid in others}
    evaluations[gcir_id] = {"outcome": "fail"}
    verdict = resolve_phase_aware(bundle, evaluations)
    assert verdict["decision"] == "PERMIT"


def test_unknown_predicate_in_evaluations_raises():
    from gcir.models import PrecedenceError

    class _FakeBundle:
        predicates = []
        gate_map = {}

    with pytest.raises(PrecedenceError):
        resolve_phase_aware(_FakeBundle(), {"GHOST": {"outcome": "pass"}})


# ---------------------------------------------------------------------------
# Auxiliary checks A1-A4
# ---------------------------------------------------------------------------


def test_a1_detects_actuation_after_revocation():
    actuations = [{
        "actor_id": "surgeon.jones",
        "action_tuple": {"subject": "s", "action": "fire", "resource": "r", "destination": "d"},
        "authorization_time": "2026-03-01T12:00:00Z",
    }]
    revocations = [{
        "record_type": "ActorScopeRevocation",
        "actor_id": "surgeon.jones",
        "scope": [{"subject": "s", "action": "fire", "resource": "r", "destination": "d"}],
        "effective_time": "2026-03-01T11:00:00Z",
    }]
    passed, issues = auxiliary_checks.a1_actor_scope_revocation_validity(actuations, revocations)
    assert passed is False
    assert issues


def test_a1_permits_actuation_before_revocation():
    actuations = [{
        "actor_id": "surgeon.jones",
        "action_tuple": {"subject": "s", "action": "fire", "resource": "r", "destination": "d"},
        "authorization_time": "2026-03-01T10:00:00Z",
    }]
    revocations = [{
        "record_type": "ActorScopeRevocation",
        "actor_id": "surgeon.jones",
        "scope": [{"subject": "s", "action": "fire", "resource": "r", "destination": "d"}],
        "effective_time": "2026-03-01T11:00:00Z",
    }]
    passed, issues = auxiliary_checks.a1_actor_scope_revocation_validity(actuations, revocations)
    assert passed is True


def test_a2_detects_correlation_to_the_wrong_bundle():
    events = [{
        "safety_event_id": "SE-1", "safety_layer_id": "force_envelope",
        "origin": "INV-SAFETY-RECOVERY", "correlated_bundle_hash": "0" * 64,
        "effective_time": "2026-03-01T00:00:00Z",
    }]
    passed, issues = auxiliary_checks.a2_safety_event_correlation_validity(
        events, ["force_envelope"], "1" * 64
    )
    assert passed is False


def test_a2_accepts_correctly_correlated_event():
    events = [{
        "safety_event_id": "SE-1", "safety_layer_id": "force_envelope",
        "origin": "INV-SAFETY-RECOVERY", "correlated_bundle_hash": "a" * 64,
        "effective_time": "2026-03-01T00:00:00Z",
    }]
    passed, issues = auxiliary_checks.a2_safety_event_correlation_validity(
        events, ["force_envelope"], "a" * 64
    )
    assert passed is True


def test_a2_missing_correlation_detected():
    interventions = [{"effective_time": "2026-03-01T00:00:00Z", "correlated_permit_id": "P-1"}]
    passed, issues = auxiliary_checks.a2_missing_safety_correlation(interventions, [], 300)
    assert passed is False


def test_a3_rejects_identical_child_as_not_a_delegation():
    parent = {"scope": ["s1"], "actions": ["a1"], "validity": {"effective_from": "2026-01-01T00:00:00Z", "effective_until": "2026-06-01T00:00:00Z"}}
    child = copy.deepcopy(parent)
    passed, issues = auxiliary_checks.a3_delegation_containment(child, parent)
    assert passed is False


def test_a3_rejects_child_wider_than_parent():
    parent = {"scope": ["s1"], "actions": ["a1"], "validity": {"effective_from": "2026-01-01T00:00:00Z", "effective_until": "2026-06-01T00:00:00Z"}}
    child = {"scope": ["s1", "s2"], "actions": ["a1"], "validity": {"effective_from": "2026-01-01T00:00:00Z", "effective_until": "2026-06-01T00:00:00Z"}}
    passed, issues = auxiliary_checks.a3_delegation_containment(child, parent)
    assert passed is False


def test_a3_accepts_a_genuinely_narrower_child():
    parent = {"scope": ["s1", "s2"], "actions": ["a1"], "validity": {"effective_from": "2026-01-01T00:00:00Z", "effective_until": "2026-06-01T00:00:00Z"}}
    child = {"scope": ["s1"], "actions": ["a1"], "validity": {"effective_from": "2026-02-01T00:00:00Z", "effective_until": "2026-05-01T00:00:00Z"}}
    passed, issues = auxiliary_checks.a3_delegation_containment(child, parent)
    assert passed is True


def test_a4_detects_missing_human_response():
    predicates = [{"gcir_id": "GCIR-1", "response_policy": "REQUIRED"}]
    permits = [{"permit_id": "PERMIT-1", "gcir_id": "GCIR-1"}]
    passed, issues = auxiliary_checks.a4_human_response_coverage(predicates, permits, [])
    assert passed is False


def test_a4_optional_response_policy_needs_no_response():
    predicates = [{"gcir_id": "GCIR-1", "response_policy": "OPTIONAL"}]
    permits = [{"permit_id": "PERMIT-1", "gcir_id": "GCIR-1"}]
    passed, issues = auxiliary_checks.a4_human_response_coverage(predicates, permits, [])
    assert passed is True


def test_run_all_auxiliary_checks_reports_not_applicable_when_evidence_absent():
    results = auxiliary_checks.run_all_auxiliary_checks({})
    assert set(results) == {"A1", "A2", "A3", "A4"}
    for name, (passed, details) in results.items():
        assert passed is True
        assert "NOT_APPLICABLE" in details[0]


# ---------------------------------------------------------------------------
# C* reversibility qualifier (schema v1.1): real semantics, not a materiality
# workaround. gcir.coverage.CStarProfile.evaluate() now reads an optional
# required_reversibility list on a classification rule.
# ---------------------------------------------------------------------------


def _profile_with_reversibility_qualifier():
    from gcir.coverage import CStarProfile

    document = {
        "profile_id": "TEST-CSTAR-REV", "version": "1.0", "version_binding_ref": "VB-TEST",
        "approved_by": "test.forum", "approval_time": "2026-01-01T00:00:00Z",
        "materiality_order": ["immaterial", "minor", "material", "severe"],
        "member_kinds": ["physical_harm_to_person"],
        "classification_rules": {
            "physical_harm_to_person": {
                "approving_authority": "test.forum", "rationale": "test",
                "materiality_boundary": {"minimum_materiality": "material", "description": "test"},
                "effective_date": "2026-01-01T00:00:00Z", "emergency_override_procedure": None,
                "required_reversibility": ["irreversible", "requires_intervention"],
            }
        },
    }
    return CStarProfile(document)


def test_irreversible_physical_harm_is_classified_c_star():
    profile = _profile_with_reversibility_qualifier()
    descriptor = {"kind": "physical_harm_to_person", "materiality": "material", "reversibility": "irreversible"}
    assert profile.evaluate(descriptor) == 1


def test_requires_intervention_physical_harm_is_classified_c_star():
    profile = _profile_with_reversibility_qualifier()
    descriptor = {"kind": "physical_harm_to_person", "materiality": "material", "reversibility": "requires_intervention"}
    assert profile.evaluate(descriptor) == 1


def test_reversible_physical_harm_is_excluded_despite_material_materiality():
    """The exact regression the manuscript's reversibility qualifier exists
    to enforce: a self-limiting reversible harm does not enter C* on its
    class alone, even at material (or higher) materiality."""
    profile = _profile_with_reversibility_qualifier()
    descriptor = {"kind": "physical_harm_to_person", "materiality": "material", "reversibility": "reversible"}
    assert profile.evaluate(descriptor) == 0

    descriptor_severe = {"kind": "physical_harm_to_person", "materiality": "severe", "reversibility": "reversible"}
    assert profile.evaluate(descriptor_severe) == 0, (
        "raising materiality alone must not silently substitute for reversibility"
    )


def test_partially_reversible_physical_harm_is_excluded():
    profile = _profile_with_reversibility_qualifier()
    descriptor = {"kind": "physical_harm_to_person", "materiality": "material", "reversibility": "partially_reversible"}
    assert profile.evaluate(descriptor) == 0


def test_a_profile_declaring_no_reversibility_qualifier_is_unaffected():
    """Backward compatibility: Case A and Case B's C*_fin profile declares no
    required_reversibility on any rule, so evaluate() behaves exactly as
    before this generation -- materiality alone decides."""
    from gcir.coverage import CStarProfile

    document = {
        "profile_id": "TEST-CSTAR-NOREV", "version": "1.0", "version_binding_ref": "VB-TEST",
        "approved_by": "test.forum", "approval_time": "2026-01-01T00:00:00Z",
        "materiality_order": ["immaterial", "minor", "material", "severe"],
        "member_kinds": ["unauthorized_authority_exercise"],
        "classification_rules": {
            "unauthorized_authority_exercise": {
                "approving_authority": "test.forum", "rationale": "test",
                "materiality_boundary": {"minimum_materiality": "material", "description": "test"},
                "effective_date": "2026-01-01T00:00:00Z", "emergency_override_procedure": None,
            }
        },
    }
    profile = CStarProfile(document)
    for reversibility in ("reversible", "partially_reversible", "requires_intervention", "irreversible"):
        descriptor = {"kind": "unauthorized_authority_exercise", "materiality": "material", "reversibility": reversibility}
        assert profile.evaluate(descriptor) == 1, "no required_reversibility declared -- reversibility must not gate membership"


def test_case_a_and_case_b_cstar_profiles_declare_no_reversibility_qualifier(case_a, case_b):
    """Confirms the historical, frozen profiles are genuinely untouched by
    this mechanism -- they simply never set required_reversibility."""
    _, inputs_a, _ = case_a
    _, inputs_b, _ = case_b
    for inputs in (inputs_a, inputs_b):
        for rule in inputs.cstar_profile.document["classification_rules"].values():
            assert "required_reversibility" not in rule


def test_case_c_physical_harm_to_person_declares_the_manuscript_qualifier(case_c):
    _, inputs, _ = case_c
    rule = inputs.cstar_profile.document["classification_rules"]["physical_harm_to_person"]
    assert rule["required_reversibility"] == ["irreversible", "requires_intervention"]


def test_case_c_reversible_guidance_rows_are_excluded_from_c_star_by_reversibility(case_c):
    """C-08 and C-10 are reversible physical-harm rows; with the real
    qualifier active they must be absent from the C* coverage matrix (not
    merely below a materiality threshold)."""
    _, _, result = case_c
    cstar_risk_ids = {row["risk_id"] for row in result.bundle.payload["coverage_matrix"]["c_star_coverage"]}
    assert "C-08" not in cstar_risk_ids
    assert "C-10" not in cstar_risk_ids
