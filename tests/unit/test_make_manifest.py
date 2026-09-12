"""Regression tests for experiments.make_manifest reading exclusively from
Git (index or a commit tree), never from a raw filesystem walk.

These tests build small, throwaway git repositories under a temp directory
so they never touch this repository's own history. Each proves one of the
properties the preregister-tier0-v4 MANIFEST defect violated: an ignored,
untracked, or working-tree-only-deleted file must never enter the manifest,
a tracked file must be included regardless of unrelated local noise, and the
same commit must always produce a byte-identical manifest no matter what the
working directory looks like at generation time.
"""

from __future__ import annotations

import os
import subprocess
import tempfile

import pytest

from experiments.make_manifest import build, list_entries, verify_against_ref


def _git(root, *args):
    subprocess.run(["git", "-C", root] + list(args), check=True, capture_output=True)


def _init_repo(root):
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test")
    _git(root, "config", "commit.gpgsign", "false")


def _write(root, relative, content):
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


@pytest.fixture
def repo():
    with tempfile.TemporaryDirectory() as tmp:
        _init_repo(tmp)
        yield tmp


def test_ignored_file_does_not_enter_manifest(repo):
    _write(repo, ".gitignore", "*.secret\n")
    _write(repo, "tracked.txt", "hello\n")
    _write(repo, "leaked.secret", "should never appear\n")
    _git(repo, "add", ".gitignore", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "initial")

    rows = build(repo, ref="INDEX")
    paths = {row["path"] for row in rows}
    assert "leaked.secret" not in paths
    assert "tracked.txt" in paths


def test_untracked_file_does_not_enter_manifest(repo):
    _write(repo, "tracked.txt", "hello\n")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "initial")

    _write(repo, "never_added.txt", "local scratch file\n")

    rows = build(repo, ref="INDEX")
    paths = {row["path"] for row in rows}
    assert "never_added.txt" not in paths
    assert "tracked.txt" in paths


def test_tracked_file_is_included_even_if_unrelated_local_files_exist(repo):
    _write(repo, "tracked.txt", "hello\n")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "initial")

    _write(repo, "scratch1.tmp", "noise\n")
    _write(repo, "scratch2.tmp", "more noise\n")
    os.makedirs(os.path.join(repo, "some_local_dir"), exist_ok=True)
    _write(repo, "some_local_dir/whatever.txt", "also noise\n")

    rows = build(repo, ref="INDEX")
    tracked = next((row for row in rows if row["path"] == "tracked.txt"), None)
    assert tracked is not None
    import hashlib
    assert tracked["sha256"] == hashlib.sha256(b"hello\n").hexdigest()
    paths = {row["path"] for row in rows}
    assert "scratch1.tmp" not in paths
    assert "scratch2.tmp" not in paths
    assert "some_local_dir/whatever.txt" not in paths


def test_clean_clone_produces_identical_manifest(repo):
    _write(repo, "a.txt", "content a\n")
    _write(repo, "sub/b.txt", "content b\n")
    _git(repo, "add", "a.txt", "sub/b.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    commit = subprocess.run(
        ["git", "-C", repo, "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()

    original_rows = build(repo, ref=commit)

    with tempfile.TemporaryDirectory() as clone_dir:
        subprocess.run(["git", "clone", "-q", repo, clone_dir], check=True, capture_output=True)
        clone_rows = build(clone_dir, ref=commit)

    assert original_rows == clone_rows


def test_same_commit_produces_identical_manifest_regardless_of_working_directory_noise(repo):
    _write(repo, "a.txt", "content a\n")
    _write(repo, "b.txt", "content b\n")
    _git(repo, "add", "a.txt", "b.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    commit = subprocess.run(
        ["git", "-C", repo, "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()

    clean_rows = build(repo, ref=commit)

    # Dirty the working directory in every way the old os.walk-based
    # generator was vulnerable to: edit a tracked file without staging,
    # delete another tracked file without staging, and drop in stray
    # untracked files -- none of this may change a ref-based build.
    _write(repo, "a.txt", "MUTATED CONTENT, NEVER STAGED\n")
    os.remove(os.path.join(repo, "b.txt"))
    _write(repo, "untracked_noise.txt", "should never matter\n")

    dirty_rows = build(repo, ref=commit)
    assert dirty_rows == clean_rows


def test_all_manifest_paths_resolve_in_the_tagged_commit(repo):
    _write(repo, "a.txt", "content a\n")
    _write(repo, "b.txt", "content b\n")
    _git(repo, "add", "a.txt", "b.txt")
    _git(repo, "commit", "-q", "-m", "initial")
    _git(repo, "tag", "-a", "v-test", "-m", "test tag")

    rows = build(repo, ref="v-test")
    diff = verify_against_ref(rows, repo, ref="v-test")
    assert diff == {"missing": [], "extra": [], "changed": []}


def test_verify_against_ref_detects_a_real_discrepancy(repo):
    _write(repo, "a.txt", "content a\n")
    _git(repo, "add", "a.txt")
    _git(repo, "commit", "-q", "-m", "initial")

    rows = build(repo, ref="HEAD")
    # Simulate a stale manifest row: change a hash and drop a real file.
    tampered = [dict(row, sha256="0" * 64) for row in rows]
    tampered.append({"path": "phantom.txt", "sha256": "1" * 64, "role": "repository_root", "bytes": 0})

    diff = verify_against_ref(tampered, repo, ref="HEAD")
    assert "a.txt" in diff["changed"]
    assert "phantom.txt" in diff["extra"]


def test_list_entries_excludes_manifest_sha256_self_reference(repo):
    _write(repo, "a.txt", "content a\n")
    _write(repo, "MANIFEST.sha256", "should not self-list\n")
    _git(repo, "add", "a.txt", "MANIFEST.sha256")
    _git(repo, "commit", "-q", "-m", "initial")

    entries = list_entries(repo, ref="INDEX")
    paths = {path for path, _ in entries}
    assert "MANIFEST.sha256" not in paths
    assert "a.txt" in paths
