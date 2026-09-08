"""Case A control layer: catalog K, threshold contracts, ACS set D, judgment
record J, dispositions Delta, and the invariant register INV.

Every entry corresponds to a row of the Section IX table.  Where the manuscript
gives a "predicate sketch" in prose, the machine-readable form here is the
smallest deterministic condition that expresses that sketch under an
``evaluation_basis`` from the closed set -- never a semantic classification of
prose.
"""

from .case_a_data import (  # noqa: F401  (relative import when run as a package)
    APPROVAL_TIME,
    BINDING,
    EFFECTIVE_FROM,
    FORUM,
    PUBLISH,
    RETRIEVE,
    TOOLCALL,
    VALID_UNTIL,
)

APPROVER = "forum.chair_l_tremblay"
OWNER_RESEARCH = "business.research_operations"
OWNER_COMPLIANCE = "compliance.research_supervision"
OWNER_SECURITY = "technology.security_engineering"
OWNER_PLATFORM = "technology.applied_ai_platform"

VALIDITY = {"effective_from": EFFECTIVE_FROM, "effective_until": VALID_UNTIL}

# ---------------------------------------------------------------------------
# Control Derivation Catalog K
# ---------------------------------------------------------------------------

_PUBLISH_TRIPLE = {
    "subject": ["research_agent"],
    "action": ["publish_report"],
    "resource": ["research_report"],
    "destination": ["internal_distribution"],
}
_TOOL_TRIPLE = {
    "subject": ["research_agent"],
    "action": ["invoke_tool"],
    "resource": ["external_tool"],
    "destination": ["tool_gateway"],
}
_RETRIEVE_TRIPLE = {
    "subject": ["research_agent"],
    "action": ["retrieve_document"],
    "resource": ["research_library"],
    "destination": ["agent_context"],
}


def _entry(event_type, template_id, observable_class, producers, triple, operators,
           value_schema, basis, schema_id, fields, responses, notes=""):
    return {
        "event_type": event_type,
        "template_id": template_id,
        "observable_class": observable_class,
        "allowed_producers": producers,
        "triple_template": triple,
        "allowed_operators": operators,
        "value_schema": value_schema,
        "evaluation_basis": basis,
        "evidence_schema": {"schema_id": schema_id, "fields": fields},
        "permitted_responses": responses,
        "notes": notes,
    }


CATALOG_ENTRIES = [
    _entry(
        "output_schema_claim_resolution", "T-CLAIM-RESOLVE", "typed_claim_object_set",
        ["brief_schema_validator_v2"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-CLAIM-RESOLUTION", ["draft_hash", "claim_count", "unresolved_claim_ids"],
        ["SAFE_STATE"],
        "Structural check over enumerated typed claim objects. Identifying what "
        "constitutes a factual claim in unstructured prose would require "
        "probabilistic judgment and is an RC-03 condition, not this template.",
    ),
    _entry(
        "citation_membership", "T-CITE-SUBSET", "citation_set",
        ["library_manifest_service_v4"], _PUBLISH_TRIPLE, ["subset_of"],
        {"type": "boolean"}, "deterministic_lookup",
        "ES-CITATION-SET", ["draft_hash", "cited_source_hashes", "manifest_version"],
        ["SAFE_STATE"],
    ),
    _entry(
        "source_freshness", "T-FRESHNESS", "source_age_measurement",
        ["library_manifest_service_v4"], _PUBLISH_TRIPLE, ["<="],
        {"type": "number"}, "threshold_on_measured_value",
        "ES-SOURCE-AGE", ["draft_hash", "max_source_age_hours", "asset_class"],
        ["SAFE_STATE"],
    ),
    _entry(
        "coverage_skew", "T-SKEW", "coverage_skew_measurement",
        ["editorial_metrics_service_v1"], _PUBLISH_TRIPLE, ["<="],
        {"type": "number"}, "threshold_on_measured_value",
        "ES-COVERAGE-SKEW", ["draft_hash", "skew_index", "issuer_id"],
        ["WARN"],
    ),
    _entry(
        "advisory_framing_flag", "T-FRAMING-ADVISORY", "framing_flag_set",
        ["editorial_metrics_service_v1"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-FRAMING-FLAGS", ["draft_hash", "flagged_section_ids"],
        ["WARN"],
    ),
    _entry(
        "restricted_list_screening", "T-RESTRICTED", "restricted_list_match",
        ["entity_resolution_service_v3"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "deterministic_lookup",
        "ES-RESTRICTED-MATCH", ["draft_hash", "restricted_list_version", "match_count", "artifact_signature"],
        ["SAFE_STATE"],
        "The predicate deterministically verifies that a SIGNED entity-resolution "
        "artifact reports no restricted-list match. It does not claim the upstream "
        "entity resolver is perfectly accurate -- that is the warrant boundary.",
    ),
    _entry(
        "disclosure_completeness", "T-DISCLOSURE", "disclosure_checklist_state",
        ["disclosure_checklist_service_v2"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-DISCLOSURE", ["draft_hash", "checklist_id", "missing_item_ids"],
        ["SAFE_STATE"],
    ),
    _entry(
        "retrieval_provenance", "T-PROVENANCE", "document_provenance_state",
        ["library_manifest_service_v4"], _RETRIEVE_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-PROVENANCE", ["query_id", "document_hashes", "unverified_document_hashes"],
        ["SAFE_STATE"],
    ),
    _entry(
        "tool_call_origin", "T-TOOL-ORIGIN", "tool_call_origin_state",
        ["tool_gateway_v2"], _TOOL_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-TOOL-ORIGIN", ["tool_id", "originating_span_class"],
        ["SAFE_STATE"],
    ),
    _entry(
        "approval_token_binding", "T-APPROVAL", "supervisory_approval_attestation",
        ["approval_service_v3"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "human_attestation",
        "ES-APPROVAL-TOKEN", ["draft_hash", "approver_id", "token_id", "token_signature"],
        ["SAFE_STATE"],
        "human_attestation is deterministic at evaluation time: the predicate tests "
        "for the presence and validity of a signed attestation artifact, not for "
        "the quality of the human judgment it records.",
    ),
    _entry(
        "output_field_class_absence", "T-FIELD-ABSENT", "output_field_class_set",
        ["brief_schema_validator_v2"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-FIELD-CLASS", ["draft_hash", "present_field_classes"],
        ["SAFE_STATE"],
    ),
    _entry(
        "disclaimer_presence", "T-DISCLAIMER", "disclaimer_slot_state",
        ["brief_schema_validator_v2"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-DISCLAIMER", ["draft_hash", "disclaimer_slot_populated", "disclaimer_text_hash"],
        ["SAFE_STATE"],
    ),
    _entry(
        "tool_target_authorization", "T-TOOL-TARGET", "tool_target_membership",
        ["tool_gateway_v2"], _TOOL_TRIPLE, ["in"],
        {"type": "boolean"}, "deterministic_lookup",
        "ES-TOOL-TARGET", ["tool_id", "target_endpoint", "manifest_version"],
        ["SAFE_STATE"],
    ),
    _entry(
        "version_fingerprint_match", "T-VERSION", "runtime_fingerprint",
        ["deployment_attestation_service_v1"], _PUBLISH_TRIPLE, ["=="],
        {"type": "string"}, "deterministic_lookup",
        "ES-VERSION-FINGERPRINT", ["model_version", "prompt_version", "dataset_version", "policy_version", "fingerprint"],
        ["SAFE_STATE"],
    ),
    _entry(
        "review_telemetry_band", "T-REVIEW-BAND", "review_dwell_measurement",
        ["review_telemetry_service_v1"], _PUBLISH_TRIPLE, [">="],
        {"type": "number"}, "threshold_on_measured_value",
        "ES-REVIEW-TELEMETRY", ["draft_hash", "reviewer_id", "dwell_seconds", "reviews_in_window"],
        ["WARN"],
        "A deterministic proxy for substantive review. It does not measure the "
        "quality of the reviewer's judgment.",
    ),
    _entry(
        "receipt_chain_completeness", "T-RECEIPT-CHAIN", "receipt_chain_state",
        ["evidence_chain_service_v2"], _PUBLISH_TRIPLE, ["=="],
        {"type": "boolean"}, "structural_check",
        "ES-RECEIPT-CHAIN", ["receipt_id", "authorization_time", "evidence_commit_time", "chain_prev_hash"],
        ["SAFE_STATE"],
    ),
]

CATALOG = {
    "catalog_id": "K-CASE-A",
    "version": "1.0",
    "version_binding_ref": BINDING,
    "approved_by": FORUM,
    "approval_time": APPROVAL_TIME,
    "entries": CATALOG_ENTRIES,
}

# ---------------------------------------------------------------------------
# Threshold contracts
# ---------------------------------------------------------------------------

THRESHOLD_CONTRACTS = {
    "TC-FRESHNESS-EQUITY": {
        "contract_id": "TC-FRESHNESS-EQUITY",
        "operational_definition": "Maximum age, at authorization time, of the oldest source document cited by a brief covering a listed-equity issuer.",
        "numerator": "hours elapsed between the source document's library ingestion timestamp and the authorization decision time",
        "denominator": "one brief (per-brief maximum over its cited sources); not a rate",
        "evidence_source": "library_manifest_service_v4 signed source-age artifact",
        "ground_truth": "library ingestion timestamps recorded at document intake, independently of the drafting pipeline",
        "threshold_rationale": "The research supervision policy requires listed-equity briefs to rest on sources no older than one quarter's reporting cycle; 2160 hours is 90 days.",
        "uncertainty_method": "Ingestion timestamps are exact to the second; the reported uncertainty is the clock skew bound of the ingestion service (<= 2 s), which is immaterial at this threshold.",
        "unit": "hours",
        "reproduction_procedure": "Re-request the signed source-age artifact for the draft hash and recompute max(authorization_time - ingestion_time) over cited sources.",
        "proposed_by": OWNER_RESEARCH,
        "approved_by": FORUM,
        "approval_time": APPROVAL_TIME,
        "value": 2160,
        "zero_event_reporting": "Not applicable: this is a per-brief maximum, not a rate.",
    },
    "TC-COVERAGE-SKEW": {
        "contract_id": "TC-COVERAGE-SKEW",
        "operational_definition": "Coverage-skew index for a brief: the normalized absolute difference between the share of cited evidence supporting and the share opposing the brief's central assertion, as tagged in the approved library metadata.",
        "numerator": "|supporting_citation_count - opposing_citation_count|",
        "denominator": "supporting_citation_count + opposing_citation_count (citations carrying a directional tag in the approved library)",
        "evidence_source": "editorial_metrics_service_v1 signed skew artifact",
        "ground_truth": "directional tags assigned at library intake by the research editorial function, not by the drafting model",
        "threshold_rationale": "The Research Quality Assurance Standard treats a directional imbalance above 0.6 as requiring editorial attention; the bound is advisory and feeds a weighted aggregation group rather than a mandatory gate.",
        "uncertainty_method": "Binomial proportion; the artifact reports the Jeffreys 95% interval alongside the point estimate. Briefs with fewer than 5 directional citations report the exposure denominator and are excluded from the weighted group.",
        "unit": "dimensionless ratio in [0, 1]",
        "reproduction_procedure": "Re-request the signed skew artifact for the draft hash and recompute the index from the tagged citation counts it carries.",
        "proposed_by": OWNER_RESEARCH,
        "approved_by": FORUM,
        "approval_time": APPROVAL_TIME,
        "value": 0.6,
        "zero_event_reporting": "A zero-skew result is reported with its citation denominator and an exact one-sided upper bound, never as 'no bias'.",
    },
    "TC-REVIEW-DWELL": {
        "contract_id": "TC-REVIEW-DWELL",
        "operational_definition": "Reviewer dwell time on a brief: seconds between the reviewer opening the draft in the approval workspace and submitting the approval decision, excluding periods with no interaction events for more than 120 s.",
        "numerator": "active dwell seconds recorded by the approval workspace",
        "denominator": "one review event; reported alongside reviews_in_window (reviews by the same reviewer in the preceding 60 minutes)",
        "evidence_source": "review_telemetry_service_v1 signed telemetry artifact",
        "ground_truth": "workspace interaction events, recorded independently of the reviewer's self-report",
        "threshold_rationale": "Supervisory policy sets 180 s as the minimum plausible time to examine a brief's claims and disclosures. The bound is an advisory monitoring proxy, not an authorization gate: it does not measure the quality of the judgment.",
        "uncertainty_method": "Dwell is a censored measurement (idle gaps excluded). The artifact reports both raw and active dwell so the censoring is visible; no distributional assumption is made.",
        "unit": "seconds",
        "reproduction_procedure": "Re-request the signed telemetry artifact for the draft hash and recompute active dwell from its interaction-event list.",
        "proposed_by": OWNER_COMPLIANCE,
        "approved_by": FORUM,
        "approval_time": APPROVAL_TIME,
        "value": 180,
        "zero_event_reporting": "A window with zero qualifying reviews is reported with its exposure denominator, never as compliance.",
    },
}

# ---------------------------------------------------------------------------
# Approved Control Specifications D
# ---------------------------------------------------------------------------


def _acs(acs_id, gcir_id, risk_id, obligations, event_type, template_id, observable_id,
         observable_class, producer, evidence_schema_ref, tuple_, param_schema_ref,
         params, operator, expected, basis, on_unknown, on_fail, gate_candidate,
         mandatory_role, escalation_route, escalation_sla, evidence_reqs, conditions,
         owner, evidence_semantics, decision_semantics, warrant_boundary,
         soft_gate_type=None, aggregation=None, threshold_contract_ref=None,
         temporal_window=None, conflict_group=None, policy_id=None):
    record = {
        "acs_id": acs_id,
        "gcir_id": gcir_id,
        "risk_id": risk_id,
        "obligation_refs": obligations,
        "event_type": event_type,
        "template_id": template_id,
        "observable_id": observable_id,
        "observable_class": observable_class,
        "observable_producer": producer,
        "evidence_source": "%s signed artifact bound to the draft or invocation hash" % producer,
        "evidence_schema_ref": evidence_schema_ref,
        "subject": tuple_["subject"],
        "action": tuple_["action"],
        "resource": tuple_["resource"],
        "destination": tuple_["destination"],
        "action_parameters": params,
        "parameter_schema_ref": param_schema_ref,
        "operator": operator,
        "expected_value": expected,
        "temporal_window": temporal_window,
        "evaluation_basis": basis,
        "threshold_contract_ref": threshold_contract_ref,
        "on_unknown": on_unknown,
        "on_fail": on_fail,
        "gate_candidate": gate_candidate,
        "mandatory_role": mandatory_role,
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
    }
    if soft_gate_type:
        record["soft_gate_type"] = soft_gate_type
    if aggregation:
        record["aggregation"] = aggregation
    if conflict_group:
        record["conflict_group"] = conflict_group
    if policy_id:
        record["policy_id"] = policy_id
    return record


def _cond(attribute, operator, value, producer, schema_ref, on_unknown="fail",
          unit=None, contract=None, window=None, required=True):
    return {
        "attribute": attribute,
        "operator": operator,
        "value": value,
        "unit": unit,
        "on_unknown": on_unknown,
        "required": required,
        "evidence_producer": producer,
        "evidence_schema_ref": schema_ref,
        "threshold_contract_ref": contract,
        "temporal_window": window,
    }


PUBLISH_PARAMS = {"draft_id": "DRAFT-BOUND", "distribution_list": "internal_research_desk"}
TOOL_PARAMS = {"tool_id": "TOOL-BOUND", "invocation_class": "read_only"}
RETRIEVE_PARAMS = {"query_id": "QUERY-BOUND"}


def build_acs_records():
    return [
        # ---- R-01 -------------------------------------------------------
        _acs(
            "ACS-0001-01", "GCIR-0001", "R-01", ["INT-RES-QA", "OSFI-E23-MRM"],
            "output_schema_claim_resolution", "T-CLAIM-RESOLVE",
            "unresolved_claim_objects_present", "typed_claim_object_set",
            "brief_schema_validator_v2", "ES-CLAIM-RESOLUTION",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", False, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "research_supervision_desk", 4,
            ["draft_hash", "claim_count", "unresolved_claim_ids", "artifact_signature"],
            [_cond("unresolved_claim_objects_present", "==", False,
                   "brief_schema_validator_v2", "ES-CLAIM-RESOLUTION")],
            OWNER_RESEARCH,
            "A signed schema-validation artifact enumerating every typed claim object in the draft and the subset whose source-hash slot is empty or unresolvable against the approved library.",
            "PERMIT requires that the set of unresolved typed claim objects is empty; indeterminate or absent evidence fails.",
            "Establishes that every claim REPRESENTED AS A TYPED CLAIM OBJECT resolves to an approved source. It does NOT establish that untyped prose contains no factual assertion -- identifying that would require probabilistic judgment (RC-03) and is routed to the evidence-production layer and to R-12 monitoring.",
            policy_id="POL-A-SOURCING",
        ),
        # ---- R-02 -------------------------------------------------------
        _acs(
            "ACS-0002-01", "GCIR-0002", "R-02", ["INT-RES-QA"],
            "citation_membership", "T-CITE-SUBSET",
            "citations_within_manifest", "citation_set",
            "library_manifest_service_v4", "ES-CITATION-SET",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "subset_of", True, "deterministic_lookup", "fail", "SAFE_STATE", "mandatory",
            "decisive", "research_supervision_desk", 4,
            ["draft_hash", "cited_source_hashes", "manifest_version", "artifact_signature"],
            [_cond("citations_within_manifest", "subset_of", True,
                   "library_manifest_service_v4", "ES-CITATION-SET")],
            OWNER_RESEARCH,
            "A signed manifest-membership artifact listing every cited source hash and whether each is a member of the approved library manifest at the stated manifest version.",
            "PERMIT requires the cited source-hash set to be a subset of the approved library manifest; indeterminate or absent evidence fails.",
            "Establishes membership in the approved library. It does not establish that a cited source supports the claim it is attached to.",
            policy_id="POL-A-SOURCING",
        ),
        # ---- R-03 -------------------------------------------------------
        _acs(
            "ACS-0003-01", "GCIR-0003", "R-03", ["INT-RES-QA"],
            "source_freshness", "T-FRESHNESS",
            "max_source_age_hours", "source_age_measurement",
            "library_manifest_service_v4", "ES-SOURCE-AGE",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "<=", 2160, "threshold_on_measured_value", "fail", "SAFE_STATE", "mandatory",
            "decisive", "research_supervision_desk", 4,
            ["draft_hash", "max_source_age_hours", "asset_class", "artifact_signature"],
            [_cond("max_source_age_hours", "<=", 2160,
                   "library_manifest_service_v4", "ES-SOURCE-AGE",
                   unit="hours", contract="TC-FRESHNESS-EQUITY")],
            OWNER_RESEARCH,
            "A signed source-age artifact reporting the maximum age in hours, at authorization time, of any source cited by the draft, together with the asset class that selects the bound.",
            "PERMIT requires max_source_age_hours <= the approved bound under threshold contract TC-FRESHNESS-EQUITY; indeterminate or absent evidence fails.",
            "Establishes that no cited source exceeds the approved age bound. It does not establish that the underlying facts have not changed within the bound.",
            threshold_contract_ref="TC-FRESHNESS-EQUITY",
            policy_id="POL-A-SOURCING",
        ),
        # ---- R-04 (two specifications: weighted + advisory) --------------
        _acs(
            "ACS-0004-01", "GCIR-0004", "R-04", ["INT-RES-QA"],
            "coverage_skew", "T-SKEW",
            "coverage_skew_index", "coverage_skew_measurement",
            "editorial_metrics_service_v1", "ES-COVERAGE-SKEW",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "<=", 0.6, "threshold_on_measured_value", "warn", "WARN", "weighted",
            "supporting", "research_editorial_desk", 24,
            ["draft_hash", "skew_index", "issuer_id", "artifact_signature"],
            [_cond("coverage_skew_index", "<=", 0.6,
                   "editorial_metrics_service_v1", "ES-COVERAGE-SKEW",
                   on_unknown="warn", unit="dimensionless ratio in [0, 1]",
                   contract="TC-COVERAGE-SKEW")],
            OWNER_RESEARCH,
            "A signed editorial-metrics artifact reporting the coverage-skew index computed from directional tags assigned at library intake, not by the drafting model.",
            "The condition contributes a normalized deficit to the editorial-balance aggregation group; the group's threshold test enters the mandatory aggregate as a single dimension. It never overrides a mandatory result.",
            "Establishes that measured directional imbalance is within the approved bound. It does not establish that the brief is balanced in any editorial or legal sense.",
            soft_gate_type="weighted",
            aggregation={
                "aggregation_group": "AG-EDITORIAL-BALANCE",
                "weight": 0.7,
                "deficit_function": "max(0, (skew_index - 0.6) / 0.4)",
                "group_threshold": 0.5,
                "response": "WARN",
            },
            threshold_contract_ref="TC-COVERAGE-SKEW",
            policy_id="POL-A-BALANCE",
        ),
        _acs(
            "ACS-0004-02", "GCIR-0005", "R-04", ["INT-RES-QA"],
            "advisory_framing_flag", "T-FRAMING-ADVISORY",
            "framing_flags_absent", "framing_flag_set",
            "editorial_metrics_service_v1", "ES-FRAMING-FLAGS",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", True, "structural_check", "warn", "WARN", "advisory",
            "supporting", "research_editorial_desk", 24,
            ["draft_hash", "flagged_section_ids", "artifact_signature"],
            [_cond("framing_flags_absent", "==", True,
                   "editorial_metrics_service_v1", "ES-FRAMING-FLAGS",
                   on_unknown="warn")],
            OWNER_RESEARCH,
            "A signed artifact listing brief sections flagged by the approved structural framing rules (for example, a conclusion section citing only one directional tag).",
            "An advisory result surfaced to the editorial desk. It never overrides a mandatory result and never blocks distribution.",
            "Establishes that no approved structural framing rule fired. It does not establish absence of bias.",
            soft_gate_type="advisory",
            policy_id="POL-A-BALANCE",
        ),
        # ---- R-05 (C*: information barrier) ------------------------------
        _acs(
            "ACS-0005-01", "GCIR-0006", "R-05", ["SEC-BAR-INT", "PIPEDA-PRIV"],
            "restricted_list_screening", "T-RESTRICTED",
            "restricted_list_match", "restricted_list_match",
            "entity_resolution_service_v3", "ES-RESTRICTED-MATCH",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", False, "deterministic_lookup", "fail", "SAFE_STATE", "mandatory",
            "decisive", "compliance_information_barrier_desk", 1,
            ["draft_hash", "restricted_list_version", "match_count", "artifact_signature"],
            [_cond("restricted_list_match", "==", False,
                   "entity_resolution_service_v3", "ES-RESTRICTED-MATCH")],
            OWNER_COMPLIANCE,
            "A SIGNED entity-resolution artifact reporting whether any entity in the retrieval context or the generated brief matches the restricted list at a stated list version.",
            "PERMIT requires restricted_list_match == false. Missing, stale or schema-invalid evidence is indeterminacy and fails; escalation is raised on failure.",
            "Establishes that the signed entity-resolution artifact reports no match. It does NOT establish that the upstream entity resolver is perfectly accurate, nor that no material non-public information reached the context by a path the resolver does not observe.",
            policy_id="POL-A-INFOBARRIER",
        ),
        # ---- R-06 (C*: statutory) ----------------------------------------
        _acs(
            "ACS-0006-01", "GCIR-0007", "R-06", ["CIRO-3608-DISC"],
            "disclosure_completeness", "T-DISCLOSURE",
            "disclosure_checklist_complete", "disclosure_checklist_state",
            "disclosure_checklist_service_v2", "ES-DISCLOSURE",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", True, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "compliance_research_supervision", 2,
            ["draft_hash", "checklist_id", "missing_item_ids", "artifact_signature"],
            [_cond("disclosure_checklist_complete", "==", True,
                   "disclosure_checklist_service_v2", "ES-DISCLOSURE")],
            OWNER_COMPLIANCE,
            "A signed checklist artifact enumerating every disclosure item CIRO s. 3608 requires for this brief and which of them are populated.",
            "PERMIT requires every required checklist item to be populated; indeterminate or absent evidence fails.",
            "Establishes structural completeness of the disclosure checklist. It does not establish that a populated disclosure is accurate or adequate as a matter of law.",
            policy_id="POL-A-DISCLOSURE",
        ),
        # ---- R-07 (two specifications on two action paths) ----------------
        _acs(
            "ACS-0007-01", "GCIR-0008", "R-07", ["OSFI-B13-TECH"],
            "retrieval_provenance", "T-PROVENANCE",
            "all_documents_provenance_verified", "document_provenance_state",
            "library_manifest_service_v4", "ES-PROVENANCE",
            RETRIEVE, "PS-RETRIEVE", RETRIEVE_PARAMS,
            "==", True, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "security_operations", 2,
            ["query_id", "document_hashes", "unverified_document_hashes", "artifact_signature"],
            [_cond("all_documents_provenance_verified", "==", True,
                   "library_manifest_service_v4", "ES-PROVENANCE")],
            OWNER_SECURITY,
            "A signed provenance artifact listing each retrieved document hash and whether its ingestion signature and structural form verify.",
            "PERMIT requires every retrieved document to verify; indeterminate or absent evidence fails.",
            "Establishes that retrieved documents carry verified provenance. It does not establish that a verified document contains no adversarial content.",
            policy_id="POL-A-SECURITY",
        ),
        _acs(
            "ACS-0007-02", "GCIR-0009", "R-07", ["OSFI-B13-TECH"],
            "tool_call_origin", "T-TOOL-ORIGIN",
            "tool_call_originates_outside_retrieved_content", "tool_call_origin_state",
            "tool_gateway_v2", "ES-TOOL-ORIGIN",
            TOOLCALL, "PS-INVOKE-TOOL", TOOL_PARAMS,
            "==", True, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "security_operations", 2,
            ["tool_id", "originating_span_class", "artifact_signature"],
            [_cond("tool_call_originates_outside_retrieved_content", "==", True,
                   "tool_gateway_v2", "ES-TOOL-ORIGIN")],
            OWNER_SECURITY,
            "A signed gateway artifact recording the span class (system prompt, user turn, or retrieved document) from which each tool invocation originated.",
            "PERMIT requires the invocation to originate outside retrieved content; indeterminate or absent evidence fails.",
            "Establishes the structural origin of the invocation. It does not establish that a legitimately originated invocation is safe.",
            policy_id="POL-A-SECURITY",
        ),
        # ---- R-08 (C*: authority) -----------------------------------------
        _acs(
            "ACS-0008-01", "GCIR-0010", "R-08", ["CIRO-3616-SUP"],
            "approval_token_binding", "T-APPROVAL",
            "approval_token_bound_and_valid", "supervisory_approval_attestation",
            "approval_service_v3", "ES-APPROVAL-TOKEN",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", True, "human_attestation", "fail", "SAFE_STATE", "mandatory",
            "decisive", "research_supervision_desk", 1,
            ["draft_hash", "approver_id", "token_id", "token_signature"],
            [_cond("approval_token_bound_and_valid", "==", True,
                   "approval_service_v3", "ES-APPROVAL-TOKEN")],
            OWNER_COMPLIANCE,
            "A signed supervisory approval token whose payload binds the approver identity to this draft hash.",
            "PERMIT requires a valid, unexpired approval token cryptographically bound to the draft hash under evaluation; indeterminate or absent evidence fails.",
            "Establishes the presence and validity of the signed attestation artifact. It does NOT establish that the review behind the artifact was substantive -- that is monitored separately and deterministically by R-12.",
            policy_id="POL-A-SUPERVISION",
        ),
        # ---- R-09 (C*: authority; two decisive specifications) ------------
        _acs(
            "ACS-0009-01", "GCIR-0011", "R-09", ["CIRO-3622-REC"],
            "output_field_class_absence", "T-FIELD-ABSENT",
            "recommendation_class_fields_absent", "output_field_class_set",
            "brief_schema_validator_v2", "ES-FIELD-CLASS",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", True, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "compliance_research_supervision", 2,
            ["draft_hash", "present_field_classes", "artifact_signature"],
            [_cond("recommendation_class_fields_absent", "==", True,
                   "brief_schema_validator_v2", "ES-FIELD-CLASS")],
            OWNER_COMPLIANCE,
            "A signed schema-validation artifact enumerating which output field classes are populated in the draft, including the rating, price-target and action-language slots.",
            "PERMIT requires every recommendation-class field slot to be unpopulated; indeterminate or absent evidence fails.",
            "Establishes that no recommendation-class FIELD is populated. It does not establish that free prose could not be read as a recommendation -- that residual is a human-factors exposure routed to R-12 monitoring.",
            policy_id="POL-A-RECOMMENDATION",
        ),
        _acs(
            "ACS-0009-02", "GCIR-0012", "R-09", ["CIRO-3622-REC"],
            "disclaimer_presence", "T-DISCLAIMER",
            "reliance_disclaimer_present", "disclaimer_slot_state",
            "brief_schema_validator_v2", "ES-DISCLAIMER",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", True, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "compliance_research_supervision", 2,
            ["draft_hash", "disclaimer_slot_populated", "disclaimer_text_hash"],
            [_cond("reliance_disclaimer_present", "==", True,
                   "brief_schema_validator_v2", "ES-DISCLAIMER")],
            OWNER_COMPLIANCE,
            "A signed schema-validation artifact reporting whether the mandatory reliance-disclaimer slot is populated with the approved text, identified by hash.",
            "PERMIT requires the disclaimer slot to be populated with the approved text hash; indeterminate or absent evidence fails.",
            "Establishes structural presence of the approved disclaimer. It does not establish that a reader will act on it.",
            policy_id="POL-A-RECOMMENDATION",
        ),
        # ---- R-10 (C*: irreversible) --------------------------------------
        _acs(
            "ACS-0010-01", "GCIR-0013", "R-10", ["INT-NO-TRADE-CONN"],
            "tool_target_authorization", "T-TOOL-TARGET",
            "tool_target_in_approved_manifest", "tool_target_membership",
            "tool_gateway_v2", "ES-TOOL-TARGET",
            TOOLCALL, "PS-INVOKE-TOOL", TOOL_PARAMS,
            "in", True, "deterministic_lookup", "fail", "SAFE_STATE", "mandatory",
            "decisive", "security_operations", 1,
            ["tool_id", "target_endpoint", "manifest_version", "artifact_signature"],
            [_cond("tool_target_in_approved_manifest", "in", True,
                   "tool_gateway_v2", "ES-TOOL-TARGET")],
            OWNER_SECURITY,
            "A signed gateway artifact recording the resolved target endpoint of each tool invocation and its membership in the approved read-only tool manifest. No order-management endpoint is a member of that manifest.",
            "PERMIT requires the resolved target endpoint to be a member of the approved manifest; indeterminate or absent evidence fails. An order-system call is therefore structurally unpermittable.",
            "Establishes that the invocation resolves to an approved read-only endpoint. It does not establish that the endpoint behaves as its manifest entry describes.",
            policy_id="POL-A-TOOLING",
        ),
        # ---- R-11 (coincides with INV-VERSION but is a distinct origin) ----
        _acs(
            "ACS-0011-01", "GCIR-0014", "R-11", ["OSFI-B13-TECH", "OSFI-E23-MRM"],
            "version_fingerprint_match", "T-VERSION",
            "runtime_fingerprint", "runtime_fingerprint",
            "deployment_attestation_service_v1", "ES-VERSION-FINGERPRINT",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", "sha256:8f3a1d5c2e0b47a9c6d18e4f7b2a09c35de6178b4a0c9f2e1d7b3865a4c0e9f1",
            "deterministic_lookup", "fail", "SAFE_STATE", "mandatory",
            "decisive", "technology_change_management", 2,
            ["model_version", "prompt_version", "dataset_version", "policy_version", "fingerprint", "artifact_signature"],
            [_cond("runtime_fingerprint", "==",
                   "sha256:8f3a1d5c2e0b47a9c6d18e4f7b2a09c35de6178b4a0c9f2e1d7b3865a4c0e9f1",
                   "deployment_attestation_service_v1", "ES-VERSION-FINGERPRINT")],
            OWNER_PLATFORM,
            "A signed deployment attestation reporting the model, prompt, dataset and policy versions actually loaded at authorization time, and their combined fingerprint.",
            "PERMIT requires the runtime fingerprint to equal M.version_binding.fingerprint; indeterminate or absent evidence fails.",
            "Establishes that the running configuration is the assessed configuration. It coincides with compiler invariant INV-VERSION, which Phi emits for every bundle regardless; origin metadata keeps the two authorizations distinct. The register row attaches the governance apparatus -- owner, rating, treatment, escalation -- to the invariant.",
            policy_id="POL-A-VERSION",
        ),
        # ---- R-12 (advisory monitoring) -----------------------------------
        _acs(
            "ACS-0012-01", "GCIR-0015", "R-12", ["CIRO-3616-SUP"],
            "review_telemetry_band", "T-REVIEW-BAND",
            "review_dwell_seconds", "review_dwell_measurement",
            "review_telemetry_service_v1", "ES-REVIEW-TELEMETRY",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            ">=", 180, "threshold_on_measured_value", "warn", "WARN", "advisory",
            "supporting", "compliance_research_supervision", 48,
            ["draft_hash", "reviewer_id", "dwell_seconds", "reviews_in_window", "artifact_signature"],
            [_cond("review_dwell_seconds", ">=", 180,
                   "review_telemetry_service_v1", "ES-REVIEW-TELEMETRY",
                   on_unknown="warn", unit="seconds", contract="TC-REVIEW-DWELL")],
            OWNER_COMPLIANCE,
            "A signed telemetry artifact reporting active reviewer dwell time on this draft and the reviewer's review volume in the preceding window.",
            "An advisory monitoring result routed to supervisory review. It never blocks distribution and never overrides a mandatory result.",
            "Establishes a deterministic PROXY for substantive review. It does not establish that the review was substantive; it establishes only that dwell and volume are inside the approved band.",
            soft_gate_type="advisory",
            threshold_contract_ref="TC-REVIEW-DWELL",
            policy_id="POL-A-SUPERVISION",
        ),
        # ---- R-13 (C*: statutory; coincides with INV-EVIDENCE-COMMIT) ------
        _acs(
            "ACS-0013-01", "GCIR-0016", "R-13", ["INT-EVID-CHAIN", "CIRO-3616-SUP"],
            "receipt_chain_completeness", "T-RECEIPT-CHAIN",
            "receipt_committed_and_chained", "receipt_chain_state",
            "evidence_chain_service_v2", "ES-RECEIPT-CHAIN",
            PUBLISH, "PS-PUBLISH-REPORT", PUBLISH_PARAMS,
            "==", True, "structural_check", "fail", "SAFE_STATE", "mandatory",
            "decisive", "compliance_records_desk", 2,
            ["receipt_id", "authorization_time", "evidence_commit_time", "chain_prev_hash"],
            [_cond("receipt_committed_and_chained", "==", True,
                   "evidence_chain_service_v2", "ES-RECEIPT-CHAIN")],
            OWNER_COMPLIANCE,
            "A signed evidence-chain artifact reporting that the decision receipt for this authorization was committed after the authorization decision and chained to its predecessor before release.",
            "PERMIT requires authorization_time <= evidence_commit_time and a verified chain link, evaluated before actuation; indeterminate or absent evidence fails.",
            "Establishes that the receipt exists, is ordered correctly and is chained. It coincides with compiler invariant INV-EVIDENCE-COMMIT; origin metadata keeps the two authorizations distinct. It does not establish that the receipt's content is true.",
            policy_id="POL-A-EVIDENCE",
        ),
    ]


# ---------------------------------------------------------------------------
# Dispositions Delta
# ---------------------------------------------------------------------------

RUNTIME_ACS = {
    "R-01": ["ACS-0001-01"],
    "R-02": ["ACS-0002-01"],
    "R-03": ["ACS-0003-01"],
    "R-04": ["ACS-0004-01", "ACS-0004-02"],
    "R-05": ["ACS-0005-01"],
    "R-06": ["ACS-0006-01"],
    "R-07": ["ACS-0007-01", "ACS-0007-02"],
    "R-08": ["ACS-0008-01"],
    "R-09": ["ACS-0009-01", "ACS-0009-02"],
    "R-10": ["ACS-0010-01"],
    "R-11": ["ACS-0011-01"],
    "R-12": ["ACS-0012-01"],
    "R-13": ["ACS-0013-01"],
}

NONRUNTIME = {
    "R-14": {
        "reason_code": "RC-01",
        "routed_to_control_family": "architectural_and_contractual",
        "control_ref": "CTL-A-RESILIENCE-01 (multi-vendor clause; annual resilience testing; OSFI B-10 alignment)",
        "owner": "technology.applied_ai_platform",
        "rationale": "No event evaluable at authorization time distinguishes a concentrated retrieval architecture from a diversified one. An honest non-runtime disposition, not a forced translation.",
    },
    "R-15": {
        "reason_code": "RC-03",
        "routed_to_control_family": "human_process",
        "control_ref": "CTL-A-TONE-01 (editorial review workflow under the style guide)",
        "owner": "business.research_operations",
        "rationale": "Tone has no approved catalog observable; any classifier score is a probability, which GC-IR conditions may not evaluate directly. A derived deterministic proxy (measured style-guide violation count under a threshold contract) may be proposed to the governance forum as a new catalog entry and register row -- a governance act, not a compiler shortcut.",
    },
    "R-16": {
        "reason_code": "RC-01",
        "routed_to_control_family": "contractual",
        "control_ref": "CTL-A-VENDOR-01 (source-code escrow; exit and transition clause)",
        "owner": "procurement.third_party_risk",
        "rationale": "Vendor solvency has no authorization-time observable. Distinct from R-11's technical vendor-change risk, which compiles.",
    },
}


def build_dispositions():
    records = []
    for risk_id in sorted(RUNTIME_ACS):
        records.append(
            {"risk_id": risk_id, "status": "runtime", "acs_ids": list(RUNTIME_ACS[risk_id])}
        )
    for risk_id in sorted(NONRUNTIME):
        spec = NONRUNTIME[risk_id]
        records.append(
            {
                "risk_id": risk_id,
                "status": "nonruntime",
                "reason_code": spec["reason_code"],
                "routed_to_control_family": spec["routed_to_control_family"],
                "control_ref": spec["control_ref"],
                "owner": spec["owner"],
                "approval": {
                    "approver": APPROVER,
                    "approval_time": APPROVAL_TIME,
                    "forum": FORUM,
                },
            }
        )
    return records


# ---------------------------------------------------------------------------
# Judgment record J
# ---------------------------------------------------------------------------

_SELECTION_RATIONALE = {
    "ACS-0001-01": "The register row names a typed claim object as the phenomenon; T-CLAIM-RESOLVE is the only approved template whose observable class is the typed claim object set.",
    "ACS-0002-01": "Citation membership against the approved manifest is a deterministic lookup; T-CITE-SUBSET is the approved template for it.",
    "ACS-0003-01": "Source age is a measured value requiring a threshold contract; T-FRESHNESS is selected with TC-FRESHNESS-EQUITY.",
    "ACS-0004-01": "Coverage skew is measurable but not decisive; selected as a weighted contribution to the editorial-balance group rather than a gate.",
    "ACS-0004-02": "A second, structural framing check is selected as advisory support for the same risk.",
    "ACS-0005-01": "Restricted-list screening resolves to a signed artifact; T-RESTRICTED is the approved deterministic-lookup template.",
    "ACS-0006-01": "Disclosure completeness is a structural check over an enumerated checklist; T-DISCLOSURE selected.",
    "ACS-0007-01": "Provenance verification of retrieved documents is structural; T-PROVENANCE selected on the retrieval path.",
    "ACS-0007-02": "Tool-call origin is a distinct action path for the same risk; T-TOOL-ORIGIN selected on the invocation path.",
    "ACS-0008-01": "Supervisory approval is a signed human attestation; T-APPROVAL selected, with the warrant boundary stated.",
    "ACS-0009-01": "Recommendation-class field absence is structural, never a judgment about whether prose sounds like advice.",
    "ACS-0009-02": "Disclaimer presence is a second structural condition on the same authorized hazardous path.",
    "ACS-0010-01": "Tool-target membership in the approved manifest is a deterministic lookup; T-TOOL-TARGET selected.",
    "ACS-0011-01": "Runtime fingerprint equality is a deterministic lookup; T-VERSION selected. The forum recorded that this coincides with INV-VERSION and approved both origins.",
    "ACS-0012-01": "Reviewer dwell is a measured proxy under a threshold contract; selected as advisory monitoring, explicitly not as a gate.",
    "ACS-0013-01": "Receipt chain completeness is structural; T-RECEIPT-CHAIN selected. The forum recorded that this coincides with INV-EVIDENCE-COMMIT.",
}

_DISPOSITION_RATIONALE = {
    "R-14": NONRUNTIME["R-14"]["rationale"],
    "R-15": NONRUNTIME["R-15"]["rationale"],
    "R-16": NONRUNTIME["R-16"]["rationale"],
}

SELECTORS = {
    "ACS-0005-01": "compliance.head_information_barriers",
    "ACS-0006-01": "compliance.head_research_supervision",
    "ACS-0008-01": "compliance.head_research_supervision",
    "ACS-0009-01": "compliance.head_research_supervision",
    "ACS-0009-02": "compliance.head_research_supervision",
    "ACS-0010-01": "technology.head_security_engineering",
    "ACS-0007-01": "technology.head_security_engineering",
    "ACS-0007-02": "technology.head_security_engineering",
    "ACS-0011-01": "technology.head_change_management",
    "ACS-0013-01": "compliance.head_records",
}
DEFAULT_SELECTOR = "business.head_research_operations"


def build_judgment_record(acs_records):
    selections = []
    approvals = []
    index = 0
    for acs in acs_records:
        index += 1
        selections.append(
            {
                "selection_id": "J-SEL-%03d" % index,
                "risk_id": acs["risk_id"],
                "acs_id": acs["acs_id"],
                "event_type": acs["event_type"],
                "template_id": acs["template_id"],
                "selected_by": SELECTORS.get(acs["acs_id"], DEFAULT_SELECTOR),
                "selection_time": "2026-01-19T11:00:00Z",
                "rationale": _SELECTION_RATIONALE[acs["acs_id"]],
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

    decisions = []
    for acs in acs_records:
        pass
    seen = set()
    for acs in acs_records:
        if acs["risk_id"] in seen:
            continue
        seen.add(acs["risk_id"])
        decisions.append(
            {
                "risk_id": acs["risk_id"],
                "status": "runtime",
                "decided_by": SELECTORS.get(acs["acs_id"], DEFAULT_SELECTOR),
                "decision_time": "2026-01-19T11:00:00Z",
                "rationale": "The risk has at least one approved catalog observable evaluable at authorization time.",
            }
        )
    for risk_id in sorted(NONRUNTIME):
        decisions.append(
            {
                "risk_id": risk_id,
                "status": "nonruntime",
                "reason_code": NONRUNTIME[risk_id]["reason_code"],
                "decided_by": DEFAULT_SELECTOR,
                "decision_time": "2026-01-19T11:00:00Z",
                "rationale": _DISPOSITION_RATIONALE[risk_id],
            }
        )
    decisions.sort(key=lambda d: d["risk_id"])

    return {
        "judgment_id": "J-CASE-A",
        "version": "1.0",
        "assessment_ref": {"assessment_id": "ASSESSMENT-CASE-A", "binding_id": BINDING},
        "catalog_ref": {"catalog_id": "K-CASE-A", "version": "1.0"},
        "selections": selections,
        "disposition_decisions": decisions,
        "approvals": approvals,
    }


# ---------------------------------------------------------------------------
# C* profile
# ---------------------------------------------------------------------------

MATERIALITY_ORDER = ["immaterial", "minor", "material", "severe"]

CSTAR_PROFILE = {
    "profile_id": "CSTAR-A",
    "version": "1.0",
    "version_binding_ref": BINDING,
    "approved_by": FORUM,
    "approval_time": APPROVAL_TIME,
    "materiality_order": MATERIALITY_ORDER,
    "member_kinds": [
        "material_statutory_prohibition",
        "unauthorized_authority_exercise",
        "material_information_barrier_breach",
        "irreversible_external_effect_above_approved_bound",
    ],
    "classification_rules": {
        "material_statutory_prohibition": {
            "approving_authority": "exec.head_of_research",
            "rationale": "A statutory prohibition whose breach is material to clients or to the dealer's registration is non-negotiable irrespective of its heat-map score.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "A documentation defect or other immaterial technical non-conformance does not enter C* solely because its source is statutory.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
        "unauthorized_authority_exercise": {
            "approving_authority": "exec.head_of_research",
            "rationale": "The system causing an effect it is not authorized to cause is an authorization failure, not a priority question.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "An unauthorized act with no external effect and no reliance exposure is below the boundary.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
        "material_information_barrier_breach": {
            "approving_authority": "exec.head_of_research",
            "rationale": "Information-barrier integrity is a condition of the dealer's registration; a material breach is irreversible on disclosure.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "A match on a de-listed or expired restricted-list entry with no live exposure is below the boundary.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": "Head of Information Barriers may authorize a time-boxed exception with written rationale, recorded and reported to the forum within 24 hours.",
        },
        "irreversible_external_effect_above_approved_bound": {
            "approving_authority": "exec.head_of_research",
            "rationale": "An external effect that cannot be rescinded cannot be traded off against a priority score.",
            "materiality_boundary": {
                "minimum_materiality": "material",
                "description": "A reversible or rescindable external effect, or one below the approved bound, is not a member.",
            },
            "effective_date": APPROVAL_TIME,
            "emergency_override_procedure": None,
        },
    },
}

# ---------------------------------------------------------------------------
# Policy metadata (precedence)
# ---------------------------------------------------------------------------

POLICY_METADATA = {
    "bundle_id": "BUNDLE-CASE-A-1.0",
    "precedence": {},
    "precedence_relation": [
        "mandatory_failure",
        "mandatory_pass",
        "weighted_or_advisory",
    ],
    "aggregation_groups": {
        "AG-EDITORIAL-BALANCE": {
            "group_threshold": 0.5,
            "response": "WARN",
            "note": "The group resolves to a single group-level deficit at the enforcement boundary; compensation is admissible only inside the group.",
        }
    },
    "runtime_acceptance_condition": (
        "A conformant consuming runtime loads only bundles verifying as signed Phi "
        "outputs (signature, payload hash, lifecycle-registry state), accepts no "
        "policy content through any other channel, and emits decision receipts "
        "carrying the requirement reference (gcir_id, acs_id and origin) of every "
        "evaluated predicate."
    ),
}
