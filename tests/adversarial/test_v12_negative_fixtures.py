"""Regression test for every new Paper 2 v1.2 negative fixture (spec
sections 9-10): each must be detected, by its declared target check, for
the expected reason -- never silently accepted.

Development-generation artifact; not part of any frozen preregister-tier0
campaign.
"""

from __future__ import annotations

import pytest

from gcir import contract_v12, negative_fixtures


def _check_for(target):
    if target == "judgment_hash_binding":
        def check(nominal, candidate, case=None, expected_judgment=None):
            return contract_v12.judgment_hash_binding(candidate, expected_judgment=expected_judgment)
        return check
    if target == "lifecycle":
        def check(nominal, candidate, case=None, expected_judgment=None):
            return contract_v12.lifecycle(candidate, expected_judgment_version="9.9-nonexistent")
        return check
    if target == "synchronization_contract_representation":
        def check(nominal, candidate, case=None, expected_judgment=None):
            return contract_v12.synchronization_contract_representation(candidate)
        return check
    fn = getattr(contract_v12, target)

    def check(nominal, candidate, case=None, expected_judgment=None):
        return fn(nominal, candidate)

    return check


@pytest.mark.parametrize("fixture_name", sorted(negative_fixtures.FIXTURE_TARGET_CHECK_V12))
def test_v12_negative_fixture_is_detected_for_the_expected_reason(fixture_name, case_d_ccs1):
    case, inputs, result = case_d_ccs1
    builder = getattr(negative_fixtures, "create_negative_fixture_" + fixture_name[len("negative_"):])
    nominal, candidate = builder(result.bundle)

    target = negative_fixtures.FIXTURE_TARGET_CHECK_V12[fixture_name]
    check = _check_for(target)
    ok, issues = check(nominal, candidate, case=case, expected_judgment=inputs.judgment)

    assert not ok, "%s (target %s) was unexpectedly ACCEPTED" % (fixture_name, target)
    assert issues, "%s (target %s) was rejected with no recorded reason (wrong-reason / empty issues)" % (fixture_name, target)


def test_every_v12_check_id_referenced_by_a_fixture_is_a_real_contract_v12_function():
    for check_id in set(negative_fixtures.FIXTURE_TARGET_CHECK_V12.values()):
        if check_id in ("judgment_hash_binding", "lifecycle", "synchronization_contract_representation"):
            assert hasattr(contract_v12, check_id)
            continue
        assert callable(getattr(contract_v12, check_id, None)), check_id
