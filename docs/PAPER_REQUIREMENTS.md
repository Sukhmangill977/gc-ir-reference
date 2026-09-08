# PAPER_REQUIREMENTS.md — Normative extraction from the manuscript

**Source of truth:** `From_Risk_Register_to_Runtime_Predicate_FINAL.docx`
(Abhinandan Gill-Lakhowal, "From Risk Register to Runtime Predicate: A Deterministic Method
for Compiling AI Governance Assessments into Enforceable Controls").

This file is a *requirements extraction*, not a summary. Every entry is a thing the reference
implementation must implement, validate, or measure. Section references are to the manuscript.

> **Status convention used throughout this repository**
> * `NORMATIVE` — stated by the paper as a requirement (`shall`, `must`, `requires`, `is required`).
> * `DESCRIPTIVE` — stated by the paper as an observation or design commitment.
> * `PROVISIONAL-NUMBER` — a numeric value printed in the manuscript that this artifact must
>   **re-measure**. Provisional numbers are never inputs to the implementation.
> * `FIXTURE` — a value the method requires but the manuscript does not state; supplied here as a
>   documented synthetic research fixture (see `FIXTURE_PROVENANCE.md`).

---

## 1. Contributions C1–C5 (Section I-C)

| ID | Contribution | Artifact obligation |
|----|--------------|---------------------|
| **C1** | Governed semantic refinement `Ψ_K`. Approved, versioned Control Derivation Catalog `K` constrains how each assessed risk may be refined into signed Approved Control Specifications. Every risk receives exactly one disposition. `Ψ_K` is a **relation** over the assessment, closed into a single-valued mapping only by a signed judgment record `J`: `(D, Δ) ∈ Ψ_K(𝒢)`, `Ψ_K(𝒢, J) → (D, Δ)`. Determinism is claimed only for what follows the boundary. | `src/gcir/refinement.py`, `src/gcir/catalog.py`; judgment-record schema; **no** inference from prose. |
| **C2** | GC-IR with total disposition. Record family covering compiled predicates and non-runtime / accepted / unresolved dispositions. Totality is a property of dispositions (exactly one per risk), never of predicate counts; one risk may yield 0, 1 or several predicates. | `src/gcir/models.py`, `schemas/gcir.schema.json`. |
| **C3** | Deterministic compilation `Φ` from signed refinement outputs to a canonically serialized (RFC 8785), hashed, signed, immutable predicate bundle: authority closure, explicit predicate origins, mandatory-gate unknown-failure enforcement, explicit precedence, lifecycle state in a separately signed registry. **No best-match, similarity or probabilistic rule selection inside Φ.** | `src/gcir/compiler.py`, `canonicalization.py`, `authority.py`, `lifecycle.py`. |
| **C4** | Consequence-class gate coverage, formalized, with Propositions 1–3. | `src/gcir/coverage.py`, `experiments/run_gate_divergence.py`. |
| **C5** | Temporally valid traceability: obligation/internal requirement → risk/disposition → ACS or compiler invariant → predicate → receipt, with decision-time validity and authorization→commit→actuation ordering. | `src/gcir/traceability.py`, `queries/traceability.sql`. |

## 2. Non-contributions / claim boundary (Sections I-D, XIV)

The paper explicitly does **not** claim:

1. Legal interpretation of any statute.
2. Automated determination of applicable obligations (Step 3 remains a human legal function).
3. Deterministic interpretation of unconstrained risk prose; that `Ψ_K` is a function of the assessment alone.
4. Detection capability.
5. Production deployment.
6. Comparative superiority over unaided manual practice (**RQ5 preregistered and deferred**).
7. That compilation eliminates the need for control validation (Step 7).
8. That every risk should become a runtime predicate.
9. That every possible risk-scoring method is compensatory.
10. That controls can never justify formal consequence reclassification.
11. That empty traceability queries prove substantive compliance, legal compliance, semantic correctness, or control effectiveness.
12. Orphan-control impossibility for policy injected through channels outside the runtime acceptance condition.
13. Independent certification (C3/C4 evidence classes), production effectiveness, detection capability, or real-world harm elimination.

**Claim classes (Section XI-I).** Only **C1** (author-operated measurement under declared conditions) and
**C2** (conformance run against a declared, versioned profile with reported bounds) may be asserted.
No C3 (independently verified) or C4 (consensus-bound) claim is made.

## 3. The five-step governance input model 𝒢 = (M, S, O, R, A) (Section III)

### Step 1 — Assessment metadata `M` — NORMATIVE
`M = (system_id, purpose, owner_business, owner_technical, accountable_exec, assessor, deployment,
scope, exclusions, method, version_binding, review_cycle, triggers)`

* `version_binding` — the exact model, prompt, dataset and policy versions the assessment covers.
  Compilation output inherits this binding; version drift invalidates the compiled control set by construction.
* `accountable_exec` — the party who accepts residual risk; **the accountable business authority**, never
  the developer, model vendor, or the AI-governance team that performed the assessment.
* **Constraint (enforced mechanically):** escalation routes and threshold approvals resolve to `M` ownership
  fields; *a bundle in which the assessor and the acceptor are the same identity fails structural validation.*
* `M.triggers` enumerates re-assessment forcing events: model version change, prompt or policy change,
  dataset refresh outside declared bounds, scope expansion, new obligation, catalog change,
  consequence-class reclassification, incident above a declared severity.
  A trigger firing **retires the bundle through the lifecycle registry**, it does not merely recommend review.

### Step 2 — System profile `S` — NORMATIVE
`S = (capabilities, data_classes, actors, affected_parties, authority_matrix, architecture, scale, autonomy_level)`

* `authority_matrix` — **actor × action × resource × destination**. It is the closed vocabulary from which
  predicate subjects, actions, resources and destinations are drawn.
  *If an action does not appear in `S.authority_matrix`, no predicate can permit it.*
  The matrix is both a governance artifact and the compiler symbol table.
* `autonomy_level` — records generative application vs. agent.
* Human review appearing in the authority matrix must be substantive; `human_attestation` tests only the
  presence and validity of the signed attestation artifact, and substantive-ness is monitored by a separate
  deterministic proxy (reviewer dwell/volume telemetry — Case A row R-12).

### Step 3 — Obligation matrix `O` — NORMATIVE
`O = {(obligation_id, source, jurisdiction, territorial_basis, clause_ref, requirement_text_hash,
applicability_basis, applicability_decision, decision_authority, decision_time, effective_from,
effective_until, legal_source_version, requirement_class)}`

* `requirement_class ∈ {statutory, supervisory, contractual, internal}` — closed vocabulary, used in gate selection.
* The method consumes `O` as ground truth and **never interprets legislation**.
* A later amendment to the legal source must be detectable as a hash or version mismatch.

### Step 4 — Risk register `R` — NORMATIVE
`r_i = (cause, event, consequence, affected_parties, obligation_refs ⊆ O, existing_controls, owner)`

* The **cause–event–consequence triple is mandatory**: it is what makes a register row refinable.

### Step 5 — Risk analysis `A` — NORMATIVE
`A = {(r_i, L_i^inh, I_i^inh, e_i, L_i^res, I_i^res, consequence_class_i, tier_i, treatment_i)}`

* Separates inherent risk, control effectiveness `e_i`, residual risk.
* Tiering/treatment/review priority driven by **residual** ratings.
* Where treatment is acceptance, the row carries acceptance authority (resolving to `M.accountable_exec`),
  scope and expiry consumed by `accepted(RA)`.
* Each row may declare a per-risk reopening trigger `ρ_i`.
* `consequence_class` is recorded **separately from any impact rating** and is the element ordinary control
  effectiveness does not move.

## 4. Governed semantic refinement `Ψ_K` (Section IV)

### 4.1 Refinement is a relation, not a function — NORMATIVE
`(D, Δ) ∈ Ψ_K(𝒢)`, with `Ψ_K(𝒢, J) → (D, Δ)` single-valued **given** `J`.
`J` is versioned, signed, and included in the authorized-origin chain.
`Ψ_K` is **not** a legal interpreter and does not infer requirements from unconstrained natural language.
Human governance authorities assign an approved `event_type`, select an allowed template from `K`,
complete the required control fields and sign; those signed acts are `J`.

The compiler is `Φ : (M, S, O, R, A, K, D, Δ) → (P, G, E, B)` where `P` is the predicate set, `G` the gate
map, `E` the escalation map, and `B` the canonical signed bundle.

### 4.2 Control Derivation Catalog `K` — NORMATIVE
`k_j = (event_type, observable_class, allowed_producers, triple_template, allowed_operators, value_schema,
evaluation_basis, evidence_schema, permitted_responses)`

* Approved by the governance forum, versioned with `M`, canonically serialized, **included in the compiled-bundle hash**.
* Addition, removal or semantic alteration of a catalog entry is a reassessment trigger.
* A register row whose approved `event_type` does not resolve to a catalog entry is **not interpreted
  heuristically**; it receives an `unresolved` or `nonruntime` disposition.

### 4.3 Approved Control Specification `d_ij` — NORMATIVE
`d_ij = (acs_id, risk_id, obligation_refs, event_type, observable_id, observable_producer, evidence_source,
subject, action, resource, destination, parameter_schema, operator, expected_value, temporal_window,
evaluation_basis, threshold_contract_ref, on_unknown, gate_candidate, mandatory_role, escalation,
evidence_requirements, control_owner, approver, approval_time, validity_interval)`

* `mandatory_role ∈ {decisive, supporting}`.
* Each ACS carries three express statements: **evidence semantics**, **decision semantics**, **warrant boundary**.

### 4.4 Total risk disposition — NORMATIVE
`Δ_i ∈ { runtime(D_i), nonruntime(C_i), accepted(RA_i), unresolved(U_i) }`

* **Totality:** `∀ r_i ∈ R, |Δ(r_i)| = 1`.
* **Release admissibility:** `∀ r_i ∈ R, Δ_i ≠ unresolved` **and** every acceptance is within its approved validity interval.
* Predicate cardinality is deliberately independent of risk cardinality (0, 1 or several predicates per risk).
* The implementation **shall assert** `|{Δ_i}| = |R|` and `∀ r_i, |Δ(r_i)| = 1`;
  it **shall not** assert `|P| + |X| = |R|` (Section VI-E).

### 4.5 Silent narrowing (Section IV-E) — DESCRIPTIVE + deferred measurement
`SN_i = 𝟙[ Q_i* \ Q_i ≠ ∅ ∧ no explicit residual or non-runtime disposition covers the difference ]`
where `Q_i*` is the adjudicated reference element set. **SNR is an RQ5 outcome — DEFERRED.**
The compiler warrants fidelity to the signed ACS, **not** completeness over the real-world hazard.

## 5. GC-IR record family (Section V, Appendix A)

`Record = CompiledPredicate ⊕ NonRuntimeDisposition ⊕ AcceptedRiskDisposition ⊕ UnresolvedDisposition (oneOf)`

A non-runtime / accepted / unresolved record **shall not be required** to contain subject, action, resource,
evaluation basis, or gate type.

### 5.1 CompiledPredicate required fields (Appendix A) — NORMATIVE
predicate ID and ACS ID; authorized origin type and origin ID; risk and obligation references; subject,
action, resource, destination; action-parameter schema; **at least one context condition**; evidence producer
and evidence schema; evaluation basis; gate type, gate source and mandatory role; on-fail and on-unknown;
escalation; evidence requirements; version and validity bindings (**`effective_from` only** — lifecycle state
is external).

### 5.2 Other record types (Appendix A) — NORMATIVE
* `NonRuntimeDisposition`: risk reference, reason code, routed-to control family, control reference, owner, approval record.
* `AcceptedRiskDisposition`: risk reference, scope, rationale, acceptor identity (resolving to `M.accountable_exec`), approval time, expiry.
* `UnresolvedDisposition`: risk reference, reason code, authority scope blocked from release.

### 5.3 Design commitments — NORMATIVE
1. **Every context condition declares `on_unknown`.** Indeterminacy is a named failure class distinct from
   violation. *For mandatory gates `on_unknown = fail` is required, not default.* For non-mandatory conditions
   any fail-open exception must be explicitly approved and carries the approver's identity.
2. `evaluation_basis ∈ {deterministic_lookup, threshold_on_measured_value, structural_check, human_attestation}`
   — **closed**. A GC-IR condition never evaluates a probability directly.
3. `gate_type ∈ {mandatory, weighted, advisory}`; `gate_source ∈ {C_STAR, OTHER_MANDATORY, SOFT}`.
   A `weighted` record is **structurally invalid** unless it carries `aggregation_group`, a positive weight
   `w_i`, a normalized deficit function `v_i`, a group threshold, and a response. A weighted group resolves to
   a single group-level deficit which enters the non-compensatory aggregate as one dimension.
4. **Every threshold ships with a threshold contract** carrying: operational definition, numerator,
   denominator, evidence source, ground truth, threshold rationale, uncertainty method, unit, reproduction
   procedure. Threshold authority is separated from evaluation.
5. **Non-runtime disposition is first-class**, with typed reason codes:
   * `RC-01` no per-action observable
   * `RC-02` no authority-matrix action
   * `RC-03` requires probabilistic judgment
   * `RC-05` consequence class undefined
   * `WC-01` unresolved obligation reference — a **warning code**, not a disposition.
   *(The manuscript's closed v1.0 set names RC-01, RC-02, RC-03, RC-05; RC-04 is not defined in the manuscript
   and is therefore reserved-unused here — see `FIXTURE_PROVENANCE.md` FP-013.)*
   Reason and warning codes are **closed at schema v1.0**; extension is a schema-version event.
6. **The hashed payload is immutable — lifecycle state lives outside it.**

## 6. Compiler `Φ` (Section VI, Appendix B)

### 6.1 Per-ACS steps — NORMATIVE (Section VI-A)
1. Verify signatures and version bindings of `M, S, O, R, A, K, D, Δ`.
2. Resolve `event_type` to **exactly one** approved catalog template.
3. Resolve `(subject, action, resource, destination)` against `S.authority_matrix`.
4. Validate action parameters against `parameter_schema`.
5. Validate evidence type and producer against the selected catalog entry.
6. Require a threshold contract for every numeric or temporal condition.
7. Assign gate source and gate type under Section VII.
8. Require `on_unknown = fail` for mandatory gates.
9. Bind escalation, evidence and validity requirements.
10. Emit the predicate and its authorized origin.

### 6.2 Bundle-level — NORMATIVE
* Verify the **C\* coverage requirement**; reject any bundle in which coverage fails.
* **No best-match, similarity, or probabilistic rule selection is permitted inside Φ.**

### 6.3 Predicate origins (Section VI-B) — NORMATIVE
`origin_type ∈ {risk_derived, compiler_invariant}`; invariants cite an approved invariant register `INV`
(e.g. `INV-VERSION`, `INV-EVIDENCE-COMMIT`, `INV-AUTHORITY-CLOSURE`).
**Traceability requirement:** `∀ p ∈ P, origin(p) ∈ R ∪ INV`.

### 6.4 Canonicalization and determinism (Section VI-C) — NORMATIVE
RFC 8785 JCS; UTF-8; canonical object-key ordering; deterministic array ordering where order is not
semantically meaningful; explicit numeric representations; explicit units; **no local time, locale, or
floating-point-environment dependencies; no timestamp or random nonce inside the hashed payload; no mutable
lifecycle field inside the hashed payload**.

`TD(x) = 𝟙[ H(C(Φ_e(x))) = H(C(Φ_{e′}(π(x)))) ]` — applies to the **canonical payload hash**.
*The signature envelope may include signing time, key identifier and certificate material and therefore is
**not required to be byte-identical** across signing events.*

### 6.5 Precedence (Section VI-D) — NORMATIVE
`mandatory failure ≻ mandatory pass ≻ weighted/advisory result`.
No weighted or advisory result may override a mandatory failure.
**Conflicts among applicable mandatory policies are themselves indeterminate and produce `SAFE_STATE`
unless a unique precedence relation is present in the approved policy metadata.**

### 6.6 Bundle lifecycle (Section VI-F) — NORMATIVE
`reg_entry = (bundle_hash, action ∈ {retire, supersede, revoke}, effective_time, authority, successor_hash?, signature)`
Retirement/supersession/revocation are **separately signed registry records**, never payload mutation.

**Runtime acceptance condition (Appendix A, constraint 14):** a conformant consuming runtime loads only
bundles verifying as signed `Φ` outputs (signature, payload hash, lifecycle-registry state), accepts no policy
content through any other channel, and emits decision receipts carrying the requirement reference
(`gcir_id`, `acs_id`, and origin) of every evaluated predicate.

### 6.7 Appendix A normative cross-field constraints — NORMATIVE (all 14)
| # | Constraint |
|---|-----------|
| 1 | `mandatory` implies `on_fail = SAFE_STATE`. |
| 2 | `mandatory` implies every required condition has `on_unknown = fail`. |
| 3 | Numeric or temporal operators require a threshold contract **and unit**. |
| 4 | `weighted` requires weight, normalized deficit function, aggregation group, and group threshold; the group resolves to a single group-level deficit at the enforcement boundary. |
| 5 | Every action tuple resolves to `S.authority_matrix`. |
| 6 | Every risk-derived predicate resolves to an ACS and risk. |
| 7 | Every compiler invariant resolves to an approved invariant ID in `INV`. |
| 8 | Every obligation reference resolves to `O`; an unresolved reference raises **`WC-01` (warning, not a disposition)**. |
| 9 | No expired approval may enter a release-admissible bundle. |
| 10 | **Assessor identity may not equal acceptor identity.** |
| 11 | An accepted-risk disposition's acceptor resolves to `M.accountable_exec`; its expiry does not exceed the assessment validity interval; no release-admissible bundle contains an acceptance already past expiry at compile time. |
| 12 | Every risk with `C*(c_i) = 1` has ≥1 mandatory gate (or mandatory gate set) covering **each** of its authorized hazardous action paths (**CV**). |
| 13 | The bundle payload contains **no timestamp, nonce, or mutable lifecycle field**; retirement and supersession resolve only through signed lifecycle-registry records. |
| 14 | Runtime acceptance condition (deployment conformance) — see 6.6. |

## 7. Consequence-class gate coverage (Section VII)

### 7.1 Descriptor and base profile — NORMATIVE
`c_i = (kind_i, materiality_i, reversibility_i, authority_i)`; `C*(c_i) ∈ {0,1}`.

Base profile used in the worked cases (**closed for v1.0**):
```
C* = { material_statutory_prohibition,
       unauthorized_authority_exercise,
       material_information_barrier_breach,
       irreversible_external_effect_above_approved_bound }
```
Materiality qualifies membership: an immaterial technical non-conformance does not enter `C*` merely because
its source is statutory. Each classification records approving authority, rationale, materiality boundary,
effective date, and any authorized emergency-override procedure.

`g_i^C = C*(c_i)`; final approved gate `g_i = g_i^C ∨ g_i^other`; `gate_source` keeps them distinguishable.
Contraction of `C*` within an active assessment is a trigger event requiring re-approval.

### 7.2 Coverage rule CV — NORMATIVE
For any risk `r_i` with `C*(c_i) = 1`, `D_i` must contain **at least one mandatory gate — or mandatory gate
set — covering each authorized hazardous action path associated with `r_i`, irrespective of L × I**.
A `C*` risk may in addition generate supporting advisory or weighted predicates (`mandatory_role` records
which are decisive and which are supporting). `Φ` verifies CV structurally and **rejects non-covering bundles**.
Heat-map score governs review priority, monitoring depth and treatment sequencing — **never gate membership**.

### 7.3 Gate divergence — NORMATIVE definitions
`s_i = L_i · I_i`; declared heat-map rule `h_{T_H}(i) = 𝟙[s_i ≥ T_H]`.
`GD(T_H) = Σ_i 𝟙[g_i ≠ h_{T_H}(i)]`
`GD_min = min_{t ∈ 𝒯} Σ_i 𝟙[g_i ≠ 𝟙[s_i ≥ t]]`, where `𝒯` contains the distinct observed scores **and
boundary values immediately above and below them**.
**Both sums run over all register rows, non-runtime dispositions included** (those rows carry ratings but no
gate; excluding them would understate divergence at low thresholds).

### 7.4 Propositions
* **Proposition 1 (threshold separation).** If `∃ r_i, r_j` with `s_i < s_j`, `g_i = 1`, `g_j = 0`, then no
  monotone threshold rule reproduces both assignments, and `GD_min ≥ 1`.
* **Proposition 2 (score-collision non-representability).** If `∃ r_i, r_j` with `s_i = s_j` and `g_i ≠ g_j`,
  then no rule that is a function of the scalar score alone reproduces the approved gate assignment.
* **Proposition 3 (qualified gate invariance).** Conditional on unchanged action model, consequence
  descriptor, `C*` definition, and approved mandatory-policy set, gate membership is invariant under changes
  to likelihood, impact, or ordinary control-effectiveness estimates.

### 7.5 Rating-sensitivity bound (Section VII-F) — explanatory only
`|s(z+δ) − s(z)| ≤ sup_ξ √(ξ_L² + ξ_I²) · ‖δ‖₂`. Explanatory because ratings are ordinal; empirical
robustness uses discrete Monte Carlo sampling.

### 7.6 Normalized non-compensatory evaluation (Section VII-G) — consumed, not re-proven
`d_i = v_i(m_i, θ_i) ≥ 0`; mandatory aggregate `Γ = max_i d_i`; `PERMIT ⇔ Γ = 0`.

### 7.7 Cumulative decision influence (Section VII-H) — stated, not proved, **not exercised by either case**
Disposition rule: declared input-provenance field on an already-classified consequential decision; residual is
an evidence-production exposure routed to `RC-03` / non-runtime.

## 8. Temporal traceability (Section VIII)

Chain: `(obligation or internal requirement) → risk/disposition → ACS or compiler invariant → predicate → receipt`.
An obligation that cannot be represented by a runtime predicate remains traceable through its approved
non-runtime or accepted-risk disposition. **Traceability completeness does not require every obligation to
produce a predicate.**

```
ValidAt(t, b, REG) = SignatureValid(t)
                   ∧ t.bundle_hash = H(b.payload)
                   ∧ b.effective_from ≤ t.decision_time
                   ∧ ¬Retired(REG, H(b.payload), t.decision_time)
```
`Retired(REG, h, τ)` holds iff `REG` contains a **validly signed** retirement, supersession, or revocation
record for `h` with `effective_time ≤ τ`.
*A historical receipt is not drift merely because its bundle is now retired.*

Temporal ordering — NORMATIVE:
`t.authorization_time ≤ t.evidence_commit_time < t.actuation_time`

### 8.1 The six audit queries — NORMATIVE
1. obligations without an approved disposition;
2. risks without exactly one disposition;
3. predicates without a risk or compiler-invariant origin;
4. receipts whose bundle was not valid at decision time (payload hash or registry state);
5. actuation records lacking a temporally prior committed receipt whose authorization time is not later than its commit time;
6. lifecycle-registry records lacking a valid signing authority.

Empty result sets demonstrate linkage and temporal-integrity completeness **under the declared data model**;
they do not establish legal compliance, semantic correctness, or control effectiveness.

## 9. Case A — investment research agent (Section IX) — **SYNTHETIC**

Profile: RAG summarizer over an approved research library; ~220 analysts, ~3,200 briefs/month; **draft-only
authority** (analyst approval required); no trading connectivity in scope; exclusions explicit.
Obligations (Canadian dealer): OSFI B-13 / E-21 / B-10 / E-23-readiness; CIRO Rule 3600 research supervision
with section-level citation (notably ss. 3608–3622); privacy statutes; securities / information-barrier requirements.

**16 register rows. Dispositions: 13 runtime, 3 non-runtime, 0 accepted, 0 unresolved.**
Rows R-01–R-14 correspond one-to-one to the fourteen-row source register; R-15 and R-16 are register
extensions added to exercise the remaining reason-code classes.

| risk_id | Event (phenomenon → approved observable) | consequence_class | L×I | Disposition / gate (source) | on_unknown |
|---|---|---|---|---|---|
| R-01 | hallucinated facts — typed claim object lacks resolving source hash | client_harm | 20 | runtime · mandatory (other) | fail |
| R-02 | citation failure — cited source ∉ approved library | client_harm | 16 | runtime · mandatory (other) | fail |
| R-03 | stale data — source timestamp > freshness bound | client_harm | 16 | runtime · mandatory (other) | fail |
| R-04 | biased framing — coverage skew metric > bound | conduct | 12 | runtime · **weighted + advisory** (no gate) | warn |
| R-05 | MNPI leakage — restricted-list match in context/output | **C\***: info-barrier (material) | 15 | runtime · mandatory (C\*) | fail + escalate |
| R-06 | missing conflict disclosures | **C\***: statutory (material) | 15 | runtime · mandatory (C\*) | fail |
| R-07 | prompt injection / poisoning | security | 15 | runtime · mandatory (other) | fail |
| R-08 | unauthorized publication — distribution without supervisor approval token | **C\***: authority | 15 | runtime · mandatory (C\*) | fail |
| R-09 | unauthorized recommendation | **C\***: authority | 12 | runtime · mandatory (C\*) | fail |
| R-10 | unauthorized trading — order-system call attempted | **C\***: irreversible | 10 | runtime · mandatory (C\*) | fail |
| R-11 | model/vendor change | governance (bundle validity) | 16 | runtime · mandatory (other; coincides with INV-VERSION) | fail |
| R-12 | weak oversight — reviewer dwell/volume outside band | governance | 12 | runtime · **advisory → monitoring** (no gate) | warn |
| R-13 | evidence failure — receipt chain gap | **C\***: statutory (material) | 10 | runtime · mandatory (C\*; coincides with INV-EVIDENCE-COMMIT) | fail |
| R-14 | concentration / resilience (single-vendor retrieval stack) | — | *(FIXTURE)* | **nonruntime · RC-01** | — |
| R-15 | unprofessional / reputationally damaging tone | — | *(FIXTURE)* | **nonruntime · RC-03** | — |
| R-16 | third-party model vendor commercial viability | — | *(FIXTURE)* | **nonruntime · RC-01** | — |

Manuscript notes to preserve: R-01 note (typed claim objects; RC-03 residual routed upstream), R-09 note
(structural test only; residual to R-12 monitoring), R-11 note (register row + `INV-VERSION` coincide; origin
metadata keeps the two authorizations distinct).

Manuscript's provisional Case A numbers (**all must be re-measured**):
`DC = 1`, `RCY = 13/16`, `GD(15) = 3`, `GD_min = 3`, `max Monte Carlo flip probability = 0.321`.
Note also `WC-01` and `RC-05` are exercised "in the machine-readable artifact's deliberately seeded validation
rows" — i.e. **outside** the release-admissible register.

## 10. Case B — transaction authorization agent (Section X) — **FORENSIC RECONSTRUCTION**

Per-transaction authorization agent; machine-speed decisioning; every proposed externalization (payment
release) mediated by the runtime authority; authority matrix admits **exactly one external action
(`release_payment`) with bound parameters**.

**6 register rows, all runtime, all mandatory (4 by C\*, 2 by other approved mandatory policy).**

| risk_id | Event (observable) | consequence_class | L×I | Gate (source) | on_unknown |
|---|---|---|---|---|---|
| B-01 | payment release without valid permit | **C\***: authority | 15 | mandatory (C\*) | fail |
| B-02 | amount > per-transaction limit | financial_loss | 16 | mandatory (other) | fail |
| B-03 | txn count/window > bound | financial_loss | 12 | mandatory (other) | fail |
| B-04 | counterparty ∈ restricted list | **C\***: statutory (material) | 5 (**L=1, I=5**) | mandatory (C\*) | fail + escalate |
| B-05 | permit reuse or duplicate txn hash | **C\***: irreversible | 10 | mandatory (C\*) | fail |
| B-06 | receipt not committed between authorization and actuation | **C\***: statutory (material) | 10 | mandatory (C\*; coincides with INV-EVIDENCE-COMMIT) | fail |

Because every row carries a mandatory gate, **any threshold `t ≤ 5` reproduces the gate set**, so Case B
contains no Proposition 1 inversion or Proposition 2 collision and `GD_min = 0`. Case B contributes
gate-source diversity, not separation evidence.

**Evidence classification (must be preserved verbatim in spirit):** the 284,807-event run reported in [15] is
a *golden-trace conformance result* — not detection evidence, and **not reproduced here**. The Case B register
is a **forensic reconstruction**; the mitigation is the hash-pinned artifact.

## 11. Metrics (Section XI-B) — all computed from artifacts, never hardcoded

| Metric | Definition |
|---|---|
| **DC** Disposition Completeness | `|{r_i : Δ_i ∈ (runtime, nonruntime, accepted)}| / |R|` |
| **RCY** Runtime Compilability Yield | `|{r_i : Δ_i = runtime(D_i)}| / |R|` — *descriptive, not a quality target* |
| **NDR** Non-Runtime Disposition Rate | `|{r_i : Δ_i ∈ (nonruntime, accepted)}| / |R|` — descriptive |
| **OPR** Orphan Predicate Rate | `|{p ∈ P : origin(p) ∉ R ∪ INV}| / |P|` — **required 0** |
| **ODC** Obligation Disposition Completeness | `|{o ∈ O : o ⇝ runtime ∨ nonruntime ∨ accepted}| / |O|` |
| **PTC** Predicate Traceability Completeness | `|{p ∈ P : p ⇝ risk ∨ compiler invariant}| / |P|` |
| **CV** C\* Coverage | `|{r_i : C*(c_i)=1 ∧ each hazardous action path mandatorily gated}| / |{r_i : C*(c_i)=1}|` — **required 1** |
| **TD** Translation Determinism | `Σ_k 𝟙[H_k = H_reference] / N` over environments and permutations |
| **GD** Gate Divergence | `GD(T_H)` with predeclared frozen `T_H`; and `GD_min` |
| **SNR** Silent-Narrowing Rate | RQ5 — **DEFERRED** |
| **DF** Field-Level Derivation Fidelity | `DF_i = |F_i ∩ F_i*| / |F_i*|` — RQ5 — **DEFERRED** |

## 12. Evaluation questions (Section XI-A)
* **RQ1** Total disposition.
* **RQ2** Determinism — same canonical payload hash across supported environments.
* **RQ3** Gate selection — divergence from the predeclared heat-map comparator; can any scalar threshold reproduce the approved assignment?
* **RQ4** Traceability — no orphan or temporally invalid links.
* **RQ5** Human translation quality — **preregistered, DEFERRED**. Not answered by this paper or this artifact.

## 13. Monte Carlo rating robustness (Section XI-G) — NORMATIVE spec
* Per risk, **discrete probability masses over plausible ratings**: `L_i^(k) ~ Cat(π_{L_i})`, `I_i^(k) ~ Cat(π_{I_i})`.
* `K ≥ 250,000` draws. `s_i^(k) = L_i^(k) I_i^(k)`, `h_i^(k) = 𝟙[s_i^(k) ≥ T_H]`.
* `FP_i^heat = (1/K) Σ_k 𝟙[h_i^(k) ≠ h_i^approved]`.
* **Conditional on unchanged consequence classification and policy version, `FP_i^{C*} = 0`.**
* Report: per-risk flip probability; expected gate changes per register; distributions of `GD(T_H)` and `GD_min`;
  `MCSE(p̂) = √(p̂(1−p̂)/K)`, bounded above by 0.001 at K = 250,000.
* **Manuscript attributes the rating distributions to "the independent panel". No panel exists. This artifact
  supplies author-specified synthetic sensitivity distributions and says so — see `FIXTURE_PROVENANCE.md` and
  `paper_update/MEASURED_RESULTS.md`.**

## 14. Determinism and adversarial testing (Section XI-H) — NORMATIVE list
TD testing includes: repeated runs; key and row reordering; equivalent numeric encodings rejected or
normalized per schema; locale and time-zone changes; supported operating systems or reproducible containers;
malformed references; duplicate IDs; conflicting predicates; expired approvals; stale catalog versions;
missing evidence producers; unknown consequence classes; unauthorized action triples; `C*` rows with missing
mandatory coverage; attempted in-place payload mutation (**must fail the hash check**); post-retirement bundle
use against the lifecycle registry.

Property-based tests verify: total disposition; authority closure; mandatory unknown-failure; `C*` coverage;
origin closure; payload immutability; temporal receipt validity.

Manuscript provisional: `TD = 1.000 over 31 compilation runs`. **This artifact targets ≥ 60 and re-measures.**

## 15. Preregistration (Section XI-I) — NORMATIVE
Publicly hash-committed **before execution**: hypotheses and primary outcomes; case artifacts and held-out
register hash; derivation catalog; adjudication instrument; thresholds and the `C*` definition; compiler commit
and container digest; randomization seed; Bayesian priors; Monte Carlo distributions and seed; exclusion and
missing-data rules; analysis code.

> "**The internal selection of frozen elements is not a freeze — the public timestamped commitment is.**"

RQ5 deferral is itself part of the preregistration. Recruitment rule (frozen): minimum 8 reviewers, continue to
12 if the 95% interval half-width for the primary agreement estimate exceeds 0.15 after 8.
Primary RQ5 outcomes: SNR, incorrect-gate rate, DC.

## 16. Limitations to preserve (Section XII)
Case A synthetic; Case B forensic reconstruction; single-author methodology risk; Step 3 human;
`C*` membership is a governance judgment; generality beyond financial services argued structurally;
authorization-soundness not semantic correctness; epistemic bounding; semantic-refinement dependence;
reference-standard uncertainty; catalog dependence; prevalence effects; ordinal-rating approximation;
Monte Carlo scope; temporal evidence dependence; comparative evidence deferred; scope of the
structural-impossibility claim; **determinism scope** (container-pinned; cross-host replication outstanding);
cumulative influence unevaluated.

## 17. Data & Code Availability + Appendix C — repository requirements
Release contains: GC-IR schema; `Ψ_K` tooling and `Φ` reference implementation; Control Derivation Catalog;
Steps 1–5 serialized inputs, signed judgment records, dispositions and ACS for Cases A and B; compiled bundles
and lifecycle-registry fixtures; coverage and temporal-validity queries; the adjudication instrument; and the
preregistration commitment (including the frozen RQ5 protocol).
The held-out expert-study register is **withheld until study close**.

**Hash manifest structure (Appendix C) — NORMATIVE.** One `MANIFEST.sha256` at release root listing, per file:
`path`, `SHA-256`, and `role ∈ {schema, catalog, psi_tooling, phi_impl, judgment_record_a, judgment_record_b,
case_a_input, case_b_input, dispositions_a, dispositions_b, acs_a, acs_b, compiled_bundle_a, compiled_bundle_b,
lifecycle_registry, queries, adjudication_instrument, prereg_commitment}`.
**The release tag and manifest hash together constitute the public preregistration commitment.**

MIT license for code and schema (per the precedent named in Appendix C).

## 18. Values printed in the manuscript that this artifact must re-measure (PROVISIONAL-NUMBER)
| Location | Manuscript value |
|---|---|
| Abstract; XI-B | `DC = 1.000` |
| XI-B | `RCY = 0.8125 (13/16)`, `NDR = 0.1875 (3/16)`, `OPR = 0.000`, `ODC = 1.000`, `PTC = 1.000`, `CV = 1.000` |
| Abstract; XI-B; XI-H | `TD = 1.000 (31/31 runs)` |
| Abstract; IX; XI-B | `GD(15) = 3`, `GD_min = 3` (Case A) |
| X; XI-B | Case B `GD_min = 0` |
| Abstract; XI-G | Monte Carlo max flip probability `0.321`; `FP^{C*} = 0.000` |
| IX | Case A disposition counts 13/3/0/0 |
| Appendix C | `[TO CONFIRM: final repository path]`, `[PENDING: hash-pinned Case B artifact release]`, `[PENDING: v1.0 freeze and $id host]` |
