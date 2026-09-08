"""Case A -- investment research agent (manuscript Section IX).

EVIDENCE CLASS: **synthetic**.  Every field required by Sections III-IV is
populated; no field is a production observation.  Fields the manuscript states
explicitly are reproduced; fields the method requires but the manuscript does not
state are documented synthetic research fixtures recorded in
``docs/FIXTURE_PROVENANCE.md`` with an ``FP-nnn`` identifier.

Manuscript-stated content preserved here verbatim in substance:
  * 16 register rows; R-01..R-14 correspond to the fourteen-row source register,
    R-15 and R-16 are register extensions added to exercise the remaining
    reason-code classes.
  * dispositions 13 runtime / 3 non-runtime / 0 accepted / 0 unresolved
  * the residual L x I products of the 13 runtime rows
  * the consequence classes and gate sources of the Section IX table
  * R-10's rating decomposition L=2, I=5 (stated in Section VII)
  * profile: RAG summarizer over an approved research library; ~220 analysts,
    ~3,200 briefs/month; draft-only authority; no trading connectivity in scope
"""

BINDING = "VB-CASE-A-1.0"
T0 = "2026-01-15T00:00:00Z"
APPROVAL_TIME = "2026-01-20T14:00:00Z"
EFFECTIVE_FROM = "2026-02-01T00:00:00Z"
VALID_UNTIL = "2027-02-01T00:00:00Z"
COMPILE_TIME = "2026-02-02T09:00:00Z"

FORUM = "ai_governance_forum"
ACCOUNTABLE_EXEC = "exec.head_of_research"
ASSESSOR = "governance.assessor_r_okafor"
APPROVER = "forum.chair_l_tremblay"

# ---------------------------------------------------------------------------
# Step 1 -- M
# ---------------------------------------------------------------------------

METADATA = {
    "system_id": "CASE-A-INVESTMENT-RESEARCH-AGENT",
    "purpose": (
        "Retrieval-augmented drafting of internal equity research briefs from an "
        "approved research library, for analyst review and supervisory approval "
        "before internal distribution."
    ),
    "owner_business": "business.research_operations",
    "owner_technical": "technology.applied_ai_platform",
    "accountable_exec": ACCOUNTABLE_EXEC,
    "assessor": ASSESSOR,
    "deployment": "internal-only, single production tenant, Canadian dealer entity",
    "scope": (
        "Draft generation and internal distribution of equity research briefs. "
        "Draft-only authority: analyst review and supervisory approval are "
        "required before any brief leaves the drafting workspace."
    ),
    "exclusions": [
        "No trading connectivity: the order-management system is not reachable "
        "from the agent's tool gateway and is not in scope.",
        "No external client distribution; internal distribution only.",
        "No portfolio construction, no discretionary mandate.",
        "No retail-facing summarization.",
    ],
    "method": "NIST AI RMF 1.0 Map/Measure profile with ISO 31000 cause-event-consequence register",
    "version_binding": {
        "binding_id": BINDING,
        "model_version": "vendor-llm-2026.01-rev3",
        "prompt_version": "research-brief-prompt-v7",
        "dataset_version": "approved-research-library-2026-01",
        "policy_version": "research-policy-2026.1",
        "fingerprint": "sha256:8f3a1d5c2e0b47a9c6d18e4f7b2a09c35de6178b4a0c9f2e1d7b3865a4c0e9f1",
    },
    "review_cycle": "annual, or on any trigger",
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

# ---------------------------------------------------------------------------
# Step 2 -- S
# ---------------------------------------------------------------------------

AUTHORITY_MATRIX = [
    {
        "subject": "research_agent",
        "action": "publish_report",
        "resource": "research_report",
        "destination": "internal_distribution",
        "parameter_schema_id": "PS-PUBLISH-REPORT",
        "parameter_schema": {
            "draft_id": {"type": "string", "required": True},
            "distribution_list": {
                "type": "string",
                "enum": ["internal_research_desk", "internal_all_analysts"],
                "required": True,
            },
        },
        "hazardous": True,
        "notes": "The only externally effective action in scope: once distributed, a brief is not rescindable from readers who have already acted on it.",
    },
    {
        "subject": "research_agent",
        "action": "invoke_tool",
        "resource": "external_tool",
        "destination": "tool_gateway",
        "parameter_schema_id": "PS-INVOKE-TOOL",
        "parameter_schema": {
            "tool_id": {"type": "string", "required": True},
            "invocation_class": {
                "type": "string",
                "enum": ["read_only", "stateful"],
                "required": True,
            },
        },
        "hazardous": True,
        "notes": "Tool invocation is hazardous because a tool target outside the approved manifest would be an unauthorized authority exercise.",
    },
    {
        "subject": "research_agent",
        "action": "generate_draft",
        "resource": "research_report",
        "destination": "draft_workspace",
        "parameter_schema_id": "PS-GENERATE-DRAFT",
        "parameter_schema": {"draft_id": {"type": "string", "required": True}},
        "hazardous": False,
        "notes": "Internal, reversible, not externally effective.",
    },
    {
        "subject": "research_agent",
        "action": "retrieve_document",
        "resource": "research_library",
        "destination": "agent_context",
        "parameter_schema_id": "PS-RETRIEVE",
        "parameter_schema": {"query_id": {"type": "string", "required": True}},
        "hazardous": False,
        "notes": "Retrieval into context is reversible and not externally effective.",
    },
    {
        "subject": "supervisory_analyst",
        "action": "approve_draft",
        "resource": "research_report",
        "destination": "approval_service",
        "parameter_schema_id": "PS-APPROVE",
        "parameter_schema": {"draft_id": {"type": "string", "required": True}},
        "hazardous": False,
        "notes": "Human approval act; recorded as a signed attestation artifact.",
    },
]

SYSTEM_PROFILE = {
    "capabilities": [
        "retrieval over an approved research library",
        "abstractive and extractive summarization into a typed brief schema",
        "typed claim-object emission with source-hash slots",
        "read-only tool invocation through an approved tool gateway",
    ],
    "data_classes": [
        "public issuer filings",
        "licensed third-party research",
        "internal restricted list (information-barrier controlled)",
        "analyst identity and review telemetry",
    ],
    "actors": ["research_agent", "supervisory_analyst", "research_analyst", "compliance_officer"],
    "affected_parties": [
        "internal research consumers",
        "issuers covered by the brief",
        "clients of the dealer (indirectly, via analyst-authored output)",
    ],
    "architecture": (
        "RAG summarizer: approved research library -> retriever -> typed brief "
        "generator -> analyst review -> supervisory approval -> internal distribution."
    ),
    "scale": {
        "analysts": 220,
        "briefs_per_month": 3200,
        "unit": "count",
    },
    "autonomy_level": "assisted_agent",
    "authority_matrix": AUTHORITY_MATRIX,
}

PUBLISH = {
    "subject": "research_agent",
    "action": "publish_report",
    "resource": "research_report",
    "destination": "internal_distribution",
}
TOOLCALL = {
    "subject": "research_agent",
    "action": "invoke_tool",
    "resource": "external_tool",
    "destination": "tool_gateway",
}
RETRIEVE = {
    "subject": "research_agent",
    "action": "retrieve_document",
    "resource": "research_library",
    "destination": "agent_context",
}

# ---------------------------------------------------------------------------
# Step 3 -- O
# ---------------------------------------------------------------------------


def _obligation(oid, source, clause, cls, basis, jurisdiction="Canada", version="", text_hash=None):
    import hashlib

    return {
        "obligation_id": oid,
        "source": source,
        "jurisdiction": jurisdiction,
        "territorial_basis": "legal entity domiciled and registered in Canada",
        "clause_ref": clause,
        "requirement_text_hash": text_hash
        or hashlib.sha256(("REQUIREMENT-TEXT-FIXTURE::%s::%s" % (oid, clause)).encode("utf-8")).hexdigest(),
        "applicability_basis": basis,
        "applicability_decision": "applicable",
        "decision_authority": "legal.regulatory_counsel",
        "decision_time": "2026-01-12T16:30:00Z",
        "effective_from": EFFECTIVE_FROM,
        "legal_source_version": version,
        "requirement_class": cls,
    }


OBLIGATIONS = [
    _obligation(
        "CIRO-3608-DISC",
        "CIRO Investment Dealer and Partially Consolidated Rules, Rule 3600 (Research Reports)",
        "s. 3608",
        "statutory",
        ["registered investment dealer", "produces research reports", "internal distribution to registered representatives"],
        version="CIRO Rules consolidated 2025-12-01",
    ),
    _obligation(
        "CIRO-3616-SUP",
        "CIRO Investment Dealer and Partially Consolidated Rules, Rule 3600 (Research Reports)",
        "s. 3616",
        "statutory",
        ["registered investment dealer", "supervisory review of research reports required"],
        version="CIRO Rules consolidated 2025-12-01",
    ),
    _obligation(
        "CIRO-3622-REC",
        "CIRO Investment Dealer and Partially Consolidated Rules, Rule 3600 (Research Reports)",
        "s. 3622",
        "statutory",
        ["registered investment dealer", "recommendation and rating standards"],
        version="CIRO Rules consolidated 2025-12-01",
    ),
    _obligation(
        "SEC-BAR-INT",
        "Provincial securities legislation -- information barrier and material non-public information requirements",
        "information barrier policy clause 4.2",
        "statutory",
        ["dealer with both advisory and research functions", "access to material non-public information"],
        version="OSC/ASC consolidated 2025-09-30",
    ),
    _obligation(
        "PIPEDA-PRIV",
        "Personal Information Protection and Electronic Documents Act",
        "Sch. 1, principle 4.7 (safeguards)",
        "statutory",
        ["processes personal information of identifiable individuals"],
        version="PIPEDA as amended to 2025-06-20",
    ),
    _obligation(
        "OSFI-B13-TECH",
        "OSFI Guideline B-13, Technology and Cyber Risk Management",
        "s. 2.3 technology operations and s. 3 cyber security",
        "supervisory",
        ["federally regulated financial institution", "technology system in production"],
        version="OSFI B-13 (2022)",
    ),
    _obligation(
        "OSFI-E21-ORR",
        "OSFI Guideline E-21, Operational Risk and Resilience",
        "s. 4 critical operations and s. 5 resilience",
        "supervisory",
        ["federally regulated financial institution", "operation supports a critical business service"],
        version="OSFI E-21 (2024)",
    ),
    _obligation(
        "OSFI-B10-TPR",
        "OSFI Guideline B-10, Third-Party Risk Management",
        "s. 3 third-party arrangements",
        "supervisory",
        ["material third-party arrangement for model and retrieval services"],
        version="OSFI B-10 (2023)",
    ),
    _obligation(
        "OSFI-E23-MRM",
        "OSFI Guideline E-23, Model Risk Management (readiness)",
        "s. 3 model lifecycle and s. 5 model risk controls",
        "supervisory",
        ["model in the enterprise model inventory", "readiness posture ahead of the 2027-05-01 effective date"],
        version="OSFI E-23 published 2025-09-11, effective 2027-05-01",
    ),
    _obligation(
        "INT-RES-QA",
        "Internal requirement -- Research Quality Assurance Standard",
        "RQA-2026 s. 2 (sourcing) and s. 3 (balance)",
        "internal",
        ["all internally distributed research output"],
        version="RQA-2026.1",
    ),
    _obligation(
        "INT-EVID-CHAIN",
        "Internal requirement -- Evidence Chain Completeness Standard",
        "ECC-2026 s. 1 (authorization receipts)",
        "internal",
        ["all authorization decisions taken by an automated authority"],
        version="ECC-2026.1",
    ),
    _obligation(
        "INT-NO-TRADE-CONN",
        "Internal requirement -- Research Systems Trading Connectivity Prohibition",
        "RSTP-2026 s. 1",
        "internal",
        ["research systems without a discretionary trading mandate"],
        version="RSTP-2026.1",
    ),
]

# ---------------------------------------------------------------------------
# Step 4/5 -- R and A
# ---------------------------------------------------------------------------

# (risk_id, cause, event, consequence, obligation_refs, hazardous paths,
#  L_inh, I_inh, effectiveness, L_res, I_res, consequence_class, descriptor kind,
#  materiality, reversibility, tier, treatment)
_RISKS = [
    (
        "R-01",
        "because the model generates probabilistic text, unsupported financial facts may be presented as true",
        "a typed claim object in the output schema carries no resolving source hash",
        "defective research is distributed and relied upon, causing client harm",
        ["INT-RES-QA", "OSFI-E23-MRM"],
        [],
        5, 5, "partially_effective", 4, 5,
        "client_harm", "client_harm", "material", "partially_reversible", "tier_1", "mitigate",
        "R14-01",
    ),
    (
        "R-02",
        "retrieval may surface documents outside the approved library, or the generator may fabricate a citation",
        "a cited source is not a member of the approved library manifest",
        "unsourced or misattributed research is distributed, causing client harm",
        ["INT-RES-QA"],
        [],
        5, 4, "partially_effective", 4, 4,
        "client_harm", "client_harm", "material", "partially_reversible", "tier_1", "mitigate",
        "R14-02",
    ),
    (
        "R-03",
        "the approved library contains documents of differing vintage and no per-asset-class freshness gate exists at generation time",
        "a source timestamp exceeds the approved freshness bound for its asset class",
        "stale analysis is distributed as current, causing client harm",
        ["INT-RES-QA"],
        [],
        5, 4, "partially_effective", 4, 4,
        "client_harm", "client_harm", "material", "partially_reversible", "tier_1", "mitigate",
        "R14-03",
    ),
    (
        "R-04",
        "retrieval ranking and prompt framing may systematically over-weight one side of a covered issuer's evidence base",
        "the measured coverage-skew metric for a brief exceeds the approved bound",
        "systematically biased framing reaches internal readers, a conduct exposure",
        ["INT-RES-QA"],
        [],
        4, 4, "partially_effective", 3, 4,
        "conduct", "conduct", "minor", "reversible", "tier_2", "mitigate",
        "R14-04",
    ),
    (
        "R-05",
        "the agent's retrieval context spans repositories on both sides of the information barrier",
        "a restricted-list entity match appears in the retrieval context or the generated brief",
        "material non-public information crosses the information barrier",
        ["SEC-BAR-INT", "PIPEDA-PRIV"],
        [PUBLISH],
        4, 5, "partially_effective", 3, 5,
        "information_barrier", "material_information_barrier_breach", "material", "irreversible", "tier_1", "mitigate",
        "R14-05",
    ),
    (
        "R-06",
        "conflict disclosures are assembled from several systems and the generator has no structural obligation to include them",
        "a mandatory conflict disclosure required by the disclosure checklist is absent from the brief",
        "a research report is distributed without a statutorily mandated disclosure",
        ["CIRO-3608-DISC"],
        [PUBLISH],
        4, 5, "partially_effective", 3, 5,
        "statutory", "material_statutory_prohibition", "material", "irreversible", "tier_1", "mitigate",
        "R14-06",
    ),
    (
        "R-07",
        "retrieved documents are third-party controlled and may carry adversarial instructions or forged provenance",
        "a retrieved document fails its provenance or structural check, or a tool call originates inside retrieved content",
        "the agent is steered by untrusted content, a security exposure",
        ["OSFI-B13-TECH"],
        [],
        4, 5, "partially_effective", 3, 5,
        "security", "security", "material", "partially_reversible", "tier_1", "mitigate",
        "R14-07",
    ),
    (
        "R-08",
        "the drafting workspace and the distribution channel are separate systems and approval state is carried by a token",
        "distribution proceeds without a valid supervisory approval token bound to the draft hash",
        "an unapproved research report is distributed -- an exercise of authority the system does not hold",
        ["CIRO-3616-SUP"],
        [PUBLISH],
        4, 5, "partially_effective", 3, 5,
        "authority", "unauthorized_authority_exercise", "material", "irreversible", "tier_1", "mitigate",
        "R14-08",
    ),
    (
        "R-09",
        "the brief schema contains rating, price-target and action-language slots that the system is not authorized to populate",
        "recommendation-class fields are present in the output, or the mandatory reliance disclaimer is absent",
        "an unauthorized investment recommendation is issued in the dealer's name",
        ["CIRO-3622-REC"],
        [PUBLISH],
        3, 5, "partially_effective", 3, 4,
        "authority", "unauthorized_authority_exercise", "material", "irreversible", "tier_1", "mitigate",
        "R14-09",
    ),
    (
        "R-10",
        "the tool gateway is a general invocation surface and an order-management endpoint could be reachable through a misconfiguration",
        "a tool call targets an endpoint outside the approved read-only tool manifest",
        "an unauthorized trade is placed -- an irreversible external effect",
        ["INT-NO-TRADE-CONN"],
        [TOOLCALL],
        3, 5, "effective", 2, 5,
        "irreversible", "irreversible_external_effect_above_approved_bound", "severe", "irreversible", "tier_1", "mitigate",
        "R14-10",
    ),
    (
        "R-11",
        "model, prompt, dataset and policy artifacts are deployed independently and a stale artifact can remain active",
        "the runtime model, prompt or policy fingerprint differs from the assessed configuration",
        "the system operates under a configuration the assessment never covered; the compiled control set is invalid by construction",
        ["OSFI-B13-TECH", "OSFI-E23-MRM"],
        [],
        5, 4, "partially_effective", 4, 4,
        "governance", "governance_bundle_validity", "material", "reversible", "tier_1", "mitigate",
        "R14-11",
    ),
    (
        "R-12",
        "review volume and time pressure make click-through approval possible without substantive examination",
        "reviewer dwell time or review volume for a brief falls outside the approved band",
        "human oversight is nominal rather than substantive, a governance exposure",
        ["CIRO-3616-SUP"],
        [],
        4, 4, "partially_effective", 3, 4,
        "governance", "governance_oversight", "minor", "reversible", "tier_2", "mitigate",
        "R14-12",
    ),
    (
        "R-13",
        "the authorization decision and its evidence record are produced by different components and can diverge under failure",
        "a decision receipt is absent from, or unchained in, the evidence record for an authorized release",
        "the authorization decision is not evidenced, defeating the statutory record-keeping requirement",
        ["INT-EVID-CHAIN", "CIRO-3616-SUP"],
        [PUBLISH],
        3, 5, "partially_effective", 2, 5,
        "statutory", "material_statutory_prohibition", "material", "irreversible", "tier_1", "mitigate",
        "R14-13",
    ),
    (
        "R-14",
        "the retrieval stack depends on a single vendor for both embedding and index services",
        "that vendor's service degrades or becomes unavailable",
        "the research pipeline loses its retrieval capability, an operational-resilience exposure",
        ["OSFI-E21-ORR"],
        [],
        4, 4, "partially_effective", 3, 4,
        "operational_resilience", "operational_resilience", "material", "reversible", "tier_2", "mitigate",
        "R14-14",
    ),
    (
        "R-15",
        "generated prose carries a register and tone that no structural field of the brief schema constrains",
        "a brief is drafted in an unprofessional or reputationally damaging register",
        "reputational damage to the dealer's research franchise",
        ["INT-RES-QA"],
        [],
        3, 3, "ineffective", 3, 2,
        "reputational", "reputational", "minor", "reversible", "tier_3", "mitigate",
        "register extension",
    ),
    (
        "R-16",
        "the third-party model vendor is an early-stage company with concentrated funding",
        "the vendor ceases trading or is acquired and the service is withdrawn",
        "loss of the model capability on which the pipeline depends, a third-party viability exposure",
        ["OSFI-B10-TPR"],
        [],
        3, 4, "partially_effective", 2, 4,
        "third_party_viability", "third_party_viability", "material", "reversible", "tier_2", "mitigate",
        "register extension",
    ),
]

_AFFECTED = {
    "client_harm": ["internal research consumers", "clients of the dealer"],
    "conduct": ["internal research consumers", "issuers covered by the brief"],
    "information_barrier": ["issuers covered by the brief", "clients of the dealer"],
    "statutory": ["clients of the dealer", "the dealer as regulated entity"],
    "security": ["the dealer as regulated entity", "internal research consumers"],
    "authority": ["clients of the dealer", "the dealer as regulated entity"],
    "irreversible": ["clients of the dealer", "the dealer as regulated entity"],
    "governance": ["the dealer as regulated entity"],
    "operational_resilience": ["internal research consumers"],
    "reputational": ["the dealer as regulated entity"],
    "third_party_viability": ["internal research consumers"],
}

_EXISTING_CONTROLS = {
    "R-01": ["analyst review of every brief", "typed claim schema in the brief template"],
    "R-02": ["approved research library manifest", "analyst spot-check of citations"],
    "R-03": ["library ingestion timestamps", "analyst judgement on vintage"],
    "R-04": ["editorial guidance on balance"],
    "R-05": ["repository-level access control", "restricted-list maintenance process"],
    "R-06": ["disclosure checklist maintained by compliance"],
    "R-07": ["library ingestion vetting", "network egress controls"],
    "R-08": ["supervisory approval workflow"],
    "R-09": ["brief template guidance", "analyst attestation"],
    "R-10": ["network segmentation between research and trading estates"],
    "R-11": ["change management process", "deployment manifests"],
    "R-12": ["supervisory review policy"],
    "R-13": ["application logging"],
    "R-14": ["vendor SLA", "annual resilience review"],
    "R-15": ["style guide", "analyst editing"],
    "R-16": ["vendor financial review at onboarding"],
}


def build_risk_register():
    rows = []
    for (
        rid, cause, event, consequence, obligations, hazards,
        _li, _ii, _eff, _lr, _ir, cclass, _kind, _mat, _rev, _tier, _treat, source_row,
    ) in _RISKS:
        rows.append(
            {
                "risk_id": rid,
                "cause": cause,
                "event": event,
                "consequence": consequence,
                "affected_parties": _AFFECTED[cclass],
                "obligation_refs": obligations,
                "existing_controls": _EXISTING_CONTROLS[rid],
                "owner": "business.research_operations",
                "hazardous_action_paths": hazards,
                "source_register_row": source_row,
            }
        )
    return rows


_CLASSIFICATION_AUTHORITY = "forum.consequence_classification_panel"


def build_risk_analysis():
    rows = []
    for (
        rid, _c, _e, _q, _o, _h,
        li, ii, eff, lr, ir, cclass, kind, materiality, reversibility, tier, treatment, _src,
    ) in _RISKS:
        rows.append(
            {
                "risk_id": rid,
                "likelihood_inherent": li,
                "impact_inherent": ii,
                "control_effectiveness": eff,
                "likelihood_residual": lr,
                "impact_residual": ir,
                "consequence_class": cclass,
                "consequence_descriptor": {
                    "kind": kind,
                    "materiality": materiality,
                    "reversibility": reversibility,
                    "authority": "dealer_research_function",
                    "classification_authority": _CLASSIFICATION_AUTHORITY,
                    "rationale": "Classified under the approved C* profile CSTAR-A-1.0; "
                    "materiality assessed against the profile's boundary for this kind.",
                    "effective_date": APPROVAL_TIME,
                    "emergency_override_procedure": None,
                },
                "tier": tier,
                "treatment": treatment,
                "reopening_trigger": _REOPENING.get(rid),
            }
        )
    return rows


_REOPENING = {
    "R-05": "any change to the restricted-list feed or to repository access boundaries",
    "R-10": "any change to the approved tool manifest or to network segmentation",
    "R-11": "any deployment of a model, prompt, dataset or policy artifact",
    "R-14": "any change to the retrieval vendor arrangement",
    "R-16": "any adverse change in the vendor's published financial position",
}
