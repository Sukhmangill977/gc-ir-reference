"""GC-IR data model and the closed vocabularies the manuscript fixes at v1.0.

Every vocabulary in this module is *closed*: the manuscript states that reason and
warning codes are closed at schema v1.0 and that extension is a schema-version
event (Section V), and that ``evaluation_basis``, ``gate_type``, ``gate_source``,
``origin_type``, ``requirement_class`` and the disposition set are enumerated.

Nothing here reads a clock, consults a locale, or draws a random number.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Closed vocabularies (manuscript Sections III, IV-D, V, VI-B, VII-A)
# ---------------------------------------------------------------------------

#: Section IV-D -- every risk receives exactly one of these.
DISPOSITION_STATUSES = ("runtime", "nonruntime", "accepted", "unresolved")

#: Section V -- ``evaluation_basis`` is constrained to exactly these four.
#: A GC-IR condition never evaluates a probability directly.
EVALUATION_BASES = (
    "deterministic_lookup",
    "threshold_on_measured_value",
    "structural_check",
    "human_attestation",
)

#: Section V / VII-A.
GATE_TYPES = ("mandatory", "weighted", "advisory")
GATE_SOURCES = ("C_STAR", "OTHER_MANDATORY", "SOFT")

#: Section IV-C -- decisive gates block; supporting predicates advise.
MANDATORY_ROLES = ("decisive", "supporting")

#: Section VI-B.
ORIGIN_TYPES = ("risk_derived", "compiler_invariant")

#: Section III, Step 3.
REQUIREMENT_CLASSES = ("statutory", "supervisory", "contractual", "internal")

#: Section V -- responses.
ON_FAIL_RESPONSES = ("SAFE_STATE", "WARN", "ESCALATE")
ON_UNKNOWN_RESPONSES = ("fail", "warn", "pass_with_approved_exception")

#: Section VI-F -- lifecycle registry actions.
LIFECYCLE_ACTIONS = ("retire", "supersede", "revoke")

#: Section V -- typed non-runtime reason codes, closed at schema v1.0.
#: The manuscript names RC-01, RC-02, RC-03 and RC-05.  RC-04 is *not defined in
#: the manuscript*; it is reserved-unused here rather than invented.
#: See docs/FIXTURE_PROVENANCE.md FP-013.
REASON_CODES = {
    "RC-01": "no per-action observable",
    "RC-02": "no authority-matrix action",
    "RC-03": "requires probabilistic judgment",
    "RC-05": "consequence class undefined",
}
RESERVED_UNUSED_REASON_CODES = ("RC-04",)

#: Section V -- warning codes.  WC-01 is a *warning*, never a disposition:
#: "an unresolved reference is not simultaneously a successful compilation and a
#: rejection, so it is a warning, not a disposition".
WARNING_CODES = {
    "WC-01": "unresolved obligation reference",
}

#: Section VII-A -- the base C* profile used by the worked cases.
CSTAR_BASE_PROFILE_V1 = (
    "material_statutory_prohibition",
    "unauthorized_authority_exercise",
    "material_information_barrier_breach",
    "irreversible_external_effect_above_approved_bound",
)

#: Section VI-C -- operators whose conditions require a threshold contract and a
#: unit (Appendix A constraint 3).
NUMERIC_TEMPORAL_OPERATORS = ("<", "<=", ">", ">=", "within", "not_older_than")

#: All operators GC-IR conditions may use.
OPERATORS = NUMERIC_TEMPORAL_OPERATORS + ("==", "!=", "in", "not_in", "subset_of")


class GcirError(Exception):
    """Base class for every deterministic rejection this implementation raises."""

    code = "GCIR_ERROR"

    def __init__(self, message, code=None, detail=None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.detail = detail or {}

    def to_dict(self):
        return {"code": self.code, "message": self.message, "detail": self.detail}


class ValidationError(GcirError):
    code = "VALIDATION_ERROR"


class SignatureError(GcirError):
    code = "SIGNATURE_INVALID"


class VersionBindingError(GcirError):
    code = "VERSION_BINDING_MISMATCH"


class CatalogResolutionError(GcirError):
    code = "UNRESOLVED_TEMPLATE"


class AuthorityClosureError(GcirError):
    code = "AUTHORITY_CLOSURE_VIOLATION"


class CoverageError(GcirError):
    code = "CSTAR_COVERAGE_INCOMPLETE"


class ReleaseInadmissibleError(GcirError):
    code = "RELEASE_INADMISSIBLE"


class PrecedenceError(GcirError):
    code = "PRECEDENCE_INDETERMINATE"


# ---------------------------------------------------------------------------
# Governance input model  G = (M, S, O, R, A)   -- manuscript Section III
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ActionTuple:
    """The (subject, action, resource, destination) quadruple of Section III-2."""

    subject: str
    action: str
    resource: str
    destination: str

    def as_tuple(self):
        return (self.subject, self.action, self.resource, self.destination)

    def as_dict(self):
        return {
            "subject": self.subject,
            "action": self.action,
            "resource": self.resource,
            "destination": self.destination,
        }

    @classmethod
    def from_mapping(cls, mapping):
        return cls(
            subject=mapping["subject"],
            action=mapping["action"],
            resource=mapping["resource"],
            destination=mapping["destination"],
        )

    def __str__(self):
        return "%s/%s/%s/%s" % (
            self.subject,
            self.action,
            self.resource,
            self.destination,
        )


@dataclass(frozen=True)
class AuthorityEntry:
    """One row of ``S.authority_matrix``: an authorized tuple plus its parameter
    schema and whether the path is hazardous (used by the C* coverage rule)."""

    tuple_: ActionTuple
    parameter_schema: Dict[str, Any]
    parameter_schema_id: str = ""
    hazardous: bool = False
    notes: str = ""


@dataclass
class Assessment:
    """M, S, O, R, A held together -- the approved governance assessment."""

    metadata: Dict[str, Any]  # M
    system_profile: Dict[str, Any]  # S
    obligations: List[Dict[str, Any]]  # O
    risk_register: List[Dict[str, Any]]  # R
    risk_analysis: List[Dict[str, Any]]  # A

    # -- convenience indexes ------------------------------------------------
    @property
    def obligation_index(self):
        return {o["obligation_id"]: o for o in self.obligations}

    @property
    def risk_index(self):
        return {r["risk_id"]: r for r in self.risk_register}

    @property
    def analysis_index(self):
        return {a["risk_id"]: a for a in self.risk_analysis}

    @property
    def authority_matrix(self):
        entries = {}
        for row in self.system_profile["authority_matrix"]:
            tup = ActionTuple.from_mapping(row)
            entries[tup.as_tuple()] = AuthorityEntry(
                tuple_=tup,
                parameter_schema=row.get("parameter_schema", {}),
                parameter_schema_id=row.get("parameter_schema_id", ""),
                hazardous=bool(row.get("hazardous", False)),
                notes=row.get("notes", ""),
            )
        return entries

    @property
    def version_binding(self):
        return self.metadata["version_binding"]


# ---------------------------------------------------------------------------
# Refinement products: judgment record J, dispositions, ACS  -- Section IV
# ---------------------------------------------------------------------------


@dataclass
class JudgmentRecord:
    """The signed record ``J`` that closes the relation ``Psi_K`` into a mapping.

    The manuscript is emphatic that ``Psi_K`` is *not* a function of the
    assessment alone (Section IV-A).  ``J`` carries the selections that human
    governance authorities actually made: assigned event types, chosen templates,
    completed control fields, approvals.
    """

    judgment_id: str
    version: str
    assessment_ref: Dict[str, Any]
    catalog_ref: Dict[str, Any]
    selections: List[Dict[str, Any]]
    approvals: List[Dict[str, Any]]
    signature: Optional[Dict[str, Any]] = None

    @property
    def selection_index(self):
        index = {}
        for sel in self.selections:
            index.setdefault(sel["risk_id"], []).append(sel)
        return index


@dataclass
class Disposition:
    """One risk's single disposition (Section IV-D)."""

    risk_id: str
    status: str
    acs_ids: List[str] = field(default_factory=list)
    reason_code: Optional[str] = None
    routed_to_control_family: Optional[str] = None
    control_ref: Optional[str] = None
    owner: Optional[str] = None
    approval: Optional[Dict[str, Any]] = None
    # accepted(RA) fields
    scope: Optional[str] = None
    rationale: Optional[str] = None
    acceptor: Optional[str] = None
    approval_time: Optional[str] = None
    expiry: Optional[str] = None
    # unresolved(U) fields
    blocked_authority_scope: Optional[List[str]] = None

    @classmethod
    def from_mapping(cls, mapping):
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in mapping.items() if k in known})


@dataclass
class ApprovedControlSpecification:
    """``d_ij`` of Section IV-C, held as a mapping so schema validation is the
    single source of structural truth."""

    data: Dict[str, Any]

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    @property
    def acs_id(self):
        return self.data["acs_id"]

    @property
    def risk_id(self):
        return self.data["risk_id"]

    @property
    def action_tuple(self):
        return ActionTuple.from_mapping(self.data)

    @property
    def mandatory_role(self):
        return self.data["mandatory_role"]


# ---------------------------------------------------------------------------
# Compiled artefacts
# ---------------------------------------------------------------------------


@dataclass
class CompiledBundle:
    """The output of Phi: an immutable payload, its hash, and a signature envelope.

    The envelope lives *outside* the hashed payload (Section VI-C), so signing
    time and key identity never perturb ``payload_hash``.
    """

    payload: Dict[str, Any]
    payload_hash: str
    envelope: Optional[Dict[str, Any]] = None
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def predicates(self):
        return self.payload["predicates"]

    @property
    def gate_map(self):
        return self.payload["gate_map"]

    @property
    def escalation_map(self):
        return self.payload["escalation_map"]

    @property
    def coverage_matrix(self):
        return self.payload["coverage_matrix"]

    @property
    def dispositions(self):
        return self.payload["dispositions"]


@dataclass
class CompilationResult:
    bundle: CompiledBundle
    warnings: List[Dict[str, Any]]
    statistics: Dict[str, Any]
