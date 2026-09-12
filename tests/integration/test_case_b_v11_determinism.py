"""Translation determinism, run explicitly for Case B v1.1 (runbook item 4) --
not reused from the historical Case B's determinism evidence.

This test re-executes the real 31-run-per-case matrix (10 repeat, 10
row_shuffle, 5 key_shuffle, 3 locale, 3 timezone) via
experiments.run_determinism_case_b_v11, the same building blocks the
historical experiments/run_determinism.py uses, retargeted at Case B v1.1.
"""

from __future__ import annotations

from experiments.run_determinism_case_b_v11 import run


def test_case_a_and_case_b_v11_determinism_is_1_0_over_62_runs():
    summary = run()
    assert summary["TD"]["value"] == 1.0
    assert summary["total_runs"] == 62
    assert summary["matches"] == 62
    assert summary["per_case"]["case_a"]["reference_hash"] == (
        "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536"
    )
    assert summary["per_case"]["case_a"]["TD"]["value"] == 1.0
    assert summary["per_case"]["case_a"]["runs"] == 31
    assert summary["per_case"]["case_b_v1_1"]["reference_hash"] == (
        "0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1"
    )
    assert summary["per_case"]["case_b_v1_1"]["TD"]["value"] == 1.0
    assert summary["per_case"]["case_b_v1_1"]["runs"] == 31
    assert summary["failures"] == []
