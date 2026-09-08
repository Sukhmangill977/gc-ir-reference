"""Generate the Tier-0 preregistration freeze manifest.

    python -m experiments.make_freeze_manifest

Section XI-I lists what must be publicly hash-committed **before execution**:

    hypotheses and primary outcomes; case artifacts and held-out-register hash;
    derivation catalog; adjudication instrument; thresholds and the C* definition;
    compiler commit and container digest; randomization seed; Bayesian priors;
    Monte Carlo distributions and seed; exclusion and missing-data rules; and
    analysis code.

This script hashes every one of those items from the files on disk and writes
``preregistration/FREEZE_MANIFEST.sha256``.  It also verifies that every category
is actually covered, and refuses to write a manifest with an uncovered category --
a freeze that silently omitted the analysis code would be worthless.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import subprocess

from experiments.common import REPO_ROOT

FREEZE_DIR = os.path.join(REPO_ROOT, "preregistration")

#: Section XI-I category -> the paths that discharge it.
FROZEN_ITEMS = {
    "hypotheses_and_primary_outcomes": [
        "preregistration/TIER0_FREEZE.md",
        "preregistration/RQ5_DEFERRED_PROTOCOL.md",
        "docs/EXPERIMENT_PROTOCOL.md",
    ],
    "case_artifacts": [
        "cases/case_a/inputs/assessment.json",
        "cases/case_a/inputs/cstar_profile.json",
        "cases/case_a/inputs/invariant_register.json",
        "cases/case_a/inputs/threshold_contracts.json",
        "cases/case_a/inputs/policy_metadata.json",
        "cases/case_a/inputs/compile_parameters.json",
        "cases/case_a/judgment/judgment_record.json",
        "cases/case_a/dispositions/dispositions.json",
        "cases/case_a/acs/approved_control_specifications.json",
        "cases/case_a/lifecycle/lifecycle_registry.json",
        "cases/case_a/lifecycle/receipts.json",
        "cases/case_a/lifecycle/actuations.json",
        "cases/case_a/lifecycle/negative/fixtures.json",
        "cases/case_a/expected/reference_hashes.json",
        "cases/case_b/inputs/assessment.json",
        "cases/case_b/inputs/cstar_profile.json",
        "cases/case_b/inputs/invariant_register.json",
        "cases/case_b/inputs/threshold_contracts.json",
        "cases/case_b/inputs/policy_metadata.json",
        "cases/case_b/inputs/compile_parameters.json",
        "cases/case_b/judgment/judgment_record.json",
        "cases/case_b/dispositions/dispositions.json",
        "cases/case_b/acs/approved_control_specifications.json",
        "cases/case_b/lifecycle/lifecycle_registry.json",
        "cases/case_b/lifecycle/receipts.json",
        "cases/case_b/lifecycle/actuations.json",
        "cases/case_b/lifecycle/negative/fixtures.json",
        "cases/case_b/expected/reference_hashes.json",
    ],
    "derivation_catalog": [
        "cases/case_a/inputs/control_derivation_catalog.json",
        "cases/case_b/inputs/control_derivation_catalog.json",
        "catalog/control_derivation_catalog_v1.json",
        "catalog/control_derivation_catalog_b_v1.json",
    ],
    "held_out_register_hash": [
        "preregistration/HELD_OUT_REGISTER.md",
    ],
    "adjudication_instrument": [
        "preregistration/RQ5_DEFERRED_PROTOCOL.md",
    ],
    "thresholds_and_cstar_definition": [
        "cases/case_a/inputs/threshold_contracts.json",
        "cases/case_b/inputs/threshold_contracts.json",
        "cases/case_a/inputs/cstar_profile.json",
        "cases/case_b/inputs/cstar_profile.json",
        "invariants/invariant_register_v1.json",
        "invariants/invariant_register_b_v1.json",
    ],
    "schemas": [
        "schemas/common.schema.json",
        "schemas/assessment.schema.json",
        "schemas/control_derivation_catalog.schema.json",
        "schemas/judgment_record.schema.json",
        "schemas/dispositions.schema.json",
        "schemas/acs.schema.json",
        "schemas/gcir.schema.json",
        "schemas/bundle.schema.json",
        "schemas/lifecycle_registry.schema.json",
        "schemas/threshold_contract.schema.json",
        "schemas/cstar_profile.schema.json",
        "schemas/invariant_register.schema.json",
        "schemas/receipt.schema.json",
    ],
    "compiler_implementation": [
        "src/gcir/__init__.py",
        "src/gcir/models.py",
        "src/gcir/canonicalization.py",
        "src/gcir/catalog.py",
        "src/gcir/refinement.py",
        "src/gcir/compiler.py",
        "src/gcir/authority.py",
        "src/gcir/coverage.py",
        "src/gcir/lifecycle.py",
        "src/gcir/temporal.py",
        "src/gcir/traceability.py",
        "src/gcir/metrics.py",
        "src/gcir/precedence.py",
        "src/gcir/signatures.py",
        "src/gcir/validation.py",
        "src/gcir/caseio.py",
    ],
    "analysis_code": [
        "experiments/common.py",
        "experiments/run_case.py",
        "experiments/run_determinism.py",
        "experiments/run_metrics.py",
        "experiments/run_gate_divergence.py",
        "experiments/run_traceability.py",
        "experiments/run_adversarial.py",
        "experiments/run_monte_carlo.py",
        "experiments/run_properties.py",
        "experiments/adversarial_cases.py",
        "experiments/reproduce_all.py",
        "experiments/make_summary.py",
        "experiments/make_manifest.py",
        "experiments/verify_hashes.py",
        "experiments/check_ci_agreement.py",
        "queries/traceability.sql",
    ],
    "test_suite": [
        "tests/conftest.py",
        "tests/unit/test_rfc8785.py",
        "tests/unit/test_core.py",
        "tests/properties/test_invariants.py",
        "tests/adversarial/test_corpus.py",
        "tests/adversarial/test_no_inference.py",
        "tests/integration/test_cases.py",
    ],
    "monte_carlo_distributions_and_seed": [
        "preregistration/monte_carlo_distributions_v1.json",
    ],
    "determinism_matrix": [
        "experiments/run_determinism.py",
    ],
    "exclusion_and_missing_data_rules": [
        "preregistration/RQ5_DEFERRED_PROTOCOL.md",
        "preregistration/monte_carlo_distributions_v1.json",
    ],
    "bayesian_priors": [
        "preregistration/RQ5_DEFERRED_PROTOCOL.md",
    ],
    "randomization_seed": [
        "preregistration/TIER0_FREEZE.md",
    ],
    "dependency_lock_and_container": [
        "requirements.lock",
        "pyproject.toml",
        "Dockerfile",
        "Makefile",
    ],
    "fixture_generators": [
        "tools/build_cases.py",
        "tools/build_lifecycle.py",
        "tools/case_a_data.py",
        "tools/case_a_control.py",
        "tools/case_b_data.py",
        "tools/case_b_control.py",
        "tools/invariants_data.py",
    ],
    "provenance_and_interpretation": [
        "docs/PAPER_REQUIREMENTS.md",
        "docs/CLAIM_TO_ARTIFACT_MATRIX.md",
        "docs/FIXTURE_PROVENANCE.md",
        "docs/RESULT_INTERPRETATION.md",
    ],
    "research_signing_keys": [
        "keys/public_keys.json",
    ],
}


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return None


def build():
    rows = []
    missing = []
    for category in sorted(FROZEN_ITEMS):
        for relative in FROZEN_ITEMS[category]:
            path = os.path.join(REPO_ROOT, relative)
            if not os.path.exists(path):
                missing.append("%s (%s)" % (relative, category))
                continue
            rows.append({
                "category": category,
                "path": relative,
                "sha256": sha256_file(path),
                "bytes": os.path.getsize(path),
            })

    uncovered = sorted(
        category for category in FROZEN_ITEMS
        if not any(row["category"] == category for row in rows)
    )
    return rows, missing, uncovered


def render(rows, commit, tag):
    lines = [
        "# FREEZE_MANIFEST.sha256 -- Tier-0 preregistration commitment",
        "#",
        "# Manuscript Section XI-I requires the following to be publicly",
        "# hash-committed BEFORE the reportable campaign is executed:",
        "#",
        "#   hypotheses and primary outcomes; case artifacts and held-out-register",
        "#   hash; derivation catalog; adjudication instrument; thresholds and the",
        "#   C* definition; compiler commit and container digest; randomization",
        "#   seed; Bayesian priors; Monte Carlo distributions and seed; exclusion",
        "#   and missing-data rules; and analysis code.",
        "#",
        "# Every hash below is computed from the file on disk by",
        "# `python -m experiments.make_freeze_manifest`. None is typed by hand.",
        "#",
        "#   frozen at commit: %s" % (commit or "UNKNOWN"),
        "#   frozen at tag:    %s" % (tag or "(tag applied after this file is committed)"),
        "#",
        '# "The internal selection of frozen elements is not a freeze -- the public',
        '#  timestamped commitment is."  (Section XI-I)',
        "#",
        "# Format:  <sha256>  <category>  <path>",
        "",
    ]
    width = max(len(row["category"]) for row in rows)
    for row in sorted(rows, key=lambda r: (r["category"], r["path"])):
        lines.append("%s  %-*s  %s" % (row["sha256"], width, row["category"], row["path"]))
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-missing", action="store_true",
                        help="write the manifest even if a listed file is absent")
    args = parser.parse_args(argv)

    rows, missing, uncovered = build()

    if uncovered:
        print("REFUSING TO WRITE: these Section XI-I freeze categories have no "
              "covering file: %s" % ", ".join(uncovered))
        return 1
    if missing and not args.allow_missing:
        print("REFUSING TO WRITE: listed files are absent:")
        for entry in missing:
            print("  %s" % entry)
        return 1

    commit = git("rev-parse", "HEAD")
    tag = git("describe", "--tags", "--exact-match")
    text = render(rows, commit, tag)

    path = os.path.join(FREEZE_DIR, "FREEZE_MANIFEST.sha256")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    manifest_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    index = {
        "freeze_version": "tier0-v1",
        "commit_at_generation": commit,
        "tag_at_generation": tag,
        "categories": sorted(FROZEN_ITEMS),
        "file_count": len(rows),
        "freeze_manifest_sha256": manifest_hash,
        "files": sorted(rows, key=lambda r: r["path"]),
        "note": (
            "The release tag and this manifest's hash together constitute the "
            "public preregistration commitment referenced in Section XI-I. The "
            "commitment is the public timestamped git tag, not this file on its own."
        ),
    }
    with open(os.path.join(FREEZE_DIR, "FREEZE_MANIFEST.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("FREEZE_MANIFEST.sha256: %d files across %d Section XI-I categories"
          % (len(rows), len(FROZEN_ITEMS)))
    print("freeze manifest SHA-256: %s" % manifest_hash)
    print("commit at generation:    %s" % commit)
    if missing:
        print("WARNING: written with %d missing file(s)" % len(missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
