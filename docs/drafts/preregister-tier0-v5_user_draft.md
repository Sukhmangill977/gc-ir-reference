# Paper 2 — Tier-0 Preregistration
## `preregister-tier0-v5`

**Protocol version:** Paper 2 v1.2  
**Campaign tier:** Tier-0 / reportable empirical campaign  
**Proposed repository tag:** `preregister-tier0-v5`  
**Status:** Preregistered protocol; results must be generated prospectively and must not be edited to satisfy expected outcomes.

---

## 1. Purpose

This preregistration defines the empirical validation campaign for Paper 2 v1.2.

The primary empirical question is:

> Can the translation validator distinguish an authorized translation from a controlled unauthorized semantic change while preserving the authorized translation contract before the existing L-DREA execution boundary?

The campaign tests semantic preservation, rejection of controlled semantic violations, contract validation, determinism, cross-environment reproducibility, gate-deficit behavior, Monte Carlo behavior, compile timing, and downstream integration.

The campaign is intended to produce machine-readable evidence that can be independently rerun from a clean repository state.

---

## 2. Scope and non-goals

### In scope

1. Translation-contract preservation.
2. Controlled semantic-negative rejection.
3. Case-D governance/translation behavior.
4. Machine-checkable contract conjuncts.
5. Q1–Q10 regression/audit evidence.
6. Local determinism.
7. Cross-environment canonical-output reproducibility.
8. GD/GDmin computation.
9. Monte Carlo experiment.
10. Compile timing.
11. Observation diagnostics.
12. Case-B downstream runtime integration.
13. Full automated test suite.
14. Final freeze and manuscript-number verification.

### Explicit non-goal

The 284,807-row Case-B-v1.1 ULB replay is **not** a required primary experiment for this Tier-0 campaign when the corresponding controls do not have ULB linkage. It may be reported separately if a valid, pre-specified linkage is established without changing the protocol after seeing results.

---

## 3. Frozen primary surfaces

### 3.1 Surface A paired validation

Surface A contains eight nominal/negative paired artifact families.

Each family has:

- one authorized nominal artifact;
- one controlled semantic-negative artifact;
- valid syntax/package structure;
- legitimate hashes/signatures where applicable;
- exactly one intended semantic corruption in the negative artifact.

The eight families are:

| ID | Property |
|---|---|
| A1 | Origin/provenance preservation |
| A2 | Disposition / no-narrowing preservation |
| A3 | Class / role preservation |
| A4 | Action, parameter, scope / no-broadening preservation |
| A5 | Exception-scope preservation |
| A6 | Lifecycle/current-authority preservation |
| A7 | Evidence / observation-contract preservation |
| A8 | Unauthorized invention / no-invention |

Determinism is **not** one of the eight Surface-A semantic families; it is tested separately.

### Tier-0 success condition

- 8/8 nominal artifacts accepted.
- 8/8 semantic negatives rejected.
- 8/8 negatives fail for the intended semantic property.
- 0/8 failures caused only by malformed packaging.
- 0 unexpected semantic-negative acceptances.

---

## 4. Case-D matrix

The frozen Case-D matrix contains D1–D10.

| Case | Required behavior |
|---|---|
| D1 | Unresolved N4 causes compile failure through indeterminacy/materiality. |
| D2 | N4 is explicitly refused/residualized, emergency exception disabled, ordinary transfer path retained; CCS_0 compiles. |
| D3 | Ordinary transfer under CCS_0 with beneficiary >24h; no emergency prerequisite is imposed on the ordinary path. |
| D4 | Emergency-dependent transfer under CCS_0 is HOLD + escalation because the request is outside CCS_0 applicability scope. |
| D5 | Signed JD resolves the authorized officer to Treasury Officer; CCS_1 compiles with the conditional emergency branch. |
| D6 | CCS_1 exception branch checks emergency-officer validity/evidence only inside the branch; the requirement is not globalized. |
| D7 | N4 exception is widened into N3/general bypass; compile failure for no-broadening/exception-scope violation. |
| D8 | Mandatory residual/retention is dropped; compile failure for disposition/no-narrowing. |
| D9 | Policy 4.3 plus new J' changes emergency scope; a new canonical payload/hash is required and the old derivation is not current. |
| D10 | Semantically equivalent reordering of canonical source objects/keys produces the identical Phi_core hash. |

### Tier-0 success condition

10/10 cases satisfy their pre-specified expected status and contract property.

---

## 5. Contract-validator suite

Every machine-checkable contract conjunct must have at least:

- one positive fixture; and
- one isolated negative fixture.

A negative fixture must change one semantic property at a time and must not fail merely because of malformed packaging unless packaging validity is itself the property being tested.

The v1.2 contract includes, as applicable to the implementation:

1. origin/provenance;
2. disposition/no-narrowing;
3. class/role preservation;
4. action/parameter/scope/no-broadening;
5. exception scope;
6. lifecycle/current authority;
7. evidence/observation;
8. unauthorized invention/no-invention;
9. indeterminacy/materiality;
10. declared-path contract;
11. synchronization contract;
12. RC-04 timing assurance;
13. RC-06 wrong-layer/continuous-control routing.

RC-04 must represent the condition in which timing assurance is not established when a discrete transition could be gated but lacks the required timing evidence.

RC-06 remains a wrong-layer/continuous-control condition routed to the appropriate safety/RTA layer.

---

## 6. Regression and audit

Run the existing Q1–Q10 audit against the applicable current campaign artifacts.

Retain the historical seeded-negative fixture family.

Do not hard-code a historical denominator. The campaign must discover and report the actual number of fixtures present and evaluated.

Any failed or unavailable fixture must remain visible in the machine-readable results.

---

## 7. Local determinism

Run:

- Surface A;
- applicable Case-B/v1.1 inputs;
- Case D.

For each surface, perform 31 local runs:

- 10 repeated identical-input runs;
- 10 row-shuffle runs;
- 5 key-order-shuffle runs;
- 3 locale variations;
- 3 timezone variations.

Total:

**31 × 3 = 93 local determinism runs.**

The invariant is the canonical output / canonical payload identity required by the implementation.

The 93-run local campaign is reported separately from cross-environment reproducibility.

---

## 8. Cross-environment reproducibility

Evaluate the applicable A/B/D artifacts in these environments:

1. Linux x86-64, Python 3.11;
2. Linux x86-64, Python 3.12;
3. Windows AMD64, Python 3.11;
4. Windows AMD64, Python 3.12;
5. macOS ARM64, Python 3.11;
6. macOS ARM64, Python 3.12;
7. pinned Linux/aarch64 container;
8. frozen reference environment.

For each applicable case, compare canonical payload/hash output.

Cross-environment evidence is distinct from the 93 local determinism runs.

---

## 9. GD/GDmin

Use the repository's existing GD/GDmin definition and implementation.

Do not alter the formula to improve results.

Record:

- register/configuration version;
- input hashes;
- output values;
- relevant artifact hashes;
- implementation commit.

If an input or formula discrepancy is discovered, stop and preserve the discrepancy rather than silently replacing the frozen input.

---

## 10. Monte Carlo

Run the pre-specified Monte Carlo campaign with:

- **K = 250,000**
- **seed = 20260201**

Record:

- parameter/register configuration;
- input hashes;
- number of flips/events;
- estimated fraction/probability;
- Monte Carlo standard error where applicable;
- output hash;
- implementation commit.

If the repository implementation differs from this specification, report the actual implementation rather than fabricating conformity.

---

## 11. Compile timing

Measure compilation separately for A, B, and D.

For each:

- 10 warm-up runs;
- 100 measured runs.

Primary timing target:

> `T_core`: canonical signed source inputs → canonical CCS payload.

If an end-to-end measurement is available, it may additionally be reported as `T_e2e`, but it must not replace `T_core`.

Report per environment/case:

- n;
- median;
- p95;
- minimum;
- maximum;
- IQR;
- CPU/architecture;
- OS;
- Python version;
- dependency versions;
- case identifier;
- artifact size;
- input/output hashes.

Do not pool all environments into one universal latency number.

---

## 12. Observation diagnostics

Run the A/B observation diagnostics when implemented.

These are diagnostic evidence, not substitutes for the primary Surface-A or Case-D evidence.

They must be labelled as post-hoc/diagnostic where appropriate.

---

## 13. Case-B runtime integration

Run the downstream integration campaign consisting of:

- 13 adverse scenarios;
- 1 clean scenario.

This is integration evidence only.

For every row record:

- scenario ID;
- expected outcome;
- actual outcome;
- compiled artifact/hash;
- downstream evaluator result;
- pass/fail.

Do not treat downstream runtime integration as proof of the translation contract itself.

---

## 14. Full automated test suite

Run:

```bash
python -m pytest -q --junitxml=results/final_v5/pytest-junit.xml
```

Report the actual test count and failures from the generated output.

Do not state a historical denominator unless it is reproduced by the current run.

---

## 15. Manuscript-number verification

Run:

```bash
python tools/verify_manuscript_v1_2_0.py
```

Every numerical claim used in the manuscript must be checked against the machine-readable campaign results.

A mismatch is a campaign failure/blocker until resolved transparently.

---

## 16. Machine-readable campaign result

Produce:

```text
results/final_v5/campaign_results.json
```

At minimum include:

```json
{
  "protocol": "preregister-tier0-v5",
  "paper_version": "1.2",
  "status": "PASS|FAIL|BLOCKED",
  "repository_commit": "...",
  "timestamp_utc": "...",
  "surface_a": {},
  "case_d": {},
  "contract_validator": {},
  "audit_q1_q10": {},
  "case_b_integration": {},
  "determinism_local": {},
  "determinism_cross_environment": {},
  "gd_gdmin": {},
  "monte_carlo": {},
  "compile_timing": {},
  "observation_diagnostics": {},
  "tests": {},
  "freeze": {},
  "manuscript_verification": {}
}
```

Each experiment section must include actual denominators/numerators where applicable, expected/actual outcomes, artifact paths, hashes, commit, and timestamps.

---

## 17. Freeze procedure

Before the reportable run:

1. Freeze the protocol and expected fixtures.
2. Freeze scripts/fixtures/expected outcomes.
3. Create and verify a manifest.
4. Commit the frozen state.
5. Create the proposed tag:

```text
preregister-tier0-v5
```

6. Verify that the tag points to the intended commit.
7. If repository policy requires a remote tag, push and verify the remote reference.
8. Do not modify scientific-state files after the freeze except through explicitly documented correction procedures.

The clean reportable campaign must be run from the frozen commit/tag or an exact clean worktree at that commit.

---

## 18. Required reportable run order

1. Full pytest suite.
2. A compile.
3. B/v1.1 compile.
4. D compile.
5. Surface-A paired validation.
6. Case-D matrix.
7. Full contract-validator suite.
8. Q1–Q10 audit and seeded negatives.
9. Case-B 13+1 integration.
10. Local determinism, 93 runs.
11. GD/GDmin.
12. Monte Carlo.
13. Compile timing.
14. Observation diagnostics.
15. Cross-environment reproducibility.
16. Generate `campaign_results.json`.
17. Freeze verification.
18. Manuscript-number verification.

The order may be implemented by the repository runner provided that all required components and dependencies remain explicit.

---

## 19. Anti-fabrication and integrity rules

The campaign must never:

- invent a passing result;
- change a fixture after observing its result to obtain a pass;
- tune the validator against a failed negative;
- delete a failed run;
- overwrite frozen results without an explicit correction record;
- relabel a development run as a final run;
- relabel diagnostic evidence as primary evidence;
- claim a denominator that was not actually evaluated;
- silently replace an input, formula, or fixture;
- suppress a failure from the final machine-readable result.

If a run fails:

1. preserve the failure;
2. record the exact error;
3. identify whether it is implementation, fixture, environment, or protocol-related;
4. make any correction transparently;
5. rerun from a clean state where required;
6. retain the original failed evidence.

---

## 20. Final campaign status

The final machine-readable status may be:

- `PASS` only when every mandatory Tier-0 component is present and all frozen success conditions pass;
- `FAIL` when a required experiment runs but violates its frozen success condition;
- `BLOCKED` when a mandatory component cannot be validly evaluated.

Final summary must include:

- Surface A result;
- Case-D result;
- contract-validator result;
- Q1–Q10 audit result;
- local determinism: 93-run denominator;
- cross-environment result;
- GD/GDmin result;
- Monte Carlo result;
- timing result;
- test result;
- freeze result;
- manuscript verification result;
- final commit SHA;
- preregistration tag.

---

## 21. Reproducibility command

The repository should provide one documented entry point equivalent to:

```bash
python experiments/final_campaign_v12.py --final
```

The entry point must:

- refuse to call a campaign final if the worktree/tag state is inconsistent with the freeze;
- execute or dispatch every required experiment;
- preserve stdout/stderr and machine-readable artifacts;
- stop or mark the campaign appropriately on mandatory failures;
- write the final campaign result only from actual run outputs.

---

## 22. Protocol amendments

Any change made after the preregistration freeze must be recorded as an amendment containing:

- date/time;
- commit;
- original protocol text/behavior;
- changed behavior;
- reason;
- whether the change affects a primary outcome;
- whether previously generated results remain valid.

A post-result change must never be represented as if it had been part of the original preregistration.

---

**End of `preregister-tier0-v5`**
