# PHASE_1_GO_NO_GO_FINAL.md

**⚠️ STATUS UPDATE (2026-09-10)**

This document recommended **NO-GO** for Phase 1 with the unsupported 9-ACS specification. **The author has accepted this finding and approved proceeding with the scientifically justified 6-ACS configuration.**

**Current status:** Phase 1 development proceeds with 6 ACS per the forensic audit. See `CASE_B_ACS_CARDINALITY_CORRECTION.md` for corrected specification.

---

**Decision:** **NO-GO FOR PHASE 1 DEVELOPMENT WITH 9-ACS GOAL** (Document created during audit; subsequently author-approved for 6-ACS proceeding)

**Date:** 2026-09-10

**Authority:** User directive from prior session:

> "If genuine semantic provenance cannot support all nine: STOP. Report a manuscript specification defect. Do not implement Phase 1 yet."

---

## EXECUTIVE DECISION

### Phase 1 cannot proceed as planned because the 9-ACS requirement lacks manuscript semantic justification.

**Blocking issue:** The specification to expand Case B from 6 to 9 Approved Control Specifications (distributed 3/2/1/1/1/1) cannot be grounded in the manuscript.

---

## FINDINGS SUMMARY

### ✅ COMPLETE AND VERIFIED

1. **13-scenario injection audit** — 4 HOLD, 9 DENY, all outcomes mapped
   - Escalation paths verified in results/final_v2/case_b/escalation_map.json
   - All target predicates are mandatory/decisive with on_unknown=fail
   - Outcome classification is deterministic and evidenced

2. **Outcome state machine** — PERMIT/DENY/HOLD/REJECT states defined
   - All 13 scenarios occur at runtime evaluation stage
   - SAFE_STATE is derived (¬PERMIT)
   - Externalization = false for all

3. **Code/spec delta** — Identified
   - Current: verdict["decision"] == "SAFE_STATE" (conflates DENY and HOLD)
   - New: verdict["decision"] ∈ {PERMIT, DENY, HOLD}

4. **Q7-Q10 audit queries** — Specifications complete
   - Q7: Runtime ACS with zero emitted predicates
   - Q8: Gate/predicate reference integrity
   - Q9: Actuation authority validity
   - Q10: Mandatory predicate evidence integrity

---

### ⛔ BLOCKING ISSUE: 9-ACS SPECIFICATION

**Finding:** The 9-ACS requirement cannot be justified from manuscript semantic provenance.

**Evidence:**

1. **Manuscript basis:** PAPER_REQUIREMENTS.md (official manuscript extraction) Section 10 states:
   > "**6 register rows, all runtime, all mandatory**"

2. **Semantic analysis:** Risk-by-risk forensic decomposition yields exactly 6 control requirements:
   - B-01: 1 requirement (permit validity, though could split to 2 with author clarification)
   - B-02: 1 requirement (single threshold)
   - B-03: 1 requirement (single velocity bound)
   - B-04: 1 requirement (single screening check)
   - B-05: 1 requirement (joint idempotency, could split to 2 with author clarification)
   - B-06: 1 requirement (single temporal ordering)
   - **Total: 6 distinct requirements**

3. **9-ACS distribution unjustified:**
   - No manuscript text justifies splitting B-01 into 3 ACS
   - No manuscript text justifies splitting B-02 into 2 ACS
   - The 3/2/1/1/1/1 distribution is an author-directed design goal without manuscript basis

4. **Provenance of 9-ACS:** Type C source (author-designed without explicit manuscript basis)
   - Not A (explicitly enumerated in manuscript)
   - Not B (unambiguously derived from distinct manuscript control requirements)
   - Functionally D (unsupported without author manuscript amendment)

---

## DETAILED FINDINGS

### Semantically Justified ACS Cardinality

**Risk-by-risk verdict:**

| Risk | Control requirement | ACS count | Justification |
|---|---|---|---|
| B-01 | Payment release without valid permit | 1 | Joint observable; no split mandate in manuscript |
| B-02 | Amount > per-transaction limit | 1 | Single scalar threshold |
| B-03 | Txn count/window > bound | 1 | Indivisible velocity bound |
| B-04 | Counterparty ∈ restricted list | 1 | Single deterministic check |
| B-05 | Permit reuse or duplicate hash | 1 | Joint idempotency (could be 2 with clarification) |
| B-06 | Receipt not committed between auth and actuation | 1 | Atomic temporal ordering |
| **Total** | | **6** | **Scientifically justified** |

**Possible defensible expansion:** 7 ACS (if B-05 is split and B-01 remains 1). Cannot reach 9 without inventing controls.

---

### 13-Injection Scenario Verification ✅

**Status:** COMPLETE AND VERIFIED

**All 13 scenarios audit successfully:**
- 4 scenarios → **HOLD** (unknown evidence + escalation path)
- 9 scenarios → **DENY** (known policy violation)
- 0 scenarios → REJECT_AT_COMPILATION (none)
- 0 scenarios → REJECT_AT_ISSUANCE (none)

**Verification:**
- Injection stage: All occur at **runtime predicate evaluation** (after compilation and issuance)
- Escalation routes: All verified from results/final_v2/case_b/escalation_map.json
- Gate semantics: All targets are mandatory/decisive with on_unknown=fail
- Outcome determinism: DENY = outcome is "fail"; HOLD = outcome is "unknown" + escalation exists

**Conclusion:** 13-injection outcomes are **independent of ACS cardinality**. They map to predicates, not ACS records. The outcomes remain valid whether Case B has 6, 7, or 9 ACS.

---

### Q7-Q10 Audit Query Specifications ✅

**Status:** COMPLETE

**All 10 queries are scientifically justified:**

| Query | Justification | Independent of ACS cardinality? |
|---|---|---|
| Q1-Q6 | Temporal traceability (existing) | YES |
| Q7 | Every runtime ACS emits ≥1 predicate | YES (applies to any ACS count) |
| Q8 | Gate/predicate closure | YES |
| Q9 | Actuation authority validity | YES |
| Q10 | Mandatory predicate evidence integrity | YES |

**Conclusion:** All 10 queries remain valid regardless of final ACS cardinality.

---

### Code/Spec Delta ✅

**Status:** IDENTIFIED

**Required code changes:**

1. `src/gcir/precedence.py` (resolver)
   - Current: returns SAFE_STATE aggregate
   - New: returns exact enum {PERMIT, DENY, HOLD, ...}

2. `experiments/case_b_injection_scenarios.py` (test harness)
   - Current: assert verdict["decision"] == "SAFE_STATE"
   - New: assert verdict["decision"] in {specific_outcome_per_scenario}

3. Test suite updates
   - Verify exact outcomes (not aggregate)
   - Verify externalization=false

**Conclusion:** Code changes are scoped and feasible. They do **not depend on ACS cardinality**.

---

## DECISION FRAMEWORK

### User's Original Criteria

The user explicitly stated:

> "There are only two acceptable outcomes:
> A. The existing Case B semantics genuinely contain nine independently enforceable control requirements.
> B. They do not.
> Do not manufacture a third option."

**Applying the criterion:**

**Result: B is true.** Case B does **not** contain nine independently enforceable control requirements.

The 6-risk structure, as stated in the manuscript, yields 6 semantically distinct control requirements.

---

## BLOCKING DECISION

**Per user directive:**

> "If genuine semantic provenance cannot support all nine: STOP. Report a manuscript specification defect."

**Applied:**

**Genuine semantic provenance does NOT exist.** No manuscript text explicitly enumerates 9 control requirements or justifies the 3/2/1/1/1/1 distribution.

**Specification defect:** The planning document (MANUSCRIPT_5_5D_DELTA.md) asserts the 9-ACS requirement as "Normative from 5.5d" without citing a manuscript section, page number, or quotation. The authoritative manuscript extraction (PAPER_REQUIREMENTS.md Section 10) contradicts this, stating "6 register rows."

---

## PHASE 1 DECISION

### GO / NO-GO: **NO-GO**

**Reason:** The 9-ACS specification cannot proceed because it lacks genuine manuscript semantic basis.

**Blocked work:**
- Case B ACS expansion from 6 to 9 ✗
- Judgment record update to include 9 ACS ✗
- Case B compiler modifications for N:1 ACS:risk mapping ✗
- Final_v3 campaign with 9-ACS configuration ✗
- Scientific freeze (preregister-tier0-v3) with 9 ACS ✗
- Release of v1.0.4 with 9-ACS Case B ✗

**Unblocked work (can proceed independently):**
- 13-injection outcome mappings ✓ (predicate-based, not ACS-based)
- Q7-Q10 query specifications ✓ (valid for any ACS cardinality)
- Negative fixture design ✓ (applies to both 6 and 9 ACS scenarios)
- Code/spec alignment (DENY/HOLD vs. SAFE_STATE) ✓ (applies to both)

---

## REQUIRED ACTION

The blocking issue must be resolved by one of the following:

### **Option A: Author provides manuscript justification**

Author must provide explicit text from the 5.5d manuscript that:
- Enumerates 3 distinct control requirements for B-01, with separate observables, evidence requirements, or decision consequences
- Enumerates 2 distinct control requirements for B-02, with separate observables, evidence requirements, or decision consequences
- Cites section and page numbers
- Explains why these are separate ACS rather than joint controls

**If Option A is fulfilled:** Re-evaluate and potentially approve Phase 1 with 9-ACS configuration.

### **Option B: Accept scientifically justified 6-ACS configuration**

Proceed with Phase 1 using the manuscript-grounded 6-ACS configuration:
- B-01: 1 ACS (permit validity)
- B-02: 1 ACS (amount limit)
- B-03: 1 ACS (velocity bound)
- B-04: 1 ACS (restricted-party screening)
- B-05: 1 ACS (permit single-use + hash novelty)
- B-06: 1 ACS (receipt temporal ordering)
- **Total: 6 ACS**

All other Phase 1 work remains unchanged:
- 13-injection outcomes (4 HOLD, 9 DENY)
- 10 audit queries (Q1-Q10)
- Code modifications (PERMIT/DENY/HOLD)
- Final campaign and freeze

**Advantages:**
- Semantically sound
- Manuscript-aligned
- No invented controls
- Can proceed immediately

**Timeline:** Phase 1 implementation can begin immediately.

### **Option C: Defer Phase 1 pending manuscript amendment**

Request that the 5.5d manuscript be formally amended to explicitly justify 9 ACS (or explicitly retain 6). Do not proceed with Phase 1 until the manuscript is updated and frozen.

**Timeline:** Dependent on manuscript amendment cycle.

---

## INVARIANTS PRESERVED

Regardless of ACS cardinality (6, 7, or 9), the following remain valid:

✅ **"Every runtime ACS emits ≥1 predicate"** (verified by Q7)

✅ **13-injection outcomes** (4 HOLD, 9 DENY) — mapped to predicates, not ACS

✅ **10 audit queries** — valid for any ACS count

✅ **Code/spec alignment** — PERMIT/DENY/HOLD vs. SAFE_STATE

✅ **Outcome state machine** — compilation → issuance → runtime → decision

---

## FINAL STATEMENT

**The audit confirms that Case B contains 6 semantically distinct, manuscript-supported control requirements. The 9-ACS expansion cannot be justified without explicit manuscript basis. Phase 1 cannot proceed to implementation unless the blocking specification defect is resolved.**

**Recommendation: Accept the 6-ACS configuration as the scientifically justified baseline and proceed with Phase 1 immediately, or require author to provide manuscript text justifying 9 ACS before implementation begins.**

