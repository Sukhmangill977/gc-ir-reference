"""Appendix A normative cross-field constraints and JSON Schema validation.

Constraints 1-14 of Appendix A are implemented here as named, individually
testable functions so the adversarial suite can point at exactly one of them.

Constraint 14 (the runtime acceptance condition) is a *deployment conformance*
requirement rather than a compile-time check; it is implemented as
``check_runtime_acceptance`` over a candidate receipt and consuming-runtime
declaration, and is exercised by the traceability experiment.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012 as DRAFT_2020_12

from .models import (
    EVALUATION_BASES,
    GATE_SOURCES,
    GATE_TYPES,
    MANDATORY_ROLES,
    NUMERIC_TEMPORAL_OPERATORS,
    ORIGIN_TYPES,
    ReleaseInadmissibleError,
    ValidationError,
)
from .temporal import is_within, parse_time

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "schemas")


# ---------------------------------------------------------------------------
# JSON Schema
# ---------------------------------------------------------------------------

_SCHEMA_CACHE = {}


def load_schema(name, schema_dir=None):
    directory = schema_dir or SCHEMA_DIR
    key = (directory, name)
    if key not in _SCHEMA_CACHE:
        with open(os.path.join(directory, name), encoding="utf-8") as handle:
            _SCHEMA_CACHE[key] = json.load(handle)
    return _SCHEMA_CACHE[key]


_REGISTRY_CACHE = {}


def _registry(directory):
    """A ``referencing`` registry over every schema in ``directory``.

    Each schema is registered under both its absolute ``$id`` and its bare
    filename, so ``{"$ref": "common.schema.json#/$defs/identifier"}`` resolves
    the same way whether the referring schema declares an ``$id`` or not.
    """
    if directory not in _REGISTRY_CACHE:
        resources = []
        for filename in sorted(os.listdir(directory)):
            if not filename.endswith(".schema.json"):
                continue
            document = load_schema(filename, directory)
            resource = Resource.from_contents(
                document, default_specification=DRAFT_2020_12
            )
            if "$id" in document:
                resources.append((document["$id"], resource))
            resources.append((filename, resource))
        _REGISTRY_CACHE[directory] = Registry().with_resources(resources)
    return _REGISTRY_CACHE[directory]


def schema_validator(name, schema_dir=None):
    directory = schema_dir or SCHEMA_DIR
    schema = load_schema(name, directory)
    return Draft202012Validator(schema, registry=_registry(directory))


def validate_document(document, schema_name, label=None, schema_dir=None):
    """Validate and raise a single aggregated ``ValidationError`` on failure."""
    validator = schema_validator(schema_name, schema_dir)
    errors = sorted(validator.iter_errors(document), key=lambda e: list(e.path))
    if errors:
        rendered = [
            "%s: %s" % ("/".join(str(p) for p in error.path) or "<root>", error.message)
            for error in errors[:20]
        ]
        raise ValidationError(
            "%s failed %s validation: %s"
            % (label or schema_name, schema_name, "; ".join(rendered)),
            code="SCHEMA_VALIDATION_FAILED",
            detail={"schema": schema_name, "errors": rendered, "count": len(errors)},
        )
    return True


# ---------------------------------------------------------------------------
# Appendix A constraints 1-13 (compile-time)
# ---------------------------------------------------------------------------


def constraint_01_mandatory_implies_safe_state(predicate, gate_type):
    """mandatory implies on_fail = SAFE_STATE."""
    if gate_type == "mandatory" and predicate["on_fail"] != "SAFE_STATE":
        raise ValidationError(
            "predicate %s is a mandatory gate but declares on_fail=%r; Appendix A "
            "constraint 1 requires SAFE_STATE"
            % (predicate["gcir_id"], predicate["on_fail"]),
            code="A1_MANDATORY_ON_FAIL",
        )


def constraint_02_mandatory_unknown_fails(predicate, gate_type):
    """mandatory implies every required condition has on_unknown = fail.

    Section V: "For mandatory gates, on_unknown = fail is required, not default."
    Missing, stale or schema-invalid context is indeterminacy, and indeterminacy
    must never become a silent mandatory pass.
    """
    if gate_type != "mandatory":
        return
    offenders = [
        condition["attribute"]
        for condition in predicate["context_conditions"]
        if condition.get("required", True) and condition["on_unknown"] != "fail"
    ]
    if offenders:
        raise ValidationError(
            "predicate %s is a mandatory gate but conditions %s declare "
            "on_unknown != fail; Appendix A constraint 2"
            % (predicate["gcir_id"], offenders),
            code="A2_MANDATORY_ON_UNKNOWN",
        )


def constraint_03_threshold_contract_and_unit(predicate, threshold_contracts):
    """Numeric or temporal operators require a threshold contract and unit."""
    for condition in predicate["context_conditions"]:
        if condition["operator"] not in NUMERIC_TEMPORAL_OPERATORS:
            continue
        ref = condition.get("threshold_contract_ref")
        if not ref:
            raise ValidationError(
                "predicate %s condition %r uses numeric/temporal operator %r with "
                "no threshold_contract_ref; Appendix A constraint 3"
                % (predicate["gcir_id"], condition["attribute"], condition["operator"]),
                code="A3_THRESHOLD_CONTRACT_MISSING",
            )
        contract = threshold_contracts.get(ref)
        if contract is None:
            raise ValidationError(
                "predicate %s references threshold contract %r which does not exist"
                % (predicate["gcir_id"], ref),
                code="A3_THRESHOLD_CONTRACT_UNRESOLVED",
            )
        if not contract.get("unit"):
            raise ValidationError(
                "threshold contract %r carries no unit; Appendix A constraint 3" % ref,
                code="A3_THRESHOLD_UNIT_MISSING",
            )
        missing = [
            field
            for field in (
                "operational_definition",
                "numerator",
                "denominator",
                "evidence_source",
                "ground_truth",
                "threshold_rationale",
                "uncertainty_method",
                "unit",
                "reproduction_procedure",
            )
            if not contract.get(field)
        ]
        if missing:
            raise ValidationError(
                "threshold contract %r is incomplete, missing %s; Section V "
                "commitment 4" % (ref, missing),
                code="A3_THRESHOLD_CONTRACT_INCOMPLETE",
            )


def constraint_03b_mandatory_temporal_window_is_contractual(predicate, gate_type,
                                                            threshold_contracts):
    """A mandatory condition that declares a temporal window must state the bound.

    Section V: "Missing, stale, or schema-invalid context is indeterminacy,
    distinct from violation ... For mandatory gates, on_unknown = fail is
    required, not default."

    A condition can only fail closed on *stale* evidence if "stale" is defined.
    A declared ``temporal_window`` without a threshold contract carrying the
    freshness bound and its unit leaves the timeout boundary unspecified, so the
    predicate cannot deterministically distinguish fresh evidence from stale
    evidence -- and an unevaluable staleness test is exactly the silent mandatory
    pass Appendix A constraint 2 exists to prevent.
    """
    if gate_type != "mandatory":
        return
    for condition in predicate["context_conditions"]:
        window = condition.get("temporal_window")
        if not window:
            continue
        ref = condition.get("threshold_contract_ref")
        if not ref:
            raise ValidationError(
                "predicate %s condition %r declares temporal_window %r on a "
                "mandatory gate with no threshold_contract_ref; the staleness "
                "boundary would be unevaluable and stale evidence could not fail "
                "closed" % (predicate["gcir_id"], condition["attribute"], window),
                code="A3B_TEMPORAL_WINDOW_UNCONTRACTED",
            )
        contract = threshold_contracts.get(ref)
        if contract is None or not contract.get("unit"):
            raise ValidationError(
                "predicate %s condition %r declares a temporal_window whose "
                "threshold contract %r is missing or carries no unit"
                % (predicate["gcir_id"], condition["attribute"], ref),
                code="A3B_TEMPORAL_WINDOW_UNCONTRACTED",
            )


def constraint_04_weighted_structure(predicate, gate_type):
    """weighted requires weight, normalized deficit function, aggregation group,
    group threshold, and a response."""
    if gate_type != "weighted":
        return
    aggregation = predicate.get("aggregation")
    if not aggregation:
        raise ValidationError(
            "predicate %s is weighted but carries no aggregation block; "
            "Appendix A constraint 4" % predicate["gcir_id"],
            code="A4_WEIGHTED_STRUCTURE",
        )
    missing = [
        field
        for field in ("aggregation_group", "weight", "deficit_function", "group_threshold", "response")
        if aggregation.get(field) in (None, "")
    ]
    if missing:
        raise ValidationError(
            "predicate %s weighted aggregation block is missing %s; Appendix A "
            "constraint 4" % (predicate["gcir_id"], missing),
            code="A4_WEIGHTED_STRUCTURE",
        )
    if not (isinstance(aggregation["weight"], (int, float)) and aggregation["weight"] > 0):
        raise ValidationError(
            "predicate %s weighted aggregation requires a positive weight, got %r"
            % (predicate["gcir_id"], aggregation["weight"]),
            code="A4_WEIGHTED_WEIGHT",
        )


def constraint_06_risk_derived_resolves(predicate, acs_index, risk_index):
    """Every risk-derived predicate resolves to an ACS and a risk."""
    origin = predicate["origin"]
    if origin["origin_type"] != "risk_derived":
        return
    if origin["origin_id"] not in risk_index:
        raise ValidationError(
            "predicate %s cites risk %r which is not in the register; Appendix A "
            "constraint 6" % (predicate["gcir_id"], origin["origin_id"]),
            code="A6_RISK_UNRESOLVED",
        )
    if predicate.get("acs_id") not in acs_index:
        raise ValidationError(
            "predicate %s cites acs_id %r which is not in the approved "
            "specification set; Appendix A constraint 6"
            % (predicate["gcir_id"], predicate.get("acs_id")),
            code="A6_ACS_UNRESOLVED",
        )


def constraint_07_invariant_resolves(predicate, invariant_index):
    """Every compiler invariant resolves to an approved invariant ID in INV."""
    origin = predicate["origin"]
    if origin["origin_type"] != "compiler_invariant":
        return
    if origin["origin_id"] not in invariant_index:
        raise ValidationError(
            "predicate %s cites compiler invariant %r which is not in the approved "
            "invariant register INV; Appendix A constraint 7"
            % (predicate["gcir_id"], origin["origin_id"]),
            code="A7_INVARIANT_UNRESOLVED",
        )


def constraint_08_obligation_refs(predicate, obligation_index):
    """Every obligation reference resolves to O; an unresolved reference raises
    warning code WC-01 (not a disposition).

    Returns the list of warnings so the compiler can record them without failing.
    """
    warnings = []
    for obligation_id in predicate["requirement_ref"].get("obligation_ids", []):
        if obligation_id not in obligation_index:
            warnings.append(
                {
                    "warning_code": "WC-01",
                    "message": "unresolved obligation reference %r on predicate %s"
                    % (obligation_id, predicate["gcir_id"]),
                    "gcir_id": predicate["gcir_id"],
                    "obligation_id": obligation_id,
                }
            )
    return warnings


def constraint_09_no_expired_approval(acs_records, compile_time):
    """No expired approval may enter a release-admissible bundle."""
    expired = []
    for acs in acs_records:
        interval = acs["validity_interval"]
        if not is_within(compile_time, interval["effective_from"], interval.get("effective_until")):
            expired.append(
                {
                    "acs_id": acs.acs_id,
                    "validity_interval": interval,
                    "compile_time": compile_time,
                }
            )
    if expired:
        raise ReleaseInadmissibleError(
            "%d Approved Control Specification(s) are outside their approved "
            "validity interval at compile time; Appendix A constraint 9"
            % len(expired),
            code="A9_EXPIRED_APPROVAL",
            detail={"expired": expired},
        )


def constraint_10_assessor_is_not_acceptor(assessment):
    """Assessor identity may not equal acceptor identity (Section III, Step 1)."""
    metadata = assessment.metadata
    if metadata["assessor"] == metadata["accountable_exec"]:
        raise ValidationError(
            "M.assessor and M.accountable_exec are the same identity (%r); the "
            "party who performs the assessment may not be the party who accepts "
            "residual risk; Appendix A constraint 10" % metadata["assessor"],
            code="A10_SEPARATION_OF_DUTY",
        )


def constraint_11_acceptance_bounds(dispositions, assessment, compile_time):
    """An accepted-risk disposition's acceptor resolves to M.accountable_exec, its
    expiry does not exceed the assessment validity interval, and no
    release-admissible bundle contains an acceptance already past expiry."""
    problems = []
    accountable = assessment.metadata["accountable_exec"]
    assessment_until = assessment.metadata["validity_interval"].get("effective_until")
    for disposition in dispositions:
        if disposition.status != "accepted":
            continue
        if disposition.acceptor != accountable:
            problems.append(
                "risk %s acceptance is signed by %r, not M.accountable_exec %r"
                % (disposition.risk_id, disposition.acceptor, accountable)
            )
        if parse_time(disposition.expiry) <= parse_time(compile_time):
            problems.append(
                "risk %s acceptance expired at %s, before compile time %s"
                % (disposition.risk_id, disposition.expiry, compile_time)
            )
        if assessment_until and parse_time(disposition.expiry) > parse_time(assessment_until):
            problems.append(
                "risk %s acceptance expiry %s exceeds the assessment validity "
                "interval end %s" % (disposition.risk_id, disposition.expiry, assessment_until)
            )
    if problems:
        raise ReleaseInadmissibleError(
            "accepted-risk disposition constraint violated: %s" % "; ".join(problems),
            code="A11_ACCEPTANCE_BOUNDS",
            detail={"problems": problems},
        )


#: Keys that may never appear anywhere inside a hashed bundle payload.
FORBIDDEN_PAYLOAD_KEYS = (
    "signing_time",
    "signature",
    "nonce",
    "random_nonce",
    "generated_at",
    "compiled_at",
    "timestamp",
    "retired_at",
    "superseded_at",
    "revoked_at",
    "lifecycle_state",
    "lifecycle_status",
    "current_status",
    "effective_until",
)


def constraint_13_payload_is_hash_clean(payload, path="$"):
    """The bundle payload contains no timestamp, nonce, or mutable lifecycle field.

    ``effective_until`` is forbidden alongside the lifecycle fields because
    Appendix A restricts a compiled record's validity binding to ``effective_from``
    only -- an end date inside the payload would be lifecycle state by another
    name.
    """
    offenders = []
    _walk_payload(payload, path, offenders)
    if offenders:
        raise ValidationError(
            "bundle payload contains forbidden mutable/nondeterministic field(s): "
            "%s; Appendix A constraint 13" % ", ".join(offenders),
            code="A13_PAYLOAD_NOT_HASH_CLEAN",
            detail={"offenders": offenders},
        )
    return True


def _walk_payload(node, path, offenders):
    if isinstance(node, dict):
        for key in sorted(node):
            if key in FORBIDDEN_PAYLOAD_KEYS:
                offenders.append("%s.%s" % (path, key))
            _walk_payload(node[key], "%s.%s" % (path, key), offenders)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _walk_payload(item, "%s[%d]" % (path, index), offenders)


# ---------------------------------------------------------------------------
# Schema v1.1 constraints (this generation)
# ---------------------------------------------------------------------------


def constraint_15_evaluation_latency_requires_timeout_response(predicate):
    """Appendix A constraint 15 (v1.1): a predicate declaring
    ``evaluation_latency_bound`` must declare ``on_evaluation_timeout``, and its
    value is fixed at ``HOLD`` -- an evaluator that does not finish inside its
    bound never produces a partial permit."""
    bound = predicate.get("evaluation_latency_bound")
    if bound is None:
        return
    timeout_response = predicate.get("on_evaluation_timeout")
    if timeout_response != "HOLD":
        raise ValidationError(
            "predicate %s declares evaluation_latency_bound but "
            "on_evaluation_timeout=%r; Appendix A constraint 15 fixes this at "
            "HOLD" % (predicate["gcir_id"], timeout_response),
            code="A15_TIMEOUT_RESPONSE_NOT_HOLD",
        )


def constraint_16_permit_eligibility_matches_phase(predicate, permit_eligible):
    """Appendix A constraint 16 (v1.1): ``permit_eligible`` (recorded in the
    bundle's gate_map) must be exactly ``enforcement_phase in
    {PRE_AUTHORIZATION, BOUNDARY_REVALIDATION, <undeclared>}``.  This is the
    structural claim audit query Q5 re-verifies post-hoc against the emitted
    bundle."""
    from .models import PERMIT_ELIGIBLE_PHASES

    phase = predicate.get("enforcement_phase")
    expected = phase is None or phase in PERMIT_ELIGIBLE_PHASES
    if permit_eligible != expected:
        raise ValidationError(
            "predicate %s has enforcement_phase=%r but permit_eligible=%r was "
            "computed; Appendix A constraint 16"
            % (predicate["gcir_id"], phase, permit_eligible),
            code="A16_PERMIT_ELIGIBILITY_MISMATCH",
        )


def constraint_17_concurrence_expiry_fixed(predicate):
    """Appendix A constraint 17 (v1.1): ``concurrence_policy.expiry_response``
    is fixed DENY.  Schema-enforced already (``const: DENY``); restated here as
    a named, individually testable function alongside constraints 1-16."""
    policy = predicate.get("concurrence_policy")
    if policy is None:
        return
    if policy.get("expiry_response") != "DENY":
        raise ValidationError(
            "predicate %s concurrence_policy.expiry_response=%r; Appendix A "
            "constraint 17 fixes this at DENY"
            % (predicate["gcir_id"], policy.get("expiry_response")),
            code="A17_CONCURRENCE_EXPIRY_NOT_DENY",
        )


# ---------------------------------------------------------------------------
# Constraint 14: runtime acceptance condition (deployment conformance)
# ---------------------------------------------------------------------------


def check_runtime_acceptance(runtime_declaration, receipt, bundle):
    """Appendix A constraint 14.

    A conformant consuming runtime:
      * loads only bundles verifying as signed Phi outputs (signature, payload
        hash, lifecycle-registry state);
      * accepts no policy content through any other channel;
      * emits decision receipts carrying the requirement reference (gcir_id,
        acs_id and origin) of every evaluated predicate.
    """
    problems = []
    if not runtime_declaration.get("loads_only_signed_phi_bundles"):
        problems.append("runtime does not declare that it loads only signed Phi bundles")
    if runtime_declaration.get("alternate_policy_channels"):
        problems.append(
            "runtime declares alternate policy channels %r; the orphan-control "
            "guarantee does not extend to this deployment"
            % runtime_declaration["alternate_policy_channels"]
        )
    if not runtime_declaration.get("emits_requirement_reference"):
        problems.append("runtime does not declare that receipts carry requirement_ref")

    evaluated = {e["gcir_id"] for e in receipt.get("evaluated_predicates", [])}
    for entry in receipt.get("evaluated_predicates", []):
        for field in ("gcir_id", "acs_id", "origin"):
            if field not in entry:
                problems.append(
                    "receipt entry for %s omits required requirement-reference "
                    "field %r" % (entry.get("gcir_id", "<unknown>"), field)
                )
    known = {p["gcir_id"] for p in bundle.predicates}
    unknown = sorted(evaluated - known)
    if unknown:
        problems.append(
            "receipt cites predicates %s that are not in the bundle -- policy "
            "content entered through a channel outside the compiled bundle" % unknown
        )

    # The other direction: a receipt that silently omits mandatory predicates the
    # bundle requires is a state mismatch between the loaded policy and the
    # policy actually evaluated. Only mandatory gates are required to appear --
    # an advisory result may legitimately be absent.
    required = {
        p["gcir_id"] for p in bundle.predicates if p["gate_type"] == "mandatory"
    }
    omitted = sorted(required - evaluated)
    if omitted:
        problems.append(
            "receipt omits mandatory predicates %s that the cited bundle requires "
            "-- the evaluated policy state does not match the loaded bundle" % omitted
        )
    return (not problems), problems
