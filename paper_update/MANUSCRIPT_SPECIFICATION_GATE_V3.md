# MANUSCRIPT_SPECIFICATION_GATE_V3.md

**Purpose:** Verify that the working manuscript contains the corrected Case B specification BEFORE Phase 1 development proceeds.

**Date:** 2026-09-10

**Status:** GATE VERIFICATION IN PROGRESS

---

## GATE REQUIREMENTS

Before Phase 1 implementation, the actual working manuscript revision must contain:

### 1. ✅ Corrected Case B ACS cardinality = 6

**Required text:** "Case B contains six semantically distinct Approved Control Specifications, one per risk."

**Source:** Should appear in manuscript Section X (Case B)

**Current status (PAPER_REQUIREMENTS.md):** "6 register rows, all runtime" ✓

**Gate status:** PASS (Section 10 of extracted requirements confirms 6 risks → 6 ACS)

---

### 2. ✅ Distinction: 6 ACS vs. risk-derived predicates vs. compiler-invariants

**Required text:** "The compiled Case B bundle contains risk-derived predicates (determined by Φ, ≥1 per ACS) and compiler-invariant predicates (mandatory gates over architecture), both counted separately. Total predicate count is determined at compilation."

**Source:** Should appear in Section X or Section VI (Compiler)

**Current status:** CASE_B_ACS_CARDINALITY_CORRECTION.md contains this; not yet in published manuscript

**Gate status:** PENDING (Must be added to working manuscript before freeze)

---

### 3. ✅ General requirement: every runtime ACS emits ≥ 1 risk-derived predicate

**Required text:** "Every approved runtime Approved Control Specification must compile to at least one risk-derived predicate. This requirement is independent of ACS cardinality in any particular case and is verified by audit query Q7."

**Source:** Should appear in Section V or VI (Normative requirements)

**Current status:** Implied in PAPER_REQUIREMENTS.md Section 4.4 ("predicate cardinality independent of risk cardinality")

**Gate status:** PASS (exists as principle; should be made more explicit in corrected manuscript)

---

### 4. ✅ Complete normative Q1-Q10 definitions

**Required text:** All 10 queries must be formally specified in the manuscript.

**Q1-Q6:** Temporal traceability (already in manuscript Section VIII)

**Q7-Q10:** Structural integrity (NEW; must be added)

| Query | Specification location |
|---|---|
| Q7 | Runtime ACS compilation coverage |
| Q8 | Gate/predicate reference integrity |
| Q9 | Actuation authority validity |
| Q10 | Mandatory evidence/fail-closed integrity |

**Current status:** CORRECTED_Q7_Q10_SPECIFICATION_5_5D.md complete; not yet integrated into published manuscript

**Gate status:** PENDING (Q7-Q10 must be formally added to manuscript Section VIII before freeze)

---

### 5. ✅ PERMIT / DENY / HOLD semantics defined

**Required text:** Exact definitions of three runtime decision outcomes:

- **PERMIT:** All required runtime conditions needed for permission are satisfied.
- **DENY:** At least one decisive/mandatory runtime condition is known false.
- **HOLD:** Permission cannot be established because required evidence is unknown/unavailable AND explicit escalation/hold mechanism exists.

**Current status:** CASE_B_13_INJECTION_STAGE_AUDIT_V3.md contains these; not yet in published manuscript

**Gate status:** PENDING (Must be added to manuscript Section VII or VIII before freeze)

---

### 6. ✅ SAFE_STATE defined only as aggregate non-externalization property

**Required text:** "SAFE_STATE is a derived aggregate property, not an exact runtime decision class. For the three runtime exact outcomes PERMIT, DENY, HOLD: safe_state = (exact_outcome != PERMIT). A runtime execution with DENY or HOLD both exhibit SAFE_STATE property (non-externalization)."

**Current status:** CASE_B_ACS_CARDINALITY_CORRECTION.md contains this; not yet in published manuscript

**Gate status:** PENDING (Must be clarified in manuscript Section VII before freeze)

---

### 7. ✅ No current normative 9-ACS statement

**Required text:** The manuscript must NOT contain normative text stating Case B has 9 ACS.

**Forbidden phrases:**
- "Case B contains 9 Approved Control Specifications"
- "B-01: 3 ACS"
- "B-02: 2 ACS"
- "P_B_risk >= 9"

**Current status:** PAPER_REQUIREMENTS.md Section 10 contains only "6 register rows" ✓

**Gate status:** PASS (No 9-ACS normative text in official manuscript extraction)

---

## MANUSCRIPT REVISION DECISION

### Current Status Summary

| Item | Status | Evidence |
|---|---|---|
| Case B cardinality = 6 | PASS | PAPER_REQUIREMENTS.md Section 10 |
| ACS vs. predicate distinction | PENDING | Documented in correction files; not in manuscript |
| Q1-Q10 definitions | PARTIAL | Q1-Q6 in manuscript; Q7-Q10 pending |
| PERMIT/DENY/HOLD semantics | PENDING | Documented in audit; not in manuscript |
| SAFE_STATE clarification | PENDING | Documented in correction; not in manuscript |
| No 9-ACS statement | PASS | Confirmed absent |
| Q7-Q10 new requirements | PENDING | Specified; not in manuscript |

**Overall gate status:** PENDING MANUSCRIPT AMENDMENT

---

## REQUIRED ACTION

The working manuscript must be updated to incorporate the corrections BEFORE Phase 1 implementation proceeds.

### Option A: Update Current 5.5d Manuscript

If the 5.5d manuscript is editable and the author intends to publish 5.5d with corrections:

1. Update Section X (Case B) with cardinality and predicate distinction text
2. Update Section VIII to add Q7-Q10 definitions
3. Add Section VII clarification: PERMIT/DENY/HOLD exact outcomes
4. Clarify SAFE_STATE as derived aggregate only
5. Verify no 9-ACS normative text remains
6. Re-hash and re-sign the manuscript
7. Update PAPER_REQUIREMENTS.md to reflect changes

### Option B: Create New 5.5e Manuscript Revision

If the author intends to preserve 5.5d as-is and create a new 5.5e revision:

1. Copy 5.5d to 5.5e
2. Apply corrections above
3. Update header to indicate version 5.5e
4. Create PAPER_REQUIREMENTS.md for 5.5e
5. Note in release notes that 5.5d had unsupported 9-ACS proposal; 5.5e corrects to 6 ACS

---

## GATE DECISION

**Gate requirement:** At least 5 items must PASS before Phase 1 implementation begins.

**Current PASS count:** 3/7

**Current PENDING count:** 4/7

**Gate status:** ⛔ **BLOCKED** until manuscript is updated

**Unblock action:** Update working manuscript with corrected Q7-Q10, PERMIT/DENY/HOLD, and ACS/predicate distinction text, then re-verify.

---

## PHASE 1 CANNOT PROCEED UNTIL

1. Working manuscript is updated with all 7 gate requirements
2. This gate document is updated to show all 7 items as PASS
3. Manuscript revision is identified (5.5d with corrections or new 5.5e)
4. Updated PAPER_REQUIREMENTS.md reflects manuscript changes

---

## NEXT STEP

**Author decision required:**

**Question:** Should Phase 1 wait for manuscript amendment, or should development proceed in parallel with manuscript drafting?

**Option 1:** Amend manuscript first (ensures manuscript accuracy), then develop

**Option 2:** Develop in parallel; manuscript catches up before preregister-tier0-v3 freeze

**Recommendation:** Option 1 (manuscript first) for scientific integrity, but author may choose Option 2 if timeline constraints allow parallel work.

---

## GATE RE-VERIFICATION POINT

Once manuscript is updated, re-run this gate verification and set all items to PASS before beginning Task 1 (exact runtime outcomes).

