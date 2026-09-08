"""Gate-divergence analysis and the heat-map comparator (Section VII-B..D, IX).

    python -m experiments.run_gate_divergence [--final]

Computes, per case:
  * ``GD(T_H)`` at the enterprise's predeclared frozen threshold
  * ``GD_min`` over all candidate thresholds (distinct observed scores and the
    boundary values immediately above and below them)
  * whether the register contains a **threshold inversion** (Proposition 1
    premise) and a **score collision with divergent gates** (Proposition 2
    premise)
  * the full ``GD(t)`` curve, so the reader can see that no threshold does better
  * a heat-map comparison table, one row per register row

It also runs a **sensitivity analysis** the manuscript does not contain.  Case A's
three non-runtime rows carry residual ratings that the manuscript does not state,
so they are documented synthetic fixtures (FP-014).  Because both GD sums run
over all register rows, those three ratings can move ``GD_min``.  The sweep
reports how, so the reported ``GD_min`` is not silently contingent on an
undisclosed choice.
"""

from __future__ import annotations

import argparse
import itertools
import json

from experiments.common import (
    CASES,
    add_common_args,
    load_case_bundle,
    write_csv,
    write_result,
)

#: Case A rows whose L x I the manuscript does not state (see FP-014).
CASE_A_FIXTURE_RATED_ROWS = ("R-14", "R-15", "R-16")


def analyse_case(case_id):
    from gcir import coverage as cov

    case, inputs, result = load_case_bundle(case_id)
    threshold = case.parameters["declared_heatmap_threshold"]
    bundle = result.bundle
    assessment = inputs.assessment

    gates = cov.approved_gate_vector(assessment, bundle.gate_map, bundle.predicates)
    scores = cov.residual_scores(assessment)
    analysis = assessment.analysis_index
    disposition_status = {
        record["risk_id"]: record["record_type"] for record in bundle.dispositions
    }

    gd, divergent = cov.gate_divergence(gates, scores, threshold)
    minimum, argmin, per_threshold = cov.gd_min(gates, scores)
    inversions = cov.detect_inversions(gates, scores)
    collisions = cov.detect_collisions(gates, scores)

    gate_sources = {}
    for predicate in bundle.predicates:
        if predicate["origin"]["origin_type"] != "risk_derived":
            continue
        entry = bundle.gate_map[predicate["gcir_id"]]
        gate_sources.setdefault(predicate["origin"]["origin_id"], set()).add(
            "%s/%s" % (entry["gate_type"], entry["gate_source"])
        )

    table = []
    for risk_id in sorted(gates):
        row = analysis[risk_id]
        heat = 1 if scores[risk_id] >= threshold else 0
        table.append(
            {
                "case": case_id,
                "risk_id": risk_id,
                "likelihood_residual": row["likelihood_residual"],
                "impact_residual": row["impact_residual"],
                "score": scores[risk_id],
                "consequence_class": row["consequence_class"],
                "c_star": 1 if (row.get("consequence_descriptor") or {}).get("kind")
                in inputs.cstar_profile.members
                and inputs.cstar_profile.evaluate(row.get("consequence_descriptor")) == 1
                else 0,
                "approved_gate": gates[risk_id],
                "heatmap_gate_at_declared_threshold": heat,
                "divergent": 1 if gates[risk_id] != heat else 0,
                "disposition": disposition_status[risk_id],
                "gate_sources": "|".join(sorted(gate_sources.get(risk_id, []))) or "none",
            }
        )

    return {
        "case_id": case_id,
        "declared_threshold": threshold,
        "GD_at_declared_threshold": gd,
        "divergent_rows": divergent,
        "GD_min": minimum,
        "GD_min_argmin_thresholds": argmin,
        "gd_curve": per_threshold,
        "register_row_count": len(gates),
        "proposition_1": {
            "premise": "exists r_i, r_j with s_i < s_j, g_i = 1, g_j = 0",
            "holds": bool(inversions),
            "consequence": "GD_min >= 1" if inversions else "no inversion on this register",
            "inversion_count": len(inversions),
            "inversions": inversions,
            "measured_GD_min": minimum,
            "consistent_with_proposition": (minimum >= 1) if inversions else True,
        },
        "proposition_2": {
            "premise": "exists r_i, r_j with s_i = s_j and g_i != g_j",
            "holds": bool(collisions),
            "consequence": "no function of the scalar score alone -- monotone or "
            "otherwise -- reproduces the approved gate assignment"
            if collisions
            else "no score collision with divergent gates on this register",
            "collisions": collisions,
        },
        "heatmap_table": table,
    }


def sensitivity_sweep(case_id, fixture_rows):
    """Re-measure GD_min over every plausible rating for the fixture-rated rows.

    This exists because the manuscript does not state L x I for Case A's three
    non-runtime rows, and both GD sums include them.  Reporting GD_min without
    reporting this sweep would hide a real dependence on an undisclosed choice.
    """
    from gcir import coverage as cov

    case, inputs, result = load_case_bundle(case_id)
    assessment = inputs.assessment
    gates = cov.approved_gate_vector(assessment, result.bundle.gate_map,
                                     result.bundle.predicates)
    base_scores = cov.residual_scores(assessment)
    present = [r for r in fixture_rows if r in base_scores]
    if not present:
        return None

    outcomes = {}
    grid = list(itertools.product(range(1, 6), repeat=2))
    for combination in itertools.product(grid, repeat=len(present)):
        scores = dict(base_scores)
        for risk_id, (likelihood, impact) in zip(present, combination):
            scores[risk_id] = likelihood * impact
        minimum, _, _ = cov.gd_min(gates, scores)
        outcomes[minimum] = outcomes.get(minimum, 0) + 1

    total = sum(outcomes.values())
    actual, _, _ = cov.gd_min(gates, base_scores)
    return {
        "fixture_rated_rows": present,
        "actual_scores": {r: base_scores[r] for r in present},
        "actual_GD_min": actual,
        "grid": "every (L, I) in {1..5}^2 for each fixture-rated row",
        "combinations_evaluated": total,
        "GD_min_distribution": {str(k): v for k, v in sorted(outcomes.items())},
        "GD_min_range": [min(outcomes), max(outcomes)],
        "share_of_grid_matching_actual": outcomes.get(actual, 0) / total,
        "interpretation": (
            "GD_min over the whole register depends in part on the ratings assigned "
            "to rows the manuscript leaves unrated. The reported GD_min is the value "
            "for the committed fixture ratings; this sweep states the range the "
            "choice could have produced, so the number is not silently contingent."
        ),
    }


def run(final):
    payload = {"per_case": {}}
    all_rows = []
    for case_id in CASES:
        analysis = analyse_case(case_id)
        payload["per_case"][case_id] = analysis
        all_rows.extend(analysis["heatmap_table"])
        print("%s  GD(%d)=%d  GD_min=%d (argmin t=%s)  inversions=%d  collisions=%d"
              % (case_id, analysis["declared_threshold"],
                 analysis["GD_at_declared_threshold"], analysis["GD_min"],
                 analysis["GD_min_argmin_thresholds"],
                 analysis["proposition_1"]["inversion_count"],
                 len(analysis["proposition_2"]["collisions"])))
        if analysis["divergent_rows"]:
            print("    divergent at declared threshold: %s"
                  % ", ".join(d["risk_id"] for d in analysis["divergent_rows"]))

    sweep = sensitivity_sweep("case_a", CASE_A_FIXTURE_RATED_ROWS)
    payload["case_a_fixture_rating_sensitivity"] = sweep
    if sweep:
        print("case_a GD_min sensitivity to the three fixture-rated non-runtime rows: "
              "range %s over %d rating combinations (actual %d)"
              % (sweep["GD_min_range"], sweep["combinations_evaluated"],
                 sweep["actual_GD_min"]))

    write_result(final, "gate_divergence", payload)
    write_csv(
        final, "gate_divergence_heatmap.csv",
        ["case", "risk_id", "likelihood_residual", "impact_residual", "score",
         "consequence_class", "c_star", "approved_gate",
         "heatmap_gate_at_declared_threshold", "divergent", "disposition",
         "gate_sources"],
        all_rows,
    )
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args(argv)
    run(args.final)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
