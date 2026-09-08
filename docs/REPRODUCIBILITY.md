# REPRODUCIBILITY.md

How to reproduce every number this artifact reports, and how to tell whether you did.

---

## The short version

```bash
git clone https://github.com/AGLakhowal/gc-ir-reference.git
cd gc-ir-reference
make install
make test
make verify-hashes
make reproduce
cat results/development/SUMMARY.md
```

Total wall time on a 2023-class laptop: about 90 seconds, most of it the Monte
Carlo step.

---

## What "reproduced" means here

Three different things, with three different bars.

**1. Byte-identical.** The compiled canonical payload hash of each case. This must
match exactly, on any platform, or the artifact's central determinism claim fails.
`make verify-hashes` checks it against the values committed in
`cases/*/expected/reference_hashes.json`.

**2. Exactly equal.** Every count and ratio: DC, RCY, NDR, OPR, ODC, PTC, CV, the
disposition counts, GD, GD_min, the adversarial pass counts, the traceability row
counts. These are deterministic functions of committed files and must match.

**3. Equal to within Monte Carlo error.** The flip probabilities. The seed is
frozen, so on the same NumPy version they reproduce exactly; across NumPy versions
the generator stream can differ, in which case agreement is to within the reported
MCSE (bounded above by 0.001 at K = 250,000). The result file records the NumPy
version that produced it.

**Not reproducible, and not required to be:** signature envelope bytes. The
envelope carries signing time and key identity and is excluded from the payload by
design (Section VI-C).

---

## Prerequisites

* Python 3.11 or 3.12
* `git` (the experiments record the commit and tag in every result file)
* Optionally Docker, for the pinned container

No network access is needed after `make install`.

---

## Environment

```bash
make install
```

creates `.venv` and installs exactly `requirements.lock`. To reproduce inside the
pinned container instead:

```bash
make docker-build
make docker-reproduce
```

The `Dockerfile` pins the base image by digest and generates the four non-C locales
the determinism experiment exercises.

---

## The eleven steps of `make reproduce`

| # | Step | Checks |
|---|---|---|
| 1 | Regenerate the case artifacts | the committed tree is byte-identical after regeneration |
| 2 | Compile Case A and Case B | bundle and GC-IR schema validation, payload purity, hash stability under signing |
| 3 | Test suites | unit, property-based, adversarial, integration |
| 4 | Adversarial corpus | 59 cases, 20 structural checks, 3 seeded validation rows |
| 5 | Traceability | six audit queries empty; 18 negative controls all fire |
| 6 | Metrics | DC, RCY, NDR, OPR, ODC, PTC, CV |
| 7 | Gate divergence | GD, GD_min, Proposition 1/2 premises, the FP-014 sensitivity sweep |
| 8 | Determinism | ≥ 60 runs; TD |
| 9 | Monte Carlo | K = 250,000 per risk; FP^heat, FP^C\*, GD distributions, MCSE |
| 10 | Hash manifest | MANIFEST.sha256 regenerated from the files on disk |
| 11 | Summary | SUMMARY.md generated entirely from result files |

A failed step is reported as `FAILED` and the script exits non-zero. Nothing is
skipped silently.

---

## Verifying you got the same thing

```bash
# 1. the case hashes
make verify-hashes

# 2. the manifest reflects the tree
make manifest && git diff --exit-code MANIFEST.sha256 MANIFEST.json

# 3. regeneration changes nothing
make cases && git diff --exit-code -- cases/ catalog/ invariants/ keys/

# 4. the canonical bytes hash to the reported value
shasum -a 256 results/development/case_a/canonical_payload.json
cat results/development/case_a/payload_hash.txt

# 5. compare your summary against the committed final one
diff <(sed '/run_completed_utc/d' results/development/SUMMARY.md) \
     <(sed '/run_completed_utc/d' results/final/SUMMARY.md) | head -40
```

Step 5 will show differences in the environment table (your platform, your commit)
and in the `phase` banner. Any difference in a *measured value* is a real
discrepancy and worth reporting as an issue.

---

## Cross-platform reproduction

The local determinism experiment runs on one host. The cross-platform question is
answered by `.github/workflows/determinism.yml`, which compiles both cases on
`ubuntu-latest`, `windows-latest` and `macos-latest` under Python 3.11 and 3.12,
each with a different locale and time zone, and compares against the committed
reference hashes. A separate job then asserts that every leg agreed.

The status table that workflow produces is written to
`results/final/CI_STATUS.md`. **Until that workflow has actually passed, the
supportable wording is "deterministic under the declared environment"** — and once
it passes, it becomes "deterministic across the tested supported environments",
never "platform independent".

---

## The two-phase workflow

**Phase 1 — development.** Code written, debugged, experiments designed. Results
land in `results/development/`. They are committed, so the history the freeze
separates from is visible, and they are labelled non-reportable in every file.

**Phase 2 — freeze.** `preregistration/TIER0_FREEZE.md` and
`FREEZE_MANIFEST.sha256` are generated, committed, **pushed publicly**, and tagged
`preregister-tier0-v1`. The public timestamped tag is the freeze; an internal
selection is not.

**Phase 3 — final campaign.** `make reproduce-final` runs without changing any
frozen analysis logic and writes only to `results/final/`.

If a defect is found in frozen code after the campaign, the frozen number is not
edited: the freeze version is incremented, a new public tag is pushed, and the
campaign is re-run from scratch. The amendment procedure is in `TIER0_FREEZE.md`.

---

## What you cannot reproduce, and why

* **RQ5 results.** There are none. The study has not been executed and no script
  generates participant data.
* **A Zenodo DOI.** No deposit has been made. `docs/ZENODO_RELEASE_STEPS.md` lists
  the remaining manual steps rather than inventing an identifier.
* **The 284,807-event conformance run** of the prior work. It belongs to that
  paper and is not reproduced here.

---

## Troubleshooting

**`make verify-hashes` mismatches.** Report it — that is a genuine finding. Include
your platform, Python version, and the output of
`.venv/bin/python -m experiments.run_determinism --runs-per-case 11`.

**A locale is unavailable.** The determinism experiment records the locale it
actually applied (`"en_US.UTF-8 (unavailable, fell back to C)"`) rather than
pretending it ran under one it could not set. The hash comparison is unaffected —
that is the point — but the run log will show reduced locale coverage. On Debian
or Ubuntu: `sudo sed -i '/en_US.UTF-8/s/^# //' /etc/locale.gen && sudo locale-gen`.

**Monte Carlo values differ in the fourth decimal.** Expected across NumPy
versions. Compare against the reported MCSE.

**`filterwarnings = error` fails a test on a newer dependency.** Deliberate: a
deprecation in a dependency the compiler path uses is something the artifact should
surface, not suppress. Pin to `requirements.lock` or report the deprecation.
