"""Unit tests for the individually-named manuscript requirements."""

from __future__ import annotations

import copy
import json
import os

import pytest

from gcir.canonicalization import hash_payload
from gcir.models import (
    CSTAR_BASE_PROFILE_V1,
    EVALUATION_BASES,
    GATE_SOURCES,
    GATE_TYPES,
    REASON_CODES,
    RESERVED_UNUSED_REASON_CODES,
    WARNING_CODES,
    ValidationError,
)


# ---------------------------------------------------------------------------
# Closed vocabularies (Sections III, IV-D, V, VI-B, VII-A)
# ---------------------------------------------------------------------------


def test_reason_codes_are_closed_at_v1_and_match_the_manuscript():
    """Section V names RC-01, RC-02, RC-03 and RC-05. RC-04 is not defined by the
    manuscript and must not be invented."""
    assert sorted(REASON_CODES) == ["RC-01", "RC-02", "RC-03", "RC-05"]
    assert REASON_CODES["RC-01"] == "no per-action observable"
    assert REASON_CODES["RC-02"] == "no authority-matrix action"
    assert REASON_CODES["RC-03"] == "requires probabilistic judgment"
    assert REASON_CODES["RC-05"] == "consequence class undefined"
    assert RESERVED_UNUSED_REASON_CODES == ("RC-04",)
    assert "RC-04" not in REASON_CODES


def test_wc01_is_a_warning_code_not_a_reason_code():
    """'An unresolved reference is not simultaneously a successful compilation
    and a rejection, so it is a warning, not a disposition.'"""
    assert sorted(WARNING_CODES) == ["WC-01"]
    assert "WC-01" not in REASON_CODES


def test_evaluation_basis_is_the_closed_set_of_four():
    assert EVALUATION_BASES == (
        "deterministic_lookup",
        "threshold_on_measured_value",
        "structural_check",
        "human_attestation",
    )


def test_gate_vocabularies():
    assert GATE_TYPES == ("mandatory", "weighted", "advisory")
    assert GATE_SOURCES == ("C_STAR", "OTHER_MANDATORY", "SOFT")


def test_c_star_base_profile_is_the_four_manuscript_kinds():
    assert CSTAR_BASE_PROFILE_V1 == (
        "material_statutory_prohibition",
        "unauthorized_authority_exercise",
        "material_information_barrier_breach",
        "irreversible_external_effect_above_approved_bound",
    )


def test_case_profiles_are_the_base_profile(any_case):
    _, inputs, _ = any_case
    assert inputs.cstar_profile.is_base_profile_v1()


# ---------------------------------------------------------------------------
# C* materiality qualification (Section VII-A)
# ---------------------------------------------------------------------------


def test_materiality_qualifies_c_star_membership(case_a):
    """'A documentation defect or other immaterial technical non-conformance does
    not enter C* solely because its source is statutory.'"""
    _, inputs, _ = case_a
    profile = inputs.cstar_profile

    material = {"kind": "material_statutory_prohibition", "materiality": "material",
                "reversibility": "irreversible", "authority": "a"}
    immaterial = dict(material, materiality="immaterial")
    minor = dict(material, materiality="minor")

    assert profile.evaluate(material) == 1
    assert profile.evaluate(immaterial) == 0
    assert profile.evaluate(minor) == 0
    assert profile.evaluate(None) == 0
    assert profile.evaluate({"kind": "client_harm", "materiality": "severe",
                             "reversibility": "irreversible", "authority": "a"}) == 0


def test_unknown_materiality_is_rejected_not_silently_treated_as_low(case_a):
    _, inputs, _ = case_a
    with pytest.raises(ValidationError) as excinfo:
        inputs.cstar_profile.evaluate(
            {"kind": "material_statutory_prohibition", "materiality": "quite_bad",
             "reversibility": "irreversible", "authority": "a"}
        )
    assert excinfo.value.code == "MATERIALITY_UNKNOWN"


# ---------------------------------------------------------------------------
# Catalog resolution is exact (Section IV-B, Appendix B)
# ---------------------------------------------------------------------------


def test_catalog_lookup_is_exact_and_has_no_fallback(case_a):
    from gcir.models import CatalogResolutionError

    case, inputs, _ = case_a
    catalog = inputs.catalog
    entry = catalog.entries[0]

    assert catalog.exact_lookup(entry["event_type"], entry["template_id"]) is entry

    # A near miss on either key resolves to nothing -- no best-match fallback.
    with pytest.raises(CatalogResolutionError):
        catalog.exact_lookup(entry["event_type"], entry["template_id"] + "-V2")
    with pytest.raises(CatalogResolutionError):
        catalog.exact_lookup(entry["event_type"].upper(), entry["template_id"])
    with pytest.raises(CatalogResolutionError):
        catalog.exact_lookup(entry["event_type"][:-1], entry["template_id"])


# ---------------------------------------------------------------------------
# Payload purity and signature envelope separation (Section VI-C, VI-F)
# ---------------------------------------------------------------------------


def test_payload_carries_no_timestamp_nonce_or_lifecycle_field(any_case):
    from gcir.validation import constraint_13_payload_is_hash_clean

    _, _, result = any_case
    assert constraint_13_payload_is_hash_clean(result.bundle.payload)


def test_signature_envelope_lives_outside_the_hashed_payload(any_case):
    from gcir.compiler import sign_bundle

    case, _, result = any_case
    bundle = result.bundle
    before = bundle.payload_hash
    sign_bundle(bundle, case.keyring, case.parameters["bundle_signing_key"],
                signing_time="2026-02-02T09:05:00Z")
    assert "signature" not in bundle.payload
    assert bundle.envelope["signing_time"] == "2026-02-02T09:05:00Z"
    assert hash_payload(bundle.payload) == before


def test_two_signings_differ_in_envelope_but_not_in_payload_hash(any_case):
    """Section VI-C: 'the signature envelope ... is not required to be
    byte-identical across signing events'."""
    case, _, result = any_case
    payload = result.bundle.payload
    key_id = case.parameters["bundle_signing_key"]
    first = case.keyring.sign(payload, key_id, domain="bundle",
                              signing_time="2026-02-02T09:05:00Z")
    second = case.keyring.sign(payload, key_id, domain="bundle",
                               signing_time="2026-03-09T17:41:00Z")
    assert first["signing_time"] != second["signing_time"]
    assert first != second
    assert first["payload_hash"] == second["payload_hash"] == result.bundle.payload_hash


def test_compiled_predicate_validity_carries_effective_from_only(any_case):
    """Appendix A: 'version and validity bindings (effective_from only --
    lifecycle state is external per Section VI-F)'."""
    _, _, result = any_case
    for predicate in result.bundle.predicates:
        assert set(predicate["validity"]) == {"effective_from"}


# ---------------------------------------------------------------------------
# Totality is about dispositions, not predicate counts (Section VI-E)
# ---------------------------------------------------------------------------


def test_totality_is_asserted_over_dispositions_not_predicate_cardinality(case_a):
    """'It shall not assert |P| + |X| = |R|, because one risk may lawfully produce
    multiple predicates.'"""
    _, inputs, result = case_a
    risks = len(inputs.assessment.risk_register)
    dispositions = len(result.bundle.dispositions)
    predicates = len(result.bundle.predicates)

    assert dispositions == risks
    assert predicates != risks  # 19 predicates for 16 risks -- and that is lawful

    risk_derived = [p for p in result.bundle.predicates
                    if p["origin"]["origin_type"] == "risk_derived"]
    per_risk = {}
    for predicate in risk_derived:
        per_risk.setdefault(predicate["origin"]["origin_id"], []).append(predicate)
    assert max(len(v) for v in per_risk.values()) >= 2, "expected a risk with several predicates"
    nonruntime = [d for d in result.bundle.dispositions
                  if d["record_type"] == "NonRuntimeDisposition"]
    assert nonruntime, "expected a risk with zero predicates"


def test_non_runtime_records_need_no_action_or_gate_fields(case_a):
    """Appendix A: a non-runtime record 'shall not be required to contain subject,
    action, resource, evaluation basis, or gate type'."""
    _, _, result = case_a
    nonruntime = [d for d in result.bundle.dispositions
                  if d["record_type"] == "NonRuntimeDisposition"]
    assert nonruntime
    for record in nonruntime:
        for absent in ("subject", "action", "resource", "evaluation_basis", "gate_type"):
            assert absent not in record
        for present in ("risk_id", "reason_code", "routed_to_control_family",
                        "control_ref", "owner", "approval"):
            assert present in record


# ---------------------------------------------------------------------------
# Origins (Section VI-B)
# ---------------------------------------------------------------------------


def test_every_predicate_has_an_authorized_origin(any_case):
    _, inputs, result = any_case
    risk_ids = set(inputs.assessment.risk_index)
    invariant_ids = {inv["invariant_id"] for inv in inputs.invariants}
    for predicate in result.bundle.predicates:
        origin = predicate["origin"]
        if origin["origin_type"] == "risk_derived":
            assert origin["origin_id"] in risk_ids
            assert predicate["acs_id"]
        else:
            assert origin["origin_type"] == "compiler_invariant"
            assert origin["origin_id"] in invariant_ids


def test_the_three_manuscript_invariants_are_present(any_case):
    _, inputs, result = any_case
    ids = {inv["invariant_id"] for inv in inputs.invariants}
    assert ids == {"INV-VERSION", "INV-EVIDENCE-COMMIT", "INV-AUTHORITY-CLOSURE"}
    emitted = {p["origin"]["origin_id"] for p in result.bundle.predicates
               if p["origin"]["origin_type"] == "compiler_invariant"}
    assert emitted == ids


def test_register_row_and_coinciding_invariant_keep_distinct_origins(case_a):
    """Section IX R-11 note: 'Origin metadata keeps the two authorizations
    distinct (risk_derived citing R-11; compiler_invariant citing INV-VERSION).'"""
    _, _, result = case_a
    from_risk = [p for p in result.bundle.predicates
                 if p["origin"]["origin_id"] == "R-11"]
    from_invariant = [p for p in result.bundle.predicates
                      if p["origin"]["origin_id"] == "INV-VERSION"]
    assert len(from_risk) == 1
    assert len(from_invariant) == 1
    assert from_risk[0]["gcir_id"] != from_invariant[0]["gcir_id"]
    assert from_risk[0]["origin"]["origin_type"] == "risk_derived"
    assert from_invariant[0]["origin"]["origin_type"] == "compiler_invariant"


# ---------------------------------------------------------------------------
# Mandatory gates and unknown handling
# ---------------------------------------------------------------------------


def test_every_mandatory_gate_fails_closed_on_unknown(any_case):
    _, _, result = any_case
    for predicate in result.bundle.predicates:
        if predicate["gate_type"] != "mandatory":
            continue
        assert predicate["on_fail"] == "SAFE_STATE"
        for condition in predicate["context_conditions"]:
            if condition.get("required", True):
                assert condition["on_unknown"] == "fail"


def test_non_mandatory_conditions_may_warn_on_unknown(case_a):
    _, _, result = case_a
    soft = [p for p in result.bundle.predicates if p["gate_type"] != "mandatory"]
    assert soft
    assert any(c["on_unknown"] == "warn" for p in soft for c in p["context_conditions"])


# ---------------------------------------------------------------------------
# Threshold contracts (Section V commitment 4)
# ---------------------------------------------------------------------------


REQUIRED_CONTRACT_FIELDS = (
    "operational_definition", "numerator", "denominator", "evidence_source",
    "ground_truth", "threshold_rationale", "uncertainty_method", "unit",
    "reproduction_procedure",
)


def test_every_numeric_condition_carries_a_complete_threshold_contract(any_case):
    from gcir.models import NUMERIC_TEMPORAL_OPERATORS

    _, inputs, result = any_case
    contracts = inputs.threshold_contracts
    seen = 0
    for predicate in result.bundle.predicates:
        for condition in predicate["context_conditions"]:
            if condition["operator"] not in NUMERIC_TEMPORAL_OPERATORS:
                continue
            seen += 1
            ref = condition["threshold_contract_ref"]
            assert ref, predicate["gcir_id"]
            contract = contracts[ref]
            for field in REQUIRED_CONTRACT_FIELDS:
                assert contract[field], (ref, field)
            assert condition["unit"]
    assert seen >= 1


def test_threshold_authority_is_separated_from_evaluation(any_case):
    """'Control owners propose thresholds with rationale, the accountable
    governance forum approves them, and the runtime evaluator never sets or
    adjusts them.'"""
    _, inputs, _ = any_case
    for contract in inputs.threshold_contracts.values():
        assert contract["proposed_by"] != contract["approved_by"]
        assert "forum" in contract["approved_by"]


# ---------------------------------------------------------------------------
# Weighted aggregation (Section V commitment 3)
# ---------------------------------------------------------------------------


def test_weighted_predicates_carry_a_complete_aggregation_block(case_a):
    _, _, result = case_a
    weighted = [p for p in result.bundle.predicates if p["gate_type"] == "weighted"]
    assert weighted, "Case A R-04 should yield a weighted predicate"
    for predicate in weighted:
        aggregation = predicate["aggregation"]
        assert aggregation["aggregation_group"]
        assert aggregation["weight"] > 0
        assert aggregation["deficit_function"]
        assert "group_threshold" in aggregation
        assert aggregation["response"]


# ---------------------------------------------------------------------------
# Precedence (Section VI-D)
# ---------------------------------------------------------------------------


def test_mandatory_failure_outranks_everything(case_a):
    from gcir.precedence import resolve

    _, _, result = case_a
    bundle = result.bundle
    outcomes = {p["gcir_id"]: "pass" for p in bundle.predicates}
    verdict = resolve(bundle, outcomes)
    assert verdict["decision"] == "PERMIT"

    mandatory = next(p for p in bundle.predicates if p["gate_type"] == "mandatory")
    outcomes[mandatory["gcir_id"]] = "fail"
    verdict = resolve(bundle, outcomes)
    assert verdict["decision"] == "SAFE_STATE"
    assert verdict["deciding_class"] == "mandatory_failure"


def test_weighted_or_advisory_never_overrides_a_mandatory_pass(case_a):
    from gcir.precedence import resolve

    _, _, result = case_a
    bundle = result.bundle
    outcomes = {p["gcir_id"]: "pass" for p in bundle.predicates}
    for predicate in bundle.predicates:
        if predicate["gate_type"] != "mandatory":
            outcomes[predicate["gcir_id"]] = "fail"
    verdict = resolve(bundle, outcomes)
    assert verdict["decision"] == "PERMIT"


def test_unknown_evidence_on_a_mandatory_gate_produces_safe_state(case_a):
    from gcir.precedence import resolve

    _, _, result = case_a
    bundle = result.bundle
    outcomes = {p["gcir_id"]: "pass" for p in bundle.predicates}
    mandatory = next(p for p in bundle.predicates if p["gate_type"] == "mandatory")
    outcomes[mandatory["gcir_id"]] = "unknown"
    verdict = resolve(bundle, outcomes)
    assert verdict["decision"] == "SAFE_STATE"
    assert verdict["deciding_class"] == "mandatory_failure"


def test_conflicting_mandatory_policies_without_precedence_are_indeterminate(case_a):
    """Section VI-D: 'Conflicts among applicable mandatory policies are themselves
    indeterminate and produce SAFE_STATE unless a unique precedence relation is
    present in the approved policy metadata.'"""
    from gcir.models import CompiledBundle
    from gcir.precedence import resolve

    _, _, result = case_a
    payload = copy.deepcopy(result.bundle.payload)
    mandatory = [p for p in payload["predicates"] if p["gate_type"] == "mandatory"][:2]
    for predicate in mandatory:
        predicate["conflict_group"] = "CG-DISPUTED"
    bundle = CompiledBundle(payload=payload, payload_hash="unused")

    outcomes = {p["gcir_id"]: "pass" for p in payload["predicates"]}
    outcomes[mandatory[0]["gcir_id"]] = "fail"
    verdict = resolve(bundle, outcomes)
    assert verdict["decision"] == "SAFE_STATE"
    assert verdict["deciding_class"] == "indeterminate_mandatory_conflict"

    # With a unique precedence relation declared, it is no longer indeterminate.
    payload["policy_metadata"]["precedence"] = {
        "CG-DISPUTED": {"order": [p["gcir_id"] for p in mandatory]}
    }
    verdict = resolve(bundle, outcomes)
    assert verdict["decision"] == "SAFE_STATE"
    assert verdict["deciding_class"] == "mandatory_failure"


# ---------------------------------------------------------------------------
# Temporal ordering (Section VIII)
# ---------------------------------------------------------------------------


def test_commit_before_actuate_is_strict_on_the_second_inequality():
    from gcir.temporal import commit_before_actuate

    ok, _ = commit_before_actuate({
        "authorization_time": "2026-03-04T10:15:00Z",
        "evidence_commit_time": "2026-03-04T10:15:01Z",
        "actuation_time": "2026-03-04T10:15:02Z",
    })
    assert ok

    ok, reasons = commit_before_actuate({
        "authorization_time": "2026-03-04T10:15:00Z",
        "evidence_commit_time": "2026-03-04T10:15:02Z",
        "actuation_time": "2026-03-04T10:15:02Z",
    })
    assert not ok and "strictly before" in reasons[0]

    ok, reasons = commit_before_actuate({
        "authorization_time": "2026-03-04T10:15:03Z",
        "evidence_commit_time": "2026-03-04T10:15:01Z",
        "actuation_time": "2026-03-04T10:15:05Z",
    })
    assert not ok


def test_local_time_offsets_are_rejected():
    """Section VI-C forbids local-time dependence."""
    from gcir.temporal import parse_time

    parse_time("2026-03-04T10:15:00Z")
    for bad in ("2026-03-04T10:15:00+01:00", "2026-03-04 10:15:00Z",
                "2026-03-04T10:15:00", "04/03/2026"):
        with pytest.raises(ValidationError):
            parse_time(bad)


# ---------------------------------------------------------------------------
# Lifecycle and ValidAt (Sections VI-F, VIII) -- the six scenarios
# ---------------------------------------------------------------------------


def _lifecycle(case_id, repo_root):
    directory = os.path.join(repo_root, "cases", case_id, "lifecycle")
    with open(os.path.join(directory, "lifecycle_registry.json"), encoding="utf-8") as fh:
        registry = json.load(fh)
    with open(os.path.join(directory, "receipts.json"), encoding="utf-8") as fh:
        receipts = json.load(fh)["receipts"]
    with open(os.path.join(directory, "negative", "fixtures.json"), encoding="utf-8") as fh:
        negative = json.load(fh)
    return registry, receipts, negative


def test_valid_at_six_scenarios(case_a, repo_root):
    from gcir.lifecycle import LifecycleRegistry, valid_at

    case, _, result = case_a
    bundle = result.bundle
    registry_doc, receipts, negative = _lifecycle("case_a", repo_root)
    registry = LifecycleRegistry(registry_doc, keyring=case.keyring,
                                 authorized_key_ids=registry_doc["authorized_signing_keys"])

    # 1. A valid historical receipt.
    current = receipts[0]
    ok, reasons = valid_at(current, bundle, registry, keyring=case.keyring)
    assert ok, reasons

    # 2. A retired bundle used BEFORE retirement is still valid -- not drift.
    historical = receipts[1]
    ok, reasons = valid_at(historical, bundle, registry, keyring=case.keyring)
    assert ok, reasons

    # 3. A retired bundle used AFTER retirement is invalid.
    ok, reasons = valid_at(negative["q4_post_retirement_receipt"], bundle, registry,
                           keyring=case.keyring)
    assert not ok and any("retired" in r for r in reasons)

    # 4. Payload mutation breaks the hash binding.
    mutated = copy.deepcopy(bundle)
    mutated.payload = copy.deepcopy(bundle.payload)
    mutated.payload["predicates"][0]["gate_type"] = "advisory"
    ok, reasons = valid_at(current, mutated, registry, keyring=case.keyring)
    assert not ok and any("bundle_hash" in r for r in reasons)

    # 5. An invalidly signed registry record does not retire the bundle.
    rogue = copy.deepcopy(registry_doc)
    rogue["entries"] = [negative["q6_unauthorized_registry_entry"]]
    rogue_registry = LifecycleRegistry(rogue, keyring=case.keyring,
                                       authorized_key_ids=rogue["authorized_signing_keys"])
    assert not rogue_registry.is_retired(bundle.payload_hash, "2026-12-01T00:00:00Z")
    assert len(rogue_registry.invalid_authority_entries()) == 1

    # 6. A receipt citing the wrong bundle hash is invalid.
    ok, reasons = valid_at(negative["q4_wrong_bundle_hash_receipt"], bundle, registry,
                           keyring=case.keyring)
    assert not ok and any("bundle_hash" in r for r in reasons)


def test_lifecycle_actions_are_the_three_manuscript_actions(repo_root):
    from gcir.models import LIFECYCLE_ACTIONS

    assert LIFECYCLE_ACTIONS == ("retire", "supersede", "revoke")


def test_supersede_requires_a_successor_hash(case_a, repo_root):
    from gcir.lifecycle import LifecycleRegistry

    case, _, _ = case_a
    registry_doc, _, _ = _lifecycle("case_a", repo_root)
    broken = copy.deepcopy(registry_doc)
    broken["entries"][0]["action"] = "supersede"
    broken["entries"][0].pop("successor_hash", None)
    with pytest.raises(ValidationError) as excinfo:
        LifecycleRegistry(broken, keyring=case.keyring)
    assert excinfo.value.code == "LIFECYCLE_SUCCESSOR_MISSING"


# ---------------------------------------------------------------------------
# Signature domain separation
# ---------------------------------------------------------------------------


def test_a_bundle_signature_cannot_be_replayed_as_a_lifecycle_signature(case_a):
    from gcir.models import SignatureError

    case, _, result = case_a
    envelope = case.keyring.sign(result.bundle.payload,
                                 case.parameters["bundle_signing_key"],
                                 domain="bundle")
    with pytest.raises(SignatureError):
        case.keyring.verify(result.bundle.payload, envelope, domain="lifecycle")


def test_verification_detects_a_flipped_payload_bit(case_a):
    from gcir.models import SignatureError

    case, _, result = case_a
    envelope = case.keyring.sign(result.bundle.payload,
                                 case.parameters["bundle_signing_key"],
                                 domain="bundle")
    mutated = copy.deepcopy(result.bundle.payload)
    mutated["bundle_id"] = mutated["bundle_id"] + "x"
    with pytest.raises(SignatureError):
        case.keyring.verify(mutated, envelope, domain="bundle")
