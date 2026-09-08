"""Primary metrics (manuscript Section XI-B), computed from artifacts only.

No metric in this module has a hardcoded expected value.  Each is a function of
the compiled bundle and the assessment it was compiled from.

    DC   |{r : Delta_i in (runtime, nonruntime, accepted)}| / |R|
    RCY  |{r : Delta_i = runtime}| / |R|                     -- descriptive
    NDR  |{r : Delta_i in (nonruntime, accepted)}| / |R|      -- descriptive
    OPR  |{p : origin(p) not in R union INV}| / |P|           -- required 0
    ODC  |{o : o ~> runtime or nonruntime or accepted}| / |O|
    PTC  |{p : p ~> risk or compiler invariant}| / |P|
    CV   |{r : C*=1 and every hazardous path mandatorily gated}| / |{r : C*=1}|
    TD   sum_k 1[H_k = H_reference] / N
    GD   GD(T_H) and GD_min

SNR and DF are RQ5 outcomes and are DEFERRED; this module deliberately does not
compute them and ``rq5_deferred_metrics`` says so explicitly.
"""

from __future__ import annotations

from typing import Any, Dict, List

from . import coverage as coverage_mod


def _ratio(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator


def disposition_metrics(assessment, bundle):
    """DC, RCY, NDR over the disposition records in the compiled payload."""
    statuses = {}
    for record in bundle.dispositions:
        kind = record["record_type"]
        status = {
            "RuntimeDisposition": "runtime",
            "NonRuntimeDisposition": "nonruntime",
            "AcceptedRiskDisposition": "accepted",
            "UnresolvedDisposition": "unresolved",
        }[kind]
        statuses[record["risk_id"]] = status

    total = len(assessment.risk_register)
    disposed = sum(1 for s in statuses.values() if s in ("runtime", "nonruntime", "accepted"))
    runtime = sum(1 for s in statuses.values() if s == "runtime")
    nonruntime_or_accepted = sum(1 for s in statuses.values() if s in ("nonruntime", "accepted"))

    return {
        "DC": {
            "value": _ratio(disposed, total),
            "numerator": disposed,
            "denominator": total,
            "definition": "|{r_i : Delta_i in (runtime, nonruntime, accepted)}| / |R|",
            "required": "1.000 for release admissibility",
        },
        "RCY": {
            "value": _ratio(runtime, total),
            "numerator": runtime,
            "denominator": total,
            "definition": "|{r_i : Delta_i = runtime(D_i)}| / |R|",
            "required": "descriptive, not a quality target",
        },
        "NDR": {
            "value": _ratio(nonruntime_or_accepted, total),
            "numerator": nonruntime_or_accepted,
            "denominator": total,
            "definition": "|{r_i : Delta_i in (nonruntime, accepted)}| / |R|",
            "required": "descriptive",
        },
        "disposition_counts": {
            "runtime": runtime,
            "nonruntime": sum(1 for s in statuses.values() if s == "nonruntime"),
            "accepted": sum(1 for s in statuses.values() if s == "accepted"),
            "unresolved": sum(1 for s in statuses.values() if s == "unresolved"),
        },
    }


def origin_metrics(assessment, bundle, invariant_ids):
    """OPR and PTC.  Both are computed by re-deriving origin resolution from the
    payload rather than trusting the compiler's own assertion."""
    risk_ids = set(assessment.risk_index)
    invariants = set(invariant_ids)
    predicates = bundle.predicates

    orphans = []
    traceable = 0
    for predicate in predicates:
        origin = predicate["origin"]
        resolved = (
            (origin["origin_type"] == "risk_derived" and origin["origin_id"] in risk_ids)
            or (origin["origin_type"] == "compiler_invariant" and origin["origin_id"] in invariants)
        )
        if resolved:
            traceable += 1
        else:
            orphans.append(predicate["gcir_id"])

    total = len(predicates)
    return {
        "OPR": {
            "value": _ratio(len(orphans), total),
            "numerator": len(orphans),
            "denominator": total,
            "definition": "|{p in P : origin(p) not in R union INV}| / |P|",
            "required": "0.000",
            "orphans": orphans,
        },
        "PTC": {
            "value": _ratio(traceable, total),
            "numerator": traceable,
            "denominator": total,
            "definition": "|{p in P : p ~> risk or compiler invariant}| / |P|",
            "required": "1.000",
        },
    }


def obligation_metrics(bundle):
    """ODC.

    Traceability completeness does not require every obligation to produce a
    predicate (Section VIII): an obligation is disposed if every risk that cites
    it carries a runtime, non-runtime or accepted disposition.
    """
    rows = bundle.coverage_matrix["obligations"]
    disposed = sum(1 for row in rows if row["disposed"])
    return {
        "ODC": {
            "value": _ratio(disposed, len(rows)),
            "numerator": disposed,
            "denominator": len(rows),
            "definition": "|{o in O : o ~> runtime or nonruntime or accepted}| / |O|",
            "required": "1.000",
            "undisposed": [row["obligation_id"] for row in rows if not row["disposed"]],
            "obligations_without_predicate": [
                row["obligation_id"] for row in rows if row["disposed"] and not row["predicate_ids"]
            ],
        }
    }


def coverage_metrics(bundle):
    """CV over the compiled coverage matrix."""
    matrix = bundle.coverage_matrix["c_star_coverage"]
    value, covered, total = coverage_mod.cv_metric(matrix)
    return {
        "CV": {
            "value": value,
            "numerator": covered,
            "denominator": total,
            "definition": "|{r_i : C*(c_i)=1 and each hazardous action path mandatorily gated}| / |{r_i : C*(c_i)=1}|",
            "required": "1.000",
            "note": "1.0 vacuously when the register contains no C* risk" if total == 0 else "",
        }
    }


def gate_metrics(assessment, bundle, declared_threshold):
    """GD(T_H), GD_min, and the Proposition 1/2 premises."""
    gates = coverage_mod.approved_gate_vector(assessment, bundle.gate_map, bundle.predicates)
    scores = coverage_mod.residual_scores(assessment)
    gd, divergent = coverage_mod.gate_divergence(gates, scores, declared_threshold)
    minimum, argmin, per_threshold = coverage_mod.gd_min(gates, scores)
    inversions = coverage_mod.detect_inversions(gates, scores)
    collisions = coverage_mod.detect_collisions(gates, scores)
    return {
        "GD": {
            "declared_threshold": declared_threshold,
            "value": gd,
            "definition": "GD(T_H) = sum_i 1[g_i != 1[s_i >= T_H]] over ALL register rows",
            "divergent_rows": divergent,
        },
        "GD_min": {
            "value": minimum,
            "argmin_thresholds": argmin,
            "definition": "min over t in T of sum_i 1[g_i != 1[s_i >= t]]",
            "per_threshold": per_threshold,
        },
        "proposition_1_premise": {
            "holds": bool(inversions),
            "statement": "exists r_i, r_j with s_i < s_j, g_i = 1, g_j = 0",
            "implies": "GD_min >= 1",
            "inversion_count": len(inversions),
            "inversions": inversions,
        },
        "proposition_2_premise": {
            "holds": bool(collisions),
            "statement": "exists r_i, r_j with s_i = s_j and g_i != g_j",
            "implies": "no function of the scalar score alone reproduces the approved gate assignment",
            "collisions": collisions,
        },
        "gate_vector": {rid: gates[rid] for rid in sorted(gates)},
        "score_vector": {rid: scores[rid] for rid in sorted(scores)},
    }


def gate_source_breakdown(bundle):
    counts = {}
    roles = {}
    for entry in bundle.gate_map.values():
        key = "%s/%s" % (entry["gate_type"], entry["gate_source"])
        counts[key] = counts.get(key, 0) + 1
        roles[entry["mandatory_role"]] = roles.get(entry["mandatory_role"], 0) + 1
    return {"by_gate_type_and_source": counts, "by_mandatory_role": roles}


def translation_determinism(hashes, reference_hash):
    """TD = sum_k 1[H_k = H_reference] / N."""
    matches = sum(1 for h in hashes if h == reference_hash)
    return {
        "TD": {
            "value": _ratio(matches, len(hashes)),
            "numerator": matches,
            "denominator": len(hashes),
            "definition": "sum_k 1[H_k = H_reference] / N over environments and permutations",
            "reference_hash": reference_hash,
            "note": "TD applies to the canonical payload hash. The signature envelope "
            "is not required to be byte-identical across signing events.",
        }
    }


def rq5_deferred_metrics():
    """SNR and DF are the primary outcomes of the deferred comparative study."""
    return {
        "SNR": {
            "value": None,
            "status": "DEFERRED",
            "definition": "sum_i SN_i / |R| against the independently adjudicated reference",
            "reason": "RQ5 is preregistered and deferred (Section XI). No adjudication panel "
            "has been convened and no participant data exists. Reporting any value here "
            "would be fabrication.",
        },
        "DF": {
            "value": None,
            "status": "DEFERRED",
            "definition": "DF_i = |F_i intersect F_i*| / |F_i*|; DF = mean over R",
            "reason": "RQ5 is preregistered and deferred (Section XI).",
        },
    }


def compute_all(assessment, bundle, invariant_ids, declared_threshold):
    result = {}
    result.update(disposition_metrics(assessment, bundle))
    result.update(origin_metrics(assessment, bundle, invariant_ids))
    result.update(obligation_metrics(bundle))
    result.update(coverage_metrics(bundle))
    result.update(gate_metrics(assessment, bundle, declared_threshold))
    result["gate_sources"] = gate_source_breakdown(bundle)
    result["deferred"] = rq5_deferred_metrics()
    return result
