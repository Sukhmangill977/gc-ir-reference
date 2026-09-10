# CASE_B_ACS_CARDINALITY_CORRECTION.md

**Manuscript version affected:** 5.5d (IEEE submission)

**Correction target version:** 5.5e

**Correction date:** 2026-09-10

**Status:** Correction validated by forensic audit; author-approved for implementation

---

## SUMMARY OF CORRECTION

The previously proposed expansion of Case B from 6 to 9 Approved Control Specifications (distributed 3/2/1/1/1/1) is **withdrawn** based on forensic audit findings.

**Corrected specification:**

Case B contains **six semantically distinct Approved Control Specifications**, one per risk:
- B-01: 1 ACS (payment release without valid permit)
- B-02: 1 ACS (amount > per-transaction limit)
- B-03: 1 ACS (txn count/window > bound)
- B-04: 1 ACS (counterparty ∈ restricted list)
- B-05: 1 ACS (permit reuse or duplicate hash)
- B-06: 1 ACS (receipt not committed between auth and actuation)

**Total: 6 ACS (not 9)**

---

## FORENSIC AUDIT FINDINGS

### Semantic Analysis

A forensic decomposition of each Case B risk was performed against the ACS granularity criterion (ACS_GRANULARITY_RULE_5_5D.md):

**An ACS warrants separate specification if it exhibits at least one of:**
1. Independent failure modes
2. Independent evidence source
3. Independent operational bound
4. Independent authorization scope
5. Independent temporal condition
6. Independent gate consequence
7. Can be evaluated independently at runtime

**Result for each risk:**

| Risk | Criterion test | Result | ACS count |
|---|---|---|---|
| B-01 | permit validity (sig + binding): joint observable; no split mandate | NOT DISTINCT (unless manuscript clarifies) | 1 |
| B-02 | amount ≤ bound: single scalar threshold | ATOMIC (no decomposition) | 1 |
| B-03 | count ≤ window_bound: single velocity threshold | ATOMIC (indivisible) | 1 |
| B-04 | counterparty match: single deterministic check | ATOMIC | 1 |
| B-05 | permit unredeemed AND hash novel: two conditions, but joint idempotency purpose | NOT DISTINCT (defensible as 2 with author clarification; currently 1) | 1 |
| B-06 | temporal ordering (auth ≤ commit < actuation) | ATOMIC (ordering is indivisible) | 1 |

**Conclusion:** 6 semantically justified ACS. No manuscript text supports splitting to 9.

### Provenance of Withdrawn 9-ACS Requirement

The 9-ACS requirement originated as an author-directed design goal (source type C: author-designed without explicit manuscript basis). It was not extracted from the 5.5d manuscript text.

**Evidence:**
- PAPER_REQUIREMENTS.md (official manuscript extraction) states "6 register rows" with no mention of 9 ACS
- No quoted manuscript text enumerates 3 controls for B-01 or 2 for B-02
- The 3/2/1/1/1/1 distribution does not appear in any published manuscript section

---

## NORMATIVE STATEMENT FOR CORRECTED MANUSCRIPT (5.5e)

### Case B (Section X)

**Current (5.5d):**
> [Previous text with 9 ACS]

**Corrected (5.5e):**

> **Case B — Transaction Authorization Agent**
>
> Case B is a per-transaction authorization agent operating at machine speed. Every proposed payment externalization is mediated by the runtime authority. The authority matrix admits exactly one external action (`release_payment`) with bound parameters.
>
> **Case B Risk Register**
>
> Six register risks, all runtime, all mandatory (4 by consequence-class C*, 2 by other approved mandatory policy):
>
> | risk_id | Event | consequence_class | L×I | Gate |
> |---|---|---|---|---|
> | B-01 | payment release without valid permit | **C\***: authority | 15 | mandatory (C\*) |
> | B-02 | amount > per-transaction limit | financial_loss | 16 | mandatory (other) |
> | B-03 | txn count/window > bound | financial_loss | 12 | mandatory (other) |
> | B-04 | counterparty ∈ restricted list | **C\***: statutory (material) | 5 | mandatory (C\*) |
> | B-05 | permit reuse or duplicate txn hash | **C\***: irreversible | 10 | mandatory (C\*) |
> | B-06 | receipt not committed between authorization and actuation | **C\***: statutory (material) | 10 | mandatory (C\*) |
>
> **Approved Control Specifications**
>
> Case B contains six semantically distinct Approved Control Specifications, one per risk. Each ACS is assigned by the human authority and approved through the judgment record. The compiled bundle must verify that each approved ACS compiles to at least one risk-derived predicate.
>
> **Predicate Composition**
>
> The compiled Case B bundle contains:
> - Risk-derived predicates: one or more per approved ACS (determined at compilation; required ≥ 1 per ACS)
> - Compiler-invariant predicates: mandatory gates over authority closure, evidence commit, and version/configuration integrity
>
> Total predicate count is determined by compilation, not ACS count. The general requirement remains: every approved **runtime ACS** must emit at least one **risk-derived predicate**. This requirement is independent of the ACS cardinality in any particular case and is verified by audit query Q7.
>
> Because every row carries a mandatory gate, any threshold `t ≤ 5` reproduces the approved gate set. Case B contains no Proposition 1 inversion or Proposition 2 collision, and `GD_min = 0`. Case B contributes gate-source diversity, not separation evidence.
>
> [Continue with evidence classification, forensic reconstruction note, etc.]

---

## KEY DISTINCTIONS CLARIFIED

### ACS count ≠ Predicate count

**Previously unclear:** Did "9 ACS" mean 9 risk-derived predicates?

**Corrected language:**
- **Approved Control Specifications (ACS):** The set of approved control requirements the governance authority has assigned per-risk. Case B has 6.
- **Risk-derived predicates:** The predicates compiled from approved ACS. Case B will have ≥ 6 (one per ACS minimum, but possibly more depending on catalog choices).
- **Compiler-invariant predicates:** Predicates added by the compiler for architecture reasons (version, evidence commit, authority closure). Currently 3 for Case B.
- **Total predicates:** Risk-derived + compiler-invariant.

**Example:** Case B may have:
- 6 ACS
- 6 risk-derived predicates (one per ACS)
- 3 compiler-invariant predicates
- **9 total predicates**

This is not "9 ACS." It is "6 ACS, 9 total predicates."

### Q7 is not a cardinality enforcement query

**Previously implied:** Q7 might force Case B to have 9 ACS.

**Corrected:** Q7 tests **compilation completeness at ACS granularity**:

> For every approved runtime ACS, count(risk-derived predicates where acs_id matches) ≥ 1.

Q7 is satisfied by Case B equally whether it has 6, 7, or 9 ACS, provided each ACS compiles to ≥ 1 predicate.

---

## GENERAL REQUIREMENT STATEMENT (Section V, restated for clarity)

**Normative from Section V (5.5d unchanged):**

> Every approved **runtime Approved Control Specification** must compile to at least one **risk-derived predicate**. This requirement is independent of:
> - The cardinality of ACS in any particular case
> - The total count of predicates in the compiled bundle
> - The number of compiler-invariant predicates added
>
> Verification: Audit query Q7 detects any runtime ACS that compiles to zero risk-derived predicates, indicating a compiler defect or catalog gap.

---

## WHAT THIS CORRECTION DOES AND DOES NOT CHANGE

### Preserves (unchanged)

- **6 Case B risks** (immutable: defined in the risk assessment)
- **Semantics of each risk** (no control requirement redefined)
- **The 13 Case B injection scenarios** (test the 6 ACS predicates)
- **Outcome classifications** (4 HOLD, 9 DENY — mapping to predicates, not ACS)
- **Audit queries Q1-Q10** (all 10 remain valid; Q7 is independent of ACS cardinality)
- **The general compiler invariant** (every runtime ACS → ≥ 1 predicate)
- **Temporal ordering and gate coverage** (unchanged)

### Corrects

- **ACS cardinality for Case B:** 6 (not 9)
- **Removal of unsupported split:** B-01 remains 1 ACS, B-02 remains 1 ACS
- **Manuscript clarity:** Explicitly distinguish ACS count from total predicate count
- **Q7 framing:** Make clear it is not a cardinality enforcer

### Does NOT change

- **Case B bundle hash:** If the 6 ACS inputs and compiler semantics remain unchanged, the canonical bundle hash should not change. A scientific correction does not force a hash change unless the hashed artifact actually differs.
- **Historical record:** The rejected 9-ACS proposal is documented in NINE_ACS_PROVENANCE_AUDIT.md and CASE_B_ACS_CARDINALITY_CORRECTION.md for scientific transparency.
- **Case A:** Unaffected.
- **final_v2 results:** Historical; preserved as-is.

---

## IMPLEMENTATION CHECKLIST

- [ ] Manuscript 5.5e (corrected): Section X updated with 6-ACS Case B specification
- [ ] Q7 documentation: Clarified as compilation-completeness test, not cardinality enforcer
- [ ] Case B ACS file: Remains 6 records (no splitting of B-01 or B-02)
- [ ] Case B compilation: Rerun with 6 ACS; record actual P_B_risk, P_B_inv, P_B_total
- [ ] Case B bundle hash: Record; verify whether it changed (should not if inputs/compiler unchanged)
- [ ] Development test suite: Run with corrected 6-ACS configuration
- [ ] 13 injection scenarios: Revalidate exact outcomes (4 HOLD, 9 DENY)
- [ ] Historical trace: NINE_ACS_CORRECTION_TRACE.md documents all references updated or superseded

---

## RATIONALE FOR THIS CORRECTION

**Scientific integrity:** The 9-ACS requirement lacked genuine semantic provenance. Proceeding with an unjustified specification would have created 3 "artificial" ACS without independent control requirements, violating the ACS granularity criterion.

**Manuscript fidelity:** PAPER_REQUIREMENTS.md Section 10 explicitly states "6 register rows," and the forensic audit confirms 6 semantically distinct control requirements. The manuscript was correct; the planning assumption was not.

**Compiler correctness:** The general requirement "every runtime ACS emits ≥ 1 predicate" is independent of whether Case B has 6 or 9 ACS. Eliminating the unsupported split restores alignment between the actual control semantics and the approved specification.

