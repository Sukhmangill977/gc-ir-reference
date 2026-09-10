# AUDIT_QUERY_GAP_ANALYSIS.md

**Objective:** Identify GC-IR architectural invariants not covered by Q1-Q6, to enable specification of Q7-Q10.

**Date:** 2026-09-10  
**Scope:** Manuscript Section VI-VIII; compiler constraints Appendix A, B

---

## SECTION 1: Q1–Q6 PRECISE DEFINITIONS

### Q1: Obligations without an approved disposition

**Source:** `queries/traceability.sql`, lines 9-21  
**Violation detected:** An obligation in O with no risk in R that disposes it, or every disposing risk has disposition ∉ {runtime, nonruntime, accepted}

**Objects involved:**
- obligation (from assessment.O)
- risk_obligation (from assessment.O cross-reference)
- risk (from assessment.R)
- disposition (from Δ, the disposition mapping)

**Expected on conforming artifact:** Empty result set (every obligation is disposed by at least one approved/accepted risk)

**Negative fixture mutation:** Add an obligation to O, then remove its risk reference from the risk_obligation cross-table, or mark the disposing disposition as "unresolved"

**Rationale for Q1:** Manuscript Section IV-C requires that every obligation be dispositioned. Q1 is mandatory.

---

### Q2: Risks without exactly one disposition

**Source:** `queries/traceability.sql`, lines 24-32  
**Violation detected:** A risk in R with zero dispositions, or with more than one

**Objects involved:**
- risk (from assessment.R)
- disposition (from Δ)

**Expected on conforming artifact:** Empty result set (every risk receives exactly one disposition)

**Negative fixture mutation:** Create a risk without a disposition record, or add a second disposition for an existing risk

**Rationale for Q2:** Manuscript Section IV-D, Contribution C2: "Total disposition is a property of dispositions (exactly one per risk)". Q2 is mandatory.

---

### Q3: Predicates without a risk or compiler-invariant origin

**Source:** `queries/traceability.sql`, lines 35-48  
**Violation detected:** An orphan predicate: p ∈ P where p.origin ∉ (R ∪ INV), or origin_id does not resolve

**Objects involved:**
- predicate (from compiled bundle P)
- risk (from assessment.R, via origin_id)
- acs (from disposal, via acs_id, must exist)
- internal_requirement (from INV, via origin_id)

**Expected on conforming artifact:** Empty result set (every predicate has a valid risk or invariant origin)

**Negative fixture mutation:** Add a predicate with origin_id referencing a non-existent risk, or acs_id not in the approved ACS set

**Rationale for Q3:** Manuscript Section VI-B requires explicit predicate origins. Every predicate must trace to R or INV. Q3 is mandatory.

---

### Q4: Receipts whose bundle was not valid at decision time

**Source:** `queries/traceability.sql`, lines 51-57  
**Violation detected:** A receipt whose bundle hash did not bind, whose bundle was not yet effective at decision_time, or whose bundle the lifecycle registry had already retired at decision_time

**Objects involved:**
- receipt (from lifecycle evidence)
- bundle (from compiled bundle B)
- lifecycle_entry (from lifecycle registry REG)

**Expected on conforming artifact:** Empty result set (every receipt's bundle is valid at its decision time)

**Negative fixture mutation:** Create a receipt whose bundle_hash does not match any compiled bundle, or set bundle effective_from > receipt decision_time, or create a lifecycle retire entry before the receipt decision_time

**Rationale for Q4:** Manuscript Section VI-F, Contribution C5 requires temporally valid receipts. Q4 is mandatory.

---

### Q5: Actuation without a temporally prior committed receipt

**Source:** `queries/traceability.sql`, lines 60-69  
**Violation detected:** An actuation with no receipt, or whose receipt violates authorization_time ≤ evidence_commit_time < actuation_time

**Objects involved:**
- actuation (from lifecycle evidence)
- receipt (from lifecycle evidence)

**Expected on conforming artifact:** Empty result set (every actuation has a temporally prior receipt)

**Negative fixture mutation:** Create an actuation without a receipt, or set receipt evidence_commit_time ≥ actuation_time, or set receipt authorization_time > evidence_commit_time

**Rationale for Q5:** Manuscript Section VIII, Contribution C5 on temporal ordering. Q5 is mandatory.

---

### Q6: Lifecycle-registry records lacking a valid signing authority

**Source:** `queries/traceability.sql`, lines 72-78  
**Violation detected:** A lifecycle registry entry signed by a key outside authorized_signing_keys, or whose signature does not verify

**Objects involved:**
- lifecycle_entry (from REG)
- signing_key (from authority matrix S.signing_keys)

**Expected on conforming artifact:** Empty result set (every registry entry is signed by an authorized key)

**Negative fixture mutation:** Add a lifecycle entry signed by a key not in authorized_signing_keys, or forge a signature that fails verification

**Rationale for Q6:** Manuscript Section VI-F requires signed lifecycle entries. Q6 is mandatory.

---

## SECTION 2: COMPILER INVARIANTS NOT COVERED BY Q1-Q6

### Invariant Set A: ACS Compilation Coverage

**Manuscript requirement (Section V, Contribution C1):**
> "Every runtime ACS receives a disposition and may produce zero, one or several predicates."

**Current coverage:**
- Q3 checks predicate origin lineage (p → ACS)
- Q2 checks disposition totality (risk → exactly one disposition)

**UNCOVERED:**
- Whether every runtime ACS actually **emits at least one predicate**
- Whether a runtime ACS → predicate count is deterministically observable
- Distinction between "zero-predicate ACS" and "missing ACS"

**Scenario:** An ACS approved by judgment but not compiled into a predicate (e.g., conflict resolution skipped it, catalog resolution failed, or compiler has a latent bug).

**5.5d addition:** Manuscript now requires: "Every runtime ACS must emit at least one predicate."

**Proposed Q7 audit:** Runtime ACS with zero emitted predicates

---

### Invariant Set B: Gate/Decision Closure

**Manuscript requirement (Section VII-A, Proposition 1):**
> "The gate set of every risk is reachable through the authority matrix AND either the C* profile or an approved mandatory-policy gate."

**Current coverage:**
- Q1/Q2/Q3 check disposition completeness and origin
- Q6 checks registry authority

**UNCOVERED:**
- Whether a compiled gate in the gate map is actually referenced by a decision path
- Whether a decision can reach all required gates
- Whether gate-to-predicate links are internally consistent
- Missing or orphan gates in the gate map

**Scenario:** A predicate is compiled and added to gate_map, but the decision that should enforce it never consults that gate, or the gate references a predicate that does not exist.

**Proposed Q8 audit:** Gate/predicate closure: gates without reachable predicates, or predicates in gate map but not in bundle

---

### Invariant Set C: Authority Instantiation at Runtime

**Manuscript requirement (Section III-2, authority_matrix S):**
> "The (subject, action, resource, destination) tuple of every decision must resolve to S.authority_matrix."

**Current coverage:**
- Compiler step 4 (authority.py) enforces action-tuple resolution at **compilation time**
- Q6 checks signing authority in lifecycle

**UNCOVERED:**
- Whether the authority matrix is still applicable at **actuation time** (matrix may be superseded, roles changed, subjects removed)
- Whether every actuation_tuple can resolve to the authority matrix at the time of actuation
- Whether the evidence producer for an action is still authorized

**Scenario:** Authorization matrix was updated after compilation; an action that was authorized at compile-time is no longer authorized at runtime.

**Proposed Q9 audit:** Actuation authority validity: actuation whose action tuple or evidence producer cannot resolve in the authority matrix at actuation time

---

### Invariant Set D: Evidence and On-Unknown Integrity

**Manuscript requirement (Section VI-C, V):**
> "Every mandatory predicate must have on_unknown = fail."
> "Required evidence producers must be resolvable and not stale."

**Current coverage:**
- Q3 checks predicate origin (but not on_unknown setting)
- Q4 checks receipt validity (but not evidence freshness)
- Q5 checks temporal ordering (but not producer staleness)

**UNCOVERED:**
- Whether every mandatory predicate has on_unknown == "fail"
- Whether required evidence producers are resolvable in S.authority_matrix
- Whether evidence reference (if temporal) is within a specified freshness window
- Whether an evidence schema matches what the predicate expects

**Scenario:** A mandatory gate has on_unknown == "warn" (non-fail-closed); or evidence_producer cannot be resolved in the authority matrix; or evidence is stale beyond a required freshness bound.

**Proposed Q10 audit:** Mandatory predicate integrity: mandatory predicates without fail-closed on_unknown, or missing evidence producers, or stale evidence

---

## SECTION 3: SUMMARY OF UNCOVERED INVARIANTS

| Invariant class | Coverage gap | Proposed query |
|-----------------|--------------|-----------------|
| ACS compilation | Runtime ACS emission | Q7 |
| Gate reachability | Gate-predicate closure | Q8 |
| Authority at runtime | Action/producer resolution at actuation | Q9 |
| Evidence integrity | Mandatory on_unknown, producer resolution, staleness | Q10 |

**Key observation:** Q1-Q6 are temporally focused (when did X happen, was Y prior to Z). Q7-Q10 are structurally focused (does X exist, can Y resolve, is Z referenced).

This is a natural partition: Q1-Q6 (temporal traceability), Q7-Q10 (structural integrity).

---

## SECTION 4: NON-REDUNDANCY ASSURANCE

### Q7 vs. Q1-Q6

**Q1** checks: obligation has a disposition.  
**Q7** checks: runtime ACS emits a predicate.

**Difference:** Q1 is about input completeness; Q7 is about output completeness. Not redundant. ✓

### Q8 vs. Q1-Q6

**Q3** checks: predicate has a valid origin (risk or invariant).  
**Q8** checks: gate in gate-map references a predicate that exists, and is reachable.

**Difference:** Q3 is about origin lineage; Q8 is about gate closure. Not redundant. ✓

### Q9 vs. Q1-Q6

**No existing query** checks authority validity at actuation time.  
**Q6** checks lifecycle signing; **Q9** checks action/producer authority.

**Difference:** Q6 is about signatures; Q9 is about authorization. Not redundant. ✓

### Q10 vs. Q1-Q6

**Q3** checks predicate origin; **Q5** checks temporal order; **Q6** checks signatures.  
**Q10** checks on_unknown setting and evidence producer resolution.

**Difference:** No existing query checks on_unknown or evidence-producer availability. Not redundant. ✓

---

## SECTION 5: ALIGNMENT WITH MANUSCRIPT

**Contribution C5 (Section VIII):** Temporally valid traceability.
- Q1-Q5 directly support this.
- Q6 (lifecycle authority) is a prerequisite.

**New requirement (5.5d):** Every runtime ACS emits at least one predicate.
- Q7 directly audits this.

**Implicit architectural requirement (Sections VI-VII):** Structural integrity of compiled outputs.
- Q8 (gates exist and close properly)
- Q9 (authority is still valid)
- Q10 (evidence is available)

These are orthogonal to the temporal claims and do not introduce new research claims.

---

## FINAL ASSESSMENT

Q7-Q10 are **necessary for completeness** and **non-redundant** with respect to Q1-Q6.

They close gaps in structural integrity that are implied by the architecture but not explicitly audited.

**Recommendation:** Proceed to detailed Q7-Q10 specification (Section 3).

