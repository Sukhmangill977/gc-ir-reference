"""Unit tests for gcir.contract_v12 (Paper 2 v1.2 spec sections 1A-1L, 5).

Development-generation artifact; not part of any frozen preregister-tier0
campaign. Exercises every headline validator against the real Case D CCS1
compiled bundle plus the v1.2 negative fixtures in gcir.negative_fixtures,
mirroring how tests/unit/test_core.py exercises gcir.audit_queries.
"""

from __future__ import annotations

import copy

from gcir import contract_v12, negative_fixtures
from gcir.compiler import compile_bundle
from gcir.models import PRIMARY_CLASSES


def test_run_all_v12_checks_pass_on_an_unmutated_bundle(case_d_ccs1):
    _, _, result = case_d_ccs1
    results = contract_v12.run_all_v12_checks(result.bundle, result.bundle)
    for check_id, (ok, issues) in results.items():
        assert ok, "%s unexpectedly failed on an unmutated bundle: %s" % (check_id, issues)


def test_judgment_hash_binding_positive_and_negative(case_d_ccs1):
    case, inputs, result = case_d_ccs1
    ok, issues = contract_v12.judgment_hash_binding(result.bundle, expected_judgment=inputs.judgment)
    assert ok, issues

    nominal, candidate = negative_fixtures.create_negative_fixture_v12_judgment_hash_tamper(result.bundle)
    ok, issues = contract_v12.judgment_hash_binding(candidate, expected_judgment=inputs.judgment)
    assert not ok
    assert "content_hash" in issues[0]


def test_no_narrowing_positive_and_negative(case_d_ccs1):
    _, _, result = case_d_ccs1
    ok, _ = contract_v12.no_narrowing(result.bundle, result.bundle)
    assert ok

    nominal, candidate = negative_fixtures.create_negative_fixture_v12_narrowing(result.bundle)
    ok, issues = contract_v12.no_narrowing(nominal, candidate)
    assert not ok
    assert "dropped" in issues[0]


def test_no_broadening_positive_and_negative(case_d_ccs1):
    _, _, result = case_d_ccs1
    ok, _ = contract_v12.no_broadening(result.bundle, result.bundle)
    assert ok

    nominal, candidate = negative_fixtures.create_negative_fixture_v12_broadening(result.bundle)
    ok, issues = contract_v12.no_broadening(nominal, candidate)
    assert not ok
    assert "widened" in issues[0]


def test_no_invention_positive_and_negative(case_d_ccs1):
    _, _, result = case_d_ccs1
    ok, _ = contract_v12.no_invention(result.bundle, result.bundle)
    assert ok

    nominal, candidate = negative_fixtures.create_negative_fixture_v12_invention(result.bundle)
    ok, issues = contract_v12.no_invention(nominal, candidate)
    assert not ok
    assert "invented" in issues[0]


def test_primary_class_preservation_rejects_named_collapses(case_d_ccs1):
    _, _, result = case_d_ccs1
    nominal, candidate = negative_fixtures.create_negative_fixture_v12_class_collapse(result.bundle)
    ok, issues = contract_v12.primary_class_preservation(nominal, candidate)
    assert not ok
    assert "human -> auth" in issues[0]


def test_primary_class_is_closed_and_singular():
    assert PRIMARY_CLASSES == ("auth", "meta", "standing", "state", "evidence", "human", "audit")


def test_indeterminacy_compile_fail_never_becomes_deny_or_hold(case_d_ccs1):
    from gcir.models import IndeterminacyError
    from tools import case_d_control as ctl

    case, _, _ = case_d_ccs1
    acs = [ctl.acs_d01_01(), ctl.acs_d02_01(authorized_actor=["treasury.officer_on_duty"], interpretation_status="unresolved")]
    override = {"approved_control_specifications": {"acs_set_id": "TEST-INDET", "version_binding_ref": ctl.BINDING, "records": acs}}

    def compile_attempt():
        inputs = case.compiler_inputs(overrides=override)
        return compile_bundle(inputs, verify_signatures=False)

    ok, issues = contract_v12.indeterminacy(compile_attempt)
    assert not ok
    assert "COMPILE-FAIL" in issues[0]

    import pytest
    with pytest.raises(IndeterminacyError):
        compile_attempt()


def test_exception_scope_rejects_global_bypass(case_d_ccs1):
    _, _, result = case_d_ccs1
    nominal, candidate = negative_fixtures.create_negative_fixture_v12_exception_widening(result.bundle)
    ok, issues = contract_v12.exception_scope(nominal, candidate)
    assert not ok
    assert "global bypass" in issues[0]


def test_lifecycle_flags_a_stale_judgment_version(case_d_ccs1, case_d_ccs2):
    _, _, ccs1 = case_d_ccs1
    _, _, ccs2 = case_d_ccs2
    ccs2_version = ccs2.bundle.payload["judgment_record_ref"]["version"]
    ok, issues = contract_v12.lifecycle(ccs1.bundle, expected_judgment_version=ccs2_version)
    assert not ok
    assert "does not match the current judgment version" in issues[0]


def test_declared_path_flags_an_undeclared_but_claimed_path(case_d_ccs1):
    _, _, result = case_d_ccs1
    declared = [{"path_id": "PATH-RELEASE", "subject": "treasury_agent", "action": "release_funds",
                 "resource": "funds_transfer_instruction", "destination": "treasury_rail"}]
    ok, _ = contract_v12.declared_path(result.bundle, declared)
    assert ok

    missing = declared + [{"path_id": "PATH-NEVER-COMPILED", "subject": "treasury_agent",
                            "action": "release_funds_via_undeclared_channel",
                            "resource": "funds_transfer_instruction", "destination": "treasury_rail"}]
    ok, issues = contract_v12.declared_path(result.bundle, missing)
    assert not ok
    assert "PATH-NEVER-COMPILED" in issues[0]


def test_synchronization_contract_representation_positive_and_negative(case_d_ccs1):
    _, _, result = case_d_ccs1
    nominal, candidate = negative_fixtures.create_negative_fixture_v12_sync_contract_incomplete(result.bundle)
    ok, _ = contract_v12.synchronization_contract_representation(nominal)
    assert ok
    ok, issues = contract_v12.synchronization_contract_representation(candidate)
    assert not ok
    assert "invalidation_trigger" in issues[0]


def test_observation_obligation_and_no_narrowing_over_beta_r(case_d_ccs1):
    _, _, result = case_d_ccs1
    nominal, candidate = negative_fixtures.create_negative_fixture_v12_observation_scope_removed(result.bundle)
    ok, _ = contract_v12.observation_obligation(nominal)
    assert ok
    ok, _ = contract_v12.observation_obligation(candidate)
    assert ok, "beta_r is still non-empty after dropping one element -- representation-only check correctly still passes"

    ok, issues = contract_v12.no_narrowing(nominal, candidate)
    assert not ok
    assert "beta_r" in issues[0]


def test_evidence_representation_rejects_empty_evidence_producer(case_d_ccs1):
    from gcir.models import CompiledBundle

    _, _, result = case_d_ccs1
    ok, _ = contract_v12.evidence_representation(result.bundle)
    assert ok

    negative_payload = copy.deepcopy(result.bundle.payload)
    negative_payload["predicates"][0]["evidence_producer"] = ""
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    ok, issues = contract_v12.evidence_representation(negative_bundle)
    assert not ok
    assert "evidence_producer" in issues[0]


def test_failure_semantics_rejects_weakened_on_fail(case_d_ccs1):
    from gcir.models import CompiledBundle

    _, _, result = case_d_ccs1
    ok, _ = contract_v12.failure_semantics(result.bundle, result.bundle)
    assert ok

    negative_payload = copy.deepcopy(result.bundle.payload)
    negative_payload["predicates"][0]["on_fail"] = "WARN"
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    ok, issues = contract_v12.failure_semantics(result.bundle, negative_bundle)
    assert not ok
    assert "weakened" in issues[0]


def test_origin_flags_an_unauthorized_authorizer(case_d_ccs1):
    _, _, result = case_d_ccs1
    # ACS-derived predicates are authorized by the approver
    # ("forum.chair_treasury"); compiler-invariant predicates are
    # authorized by the forum itself ("treasury_governance_forum") -- both
    # are legitimately approved authorizers for this bundle.
    ok, _ = contract_v12.origin(result.bundle, approved_authorizers={"forum.chair_treasury", "treasury_governance_forum"})
    assert ok
    ok, issues = contract_v12.origin(result.bundle, approved_authorizers={"someone.else"})
    assert not ok
    assert "authorized_by" in issues[0]


def test_total_disposition_detects_a_duplicate_record(case_d_ccs1):
    from gcir.models import CompiledBundle

    _, _, result = case_d_ccs1
    ok, _ = contract_v12.total_disposition(result.bundle)
    assert ok

    negative_payload = copy.deepcopy(result.bundle.payload)
    negative_payload["dispositions"].append(copy.deepcopy(negative_payload["dispositions"][0]))
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    ok, issues = contract_v12.total_disposition(negative_bundle)
    assert not ok
