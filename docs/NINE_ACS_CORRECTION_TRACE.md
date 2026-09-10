# NINE_ACS_CORRECTION_TRACE.md

**Purpose:** Audit every reference to "9 ACS", "nine ACS", "P_B_risk >= 9", and related variants. Classify each as HISTORICAL, SUPERSEDED, CURRENT_NORMATIVE, or CURRENT_RESULT. Document the correction applied.

**Audit date:** 2026-09-10

**Correction status:** Author-approved; implemented in CASE_B_ACS_CARDINALITY_CORRECTION.md

---

## REFERENCE CLASSIFICATION SCHEME

| Classification | Definition | Action |
|---|---|---|
| **HISTORICAL** | Captures the rejected 9-ACS requirement as it was proposed; documents provenance for scientific transparency | Keep as-is; mark with metadata tag SUPERSEDED |
| **SUPERSEDED** | Previously normative; now replaced by corrected 6-ACS specification | Update or replace with corrected text |
| **CURRENT_NORMATIVE** | Should remain in corrected form after Phase 1 implementation (e.g., "every runtime ACS emits ≥1 predicate" is independent of cardinality) | No change; clarify scope if needed |
| **CURRENT_RESULT** | Will be determined by actual development compilation and Phase 1 execution | Placeholder; update after Phase 1 |

---

## AUDIT RESULTS

### File: docs/MANUSCRIPT_5_5D_DELTA.md

**Status:** PLANNING DOCUMENT (historical record of rejected 9-ACS requirement)

**Action:** Mark entire section "SECTION 1: CASE B — APPROVED CONTROL SPECIFICATIONS (ACS) CARDINALITY" as SUPERSEDED. Retain as historical record with prominent note.

**References found:**

| Line | Text | Classification | Note | Action |
|---|---|---|---|---|
| 10 | "SECTION 1: CASE B — APPROVED CONTROL SPECIFICATIONS (ACS) CARDINALITY" | SUPERSEDED | This entire section proposes the 9-ACS expansion | Mark as SUPERSEDED; retain for provenance |
| 27-38 | "New 5.5d requirement: Case B must contain 9 ACS..." | SUPERSEDED | The proposed requirement | Remove from current specification; archive here |
| 42 | "P_B_risk >= 9" | SUPERSEDED | Incorrect; replace with "P_B_risk >= 6" | Update |
| 48 | "judgment_record.json — must mark all 9 ACS as approved" | SUPERSEDED | Instruction for non-existent 9th ACS | Remove; 6 ACS only |
| 325-326 | "Corrected Case B inputs with 9 ACS" | SUPERSEDED | Development goal that was rejected | Update to "with 6 ACS" |
| 366 | "Case B compilation with 9 ACS (31 runs, stratified)" | SUPERSEDED | Compilation plan for rejected specification | Update to "with 6 ACS" |
| 384 | "Case B: 31 executions (new, with 9 ACS)" | SUPERSEDED | Experiment plan for rejected spec | Update to "with 6 ACS" |
| 410 | "src/gcir/compiler.py (Case B with 9 ACS)" | SUPERSEDED | Compiler requirement for rejected spec | Update to "Case B" (6 ACS) |
| 476 | "Displays new Case B: 9 ACS, actual P_B_risk, new bundle SHA-256" | SUPERSEDED | Reporting plan for rejected spec | Update to "6 ACS" |
| 539 | "nine Case B ACSs, expanding audit validation..." | SUPERSEDED | Framing for rejected spec | Update to "six" |

**Correction action:** Add header to MANUSCRIPT_5_5D_DELTA.md:

```markdown
## STATUS NOTICE (2026-09-10)

The 9-ACS expansion described in Section 1 of this document has been **SUPERSEDED**
by forensic audit findings documented in:

- CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md
- ACS_GRANULARITY_RULE_5_5D.md
- NINE_ACS_PROVENANCE_AUDIT.md
- CASE_B_9_ACS_SEMANTIC_PROVENANCE.md
- CASE_B_ACS_CARDINALITY_CORRECTION.md

The forensic audit determined that Case B contains **6 semantically distinct
Approved Control Specifications** (not 9). The 9-ACS distribution cannot be
justified from manuscript material.

**Current specification:** 6 ACS per Case B risk (one per risk).

This document is retained as a historical record of the rejected proposal.
```

---

### File: docs/PROPOSED_AUDIT_QUERY_AMENDMENT_5_5D.md

**Status:** Q7-Q10 specifications remain valid; cosmetic reference to 9-ACS expansion

**Reference found:**

| Line | Text | Classification | Note | Action |
|---|---|---|---|---|
| (search result) | "expanded for 9-ACS Case B" | SUPERSEDED | Cosmetic; refers to size impact that won't occur | Update to "expanded for Case B" |

**Correction action:** Change "expanded for 9-ACS Case B" to "expanded for Case B (6 ACS)" or simply "expanded for Case B" if size is immaterial.

---

### File: docs/CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md

**Status:** CURRENT (forensic audit document; supersedes the 9-ACS proposal)

**References found:** (All are critique/analysis of the rejected 9-ACS proposal)

| Lines | Text | Classification | Note | Action |
|---|---|---|---|---|
| Various | Discusses "9-ACS requirement," "3/2/1/1/1/1 distribution," etc. | HISTORICAL | This is the audit document that rejected 9 ACS | No change; is part of the scientific record |

**Action:** Mark document as FORENSIC_AUDIT in metadata; retain as-is.

---

### File: docs/ACS_GRANULARITY_RULE_5_5D.md

**Status:** CURRENT (defines the criterion; includes critique of unsupported 9-ACS)

**References found:**

| Section | Text | Classification | Note | Action |
|---|---|---|---|---|
| Conclusion | "**NOT justified:** 9 ACS (3/2/1/1/1/1)" | HISTORICAL | Demonstrates why 9 ACS fails the granularity criterion | No change; keep as evidence |

**Action:** No change. Document is part of scientific record.

---

### File: docs/NINE_ACS_PROVENANCE_AUDIT.md

**Status:** CURRENT (provenance audit of the rejected proposal)

**References found:** (All are about the rejected requirement)

**Action:** No change; retain as scientific record.

---

### File: docs/CASE_B_9_ACS_SEMANTIC_PROVENANCE.md

**Status:** CURRENT (comprehensive semantic audit; recommended NO-GO before correction)

**References found:** (All document why 9 ACS cannot be supported)

**Action:** No change; retain as the primary audit report.

---

### File: docs/CASE_B_13_INJECTION_STAGE_AUDIT_V3.md

**Status:** CURRENT; update one reference

**Reference found:**

| Line | Text | Classification | Note | Action |
|---|---|---|---|---|
| 172 | "Status: READY FOR PHASE 1 DEVELOPMENT (pending 9-ACS provenance verification)" | CURRENT_RESULT | Conditional on 9-ACS; now that 9 ACS is rejected, can update | Update to "READY FOR PHASE 1 DEVELOPMENT with 6-ACS configuration" |

**Correction action:** Update line 172 to:

```
Status: READY FOR PHASE 1 DEVELOPMENT (6-ACS configuration)
```

---

### File: docs/PHASE_1_GO_NO_GO_FINAL.md

**Status:** CURRENT (final audit report recommending NO-GO; now superseded by author decision)

**References found:** (All relate to the blocked 9-ACS requirement)

**Action:** Add cover note marking this as the rejection document; subsequent work proceeds with 6 ACS.

```markdown
## STATUS UPDATE (2026-09-10)

This document recommended **NO-GO** for Phase 1 with the unsupported 9-ACS
specification.

The author has accepted this finding and approved proceeding with the
scientifically justified **6-ACS configuration**.

Phase 1 development now proceeds with:

- 6 semantically distinct ACS per the forensic audit
- All prior work (13 injections, Q7-Q10 queries) remains valid and unchanged
- Code/spec alignment work (PERMIT/DENY/HOLD) proceeds as planned

See CASE_B_ACS_CARDINALITY_CORRECTION.md for the corrected specification.
```

---

### File: paper_update/MANUSCRIPT_5_5D_DELTA.md

**Status:** PLANNING DOCUMENT (superseded by CASE_B_ACS_CARDINALITY_CORRECTION.md)

**Action:** Retain as-is for historical documentation. Add header:

```markdown
## STATUS (2026-09-10)

This delta document proposed a 9-ACS expansion for Case B. That proposal has
been **REJECTED** based on forensic audit findings. See:

- CASE_B_ACS_CARDINALITY_CORRECTION.md (corrected specification)
- CASE_B_9_ACS_SEMANTIC_PROVENANCE.md (audit findings)

The corrected specification specifies 6 ACS per Case B risk. This document is
retained for provenance documentation.
```

---

### File: paper_update/CASE_B_ACS_CARDINALITY_CORRECTION.md

**Status:** NEW; CURRENT_NORMATIVE (replaces the 9-ACS proposal)

**Content:** Establishes 6 ACS as the corrected, scientifically justified specification.

**Action:** None; this is the correction document.

---

## PREDICATE COUNT CLARIFICATIONS

### Across all documentation, distinguish:

- **ACS count (Case B):** Now fixed at 6 (one per risk)
- **Risk-derived predicate count (P_B_risk):** TBD at Phase 1 compilation; will be ≥ 6 (at least one per ACS)
- **Compiler-invariant predicate count (P_B_inv):** Currently 3 (INV-VERSION, INV-AUTHORITY-CLOSURE, INV-EVIDENCE-COMMIT)
- **Total predicate count (P_B_total):** TBD; = P_B_risk + P_B_inv; expected ~9 if P_B_risk remains 6, but DO NOT assume

### Update all references that confused these quantities:

**Example:**
- **Before:** "Case B will have 9 ACS"
- **After:** "Case B will have 6 ACS and approximately 9 total predicates (6 risk-derived + 3 compiler-invariant)"

---

## FILES CREATED OR UPDATED

### Created (new audit/correction documents)

- [ ] `docs/CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md` ✓ (created)
- [ ] `docs/ACS_GRANULARITY_RULE_5_5D.md` ✓ (created)
- [ ] `docs/NINE_ACS_PROVENANCE_AUDIT.md` ✓ (created)
- [ ] `docs/CASE_B_9_ACS_SEMANTIC_PROVENANCE.md` ✓ (created)
- [ ] `docs/PHASE_1_GO_NO_GO_FINAL.md` ✓ (created)
- [ ] `docs/NINE_ACS_CORRECTION_TRACE.md` ✓ (this file)
- [ ] `paper_update/CASE_B_ACS_CARDINALITY_CORRECTION.md` ✓ (created)

### To update (add status headers/marks)

- [ ] `docs/MANUSCRIPT_5_5D_DELTA.md` (add SUPERSEDED header to Section 1)
- [ ] `docs/CASE_B_13_INJECTION_STAGE_AUDIT_V3.md` (update line 172)
- [ ] `docs/PROPOSED_AUDIT_QUERY_AMENDMENT_5_5D.md` (minor cosmetic: "9-ACS" → "6-ACS" or remove "9-")
- [ ] `docs/PHASE_1_GO_NO_GO_FINAL.md` (add status update header)

---

## SUMMARY

**Total "9 ACS" references audited:** 10+ across 5 files

**Classification breakdown:**
- **HISTORICAL (retain as scientific record):** Documents that show why the proposal was rejected
- **SUPERSEDED (update):** Planning/specification documents that proposed the rejected expansion
- **CURRENT_NORMATIVE (keep as-is):** General requirements like "every runtime ACS emits ≥1 predicate" remain valid
- **CURRENT_RESULT (TBD):** Actual Phase 1 compilation results to be filled in after development

**Correction principle:** The 9-ACS proposal is documented for provenance and scientific transparency, but all specification moving forward uses the corrected 6-ACS configuration.

