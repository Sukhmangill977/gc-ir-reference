"""Case D control layer: catalog, ACS, dispositions, judgment record -- for
each of the three CCS variants (spec section 4, D2/D5/D9).

    CCS0: emergency exception explicitly disabled (D2/D3).
    CCS1: emergency exception enabled; J_D resolves "authorized officer" =
          the Treasury Officer credential (D5); confined to the exception
          path (D6).
    CCS2: policy 4.3 / J' widens the authorized actor set to include the
          analyst + ETA-2 tier, up to the same $1M bound (D9) -- a new,
          separately authorized judgment, not an unauthorized ad-hoc
          widening (contrast D7).
"""

from .case_d_data import (
    ACCOUNTABLE_EXEC,
    APPROVAL_TIME,
    APPROVER,
    BINDING,
    EFFECTIVE_FROM,
    FORUM,
    RELEASE,
    VALID_UNTIL,
)

VALIDITY = {"effective_from": EFFECTIVE_FROM, "effective_until": VALID_UNTIL}

_RELEASE_TRIPLE = {
    "subject": ["treasury_agent"], "action": ["release_funds"],
    "resource": ["funds_transfer_instruction"], "destination": ["treasury_rail"],
}

RELEASE_PARAMS = {"transfer_hash": "PARAM-BOUND-AT-RUNTIME", "currency": "CAD"}

MAX_EMERGENCY_AMOUNT = 1000000


def _catalog_entry(event_type, template_id, observable_class, producer, evidence_schema_id, fields, notes):
    return {
        "event_type": event_type, "template_id": template_id,
        "observable_class": observable_class, "allowed_producers": [producer],
        "triple_template": _RELEASE_TRIPLE, "allowed_operators": ["=="],
        "value_schema": {"type": "boolean"}, "evaluation_basis": "structural_check",
        "evidence_schema": {"schema_id": evidence_schema_id, "fields": fields},
        "permitted_responses": ["SAFE_STATE"], "notes": notes,
    }


CATALOG_ENTRIES = [
    _catalog_entry(
        "dual_authorization_check", "T-DUAL-AUTH", "dual_authorization_state",
        "authorization_registry_service_v1", "ES-DUAL-AUTH",
        ["transfer_hash", "authorizer_1_id", "authorizer_2_id", "dual_authorization_present"],
        "Ordinary path: a signed registry artifact reporting whether two distinct treasury officers authorized this transfer.",
    ),
    _catalog_entry(
        "emergency_officer_authority_check", "T-EMERGENCY-AUTHORITY", "emergency_authority_state",
        "emergency_authority_registry_service_v1", "ES-EMERGENCY-AUTHORITY",
        ["transfer_hash", "emergency_event_id", "officer_id", "officer_credential",
         "emergency_event_active", "officer_authority_valid", "evidence_freshness_seconds"],
        "Exception path only (spec D6): a signed registry artifact jointly reporting EmergencyEvent, EmergencyOfficerAuthorityValid and EmergencyEvidenceFresh. Never consulted by the ordinary dual-authorization gate.",
    ),
]

CATALOG = {
    "catalog_id": "K-CASE-D", "version": "1.0", "version_binding_ref": BINDING,
    "approved_by": FORUM, "approval_time": APPROVAL_TIME, "entries": CATALOG_ENTRIES,
}

CSTAR_PROFILE = {
    "profile_id": "CSTAR-D", "version": "1.0", "version_binding_ref": BINDING,
    "approved_by": FORUM, "approval_time": APPROVAL_TIME,
    "materiality_order": ["immaterial", "minor", "material", "severe"],
    "member_kinds": ["unauthorized_authority_exercise"],
    "classification_rules": {
        "unauthorized_authority_exercise": {
            "approving_authority": ACCOUNTABLE_EXEC,
            "rationale": "Release of treasury funds without the authority actually held (dual authorization, or a validly authorized and confined emergency exception) is an unauthorized externalization irrespective of amount.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "An immaterial technical non-conformance does not enter C* solely because its source is an authority requirement.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
    },
}

POLICY_METADATA = {
    "bundle_id": "BUNDLE-CASE-D",
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

THRESHOLD_CONTRACTS = {}


def _acs(acs_id, gcir_id, risk_id, obligations, event_type, template_id,
         observable_id, observable_class, producer, evidence_schema_ref,
         escalation_route, escalation_sla, evidence_reqs, conditions,
         evidence_semantics, decision_semantics, warrant_boundary,
         policy_id, extra=None):
    record = {
        "acs_id": acs_id, "gcir_id": gcir_id, "risk_id": risk_id, "obligation_refs": obligations,
        "event_type": event_type, "template_id": template_id,
        "observable_id": observable_id, "observable_class": observable_class,
        "observable_producer": producer,
        "evidence_source": "%s signed artifact bound to the transfer hash" % producer,
        "evidence_schema_ref": evidence_schema_ref,
        "subject": RELEASE["subject"], "action": RELEASE["action"],
        "resource": RELEASE["resource"], "destination": RELEASE["destination"],
        "action_parameters": dict(RELEASE_PARAMS),
        "parameter_schema_ref": "PS-RELEASE-FUNDS",
        "operator": "==", "expected_value": True, "temporal_window": None,
        "evaluation_basis": "structural_check", "threshold_contract_ref": None,
        "on_unknown": "fail", "on_fail": "SAFE_STATE",
        "gate_candidate": "mandatory", "mandatory_role": "decisive",
        "escalation": {"route": escalation_route, "sla_hours": escalation_sla},
        "evidence_requirements": evidence_reqs, "context_conditions": conditions,
        "control_owner": "business.treasury_operations", "approver": APPROVER, "approval_time": APPROVAL_TIME,
        "validity_interval": dict(VALIDITY), "version_binding_ref": BINDING,
        "evidence_semantics": evidence_semantics, "decision_semantics": decision_semantics,
        "warrant_boundary": warrant_boundary, "policy_id": policy_id,
    }
    if extra:
        record.update(extra)
    return record


def _cond(attribute, producer, schema_ref):
    return {
        "attribute": attribute, "operator": "==", "value": True, "unit": None,
        "on_unknown": "fail", "required": True, "evidence_producer": producer,
        "evidence_schema_ref": schema_ref, "threshold_contract_ref": None,
        "temporal_window": None,
    }


def acs_d01_01():
    """The ordinary dual-authorization gate -- present, identical, and
    decisive across every CCS variant (spec D3: "ordinary requirements
    preserved")."""
    return _acs(
        "ACS-D01-01", "GCIR-D0001", "D-01", ["INT-DUAL-AUTH"],
        "dual_authorization_check", "T-DUAL-AUTH",
        "dual_authorization_present", "dual_authorization_state",
        "authorization_registry_service_v1", "ES-DUAL-AUTH",
        "treasury_operations_urgent", 1,
        ["transfer_hash", "authorizer_1_id", "authorizer_2_id", "dual_authorization_present"],
        [_cond("dual_authorization_present", "authorization_registry_service_v1", "ES-DUAL-AUTH")],
        "A signed registry artifact reporting whether two distinct treasury officers authorized this transfer.",
        "PERMIT requires dual_authorization_present == true; indeterminate or absent evidence fails. This condition carries no emergency-authority prerequisite and no emergency-evidence prerequisite (spec D3): it is evaluated identically whether or not the emergency exception is enabled elsewhere.",
        "Establishes that two distinct treasury officers authorized this transfer. It does not establish that either officer's judgment was substantively correct.",
        "POL-D-DUAL-AUTH",
        extra={"primary_class": "auth", "enforcement_phase": "PRE_AUTHORIZATION"},
    )


def acs_d02_01(authorized_actor, max_amount=MAX_EMERGENCY_AMOUNT, policy_id="POL-D-EMERGENCY-EXCEPTION",
               interpretation_status=None):
    """The emergency-exception gate (spec D6): active only where
    ``ValidEmergencyException = EmergencyEvent AND
    EmergencyOfficerAuthorityValid AND EmergencyEvidenceFresh`` all hold --
    three independent context conditions, none of which appears on
    ``acs_d01_01``'s condition set. ``authorized_actor``/``max_amount``
    vary across CCS1 (D5) and CCS2 (D9); ``interpretation_status`` lets a
    caller build the D1 unresolved-interpretation negative directly from
    this same builder.
    """
    conditions = [
        _cond("emergency_event_active", "emergency_authority_registry_service_v1", "ES-EMERGENCY-AUTHORITY"),
        _cond("officer_authority_valid", "emergency_authority_registry_service_v1", "ES-EMERGENCY-AUTHORITY"),
        _cond("evidence_fresh", "emergency_authority_registry_service_v1", "ES-EMERGENCY-AUTHORITY"),
    ]
    extra = {
        "primary_class": "auth",
        "enforcement_phase": "PRE_AUTHORIZATION",
        "exception": {
            "target_requirement": "INT-DUAL-AUTH",
            "trigger": "EmergencyEvent",
            "authorized_actor": list(authorized_actor),
            "parameter_bounds": {"max_amount": max_amount},
            "scope": ["emergency_single_officer_transfer"],
            "lifecycle_version_binding": BINDING,
        },
    }
    if interpretation_status is not None:
        extra["interpretation_status"] = interpretation_status
    return _acs(
        "ACS-D02-01", "GCIR-D0002", "D-02", ["INT-EMERGENCY-EXCEPTION"],
        "emergency_officer_authority_check", "T-EMERGENCY-AUTHORITY",
        "emergency_officer_authority_valid", "emergency_authority_state",
        "emergency_authority_registry_service_v1", "ES-EMERGENCY-AUTHORITY",
        "treasury_operations_urgent", 1,
        ["transfer_hash", "emergency_event_id", "officer_id", "officer_credential",
         "emergency_event_active", "officer_authority_valid", "evidence_freshness_seconds"],
        conditions,
        "A signed emergency-authority-registry artifact jointly reporting EmergencyEvent, EmergencyOfficerAuthorityValid, and EmergencyEvidenceFresh for the named officer.",
        "PERMIT requires all three of EmergencyEvent, EmergencyOfficerAuthorityValid and EmergencyEvidenceFresh; indeterminate or absent evidence fails. This is a confined exception predicate (spec D6): it is never evaluated as, and never becomes, a prerequisite of the ordinary transfer gate ACS-D01-01.",
        "Establishes that a validly authorized emergency officer exercised the confined emergency exception under fresh evidence of an active emergency. It does not establish that declaring the emergency itself was substantively correct.",
        policy_id,
        extra=extra,
    )


def build_dispositions_ccs0():
    return [
        {"risk_id": "D-01", "status": "runtime", "acs_ids": ["ACS-D01-01"]},
        {
            "risk_id": "D-02", "status": "accepted",
            "scope": "Emergency-exception path is explicitly disabled under CCS0 (spec D2): any actual emergency request is routed to the declared manual governance process, never compiled as a runtime control.",
            "rationale": "emergency_exception_disabled; route=manual_governance_process (spec D2 example).",
            "acceptor": ACCOUNTABLE_EXEC, "approval_time": APPROVAL_TIME, "expiry": VALID_UNTIL,
        },
    ]


def build_dispositions_active():
    """CCS1/CCS2: both risks runtime."""
    return [
        {"risk_id": "D-01", "status": "runtime", "acs_ids": ["ACS-D01-01"]},
        {"risk_id": "D-02", "status": "runtime", "acs_ids": ["ACS-D02-01"]},
    ]


_SELECTION_RATIONALE = {
    "ACS-D01-01": "Dual authorization is a structural check over a signed registry artifact; T-DUAL-AUTH is the approved template. Ordinary path, present and decisive across every CCS variant.",
}

_SELECTION_RATIONALE_CCS1 = (
    "Emergency-exception structural check per T-EMERGENCY-AUTHORITY. J_D resolves the "
    "policy's undefined term 'authorized officer' to mean specifically the Treasury "
    "Officer credential (spec D5): authorized_actor = ['treasury.officer_on_duty']. "
    "Confined to the exception path per spec D6."
)
_SELECTION_RATIONALE_CCS2 = (
    "Emergency-exception structural check per T-EMERGENCY-AUTHORITY, re-selected under "
    "policy 4.3 / new judgment J' (spec D9): the analyst + ETA-2 tier may now also "
    "exercise the confined emergency authority, up to the same $1,000,000 bound. This is "
    "a new, separately authorized widening -- not the unauthorized ad-hoc widening spec "
    "D7 rejects."
)


def _base_judgment(judgment_id, version, acs_records, selections, disposition_decisions, catalog_version="1.0"):
    approvals = [
        {"acs_id": acs["acs_id"], "approver": APPROVER, "approval_time": APPROVAL_TIME, "forum": FORUM}
        for acs in acs_records
    ]
    return {
        "judgment_id": judgment_id, "version": version,
        "assessment_ref": {"assessment_id": "ASSESSMENT-CASE-D", "binding_id": BINDING},
        "catalog_ref": {"catalog_id": "K-CASE-D", "version": catalog_version},
        "selections": selections, "disposition_decisions": disposition_decisions, "approvals": approvals,
    }


def build_judgment_ccs0(acs_records):
    selections = [{
        "selection_id": "JD-CCS0-SEL-001", "risk_id": "D-01", "acs_id": "ACS-D01-01",
        "event_type": "dual_authorization_check", "template_id": "T-DUAL-AUTH",
        "selected_by": "business.head_treasury_operations", "selection_time": "2026-03-02T15:00:00Z",
        "rationale": _SELECTION_RATIONALE["ACS-D01-01"],
    }]
    decisions = [
        {"risk_id": "D-01", "status": "runtime", "decided_by": "business.head_treasury_operations",
         "decision_time": "2026-03-02T15:00:00Z",
         "rationale": "The risk has an approved catalog observable evaluable at authorization time on the sole authorized external action path."},
        {"risk_id": "D-02", "status": "accepted", "decided_by": ACCOUNTABLE_EXEC,
         "decision_time": "2026-03-02T15:00:00Z",
         "rationale": "Emergency-exception path explicitly disabled (spec D2); residual risk accepted with an authorized non-runtime (manual governance process) treatment."},
    ]
    return _base_judgment("J-CASE-D-CCS0", "1.0", acs_records, selections, decisions)


def build_judgment_ccs1(acs_records):
    selections = [
        {
            "selection_id": "JD-CCS1-SEL-001", "risk_id": "D-01", "acs_id": "ACS-D01-01",
            "event_type": "dual_authorization_check", "template_id": "T-DUAL-AUTH",
            "selected_by": "business.head_treasury_operations", "selection_time": "2026-03-02T15:00:00Z",
            "rationale": _SELECTION_RATIONALE["ACS-D01-01"],
        },
        {
            "selection_id": "JD-CCS1-SEL-002", "risk_id": "D-02", "acs_id": "ACS-D02-01",
            "event_type": "emergency_officer_authority_check", "template_id": "T-EMERGENCY-AUTHORITY",
            "selected_by": APPROVER, "selection_time": "2026-03-02T15:05:00Z",
            "rationale": _SELECTION_RATIONALE_CCS1,
        },
    ]
    decisions = [
        {"risk_id": "D-01", "status": "runtime", "decided_by": "business.head_treasury_operations",
         "decision_time": "2026-03-02T15:00:00Z",
         "rationale": "The risk has an approved catalog observable evaluable at authorization time on the sole authorized external action path."},
        {"risk_id": "D-02", "status": "runtime", "decided_by": APPROVER,
         "decision_time": "2026-03-02T15:05:00Z",
         "rationale": "Emergency-exception path enabled and confined per spec D5/D6; J_D resolves 'authorized officer' to the Treasury Officer credential."},
    ]
    return _base_judgment("J-CASE-D-CCS1", "1.1", acs_records, selections, decisions)


def build_judgment_ccs2(acs_records):
    selections = [
        {
            "selection_id": "JD-CCS2-SEL-001", "risk_id": "D-01", "acs_id": "ACS-D01-01",
            "event_type": "dual_authorization_check", "template_id": "T-DUAL-AUTH",
            "selected_by": "business.head_treasury_operations", "selection_time": "2026-03-02T15:00:00Z",
            "rationale": _SELECTION_RATIONALE["ACS-D01-01"],
        },
        {
            "selection_id": "JD-CCS2-SEL-002", "risk_id": "D-02", "acs_id": "ACS-D02-01",
            "event_type": "emergency_officer_authority_check", "template_id": "T-EMERGENCY-AUTHORITY",
            "selected_by": APPROVER, "selection_time": "2026-03-09T15:05:00Z",
            "rationale": _SELECTION_RATIONALE_CCS2,
        },
    ]
    decisions = [
        {"risk_id": "D-01", "status": "runtime", "decided_by": "business.head_treasury_operations",
         "decision_time": "2026-03-02T15:00:00Z",
         "rationale": "The risk has an approved catalog observable evaluable at authorization time on the sole authorized external action path."},
        {"risk_id": "D-02", "status": "runtime", "decided_by": APPROVER,
         "decision_time": "2026-03-09T15:05:00Z",
         "rationale": "Emergency-exception path widened under policy 4.3 / new judgment J' (spec D9): the analyst + ETA-2 tier may now also exercise the confined emergency authority."},
    ]
    return _base_judgment("J-CASE-D-CCS2", "1.2", acs_records, selections, decisions)
