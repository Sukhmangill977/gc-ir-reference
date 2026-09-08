"""Generate ``results/V1_V2_COMPARISON.md``.

    python -m experiments.compare_campaigns

Compares the v1 campaign (`results/final/`, executed after a LOCAL freeze) with
the v2 campaign (`results/final_v2/`, executed after a PUBLIC freeze), value by
value.

Differences are reported, never hidden. Where a value differs, the comparison
states why -- and if it cannot state why, it says so, which is itself the
finding.
"""

from __future__ import annotations

import argparse
import os

from experiments.common import REPO_ROOT, read_json

V1 = os.path.join(REPO_ROOT, "results", "final")
V2 = os.path.join(REPO_ROOT, "results", "final_v2")

#: Differences that are expected, with the reason. Anything not listed here and
#: not equal is flagged as UNEXPLAINED.
EXPECTED_DIFFERENCES = {
    "TD denominator": "v1 ran 30 runs per case (60); v2 runs the examiner's "
                      "stratified 31 per case (62).",
    "TD runs_per_case": "30 -> 31, per the artifact-runs memo's 10+10+5+3+3 breakdown.",
    "adversarial corpus size": "v1 had 59 cases; v2 adds ADV-055, ADV-056 (the "
                               "timeout class) and POS-006, giving 62.",
    "structural checks": "v1 had 24; v2 adds the omitted-mandatory-predicate "
                         "direction of state mismatch, giving 26.",
    "test count": "v2 adds the timeout adversarial cases to the parametrised suite.",
    "case_b_injection_scenarios": "new in v2; absent from v1.",
}


def load(directory, name):
    path = os.path.join(directory, name)
    if not os.path.exists(path):
        return None
    blob = read_json(path)
    return blob.get("result", blob)


def fmt(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return "%.6f" % value
    return str(value)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=os.path.join(REPO_ROOT, "results",
                                                      "V1_V2_COMPARISON.md"))
    args = parser.parse_args(argv)

    rows = []
    unexplained = []

    def compare(label, a, b, reason=None):
        same = a == b
        if not same and reason is None:
            unexplained.append(label)
        rows.append({
            "label": label, "v1": fmt(a), "v2": fmt(b),
            "same": same,
            "reason": ("identical" if same else (reason or "**UNEXPLAINED**")),
        })

    m1, m2 = load(V1, "metrics.json"), load(V2, "metrics.json")
    d1, d2 = load(V1, "determinism_summary.json"), load(V2, "determinism_summary.json")
    mc1, mc2 = load(V1, "monte_carlo_summary.json"), load(V2, "monte_carlo_summary.json")
    a1, a2 = load(V1, "adversarial.json"), load(V2, "adversarial.json")
    p1, p2 = load(V1, "property_tests.json"), load(V2, "property_tests.json")
    t1, t2 = load(V1, "traceability_queries.json"), load(V2, "traceability_queries.json")

    for case_id in ("case_a", "case_b"):
        c1 = load(V1, "%s/compilation.json" % case_id)
        c2 = load(V2, "%s/compilation.json" % case_id)
        compare("%s canonical payload hash" % case_id,
                c1 and c1["payload_hash"], c2 and c2["payload_hash"])
        compare("%s predicate count" % case_id,
                c1 and c1["statistics"]["predicate_count"],
                c2 and c2["statistics"]["predicate_count"])

    for case_id in ("case_a", "case_b"):
        for name in ("DC", "RCY", "NDR", "OPR", "ODC", "PTC", "CV"):
            compare("%s %s" % (case_id, name),
                    m1 and m1["per_case"][case_id][name]["value"],
                    m2 and m2["per_case"][case_id][name]["value"])
        compare("%s GD(T_H)" % case_id,
                m1 and m1["per_case"][case_id]["GD"]["value"],
                m2 and m2["per_case"][case_id]["GD"]["value"])
        compare("%s GD_min" % case_id,
                m1 and m1["per_case"][case_id]["GD_min"]["value"],
                m2 and m2["per_case"][case_id]["GD_min"]["value"])

    compare("TD value", d1 and d1["TD"]["value"], d2 and d2["TD"]["value"])
    compare("TD numerator", d1 and d1["TD"]["numerator"], d2 and d2["TD"]["numerator"],
            EXPECTED_DIFFERENCES["TD denominator"])
    compare("TD denominator", d1 and d1["TD"]["denominator"],
            d2 and d2["TD"]["denominator"], EXPECTED_DIFFERENCES["TD denominator"])
    compare("determinism runs per case", d1 and d1.get("runs_per_case"),
            d2 and d2.get("runs_per_case"), EXPECTED_DIFFERENCES["TD runs_per_case"])
    for case_id in ("case_a", "case_b"):
        compare("%s determinism reference hash" % case_id,
                d1 and d1["per_case"][case_id]["reference_hash"],
                d2 and d2["per_case"][case_id]["reference_hash"])

    for case_id in ("case_a", "case_b"):
        compare("%s Monte Carlo K" % case_id,
                mc1 and mc1["per_case"][case_id]["draws_K"],
                mc2 and mc2["per_case"][case_id]["draws_K"])
        compare("%s max FP^heat" % case_id,
                mc1 and mc1["per_case"][case_id]["max_FP_heat"]["value"],
                mc2 and mc2["per_case"][case_id]["max_FP_heat"]["value"])
        compare("%s max FP^C*" % case_id,
                mc1 and mc1["per_case"][case_id]["max_FP_cstar"],
                mc2 and mc2["per_case"][case_id]["max_FP_cstar"])

    compare("adversarial corpus size", a1 and a1["corpus"]["total"],
            a2 and a2["corpus"]["total"], EXPECTED_DIFFERENCES["adversarial corpus size"])
    compare("adversarial failures", a1 and a1["corpus"]["failed"],
            a2 and a2["corpus"]["failed"])
    compare("adversarial code mismatches", a1 and a1["corpus"]["code_mismatch"],
            a2 and a2["corpus"]["code_mismatch"])
    compare("structural checks passed", a1 and a1["structural_checks"]["passed"],
            a2 and a2["structural_checks"]["passed"],
            EXPECTED_DIFFERENCES["structural checks"])
    compare("Case B injection scenarios",
            (a1 or {}).get("case_b_injection_scenarios", {}).get("scenario_count"),
            (a2 or {}).get("case_b_injection_scenarios", {}).get("scenario_count"),
            EXPECTED_DIFFERENCES["case_b_injection_scenarios"])

    compare("tests total", p1 and p1["totals"]["tests"], p2 and p2["totals"]["tests"],
            EXPECTED_DIFFERENCES["test count"])
    compare("tests failed", p1 and p1["totals"]["failures"],
            p2 and p2["totals"]["failures"])
    compare("properties", p1 and p1["property_based"]["property_count"],
            p2 and p2["property_based"]["property_count"])
    compare("generated examples",
            p1 and p1["property_based"]["total_generated_examples"],
            p2 and p2["property_based"]["total_generated_examples"])

    compare("traceability clean queries empty",
            t1 and t1["summary"]["all_clean_queries_empty"],
            t2 and t2["summary"]["all_clean_queries_empty"])
    compare("traceability controls all detected",
            t1 and t1["summary"]["all_negative_controls_detected"],
            t2 and t2["summary"]["all_negative_controls_detected"])

    identical = sum(1 for r in rows if r["same"])
    differing = len(rows) - identical

    lines = [
        "# v1 vs v2 campaign comparison",
        "",
        "Two complete reportable campaigns were executed.",
        "",
        "| | v1 | v2 |",
        "|---|---|---|",
        "| Results | `results/final/` | `results/final_v2/` |",
        "| Freeze | `preregister-tier0-v1` | `preregister-tier0-v2.1` |",
        "| Freeze was public **at execution time** | **No** — local tag only | **Yes** — pushed and remote-verified first |",
        "| Determinism runs | 30 per case (60) | 31 per case (62) |",
        "| Reportable | **No** — superseded | **Yes** |",
        "",
        "**Why v1 is not reported.** Its freeze was never pushed before the campaign "
        "ran. A later push cannot convert a past experiment into a prospectively "
        "public preregistered one, so v1 was superseded rather than relabelled. Its "
        "files are retained unedited; its metadata was not altered and "
        "`public_commitment_discharged` was not flipped retroactively.",
        "",
        "---",
        "",
        "## Value-by-value",
        "",
        "| Quantity | v1 | v2 | Same? | Explanation |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append("| %s | `%s` | `%s` | %s | %s |"
                     % (row["label"], row["v1"], row["v2"],
                        "yes" if row["same"] else "**no**", row["reason"]))

    lines += [
        "",
        "## Summary",
        "",
        "| | Count |",
        "|---|---|",
        "| Quantities compared | %d |" % len(rows),
        "| Identical | %d |" % identical,
        "| Differing, with a stated reason | %d |" % (differing - len(unexplained)),
        "| **Differing, unexplained** | **%d** |" % len(unexplained),
        "",
    ]
    if unexplained:
        lines += [
            "### Unexplained differences — these need attention",
            "",
        ]
        for label in unexplained:
            lines.append("* `%s`" % label)
        lines.append("")
    else:
        lines += [
            "**Every difference between the two campaigns has a stated cause, and "
            "every substantive measured value is identical.** The bundle hashes, all "
            "seven per-case metrics, GD, GD_min, TD = 1.000, the Monte Carlo flip "
            "probabilities and the traceability outcomes are unchanged; what changed "
            "is the number of determinism runs, the size of the adversarial corpus, "
            "and the addition of the Case B injection scenarios — all of them "
            "deliberate scope increases made *before* the v2 freeze.",
            "",
            "That the measured values are identical across two independently "
            "executed campaigns, at different corpus sizes and run counts, is itself "
            "corroboration: the numbers are properties of the artifacts, not of a "
            "particular execution.",
            "",
        ]

    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))

    print("wrote %s" % os.path.relpath(args.out, REPO_ROOT))
    print("  %d compared, %d identical, %d differing (%d unexplained)"
          % (len(rows), identical, differing, len(unexplained)))
    for label in unexplained:
        print("    UNEXPLAINED: %s" % label)
    return 1 if unexplained else 0


if __name__ == "__main__":
    raise SystemExit(main())
