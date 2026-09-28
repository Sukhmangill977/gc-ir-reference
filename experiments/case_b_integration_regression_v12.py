"""Case-B integration regression (Paper 2 v1.2 spec section 14).

    python -m experiments.case_b_integration_regression_v12

Retains the existing 13 adverse + 1 clean = 14 rows, run as regression --
NOT counted as new translation-fidelity evidence. Uses the existing
``experiments.case_b_v11_injection_scenarios`` implementation unmodified.
Wording: "phase-aware reference evaluator implementing the downstream
authorization/release distinction" (spec section 14) -- not "translation
fidelity".
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402


def run():
    from experiments import case_b_v11_injection_scenarios as inj
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    result = compile_bundle(case.compiler_inputs())
    report = inj.run(result.bundle)
    report["wording"] = "phase-aware reference evaluator implementing the downstream authorization/release distinction"
    report["not_new_translation_fidelity_evidence"] = True
    report["row_count"] = report["scenario_count"]
    assert report["row_count"] == 14, "expected 13 adverse + 1 clean = 14 rows, got %d" % report["row_count"]
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run()
    document = {
        "result_name": "case_b_integration_regression_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "case_b_integration.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print("%d/%d rows passed (14 rows: 13 adverse + 1 clean)" % (report["passed"], report["scenario_count"]))
    print("-> %s" % out_path)
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
