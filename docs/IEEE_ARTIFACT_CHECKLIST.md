# IEEE_ARTIFACT_CHECKLIST.md

Self-assessment against the criteria an IEEE artifact evaluation typically applies.
Every "yes" names the file that discharges it; every gap is stated as a gap.

---

## Available

| Criterion | Status | Evidence |
|---|---|---|
| Publicly accessible | yes | Public GitHub repository; tagged release `v1.0.0` |
| Permanent identifier | **outstanding** | No Zenodo deposit has been made. `docs/ZENODO_RELEASE_STEPS.md` lists the remaining manual steps. **No DOI is claimed or invented.** |
| Licence | yes | `LICENSE` (MIT), matching the precedent named in Appendix C |
| Citation metadata | yes | `CITATION.cff` |
| Complete relative to the paper | yes | `docs/CLAIM_TO_ARTIFACT_MATRIX.md` maps every claim to its component, test, output file and manuscript section |

## Functional

| Criterion | Status | Evidence |
|---|---|---|
| Documented | yes | `README.md`, `docs/REPRODUCIBILITY.md`, `docs/EXPERIMENT_PROTOCOL.md`, module docstrings citing manuscript sections |
| Consistent with the paper | yes | `docs/PAPER_REQUIREMENTS.md` extracts every normative requirement before implementation |
| Complete | yes | Schemas, `Ψ_K` tooling, `Φ`, both cases, queries, tests, experiments, preregistration — the full Appendix C list |
| Exercisable | yes | `make install && make test && make verify-hashes` from a clean clone |
| Includes its own test suite | yes | 275 tests across four suites |

## Reusable

| Criterion | Status | Evidence |
|---|---|---|
| Dependencies pinned | yes | `requirements.lock`, `pyproject.toml`; Docker base image pinned **by digest** |
| Environment reproducible | yes | `Dockerfile`; `make docker-reproduce` |
| One-command reproduction | yes | `make reproduce` / `python -m experiments.reproduce_all` |
| Results machine-readable | yes | JSON and CSV under `results/`; `SUMMARY.md` generated from them |
| Provenance on every result | yes | git commit, tag, tree-clean flag, Python version, platform, dependency versions |
| Structured for reuse | yes | `src/gcir/` is an importable package with no framework dependency |
| CI | yes | Three workflows; cross-platform matrix; a failure fails the workflow |

---

## Reproducibility specifics

| Question | Answer |
|---|---|
| Can a reviewer reproduce the main results? | Yes. `make reproduce`, ~90 s. |
| Is the expected output stated in advance? | Yes. Reference hashes are committed in `cases/*/expected/`; success criteria are frozen in `preregistration/TIER0_FREEZE.md`. |
| Are exploratory and reportable results separated? | Yes. `results/development/` vs `results/final/`, with the separation enforced by a public timestamped tag. |
| Are randomness sources controlled? | Yes. Every seed is frozen and recorded; the compiler itself contains no RNG at all, asserted statically. |
| Is the environment recorded? | Yes, in every result file. |
| Are failures reported? | Yes. `reproduce_all` reports each step's status and exits non-zero on any failure; an adversarial case rejected with the wrong code is `CODE_MISMATCH`, not a pass. |

## Scientific-integrity specifics

| Question | Answer |
|---|---|
| Does any reported number come from anywhere but executed code? | No. `SUMMARY.md` is generated from result files; nothing is typed by hand. |
| Were manuscript values used as targets? | No. No script reads a manuscript value. `docs/PAPER_REQUIREMENTS.md` §18 lists the provisional numbers explicitly so they can be *compared against*, not reproduced. |
| Are synthetic values distinguished from measurements? | Yes, individually. `docs/FIXTURE_PROVENANCE.md` gives every fixture an FP-nnn identifier, the reason it was needed, and the basis for its value. |
| Is any human-study data present? | No. RQ5 is deferred; no script generates, simulates or approximates participant data. |
| Are methodological deviations from the manuscript declared? | Yes. FP-020 (Monte Carlo distributions are author-specified, not panel-adjudicated) and FP-014 (`GD_min` sensitivity to unstated ratings) are stated in the freeze, in the result files, and in `paper_update/MEASURED_RESULTS.md`. |
| Are limitations discoverable without reading the code? | Yes. `README.md` "Limitations", `docs/RESULT_INTERPRETATION.md`, and a "Deferred and out of scope" section in every generated summary. |

---

## Known gaps, stated rather than papered over

1. **No DOI.** No Zenodo deposit has been made. Remaining steps in
   `docs/ZENODO_RELEASE_STEPS.md`.
2. **Held-out-register hash outstanding.** Section XI-I lists one; no held-out
   register has been authored, so none is committed. Recorded in
   `preregistration/HELD_OUT_REGISTER.md`; must be discharged in a Tier-1 freeze
   before RQ5 recruitment.
3. **RQ5 not executed.** By design and by preregistration.
4. **`GD_min` depends partly on fixture ratings.** Measured and reported as a
   sensitivity range (FP-014), not hidden.
5. **Monte Carlo distributions are author-specified.** Declared deviation (FP-020).
6. **Cross-platform determinism is a CI claim, not a local one.** Scoped wording
   used throughout.
7. **The container image digest is environment-specific.** The `Dockerfile` and
   lock file are frozen; the built digest is recorded by CI rather than committed.
