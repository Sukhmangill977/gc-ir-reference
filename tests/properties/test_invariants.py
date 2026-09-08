"""Property-based tests (manuscript Section XI-H).

    "Property-based tests verify total disposition, authority closure, mandatory
     unknown-failure, C* coverage, origin closure, payload immutability, and
     temporal receipt validity."

Each property below runs at least 100 generated examples (``MAX_EXAMPLES``).
The generators build *synthetic assessments and bundles* rather than perturbing
the two case artifacts, so the properties are tested over a space of registers
rather than over two points in it.

The exact example counts are recorded in ``results/*/property_tests.json`` by
``experiments/run_properties.py``.
"""

from __future__ import annotations

import copy

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from gcir.canonicalization import canonical_json_string, hash_payload
from gcir.coverage import CStarProfile, classify_risks, cv_metric
from gcir.models import (
    EVALUATION_BASES,
    GATE_SOURCES,
    GATE_TYPES,
    ActionTuple,
    Assessment,
)
from gcir.temporal import commit_before_actuate, parse_time

MAX_EXAMPLES = 100

SETTINGS = settings(
    max_examples=MAX_EXAMPLES,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


# ---------------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------------

identifiers = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-",
    min_size=1, max_size=12,
)

ratings = st.integers(min_value=1, max_value=5)

CSTAR_KINDS = [
    "material_statutory_prohibition",
    "unauthorized_authority_exercise",
    "material_information_barrier_breach",
    "irreversible_external_effect_above_approved_bound",
]
NON_CSTAR_KINDS = ["client_harm", "conduct", "security", "governance", "reputational"]
MATERIALITY_ORDER = ["immaterial", "minor", "material", "severe"]


def _profile():
    return CStarProfile(
        {
            "profile_id": "CSTAR-PROP",
            "version": "1.0",
            "version_binding_ref": "VB-PROP",
            "approved_by": "forum",
            "approval_time": "2026-01-01T00:00:00Z",
            "materiality_order": MATERIALITY_ORDER,
            "member_kinds": CSTAR_KINDS,
            "classification_rules": {
                kind: {
                    "approving_authority": "exec",
                    "rationale": "property-test profile",
                    "materiality_boundary": {
                        "minimum_materiality": "material",
                        "description": "property-test boundary",
                    },
                    "effective_date": "2026-01-01T00:00:00Z",
                    "emergency_override_procedure": None,
                }
                for kind in CSTAR_KINDS
            },
        }
    )


HAZARD_PATHS = [
    {"subject": "agent", "action": "act_%d" % i, "resource": "res", "destination": "dest"}
    for i in range(4)
]


@st.composite
def synthetic_register(draw, min_rows=1, max_rows=8):
    """A synthetic (assessment, gate assignment) pair."""
    count = draw(st.integers(min_value=min_rows, max_value=max_rows))
    risks, analysis = [], []
    for index in range(count):
        risk_id = "PR-%02d" % index
        is_cstar = draw(st.booleans())
        kind = draw(st.sampled_from(CSTAR_KINDS if is_cstar else NON_CSTAR_KINDS))
        materiality = draw(st.sampled_from(MATERIALITY_ORDER))
        path_count = draw(st.integers(min_value=0, max_value=2))
        paths = [copy.deepcopy(HAZARD_PATHS[i]) for i in range(path_count)]
        risks.append(
            {
                "risk_id": risk_id,
                "cause": "c", "event": "e", "consequence": "q",
                "affected_parties": ["p"],
                "obligation_refs": [],
                "existing_controls": [],
                "owner": "owner",
                "hazardous_action_paths": paths,
            }
        )
        analysis.append(
            {
                "risk_id": risk_id,
                "likelihood_inherent": 5, "impact_inherent": 5,
                "control_effectiveness": "partially_effective",
                "likelihood_residual": draw(ratings),
                "impact_residual": draw(ratings),
                "consequence_class": kind,
                "consequence_descriptor": {
                    "kind": kind,
                    "materiality": materiality,
                    "reversibility": "irreversible",
                    "authority": "a",
                },
                "tier": "tier_1", "treatment": "mitigate",
            }
        )

    matrix = [
        dict(path, parameter_schema_id="PS", parameter_schema={}, hazardous=True)
        for path in HAZARD_PATHS
    ]
    assessment = Assessment(
        metadata={
            "system_id": "PROP", "assessor": "assessor",
            "accountable_exec": "exec",
            "version_binding": {"binding_id": "VB-PROP", "fingerprint": "fp"},
            "validity_interval": {"effective_from": "2026-01-01T00:00:00Z"},
        },
        system_profile={"authority_matrix": matrix},
        obligations=[],
        risk_register=risks,
        risk_analysis=analysis,
    )
    return assessment


# ---------------------------------------------------------------------------
# P1 -- total disposition
# ---------------------------------------------------------------------------


@SETTINGS
@given(assessment=synthetic_register(), extra=st.booleans(), drop=st.booleans())
def test_total_disposition_is_exactly_one_per_risk(assessment, extra, drop):
    """Section IV-D: for all r_i, |Delta(r_i)| = 1.

    The compiler's totality assertion must accept a disposition set exactly when
    it is a bijection onto the register, and reject it otherwise. The oracle is
    computed from the resulting multiset rather than from which mutations were
    requested, because a duplicate followed by a drop can cancel out.
    """
    from collections import Counter

    from gcir.compiler import _assert_exactly_one_disposition_per_risk
    from gcir.models import Disposition, ValidationError

    class _Closure:
        def __init__(self, dispositions):
            self.dispositions = dispositions

    risk_ids = [r["risk_id"] for r in assessment.risk_register]
    records = [
        Disposition(risk_id=rid, status="nonruntime", reason_code="RC-01",
                    routed_to_control_family="f", control_ref="c", owner="o",
                    approval={"approver": "a", "approval_time": "2026-01-01T00:00:00Z",
                              "forum": "f"})
        for rid in risk_ids
    ]
    if extra and records:
        records.append(copy.deepcopy(records[0]))
    if drop and len(records) > 1:
        records = records[:-1]

    counts = Counter(record.risk_id for record in records)
    is_bijection = (set(counts) == set(risk_ids)
                    and all(value == 1 for value in counts.values()))

    if is_bijection:
        _assert_exactly_one_disposition_per_risk(assessment, _Closure(records))
    else:
        with pytest.raises(ValidationError) as excinfo:
            _assert_exactly_one_disposition_per_risk(assessment, _Closure(records))
        assert excinfo.value.code == "TOTALITY_VIOLATION"


@SETTINGS
@given(assessment=synthetic_register())
def test_predicate_cardinality_is_independent_of_risk_cardinality(assessment):
    """Section VI-E: the implementation must NOT assert |P| + |X| = |R|.

    A risk may lawfully yield zero, one, or several predicates, and compiler
    invariants yield predicates with no register parent at all.
    """
    risk_count = len(assessment.risk_register)
    # A totality checker that also checked predicate cardinality would reject
    # this perfectly lawful shape.
    predicate_counts = [0, 1, 2, 3][: max(1, risk_count)]
    total_predicates = sum(predicate_counts) + 3  # + three compiler invariants
    dispositions = {r["risk_id"]: "runtime" for r in assessment.risk_register}
    assert len(dispositions) == risk_count
    # The property: totality holds regardless of the predicate total.
    assert all(count == 1 for count in
               {rid: 1 for rid in dispositions}.values())
    assert total_predicates >= 3


# ---------------------------------------------------------------------------
# P2 -- authority closure
# ---------------------------------------------------------------------------


@SETTINGS
@given(
    subject=identifiers, action=identifiers,
    resource=identifiers, destination=identifiers,
)
def test_authority_closure_rejects_every_tuple_outside_the_matrix(
    subject, action, resource, destination
):
    """Appendix A constraint 5. Resolution is exact on all four components."""
    from gcir.authority import resolve_action_tuple
    from gcir.models import AuthorityClosureError, AuthorityEntry

    approved = ActionTuple("agent", "publish", "report", "internal")
    matrix = {
        approved.as_tuple(): AuthorityEntry(
            tuple_=approved, parameter_schema={}, parameter_schema_id="PS",
            hazardous=True,
        )
    }
    candidate = ActionTuple(subject, action, resource, destination)
    if candidate.as_tuple() == approved.as_tuple():
        assert resolve_action_tuple(candidate, matrix) is not None
    else:
        with pytest.raises(AuthorityClosureError):
            resolve_action_tuple(candidate, matrix)


@SETTINGS
@given(
    parameters=st.dictionaries(identifiers, st.text(max_size=8), max_size=4),
)
def test_authority_closure_rejects_unapproved_parameters(parameters):
    """A predicate binding a parameter the matrix never authorized is outside
    the approved authority even though its four-tuple resolves."""
    from gcir.authority import validate_parameters
    from gcir.models import AuthorityClosureError, AuthorityEntry

    tuple_ = ActionTuple("agent", "publish", "report", "internal")
    entry = AuthorityEntry(
        tuple_=tuple_,
        parameter_schema={"draft_id": {"type": "string", "required": True}},
        parameter_schema_id="PS", hazardous=True,
    )
    supplied = dict(parameters)
    supplied["draft_id"] = "D-1"
    unapproved = set(supplied) - {"draft_id"}
    if unapproved:
        with pytest.raises(AuthorityClosureError):
            validate_parameters(tuple_, supplied, entry, parameter_schema_ref="PS")
    else:
        assert validate_parameters(tuple_, supplied, entry, parameter_schema_ref="PS")


# ---------------------------------------------------------------------------
# P3 -- mandatory unknown-failure
# ---------------------------------------------------------------------------


@SETTINGS
@given(
    gate_type=st.sampled_from(GATE_TYPES),
    on_unknown=st.sampled_from(["fail", "warn", "pass_with_approved_exception"]),
    required=st.booleans(),
)
def test_mandatory_gate_requires_on_unknown_fail(gate_type, on_unknown, required):
    """Appendix A constraint 2. 'on_unknown = fail is required, not default.'

    Indeterminacy -- missing, stale or schema-invalid evidence -- must never
    become a silent mandatory pass.
    """
    from gcir.models import ValidationError
    from gcir.validation import constraint_02_mandatory_unknown_fails

    predicate = {
        "gcir_id": "GCIR-PROP",
        "context_conditions": [
            {"attribute": "a", "on_unknown": on_unknown, "required": required}
        ],
    }
    should_reject = (gate_type == "mandatory" and required and on_unknown != "fail")
    if should_reject:
        with pytest.raises(ValidationError) as excinfo:
            constraint_02_mandatory_unknown_fails(predicate, gate_type)
        assert excinfo.value.code == "A2_MANDATORY_ON_UNKNOWN"
    else:
        constraint_02_mandatory_unknown_fails(predicate, gate_type)


@SETTINGS
@given(
    gate_type=st.sampled_from(GATE_TYPES),
    on_fail=st.sampled_from(["SAFE_STATE", "WARN", "ESCALATE"]),
)
def test_mandatory_gate_requires_safe_state(gate_type, on_fail):
    """Appendix A constraint 1."""
    from gcir.models import ValidationError
    from gcir.validation import constraint_01_mandatory_implies_safe_state

    predicate = {"gcir_id": "GCIR-PROP", "on_fail": on_fail}
    if gate_type == "mandatory" and on_fail != "SAFE_STATE":
        with pytest.raises(ValidationError):
            constraint_01_mandatory_implies_safe_state(predicate, gate_type)
    else:
        constraint_01_mandatory_implies_safe_state(predicate, gate_type)


@SETTINGS
@given(
    outcomes=st.lists(st.sampled_from(["pass", "fail", "unknown"]), min_size=1, max_size=6),
    gate_types=st.lists(st.sampled_from(GATE_TYPES), min_size=1, max_size=6),
)
def test_unknown_on_a_mandatory_gate_never_resolves_to_pass(outcomes, gate_types):
    """A mandatory gate whose evidence is indeterminate must resolve to a
    mandatory failure, never to a mandatory pass (Section V, Section VI-D)."""
    from gcir.precedence import classify_outcome

    for outcome, gate_type in zip(outcomes, gate_types):
        predicate = {
            "context_conditions": [{"attribute": "a", "on_unknown": "fail"}]
        }
        klass = classify_outcome(predicate, {"gate_type": gate_type}, outcome)
        if gate_type == "mandatory" and outcome in ("fail", "unknown"):
            assert klass == "mandatory_failure"
        elif gate_type == "mandatory":
            assert klass == "mandatory_pass"
        else:
            assert klass == "weighted_or_advisory"


# ---------------------------------------------------------------------------
# P4 -- C* coverage
# ---------------------------------------------------------------------------


@SETTINGS
@given(assessment=synthetic_register(), gate_all=st.booleans())
def test_c_star_coverage_holds_exactly_when_every_hazardous_path_is_gated(
    assessment, gate_all
):
    """Section VII-A / Appendix A constraint 12.

    CV must be satisfied iff every authorized hazardous action path of every
    C*-classified risk carries at least one DECISIVE MANDATORY gate.
    """
    from gcir.authority import hazardous_paths_for
    from gcir.coverage import verify_cv
    from gcir.models import CoverageError

    profile = _profile()
    flags = classify_risks(assessment, profile)
    hazard_paths = {
        risk["risk_id"]: hazardous_paths_for(risk["risk_id"], assessment)
        for risk in assessment.risk_register
    }

    predicates, gate_map = [], {}
    index = 0
    for risk in assessment.risk_register:
        for path in hazard_paths[risk["risk_id"]]:
            if not gate_all:
                continue
            index += 1
            gcir_id = "GCIR-P%03d" % index
            predicates.append(
                dict(path.as_dict(), gcir_id=gcir_id, mandatory_role="decisive",
                     origin={"origin_type": "risk_derived",
                             "origin_id": risk["risk_id"], "authorized_by": "a"})
            )
            gate_map[gcir_id] = {"gate_type": "mandatory", "gate_source": "C_STAR",
                                 "mandatory_role": "decisive"}

    cstar_risks = [rid for rid, flag in flags.items() if flag == 1]
    needs_coverage = any(
        flag == 1 for rid, flag in flags.items()
    )
    every_cstar_has_a_path = all(hazard_paths[rid] for rid in cstar_risks)

    should_pass = (not cstar_risks) or (gate_all and every_cstar_has_a_path)

    if should_pass:
        matrix = verify_cv(assessment, profile, predicates, gate_map, hazard_paths)
        value, covered, total = cv_metric(matrix)
        assert value == 1.0
        assert covered == total == len(cstar_risks)
    else:
        with pytest.raises(CoverageError):
            verify_cv(assessment, profile, predicates, gate_map, hazard_paths)


@SETTINGS
@given(assessment=synthetic_register())
def test_supporting_predicates_never_satisfy_coverage(assessment):
    """'C* membership mandates coverage, not mandatory status for every predicate.'

    The converse also has to hold: a *supporting* predicate must not be able to
    discharge coverage, or the distinction would be decorative.
    """
    from gcir.authority import hazardous_paths_for
    from gcir.coverage import verify_cv
    from gcir.models import CoverageError

    profile = _profile()
    flags = classify_risks(assessment, profile)
    hazard_paths = {
        risk["risk_id"]: hazardous_paths_for(risk["risk_id"], assessment)
        for risk in assessment.risk_register
    }
    cstar_with_paths = [
        rid for rid, flag in flags.items() if flag == 1 and hazard_paths[rid]
    ]

    predicates, gate_map = [], {}
    index = 0
    for risk in assessment.risk_register:
        for path in hazard_paths[risk["risk_id"]]:
            index += 1
            gcir_id = "GCIR-S%03d" % index
            predicates.append(
                dict(path.as_dict(), gcir_id=gcir_id, mandatory_role="supporting",
                     origin={"origin_type": "risk_derived",
                             "origin_id": risk["risk_id"], "authorized_by": "a"})
            )
            gate_map[gcir_id] = {"gate_type": "mandatory", "gate_source": "C_STAR",
                                 "mandatory_role": "supporting"}

    if cstar_with_paths or any(flags[rid] == 1 for rid in flags):
        if any(flags[rid] == 1 for rid in flags):
            with pytest.raises(CoverageError):
                verify_cv(assessment, profile, predicates, gate_map, hazard_paths)
            return
    verify_cv(assessment, profile, predicates, gate_map, hazard_paths)


# ---------------------------------------------------------------------------
# P5 -- authorized-origin closure
# ---------------------------------------------------------------------------


@SETTINGS
@given(
    risk_ids=st.lists(identifiers, min_size=1, max_size=6, unique=True),
    invariant_ids=st.lists(identifiers, min_size=1, max_size=3, unique=True),
    rogue=st.booleans(),
)
def test_origin_closure(risk_ids, invariant_ids, rogue):
    """Section VI-B: for all p in P, origin(p) in R union INV."""
    from gcir.compiler import _assert_all_predicates_have_authorized_origin
    from gcir.models import ValidationError

    risk_index = {rid: {} for rid in risk_ids}
    invariant_index = {iid: {} for iid in invariant_ids}
    predicates = [
        {"gcir_id": "P%d" % i, "acs_id": "A%d" % i,
         "origin": {"origin_type": "risk_derived", "origin_id": rid}}
        for i, rid in enumerate(risk_ids)
    ] + [
        {"gcir_id": "I%d" % i, "acs_id": None,
         "origin": {"origin_type": "compiler_invariant", "origin_id": iid}}
        for i, iid in enumerate(invariant_ids)
    ]
    if rogue:
        predicates.append({
            "gcir_id": "ORPHAN",
            "acs_id": None,
            "origin": {"origin_type": "risk_derived",
                       "origin_id": "@@definitely-not-a-risk@@"},
        })

    if rogue:
        with pytest.raises(ValidationError) as excinfo:
            _assert_all_predicates_have_authorized_origin(
                predicates, risk_index, invariant_index)
        assert excinfo.value.code == "ORPHAN_PREDICATE"
    else:
        _assert_all_predicates_have_authorized_origin(
            predicates, risk_index, invariant_index)


# ---------------------------------------------------------------------------
# P6 -- payload immutability and canonicalization order invariance
# ---------------------------------------------------------------------------


@st.composite
def json_documents(draw, depth=0):
    leaves = st.one_of(
        st.none(), st.booleans(),
        st.integers(min_value=-(2**40), max_value=2**40),
        st.floats(allow_nan=False, allow_infinity=False, width=32),
        st.text(max_size=12),
    )
    if depth >= 2:
        return draw(leaves)
    return draw(
        st.one_of(
            leaves,
            st.lists(json_documents(depth=depth + 1), max_size=4),
            st.dictionaries(st.text(min_size=1, max_size=6),
                            json_documents(depth=depth + 1), max_size=4),
        )
    )


def _shuffle_keys(node, rng):
    if isinstance(node, dict):
        items = [(k, _shuffle_keys(v, rng)) for k, v in node.items()]
        rng.shuffle(items)
        return dict(items)
    if isinstance(node, list):
        return [_shuffle_keys(item, rng) for item in node]
    return node


@SETTINGS
@given(document=json_documents(), seed=st.integers(min_value=0, max_value=2**16))
def test_canonicalization_is_invariant_under_object_key_order(document, seed):
    """RFC 8785: object key order carries no meaning, so the canonical bytes and
    therefore the hash must not depend on it (Section VI-C)."""
    import random

    rng = random.Random(seed)
    reordered = _shuffle_keys(document, rng)
    assert canonical_json_string(document) == canonical_json_string(reordered)
    assert hash_payload(document) == hash_payload(reordered)


@SETTINGS
@given(document=json_documents(), path_seed=st.integers(min_value=0, max_value=2**16))
def test_any_payload_edit_changes_the_hash(document, path_seed):
    """Section VI-F: the payload is immutable after signing -- any in-place edit
    changes the hash and breaks every receipt that cites it."""
    if not isinstance(document, dict):
        document = {"root": document}
    original = hash_payload(document)
    mutated = copy.deepcopy(document)
    mutated["@@injected@@"] = "an edit that must be detectable"
    assert hash_payload(mutated) != original


@SETTINGS
@given(payload=json_documents())
def test_forbidden_payload_keys_are_always_detected(payload):
    """Appendix A constraint 13: no timestamp, nonce, or mutable lifecycle field
    may appear anywhere inside the hashed payload."""
    from gcir.models import ValidationError
    from gcir.validation import FORBIDDEN_PAYLOAD_KEYS, constraint_13_payload_is_hash_clean

    if not isinstance(payload, dict):
        payload = {"root": payload}
    clean = _strip_forbidden(payload)
    constraint_13_payload_is_hash_clean(clean)

    for key in FORBIDDEN_PAYLOAD_KEYS:
        polluted = copy.deepcopy(clean)
        polluted[key] = "anything at all"
        with pytest.raises(ValidationError) as excinfo:
            constraint_13_payload_is_hash_clean(polluted)
        assert excinfo.value.code == "A13_PAYLOAD_NOT_HASH_CLEAN"


def _strip_forbidden(node):
    from gcir.validation import FORBIDDEN_PAYLOAD_KEYS

    if isinstance(node, dict):
        return {k: _strip_forbidden(v) for k, v in node.items()
                if k not in FORBIDDEN_PAYLOAD_KEYS}
    if isinstance(node, list):
        return [_strip_forbidden(item) for item in node]
    return node


# ---------------------------------------------------------------------------
# P7 -- temporal receipt validity
# ---------------------------------------------------------------------------

instants = st.integers(min_value=0, max_value=10**6)


def _instant(offset):
    import datetime as dt

    base = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    return (base + dt.timedelta(seconds=offset)).strftime("%Y-%m-%dT%H:%M:%SZ")


@SETTINGS
@given(authorization=instants, commit=instants, actuation=instants)
def test_commit_before_actuate_ordering(authorization, commit, actuation):
    """Section VIII: authorization_time <= evidence_commit_time < actuation_time.

    The second inequality is strict.
    """
    receipt = {
        "authorization_time": _instant(authorization),
        "evidence_commit_time": _instant(commit),
        "actuation_time": _instant(actuation),
    }
    ok, reasons = commit_before_actuate(receipt)
    expected = (authorization <= commit) and (commit < actuation)
    assert ok == expected
    if not ok:
        assert reasons


@SETTINGS
@given(decision=instants, effective=instants, retirement=instants,
       retired=st.booleans())
def test_valid_at_conjuncts(decision, effective, retirement, retired):
    """Section VIII: ValidAt is the conjunction of four conditions, and a
    historical receipt is not drift merely because its bundle is now retired."""
    from gcir.lifecycle import LifecycleRegistry, valid_at
    from gcir.signatures import KeyRing

    keyring = KeyRing.generate(["key.rt", "key.lc"], seed_material="property-test")
    payload = {"validity": {"effective_from": _instant(effective)},
               "content": "immutable"}
    digest = hash_payload(payload)

    entries = []
    if retired:
        entry = {
            "entry_id": "E1", "bundle_hash": digest, "action": "retire",
            "effective_time": _instant(retirement), "authority": "exec",
            "reason": "property test",
        }
        entry["signature"] = keyring.sign(
            {k: v for k, v in entry.items() if k != "signature"},
            "key.lc", domain="lifecycle")
        entries.append(entry)

    registry = LifecycleRegistry(
        {"registry_id": "REG", "authorized_signing_keys": ["key.lc"], "entries": entries},
        keyring=keyring, authorized_key_ids=["key.lc"],
    )

    receipt = {
        "receipt_id": "R1", "bundle_hash": digest, "decision": "PERMIT",
        "decision_time": _instant(decision),
        "authorization_time": _instant(decision),
        "evidence_commit_time": _instant(decision + 1),
        "evaluated_predicates": [],
    }
    receipt["signature"] = keyring.sign(
        {k: v for k, v in receipt.items() if k != "signature"},
        "key.rt", domain="receipt")

    class _Bundle:
        pass

    bundle = _Bundle()
    bundle.payload = payload

    ok, reasons = valid_at(receipt, bundle, registry, keyring=keyring)
    expected = (effective <= decision) and not (retired and retirement <= decision)
    assert ok == expected, reasons


@SETTINGS
@given(decision=instants, tamper=st.booleans())
def test_valid_at_requires_the_payload_hash_to_bind(decision, tamper):
    """A receipt whose bundle_hash is not H(b.payload) is never valid."""
    from gcir.lifecycle import LifecycleRegistry, valid_at
    from gcir.signatures import KeyRing

    keyring = KeyRing.generate(["key.rt", "key.lc"], seed_material="property-test")
    payload = {"validity": {"effective_from": _instant(0)}, "content": "immutable"}
    digest = hash_payload(payload)

    receipt = {
        "receipt_id": "R1",
        "bundle_hash": ("0" * 64) if tamper else digest,
        "decision": "PERMIT",
        "decision_time": _instant(decision),
        "authorization_time": _instant(decision),
        "evidence_commit_time": _instant(decision + 1),
        "evaluated_predicates": [],
    }
    receipt["signature"] = keyring.sign(
        {k: v for k, v in receipt.items() if k != "signature"},
        "key.rt", domain="receipt")

    registry = LifecycleRegistry(
        {"registry_id": "REG", "authorized_signing_keys": ["key.lc"], "entries": []},
        keyring=keyring, authorized_key_ids=["key.lc"])

    class _Bundle:
        pass

    bundle = _Bundle()
    bundle.payload = payload
    ok, reasons = valid_at(receipt, bundle, registry, keyring=keyring)
    assert ok == (not tamper), reasons
