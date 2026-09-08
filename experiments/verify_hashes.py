"""Verify the committed reference canonical payload hashes.

    python -m experiments.verify_hashes            # check
    python -m experiments.verify_hashes --write    # (re)write the reference file

This is the shortest end-to-end check of the artifact's central claim, and it is
what the cross-platform CI matrix runs on ubuntu, windows and macOS.  A mismatch
on any platform means the compiler is not deterministic across the tested
supported environments, and it fails the workflow.

The reference hashes live in ``cases/<case>/expected/reference_hashes.json`` and
are committed, so a reviewer is comparing against a value in the repository
rather than against whatever this run happens to produce.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys

from experiments.common import REPO_ROOT, environment, read_json

CASES = ("case_a", "case_b")


def reference_path(case_id):
    return os.path.join(REPO_ROOT, "cases", case_id, "expected", "reference_hashes.json")


def compile_case(case_id):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case(case_id)
    result = compile_bundle(case.compiler_inputs())
    return case, result


def write_references():
    written = {}
    for case_id in CASES:
        case, result = compile_case(case_id)
        bundle = result.bundle
        document = {
            "case_id": case_id,
            "case_class": read_json(
                os.path.join(REPO_ROOT, "cases", case_id, "inputs", "assessment.json")
            )["case_class"],
            "canonical_payload_sha256": bundle.payload_hash,
            "bundle_id": bundle.payload["bundle_id"],
            "version_binding_id": bundle.payload["version_binding"]["binding_id"],
            "catalog_content_sha256": bundle.payload["catalog_ref"]["content_hash"],
            "cstar_profile_content_sha256":
                bundle.payload["cstar_profile_ref"]["content_hash"],
            "predicate_count": len(bundle.predicates),
            "disposition_count": len(bundle.dispositions),
            "note": (
                "SHA-256 over the RFC 8785 canonical serialization of the immutable "
                "bundle payload. The signature envelope is NOT part of this hash and "
                "is not required to be byte-identical across signing events "
                "(manuscript Section VI-C)."
            ),
        }
        path = reference_path(case_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written[case_id] = bundle.payload_hash
        print("wrote %s" % os.path.relpath(path, REPO_ROOT))
    return written


def verify():
    env = environment()
    print("platform: %s  python: %s" % (env["platform"], env["python_version"]))
    print("locale env: LANG=%s LC_ALL=%s TZ=%s"
          % (os.environ.get("LANG"), os.environ.get("LC_ALL"), os.environ.get("TZ")))
    print("")

    failures = []
    for case_id in CASES:
        path = reference_path(case_id)
        if not os.path.exists(path):
            failures.append("%s: no committed reference hash at %s" % (case_id, path))
            continue
        expected = read_json(path)
        case, result = compile_case(case_id)
        actual = result.bundle.payload_hash
        match = actual == expected["canonical_payload_sha256"]
        print("%-8s expected %s" % (case_id, expected["canonical_payload_sha256"]))
        print("%-8s actual   %s   %s"
              % ("", actual, "MATCH" if match else "MISMATCH <<<"))
        if not match:
            failures.append("%s: expected %s, got %s"
                            % (case_id, expected["canonical_payload_sha256"], actual))
        for key, value in (
            ("catalog_content_sha256", result.bundle.payload["catalog_ref"]["content_hash"]),
            ("cstar_profile_content_sha256",
             result.bundle.payload["cstar_profile_ref"]["content_hash"]),
            ("predicate_count", len(result.bundle.predicates)),
            ("disposition_count", len(result.bundle.dispositions)),
        ):
            if expected.get(key) != value:
                failures.append("%s: %s expected %r, got %r"
                                % (case_id, key, expected.get(key), value))
        print("")

    if failures:
        print("FAILED:")
        for failure in failures:
            print("  %s" % failure)
        return 1
    print("All committed reference hashes verified on this platform.")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="(re)write the committed reference hash files")
    args = parser.parse_args(argv)
    if args.write:
        write_references()
        return 0
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
