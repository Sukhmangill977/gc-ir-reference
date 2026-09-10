"""Negative fixtures for Q1-Q10 audit query testing.

These are deliberately malformed bundles that violate each query requirement.
Used to verify that queries correctly detect violations.

Q7: Runtime ACS compilation coverage - missing predicate for runtime ACS
Q8: Gate/predicate reference integrity - reference to non-existent predicate
Q9: Actuation authority validity - producer not in authority matrix
Q10: Mandatory predicate evidence integrity - decisive gate without fail-closed
"""

from __future__ import annotations
from typing import Dict, Any
import copy


def create_negative_fixture_q7_missing_predicate(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: runtime ACS without corresponding risk-derived predicate.

    Creates a scenario where dispositions declares a runtime ACS that does not
    compile to any predicate.
    """
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    # Add a fake ACS to first runtime disposition without adding a predicate
    if payload.get("dispositions"):
        for disp in payload["dispositions"]:
            if disp.get("disposition_status") == "runtime":
                # Append a fake ACS that won't have a matching predicate
                fake_acs = {
                    "acs_id": "ACS-MISSING-Q7",
                    "risk_id": "MISSING-RISK",
                    "control_text": "This ACS has no compiled predicate"
                }
                if "approved_controls" not in disp:
                    disp["approved_controls"] = []
                disp["approved_controls"].append(fake_acs)
                break

    return bundle


def create_negative_fixture_q8_missing_predicate_reference(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: gate-map references non-existent predicate.

    The gate_map references a GCIR-ID that doesn't exist in predicates.
    """
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    # Add a fake entry to gate_map that references no predicate
    if "gate_map" not in payload:
        payload["gate_map"] = {}

    payload["gate_map"]["GCIR-MISSING-Q8"] = {
        "gate_type": "mandatory",
        "gate_source": "C_STAR"
    }

    return bundle


def create_negative_fixture_q8_unused_decisive_predicate(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: decisive predicate not included in gate_map.

    A predicate with mandatory_role='decisive' is missing from gate_map.
    """
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    # Add a predicate with decisive role
    fake_pred = {
        "gcir_id": "GCIR-DECISIVE-UNUSED",
        "mandatory_role": "decisive",
        "gate_type": "mandatory",
        "acs_id": "ACS-Q8",
        "origin_type": "risk_derived",
        "context_conditions": [{"on_unknown": "fail"}],
        "evidence_producer": "test_producer",
    }

    if "predicates" not in payload:
        payload["predicates"] = []
    payload["predicates"].append(fake_pred)

    # But don't add it to gate_map - this violates Q8

    return bundle


def create_negative_fixture_q9_invalid_producer(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: predicate references evidence producer not in authority matrix.

    A predicate references an evidence_producer that is not declared in the
    authority_matrix.
    """
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    # Add a predicate with non-existent producer
    fake_pred = {
        "gcir_id": "GCIR-BAD-PRODUCER",
        "mandatory_role": "supporting",
        "gate_type": "advisory",
        "acs_id": "ACS-Q9",
        "origin_type": "risk_derived",
        "context_conditions": [{"on_unknown": "warn"}],
        "evidence_producer": "NONEXISTENT_PRODUCER_XYZ",  # Not in authority
    }

    if "predicates" not in payload:
        payload["predicates"] = []
    payload["predicates"].append(fake_pred)

    return bundle


def create_negative_fixture_q10_decisive_not_fail_closed(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: decisive gate without fail-closed behavior.

    A predicate with mandatory_role='decisive' has a context condition with
    on_unknown != 'fail', violating fail-closed requirement.
    """
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    # Add a predicate with decisive but not fail-closed
    fake_pred = {
        "gcir_id": "GCIR-NOT-FAIL-CLOSED",
        "mandatory_role": "decisive",
        "gate_type": "mandatory",
        "acs_id": "ACS-Q10",
        "origin_type": "risk_derived",
        "context_conditions": [
            {
                "on_unknown": "warn"  # VIOLATION: should be "fail" for decisive
            }
        ],
        "evidence_producer": "test_producer",
    }

    if "predicates" not in payload:
        payload["predicates"] = []
    payload["predicates"].append(fake_pred)

    # Also add to gate_map so Q8 doesn't fail
    if "gate_map" not in payload:
        payload["gate_map"] = {}
    payload["gate_map"]["GCIR-NOT-FAIL-CLOSED"] = {
        "gate_type": "mandatory",
        "gate_source": "C_STAR"
    }

    return bundle


# Additional fixtures for edge cases

def create_negative_fixture_q7_compiler_invariant_only(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: runtime ACS with only compiler-invariant predicate (no risk-derived).

    The ACS compiles only to INV-* predicates, not to risk-derived ones.
    """
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    # Add runtime ACS
    if payload.get("dispositions"):
        for disp in payload["dispositions"]:
            if disp.get("disposition_status") == "runtime":
                fake_acs = {
                    "acs_id": "ACS-INV-ONLY-Q7",
                    "risk_id": "RISK-INV",
                    "control_text": "Compiles only to invariant, not risk-derived"
                }
                if "approved_controls" not in disp:
                    disp["approved_controls"] = []
                disp["approved_controls"].append(fake_acs)
                break

    # Add only an invariant predicate
    inv_pred = {
        "gcir_id": "GCIR-INV-ONLY",
        "acs_id": "ACS-INV-ONLY-Q7",
        "origin_type": "compiler_invariant",  # Not risk_derived!
        "mandatory_role": "supporting",
        "gate_type": "mandatory",
        "context_conditions": [{"on_unknown": "fail"}],
        "evidence_producer": "test",
    }

    if "predicates" not in payload:
        payload["predicates"] = []
    payload["predicates"].append(inv_pred)

    return bundle


def create_negative_fixture_q10_multiple_fail_closed_violations(base_bundle: Dict[str, Any]) -> Dict[str, Any]:
    """Fixture: multiple context conditions on a decisive gate, some not fail-closed."""
    bundle = copy.deepcopy(base_bundle)
    payload = bundle.get("payload", {})

    bad_pred = {
        "gcir_id": "GCIR-MULTI-NOT-CLOSED",
        "mandatory_role": "decisive",
        "gate_type": "mandatory",
        "acs_id": "ACS-Q10-MULTI",
        "origin_type": "risk_derived",
        "context_conditions": [
            {"on_unknown": "fail"},    # OK
            {"on_unknown": "warn"},    # VIOLATION
            {"on_unknown": "pass_with_approved_exception"},  # VIOLATION
        ],
        "evidence_producer": "test",
    }

    if "predicates" not in payload:
        payload["predicates"] = []
    payload["predicates"].append(bad_pred)

    if "gate_map" not in payload:
        payload["gate_map"] = {}
    payload["gate_map"]["GCIR-MULTI-NOT-CLOSED"] = {
        "gate_type": "mandatory",
        "gate_source": "C_STAR"
    }

    return bundle


def get_negative_fixtures(base_bundle: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Create all 10 negative fixtures (multiple per query where applicable).

    Returns: {fixture_name: bundle_with_violation}
    """
    return {
        # Q7: Runtime ACS compilation coverage
        "negative_q7_missing_predicate": create_negative_fixture_q7_missing_predicate(base_bundle),
        "negative_q7_compiler_invariant_only": create_negative_fixture_q7_compiler_invariant_only(base_bundle),

        # Q8: Gate/predicate reference integrity
        "negative_q8_missing_predicate_reference": create_negative_fixture_q8_missing_predicate_reference(base_bundle),
        "negative_q8_unused_decisive_predicate": create_negative_fixture_q8_unused_decisive_predicate(base_bundle),

        # Q9: Actuation authority validity
        "negative_q9_invalid_producer": create_negative_fixture_q9_invalid_producer(base_bundle),

        # Q10: Mandatory predicate evidence integrity
        "negative_q10_not_fail_closed": create_negative_fixture_q10_decisive_not_fail_closed(base_bundle),
        "negative_q10_multiple_violations": create_negative_fixture_q10_multiple_fail_closed_violations(base_bundle),

        # Additional edge cases
        "negative_q7_missing_predicate_alt": create_negative_fixture_q7_missing_predicate(base_bundle),
        "negative_q8_unused_decisive_alt": create_negative_fixture_q8_unused_decisive_predicate(base_bundle),
        "negative_q10_not_fail_closed_alt": create_negative_fixture_q10_decisive_not_fail_closed(base_bundle),
    }
