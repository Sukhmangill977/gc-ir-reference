# Proposed Scientific Freeze: `preregister-tier0-v4` (NOT YET CREATED)

**Status: PREPARATION ONLY. No tag has been created. No commit has been made
under this proposal.** This document exists so the proposed freeze can be
reviewed before `git tag` is ever run.

## Why `v4`, not `v2.3`

The runbook this generation started from (`RUNBOOK v1_1_0 refreeze.pdf`)
assumed a baseline of `v1.0.3` / `preregister-tier0-v2.2` and proposed the
next freeze be `preregister-tier0-v2.3`. That baseline is stale: this
repository has since progressed through `preregister-tier0-v3`,
`preregister-tier0-v3.1` (the current frozen campaign,
`results/final_v3_1/`), and releases through `v1.0.5`. `preregister-tier0-v2.3`
would be a **backward** identifier relative to already-published `v3` and
`v3.1` tags — never create it. The correct next forward-only identifier,
per the task's explicit instruction, is:

```
preregister-tier0-v4
```

## Immutable historical evidence (untouched, unmodified, unmoved)

```
preregister-tier0-v1
preregister-tier0-v2
preregister-tier0-v2.1
preregister-tier0-v2.2
preregister-tier0-v3
preregister-tier0-v3.1   <- current frozen campaign, results/final_v3_1/
v1.0.0 .. v1.0.5
results/final_v2/
results/final_v3/
results/final_v3_1/
```

All verified present and unmodified as of this proposal (`git tag --list`,
confirmed above; `results/final_v3_1/` never read from or written to by this
generation's work).

## The "9-file historical drift" is a tooling artifact, not scientific drift

`tools/freeze_check.py --final-v2` resolves to the newest historical tag,
`preregister-tier0-v3.1`, and reports 9 frozen file(s) not matching the
manifest at the freeze commit. This has been fully root-caused this session
and is **two independent, pre-existing bugs in
`experiments/verify_freeze.py`**, neither introduced by this generation's
work, and it does **not** indicate any file was modified after any freeze:

1. `FREEZE_MANIFESTS = {"preregister-tier0-v1": ..., "preregister-tier0-v2":
   ...}` has no entry for `preregister-tier0-v3` or `-v3.1`. `manifest_for()`
   silently falls back to `FREEZE_MANIFEST_V2.sha256` for any other tag — so
   verifying `v3.1` actually compares the `v3.1` commit's files against the
   **`v2`-era** manifest, not `FREEZE_MANIFEST_V3_1.sha256`.
2. Even with the right mapping, `preregistration/FREEZE_MANIFEST_V3_1.sha256`
   uses a 2-column format (`<sha256>  <path>`, no category token), while
   `parse_manifest()` requires >= 3 whitespace-separated tokens per line and
   silently skips (`continue`) any line with fewer — so it parses to **0
   rows** regardless of the mapping bug.

Per the task's explicit instruction, `experiments/verify_freeze.py` and the
historical manifest files were **not** modified to paper over this — the old
`--final-v2` check remains exactly as broken/passing as it already was; this
is a historical-checker-only defect. Direct verification this session
(`git rev-parse <freeze_commit>:<path>`, hashed and compared to what
`FREEZE_MANIFEST_V3_1.sha256` actually records) confirms all 8 unique files
in the false-positive list are innocent:

| File | Recorded in `FREEZE_MANIFEST_V3_1.sha256`? | Hash at freeze commit vs. manifest |
|---|---|---|
| `experiments/case_b_injection_scenarios.py` | yes | **matches exactly** |
| `src/gcir/precedence.py` | yes | **matches exactly** |
| `Makefile` | yes | **matches exactly** |
| `tests/unit/test_core.py` | yes | **matches exactly** |
| `experiments/common.py` | not present in v3.1's manifest scope | n/a — compared against the wrong (v2) manifest only |
| `experiments/run_adversarial.py` | not present in v3.1's manifest scope | n/a — compared against the wrong (v2) manifest only |
| `docs/ARTIFACT_RUNS_COMPLIANCE.md` | not present in v3.1's manifest scope | n/a — compared against the wrong (v2) manifest only |
| `tools/freeze_check.py` | not present in v3.1's manifest scope | n/a — compared against the wrong (v2) manifest only |

4 of the 8 files ARE in v3.1's real manifest and their current committed
content at the freeze commit is byte-identical to what that manifest
recorded — zero drift. The other 4 were never part of v3.1's manifest scope
at all (they evolved normally, as ordinary non-frozen files, between `v2` and
`v3.1`); the checker only flagged them because bug #1 sent it to the wrong
(`v2`) manifest, where their v2-era hashes naturally no longer match their
current, legitimately-evolved content. **Classification: pure
tooling/infrastructure defect in the historical verifier, zero scientific
content, zero contamination of this prospective freeze** — this checker
(`tools/freeze_check_prospective_v4.py`) is new code that never reads
`experiments/verify_freeze.py` or any `FREEZE_MANIFEST_V*.sha256` file, so
the bug cannot propagate into it.

## A real, independent `--prospective-v4` verifier now exists

`tools/freeze_check_prospective_v4.py` (dispatched via
`python tools/freeze_check.py --prospective-v4`) is a new, from-scratch
checker — 42 individual checks — that verifies the CURRENT prospective v1.1
state directly (Case A isolation and generator-reproducibility, Case B v1.1's
9 ACS and full provenance chain, Case C compilation and the genuine
reversibility qualifier, canonical Q1-Q10 for all four cases, all 19 negative
fixtures, A1-A4, all 13 Case B v1.1 injection scenarios on both decision
axes, Case B v1.1's own determinism and Monte Carlo evidence, dependency
lock/Dockerfile presence, MANIFEST working-tree self-consistency, and that
the historical tags are unchanged). It does not read, call, or depend on
`experiments/verify_freeze.py` or any historical `FREEZE_MANIFEST_V*.sha256`
file. Current result: **PASSED — 42/42 checks**, recorded via
`make ieee-check-v4` → `results/development/ieee_check_v4_result.json`
(distinct from the historical, still-unwritten
`results/development/ieee_check_result.json`, which `make results` reports
honestly as "no recorded machine-readable result" since `--final-v2` was not
modified and still fails on the bug above).

## Current state this proposal would freeze

**Git HEAD (uncommitted at time of writing):** `efe84dc2dfa4502f270dd940c63d7a6e25760d72`
(this is the commit BEFORE this session's changes are committed — the actual
freeze commit will differ once the work below is committed).

**Case hashes:**

| Case | Schema | Hash | Status |
|---|---|---|---|
| A | 1.0 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | Byte-identical to frozen v3.1 |
| B (historical) | 1.0 | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | Byte-identical to frozen v3.1 |
| B v1.1 (new) | 1.1 | `0d8b602a4c8af888beb27058b7217893eff92d2f9df7f2944d35347c1031cfc1` | New: 9 ACS per manuscript Table II |
| C (new) | 1.1 | `d7c7971156e3591b64567148ed8fc21cc1cbee21973d3646f59e439c74bf1dbd` | New: first-ever compilation |

## What the freeze would include

```
src/gcir/                          -- all modules, including new v1.1:
  precedence_v11.py                     phase-aware resolver
  auxiliary_checks.py                   A1-A4
  audit_queries.py                      canonical Q1-Q10 (rewritten, real)
  negative_fixtures.py                  19 fixtures across all 10 queries
  models.py, compiler.py, coverage.py,  (extended, not replaced)
  validation.py, precedence.py

schemas/                           -- v1.0 schemas (unchanged semantics,
                                       $id host updated) + v1.1 additions:
  actor_scope_revocation.schema.json
  safety_event.schema.json
  human_response.schema.json
  delegated_permit.schema.json
  (common/gcir/acs/bundle/assessment/cstar_profile/invariant_register/
   receipt: extended with v1.1 optional fields, additive only)

cases/
  case_a/                           -- UNCHANGED, byte-identical
  case_b/                           -- UNCHANGED, byte-identical
  case_b_v1_1/                      -- NEW: 9-ACS Case B
    inputs/, judgment/, dispositions/, acs/, expected/
    ldrea_traceability_v1_1_addendum.json
  case_c/                           -- NEW: first compiled Case C
    inputs/, judgment/, dispositions/, acs/, expected/

tools/
  case_b_v11_control.py, build_case_b_v11.py
  case_c_data.py, case_c_control.py, build_case_c.py
  invariants_data.py (extended: opt-in enforcement_phase)
  record_ieee_check_result.py

experiments/
  case_b_v11_injection_scenarios.py  -- 13 scenarios, exact category outcomes
  case_c_injection_scenarios.py      -- 12 scenarios (E1-E12)
  make_manifest.py (extended: case_b_v1_1 / case_c roles)

tests/                              -- all new test files (see below)

docs/
  CASE_B_V1_1_RATIONALE.md
  CASE_C_STATUS.md
  PROPOSED_FREEZE_V4_MANIFEST.md (this file)

requirements.lock                   -- unchanged (no new runtime dependency)
Dockerfile                          -- unchanged
tools/freeze_check_prospective_v4.py -- NEW: independent 42-check verifier
tools/record_ieee_check_v4_result.py -- NEW: records ieee-check-v4 result
src/gcir/provenance.py             -- NEW: ACS governance provenance verifier
tests/integration/test_provenance.py           -- NEW: 11 tests
experiments/run_determinism_case_b_v11.py      -- NEW: Case B v1.1's own TD run
experiments/run_monte_carlo_case_b_v11.py      -- NEW: Case B v1.1's own MC run
tests/integration/test_case_b_v11_determinism.py  -- NEW
tests/integration/test_case_b_v11_monte_carlo.py  -- NEW

MANIFEST.sha256 / MANIFEST.json     -- regenerated: 432 files, 31 roles.
                                       The manifest's own root hash is
                                       necessarily a moving target while this
                                       very document (itself a manifest
                                       entry) is still being edited -- see
                                       MANIFEST.json's own manifest_sha256
                                       field for the authoritative current
                                       value at any given moment, exactly as
                                       `tools/freeze_check_prospective_v4.py`
                                       already excludes MANIFEST.json from
                                       its own self-consistency check for the
                                       same reason.
```

**New test files** (all passing, see FINAL REPORT for exact counts):
`tests/unit/test_v1_1.py`, `tests/integration/test_case_b_v11.py`,
`tests/integration/test_case_b_v11_auxiliary.py`,
`tests/integration/test_case_c.py`,
`tests/adversarial/test_case_b_v11_injections.py`,
`tests/adversarial/test_case_c_injections.py`.

**Seeds and distributions:** unchanged from `preregister-tier0-v3.1` — Monte
Carlo seed `20260201`, `K=250,000`, the 31-run-per-case determinism matrix
design (10 repeat, 10 row_shuffle, 5 key_shuffle, 3 locale, 3 timezone). Run
explicitly through Case B v1.1's own compiled bundle this session (not
reused from historical Case B's evidence): determinism TD=1.000 (62/62,
Case A + Case B v1.1 paired), Monte Carlo max FP_heat=0.317980 (risk B-01,
MCSE 0.000931) — reproduced, not assumed, since Case B v1.1 shares Case B's
six risks/ratings and only its ACS/predicate structure differs.

## What is explicitly NOT ready to freeze yet

- Case C's E13-E19 injection scenarios (require a live runtime/simulator) are
  deferred, not executed — E1-E12 are implemented and tested. Do not report
  19/19 for Case C.
- No Case B v1.1 / Case C reportable campaign has been executed under a
  dedicated `results/final_v4/`-style directory; all figures above come from
  direct compilation and the existing `results/development/` pipeline (this
  is expected and correct for a *prospective* freeze — a reportable campaign
  is generated only after a freeze tag is cut, not before).
- The historical `--final-v2`/`--final-v3` tooling bug described above
  remains unfixed by design (task instruction: do not modify historical
  checkers/manifests). It is fully explained and does not block this
  proposal, but a reviewer relying on `make ieee-check` (the historical
  target) will still see it fail at its stage 5/8 — `make ieee-check-v4`
  (new, prospective-scoped) is the one that genuinely passes end to end.

## Explicit non-actions (per task instruction)

- No `git tag` has been run.
- No commit has been made.
- No manuscript file has been edited.
- No Zenodo interaction has occurred.
- No historical tag has been moved, rewritten, or deleted.
