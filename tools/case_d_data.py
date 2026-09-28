"""Case D -- treasury emergency-exception funds transfer agent (Paper 2 v1.2,
spec section 4, D1-D10).

This is a new, prospectively designed case exercising the v1.2
governance-to-control validation layer, not a reconstruction of any
historical artifact. Its purpose is narrow: does the compiler/validator
accept a genuinely authorized emergency-exception translation while
rejecting a controlled unauthorized semantic change to it, for the correct
reason -- while keeping the emergency exception path structurally confined
to its own predicate and never becoming an ordinary-transfer prerequisite.

Two risks, one authority (release_funds):

    D-01: an ordinary funds transfer releases without the required dual
          authorization (two treasury officers). Present, identical, and
          decisive across every CCS variant.

    D-02: an emergency funds transfer proceeds without a validly authorized
          emergency officer under declared emergency conditions. This risk's
          DISPOSITION is what varies across CCS0/CCS1/CCS2 (spec D2-D9):
            CCS0: emergency path explicitly disabled -- D-02 is an accepted
                  residual risk, routed to a declared manual governance
                  process, not compiled as a runtime control at all.
            CCS1: emergency path enabled; J_D resolves "authorized officer"
                  = the Treasury Officer credential (spec D5). D-02 compiles
                  to its own predicate (ACS-D02-01), confined to the
                  exception path (spec D6), never touching D-01's ordinary
                  gate.
            CCS2: policy 4.3 / J' (spec D9) widens the authorized actor set
                  to include the analyst + ETA-2 tier, up to the same $1M
                  bound -- a NEW, separately authorized judgment, not an
                  unauthorized ad-hoc widening (contrast spec D7).
"""

import hashlib

BINDING = "VB-CASE-D-1.0"
APPROVAL_TIME = "2026-03-02T15:00:00Z"
EFFECTIVE_FROM = "2026-03-05T00:00:00Z"
VALID_UNTIL = "2027-03-05T00:00:00Z"
COMPILE_TIME = "2026-03-06T09:00:00Z"

FORUM = "treasury_governance_forum"
ACCOUNTABLE_EXEC = "exec.head_of_treasury"
ASSESSOR = "governance.assessor_treasury"
APPROVER = "forum.chair_treasury"

OWNER_TREASURY = "business.treasury_operations"

RELEASE = {
    "subject": "treasury_agent",
    "action": "release_funds",
    "resource": "funds_transfer_instruction",
    "destination": "treasury_rail",
}

METADATA = {
    "system_id": "CASE-D-TREASURY-EMERGENCY-EXCEPTION-AGENT",
    "purpose": (
        "Per-transfer authorization of outbound treasury funds releases, "
        "requiring dual authorization under ordinary conditions and "
        "supporting a narrowly confined, separately authorized emergency "
        "exception for a single validly authorized emergency officer."
    ),
    "owner_business": OWNER_TREASURY,
    "owner_technical": "technology.treasury_platform",
    "accountable_exec": ACCOUNTABLE_EXEC,
    "assessor": ASSESSOR,
    "deployment": "production treasury funds-release path, single rail",
    "scope": (
        "Authorization of outbound treasury funds release under ordinary "
        "dual-authorization, and, only where the emergency exception is "
        "itself enabled and authorized, a narrowly confined single-officer "
        "emergency path."
    ),
    "exclusions": [
        "No transfer initiation: the agent authorizes releases, it does not originate instructions.",
        "No counterparty onboarding.",
        "No customer-facing communication.",
    ],
    "method": "Paper 2 v1.2 governance-to-control validation campaign; prospectively designed, not a forensic reconstruction.",
    "version_binding": {
        "binding_id": BINDING,
        "model_version": "treasury-authorization-policy-engine-2026.03",
        "prompt_version": "not-applicable-non-generative",
        "dataset_version": "treasury-authority-roster-2026-03-01",
        "policy_version": "treasury-policy-2026.1",
        "fingerprint": "sha256:9a1d4e6b0c7f2e83a5d19c4b3e8f60a2d7c5b9e1f4a8c2d6b0e3f7a1c5d9b2e6",
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
        "subject": "treasury_agent",
        "action": "release_funds",
        "resource": "funds_transfer_instruction",
        "destination": "treasury_rail",
        "parameter_schema_id": "PS-RELEASE-FUNDS",
        "parameter_schema": {
            "transfer_hash": {"type": "string", "required": True},
            "currency": {"type": "string", "enum": ["CAD", "USD"], "required": True},
        },
        "hazardous": True,
        "notes": "The sole external action. Once released, a treasury transfer is not rescindable on the rail.",
    },
]

SYSTEM_PROFILE = {
    "capabilities": [
        "per-transfer authorization decisioning",
        "dual-authorization verification against the authorization registry",
        "narrowly confined emergency-exception evaluation, only where enabled and authorized",
    ],
    "data_classes": [
        "funds transfer instruction detail",
        "treasury officer authorization roster",
        "emergency-event and emergency-officer-authority evidence",
    ],
    "actors": ["treasury_agent", "treasury.officer_on_duty", "payments.analyst_eta2_tier"],
    "affected_parties": [
        "beneficiaries of authorized transfers",
        "the institution as a regulated entity",
    ],
    "architecture": (
        "Transfer request -> decision service -> runtime authority (permit or "
        "SAFE_STATE) -> evidence commit -> treasury rail release."
    ),
    "scale": {"transfers_per_day": 400, "unit": "count"},
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
        "decision_time": "2026-02-20T16:30:00Z",
        "effective_from": EFFECTIVE_FROM,
        "legal_source_version": version,
        "requirement_class": cls,
    }


OBLIGATIONS = [
    _obligation(
        "INT-DUAL-AUTH",
        "Internal requirement -- Treasury Dual Authorization Standard",
        "TDA-2026 s. 1",
        "internal",
        ["all automated treasury funds release"],
        "TDA-2026.1",
    ),
    _obligation(
        "INT-EMERGENCY-EXCEPTION",
        "Internal requirement -- Treasury Emergency Exception Standard",
        "TEE-2026 s. 1 (confined single-officer emergency path)",
        "internal",
        ["treasury funds release under declared emergency conditions only"],
        "TEE-2026.1",
    ),
]

_AFFECTED = ["beneficiaries of authorized transfers", "the institution as a regulated entity"]
_EXISTING_CONTROLS = ["service-to-service authentication"]


def _risk_row(risk_id, cause, event, consequence, obligations):
    return {
        "risk_id": risk_id,
        "cause": cause,
        "event": event,
        "consequence": consequence,
        "affected_parties": list(_AFFECTED),
        "obligation_refs": obligations,
        "existing_controls": list(_EXISTING_CONTROLS),
        "owner": OWNER_TREASURY,
        "hazardous_action_paths": [dict(RELEASE)],
        "source_register_row": "prospectively designed for the Paper 2 v1.2 governance-to-control validation campaign",
    }


def build_risk_register():
    return [
        _risk_row(
            "D-01",
            "the release path can be invoked with only one authorizing officer",
            "a funds transfer releases without the required dual authorization",
            "an unauthorized externalization -- the system exercises authority it does not hold",
            ["INT-DUAL-AUTH"],
        ),
        _risk_row(
            "D-02",
            "an emergency-exception path, when enabled, permits a single officer to release without dual authorization",
            "an emergency funds transfer proceeds without a validly authorized emergency officer under declared emergency conditions",
            "an unauthorized externalization under a claimed emergency -- the exception is exercised without its required preconditions",
            ["INT-EMERGENCY-EXCEPTION"],
        ),
    ]


def _analysis_row(risk_id, lr, ir, kind, rationale, reopening=None):
    return {
        "risk_id": risk_id,
        "likelihood_inherent": min(5, lr + 1),
        "impact_inherent": ir,
        "control_effectiveness": "partially_effective",
        "likelihood_residual": lr,
        "impact_residual": ir,
        "consequence_class": "authority",
        "consequence_descriptor": {
            "kind": kind,
            "materiality": "material",
            "reversibility": "irreversible",
            "authority": "institution_treasury_function",
            "classification_authority": "forum.consequence_classification_panel",
            "rationale": rationale,
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
        "tier": "tier_1",
        "treatment": "mitigate",
        "reopening_trigger": reopening,
    }


def build_risk_analysis():
    return [
        _analysis_row(
            "D-01", 2, 5, "unauthorized_authority_exercise",
            "Classified under the approved C* profile CSTAR-D-1.0: an ordinary release without the required dual authorization is a material, irreversible unauthorized externalization.",
        ),
        _analysis_row(
            "D-02", 2, 5, "confined_emergency_exception_exposure",
            "Deliberately NOT a CSTAR-D-1.0 member kind (mirrors Case B v1.1's B-02/B-03 'other approved mandatory' pattern, docs/CASE_B_V1_1_RATIONALE.md): the confined emergency exception is mandatorily gated via gate_candidate=mandatory whenever it is compiled at all, independent of C* membership, which is exactly what lets D-02's disposition legitimately vary -- runtime (CCS1/CCS2) or an accepted residual with a declared non-runtime treatment when the path is governance-disabled (CCS0, spec D2) -- without invoking C* coverage's runtime-or-RC-06-only rule.",
            reopening="any change to the emergency-exception authorization roster or parameter bounds",
        ),
    ]
