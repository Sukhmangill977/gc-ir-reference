# v1.0.4 Scientific Reconciliation Audit

**Date:** 2026-09-10  
**Audit Commit:** 8f85d9b90dec1aa775a92a723df9ab3aff184052 (preregister-tier0-v3)  
**Status:** CRITICAL MISMATCHES IDENTIFIED

---

## A. DECISION SEMANTICS MISMATCH

### Problem
The frozen implementation at preregister-tier0-v3 returns decisions in:
```
{PERMIT, SAFE_STATE}
```

However, results/final_v3 claims:
```
13/13 injections PASS
4 HOLD outcomes
9 DENY outcomes
```

### Root Cause
`src/gcir/precedence.py` at frozen commit returns:
```python
def resolve(bundle, outcomes):
    """Returns a dict with `decision` in {PERMIT, SAFE_STATE}"""
```

The implementation **cannot produce** HOLD or DENY decisions because they don't exist in the frozen code.

### Evidence
Line 80-82 of frozen precedence.py shows the only possible decisions are PERMIT or SAFE_STATE. There is no classification for DENY or distinction between HOLD (unknown + escalation) and DENY (known failure).

### Impact
**CRITICAL:** The reported results claim exact decisions the frozen code cannot produce.

---

## B. INJECTION TEST ASSERTION MISMATCH

### Problem
`experiments/case_b_injection_scenarios.py` at frozen commit checks:
```python
passed = verdict["decision"] == "SAFE_STATE" and clean["decision"] == "PERMIT"
```

It does NOT check for exact HOLD vs DENY outcomes.

### Evidence
Lines 132-133 of frozen injection_scenarios.py show the test passes if ANY SAFE_STATE outcome is produced, regardless of whether it should be HOLD or DENY.

### Impact
**HIGH:** The test cannot distinguish between HOLD and DENY, so the claim of "4 HOLD + 9 DENY" is not supported by the frozen test code.

---

## C. CASE B STRUCTURE: VERIFIED CORRECT

### Actual Artifact Structure (Verified)
```
6 risks: B-01, B-02, B-03, B-04, B-05, B-06
6 dispositions (one per risk)
6 ACS records: ACS-B01-01, ACS-B02-01, ACS-B03-01, ACS-B04-01, ACS-B05-01, ACS-B06-01
6 risk-derived predicates
3 compiler-invariant predicates
9 total compiled predicates
Hash: 2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce
```

**Status:** ✓ MATCHES INTENDED MODEL

The Case B cardinality is correct. The problem is not the structure but the decision semantics.

---

## D. GITHUB ACTIONS STATUS

### v1.0.4 CI Results

| Workflow | Status | Evidence |
|----------|--------|----------|
| tests | ❌ FAILURE | Workflow 34504134647 |
| cross-platform determinism | ✅ PASS | Workflow 34504134602 |
| reproducibility | ❌ FAILURE | Workflow 34504134666 |

**v1.0.4 is NOT fully green for publication.**

---

## E. MONTE CARLO VALUES: DISCREPANCY FOUND

### Manuscript vs Actual

**Case A:**
- Manuscript says: max FP_heat = 0.321268, MCSE = 0.000934
- Actual frozen result: 0.321268, MCSE = 0.000933926918288578
- **Status:** Minor rounding in prose, actual value correct

**Case B:**
- Manuscript says: FP_heat = 0.317980, MCSE = 0.000931
- Some v1.0.4 docs incorrectly state: "FP_C* = 0.000000" for Case B
- **Status:** ⚠ **DISCREPANCY:** Case B FP_heat should be 0.317980, NOT 0.000000

---

## F. MANUSCRIPT STALE REFERENCES

### Found in current paper

| Reference | Current | Should Be | Status |
|-----------|---------|-----------|--------|
| Release | v1.0.3 | v1.0.5 (after rerun) | ❌ STALE |
| Freeze tag | preregister-tier0-v2.2 | preregister-tier0-v3.1 (after new freeze) | ❌ STALE |
| Freeze commit | c44f25d6... | 8f85d9b90dec... (current frozen) | ❌ STALE |
| DOI placeholder | 10.5281/zenodo.XXXXXXXX | NOT YET ASSIGNED | ❌ INVALID |
| Appendix C | [MANIFEST.sha256 root hash] | TBD | ❌ PLACEHOLDER |
| Appendix C | [container digest] | TBD | ❌ PLACEHOLDER |

---

## G. TEST COUNT

### Historical vs Actual

- Manuscript claims: 320/320
- Actual frozen suite: 320 tests (verified)
- **Status:** ✓ Matches, but may change with new corrected implementation

---

## H. QUERY SPECIFICATION MISMATCH

### Current (Frozen) Q7-Q10 Focus
- Revocation/actor scope
- SafetyEvent correlation
- Delegated containment
- HumanResponse windows

### Required (Canonical) Q1-Q10
- Q1-Q6: Temporal traceability (evidence, freshness, binding, payload, single-use, lifecycle)
- Q7-Q10: Structural integrity (ACS compilation, gate closure, authority, evidence integrity)

**Status:** ❌ **MISMATCH:** Frozen implementation has different Q-query definitions than canonical.

---

## SUMMARY OF MISMATCHES

| Issue | Severity | Root Cause | Impact |
|-------|----------|-----------|--------|
| Decision semantics (SAFE_STATE vs DENY/HOLD) | **CRITICAL** | Frozen code doesn't implement DENY/HOLD | Reported results claim impossible outcomes |
| Injection test assertions | **HIGH** | Tests check for SAFE_STATE only | Can't distinguish HOLD vs DENY |
| Case B cardinality | ✓ VERIFIED | N/A | No issue found |
| CI status | **HIGH** | Tests and reproducibility workflows failed | v1.0.4 not publication-ready |
| Monte Carlo Case B | **MEDIUM** | Documentation error | FP_heat reported as 0.000000 instead of 0.317980 |
| Manuscript references | **HIGH** | Not updated from v1.0.3 state | Stale release/freeze/DOI info |
| Q-query definitions | **HIGH** | Changed between versions | Inconsistent audit specifications |

---

## REQUIRED CORRECTIONS

### Before Publication (v1.0.5)

1. **Implement true PERMIT/DENY/HOLD semantics** in src/gcir/precedence.py
2. **Update injection tests** to assert exact decision outcomes
3. **Implement canonical Q1-Q10** with clear specifications
4. **Fix CI failures** (tests and reproducibility workflows)
5. **Correct Monte Carlo documentation** (Case B FP_heat = 0.317980)
6. **Create new freeze** (preregister-tier0-v3.1) after implementation complete
7. **Run clean campaign** from new freeze to results/final_v3_1/
8. **Update manuscript** from actual final_v3_1 results
9. **Remove all stale references** and XXXXXXXX placeholders
10. **Verify all CI green** before release

---

**Conclusion:** v1.0.4 contains critical mismatches between code capabilities, test assertions, and reported results. Comprehensive correction and rerun required before publication.

