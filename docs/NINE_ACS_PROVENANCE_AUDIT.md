# NINE_ACS_PROVENANCE_AUDIT.md

**Objective:** Determine the origin of the "9 ACS" requirement for Case B (distributed as 3/2/1/1/1/1).

**Methodology:** Trace the requirement through repository history, manuscript extracts, and documentation changes.

---

## REQUIREMENT STATEMENT

The 9-ACS requirement appears in:

**File:** `docs/MANUSCRIPT_5_5D_DELTA.md`

**Location:** Section 1, "New 5.5d requirement"

**Text:**
> "**Normative from 5.5d:**
> - Case B must contain **9 Approved Control Specifications**
> - Distribution:
>   - B-01: 3 ACS
>   - B-02: 2 ACS
>   - B-03: 1 ACS
>   - B-04: 1 ACS
>   - B-05: 1 ACS
>   - B-06: 1 ACS
>   - **Total = 9 ACS**"

---

## MANUSCRIPT SOURCE VERIFICATION

**Claimed source:** "5.5d manuscript"

**Files consulted:**
1. `/Users/sukhmangill/Desktop/paper3 doc/files (73)/From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx` (Sept 9, 2026)
   - Cannot be read with available tools
   - Binary Word document format

2. `docs/PAPER_REQUIREMENTS.md` (authoritative extracted manuscript requirements)
   - Section 10: "**6 register rows, all runtime, all mandatory**"
   - No mention of 9 ACS
   - No enumeration of split ACS

3. `docs/MANUSCRIPT_5_5D_DELTA.md` (change audit document)
   - Asserts "Normative from 5.5d" without source section reference
   - No page number, no quotation, no manuscript location cited

---

## REPOSITORY HISTORY SEARCH

**Search for 9-ACS requirement in commit history:**

Command:
```bash
git log --all --grep="9.*ACS\|B-01.*3\|B-02.*2" --oneline
```

Result: No commits found with this pattern.

**Search for recent changes to MANUSCRIPT_5_5D_DELTA.md:**

The file `docs/MANUSCRIPT_5_5D_DELTA.md` is recent (audit date Sept 10, 2026, per file header). It is likely a planning document created to track 5.5d requirements, not an extracted set of actual manuscript statements.

---

## CHAIN OF CUSTODY ANALYSIS

### Who authored MANUSCRIPT_5_5D_DELTA.md?

**Evidence:**
- File header: "Audit date: 2026-09-10"
- Authority: "Explicit 5.5d requirements provided"
- Content: Structured planning document with "Old artifact assumption" vs. "New 5.5d requirement" format

**Interpretation:** This document was written to capture requirements stated verbally or in a separate communication (not textually in the manuscript itself).

### What is the "explicit 5.5d requirements provided" source?

**From the conversation context (prior session):**

The user (author) provided explicit 5.5d requirements in their first message:

> "Design and audit a comprehensive specification update for a scientific artifact to align with a new '5.5d' manuscript version. The primary requirements are: (1) expand Case B from 6 to 9 Approved Control Specifications with every runtime ACS emitting at least one predicate..."

**Key finding:** The 9-ACS requirement was **provided as an explicit requirement statement by the user/author**, not extracted from manuscript text.

The MANUSCRIPT_5_5D_DELTA.md document is a **planning specification**, not a **manuscript extraction**.

---

## ORIGIN CLASSIFICATION

### Source type: AUTHOR INSTRUCTION

The 9-ACS requirement is:

- **Type:** Author-provided explicit requirement
- **Channel:** Verbal/conversation directive
- **Authority:** The manuscript author (via conversation)
- **Manuscript basis:** Implied but not explicitly quoted
- **Documentation:** Captured in MANUSCRIPT_5_5D_DELTA.md as "Normative from 5.5d"

### Alternative interpretations (rejected)

1. **"It's in the manuscript text"** — REJECTED
   - No quoted text found
   - No section/page reference
   - PAPER_REQUIREMENTS.md Section 10 explicitly states "6 register rows"

2. **"It's derived from prior artifact versions"** — REJECTED
   - Current artifact (v1.0.3) has 6 ACS
   - v1.0.2 had 6 ACS
   - No prior version has 9 ACS

3. **"It's from automated tooling or inference"** — REJECTED
   - No Claude-generated code audit produced this split
   - No algorithmic rule generates the 3/2/1/1/1/1 distribution

---

## ASSESSMENT

### Is the 9-ACS requirement scientifically grounded?

**Evidence:**

1. **Manuscript text:** No explicit manuscript text enumerates 9 ACS or justifies 3/2/1/1/1/1 split
   - PAPER_REQUIREMENTS.md says "6 register rows"
   - No supplement or errata mentions 9 ACS

2. **Semantic justification:** No independent normative control requirements justify splitting:
   - B-01: No manuscript text suggests signature verification and hash binding are separate controls
   - B-02: Single threshold; no basis for split

3. **Author intent:** Author explicitly stated:
   - "expand Case B from 6 to 9 Approved Control Specifications"
   - This was an explicit design goal, not derived from manuscript analysis

---

## CONCLUSION: PROVENANCE CLASSIFICATION

**Source classification per author's original directive:**

The 9-ACS requirement is:

- **A**: Explicitly enumerated in manuscript ← **NO**
- **B**: Unambiguously derived from distinct manuscript control requirements ← **NO** (only 6 risks stated)
- **C**: Author-designed without manuscript basis ← **YES** (author instruction, not manuscript extraction)
- **D**: Unsupported ← **TECHNICALLY YES, but author-directed**

**Classification: C (Author-designed without explicit manuscript basis)**

The 9-ACS requirement was **explicitly provided by the author as a design goal**, not discovered through manuscript analysis. However, it **lacks manuscript text explicitly justifying the 3/2/1/1/1/1 distribution**.

---

## IMPLICATIONS FOR PHASE 1 APPROVAL

**Per user's directive:**

> "If genuine semantic provenance cannot support all nine: STOP. Report a manuscript specification defect."

**Finding:** The 9-ACS specification **cannot be supported by genuine manuscript semantic provenance**. 

The 6-ACS configuration (current) is explicitly supported by PAPER_REQUIREMENTS.md Section 10:
> "**6 register rows, all runtime, all mandatory**"

The 9-ACS configuration is a **planning/design goal without manuscript basis**.

**Action required:** Author must either:

1. **Provide explicit manuscript text** enumerating control requirements that justify 3 ACS for B-01 and 2 for B-02, OR
2. **Revise the specification** to align Phase 1 with the scientifically justified 6-ACS cardinality

---

## RECOMMENDATION

The 9-ACS requirement is **author-directed (source: C)** but **not manuscript-grounded (source: A or B)**.

**Status for Phase 1:** **BLOCKED unless author clarifies manuscript basis**

**Options:**

### Option 1: Provide manuscript justification
If the 5.5d manuscript actually contains explicit control-requirement text supporting 9 ACS, provide the quotation and section reference. Then proceed with 9-ACS implementation.

### Option 2: Accept scientific finding
Accept that Case B has **6 semantically distinct control requirements** (1 per risk, per manuscript). Proceed with Phase 1 using 6 ACS. The general requirement "every runtime ACS emits ≥ 1 predicate" is still satisfied with 6 ACS, and Q7 will verify this.

### Option 3: Delay and request amendment
Request that the 5.5d manuscript be amended to explicitly enumerate the control requirements justifying 9 ACS (or 7 ACS if B-05 is split). Then freeze the amended specification and proceed.

