# MEASURED_RESULTS.md — publication-ready wording

Exact replacement text for each place the manuscript reports an empirical result
or an empirical status. Every figure below is read from `results/final/`.

**Campaign:** final, executed after the Tier-0 freeze
(`preregister-tier0-v1`, commit `196820b23a632d56c4575dba3def71247b343f6a`).
**Environment:** macOS 26.6.2 arm64, CPython 3.11.15; jsonschema 4.23.0,
cryptography 44.0.0, numpy 2.2.1, hypothesis 6.122.3, pytest 8.3.4.
**Freeze verification:** `results/final/freeze_verification.json` — 117 frozen
files all match the manifest at the freeze commit; the results were produced at
that commit; no frozen file changed in between.

Bracketed `⟨…⟩` markers are values that can only be filled in after the
repository is pushed.

---

## 1. Abstract

Replace the results sentence:

> On the two pinned case artifacts the method achieves total disposition
> (DC = 1.000), zero orphan predicates, complete predicate and obligation
> traceability, full consequence-class coverage, and translation determinism of
> **1.000 over 60 compilation runs (30 per case)**; gate divergence against the
> enterprise's predeclared heat-map rule is GD(15) = 3 with GD_min = 3 on Case A,
> and Monte Carlo rating perturbation under a declared ±1 ordinal model moves
> heat-map gate membership with probability up to 0.321 (MCSE 0.001) while
> consequence-class membership does not move at all.

Two changes from the current text: **31 → 60 runs**, and the qualifier
**"under a declared ±1 ordinal model"** on the Monte Carlo figure, which is
required by §5 below.

---

## 2. Section IX — Case A

### 2.1 Add the hash

> The Case A artifact set is hash-pinned: the SHA-256 of the RFC 8785 canonical
> bundle payload is
> `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536`.

Case A compiles to **19 predicates** — 16 risk-derived from 16 Approved Control
Specifications, plus 3 compiler invariants (`INV-VERSION`,
`INV-EVIDENCE-COMMIT`, `INV-AUTHORITY-CLOSURE`) — over 16 register rows and 12
obligations, with **16 mandatory gates** and **0 warnings**.

### 2.2 Publish the three non-runtime rows' ratings — REQUIRED

The Section IX table gives `L × I` for the thirteen runtime rows only, but the
`GD` sums run over all sixteen. `GD_min = 3` is therefore not reproducible from
the published table alone. Add to the table:

| risk_id | L×I |
|---|---|
| R-14 concentration/resilience | 12 (L=3, I=4) |
| R-15 unprofessional or reputationally damaging tone | 6 (L=3, I=2) |
| R-16 third-party model vendor commercial viability | 8 (L=2, I=4) |

And add the accompanying sentence:

> Because both divergence sums run over all sixteen rows, the three non-runtime
> rows' residual ratings enter the computation. Under a sweep of every (L, I) in
> {1…5}² for those three rows, GD_min ranges from 2 to 5; the value of 3 reported
> here is the value for the ratings above, which are published with the artifact.

### 2.3 Correct the collision description — REQUIRED

Current text: *"the three-way collision at s = 12 (R-04, R-09, R-12 with gates 0,
1, 0) instantiates Proposition 2"*.

On the pinned artifact the score-12 collision has **four** members, because R-14
also rates 12. Recommended replacement, which keeps the claim on the rows the
manuscript states:

> …and the collision at s = 12 among the runtime rows — R-04, R-09 and R-12, with
> gates 0, 1, 0 — instantiates Proposition 2: no function of the scalar score,
> monotone or otherwise, reproduces this assignment.

Optionally add: *"On the released artifact the non-runtime row R-14 also rates 12
and is ungated, widening the collision to four rows without altering the result."*

### 2.4 Strengthen the Proposition 1 sentence (optional)

> The inversion (s_{R-10} = 10 < 12 = s_{R-04}, g_{R-10} = 1, g_{R-04} = 0)
> satisfies Proposition 1, so GD_min ≥ 1 on this register; the released artifact
> contains **six** such inverted pairs.

### 2.5 The measured divergence sentence

> Measured on the pinned artifact, against the enterprise's predeclared threshold
> T_H = 15: **GD(15) = 3** — R-09, R-10 and R-13 carry mandatory gates by class
> while scoring below the threshold — and **GD_min = 3**, attained at
> t ∈ {9, 10, 13, 14, 15}, so no scalar threshold reproduces the approved
> assignment more closely than the declared one.

---

## 3. Section X — Case B

Replace `[PENDING: hash-pinned Case B artifact release]`:

> The Case B artifact set is hash-pinned: the SHA-256 of the RFC 8785 canonical
> bundle payload is
> `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce`.

Optional addition:

> Measured on the pinned Case B artifact at the same declared threshold,
> GD(15) = 4 and **GD_min = 0**, attained at any t ≤ 5 — confirming that a
> register in which every row is gated admits a reproducing scalar threshold, and
> that the separation results rest on Case A.

The evidence-classification paragraph is **unchanged**: the 284,807-event run of
[15] remains a golden-trace conformance result, is not reproduced here, and is not
presented as detection evidence. The register remains a forensic reconstruction;
the released artifact records this as a machine-readable field
(`"case_class": "forensic_reconstruction"`).

---

## 4. Section XI-B — the metrics table

| Metric | Result to print |
|---|---|
| Disposition Completeness (DC) | **1.000 (16/16)** — release-admissible |
| Runtime Compilability Yield (RCY) | **0.8125 (13/16)** — descriptive, not a quality target |
| Non-Runtime Disposition Rate (NDR) | **0.1875 (3/16)** — descriptive |
| Orphan Predicate Rate (OPR) | **0.000 (0/19)** — required 0 |
| Obligation Disposition Completeness (ODC) | **1.000 (12/12)** |
| Predicate Traceability Completeness (PTC) | **1.000 (19/19)** |
| C\* Coverage (CV) | **1.000 (6/6)** — required 1 |
| Translation Determinism (TD) | **1.000 (60/60 runs; 30 per case)** |
| Gate Divergence | Case A: **GD(15) = 3, GD_min = 3** · Case B: **GD(15) = 4, GD_min = 0** |
| Silent-Narrowing Rate (SNR) | primary outcome of the deferred study · **[TO REPORT]** |
| Field-Level Derivation Fidelity (DF) | primary outcome of the deferred study · **[TO REPORT]** |

Case B, where it differs: DC 1.000 (6/6), RCY 1.000 (6/6), NDR 0.000 (0/6),
OPR 0.000 (0/9), ODC 1.000 (6/6), PTC 1.000 (9/9), CV 1.000 (4/4).

---

## 5. Section XI-G — Monte Carlo. **MANDATORY CORRECTION.**

### The problem

The manuscript currently reads:

> "For each risk rᵢ, **the independent panel** freezes discrete probability masses
> over plausible ratings: Lᵢ⁽ᵏ⁾ ~ Cat(π_{Lᵢ}), Iᵢ⁽ᵏ⁾ ~ Cat(π_{Iᵢ})."

**No independent adjudication panel has been convened.** The panel described in
Section XI-C belongs to the deferred RQ5 protocol. As written, the manuscript
attributes a methodological input to a body that does not exist, and a reader
would reasonably take the Monte Carlo result to carry independent adjudication it
does not have.

### Replacement text

> For each risk rᵢ, discrete probability masses over plausible ratings are fixed
> before execution: Lᵢ⁽ᵏ⁾ ~ Cat(π_{Lᵢ}), Iᵢ⁽ᵏ⁾ ~ Cat(π_{Iᵢ}). **In the analysis
> reported here these masses are author-specified rather than
> panel-adjudicated**: a symmetric ±1 ordinal perturbation placing probability 0.6
> on the approved rating and 0.2 on each adjacent rating of the enterprise 1–5
> scale, with mass falling outside the scale reassigned to the approved rating.
> The rule was chosen a priori for simplicity, frozen in the artifact's
> preregistration before any result was computed, and is not tuned toward any
> value. It is a **declared sensitivity model, not an estimate of how uncertain
> real enterprise ratings are.** When the independent panel of Section XI-C is
> convened for the deferred comparative study, the analysis is to be re-run under
> panel-adjudicated masses and reported separately.

### The results sentence

> Measured on Case A at K = 250,000 under that model: the maximum per-risk
> heat-map flip probability is **0.321** (MCSE 0.001, on R-06), concentrated on
> rows adjacent to T_H, and the expected number of heat-map gate changes per
> register is **3.64**. `FPᵢ^{C*} = 0.000` across the register: re-running the
> approved consequence-class classifier on 1,000 randomly selected perturbed draws
> produced **no** change in C\* membership, as the coverage rule reads the
> consequence descriptor and never reads L or I. Gate membership under the
> coverage rule does not move with rating uncertainty, conditional on unchanged
> consequence classification and policy version.

### Optional additions Section XI-G already promises

> Over the 250,000 draws the distribution of GD(15) has mean **5.447** on Case A
> against an approved value of 3, and the distribution of GD_min has mean
> **3.226**. On Case B, GD_min was **0 in all 250,000 draws**. Under a secondary
> variant that renormalises the out-of-scale mass instead of reassigning it, the
> maximum per-risk flip probability is **0.352**.

### Section XI-C

Add, so the two sections do not contradict each other:

> The panel has not yet been convened; the reference standard, and any
> panel-adjudicated input to the sensitivity analysis of Section XI-G, are part of
> the deferred study.

---

## 6. Section XI-H — determinism and adversarial testing

Replace the "Measured:" sentence:

> Measured: **TD = 1.000 over 60 compilation runs (30 per case)** — repeated runs;
> object-key reordering (reversal, rotation and shuffling applied to every object
> in every input document); permutation of the risk register, risk analysis,
> obligation matrix, authority matrix, Approved Control Specifications,
> dispositions, judgment-record selections and approvals, catalog entries and
> invariant register; re-encoding of integers as equal-valued floats; five locales
> (C, en_US.UTF-8, de_DE.UTF-8, tr_TR.UTF-8, ja_JP.UTF-8); five time zones (UTC,
> America/Edmonton, Asia/Kolkata, Pacific/Chatham, Europe/Berlin); and
> clean-process execution under varying PYTHONHASHSEED. Runs were executed on the
> declared host environment (macOS 26.6.2, arm64, CPython 3.11.15); a pinned
> container definition ships with the artifact, and replication across
> independently installed host operating systems is measured by the artifact's
> continuous-integration matrix and reported in ⟨CI status reference⟩.

Add the adversarial and property counts, which the manuscript currently omits:

> The adversarial suite comprises **59 cases — 52 negative and 7 positive controls
> — all passing**, together with 24 structural checks over payload mutation,
> post-retirement bundle use, lifecycle signing authority, precedence and the
> runtime acceptance condition, and 3 seeded validation rows exercising WC-01,
> RC-05 and RC-02. A case is counted as passing only if it is rejected with the
> error code its requirement predicts; rejection for an unrelated reason is
> recorded as a mismatch. Property-based testing covers **16 properties over 1,427
> generated examples** (max_examples = 100; two properties terminate earlier
> because their finite input spaces are exhausted).

### A defect the experiment found — worth one sentence

> The determinism experiment is not a formality: on the reference implementation
> it detected a genuine ordering dependence, in which the compiled bundle hashed
> the derivation catalog as authored rather than in canonical order, so that an
> equivalent catalog serialization produced a different bundle hash. The defect
> was fixed before the reportable campaign and is covered by a regression test.

---

## 7. Section VIII — traceability

> All six audit queries return empty result sets on both pinned case artifacts.
> Each query is additionally exercised against a deliberately corrupted fixture —
> nine per case, eighteen in total — and every one detects the violation it exists
> to detect; a query that never fires would demonstrate nothing.

---

## 8. Section XII — limitations

### 8.1 Determinism scope — **do not upgrade yet**

Keep the limitation until the CI matrix has actually run green:

> Determinism scope. TD = 1.000 is measured over 60 compilation runs spanning
> input permutation, locale, time zone and process boundaries on a declared host
> environment. A pinned container definition ships with the artifact and a
> cross-platform continuous-integration matrix (Linux, Windows and macOS runners
> under two Python versions, each compared against committed reference payload
> hashes) is configured; **until those runs are reported, TD = 1.000 supports
> determinism under the declared environment rather than environment independence
> in general.** Even once they pass, the supportable claim is determinism across
> the tested supported environments, not platform independence.

### 8.2 New limitation to add — fixture sensitivity of GD_min

> Divergence measured over a partly synthetic register. GD and GD_min are computed
> over all sixteen Case A rows, and three of those rows — the non-runtime
> dispositions — carry residual ratings supplied as documented synthetic fixtures
> rather than derived from the case narrative. Their ratings are published with
> the artifact, and a sweep over all plausible values shows GD_min would range
> from 2 to 5. The reported value of 3 is exact for the published register, and
> neither Proposition 1's inversion nor Proposition 2's collision depends on those
> three rows.

### 8.3 New limitation to add — sensitivity-model provenance

> Sensitivity-model provenance. The rating distributions used in the Monte Carlo
> analysis are author-specified, frozen a priori, and not panel-adjudicated. The
> analysis therefore establishes that heat-map gate membership is unstable and
> consequence-class membership is not, under a declared perturbation model; it
> does not estimate the true dispersion of enterprise rating judgments.

---

## 9. Section XV — conclusion

The conclusion currently ends by naming the immediate future work: *"execute the
Tier-0 measurements, pin both case artifacts, publish the hash commitment that
binds the deferred comparative study — then hand the compiled-bundle interface to
the shadow-mode deployment that a subsequent paper will require."*

Once the repository is pushed, the first three are done and the sentence should be
updated:

> The Tier-0 measurements are executed and reported, both case artifacts are
> pinned by canonical payload hash, and the preregistration commitment that binds
> the deferred comparative study is published at ⟨repository URL⟩, tag
> `preregister-tier0-v1`. What remains is to execute the committed comparative
> study, and to hand the compiled-bundle interface to the shadow-mode deployment
> that a subsequent paper will require.

**Do not adopt this wording before the push.** Until then the commitment is
prepared and locally committed, not published.

---

## 10. Data and Code Availability

> The GC-IR schema, reference implementations of Ψ_K tooling and Φ, the Control
> Derivation Catalog, both case artifact sets (Steps 1–5 inputs, judgment records,
> dispositions, specifications, compiled bundles, lifecycle-registry fixtures),
> coverage and temporal-validity queries, the adjudication instrument, and the
> preregistration commitment are released as a hash-pinned tagged release at
> ⟨repository URL⟩, tag `v1.0.0`, under the MIT licence. The release manifest
> `MANIFEST.sha256` lists ⟨n⟩ files with their SHA-256 digests and Appendix C
> roles. The preregistration freeze is tag `preregister-tier0-v1`, whose manifest
> `FREEZE_MANIFEST.sha256` covers 117 files across 19 categories. The held-out
> expert-study register is withheld until study close, then released with the
> study data.

**Do not include a DOI** unless a Zenodo deposit has actually been made; see
`docs/ZENODO_RELEASE_STEPS.md`.

---

## 11. Appendix C

Replace `[TO CONFIRM: final repository path at release]` with the resolved path.
Then state:

> The release tag and the manifest hash together constitute the public
> preregistration commitment referenced in Section XI-I. Reproduction is a single
> command (`make reproduce`); the artifact regenerates every reported figure into
> `results/final/` and verifies both case artifacts against committed reference
> canonical payload hashes.

---

## 12. Appendix A

Replace `[PENDING: v1.0 freeze and $id host set at the artifact-repository
release]`:

> The machine-readable JSON Schema (draft 2020-12) implementing these requirements
> ships in the repository, frozen at v1.0 and hash-pinned in the release manifest.
> Schema `$id` values are stable identifiers under the
> `https://gcir.example/schemas/v1.0/` namespace; they are identifiers rather than
> resolvable endpoints, and the authoritative copies are the files in the tagged
> release.

Adjust if a resolvable host will actually be maintained. **Do not name a host that
will not resolve.**

---

## 13. Section XI-I — preregistration

Two corrections.

**Held-out-register hash.** The Tier-0 freeze does not contain one, because no
held-out register has been authored. Recommended:

> The Tier-0 freeze covers the hypotheses and primary outcomes, case artifacts,
> derivation catalog, thresholds and the C\* definition, schemas, compiler commit,
> analysis code and test suite, Monte Carlo distributions and seed, determinism
> matrix, exclusion and missing-data rules, Bayesian priors, and the dependency
> lock and container definition. The held-out-register hash is committed
> separately, in a Tier-1 freeze published before recruitment for the comparative
> study opens, since the instrument is authored as part of that study.

**Public commitment.** Until the repository and tag are pushed, describe the
preregistration as prepared and committed rather than published. The artifact
reports this state itself: `verify_freeze.py` prints
`public_commitment_discharged: false` until the tag appears on a remote.

---

## Summary of mandatory changes

Everything else in this file is optional strengthening. These four are not:

1. **§5 — the Monte Carlo panel attribution.** The manuscript credits distributions
   to a panel that has not been convened.
2. **§2.2 / §8.2 — publish the three non-runtime ratings**, or `GD_min = 3` is not
   reproducible from the paper.
3. **§2.3 — "three-way collision"** is inaccurate for the pinned artifact.
4. **§1, §4, §6 — 31 runs → 60 runs**, and the environment description, which
   currently says the runs were executed inside the pinned container.
