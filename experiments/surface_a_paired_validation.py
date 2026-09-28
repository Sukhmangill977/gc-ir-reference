"""Surface A: eight paired semantic families (Paper 2 v1.2 spec section 2).

    python -m experiments.surface_a_paired_validation --phase development

The primary new experiment in the paper. Freezes exactly eight paired
semantic families, each with one valid nominal and one controlled semantic
negative -- 16 canonical artifacts total, every one a REAL bundle compiled
through the unmodified ``gcir.compiler.compile_bundle`` from Case B v1.1's
own approved base assessment/catalog (``cases/case_b_v1_1``), never a
hand-shaped stand-in payload.

Both members of every pair are compiled with ``verify_signatures=False``
(the same pattern ``experiments.case_d_matrix`` uses for its controlled
negatives): the compiler's signature-verification step is simply never
consulted, so a pair's rejection can never be "caused only by a stale
hash/signature" (spec section 2's explicit disqualifying condition) --
every rejection reported here is the semantic validator's own finding.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402

APPROVED_AUTHORIZER = "forum.chair_m_dubois"  # cases/case_b_v1_1's real APPROVER


def _base_case():
    from gcir.caseio import load_case
    return load_case("case_b_v1_1")


def _compile(case, acs_records):
    from gcir.compiler import compile_bundle

    acs_set = dict(case.documents["approved_control_specifications"])
    acs_set["records"] = acs_records
    inputs = case.compiler_inputs(overrides={"approved_control_specifications": acs_set})
    return compile_bundle(inputs, verify_signatures=False)


def _template_acs(case):
    """ACS-B01-01, the shared starting point for every family below -- a real
    approved decisive-mandatory specification, deep-copied fresh per family
    so mutations never leak across families."""
    records = case.documents["approved_control_specifications"]["records"]
    template = next(r for r in records if r["acs_id"] == "ACS-B01-01")
    return copy.deepcopy(template)


def _other_records(case, exclude_acs_id="ACS-B01-01"):
    records = case.documents["approved_control_specifications"]["records"]
    return [copy.deepcopy(r) for r in records if r["acs_id"] != exclude_acs_id]


# ---------------------------------------------------------------------------
# A1 -- Origin
# ---------------------------------------------------------------------------


def family_a1(case):
    """Origin/judgment-binding (spec 1A, Surface A1): the candidate claims the
    SAME judgment_id/version as the approved reference, but its actual
    canonical judgment content was tampered with after approval -- exactly
    what ``judgment_hash_binding`` exists to catch. Both bundles declare
    ``primary_class`` (a v1.2-only field) so ``schema_version`` is "1.2" and
    ``judgment_record_ref.content_hash`` is populated to compare."""
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    nominal_acs["primary_class"] = "auth"
    negative_acs = copy.deepcopy(nominal_acs)

    original_inputs = case.compiler_inputs()
    nominal_result = _compile(case, [nominal_acs] + other)

    tampered_judgment = copy.deepcopy(case.documents["judgment_record"])
    tampered_judgment["selections"][0]["rationale"] = "TAMPERED AFTER APPROVAL: " + tampered_judgment["selections"][0]["rationale"]
    negative_acs_set = dict(case.documents["approved_control_specifications"])
    negative_acs_set["records"] = [negative_acs] + other
    from gcir.compiler import compile_bundle
    negative_inputs = case.compiler_inputs(overrides={
        "approved_control_specifications": negative_acs_set,
        "judgment_record": tampered_judgment,
    })
    negative_result = compile_bundle(negative_inputs, verify_signatures=False)

    nominal_ok, _ = contract_v12.judgment_hash_binding(nominal_result.bundle, expected_judgment=original_inputs.judgment)
    negative_ok, negative_issues = contract_v12.judgment_hash_binding(negative_result.bundle, expected_judgment=original_inputs.judgment)

    return {
        "family": "A1", "description": "Origin: valid approved origin/J relationship vs. tampered judgment content under the same judgment_id/version",
        "nominal_accepted": nominal_ok, "negative_rejected": not negative_ok,
        "expected_reason": "origin/judgment-binding rejection (judgment_record_ref.content_hash mismatch)",
        "observed_reason": "; ".join(negative_issues),
        "wrong_reason": (not negative_ok) and not negative_issues,
        "packaging_only_reject": False, "unexpected_accept": negative_ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
    }


# ---------------------------------------------------------------------------
# A2 -- Disposition / no-narrowing
# ---------------------------------------------------------------------------


def family_a2(case):
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    negative_acs = _template_acs(case)
    negative_acs["evidence_requirements"] = negative_acs["evidence_requirements"][:-1]

    nominal_result = _compile(case, [nominal_acs] + other)
    negative_result = _compile(case, [negative_acs] + other)
    ok, issues = contract_v12.no_narrowing(nominal_result.bundle, negative_result.bundle)
    nominal_ok, _ = contract_v12.no_narrowing(nominal_result.bundle, nominal_result.bundle)

    return {
        "family": "A2", "description": "Disposition/no-narrowing: all mandatory elements represented vs. one dropped evidence_requirement",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "disposition/no-narrowing rejection (dropped evidence_requirement)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
    }


# ---------------------------------------------------------------------------
# A3 -- Class / role
# ---------------------------------------------------------------------------


def family_a3(case):
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    nominal_acs["primary_class"] = "human"
    negative_acs = _template_acs(case)
    negative_acs["primary_class"] = "auth"  # prohibited collapse human -> auth

    nominal_result = _compile(case, [nominal_acs] + other)
    negative_result = _compile(case, [negative_acs] + other)
    ok, issues = contract_v12.primary_class_preservation(nominal_result.bundle, negative_result.bundle)
    nominal_ok, _ = contract_v12.primary_class_preservation(nominal_result.bundle, nominal_result.bundle)

    return {
        "family": "A3", "description": "Class/role: authorized primary class vs. prohibited collapse human -> auth",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "class-preservation / non-collapse rejection (human -> auth)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
    }


# ---------------------------------------------------------------------------
# A4 -- Action / parameter scope
# ---------------------------------------------------------------------------


def family_a4(case_d_case):
    """Action/parameter scope (spec 1D, Surface A4): uses Case D's confined
    emergency-exception ACS (``ACS-D02-01``) as template, since its
    ``exception.parameter_bounds.max_amount`` is a real numeric ceiling that
    -- unlike Case B v1.1's declared ``action_parameters``, which the
    authority matrix's ``parameter_schema`` closes to exactly three
    non-numeric string fields -- can be widened while the ACS remains
    structurally valid and compiles (parameter_bounds is not authority-
    matrix-checked; only ``action_parameters`` is, per
    ``gcir.authority.validate_parameters``'s closed-schema design)."""
    from gcir import contract_v12
    from gcir.compiler import compile_bundle
    from tools import case_d_control as ctl

    nominal_acs = [ctl.acs_d01_01(), ctl.acs_d02_01(authorized_actor=["treasury.officer_on_duty"], max_amount=1000000)]
    negative_acs = [ctl.acs_d01_01(), ctl.acs_d02_01(authorized_actor=["treasury.officer_on_duty"], max_amount=999999999)]

    nominal_inputs = case_d_case.compiler_inputs(overrides={
        "approved_control_specifications": {"acs_set_id": "D-A4-NOMINAL", "version_binding_ref": ctl.BINDING, "records": nominal_acs},
    })
    negative_inputs = case_d_case.compiler_inputs(overrides={
        "approved_control_specifications": {"acs_set_id": "D-A4-NEGATIVE", "version_binding_ref": ctl.BINDING, "records": negative_acs},
    })
    nominal_result = compile_bundle(nominal_inputs, verify_signatures=False)
    negative_result = compile_bundle(negative_inputs, verify_signatures=False)

    ok, issues = contract_v12.no_broadening(nominal_result.bundle, negative_result.bundle)
    nominal_ok, _ = contract_v12.no_broadening(nominal_result.bundle, nominal_result.bundle)

    return {
        "family": "A4", "description": "Action/parameter scope: approved $1,000,000 emergency ceiling vs. widened to $999,999,999",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "no-broadening rejection (exception.parameter_bounds.max_amount widened beyond the approved ceiling)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
    }


# ---------------------------------------------------------------------------
# A5 -- Exception scope
# ---------------------------------------------------------------------------


_A5_EXCEPTION = {
    "target_requirement": "INT-PERMIT-BIND", "trigger": "EmergencyEvent",
    "authorized_actor": ["compliance.enhanced_approval_officer"],
    "parameter_bounds": {"max_amount": 5000000}, "scope": ["emergency_single_officer_transfer"],
    "lifecycle_version_binding": "VB-CASE-B-1.0",
}


def family_a5(case):
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    nominal_acs["exception"] = copy.deepcopy(_A5_EXCEPTION)
    negative_acs = _template_acs(case)
    negative_acs["exception"] = dict(copy.deepcopy(_A5_EXCEPTION), scope="*")  # global bypass

    nominal_result = _compile(case, [nominal_acs] + other)
    negative_result = _compile(case, [negative_acs] + other)
    ok, issues = contract_v12.exception_scope(nominal_result.bundle, negative_result.bundle)
    nominal_ok, _ = contract_v12.exception_scope(nominal_result.bundle, nominal_result.bundle)

    return {
        "family": "A5", "description": "Exception scope: valid targeted exception vs. widened into a global bypass",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "exception/no-broadening rejection (scope widened into a global bypass)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
    }


# ---------------------------------------------------------------------------
# A6 -- Lifecycle
# ---------------------------------------------------------------------------


def family_a6(case):
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    negative_acs = _template_acs(case)  # lifecycle staleness is a judgment-level property, not an ACS mutation

    nominal_result = _compile(case, [nominal_acs] + other)
    # The negative: the SAME compiled bundle, checked against a "current"
    # judgment version the approved reference has since moved to (a
    # superseded/stale reference) -- structurally valid, semantically stale.
    negative_result = _compile(case, [negative_acs] + other)

    nominal_ok, _ = contract_v12.lifecycle(nominal_result.bundle, expected_judgment_version=nominal_result.bundle.payload["judgment_record_ref"]["version"])
    ok, issues = contract_v12.lifecycle(negative_result.bundle, expected_judgment_version="1.2-SUPERSEDING")

    return {
        "family": "A6", "description": "Lifecycle: current compatible policy/J/profile references vs. a superseded judgment reference",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "lifecycle/validity rejection (stale judgment_record_ref.version)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash == negative_result.bundle.payload_hash,
    }


# ---------------------------------------------------------------------------
# A7 -- Evidence / observation contract
# ---------------------------------------------------------------------------


_A7_OMEGA = {"beta_r": ["realized_amount", "beneficiary", "grant_identifier"], "kappa_r": "binding_v1", "q_r": "cross-request"}


def family_a7(case):
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    nominal_acs["observation_obligation"] = copy.deepcopy(_A7_OMEGA)
    negative_acs = _template_acs(case)
    negative_acs["observation_obligation"] = {"beta_r": ["beneficiary", "grant_identifier"], "kappa_r": "binding_v1", "q_r": "cross-request"}  # dropped realized_amount

    nominal_result = _compile(case, [nominal_acs] + other)
    negative_result = _compile(case, [negative_acs] + other)
    # observation_obligation is a single-bundle REPRESENTATION check (spec
    # 1J/1K say so explicitly): it can confirm beta_r is well-formed, but
    # detecting that one element was DROPPED relative to the approved
    # reference is a no-narrowing instance (Omega_r's beta_r is exactly a
    # "required represented element" under spec 1C), so that is the check
    # this family targets.
    representation_ok, _ = contract_v12.observation_obligation(negative_result.bundle)
    ok, issues = contract_v12.no_narrowing(nominal_result.bundle, negative_result.bundle)
    nominal_ok, _ = contract_v12.no_narrowing(nominal_result.bundle, nominal_result.bundle)

    return {
        "family": "A7", "description": "Evidence/observation contract: required beta_r/scope present vs. a dropped decision-relevant distinction (realized_amount)",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "evidence/Omega_r rejection (realized_amount missing from beta_r)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
        "observation_obligation_representation_ok": representation_ok,
    }


# ---------------------------------------------------------------------------
# A8 -- Unauthorized invention
# ---------------------------------------------------------------------------


def family_a8(case):
    from gcir import contract_v12

    other = _other_records(case)
    nominal_acs = _template_acs(case)
    negative_acs = _template_acs(case)
    negative_acs["standing_permit_ref"] = "SP-NEVER-APPROVED-001"  # invented element with no approved-input backing

    nominal_result = _compile(case, [nominal_acs] + other)
    negative_result = _compile(case, [negative_acs] + other)
    ok, issues = contract_v12.no_invention(nominal_result.bundle, negative_result.bundle)
    nominal_ok, _ = contract_v12.no_invention(nominal_result.bundle, nominal_result.bundle)

    return {
        "family": "A8", "description": "Unauthorized invention: every field traces to approved input vs. an invented standing_permit_ref",
        "nominal_accepted": nominal_ok, "negative_rejected": not ok,
        "expected_reason": "no-invention / applicable neutrality rejection (invented standing_permit_ref)",
        "observed_reason": "; ".join(issues),
        "wrong_reason": (not ok) and not issues, "packaging_only_reject": False, "unexpected_accept": ok,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "negative_payload_hash": negative_result.bundle.payload_hash,
        "hashes_recomputed_not_stale": nominal_result.bundle.payload_hash != negative_result.bundle.payload_hash,
    }


def run_all():
    from gcir.caseio import load_case

    case = _base_case()
    case_d = load_case("case_d_ccs1")
    rows = [
        family_a1(case), family_a2(case), family_a3(case), family_a4(case_d),
        family_a5(case), family_a6(case), family_a7(case), family_a8(case),
    ]
    nominal_accepted = sum(1 for r in rows if r["nominal_accepted"])
    negative_rejected = sum(1 for r in rows if r["negative_rejected"])
    correct_expected_reason = sum(1 for r in rows if r["negative_rejected"] and not r["wrong_reason"])
    wrong_reason_rejects = sum(1 for r in rows if r["wrong_reason"])
    packaging_only_rejects = sum(1 for r in rows if r["packaging_only_reject"])
    unexpected_accepts = sum(1 for r in rows if r["unexpected_accept"])
    stale_hash_only = sum(1 for r in rows if r["negative_rejected"] and not r["hashes_recomputed_not_stale"])

    return {
        "families": rows,
        "counts": {
            "nominal_accepted": "%d/8" % nominal_accepted,
            "semantic_negatives_rejected": "%d/8" % negative_rejected,
            "correct_expected_reason": "%d/8" % correct_expected_reason,
            "wrong_reason_rejects": wrong_reason_rejects,
            "packaging_only_rejects": packaging_only_rejects,
            "unexpected_accepts": unexpected_accepts,
            "stale_hash_only_rejects": stale_hash_only,
        },
        "target": {
            "nominal_accepted": "8/8", "semantic_negatives_rejected": "8/8",
            "correct_expected_reason": "8/8", "wrong_reason_rejects": 0,
            "packaging_only_rejects": 0, "unexpected_accepts": 0,
        },
        "note": "Targets are aspirational per spec section 3; this reports the ACTUAL measured result, not the assumed target.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run_all()
    document = {
        "result_name": "surface_a_paired_validation", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }

    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "surface_a.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print(json.dumps(report["counts"], indent=2))
    print("-> %s" % out_path)
    counts = report["counts"]
    ok = (
        counts["nominal_accepted"] == "8/8" and counts["semantic_negatives_rejected"] == "8/8"
        and counts["correct_expected_reason"] == "8/8" and counts["wrong_reason_rejects"] == 0
        and counts["packaging_only_rejects"] == 0 and counts["unexpected_accepts"] == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
