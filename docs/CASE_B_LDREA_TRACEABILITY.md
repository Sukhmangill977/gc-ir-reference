# Case B → L-DREA traceability

What the mapping in `cases/case_b/ldrea_traceability.json` establishes, what it
does not, and where the artifact-runs memo's description does not match the
published artifact.

**External artifact of record.** `github.com/AGLakhowal/Gamma-Permit-Package` —
the repository the manuscript names in Appendix C for reference [15].
Commit `40fa8f046ad3c6632c66df46abe5500e5dd05696`. No tag is present on that repository, so the commit SHA
is the pin. The relevant subtree is `realdatatestcode/`, exactly as the memo names.

---

## 1. The finding that had to come first: there is no "P1–P13"

The artifact-runs memo asks for "the P1–P13 → artifact-identifier mapping". Before
writing any mapping, the identifiers had to be established from the published
artifact rather than assumed from the memo's wording.
`tools/derive_ldrea_predicate_family.py` does that, from source, and finds:

* **`P1`–`P4` exist, but they are not predicates.** They name four *stress-test
  scenarios* in `realdatatestcode/stress_test.py`: Ghost Treasury Transfer,
  Sanctions Drift Cascade, Multi-Agent Liquidity Panic, Sovereign Cascade Edge
  Case. There is no `P5`, and no `P13`.
* **There is no P1–P13 predicate identifier family anywhere in the artifact.**

**No P1–P13 identifiers were fabricated.** The memo's naming is recorded as a
source inconsistency in `docs/ARTIFACT_RUNS_COMPLIANCE.md`.

## 2. What the L-DREA predicate family actually is

The artifact *does* have a predicate family, and it *does* have thirteen members —
which is very likely what the memo was reaching for. It is derived from
`realdatatestcode/gamma_test_runner.py`, whose own comment reads:

> Node-level authorization predicates. Each must concur (be TRUE) for Gamma_G = 0.
> This is the predicate vector G = {g_1..g_n}; deficit d_i = 1 when g_i fails.

| # | Identifier | Kind |
|---|---|---|
| g1–g7 | `Gate_A1` … `Gate_A7` | node authorization gate |
| g8 | `Lambda_G` | node authorization gate |
| g9 | `TOKEN_VALID` | node authorization gate |
| g10 | `AuthoritySignatureValid` | node authorization gate |
| g11 | `HARM_RISK_THETA` | derived deficit (`HARM_RISK > θ`) |
| g12 | `STALE_CONTEXT` | derived deficit |
| g13 | `TELEMETRY_STALE` | derived deficit (`¬TelemetryFresh`) |

**Ten `NODE_GATE_COLS` + three derived deficit columns = 13.**

This is not an inference. It is corroborated by four independent checks, all of
which pass:

| Cross-check | Expected | Actual |
|---|---|---|
| `benchmark_report.predicate_count` | 13 | 13 |
| `dataset.predicate_dimensionality` | 13 | 13 |
| `negative_control.n_predicates` | 13 | 13 |
| `negative_control.single_deficit_score` = round(1/13, 3) | 0.077 | 0.077 |

and every node-gate identifier appears as a column in the published golden-trace
CSV.

## 3. The mapping

Nine rows — six Case B risk-derived predicates and three compiler invariants.
Grading:

* **`exact`** — the L-DREA artifact evaluates the same condition on the same
  observable, under the same name.
* **`family`** — same predicate family and decision semantics, on a
  domain-specific observable.
* **`not_established`** — no corresponding L-DREA predicate exists; the gap is
  declared.

| GC-IR predicate | Case B risk | ACS | GC-IR family | L-DREA predicate(s) | Grade |
|---|---|---|---|---|---|
| `GCIR-B0001` | B-01 | `ACS-B01-01` | permit binding | `TOKEN_VALID`, `AuthoritySignatureValid` | **exact** |
| `GCIR-B0002` | B-02 | `ACS-B02-01` | bound check on measured value | `Gate_A3`, `HARM_RISK_THETA` | family |
| `GCIR-B0003` | B-03 | `ACS-B03-01` | windowed count bound | — | **not established** |
| `GCIR-B0004` | B-04 | `ACS-B04-01` | restricted-party screening | `Gate_A3` | family |
| `GCIR-B0005` | B-05 | `ACS-B05-01` | permit single-use / replay | `TOKEN_VALID` | **exact** |
| `GCIR-B0006` | B-06 | `ACS-B06-01` | receipt commit-before-actuate | `Gate_A7` | **exact** |
| `GCIR-INV-EVIDENCE-COMMIT` | (INV) | — | receipt commit-before-actuate | `Gate_A7` | **exact** |
| `GCIR-INV-AUTHORITY-CLOSURE` | (INV) | — | authority closure | `AuthoritySignatureValid`, `TOKEN_VALID` | family |
| `GCIR-INV-VERSION` | (INV) | — | version binding | — | **not established** |

**4 exact · 3 family · 2 gaps declared. 0 verification failures.**

Each row is machine-verified before it is written: the `gcir_id` must exist in the
compiled Case B bundle with the stated ACS and origin; every named L-DREA
predicate must be a member of the derived family; and every named observable must
be a real column in the golden-trace header.

### The strongest correspondence

**B-06 / `INV-EVIDENCE-COMMIT` ↔ `Gate_A7` + `CommitBeforeActuate`.** The
manuscript's temporal ordering — `authorization_time ≤ evidence_commit_time <
actuation_time` — is carried in the published artifact as an explicit
`CommitBeforeActuate` column with `HASH_prev`/`HASH_current` chaining and an
`OrderingInversionFlag`. This is the same property, measured, in both layers.

### The two declared gaps

* **B-03 (velocity).** No L-DREA predicate evaluates a rolling per-counterparty
  window count. The artifact's temporal predicates (`STALE_CONTEXT`,
  `TELEMETRY_STALE`) concern evidence *freshness*, not velocity. Mapping B-03 to
  either would have been an approximate neighbour dressed as continuity.
* **`INV-VERSION`.** The artifact records `ModelVersionHash`, `SpecVersion`,
  `DictionaryVersion` and `PolicyHash` as trace columns, but **no member of its
  predicate vector evaluates them**. The observables exist; the predicate does
  not. This is a genuinely interesting gap: it is precisely the per-action
  version-binding check the manuscript argues for in Section III (the Knight
  Capital argument), and the enforcement artifact does not yet implement it.

## 4. Claim boundary — preserved exactly

Manuscript Section X:

> The 284,807-event run reported in [15] is a golden-trace conformance result …
> It is not detection evidence and is not presented as such. What Case B adds for
> this paper is upstream: the register-to-disposition-to-predicate mapping that
> produced those predicate families, previously undocumented.

Accordingly, this mapping establishes **continuity of predicate family** and
nothing else.

**Established.** Four Case B predicate families correspond exactly to named
members of the published L-DREA predicate vector, on the same observables. Two
more correspond by family. The Case B bundle's predicate identifiers resolve to
the `realdatatestcode/` subtree of the repository of record.

**Not established, and not claimed.**

* That the compiled Case B bundle was ever executed against the 284,807-event
  corpus. **It was not.**
* Any detection performance, false-permit rate or unauthorized-execution rate for
  Case B. Those figures belong to [15] and are conformance-class there.
* That the L-DREA artifact implements the Case B register. The direction of the
  reconstruction is the reverse: Case B is a retrospective reconstruction of the
  governance mapping that would have produced predicate families of this shape.

## 5. Reproducing this

```bash
python -m tools.derive_ldrea_predicate_family --ldrea-root <path to Gamma-Permit-Package>
python -m tools.build_ldrea_traceability      --ldrea-root <path to Gamma-Permit-Package>
```

Both scripts fail loudly if the external artifact is absent, if the derived family
size disagrees with any reported count, or if any mapped identifier is not a real
member of the family. Outputs: `cases/case_b/ldrea_predicate_family.json`,
`cases/case_b/ldrea_traceability.json`, both carried in `MANIFEST.sha256` under
role `case_b_input`.
