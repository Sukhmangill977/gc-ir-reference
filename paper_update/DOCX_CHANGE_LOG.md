# MEASURED manuscript copy — change log

Source:      From_Risk_Register_to_Runtime_Predicate_FINAL.docx
Destination: From_Risk_Register_to_Runtime_Predicate_MEASURED.docx

**The original manuscript is not modified.** This log records every change
made to the copy, and every change that was deliberately left for manual
application because it alters meaning rather than a value.

---

## Applied automatically (7)

### `translation determinism of 1.000 over 31 compilation runs`

**Replaced with:** translation determinism of 1.000 over 60 compilation runs (30 per case)

**Why:** Abstract: the reportable campaign ran 60 runs, not the provisional 31. Evidence: results/final/determinism_runs.csv

### `[PENDING: hash-pinned Case B artifact release]`

**Replaced with:** Case B canonical bundle payload SHA-256: 2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce

**Why:** Section X: placeholder resolved. Evidence: cases/case_b/expected/reference_hashes.json

### `1.000 (31/31 runs, pinned container)`

**Replaced with:** 1.000 (60/60 runs; 30 per case, declared host environment)

**Why:** Section XI-B metrics table: measured count and the actual execution environment. The 60 reported runs were executed on a host, not inside the container; a pinned container definition ships with the artifact. Evidence: results/final/determinism_summary.json

### `the maximum per-risk heat-map flip probability is 0.321`

**Replaced with:** the maximum per-risk heat-map flip probability is 0.321 (MCSE 0.001)

**Why:** Section XI-G: value confirmed at K = 250,000; Monte Carlo standard error added. Evidence: results/final/monte_carlo_summary.json

### `while FPᵢ^C* = 0.000 across the register by construction`

**Replaced with:** while FPᵢ^C* = 0.000 across the register -- verified by re-running the approved consequence-class classifier on 1,000 perturbed draws, with no membership change observed

**Why:** Section XI-G: the zero is verified rather than asserted. Evidence: results/final/monte_carlo_summary.json cstar_membership_changes_observed

### `Measured: TD = 1.000 over 31 compilation runs`

**Replaced with:** Measured: TD = 1.000 over 60 compilation runs (30 per case)

**Why:** Section XI-H: measured count. Evidence: results/final/determinism_runs.csv

### `[PENDING: v1.0 freeze and $id host set at the artifact-repository release]`

**Replaced with:** The schema is frozen at v1.0 and hash-pinned in the release manifest; schema $id values are stable identifiers rather than resolvable endpoints, and the authoritative copies are the files in the tagged release.

**Why:** Appendix A: placeholder resolved as far as it honestly can be. A resolvable $id host is NOT claimed, because none is maintained. Evidence: preregistration/FREEZE_MANIFEST.sha256

---

## Left for manual application — these change meaning (8)

A script should not silently rewrite what a claim means. Each of these is
specified with publication-ready wording in the referenced file.

### Section XI-G / XI-C -- Monte Carlo panel attribution

The manuscript states that 'the independent panel freezes discrete probability masses over plausible ratings'. NO PANEL HAS BEEN CONVENED. The distributions are author-specified. This is the single most important correction and it changes what the result means, so it is left for manual application.

See: `paper_update/MEASURED_RESULTS.md section 5`

### Section IX -- publish the three non-runtime rows' ratings

GD_min = 3 is computed over all sixteen rows, but the table publishes L x I for only the thirteen runtime rows, so the value is not reproducible from the paper. Add R-14 = 12, R-15 = 6, R-16 = 8 and the sensitivity sentence (GD_min ranges 2-5 across plausible ratings).

See: `paper_update/MEASURED_RESULTS.md section 2.2`

### Section IX -- 'three-way collision at s = 12'

On the pinned artifact the score-12 collision has four members, because R-14 also rates 12. Scope the sentence to the runtime rows.

See: `paper_update/MEASURED_RESULTS.md section 2.3`

### Section XII -- two new limitations

Add the GD_min fixture-sensitivity limitation and the sensitivity-model provenance limitation.

See: `paper_update/MEASURED_RESULTS.md sections 8.2 and 8.3`

### Section XI-I -- held-out-register hash

The Tier-0 freeze does not contain one, because no held-out register has been authored. State that it is committed in a Tier-1 freeze before recruitment opens.

See: `paper_update/MEASURED_RESULTS.md section 13`

### Appendix C / Data & Code Availability -- repository path

'[TO CONFIRM: final repository path at release]' cannot be resolved until the repository is pushed. No DOI exists; do not cite one.

See: `docs/ZENODO_RELEASE_STEPS.md`

### Section XII -- determinism scope

LEAVE UNCHANGED. The cross-platform CI matrix is configured but has not run, so the limitation still holds as written.

See: `results/final/CI_STATUS.md`

### Sections II and XIII -- [VERIFY] markers

A final literature sweep and a sentence-level overlap check against the published version of [15]. Author tasks; no artifact can discharge them.

See: `-`

---

## Deliberately untouched

* Propositions 1–3, their statements and their proofs.
* The claim boundary (Section XIV), the non-contributions (Section I-D),
  and the limitations (Section XII) other than the two additions listed above.
* Everything concerning RQ5, which remains preregistered and deferred.
* The evidence classification of Case B as a forensic reconstruction, and
  of the 284,807-event run as conformance-class evidence belonging to [15].
* Every `[TO REPORT]` marker for SNR and DF: no value exists.
