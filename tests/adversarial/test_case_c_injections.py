"""Case C injection scenarios E1-E12 (development-generation; see
docs/CASE_C_STATUS.md). Wires experiments/case_c_injection_scenarios.py into
pytest so it runs as part of the ordinary suite rather than only via manual
invocation."""

from __future__ import annotations

from experiments.case_c_injection_scenarios import run


def test_all_case_c_injection_scenarios_pass(case_c):
    _, _, result = case_c
    report = run(result.bundle)
    failed = [r for r in report["scenarios"] if not r["passed"]]
    assert failed == [], failed
    assert report["scenario_count"] == 13  # 12 injections + clean control
    assert report["passed"] == 13
