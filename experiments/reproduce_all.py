"""One-command reproduction of every non-CI experiment.

    python -m experiments.reproduce_all            # development phase
    python -m experiments.reproduce_all --final    # frozen reportable campaign
    make reproduce

Runs, in order:

  1. regenerate the case artifacts and verify the committed tree is unchanged
  2. compile Case A and Case B
  3. the four pytest suites (unit, property-based, adversarial, integration)
  4. the adversarial corpus, structural checks and seeded validation rows
  5. the traceability audit queries and their negative controls
  6. the primary metrics
  7. gate divergence and the Proposition 1/2 premises
  8. the determinism experiment
  9. the Monte Carlo rating-robustness experiment
 10. the hash manifest
 11. SUMMARY.md

Cross-platform determinism is measured by the GitHub Actions matrix and is
therefore *not* part of this script; `results/final/CI_STATUS.md` records it.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

from experiments.common import (REPO_ROOT, add_common_args, banner, phase_of,
                                results_dir, write_result)


def _step(name, function, *args, **kwargs):
    banner(name)
    started = time.time()
    try:
        function(*args, **kwargs)
        status = "ok"
        detail = ""
    except SystemExit as exc:
        status = "ok" if exc.code in (0, None) else "failed"
        detail = "exit code %s" % exc.code
    except Exception as exc:  # noqa: BLE001 -- a failed step must be reported, not hidden
        status = "failed"
        detail = "%s: %s" % (type(exc).__name__, exc)
        import traceback

        traceback.print_exc()
    elapsed = round(time.time() - started, 2)
    print("\n[%s] %s (%.2fs)%s" % (status.upper(), name, elapsed,
                                   " -- " + detail if detail else ""))
    return {"step": name, "status": status, "seconds": elapsed, "detail": detail}


def _regenerate_and_verify():
    """The committed case tree is the artifact of record; regeneration must not
    change it."""
    from tools import build_cases, build_lifecycle

    before = _tree_digest()
    build_cases.main([])
    build_lifecycle.main()
    after = _tree_digest()
    changed = sorted(k for k in before if before.get(k) != after.get(k))
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    if changed or added or removed:
        raise RuntimeError(
            "regenerating the case artifacts changed the committed tree: "
            "changed=%s added=%s removed=%s" % (changed, added, removed)
        )
    print("case tree regenerated; %d files unchanged" % len(after))


def _tree_digest():
    import hashlib

    digests = {}
    for root in ("cases", "catalog", "invariants", "keys"):
        base = os.path.join(REPO_ROOT, root)
        if not os.path.isdir(base):
            continue
        for directory, _, files in os.walk(base):
            for name in sorted(files):
                if not name.endswith(".json"):
                    continue
                path = os.path.join(directory, name)
                with open(path, "rb") as handle:
                    digests[os.path.relpath(path, REPO_ROOT)] = hashlib.sha256(
                        handle.read()).hexdigest()
    return digests


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-per-case", type=int, default=31,
                        help="determinism runs per case; the frozen matrix is 31 "
                             "(10 repeats + 10 row shuffles + 5 key shuffles + "
                             "3 locales + 3 time zones), 62 total")
    parser.add_argument("--draws", type=int, default=None,
                        help="Monte Carlo K (default: the frozen 250000)")
    parser.add_argument("--skip-monte-carlo", action="store_true",
                        help="skip the Monte Carlo step (it is the slowest)")
    add_common_args(parser)
    args = parser.parse_args(argv)

    from experiments import (
        make_manifest,
        make_summary,
        run_adversarial,
        run_case,
        run_determinism,
        run_gate_divergence,
        run_metrics,
        run_monte_carlo,
        run_properties,
        run_traceability,
    )

    phase = phase_of(args)
    phase_args = (["--final-v2"] if phase == "final_v2"
                  else ["--final"] if phase == "final" else [])

    steps = []
    steps.append(_step("1. Regenerate case artifacts and verify the committed tree",
                       _regenerate_and_verify))
    steps.append(_step("2. Compile Case A and Case B",
                       run_case.main, phase_args))
    steps.append(_step("3. Test suites (unit, property-based, adversarial, integration)",
                       run_properties.main, phase_args))
    steps.append(_step("4. Adversarial corpus, structural checks, validation seeds",
                       run_adversarial.main, phase_args))
    steps.append(_step("5. Traceability audit queries and negative controls",
                       run_traceability.main, phase_args))
    steps.append(_step("6. Primary metrics",
                       run_metrics.main, phase_args))
    steps.append(_step("7. Gate divergence and Proposition 1/2 premises",
                       run_gate_divergence.main, phase_args))

    determinism_args = ["--runs-per-case", str(args.runs_per_case)]
    determinism_args += phase_args
    steps.append(_step("8. Determinism experiment (%d runs per case)" % args.runs_per_case,
                       run_determinism.main, determinism_args))

    if args.skip_monte_carlo:
        steps.append({"step": "9. Monte Carlo", "status": "skipped",
                      "seconds": 0.0, "detail": "--skip-monte-carlo"})
        print("\n[SKIPPED] 9. Monte Carlo")
    else:
        monte_args = []
        if args.draws:
            monte_args += ["--draws", str(args.draws)]
        monte_args += phase_args
        steps.append(_step("9. Monte Carlo rating robustness",
                           run_monte_carlo.main, monte_args))

    steps.append(_step("10. Hash manifest", make_manifest.main, []))
    steps.append(_step("11. SUMMARY.md",
                       make_summary.main, phase_args))

    banner("REPRODUCTION SUMMARY")
    width = max(len(step["step"]) for step in steps)
    for step in steps:
        print("  %-8s %-*s %8.2fs %s"
              % (step["status"].upper(), width, step["step"], step["seconds"],
                 step["detail"]))

    failed = [step for step in steps if step["status"] == "failed"]
    write_result(phase, "reproduce_all", {
        "steps": steps,
        "failed_steps": [step["step"] for step in failed],
        "all_ok": not failed,
        "arguments": {
            "runs_per_case": args.runs_per_case,
            "draws": args.draws,
            "skip_monte_carlo": args.skip_monte_carlo,
            "phase": phase,
        },
    })

    if failed:
        print("\n%d STEP(S) FAILED: %s"
              % (len(failed), ", ".join(step["step"] for step in failed)))
        return 1
    print("\nAll steps completed. Results in %s"
          % os.path.relpath(results_dir(phase), REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
