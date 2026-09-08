-- Temporal traceability audit queries (manuscript Section VIII).
-- Generated from src/gcir/traceability.py; do not edit by hand.
--
-- Empty result sets demonstrate linkage and temporal-integrity completeness
-- UNDER THE DECLARED DATA MODEL.  They do not, by themselves, establish legal
-- compliance, semantic correctness, or control effectiveness.

-- =====================================================================
-- Q1. Obligations without an approved disposition
-- Detects: an obligation that no risk disposes, or whose risks are unresolved
-- =====================================================================
SELECT o.obligation_id, o.requirement_class
FROM obligation o
WHERE NOT EXISTS (
    SELECT 1
    FROM risk_obligation ro
    JOIN disposition d ON d.risk_id = ro.risk_id
    WHERE ro.obligation_id = o.obligation_id
      AND d.status IN ('runtime', 'nonruntime', 'accepted')
)
ORDER BY o.obligation_id;

-- =====================================================================
-- Q2. Risks without exactly one disposition
-- Detects: a risk with zero dispositions, or with more than one
-- =====================================================================
SELECT r.risk_id, COUNT(d.status) AS disposition_count
FROM risk r
LEFT JOIN disposition d ON d.risk_id = r.risk_id
GROUP BY r.risk_id
HAVING COUNT(d.status) != 1
ORDER BY r.risk_id;

-- =====================================================================
-- Q3. Predicates without a risk or compiler-invariant origin
-- Detects: an orphan predicate: origin(p) not in R union INV
-- =====================================================================
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
ORDER BY p.gcir_id;

-- =====================================================================
-- Q4. Receipts whose bundle was not valid at decision time
-- Detects: a receipt whose payload hash does not bind, whose bundle was not yet effective, or whose bundle the registry had already retired at decision time
-- =====================================================================
SELECT t.receipt_id, t.bundle_hash, t.decision_time, t.valid_at_reasons
FROM receipt t
WHERE t.valid_at_decision = 0
ORDER BY t.receipt_id;

-- =====================================================================
-- Q5. Actuation without a temporally prior committed receipt
-- Detects: an actuation with no receipt, or whose receipt violates authorization_time <= evidence_commit_time < actuation_time
-- =====================================================================
SELECT a.actuation_id, a.receipt_id, a.actuation_time
FROM actuation a
LEFT JOIN receipt t ON t.receipt_id = a.receipt_id
WHERE t.receipt_id IS NULL
   OR t.authorization_time > t.evidence_commit_time
   OR t.evidence_commit_time >= a.actuation_time
ORDER BY a.actuation_id;

-- =====================================================================
-- Q6. Lifecycle-registry records lacking a valid signing authority
-- Detects: a registry record signed by a key outside authorized_signing_keys, or whose signature does not verify
-- =====================================================================
SELECT l.entry_id, l.bundle_hash, l.action, l.authority, l.signing_key_id
FROM lifecycle_entry l
WHERE l.authority_valid = 0
ORDER BY l.entry_id;
