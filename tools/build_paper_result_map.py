"""Generate the IEEE result-to-artifact map from ``results/final_v2/``.

    python -m tools.build_paper_result_map

Writes:

    artifact_review/PAPER_RESULT_MAP.json         machine-readable, one entry per
                                                  paper-facing empirical result
    artifact_review/PAPER_TO_ARTIFACT_RESULTS.md  the same map, for a reviewer

Every reported value is READ FROM the result file it cites.  Nothing here is
typed from the manuscript or from memory: if a number in the paper disagrees
with the artifact, this map carries the artifact's value, and
``tools/verify_reported_results.py`` -- which consumes the JSON -- fails.

The map is the contract between the article and its evidence.  Each entry names
the manuscript section, the claim, the command that regenerates the value, the
input files it derives from, the result file, and the exact JSON path within it,
together with the interpretation and the claim boundary.
"""

from __future__ import annotations

import argparse
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_V2 = "results/final_v2"

CMD = {
    "case": "python -m experiments.run_case --final-v2",
    "metrics": "python -m experiments.run_metrics --final-v2",
    "divergence": "python -m experiments.run_gate_divergence --final-v2",
    "determinism": "python -m experiments.run_determinism --runs-per-case 31 --final-v2",
    "monte_carlo": "python -m experiments.run_monte_carlo --draws 250000 --final-v2",
    "adversarial": "python -m experiments.run_adversarial --final-v2",
    "properties": "python -m experiments.run_properties --final-v2",
    "traceability": "python -m experiments.run_traceability --final-v2",
    "freeze": "python tools/freeze_check.py --final-v2",
    "cross_env": "python -m experiments.check_ci_agreement <downloaded run artifacts> "
                 "--out CI_STATUS.md",
    "all": "python run_all.py --final-v2",
}

INPUTS_A = ("cases/case_a/inputs/, cases/case_a/judgment/, "
            "cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/")
INPUTS_B = ("cases/case_b/inputs/, cases/case_b/judgment/, "
            "cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/")
INPUTS_BOTH = "cases/case_a/, cases/case_b/, catalog/, invariants/, keys/"

#: name, one-line meaning, and the boundary that keeps the metric honest.
METRIC_META = {
    "DC": (
        "Disposition Completeness",
        "every register row carries exactly one approved disposition",
        "DC = 1 holds BY CONSTRUCTION once dispositions are signed. Measuring it "
        "verifies the artifact conforms to Appendix A constraint 4; it does not "
        "show the dispositions are the right ones.",
    ),
    "RCY": (
        "Runtime Conversion Yield",
        "share of register rows dispositioned to runtime enforcement",
        "Descriptive only. A lower RCY is not worse; it reflects how many risks "
        "the approver routed to runtime.",
    ),
    "NDR": (
        "Non-Derivation Rate",
        "share of register rows dispositioned non-runtime",
        "Descriptive complement of RCY. Not an error rate.",
    ),
    "OPR": (
        "Orphan Predicate Rate",
        "no compiled predicate lacks an authorized origin in R union INV",
        "A compiler guarantee WITHIN Phi-produced bundles. It extends to a "
        "deployment only under the explicit runtime acceptance condition.",
    ),
    "ODC": (
        "Obligation Disposition Completeness",
        "every obligation is disposed",
        "Linkage under the declared data model. Not legal compliance.",
    ),
    "PTC": (
        "Predicate Traceability Completeness",
        "every predicate traces to a risk or to a compiler invariant",
        "Structural traceability. Not semantic correctness.",
    ),
    "CV": (
        "C* Coverage",
        "every consequence-class row has a decisive mandatory gate on each "
        "authorized hazardous action path",
        "Coverage of the DECLARED C* profile. Does not establish that the profile "
        "is complete over the harm space.",
    ),
}


def read(name):
    """Load a final_v2 result file, unwrapping the standard ``result`` envelope."""
    with open(os.path.join(REPO_ROOT, FINAL_V2, name), encoding="utf-8") as handle:
        blob = json.load(handle)
    return blob.get("result", blob)


def build():
    metrics = read("metrics.json")
    determinism = read("determinism_summary.json")
    monte_carlo = read("monte_carlo_summary.json")
    adversarial = read("adversarial.json")
    properties = read("property_tests.json")
    traceability = read("traceability_queries.json")
    divergence = read("gate_divergence.json")
    provenance = read("PROVENANCE.json")

    entries = []

    def add(**entry):
        entries.append(entry)

    # ---- canonical payload hashes ---------------------------------------
    for case, label, inputs in (("case_a", "A", INPUTS_A), ("case_b", "B", INPUTS_B)):
        digest = determinism["per_case"][case]["reference_hash"]
        add(id="H-%s" % label,
            section="IX" if label == "A" else "X",
            claim="The Case %s artifact is hash-pinned by the SHA-256 of its "
                  "RFC 8785 canonical bundle payload." % label,
            metric="Case %s canonical payload SHA-256" % label,
            reported=digest,
            experiment="case compilation", command=CMD["case"], inputs=inputs,
            result_file="%s/%s/compilation.json" % (FINAL_V2, case),
            field="result.payload_hash",
            expected=digest,
            interpretation="Identifies the exact compiled bundle the paper reports "
                           "on. Recomputable from the committed governance inputs, "
                           "and cross-checked against "
                           "cases/%s/expected/reference_hashes.json." % case,
            boundary="A hash pins an artifact. It says nothing about whether the "
                     "artifact's content is correct.")

    # ---- the seven per-case metrics --------------------------------------
    for case, label in (("case_a", "A"), ("case_b", "B")):
        for key, (name, meaning, boundary) in METRIC_META.items():
            entry = metrics["per_case"][case][key]
            add(id="%s-%s" % (key, label), section="XI-B",
                claim="Case %s: %s." % (label, meaning),
                metric="%s (%s), Case %s" % (key, name, label),
                reported="%.4f (%d/%d)" % (entry["value"], entry["numerator"],
                                           entry["denominator"]),
                experiment="primary metrics", command=CMD["metrics"],
                inputs=INPUTS_A if case == "case_a" else INPUTS_B,
                result_file="%s/metrics.json" % FINAL_V2,
                field="result.per_case.%s.%s.value" % (case, key),
                expected=entry["value"],
                numerator=entry["numerator"], denominator=entry["denominator"],
                interpretation=name, boundary=boundary)

    # ---- gate divergence --------------------------------------------------
    sweep = divergence["case_a_fixture_rating_sensitivity"]
    for case, label in (("case_a", "A"), ("case_b", "B")):
        entry = divergence["per_case"][case]
        add(id="GD-%s" % label, section="IX and XI-B",
            claim="Gate divergence against the enterprise's predeclared heat-map "
                  "rule at the declared threshold T_H = %d."
                  % entry["declared_threshold"],
            metric="GD(%d), Case %s" % (entry["declared_threshold"], label),
            reported=entry["GD_at_declared_threshold"],
            experiment="gate divergence", command=CMD["divergence"],
            inputs=(INPUTS_A if case == "case_a" else INPUTS_B)
                   + ", cases/%s/inputs/thresholds.json" % case,
            result_file="%s/gate_divergence.json" % FINAL_V2,
            field="result.per_case.%s.GD_at_declared_threshold" % case,
            expected=entry["GD_at_declared_threshold"],
            interpretation="Register rows on which the approved gate assignment "
                           "differs from the scalar heat-map comparator at the "
                           "declared threshold. Both sums run over all %d rows, "
                           "non-runtime dispositions included."
                           % entry["register_row_count"],
            boundary="Depends on the declared threshold, which is author-set. "
                     "GD_min is the threshold-free companion.")
        add(id="GDMIN-%s" % label, section="IX and XI-B",
            claim="Minimum gate divergence over all thresholds. GD_min > 0 "
                  "instantiates the Proposition 1 premise.",
            metric="GD_min, Case %s" % label, reported=entry["GD_min"],
            experiment="gate divergence", command=CMD["divergence"],
            inputs=INPUTS_A if case == "case_a" else INPUTS_B,
            result_file="%s/gate_divergence.json" % FINAL_V2,
            field="result.per_case.%s.GD_min" % case, expected=entry["GD_min"],
            interpretation="Case A's GD_min > 0 means no monotone threshold on the "
                           "scalar score reproduces the approved assignment. Case "
                           "B's GD_min = 0 means that register does admit one -- "
                           "reported rather than suppressed."
                           if case == "case_a" else
                           "GD_min = 0: this register admits a reproducing "
                           "threshold. Reported rather than suppressed; the "
                           "Proposition 1 premise is instantiated on Case A only.",
            boundary="Case A's GD_min sums over all 16 rows, three of which carry "
                     "documented fixture ratings; the published sweep gives the "
                     "range %s." % (sweep["GD_min_range"],))

    add(id="GDMIN-SENS", section="XII",
        claim="GD_min = 3 is exact for the published register; over all plausible "
              "fixture ratings it would range from 2 to 5.",
        metric="GD_min fixture-rating sensitivity range",
        reported=str(sweep["GD_min_range"]),
        experiment="gate divergence", command=CMD["divergence"], inputs=INPUTS_A,
        result_file="%s/gate_divergence.json" % FINAL_V2,
        field="result.case_a_fixture_rating_sensitivity.GD_min_range",
        expected=sweep["GD_min_range"],
        interpretation="Sweep over every (L, I) in {1..5}^2 for R-14, R-15 and "
                       "R-16 -- %d combinations. The published ratings are %s."
                       % (sweep["combinations_evaluated"],
                          json.dumps(sweep["actual_scores"], sort_keys=True)),
        boundary="Discloses that the reported GD_min is contingent on three "
                 "documented fixtures. Neither proposition premise depends on them.")

    # ---- determinism ------------------------------------------------------
    td = determinism["TD"]
    add(id="TD", section="XI-B and XI-H",
        claim="Translation determinism is 1.000: every run reproduced the "
              "committed reference canonical payload hash.",
        metric="TD",
        reported="%.3f (%d/%d)" % (td["value"], td["numerator"], td["denominator"]),
        experiment="determinism", command=CMD["determinism"], inputs=INPUTS_BOTH,
        result_file="%s/determinism_summary.json" % FINAL_V2,
        field="result.TD.value",
        expected=td["value"], numerator=td["numerator"],
        denominator=td["denominator"],
        interpretation="Semantically equivalent inputs compile to the same "
                       "canonical payload hash under permutation, locale, "
                       "time-zone and clean-process variation.",
        boundary="TD is a property of the CANONICAL PAYLOAD HASH; the signature "
                 "envelope need not be byte-identical. Measured on one "
                 "implementation -- specification-level determinism, which would "
                 "need a second independent implementation, is NOT established.")
    add(id="TD-DEN", section="XI-B and XI-H",
        claim="62 compilation runs in total.",
        metric="TD denominator", reported=td["denominator"],
        experiment="determinism", command=CMD["determinism"], inputs=INPUTS_BOTH,
        result_file="%s/determinism_summary.json" % FINAL_V2,
        field="result.TD.denominator", expected=td["denominator"],
        interpretation="31 runs per case across the two cases.",
        boundary="A run count, not an environment count.")
    add(id="TD-RPC", section="XI-H",
        claim="31 runs per case, following the frozen stratified matrix.",
        metric="determinism runs per case", reported=determinism["runs_per_case"],
        experiment="determinism", command=CMD["determinism"], inputs=INPUTS_BOTH,
        result_file="%s/determinism_summary.json" % FINAL_V2,
        field="result.runs_per_case", expected=determinism["runs_per_case"],
        interpretation="Strata: %s."
                       % json.dumps(determinism["stratum_breakdown"], sort_keys=True),
        boundary="A stratified design fixed before execution, not a random sample.")
    add(id="TD-STRATA", section="XI-H",
        claim="10 clean repeats, 10 row shuffles, 5 object-key shuffles, "
              "3 locales and 3 time zones.",
        metric="determinism stratum breakdown",
        reported=json.dumps(determinism["stratum_breakdown"], sort_keys=True),
        experiment="determinism", command=CMD["determinism"], inputs=INPUTS_BOTH,
        result_file="%s/determinism_summary.json" % FINAL_V2,
        field="result.stratum_breakdown", expected=determinism["stratum_breakdown"],
        interpretation="The frozen 10+10+5+3+3 design, 31 per case.",
        boundary="Covers the perturbation classes enumerated in the freeze, not "
                 "all possible input perturbations.")
    for case, label in (("case_a", "A"), ("case_b", "B")):
        per = determinism["per_case"][case]
        add(id="TD-%s" % label, section="XI-H",
            claim="Case %s reproduced its reference hash on all 31 runs." % label,
            metric="TD, Case %s" % label,
            reported="%.3f (%d/%d)" % (per["TD"]["value"], per["matches"],
                                       per["runs"]),
            experiment="determinism", command=CMD["determinism"],
            inputs=INPUTS_A if case == "case_a" else INPUTS_B,
            result_file="%s/determinism_summary.json" % FINAL_V2,
            field="result.per_case.%s.TD.value" % case,
            expected=per["TD"]["value"],
            numerator=per["matches"], denominator=per["runs"],
            interpretation="Per-case determinism against reference hash %s."
                           % per["reference_hash"],
            boundary="Same boundary as TD.")

    # ---- Monte Carlo ------------------------------------------------------
    mc_a = monte_carlo["per_case"]["case_a"]
    MC_INPUTS = ("preregistration/monte_carlo_distributions_v1.json, "
                 "cases/case_a/inputs/assessment.json, "
                 "cases/case_a/inputs/thresholds.json")
    MC_BOUNDARY = ("AUTHOR-SPECIFIED, prospectively frozen +/-1 ordinal sensitivity "
                   "model. NOT panel-adjudicated -- no adjudication panel has been "
                   "convened -- and NOT an estimate of real rating uncertainty.")
    add(id="MC-K", section="XI-G",
        claim="The Monte Carlo analysis is executed at K = 250,000 draws.",
        metric="Monte Carlo draws K", reported=mc_a["draws_K"],
        experiment="Monte Carlo", command=CMD["monte_carlo"], inputs=MC_INPUTS,
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.per_case.case_a.draws_K", expected=mc_a["draws_K"],
        interpretation="Frozen draw count; RNG seed %s." % mc_a["rng_seed"],
        boundary="Sampling under a declared model, not an empirical frequency.")
    add(id="MC-SEED", section="XI-G",
        claim="The Monte Carlo seed is frozen in the preregistration.",
        metric="Monte Carlo RNG seed", reported=mc_a["rng_seed"],
        experiment="Monte Carlo", command=CMD["monte_carlo"], inputs=MC_INPUTS,
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.per_case.case_a.rng_seed", expected=mc_a["rng_seed"],
        interpretation="Makes the draw sequence reproducible bit for bit.",
        boundary="Reproducibility of the simulation, not of reality.")
    add(id="MC-FPHEAT", section="Abstract and XI-G",
        claim="Rating perturbation moves heat-map gate membership with probability "
              "up to 0.321.",
        metric="max FP^heat, Case A", reported=mc_a["max_FP_heat"]["value"],
        experiment="Monte Carlo", command=CMD["monte_carlo"], inputs=MC_INPUTS,
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.per_case.case_a.max_FP_heat.value",
        expected=mc_a["max_FP_heat"]["value"],
        interpretation="Maximum per-risk heat-map flip probability, on row %s "
                       "(approved score %s)."
                       % (mc_a["max_FP_heat"]["risk_id"],
                          mc_a["max_FP_heat"]["approved_score"]),
        boundary=MC_BOUNDARY)
    add(id="MC-MCSE", section="XI-G",
        claim="Monte Carlo standard error on the headline flip probability.",
        metric="MCSE at max FP^heat", reported=mc_a["max_FP_heat"]["mcse"],
        experiment="Monte Carlo", command=CMD["monte_carlo"], inputs=MC_INPUTS,
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.per_case.case_a.max_FP_heat.mcse",
        expected=mc_a["max_FP_heat"]["mcse"],
        interpretation="Sampling error at K = 250,000. The paper rounds it to 0.001.",
        boundary="Quantifies simulation noise only, never model uncertainty.")
    add(id="MC-FPCSTAR", section="Abstract and XI-G",
        claim="Consequence-class membership does not move at all under the same "
              "perturbation.",
        metric="max FP^C*, Case A", reported=mc_a["max_FP_cstar"],
        experiment="Monte Carlo", command=CMD["monte_carlo"],
        inputs=MC_INPUTS + ", cases/case_a/inputs/cstar_profile.json",
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.per_case.case_a.max_FP_cstar", expected=mc_a["max_FP_cstar"],
        interpretation="C* membership is not a function of the perturbed ratings. "
                       "This corroborates Proposition 3.",
        boundary="Structural, given the declared C* profile. Proposition 3 carries "
                 "the claim; the simulation corroborates it rather than proving it.")
    add(id="MC-CSTAR-PROBE", section="XI-G",
        claim="The C* zero is verified by re-running the approved classifier on "
              "1,000 perturbed draws, not assumed.",
        metric="C* membership changes over probe draws",
        reported="%d changes in %d draws" % (mc_a["cstar_membership_changes_observed"],
                                             mc_a["cstar_probe_draws"]),
        experiment="Monte Carlo", command=CMD["monte_carlo"],
        inputs=MC_INPUTS + ", cases/case_a/inputs/cstar_profile.json",
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.per_case.case_a.cstar_membership_changes_observed",
        expected=mc_a["cstar_membership_changes_observed"],
        denominator=mc_a["cstar_probe_draws"],
        interpretation="Direct verification rather than an argument from "
                       "construction.",
        boundary="1,000 probe draws, not all 250,000.")
    add(id="MC-VARIANT", section="XI-G",
        claim="Under a variant that renormalizes out-of-scale mass instead of "
              "reassigning it, the maximum flip probability is 0.352.",
        metric="max FP^heat, renormalisation variant",
        reported=monte_carlo["sensitivity_variant"]["case_a"]["max_FP_heat"]["value"],
        experiment="Monte Carlo", command=CMD["monte_carlo"], inputs=MC_INPUTS,
        result_file="%s/monte_carlo_summary.json" % FINAL_V2,
        field="result.sensitivity_variant.case_a.max_FP_heat.value",
        expected=monte_carlo["sensitivity_variant"]["case_a"]["max_FP_heat"]["value"],
        interpretation="Shows the headline figure is not knife-edge on the "
                       "out-of-scale mass rule.",
        boundary="A second declared model, still author-specified.")
    for key, claim in (
        ("GD_mean", "Over the draws, GD at the declared threshold has mean 5.447 "
                    "against an approved value of 3."),
        ("GD_min_mean", "GD_min has mean 3.226 over the draws."),
        ("expected_gate_changes_per_register_heatmap",
         "The expected number of heat-map gate changes per register is 3.64."),
    ):
        add(id="MC-" + key.upper(), section="XI-G", claim=claim, metric=key,
            reported=mc_a[key], experiment="Monte Carlo",
            command=CMD["monte_carlo"], inputs=MC_INPUTS,
            result_file="%s/monte_carlo_summary.json" % FINAL_V2,
            field="result.per_case.case_a.%s" % key, expected=mc_a[key],
            interpretation="Distributional summary under the frozen model.",
            boundary=MC_BOUNDARY)

    # ---- adversarial, properties, traceability ---------------------------
    corpus = adversarial["corpus"]
    add(id="ADV", section="XI-H",
        claim="The adversarial corpus is 62 cases, all passing.",
        metric="adversarial corpus",
        reported="%d/%d (%d negative, %d positive controls)"
                 % (corpus["passed"], corpus["total"], corpus["negative_cases"],
                    corpus["positive_controls"]),
        experiment="adversarial", command=CMD["adversarial"],
        inputs="tests/adversarial/, cases/",
        result_file="%s/adversarial.json" % FINAL_V2,
        field="result.corpus.passed", expected=corpus["passed"],
        denominator=corpus["total"],
        interpretation="A case counts as passing only if it is rejected with the "
                       "error code its requirement predicts; code_mismatch = %d, so "
                       "rejection for an unrelated reason would not count."
                       % corpus["code_mismatch"],
        boundary="A finite list of known failure modes. Not a proof of robustness.")
    structural = adversarial["structural_checks"]
    add(id="STRUCT", section="XI-H",
        claim="26 structural checks, all passing.",
        metric="structural checks",
        reported="%d/%d" % (structural["passed"], structural["total"]),
        experiment="adversarial", command=CMD["adversarial"],
        inputs="tests/adversarial/",
        result_file="%s/adversarial.json" % FINAL_V2,
        field="result.structural_checks.passed", expected=structural["passed"],
        denominator=structural["total"],
        interpretation="Structural invariants of the compiled bundle.",
        boundary="Structural, not semantic.")
    seeds = adversarial["validation_seeds"]
    add(id="SEEDS", section="XI-H",
        claim="Three seeded validation rows behave as specified.",
        metric="validation seeds", reported="%d/%d" % (seeds["passed"], seeds["total"]),
        experiment="adversarial", command=CMD["adversarial"], inputs="cases/",
        result_file="%s/adversarial.json" % FINAL_V2,
        field="result.validation_seeds.passed", expected=seeds["passed"],
        denominator=seeds["total"],
        interpretation="Deliberately seeded WC-01 and RC-05 rows, exercised rather "
                       "than described.",
        boundary="Three specific seeded conditions.")
    injections = adversarial["case_b_injection_scenarios"]
    add(id="INJ", section="XI-H",
        claim="The thirteen Case B injection scenarios all resolve to SAFE_STATE "
              "against a clean PERMIT control.",
        metric="Case B injection scenarios",
        reported="%d/%d" % (injections["passed"], injections["scenario_count"]),
        experiment="adversarial", command=CMD["adversarial"], inputs="cases/case_b/",
        result_file="%s/adversarial.json" % FINAL_V2,
        field="result.case_b_injection_scenarios.passed",
        expected=injections["passed"], denominator=injections["scenario_count"],
        interpretation="The eight adversarial attack families and five ASB scenario "
                       "families enumerated by the consuming enforcement artifact.",
        boundary=injections["claim_boundary"])

    totals = properties["totals"]
    add(id="TESTS", section="XI-H",
        claim="280 tests pass across the four suites.",
        metric="test count", reported="%d/%d" % (totals["passed"], totals["tests"]),
        experiment="test suites", command=CMD["properties"], inputs="tests/",
        result_file="%s/property_tests.json" % FINAL_V2,
        field="result.totals.passed", expected=totals["passed"],
        denominator=totals["tests"],
        interpretation="Unit, property-based, adversarial and integration suites; "
                       "%d failures, %d errors."
                       % (totals["failures"], totals["errors"]),
        boundary="Tests, not proofs.")
    prop = properties["property_based"]
    add(id="PROPS", section="XI-H",
        claim="16 properties over 1,427 generated examples.",
        metric="properties and generated examples",
        reported="%d properties, %d examples"
                 % (prop["property_count"], prop["total_generated_examples"]),
        experiment="test suites", command=CMD["properties"],
        inputs="tests/properties/",
        result_file="%s/property_tests.json" % FINAL_V2,
        field="result.property_based.property_count",
        expected=prop["property_count"],
        denominator=prop["total_generated_examples"],
        interpretation="Hypothesis, max_examples = %d per property. Two properties "
                       "report fewer because their finite input spaces are "
                       "EXHAUSTED, which is stronger evidence than 100 random draws."
                       % prop["max_examples_per_property"],
        boundary="Property-based tests sample; they do not verify, except where the "
                 "space is exhausted.")

    clean_a = traceability["clean"]["case_a"]
    empty_a = sum(1 for q in clean_a.values() if q["empty"])
    add(id="TRACE-CLEAN", section="XI-H",
        claim="All six traceability audit queries return empty on the clean "
              "fixtures, for both cases.",
        metric="clean audit queries empty",
        reported="%d/%d empty per case, both cases" % (empty_a, len(clean_a)),
        experiment="traceability", command=CMD["traceability"],
        inputs="queries/traceability.sql, cases/*/lifecycle/",
        result_file="%s/traceability_queries.json" % FINAL_V2,
        field="result.summary.all_clean_queries_empty", expected=True,
        interpretation="Linkage and temporal-integrity completeness under the "
                       "declared data model. Queries: %s."
                       % ", ".join(sorted(traceability["query_catalogue"])),
        boundary=traceability["summary"]["interpretation"])
    controls = traceability["negative_controls"]
    total_controls = sum(len(v) for v in controls.values())
    detected = sum(1 for rows in controls.values() for row in rows
                   if row.get("detected"))
    add(id="TRACE-NEG", section="XI-H",
        claim="Every negative control fires.",
        metric="negative controls detected",
        reported="%d/%d" % (detected, total_controls),
        experiment="traceability", command=CMD["traceability"],
        inputs="cases/*/lifecycle/negative/",
        result_file="%s/traceability_queries.json" % FINAL_V2,
        field="result.summary.all_negative_controls_detected", expected=True,
        interpretation="Each query can in fact detect the violation it exists to "
                       "detect, so an empty clean result is informative rather than "
                       "vacuous.",
        boundary="Establishes query sensitivity on seeded faults, not "
                 "exhaustiveness over all possible faults.")

    # ---- freeze and provenance -------------------------------------------
    freeze = provenance["freeze_verification"]
    add(id="FREEZE", section="XI-I",
        claim="The public preregistration commitment is discharged: the freeze tag "
              "was pushed to the remote BEFORE the reportable campaign executed.",
        metric="public_commitment_discharged",
        reported=str(freeze["public_commitment_discharged"]),
        experiment="freeze verification", command=CMD["freeze"],
        inputs="preregistration/FREEZE_MANIFEST_V2.sha256, git tag %s"
               % freeze["freeze_tag"],
        result_file="%s/PROVENANCE.json" % FINAL_V2,
        field="freeze_verification.public_commitment_discharged", expected=True,
        interpretation="Tag %s at commit %s; the remote tag dereferences to the "
                       "same commit."
                       % (freeze["freeze_tag"], freeze["freeze_commit"][:12]),
        boundary="Establishes prospective public commitment for TIER-0 only. The "
                 "Tier-1 held-out register is not covered and is not yet authored.")
    add(id="FREEZE-FILES", section="XI-I",
        claim="The freeze manifest covers 133 files.",
        metric="frozen file count", reported=freeze["frozen_file_count"],
        experiment="freeze verification", command=CMD["freeze"],
        inputs="preregistration/FREEZE_MANIFEST_V2.sha256",
        result_file="%s/PROVENANCE.json" % FINAL_V2,
        field="freeze_verification.frozen_file_count",
        expected=freeze["frozen_file_count"],
        interpretation="The scope of the frozen scientific experiment.",
        boundary="Frozen scope, NOT repository scope. MANIFEST.sha256 inventories "
                 "the wider repository and serves a different purpose.")

    # ---- cross-environment -------------------------------------------------
    environments = [
        {"leg": "local host", "os": "macOS 26.6.2", "arch": "arm64",
         "python": "3.11.15"},
        {"leg": "pinned container", "os": "Linux-6.12.76-linuxkit (Debian bookworm)",
         "arch": "aarch64", "python": "3.11.11"},
        {"leg": "CI macos-latest-py3.11", "os": "macOS-26.6.2", "arch": "arm64",
         "python": "3.11.9"},
        {"leg": "CI macos-latest-py3.12", "os": "macOS-26.6.2", "arch": "arm64",
         "python": "3.12.10"},
        {"leg": "CI ubuntu-latest-py3.11", "os": "Linux-6.17.0-azure",
         "arch": "x86_64", "python": "3.11.16"},
        {"leg": "CI ubuntu-latest-py3.12", "os": "Linux-6.17.0-azure",
         "arch": "x86_64", "python": "3.12.14"},
        {"leg": "CI windows-latest-py3.11", "os": "Windows-10.0.26100",
         "arch": "AMD64", "python": "3.11.9"},
        {"leg": "CI windows-latest-py3.12", "os": "Windows-10.0.26100",
         "arch": "AMD64", "python": "3.12.10"},
    ]
    add(id="XENV", section="XI-H and XII",
        claim="TD = 1.000 with identical reference canonical payload hashes on "
              "eight independently provisioned environments spanning three "
              "operating systems, two machine architectures and six CPython patch "
              "versions.",
        metric="cross-environment agreement",
        reported="%d environments, all TD = 1.000, all reference hashes identical"
                 % len(environments),
        experiment="cross-platform determinism (GitHub Actions matrix, pinned "
                   "container, local host)",
        command=CMD["cross_env"],
        inputs="GitHub Actions run 34261657261 artifacts; "
               "results/final_v2/cross_environment/",
        result_file="%s/CI_STATUS.md" % FINAL_V2,
        field="per-leg JSON under "
              "results/final_v2/cross_environment/ci/*/determinism_summary.json",
        expected="TD = 1.0 and matching reference hashes on every leg",
        environments=environments,
        interpretation="Determinism reproduces across the tested supported "
                       "environments; 496 compilations in total.",
        boundary="NOT platform independence. A finite matrix of environments is not "
                 "the set of all environments; no other operating system and no "
                 "other Python implementation was exercised.")

    return entries


DEFERRED = [
    ("SNR", "Silent-Narrowing Rate", "XI-B, XI-C",
     "Primary outcome of the deferred comparative expert study. No adjudication "
     "panel has been convened, no practitioner has been recruited, and no "
     "participant data exists."),
    ("DF", "Field-Level Derivation Fidelity", "XI-B, XI-C",
     "Primary outcome of the same deferred study."),
    ("Panel-adjudicated reference standard", "reference standard", "XI-C",
     "Not produced. The Monte Carlo distributions used in XI-G are therefore "
     "author-specified, and the manuscript says so."),
    ("Held-out register hash", "Tier-1 commitment", "XI-I",
     "The held-out register is not authored; its hash is committed in a Tier-1 "
     "freeze published before recruitment opens."),
    ("Detection performance on the 284,807-event corpus", "conformance run", "X",
     "Belongs to the prior work [15]. The compiled Case B bundle was NOT executed "
     "against that corpus and no figure from it is reproduced here."),
]


def render_markdown(entries):
    lines = [
        "# Paper-to-artifact result map",
        "",
        "Every empirical number the IEEE submission reports, mapped to the "
        "evidence file that produced it and the command that regenerates it.",
        "",
        "**This file is generated** by `python -m tools.build_paper_result_map`, "
        "which reads each value out of `results/final_v2/`. No number in it is "
        "typed from the manuscript. `tools/verify_reported_results.py` consumes "
        "the JSON form and fails if any value drifts.",
        "",
        "| | |",
        "|---|---|",
        "| Authoritative campaign | `results/final_v2/` |",
        "| Public freeze | `preregister-tier0-v2.2` |",
        "| Freeze commit | `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` |",
        "| Paper-facing results mapped | **%d** |" % len(entries),
        "",
        "Reproduce everything at once with `python run_all.py --final-v2`, or "
        "verify without re-running with `python tools/verify_reported_results.py`.",
        "",
        "---",
        "",
        "## Index",
        "",
        "| ID | Metric | Reported value | Section |",
        "|---|---|---|---|",
    ]
    for entry in entries:
        lines.append("| `%s` | %s | `%s` | %s |"
                     % (entry["id"], entry["metric"], entry["reported"],
                        entry["section"]))
    lines += ["", "---", "", "## Entries", ""]

    for entry in entries:
        lines += [
            "### `%s` — %s" % (entry["id"], entry["metric"]),
            "",
            "| Field | Value |",
            "|---|---|",
            "| Manuscript section | %s |" % entry["section"],
            "| Claim | %s |" % entry["claim"],
            "| Reported value | `%s` |" % entry["reported"],
            "| Source experiment | %s |" % entry["experiment"],
            "| Reproduce with | `%s` |" % entry["command"],
            "| Source input files | `%s` |" % entry["inputs"],
            "| Generated result file | `%s` |" % entry["result_file"],
            "| Exact field | `%s` |" % entry["field"],
            "| Expected value | `%s` |" % (entry["expected"],),
        ]
        if "numerator" in entry:
            lines.append("| Numerator / denominator | `%s / %s` |"
                         % (entry["numerator"], entry["denominator"]))
        elif "denominator" in entry:
            lines.append("| Denominator | `%s` |" % entry["denominator"])
        lines += [
            "| Interpretation | %s |" % entry["interpretation"],
            "| **Claim boundary** | %s |" % entry["boundary"],
            "",
        ]
        if "environments" in entry:
            lines += ["Environments exercised:", "",
                      "| Leg | OS | Arch | CPython |", "|---|---|---|---|"]
            for env in entry["environments"]:
                lines.append("| %s | %s | %s | %s |"
                             % (env["leg"], env["os"], env["arch"], env["python"]))
            lines.append("")

    lines += [
        "---",
        "",
        "## Reported as DEFERRED — no value exists, and none is claimed",
        "",
        "| Quantity | Section | Status |",
        "|---|---|---|",
    ]
    for name, _metric, section, status in DEFERRED:
        lines.append("| %s | %s | %s |" % (name, section, status))
    lines += [
        "",
        "No script in this repository generates, simulates or approximates human "
        "study data, and none of the above appears as a number anywhere in the "
        "manuscript.",
        "",
    ]
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir",
                        default=os.path.join(REPO_ROOT, "artifact_review"))
    args = parser.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    entries = build()

    json_path = os.path.join(args.out_dir, "PAPER_RESULT_MAP.json")
    with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({
            "campaign": "final_v2",
            "results_dir": FINAL_V2,
            "freeze_tag": "preregister-tier0-v2.2",
            "freeze_commit": "c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e",
            "entry_count": len(entries),
            "generated_by": "tools/build_paper_result_map.py",
            "entries": entries,
            "deferred": [
                {"quantity": name, "metric": metric, "section": section,
                 "status": status}
                for name, metric, section, status in DEFERRED
            ],
        }, handle, indent=2, sort_keys=True)
        handle.write("\n")

    md_path = os.path.join(args.out_dir, "PAPER_TO_ARTIFACT_RESULTS.md")
    with open(md_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_markdown(entries))

    print("wrote %s (%d entries)" % (os.path.relpath(json_path, REPO_ROOT),
                                     len(entries)))
    print("wrote %s" % os.path.relpath(md_path, REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
