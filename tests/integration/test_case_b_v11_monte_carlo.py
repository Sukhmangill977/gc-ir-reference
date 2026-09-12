"""Monte Carlo rating-robustness, run explicitly for Case A and Case B v1.1
(prospective v4, runbook item G) -- reproduced through the real compiled
bundles, not assumed unchanged from the historical figures. Case A is paired
in here (as run_determinism_case_b_v11.py already pairs it for determinism)
so a Case A drift -- forbidden under runbook item H, "Case A must not move"
-- would be caught by this test, not just cited from history."""

from __future__ import annotations

from experiments.run_monte_carlo_case_b_v11 import run


def test_case_a_and_case_b_v11_monte_carlo_reproduces_historical_figures():
    payload = run(draws=250000)

    case_a = payload["per_case"]["case_a"]
    assert case_a["max_FP_heat"]["risk_id"] == "R-06"
    assert abs(case_a["max_FP_heat"]["value"] - 0.321268) < 1e-6
    assert abs(case_a["max_FP_heat"]["mcse"] - 0.000934) < 1e-5
    assert case_a["max_FP_cstar"] == 0.0
    assert case_a["GD_approved"] == 3

    analysis = payload["per_case"]["case_b_v1_1"]
    assert analysis["max_FP_heat"]["risk_id"] == "B-01"
    assert abs(analysis["max_FP_heat"]["value"] - 0.317980) < 1e-6
    assert abs(analysis["max_FP_heat"]["mcse"] - 0.000931) < 1e-6
    assert analysis["max_FP_cstar"] == 0.0
    assert analysis["cstar_membership_changes_observed"] == 0
    assert analysis["GD_approved"] == 4
    assert analysis["GD_min_mean"] == 0.0
    assert payload["specification"]["seed"] == 20260201
    assert payload["specification"]["draws_K"] == 250000
