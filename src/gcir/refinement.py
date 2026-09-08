"""Psi_K support tooling (manuscript Section IV).

    (D, Delta) in Psi_K(G),  with  Psi_K(G, J) -> (D, Delta) single-valued given J.

**What this module does NOT do, by design.**  It does not read risk prose and
propose a control.  There is no embedding, no similarity score, no classifier, no
language model, and no keyword heuristic anywhere in this file or anywhere it
calls.  Section IV-A: "Psi_K is not a legal interpreter and does not infer
requirements from unconstrained natural language."

**What it does.**  It loads the approved governance artifacts and the approved
catalog, accepts the explicit human-approved selections carried in the signed
judgment record J, validates that those selections are ones the catalog actually
permits, and emits the approved dispositions Delta and Approved Control
Specifications D.  The software is a *validator and assembler* of signed human
acts, which is the only role the manuscript gives it.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import (
    DISPOSITION_STATUSES,
    REASON_CODES,
    ApprovedControlSpecification,
    Disposition,
    JudgmentRecord,
    ValidationError,
)
from .temporal import is_within, parse_time


class RefinementClosure:
    """The single-valued closure of ``Psi_K`` under a specific judgment record."""

    def __init__(self, assessment, catalog, judgment, dispositions, acs_records):
        self.assessment = assessment
        self.catalog = catalog
        self.judgment = judgment
        self.dispositions = dispositions
        self.acs_records = acs_records

    @property
    def acs_index(self):
        return {a.acs_id: a for a in self.acs_records}

    @property
    def disposition_index(self):
        return {d.risk_id: d for d in self.dispositions}


def close_relation(assessment, catalog, judgment, dispositions, acs_records):
    """Validate that ``J`` closes ``Psi_K`` over this assessment, and return the
    closure.

    Every check here is a *conformance* check on a human decision that has already
    been made and signed.  Nothing is chosen by the software.
    """
    problems = []

    disposition_list = [
        d if isinstance(d, Disposition) else Disposition.from_mapping(d)
        for d in dispositions
    ]
    acs_list = [
        a if isinstance(a, ApprovedControlSpecification)
        else ApprovedControlSpecification(a)
        for a in acs_records
    ]
    acs_index = {a.acs_id: a for a in acs_list}
    if len(acs_index) != len(acs_list):
        raise ValidationError(
            "duplicate acs_id in the approved specification set",
            code="DUPLICATE_ACS_ID",
        )

    risk_ids = [r["risk_id"] for r in assessment.risk_register]
    if len(set(risk_ids)) != len(risk_ids):
        raise ValidationError(
            "duplicate risk_id in the risk register", code="DUPLICATE_RISK_ID"
        )

    # -- Totality: exactly one disposition per risk (Section IV-D) ----------
    seen = {}
    for disposition in disposition_list:
        if disposition.risk_id in seen:
            problems.append(
                "risk %s carries more than one disposition" % disposition.risk_id
            )
        seen[disposition.risk_id] = disposition
        if disposition.status not in DISPOSITION_STATUSES:
            problems.append(
                "risk %s has disposition status %r outside the closed set %r"
                % (disposition.risk_id, disposition.status, DISPOSITION_STATUSES)
            )
    for risk_id in risk_ids:
        if risk_id not in seen:
            problems.append("risk %s has no disposition" % risk_id)
    for risk_id in sorted(set(seen) - set(risk_ids)):
        problems.append("disposition references unknown risk %s" % risk_id)

    # -- Judgment record covers every runtime selection ---------------------
    selections = judgment.selection_index
    for disposition in disposition_list:
        if disposition.status != "runtime":
            continue
        if disposition.risk_id not in selections:
            problems.append(
                "risk %s is dispositioned runtime but the judgment record carries "
                "no signed selection for it -- Psi_K is not closed"
                % disposition.risk_id
            )
            continue
        selected_acs = {s["acs_id"] for s in selections[disposition.risk_id]}
        declared = set(disposition.acs_ids)
        if selected_acs != declared:
            problems.append(
                "risk %s: judgment record selects %s but the disposition binds %s"
                % (disposition.risk_id, sorted(selected_acs), sorted(declared))
            )
        for acs_id in sorted(declared):
            if acs_id not in acs_index:
                problems.append(
                    "risk %s binds acs_id %s which is not in the approved "
                    "specification set" % (disposition.risk_id, acs_id)
                )

    # -- Every selection names a template the catalog actually permits ------
    for selection in judgment.selections:
        acs_id = selection["acs_id"]
        acs = acs_index.get(acs_id)
        if acs is None:
            problems.append(
                "judgment record selects acs_id %s which does not exist" % acs_id
            )
            continue
        if acs["event_type"] != selection["event_type"]:
            problems.append(
                "acs %s declares event_type %r but the judgment record assigned %r"
                % (acs_id, acs["event_type"], selection["event_type"])
            )
        if acs["template_id"] != selection["template_id"]:
            problems.append(
                "acs %s declares template_id %r but the judgment record selected %r"
                % (acs_id, acs["template_id"], selection["template_id"])
            )
        if not catalog.has(selection["event_type"], selection["template_id"]):
            problems.append(
                "judgment record selects catalog template %s/%s which the approved "
                "catalog does not contain -- Section IV-B forbids heuristic "
                "resolution" % (selection["event_type"], selection["template_id"])
            )
        if acs.risk_id != selection["risk_id"]:
            problems.append(
                "acs %s belongs to risk %s but was selected under risk %s"
                % (acs_id, acs.risk_id, selection["risk_id"])
            )

    # -- Non-runtime / accepted / unresolved record requirements -----------
    for disposition in disposition_list:
        if disposition.status == "runtime":
            if not disposition.acs_ids:
                problems.append(
                    "risk %s is dispositioned runtime with no Approved Control "
                    "Specification" % disposition.risk_id
                )
        elif disposition.status == "nonruntime":
            problems.extend(_check_nonruntime(disposition))
        elif disposition.status == "accepted":
            problems.extend(_check_accepted(disposition, assessment))
        elif disposition.status == "unresolved":
            problems.extend(_check_unresolved(disposition))
        if disposition.status != "runtime" and disposition.acs_ids:
            problems.append(
                "risk %s is dispositioned %s but binds Approved Control "
                "Specifications" % (disposition.risk_id, disposition.status)
            )

    # -- Approvals in the judgment record ----------------------------------
    approver_index = {a["acs_id"]: a for a in judgment.approvals}
    for acs in acs_list:
        approval = approver_index.get(acs.acs_id)
        if approval is None:
            problems.append(
                "acs %s carries no approval in the judgment record" % acs.acs_id
            )
            continue
        if approval["approver"] != acs["approver"]:
            problems.append(
                "acs %s names approver %r but the judgment record records %r"
                % (acs.acs_id, acs["approver"], approval["approver"])
            )

    if problems:
        raise ValidationError(
            "Psi_K is not closed by the supplied judgment record: %s"
            % "; ".join(problems),
            code="REFINEMENT_NOT_CLOSED",
            detail={"problems": problems},
        )

    return RefinementClosure(assessment, catalog, judgment, disposition_list, acs_list)


def _check_nonruntime(disposition):
    """Appendix A: risk reference, reason code, routed-to control family, control
    reference, owner, approval record."""
    problems = []
    if disposition.reason_code not in REASON_CODES:
        problems.append(
            "risk %s: non-runtime reason_code %r is outside the closed v1.0 set %r"
            % (disposition.risk_id, disposition.reason_code, sorted(REASON_CODES))
        )
    for field_name in ("routed_to_control_family", "control_ref", "owner"):
        if not getattr(disposition, field_name):
            problems.append(
                "risk %s: non-runtime disposition is missing %s"
                % (disposition.risk_id, field_name)
            )
    if not disposition.approval:
        problems.append(
            "risk %s: non-runtime disposition is missing its approval record"
            % disposition.risk_id
        )
    return problems


def _check_accepted(disposition, assessment):
    """Appendix A: risk reference, scope, rationale, acceptor identity (resolving
    to M.accountable_exec), approval time, expiry."""
    problems = []
    for field_name in ("scope", "rationale", "acceptor", "approval_time", "expiry"):
        if not getattr(disposition, field_name):
            problems.append(
                "risk %s: accepted-risk disposition is missing %s"
                % (disposition.risk_id, field_name)
            )
    accountable = assessment.metadata.get("accountable_exec")
    if disposition.acceptor and disposition.acceptor != accountable:
        problems.append(
            "risk %s: acceptor %r does not resolve to M.accountable_exec %r"
            % (disposition.risk_id, disposition.acceptor, accountable)
        )
    return problems


def _check_unresolved(disposition):
    """Appendix A: risk reference, reason code, authority scope blocked."""
    problems = []
    if disposition.reason_code not in REASON_CODES:
        problems.append(
            "risk %s: unresolved reason_code %r is outside the closed v1.0 set"
            % (disposition.risk_id, disposition.reason_code)
        )
    if not disposition.blocked_authority_scope:
        problems.append(
            "risk %s: unresolved disposition does not name the authority scope "
            "blocked from release" % disposition.risk_id
        )
    return problems


def release_admissible(closure):
    """Section IV-D: admissible iff no unresolved disposition and every acceptance
    is within its approved validity interval.

    Returns ``(bool, blockers)``.
    """
    blockers = []
    for disposition in closure.dispositions:
        if disposition.status == "unresolved":
            blockers.append(
                {
                    "risk_id": disposition.risk_id,
                    "reason": "unresolved disposition",
                    "reason_code": disposition.reason_code,
                    "blocked_authority_scope": disposition.blocked_authority_scope,
                }
            )
    return (not blockers), blockers
