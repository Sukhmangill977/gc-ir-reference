# RUNTIME_OUTCOME_MIGRATION_V3.md

**Purpose:** Document the migration from aggregated SAFE_STATE reporting to exact outcome (PERMIT/DENY/HOLD) without breaking existing tooling.

**Status:** PLANNING PHASE

---

## CURRENT BEHAVIOR

```python
verdict["decision"] in {"PERMIT", "SAFE_STATE"}
```

All non-permit failures reported as "SAFE_STATE", without distinction between:
- Known policy violation (should be DENY)
- Unknown evidence with escalation (should be HOLD)

---

## NEW BEHAVIOR

```python
verdict["decision"] in {"PERMIT", "DENY", "HOLD"}
verdict["safe_state"] = (verdict["decision"] != "PERMIT")
```

Exact runtime outcomes reported; SAFE_STATE derived.

---

## AFFECTED CONSUMERS

Search all code for these patterns:

### Pattern 1: Direct decision check

```python
if verdict["decision"] == "SAFE_STATE":
    # handle non-permit
```

**Files using this pattern:**

- `experiments/case_b_injection_scenarios.py` line ~202: `passed = verdict["decision"] == "SAFE_STATE"`
- Any resolver test checking specific outcome
- Any report/display assuming only PERMIT or SAFE_STATE

**Impact:** Will break; requires explicit update to check exact outcome

### Pattern 2: Safe-state property check

```python
is_safe = verdict["decision"] != "PERMIT"
```

**Files using this pattern:**

- Unclear; requires codebase scan

**Impact:** May work unchanged if refactored to use exact_outcome; should migrate to `verdict["safe_state"]`

### Pattern 3: Decision in set check

```python
if verdict["decision"] in {"PERMIT", "SAFE_STATE"}:
```

**Files using this pattern:**

- Unknown; requires codebase scan

**Impact:** Will break if expecting only two values; needs update for DENY/HOLD

---

## MIGRATION STRATEGY

### Phase A: Dual Reporting (Backward Compatible)

Implement resolver to return BOTH exact outcome and aggregate:

```python
{
    "decision": "DENY",              # Exact outcome
    "exact_outcome": "DENY",         # Explicit alias
    "safe_state": True,              # Aggregate property
    "safe_state_from": "DENY",       # Traceability
    "deciding_class": "mandatory_failure",
    "deciding_predicate": "GCIR-B0001",
    "externalization": False,
    ... (existing fields)
}
```

**Backward compatibility:**
- Old code checking `verdict["decision"] == "SAFE_STATE"` will break
- New code can check `verdict["decision"] in {"DENY", "HOLD"}`
- Code checking `verdict["safe_state"]` will continue to work
- Code checking `verdict["decision"] != "PERMIT"` will continue to work

### Phase B: Consumer Updates

**Priority 1 (must update before Phase 1 test runs):**
- `experiments/case_b_injection_scenarios.py`: Update test assertions
  - From: `verdict["decision"] == "SAFE_STATE"`
  - To: `verdict["decision"] in {"DENY", "HOLD"} and verdict["safe_state"] == True`

**Priority 2 (should update before freeze):**
- Any historical test checking for SAFE_STATE
- Any reporting that assumes only PERMIT/SAFE_STATE split
- Any documentation assuming binary decision

**Priority 3 (nice to have):**
- Update README examples
- Update schema documentation
- Update architecture diagrams

### Phase C: Deprecation Warning (Optional)

For backwards compatibility, could add:

```python
if "decision" in verdict and verdict["decision"] == "SAFE_STATE":
    # This is now "DENY" or "HOLD"
    # See RUNTIME_OUTCOME_MIGRATION_V3.md
    warnings.warn("SAFE_STATE is deprecated; use exact_outcome")
```

But this may be unnecessary if changes are localized.

---

## IMPLEMENTATION PLAN

### Step 1: Identify All Consumers

```bash
grep -r "SAFE_STATE\|decision.*PERMIT\|decision\|resolve(" \
  src/ experiments/ tests/ tools/ \
  --include="*.py" \
  | grep -v ".pyc" \
  | sort | uniq
```

Create: `RUNTIME_OUTCOME_MIGRATION_V3_CONSUMERS.txt` (list all affected files)

### Step 2: Update Resolver

**File:** `src/gcir/precedence.py`

**Changes:**
1. Add exact outcome classification (PERMIT/DENY/HOLD)
2. Return new schema with `decision`, `exact_outcome`, `safe_state`
3. Preserve all existing fields for backward compatibility

**Testing:**
- Unit tests for each outcome type
- All three outcomes (PERMIT, DENY, HOLD) covered
- Aggregate property verified (safe_state correct)

### Step 3: Update Primary Consumer

**File:** `experiments/case_b_injection_scenarios.py`

**Changes:**
1. Update test assertion from SAFE_STATE to exact outcomes
2. Add secondary safe_state assertion
3. Update row output schema to include exact_outcome

**Testing:**
- All 13 injections pass with exact outcomes
- SAFE_STATE aggregate property verified

### Step 4: Run Historical Tests

**Command:** `make test` (or equivalent)

**Expected results:**
- Tests that check `decision == "SAFE_STATE"` will fail
- Tests that check aggregate properties should pass
- Identify all broken tests

**Action:** Fix all broken tests to use exact outcomes or aggregates

### Step 5: Update Documentation

**Files to update:**
- `README.md`: Update examples
- `docs/DECISION_OUTCOMES.md`: New file with PERMIT/DENY/HOLD semantics
- `docs/SCHEMA.md`: Update verdict schema
- Architecture diagrams if any

### Step 6: Regression Testing

**Ensure:**
- Case A unaffected (if resolver generic)
- Case B 13 injections produce exact outcomes
- Q1-Q10 implementations unaffected
- No unexpected changes to bundle hashes

---

## SCHEMA CHANGE

### Old schema

```json
{
  "decision": "SAFE_STATE",
  "deciding_class": "mandatory_failure",
  "contributing_predicates": [...]
}
```

### New schema (Phase A - Dual reporting)

```json
{
  "decision": "DENY",
  "exact_outcome": "DENY",
  "safe_state": true,
  "safe_state_from": "DENY",
  "deciding_class": "mandatory_failure",
  "deciding_predicate": "GCIR-B0001",
  "contributing_predicates": [...],
  "externalization": false,
  "escalation_route": "payment_operations_urgent" (if HOLD only)
}
```

### New schema (Phase B - Simplified, if approved)

```json
{
  "decision": "DENY",
  "safe_state": true,
  "deciding_class": "mandatory_failure",
  "contributing_predicates": [...]
}
```

---

## TESTING STRATEGY

### Unit tests for resolver

```python
def test_resolve_permit():
    # All pass -> PERMIT
    
def test_resolve_deny():
    # Mandatory failure (known fail) -> DENY
    
def test_resolve_hold():
    # Mandatory failure (unknown + escalation) -> HOLD
    
def test_safe_state_aggregate():
    # safe_state = (decision != "PERMIT")
    
def test_externalization_property():
    # externalization = false for all non-permit cases
```

### Integration tests

```python
def test_case_b_injections_exact_outcomes():
    # Scenarios 1,2,7,13 -> HOLD
    # Scenarios 3-6,8-12 -> DENY
    # All -> safe_state=True
```

### Regression tests

```python
def test_case_a_unaffected():
    # Case A behavior unchanged
    
def test_historical_safe_state_aggregate():
    # All non-permit (DENY or HOLD) have safe_state=True
```

---

## RISK ASSESSMENT

| Risk | Probability | Mitigation |
|---|---|---|
| Breaking historical code | HIGH | Identify and update all consumers |
| Schema misunderstanding | MEDIUM | Clear documentation and examples |
| Regression in Case A | MEDIUM | Comprehensive regression testing |
| Escalation route missing for HOLD | MEDIUM | Verify all HOLD scenarios have escalation_map entry |
| Hash changes unexpectedly | MEDIUM | Document any source changes |

---

## ROLLBACK PLAN

If critical breakage occurs during Phase 1:

1. Revert resolver changes
2. Return to SAFE_STATE-only reporting
3. Proceed with Phase 1 using aggregate outcomes only
4. Document why exact outcomes could not be implemented
5. Report as known gap for future work

---

## SUCCESS CRITERIA

Phase 1 runtime outcome migration is successful if:

1. ✅ All 13 injections produce exact DENY/HOLD outcomes
2. ✅ SAFE_STATE property correctly aggregates to all non-permit cases
3. ✅ No regression in Case A scientific results
4. ✅ Test suite passes with updated assertions
5. ✅ Schema change documented clearly
6. ✅ Backward compatibility strategy implemented

---

## DOCUMENTATION UPDATE

Create new file: `docs/DECISION_OUTCOMES_V3.md`

Content should include:

- PERMIT definition and conditions
- DENY definition and conditions
- HOLD definition, conditions, and escalation requirement
- SAFE_STATE as aggregate property
- Schema representation
- 13-injection example outcomes
- Backward compatibility note

