# CASE_B_CONTROL_REQUIREMENT_EXTRACTION.md

**Objective:** Forensically reconstruct Case B control requirements from the authoritative manuscript and repository sources. Determine the scientifically justified cardinality of Approved Control Specifications.

**Methodology:** Direct extraction from:
1. PAPER_REQUIREMENTS.md (Section 10, Case B — official manuscript extraction)
2. cases/case_b/inputs/assessment.json (6 risks with cause-event-consequence triples)
3. cases/case_b/acs/approved_control_specifications.json (current 6 ACS records)
4. results/final_v2/case_b/bundle.json (compiled predicates)
5. results/final_v2/case_b/gate_map.json (gate semantics)

---

## MANUSCRIPT BASELINE (PAPER_REQUIREMENTS.md SECTION 10)

**Authoritative text on Case B:**

> "**6 register rows, all runtime, all mandatory (4 by C\*, 2 by other approved mandatory policy).**"

The manuscript explicitly enumerates 6 risks, each with a single event/consequence pair:

| risk_id | Event (observable) | consequence_class | L×I | Gate (source) | on_unknown |
|---|---|---|---|---|---|
| B-01 | payment release without valid permit | **C\***: authority | 15 | mandatory (C\*) | fail |
| B-02 | amount > per-transaction limit | financial_loss | 16 | mandatory (other) | fail |
| B-03 | txn count/window > bound | financial_loss | 12 | mandatory (other) | fail |
| B-04 | counterparty ∈ restricted list | **C\***: statutory (material) | 5 (**L=1, I=5**) | mandatory (C\*) | fail + escalate |
| B-05 | permit reuse or duplicate txn hash | **C\***: irreversible | 10 | mandatory (C\*) | fail |
| B-06 | receipt not committed between authorization and actuation | **C\***: statutory (material) | 10 | mandatory (C\*; coincides with INV-EVIDENCE-COMMIT) | fail |

**Key normative constraint from PAPER_REQUIREMENTS.md Section 4.4:**

> "Predicate cardinality is deliberately independent of risk cardinality **(0, 1 or several predicates per risk)**."

The manuscript does **not** mandate that every risk must yield exactly one ACS. It permits 0, 1, or multiple.

---

## RISK-BY-RISK CONTROL REQUIREMENT ANALYSIS

### B-01: Payment Release Without Valid Permit

**Manuscript definition:**
- Event: "payment release without valid permit"
- Observable: Permit valid AND bound to transaction hash (per ACS record)
- Consequence class: Unauthorized authority exercise (C\*)
- Evidence source: Signed permit artifact bound to transaction
- Evaluation basis: Structural check (signature + hash matching)

**Current ACS:** ACS-B01-01 (permit_binding)
```json
{
  "acs_id": "ACS-B01-01",
  "event_type": "permit_binding",
  "observable_id": "permit_valid_and_bound",
  "decision_semantics": "PERMIT requires a valid permit signature whose bound hash equals the transaction hash"
}
```

**Control requirement atomicity analysis:**

The observable requires **two sequential logical conditions**:
1. **Signature validity:** The permit's cryptographic signature must verify under the authorized authority's key
2. **Hash binding:** The transaction hash embedded in the permit must match the actual transaction hash

**Question:** Are these genuinely independent conditions that can fail separately?

- Signature verification FAILS → evidence producer cannot be trusted; decision fails
- Hash matching FAILS → payload has been modified after permit issuance; decision fails
- Both can fail independently
- Both are **mandatory** (on_unknown = fail)

**Candidate split:**
- ACS-B01-01a: Permit signature verification (structural check)
- ACS-B01-01b: Transaction hash binding (deterministic lookup)

**Verdict on split:** AMBIGUOUS (can be split, but currently merged)

**Alternative interpretation:** The observable combines these as a **single atomic property**: "valid, bound permit." Splitting would be artificial unless the system architecture treats them separately for governance or monitoring purposes.

**No mandate for split in manuscript:** The manuscript text says "payment release without valid permit" as a **single phenomenon**, not as two separate risks or control requirements.

---

### B-02: Amount > Per-Transaction Limit

**Manuscript definition:**
- Event: "amount > per-transaction limit"
- Observable: amount_minor_units
- Consequence class: Financial loss
- Evidence source: Signed payment instruction
- Evaluation basis: Threshold on measured value

**Current ACS:** ACS-B02-01 (amount_limit)
```json
{
  "acs_id": "ACS-B02-01",
  "event_type": "amount_limit",
  "observable_id": "amount_minor_units",
  "decision_semantics": "PERMIT requires amount_minor_units <= the approved bound"
}
```

**Control requirement atomicity analysis:**

Single, atomic threshold condition:
- Observable: measured amount in transaction
- Threshold: approved per-transaction bound
- Evaluation: amount ≤ bound?
- Failure condition: amount > bound

**No natural splitting:** This is a single scalar comparison. Cannot be decomposed into independent enforcement conditions.

**Candidate split:** None evident.

**Verdict:** NOT DISTINCT — cannot justify splitting.

---

### B-03: Transaction Count/Window > Bound

**Manuscript definition:**
- Event: "txn count/window > bound"
- Observable: window_transaction_count
- Consequence class: Financial loss + business disruption
- Evidence source: Velocity counter
- Evaluation basis: Threshold on measured value (aggregate over time window)

**Current ACS:** ACS-B03-01 (velocity_bound)
```json
{
  "acs_id": "ACS-B03-01",
  "event_type": "velocity_bound",
  "observable_id": "window_transaction_count",
  "decision_semantics": "PERMIT requires window_transaction_count <= the approved bound"
}
```

**Control requirement atomicity analysis:**

Single threshold condition:
- Observable: count of transactions in the approved time window
- Threshold: approved maximum count
- Evaluation: count ≤ bound?

**No natural splitting:** A velocity control is indivisible. Cannot separate "transactions up to bound 1" from "transactions up to bound 2" without inventing artificial sub-thresholds.

**Verdict:** NOT DISTINCT — cannot justify splitting.

---

### B-04: Counterparty ∈ Restricted Party List

**Manuscript definition:**
- Event: "counterparty ∈ restricted list"
- Observable: restricted_party_match
- Consequence class: Statutory prohibition (C*)
- Evidence source: Sanctions screening service
- Evaluation basis: Deterministic lookup (matching algorithm)

**Current ACS:** ACS-B04-01 (restricted_party_screening)
```json
{
  "acs_id": "ACS-B04-01",
  "event_type": "restricted_party_screening",
  "observable_id": "restricted_party_match",
  "decision_semantics": "PERMIT requires restricted_party_match == false"
}
```

**Control requirement atomicity analysis:**

Single condition:
- Observable: whether counterparty matches restricted list
- Decision: match == false (allowed) or match == true (prohibited)

**No natural splitting:** Sanctions screening is a unified check. Cannot split into "partial match screening" or "multi-match screening."

**Verdict:** NOT DISTINCT — cannot justify splitting.

---

### B-05: Permit Reuse or Duplicate Transaction Hash

**Manuscript definition:**
- Event: "permit reuse or duplicate txn hash"
- Observable: permit_unredeemed_and_hash_novel
- Consequence class: Irreversible external effect (C*)
- Evidence source: Permit authority service
- Evaluation basis: Deterministic lookup

**Current ACS:** ACS-B05-01 (permit_single_use)
```json
{
  "acs_id": "ACS-B05-01",
  "event_type": "permit_single_use",
  "observable_id": "permit_unredeemed_and_hash_novel",
  "decision_semantics": "PERMIT requires the permit to be unredeemed and the transaction hash to be novel"
}
```

**Control requirement atomicity analysis:**

The observable is a **conjunction** of two independent conditions:
1. **Permit single-use:** Permit has not been redeemed before
2. **Transaction novelty:** Transaction hash has not been seen before

**Question:** Are these genuinely independent?

- Permit unredeemed FAILS → same permit used twice (replay of authorization)
- Transaction hash not novel FAILS → same transaction attempted twice (replay of payment)
- Both can fail independently
- Both are **mandatory** (on_unknown = fail)

**Candidate split:**
- ACS-B05-01a: Permit single-use enforcement
- ACS-B05-01b: Transaction hash novelty check

**Verdict on split:** DISTINCT (genuinely independent conditions; can fail separately; different observable states; can be evaluated independently)

**Manuscript support for split?** The event text says "permit reuse OR duplicate hash" — the disjunction suggests two distinct failure modes. However, the current ACS treats them as a **conjunction** ("AND," not "OR"): both must be true to permit the transaction.

The manuscript does not explicitly split this into 2 ACS. It presents it as a single risk. However, the observable logic permits a 1→2 decomposition.

**Alternative interpretation:** Permit single-use and transaction novelty are both **idempotency safeguards** that serve the same control purpose (prevent duplicate settlement). Treating them as one atomic idempotency check is reasonable.

**Conclusion:** Can be split, but not mandated by manuscript. Currently justified as 1 ACS; could be expanded to 2 without violation of semantics.

---

### B-06: Receipt Not Committed Between Authorization and Actuation

**Manuscript definition:**
- Event: "receipt not committed between authorization and actuation"
- Observable: receipt_committed_between_authorization_and_actuation
- Consequence class: Statutory record-keeping gap (C*)
- Evidence source: Evidence chain service
- Evaluation basis: Temporal ordering check

**Current ACS:** ACS-B06-01 (receipt_chain_completeness)
```json
{
  "acs_id": "ACS-B06-01",
  "event_type": "receipt_chain_completeness",
  "observable_id": "receipt_committed_between_authorization_and_actuation",
  "decision_semantics": "PERMIT requires authorization_time <= evidence_commit_time < actuation_time"
}
```

**Control requirement atomicity analysis:**

Single temporal ordering condition:
- Requirement: Three timestamps must satisfy: auth ≤ commit < actuation
- Failure: Any temporal inversion (commit before auth, or actuation before/at commit)

**No natural splitting:** Temporal ordering is indivisible. Cannot split into separate authorization vs. commitment vs. actuation checks without losing the **ordering invariant** that enforces evidentiary chain completeness.

**Verdict:** NOT DISTINCT — temporal ordering is atomic.

---

## SUMMARY: DISTINCT CONTROL REQUIREMENTS

| Risk | Current ACS | Atomic/Distinct? | Can split? | Manuscript mandate | Verdict |
|---|---|---|---|---|---|
| B-01 | 1 | Ambiguous (sig verify + hash bind) | Maybe (2 candidates) | No explicit split | Remains 1 (joint observable) |
| B-02 | 1 | Yes (single threshold) | No | No | Remains 1 |
| B-03 | 1 | Yes (single threshold) | No | No | Remains 1 |
| B-04 | 1 | Yes (single lookup) | No | No | Remains 1 |
| B-05 | 1 | Ambiguous (permit single-use + hash novelty) | Yes (2 candidates) | No explicit split | Can be 1 or 2 |
| B-06 | 1 | Yes (single temporal ordering) | No | No | Remains 1 |

---

## ACS CARDINALITY JUSTIFICATION

### Conservative (status quo)
- B-01: 1 ACS (permit binding, joint observable)
- B-02: 1 ACS (amount limit)
- B-03: 1 ACS (velocity bound)
- B-04: 1 ACS (restricted-party screening)
- B-05: 1 ACS (permit single-use AND hash novelty, joint observable)
- B-06: 1 ACS (receipt temporal ordering)
- **Total: 6 ACS**

**Justification:** Each ACS corresponds to a single atomic control requirement identified in the manuscript.

### Optional expansion
- B-05 could be split into:
  - ACS-B05-01: Permit single-use
  - ACS-B05-02: Transaction hash novelty
- **Total: 7 ACS**

**Justification:** The disjunctive risk event ("permit reuse OR duplicate hash") suggests two independent failure modes.

### NOT JUSTIFIED
- **9 ACS distribution (3/2/1/1/1/1):** No manuscript text enumerates 3 distinct control requirements for B-01 or 2 for B-02. The manuscript presents both as single risks with single events.

---

## MANUSCRIPT EVIDENCE REVIEW

### Does the manuscript explicitly state 9 ACS for Case B?

**Search results:**
- PAPER_REQUIREMENTS.md Section 10: "**6 register rows, all runtime**"
- PAPER_REQUIREMENTS.md Section 10: "Because every row carries a mandatory gate, **any threshold `t ≤ 5` reproduces the gate set**, so Case B contains **no Proposition 1 inversion** or Proposition 2 collision and **`GD_min = 0`**."

No mention of 9 ACS. No enumeration of split ACS.

### Origin of 9-ACS requirement

The 9-ACS requirement appears in:
- `docs/MANUSCRIPT_5_5D_DELTA.md` — labeled "Normative from 5.5d" without source section/page reference
- No corresponding manuscript text in PAPER_REQUIREMENTS.md
- No corresponding ACS records in cases/case_b/acs/approved_control_specifications.json (still 6 records)

**Conclusion:** The 9-ACS requirement is an unsourced assertion in the planning document. It does not appear in the extracted manuscript requirements.

---

## FINAL VERDICT

**Scientifically justified Case B ACS cardinality: 6**

- B-01: 1 ACS (defensible; could argue for 2 if signature and binding were decoupled, but manuscript presents as one phenomenon)
- B-02: 1 ACS (single threshold; no decomposition justified)
- B-03: 1 ACS (single velocity threshold; indivisible)
- B-04: 1 ACS (single sanctions screening check)
- B-05: 1 ACS (mandatory joint idempotency check; defensible as 2 if decoupled, but currently justified as 1)
- B-06: 1 ACS (single temporal ordering constraint; indivisible)

**Total: 6 ACS (could defensibly expand to 7 by splitting B-05, but not to 9)**

**Manuscript support for 9 ACS: NONE**

The 9-ACS distribution (3/2/1/1/1/1) is an unsourced requirement that cannot be justified from the extracted manuscript. The distribution appears to be a planning assumption, not a normative requirement.

---

## RECOMMENDATION

### If 9 ACS is a firm requirement:
**Author must provide manuscript text explicitly enumerating which distinct control requirements justify:**
- 3 separate ACS under B-01, AND
- 2 separate ACS under B-02

Until that text exists, the 9-ACS requirement is unsupported and Phase 1 cannot proceed.

### If 6 ACS is the scientifically justified cardinality:
**Revise the 5.5d specification to remove the unsupported 9-ACS requirement.** The general requirement "every runtime ACS emits ≥ 1 predicate" remains valid and can be verified with 6 ACS.

---

## CLAIM BOUNDARY PRESERVATION

This analysis does not introduce or require new research claims. It affirms existing 5.5d normative requirements from Section IV-D (total disposition): 

> "Predicate cardinality is deliberately independent of risk cardinality (0, 1 or several predicates per risk)."

No ACS count constraint is imposed by the manuscript on the Case B instance. The constraint is **only** that every **runtime** ACS (whatever the count) must emit ≥ 1 predicate at compilation.

