# MANUSCRIPT_UPDATE_STATUS.md

**Status:** AMENDMENT SPECIFICATION COMPLETE — Awaiting integration

**Date:** 2026-09-10

---

## MANUSCRIPT AMENDMENT PREPARATION COMPLETE

The four required amendments to create manuscript version 5.5e have been fully specified in:

**`paper_update/MANUSCRIPT_AMENDMENT_5_5E.md`**

---

## FOUR AMENDMENTS REQUIRED

### Amendment 1: Q7-Q10 Audit Query Definitions
**Location:** Section VIII, after Q1-Q6 definitions  
**Content:** Complete normative definitions of Q7 (ACS compilation coverage), Q8 (gate/predicate closure), Q9 (authority validity), Q10 (evidence integrity)  
**Status:** ✅ Specified in amendment document

### Amendment 2: ACS vs. Predicate Cardinality Distinction
**Location:** Section VI, new subsection B.1  
**Content:** Explicit statement that ACS count ≠ total predicate count; normative requirement that every runtime ACS emits ≥1 predicate  
**Status:** ✅ Specified in amendment document

### Amendment 3: Exact Runtime Outcome Semantics
**Location:** Section VI, new subsection D.1  
**Content:** PERMIT, DENY, HOLD definitions with distinction from compilation/issuance rejections  
**Status:** ✅ Specified in amendment document

### Amendment 4: SAFE_STATE Clarification
**Location:** Section VIII, after Q7-Q10 text  
**Content:** SAFE_STATE as aggregate non-externalization property, distinct from exact outcomes  
**Status:** ✅ Specified in amendment document

---

## HOW TO PROCEED

### Step 1: Integrate Amendments into DOCX

Open: `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx`

For each amendment in `MANUSCRIPT_AMENDMENT_5_5E.md`:
1. Navigate to specified section
2. Position cursor at indicated location
3. Insert the provided text
4. Match formatting to surrounding content

### Step 2: Apply Consistency Corrections

Search manuscript for these phrases and remove/correct:
- "9 Approved Control Specifications" → Delete
- "B-01: 3 ACS" → Delete
- "B-02: 2 ACS" → Delete
- "P_B_risk >= 9" → Change to "P_B_risk >= 6"
- "six audit queries" → Change to "ten audit queries"

### Step 3: Save as New Revision

Save the updated manuscript as:
```
From_Risk_Register_to_Runtime_Predicate_5_5e.docx
```

**Do NOT overwrite the IEEE submission version (5.5d).**

### Step 4: Confirm Integration

Record:
- File path
- SHA-256 of new file
- Integration completion date

---

## VERIFICATION CHECKLIST

Once manuscript is updated, verify:
- [ ] Section VIII contains Q1-Q10 (6 temporal + 4 structural queries)
- [ ] Section VI explicitly discusses ACS vs. predicate cardinality
- [ ] Section VI defines PERMIT, DENY, HOLD exactly
- [ ] Section VIII clarifies SAFE_STATE as derived aggregate
- [ ] No normative "9 ACS" statement remains
- [ ] No normative "P_B_risk >= 9" statement remains
- [ ] Section X (Case B) correctly states "6 ACS"
- [ ] All formatting is preserved
- [ ] No substantive 5.5d text was removed unintentionally

---

## NEXT STEP

Once manuscript 5.5e is created:

1. **Update gate verification:** `paper_update/MANUSCRIPT_SPECIFICATION_GATE_V3.md`
2. **Mark all 7 items as PASS**
3. **Immediately proceed to Phase 1 Development** — no further questions

Phase 1 includes:
- Exact runtime outcome implementation (PERMIT/DENY/HOLD)
- Q7-Q10 audit query implementation
- Negative fixture creation (Q1-Q10)
- 13-injection revalidation
- Full development test suite

---

## SUPPORTING DOCUMENTS

All manuscript amendment content has been extracted and is ready for use:

- ✅ `MANUSCRIPT_AMENDMENT_5_5E.md` — Detailed amendment specifications
- ✅ `MANUSCRIPT_SPECIFICATION_GATE_V3.md` — Gate verification
- ✅ `CASE_B_ACS_CARDINALITY_CORRECTION.md` — Detailed justification
- ✅ `CORRECTED_Q7_Q10_SPECIFICATION_5_5D.md` — Q7-Q10 full specs
- ✅ `CASE_B_13_INJECTION_STAGE_AUDIT_V3.md` — 13-outcome mapping
- ✅ All supporting forensic audit documents

---

## READY FOR PHASE 1

Once the manuscript gate passes 7/7, Phase 1 development is **completely ready**:

- ✅ Specification decisions finalized
- ✅ Amendment specifications complete
- ✅ Development tasks detailed
- ✅ Runtime outcome migration planned
- ✅ Q7-Q10 implementations specified
- ✅ 13-injection outcomes verified
- ✅ Testing strategy documented
- ✅ Result tracking structure planned

**Zero additional planning required.**

**Proceed immediately to code implementation upon gate = 7/7 PASS.**

---

## AWAITING CONFIRMATION

**Status:** Waiting for confirmation that manuscript 5.5e has been created and integrated.

**When ready:** Reply with:
1. Confirmation that 5.5e is created
2. File path of new manuscript
3. SHA-256 of new manuscript (optional but recommended)

**Then:** Update `MANUSCRIPT_SPECIFICATION_GATE_V3.md` to 7/7 PASS

**Then:** Begin Phase 1 Development immediately

