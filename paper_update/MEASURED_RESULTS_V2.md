# MEASURED_RESULTS_V2.md — publication-ready wording (v2 campaign)

Supersedes `MEASURED_RESULTS.md`, which reported the v1 campaign. Every figure
below is read from `results/final_v2/`.

## Provenance of these numbers

| | |
|---|---|
| **Public freeze tag** | `preregister-tier0-v2.2` |
| **Freeze commit** | `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` |
| **Public repository** | <https://github.com/Sukhmangill977/gc-ir-reference> |
| **Freeze pushed** | 2026-09-08T18:01:36Z — **before** execution; remote tag verified to dereference to the freeze commit |
| **Execution commit** | `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` — the freeze commit itself |
| **Frozen files changed in between** | **0 of 133** |
| Host environment | macOS 26.6.2 arm64, CPython 3.11.15 |
| Evidence | `results/final_v2/PROVENANCE.json`, `freeze_verification.json` |

The v1 campaign ran after a *local* freeze that was never pushed. It is **not**
relabelled and its metadata is **not** edited; `results/V1_V2_COMPARISON.md`
compares the two.

---

## 1. Abstract

> On the two pinned case artifacts the method achieves total disposition
> (DC = 1.000), zero orphan predicates, complete predicate and obligation
> traceability, full consequence-class coverage, and translation determinism of
> **1.000 over 62 compilation runs (31 per case)**; gate divergence against the
> enterprise's predeclared heat-map rule is GD(15) = 3 with GD_min = 3 on Case A,
> and Monte Carlo rating perturbation under a declared ±1 ordinal model moves
> heat-map gate membership with probability up to 0.321 while consequence-class
> membership does not move at all.

Changes from the current text: **31 → 62 runs**, and the qualifier **"under a
declared ±1 ordinal model"**, required by §5.

## 2. Section XI-B — the metrics table

| Metric | Result to print |
|---|---|
| Disposition Completeness (DC) | **1.000 (16/16)** |
| Runtime Compilability Yield (RCY) | **0.8125 (13/16)** — descriptive |
| Non-Runtime Disposition Rate (NDR) | **0.1875 (3/16)** — descriptive |
| Orphan Predicate Rate (OPR) | **0.000 (0/19)** — required 0 |
| Obligation Disposition Completeness (ODC) | **1.000 (12/12)** |
| Predicate Traceability Completeness (PTC) | **1.000 (19/19)** |
| C\* Coverage (CV) | **1.000 (6/6)** — required 1 |
| Translation Determinism (TD) | **1.000 (62/62 runs; 31 per case)** |
| Gate Divergence | Case A **GD(15) = 3, GD_min = 3** · Case B **GD(15) = 4, GD_min = 0** |
| SNR · DF | **[TO REPORT]** — deferred study |

Case B: DC 1.000 (6/6), RCY 1.000, NDR 0.000, OPR 0.000 (0/9), ODC 1.000 (6/6),
PTC 1.000 (9/9), CV 1.000 (4/4).

## 3. Section XI-H — the 31-run breakdown

> Measured: **TD = 1.000 over 62 compilation runs, 31 per case**, following the
> stratified matrix **10 clean repeats + 10 row shuffles + 5 object-key shuffles
> + 3 locales + 3 time zones**. Row shuffles permute the risk register, risk
> analysis, obligation matrix, authority matrix, Approved Control Specifications,
> dispositions, judgment-record selections, catalog entries and invariant
> register; key shuffles reverse, rotate or shuffle the keys of every object in
> every input document; equivalent permitted serialization (integers re-encoded
> as equal-valued floats) is layered onto five runs per case; 15 of the 31 execute
> in a freshly spawned interpreter under a varying hash seed. Each run records the
> canonical payload hash and an environment fingerprint.

Add the counts the manuscript currently omits:

> The adversarial suite comprises **62 cases — 54 negative and 8 positive
> controls — all passing**, with 26 structural checks and 3 seeded validation
> rows. A case counts as passing only if it is rejected with the error code its
> requirement predicts. Property-based testing covers **16 properties over 1,427
> generated examples**. The **thirteen Case B injection scenarios** — the eight
> adversarial attack families and five ASB scenario families enumerated by the
> consuming enforcement artifact — all resolve to SAFE_STATE against a clean
> PERMIT control.

## 4. Section XII — determinism scope. **Substantially widened.**

Replace the limitation:

> Determinism scope. TD = 1.000 is measured over 62 compilation runs (31 per case)
> on each of **eight independently provisioned environments** spanning **three
> operating systems** (macOS 26.6.2, Linux — both Ubuntu 6.17/glibc 2.39 on
> x86_64 and Debian bookworm/glibc 2.36 on aarch64 — and Windows 10.0.26100),
> **two machine architectures** (arm64 and x86_64) and **six CPython patch
> versions**, every one reproducing the committed reference canonical payload
> hashes exactly across five locales, five time zones, input permutation and
> clean-process execution. The claim supported is determinism across the tested
> supported environments; it is not a claim of platform independence, since a
> finite matrix of environments is not the set of all environments.

Evidence: `results/final_v2/CI_STATUS.md`, generated from the GitHub Actions run
artifacts at <https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34261657261>.

## 5. Section XI-G — Monte Carlo. **MANDATORY CORRECTION, UNCHANGED FROM V1.**

The manuscript states "the independent panel freezes discrete probability masses".
**No panel has been convened.** Replace:

> For each risk rᵢ, discrete probability masses over plausible ratings are fixed
> before execution. **In the analysis reported here these masses are
> author-specified rather than panel-adjudicated**: a symmetric ±1 ordinal
> perturbation placing probability 0.6 on the approved rating and 0.2 on each
> adjacent rating of the enterprise 1–5 scale, with out-of-scale mass reassigned
> to the approved rating. The rule was chosen a priori, frozen in the artifact's
> public preregistration before any result was computed, and is not tuned toward
> any value. It is a **declared sensitivity model, not an estimate of how
> uncertain real enterprise ratings are.** When the independent panel of Section
> XI-C is convened for the deferred comparative study, the analysis is to be
> re-run under panel-adjudicated masses and reported separately.

Results:

> Measured on Case A at K = 250,000: the maximum per-risk heat-map flip
> probability is **0.321** (MCSE 0.001, on R-06), and the expected number of
> heat-map gate changes per register is 3.64. `FPᵢ^{C*} = 0.000` across the
> register: re-running the approved consequence-class classifier on 1,000
> perturbed draws produced **no** change in C\* membership. Over the draws, GD(15)
> has mean **5.447** against an approved value of 3 and GD_min has mean **3.226**;
> on Case B GD_min was 0 in all 250,000 draws. Under a secondary variant that
> renormalises the out-of-scale mass, the maximum flip probability is **0.352**.

Add to Section XI-C: *"The panel has not yet been convened; the reference standard,
and any panel-adjudicated input to Section XI-G, are part of the deferred study."*

## 6. Section IX — Case A. Two required edits, unchanged from v1.

**6.1 Publish the three non-runtime ratings**, or `GD_min = 3` is not reproducible
from the paper: R-14 = 12 (L=3, I=4), R-15 = 6 (L=3, I=2), R-16 = 8 (L=2, I=4).
Add: *"Because both divergence sums run over all sixteen rows, those ratings enter
the computation; under a sweep of every (L, I) in {1…5}² for the three rows,
GD_min ranges from 2 to 5."*

**6.2 The "three-way collision at s = 12"** is four-way on the pinned artifact
(R-14 also rates 12). Scope it: *"the collision at s = 12 among the runtime rows —
R-04, R-09 and R-12, with gates 0, 1, 0 — instantiates Proposition 2."*

Hash: `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536`.

## 7. Section X — Case B, and the L-DREA linkage. **NEW.**

Replace `[PENDING: hash-pinned Case B artifact release]`:

> The Case B artifact set is hash-pinned: the canonical bundle payload SHA-256 is
> `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce`.

Add the linkage the memo calls "the one remaining [15]-linkage author action":

> The Case B predicate set is traced to the published enforcement artifact's own
> predicate family. That family comprises **thirteen** named predicates — the ten
> node authorization gates `Gate_A1`…`Gate_A7`, `Lambda_G`, `TOKEN_VALID` and
> `AuthoritySignatureValid`, plus three derived deficit predicates
> `HARM_RISK_THETA`, `STALE_CONTEXT` and `TELEMETRY_STALE` — derived from that
> artifact's source and corroborated by three independently reported predicate
> counts and by its reported single-deficit score of 1/13. Of the nine Case B
> predicates and compiler invariants, **four correspond exactly** to named members
> of that family on the same observables (permit binding, permit single-use and
> replay, and receipt commit-before-actuate, the last both as a risk-derived
> predicate and as compiler invariant `INV-EVIDENCE-COMMIT`), **three correspond
> by family**, and **two are declared gaps**: no L-DREA predicate evaluates a
> rolling velocity bound, and although the artifact records version identifiers as
> trace columns, no member of its predicate vector evaluates them — so the
> per-action version binding of `INV-VERSION` has no counterpart there. The
> mapping is machine-verified and released as
> `cases/case_b/ldrea_traceability.json` under manifest role `case_b_input`.

> This establishes continuity of predicate family only. It does not establish
> detection performance, and the compiled Case B bundle was not executed against
> the 284,807-event corpus.

External artifact pin: `github.com/AGLakhowal/Gamma-Permit-Package`, commit
`40fa8f046ad3c6632c66df46abe5500e5dd05696`, subtree `realdatatestcode/`.

## 8. Section XI-I and Appendix C — the public commitment. **NOW DISCHARGEABLE.**

> The frozen elements are publicly hash-committed at
> <https://github.com/Sukhmangill977/gc-ir-reference>, tag
> `preregister-tier0-v2.2`, whose manifest `FREEZE_MANIFEST_V2.sha256` covers 133
> files across 23 categories. The tag was pushed before the reportable campaign
> was executed; the campaign ran at the freeze commit itself, and no frozen file
> changed in between — verifiable with
> `python -m experiments.verify_freeze --tag preregister-tier0-v2.2`.

Section XI-I still needs the held-out-register correction:

> The held-out-register hash is committed separately, in a Tier-1 freeze published
> before recruitment for the comparative study opens, since the instrument is
> authored as part of that study.

Appendix C: replace `[TO CONFIRM: final repository path at release]` with
<https://github.com/Sukhmangill977/gc-ir-reference>. **Do not cite a DOI** — none
exists; see `docs/ZENODO_RELEASE_STEPS.md`.

## 9. Section XV — conclusion

> The Tier-0 measurements are executed and reported, both case artifacts are
> pinned by canonical payload hash, and the preregistration commitment that binds
> the deferred comparative study is published at
> <https://github.com/Sukhmangill977/gc-ir-reference>, tag
> `preregister-tier0-v2.2`. What remains is to execute the committed comparative
> study, and to hand the compiled-bundle interface to the shadow-mode deployment
> that a subsequent paper will require.

## 10. Appendix A — schema version. **Unchanged at v1.0.**

Replace the pending marker:

> The machine-readable JSON Schema (draft 2020-12) implementing these requirements
> ships in the repository, frozen at v1.0 and hash-pinned in the release manifest.
> Schema `$id` values are stable identifiers under the
> `https://gcir.example/schemas/v1.0/` namespace; they are identifiers rather than
> resolvable endpoints.

The artifact-runs memo refers to "the v1.1 JSON Schema". **No revision was made.**
The manuscript is normative at v1.0 in three places and nothing in the audit
produced a scientific reason to revise it. See `docs/ARTIFACT_RUNS_COMPLIANCE.md`
§C2.

---

## Mandatory changes

1. **§5** — the Monte Carlo panel attribution. Credits a panel that has not met.
2. **§6.1** — publish the three non-runtime ratings, or `GD_min` is not reproducible.
3. **§6.2** — "three-way collision" is four-way on the pinned artifact.
4. **§1, §2, §3** — 31 runs → **62** (31 per case), with the stratified breakdown.
5. **§4** — the determinism limitation must be *widened*, not deleted: three
   operating systems and two architectures are now measured, but that is still not
   platform independence.
