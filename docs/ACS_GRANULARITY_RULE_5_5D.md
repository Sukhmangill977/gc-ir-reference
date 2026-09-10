# ACS_GRANULARITY_RULE_5_5D.md

**Purpose:** Define a defensible criterion for when two control requirements deserve separate Approved Control Specification (ACS) records.

**Authority:** Derived from PAPER_REQUIREMENTS.md Section 4.3 (ACS definition) and Section 4.4 (total disposition with independent predicate cardinality).

---

## CRITERION FOR DISTINCT ACS

An Approved Control Specification should normally have its own ACS record if it exhibits **at least one** of the following:

### 1. **Independent condition that can pass/fail separately**

The control requirement can be evaluated in isolation from other requirements in the same risk. If two requirements are logically OR'd or AND'd but can have different outcomes, they may warrant separate ACS records.

**Example (justifies split):**
- "Permit must be unredeemed AND transaction hash must be novel"
  - These can fail independently
  - Permit unredeemed = FAIL, hash novel = PASS → Decision fails
  - Permit unredeemed = PASS, hash novel = FAIL → Decision fails
  - Separate evaluation possible

**Example (does NOT justify split):**
- "Amount must be ≤ bound"
  - Single scalar comparison
  - Cannot decompose without creating artificial sub-bounds

### 2. **Independent observable/evidence requirement**

The control requires evidence from a different source or subject than other controls in the same risk.

**Example (justifies split):**
- Control 1 requires evidence from permit authority service
- Control 2 requires evidence from sanctions screening service
- Different evidence producers → may warrant separate ACS

**Example (does NOT justify split):**
- "Amount received from payment instruction service must ≤ approved bound"
- Single evidence source, single observable
- No basis for split

### 3. **Independent authorization scope**

The control operates under a different decision authority, delegation, or approval scope.

**Example (justifies split):**
- Control 1: "Compliance officer must approve transaction"
- Control 2: "Risk manager must confirm exposure limit"
- Different approvers/authorities → separate ACS justified

**Example (does NOT justify split):**
- "Payment must be approved by transaction agent"
- Single authority → no split basis

### 4. **Independent threshold/bound**

The control has its own measured bound, trigger level, or quantitative decision point that is independently managed.

**Example (justifies split):**
- Control 1: "Amount ≤ $10K per transaction"
- Control 2: "Amount ≤ $100K per day"
- Independent thresholds, distinct operational bounds → separate ACS justified

**Example (does NOT justify split):**
- "Count ≤ window_bound" (single threshold, single bound, single observable)
- No basis for split

### 5. **Independent temporal condition**

The control requirement is gated by a different temporal constraint or time window.

**Example (justifies split):**
- Control 1: "Not redeemed in last 30 days"
- Control 2: "Not redeemed in entire permit lifetime"
- Different temporal windows → may warrant separate ACS

**Example (does NOT justify split):**
- "Commit time must be between auth time and actuation time" (single ordering requirement)
- No temporal split

### 6. **Independent gate consequence**

The control, if violated, triggers a different escalation path, approval chain, or business consequence.

**Example (justifies split):**
- Control 1 violation → escalate to payment operations (SLA 1h)
- Control 2 violation → escalate to sanctions desk (SLA 24h)
- Different escalation routes → may warrant separate ACS

**Example (does NOT justify split):**
- "Both violations escalate to same route with same SLA"
- No basis for separate ACS

### 7. **Can be evaluated independently (technical criterion)**

The runtime evaluation can be decomposed: one ACS can be evaluated, pass/fail determined, and recorded without evaluating the second.

**Example (justifies split):**
- ACS-1: Check permit signature (yes/no)
- ACS-2: Check hash binding (yes/no)
- Can evaluate #1 independently, then #2

**Example (does NOT justify split):**
- "Receipt must be committed between auth and actuation"
- Cannot evaluate "between auth" without evaluating "before actuation"
- Temporal ordering is indivisible

---

## DIFFERENCES THAT ARE NOT SUFFICIENT

The following are **insufficient** by themselves to warrant separate ACS:

### Cosmetic differences
- Different ACS ID numbering scheme
- Paraphrased or synonymous wording of the same requirement
- Different field names for the same observable

### Duplicated observable with same semantics
- Same predicate type repeated
- Same evaluation basis, threshold, evidence source

### Arbitrary decomposition to increase count
- Splitting a single risk into multiple ACS merely to expand a number
- Decomposing without independent failure modes or decision consequences

---

## DECISION FRAMEWORK: WHEN TO SPLIT

**Ask these questions in order:**

1. **Does the requirement have independent failure modes?**
   - Can failure mode A occur without failure mode B?
   - If YES → consider split
   - If NO → single ACS

2. **Does the requirement come from separate evidence sources?**
   - Different evidence producer required?
   - If YES → consider split
   - If NO → continue

3. **Does the requirement have independent operational bounds or thresholds?**
   - Separate measured threshold?
   - Separate approval authority?
   - If YES → consider split
   - If NO → single ACS

4. **Can the requirement be evaluated independently at runtime?**
   - Can one condition be evaluated and a pass/fail determined without evaluating the other?
   - If YES → consider split
   - If NO → single ACS

5. **Is the split explicitly mandated or implied by the manuscript?**
   - Does the manuscript explicitly enumerate separate control requirements?
   - Does the risk prose suggest OR (two failure modes) rather than AND (joint property)?
   - If YES → split justified
   - If NO → require author clarification

**Default:** Single ACS per risk unless one or more of criteria 1–4 are met AND manuscript evidence exists or author explicitly requests split.

---

## APPLICATION TO CASE B

### B-01: Payment Release Without Valid Permit

**Requirement text:** "permit valid and bound"

**Analysis:**
1. Independent failure modes? 
   - Signature verification fails ← YES
   - Hash binding fails ← YES
   - Can both fail together ← YES
   - Can one fail while other passes ← YES
   - **→ Potentially splittable**

2. Independent evidence sources?
   - Both from same permit artifact
   - **→ Not a split basis**

3. Independent operational bounds?
   - No; both part of "valid permit" definition
   - **→ Not a split basis**

4. Runtime evaluation independence?
   - Can evaluate signature without binding (returns known-invalid)
   - Can evaluate binding without signature (returns unknown if sig invalid)
   - **→ Somewhat independent**

5. Manuscript mandate for split?
   - Manuscript says: "payment release **without valid permit**" (singular phenomenon)
   - No enumeration of signature vs. binding as separate risks
   - **→ NO split mandate**

**Verdict:** Can defensibly remain 1 ACS (current practice). A split to 2 would require manuscript clarification that signature verification and hash binding are governed as separate concerns. Not evident from manuscript.

**Recommendation:** Remain 1 ACS.

---

### B-02: Amount > Per-Transaction Limit

**Requirement text:** "amount > per-transaction limit"

**Analysis:**
1. Independent failure modes?
   - Only one condition: amount ≤ bound?
   - **→ NO**

2. Continue analysis?
   - **→ NO; single ACS justified**

**Verdict:** 1 ACS. Single threshold, no decomposition.

**Recommendation:** Remain 1 ACS.

---

### B-03: Transaction Count/Window > Bound

**Requirement text:** "txn count/window > bound"

**Analysis:**
1. Independent failure modes?
   - Only one condition: count ≤ bound?
   - **→ NO**

**Verdict:** 1 ACS. Single velocity bound.

**Recommendation:** Remain 1 ACS.

---

### B-04: Counterparty ∈ Restricted List

**Requirement text:** "counterparty ∈ restricted-party list"

**Analysis:**
1. Independent failure modes?
   - Only one condition: match == false?
   - **→ NO**

**Verdict:** 1 ACS. Single screening check.

**Recommendation:** Remain 1 ACS.

---

### B-05: Permit Reuse or Duplicate Transaction Hash

**Requirement text:** "permit reuse OR duplicate txn hash"

**Analysis:**
1. Independent failure modes?
   - Permit unredeemed ← independent condition
   - Transaction hash novel ← independent condition
   - "OR" suggests two distinct failure modes
   - **→ YES, defensibly splittable**

2. Independent evidence sources?
   - Both from permit service/transaction ledger
   - **→ Not a split basis; same source**

3. Independent operational bounds?
   - Permit lifetime vs. transaction novelty
   - **→ Separate managed entities**

4. Runtime evaluation independence?
   - Can evaluate permit redemption independently
   - Can evaluate hash novelty independently
   - **→ YES**

5. Manuscript mandate for split?
   - Risk prose says "permit reuse **OR** duplicate hash" (disjunction)
   - Two separate failure classes
   - However, current ACS treats as conjunction (both must be true)
   - No explicit enumeration as 2 ACS
   - **→ Weakly supported; author clarification needed**

**Verdict:** Can split to 2 ACS if manuscript clarifies intent. Current 1 ACS is defensible. Without author mandate, remain 1 ACS.

**Alternative:** If author explicitly states these are independently monitored/escalated, split to:
- ACS-B05-01: Permit single-use
- ACS-B05-02: Transaction hash novelty

**Recommendation:** Remain 1 ACS (current state) unless author provides explicit split mandate.

---

### B-06: Receipt Not Committed Between Authorization and Actuation

**Requirement text:** "receipt not committed between authorization and actuation"

**Analysis:**
1. Independent failure modes?
   - Single temporal ordering: auth ≤ commit < actuation
   - Cannot decompose without losing ordering invariant
   - **→ NO**

**Verdict:** 1 ACS. Temporal ordering is atomic.

**Recommendation:** Remain 1 ACS.

---

## CONCLUSION: SCIENTIFICALLY JUSTIFIED CARDINALITY

**Case B ACS count:** **6** (current)

**Rationale:**
- B-01: 1 ACS (joint permit validity observable)
- B-02: 1 ACS (single threshold)
- B-03: 1 ACS (single velocity bound)
- B-04: 1 ACS (single screening check)
- B-05: 1 ACS (joint idempotency check, OR-ed risk prose but AND-ed implementation)
- B-06: 1 ACS (single temporal ordering)

**Total: 6 ACS (scientifically justified)**

**Possible expansion:** 7 ACS if B-05 is split into permit single-use + hash novelty, but this requires author clarification.

**NOT justified:** 9 ACS (3/2/1/1/1/1). No manuscript basis for splitting B-01 into 3 or B-02 into 2.

