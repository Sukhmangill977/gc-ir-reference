"""Regenerate the Case D artifact trees under ``cases/case_d_ccs0/``,
``cases/case_d_ccs1/`` and ``cases/case_d_ccs2/`` (Paper 2 v1.2, spec
section 4, D1-D10).

    python -m tools.build_case_d

Three case trees, not one multi-judgment tree: ``gcir.caseio.load_case``
loads one case_id directory as one self-contained set of documents, and
inventing a second loading mechanism to hold three judgment/ACS variants in
a single tree would be new, untested machinery for no benefit over reusing
the existing, already-relied-upon per-case-id convention three times. All
three share byte-identical assessment/catalog/cstar_profile/invariant_register
content (same governance corpus; see ``tools/case_d_data.py`` and
``tools/case_d_control.py``); only ACS, dispositions and judgment differ,
exactly as CCS0/CCS1/CCS2 are specified to.

Reuses the existing Case A/B/C/B-v1.1 signing keys (``tools/build_cases.KEY_SEED``).
Run ``python -m tools.build_cases`` first (or at least once) so ``keys/`` exists.
"""

from __future__ import annotations

import argparse
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from gcir.signatures import KeyRing  # noqa: E402

from tools import case_d_control as c  # noqa: E402
from tools import case_d_data as d  # noqa: E402
from tools.build_cases import KEY_IDS, KEY_SEED, sign_document, write_json  # noqa: E402
from tools.invariants_data import build_invariant_register  # noqa: E402

_SIGNING_TIMES = {
    "assessment": "2026-03-02T09:00:00Z",
    "catalog": "2026-03-02T15:05:00Z",
    "cstar_profile": "2026-03-02T15:06:00Z",
    "invariants": "2026-03-02T15:14:00Z",
}


def _shared_documents(keyring):
    """The byte-identical corpus every CCS variant shares."""
    assessment = {
        "assessment_id": "ASSESSMENT-CASE-D",
        "case_class": "synthetic",
        "metadata": d.METADATA,
        "system_profile": d.SYSTEM_PROFILE,
        "obligations": d.OBLIGATIONS,
        "risk_register": d.build_risk_register(),
        "risk_analysis": d.build_risk_analysis(),
    }
    sign_document(keyring, assessment, "key.assessor", "assessment", _SIGNING_TIMES["assessment"])

    catalog = dict(c.CATALOG)
    sign_document(keyring, catalog, "key.governance_forum_b", "catalog", _SIGNING_TIMES["catalog"])

    cstar = dict(c.CSTAR_PROFILE)
    sign_document(keyring, cstar, "key.governance_forum_b", "cstar_profile", _SIGNING_TIMES["cstar_profile"])

    invariants = build_invariant_register(
        register_id="INV-CASE-D",
        binding=d.BINDING,
        approver=d.FORUM,
        approval_time=d.APPROVAL_TIME,
        effective_from=d.EFFECTIVE_FROM,
        action_tuple=d.RELEASE,
        parameter_schema_ref="PS-RELEASE-FUNDS",
        action_parameters=c.RELEASE_PARAMS,
        fingerprint=d.METADATA["version_binding"]["fingerprint"],
        include_enforcement_phases=True,
    )
    sign_document(keyring, invariants, "key.governance_forum_b", "invariants", _SIGNING_TIMES["invariants"])

    return assessment, catalog, cstar, invariants


def _compile_parameters(acs_records):
    return {
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
    }


def _write_variant(keyring, out_dir, assessment, catalog, cstar, invariants,
                    acs_records, dispositions_records, judgment, acs_set_id):
    acs_set = {"acs_set_id": acs_set_id, "version_binding_ref": d.BINDING, "records": acs_records}
    sign_document(keyring, acs_set, "key.governance_forum_b", "acs", "2026-03-02T15:10:00Z")

    dispositions = {
        "disposition_set_id": "DELTA-" + acs_set_id.replace("D-CASE-D-", "CASE-D-"),
        "version_binding_ref": d.BINDING, "records": dispositions_records,
    }
    sign_document(keyring, dispositions, "key.governance_forum_b", "dispositions", "2026-03-02T15:12:00Z")

    sign_document(keyring, judgment, "key.governance_forum_b", "judgment_record", "2026-03-02T15:08:00Z")

    write_json(os.path.join(out_dir, "inputs", "assessment.json"), assessment)
    write_json(os.path.join(out_dir, "inputs", "control_derivation_catalog.json"), catalog)
    write_json(os.path.join(out_dir, "inputs", "cstar_profile.json"), cstar)
    write_json(os.path.join(out_dir, "inputs", "invariant_register.json"), invariants)
    write_json(os.path.join(out_dir, "inputs", "threshold_contracts.json"), {"contracts": c.THRESHOLD_CONTRACTS})
    write_json(os.path.join(out_dir, "inputs", "policy_metadata.json"), c.POLICY_METADATA)
    write_json(os.path.join(out_dir, "judgment", "judgment_record.json"), judgment)
    write_json(os.path.join(out_dir, "dispositions", "dispositions.json"), dispositions)
    write_json(os.path.join(out_dir, "acs", "approved_control_specifications.json"), acs_set)
    write_json(os.path.join(out_dir, "inputs", "compile_parameters.json"), _compile_parameters(acs_records))


def build_case_d(keyring, cases_root):
    assessment, catalog, cstar, invariants = _shared_documents(keyring)

    # CCS0: emergency exception disabled -- ordinary ACS only (D2/D3).
    ccs0_acs = [c.acs_d01_01()]
    _write_variant(
        keyring, os.path.join(cases_root, "case_d_ccs0"),
        assessment, catalog, cstar, invariants,
        ccs0_acs, c.build_dispositions_ccs0(), c.build_judgment_ccs0(ccs0_acs),
        "D-CASE-D-CCS0",
    )

    # CCS1: emergency exception enabled, confined, resolved to the Treasury
    # Officer credential (D5/D6).
    ccs1_acs = [c.acs_d01_01(), c.acs_d02_01(authorized_actor=["treasury.officer_on_duty"])]
    _write_variant(
        keyring, os.path.join(cases_root, "case_d_ccs1"),
        assessment, catalog, cstar, invariants,
        ccs1_acs, c.build_dispositions_active(), c.build_judgment_ccs1(ccs1_acs),
        "D-CASE-D-CCS1",
    )

    # CCS2: policy 4.3 / J' widens the authorized actor set (D9).
    ccs2_acs = [
        c.acs_d01_01(),
        c.acs_d02_01(
            authorized_actor=["treasury.officer_on_duty", "payments.analyst_eta2_tier"],
            policy_id="POL-D-EMERGENCY-EXCEPTION-4.3",
        ),
    ]
    _write_variant(
        keyring, os.path.join(cases_root, "case_d_ccs2"),
        assessment, catalog, cstar, invariants,
        ccs2_acs, c.build_dispositions_active(), c.build_judgment_ccs2(ccs2_acs),
        "D-CASE-D-CCS2",
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=REPO_ROOT)
    args = parser.parse_args(argv)

    keys_dir = os.path.join(args.repo_root, "keys")
    keyring = KeyRing.generate(KEY_IDS, seed_material=KEY_SEED)
    keyring.write(keys_dir)

    build_case_d(keyring, os.path.join(args.repo_root, "cases"))
    print("Case D artifacts (CCS0/CCS1/CCS2) regenerated under cases/case_d_ccs*/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
