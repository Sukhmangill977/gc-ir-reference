"""Run the adversarial corpus and record the outcome of every case.

    python -m experiments.run_adversarial [--final]

Each case either *must be rejected with a specific error code* or *must compile*
(the positive controls).  A case that is rejected with the wrong code is recorded
as a mismatch, not silently counted as a pass: rejecting for an unrelated reason
is not evidence that the intended constraint works.

Also exercises the seeded validation rows that the manuscript refers to in
Section IX -- "WC-01 and RC-05 handling are exercised in the machine-readable
artifact's deliberately seeded validation rows" -- and the payload-mutation and
post-retirement checks of Sections VI-F and VIII.
"""

from __future__ import annotations

import argparse
import copy
import inspect
import json
import os

from experiments.common import (
    REPO_ROOT,
    add_common_args,
    load_case_bundle,
    read_json,
    write_csv,
    write_result,
)
from experiments import adversarial_cases


def _apply(entry, documents, keyring):
    mutate = entry["mutate"]
    if "keyring" in inspect.signature(mutate).parameters:
        return mutate(documents, keyring=keyring)
    return mutate(documents)


#: Which loaded document is signed under which signature domain, and which
#: ``compile_parameters.signing_authorities`` key names its legitimate signer.
SIGNED_DOCUMENTS = (
    ("assessment", "assessment", "assessment"),
    ("control_derivation_catalog", "catalog", "catalog"),
    ("cstar_profile", "cstar_profile", "cstar_profile"),
    ("invariant_register", "invariants", "invariants"),
    ("judgment_record", "judgment_record", "judgment_record"),
    ("dispositions", "dispositions", "dispositions"),
    ("approved_control_specifications", "acs", "acs"),
)


def resign_all(documents, keyring, signing_authorities):
    """Re-sign every mutated governance artifact with its legitimate authority.

    Without this, every mutation would be rejected at Phi step 1 as a broken
    signature, masking the constraint each case exists to exercise.  Re-signing
    models the realistic failure the manuscript's constraints are written
    against: a governance forum that validly signs a structurally defective
    artifact.
    """
    for document_key, domain, authority_key in SIGNED_DOCUMENTS:
        document = documents.get(document_key)
        if document is None or "signature" not in document:
            continue
        body = {k: v for k, v in document.items() if k != "signature"}
        document["signature"] = keyring.sign(
            body,
            signing_authorities[authority_key],
            domain=domain,
            signing_time=document["signature"].get("signing_time"),
        )
    return documents


def _expected_codes(entry):
    code = entry["expected_code"]
    if code is None:
        return []
    if isinstance(code, str):
        return [code]
    return list(code)


def _validate_all_schemas(documents):
    """Phi step 1's ``validate_all_schemas()``.  Returns the error code or None."""
    from gcir.models import GcirError
    from gcir.validation import validate_document

    checks = [
        ("assessment", "assessment.schema.json"),
        ("control_derivation_catalog", "control_derivation_catalog.schema.json"),
        ("cstar_profile", "cstar_profile.schema.json"),
        ("invariant_register", "invariant_register.schema.json"),
        ("judgment_record", "judgment_record.schema.json"),
        ("dispositions", "dispositions.schema.json"),
        ("approved_control_specifications", "acs.schema.json"),
    ]
    try:
        for key, schema_name in checks:
            validate_document(documents[key], schema_name, label=key)
        for contract in documents["threshold_contracts"]["contracts"].values():
            validate_document(contract, "threshold_contract.schema.json",
                              label=contract["contract_id"])
    except GcirError as exc:
        return exc.code, str(exc)[:400]
    return None, ""


def run_corpus():
    """Run every registered case through both defence layers.

    Both the schema layer and the cross-field-constraint layer are exercised, and
    both outcomes are recorded, because which one catches a given defect first is
    an implementation detail rather than a claim.  A case passes when the defect
    is caught, by either layer, with one of its expected codes.
    """
    from gcir.caseio import build_compiler_inputs, load_case
    from gcir.compiler import compile_bundle
    from gcir.models import GcirError
    from gcir.validation import validate_document

    rows = []
    for entry in adversarial_cases.all_cases():
        case_id = entry["target_case"]
        case = load_case(case_id, validate=False)
        documents = copy.deepcopy(case.documents)
        authorities = case.parameters["signing_authorities"]

        try:
            documents = _apply(entry, documents, case.keyring)
            if entry.get("resign", True):
                resign_all(documents, case.keyring, authorities)
        except Exception as exc:  # a mutation that cannot apply is a corpus bug
            rows.append(
                {
                    "id": entry["id"], "name": entry["name"], "target_case": case_id,
                    "expects": entry["expects"],
                    "expected_code": "|".join(_expected_codes(entry)),
                    "schema_code": "", "compiler_code": "",
                    "actual_code": "MUTATION_FAILED", "outcome": "ERROR",
                    "detail": "%s: %s" % (type(exc).__name__, exc),
                    "manuscript_ref": entry["manuscript_ref"],
                }
            )
            continue

        schema_code, schema_detail = _validate_all_schemas(documents)

        compiler_code = None
        compiler_detail = ""
        warning_codes = []
        compiled = False
        try:
            result = compile_bundle(build_compiler_inputs(documents, case.keyring))
            validate_document(result.bundle.payload, "bundle.schema.json", "bundle")
            for record in result.bundle.predicates:
                validate_document(record, "gcir.schema.json", record["gcir_id"])
            warning_codes = sorted({w["warning_code"] for w in result.warnings})
            compiled = True
            compiler_detail = "compiled; hash=%s; warnings=%s" % (
                result.bundle.payload_hash[:16], warning_codes or "none"
            )
        except GcirError as exc:
            compiler_code = exc.code
            compiler_detail = str(exc)[:400]
        except Exception as exc:
            compiler_code = "UNEXPECTED_%s" % type(exc).__name__
            compiler_detail = "%s: %s" % (type(exc).__name__, str(exc)[:360])

        observed = [c for c in (schema_code, compiler_code) if c] + warning_codes
        expected = _expected_codes(entry)
        rejected = bool(schema_code) or bool(compiler_code)

        if entry["expects"] == "compile":
            if rejected:
                outcome = "FAIL"
            elif expected and not any(c in observed for c in expected):
                outcome = "CODE_MISMATCH"
            else:
                outcome = "PASS"
        else:
            if not rejected:
                outcome = "FAIL"
            elif not any(c in observed for c in expected):
                outcome = "CODE_MISMATCH"
            else:
                outcome = "PASS"

        rows.append(
            {
                "id": entry["id"], "name": entry["name"], "target_case": case_id,
                "expects": entry["expects"],
                "expected_code": "|".join(expected),
                "schema_code": schema_code or "",
                "compiler_code": compiler_code or "",
                "actual_code": "|".join(observed) or "none",
                "outcome": outcome,
                "detail": (schema_detail + " || " + compiler_detail).strip(" |"),
                "manuscript_ref": entry["manuscript_ref"],
            }
        )
    return rows


def run_structural_checks():
    """Payload mutation, post-retirement use, and the runtime acceptance condition."""
    from gcir.canonicalization import hash_payload
    from gcir.lifecycle import LifecycleRegistry, payload_is_unmutated, valid_at
    from gcir.models import SignatureError
    from gcir.signatures import strip_envelope
    from gcir.validation import check_runtime_acceptance

    checks = []
    for case_id in ("case_a", "case_b"):
        case, inputs, result = load_case_bundle(case_id)
        bundle = result.bundle
        keyring = case.keyring
        parameters = case.parameters
        envelope = keyring.sign(bundle.payload, parameters["bundle_signing_key"],
                                domain="bundle", signing_time="2026-02-02T09:05:00Z")

        lifecycle_dir = os.path.join(REPO_ROOT, "cases", case_id, "lifecycle")
        registry_doc = read_json(os.path.join(lifecycle_dir, "lifecycle_registry.json"))
        registry = LifecycleRegistry(
            registry_doc, keyring=keyring,
            authorized_key_ids=registry_doc["authorized_signing_keys"],
        )
        receipts = read_json(os.path.join(lifecycle_dir, "receipts.json"))["receipts"]
        negatives = read_json(os.path.join(lifecycle_dir, "negative", "fixtures.json"))

        # 1. In-place payload mutation must break the hash check.
        mutated = copy.deepcopy(bundle.payload)
        mutated["predicates"][0]["gate_type"] = "advisory"
        checks.append({
            "case": case_id, "check": "in_place_payload_mutation_breaks_hash",
            "manuscript_ref": "Section VI-F; Appendix A constraint 13",
            "passed": hash_payload(mutated) != bundle.payload_hash,
            "detail": "mutated hash %s vs original %s"
                      % (hash_payload(mutated)[:16], bundle.payload_hash[:16]),
        })

        # 2. Mutation must also break the signature.
        signature_broken = False
        try:
            keyring.verify(mutated, envelope, domain="bundle")
        except SignatureError:
            signature_broken = True
        checks.append({
            "case": case_id, "check": "in_place_payload_mutation_breaks_signature",
            "manuscript_ref": "Section VI-F",
            "passed": signature_broken, "detail": "",
        })

        # 3. Adding a lifecycle field to the payload must be rejected outright.
        from gcir.models import ValidationError
        from gcir.validation import constraint_13_payload_is_hash_clean
        polluted = copy.deepcopy(bundle.payload)
        polluted["retired_at"] = "2026-06-01T00:00:00Z"
        rejected = False
        try:
            constraint_13_payload_is_hash_clean(polluted)
        except ValidationError:
            rejected = True
        checks.append({
            "case": case_id, "check": "lifecycle_field_inside_payload_rejected",
            "manuscript_ref": "Section V; Appendix A constraint 13",
            "passed": rejected, "detail": "",
        })

        # 4. A receipt taken BEFORE retirement stays valid (not drift).
        historical = next(r for r in receipts if r["receipt_id"].endswith("-002"))
        ok, reasons = valid_at(historical, bundle, registry, keyring=keyring)
        checks.append({
            "case": case_id, "check": "pre_retirement_receipt_remains_valid",
            "manuscript_ref": "Section VIII",
            "passed": ok,
            "detail": "; ".join(reasons),
        })

        # 5. A receipt taken AFTER registry-effective retirement is invalid.
        post = negatives["q4_post_retirement_receipt"]
        ok_post, reasons_post = valid_at(post, bundle, registry, keyring=keyring)
        checks.append({
            "case": case_id, "check": "post_retirement_receipt_is_invalid",
            "manuscript_ref": "Section VIII",
            "passed": (not ok_post) and any("retired" in r for r in reasons_post),
            "detail": "; ".join(reasons_post),
        })

        # 6. A receipt citing the wrong bundle hash is invalid.
        wrong = negatives["q4_wrong_bundle_hash_receipt"]
        ok_wrong, reasons_wrong = valid_at(wrong, bundle, registry, keyring=keyring)
        checks.append({
            "case": case_id, "check": "wrong_bundle_hash_receipt_is_invalid",
            "manuscript_ref": "Section VIII",
            "passed": (not ok_wrong) and any("bundle_hash" in r for r in reasons_wrong),
            "detail": "; ".join(reasons_wrong),
        })

        # 7. A registry record signed outside authorized_signing_keys does not retire.
        rogue_doc = copy.deepcopy(registry_doc)
        rogue_doc["entries"] = [negatives["q6_unauthorized_registry_entry"]]
        rogue_registry = LifecycleRegistry(
            rogue_doc, keyring=keyring,
            authorized_key_ids=rogue_doc["authorized_signing_keys"],
        )
        checks.append({
            "case": case_id, "check": "unauthorized_registry_record_does_not_retire",
            "manuscript_ref": "Section VI-F; Section VIII query 6",
            "passed": (not rogue_registry.is_retired(bundle.payload_hash,
                                                     "2026-12-01T00:00:00Z"))
                      and len(rogue_registry.invalid_authority_entries()) == 1,
            "detail": json.dumps(rogue_registry.invalid_authority_entries()),
        })

        # 8. Conflicting mandatory policies with no unique precedence relation
        #    resolve to SAFE_STATE as indeterminate (Section VI-D). This is an
        #    evaluation-time property, not a compile-time rejection, so it is
        #    checked here rather than in the mutation corpus.
        from gcir.models import CompiledBundle
        from gcir.precedence import resolve

        conflicted = copy.deepcopy(bundle.payload)
        mandatory_ids = [p["gcir_id"] for p in conflicted["predicates"]
                         if p["gate_type"] == "mandatory"][:2]
        for predicate in conflicted["predicates"]:
            if predicate["gcir_id"] in mandatory_ids:
                predicate["conflict_group"] = "CG-DISPUTED"
        conflicted_bundle = CompiledBundle(payload=conflicted, payload_hash="n/a")
        outcomes = {p["gcir_id"]: "pass" for p in conflicted["predicates"]}
        outcomes[mandatory_ids[0]] = "fail"
        verdict = resolve(conflicted_bundle, outcomes)
        checks.append({
            "case": case_id, "check": "conflicting_mandatory_policies_are_indeterminate",
            "manuscript_ref": "Section VI-D",
            "passed": (verdict["decision"] == "SAFE_STATE"
                       and verdict["deciding_class"] == "indeterminate_mandatory_conflict"),
            "detail": verdict["reason"],
        })

        conflicted["policy_metadata"]["precedence"] = {
            "CG-DISPUTED": {"order": mandatory_ids}
        }
        verdict = resolve(conflicted_bundle, outcomes)
        checks.append({
            "case": case_id,
            "check": "unique_precedence_relation_resolves_the_conflict",
            "manuscript_ref": "Section VI-D",
            "passed": (verdict["decision"] == "SAFE_STATE"
                       and verdict["deciding_class"] == "mandatory_failure"),
            "detail": verdict["reason"],
        })

        # 9. A weighted or advisory failure never overrides a mandatory pass.
        clean_bundle = CompiledBundle(payload=bundle.payload, payload_hash=bundle.payload_hash)
        soft_outcomes = {p["gcir_id"]: "pass" for p in bundle.predicates}
        soft_ids = [p["gcir_id"] for p in bundle.predicates if p["gate_type"] != "mandatory"]
        for gid in soft_ids:
            soft_outcomes[gid] = "fail"
        verdict = resolve(clean_bundle, soft_outcomes)
        checks.append({
            "case": case_id, "check": "soft_failure_never_overrides_mandatory_pass",
            "manuscript_ref": "Section VI-D",
            "passed": verdict["decision"] == "PERMIT",
            "detail": "%d weighted/advisory failures; decision=%s"
                      % (len(soft_ids), verdict["decision"]),
        })

        # 10. Runtime acceptance condition: policy from another channel is refused.
        clean_receipt = receipts[0]
        conformant = {
            "loads_only_signed_phi_bundles": True,
            "alternate_policy_channels": [],
            "emits_requirement_reference": True,
        }
        ok_rt, problems_rt = check_runtime_acceptance(conformant, clean_receipt, bundle)
        checks.append({
            "case": case_id, "check": "conformant_runtime_accepted",
            "manuscript_ref": "Appendix A constraint 14",
            "passed": ok_rt, "detail": "; ".join(problems_rt),
        })

        injected = copy.deepcopy(clean_receipt)
        injected["evaluated_predicates"].append({
            "gcir_id": "GCIR-INJECTED-FROM-ANOTHER-CHANNEL",
            "acs_id": None,
            "origin": {"origin_type": "risk_derived", "origin_id": "R-99"},
            "outcome": "pass",
        })
        nonconformant = {
            "loads_only_signed_phi_bundles": True,
            "alternate_policy_channels": ["operator_console_policy_upload"],
            "emits_requirement_reference": True,
        }
        ok_inj, problems_inj = check_runtime_acceptance(nonconformant, injected, bundle)
        checks.append({
            "case": case_id, "check": "policy_injected_outside_bundle_detected",
            "manuscript_ref": "Section VI-F; Appendix A constraint 14",
            "passed": (not ok_inj) and len(problems_inj) >= 2,
            "detail": "; ".join(problems_inj),
        })

    return checks


def run_validation_seeds():
    """The deliberately seeded rows exercising WC-01 and RC-05 (Section IX)."""
    from gcir.caseio import build_compiler_inputs, load_case
    from gcir.compiler import compile_bundle
    from gcir.models import GcirError

    seeds = []

    # VS-01: RC-05 -- consequence class undefined, routed to a NON-RUNTIME
    # disposition with reason code RC-05. Compiles; the row is honestly routed.
    case = load_case("case_a", validate=False)
    documents = copy.deepcopy(case.documents)
    documents["assessment"]["risk_register"].append({
        "risk_id": "R-VS-01",
        "cause": "a novel interaction pattern the enterprise taxonomy does not yet describe",
        "event": "the interaction produces an effect whose consequence kind the approved taxonomy does not name",
        "consequence": "the effect cannot be classified under the approved consequence taxonomy",
        "affected_parties": ["the dealer as regulated entity"],
        "obligation_refs": ["INT-RES-QA"],
        "existing_controls": ["ad hoc escalation to the governance forum"],
        "owner": "business.research_operations",
        "hazardous_action_paths": [],
        "source_register_row": "seeded validation row",
    })
    documents["assessment"]["risk_analysis"].append({
        "risk_id": "R-VS-01",
        "likelihood_inherent": 2, "impact_inherent": 3,
        "control_effectiveness": "ineffective",
        "likelihood_residual": 2, "impact_residual": 3,
        "consequence_class": "undefined",
        "tier": "tier_3", "treatment": "mitigate", "reopening_trigger": None,
    })
    documents["dispositions"]["records"].append({
        "risk_id": "R-VS-01", "status": "nonruntime", "reason_code": "RC-05",
        "routed_to_control_family": "governance_process",
        "control_ref": "CTL-A-TAXONOMY-01 (consequence-taxonomy extension request)",
        "owner": "business.research_operations",
        "approval": {"approver": "forum.chair_l_tremblay",
                     "approval_time": "2026-01-20T14:00:00Z",
                     "forum": "ai_governance_forum"},
    })
    resign_all(documents, case.keyring, case.parameters["signing_authorities"])
    try:
        result = compile_bundle(build_compiler_inputs(documents, case.keyring))
        seeds.append({
            "seed_id": "VS-01", "code_exercised": "RC-05",
            "manuscript_ref": "Section V; Section IX",
            "expected": "compiles with the row routed to a non-runtime disposition carrying RC-05",
            "outcome": "PASS",
            "detail": "hash=%s; RC-05 record present=%s" % (
                result.bundle.payload_hash[:16],
                any(r.get("reason_code") == "RC-05" for r in result.bundle.dispositions),
            ),
        })
    except GcirError as exc:
        seeds.append({
            "seed_id": "VS-01", "code_exercised": "RC-05",
            "manuscript_ref": "Section V; Section IX",
            "expected": "compiles with RC-05 disposition",
            "outcome": "FAIL", "detail": str(exc)[:300],
        })

    # VS-02: WC-01 -- unresolved obligation reference raises a WARNING and the
    # bundle still compiles. It is not simultaneously a success and a rejection.
    case = load_case("case_a", validate=False)
    documents = copy.deepcopy(case.documents)
    documents["approved_control_specifications"]["records"][0]["obligation_refs"].append(
        "OBLIGATION-WITHDRAWN-2026"
    )
    resign_all(documents, case.keyring, case.parameters["signing_authorities"])
    try:
        result = compile_bundle(build_compiler_inputs(documents, case.keyring))
        codes = sorted({w["warning_code"] for w in result.warnings})
        seeds.append({
            "seed_id": "VS-02", "code_exercised": "WC-01",
            "manuscript_ref": "Section V; Appendix A constraint 8; Section IX",
            "expected": "compiles AND raises warning WC-01 (a warning, not a disposition)",
            "outcome": "PASS" if codes == ["WC-01"] else "FAIL",
            "detail": "warnings=%s; %s" % (
                codes, json.dumps(result.warnings[:2])
            ),
        })
    except GcirError as exc:
        seeds.append({
            "seed_id": "VS-02", "code_exercised": "WC-01",
            "manuscript_ref": "Section V; Section IX",
            "expected": "compiles with WC-01 warning",
            "outcome": "FAIL", "detail": str(exc)[:300],
        })

    # VS-03: RC-02 -- no authority-matrix action, routed to a non-runtime row.
    case = load_case("case_a", validate=False)
    documents = copy.deepcopy(case.documents)
    documents["assessment"]["risk_register"].append({
        "risk_id": "R-VS-03",
        "cause": "the desired control would have to constrain an action the system is not authorized to take at all",
        "event": "the enterprise wishes to gate an action absent from S.authority_matrix",
        "consequence": "no predicate can be emitted because no authorized action exists to gate",
        "affected_parties": ["the dealer as regulated entity"],
        "obligation_refs": ["INT-NO-TRADE-CONN"],
        "existing_controls": ["network segmentation"],
        "owner": "technology.applied_ai_platform",
        "hazardous_action_paths": [],
        "source_register_row": "seeded validation row",
    })
    documents["assessment"]["risk_analysis"].append({
        "risk_id": "R-VS-03",
        "likelihood_inherent": 2, "impact_inherent": 4,
        "control_effectiveness": "effective",
        "likelihood_residual": 1, "impact_residual": 4,
        "consequence_class": "authority",
        "tier": "tier_3", "treatment": "mitigate", "reopening_trigger": None,
    })
    documents["dispositions"]["records"].append({
        "risk_id": "R-VS-03", "status": "nonruntime", "reason_code": "RC-02",
        "routed_to_control_family": "architectural",
        "control_ref": "CTL-A-SEGMENT-01 (network segmentation; the action remains outside the matrix)",
        "owner": "technology.applied_ai_platform",
        "approval": {"approver": "forum.chair_l_tremblay",
                     "approval_time": "2026-01-20T14:00:00Z",
                     "forum": "ai_governance_forum"},
    })
    resign_all(documents, case.keyring, case.parameters["signing_authorities"])
    try:
        result = compile_bundle(build_compiler_inputs(documents, case.keyring))
        seeds.append({
            "seed_id": "VS-03", "code_exercised": "RC-02",
            "manuscript_ref": "Section V",
            "expected": "compiles with the row routed to a non-runtime disposition carrying RC-02",
            "outcome": "PASS" if any(r.get("reason_code") == "RC-02"
                                     for r in result.bundle.dispositions) else "FAIL",
            "detail": "hash=%s" % result.bundle.payload_hash[:16],
        })
    except GcirError as exc:
        seeds.append({
            "seed_id": "VS-03", "code_exercised": "RC-02",
            "manuscript_ref": "Section V",
            "expected": "compiles with RC-02 disposition",
            "outcome": "FAIL", "detail": str(exc)[:300],
        })

    return seeds


def run(final):
    rows = run_corpus()
    checks = run_structural_checks()
    seeds = run_validation_seeds()

    negative = [r for r in rows if r["expects"] == "reject"]
    positive = [r for r in rows if r["expects"] == "compile"]

    summary = {
        "corpus": {
            "total": len(rows),
            "negative_cases": len(negative),
            "positive_controls": len(positive),
            "passed": sum(1 for r in rows if r["outcome"] == "PASS"),
            "failed": sum(1 for r in rows if r["outcome"] == "FAIL"),
            "code_mismatch": sum(1 for r in rows if r["outcome"] == "CODE_MISMATCH"),
            "errors": sum(1 for r in rows if r["outcome"] == "ERROR"),
            "rows": rows,
        },
        "structural_checks": {
            "total": len(checks),
            "passed": sum(1 for c in checks if c["passed"]),
            "failed": sum(1 for c in checks if not c["passed"]),
            "checks": checks,
        },
        "validation_seeds": {
            "total": len(seeds),
            "passed": sum(1 for s in seeds if s["outcome"] == "PASS"),
            "seeds": seeds,
        },
        "note": "A case rejected with the WRONG error code is recorded as "
                "CODE_MISMATCH, not counted as a pass: rejecting for an unrelated "
                "reason is not evidence that the intended constraint works.",
    }

    write_result(final, "adversarial", summary)
    write_csv(final, "adversarial_cases.csv",
              ["id", "name", "target_case", "expects", "expected_code",
               "schema_code", "compiler_code", "actual_code", "outcome",
               "manuscript_ref", "detail"], rows)

    print("adversarial corpus: %d cases (%d negative, %d positive control) -- "
          "%d PASS, %d FAIL, %d CODE_MISMATCH, %d ERROR"
          % (len(rows), len(negative), len(positive),
             summary["corpus"]["passed"], summary["corpus"]["failed"],
             summary["corpus"]["code_mismatch"], summary["corpus"]["errors"]))
    print("structural checks: %d/%d passed"
          % (summary["structural_checks"]["passed"], len(checks)))
    print("validation seeds: %d/%d passed"
          % (summary["validation_seeds"]["passed"], len(seeds)))
    for row in rows:
        if row["outcome"] != "PASS":
            print("  %s %-8s %-52s expected=%s actual=%s"
                  % (row["outcome"], row["id"], row["name"][:52],
                     row["expected_code"], row["actual_code"]))
    for check in checks:
        if not check["passed"]:
            print("  FAILED CHECK %s/%s: %s" % (check["case"], check["check"], check["detail"]))
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args(argv)
    summary = run(args.final)
    ok = (
        summary["corpus"]["failed"] == 0
        and summary["corpus"]["code_mismatch"] == 0
        and summary["corpus"]["errors"] == 0
        and summary["structural_checks"]["failed"] == 0
        and summary["validation_seeds"]["passed"] == summary["validation_seeds"]["total"]
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
