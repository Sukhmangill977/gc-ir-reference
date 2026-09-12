"""Case C control layer: catalog K_C, threshold contracts, ACS set, judgment
record, dispositions, C*_cp profile, and policy metadata.

Thirteen of sixteen rows receive runtime dispositions; three (C-06, C-07,
C-16) receive non-runtime dispositions (RC-06 x2, RC-03 x1). Seven runtime
rows are C*_cp-classified (C-01, C-02, C-03, C-04, C-05, C-09, C-12); five are
mandatory by other approved policy (C-08, C-10, C-13, C-14, C-15); one is
advisory (C-11). See tools/case_c_data.py's module docstring for the scope
reduction this generation applies relative to the manuscript's full Tables
V-VI predicate sketches.
"""

from .case_c_data import (
    ACTIVATE_INSTRUMENT,
    APPROVAL_TIME,
    APPROVER,
    ASSISTANT,
    BINDING,
    DELEGATE,
    ENERGY_ACTIVATE,
    ENTER_AUTONOMOUS_SUBTASK,
    EXPORT_DATA,
    FORUM,
    PRESENT_GUIDANCE,
    TRANSFER_CONTROL,
    VALID_UNTIL,
)

OWNER_SURGICAL = "business.surgical_program_office"
OWNER_PLATFORM = "technology.surgical_robotics_platform"
OWNER_SAFETY = "compliance.surgical_safety_desk"

VALIDITY = {"effective_from": "2026-03-01T00:00:00Z", "effective_until": VALID_UNTIL}


def _triple(tuple_):
    return {k: [v] for k, v in tuple_.items()}


def _entry(event_type, template_id, observable_class, producers, operators,
           value_schema, basis, schema_id, fields, action_tuple, responses=("SAFE_STATE",), notes=""):
    return {
        "event_type": event_type, "template_id": template_id,
        "observable_class": observable_class, "allowed_producers": producers,
        "triple_template": _triple(action_tuple), "allowed_operators": operators,
        "value_schema": value_schema, "evaluation_basis": basis,
        "evidence_schema": {"schema_id": schema_id, "fields": fields},
        "permitted_responses": list(responses), "notes": notes,
    }


CATALOG_ENTRIES = [
    _entry("contraindication_check", "T-CONTRAINDICATION", "instrument_procedure_contraindication",
           ["ifu_contraindication_table_v3"], ["=="], {"type": "boolean"}, "deterministic_lookup",
           "ES-CONTRAINDICATION", ["procedure_class", "instrument_class", "task", "table_version"], ACTIVATE_INSTRUMENT),
    _entry("state_binding_check", "T-STATE-BINDING", "world_state_digest_match",
           ["state_binding_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-STATE-BINDING", ["procedure_step", "instrument_id", "port_configuration", "digest_at_authorization", "digest_at_boundary"], ENERGY_ACTIVATE),
    _entry("supervisory_authority_check", "T-SUPERVISORY-AUTHORITY", "supervisor_authority_state",
           ["control_token_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-SUPERVISORY-AUTHORITY", ["supervisor_id", "procedure_class", "control_token_owner", "autonomy_mode"], ENTER_AUTONOMOUS_SUBTASK),
    _entry("concurrence_check", "T-TRANSFER-CONCURRENCE", "control_transfer_concurrence_state",
           ["console_attestation_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-TRANSFER-CONCURRENCE", ["releasing_actor", "receiving_actor", "attestation_count"], TRANSFER_CONTROL),
    _entry("actor_scope_check", "T-ACTOR-SCOPE", "actor_scope_revocation_state",
           ["registry_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-ACTOR-SCOPE", ["actor_id", "action_tuple", "revocation_effective_time"], ACTIVATE_INSTRUMENT),
    _entry("guidance_contraindication_check", "T-GUIDANCE-CONTRAINDICATION", "guidance_contraindication_state",
           ["ifu_contraindication_table_v3"], ["=="], {"type": "boolean"}, "deterministic_lookup",
           "ES-GUIDANCE-CONTRAINDICATION", ["guidance_class", "procedure_class", "context_snapshot_age_seconds"], PRESENT_GUIDANCE),
    _entry("consent_scope_check", "T-CONSENT-SCOPE", "consent_artifact_state",
           ["consent_registry_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-CONSENT-SCOPE", ["data_class", "destination", "purpose", "attester"], EXPORT_DATA),
    _entry("model_validity_check", "T-MODEL-VALIDITY", "model_validation_state",
           ["model_registry_service_v1"], ["=="], {"type": "boolean"}, "deterministic_lookup",
           "ES-MODEL-VALIDITY", ["model_id", "procedure_class", "model_version"], PRESENT_GUIDANCE),
    _entry("attestation_dwell_check", "T-ATTESTATION-DWELL", "attestation_dwell_state",
           ["attestation_telemetry_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-ATTESTATION-DWELL", ["step_class", "dwell_seconds"], PRESENT_GUIDANCE, responses=("WARN",)),
    _entry("delegation_containment_check", "T-DELEGATION-CONTAINMENT", "delegation_containment_state",
           ["delegation_registry_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-DELEGATION-CONTAINMENT", ["parent_permit_id", "child_scope", "child_validity", "child_actions"], DELEGATE),
    _entry("snapshot_provenance_check", "T-SNAPSHOT-PROVENANCE", "snapshot_provenance_state",
           ["context_snapshot_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-SNAPSHOT-PROVENANCE", ["patient_id", "scheduled_patient_id", "snapshot_age_seconds", "lineage_hash_chain_valid"], ENTER_AUTONOMOUS_SUBTASK),
    _entry("latency_watchdog_check", "T-LATENCY-WATCHDOG", "evaluation_completion_state",
           ["deadline_watchdog_service_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-LATENCY-WATCHDOG", ["evaluation_id", "completed_within_bound"], ENTER_AUTONOMOUS_SUBTASK),
    _entry("safety_correlation_check", "T-SAFETY-CORRELATION", "safety_event_correlation_state",
           ["safety_event_registry_v1"], ["=="], {"type": "boolean"}, "structural_check",
           "ES-SAFETY-CORRELATION", ["intervention_id", "correlated_safety_event_id", "recorded_within_window"], ACTIVATE_INSTRUMENT),
]

CATALOG = {
    "catalog_id": "K-CASE-C", "version": "1.0", "version_binding_ref": BINDING,
    "approved_by": FORUM, "approval_time": APPROVAL_TIME, "entries": CATALOG_ENTRIES,
}

THRESHOLD_CONTRACTS = {}


def _acs(acs_id, gcir_id, risk_id, obligations, event_type, template_id,
         observable_id, observable_class, producer, evidence_schema_ref,
         attribute, operator, expected, basis, escalation_route, escalation_sla,
         evidence_reqs, action_tuple, owner, evidence_semantics, decision_semantics,
         warrant_boundary, gate_candidate="mandatory", soft_gate_type=None,
         policy_id=None, v11=None, on_fail="SAFE_STATE"):
    record = {
        "acs_id": acs_id, "gcir_id": gcir_id, "risk_id": risk_id, "obligation_refs": obligations,
        "event_type": event_type, "template_id": template_id,
        "observable_id": observable_id, "observable_class": observable_class,
        "observable_producer": producer,
        "evidence_source": "%s signed artifact" % producer,
        "evidence_schema_ref": evidence_schema_ref,
        "subject": action_tuple["subject"], "action": action_tuple["action"],
        "resource": action_tuple["resource"], "destination": action_tuple["destination"],
        "action_parameters": dict(_ACTION_PARAMETERS[action_tuple["action"]]),
        "parameter_schema_ref": _PARAM_SCHEMA_REF[action_tuple["action"]],
        "operator": operator, "expected_value": expected,
        "temporal_window": None, "evaluation_basis": basis,
        "threshold_contract_ref": None,
        "on_unknown": "fail", "on_fail": on_fail,
        "gate_candidate": gate_candidate,
        "mandatory_role": "decisive" if gate_candidate == "mandatory" else "supporting",
        "escalation": {"route": escalation_route, "sla_hours": escalation_sla},
        "evidence_requirements": evidence_reqs,
        "context_conditions": [
            {
                "attribute": attribute, "operator": operator, "value": expected,
                "unit": None, "on_unknown": "fail", "required": True,
                "evidence_producer": producer, "evidence_schema_ref": evidence_schema_ref,
                "threshold_contract_ref": None, "temporal_window": None,
            }
        ],
        "control_owner": owner, "approver": APPROVER, "approval_time": APPROVAL_TIME,
        "validity_interval": dict(VALIDITY), "version_binding_ref": BINDING,
        "evidence_semantics": evidence_semantics, "decision_semantics": decision_semantics,
        "warrant_boundary": warrant_boundary,
        "policy_id": policy_id,
    }
    if soft_gate_type:
        record["soft_gate_type"] = soft_gate_type
    if v11:
        record.update(v11)
    return record


_PARAM_SCHEMA_REF = {
    "activate_instrument": "PS-ACTIVATE-INSTRUMENT",
    "energy_activate": "PS-ENERGY-ACTIVATE",
    "enter_autonomous_subtask": "PS-ENTER-SUBTASK",
    "transfer_control": "PS-TRANSFER-CONTROL",
    "delegate": "PS-DELEGATE",
    "present_guidance": "PS-PRESENT-GUIDANCE",
    "export_data": "PS-EXPORT-DATA",
}

_ACTION_PARAMETERS = {
    "activate_instrument": {"procedure_step": "step_6", "instrument_id": "INSTR-001"},
    "energy_activate": {"port_configuration": "config_A"},
    "enter_autonomous_subtask": {"procedure_step": "step_6"},
    "transfer_control": {"releasing_actor": "surgeon.primary", "receiving_actor": "surgeon.second"},
    "delegate": {"parent_permit_id": "PARENT-SUBTASK-PERMIT"},
    "present_guidance": {"guidance_class": "phase_detection"},
    "export_data": {"data_class": "video"},
}


def build_acs_records():
    return [
        _acs("ACS-C01-01", "GCIR-C0001", "C-01", ["IFU-CONTRAINDICATION"],
             "contraindication_check", "T-CONTRAINDICATION", "contraindication_absent",
             "instrument_procedure_contraindication", "ifu_contraindication_table_v3", "ES-CONTRAINDICATION",
             "contraindication_absent", "==", True, "deterministic_lookup", "surgical_safety_urgent", 1,
             ["procedure_class", "instrument_class", "task", "table_version"], ACTIVATE_INSTRUMENT,
             OWNER_SAFETY,
             "A versioned IFU contraindication table lookup over (procedure_class, instrument_class, task).",
             "PERMIT requires the triple to be absent from the approved contraindication table; indeterminate or absent evidence fails.",
             "Establishes the triple is not on the approved contraindication list. It does not establish trajectory or force safety.",
             policy_id="POL-C-CONTRAINDICATION",
             v11={"enforcement_phase": "PRE_AUTHORIZATION"}),
        _acs("ACS-C02-01", "GCIR-C0002", "C-02", [],
             "state_binding_check", "T-STATE-BINDING", "state_digest_match",
             "world_state_digest_match", "state_binding_service_v1", "ES-STATE-BINDING",
             "state_digest_match", "==", True, "structural_check", "surgical_safety_urgent", 1,
             ["procedure_step", "instrument_id", "port_configuration", "digest_at_authorization", "digest_at_boundary"], ENERGY_ACTIVATE,
             OWNER_PLATFORM,
             "A world-state digest computed over (procedure_step, instrument_id, port_configuration) at authorization and recomputed at the boundary.",
             "PERMIT requires the boundary digest to equal the authorization digest; a mismatch is HOLD (INV-STATE-BINDING), never a silent permit.",
             "Establishes the world state has not changed since authorization. It does not establish the delivered energy is clinically appropriate.",
             policy_id="POL-C-ENERGY",
             v11={"enforcement_phase": "PRE_AUTHORIZATION",
                  "state_binding": {"attributes": ["procedure_step", "instrument_id", "port_configuration"]}}),
        _acs("ACS-C03-01", "GCIR-C0003", "C-03", [],
             "supervisory_authority_check", "T-SUPERVISORY-AUTHORITY", "supervisor_authorized",
             "supervisor_authority_state", "control_token_service_v1", "ES-SUPERVISORY-AUTHORITY",
             "supervisor_authorized", "==", True, "structural_check", "surgical_safety_urgent", 1,
             ["supervisor_id", "procedure_class", "control_token_owner", "autonomy_mode"], ENTER_AUTONOMOUS_SUBTASK,
             OWNER_SAFETY,
             "A signed control-token artifact reporting the authenticated supervisor, procedure-class privileging, token ownership, and autonomy mode.",
             "PERMIT requires an authenticated, privileged, token-holding supervisor in SUPERVISED mode; indeterminate or absent evidence fails.",
             "Establishes an identifiable supervising surgeon holds authority for this subtask. It does not establish the surgeon is attentive (see C-16).",
             policy_id="POL-C-AUTONOMY"),
        _acs("ACS-C04-01", "GCIR-C0004", "C-04", [],
             "concurrence_check", "T-TRANSFER-CONCURRENCE", "concurrence_satisfied",
             "control_transfer_concurrence_state", "console_attestation_service_v1", "ES-TRANSFER-CONCURRENCE",
             "concurrence_satisfied", "==", True, "structural_check", "surgical_safety_urgent", 1,
             ["releasing_actor", "receiving_actor", "attestation_count"], TRANSFER_CONTROL,
             OWNER_SAFETY,
             "A signed console-attestation artifact reporting distinct releasing and receiving actor attestations.",
             "PERMIT requires 2-of-2 concurrence within the declared window; expiry with fewer than 2 attestations is DENY, never a timeout.",
             "Establishes both parties attested to the transfer. It does not establish either party reviewed the handoff substantively.",
             policy_id="POL-C-TRANSFER",
             v11={"enforcement_phase": "PRE_AUTHORIZATION",
                  "concurrence_policy": {"n_required": 2, "m_eligible": ["privileged_surgeon"], "window_seconds": 300, "expiry_response": "DENY"}}),
        _acs("ACS-C05-01", "GCIR-C0005", "C-05", [],
             "actor_scope_check", "T-ACTOR-SCOPE", "actor_scope_not_revoked",
             "actor_scope_revocation_state", "registry_service_v1", "ES-ACTOR-SCOPE",
             "actor_scope_not_revoked", "==", True, "structural_check", "surgical_safety_urgent", 1,
             ["actor_id", "action_tuple", "revocation_effective_time"], ACTIVATE_INSTRUMENT,
             OWNER_SAFETY,
             "A signed registry lookup reporting whether the proposing actor's scope over this action tuple has been revoked (auxiliary check A1).",
             "PERMIT requires no effective ActorScopeRevocation covers this actor and action tuple at authorization time.",
             "Establishes the actor's scope was not revoked. It does not establish the actor was ever competent to hold it.",
             policy_id="POL-C-REVOCATION"),
        _acs("ACS-C08-01", "GCIR-C0008", "C-08", ["IFU-CONTRAINDICATION"],
             "guidance_contraindication_check", "T-GUIDANCE-CONTRAINDICATION", "guidance_permitted",
             "guidance_contraindication_state", "ifu_contraindication_table_v3", "ES-GUIDANCE-CONTRAINDICATION",
             "guidance_permitted", "==", True, "deterministic_lookup", "surgical_safety_desk", 4,
             ["guidance_class", "procedure_class", "context_snapshot_age_seconds"], PRESENT_GUIDANCE,
             OWNER_SAFETY,
             "A structural check that the guidance class is not contraindicated for this procedure class and the context snapshot is not stale.",
             "PERMIT requires the guidance class to be absent from the contraindication table for this procedure class, on a non-stale snapshot.",
             "Establishes the presented guidance is not contraindicated by class. It does not establish the guidance content is clinically correct.",
             policy_id="POL-C-GUIDANCE",
             v11={"enforcement_phase": "PRE_AUTHORIZATION", "response_policy": "REQUIRED"}),
        _acs("ACS-C09-01", "GCIR-C0009", "C-09", ["INST-CONSENT-SCOPE"],
             "consent_scope_check", "T-CONSENT-SCOPE", "consent_covers_export",
             "consent_artifact_state", "consent_registry_service_v1", "ES-CONSENT-SCOPE",
             "consent_covers_export", "==", True, "structural_check", "compliance_records_desk", 1,
             ["data_class", "destination", "purpose", "attester"], EXPORT_DATA,
             OWNER_SAFETY,
             "A signed consent artifact covering (data_class, destination, purpose), attested by the circulating nurse.",
             "PERMIT requires the signed consent artifact to cover the proposed export tuple; indeterminate or absent evidence fails.",
             "Establishes the export is within the recorded consent scope. It does not establish the consent itself was properly obtained.",
             policy_id="POL-C-CONSENT"),
        _acs("ACS-C10-01", "GCIR-C0010", "C-10", [],
             "model_validity_check", "T-MODEL-VALIDITY", "model_validated_for_procedure",
             "model_validation_state", "model_registry_service_v1", "ES-MODEL-VALIDITY",
             "model_validated_for_procedure", "==", True, "deterministic_lookup", "surgical_safety_desk", 4,
             ["model_id", "procedure_class", "model_version"], PRESENT_GUIDANCE,
             OWNER_PLATFORM,
             "A signed model-registry lookup reporting whether the consulted model is validated for this procedure class and matches M.version_binding.",
             "PERMIT requires the model id to resolve in the validated-models registry for this procedure class at the bound model version.",
             "Establishes the model was validated for this use. It does not establish the model's output is clinically correct.",
             policy_id="POL-C-MODEL"),
        _acs("ACS-C11-01", "GCIR-C0011", "C-11", [],
             "attestation_dwell_check", "T-ATTESTATION-DWELL", "dwell_within_band",
             "attestation_dwell_state", "attestation_telemetry_service_v1", "ES-ATTESTATION-DWELL",
             "dwell_within_band", "==", True, "structural_check", "surgical_safety_desk", 24,
             ["step_class", "dwell_seconds"], PRESENT_GUIDANCE,
             OWNER_SAFETY,
             "Deterministic telemetry proxy for substantive review: per-step attestation dwell time for pre-authorized step classes.",
             "A dwell outside the approved band raises an advisory monitoring signal; it does not itself deny authorization.",
             "Establishes a proxy for review substance. It does not establish the surgeon's attention was actually engaged.",
             gate_candidate="advisory", soft_gate_type="advisory",
             policy_id="POL-C-MONITORING", on_fail="WARN"),
        _acs("ACS-C12-01", "GCIR-C0012", "C-12", [],
             "delegation_containment_check", "T-DELEGATION-CONTAINMENT", "child_strictly_contained",
             "delegation_containment_state", "delegation_registry_service_v1", "ES-DELEGATION-CONTAINMENT",
             "child_strictly_contained", "==", True, "structural_check", "surgical_safety_urgent", 1,
             ["parent_permit_id", "child_scope", "child_validity", "child_actions"], DELEGATE,
             OWNER_SAFETY,
             "A signed delegation-registry check that the child permit's (scope, validity, actions) is strictly contained in its parent's (auxiliary check A3, INV-DELEGATION-NARROWING).",
             "PERMIT requires strict containment on every component and inequality on at least one; an identical or wider child is DENY.",
             "Establishes the child permit narrows its parent. It does not establish the parent permit itself was properly authorized.",
             policy_id="POL-C-DELEGATION",
             v11={"enforcement_phase": "PRE_AUTHORIZATION", "delegation": {"parent_permit_class_id": "PARENT-SUBTASK-PERMIT"}}),
        _acs("ACS-C13-01", "GCIR-C0013", "C-13", [],
             "snapshot_provenance_check", "T-SNAPSHOT-PROVENANCE", "snapshot_valid",
             "snapshot_provenance_state", "context_snapshot_service_v1", "ES-SNAPSHOT-PROVENANCE",
             "snapshot_valid", "==", True, "structural_check", "surgical_safety_urgent", 1,
             ["patient_id", "scheduled_patient_id", "snapshot_age_seconds", "lineage_hash_chain_valid"], ENTER_AUTONOMOUS_SUBTASK,
             OWNER_PLATFORM,
             "A signed context-snapshot artifact reporting patient-identity match, freshness, and an unbroken lineage hash chain.",
             "PERMIT requires patient_id == scheduled patient, snapshot within its declared freshness bound, and a verified lineage chain.",
             "Establishes the snapshot's identity, freshness and lineage. It propagates to C-03 via input_provenance; it does not itself establish the autonomous proposal is clinically correct.",
             policy_id="POL-C-SNAPSHOT"),
        _acs("ACS-C14-01", "GCIR-C0014", "C-14", [],
             "latency_watchdog_check", "T-LATENCY-WATCHDOG", "evaluation_completed_within_bound",
             "evaluation_completion_state", "deadline_watchdog_service_v1", "ES-LATENCY-WATCHDOG",
             "evaluation_completed_within_bound", "==", True, "structural_check", "technology_change_management", 1,
             ["evaluation_id", "completed_within_bound"], ENTER_AUTONOMOUS_SUBTASK,
             OWNER_PLATFORM,
             "An independent deadline watchdog, outside the evaluator it supervises, reporting whether evaluation completed within evaluation_latency_bound.",
             "Expiry of the bound is HOLD (on_evaluation_timeout), never a partial permit; this is the governance row over INV-LATENCY, as R-11/B-06 sit over their coinciding invariants.",
             "Establishes the evaluator signaled completion in time. It does not establish the evaluation's substantive correctness.",
             policy_id="POL-C-LATENCY",
             v11={"enforcement_phase": "PRE_AUTHORIZATION",
                  "evaluation_latency_bound": {"value": 300, "unit": "ms"}, "on_evaluation_timeout": "HOLD"}),
        _acs("ACS-C15-01", "GCIR-C0015", "C-15", [],
             "safety_correlation_check", "T-SAFETY-CORRELATION", "intervention_correlated",
             "safety_event_correlation_state", "safety_event_registry_v1", "ES-SAFETY-CORRELATION",
             "intervention_correlated", "==", True, "structural_check", "incident_review_board", 24,
             ["intervention_id", "correlated_safety_event_id", "recorded_within_window"], ACTIVATE_INSTRUMENT,
             OWNER_SAFETY,
             "A signed safety-event registry check (auxiliary check A2) that every declared safety-layer intervention is correlated to a SafetyEvent within its recording window.",
             "A missing correlation places HOLD on the next ordinary authorization in the affected scope (POST_EVENT_AUDIT); it never gates the intervention itself.",
             "Establishes recovery evidence completeness. It does not establish the safety layer's own correctness or certification.",
             policy_id="POL-C-SAFETY-EVIDENCE",
             v11={"enforcement_phase": "POST_EVENT_AUDIT"}),
    ]


RUNTIME_ACS = {
    "C-01": ["ACS-C01-01"], "C-02": ["ACS-C02-01"], "C-03": ["ACS-C03-01"],
    "C-04": ["ACS-C04-01"], "C-05": ["ACS-C05-01"], "C-08": ["ACS-C08-01"],
    "C-09": ["ACS-C09-01"], "C-10": ["ACS-C10-01"], "C-11": ["ACS-C11-01"],
    "C-12": ["ACS-C12-01"], "C-13": ["ACS-C13-01"], "C-14": ["ACS-C14-01"],
    "C-15": ["ACS-C15-01"],
}

_NONRUNTIME = {
    "C-06": ("RC-06", "runtime_safety", "force_envelope safety layer (IEC 80601-2-77)"),
    "C-07": ("RC-06", "runtime_safety", "instrument_interlock safety layer (IEC 80601-2-77)"),
    "C-16": ("RC-03", "human_process", "scheduling and relief policy"),
}


def build_dispositions():
    records = [
        {"risk_id": rid, "status": "runtime", "acs_ids": list(acs_ids)}
        for rid, acs_ids in sorted(RUNTIME_ACS.items())
    ]
    for rid, (reason_code, family, control_ref) in sorted(_NONRUNTIME.items()):
        records.append({
            "risk_id": rid, "status": "nonruntime", "reason_code": reason_code,
            "routed_to_control_family": family, "control_ref": control_ref,
            "owner": OWNER_SAFETY,
            "approval": {"approver": APPROVER, "approval_time": APPROVAL_TIME, "forum": FORUM},
        })
    return records


_SELECTION_RATIONALE_C = {
    "ACS-C01-01": "Contraindication is a deterministic lookup against a versioned IFU table; T-CONTRAINDICATION selected.",
    "ACS-C02-01": "World-state binding requires a digest comparison at the boundary; T-STATE-BINDING selected (schema v1.1 state_binding).",
    "ACS-C03-01": "Supervisory authority is a structural check over a signed control-token artifact; T-SUPERVISORY-AUTHORITY selected.",
    "ACS-C04-01": "Control transfer requires 2-of-2 concurrence; T-TRANSFER-CONCURRENCE selected (schema v1.1 concurrence_policy).",
    "ACS-C05-01": "Actor-scope revocation is a structural registry check; T-ACTOR-SCOPE selected (exercised by auxiliary check A1).",
    "ACS-C08-01": "Guidance contraindication and staleness is a deterministic lookup plus freshness check; T-GUIDANCE-CONTRAINDICATION selected, response_policy=REQUIRED for the HumanResponse record.",
    "ACS-C09-01": "Consent scope is a structural check over a signed consent artifact; T-CONSENT-SCOPE selected.",
    "ACS-C10-01": "Model validity for procedure class is a deterministic registry lookup; T-MODEL-VALIDITY selected.",
    "ACS-C11-01": "Attestation dwell is a deterministic telemetry proxy, advisory only; T-ATTESTATION-DWELL selected.",
    "ACS-C12-01": "Delegation containment is a structural registry check; T-DELEGATION-CONTAINMENT selected (exercised by auxiliary check A3).",
    "ACS-C13-01": "Snapshot identity/freshness/lineage is a structural check; T-SNAPSHOT-PROVENANCE selected.",
    "ACS-C14-01": "Evaluation completion is watched by an independent deadline watchdog; T-LATENCY-WATCHDOG selected (schema v1.1 evaluation_latency_bound).",
    "ACS-C15-01": "Safety-event correlation is a post-event structural check; T-SAFETY-CORRELATION selected (schema v1.1 enforcement_phase=POST_EVENT_AUDIT, exercised by auxiliary check A2).",
}

SELECTORS_C = {"ACS-C09-01": "compliance.head_records"}
DEFAULT_SELECTOR_C = "business.head_surgical_program"


def build_judgment_record(acs_records):
    selections, approvals, decisions = [], [], []
    for index, acs in enumerate(acs_records, start=1):
        selector = SELECTORS_C.get(acs["acs_id"], DEFAULT_SELECTOR_C)
        selections.append({
            "selection_id": "JC-SEL-%03d" % index, "risk_id": acs["risk_id"],
            "acs_id": acs["acs_id"], "event_type": acs["event_type"], "template_id": acs["template_id"],
            "selected_by": selector, "selection_time": "2026-02-08T10:00:00Z",
            "rationale": _SELECTION_RATIONALE_C[acs["acs_id"]],
        })
        approvals.append({"acs_id": acs["acs_id"], "approver": APPROVER, "approval_time": APPROVAL_TIME, "forum": FORUM})
        decisions.append({
            "risk_id": acs["risk_id"], "status": "runtime", "decided_by": selector,
            "decision_time": "2026-02-08T10:00:00Z",
            "rationale": "The risk has an approved catalog observable evaluable at authorization time on the sole authorized action path.",
        })
    for rid, (reason_code, family, _ref) in sorted(_NONRUNTIME.items()):
        decisions.append({
            "risk_id": rid, "status": "nonruntime", "decided_by": DEFAULT_SELECTOR_C,
            "decision_time": "2026-02-08T10:00:00Z",
            "rationale": "%s: %s" % (reason_code, family),
        })
    decisions.sort(key=lambda d: d["risk_id"])
    return {
        "judgment_id": "J-CASE-C", "version": "1.0",
        "assessment_ref": {"assessment_id": "ASSESSMENT-CASE-C", "binding_id": BINDING},
        "catalog_ref": {"catalog_id": "K-CASE-C", "version": "1.0"},
        "selections": selections, "disposition_decisions": decisions, "approvals": approvals,
    }


def _rule(authority, rationale, min_materiality, description, required_reversibility=None):
    rule = {
        "approving_authority": authority, "rationale": rationale,
        "materiality_boundary": {"minimum_materiality": min_materiality, "description": description},
        "effective_date": APPROVAL_TIME, "emergency_override_procedure": None,
    }
    if required_reversibility is not None:
        rule["required_reversibility"] = list(required_reversibility)
    return rule


CSTAR_PROFILE = {
    "profile_id": "CSTAR-C", "version": "1.0", "version_binding_ref": BINDING,
    "approved_by": FORUM, "approval_time": APPROVAL_TIME,
    "materiality_order": ["immaterial", "minor", "material", "severe"],
    "member_kinds": [
        "material_statutory_prohibition", "unauthorized_authority_exercise",
        "material_information_barrier_breach", "irreversible_external_effect_above_approved_bound",
        "physical_harm_to_person", "accountability_transfer", "protected_data_disclosure_outside_consent_scope",
    ],
    "classification_rules": {
        "material_statutory_prohibition": _rule("exec.head_of_surgical_platform", "Retained from the base profile; not exercised by this register.", "material", "Not exercised by this register."),
        "unauthorized_authority_exercise": _rule("exec.head_of_surgical_platform", "Actuation or autonomous subtask entry without identifiable supervisory authority is the system exercising authority it does not hold.", "material", "An unauthorized act with no external effect is below the boundary."),
        "material_information_barrier_breach": _rule("exec.head_of_surgical_platform", "Retained from the base profile; not exercised by this register.", "material", "Not exercised by this register."),
        "irreversible_external_effect_above_approved_bound": _rule("exec.head_of_surgical_platform", "Retained from the base profile; not exercised by this register.", "material", "Not exercised by this register."),
        "physical_harm_to_person": _rule(
            "exec.head_of_surgical_platform",
            "Physical harm to a patient arising from a mediated transition (instrument activation, energy delivery) that is not self-limiting.",
            "material",
            "Reversibility-qualified per Section VII-A: harm that is self-limiting and requires no intervention does not enter C* on its class alone. Enforced directly by gcir.coverage.CStarProfile.evaluate()'s required_reversibility check, not by a materiality workaround.",
            required_reversibility=["irreversible", "requires_intervention"],
        ),
        "accountability_transfer": _rule("exec.head_of_surgical_platform", "A transition that changes who is answerable for the system's next consequential act -- control handoff or delegation to autonomy.", "material", "A transfer with full symmetric attestation and no scope widening is still material at proposal time; materiality governs, not outcome."),
        "protected_data_disclosure_outside_consent_scope": _rule("exec.head_of_surgical_platform", "Intraoperative video/telemetry export outside the recorded consent scope.", "material", "Export within consent scope is below the boundary by definition, not by materiality."),
    },
}

POLICY_METADATA = {
    "bundle_id": "BUNDLE-CASE-C-1.0", "precedence": {},
    "precedence_relation": ["mandatory_failure", "mandatory_pass", "weighted_or_advisory"],
    "aggregation_groups": {},
    "runtime_acceptance_condition": (
        "A conformant consuming runtime loads only bundles verifying as signed Phi "
        "outputs (signature, payload hash, lifecycle-registry state), accepts no "
        "policy content through any other channel, and emits decision receipts "
        "carrying the requirement reference of every evaluated predicate."
    ),
}
