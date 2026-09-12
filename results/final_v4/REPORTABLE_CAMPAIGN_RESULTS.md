# Reportable campaign: preregister-tier0-v4

**Freeze commit:** `48791c720b9d08cc4005e0c49f6d64eab2a361f1`
**Freeze tag:** `preregister-tier0-v4` (annotated, pushed to
`github.com/Sukhmangill977/gc-ir-reference`, verified remotely to resolve to
the freeze commit above)
**Source:** a clean `git worktree` checkout of the tag (detached HEAD),
never modified. This directory (`results/final_v4/`) is committed to `main`
separately, after the freeze; it is not itself part of the tagged tree, the
same way `results/final_v2/`, `results/final_v3/`, and `results/final_v3_1/`
are post-freeze evidence for their respective tags.

## Case A — unchanged

| | expected | actual | match |
|---|---|---|---|
| payload hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | same | yes |

Byte-identical to `preregister-tier0-v3.1`. Confirmed independently via
determinism (31/31) and Monte Carlo (`FP_heat=0.321268`, risk `R-06`,
`GD_approved=3`) — all reproduced fresh from this exact checkout.

## Case B v1.1

| | expected | actual | match |
|---|---|---|---|
| payload hash | `0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1` | same | yes |

Structure: 6 risks, 6 dispositions, 9 ACS, 9 risk-derived + 3 compiler
invariant = 12 predicates (see `case_b_v1_1/bundle.json` `statistics`).
Governance provenance chain complete for all 9 ACS
(`provenance/case_b_v11_provenance_9_acs.json`).

## Case B (historical) and Case C

Case B historical hash `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce`
unchanged. Case C hash `d7c7971156e3591b64567148ed8fc21cc1cbee21973d3646f59e439c74bf1dbd`
matches its committed reference.

## Audit evidence

- Canonical Q1-Q10: **10/10** for Case A, Case B (historical), Case B v1.1,
  and Case C (`audit/q1_q10_all_cases.json`).
- Negative fixtures: **19/19 detected** (`audit/negative_fixtures_19.json`).
- A1-A4: A1 (applicable) correctly detects a revoked actuation; A2/A3/A4
  correctly report `NOT_APPLICABLE` when no evidence is supplied — never
  counted as PASS (`audit/auxiliary_checks_a1_a4.json`).

## Case B v1.1 injections

**14/14 rows pass** (13 injection scenarios + clean control;
`injections/case_b_v11_13_injections.json`). Two-axis aggregate over the 13
injection rows: `authorization_decision` {PERMIT: 1, DENY: 8, HOLD: 4},
`release_decision` {ALLOW_RELEASE: 12, BLOCK_RELEASE: 1}. `externalization`
0/13. TOCTOU row: `authorization_decision=PERMIT`, `safe_state=false`,
`release_decision=BLOCK_RELEASE`, `release_safe=true`,
`externalization=false`.

## Determinism

`determinism/determinism_summary_case_b_v11.json`: **TD = 1.000, 62/62**
(Case A 31/31, Case B v1.1 31/31), reference hashes match the values above.

## Monte Carlo

`monte_carlo/monte_carlo_summary_case_b_v11.json`: K=250,000, seed=20260201.
Case A `max_FP_heat=0.321268` (risk R-06), Case B v1.1
`max_FP_heat=0.317980` (risk B-01), `FP_C*=0`, `GD_approved=4`,
`GD_min_mean=0.0` — reproduces the historical Case B figures exactly.

## Test suite

`tests/junit_full.xml`: **438 tests, 0 failures, 0 errors, 0 skipped.**

## ieee-check-v4

`ieee_check/ieee_check_v4_result.json`: **PASSED, 3/3 stages.**

## Freeze verification (prospective-v4 checker)

`freeze_verification/prospective_v4_check.json`: 44/45 individual checks
pass. **One check fails — a non-scientific MANIFEST bookkeeping
discrepancy, not a data-integrity problem** (full explanation in
`campaign_results.json`'s `freeze_verification_prospective_v4.explanation`
field, and in this document's "Explained differences" section below).

## L-DREA / ULB

`ldrea_ulb/gamma_summary.json`, `gamma_lab_v1_report.json`: the original,
unmodified 284,807-row L-DREA experiment
(`github.com/AGLakhowal/Gamma-Permit-Package` @ `40fa8f0`) reproduced fresh
from this campaign: 492 fraud-labelled rows, 0 false permits, 0 false
denials, 100% decision agreement — identical to the committed report.
GC-IR↔downstream predicate-family correspondence
(`ldrea_traceability.json`, `ldrea_traceability_v1_1_addendum.json`): 4
exact, 3 family, 5 not_established across all 12 Case B v1.1 predicates. A
new v1.1 12-predicate ULB replay was **not executed** — see
`ldrea_ulb/CASE_B_LDREA_ULB_REPLAY_ASSESSMENT.md` for the reasoned decision.
**No fraud-detection accuracy claim is made anywhere in this campaign.**
The 128 MB row-level CSV this run produced is not committed (size); its
SHA-256 and regeneration instructions are in
`ldrea_ulb/NOTE_row_level_csv_not_committed.md`.

## Explained differences vs. pre-freeze `results/development/` evidence

Every scientific figure above (both case hashes, Q1-Q10, 19 fixtures, A1-A4,
13 injections, provenance, determinism TD=1.000/62/62, Monte Carlo
FP_heat/MCSE/GD values, 438/438 tests, L-DREA reproduction) is
**value-for-value identical** to the corresponding pre-freeze
`results/development/*_case_b_v11*` evidence generated during this same
generation of work. This is expected: nothing scientific changed between
pre-freeze verification and this campaign run — the campaign simply
re-executes the same frozen code against the same frozen inputs, from a
genuinely clean checkout instead of the development working directory.

The one non-identical item is the freeze-verification MANIFEST
self-consistency check itself, which is **less permissive** here than it
was pre-freeze, precisely because this is the first time it has been run
against a real `git worktree` checkout rather than the (locally dirty)
development directory. It surfaced a real, pre-existing, non-scientific gap
in `experiments/make_manifest.py` (it walks the filesystem rather than
`git ls-files`, so uncommitted/gitignored local state can leak into a
generated manifest) — a genuine and useful finding from running "the entire
reportable campaign" as instructed, not evidence of anything going wrong
with Case A, Case B v1.1, or any other scientific artifact. No retagging
was performed; `preregister-tier0-v4` remains exactly as pushed.
