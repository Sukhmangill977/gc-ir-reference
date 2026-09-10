# AUDIT_QUERY_5_5D_MANUSCRIPT_AMENDMENT.md

**Purpose:** Manuscript amendment showing how Section VIII should be revised to include all 10 audit queries with complete normative definitions.

**Status:** DESIGN PHASE — awaiting author approval

---

## MANUSCRIPT SECTION VIII AMENDMENT

### BEFORE (Current manuscript, Section VIII)

The current manuscript states:

> "Section VIII: Traceability
>
> The reference implementation ships with a suite of audit queries over the compiled
> evidence store and the wrapped governance inputs. An artifact that produces empty
> result sets for all queries demonstrates the five-step governance input model and
> the compiler invariants in isolation."

The current implementation defines SIX queries (Q1-Q6) in the released `queries/traceability.sql`.

---

### AFTER (Proposed 5.5d revision, Section VIII)

**Proposed replacement:**

> "Section VIII: Complete Traceability and Structural Integrity Audit
>
> The reference implementation ships with a comprehensive audit suite of ten queries
> over the compiled evidence store and the wrapped governance inputs.  These queries
> partition into two categories:
>
> **Temporal Traceability Queries (Q1-Q6)** verify that the five-step governance
> model and temporal-ordering constraints are satisfied:
>
> - **Q1: Obligations without an approved disposition** (Section IV-C)
>   For each obligation o ∈ O, at least one risk r ∈ R that references o must receive
>   a disposition with status ∈ {runtime, nonruntime, accepted}. This query detects
>   any obligation that is unlinked or all of whose disposing risks are unresolved.
>
> - **Q2: Risks without exactly one disposition** (Section IV-D)
>   Every risk r ∈ R must receive exactly one disposition δ ∈ Δ. This query detects
>   risks with zero dispositions or with multiple (conflicting) dispositions.
>
> - **Q3: Predicates without a risk or compiler-invariant origin** (Section VI-B)
>   Every compiled predicate p ∈ P must have a valid origin: either a risk r ∈ R
>   whose approved ACS set (in judgment record J) includes p.acs_id, or an internal
>   invariant inv ∈ INV with p.origin_id = inv.invariant_id. This query detects
>   orphan predicates.
>
> - **Q4: Receipts whose bundle was not valid at decision time** (Section VI-F)
>   For each receipt t ∈ evidence.receipts, the bundle B it references must satisfy:
>   its canonical hash must bind, its effective_from must precede t.decision_time, and
>   no lifecycle registry entry must retire it before t.decision_time. This query
>   detects bundles that are invalid, not yet effective, or superseded.
>
> - **Q5: Actuation without a temporally prior committed receipt** (Section VIII, Contribution C5)
>   For each actuation a ∈ evidence.actuations, a receipt t must exist with
>   authorization_time ≤ evidence_commit_time < actuation_time. This query detects
>   actuations with missing, out-of-order, or temporally inverted receipts.
>
> - **Q6: Lifecycle-registry records lacking a valid signing authority** (Section VI-F)
>   Every lifecycle registry entry l ∈ REG must be signed by an authorized signing
>   authority, and the signature must verify. This query detects unsigned, forged, or
>   unauthorized registry entries.
>
> **Structural Integrity Queries (Q7-Q10)** verify that the compiled artifact exhibits
> the structural completeness and reference closure required by the compiler design:
>
> - **Q7: Runtime ACS with zero emitted predicates** (Section V, 5.5d clarification)
>   Every approved control specification acs ∈ Δ with disposition status = 'runtime'
>   must compile to at least one predicate p ∈ P where p.origin_type = 'risk_derived'
>   and p.acs_id = acs.acs_id. This query detects approved runtime controls that did
>   not produce any executable predicate (a compiler defect or missing catalog
>   resolution).
>
> - **Q8: Gate/predicate reference integrity** (Section VII-A, Proposition 1)
>   Every gate-map entry must reference a predicate that exists in P. Conversely,
>   every predicate p ∈ P with mandatory_role = 'decisive' (a mandatory gate) must
>   appear in at least one gate-map entry. This query detects gates that reference
>   non-existent predicates, or decisive predicates that were compiled but not gated.
>
> - **Q9: Actuation authority validity** (Section III-2, runtime instantiation)
>   For each actuation a, the action tuple (subject, action, resource, destination)
>   must resolve in the authority matrix S.authority_matrix at the time of
>   a.actuation_time. Additionally, every evidence producer cited by a predicate used
>   in the actuation must be resolvable in S. This query detects actuations whose
>   actions are not authorized, or whose evidence producers are not recognized, at
>   runtime.
>
> - **Q10: Mandatory predicate evidence integrity** (Section V and VI-C)
>   Every predicate p with mandatory_role = 'decisive' must have on_unknown = 'fail'
>   (fail-closed for missing evidence). Additionally, every evidence producer named
>   in p's context conditions must be resolvable in S.authority_matrix or explicitly
>   trusted by policy, and the evidence schema must support the required freshness
>   constraints. This query detects mandatory predicates that are not fail-closed, or
>   that depend on unavailable or unsupported evidence sources.
>
> **Query semantics:** An artifact that produces empty result sets for all ten queries
> Q1-Q10 demonstrates:
> (1) Five-step governance input model completeness (Q1-Q2)
> (2) Explicit predicate lineage (Q3)
> (3) Temporal traceability and ordering (Q4-Q6)
> (4) Compilation output completeness (Q7-Q8)
> (5) Authority closure and evidence availability at runtime (Q9-Q10)
>
> Empty result sets do not establish legal compliance, semantic correctness, or
> control effectiveness (see Section XIV, claim boundary)."

---

## CHANGE JUSTIFICATION

### Why Q7 (Runtime ACS emission)

**Motivation:** Manuscript 5.5d refines the prior statement "every ACS may produce zero, one, or several predicates" to require "every runtime ACS must emit at least one predicate." This is a compliance clarification, not a design change. Q7 audits this requirement.

**Architectural reason:** A runtime ACS that compiles to zero predicates is useless—either a compiler bug, a catalog gap, or a missing approval decision. Q7 catches this.

### Why Q8 (Gate/predicate closure)

**Motivation:** The compiler and the paper establish that every risk must be gated (Section VII-A, Proposition 1). However, the temporal queries (Q1-Q6) do not check that gates actually exist and close properly in the compiled bundle. A predicate could be risk-derived (passing Q3) but never appear in any gate-map entry. Conversely, a gate could reference a non-existent predicate (a compiler bug).

**Architectural reason:** Q8 is a structural complement to Q3 (which checks origins) and Q1-Q2 (which check disposition).

### Why Q9 (Actuation authority)

**Motivation:** The compiler enforces authority at compile-time (Appendix A constraint 5). However, the authority matrix may change between compilation and runtime (roles revoked, subjects removed). Q9 verifies that every actuation is still authorized at its actual time.

**Architectural reason:** Governance policies evolve. An action authorized at approval time may become unauthorized later. Q9 catches this drift.

### Why Q10 (Mandatory evidence integrity)

**Motivation:** A mandatory gate with on_unknown ≠ 'fail' is not fail-closed—it allows decisions to proceed with missing evidence. A mandatory predicate that depends on an unavailable or unsupported evidence source cannot execute. Q10 catches both.

**Architectural reason:** Mandatory predicates are the enforcement backbone. They must be fail-closed and operationally available.

---

## SECTION-BY-SECTION MAPPING

### Q1-Q6 (unchanged)

These are tied to existing manuscript sections and requirements:

| Query | Manuscript section | Requirement |
|-------|--------------------|-------------|
| Q1 | IV-C | Obligations must be dispositioned |
| Q2 | IV-D, C2 | Every risk receives exactly one disposition |
| Q3 | VI-B | Predicates must have valid origins |
| Q4 | VI-F | Receipts must have valid bundles |
| Q5 | VIII, C5 | Temporal ordering: auth ≤ commit < actuation |
| Q6 | VI-F | Lifecycle entries must be signed |

### Q7-Q10 (new)

These close gaps implied by existing architecture:

| Query | Manuscript section | Requirement |
|-------|--------------------|-------------|
| Q7 | V, 5.5d | Every runtime ACS must emit ≥ 1 predicate |
| Q8 | VII-A, P1 | Gates must close properly; predicates must be gated |
| Q9 | III-2 | Actions must be authorized at actuation time |
| Q10 | V, VI-C | Mandatory predicates must be fail-closed and operational |

---

## IMPLEMENTATION CHECKLIST (for reference implementation)

Once the author approves Q7-Q10, the following artifacts must be updated:

- [ ] `queries/traceability.sql` — expand from 6 to 10 query definitions
- [ ] `src/gcir/traceability.py` — implement Q7-Q10 query logic
- [ ] `cases/case_a/negative_fixtures/Q7_*.json` ... `cases/case_a/negative_fixtures/Q10_*.json` — create negative fixtures
- [ ] `cases/case_b/negative_fixtures/Q7_*.json` ... `cases/case_b/negative_fixtures/Q10_*.json` — create negative fixtures
- [ ] `tests/integration/test_audit_query_negative_controls.py` — test all Q1-Q10 fixtures
- [ ] `experiments/run_audit_queries.py` — run all 10 queries in the final campaign
- [ ] `results/final_v3/traceability_queries.json` — results for all 10 queries
- [ ] `tools/verify_reported_results.py` — verify 10/10 empty results in final artifact
- [ ] README / `make results` — display all 10 query results

---

## CLAIM BOUNDARY VERIFICATION

Q7-Q10 remain **internal consistency checks**. They do not introduce new research claims about:

- ✓ Detection performance (not claimed)
- ✓ Production deployment (not claimed)
- ✓ Legal compliance (not claimed; claim boundary in Section XIV unchanged)
- ✓ Comparative superiority (RQ5 remains deferred)
- ✓ Real-world harm prevention (not claimed)

Q7-Q10 are **auditing**, not **empirical measurement**.

---

## NEXT STEP

**Author approval is required.**

Once approved, Q7-Q10 are locked into the specification, and Phase 1 implementation can begin:

1. Update `queries/traceability.sql` with Q7-Q10 SQL definitions
2. Create negative fixtures for Q1-Q10
3. Implement test suite
4. Run final_v3 campaign with all 10 queries
5. Commit new scientific freeze (preregister-tier0-v3)
6. Release v1.0.4 with audited 10-query suite

