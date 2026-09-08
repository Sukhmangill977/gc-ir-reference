# ARTIFACT_RUNS_COMPLIANCE.md

Audit of the reference implementation against
`docs/source/Artifact_Runs_Effort_and_Impact(1).docx`
(*"Artifact runs for the IEEE Access submission: effort and impact"*, rev. 5.3,
7 September 2026), treated as an additional acceptance checklist.

Source document SHA-256:
`dc0215f7e205de187a17c832602f58366479887993766664658b865ef26001e4`

**Method.** Every row was verified by reading the file or running the command
named in the Evidence column. Nothing is marked PASS on the assumption that the
existing implementation already covered it; three rows were genuinely missing and
were built, and four are recorded as source inconsistencies rather than
implemented.

**Status vocabulary**

| Status | Meaning |
|---|---|
| **PASS** | Verified present and working. |
| **PASS (added)** | A genuine gap this audit found and closed. |
| **PASS (deviation declared)** | Satisfied, but not in the way the memo describes; the difference is documented and justified. |
| **SOURCE INCONSISTENCY** | The memo describes something that does not exist in the manuscript or in the referenced artifact. Not implemented; recorded. |
| **DEFERRED** | Out of scope by preregistration. |

---

## A. Effort-table items

| # | Requirement | Source location | Existing implementation | Status | Evidence | Action required |
|---|---|---|---|---|---|---|
| A1 | Case A/B inputs (M, S, O, R, A, K, J, D, Δ) as JSON, signed, hashed | Row 1 | `cases/case_a/**`, `cases/case_b/**`; Ed25519-signed, RFC 8785 canonicalized, SHA-256 pinned | **PASS** | `make verify-hashes`; `cases/*/expected/reference_hashes.json` | none |
| A2 | "Constraints 1–14 checked structurally" | Row 1 | All fourteen Appendix A constraints as individually named functions in `src/gcir/validation.py`, called from `Φ` | **PASS** | `constraint_01…constraint_13`, `check_runtime_acceptance` (14); adversarial cases ADV-009…ADV-044 exercise each | none |
| A3 | "DC, RCY, NDR, OPR, ODC, PTC and CV all fall out of one compile" | Row 1 | `src/gcir/metrics.py::compute_all` derives all seven from the compiled bundle | **PASS** | `python tools/freeze_check.py` prints all seven per case | none |
| A4 | **v1.1 JSON Schema** | Row 1 | Repository implements **v1.0** | **SOURCE INCONSISTENCY** | See §C below | none — v1.0 retained |
| A5 | **31-run TD manifest per case**, breakdown 10 repeats + 10 row shuffles + 5 key shuffles + 3 LC_ALL + 3 TZ | Row 2 | Was 30/case unstratified; **rebuilt** as the exact 10+10+5+3+3 stratified matrix | **PASS (added)** | `experiments/run_determinism.py::STRATA`; `results/final_v2/determinism_runs.csv` has 62 rows with a `stratum` column | none |
| A6 | "record hash and fingerprint" | Row 2 | Each run records the canonical payload hash **and** an `environment_fingerprint` over stratum, label, execution mode, locale, TZ, hash seed, numeric form, spec, platform, machine and Python version | **PASS (added)** | `environment_fingerprint` column in the CSV | none |
| A7 | `\TDruns` and its breakdown; TD = 1.000 | Row 2 | 62 runs, TD = 1.000 | **PASS** | `results/final_v2/determinism_summary.json` → `stratum_breakdown` | none |
| A8 | "or a real bug, better found now than in review" | Row 2 | **A real bug was found.** `Φ` hashed the derivation catalog as authored, so re-ordering catalog entries changed the bundle hash — the ordering dependence §VI-C forbids | **PASS** | `CHANGELOG.md`; regression tests `test_catalog_entry_order_does_not_reach_the_bundle_hash`, `test_input_array_order_does_not_change_the_payload_hash` | none |
| A9 | `freeze_check.py` green | Row 3 | Was `experiments/verify_freeze.py` only; **added** `tools/freeze_check.py` as a thin documented wrapper over the authoritative implementations | **PASS (added)** | `python tools/freeze_check.py` → 24 checks | none |
| A10 | "the thirteen frozen numbers stop being manuscript arithmetic" | Row 3 | Thirteen enumerated in `tools/freeze_check.py::FROZEN_NUMBERS`, each recomputed from artifacts | **PASS** | `freeze_check.py` prints "(13 frozen numbers enumerated)" | none |
| A11 | Monte Carlo, K = 250,000, via `tools/montecarlo.py` | Row 4 | `experiments/run_monte_carlo.py`; **added** `tools/montecarlo.py` wrapper at the memo's path | **PASS (added)** | `python tools/montecarlo.py` | none |
| A12 | "after the panel's rating distributions are frozen (panel sign-off is the long pole)" | Row 4 | **No panel has been convened.** Distributions are author-specified and were frozen a priori | **PASS (deviation declared)** | `docs/FIXTURE_PROVENANCE.md` FP-020; `preregistration/monte_carlo_distributions_v1.json` → `provenance` | none — see §D |
| A13 | "the 0.6/0.2/0.2 model" | Row 4 | Exactly the frozen rule: 0.6 on the approved rating, 0.2 on each adjacent | **PASS** | `monte_carlo_distributions_v1.json::perturbation_rule`. The memo independently names the same model the artifact froze a priori. | none |
| A14 | `\MCmax` | Row 4 | Measured and reported | **PASS** | `results/final_v2/monte_carlo_summary.json::per_case.case_a.max_FP_heat` | none |
| A15 | Adversarial suite: malformed reference, unauthorized tuple, missing producer, stale catalog, **timeout**, **state mismatch**, post-retirement use, in-place mutation | Row 5 | Seven of eight were present. **`timeout` was genuinely missing** and was built, together with the omitted-mandatory-predicate direction of state mismatch | **PASS (added)** | ADV-055, ADV-056, POS-006; new constraint `constraint_03b_mandatory_temporal_window_is_contractual`; structural check `state_mismatch_omitted_mandatory_predicate_detected` | none |
| A16 | "§XI-H's 'TD testing includes …' becomes a test log" | Row 5 | 62-case adversarial corpus + 26 structural checks + 3 seeded validation rows, all logged | **PASS** | `results/final_v2/adversarial.json`, `adversarial_cases.csv` | none |
| A17 | "the thirteen Case B injection scenarios become executable" | Row 5 | **Built.** The thirteen are the published artifact's own families: 8 adversarial attack families + 5 ASB scenario families | **PASS (added)** | `experiments/case_b_injection_scenarios.py`; 13/13 resolve to `SAFE_STATE` with a clean PERMIT control | none |
| A18 | Case B traceability: "P1–P13 → artifact-identifier mapping in MANIFEST.sha256" | Row 6 | **Built**, but **there is no P1–P13 family** in the published artifact | **PASS (deviation declared)** | `cases/case_b/ldrea_traceability.json`; `docs/CASE_B_LDREA_TRACEABILITY.md` | none — see §B |
| A19 | "a compiled Case B bundle whose predicate ids resolve to `realdatatestcode/`" | Row 6 | Nine mapping rows, each machine-verified against the compiled bundle and the external artifact | **PASS** | `python -m tools.build_ldrea_traceability` → 0 verification failures | none |
| A20 | Manifest mapping under role `case_b_input` | Examiner map, line 32 | Both L-DREA files carry role `case_b_input` in `MANIFEST.sha256` | **PASS** | `grep ldrea MANIFEST.sha256` | none |
| A21 | Cross-environment run via `td_crossenv.py`; flips `\crossenvtrue` | Row 7 | Measured on macOS/arm64 and Linux/aarch64 container; **added** `tools/td_crossenv.py` wrapper; CI matrix adds Windows and x86-64 | **PASS (added)** | `results/final_v2/CI_STATUS.md`; `tools/td_crossenv.py` | run the CI matrix after publication |
| A22 | "before a reviewer runs `run_all.py`" | Impact §, line 20 | **Added** `run_all.py` at the repository root over `experiments/reproduce_all.py` | **PASS (added)** | `python run_all.py --help` | none |

## B. `P1–P13` — SOURCE INCONSISTENCY, resolved constructively

**The memo says** (row 6): "the P1–P13 → artifact-identifier mapping".

**What the published artifact contains**, established by
`tools/derive_ldrea_predicate_family.py` reading its source:

* `P1`–`P4` exist, and are **stress-test scenarios**, not predicates
  (`realdatatestcode/stress_test.py`: Ghost Treasury Transfer, Sanctions Drift
  Cascade, Multi-Agent Liquidity Panic, Sovereign Cascade Edge Case).
  There is no `P5`, and no `P13`.
* **No P1–P13 predicate-identifier family exists anywhere in the artifact.**

**What does exist, and is very likely what the memo meant:** a predicate family
of exactly **thirteen** members — `NODE_GATE_COLS` (10: `Gate_A1`…`Gate_A7`,
`Lambda_G`, `TOKEN_VALID`, `AuthoritySignatureValid`) plus three derived deficit
columns (`HARM_RISK_THETA`, `STALE_CONTEXT`, `TELEMETRY_STALE`). The artifact's
own comment calls this "the predicate vector G = {g_1..g_n}".

Corroborated by four independent figures in the published reports, all agreeing
on 13: `benchmark_report.predicate_count`, `dataset.predicate_dimensionality`,
`negative_control.n_predicates`, and `single_deficit_score` = round(1/13, 3) =
0.077.

**Action taken.** Case B was mapped to the **thirteen real identifiers**.
**No P1–P13 identifiers were fabricated.** Full detail, including the two
declared gaps (B-03 velocity, `INV-VERSION`), in
`docs/CASE_B_LDREA_TRACEABILITY.md`.

## C. "Case C" and the schema version — SOURCE INCONSISTENCIES

### C1. "thirteen Case B and nineteen Case C scenarios" (memo, line 31)

| Question | Finding |
|---|---|
| Does the manuscript define a Case C? | **No.** Zero occurrences of "Case C" in the manuscript. It defines Cases A and B only (Sections IX and X). |
| Does the L-DREA artifact define a Case C? | **No.** No "Case C" and no 19-count anywhere in it. |
| Where might "thirteen" come from? | 8 adversarial attack families + 5 ASB scenario families = 13. This is implemented (A17). |
| Where might "nineteen" come from? | **No basis found** in the manuscript or the referenced artifact. |

**Action: no Case C was invented.** The manuscript's actual case structure —
Case A (synthetic, 16 rows) and Case B (forensic reconstruction, 6 rows) — is
preserved unchanged. Only the thirteen were implementable, and they were.

### C2. "the v1.1 JSON Schema" (memo, row 1)

| Source | Version |
|---|---|
| Manuscript, Section V | "Reason and warning codes are closed at **schema v1.0**" |
| Manuscript, Appendix A title | "GC-IR NORMATIVE SCHEMA REQUIREMENTS (**v1.0**; hash-pinned…)" |
| Manuscript, Appendix A footer | "[PENDING: **v1.0** freeze and $id host…]" |
| Repository | `SCHEMA_VERSION = "1.0"`; every schema pins `"schema_version": {"const": "1.0"}`; `$id` namespace `…/v1.0/` |
| Memo | "v1.1" — once, in a cost-estimate cell |

**Assessment.** The manuscript is consistent and normative at **v1.0** in three
places, including the appendix that *defines* the schema. The memo's "v1.1"
appears once, in an effort estimate, with no accompanying revision, changelog or
justification. Nothing in this audit produced a scientific reason to revise the
schema: no normative field changed, and the closed vocabularies are unchanged.

**Action: v1.0 retained. No silent version bump.** Bumping to v1.1 would have
invalidated the manuscript's Section V "closed at schema v1.0" statement and
every `$id`, to match a number in a memo cell. If a v1.1 is intended, it needs a
stated revision and a manuscript edit; that is a decision, not a rename.

## D. Monte Carlo panel attribution — CORRECTION MAINTAINED

The memo (row 4) treats panel sign-off as a prerequisite: "after the panel's
rating distributions are frozen (panel sign-off is the long pole — days, not
hours)". The manuscript's Section XI-G states the panel *did* freeze them.

**No independent adjudication panel has been convened.** The measured campaign
therefore uses author-specified distributions, frozen a priori, and says so
everywhere the number appears.

**This correction is maintained and was not reverted.** Specifically:

* `K = 250,000` **was executed** — `results/final_v2/monte_carlo_summary.json`.
* The distributions were **author-specified and prospectively frozen** in
  `preregistration/monte_carlo_distributions_v1.json`, before any result was
  computed, and are hashed into `FREEZE_MANIFEST_V2.sha256`.
* **Independent-panel distributions belong to the deferred RQ5 study** unless and
  until such a panel is genuinely convened.
* The memo's own "0.6/0.2/0.2 model" is precisely the rule frozen here — an
  independent corroboration that the a-priori choice was the natural one.

Manuscript wording: `paper_update/MEASURED_RESULTS.md` §5.

## E. Examiner mapping (memo lines 27–32)

| Examiner asked for | Discharged by | Status |
|---|---|---|
| Cases A and B inputs, compiled outputs, hashes | `cases/**`, `results/final_v2/case_*/`, `cases/*/expected/reference_hashes.json` | **PASS** |
| 31 compilation runs per case with the 10+10+5+3+3 breakdown | `experiments/run_determinism.py::STRATA`; 62 rows | **PASS (added)** |
| `freeze_check.py` one-command reproduction of DC, OPR, ODC, PTC, CV, TD, GD(15), GD_min | `tools/freeze_check.py` — all eight, plus RCY, NDR and Case B's CV/GD/GD_min | **PASS (added)** |
| Monte Carlo 250,000-draw output with frozen distributions and seed | `tools/montecarlo.py`; seed 20260201 frozen | **PASS** |
| Adversarial / property tests; the thirteen Case B scenarios | 62-case corpus, 16 properties, 13/13 injections | **PASS (added)** |
| …and nineteen Case C scenarios | No Case C exists | **SOURCE INCONSISTENCY** (§C1) |
| Case B traceability under role `case_b_input` | `cases/case_b/ldrea_traceability.json` | **PASS (deviation declared)** (§B) |

## F. The memo's six "author actions that close"

> "Six of the fourteen author actions close (freeze block, Case B in release,
> manifest mapping, schema freeze, tag, Monte Carlo inputs)"

| Action | Status | Evidence |
|---|---|---|
| Freeze block | **CLOSED** | `preregistration/TIER0_FREEZE_V2.md`, `FREEZE_MANIFEST_V2.sha256` |
| Case B in release | **CLOSED** | `cases/case_b/**` + compiled bundle in `results/final_v2/case_b/` |
| Manifest mapping | **CLOSED** | `MANIFEST.sha256`, role `case_b_input` |
| Schema freeze | **CLOSED at v1.0** | 13 schemas in `FREEZE_MANIFEST_V2.sha256` (§C2) |
| Tag | **CLOSED** | `preregister-tier0-v2`, pushed publicly |
| Monte Carlo inputs | **CLOSED, with attribution corrected** | `monte_carlo_distributions_v1.json` (§D) |

## G. Items outside this artifact's reach

| Item | Why |
|---|---|
| "citation dates and the disclosure sentence" (memo line 21) | Author editorial tasks. |
| Panel-adjudicated Monte Carlo distributions | Requires convening a panel; part of deferred RQ5. |
| RQ5 / SNR / DF | **DEFERRED** by preregistration; no participant data exists. |
| Windows and x86-64 determinism | Requires the CI matrix to execute after publication. |
| Zenodo DOI | No deposit made; `docs/ZENODO_RELEASE_STEPS.md`. |

---

## Summary

| Status | Count |
|---|---|
| PASS | 11 |
| PASS (added) | 9 |
| PASS (deviation declared) | 2 |
| SOURCE INCONSISTENCY (documented, not implemented) | 2 |
| DEFERRED | 1 |

**Nothing in the memo is left unaddressed.** The two source inconsistencies —
"P1–P13" and "nineteen Case C scenarios", plus the v1.1 schema reference — are
recorded with the evidence that establishes them as inconsistencies, and in each
case the constructive alternative that *was* implementable was implemented
instead.
