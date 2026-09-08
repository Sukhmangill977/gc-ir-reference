# PLACEHOLDER_REPLACEMENT_TABLE_V2.md

Every provisional empirical number and empirical-status statement in the
manuscript, against the **v2 campaign**. Supersedes the v1 table.

**Campaign provenance.** Public freeze `preregister-tier0-v2.2`, commit
`c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e`, pushed 2026-09-08T18:01:36Z to
<https://github.com/Sukhmangill977/gc-ir-reference>; campaign executed at that
commit; 0 of 133 frozen files changed in between. Evidence in
`results/final_v2/PROVENANCE.json`.

**Legend** ✅ CONFIRMED · ⚠️ CHANGE REQUIRED · ➕ NEW · 🔓 RESOLVE

---

## A. Primary metrics

| # | Location | Manuscript | Measured (v2) | Evidence | Replacement | Status |
|---|---|---|---|---|---|---|
| A1 | Abstract; XI-B | `DC = 1.000 (16/16)` | **1.000 (16/16)** | `metrics.json` | keep | ✅ |
| A2 | XI-B | `RCY = 0.8125 (13/16)` | **0.8125 (13/16)** | `metrics.json` | keep | ✅ |
| A3 | XI-B | `NDR = 0.1875 (3/16)` | **0.1875 (3/16)** | `metrics.json` | keep | ✅ |
| A4 | XI-B | `OPR = 0.000 (0/\|P\|)` | **0.000 (0/19)** | `metrics.json` | state the denominator | ✅ |
| A5 | XI-B | `ODC = 1.000` | **1.000 (12/12)** | `metrics.json` | add denominator | ✅ |
| A6 | XI-B | `PTC = 1.000` | **1.000 (19/19)** | `metrics.json` | add denominator | ✅ |
| A7 | XI-B | `CV = 1.000` | **1.000 (6/6)** | `metrics.json` | add denominator | ✅ |
| A8 | IX | 13 / 3 / 0 / 0 dispositions | **13 / 3 / 0 / 0** | `metrics.json` | keep | ✅ |
| A9 | XI-B | `SNR [TO REPORT]` | **DEFERRED** | — | keep | ✅ |
| A10 | XI-B | `DF [TO REPORT]` | **DEFERRED** | — | keep | ✅ |

## B. Determinism

| # | Location | Manuscript | Measured (v2) | Evidence | Replacement | Status |
|---|---|---|---|---|---|---|
| B1 | Abstract | "1.000 over 31 compilation runs" | **1.000 over 62 runs (31 per case)** | `determinism_summary.json` | "62 compilation runs (31 per case)" | ⚠️ |
| B2 | XI-B table | `1.000 (31/31 runs, pinned container)` | **1.000 (62/62)**, reproduced on 8 environments | `CI_STATUS.md` | `1.000 (62/62 runs; 31 per case)` | ⚠️ |
| B3 | XI-H | "31 compilation runs … executed inside the pinned reproducible container" | 62 runs across the **10+10+5+3+3** stratified matrix, on 3 OSes and 2 architectures | `determinism_runs.csv` (62 rows, `stratum` column) | `MEASURED_RESULTS_V2.md` §3 | ⚠️ |
| B4 | XII determinism scope | "replication across independently installed host operating systems is not yet reported" | **Now reported.** macOS/arm64, Ubuntu/x86_64, Windows/AMD64, plus a Debian container/aarch64; 6 CPython versions; all TD = 1.000, identical hashes | `CI_STATUS.md`; [run 34261657261](https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34261657261) | **Widen, do not delete** — `MEASURED_RESULTS_V2.md` §4 | ⚠️ |

## C. Gate divergence

| # | Location | Manuscript | Measured (v2) | Evidence | Replacement | Status |
|---|---|---|---|---|---|---|
| C1 | Abstract; IX | `GD(15) = 3` | **3** — R-09, R-10, R-13, exactly the named rows | `gate_divergence.json` | keep | ✅ |
| C2 | Abstract; IX | `GD_min = 3` | **3**, at t ∈ {9,10,13,14,15} | `gate_divergence.json` | keep + C3 caveat | ✅ |
| C3 | IX | (ratings for R-14/15/16 not stated) | With the documented fixtures (12, 6, 8) `GD_min = 3`; sweeping all 15,625 combinations it ranges **2–5** | `gate_divergence.json` | **publish the three ratings** | ⚠️ |
| C4 | X | Case B `GD_min = 0` | **0**, at t ≤ 5 | `gate_divergence.json` | keep | ✅ |
| C5 | — | (not stated) | Case B `GD(15) = 4` | `gate_divergence.json` | optional | ➕ |
| C6 | IX | one inversion cited | premise holds; **6** inverted pairs | `gate_divergence.json` | optional | ✅ |
| C7 | IX | "three-way collision at s = 12" | **four-way** — R-14 also rates 12 | `gate_divergence.json` | scope to the runtime rows | ⚠️ |

## D. Monte Carlo

| # | Location | Manuscript | Measured (v2) | Evidence | Replacement | Status |
|---|---|---|---|---|---|---|
| D1 | Abstract; XI-G | "up to 0.321" | **0.321268** (MCSE 0.000934, R-06) at K = 250,000 | `monte_carlo_summary.json` | "up to 0.321 (MCSE 0.001)" | ✅ |
| D2 | XI-G | `FP^{C*} = 0.000 by construction` | **0.000**, verified on 1,000 re-classified draws, 0 changes | `monte_carlo_summary.json` | keep; note the verification | ✅ |
| D3 | **XI-G, XI-C** | **"the independent panel freezes discrete probability masses"** | **NO PANEL CONVENED.** Author-specified, frozen a priori | `preregistration/monte_carlo_distributions_v1.json`; FP-020 | **mandatory rewrite** — `MEASURED_RESULTS_V2.md` §5 | ⚠️ |
| D4 | XI-G | MCSE ≤ 0.001 at K = 250,000 | exact bound 0.0005; at the estimate 0.000934 | `monte_carlo_summary.json` | correct as stated | ✅ |
| D5 | — | (promised, not given) | GD mean **5.447**, GD_min mean **3.226**; Case B GD_min = 0 in all draws | `monte_carlo_summary.json` | optional addition | ➕ |
| D6 | — | (not stated) | renormalising variant: **0.352** | `monte_carlo_summary.json` | optional footnote | ➕ |

## E. Testing

| # | Location | Manuscript | Measured (v2) | Evidence | Status |
|---|---|---|---|---|---|
| E1 | XI-H | lists conditions, gives no counts | **62-case corpus** (54 negative, 8 positive), 26 structural checks, 3 seeded rows — all passing | `adversarial.json` | ➕ |
| E2 | XI-H | names 7 properties | **16 properties, 1,427 generated examples** | `property_tests.json` | ➕ |
| E3 | — | — | **280 tests**, 0 failures | `property_tests.json` | ➕ |
| E4 | VIII | six queries | all empty; **18 negative controls all fire** | `traceability_queries.json` | ➕ |
| E5 | IX | WC-01 / RC-05 seeded rows | confirmed; RC-02 added | `adversarial.json` | ✅ |
| E6 | — | (memo asks for it) | **13 Case B injection scenarios**, all → SAFE_STATE | `adversarial.json` | ➕ |

## F. Placeholders and linkage

| # | Location | Manuscript | Resolved | Status |
|---|---|---|---|---|
| F1 | IX | hash-pinned Case A | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | 🔓 |
| F2 | X | `[PENDING: hash-pinned Case B artifact release]` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | 🔓 |
| F3 | App. A | `[PENDING: v1.0 freeze and $id host]` | Frozen at **v1.0**; `$id` values are identifiers, not resolvable endpoints. The memo's "v1.1" has no manuscript basis — see `ARTIFACT_RUNS_COMPLIANCE.md` §C2 | 🔓 |
| F4 | App. C | `[TO CONFIRM: final repository path]` | <https://github.com/Sukhmangill977/gc-ir-reference> | 🔓 |
| F5 | Data & Code | hash-pinned tagged release | `MANIFEST.sha256`, release `v1.0.0` | 🔓 |
| F6 | XI-I | public hash commitment | **DISCHARGED** — tag `preregister-tier0-v2.2`, remote-verified, pushed before execution | ✅ |
| F7 | XI-I | held-out-register hash | **Still outstanding** — no held-out register authored; Tier-1 item | ⚠️ |
| F8 | X | L-DREA linkage | **NEW** — 9-row machine-verified mapping to the 13 real predicate identifiers; 4 exact, 3 family, 2 declared gaps | ➕ |

## G. Statements that must not change

| Location | Statement | Status |
|---|---|---|
| Abstract; I-D; XI; XII; XIV | RQ5 preregistered, deferred, no comparative claim | ✅ **preserved** — no participant data exists anywhere |
| X; XII | Case B forensic; the 284,807-event run is conformance-class and not reproduced | ✅ **preserved**, and re-asserted in the L-DREA mapping's claim boundary |
| XII | Case A synthetic | ✅ preserved |
| XI-I | C1/C2 only, no C3/C4 | ✅ preserved |
| VI-C | signature envelope need not be byte-identical | ✅ implemented and tested |
| VII-C/D/E | Propositions 1–3 | **untouched** — the artifact checks their premises, it does not modify them |

## H. Remaining actions

1. **Zenodo DOI** — no deposit made; do not cite one. `docs/ZENODO_RELEASE_STEPS.md`.
2. **Held-out register** — author it and commit its hash in a Tier-1 freeze before
   RQ5 recruitment.
3. **`[VERIFY]` markers in Sections II and XIII** — literature sweep and overlap
   check. Author tasks.
