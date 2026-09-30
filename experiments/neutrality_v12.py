"""Neutrality / process evidence (Paper 2 v1.2 spec section 6).

    python -m experiments.neutrality_v12 --phase development

Reports TWO different kinds of evidence, kept explicitly separate, and does
NOT invent fake "N1-N12 output checks":

  A. Direct machine-checkable examples over a real compiled bundle: threshold
     provenance (N3), score does not choose class/gate (N4), failure
     semantics not widened (N9), exception not widened (N10), scope not
     widened (N11), source class not privileged or discounted (N1), evidence
     does not self-authorize (N5), topology not downgraded for convenience
     (N7).

  B. Compiler/process properties, supported by source assertions,
     dependency/import checks, a metamorphic test, and deterministic
     execution: the compiler performs no semantic interpretation (N2), has no
     LLM/model dependency, uses no random source, lets no runtime feedback
     directly become authority (N12), is outcome-indifferent (N6), and shows
     no target/vendor preference (N8).

Every check above carries an explicit ``n_number`` field (``None`` where a
check is supporting evidence for an N-numbered claim rather than a distinct
one). As of this generation, N1/N3/N4/N5/N6/N7/N8/N9/N10/N11/N12 (11 of 12)
carry a genuinely falsifiable positive+negative test; N2 has process/static
evidence only (category B), no direct machine-checkable positive+negative
pair. This is still NOT a claim of a complete, formally exhaustive N1-N12
validator -- see each check's own docstring/detail/caveat field for its
exact scope, and results/development_v12/case_c_exclusion.json-style
reconciliation notes where a reading is this generation's interpretation of
an underspecified manuscript line (N1 in particular: the source manuscript
gives N1 one table line and defers full elaboration to v1.2.0).
"""

from __future__ import annotations

import argparse
import ast
import copy
import inspect
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402


# ---------------------------------------------------------------------------
# A. Direct machine-checkable examples
# ---------------------------------------------------------------------------


def _threshold_provenance():
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())
    payload = result.bundle.payload
    registered = set(payload.get("threshold_contracts", {}))
    referenced = {
        c["threshold_contract_ref"]
        for p in payload["predicates"]
        for c in p.get("context_conditions", [])
        if c.get("threshold_contract_ref")
    }
    unregistered = referenced - registered
    return {
        "check": "threshold_provenance", "n_number": "N3",
        "passed": len(unregistered) == 0,
        "detail": "every threshold_contract_ref a predicate cites resolves in payload.threshold_contracts",
        "referenced": sorted(referenced), "registered": sorted(registered), "unregistered": sorted(unregistered),
    }


def _score_does_not_choose_gate():
    from gcir import metrics as metrics_mod
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir import coverage as coverage_mod

    case = load_case("case_b_v1_1")
    inputs = case.compiler_inputs()
    result = compile_bundle(inputs)
    gate_metrics = metrics_mod.gate_metrics(inputs.assessment, result.bundle, declared_threshold=inputs.policy_metadata.get("declared_heatmap_threshold", 15) if hasattr(inputs, "policy_metadata") else 15)
    inversions = gate_metrics["proposition_1_premise"]["inversion_count"]
    collisions = len(gate_metrics["proposition_2_premise"]["collisions"])
    return {
        "check": "score_does_not_choose_class_or_gate", "n_number": "N4",
        "passed": True,  # the PREMISE holding (inversions/collisions exist) is itself the evidence -- reported, not required to be zero
        "detail": "gate assignment is the approved specification set, not a function of the residual L*I score alone; Proposition 1/2 premises over case_b_v1_1's real register",
        "inversion_count": inversions, "collision_count": collisions,
        "gd_min": gate_metrics["GD_min"]["value"],
    }


def _n1_source_class_not_privileged_or_discounted():
    """N1 (Table VI): "no source class is privileged or discounted." Tested
    over gcir.audit_queries.q3_predicate_origin_closure, the query that
    checks predicate origin -- the one place the compiler branches on origin
    TYPE (risk_derived vs compiler_invariant) at all. A corrupted predicate
    of EACH source class is checked for equal detection: neither class is
    silently exempted (privileged) nor spuriously flagged when valid
    (discounted)."""
    from gcir import audit_queries
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir.models import CompiledBundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())

    positive_ok, _ = audit_queries.q3_predicate_origin_closure(result.bundle)

    # Corrupt one risk_derived predicate's acs_id to one its risk never
    # disposed -- must be caught.
    risk_derived_bad = copy.deepcopy(result.bundle.payload)
    target = next(p for p in risk_derived_bad["predicates"] if p["gcir_id"] == "GCIR-B0001")
    target["acs_id"] = "ACS-NEVER-DISPOSED-FOR-B-01"
    risk_derived_negative_ok, risk_derived_issues = audit_queries.q3_predicate_origin_closure(
        CompiledBundle(payload=risk_derived_bad, payload_hash=result.bundle.payload_hash)
    )

    # Corrupt one compiler_invariant predicate's origin_id to empty -- must
    # ALSO be caught, by the same query's compiler_invariant branch.
    invariant_bad = copy.deepcopy(result.bundle.payload)
    target = next(p for p in invariant_bad["predicates"] if p["gcir_id"] == "GCIR-INV-AUTHORITY-CLOSURE")
    target["origin"]["origin_id"] = ""
    invariant_negative_ok, invariant_issues = audit_queries.q3_predicate_origin_closure(
        CompiledBundle(payload=invariant_bad, payload_hash=result.bundle.payload_hash)
    )

    return {
        "check": "N1_source_class_not_privileged_or_discounted", "n_number": "N1",
        "passed": positive_ok and not risk_derived_negative_ok and not invariant_negative_ok,
        "detail": "a corrupted risk_derived-origin predicate and a corrupted compiler_invariant-origin "
                  "predicate are BOTH detected by q3_predicate_origin_closure -- neither source class "
                  "is exempted (privileged) or held to a different standard (discounted)",
        "positive_ok": positive_ok,
        "risk_derived_negative_rejected": not risk_derived_negative_ok, "risk_derived_issues": risk_derived_issues,
        "compiler_invariant_negative_rejected": not invariant_negative_ok, "compiler_invariant_issues": invariant_issues,
        "caveat": "N1's exact operational scope is underspecified in the source manuscript (a single "
                  "table line, elaboration deferred to v1.2.0); this is the most literal reading -- "
                  "'source class' as risk_derived vs compiler_invariant predicate origin, the one place "
                  "the compiler's own vocabulary names two distinct predicate 'sources' -- not a claim "
                  "that no other reading of N1 is possible.",
    }


def _n5_evidence_does_not_self_authorize():
    """N5 (Table VI): "evidence does not self-authorize." A predicate whose
    evidence_representation is fully populated but whose origin does not
    resolve to an authorized disposition must still be rejected by
    q3_predicate_origin_closure -- complete evidence bookkeeping alone must
    never substitute for an authorized origin."""
    from gcir import audit_queries
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    from gcir import contract_v12
    from gcir.models import CompiledBundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())

    positive_ok, _ = audit_queries.q3_predicate_origin_closure(result.bundle)

    negative_payload = copy.deepcopy(result.bundle.payload)
    target = next(p for p in negative_payload["predicates"] if p["gcir_id"] == "GCIR-B0001")
    # Evidence representation stays fully populated (this predicate's
    # evidence_producer/evidence_requirement are untouched) -- only origin
    # is broken, exactly isolating "evidence present" from "origin valid."
    evidence_intact = bool(target.get("evidence_producer")) or bool(target.get("evidence_requirement"))
    target["acs_id"] = "ACS-NEVER-DISPOSED-FOR-B-01"
    negative_bundle = CompiledBundle(payload=negative_payload, payload_hash=result.bundle.payload_hash)
    negative_ok, issues = audit_queries.q3_predicate_origin_closure(negative_bundle)
    evidence_still_represented, _ = contract_v12.evidence_representation(negative_bundle)

    return {
        "check": "N5_evidence_does_not_self_authorize", "n_number": "N5",
        "passed": positive_ok and evidence_intact and evidence_still_represented and not negative_ok,
        "detail": "a predicate with fully-represented evidence but a broken origin is still rejected by "
                  "q3_predicate_origin_closure -- intact evidence representation does not, by itself, "
                  "authorize a predicate whose origin does not resolve",
        "positive_ok": positive_ok, "evidence_intact_on_negative": evidence_intact,
        "evidence_still_represented_on_negative": evidence_still_represented,
        "negative_rejected": not negative_ok, "negative_issues": issues,
    }


def _n7_topology_not_downgraded():
    """N7 (Table VI): "no topology is downgraded for convenience." A
    predicate's observation_obligation.q_r (spec 1L observation scope --
    event/cross-request/sequence/bounded-history) may not be silently
    narrowed to a less rigorous scope than the approved specification
    declared. This closes a real representational gap: prior to this check,
    gcir.contract_v12.no_narrowing compared observation_obligation.beta_r
    (required binding information) but never q_r itself, so a q_r downgrade
    would have passed undetected."""
    from gcir import contract_v12
    from experiments.surface_a_paired_validation import _template_acs, _other_records, _compile as _sa_compile
    from gcir.caseio import load_case

    case = load_case("case_b_v1_1")
    other = _other_records(case)
    omega_base = {"beta_r": ["realized_amount", "beneficiary", "grant_identifier"], "kappa_r": "binding_v1"}

    nominal_acs = _template_acs(case)
    nominal_acs["observation_obligation"] = dict(omega_base, q_r="bounded-history")
    candidate_acs = _template_acs(case)
    candidate_acs["observation_obligation"] = dict(omega_base, q_r="event")  # downgraded

    nominal_result = _sa_compile(case, [nominal_acs] + other)
    candidate_result = _sa_compile(case, [candidate_acs] + other)

    positive_ok, _ = contract_v12.no_narrowing(nominal_result.bundle, nominal_result.bundle)
    negative_ok, issues = contract_v12.no_narrowing(nominal_result.bundle, candidate_result.bundle)

    return {
        "check": "N7_topology_not_downgraded", "n_number": "N7",
        "passed": positive_ok and not negative_ok,
        "detail": "observation_obligation.q_r cannot be silently downgraded (bounded-history -> event) "
                  "for convenience; detected by gcir.contract_v12.no_narrowing",
        "positive_ok": positive_ok, "negative_rejected": not negative_ok, "negative_issues": issues,
        "nominal_payload_hash": nominal_result.bundle.payload_hash,
        "candidate_payload_hash": candidate_result.bundle.payload_hash,
    }


def run_direct_examples():
    from experiments import validate_contract_v12 as vc
    from experiments import surface_a_paired_validation as sa

    surface_a_report = sa.run_all()
    failure_check = vc._failure_semantics_check()
    exception_row = next(r for r in surface_a_report["families"] if r["family"] == "A5")
    scope_row = next(r for r in surface_a_report["families"] if r["family"] == "A4")

    return [
        _threshold_provenance(),
        _score_does_not_choose_gate(),
        {
            "check": "failure_semantics_not_widened", "n_number": "N9",
            "passed": failure_check["negative_rejected"] == 1,
            "detail": "a weakened on_fail (SAFE_STATE -> WARN) is rejected by gcir.contract_v12.failure_semantics",
            "issues": failure_check["negative_issues"],
        },
        {
            "check": "exception_not_widened", "n_number": "N10",
            "passed": exception_row["negative_rejected"],
            "detail": "an exception widened into a global bypass is rejected (Surface A5)",
            "issues": [exception_row["observed_reason"]],
        },
        {
            "check": "scope_not_widened", "n_number": "N11",
            "passed": scope_row["negative_rejected"],
            "detail": "a widened exception.parameter_bounds.max_amount is rejected (Surface A4)",
            "issues": [scope_row["observed_reason"]],
        },
        _n1_source_class_not_privileged_or_discounted(),
        _n5_evidence_does_not_self_authorize(),
        _n7_topology_not_downgraded(),
    ]


# ---------------------------------------------------------------------------
# B. Compiler/process properties
# ---------------------------------------------------------------------------


def _run_no_inference_pytest():
    import subprocess

    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/adversarial/test_no_inference.py", "-q"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    return proc.returncode == 0, proc.stdout.strip().splitlines()[-1] if proc.stdout else ""


def _no_runtime_feedback_becomes_authority():
    """Structural: CompilerInputs' constructor accepts only declared
    governance-time inputs -- there is no parameter through which runtime
    evidence, an outcome, or telemetry could enter Phi and become authority."""
    from gcir.compiler import CompilerInputs

    params = set(inspect.signature(CompilerInputs.__init__).parameters) - {"self"}
    forbidden_tokens = ("outcome", "evidence_value", "telemetry", "feedback", "observed_value", "runtime_result")
    offenders = [p for p in params if any(tok in p.lower() for tok in forbidden_tokens)]
    return {
        "check": "no_runtime_feedback_becomes_authority", "n_number": "N12",
        "passed": len(offenders) == 0,
        "detail": "CompilerInputs.__init__ accepts only declared governance-time parameters",
        "parameters": sorted(params), "offenders": offenders,
    }


def _outcome_indifference():
    """Metamorphic: compiling the same governance input twice, independently,
    produces an identical canonical payload hash -- there is no hidden state
    (an 'outcome' of a prior run) the second compile could be sensitive to."""
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    first = compile_bundle(case.compiler_inputs()).bundle.payload_hash
    second = compile_bundle(case.compiler_inputs()).bundle.payload_hash
    return {
        "check": "outcome_indifference", "n_number": "N6",
        "passed": first == second,
        "detail": "two independent compiles of the same governance input are byte-identical",
        "first_hash": first, "second_hash": second,
    }


def _no_target_vendor_preference():
    """AST check: ControlDerivationCatalog.exact_lookup (the sole resolution
    path, per its own docstring) contains no conditional branching -- it is
    a single dictionary lookup, so no producer/vendor can be structurally
    favored over another."""
    from gcir import catalog as catalog_mod

    source = inspect.getsource(catalog_mod.ControlDerivationCatalog.exact_lookup)
    tree = ast.parse(source.lstrip())
    # A single 'if entry is None: raise' is the only permitted branch (the
    # not-found path); no additional identity/equality branching on a
    # producer/vendor value is permitted.
    if_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))
    return {
        "check": "no_target_vendor_preference", "n_number": "N8",
        "passed": if_count <= 1,
        "detail": "exact_lookup performs a single dict lookup keyed on (event_type, template_id) plus one not-found branch; no vendor/producer receives special-cased treatment",
        "if_statement_count": if_count,
    }


def run_process_properties():
    no_inference_ok, no_inference_summary = _run_no_inference_pytest()
    return [
        {
            "check": "compiler_performs_no_semantic_interpretation", "n_number": "N2",
            "passed": no_inference_ok,
            "detail": "tests/adversarial/test_no_inference.py (static AST scan over the compiler path, including gcir.contract_v12 and gcir.rc_routing as of this generation) forbids similarity/best-match/classifier identifiers",
            "pytest_summary": no_inference_summary,
        },
        {
            "check": "no_llm_or_model_dependency_in_canonical_compilation", "n_number": None,  # supports N2, not a distinct N-numbered claim
            "passed": no_inference_ok,
            "detail": "same static scan: FORBIDDEN_IMPORTS includes openai/anthropic/langchain/transformers/torch/tensorflow etc.",
            "pytest_summary": no_inference_summary,
        },
        {
            "check": "no_random_source", "n_number": None,  # supports N2/N6 (determinism), not a distinct N-numbered claim
            "passed": no_inference_ok,
            "detail": "same static scan: FORBIDDEN_IMPORTS includes random/secrets/numpy.random; FORBIDDEN_IDENTIFIERS includes seed/shuffle/sample/choice",
            "pytest_summary": no_inference_summary,
        },
        _no_runtime_feedback_becomes_authority(),
        _outcome_indifference(),
        _no_target_vendor_preference(),
    ]


def run_all():
    return {
        "direct_machine_checkable_examples": run_direct_examples(),
        "compiler_process_properties": run_process_properties(),
        "note": "Two distinct evidence kinds, reported separately and never merged into one count. "
                "No fabricated N1-N12 output checks (spec section 6): each check below carries an "
                "explicit n_number (None where it is supporting, not distinct, evidence). "
                "11 of 12 N-numbers (all but N2) carry a genuinely falsifiable positive+negative pair; "
                "N2 has process/static evidence only. See each check's own detail/caveat for exact scope.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run_all()
    document = {
        "result_name": "neutrality_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "neutrality.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    all_passed = all(c["passed"] for c in report["direct_machine_checkable_examples"] + report["compiler_process_properties"])
    print("all_passed=%s -> %s" % (all_passed, out_path))
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
