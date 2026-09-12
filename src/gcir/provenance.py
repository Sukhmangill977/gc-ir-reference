"""Verify the full governance-to-predicate provenance chain for every
Approved Control Specification in a case: risk -> obligation(s) -> signed
judgment-record selection/approval -> disposition -> ACS -> compiled
predicate.

This exists specifically so a v1.1-prospective ACS (one added without a
signed judgment-record entry, or naming a risk/obligation that does not
exist) can be caught mechanically rather than asserted only in prose
(docs/CASE_B_V1_1_RATIONALE.md). Every ACS in every case this codebase loads
is checked identically -- there is no separate, weaker path for a "new" ACS.

Note on scope: the manuscript states every compiled record carries
``judgment_ref = (J.id, J.version, J.hash)`` at the *predicate* level
(Section IV-A). This implementation's compiler stamps the judgment reference
at the *bundle* level only (``payload["judgment_record_ref"]``), not
per-predicate -- a pre-existing simplification, unchanged by this
generation's work (Case A and Case B's historical ACS records carry the same
bundle-level-only reference). What this module verifies is therefore the
finer-grained chain that *is* actually recorded per-ACS in the judgment
record's own ``selections``/``approvals`` lists, which is a real and
sufficient substitute for the purposes of "does this ACS have genuine,
attributable governance provenance" -- it is not a claim that per-predicate
``judgment_ref`` stamping has been implemented.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ProvenanceError(Exception):
    """Raised when an ACS lacks a complete, genuine provenance chain."""


def verify_acs_provenance(documents: Dict[str, Any], bundle) -> List[Dict[str, Any]]:
    """Verify the provenance chain for every ACS in ``documents`` (the
    ``CaseBundleInputs.documents`` dict: assessment, dispositions,
    approved_control_specifications, judgment_record) against the compiled
    ``bundle``.

    Returns one record per ACS, each carrying every link found; raises
    ``ProvenanceError`` naming every ACS with a broken or missing link (never
    silently skips one).
    """
    assessment = documents["assessment"]
    risk_ids = {r["risk_id"] for r in assessment["risk_register"]}
    obligation_ids = {o["obligation_id"] for o in assessment["obligations"]}

    dispositions = documents["dispositions"]["records"]
    disposition_by_risk = {d["risk_id"]: d for d in dispositions}

    judgment = documents["judgment_record"]
    selections_by_acs = {s["acs_id"]: s for s in judgment["selections"]}
    approvals_by_acs = {a["acs_id"]: a for a in judgment["approvals"]}

    predicates_by_acs: Dict[str, List[dict]] = {}
    for predicate in bundle.predicates:
        if predicate["origin"]["origin_type"] == "risk_derived":
            predicates_by_acs.setdefault(predicate["acs_id"], []).append(predicate)

    acs_records = documents["approved_control_specifications"]["records"]

    results = []
    errors = []
    for acs in acs_records:
        acs_id = acs["acs_id"]
        risk_id = acs["risk_id"]
        record = {
            "acs_id": acs_id, "risk_id": risk_id,
            "obligation_refs": list(acs.get("obligation_refs", [])),
            "links": {},
        }

        # 1. risk exists
        record["links"]["risk_exists"] = risk_id in risk_ids
        if not record["links"]["risk_exists"]:
            errors.append("%s: risk_id %r is not in the risk register" % (acs_id, risk_id))

        # 2. every declared obligation exists
        unresolved_obligations = [o for o in record["obligation_refs"] if o not in obligation_ids]
        record["links"]["obligations_resolve"] = not unresolved_obligations
        if unresolved_obligations:
            errors.append("%s: obligation_refs %s do not resolve" % (acs_id, unresolved_obligations))

        # 3. judgment record carries a signed selection for this ACS
        selection = selections_by_acs.get(acs_id)
        record["links"]["judgment_selection"] = selection is not None
        if selection is None:
            errors.append("%s: no judgment-record selection entry" % acs_id)
        else:
            record["selected_by"] = selection.get("selected_by")
            record["selection_rationale"] = selection.get("rationale")
            record["links"]["selection_names_this_risk"] = selection.get("risk_id") == risk_id
            if not record["links"]["selection_names_this_risk"]:
                errors.append(
                    "%s: judgment selection names risk_id %r, not %r"
                    % (acs_id, selection.get("risk_id"), risk_id)
                )

        # 4. judgment record carries a signed approval for this ACS
        approval = approvals_by_acs.get(acs_id)
        record["links"]["judgment_approval"] = approval is not None
        if approval is None:
            errors.append("%s: no judgment-record approval entry" % acs_id)
        else:
            record["approver"] = approval.get("approver")
            record["approval_time"] = approval.get("approval_time")
            record["approval_forum"] = approval.get("forum")

        # 5. the risk's RuntimeDisposition names this acs_id
        disposition = disposition_by_risk.get(risk_id)
        acs_ids_in_disposition = disposition.get("acs_ids", []) if disposition else []
        record["links"]["disposition_names_acs"] = acs_id in acs_ids_in_disposition
        if not record["links"]["disposition_names_acs"]:
            errors.append(
                "%s: risk %r's disposition acs_ids %s does not include this ACS"
                % (acs_id, risk_id, acs_ids_in_disposition)
            )

        # 6. exactly one compiled, risk-derived predicate cites this ACS,
        #    with origin_id == risk_id
        compiled = predicates_by_acs.get(acs_id, [])
        record["links"]["compiled_exactly_once"] = len(compiled) == 1
        if len(compiled) != 1:
            errors.append(
                "%s: %d compiled risk-derived predicate(s) cite this ACS (expected exactly 1)"
                % (acs_id, len(compiled))
            )
        else:
            predicate = compiled[0]
            record["gcir_id"] = predicate["gcir_id"]
            record["links"]["predicate_origin_matches_risk"] = predicate["origin"]["origin_id"] == risk_id
            if not record["links"]["predicate_origin_matches_risk"]:
                errors.append(
                    "%s: compiled predicate %s origin_id=%r does not match risk_id %r"
                    % (acs_id, predicate["gcir_id"], predicate["origin"]["origin_id"], risk_id)
                )

        record["complete"] = all(record["links"].values())
        results.append(record)

    if errors:
        raise ProvenanceError(
            "%d ACS record(s) have an incomplete provenance chain:\n  %s"
            % (len(errors), "\n  ".join(errors))
        )
    return results
