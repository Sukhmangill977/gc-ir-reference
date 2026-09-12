"""Case C -- supervised-autonomy surgical assistant (manuscript Section XI).

EVIDENCE CLASS: synthetic, standards-anchored design case, now COMPILED for
the first time in this generation.  Prior generations of this repository
deliberately treated Case C as a design/theoretical case and did not compile
it (see docs/CASE_C_STATUS.md for the full boundary statement) -- no vendor's
internal risk register, software, or telemetry is described, inferred, or
claimed here either; this is a synthetic register anchored to public
standards (ISO 14971, IEC 62304, IEC 80601-2-77), exercising the schema v1.1
mechanisms (state binding, concurrence, delegation, actor-scope revocation,
safety-event correlation, human response) this generation adds.

Scope reduction relative to the manuscript's Tables V-VI, stated plainly: each
compiled Approved Control Specification here carries ONE context condition
(the same granularity as every Case A/B ACS), not the full multi-clause
predicate sketch the manuscript prose describes for some rows (e.g. C-03's
seven-conjunct authority check).  The disposition, consequence
classification, gate source, and v1.1-mechanism assignment for all sixteen
rows match the manuscript's Tables V-VI exactly; the internal structure of
each compiled predicate is schematic, at the same fidelity Case A and Case B
already use.  This is a development artifact: it has not been through a
scientific freeze, and no CI-reported figure or manuscript claim should cite
its metrics as measured results without saying so explicitly.
"""

import hashlib

BINDING = "VB-CASE-C-1.0"
APPROVAL_TIME = "2026-02-10T14:00:00Z"
EFFECTIVE_FROM = "2026-03-01T00:00:00Z"
VALID_UNTIL = "2027-03-01T00:00:00Z"
COMPILE_TIME = "2026-03-02T09:00:00Z"

FORUM = "surgical_platform_governance_forum"
ACCOUNTABLE_EXEC = "exec.head_of_surgical_platform"
ASSESSOR = "governance.assessor_l_martins"
APPROVER = "forum.chair_surgical_safety"

ASSISTANT = "assistance_module"

ACTIVATE_INSTRUMENT = {"subject": ASSISTANT, "action": "activate_instrument", "resource": "surgical_instrument", "destination": "patient"}
ENERGY_ACTIVATE = {"subject": ASSISTANT, "action": "energy_activate", "resource": "energy_delivery_channel", "destination": "patient"}
ENTER_AUTONOMOUS_SUBTASK = {"subject": ASSISTANT, "action": "enter_autonomous_subtask", "resource": "subtask_permit", "destination": "procedure_field"}
TRANSFER_CONTROL = {"subject": ASSISTANT, "action": "transfer_control", "resource": "control_session", "destination": "console"}
DELEGATE = {"subject": ASSISTANT, "action": "delegate", "resource": "subtask_permit", "destination": "delegatee_actor"}
PRESENT_GUIDANCE = {"subject": ASSISTANT, "action": "present_guidance", "resource": "guidance_output", "destination": "surgeon_display"}
EXPORT_DATA = {"subject": ASSISTANT, "action": "export_data", "resource": "telemetry_data", "destination": "external_review_system"}

METADATA = {
    "system_id": "CASE-C-SUPERVISED-AUTONOMY-SURGICAL-ASSISTANT",
    "purpose": (
        "AI assistance module for a robotically assisted surgical platform, "
        "operating at the supervised-autonomy tier for bounded subtasks under "
        "an identifiable supervising surgeon. Synthetic, standards-anchored "
        "design case; no vendor system is described."
    ),
    "owner_business": "business.surgical_program_office",
    "owner_technical": "technology.surgical_robotics_platform",
    "accountable_exec": ACCOUNTABLE_EXEC,
    "assessor": ASSESSOR,
    "deployment": "research/design case, not a deployed clinical product",
    "scope": (
        "Supervised-autonomy assistance module: instrument activation, energy "
        "delivery, bounded autonomous subtasks, control transfer, delegation, "
        "guidance presentation, and telemetry export, each mediated by the "
        "runtime authority. Continuous force-scaling and envelope-keeping "
        "corrections are excluded (AD-1) and supervised by an independent "
        "safety layer."
    ),
    "exclusions": [
        "No trajectory or motion safety claim: the authorization gate decides whether a transition may be attempted, never whether the resulting motion is safe.",
        "No clinical efficacy or product-conformance claim.",
        "No certified safety-layer implementation is described; the safety layer is declared, not built.",
    ],
    "method": "NIST AI RMF 1.0 Map/Measure profile with ISO 31000 cause-event-consequence register, anchored to ISO 14971 / IEC 62304 / IEC 80601-2-77.",
    "version_binding": {
        "binding_id": BINDING,
        "model_version": "surgical-assistance-module-2026.02",
        "prompt_version": "not-applicable-non-generative",
        "dataset_version": "procedure-context-corpus-2026-02",
        "policy_version": "surgical-safety-policy-2026.1",
        "fingerprint": "sha256:7a1f0c6b4e832d915ac0e7f4d1b8c6a5e93f7028b1a4c6d9e5f0a3b7c2d8e416",
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
        "subject": ASSISTANT, "action": "activate_instrument", "resource": "surgical_instrument", "destination": "patient",
        "parameter_schema_id": "PS-ACTIVATE-INSTRUMENT",
        "parameter_schema": {"procedure_step": {"type": "string", "required": True}, "instrument_id": {"type": "string", "required": True}},
        "hazardous": True, "notes": "Contraindication and state-binding are checked before every activation.",
    },
    {
        "subject": ASSISTANT, "action": "energy_activate", "resource": "energy_delivery_channel", "destination": "patient",
        "parameter_schema_id": "PS-ENERGY-ACTIVATE",
        "parameter_schema": {"port_configuration": {"type": "string", "required": True}},
        "hazardous": True, "notes": "State-bound: a permit is valid only for the world state under which it was authorized.",
    },
    {
        "subject": ASSISTANT, "action": "enter_autonomous_subtask", "resource": "subtask_permit", "destination": "procedure_field",
        "parameter_schema_id": "PS-ENTER-SUBTASK",
        "parameter_schema": {"procedure_step": {"type": "string", "required": True}},
        "hazardous": True, "notes": "Supervised autonomy: never removes the surgeon from the loop.",
    },
    {
        "subject": ASSISTANT, "action": "transfer_control", "resource": "control_session", "destination": "console",
        "parameter_schema_id": "PS-TRANSFER-CONTROL",
        "parameter_schema": {"releasing_actor": {"type": "string", "required": True}, "receiving_actor": {"type": "string", "required": True}},
        "hazardous": True, "notes": "An accountability transfer; requires 2-of-2 concurrence.",
    },
    {
        "subject": ASSISTANT, "action": "delegate", "resource": "subtask_permit", "destination": "delegatee_actor",
        "parameter_schema_id": "PS-DELEGATE",
        "parameter_schema": {"parent_permit_id": {"type": "string", "required": True}},
        "hazardous": True, "notes": "Child permit strictly contained in its parent (INV-DELEGATION-NARROWING, checked by auxiliary A3).",
    },
    {
        "subject": ASSISTANT, "action": "present_guidance", "resource": "guidance_output", "destination": "surgeon_display",
        "parameter_schema_id": "PS-PRESENT-GUIDANCE",
        "parameter_schema": {"guidance_class": {"type": "string", "required": True}},
        "hazardous": False, "notes": "Advisory; response_policy governs HumanResponse capture, not a physical effect.",
    },
    {
        "subject": ASSISTANT, "action": "export_data", "resource": "telemetry_data", "destination": "external_review_system",
        "parameter_schema_id": "PS-EXPORT-DATA",
        "parameter_schema": {"data_class": {"type": "string", "required": True}},
        "hazardous": True, "notes": "Protected data disclosure; consent-scope structural check.",
    },
]

SYSTEM_PROFILE = {
    "capabilities": [
        "instrument activation and energy delivery proposal under supervision",
        "bounded autonomous subtask execution",
        "control transfer between consoles or into autonomy mode",
        "delegated subtask authority issuance",
        "intraoperative guidance presentation",
        "telemetry and video export for review",
    ],
    "data_classes": ["procedure context", "instrument and energy state", "intraoperative video/telemetry", "consent scope records"],
    "actors": ["supervising_surgeon", "second_surgeon", "circulating_nurse", ASSISTANT],
    "affected_parties": ["the patient", "the supervising surgeon", "the institution as a regulated entity"],
    "architecture": (
        "Proposed transition -> runtime authority (PERMIT/DENY/HOLD) -> evidence "
        "commit -> actuation, with an independent safety layer supervising the "
        "resulting motion at control-loop rate, outside the authorization gate."
    ),
    "scale": {"procedures_per_year": 4000, "unit": "count"},
    "autonomy_level": "supervised_autonomy",
    "authority_matrix": AUTHORITY_MATRIX,
    "safety_layers": [
        {"safety_layer_id": "force_envelope", "standards_basis": "IEC 80601-2-77", "safety_event_window_seconds": 5},
        {"safety_layer_id": "instrument_interlock", "standards_basis": "IEC 80601-2-77", "safety_event_window_seconds": 5},
    ],
    "control_loops": [
        {"control_loop_ref": "haptic_force_scaling_loop", "control_loop_period_ms": 2, "excluded_action_family": "force_scaling_correction"},
        {"control_loop_ref": "envelope_keeping_loop", "control_loop_period_ms": 5, "excluded_action_family": "envelope_keeping_correction"},
    ],
}


def _obligation(oid, source, clause, cls, basis, version):
    return {
        "obligation_id": oid,
        "source": source,
        "jurisdiction": "Canada",
        "territorial_basis": "institution operating the platform is domiciled in Canada",
        "clause_ref": clause,
        "requirement_text_hash": hashlib.sha256(
            ("REQUIREMENT-TEXT-FIXTURE::%s::%s" % (oid, clause)).encode("utf-8")
        ).hexdigest(),
        "applicability_basis": basis,
        "applicability_decision": "applicable",
        "decision_authority": "legal.regulatory_counsel",
        "decision_time": "2026-02-05T10:00:00Z",
        "effective_from": EFFECTIVE_FROM,
        "legal_source_version": version,
        "requirement_class": cls,
    }


OBLIGATIONS = [
    _obligation("ISO-14971-RISK", "ISO 14971:2019", "risk control and residual-risk requirements", "standards",
                ["robotically assisted surgical platform"], "ISO 14971:2019 (confirmed 2025)"),
    _obligation("IEC-62304-SW", "IEC 62304:2006+AMD1:2015", "software safety classification of the assistance module", "standards",
                ["software item of a medical device"], "IEC 62304:2006+AMD1:2015"),
    _obligation("IEC-80601-2-77-RASE", "IEC 80601-2-77:2019+AMD1:2023", "basic safety and essential performance of robotically assisted surgical equipment", "standards",
                ["robotically assisted surgical equipment"], "IEC 80601-2-77:2019+AMD1:2023"),
    _obligation("IFU-CONTRAINDICATION", "Manufacturer instructions for use", "contraindicated instrument-procedure combinations", "contractual",
                ["institution operates under the device's conditions of use"], "IFU-2026.1"),
    _obligation("INST-PRIVILEGING", "Institutional privileging and credentialing policy", "surgeon privileging by procedure class", "internal",
                ["all supervised-autonomy procedures"], "PRIV-2026.1"),
    _obligation("INST-CONSENT-SCOPE", "Institutional consent policy", "intraoperative video/telemetry consent scope", "internal",
                ["all recorded procedures"], "CONSENT-2026.1"),
]

# (risk_id, cause, event, consequence, obligation_refs, L_res, I_res,
#  consequence_class, descriptor kind, materiality, reversibility, action_tuple or None)
_RISKS = [
    ("C-01", "the module can propose activating an instrument class the IFU contraindicates for this task in this procedure class",
     "instrument of a contraindicated class is activated for a contraindicated task in a contraindicated procedure class",
     "physical harm requiring intervention", ["IFU-CONTRAINDICATION", "ISO-14971-RISK"], 2, 4,
     "physical_harm", "physical_harm_to_person", "material", "requires_intervention", ACTIVATE_INSTRUMENT),
    ("C-02", "the world state can change between authorization and the execution boundary",
     "ENERGY_ACTIVATE is proposed under a permit whose state digest no longer matches",
     "irreversible physical harm", ["ISO-14971-RISK"], 2, 5,
     "physical_harm", "physical_harm_to_person", "material", "irreversible", ENERGY_ACTIVATE),
    ("C-03", "an autonomous proposal can be issued without an authenticated, privileged, in-mode supervising surgeon",
     "a consequential autonomous actuation is proposed without identifiable authorized supervisory authority",
     "loss of accountable supervision over a consequential act", ["INST-PRIVILEGING"], 1, 5,
     "authority", "unauthorized_authority_exercise", "material", "irreversible", ENTER_AUTONOMOUS_SUBTASK),
    ("C-04", "a control handoff between consoles or into autonomy mode can be attempted with only one party attesting",
     "control transfer is proposed without both parties' attestation",
     "an accountability gap at the moment of transfer", ["INST-PRIVILEGING"], 2, 4,
     "accountability_transfer", "accountability_transfer", "material", "partially_reversible", TRANSFER_CONTROL),
    ("C-05", "authority can be withdrawn mid-procedure while a proposal is already in flight",
     "an actuation is proposed whose actor-scope carries an effective revocation",
     "actuation under withdrawn authority", ["INST-PRIVILEGING"], 1, 5,
     "authority", "unauthorized_authority_exercise", "material", "irreversible", ACTIVATE_INSTRUMENT),
    ("C-06", "a force-scaling correction is a feedback primitive of a declared control loop",
     "control-loop-rate correction exceeds the approved force bound",
     "excess tissue force, requiring intervention", ["IEC-80601-2-77-RASE"], 4, 4,
     "patient_harm", "physical_harm_to_person", "material", "requires_intervention", None),
    ("C-07", "an instrument can leave its geometric or force envelope during continuous supervision",
     "collision or envelope excursion",
     "patient harm requiring intervention", ["IEC-80601-2-77-RASE"], 3, 4,
     "patient_harm", "physical_harm_to_person", "material", "requires_intervention", None),
    ("C-08", "guidance can be generated from a stale context snapshot or for a contraindicated procedure class",
     "contraindicated or stale guidance is presented to the supervising surgeon",
     "reversible patient harm if followed", ["IFU-CONTRAINDICATION"], 3, 3,
     # Correctly excluded from C* by the real reversibility qualifier
     # (reversible harm does not enter physical_harm_to_person's C* membership
     # on its class alone -- Section VII-A), not by a materiality workaround.
     "patient_harm", "physical_harm_to_person", "material", "reversible", PRESENT_GUIDANCE),
    ("C-09", "intraoperative video/telemetry export is a transition with its own authority-matrix row",
     "data is exported to a destination or for a purpose not in the consent record",
     "protected data disclosure outside consent scope", ["INST-CONSENT-SCOPE"], 3, 4,
     "protected_data_disclosure", "protected_data_disclosure_outside_consent_scope", "material", "irreversible", EXPORT_DATA),
    ("C-10", "a model can be consulted outside the procedure class it was validated for",
     "recommendation or phase detection is produced by a model not validated for this procedure class",
     "reversible patient harm from an out-of-scope model", ["IEC-62304-SW"], 3, 3,
     # Correctly excluded from C* by the real reversibility qualifier.
     "patient_harm", "physical_harm_to_person", "material", "reversible", PRESENT_GUIDANCE),
    ("C-11", "pre-authorized routine steps under a standing permit can still accumulate unattended attestation",
     "per-step attestation dwell falls outside the approved band for pre-authorized step classes",
     "erosion of substantive human oversight", [], 3, 4,
     "governance", "unauthorized_authority_exercise", "minor", "reversible", PRESENT_GUIDANCE),
    ("C-12", "a delegated subtask permit can be issued wider than the authority it derives from",
     "a child permit issued by DELEGATE is wider than its parent in scope, validity, or action set",
     "an accountability transfer with no narrowing guarantee", [], 2, 5,
     "accountability_transfer", "accountability_transfer", "material", "irreversible", DELEGATE),
    ("C-13", "context snapshots can be stale, mismatched to the scheduled patient, or missing lineage",
     "a context snapshot fails identity, freshness, or lineage verification",
     "an autonomous proposal rests on unprovenanced or wrong-patient data", [], 3, 5,
     # A data-provenance/lineage defect, not itself a physical-harm mechanism;
     # kept out of C*_cp's member_kinds entirely (rather than relying on the
     # reversibility qualifier, which this row's "requires_intervention" value
     # would otherwise satisfy) so the manuscript's stated "mandatory (other)"
     # disposition is structural, not incidental to a materiality/reversibility
     # combination.
     "patient_harm", "clinical_oversight_defect", "material", "requires_intervention", ENTER_AUTONOMOUS_SUBTASK),
    ("C-14", "the authorization evaluator can fail to complete within its declared bound",
     "evaluation exceeds evaluation_latency_bound",
     "an unresolved authorization state with no declared failure mode", [], 2, 3,
     "governance", "unauthorized_authority_exercise", "minor", "reversible", ENTER_AUTONOMOUS_SUBTASK),
    ("C-15", "a safety-layer intervention can occur without a correlated signed record",
     "interlock or fallback fires and no signed SafetyEvent is recorded within the declared window",
     "incomplete recovery evidence, defeating post-event audit", [], 2, 3,
     "governance", "unauthorized_authority_exercise", "minor", "reversible", ACTIVATE_INSTRUMENT),
    ("C-16", "sustained attention during long procedures is not observable at authorization time",
     "supervisor performance degrades (fatigue, distraction) without an approved observable",
     "patient harm mediated by degraded human oversight", [], 3, 4,
     # Non-runtime (RC-03); kept out of C*_cp's member_kinds for the same
     # reason as C-13 -- an oversight/process defect, not a direct
     # physical-harm mechanism, and a NonRuntimeDisposition row has no
     # RC-06 coverage exemption available to it.
     "patient_harm", "clinical_oversight_defect", "material", "requires_intervention", None),
]

_EXISTING_CONTROLS_C = {
    "C-01": ["manual IFU checklist"], "C-02": ["session timeout"], "C-03": ["console lockout"],
    "C-04": ["verbal handoff protocol"], "C-05": ["badge-based session binding"],
    "C-06": ["force envelope firmware limit"], "C-07": ["geometric envelope firmware limit"],
    "C-08": ["guidance review by surgeon"], "C-09": ["export approval workflow"],
    "C-10": ["model validation registry"], "C-11": ["periodic audit sampling"],
    "C-12": ["delegation logging"], "C-13": ["patient ID barcode scan"],
    "C-14": ["evaluator health monitoring"], "C-15": ["incident review board"],
    "C-16": ["scheduling and relief policy"],
}


#: Only the seven C*_cp-classified rows declare a hazardous_action_path: the
#: authority matrix marks their action tuples hazardous=True. The remaining
#: runtime rows' ACS still resolve against the authority matrix normally
#: (their action is authorized) -- they simply do not require C* coverage.
CSTAR_ROWS = frozenset(["C-01", "C-02", "C-03", "C-04", "C-05", "C-09", "C-12"])


def build_risk_register():
    rows = []
    for rid, cause, event, consequence, obligations, _lr, _ir, cclass, _k, _m, _rev, action_tuple in _RISKS:
        declare_hazardous = action_tuple and rid in CSTAR_ROWS
        rows.append({
            "risk_id": rid, "cause": cause, "event": event, "consequence": consequence,
            "affected_parties": ["the patient", "the supervising surgeon"],
            "obligation_refs": obligations, "existing_controls": _EXISTING_CONTROLS_C[rid],
            "owner": "business.surgical_program_office",
            "hazardous_action_paths": [dict(action_tuple)] if declare_hazardous else [],
            "source_register_row": "synthetic, standards-anchored design case (manuscript Section XI)",
        })
    return rows


def build_risk_analysis():
    rows = []
    for rid, _c, _e, _q, _o, lr, ir, cclass, kind, materiality, reversibility, _a in _RISKS:
        rows.append({
            "risk_id": rid,
            "likelihood_inherent": min(5, lr + 1), "impact_inherent": ir,
            "control_effectiveness": "partially_effective",
            "likelihood_residual": lr, "impact_residual": ir,
            "consequence_class": cclass,
            "consequence_descriptor": {
                "kind": kind, "materiality": materiality, "reversibility": reversibility,
                "authority": "surgical_platform_governance", "classification_authority": FORUM,
                "rationale": "Classified under the approved C*_cp profile CSTAR-C-1.0.",
                "effective_date": APPROVAL_TIME, "emergency_override_procedure": None,
            },
            "tier": "tier_1", "treatment": "mitigate", "reopening_trigger": None,
        })
    return rows
