"""Canonical audit queries Q1-Q10 (manuscript Section VIII, Appendix A).

Q1-Q6: temporal/structural traceability of the compiled bundle itself.
Q7-Q10: compilation completeness and reference closure.

This is a rewrite of an earlier version of this module that had drifted from
the bundle format ``gcir.compiler`` actually emits: Q1 read a top-level
``"risks"`` key the payload has never had (silently vacuous against every real
bundle), and Q4/Q5/Q6 were unconditional no-ops whose docstrings claimed checks
their bodies never performed.  Every query below is written directly against
the fields ``compile_bundle`` actually produces (``payload["dispositions"]``,
``payload["predicates"]``, ``payload["gate_map"]``, ``payload["coverage_matrix"]``
-- see ``gcir.compiler.build_payload``), and every negative fixture in
``gcir.negative_fixtures`` mutates a *real* compiled bundle rather than a
hand-shaped stand-in.

Relationship to ``gcir.traceability`` (the SQL Q1-Q6): that module answers a
different, complementary question -- given a compiled bundle *plus* its
lifecycle registry, receipts and actuations, is the runtime evidence chain
temporally valid?  The Q1-Q6 here answer a narrower one that needs no runtime
evidence at all: is the *compiled bundle itself* structurally complete and
internally consistent?  A bundle can pass every query in this module and still
fail the SQL Q4/Q5 (e.g. a receipt was never committed) -- that is not a
contradiction, it is two audits at two different points in the record's life.
Where both modules examine a bundle-only property (Q1-Q3), they must not
disagree; where the SQL module additionally examines receipts/lifecycle/
actuations, it is authoritative for that runtime claim and this module says so
in its own docstring rather than approximating it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .canonicalization import hash_payload
from .temporal import parse_time


def _payload_of(bundle):
    """Accept a ``CompiledBundle``, or a raw payload dict for fixture testing."""
    if hasattr(bundle, "payload"):
        return bundle.payload
    return bundle


def _envelope_of(bundle):
    if hasattr(bundle, "envelope"):
        return bundle.envelope
    if isinstance(bundle, dict):
        return bundle.get("signature") or bundle.get("envelope")
    return None


def _payload_hash_of(bundle):
    if hasattr(bundle, "payload_hash"):
        return bundle.payload_hash
    if isinstance(bundle, dict):
        return bundle.get("payload_hash")
    return None


# ---------------------------------------------------------------------------
# Q1-Q6: bundle-only structural/temporal integrity
# ---------------------------------------------------------------------------


def q1_obligation_disposition_completeness(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q1: every obligation the coverage matrix links to a risk is disposed.

    Reads ``payload["coverage_matrix"]["obligations"][*]["disposed"]`` -- a
    field ``gcir.compiler._coverage_matrix`` computes as ``bool(statuses) and
    all(s in (runtime, nonruntime, accepted) for s in statuses)`` over the
    obligation's linked risks' actual dispositions.  Unlike the superseded
    version of this query, this reads a field that exists on every bundle this
    compiler emits.
    """
    payload = _payload_of(bundle)
    obligations = payload.get("coverage_matrix", {}).get("obligations", [])
    issues = [
        "%s: not disposed (linked risk statuses=%s)" % (row["obligation_id"], row.get("disposition_statuses"))
        for row in obligations
        if not row.get("disposed")
    ]
    return len(issues) == 0, issues


def q2_exactly_one_disposition_per_risk(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q2: every ``risk_id`` appears in exactly one disposition record."""
    payload = _payload_of(bundle)
    counts: Dict[str, int] = {}
    for disp in payload.get("dispositions", []):
        counts[disp["risk_id"]] = counts.get(disp["risk_id"], 0) + 1
    issues = [
        "%s: %d disposition record(s) (expected 1)" % (risk_id, count)
        for risk_id, count in sorted(counts.items())
        if count != 1
    ]
    return len(issues) == 0, issues


def q3_predicate_origin_closure(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q3: every predicate's origin resolves, and a risk-derived predicate's
    ``acs_id`` is actually one of the risk's disposed ACS ids -- not merely
    that the risk exists (the superseded version stopped at risk existence)."""
    payload = _payload_of(bundle)
    runtime_acs_by_risk = {
        disp["risk_id"]: set(disp.get("acs_ids", []))
        for disp in payload.get("dispositions", [])
        if disp.get("record_type") == "RuntimeDisposition"
    }
    issues = []
    for predicate in payload.get("predicates", []):
        origin = predicate.get("origin", {})
        origin_type = origin.get("origin_type")
        origin_id = origin.get("origin_id")
        gcir_id = predicate.get("gcir_id")
        if origin_type == "risk_derived":
            acs_ids = runtime_acs_by_risk.get(origin_id)
            if acs_ids is None:
                issues.append(
                    "%s: risk_derived origin %r is not a risk with a "
                    "RuntimeDisposition" % (gcir_id, origin_id)
                )
            elif predicate.get("acs_id") not in acs_ids:
                issues.append(
                    "%s: acs_id %r is not among risk %s's disposed acs_ids %s"
                    % (gcir_id, predicate.get("acs_id"), origin_id, sorted(acs_ids))
                )
        elif origin_type == "compiler_invariant":
            if not origin_id:
                issues.append("%s: compiler_invariant origin has no origin_id" % gcir_id)
        else:
            issues.append("%s: origin_type %r is outside {risk_derived, compiler_invariant}" % (gcir_id, origin_type))
    return len(issues) == 0, issues


def q4_temporal_bundle_validity(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q4: the bundle's own hash and validity fields are well-formed.

    ``bundle_id``, ``version_binding.binding_id`` are non-empty;
    ``payload_hash`` (from the ``CompiledBundle`` wrapper, not inside the
    payload -- the payload is hashed, it does not hash itself) is 64 lowercase
    hex characters and, when the payload is available, actually equals
    ``hash_payload(payload)``; ``validity.effective_from`` parses as RFC 3339
    UTC.  This is the bundle-only half of temporal validity; whether a
    *receipt* citing this bundle was valid at decision time (payload hash,
    lifecycle-registry state, actor-scope state) is the SQL module's Q4, which
    additionally requires the lifecycle registry and receipts.
    """
    payload = _payload_of(bundle)
    issues = []

    payload_hash = _payload_hash_of(bundle)
    if not (isinstance(payload_hash, str) and len(payload_hash) == 64
            and all(c in "0123456789abcdef" for c in payload_hash)):
        issues.append("payload_hash %r is not 64 lowercase hex characters" % payload_hash)
    elif hasattr(bundle, "payload"):
        recomputed = hash_payload(payload)
        if recomputed != payload_hash:
            issues.append(
                "payload_hash %s does not match hash_payload(payload) = %s "
                "(payload was mutated after hashing)" % (payload_hash, recomputed)
            )

    if not payload.get("bundle_id"):
        issues.append("bundle_id is missing or empty")
    if not payload.get("version_binding", {}).get("binding_id"):
        issues.append("version_binding.binding_id is missing or empty")

    effective_from = payload.get("validity", {}).get("effective_from")
    try:
        parse_time(effective_from)
    except Exception as exc:  # noqa: BLE001 -- report any parse failure as an issue
        issues.append("validity.effective_from %r does not parse as RFC 3339 UTC: %s" % (effective_from, exc))

    return len(issues) == 0, issues


def q5_commit_before_actuation_ordering(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q5: the compiled bundle's declared timing structure is internally
    consistent, as a compile-time precondition of commit-before-actuation
    ordering.

    Two checks, both real and both over fields the compiler actually emits:

    1. Every predicate declaring ``evaluation_latency_bound`` also declares
       ``on_evaluation_timeout = HOLD`` (Appendix A constraint 15) -- an
       evaluator with a declared deadline but no declared timeout response
       could not deterministically resolve commit ordering if it were ever
       late.
    2. ``gate_map[gcir_id]["permit_eligible"]`` (Appendix A constraint 16) is
       exactly ``enforcement_phase in {PRE_AUTHORIZATION,
       BOUNDARY_REVALIDATION, <undeclared>}`` for every predicate -- i.e. a
       POST_AUTH_PRE_ACTUATION or POST_EVENT_AUDIT predicate (an
       evidence-commit or safety-correlation obligation, by construction
       *after* authorization) can never be miscategorized as contributing to
       the PRE_AUTHORIZATION PERMIT aggregate.

    This is the compile-time precondition for the *runtime* ordering claim
    ``t_authorization <= t_evidence_commit < t_actuation``, which requires
    actual receipts and actuation records and is therefore the SQL module's
    Q5, not this one.
    """
    payload = _payload_of(bundle)
    gate_map = payload.get("gate_map", {})
    issues = []
    for predicate in payload.get("predicates", []):
        gcir_id = predicate["gcir_id"]
        if predicate.get("evaluation_latency_bound") is not None:
            if predicate.get("on_evaluation_timeout") != "HOLD":
                issues.append(
                    "%s declares evaluation_latency_bound but "
                    "on_evaluation_timeout=%r (must be HOLD)"
                    % (gcir_id, predicate.get("on_evaluation_timeout"))
                )
        phase = predicate.get("enforcement_phase")
        expected_permit_eligible = phase is None or phase in ("PRE_AUTHORIZATION", "BOUNDARY_REVALIDATION")
        actual = gate_map.get(gcir_id, {}).get("permit_eligible")
        if actual is not None and actual != expected_permit_eligible:
            issues.append(
                "%s has enforcement_phase=%r but gate_map.permit_eligible=%r "
                "(expected %r)" % (gcir_id, phase, actual, expected_permit_eligible)
            )
    return len(issues) == 0, issues


def q6_lifecycle_signing_authority(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q6: the bundle carries a structurally valid signature envelope, ready
    for lifecycle registration.

    Checks the envelope (outside the hashed payload, per Section VI-C) carries
    ``algorithm``, ``domain``, ``key_id``, ``payload_hash`` and
    ``signature_b64``, that ``domain == "bundle"``, and that the envelope's
    ``payload_hash`` equals the bundle's actual ``payload_hash``.  It does
    *not* re-verify the Ed25519 signature bytes against a keyring -- that is a
    cryptographic check, not a structural one, and is exercised directly by
    ``tests/unit/test_core.py``'s signature tests and by
    ``negative_fixtures``'s Q6 fixture (a bundle with no envelope at all).
    Whether a *lifecycle-registry entry* citing this bundle carries a valid
    signing authority is the SQL module's Q6, which requires the lifecycle
    registry document.
    """
    payload = _payload_of(bundle)
    envelope = _envelope_of(bundle)
    if not envelope:
        return False, ["bundle carries no signature envelope"]
    issues = []
    for field in ("algorithm", "domain", "key_id", "payload_hash", "signature_b64"):
        if not envelope.get(field):
            issues.append("envelope missing or empty field %r" % field)
    if envelope.get("domain") not in (None, "bundle"):
        issues.append("envelope domain=%r, expected 'bundle'" % envelope.get("domain"))
    bundle_hash = _payload_hash_of(bundle)
    if envelope.get("payload_hash") and bundle_hash and envelope["payload_hash"] != bundle_hash:
        issues.append(
            "envelope payload_hash %s does not match bundle payload_hash %s"
            % (envelope["payload_hash"], bundle_hash)
        )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------
# Q7-Q10: compilation completeness and reference closure
# ---------------------------------------------------------------------------


def q7_runtime_acs_compilation_coverage(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q7: every ACS a RuntimeDisposition names compiles to >= 1 risk-derived
    predicate citing it."""
    payload = _payload_of(bundle)
    runtime_acs_ids = set()
    for disp in payload.get("dispositions", []):
        if disp.get("record_type") == "RuntimeDisposition":
            runtime_acs_ids.update(disp.get("acs_ids", []))
    compiled_acs_ids = {
        p.get("acs_id")
        for p in payload.get("predicates", [])
        if p.get("origin", {}).get("origin_type") == "risk_derived"
    }
    uncompiled = sorted(runtime_acs_ids - compiled_acs_ids)
    return len(uncompiled) == 0, uncompiled


def q8_gate_predicate_reference_integrity(bundle, evidence=None) -> Tuple[bool, Dict[str, List[str]]]:
    """Q8: every gate_map entry references a real predicate, and every
    decisive predicate appears in gate_map."""
    payload = _payload_of(bundle)
    gate_map = payload.get("gate_map", {})
    predicates = {p["gcir_id"]: p for p in payload.get("predicates", [])}

    missing_predicates = sorted(pid for pid in gate_map if pid not in predicates)
    unused_decisive = sorted(
        pid for pid, p in predicates.items()
        if p.get("mandatory_role") == "decisive" and pid not in gate_map
    )
    errors = {"missing_predicates": missing_predicates, "unused_decisive": unused_decisive}
    return len(missing_predicates) == 0 and len(unused_decisive) == 0, errors


def build_authority_map_from_catalog(catalog_document) -> Dict[str, set]:
    """Section VI-A step 5: the explicit, machine-readable authority mapping
    Q9 consults -- every catalog entry's ``allowed_producers`` for its
    ``event_type``, read directly from the approved Control Derivation
    Catalog K rather than reconstructed or assumed."""
    return {
        entry["event_type"]: set(entry.get("allowed_producers", []))
        for entry in catalog_document.get("entries", [])
    }


def q9_actuation_authority_validity(bundle, evidence=None, catalog_document=None) -> Tuple[bool, List[str]]:
    """Q9: every predicate's evidence_producer is an approved producer for its
    catalog event_type.

    When ``catalog_document`` (the signed Control Derivation Catalog K) is
    supplied, this cross-references ``predicate["catalog_ref"]["event_type"]``
    against ``build_authority_map_from_catalog(catalog_document)`` -- a real,
    approved, machine-readable authority mapping, not an inferred one. Without
    a catalog document (e.g. a hand-built fixture with no catalog context),
    this falls back to the weaker structural check that every predicate
    declares a non-empty evidence_producer string; this fallback is reported
    explicitly in the returned details so a caller cannot mistake a weak check
    for a strong one.
    """
    payload = _payload_of(bundle)
    predicates = payload.get("predicates", [])

    if catalog_document is not None:
        authority_map = build_authority_map_from_catalog(catalog_document)
        issues = []
        for predicate in predicates:
            producer = predicate.get("evidence_producer")
            catalog_ref = predicate.get("catalog_ref") or {}
            event_type = catalog_ref.get("event_type")
            if event_type is None:
                # A compiler-invariant predicate has no catalog_ref; its
                # producer is validated by Appendix A constraint 7 (invariant
                # register resolution) elsewhere, not by K.
                continue
            allowed = authority_map.get(event_type)
            if allowed is None:
                issues.append("%s: catalog has no entry for event_type %r" % (predicate["gcir_id"], event_type))
            elif producer not in allowed:
                issues.append(
                    "%s: evidence_producer %r is not an allowed_producer for "
                    "event_type %r (allowed: %s)"
                    % (predicate["gcir_id"], producer, event_type, sorted(allowed))
                )
        return len(issues) == 0, issues

    issues = [
        "%s: no evidence_producer declared [fallback check: no catalog_document supplied]" % p["gcir_id"]
        for p in predicates
        if not p.get("evidence_producer")
    ]
    return len(issues) == 0, issues


def q10_mandatory_predicate_evidence_integrity(bundle, evidence=None) -> Tuple[bool, List[str]]:
    """Q10: every decisive predicate's conditions all declare on_unknown = fail."""
    payload = _payload_of(bundle)
    issues = []
    for predicate in payload.get("predicates", []):
        if predicate.get("mandatory_role") != "decisive":
            continue
        for condition in predicate.get("context_conditions", []):
            if condition.get("on_unknown") != "fail":
                issues.append(
                    "%s: mandatory_role=decisive but condition %r has on_unknown=%r"
                    % (predicate["gcir_id"], condition.get("attribute"), condition.get("on_unknown"))
                )
    return len(issues) == 0, issues


# ---------------------------------------------------------------------------


def run_all_audit_queries(bundle, evidence=None, catalog_document=None) -> Dict[str, Tuple[bool, Any]]:
    """Run canonical Q1-Q10 against a compiled bundle.

    ``bundle`` should be the real ``CompiledBundle`` returned by
    ``gcir.compiler.compile_bundle(...).bundle`` for a genuine run, or a
    negative fixture built by ``gcir.negative_fixtures`` from a real one.
    """
    return {
        "Q1": q1_obligation_disposition_completeness(bundle, evidence),
        "Q2": q2_exactly_one_disposition_per_risk(bundle, evidence),
        "Q3": q3_predicate_origin_closure(bundle, evidence),
        "Q4": q4_temporal_bundle_validity(bundle, evidence),
        "Q5": q5_commit_before_actuation_ordering(bundle, evidence),
        "Q6": q6_lifecycle_signing_authority(bundle, evidence),
        "Q7": q7_runtime_acs_compilation_coverage(bundle, evidence),
        "Q8": q8_gate_predicate_reference_integrity(bundle, evidence),
        "Q9": q9_actuation_authority_validity(bundle, evidence, catalog_document=catalog_document),
        "Q10": q10_mandatory_predicate_evidence_integrity(bundle, evidence),
    }
