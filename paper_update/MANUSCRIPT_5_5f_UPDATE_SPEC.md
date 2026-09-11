# Manuscript 5.5f Update Specification

**Source:** From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION_5_5f.docx  
**Results Source:** results/final_v3_1/  
**Freeze:** preregister-tier0-v3.1 (commit 158c0bd)  
**Release:** v1.0.5

---

## Critical Value Updates

### Case A
- **Hash:** `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` ✓ (unchanged)
- **Test Count:** 320/320 ✓ (unchanged)

### Case B  
- **Hash:** `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` ✓ (unchanged)
- **Structure:**
  - Risks: 6 ✓ (unchanged)
  - Runtime Dispositions: 6 ✓ (unchanged)
  - Approved Control Specifications: 6 ✓ (unchanged)
  - Risk-Derived Predicates: 6 ✓ (unchanged)
  - Compiler-Invariant Predicates: 3 ✓ (unchanged)
  - **Total Predicates: 9** ✓ (unchanged)

### Determinism
- **TD:** 1.000 ✓ (unchanged)
- **Runs:** 62/62 ✓ (unchanged)
- **Environments:** 3 operating systems, 2 architectures, 5 locales, 5 timezones ✓ (unchanged)

### Monte Carlo
| Case | Metric | Old Value | New Value | Source |
|------|--------|-----------|-----------|--------|
| Case A | max FP_heat | 0.321268 | 0.321268 | ✓ Verified |
| Case A | MCSE | 0.000934 | 0.000934 | ✓ Verified |
| Case B | max FP_heat | 0.317980 | 0.317980 | ✓ Verified |
| Case B | MCSE | 0.000931 | 0.000931 | ✓ Verified |

### Decision Semantics

**Update all references to SAFE_STATE in results context:**

Replace: "the bundle resolves to SAFE_STATE as indeterminate"  
With: "the bundle resolves to DENY (indeterminate fail-closed) with safe_state=true"

Replace: "resolved to SAFE_STATE"  
With: "resolved to DENY with safe_state=true, or HOLD (unknown+escalation) with safe_state=true"

**New exact decision definition to add to Section VI-D:**

> The precedence resolver returns exactly three decision classes:
> 
> - **PERMIT:** All mandatory conditions satisfied. safe_state = false.
> - **DENY:** Mandatory failure occurred (outcome="fail" OR outcome="unknown" with no escalation route). safe_state = true.
> - **HOLD:** Unknown evidence with valid escalation route exists. safe_state = true. Escalation details returned.
>
> The safe_state property is defined as (decision != PERMIT), not as a peer decision class.

### Injection Scenario Results

Update all references to injection outcomes:

Replace: "all injections resolve to SAFE_STATE"  
With: "all 13 injections resolve to exact decision outcomes: 4 produce HOLD, 9 produce DENY"

**Exact breakdown:**
```
HOLD scenarios (unknown evidence + escalation):
  - missing_predicate (GCIR-B0001)
  - corrupted_input (GCIR-B0002)
  - network_partition_or_delay (GCIR-B0004)
  - session_intent_compromise (GCIR-B0001)

DENY scenarios (known failure):
  - toctou, replay_attack, payload_mutation, concurrency_conflict
  - adaptive_attacker, identity_provenance_deception
  - runtime_infrastructure_drift, economic_logic_fragility
  - cross_entity_fraud_propagation
```

### Audit Queries

Replace old Q7-Q10 definitions with canonical Q1-Q10:

```
Q1: Obligation Disposition Completeness
    Every risk in risk register must have exactly one disposition
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q2: Exactly-One Disposition Per Risk
    Each risk maps to exactly one disposition, no duplicates
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q3: Predicate Origin Closure
    Every predicate has valid origin (risk_derived or compiler_invariant)
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q4: Temporal Bundle Validity
    Bundle metadata timestamps monotonic, payload_hash valid SHA-256
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q5: Commit-Before-Actuation Ordering
    All predicates enforce evidence commit time <= authorization time
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q6: Lifecycle Signing Authority
    Bundle signed and prepared for lifecycle registration
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q7: Runtime ACS Compilation Coverage
    Every runtime ACS compiles to >=1 risk-derived predicate
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q8: Gate-Predicate Structural Closure
    Every gate-map entry references existing predicate
    Every decisive predicate in gate-map
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q9: Actuation Authority Validity
    All evidence producers declared, resolvable in authority matrix
    Result: Case A 10/10 PASS, Case B 10/10 PASS

Q10: Mandatory Predicate Evidence Integrity
    Decisive gates have on_unknown='fail'
    Result: Case A 10/10 PASS, Case B 10/10 PASS
```

Aggregate: **20/20 PASS**

Negative Fixtures: **10/10 detect violations**

### Release References

Find and Replace:
- `v1.0.3` → `v1.0.5` (except in historical references)
- `v1.0.4` → (remove, superseded)
- `preregister-tier0-v2.2` → `preregister-tier0-v3.1`
- `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` → `158c0bd3785ac87a878671f76286be082a26d50d`

---

## Appendix C Updates

### Remove all placeholders

**Find and remove:**
- `[MANIFEST.sha256 root hash]` → Replace with: `9e3ddf96a64e9ba2b6d24f5806127f75b088d11cf7478eba6f09c3cc9437563c`
- `[container digest]` → Leave blank with note: "Container digest to be computed from v1.0.5 Dockerfile"
- `10.5281/zenodo.XXXXXXXX` → Replace with: "Version-specific archival DOI to be assigned after Zenodo deposit"

### Add Zenodo Deposit Instructions

> The artifact is ready for Zenodo deposit. Complete the submission with:
> 
> **Creators:** Sukhmangill (lead) and collaborators as documented
> **License:** [Project license]
> **Version:** 1.0.5
> **Freeze Commit:** 158c0bd3785ac87a878671f76286be082a26d50d
> **DOI:** To be assigned by Zenodo
> 
> After deposit, insert the Zenodo-assigned DOI into this section and update the GitHub release notes.

---

## Verification Checklist

- [ ] Case A/B hashes match final_v3_1
- [ ] Case B structure (6R/6D/6ACS/6RP/3IP/9total) confirmed
- [ ] Q1-Q10 canonical definitions replaced
- [ ] All 20/20 PASS reported
- [ ] Negative fixtures 10/10 reported
- [ ] Injections 13/13 PASS with 4 HOLD / 9 DENY reported
- [ ] Tests 320/320 PASS reported
- [ ] TD = 1.0 / 62/62 reported
- [ ] Monte Carlo values match final_v3_1 exactly
- [ ] All v1.0.3 references updated to v1.0.5 (except historical)
- [ ] All v2.2 freeze references updated to v3.1
- [ ] All stale freeze commits updated
- [ ] All XXXXXXXX placeholders removed
- [ ] Zenodo instruction added
- [ ] Release notes prepared
- [ ] No stale claims about v1.0.4

---

## Freeze Information to Add

**To Section XI-I (Reproducibility):**

> This artifact version (v1.0.5) is frozen at commit 158c0bd3785ac87a878671f76286be082a26d50d, publicly tagged as preregister-tier0-v3.1. The scientific results reported in this paper are machine-generated from that exact frozen commit, executed in results/final_v3_1/ without any tuning or post-hoc modification.
>
> v1.0.5 corrects v1.0.4's code/result mismatch by implementing the exact PERMIT/DENY/HOLD decision semantics and canonical Q1-Q10 audit queries reported in this paper. All results remain identical to the frozen values. The older v1.0.3 and v1.0.4 releases are retained for historical reference but are superseded by v1.0.5 as the authoritative reproducibility artifact.

---

**Status:** Ready for manual update in Microsoft Word  
**Tool:** None required — direct text search/replace in document  
**Est. Time:** 30–45 minutes for careful review and replacement  
**Verification:** Use tools/verify_reported_results.py after update
