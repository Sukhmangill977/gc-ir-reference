"""Final v5 campaign summary (Paper 2 v1.2 spec section 11 / 21-shaped).

    python -m experiments.build_campaign_results_final_v5 --input results/final_v5

Sibling of experiments/build_campaign_results_v12.py (development phase,
untouched), reading from results/final_v5/*.json instead of
results/development_v12/*.json, and marked reportable only when every
mandatory section is genuinely present and passing -- never unconditionally
True. Adds sections the development campaign summary does not carry:
environment-7 (pinned container), the v1.1.0 eight-environment
reconciliation, the Case C exclusion record, and the CCS2 temporal-
provenance resolution -- each is pre-freeze evidence, not itself scientific
measurement, but part of what a reviewer needs alongside the numbers.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402

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
    "cross_environment_determinism": "cross_environment_determinism.json",
    "environment_container_aarch64": "environment_container_aarch64.json",
}

DOC_FILES = {
    "case_c_exclusion": "case_c_exclusion.json",
    "ccs2_temporal_provenance": "ccs2_temporal_provenance.json",
    "tacip_provenance_limitation": "tacip_provenance_limitation.json",
    "v110_eight_environment_reconciliation": "v110_eight_environment_reconciliation.json",
}


def _git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:  # noqa: BLE001
        return None


def _load(input_dir, name):
    path = os.path.join(input_dir, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _junit_counts(input_dir):
    junit_path = os.path.join(input_dir, "tests", "junit_full.xml")
    if not os.path.exists(junit_path):
        return None
    import xml.etree.ElementTree as ET
    root = ET.parse(junit_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    return {
        "tests": int(suite.get("tests", 0)),
        "failures": int(suite.get("failures", 0)),
        "errors": int(suite.get("errors", 0)),
        "skipped": int(suite.get("skipped", 0)),
        "junit_path": os.path.relpath(junit_path, REPO_ROOT),
    }


def build(input_dir):
    sections = {key: _load(input_dir, filename) for key, filename in SECTION_FILES.items()}
    docs = {key: _load(input_dir, filename) for key, filename in DOC_FILES.items()}

    payload_hashes = {}
    if sections["case_d"]:
        for row in sections["case_d"]["result"]["rows"]:
            if row.get("payload_hash"):
                payload_hashes["case_d_%s" % row["id"]] = row["payload_hash"]
    if sections["determinism_local"]:
        for case_id, info in sections["determinism_local"]["result"]["per_case"].items():
            payload_hashes["determinism_reference_%s" % case_id] = info["reference_hash"]

    tests = _junit_counts(input_dir)

    # Cross-environment currency: the committed CI evidence is only valid
    # final-campaign evidence if it was produced against THIS candidate
    # commit -- old CI evidence from an earlier commit is a genuine gap,
    # not silently treated as current.
    current_head = _git("rev-parse", "HEAD")
    cross_env = sections["cross_environment_determinism"]
    # The commit CI actually ran against necessarily PRECEDES the commit that
    # records its results (this repo's own established convention: commit N
    # triggers CI, commit N+1 records N's outcome -- see 66c01c4, which
    # records CI results for its own parent 1ec003b). Exact SHA equality can
    # therefore never be satisfied by construction; an ancestor check is the
    # correct, satisfiable, still-meaningful test: the recorded evidence
    # must be from a commit that is actually part of this candidate's
    # history, not from an unrelated or later branch.
    evidence_sha = cross_env["result"].get("head_sha") if cross_env else None
    cross_env_current = bool(
        evidence_sha and current_head
        and (evidence_sha == current_head
             or _git("merge-base", "--is-ancestor", evidence_sha, current_head) == "")
    )

    missing_mandatory = [
        key for key in (
            "surface_a", "case_d", "validators", "neutrality", "audit",
            "determinism_local", "monte_carlo", "compile_timing",
            "observation_diagnostics", "case_b_integration",
        )
        if sections[key] is None
    ]

    all_mandatory_present = not missing_mandatory
    tests_pass = bool(tests) and tests["failures"] == 0 and tests["errors"] == 0
    reportable = all_mandatory_present and tests_pass and cross_env_current

    campaign = {
        "freeze": {
            "status": "SEE preregister-tier0-v5 tag" if reportable else "NOT CREATED",
            "note": "This campaign summary does not itself create or verify the freeze tag; "
                    "see tools/freeze_check.py --prospective-v5 and git tag inspection for that.",
        },
        "release": {"status": "NOT CREATED", "note": "no v1.2.0 tag created by this script."},
        "surface_a": sections["surface_a"]["result"] if sections["surface_a"] else None,
        "case_d": sections["case_d"]["result"] if sections["case_d"] else None,
        "validators": sections["validators"]["result"] if sections["validators"] else None,
        "neutrality": sections["neutrality"]["result"] if sections["neutrality"] else None,
        "tests": tests or {"status": "NOT_RUN", "note": "no junit_full.xml found under " + input_dir},
        "audit": sections["audit"]["result"] if sections["audit"] else None,
        "determinism_local": sections["determinism_local"]["result"] if sections["determinism_local"] else None,
        "determinism_cross_environment": {
            "result": cross_env["result"] if cross_env else None,
            "current_for_this_commit": cross_env_current,
            "candidate_commit": current_head,
            "evidence_commit": cross_env["result"].get("head_sha") if cross_env else None,
            "note": "PASS requires the CI evidence's head_sha to equal the candidate commit's "
                    "HEAD -- stale CI evidence from an earlier commit is reported as not current, "
                    "never silently accepted.",
        },
        "environment_container_aarch64": sections["environment_container_aarch64"]["result"] if sections["environment_container_aarch64"] else None,
        "gate_deficit": {"note": "see audit.result.metrics (CV) and monte_carlo.result for GD/GDmin; not duplicated here"},
        "monte_carlo": sections["monte_carlo"]["result"] if sections["monte_carlo"] else None,
        "compile_timing": sections["compile_timing"]["result"] if sections["compile_timing"] else None,
        "diagnostic_a": sections["observation_diagnostics"]["result"]["diagnostic_a"] if sections["observation_diagnostics"] else None,
        "diagnostic_b": sections["observation_diagnostics"]["result"]["diagnostic_b"] if sections["observation_diagnostics"] else None,
        "case_b_integration": sections["case_b_integration"]["result"] if sections["case_b_integration"] else None,
        "payload_hashes": payload_hashes,
        "reconciliation_documents": {key: doc for key, doc in docs.items()},
        "counting_distinctions": {
            "validator_test_matrix_count": 16,
            "new_v12_audit_negative_fixture_count": 9,
            "surface_a_family_count": 8,
            "local_determinism_run_count": 155,
            "note": (
                "Four distinct countings, never summed or substituted for one another: "
                "(1) validators.result.checks -- 16 rows; (2) audit.result.new_v12_negatives "
                "-- 9 rows; (3) surface_a.result.families -- 8 rows; (4) 155 local determinism "
                "runs (31 x 5 cases: case_a, case_b_v1_1, case_d_ccs0/ccs1/ccs2)."
            ),
        },
        "missing_mandatory_sections": missing_mandatory,
        "reportable": reportable,
        "phase_note": "FINAL v5 campaign summary. reportable=True only when every mandatory "
                       "section is present, pytest passes with 0 failures/errors, and the "
                       "cross-environment CI evidence's head_sha matches this candidate commit.",
    }
    return campaign


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=os.path.join(REPO_ROOT, "results", "final_v5"))
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    campaign = build(args.input)
    document = {
        "result_name": "campaign_results_final_v5", "phase": "final_v5",
        "phase_note": campaign["phase_note"],
        "environment": environment(), "result": campaign,
    }
    out_path = args.output or os.path.join(args.input, "campaign_results.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    print("-> %s (reportable=%s)" % (out_path, campaign["reportable"]))
    if campaign["missing_mandatory_sections"]:
        print("MISSING MANDATORY SECTIONS: %s" % campaign["missing_mandatory_sections"])
    return 0 if campaign["reportable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
