"""Print the complete reportable Tier-0 result set.

    python tools/show_results.py            # human-readable terminal report
    python tools/show_results.py --json     # the same values, machine-readable
    make results

Every value is READ from ``results/final_v2/`` -- the authoritative campaign
governed by the public preregistration freeze ``preregister-tier0-v2.2``.
Nothing is recomputed, substituted, or taken from manuscript prose.

This module is the **single authoritative result-reading implementation**.
``tools/update_readme_results.py`` imports :func:`load_results` from here rather
than reading the result files again, so the terminal report and the README table
cannot drift apart: there is one loader and one loaded object behind both.

Provenance is recorded as the values are read, not reconstructed afterwards.
Every entry in the returned object carries the file and the exact JSON path it
came from, which is what ``artifact_review/RESULT_DISPLAY_PROVENANCE.md`` is
generated from.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
from pathlib import Path
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINAL_V2 = "results/final_v2"

#: Result files that must exist and parse. A missing one is a hard failure --
#: this viewer never substitutes a placeholder for evidence it cannot read.
REQUIRED = (
    "metrics.json",
    "determinism_summary.json",
    "monte_carlo_summary.json",
    "adversarial.json",
    "property_tests.json",
    "traceability_queries.json",
    "gate_divergence.json",
    "PROVENANCE.json",
    "case_a/compilation.json",
    "case_b/compilation.json",
)

METRIC_ORDER = ("DC", "RCY", "NDR", "OPR", "ODC", "PTC", "CV")


class MissingEvidence(Exception):
    """A required result file is absent, unreadable, or missing a field."""


class Provenance:
    """Records where each displayed value came from, as it is read."""

    def __init__(self):
        self.rows = []

    def note(self, label, source, field, terminal=True, readme=False):
        self.rows.append({
            "displayed_result": label,
            "source_file": source,
            "field": field,
            "terminal": terminal,
            "readme": readme,
        })
        return self


def _read(relative):
    path = os.path.join(REPO_ROOT, relative)
    if not os.path.exists(path):
        raise MissingEvidence("required result file is missing: %s" % relative)
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise MissingEvidence("cannot read %s: %s" % (relative, exc)) from exc


def _result(relative):
    """Load a result file and unwrap the standard ``result`` envelope."""
    blob = _read(relative)
    return blob.get("result", blob)


def _need(blob, path, source):
    node = blob
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            raise MissingEvidence("%s: missing field %s" % (source, path))
        node = node[part]
    return node


def load_results():
    """Load every displayed value once, with its provenance.

    Returns a plain dict. Both the terminal renderer and the README generator
    consume this same object -- neither reads a result file directly.
    """
    for relative in REQUIRED:
        _read("%s/%s" % (FINAL_V2, relative))  # existence + parse check

    validate_evidence()
    prov = Provenance()

    metrics = _result("%s/metrics.json" % FINAL_V2)
    determinism = _result("%s/determinism_summary.json" % FINAL_V2)
    monte = _result("%s/monte_carlo_summary.json" % FINAL_V2)
    adversarial = _result("%s/adversarial.json" % FINAL_V2)
    properties = _result("%s/property_tests.json" % FINAL_V2)
    traceability = _result("%s/traceability_queries.json" % FINAL_V2)
    divergence = _result("%s/gate_divergence.json" % FINAL_V2)
    provenance_blob = _read("%s/PROVENANCE.json" % FINAL_V2)

    # ---- provenance ------------------------------------------------------
    freeze = _need(provenance_blob, "freeze_verification",
                   "PROVENANCE.json")
    main_env = _read("%s/determinism_summary.json" % FINAL_V2).get(
        "environment", {})
    prov.note("freeze tag", "%s/PROVENANCE.json" % FINAL_V2,
              "freeze_verification.freeze_tag", readme=True)
    prov.note("freeze commit", "%s/PROVENANCE.json" % FINAL_V2,
              "freeze_verification.freeze_commit", readme=True)
    prov.note("public commitment discharged", "%s/PROVENANCE.json" % FINAL_V2,
              "freeze_verification.public_commitment_discharged")
    prov.note("frozen file count", "%s/PROVENANCE.json" % FINAL_V2,
              "freeze_verification.frozen_file_count")
    prov.note("execution commit", "%s/determinism_summary.json" % FINAL_V2,
              "environment.git_commit")

    data = {
        "provenance": {
            "results_dir": FINAL_V2,
            "freeze_tag": freeze.get("freeze_tag"),
            "freeze_commit": freeze.get("freeze_commit"),
            "public_commitment_discharged": freeze.get(
                "public_commitment_discharged"),
            "frozen_file_count": freeze.get("frozen_file_count"),
            "execution_commit": main_env.get("git_commit"),
            "artifact_release": _artifact_release(),
        },
        "cases": {},
        "metrics": {},
        "determinism": {},
        "cross_platform": [],
        "monte_carlo": {},
        "verification": {},
    }

    # ---- case artifacts ---------------------------------------------------
    CASE_NAMES = {
        "case_a": "Investment research agent",
        "case_b": "Transaction authorization agent",
    }
    for case in ("case_a", "case_b"):
        source = "%s/%s/compilation.json" % (FINAL_V2, case)
        compilation = _result(source)
        stats = _need(compilation, "statistics", source)
        per_case = _need(metrics, "per_case.%s" % case,
                         "%s/metrics.json" % FINAL_V2)
        data["cases"][case] = {
            "name": CASE_NAMES[case],
            "case_class": compilation.get("case_class"),
            "risk_count": stats.get("risk_count"),
            "obligation_count": stats.get("obligation_count"),
            "predicate_count": stats.get("predicate_count"),
            "risk_derived_predicates": stats.get("risk_derived_predicate_count"),
            "invariant_predicates": stats.get("compiler_invariant_predicate_count"),
            "cstar_risk_count": stats.get("cstar_risk_count"),
            "dispositions": per_case.get("disposition_counts", {}),
            "bundle_sha256": compilation.get("payload_hash"),
            "declared_threshold": compilation.get("declared_heatmap_threshold"),
        }
        prov.note("Case %s bundle SHA-256" % case[-1].upper(), source,
                  "result.payload_hash", readme=True)
        prov.note("Case %s risk count" % case[-1].upper(), source,
                  "result.statistics.risk_count")
        prov.note("Case %s predicate count" % case[-1].upper(), source,
                  "result.statistics.predicate_count")
        prov.note("Case %s disposition counts" % case[-1].upper(),
                  "%s/metrics.json" % FINAL_V2,
                  "result.per_case.%s.disposition_counts" % case)
        prov.note("Case %s class" % case[-1].upper(), source,
                  "result.case_class")

    # ---- primary metrics ---------------------------------------------------
    for case in ("case_a", "case_b"):
        entry = {}
        for name in METRIC_ORDER:
            metric = _need(metrics, "per_case.%s.%s" % (case, name),
                           "%s/metrics.json" % FINAL_V2)
            entry[name] = {
                "value": metric["value"],
                "numerator": metric.get("numerator"),
                "denominator": metric.get("denominator"),
            }
            prov.note("%s (Case %s)" % (name, case[-1].upper()),
                      "%s/metrics.json" % FINAL_V2,
                      "result.per_case.%s.%s.value" % (case, name), readme=True)
        gd = _need(divergence, "per_case.%s" % case,
                   "%s/gate_divergence.json" % FINAL_V2)
        entry["GD"] = {"value": gd["GD_at_declared_threshold"],
                       "threshold": gd["declared_threshold"]}
        entry["GD_min"] = {"value": gd["GD_min"]}
        entry["register_rows"] = gd.get("register_row_count")
        prov.note("GD(T_H) (Case %s)" % case[-1].upper(),
                  "%s/gate_divergence.json" % FINAL_V2,
                  "result.per_case.%s.GD_at_declared_threshold" % case,
                  readme=True)
        prov.note("GD_min (Case %s)" % case[-1].upper(),
                  "%s/gate_divergence.json" % FINAL_V2,
                  "result.per_case.%s.GD_min" % case, readme=True)
        data["metrics"][case] = entry

    sweep = divergence.get("case_a_fixture_rating_sensitivity", {})
    data["metrics"]["gd_min_fixture_range"] = sweep.get("GD_min_range")
    prov.note("GD_min fixture-rating range", "%s/gate_divergence.json" % FINAL_V2,
              "result.case_a_fixture_rating_sensitivity.GD_min_range")

    # ---- determinism -------------------------------------------------------
    td = _need(determinism, "TD", "%s/determinism_summary.json" % FINAL_V2)
    data["determinism"] = {
        "TD": td["value"],
        "passed": td["numerator"],
        "total": td["denominator"],
        "failed": td["denominator"] - td["numerator"],
        "runs_per_case": determinism.get("runs_per_case"),
        "strata": determinism.get("stratum_breakdown", {}),
        "per_case": {
            case: {
                "TD": determinism["per_case"][case]["TD"]["value"],
                "matches": determinism["per_case"][case]["matches"],
                "runs": determinism["per_case"][case]["runs"],
                "reference_hash": determinism["per_case"][case]["reference_hash"],
            }
            for case in ("case_a", "case_b")
        },
    }
    for label, field in (("TD", "result.TD.value"),
                         ("TD passed / total",
                          "result.TD.numerator, result.TD.denominator"),
                         ("determinism runs per case", "result.runs_per_case"),
                         ("determinism strata", "result.stratum_breakdown")):
        prov.note(label, "%s/determinism_summary.json" % FINAL_V2, field,
                  readme=(label in ("TD", "TD passed / total",
                                    "determinism runs per case")))

    # ---- cross-platform ----------------------------------------------------
    data["cross_platform"] = _load_cross_platform(determinism, prov)

    # ---- Monte Carlo -------------------------------------------------------
    for case in ("case_a", "case_b"):
        source = "%s/monte_carlo_summary.json" % FINAL_V2
        mc = _need(monte, "per_case.%s" % case, source)
        data["monte_carlo"][case] = {
            "draws_K": mc["draws_K"],
            "rng_seed": mc.get("rng_seed"),
            "max_FP_heat": mc["max_FP_heat"]["value"],
            "max_FP_heat_risk": mc["max_FP_heat"].get("risk_id"),
            "max_FP_heat_mcse": mc["max_FP_heat"].get("mcse"),
            "max_FP_cstar": mc["max_FP_cstar"],
            "cstar_changes_observed": mc.get("cstar_membership_changes_observed"),
            "cstar_probe_draws": mc.get("cstar_probe_draws"),
        }
        prov.note("Monte Carlo K (Case %s)" % case[-1].upper(), source,
                  "result.per_case.%s.draws_K" % case, readme=True)
        prov.note("max FP_heat (Case %s)" % case[-1].upper(), source,
                  "result.per_case.%s.max_FP_heat.value" % case,
                  readme=(case == "case_a"))
        prov.note("max FP_C* (Case %s)" % case[-1].upper(), source,
                  "result.per_case.%s.max_FP_cstar" % case,
                  readme=True)
    data["monte_carlo"]["distributions_are"] = (
        "author-specified, prospectively frozen; NOT panel-adjudicated")
    prov.note("Monte Carlo MCSE (Case A)",
              "%s/monte_carlo_summary.json" % FINAL_V2,
              "result.per_case.case_a.max_FP_heat.mcse", readme=True)
    prov.note("C* membership changes observed",
              "%s/monte_carlo_summary.json" % FINAL_V2,
              "result.per_case.case_a.cstar_membership_changes_observed",
              readme=True)

    # ---- verification summary ----------------------------------------------
    corpus = _need(adversarial, "corpus", "%s/adversarial.json" % FINAL_V2)
    structural = _need(adversarial, "structural_checks",
                       "%s/adversarial.json" % FINAL_V2)
    seeds = adversarial.get("validation_seeds", {})
    injections = adversarial.get("case_b_injection_scenarios", {})
    totals = _need(properties, "totals", "%s/property_tests.json" % FINAL_V2)
    prop = _need(properties, "property_based", "%s/property_tests.json" % FINAL_V2)
    clean = _need(traceability, "clean", "%s/traceability_queries.json" % FINAL_V2)
    controls = _need(traceability, "negative_controls",
                     "%s/traceability_queries.json" % FINAL_V2)

    data["verification"] = {
        "tests_total": totals["tests"],
        "tests_passed": totals["passed"],
        "tests_failed": totals["failures"] + totals["errors"],
        "adversarial_passed": corpus["passed"],
        "adversarial_total": corpus["total"],
        "adversarial_negative": corpus["negative_cases"],
        "adversarial_positive": corpus["positive_controls"],
        "adversarial_code_mismatch": corpus["code_mismatch"],
        "structural_passed": structural["passed"],
        "structural_total": structural["total"],
        "validation_seeds_passed": seeds.get("passed"),
        "validation_seeds_total": seeds.get("total"),
        "injection_passed": injections.get("passed"),
        "injection_total": injections.get("scenario_count"),
        "property_count": prop["property_count"],
        "generated_examples": prop["total_generated_examples"],
        "clean_queries_per_case": len(clean.get("case_a", {})),
        "clean_queries_empty": all(
            q["empty"] for case in clean.values() for q in case.values()),
        "negative_controls_total": sum(len(v) for v in controls.values()),
        "negative_controls_detected": sum(
            1 for rows in controls.values() for row in rows
            if row.get("detected")),
        "freeze_checks": _read(FINAL_V2 + "/freeze_verification.json")["verified"],
        "paper_facing_results": _paper_facing_count(),
    }
    for label, source, field, in_readme in (
        ("test count", "%s/property_tests.json" % FINAL_V2,
         "result.totals.tests", True),
        ("adversarial corpus", "%s/adversarial.json" % FINAL_V2,
         "result.corpus.passed / .total", True),
        ("structural checks", "%s/adversarial.json" % FINAL_V2,
         "result.structural_checks.passed / .total", True),
        ("validation seeds", "%s/adversarial.json" % FINAL_V2,
         "result.validation_seeds.passed / .total", False),
        ("Case B injection scenarios", "%s/adversarial.json" % FINAL_V2,
         "result.case_b_injection_scenarios.passed / .scenario_count", False),
        ("property count", "%s/property_tests.json" % FINAL_V2,
         "result.property_based.property_count", True),
        ("generated examples", "%s/property_tests.json" % FINAL_V2,
         "result.property_based.total_generated_examples", True),
        ("clean traceability queries", "%s/traceability_queries.json" % FINAL_V2,
         "result.clean.<case>.Q1..Q6.empty", True),
        ("negative controls", "%s/traceability_queries.json" % FINAL_V2,
         "result.negative_controls.<case>[].detected", True),
        ("paper-facing results verified",
         "artifact_review/PAPER_RESULT_MAP.json", "entry_count", False),
    ):
        prov.note(label, source, field, readme=in_readme)

    prov.note("artifact release", "CITATION.cff", "version", readme=True)
    prov.note("result directory", "artifact_review/PAPER_RESULT_MAP.json", "results_dir", readme=True)
    prov.note("freeze verification", FINAL_V2 + "/freeze_verification.json", "verified, findings, frozen_files_changed_since_freeze")
    for case in ("case_a", "case_b"):
        source = FINAL_V2 + "/" + case + "/compilation.json"
        for field in ("obligation_count", "risk_derived_predicate_count", "compiler_invariant_predicate_count", "cstar_risk_count"):
            prov.note(case + " " + field, source, "result.statistics." + field)
        prov.note(case + " name", "tools/show_results.py", "CASE_NAMES (editorial label, not an empirical result)")
        prov.note(case + " GD threshold", FINAL_V2 + "/gate_divergence.json", "result.per_case." + case + ".declared_threshold", readme=True)
        for metric in METRIC_ORDER:
            prov.note(case + " " + metric + " fraction", FINAL_V2 + "/metrics.json", "result.per_case." + case + "." + metric + ".{numerator,denominator}")
        for field in ("rng_seed", "max_FP_heat.risk_id", "max_FP_heat.mcse", "cstar_probe_draws", "cstar_membership_changes_observed"):
            prov.note(case + " MC " + field, FINAL_V2 + "/monte_carlo_summary.json", "result.per_case." + case + "." + field)
        prov.note(case + " determinism counts", FINAL_V2 + "/determinism_summary.json", "result.per_case." + case + ".{matches,runs}")
    prov.note("TD failed", FINAL_V2 + "/determinism_summary.json", "result.TD.denominator - result.TD.numerator")
    prov.note("tests passed", FINAL_V2 + "/property_tests.json", "result.totals.passed", readme=True)
    prov.note("adversarial composition", FINAL_V2 + "/adversarial.json", "result.corpus.{negative_cases,positive_controls,code_mismatch}")
    data["_provenance_rows"] = prov.rows
    data["_consistency"] = _consistency(data)
    return data


def validate_evidence():
    """Check the packaged evidence inventory and the existing paper verifier.

    Inventory hashes detect missing/corrupt evidence, including CI legs and
    fields outside the paper map. The paper verifier additionally checks
    independently recorded counts, hashes and the freeze tag. No experiments run.
    """
    inventory = _read("MANIFEST.json")["files"]
    rows = [r for r in inventory if r["path"].startswith(FINAL_V2 + "/")]
    if not rows:
        raise MissingEvidence("MANIFEST.json has no final_v2 evidence inventory")
    for row in rows:
        path = Path(REPO_ROOT) / row["path"]
        if not path.is_file():
            raise MissingEvidence("required result file is missing: " + row["path"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
            raise MissingEvidence("evidence checksum mismatch: " + row["path"])
    # Import works both as a standalone script and as tools.show_results.
    if __package__:
        from . import verify_reported_results as verifier
    else:
        import verify_reported_results as verifier
    old_root = verifier.REPO_ROOT
    try:
        verifier.REPO_ROOT = REPO_ROOT
        mapping = _read("artifact_review/PAPER_RESULT_MAP.json")
        checks = verifier.verify_map(mapping["entries"]) + verifier.cross_checks()
    finally:
        verifier.REPO_ROOT = old_root
    failures = [c.label + ": " + c.detail for c in checks if not c.passed]
    freeze = _read(FINAL_V2 + "/freeze_verification.json")
    if not freeze["verified"] or freeze["findings"] or freeze["frozen_files_changed_since_freeze"]:
        failures.append("recorded freeze verification failed")
    if failures:
        raise MissingEvidence("; ".join(failures))


def _artifact_release():
    """The artifact release, read from CITATION.cff rather than hardcoded."""
    path = os.path.join(REPO_ROOT, "CITATION.cff")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("version:"):
                return "v" + line.split(":", 1)[1].strip()
    raise MissingEvidence("CITATION.cff: missing version")


def _paper_facing_count():
    path = os.path.join(REPO_ROOT, "artifact_review", "PAPER_RESULT_MAP.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle).get("entry_count")


def _load_cross_platform(determinism, prov):
    """Only environments that actually executed and left a result file."""
    legs = []
    reference = {c: determinism["per_case"][c]["reference_hash"]
                 for c in ("case_a", "case_b")}

    # the campaign host itself
    host_env = _read("%s/determinism_summary.json" % FINAL_V2).get(
        "environment", {})
    legs.append({
        "leg": "local host",
        "os": host_env.get("platform"),
        "arch": host_env.get("machine"),
        "python": host_env.get("python_version"),
        "TD": determinism["TD"]["value"],
        "hashes_match": True,
    })

    paths = sorted(glob.glob(os.path.join(
        REPO_ROOT, FINAL_V2, "cross_environment", "ci", "*",
        "determinism_summary.json")))
    container = os.path.join(
        REPO_ROOT, FINAL_V2, "cross_environment",
        "determinism_summary_container_linux.json")
    if os.path.exists(container):
        paths.append(container)

    for path in paths:
        with open(path, encoding="utf-8") as handle:
            blob = json.load(handle)
        env = blob.get("environment", {})
        result = blob.get("result", blob)
        name = os.path.basename(os.path.dirname(path))
        if name == "cross_environment":
            name = "pinned container"
        prov.note("cross-platform " + name, Path(path).relative_to(REPO_ROOT).as_posix(),
                  "environment.{platform,machine,python_version}; result.TD.value; result.per_case.*.reference_hash", readme=True)
        legs.append({
            "leg": name,
            "os": env.get("platform"),
            "arch": env.get("machine"),
            "python": env.get("python_version"),
            "TD": result["TD"]["value"],
            "hashes_match": all(
                result["per_case"][c]["reference_hash"] == reference[c]
                for c in ("case_a", "case_b")),
        })

    prov.note("cross-platform local host",
              FINAL_V2 + "/determinism_summary.json",
              "environment.{platform,machine,python_version}; result.TD.value", readme=True)
    prov.note("cross-platform environments",
              "%s/cross_environment/**/determinism_summary.json" % FINAL_V2,
              "environment.platform, .machine, .python_version; result.TD.value",
              readme=True)
    return legs


def _consistency(data):
    """Internal agreement checks over the values actually displayed.

    These are not a re-verification of the science -- ``freeze_check.py`` and
    ``verify_reported_results.py`` do that. They establish that the numbers this
    viewer is about to print agree with one another, so the presentation layer
    cannot show a self-contradictory report.
    """
    findings = []

    det = data["determinism"]
    if det["passed"] + det["failed"] != det["total"]:
        findings.append("determinism passed + failed != total")
    per_case_runs = sum(v["runs"] for v in det["per_case"].values())
    if per_case_runs != det["total"]:
        findings.append("per-case runs (%d) != TD denominator (%d)"
                        % (per_case_runs, det["total"]))
    if det["strata"] and sum(det["strata"].values()) != det["runs_per_case"]:
        findings.append("strata do not sum to runs_per_case")

    for case in ("case_a", "case_b"):
        bundle = data["cases"][case]["bundle_sha256"]
        if det["per_case"][case]["reference_hash"] != bundle:
            findings.append("%s determinism reference hash != bundle hash" % case)
        disp = data["cases"][case]["dispositions"]
        if disp and sum(disp.values()) != data["cases"][case]["risk_count"]:
            findings.append("%s dispositions do not sum to the risk count" % case)
        predicates = data["cases"][case]["predicate_count"]
        ptc = data["metrics"][case]["PTC"]["denominator"]
        if ptc != predicates:
            findings.append("%s PTC denominator != predicate count" % case)

    for leg in data["cross_platform"]:
        if leg["TD"] != 1.0 or not leg["hashes_match"]:
            findings.append("cross-platform leg %r does not agree" % leg["leg"])

    ver = data["verification"]
    for prefix in ("structural", "validation_seeds", "injection"):
        if ver[prefix + "_passed"] != ver[prefix + "_total"]:
            findings.append(prefix + " checks not fully passing")
    if ver["tests_passed"] != ver["tests_total"]:
        findings.append("test total does not equal passing tests")
    if ver["tests_failed"]:
        findings.append("%d test failures recorded" % ver["tests_failed"])
    if ver["adversarial_passed"] != ver["adversarial_total"]:
        findings.append("adversarial corpus not fully passing")
    if ver["negative_controls_detected"] != ver["negative_controls_total"]:
        findings.append("not every negative control fired")
    if not ver["clean_queries_empty"]:
        findings.append("a clean traceability query returned rows")

    return {"ok": not findings, "findings": findings}


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

WIDTH = 78


def _rule(char="="):
    return char * WIDTH


def _fmt(value, places=3):
    if value is None:
        return "—"
    if isinstance(value, float):
        return "%.*f" % (places, value)
    return str(value)


def render_text(data):
    out = []
    add = out.append

    add(_rule())
    add("GC-IR — REPORTABLE TIER-0 RESULTS")
    add(_rule())

    p = data["provenance"]
    add("")
    add("PROVENANCE")
    add("")
    add("  artifact release      %s" % (p["artifact_release"] or "—"))
    add("  scientific freeze     %s" % (p["freeze_tag"] or "—"))
    add("  freeze commit         %s" % (p["freeze_commit"] or "—"))
    add("  result directory      %s" % p["results_dir"])
    add("  execution commit      %s" % (p["execution_commit"] or "—"))
    add("  frozen files          %s" % (p["frozen_file_count"] or "—"))
    add("  public commitment     %s" % (
        "discharged" if p["public_commitment_discharged"] else "NOT discharged"))

    add("")
    add("CASE ARTIFACTS")
    for case in ("case_a", "case_b"):
        c = data["cases"][case]
        disp = c["dispositions"]
        add("")
        add("  Case %s — %s" % (case[-1].upper(), c["name"]))
        add("    class               %s" % c["case_class"])
        add("    register rows       %s" % c["risk_count"])
        add("    obligations         %s" % c["obligation_count"])
        add("    dispositions        %s runtime, %s non-runtime, "
            "%s accepted, %s unresolved"
            % (disp.get("runtime"), disp.get("nonruntime"),
               disp.get("accepted"), disp.get("unresolved")))
        add("    predicates          %s  (%s risk-derived, %s compiler invariant)"
            % (c["predicate_count"], c["risk_derived_predicates"],
               c["invariant_predicates"]))
        add("    C* rows             %s" % c["cstar_risk_count"])
        add("    bundle SHA-256")
        add("      %s" % c["bundle_sha256"])

    add("")
    add("PRIMARY METRICS")
    add("")
    a, b = data["metrics"]["case_a"], data["metrics"]["case_b"]
    add("  %-10s %18s %18s" % ("Metric", "Case A", "Case B"))
    add("  %s" % ("-" * 48))
    for name in METRIC_ORDER:
        add("  %-10s %18s %18s" % (
            name,
            "%s (%s/%s)" % (_fmt(a[name]["value"], 4), a[name]["numerator"],
                            a[name]["denominator"]),
            "%s (%s/%s)" % (_fmt(b[name]["value"], 4), b[name]["numerator"],
                            b[name]["denominator"])))
    add("  %-10s %18s %18s" % ("GD(%d)" % a["GD"]["threshold"],
                               a["GD"]["value"], b["GD"]["value"]))
    add("  %-10s %18s %18s" % ("GD_min", a["GD_min"]["value"],
                               b["GD_min"]["value"]))
    rng = data["metrics"].get("gd_min_fixture_range")
    if rng:
        add("")
        add("  Case A GD_min depends in part on documented fixture ratings;")
        add("  over all plausible values it would range from %s to %s."
            % (rng[0], rng[1]))

    add("")
    add("DETERMINISM")
    d = data["determinism"]
    add("")
    add("  TD                    %s" % _fmt(d["TD"]))
    add("  executions            %s" % d["total"])
    add("  passed                %s" % d["passed"])
    add("  failed                %s" % d["failed"])
    for case in ("case_a", "case_b"):
        pc = d["per_case"][case]
        add("  Case %s                %s/%s" % (case[-1].upper(), pc["matches"],
                                                pc["runs"]))
    add("  strata (per case)")
    for stratum in ("repeat", "row_shuffle", "key_shuffle", "locale", "timezone"):
        if stratum in d["strata"]:
            add("    %-18s %s" % (stratum, d["strata"][stratum]))

    add("")
    add("CROSS-PLATFORM")
    add("")
    add("  %-26s %-10s %-9s %-6s %s"
        % ("OS / environment", "arch", "CPython", "TD", "hashes"))
    add("  %s" % ("-" * 68))
    for leg in data["cross_platform"]:
        add("  %-26s %-10s %-9s %-6s %s"
            % (leg["os"].split("-")[0] + " / " + (leg["leg"] if leg["leg"] in ("local host", "pinned container") else "CI"), _clip(leg["arch"] or "—", 10),
               _clip(leg["python"] or "—", 9), _fmt(leg["TD"]),
               "match" if leg["hashes_match"] else "DIFFER"))
    add("")
    add("  Operating systems observed:")
    for os_name in sorted({(leg["os"] or "—").split("-")[0] for leg in
                           data["cross_platform"]}):
        add("    %s" % os_name)
    add("")
    add("  %d environments reproduced the committed reference hashes."
        % len(data["cross_platform"]))
    add("  This is determinism across the tested supported environments.")
    add("  It is NOT a claim of platform independence.")

    add("")
    add("MONTE CARLO")
    add("")
    add("  Distributions are %s." % data["monte_carlo"]["distributions_are"])
    for case in ("case_a", "case_b"):
        mc = data["monte_carlo"][case]
        add("")
        add("  Case %s" % case[-1].upper())
        add("    K                   %s" % format(mc["draws_K"], ","))
        add("    seed                %s" % mc["rng_seed"])
        add("    max FP_heat         %s  (risk %s)"
            % (_fmt(mc["max_FP_heat"], 6), mc["max_FP_heat_risk"]))
        add("    MCSE                %s" % _fmt(mc["max_FP_heat_mcse"], 6))
        add("    FP_C*               %s" % _fmt(mc["max_FP_cstar"], 6))
        if mc["cstar_changes_observed"] is not None:
            add("    C* changes observed %s in %s probe draws"
                % (mc["cstar_changes_observed"], mc["cstar_probe_draws"]))

    add("")
    add("TEST / VALIDATION SUMMARY")
    v = data["verification"]
    add("")
    add("  tests                     %s/%s passed"
        % (v["tests_passed"], v["tests_total"]))
    add("  adversarial corpus        %s/%s\n"
        "    %s negative, %s positive controls, %s code mismatches"
        % (v["adversarial_passed"], v["adversarial_total"],
           v["adversarial_negative"], v["adversarial_positive"],
           v["adversarial_code_mismatch"]))
    add("  structural checks         %s/%s"
        % (v["structural_passed"], v["structural_total"]))
    add("  validation seeds          %s/%s"
        % (v["validation_seeds_passed"], v["validation_seeds_total"]))
    add("  Case B injections         %s/%s → SAFE_STATE"
        % (v["injection_passed"], v["injection_total"]))
    add("  property tests            %s properties, %s generated examples"
        % (v["property_count"], format(v["generated_examples"], ",")))
    add("  traceability queries      %s clean queries per case, all empty"
        % v["clean_queries_per_case"])
    add("  negative controls         %s/%s fired"
        % (v["negative_controls_detected"], v["negative_controls_total"]))
    add("  freeze checks             recorded verification passed" if v["freeze_checks"] else "  freeze checks             FAILED")
    add("  ieee-check                no recorded machine-readable result")
    add("  paper-facing results      %s mapped and machine-verified"
        % v["paper_facing_results"])

    add("")
    add("CLAIM BOUNDARY")
    add("")
    for line in (
        "These results establish properties of the reference governance-to-control",
        "compiler and its two pinned case artifacts. They do not establish",
        "production detection performance, legal compliance, or superiority over",
        "unaided practitioners. RQ5 remains deferred.",
    ):
        add("  %s" % line)

    add("")
    add(_rule())
    consistency = data["_consistency"]
    if consistency["ok"]:
        add("REPORTABLE ARTIFACT VERIFIED")
        add("all displayed values are internally consistent and read from %s"
            % data["provenance"]["results_dir"])
    else:
        add("INCONSISTENT — the displayed values do not agree with one another")
        for finding in consistency["findings"]:
            add("  %s" % finding)
    add(_rule())
    return "\n".join(out)


def _clip(text, width):
    text = str(text)
    return text if len(text) <= width else text[:width - 1] + "…"


def headline(data):
    """The machine-readable projection. Same object, no second calculation."""
    return {
        "provenance": data["provenance"],
        "cases": data["cases"],
        "metrics": {
            case: {
                **{name: data["metrics"][case][name] for name in METRIC_ORDER},
                "GD": data["metrics"][case]["GD"],
                "GD_min": data["metrics"][case]["GD_min"],
            }
            for case in ("case_a", "case_b")
        },
        "gd_min_fixture_range": data["metrics"].get("gd_min_fixture_range"),
        "determinism": data["determinism"],
        "cross_platform": data["cross_platform"],
        "monte_carlo": data["monte_carlo"],
        "verification": data["verification"],
        "claim_boundary": (
            "These results establish properties of the reference "
            "governance-to-control compiler and its two pinned case artifacts. "
            "They do not establish production detection performance, legal "
            "compliance, or superiority over unaided practitioners. RQ5 remains "
            "deferred."),
        "consistent": data["_consistency"]["ok"],
        "findings": data["_consistency"]["findings"],
    }


def main(argv=None):
    # Preserve the complete plain-text report when redirected on Windows or
    # under an ASCII locale. Console and pipe output share UTF-8 bytes.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true",
                        help="emit the same values as JSON")
    args = parser.parse_args(argv)

    try:
        data = load_results()
    except (MissingEvidence, OSError, ValueError, KeyError, TypeError) as exc:
        print("ERROR: %s" % exc, file=sys.stderr)
        print("The reportable evidence under %s is incomplete; nothing was "
              "printed rather than showing a partial report." % FINAL_V2,
              file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(headline(data), indent=2, sort_keys=True))
    else:
        print(render_text(data))

    return 0 if data["_consistency"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
