"""Regenerate the committed case artifacts under ``cases/``.

The JSON files this writes are the *artifact of record*; this script exists so a
reviewer can see exactly how each field was constructed and can regenerate the
tree byte-for-byte.  CI checks that a regeneration produces no diff.

    python -m tools.build_cases

Determinism: the research signing keys are derived from a fixed seed string, so
the generated public keys and signatures are reproducible from a fresh clone.
The keys are TEST ONLY / NOT FOR PRODUCTION.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from gcir.canonicalization import canonical_json_string  # noqa: E402
from gcir.signatures import KeyRing  # noqa: E402

from tools import case_a_control, case_a_data, case_b_control, case_b_data  # noqa: E402
from tools.invariants_data import build_invariant_register  # noqa: E402

#: Fixed derivation seed for the research keys.  Recorded in
#: docs/FIXTURE_PROVENANCE.md (FP-030).  TEST ONLY / NOT FOR PRODUCTION.
KEY_SEED = "gc-ir-reference research fixture keys v1 -- TEST ONLY, NOT FOR PRODUCTION"

KEY_IDS = [
    "key.governance_forum_a",
    "key.governance_forum_b",
    "key.assessor",
    "key.lifecycle_authority_a",
    "key.lifecycle_authority_b",
    "key.runtime_authority_a",
    "key.runtime_authority_b",
    "key.unauthorized_party",
]


def write_json(path, document):
    """Write a document as pretty JSON with sorted keys and a trailing newline."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")
    return path


def sign_document(keyring, document, key_id, domain, signing_time):
    """Attach a detached signature over the document minus its signature field."""
    body = {k: v for k, v in document.items() if k != "signature"}
    document["signature"] = keyring.sign(
        body, key_id, domain=domain, signing_time=signing_time
    )
    return document


# ---------------------------------------------------------------------------


def build_case_a(keyring, out_dir):
    d = case_a_data
    c = case_a_control

    assessment = {
        "assessment_id": "ASSESSMENT-CASE-A",
        "case_class": "synthetic",
        "metadata": d.METADATA,
        "system_profile": d.SYSTEM_PROFILE,
        "obligations": d.OBLIGATIONS,
        "risk_register": d.build_risk_register(),
        "risk_analysis": d.build_risk_analysis(),
    }
    sign_document(keyring, assessment, "key.assessor", "assessment", "2026-01-20T09:00:00Z")

    catalog = dict(c.CATALOG)
    sign_document(keyring, catalog, "key.governance_forum_a", "catalog", "2026-01-20T14:05:00Z")

    cstar = dict(c.CSTAR_PROFILE)
    sign_document(keyring, cstar, "key.governance_forum_a", "cstar_profile", "2026-01-20T14:06:00Z")

    acs_records = c.build_acs_records()
    acs_set = {
        "acs_set_id": "D-CASE-A",
        "version_binding_ref": d.BINDING,
        "records": acs_records,
    }
    sign_document(keyring, acs_set, "key.governance_forum_a", "acs", "2026-01-20T14:10:00Z")

    judgment = c.build_judgment_record(acs_records)
    sign_document(keyring, judgment, "key.governance_forum_a", "judgment_record", "2026-01-20T14:08:00Z")

    dispositions = {
        "disposition_set_id": "DELTA-CASE-A",
        "version_binding_ref": d.BINDING,
        "records": c.build_dispositions(),
    }
    sign_document(keyring, dispositions, "key.governance_forum_a", "dispositions", "2026-01-20T14:12:00Z")

    invariants = build_invariant_register(
        register_id="INV-CASE-A",
        binding=d.BINDING,
        approver=d.FORUM,
        approval_time=d.APPROVAL_TIME,
        effective_from=d.EFFECTIVE_FROM,
        action_tuple=d.PUBLISH,
        parameter_schema_ref="PS-PUBLISH-REPORT",
        action_parameters=c.PUBLISH_PARAMS,
        fingerprint=d.METADATA["version_binding"]["fingerprint"],
    )
    sign_document(keyring, invariants, "key.governance_forum_a", "invariants", "2026-01-20T14:14:00Z")

    write_json(os.path.join(out_dir, "inputs", "assessment.json"), assessment)
    write_json(os.path.join(out_dir, "inputs", "control_derivation_catalog.json"), catalog)
    write_json(os.path.join(out_dir, "inputs", "cstar_profile.json"), cstar)
    write_json(os.path.join(out_dir, "inputs", "invariant_register.json"), invariants)
    write_json(os.path.join(out_dir, "inputs", "threshold_contracts.json"),
               {"contracts": c.THRESHOLD_CONTRACTS})
    write_json(os.path.join(out_dir, "inputs", "policy_metadata.json"), c.POLICY_METADATA)
    write_json(os.path.join(out_dir, "judgment", "judgment_record.json"), judgment)
    write_json(os.path.join(out_dir, "dispositions", "dispositions.json"), dispositions)
    write_json(os.path.join(out_dir, "acs", "approved_control_specifications.json"), acs_set)
    write_json(
        os.path.join(out_dir, "inputs", "compile_parameters.json"),
        {
            "compile_time": d.COMPILE_TIME,
            "bundle_effective_from": d.EFFECTIVE_FROM,
            "declared_heatmap_threshold": 15,
            "signing_authorities": {
                "assessment": "key.assessor",
                "catalog": "key.governance_forum_a",
                "cstar_profile": "key.governance_forum_a",
                "judgment_record": "key.governance_forum_a",
                "dispositions": "key.governance_forum_a",
                "acs": "key.governance_forum_a",
                "invariants": "key.governance_forum_a",
            },
            "bundle_signing_key": "key.governance_forum_a",
            "lifecycle_authority_key": "key.lifecycle_authority_a",
            "runtime_authority_key": "key.runtime_authority_a",
        },
    )
    return assessment


def build_case_b(keyring, out_dir):
    d = case_b_data
    c = case_b_control

    assessment = {
        "assessment_id": "ASSESSMENT-CASE-B",
        "case_class": "forensic_reconstruction",
        "metadata": d.METADATA,
        "system_profile": d.SYSTEM_PROFILE,
        "obligations": d.OBLIGATIONS,
        "risk_register": d.build_risk_register(),
        "risk_analysis": d.build_risk_analysis(),
    }
    sign_document(keyring, assessment, "key.assessor", "assessment", "2026-01-22T09:00:00Z")

    catalog = dict(c.CATALOG)
    sign_document(keyring, catalog, "key.governance_forum_b", "catalog", "2026-01-22T15:05:00Z")

    cstar = dict(c.CSTAR_PROFILE)
    sign_document(keyring, cstar, "key.governance_forum_b", "cstar_profile", "2026-01-22T15:06:00Z")

    acs_records = c.build_acs_records()
    acs_set = {
        "acs_set_id": "D-CASE-B",
        "version_binding_ref": d.BINDING,
        "records": acs_records,
    }
    sign_document(keyring, acs_set, "key.governance_forum_b", "acs", "2026-01-22T15:10:00Z")

    judgment = c.build_judgment_record(acs_records)
    sign_document(keyring, judgment, "key.governance_forum_b", "judgment_record", "2026-01-22T15:08:00Z")

    dispositions = {
        "disposition_set_id": "DELTA-CASE-B",
        "version_binding_ref": d.BINDING,
        "records": c.build_dispositions(),
    }
    sign_document(keyring, dispositions, "key.governance_forum_b", "dispositions", "2026-01-22T15:12:00Z")

    invariants = build_invariant_register(
        register_id="INV-CASE-B",
        binding=d.BINDING,
        approver=d.FORUM,
        approval_time=d.APPROVAL_TIME,
        effective_from=d.EFFECTIVE_FROM,
        action_tuple=d.RELEASE,
        parameter_schema_ref="PS-RELEASE-PAYMENT",
        action_parameters=c.RELEASE_PARAMS,
        fingerprint=d.METADATA["version_binding"]["fingerprint"],
    )
    sign_document(keyring, invariants, "key.governance_forum_b", "invariants", "2026-01-22T15:14:00Z")

    write_json(os.path.join(out_dir, "inputs", "assessment.json"), assessment)
    write_json(os.path.join(out_dir, "inputs", "control_derivation_catalog.json"), catalog)
    write_json(os.path.join(out_dir, "inputs", "cstar_profile.json"), cstar)
    write_json(os.path.join(out_dir, "inputs", "invariant_register.json"), invariants)
    write_json(os.path.join(out_dir, "inputs", "threshold_contracts.json"),
               {"contracts": c.THRESHOLD_CONTRACTS})
    write_json(os.path.join(out_dir, "inputs", "policy_metadata.json"), c.POLICY_METADATA)
    write_json(os.path.join(out_dir, "judgment", "judgment_record.json"), judgment)
    write_json(os.path.join(out_dir, "dispositions", "dispositions.json"), dispositions)
    write_json(os.path.join(out_dir, "acs", "approved_control_specifications.json"), acs_set)
    write_json(
        os.path.join(out_dir, "inputs", "compile_parameters.json"),
        {
            "compile_time": d.COMPILE_TIME,
            "bundle_effective_from": d.EFFECTIVE_FROM,
            "declared_heatmap_threshold": 15,
            "signing_authorities": {
                "assessment": "key.assessor",
                "catalog": "key.governance_forum_b",
                "cstar_profile": "key.governance_forum_b",
                "judgment_record": "key.governance_forum_b",
                "dispositions": "key.governance_forum_b",
                "acs": "key.governance_forum_b",
                "invariants": "key.governance_forum_b",
            },
            "bundle_signing_key": "key.governance_forum_b",
            "lifecycle_authority_key": "key.lifecycle_authority_b",
            "runtime_authority_key": "key.runtime_authority_b",
        },
    )
    return assessment


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT)
    args = parser.parse_args(argv)

    keys_dir = os.path.join(args.repo_root, "keys")
    keyring = KeyRing.generate(KEY_IDS, seed_material=KEY_SEED)
    keyring.write(keys_dir)

    build_case_a(keyring, os.path.join(args.repo_root, "cases", "case_a"))
    build_case_b(keyring, os.path.join(args.repo_root, "cases", "case_b"))

    # The catalog is also published at the repository root path named in the
    # target structure, so a reviewer can find it without opening a case tree.
    for case, name in (("case_a", "control_derivation_catalog_v1.json"),
                       ("case_b", "control_derivation_catalog_b_v1.json")):
        src = os.path.join(args.repo_root, "cases", case, "inputs",
                           "control_derivation_catalog.json")
        dst = os.path.join(args.repo_root, "catalog", name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, encoding="utf-8") as fh:
            blob = fh.read()
        with open(dst, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(blob)

    for case, name in (("case_a", "invariant_register_v1.json"),
                       ("case_b", "invariant_register_b_v1.json")):
        src = os.path.join(args.repo_root, "cases", case, "inputs",
                           "invariant_register.json")
        dst = os.path.join(args.repo_root, "invariants", name)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(src, encoding="utf-8") as fh:
            blob = fh.read()
        with open(dst, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(blob)

    print("case artifacts regenerated under cases/, catalog/ and invariants/")
    print("research signing keys written to keys/ (TEST ONLY / NOT FOR PRODUCTION)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
