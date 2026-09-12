"""Print the CURRENT release-facing result set for v1.1.0, read from
results/final_v4_1/ -- not results/final_v2/.

    python tools/show_results_v1_1_0.py
    python tools/show_results_v1_1_0.py --json

Sibling of tools/show_results.py, which remains scoped to results/final_v2/
and is not modified here (that historical campaign is unaffected and its
own display is unchanged; call it explicitly to see it, or run `make
results` which now prints both, current first).
"""

from __future__ import annotations

import argparse
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPAIGN_PATH = os.path.join(REPO_ROOT, "results", "final_v4_1", "campaign_results.json")


def load():
    with open(CAMPAIGN_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def render_text(data):
    lines = []
    add = lines.append
    add("=" * 78)
    add("CURRENT RELEASE -- v1.1.0 (results/final_v4_1/)")
    add("=" * 78)
    add("")
    add("Scientific freeze : %s" % data["freeze_tag"])
    add("Freeze commit     : %s" % data["freeze_commit"])
    add("Purpose           : %s" % data.get("purpose", ""))
    add("")
    add("CASE A")
    add("  hash   : %s (match: %s)" % (data["case_a_hash"]["actual"], data["case_a_hash"]["match"]))
    add("")
    add("CASE B v1.1")
    s = data["case_b_v1_1_structure"]
    add("  hash   : %s (match: %s)" % (data["case_b_v1_1_hash"]["actual"], data["case_b_v1_1_hash"]["match"]))
    add("  risks=%d  dispositions unchanged  ACS=%d  risk_derived_predicates=%d  "
        "invariants=%d  total_predicates=%d"
        % (s["risk_count"], s["acs_count"], s["risk_derived_predicate_count"],
           s["compiler_invariant_predicate_count"], s["predicate_count"]))
    add("")
    add("AUDIT")
    for case_id, q in data["audit_queries"].items():
        add("  %-14s Q1-Q10 %d/%d" % (case_id, q["passed"], q["total"]))
    add("  negative fixtures  %d/%d detected"
        % (data["negative_fixtures"]["detected"], data["negative_fixtures"]["total"]))
    add("")
    add("INJECTIONS (Case B v1.1, 13 scenarios)")
    add("  authorization_decision  %s" % data["case_b_v1_1_injections"]["authorization_decision_counts"])
    add("  release_decision        %s" % data["case_b_v1_1_injections"]["release_decision_counts"])
    add("  passed/failed           %d/%d"
        % (data["case_b_v1_1_injections"]["passed"], data["case_b_v1_1_injections"]["scenario_count"]))
    add("")
    add("DETERMINISM")
    add("  TD = %.3f  (%d/%d)" % (data["determinism"]["TD"]["value"],
                                    data["determinism"]["matches"], data["determinism"]["total_runs"]))
    add("")
    add("MONTE CARLO  K=%d seed=%d" % (data["monte_carlo"]["K"], data["monte_carlo"]["seed"]))
    add("  Case A      max FP_heat=%s" % data["monte_carlo"]["case_a_max_FP_heat"])
    add("  Case B v1.1 max FP_heat=%s  FP_C*=%s  GD_approved=%s  GD_min_mean=%s"
        % (data["monte_carlo"]["case_b_v1_1_max_FP_heat"], data["monte_carlo"]["case_b_v1_1_max_FP_cstar"],
           data["monte_carlo"]["case_b_v1_1_GD_approved"], data["monte_carlo"]["case_b_v1_1_GD_min_mean"]))
    add("")
    add("TESTS       %d passed, %d failed, %d errors, %d skipped"
        % (data["test_suite"]["tests"], data["test_suite"]["failures"],
           data["test_suite"]["errors"], data["test_suite"]["skipped"]))
    add("")
    add("ieee-check-v4        %s (%d stages)" % (data["ieee_check_v4"]["status"], data["ieee_check_v4"]["stage_count"]))
    fv = data["freeze_verification_prospective_v4"]
    add("freeze verification  %s (%d checks, %d failures)"
        % ("PASS" if fv["passed"] else "FAIL", fv["checks"], fv["failures"]))
    add("")
    add("L-DREA / ULB")
    ld = data["ldrea_ulb"]
    add("  pinned: %s @ %s" % (ld["pinned_repository"], ld["pinned_commit"]))
    add("  rows=%d  fraud_labelled=%d  false_permits=%d  false_denials=%d"
        % (ld["rows"], ld["fraud_labelled_rows"], ld["false_permit_count"], ld["false_denial_count"]))
    add("  original_experiment_reproduced=%s  new_v1_1_replay_executed=%s  fraud_detection_claim=%s"
        % (ld["original_experiment_reproduced"], ld["new_v1_1_replay_executed"], ld["fraud_detection_claim"]))
    add("  correspondence: %s" % ld["correspondence_summary"])
    add("")
    add("-" * 78)
    add("HISTORICAL (v1.0.5 / results/final_v2/): see `python tools/show_results.py` --")
    add("that campaign, its Bundle B (6 ACS) hash, and its own ieee-check status are")
    add("unchanged and reported separately; they are not this release's evidence.")
    add("=" * 78)
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.exists(CAMPAIGN_PATH):
        print("no results/final_v4_1/campaign_results.json -- run the v4.1 campaign first")
        return 1

    data = load()
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(render_text(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
