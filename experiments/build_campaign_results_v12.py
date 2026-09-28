"""Development campaign summary (Paper 2 v1.2 spec section 11 / 21-shaped,
applied to the DEVELOPMENT phase only).

    python -m experiments.build_campaign_results_v12

Reads every results/development_v12/*.json file this generation's other
experiment modules already wrote and assembles one summary document. Every
section is explicitly marked "reportable": false -- development results are
never reportable numbers (spec section 16).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402

RESULTS_DIR = os.path.join(REPO_ROOT, "results", "development_v12")

SECTION_FILES = {
    "surface_a": "surface_a.json",
    "case_d": "case_d.json",
    "validators": "validators.json",
    "neutrality": "neutrality.json",
    "audit": "audit.json",
    "determinism_local": "determinism.json",
    "monte_carlo": "monte_carlo.json",
    "compile_timing": "compile_timing.json",
    "observation_diagnostics": "observation_diagnostics.json",
    "case_b_integration": "case_b_integration.json",
}


def _load(name):
    path = os.path.join(RESULTS_DIR, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def build():
    sections = {key: _load(filename) for key, filename in SECTION_FILES.items()}

    payload_hashes = {}
    if sections["case_d"]:
        for row in sections["case_d"]["result"]["rows"]:
            if row.get("payload_hash"):
                payload_hashes["case_d_%s" % row["id"]] = row["payload_hash"]
    if sections["determinism_local"]:
        for case_id, info in sections["determinism_local"]["result"]["per_case"].items():
            payload_hashes["determinism_reference_%s" % case_id] = info["reference_hash"]

    campaign = {
        "freeze": {"status": "NOT CREATED", "note": "preregister-tier0-v5 is explicitly not created by this pass; development phase only."},
        "release": {"status": "NOT CREATED", "note": "no v1.2.0 tag, no Zenodo publish."},
        "surface_a": sections["surface_a"]["result"] if sections["surface_a"] else None,
        "case_d": sections["case_d"]["result"] if sections["case_d"] else None,
        "validators": sections["validators"]["result"] if sections["validators"] else None,
        "neutrality": sections["neutrality"]["result"] if sections["neutrality"] else None,
        "tests": {"note": "see the final pytest run reported separately; not duplicated here to avoid a second, potentially stale, source of truth"},
        "audit": sections["audit"]["result"] if sections["audit"] else None,
        "determinism_local": sections["determinism_local"]["result"] if sections["determinism_local"] else None,
        "determinism_cross_environment": {"status": "NOT RUN", "note": "spec section 8: recommended but secondary; not run this pass"},
        "gate_deficit": {"note": "see audit.result.metrics (CV) and monte_carlo.result for GD/GDmin; not duplicated here"},
        "monte_carlo": sections["monte_carlo"]["result"] if sections["monte_carlo"] else None,
        "compile_timing": sections["compile_timing"]["result"] if sections["compile_timing"] else None,
        "diagnostic_a": sections["observation_diagnostics"]["result"]["diagnostic_a"] if sections["observation_diagnostics"] else None,
        "diagnostic_b": sections["observation_diagnostics"]["result"]["diagnostic_b"] if sections["observation_diagnostics"] else None,
        "case_b_integration": sections["case_b_integration"]["result"] if sections["case_b_integration"] else None,
        "payload_hashes": payload_hashes,
        "counting_distinctions": {
            "validator_test_matrix_count": 16,
            "new_v12_audit_negative_fixture_count": 9,
            "surface_a_family_count": 8,
            "note": (
                "Three distinct countings, never summed or substituted for one "
                "another: (1) validators.result.checks -- 16 rows, the full spec "
                "section 5 positive/negative pair per headline v1.2 validator; "
                "(2) audit.result.new_v12_negatives -- 9 rows, new fixtures added "
                "to the audit/regression corpus (spec sections 9-10), parallel to "
                "the historical 19 Q1-Q10 fixtures; (3) surface_a.result.families "
                "-- 8 rows, the spec section 2 paired semantic families. Each "
                "result file carries its own 'counting_note' with the full "
                "cross-reference."
            ),
        },
        "reportable": False,
        "phase_note": "DEVELOPMENT campaign summary. Not a reportable number, not a freeze, not a release. See the accompanying development report for the exact commands run and the actual pytest total.",
    }
    return campaign


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=RESULTS_DIR)
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    campaign = build()
    document = {
        "result_name": "campaign_results_development", "phase": "development",
        "phase_note": "DEVELOPMENT result; not reportable.",
        "environment": environment(), "result": campaign,
    }
    out_path = args.output or os.path.join(args.input, "campaign_results_development.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print("-> %s" % out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
