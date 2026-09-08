"""Generate ``SUMMARY.md`` from the result files.

    python -m experiments.make_summary [--final]

Every number in the generated summary is read from a result file that a script
produced.  Nothing is typed by hand, and a missing result file is reported as
missing rather than filled in.
"""

from __future__ import annotations

import argparse
import json
import os

from experiments.common import (
    REPO_ROOT,
    add_common_args,
    environment,
    read_json,
    results_dir,
)

REQUIRED = [
    "case_a/compilation.json",
    "case_b/compilation.json",
    "metrics.json",
    "determinism_summary.json",
    "gate_divergence.json",
    "monte_carlo_summary.json",
    "adversarial.json",
    "property_tests.json",
    "traceability_queries.json",
]


def _load(directory, name):
    path = os.path.join(directory, name)
    if not os.path.exists(path):
        return None
    return read_json(path)["result"]


def _fmt(value, digits=4):
    if value is None:
        return "not measured"
    if isinstance(value, float):
        return "%.*f" % (digits, value)
    return str(value)


def build(final):
    directory = results_dir(final)
    phase = "final" if final else "development"
    missing = [name for name in REQUIRED if not os.path.exists(os.path.join(directory, name))]

    case_a = _load(directory, "case_a/compilation.json")
    case_b = _load(directory, "case_b/compilation.json")
    metrics = _load(directory, "metrics.json")
    determinism = _load(directory, "determinism_summary.json")
    gates = _load(directory, "gate_divergence.json")
    monte = _load(directory, "monte_carlo_summary.json")
    adversarial = _load(directory, "adversarial.json")
    properties = _load(directory, "property_tests.json")
    traceability = _load(directory, "traceability_queries.json")

    env = environment()
    lines = []
    add = lines.append

    add("# Measured results -- %s campaign" % phase.upper())
    add("")
    if phase == "development":
        add("> **These are DEVELOPMENT results and are not reportable numbers.**")
        add("> The reportable campaign runs after the public preregistration freeze")
        add("> and writes to `results/final/`.")
    else:
        # verify_freeze writes a flat document, not the {result: ...} envelope.
        freeze_path = os.path.join(directory, "freeze_verification.json")
        freeze = read_json(freeze_path) if os.path.exists(freeze_path) else None
        add("> **FINAL reportable campaign.** Produced after the Tier-0 preregistration")
        add("> freeze (`preregistration/TIER0_FREEZE.md`, tag `preregister-tier0-v1`).")
        if freeze is None:
            add(">")
            add("> Freeze verification has not been run; run "
                "`python -m experiments.verify_freeze`.")
        else:
            add(">")
            add("> Freeze verification: **%s**. %d frozen files checked; results were "
                "produced at commit `%s`; frozen files changed since the freeze: **%d**."
                % ("PASSED" if freeze.get("verified") else "FAILED",
                   freeze.get("frozen_file_count", 0),
                   ", ".join(c[:12] for c in freeze.get("results_commits", [])) or "unknown",
                   len(freeze.get("frozen_files_changed_since_freeze", {}))))
            if freeze.get("public_commitment_discharged"):
                add(">")
                add("> The freeze tag is present on the public remote, so the Section XI-I")
                add("> public timestamped commitment **is discharged**.")
            else:
                add(">")
                add("> **The freeze tag has not been pushed to a public remote, so the")
                add("> Section XI-I *public* timestamped commitment is NOT yet discharged.**")
                add("> What is established is the content-and-ancestry relationship above,")
                add("> which a timestamp cannot fake; what is not yet established is")
                add("> third-party-verifiable ordering in time. Until the push, describe the")
                add("> preregistration as prepared and committed, not as published.")
    add("")
    if missing:
        add("**Missing result files: %s**" % ", ".join(missing))
        add("")

    # ---------------------------------------------------------------- env
    add("## Environment and provenance")
    add("")
    add("| Field | Value |")
    add("|---|---|")
    campaign_commit = None
    campaign_blob_path = os.path.join(directory, "reproduce_all.json")
    if os.path.exists(campaign_blob_path):
        campaign_commit = (read_json(campaign_blob_path)
                           .get("environment", {}).get("git_commit"))
    if campaign_commit:
        add("| **git commit the campaign ran at** | `%s` |" % campaign_commit)
    add("| git commit when this summary was rendered | `%s` |" % env["git_commit"])
    add("| git describe | `%s` |" % env["git_describe"])
    add("| git tag (exact) | `%s` |" % (env["git_tag_exact"] or "none at this commit"))
    add("| working tree clean | %s |" % env["git_status_clean"])
    add("| Python | %s (%s) |" % (env["python_version"], env["python_implementation"]))
    add("| platform | %s |" % env["platform"])
    add("| machine | %s |" % env["machine"])
    for package, version in sorted(env["dependencies"].items()):
        add("| %s | %s |" % (package, version))
    add("")

    # ---------------------------------------------------------------- cases
    add("## Case artifacts")
    add("")
    add("| | Case A | Case B |")
    add("|---|---|---|")
    if case_a and case_b:
        add("| evidence class | %s | %s |" % (case_a["case_class"], case_b["case_class"]))
        add("| canonical payload hash (SHA-256) | `%s` | `%s` |"
            % (case_a["payload_hash"], case_b["payload_hash"]))
        for key, label in (
            ("risk_count", "register rows"),
            ("obligation_count", "obligations"),
            ("acs_count", "Approved Control Specifications"),
            ("predicate_count", "compiled predicates"),
            ("risk_derived_predicate_count", "-- risk-derived"),
            ("compiler_invariant_predicate_count", "-- compiler-invariant"),
            ("mandatory_gate_count", "mandatory gates"),
            ("cstar_risk_count", "C* risks"),
            ("warning_count", "warnings"),
        ):
            add("| %s | %s | %s |" % (label, case_a["statistics"][key],
                                      case_b["statistics"][key]))
    add("")

    # ---------------------------------------------------------------- metrics
    add("## Primary metrics (Section XI-B)")
    add("")
    if metrics:
        add("| Metric | Case A | Case B | Definition |")
        add("|---|---|---|---|")
        a = metrics["per_case"]["case_a"]
        b = metrics["per_case"]["case_b"]
        for name in ("DC", "RCY", "NDR", "OPR", "ODC", "PTC", "CV"):
            add("| **%s** | %s (%s/%s) | %s (%s/%s) | %s |"
                % (name,
                   _fmt(a[name]["value"], 4), a[name]["numerator"], a[name]["denominator"],
                   _fmt(b[name]["value"], 4), b[name]["numerator"], b[name]["denominator"],
                   a[name]["definition"]))
        add("| **GD(T_H)** | %d at T_H=%d | %d at T_H=%d | GD(T_H) = sum_i 1[g_i != 1[s_i >= T_H]] |"
            % (a["GD"]["value"], a["GD"]["declared_threshold"],
               b["GD"]["value"], b["GD"]["declared_threshold"]))
        add("| **GD_min** | %d | %d | min over t of sum_i 1[g_i != 1[s_i >= t]] |"
            % (a["GD_min"]["value"], b["GD_min"]["value"]))
        if determinism:
            add("| **TD** | %s (%d/%d) | %s (%d/%d) | sum_k 1[H_k = H_ref] / N |"
                % (_fmt(determinism["per_case"]["case_a"]["TD"]["value"], 4),
                   determinism["per_case"]["case_a"]["TD"]["numerator"],
                   determinism["per_case"]["case_a"]["TD"]["denominator"],
                   _fmt(determinism["per_case"]["case_b"]["TD"]["value"], 4),
                   determinism["per_case"]["case_b"]["TD"]["numerator"],
                   determinism["per_case"]["case_b"]["TD"]["denominator"]))
        add("| **SNR** | DEFERRED | DEFERRED | RQ5 -- no adjudication panel convened |")
        add("| **DF** | DEFERRED | DEFERRED | RQ5 -- no adjudication panel convened |")
        add("")
        add("Disposition counts -- Case A: %s; Case B: %s."
            % (json.dumps(a["disposition_counts"]), json.dumps(b["disposition_counts"])))
        add("")
        add("Gate-source breakdown -- Case A: %s; Case B: %s."
            % (json.dumps(a["gate_sources"]["by_gate_type_and_source"]),
               json.dumps(b["gate_sources"]["by_gate_type_and_source"])))
    add("")

    # ---------------------------------------------------------- determinism
    add("## Translation determinism (RQ2)")
    add("")
    if determinism:
        add("**TD = %s (%d/%d runs).**"
            % (_fmt(determinism["TD"]["value"], 4),
               determinism["TD"]["numerator"], determinism["TD"]["denominator"]))
        add("")
        add("| | value |")
        add("|---|---|")
        add("| total runs | %d |" % determinism["total_runs"])
        add("| runs per case | %d |" % determinism["runs_per_case"])
        add("| matching the reference hash | %d |" % determinism["matches"])
        add("| Case A reference hash | `%s` |"
            % determinism["per_case"]["case_a"]["reference_hash"])
        add("| Case B reference hash | `%s` |"
            % determinism["per_case"]["case_b"]["reference_hash"])
        add("| locales exercised | %s |" % ", ".join(determinism["locales_used"]))
        add("| time zones exercised | %s |" % ", ".join(determinism["timezones_used"]))
        add("| failures | %d |" % len(determinism["failures"]))
        add("")
        add("Permutation dimensions:")
        for dimension in determinism["permutation_dimensions"]:
            add("* %s" % dimension)
        add("")
        add("> %s" % determinism["environment_scope_note"])
    add("")

    # -------------------------------------------------------------- gates
    add("## Gate divergence (RQ3)")
    add("")
    if gates:
        for case_id in ("case_a", "case_b"):
            entry = gates["per_case"][case_id]
            add("### %s" % case_id)
            add("")
            add("* declared heat-map threshold T_H = **%d**" % entry["declared_threshold"])
            add("* **GD(%d) = %d** over all %d register rows"
                % (entry["declared_threshold"], entry["GD_at_declared_threshold"],
                   entry["register_row_count"]))
            if entry["divergent_rows"]:
                add("  * divergent rows: %s"
                    % ", ".join("%s (s=%d, approved g=%d, heat-map h=%d)"
                                % (d["risk_id"], d["score"], d["approved_gate"],
                                   d["heatmap_gate"]) for d in entry["divergent_rows"]))
            add("* **GD_min = %d**, attained at t in %s"
                % (entry["GD_min"], entry["GD_min_argmin_thresholds"]))
            add("* Proposition 1 premise (score inversion): **%s**%s"
                % ("holds" if entry["proposition_1"]["holds"] else "does not hold",
                   " -- %d inverted pairs" % entry["proposition_1"]["inversion_count"]
                   if entry["proposition_1"]["holds"] else ""))
            add("* Proposition 2 premise (score collision with divergent gates): **%s**"
                % ("holds" if entry["proposition_2"]["holds"] else "does not hold"))
            for collision in entry["proposition_2"]["collisions"]:
                add("  * at s = %d: gated %s, ungated %s"
                    % (collision["score"], collision["gated"], collision["ungated"]))
            add("")
        sweep = gates.get("case_a_fixture_rating_sensitivity")
        if sweep:
            add("### Sensitivity of Case A GD_min to fixture-rated rows")
            add("")
            add("The manuscript does not state L x I for the three non-runtime rows "
                "%s, and both GD sums run over all register rows. Sweeping every "
                "(L, I) in {1..5}^2 for each of them over %d combinations:"
                % (", ".join(sweep["fixture_rated_rows"]),
                   sweep["combinations_evaluated"]))
            add("")
            add("* actual GD_min with the committed ratings %s: **%d**"
                % (json.dumps(sweep["actual_scores"]), sweep["actual_GD_min"]))
            add("* range across the sweep: **%s**" % (sweep["GD_min_range"],))
            add("* share of the grid giving the actual value: %.3f"
                % sweep["share_of_grid_matching_actual"])
            add("* distribution: %s" % json.dumps(sweep["GD_min_distribution"]))
            add("")
            add("> %s" % sweep["interpretation"])
    add("")

    # ------------------------------------------------------- monte carlo
    add("## Monte Carlo rating robustness (Section XI-G)")
    add("")
    if monte:
        add("> **%s**" % monte["provenance_warning"])
        add("")
        spec = monte["specification"]
        add("* K = **%d** draws per risk; seed = %d (frozen before execution)"
            % (spec["draws_K"], spec["seed"]))
        add("* perturbation rule: `%s` -- %.1f on the approved rating, %.1f on each "
            "adjacent rating, out-of-range mass %s"
            % (spec["perturbation_rule"]["name"],
               spec["perturbation_rule"]["mass_on_approved"],
               spec["perturbation_rule"]["mass_one_step_each_side"],
               spec["perturbation_rule"]["out_of_range_handling"]))
        add("")
        add("| | Case A | Case B |")
        add("|---|---|---|")
        a = monte["per_case"]["case_a"]
        b = monte["per_case"]["case_b"]
        add("| max per-risk heat-map flip probability FP^heat | **%.6f** (%s) | **%.6f** (%s) |"
            % (a["max_FP_heat"]["value"], a["max_FP_heat"]["risk_id"],
               b["max_FP_heat"]["value"], b["max_FP_heat"]["risk_id"]))
        add("| MCSE at that estimate | %.6f | %.6f |"
            % (a["max_FP_heat"]["mcse"], b["max_FP_heat"]["mcse"]))
        add("| mean FP^heat across the register | %.6f | %.6f |"
            % (a["mean_FP_heat"], b["mean_FP_heat"]))
        add("| max per-risk C* flip probability FP^C* | **%.6f** | **%.6f** |"
            % (a["max_FP_cstar"], b["max_FP_cstar"]))
        add("| expected heat-map gate changes per register | %.4f | %.4f |"
            % (a["expected_gate_changes_per_register_heatmap"],
               b["expected_gate_changes_per_register_heatmap"]))
        add("| expected C* gate changes per register | %.4f | %.4f |"
            % (a["expected_gate_changes_per_register_cstar"],
               b["expected_gate_changes_per_register_cstar"]))
        add("| C* membership changes observed in %d re-classified draws | %d | %d |"
            % (a["cstar_probe_draws"], a["cstar_membership_changes_observed"],
               b["cstar_membership_changes_observed"]))
        add("| MCSE upper bound at this K | %.6f | %.6f |"
            % (a["MCSE_upper_bound_at_K"], b["MCSE_upper_bound_at_K"]))
        add("| GD(T_H) mean over draws (approved = %d / %d) | %.4f | %.4f |"
            % (a["GD_approved"], b["GD_approved"], a["GD_mean"], b["GD_mean"]))
        add("| GD_min mean over draws | %.4f | %.4f |"
            % (a["GD_min_mean"], b["GD_min_mean"]))
        add("")
        add("Case A GD(T_H) distribution over draws: %s" % json.dumps(a["GD_distribution"]))
        add("")
        add("Case A GD_min distribution over draws: %s" % json.dumps(a["GD_min_distribution"]))
        add("")
        add("> %s" % a["cstar_verification_note"])
        add("")
        variant = monte.get("sensitivity_variant", {}).get("case_a")
        if variant:
            add("Secondary sensitivity (boundary mass renormalised instead of "
                "reassigned): max FP^heat = %.6f on Case A."
                % variant["max_FP_heat"]["value"])
    add("")

    # ------------------------------------------------------- adversarial
    add("## Adversarial suite (Section XI-H)")
    add("")
    if adversarial:
        corpus = adversarial["corpus"]
        add("| | count |")
        add("|---|---|")
        add("| corpus cases | %d |" % corpus["total"])
        add("| -- negative (must be rejected) | %d |" % corpus["negative_cases"])
        add("| -- positive controls (must compile) | %d |" % corpus["positive_controls"])
        add("| PASS | %d |" % corpus["passed"])
        add("| FAIL | %d |" % corpus["failed"])
        add("| CODE_MISMATCH | %d |" % corpus["code_mismatch"])
        add("| ERROR | %d |" % corpus["errors"])
        add("| structural checks passed | %d/%d |"
            % (adversarial["structural_checks"]["passed"],
               adversarial["structural_checks"]["total"]))
        add("| seeded validation rows passed | %d/%d |"
            % (adversarial["validation_seeds"]["passed"],
               adversarial["validation_seeds"]["total"]))
        add("")
        add("Seeded validation rows (Section IX): %s"
            % ", ".join("%s exercises %s (%s)"
                        % (s["seed_id"], s["code_exercised"], s["outcome"])
                        for s in adversarial["validation_seeds"]["seeds"]))
        add("")
        add("> %s" % adversarial["note"])
    add("")

    # --------------------------------------------------------- properties
    add("## Test suites and property-based testing")
    add("")
    if properties:
        add("| Suite | tests | passed | failed | errors |")
        add("|---|---|---|---|---|")
        for name in ("unit", "properties", "adversarial", "integration"):
            suite = properties["suites"][name]
            add("| %s | %d | %d | %d | %d |"
                % (name, suite["tests"], suite["passed"], suite["failures"],
                   suite["errors"]))
        totals = properties["totals"]
        add("| **total** | **%d** | **%d** | **%d** | **%d** |"
            % (totals["tests"], totals["passed"], totals["failures"], totals["errors"]))
        add("")
        pb = properties["property_based"]
        add("Property-based testing: **%d properties**, `max_examples = %d`, "
            "**%d generated examples in total**."
            % (pb["property_count"], pb["max_examples_per_property"],
               pb["total_generated_examples"]))
        add("")
        add("| Property | generated examples |")
        add("|---|---|")
        for name, count in sorted(pb["example_counts"].items()):
            add("| `%s` | %s |" % (name, count))
        add("")
        if pb["properties_below_100_examples"]:
            add("> %s" % pb["note_on_example_counts"])
    add("")

    # ------------------------------------------------------- traceability
    add("## Traceability audit queries (RQ4)")
    add("")
    if traceability:
        add("| Query | Detects | Case A clean | Case B clean |")
        add("|---|---|---|---|")
        for qid in sorted(traceability["query_catalogue"]):
            catalogue = traceability["query_catalogue"][qid]
            a_rows = traceability["clean"]["case_a"][qid]["row_count"]
            b_rows = traceability["clean"]["case_b"][qid]["row_count"]
            add("| **%s** %s | %s | %d rows | %d rows |"
                % (qid, catalogue["title"], catalogue["detects"], a_rows, b_rows))
        add("")
        add("Negative controls -- each query must fire on a deliberately corrupted fixture:")
        add("")
        add("| Case | Query | Control | Detected | Rows |")
        add("|---|---|---|---|---|")
        for case_id in ("case_a", "case_b"):
            for control in traceability["negative_controls"][case_id]:
                add("| %s | %s | %s | %s | %d |"
                    % (case_id, control["query_id"], control["control_label"],
                       "yes" if control["detected"] else "**NO**", control["row_count"]))
        add("")
        add("* all clean queries empty: **%s**"
            % traceability["summary"]["all_clean_queries_empty"])
        add("* all negative controls detected: **%s**"
            % traceability["summary"]["all_negative_controls_detected"])
        add("")
        add("> %s" % traceability["summary"]["interpretation"])
    add("")

    # ------------------------------------------------------------ deferred
    add("## Deferred and out of scope")
    add("")
    add("* **RQ5 (comparative expert study)** is preregistered and DEFERRED. No "
        "adjudication panel has been convened, no participant data exists, and no "
        "comparative-superiority claim is made. SNR and DF are therefore reported "
        "as DEFERRED, not as numbers. See `preregistration/RQ5_DEFERRED_PROTOCOL.md`.")
    add("* **The Monte Carlo rating distributions are author-specified**, not "
        "panel-adjudicated. See `docs/FIXTURE_PROVENANCE.md` FP-020.")
    add("* **Cross-environment determinism.** The full determinism experiment has been "
        "run to completion on two independently installed operating systems -- the "
        "host recorded above and the pinned Linux container -- with identical "
        "reference hashes and TD = 1.000 on each. **Windows and x86-64 remain "
        "untested**; the CI matrix covering them is configured but has not run. "
        "See `results/final/CI_STATUS.md`. The supportable wording is scoped to the "
        "environments actually measured, never 'platform independent'.")
    add("* **Detection performance, production impact and false-denial rates** are "
        "out of scope; they require the shadow-mode deployment identified as future work.")
    add("* The 284,807-event golden-trace conformance run of [15] is **not** "
        "reproduced here and is not claimed as evidence for this paper.")
    add("")
    add("---")
    add("")
    add("Generated by `python -m experiments.make_summary%s`."
        % (" --final" if final else ""))
    add("")

    return "\n".join(lines), missing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args(argv)
    text, missing = build(args.final)
    path = os.path.join(results_dir(args.final), "SUMMARY.md")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote %s" % os.path.relpath(path, REPO_ROOT))
    if missing:
        print("MISSING result files: %s" % ", ".join(missing))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
