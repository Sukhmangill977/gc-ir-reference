# Reading the frozen documents

Some documents under `docs/` are **part of the preregistration record** and are
covered by the `preregister-tier0-v2.2` freeze manifest. They describe the state
of the world **as it was committed before the reportable campaign executed**, and
they still point at `results/final/` — the v1 output path — in places.

**They have deliberately not been updated, and they will not be.** Rewriting a
preregistered hypothesis or interpretation document after seeing the results would
destroy exactly the evidence the freeze exists to provide. A preregistration you
edit afterwards is not a preregistration.

This note is *not* frozen, and exists so a reviewer can read the frozen documents
correctly without them being altered.

---

## Which documents are frozen

| Document | Freeze role |
|---|---|
| `docs/EXPERIMENT_PROTOCOL.md` | `hypotheses_and_primary_outcomes` |
| `docs/CLAIM_TO_ARTIFACT_MATRIX.md` | `provenance_and_interpretation` |
| `docs/RESULT_INTERPRETATION.md` | `provenance_and_interpretation` |
| `docs/PAPER_REQUIREMENTS.md` | `provenance_and_interpretation` |
| `docs/FIXTURE_PROVENANCE.md` | `provenance_and_interpretation` |
| `docs/CASE_B_LDREA_TRACEABILITY.md` | `case_b_ldrea_mapping` |
| `docs/ARTIFACT_RUNS_COMPLIANCE.md` | `artifact_runs_compliance` |

`docs/REPRODUCIBILITY.md` is **not** frozen and has been kept current.

---

## How to read them

### 1. `results/final/` in a frozen document means `results/final_v2/`

The frozen documents were written when `results/final/` was the reportable output
path. **The authoritative campaign is now `results/final_v2/`.** Every result file
named in those documents exists under `results/final_v2/` with the same name.

`results/final/` still exists, holds the **superseded v1 campaign**, and is
retained unedited for provenance. It is not reportable: its freeze tag existed only
locally when that campaign ran. See `results/V1_V2_COMPARISON.md`.

### 2. The run counts are floors, and were met

`EXPERIMENT_PROTOCOL.md` and `CLAIM_TO_ARTIFACT_MATRIX.md` specify **"≥ 30 runs per
case, ≥ 60 total"**. That is a preregistered *minimum*, not a description of what
ran. The v2 campaign ran **31 per case, 62 total**, which satisfies it.

The specific figure `TD = 1.000 (60/60)` in `RESULT_INTERPRETATION.md` §on
cross-platform reproduction is the **v1** measurement. The reportable value is
**TD = 1.000 (62/62)**, in `results/final_v2/determinism_summary.json`.

### 3. `preregister-tier0-v1` in a frozen document

Where a frozen document names the freeze tag or `FREEZE_MANIFEST.sha256`, the
governing freeze for the reportable campaign is **`preregister-tier0-v2.2`** at
commit `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e`, with manifest
`preregistration/FREEZE_MANIFEST_V2.sha256` (133 files).

### 4. Where the frozen documents are still exactly right

Their substance is unaffected by any of the above. In particular:

* `EXPERIMENT_PROTOCOL.md`'s instruction that the supportable wording is
  *"deterministic across the tested supported environments"* and **never
  "platform independent"** is the rule the published claim was held to, and it
  still governs.
* `RESULT_INTERPRETATION.md`'s per-metric statements of what each number means and
  does not mean apply unchanged to the v2 values.
* `FIXTURE_PROVENANCE.md`'s 29 fixture entries — including FP-014 (the three Case A
  non-runtime ratings) and FP-020 (the author-specified Monte Carlo distributions)
  — describe the same committed inputs, which are **byte-identical** in v1 and v2.
* `CASE_B_LDREA_TRACEABILITY.md` describes the same machine-verified mapping that
  `freeze_check.py` re-verifies on every run.

### 5. The one place to look instead

For the current, machine-verified mapping from every reported number to its
evidence file and exact JSON field, use
**`artifact_review/PAPER_TO_ARTIFACT_RESULTS.md`**. It is generated from
`results/final_v2/` by `python -m tools.build_paper_result_map`, and
`tools/verify_reported_results.py` checks it on every run.

---

## Verification

That the frozen documents are unmodified is checkable:

```bash
python tools/freeze_check.py --final-v2     # includes frozen-file verification
```

`experiments/verify_freeze.py` hashes each frozen file **at the freeze commit** and
compares against `FREEZE_MANIFEST_V2.sha256`, then confirms no frozen file changed
between the freeze and the campaign. `results/final_v2/PROVENANCE.json` records
`frozen_files_changed_since_freeze: {}` and `results_commits: ["c44f25d6…"]` — the
campaign ran **at the freeze commit itself**.
