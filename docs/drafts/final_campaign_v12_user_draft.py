#!/usr/bin/env python3
"""
Paper 2 v1.2 — Tier-0 final campaign orchestrator.

This runner intentionally acts as an orchestration layer. It does not invent
scientific results and does not silently convert missing implementations into
passes.

Expected repository entry points are discovered at runtime. Adapt the command
mapping only after inspecting the repository and documenting the mapping in
the campaign manifest.

Usage:
    python experiments/final_campaign_v12.py --dry-run
    python experiments/final_campaign_v12.py --final
    python experiments/final_campaign_v12.py --final --continue-on-error

The --final mode is conservative:
- it records the repository state;
- it verifies expected entry points exist;
- it executes each mandatory experiment;
- it captures stdout/stderr;
- it records exit status;
- it writes a machine-readable campaign result;
- it never fabricates PASS values.

A campaign can only be reported PASS when all mandatory commands execute
successfully AND their result artifacts contain an explicit successful status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "final_v5"
LOGS = RESULTS / "logs"
RESULTS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

PROTOCOL = "preregister-tier0-v5"
PAPER_VERSION = "1.2"
MONTE_CARLO_K = 250_000
MONTE_CARLO_SEED = 20260201
EXPECTED_LOCAL_DETERMINISM_RUNS = 93


@dataclass
class StepResult:
    name: str
    command: list[str]
    started_utc: str
    finished_utc: str
    returncode: int
    duration_seconds: float
    stdout_log: str
    stderr_log: str
    status: str
    notes: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    p = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode != 0:
        return ""
    return p.stdout.strip()


def repository_state() -> dict[str, Any]:
    status = git("status", "--porcelain")
    commit = git("rev-parse", "HEAD")
    branch = git("branch", "--show-current")
    tag_points = git("tag", "--points-at", "HEAD").splitlines()
    return {
        "commit": commit,
        "branch": branch,
        "dirty": bool(status),
        "status_porcelain": status.splitlines(),
        "tags_at_head": tag_points,
        "protocol_tag_present_at_head": PROTOCOL in tag_points,
    }


def require_clean_for_final() -> tuple[bool, str]:
    state = repository_state()
    if state["dirty"]:
        return False, "working tree is dirty"
    return True, ""


def run_step(name: str, command: list[str]) -> StepResult:
    started = utc_now()
    t0 = time.perf_counter()
    stdout_path = LOGS / f"{name}.stdout.log"
    stderr_path = LOGS / f"{name}.stderr.log"

    print(f"\n=== {name} ===")
    print("$", shlex.join(command))

    p = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=os.environ.copy(),
    )

    stdout_path.write_text(p.stdout, encoding="utf-8")
    stderr_path.write_text(p.stderr, encoding="utf-8")
    duration = time.perf_counter() - t0
    finished = utc_now()

    status = "PASS" if p.returncode == 0 else "FAIL"
    print(f"[{status}] returncode={p.returncode} duration={duration:.3f}s")

    return StepResult(
        name=name,
        command=command,
        started_utc=started,
        finished_utc=finished,
        returncode=p.returncode,
        duration_seconds=duration,
        stdout_log=str(stdout_path.relative_to(ROOT)),
        stderr_log=str(stderr_path.relative_to(ROOT)),
        status=status,
    )


def command_exists(relative: str) -> bool:
    return (ROOT / relative).exists()


def discover_command_candidates() -> dict[str, list[list[str]]]:
    py = sys.executable
    return {
        "pytest": [
            [py, "-m", "pytest", "-q",
             "--junitxml=results/final_v5/pytest-junit.xml"],
        ],
        "compile_a": [
            [py, "experiments/surface_a_paired_validation.py", "--compile-only"],
            [py, "run_all.py", "--case", "A"],
        ],
        "compile_b": [
            [py, "run_all.py", "--case", "B"],
            [py, "run_all.py", "--case", "Bv1.1"],
        ],
        "compile_d": [
            [py, "experiments/case_d_matrix.py", "--compile-only"],
            [py, "run_all.py", "--case", "D"],
        ],
        "surface_a": [
            [py, "experiments/surface_a_paired_validation.py"],
        ],
        "case_d": [
            [py, "experiments/case_d_matrix.py"],
        ],
        "contract_validator": [
            [py, "experiments/validate_contract_v12.py"],
        ],
        "audit": [
            [py, "run_all.py", "--audit"],
        ],
        "case_b_integration": [
            [py, "run_all.py", "--case-b-integration"],
        ],
        "determinism": [
            [py, "experiments/run_determinism_v12.py"],
        ],
        "gd": [
            [py, "run_all.py", "--gd"],
        ],
        "monte_carlo": [
            [py, "run_all.py", "--monte-carlo",
             "--K", str(MONTE_CARLO_K), "--seed", str(MONTE_CARLO_SEED)],
        ],
        "timing": [
            [py, "experiments/compile_timing_v12.py"],
        ],
        "observation": [
            [py, "run_all.py", "--observation-diagnostics"],
        ],
        "cross_environment": [
            [py, "run_all.py", "--cross-environment"],
        ],
        "manuscript": [
            [py, "tools/verify_manuscript_v1_2_0.py"],
        ],
    }


def resolve_command(candidates: list[list[str]]) -> list[str] | None:
    for cmd in candidates:
        script = cmd[1] if len(cmd) > 1 else ""
        if script.endswith(".py") and not (ROOT / script).exists():
            continue
        if cmd[1:3] == ["-m", "pytest"]:
            return cmd
        return cmd
    return None


def artifact_status() -> dict[str, Any]:
    expected = [
        RESULTS / "campaign_results.json",
        RESULTS / "pytest-junit.xml",
    ]
    out: dict[str, Any] = {}
    for p in expected:
        out[str(p.relative_to(ROOT))] = {
            "exists": p.exists(),
            "sha256": sha256_file(p) if p.exists() and p.is_file() else None,
        }
    return out


def build_summary(
    state_before: dict[str, Any],
    steps: list[StepResult],
    dry_run: bool,
) -> dict[str, Any]:
    failed = [s.name for s in steps if s.status != "PASS"]
    mandatory = [s.name for s in steps]

    # This orchestrator deliberately does not infer experiment PASS from a
    # process exit code alone. Individual experiment scripts should write
    # explicit machine-readable results. The overall status therefore remains
    # BLOCKED until a separate result verifier confirms all required outcomes.
    if dry_run:
        overall = "DRY_RUN"
    elif failed:
        overall = "FAIL"
    else:
        overall = "BLOCKED"

    return {
        "protocol": PROTOCOL,
        "paper_version": PAPER_VERSION,
        "status": overall,
        "repository": state_before,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "configuration": {
            "monte_carlo_K": MONTE_CARLO_K,
            "monte_carlo_seed": MONTE_CARLO_SEED,
            "expected_local_determinism_runs": EXPECTED_LOCAL_DETERMINISM_RUNS,
        },
        "steps": [asdict(s) for s in steps],
        "failed_steps": failed,
        "mandatory_steps": mandatory,
        "artifacts": artifact_status(),
        "timestamp_utc": utc_now(),
        "notes": (
            "Overall PASS requires explicit verification of all experiment "
            "result artifacts against preregister-tier0-v5. This orchestrator "
            "does not manufacture that verification."
        ),
    }


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(obj, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.final:
        parser.error("choose --dry-run or --final")

    state_before = repository_state()

    if args.final:
        ok, reason = require_clean_for_final()
        if not ok:
            print(f"BLOCKED: {reason}", file=sys.stderr)
            summary = build_summary(state_before, [], False)
            summary["status"] = "BLOCKED"
            summary["block_reason"] = reason
            write_json(RESULTS / "orchestrator_results.json", summary)
            return 2

        if not state_before["protocol_tag_present_at_head"]:
            print(
                f"WARNING: HEAD is not tagged {PROTOCOL}. "
                "Final execution is allowed only if repository policy permits "
                "an exact clean frozen commit without the tag.",
                file=sys.stderr,
            )

    candidates = discover_command_candidates()

    ordered = [
        ("pytest", "pytest"),
        ("compile_a", "compile_a"),
        ("compile_b", "compile_b"),
        ("compile_d", "compile_d"),
        ("surface_a", "surface_a"),
        ("case_d", "case_d"),
        ("contract_validator", "contract_validator"),
        ("audit", "audit"),
        ("case_b_integration", "case_b_integration"),
        ("determinism", "determinism"),
        ("gd", "gd"),
        ("monte_carlo", "monte_carlo"),
        ("timing", "timing"),
        ("observation", "observation"),
        ("cross_environment", "cross_environment"),
        ("manuscript", "manuscript"),
    ]

    steps: list[StepResult] = []

    for name, key in ordered:
        cmd = resolve_command(candidates[key])
        if cmd is None:
            step = StepResult(
                name=name,
                command=[],
                started_utc=utc_now(),
                finished_utc=utc_now(),
                returncode=127,
                duration_seconds=0.0,
                stdout_log="",
                stderr_log="",
                status="BLOCKED",
                notes="No configured repository entry point was found.",
            )
            steps.append(step)
            print(f"[BLOCKED] {name}: no entry point found")
            if not args.continue_on_error:
                break
            continue

        if args.dry_run:
            print("$", shlex.join(cmd))
            continue

        result = run_step(name, cmd)
        steps.append(result)

        if result.returncode != 0 and not args.continue_on_error:
            print(f"Stopping after mandatory failure: {name}", file=sys.stderr)
            break

    summary = build_summary(state_before, steps, args.dry_run)

    if args.dry_run:
        summary["status"] = "DRY_RUN"

    write_json(RESULTS / "orchestrator_results.json", summary)

    print("\n=== CAMPAIGN ORCHESTRATOR SUMMARY ===")
    print(json.dumps(summary, indent=2))

    if args.dry_run:
        return 0
    if any(s.status != "PASS" for s in steps):
        return 1

    # Deliberately conservative: successful subprocesses do not prove the
    # preregistered scientific outcomes. A dedicated result verifier should
    # convert this BLOCKED state to PASS only after inspecting the outputs.
    print(
        "\nCampaign commands completed successfully, but scientific PASS "
        "has not been inferred. Verify campaign_results.json and all "
        "preregistered denominators/outcomes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
