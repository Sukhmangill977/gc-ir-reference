# Scientific Freeze: preregister-tier0-v3.1

**Freeze Date:** 2026-09-11  
**Freeze Commit:** (to be filled after tagging)  
**Public Tag:** preregister-tier0-v3.1  
**Status:** LOCKED FOR REPORTABLE CAMPAIGN

---

## Scope

This freeze locks the exact code and configuration for Phase 1 v1.0.5 correction:

### Code Implementation
- **PERMIT/DENY/HOLD Decision Semantics:** Exact three-state outcome classification in src/gcir/precedence.py
  - PERMIT: all mandatory conditions satisfied, safe_state=false
  - DENY: mandatory failure (known fail or no escalation), safe_state=true
  - HOLD: unknown evidence + valid escalation route, safe_state=true
- **Canonical Q1-Q10 Audit Queries:** src/gcir/audit_queries.py
  - Q1: Obligation disposition completeness
  - Q2: Exactly-one disposition per risk
  - Q3: Predicate origin closure
  - Q4: Temporal bundle validity
  - Q5: Commit-before-actuation ordering
  - Q6: Lifecycle signing authority
  - Q7: Runtime ACS compilation coverage
  - Q8: Gate/predicate structural closure
  - Q9: Actuation authority validity
  - Q10: Mandatory predicate evidence integrity

### Test Coverage
- **Unit Tests:** tests/unit/test_core.py (52 tests)
- **Corpus Tests:** tests/adversarial/test_corpus.py (93 tests)
- **Injection Scenarios:** experiments/case_b_injection_scenarios.py
  - 4 HOLD outcomes (missing_predicate, corrupted_input, network_partition_or_delay, session_intent_compromise)
  - 9 DENY outcomes (toctou, replay_attack, payload_mutation, concurrency_conflict, adaptive_attacker, identity_provenance_deception, runtime_infrastructure_drift, economic_logic_fragility, cross_entity_fraud_propagation)
- **Negative Fixtures:** src/gcir/negative_fixtures.py (10 fixtures, all detect violations)
- **Total Test Count:** 320 tests, 100% pass

### Case Studies
- **Case A:** f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536
- **Case B:** 2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce
  - 6 risks (B-01, B-02, B-03, B-04, B-05, B-06)
  - 6 dispositions (one per risk)
  - 6 approved control specifications (ACS)
  - 6 risk-derived predicates
  - 3 compiler-invariant predicates
  - 9 total predicates

### Determinism
- **Translation Determinism (TD):** 1.0 (62/62 runs)
- **Coverage:** key_shuffle (5), row_shuffle (10), locale (3), timezone (3), repeat (10)
- **All runs produce identical output:** Verified across macOS locales (C, en_US, de_DE, tr_TR, ja_JP) and timezones (UTC, America/Edmonton, Europe/Berlin, Asia/Kolkata, Pacific/Chatham)

### Monte Carlo (K=250,000)
- **Case A:** max FP_heat=0.321268 (R-06, MCSE=0.000934), max FP_C*=0.000000
- **Case B:** max FP_heat=0.317980 (B-01, MCSE=0.000931), max FP_C*=0.000000

### Q1-Q10 Verification
- **Case A:** 10/10 queries PASS
- **Case B:** 10/10 queries PASS

### Injection Verification
- **All 13 scenarios:** PASS with exact decision outcomes
  - Clean control: PERMIT / safe_state=false
  - All injections: DENY or HOLD / safe_state=true

---

## Constraints

- **No further code changes** until reportable campaign complete
- **No tuning** after seeing final results
- **No modifications** to historical releases/tags (preregister-tier0-v3, v1.0.3)
- **Reportable campaign input:** Exact commit identified by this tag, no other source

---

## Files Included

```
src/gcir/                       # Core implementation
  precedence.py               # PERMIT/DENY/HOLD resolver
  audit_queries.py            # Q1-Q10 audit queries
  negative_fixtures.py        # Q-query violation fixtures

tests/                         # Test suite (320/320 pass)
experiments/                   # Adversarial corpus + injections
cases/case_a, case_b/         # Case studies with schemas
.github/workflows/            # CI/CD (tests, determinism, reproducibility)
requirements.txt              # Dependencies pinned
Dockerfile                    # Reproducibility container
```

---

## Reportable Campaign Instructions

1. Clone/checkout this exact freeze commit
2. Run all experiments in clean environment
3. Write outputs to `results/final_v3_1/` only
4. Do NOT modify any other results/ subdirectory
5. Record actual counts, hashes, metrics
6. Report verifier results
7. Await approval before manuscript update

---

## Success Criteria for Reportable Campaign

All of the following must pass from this frozen code:
- [ ] Case A/B compilation with matching hashes
- [ ] Q1-Q10 both cases: 10/10 PASS
- [ ] 10 negative fixtures: all detect violations
- [ ] 13 injections: 4 HOLD + 9 DENY with exact outcomes
- [ ] Test suite: actual count and 100% pass
- [ ] TD: 1.0 (62/62 determinism runs)
- [ ] Monte Carlo: actual FP_heat values
- [ ] Freeze check: all metrics verified
- [ ] Docker reproducibility: successful build and run
- [ ] Cross-platform CI: all workflows green

---

**This freeze is locked and public. No further commits to this tag are permitted.**
