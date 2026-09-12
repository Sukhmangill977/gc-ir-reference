"""Generate ``MANIFEST.sha256`` over the research artifact.

    python -m experiments.make_manifest              # from the git index (staged state)
    python -m experiments.make_manifest --ref HEAD    # from a specific commit/tag
    python -m experiments.make_manifest --ref preregister-tier0-v4

Appendix C requires "One MANIFEST.sha256 at release root listing, per file: path,
SHA-256, and role", with the role drawn from a declared vocabulary.

**Enumeration and content are read from Git, never from a raw filesystem walk.**
An earlier version of this script used ``os.walk``, so any local, uncommitted
filesystem state -- an untracked file, a gitignored settings file, a locally
deleted-but-uncommitted file -- silently leaked into the generated manifest.
That defect was discovered by comparing a locally-generated manifest against
a genuine clean `git worktree` checkout of `preregister-tier0-v4` (see
docs/V4_MANIFEST_DEFECT_REPORT.json and preregister-tier0-v4.1's freeze
notes) and is the reason this module now reads exclusively through Git:

* ``ref="INDEX"`` (the default) lists exactly what is staged right now
  (``git ls-files -s``) and reads each blob's *staged* content
  (``git cat-file -p <blob-sha>``) -- never the working-tree file on disk.
  This is the right mode to run immediately before a commit: it reflects
  what the commit will actually contain, is immune to any *unstaged*
  working-tree noise (an edited-but-not-added file, a stray local file
  sitting nearby), and never depends on `os.walk` traversal order.
* ``ref="<commit-ish>"`` (a commit, branch, or tag) lists exactly what that
  commit's tree contains (``git ls-tree -r <ref>``) and reads each blob's
  *committed* content. This is the right mode to verify a manifest against
  an already-tagged freeze, and is exactly equivalent to checking out that
  commit into a clean directory and hashing the files there -- without
  needing to actually perform the checkout.

Either way, a file that is untracked, gitignored, or only locally deleted
(without the deletion being staged/committed) can never appear in or be
mistaken for the manifest: Git's own index/tree is the sole source of
truth, and a raw filesystem read never happens.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess

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

#: MANIFEST.sha256 excludes itself (a manifest cannot list its own rendered
#: text file, which does not exist yet when it is being generated).
#: MANIFEST.json is NOT excluded -- it is git-tracked like anything else, so
#: it appears with a one-generation-lagged self-hash, same as always.
SELF_EXCLUDE = {"MANIFEST.sha256"}

#: Git tree entry modes that represent a plain file whose content should be
#: hashed. Symlinks (120000) and submodule gitlinks (160000) are skipped --
#: neither is a "file" whose bytes this manifest can meaningfully hash, and
#: this repository does not use either.
_BLOB_MODES = {"100644", "100755"}


def role_for(relative):
    posix = relative.replace(os.sep, "/")
    for prefix, role in ROLE_RULES:
        if posix == prefix or posix.startswith(prefix):
            return role
    return "repository_root"


def _git(root, *args):
    return subprocess.run(
        ["git", "-C", root] + list(args),
        check=True, capture_output=True,
    )


def list_entries(root=REPO_ROOT, ref="INDEX"):
    """Return sorted (path, blob_sha) pairs for every tracked regular file.

    ``ref="INDEX"`` reads the git index (what is currently staged); any other
    value is passed to ``git ls-tree`` as a commit-ish. Either way this is a
    read of Git's own object database, never a filesystem walk -- an
    untracked, gitignored, or working-tree-only-deleted file cannot appear
    here, and an unstaged working-tree edit cannot change what INDEX mode
    reports.
    """
    if ref == "INDEX":
        output = _git(root, "ls-files", "-s").stdout.decode("utf-8")
        entries = []
        for line in output.splitlines():
            meta, path = line.split("\t", 1)
            mode, blob_sha = meta.split()[:2]
            if mode in _BLOB_MODES:
                entries.append((path, blob_sha))
    else:
        output = _git(root, "ls-tree", "-r", ref).stdout.decode("utf-8")
        entries = []
        for line in output.splitlines():
            meta, path = line.split("\t", 1)
            mode, _kind, blob_sha = meta.split()[:3]
            if mode in _BLOB_MODES:
                entries.append((path, blob_sha))
    return sorted(
        (path, blob_sha) for path, blob_sha in entries
        if path not in SELF_EXCLUDE
    )


def blob_bytes(root, blob_sha):
    """Exact committed/staged bytes for one blob -- no smudge filters, no
    line-ending conversion, independent of any local checkout configuration."""
    return _git(root, "cat-file", "-p", blob_sha).stdout


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def build(root=REPO_ROOT, ref="INDEX"):
    rows = []
    for path, blob_sha in list_entries(root, ref):
        content = blob_bytes(root, blob_sha)
        rows.append({
            "path": path,
            "sha256": sha256_bytes(content),
            "role": role_for(path),
            "bytes": len(content),
        })
    rows.sort(key=lambda row: row["path"])
    return rows


def verify_against_ref(rows, root=REPO_ROOT, ref="HEAD"):
    """Check that every row in ``rows`` (typically a committed MANIFEST.json's
    ``files`` list) resolves in ``ref``'s tree with a matching hash, and that
    ``ref``'s tree has no tracked file missing from ``rows``.

    Returns a dict with ``missing`` (in the ref's tree, absent from rows),
    ``extra`` (in rows, absent from the ref's tree), and ``changed`` (present
    in both, hash differs) -- each a sorted list of paths. All three empty
    means the manifest is exactly self-consistent against that ref.
    """
    ref_rows = {path: sha256_bytes(blob_bytes(root, blob_sha))
                for path, blob_sha in list_entries(root, ref)}
    manifest_rows = {row["path"]: row["sha256"] for row in rows}

    missing = sorted(set(ref_rows) - set(manifest_rows))
    extra = sorted(set(manifest_rows) - set(ref_rows))
    changed = sorted(
        path for path in (set(ref_rows) & set(manifest_rows))
        if ref_rows[path] != manifest_rows[path]
    )
    return {"missing": missing, "extra": extra, "changed": changed}


def render(rows):
    lines = [
        "# MANIFEST.sha256 -- GC-IR reference implementation",
        "#",
        "# Appendix C: one manifest at release root listing, per file: path,",
        "# SHA-256, and role. Generated by `python -m experiments.make_manifest`;",
        "# every path and hash is read from Git's own index/tree (git ls-files /",
        "# git ls-tree + git cat-file), never from a raw filesystem walk -- an",
        "# untracked, gitignored, or working-tree-only file can never appear here.",
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
    parser.add_argument("--ref", default="INDEX",
                         help="'INDEX' (default, staged state) or a git commit-ish "
                              "(commit/branch/tag) to generate the manifest from")
    args = parser.parse_args(argv)

    rows = build(args.root, args.ref)
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
                "generated_from_ref": args.ref,
                "files": rows,
            },
            handle, indent=2, sort_keys=True,
        )
        handle.write("\n")

    print("MANIFEST.sha256: %d files, %d roles (from ref=%s)"
          % (len(rows), len({r["role"] for r in rows}), args.ref))
    print("manifest SHA-256: %s" % manifest_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
