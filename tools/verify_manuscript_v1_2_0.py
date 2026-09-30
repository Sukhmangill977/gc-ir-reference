"""Verify the manuscript's v1.2-facing claims against machine-readable v1.2
evidence, and scan it for stale/placeholder terms.

    python tools/verify_manuscript_v1_2_0.py
    python tools/verify_manuscript_v1_2_0.py --json
    python tools/verify_manuscript_v1_2_0.py --campaign results/final_v5/campaign_results.json

Sibling of tools/verify_manuscript_v1_1_0.py (unmodified, still scoped to
results/final_v4_1/). This checker is SCAFFOLDING, written ahead of the
manuscript content it verifies: as of the commit that adds this file, the
manuscript (paper_update/..._SUBMISSION_5_5f.docx) contains NO v1.2 section
at all -- no Case D, no Surface A, no validator-matrix, no v1.2 numbers.
Every REQUIRED_SUBSTRINGS check below is therefore EXPECTED to fail until
those sections are authored (an authorial task, deliberately out of scope
for this script -- see docs/ for the gap this file exists to eventually
close). Running this script now and seeing failures is not a defect in the
script; it is the script doing its job: proving the manuscript does not yet
say what it does not yet say.

Once the v1.2 sections are written, re-run this script. Each required
substring below is copied verbatim from an already-verified v1.2 artifact
(results/development_v12/*.json, or results/final_v5/campaign_results.json
once that exists), so a PASS here means the manuscript text matches machine
evidence, not that the checker was loosened to match whatever the
manuscript happens to say.

By default this script checks manuscript numbers against
results/development_v12/campaign_results_development.json, since no
results/final_v5/ exists yet. That file is explicitly phase="development" /
reportable=False -- it is NOT a substitute for a real freeze verification,
and this script's PASS does not by itself mean the manuscript is submission-
ready. Pass --campaign results/final_v5/campaign_results.json once a v5
freeze exists, to check against the real reportable campaign instead.

Limitations, stated plainly (same as verify_manuscript_v1_1_0.py): this
environment has no LaTeX/Word/LibreOffice toolchain, so this script checks
extracted paragraph/table text, not layout or the citation graph. It also
checks for Word's own unresolved-field markers as a static proxy.
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
DEFAULT_CAMPAIGN_PATH = os.path.join(
    REPO_ROOT, "results", "development_v12", "campaign_results_development.json"
)

# Each pattern here matches wording that would be WRONG for v1.2: either a
# stale v1.1-era number the v1.2 section must not silently inherit, or a
# framing this project has explicitly rejected in its own v1.2 code comments
# (e.g. "8 environments" -- see experiments/run_determinism_v12.py and
# results/development_v12/cross_environment_determinism.json, which insist
# on "deterministic across the tested supported environments," never
# "platform independence" or a fixed environment count the repo's own spec
# does not enumerate).
STALE_PATTERNS = [
    (r"\beight\s+environments\b|\b8\s+environments\b", "an '8 environments' claim not defined anywhere in this repo's own v1.2 spec"),
    (r"(?<!not a claim of )(?<!not )(?<!nor is it a claim of )"
     r"(achieves|demonstrates|provides|establishes|is)\s+platform[- ]independen(t|ce)",
     "an affirmative platform-independence overclaim (disclaiming it, as the existing "
     "v1.1 determinism paragraph does, is fine and must not be flagged)"),
    (r"\bXXXXXXXX\b", "literal placeholder XXXXXXXX"),
    (r"doi:\s*10\.5281/zenodo\.PLACEHOLDER|PLACEHOLDER.?DOI|\[DOI TBD\]", "placeholder DOI"),
    (r"sha256:[0]{10,}|fake.{0,10}digest", "a fabricated/fake container digest"),
    (r"Error! Reference source not found\.|Bookmark not defined",
     "an unresolved Word cross-reference/bookmark field"),
    (r"translation.fidelity.{0,60}(Case B integration|runtime integration)",
     "Case B integration described as translation-fidelity evidence (spec explicitly rejects this "
     "wording -- see experiments/case_b_integration_regression_v12.py)"),
    (r"K\s*=\s*250000.{0,80}not (?:executed|run)", "Monte Carlo K=250000 described as not executed"),
]

# Verbatim strings pulled from already-verified results/development_v12/*.json
# artifacts (see tools/freeze_check_prospective_v5.py, which independently
# re-derives every one of these numbers from source). NOT invented for this
# checker.
REQUIRED_SUBSTRINGS = [
    # Case D CCS1
    "32edcb72bd6cdcd760252bb85431a898b9aded86db2c8468ba77f4aac6b53784",
    # Surface A (results/development_v12/surface_a.json)
    "eight paired semantic families",
    # Case D matrix (results/development_v12/case_d.json)
    "D1",
    "D10",
    # Validator matrix (results/development_v12/validators.json)
    "sixteen",
    # Audit / regression (results/development_v12/audit.json)
    "nine new",
    # Local determinism (results/development_v12/determinism.json)
    "93",
    # GD/GDmin Monte Carlo (results/development_v12/monte_carlo.json)
    "K = 250,000",
    "seed 20260201",
    # Compile timing (results/development_v12/compile_timing.json)
    "10 warmup",
    "100 measured",
    # Case B integration (results/development_v12/case_b_integration.json)
    "thirteen adverse",
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


def check(campaign_path=DEFAULT_CAMPAIGN_PATH):
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
        record("no stale/overclaim term: %s" % label, match is None,
               "found: %r" % text[max(0, match.start() - 40):match.end() + 40] if match else "")

    is_development_campaign = "development" in os.path.relpath(campaign_path, REPO_ROOT)
    if not os.path.exists(campaign_path):
        record("campaign result file present (%s)"
               % os.path.relpath(campaign_path, REPO_ROOT), False, campaign_path)
    else:
        with open(campaign_path, encoding="utf-8") as fh:
            campaign = json.load(fh)
        result = campaign.get("result", campaign)
        if is_development_campaign:
            record("campaign is explicitly development-phase, not reportable "
                   "(a PASS above does not itself mean submission-ready)",
                   result.get("reportable") is False, "")

    return {
        "passed": not findings,
        "checks": checks,
        "findings": findings,
        "check_count": len(checks),
        "failure_count": len(findings),
        "campaign_path": os.path.relpath(campaign_path, REPO_ROOT),
        "campaign_is_development_phase": is_development_campaign,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", default=DEFAULT_CAMPAIGN_PATH,
                        help="campaign_results.json to check manuscript numbers against "
                             "(default: results/development_v12/campaign_results_development.json)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = check(args.campaign)
    for c in report["checks"]:
        print("  [%s] %s %s" % ("PASS" if c["passed"] else "FAIL", c["check"], c["detail"]))

    print("\n%s -- %d checks, %d failures"
          % ("PASSED" if report["passed"] else "FAILED",
             report.get("check_count", len(report["checks"])),
             report.get("failure_count", len(report["findings"]))))
    if report.get("campaign_is_development_phase"):
        print("NOTE: checked against a development-phase campaign file; "
              "this is NOT a submission-readiness verdict.")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
