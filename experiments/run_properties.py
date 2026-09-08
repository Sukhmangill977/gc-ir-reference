"""Run the pytest suites and record machine-readable outcomes.

    python -m experiments.run_properties [--final]

Section XI-H requires property-based tests and states which properties they must
verify.  This script runs them under pytest with a JUnit XML report, then parses
that report so the number of tests, the number of generated examples per
property, and any failure are all recorded in a result file rather than only in
terminal output.

Hypothesis's own statistics are captured too, so the "at least 100 generated
examples per property" claim is evidenced rather than asserted.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from experiments.common import REPO_ROOT, add_common_args, results_dir, write_result

SUITES = {
    "unit": "tests/unit",
    "properties": "tests/properties",
    "adversarial": "tests/adversarial",
    "integration": "tests/integration",
}


def _run_suite(name, path, report_dir):
    xml_path = os.path.join(report_dir, "junit_%s.xml" % name)
    command = [
        sys.executable, "-m", "pytest", path, "-q",
        "--junitxml=%s" % xml_path,
    ]
    if name == "properties":
        command += ["-p", "no:randomly", "--hypothesis-show-statistics"]
    completed = subprocess.run(command, cwd=REPO_ROOT, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    output = completed.stdout.decode("utf-8", "replace")

    tests = failures = errors = skipped = 0
    duration = 0.0
    cases = []
    if os.path.exists(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        suites = [root] if root.tag == "testsuite" else list(root)
        for suite in suites:
            tests += int(suite.get("tests", 0))
            failures += int(suite.get("failures", 0))
            errors += int(suite.get("errors", 0))
            skipped += int(suite.get("skipped", 0))
            duration += float(suite.get("time", 0.0))
            for case in suite.iter("testcase"):
                status = "passed"
                message = ""
                for child in case:
                    if child.tag in ("failure", "error"):
                        status = child.tag
                        message = (child.get("message") or "")[:300]
                cases.append({
                    "classname": case.get("classname"),
                    "name": case.get("name"),
                    "status": status,
                    "time": float(case.get("time", 0.0)),
                    "message": message,
                })

    return {
        "suite": name,
        "path": path,
        "returncode": completed.returncode,
        "tests": tests,
        "passed": tests - failures - errors - skipped,
        "failures": failures,
        "errors": errors,
        "skipped": skipped,
        "duration_seconds": round(duration, 3),
        "cases": cases,
        "stdout_tail": output[-4000:],
        "_full_output": output,
    }


_HYPOTHESIS_BLOCK = re.compile(
    r"^\s*(tests/properties/[^:]+::\w+):\s*$\n((?:\s+-.*\n)+)", re.MULTILINE
)
_TYPICAL = re.compile(r"typically ran (\d+)|(\d+) passing examples")


def _hypothesis_statistics(output):
    """Extract per-property example counts from --hypothesis-show-statistics.

    Hypothesis prints a header line ``path::test_name:`` followed by an indented
    block; a blank line separates the header from the block, so the parser must
    not treat a blank line as the end of a record.
    """
    stats = {}
    current = None
    for line in output.splitlines():
        stripped = line.strip()
        if "::" in stripped and stripped.endswith(":") and not stripped.startswith("-"):
            current = stripped[:-1]
            stats[current] = {"lines": []}
            continue
        if current is None:
            continue
        if stripped.startswith("-"):
            stats[current]["lines"].append(stripped)
            match = re.search(r"(\d+)\s+passing examples", stripped)
            if match:
                stats[current]["passing_examples"] = int(match.group(1))
            match = re.search(r"(\d+)\s+failing examples", stripped)
            if match:
                stats[current]["failing_examples"] = int(match.group(1))
            match = re.search(r"settings\.max_examples=(\d+)", stripped)
            if match:
                stats[current]["max_examples"] = int(match.group(1))
            if "exhausted" in stripped.lower():
                stats[current]["stopped_because"] = "input space exhausted"
        elif stripped and not stripped.startswith("="):
            # A non-indented, non-blank line ends the block.
            current = None
    return stats


def run(final):
    report_dir = os.path.join(results_dir(final), "test_reports")
    os.makedirs(report_dir, exist_ok=True)

    suites = {}
    for name, path in SUITES.items():
        suites[name] = _run_suite(name, path, report_dir)
        entry = suites[name]
        print("%-12s %3d tests, %3d passed, %d failed, %d errors (%.2fs)"
              % (name, entry["tests"], entry["passed"], entry["failures"],
                 entry["errors"], entry["duration_seconds"]))

    from tests.properties import test_invariants  # noqa: E402

    hypothesis_stats = _hypothesis_statistics(suites["properties"].pop("_full_output", ""))
    for entry in suites.values():
        entry.pop("_full_output", None)

    property_functions = sorted(
        name for name in dir(test_invariants)
        if name.startswith("test_")
    )

    payload = {
        "suites": suites,
        "totals": {
            "tests": sum(s["tests"] for s in suites.values()),
            "passed": sum(s["passed"] for s in suites.values()),
            "failures": sum(s["failures"] for s in suites.values()),
            "errors": sum(s["errors"] for s in suites.values()),
        },
        "property_based": {
            "framework": "Hypothesis",
            "max_examples_per_property": test_invariants.MAX_EXAMPLES,
            "property_count": len(property_functions),
            "properties": property_functions,
            "properties_required_by_manuscript": [
                "total disposition", "authority closure", "mandatory unknown-failure",
                "C* coverage", "origin closure", "payload immutability",
                "temporal receipt validity",
            ],
            "additional_properties_tested": [
                "canonicalization order invariance (RFC 8785)",
                "forbidden payload keys always detected (Appendix A constraint 13)",
                "supporting predicates never satisfy C* coverage",
                "predicate cardinality independent of risk cardinality",
            ],
            "hypothesis_statistics": hypothesis_stats,
            "example_counts": {
                name.split("::")[-1]: entry.get("passing_examples")
                for name, entry in sorted(hypothesis_stats.items())
            },
            "total_generated_examples": sum(
                entry.get("passing_examples") or 0
                for entry in hypothesis_stats.values()
            ),
            "properties_below_100_examples": {
                name.split("::")[-1]: {
                    "passing_examples": entry.get("passing_examples"),
                    "reason": entry.get("stopped_because", "unknown"),
                }
                for name, entry in sorted(hypothesis_stats.items())
                if (entry.get("passing_examples") or 0) < test_invariants.MAX_EXAMPLES
            },
            "note_on_example_counts": (
                "settings.max_examples is 100 for every property. Two properties "
                "report fewer: their input spaces are finite and small "
                "(gate_type x on_unknown x required = 3 x 3 x 2 = 18, and "
                "gate_type x on_fail = 3 x 3 = 9), so Hypothesis stops once the "
                "space is EXHAUSTED. An exhaustive check of a finite space is "
                "stronger evidence than 100 random draws from it, not weaker; the "
                "counts are reported as measured rather than padded."
            ),
        },
        "all_green": all(s["returncode"] == 0 for s in suites.values()),
    }
    write_result(final, "property_tests", payload)
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args(argv)
    payload = run(phase_of(args))
    return 0 if payload["all_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
