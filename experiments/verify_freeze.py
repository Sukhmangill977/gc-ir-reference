"""Verify that the final campaign ran against the frozen state.

    python -m experiments.verify_freeze

The manuscript's requirement is that the frozen elements be **publicly**
hash-committed before the reportable campaign is executed (Section XI-I: "The
internal selection of frozen elements is not a freeze -- the public timestamped
commitment is").

A timestamp alone is weak evidence: a local tag's date is author-settable.  This
script therefore checks something a timestamp cannot fake -- the *content* and
*ancestry* relationship between the freeze and the results:

1. The freeze tag exists and resolves to a commit.
2. Every file listed in ``FREEZE_MANIFEST.sha256`` hashes, **as it stood at the
   freeze commit**, to the value the manifest records.
3. The commit that produced the final results is the freeze commit or a
   descendant of it.
4. **No frozen file changed between the freeze commit and the results commit.**
   This is the substantive check: it is what makes "the campaign ran against the
   frozen analysis logic" verifiable rather than asserted.

Item 4 is the one that matters. If a frozen file changed, the campaign did not run
against the freeze, whatever the timestamps say.

Publication state is reported separately and honestly: whether the tag has been
pushed to a public remote is checked, and if it has not, the script says the
public-commitment requirement is **not yet discharged**.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess

from experiments.common import REPO_ROOT, read_json

FREEZE_TAG = "preregister-tier0-v1"
FREEZE_MANIFEST = os.path.join(REPO_ROOT, "preregistration", "FREEZE_MANIFEST.sha256")


def git(*args, check=False):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        if check:
            raise
        return None


def parse_manifest(path):
    rows = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            rows.append({"sha256": parts[0], "category": parts[1],
                         "path": " ".join(parts[2:])})
    return rows


def blob_hash_at(commit, path):
    """SHA-256 of a file's content as it stood at ``commit``."""
    try:
        blob = subprocess.check_output(
            ["git", "show", "%s:%s" % (commit, path)],
            cwd=REPO_ROOT, stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return None
    return hashlib.sha256(blob).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default=FREEZE_TAG)
    parser.add_argument("--results", default=os.path.join(REPO_ROOT, "results", "final"))
    parser.add_argument("--write", default=None,
                        help="write the verification result here as JSON")
    args = parser.parse_args(argv)

    findings = []
    report = {"freeze_tag": args.tag}

    # ---- 1. the tag resolves -------------------------------------------
    freeze_commit = git("rev-list", "-n", "1", args.tag)
    report["freeze_commit"] = freeze_commit
    report["freeze_tag_date"] = git("log", "-1", "--format=%cI", args.tag)
    if not freeze_commit:
        findings.append("freeze tag %r does not exist" % args.tag)
        print("FREEZE TAG %r NOT FOUND -- the campaign has no freeze to verify against"
              % args.tag)
        report["verified"] = False
        report["findings"] = findings
        if args.write:
            _write(args.write, report)
        return 1
    print("freeze tag      : %s -> %s" % (args.tag, freeze_commit[:12]))
    print("freeze date     : %s" % report["freeze_tag_date"])

    # ---- 2. manifest hashes match the freeze commit's content ----------
    rows = parse_manifest(FREEZE_MANIFEST)
    report["frozen_file_count"] = len(rows)
    mismatched = []
    absent = []
    for row in rows:
        actual = blob_hash_at(freeze_commit, row["path"])
        if actual is None:
            absent.append(row["path"])
        elif actual != row["sha256"]:
            mismatched.append(row["path"])
    if absent:
        findings.append("%d frozen file(s) absent at the freeze commit: %s"
                        % (len(absent), absent[:5]))
    if mismatched:
        findings.append("%d frozen file(s) do not match the manifest at the freeze "
                        "commit: %s" % (len(mismatched), mismatched[:5]))
    print("frozen files    : %d listed, %d absent, %d mismatched"
          % (len(rows), len(absent), len(mismatched)))

    # ---- 3 and 4. the results commit, and whether frozen files moved ----
    results_commits = set()
    summary_path = os.path.join(args.results, "reproduce_all.json")
    result_files = []
    if os.path.isdir(args.results):
        for directory, _, files in os.walk(args.results):
            for name in sorted(files):
                if name.endswith(".json"):
                    result_files.append(os.path.join(directory, name))
    for path in result_files:
        try:
            blob = read_json(path)
        except Exception:
            continue
        commit = (blob.get("environment") or {}).get("git_commit")
        if commit:
            results_commits.add(commit)

    report["results_commits"] = sorted(results_commits)
    report["final_result_file_count"] = len(result_files)

    if not results_commits:
        findings.append("no final result file records a git commit -- cannot verify "
                        "the campaign ran after the freeze")
        print("results commits : none found in %s" % args.results)
    else:
        print("results commits : %s" % ", ".join(c[:12] for c in sorted(results_commits)))

    changed_frozen = {}
    for commit in sorted(results_commits):
        is_descendant = git("merge-base", "--is-ancestor", freeze_commit, commit) is not None
        if not is_descendant:
            # merge-base --is-ancestor exits 1 (no output) when false; distinguish
            # that from an error by checking the commit exists at all.
            exists = git("cat-file", "-e", commit + "^{commit}") is not None
            if exists:
                findings.append(
                    "results commit %s is NOT a descendant of the freeze commit %s"
                    % (commit[:12], freeze_commit[:12])
                )
            else:
                findings.append("results commit %s is not in this repository" % commit[:12])
            continue

        diff = git("diff", "--name-only", freeze_commit, commit) or ""
        touched = set(diff.splitlines())
        frozen_paths = {row["path"] for row in rows}
        moved = sorted(touched & frozen_paths)
        if moved:
            changed_frozen[commit] = moved
            findings.append(
                "%d frozen file(s) changed between the freeze and results commit %s: %s"
                % (len(moved), commit[:12], moved[:5])
            )

    report["frozen_files_changed_since_freeze"] = changed_frozen
    print("frozen files changed since freeze: %d commit(s) affected"
          % len(changed_frozen))

    # ---- publication state, reported honestly ---------------------------
    remotes = git("remote") or ""
    pushed = False
    remote_url = None
    if remotes:
        remote_name = remotes.splitlines()[0]
        remote_url = git("remote", "get-url", remote_name)
        listing = git("ls-remote", "--tags", remote_name, args.tag)
        pushed = bool(listing)
    report["remote"] = remote_url
    report["tag_pushed_to_remote"] = pushed
    report["public_commitment_discharged"] = pushed

    print("")
    if pushed:
        print("PUBLICATION     : freeze tag is present on %s" % remote_url)
        print("                  the Section XI-I public timestamped commitment IS discharged")
    else:
        print("PUBLICATION     : freeze tag is NOT present on any remote")
        print("                  the Section XI-I public timestamped commitment is NOT yet")
        print("                  discharged. The local tag records the frozen content and")
        print("                  the ancestry relationship, but a local tag date is")
        print("                  author-settable and is not a public commitment.")

    report["verified"] = not findings
    report["findings"] = findings

    print("")
    if findings:
        print("FREEZE VERIFICATION FAILED:")
        for finding in findings:
            print("  %s" % finding)
    else:
        print("FREEZE VERIFICATION PASSED: every frozen file matches the manifest at the")
        print("freeze commit, the final results were produced at a descendant commit, and")
        print("no frozen file changed in between.")

    if args.write:
        _write(args.write, report)
    return 0 if not findings else 1


def _write(path, report):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print("wrote %s" % os.path.relpath(path, REPO_ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
