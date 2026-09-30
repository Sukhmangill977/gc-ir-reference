"""Paper 2 v1.2 governance-to-control validator suite (spec sections 1A-1L, 5).

The empirical question this module exists to answer: "Can the compiler/
validator accept an authorized governance translation while rejecting a
controlled unauthorized semantic change, for the correct reason?" Every check
below is therefore a **reference-vs-candidate comparator**: a ``nominal``
compiled bundle (the approved translation) and a ``candidate`` compiled
bundle (a translation under test, possibly a controlled negative) are
compiled through the *same*, unmodified ``gcir.compiler.compile_bundle``
(Phi) -- nothing about Phi's own logic is v1.2-aware beyond the additive
fields ``gcir.compiler.V12_PREDICATE_FIELDS`` already thread through. This
module only inspects the two resulting payloads.

A handful of checks (``indeterminacy``, ``declared_path``,
``synchronization_contract_representation``, ``observation_obligation``,
``evidence_representation``, ``lifecycle``) are single-bundle: they ask
whether a *representation* is well-formed, not whether it matches a
reference. The spec is explicit that this module never claims more than
representation: it does not prove runtime synchronization, complete
mediation, or full semantic equivalence with natural-language policy
(spec sections 1C, 1I, 1J).

Every function returns ``(bool, List[str])``, exactly like
``gcir.audit_queries`` and ``gcir.auxiliary_checks``, so callers can compose
and report them uniformly.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from .audit_queries import q2_exactly_one_disposition_per_risk, q3_predicate_origin_closure
from .models import IndeterminacyError, PRIMARY_CLASSES

#: spec 1L's closed set for observation scope q_r.
OBSERVATION_SCOPES = ("event", "cross-request", "sequence", "bounded-history")

#: Rigor ordering over OBSERVATION_SCOPES, weakest first (spec 1L / Paper 2
#: v1.2 neutrality N7: "no topology is downgraded for convenience"). An
#: "event" scope sees only the single current request; "bounded-history"
#: sees the full prior-consumption history -- the diagnostics in
#: experiments/observation_diagnostics_v12.py exercise exactly this: an
#: event-scoped evaluator cannot detect a violation only visible across
#: history, a bounded-history-scoped one can. A candidate whose q_r moves to
#: a strictly lower rank than the nominal's is a scope downgrade.
OBSERVATION_SCOPE_STRENGTH = {name: rank for rank, name in enumerate(OBSERVATION_SCOPES)}

#: spec 1J's required synchronization-contract sub-fields.
SYNCHRONIZATION_CONTRACT_FIELDS = (
    "source",
    "epoch_version",
    "freshness",
    "observed_at",
    "valid_until",
    "invalidation_trigger",
    "revalidation_requirement",
    "failure_response",
    "downstream_interface",
)

#: spec 1G's required exception sub-fields.
EXCEPTION_FIELDS = (
    "target_requirement",
    "trigger",
    "authorized_actor",
    "parameter_bounds",
    "scope",
    "lifecycle_version_binding",
)

#: Relative strength of ``on_fail`` responses, strongest (safest) first. Used
#: by ``failure_semantics`` to detect a candidate weakening a nominal's
#: declared failure response -- never merely a different one.
_ON_FAIL_STRENGTH = {"SAFE_STATE": 2, "ESCALATE": 1, "WARN": 0}

#: Prohibited primary-class collapses the spec names explicitly (section A3);
#: checked first so their rejection message is specific, not generic.
_NAMED_PROHIBITED_COLLAPSES = {("human", "auth"), ("meta", "auth")}


def _payload_of(bundle):
    return bundle.payload if hasattr(bundle, "payload") else bundle


def _predicates_by_acs_id(bundle):
    payload = _payload_of(bundle)
    index = {}
    for predicate in payload.get("predicates", []):
        acs_id = predicate.get("acs_id")
        if acs_id is not None:
            index[acs_id] = predicate
    return index


def _matched_pairs(nominal_bundle, candidate_bundle):
    """``(acs_id, nominal_predicate, candidate_predicate)`` for every ACS the
    nominal bundle compiled, paired with its candidate counterpart (``None``
    if the candidate dropped it entirely -- itself a narrowing)."""
    nominal_index = _predicates_by_acs_id(nominal_bundle)
    candidate_index = _predicates_by_acs_id(candidate_bundle)
    return [
        (acs_id, nominal_index[acs_id], candidate_index.get(acs_id))
        for acs_id in sorted(nominal_index)
    ]


# ---------------------------------------------------------------------------
# judgment hash binding
# ---------------------------------------------------------------------------


def judgment_hash_binding(candidate_bundle, expected_judgment=None) -> Tuple[bool, List[str]]:
    """spec 1A: ``judgment_record_ref`` carries ``judgment_id``, ``version``
    and a ``content_hash`` binding the canonical judgment content itself.

    When ``expected_judgment`` (a ``gcir.models.JudgmentRecord``) is supplied,
    the bundle's declared ``content_hash`` must equal
    ``hash_payload(expected_judgment.canonical_document())`` -- a mismatch is
    exactly the A1-style "mismatch or unauthorized origin/J relationship"
    negative. Without ``expected_judgment``, this only checks the field is
    present and well-formed (64 lowercase hex characters).
    """
    from .canonicalization import hash_payload

    payload = _payload_of(candidate_bundle)
    ref = payload.get("judgment_record_ref", {})
    issues = []
    content_hash = ref.get("content_hash")
    if not (isinstance(content_hash, str) and len(content_hash) == 64
            and all(c in "0123456789abcdef" for c in content_hash)):
        issues.append(
            "judgment_record_ref.content_hash %r is not present as 64 "
            "lowercase hex characters" % content_hash
        )
    elif expected_judgment is not None:
        expected_hash = hash_payload(expected_judgment.canonical_document())
        if content_hash != expected_hash:
            issues.append(
                "judgment_record_ref.content_hash %s does not match the "
                "approved judgment record's canonical content hash %s "
                "(judgment_id=%r, version=%r)"
                % (content_hash, expected_hash, ref.get("judgment_id"), ref.get("version"))
            )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# total disposition
# ---------------------------------------------------------------------------


def total_disposition(bundle) -> Tuple[bool, List[str]]:
    """spec 5's "total disposition": every risk carries exactly one
    disposition record (reuses ``gcir.audit_queries`` Q2 -- release
    admissibility, |P|+|X|=|R|, is already enforced at compile time by
    ``gcir.compiler.compile_bundle``; this is the post-hoc structural
    restatement of the same totality property)."""
    return q2_exactly_one_disposition_per_risk(bundle)


# ---------------------------------------------------------------------------
# origin
# ---------------------------------------------------------------------------


def origin(candidate_bundle, approved_authorizers=None) -> Tuple[bool, List[str]]:
    """spec Surface A1: valid approved origin/J/ACS relationship.

    Reuses ``gcir.audit_queries`` Q3 (every predicate's origin resolves, and
    a risk-derived predicate's acs_id is actually one of its risk's disposed
    acs_ids) as the structural half. When ``approved_authorizers`` (a set of
    authorized-by identifiers) is supplied, additionally rejects a predicate
    whose ``origin.authorized_by`` is outside it -- the "unauthorized
    origin/J/ACS relationship" negative surface.
    """
    ok, issues = q3_predicate_origin_closure(candidate_bundle)
    issues = list(issues)
    if approved_authorizers is not None:
        payload = _payload_of(candidate_bundle)
        for predicate in payload.get("predicates", []):
            authorized_by = predicate.get("origin", {}).get("authorized_by")
            if authorized_by not in approved_authorizers:
                issues.append(
                    "%s: origin.authorized_by %r is not among the approved "
                    "authorizers %s"
                    % (predicate["gcir_id"], authorized_by, sorted(approved_authorizers))
                )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# no-narrowing (spec 1C)
# ---------------------------------------------------------------------------


def no_narrowing(nominal_bundle, candidate_bundle) -> Tuple[bool, List[str]]:
    """spec 1C: machine-checkable preservation of every field/relation the
    v1.2 profile actually represents. This is schema/profile preservation
    only -- it never claims full semantic equivalence with natural-language
    policy (spec 1C)."""
    issues = []
    for acs_id, nominal, candidate in _matched_pairs(nominal_bundle, candidate_bundle):
        if candidate is None:
            issues.append("%s: dropped entirely from the candidate bundle (narrowing)" % acs_id)
            continue

        # mandatory represented obligations
        nominal_obligations = set(nominal.get("requirement_ref", {}).get("obligation_ids", []))
        candidate_obligations = set(candidate.get("requirement_ref", {}).get("obligation_ids", []))
        missing = nominal_obligations - candidate_obligations
        if missing:
            issues.append("%s: obligation_ids %s dropped from requirement_ref" % (acs_id, sorted(missing)))

        # scope constraints (context_conditions): no condition may be dropped
        nominal_conditions = {c["attribute"] for c in nominal.get("context_conditions", [])}
        candidate_conditions = {c["attribute"] for c in candidate.get("context_conditions", [])}
        missing_conditions = nominal_conditions - candidate_conditions
        if missing_conditions:
            issues.append("%s: context_conditions %s dropped" % (acs_id, sorted(missing_conditions)))

        # evidence requirements
        nominal_evidence = set(nominal.get("evidence_requirement", []))
        candidate_evidence = set(candidate.get("evidence_requirement", []))
        missing_evidence = nominal_evidence - candidate_evidence
        if missing_evidence:
            issues.append("%s: evidence_requirement %s dropped" % (acs_id, sorted(missing_evidence)))

        # exception conditions + required residual treatment
        nominal_exception = nominal.get("exception")
        if nominal_exception is not None:
            candidate_exception = candidate.get("exception")
            if candidate_exception is None:
                issues.append("%s: exception dropped entirely" % acs_id)
            else:
                for field_name in EXCEPTION_FIELDS:
                    if nominal_exception.get(field_name) is not None and candidate_exception.get(field_name) is None:
                        issues.append("%s: exception.%s dropped (required residual treatment)" % (acs_id, field_name))

        # lifecycle references
        if nominal.get("version_binding_ref") and not candidate.get("version_binding_ref"):
            issues.append("%s: version_binding_ref dropped" % acs_id)
        if nominal.get("validity", {}).get("effective_from") and not candidate.get("validity", {}).get("effective_from"):
            issues.append("%s: validity.effective_from dropped" % acs_id)

        # enforcement phase
        if nominal.get("enforcement_phase") is not None and candidate.get("enforcement_phase") is None:
            issues.append("%s: enforcement_phase dropped" % acs_id)

        # failure semantics (presence only -- value weakening is failure_semantics' job)
        if nominal.get("on_fail") is not None and candidate.get("on_fail") is None:
            issues.append("%s: on_fail dropped" % acs_id)

        # primary class (presence only -- collapse is primary_class_preservation's job)
        if nominal.get("primary_class") is not None and candidate.get("primary_class") is None:
            issues.append("%s: primary_class dropped" % acs_id)

        # observation obligation: beta_r (required binding information) may
        # not be narrowed -- a dropped decision-relevant distinction (spec
        # Surface A7) is exactly a no-narrowing instance over Omega_r.
        nominal_omega = nominal.get("observation_obligation")
        if nominal_omega is not None:
            candidate_omega = candidate.get("observation_obligation")
            if candidate_omega is None:
                issues.append("%s: observation_obligation dropped entirely" % acs_id)
            else:
                missing_beta = set(nominal_omega.get("beta_r", [])) - set(candidate_omega.get("beta_r", []))
                if missing_beta:
                    issues.append("%s: observation_obligation.beta_r %s dropped" % (acs_id, sorted(missing_beta)))

                # q_r (observation scope/topology) may not be silently
                # downgraded to a less rigorous scope for convenience
                # (neutrality N7). Presence/closed-set membership is
                # observation_obligation()'s job; this is narrowing over time
                # (a candidate weaker than its own nominal), not validity.
                nominal_q_r = nominal_omega.get("q_r")
                candidate_q_r = candidate_omega.get("q_r")
                nominal_rank = OBSERVATION_SCOPE_STRENGTH.get(nominal_q_r)
                candidate_rank = OBSERVATION_SCOPE_STRENGTH.get(candidate_q_r)
                if nominal_rank is not None and candidate_rank is not None and candidate_rank < nominal_rank:
                    issues.append(
                        "%s: observation_obligation.q_r downgraded from %r to %r "
                        "(topology/placement narrowed for convenience, neutrality N7)"
                        % (acs_id, nominal_q_r, candidate_q_r)
                    )

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# no-broadening (spec 1D)
# ---------------------------------------------------------------------------


def _is_subset_or_equal(candidate_value, nominal_value):
    if isinstance(nominal_value, (list, tuple, set)) and isinstance(candidate_value, (list, tuple, set)):
        return set(candidate_value).issubset(set(nominal_value))
    return candidate_value == nominal_value


def no_broadening(nominal_bundle, candidate_bundle) -> Tuple[bool, List[str]]:
    """spec 1D: reject unauthorized widening of actor, action, resource,
    destination, amount/parameter, delegation scope, exception scope.

    ``subject``/``action``/``resource``/``destination`` are approved exact
    tuples (Section III-2 of the manuscript): any candidate value that
    differs from the nominal's approved value is, by construction,
    unauthorized widening -- there is no "narrower than approved" case for a
    tuple that was compiled from a single approved ACS row.
    """
    issues = []
    for acs_id, nominal, candidate in _matched_pairs(nominal_bundle, candidate_bundle):
        if candidate is None:
            continue  # a dropped predicate is no_narrowing's concern, not broadening's

        for field_name in ("subject", "action", "resource", "destination"):
            if candidate.get(field_name) != nominal.get(field_name):
                issues.append(
                    "%s: %s widened from approved %r to %r"
                    % (acs_id, field_name, nominal.get(field_name), candidate.get(field_name))
                )

        nominal_params = nominal.get("action_parameters") or {}
        candidate_params = candidate.get("action_parameters") or {}
        for key, nominal_value in nominal_params.items():
            candidate_value = candidate_params.get(key)
            if not isinstance(nominal_value, (int, float)) or isinstance(nominal_value, bool):
                if candidate_value != nominal_value:
                    issues.append("%s: action_parameters.%s changed from %r to %r" % (acs_id, key, nominal_value, candidate_value))
                continue
            lowered_key = key.lower()
            if any(token in lowered_key for token in ("min", "floor")):
                if candidate_value is not None and candidate_value < nominal_value:
                    issues.append(
                        "%s: action_parameters.%s (a lower bound) widened from %r to %r"
                        % (acs_id, key, nominal_value, candidate_value)
                    )
            else:
                # default: treat as an upper bound/ceiling-style parameter.
                if candidate_value is not None and candidate_value > nominal_value:
                    issues.append(
                        "%s: action_parameters.%s widened from %r to %r"
                        % (acs_id, key, nominal_value, candidate_value)
                    )

        nominal_delegation = nominal.get("delegation")
        candidate_delegation = candidate.get("delegation")
        if nominal_delegation is not None and candidate_delegation is not None:
            nominal_scope = nominal_delegation.get("scope", [])
            candidate_scope = candidate_delegation.get("scope", [])
            if not _is_subset_or_equal(candidate_scope, nominal_scope):
                issues.append(
                    "%s: delegation.scope widened from %s to %s"
                    % (acs_id, sorted(nominal_scope), sorted(candidate_scope))
                )

        nominal_exception = nominal.get("exception")
        candidate_exception = candidate.get("exception")
        if nominal_exception is not None and candidate_exception is not None:
            nominal_bounds = nominal_exception.get("parameter_bounds", {}) or {}
            candidate_bounds = candidate_exception.get("parameter_bounds", {}) or {}
            for key, nominal_value in nominal_bounds.items():
                candidate_value = candidate_bounds.get(key)
                if not isinstance(nominal_value, (int, float)) or isinstance(nominal_value, bool):
                    if candidate_value != nominal_value:
                        issues.append("%s: exception.parameter_bounds.%s changed from %r to %r" % (acs_id, key, nominal_value, candidate_value))
                    continue
                lowered_key = key.lower()
                if any(token in lowered_key for token in ("min", "floor")):
                    if candidate_value is not None and candidate_value < nominal_value:
                        issues.append("%s: exception.parameter_bounds.%s (a lower bound) widened from %r to %r" % (acs_id, key, nominal_value, candidate_value))
                else:
                    if candidate_value is not None and candidate_value > nominal_value:
                        issues.append("%s: exception.parameter_bounds.%s widened from %r to %r" % (acs_id, key, nominal_value, candidate_value))
            nominal_scope = nominal_exception.get("scope", [])
            candidate_scope = candidate_exception.get("scope", [])
            if isinstance(nominal_scope, list) and isinstance(candidate_scope, list):
                if not _is_subset_or_equal(candidate_scope, nominal_scope):
                    issues.append(
                        "%s: exception.scope widened from %s to %s"
                        % (acs_id, sorted(nominal_scope), sorted(candidate_scope))
                    )
            elif candidate_scope != nominal_scope:
                issues.append(
                    "%s: exception.scope widened from %r to %r"
                    % (acs_id, nominal_scope, candidate_scope)
                )
            nominal_actor = nominal_exception.get("authorized_actor")
            candidate_actor = candidate_exception.get("authorized_actor")
            if isinstance(nominal_actor, list) and isinstance(candidate_actor, list):
                if not _is_subset_or_equal(candidate_actor, nominal_actor):
                    issues.append(
                        "%s: exception.authorized_actor widened from %s to %s"
                        % (acs_id, sorted(nominal_actor), sorted(candidate_actor))
                    )

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# no-invention (spec 1E)
# ---------------------------------------------------------------------------


def no_invention(nominal_bundle, candidate_bundle) -> Tuple[bool, List[str]]:
    """spec 1E: every normative output element must trace to an approved
    specification input or an explicitly authorized compiler invariant.

    Both bundles compile through the same unmodified Phi, which only ever
    emits fields an ACS/invariant actually declared -- so an "invented"
    element in the candidate is detected here as an element with no
    counterpart in the nominal (approved) bundle: an extra predicate
    (unauthorized acs_id/origin), an extra field on a matched predicate, or
    an extra threshold_contract key.
    """
    issues = []
    nominal_payload = _payload_of(nominal_bundle)
    candidate_payload = _payload_of(candidate_bundle)

    nominal_acs_ids = set(_predicates_by_acs_id(nominal_bundle))
    candidate_acs_ids = set(_predicates_by_acs_id(candidate_bundle))
    invented_predicates = candidate_acs_ids - nominal_acs_ids
    if invented_predicates:
        issues.append(
            "candidate compiles predicate(s) for acs_id(s) %s with no "
            "counterpart in the approved nominal bundle (invented predicate)"
            % sorted(invented_predicates)
        )

    for acs_id, nominal, candidate in _matched_pairs(nominal_bundle, candidate_bundle):
        if candidate is None:
            continue
        extra_keys = set(candidate) - set(nominal)
        # schema_version legitimately differs once a v1.2-only field is used
        # anywhere in the bundle; it is not itself an invented element.
        extra_keys.discard("schema_version")
        if extra_keys:
            issues.append("%s: field(s) %s present on the candidate with no counterpart on the nominal (invented field)" % (acs_id, sorted(extra_keys)))
        if candidate.get("primary_class") is not None and candidate["primary_class"] not in PRIMARY_CLASSES:
            issues.append("%s: primary_class %r is outside the closed set %s (invented class)" % (acs_id, candidate["primary_class"], PRIMARY_CLASSES))

    nominal_thresholds = set(nominal_payload.get("threshold_contracts", {}))
    candidate_thresholds = set(candidate_payload.get("threshold_contracts", {}))
    invented_thresholds = candidate_thresholds - nominal_thresholds
    if invented_thresholds:
        issues.append("threshold_contracts key(s) %s present on the candidate with no counterpart on the nominal (invented threshold)" % sorted(invented_thresholds))

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# primary class preservation (spec 1B)
# ---------------------------------------------------------------------------


def primary_class_preservation(nominal_bundle, candidate_bundle) -> Tuple[bool, List[str]]:
    """spec 1B / Surface A3: every derived artifact keeps its single approved
    primary class; a candidate that collapses one primary class into another
    (``human -> auth`` and ``meta -> auth`` are the two the spec names
    explicitly) is rejected."""
    issues = []
    for acs_id, nominal, candidate in _matched_pairs(nominal_bundle, candidate_bundle):
        if candidate is None:
            continue
        nominal_class = nominal.get("primary_class")
        candidate_class = candidate.get("primary_class")
        if nominal_class is None or candidate_class is None or nominal_class == candidate_class:
            continue
        if (nominal_class, candidate_class) in _NAMED_PROHIBITED_COLLAPSES:
            issues.append(
                "%s: prohibited primary_class collapse %s -> %s"
                % (acs_id, nominal_class, candidate_class)
            )
        else:
            issues.append(
                "%s: primary_class changed from %r to %r (class must be preserved, "
                "never collapsed)" % (acs_id, nominal_class, candidate_class)
            )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# indeterminacy (spec 1F)
# ---------------------------------------------------------------------------


def indeterminacy(compile_callable: Callable[[], Any]) -> Tuple[bool, List[str]]:
    """spec 1F: calls ``compile_callable()`` (no arguments) and classifies the
    outcome. Returns ``(True, [...])`` if the compile succeeded (no
    unresolved mandatory interpretation was encountered) and
    ``(False, [...])`` if it raised ``gcir.models.IndeterminacyError``
    (COMPILE-FAIL / release-inadmissible, per ``constraint_18`` in
    ``gcir.validation``). Any other exception is left to propagate --
    this function only classifies the indeterminacy outcome, not every
    possible compile failure.
    """
    try:
        compile_callable()
        return True, ["compiled successfully; no unresolved mandatory interpretation encountered"]
    except IndeterminacyError as exc:
        return False, ["COMPILE-FAIL/release-inadmissible: %s" % exc]


# ---------------------------------------------------------------------------
# exception scope (spec 1G)
# ---------------------------------------------------------------------------


def exception_scope(nominal_bundle, candidate_bundle) -> Tuple[bool, List[str]]:
    """spec 1G: every declared exception preserves target_requirement,
    trigger, authorized_actor, parameter_bounds, scope, and
    lifecycle_version_binding; rejects a global bypass, a missing
    precondition, or a widened scope."""
    issues = []
    for acs_id, nominal, candidate in _matched_pairs(nominal_bundle, candidate_bundle):
        nominal_exception = nominal.get("exception")
        if nominal_exception is None:
            continue
        if candidate is None:
            continue
        candidate_exception = candidate.get("exception")
        if candidate_exception is None:
            issues.append("%s: exception dropped entirely (missing precondition)" % acs_id)
            continue
        for field_name in EXCEPTION_FIELDS:
            if not candidate_exception.get(field_name):
                issues.append("%s: exception.%s missing (missing exception precondition)" % (acs_id, field_name))
        scope = candidate_exception.get("scope")
        if scope in (None, [], "*", "ALL", "GLOBAL"):
            issues.append("%s: exception.scope %r is a global bypass, not a targeted exception" % (acs_id, scope))
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# lifecycle (spec 1H)
# ---------------------------------------------------------------------------


def lifecycle(
    bundle,
    expected_policy_version=None,
    expected_catalog_version=None,
    expected_cstar_profile_version=None,
    expected_judgment_version=None,
    lifecycle_registry=None,
    at_time=None,
) -> Tuple[bool, List[str]]:
    """spec 1H: validate consistency of policy version, judgment ID/version/
    content hash, profile version, supersession, expiry, and applicable
    lifecycle reference. Every ``expected_*`` argument is optional; supplying
    one turns on the corresponding staleness/supersession check."""
    from .temporal import parse_time

    payload = _payload_of(bundle)
    issues = []

    version_binding = payload.get("version_binding", {})
    if expected_policy_version is not None and version_binding.get("policy_version") != expected_policy_version:
        issues.append(
            "version_binding.policy_version %r does not match the current "
            "policy version %r (stale or superseded policy reference)"
            % (version_binding.get("policy_version"), expected_policy_version)
        )

    catalog_ref = payload.get("catalog_ref", {})
    if expected_catalog_version is not None and catalog_ref.get("version") != expected_catalog_version:
        issues.append(
            "catalog_ref.version %r does not match the current catalog "
            "version %r" % (catalog_ref.get("version"), expected_catalog_version)
        )

    cstar_ref = payload.get("cstar_profile_ref", {})
    if expected_cstar_profile_version is not None and cstar_ref.get("version") != expected_cstar_profile_version:
        issues.append(
            "cstar_profile_ref.version %r does not match the current C* "
            "profile version %r" % (cstar_ref.get("version"), expected_cstar_profile_version)
        )

    judgment_ref = payload.get("judgment_record_ref", {})
    if expected_judgment_version is not None and judgment_ref.get("version") != expected_judgment_version:
        issues.append(
            "judgment_record_ref.version %r does not match the current "
            "judgment version %r" % (judgment_ref.get("version"), expected_judgment_version)
        )

    if lifecycle_registry is not None:
        bundle_hash = bundle.payload_hash if hasattr(bundle, "payload_hash") else payload.get("payload_hash")
        check_time_raw = at_time or payload.get("validity", {}).get("effective_from")
        check_time = parse_time(check_time_raw)
        if lifecycle_registry.is_retired(bundle_hash, check_time):
            issues.append(
                "bundle %s is retired/superseded/revoked in the lifecycle "
                "registry as of %s" % (bundle_hash, check_time_raw)
            )

    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# declared path (spec 1I)
# ---------------------------------------------------------------------------


def declared_path(bundle, declared_paths: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """spec 1I: validate only that every DECLARED in-scope path has its
    required gate/placement mapping. Does NOT claim complete mediation or the
    absence of undeclared deployment paths -- ``declared_paths`` is the
    caller's own registry of paths it asserts are in scope, nothing more.

    ``declared_paths``: ``[{"path_id", "subject", "action", "resource",
    "destination"}, ...]``.
    """
    payload = _payload_of(bundle)
    gate_map = payload.get("gate_map", {})
    tuples = {
        (p.get("subject"), p.get("action"), p.get("resource"), p.get("destination")): p["gcir_id"]
        for p in payload.get("predicates", [])
    }
    issues = []
    for path in declared_paths:
        key = (path["subject"], path["action"], path["resource"], path["destination"])
        gcir_id = tuples.get(key)
        if gcir_id is None:
            issues.append("declared path %s (%s) has no compiled predicate (no gate/placement mapping)" % (path.get("path_id"), key))
            continue
        if gcir_id not in gate_map:
            issues.append("declared path %s (%s) compiles to %s, which has no gate_map entry (no placement mapping)" % (path.get("path_id"), key, gcir_id))
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# synchronization contract representation (spec 1J)
# ---------------------------------------------------------------------------


def synchronization_contract_representation(bundle) -> Tuple[bool, List[str]]:
    """spec 1J: validates representation of the required synchronization
    contract fields only. This does NOT prove runtime synchronization."""
    payload = _payload_of(bundle)
    issues = []
    for predicate in payload.get("predicates", []):
        contract = predicate.get("synchronization_contract")
        if contract is None:
            continue
        for field_name in SYNCHRONIZATION_CONTRACT_FIELDS:
            if not contract.get(field_name):
                issues.append("%s: synchronization_contract.%s missing or empty" % (predicate["gcir_id"], field_name))
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# observation obligation (spec 1K)
# ---------------------------------------------------------------------------


def observation_obligation(bundle) -> Tuple[bool, List[str]]:
    """spec 1K: Omega_r = (beta_r, kappa_r, q_r). Validates that every
    declared observation obligation carries required binding information
    (beta_r) and a required observation scope (q_r) from the closed set
    {event, cross-request, sequence, bounded-history}."""
    payload = _payload_of(bundle)
    issues = []
    for predicate in payload.get("predicates", []):
        omega = predicate.get("observation_obligation")
        if omega is None:
            continue
        beta_r = omega.get("beta_r")
        if not beta_r:
            issues.append("%s: observation_obligation.beta_r (required binding information) is missing or empty" % predicate["gcir_id"])
        q_r = omega.get("q_r")
        if q_r not in OBSERVATION_SCOPES:
            issues.append("%s: observation_obligation.q_r %r is outside the closed observation-scope set %s" % (predicate["gcir_id"], q_r, OBSERVATION_SCOPES))
        if "kappa_r" not in omega:
            issues.append("%s: observation_obligation.kappa_r is missing" % predicate["gcir_id"])
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# evidence representation
# ---------------------------------------------------------------------------


def evidence_representation(bundle) -> Tuple[bool, List[str]]:
    """Every predicate's evidence path (producer, schema, requirement list)
    is represented; a decisive mandatory predicate must declare at least one
    evidence_requirement."""
    payload = _payload_of(bundle)
    gate_map = payload.get("gate_map", {})
    issues = []
    for predicate in payload.get("predicates", []):
        gcir_id = predicate["gcir_id"]
        if not predicate.get("evidence_producer"):
            issues.append("%s: evidence_producer missing" % gcir_id)
        if not predicate.get("evidence_schema_ref"):
            issues.append("%s: evidence_schema_ref missing" % gcir_id)
        gate_entry = gate_map.get(gcir_id, {})
        if gate_entry.get("gate_type") == "mandatory" and gate_entry.get("mandatory_role") == "decisive":
            if not predicate.get("evidence_requirement"):
                issues.append("%s: decisive mandatory predicate declares no evidence_requirement" % gcir_id)
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# failure semantics
# ---------------------------------------------------------------------------


def failure_semantics(nominal_bundle, candidate_bundle) -> Tuple[bool, List[str]]:
    """A candidate must not weaken a nominal's declared failure response
    (``on_fail``: SAFE_STATE > ESCALATE > WARN, strongest first) or silently
    drop a declared escalation route."""
    issues = []
    for acs_id, nominal, candidate in _matched_pairs(nominal_bundle, candidate_bundle):
        if candidate is None:
            continue
        nominal_fail = nominal.get("on_fail")
        candidate_fail = candidate.get("on_fail")
        if nominal_fail in _ON_FAIL_STRENGTH and candidate_fail in _ON_FAIL_STRENGTH:
            if _ON_FAIL_STRENGTH[candidate_fail] < _ON_FAIL_STRENGTH[nominal_fail]:
                issues.append("%s: on_fail weakened from %r to %r" % (acs_id, nominal_fail, candidate_fail))
        if nominal.get("escalation") and not candidate.get("escalation"):
            issues.append("%s: escalation route dropped" % acs_id)
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# aggregate runner
# ---------------------------------------------------------------------------

#: check_id -> whether it needs (nominal, candidate) or a single bundle.
_COMPARATIVE_CHECKS = {
    "no_narrowing": no_narrowing,
    "no_broadening": no_broadening,
    "no_invention": no_invention,
    "primary_class_preservation": primary_class_preservation,
    "exception_scope": exception_scope,
    "failure_semantics": failure_semantics,
}
_SINGLE_BUNDLE_CHECKS = {
    "total_disposition": total_disposition,
    "synchronization_contract_representation": synchronization_contract_representation,
    "observation_obligation": observation_obligation,
    "evidence_representation": evidence_representation,
}


def run_all_v12_checks(nominal_bundle, candidate_bundle, **kwargs) -> Dict[str, Tuple[bool, List[str]]]:
    """Run every headline v1.2 validator that operates purely on compiled
    bundles (spec section 5's list, minus ``indeterminacy`` -- a compile-time
    outcome, not a post-hoc bundle check -- and minus ``lifecycle``/
    ``declared_path``/``origin``/``judgment_hash_binding``, which need
    caller-supplied registries/expected values and are better called
    directly; see their own docstrings).
    """
    results = {name: fn(nominal_bundle, candidate_bundle) for name, fn in _COMPARATIVE_CHECKS.items()}
    results.update({name: fn(candidate_bundle) for name, fn in _SINGLE_BUNDLE_CHECKS.items()})
    return results
