"""pytest view of the adversarial corpus.

The corpus itself lives in ``experiments/adversarial_cases.py`` so that the test
suite and ``experiments/run_adversarial.py`` cannot drift apart: there is exactly
one definition of what was tested and what each case expects.
"""

import pytest

from experiments import adversarial_cases
from experiments.run_adversarial import (
    run_corpus,
    run_structural_checks,
    run_validation_seeds,
)

CORPUS = {row["id"]: row for row in run_corpus()}
STRUCTURAL = run_structural_checks()
SEEDS = {seed["seed_id"]: seed for seed in run_validation_seeds()}


@pytest.mark.parametrize("case_id", sorted(CORPUS))
def test_adversarial_case(case_id):
    row = CORPUS[case_id]
    assert row["outcome"] == "PASS", (
        "%s (%s): expected %s %s, observed schema=%r compiler=%r -- %s"
        % (case_id, row["name"], row["expects"], row["expected_code"],
           row["schema_code"], row["compiler_code"], row["detail"][:300])
    )


def test_corpus_covers_every_manuscript_failure_class():
    """Section XI-H enumerates the failure classes the suite must cover."""
    names = " ".join(
        "%s %s %s" % (entry["name"], entry["manuscript_ref"], entry["description"])
        for entry in adversarial_cases.all_cases()
    ).lower()
    names += " " + " ".join(check["check"] for check in STRUCTURAL).lower()
    required = [
        "malformed", "duplicate", "unresolved", "conflict", "expired", "stale",
        "producer", "materiality", "outside s.authority_matrix", "threshold contract",
        "on_unknown", "coverage", "signature", "version binding",
    ]
    missing = [term for term in required if term not in names]
    assert not missing, "adversarial corpus lacks a case for: %s" % missing


def test_corpus_contains_positive_controls():
    """A suite that only ever expects rejection cannot distinguish a correct
    compiler from one that rejects everything."""
    positive = [e for e in adversarial_cases.all_cases() if e["expects"] == "compile"]
    assert len(positive) >= 5


@pytest.mark.parametrize(
    "index", range(len(STRUCTURAL)), ids=[c["check"] + ":" + c["case"] for c in STRUCTURAL]
)
def test_structural_check(index):
    check = STRUCTURAL[index]
    assert check["passed"], "%s/%s: %s" % (check["case"], check["check"], check["detail"])


@pytest.mark.parametrize("seed_id", sorted(SEEDS))
def test_validation_seed(seed_id):
    """Section IX: 'WC-01 and RC-05 handling are exercised in the machine-readable
    artifact's deliberately seeded validation rows.'"""
    seed = SEEDS[seed_id]
    assert seed["outcome"] == "PASS", "%s: %s" % (seed_id, seed["detail"])
