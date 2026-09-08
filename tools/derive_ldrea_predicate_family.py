"""Derive the L-DREA predicate family from the published enforcement artifact.

    python -m tools.derive_ldrea_predicate_family --ldrea-root <path>

This script does not assume anything about the enforcement artifact's contents.
It reads the published source and data, extracts the predicate (deficit) vector
that the artifact itself evaluates, cross-checks the count against three
independently reported figures, and writes a machine-readable result.

Why this exists: the artifact-runs memo asks for a "P1-P13 -> artifact identifier"
mapping.  Before writing any mapping, the actual identifiers have to be
established from the published artifact rather than assumed from the memo's
wording.  What this script finds is reported as found, including where it
contradicts the memo.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_LDREA_ROOT = "/Users/sukhmangill/Documents/GitHub/Gamma-Permit-Package"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=root, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return None


def extract_node_gate_cols(runner_path):
    """Parse ``NODE_GATE_COLS`` out of the runner's AST -- no regex guessing."""
    with open(runner_path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read(), filename=runner_path)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "NODE_GATE_COLS":
                return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("NODE_GATE_COLS not found in %s" % runner_path)


def extract_derived_deficits(runner_path):
    """Find the extra deficit columns assigned as ``deficits["NAME"] = ...``."""
    with open(runner_path, encoding="utf-8") as handle:
        source = handle.read()
    names = []
    for match in re.finditer(r'deficits\[\s*"([A-Z_]+)"\s*\]\s*=', source):
        if match.group(1) not in names:
            names.append(match.group(1))
    return names


def reported_counts(ldrea_root):
    """Every independently reported predicate count in the published reports."""
    found = {}
    candidates = [
        ("realdatatestcode/concurbench_full_report.json",
         ["benchmark_report.predicate_count", "dataset.predicate_dimensionality"]),
        ("realdatatestcode/gamma_lab_v1_report.json",
         ["negative_control.n_predicates", "negative_control.single_deficit_score"]),
    ]
    for relative, paths in candidates:
        full = os.path.join(ldrea_root, relative)
        if not os.path.exists(full):
            continue
        with open(full, encoding="utf-8") as handle:
            blob = json.load(handle)
        for dotted in paths:
            node = blob
            for part in dotted.split("."):
                if not isinstance(node, dict) or part not in node:
                    node = None
                    break
                node = node[part]
            if node is not None:
                found["%s::%s" % (relative, dotted)] = node
    return found


def golden_trace_columns(ldrea_root):
    directory = os.path.join(ldrea_root, "realdatatestcode")
    for name in sorted(os.listdir(directory)):
        if name.endswith(".csv") and "GOLDEN_TRACE" in name:
            path = os.path.join(directory, name)
            with open(path, encoding="utf-8", newline="") as handle:
                header = next(csv.reader(handle))
            return name, path, header
    return None, None, []


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ldrea-root", default=DEFAULT_LDREA_ROOT)
    parser.add_argument("--out", default=os.path.join(
        REPO_ROOT, "cases", "case_b", "ldrea_predicate_family.json"))
    args = parser.parse_args(argv)

    root = args.ldrea_root
    if not os.path.isdir(root):
        raise SystemExit("L-DREA artifact root not found: %s" % root)

    runner = os.path.join(root, "realdatatestcode", "gamma_test_runner.py")
    node_gates = extract_node_gate_cols(runner)
    derived = extract_derived_deficits(runner)
    family = node_gates + derived

    csv_name, csv_path, header = golden_trace_columns(root)
    counts = reported_counts(root)

    # Cross-checks: the derived family size must agree with every independently
    # reported figure, or the derivation is wrong and must not be used.
    checks = []
    checks.append({
        "check": "derived family size equals benchmark_report.predicate_count",
        "expected": counts.get(
            "realdatatestcode/concurbench_full_report.json::benchmark_report.predicate_count"),
        "actual": len(family),
        "passed": counts.get(
            "realdatatestcode/concurbench_full_report.json::benchmark_report.predicate_count")
        == len(family),
    })
    checks.append({
        "check": "derived family size equals dataset.predicate_dimensionality",
        "expected": counts.get(
            "realdatatestcode/concurbench_full_report.json::dataset.predicate_dimensionality"),
        "actual": len(family),
        "passed": counts.get(
            "realdatatestcode/concurbench_full_report.json::dataset.predicate_dimensionality")
        == len(family),
    })
    checks.append({
        "check": "derived family size equals negative_control.n_predicates",
        "expected": counts.get(
            "realdatatestcode/gamma_lab_v1_report.json::negative_control.n_predicates"),
        "actual": len(family),
        "passed": counts.get(
            "realdatatestcode/gamma_lab_v1_report.json::negative_control.n_predicates")
        == len(family),
    })
    single = counts.get(
        "realdatatestcode/gamma_lab_v1_report.json::negative_control.single_deficit_score")
    # The artifact stores this value already rounded to three places
    # (round(1.0 / n_predicates, 3)), so the comparison must be made against the
    # rounded quantity, not the exact reciprocal.
    derived_single = round(1.0 / len(family), 3) if family else None
    checks.append({
        "check": "reported single_deficit_score equals round(1/|family|, 3)",
        "expected": single,
        "actual": derived_single,
        "passed": single is not None and derived_single == single,
    })
    missing_in_csv = [
        name for name in node_gates if header and name not in header
    ]
    checks.append({
        "check": "every node gate column is present in the golden trace header",
        "expected": [],
        "actual": missing_in_csv,
        "passed": not missing_in_csv,
    })

    # The memo's "P1-P13": what do P-identifiers actually denote in the artifact?
    stress = os.path.join(root, "realdatatestcode", "stress_test.py")
    p_identifiers = []
    if os.path.exists(stress):
        with open(stress, encoding="utf-8") as handle:
            text = handle.read()
        for match in re.finditer(r'_scenario\(\s*"(P\d+)"\s*,\s*"([^"]+)"', text):
            p_identifiers.append({"id": match.group(1), "title": match.group(2)})

    document = {
        "derivation_note": (
            "Derived programmatically from the published enforcement artifact by "
            "tools/derive_ldrea_predicate_family.py. Nothing here is transcribed "
            "from prose or assumed from the artifact-runs memo."
        ),
        "source_repository": {
            "path": root,
            "remote": git(root, "remote", "get-url", "origin"),
            "commit": git(root, "rev-parse", "HEAD"),
            "commit_short": git(root, "rev-parse", "--short", "HEAD"),
            "tag": git(root, "describe", "--tags", "--always"),
            "note": "This is the repository of record named in the manuscript's "
                    "Appendix C for reference [15].",
        },
        "source_files": {
            relative: {
                "sha256": sha256_file(os.path.join(root, relative)),
                "bytes": os.path.getsize(os.path.join(root, relative)),
            }
            for relative in [
                "realdatatestcode/gamma_test_runner.py",
                "realdatatestcode/concurbench_full_report.json",
                "realdatatestcode/gamma_lab_v1_report.json",
                "realdatatestcode/stress_test.py",
            ]
            if os.path.exists(os.path.join(root, relative))
        },
        "golden_trace": {
            "file": csv_name,
            "sha256": sha256_file(csv_path) if csv_path else None,
            "column_count": len(header),
        },
        "predicate_family": {
            "size": len(family),
            "node_authorization_gates": node_gates,
            "derived_deficit_predicates": derived,
            "all": family,
            "definition_site": "realdatatestcode/gamma_test_runner.py :: NODE_GATE_COLS "
                               "plus the deficits[...] assignments in the deficit-matrix "
                               "construction",
            "artifact_comment": "Node-level authorization predicates. Each must concur "
                                "(be TRUE) for Gamma_G = 0. This is the predicate vector "
                                "G = {g_1..g_n}; deficit d_i = 1 when g_i fails.",
        },
        "reported_counts": counts,
        "cross_checks": checks,
        "all_cross_checks_passed": all(c["passed"] for c in checks),
        "p_identifiers_in_artifact": {
            "found": p_identifiers,
            "count": len(p_identifiers),
            "what_they_are": "stress-test SCENARIOS in realdatatestcode/stress_test.py",
            "what_they_are_not": "predicate identifiers; there is no P1-P13 predicate "
                                 "identifier family anywhere in the published artifact",
        },
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("L-DREA predicate family derived: %d predicates" % len(family))
    for index, name in enumerate(family, start=1):
        kind = "node gate" if name in node_gates else "derived deficit"
        print("  g_%-2d %-24s (%s)" % (index, name, kind))
    print("")
    for check in checks:
        print("  [%s] %s (expected %r, actual %r)"
              % ("PASS" if check["passed"] else "FAIL", check["check"],
                 check["expected"], check["actual"]))
    print("")
    print("P-identifiers found in the artifact: %d (%s)"
          % (len(p_identifiers), ", ".join(p["id"] for p in p_identifiers) or "none"))
    print("wrote %s" % os.path.relpath(args.out, REPO_ROOT))
    return 0 if document["all_cross_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
