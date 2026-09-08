"""Case B -- transaction authorization agent (manuscript Section X).

EVIDENCE CLASS: **forensic reconstruction**.

    "The register above is a forensic reconstruction; Section XII states this
     openly, and the mitigation is the hash-pinned artifact: once pinned, the
     mapping is reproducible going forward even though its origin is
     retrospective."  (Section X)

What this artifact is NOT: it is not new production evidence, and it does not
reproduce the 284,807-event golden-trace conformance run reported in [15].  That
run's figures are stated and bounded there.  What Case B adds here is the
upstream register-to-disposition-to-predicate mapping that produced those
predicate families.

Manuscript-stated content preserved:
  * per-transaction authorization agent, machine-speed decisioning
  * the authority matrix admits exactly one external action (release_payment)
    with bound parameters
  * six register rows, all runtime, all mandatory (four by C*, two by other
    approved mandatory policy)
  * B-04's rating decomposition L=1, I=5 (stated explicitly in Section X)
  * the residual L x I products of all six rows
"""

import hashlib

BINDING = "VB-CASE-B-1.0"
APPROVAL_TIME = "2026-01-22T15:00:00Z"
EFFECTIVE_FROM = "2026-02-01T00:00:00Z"
VALID_UNTIL = "2027-02-01T00:00:00Z"
COMPILE_TIME = "2026-02-02T09:00:00Z"

FORUM = "payments_governance_forum"
ACCOUNTABLE_EXEC = "exec.head_of_payments"
ASSESSOR = "governance.assessor_r_okafor"
APPROVER = "forum.chair_m_dubois"

RELEASE = {
    "subject": "transaction_agent",
    "action": "release_payment",
    "resource": "payment_instruction",
    "destination": "payment_rail",
}
EVALUATE = {
    "subject": "transaction_agent",
    "action": "evaluate_transaction",
    "resource": "transaction_request",
    "destination": "decision_service",
}

METADATA = {
    "system_id": "CASE-B-TRANSACTION-AUTHORIZATION-AGENT",
    "purpose": (
        "Per-transaction authorization of outbound payment instructions at machine "
        "speed, with every proposed externalization mediated by the runtime "
        "authority."
    ),
    "owner_business": "business.payment_operations",
    "owner_technical": "technology.payments_platform",
    "accountable_exec": ACCOUNTABLE_EXEC,
    "assessor": ASSESSOR,
    "deployment": "production payment authorization path, single rail",
    "scope": (
        "Authorization of outbound payment release. Every proposed externalization "
        "is mediated by the runtime authority; no payment leaves the institution "
        "without a permit."
    ),
    "exclusions": [
        "No payment initiation: the agent authorizes releases, it does not originate instructions.",
        "No counterparty onboarding or KYC decisioning.",
        "No customer-facing communication.",
    ],
    "method": "NIST AI RMF 1.0 Map/Measure profile with ISO 31000 cause-event-consequence register; register reconstructed retrospectively from the deployed predicate families",
    "version_binding": {
        "binding_id": BINDING,
        "model_version": "txn-authorization-policy-engine-2026.01",
        "prompt_version": "not-applicable-non-generative",
        "dataset_version": "restricted-party-list-2026-01-28",
        "policy_version": "payments-policy-2026.1",
        "fingerprint": "sha256:2c7e94b0af165d3e8a2140c9db73f6e50b8d1a4c9e2f70b6a538d1c04e97fa38",
    },
    "review_cycle": "semi-annual, or on any trigger",
    "triggers": [
        "model_version_change",
        "prompt_or_policy_change",
        "dataset_refresh_outside_bounds",
        "scope_expansion",
        "new_obligation",
        "catalog_change",
        "consequence_class_reclassification",
        "incident_above_declared_severity",
    ],
    "validity_interval": {"effective_from": EFFECTIVE_FROM, "effective_until": VALID_UNTIL},
}

AUTHORITY_MATRIX = [
    {
        "subject": "transaction_agent",
        "action": "release_payment",
        "resource": "payment_instruction",
        "destination": "payment_rail",
        "parameter_schema_id": "PS-RELEASE-PAYMENT",
        "parameter_schema": {
            "transaction_hash": {"type": "string", "required": True},
            "currency": {"type": "string", "enum": ["CAD", "USD"], "required": True},
            "rail": {"type": "string", "enum": ["domestic_rtr", "swift"], "required": True},
        },
        "hazardous": True,
        "notes": "The sole external action. Once released, a payment is not rescindable on the rail.",
    },
    {
        "subject": "transaction_agent",
        "action": "evaluate_transaction",
        "resource": "transaction_request",
        "destination": "decision_service",
        "parameter_schema_id": "PS-EVALUATE-TXN",
        "parameter_schema": {"transaction_hash": {"type": "string", "required": True}},
        "hazardous": False,
        "notes": "Internal evaluation; produces no external effect.",
    },
]

SYSTEM_PROFILE = {
    "capabilities": [
        "per-transaction authorization decisioning at machine speed",
        "restricted-party screening against a signed list artifact",
        "velocity and limit evaluation over a bounded window",
        "single-use permit issuance bound to a transaction hash",
    ],
    "data_classes": [
        "payment instruction detail",
        "counterparty identity and restricted-party list",
        "transaction history within the velocity window",
    ],
    "actors": ["transaction_agent", "payment_operations_analyst", "sanctions_officer"],
    "affected_parties": [
        "payers and payees of authorized transactions",
        "the institution as a regulated entity",
        "sanctioned parties whose transactions must not settle",
    ],
    "architecture": (
        "Transaction request -> decision service -> runtime authority (permit or "
        "SAFE_STATE) -> evidence commit -> payment rail release."
    ),
    "scale": {"transactions_per_day": 180000, "unit": "count"},
    "autonomy_level": "autonomous_agent",
    "authority_matrix": AUTHORITY_MATRIX,
}


def _obligation(oid, source, clause, cls, basis, version):
    return {
        "obligation_id": oid,
        "source": source,
        "jurisdiction": "Canada",
        "territorial_basis": "legal entity domiciled and registered in Canada",
        "clause_ref": clause,
        "requirement_text_hash": hashlib.sha256(
            ("REQUIREMENT-TEXT-FIXTURE::%s::%s" % (oid, clause)).encode("utf-8")
        ).hexdigest(),
        "applicability_basis": basis,
        "applicability_decision": "applicable",
        "decision_authority": "legal.regulatory_counsel",
        "decision_time": "2026-01-14T16:30:00Z",
        "effective_from": EFFECTIVE_FROM,
        "legal_source_version": version,
        "requirement_class": cls,
    }


OBLIGATIONS = [
    _obligation(
        "SEMA-SANCTIONS",
        "Special Economic Measures Act and related regulations; UN Act regulations",
        "prohibition on dealings with listed persons",
        "statutory",
        ["Canadian financial institution", "effects outbound payments"],
        "consolidated to 2026-01-15",
    ),
    _obligation(
        "PCMLTFA-REPORT",
        "Proceeds of Crime (Money Laundering) and Terrorist Financing Act",
        "s. 7 reporting and s. 6 record keeping",
        "statutory",
        ["reporting entity under the Act"],
        "consolidated to 2025-11-01",
    ),
    _obligation(
        "OSFI-E21-ORR-B",
        "OSFI Guideline E-21, Operational Risk and Resilience",
        "s. 4 critical operations",
        "supervisory",
        ["payment authorization is a critical business service"],
        "OSFI E-21 (2024)",
    ),
    _obligation(
        "INT-PAY-LIMIT",
        "Internal requirement -- Payment Authorization Limit Standard",
        "PAL-2026 s. 2 (per-transaction limit) and s. 3 (velocity bound)",
        "internal",
        ["all automated payment authorization"],
        "PAL-2026.1",
    ),
    _obligation(
        "INT-PERMIT-BIND",
        "Internal requirement -- Permit Binding and Single-Use Standard",
        "PBS-2026 s. 1",
        "internal",
        ["all automated authorization decisions with an external effect"],
        "PBS-2026.1",
    ),
    _obligation(
        "INT-EVID-CHAIN-B",
        "Internal requirement -- Evidence Chain Completeness Standard",
        "ECC-2026 s. 1 (authorization receipts)",
        "internal",
        ["all authorization decisions taken by an automated authority"],
        "ECC-2026.1",
    ),
]

# (risk_id, cause, event, consequence, obligations, L_res, I_res,
#  consequence_class, descriptor kind, materiality, reversibility)
_RISKS = [
    (
        "B-01",
        "the release path and the decision path are separate services and a release could proceed without consulting the authority",
        "a payment release proceeds without a valid permit bound to the transaction hash",
        "an unauthorized externalization -- the system exercises authority it does not hold",
        ["INT-PERMIT-BIND"],
        3, 5,
        "authority", "unauthorized_authority_exercise", "material", "irreversible",
    ),
    (
        "B-02",
        "instruction amounts are supplied upstream and are not bounded by the originating system",
        "the instruction amount exceeds the approved per-transaction limit",
        "financial loss beyond the approved exposure bound",
        ["INT-PAY-LIMIT"],
        4, 4,
        "financial_loss", "financial_loss", "material", "partially_reversible",
    ),
    (
        "B-03",
        "an upstream compromise or defect can emit many individually-conforming instructions in a short window",
        "the transaction count in the approved window exceeds the approved bound",
        "aggregate financial loss through high-velocity release, and disruption of a critical business service",
        ["INT-PAY-LIMIT", "OSFI-E21-ORR-B"],
        3, 4,
        "financial_loss", "financial_loss", "material", "partially_reversible",
    ),
    (
        "B-04",
        "counterparty records and the restricted-party list are maintained in separate systems and can diverge",
        "the counterparty is a member of the restricted-party list at release time",
        "a sanctions breach -- a statutory prohibition, material irrespective of frequency",
        ["SEMA-SANCTIONS", "PCMLTFA-REPORT"],
        1, 5,
        "statutory", "material_statutory_prohibition", "material", "irreversible",
    ),
    (
        "B-05",
        "permits are transported between services and a retry path can present the same permit twice",
        "a permit is reused, or a transaction hash already seen is presented again",
        "duplicate settlement -- an irreversible external effect",
        ["INT-PERMIT-BIND"],
        2, 5,
        "irreversible", "irreversible_external_effect_above_approved_bound", "material", "irreversible",
    ),
    (
        "B-06",
        "the authorization decision and its evidence record are produced by different components and can diverge under failure",
        "the decision receipt is not committed between the authorization decision and actuation",
        "the authorization is not evidenced, defeating the statutory record-keeping requirement",
        ["INT-EVID-CHAIN-B", "PCMLTFA-REPORT"],
        2, 5,
        "statutory", "material_statutory_prohibition", "material", "irreversible",
    ),
]

_AFFECTED_B = {
    "authority": ["payers and payees of authorized transactions", "the institution as a regulated entity"],
    "financial_loss": ["the institution as a regulated entity", "payers of authorized transactions"],
    "statutory": ["the institution as a regulated entity", "sanctioned parties whose transactions must not settle"],
    "irreversible": ["payers and payees of authorized transactions", "the institution as a regulated entity"],
}

_EXISTING_CONTROLS_B = {
    "B-01": ["service-to-service authentication"],
    "B-02": ["upstream limit configuration"],
    "B-03": ["rail-level throttling"],
    "B-04": ["nightly restricted-party list refresh"],
    "B-05": ["idempotency keys in the originating system"],
    "B-06": ["application logging"],
}


def build_risk_register():
    rows = []
    for rid, cause, event, consequence, obligations, _lr, _ir, cclass, _k, _m, _rev in _RISKS:
        rows.append(
            {
                "risk_id": rid,
                "cause": cause,
                "event": event,
                "consequence": consequence,
                "affected_parties": _AFFECTED_B[cclass],
                "obligation_refs": obligations,
                "existing_controls": _EXISTING_CONTROLS_B[rid],
                "owner": "business.payment_operations",
                "hazardous_action_paths": [dict(RELEASE)],
                "source_register_row": "forensic reconstruction from the deployed predicate family",
            }
        )
    return rows


def build_risk_analysis():
    rows = []
    for rid, _c, _e, _q, _o, lr, ir, cclass, kind, materiality, reversibility in _RISKS:
        rows.append(
            {
                "risk_id": rid,
                "likelihood_inherent": min(5, lr + 1),
                "impact_inherent": ir,
                "control_effectiveness": "partially_effective",
                "likelihood_residual": lr,
                "impact_residual": ir,
                "consequence_class": cclass,
                "consequence_descriptor": {
                    "kind": kind,
                    "materiality": materiality,
                    "reversibility": reversibility,
                    "authority": "institution_payment_function",
                    "classification_authority": "forum.consequence_classification_panel",
                    "rationale": "Classified under the approved C* profile CSTAR-B-1.0; reconstructed retrospectively from the deployed predicate family and re-approved by the forum.",
                    "effective_date": APPROVAL_TIME,
                    "emergency_override_procedure": None,
                },
                "tier": "tier_1",
                "treatment": "mitigate",
                "reopening_trigger": _REOPENING_B.get(rid),
            }
        )
    return rows


_REOPENING_B = {
    "B-04": "any change to the restricted-party list source or refresh cadence",
    "B-02": "any change to the approved per-transaction limit",
    "B-03": "any change to the approved velocity window or bound",
}
