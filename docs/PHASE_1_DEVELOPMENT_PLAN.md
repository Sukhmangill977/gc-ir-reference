# PHASE_1_DEVELOPMENT_PLAN.md

**Status:** DEVELOPMENT IN PROGRESS

**Date started:** 2026-09-10

**Configuration:** 6-ACS, 6 risk-derived predicates, 3 compiler-invariant predicates, 9 total

---

## DEVELOPMENT OBJECTIVES

1. ✅ Correct manuscript specification (6 ACS) — COMPLETE
2. ⏳ Verify exact runtime outcomes (PERMIT/DENY/HOLD) for 13 injections
3. ⏳ Implement Q7-Q10 audit queries
4. ⏳ Create negative fixtures for Q1-Q10
5. ⏳ Update runtime decision reporting (PERMIT/DENY/HOLD vs. SAFE_STATE)
6. ⏳ Run development test suite
7. ⏳ Report final results (24 items)

---

## TASK 2: EXACT RUNTIME OUTCOMES FOR 13 INJECTIONS

**Status:** VERIFICATION IN PROGRESS

**Expected from forensic audit:**
- **HOLD (4):** Scenarios 1, 2, 7, 13 (unknown evidence + escalation)
- **DENY (9):** Scenarios 3-6, 8-12 (known policy violation)
- **SAFE_STATE (13):** All scenarios fail to permit

**Current test assertion:** `verdict["decision"] == "SAFE_STATE"`

**Required update:** Individual assertions per scenario
- Scenarios 1, 2, 7, 13: Assert `decision == "HOLD"`
- Scenarios 3-6, 8-12: Assert `decision == "DENY"`
- All 13: Assert `safe_state == true` (secondary aggregate)

**Current architecture question:** Does the resolver return an exact decision enum, or only PERMIT/SAFE_STATE?

---

## TASK 3: IMPLEMENT Q7-Q10 AUDIT QUERIES

**Specifications complete:** `CORRECTED_Q7_Q10_SPECIFICATION_5_5D.md`

**Q7:** Runtime ACS with zero emitted predicates
- For each ACS: count(risk-derived predicates where acs_id = ACS) >= 1
- Case B expected: 6 ACS, 6 risk-derived predicates → 6/6 ✓

**Q8:** Gate/predicate reference integrity
- Every gate-map entry must reference an existing predicate
- Every mandatory predicate must appear in gate-map
- Case B status: 9 predicates, all gated ✓

**Q9:** Actuation authority validity
- Every action must be authorized at actuation time
- Authority matrix must resolve all evidence producers
- Case B expected: clean (no actuations in test environment)

**Q10:** Mandatory predicate evidence integrity
- Every mandatory predicate: on_unknown = fail
- All evidence producers resolvable
- Case B expected: clean (Q10 verify)

**Implementation path:**
1. Write SQL for Q7-Q10 in `queries/traceability.sql`
2. Update `src/gcir/traceability.py` with query logic
3. Run Q1-Q10 against valid Case A and Case B evidence
4. Expected: 10/10 clean results

---

## TASK 4: NEGATIVE FIXTURES FOR Q1-Q10

**Scope:** 10 seeded violations (one per query)

**For each query:**
- Create minimal evidence store mutation that triggers the violation
- Verify query detects it (returns non-empty result)
- Record both the mutation and the detected outcome

**Expected structure:**
```
cases/case_b/negative_fixtures/
  Q1_obligation_unresolved/
    evidence_store.json
    expected_query_result.json (non-empty)
  ...
  Q10_mandatory_evidence_fails/
    ...
```

**Implementation path:**
1. Design mutation for each query
2. Create fixture files
3. Run test suite `test_audit_query_negative_fixtures.py`
4. Report: 10/10 detected

---

## TASK 5: RUNTIME DECISION REPORTING

**Current code architecture:**
```python
verdict["decision"] = "SAFE_STATE"  # All non-permit
```

**Required new reporting:**
```python
verdict["decision"] = "PERMIT" | "DENY" | "HOLD"
verdict["safe_state"] = (verdict["decision"] != "PERMIT")
```

**Affected files:**
- `src/gcir/precedence.py` (resolver/decision logic)
- `experiments/case_b_injection_scenarios.py` (test harness)
- Query/report infrastructure

**Implementation constraint:** Do NOT break backward compatibility with SAFE_STATE; add exact_outcome alongside.

---

## TASK 6: DEVELOPMENT TEST SUITE

**Current test count (v2.2 freeze):** 280 tests

**Development test suite must include:**
- [ ] Case A compilation (unchanged)
- [ ] Case B compilation (unchanged)
- [ ] Q1-Q6 valid queries (Case A + B)
- [ ] Q7-Q10 new queries (Case A + B)
- [ ] Negative fixtures Q1-Q10 (Case A + B)
- [ ] 13 exact-outcome injections with assertions
- [ ] Property tests (disposition, authority closure, C* coverage)
- [ ] Adversarial tests (determinism, hash immutability)

**Expected development test count:** ~320-340 tests

---

## TASK 7: COMPILATION & BUNDLE STATE

**Current Case B (final_v2):**
- Bundle hash: `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce`
- ACS: 6 (unchanged)
- Risk-derived predicates: 6
- Compiler-invariants: 3
- Total: 9

**Development recompilation:**
- Input: 6 ACS, same judgment records, same catalog
- Expected output: Identical bundle hash (inputs unchanged)
- If hash differs: Investigate root cause

---

## TASK 8: FINAL GO/NO-GO FOR PHASE 2 (v3 FREEZE)

**Phase 2 decision gates:**

1. ✅ Manuscript specification corrected (6 ACS) — COMPLETE
2. ⏳ All 13 injections have exact outcome assertions — IN PROGRESS
3. ⏳ Q1-Q10 all clean on valid artifacts — PENDING
4. ⏳ Q1-Q10 all detect violations on negative fixtures — PENDING
5. ⏳ Development test suite passes — PENDING
6. ⏳ Case B bundle hash unchanged (or justified change) — PENDING
7. ⏳ No regression in Case A — PENDING
8. ⏳ No modifications to final_v2 or v1.0.3 — VERIFIED

**If all gates pass:** Ready for preregister-tier0-v3 freeze

**If any gate fails:** Debug and report; do NOT freeze until resolved

---

## DELIVERABLES (24-ITEM FINAL REPORT)

After Phase 1 development, report:

1. New manuscript version/path (5.5e)
2. "9 ACS" references: All removed/corrected? (yes)
3. Historical provenance retained? (yes)
4. Final Case B ACS count (6)
5. Semantic justification for all 6 (provided in CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md)
6. Actual development P_B_risk (expected 6)
7. Actual P_B_inv (expected 3)
8. Actual P_B_total (expected 9)
9. Development Case B bundle hash (expected: unchanged)
10. Whether hash changed and why (expected: no change)
11. Q1-Q10 clean results for Case A (expected: 10/10)
12. Q1-Q10 clean results for Case B (expected: 10/10)
13. Negative-fixture detection results (expected: 10/10 detected)
14. Exact 13-injection outcome: HOLD count and IDs (4: 1,2,7,13)
15. Exact 13-injection outcome: DENY count and IDs (9: 3-6,8-12)
16. Exact 13-injection outcome: SAFE_STATE aggregate result (all 13)
17. Total development test count (estimated 320-340)
18. Code/spec disagreements remaining (expected: none)
19. Case A scientific artifacts changed? (expected: no)
20. final_v2 changed? (expected: no)
21. Historical tags moved? (expected: no)
22. Remaining manuscript defects? (expected: none)
23. Data file structure changes? (expected: none)
24. GO / NO-GO for preregister-tier0-v3 (decision pending completion)

---

## NO NEW FREEZE UNTIL COMPLETE

**Do NOT create:**
- preregister-tier0-v3
- final_v3 campaign
- v1.0.4 release
- Any new scientific freeze

**When to create:** After all 24 items reported and Phase 2 gates cleared.

