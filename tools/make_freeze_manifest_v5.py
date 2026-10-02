"""Generate the retrospective Tier-0 v5 freeze manifest.

    python -m tools.make_freeze_manifest_v5

preregister-tier0-v5 was pushed as a public git tag (4e3d473, "Freeze Paper 2
v1.2 empirical protocol") BEFORE the clean-worktree results/final_v5/ run --
that tag is the actual preregistration commitment. This script only produces
the supplementary, human-readable manifest documenting what the tag froze,
matching the FREEZE_MANIFEST.sha256/.json convention of TIER0_FREEZE through
TIER0_FREEZE_V3_1. It is written AFTER the fact (the v1.2.0 release already
shipped), so it is explicitly retrospective documentation, not a new
commitment -- see preregistration/TIER0_FREEZE_V5.md's own "Retrospective
disclosure" note.

Every hash below is read from the preregister-tier0-v5 TAG's git blobs via
`git cat-file`, never from the working tree, so this manifest is correct
even if a file has since changed on disk -- it documents what the tag
actually froze, not whatever is currently checked out.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FREEZE_DIR = os.path.join(REPO_ROOT, "preregistration")
TAG = "preregister-tier0-v5"

#: category -> paths frozen at the preregister-tier0-v5 tag that discharge it.
#: Scoped to the Paper 2 v1.2 Tier-0 campaign (Surface A / Case D / neutrality
#: / determinism / audit / Monte Carlo / compile timing / observation
#: diagnostics / Case B v1.1 integration), not the older v1.0-v1.1 categories
#: in experiments/make_freeze_manifest.py (a different freeze, different
#: scope -- FREEZE_MANIFEST_V2.json/.sha256).
FROZEN_ITEMS = {
    # NOTE: preregistration/TIER0_FREEZE_V5.md is deliberately NOT in this
    # dict. It is written after the tag (retrospective documentation of what
    # the tag already froze -- see its own "Retrospective disclosure" note),
    # so it is not itself part of the tag's frozen tree and hashing it here
    # would misrepresent it as pre-existing at tag time. The actual
    # specification that predates the tag is the external MVP document
    # supplied before this campaign ran; the rows below are the operational
    # commitment (code + fixtures) that the tag's blob content constitutes.
    "contract_validators": [
        "src/gcir/contract_v12.py",
        "src/gcir/rc_routing.py",
        "src/gcir/audit_queries.py",
        "tests/unit/test_contract_v12.py",
        "tests/unit/test_rc_routing.py",
    ],
    "surface_a": [
        "experiments/surface_a_paired_validation.py",
        "tests/adversarial/test_surface_a.py",
    ],
    "case_d": [
        "tools/build_case_d.py",
        "tools/case_d_data.py",
        "tools/case_d_control.py",
        "tools/write_case_d_reference_hashes.py",
        "experiments/case_d_matrix.py",
        "tests/integration/test_case_d.py",
    ],
    "case_b_v1_1": [
        "tools/build_case_b_v11.py",
        "tools/case_b_v11_control.py",
        "tools/case_b_data.py",
        "experiments/run_determinism_case_b_v11.py",
        "experiments/run_monte_carlo_case_b_v11.py",
        "experiments/case_b_v11_injection_scenarios.py",
        "experiments/case_b_integration_regression_v12.py",
    ],
    "neutrality": [
        "experiments/neutrality_v12.py",
    ],
    "audit_regression": [
        "experiments/audit_regression_v12.py",
    ],
    "determinism_driver": [
        "experiments/run_determinism_v12.py",
    ],
    "monte_carlo": [
        "experiments/monte_carlo_regression_v12.py",
        "preregistration/monte_carlo_distributions_v1.json",
    ],
    "compile_timing": [
        "experiments/compile_timing_v12.py",
    ],
    "observation_diagnostics": [
        "experiments/observation_diagnostics_v12.py",
    ],
    "campaign_orchestration": [
        "experiments/final_campaign_v12.py",
        "experiments/build_campaign_results_final_v5.py",
        "experiments/validate_contract_v12.py",
        "tools/freeze_check_prospective_v5.py",
        "tools/verify_manuscript_v1_2_0.py",
    ],
}


def _git(*args):
    return subprocess.check_output(
        ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.STDOUT
    ).decode("utf-8").strip()


def _blob_sha256(path):
    """SHA-256 of the file's content AT THE TAG, not the working tree."""
    content = subprocess.check_output(
        ["git", "cat-file", "blob", "%s:%s" % (TAG, path)], cwd=REPO_ROOT
    )
    return hashlib.sha256(content).hexdigest()


def _tree_paths(path):
    """Expand a directory (as it existed at the tag) to its file paths."""
    out = _git("ls-tree", "-r", "--name-only", TAG, "--", path)
    return [line for line in out.splitlines() if line]


def build():
    rows = []
    missing = []
    for category, paths in FROZEN_ITEMS.items():
        for path in paths:
            try:
                _git("cat-file", "-e", "%s:%s" % (TAG, path))
            except subprocess.CalledProcessError:
                missing.append("%s (%s)" % (path, category))
                continue
            rows.append({"category": category, "path": path, "sha256": _blob_sha256(path)})

    for case_dir in ("cases/case_d_ccs0", "cases/case_d_ccs1", "cases/case_d_ccs2",
                      "cases/case_b_v1_1", "cases/case_a"):
        category = "case_fixtures"
        for path in _tree_paths(case_dir):
            rows.append({"category": category, "path": path, "sha256": _blob_sha256(path)})

    return rows, missing


def render(rows, commit, tag):
    lines = [
        "# Freeze Manifest: preregister-tier0-v5",
        "# Tag commit: %s" % commit,
        "# Tag: %s" % tag,
        "# Generated retrospectively (see preregistration/TIER0_FREEZE_V5.md) "
        "from the git blobs AT THE TAG, not the working tree.",
        "",
    ]
    width = max(len(row["category"]) for row in rows)
    for row in sorted(rows, key=lambda r: (r["category"], r["path"])):
        lines.append("%s  %-*s  %s" % (row["sha256"], width, row["category"], row["path"]))
    lines.append("")
    return "\n".join(lines)


def main():
    rows, missing = build()
    if missing:
        print("REFUSING TO WRITE: listed files are absent at the tag:")
        for entry in missing:
            print("  %s" % entry)
        return 1

    commit = _git("rev-list", "-n1", TAG)
    text = render(rows, commit, TAG)

    sha_path = os.path.join(FREEZE_DIR, "FREEZE_MANIFEST_V5.sha256")
    with open(sha_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    manifest_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    index = {
        "freeze_version": "tier0-v5",
        "tag": TAG,
        "tag_commit": commit,
        "categories": sorted(FROZEN_ITEMS) + ["case_fixtures"],
        "file_count": len(rows),
        "freeze_manifest_sha256": manifest_hash,
        "files": sorted(rows, key=lambda r: r["path"]),
        "note": (
            "The public git tag preregister-tier0-v5 (pushed before the clean-"
            "worktree results/final_v5/ run) is the actual preregistration "
            "commitment. This manifest is supplementary documentation of what "
            "that tag froze, generated retrospectively from the tag's own git "
            "blobs -- see preregistration/TIER0_FREEZE_V5.md."
        ),
    }
    json_path = os.path.join(FREEZE_DIR, "FREEZE_MANIFEST_V5.json")
    with open(json_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("FREEZE_MANIFEST_V5.sha256: %d files across %d categories"
          % (len(rows), len(index["categories"])))
    print("freeze manifest SHA-256: %s" % manifest_hash)
    print("tag commit: %s" % commit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
