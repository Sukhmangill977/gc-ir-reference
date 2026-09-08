"""Temporal traceability projection into SQLite, and the six audit queries.

Manuscript Section VIII.  The authorized-origin chain is:

    (obligation or internal requirement)
      -> risk/disposition
      -> ACS or compiler invariant
      -> predicate
      -> receipt

"Coverage gaps become mechanical queries."  This module builds the relational
projection those queries run against, so that the queries themselves are ordinary
SQL a reviewer can read in ``queries/traceability.sql``.

Signature validity and ``ValidAt`` are not expressible in SQL, so the projection
carries them as pre-computed columns whose derivation is in ``gcir.lifecycle``
and ``gcir.signatures``.  The columns are named ``*_verified`` so it is obvious
in the SQL where the cryptographic check happened.
"""

from __future__ import annotations

import os
import sqlite3

from .canonicalization import hash_payload
from .lifecycle import LifecycleRegistry, valid_at
from .temporal import commit_before_actuate, parse_time

SCHEMA = """
CREATE TABLE obligation (
    obligation_id      TEXT PRIMARY KEY,
    requirement_class  TEXT NOT NULL,
    source             TEXT NOT NULL,
    clause_ref         TEXT NOT NULL,
    effective_from     TEXT NOT NULL
);

CREATE TABLE internal_requirement (
    invariant_id       TEXT PRIMARY KEY,
    title              TEXT NOT NULL,
    authorizing_source TEXT NOT NULL,
    reference          TEXT NOT NULL
);

CREATE TABLE risk (
    risk_id            TEXT PRIMARY KEY,
    consequence_class  TEXT NOT NULL,
    c_star             INTEGER NOT NULL,
    likelihood_residual INTEGER NOT NULL,
    impact_residual    INTEGER NOT NULL
);

CREATE TABLE risk_obligation (
    risk_id            TEXT NOT NULL REFERENCES risk(risk_id),
    obligation_id      TEXT NOT NULL,
    PRIMARY KEY (risk_id, obligation_id)
);

CREATE TABLE disposition (
    risk_id            TEXT NOT NULL REFERENCES risk(risk_id),
    status             TEXT NOT NULL,
    reason_code        TEXT,
    PRIMARY KEY (risk_id, status)
);

CREATE TABLE acs (
    acs_id             TEXT PRIMARY KEY,
    risk_id            TEXT NOT NULL,
    approver           TEXT NOT NULL,
    approval_time      TEXT NOT NULL
);

CREATE TABLE predicate (
    gcir_id            TEXT PRIMARY KEY,
    acs_id             TEXT,
    origin_type        TEXT NOT NULL,
    origin_id          TEXT NOT NULL,
    risk_id            TEXT,
    internal_requirement_id TEXT,
    gate_type          TEXT NOT NULL,
    gate_source        TEXT NOT NULL,
    mandatory_role     TEXT NOT NULL,
    effective_from     TEXT NOT NULL
);

CREATE TABLE predicate_obligation (
    gcir_id            TEXT NOT NULL REFERENCES predicate(gcir_id),
    obligation_id      TEXT NOT NULL,
    PRIMARY KEY (gcir_id, obligation_id)
);

CREATE TABLE bundle (
    bundle_hash        TEXT PRIMARY KEY,
    bundle_id          TEXT NOT NULL,
    effective_from     TEXT NOT NULL,
    payload_hash_recomputed TEXT NOT NULL
);

CREATE TABLE lifecycle_entry (
    entry_id           TEXT PRIMARY KEY,
    bundle_hash        TEXT NOT NULL,
    action             TEXT NOT NULL,
    effective_time     TEXT NOT NULL,
    authority          TEXT NOT NULL,
    signing_key_id     TEXT,
    signature_verified INTEGER NOT NULL,
    authority_valid    INTEGER NOT NULL
);

CREATE TABLE receipt (
    receipt_id         TEXT PRIMARY KEY,
    bundle_hash        TEXT NOT NULL,
    decision           TEXT NOT NULL,
    decision_time      TEXT NOT NULL,
    authorization_time TEXT NOT NULL,
    evidence_commit_time TEXT NOT NULL,
    actuation_time     TEXT,
    signature_verified INTEGER NOT NULL,
    valid_at_decision  INTEGER NOT NULL,
    valid_at_reasons   TEXT NOT NULL
);

CREATE TABLE receipt_predicate (
    receipt_id         TEXT NOT NULL REFERENCES receipt(receipt_id),
    gcir_id            TEXT NOT NULL,
    acs_id             TEXT,
    origin_type        TEXT,
    origin_id          TEXT,
    outcome            TEXT NOT NULL,
    PRIMARY KEY (receipt_id, gcir_id)
);

CREATE TABLE actuation (
    actuation_id       TEXT PRIMARY KEY,
    receipt_id         TEXT,
    actuation_time     TEXT NOT NULL,
    action_tuple       TEXT NOT NULL
);
"""


def build_projection(connection, assessment, bundle, invariants, registry,
                     receipts, actuations, keyring, cstar_flags):
    """Populate the relational projection from the compiled artifacts."""
    connection.executescript(SCHEMA)

    for obligation in assessment.obligations:
        connection.execute(
            "INSERT INTO obligation VALUES (?,?,?,?,?)",
            (
                obligation["obligation_id"],
                obligation["requirement_class"],
                obligation["source"],
                obligation["clause_ref"],
                obligation["effective_from"],
            ),
        )

    for invariant in invariants:
        connection.execute(
            "INSERT INTO internal_requirement VALUES (?,?,?,?)",
            (
                invariant["invariant_id"],
                invariant["title"],
                invariant["authorizing_requirement"]["source"],
                invariant["authorizing_requirement"]["reference"],
            ),
        )

    analysis = assessment.analysis_index
    for risk in assessment.risk_register:
        row = analysis[risk["risk_id"]]
        connection.execute(
            "INSERT INTO risk VALUES (?,?,?,?,?)",
            (
                risk["risk_id"],
                row["consequence_class"],
                cstar_flags.get(risk["risk_id"], 0),
                row["likelihood_residual"],
                row["impact_residual"],
            ),
        )
        for obligation_id in risk.get("obligation_refs", []):
            connection.execute(
                "INSERT INTO risk_obligation VALUES (?,?)",
                (risk["risk_id"], obligation_id),
            )

    status_of = {
        "RuntimeDisposition": "runtime",
        "NonRuntimeDisposition": "nonruntime",
        "AcceptedRiskDisposition": "accepted",
        "UnresolvedDisposition": "unresolved",
    }
    for record in bundle.dispositions:
        connection.execute(
            "INSERT INTO disposition VALUES (?,?,?)",
            (
                record["risk_id"],
                status_of[record["record_type"]],
                record.get("reason_code"),
            ),
        )

    for predicate in bundle.predicates:
        connection.execute(
            "INSERT INTO predicate VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                predicate["gcir_id"],
                predicate.get("acs_id"),
                predicate["origin"]["origin_type"],
                predicate["origin"]["origin_id"],
                predicate["requirement_ref"].get("risk_id"),
                predicate["requirement_ref"].get("internal_requirement_id"),
                predicate["gate_type"],
                predicate["gate_source"],
                predicate["mandatory_role"],
                predicate["validity"]["effective_from"],
            ),
        )
        for obligation_id in predicate["requirement_ref"].get("obligation_ids", []):
            connection.execute(
                "INSERT INTO predicate_obligation VALUES (?,?)",
                (predicate["gcir_id"], obligation_id),
            )

    seen_acs = set()
    for record in bundle.dispositions:
        if record["record_type"] != "RuntimeDisposition":
            continue
        for acs_id in record["acs_ids"]:
            seen_acs.add((acs_id, record["risk_id"]))

    for acs_id, risk_id in sorted(seen_acs):
        connection.execute(
            "INSERT INTO acs VALUES (?,?,?,?)",
            (acs_id, risk_id, "recorded_in_judgment_record", "recorded_in_judgment_record"),
        )

    recomputed = hash_payload(bundle.payload)
    connection.execute(
        "INSERT INTO bundle VALUES (?,?,?,?)",
        (
            bundle.payload_hash,
            bundle.payload["bundle_id"],
            bundle.payload["validity"]["effective_from"],
            recomputed,
        ),
    )

    authorized_keys = set(registry.document.get("authorized_signing_keys", []))
    for entry in registry.entries:
        key_id = (entry.get("signature") or {}).get("key_id")
        verified = registry.entry_signature_valid(entry)
        connection.execute(
            "INSERT INTO lifecycle_entry VALUES (?,?,?,?,?,?,?,?)",
            (
                entry["entry_id"],
                entry["bundle_hash"],
                entry["action"],
                entry["effective_time"],
                entry["authority"],
                key_id,
                1 if verified else 0,
                1 if (key_id in authorized_keys and verified) else 0,
            ),
        )

    for receipt in receipts:
        ok, reasons = valid_at(receipt, bundle, registry, keyring=keyring)
        signature_verified = not any("signature" in r for r in reasons)
        connection.execute(
            "INSERT INTO receipt VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                receipt["receipt_id"],
                receipt["bundle_hash"],
                receipt["decision"],
                receipt["decision_time"],
                receipt["authorization_time"],
                receipt["evidence_commit_time"],
                receipt.get("actuation_time"),
                1 if signature_verified else 0,
                1 if ok else 0,
                "; ".join(reasons),
            ),
        )
        for entry in receipt["evaluated_predicates"]:
            connection.execute(
                "INSERT INTO receipt_predicate VALUES (?,?,?,?,?,?)",
                (
                    receipt["receipt_id"],
                    entry["gcir_id"],
                    entry.get("acs_id"),
                    (entry.get("origin") or {}).get("origin_type"),
                    (entry.get("origin") or {}).get("origin_id"),
                    entry["outcome"],
                ),
            )

    for record in actuations:
        connection.execute(
            "INSERT INTO actuation VALUES (?,?,?,?)",
            (
                record["actuation_id"],
                record.get("receipt_id"),
                record["actuation_time"],
                record["action_tuple"],
            ),
        )

    connection.commit()
    return connection


def open_projection(path=":memory:"):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


# ---------------------------------------------------------------------------
# The six audit queries (Section VIII)
# ---------------------------------------------------------------------------

QUERIES = {}


def _q(qid, title, detects, sql):
    QUERIES[qid] = {"id": qid, "title": title, "detects": detects, "sql": sql.strip()}


_q(
    "Q1",
    "Obligations without an approved disposition",
    "an obligation that no risk disposes, or whose risks are unresolved",
    """
SELECT o.obligation_id, o.requirement_class
FROM obligation o
WHERE NOT EXISTS (
    SELECT 1
    FROM risk_obligation ro
    JOIN disposition d ON d.risk_id = ro.risk_id
    WHERE ro.obligation_id = o.obligation_id
      AND d.status IN ('runtime', 'nonruntime', 'accepted')
)
ORDER BY o.obligation_id
""",
)

_q(
    "Q2",
    "Risks without exactly one disposition",
    "a risk with zero dispositions, or with more than one",
    """
SELECT r.risk_id, COUNT(d.status) AS disposition_count
FROM risk r
LEFT JOIN disposition d ON d.risk_id = r.risk_id
GROUP BY r.risk_id
HAVING COUNT(d.status) != 1
ORDER BY r.risk_id
""",
)

_q(
    "Q3",
    "Predicates without a risk or compiler-invariant origin",
    "an orphan predicate: origin(p) not in R union INV",
    """
SELECT p.gcir_id, p.origin_type, p.origin_id
FROM predicate p
WHERE NOT (
        (p.origin_type = 'risk_derived'
         AND p.origin_id IN (SELECT risk_id FROM risk)
         AND p.acs_id IS NOT NULL
         AND p.acs_id IN (SELECT acs_id FROM acs))
     OR (p.origin_type = 'compiler_invariant'
         AND p.origin_id IN (SELECT invariant_id FROM internal_requirement))
)
ORDER BY p.gcir_id
""",
)

_q(
    "Q4",
    "Receipts whose bundle was not valid at decision time",
    "a receipt whose payload hash does not bind, whose bundle was not yet "
    "effective, or whose bundle the registry had already retired at decision time",
    """
SELECT t.receipt_id, t.bundle_hash, t.decision_time, t.valid_at_reasons
FROM receipt t
WHERE t.valid_at_decision = 0
ORDER BY t.receipt_id
""",
)

_q(
    "Q5",
    "Actuation without a temporally prior committed receipt",
    "an actuation with no receipt, or whose receipt violates "
    "authorization_time <= evidence_commit_time < actuation_time",
    """
SELECT a.actuation_id, a.receipt_id, a.actuation_time
FROM actuation a
LEFT JOIN receipt t ON t.receipt_id = a.receipt_id
WHERE t.receipt_id IS NULL
   OR t.authorization_time > t.evidence_commit_time
   OR t.evidence_commit_time >= a.actuation_time
ORDER BY a.actuation_id
""",
)

_q(
    "Q6",
    "Lifecycle-registry records lacking a valid signing authority",
    "a registry record signed by a key outside authorized_signing_keys, or whose "
    "signature does not verify",
    """
SELECT l.entry_id, l.bundle_hash, l.action, l.authority, l.signing_key_id
FROM lifecycle_entry l
WHERE l.authority_valid = 0
ORDER BY l.entry_id
""",
)


def run_query(connection, query_id):
    query = QUERIES[query_id]
    rows = [dict(row) for row in connection.execute(query["sql"])]
    return {
        "query_id": query_id,
        "title": query["title"],
        "detects": query["detects"],
        "row_count": len(rows),
        "rows": rows,
        "empty": len(rows) == 0,
    }


def run_all(connection):
    return {qid: run_query(connection, qid) for qid in sorted(QUERIES)}


def write_sql_file(path):
    """Emit ``queries/traceability.sql`` from the single source of truth above."""
    parts = [
        "-- Temporal traceability audit queries (manuscript Section VIII).",
        "-- Generated from src/gcir/traceability.py; do not edit by hand.",
        "--",
        "-- Empty result sets demonstrate linkage and temporal-integrity completeness",
        "-- UNDER THE DECLARED DATA MODEL.  They do not, by themselves, establish legal",
        "-- compliance, semantic correctness, or control effectiveness.",
        "",
    ]
    for qid in sorted(QUERIES):
        query = QUERIES[qid]
        parts.append("-- =====================================================================")
        parts.append("-- %s. %s" % (qid, query["title"]))
        parts.append("-- Detects: %s" % query["detects"])
        parts.append("-- =====================================================================")
        parts.append(query["sql"] + ";")
        parts.append("")
    text = "\n".join(parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    return path
