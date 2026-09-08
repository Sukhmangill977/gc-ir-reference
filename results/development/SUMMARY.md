# Measured results -- DEVELOPMENT campaign

> **These are DEVELOPMENT results and are not reportable numbers.**
> The reportable campaign runs after the public preregistration freeze
> and writes to `results/final/`.

## Environment and provenance

| Field | Value |
|---|---|
| git commit | `fed211aece4064cba1479138a9edca0b2a27e209` |
| git describe | `fed211a-dirty` |
| git tag (exact) | `none at this commit` |
| working tree clean | False |
| Python | 3.11.15 (CPython) |
| platform | macOS-26.6.2-arm64-arm-64bit |
| machine | arm64 |
| cryptography | 44.0.0 |
| hypothesis | 6.122.3 |
| jsonschema | 4.23.0 |
| numpy | 2.2.1 |
| pytest | 8.3.4 |

## Case artifacts

| | Case A | Case B |
|---|---|---|
| evidence class | synthetic | forensic_reconstruction |
| canonical payload hash (SHA-256) | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| register rows | 16 | 6 |
| obligations | 12 | 6 |
| Approved Control Specifications | 16 | 6 |
| compiled predicates | 19 | 9 |
| -- risk-derived | 16 | 6 |
| -- compiler-invariant | 3 | 3 |
| mandatory gates | 16 | 9 |
| C* risks | 6 | 4 |
| warnings | 0 | 0 |

## Primary metrics (Section XI-B)

| Metric | Case A | Case B | Definition |
|---|---|---|---|
| **DC** | 1.0000 (16/16) | 1.0000 (6/6) | |{r_i : Delta_i in (runtime, nonruntime, accepted)}| / |R| |
| **RCY** | 0.8125 (13/16) | 1.0000 (6/6) | |{r_i : Delta_i = runtime(D_i)}| / |R| |
| **NDR** | 0.1875 (3/16) | 0.0000 (0/6) | |{r_i : Delta_i in (nonruntime, accepted)}| / |R| |
| **OPR** | 0.0000 (0/19) | 0.0000 (0/9) | |{p in P : origin(p) not in R union INV}| / |P| |
| **ODC** | 1.0000 (12/12) | 1.0000 (6/6) | |{o in O : o ~> runtime or nonruntime or accepted}| / |O| |
| **PTC** | 1.0000 (19/19) | 1.0000 (9/9) | |{p in P : p ~> risk or compiler invariant}| / |P| |
| **CV** | 1.0000 (6/6) | 1.0000 (4/4) | |{r_i : C*(c_i)=1 and each hazardous action path mandatorily gated}| / |{r_i : C*(c_i)=1}| |
| **GD(T_H)** | 3 at T_H=15 | 4 at T_H=15 | GD(T_H) = sum_i 1[g_i != 1[s_i >= T_H]] |
| **GD_min** | 3 | 0 | min over t of sum_i 1[g_i != 1[s_i >= t]] |
| **TD** | 1.0000 (30/30) | 1.0000 (30/30) | sum_k 1[H_k = H_ref] / N |
| **SNR** | DEFERRED | DEFERRED | RQ5 -- no adjudication panel convened |
| **DF** | DEFERRED | DEFERRED | RQ5 -- no adjudication panel convened |

Disposition counts -- Case A: {"accepted": 0, "nonruntime": 3, "runtime": 13, "unresolved": 0}; Case B: {"accepted": 0, "nonruntime": 0, "runtime": 6, "unresolved": 0}.

Gate-source breakdown -- Case A: {"advisory/SOFT": 2, "mandatory/C_STAR": 7, "mandatory/OTHER_MANDATORY": 9, "weighted/SOFT": 1}; Case B: {"mandatory/C_STAR": 4, "mandatory/OTHER_MANDATORY": 5}.

## Translation determinism (RQ2)

**TD = 1.0000 (60/60 runs).**

| | value |
|---|---|
| total runs | 60 |
| runs per case | 30 |
| matching the reference hash | 60 |
| Case A reference hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| Case B reference hash | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| locales exercised | C, de_DE.UTF-8, en_US.UTF-8, ja_JP.UTF-8, tr_TR.UTF-8 |
| time zones exercised | America/Edmonton, Asia/Kolkata, Europe/Berlin, Pacific/Chatham, UTC |
| failures | 0 |

Permutation dimensions:
* key_order (reverse / shuffle / rotate, applied to every object in every input)
* risk_order
* obligation_order
* acs_order
* catalog_order
* authority_order
* numeric_form (integer re-encoded as equal float)
* locale
* timezone
* clean_process (fresh interpreter, new PYTHONHASHSEED)

> This experiment measures determinism across the permutations, locales, time zones and process boundaries listed above, on ONE host operating system. Cross-platform replication is measured separately by the GitHub Actions matrix (ubuntu / windows / macOS). No claim of universal platform independence is supported by this run alone.

## Gate divergence (RQ3)

### case_a

* declared heat-map threshold T_H = **15**
* **GD(15) = 3** over all 16 register rows
  * divergent rows: R-09 (s=12, approved g=1, heat-map h=0), R-10 (s=10, approved g=1, heat-map h=0), R-13 (s=10, approved g=1, heat-map h=0)
* **GD_min = 3**, attained at t in [9, 10, 13, 14, 15]
* Proposition 1 premise (score inversion): **holds** -- 6 inverted pairs
* Proposition 2 premise (score collision with divergent gates): **holds**
  * at s = 12: gated ['R-09'], ungated ['R-04', 'R-12', 'R-14']

### case_b

* declared heat-map threshold T_H = **15**
* **GD(15) = 4** over all 6 register rows
  * divergent rows: B-03 (s=12, approved g=1, heat-map h=0), B-04 (s=5, approved g=1, heat-map h=0), B-05 (s=10, approved g=1, heat-map h=0), B-06 (s=10, approved g=1, heat-map h=0)
* **GD_min = 0**, attained at t in [4, 5]
* Proposition 1 premise (score inversion): **does not hold**
* Proposition 2 premise (score collision with divergent gates): **does not hold**

### Sensitivity of Case A GD_min to fixture-rated rows

The manuscript does not state L x I for the three non-runtime rows R-14, R-15, R-16, and both GD sums run over all register rows. Sweeping every (L, I) in {1..5}^2 for each of them over 15625 combinations:

* actual GD_min with the committed ratings {"R-14": 12, "R-15": 6, "R-16": 8}: **3**
* range across the sweep: **[2, 5]**
* share of the grid giving the actual value: 0.482
* distribution: {"2": 3375, "3": 7534, "4": 4068, "5": 648}

> GD_min over the whole register depends in part on the ratings assigned to rows the manuscript leaves unrated. The reported GD_min is the value for the committed fixture ratings; this sweep states the range the choice could have produced, so the number is not silently contingent.

## Monte Carlo rating robustness (Section XI-G)

> **Manuscript Section XI-G attributes the rating distributions to the independent adjudication panel of Section XI-C. NO SUCH PANEL HAS BEEN CONVENED. The distributions used here are author-specified synthetic sensitivity distributions constructed from a single a-priori rule (below). They are NOT independently adjudicated and must not be described as such. See docs/FIXTURE_PROVENANCE.md FP-020 and paper_update/MEASURED_RESULTS.md for the exact manuscript wording this requires.**

* K = **250000** draws per risk; seed = 20260201 (frozen before execution)
* perturbation rule: `symmetric_pm1_ordinal_with_clamping` -- 0.6 on the approved rating, 0.2 on each adjacent rating, out-of-range mass reassign_to_approved

| | Case A | Case B |
|---|---|---|
| max per-risk heat-map flip probability FP^heat | **0.321268** (R-06) | **0.317980** (B-01) |
| MCSE at that estimate | 0.000934 | 0.000931 |
| mean FP^heat across the register | 0.227636 | 0.199045 |
| max per-risk C* flip probability FP^C* | **0.000000** | **0.000000** |
| expected heat-map gate changes per register | 3.6422 | 1.1943 |
| expected C* gate changes per register | 0.0000 | 0.0000 |
| C* membership changes observed in 1000 re-classified draws | 0 | 0 |
| MCSE upper bound at this K | 0.001000 | 0.001000 |
| GD(T_H) mean over draws (approved = 3 / 4) | 5.4466 | 4.0015 |
| GD_min mean over draws | 3.2264 | 0.0000 |

Case A GD(T_H) distribution over draws: {"0": 57, "1": 854, "10": 1534, "11": 267, "12": 29, "13": 2, "2": 5744, "3": 20524, "4": 44115, "5": 59724, "6": 56250, "7": 36918, "8": 17759, "9": 6223}

Case A GD_min distribution over draws: {"0": 1065, "1": 10814, "2": 43730, "3": 90850, "4": 81940, "5": 21601}

> The C* classifier was re-run on 1000 randomly selected perturbed draws. A non-zero count here would mean a rating dependence had leaked into gate assignment. The count is the measurement, not an assumption.

Secondary sensitivity (boundary mass renormalised instead of reassigned): max FP^heat = 0.352092 on Case A.

## Adversarial suite (Section XI-H)

| | count |
|---|---|
| corpus cases | 59 |
| -- negative (must be rejected) | 52 |
| -- positive controls (must compile) | 7 |
| PASS | 59 |
| FAIL | 0 |
| CODE_MISMATCH | 0 |
| ERROR | 0 |
| structural checks passed | 24/24 |
| seeded validation rows passed | 3/3 |

Seeded validation rows (Section IX): VS-01 exercises RC-05 (PASS), VS-02 exercises WC-01 (PASS), VS-03 exercises RC-02 (PASS)

> A case rejected with the WRONG error code is recorded as CODE_MISMATCH, not counted as a pass: rejecting for an unrelated reason is not evidence that the intended constraint works.

## Test suites and property-based testing

| Suite | tests | passed | failed | errors |
|---|---|---|---|---|
| unit | 100 | 100 | 0 | 0 |
| properties | 16 | 16 | 0 | 0 |
| adversarial | 134 | 134 | 0 | 0 |
| integration | 25 | 25 | 0 | 0 |
| **total** | **275** | **275** | **0** | **0** |

Property-based testing: **16 properties**, `max_examples = 100`, **1427 generated examples in total**.

| Property | generated examples |
|---|---|
| `test_any_payload_edit_changes_the_hash` | 100 |
| `test_authority_closure_rejects_every_tuple_outside_the_matrix` | 100 |
| `test_authority_closure_rejects_unapproved_parameters` | 100 |
| `test_c_star_coverage_holds_exactly_when_every_hazardous_path_is_gated` | 100 |
| `test_canonicalization_is_invariant_under_object_key_order` | 100 |
| `test_commit_before_actuate_ordering` | 100 |
| `test_forbidden_payload_keys_are_always_detected` | 100 |
| `test_mandatory_gate_requires_on_unknown_fail` | 18 |
| `test_mandatory_gate_requires_safe_state` | 9 |
| `test_origin_closure` | 100 |
| `test_predicate_cardinality_is_independent_of_risk_cardinality` | 100 |
| `test_supporting_predicates_never_satisfy_coverage` | 100 |
| `test_total_disposition_is_exactly_one_per_risk` | 100 |
| `test_unknown_on_a_mandatory_gate_never_resolves_to_pass` | 100 |
| `test_valid_at_conjuncts` | 100 |
| `test_valid_at_requires_the_payload_hash_to_bind` | 100 |

> settings.max_examples is 100 for every property. Two properties report fewer: their input spaces are finite and small (gate_type x on_unknown x required = 3 x 3 x 2 = 18, and gate_type x on_fail = 3 x 3 = 9), so Hypothesis stops once the space is EXHAUSTED. An exhaustive check of a finite space is stronger evidence than 100 random draws from it, not weaker; the counts are reported as measured rather than padded.

## Traceability audit queries (RQ4)

| Query | Detects | Case A clean | Case B clean |
|---|---|---|---|
| **Q1** Obligations without an approved disposition | an obligation that no risk disposes, or whose risks are unresolved | 0 rows | 0 rows |
| **Q2** Risks without exactly one disposition | a risk with zero dispositions, or with more than one | 0 rows | 0 rows |
| **Q3** Predicates without a risk or compiler-invariant origin | an orphan predicate: origin(p) not in R union INV | 0 rows | 0 rows |
| **Q4** Receipts whose bundle was not valid at decision time | a receipt whose payload hash does not bind, whose bundle was not yet effective, or whose bundle the registry had already retired at decision time | 0 rows | 0 rows |
| **Q5** Actuation without a temporally prior committed receipt | an actuation with no receipt, or whose receipt violates authorization_time <= evidence_commit_time < actuation_time | 0 rows | 0 rows |
| **Q6** Lifecycle-registry records lacking a valid signing authority | a registry record signed by a key outside authorized_signing_keys, or whose signature does not verify | 0 rows | 0 rows |

Negative controls -- each query must fire on a deliberately corrupted fixture:

| Case | Query | Control | Detected | Rows |
|---|---|---|---|---|
| case_a | Q1 | orphan obligation | yes | 1 |
| case_a | Q2 | risk with no disposition | yes | 1 |
| case_a | Q2 | risk with two dispositions | yes | 1 |
| case_a | Q3 | orphan predicate | yes | 1 |
| case_a | Q4 | post-retirement receipt | yes | 1 |
| case_a | Q4 | wrong bundle hash | yes | 1 |
| case_a | Q5 | actuation with no receipt | yes | 1 |
| case_a | Q5 | commit after actuation | yes | 1 |
| case_a | Q6 | unauthorized registry signature | yes | 1 |
| case_b | Q1 | orphan obligation | yes | 1 |
| case_b | Q2 | risk with no disposition | yes | 1 |
| case_b | Q2 | risk with two dispositions | yes | 1 |
| case_b | Q3 | orphan predicate | yes | 1 |
| case_b | Q4 | post-retirement receipt | yes | 1 |
| case_b | Q4 | wrong bundle hash | yes | 1 |
| case_b | Q5 | actuation with no receipt | yes | 1 |
| case_b | Q5 | commit after actuation | yes | 1 |
| case_b | Q6 | unauthorized registry signature | yes | 1 |

* all clean queries empty: **True**
* all negative controls detected: **True**

> Empty result sets on the clean fixtures demonstrate linkage and temporal-integrity completeness UNDER THE DECLARED DATA MODEL. They do not establish legal compliance, semantic correctness, or control effectiveness. The negative controls establish that each query can in fact detect the violation it exists to detect.

## Deferred and out of scope

* **RQ5 (comparative expert study)** is preregistered and DEFERRED. No adjudication panel has been convened, no participant data exists, and no comparative-superiority claim is made. SNR and DF are therefore reported as DEFERRED, not as numbers. See `preregistration/RQ5_DEFERRED_PROTOCOL.md`.
* **The Monte Carlo rating distributions are author-specified**, not panel-adjudicated. See `docs/FIXTURE_PROVENANCE.md` FP-020.
* **Cross-platform determinism** is measured by the GitHub Actions matrix (ubuntu / windows / macOS), not by this run. See `results/final/CI_STATUS.md`.
* **Detection performance, production impact and false-denial rates** are out of scope; they require the shadow-mode deployment identified as future work.
* The 284,807-event golden-trace conformance run of [15] is **not** reproduced here and is not claimed as evidence for this paper.

---

Generated by `python -m experiments.make_summary`.
