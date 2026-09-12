"""Regenerate the Case B v1.1 artifact tree under ``cases/case_b_v1_1/``.

    python -m tools.build_case_b_v11

Reuses the exact Case A/B signing keys (``tools/build_cases.KEY_SEED``) so the
artifact is reproducible from a fresh clone alongside Case A and Case B.  Run
``python -m tools.build_cases`` first (or at least once) so ``keys/`` exists.
"""

from __future__ import annotations

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from gcir.signatures import KeyRing  # noqa: E402

from tools import case_b_data as d  # noqa: E402
from tools import case_b_v11_control as c  # noqa: E402
from tools.build_cases import KEY_IDS, KEY_SEED, sign_document, write_json  # noqa: E402
from tools.invariants_data import build_invariant_register  # noqa: E402


def build_case_b_v11(keyring, out_dir):
    assessment = {
        "assessment_id": "ASSESSMENT-CASE-B-V1.1",
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
        "acs_set_id": "D-CASE-B-V1.1",
        "version_binding_ref": d.BINDING,
        "records": acs_records,
    }
    sign_document(keyring, acs_set, "key.governance_forum_b", "acs", "2026-01-22T15:10:00Z")

    judgment = c.build_judgment_record(acs_records)
    judgment["judgment_id"] = "J-CASE-B-V1.1"
    sign_document(keyring, judgment, "key.governance_forum_b", "judgment_record", "2026-01-22T15:08:00Z")

    dispositions = {
        "disposition_set_id": "DELTA-CASE-B-V1.1",
        "version_binding_ref": d.BINDING,
        "records": c.build_dispositions(),
    }
    sign_document(keyring, dispositions, "key.governance_forum_b", "dispositions", "2026-01-22T15:12:00Z")

    invariants = build_invariant_register(
        register_id="INV-CASE-B-V1.1",
        binding=d.BINDING,
        approver=d.FORUM,
        approval_time=d.APPROVAL_TIME,
        effective_from=d.EFFECTIVE_FROM,
        action_tuple=d.RELEASE,
        parameter_schema_ref="PS-RELEASE-PAYMENT",
        action_parameters=v10_release_params(),
        fingerprint=d.METADATA["version_binding"]["fingerprint"],
        include_enforcement_phases=True,
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


def v10_release_params():
    from tools import case_b_control as v10
    return v10.RELEASE_PARAMS


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT)
    args = parser.parse_args(argv)

    keys_dir = os.path.join(args.repo_root, "keys")
    keyring = KeyRing.generate(KEY_IDS, seed_material=KEY_SEED)
    keyring.write(keys_dir)

    build_case_b_v11(keyring, os.path.join(args.repo_root, "cases", "case_b_v1_1"))
    print("Case B v1.1 artifacts regenerated under cases/case_b_v1_1/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
