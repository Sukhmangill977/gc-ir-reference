# Case B v1.1: Nine Approved Control Specifications — Rationale

**Status:** development artifact, not part of the frozen `preregister-tier0-v3.1`
campaign. `results/final_v3_1/` and the historical Case B (`cases/case_b/`,
hash `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce`, 6 ACS)
are **untouched** by this work.

## Revision of the prior session's finding

A prior pass over this repository's history (`docs/NINE_ACS_PROVENANCE_AUDIT.md`,
`docs/PHASE_1_GO_NO_GO_FINAL.md`, `paper_update/CASE_B_ACS_CARDINALITY_CORRECTION.md`)
concluded that no manuscript text justified splitting B-01 into three ACS
records, and the previous development-generation report (this repo, prior
session) followed that finding and kept Case B v1.1 at six ACS, enriched with
schema-v1.1 fields.

That conclusion is **revised** here after directly re-reading
`docs/paperieee2 (1).pdf` Section X (the paper actually supplied for this
generation, distinct from whatever earlier manuscript draft the prior audits
examined). That section's Table II and its accompanying prose state, in exact,
quotable, machine-checkable form, that B-01 and B-02 compile from three and
two Approved Control Specifications respectively:

> "Under Ψ_K the requirement yields two structured controls that the DENY/HOLD
> distinction of Section V exists to keep apart:
> `# ACS-B01-02 (PROHIBIT -> DENY) subject = TRANSACTION; action = RELEASE_TRANSACTION
> condition: risk_class != PROHIBITED (deterministic_lookup, active policy)
> on_fail = DENY; on_unknown = HOLD`
> `# ACS-B01-03 (REQUIRE -> HOLD) subject = TRANSACTION; action = RELEASE_TRANSACTION
> condition: enhanced_approval_present where risk_class == ENHANCED_APPROVAL_REQUIRED
> (human_attestation; concurrence_policy per approval tier)
> on_fail = DENY; on_unknown = HOLD -> escalation: verification workflow`"
> — Section X

> "ACS-B01-01: valid single-use permit, state-bound to (transaction hash,
> amount, beneficiary, account status, token status)" — Table II

> "two specifications: ACS-B02-01 (hard authority ceiling) amount ≤ absolute
> authority ceiling, on_fail = DENY; ACS-B02-02 (delegated escalation
> threshold) amount ≤ ordinary_limit ∨ additional approval established;
> on_fail = DENY (approval denied or concurrence window expired), on_unknown =
> HOLD (approval pending or unavailable) → additional-authorization route,
> PERMIT once established (threshold contracts on both bounds)" — Table II

This is not an inference from prose sentiment; it is a literal specification
table with field-level `condition`, `on_fail`, and `on_unknown` values already
written out. `docs/NINE_ACS_PROVENANCE_AUDIT.md`'s finding was correct for the
manuscript text it examined; it does not survive contact with this Table II.

## The nine records, with full provenance

| # | acs_id | risk_id | Source (exact) | Distinct semantics | Why not foldable into an existing ACS |
|---|---|---|---|---|---|
| 1 | ACS-B01-01 | B-01 | Table II, "ACS-B01-01: valid single-use permit, state-bound to..." | Structural check that a signed permit is valid and bound (state_binding) to the five-attribute transaction tuple. | Baseline; pre-existing. |
| 2 | ACS-B01-02 | B-01 | Section X, "# ACS-B01-02 (PROHIBIT -> DENY)" | Deterministic lookup against the **active risk-classification policy**: is this transaction's `risk_class` a known-prohibited class? Evidence source is a policy/classification service, not the permit artifact. | A valid, correctly-bound permit (ACS-B01-01 passes) says nothing about whether the classified risk itself is prohibited — these are independent evidence sources evaluated by different services, and the manuscript deliberately keeps DENY (known prohibition) distinct from HOLD (unresolved permit state), which collapsing them would erase. |
| 3 | ACS-B01-03 | B-01 | Section X, "# ACS-B01-03 (REQUIRE -> HOLD)" | `human_attestation` evaluation basis with a schema-v1.1 `concurrence_policy` (a v1.0 ACS literally could not express this — no concurrence mechanism existed) gating releases whose risk class requires enhanced approval. | Requires evidence of a *human decision*, not a structural or policy-lookup fact; the paper explicitly built this as a `REQUIRE -> HOLD` control distinct from the `PROHIBIT -> DENY` one at #2, and distinct again from #1's permit-binding check, because each is a different failure mode with a different owning service. |
| 4 | ACS-B02-01 | B-02 | Table II, "ACS-B02-01 (hard authority ceiling)" | Numeric threshold: `amount <= absolute_ceiling`. Pure DENY on breach — an absolute bound has no escalation path. | Baseline; pre-existing (unchanged from the historical six-ACS design). |
| 5 | ACS-B02-02 | B-02 | Table II, "ACS-B02-02 (delegated escalation threshold)" | A disjunctive escalation-tier check (`amount <= ordinary_limit OR additional_approval_established`), evaluated via `human_attestation` + `concurrence_policy` (again unrepresentable before schema v1.1) with its own DENY-on-expiry / HOLD-on-pending semantics distinct from #4's unconditional numeric ceiling. | #4 is a hard, non-negotiable ceiling with no escalation route by design (Table III: "DENY above absolute ceiling"); #5 governs the band *below* that ceiling but *above* the ordinary limit, where an escalation path exists. Merging them would either remove the absolute ceiling's unconditional DENY or add a spurious escalation path to it. |
| 6 | ACS-B03-01 | B-03 | Unchanged | Velocity/window bound. | Baseline; pre-existing. |
| 7 | ACS-B04-01 | B-04 | Unchanged | Restricted-party screening. | Baseline; pre-existing. |
| 8 | ACS-B05-01 | B-05 | Unchanged | Single-use/replay check. | Baseline; pre-existing. |
| 9 | ACS-B06-01 | B-06 | Unchanged | Receipt-chain completeness. | Baseline; pre-existing. |

Every new record (#2, #3, #5) is signed under a **new judgment-record
selection and approval** in `cases/case_b_v1_1/judgment/judgment_record.json`
(selector, rationale, approver, approval time) — the same governed-refinement
provenance every other ACS in this repository carries, not a schema
short-cut.

## Consequence: predicate and disposition counts

Disposition count is **unchanged at 6** (one per risk — `Disposition.acs_ids`
is a list, and B-01's single `RuntimeDisposition` record now names three
`acs_ids`; B-02's names two). This is exactly the mechanism Section IV-D
describes: *"Predicate cardinality remains independent of risk cardinality: a
risk may yield zero, one, or several predicates without violating total
disposition."*

ACS count is **9** (not 6). Because this compiler's Φ implementation compiles
exactly one `CompiledPredicate` per ACS (`gcir.compiler._instantiate_predicates`
returns one record per call, by construction — "one ACS yields one compiled
predicate," Section VI-A), **risk-derived predicate count is 9, not 6**. The
frozen v3.1 Case B bundle's own stated "6 risk-derived + 3 invariant = 9
total" is therefore specific to the *six-ACS* fixture that bundle was actually
compiled from — it is not evidence that a nine-ACS Case B must also total 9
predicates. This report states the new counts as measured, not as forced to
match either the paper's summary sentence or the frozen bundle's:

```
ACS records:              9
Risk-derived predicates:  9
Compiler invariants:      3
Total predicates:        12
```

## What did not change

- Historical `cases/case_b/` (6 ACS), `preregister-tier0-v3.1`, and
  `results/final_v3_1/` are untouched.
- The six risks, their obligations, their consequence classifications, and
  the authority matrix are identical to the historical Case B.
- C\* classification remains per-risk (four C\*-classified risks: B-01, B-04,
  B-05, B-06; two other-mandatory: B-02, B-03) — unchanged by adding ACS
  records to already-classified risks.
