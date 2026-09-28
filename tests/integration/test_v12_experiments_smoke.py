"""Fast regression smoke tests for the remaining Paper 2 v1.2 development
experiments (spec sections 13, 14). The 93-run determinism harness
(experiments.run_determinism_v12), the K=250000 Monte Carlo regression
(experiments.monte_carlo_regression_v12), and the 100-run compile-timing
harness (experiments.compile_timing_v12) are deliberately NOT run inside
pytest -q -- they are the standalone, longer-running experiment invocations
spec section 16's own command list shows separately, exactly like their
v1.0/v1.1 counterparts (experiments.run_determinism,
experiments.run_monte_carlo) are not run inside pytest -q either.

Development-generation artifact; not part of any frozen preregister-tier0
campaign.
"""

from __future__ import annotations

from experiments import case_b_integration_regression_v12, observation_diagnostics_v12


def test_observation_diagnostics_a_and_b_both_pass():
    report = observation_diagnostics_v12.run_all()
    assert report["diagnostic_a"]["passed"]
    assert report["diagnostic_b"]["passed"]
    assert report["diagnostic_a"]["claim_boundary"] == "Bounded software-simulation diagnostic. Not deployment validation."
    assert report["diagnostic_b"]["claim_boundary"] == "Bounded software-simulation diagnostic. Not deployment validation."


def test_case_b_integration_regression_is_fourteen_rows_all_passing():
    report = case_b_integration_regression_v12.run()
    assert report["row_count"] == 14
    assert report["failed"] == 0
    assert report["passed"] == 14
    assert report["not_new_translation_fidelity_evidence"] is True
