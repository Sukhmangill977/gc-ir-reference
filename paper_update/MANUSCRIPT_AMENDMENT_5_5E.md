# MANUSCRIPT_AMENDMENT_5_5E.md

**Purpose:** Detailed amendment document for updating manuscript from 5.5d (IEEE submission) to 5.5e (corrected specification).

**Source manuscript:** `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx` (Sept 9, 2026)

**Output manuscript:** `From_Risk_Register_to_Runtime_Predicate_5_5e.docx`

**Status:** AMENDMENT SPECIFICATION — Ready for integration

---

## FOUR REQUIRED AMENDMENTS

### AMENDMENT 1: Expand Section VIII with Q7-Q10 Definitions

**Location:** Section VIII "TEMPORAL TRACEABILITY AND EVIDENCE BINDING" (approximately paragraph 198-219 in source)

**Current text ends with:**
> "lifecycle-registry records lacking a valid signing authority."
> 
> "Empty result sets demonstrate linkage and temporal-integrity completeness under the declared data model..."

**INSERT BEFORE "Empty result sets..." the following text:**

---

**The Structural Integrity Queries (Q7–Q10)** verify that the compiled artifact exhibits compilation completeness and reference closure required by the compiler design.

**Q7: Runtime ACS compilation coverage.** Every approved control specification d with disposition status = 'runtime' must compile to at least one predicate p ∈ P where p.origin_type = 'risk_derived' and p.acs_id = d.acs_id. This query detects approved runtime controls that did not produce any executable predicate (a compiler defect, missing catalog resolution, or unsupported event type).

**Q8: Gate/predicate reference integrity.** Every gate-map entry must reference a predicate that exists in P. Conversely, every predicate p with mandatory_role = 'decisive' (a mandatory gate) must appear in at least one gate-map entry. This query detects gates that reference non-existent predicates, or decisive predicates that were compiled but not included in the gate structure.

**Q9: Actuation authority validity.** For each actuation a ∈ evidence.actuations, the action tuple (subject, action, resource, destination) must resolve in the authority matrix S.authority_matrix at a.actuation_time. Additionally, every evidence producer cited by predicates used in the actuation must be resolvable in S. This query detects actuations whose actions are not authorized at runtime, or whose evidence sources are not recognized.

**Q10: Mandatory predicate evidence integrity.** Every predicate p with mandatory_role = 'decisive' must have on_unknown = 'fail' (fail-closed for missing evidence). Additionally, every evidence producer named in p's context conditions must be resolvable in S.authority_matrix or explicitly trusted by policy, and the evidence schema must support required freshness constraints. This query detects mandatory predicates that are not fail-closed, or that depend on unavailable or unsupported evidence sources.

---

### AMENDMENT 2: Add ACS vs. Predicate Cardinality Distinction

**Location:** Section VI "DETERMINISTIC COMPILATION AND BUNDLE SEMANTICS", after subsection A "Compiler Definition"

**INSERT the following text (new subsection):**

---

**B.1. Control Specification Count vs. Predicate Count**

An important distinction: the approved cardinality of Approved Control Specifications (ACS) is **independent** of the total count of compiled predicates. 

- An Approved Control Specification d_ij specifies the approved control policy for a single risk under a single disposition.
- At compilation time, Φ translates each approved runtime ACS into one or more predicates (p ∈ P).
- **Normative requirement:** Every approved runtime ACS must compile to at least one risk-derived predicate.
- Additionally, the compiler may add compiler-invariant predicates (INV-*) for architectural enforcement independent of risk count.

For example, a case study may have six risks, yielding six approved runtime ACS, and compile to six risk-derived predicates plus three compiler-invariant predicates, for a total of nine. The specification describes **6 ACS**, and the compiled artifact includes **9 predicates**. These are distinct quantities.

Audit query Q7 verifies that every approved runtime ACS produces at least one risk-derived predicate, regardless of the total predicate count in the bundle.

---

### AMENDMENT 3: Add Exact Runtime Outcome Semantics

**Location:** Section VI "DETERMINISTIC COMPILATION AND BUNDLE SEMANTICS", after subsection D "Policy Conflict and Precedence"

**INSERT the following text (new subsection):**

---

**D.1. Exact Runtime Decision Outcomes**

The resolver produces an exact decision at three levels:

- **PERMIT:** All required runtime conditions for authorization are satisfied under the applicable governed context.
- **DENY:** At least one mandatory/decisive runtime condition is known to be false or fails evaluation. The authorization is explicitly refused. No governed actuation/externalization occurs.
- **HOLD:** Permission cannot be established because required runtime evidence is unknown, unavailable, stale, or otherwise indeterminate, AND a valid escalation or manual-review route exists in the policy. The decision is deferred pending evidence arrival or escalation review. No actuation occurs.

**Unknown evidence without an escalation route** resolves to the fail-closed terminal behavior specified by the architecture for that mandatory gate (typically DENY, but may vary by implementation and context).

These three exact outcomes—PERMIT, DENY, HOLD—are distinct from stage-specific outcomes such as REJECT_AT_COMPILATION or REJECT_AT_ISSUANCE, which occur at compile or issuance time, not runtime.

---

### AMENDMENT 4: Add SAFE_STATE Clarification

**Location:** Section VIII "TEMPORAL TRACEABILITY AND EVIDENCE BINDING", after the newly inserted Q7-Q10 text and the "Empty result sets..." paragraph

**INSERT the following text:**

---

**Aggregate Non-Externalization Property.** The term "SAFE_STATE" in this manuscript denotes an aggregate property, not an exact runtime decision class. SAFE_STATE holds when the governed system prevents externalization (execution of the guarded external action) through any of several means:

- Exact decision = DENY (known policy violation)
- Exact decision = HOLD (escalation pending)
- Compilation rejection or issuance rejection at a prior stage

All three of these exhibit the aggregate property that externalization = false. In the context of runtime decision-level testing, DENY and HOLD both produce SAFE_STATE (non-externalization), while only PERMIT allows governed actuation.

The relationship is: **safe_state = (exact_outcome ≠ PERMIT)** for runtime decisions.

---

## ADDITIONAL CORRECTIONS

### Consistency Check: Search and Replace

Search the entire manuscript for the following normative phrases and **remove or correct them**:

| Phrase | Status | Action |
|---|---|---|
| "Case B contains 9 Approved Control Specifications" | Remove | Delete if present |
| "B-01: 3 ACS" | Remove | Delete if present |
| "B-02: 2 ACS" | Remove | Delete if present |
| "P_B_risk >= 9" | Correct to | "P_B_risk >= 6" if present |
| "six audit queries" | Correct to | "ten audit queries" if present |

**NOTE:** The current Section X (Case B) should state **six register rows, six semantically justified ACS**. Verify this is correct in the source.

---

## VERIFICATION CHECKLIST

After amendments are integrated into the DOCX, verify the following:

- [ ] Section VIII now contains Q1-Q10 (6 temporal + 4 structural)
- [ ] Section VI explicitly discusses ACS vs. predicate cardinality
- [ ] Section VI defines PERMIT, DENY, HOLD exactly
- [ ] Section VIII clarifies SAFE_STATE as aggregate
- [ ] No normative "9 ACS" statement remains
- [ ] No normative "P_B_risk >= 9" statement remains
- [ ] Section X (Case B) correctly states "6 ACS"
- [ ] All formatting is preserved (headers, tables, citations)
- [ ] No substantive text from 5.5d was removed unintentionally

---

## INTEGRATION METHOD

### Option 1: Manual Integration (Recommended for Accuracy)

1. Open `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx` in Microsoft Word
2. For each amendment above:
   - Navigate to the specified section
   - Position cursor at indicated location
   - Paste/type the amendment text
   - Adjust formatting to match surrounding text
3. Run "Find & Replace" for consistency check phrases
4. Save as `From_Risk_Register_to_Runtime_Predicate_5_5e.docx`
5. Record SHA-256 of new file

### Option 2: Programmatic Integration (Python-DOCX)

If programmatic integration is preferred:

```python
from docx import Document

source = "From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx"
doc = Document(source)

# Amendment 1: Insert Q7-Q10 before paragraph 218
# (complex due to need to preserve formatting)

# Amendment 2: Insert ACS vs predicate after finding "Compiler Definition" heading
# (complex paragraph insertion)

# Amendment 3: Insert PERMIT/DENY/HOLD after "Policy Conflict" section
# (requires finding exact location and preserving structure)

# Amendment 4: Insert SAFE_STATE clarification after Q1-Q10
# (requires formatted insertion)

doc.save("From_Risk_Register_to_Runtime_Predicate_5_5e.docx")
```

**Note:** Programmatic DOCX editing is complex and risks formatting loss. Manual integration is safer.

---

## FILE TRACKING

**Source:**
- File: `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx`
- Date: Sept 9, 2026, 13:13
- Size: 2.2 MB
- SHA-256: [To be recorded]

**Output (after amendment):**
- File: `From_Risk_Register_to_Runtime_Predicate_5_5e.docx`
- Date: [To be recorded]
- Size: [To be recorded]
- SHA-256: [To be recorded]
- Status: CORRECTED SPECIFICATION

**Do NOT overwrite the source file. Create a new revision.**

---

## GATE RE-VERIFICATION

After amendments are integrated and the new 5.5e manuscript is created:

1. Update `paper_update/MANUSCRIPT_SPECIFICATION_GATE_V3.md`
2. Verify all 7 requirements:
   - [ ] 1. Case B ACS = 6 ✓ PASS
   - [ ] 2. ACS vs predicate distinction PASS
   - [ ] 3. every runtime ACS emits >=1 predicate PASS
   - [ ] 4. complete Q1-Q10 definitions PASS
   - [ ] 5. PERMIT/DENY/HOLD semantics PASS
   - [ ] 6. SAFE_STATE aggregate clarification PASS
   - [ ] 7. no 9-ACS normative statement PASS

**Result:** If all 7 = PASS, immediately proceed to Phase 1 Development without further questions.

---

## NEXT STEP

Once 5.5e is created and gate = 7/7 PASS:

**IMMEDIATELY PROCEED TO PHASE 1 DEVELOPMENT** — no further approvals needed.

Implement:
1. Exact runtime outcomes (PERMIT/DENY/HOLD)
2. Q7-Q10 audit queries
3. Negative fixtures
4. 13-injection revalidation
5. Full development test suite

**DO NOT create preregister-tier0-v3 or final_v3 yet.**

Return results at completion.

