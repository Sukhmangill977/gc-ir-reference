# EXPERIMENT_PROTOCOL.md

What each experiment measures, how, and what its result does and does not license.

Every experiment writes a machine-readable result file carrying the git commit,
git tag, Python version, platform and dependency versions that produced it.
Development results go to `results/development/`; the frozen reportable campaign
writes to `results/final/`.

---

## RQ1 — Total disposition

**Question.** Does every risk receive exactly one approved runtime, non-runtime or
accepted-risk disposition?

**Instrument.** `experiments/run_metrics.py`, over the compiled bundle of each case.

**Procedure.** `Φ` asserts `|{Δᵢ}| = |R|` and `∀rᵢ, |Δ(rᵢ)| = 1` before emitting a
payload (`compiler._assert_exactly_one_disposition_per_risk`). The metric script
then *re-derives* the counts from the emitted disposition records rather than
trusting the compiler's own assertion, so the measurement is independent of the
thing it measures.

**Outputs.** `DC`, `RCY`, `NDR`, plus the four disposition counts.

**Does not license.** `DC = 1` says every row was dispositioned, not that any
disposition was correct. `RCY` is descriptive; a higher value is not better.

---

## RQ2 — Translation determinism

**Question.** Do semantically equivalent inputs produce the same canonical payload
hash across supported environments?

**Instrument.** `experiments/run_determinism.py`.

**Procedure.** A fixed run matrix (seed 20260101, so the matrix is identical on
every execution and every platform) of ≥ 30 runs per case, ≥ 60 total. Runs 1–11
exercise each dimension in isolation and then all together; the remainder combine
random subsets. Each run compiles a permuted copy of the committed inputs and
compares the canonical payload hash against a reference compilation.

| Dimension | What varies |
|---|---|
| `key_order` | every JSON object in every input document has its keys reversed, rotated or shuffled |
| `risk_order` | risk register and risk analysis rows permuted |
| `obligation_order` | obligation matrix rows permuted |
| `acs_order` | ACS records, dispositions, judgment selections and approvals permuted |
| `catalog_order` | catalog entries and invariant register entries permuted |
| `authority_order` | authority matrix rows permuted |
| `numeric_form` | integers re-encoded as equal-valued floats (`3` → `3.0`) |
| `locale` | `LC_ALL`/`LANG` cycled over C, en_US, de_DE, tr_TR, ja_JP |
| `timezone` | `TZ` cycled over UTC, America/Edmonton, Asia/Kolkata, Pacific/Chatham, Europe/Berlin |
| `clean_process` | every second run compiles in a freshly spawned interpreter with a new `PYTHONHASHSEED` |

`tr_TR` is included deliberately: the Turkish dotless-i casing rule breaks naive
case-insensitive comparison, so a compiler that lower-cased an identifier anywhere
would fail here.

**Re-signing.** Permuted inputs are re-signed by the *same* authority key. A
signature binds an exact document, so re-ordering an array correctly breaks it; the
permutation models an equivalent authoring order the same authority would have
signed. The signature check is not bypassed — see `docs/FIXTURE_PROVENANCE.md`
FP-024 and adversarial cases ADV-018/019/020.

**Success criterion.** All runs for a case produce that case's reference canonical
payload hash. **Signature-envelope bytes are not required to match** (Section VI-C).

**Outputs.** `results/final/determinism_runs.csv` (one row per run: run id, case,
permutation, seed, environment, locale, timezone, hash, reference hash, pass/fail)
and `determinism_summary.json`.

**Does not license.** This runs on one host operating system. It supports
determinism across the *tested* permutations, locales, time zones and process
boundaries. Cross-platform replication is measured separately by CI. **No claim of
universal platform independence follows from this experiment.**

---

## RQ3 — Gate selection and divergence

**Question.** Does consequence-class coverage differ from the predeclared heat-map
comparator, and can any scalar threshold reproduce the approved gate assignment?

**Instrument.** `experiments/run_gate_divergence.py`.

**Procedure.**
1. Derive `gᵢ` per register row from the compiled gate map: `gᵢ = 1` iff the row
   carries at least one mandatory gate. Rows with a non-runtime, accepted or
   unresolved disposition carry ratings but no gate, so `gᵢ = 0` — and they are
   **included** in both sums, as Section IX requires.
2. `sᵢ = Lᵢ^res · Iᵢ^res`.
3. `GD(T_H) = Σᵢ 𝟙[gᵢ ≠ 𝟙[sᵢ ≥ T_H]]` at the declared frozen `T_H`.
4. `GD_min = min_{t∈𝒯} Σᵢ 𝟙[gᵢ ≠ 𝟙[sᵢ ≥ t]]`, with `𝒯` the distinct observed
   scores and the boundary values immediately above and below each.
5. Detect the Proposition 1 premise (a pair with `sᵢ < s_j`, `gᵢ = 1`, `g_j = 0`)
   and the Proposition 2 premise (equal scores with divergent gates).
6. **Sensitivity sweep** over every `(L, I)` in `{1..5}²` for Case A's three
   fixture-rated non-runtime rows — 15,625 combinations — reporting the `GD_min`
   distribution (see FP-014).

**Outputs.** `gate_divergence.json`, `gate_divergence_heatmap.csv`.

**Does not license.** Detecting the premise of a proposition is not proving the
proposition; the propositions are proved in the manuscript. What is measured is
that the pinned register *instantiates* the premise, and what `GD_min` actually is.

---

## RQ4 — Temporal traceability

**Question.** Are obligations, dispositions, predicates and receipts connected
without orphan or temporally invalid links?

**Instrument.** `experiments/run_traceability.py` over the SQLite projection built
by `src/gcir/traceability.py`; queries in `queries/traceability.sql`.

**Procedure.** Two passes.

*Clean pass* — all six audit queries must return empty over the committed fixtures.

*Negative-control pass* — for each query, a deliberately corrupted projection is
built and the query must fire. **A query that never fires proves nothing**, so a
clean pass alone would be weak evidence. Nine controls per case:

| Query | Controls |
|---|---|
| Q1 obligations without an approved disposition | an obligation no register row cites |
| Q2 risks without exactly one disposition | a removed disposition; a duplicated disposition |
| Q3 predicates without an authorized origin | a predicate whose `origin_id` resolves to nothing |
| Q4 receipts whose bundle was invalid at decision time | a post-retirement receipt; a receipt citing a hash that does not bind |
| Q5 actuation without a prior committed receipt | an actuation with no receipt; a receipt committed after actuation |
| Q6 registry records lacking valid signing authority | a revocation signed by a key outside `authorized_signing_keys` |

**Outputs.** `traceability_queries.json`, `traceability_queries.csv`.

**Does not license.** Empty result sets demonstrate linkage and temporal-integrity
completeness **under the declared data model**. They do not establish legal
compliance, semantic correctness, or control effectiveness.

---

## RQ5 — Human translation quality

**DEFERRED.** Preregistered in `preregistration/RQ5_DEFERRED_PROTOCOL.md` and
executed as an independent follow-up study. No adjudication panel has been
convened, no participant has been recruited, and no participant data exists.
`SNR` and `DF` are reported as `DEFERRED`, never as numbers. **No
comparative-superiority claim over unaided manual practice is made anywhere in this
artifact.**

---

## Monte Carlo rating robustness (Section XI-G)

**Instrument.** `experiments/run_monte_carlo.py`, specification frozen in
`preregistration/monte_carlo_distributions_v1.json`.

**Procedure.** `K = 250,000` draws per risk, seed 20260201 fixed before execution.
Per risk and independently for `L` and `I`: probability 0.6 on the approved rating,
0.2 on each adjacent rating on the 1–5 scale, out-of-range mass reassigned to the
approved rating. Then `sᵢ⁽ᵏ⁾ = Lᵢ⁽ᵏ⁾Iᵢ⁽ᵏ⁾`, `hᵢ⁽ᵏ⁾ = 𝟙[sᵢ⁽ᵏ⁾ ≥ T_H]`,
`FPᵢ^heat = (1/K)Σₖ 𝟙[hᵢ⁽ᵏ⁾ ≠ hᵢ^approved]`.

`FPᵢ^{C*}` is **verified rather than assumed**: the real `C*` classifier is re-run
on 1,000 randomly selected perturbed draws per case and the number of membership
changes is reported. A non-zero count would mean a rating dependence had leaked
into gate assignment.

Also reported: expected gate changes per register, the `GD(T_H)` and `GD_min`
distributions over draws, and `MCSE(p̂) = √(p̂(1−p̂)/K)` — bounded above by 0.001
at this `K`. A secondary variant renormalises the boundary mass instead of
reassigning it, so the reader can see how much that convention matters.

**Provenance — read this before citing any number from it.** The manuscript
attributes these distributions to the independent adjudication panel. No panel
exists. These are **author-specified synthetic sensitivity distributions**, chosen
a priori for simplicity and not tuned to any target. The result is a sensitivity
analysis under a declared perturbation model; it is not an estimate of real rating
uncertainty and must not be described as independently adjudicated. See FP-020.

---

## Adversarial and property-based testing (Section XI-H)

**Instruments.** `experiments/run_adversarial.py` over the corpus in
`experiments/adversarial_cases.py`; `experiments/run_properties.py` over
`tests/`.

**Adversarial procedure.** Each case mutates a deep copy of a loaded case's
documents, re-signs it with the legitimate authority (except the three cases
testing signature integrity itself), then runs it through **both** defence layers:
JSON Schema validation and the Appendix A cross-field constraints. Both outcomes
are recorded, because which layer catches a given defect first is an implementation
detail rather than a claim.

* A case that **must be rejected** passes only if it is rejected *with one of its
  expected error codes*. Rejection with an unrelated code is recorded as
  `CODE_MISMATCH`, not as a pass — rejecting for the wrong reason is not evidence
  that the intended constraint works.
* A case that **must compile** (a positive control) passes only if it compiles.
  Positive controls are included because a suite that only ever expects rejection
  cannot distinguish a correct compiler from one that rejects everything.

Structural checks additionally cover payload mutation, post-retirement bundle use,
lifecycle signing authority, precedence and the runtime acceptance condition.
Seeded validation rows exercise `WC-01`, `RC-05` and `RC-02`.

**Property-based procedure.** Hypothesis, `max_examples = 100` per property, over
*synthetic* assessments rather than perturbations of the two cases — so the
properties are tested over a space of registers rather than two points in it. Two
properties report fewer than 100 examples because their input spaces are finite and
small (3×3×2 = 18 and 3×3 = 9); Hypothesis exhausts them. **An exhaustive check of
a finite space is stronger than 100 draws from it**, and the counts are reported as
measured rather than padded.

**Outputs.** `adversarial.json`, `adversarial_cases.csv`, `property_tests.json`,
JUnit XML per suite under `test_reports/`.

---

## Cross-platform conformance

**Instrument.** `.github/workflows/determinism.yml`, matrix over
`ubuntu-latest`, `windows-latest`, `macos-latest`.

**Procedure.** Each runner compiles both cases and compares the canonical payload
hash against the reference hashes committed in `cases/*/expected/reference_hashes.json`.

**Wording this licenses.** "Deterministic across the tested supported
environments." **Never** "platform independent". A CI matrix of three runner images
is not the set of all environments.
