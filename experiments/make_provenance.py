"""Generate ``results/final_v2/PROVENANCE.json``.

    python -m experiments.make_provenance --final-v2

Every reported empirical value must be traceable to the state that produced it.
This collects, for the campaign in a results directory:

  * the freeze tag and freeze commit that governed it
  * the **public** GitHub reference, and whether the remote tag actually
    dereferences to that freeze commit
  * the execution commit every result file recorded
  * the environment
  * every result file, with its SHA-256
  * the headline measured values, read back from those files

The ordering claim -- freeze published *before* execution -- is not asserted
here; it is recomputed by ``experiments/verify_freeze.py`` and its verdict is
embedded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess

from experiments.common import (
    REPO_ROOT,
    add_common_args,
    environment,
    phase_of,
    read_json,
    results_dir,
)


def git(*args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=REPO_ROOT, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return None


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _result(directory, name):
    path = os.path.join(directory, name)
    if not os.path.exists(path):
        return None
    blob = read_json(path)
    return blob.get("result", blob)


def build(directory, freeze_tag):
    freeze_commit = git("rev-list", "-n", "1", freeze_tag)
    remote_url = git("remote", "get-url", "origin")
    listing = git("ls-remote", "origin",
                  "refs/tags/%s" % freeze_tag,
                  "refs/tags/%s^{}" % freeze_tag) or ""
    remote_tag_object = None
    remote_tag_commit = None
    for line in listing.splitlines():
        sha, ref = line.split("\t", 1)
        if ref.endswith("^{}"):
            remote_tag_commit = sha
        else:
            remote_tag_object = sha

    files = []
    for root, _, names in os.walk(directory):
        for name in sorted(names):
            path = os.path.join(root, name)
            files.append({
                "path": os.path.relpath(path, REPO_ROOT),
                "sha256": sha256_file(path),
                "bytes": os.path.getsize(path),
            })
    files.sort(key=lambda row: row["path"])

    execution_commits = set()
    for row in files:
        if not row["path"].endswith(".json"):
            continue
        try:
            blob = read_json(os.path.join(REPO_ROOT, row["path"]))
        except Exception:
            continue
        commit = (blob.get("environment") or {}).get("git_commit")
        if commit:
            execution_commits.add(commit)

    metrics = _result(directory, "metrics.json")
    determinism = _result(directory, "determinism_summary.json")
    monte = _result(directory, "monte_carlo_summary.json")
    adversarial = _result(directory, "adversarial.json")
    properties = _result(directory, "property_tests.json")
    traceability = _result(directory, "traceability_queries.json")
    case_a = _result(directory, "case_a/compilation.json")
    case_b = _result(directory, "case_b/compilation.json")
    freeze = None
    freeze_path = os.path.join(directory, "freeze_verification.json")
    if os.path.exists(freeze_path):
        freeze = read_json(freeze_path)

    headline = {}
    if metrics:
        for case_id in ("case_a", "case_b"):
            entry = metrics["per_case"][case_id]
            headline[case_id] = {
                name: entry[name]["value"]
                for name in ("DC", "RCY", "NDR", "OPR", "ODC", "PTC", "CV")
            }
            headline[case_id]["GD"] = entry["GD"]["value"]
            headline[case_id]["GD_min"] = entry["GD_min"]["value"]
            headline[case_id]["declared_threshold"] = entry["GD"]["declared_threshold"]
    if determinism:
        headline["TD"] = {
            "value": determinism["TD"]["value"],
            "numerator": determinism["TD"]["numerator"],
            "denominator": determinism["TD"]["denominator"],
            "runs_per_case": determinism.get("runs_per_case"),
            "stratum_breakdown": determinism.get("stratum_breakdown"),
        }
    if monte:
        headline["monte_carlo"] = {
            case_id: {
                "draws_K": monte["per_case"][case_id]["draws_K"],
                "max_FP_heat": monte["per_case"][case_id]["max_FP_heat"]["value"],
                "max_FP_heat_mcse": monte["per_case"][case_id]["max_FP_heat"]["mcse"],
                "max_FP_cstar": monte["per_case"][case_id]["max_FP_cstar"],
            }
            for case_id in ("case_a", "case_b")
        }
    if case_a and case_b:
        headline["payload_hashes"] = {
            "case_a": case_a["payload_hash"], "case_b": case_b["payload_hash"],
        }
    if adversarial:
        headline["adversarial"] = {
            "corpus": adversarial["corpus"]["total"],
            "passed": adversarial["corpus"]["passed"],
            "structural": "%d/%d" % (adversarial["structural_checks"]["passed"],
                                     adversarial["structural_checks"]["total"]),
            "case_b_injections": "%d/%d" % (
                adversarial["case_b_injection_scenarios"]["passed"],
                adversarial["case_b_injection_scenarios"]["scenario_count"]),
        }
    if properties:
        headline["tests"] = properties["totals"]
    if traceability:
        headline["traceability"] = {
            "all_clean_empty": traceability["summary"]["all_clean_queries_empty"],
            "all_controls_detected":
                traceability["summary"]["all_negative_controls_detected"],
        }

    mapping_path = os.path.join(REPO_ROOT, "cases", "case_b", "ldrea_traceability.json")
    ldrea = None
    if os.path.exists(mapping_path):
        blob = read_json(mapping_path)
        ldrea = {
            "external_repository": blob["external_artifact"]["repository"],
            "external_commit": blob["external_artifact"]["commit"],
            "predicate_family_size": blob["ldrea_predicate_family"]["size"],
            "rows": blob["summary"]["rows"],
            "by_correspondence": blob["summary"]["by_correspondence"],
            "verification_failures": blob["summary"]["failed"],
            "mapping_file_sha256": sha256_file(mapping_path),
        }

    return {
        "document_type": "CampaignProvenance",
        "campaign": os.path.basename(directory.rstrip("/")),
        "public_freeze": {
            "tag": freeze_tag,
            "freeze_commit": freeze_commit,
            "remote_url": remote_url,
            "remote_tag_object": remote_tag_object,
            "remote_tag_commit": remote_tag_commit,
            "remote_tag_matches_freeze_commit": remote_tag_commit == freeze_commit,
            "remote_tag_verified": bool(remote_tag_commit)
            and remote_tag_commit == freeze_commit,
            "public_url": ("%s/releases/tag/%s"
                           % ((remote_url or "").removesuffix(".git"), freeze_tag))
            if remote_url else None,
            "note": "The commitment is the PUBLIC tag. Its presence on the remote, "
                    "dereferencing to the freeze commit, is what discharges "
                    "Section XI-I -- not the local tag's date.",
        },
        "execution": {
            "commits_recorded_in_result_files": sorted(execution_commits),
            "environment": environment(),
        },
        "freeze_verification": freeze,
        "headline_measurements": headline,
        "case_b_ldrea_traceability": ldrea,
        "result_files": files,
        "result_file_count": len(files),
        "manifest_sha256": (read_json(os.path.join(REPO_ROOT, "MANIFEST.json"))
                            ["manifest_sha256"]
                            if os.path.exists(os.path.join(REPO_ROOT, "MANIFEST.json"))
                            else None),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="preregister-tier0-v2.1")
    add_common_args(parser)
    args = parser.parse_args(argv)

    directory = results_dir(phase_of(args))
    document = build(directory, args.tag)
    path = os.path.join(directory, "PROVENANCE.json")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("wrote %s" % os.path.relpath(path, REPO_ROOT))
    print("  freeze tag        : %s -> %s"
          % (args.tag, (document["public_freeze"]["freeze_commit"] or "?")[:12]))
    print("  remote tag verified: %s" % document["public_freeze"]["remote_tag_verified"])
    print("  execution commits : %s"
          % ", ".join(c[:12] for c in document["execution"]
                      ["commits_recorded_in_result_files"]))
    print("  result files      : %d" % document["result_file_count"])
    return 0 if document["public_freeze"]["remote_tag_verified"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
