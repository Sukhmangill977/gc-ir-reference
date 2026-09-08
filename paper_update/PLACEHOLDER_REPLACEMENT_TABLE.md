# PLACEHOLDER_REPLACEMENT_TABLE.md

Every provisional empirical number and empirical-status statement in the
manuscript, against what the executed artifact actually measured.

**Campaign:** final, executed after the Tier-0 freeze.
**Freeze commit / tag:** `196820b23a632d56c4575dba3def71247b343f6a` /
`preregister-tier0-v1`
**Environment:** macOS 26.6.2 arm64, CPython 3.11.15; jsonschema 4.23.0,
cryptography 44.0.0, numpy 2.2.1, hypothesis 6.122.3, pytest 8.3.4.
**Evidence:** `results/final/` — every value below is read from a file in that
directory, and `results/final/SUMMARY.md` is generated from those files.

**Legend**

* ✅ **CONFIRMED** — the artifact measured the manuscript's value.
* ⚠️ **CHANGE REQUIRED** — the measured value or status differs; the manuscript must change.
* ➕ **NEW** — measured here, not currently in the manuscript.
* 🔓 **RESOLVE** — a bracketed placeholder to be filled in at release.

---

## A. Primary metrics (Section XI-B table; Abstract)

| # | Paper location | Current manuscript text/value | Measured value | Evidence file | Recommended replacement | Reason |
|---|---|---|---|---|---|---|
| A1 | Abstract; XI-B | `DC = 1.000 (16/16)` | **1.000 (16/16)** | `results/final/metrics.json` | keep | ✅ CONFIRMED |
| A2 | XI-B | `RCY = 0.8125 (13/16)` | **0.8125 (13/16)** | `metrics.json` | keep | ✅ CONFIRMED |
| A3 | XI-B | `NDR = 0.1875 (3/16)` | **0.1875 (3/16)** | `metrics.json` | keep | ✅ CONFIRMED |
| A4 | Abstract; XI-B | `OPR = 0.000 (0/|P|)` | **0.000 (0/19)** on Case A; 0.000 (0/9) on Case B | `metrics.json` | state the denominator: `0.000 (0/19)` | ✅ CONFIRMED; `|P|` now has a value |
| A5 | XI-B | `ODC = 1.000` | **1.000 (12/12)** Case A; 1.000 (6/6) Case B | `metrics.json` | add denominators | ✅ CONFIRMED |
| A6 | XI-B | `PTC = 1.000` | **1.000 (19/19)** Case A; 1.000 (9/9) Case B | `metrics.json` | add denominators | ✅ CONFIRMED |
| A7 | Abstract; XI-B | `CV = 1.000` | **1.000 (6/6)** Case A; 1.000 (4/4) Case B | `metrics.json` | add denominators | ✅ CONFIRMED |
| A8 | IX | "Dispositions: 13 runtime, 3 non-runtime, 0 accepted, 0 unresolved" | **13 / 3 / 0 / 0** | `metrics.json` | keep | ✅ CONFIRMED |
| A9 | XI-B | `SNR ... [TO REPORT]` | **DEFERRED** | `metrics.json` `deferred` block | keep `[TO REPORT]`, or state "deferred to the committed follow-up study" | ✅ status confirmed; no value exists |
| A10 | XI-B | `DF ... [TO REPORT]` | **DEFERRED** | same | as A9 | ✅ status confirmed |

## B. Translation determinism

| # | Paper location | Current manuscript text/value | Measured value | Evidence file | Recommended replacement | Reason |
|---|---|---|---|---|---|---|
| B1 | Abstract | "translation determinism of 1.000 over 31 compilation runs" | **1.000 over 60 runs (30 per case)** | `determinism_summary.json`, `determinism_runs.csv` | "translation determinism of 1.000 over 60 compilation runs (30 per case)" | ⚠️ **CHANGE REQUIRED** — value confirmed, count is now higher |
| B2 | XI-B table | `TD ... 1.000 (31/31 runs, pinned container)` | **1.000 (60/60 runs)**, executed on a macOS 26.6.2 arm64 host under CPython 3.11.15 | `determinism_summary.json` | `1.000 (60/60 runs; 30 per case)` and replace "pinned container" with the actual environment | ⚠️ **CHANGE REQUIRED** — the runs reported here were executed on a host, not inside the container. A pinned container is *provided* (`Dockerfile`, base image pinned by digest) and CI builds and runs it, but the 60 reported runs are host runs. |
| B3 | XI-H | "Measured: TD = 1.000 over 31 compilation runs — repeated runs, key and row reorderings, and locale and time-zone variation — executed inside the pinned reproducible container." | **1.000 over 60 runs** across: key ordering (reverse/shuffle/rotate over every object in every input), risk-row, obligation, ACS, disposition, judgment-selection, catalog, invariant and authority-matrix ordering; integer→float numeric re-encoding; 5 locales (C, en_US, de_DE, tr_TR, ja_JP); 5 time zones (UTC, America/Edmonton, Asia/Kolkata, Pacific/Chatham, Europe/Berlin); and clean-process execution with a varying `PYTHONHASHSEED` | `determinism_runs.csv` | See `MEASURED_RESULTS.md` §Determinism for publication-ready wording | ⚠️ **CHANGE REQUIRED** — more runs, more dimensions, different environment claim |
| B4 | XII (Determinism scope) | "Environment-independence is measured inside a pinned reproducible container... replication across independently installed host operating systems is not yet reported" | Cross-platform CI **is configured** (`.github/workflows/determinism.yml`: ubuntu / windows / macOS × Python 3.11 / 3.12, each with a distinct locale and time zone, all compared against committed reference hashes) but **has not yet executed**, because the repository has not been pushed. | `results/final/CI_STATUS.md` | Keep the limitation as stated until the CI matrix has actually passed; then narrow it to "deterministic across the tested supported environments". **Do not claim cross-platform determinism before the workflow runs green.** | ⚠️ **STATUS UNCHANGED — do not upgrade the claim yet** |

## C. Gate divergence (Sections VII, IX, X, XI-B)

| # | Paper location | Current manuscript text/value | Measured value | Evidence file | Recommended replacement | Reason |
|---|---|---|---|---|---|---|
| C1 | Abstract; IX; XI-B | `GD(15) = 3` on Case A | **3**, diverging on R-09, R-10, R-13 — exactly the three rows the manuscript names | `gate_divergence.json` | keep | ✅ CONFIRMED |
| C2 | Abstract; IX; XI-B | `GD_min = 3` on Case A | **3**, attained at t ∈ {9, 10, 13, 14, 15} | `gate_divergence.json` | keep, **but add the caveat in C3** | ✅ CONFIRMED as measured |
| C3 | IX | (no statement of the non-runtime rows' ratings) | `GD_min` runs over all 16 rows, and the manuscript states `L × I` for only the 13 runtime rows. With the artifact's documented fixture ratings (R-14 = 3×4 = 12, R-15 = 3×2 = 6, R-16 = 2×4 = 8) `GD_min = 3`. Sweeping every (L, I) in {1..5}² for those three rows — 15,625 combinations — `GD_min` ranges over **2 to 5** (distribution: 2→3375, 3→7534, 4→4068, 5→648). | `gate_divergence.json` `case_a_fixture_rating_sensitivity` | **Add** the three ratings to the Section IX table, so `GD_min = 3` is reproducible from the published register. | ⚠️ **CHANGE REQUIRED** — otherwise `GD_min` is not reproducible from the paper alone |
| C4 | X; XI-B | Case B `GD_min = 0` | **0**, attained at t ∈ {4, 5} | `gate_divergence.json` | keep | ✅ CONFIRMED |
| C5 | — | (not stated) | Case B `GD(15) = 4` — B-03, B-04, B-05, B-06 carry mandatory gates while scoring below 15 | `gate_divergence.json` | Optional addition to Section X | ➕ **NEW** |
| C6 | IX | "The inversion (s_{R-10} = 10 < 12 = s_{R-04}, g_{R-10} = 1, g_{R-04} = 0) satisfies Proposition 1" | Premise **holds**; **6** inverted pairs on the pinned register (R-10 and R-13, each at s = 10, against R-04, R-12 and R-14, each at s = 12) | `gate_divergence.json` `proposition_1` | Optionally state that six pairs instantiate it | ✅ CONFIRMED, strengthened |
| C7 | IX | "the three-way collision at s = 12 (R-04, R-09, R-12 with gates 0, 1, 0) instantiates Proposition 2" | Premise **holds**. On the pinned artifact the collision at s = 12 has **four** members: R-09 gated; R-04, R-12 **and R-14** ungated. R-14's rating is a fixture (C3). | `gate_divergence.json` `proposition_2` | Either (a) keep "three-way" and scope it to the runtime rows — "the collision at s = 12 among the runtime rows (R-04, R-09, R-12 with gates 0, 1, 0)"; or (b) publish R-14's rating and say "four-way". **Option (a) is recommended**: the three stated rows already instantiate Proposition 2, and the claim does not depend on the fixture. | ⚠️ **CHANGE REQUIRED (wording)** — "three-way" is inaccurate for the pinned artifact as it stands |

## D. Monte Carlo rating robustness (Abstract; Section XI-G)

| # | Paper location | Current manuscript text/value | Measured value | Evidence file | Recommended replacement | Reason |
|---|---|---|---|---|---|---|
| D1 | Abstract; XI-G | "Monte Carlo rating perturbation moves heat-map gate membership with probability up to 0.321" | **0.321268** (max per-risk `FP^heat`, on R-06), MCSE **0.000934**, at K = 250,000 | `monte_carlo_summary.json`, `monte_carlo_per_risk.csv` | "up to 0.321 (MCSE 0.001)" | ✅ CONFIRMED to three decimal places |
| D2 | XI-G | "`FPᵢ^{C*} = 0.000` across the register by construction" | **0.000** on both cases, and **verified rather than assumed**: the real `C*` classifier was re-run on 1,000 randomly selected perturbed draws per case and **0** membership changes were observed | `monte_carlo_summary.json` | keep; optionally note the verification | ✅ CONFIRMED and strengthened |
| D3 | **XI-G, XI-C** | **"For each risk `rᵢ`, the independent panel freezes discrete probability masses over plausible ratings"** | **NO INDEPENDENT ADJUDICATION PANEL HAS BEEN CONVENED.** The distributions used are author-specified synthetic sensitivity distributions, frozen a priori in `preregistration/monte_carlo_distributions_v1.json`: 0.6 on the approved rating, 0.2 on each adjacent rating on the 1–5 scale, out-of-range mass reassigned to the approved rating. | `preregistration/monte_carlo_distributions_v1.json`; `docs/FIXTURE_PROVENANCE.md` FP-020 | **Mandatory rewrite.** See `MEASURED_RESULTS.md` §Monte Carlo for the exact replacement sentence. | ⚠️ **CHANGE REQUIRED — this is the most important correction in this table.** As written, the manuscript attributes a methodological input to a panel that does not exist. |
| D4 | XI-G | "MCSE ... bounded above by 0.001 at K = 250,000" | **0.0005** is the actual upper bound `√(0.25/250000)`; the MCSE at the reported estimate is **0.000934** | `monte_carlo_summary.json` | The stated bound of 0.001 is correct as an upper bound and can stand; optionally give the exact figure | ✅ CONFIRMED (conservative as stated) |
| D5 | — | (not stated) | Expected heat-map gate changes per register: **3.64** (Case A), **1.19** (Case B). GD(15) distribution over draws and GD_min distribution over draws are reported. Case B's `GD_min` was **0 in all 250,000 draws**. | `monte_carlo_summary.json` | Optional addition to Section XI-G, which promises these quantities | ➕ **NEW** — Section XI-G lists "distributions of GD(T_H) and GD_min" as reported quantities; they now exist |
| D6 | — | (not stated) | Secondary sensitivity: renormalising the out-of-range mass instead of reassigning it gives max `FP^heat` = **0.352** (Case A) | `monte_carlo_summary.json` `sensitivity_variant` | Optional footnote | ➕ **NEW** |

## E. Testing (Section XI-H)

| # | Paper location | Current manuscript text/value | Measured value | Evidence file | Recommended replacement | Reason |
|---|---|---|---|---|---|---|
| E1 | XI-H | "TD testing includes: [list of 15 adversarial conditions]" | **59-case adversarial corpus** (52 negative, 7 positive controls): 59 PASS, 0 FAIL, 0 CODE_MISMATCH. Plus **24 structural checks** (24/24) and **3 seeded validation rows** (3/3). Every listed condition is covered. | `adversarial.json`, `adversarial_cases.csv` | Report the counts | ➕ **NEW** — the manuscript lists conditions but reports no counts |
| E2 | XI-H | "Property-based tests verify total disposition, authority closure, mandatory unknown-failure, C\* coverage, origin closure, payload immutability, and temporal receipt validity." | **16 properties**, all seven named plus nine more; **1,427 generated examples**; `max_examples = 100`. Two properties report 18 and 9 examples because Hypothesis **exhausts** their finite input spaces (3×3×2 and 3×3). | `property_tests.json` | Report the counts and the exhaustion note | ➕ **NEW** |
| E3 | — | (not stated) | **275 tests** across four suites, 0 failures | `property_tests.json` | Optional | ➕ **NEW** |
| E4 | VIII | "The audit queries therefore test: [six queries]" | All six implemented; **all return empty** on both cases' clean fixtures; **18 negative controls (9 per case) all fire**, so each query demonstrably detects the violation it exists to detect. | `traceability_queries.json` | Report both halves — the negative controls are the stronger evidence | ➕ **NEW** |
| E5 | IX | "WC-01 and RC-05 handling are exercised in the machine-readable artifact's deliberately seeded validation rows." | **Confirmed.** VS-01 exercises RC-05, VS-02 exercises WC-01, VS-03 exercises RC-02 — all pass, all outside the release-admissible register. | `adversarial.json` `validation_seeds` | keep | ✅ CONFIRMED |

## F. Case artifacts and bracketed placeholders

| # | Paper location | Current manuscript text/value | Measured / resolved value | Evidence file | Recommended replacement | Reason |
|---|---|---|---|---|---|---|
| F1 | IX | "the full Step 1–5 artifact set ... ship machine-readable in the repository ... the artifact is hash-pinned" | Case A canonical payload SHA-256 = **`f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536`** | `results/final/case_a/payload_hash.txt`, `cases/case_a/expected/reference_hashes.json` | State the hash | 🔓 **RESOLVE** |
| F2 | X | **`[PENDING: hash-pinned Case B artifact release]`** | Case B canonical payload SHA-256 = **`2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce`** | `results/final/case_b/payload_hash.txt` | Replace the placeholder with the hash | 🔓 **RESOLVE** |
| F3 | Appendix A | **`[PENDING: v1.0 freeze and $id host set at the artifact-repository release]`** | Schemas are frozen at v1.0 (13 documents in `schemas/`, all in `FREEZE_MANIFEST.sha256`). The `$id` host is currently the placeholder `https://gcir.example/schemas/v1.0/`. | `preregistration/FREEZE_MANIFEST.sha256` | Say the schema is frozen at v1.0 and hash-pinned; set the `$id` host to a real resolvable base only if one will be maintained, otherwise state that `$id` values are stable identifiers rather than resolvable URLs | 🔓 **PARTIALLY RESOLVE** — do not claim a resolvable host that does not resolve |
| F4 | Appendix C | **`[TO CONFIRM: final repository path at release]`** | Repository path pending publication; see the outstanding-actions note below | — | Fill in once the repository is pushed | 🔓 **RESOLVE AT RELEASE** |
| F5 | Data & Code Availability; Appendix C | "released as a hash-pinned tagged release" | `MANIFEST.sha256` covers **174 files across 24 roles**; manifest SHA-256 recorded in `MANIFEST.json` | `MANIFEST.sha256`, `MANIFEST.json` | State the manifest hash and the release tag | 🔓 **RESOLVE AT RELEASE** |
| F6 | Data & Code Availability | "the preregistration commitment ... are released" | `FREEZE_MANIFEST.sha256` covers **117 files across 19 Section XI-I categories**; tag `preregister-tier0-v1` | `preregistration/FREEZE_MANIFEST.json` | State the freeze manifest hash and tag | 🔓 **RESOLVE AT RELEASE** |
| F7 | XI-I | "the following are publicly hash-committed: ... case artifacts and **held-out-register hash** ..." | **No held-out register has been authored, so no hash is committed.** Recorded openly in `preregistration/HELD_OUT_REGISTER.md` rather than committing a hash of a placeholder. | `preregistration/HELD_OUT_REGISTER.md` | State that the held-out-register hash is committed in a **Tier-1 freeze before RQ5 recruitment opens**, not in the Tier-0 freeze | ⚠️ **CHANGE REQUIRED** — the Tier-0 freeze does not discharge this item |

## G. Statements that must not change

| Paper location | Statement | Status |
|---|---|---|
| Abstract; I-D; XI; XII; XIV | RQ5 is preregistered, deferred, and no comparative-superiority claim is made | ✅ **Confirmed and preserved.** No participant data exists anywhere in the artifact. |
| X; XII | Case B is a forensic reconstruction; the 284,807-event run is conformance-class and is not reproduced | ✅ **Preserved.** `case_class: "forensic_reconstruction"` is a machine-readable field, and the run is deliberately absent. |
| XII | Case A is synthetic | ✅ **Preserved.** `case_class: "synthetic"`. |
| XI-I | Only C1/C2 claim classes; no C3/C4 | ✅ **Preserved** throughout `docs/RESULT_INTERPRETATION.md`. |
| VI-C | The signature envelope need not be byte-identical | ✅ **Implemented and tested.** |
| VII-C, VII-D, VII-E | Propositions 1–3 | **Not touched.** These are analytic results. The artifact checks that the pinned register instantiates the premises of 1 and 2; it does not re-derive or modify any proposition. |

---

## Outstanding actions not discharged by this artifact

1. **Push the repository and the freeze tag.** Until then the Section XI-I *public*
   timestamped commitment is not discharged, and the manuscript must describe the
   preregistration as prepared and locally committed. `verify_freeze.py` reports
   `public_commitment_discharged: false` and will report `true` after the push.
2. **Run the cross-platform CI matrix.** Until it passes, do not upgrade the
   determinism claim beyond the declared environment (B4).
3. **Zenodo deposit.** No DOI exists; do not cite one. See
   `docs/ZENODO_RELEASE_STEPS.md`.
4. **Author the held-out register** and commit its hash in a Tier-1 freeze before
   RQ5 recruitment (F7).
5. **`[VERIFY]` markers in Sections II and XIII** — a final literature sweep and a
   sentence-level overlap check against the published version of [15]. These are
   author tasks; no artifact can discharge them.
