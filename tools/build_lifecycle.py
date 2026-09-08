"""Generate the committed lifecycle, receipt and actuation fixtures.

These fixtures cite the compiled bundle's payload hash, so they are generated
after a compilation.  The hash is deterministic, so re-running this script on a
fresh clone reproduces the tree byte-for-byte.

    python -m tools.build_lifecycle

Two fixture families are written per case:

``lifecycle/`` -- the clean, release-admissible fixtures.  Every one of the six
audit queries returns an empty set over these.

``lifecycle/negative/`` -- one deliberately corrupted fixture per query, so the
experiment can demonstrate that each query *detects* the violation it exists to
detect.  A query that never fires proves nothing.
"""

from __future__ import annotations

import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from gcir.caseio import load_case  # noqa: E402
from gcir.compiler import compile_bundle  # noqa: E402

from tools.build_cases import write_json  # noqa: E402

# Instants used by the fixtures.  All are declared governance inputs, never
# clock readings; none of them enters a hashed bundle payload.
DECISION_TIME = "2026-03-04T10:15:00Z"
AUTHORIZATION_TIME = "2026-03-04T10:15:00Z"
COMMIT_TIME = "2026-03-04T10:15:01Z"
ACTUATION_TIME = "2026-03-04T10:15:02Z"

RETIREMENT_TIME = "2026-06-01T00:00:00Z"
POST_RETIREMENT_DECISION = "2026-07-01T09:00:00Z"

CASE_SETUP = {
    "case_a": {
        "registry_id": "REG-CASE-A",
        "lifecycle_key": "key.lifecycle_authority_a",
        "runtime_key": "key.runtime_authority_a",
        "authority": "exec.head_of_research",
        "action_tuple": "research_agent/publish_report/research_report/internal_distribution",
        "successor_hash": "f" * 64,
    },
    "case_b": {
        "registry_id": "REG-CASE-B",
        "lifecycle_key": "key.lifecycle_authority_b",
        "runtime_key": "key.runtime_authority_b",
        "authority": "exec.head_of_payments",
        "action_tuple": "transaction_agent/release_payment/payment_instruction/payment_rail",
        "successor_hash": "e" * 64,
    },
}


def _receipt(receipt_id, bundle, decision_time, authorization_time, commit_time,
             actuation_time, action_tuple):
    return {
        "receipt_id": receipt_id,
        "bundle_hash": bundle.payload_hash,
        "decision": "PERMIT",
        "decision_time": decision_time,
        "authorization_time": authorization_time,
        "evidence_commit_time": commit_time,
        "actuation_time": actuation_time,
        "action_tuple": dict(
            zip(("subject", "action", "resource", "destination"), action_tuple.split("/"))
        ),
        "evaluated_predicates": [
            {
                "gcir_id": predicate["gcir_id"],
                "acs_id": predicate.get("acs_id"),
                "origin": {
                    "origin_type": predicate["origin"]["origin_type"],
                    "origin_id": predicate["origin"]["origin_id"],
                },
                "outcome": "pass",
            }
            for predicate in bundle.predicates
        ],
    }


def build_for_case(case_id, out_root):
    setup = CASE_SETUP[case_id]
    case = load_case(case_id)
    keyring = case.keyring
    result = compile_bundle(case.compiler_inputs())
    bundle = result.bundle

    # ---- clean lifecycle registry ----------------------------------------
    retirement = {
        "entry_id": "REG-%s-001" % case_id.upper().replace("_", "-"),
        "bundle_hash": bundle.payload_hash,
        "action": "retire",
        "effective_time": RETIREMENT_TIME,
        "authority": setup["authority"],
        "reason": "Scheduled retirement on the annual review cycle. Recorded as a "
                  "signed registry record; the bundle payload is not touched.",
        "trigger": "model_version_change",
    }
    retirement["signature"] = keyring.sign(
        {k: v for k, v in retirement.items() if k != "signature"},
        setup["lifecycle_key"],
        domain="lifecycle",
        signing_time="2026-05-25T12:00:00Z",
    )
    registry = {
        "registry_id": setup["registry_id"],
        "authorized_signing_keys": [setup["lifecycle_key"]],
        "entries": [retirement],
    }

    # A registry with no entries at all, for the "bundle currently in force"
    # scenarios.
    empty_registry = {
        "registry_id": setup["registry_id"] + "-EMPTY",
        "authorized_signing_keys": [setup["lifecycle_key"]],
        "entries": [],
    }

    # ---- clean receipts ---------------------------------------------------
    receipt = _receipt(
        "RCPT-%s-001" % case_id.upper().replace("_", "-"),
        bundle, DECISION_TIME, AUTHORIZATION_TIME, COMMIT_TIME, ACTUATION_TIME,
        setup["action_tuple"],
    )
    receipt["signature"] = keyring.sign(
        {k: v for k, v in receipt.items() if k != "signature"},
        setup["runtime_key"], domain="receipt", signing_time=COMMIT_TIME,
    )

    # A historical receipt taken BEFORE retirement.  Section VIII: a historical
    # receipt is not drift merely because its bundle is now retired.
    historical = _receipt(
        "RCPT-%s-002" % case_id.upper().replace("_", "-"),
        bundle, "2026-05-30T08:00:00Z", "2026-05-30T08:00:00Z",
        "2026-05-30T08:00:01Z", "2026-05-30T08:00:02Z", setup["action_tuple"],
    )
    historical["signature"] = keyring.sign(
        {k: v for k, v in historical.items() if k != "signature"},
        setup["runtime_key"], domain="receipt", signing_time="2026-05-30T08:00:01Z",
    )

    actuations = [
        {
            "actuation_id": "ACT-%s-001" % case_id.upper().replace("_", "-"),
            "receipt_id": receipt["receipt_id"],
            "actuation_time": ACTUATION_TIME,
            "action_tuple": setup["action_tuple"],
        },
        {
            "actuation_id": "ACT-%s-002" % case_id.upper().replace("_", "-"),
            "receipt_id": historical["receipt_id"],
            "actuation_time": "2026-05-30T08:00:02Z",
            "action_tuple": setup["action_tuple"],
        },
    ]

    lifecycle_dir = os.path.join(out_root, case_id, "lifecycle")
    write_json(os.path.join(lifecycle_dir, "lifecycle_registry.json"), registry)
    write_json(os.path.join(lifecycle_dir, "lifecycle_registry_empty.json"), empty_registry)
    write_json(os.path.join(lifecycle_dir, "receipts.json"),
               {"receipts": [receipt, historical]})
    write_json(os.path.join(lifecycle_dir, "actuations.json"),
               {"actuations": actuations})

    # ---- negative fixtures, one per audit query --------------------------
    negatives = {}

    # Q4-a: a receipt taken AFTER the registry-effective retirement.
    post = _receipt(
        "RCPT-%s-NEG-Q4A" % case_id.upper().replace("_", "-"),
        bundle, POST_RETIREMENT_DECISION, POST_RETIREMENT_DECISION,
        "2026-07-01T09:00:01Z", "2026-07-01T09:00:02Z", setup["action_tuple"],
    )
    post["signature"] = keyring.sign(
        {k: v for k, v in post.items() if k != "signature"},
        setup["runtime_key"], domain="receipt", signing_time="2026-07-01T09:00:01Z",
    )
    negatives["q4_post_retirement_receipt"] = post

    # Q4-b: a receipt citing a bundle hash that does not bind to the payload.
    wrong = _receipt(
        "RCPT-%s-NEG-Q4B" % case_id.upper().replace("_", "-"),
        bundle, DECISION_TIME, AUTHORIZATION_TIME, COMMIT_TIME, ACTUATION_TIME,
        setup["action_tuple"],
    )
    wrong["bundle_hash"] = "0" * 64
    wrong["signature"] = keyring.sign(
        {k: v for k, v in wrong.items() if k != "signature"},
        setup["runtime_key"], domain="receipt", signing_time=COMMIT_TIME,
    )
    negatives["q4_wrong_bundle_hash_receipt"] = wrong

    # Q5-a: an actuation with no receipt at all.
    negatives["q5_orphan_actuation"] = {
        "actuation_id": "ACT-%s-NEG-Q5A" % case_id.upper().replace("_", "-"),
        "receipt_id": None,
        "actuation_time": ACTUATION_TIME,
        "action_tuple": setup["action_tuple"],
    }

    # Q5-b: a receipt committed AFTER actuation (ordering violation).
    late = _receipt(
        "RCPT-%s-NEG-Q5B" % case_id.upper().replace("_", "-"),
        bundle, DECISION_TIME, AUTHORIZATION_TIME,
        "2026-03-04T10:15:05Z", "2026-03-04T10:15:03Z", setup["action_tuple"],
    )
    late["signature"] = keyring.sign(
        {k: v for k, v in late.items() if k != "signature"},
        setup["runtime_key"], domain="receipt", signing_time="2026-03-04T10:15:05Z",
    )
    negatives["q5_late_commit_receipt"] = late
    negatives["q5_late_commit_actuation"] = {
        "actuation_id": "ACT-%s-NEG-Q5B" % case_id.upper().replace("_", "-"),
        "receipt_id": late["receipt_id"],
        "actuation_time": "2026-03-04T10:15:03Z",
        "action_tuple": setup["action_tuple"],
    }

    # Q6: a registry record signed by a key with no lifecycle signing authority.
    rogue = {
        "entry_id": "REG-%s-NEG-Q6" % case_id.upper().replace("_", "-"),
        "bundle_hash": bundle.payload_hash,
        "action": "revoke",
        "effective_time": "2026-03-01T00:00:00Z",
        "authority": "impersonated.head_of_operations",
        "reason": "Purported emergency revocation signed by a key that is not in "
                  "the registry's authorized_signing_keys.",
        "trigger": None,
    }
    rogue["signature"] = keyring.sign(
        {k: v for k, v in rogue.items() if k != "signature"},
        "key.unauthorized_party", domain="lifecycle",
        signing_time="2026-03-01T00:00:00Z",
    )
    negatives["q6_unauthorized_registry_entry"] = rogue

    write_json(os.path.join(lifecycle_dir, "negative", "fixtures.json"), negatives)

    return bundle.payload_hash


def main():
    hashes = {}
    for case_id in sorted(CASE_SETUP):
        hashes[case_id] = build_for_case(case_id, os.path.join(REPO_ROOT, "cases"))
    print("lifecycle, receipt and actuation fixtures written")
    for case_id, digest in sorted(hashes.items()):
        print("  %s bundle payload hash: %s" % (case_id, digest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
