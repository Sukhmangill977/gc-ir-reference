"""Authority closure against ``S.authority_matrix`` (manuscript Sections III-2, VI-A).

    "If an action does not appear in S.authority_matrix, no predicate can permit
     it; the fail-closed default of the enforcement layer handles the remainder."

    Appendix A, constraint 5: "Every action tuple resolves to S.authority_matrix."

The matrix does double duty as a governance artifact and as the compiler's symbol
table.  Resolution is exact on all four components plus parameter conformance;
there is no wildcard and no partial match.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import ActionTuple, AuthorityClosureError, ValidationError


def resolve_action_tuple(action_tuple, authority_matrix):
    """Return the authorizing matrix entry, or raise ``AuthorityClosureError``."""
    entry = authority_matrix.get(action_tuple.as_tuple())
    if entry is None:
        raise AuthorityClosureError(
            "action tuple %s is not present in S.authority_matrix" % action_tuple,
            detail={"action_tuple": action_tuple.as_dict()},
        )
    return entry


def validate_parameters(action_tuple, parameters, entry, parameter_schema_ref=None):
    """Compiler step 4: validate action parameters against ``parameter_schema``.

    The schema is a closed mapping of parameter name to a small type descriptor.
    Unknown parameters are a closure violation, not a warning: a predicate that
    binds a parameter the matrix never authorized is outside the approved
    authority even though its four-tuple resolves.
    """
    schema = entry.parameter_schema or {}
    problems = []

    if parameter_schema_ref is not None and parameter_schema_ref != entry.parameter_schema_id:
        problems.append(
            "parameter_schema_ref %r does not resolve to the matrix entry's "
            "parameter schema %r" % (parameter_schema_ref, entry.parameter_schema_id)
        )

    for name, descriptor in sorted(schema.items()):
        if descriptor.get("required", False) and name not in parameters:
            problems.append("required parameter %r is absent" % name)

    for name, value in sorted(parameters.items()):
        descriptor = schema.get(name)
        if descriptor is None:
            problems.append(
                "parameter %r is not authorized by the matrix parameter_schema" % name
            )
            continue
        if not _matches(value, descriptor):
            problems.append(
                "parameter %r value %r does not satisfy %r" % (name, value, descriptor)
            )

    if problems:
        raise AuthorityClosureError(
            "action parameters for %s fall outside S.authority_matrix: %s"
            % (action_tuple, "; ".join(problems)),
            detail={"action_tuple": action_tuple.as_dict(), "problems": problems},
        )
    return True


def _matches(value, descriptor):
    kind = descriptor["type"]
    if kind == "string":
        if not isinstance(value, str):
            return False
        if "enum" in descriptor:
            return value in descriptor["enum"]
        return True
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind == "array":
        return isinstance(value, list)
    return False


def hazardous_paths_for(risk_id, assessment):
    """The authorized hazardous action paths declared for a risk.

    The C* coverage rule of Section VII-A is stated over "each authorized
    hazardous action path associated with r_i".  The association is a governance
    declaration carried on the register row (``hazardous_action_paths``), and each
    declared path must itself resolve to the authority matrix -- a hazardous path
    that is not authorized cannot be exercised and cannot need a gate.
    """
    risk = assessment.risk_index[risk_id]
    matrix = assessment.authority_matrix
    paths = []
    for raw in risk.get("hazardous_action_paths", []):
        tup = ActionTuple.from_mapping(raw)
        entry = matrix.get(tup.as_tuple())
        if entry is None:
            raise AuthorityClosureError(
                "risk %s declares hazardous action path %s which is not in "
                "S.authority_matrix" % (risk_id, tup),
                detail={"risk_id": risk_id, "action_tuple": tup.as_dict()},
            )
        if not entry.hazardous:
            raise ValidationError(
                "risk %s declares %s as hazardous but the authority matrix does "
                "not mark it hazardous" % (risk_id, tup),
                code="HAZARD_DECLARATION_MISMATCH",
                detail={"risk_id": risk_id, "action_tuple": tup.as_dict()},
            )
        paths.append(tup)
    return paths


def all_action_tuples_authorized(predicates, authority_matrix):
    """Bundle-level assertion used by ``Phi`` and by the property tests."""
    offenders = []
    for predicate in predicates:
        tup = ActionTuple.from_mapping(predicate)
        if tup.as_tuple() not in authority_matrix:
            offenders.append({"gcir_id": predicate["gcir_id"], "action_tuple": tup.as_dict()})
    return offenders
