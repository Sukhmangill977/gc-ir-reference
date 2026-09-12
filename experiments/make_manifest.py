"""Generate ``MANIFEST.sha256`` over the research artifact.

    python -m experiments.make_manifest

Appendix C requires "One MANIFEST.sha256 at release root listing, per file: path,
SHA-256, and role", with the role drawn from a declared vocabulary.  Every hash is
computed from the file on disk; none is ever typed by hand.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

from experiments.common import REPO_ROOT

#: Appendix C role vocabulary, plus the roles this artifact adds for material the
#: manuscript enumerates in the Data & Code Availability statement.
ROLE_RULES = [
    ("schemas/", "schema"),
    ("catalog/", "catalog"),
    ("invariants/", "invariant_register"),
    ("src/gcir/refinement.py", "psi_tooling"),
    ("src/gcir/catalog.py", "psi_tooling"),
    ("src/gcir/compiler.py", "phi_impl"),
    ("src/gcir/canonicalization.py", "phi_impl"),
    ("src/gcir/", "phi_impl"),
    ("cases/case_a/judgment/", "judgment_record_a"),
    ("cases/case_b/judgment/", "judgment_record_b"),
    ("cases/case_a/dispositions/", "dispositions_a"),
    ("cases/case_b/dispositions/", "dispositions_b"),
    ("cases/case_a/acs/", "acs_a"),
    ("cases/case_b/acs/", "acs_b"),
    ("cases/case_a/lifecycle/", "lifecycle_registry"),
    ("cases/case_b/lifecycle/", "lifecycle_registry"),
    ("cases/case_a/", "case_a_input"),
    # The artifact-runs memo asks specifically for the Case B -> L-DREA manifest
    # mapping to carry role `case_b_input`.
    ("cases/case_b/ldrea_traceability.json", "case_b_input"),
    ("cases/case_b/ldrea_predicate_family.json", "case_b_input"),
    ("cases/case_b/", "case_b_input"),
    # Schema v1.1 development artifacts (not part of preregister-tier0-v3.1).
    # Case B v1.1's downstream correspondence addendum keeps the same
    # `case_b_input` role as its historical counterpart, per runbook item 7/8.
    ("cases/case_b_v1_1/ldrea_traceability_v1_1_addendum.json", "case_b_input"),
    ("cases/case_b_v1_1/", "case_b_input"),
    ("cases/case_c/", "case_c_input"),
    ("results/final/case_a/bundle.json", "compiled_bundle_a"),
    ("results/final/case_b/bundle.json", "compiled_bundle_b"),
    ("results/final/case_a/", "compiled_bundle_a"),
    ("results/final/case_b/", "compiled_bundle_b"),
    ("queries/", "queries"),
    ("preregistration/RQ5_DEFERRED_PROTOCOL.md", "adjudication_instrument"),
    ("preregistration/", "prereg_commitment"),
    ("tests/", "test_suite"),
    ("experiments/", "experiment_code"),
    ("tools/freeze_check.py", "phi_impl"),
    ("tools/montecarlo.py", "experiment_code"),
    ("tools/td_crossenv.py", "experiment_code"),
    ("tools/derive_ldrea_predicate_family.py", "case_b_input"),
    ("tools/build_ldrea_traceability.py", "case_b_input"),
    ("run_all.py", "experiment_code"),
    ("tools/", "fixture_generator"),
    ("results/final_v2/", "measured_result"),
    ("results/final/", "superseded_result"),
    ("results/development/", "development_result"),
    ("docs/source/", "source_document"),
    ("docs/", "documentation"),
    ("paper_update/", "manuscript_reconciliation"),
    ("keys/", "research_key_TEST_ONLY"),
    (".github/", "ci_configuration"),
]

SKIP_DIRECTORIES = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".hypothesis",
    ".idea", ".vscode", "node_modules", ".eggs", "build", "dist",
}
SKIP_FILES = {"MANIFEST.sha256", ".DS_Store"}
SKIP_SUFFIXES = (".pyc", ".pyo", ".swp", ".log", ".tmp")


def role_for(relative):
    posix = relative.replace(os.sep, "/")
    for prefix, role in ROLE_RULES:
        if posix == prefix or posix.startswith(prefix):
            return role
    return "repository_root"


def iter_files(root):
    for directory, subdirectories, files in os.walk(root):
        subdirectories[:] = sorted(
            d for d in subdirectories if d not in SKIP_DIRECTORIES and not d.startswith(".git")
        )
        for name in sorted(files):
            if name in SKIP_FILES or name.endswith(SKIP_SUFFIXES):
                continue
            path = os.path.join(directory, name)
            relative = os.path.relpath(path, root)
            if relative.split(os.sep)[0] in SKIP_DIRECTORIES:
                continue
            yield relative, path


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(root=REPO_ROOT):
    rows = []
    for relative, path in iter_files(root):
        rows.append({
            "path": relative.replace(os.sep, "/"),
            "sha256": sha256_file(path),
            "role": role_for(relative),
            "bytes": os.path.getsize(path),
        })
    rows.sort(key=lambda row: row["path"])
    return rows


def render(rows):
    lines = [
        "# MANIFEST.sha256 -- GC-IR reference implementation",
        "#",
        "# Appendix C: one manifest at release root listing, per file: path,",
        "# SHA-256, and role. Generated by `python -m experiments.make_manifest`;",
        "# every hash is computed from the file on disk.",
        "#",
        "# Format:  <sha256>  <role>  <path>",
        "#",
        "# The release tag and this manifest's own hash together constitute the",
        "# public preregistration commitment referenced in Section XI-I.",
        "#",
        "# NOTE: keys/ contains RESEARCH FIXTURE Ed25519 keys marked",
        "# TEST ONLY / NOT FOR PRODUCTION. They are committed so that a reviewer",
        "# regenerating the case artifacts obtains byte-identical signatures.",
        "",
    ]
    width = max((len(row["role"]) for row in rows), default=10)
    for row in rows:
        lines.append("%s  %-*s  %s" % (row["sha256"], width, row["role"], row["path"]))
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=REPO_ROOT)
    args = parser.parse_args(argv)

    rows = build(args.root)
    text = render(rows)
    path = os.path.join(args.root, "MANIFEST.sha256")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    manifest_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    index_path = os.path.join(args.root, "MANIFEST.json")
    with open(index_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(
            {
                "file_count": len(rows),
                "total_bytes": sum(row["bytes"] for row in rows),
                "manifest_sha256": manifest_hash,
                "roles": sorted({row["role"] for row in rows}),
                "files": rows,
            },
            handle, indent=2, sort_keys=True,
        )
        handle.write("\n")

    print("MANIFEST.sha256: %d files, %d roles" % (len(rows), len({r["role"] for r in rows})))
    print("manifest SHA-256: %s" % manifest_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
