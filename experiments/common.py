"""Shared plumbing for the experiment scripts.

Two rules this module enforces for every experiment:

1. Results are written under ``results/development/`` unless ``--final`` is
   given, in which case they go to ``results/final/``.  The two-phase workflow
   is explicit in the filesystem, not in a convention someone has to remember.

2. Every result file records the environment it was produced in -- git commit,
   git tag, Python version, platform, dependency versions -- so a number can
   always be traced back to the state that produced it.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(REPO_ROOT, "src") not in sys.path:
    sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

RESULTS_DEV = os.path.join(REPO_ROOT, "results", "development")
RESULTS_FINAL = os.path.join(REPO_ROOT, "results", "final")
RESULTS_FINAL_V2 = os.path.join(REPO_ROOT, "results", "final_v2")

CASES = ("case_a", "case_b")


def add_common_args(parser):
    parser.add_argument(
        "--final",
        action="store_true",
        help="write to results/final/ (the tier0-v1 reportable campaign)",
    )
    parser.add_argument(
        "--final-v2",
        dest="final_v2",
        action="store_true",
        help="write to results/final_v2/ (the tier0-v2 reportable campaign, "
             "executed after the PUBLIC freeze)",
    )
    return parser


def phase_of(args):
    """Resolve the results phase from parsed arguments."""
    if getattr(args, "final_v2", False):
        return "final_v2"
    if getattr(args, "final", False):
        return "final"
    return "development"


def results_dir(final):
    """``final`` may be a bool (legacy) or a phase string."""
    if final == "final_v2":
        directory = RESULTS_FINAL_V2
    elif final == "final" or final is True:
        directory = RESULTS_FINAL
    else:
        directory = RESULTS_DEV
    os.makedirs(directory, exist_ok=True)
    return directory


def _git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return None


def environment():
    """Environment provenance recorded alongside every result."""
    try:
        from importlib.metadata import version as _version
    except ImportError:  # pragma: no cover
        _version = None

    dependencies = {}
    if _version is not None:
        for package in ("pytest", "hypothesis", "jsonschema", "cryptography", "numpy"):
            try:
                dependencies[package] = _version(package)
            except Exception:
                dependencies[package] = "not installed"

    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_commit_short": _git("rev-parse", "--short", "HEAD"),
        "git_describe": _git("describe", "--tags", "--always", "--dirty"),
        "git_tag_exact": _git("describe", "--tags", "--exact-match"),
        "git_status_clean": (_git("status", "--porcelain") == ""),
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "system": platform.system(),
        "dependencies": dependencies,
        "run_completed_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def write_result(final, name, payload, phase_note=None):
    """Write a machine-readable result file with environment provenance.

    The recorded ``run_completed_utc`` is a *result-file* timestamp.  It is never
    part of any hashed bundle payload -- see ``gcir.validation``
    ``constraint_13_payload_is_hash_clean``.
    """
    directory = results_dir(final)
    phase = ("final_v2" if final == "final_v2"
             else "final" if (final == "final" or final is True)
             else "development")
    default_note = {
        "final_v2": "FINAL v2 reportable campaign result, produced AFTER the "
                    "publicly pushed preregistration freeze preregister-tier0-v2.",
        "final": "tier0-v1 campaign result. Produced after a LOCAL freeze that was "
                 "not public at execution time; superseded by the v2 campaign for "
                 "reporting purposes.",
        "development": "DEVELOPMENT result. Not a reportable number.",
    }
    document = {
        "result_name": name,
        "phase": phase,
        "phase_note": phase_note or default_note[phase],
        "environment": environment(),
        "result": payload,
    }
    path = os.path.join(directory, name if name.endswith(".json") else name + ".json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return path


def write_csv(final, name, fieldnames, rows):
    import csv

    directory = results_dir(final)
    path = os.path.join(directory, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def load_case_bundle(case_id):
    """Load a case and compile it.  Returns (case, compiler_inputs, result)."""
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case(case_id)
    inputs = case.compiler_inputs()
    result = compile_bundle(inputs)
    return case, inputs, result


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def case_path(case_id, *parts):
    return os.path.join(REPO_ROOT, "cases", case_id, *parts)


def banner(text):
    line = "=" * 72
    print("\n%s\n%s\n%s" % (line, text, line))
