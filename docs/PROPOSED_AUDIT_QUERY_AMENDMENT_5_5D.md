# PROPOSED_AUDIT_QUERY_AMENDMENT_5_5D.md

**Purpose:** Normative specification of Q7, Q8, Q9, Q10 for inclusion in the 5.5d manuscript (Section VIII).

**Status:** DESIGN PHASE — awaiting author approval before implementation and freeze

---

## COMPLETE Q1-Q10 AUDIT QUERY SPECIFICATION

The following is proposed as the normative set of ten audit queries for Section VIII of the manuscript.

### Overview

An audit query is a Boolean predicate over the compiled bundle (B), the wrapped evidence store (evidence), and the governance inputs (𝒢 = M, S, O, R, A). A clean artifact returns **empty result sets** for all ten queries. Each query targets a distinct completeness criterion.

**Temporal Queries (Q1-Q6):** Traceability and temporal-ordering integrity.  
**Structural Queries (Q7-Q10):** Compilation completeness and reference closure.

---

## TEMPORAL QUERIES

### Q1: Obligations without an approved disposition

**Normative definition:**

For each obligation o ∈ O, verify that there exists at least one risk r ∈ R such that:
1. r references o (i.e., o ∈ r.obligation_refs)
2. r receives a disposition δ where δ.status ∈ {runtime, nonruntime, accepted}

**Violation:** An obligation that no risk disposes, or every disposing risk has disposition = unresolved.

**Objects involved:** obligation, risk_obligation, risk, disposition

**Expected query result on conforming artifact:** Empty (all obligations dispositioned)

**SQL:** See `queries/traceability.sql` line 9-21 (unchanged)

**Negative fixture:** Create obligation O_NEW; omit it from risk_obligation cross-table, or set all disposing risk dispositions to "unresolved"

---

### Q2: Risks without exactly one disposition

**Normative definition:**

For each risk r ∈ R, verify that exactly one disposition record δ exists where δ.risk_id = r.risk_id.

**Violation:** A risk with zero dispositions, or more than one.

**Objects involved:** risk, disposition

**Expected query result on conforming artifact:** Empty (each risk has exactly one disposition)

**SQL:** See `queries/traceability.sql` line 24-32 (unchanged)

**Negative fixture:** Create risk R_NEW without a disposition, or add a second disposition for an existing risk

---

### Q3: Predicates without a risk or compiler-invariant origin

**Normative definition:**

For each predicate p ∈ P, verify that p.origin_type and p.origin_id resolve to either:
- A risk r ∈ R where p.acs_id resolves to an approved ACS in the judgment record J, OR
- An internal invariant inv ∈ INV where p.origin_id = inv.invariant_id

**Violation:** An orphan predicate whose origin does not resolve, or whose ACS is not approved.

**Objects involved:** predicate, risk, acs, internal_requirement, judgment

**Expected query result on conforming artifact:** Empty (all predicates have valid origins)

**SQL:** See `queries/traceability.sql` line 35-48 (unchanged in structure; expanded for Case B with 6 ACS)

**Negative fixture:** Add predicate with origin_id referencing a non-existent risk, or acs_id not in the approved ACS set from judgment

---

### Q4: Receipts whose bundle was not valid at decision time

**Normative definition:**

For each receipt t ∈ evidence.receipts, verify that the bundle B identified by t.bundle_hash satisfies ALL of:
1. t.bundle_hash matches the RFC 8785 canonical hash of B
2. t.decision_time ≥ B.bundle_effective_from
3. No lifecycle registry entry in REG (the signed lifecycle registry) retires B at a time ≤ t.decision_time

**Violation:** Bundle hash mismatch, bundle not yet effective, or bundle superseded/retired before decision.

**Objects involved:** receipt, compiled_bundle, lifecycle_registry

**Expected query result on conforming artifact:** Empty (all receipts reference valid bundles at decision time)

**SQL:** See `queries/traceability.sql` line 51-57 (unchanged)

**Negative fixture:** Create receipt with bundle_hash not in B; or set bundle effective_from > receipt decision_time; or create a lifecycle retire entry before receipt decision_time

---

### Q5: Actuation without a temporally prior committed receipt

**Normative definition:**

For each actuation a ∈ evidence.actuations, verify that:
1. A receipt t exists with t.receipt_id = a.receipt_id
2. t.authorization_time ≤ t.evidence_commit_time (evidence committed after authorization)
3. t.evidence_commit_time < a.actuation_time (evidence committed before actuation)

**Violation:** Missing receipt, or temporal ordering violated (authorization ≤ commit ≤ actuation).

**Objects involved:** actuation, receipt

**Expected query result on conforming artifact:** Empty (all actuations have temporally valid prior receipts)

**SQL:** See `queries/traceability.sql` line 60-69 (unchanged)

**Negative fixture:** Create actuation without a receipt; or set receipt evidence_commit_time ≥ actuation_time; or set authorization_time > evidence_commit_time

---

### Q6: Lifecycle-registry records lacking a valid signing authority

**Normative definition:**

For each entry l ∈ REG (lifecycle registry), verify that:
1. l.authority is present in the list of authorized signing authorities (S.signing_keys or equivalent policy role)
2. l.signature verifies correctly using the key identified by l.signing_key_id

**Violation:** A registry entry signed by a non-authorized key, or whose signature does not cryptographically verify.

**Objects involved:** lifecycle_entry, signing_authority, key (public)

**Expected query result on conforming artifact:** Empty (all registry entries are validly signed)

**SQL:** See `queries/traceability.sql` line 72-78 (unchanged)

**Negative fixture:** Add a lifecycle entry signed by a key not in authorized_signing_keys; or forge a signature that fails verification

---

## STRUCTURAL QUERIES

### Q7: Runtime ACS with zero emitted predicates

**Normative definition:**

For each Approved Control Specification acs ∈ Δ where the disposition of its risk is 'runtime', verify that the compiled bundle B contains at least one predicate p where:
- p.origin_type = 'risk_derived'
- p.acs_id = acs.acs_id

**Violation:** A runtime ACS that compiles to zero predicates (compiler did not emit any risk-derived predicate for it).

**Manuscript reference:** Section V, Contribution C1: "Every runtime ACS may produce zero, one or several predicates." 5.5d requirement: "Every runtime ACS must emit at least one predicate."

**Objects involved:** acs (from judgment), disposition, predicate, compiled_bundle

**Expected query result on conforming artifact:** Empty (all runtime ACS emit at least one predicate)

**SQL:**
```sql
-- Q7. Runtime ACS with zero emitted predicates
SELECT acs.acs_id, acs.risk_id
FROM acs
JOIN disposition d ON d.risk_id = acs.risk_id
WHERE d.status = 'runtime'
  AND NOT EXISTS (
    SELECT 1
    FROM predicate p
    WHERE p.origin_type = 'risk_derived'
      AND p.acs_id = acs.acs_id
  )
ORDER BY acs.acs_id;
```

**Negative fixture:** Create a runtime ACS; do not emit any predicate for it in the compiler output.

**Relationship to Q1-Q6:** Q3 checks that predicates have valid origins. Q7 checks the converse: that approved ACS have predicate products.

---

### Q8: Gate/predicate reference integrity

**Normative definition:**

For each entry in the gate_map of the compiled bundle B, verify that:
1. The referenced predicate(s) exist in B
2. Every risk-derived predicate in B that is referenced by a gate-map entry has a corresponding entry in gate_map

Conversely, for each predicate p ∈ B with mandatory_role = 'decisive' (a gate-candidate), verify that:
- p appears in at least one gate-map decision path, OR
- p is an optional/supporting predicate not required to be gated

**Violation:** Gate references a non-existent predicate; or a decisive predicate is compiled but not included in any gate map.

**Manuscript reference:** Section VII-A, Proposition 1: "The gate set of every risk is reachable through the authority matrix and the C* profile or approved mandatory policy."

**Objects involved:** gate_map, predicate, compiled_bundle

**Expected query result on conforming artifact:** Empty (all gate references resolve; all decisive predicates are gated)

**SQL:**
```sql
-- Q8a. Gate-map references non-existent predicate
SELECT g.gate_id, g.predicate_id
FROM gate_map g
WHERE g.predicate_id NOT IN (SELECT gcir_id FROM predicate)
ORDER BY g.gate_id;

-- Q8b. Decisive predicate not in any gate-map
SELECT p.gcir_id, p.origin_id
FROM predicate p
WHERE p.mandatory_role = 'decisive'
  AND p.gcir_id NOT IN (SELECT predicate_id FROM gate_map)
ORDER BY p.gcir_id;
```

**Negative fixture:** Add a gate-map entry referencing a non-existent predicate gcir_id; or remove a decisive predicate from gate_map while keeping it in the bundle.

**Relationship to Q1-Q6:** Q3 checks origin. Q8 checks that gates consuming those predicates are internally consistent.

---

### Q9: Actuation authority validity

**Normative definition:**

For each actuation a ∈ evidence.actuations, verify that the action tuple:
- (a.subject, a.action, a.resource, a.destination)

resolves to an entry in the authority matrix S.authority_matrix at the time of a.actuation_time, **AND**

the evidence producer referenced by the receipt or predicate that justified the actuation is also resolvable in S.authority_matrix (or is an externally trusted producer explicitly authorized in the system policy).

**Violation:** Action tuple does not resolve in the authority matrix at actuation time; or the evidence producer cannot be resolved.

**Manuscript reference:** Section III-2: "The authority_matrix is the closed vocabulary from which predicate subjects, actions, resources and destinations are drawn."

**Note:** This query audits **runtime applicability** of the authority matrix. The compiler (Φ) verifies authority at compile-time (Appendix A constraint 5); Q9 checks that authority remains valid at runtime.

**Objects involved:** actuation, authority_matrix (at actuation time), evidence_producer

**Expected query result on conforming artifact:** Empty (all actuations are authorized at their time; all evidence producers are recognized)

**SQL:**
```sql
-- Q9. Actuation authority validity
-- (This is a conceptual query; implementation requires the authority matrix at actuation time)
SELECT a.actuation_id, a.subject, a.action, a.resource, a.destination
FROM actuation a
LEFT JOIN authority_matrix m ON (
    m.subject = a.subject
    AND m.action = a.action
    AND m.resource = a.resource
    AND m.destination = a.destination
    AND m.effective_from <= a.actuation_time
    AND (m.effective_until IS NULL OR m.effective_until > a.actuation_time)
)
WHERE m.authority_id IS NULL
ORDER BY a.actuation_id;
```

**Negative fixture:** Create an actuation whose (subject, action, resource, destination) tuple does not exist in the authority matrix; or set authority_until before actuation_time, retiring the action before it is used.

**Relationship to Q1-Q6:** Q6 checks registry signatures. Q9 checks authority applicability at runtime.

---

### Q10: Mandatory predicate evidence integrity

**Normative definition:**

For each predicate p ∈ B with mandatory_role = 'decisive', verify that:
1. p.on_unknown = 'fail' (fail-closed for missing evidence)
2. The evidence producer named in the predicate's context_conditions is resolvable in S.authority_matrix OR is an explicitly trusted external source
3. If p includes a temporal_window, that window is satisfied by the evidence schema (evidence_producer can provide timestamps, evidence is fresher than required)

**Violation:** A mandatory predicate with on_unknown ≠ 'fail'; or an evidence producer that does not exist or is not authorized; or evidence staleness requirement cannot be met.

**Manuscript reference:** Section V: "Missing or indeterminate evidence causes failure."  Section VI-C: "Required evidence producers must be resolvable."

**Objects involved:** predicate (mandatory), evidence_producer, authority_matrix, evidence schema

**Expected query result on conforming artifact:** Empty (all mandatory predicates are fail-closed and have resolvable, non-stale evidence producers)

**SQL:**
```sql
-- Q10. Mandatory predicate evidence integrity
SELECT p.gcir_id, p.on_unknown, p.evidence_producer
FROM predicate p
WHERE p.mandatory_role = 'decisive'
  AND (
    p.on_unknown != 'fail'
    OR p.evidence_producer NOT IN (SELECT producer_id FROM evidence_producer_registry)
    OR p.evidence_schema_ref NOT IN (SELECT schema_id FROM evidence_schema_registry)
  )
ORDER BY p.gcir_id;
```

**Negative fixture:** Create a mandatory predicate with on_unknown = 'warn' or 'pass_with_approved_exception'; or reference an evidence_producer not in the authority matrix; or specify a required freshness window that no evidence source can provide.

**Relationship to Q1-Q6:** Q3-Q5 check temporal and lineage integrity. Q10 checks evidence availability and fail-closedness of gates.

---

## SUMMARY TABLE: Q1-Q10

| Query | Type | Detects | Objects | Clean expected | 5.5d? |
|-------|------|---------|---------|---|---|
| Q1 | Temporal | Obligation without disposition | O, R, Δ | ✓ ∀o | ✗ (existing) |
| Q2 | Temporal | Risk without exactly one disposition | R, Δ | ✓ ∀r | ✗ (existing) |
| Q3 | Temporal | Orphan predicate | P, R, INV, ACS | ✓ ∀p | ✗ (existing) |
| Q4 | Temporal | Invalid receipt bundle | receipts, B, REG | ✓ ∀t | ✗ (existing) |
| Q5 | Temporal | Actuation without prior receipt | actuations, receipts | ✓ ∀a | ✗ (existing) |
| Q6 | Temporal | Unsigned/forged registry entry | REG, keys | ✓ ∀l | ✗ (existing) |
| Q7 | Structural | Runtime ACS → zero predicates | ACS, P, Δ | ✓ ∀acs | ✓ (NEW) |
| Q8 | Structural | Gate/predicate closure | gate_map, P | ✓ ∀g, ∀p | ✓ (NEW) |
| Q9 | Structural | Actuation authority invalid | actuations, S, REG | ✓ ∀a | ✓ (NEW) |
| Q10 | Structural | Mandatory predicate incomplete | P, S, evidence_registry | ✓ ∀p_mandatory | ✓ (NEW) |

---

## IMPLEMENTATION NOTES

### Q1-Q6 (Existing)

These queries are already specified in `queries/traceability.sql`. Their definitions remain unchanged. However:

- Q3 must be rerun after Case B ACS expansion to 9 (new origin linkages)
- Q4-Q5 behavior does not change with ACS count
- Q1, Q2, Q6 behavior does not change

### Q7-Q10 (New, awaiting approval)

These are NEW and must be added to the traceability audit suite. Implementation will:

1. Extend `src/gcir/traceability.py` with Q7-Q10 query definitions
2. Add Q7-Q10 to `queries/traceability.sql`
3. Create negative fixture definitions for each (see Section 4 below)
4. Add Q7-Q10 to the test suite
5. Update `tools/verify_reported_results.py` to include Q7-Q10 results

### Evidence Model Requirements

Q9 and Q10 require that the evidence store include:

- A resolvable reference to the authority matrix at each actuation time (or a mechanism to reconstruct it)
- Evidence schema registry / evidence producer registry
- Temporal metadata on evidence freshness

Case A and Case B fixtures must be extended to include these to support Q9-Q10 testing.

---

## NEGATIVE FIXTURE REFERENCE

See `AUDIT_QUERY_NEGATIVE_FIXTURE_PLAN.md` (Section 4 below) for detailed negative fixture specifications for Q1-Q10.

