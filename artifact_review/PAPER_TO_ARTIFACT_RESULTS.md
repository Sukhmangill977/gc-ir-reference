# Paper-to-artifact result map

Every empirical number the IEEE submission reports, mapped to the evidence file that produced it and the command that regenerates it.

**This file is generated** by `python -m tools.build_paper_result_map`, which reads each value out of `results/final_v2/`. No number in it is typed from the manuscript. `tools/verify_reported_results.py` consumes the JSON form and fails if any value drifts.

| | |
|---|---|
| Authoritative campaign | `results/final_v2/` |
| Public freeze | `preregister-tier0-v2.2` |
| Freeze commit | `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` |
| Paper-facing results mapped | **48** |

Reproduce everything at once with `python run_all.py --final-v2`, or verify without re-running with `python tools/verify_reported_results.py`.

---

## Index

| ID | Metric | Reported value | Section |
|---|---|---|---|
| `H-A` | Case A canonical payload SHA-256 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | IX |
| `H-B` | Case B canonical payload SHA-256 | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | X |
| `DC-A` | DC (Disposition Completeness), Case A | `1.0000 (16/16)` | XI-B |
| `RCY-A` | RCY (Runtime Conversion Yield), Case A | `0.8125 (13/16)` | XI-B |
| `NDR-A` | NDR (Non-Derivation Rate), Case A | `0.1875 (3/16)` | XI-B |
| `OPR-A` | OPR (Orphan Predicate Rate), Case A | `0.0000 (0/19)` | XI-B |
| `ODC-A` | ODC (Obligation Disposition Completeness), Case A | `1.0000 (12/12)` | XI-B |
| `PTC-A` | PTC (Predicate Traceability Completeness), Case A | `1.0000 (19/19)` | XI-B |
| `CV-A` | CV (C* Coverage), Case A | `1.0000 (6/6)` | XI-B |
| `DC-B` | DC (Disposition Completeness), Case B | `1.0000 (6/6)` | XI-B |
| `RCY-B` | RCY (Runtime Conversion Yield), Case B | `1.0000 (6/6)` | XI-B |
| `NDR-B` | NDR (Non-Derivation Rate), Case B | `0.0000 (0/6)` | XI-B |
| `OPR-B` | OPR (Orphan Predicate Rate), Case B | `0.0000 (0/9)` | XI-B |
| `ODC-B` | ODC (Obligation Disposition Completeness), Case B | `1.0000 (6/6)` | XI-B |
| `PTC-B` | PTC (Predicate Traceability Completeness), Case B | `1.0000 (9/9)` | XI-B |
| `CV-B` | CV (C* Coverage), Case B | `1.0000 (4/4)` | XI-B |
| `GD-A` | GD(15), Case A | `3` | IX and XI-B |
| `GDMIN-A` | GD_min, Case A | `3` | IX and XI-B |
| `GD-B` | GD(15), Case B | `4` | IX and XI-B |
| `GDMIN-B` | GD_min, Case B | `0` | IX and XI-B |
| `GDMIN-SENS` | GD_min fixture-rating sensitivity range | `[2, 5]` | XII |
| `TD` | TD | `1.000 (62/62)` | XI-B and XI-H |
| `TD-DEN` | TD denominator | `62` | XI-B and XI-H |
| `TD-RPC` | determinism runs per case | `31` | XI-H |
| `TD-STRATA` | determinism stratum breakdown | `{"key_shuffle": 5, "locale": 3, "repeat": 10, "row_shuffle": 10, "timezone": 3}` | XI-H |
| `TD-A` | TD, Case A | `1.000 (31/31)` | XI-H |
| `TD-B` | TD, Case B | `1.000 (31/31)` | XI-H |
| `MC-K` | Monte Carlo draws K | `250000` | XI-G |
| `MC-SEED` | Monte Carlo RNG seed | `20260201` | XI-G |
| `MC-FPHEAT` | max FP^heat, Case A | `0.321268` | Abstract and XI-G |
| `MC-MCSE` | MCSE at max FP^heat | `0.000933926918288578` | XI-G |
| `MC-FPCSTAR` | max FP^C*, Case A | `0.0` | Abstract and XI-G |
| `MC-CSTAR-PROBE` | C* membership changes over probe draws | `0 changes in 1000 draws` | XI-G |
| `MC-VARIANT` | max FP^heat, renormalisation variant | `0.352092` | XI-G |
| `MC-GD_MEAN` | GD_mean | `5.4466` | XI-G |
| `MC-GD_MIN_MEAN` | GD_min_mean | `3.226356` | XI-G |
| `MC-EXPECTED_GATE_CHANGES_PER_REGISTER_HEATMAP` | expected_gate_changes_per_register_heatmap | `3.642176` | XI-G |
| `ADV` | adversarial corpus | `62/62 (54 negative, 8 positive controls)` | XI-H |
| `STRUCT` | structural checks | `26/26` | XI-H |
| `SEEDS` | validation seeds | `3/3` | XI-H |
| `INJ` | Case B injection scenarios | `13/13` | XI-H |
| `TESTS` | test count | `280/280` | XI-H |
| `PROPS` | properties and generated examples | `16 properties, 1427 examples` | XI-H |
| `TRACE-CLEAN` | clean audit queries empty | `6/6 empty per case, both cases` | XI-H |
| `TRACE-NEG` | negative controls detected | `18/18` | XI-H |
| `FREEZE` | public_commitment_discharged | `True` | XI-I |
| `FREEZE-FILES` | frozen file count | `133` | XI-I |
| `XENV` | cross-environment agreement | `8 environments, all TD = 1.000, all reference hashes identical` | XI-H and XII |

---

## Entries

### `H-A` — Case A canonical payload SHA-256

| Field | Value |
|---|---|
| Manuscript section | IX |
| Claim | The Case A artifact is hash-pinned by the SHA-256 of its RFC 8785 canonical bundle payload. |
| Reported value | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| Source experiment | case compilation |
| Reproduce with | `python -m experiments.run_case --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/case_a/compilation.json` |
| Exact field | `result.payload_hash` |
| Expected value | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| Interpretation | Identifies the exact compiled bundle the paper reports on. Recomputable from the committed governance inputs, and cross-checked against cases/case_a/expected/reference_hashes.json. |
| **Claim boundary** | A hash pins an artifact. It says nothing about whether the artifact's content is correct. |

### `H-B` — Case B canonical payload SHA-256

| Field | Value |
|---|---|
| Manuscript section | X |
| Claim | The Case B artifact is hash-pinned by the SHA-256 of its RFC 8785 canonical bundle payload. |
| Reported value | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| Source experiment | case compilation |
| Reproduce with | `python -m experiments.run_case --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/case_b/compilation.json` |
| Exact field | `result.payload_hash` |
| Expected value | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| Interpretation | Identifies the exact compiled bundle the paper reports on. Recomputable from the committed governance inputs, and cross-checked against cases/case_b/expected/reference_hashes.json. |
| **Claim boundary** | A hash pins an artifact. It says nothing about whether the artifact's content is correct. |

### `DC-A` — DC (Disposition Completeness), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: every register row carries exactly one approved disposition. |
| Reported value | `1.0000 (16/16)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.DC.value` |
| Expected value | `1.0` |
| Numerator / denominator | `16 / 16` |
| Interpretation | Disposition Completeness |
| **Claim boundary** | DC = 1 holds BY CONSTRUCTION once dispositions are signed. Measuring it verifies the artifact conforms to Appendix A constraint 4; it does not show the dispositions are the right ones. |

### `RCY-A` — RCY (Runtime Conversion Yield), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: share of register rows dispositioned to runtime enforcement. |
| Reported value | `0.8125 (13/16)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.RCY.value` |
| Expected value | `0.8125` |
| Numerator / denominator | `13 / 16` |
| Interpretation | Runtime Conversion Yield |
| **Claim boundary** | Descriptive only. A lower RCY is not worse; it reflects how many risks the approver routed to runtime. |

### `NDR-A` — NDR (Non-Derivation Rate), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: share of register rows dispositioned non-runtime. |
| Reported value | `0.1875 (3/16)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.NDR.value` |
| Expected value | `0.1875` |
| Numerator / denominator | `3 / 16` |
| Interpretation | Non-Derivation Rate |
| **Claim boundary** | Descriptive complement of RCY. Not an error rate. |

### `OPR-A` — OPR (Orphan Predicate Rate), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: no compiled predicate lacks an authorized origin in R union INV. |
| Reported value | `0.0000 (0/19)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.OPR.value` |
| Expected value | `0.0` |
| Numerator / denominator | `0 / 19` |
| Interpretation | Orphan Predicate Rate |
| **Claim boundary** | A compiler guarantee WITHIN Phi-produced bundles. It extends to a deployment only under the explicit runtime acceptance condition. |

### `ODC-A` — ODC (Obligation Disposition Completeness), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: every obligation is disposed. |
| Reported value | `1.0000 (12/12)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.ODC.value` |
| Expected value | `1.0` |
| Numerator / denominator | `12 / 12` |
| Interpretation | Obligation Disposition Completeness |
| **Claim boundary** | Linkage under the declared data model. Not legal compliance. |

### `PTC-A` — PTC (Predicate Traceability Completeness), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: every predicate traces to a risk or to a compiler invariant. |
| Reported value | `1.0000 (19/19)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.PTC.value` |
| Expected value | `1.0` |
| Numerator / denominator | `19 / 19` |
| Interpretation | Predicate Traceability Completeness |
| **Claim boundary** | Structural traceability. Not semantic correctness. |

### `CV-A` — CV (C* Coverage), Case A

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case A: every consequence-class row has a decisive mandatory gate on each authorized hazardous action path. |
| Reported value | `1.0000 (6/6)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_a.CV.value` |
| Expected value | `1.0` |
| Numerator / denominator | `6 / 6` |
| Interpretation | C* Coverage |
| **Claim boundary** | Coverage of the DECLARED C* profile. Does not establish that the profile is complete over the harm space. |

### `DC-B` — DC (Disposition Completeness), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: every register row carries exactly one approved disposition. |
| Reported value | `1.0000 (6/6)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.DC.value` |
| Expected value | `1.0` |
| Numerator / denominator | `6 / 6` |
| Interpretation | Disposition Completeness |
| **Claim boundary** | DC = 1 holds BY CONSTRUCTION once dispositions are signed. Measuring it verifies the artifact conforms to Appendix A constraint 4; it does not show the dispositions are the right ones. |

### `RCY-B` — RCY (Runtime Conversion Yield), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: share of register rows dispositioned to runtime enforcement. |
| Reported value | `1.0000 (6/6)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.RCY.value` |
| Expected value | `1.0` |
| Numerator / denominator | `6 / 6` |
| Interpretation | Runtime Conversion Yield |
| **Claim boundary** | Descriptive only. A lower RCY is not worse; it reflects how many risks the approver routed to runtime. |

### `NDR-B` — NDR (Non-Derivation Rate), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: share of register rows dispositioned non-runtime. |
| Reported value | `0.0000 (0/6)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.NDR.value` |
| Expected value | `0.0` |
| Numerator / denominator | `0 / 6` |
| Interpretation | Non-Derivation Rate |
| **Claim boundary** | Descriptive complement of RCY. Not an error rate. |

### `OPR-B` — OPR (Orphan Predicate Rate), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: no compiled predicate lacks an authorized origin in R union INV. |
| Reported value | `0.0000 (0/9)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.OPR.value` |
| Expected value | `0.0` |
| Numerator / denominator | `0 / 9` |
| Interpretation | Orphan Predicate Rate |
| **Claim boundary** | A compiler guarantee WITHIN Phi-produced bundles. It extends to a deployment only under the explicit runtime acceptance condition. |

### `ODC-B` — ODC (Obligation Disposition Completeness), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: every obligation is disposed. |
| Reported value | `1.0000 (6/6)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.ODC.value` |
| Expected value | `1.0` |
| Numerator / denominator | `6 / 6` |
| Interpretation | Obligation Disposition Completeness |
| **Claim boundary** | Linkage under the declared data model. Not legal compliance. |

### `PTC-B` — PTC (Predicate Traceability Completeness), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: every predicate traces to a risk or to a compiler invariant. |
| Reported value | `1.0000 (9/9)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.PTC.value` |
| Expected value | `1.0` |
| Numerator / denominator | `9 / 9` |
| Interpretation | Predicate Traceability Completeness |
| **Claim boundary** | Structural traceability. Not semantic correctness. |

### `CV-B` — CV (C* Coverage), Case B

| Field | Value |
|---|---|
| Manuscript section | XI-B |
| Claim | Case B: every consequence-class row has a decisive mandatory gate on each authorized hazardous action path. |
| Reported value | `1.0000 (4/4)` |
| Source experiment | primary metrics |
| Reproduce with | `python -m experiments.run_metrics --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/metrics.json` |
| Exact field | `result.per_case.case_b.CV.value` |
| Expected value | `1.0` |
| Numerator / denominator | `4 / 4` |
| Interpretation | C* Coverage |
| **Claim boundary** | Coverage of the DECLARED C* profile. Does not establish that the profile is complete over the harm space. |

### `GD-A` — GD(15), Case A

| Field | Value |
|---|---|
| Manuscript section | IX and XI-B |
| Claim | Gate divergence against the enterprise's predeclared heat-map rule at the declared threshold T_H = 15. |
| Reported value | `3` |
| Source experiment | gate divergence |
| Reproduce with | `python -m experiments.run_gate_divergence --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/gate_divergence.json` |
| Exact field | `result.per_case.case_a.GD_at_declared_threshold` |
| Expected value | `3` |
| Interpretation | Register rows on which the approved gate assignment differs from the scalar heat-map comparator at the declared threshold. Both sums run over all 16 rows, non-runtime dispositions included. |
| **Claim boundary** | Depends on the declared threshold, which is author-set. GD_min is the threshold-free companion. |

### `GDMIN-A` — GD_min, Case A

| Field | Value |
|---|---|
| Manuscript section | IX and XI-B |
| Claim | Minimum gate divergence over all thresholds. GD_min > 0 instantiates the Proposition 1 premise. |
| Reported value | `3` |
| Source experiment | gate divergence |
| Reproduce with | `python -m experiments.run_gate_divergence --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/gate_divergence.json` |
| Exact field | `result.per_case.case_a.GD_min` |
| Expected value | `3` |
| Interpretation | Case A's GD_min > 0 means no monotone threshold on the scalar score reproduces the approved assignment. Case B's GD_min = 0 means that register does admit one -- reported rather than suppressed. |
| **Claim boundary** | Case A's GD_min sums over all 16 rows, three of which carry documented fixture ratings; the published sweep gives the range [2, 5]. |

### `GD-B` — GD(15), Case B

| Field | Value |
|---|---|
| Manuscript section | IX and XI-B |
| Claim | Gate divergence against the enterprise's predeclared heat-map rule at the declared threshold T_H = 15. |
| Reported value | `4` |
| Source experiment | gate divergence |
| Reproduce with | `python -m experiments.run_gate_divergence --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/, cases/case_b/inputs/thresholds.json` |
| Generated result file | `results/final_v2/gate_divergence.json` |
| Exact field | `result.per_case.case_b.GD_at_declared_threshold` |
| Expected value | `4` |
| Interpretation | Register rows on which the approved gate assignment differs from the scalar heat-map comparator at the declared threshold. Both sums run over all 6 rows, non-runtime dispositions included. |
| **Claim boundary** | Depends on the declared threshold, which is author-set. GD_min is the threshold-free companion. |

### `GDMIN-B` — GD_min, Case B

| Field | Value |
|---|---|
| Manuscript section | IX and XI-B |
| Claim | Minimum gate divergence over all thresholds. GD_min > 0 instantiates the Proposition 1 premise. |
| Reported value | `0` |
| Source experiment | gate divergence |
| Reproduce with | `python -m experiments.run_gate_divergence --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/gate_divergence.json` |
| Exact field | `result.per_case.case_b.GD_min` |
| Expected value | `0` |
| Interpretation | GD_min = 0: this register admits a reproducing threshold. Reported rather than suppressed; the Proposition 1 premise is instantiated on Case A only. |
| **Claim boundary** | Case A's GD_min sums over all 16 rows, three of which carry documented fixture ratings; the published sweep gives the range [2, 5]. |

### `GDMIN-SENS` — GD_min fixture-rating sensitivity range

| Field | Value |
|---|---|
| Manuscript section | XII |
| Claim | GD_min = 3 is exact for the published register; over all plausible fixture ratings it would range from 2 to 5. |
| Reported value | `[2, 5]` |
| Source experiment | gate divergence |
| Reproduce with | `python -m experiments.run_gate_divergence --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/gate_divergence.json` |
| Exact field | `result.case_a_fixture_rating_sensitivity.GD_min_range` |
| Expected value | `[2, 5]` |
| Interpretation | Sweep over every (L, I) in {1..5}^2 for R-14, R-15 and R-16 -- 15625 combinations. The published ratings are {"R-14": 12, "R-15": 6, "R-16": 8}. |
| **Claim boundary** | Discloses that the reported GD_min is contingent on three documented fixtures. Neither proposition premise depends on them. |

### `TD` — TD

| Field | Value |
|---|---|
| Manuscript section | XI-B and XI-H |
| Claim | Translation determinism is 1.000: every run reproduced the committed reference canonical payload hash. |
| Reported value | `1.000 (62/62)` |
| Source experiment | determinism |
| Reproduce with | `python -m experiments.run_determinism --runs-per-case 31 --final-v2` |
| Source input files | `cases/case_a/, cases/case_b/, catalog/, invariants/, keys/` |
| Generated result file | `results/final_v2/determinism_summary.json` |
| Exact field | `result.TD.value` |
| Expected value | `1.0` |
| Numerator / denominator | `62 / 62` |
| Interpretation | Semantically equivalent inputs compile to the same canonical payload hash under permutation, locale, time-zone and clean-process variation. |
| **Claim boundary** | TD is a property of the CANONICAL PAYLOAD HASH; the signature envelope need not be byte-identical. Measured on one implementation -- specification-level determinism, which would need a second independent implementation, is NOT established. |

### `TD-DEN` — TD denominator

| Field | Value |
|---|---|
| Manuscript section | XI-B and XI-H |
| Claim | 62 compilation runs in total. |
| Reported value | `62` |
| Source experiment | determinism |
| Reproduce with | `python -m experiments.run_determinism --runs-per-case 31 --final-v2` |
| Source input files | `cases/case_a/, cases/case_b/, catalog/, invariants/, keys/` |
| Generated result file | `results/final_v2/determinism_summary.json` |
| Exact field | `result.TD.denominator` |
| Expected value | `62` |
| Interpretation | 31 runs per case across the two cases. |
| **Claim boundary** | A run count, not an environment count. |

### `TD-RPC` — determinism runs per case

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | 31 runs per case, following the frozen stratified matrix. |
| Reported value | `31` |
| Source experiment | determinism |
| Reproduce with | `python -m experiments.run_determinism --runs-per-case 31 --final-v2` |
| Source input files | `cases/case_a/, cases/case_b/, catalog/, invariants/, keys/` |
| Generated result file | `results/final_v2/determinism_summary.json` |
| Exact field | `result.runs_per_case` |
| Expected value | `31` |
| Interpretation | Strata: {"key_shuffle": 5, "locale": 3, "repeat": 10, "row_shuffle": 10, "timezone": 3}. |
| **Claim boundary** | A stratified design fixed before execution, not a random sample. |

### `TD-STRATA` — determinism stratum breakdown

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | 10 clean repeats, 10 row shuffles, 5 object-key shuffles, 3 locales and 3 time zones. |
| Reported value | `{"key_shuffle": 5, "locale": 3, "repeat": 10, "row_shuffle": 10, "timezone": 3}` |
| Source experiment | determinism |
| Reproduce with | `python -m experiments.run_determinism --runs-per-case 31 --final-v2` |
| Source input files | `cases/case_a/, cases/case_b/, catalog/, invariants/, keys/` |
| Generated result file | `results/final_v2/determinism_summary.json` |
| Exact field | `result.stratum_breakdown` |
| Expected value | `{'key_shuffle': 5, 'locale': 3, 'repeat': 10, 'row_shuffle': 10, 'timezone': 3}` |
| Interpretation | The frozen 10+10+5+3+3 design, 31 per case. |
| **Claim boundary** | Covers the perturbation classes enumerated in the freeze, not all possible input perturbations. |

### `TD-A` — TD, Case A

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | Case A reproduced its reference hash on all 31 runs. |
| Reported value | `1.000 (31/31)` |
| Source experiment | determinism |
| Reproduce with | `python -m experiments.run_determinism --runs-per-case 31 --final-v2` |
| Source input files | `cases/case_a/inputs/, cases/case_a/judgment/, cases/case_a/dispositions/, cases/case_a/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/determinism_summary.json` |
| Exact field | `result.per_case.case_a.TD.value` |
| Expected value | `1.0` |
| Numerator / denominator | `31 / 31` |
| Interpretation | Per-case determinism against reference hash f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536. |
| **Claim boundary** | Same boundary as TD. |

### `TD-B` — TD, Case B

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | Case B reproduced its reference hash on all 31 runs. |
| Reported value | `1.000 (31/31)` |
| Source experiment | determinism |
| Reproduce with | `python -m experiments.run_determinism --runs-per-case 31 --final-v2` |
| Source input files | `cases/case_b/inputs/, cases/case_b/judgment/, cases/case_b/dispositions/, cases/case_b/acs/, catalog/, invariants/` |
| Generated result file | `results/final_v2/determinism_summary.json` |
| Exact field | `result.per_case.case_b.TD.value` |
| Expected value | `1.0` |
| Numerator / denominator | `31 / 31` |
| Interpretation | Per-case determinism against reference hash 2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce. |
| **Claim boundary** | Same boundary as TD. |

### `MC-K` — Monte Carlo draws K

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | The Monte Carlo analysis is executed at K = 250,000 draws. |
| Reported value | `250000` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.draws_K` |
| Expected value | `250000` |
| Interpretation | Frozen draw count; RNG seed 20260201. |
| **Claim boundary** | Sampling under a declared model, not an empirical frequency. |

### `MC-SEED` — Monte Carlo RNG seed

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | The Monte Carlo seed is frozen in the preregistration. |
| Reported value | `20260201` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.rng_seed` |
| Expected value | `20260201` |
| Interpretation | Makes the draw sequence reproducible bit for bit. |
| **Claim boundary** | Reproducibility of the simulation, not of reality. |

### `MC-FPHEAT` — max FP^heat, Case A

| Field | Value |
|---|---|
| Manuscript section | Abstract and XI-G |
| Claim | Rating perturbation moves heat-map gate membership with probability up to 0.321. |
| Reported value | `0.321268` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.max_FP_heat.value` |
| Expected value | `0.321268` |
| Interpretation | Maximum per-risk heat-map flip probability, on row R-06 (approved score 15). |
| **Claim boundary** | AUTHOR-SPECIFIED, prospectively frozen +/-1 ordinal sensitivity model. NOT panel-adjudicated -- no adjudication panel has been convened -- and NOT an estimate of real rating uncertainty. |

### `MC-MCSE` — MCSE at max FP^heat

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | Monte Carlo standard error on the headline flip probability. |
| Reported value | `0.000933926918288578` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.max_FP_heat.mcse` |
| Expected value | `0.000933926918288578` |
| Interpretation | Sampling error at K = 250,000. The paper rounds it to 0.001. |
| **Claim boundary** | Quantifies simulation noise only, never model uncertainty. |

### `MC-FPCSTAR` — max FP^C*, Case A

| Field | Value |
|---|---|
| Manuscript section | Abstract and XI-G |
| Claim | Consequence-class membership does not move at all under the same perturbation. |
| Reported value | `0.0` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json, cases/case_a/inputs/cstar_profile.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.max_FP_cstar` |
| Expected value | `0.0` |
| Interpretation | C* membership is not a function of the perturbed ratings. This corroborates Proposition 3. |
| **Claim boundary** | Structural, given the declared C* profile. Proposition 3 carries the claim; the simulation corroborates it rather than proving it. |

### `MC-CSTAR-PROBE` — C* membership changes over probe draws

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | The C* zero is verified by re-running the approved classifier on 1,000 perturbed draws, not assumed. |
| Reported value | `0 changes in 1000 draws` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json, cases/case_a/inputs/cstar_profile.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.cstar_membership_changes_observed` |
| Expected value | `0` |
| Denominator | `1000` |
| Interpretation | Direct verification rather than an argument from construction. |
| **Claim boundary** | 1,000 probe draws, not all 250,000. |

### `MC-VARIANT` — max FP^heat, renormalisation variant

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | Under a variant that renormalizes out-of-scale mass instead of reassigning it, the maximum flip probability is 0.352. |
| Reported value | `0.352092` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.sensitivity_variant.case_a.max_FP_heat.value` |
| Expected value | `0.352092` |
| Interpretation | Shows the headline figure is not knife-edge on the out-of-scale mass rule. |
| **Claim boundary** | A second declared model, still author-specified. |

### `MC-GD_MEAN` — GD_mean

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | Over the draws, GD at the declared threshold has mean 5.447 against an approved value of 3. |
| Reported value | `5.4466` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.GD_mean` |
| Expected value | `5.4466` |
| Interpretation | Distributional summary under the frozen model. |
| **Claim boundary** | AUTHOR-SPECIFIED, prospectively frozen +/-1 ordinal sensitivity model. NOT panel-adjudicated -- no adjudication panel has been convened -- and NOT an estimate of real rating uncertainty. |

### `MC-GD_MIN_MEAN` — GD_min_mean

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | GD_min has mean 3.226 over the draws. |
| Reported value | `3.226356` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.GD_min_mean` |
| Expected value | `3.226356` |
| Interpretation | Distributional summary under the frozen model. |
| **Claim boundary** | AUTHOR-SPECIFIED, prospectively frozen +/-1 ordinal sensitivity model. NOT panel-adjudicated -- no adjudication panel has been convened -- and NOT an estimate of real rating uncertainty. |

### `MC-EXPECTED_GATE_CHANGES_PER_REGISTER_HEATMAP` — expected_gate_changes_per_register_heatmap

| Field | Value |
|---|---|
| Manuscript section | XI-G |
| Claim | The expected number of heat-map gate changes per register is 3.64. |
| Reported value | `3.642176` |
| Source experiment | Monte Carlo |
| Reproduce with | `python -m experiments.run_monte_carlo --draws 250000 --final-v2` |
| Source input files | `preregistration/monte_carlo_distributions_v1.json, cases/case_a/inputs/assessment.json, cases/case_a/inputs/thresholds.json` |
| Generated result file | `results/final_v2/monte_carlo_summary.json` |
| Exact field | `result.per_case.case_a.expected_gate_changes_per_register_heatmap` |
| Expected value | `3.642176` |
| Interpretation | Distributional summary under the frozen model. |
| **Claim boundary** | AUTHOR-SPECIFIED, prospectively frozen +/-1 ordinal sensitivity model. NOT panel-adjudicated -- no adjudication panel has been convened -- and NOT an estimate of real rating uncertainty. |

### `ADV` — adversarial corpus

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | The adversarial corpus is 62 cases, all passing. |
| Reported value | `62/62 (54 negative, 8 positive controls)` |
| Source experiment | adversarial |
| Reproduce with | `python -m experiments.run_adversarial --final-v2` |
| Source input files | `tests/adversarial/, cases/` |
| Generated result file | `results/final_v2/adversarial.json` |
| Exact field | `result.corpus.passed` |
| Expected value | `62` |
| Denominator | `62` |
| Interpretation | A case counts as passing only if it is rejected with the error code its requirement predicts; code_mismatch = 0, so rejection for an unrelated reason would not count. |
| **Claim boundary** | A finite list of known failure modes. Not a proof of robustness. |

### `STRUCT` — structural checks

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | 26 structural checks, all passing. |
| Reported value | `26/26` |
| Source experiment | adversarial |
| Reproduce with | `python -m experiments.run_adversarial --final-v2` |
| Source input files | `tests/adversarial/` |
| Generated result file | `results/final_v2/adversarial.json` |
| Exact field | `result.structural_checks.passed` |
| Expected value | `26` |
| Denominator | `26` |
| Interpretation | Structural invariants of the compiled bundle. |
| **Claim boundary** | Structural, not semantic. |

### `SEEDS` — validation seeds

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | Three seeded validation rows behave as specified. |
| Reported value | `3/3` |
| Source experiment | adversarial |
| Reproduce with | `python -m experiments.run_adversarial --final-v2` |
| Source input files | `cases/` |
| Generated result file | `results/final_v2/adversarial.json` |
| Exact field | `result.validation_seeds.passed` |
| Expected value | `3` |
| Denominator | `3` |
| Interpretation | Deliberately seeded WC-01 and RC-05 rows, exercised rather than described. |
| **Claim boundary** | Three specific seeded conditions. |

### `INJ` — Case B injection scenarios

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | The thirteen Case B injection scenarios all resolve to SAFE_STATE against a clean PERMIT control. |
| Reported value | `13/13` |
| Source experiment | adversarial |
| Reproduce with | `python -m experiments.run_adversarial --final-v2` |
| Source input files | `cases/case_b/` |
| Generated result file | `results/final_v2/adversarial.json` |
| Exact field | `result.case_b_injection_scenarios.passed` |
| Expected value | `13` |
| Denominator | `13` |
| Interpretation | The eight adversarial attack families and five ASB scenario families enumerated by the consuming enforcement artifact. |
| **Claim boundary** | Decision-level injections against the compiled Case B predicate set. These establish that the compiled bundle refuses to permit under each hazard class the published enforcement artifact enumerates. They are NOT a run over the 284,807-event corpus, establish NO detection performance, and reproduce no figure from [15]. |

### `TESTS` — test count

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | 280 tests pass across the four suites. |
| Reported value | `280/280` |
| Source experiment | test suites |
| Reproduce with | `python -m experiments.run_properties --final-v2` |
| Source input files | `tests/` |
| Generated result file | `results/final_v2/property_tests.json` |
| Exact field | `result.totals.passed` |
| Expected value | `280` |
| Denominator | `280` |
| Interpretation | Unit, property-based, adversarial and integration suites; 0 failures, 0 errors. |
| **Claim boundary** | Tests, not proofs. |

### `PROPS` — properties and generated examples

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | 16 properties over 1,427 generated examples. |
| Reported value | `16 properties, 1427 examples` |
| Source experiment | test suites |
| Reproduce with | `python -m experiments.run_properties --final-v2` |
| Source input files | `tests/properties/` |
| Generated result file | `results/final_v2/property_tests.json` |
| Exact field | `result.property_based.property_count` |
| Expected value | `16` |
| Denominator | `1427` |
| Interpretation | Hypothesis, max_examples = 100 per property. Two properties report fewer because their finite input spaces are EXHAUSTED, which is stronger evidence than 100 random draws. |
| **Claim boundary** | Property-based tests sample; they do not verify, except where the space is exhausted. |

### `TRACE-CLEAN` — clean audit queries empty

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | All six traceability audit queries return empty on the clean fixtures, for both cases. |
| Reported value | `6/6 empty per case, both cases` |
| Source experiment | traceability |
| Reproduce with | `python -m experiments.run_traceability --final-v2` |
| Source input files | `queries/traceability.sql, cases/*/lifecycle/` |
| Generated result file | `results/final_v2/traceability_queries.json` |
| Exact field | `result.summary.all_clean_queries_empty` |
| Expected value | `True` |
| Interpretation | Linkage and temporal-integrity completeness under the declared data model. Queries: Q1, Q2, Q3, Q4, Q5, Q6. |
| **Claim boundary** | Empty result sets on the clean fixtures demonstrate linkage and temporal-integrity completeness UNDER THE DECLARED DATA MODEL. They do not establish legal compliance, semantic correctness, or control effectiveness. The negative controls establish that each query can in fact detect the violation it exists to detect. |

### `TRACE-NEG` — negative controls detected

| Field | Value |
|---|---|
| Manuscript section | XI-H |
| Claim | Every negative control fires. |
| Reported value | `18/18` |
| Source experiment | traceability |
| Reproduce with | `python -m experiments.run_traceability --final-v2` |
| Source input files | `cases/*/lifecycle/negative/` |
| Generated result file | `results/final_v2/traceability_queries.json` |
| Exact field | `result.summary.all_negative_controls_detected` |
| Expected value | `True` |
| Interpretation | Each query can in fact detect the violation it exists to detect, so an empty clean result is informative rather than vacuous. |
| **Claim boundary** | Establishes query sensitivity on seeded faults, not exhaustiveness over all possible faults. |

### `FREEZE` — public_commitment_discharged

| Field | Value |
|---|---|
| Manuscript section | XI-I |
| Claim | The public preregistration commitment is discharged: the freeze tag was pushed to the remote BEFORE the reportable campaign executed. |
| Reported value | `True` |
| Source experiment | freeze verification |
| Reproduce with | `python tools/freeze_check.py --final-v2` |
| Source input files | `preregistration/FREEZE_MANIFEST_V2.sha256, git tag preregister-tier0-v2.2` |
| Generated result file | `results/final_v2/PROVENANCE.json` |
| Exact field | `freeze_verification.public_commitment_discharged` |
| Expected value | `True` |
| Interpretation | Tag preregister-tier0-v2.2 at commit c44f25d6fdb6; the remote tag dereferences to the same commit. |
| **Claim boundary** | Establishes prospective public commitment for TIER-0 only. The Tier-1 held-out register is not covered and is not yet authored. |

### `FREEZE-FILES` — frozen file count

| Field | Value |
|---|---|
| Manuscript section | XI-I |
| Claim | The freeze manifest covers 133 files. |
| Reported value | `133` |
| Source experiment | freeze verification |
| Reproduce with | `python tools/freeze_check.py --final-v2` |
| Source input files | `preregistration/FREEZE_MANIFEST_V2.sha256` |
| Generated result file | `results/final_v2/PROVENANCE.json` |
| Exact field | `freeze_verification.frozen_file_count` |
| Expected value | `133` |
| Interpretation | The scope of the frozen scientific experiment. |
| **Claim boundary** | Frozen scope, NOT repository scope. MANIFEST.sha256 inventories the wider repository and serves a different purpose. |

### `XENV` — cross-environment agreement

| Field | Value |
|---|---|
| Manuscript section | XI-H and XII |
| Claim | TD = 1.000 with identical reference canonical payload hashes on eight independently provisioned environments spanning three operating systems, two machine architectures and six CPython patch versions. |
| Reported value | `8 environments, all TD = 1.000, all reference hashes identical` |
| Source experiment | cross-platform determinism (GitHub Actions matrix, pinned container, local host) |
| Reproduce with | `python -m experiments.check_ci_agreement <downloaded run artifacts> --out CI_STATUS.md` |
| Source input files | `GitHub Actions run 34261657261 artifacts; results/final_v2/cross_environment/` |
| Generated result file | `results/final_v2/CI_STATUS.md` |
| Exact field | `per-leg JSON under results/final_v2/cross_environment/ci/*/determinism_summary.json` |
| Expected value | `TD = 1.0 and matching reference hashes on every leg` |
| Interpretation | Determinism reproduces across the tested supported environments; 496 compilations in total. |
| **Claim boundary** | NOT platform independence. A finite matrix of environments is not the set of all environments; no other operating system and no other Python implementation was exercised. |

Environments exercised:

| Leg | OS | Arch | CPython |
|---|---|---|---|
| local host | macOS 26.6.2 | arm64 | 3.11.15 |
| pinned container | Linux-6.12.76-linuxkit (Debian bookworm) | aarch64 | 3.11.11 |
| CI macos-latest-py3.11 | macOS-26.6.2 | arm64 | 3.11.9 |
| CI macos-latest-py3.12 | macOS-26.6.2 | arm64 | 3.12.10 |
| CI ubuntu-latest-py3.11 | Linux-6.17.0-azure | x86_64 | 3.11.16 |
| CI ubuntu-latest-py3.12 | Linux-6.17.0-azure | x86_64 | 3.12.14 |
| CI windows-latest-py3.11 | Windows-10.0.26100 | AMD64 | 3.11.9 |
| CI windows-latest-py3.12 | Windows-10.0.26100 | AMD64 | 3.12.10 |

---

## Reported as DEFERRED — no value exists, and none is claimed

| Quantity | Section | Status |
|---|---|---|
| SNR | XI-B, XI-C | Primary outcome of the deferred comparative expert study. No adjudication panel has been convened, no practitioner has been recruited, and no participant data exists. |
| DF | XI-B, XI-C | Primary outcome of the same deferred study. |
| Panel-adjudicated reference standard | XI-C | Not produced. The Monte Carlo distributions used in XI-G are therefore author-specified, and the manuscript says so. |
| Held-out register hash | XI-I | The held-out register is not authored; its hash is committed in a Tier-1 freeze published before recruitment opens. |
| Detection performance on the 284,807-event corpus | X | Belongs to the prior work [15]. The compiled Case B bundle was NOT executed against that corpus and no figure from it is reproduced here. |

No script in this repository generates, simulates or approximates human study data, and none of the above appears as a number anywhere in the manuscript.

