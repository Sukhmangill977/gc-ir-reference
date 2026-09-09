# CI evidence

The three workflows, all green on the current HEAD. Run IDs are recorded so a
reviewer can open each one directly.

---

## Final successful runs

**Commit `675d2fc4d811` — the `v1.0.2` release commit (final pre-submission)**

| Workflow | Run ID | Result |
|---|---|---|
| `tests` | **34325410118** | ✅ success |
| `cross-platform determinism` | **34325410022** | ✅ success |
| `reproducibility` | **34325410136** | ✅ success |

The preceding commit `9a18244` was also fully green (`tests` 34325156932,
`determinism` 34325156894, `reproducibility` 34325156902), as was `9280698`
(`tests` 34324938516, `determinism` 34324938569, `reproducibility` 34324938666).

### Earlier: commit `836436baa6e8` — the `v1.0.1` release commit

| Workflow | Run ID | Result | Duration | Link |
|---|---|---|---|---|
| `tests` | **34315187544** | ✅ success | 1m17s | [run](https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34315187544) |
| `cross-platform determinism` | **34315187589** | ✅ success | 1m19s | [run](https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34315187589) |
| `reproducibility` | **34315187557** | ✅ success | 2m02s | [run](https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34315187557) |

The following documentation commit `0bf23f6` is also fully green (`tests`
34315506153, `determinism` 34315506155, `reproducibility` 34315506144). `main`
may sit ahead of the release tag; **`v1.0.1` at `836436b` is the artifact of
record**, and the runs in the table above are its runs.

The immediately preceding commit `5dea99f1a0ef` was also fully green
(`tests` 34314658635, `determinism` 34314658496, `reproducibility` 34314658462);
its per-job breakdown is what is listed below, and the job matrices are identical.

### `tests` — 6/6 matrix legs

```
success  tests (ubuntu-latest,  python 3.11)
success  tests (ubuntu-latest,  python 3.12)
success  tests (macos-latest,   python 3.11)
success  tests (macos-latest,   python 3.12)
success  tests (windows-latest, python 3.11)
success  tests (windows-latest, python 3.12)
```

### `cross-platform determinism` — 6 legs plus the agreement job

```
success  reference hashes (ubuntu-latest,  py3.11, C.UTF-8,     UTC)
success  reference hashes (ubuntu-latest,  py3.12, C.UTF-8,     UTC)
success  reference hashes (macos-latest,   py3.11, en_US.UTF-8, Pacific/Chatham)
success  reference hashes (macos-latest,   py3.12, en_US.UTF-8, Pacific/Chatham)
success  reference hashes (windows-latest, py3.11, C,           Asia/Kolkata)
success  reference hashes (windows-latest, py3.12, C,           Asia/Kolkata)
success  all platforms agree on the reference hashes
```

Each leg runs under a different locale and time zone, so agreement is a
determinism result, not a repetition.

### `reproducibility` — both jobs

```
success  make reproduce (ubuntu-latest)
success  docker build and reproduce
```

---

## The measurement run of record

Separate from the runs above, the **cross-environment determinism evidence the
article cites** comes from:

| | |
|---|---|
| Run | [**34261657261**](https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34261657261) |
| Recorded in | `results/final_v2/CI_STATUS.md` |
| Artifacts | `results/final_v2/cross_environment/ci/` — the six per-leg `determinism_summary.json` files, committed |
| Result | TD = 1.000 on all 8 environments; identical reference canonical payload hashes; 496 compilations |

`tools/verify_reported_results.py` re-reads those per-leg files on every run and
confirms each reports TD = 1.0 with reference hashes matching the main summary.

---

## Failures encountered and fixed — no red run was waived

Three CI failures occurred during this packaging work. Each was diagnosed from
the actual log and fixed at the cause.

### 1. Run `34311015446` — `reproducibility` / "Verify MANIFEST.sha256 is current"

**Cause.** The manuscript-finalization commit added seven files — six under
`paper_update/` and `tools/build_submission_docx.py` — without regenerating the
root manifest. Both paths already have role rules in
`experiments/make_manifest.py`, so the files were intentionally manifested; the
manifest had simply not been rebuilt.

**Evidence it was benign.** The diff was **additions only** — seven new rows plus
`MANIFEST.json`'s own row, which necessarily changes because it embeds every
file's hash. No existing file's hash changed, and the seven hashes matched those
CI computed independently.

**Fix.** Regenerated `MANIFEST.sha256` / `MANIFEST.json`. The scientific
reproduction itself had passed; no result was altered to make CI green, and
`FREEZE_MANIFEST_V2.sha256` was not touched.

### 2. Run `34314196961` — `tests`, all 6 legs

**Cause.** A design flaw in the new `tools/verify_reported_results.py`. The
`tests` workflow checks out without tags, so the freeze-tag cross-check could not
resolve `preregister-tier0-v2.2` and reported a **failure**. Absence of the tag
is not evidence that the recorded freeze commit is wrong.

**Fix.** Checks now have three states. A skipped check reports `SKIP`, is listed
explicitly in the summary, and does not fail the run. A tag that *is* present but
points at the wrong commit still fails — with a test asserting exactly that, so
the skip path cannot become a way for a wrong tag to pass.

### 3. Run `34314513010` — `tests`, all 6 legs

**Cause.** A stale assertion in my own test, written before the skip state
existed: `assert len(blob["checks"]) == blob["passed"]`. True in a full clone
(0 skips), false in CI (1 skip). It passed locally and failed on all six legs.

**Fix.** The assertion now checks that `passed + failed + skipped` accounts for
every check. Verified in both a full clone and a `--depth 1 --no-tags` clone.

**None of these was ignored, waived, or worked around by weakening a check.**
Failure 2 in particular was fixed by making the check *more* precise, not less.

---

## Workflow configuration

| Workflow | Triggers | Notes |
|---|---|---|
| `tests` | push to `main`, tags, PR | 6-leg OS × Python matrix |
| `determinism` | push to `main`, tags, PR | 6 legs under varying locale and time zone, plus an agreement job |
| `reproducibility` | push to `main`, tags, weekly cron | Full `make reproduce` plus a digest-pinned Docker build; the weekly schedule surfaces environment bit-rot on its own rather than at submission time |

The `reproducibility` workflow also asserts that regenerating the case artifacts
leaves the committed tree unchanged (`git diff --exit-code -- cases/ catalog/
invariants/ keys/`), so a silent change to a case fixture cannot pass CI.
