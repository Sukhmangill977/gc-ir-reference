# CLAIM_TO_ARTIFACT_MATRIX.md

Every manuscript claim that this artifact is responsible for, mapped to the component that implements it,
the test or experiment that exercises it, the output file that records the evidence, and the manuscript
section supported.

**Legend — evidence class**
* **F** formally derived (proof in the paper; artifact checks the premise holds on the pinned data)
* **S** synthetic case fixture (Case A)
* **R** forensic reconstruction (Case B)
* **M** author-operated measurement (claim class C1)
* **X** cross-platform conformance measurement (claim class C2)
* **D** deferred human study (RQ5 — no evidence produced here)

---

## A. Governed semantic refinement (C1)

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| A1 | `Ψ_K` is a relation closed by a signed judgment record `J`; no control semantics are inferred from prose | `src/gcir/refinement.py`, `src/gcir/catalog.py` | `tests/unit/test_refinement.py`, `tests/adversarial/test_no_inference.py` | `results/final/adversarial.json` | IV-A | F+M |
| A2 | Compilation contains **no** LLM, embedding, similarity, best-match, probabilistic or random rule selection | `src/gcir/compiler.py` (`exact_lookup` only) | `tests/adversarial/test_no_inference.py::test_source_contains_no_probabilistic_selection` (static source scan) | `results/final/adversarial.json` | IV-A, VI-A, VI-B | M |
| A3 | A register row whose `event_type` does not resolve to a catalog entry is not interpreted heuristically | `catalog.exact_lookup` | `tests/adversarial/test_catalog.py` | `results/final/adversarial.json` | IV-B | M |
| A4 | Catalog `K` is versioned with `M` and included in the compiled-bundle hash | `compiler.compile_bundle` payload assembly | `tests/unit/test_bundle_payload.py::test_catalog_version_in_payload` | `results/final/case_a/bundle.json` | IV-B | M |
| A5 | Each ACS carries evidence semantics, decision semantics and warrant boundary | `schemas/acs.schema.json` | `tests/unit/test_schemas.py` | `results/final/schema_validation.json` | IV-C | S |

## B. Total disposition and GC-IR (C2)

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| B1 | Every risk receives **exactly one** disposition; `DC` is measured, not assumed | `src/gcir/validation.py::assert_total_disposition` | `tests/properties/test_total_disposition.py`, `experiments/run_metrics.py` | `results/final/metrics.json` | IV-D, VI-E, XI-B | F+M |
| B2 | Implementation asserts `\|{Δ_i}\| = \|R\|` and never asserts `\|P\|+\|X\| = \|R\|` | `validation.py` | `tests/unit/test_totality_not_cardinality.py` | `results/final/unit_tests.json` | VI-E | M |
| B3 | One risk may yield 0, 1 or several predicates without violating totality | Case A R-04 (2 ACS), R-07, R-09 (2 ACS) | `tests/integration/test_case_a.py::test_predicate_multiplicity` | `results/final/case_a/gcir_records.json` | IV-D, VI-E | S+M |
| B4 | Non-runtime / accepted / unresolved records are first-class and need not carry subject/action/resource/basis/gate | `src/gcir/models.py`, `schemas/gcir.schema.json` (`oneOf`) | `tests/unit/test_record_family.py` | `results/final/schema_validation.json` | V, App. A | M |
| B5 | Reason codes RC-01/02/03/05 and warning WC-01 are closed at v1.0 | `src/gcir/models.py::ReasonCode` | `tests/adversarial/test_reason_codes.py` | `results/final/adversarial.json` | V | M |
| B6 | `WC-01` is a warning, not a disposition (a bundle can compile and still warn) | `compiler.py` warning channel | `tests/adversarial/test_wc01.py`, seeded row `VS-02` | `results/final/validation_seeds.json` | V, App. A #8 | M |
| B7 | `evaluation_basis` is closed to the four listed values; no condition evaluates a probability | `schemas/gcir.schema.json` | `tests/adversarial/test_evaluation_basis.py` | `results/final/adversarial.json` | V | M |

## C. Deterministic compilation `Φ` (C3)

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| C1 | RFC 8785 canonicalization implemented correctly | `src/gcir/canonicalization.py` | `tests/unit/test_rfc8785.py` (JCS vectors incl. the RFC's French/numeric cases) | `results/final/unit_tests.json` | VI-C | M |
| C2 | Hashed payload contains no timestamp, nonce, or mutable lifecycle field | `compiler.build_payload` + `validation.assert_payload_is_hash_clean` | `tests/adversarial/test_payload_purity.py`, `tests/properties/test_payload_immutability.py` | `results/final/case_a/payload_purity.json` | VI-C, VI-F, App. A #13 | M |
| C3 | `TD` — identical canonical payload hash under semantics-preserving permutation, locale, timezone, process | `experiments/run_determinism.py` | ≥ 30 runs per case, ≥ 60 total | `results/final/determinism_runs.csv`, `determinism_summary.json` | VI-C, XI-B, XI-H | M |
| C4 | Signature envelope is **not** required to be byte-identical | `src/gcir/signatures.py` (envelope excluded from payload) | `tests/unit/test_signature_envelope.py` | `results/final/unit_tests.json` | VI-C | M |
| C5 | Authority closure — every action tuple resolves to `S.authority_matrix`; unauthorized tuples cause deterministic rejection | `src/gcir/authority.py` | `tests/properties/test_authority_closure.py`, `tests/adversarial/test_unauthorized_tuple.py` | `results/final/property_tests.json` | VI-A, App. A #5 | F+M |
| C6 | Every predicate has an authorized origin: `∀p, origin(p) ∈ R ∪ INV` (OPR = 0) | `compiler.py` origin tagging; `validation.assert_origin_closure` | `tests/properties/test_origin_closure.py`, `experiments/run_metrics.py` | `results/final/metrics.json` | VI-B, XI-B | F+M |
| C7 | Mandatory gates require `on_unknown = fail` and `on_fail = SAFE_STATE` | `compiler.py` steps 8, `validation.py` | `tests/properties/test_mandatory_unknown.py`, `tests/adversarial/test_unknown_handling.py` | `results/final/property_tests.json` | V, VI-A, App. A #1,#2 | F+M |
| C8 | Every numeric/temporal condition ships a threshold contract with unit | `compiler.py` step 6 | `tests/adversarial/test_threshold_contract.py` | `results/final/adversarial.json` | V, App. A #3 | M |
| C9 | Precedence: mandatory failure ≻ mandatory pass ≻ weighted/advisory; unresolvable mandatory conflict → `SAFE_STATE` (indeterminate) | `src/gcir/precedence.py` | `tests/unit/test_precedence.py`, `tests/adversarial/test_conflicting_mandatory.py` | `results/final/precedence.json` | VI-D | F+M |
| C10 | Weighted records structurally invalid without group, weight, deficit function, group threshold, response | `schemas/gcir.schema.json` + `validation.py` | `tests/adversarial/test_weighted_structure.py` | `results/final/adversarial.json` | V | M |
| C11 | Assessor identity ≠ acceptor identity | `validation.py` | `tests/adversarial/test_separation_of_duty.py` | `results/final/adversarial.json` | III, App. A #10 | M |
| C12 | No expired approval enters a release-admissible bundle | `validation.py` | `tests/adversarial/test_expired_approval.py` | `results/final/adversarial.json` | App. A #9,#11 | M |
| C13 | Version binding: stale catalog / profile version rejected | `compiler.py` step 1 | `tests/adversarial/test_version_binding.py` | `results/final/adversarial.json` | III, VI-A | M |
| C14 | Signature verification of all signed inputs | `src/gcir/signatures.py` | `tests/adversarial/test_invalid_signature.py` | `results/final/adversarial.json` | VI-A | M |

## D. Consequence-class gate coverage (C4)

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| D1 | `C*` base profile is exactly the four listed kinds, materiality-qualified | `src/gcir/coverage.py::CSTAR_BASE_PROFILE_V1`, `invariants/c_star_profile_v1.json` | `tests/unit/test_c_star_profile.py` | `results/final/schema_validation.json` | VII-A | M |
| D2 | **CV** — each `C*` risk has ≥1 decisive mandatory gate per authorized hazardous action path; `Φ` rejects non-covering bundles | `coverage.py::verify_cv` | `tests/properties/test_c_star_coverage.py`, `tests/adversarial/test_missing_coverage.py` | `results/final/case_a/coverage_matrix.json`, `metrics.json` | VII-A, App. A #12 | F+M |
| D3 | Supporting/advisory predicates remain distinguishable from decisive mandatory gates | `mandatory_role` + `gate_source` in GC-IR | `tests/integration/test_case_a.py::test_mandatory_role_distinguishable` | `results/final/case_a/gate_map.json` | VII-A | S+M |
| D4 | **Proposition 1** premise holds on Case A (score inversion) ⇒ `GD_min ≥ 1` | `experiments/run_gate_divergence.py::detect_inversions` | gate-divergence experiment | `results/final/gate_divergence.json` | VII-C, IX | F+M |
| D5 | **Proposition 2** premise holds on Case A (score collision with divergent gates) | `run_gate_divergence.py::detect_collisions` | gate-divergence experiment | `results/final/gate_divergence.json` | VII-D, IX | F+M |
| D6 | `GD(T_H)` and `GD_min` measured over **all** register rows including non-runtime | `run_gate_divergence.py` | gate-divergence experiment | `results/final/gate_divergence.json` | VII-B, IX | M |
| D7 | Case B has no inversion/collision and `GD_min = 0` | same | gate-divergence experiment (Case B) | `results/final/gate_divergence.json` | X | R+M |
| D8 | **Proposition 3** — gate membership invariant under `(L, I, e)` perturbation with unchanged class | `run_monte_carlo.py` (`FP^{C*}`) | Monte Carlo, `K ≥ 250,000` | `results/final/monte_carlo_summary.json` | VII-E, XI-G | F+M |
| D9 | Heat-map gate membership does move under rating uncertainty | `run_monte_carlo.py` (`FP^heat`) | Monte Carlo, `K ≥ 250,000` | `results/final/monte_carlo_summary.json`, `monte_carlo_per_risk.csv` | XI-G | M |

## E. Bundle lifecycle and immutability

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| E1 | Payload immutable after signing; in-place mutation fails the hash check | `src/gcir/lifecycle.py`, `signatures.py` | `tests/adversarial/test_payload_mutation.py`, property test | `results/final/adversarial.json` | VI-F | M |
| E2 | Lifecycle state carried in a separately signed registry (`retire`/`supersede`/`revoke`) | `lifecycle.py::LifecycleRegistry` | `tests/unit/test_lifecycle.py` | `results/final/case_a/lifecycle_eval.json` | VI-F | M |
| E3 | `ValidAt(t, b, REG)` — 4-conjunct definition | `lifecycle.py::valid_at` | `tests/unit/test_valid_at.py` (6 scenarios) | `results/final/valid_at_scenarios.json` | VIII | F+M |
| E4 | A historical receipt citing a since-retired bundle is **not** drift | `valid_at` uses `decision_time` | `test_valid_at.py::test_pre_retirement_receipt_valid` | `results/final/valid_at_scenarios.json` | VIII | M |
| E5 | Registry record with invalid signing authority is rejected | `lifecycle.py` authority check | `tests/adversarial/test_lifecycle_authority.py`, query Q6 | `results/final/traceability_queries.json` | VIII | M |

## F. Temporal traceability (C5)

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| F1 | Authorized-origin chain obligation → disposition → ACS/INV → predicate → receipt | `src/gcir/traceability.py` (SQLite projection) | `experiments/run_traceability.py` | `results/final/traceability_queries.json` | VIII | M |
| F2 | Ordering `authorization_time ≤ evidence_commit_time < actuation_time` | `traceability.py`, query Q5 | `tests/unit/test_temporal_order.py`, property test | `results/final/property_tests.json` | VIII | F+M |
| F3 | **All six** audit queries implemented; empty on clean fixtures | `queries/traceability.sql` Q1–Q6 | `experiments/run_traceability.py` | `results/final/traceability_queries.json` | VIII | M |
| F4 | Each query **detects** its intended violation on a corrupted fixture | `queries/query_runner.py` corruption harness | `experiments/run_traceability.py` (negative controls) | `results/final/traceability_queries.json` | VIII, XI-H | M |
| F5 | `ODC` and `PTC` measured; traceability completeness does not require every obligation to produce a predicate | `metrics.py` | `experiments/run_metrics.py` | `results/final/metrics.json` | VIII, XI-B | M |

## G. Cases

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| G1 | Case A fully specified, hash-pinned, reproducible; **synthetic** | `cases/case_a/**` | `experiments/run_case.py case_a` | `results/final/case_a/*`, `docs/FIXTURE_PROVENANCE.md` | IX, XII | S+M |
| G2 | Case A dispositions 13 runtime / 3 non-runtime / 0 accepted / 0 unresolved | `cases/case_a/dispositions/` | `tests/integration/test_case_a.py` | `results/final/metrics.json` | IX | S+M |
| G3 | Case B fully specified, hash-pinned; **forensic reconstruction**, not new production evidence | `cases/case_b/**` | `experiments/run_case.py case_b` | `results/final/case_b/*` | X, XII | R+M |
| G4 | Case B's 284,807-event run is *not* reproduced or claimed here | (deliberate absence) | `docs/RESULT_INTERPRETATION.md` | — | X | — |
| G5 | `WC-01` and `RC-05` exercised in deliberately seeded validation rows outside the admissible register | `cases/case_a/validation_seeds/` | `experiments/run_adversarial.py` | `results/final/validation_seeds.json` | IX | S+M |

## H. Determinism and environment scope

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| H1 | ≥ 60 determinism runs across permutation, locale, timezone, clean process | `experiments/run_determinism.py` | final campaign | `results/final/determinism_runs.csv` | XI-H | M |
| H2 | Cross-platform: same reference hashes on ubuntu / windows / macOS runners | `.github/workflows/determinism.yml` | GitHub Actions matrix | CI run logs + `results/final/CI_STATUS.md` | XI-H, XII | X |
| H3 | Wording remains scoped to "deterministic across the tested supported environments" — **no universal platform-independence claim** | `docs/RESULT_INTERPRETATION.md` | — | `paper_update/MEASURED_RESULTS.md` | XII | — |

## I. Preregistration and deferral

| # | Claim | Implementation | Test / experiment | Output file | Paper § | Class |
|---|-------|----------------|-------------------|-------------|---------|-------|
| I1 | Public timestamped commitment precedes the final campaign | git tag `preregister-tier0-v1` | `experiments/verify_freeze.py` | `preregistration/FREEZE_MANIFEST.sha256`, `results/final/freeze_verification.json` | XI-I | M |
| I2 | Frozen items enumerated and hashed | `preregistration/TIER0_FREEZE.md` | freeze manifest generation | `preregistration/FREEZE_MANIFEST.sha256` | XI-I | M |
| I3 | RQ5 protocol frozen and **deferred**; no participant data generated | `preregistration/RQ5_DEFERRED_PROTOCOL.md` | — | — | XI-D, XI-I | D |
| I4 | Monte Carlo seed and distributions frozen before the final campaign | `preregistration/monte_carlo_distributions_v1.json` | included in freeze manifest | `results/final/monte_carlo_summary.json` | XI-G, XI-I | M |
| I5 | Monte Carlo distributions are **author-specified**, not panel-adjudicated | — | — | `docs/FIXTURE_PROVENANCE.md` FP-020, `paper_update/MEASURED_RESULTS.md` | XI-C, XI-G | — |

## J. Repository and release (Appendix C)

| # | Claim | Implementation | Output file | Paper § |
|---|-------|----------------|-------------|---------|
| J1 | `MANIFEST.sha256` lists path, SHA-256 and role per file | `experiments/make_manifest.py` | `MANIFEST.sha256` | App. C |
| J2 | Release contains the full enumerated artifact list | tagged release `v1.0.0` | `CHANGELOG.md`, release notes | App. C, Data & Code Availability |
| J3 | Held-out expert-study register withheld until study close | (deliberate absence) | `preregistration/RQ5_DEFERRED_PROTOCOL.md` | Data & Code Availability |
| J4 | MIT license for code and schema | `LICENSE` | `LICENSE` | App. C |

## K. Claims this artifact **cannot** support (recorded so they are never over-stated)

| Claim | Why not | Where recorded |
|---|---|---|
| RQ5 comparative superiority (SNR, DF) | No human study executed; **deferred** | `preregistration/RQ5_DEFERRED_PROTOCOL.md`, `docs/RESULT_INTERPRETATION.md` |
| Independently adjudicated reference standard | No panel convened | `docs/FIXTURE_PROVENANCE.md` FP-020 |
| Detection performance / production impact / false-denial rates | Out of scope; requires shadow-mode deployment | `docs/RESULT_INTERPRETATION.md` |
| Universal platform independence | Only the tested CI environments are measured | `docs/RESULT_INTERPRETATION.md`, H3 |
| Semantic correctness or completeness over the harm space | Authorization-soundness only | `docs/RESULT_INTERPRETATION.md` |
| Legal compliance from empty traceability queries | Explicitly disclaimed by the paper | `docs/RESULT_INTERPRETATION.md` |
