# Reportable campaign: preregister-tier0-v4.1

**Purpose: manifest/tooling correction only; scientific state byte-identical
to `preregister-tier0-v4`.**

**Freeze commit:** `efe4e165619ecb5d781fb795113f33720794a2e5`
**Freeze tag:** `preregister-tier0-v4.1` (annotated, pushed to
`github.com/Sukhmangill977/gc-ir-reference`, verified remotely to resolve to
the freeze commit above)
**Source:** a clean `git worktree` checkout of the tag (detached HEAD),
never modified. Committed separately on `main`, after the freeze, same as
`results/final_v4/` is for `preregister-tier0-v4`.

`preregister-tier0-v4` (`48791c720b9d08cc4005e0c49f6d64eab2a361f1`) and
`results/final_v4/` are **untouched** by this correction. Neither this tag
nor this directory copies `results/final_v4/` — every figure below was
independently regenerated.

## What changed vs. `preregister-tier0-v4`

`experiments/make_manifest.py` now enumerates and hashes files via Git's
own index/tree (`git ls-files` / `git ls-tree` + `git cat-file`) instead of
a raw filesystem walk, fixing the defect where local working-directory
state could leak into or drop out of the generated MANIFEST (full
reconciliation: `docs/V4_MANIFEST_DEFECT_REPORT.json`). Nothing else.
**`SCIENTIFIC_DIFF_COUNT` between `preregister-tier0-v4` and
`preregister-tier0-v4.1` = 0** across `cases/`, `src/gcir/`,
`preregistration/`, every Case B v1.1/Case C injection/determinism/Monte
Carlo experiment module, and `schemas/` — verified by `git diff` before
tagging.

## Case A / Case B v1.1 — unchanged

| | expected | actual | match |
|---|---|---|---|
| Case A hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | same | yes |
| Case B v1.1 hash | `0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1` | same | yes |

Case B v1.1 structure: 6 risks, 6 dispositions, 9 ACS, 9 risk-derived + 3
compiler invariant = 12 predicates.

## Audit, injections, provenance, determinism, Monte Carlo, L-DREA/ULB

All identical to `results/final_v4/` — see the field-by-field comparison
below. Q1-Q10 10/10 for all four cases; 19/19 negative fixtures; A1-A4 as
before; 14/14 injection rows (two-axis aggregate: authorization {PERMIT: 1,
DENY: 8, HOLD: 4}, release {ALLOW_RELEASE: 12, BLOCK_RELEASE: 1}); all 9 ACS
provenance-complete; determinism TD=1.000 62/62; Monte Carlo K=250000
seed=20260201 reproducing the same FP_heat/GD figures; the original
284,807-row L-DREA experiment reproduced again (byte-identical row-level
output, same SHA-256 as the `final_v4` run, since the computation is fully
deterministic).

## Test suite

**446 tests, 0 failures, 0 errors, 0 skipped** (438 from `final_v4` + 8 new
`tests/unit/test_make_manifest.py` regression tests proving the fix).

## Freeze verification (prospective-v4 checker)

**45/45 checks pass, including the MANIFEST self-consistency check** — the
exact check that failed for `preregister-tier0-v4` (comparing MANIFEST.json
against the committed HEAD tree via `git ls-tree`/`git cat-file`) now passes
cleanly from a genuine clean checkout, with zero findings.

## Automated comparison: `final_v4` vs. `final_v4_1`

Every scientific field compared programmatically
(`case_a_hash`, `case_b_historical_hash`, `case_b_v1_1_hash`, `case_c_hash`,
`case_b_v1_1_structure`, `audit_queries`, `negative_fixtures`,
`auxiliary_checks_a1_a4`, `case_b_v1_1_injections`,
`case_b_v1_1_provenance`, `determinism`, `monte_carlo`, and every L-DREA/ULB
figure): **all MATCH exactly.**

Two differences, both expected and non-scientific:
- `test_suite.tests`: 438 → 446 (+8 new manifest regression tests; this is
  the fix's own test coverage, not a change to any case, query, fixture,
  injection expectation, or experiment).
- `freeze_verification_prospective_v4.passed`: `false` → `true` — this is
  precisely the defect being corrected, not new drift.

No other field in either campaign's `campaign_results.json` differs.
