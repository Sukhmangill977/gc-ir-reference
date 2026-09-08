"""The adversarial corpus: one named mutation per manuscript failure class.

Manuscript Section XI-H lists the failure classes the compiler must reject:

    malformed references; duplicate IDs; conflicting predicates; expired
    approvals; stale catalog versions; missing evidence producers; unknown
    consequence classes; unauthorized action triples; C* rows with missing
    mandatory coverage; attempted in-place payload mutation (must fail the hash
    check); and post-retirement bundle use against the lifecycle registry.

Each entry here is a function that mutates a deep copy of a loaded case's
documents, plus the error code the compiler is expected to raise.  Both the
pytest suite and ``experiments/run_adversarial.py`` consume this single
definition, so there is exactly one source of truth for what was tested.

**Positive controls** are included deliberately: mutations that are *legitimate*
and must still compile.  A suite that only ever expects rejection cannot
distinguish a correct compiler from one that rejects everything.
"""

from __future__ import annotations

import copy

CASES = []


def case(case_id, name, expects, code, manuscript_ref, description,
         target="case_a", resign=True):
    """Register an adversarial or positive-control case.

    ``code`` is the error code the case must produce; a list means any one of
    them is acceptable, because a defect can legitimately be caught either by
    JSON Schema validation or by an Appendix A cross-field constraint, and which
    fires first is an implementation detail rather than a claim.

    ``resign`` (default True) re-signs every mutated governance artifact with its
    legitimate authority key before compilation.  Without it, every mutation
    would be rejected at Phi step 1 as a broken signature, which would mask the
    constraint the case exists to exercise.  Re-signing models the realistic
    failure the manuscript's constraints are written against: a governance forum
    that validly signs a *structurally defective* artifact.  The three cases that
    test signature integrity itself set ``resign=False``.
    """

    def decorator(func):
        CASES.append(
            {
                "id": case_id,
                "name": name,
                "expects": expects,  # "reject" or "compile"
                "expected_code": code,
                "manuscript_ref": manuscript_ref,
                "description": description,
                "target_case": target,
                "resign": resign,
                "mutate": func,
            }
        )
        return func

    return decorator


# ---------------------------------------------------------------------------
# Reference and identifier integrity
# ---------------------------------------------------------------------------


@case("ADV-001", "malformed obligation reference on a risk",
      "compile", "WC-01",
      "Section V; Appendix A constraint 8",
      "An unresolved obligation reference raises warning WC-01. It is a WARNING, "
      "not a disposition and not a rejection: 'an unresolved reference is not "
      "simultaneously a successful compilation and a rejection'.")
def adv_001(documents):
    documents["assessment"]["risk_register"][0]["obligation_refs"].append("NOT-AN-OBLIGATION")
    for record in documents["approved_control_specifications"]["records"]:
        if record["risk_id"] == documents["assessment"]["risk_register"][0]["risk_id"]:
            record["obligation_refs"].append("NOT-AN-OBLIGATION")
    return documents


@case("ADV-002", "malformed ACS reference in a disposition",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-D; Appendix A constraint 6",
      "A disposition binding an acs_id that does not exist cannot close Psi_K.")
def adv_002(documents):
    for record in documents["dispositions"]["records"]:
        if record["status"] == "runtime":
            record["acs_ids"] = ["ACS-DOES-NOT-EXIST"]
            break
    return documents


@case("ADV-003", "duplicate risk_id in the register",
      "reject", ["DUPLICATE_RISK_ID", "REFINEMENT_NOT_CLOSED"],
      "Section IV-D",
      "Two register rows sharing an identifier make totality unverifiable.")
def adv_003(documents):
    register = documents["assessment"]["risk_register"]
    clone = copy.deepcopy(register[0])
    register.append(clone)
    return documents


@case("ADV-004", "duplicate acs_id in the specification set",
      "reject", ["DUPLICATE_ACS_ID", "REFINEMENT_NOT_CLOSED"],
      "Section IV-C",
      "Two Approved Control Specifications sharing an identifier make the "
      "judgment record's selection ambiguous.")
def adv_004(documents):
    records = documents["approved_control_specifications"]["records"]
    clone = copy.deepcopy(records[0])
    clone["gcir_id"] = clone["gcir_id"] + "-DUP"
    records.append(clone)
    return documents


@case("ADV-005", "duplicate gcir_id across two specifications",
      "reject", ["DUPLICATE_GCIR_ID", "REFINEMENT_NOT_CLOSED"],
      "Section V",
      "Two predicates sharing a GC-IR identifier break the receipt's "
      "requirement reference.")
def adv_005(documents):
    records = documents["approved_control_specifications"]["records"]
    records[1]["gcir_id"] = records[0]["gcir_id"]
    return documents


@case("ADV-006", "risk with no disposition at all",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-D",
      "Totality requires exactly one disposition per risk.")
def adv_006(documents):
    documents["dispositions"]["records"] = documents["dispositions"]["records"][:-1]
    return documents


@case("ADV-007", "risk with two dispositions",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-D",
      "|Delta(r_i)| must equal 1.")
def adv_007(documents):
    records = documents["dispositions"]["records"]
    duplicate = copy.deepcopy(records[0])
    records.append(duplicate)
    return documents


# ---------------------------------------------------------------------------
# Release admissibility, approvals and separation of duty
# ---------------------------------------------------------------------------


@case("ADV-008", "unresolved disposition blocks release",
      "reject", "RELEASE_INADMISSIBLE",
      "Section IV-D",
      "A bundle is release-admissible only if no risk is unresolved.")
def adv_008(documents):
    records = documents["dispositions"]["records"]
    for record in records:
        if record["status"] == "nonruntime":
            record.clear()
            record.update(
                {
                    "risk_id": "R-14",
                    "status": "unresolved",
                    "reason_code": "RC-05",
                    "blocked_authority_scope": [
                        "research_agent/publish_report/research_report/internal_distribution"
                    ],
                }
            )
            break
    documents["judgment_record"]["disposition_decisions"] = [
        d for d in documents["judgment_record"].get("disposition_decisions", [])
    ]
    return documents


@case("ADV-009", "expired ACS approval at compile time",
      "reject", "A9_EXPIRED_APPROVAL",
      "Appendix A constraint 9",
      "No expired approval may enter a release-admissible bundle.")
def adv_009(documents):
    documents["approved_control_specifications"]["records"][0]["validity_interval"][
        "effective_until"
    ] = "2026-02-01T00:00:01Z"
    return documents


@case("ADV-010", "assessor is also the acceptor",
      "reject", "A10_SEPARATION_OF_DUTY",
      "Section III Step 1; Appendix A constraint 10",
      "The party who performs the assessment may not be the party who accepts "
      "residual risk. 'A bundle in which the assessor and the acceptor are the "
      "same identity fails structural validation.'")
def adv_010(documents):
    documents["assessment"]["metadata"]["assessor"] = documents["assessment"][
        "metadata"
    ]["accountable_exec"]
    return documents


@case("ADV-011", "accepted risk whose acceptor is not M.accountable_exec",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Appendix A constraint 11",
      "An accepted-risk disposition's acceptor must resolve to M.accountable_exec.")
def adv_011(documents):
    for record in documents["dispositions"]["records"]:
        if record["status"] == "nonruntime":
            risk_id = record["risk_id"]
            record.clear()
            record.update(
                {
                    "risk_id": risk_id,
                    "status": "accepted",
                    "scope": "the retrieval concentration exposure for one review cycle",
                    "rationale": "fixture: acceptance signed by the wrong authority",
                    "acceptor": "technology.applied_ai_platform",
                    "approval_time": "2026-01-20T14:00:00Z",
                    "expiry": "2026-12-01T00:00:00Z",
                }
            )
            break
    return documents


@case("ADV-012", "accepted risk already past expiry at compile time",
      "reject", "A11_ACCEPTANCE_BOUNDS",
      "Appendix A constraint 11",
      "No release-admissible bundle contains an acceptance already past expiry "
      "at compile time.")
def adv_012(documents):
    for record in documents["dispositions"]["records"]:
        if record["status"] == "nonruntime":
            risk_id = record["risk_id"]
            record.clear()
            record.update(
                {
                    "risk_id": risk_id,
                    "status": "accepted",
                    "scope": "the retrieval concentration exposure",
                    "rationale": "fixture: acceptance that expired before compile time",
                    "acceptor": "exec.head_of_research",
                    "approval_time": "2026-01-20T14:00:00Z",
                    "expiry": "2026-02-01T00:00:01Z",
                }
            )
            break
    return documents


# ---------------------------------------------------------------------------
# Catalog, version binding and signatures
# ---------------------------------------------------------------------------


@case("ADV-013", "event type that resolves to no catalog template",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-B; Appendix B halt(UNRESOLVED_TEMPLATE)",
      "'A register row whose approved event_type does not resolve to a catalog "
      "entry is not interpreted heuristically.' No best-match fallback exists.")
def adv_013(documents):
    documents["approved_control_specifications"]["records"][0]["event_type"] = (
        "an_event_type_the_catalog_has_never_heard_of"
    )
    for selection in documents["judgment_record"]["selections"]:
        if selection["acs_id"] == documents["approved_control_specifications"]["records"][0]["acs_id"]:
            selection["event_type"] = "an_event_type_the_catalog_has_never_heard_of"
    return documents


@case("ADV-014", "template id that resolves to no catalog template",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-B",
      "Resolution is exact on (event_type, template_id); a near-miss is not a hit.")
def adv_014(documents):
    records = documents["approved_control_specifications"]["records"]
    records[0]["template_id"] = records[0]["template_id"] + "-V2"
    for selection in documents["judgment_record"]["selections"]:
        if selection["acs_id"] == records[0]["acs_id"]:
            selection["template_id"] = records[0]["template_id"]
    return documents


@case("ADV-015", "stale catalog version cited by the judgment record",
      "reject", "VERSION_BINDING_MISMATCH",
      "Section IV-B; Section VI-A step 1",
      "'Addition, removal, or semantic alteration of a catalog entry is a "
      "reassessment trigger.' A stale catalog is not a compilable input.")
def adv_015(documents):
    documents["control_derivation_catalog"]["version"] = "0.9"
    return documents


@case("ADV-016", "catalog bound to a different version binding",
      "reject", "VERSION_BINDING_MISMATCH",
      "Section III Step 1; Section VI-A step 1",
      "Compilation output inherits M.version_binding; a catalog bound elsewhere "
      "cannot contribute to it.")
def adv_016(documents):
    documents["control_derivation_catalog"]["version_binding_ref"] = "VB-SOME-OTHER-1.0"
    return documents


@case("ADV-017", "invariant bound to a different version binding",
      "reject", "VERSION_BINDING_MISMATCH",
      "Section VI-B",
      "A compiler invariant authorized under another binding is not authorized here.")
def adv_017(documents):
    documents["invariant_register"]["invariants"][0]["version_binding_ref"] = "VB-OTHER"
    return documents


@case("ADV-018", "tampered assessment payload with intact signature envelope",
      "reject", "SIGNATURE_INVALID",
      "Section VI-A step 1",
      "Phi verifies the signature over the exact document content. Editing the "
      "content after signing breaks verification.", resign=False)
def adv_018(documents):
    documents["assessment"]["metadata"]["scope"] = (
        documents["assessment"]["metadata"]["scope"] + " (silently widened)"
    )
    return documents


@case("ADV-019", "governance artifact signed by an unauthorized key",
      "reject", "SIGNATURE_INVALID",
      "Section VI-A step 1",
      "The signing key must be the approved authority for that artifact.", resign=False)
def adv_019(documents, keyring=None):
    if keyring is not None:
        body = {k: v for k, v in documents["control_derivation_catalog"].items()
                if k != "signature"}
        documents["control_derivation_catalog"]["signature"] = keyring.sign(
            body, "key.unauthorized_party", domain="catalog",
            signing_time="2026-01-20T14:05:00Z",
        )
    return documents


@case("ADV-020", "governance artifact with its signature removed",
      "reject", "SIGNATURE_INVALID",
      "Section VI-A step 1",
      "Phi requires signed inputs; an unsigned artifact is not compilable.", resign=False)
def adv_020(documents):
    documents["approved_control_specifications"].pop("signature", None)
    return documents


# ---------------------------------------------------------------------------
# Authority closure
# ---------------------------------------------------------------------------


@case("ADV-021", "action tuple outside S.authority_matrix",
      "reject", "AUTHORITY_CLOSURE_VIOLATION",
      "Section III Step 2; Appendix A constraint 5",
      "'If an action does not appear in S.authority_matrix, no predicate can "
      "permit it.'")
def adv_021(documents):
    documents["approved_control_specifications"]["records"][0]["action"] = "place_order"
    return documents


@case("ADV-022", "action parameter outside the approved parameter schema",
      "reject", "AUTHORITY_CLOSURE_VIOLATION",
      "Section VI-A step 4",
      "A predicate binding a parameter the matrix never authorized is outside "
      "the approved authority even though its four-tuple resolves.")
def adv_022(documents):
    documents["approved_control_specifications"]["records"][0]["action_parameters"][
        "unapproved_parameter"
    ] = "anything"
    return documents


@case("ADV-023", "action parameter value outside the approved enum",
      "reject", "AUTHORITY_CLOSURE_VIOLATION",
      "Section VI-A step 4",
      "Parameter conformance is part of authority closure, not a soft check.")
def adv_023(documents):
    documents["approved_control_specifications"]["records"][0]["action_parameters"][
        "distribution_list"
    ] = "external_client_distribution"
    return documents


@case("ADV-024", "parameter_schema_ref pointing at another matrix row's schema",
      "reject", "AUTHORITY_CLOSURE_VIOLATION",
      "Section VI-A step 4",
      "The referenced schema must be the one the matrix row actually carries.")
def adv_024(documents):
    documents["approved_control_specifications"]["records"][0][
        "parameter_schema_ref"
    ] = "PS-RETRIEVE"
    return documents


@case("ADV-025", "hazardous action path not present in the authority matrix",
      "reject", "AUTHORITY_CLOSURE_VIOLATION",
      "Section VII-A",
      "A hazardous path that is not authorized cannot be exercised and cannot "
      "need a gate; declaring one is a fixture error, not a coverage gap.")
def adv_025(documents):
    for risk in documents["assessment"]["risk_register"]:
        if risk.get("hazardous_action_paths"):
            risk["hazardous_action_paths"].append(
                {
                    "subject": "research_agent",
                    "action": "place_order",
                    "resource": "order_ticket",
                    "destination": "order_management_system",
                }
            )
            break
    return documents


# ---------------------------------------------------------------------------
# Unknown handling, thresholds and gate structure
# ---------------------------------------------------------------------------


@case("ADV-026", "mandatory gate with on_unknown = warn",
      "reject", "A2_MANDATORY_ON_UNKNOWN",
      "Section V; Section VI-A step 8; Appendix A constraint 2",
      "'For mandatory gates, on_unknown = fail is required, not default.' "
      "Indeterminacy must never become a silent mandatory pass.")
def adv_026(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record["gate_candidate"] == "mandatory":
            record["context_conditions"][0]["on_unknown"] = "warn"
            record["on_unknown"] = "warn"
            break
    return documents


@case("ADV-027", "mandatory gate with on_unknown = pass_with_approved_exception",
      "reject", "A2_MANDATORY_ON_UNKNOWN",
      "Section V; Appendix A constraint 2",
      "An approved fail-open exception is admissible only on a NON-mandatory "
      "condition; on a mandatory gate it is a rejection.")
def adv_027(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record["gate_candidate"] == "mandatory":
            record["context_conditions"][0]["on_unknown"] = "pass_with_approved_exception"
            record["on_unknown"] = "pass_with_approved_exception"
            break
    return documents


@case("ADV-028", "mandatory gate with on_fail != SAFE_STATE",
      "reject", "TEMPLATE_CONFORMANCE_FAILURE",
      "Appendix A constraint 1",
      "mandatory implies on_fail = SAFE_STATE; the catalog template's "
      "permitted_responses catch it first.")
def adv_028(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record["gate_candidate"] == "mandatory":
            record["on_fail"] = "WARN"
            break
    return documents


@case("ADV-029", "numeric condition with no threshold contract",
      "reject", "A3_THRESHOLD_CONTRACT_MISSING",
      "Section V commitment 4; Appendix A constraint 3",
      "'A numeric or temporal bound is not admissible until it carries "
      "operational definition, numerator, denominator, evidence source, ground "
      "truth, threshold rationale, uncertainty method, unit, and reproduction "
      "procedure.'")
def adv_029(documents):
    for record in documents["approved_control_specifications"]["records"]:
        for condition in record["context_conditions"]:
            if condition["operator"] in ("<", "<=", ">", ">="):
                condition["threshold_contract_ref"] = None
                return documents
    return documents


@case("ADV-030", "threshold contract that resolves to nothing",
      "reject", "A3_THRESHOLD_CONTRACT_UNRESOLVED",
      "Appendix A constraint 3",
      "A dangling threshold-contract reference is a rejection, not a warning.")
def adv_030(documents):
    for record in documents["approved_control_specifications"]["records"]:
        for condition in record["context_conditions"]:
            if condition["threshold_contract_ref"]:
                condition["threshold_contract_ref"] = "TC-DOES-NOT-EXIST"
                return documents
    return documents


@case("ADV-031", "threshold contract missing its unit",
      "reject", ["A3_THRESHOLD_UNIT_MISSING", "SCHEMA_VALIDATION_FAILED"],
      "Appendix A constraint 3",
      "Numeric or temporal operators require a threshold contract AND unit.")
def adv_031(documents):
    for contract in documents["threshold_contracts"]["contracts"].values():
        contract["unit"] = ""
        break
    return documents


@case("ADV-032", "threshold contract missing its uncertainty method",
      "reject", ["A3_THRESHOLD_CONTRACT_INCOMPLETE", "SCHEMA_VALIDATION_FAILED"],
      "Section V commitment 4",
      "A partial threshold contract is not a threshold contract.")
def adv_032(documents):
    for contract in documents["threshold_contracts"]["contracts"].values():
        contract["uncertainty_method"] = ""
        break
    return documents


@case("ADV-033", "weighted predicate with no aggregation block",
      "reject", ["A4_WEIGHTED_STRUCTURE", "SCHEMA_VALIDATION_FAILED"],
      "Section V commitment 3; Appendix A constraint 4",
      "'A record marked weighted is structurally invalid unless it carries "
      "aggregation_group, a positive weight, a normalized deficit function, a "
      "group threshold, and a response.'")
def adv_033(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record.get("soft_gate_type") == "weighted":
            record.pop("aggregation", None)
            return documents
    return documents


@case("ADV-034", "weighted predicate with a non-positive weight",
      "reject", ["A4_WEIGHTED_WEIGHT", "SCHEMA_VALIDATION_FAILED"],
      "Section V commitment 3; Appendix A constraint 4",
      "The weight must be positive.")
def adv_034(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record.get("aggregation"):
            record["aggregation"]["weight"] = 0
            return documents
    return documents


# ---------------------------------------------------------------------------
# Evidence semantics and evaluation basis
# ---------------------------------------------------------------------------


@case("ADV-035", "evidence producer outside the catalog's allowed_producers",
      "reject", "TEMPLATE_CONFORMANCE_FAILURE",
      "Section VI-A step 5",
      "'Validate evidence type and producer against the selected catalog entry.'")
def adv_035(documents):
    documents["approved_control_specifications"]["records"][0][
        "observable_producer"
    ] = "an_unapproved_producer_v9"
    return documents


@case("ADV-036", "evidence schema reference that the template does not name",
      "reject", "TEMPLATE_CONFORMANCE_FAILURE",
      "Section VI-A step 5",
      "The evidence schema must be the one the selected template declares.")
def adv_036(documents):
    documents["approved_control_specifications"]["records"][0][
        "evidence_schema_ref"
    ] = "ES-SOMETHING-ELSE"
    return documents


@case("ADV-037", "evaluation basis outside the closed set",
      "reject", ["SCHEMA_VALIDATION_FAILED", "TEMPLATE_CONFORMANCE_FAILURE"],
      "Section V commitment 2",
      "evaluation_basis is constrained to four values. A GC-IR condition never "
      "evaluates a probability directly.")
def adv_037(documents):
    documents["approved_control_specifications"]["records"][0][
        "evaluation_basis"
    ] = "probabilistic_classifier_score"
    return documents


@case("ADV-038", "operator outside the template's allowed_operators",
      "reject", "TEMPLATE_CONFORMANCE_FAILURE",
      "Section IV-B",
      "The catalog constrains which operators an event type may use.")
def adv_038(documents):
    documents["approved_control_specifications"]["records"][0]["operator"] = ">="
    return documents


@case("ADV-039", "expected value violating the template value schema",
      "reject", "TEMPLATE_CONFORMANCE_FAILURE",
      "Section IV-B",
      "The value schema is part of the approved template, not advisory.")
def adv_039(documents):
    documents["approved_control_specifications"]["records"][0]["expected_value"] = "maybe"
    return documents


@case("ADV-040", "triple template reused for a different action path",
      "reject", "TEMPLATE_CONFORMANCE_FAILURE",
      "Section IV-B",
      "A template approved for a publication event may not be reused to gate a "
      "tool call.")
def adv_040(documents):
    record = documents["approved_control_specifications"]["records"][0]
    record.update({"subject": "research_agent", "action": "invoke_tool",
                   "resource": "external_tool", "destination": "tool_gateway",
                   "parameter_schema_ref": "PS-INVOKE-TOOL",
                   "action_parameters": {"tool_id": "T", "invocation_class": "read_only"}})
    return documents


# ---------------------------------------------------------------------------
# C* classification and coverage
# ---------------------------------------------------------------------------


@case("ADV-041", "C* risk whose only gate is downgraded to advisory",
      "reject", "CSTAR_COVERAGE_INCOMPLETE",
      "Section VII-A; Appendix A constraint 12",
      "'Phi verifies CV structurally and rejects non-covering bundles.'")
def adv_041(documents):
    cstar_risks = {"R-05", "R-06", "R-08", "R-10", "R-13", "B-01", "B-04", "B-05", "B-06"}
    for record in documents["approved_control_specifications"]["records"]:
        if record["risk_id"] in cstar_risks:
            # Only the gate assignment is changed. on_fail stays SAFE_STATE and
            # on_unknown stays fail, so the catalog template's permitted_responses
            # cannot reject this first -- the coverage rule has to be what catches it.
            record["gate_candidate"] = "advisory"
            record["soft_gate_type"] = "advisory"
            return documents
    return documents


@case("ADV-042", "C* risk whose gate is marked supporting rather than decisive",
      "reject", "CSTAR_COVERAGE_INCOMPLETE",
      "Section VII-A",
      "'The ACS mandatory_role field records which specifications are decisive "
      "and which are supporting.' Coverage requires a DECISIVE gate.")
def adv_042(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record["risk_id"] in ("R-05", "B-04"):
            record["mandatory_role"] = "supporting"
            return documents
    return documents


@case("ADV-043", "C* risk declaring a second hazardous path with no gate",
      "reject", "CSTAR_COVERAGE_INCOMPLETE",
      "Section VII-A",
      "Coverage is required for EACH authorized hazardous action path, not for "
      "the risk as a whole.")
def adv_043(documents):
    for risk in documents["assessment"]["risk_register"]:
        if risk["risk_id"] == "R-05":
            risk["hazardous_action_paths"].append(
                {
                    "subject": "research_agent",
                    "action": "invoke_tool",
                    "resource": "external_tool",
                    "destination": "tool_gateway",
                }
            )
            return documents
    return documents


@case("ADV-044", "C* risk with no hazardous action path declared",
      "reject", "CSTAR_COVERAGE_INCOMPLETE",
      "Section VII-A",
      "A C* classification with no authorized hazardous path is an incomplete "
      "assessment, not a covered risk.")
def adv_044(documents):
    for risk in documents["assessment"]["risk_register"]:
        if risk["risk_id"] == "R-05":
            risk["hazardous_action_paths"] = []
            return documents
    return documents


@case("ADV-045", "consequence descriptor with an unknown materiality level",
      "reject", "MATERIALITY_UNKNOWN",
      "Section VII-A",
      "Materiality qualifies C* membership; an unrecognised level cannot be "
      "silently treated as below the boundary.")
def adv_045(documents):
    for row in documents["assessment"]["risk_analysis"]:
        if row["risk_id"] in ("R-05", "B-01"):
            row["consequence_descriptor"]["materiality"] = "quite_bad_actually"
            return documents
    return documents


@case("ADV-046", "C* profile member kind with no classification rule",
      "reject", "CSTAR_RULE_MISSING",
      "Section VII-A",
      "'Each classification records the approving authority, rationale, "
      "materiality boundary, effective date, and any authorized emergency-"
      "override procedure.'")
def adv_046(documents):
    documents["cstar_profile"]["member_kinds"].append("a_kind_with_no_rule")
    return documents


@case("ADV-047", "risk analysis row with no consequence descriptor",
      "compile", None,
      "Section V reason code RC-05",
      "A missing descriptor makes the row non-C*. That is admissible ONLY "
      "because the row is dispositioned non-runtime; the seeded validation row "
      "VS-01 exercises the RC-05 disposition path directly.")
def adv_047(documents):
    for row in documents["assessment"]["risk_analysis"]:
        if row["risk_id"] == "R-15":
            row.pop("consequence_descriptor", None)
            return documents
    return documents


# ---------------------------------------------------------------------------
# Psi_K closure
# ---------------------------------------------------------------------------


@case("ADV-048", "runtime disposition with no signed selection in J",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-A",
      "Psi_K is single-valued only given J. A runtime disposition the judgment "
      "record never authorized is not a closure.")
def adv_048(documents):
    documents["judgment_record"]["selections"] = documents["judgment_record"][
        "selections"
    ][:-1]
    return documents


@case("ADV-049", "judgment record selecting a template the catalog lacks",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-A, IV-B",
      "The catalog constrains what may be selected; the judgment record "
      "establishes who authorized the selection. Both must hold.")
def adv_049(documents):
    documents["judgment_record"]["selections"][0]["template_id"] = "T-INVENTED"
    return documents


@case("ADV-050", "ACS approver differing from the judgment record's approver",
      "reject", "REFINEMENT_NOT_CLOSED",
      "Section IV-A",
      "The approval recorded on the specification must be the approval the "
      "judgment record carries.")
def adv_050(documents):
    documents["approved_control_specifications"]["records"][0]["approver"] = (
        "someone.else"
    )
    return documents


@case("ADV-051", "judgment record bound to a different assessment",
      "reject", "VERSION_BINDING_MISMATCH",
      "Section IV-A; Section VI-A step 1",
      "J is versioned and bound; a judgment record for another assessment "
      "cannot close this one.")
def adv_051(documents):
    documents["judgment_record"]["assessment_ref"]["binding_id"] = "VB-SOMETHING-ELSE"
    return documents


@case("ADV-052", "non-runtime disposition with no reason code",
      "reject", ["SCHEMA_VALIDATION_FAILED", "REFINEMENT_NOT_CLOSED"],
      "Section V; Appendix A",
      "A NonRuntimeDisposition requires a typed reason code from the closed "
      "v1.0 set.")
def adv_052(documents):
    for record in documents["dispositions"]["records"]:
        if record["status"] == "nonruntime":
            record.pop("reason_code")
            return documents
    return documents


@case("ADV-053", "non-runtime disposition with a reason code outside the closed set",
      "reject", ["SCHEMA_VALIDATION_FAILED", "REFINEMENT_NOT_CLOSED"],
      "Section V",
      "'Reason and warning codes are closed at schema v1.0; extension is a "
      "schema-version event.' RC-04 is not defined by the manuscript.")
def adv_053(documents):
    for record in documents["dispositions"]["records"]:
        if record["status"] == "nonruntime":
            record["reason_code"] = "RC-04"
            return documents
    return documents


@case("ADV-054", "non-runtime disposition that also binds an ACS",
      "reject", ["REFINEMENT_NOT_CLOSED", "SCHEMA_VALIDATION_FAILED"],
      "Section IV-D",
      "Only a runtime disposition binds Approved Control Specifications.")
def adv_054(documents):
    for record in documents["dispositions"]["records"]:
        if record["status"] == "nonruntime":
            record["acs_ids"] = ["ACS-0001-01"]
            return documents
    return documents


# ---------------------------------------------------------------------------
# Positive controls -- legitimate variations that MUST still compile
# ---------------------------------------------------------------------------


@case("POS-001", "unmutated case", "compile", None,
      "Sections IX, X",
      "Positive control: the committed case compiles.")
def pos_001(documents):
    return documents


@case("POS-002", "reordered register and specification records", "compile", None,
      "Section VI-C",
      "Positive control: order is not semantically meaningful, so reordering "
      "must compile AND produce the same payload hash.")
def pos_002(documents):
    documents["assessment"]["risk_register"].reverse()
    documents["assessment"]["risk_analysis"].reverse()
    documents["approved_control_specifications"]["records"].reverse()
    documents["dispositions"]["records"].reverse()
    return documents


@case("POS-003", "non-mandatory condition with an approved fail-open exception",
      "compile", None,
      "Section V commitment 1",
      "Positive control: 'for non-mandatory conditions any fail-open exception "
      "must be explicitly approved and carries the approver's identity'. With "
      "the approval present, this is admissible.")
def pos_003(documents):
    for record in documents["approved_control_specifications"]["records"]:
        if record["gate_candidate"] in ("advisory", "weighted"):
            record["context_conditions"][0]["on_unknown"] = "pass_with_approved_exception"
            record["context_conditions"][0]["fail_open_approval"] = {
                "approver": "forum.chair_l_tremblay",
                "approval_time": "2026-01-20T14:00:00Z",
                "rationale": "Advisory monitoring signal; an unavailable telemetry "
                "artifact must not suppress distribution of an otherwise compliant brief.",
            }
            record["on_unknown"] = "pass_with_approved_exception"
            return documents
    return documents


@case("POS-004", "C* risk carrying an additional supporting advisory predicate",
      "compile", None,
      "Section VII-A",
      "Positive control: 'A C* risk may, in addition, generate supporting "
      "advisory or weighted predicates: C* membership mandates coverage, not "
      "mandatory status for every predicate derived from r_i.'")
def pos_004(documents):
    records = documents["approved_control_specifications"]["records"]
    source = next(r for r in records if r["risk_id"] == "R-06")
    extra = copy.deepcopy(source)
    extra["acs_id"] = "ACS-0006-02"
    extra["gcir_id"] = "GCIR-0007-SUPPORT"
    extra["gate_candidate"] = "advisory"
    extra["soft_gate_type"] = "advisory"
    extra["mandatory_role"] = "supporting"
    extra["on_fail"] = "WARN"
    extra["on_unknown"] = "warn"
    extra["event_type"] = "advisory_framing_flag"
    extra["template_id"] = "T-FRAMING-ADVISORY"
    extra["observable_id"] = "framing_flags_absent"
    extra["observable_class"] = "framing_flag_set"
    extra["observable_producer"] = "editorial_metrics_service_v1"
    extra["evidence_schema_ref"] = "ES-FRAMING-FLAGS"
    extra["operator"] = "=="
    extra["expected_value"] = True
    extra["evaluation_basis"] = "structural_check"
    extra["threshold_contract_ref"] = None
    extra["evidence_requirements"] = ["draft_hash", "flagged_section_ids"]
    extra["context_conditions"] = [
        {
            "attribute": "framing_flags_absent",
            "operator": "==",
            "value": True,
            "unit": None,
            "on_unknown": "warn",
            "required": True,
            "evidence_producer": "editorial_metrics_service_v1",
            "evidence_schema_ref": "ES-FRAMING-FLAGS",
            "threshold_contract_ref": None,
            "temporal_window": None,
        }
    ]
    records.append(extra)
    for record in documents["dispositions"]["records"]:
        if record["risk_id"] == "R-06":
            record["acs_ids"].append("ACS-0006-02")
    documents["judgment_record"]["selections"].append(
        {
            "selection_id": "J-SEL-900",
            "risk_id": "R-06",
            "acs_id": "ACS-0006-02",
            "event_type": "advisory_framing_flag",
            "template_id": "T-FRAMING-ADVISORY",
            "selected_by": "compliance.head_research_supervision",
            "selection_time": "2026-01-19T11:00:00Z",
            "rationale": "Supporting advisory signal alongside the decisive "
            "disclosure gate; recorded as supporting, not decisive.",
        }
    )
    documents["judgment_record"]["approvals"].append(
        {
            "acs_id": "ACS-0006-02",
            "approver": "forum.chair_l_tremblay",
            "approval_time": "2026-01-20T14:00:00Z",
            "forum": "ai_governance_forum",
        }
    )
    return documents


@case("POS-005", "risk yielding several predicates", "compile", None,
      "Sections IV-D, VI-E",
      "Positive control: 'one risk may produce zero, one, or several predicates "
      "without invalidating totality'. R-04, R-07 and R-09 each carry two.")
def pos_005(documents):
    return documents


def all_cases(target=None):
    if target is None:
        return list(CASES)
    return [entry for entry in CASES if entry["target_case"] == target]


def applicable_to(entry, case_id):
    """Case B lacks non-runtime rows and some Case A identifiers."""
    return entry["target_case"] == case_id
