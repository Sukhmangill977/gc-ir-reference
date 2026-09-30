# Reconciliation before execution — Paper 2 v1.2 final completion pass

Generated: 2026-09-30, by direct command execution (not inferred from source
reading). Every claim below was independently re-run in this session; none
is copied from a prior Claude report without re-verification.

## 1. What exists in Git HEAD (local)

- Local branch `main`, HEAD = `95c1bf7fae0fd0850665353d6e3b0a582918c5d5`.
- `git grep` against `HEAD` (not the working tree) confirms `DEFAULT_CASES`
  in `experiments/run_determinism_v12.py` is genuinely
  `("case_a", "case_b_v1_1", "case_d_ccs0", "case_d_ccs1", "case_d_ccs2")` —
  this is real, committed source, not a working-tree-only claim.
- `cases/case_d_ccs0/expected/reference_hashes.json` and
  `cases/case_d_ccs2/expected/reference_hashes.json` are tracked at HEAD.
- `tools/write_case_d_reference_hashes.py`, `tools/freeze_check_prospective_v5.py`,
  `experiments/check_environment_container_v12.py`,
  `results/development_v12/environment_container_aarch64.json` are tracked
  at HEAD.
- `results/development_v12/case_c_exclusion.json` is tracked at HEAD.
- N1/N5/N7 neutrality checks and the `q_r`-downgrade fix in
  `src/gcir/contract_v12.py`'s `no_narrowing` are tracked at HEAD.

## 2. What exists ONLY in the working tree (uncommitted)

At the start of this reconciliation, `git status --short` showed:

```
 D docs/paper3.pdf
 M results.html
 M results/development/determinism_summary_case_b_v11.json
 M results/development/monte_carlo_summary_case_b_v11.json
?? "docs/paperieee2 (1).pdf"
?? papermain.pdf
?? results/final_v3_1/
```

`docs/paper3.pdf` (deleted), `docs/paperieee2 (1).pdf` (untracked),
`results/final_v3_1/` (untracked) are pre-existing working-tree state from
before any of this session's work — carried forward unmodified, per prior
instruction not to touch them without a documented reason.
`results.html` and the two `results/development/*_case_b_v11.json` files
drift on every `pytest` run (regenerated as a designed side effect of
`tests/unit/test_generate_results_page.py` and
`tests/integration/test_case_b_v11_*.py` respectively) — this is expected,
not a sign of untracked scientific state.

`papermain.pdf` is the real Paper 2 v1.2 manuscript (compiled PDF only, no
`.tex` source available in this environment) — untracked, added to the
working tree by the user mid-session, not yet placed anywhere in the repo
structure.

## 3. What a previous session in this conversation CLAIMED

That `experiments/run_determinism_v12.py` was extended to cover Case D
CCS0/CCS1/CCS2 (155 = 31×5 runs total), that `results/development_v12/`
was updated accordingly, that the pinned-container (environment-7) check
was re-run and updated to match, and that all of this was committed in
three local commits (`54d7f63`, `256a624`, `95c1bf7`) — but was **pushed
only through `c1a9b95`** (the results-dashboard commit), one commit short
of any of the CCS0/CCS2 work.

## 4. What is actually reproducible from HEAD — independently re-verified THIS SESSION, live

- **Historical tags, dereferenced to commits** (`<tag>^{commit}`, not the
  tag object `rev-parse` returns for an annotated tag — an early `git
  rev-parse <tag>` in this session returned the tag OBJECT hash and looked
  like a mismatch; `<tag>^{commit}` / `git rev-list -n1 <tag>` resolves the
  same annotated tags to the expected commits, confirmed clean):
  - `preregister-tier0-v3.1` → `158c0bd3785ac87a878671f76286be082a26d50d` ✅ matches expected
  - `preregister-tier0-v4` → `48791c720b9d08cc4005e0c49f6d64eab2a361f1` ✅ matches expected
  - `preregister-tier0-v4.1` → `efe4e165619ecb5d781fb795113f33720794a2e5` ✅ matches expected
  - **No historical tag moved.**
- **Case compilation, recompiled fresh, this run**:
  - `case_a` → `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` (19 predicates)
  - `case_b_v1_1` → `0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1` (12 predicates)
  - `case_d_ccs0` → `09495d8ee59a9868db4749e40812ad40a4c2683d79c931d641811a2849635912` (4 predicates) — matches committed `expected/reference_hashes.json`
  - `case_d_ccs1` → `32edcb72bd6cdcd760252bb85431a898b9aded86db2c8468ba77f4aac6b53784` (5 predicates) — matches committed
  - `case_d_ccs2` → `f7b5827d6c7fc4702d9e276b3ae34179482bcecd466bddba440103f751c603d2` (5 predicates) — matches committed
- **Local determinism, re-executed fresh this session** (not copied from
  any prior report): `experiments.run_determinism_v12` with no `--cases`
  override (i.e. the real `DEFAULT_CASES`) produced **155/155**, verified
  at the raw CSV row level: 156 lines (1 header + 155 data rows), exactly
  31 rows per case across all 5 cases, all 155 rows `PASS`, zero `FAIL`.
  File: `results/development_v12/determinism_runs.csv` (regenerated this
  run), `results/development_v12/determinism.json`.
- **Full pytest with JUnit, re-executed fresh this session**:
  `python -m pytest -q --junitxml=results/development_v12/junit_full.xml`
  → `495 passed`, and the generated XML itself states
  `tests="495" errors="0" failures="0" skipped="0"` (checked in the XML,
  not just the terminal summary).
- **`.gitattributes`/CRLF finding**: checking out commit `c1a9b95` into an
  isolated worktree showed `results/final/*.csv` and `results/final_v2/*.csv`
  as locally "modified." Investigated: `.gitattributes` declares
  `*.csv text eol=lf`, but the blobs committed for these old files are
  CRLF; git's checkout-time `eol=lf` filter normalizes them, which then
  reads as a working-tree diff against the (still-CRLF) index/blob. This
  reproduces on ANY fresh checkout of these old commits — it predates this
  session's work and is not evidence of historical data modification. The
  worktree was discarded without committing anything from it.

## 5. Every discrepancy found

| # | Discrepancy | Status |
|---|---|---|
| 1 | GitHub `origin/main` is at `c1a9b95`; the CCS0/CCS2/155-run work exists only in 3 unpushed local commits (`54d7f63`, `256a624`, `95c1bf7`) | Confirmed. Work is real (independently re-executed above), just unpublished. Not fabrication — a publication gap. |
| 2 | Manifest currency: at `c1a9b95` (the pushed commit), `README.md`, `results.html`, and `tools/generate_results_page.py` do NOT match `MANIFEST.sha256` | Confirmed, independently reproduced by replicating CI's exact check (`git show HEAD:MANIFEST.sha256` vs. a fresh `experiments.make_manifest` run) against an isolated worktree at that exact commit. Real bug: `MANIFEST.sha256` was regenerated and staged BEFORE the dashboard-generation script's own last edits were finalized in that commit, or the manifest committed doesn't reflect final file content. Root cause not yet fixed — see remaining work. |
| 3 | `experiments/reproduce_all.py` (the driver behind `make reproduce` / `run_all.py`) has zero references to `development_v12` — the v1.2 pipeline is not, and was never claimed to be, wired into the historical driver; a separate `make reproduce-v12` target exists instead | Consistent with design intent recorded in this session's own commit messages. Not a discrepancy, a documented design choice. |
| 4 | No `experiments/run_all.py` module or `--final-v5` flag exists anywhere; `run_all.py` (repo root) is a thin wrapper over `reproduce_all.main`, which has no v1.2 or final-v5 awareness | Confirmed gap. A real final-campaign driver does not yet exist — required before any `results/final_v5/` can be produced. |
| 5 | No `results/final_v5/` directory exists anywhere (checked: absent from both HEAD and the working tree) | Confirmed. No premature/fabricated final campaign exists. |
| 6 | No `preregister-tier0-v5` or `v1.2.0` tag exists, locally or (by definition, since local doesn't have it either) remotely | Confirmed via `git tag --list` above — absent. |

## 6. Every test still missing (not yet executed under this reconciliation)

- Cross-environment (CI) re-execution of the 5-case (155-run) protocol —
  the committed `.github/workflows/determinism.yml` Case-D job pair now
  requests `case_d_ccs0 case_d_ccs1 case_d_ccs2`, but no CI RUN has
  actually executed it yet (nothing has been pushed).
- A genuine 8th/frozen-reference environment definition — still pending
  the user's decision from earlier in this conversation (generate a real
  container leg for Case A + Case B v1.1 specifically, vs. correct the
  manuscript's RQ1 wording).
- `results/final_v5/` and everything under Phases 17 onward of the current
  operating brief (final campaign driver, clean-tree freeze, per-leg JSON,
  test ledger, manuscript audit, release).
- CCS2 temporal-provenance fix — still pending the user's decision
  (move the signature after 2026-03-09, or move the decision/selection
  before 2026-03-02).
- TACIP hash — still blocked; no source document available in this
  environment.

## Root cause of discrepancy #2, and its current status

At commit `c1a9b95` (the commit actually pushed to `origin/main`),
`MANIFEST.sha256` was regenerated and staged, but `results.html` was
subsequently touched again by the pytest run that happens as part of that
commit's own verification pass (`tests/unit/test_generate_results_page.py`
regenerates `results.html` with a fresh embedded timestamp) — and that
later regeneration was committed without a further manifest refresh
afterward. A real, if narrow, procedural bug in how that commit was
assembled, not a reproducibility defect in the manifest tool itself.

**This is already fixed, transitively, by the three unpushed local
commits** (`54d7f63`, `256a624`, `95c1bf7`) — each of those re-ran
`make manifest` immediately before committing. Independently confirmed,
twice, in isolated `git worktree add --detach` checkouts with no
extraneous files:
- Against current HEAD (`95c1bf7`) in-place: manifest current.
- Against current HEAD (`95c1bf7`) in a fresh, isolated worktree: manifest
  current, `pytest -q` → `495 passed`, and
  `python tools/freeze_check.py --prospective-v5` → **50/50 checks
  passed**, including MANIFEST currency.

No new manifest-fix commit is required. Pushing the three already-existing
local commits resolves discrepancy #1 and discrepancy #2 together.

## Immediate next step

Push `54d7f63`, `256a624`, and `95c1bf7` to `origin/main` (pending
confirmation, since this touches the shared remote), which brings GitHub's
visible state into agreement with what is actually implemented and
verified locally, and resolves the manifest-currency CI failure without
any further code change. Then continue into the remaining phases (final
campaign driver, clean-tree freeze, per-leg JSON, test ledger, manuscript
audit, release) — several of which remain blocked on pending decisions
from earlier in this conversation (CCS2 temporal-provenance fix direction,
the "eight environments" reconciliation approach for v1.1.0, TACIP source
document, and an editable manuscript source). Historical artifacts
(discrepancy-free per Section 4) are not touched by this or any planned
step.
