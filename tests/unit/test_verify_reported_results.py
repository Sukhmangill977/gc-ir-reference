"""Tests for the paper-facing result verifier.

A verifier that only ever passes is worthless, so most of these tests corrupt
something and assert that the verifier NOTICES.  The corruption is always done
on a copy in a tmp_path; nothing under ``results/final_v2/`` is written to.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from tools import verify_reported_results as verifier  # noqa: E402

MAP_PATH = os.path.join(REPO_ROOT, "artifact_review", "PAPER_RESULT_MAP.json")


@pytest.fixture(scope="module")
def mapping():
    with open(MAP_PATH, encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------- the map ---

def test_map_exists_and_is_populated(mapping):
    assert mapping["entry_count"] == len(mapping["entries"])
    assert mapping["entry_count"] >= 40, "the map should cover every reported result"
    assert mapping["results_dir"] == "results/final_v2"
    assert mapping["freeze_tag"] == "preregister-tier0-v2.2"


def test_every_entry_is_fully_specified(mapping):
    required = ("id", "section", "claim", "metric", "reported", "experiment",
                "command", "inputs", "result_file", "field", "expected",
                "interpretation", "boundary")
    for entry in mapping["entries"]:
        for key in required:
            assert entry.get(key) not in (None, ""), \
                "entry %s is missing %s" % (entry["id"], key)


def test_entry_ids_are_unique(mapping):
    ids = [entry["id"] for entry in mapping["entries"]]
    assert len(ids) == len(set(ids))


def test_every_result_file_exists(mapping):
    for entry in mapping["entries"]:
        path = os.path.join(REPO_ROOT, entry["result_file"])
        assert os.path.exists(path), \
            "%s cites a missing result file %s" % (entry["id"], entry["result_file"])


def test_deferred_quantities_carry_no_value(mapping):
    assert mapping["deferred"], "RQ5 deferral must be recorded explicitly"
    reported_metrics = {entry["metric"] for entry in mapping["entries"]}
    for deferred in mapping["deferred"]:
        assert deferred["metric"] not in reported_metrics, \
            "%s is deferred but appears as a reported result" % deferred["quantity"]


# ------------------------------------------------------------ the verifier ---

def test_verifier_passes_on_the_committed_evidence():
    assert verifier.main([]) == 0


def test_verifier_json_mode_is_wellformed(capsys):
    assert verifier.main(["--json"]) == 0
    blob = json.loads(capsys.readouterr().out)
    assert blob["all_ok"] is True
    assert blob["failed"] == 0
    assert blob["reported_result_count"] > 0
    assert blob["cross_check_count"] > 0
    # Skips are legitimate -- a tagless CI checkout cannot resolve the freeze tag --
    # so the three states must account for every check, rather than assuming all
    # of them passed.
    assert (blob["passed"] + blob["failed"] + blob["skipped"]
            == len(blob["checks"]))
    assert blob["reported_result_count"] + blob["cross_check_count"] \
        == len(blob["checks"])


def test_missing_map_exits_two(tmp_path):
    assert verifier.main(["--map", str(tmp_path / "absent.json")]) == 2


# --- the important direction: does it actually catch a wrong number? --------

def _map_with(tmp_path, mutate):
    """Copy the map, apply ``mutate`` to it, and return the new path."""
    with open(MAP_PATH, encoding="utf-8") as handle:
        blob = json.load(handle)
    mutate(blob)
    path = tmp_path / "mutated_map.json"
    path.write_text(json.dumps(blob), encoding="utf-8")
    return str(path)


def _set_expected(blob, entry_id, value):
    for entry in blob["entries"]:
        if entry["id"] == entry_id:
            entry["expected"] = value
            return
    raise AssertionError("no entry %s in the map" % entry_id)


@pytest.mark.parametrize("entry_id,wrong", [
    ("TD", 0.999),                      # a determinism value that did not happen
    ("DC-A", 0.9),                      # a metric drifted
    ("GDMIN-A", 4),                     # an integer result changed
    ("MC-FPHEAT", 0.321),               # the ROUNDED value: must not silently pass
    ("MC-K", 100000),                   # a different draw count
    ("H-A", "0" * 64),                  # a wrong bundle hash
    ("ADV", 61),                        # one fewer adversarial case
    ("TRACE-CLEAN", False),             # a boolean flipped
])
def test_verifier_fails_when_a_reported_value_is_wrong(tmp_path, entry_id, wrong):
    path = _map_with(tmp_path, lambda blob: _set_expected(blob, entry_id, wrong))
    assert verifier.main(["--map", path]) == 1, \
        "the verifier accepted a wrong value for %s" % entry_id


def test_verifier_fails_on_an_unknown_field(tmp_path):
    def mutate(blob):
        for entry in blob["entries"]:
            if entry["id"] == "TD":
                entry["field"] = "result.TD.no_such_field"
    assert verifier.main(["--map", _map_with(tmp_path, mutate)]) == 1


def test_verifier_fails_on_a_missing_result_file(tmp_path):
    def mutate(blob):
        for entry in blob["entries"]:
            if entry["id"] == "TD":
                entry["result_file"] = "results/final_v2/does_not_exist.json"
    assert verifier.main(["--map", _map_with(tmp_path, mutate)]) == 1


# --- cross-checks must catch a tampered result file ------------------------

def test_cross_checks_catch_a_tampered_payload_hash(tmp_path, monkeypatch):
    """Rewrite a compiled hash in a COPY of the repo and confirm detection.

    This is the scenario the cross-checks exist for: someone edits a result file
    to match a number in the paper. The committed reference hash, the standalone
    payload_hash.txt and the canonical bytes all still disagree.
    """
    work = tmp_path / "repo"
    for directory in ("results", "cases", "artifact_review"):
        shutil.copytree(os.path.join(REPO_ROOT, directory), work / directory)

    target = work / "results" / "final_v2" / "case_a" / "compilation.json"
    blob = json.loads(target.read_text(encoding="utf-8"))
    container = blob.get("result", blob)
    container["payload_hash"] = "0" * 64
    target.write_text(json.dumps(blob), encoding="utf-8")

    monkeypatch.setattr(verifier, "REPO_ROOT", str(work))
    checks = verifier.cross_checks()
    failed = [c for c in checks if not c.passed]
    assert failed, "a tampered payload hash went undetected"
    assert any("case_a" in c.label for c in failed)


def test_cross_checks_pass_on_the_untouched_repository():
    failed = [c for c in verifier.cross_checks() if not c.passed]
    assert not failed, "cross-checks failed: %s" % [c.label for c in failed]


# --- the CLI is what a reviewer actually runs ------------------------------

def test_command_line_entry_point_succeeds():
    completed = subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "tools",
                                      "verify_reported_results.py")],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    assert completed.returncode == 0, completed.stdout.decode()
    assert b"paper-facing empirical claims verified" in completed.stdout


# --- skip semantics: "cannot verify" must not be conflated with "wrong" -------

def test_missing_git_tag_is_skipped_not_failed(monkeypatch):
    """A tagless or shallow checkout -- as CI's `tests` workflow uses -- cannot
    resolve the freeze tag. That must skip, not fail: absence of the tag is not
    evidence that the recorded freeze commit is wrong."""
    real_run = subprocess.run

    def no_tag(args, **kwargs):
        if args[:2] == ["git", "rev-list"]:
            return subprocess.CompletedProcess(args, 128, stdout=b"")
        return real_run(args, **kwargs)

    monkeypatch.setattr(verifier.subprocess, "run", no_tag)
    checks = verifier.cross_checks()
    tag_checks = [c for c in checks if "git tag" in c.label]
    assert len(tag_checks) == 1
    assert tag_checks[0].skipped is True
    assert tag_checks[0].status == "SKIP"
    assert not [c for c in checks if not c.passed], \
        "a missing tag must not fail the run"


def test_wrong_git_tag_commit_still_fails(monkeypatch):
    """The skip path must not become a way for a genuinely wrong tag to pass."""
    real_run = subprocess.run

    def wrong_tag(args, **kwargs):
        if args[:2] == ["git", "rev-list"]:
            return subprocess.CompletedProcess(args, 0, stdout=b"0" * 40 + b"\n")
        return real_run(args, **kwargs)

    monkeypatch.setattr(verifier.subprocess, "run", wrong_tag)
    failed = [c for c in verifier.cross_checks() if not c.passed]
    assert any("git tag" in c.label for c in failed), \
        "a tag pointing at the wrong commit must fail"


def test_json_mode_reports_skips_separately(capsys):
    assert verifier.main(["--json"]) == 0
    blob = json.loads(capsys.readouterr().out)
    assert "skipped" in blob
    assert blob["passed"] + blob["failed"] + blob["skipped"] == len(blob["checks"])
    assert all("status" in check for check in blob["checks"])
