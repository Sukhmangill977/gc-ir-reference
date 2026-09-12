"""Case B v1.1 injection scenarios: 13/13 with the exact category outcome
asserted (authorization_decision, release_decision, next_authorization_effect)
-- runbook item 3/4, not merely non-externalization.

authorization_decision and release_decision are asserted as two independent
axes (item 7): BLOCK_RELEASE is tallied under release_decision_counts, never
folded into authorization_decision_counts as a fourth peer outcome.
"""

from __future__ import annotations

from gcir.models import safe_state_of
from experiments.case_b_v11_injection_scenarios import run


def test_all_thirteen_case_b_v11_injections_assert_exact_category_outcome(case_b_v1_1):
    _, _, result = case_b_v1_1
    report = run(result.bundle)
    failed = [r for r in report["scenarios"] if not r["passed"]]
    assert failed == [], failed
    assert report["scenario_count"] == 14  # 13 scenarios + clean control
    assert report["passed"] == 14
    assert report["zero_externalization"] is True


def test_authorization_and_release_axes_are_independent_and_sum_correctly(case_b_v1_1):
    _, _, result = case_b_v1_1
    report = run(result.bundle)

    auth = report["authorization_decision_counts"]
    rel = report["release_decision_counts"]
    assert auth == {"PERMIT": 1, "DENY": 8, "HOLD": 4}
    assert rel == {"ALLOW_RELEASE": 12, "BLOCK_RELEASE": 1}
    # Each axis independently sums to all 13 injection rows (clean_control excluded).
    assert sum(auth.values()) == 13
    assert sum(rel.values()) == 13
    # The one BLOCK_RELEASE row is also counted as PERMIT under authorization,
    # not as some fifth/fourth category -- exactly one row is both.
    permit_and_block = [
        r for r in report["scenarios"][:-1]
        if r["authorization_decision"] == "PERMIT" and r["release_decision"] == "BLOCK_RELEASE"
    ]
    assert len(permit_and_block) == 1
    assert permit_and_block[0]["scenario"] == "toctou"


def test_toctou_row_keeps_safe_state_false_despite_blocked_release(case_b_v1_1):
    """The runbook item 3 regression check, against the real injection
    harness output (not a synthetic fixture): a PERMIT authorization whose
    release is blocked must NOT report safe_state=True."""
    _, _, result = case_b_v1_1
    report = run(result.bundle)
    toctou = next(r for r in report["scenarios"] if r["scenario"] == "toctou")

    assert toctou["authorization_decision"] == "PERMIT"
    assert toctou["release_decision"] == "BLOCK_RELEASE"
    assert toctou["safe_state"] is False
    assert toctou["release_safe"] is True
    assert toctou["externalization_blocked"] is True
    assert toctou["externalization"] is False
    assert toctou["passed"] is True


def test_every_scenario_row_satisfies_safe_state_of_authorization_decision(case_b_v1_1):
    """No scenario -- including toctou -- may have safe_state disagree with
    models.safe_state_of(authorization_decision)."""
    _, _, result = case_b_v1_1
    report = run(result.bundle)
    for row in report["scenarios"]:
        assert row["safe_state"] == safe_state_of(row["authorization_decision"]), row
