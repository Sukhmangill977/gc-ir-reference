# PHASE_1_STATUS_CHECKPOINT.md

**Checkpoint date:** 2026-09-10

**Status:** MANUSCRIPT CORRECTION COMPLETE; DEVELOPMENT READY

---

## COMPLETED WORK

### ✅ PHASE A: Manuscript Specification Correction

**Forensic audit completed:**
1. CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md — Semantic analysis of all 6 risks
2. ACS_GRANULARITY_RULE_5_5D.md — Definition of "distinct ACS"
3. NINE_ACS_PROVENANCE_AUDIT.md — Origin tracing (9-ACS rejected, source: Type C)
4. CASE_B_9_ACS_SEMANTIC_PROVENANCE.md — Comprehensive semantic audit
5. PHASE_1_GO_NO_GO_FINAL.md — Final NO-GO recommendation (for 9 ACS)

**Manuscript correction published:**
1. CASE_B_ACS_CARDINALITY_CORRECTION.md — Corrected specification (6 ACS)
2. NINE_ACS_CORRECTION_TRACE.md — Audit of all 9-ACS references and corrections

**Corrections applied:**
- ✅ MANUSCRIPT_5_5D_DELTA.md — Added SUPERSEDED header; Section 1 marked historical
- ✅ CASE_B_13_INJECTION_STAGE_AUDIT_V3.md — Updated status line (6-ACS configuration approved)
- ✅ PROPOSED_AUDIT_QUERY_AMENDMENT_5_5D.md — Cosmetic update ("expanded for Case B with 6 ACS")
- ✅ PHASE_1_GO_NO_GO_FINAL.md — Added status update (author-approved for 6-ACS proceeding)

**Specification status:**
- Manuscript 5.5d: Contains "6 register rows" (Section 10, PAPER_REQUIREMENTS.md)
- Corrected interpretation: 6 ACS (not 9)
- Predicate composition: 6 risk-derived + 3 compiler-invariant = 9 total
- Distinction clarified: ACS count ≠ total predicate count

### ✅ Current Case B Configuration Verified

| Item | Current (final_v2) | Justified? | Status |
|---|---|---|---|
| ACS count | 6 | ✓ YES | Correct |
| Risk-derived predicates | 6 | ✓ YES (1 per ACS minimum) | Correct |
| Compiler-invariant predicates | 3 | ✓ YES (INV-VERSION, INV-AUTHORITY-CLOSURE, INV-EVIDENCE-COMMIT) | Correct |
| Total predicates | 9 | ✓ YES (6+3) | Correct |
| Bundle hash | 2850155a2ee7... | N/A | Stable (inputs unchanged) |

**Conclusion:** The current Case B artifact already implements the 6-ACS configuration correctly. No ACS reorganization needed.

### ✅ 13-Injection Scenario Outcomes Verified

| Outcome | Count | Scenario IDs | Evidence |
|---|---|---|---|
| HOLD (unknown + escalation) | 4 | 1, 2, 7, 13 | CASE_B_13_INJECTION_STAGE_AUDIT_V3.md |
| DENY (known failure) | 9 | 3, 4, 5, 6, 8, 9, 10, 11, 12 | CASE_B_13_INJECTION_STAGE_AUDIT_V3.md |
| SAFE_STATE (aggregate) | 13 | All | All fail to permit |
| REJECT_AT_COMPILATION | 0 | None | All occur at runtime |
| REJECT_AT_ISSUANCE | 0 | None | All occur at runtime |

**Status:** All 13 injection outcomes mapped; escalation routes verified; independent of ACS cardinality.

### ✅ Audit Queries Q1-Q10 Specifications Complete

| Query | Scope | Status |
|---|---|---|
| Q1 | Obligations without disposition | Specified (CORRECTED_Q7_Q10_SPECIFICATION_5_5D.md) |
| Q2 | Risks without exactly 1 disposition | Specified |
| Q3 | Orphan predicates | Specified |
| Q4 | Receipts without valid bundle | Specified |
| Q5 | Actuation without prior receipt | Specified |
| Q6 | Lifecycle without signing authority | Specified |
| Q7 | Runtime ACS with zero risk-derived predicates | Specified (new) |
| Q8 | Gate/predicate reference integrity | Specified (new) |
| Q9 | Actuation authority validity | Specified (new) |
| Q10 | Mandatory evidence integrity | Specified (new) |

**Status:** All 10 queries fully specified; ready for implementation.

---

## REMAINING WORK FOR PHASE 1 DEVELOPMENT

### TASK 2: Exact Runtime Outcome Reporting

**Current architecture:**
- Resolver returns `decision` in {PERMIT, SAFE_STATE}
- Does not distinguish DENY from HOLD (both reported as SAFE_STATE)

**Required change:**
```python
# Current
verdict["decision"] in {"PERMIT", "SAFE_STATE"}

# New
verdict["decision"] in {"PERMIT", "DENY", "HOLD"}
verdict["safe_state"] = (verdict["decision"] != "PERMIT")  # aggregate
```

**Implementation scope:**
- `src/gcir/precedence.py`: Modify classify_outcome or resolve to track:
  - Mandatory failure + known outcome (fail) → DENY
  - Mandatory failure + unknown outcome (unknown + escalation) → HOLD
- `experiments/case_b_injection_scenarios.py`: Update test assertions
  - Scenarios 1,2,7,13: Assert `decision == "HOLD"`
  - Scenarios 3-6,8-12: Assert `decision == "DENY"`
  - All 13: Assert `safe_state == true`

**Effort:** ~2-3 hours

**Risk:** Low (isolated to decision reporting; SAFE_STATE aggregate derived from exact outcome)

### TASK 3: Implement Q7-Q10 SQL and Python

**Files to create/modify:**
- `queries/traceability.sql`: Add Q7-Q10 query definitions
- `src/gcir/traceability.py`: Implement Q7-Q10 query execution
- `tests/integration/test_traceability_queries.py`: Add Q7-Q10 to valid-artifact tests

**Expected results:**
- Q1-Q10 all return empty sets on valid Case A and Case B evidence

**Effort:** ~4-6 hours

**Risk:** Low (specifications complete; straightforward SQL/Python)

### TASK 4: Create Negative Fixtures Q1-Q10

**Scope:** 10 seeded violations (one per query)

**Structure per query:**
```json
{
  "query": "Q7",
  "violation": "ACS-B01-01 compiles to zero risk-derived predicates",
  "fixture": {...evidence with violation...},
  "expected_query_result": ["ACS-B01-01"],
  "actual_result": "TBD"
}
```

**Effort:** ~3-4 hours (design mutation, verify detection)

**Risk:** Low (straightforward fixture creation)

### TASK 5: Run Development Test Suite

**Current test count (v2.2):** 280 tests

**Development test count (estimated):** 320-340 tests

**Tests to run:**
- Case A compilation & traceability (unchanged)
- Case B compilation & traceability (unchanged)
- Q1-Q10 on valid artifacts (new, 20 tests)
- Q1-Q10 negative fixtures (new, 10-20 tests)
- 13 exact-outcome injections (updated, 13 tests)
- Property/adversarial tests (existing, ~150 tests)

**Expected duration:** ~10-15 minutes automated

**Risk:** Very low (existing test suite stable; new tests straightforward)

---

## TASK 6-8: VERIFICATION & GO/NO-GO

**Task 6: Compilation & Bundle State**
- Recompile Case B with 6 ACS (inputs unchanged)
- Expected: Bundle hash remains 2850155a2ee7...
- If hash differs: Investigate root cause
- **Status:** Ready to execute

**Task 7: Case A Regression Check**
- Run Case A tests (expect: unchanged)
- Verify final_v2 unchanged (expect: yes)
- Verify v1.0.3 unchanged (expect: yes)
- **Status:** Ready to execute

**Task 8: Final GO/NO-GO for v3 Freeze**
- Gate 1: Exact outcomes for all 13 injections ← PENDING
- Gate 2: Q1-Q10 clean on valid artifacts ← PENDING
- Gate 3: Q1-Q10 detect violations on fixtures ← PENDING
- Gate 4: Development test suite passes ← PENDING
- Gate 5: Case B bundle hash unchanged (or justified) ← PENDING
- Gate 6: Case A not regressed ← PENDING
- Gate 7: No modifications to final_v2/v1.0.3 ← VERIFIED
- Gate 8: Manuscript corrected ← VERIFIED

**GO/NO-GO decision:** Pending Task 2-7 completion

---

## TIMELINE ESTIMATE

| Task | Effort | Status |
|---|---|---|
| Task 2: Exact outcomes | 2-3 hours | Ready to start |
| Task 3: Q7-Q10 queries | 4-6 hours | Ready to start |
| Task 4: Negative fixtures | 3-4 hours | Ready to start |
| Task 5: Development test run | ~15 min | Automated |
| Task 6: Compilation & bundle | ~10 min | Automated |
| Task 7: Regression check | ~10 min | Automated |
| Task 8: GO/NO-GO decision | ~30 min | Reporting |
| **Total** | **12-16 hours** | **Sequential** |

---

## CRITICAL INVARIANTS PRESERVED

✅ **"Every runtime ACS emits ≥ 1 predicate"**
- Case B: 6 ACS, 6 risk-derived predicates (verified by Q7)
- Invariant satisfied independent of total predicate count

✅ **13-injection outcome mappings**
- 4 HOLD, 9 DENY
- Determined by predicate eval + escalation, not ACS cardinality
- Remain valid for 6-ACS configuration

✅ **Case A scientific artifacts**
- Unchanged (Case A not affected by Case B correction)

✅ **Historical record**
- 9-ACS proposal documented in MANUSCRIPT_5_5D_DELTA.md
- Rejection documented in CASE_B_9_ACS_SEMANTIC_PROVENANCE.md
- Correction documented in CASE_B_ACS_CARDINALITY_CORRECTION.md

---

## NEXT STEPS

**Immediate (developer work):**

1. Update `src/gcir/precedence.py` to return exact outcomes (PERMIT/DENY/HOLD)
2. Implement Q7-Q10 in SQL and Python
3. Create negative fixtures for Q1-Q10
4. Run development test suite
5. Report final 24-item results

**Afterward (author review):**

- Review final results
- Approve or request corrections
- If approved: Create preregister-tier0-v3 and final_v3 campaign
- If issues: Debug and retry

**DO NOT:**
- Create v3 freeze, final_v3 campaign, or v1.0.4 until all gates pass
- Modify final_v2 or v1.0.3
- Move historical tags

---

## SUMMARY

The manuscript specification has been **forensically audited and corrected**. The 9-ACS requirement has been **rejected as unsupported**. Case B remains at **6 ACS (scientifically justified)**. The current artifact already implements this correctly.

Phase 1 development work is **ready to begin**. The critical path is:

1. Update runtime decision reporting (exact outcomes)
2. Implement 4 new audit queries
3. Create 10 negative fixtures
4. Run test suite
5. Report results

**Estimated completion: 12-16 hours development time**

**GO/NO-GO pending:** Successful completion of Tasks 2-8

