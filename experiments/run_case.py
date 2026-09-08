"""Compile a case end to end and write every emitted artifact.

    python -m experiments.run_case --case case_a [--final]

Writes, per case:
  bundle.json            the immutable payload plus its signature envelope
  payload_hash.txt       SHA-256 over the RFC 8785 canonical payload
  canonical_payload.json the exact canonical bytes that were hashed
  gcir_records.json      the GC-IR record family emitted (predicates + dispositions)
  gate_map.json          G
  escalation_map.json    E
  coverage_matrix.json   CM, including the C* coverage rows
  payload_purity.json    the Appendix A constraint 13 audit of the payload
  compilation.json       statistics, warnings and the schema-validation outcome
"""

from __future__ import annotations

import argparse
import json
import os

from experiments.common import (
    REPO_ROOT,
    add_common_args,
    environment,
    load_case_bundle,
    read_json,
    results_dir,
    write_result,
)


def run(case_id, final):
    from gcir.canonicalization import canonical_json_string, hash_payload
    from gcir.compiler import sign_bundle
    from gcir.validation import (
        FORBIDDEN_PAYLOAD_KEYS,
        constraint_13_payload_is_hash_clean,
        validate_document,
    )

    case, inputs, result = load_case_bundle(case_id)
    bundle = result.bundle
    parameters = case.parameters

    validate_document(bundle.payload, "bundle.schema.json", label="%s bundle" % case_id)
    for record in bundle.predicates + bundle.dispositions:
        validate_document(record, "gcir.schema.json", label="%s %s" % (case_id, record.get("gcir_id") or record.get("risk_id")))

    constraint_13_payload_is_hash_clean(bundle.payload)

    # Sign the bundle.  The envelope lives outside the payload; signing does not
    # change payload_hash.
    hash_before = bundle.payload_hash
    sign_bundle(bundle, case.keyring, parameters["bundle_signing_key"],
                signing_time="2026-02-02T09:05:00Z")
    assert hash_payload(bundle.payload) == hash_before, (
        "signing must not perturb the payload hash"
    )

    out_dir = os.path.join(results_dir(final), case_id)
    os.makedirs(out_dir, exist_ok=True)

    def dump(name, document):
        path = os.path.join(out_dir, name)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
        return path

    dump("bundle.json", {"payload": bundle.payload, "payload_hash": bundle.payload_hash,
                         "signature_envelope": bundle.envelope})
    dump("gcir_records.json", {"predicates": bundle.predicates,
                               "dispositions": bundle.dispositions})
    dump("gate_map.json", bundle.gate_map)
    dump("escalation_map.json", bundle.escalation_map)
    dump("coverage_matrix.json", bundle.coverage_matrix)

    canonical = canonical_json_string(bundle.payload)
    with open(os.path.join(out_dir, "canonical_payload.json"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(canonical)
    with open(os.path.join(out_dir, "payload_hash.txt"), "w",
              encoding="utf-8", newline="\n") as handle:
        handle.write(bundle.payload_hash + "\n")

    purity = {
        "forbidden_keys_checked": sorted(FORBIDDEN_PAYLOAD_KEYS),
        "offenders": [],
        "canonical_payload_bytes": len(canonical.encode("utf-8")),
        "payload_hash": bundle.payload_hash,
        "signature_envelope_outside_payload": "signature" not in bundle.payload,
        "envelope_signing_time": (bundle.envelope or {}).get("signing_time"),
        "hash_unchanged_by_signing": hash_payload(bundle.payload) == hash_before,
    }
    dump("payload_purity.json", purity)

    summary = {
        "case_id": case_id,
        "case_class": read_json(os.path.join(REPO_ROOT, "cases", case_id, "inputs",
                                             "assessment.json"))["case_class"],
        "payload_hash": bundle.payload_hash,
        "signature_envelope": bundle.envelope,
        "statistics": result.statistics,
        "warnings": result.warnings,
        "schema_validation": {
            "bundle": "pass",
            "gcir_records": "pass",
            "record_count": len(bundle.predicates) + len(bundle.dispositions),
        },
        "declared_heatmap_threshold": parameters["declared_heatmap_threshold"],
        "compile_time_declared": parameters["compile_time"],
        "output_dir": os.path.relpath(out_dir, REPO_ROOT),
    }
    write_result(final, os.path.join(case_id, "compilation"), summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", default=None, help="case_a, case_b, or omit for both")
    add_common_args(parser)
    args = parser.parse_args(argv)

    cases = [args.case] if args.case else ["case_a", "case_b"]
    summaries = {}
    for case_id in cases:
        summary = run(case_id, args.final)
        summaries[case_id] = summary
        print("%s: payload_hash=%s predicates=%d warnings=%d"
              % (case_id, summary["payload_hash"],
                 summary["statistics"]["predicate_count"],
                 len(summary["warnings"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
