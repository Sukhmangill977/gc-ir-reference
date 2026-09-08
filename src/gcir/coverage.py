"""Consequence-class gate coverage: C*, the coverage rule CV, and gate divergence.

Manuscript Section VII.

    c_i = (kind_i, materiality_i, reversibility_i, authority_i);  C*(c_i) in {0,1}

Base profile (Section VII-A), closed for v1.0::

    C* = { material_statutory_prohibition,
           unauthorized_authority_exercise,
           material_information_barrier_breach,
           irreversible_external_effect_above_approved_bound }

Coverage rule CV: for any risk with ``C*(c_i) = 1`` the approved specification set
must contain at least one mandatory gate -- or mandatory gate set -- covering
*each* authorized hazardous action path, irrespective of L x I.  A C* risk may in
addition carry supporting advisory or weighted predicates; ``mandatory_role``
records which specifications are decisive.

Gate divergence (Section VII-B)::

    GD(T_H) = sum_i 1[g_i != 1[s_i >= T_H]]
    GD_min  = min over t in T of sum_i 1[g_i != 1[s_i >= t]]

where T contains the distinct observed scores and the boundary values immediately
above and below them, and *both sums run over all register rows including
non-runtime dispositions*.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .models import CSTAR_BASE_PROFILE_V1, ActionTuple, CoverageError, ValidationError


class CStarProfile:
    """An approved, versioned consequence-class profile."""

    def __init__(self, document):
        self._doc = document
        kinds = tuple(document["member_kinds"])
        self._members = kinds
        for kind in kinds:
            if kind not in document["classification_rules"]:
                raise ValidationError(
                    "C* member kind %r has no recorded classification rule "
                    "(approving authority, rationale, materiality boundary, "
                    "effective date)" % kind,
                    code="CSTAR_RULE_MISSING",
                )

    @property
    def version(self):
        return self._doc["version"]

    @property
    def profile_id(self):
        return self._doc["profile_id"]

    @property
    def members(self):
        return self._members

    @property
    def document(self):
        return self._doc

    def canonical_document(self):
        """The profile as it enters the bundle hash.

        ``member_kinds`` is a set expressed as a list; its order carries no
        meaning, so it is sorted before hashing (Section VI-C).  Object keys are
        already ordered by RFC 8785 itself.
        """
        document = {
            key: value
            for key, value in self._doc.items()
            if key not in ("signature", "member_kinds")
        }
        document["member_kinds"] = sorted(self._doc["member_kinds"])
        return document

    def is_base_profile_v1(self):
        return tuple(sorted(self._members)) == tuple(sorted(CSTAR_BASE_PROFILE_V1))

    def evaluate(self, descriptor):
        """``C*(c_i)`` -- 1 iff the descriptor's kind is a member *and* the
        materiality qualification is satisfied.

        "A documentation defect or other immaterial technical non-conformance does
        not enter C* solely because its source is statutory -- materiality
        qualifies membership." (Section VII-A)
        """
        if descriptor is None:
            return 0
        kind = descriptor.get("kind")
        if kind not in self._members:
            return 0
        rule = self._doc["classification_rules"][kind]
        required = rule["materiality_boundary"]["minimum_materiality"]
        order = self._doc["materiality_order"]
        actual = descriptor.get("materiality")
        if actual not in order:
            raise ValidationError(
                "consequence descriptor materiality %r is outside the approved "
                "materiality order %r" % (actual, order),
                code="MATERIALITY_UNKNOWN",
            )
        if order.index(actual) < order.index(required):
            return 0
        return 1


def classify_risks(assessment, profile):
    """Return ``{risk_id: 0|1}`` for every register row.

    A risk whose analysis row carries no consequence descriptor is *not* silently
    treated as non-C*: it is a RC-05 condition ("consequence class undefined") and
    the caller must have dispositioned it accordingly.
    """
    result = {}
    for risk in assessment.risk_register:
        analysis = assessment.analysis_index.get(risk["risk_id"])
        descriptor = (analysis or {}).get("consequence_descriptor")
        result[risk["risk_id"]] = profile.evaluate(descriptor)
    return result


def verify_cv(assessment, profile, predicates, gate_map, hazardous_paths_by_risk):
    """Bundle-level C* coverage check.  Returns the coverage matrix.

    Raises ``CoverageError`` when any C* risk has an authorized hazardous action
    path with no decisive mandatory gate.  Section VI-A: "rejects any bundle in
    which coverage fails".
    """
    cstar = classify_risks(assessment, profile)
    matrix = []
    failures = []

    for risk_id in sorted(cstar):
        if cstar[risk_id] != 1:
            continue
        paths = hazardous_paths_by_risk.get(risk_id, [])
        if not paths:
            failures.append(
                {
                    "risk_id": risk_id,
                    "problem": "C* risk declares no authorized hazardous action path",
                }
            )
            matrix.append(
                {
                    "risk_id": risk_id,
                    "c_star": 1,
                    "paths": [],
                    "covered": False,
                }
            )
            continue

        path_rows = []
        for path in paths:
            covering = sorted(
                p["gcir_id"]
                for p in predicates
                if p["origin"]["origin_id"] == risk_id
                and gate_map[p["gcir_id"]]["gate_type"] == "mandatory"
                and p["mandatory_role"] == "decisive"
                and ActionTuple.from_mapping(p).as_tuple() == path.as_tuple()
            )
            path_rows.append(
                {
                    "action_path": path.as_dict(),
                    "covering_predicates": covering,
                    "covered": bool(covering),
                }
            )
            if not covering:
                failures.append(
                    {
                        "risk_id": risk_id,
                        "action_path": path.as_dict(),
                        "problem": "no decisive mandatory gate covers this "
                        "authorized hazardous action path",
                    }
                )

        matrix.append(
            {
                "risk_id": risk_id,
                "c_star": 1,
                "paths": path_rows,
                "covered": all(row["covered"] for row in path_rows),
            }
        )

    if failures:
        raise CoverageError(
            "C* coverage requirement CV is not satisfied for %d path(s)"
            % len(failures),
            detail={"failures": failures},
        )
    return matrix


def cv_metric(coverage_matrix):
    """CV = |covered C* risks| / |C* risks|; 1.0 vacuously when there are none."""
    if not coverage_matrix:
        return 1.0, 0, 0
    covered = sum(1 for row in coverage_matrix if row["covered"])
    return covered / len(coverage_matrix), covered, len(coverage_matrix)


# ---------------------------------------------------------------------------
# Gate divergence (Section VII-B, VII-C, VII-D)
# ---------------------------------------------------------------------------


def approved_gate_vector(assessment, gate_map, predicates):
    """``g_i`` per register row: 1 iff the row carries mandatory-gate coverage.

    Section VII-B: "g_i = 1 denotes that risk r_i carries mandatory-gate coverage
    under the approved assignment".  Rows with a non-runtime, accepted or
    unresolved disposition carry ratings but no gate, and are therefore 0 -- they
    are included in the divergence sums (Section IX).
    """
    gated = set()
    for predicate in predicates:
        if predicate["origin"]["origin_type"] != "risk_derived":
            continue
        if gate_map[predicate["gcir_id"]]["gate_type"] == "mandatory":
            gated.add(predicate["origin"]["origin_id"])
    return {risk["risk_id"]: (1 if risk["risk_id"] in gated else 0) for risk in assessment.risk_register}


def residual_scores(assessment):
    """``s_i = L_i^res * I_i^res`` for every register row."""
    scores = {}
    for row in assessment.risk_analysis:
        scores[row["risk_id"]] = row["likelihood_residual"] * row["impact_residual"]
    return scores


def threshold_candidates(scores):
    """T: the distinct observed scores and the boundary values immediately above
    and below them (Section VII-B)."""
    observed = sorted(set(scores))
    candidates = set()
    for value in observed:
        candidates.add(value)
        candidates.add(value + 1)
        candidates.add(value - 1)
    return sorted(candidates)


def gate_divergence(gates, scores, threshold):
    """``GD(t) = sum_i 1[g_i != 1[s_i >= t]]``, with the disagreeing rows."""
    divergent = []
    for risk_id in sorted(gates):
        heat = 1 if scores[risk_id] >= threshold else 0
        if gates[risk_id] != heat:
            divergent.append(
                {
                    "risk_id": risk_id,
                    "score": scores[risk_id],
                    "approved_gate": gates[risk_id],
                    "heatmap_gate": heat,
                }
            )
    return len(divergent), divergent


def gd_min(gates, scores):
    """``GD_min`` over all candidate thresholds, with the argmin set."""
    best = None
    per_threshold = []
    for threshold in threshold_candidates(scores.values()):
        count, _ = gate_divergence(gates, scores, threshold)
        per_threshold.append({"threshold": threshold, "gd": count})
        if best is None or count < best:
            best = count
    argmin = sorted(row["threshold"] for row in per_threshold if row["gd"] == best)
    return best, argmin, per_threshold


def detect_inversions(gates, scores):
    """Proposition 1 premise: pairs with ``s_i < s_j``, ``g_i = 1``, ``g_j = 0``."""
    inversions = []
    ids = sorted(gates)
    for i in ids:
        for j in ids:
            if gates[i] == 1 and gates[j] == 0 and scores[i] < scores[j]:
                inversions.append(
                    {
                        "gated_risk": i,
                        "gated_score": scores[i],
                        "ungated_risk": j,
                        "ungated_score": scores[j],
                    }
                )
    return inversions


def detect_collisions(gates, scores):
    """Proposition 2 premise: equal scores carrying divergent gates."""
    by_score = {}
    for risk_id in sorted(gates):
        by_score.setdefault(scores[risk_id], []).append(risk_id)
    collisions = []
    for score in sorted(by_score):
        members = by_score[score]
        values = {gates[m] for m in members}
        if len(values) > 1:
            collisions.append(
                {
                    "score": score,
                    "gated": sorted(m for m in members if gates[m] == 1),
                    "ungated": sorted(m for m in members if gates[m] == 0),
                }
            )
    return collisions
