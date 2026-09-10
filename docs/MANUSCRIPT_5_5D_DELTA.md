# MANUSCRIPT_5_5D_DELTA.md

**⚠️ STATUS NOTICE (2026-09-10)**

**The 9-ACS expansion described in Section 1 has been SUPERSEDED by forensic audit findings.**

The 9-ACS requirement cannot be justified from manuscript material. Case B contains **6 semantically distinct Approved Control Specifications** (one per risk), not 9.

See:
- `CASE_B_ACS_CARDINALITY_CORRECTION.md` (corrected specification)
- `CASE_B_9_ACS_SEMANTIC_PROVENANCE.md` (audit findings)  
- `NINE_ACS_CORRECTION_TRACE.md` (reference audit)

This document is retained as a **HISTORICAL RECORD** of the rejected proposal.

---

**Scope:** Complete delta audit between previous artifact (v1.0.3, manuscript aligned to Tier0-v2.2 freeze) and authoritative 5.5d manuscript state.

**Audit date:** 2026-09-10  
**Authority:** Explicit 5.5d requirements provided; manuscript source `/Users/sukhmangill/Desktop/paper3\ doc/files\ (73)/From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx` (Sept 9, 2026)

---

## SECTION 1: CASE B — APPROVED CONTROL SPECIFICATIONS (ACS) CARDINALITY

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

**Current state:**
- Case B contains **6 ACS records** in 1:1 mapping with 6 risks
- File: `cases/case_b/acs/approved_control_specifications.json`
- ACS mapping:
  - ACS-B01-01 → risk B-01 (permit binding)
  - ACS-B02-01 → risk B-02 (amount limit)
  - ACS-B03-01 → risk B-03 (velocity bound)
  - ACS-B04-01 → risk B-04 (restricted party screening)
  - ACS-B05-01 → risk B-05 (permit single-use)
  - ACS-B06-01 → risk B-06 (receipt chain)
- Total compiled predicates: **6 risk-derived predicates**
- P_B_risk = 6

### New 5.5d requirement

**Normative from 5.5d:**
- Case B must contain **9 Approved Control Specifications**
- Distribution:
  - B-01: 3 ACS
  - B-02: 2 ACS
  - B-03: 1 ACS
  - B-04: 1 ACS
  - B-05: 1 ACS
  - B-06: 1 ACS
  - **Total = 9 ACS**

**Normative:**
- Every runtime ACS must emit at least one predicate
- Therefore: **P_B_risk >= 9** (if every ACS compiles to 1 predicate minimum)

### Code/artifact affected

- `cases/case_b/acs/approved_control_specifications.json` — must expand from 6 to 9 records
- `src/gcir/compiler.py` — must handle N:1 risk:ACS mapping (not just 1:1)
- `cases/case_b/judgment/judgment_record.json` — must mark all 9 ACS as approved
- `cases/case_b/dispositions/dispositions.json` — dispositions reference ACS; must be updated if changed
- Case B compilation output: canonical payload hash **will change**
- Case B canonical bundle SHA-256 **will change** (in expected/reference_hashes.json)

### Experiments affected

- GC-IR bundle compilation
- All case_b results files
- Reference hash verification
- Manifest entries
- CI/CD reproducibility checks

### Manuscript result affected

- Case B predicate counts in all tables
- P_B_risk value
- Bundle hash in Section X
- Any prose claiming "six" controls or "six Case B predicates"

---

## SECTION 2: AUDIT QUERIES — EXPANSION FROM 6 TO 10

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

**Current state:**
- Queries file: `queries/traceability.sql`
- **6 queries defined:** Q1, Q2, Q3, Q4, Q5, Q6
- Scope per manuscript Section VIII:
  - Q1: Obligations without approved disposition
  - Q2: Risks without exactly one disposition
  - Q3: Orphan predicates (no risk/invariant origin)
  - Q4: Receipts not valid at decision time
  - Q5: Actuation without temporally prior receipt
  - Q6: Lifecycle-registry without valid signing authority

**Expected behavior:**
- All 6 queries return **empty sets** on valid Case A and Case B evidence stores

### New 5.5d requirement

**Normative from 5.5d:**
- Manuscript now defines **10 audit queries**
- All 10 queries must be **explicitly identified** in code (Q1...Q10)
- **For BOTH Case A and Case B valid evidence stores:** All 10 queries must return empty sets

### Code/artifact affected

- `queries/traceability.sql` — must be expanded to 10 queries (currently 6)
- `src/gcir/traceability.py` — source-of-truth query logic; must extend to Q7, Q8, Q9, Q10
- Query IDs and descriptions must be clear and distinct
- Tests must verify all 10 return empty on valid evidence

### Specification gap

The **exact definition of Q7, Q8, Q9, Q10 must come from the 5.5d manuscript itself**. Current audit:
- Manuscript text extracted mentions "ten audit queries" but does not enumerate all 10 names/definitions in extracted form
- **ACTION:** Read complete 5.5d manuscript Section VIII or section defining audit validation to extract exact Q7-Q10 definitions

### Experiments affected

- `experiments/run_audit_queries.py` (if exists)
- All query-result files
- Query coverage metrics
- Traceability verification in final_v3 results

### Manuscript result affected

- Section VIII figure/table showing audit queries will expand
- Any metrics showing "6 audit controls" must become "10"
- Negative-control fixture results (see Section 3 below)

---

## SECTION 3: AUDIT QUERY NEGATIVE FIXTURES — NEW REQUIREMENT

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

**Current state:**
- Audit queries exist in `queries/traceability.sql`
- Tests verify queries return empty on **valid** evidence stores
- No explicit **negative fixtures** (deliberately corrupted evidence)
- No seeded-violation detection tests

### New 5.5d requirement

**Normative from 5.5d:**
- For **each of Q1...Q10**, create at least one deliberately corrupted fixture
- Corruption must instantiate the **target violation** (the exact thing Q_i detects)
- Minimal mutation: alter only what is necessary to trigger the violation
- **Expected:** 10/10 seeded violations **detected** (query returns non-empty)
- Preferably for each relevant case (A and/or B) where meaningful

### Code/artifact affected

- New directory/structure: `cases/negative_fixtures/` or `queries/negative_fixtures/`
- Must contain 10+ fixture files (one per query, possibly per case)
- Fixture structure:
  - obligation, risk, disposition, predicate, receipt, actuation, lifecycle data
  - Exactly one violation seeded per fixture
  - Expected query result specified
- Test suite: `tests/integration/test_audit_query_negative_fixtures.py` (new)

### Example structure

```
cases/case_a/negative_fixtures/
  Q1_obligation_unresolved/
    evidence_store.json (with Q1 violation)
    expected_query_result.json (non-empty)
  Q2_dual_disposition/
    evidence_store.json (with Q2 violation)
    expected_query_result.json (non-empty)
  ...

cases/case_b/negative_fixtures/
  Q1_obligation_unresolved/
    ...
  ...
```

### Experiments affected

- New experiment: `experiments/run_audit_query_negative_controls.py`
- Result file: `results/final_v3/audit_query_negative_controls.json`

### Manuscript result affected

- Section VIII or new subsection showing negative-control detection results
- Quantitative: "10/10 seeded violations detected" or detailed breakdown per case

---

## SECTION 4: CASE B INJECTION SCENARIOS — EXACT EXPECTED OUTCOMES

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

**Current state:**
- 13 Case B injection scenarios exist (test them to confirm exact count)
- Each scenario tests a specific risk condition or control disruption
- Old test result: **13/13 → SAFE_STATE** (generic safe outcome)
- No distinction between DENY, HOLD, issuance rejection, compilation rejection, etc.
- `externalization = false` (unstated, implicit)

### New 5.5d requirement

**Normative from 5.5d:**
- Each of the 13 Case B injection scenarios must assert its **exact expected semantic outcome** from the manuscript:
  - **DENY** (explicit rejection at runtime evaluation)
  - **HOLD** (explicit escalation/deferral with no decision)
  - **Issuance rejection** (refusal at permit/ACS issuance time)
  - **Compilation rejection** (refusal at Φ compilation stage)
  - **Or another explicitly defined final outcome** (if other states exist in manuscript)
- Each scenario must also assert:
  - `externalization = false` (no externalization allowed under any outcome)
  - Manuscript section or clause supporting the expected outcome

### Code/artifact affected

- New file: `cases/case_b/injections/expected_outcomes.json`
- Schema:
  ```json
  {
    "scenarios": [
      {
        "scenario_id": "INTEST_B01_001",
        "injected_condition": "permit_signature_invalid",
        "expected_stage": "runtime_evaluation",
        "expected_decision": "DENY",
        "expected_reason_code": "RC-01",
        "expected_externalization": false,
        "manuscript_basis": "Section VII-A, constraint that permit binding must be verified",
        "notes": "ACS-B01-01 context condition fails; decision gate forced to SAFE_STATE/DENY"
      },
      ...
    ]
  }
  ```
- Tests: `tests/integration/test_case_b_injection_outcomes.py`
  - Each scenario must **assert exact outcome**, not collapse DENY and HOLD as equivalent
  - Failure if scenario expected to HOLD returns DENY
  - Failure if scenario expected to DENY returns HOLD

### Experiments affected

- New experiment: `experiments/run_case_b_injection_scenarios.py` (enhanced)
- Result file: `results/final_v3/case_b_injection_outcomes.json`

### Manuscript result affected

- Section X table or new subsection: "Case B Injection Test Results"
- Breakdown: DENY count, HOLD count, issuance rejection count, compilation rejection count
- Not: generic "13/13 safe"

---

## SECTION 5: MONTE CARLO MODEL — NO REDESIGN REQUIRED

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

- Monte Carlo based on six register rows (B-01 through B-06)
- Author-specified ±1 ordinal perturbation model
- K = 250,000 draws
- Seed: 4242 (pinned)
- Distributions defined in `preregistration/monte_carlo_distributions_v1.json`

### New 5.5d directive

**From requirements:**
- "DO NOT redesign the Monte Carlo model"
- "DO NOT change the seed"
- ACS cardinality change "does not obviously require a new Monte Carlo model"
- **ACTION:** Rerun Monte Carlo during final_v3 campaign to demonstrate values remain stable

### Code/artifact affected

- Monte Carlo code: **no change** to distributions or seed
- Re-execution: same K=250,000, same seed=4242
- Result comparison: final_v2 vs final_v3 to check stability

### Experiments affected

- `experiments/run_monte_carlo.py` — unchanged, rerun only
- `results/final_v3/monte_carlo_summary.json` — new results

### Manuscript result affected

- If Monte Carlo results change unexpectedly: investigate root cause before manuscript
- If results remain stable: state "Monte Carlo results remain stable under ACS cardinality correction"

---

## SECTION 6: CASE C — NOT AN EXECUTION TARGET

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

- Case C not compiled as part of the artifact campaign
- Case C GD values are deterministic register-level recomputations (Section X, Proposition 3)
- Not part of executable Φ

### New 5.5d directive

**From requirements:**
- "Do NOT invent or compile a Case C artifact merely because 5.5d contains a design Case C"
- Manuscript treats Case C as a fully specified design/register-level case
- GD values are deterministic recomputations, not compiled-artifact measurements
- **Unless the actual 5.5d manuscript explicitly requires executable Case C compilation, leave Case C outside Φ's empirical campaign**
- Document this distinction

### Code/artifact affected

- No new Case C compilation code
- Documentation: `docs/CASE_C_DESIGN_STATUS.md` (create if not present)
- Statement: Case C remains a design/theoretical case, not an execution artifact

---

## SECTION 7: SCIENTIFIC FREEZE — NEW TAG REQUIRED

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

- Governed by: `preregister-tier0-v2.2` (public tag, immutable)
- Manifest: `preregistration/FREEZE_MANIFEST_V2.sha256`

### New 5.5d requirement

**Normative:**
- Create new prospective scientific freeze (before executing final_v3 campaign)
- Old v2.2 remains untouched and historical
- **New tag:** `preregister-tier0-v3` (or appropriate unused version if repo history differs)
- **New freeze documentation:** `preregistration/TIER0_FREEZE_V3.md`
- **New manifest:** `preregistration/FREEZE_MANIFEST_V3.sha256`
- **New freeze must include:**
  - Schema (v1.0, unchanged)
  - Compiler source (updated for N:1 ACS)
  - Case A inputs (may be unchanged)
  - **Corrected Case B inputs with 9 ACS**
  - Judgment records (all 9 ACS approved)
  - All 10 audit query definitions
  - 10 negative-query fixtures
  - 13 exact-outcome injection expectations
  - Determinism matrix, test suites, Monte Carlo distributions (unchanged)
  - Analysis code, metrics definitions, paper-result definitions

### Code/artifact affected

- `preregistration/TIER0_FREEZE_V3.md` (new)
- `preregistration/FREEZE_MANIFEST_V3.sha256` (new)
- Freeze git tag: `preregister-tier0-v3`
- Updated: `src/gcir/freeze_check.py` to support `--final-v3` verification

### Experiments affected

- `experiments/run_freeze_verification.py` must support both v2.2 and v3

### Manuscript result affected

- v3 freeze tag in methodology / data availability statement
- v3 freeze manifest hash in preregistration section

---

## SECTION 8: NEW FINAL CAMPAIGN (final_v3)

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

- Results directory: `results/final_v2/`
- Results generated after public v2.2 freeze
- Executed on pinned Case A and Case B artifacts

### New 5.5d requirement

**After public v3 freeze exists (tagged remotely):**
- Execute complete reportable campaign from frozen v3 commit
- **New results directory:** `results/final_v3/` (do not overwrite final_v2)
- Run complete pipeline:
  1. Case A compilation (31 runs, stratified)
  2. **Case B compilation with 9 ACS** (31 runs, stratified)
  3. Primary metrics
  4. All 10 audit queries per valid case
  5. All 10 negative audit-query fixtures
  6. 13 exact Case B injection outcome tests
  7. Adversarial suite
  8. Structural tests
  9. Property tests
  10. Determinism (62 total runs: 31 per case, across locales/timezones/shuffles)
  11. Gate-divergence calculations
  12. Monte Carlo (K=250,000, seed=4242)
  13. Freeze verification
  14. Manifest generation
  15. Result-provenance generation

### Determinism requirement (final_v3)

- **Case A:** 31 executions (same as v2 if inputs unchanged)
- **Case B:** 31 executions (new, with 9 ACS)
- **Total:** 62 runs
- Stratification: 10 repeats, 10 row shuffles, 5 key shuffles, 3 locales, 3 timezones
- **Success criterion:** TD = 1.000 over the new 62-run campaign
- Case A reference hash: may remain unchanged (if scientific inputs unchanged)
- **Case B reference hash:** will likely change (new ACS set)
- Report: actual TD result and 62-run breakdown if != 1.000

### Cross-platform requirement (final_v3)

- Rerun determinism testing on tested supported environments:
  - macOS arm64
  - Linux x86_64
  - Windows AMD64
  - Pinned container (Linux/aarch64)
- All environments must reproduce new Case A and Case B reference hashes
- Claim: "deterministic across the tested supported environments" (not universally platform-independent)

### Docker requirement (final_v3)

- Rerun clean pinned-container reproduction
- Must reproduce new Case B hash and final metrics

### Code/artifact affected

- `results/final_v3/` (new directory, full parallel of final_v2 structure)
- `src/gcir/compiler.py` (Case B with 9 ACS)
- All metrics calculation code
- All query execution code
- Freeze check: `src/gcir/freeze_check.py` supporting `--final-v3`
- CI/CD: add `final_v3` to build matrix

---

## SECTION 9: PAPER RESULT MAP REGENERATION

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

- Paper result map: `artifact_review/PAPER_RESULT_MAP.json`
- Maps 48 claims / 22 cross-checks to Case A/B artifacts
- Verifier: `tools/verify_reported_results.py`

### New 5.5d requirement

**Normative:**
- Rebuild paper-facing result map from **actual 5.5d manuscript claims**
- Do not preserve arbitrary count of 48
- For each empirical 5.5d claim map to:
  - Input file
  - Experiment name
  - Result file path
  - Field/value within result
  - Expected value from manuscript
  - Claim boundary (what it does and does not claim)

### Code/artifact affected

- `artifact_review/PAPER_RESULT_MAP.json` (regenerated)
- `artifact_review/PAPER_TO_ARTIFACT_RESULTS.md` (regenerated)
- Verifier runs: `tools/verify_reported_results.py` against final_v3 outputs
- Actual count of verified claims may increase or decrease

### Experiments affected

- `experiments/run_paper_result_verification.py` (if exists)

### Manuscript result affected

- Section XI metrics table alignment with final_v3 results
- Any claims with changed numerical values

---

## SECTION 10: MAKE RESULTS / README UPDATE

### Old artifact assumption (v1.0.3 / Tier0-v2.2)

```bash
make results
```
- Shows: results/final_v2/ as reportable campaign
- Shows: preregister-tier0-v2.2 as frozen version
- Displays old Case B: 6 ACS, P_B_risk = 6, old hash

### New 5.5d requirement

**After final_v3 exists:**
```bash
make results
```
- Shows: results/final_v3/ as reportable campaign (primary)
- Shows: preregister-tier0-v3 as scientific freeze
- Displays new Case B: 9 ACS, actual P_B_risk, new bundle SHA-256
- Includes all new final metrics
- Audit queries: "Case A 10/10 empty, Case B 10/10 empty"
- Negative controls: "10/10 detected"
- Case B injections: breakdown by DENY / HOLD / issuance rejection / etc. (not generic "SAFE_STATE")
- Test counts: new frozen final_v3 count, current reviewer-package count if different

### Code/artifact affected

- `Makefile` target `results`
- `tools/show_results.py` (enhanced)
- `README.md` measured-results section (regenerated from final_v3)

### Manuscript result affected

- README must never display old Case B hash as current
- README measured results section automatically regenerated

---

## SECTION 11: PREVIOUS MANUSCRIPT FIXES — PRESERVATION

### Constraints (R-04, R-07, references, claim boundaries, RQ5)

These previously corrected items must **NOT regress** while rebuilding for 5.5d:

| Fix | Item | Location |
|-----|------|----------|
| R-04 | Implementation-vs-spec determinism limitation | Section XII, manuscript text |
| R-07 | Overlapping-author disclosure for [15]-[17] | Section XIII opening |
| Ref corrections | [21]/[22] verification | `paper_update/REFERENCES_21_22_VERIFICATION.md` |
| Claim boundaries | RQ5 deferral | Sections XI-G, XI-H, XV |
| | Case A synthetic disclosure | Section IX |
| | Case B forensic reconstruction | Section X |
| | Author-specified Monte Carlo disclosure | Section XI-G |

**Action:** During manuscript reconciliation for 5.5d, preserve all these corrections. Do not regress.

---

## SECTION 12: RELEASE v1.0.4

### Old artifact (v1.0.3)

- Public and immutable
- Tied to Tier0-v2.2 freeze
- Case B: 6 ACS, hash 2850155a2ee7...

### New 5.5d requirement

**After:**
- Public v3 freeze tag verified on GitHub
- final_v3 campaign complete
- Manuscript updated with 5.5d values
- Local verification green
- Docker reproduction green
- CI tag tests green

**Publish:**
- Release tag: **v1.0.4**
- Description: NOT packaging-only
  ```
  v1.0.4 aligns the executable artifact with manuscript 5.5d by compiling all
  nine Case B ACSs, expanding audit validation to ten queries with seeded
  negative controls, and asserting exact Case B DENY/HOLD injection semantics.
  The artifact was re-frozen prospectively under preregister-tier0-v3 and the
  complete determinism, CI, Docker and result-verification pipeline was rerun.
  ```
- Do not call v1.0.4 cosmetic

### Code/artifact affected

- GitHub release page: v1.0.4
- Tag: v1.0.4 on commit after final_v3 results

### CI/CD requirement

After v1.0.4 publication:
- Tag-triggered CI must pass
- Tests, cross-platform determinism, reproducibility
- Record real workflow IDs

---

## SECTION 13: ZENODO DEPOSIT

### Old artifact

- v1.0.3 released Sept 9
- Do NOT deposit v1.0.3 as the final 5.5d artifact

### New 5.5d requirement

**After v1.0.4 exists and passes tag CI:**
- Download/clone exact v1.0.4 release artifact
- Run reviewer commands:
  - `make install`
  - `make results`
  - `make test`
  - `make verify-hashes`
  - `python tools/freeze_check.py --final-v3`
  - `python tools/verify_reported_results.py`
  - `make verify-readme-results`
  - `make ieee-check`
  - Docker reproduction
- All must use new final_v3 evidence
- Once verified, deposit exact v1.0.4 tarball on Zenodo
- Do not invent DOI; use Zenodo-assigned DOI

---

## SECTION 14: SUMMARY OF CHANGES BY ARTIFACT COMPONENT

| Component | Current | 5.5d Required | Status |
|-----------|---------|---------------|--------|
| Case B ACS count | 6 | 9 | Expand required |
| P_B_risk | 6 | >= 9 | Recompile after expansion |
| Audit queries (Q1..Qn) | 6 | 10 | Expand required |
| Negative fixtures | None | 10+ | Create required |
| Injection scenario outcomes | Generic SAFE_STATE | Exact DENY/HOLD/etc. | Specify required |
| Scientific freeze tag | preregister-tier0-v2.2 | preregister-tier0-v3 | Create required |
| Results directory | results/final_v2 | results/final_v3 | Generate required |
| Case A compilation | 31 runs | 31 runs | Rerun (may be unchanged) |
| Case B compilation | 31 runs | 31 runs | Rerun (new ACS set) |
| Determinism runs (total) | 31 | 62 (31 per case) | Stratified rerun |
| TD target | 1.000 | 1.000 over 62 | Verify |
| Cross-platform matrix | 8 environments | Same matrix | Rerun verification |
| Monte Carlo | K=250,000, seed=4242 | Same (rerun) | Stability verification |
| Case C | Design only | Design only (unchanged) | No compilation |
| Release | v1.0.2 | v1.0.4 | Create |
| Zenodo | v1.0.3 | v1.0.4 | Deposit after tag CI |

---

## FINAL AUDIT SIGN-OFF

**Phase 0 audit status:** COMPLETE

All 5.5d requirements have been documented and mapped to code/artifact locations. The delta is substantial but not architectural:
- Case B ACS cardinality expands 6 → 9 (data structure change, not schema change)
- Audit queries expand 6 → 10 (new queries, same verification structure)
- Injection semantics specified exactly (test specification, not code change)
- New freeze/campaign/release follow existing patterns

**Ready for Phase 1:** Development changes

