"""Environment 7: pinned Linux/aarch64 container determinism (Paper 2 v1.2
gap-closure, distinct from the 6-leg OS/Python CI matrix already recorded in
results/development_v12/cross_environment_determinism.json).

    docker build -t gcir .
    docker run --rm -v /tmp/env7_out:/out gcir \
        python -m experiments.run_determinism_v12 \
        --cases case_a case_b_v1_1 case_d_ccs1 --runs-per-case 31 \
        --phase development --output /out
    python -m experiments.check_environment_container_v12 /tmp/env7_out/determinism.json

Verifies a determinism.json produced by experiments.run_determinism_v12
INSIDE the Dockerfile-pinned container (python:3.11.11-slim-bookworm, pinned
by digest) against the three committed cases/<case>/expected/reference_hashes.json
files -- the same committed references the 155-run local (host) determinism
result and the 6-leg CI matrix are each independently checked against.

This is additional, recommended-but-secondary cross-environment evidence
(spec section 8), never conflated with the 155-run local determinism claim or
the 6-leg OS x Python CI matrix. It does not require network access or the
GitHub Actions runner; it runs on any host with Docker able to build the
repo's pinned Dockerfile, which is how the equivalent container leg was
produced for the historical (pre-v1.2) reproducibility.yml `container` job.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

CASES = ("case_a", "case_b_v1_1", "case_d_ccs0", "case_d_ccs1", "case_d_ccs2")


def committed_hash(case_id):
    path = os.path.join(REPO_ROOT, "cases", case_id, "expected", "reference_hashes.json")
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
        return data.get("payload_hash", data.get("canonical_payload_sha256"))


def check(determinism_path):
    with open(determinism_path, encoding="utf-8") as handle:
        document = json.load(handle)
    environment = document["environment"]
    result = document["result"]

    findings = []
    checks = []

    def record(name, passed, detail=""):
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            findings.append("%s -- %s" % (name, detail))
        print("  [%s] %-60s %s" % ("PASS" if passed else "FAIL", name, detail))

    record("container system is Linux", environment.get("system") == "Linux",
           environment.get("system"))
    record("container machine is aarch64", environment.get("machine") == "aarch64",
           environment.get("platform"))
    record("total_runs == 155 (31 per case x 5 cases)", result.get("total_runs") == 155,
           str(result.get("total_runs")))
    record("overall TD == 1.0 (155/155)", result["TD"]["value"] == 1.0,
           "%s/%s" % (result["TD"]["numerator"], result["TD"]["denominator"]))

    for case_id in CASES:
        expected = committed_hash(case_id)
        per_case = result["per_case"].get(case_id, {})
        actual = per_case.get("reference_hash")
        record("%s: 31/31 and hash matches committed reference" % case_id,
               per_case.get("TD", {}).get("value") == 1.0 and actual == expected,
               "%s (expected %s)" % (actual, expected))

    return {
        "checks": checks,
        "findings": findings,
        "passed": not findings,
        "failure_count": len(findings),
        "container_environment": environment,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("determinism_json",
                        help="path to a determinism.json produced INSIDE the container "
                             "by experiments.run_determinism_v12")
    parser.add_argument("--out", default=None,
                        help="write the verified artifact to "
                             "results/development_v12/environment_container_aarch64.json")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    print("=" * 78)
    print("check_environment_container_v12.py -- environment 7 (pinned Linux/aarch64 container)")
    print("=" * 78)

    report = check(args.determinism_json)

    print("\n" + "=" * 78)
    if report["passed"]:
        print("ENVIRONMENT-7 CONTAINER CHECK PASSED -- %d checks, 0 failures" % len(report["checks"]))
    else:
        print("ENVIRONMENT-7 CONTAINER CHECK FAILED -- %d of %d checks failed"
              % (report["failure_count"], len(report["checks"])))
        for finding in report["findings"]:
            print("  %s" % finding)
    print("=" * 78)

    if args.out:
        with open(args.determinism_json, encoding="utf-8") as handle:
            raw = json.load(handle)
        document = {
            "result_name": "environment_container_aarch64_v12",
            "phase": "development",
            "phase_note": "DEVELOPMENT result; not reportable.",
            "purpose": (
                "Environment 7 (pinned Linux/aarch64 container), distinct from the "
                "6-leg OS/Python CI matrix in cross_environment_determinism.json. "
                "Recommended-but-secondary evidence (spec section 8); the 155-run "
                "local determinism result is the primary local claim."
            ),
            "container_image": "gcir (built from the repo's pinned Dockerfile: "
                                "python:3.11.11-slim-bookworm, pinned by digest)",
            "environment": raw["environment"],
            "result": raw["result"],
            "verification": {k: v for k, v in report.items() if k != "container_environment"},
        }
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
        print("-> %s" % args.out)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
