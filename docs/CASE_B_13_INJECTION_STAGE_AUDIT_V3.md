# CASE_B_13_INJECTION_STAGE_AUDIT_V3.md

**Forensic stage audit of all 13 Case B injection scenarios.**

**Source:** `experiments/case_b_injection_scenarios.py`, actual runtime resolver

---

## CRITICAL ARCHITECTURAL FINDING

**ALL 13 existing Case B injections operate at RUNTIME PREDICATE EVALUATION stage.**

Evidence:
- File: `experiments/case_b_injection_scenarios.py` lines 193-195
- Execution: `outcomes[spec["target"]] = spec["outcome"]` then `resolve(bundle, outcomes)`
- Stage: AFTER valid compiled bundle exists; BEFORE runtime decision is final
- Not: compilation stage, not issuance stage

---

## STAGE-BY-STAGE ANALYSIS

### COMPILATION STAGE
- Status: **SUCCESSFULLY COMPLETED** for all 13 scenarios
- Evidence: `bundle.predicates` exists and is non-empty
- Valid compiled bundle artifact: confirmed to exist in results/final_v2/case_b/

### ISSUANCE / ACTIVATION STAGE
- Status: **SUCCESSFULLY COMPLETED** for all 13 scenarios
- Evidence: Bundle passed activation; predicates loaded with gate_map and escalation_map
- Bundle is issued and active

### RUNTIME EVALUATION STAGE
- Status: **THIS IS WHERE ALL 13 INJECTIONS OCCUR**
- Mechanism: `resolve(bundle, outcomes_with_injection)`
- Outcome mutation: `outcomes[predicate_id]` = "fail" or "unknown"
- Resolver response: `decision` in {PERMIT, SAFE_STATE}

---

## FINAL 13-SCENARIO TABLE

| # | Family | Predicate | Injected state | Escalation route | Decision expected | Exact outcome | Externalization |
|---|--------|-----------|---|---|---|---|---|
| 1 | missing_predicate | GCIR-B0001 | unknown | payment_operations_urgent | SAFE_STATE | **HOLD** | false |
| 2 | corrupted_input | GCIR-B0002 | unknown | payment_operations_urgent | SAFE_STATE | **HOLD** | false |
| 3 | toctou | GCIR-B0006 | fail | compliance_records_urgent | SAFE_STATE | **DENY** | false |
| 4 | replay_attack | GCIR-B0005 | fail | payment_operations_urgent | SAFE_STATE | **DENY** | false |
| 5 | payload_mutation | GCIR-B0001 | fail | payment_operations_urgent | SAFE_STATE | **DENY** | false |
| 6 | concurrency_conflict | GCIR-B0003 | fail | payment_operations_urgent | SAFE_STATE | **DENY** | false |
| 7 | network_partition_or_delay | GCIR-B0004 | unknown | sanctions_desk_urgent | SAFE_STATE | **HOLD** | false |
| 8 | adaptive_attacker | GCIR-B0002 | fail | payment_operations_urgent | SAFE_STATE | **DENY** | false |
| 9 | identity_provenance_deception | GCIR-B0001 | fail | payment_operations_urgent | SAFE_STATE | **DENY** | false |
| 10 | runtime_infrastructure_drift | GCIR-INV-VERSION | fail | technology_change_management | SAFE_STATE | **DENY** | false |
| 11 | economic_logic_fragility | GCIR-B0002 | fail | payment_operations_urgent | SAFE_STATE | **DENY** | false |
| 12 | cross_entity_fraud_propagation | GCIR-B0004 | fail | sanctions_desk_urgent | SAFE_STATE | **DENY** | false |
| 13 | session_intent_compromise | GCIR-B0001 | unknown | payment_operations_urgent | SAFE_STATE | **HOLD** | false |

---

## OUTCOME SUMMARY

**HOLD scenarios (unknown evidence + escalation path):** 1, 2, 7, 13 = **4 scenarios**  
**DENY scenarios (known failure):** 3, 4, 5, 6, 8, 9, 10, 11, 12 = **9 scenarios**  
**REJECT_AT_COMPILATION:** 0 (not applicable; compilation already succeeded)  
**REJECT_AT_ISSUANCE:** 0 (not applicable; bundle already issued)  
**PERMIT:** 0 (no scenario is positive control)

---

## MANDATORY GATE ANALYSIS

All 13 target predicates are **mandatory/decisive** gates with **on_unknown = fail**:

- GCIR-B0001: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail
- GCIR-B0002: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail
- GCIR-B0003: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail
- GCIR-B0004: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail
- GCIR-B0005: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail
- GCIR-B0006: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail
- GCIR-INV-VERSION: gate_type=mandatory, mandatory_role=decisive, on_unknown=fail

---

## ESCALATION PATH VERIFICATION

ALL 13 target predicates have explicit escalation routes:

```
GCIR-B0001 → payment_operations_urgent (sla_hours: 1)
GCIR-B0002 → payment_operations_urgent (sla_hours: 2)
GCIR-B0003 → payment_operations_urgent (sla_hours: 2)
GCIR-B0004 → sanctions_desk_urgent (sla_hours: 1)
GCIR-B0005 → payment_operations_urgent (sla_hours: 1)
GCIR-B0006 → compliance_records_urgent (sla_hours: 1)
GCIR-INV-VERSION → technology_change_management (sla_hours: 1)
```

Source: `results/final_v2/case_b/escalation_map.json`

---

## OUTCOME CLASSIFICATION RATIONALE

### HOLD (4 scenarios: 1, 2, 7, 13)

All have:
- **Injected state:** `outcome="unknown"`
- **Predicate:** mandatory/decisive, on_unknown=fail
- **Escalation:** YES (concrete route defined)

Per 5.5d semantics: **Unknown evidence + explicit escalation path → HOLD**

Decision is paused, escalated to the defined route pending evidence or manual review.

### DENY (9 scenarios: 3-6, 8-12)

All have:
- **Injected state:** `outcome="fail"`
- **Predicate:** mandatory/decisive, on_unknown=fail
- **Condition:** Known false (evidence shows violation)

Per 5.5d semantics: **Known policy failure → DENY**

Decision is explicitly refused because the mandatory condition is not satisfied.

---

## RUNTIME EXECUTION PATHWAY

All 13 follow this sequence:

1. **Compile:** Compiler Φ produces valid bundle (COMPLETED before injection)
2. **Issue:** Bundle passes activation validation (COMPLETED before injection)
3. **Evaluate:** Runtime resolver called with outcomes dict
4. **Inject:** `outcomes[predicate_id] = "unknown"` or `"fail"`
5. **Resolve:** `resolve(bundle, outcomes)` produces `decision`
6. **Current:** decision ∈ {PERMIT, SAFE_STATE}
7. **New:** decision ∈ {PERMIT, DENY, HOLD} + derived SAFE_STATE = (decision != PERMIT)

---

## CODE/SPEC DELTA

Current code:
```python
verdict["decision"] == "SAFE_STATE"  # Conflates DENY and HOLD
```

New code required:
```python
verdict["decision"] in {PERMIT, DENY, HOLD}  # Exact outcomes
safe_state = verdict["decision"] != PERMIT   # Derived aggregate
```

Affected files:
- `experiments/case_b_injection_scenarios.py` line 202: test assertion
- `src/gcir/precedence.py`: resolver must return exact outcome enum
- Test harness: all 13 assertions must be exact (DENY or HOLD, not aggregate)

---

## CONCLUSION

✅ All 13 scenarios are unambiguously runtime predicate evaluation injections  
✅ All have mandatory gates with escalation routes  
✅ Outcome mapping is deterministic: unknown + escalation → HOLD; fail → DENY  
✅ 4 HOLD + 9 DENY + 0 rejections = complete mapping  
✅ Externalization = false for all (fail-closed)  
✅ Code changes required but scoped and understood

**Status: READY FOR PHASE 1 DEVELOPMENT** (6-ACS configuration approved)

