# Case B / L-DREA / ULB: pinned-artifact reproduction and v1.1 replay assessment

**Status: development evidence, generated this session by direct execution
against the pinned downstream artifact. Not part of any frozen
`preregister-tier0-v3.1` evidence, which this document never reads from or
writes to.**

## 1. The pinned downstream artifact

Per `cases/case_b/ldrea_traceability.json` (already committed, prior
generation):

| Field | Value |
|---|---|
| Repository | `https://github.com/AGLakhowal/Gamma-Permit-Package.git` |
| Local checkout | `/Users/sukhmangill/Documents/GitHub/Gamma-Permit-Package` |
| Pinned commit | `40fa8f046ad3c6632c66df46abe5500e5dd05696` |
| Artifact subtree | `realdatatestcode/` |
| Role | enforcement layer, manuscript reference [15] |

Verified this session: the local checkout's `git rev-parse HEAD` equals the
pinned commit exactly, and `git status` is clean (no local modification).
This is a genuine pin, not a guess.

## 2. Original 284,807-row L-DREA experiment: reproduced, unchanged

The raw ULB dataset lives in a separate, sibling local repository,
`/Users/sukhmangill/Documents/GitHub/carddataset` (its own git checkout; not
itself named in `ldrea_traceability.json`, which only pins the enforcement
code, not the data repository — the data's identity is verified directly
below instead of assumed):

- `creditcard.csv`: 284,808 lines (284,807 data rows + 1 header). Column
  header exactly `Time,V1,...,V28,Amount,Class` — the canonical public
  ULB/Worldline "Credit Card Fraud Detection" schema.
- `Class` distribution: **284,315 rows `Class=0`, 492 rows `Class=1`** —
  counted directly with `awk`, not read from a report. This matches exactly
  the historical figures the runbook cited (284,807 transactions, 492
  fraud-labelled).
- `gamma_test_runner.py` and `gamma_summary.json` are **byte-identical**
  between the pinned `Gamma-Permit-Package/realdatatestcode/` checkout and
  the `carddataset` repository's own copies (`diff` exit 0 on both) — the
  code that produced the committed report is the same code pinned in the
  manuscript's repository of record.

**Fresh re-execution this session** (not a read of the committed report):

```
python3 gamma_test_runner.py --input GAMMA_G0_CREDITCARD_FULL_mapped.csv \
  --no-html --no-replay-manifest
```

Result, diffed against the committed `carddataset/gamma_summary.json`:
identical on every field except the recorded `input_file` path string
(relative vs. absolute — a cosmetic artifact of the two invocations'
respective working directories, not a result value). In particular:

| Metric | Committed | Reproduced this session |
|---|---|---|
| rows | 284,807 | 284,807 |
| derived_permit | 284,315 | 284,315 |
| derived_safe_state | 492 | 492 |
| false_permit_count | 0 | 0 |
| false_denial_count | 0 | 0 |
| unauthorized_execution_count | 0 | 0 |
| decision agreement vs. Status/SAFE_STATE/ACT_PERMIT | 100% | 100% |
| top rule failures (all 492 adversarial rows) | Gate_A3, Gate_A7, Lambda_G, HARM_RISK_THETA | same |

**Verdict: the original L-DREA experiment reproduces exactly, unmodified.**
Its code and results were not altered to fit GC-IR v1.1.

## 3. What this experiment actually is (read directly from its own mapping code)

`gamma_map_raw.py` (the script that builds `GAMMA_G0_CREDITCARD_FULL_mapped.csv`
from raw `creditcard.csv`) states its own construction in its docstring and
enforces it in code:

```
GROUND TRUTH is the real `Class` column (0 = legitimate, 1 = fraud).
Class == 1  -> HARM_RISK high, Gate_A3 & Gate_A7 & Lambda_G fail,
Class == 0  -> all gates pass, Gamma = 0, PERMIT (actuated)
...
row["TOKEN_VALID"] = True
row["AuthoritySignatureValid"] = True
```

This confirms, from the pinned artifact's own code (not inferred), exactly
what `cases/case_b/ldrea_traceability.json`'s `claim_boundary` already says:
this is a **golden-trace conformance demonstration** — gate outcomes are
constructed from the `Class` label to prove the enforcement pipeline
mechanically reaches `SAFE_STATE` for 100% of labelled-adversarial rows and
`PERMIT` for 100% of labelled-nominal rows — not an independent detection
signal evaluated against real permit/authority/ordering evidence. Two
concrete consequences for any downstream replay:

- `TOKEN_VALID` / `AuthoritySignatureValid` (→ Case B's `ACS-B01-01` permit
  binding, `ACS-B05-01` replay/single-use, and `GCIR-INV-AUTHORITY-CLOSURE`)
  are **declared constant `True` for every row**, independent of `Class`.
  This is precisely the "hold a governance field at a declared deterministic
  conformant value" pattern — already how the *original, frozen* experiment
  itself treats these fields, not a new invention for this session.
- `Gate_A3` / `Gate_A7` / `HARM_RISK_THETA` / `Lambda_G` (→ Case B's
  `ACS-B02-01` bound check, `ACS-B04-01` restricted-party screening,
  `ACS-B06-01` / `GCIR-INV-EVIDENCE-COMMIT` receipt ordering) **are
  synthetically derived from `Class` in the original experiment** — this is
  the "genuinely part of the prior frozen experiment" case the runbook's
  strict rule allows reusing unchanged, since it is not a new derivation
  introduced here.

## 4. GC-IR → downstream predicate-family correspondence

Unchanged from the prior generation's work, re-verified against the pinned
commit above:

- Historical Case B (6 ACS + 3 compiler invariants, 9 rows):
  `cases/case_b/ldrea_traceability.json` — **4 exact, 3 family,
  2 not_established**.
- Case B v1.1's 3 new ACS (`ACS-B01-02`, `ACS-B01-03`, `ACS-B02-02`):
  `cases/case_b_v1_1/ldrea_traceability_v1_1_addendum.json` — **0 exact,
  0 family, 3 not_established**. Correctly so: the confirmed 13-member
  predicate family (`Gate_A1..A7, Lambda_G, TOKEN_VALID,
  AuthoritySignatureValid, HARM_RISK_THETA, STALE_CONTEXT, TELEMETRY_STALE`)
  contains no prohibited-class lookup, no human-attestation/concurrence
  predicate, and no two-tier delegated-escalation structure — these three
  v1.1 mechanisms did not exist in the frozen v1.0-era enforcement artifact's
  evaluation surface by construction. This was **not** converted to
  `family` on the basis of loose conceptual similarity.
- Combined Case B v1.1 (12 predicates total): **4 exact, 3 family,
  5 not_established**.

No `P1`-`P13` predicate-identifier family exists in the pinned artifact —
`P1`-`P4` name four stress-test *scenarios* in `stress_test.py`, not
predicates (already documented; not repeated here as a new finding).

## 5. Section E: was a new Case B v1.1 (12-predicate) ULB replay attempted?

**Assessed and deliberately not executed. This is a reasoned decision, not
an omission.**

The runbook's strict rule forbids deriving governance evidence (permit
validity, approval attestation, policy class, revocation state, producer
authority, state-binding evidence) from the dataset's fraud label unless
that is genuinely part of the prior frozen experiment, and offers two
options when v1.1 predicates need fields the ULB corpus does not carry:
either (1) hold them at a declared deterministic conformant value in an
explicitly-labelled hybrid replay, or (2) exercise them separately through
the existing injection/fixture harness.

Classifying all 12 Case B v1.1 predicates by what the mapped corpus actually
supports (Section 3 above, plus the correspondence tables in Section 4):

| Predicate | Corpus support |
|---|---|
| `ACS-B01-01` (permit binding) | declared-conformant `TOKEN_VALID`/`AuthoritySignatureValid` — **from the original experiment**, reusable unchanged |
| `ACS-B02-01` (bound check) | `Gate_A3`/`HARM_RISK_THETA`, synthetically Class-derived **in the original experiment** — reusable unchanged, family-level |
| `ACS-B04-01` (restricted-party screening) | `Gate_A3` reused (same column as B-02, an acknowledged pre-existing ambiguity in the historical mapping, not introduced here) |
| `ACS-B05-01` (replay/single-use) | declared-conformant `TOKEN_VALID` — reusable unchanged |
| `ACS-B06-01` + `GCIR-INV-EVIDENCE-COMMIT` (receipt ordering) | `Gate_A7`/`CommitBeforeActuate`, Class-derived in the original — reusable unchanged |
| `GCIR-INV-AUTHORITY-CLOSURE` | declared-conformant, family-level, reusable unchanged |
| `ACS-B03-01` (windowed-count velocity) | **no field of any kind** — the 112-column mapped schema has no counterparty identifier to window over |
| `ACS-B01-02` (prohibited-class lookup) | **no field of any kind** |
| `ACS-B01-03` (enhanced-approval concurrence) | **no field of any kind** |
| `ACS-B02-02` (delegated escalation tier) | **no field of any kind** |

Four of the twelve predicates (`ACS-B03-01` and all three new v1.1 ACS) have
**zero linkage to the ULB corpus, not even at "family" correspondence**.
A hybrid replay could only represent them by declaring a single hard-coded
constant outcome for all 284,807 rows, with no row ever varying — which is
not "holding a governance field at a value the golden trace already
declares" (as `TOKEN_VALID=True` legitimately is), it would be a new
constant invented solely to make the replay run, contributing zero
information and never able to flip any row's decision.

Running the full 12-predicate bundle over the corpus under those four
constants would therefore produce **exactly the same 492-`SAFE_STATE` /
284,315-`PERMIT` split as the existing 9-row historical predicate-family
continuity check already shows** — it would not exercise anything new about
the v1.1 bundle's actual contribution (the three new ACS and the velocity
check), because those are precisely the four predicates held constant. The
replay would look like new evidence while adding none.

**Decision: do not force it.** Per the runbook's own explicit permission for
this outcome, this is reported as the cleaner alternative:

1. The original 284,807-row L-DREA experiment is reproduced, unchanged
   (Section 2).
2. GC-IR → downstream predicate-family correspondence is verified for all 12
   Case B v1.1 predicates, honestly classified exact/family/not_established,
   with no conversions to inflate the mapping (Section 4).
3. The three new v1.1 governance-only predicates are validated separately,
   on their own real semantics, by the native provenance verifier
   (`src/gcir/provenance.py`, 11 tests) and the 13-scenario injection harness
   (`experiments/case_b_v11_injection_scenarios.py`) — which *do* exercise
   real state transitions for these predicates, unlike a padded ULB replay
   would.

**No fraud-detection accuracy claim is made anywhere in this document or by
this session's work.** The 284,807-row figures above are golden-trace
conformance evidence for the *original* pinned artifact, exactly as
`cases/case_b/ldrea_traceability.json`'s `claim_boundary` already states;
Case B v1.1's contribution is upstream register-to-disposition-to-predicate
reconstruction and governance provenance, verified on its own terms.
