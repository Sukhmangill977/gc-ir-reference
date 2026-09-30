"""Write cases/case_d_<ccsN>/expected/reference_hashes.json for every Case D
CCS variant, by actually compiling each one (never a hand-typed hash).

    python -m tools.write_case_d_reference_hashes
    python -m tools.write_case_d_reference_hashes --check   # verify only, write nothing

Companion to tools/build_case_d.py, which regenerates the case TREES
(inputs/acs/dispositions/judgment); this script regenerates the committed
CANONICAL HASH each tree compiles to, for cases/case_d_ccs0/ and
cases/case_d_ccs2/ (cases/case_d_ccs1/expected/reference_hashes.json already
existed and is left untouched unless it no longer matches its own tree,
which would itself be a finding to report, not silently fix).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

NOTES = {
    "case_d_ccs0": (
        "Case D CCS0: emergency-exception path disabled -- ordinary ACS-D01-01 "
        "(dual authorization) only, no ACS-D02-01 (Paper 2 v1.2 spec section 4, "
        "D2/D3). 1 risk-derived + 3 compiler-invariant = 4 total predicates. "
        "Development artifact; not part of any frozen preregister-tier0 campaign."
    ),
    "case_d_ccs2": (
        "Case D CCS2: policy 4.3 / J' widens the emergency-exception authorized "
        "actor set to include the ETA-2-tier payments analyst alongside the "
        "Treasury Officer credential (Paper 2 v1.2 spec section 4, D9). "
        "ACS-D01-01 (ordinary dual authorization) + ACS-D02-01 (widened "
        "emergency exception, policy POL-D-EMERGENCY-EXCEPTION-4.3) = 2 "
        "risk-derived + 3 compiler-invariant = 5 total predicates. Canonical "
        "payload hash differs from CCS1 by design (widened authorized-actor "
        "set); CCS1's judgment reference is not current for CCS2's state. "
        "Development artifact; not part of any frozen preregister-tier0 campaign."
    ),
}

TARGETS = ("case_d_ccs0", "case_d_ccs2")


def compile_hash(case_id):
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle
    case = load_case(case_id)
    result = compile_bundle(case.compiler_inputs())
    return result.bundle.payload_hash, result.bundle.payload.get("schema_version")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                         help="verify existing files match a fresh compile; write nothing")
    args = parser.parse_args(argv)

    ok = True
    for case_id in TARGETS:
        payload_hash, schema_version = compile_hash(case_id)
        out_path = os.path.join(REPO_ROOT, "cases", case_id, "expected", "reference_hashes.json")
        document = {
            "case_id": case_id,
            "schema_version": schema_version,
            "payload_hash": payload_hash,
            "note": NOTES[case_id],
        }
        if args.check:
            if not os.path.exists(out_path):
                print("  [FAIL] %-14s no reference_hashes.json to check" % case_id)
                ok = False
                continue
            with open(out_path, encoding="utf-8") as fh:
                existing = json.load(fh)
            matched = existing.get("payload_hash") == payload_hash
            print("  [%s] %-14s %s" % ("PASS" if matched else "FAIL", case_id, payload_hash))
            ok = ok and matched
        else:
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(document, fh, indent=2, sort_keys=True, ensure_ascii=False)
                fh.write("\n")
            print("  [WROTE] %-14s %s -> %s" % (case_id, payload_hash, out_path))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
