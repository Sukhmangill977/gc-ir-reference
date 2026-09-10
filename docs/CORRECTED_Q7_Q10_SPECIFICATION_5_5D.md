# CORRECTED_Q7_Q10_SPECIFICATION_5_5D.md

**Purpose:** Corrected Q7-Q10 specifications addressing all author feedback.

**Date:** 2026-09-10  
**Status:** DESIGN PHASE — corrected, ready for author approval

---

## MANUSCRIPT NOTATION (Verified)

From PAPER_REQUIREMENTS.md and manuscript Section IV-VI:

| Symbol | Meaning | Notes |
|--------|---------|-------|
| `𝒢 = (M, S, O, R, A)` | Governance input model | Assessment metadata, system profile, obligations, risks, analysis |
| `D` | Approved Control Specifications (ACS set) | `d_ij ∈ D` per PAPER_REQUIREMENTS.md 4.3 |
| `Δ` | Disposition set | `Δ_i ∈ {runtime(D_i), nonruntime(C_i), accepted(RA_i), unresolved(U_i)}` per 4.4 |
| `K` | Control Derivation Catalog | Per 4.2 |
| `J` | Judgment record | Signed; closes Ψ_K into a function |
| `Φ` | Compiler | `Φ : (M, S, O, R, A, K, D, Δ) → (P, G, E, B)` per 4.1 |
| `P` | Predicate set | Compiled output |
| `G` | Gate map | Compiled output |
| `E` | Escalation map | Compiled output |
| `B` | Canonical signed bundle | Compiled output; includes payload hash |
| `INV` | Internal invariant register | Compiler invariants; INV-VERSION, INV-EVIDENCE-COMMIT, etc. |

---

## CORRECTED Q7: RUNTIME ACS COMPILATION COVERAGE

### Title
**Runtime ACS Compilation Coverage**

### Normative Definition (Corrected)

For every Approved Control Specification `d ∈ D` whose associated risk disposition is `Δ_i.status = 'runtime'`, verify that the compiled bundle `B` contains at least one predicate `p ∈ P` where:

- `p.origin_type = 'risk_derived'` (not a compiler invariant)
- `p.origin_id = d.risk_id` (traces back to the same risk)
- `p.acs_id = d.acs_id` (references this specific ACS)

**Violation:** A runtime ACS `d` for which `|{p ∈ P : p.acs_id = d.acs_id}| = 0`

### Manuscript Reference
- Section V, Contribution C1: "Every runtime ACS may produce zero, one or several predicates."
- 5.5d requirement: "Every runtime ACS must emit at least one predicate."
- Appendix B constraint 6: Every risk-derived predicate resolves to an ACS and risk

### Objects Involved
- `D` (Approved Control Specifications, from judgment record `J`)
- `Δ` (Dispositions)
- `P` (Predicates, from compiled bundle `B`)

### Expected Query Result on Conforming Artifact
Empty (all runtime ACS produce ≥ 1 predicate)

### SQL Implementation Concept
```sql
SELECT d.acs_id, d.risk_id
FROM acs d
JOIN disposition delta ON delta.risk_id = d.risk_id
WHERE delta.status = 'runtime'
  AND NOT EXISTS (
    SELECT 1
    FROM predicate p
    WHERE p.origin_type = 'risk_derived'
      AND p.acs_id = d.acs_id
  )
ORDER BY d.acs_id;
```

### Negative Fixture (Minimal Single Defect)

**Valid base:** One runtime ACS `d_valid` in `D`; at least one predicate `p_valid` with `p_valid.acs_id = d_valid.acs_id` in `B`.

**Mutation:** Remove all predicates from `B` whose `acs_id = d_valid.acs_id`, while keeping the ACS itself in `D` and its disposition as 'runtime'.

**Expected detection:** Q7 returns `d_valid.acs_id` (no predicates found).

### Non-redundancy vs. Q1-Q6
- Q2 checks that every risk has exactly one disposition
- Q3 checks that every predicate has a valid ACS origin
- **Q7 is the converse:** It checks that every approved runtime ACS actually produced a predicate (output completeness, not input completeness)

---

## CORRECTED Q8: GATE/PREDICATE REFERENCE INTEGRITY

### Title
**Gate/Predicate Reference Integrity**

### Normative Definition (Corrected)

Detect either:

**Part A:** An entry in the gate map `G` that references a predicate identifier absent from the compiled predicate set `P`.

**Part B:** A predicate `p ∈ P` designated as structurally decisive (meeting both criteria):
- `p.gate_type = 'mandatory'` (per Appendix A constraint 1: "mandatory implies on_fail = SAFE_STATE")
- `p.mandatory_role = 'decisive'` (per PAPER_REQUIREMENTS.md 5.1: "mandatory role ∈ {decisive, supporting}")

such that `p.gcir_id` does not appear in any entry of the gate map `G`.

**Violation (Part A):** A gate entry `g ∈ G` where `g.predicate_id ∉ {p.gcir_id : p ∈ P}`

**Violation (Part B):** A predicate `p` with `(gate_type='mandatory' AND mandatory_role='decisive')` where `p.gcir_id ∉ {g.predicate_id : g ∈ G}`

### Manuscript Reference
- Section VII-A, Proposition 1: "The gate set of every risk is reachable through the authority matrix and the C* profile or approved mandatory policy."
- Appendix A constraint 12: CV (Coverage rule): Every `C*` risk must have ≥1 mandatory gate covering each authorized hazardous action path

### Objects Involved
- `G` (Gate map, from compiled bundle `B`)
- `P` (Predicates, from compiled bundle `B`)

### Expected Query Result on Conforming Artifact
Empty (all gates reference existing predicates; all decisive predicates are gated)

### SQL Implementation Concept (Two Parts)

**Part A — Dangling gates:**
```sql
SELECT g.gate_id, g.predicate_id
FROM gate_map g
WHERE g.predicate_id NOT IN (SELECT gcir_id FROM predicate)
ORDER BY g.gate_id;
```

**Part B — Ungated mandatory predicates:**
```sql
SELECT p.gcir_id, p.origin_id
FROM predicate p
WHERE p.gate_type = 'mandatory'
  AND p.mandatory_role = 'decisive'
  AND p.gcir_id NOT IN (SELECT predicate_id FROM gate_map)
ORDER BY p.gcir_id;
```

### Negative Fixtures (Two Subfixtures, One per Part)

**Fixture A:** Add a gate-map entry `g_bad` where `g_bad.predicate_id = 'GCIR_NONEXISTENT'` and this predicate does not exist in `P`.

**Expected:** Q8 Part A returns `g_bad.gate_id`.

**Fixture B:** Add a predicate `p_bad` with `gate_type='mandatory'`, `mandatory_role='decisive'`, but do not add it to any gate-map entry.

**Expected:** Q8 Part B returns `p_bad.gcir_id`.

### Non-redundancy vs. Q1-Q6
- Q3 checks predicate origin (p → ACS → risk)
- **Q8 checks gate structural closure** (p → gate_map → decision path). This is distinct from origin validation.

---

## CORRECTED Q9: ACTUATION AUTHORITY VALIDITY

### Title
**Actuation Authority Validity**

### Normative Definition (Corrected)

For every recorded/attempted actuation `a` with an action tuple `(subject, action, resource, destination)` (per Section III-2), verify that this tuple resolves in the authority matrix `S.authority_matrix` **at the time applicable to the actuation's decision context** (either the effective authority matrix version associated with the valid bundle, or the system time if authority is versioned separately).

**Violation:** An action tuple whose four-element tuple does not exist in the applicable `S.authority_matrix`, or the matrix entry that would authorize it is not effective/valid at the relevant time.

### Manuscript Reference
- Section III, Step 2: "authority_matrix — actor × action × resource × destination. It is the closed vocabulary from which predicate subjects, actions, resources and destinations are drawn. *If an action does not appear in S.authority_matrix, no predicate can permit it.*"
- Appendix A constraint 5: "Every action tuple resolves to S.authority_matrix"
- **Note:** Q9 audits **runtime applicability**; the compiler (Φ) enforces authority at compile-time

### Objects Involved
- Actuation records (from evidence store or lifecycle evidence)
- Authority matrix `S.authority_matrix` (time-versioned if applicable)

### Expected Query Result on Conforming Artifact
Empty (all actuation action tuples are authorized)

### SQL Implementation Concept
```sql
-- Conceptual (requires authority_matrix to be versioned or time-bound in the evidence store)
SELECT a.actuation_id, a.subject, a.action, a.resource, a.destination
FROM actuation a
LEFT JOIN authority_matrix_view s ON (
    s.subject = a.subject
    AND s.action = a.action
    AND s.resource = a.resource
    AND s.destination = a.destination
    AND s.is_valid_at(a.decision_context_time)
)
WHERE s.authority_id IS NULL
ORDER BY a.actuation_id;
```

### Negative Fixture (Minimal Single Defect)

**Valid base:** An actuation whose (subject, action, resource, destination) tuple exists in `S.authority_matrix` and is valid.

**Mutation:** Change one component of the tuple (e.g., `destination`) to a value not in the authorized matrix, while keeping all other fields valid.

**Expected detection:** Q9 returns that actuation (tuple does not resolve).

### Critical Distinction from Q10

**Q9 = Authority only**

Q9 does NOT check:
- Evidence producer availability
- Evidence schema support
- `on_unknown` fail-closedness

**Q10 = Evidence only** (see below)

---

## CORRECTED Q10: MANDATORY PREDICATE EVIDENCE AND FAIL-CLOSED INTEGRITY

### Title
**Mandatory Evidence and Fail-Closed Integrity**

### Normative Definition (Corrected)

For every predicate `p ∈ P` with `(gate_type='mandatory' AND mandatory_role='decisive')`, verify all of the following:

**Constraint 1: Fail-closed condition**
- `p.on_unknown = 'fail'` (per Appendix A constraint 2: "mandatory implies every required condition has `on_unknown = fail`")

**Constraint 2: Evidence producer resolution**
- For each context condition in `p.context_conditions`, the `evidence_producer` field must resolve to a producer recognized in `S.authority_matrix` OR be an explicitly trusted external source per the approved policy

**Constraint 3: Evidence schema support**
- The `evidence_schema_ref` cited by `p` must exist and be supported (implementable) in the runtime evidence registry

**Constraint 4: Evidence freshness (if required)**
- If `p` includes a `temporal_window` or freshness requirement, the referenced evidence schema must support timestamp capture and the required freshness window must be enforceable

**Violation:** Any mandatory/decisive predicate that fails any of the four constraints above.

### Manuscript Reference
- Section V, Design commitment 1: "*For mandatory gates `on_unknown = fail` is required, not default.*"
- Appendix A constraint 2: "mandatory implies every required condition has `on_unknown = fail`"
- Section VI-C: "Required evidence producers must be resolvable"
- Section V, Design commitment 5: Evidence requirements are enforced

### Objects Involved
- Predicates `p ∈ P` (with `gate_type='mandatory'`)
- Authority matrix `S.authority_matrix` (for evidence producer resolution)
- Evidence schema registry (implementability check)
- Evidence freshness specifications

### Expected Query Result on Conforming Artifact
Empty (all mandatory predicates are fail-closed and have resolvable, supported evidence sources)

### SQL Implementation Concept (Violation Detection by Reason Code)

```sql
-- Q10a: Missing or non-fail-closed on_unknown
SELECT p.gcir_id, 'Q10_UNKNOWN_NOT_FAIL_CLOSED' as violation_code
FROM predicate p
WHERE p.gate_type = 'mandatory'
  AND p.mandatory_role = 'decisive'
  AND p.on_unknown != 'fail'
ORDER BY p.gcir_id;

-- Q10b: Evidence producer unresolved
SELECT p.gcir_id, 'Q10_PRODUCER_UNRESOLVED' as violation_code
FROM predicate p
WHERE p.gate_type = 'mandatory'
  AND p.mandatory_role = 'decisive'
  AND p.evidence_producer NOT IN (
    SELECT producer_id FROM evidence_producer_registry
  )
ORDER BY p.gcir_id;

-- Q10c: Evidence schema unsupported
SELECT p.gcir_id, 'Q10_SCHEMA_UNSUPPORTED' as violation_code
FROM predicate p
WHERE p.gate_type = 'mandatory'
  AND p.mandatory_role = 'decisive'
  AND p.evidence_schema_ref NOT IN (
    SELECT schema_id FROM evidence_schema_registry
  )
ORDER BY p.gcir_id;

-- Q10d: Freshness unenforceable
SELECT p.gcir_id, 'Q10_FRESHNESS_UNENFORCEABLE' as violation_code
FROM predicate p
WHERE p.gate_type = 'mandatory'
  AND p.mandatory_role = 'decisive'
  AND p.temporal_window IS NOT NULL
  AND NOT schema_supports_timestamp(p.evidence_schema_ref)
ORDER BY p.gcir_id;
```

### Negative Fixtures (Four Subfixtures, One per Constraint)

**Fixture Q10a:** Create a mandatory predicate with `on_unknown = 'warn'` or `'pass_with_approved_exception'`.

**Expected detection:** Q10a returns that predicate (not fail-closed).

**Fixture Q10b:** Create a mandatory predicate with `evidence_producer = 'unknown_service'` where this producer is not in the registry.

**Expected detection:** Q10b returns that predicate (producer unresolved).

**Fixture Q10c:** Create a mandatory predicate with `evidence_schema_ref = 'UNKNOWN_SCHEMA'` where this schema is not supported.

**Expected detection:** Q10c returns that predicate (schema unsupported).

**Fixture Q10d:** Create a mandatory predicate with `temporal_window = "not_older_than 1 hour"` but the referenced evidence schema does not support timestamps.

**Expected detection:** Q10d returns that predicate (freshness unenforceable).

### Critical Distinction from Q9

**Q10 = Evidence only**

Q10 does NOT check:
- Whether the action tuple is authorized (that's Q9)
- Signature validity (that's Q6 for lifecycle; Φ checks at compile time)

Q10 ONLY checks:
- Fail-closed condition (`on_unknown = fail`)
- Evidence producer availability
- Evidence schema support
- Freshness enforceability

---

## Q1-Q10 REDUNDANCY MATRIX

| Query | Primary responsibility | Objects checked | Does NOT duplicate |
|-------|------------------------|-----------------|-------------------|
| Q1 | Obligation → disposition link | O, R, Δ | Q2-Q10 |
| Q2 | Risk → exactly one disposition | R, Δ | Q1, Q3-Q10 |
| Q3 | Predicate → valid origin | P, R, INV, D | Q7, Q8, Q9, Q10 |
| Q4 | Receipt → valid bundle at decision | receipts, B, lifecycle | Q1-Q3, Q5-Q10 |
| Q5 | Actuation → prior ordered receipt | actuations, receipts | Q1-Q4, Q6-Q10 |
| Q6 | Lifecycle entry → valid signature | lifecycle, keys | Q1-Q5, Q7-Q10 |
| Q7 | **Runtime ACS → ≥1 predicate** | **D, Δ, P** | **Q1-Q6, Q8-Q10** |
| Q8 | **Gate ↔ predicate closure** | **G, P** | **Q1-Q7, Q9-Q10** |
| Q9 | **Actuation action tuple → authorized** | **a, S.authority** | **Q1-Q8, Q10** |
| Q10 | **Mandatory predicate → fail-closed + evidence** | **P (mandatory), S, schema** | **Q1-Q9** |

**Confirmation:** Each query has a distinct primary responsibility. Some negative fixtures may trigger multiple queries (e.g., Q10b might also trigger Q9 if the producer is not in the authority matrix), but the query definitions themselves are non-overlapping.

---

## OUTCOME SEMANTICS — FINAL DEFINITIONS

### PERMIT

**Definition:** A runtime predicate evaluation returns true, satisfying all required conditions under the valid governed bundle and authority context.

**Properties:**
- Terminal positive outcome
- May allow downstream externalization (subject to actuation rules)
- Requires all mandatory conditions to be satisfied with evidence
- Single, unambiguous state

**Manuscript reference:** Section VI-D (Precedence); Section VII-A (gate result).

---

### DENY

**Definition:** A runtime predicate evaluation returns false. At least one mandatory condition is known not to be satisfied.

**Properties:**
- Terminal non-permit decision
- No governed actuation
- Explicit failure: evidence exists, it contradicts the required state
- Externalization prohibited
- Fail-closed but NOT via missing evidence

**Distinction from HOLD:** DENY is **definitive** (evidence says "no"). HOLD is **indefinite** (evidence says "unknown").

**Manuscript reference:** Section V (Consequence-class gate coverage). Proposition 1, 2, 3 (gate structure).

---

### HOLD

**Definition:** A runtime decision cannot be made because required evidence is unknown, unavailable, stale, or indeterminate **AND the compiled escalation policy explicitly provides a hold/review mechanism.**

**Properties:**
- Non-permit decision
- Fail-closed (execution paused)
- No externalization
- Execution may later proceed via:
  - New valid evidence
  - Authorized escalation resolution (human review, alternative control path)
  - Supervisor override (if defined)
- Distinct from DENY: evidence is NOT available to make a decision

**Critical note:** Unknown evidence does **NOT automatically equal HOLD**. If no hold/escalation path is compiled, the actual fail-closed behavior (per constraint 1: `on_unknown = fail`) determines the outcome. A system without escalation routes defaults to DENY on unknown.

**Manuscript reference:** Section V, constraint 2 (on_unknown responses); Section VI-E (escalation map E).

---

### REJECT_AT_ISSUANCE

**Definition:** A candidate control specification (or bundle) fails an issuance-time prerequisite after governance refinement `Ψ_K` but before the bundle becomes a valid active issuable runtime artifact.

**Prerequisites that may trigger rejection:**
- Invalid approval/signature on the ACS or bundle
- Authority closure failure at issuance (the action tuple cannot be authorized even at that time)
- Mandatory C* coverage failure (CV violated)
- Other issuance-time structural invariant violation (per Appendix A constraints 1-14)

**Properties:**
- Pre-runtime; occurs during governance/approval phase
- No valid active bundle is issued
- No runtime permit can be produced
- Externalization prohibited
- Terminal; may require re-approval or redesign

**Manuscript reference:** Section VI (Compiler `Φ` steps); Appendix B (compilation steps 1-8).

---

### REJECT_AT_COMPILATION

**Definition:** The compiler `Φ` refuses to produce a valid compiled bundle because the supplied compilation inputs violate a compiler precondition or invariant (Appendix A constraints 1-14, or Section VI per-ACS steps 1-10).

**Examples of compilation rejection:**
- Malformed or unresolvable reference (e.g., risk_id not in R; acs_id not in D)
- Inconsistent field value (e.g., `on_fail != SAFE_STATE` on a mandatory gate)
- Unsupported required structure (e.g., numeric condition without threshold contract)
- Invalid catalog binding (event_type does not resolve to K)
- Authority closure violation at step 3 (action tuple not in S.authority_matrix)

**Properties:**
- Compiler-time; occurs before bundle is produced
- No valid bundle exists; compilation terminates
- No runtime execution possible
- Externalization prohibited
- Signals a specification/governance error that must be fixed before recompilation

**Manuscript reference:** Section VI, Appendix B (Compiler `Φ` specification); Appendix A (14 cross-field constraints).

---

### SAFE_STATE — Clarification

**Definition (Revised):** Not an exact outcome class. Rather, an **aggregated safety property**.

The following outcomes all satisfy **SAFE_STATE**:
- DENY (active policy rejection)
- HOLD (paused pending evidence/review)
- REJECT_AT_ISSUANCE (bundle not issued)
- REJECT_AT_COMPILATION (bundle not compiled)

**In this new semantics:**
- `SAFE_STATE` is a **secondary aggregate**, not a primary decision outcome
- Test assertions must specify the **exact outcome** (DENY vs. HOLD vs. rejection)
- Every scenario report must include:
  - **Exact outcome**: one of {PERMIT, DENY, HOLD, REJECT_AT_ISSUANCE, REJECT_AT_COMPILATION}
  - **Externalization**: false (for all non-PERMIT outcomes)

---

## Q1-Q10 SUMMARY TABLE (FINAL)

| Query | Type | Primary responsibility | Key objects | Outcome |
|-------|------|------------------------|-------------|---------|
| Q1 | Temporal | Obligation disposition link | O, Δ | Existing ✓ |
| Q2 | Temporal | Risk disposition totality | R, Δ | Existing ✓ |
| Q3 | Temporal | Predicate origin validity | P, R, INV | Existing ✓ |
| Q4 | Temporal | Receipt bundle validity | receipts, B | Existing ✓ |
| Q5 | Temporal | Actuation receipt ordering | actuations, receipts | Existing ✓ |
| Q6 | Temporal | Lifecycle signature validity | lifecycle, keys | Existing ✓ |
| **Q7** | **Structural** | **Runtime ACS compilation** | **D, Δ, P** | **NEW ✓** |
| **Q8** | **Structural** | **Gate/predicate closure** | **G, P** | **NEW ✓** |
| **Q9** | **Structural** | **Authority validity** | **a, S.authority** | **NEW ✓** |
| **Q10** | **Structural** | **Evidence integrity** | **P, S, schema** | **NEW ✓** |

---

## READY FOR NEXT PHASE

- ✅ Q7-Q10 notation corrected to match manuscript symbols
- ✅ Q9/Q10 overlap removed (Q9 authority only; Q10 evidence only)
- ✅ All four queries are non-redundant
- ✅ Outcome semantics fully defined (PERMIT, DENY, HOLD, REJECT_AT_ISSUANCE, REJECT_AT_COMPILATION)
- ✅ Manuscript amendment text prepared (to follow)

**Next step:** Map the 13 Case B scenarios to exact outcomes using these outcome definitions.

