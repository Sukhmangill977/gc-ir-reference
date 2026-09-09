# FINAL_CLAIM_EVIDENCE_AUDIT.md

Every substantive claim in `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx`
mapped to the evidence that supports it, and classified.

**Classification.**

| Class | Meaning |
|---|---|
| **C1** | Proved. A mathematical statement with a proof in the paper. |
| **C2** | Measured. A number produced by the released artifact and reproducible from it. |
| **C3** | Argued. A design or positioning claim supported by construction and reasoning, not measurement. |
| **C4** | Deferred. Stated as future or committed work; **no result is claimed**. |

**Rule applied throughout:** a claim may not be stated at a higher class than its
evidence supports. Where the manuscript previously did so, it was corrected — the
corrections are listed in `FINAL_MANUSCRIPT_CHANGELOG.md` and cross-referenced below.

---

## C1 — Proved

| # | Claim | Where | Evidence | Status |
|---|---|---|---|---|
| 1 | No monotone likelihood × impact threshold reproduces the approved gate assignment on a register containing a score inversion. | Prop. 1, §VII | Proof in §VII; premise instantiated on Case A (R-10 at s = 10 gated, R-04/R-12 at s = 12 ungated) | **Holds.** Premise verified mechanically: `results/final_v2/gate_divergence.json` → `proposition_1` |
| 2 | No function of the scalar score alone expresses class-dependent gating when equal scores carry divergent gates. | Prop. 2, §VII | Proof in §VII; premise instantiated by the s = 12 collision | **Holds.** `results/final_v2/gate_divergence.json` → `proposition_2`. Text corrected: the collision is described as being *among the runtime rows*, because non-runtime row R-14 also rates 12 (edit E05/E07). |
| 3 | Gate membership is invariant under rating and control-effectiveness change conditional on unchanged consequence classification. | Prop. 3, §VII | Proof in §VII; corroborated, not established, by the Monte Carlo FP^C* = 0.000 result | **Holds.** Corroboration is labelled as such. |
| 4 | DC = 1 by construction once dispositions are signed. | §IX | Constraint 4 (Appendix A) + signed dispositions | **Holds.** Stated as by-construction, not as a measurement, and measured DC = 1.000 agrees. |

## C2 — Measured

Every value below is produced by `results/final_v2/`, reproducible with
`python tools/freeze_check.py --final-v2`, and reproduced identically by two
independently executed campaigns (`results/V1_V2_COMPARISON.md`).

| # | Claim | Value | Evidence file |
|---|---|---|---|
| 5 | Total disposition on both cases | DC = 1.000 (A 16/16, B 6/6) | `metrics.json` |
| 6 | Zero orphan predicates | OPR = 0.000 (A 0/19, B 0/9) | `metrics.json` |
| 7 | Complete obligation and predicate traceability | ODC = 1.000, PTC = 1.000 both cases | `metrics.json` |
| 8 | Full consequence-class coverage | CV = 1.000 (A 6/6, B 4/4) | `metrics.json` |
| 9 | Runtime-conversion and non-derivation rates (descriptive) | A: RCY 0.8125, NDR 0.1875; B: 1.000 / 0.000 | `metrics.json` |
| 10 | Translation determinism | TD = 1.000 over 62 runs, 31 per case | `determinism_summary.json`, `determinism_runs.csv` |
| 11 | Determinism reproduced across environments | 8 environments; 3 operating systems; 2 architectures; 6 CPython patch versions; identical canonical payload hashes | `CI_STATUS.md`, CI run 34261657261 |
| 12 | Gate divergence | A: GD(15) = 3, GD_min = 3; B: GD(15) = 4, GD_min = 0 | `gate_divergence.json` |
| 13 | Heat-map gate instability under perturbation | max FP^heat = 0.321 (MCSE 0.001); 3.64 expected changes per register | `monte_carlo_summary.json` |
| 14 | Consequence-class stability under perturbation | FP^C* = 0.000; 0/1000 verified draws changed C* membership | `monte_carlo_summary.json` |
| 15 | Adversarial rejection | 62/62 (54 negative, 8 positive); 26 structural; 3 seeds — each rejected with the predicted error code | `adversarial.json` |
| 16 | Case B injection resilience | 13/13 scenarios resolve to SAFE_STATE | `adversarial.json` → `case_b_injection_scenarios` |
| 17 | Test and property coverage | 280 tests, 16 properties, 1 427 generated examples | `property_tests.json` |
| 18 | Traceability audit | 6 audit queries empty; 18/18 negative controls fire | `traceability_queries.json` |
| 19 | Case artifacts pinned | A `f5cbc3a8…a43536`, B `2850155a…aa33ce` | `cases/*/expected/reference_hashes.json` |
| 20 | Public preregistration discharged | tag `preregister-tier0-v2.2` @ `c44f25d6…`, 133 files, pushed **before** execution | `PROVENANCE.json`, `freeze_verification.json` |
| 21 | GD_min sensitivity to fixture ratings | GD_min ∈ [2, 5] over all plausible (L, I) for the three fixture rows | `gate_divergence.json` → `case_a_fixture_rating_sensitivity` |

**Claim 11 boundary.** The manuscript says *"determinism across the tested supported
environments"* and states explicitly that this is **not** platform independence. Edits
E01, E17 and E20 removed the prior "environment-independent" phrasing from the abstract,
the limitations section and the conclusion.

**Claim 13/14 boundary.** The perturbation distributions are **author-specified and
prospectively frozen**, not panel-adjudicated. Edits E03, E12, E13 and E18 make this
explicit in the abstract, §XI-C, §XI-G and §XII. No result is attributed to a panel.

## C3 — Argued

| # | Claim | Where | Basis |
|---|---|---|---|
| 22 | The translation step between governance frameworks and runtime enforcement is undocumented as a *method*. | §I, §II-F | Literature sweep, `LITERATURE_VERIFICATION.md`. **Narrowed:** §II-F now cites two adjacent works [28], [29] and states the position as a five-property combination rather than as absence of prior art. |
| 23 | Ψ_K is a relation closed to a mapping only by a signed judgment record; human interpretation is never claimed deterministic. | §V | Construction. Enforced by the schema and by adversarial cases. |
| 24 | Φ contains no LLM, embedding, similarity or randomness. | §VI | Construction; verifiable by reading the released implementation. |
| 25 | The compiler orphan-control guarantee extends to deployment only under an explicit runtime acceptance condition. | §VI, App. A | Construction; the conditional is stated, not elided. |
| 26 | The method is separable from, and does not restate, the consuming enforcement architecture [15]. | §XIII | Checked at submission against the released artifact (edit E19); `docs/CASE_B_LDREA_TRACEABILITY.md`. |
| 27 | Case B's predicate set continues the enforcement artifact's own predicate family. | §X | **Machine-verified mapping**, 9 rows: 4 exact, 3 family, 2 declared gaps. `cases/case_b/ldrea_traceability.json`. Stated as continuity of predicate family only — explicitly *not* detection evidence. |

## C4 — Deferred (no result claimed)

| # | Item | Where | Status |
|---|---|---|---|
| 28 | Comparative expert study (RQ5) | §XI-C, §XI-B, §XV | Preregistered, publicly hash-committed, **not executed**. No participant data exists. SNR and DF report *"primary outcome of the deferred comparative study; not reported here"* (edit E11). |
| 29 | Independent three-person adjudication panel | §XI-C | **Not convened.** Edit E12 changed the present tense to the conditional and states that no adjudicated reference standard exists. |
| 30 | Held-out register | §XI-I | Not authored; committed in a Tier-1 freeze before recruitment opens (edit E16). The Tier-0 freeze does **not** contain a held-out-register hash, and no longer claims to. |
| 31 | Shadow-mode deployment | §XV | Named as future work for a subsequent paper. |
| 32 | Archival deposit with a persistent identifier | Data & Code Availability | **Pending. No DOI is cited** (edit E22). See `ZENODO_AND_DOI_INSERTION_POINTS.md`. |

---

## Claims explicitly NOT made — verified absent

Each was searched for in the output document. All counts are zero unless noted.

| Forbidden claim | Result |
|---|---|
| Detection performance / precision / recall for the compiled bundles | Absent. The three textual matches for detection language are all **disclaimers** (§I-D non-contributions, §X evidence classification, §XI downstream-interface scope). |
| Production deployment evidence | Absent; named as a non-contribution in §I-D. |
| Independent or third-party validation | Absent. |
| Human panel involvement in any reported result | Absent after edits E12/E13. |
| Platform independence | Absent. The single textual match is the sentence **denying** it (§XII). |
| Held-out study results | Absent. |
| A DOI for this artifact | Absent. The two DOI matches are the author's prior theory paper [16], a pre-existing and legitimate citation. |
| Comparative superiority over human analysts | Absent; §XI-B, §XI-C and the abstract all state the study is deferred. |

## Audit result

31 substantive claims classified: **4 C1, 17 C2, 6 C3, 5 C4** (deferred items 28–32,
counting 32 as an availability commitment rather than a scientific claim).

No claim is stated above the class its evidence supports. Eight claims were
**downgraded or bounded** during finalization — edits E01, E03, E05/E07, E12, E13, E16,
E17, E20 — and two were **upgraded** because measurement now supports more than the
draft asserted: determinism scope (E17, from single-container to eight environments) and
Tier-0 execution status (E21, from future work to executed and reported).
