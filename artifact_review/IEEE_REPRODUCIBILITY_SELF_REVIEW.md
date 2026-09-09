# IEEE reproducibility self-review

Written as an IEEE Access reproducibility reviewer receiving this artifact
alongside the article. Scored 1–5; every issue classified BLOCKER / MAJOR /
MINOR / PASS.

The point is not a good score. It is that nothing a reviewer would find is
absent from this document.

---

## Scorecard

| Dimension | Score | Summary |
|---|---|---|
| Documentation | **5 / 5** | Artifact README in IEEE format, per-metric interpretation, explicit claim boundary. |
| Completeness | **5 / 5** | Every input, schema, key, case artifact, experiment and result is committed. No external download. |
| Exercisability | **5 / 5** | One command (`make ieee-check`, ~15 s). Verified from a clean public clone and in Docker. |
| Result reproducibility | **5 / 5** | 48/48 paper-facing results machine-verified, plus 22 cross-checks; both reference hashes reproduced on two architectures. |
| Data / input availability | **4 / 5** | All inputs available — but they are synthetic and a forensic reconstruction, not observational. Disclosed everywhere; inherently limits what the artifact can show. |
| Environment reproducibility | **5 / 5** | Digest-pinned container, `requirements.lock`, 8 environments, 3 OSes, 2 architectures, 6 CPython versions. |
| Claim / evidence alignment | **5 / 5** | 31 claims classified; deferred quantities machine-asserted to carry no value. |
| Versioning | **5 / 5** | Public preregistration freeze, superseded campaign retained unedited, semantic releases. |
| Provenance | **5 / 5** | Every result carries an environment block; campaign ran **at** the freeze commit; the public commitment is verifiable from the remote. |

**Overall: 44 / 45.** No blockers.

---

## BLOCKERS

**None.**

The artifact installs, runs and verifies from a clean public clone; all three CI
workflows are green; the frozen experiment is intact; and no claim exceeds its
evidence.

---

## MAJOR

### M-1 — Both cases were authored by the same party as the method

**Classification: MAJOR, disclosed, not fixable within this artifact.**

`DC = 1.000`, `CV = 1.000`, `OPR = 0.000` are conformance of a *self-authored*
artifact to its own constraints. `DC = 1` in particular holds **by construction**
once dispositions are signed — the artifact says so, and the map records it as
the metric's claim boundary.

What this legitimately shows is that Φ enforces its declared invariants, and the
62-case adversarial corpus — where a case passes only if rejected with the error
code its requirement *predicts* — is what makes that more than self-report.

**Disclosed in:** §I-D, §IX, §X, §XII of the article; `DATA_INVENTORY.md`;
`../paper_update/FINAL_REVIEWER_RISK_REPORT.md` R-02.

**Bounded improvement identified, not executed:** an independently authored
synthetic register, described as OPTIONAL TIER-0.5 in
[`REAL_DATASET_ASSESSMENT.md`](REAL_DATASET_ASSESSMENT.md). It needs a new
prospective freeze and author approval.

### M-2 — Determinism is one implementation, not a specification

**Classification: MAJOR, partially disclosed.**

Eight environments all run the same source tree from the same lockfile. What is
established is that *this implementation* reproduces identical canonical payload
hashes across three OSes, two architectures, six CPython versions, five locales,
five time zones, input permutation and clean-process execution. **Specification-level
determinism — that any conformant implementation produces the same hash — is not
established**, because no second independent implementation of Φ exists.

§XII states the claim as "determinism across the tested supported environments"
and explicitly denies platform independence, but does **not** currently draw the
implementation-versus-specification distinction. That sentence is flagged as a
recommended addition in `FINAL_REVIEWER_RISK_REPORT.md` R-04 and left to the
author, since it is a substantive scope statement.

**Mitigating.** The determinism experiment found a genuine Φ defect — the bundle
hashed the derivation catalog as authored rather than canonically — and the fix
is covered by a regression test. An experiment that catches its own
implementation's bug is not a formality.

### M-3 — The Monte Carlo model is chosen by the party whose result it supports

**Classification: MAJOR, fully disclosed and bounded.**

The ±1 ordinal perturbation (0.6 / 0.2 / 0.2) is author-specified. It was frozen
in the public preregistration before any result was computed, is labelled as
author-specified in the abstract, §XI-C, §XI-G and §XII, and
`monte_carlo_summary.json` carries a `provenance_warning` saying the same. A
secondary renormalising variant is reported (0.352 against 0.321), showing the
headline is not knife-edge on that choice.

`FP^C* = 0.000` is arguably close to structural — C\* membership is not a function
of the perturbed ratings. Proposition 3 carries that claim; the simulation
corroborates rather than proves it, and the artifact says so.

### M-4 — The article's central practical claim is untested

**Classification: MAJOR, honest, and a venue-fit risk rather than an integrity one.**

No evidence is offered that this method beats unaided manual translation, and
none is claimed. RQ5 is preregistered, publicly hash-committed and deferred;
`SNR` and `DF` are recorded as `status=DEFERRED, value=null`, and
`verify_reported_results.py` **asserts on every run** that neither has acquired a
value. No panel has been convened, no practitioner recruited, no participant data
exists, and no script generates or approximates any.

A reviewer expecting an empirical comparison will find the evaluation incomplete
however honestly the gap is stated. Nothing in this artifact can answer that.

---

## MINOR

### m-1 — Three frozen files have been modified since the freeze commit

`Makefile`, `tools/freeze_check.py` and `docs/ARTIFACT_RUNS_COMPLIANCE.md` appear
in `FREEZE_MANIFEST_V2.sha256` and differ from their content at
`c44f25d6`. **All three changed *after* the campaign executed**, during packaging.

This does not weaken the freeze, and the reason is worth stating precisely: the
reportable result files record `results_commits: ["c44f25d6…"]` — the campaign
ran **at the freeze commit itself** — and `freeze_verification.json` records
`frozen_files_changed_since_freeze: {}`. The freeze answers "was the experiment
run on frozen code?", which is a fact about the past and cannot be altered by
later edits. Anyone can verify the frozen content at the tag.

**Verified:** `src/`, `experiments/`, `schemas/`, `cases/`, `catalog/`,
`invariants/`, `queries/`, `keys/` and `preregistration/` are **completely
untouched** since the freeze commit — no compiler logic, experimental input,
schema, C\* profile, Monte Carlo model or preregistration was modified.

### m-2 — Test count differs between the artifact and the article

The repository now runs **304** tests; §XI-H reports **280**. The frozen campaign
measured 280; the additional tests cover `tools/verify_reported_results.py`,
written during packaging after the freeze. They test the reviewer tooling, not the
compiler. Explained in both READMEs at the point a reviewer would notice it.

### m-3 — `MANIFEST.sha256` has no fixpoint

It contains a row for `MANIFEST.json`, which itself embeds every file's hash
including `MANIFEST.json`'s from the previous generation. So regenerating always
produces a difference in that one row. The README previously documented
`make manifest && git diff --exit-code MANIFEST.sha256`, **which could therefore
never pass** — found and fixed during this work. `make verify-manifest` runs the
filtered comparison CI uses and restores the files afterwards, leaving the tree
clean.

### m-4 — Two manifest role labels are imprecise

`artifact_review/*` carries role `repository_root` and
`tools/build_submission_docx.py` carries `fixture_generator`. Both come from the
catch-all rules in `experiments/make_manifest.py`, which is a **frozen file**.
Correcting the labels would mean editing frozen analysis code for a cosmetic gain,
which is the wrong trade. Recorded here instead.

### m-5 — Three references could not be verified from a primary source

[21], [22] and the final DOI of [15]. **No bibliographic data was invented**;
[15] cites its early-access article number instead of a DOI. These require the
author's own confirmation — see `../paper_update/FINAL_REVIEWER_RISK_REPORT.md`
R-01.

### m-6 — No archival DOI

Zenodo deposition needs a browser session and cannot be completed from here. The
exact steps are in [`ARCHIVAL_CHECKLIST.md`](ARCHIVAL_CHECKLIST.md). **No DOI is
asserted anywhere.** The release tag and hash manifest are the citable artifact
until one exists.

### m-7 — `make ieee-check` refreshes `results/development/`

Stages 3 and 7 write there by design, so the working tree is dirty afterwards.
**It writes nothing into `results/final_v2/`**, which is the property that
matters and is stated in both READMEs.

---

## PASS — dimension by dimension

**Documentation (5).** IEEE-format artifact README with identification,
dependencies, installation, quick and full reproduction, expected results,
result↔article mapping and claim boundary. `docs/RESULT_INTERPRETATION.md` states
per metric what each number means and does not.

**Completeness (5).** Schemas, Ψ_K tooling, Φ, catalogs, both cases' Steps 1–5
inputs, signed judgment records, dispositions, ACS, compiled bundles, lifecycle
fixtures, negative controls, all four test suites, every experiment, all results,
and the frozen deferred RQ5 protocol. Research keys are committed so signatures
reproduce byte-identically. **No external download at any point.**

**Exercisability (5).** `make ieee-check`, 8 stages, ~15 s, non-zero on any
failure. Verified end to end from a clean public clone and in Docker
([`CLEAN_CLONE_VERIFICATION.md`](CLEAN_CLONE_VERIFICATION.md)). A `check-python`
guard — added because the clean-clone test hit it — fails legibly on Python < 3.11
instead of surfacing an opaque pip resolution error.

**Result reproducibility (5).** `tools/verify_reported_results.py` verifies
**48/48** paper-facing results against `results/final_v2/`, plus **22 independent
cross-checks** against sources the map does not read: committed reference hashes,
standalone hash files, SHA-256 recomputed from the canonical bytes, per-leg CI
determinism records, and the git tag. 24 tests cover the verifier itself, eight of
which corrupt a value and assert it is caught.

**Environment reproducibility (5).** `requirements.lock`, a digest-pinned base
image, and a determinism experiment that *deliberately varies* the locale, time
zone and hash seed the container pins — so the pinning is a declared starting
point, not a way of avoiding the question.

**Claim/evidence alignment (5).** 31 claims classified C1–C4 in
`../paper_update/FINAL_CLAIM_EVIDENCE_AUDIT.md`. Every map entry carries an
explicit claim boundary. Deferred quantities are machine-asserted to carry no
value. Searched and confirmed absent: detection performance, production
deployment, independent validation, panel adjudication, platform independence, a
fabricated DOI.

**Versioning (5).** `preregister-tier0-v2.2` public and unmoved; `v1.0.0` public
and unrewritten; the superseded v1 campaign retained **unedited**, with
`public_commitment_discharged` never flipped retroactively, and compared value by
value in `results/V1_V2_COMPARISON.md`.

**Provenance (5).** Every result file carries git commit, tag, tree-cleanliness,
Python version, platform and every dependency version. `PROVENANCE.json` records
that the freeze tag was pushed to the remote and dereferences to the freeze
commit — the public commitment is verified *from the remote*, not asserted.

---

## Data / input availability — why 4 and not 5

Everything needed is committed and nothing must be downloaded. The point is
deducted for what the inputs *are*, not for their availability: **Case A is
synthetic, Case B is a forensic reconstruction, and there is no observational
dataset**. That is disclosed in the article, in `DATA_INVENTORY.md` and in the
artifact README, and [`REAL_DATASET_ASSESSMENT.md`](REAL_DATASET_ASSESSMENT.md)
argues — claim class by claim class — that **a real dataset is not required for
the current claims**, because they are properties of Φ and of proofs rather than
of the world.

That argument is sound, but a reviewer is still entitled to note that an artifact
whose inputs are entirely authored by the method's author has a ceiling on what
it can independently establish. Hence 4.

---

## Verdict

**Recommend: Code Reviewed.**

The artifact is complete, exercisable in one command, machine-verifies every
number the article reports, and is scrupulous about the boundary between what it
demonstrates and what it does not. The remaining MAJOR items are properties of the
research programme's stage — a deferred human study, self-authored cases, a single
implementation — not defects in the artifact, and every one is disclosed in the
article itself rather than only here.

**Before submission the author must:** verify references [21] and [22]
(m-5), and complete the Zenodo deposition (m-6). Neither is a correctness defect.
