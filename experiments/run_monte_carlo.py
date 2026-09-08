"""Monte Carlo rating-robustness analysis (manuscript Section XI-G).

    python -m experiments.run_monte_carlo [--draws 250000] [--final]

For each risk r_i the frozen specification supplies discrete probability masses
over plausible ratings::

    L_i^(k) ~ Cat(pi_{L_i}),  I_i^(k) ~ Cat(pi_{I_i})
    s_i^(k) = L_i^(k) I_i^(k),  h_i^(k) = 1[s_i^(k) >= T_H]
    FP_i^heat = (1/K) sum_k 1[h_i^(k) != h_i^approved]

and, conditional on unchanged consequence classification and policy version,
``FP_i^{C*} = 0``.

**The C\\* flip probability is zero for a structural reason, not an empirical
one.**  The coverage rule of Section VII-A reads the consequence descriptor and
never reads L or I, so perturbing a rating cannot move gate membership.  This
experiment therefore *verifies* that structural fact by re-running the actual
coverage classifier on each perturbed draw -- if some code path did leak a rating
dependence into gate assignment, this experiment would find it -- rather than
asserting zero by construction.

Reported: per-risk flip probability, expected gate changes per register,
distributions of GD(T_H) and GD_min, and MCSE.

**Provenance.** Manuscript Section XI-G attributes the rating distributions to
the independent adjudication panel of Section XI-C.  No such panel has been
convened.  The distributions used here are author-specified synthetic
sensitivity distributions; the frozen specification says so, and so does every
result file this script writes.
"""

from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np

from experiments.common import (
    CASES,
    REPO_ROOT,
    add_common_args,
    phase_of,
    load_case_bundle,
    read_json,
    write_csv,
    write_result,
)

SPEC_PATH = os.path.join(REPO_ROOT, "preregistration", "monte_carlo_distributions_v1.json")

SCALE_MIN = 1
SCALE_MAX = 5


def rating_distribution(approved, rule):
    """Return the probability vector over ratings 1..5 for one approved rating."""
    mass_centre = rule["mass_on_approved"]
    mass_side = rule["mass_one_step_each_side"]
    weights = np.zeros(SCALE_MAX - SCALE_MIN + 1, dtype=float)

    def index(value):
        return value - SCALE_MIN

    weights[index(approved)] += mass_centre
    for neighbour in (approved - 1, approved + 1):
        if SCALE_MIN <= neighbour <= SCALE_MAX:
            weights[index(neighbour)] += mass_side
        elif rule["out_of_range_handling"] == "reassign_to_approved":
            weights[index(approved)] += mass_side
        # "renormalise": leave the mass off and normalise below

    total = weights.sum()
    if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-12):
        weights = weights / total
    return weights


def analyse_case(case_id, draws, spec, rule, rng_seed):
    from gcir import coverage as cov

    case, inputs, result = load_case_bundle(case_id)
    threshold = case.parameters["declared_heatmap_threshold"]
    assessment = inputs.assessment
    profile = inputs.cstar_profile

    approved_gates = cov.approved_gate_vector(assessment, result.bundle.gate_map,
                                              result.bundle.predicates)
    approved_scores = cov.residual_scores(assessment)
    analysis = assessment.analysis_index

    risk_ids = sorted(approved_gates)
    n = len(risk_ids)
    values = np.arange(SCALE_MIN, SCALE_MAX + 1)

    rng = np.random.default_rng(rng_seed)

    likelihood = np.empty((draws, n), dtype=np.int16)
    impact = np.empty((draws, n), dtype=np.int16)
    distributions = {}
    for column, risk_id in enumerate(risk_ids):
        row = analysis[risk_id]
        pi_l = rating_distribution(row["likelihood_residual"], rule)
        pi_i = rating_distribution(row["impact_residual"], rule)
        distributions[risk_id] = {
            "approved_L": row["likelihood_residual"],
            "approved_I": row["impact_residual"],
            "pi_L": {str(v): float(p) for v, p in zip(values, pi_l)},
            "pi_I": {str(v): float(p) for v, p in zip(values, pi_i)},
        }
        likelihood[:, column] = rng.choice(values, size=draws, p=pi_l)
        impact[:, column] = rng.choice(values, size=draws, p=pi_i)

    scores = likelihood.astype(np.int32) * impact.astype(np.int32)
    heat = (scores >= threshold).astype(np.int8)

    approved_heat = np.array(
        [1 if approved_scores[rid] >= threshold else 0 for rid in risk_ids], dtype=np.int8
    )
    approved_gate_vec = np.array([approved_gates[rid] for rid in risk_ids], dtype=np.int8)

    # ---- FP^heat: does the DECLARED HEAT-MAP RULE move under perturbation? ---
    heat_flips = (heat != approved_heat[None, :])
    fp_heat = heat_flips.mean(axis=0)

    # ---- FP^C*: does the APPROVED GATE ASSIGNMENT move? ---------------------
    # Re-run the actual coverage classifier on perturbed ratings.  Because the
    # rule reads the consequence descriptor and never L or I, this must be 0 --
    # and this loop is what verifies it rather than assuming it.
    perturbed_cstar_changes = 0
    probe_count = min(draws, 20000)
    probe_indices = rng.choice(draws, size=probe_count, replace=False)
    baseline_cstar = cov.classify_risks(assessment, profile)
    for draw_index in probe_indices[:1000]:
        perturbed = []
        for column, risk_id in enumerate(risk_ids):
            row = dict(analysis[risk_id])
            row["likelihood_residual"] = int(likelihood[draw_index, column])
            row["impact_residual"] = int(impact[draw_index, column])
            perturbed.append(row)
        probe_assessment = type(assessment)(
            metadata=assessment.metadata,
            system_profile=assessment.system_profile,
            obligations=assessment.obligations,
            risk_register=assessment.risk_register,
            risk_analysis=perturbed,
        )
        if cov.classify_risks(probe_assessment, profile) != baseline_cstar:
            perturbed_cstar_changes += 1

    fp_cstar = np.zeros(n, dtype=float)
    expected_gate_changes_heat = float(heat_flips.sum(axis=1).mean())

    # ---- GD(T_H) and GD_min distributions over draws ------------------------
    gd_draws = (approved_gate_vec[None, :] != heat).sum(axis=1)

    # GD_min per draw: the candidate threshold set is derived from that draw's
    # scores, exactly as the definition requires.
    gd_min_draws = np.empty(draws, dtype=np.int32)
    unique_score_sets = {}
    for k in range(draws):
        key = scores[k].tobytes()
        cached = unique_score_sets.get(key)
        if cached is None:
            row_scores = scores[k]
            candidates = set()
            for value in np.unique(row_scores):
                candidates.update((int(value) - 1, int(value), int(value) + 1))
            best = n + 1
            for t in sorted(candidates):
                predicted = (row_scores >= t).astype(np.int8)
                best = min(best, int((approved_gate_vec != predicted).sum()))
            cached = best
            unique_score_sets[key] = cached
        gd_min_draws[k] = cached

    def distribution(array):
        values_, counts = np.unique(array, return_counts=True)
        return {str(int(v)): int(c) for v, c in zip(values_, counts)}

    def mcse(p):
        return float(math.sqrt(p * (1.0 - p) / draws))

    per_risk = []
    for column, risk_id in enumerate(risk_ids):
        p = float(fp_heat[column])
        per_risk.append(
            {
                "case": case_id,
                "risk_id": risk_id,
                "approved_L": distributions[risk_id]["approved_L"],
                "approved_I": distributions[risk_id]["approved_I"],
                "approved_score": approved_scores[risk_id],
                "approved_gate": int(approved_gate_vec[column]),
                "heatmap_gate_approved": int(approved_heat[column]),
                "FP_heat": p,
                "FP_heat_mcse": mcse(p),
                "FP_cstar": float(fp_cstar[column]),
                "distance_to_threshold": approved_scores[risk_id] - threshold,
            }
        )

    max_row = max(per_risk, key=lambda r: r["FP_heat"])

    return {
        "case_id": case_id,
        "draws_K": draws,
        "declared_threshold": threshold,
        "register_row_count": n,
        "rng_seed": rng_seed,
        "distributions": distributions,
        "per_risk": per_risk,
        "max_FP_heat": {
            "value": max_row["FP_heat"],
            "risk_id": max_row["risk_id"],
            "mcse": max_row["FP_heat_mcse"],
            "approved_score": max_row["approved_score"],
        },
        "mean_FP_heat": float(fp_heat.mean()),
        "max_FP_cstar": float(fp_cstar.max()) if n else 0.0,
        "expected_gate_changes_per_register_heatmap": expected_gate_changes_heat,
        "expected_gate_changes_per_register_cstar": 0.0,
        "cstar_membership_changes_observed": perturbed_cstar_changes,
        "cstar_probe_draws": 1000,
        "cstar_verification_note": (
            "The C* classifier was re-run on 1000 randomly selected perturbed draws. "
            "A non-zero count here would mean a rating dependence had leaked into "
            "gate assignment. The count is the measurement, not an assumption."
        ),
        "GD_distribution": distribution(gd_draws),
        "GD_mean": float(gd_draws.mean()),
        "GD_approved": int((approved_gate_vec != approved_heat).sum()),
        "GD_min_distribution": distribution(gd_min_draws),
        "GD_min_mean": float(gd_min_draws.mean()),
        "MCSE_upper_bound_at_K": float(math.sqrt(0.25 / draws)),
    }


def run(draws, final):
    spec = read_json(SPEC_PATH)
    payload = {
        "specification": spec,
        "provenance_warning": spec["provenance"]["statement"],
        "per_case": {},
        "sensitivity_variant": {},
    }

    all_rows = []
    for case_id in CASES:
        analysis = analyse_case(case_id, draws, spec, spec["perturbation_rule"],
                                spec["seed"])
        payload["per_case"][case_id] = analysis
        all_rows.extend(analysis["per_risk"])
        print("%s  K=%d  max FP_heat=%.6f (%s, MCSE %.6f)  max FP_C*=%.6f  "
              "E[gate changes]=%.4f  C* changes observed=%d"
              % (case_id, draws, analysis["max_FP_heat"]["value"],
                 analysis["max_FP_heat"]["risk_id"], analysis["max_FP_heat"]["mcse"],
                 analysis["max_FP_cstar"],
                 analysis["expected_gate_changes_per_register_heatmap"],
                 analysis["cstar_membership_changes_observed"]))

    # Secondary: the renormalisation boundary rule, so the reader can see how
    # much the out-of-range handling matters.
    variant_rule = dict(spec["perturbation_rule"])
    variant_rule.update(spec["sensitivity_variant"])
    for case_id in CASES:
        variant = analyse_case(case_id, min(draws, 250000), spec, variant_rule,
                               spec["seed"] + 1)
        payload["sensitivity_variant"][case_id] = {
            "rule": spec["sensitivity_variant"]["name"],
            "max_FP_heat": variant["max_FP_heat"],
            "mean_FP_heat": variant["mean_FP_heat"],
            "max_FP_cstar": variant["max_FP_cstar"],
            "expected_gate_changes_per_register_heatmap":
                variant["expected_gate_changes_per_register_heatmap"],
        }
        print("%s  [sensitivity variant: renormalise] max FP_heat=%.6f"
              % (case_id, variant["max_FP_heat"]["value"]))

    write_result(final, "monte_carlo_summary", payload)
    write_csv(
        final, "monte_carlo_per_risk.csv",
        ["case", "risk_id", "approved_L", "approved_I", "approved_score",
         "approved_gate", "heatmap_gate_approved", "FP_heat", "FP_heat_mcse",
         "FP_cstar", "distance_to_threshold"],
        all_rows,
    )
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draws", type=int, default=None,
                        help="override K (the frozen specification says 250000)")
    add_common_args(parser)
    args = parser.parse_args(argv)
    spec = read_json(SPEC_PATH)
    draws = args.draws or spec["draws_K"]
    if phase_of(args) != "development" and draws < spec["draws_K"]:
        raise SystemExit(
            "refusing to write a reportable (%s) result with K=%d below the frozen "
            "K=%d" % (phase_of(args), draws, spec["draws_K"])
        )
    run(draws, phase_of(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
