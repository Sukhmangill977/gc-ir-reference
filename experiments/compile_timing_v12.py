"""Compile-time MVP (Paper 2 v1.2 spec section 12).

    python -m experiments.compile_timing_v12 --cases case_a case_b_v1_1 case_d_ccs1 \
        --warmup 10 --runs 100 --phase development

Runs on ONE clearly specified reportable reference machine (this host,
recorded via ``experiments.common.environment``) -- that is enough for the
IEEE Access MVP (spec section 12). No new compiler code: measures the
existing ``gcir.compiler.compile_bundle`` (canonical input -> canonical
Phi_core payload) with ``time.perf_counter``, 10 warmup + 100 measured runs
per case. Explicitly NOT called platform-general latency, and hosts are
never pooled.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402

DEFAULT_CASES = ("case_a", "case_b_v1_1", "case_d_ccs1")


def _machine_descriptor():
    return {
        "machine": platform.node(),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "python": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "single_host_disclaimer": "One reportable reference machine only (spec section 12); not pooled across hosts; not platform-general latency.",
    }


def _percentile(sorted_values, pct):
    if not sorted_values:
        return None
    k = (len(sorted_values) - 1) * pct
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def _time_case(case_id, warmup, runs):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case(case_id)
    inputs_list = [case.compiler_inputs() for _ in range(warmup + runs)]  # fresh CompilerInputs per call; no shared mutable state

    predicate_count = None
    for _ in range(warmup):
        result = compile_bundle(inputs_list.pop())
        predicate_count = len(result.bundle.predicates)

    durations_ms = []
    for _ in range(runs):
        inputs = inputs_list.pop()
        start = time.perf_counter()
        result = compile_bundle(inputs)
        end = time.perf_counter()
        durations_ms.append((end - start) * 1000.0)
        predicate_count = len(result.bundle.predicates)

    durations_ms.sort()
    return {
        "case": case_id,
        "n": runs,
        "warmup": warmup,
        "median_ms": statistics.median(durations_ms),
        "p95_ms": _percentile(durations_ms, 0.95),
        "min_ms": durations_ms[0],
        "max_ms": durations_ms[-1],
        "case_size_control_count": predicate_count,
    }


def run(cases=DEFAULT_CASES, warmup=10, runs=100):
    return {
        "machine": _machine_descriptor(),
        "per_case": {case_id: _time_case(case_id, warmup, runs) for case_id in cases},
        "measures": "canonical input -> canonical Phi_core payload (gcir.compiler.compile_bundle) only, not the file-loading/JSON-parsing wrapper",
        "not_platform_general_latency": True,
        "hosts_pooled": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", default=list(DEFAULT_CASES))
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--runs", type=int, default=100)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run(tuple(args.cases), args.warmup, args.runs)
    document = {
        "result_name": "compile_timing_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "compile_timing.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    for case_id, info in report["per_case"].items():
        print("%-14s n=%d median=%.3fms p95=%.3fms min=%.3fms max=%.3fms controls=%s"
              % (case_id, info["n"], info["median_ms"], info["p95_ms"], info["min_ms"], info["max_ms"], info["case_size_control_count"]))
    print("-> %s" % out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
