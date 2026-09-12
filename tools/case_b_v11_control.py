"""Case B v1.1: nine Approved Control Specifications.

See docs/CASE_B_V1_1_RATIONALE.md for the full per-record provenance table.
Summary: B-01 compiles from three ACS (permit+state-binding; prohibited-class
lookup; enhanced-approval concurrence), B-02 from two (hard ceiling; delegated
escalation), B-03..B-06 unchanged at one each -- nine total, matching
manuscript Section X / Table II's literal field-level specification, not an
arbitrary target count.

This is NOT the historical cases/case_b/ (six ACS, frozen, untouched). It is a
new, prospectively designed v1.1 artifact.
"""

from .case_b_data import (
    APPROVAL_TIME,
    APPROVER,
    BINDING,
    EFFECTIVE_FROM,
    FORUM,
    RELEASE,
    VALID_UNTIL,
)
from . import case_b_control as v10

OWNER_PAYMENTS = v10.OWNER_PAYMENTS
OWNER_SANCTIONS = v10.OWNER_SANCTIONS
OWNER_PLATFORM = v10.OWNER_PLATFORM
OWNER_RECORDS = v10.OWNER_RECORDS

VALIDITY = {"effective_from": EFFECTIVE_FROM, "effective_until": VALID_UNTIL}
RELEASE_PARAMS = dict(v10.RELEASE_PARAMS)

_RELEASE_TRIPLE = {
    "subject": ["transaction_agent"], "action": ["release_payment"],
    "resource": ["payment_instruction"], "destination": ["payment_rail"],
}


def _catalog_entry(event_type, template_id, observable_class, producers, operators,
                    value_schema, basis, schema_id, fields, notes=""):
    return {
        "event_type": event_type, "template_id": template_id,
        "observable_class": observable_class, "allowed_producers": producers,
        "triple_template": _RELEASE_TRIPLE, "allowed_operators": operators,
        "value_schema": value_schema, "evaluation_basis": basis,
        "evidence_schema": {"schema_id": schema_id, "fields": fields},
        "permitted_responses": ["SAFE_STATE"], "notes": notes,
    }


#: v1.0's six catalog entries, plus three new ones for ACS-B01-02, ACS-B01-03,
#: and ACS-B02-02 (schema v1.1 -- human_attestation + concurrence_policy did
#: not exist for ACS-B01-03/B02-02 to select before this generation).
CATALOG_ENTRIES = list(v10.CATALOG_ENTRIES) + [
    _catalog_entry(
        "prohibited_class_lookup", "T-PROHIBITED-CLASS", "risk_classification_state",
        ["risk_classification_service_v1"], ["!="], {"type": "string"},
        "deterministic_lookup", "ES-PROHIBITED-CLASS",
        ["transaction_hash", "risk_class", "policy_version", "artifact_signature"],
        "Section X ACS-B01-02: a signed active-policy lookup reporting the transaction's risk_class, independent of permit-binding evidence.",
    ),
    _catalog_entry(
        "enhanced_approval_check", "T-ENHANCED-APPROVAL", "enhanced_approval_state",
        ["compliance_approval_registry_v1"], ["=="], {"type": "boolean"},
        "human_attestation", "ES-ENHANCED-APPROVAL",
        ["transaction_hash", "risk_class", "approver_id", "approval_count"],
        "Section X ACS-B01-03: human-attested enhanced approval, required only where risk_class == ENHANCED_APPROVAL_REQUIRED.",
    ),
    _catalog_entry(
        "escalation_tier_check", "T-ESCALATION-TIER", "escalation_tier_state",
        ["escalation_approval_service_v1"], ["=="], {"type": "boolean"},
        "human_attestation", "ES-ESCALATION-TIER",
        ["transaction_hash", "amount_minor_units", "ordinary_limit", "additional_approval_established"],
        "Table II ACS-B02-02: amount <= ordinary_limit OR additional_approval_established, reported as one attested boolean by the escalation-approval service.",
    ),
]

CATALOG = {
    "catalog_id": "K-CASE-B-V1.1", "version": "1.0", "version_binding_ref": BINDING,
    "approved_by": FORUM, "approval_time": APPROVAL_TIME, "entries": CATALOG_ENTRIES,
}

THRESHOLD_CONTRACTS = dict(v10.THRESHOLD_CONTRACTS)
THRESHOLD_CONTRACTS["TC-ESCALATION-LIMIT"] = {
    "contract_id": "TC-ESCALATION-LIMIT",
    "operational_definition": "Ordinary (non-escalated) release limit below the absolute ceiling: the instruction amount, in minor units, releasable without additional approval.",
    "numerator": "instruction amount in minor units as carried on the signed payment-instruction artifact",
    "denominator": "one transaction; not a rate",
    "evidence_source": "payment_instruction_service_v1 signed instruction artifact",
    "ground_truth": "the instruction amount as recorded by the originating system at instruction creation",
    "threshold_rationale": "The Payment Authorization Limit Standard sets the ordinary (non-escalated) release band at CAD 100,000.00 (10,000,000 minor units); amounts between this and the absolute ceiling require the delegated escalation tier (ACS-B02-02).",
    "uncertainty_method": "Amounts are exact integers in minor units; no measurement uncertainty.",
    "unit": "minor currency units (CAD cents)",
    "reproduction_procedure": "Re-request the signed instruction artifact and compare amount_minor_units against the approved ordinary-limit bound for its currency.",
    "proposed_by": OWNER_PAYMENTS, "approved_by": FORUM, "approval_time": APPROVAL_TIME,
    "value": 10000000,
    "zero_event_reporting": "Not applicable: this is a per-transaction bound, not a rate.",
}


def _acs(acs_id, gcir_id, risk_id, obligations, event_type, template_id,
         observable_id, observable_class, producer, evidence_schema_ref,
         operator, expected, basis, escalation_route, escalation_sla,
         evidence_reqs, conditions, owner, evidence_semantics, decision_semantics,
         warrant_boundary, threshold_contract_ref=None, policy_id=None, v11=None):
    record = {
        "acs_id": acs_id, "gcir_id": gcir_id, "risk_id": risk_id, "obligation_refs": obligations,
        "event_type": event_type, "template_id": template_id,
        "observable_id": observable_id, "observable_class": observable_class,
        "observable_producer": producer,
        "evidence_source": "%s signed artifact bound to the transaction hash" % producer,
        "evidence_schema_ref": evidence_schema_ref,
        "subject": RELEASE["subject"], "action": RELEASE["action"],
        "resource": RELEASE["resource"], "destination": RELEASE["destination"],
        "action_parameters": dict(RELEASE_PARAMS),
        "parameter_schema_ref": "PS-RELEASE-PAYMENT",
        "operator": operator, "expected_value": expected, "temporal_window": None,
        "evaluation_basis": basis, "threshold_contract_ref": threshold_contract_ref,
        "on_unknown": "fail", "on_fail": "SAFE_STATE",
        "gate_candidate": "mandatory", "mandatory_role": "decisive",
        "escalation": {"route": escalation_route, "sla_hours": escalation_sla},
        "evidence_requirements": evidence_reqs, "context_conditions": conditions,
        "control_owner": owner, "approver": APPROVER, "approval_time": APPROVAL_TIME,
        "validity_interval": dict(VALIDITY), "version_binding_ref": BINDING,
        "evidence_semantics": evidence_semantics, "decision_semantics": decision_semantics,
        "warrant_boundary": warrant_boundary, "policy_id": policy_id,
    }
    if v11:
        record.update(v11)
    return record


def _cond(attribute, operator, value, producer, schema_ref, unit=None, contract=None):
    return {
        "attribute": attribute, "operator": operator, "value": value, "unit": unit,
        "on_unknown": "fail", "required": True, "evidence_producer": producer,
        "evidence_schema_ref": schema_ref, "threshold_contract_ref": contract,
        "temporal_window": None,
    }


def build_acs_records():
    return [
        # --- B-01: three records (Section X, Table II) ---------------------
        _acs(
            "ACS-B01-01", "GCIR-B0001", "B-01", ["INT-PERMIT-BIND"],
            "permit_binding", "T-PERMIT-BIND",
            "permit_valid_and_bound", "permit_binding_state",
            "authority_permit_service_v2", "ES-PERMIT-BIND",
            "==", True, "structural_check", "payment_operations_urgent", 1,
            ["transaction_hash", "permit_id", "permit_signature", "bound_hash"],
            [_cond("permit_valid_and_bound", "==", True, "authority_permit_service_v2", "ES-PERMIT-BIND")],
            OWNER_PLATFORM,
            "A signed permit artifact whose payload binds the permit identifier to this transaction hash.",
            "PERMIT requires a valid permit signature whose bound hash equals the transaction hash under evaluation; indeterminate or absent evidence fails.",
            "Establishes that a valid, bound permit exists. It does not establish that the authorization decision behind the permit was substantively correct.",
            policy_id="POL-B-PERMIT",
            v11={"enforcement_phase": "PRE_AUTHORIZATION",
                 "state_binding": {"attributes": ["transaction_hash", "amount", "beneficiary", "account_status", "token_status"]}},
        ),
        _acs(
            "ACS-B01-02", "GCIR-B0002", "B-01", ["INT-PERMIT-BIND"],
            "prohibited_class_lookup", "T-PROHIBITED-CLASS",
            "risk_class_not_prohibited", "risk_classification_state",
            "risk_classification_service_v1", "ES-PROHIBITED-CLASS",
            "!=", "PROHIBITED", "deterministic_lookup", "payment_operations_urgent", 1,
            ["transaction_hash", "risk_class", "policy_version", "artifact_signature"],
            [_cond("risk_class", "!=", "PROHIBITED", "risk_classification_service_v1", "ES-PROHIBITED-CLASS")],
            OWNER_PAYMENTS,
            "A signed active-policy classification artifact reporting the transaction's risk_class, evaluated independently of the permit-binding artifact.",
            "PERMIT requires risk_class != PROHIBITED under the active classification policy; indeterminate or absent evidence is HOLD (escalation route declared), never a silent pass.",
            "Establishes the transaction's classified risk is not a known-prohibited class. It does not establish the classification service resolves every case correctly.",
            policy_id="POL-B-PROHIBITED-CLASS",
        ),
        _acs(
            "ACS-B01-03", "GCIR-B0003", "B-01", ["INT-PERMIT-BIND"],
            "enhanced_approval_check", "T-ENHANCED-APPROVAL",
            "enhanced_approval_present", "enhanced_approval_state",
            "compliance_approval_registry_v1", "ES-ENHANCED-APPROVAL",
            "==", True, "human_attestation", "verification_workflow", 4,
            ["transaction_hash", "risk_class", "approver_id", "approval_count"],
            [_cond("enhanced_approval_present", "==", True, "compliance_approval_registry_v1", "ES-ENHANCED-APPROVAL")],
            OWNER_PAYMENTS,
            "A signed compliance-registry artifact reporting whether the required enhanced approval was attested, only where risk_class == ENHANCED_APPROVAL_REQUIRED.",
            "PERMIT requires enhanced_approval_present == true when required; pending or unavailable evidence is HOLD, routed to the verification workflow; an expired concurrence window is DENY.",
            "Establishes a human enhanced-approval attestation exists where required. It does not establish the reviewer's judgment was substantively correct.",
            policy_id="POL-B-ENHANCED-APPROVAL",
            v11={"enforcement_phase": "PRE_AUTHORIZATION",
                 "concurrence_policy": {"n_required": 1, "m_eligible": ["compliance.enhanced_approval_officer"],
                                         "window_seconds": 14400, "expiry_response": "DENY"}},
        ),

        # --- B-02: two records (Table II) -----------------------------------
        _acs(
            "ACS-B02-01", "GCIR-B0004", "B-02", ["INT-PAY-LIMIT"],
            "amount_limit", "T-AMOUNT-LIMIT",
            "amount_minor_units", "instruction_amount_measurement",
            "payment_instruction_service_v1", "ES-AMOUNT",
            "<=", 25000000, "threshold_on_measured_value", "payment_operations_urgent", 2,
            ["transaction_hash", "amount_minor_units", "currency", "artifact_signature"],
            [_cond("amount_minor_units", "<=", 25000000, "payment_instruction_service_v1", "ES-AMOUNT",
                   unit="minor currency units (CAD cents)", contract="TC-PAYMENT-LIMIT")],
            OWNER_PAYMENTS,
            "A signed instruction artifact carrying the amount in minor units and the currency code.",
            "PERMIT requires amount_minor_units <= the absolute authority ceiling under TC-PAYMENT-LIMIT; indeterminate or absent evidence fails. This is an unconditional ceiling with no escalation route.",
            "Establishes the instruction is within the absolute release ceiling. It does not establish the payment is legitimate.",
            threshold_contract_ref="TC-PAYMENT-LIMIT", policy_id="POL-B-LIMIT",
            v11={"enforcement_phase": "PRE_AUTHORIZATION",
                 "evaluation_latency_bound": {"value": 250, "unit": "ms"}, "on_evaluation_timeout": "HOLD"},
        ),
        _acs(
            "ACS-B02-02", "GCIR-B0005", "B-02", ["INT-PAY-LIMIT"],
            "escalation_tier_check", "T-ESCALATION-TIER",
            "escalation_tier_satisfied", "escalation_tier_state",
            "escalation_approval_service_v1", "ES-ESCALATION-TIER",
            "==", True, "human_attestation", "payment_operations_urgent", 4,
            ["transaction_hash", "amount_minor_units", "ordinary_limit", "additional_approval_established"],
            [_cond("escalation_tier_satisfied", "==", True, "escalation_approval_service_v1", "ES-ESCALATION-TIER")],
            OWNER_PAYMENTS,
            "A signed escalation-approval artifact attesting that amount <= the ordinary limit (TC-ESCALATION-LIMIT), or that additional delegated approval was established for amounts above it.",
            "PERMIT requires amount within the ordinary limit or an established additional approval; pending/unavailable approval is HOLD; a denied or window-expired approval is DENY.",
            "Establishes the delegated escalation tier's condition is satisfied. It does not establish the additional approver's judgment was substantively correct.",
            threshold_contract_ref="TC-ESCALATION-LIMIT", policy_id="POL-B-ESCALATION",
            v11={"enforcement_phase": "PRE_AUTHORIZATION",
                 "concurrence_policy": {"n_required": 1, "m_eligible": ["business.head_payment_operations"],
                                         "window_seconds": 14400, "expiry_response": "DENY"}},
        ),

        # --- B-03..B-06: unchanged from the historical six-ACS design ------
        _acs(
            "ACS-B03-01", "GCIR-B0006", "B-03", ["INT-PAY-LIMIT"],
            "velocity_bound", "T-VELOCITY",
            "window_transaction_count", "window_transaction_count",
            "velocity_counter_service_v1", "ES-VELOCITY",
            "<=", 20, "threshold_on_measured_value", "payment_operations_urgent", 2,
            ["transaction_hash", "window_count", "window_seconds", "counterparty_id", "artifact_signature"],
            [_cond("window_transaction_count", "<=", 20, "velocity_counter_service_v1", "ES-VELOCITY",
                   unit="transactions per counterparty per 3600 s", contract="TC-VELOCITY-BOUND")],
            OWNER_PAYMENTS,
            "A signed window-count artifact reporting committed releases to the same counterparty inside the approved rolling window.",
            "PERMIT requires window_transaction_count <= the approved bound under TC-VELOCITY-BOUND; indeterminate or absent evidence fails.",
            "Establishes that observed velocity is within the approved bound. It does not establish that a within-bound pattern is legitimate.",
            threshold_contract_ref="TC-VELOCITY-BOUND", policy_id="POL-B-LIMIT",
            v11={"enforcement_phase": "BOUNDARY_REVALIDATION",
                 "evaluation_latency_bound": {"value": 500, "unit": "ms"}, "on_evaluation_timeout": "HOLD"},
        ),
        _acs(
            "ACS-B04-01", "GCIR-B0007", "B-04", ["SEMA-SANCTIONS", "PCMLTFA-REPORT"],
            "restricted_party_screening", "T-RESTRICTED-PARTY",
            "restricted_party_match", "restricted_party_match",
            "sanctions_screening_service_v5", "ES-RESTRICTED-PARTY",
            "==", False, "deterministic_lookup", "sanctions_desk_urgent", 1,
            ["transaction_hash", "counterparty_id", "list_version", "match_count", "artifact_signature"],
            [_cond("restricted_party_match", "==", False, "sanctions_screening_service_v5", "ES-RESTRICTED-PARTY")],
            OWNER_SANCTIONS,
            "A SIGNED screening artifact reporting whether the counterparty matches the restricted-party list at a stated list version.",
            "PERMIT requires restricted_party_match == false. Missing, stale or schema-invalid evidence is indeterminacy and fails; escalation is raised on failure.",
            "Establishes that the signed screening artifact reports no match at the stated list version. It does NOT establish that the screening service resolves every alias, transliteration or ownership chain correctly.",
            policy_id="POL-B-SANCTIONS",
            v11={"enforcement_phase": "PRE_AUTHORIZATION"},
        ),
        _acs(
            "ACS-B05-01", "GCIR-B0008", "B-05", ["INT-PERMIT-BIND"],
            "permit_single_use", "T-SINGLE-USE",
            "permit_unredeemed_and_hash_novel", "permit_and_hash_novelty",
            "authority_permit_service_v2", "ES-SINGLE-USE",
            "==", True, "structural_check", "payment_operations_urgent", 1,
            ["transaction_hash", "permit_id", "permit_previously_redeemed", "hash_previously_seen"],
            [_cond("permit_unredeemed_and_hash_novel", "==", True, "authority_permit_service_v2", "ES-SINGLE-USE")],
            OWNER_PLATFORM,
            "A signed redemption-state artifact reporting whether this permit has already been redeemed and whether this transaction hash has already been seen.",
            "PERMIT requires the permit to be unredeemed and the transaction hash to be novel; indeterminate or absent evidence fails.",
            "Establishes single-use semantics over the permit and hash. It does not establish that two economically identical instructions with different hashes are not duplicates.",
            policy_id="POL-B-PERMIT",
            v11={"enforcement_phase": "PRE_AUTHORIZATION", "state_binding": {"attributes": ["transaction_hash"]}},
        ),
        _acs(
            "ACS-B06-01", "GCIR-B0009", "B-06", ["INT-EVID-CHAIN-B", "PCMLTFA-REPORT"],
            "receipt_chain_completeness", "T-RECEIPT-CHAIN-B",
            "receipt_committed_between_authorization_and_actuation", "receipt_chain_state",
            "evidence_chain_service_v2", "ES-RECEIPT-CHAIN",
            "==", True, "structural_check", "compliance_records_urgent", 1,
            ["receipt_id", "authorization_time", "evidence_commit_time", "actuation_time", "chain_prev_hash"],
            [_cond("receipt_committed_between_authorization_and_actuation", "==", True, "evidence_chain_service_v2", "ES-RECEIPT-CHAIN")],
            OWNER_RECORDS,
            "A signed evidence-chain artifact carrying the authorization, commit and actuation instants for this decision, and the chain link to its predecessor.",
            "PERMIT requires authorization_time <= evidence_commit_time < actuation_time with a verified chain link; indeterminate or absent evidence fails.",
            "Establishes the temporal ordering and chaining of the evidence record. It coincides with compiler invariant INV-EVIDENCE-COMMIT.",
            policy_id="POL-B-EVIDENCE",
            v11={"enforcement_phase": "POST_AUTH_PRE_ACTUATION",
                 "evaluation_latency_bound": {"value": 100, "unit": "ms"}, "on_evaluation_timeout": "HOLD"},
        ),
    ]


#: Disposition acs_ids per risk -- unchanged risk cardinality (6 dispositions),
#: several risks now naming more than one acs_id (Section IV-D: "Predicate
#: cardinality remains independent of risk cardinality").
RUNTIME_ACS = {
    "B-01": ["ACS-B01-01", "ACS-B01-02", "ACS-B01-03"],
    "B-02": ["ACS-B02-01", "ACS-B02-02"],
    "B-03": ["ACS-B03-01"],
    "B-04": ["ACS-B04-01"],
    "B-05": ["ACS-B05-01"],
    "B-06": ["ACS-B06-01"],
}


def build_dispositions():
    return [
        {"risk_id": rid, "status": "runtime", "acs_ids": list(RUNTIME_ACS[rid])}
        for rid in sorted(RUNTIME_ACS)
    ]


_SELECTION_RATIONALE_B = {
    "ACS-B01-01": "Permit validity and binding is a structural check over a signed artifact; T-PERMIT-BIND is the approved template. Enriched at schema v1.1 with state_binding over the five-attribute transaction tuple Table II names.",
    "ACS-B01-02": "New at schema v1.1, per Section X's explicit ACS-B01-02 specification: a deterministic-lookup prohibited-class check, kept structurally distinct from permit-binding evidence so a known prohibition DENYs independently of permit state.",
    "ACS-B01-03": "New at schema v1.1, per Section X's explicit ACS-B01-03 specification: human-attested enhanced approval with a concurrence_policy, unrepresentable before schema v1.1 added that mechanism.",
    "ACS-B02-01": "The instruction amount is a measured value requiring a threshold contract; T-AMOUNT-LIMIT selected with TC-PAYMENT-LIMIT as the absolute ceiling. Unconditional DENY on breach -- no escalation route.",
    "ACS-B02-02": "New at schema v1.1, per Table II's explicit ACS-B02-02 specification: the delegated escalation tier for amounts between the ordinary limit and the absolute ceiling, via human_attestation + concurrence_policy.",
    "ACS-B03-01": "Window transaction count is a measured value requiring a threshold contract; T-VELOCITY selected with TC-VELOCITY-BOUND.",
    "ACS-B04-01": "Restricted-party screening resolves to a signed artifact; T-RESTRICTED-PARTY is the approved deterministic-lookup template. Selected by class, not by score.",
    "ACS-B05-01": "Permit redemption state and hash novelty are structural; T-SINGLE-USE selected. state_binding over transaction_hash added at schema v1.1.",
    "ACS-B06-01": "Receipt ordering and chaining are structural; T-RECEIPT-CHAIN-B selected. enforcement_phase = POST_AUTH_PRE_ACTUATION at schema v1.1, matching its coincidence with INV-EVIDENCE-COMMIT.",
}

SELECTORS_B = {
    "ACS-B04-01": "compliance.head_sanctions",
    "ACS-B06-01": "compliance.head_records",
    "ACS-B01-02": "compliance.head_sanctions",
    "ACS-B01-03": "compliance.enhanced_approval_officer",
    "ACS-B02-02": "business.head_payment_operations",
}
DEFAULT_SELECTOR_B = "business.head_payment_operations"


def build_judgment_record(acs_records):
    selections, approvals, decisions = [], [], []
    for index, acs in enumerate(acs_records, start=1):
        selector = SELECTORS_B.get(acs["acs_id"], DEFAULT_SELECTOR_B)
        selections.append({
            "selection_id": "JB11-SEL-%03d" % index, "risk_id": acs["risk_id"],
            "acs_id": acs["acs_id"], "event_type": acs["event_type"], "template_id": acs["template_id"],
            "selected_by": selector, "selection_time": "2026-02-15T10:00:00Z",
            "rationale": _SELECTION_RATIONALE_B[acs["acs_id"]],
        })
        approvals.append({"acs_id": acs["acs_id"], "approver": APPROVER, "approval_time": APPROVAL_TIME, "forum": FORUM})
        decisions.append({
            "risk_id": acs["risk_id"], "status": "runtime", "decided_by": selector,
            "decision_time": "2026-02-15T10:00:00Z",
            "rationale": "The risk has an approved catalog observable evaluable at authorization time on the sole authorized external action path.",
        })
    # One decision entry per risk (not per ACS) -- de-duplicate.
    seen = set()
    unique_decisions = []
    for d in decisions:
        if d["risk_id"] in seen:
            continue
        seen.add(d["risk_id"])
        unique_decisions.append(d)
    unique_decisions.sort(key=lambda d: d["risk_id"])
    return {
        "judgment_id": "J-CASE-B-V1.1", "version": "1.1",
        "assessment_ref": {"assessment_id": "ASSESSMENT-CASE-B", "binding_id": BINDING},
        "catalog_ref": {"catalog_id": "K-CASE-B-V1.1", "version": "1.0"},
        "selections": selections, "disposition_decisions": unique_decisions, "approvals": approvals,
    }


CSTAR_PROFILE = dict(v10.CSTAR_PROFILE)
POLICY_METADATA = dict(v10.POLICY_METADATA, bundle_id="BUNDLE-CASE-B-V1.1")
