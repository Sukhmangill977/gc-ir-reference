"""Negative fixtures for canonical Q1-Q10, built from a real compiled bundle.

Every fixture below starts from an actual ``CompiledBundle`` (the output of
``gcir.compiler.compile_bundle`` against a committed case tree, e.g.
``tests/unit/test_core.py``'s ``case_a_bundle`` fixture) and mutates a deep
copy of its real payload to violate exactly one query.  This replaces an
earlier version of this module whose fixtures were built from an invented
shape (``disposition_status``, ``approved_controls``) that the compiler has
never emitted -- those fixtures could not have exercised the real queries
because no real bundle ever has that shape.  Every fixture here returns a
``CompiledBundle`` with a genuinely mutated ``payload``, so
``gcir.audit_queries.run_all_audit_queries`` sees exactly what it would see in
production.

Because the mutation deliberately breaks structural invariants the compiler
itself enforces, the returned bundle's ``payload_hash`` is left equal to the
*original* (pre-mutation) hash unless the fixture is specifically testing hash
integrity (Q4, Q6) -- a stale hash is not the point of a Q1/Q2/Q3/Q5/Q7-Q10
fixture and would only obscure which query is under test.
"""

from __future__ import annotations

import copy
from typing import Callable, Dict

from .models import CompiledBundle


def _mutated(bundle: CompiledBundle, mutate: Callable[[dict], None]) -> CompiledBundle:
    payload = copy.deepcopy(bundle.payload)
    mutate(payload)
    return CompiledBundle(
        payload=payload,
        payload_hash=bundle.payload_hash,
        envelope=copy.deepcopy(bundle.envelope),
        warnings=list(bundle.warnings),
    )


# ---------------------------------------------------------------------------
# Q1: obligation disposition completeness
# ---------------------------------------------------------------------------


def create_negative_fixture_q1_undisposed_obligation(bundle: CompiledBundle) -> CompiledBundle:
    """An obligation the coverage matrix still lists as undisposed."""
    def mutate(payload):
        obligations = payload["coverage_matrix"]["obligations"]
        if not obligations:
            raise ValueError("bundle has no obligations to mutate for the Q1 fixture")
        obligations[0]["disposed"] = False
        obligations[0]["disposition_statuses"] = []

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q2: exactly-one disposition per risk
# ---------------------------------------------------------------------------


def create_negative_fixture_q2_duplicate_disposition(bundle: CompiledBundle) -> CompiledBundle:
    """A risk with two disposition records instead of exactly one."""
    def mutate(payload):
        dispositions = payload["dispositions"]
        if not dispositions:
            raise ValueError("bundle has no dispositions to mutate for the Q2 fixture")
        duplicate = copy.deepcopy(dispositions[0])
        dispositions.append(duplicate)

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q3: predicate origin closure
# ---------------------------------------------------------------------------


def create_negative_fixture_q3_acs_id_not_disposed(bundle: CompiledBundle) -> CompiledBundle:
    """A risk-derived predicate cites an acs_id its risk's disposition never
    approved -- an executable control with no surviving authorized origin."""
    def mutate(payload):
        for predicate in payload["predicates"]:
            if predicate["origin"]["origin_type"] == "risk_derived":
                predicate["acs_id"] = "ACS-NEVER-DISPOSED-%s" % predicate["gcir_id"]
                return
        raise ValueError("bundle has no risk-derived predicate to mutate for the Q3 fixture")

    return _mutated(bundle, mutate)


def create_negative_fixture_q3_unknown_origin_type(bundle: CompiledBundle) -> CompiledBundle:
    """A predicate whose origin_type is outside {risk_derived, compiler_invariant}."""
    def mutate(payload):
        if not payload["predicates"]:
            raise ValueError("bundle has no predicates to mutate for the Q3 fixture")
        payload["predicates"][0]["origin"]["origin_type"] = "heuristic_match"

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q4: temporal bundle validity
# ---------------------------------------------------------------------------


def create_negative_fixture_q4_invalid_hash(bundle: CompiledBundle) -> CompiledBundle:
    """A payload_hash that is not 64 lowercase hex characters."""
    payload = copy.deepcopy(bundle.payload)
    return CompiledBundle(payload=payload, payload_hash="not-a-real-hash", envelope=copy.deepcopy(bundle.envelope))


def create_negative_fixture_q4_stale_hash(bundle: CompiledBundle) -> CompiledBundle:
    """A well-formed hash that no longer matches the (mutated) payload."""
    def mutate(payload):
        payload["bundle_id"] = payload["bundle_id"] + "-MUTATED-AFTER-HASH"

    return _mutated(bundle, mutate)  # payload_hash intentionally stays the *original* hash


def create_negative_fixture_q4_invalid_effective_from(bundle: CompiledBundle) -> CompiledBundle:
    """A validity.effective_from that is not RFC 3339 UTC (a local offset)."""
    def mutate(payload):
        payload["validity"]["effective_from"] = "2026-01-01T00:00:00-05:00"

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q5: commit-before-actuation ordering (compile-time precondition)
# ---------------------------------------------------------------------------


def create_negative_fixture_q5_timeout_response_not_hold(bundle: CompiledBundle) -> CompiledBundle:
    """A predicate declares evaluation_latency_bound but on_evaluation_timeout
    is not HOLD -- the compiler itself would reject this (Appendix A
    constraint 15); the fixture exercises Q5 as a post-hoc auditor of a bundle
    that reached the evidence store through a channel other than this Phi."""
    def mutate(payload):
        if not payload["predicates"]:
            raise ValueError("bundle has no predicates to mutate for the Q5 fixture")
        predicate = payload["predicates"][0]
        predicate["evaluation_latency_bound"] = {"value": 250, "unit": "ms"}
        predicate["on_evaluation_timeout"] = "fail"  # violation: must be HOLD

    return _mutated(bundle, mutate)


def create_negative_fixture_q5_permit_eligibility_mismatch(bundle: CompiledBundle) -> CompiledBundle:
    """gate_map.permit_eligible disagrees with the predicate's declared
    enforcement_phase."""
    def mutate(payload):
        if not payload["predicates"]:
            raise ValueError("bundle has no predicates to mutate for the Q5 fixture")
        gcir_id = payload["predicates"][0]["gcir_id"]
        payload["predicates"][0]["enforcement_phase"] = "POST_AUTH_PRE_ACTUATION"
        # Deliberately leave gate_map's permit_eligible as it was (True for an
        # ordinary risk-derived predicate) -- now inconsistent with the phase.
        payload["gate_map"][gcir_id]["permit_eligible"] = True

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q6: lifecycle signing authority
# ---------------------------------------------------------------------------


def create_negative_fixture_q6_missing_envelope(bundle: CompiledBundle) -> CompiledBundle:
    """A bundle with no signature envelope at all."""
    payload = copy.deepcopy(bundle.payload)
    return CompiledBundle(payload=payload, payload_hash=bundle.payload_hash, envelope=None)


def create_negative_fixture_q6_envelope_hash_mismatch(bundle: CompiledBundle) -> CompiledBundle:
    """A signature envelope whose payload_hash does not match the bundle's."""
    payload = copy.deepcopy(bundle.payload)
    envelope = copy.deepcopy(bundle.envelope) or {
        "algorithm": "Ed25519", "domain": "bundle", "key_id": "key.test",
        "signature_b64": "AA==",
    }
    envelope["payload_hash"] = "0" * 64
    return CompiledBundle(payload=payload, payload_hash=bundle.payload_hash, envelope=envelope)


# ---------------------------------------------------------------------------
# Q7: runtime ACS compilation coverage
# ---------------------------------------------------------------------------


def create_negative_fixture_q7_missing_predicate(bundle: CompiledBundle) -> CompiledBundle:
    """A RuntimeDisposition names an ACS with no compiled predicate at all."""
    def mutate(payload):
        for disp in payload["dispositions"]:
            if disp.get("record_type") == "RuntimeDisposition":
                disp["acs_ids"] = list(disp["acs_ids"]) + ["ACS-MISSING-Q7"]
                return
        raise ValueError("bundle has no RuntimeDisposition to mutate for the Q7 fixture")

    return _mutated(bundle, mutate)


def create_negative_fixture_q7_compiler_invariant_only(bundle: CompiledBundle) -> CompiledBundle:
    """An ACS whose only compiled predicate is (falsely) marked as a compiler
    invariant rather than risk-derived -- exercising the case where a runtime
    ACS's predicate technically exists but not as risk-derived evidence."""
    def mutate(payload):
        for predicate in payload["predicates"]:
            if predicate["origin"]["origin_type"] == "risk_derived":
                predicate["origin"]["origin_type"] = "compiler_invariant"
                predicate["origin"]["origin_id"] = "INV-RELABELED"
                return
        raise ValueError("bundle has no risk-derived predicate to relabel for the Q7 fixture")

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q8: gate/predicate reference integrity
# ---------------------------------------------------------------------------


def create_negative_fixture_q8_missing_predicate_reference(bundle: CompiledBundle) -> CompiledBundle:
    """gate_map references a gcir_id with no compiled predicate."""
    def mutate(payload):
        payload["gate_map"]["GCIR-MISSING-Q8"] = {
            "gate_type": "mandatory", "gate_source": "OTHER_MANDATORY",
            "mandatory_role": "decisive", "permit_eligible": True,
        }

    return _mutated(bundle, mutate)


def create_negative_fixture_q8_unused_decisive_predicate(bundle: CompiledBundle) -> CompiledBundle:
    """A decisive predicate absent from gate_map."""
    def mutate(payload):
        if not payload["predicates"]:
            raise ValueError("bundle has no predicates to clone for the Q8 fixture")
        clone = copy.deepcopy(payload["predicates"][0])
        clone["gcir_id"] = clone["gcir_id"] + "-Q8-UNUSED"
        clone["mandatory_role"] = "decisive"
        payload["predicates"].append(clone)
        # Deliberately never add clone["gcir_id"] to gate_map.

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q9: actuation authority validity
# ---------------------------------------------------------------------------


def create_negative_fixture_q9_invalid_producer(bundle: CompiledBundle) -> CompiledBundle:
    """A predicate's evidence_producer is not an allowed producer for its
    catalog event_type (or, without a catalog supplied, is empty)."""
    def mutate(payload):
        if not payload["predicates"]:
            raise ValueError("bundle has no predicates to mutate for the Q9 fixture")
        payload["predicates"][0]["evidence_producer"] = "unauthorized_producer_xyz"

    return _mutated(bundle, mutate)


def create_negative_fixture_q9_empty_producer(bundle: CompiledBundle) -> CompiledBundle:
    """A predicate declares no evidence_producer at all (fallback-check case)."""
    def mutate(payload):
        if not payload["predicates"]:
            raise ValueError("bundle has no predicates to mutate for the Q9 fixture")
        payload["predicates"][0]["evidence_producer"] = ""

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------
# Q10: mandatory predicate evidence integrity
# ---------------------------------------------------------------------------


def create_negative_fixture_q10_decisive_not_fail_closed(bundle: CompiledBundle) -> CompiledBundle:
    """A decisive predicate with a condition whose on_unknown != fail."""
    def mutate(payload):
        for predicate in payload["predicates"]:
            if predicate.get("mandatory_role") == "decisive" and predicate["context_conditions"]:
                predicate["context_conditions"][0]["on_unknown"] = "warn"
                return
        raise ValueError("bundle has no decisive predicate to mutate for the Q10 fixture")

    return _mutated(bundle, mutate)


def create_negative_fixture_q10_multiple_violations(bundle: CompiledBundle) -> CompiledBundle:
    """A decisive predicate with several conditions, more than one violating
    fail-closed on_unknown."""
    def mutate(payload):
        for predicate in payload["predicates"]:
            if predicate.get("mandatory_role") == "decisive":
                base = copy.deepcopy(predicate["context_conditions"][0])
                extra1 = dict(base, attribute=base["attribute"] + "_extra1", on_unknown="warn")
                extra2 = dict(base, attribute=base["attribute"] + "_extra2", on_unknown="pass_with_approved_exception")
                predicate["context_conditions"].extend([extra1, extra2])
                return
        raise ValueError("bundle has no decisive predicate to mutate for the Q10 fixture")

    return _mutated(bundle, mutate)


# ---------------------------------------------------------------------------


def get_negative_fixtures(bundle: CompiledBundle) -> Dict[str, CompiledBundle]:
    """Every negative fixture, keyed by name, built from one real compiled
    bundle.  Exactly one fixture per query except where a query has more than
    one genuinely distinct violation mode worth testing separately (Q3, Q4,
    Q5, Q9 each have two)."""
    return {
        "negative_q1_undisposed_obligation": create_negative_fixture_q1_undisposed_obligation(bundle),
        "negative_q2_duplicate_disposition": create_negative_fixture_q2_duplicate_disposition(bundle),
        "negative_q3_acs_id_not_disposed": create_negative_fixture_q3_acs_id_not_disposed(bundle),
        "negative_q3_unknown_origin_type": create_negative_fixture_q3_unknown_origin_type(bundle),
        "negative_q4_invalid_hash": create_negative_fixture_q4_invalid_hash(bundle),
        "negative_q4_stale_hash": create_negative_fixture_q4_stale_hash(bundle),
        "negative_q4_invalid_effective_from": create_negative_fixture_q4_invalid_effective_from(bundle),
        "negative_q5_timeout_response_not_hold": create_negative_fixture_q5_timeout_response_not_hold(bundle),
        "negative_q5_permit_eligibility_mismatch": create_negative_fixture_q5_permit_eligibility_mismatch(bundle),
        "negative_q6_missing_envelope": create_negative_fixture_q6_missing_envelope(bundle),
        "negative_q6_envelope_hash_mismatch": create_negative_fixture_q6_envelope_hash_mismatch(bundle),
        "negative_q7_missing_predicate": create_negative_fixture_q7_missing_predicate(bundle),
        "negative_q7_compiler_invariant_only": create_negative_fixture_q7_compiler_invariant_only(bundle),
        "negative_q8_missing_predicate_reference": create_negative_fixture_q8_missing_predicate_reference(bundle),
        "negative_q8_unused_decisive_predicate": create_negative_fixture_q8_unused_decisive_predicate(bundle),
        "negative_q9_invalid_producer": create_negative_fixture_q9_invalid_producer(bundle),
        "negative_q9_empty_producer": create_negative_fixture_q9_empty_producer(bundle),
        "negative_q10_not_fail_closed": create_negative_fixture_q10_decisive_not_fail_closed(bundle),
        "negative_q10_multiple_violations": create_negative_fixture_q10_multiple_violations(bundle),
    }


#: Which query each fixture must cause to fail (used by the test suite to
#: assert targeted, not incidental, detection).
FIXTURE_TARGET_QUERY = {
    "negative_q1_undisposed_obligation": "Q1",
    "negative_q2_duplicate_disposition": "Q2",
    "negative_q3_acs_id_not_disposed": "Q3",
    "negative_q3_unknown_origin_type": "Q3",
    "negative_q4_invalid_hash": "Q4",
    "negative_q4_stale_hash": "Q4",
    "negative_q4_invalid_effective_from": "Q4",
    "negative_q5_timeout_response_not_hold": "Q5",
    "negative_q5_permit_eligibility_mismatch": "Q5",
    "negative_q6_missing_envelope": "Q6",
    "negative_q6_envelope_hash_mismatch": "Q6",
    "negative_q7_missing_predicate": "Q7",
    "negative_q7_compiler_invariant_only": "Q7",
    "negative_q8_missing_predicate_reference": "Q8",
    "negative_q8_unused_decisive_predicate": "Q8",
    "negative_q9_invalid_producer": "Q9",
    "negative_q9_empty_producer": "Q9",
    "negative_q10_not_fail_closed": "Q10",
    "negative_q10_multiple_violations": "Q10",
}
