"""Verify every paper-facing empirical result against the final_v2 evidence.

    python tools/verify_reported_results.py           # human-readable
    python tools/verify_reported_results.py --json    # machine-readable
    python tools/verify_reported_results.py --quiet   # failures only

One command for an IEEE reviewer: confirm that every number the article reports
agrees with the machine-generated evidence in ``results/final_v2/``.  Exits
non-zero on any disagreement.

How it works, and what that is worth
------------------------------------

``artifact_review/PAPER_RESULT_MAP.json`` is the declarative mapping.  For each
entry it names a result file and the exact JSON path holding the value.  This
script opens that file, walks that path, and compares what it finds against the
entry's ``expected``.  Nothing is recomputed from the answer, and no expected
value is written into this file.

The map is *generated* from the same result files, so on its own that comparison
would only prove the map is a faithful snapshot -- which is worth something (it
catches a result file edited after the map was built, in either direction) but
is not independent.  So this script additionally runs **cross-checks against
sources the map does not read**:

  * committed reference hashes in ``cases/*/expected/reference_hashes.json``
  * the standalone ``payload_hash.txt`` written beside each compiled bundle
  * the SHA-256 of each ``canonical_payload.json``, hashed here, byte for byte
  * per-leg cross-environment determinism JSON from the CI matrix
  * the freeze commit recorded in the git tag itself
  * internal agreement between result files that were produced independently

A cross-check compares two things that were written by different code paths, so
agreement between them is evidence; the map cannot manufacture it.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_PATH = os.path.join(REPO_ROOT, "artifact_review", "PAPER_RESULT_MAP.json")

#: Floating-point results are compared exactly by default.  These are the only
#: quantities compared with a tolerance, and each says why.
TOLERANCES = {
    # MCSE is a derived square root; the last ULP is not a paper-facing claim.
    "MC-MCSE": 1e-12,
}


class Check:
    """One verification, with everything needed to explain a failure.

    Three states, not two. ``skipped`` means *this environment cannot verify the
    claim* -- for example a tagless CI checkout, where the freeze tag simply is
    not present. That is not the same as the claim being wrong, and conflating
    the two would either fail honest checkouts or hide real disagreements. A
    skipped check never fails the run; a failed one always does.
    """

    def __init__(self, label, passed, detail="", kind="map", skipped=False):
        self.label = label
        self.passed = passed or skipped
        self.skipped = skipped
        self.detail = detail
        self.kind = kind

    @property
    def status(self):
        return "SKIP" if self.skipped else ("PASS" if self.passed else "FAIL")

    def as_dict(self):
        return {"check": self.label, "passed": self.passed,
                "skipped": self.skipped, "status": self.status,
                "detail": self.detail, "kind": self.kind}


def load_json(relative):
    with open(os.path.join(REPO_ROOT, relative), encoding="utf-8") as handle:
        return json.load(handle)


def resolve(blob, path):
    """Walk a dotted path, returning (found, value)."""
    node = blob
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return False, None
        node = node[part]
    return True, node


def equal(expected, actual, tolerance):
    if isinstance(expected, bool) or isinstance(actual, bool):
        return expected is actual or expected == actual
    if isinstance(expected, float) and isinstance(actual, (int, float)):
        if tolerance:
            return abs(expected - actual) <= tolerance
        return float(expected) == float(actual)
    if isinstance(expected, (list, dict)):
        return expected == actual
    return expected == actual


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# --------------------------------------------------------------------------
# map-driven verification
# --------------------------------------------------------------------------

def verify_map(entries):
    checks = []
    cache = {}
    for entry in entries:
        label = "%s = %s" % (entry["metric"], entry["reported"])

        if entry["id"] == "XENV":
            # Not a single JSON field: it is an agreement claim over eight
            # environments. Cross-check 5 verifies it properly, by opening every
            # per-leg summary. Recorded here so the entry is never silently
            # dropped from the count.
            checks.append(Check(label, True,
                                "verified by cross-check: all cross-environment "
                                "legs agree (see below)"))
            continue

        relative = entry["result_file"]
        if not relative.endswith(".json"):
            checks.append(Check(label, False,
                                "result file is not JSON: %s" % relative))
            continue
        if not os.path.exists(os.path.join(REPO_ROOT, relative)):
            checks.append(Check(label, False, "missing result file %s" % relative))
            continue
        if relative not in cache:
            cache[relative] = load_json(relative)

        found, actual = resolve(cache[relative], entry["field"])
        if not found:
            checks.append(Check(label, False, "field %s not present in %s"
                                % (entry["field"], relative)))
            continue

        expected = entry["expected"]
        if equal(expected, actual, TOLERANCES.get(entry["id"])):
            checks.append(Check(label, True, "%s : %s" % (relative, entry["field"])))
        else:
            checks.append(Check(label, False,
                                "expected %r but %s:%s holds %r"
                                % (expected, relative, entry["field"], actual)))
    return checks


# --------------------------------------------------------------------------
# independent cross-checks -- these read sources the map does not
# --------------------------------------------------------------------------

def cross_checks():
    checks = []

    def record(label, passed, detail="", skipped=False):
        checks.append(Check(label, passed, detail, kind="cross-check",
                            skipped=skipped))

    # 1. the compiled hash, the committed reference, the standalone hash file,
    #    and a hash computed here from the canonical bytes must all agree.
    for case in ("case_a", "case_b"):
        compiled = load_json("results/final_v2/%s/compilation.json" % case)
        compiled = compiled.get("result", compiled)["payload_hash"]

        reference = load_json(
            "cases/%s/expected/reference_hashes.json" % case
        )["canonical_payload_sha256"]

        hash_file = os.path.join(REPO_ROOT, "results/final_v2", case,
                                 "payload_hash.txt")
        standalone = None
        if os.path.exists(hash_file):
            with open(hash_file, encoding="utf-8") as handle:
                standalone = handle.read().strip()

        payload = os.path.join(REPO_ROOT, "results/final_v2", case,
                               "canonical_payload.json")
        recomputed = sha256_file(payload) if os.path.exists(payload) else None

        agree = (compiled == reference == standalone == recomputed)
        record("%s hash agrees across 4 independent sources" % case, agree,
               compiled if agree else
               "compiled=%s reference=%s file=%s recomputed=%s"
               % (compiled, reference, standalone, recomputed))

    # 2. the determinism experiment's reference hash must equal the compiled one
    determinism = load_json("results/final_v2/determinism_summary.json")
    determinism = determinism.get("result", determinism)
    for case in ("case_a", "case_b"):
        compiled = load_json("results/final_v2/%s/compilation.json" % case)
        compiled = compiled.get("result", compiled)["payload_hash"]
        record("%s determinism reference hash matches the compiled bundle" % case,
               determinism["per_case"][case]["reference_hash"] == compiled,
               determinism["per_case"][case]["reference_hash"])

    # 3. TD's numerator and denominator must equal the per-case run totals
    total_runs = sum(determinism["per_case"][c]["runs"] for c in ("case_a", "case_b"))
    total_matches = sum(determinism["per_case"][c]["matches"]
                        for c in ("case_a", "case_b"))
    record("TD denominator equals the sum of per-case runs",
           determinism["TD"]["denominator"] == total_runs,
           "%d == %d" % (determinism["TD"]["denominator"], total_runs))
    record("TD numerator equals the sum of per-case matches",
           determinism["TD"]["numerator"] == total_matches,
           "%d == %d" % (determinism["TD"]["numerator"], total_matches))
    strata = sum(determinism["stratum_breakdown"].values())
    record("stratum breakdown sums to the runs per case",
           strata == determinism["runs_per_case"],
           "%d == %d" % (strata, determinism["runs_per_case"]))

    # 4. every determinism run row in the CSV must carry the reference hash
    csv_path = os.path.join(REPO_ROOT, "results/final_v2/determinism_runs.csv")
    if os.path.exists(csv_path):
        import csv as csv_mod

        with open(csv_path, encoding="utf-8", newline="") as handle:
            rows = list(csv_mod.DictReader(handle))
        needed = {"case", "hash", "reference_hash", "pass"}
        if rows and needed.issubset(rows[0]):
            # Two independent conditions: the row's own hash equals the row's own
            # reference, AND that reference equals the summary's. A CSV rewritten
            # consistently with itself would still fail the second.
            self_consistent = [r for r in rows if r["hash"] != r["reference_hash"]]
            against_summary = [
                r for r in rows
                if r["reference_hash"]
                != determinism["per_case"][r["case"]]["reference_hash"]
            ]
            record("all %d determinism CSV rows carry the reference hash" % len(rows),
                   not self_consistent and not against_summary
                   and len(rows) == total_runs,
                   "%d rows, %d self-inconsistent, %d disagreeing with the summary"
                   % (len(rows), len(self_consistent), len(against_summary)))
            record("every determinism CSV row is marked passing",
                   all(str(r["pass"]).strip().upper() == "PASS"
                       for r in rows),
                   "%d rows" % len(rows))
        else:
            record("determinism CSV has the expected columns", False,
                   "columns: %s" % (list(rows[0]) if rows else "empty"))

    # 5. cross-environment: every CI leg reproduced the same hashes at TD = 1.0
    legs = sorted(glob.glob(os.path.join(
        REPO_ROOT, "results/final_v2/cross_environment/ci/*/determinism_summary.json")))
    container = os.path.join(
        REPO_ROOT,
        "results/final_v2/cross_environment/determinism_summary_container_linux.json")
    if os.path.exists(container):
        legs.append(container)
    disagreeing = []
    for leg in legs:
        with open(leg, encoding="utf-8") as handle:
            blob = json.load(handle)
        blob = blob.get("result", blob)
        if blob["TD"]["value"] != 1.0:
            disagreeing.append("%s: TD=%s" % (os.path.basename(os.path.dirname(leg)),
                                              blob["TD"]["value"]))
            continue
        for case in ("case_a", "case_b"):
            if blob["per_case"][case]["reference_hash"] != \
                    determinism["per_case"][case]["reference_hash"]:
                disagreeing.append("%s: %s hash differs"
                                   % (os.path.basename(os.path.dirname(leg)), case))
    record("all %d cross-environment legs agree (TD = 1.0, identical hashes)"
           % len(legs), bool(legs) and not disagreeing,
           "; ".join(disagreeing) if disagreeing else
           "%d legs, every reference hash identical" % len(legs))

    # 6. the freeze commit recorded in the results must be what the git tag says
    provenance = load_json("results/final_v2/PROVENANCE.json")
    freeze = provenance["freeze_verification"]
    tag = freeze["freeze_tag"]
    resolved = subprocess.run(
        ["git", "rev-list", "-n", "1", tag],
        cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if resolved.returncode == 0 and resolved.stdout.strip():
        actual_commit = resolved.stdout.decode().strip()
        record("git tag %s resolves to the recorded freeze commit" % tag,
               actual_commit == freeze["freeze_commit"],
               actual_commit)
    else:
        # A tagless or shallow checkout -- CI's `tests` workflow uses one -- simply
        # cannot answer this. Skipped, not failed: absence of the tag is not
        # evidence that the recorded freeze commit is wrong.
        record("git tag %s resolves to the recorded freeze commit" % tag, False,
               "tag not present in this checkout (shallow or tagless clone); "
               "run in a full clone to verify", skipped=True)

    # 7. metrics recorded per case must agree with the compiled bundle's own counts
    metrics = load_json("results/final_v2/metrics.json")
    metrics = metrics.get("result", metrics)
    for case in ("case_a", "case_b"):
        compilation = load_json("results/final_v2/%s/compilation.json" % case)
        compilation = compilation.get("result", compilation)
        predicates = compilation["statistics"]["predicate_count"]
        recorded = metrics["per_case"][case]["PTC"]["denominator"]
        record("%s PTC denominator equals the compiled predicate count" % case,
               predicates == recorded, "%d == %d" % (recorded, predicates))
        record("%s OPR denominator equals the compiled predicate count" % case,
               metrics["per_case"][case]["OPR"]["denominator"] == predicates,
               "%d == %d" % (metrics["per_case"][case]["OPR"]["denominator"],
                             predicates))

    # 8. gate divergence must agree between its own file and the metrics file
    divergence = load_json("results/final_v2/gate_divergence.json")
    divergence = divergence.get("result", divergence)
    for case in ("case_a", "case_b"):
        record("%s GD agrees between gate_divergence.json and metrics.json" % case,
               divergence["per_case"][case]["GD_at_declared_threshold"]
               == metrics["per_case"][case]["GD"]["value"],
               str(metrics["per_case"][case]["GD"]["value"]))
        record("%s GD_min agrees between gate_divergence.json and metrics.json"
               % case,
               divergence["per_case"][case]["GD_min"]
               == metrics["per_case"][case]["GD_min"]["value"],
               str(metrics["per_case"][case]["GD_min"]["value"]))

    # 9. no deferred quantity may have acquired a value
    mapping = load_json("artifact_review/PAPER_RESULT_MAP.json")
    deferred_leak = [d["quantity"] for d in mapping["deferred"]
                     if any(e["metric"] == d["metric"] for e in mapping["entries"])]
    record("no deferred quantity appears as a reported result",
           not deferred_leak,
           "leaked: %s" % deferred_leak if deferred_leak else
           "%d deferred quantities, none reported" % len(mapping["deferred"]))

    # 10. RQ5 must still be deferred in the result files themselves.
    #     SNR and DF are PRESENT in metrics.json, under a `deferred` block -- that
    #     is correct and deliberate. What must hold is that neither ever acquires
    #     a value: a fabricated study result would show up here as a non-null.
    for case in ("case_a", "case_b"):
        deferred = metrics["per_case"][case].get("deferred", {})
        present = sorted(deferred)
        null_valued = all(deferred[k].get("value") is None
                          and deferred[k].get("status") == "DEFERRED"
                          for k in deferred)
        record("%s: SNR and DF are recorded as DEFERRED with no value" % case,
               present == ["DF", "SNR"] and null_valued,
               "declared %s, all status=DEFERRED value=null" % present
               if null_valued else "a deferred quantity has acquired a value")

    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON on stdout")
    parser.add_argument("--quiet", action="store_true", help="print failures only")
    parser.add_argument("--map", default=MAP_PATH)
    args = parser.parse_args(argv)

    if not os.path.exists(args.map):
        print("ERROR: %s not found. Generate it with "
              "`python -m tools.build_paper_result_map`." % args.map,
              file=sys.stderr)
        return 2

    with open(args.map, encoding="utf-8") as handle:
        mapping = json.load(handle)

    if not args.json:
        print("=" * 78)
        print("verify_reported_results.py -- paper-facing results vs %s"
              % mapping["results_dir"])
        print("freeze %s @ %s" % (mapping["freeze_tag"],
                                  mapping["freeze_commit"][:12]))
        print("=" * 78)

    checks = verify_map(mapping["entries"])
    if not args.json:
        print("\nReported results (%d)\n" % len(checks))
        for check in checks:
            if check.passed and not check.skipped and args.quiet:
                continue
            print("  %-4s %s" % (check.status, check.label))
            if not check.passed or check.skipped:
                print("       %s" % check.detail)

    crosses = cross_checks()
    if not args.json:
        print("\nIndependent cross-checks (%d)\n" % len(crosses))
        for check in crosses:
            if check.passed and not check.skipped and args.quiet:
                continue
            print("  %-4s %s" % (check.status, check.label))
            print("       %s" % check.detail)

    every = checks + crosses
    failed = [c for c in every if not c.passed]
    skipped = [c for c in every if c.skipped]

    if args.json:
        print(json.dumps({
            "results_dir": mapping["results_dir"],
            "freeze_tag": mapping["freeze_tag"],
            "reported_result_count": len(checks),
            "cross_check_count": len(crosses),
            "passed": len(every) - len(failed) - len(skipped),
            "failed": len(failed),
            "skipped": len(skipped),
            "all_ok": not failed,
            "checks": [c.as_dict() for c in every],
        }, indent=2, sort_keys=True))
    else:
        print("\n" + "=" * 78)
        if failed:
            print("FAILED -- %d of %d checks disagree with the evidence"
                  % (len(failed), len(every)))
            for check in failed:
                print("  %s: %s" % (check.label, check.detail))
        else:
            print("%d/%d paper-facing empirical claims verified, "
                  "%d independent cross-checks passed%s"
                  % (len(checks), len(checks), len(crosses) - len(skipped),
                     "" if not skipped
                     else ", %d skipped (not verifiable here)" % len(skipped)))
            for check in skipped:
                print("  SKIP %s -- %s" % (check.label, check.detail))
            print("evidence: %s at freeze %s"
                  % (mapping["results_dir"], mapping["freeze_tag"]))
        print("=" * 78)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
