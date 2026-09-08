"""The deterministic compiler Phi (manuscript Section VI and Appendix B).

    Phi : (M, S, O, R, A, K, D, Delta) -> (P, G, E, B)

Determinism argument (Appendix B), and how each source is closed here:

======================  =====================================================
nondeterminism source   how it is closed in this implementation
======================  =====================================================
iteration order         ``canonical_order`` sorts every collection by a total
                        key before it is walked or serialized
serialization           ``gcir.canonicalization`` (RFC 8785)
encoding                UTF-8, fixed, in ``canonicalize``
time                    no clock is read anywhere in this module; the compile
                        time is a *declared input*, and it never enters the
                        payload
lifecycle state         external signed registry (``gcir.lifecycle``)
matching                ``catalog.exact_lookup`` only -- no similarity, no
                        best-match, no default template, no fallback
randomness              none: this module imports no RNG
======================  =====================================================

There is no language model, embedding, classifier or heuristic in this file or in
anything it calls.  ``tests/adversarial/test_no_inference.py`` asserts that
statically over the shipped source.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Tuple

from . import authority as authority_mod
from . import validation as validation_mod
from .canonicalization import hash_payload
from .catalog import ControlDerivationCatalog
from .coverage import CStarProfile, classify_risks, verify_cv
from .models import (
    ActionTuple,
    ApprovedControlSpecification,
    CatalogResolutionError,
    CompilationResult,
    CompiledBundle,
    Disposition,
    ReleaseInadmissibleError,
    SignatureError,
    ValidationError,
    VersionBindingError,
)
from .refinement import close_relation, release_admissible
from .signatures import strip_envelope

GCIR_SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# canonical_order -- Appendix B's ``canonical_order(...)``
# ---------------------------------------------------------------------------


def canonical_order(items, key):
    """Total, locale-independent ordering.

    Sorting is by the UTF-8 code-unit sequence of the key, never by a
    locale-sensitive collation.  ``str.encode`` is used explicitly so that a
    process running under a non-C locale cannot change the result.
    """
    return sorted(items, key=lambda item: key(item).encode("utf-8"))


# ---------------------------------------------------------------------------
# CompilerInputs
# ---------------------------------------------------------------------------


class CompilerInputs:
    """Everything Phi consumes, with the signature envelopes kept alongside.

    ``compile_time`` is a *declared* input, not a clock reading.  It is used for
    approval-expiry checks (Appendix A constraints 9 and 11) and never enters the
    hashed payload.
    """

    def __init__(
        self,
        assessment,
        catalog,
        judgment,
        dispositions,
        acs_records,
        invariants,
        cstar_profile,
        threshold_contracts,
        compile_time,
        signatures=None,
        keyring=None,
        signing_authorities=None,
        policy_metadata=None,
        bundle_effective_from=None,
    ):
        self.assessment = assessment
        self.catalog = catalog
        self.judgment = judgment
        self.dispositions = dispositions
        self.acs_records = acs_records
        self.invariants = invariants
        self.cstar_profile = cstar_profile
        self.threshold_contracts = threshold_contracts
        self.compile_time = compile_time
        self.signatures = signatures or {}
        self.keyring = keyring
        self.signing_authorities = signing_authorities or {}
        self.policy_metadata = policy_metadata or {}
        self.bundle_effective_from = bundle_effective_from


# ---------------------------------------------------------------------------
# Step 1: signatures and version bindings
# ---------------------------------------------------------------------------


def _verify_signatures_and_versions(inputs):
    """Appendix B step 1: ``validate_signatures_and_versions(M, S, O, R, A, K, D, Delta, INV)``."""
    if inputs.keyring is not None:
        for artifact_name, (document, domain) in sorted(inputs.signatures.items()):
            envelope = document.get("signature")
            if not envelope:
                raise SignatureError(
                    "governance artifact %r carries no signature; Phi step 1 "
                    "requires signed inputs" % artifact_name
                )
            expected = inputs.signing_authorities.get(artifact_name)
            inputs.keyring.verify(
                strip_envelope(document), envelope, domain=domain, expected_key_id=expected
            )

    binding = inputs.assessment.version_binding
    problems = []

    if inputs.catalog.version_binding_ref != binding["binding_id"]:
        problems.append(
            "catalog %s is bound to %r but the assessment declares version binding %r"
            % (
                inputs.catalog.catalog_id,
                inputs.catalog.version_binding_ref,
                binding["binding_id"],
            )
        )
    if inputs.judgment.assessment_ref["binding_id"] != binding["binding_id"]:
        problems.append(
            "judgment record %s is bound to %r, not to the assessment binding %r"
            % (
                inputs.judgment.judgment_id,
                inputs.judgment.assessment_ref["binding_id"],
                binding["binding_id"],
            )
        )
    if inputs.judgment.catalog_ref["catalog_id"] != inputs.catalog.catalog_id:
        problems.append(
            "judgment record cites catalog %r but catalog %r was supplied"
            % (inputs.judgment.catalog_ref["catalog_id"], inputs.catalog.catalog_id)
        )
    if inputs.judgment.catalog_ref["version"] != inputs.catalog.version:
        problems.append(
            "judgment record cites catalog version %r but catalog version %r was "
            "supplied -- a stale catalog is a reassessment trigger, not a "
            "compilable input"
            % (inputs.judgment.catalog_ref["version"], inputs.catalog.version)
        )
    if inputs.cstar_profile.document["version_binding_ref"] != binding["binding_id"]:
        problems.append(
            "C* profile %s is bound to %r, not to the assessment binding %r"
            % (
                inputs.cstar_profile.profile_id,
                inputs.cstar_profile.document["version_binding_ref"],
                binding["binding_id"],
            )
        )
    for invariant in inputs.invariants:
        if invariant["version_binding_ref"] != binding["binding_id"]:
            problems.append(
                "invariant %s is bound to %r, not to the assessment binding %r"
                % (invariant["invariant_id"], invariant["version_binding_ref"], binding["binding_id"])
            )

    if problems:
        raise VersionBindingError(
            "version binding validation failed: %s" % "; ".join(problems),
            detail={"problems": problems},
        )


# ---------------------------------------------------------------------------
# Predicate instantiation
# ---------------------------------------------------------------------------


def _classify_gate(acs, cstar_flag):
    """Appendix B ``classify_gate_source`` + gate assignment.

    ``gate = mandatory if (gate_source == C_STAR and mandatory_role == decisive)
                       or gate_source == OTHER_MANDATORY
              else approved_soft_gate(acs)``

    A C* risk may carry supporting advisory/weighted predicates; coverage is
    asserted at bundle level, not per predicate.
    """
    declared = acs["gate_candidate"]
    if cstar_flag == 1 and declared == "mandatory":
        gate_source = "C_STAR"
    elif declared == "mandatory":
        gate_source = "OTHER_MANDATORY"
    else:
        gate_source = "SOFT"

    if gate_source == "C_STAR" and acs.mandatory_role == "decisive":
        gate_type = "mandatory"
    elif gate_source == "OTHER_MANDATORY":
        gate_type = "mandatory"
    elif gate_source == "C_STAR":
        # A C*-classified risk's *supporting* specification is not itself decisive.
        gate_type = acs.get("soft_gate_type", "advisory")
        gate_source = "SOFT"
    else:
        gate_type = acs.get("soft_gate_type", "advisory")

    return gate_type, gate_source


def _instantiate_predicates(template, acs, risk, cstar_flag, gate_type, gate_source):
    """Appendix B ``instantiate_predicates(template, acs)``.

    One ACS yields one compiled predicate carrying every context condition the
    specification approved.  Predicate cardinality per *risk* varies because a
    risk may carry several ACS -- which is exactly the independence Section VI-E
    requires.
    """
    conditions = []
    for index, condition in enumerate(acs["context_conditions"]):
        conditions.append(
            {
                "attribute": condition["attribute"],
                "operator": condition["operator"],
                "value": condition["value"],
                "unit": condition.get("unit"),
                "on_unknown": condition["on_unknown"],
                "required": condition.get("required", True),
                "evidence_producer": condition["evidence_producer"],
                "evidence_schema_ref": condition.get(
                    "evidence_schema_ref", acs["evidence_schema_ref"]
                ),
                "threshold_contract_ref": condition.get("threshold_contract_ref"),
                "temporal_window": condition.get("temporal_window"),
                "condition_index": index,
            }
        )

    predicate = {
        "record_type": "CompiledPredicate",
        "gcir_id": acs["gcir_id"],
        "acs_id": acs.acs_id,
        "schema_version": GCIR_SCHEMA_VERSION,
        "origin": {
            "origin_type": "risk_derived",
            "origin_id": risk["risk_id"],
            "authorized_by": acs["approver"],
        },
        "requirement_ref": {
            "risk_id": risk["risk_id"],
            "obligation_ids": sorted(acs["obligation_refs"]),
        },
        "subject": acs["subject"],
        "action": acs["action"],
        "resource": acs["resource"],
        "destination": acs["destination"],
        "action_parameters": acs.get("action_parameters", {}),
        "parameter_schema_ref": acs["parameter_schema_ref"],
        "context_conditions": conditions,
        "evidence_producer": acs["observable_producer"],
        "evidence_schema_ref": acs["evidence_schema_ref"],
        "evaluation_basis": acs["evaluation_basis"],
        "gate_type": gate_type,
        "gate_source": gate_source,
        "mandatory_role": acs.mandatory_role,
        "on_fail": acs["on_fail"],
        "escalation": acs["escalation"],
        "evidence_requirement": sorted(acs["evidence_requirements"]),
        "version_binding_ref": acs["version_binding_ref"],
        "validity": {"effective_from": acs["validity_interval"]["effective_from"]},
        "warrant_boundary": acs["warrant_boundary"],
        "evidence_semantics": acs["evidence_semantics"],
        "decision_semantics": acs["decision_semantics"],
        "catalog_ref": {
            "event_type": template["event_type"],
            "template_id": template["template_id"],
        },
        "c_star": cstar_flag,
    }
    if acs.get("aggregation"):
        predicate["aggregation"] = copy.deepcopy(acs["aggregation"])
    if acs.get("conflict_group"):
        predicate["conflict_group"] = acs["conflict_group"]
    if acs.get("policy_id"):
        predicate["policy_id"] = acs["policy_id"]
    if acs.get("input_provenance"):
        # Section VII-H: declared input-provenance enumeration on an
        # already-classified consequential decision.
        predicate["input_provenance"] = copy.deepcopy(acs["input_provenance"])
    return [predicate]


def _instantiate_invariant(invariant, assessment):
    """Appendix B ``instantiate_invariant(inv, M, S)``.

    Compiler invariants are not orphan controls: each cites an approved system
    requirement recorded in the invariant register INV (Section VI-B).
    """
    conditions = []
    for index, condition in enumerate(invariant["context_conditions"]):
        value = condition["value"]
        if condition.get("value_from") == "M.version_binding":
            value = assessment.version_binding["fingerprint"]
        conditions.append(
            {
                "attribute": condition["attribute"],
                "operator": condition["operator"],
                "value": value,
                "unit": condition.get("unit"),
                "on_unknown": condition["on_unknown"],
                "required": condition.get("required", True),
                "evidence_producer": condition["evidence_producer"],
                "evidence_schema_ref": condition["evidence_schema_ref"],
                "threshold_contract_ref": condition.get("threshold_contract_ref"),
                "temporal_window": condition.get("temporal_window"),
                "condition_index": index,
            }
        )
    return {
        "record_type": "CompiledPredicate",
        "gcir_id": invariant["gcir_id"],
        "acs_id": None,
        "schema_version": GCIR_SCHEMA_VERSION,
        "origin": {
            "origin_type": "compiler_invariant",
            "origin_id": invariant["invariant_id"],
            "authorized_by": invariant["approved_by"],
        },
        "requirement_ref": {
            "risk_id": None,
            "internal_requirement_id": invariant["invariant_id"],
            "obligation_ids": sorted(invariant.get("obligation_refs", [])),
        },
        "subject": invariant["subject"],
        "action": invariant["action"],
        "resource": invariant["resource"],
        "destination": invariant["destination"],
        "action_parameters": invariant.get("action_parameters", {}),
        "parameter_schema_ref": invariant["parameter_schema_ref"],
        "context_conditions": conditions,
        "evidence_producer": invariant["evidence_producer"],
        "evidence_schema_ref": invariant["evidence_schema_ref"],
        "evaluation_basis": invariant["evaluation_basis"],
        "gate_type": "mandatory",
        "gate_source": "OTHER_MANDATORY",
        "mandatory_role": "decisive",
        "on_fail": "SAFE_STATE",
        "escalation": invariant["escalation"],
        "evidence_requirement": sorted(invariant["evidence_requirements"]),
        "version_binding_ref": invariant["version_binding_ref"],
        "validity": {"effective_from": invariant["effective_from"]},
        "warrant_boundary": invariant["warrant_boundary"],
        "evidence_semantics": invariant["evidence_semantics"],
        "decision_semantics": invariant["decision_semantics"],
        "catalog_ref": None,
        "c_star": 0,
    }


# ---------------------------------------------------------------------------
# Disposition records (GC-IR non-predicate record family)
# ---------------------------------------------------------------------------


def _disposition_record(disposition):
    if disposition.status == "runtime":
        return {
            "record_type": "RuntimeDisposition",
            "risk_id": disposition.risk_id,
            "acs_ids": sorted(disposition.acs_ids),
        }
    if disposition.status == "nonruntime":
        return {
            "record_type": "NonRuntimeDisposition",
            "risk_id": disposition.risk_id,
            "reason_code": disposition.reason_code,
            "routed_to_control_family": disposition.routed_to_control_family,
            "control_ref": disposition.control_ref,
            "owner": disposition.owner,
            "approval": {
                "approver": disposition.approval["approver"],
                "approval_time": disposition.approval["approval_time"],
                "forum": disposition.approval["forum"],
            },
        }
    if disposition.status == "accepted":
        return {
            "record_type": "AcceptedRiskDisposition",
            "risk_id": disposition.risk_id,
            "scope": disposition.scope,
            "rationale": disposition.rationale,
            "acceptor": disposition.acceptor,
            "approval_time": disposition.approval_time,
            "expiry": disposition.expiry,
        }
    return {
        "record_type": "UnresolvedDisposition",
        "risk_id": disposition.risk_id,
        "reason_code": disposition.reason_code,
        "blocked_authority_scope": sorted(disposition.blocked_authority_scope or []),
    }


# ---------------------------------------------------------------------------
# Coverage matrix (obligation -> disposition -> specification -> predicate)
# ---------------------------------------------------------------------------


def _coverage_matrix(assessment, closure, predicates, cstar_flags, cstar_coverage):
    obligation_rows = []
    predicates_by_risk = {}
    for predicate in predicates:
        if predicate["origin"]["origin_type"] == "risk_derived":
            predicates_by_risk.setdefault(predicate["origin"]["origin_id"], []).append(
                predicate["gcir_id"]
            )

    disposition_index = closure.disposition_index
    for obligation in canonical_order(assessment.obligations, lambda o: o["obligation_id"]):
        obligation_id = obligation["obligation_id"]
        linked_risks = sorted(
            risk["risk_id"]
            for risk in assessment.risk_register
            if obligation_id in risk.get("obligation_refs", [])
        )
        statuses = sorted(
            {disposition_index[r].status for r in linked_risks if r in disposition_index}
        )
        obligation_rows.append(
            {
                "obligation_id": obligation_id,
                "requirement_class": obligation["requirement_class"],
                "risk_ids": linked_risks,
                "disposition_statuses": statuses,
                "predicate_ids": sorted(
                    gid for r in linked_risks for gid in predicates_by_risk.get(r, [])
                ),
                "disposed": bool(statuses)
                and all(s in ("runtime", "nonruntime", "accepted") for s in statuses),
            }
        )

    risk_rows = []
    for risk in canonical_order(assessment.risk_register, lambda r: r["risk_id"]):
        risk_id = risk["risk_id"]
        disposition = disposition_index[risk_id]
        risk_rows.append(
            {
                "risk_id": risk_id,
                "obligation_ids": sorted(risk.get("obligation_refs", [])),
                "disposition_status": disposition.status,
                "reason_code": disposition.reason_code,
                "acs_ids": sorted(disposition.acs_ids),
                "predicate_ids": sorted(predicates_by_risk.get(risk_id, [])),
                "c_star": cstar_flags[risk_id],
            }
        )

    return {
        "obligations": obligation_rows,
        "risks": risk_rows,
        "c_star_coverage": cstar_coverage,
    }


# ---------------------------------------------------------------------------
# Phi
# ---------------------------------------------------------------------------


def compile_bundle(inputs, verify_signatures=True):
    """Run Phi and return a ``CompilationResult``.

    Follows the Appendix B pseudocode step for step.
    """
    assessment = inputs.assessment
    warnings = []

    # --- validate_signatures_and_versions ---------------------------------
    if verify_signatures:
        _verify_signatures_and_versions(inputs)
    else:
        _verify_signatures_and_versions(
            CompilerInputs(
                assessment=assessment,
                catalog=inputs.catalog,
                judgment=inputs.judgment,
                dispositions=inputs.dispositions,
                acs_records=inputs.acs_records,
                invariants=inputs.invariants,
                cstar_profile=inputs.cstar_profile,
                threshold_contracts=inputs.threshold_contracts,
                compile_time=inputs.compile_time,
                signatures={},
                keyring=None,
                signing_authorities={},
            )
        )

    # --- separation of duty (Appendix A constraint 10) --------------------
    validation_mod.constraint_10_assessor_is_not_acceptor(assessment)

    # --- close Psi_K with the signed judgment record ----------------------
    closure = close_relation(
        assessment,
        inputs.catalog,
        inputs.judgment,
        inputs.dispositions,
        inputs.acs_records,
    )

    # --- validate_exactly_one_disposition_per_risk + release admissibility -
    admissible, blockers = release_admissible(closure)
    if not admissible:
        raise ReleaseInadmissibleError(
            "bundle is not release-admissible: %d unresolved disposition(s)"
            % len(blockers),
            detail={"blockers": blockers},
        )

    # --- approval validity (Appendix A constraints 9 and 11) --------------
    validation_mod.constraint_09_no_expired_approval(closure.acs_records, inputs.compile_time)
    validation_mod.constraint_11_acceptance_bounds(
        closure.dispositions, assessment, inputs.compile_time
    )

    cstar_flags = classify_risks(assessment, inputs.cstar_profile)
    matrix = assessment.authority_matrix
    acs_index = closure.acs_index
    risk_index = assessment.risk_index
    obligation_index = assessment.obligation_index
    invariant_index = {inv["invariant_id"]: inv for inv in inputs.invariants}

    predicates = []
    gate_map = {}
    escalation_map = {}

    # --- for r in canonical_order(R) --------------------------------------
    for risk in canonical_order(assessment.risk_register, lambda r: r["risk_id"]):
        disposition = closure.disposition_index[risk["risk_id"]]
        if disposition.status in ("nonruntime", "accepted"):
            continue  # recorded in Delta; traceable via the coverage matrix

        for acs_id in canonical_order(disposition.acs_ids, lambda x: x):
            acs = acs_index[acs_id]

            # Section VI-A steps 2-5, in the order the manuscript states them.

            # step 2: resolve event_type to exactly one approved template
            template = inputs.catalog.exact_lookup(acs["event_type"], acs["template_id"])

            # step 3: resolve the action tuple against S.authority_matrix
            action_tuple = acs.action_tuple
            entry = authority_mod.resolve_action_tuple(action_tuple, matrix)

            # step 4: validate action parameters against parameter_schema
            authority_mod.validate_parameters(
                action_tuple,
                acs.get("action_parameters", {}) or {},
                entry,
                parameter_schema_ref=acs["parameter_schema_ref"],
            )

            # step 5: validate evidence type and producer against the selected
            # catalog entry (and the rest of the template's conformance surface)
            inputs.catalog.check_acs_against_template(acs.data, template)

            # step 7: assign gate source and gate type under Section VII
            gate_type, gate_source = _classify_gate(acs, cstar_flags[risk["risk_id"]])

            # step 10: emit the predicate and its authorized origin
            for predicate in _instantiate_predicates(
                template, acs, risk, cstar_flags[risk["risk_id"]], gate_type, gate_source
            ):
                # steps 6, 8, 9 + Appendix A constraints 1-4, 6, 8
                validation_mod.constraint_01_mandatory_implies_safe_state(predicate, gate_type)
                validation_mod.constraint_02_mandatory_unknown_fails(predicate, gate_type)
                validation_mod.constraint_03_threshold_contract_and_unit(
                    predicate, inputs.threshold_contracts
                )
                validation_mod.constraint_04_weighted_structure(predicate, gate_type)
                validation_mod.constraint_06_risk_derived_resolves(
                    predicate, acs_index, risk_index
                )
                warnings.extend(
                    validation_mod.constraint_08_obligation_refs(predicate, obligation_index)
                )
                predicates.append(predicate)
                gate_map[predicate["gcir_id"]] = {
                    "gate_type": gate_type,
                    "gate_source": gate_source,
                    "mandatory_role": acs.mandatory_role,
                }
                escalation_map[predicate["gcir_id"]] = copy.deepcopy(acs["escalation"])

    # --- for inv in canonical_order(INV) ----------------------------------
    for invariant in canonical_order(inputs.invariants, lambda i: i["invariant_id"]):
        predicate = _instantiate_invariant(invariant, assessment)
        action_tuple = ActionTuple.from_mapping(predicate)
        entry = authority_mod.resolve_action_tuple(action_tuple, matrix)
        authority_mod.validate_parameters(
            action_tuple,
            predicate.get("action_parameters", {}) or {},
            entry,
            parameter_schema_ref=predicate["parameter_schema_ref"],
        )
        validation_mod.constraint_01_mandatory_implies_safe_state(predicate, "mandatory")
        validation_mod.constraint_02_mandatory_unknown_fails(predicate, "mandatory")
        validation_mod.constraint_03_threshold_contract_and_unit(
            predicate, inputs.threshold_contracts
        )
        validation_mod.constraint_07_invariant_resolves(predicate, invariant_index)
        warnings.extend(
            validation_mod.constraint_08_obligation_refs(predicate, obligation_index)
        )
        predicates.append(predicate)
        gate_map[predicate["gcir_id"]] = {
            "gate_type": "mandatory",
            "gate_source": "OTHER_MANDATORY",
            "mandatory_role": "decisive",
        }
        escalation_map[predicate["gcir_id"]] = copy.deepcopy(invariant["escalation"])

    predicates = canonical_order(predicates, lambda p: p["gcir_id"])
    duplicate = _first_duplicate([p["gcir_id"] for p in predicates])
    if duplicate is not None:
        raise ValidationError(
            "duplicate gcir_id %r in the compiled predicate set" % duplicate,
            code="DUPLICATE_GCIR_ID",
        )

    # --- bundle-level assertions (Appendix B) -----------------------------
    _assert_exactly_one_disposition_per_risk(assessment, closure)
    _assert_all_predicates_have_authorized_origin(predicates, risk_index, invariant_index)
    offenders = authority_mod.all_action_tuples_authorized(predicates, matrix)
    if offenders:
        raise ValidationError(
            "%d predicate(s) carry action tuples outside S.authority_matrix"
            % len(offenders),
            code="AUTHORITY_CLOSURE_VIOLATION",
            detail={"offenders": offenders},
        )
    _assert_no_mandatory_unknown_warns(predicates, gate_map)

    hazardous_paths = {
        risk["risk_id"]: authority_mod.hazardous_paths_for(risk["risk_id"], assessment)
        for risk in assessment.risk_register
    }
    cstar_coverage = verify_cv(
        assessment, inputs.cstar_profile, predicates, gate_map, hazardous_paths
    )

    coverage_matrix = _coverage_matrix(
        assessment, closure, predicates, cstar_flags, cstar_coverage
    )

    # --- payload -----------------------------------------------------------
    payload = build_payload(inputs, closure, predicates, gate_map, escalation_map, coverage_matrix)
    validation_mod.constraint_13_payload_is_hash_clean(payload)
    payload_hash = hash_payload(payload)

    bundle = CompiledBundle(payload=payload, payload_hash=payload_hash, warnings=list(warnings))

    statistics = {
        "risk_count": len(assessment.risk_register),
        "obligation_count": len(assessment.obligations),
        "acs_count": len(closure.acs_records),
        "predicate_count": len(predicates),
        "risk_derived_predicate_count": sum(
            1 for p in predicates if p["origin"]["origin_type"] == "risk_derived"
        ),
        "compiler_invariant_predicate_count": sum(
            1 for p in predicates if p["origin"]["origin_type"] == "compiler_invariant"
        ),
        "mandatory_gate_count": sum(
            1 for g in gate_map.values() if g["gate_type"] == "mandatory"
        ),
        "cstar_risk_count": sum(1 for v in cstar_flags.values() if v == 1),
        "warning_count": len(warnings),
    }
    return CompilationResult(bundle=bundle, warnings=warnings, statistics=statistics)


def build_payload(inputs, closure, predicates, gate_map, escalation_map, coverage_matrix):
    """Appendix B ``payload <- RFC8785_canonicalize(M.version_binding, K.version,
    C_star.version, Delta, P, G, E, CM)``.

    Nothing that varies between two semantically identical compilations may enter
    here: no clock, no nonce, no lifecycle field.  ``effective_from`` is a
    *declared* governance input, not a generated timestamp.
    """
    assessment = inputs.assessment
    dispositions = [
        _disposition_record(d)
        for d in canonical_order(closure.dispositions, lambda d: d.risk_id)
    ]

    payload = {
        "payload_type": "GcirPredicateBundle",
        "schema_version": GCIR_SCHEMA_VERSION,
        "bundle_id": inputs.policy_metadata.get("bundle_id", "BUNDLE-UNSPECIFIED"),
        "case_id": assessment.metadata["system_id"],
        "version_binding": {
            "binding_id": assessment.version_binding["binding_id"],
            "model_version": assessment.version_binding["model_version"],
            "prompt_version": assessment.version_binding["prompt_version"],
            "dataset_version": assessment.version_binding["dataset_version"],
            "policy_version": assessment.version_binding["policy_version"],
            "fingerprint": assessment.version_binding["fingerprint"],
        },
        "catalog_ref": {
            "catalog_id": inputs.catalog.catalog_id,
            "version": inputs.catalog.version,
            "content_hash": hash_payload(inputs.catalog.canonical_document()),
        },
        "cstar_profile_ref": {
            "profile_id": inputs.cstar_profile.profile_id,
            "version": inputs.cstar_profile.version,
            "member_kinds": sorted(inputs.cstar_profile.members),
            "content_hash": hash_payload(inputs.cstar_profile.canonical_document()),
        },
        "judgment_record_ref": {
            "judgment_id": inputs.judgment.judgment_id,
            "version": inputs.judgment.version,
        },
        "invariant_register_ref": {
            "invariant_ids": sorted(i["invariant_id"] for i in inputs.invariants),
        },
        "dispositions": dispositions,
        "predicates": predicates,
        "gate_map": {
            gid: gate_map[gid] for gid in canonical_order(sorted(gate_map), lambda x: x)
        },
        "escalation_map": {
            gid: escalation_map[gid]
            for gid in canonical_order(sorted(escalation_map), lambda x: x)
        },
        "coverage_matrix": coverage_matrix,
        "threshold_contracts": {
            k: inputs.threshold_contracts[k] for k in sorted(inputs.threshold_contracts)
        },
        "policy_metadata": {
            k: inputs.policy_metadata[k]
            for k in sorted(inputs.policy_metadata)
            if k != "bundle_id"
        },
        "validity": {
            "effective_from": inputs.bundle_effective_from
            or assessment.metadata["validity_interval"]["effective_from"]
        },
    }
    return payload


def sign_bundle(bundle, keyring, key_id, signing_time):
    """Attach a signature envelope.  The envelope never touches the payload."""
    envelope = keyring.sign(
        bundle.payload, key_id, domain="bundle", signing_time=signing_time
    )
    bundle.envelope = envelope
    return bundle


# ---------------------------------------------------------------------------
# Bundle-level assertions
# ---------------------------------------------------------------------------


def _first_duplicate(values):
    seen = set()
    for value in values:
        if value in seen:
            return value
        seen.add(value)
    return None


def _assert_exactly_one_disposition_per_risk(assessment, closure):
    """Section VI-E.  Note what is *not* asserted: |P| + |X| = |R|."""
    risk_ids = [r["risk_id"] for r in assessment.risk_register]
    disposition_ids = [d.risk_id for d in closure.dispositions]
    if len(set(disposition_ids)) != len(risk_ids) or set(disposition_ids) != set(risk_ids):
        raise ValidationError(
            "totality assertion failed: |{Delta_i}| = %d but |R| = %d"
            % (len(set(disposition_ids)), len(risk_ids)),
            code="TOTALITY_VIOLATION",
        )
    if len(disposition_ids) != len(set(disposition_ids)):
        raise ValidationError(
            "totality assertion failed: a risk carries more than one disposition",
            code="TOTALITY_VIOLATION",
        )


def _assert_all_predicates_have_authorized_origin(predicates, risk_index, invariant_index):
    """Section VI-B: ``for all p in P, origin(p) in R union INV``."""
    orphans = []
    for predicate in predicates:
        origin = predicate["origin"]
        if origin["origin_type"] == "risk_derived":
            if origin["origin_id"] not in risk_index:
                orphans.append(predicate["gcir_id"])
        elif origin["origin_type"] == "compiler_invariant":
            if origin["origin_id"] not in invariant_index:
                orphans.append(predicate["gcir_id"])
        else:
            orphans.append(predicate["gcir_id"])
    if orphans:
        raise ValidationError(
            "orphan predicate(s) %s have no authorized origin in R union INV" % orphans,
            code="ORPHAN_PREDICATE",
            detail={"orphans": orphans},
        )


def _assert_no_mandatory_unknown_warns(predicates, gate_map):
    offenders = []
    for predicate in predicates:
        if gate_map[predicate["gcir_id"]]["gate_type"] != "mandatory":
            continue
        for condition in predicate["context_conditions"]:
            if condition.get("required", True) and condition["on_unknown"] != "fail":
                offenders.append((predicate["gcir_id"], condition["attribute"]))
    if offenders:
        raise ValidationError(
            "mandatory gate(s) permit a non-failing unknown: %s" % offenders,
            code="MANDATORY_UNKNOWN_WARN",
            detail={"offenders": offenders},
        )
