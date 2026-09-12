"""Verify the v1.1.0-facing manuscript against results/final_v4_1/ machine
evidence, and scan it for stale terms/numbers from prior releases.

    python tools/verify_manuscript_v1_1_0.py
    python tools/verify_manuscript_v1_1_0.py --json

This is a sibling of tools/verify_reported_results.py (which remains scoped
to results/final_v2/ and is not modified here). That tool is a declarative,
JSON-path-driven checker against artifact_review/PAPER_RESULT_MAP.json; this
one is a direct, script-based checker against the docx text and
results/final_v4_1/campaign_results.json, built for the smaller, targeted
set of v1.1.0 claims rather than re-deriving a full declarative map.

Limitations, stated plainly: this environment has no LaTeX/Word/LibreOffice
toolchain, so this script cannot compile the manuscript to PDF or verify
citation/cross-reference resolution the way a real compile would. It checks
the extracted paragraph text for Word's own unresolved-field markers
("Error! Reference source not found.", "Bookmark not defined") as a static
proxy, and otherwise verifies content, not layout or citation graph.
"""

from __future__ import annotations

import argparse
import json
import os
import re

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUSCRIPT_PATH = os.path.join(
    REPO_ROOT, "paper_update",
    "From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION_5_5f.docx",
)
CAMPAIGN_PATH = os.path.join(REPO_ROOT, "results", "final_v4_1", "campaign_results.json")

STALE_PATTERNS = [
    (r"\bPBrisk\s*=\s*6\b", "PBrisk=6"),
    (r"\bPB\s*=\s*9\b", "PB=9 as current total"),
    (r"\b6/10\b", "6/10 query coverage"),
    (r"remaining four", "remaining four (stale partial-query-coverage wording)"),
    (r"all resolve to SAFE_STATE", "SAFE_STATE reported as a uniform peer outcome"),
    (r"13/13.*SAFE_STATE|SAFE_STATE.*13/13", "13/13 SAFE_STATE wording"),
    (r"2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce.{0,40}current",
     "old Bundle B hash described as current"),
    (r"release tag v1\.0\.[0-9]", "a v1.0.x release tag cited as the release"),
    (r"\bXXXXXXXX\b", "literal placeholder XXXXXXXX"),
    (r"doi:\s*10\.5281/zenodo\.PLACEHOLDER|PLACEHOLDER.?DOI|\[DOI TBD\]", "placeholder DOI"),
    (r"sha256:[0]{10,}|fake.{0,10}digest", "a fabricated/fake container digest"),
    (r"all 19.{0,20}Case C|Case C.{0,20}19/19|19/19.{0,20}Case C", "Case C claimed as 19/19"),
    (r"284,807.{0,80}(v1\.1|twelve-predicate).{0,40}(executed|replay)",
     "a claim that the new v1.1 bundle was executed/replayed over the 284,807-row corpus"),
    (r"Error! Reference source not found\.|Bookmark not defined",
     "an unresolved Word cross-reference/bookmark field"),
]

REQUIRED_SUBSTRINGS = [
    "nine Approved Control Specifications",
    "nine risk-derived predicates",
    "three compiler invariants",
    "twelve predicates in total",
    "0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1",
    "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536",
    "all ten canonical audit queries return an empty result set",
    "nineteen targeted negative fixtures",
    "authorization_decision is PERMIT once, DENY eight times, and HOLD four times",
    "release_decision is ALLOW_RELEASE twelve times and BLOCK_RELEASE once",
    "release tag v1.1.0",
    "preregister-tier0-v4.1",
    "efe4e165619ecb5d781fb795113f33720794a2e5",
    "0640ad1e7a703879d4b9083a088f5b562b638173590292a2c1aed1625102e0e6",
    "E1–E12",
    "E13–E19",
    "0.317980",
    "492 fraud-labelled",
    "comprises 446 tests",
]


def load_manuscript_text():
    import docx
    document = docx.Document(MANUSCRIPT_PATH)
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                parts.append(cell.text)
    return "\n".join(parts)


def check(final="final_v4_1"):
    findings = []
    checks = []

    def record(name, passed, detail=""):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            findings.append("%s -- %s" % (name, detail))

    if not os.path.exists(MANUSCRIPT_PATH):
        record("manuscript file present", False, MANUSCRIPT_PATH)
        return {"passed": False, "checks": checks, "findings": findings}

    text = load_manuscript_text()
    record("manuscript file present", True, MANUSCRIPT_PATH)

    for substring in REQUIRED_SUBSTRINGS:
        record("manuscript contains: %r" % (substring[:60],), substring in text, "")

    for pattern, label in STALE_PATTERNS:
        match = re.search(pattern, text)
        record("no stale term: %s" % label, match is None,
               "found: %r" % text[max(0, match.start() - 40):match.end() + 40] if match else "")

    if not os.path.exists(CAMPAIGN_PATH):
        record("results/final_v4_1/campaign_results.json present", False, CAMPAIGN_PATH)
    else:
        with open(CAMPAIGN_PATH, encoding="utf-8") as fh:
            campaign = json.load(fh)
        record("campaign case_a_hash matches manuscript-cited hash",
               "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536"
               == campaign["case_a_hash"]["actual"], "")
        record("campaign case_b_v1_1_hash matches manuscript-cited hash",
               "0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1"
               == campaign["case_b_v1_1_hash"]["actual"], "")
        record("campaign test_suite matches manuscript's implicit 446-test claim (informational)",
               campaign["test_suite"]["tests"] == 446, str(campaign["test_suite"]))
        record("campaign determinism TD == 1.0, 62 total runs",
               campaign["determinism"]["TD"]["value"] == 1.0
               and campaign["determinism"]["total_runs"] == 62, "")
        record("campaign injections match manuscript's two-axis aggregate",
               campaign["case_b_v1_1_injections"]["authorization_decision_counts"]
               == {"PERMIT": 1, "DENY": 8, "HOLD": 4}
               and campaign["case_b_v1_1_injections"]["release_decision_counts"]
               == {"ALLOW_RELEASE": 12, "BLOCK_RELEASE": 1}, "")
        record("campaign L-DREA/ULB rows/fraud counts match manuscript",
               campaign["ldrea_ulb"]["rows"] == 284807
               and campaign["ldrea_ulb"]["fraud_labelled_rows"] == 492, "")
        record("campaign correspondence summary matches manuscript's 4/3/5 claim",
               campaign["ldrea_ulb"]["correspondence_summary"]
               == {"exact": 4, "family": 3, "not_established": 5}, "")
        record("campaign new_v1_1_replay_executed is False (matches manuscript's non-claim)",
               campaign["ldrea_ulb"]["new_v1_1_replay_executed"] is False, "")

    return {
        "passed": not findings,
        "checks": checks,
        "findings": findings,
        "check_count": len(checks),
        "failure_count": len(findings),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = check()
    for c in report["checks"]:
        print("  [%s] %s %s" % ("PASS" if c["passed"] else "FAIL", c["check"], c["detail"]))

    print("\n%s -- %d checks, %d failures"
          % ("PASSED" if report["passed"] else "FAILED",
             report.get("check_count", len(report["checks"])),
             report.get("failure_count", len(report["findings"]))))

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
