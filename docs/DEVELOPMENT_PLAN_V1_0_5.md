# Development Plan: v1.0.5 Scientific Correction

**Objective:** Bring implementation, tests, results, and manuscript into strict scientific agreement.

**Timeline:** Development on main branch → test locally → new freeze → reportable campaign → v1.0.5 release.

---

## PHASE 1: Code Implementation (Development Commits)

### 1.1 PERMIT/DENY/HOLD Semantics
**Status:** Implementation prepared (in stash), needs integration
**Actions:**
- [ ] Apply stashed PERMIT/DENY/HOLD implementation
- [ ] Add _classify_exact_outcome() helper
- [ ] Verify safe_state = (decision != "PERMIT") holds
- [ ] Commit: "Implement PERMIT/DENY/HOLD exact decision semantics"

### 1.2 Canonical Q1-Q10 Queries  
**Status:** Partial (Q7-Q10 exists), needs Q1-Q6
**Actions:**
- [ ] Implement Q1: Obligation disposition completeness
- [ ] Implement Q2: Exactly-one disposition per risk
- [ ] Implement Q3: Predicate origin closure
- [ ] Implement Q4: Temporal bundle/receipt validity (structural check)
- [ ] Implement Q5: Commit-before-actuation ordering (structural check)
- [ ] Implement Q6: Lifecycle signing authority
- [ ] Verify Q7-Q10 use origin.origin_type (nested) not origin_type (flat)
- [ ] Commit: "Implement canonical Q1-Q10 audit queries"

### 1.3 Injection Test Assertions
**Status:** Tests exist but check SAFE_STATE only
**Actions:**
- [ ] Update experiments/case_b_injection_scenarios.py
- [ ] Change assertion from `decision == "SAFE_STATE"` to exact expected outcome
- [ ] Map 4 scenarios → HOLD (with escalation checks)
- [ ] Map 9 scenarios → DENY (known failure)
- [ ] Verify all 13 scenarios assert exact decision
- [ ] Commit: "Update injection tests to verify exact HOLD/DENY outcomes"

### 1.4 Negative Fixtures
**Status:** Exists, verify it detects violations
**Actions:**
- [ ] Verify all 10 negative fixtures still produce Q1-Q10 violations
- [ ] If Q-definitions change, update fixtures accordingly
- [ ] Commit: "Verify negative fixtures against canonical Q1-Q10"

---

## PHASE 2: Local Verification (Development Branch)

### 2.1 Code-Level Tests
**Actions:**
- [ ] `make test` → expect 320/320 or report actual count
- [ ] Unit tests for all Q1-Q10 implementations
- [ ] Negative fixture verification
- [ ] Injection scenario exact-outcome assertions
- [ ] All must PASS before proceeding

### 2.2 Compilation Verification
**Actions:**
- [ ] `python -m experiments.verify_hashes`
- [ ] Case A: expect f5cbc3a8... or document reason for change
- [ ] Case B: expect 2850155a... or document reason for change
- [ ] If hashes changed, update reference_hashes.json files

### 2.3 Audit Query Execution
**Actions:**
- [ ] Run Q1-Q10 on Case A → expect 10/10 PASS
- [ ] Run Q1-Q10 on Case B → expect 10/10 PASS
- [ ] Run 10 negative fixtures → expect all violations detected
- [ ] Report actual counts in results

### 2.4 Exact Injection Execution
**Actions:**
- [ ] Run 13 injection scenarios with new exact-outcome assertions
- [ ] Verify: 4 HOLD outcomes
- [ ] Verify: 9 DENY outcomes
- [ ] Verify: zero externalization in all 13
- [ ] Verify: all clean controls PERMIT

### 2.5 Determinism Check (62 runs)
**Actions:**
- [ ] `python -m experiments.run_determinism --dev`
- [ ] Expect TD = 1.0 (all 62 runs identical)
- [ ] Document any environment variations

### 2.6 Full Development Campaign
**Actions:**
- [ ] Run everything under results/development_v3_prefreeze/
- [ ] Verify all outputs are machine-generated (no hand edits)
- [ ] Fix any test failures before proceeding to freeze

---

## PHASE 3: Scientific Freeze (preregister-tier0-v3.1)

### 3.1 Create Freeze Tag
**Actions:**
- [ ] Commit all Phase 1 implementations with message "Phase 1 development complete"
- [ ] Create annotated tag: `preregister-tier0-v3.1`
- [ ] Freeze commit must contain:
  - [ ] PERMIT/DENY/HOLD resolver
  - [ ] Canonical Q1-Q10 implementations  
  - [ ] Exact injection test assertions
  - [ ] All negative fixtures
  - [ ] Dependency pins
  - [ ] Docker environment
  - [ ] Schemas and cases
  
### 3.2 Public Verification
**Actions:**
- [ ] `git push origin preregister-tier0-v3.1`
- [ ] `git ls-remote --tags origin preregister-tier0-v3.1` → verify public
- [ ] Record freeze commit hash for campaign provenance

---

## PHASE 4: Reportable Campaign (From Frozen Commit)

### 4.1 Clean Environment
**Actions:**
- [ ] Fresh clone from preregister-tier0-v3.1 tag OR
- [ ] `git checkout preregister-tier0-v3.1` in clean worktree
- [ ] `make install` in clean environment

### 4.2 Campaign Execution
**Actions:**
- [ ] Run all experiments
- [ ] Write to results/final_v3_1/
- [ ] Do NOT touch results/final_v3/ or results/final_v2/
- [ ] Generate:
  - [ ] campaign_results.json (all metrics)
  - [ ] REPORTABLE_CAMPAIGN_RESULTS.md (prose)
  - [ ] determinism_summary.json (62-run results)
  - [ ] determinism_runs.csv (run matrix)
  - [ ] monte_carlo summary & per-risk output
  - [ ] Q1-Q10 results (both cases)
  - [ ] negative fixture results
  - [ ] 13-injection exact outcomes
  - [ ] test report (actual count)
  - [ ] freeze verification
  - [ ] environment/provenance

### 4.3 Campaign Metrics (from actual execution)
**Actions:**
- [ ] Record Case A: hash, test count
- [ ] Record Case B: hash, ACS count, predicate counts
- [ ] Record: Q1-Q10 results (actual totals)
- [ ] Record: negative fixture results (actual count detected)
- [ ] Record: 13-injection outcomes (verify 4 HOLD, 9 DENY if unchanged)
- [ ] Record: test suite actual count
- [ ] Record: TD (expect 1.0)
- [ ] Record: Monte Carlo actual values
- [ ] Record: Monte Carlo Case B max FP_heat (expect ~0.317980 if unchanged)

### 4.4 CI Verification
**Actions:**
- [ ] All GitHub Actions must pass for v1.0.5 tag
- [ ] tests workflow: PASS ✓
- [ ] cross-platform determinism: PASS ✓
- [ ] reproducibility: PASS ✓

---

## PHASE 5: Manuscript Update

### 5.1 Open Source & Update
**Actions:**
- [ ] New file: `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION_5_5f.docx`
- [ ] Find source file (not PDF)

### 5.2 Update Results Tables
**Actions:**
- [ ] Table II (Case B): update from actual artifact
  - [ ] 6 risks ✓
  - [ ] 6 ACS
  - [ ] 6 risk-derived predicates
  - [ ] 3 compiler-invariant predicates
  - [ ] 9 total predicates
  - [ ] Remove any fictional identifiers
  
- [ ] Table III (Metrics): update from final_v3_1
  - [ ] Case A/B DC, RCY, NDR, OPR, ODC, PTC, CV, GD
  - [ ] Use actual values from campaign
  
- [ ] Q7-Q10 results: update to canonical definitions & actual results
  - [ ] Rewrite Appendix A with new Q1-Q10
  - [ ] Move revocation/safety/delegation checks to auxiliary if retained
  
- [ ] SAFE_STATE definition: only as aggregate property
  - [ ] safe_state = (decision != "PERMIT")
  - [ ] Not a peer decision alongside PERMIT/DENY/HOLD

### 5.3 Update Results & Metrics
**Actions:**
- [ ] Monte Carlo Case A: actual exact values
- [ ] Monte Carlo Case B: use actual final_v3_1 (not 0.000000)
- [ ] Case A MCSE: fix rounding if needed
- [ ] Test count: use actual final_v3_1 count (not forced to 320)
- [ ] TD: state 1.000 (or actual if changed)
- [ ] All machine-generated, traced to results/final_v3_1/

### 5.4 Update Release Info
**Actions:**
- [ ] Change all references from v1.0.3/preregister-tier0-v2.2 to v1.0.5/preregister-tier0-v3.1
- [ ] Fix freeze commit hash
- [ ] Remove all XXXXXXXX placeholders
- [ ] For Zenodo DOI: state "DOI will be inserted after deposit" (do not invent)
- [ ] Add explicit transparency statement about v1.0.4 error and v1.0.5 correction

### 5.5 Manuscript Verification
**Actions:**
- [ ] tools/verify_reported_results.py → all quantities match
- [ ] PDF export for final submission

---

## PHASE 6: Release v1.0.5

### 6.1 Tag & Release
**Actions:**
- [ ] Create annotated tag: `v1.0.5`
- [ ] Release notes must state:
  - [ ] v1.0.4 had code/result mismatch
  - [ ] v1.0.5 is the corrected, verified, fully green release
  - [ ] Implements PERMIT/DENY/HOLD exact semantics
  - [ ] Canonical Q1-Q10 implemented and verified
  - [ ] All CI workflows green
  - [ ] Reportable campaign from frozen commit
  
- [ ] Push: `git push origin v1.0.5`

### 6.2 CI Verification  
**Actions:**
- [ ] Wait for all v1.0.5 workflows to complete
- [ ] Verify GREEN:
  - [ ] tests
  - [ ] cross-platform determinism
  - [ ] reproducibility
  - [ ] Docker

### 6.3 Final Verification
**Actions:**
- [ ] Fresh clone of v1.0.5 tag
- [ ] `make install && make results` → works
- [ ] `make test` → all pass
- [ ] `python tools/freeze_check.py --final-v3_1` → all pass
- [ ] `python tools/verify_reported_results.py` → all match

---

## PHASE 7: Zenodo Readiness (NOT YET DEPOSIT)

### 7.1 Prepare Submission Package
**Actions:**
- [ ] v1.0.5 release tarball
- [ ] SHA-256 of tarball
- [ ] Manuscript PDF (5.5f)
- [ ] Manifest/checksum file
- [ ] Container digest (if applicable)

### 7.2 Verify Submission Metadata
**Actions:**
- [ ] Authors: correct ✓
- [ ] Title: correct ✓
- [ ] Abstract: references v1.0.5, preregister-tier0-v3.1 ✓
- [ ] Release URL: ready ✓
- [ ] License: declared ✓
- [ ] Supplementary materials: listed ✓

### 7.3 DO NOT DEPOSIT YET
**Actions:**
- [ ] Stop before Zenodo deposit
- [ ] Generate summary for final approval
- [ ] Await explicit approval before DOI assignment

---

## Success Criteria

- [ ] All code implementation complete & tested locally
- [ ] Freeze tag created and public on GitHub
- [ ] Reportable campaign complete and verified
- [ ] All campaign results match expectations OR documented differences explained
- [ ] Manuscript updated from machine-generated results
- [ ] All stale references removed
- [ ] All CI workflows pass for v1.0.5
- [ ] Final verification passes from clean clone
- [ ] Zero placeholders (XXXXXXXX) remaining

---

## Timeline Estimate

- Phase 1-2 (Implementation & Local Testing): 2-4 hours
- Phase 3 (Freeze): 30 minutes  
- Phase 4 (Campaign): 1-2 hours
- Phase 5 (Manuscript): 1-2 hours
- Phase 6 (Release & CI): 30 minutes - 1 hour
- Phase 7 (Readiness prep): 30 minutes
- **Total: 6-10 hours**

