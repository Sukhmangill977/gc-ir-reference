# GC-IR Reference Implementation

**Reproducibility artifact for “From Risk Register to Runtime Predicate: A
Deterministic Method for Compiling AI Governance Assessments into Enforceable
Controls”**

Abhinandan Gill-Lakhowal, Member, IEEE — Gillian Holdings Incorporated, Calgary, AB, Canada

[![tests](https://github.com/AGLakhowal/gc-ir-reference/actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)
[![cross-platform determinism](https://github.com/AGLakhowal/gc-ir-reference/actions/workflows/determinism.yml/badge.svg)](../../actions/workflows/determinism.yml)
[![reproducibility](https://github.com/AGLakhowal/gc-ir-reference/actions/workflows/reproducibility.yml/badge.svg)](../../actions/workflows/reproducibility.yml)

---

## 5-minute verification

The shortest path from a fresh clone to the artifact's central claims.

```bash
git clone https://github.com/AGLakhowal/gc-ir-reference.git
cd gc-ir-reference

make install        # .venv + the pinned dependency set (~30 s)
make test           # 275 tests across four suites          (~10 s)
make verify-hashes  # recompile both cases, check the committed hashes (~2 s)
```

`make verify-hashes` recompiles Case A and Case B from the committed governance
artifacts and compares the SHA-256 of the RFC 8785 canonical bundle payload
against the reference values committed in `cases/*/expected/reference_hashes.json`.
If those match on your machine, the compiler is deterministic across your
environment and the one that produced the reference.

Want the whole thing?

```bash
make reproduce      # all 11 experiment steps end to end   (~45 s)
cat results/development/SUMMARY.md
```

Everything in that summary is read from a result file a script produced. No number
in it is typed by hand.

---

## What this is

Enterprise AI governance frameworks end with an approved risk assessment — a
document. Deterministic runtime-enforcement architectures begin with an approved
predicate set — code. This artifact implements the method the paper proposes for
the step between them, and measures the properties the paper claims for it.

The research artifact is the method made executable:

| Component | What it is | Where |
|---|---|---|
| Governance input model | `𝒢 = (M, S, O, R, A)` — the five-step assessment, machine-readable | `schemas/assessment.schema.json`, `src/gcir/models.py` |
| `Ψ_K` support tooling | Validates and assembles signed human selections. **Infers nothing from prose.** | `src/gcir/refinement.py`, `src/gcir/catalog.py` |
| GC-IR | The record family: compiled predicates, non-runtime / accepted / unresolved dispositions | `schemas/gcir.schema.json`, `src/gcir/models.py` |
| Compiler `Φ` | Deterministic compilation to a canonical, hashed, signed, immutable bundle | `src/gcir/compiler.py` |
| RFC 8785 | JSON Canonicalization Scheme, with ECMAScript number formatting and UTF-16 key ordering | `src/gcir/canonicalization.py` |
| Authority closure | Every action tuple resolves to `S.authority_matrix` | `src/gcir/authority.py` |
| `C*` coverage | The consequence-class gate coverage rule CV | `src/gcir/coverage.py` |
| Lifecycle registry | Retirement, supersession, revocation — signed, outside the payload | `src/gcir/lifecycle.py` |
| Temporal traceability | The origin chain and all six audit queries | `src/gcir/traceability.py`, `queries/traceability.sql` |
| Metrics | DC, RCY, NDR, OPR, ODC, PTC, CV, TD, GD, GD_min | `src/gcir/metrics.py` |
| Case A | Investment research agent — **synthetic**, 16 register rows | `cases/case_a/` |
| Case B | Transaction authorization agent — **forensic reconstruction**, 6 rows | `cases/case_b/` |

## What this is not

Not a production system, not an AI agent, not a runtime enforcement engine, and
not a user interface. The enforcement layer belongs to the cited prior work and is
not restated here. This artifact stops at the compiled bundle.

---

## Claim boundary

The paper's own boundary governs. Applied to this artifact:

**Claimed and measured here.** Total disposition; deterministic compilation after
approval; authority closure; `C*` coverage with the Proposition 1 and 2 premises
instantiated on the pinned register; measured divergence from the declared
heat-map comparator; origin-closed, temporally valid traceability; fail-closed
unknown handling on mandatory gates; orphan-control impossibility **within
`Φ`-produced bundles**.

**Not claimed, and not measurable from anything in this repository.**

* **Comparative superiority over unaided manual practice.** RQ5 is preregistered
  and **deferred**. No adjudication panel has been convened, no practitioner has
  been recruited, and no participant data exists. `SNR` and `DF` are reported as
  `DEFERRED`, never as numbers.
* **Universal platform independence.** The local determinism experiment runs on one
  host OS; the CI matrix covers three runner images. The supportable wording is
  “deterministic across the tested supported environments”.
* **Detection capability, production impact, false-denial rates.** Out of scope.
* **Semantic correctness.** Compilation warrants that predicates faithfully encode
  the approved specifications — not that the specifications are complete over the
  harm space, nor that a permitted action is the right action.
* **Legal compliance.** Empty traceability queries demonstrate linkage under the
  declared data model. Nothing more.

`docs/RESULT_INTERPRETATION.md` states, metric by metric, what each number means
and what it does not.

---

## Architecture

```
   M, S, O, R, A                    approved governance assessment (Section III)
        │
        │   K  ── approved, versioned Control Derivation Catalog
        ▼
   ┌──────────────────────────────────────────────────────────┐
   │  Ψ_K   governed semantic refinement -- A RELATION        │
   │        closed into a mapping only by the signed          │
   │        judgment record J.  Human judgment happens HERE,  │
   │        once, and is signed.                              │
   └──────────────────────────────────────────────────────────┘
        │        (D, Δ)  ∈ Ψ_K(𝒢);  Ψ_K(𝒢, J) → (D, Δ)
        ▼
   ┌──────────────────────────────────────────────────────────┐
   │  Φ     deterministic compiler                            │
   │        exact catalog lookup · authority closure ·        │
   │        C* coverage · mandatory unknown-failure ·         │
   │        RFC 8785 · SHA-256 · no clock, no RNG, no LLM     │
   └──────────────────────────────────────────────────────────┘
        │
        ▼
   (P, G, E, B)   predicates · gate map · escalation map · signed immutable bundle
        │
        ├── lifecycle registry REG   (separately signed; NEVER in the payload)
        └── receipts                 ValidAt(t, b, REG) at decision time
```

The refinement boundary is the point of the design: **human semantic judgment is
exercised once, under an approved catalog, and recorded in a signed judgment
record. Everything to the right of it is a function of signed inputs.** Determinism
is claimed for `Φ`, never for the interpretation of unconstrained prose.

`tests/adversarial/test_no_inference.py` asserts this statically over the shipped
source: the compiler path imports no RNG, no similarity library, no model library,
and reads no clock.

---

## Project structure

```
gc-ir-reference/
├── src/gcir/              the implementation (16 modules, no framework)
├── schemas/               13 JSON Schema (draft 2020-12) documents
├── cases/case_a/          synthetic investment-research case
│   ├── inputs/            M, S, O, R, A + catalog + C* profile + INV + thresholds
│   ├── judgment/          the signed judgment record J
│   ├── dispositions/      Δ
│   ├── acs/               D -- the Approved Control Specifications
│   ├── lifecycle/         registry, receipts, actuations + negative/ fixtures
│   └── expected/          committed reference canonical payload hash
├── cases/case_b/          forensic-reconstruction transaction-authorization case
├── catalog/               the approved catalogs, published at the paths Appendix C names
├── invariants/            the approved invariant registers
├── queries/               traceability.sql -- the six audit queries
├── tests/                 unit · properties · adversarial · integration
├── experiments/           every measurement, plus reproduce_all
├── results/development/   exploratory results -- NOT reportable
├── results/final/         the frozen reportable campaign
├── preregistration/       TIER0_FREEZE.md, RQ5_DEFERRED_PROTOCOL.md, FREEZE_MANIFEST.sha256
├── paper_update/          measured results and the placeholder replacement table
├── docs/                  requirements extraction, claim matrix, provenance, interpretation
├── tools/                 the case-fixture generators
└── keys/                  research signing keys -- TEST ONLY / NOT FOR PRODUCTION
```

---

## Prerequisites

Python 3.11 or 3.12. No other runtime dependency. Four packages
(`jsonschema`, `referencing`, `cryptography`, `numpy`) plus `pytest` and
`hypothesis` for the test suites, all pinned in `requirements.lock`.

## Local setup

```bash
make install                    # or:
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.lock
```

## Docker

```bash
make docker-build               # base image pinned by digest
make docker-reproduce           # docker run --rm gcir make reproduce
```

The container fixes `LANG`, `LC_ALL`, `TZ` and `PYTHONHASHSEED` so the baseline
environment is *declared* rather than inherited — and the determinism experiment
then deliberately varies all four, so the pinning is a stated starting point, not a
way of avoiding the question.

---

## Running things

```bash
make test                                    # all four suites
.venv/bin/python -m pytest tests/properties -q --hypothesis-show-statistics

make reproduce                               # 11 steps -> results/development/
make reproduce-final                         # the frozen campaign -> results/final/

# individual experiments
.venv/bin/python -m experiments.run_case --case case_a
.venv/bin/python -m experiments.run_determinism --runs-per-case 30
.venv/bin/python -m experiments.run_gate_divergence
.venv/bin/python -m experiments.run_monte_carlo --draws 250000
.venv/bin/python -m experiments.run_traceability
.venv/bin/python -m experiments.run_adversarial
.venv/bin/python -m experiments.run_metrics
```

## Verifying hashes

```bash
make verify-hashes                           # against the committed references
make manifest && git diff --exit-code MANIFEST.sha256   # manifest is current
shasum -a 256 -c <(awk '!/^#/ && NF {print $1 "  " $3}' MANIFEST.sha256)
```

Every hash in `MANIFEST.sha256` is computed from the file on disk by
`experiments/make_manifest.py`. Each line carries the Appendix C role alongside the
path.

## Inspecting Case A and Case B

```bash
# the register, its dispositions and its gates
python -c "import json;d=json.load(open('cases/case_a/inputs/assessment.json'));
[print(r['risk_id'], '|', r['event'][:70]) for r in d['risk_register']]"

jq '.records[] | {risk_id, status, reason_code}' cases/case_a/dispositions/dispositions.json
jq '.predicates[] | {gcir_id, gate_type, gate_source, mandatory_role}' results/development/case_a/gcir_records.json
jq '.c_star_coverage' results/development/case_a/coverage_matrix.json
```

The canonical bytes that were hashed are written verbatim to
`results/*/case_*/canonical_payload.json`, so you can hash them yourself:

```bash
shasum -a 256 results/development/case_a/canonical_payload.json
cat results/development/case_a/payload_hash.txt
```

## Result provenance

Every result file carries an `environment` block: git commit, git tag, whether the
working tree was clean, Python version, platform, and every dependency version.
`phase` says `development` or `final`. A number can always be traced back to the
state that produced it.

---

## Reproducibility and the two-phase workflow

`results/development/` holds exploratory numbers from while the implementation was
being built. **They are not reportable**, and they are committed rather than
deleted so the development history the freeze separates from is visible.

`results/final/` holds the reportable campaign, executed **after** the public
timestamped preregistration commit (`preregistration/TIER0_FREEZE.md`, tag
`preregister-tier0-v1`). Per Section XI-I: *"The internal selection of frozen
elements is not a freeze — the public timestamped commitment is."*

Full detail: `docs/REPRODUCIBILITY.md` and `docs/EXPERIMENT_PROTOCOL.md`.

---

## RQ5 remains deferred

The comparative expert study is **preregistered and not executed**. Its protocol is
frozen in `preregistration/RQ5_DEFERRED_PROTOCOL.md` and hash-committed, so it is
bound to be run as written rather than merely promised.

No adjudication panel has been convened. No practitioner has been recruited. No
participant data exists. `SNR` and `DF` are reported as `DEFERRED`. **No script in
this repository generates, simulates or approximates human study data.**

The held-out expert-study register is withheld until study close, and
`preregistration/HELD_OUT_REGISTER.md` records that its hash commitment is openly
outstanding rather than committing a hash of a placeholder.

---

## Limitations

Beyond the claim boundary above, and beyond the manuscript's Section XII:

* **Case A is synthetic.** Fully specified and reproducible, but not a deployed
  system. Fields the manuscript does not state are documented fixtures —
  `docs/FIXTURE_PROVENANCE.md` lists every one with the basis on which it was chosen.
* **Case B is a forensic reconstruction.** The mapping is retrospective. The
  284,807-event conformance run of the prior work is **not** reproduced here and is
  not evidence for anything in this artifact.
* **`GD_min` is partly a function of undisclosed ratings.** Both GD sums run over
  all sixteen Case A rows, and the manuscript states `L × I` only for the thirteen
  runtime rows. The three non-runtime ratings are fixtures; a full sweep over every
  plausible value shows `GD_min` would range over **2 to 5**, and the artifact
  reports that sweep alongside the measured value (FP-014).
* **The Monte Carlo distributions are author-specified**, not panel-adjudicated,
  contrary to what the manuscript currently says. The deviation is declared in the
  freeze, in the result file, and in `paper_update/MEASURED_RESULTS.md` (FP-020).
* **The adversarial corpus is a finite list** of known failure modes, not a proof
  of robustness.
* **Property-based tests sample**; they do not verify. The two properties whose
  finite input spaces Hypothesis exhausts are the exception.
* **Research keys are committed** so signatures are reproducible from a fresh
  clone. They are marked TEST ONLY / NOT FOR PRODUCTION and protect nothing.

---

## Citing

See `CITATION.cff`. The artifact is released under MIT (`LICENSE`), matching the
precedent named in the manuscript's Appendix C.

## Security

`SECURITY.md`. In short: this is a research artifact, the committed keys are test
fixtures, and nothing here should be deployed.
