"""Case B control layer: catalog K_B, threshold contracts, ACS set, judgment
record, dispositions, C* profile and policy metadata.

All six rows receive runtime dispositions with mandatory gates: four by C*, two
by other approved mandatory policy (manuscript Section X).
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

OWNER_PAYMENTS = "business.payment_operations"
OWNER_SANCTIONS = "compliance.sanctions_desk"
OWNER_PLATFORM = "technology.payments_platform"
OWNER_RECORDS = "compliance.records_desk"

VALIDITY = {"effective_from": EFFECTIVE_FROM, "effective_until": VALID_UNTIL}

_RELEASE_TRIPLE = {
    "subject": ["transaction_agent"],
    "action": ["release_payment"],
    "resource": ["payment_instruction"],
    "destination": ["payment_rail"],
}

RELEASE_PARAMS = {
    "transaction_hash": "TXN-BOUND",
    "currency": "CAD",
    "rail": "domestic_rtr",
}


def _entry(event_type, template_id, observable_class, producers, operators,
           value_schema, basis, schema_id, fields, responses, notes=""):
    return {
        "event_type": event_type,
        "template_id": template_id,
        "observable_class": observable_class,
        "allowed_producers": producers,
        "triple_template": _RELEASE_TRIPLE,
        "allowed_operators": operators,
        "value_schema": value_schema,
        "evaluation_basis": basis,
        "evidence_schema": {"schema_id": schema_id, "fields": fields},
        "permitted_responses": responses,
        "notes": notes,
    }


CATALOG_ENTRIES = [
    _entry(
        "permit_binding", "T-PERMIT-BIND", "permit_binding_state",
        ["authority_permit_service_v2"], ["=="], {"type": "boolean"},
        "structural_check", "ES-PERMIT-BIND",
        ["transaction_hash", "permit_id", "permit_signature", "bound_hash"],
        ["SAFE_STATE"],
    ),
    _entry(
        "amount_limit", "T-AMOUNT-LIMIT", "instruction_amount_measurement",
        ["payment_instruction_service_v1"], ["<="], {"type": "number"},
        "threshold_on_measured_value", "ES-AMOUNT",
        ["transaction_hash", "amount_minor_units", "currency"],
        ["SAFE_STATE"],
    ),
    _entry(
        "velocity_bound", "T-VELOCITY", "window_transaction_count",
        ["velocity_counter_service_v1"], ["<="], {"type": "number"},
        "threshold_on_measured_value", "ES-VELOCITY",
        ["transaction_hash", "window_count", "window_seconds", "counterparty_id"],
        ["SAFE_STATE"],
    ),
    _entry(
        "restricted_party_screening", "T-RESTRICTED-PARTY", "restricted_party_match",
        ["sanctions_screening_service_v5"], ["=="], {"type": "boolean"},
        "deterministic_lookup", "ES-RESTRICTED-PARTY",
        ["transaction_hash", "counterparty_id", "list_version", "match_count", "artifact_signature"],
        ["SAFE_STATE"],
        "The predicate deterministically verifies that a signed screening artifact "
        "reports no restricted-party match. It does not claim the screening "
        "service resolves every alias correctly.",
    ),
    _entry(
        "permit_single_use", "T-SINGLE-USE", "permit_and_hash_novelty",
        ["authority_permit_service_v2"], ["=="], {"type": "boolean"},
        "structural_check", "ES-SINGLE-USE",
        ["transaction_hash", "permit_id", "permit_previously_redeemed", "hash_previously_seen"],
        ["SAFE_STATE"],
    ),
    _entry(
        "receipt_chain_completeness", "T-RECEIPT-CHAIN-B", "receipt_chain_state",
        ["evidence_chain_service_v2"], ["=="], {"type": "boolean"},
        "structural_check", "ES-RECEIPT-CHAIN",
        ["receipt_id", "authorization_time", "evidence_commit_time", "actuation_time", "chain_prev_hash"],
        ["SAFE_STATE"],
    ),
]

CATALOG = {
    "catalog_id": "K-CASE-B",
    "version": "1.0",
    "version_binding_ref": BINDING,
    "approved_by": FORUM,
    "approval_time": APPROVAL_TIME,
    "entries": CATALOG_ENTRIES,
}

THRESHOLD_CONTRACTS = {
    "TC-PAYMENT-LIMIT": {
        "contract_id": "TC-PAYMENT-LIMIT",
        "operational_definition": "Per-transaction release limit: the instruction amount, in minor currency units, that a single automated authorization may release without human co-authorization.",
        "numerator": "instruction amount in minor units as carried on the signed payment-instruction artifact",
        "denominator": "one transaction; not a rate",
        "evidence_source": "payment_instruction_service_v1 signed instruction artifact",
        "ground_truth": "the instruction amount as recorded by the originating system at instruction creation, before the authorization path sees it",
        "threshold_rationale": "The Payment Authorization Limit Standard sets the automated release ceiling at CAD 250,000.00 (25,000,000 minor units), the board-approved single-transaction exposure bound for unattended release.",
        "uncertainty_method": "Amounts are exact integers in minor units; there is no measurement uncertainty. Currency conversion is out of scope -- the bound applies per currency and the artifact carries the currency code.",
        "unit": "minor currency units (CAD cents)",
        "reproduction_procedure": "Re-request the signed instruction artifact for the transaction hash and compare its amount_minor_units field against the approved bound for its currency.",
        "proposed_by": OWNER_PAYMENTS,
        "approved_by": FORUM,
        "approval_time": APPROVAL_TIME,
        "value": 25000000,
        "zero_event_reporting": "Not applicable: this is a per-transaction bound, not a rate.",
    },
    "TC-VELOCITY-BOUND": {
        "contract_id": "TC-VELOCITY-BOUND",
        "operational_definition": "Counterparty velocity bound: the number of releases to the same counterparty permitted within a rolling 3600-second window.",
        "numerator": "count of released transactions to the counterparty with actuation_time inside the window",
        "denominator": "one rolling 3600-second window per counterparty",
        "evidence_source": "velocity_counter_service_v1 signed window-count artifact",
        "ground_truth": "committed receipts in the evidence chain, not the authorization service's own in-memory state",
        "threshold_rationale": "The Payment Authorization Limit Standard sets 20 releases per counterparty per hour as the bound above which an upstream defect or compromise is more likely than legitimate activity, based on the 99.9th percentile of the counterparty-hour distribution over the preceding twelve months.",
        "uncertainty_method": "The count is exact given the window boundary; the reported uncertainty is the evidence-chain commit latency bound (<= 250 ms), which can move at most one transaction across a window edge. The artifact reports the boundary instants so the effect is auditable.",
        "unit": "transactions per counterparty per 3600 s",
        "reproduction_procedure": "Re-request the signed window-count artifact for the transaction hash and recount committed receipts for the counterparty inside the stated window boundaries.",
        "proposed_by": OWNER_PAYMENTS,
        "approved_by": FORUM,
        "approval_time": APPROVAL_TIME,
        "value": 20,
        "zero_event_reporting": "A window with zero releases is reported with its exposure denominator and an exact one-sided upper bound, never as 'no velocity risk'.",
    },
}


def _acs(acs_id, gcir_id, risk_id, obligations, event_type, template_id,
         observable_id, observable_class, producer, evidence_schema_ref,
         operator, expected, basis, escalation_route, escalation_sla,
         evidence_reqs, conditions, owner, evidence_semantics, decision_semantics,
         warrant_boundary, threshold_contract_ref=None, policy_id=None):
    return {
        "acs_id": acs_id,
        "gcir_id": gcir_id,
        "risk_id": risk_id,
        "obligation_refs": obligations,
        "event_type": event_type,
        "template_id": template_id,
        "observable_id": observable_id,
        "observable_class": observable_class,
        "observable_producer": producer,
        "evidence_source": "%s signed artifact bound to the transaction hash" % producer,
        "evidence_schema_ref": evidence_schema_ref,
        "subject": RELEASE["subject"],
        "action": RELEASE["action"],
        "resource": RELEASE["resource"],
        "destination": RELEASE["destination"],
        "action_parameters": dict(RELEASE_PARAMS),
        "parameter_schema_ref": "PS-RELEASE-PAYMENT",
        "operator": operator,
        "expected_value": expected,
        "temporal_window": None,
        "evaluation_basis": basis,
        "threshold_contract_ref": threshold_contract_ref,
        "on_unknown": "fail",
        "on_fail": "SAFE_STATE",
        "gate_candidate": "mandatory",
        "mandatory_role": "decisive",
        "escalation": {"route": escalation_route, "sla_hours": escalation_sla},
        "evidence_requirements": evidence_reqs,
        "context_conditions": conditions,
        "control_owner": owner,
        "approver": APPROVER,
        "approval_time": APPROVAL_TIME,
        "validity_interval": dict(VALIDITY),
        "version_binding_ref": BINDING,
        "evidence_semantics": evidence_semantics,
        "decision_semantics": decision_semantics,
        "warrant_boundary": warrant_boundary,
        "policy_id": policy_id,
    }


def _cond(attribute, operator, value, producer, schema_ref, unit=None, contract=None):
    return {
        "attribute": attribute,
        "operator": operator,
        "value": value,
        "unit": unit,
        "on_unknown": "fail",
        "required": True,
        "evidence_producer": producer,
        "evidence_schema_ref": schema_ref,
        "threshold_contract_ref": contract,
        "temporal_window": None,
    }


def build_acs_records():
    return [
        _acs(
            "ACS-B01-01", "GCIR-B0001", "B-01", ["INT-PERMIT-BIND"],
            "permit_binding", "T-PERMIT-BIND",
            "permit_valid_and_bound", "permit_binding_state",
            "authority_permit_service_v2", "ES-PERMIT-BIND",
            "==", True, "structural_check", "payment_operations_urgent", 1,
            ["transaction_hash", "permit_id", "permit_signature", "bound_hash"],
            [_cond("permit_valid_and_bound", "==", True,
                   "authority_permit_service_v2", "ES-PERMIT-BIND")],
            OWNER_PLATFORM,
            "A signed permit artifact whose payload binds the permit identifier to this transaction hash.",
            "PERMIT requires a valid permit signature whose bound hash equals the transaction hash under evaluation; indeterminate or absent evidence fails.",
            "Establishes that a valid, bound permit exists. It does not establish that the authorization decision behind the permit was substantively correct.",
            policy_id="POL-B-PERMIT",
        ),
        _acs(
            "ACS-B02-01", "GCIR-B0002", "B-02", ["INT-PAY-LIMIT"],
            "amount_limit", "T-AMOUNT-LIMIT",
            "amount_minor_units", "instruction_amount_measurement",
            "payment_instruction_service_v1", "ES-AMOUNT",
            "<=", 25000000, "threshold_on_measured_value", "payment_operations_urgent", 2,
            ["transaction_hash", "amount_minor_units", "currency", "artifact_signature"],
            [_cond("amount_minor_units", "<=", 25000000,
                   "payment_instruction_service_v1", "ES-AMOUNT",
                   unit="minor currency units (CAD cents)", contract="TC-PAYMENT-LIMIT")],
            OWNER_PAYMENTS,
            "A signed instruction artifact carrying the amount in minor units and the currency code, as recorded by the originating system.",
            "PERMIT requires amount_minor_units <= the approved bound under threshold contract TC-PAYMENT-LIMIT for the stated currency; indeterminate or absent evidence fails.",
            "Establishes that the instruction is within the approved automated release ceiling. It does not establish that the payment is legitimate.",
            threshold_contract_ref="TC-PAYMENT-LIMIT",
            policy_id="POL-B-LIMIT",
        ),
        _acs(
            "ACS-B03-01", "GCIR-B0003", "B-03", ["INT-PAY-LIMIT"],
            "velocity_bound", "T-VELOCITY",
            "window_transaction_count", "window_transaction_count",
            "velocity_counter_service_v1", "ES-VELOCITY",
            "<=", 20, "threshold_on_measured_value", "payment_operations_urgent", 2,
            ["transaction_hash", "window_count", "window_seconds", "counterparty_id", "artifact_signature"],
            [_cond("window_transaction_count", "<=", 20,
                   "velocity_counter_service_v1", "ES-VELOCITY",
                   unit="transactions per counterparty per 3600 s",
                   contract="TC-VELOCITY-BOUND")],
            OWNER_PAYMENTS,
            "A signed window-count artifact reporting committed releases to the same counterparty inside the approved rolling window.",
            "PERMIT requires window_transaction_count <= the approved bound under threshold contract TC-VELOCITY-BOUND; indeterminate or absent evidence fails.",
            "Establishes that observed velocity is within the approved bound. It does not establish that a within-bound pattern is legitimate.",
            threshold_contract_ref="TC-VELOCITY-BOUND",
            policy_id="POL-B-LIMIT",
        ),
        _acs(
            "ACS-B04-01", "GCIR-B0004", "B-04", ["SEMA-SANCTIONS", "PCMLTFA-REPORT"],
            "restricted_party_screening", "T-RESTRICTED-PARTY",
            "restricted_party_match", "restricted_party_match",
            "sanctions_screening_service_v5", "ES-RESTRICTED-PARTY",
            "==", False, "deterministic_lookup", "sanctions_desk_urgent", 1,
            ["transaction_hash", "counterparty_id", "list_version", "match_count", "artifact_signature"],
            [_cond("restricted_party_match", "==", False,
                   "sanctions_screening_service_v5", "ES-RESTRICTED-PARTY")],
            OWNER_SANCTIONS,
            "A SIGNED screening artifact reporting whether the counterparty matches the restricted-party list at a stated list version.",
            "PERMIT requires restricted_party_match == false. Missing, stale or schema-invalid evidence is indeterminacy and fails; escalation is raised on failure.",
            "Establishes that the signed screening artifact reports no match at the stated list version. It does NOT establish that the screening service resolves every alias, transliteration or ownership chain correctly; that residual is an evidence-production exposure outside this predicate's warrant.",
            policy_id="POL-B-SANCTIONS",
        ),
        _acs(
            "ACS-B05-01", "GCIR-B0005", "B-05", ["INT-PERMIT-BIND"],
            "permit_single_use", "T-SINGLE-USE",
            "permit_unredeemed_and_hash_novel", "permit_and_hash_novelty",
            "authority_permit_service_v2", "ES-SINGLE-USE",
            "==", True, "structural_check", "payment_operations_urgent", 1,
            ["transaction_hash", "permit_id", "permit_previously_redeemed", "hash_previously_seen"],
            [_cond("permit_unredeemed_and_hash_novel", "==", True,
                   "authority_permit_service_v2", "ES-SINGLE-USE")],
            OWNER_PLATFORM,
            "A signed redemption-state artifact reporting whether this permit has already been redeemed and whether this transaction hash has already been seen.",
            "PERMIT requires the permit to be unredeemed and the transaction hash to be novel; indeterminate or absent evidence fails.",
            "Establishes single-use semantics over the permit and hash. It does not establish that two economically identical instructions with different hashes are not duplicates.",
            policy_id="POL-B-PERMIT",
        ),
        _acs(
            "ACS-B06-01", "GCIR-B0006", "B-06", ["INT-EVID-CHAIN-B", "PCMLTFA-REPORT"],
            "receipt_chain_completeness", "T-RECEIPT-CHAIN-B",
            "receipt_committed_between_authorization_and_actuation", "receipt_chain_state",
            "evidence_chain_service_v2", "ES-RECEIPT-CHAIN",
            "==", True, "structural_check", "compliance_records_urgent", 1,
            ["receipt_id", "authorization_time", "evidence_commit_time", "actuation_time", "chain_prev_hash"],
            [_cond("receipt_committed_between_authorization_and_actuation", "==", True,
                   "evidence_chain_service_v2", "ES-RECEIPT-CHAIN")],
            OWNER_RECORDS,
            "A signed evidence-chain artifact carrying the authorization, commit and actuation instants for this decision, and the chain link to its predecessor.",
            "PERMIT requires authorization_time <= evidence_commit_time < actuation_time with a verified chain link; indeterminate or absent evidence fails.",
            "Establishes the temporal ordering and chaining of the evidence record. It coincides with compiler invariant INV-EVIDENCE-COMMIT; origin metadata keeps the two authorizations distinct. It does not establish the truth of the receipt's content.",
            policy_id="POL-B-EVIDENCE",
        ),
    ]


RUNTIME_ACS = {
    "B-01": ["ACS-B01-01"],
    "B-02": ["ACS-B02-01"],
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
    "ACS-B01-01": "Permit validity and binding is a structural check over a signed artifact; T-PERMIT-BIND is the approved template.",
    "ACS-B02-01": "The instruction amount is a measured value requiring a threshold contract; T-AMOUNT-LIMIT selected with TC-PAYMENT-LIMIT.",
    "ACS-B03-01": "Window transaction count is a measured value requiring a threshold contract; T-VELOCITY selected with TC-VELOCITY-BOUND.",
    "ACS-B04-01": "Restricted-party screening resolves to a signed artifact; T-RESTRICTED-PARTY is the approved deterministic-lookup template. Selected by class, not by score: at s = 5 this is the lowest-rated row on the register.",
    "ACS-B05-01": "Permit redemption state and hash novelty are structural; T-SINGLE-USE selected.",
    "ACS-B06-01": "Receipt ordering and chaining are structural; T-RECEIPT-CHAIN-B selected. The forum recorded that this coincides with INV-EVIDENCE-COMMIT.",
}

SELECTORS_B = {
    "ACS-B04-01": "compliance.head_sanctions",
    "ACS-B06-01": "compliance.head_records",
}
DEFAULT_SELECTOR_B = "business.head_payment_operations"


def build_judgment_record(acs_records):
    selections = []
    approvals = []
    decisions = []
    for index, acs in enumerate(acs_records, start=1):
        selector = SELECTORS_B.get(acs["acs_id"], DEFAULT_SELECTOR_B)
        selections.append(
            {
                "selection_id": "JB-SEL-%03d" % index,
                "risk_id": acs["risk_id"],
                "acs_id": acs["acs_id"],
                "event_type": acs["event_type"],
                "template_id": acs["template_id"],
                "selected_by": selector,
                "selection_time": "2026-01-21T10:00:00Z",
                "rationale": _SELECTION_RATIONALE_B[acs["acs_id"]],
            }
        )
        approvals.append(
            {
                "acs_id": acs["acs_id"],
                "approver": APPROVER,
                "approval_time": APPROVAL_TIME,
                "forum": FORUM,
            }
        )
        decisions.append(
            {
                "risk_id": acs["risk_id"],
                "status": "runtime",
                "decided_by": selector,
                "decision_time": "2026-01-21T10:00:00Z",
                "rationale": "The risk has an approved catalog observable evaluable at authorization time on the sole authorized external action path.",
            }
        )
    decisions.sort(key=lambda d: d["risk_id"])
    return {
        "judgment_id": "J-CASE-B",
        "version": "1.0",
        "assessment_ref": {"assessment_id": "ASSESSMENT-CASE-B", "binding_id": BINDING},
        "catalog_ref": {"catalog_id": "K-CASE-B", "version": "1.0"},
        "selections": selections,
        "disposition_decisions": decisions,
        "approvals": approvals,
    }


CSTAR_PROFILE = {
    "profile_id": "CSTAR-B",
    "version": "1.0",
    "version_binding_ref": BINDING,
    "approved_by": FORUM,
    "approval_time": APPROVAL_TIME,
    "materiality_order": ["immaterial", "minor", "material", "severe"],
    "member_kinds": [
        "material_statutory_prohibition",
        "unauthorized_authority_exercise",
        "material_information_barrier_breach",
        "irreversible_external_effect_above_approved_bound",
    ],
    "classification_rules": {
        "material_statutory_prohibition": {
            "approving_authority": "exec.head_of_payments",
            "rationale": "A sanctions or record-keeping breach is a statutory prohibition whose materiality does not depend on its frequency.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "An immaterial technical non-conformance does not enter C* solely because its source is statutory.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
        "unauthorized_authority_exercise": {
            "approving_authority": "exec.head_of_payments",
            "rationale": "Releasing a payment without a valid permit is the system causing an effect it is not authorized to cause.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "An unauthorized act with no external effect is below the boundary.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
        "material_information_barrier_breach": {
            "approving_authority": "exec.head_of_payments",
            "rationale": "Retained from the enterprise base profile; no Case B row is classified under it.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "Not exercised by this register.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
        "irreversible_external_effect_above_approved_bound": {
            "approving_authority": "exec.head_of_payments",
            "rationale": "A settled duplicate payment cannot be rescinded on the rail.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "A release that the rail can recall before settlement is below the boundary.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
    },
}

POLICY_METADATA = {
    "bundle_id": "BUNDLE-CASE-B-1.0",
    "precedence": {},
    "precedence_relation": ["mandatory_failure", "mandatory_pass", "weighted_or_advisory"],
    "aggregation_groups": {},
    "runtime_acceptance_condition": (
        "A conformant consuming runtime loads only bundles verifying as signed Phi "
        "outputs (signature, payload hash, lifecycle-registry state), accepts no "
        "policy content through any other channel, and emits decision receipts "
        "carrying the requirement reference (gcir_id, acs_id and origin) of every "
        "evaluated predicate."
    ),
}
