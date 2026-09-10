# AUDIT_QUERY_NEGATIVE_FIXTURE_PLAN.md

**Purpose:** Specify minimal negative fixtures for each query Q1-Q10 to verify detection.

**Design principle:** Each fixture introduces exactly ONE violation per query where feasible. Multiple defects are noted where necessary.

---

## Q1: OBLIGATIONS WITHOUT AN APPROVED DISPOSITION

### Valid fixture base (Case A or B)
- Obligation O_1 in obligation register
- Risk R_A linked to O_1 via risk_obligation.obligation_refs
- Risk R_A has disposition δ_A.status = 'runtime' or 'accepted'
- Result: Q1 empty (O_1 is dispositioned)

### Negative mutation
**Single defect:** Remove the risk_obligation entry linking O_1 to R_A, or set the linking risk's disposition to 'unresolved'.

**Details:**
- File to mutate: risk_obligation cross-table (or in assessment.json if flat structure)
- Exact change: Delete or comment out the risk_obligation entry where obligation_id = O_1
- OR: Change disposition δ_A.status from 'runtime' to 'unresolved'

### Expected detection
Q1 returns O_1 as a row with no approved disposition.

### Why one defect is sufficient
An obligation's availability is binary (dispositioned or not). One violated link is enough to instantiate the violation.

### Secondary triggers
Removing the link does not trigger Q2 (risk still has one disposition), nor Q3 (existing predicates still valid), nor Q4-Q10.

---

## Q2: RISKS WITHOUT EXACTLY ONE DISPOSITION

### Valid fixture base
- Risk R_1 in risk register
- Disposition δ_1 exists with δ_1.risk_id = R_1, δ_1.status ∈ {runtime, nonruntime, accepted, unresolved}
- Result: Q2 empty (R_1 has exactly one disposition)

### Negative mutation A: Zero dispositions
**Single defect:** Create a risk R_new in the register, then do NOT create a disposition for it.

**Details:**
- File: risk register (risk.json or similar)
- Add: { "risk_id": "R-NEW", "cause": "...", "event": "...", "consequence": "..." }
- Do NOT add any corresponding disposition

### Expected detection
Q2 returns R_new with disposition_count = 0.

### Negative mutation B: Two dispositions
**Alternative defect:** Create a risk R_dual and assign two disposition records to it.

**Details:**
- File: disposition register
- For risk_id = R_dual, add two records:
  - δ_dual_1 with status = 'runtime'
  - δ_dual_2 with status = 'nonruntime'

### Expected detection
Q2 returns R_dual with disposition_count = 2.

### Why each is a clean single defect
- Mutation A: Only risk R_new violates (has 0); all other risks still have exactly 1
- Mutation B: Only risk R_dual violates (has 2); all other risks still have exactly 1
- These violations are independent

### Secondary triggers
Neither mutation triggers Q1 (Q1 checks obligations, not risks), nor Q3-Q10.

---

## Q3: PREDICATES WITHOUT A RISK OR COMPILER-INVARIANT ORIGIN

### Valid fixture base
- Predicate p_1 in compiled bundle P
- p_1.origin_type = 'risk_derived'
- p_1.origin_id = R_1 (a valid risk)
- p_1.acs_id = ACS_1 (an ACS approved in judgment record J)
- Result: Q3 empty (p_1 has valid origin)

### Negative mutation A: Non-existent risk origin
**Single defect:** Add a predicate p_bad to the bundle with origin_type='risk_derived', origin_id='R_MISSING' where R_MISSING does not exist in R.

**Details:**
- File: compiled_bundle.json (predicates array)
- Add: { "gcir_id": "GCIR-BAD-1", "origin_type": "risk_derived", "origin_id": "R_MISSING", "acs_id": "ACS_1", ... }
- Ensure "R_MISSING" is not in the risk register

### Expected detection
Q3 returns GCIR_BAD_1 with origin_id='R_MISSING' (does not resolve).

### Negative mutation B: Non-approved ACS
**Alternative defect:** Add a predicate p_bad with origin_type='risk_derived', origin_id=R_1, but acs_id='ACS_UNAPPROVED' where ACS_UNAPPROVED is not in the judgment record.

**Details:**
- File: compiled_bundle.json (predicates array)
- Add: { "gcir_id": "GCIR-BAD-2", "origin_type": "risk_derived", "origin_id": "R_1", "acs_id": "ACS_UNAPPROVED", ... }
- Ensure "ACS_UNAPPROVED" is not in judgment.approved_acs_set

### Expected detection
Q3 returns GCIR_BAD_2 (acs_id does not resolve to approved set).

### Negative mutation C: Orphan invariant
**Alternative defect:** Add a predicate p_inv with origin_type='compiler_invariant', origin_id='INV_MISSING' where INV_MISSING does not exist in invariants.

### Why these are clean single defects
Each mutation adds exactly one invalid predicate. Other predicates retain valid origins.

### Secondary triggers
Q7 may be triggered if the bad predicate is risk_derived and the risk is runtime (no predicate really emitted, only the bad one). This is acceptable overlap: Q7 would catch "non-existent ACS emitted zero valid predicates."

---

## Q4: RECEIPTS WHOSE BUNDLE WAS NOT VALID AT DECISION TIME

### Valid fixture base
- Receipt t_1 with bundle_hash matching a compiled bundle B
- t_1.decision_time ≥ B.bundle_effective_from
- No lifecycle entry retires B before t_1.decision_time
- Result: Q4 empty (bundle was valid at decision time)

### Negative mutation A: Hash mismatch
**Single defect:** Create a receipt t_bad with bundle_hash = 'SHA256_NONEXISTENT' where no compiled bundle has this hash.

**Details:**
- File: receipts array in evidence store
- Add: { "receipt_id": "RCP-BAD-1", "bundle_hash": "aaaa....", "decision_time": "2026-01-01T00:00:00Z", ... }
- Ensure bundle_hash does not match any bundle in the compiled artifact

### Expected detection
Q4 returns RCP_BAD_1 (bundle not found or hash does not bind).

### Negative mutation B: Bundle not yet effective
**Alternative defect:** Create a receipt t_bad with decision_time = '2025-12-01' and bundle.bundle_effective_from = '2026-01-01' (future).

**Details:**
- File: receipts array
- Add receipt with decision_time < bundle.bundle_effective_from

### Expected detection
Q4 returns RCP_BAD_2 (decision made before bundle was effective).

### Negative mutation C: Bundle retired before decision
**Alternative defect:** Create a lifecycle registry entry that retires the bundle before receipt decision_time.

**Details:**
- File: lifecycle_registry array
- Add: { "entry_id": "LCY-1", "bundle_hash": "...", "action": "retire", "effective_from": "2025-12-01", ... }
- Add receipt t_bad with decision_time = '2026-01-01' (after retirement)

### Why each is a clean single defect
Each mutation creates exactly one invalid receipt. Other receipts retain valid bundles.

### Secondary triggers
Mutation C also adds a lifecycle entry. Q6 might trigger if the entry is not signed. Ensure the retirement entry is properly signed to test Q4 in isolation.

---

## Q5: ACTUATION WITHOUT A TEMPORALLY PRIOR COMMITTED RECEIPT

### Valid fixture base
- Actuation a_1 with receipt_id = RCP_1
- Receipt RCP_1 exists with:
  - authorization_time = T1
  - evidence_commit_time = T2
  - actuation_time = T3
  - Constraint: T1 ≤ T2 < T3
- Result: Q5 empty (proper temporal order)

### Negative mutation A: Missing receipt
**Single defect:** Create an actuation a_bad with receipt_id = 'RCP_MISSING' where RCP_MISSING does not exist in receipts.

**Details:**
- File: actuations array
- Add: { "actuation_id": "ACT-BAD-1", "receipt_id": "RCP_MISSING", "actuation_time": "2026-01-02T00:00:00Z", ... }
- Ensure "RCP_MISSING" is not in receipts array

### Expected detection
Q5 returns ACT_BAD_1 (receipt does not exist).

### Negative mutation B: Authorization after commit
**Alternative defect:** Create receipt RCP_bad with authorization_time > evidence_commit_time (violates T1 ≤ T2).

**Details:**
- File: receipts array
- Add: { "receipt_id": "RCP-BAD-2", "authorization_time": "2026-01-02T00:00:00Z", "evidence_commit_time": "2026-01-01T00:00:00Z", ... }

### Expected detection
Q5 returns actuation a_bad with broken authorization_time > evidence_commit_time.

### Negative mutation C: Commit after actuation
**Alternative defect:** Create receipt RCP_bad with evidence_commit_time ≥ actuation_time (violates T2 < T3).

**Details:**
- File: receipts array
- Add: { "receipt_id": "RCP-BAD-3", "evidence_commit_time": "2026-01-02T00:00:00Z", ... }
- Link actuation with actuation_time = "2026-01-02T00:00:00Z" or earlier

### Why each is a clean single defect
Each mutation affects one actuation or the receipt it references. Temporal order is broken in exactly one place.

### Secondary triggers
If the missing receipt is linked by Q6 to a lifecycle entry, Q6 may not trigger (Q6 checks registry signing, not receipt validity). These are orthogonal.

---

## Q6: LIFECYCLE-REGISTRY RECORDS LACKING VALID SIGNING AUTHORITY

### Valid fixture base
- Lifecycle entry l_1 in lifecycle_registry
- l_1.authority ∈ authorized_signing_authorities
- l_1.signature is valid (cryptographically verifies with the key l_1.signing_key_id)
- Result: Q6 empty (all entries signed validly)

### Negative mutation A: Unauthorized signer
**Single defect:** Create a lifecycle entry l_bad with authority = 'unauthorized_party' where 'unauthorized_party' is not in the list of authorized signers.

**Details:**
- File: lifecycle_registry array
- Add: { "entry_id": "LCY-BAD-1", "bundle_hash": "...", "action": "retire", "authority": "unauthorized_party", "signing_key_id": "key_bad", "signature": "...", ... }
- Ensure "unauthorized_party" is not in authorized_signing_keys list

### Expected detection
Q6 returns LCY_BAD_1 (authority not authorized).

### Negative mutation B: Invalid signature
**Alternative defect:** Create a lifecycle entry l_bad with a forged/invalid signature that does not verify.

**Details:**
- File: lifecycle_registry array
- Add entry with a random or altered signature_b64 that fails cryptographic verification

### Expected detection
Q6 returns LCY_BAD_2 (signature does not verify).

### Why each is a clean single defect
- Mutation A: Authority key is missing
- Mutation B: Signature is cryptographically invalid
- Each breaks one aspect of signing validity

### Secondary triggers
Neither mutation affects Q1-Q5 (which deal with obligations, dispositions, predicates, receipts, actuations—not registry entries).

---

## Q7: RUNTIME ACS WITH ZERO EMITTED PREDICATES (NEW)

### Valid fixture base
- ACS acs_1 with disposition δ_1.status = 'runtime'
- Predicate p_1 in bundle P with origin_type='risk_derived', acs_id=acs_1
- Result: Q7 empty (runtime ACS has at least one predicate)

### Negative mutation
**Single defect:** Create a runtime ACS acs_bad, but do NOT emit any predicate for it in the compiler output.

**Details:**
- File: approved_control_specifications.json
- Add: { "acs_id": "ACS-BAD-07", "risk_id": "R_NEW", ..., disposition.status = 'runtime' }
- In compiled_bundle.json predicates array, do NOT add any predicate with acs_id = "ACS-BAD-07"

### Expected detection
Q7 returns ACS_BAD_07 (runtime ACS with emitted_predicate_count = 0).

### Why this is a clean single defect
Only ACS_BAD_07 violates. Other runtime ACS retain their predicates.

### Secondary triggers
The missing predicate might trigger Q7 only (not Q1-Q6, which do not check ACS→predicate mapping). Q8 would not trigger unless a gate references the missing predicate.

---

## Q8: GATE/PREDICATE REFERENCE INTEGRITY (NEW)

### Valid fixture base
- Gate-map entry g_1 referencing predicate p_1
- Predicate p_1 exists in bundle P
- If p_1.mandatory_role = 'decisive', g_1 is in gate_map
- Result: Q8 empty (gates and predicates close properly)

### Negative mutation A: Gate references non-existent predicate
**Single defect:** Add a gate-map entry g_bad with predicate_id = 'GCIR_MISSING' where GCIR_MISSING is not in the bundle.

**Details:**
- File: gate_map in compiled_bundle.json
- Add: { "gate_id": "G-BAD-1", "decision_id": "...", "predicate_id": "GCIR_MISSING", ... }
- Ensure "GCIR_MISSING" is not in predicates array

### Expected detection
Q8 returns G_BAD_1 (predicate does not exist).

### Negative mutation B: Decisive predicate not gated
**Alternative defect:** Add a predicate p_bad with mandatory_role='decisive' but do NOT add it to any gate-map entry.

**Details:**
- File: predicates array in compiled_bundle.json
- Add: { "gcir_id": "GCIR-BAD-8", "mandatory_role": "decisive", ... }
- Ensure no gate-map entry references GCIR_BAD_8

### Expected detection
Q8 returns GCIR_BAD_8 (decisive predicate not in gate_map).

### Why each is a clean single defect
- Mutation A: One gate references a missing predicate
- Mutation B: One decisive predicate is not gated
- Other gates and predicates retain closure

### Secondary triggers
Mutation B might also trigger Q7 if the unimplemented predicate is risk_derived. This is acceptable overlap: "predicate not gated" and "ACS didn't emit a usable predicate" are related.

---

## Q9: ACTUATION AUTHORITY VALIDITY (NEW)

### Valid fixture base
- Actuation a_1 with (subject, action, resource, destination) tuple
- Tuple resolves in authority_matrix S at a_1.actuation_time
- Evidence producer named in the predicate is in S
- Result: Q9 empty (authority is valid at runtime)

### Negative mutation A: Action tuple not authorized
**Single defect:** Create an actuation a_bad with (subject='X', action='Y', resource='Z', destination='W') where this tuple does not exist in authority_matrix.

**Details:**
- File: actuations array in evidence store
- Add: { "actuation_id": "ACT-BAD-9A", "subject": "unauthorized_subject", "action": "unauthorized_action", "resource": "...", "destination": "..." }
- Ensure this exact 4-tuple is NOT in authority_matrix

### Expected detection
Q9 returns ACT_BAD_9A (action tuple does not resolve).

### Negative mutation B: Evidence producer not authorized
**Alternative defect:** Create an actuation a_bad whose receipt references an evidence_producer that is not in S.

**Details:**
- File: receipts array
- Add receipt with evidence_producer = 'unknown_service_v9'
- Ensure 'unknown_service_v9' is not in authority_matrix as a valid producer

### Expected detection
Q9 returns ACT_BAD_9B (evidence producer cannot be resolved).

### Negative mutation C: Authority expired before actuation
**Alternative defect:** Create an authority_matrix entry with effective_until < actuation_time.

**Details:**
- File: authority_matrix in policy_metadata.json
- Add entry: { subject='X', action='Y', ..., effective_until='2025-12-31T23:59:59Z' }
- Create actuation with actuation_time='2026-01-01T00:00:00Z'

### Why each is a clean single defect
Each mutation violates one aspect of authority validity:
- A: Tuple not authorized
- B: Producer not authorized
- C: Authority expired

### Secondary triggers
Mutation B might also trigger Q10 if the evidence schema is missing. These are related (both about evidence) but distinct violations.

---

## Q10: MANDATORY PREDICATE EVIDENCE INTEGRITY (NEW)

### Valid fixture base
- Predicate p_1 with mandatory_role='decisive'
- p_1.on_unknown = 'fail' (fail-closed)
- p_1.evidence_producer is resolvable in S
- p_1.evidence_schema_ref is valid and supported
- Result: Q10 empty (mandatory evidence is complete)

### Negative mutation A: Non-fail-closed on_unknown
**Single defect:** Create a mandatory predicate p_bad with on_unknown ≠ 'fail'.

**Details:**
- File: predicates array in compiled_bundle.json
- Add: { "gcir_id": "GCIR-BAD-10A", "mandatory_role": "decisive", "on_unknown": "warn", ... }

### Expected detection
Q10 returns GCIR_BAD_10A (on_unknown is not 'fail').

### Negative mutation B: Evidence producer not resolvable
**Alternative defect:** Create a mandatory predicate p_bad with evidence_producer = 'nonexistent_service' where this service is not in authority_matrix.

**Details:**
- File: predicates array
- Add: { "gcir_id": "GCIR-BAD-10B", "mandatory_role": "decisive", "on_unknown": "fail", "evidence_producer": "nonexistent_service", ... }
- Ensure "nonexistent_service" is not in authority_matrix or evidence_producer_registry

### Expected detection
Q10 returns GCIR_BAD_10B (evidence_producer not found).

### Negative mutation C: Evidence schema missing
**Alternative defect:** Create a mandatory predicate with evidence_schema_ref = 'SCHEMA_MISSING' where SCHEMA_MISSING is not in evidence_schema_registry.

**Details:**
- File: predicates array
- Add: { "gcir_id": "GCIR-BAD-10C", "mandatory_role": "decisive", "on_unknown": "fail", "evidence_schema_ref": "SCHEMA_MISSING", ... }

### Why each is a clean single defect
Each mutation violates one evidence-integrity constraint:
- A: Not fail-closed
- B: Producer missing
- C: Schema missing

### Secondary triggers
None. Q10 is the only query focused on on_unknown and evidence producer availability.

---

## SUMMARY: NEGATIVE FIXTURES FOR Q1-Q10

| Query | Mutation | Violation | Expected return | Secondary triggers |
|-------|----------|-----------|------------------|-------------------|
| Q1 | Remove risk_obligation link | Obligation unlinked | O_1 | None |
| Q2A | Zero disposition | Risk with 0 dispositions | R_new | None |
| Q2B | Two dispositions | Risk with 2 dispositions | R_dual | None |
| Q3A | Non-existent risk origin | Predicate origin invalid | GCIR_BAD_1 | None |
| Q3B | Non-approved ACS | ACS not in judgment | GCIR_BAD_2 | Possibly Q7 if runtime |
| Q3C | Orphan invariant | Invariant missing | GCIR_BAD_3 | None |
| Q4A | Hash mismatch | Bundle not found | RCP_BAD_1 | None |
| Q4B | Bundle not effective | Decision before effective | RCP_BAD_2 | None |
| Q4C | Bundle retired | Bundle superseded | RCP_BAD_3 (+ registry entry) | Q6 if entry unsigned |
| Q5A | Missing receipt | Actuation orphan | ACT_BAD_1 | None |
| Q5B | Authorization after commit | T1 > T2 | ACT_BAD_2 | None |
| Q5C | Commit after actuation | T2 ≥ T3 | ACT_BAD_3 | None |
| Q6A | Unauthorized signer | Authority not in list | LCY_BAD_1 | None |
| Q6B | Invalid signature | Signature fails verification | LCY_BAD_2 | None |
| Q7 | Zero predicates | Runtime ACS emits nothing | ACS_BAD_07 | Possibly Q8 if gated |
| Q8A | Missing predicate | Gate references void | G_BAD_1 | None |
| Q8B | Ungated decisive | Decisive predicate not gated | GCIR_BAD_8 | Possibly Q7 if runtime |
| Q9A | Unauthorized tuple | Action tuple invalid | ACT_BAD_9A | None |
| Q9B | Unknown producer | Evidence producer missing | ACT_BAD_9B | Possibly Q10 |
| Q9C | Expired authority | Authority_until < actuation | ACT_BAD_9C | None |
| Q10A | Non-fail-closed | on_unknown ≠ fail | GCIR_BAD_10A | None |
| Q10B | Producer missing | Evidence producer invalid | GCIR_BAD_10B | None |
| Q10C | Schema missing | Evidence schema invalid | GCIR_BAD_10C | None |

---

## FIXTURE IMPLEMENTATION APPROACH

### For Case A and Case B

Create parallel fixture sets:

```
cases/case_a/negative_fixtures/
  Q1_obligation_unlinked/
    evidence_store.json (with Q1 violation)
    expected_query_result.json
  Q2_zero_disposition/
    evidence_store.json
    expected_query_result.json
  ...
  Q10_schema_missing/
    evidence_store.json
    expected_query_result.json

cases/case_b/negative_fixtures/
  (same structure)
```

Each negative fixture should:
1. Start with a **valid** base case (Case A or B clean fixture)
2. Apply exactly **one mutation** per query
3. Document the mutation clearly
4. Specify the **expected returned identifier(s)** from the query
5. Note any **secondary triggers** (other queries that might also return results)

### Test Harness

```python
# tests/integration/test_audit_query_negative_controls.py

for case_name in ['case_a', 'case_b']:
    for query_num in range(1, 11):
        for mutation in get_mutations_for_query(query_num):
            fixture = load_negative_fixture(case_name, query_num, mutation)
            result = run_query(query_num, fixture)
            assert len(result) > 0, f"Q{query_num} failed to detect {mutation}"
            assert expected_violation_id in result, f"Q{query_num} returned wrong violation"
```

