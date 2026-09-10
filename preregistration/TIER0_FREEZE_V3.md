# Tier 0 Freeze V3 - GC-IR Phase 1 Development

**Freeze Date:** 2026-09-10  
**Freeze Tag:** preregister-tier0-v3  
**Authority:** Phase 1 Development Gate - 7/7 PASS

---

## FREEZE SCOPE

This freeze captures the complete scientific and technical state of Phase 1 Development:

### Code and Specification
- ✓ `src/` - GC-IR compiler, precedence resolver (PERMIT/DENY/HOLD)
- ✓ `experiments/` - Case B injection scenarios (13 exact outcomes)
- ✓ `schemas/` - All JSON schemas (v1.0)
- ✓ `cases/` - Case A (19 predicates) and Case B (6 ACS, 9 predicates)
- ✓ `catalog/` - Control derivation catalogs
- ✓ `invariants/` - Compiler invariants (3 for Case B)
- ✓ `queries/` - Q1-Q10 audit queries (temporal + structural)
- ✓ `keys/` - Cryptographic keyring
- ✓ `tests/` - 320-test suite (0 failures)

### Development Artifacts
- ✓ `results/development_v3/` - Phase 1 test results
- ✓ `paper_update/` - Manuscript 5.5e with 4 approved amendments
- ✓ `docs/` - Complete specification and audit documentation
- ✓ `preregistration/` - This freeze documentation

### Dependencies
- ✓ `environment.yml` - Python environment
- ✓ `pyproject.toml` - Project configuration
- ✓ `Makefile` - Build and test automation

### Test and Verification State
- ✓ Q1-Q10 definitions: Complete (20/20 PASS across both cases)
- ✓ Negative fixtures: 10/10 created and violation detection verified
- ✓ 13 exact-outcome expectations: 4 HOLD + 9 DENY (100%)
- ✓ Monte Carlo seed: Author-specified, fixed
- ✓ Determinism matrix: 62/62 runs baseline established
- ✓ Case A: 19 predicates, no regression
- ✓ Case B: 6 ACS compiled to 9 predicates (6 risk-derived + 3 invariant)

---

## CRITICAL METRICS AT FREEZE

| Metric | Value | Evidence |
|--------|-------|----------|
| **Manuscript Gate** | 7/7 PASS | 5.5e with 4 approved amendments |
| **Case A Compilation** | ✓ SUCCESS | f5cbc3a8... (19 predicates) |
| **Case B Compilation** | ✓ SUCCESS | 2850155a... (9 predicates, 6 ACS) |
| **Q1-Q10 Case A** | 10/10 PASS | Temporal + structural complete |
| **Q1-Q10 Case B** | 10/10 PASS | Temporal + structural complete |
| **Negative Fixtures** | 10/10 detected | All violation patterns confirmed |
| **13-Injections** | 13/13 PASS | 4 HOLD + 9 DENY + externalization=false |
| **Test Suite** | 320/320 PASS | 0 failures, 0 skipped |
| **PERMIT/DENY/HOLD** | Implemented | Exact outcome resolver active |
| **SAFE_STATE Aggregate** | Implemented | Derived from (decision ≠ PERMIT) |

---

## FROZEN DOCUMENTATION

### Specification Documents
- `docs/PHASE_1_DEVELOPMENT_PLAN.md` - 14 development tasks
- `docs/RUNTIME_OUTCOME_MIGRATION_V3.md` - PERMIT/DENY/HOLD migration
- `docs/CASE_B_ACS_CARDINALITY_CORRECTION.md` - 6 ACS justification
- `docs/CORRECTED_Q7_Q10_SPECIFICATION_5_5D.md` - Q7-Q10 formal specs
- `docs/CASE_B_13_INJECTION_STAGE_AUDIT_V3.md` - 13 outcome mapping

### Test and Audit Documents
- `results/development_v3/PHASE1_FINAL_REPORT.md` - Comprehensive Phase 1 report
- `results/development_v3/phase1_results.json` - All test execution results
- `paper_update/MANUSCRIPT_AMENDMENT_5_5E.md` - 4 amendments applied

### Configuration
- `preregistration/` - Preregistration directory structure
- `pyproject.toml` - Exact dependencies pinned
- `environment.yml` - Exact Python environment

---

## INVARIANTS ESTABLISHED AT FREEZE

1. **Case A Scientific Baseline**
   - 16 register rows (risks)
   - 19 compiled predicates (6 C* mandatory + 13 supporting/advisory)
   - DC = 1.0 (release admissible)
   - All 16 risks have ACS

2. **Case B Forensic Reconstruction**
   - 6 register rows (risks)
   - 6 Approved Control Specifications (ACS-B01-01 through ACS-B06-01)
   - 9 compiled predicates (6 risk-derived + 3 compiler-invariant)
   - Bundle hash: 2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce
   - All 6 risks have runtime ACS

3. **Determinism**
   - TD = 1.0 (62/62 runs identical)
   - No nondeterminism sources active
   - Iteration order closed via canonical_order
   - Time independence verified

4. **Monte Carlo**
   - Seed: Author-specified (fixed)
   - Distributions: Not varied at freeze
   - Sample size: Per-case specification

5. **Compiler Invariants (Φ)**
   - Q7: Every runtime ACS → ≥1 risk-derived predicate
   - Q8: Every gate-map entry → valid predicate; every decisive predicate → gate-map
   - Q9: All evidence producers → authority matrix
   - Q10: All decisive gates → fail-closed (on_unknown=fail)

---

## WHAT THIS FREEZE EXCLUDES

❌ **NOT FROZEN:**
- `results/final_v3/` (to be created by reportable campaign)
- `results/final_v3_docker/` (to be created by Docker reproduction)
- `paper_v1.0.4` (pending freeze validation)
- `preregister-tier0-v3-results.md` (to be created post-campaign)

✓ **PRESERVED UNCHANGED:**
- `results/final_v2/` (Phase 0 production)
- `results/preregister-tier0-v2.2/` (previous freeze)
- `results/final/` (v1.0.1 baseline)

---

## REPRODUCTION PROTOCOL

From this exact freeze commit, the reportable campaign will execute:

1. **Compilation**
   - Case A: expect f5cbc3a8...
   - Case B: expect 2850155a...

2. **Audit Queries**
   - Q1-Q10 on both cases: expect 20/20 PASS

3. **Negative Controls**
   - 10 fixtures: expect 10/10 violations detected

4. **Exact Outcomes**
   - 13 injections: expect 13/13 PASS
   - HOLD families (4): missing_predicate, corrupted_input, network_partition_or_delay, session_intent_compromise
   - DENY families (9): toctou, replay_attack, payload_mutation, concurrency_conflict, adaptive_attacker, identity_provenance_deception, runtime_infrastructure_drift, economic_logic_fragility, cross_entity_fraud_propagation

5. **Test Suite**
   - Full suite: expect 320/320 PASS

6. **Determinism**
   - 62 runs: expect TD=1.0

7. **Monte Carlo**
   - Author distributions: baseline only

8. **Cross-platform**
   - macOS (this platform): baseline
   - Linux (CI): regression check
   - Windows (if available): regression check

9. **Docker**
   - Official image: exact reproduction

10. **Manuscript Verification**
    - paper_verifier: all Section XI quantities match

---

## FREEZE AUTHORITY

This freeze is authorized by successful completion of Phase 1 Development:

✓ Manuscript gate: 7/7 PASS (5.5e with amendments)
✓ Case B ACS cardinality: 6 (forensic audit accepted)
✓ Exact runtime outcomes: PERMIT/DENY/HOLD (implemented and tested)
✓ Q1-Q10 audit framework: Complete and verified (20/20 PASS)
✓ 13-injection scenarios: All passing with exact outcomes (13/13)
✓ Test suite: All passing (320/320)
✓ Negative fixtures: All violations detected (10/10)
✓ Historical state: Final_v2 and v2.2 preserved
✓ Manuscript amendments: All 4 applied and verified

---

## POST-FREEZE PROCESS

### Immediate (this session)
1. Tag commit as preregister-tier0-v3
2. Push tag to GitHub
3. Verify tag is public

### During Reportable Campaign (next session, from this commit)
1. Run full 320-test suite
2. Run Q1-Q10 (expect 20/20)
3. Run 13-injection scenarios (expect 13/13)
4. Run 10 negative controls (expect 10/10)
5. Run 62-run determinism (expect TD=1.0)
6. Run Monte Carlo
7. Run cross-platform verification
8. Run Docker reproduction
9. Run manuscript verifier
10. Run freeze check against this commit

### Post-Campaign
1. Report all results in final_v3 results.md
2. Prepare v1.0.4 for publication (if all checks pass)

---

**Freeze Status:** LOCKED  
**Next Step:** Public tag verification, then reportable campaign execution.

