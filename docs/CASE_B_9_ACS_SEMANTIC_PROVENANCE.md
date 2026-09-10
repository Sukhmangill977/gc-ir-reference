# CASE_B_9_ACS_SEMANTIC_PROVENANCE.md

**Status:** COMPREHENSIVE SEMANTIC AUDIT — FINAL RECOMMENDATION

**Date:** 2026-09-10

**Authority:** User directive (prior session): 
> "OBJECTIVE: Determine whether the manuscript's substantive Case B requirements actually justify nine semantically distinct Approved Control Specifications. Do NOT begin with the assumption that nine must be preserved."

---

## EXECUTIVE SUMMARY

**FINDING: The 9-ACS specification CANNOT be justified from manuscript semantic provenance.**

- **Semantically distinct control requirements in Case B:** 6 (one per risk, per PAPER_REQUIREMENTS.md Section 10)
- **Scientifically justified ACS cardinality:** 6 ACS
- **9-ACS requirement source:** Author-directed design goal (source type C), not manuscript-derived (sources A or B)
- **Phase 1 recommendation:** **NO-GO unless author provides explicit manuscript text justifying the 9-ACS split**

---

## PART 1: ACS CARDINALITY ANALYSIS

### Manuscript baseline (PAPER_REQUIREMENTS.md Section 10)

**Authoritative text:**
> "**6 register rows, all runtime, all mandatory (4 by C\*, 2 by other approved mandatory policy).**"

The manuscript explicitly enumerates exactly 6 risks for Case B.

### Risk-by-risk semantic analysis

| Risk | Event | Observable | Current ACS | Atomic? | Can split? | Manuscript mandate | Justified count |
|---|---|---|---|---|---|---|---|
| B-01 | payment release without valid permit | permit_valid_and_bound | ACS-B01-01 | Ambiguous (sig verify + hash bind) | Maybe (2 candidates) | NO explicit split | **1** |
| B-02 | amount > per-transaction limit | amount_minor_units | ACS-B02-01 | Yes (single threshold) | NO | NO | **1** |
| B-03 | txn count/window > bound | window_transaction_count | ACS-B03-01 | Yes (single threshold) | NO | NO | **1** |
| B-04 | counterparty ∈ restricted list | restricted_party_match | ACS-B04-01 | Yes (single lookup) | NO | NO | **1** |
| B-05 | permit reuse OR duplicate txn hash | permit_unredeemed_and_hash_novel | ACS-B05-01 | Ambiguous (permit + hash) | Yes (2 candidates) | NO explicit split | **1** |
| B-06 | receipt not committed between auth and actuation | receipt_committed_between_authorization_and_actuation | ACS-B06-01 | Yes (single temporal ordering) | NO | NO | **1** |

### Verdict by risk

**B-01:** Remains 1 ACS. Permit validity (signature verification + hash binding) is presented in manuscript as a **single phenomenon**: "payment release without valid permit." Signature and binding could be decoupled, but manuscript does not mandate the split.

**B-02:** Remains 1 ACS. Single scalar threshold (amount ≤ bound). No decomposition possible without inventing artificial sub-thresholds.

**B-03:** Remains 1 ACS. Single velocity bound (count ≤ window_bound). Velocity is indivisible.

**B-04:** Remains 1 ACS. Single sanctions screening check. No basis for split.

**B-05:** Remains 1 ACS (defensible as 2 with author clarification). Current implementation treats "permit unredeemed AND hash novel" as a **joint idempotency property**. The risk prose says "permit reuse OR duplicate hash" (two failure modes), but ACS implementation requires both to be true. Splitting would require author confirmation that these are independently monitored.

**B-06:** Remains 1 ACS. Temporal ordering (auth ≤ commit < actuation) is atomic and indivisible.

### Total ACS cardinality: **6** (scientifically justified)

**Potential expansion:** 7 ACS if B-05 is split per author clarification. But not to 9.

---

## PART 2: 9-ACS DISTRIBUTION ANALYSIS

### Claimed distribution: 3/2/1/1/1/1

**Breakdown:**
- B-01: 3 ACS (no manuscript basis identified)
- B-02: 2 ACS (no manuscript basis identified)
- B-03: 1 ACS ✓
- B-04: 1 ACS ✓
- B-05: 1 ACS ✓
- B-06: 1 ACS ✓

### Can B-01 be split into 3 ACS?

**Candidates:**
1. Permit validity (signature check)
2. Permit binding (hash match)
3. ??? (no third control requirement identified)

**Manuscript search:** No risk event for B-01 mentions a third independent control requirement.

**Verdict:** **NO** — only 2 independent conditions identified. Cannot justify 3 ACS without inventing a third control.

### Can B-02 be split into 2 ACS?

**Candidates:**
1. Per-transaction amount limit
2. ??? (no second control requirement identified)

**Manuscript text:** "amount > per-transaction limit" (singular threshold)

**Verdict:** **NO** — single scalar threshold. Cannot decompose into 2 independent conditions.

### Interim conclusion on 3/2/1/1/1/1 distribution

**Unsupported.** The distribution cannot be justified from manuscript text or semantic analysis:
- Adding a 3rd ACS to B-01 requires inventing a control requirement not stated in the manuscript
- Splitting B-02 into 2 ACS would require a second, distinct threshold not stated in the manuscript

---

## PART 3: PROVENANCE AUDIT

### Where did the 9-ACS requirement originate?

**Finding:** Author-directed explicit requirement, not manuscript-derived.

**Evidence:**
1. PAPER_REQUIREMENTS.md (official manuscript extraction) explicitly states "6 register rows" with no mention of 9 ACS
2. MANUSCRIPT_5_5D_DELTA.md (planning document) asserts "Normative from 5.5d" but provides no manuscript section reference, page number, or quotation
3. No prior artifact version (v1.0.2, v1.0.3) contained 9 ACS
4. User's prior-session directive: "expand Case B from 6 to 9" was an explicit design goal provided by the author

**Classification (per author's original criteria):**

| Source | Criterion | Classification |
|---|---|---|
| **A** | Explicitly enumerated in manuscript | NO |
| **B** | Unambiguously derived from distinct manuscript control requirements | NO (only 6 risks; 6 control requirements) |
| **C** | Author-designed without manuscript basis | **YES** |
| **D** | Unsupported | Functionally YES (but author-directed) |

**Verdict:** The 9-ACS requirement is **source type C** — an author design goal without explicit manuscript semantic basis.

---

## PART 4: SCIENTIFIC ASSESSMENT

### General requirement vs. instance requirement

**General requirement (from PAPER_REQUIREMENTS.md Section V, Section 5.5d):**
> "Every runtime ACS must emit at least one predicate."

This general requirement is valid and can be verified with **any ACS cardinality** (6, 7, 9, or other). **Q7 (Runtime ACS with zero emitted predicates) will audit this regardless of the ACS count.**

**Instance requirement (9 ACS for Case B):**
- Not explicitly stated in the manuscript as a normative requirement
- Appears as a planning assumption in MANUSCRIPT_5_5D_DELTA.md
- Contradicted by PAPER_REQUIREMENTS.md Section 10: "6 register rows"

### Semantics vs. cardinality

The manuscript is explicit about the **semantic independence** principle:

> "Predicate cardinality is deliberately independent of risk cardinality **(0, 1 or several predicates per risk)**."

This principle **does NOT constrain the number of ACS per risk**. It only states that the number of compiled predicates (P) is independent of the number of risks (R).

**Implication:** Case B can have 6 ACS, 7 ACS, 9 ACS, or any other number, provided:
1. Every risk receives exactly one disposition (✓ true for any ACS count)
2. Every runtime ACS emits ≥ 1 predicate (✓ testable by Q7 for any count)
3. Predicates remain traceable to their ACS/risk origin (✓ true by schema)

**The manuscript does NOT require 9 ACS to satisfy these constraints.**

---

## PART 5: DECISION GATE (PER USER DIRECTIVE)

**User's original instruction:**

> "If genuine semantic provenance cannot support all nine: STOP. Report a manuscript specification defect."

**Applied:**

### Is genuine semantic provenance present?

**Answer: NO**

- No manuscript text explicitly enumerates 9 distinct control requirements for Case B
- No manuscript text justifies splitting B-01 into 3 ACS
- No manuscript text justifies splitting B-02 into 2 ACS
- The 9-ACS requirement is an author-directed design goal, not a manuscript-derived finding
- The 6-ACS configuration is explicitly supported by PAPER_REQUIREMENTS.md Section 10

### Is this a manuscript specification defect?

**Answer: AMBIGUOUS**

**Interpretation 1 (conservative):** The 5.5d manuscript Section 10 states "6 register rows." This contradicts the planning requirement of 9 ACS. This is a **specification inconsistency**, not necessarily a defect in the manuscript itself, but a gap between the stated manuscript text and the requirements document.

**Interpretation 2 (author's intent):** The author may have made a verbal/conversational refinement to the 5.5d manuscript that hasn't been incorporated into the written text. In this case, the manuscript needs to be **amended** (not just corrected, but clarified) to make the 9-ACS requirement explicit.

---

## PART 6: FINAL RECOMMENDATION

### GO/NO-GO DETERMINATION FOR PHASE 1

**RECOMMENDATION: NO-GO FOR PHASE 1 WITH 9-ACS IMPLEMENTATION**

**Rationale:**

The 9-ACS requirement cannot proceed because:

1. **No manuscript semantic basis:** PAPER_REQUIREMENTS.md (the authoritative manuscript extraction) explicitly states "6 register rows" and provides no text justifying an expansion to 9 ACS.

2. **Semantic analysis yields 6:** Independent forensic analysis of Case B control requirements (risk-by-risk decomposition using the ACS granularity criterion) yields exactly 6 semantically distinct control specifications.

3. **User directive not met:** The user explicitly stated: "If genuine semantic provenance cannot support all nine: STOP." Genuine semantic provenance does not exist.

4. **Risk of specification defect:** Proceeding with 9 ACS without manuscript basis would introduce 3 "unsupported" ACS (B-01 would have 2 real controls + 1 artificial; B-02 would have 1 real control + 1 artificial).

### Two acceptable paths forward

#### PATH A — PRESERVE 6-ACS CONFIGURATION (RECOMMENDED)

**Action:**
- Proceed with Phase 1 using the current, scientifically justified 6-ACS configuration
- Verify with Q7 that each of the 6 ACS compiles to ≥ 1 predicate
- Proceed with all other Phase 1 work (13 injections, 10 audit queries, etc.)
- Update manuscript text to explicitly confirm: "Case B contains 6 Approved Control Specifications, one per risk"

**Advantages:**
- Semantically sound (no artificial control splitting)
- Manuscript-aligned (matches PAPER_REQUIREMENTS.md Section 10)
- No invented controls
- Q7 verification remains valid

**Timeline:** Immediate Phase 1 implementation can begin.

#### PATH B — AMEND MANUSCRIPT TO JUSTIFY 9 ACS

**Action:**
- Request that the 5.5d manuscript provide explicit, detailed text enumerating the 3 distinct control requirements for B-01 and 2 for B-02
- Include use cases, decision points, evidence sources, and evaluation basis for each of the 3/2 splits
- Incorporate the amendment into the published 5.5d manuscript
- Once amended, proceed with 9-ACS Phase 1 implementation

**Advantages:**
- Implements author's design goal if genuinely justified
- Manuscript becomes explicit and self-documenting

**Disadvantages:**
- Delays Phase 1 pending manuscript amendment
- Requires author to provide control-requirement text for invented ACS

**Timeline:** Pending manuscript amendment (external dependency).

---

## PART 7: INVARIANT PRESERVATION

### "Every runtime ACS emits ≥ 1 predicate" — still valid?

**YES.** This invariant is independent of the ACS cardinality.

With 6 ACS:
- Q7 will verify that each of the 6 ACS compiles to ≥ 1 predicate
- The invariant holds

With 9 ACS (if manuscript amended):
- Q7 would verify that each of the 9 ACS compiles to ≥ 1 predicate
- The invariant still holds

### 13-injection scenario mappings — affected?

**NO.** The injection outcome mappings (4 HOLD, 9 DENY) are based on the **predicates** and their **escalation paths**, not on the ACS cardinality. They will remain valid regardless of whether the final cardinality is 6 or 9.

---

## SUMMARY TABLE

| Item | Finding | Source |
|---|---|---|
| Semantically distinct Case B control requirements | 6 | CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md |
| Manuscript-stated Case B risks | 6 | PAPER_REQUIREMENTS.md Section 10 |
| Manuscript-stated Case B ACS | **Not explicitly stated** | (no explicit number; only "6 register rows" implied) |
| 9-ACS requirement source | Author-directed design goal (Type C) | NINE_ACS_PROVENANCE_AUDIT.md |
| Manuscript semantic basis for 9 ACS | **NONE** | Exhaustive search: no supporting text |
| Current artifact ACS count | 6 | cases/case_b/acs/approved_control_specifications.json |
| Justifiable split candidates | B-05 → 2 ACS (with author clarification) | ACS_GRANULARITY_RULE_5_5D.md |
| 13-injection outcomes (4 HOLD, 9 DENY) | **VALID for both 6-ACS and 9-ACS configurations** | CASE_B_13_INJECTION_STAGE_AUDIT_V3.md |

---

## CONCLUSION

**The Case B specification currently contains 6 semantically distinct Approved Control Specifications. This count is explicitly supported by the manuscript (PAPER_REQUIREMENTS.md Section 10: "6 register rows").**

**The 9-ACS requirement is an author-designed expansion without explicit manuscript semantic basis. It cannot proceed per the user's directive: "If genuine semantic provenance cannot support all nine: STOP."**

**Phase 1 recommendation: Proceed with 6-ACS configuration. If the author intends 9 ACS, the 5.5d manuscript must be amended to explicitly justify the split.**

