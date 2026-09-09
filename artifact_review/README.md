# Artifact README — IEEE Access Reproducibility Review

Reviewer-oriented guide to the GC-IR reference implementation. For the project
README see [`../README.md`](../README.md).

---

## 1. Artifact identification

| | |
|---|---|
| **Article** | *From Risk Register to Runtime Predicate: A Deterministic Method for Compiling AI Governance Assessments into Enforceable Controls* |
| **Author** | Abhinandan Gill-Lakhowal, Member, IEEE — Gillian Holdings Incorporated, Calgary, AB, Canada |
| **Artifact** | `gc-ir-reference` — the method made executable, plus every measurement the article reports |
| **Role** | **Supports all empirical claims in the article.** Every number in Sections IX–XII is produced by this artifact and is re-derivable from it. |
| **Repository** | https://github.com/Sukhmangill977/gc-ir-reference |
| **License** | MIT (`../LICENSE`) — code, schemas and case artifacts |
| **Authoritative results** | `results/final_v2/` |
| **Public preregistration freeze** | tag `preregister-tier0-v2.2`, commit `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` |
| **Archival DOI** | **None yet.** See [`ARCHIVAL_CHECKLIST.md`](ARCHIVAL_CHECKLIST.md). The release tag and its hash manifest are the citable artifact until one exists. |

**What the artifact is.** A deterministic compiler `Φ` from an approved governance
assessment to a canonically serialized, signed, immutable predicate bundle, with
the governed refinement relation `Ψ_K` in front of it; two worked cases; and the
experiments that measure disposition completeness, translation determinism, gate
divergence, C\* coverage, traceability and rating sensitivity.

**What it is not.** Not a production system, not an AI agent, not a runtime
enforcement engine, not a user interface. The enforcement layer belongs to cited
prior work and is not restated here.

---

## 2. Dependencies and requirements

**Hardware.** Any x86_64 or arm64 machine. No GPU. ~1 GB disk, ~1 GB RAM. All
timings below are from macOS 26.6.2 on arm64.

**Operating system.** Verified on macOS 26.6.2, Ubuntu (Linux 6.17, glibc 2.39),
Windows 10.0.26100, and Debian bookworm (glibc 2.36) in the pinned container.

**Python.** CPython 3.11 or 3.12. Verified on 3.11.9, 3.11.11, 3.11.15, 3.11.16,
3.12.10, 3.12.14.

**Libraries.** Four runtime packages plus two for testing, all pinned in
[`../requirements.lock`](../requirements.lock):

| Package | Purpose |
|---|---|
| `jsonschema` | draft 2020-12 schema validation |
| `referencing` | schema registry for cross-schema `$ref` |
| `cryptography` | Ed25519 signing and verification |
| `numpy` | the Monte Carlo experiment |
| `pytest` | test suites |
| `hypothesis` | property-based testing |

No network access is required after installation. Nothing is downloaded at run
time.

**Docker.** Optional. The base image is pinned by digest in
[`../Dockerfile`](../Dockerfile).

---

## 3. Data and inputs

Full classification in [`DATA_INVENTORY.md`](DATA_INVENTORY.md); the question of
whether real data is needed is answered in
[`REAL_DATASET_ASSESSMENT.md`](REAL_DATASET_ASSESSMENT.md).

| Input | Class | Location |
|---|---|---|
| **Case A** — investment-research RAG summarizer, 16 register rows | **SYNTHETIC.** Authored for this work; fully specified, not a deployed system. | `cases/case_a/` |
| **Case B** — transaction-authorization agent, 6 register rows | **FORENSIC RECONSTRUCTION.** Reconstructed retrospectively from a published enforcement artifact; not a contemporaneous governance record. | `cases/case_b/` |
| Monte Carlo rating distributions | **AUTHOR-SPECIFIED, prospectively frozen** ±1 ordinal sensitivity model. Not panel-adjudicated; not an empirical estimate of rating uncertainty. | `preregistration/monte_carlo_distributions_v1.json` |
| Research signing keys | **TEST ONLY / NOT FOR PRODUCTION.** Committed so signatures reproduce byte-identically. | `keys/` |
| 284,807-event transaction corpus | **NOT IN THIS REPOSITORY.** Belongs to prior work. The compiled Case B bundle was never executed against it. | — |
| Expert-study participant data | **DOES NOT EXIST.** RQ5 is preregistered and deferred. | — |

Everything needed to reproduce every reported number is committed. There is no
external download step.

---

## 4. Installation and deployment

```bash
git clone https://github.com/Sukhmangill977/gc-ir-reference.git
cd gc-ir-reference
make install                     # or: make install PYTHON=python3.11
```

**If your system `python3` is older than 3.11**, `make install` stops immediately
with a message naming the interpreter it found and how to override it. Pass
`PYTHON=python3.11` (or any 3.11/3.12 interpreter) to select one explicitly.

`make install` creates `.venv` and installs the pinned dependency set.
**Estimated time: ~30 s** on a warm pip cache, ~60 s cold.

Docker alternative:

```bash
make docker-build        # ~90 s
```

---

## 5. Quick verification (~20 s after install)

**One command:**

```bash
make ieee-check
```

Eight stages, stopping non-zero at the first failure:

| Stage | What it checks |
|---|---|
| 1 | Environment and dependency versions |
| 2 | All test suites (301 tests) |
| 3 | Case A and Case B recompile |
| 4 | Compiled payload hashes match the committed references |
| 5 | Freeze verification — public tag, ancestry, frozen-file integrity |
| 6 | **Every paper-facing number against `results/final_v2/`** |
| 7 | Traceability audit queries and negative controls |
| 8 | `MANIFEST.sha256` currency |

**It writes nothing into `results/final_v2/`.** Measured runtime: **~15 s** on a
warm `.venv`.

Or run the pieces individually:

```bash
make test                                  # 301 tests            ~10 s
make verify-hashes                         # reference hashes      ~2 s
python tools/freeze_check.py --final-v2    # the 13 frozen numbers ~3 s
python tools/verify_reported_results.py    # every reported number ~2 s
```

> **301 tests here, 280 in the article.** The frozen `preregister-tier0-v2.2`
> campaign measured **280**, which is what §XI-H reports. The 21 additional tests
> cover `tools/verify_reported_results.py`, written during artifact packaging
> *after* the freeze. They test the reviewer tooling, not the compiler, and no
> reported result depends on them.

---

## 6. Full reproduction

```bash
python run_all.py --final-v2
cat results/final_v2/SUMMARY.md
```

**Estimated time: ~60 s** (the Monte Carlo step at K = 250,000 dominates).

**This overwrites `results/final_v2/`.** To verify the published numbers without
touching them, use `make ieee-check`.

Inside the container:

```bash
make docker-reproduce
```

Cross-platform determinism is measured by the GitHub Actions matrix rather than by
this script; `results/final_v2/CI_STATUS.md` records it, generated from real run
artifacts by `experiments/check_ci_agreement.py`.

---

## 7. Expected results

All values below are read from `results/final_v2/` by
`tools/verify_reported_results.py`. Full mapping, with the exact JSON field for
each, in [`PAPER_TO_ARTIFACT_RESULTS.md`](PAPER_TO_ARTIFACT_RESULTS.md).

### Canonical payload hashes

| Case | SHA-256 of the RFC 8785 canonical bundle payload |
|---|---|
| A | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| B | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |

If these two hashes reproduce on your machine, the compiler is deterministic
across your environment and the one that produced the references.

### Primary metrics

| Metric | Case A | Case B |
|---|---|---|
| DC — Disposition Completeness | 1.000 (16/16) | 1.000 (6/6) |
| RCY — Runtime Conversion Yield | 0.8125 (13/16) | 1.000 (6/6) |
| NDR — Non-Derivation Rate | 0.1875 (3/16) | 0.000 (0/6) |
| OPR — Orphan Predicate Rate | 0.000 (0/19) | 0.000 (0/9) |
| ODC — Obligation Disposition Completeness | 1.000 (12/12) | 1.000 (6/6) |
| PTC — Predicate Traceability Completeness | 1.000 (19/19) | 1.000 (9/9) |
| CV — C\* Coverage | 1.000 (6/6) | 1.000 (4/4) |
| GD(15) | 3 | 4 |
| GD_min | 3 | 0 |

### Determinism, adversarial and traceability

| Quantity | Expected |
|---|---|
| TD | **1.000 (62/62)** — 31 runs per case |
| Determinism strata | 10 repeats + 10 row shuffles + 5 key shuffles + 3 locales + 3 time zones |
| Cross-environment | 8 environments, 3 OSes, 2 architectures, 6 CPython versions — all TD = 1.000, identical hashes |
| Adversarial corpus | 62/62 (54 negative, 8 positive controls), 0 code mismatches |
| Structural checks | 26/26 |
| Case B injection scenarios | 13/13 → SAFE_STATE |
| Tests | 280 in the frozen campaign |
| Properties | 16 properties, 1,427 generated examples |
| Traceability | 6/6 clean queries empty per case; 18/18 negative controls fire |

### Monte Carlo (K = 250,000, seed 20260201)

| Quantity | Expected |
|---|---|
| max FP^heat, Case A | **0.321268** (MCSE 0.000934, row R-06) |
| max FP^C\*, Case A | **0.000000** |
| C\* membership changes | 0 in 1,000 verified probe draws |
| Renormalisation variant | 0.352092 |
| GD mean / GD_min mean | 5.4466 / 3.226356 |

### Reported as DEFERRED — no value exists

`SNR` and `DF` are the primary outcomes of the preregistered, **deferred**
comparative expert study. `metrics.json` records them as
`"status": "DEFERRED", "value": null`. **No adjudication panel has been convened,
no practitioner recruited, and no participant data exists.** No script in this
repository generates, simulates or approximates human study data —
`tools/verify_reported_results.py` asserts this on every run.

---

## 8. Result ↔ article mapping

[**`PAPER_TO_ARTIFACT_RESULTS.md`**](PAPER_TO_ARTIFACT_RESULTS.md) and
[`PAPER_RESULT_MAP.json`](PAPER_RESULT_MAP.json) map **48 paper-facing results**.
Each entry records the manuscript section, the claim, the reported value, the
source experiment, the reproducing command, the input files, the generated result
file, **the exact JSON field**, the expected value, the interpretation and the
claim boundary.

Both are generated by `python -m tools.build_paper_result_map`, which reads every
value out of `results/final_v2/`. **No number in them is typed from the
manuscript.** `tools/verify_reported_results.py` consumes the JSON and exits
non-zero on any disagreement, and adds 22 cross-checks against sources the map
does not read — committed reference hashes, the standalone hash files, SHA-256
recomputed from the canonical bytes, per-leg CI determinism records, and the git
tag itself.

---

## 9. Claim boundary

### What this artifact demonstrates

* Total disposition of an approved register, and deterministic compilation after approval
* Authority closure against an approved action matrix
* C\* coverage with the Proposition 1 and 2 premises instantiated on the pinned register
* Measured divergence from the enterprise's declared heat-map comparator
* Origin-closed, temporally valid traceability, with negative controls proving the queries can detect
* Fail-closed unknown handling on mandatory gates
* Orphan-control impossibility **within Φ-produced bundles**
* Reproduction of identical canonical payload hashes across the tested supported environments

### What it does NOT demonstrate

| Not claimed | Why |
|---|---|
| **Comparative superiority over unaided manual practice** | RQ5 is preregistered and **deferred**. No panel, no participants, no data. |
| **Platform independence** | TD = 1.000 on **8 environments**. A finite matrix is not the set of all environments. No other OS and no other Python implementation was exercised. |
| **Specification-level determinism** | One implementation was measured. A second independent implementation of Φ would be required, and none exists. |
| **Detection capability, production impact, false-denial rates** | Explicitly out of scope (§I-D). The 13 Case B injection scenarios establish that the compiled bundle refuses to permit under each published hazard class — **not** detection performance. |
| **Execution against the 284,807-event corpus** | That run belongs to prior work and is **not** reproduced here. |
| **Semantic correctness** | Compilation warrants that predicates faithfully encode the approved specifications — not that the specifications are complete over the harm space. |
| **Legal compliance** | Empty traceability queries demonstrate linkage under the declared data model. Nothing more. |
| **Independent validation** | Both cases were authored by the same party as the method. This is the strongest objection to the artifact and is recorded as such in `../paper_update/FINAL_REVIEWER_RISK_REPORT.md` R-02. |

`docs/RESULT_INTERPRETATION.md` states, metric by metric, what each number means
and what it does not.

---

## 10. Other notes

**Two manifests, two purposes.** `MANIFEST.sha256` inventories the *current
repository* (304 files, 30 roles) and is regenerated whenever a file changes.
`preregistration/FREEZE_MANIFEST_V2.sha256` *proves the frozen experiment* (133
files at the freeze commit) and is **never** regenerated. Do not conflate them.

**Two campaigns.** `results/final_v2/` is reportable. `results/final/` is the
**superseded** v1 campaign, retained unedited for provenance: its freeze tag was
local-only when it ran, and a later push cannot make a completed experiment
prospectively preregistered. `results/V1_V2_COMPARISON.md` compares them value by
value — every substantive measured value is identical.

**Committed keys.** `keys/` contains Ed25519 research fixtures marked TEST ONLY /
NOT FOR PRODUCTION, committed so a reviewer regenerating the case artifacts
obtains byte-identical signatures. They protect nothing.

**Frozen documents point at the old path.** Several files under `docs/` are part
of the preregistration record and still reference `results/final/` (the v1 output
path). They are deliberately not updated — editing a preregistered document after
seeing results would destroy the evidence the freeze provides.
[`../docs/FROZEN_DOCS_READING_NOTE.md`](../docs/FROZEN_DOCS_READING_NOTE.md) maps
them to the current state. For the authoritative mapping use
[`PAPER_TO_ARTIFACT_RESULTS.md`](PAPER_TO_ARTIFACT_RESULTS.md).

**Determinism found a real bug.** The experiment detected an ordering dependence
in Φ — the compiled bundle hashed the derivation catalog as authored rather than
in canonical order. It was fixed before the reportable campaign and is covered by
a regression test (§XI-H). The experiment is not a formality.

## Artifact-review documents

| File | Contents |
|---|---|
| [`PAPER_TO_ARTIFACT_RESULTS.md`](PAPER_TO_ARTIFACT_RESULTS.md) | 48 results mapped to their evidence |
| [`PAPER_RESULT_MAP.json`](PAPER_RESULT_MAP.json) | The same map, machine-readable |
| [`DATA_INVENTORY.md`](DATA_INVENTORY.md) | Every input classified |
| [`REAL_DATASET_ASSESSMENT.md`](REAL_DATASET_ASSESSMENT.md) | Whether a real dataset is required (it is not) |
| [`CLEAN_CLONE_VERIFICATION.md`](CLEAN_CLONE_VERIFICATION.md) | Evidence from a fresh clone |
| [`CI_EVIDENCE.md`](CI_EVIDENCE.md) | Green workflow run IDs |
| [`ARCHIVAL_CHECKLIST.md`](ARCHIVAL_CHECKLIST.md) | Zenodo deposition readiness |
| [`IEEE_REPRODUCIBILITY_SELF_REVIEW.md`](IEEE_REPRODUCIBILITY_SELF_REVIEW.md) | Self-assessment against the review criteria |
