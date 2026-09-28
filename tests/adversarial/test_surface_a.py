"""Surface A: eight paired semantic families (Paper 2 v1.2 spec section 2).

Development-generation artifact; not part of any frozen preregister-tier0
campaign. Reruns experiments.surface_a_paired_validation and asserts the
spec section 3 target: 8/8 nominal accepted, 8/8 semantic negatives
rejected, 8/8 for the correct expected reason, 0 wrong-reason, 0
packaging-only, 0 unexpected accepts.
"""

from __future__ import annotations

import json

from experiments import surface_a_paired_validation as sa


def test_surface_a_hits_the_spec_section_3_target():
    report = sa.run_all()
    counts = report["counts"]
    failures = [row for row in report["families"] if not row["nominal_accepted"] or not row["negative_rejected"] or row["wrong_reason"]]
    assert not failures, "Surface A families failed: %s" % json.dumps(failures, indent=2, default=str)

    assert counts["nominal_accepted"] == "8/8"
    assert counts["semantic_negatives_rejected"] == "8/8"
    assert counts["correct_expected_reason"] == "8/8"
    assert counts["wrong_reason_rejects"] == 0
    assert counts["packaging_only_rejects"] == 0
    assert counts["unexpected_accepts"] == 0
    assert counts["stale_hash_only_rejects"] == 0


def test_every_family_recomputes_a_distinct_or_intentionally_identical_hash():
    """spec section 2: a rejection caused only by a stale hash/signature does
    not count. A6 (lifecycle) is the one family whose negative is a
    re-interpretation of the SAME compiled bundle (staleness is a property
    checked against a supplied 'current' version, not a payload mutation),
    so its hashes are intentionally identical; every other family's negative
    is a real semantic mutation with its own recomputed hash."""
    report = sa.run_all()
    for row in report["families"]:
        if row["family"] == "A6":
            assert row["nominal_payload_hash"] == row["negative_payload_hash"]
        else:
            assert row["nominal_payload_hash"] != row["negative_payload_hash"], row["family"]
