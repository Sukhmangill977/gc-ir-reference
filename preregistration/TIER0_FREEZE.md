# TIER0_FREEZE.md — Preregistration freeze for the reportable campaign

**Freeze version:** `tier0-v1`
**Git tag:** `preregister-tier0-v1`
**Scope:** the Tier-0 method-and-artifact measurements (RQ1–RQ4) and the Monte
Carlo rating-robustness analysis. RQ5 is frozen here as **deferred**.

---

## The rule this freeze exists to satisfy

> "Before execution, the following are publicly hash-committed: hypotheses and
> primary outcomes; case artifacts and held-out-register hash; derivation catalog;
> adjudication instrument; thresholds and the C\* definition; compiler commit and
> container digest; randomization seed; Bayesian priors; Monte Carlo distributions
> and seed; exclusion and missing-data rules; and analysis code."
>
> "**The internal selection of frozen elements is not a freeze — the public
> timestamped commitment is.**"
> — Manuscript, Section XI-I

Accordingly: this file, `FREEZE_MANIFEST.sha256` and everything they hash are
committed and **pushed to the public repository, and the tag applied, BEFORE the
final campaign is executed.** The commit and tag timestamps are the evidence. The
final campaign then runs without changing any frozen analysis logic and writes
only to `results/final/`.

---

## Hypotheses and primary outcomes (frozen)

| RQ | Question | Primary outcome | Status |
|---|---|---|---|
| RQ1 | Does every risk receive exactly one approved disposition? | `DC` | measured |
| RQ2 | Do semantically equivalent inputs produce the same canonical payload hash? | `TD` | measured |
| RQ3 | Does consequence-class coverage differ from the predeclared heat-map comparator, and can any scalar threshold reproduce the approved assignment? | `GD(T_H)`, `GD_min` | measured |
| RQ4 | Are obligations, dispositions, predicates and receipts connected without orphan or temporally invalid links? | six audit queries return empty | measured |
| RQ5 | Does the method reduce silent narrowing versus unaided manual practice? | `SNR`, incorrect-gate rate, `DC` | **DEFERRED — not executed, no data** |

Supporting metrics, all measured from the artifacts: `RCY`, `NDR`, `OPR`, `ODC`,
`PTC`, `CV`.

**Success criteria, fixed before execution.**

* `DC = 1.000` is required for release admissibility, and `Φ` refuses to emit a
  bundle otherwise. This is a construction, and the artifact reports it as such.
* `OPR = 0.000` and `CV = 1.000` are required; `Φ` rejects bundles that violate them.
* `TD = 1.000` over ≥ 60 runs is the success criterion for RQ2.
* `GD(T_H)`, `GD_min`, and the Monte Carlo flip probabilities have **no predicted
  value**. Whatever they measure is the reported result. The manuscript's
  provisional figures are not targets and are not consulted by any script.

---

## Declared thresholds and definitions (frozen)

| Item | Value | Where |
|---|---|---|
| Case A declared heat-map threshold `T_H` | **15** | `cases/case_a/inputs/compile_parameters.json` |
| Case B declared heat-map threshold `T_H` | **15** (same, for comparability) | `cases/case_b/inputs/compile_parameters.json` |
| `𝒯` (GD_min candidate set) | distinct observed scores, plus the boundary value immediately above and below each | `src/gcir/coverage.py::threshold_candidates` |
| GD summation scope | **all register rows**, non-runtime dispositions included | `src/gcir/coverage.py::approved_gate_vector` |
| `C*` base profile | the four manuscript kinds, materiality-qualified at `material` | `cases/*/inputs/cstar_profile.json` |
| Reason codes | RC-01, RC-02, RC-03, RC-05 (RC-04 reserved-unused) | `schemas/common.schema.json` |
| Warning codes | WC-01 | `schemas/common.schema.json` |

---

## Randomization and seeds (frozen)

| Purpose | Seed | Where |
|---|---|---|
| Monte Carlo draws | **20260201** | `preregistration/monte_carlo_distributions_v1.json` |
| Monte Carlo sensitivity variant | 20260202 (`seed + 1`) | `experiments/run_monte_carlo.py` |
| Determinism run matrix | **20260101** | `experiments/run_determinism.py::build_matrix` |
| Research signing key derivation | the `KEY_SEED` string | `tools/build_cases.py` |
| RQ5 participant randomization | **not drawn.** To be drawn and published at recruitment close, in a Tier-1 freeze. | — |

---

## Monte Carlo specification (frozen)

`preregistration/monte_carlo_distributions_v1.json`, in full:

* `K = 250,000` draws per risk. Fixed before execution; **no adaptive stopping**.
* Per risk, independently for `L` and `I`: 0.6 on the approved rating, 0.2 on each
  adjacent rating on the 1–5 ordinal scale; out-of-range mass reassigned to the
  approved rating.
* `MCSE(p̂) = √(p̂(1−p̂)/K)`, bounded above by 0.001 at this `K`.
* Exclusions: **none**. Every register row carries a residual rating and is
  included, consistent with the GD definition running over all rows. No draws are
  excluded. Missing data is not applicable: the distributions have finite support.
* Secondary variant: identical but renormalising the out-of-range mass instead of
  reassigning it.

> **PROVENANCE — FROZEN AS A DECLARED DEVIATION FROM THE MANUSCRIPT.**
> Section XI-G attributes these distributions to the independent adjudication
> panel of Section XI-C. **No such panel has been convened.** These are
> author-specified synthetic sensitivity distributions, chosen a priori for
> simplicity and not tuned toward any value. They must never be described as
> independently adjudicated. See `docs/FIXTURE_PROVENANCE.md` FP-020 and
> `paper_update/MEASURED_RESULTS.md` for the manuscript wording this requires.

---

## Bayesian priors (frozen, for the deferred study)

`β₀, β₁ ~ N(0, 2.5²)`; `σ_u, σ_v ~ HalfNormal(0, 1)`; Jeffreys `Beta(½, ½)` for
isolated binomial proportions. Convergence: split-R̂ < 1.01, ESS > 1,000, posterior
predictive checks. Frozen in `RQ5_DEFERRED_PROTOCOL.md`; **not exercised**, because
the study has not been executed.

---

## Exclusion and missing-data rules (frozen)

**Tier-0 measurements.** No exclusions of any kind. Every register row, every
compiled predicate, every determinism run and every Monte Carlo draw is included in
its metric. A failed determinism run would be reported as a failure, not dropped.
An adversarial case rejected with the wrong error code is recorded as
`CODE_MISMATCH`, not silently counted as a pass.

**Deferred study.** See `RQ5_DEFERRED_PROTOCOL.md`.

---

## Determinism matrix (frozen)

≥ 30 runs per case, ≥ 60 total, from a fixed matrix seed so the matrix is identical
on every execution and every platform. Dimensions: key ordering (reverse / shuffle
/ rotate over every object in every input); risk-row ordering; obligation ordering;
ACS, disposition, selection and approval ordering; catalog and invariant ordering;
authority-matrix ordering; integer-to-float numeric re-encoding; five locales
(C, en_US, de_DE, tr_TR, ja_JP); five time zones (UTC, America/Edmonton,
Asia/Kolkata, Pacific/Chatham, Europe/Berlin); and clean-process execution with a
varying `PYTHONHASHSEED`.

Success criterion: every run for a case reproduces that case's committed reference
canonical payload hash. **Signature-envelope bytes are not required to match.**

---

## Compiler commit and container

The compiler commit is the commit this freeze is tagged at; it is recorded in
`FREEZE_MANIFEST.json` and in every final result file's `environment` block.

The container is defined by `Dockerfile`, which pins the base image **by digest**
(`python:3.11.11-slim-bookworm@sha256:6ed5bff4…`) and installs exactly
`requirements.lock`. The built image digest is recorded by the `container` job of
`.github/workflows/reproducibility.yml`. The Dockerfile and the lock file are both
hashed into `FREEZE_MANIFEST.sha256`, so the environment definition is frozen even
where a locally built image digest is not portable.

---

## Held-out register hash — OPENLY OUTSTANDING

Section XI-I lists a held-out-register hash. **No held-out register has been
authored**, so no hash is committed. `preregistration/HELD_OUT_REGISTER.md` records
this gap explicitly rather than committing a hash of a placeholder, which would
create the appearance of a commitment that is not one. It must be discharged in a
Tier-1 freeze before RQ5 recruitment opens.

---

## What this freeze does NOT cover

* RQ5 execution — deferred; see `RQ5_DEFERRED_PROTOCOL.md`.
* The held-out register — see above.
* Cross-platform CI results — measured after this freeze, by the CI matrix, and
  recorded in `results/final/CI_STATUS.md`.
* A Zenodo DOI — no deposit has been made; see `docs/ZENODO_RELEASE_STEPS.md`.

---

## Amendment procedure

If a defect is found in frozen code after this freeze and the final campaign has
already run:

1. Document the defect and its effect on any already-reported number.
2. Increment the freeze version (`tier0-v2`), regenerate `FREEZE_MANIFEST.sha256`,
   and push a new public tag.
3. **Re-run the final campaign from scratch** against the new freeze.
4. Record the amendment, and the reason for it, in `CHANGELOG.md` and in
   `paper_update/PLACEHOLDER_REPLACEMENT_TABLE.md`.

A frozen number is never edited in place.
