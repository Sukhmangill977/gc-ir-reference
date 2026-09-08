# GC-IR Reference Implementation v1.0.0

Reference implementation and empirical artifact for **"From Risk Register to
Runtime Predicate: A Deterministic Method for Compiling AI Governance Assessments
into Enforceable Controls"**.

## Verify it in five minutes

```bash
make install && make test && make verify-hashes
python tools/freeze_check.py        # the thirteen frozen numbers, recomputed
python run_all.py                   # every experiment, ~60 s
```

## Public preregistration, discharged

| | |
|---|---|
| Freeze tag | **`preregister-tier0-v2.2`** |
| Freeze commit | `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` |
| Pushed | 2026-09-08T18:01:36Z — **before** the campaign |
| Campaign executed at | the freeze commit itself |
| Frozen files changed in between | **0 of 133** |

The v1 campaign ran after a freeze that was never pushed. It was **not**
relabelled: a later push cannot make a past experiment prospectively
preregistered. It is retained, unedited, in `results/final/`, and
`results/V1_V2_COMPARISON.md` compares the two.

## Measured results (`results/final_v2/`)

| | Case A (synthetic) | Case B (forensic reconstruction) |
|---|---|---|
| canonical payload SHA-256 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| register rows / predicates | 16 / 19 | 6 / 9 |
| DC · RCY · NDR | 1.000 · 0.8125 · 0.1875 | 1.000 · 1.000 · 0.000 |
| OPR · ODC · PTC · CV | 0.000 · 1.000 · 1.000 · 1.000 | 0.000 · 1.000 · 1.000 · 1.000 |
| GD(15) · GD_min | 3 · 3 | 4 · 0 |

* **TD = 1.000 over 62 runs (31 per case)** — the examiner's 10 repeats + 10 row
  shuffles + 5 key shuffles + 3 locales + 3 time zones. Reproduced on **three
  operating systems and two architectures**: macOS/arm64, Ubuntu/x86_64,
  Windows/AMD64 and a Debian container/aarch64, across six CPython versions, every
  one giving identical reference hashes.
* **Monte Carlo, K = 250,000:** max heat-map flip probability **0.321** (MCSE
  0.001); **`FP^C*` = 0.000**, verified on 1,000 re-classified draws.
* **Adversarial:** 62/62 (54 negative, 8 positive controls), 26/26 structural
  checks, 3/3 seeded validation rows.
* **Thirteen Case B injection scenarios:** 13/13 resolve to SAFE_STATE.
* **Tests:** 280; 16 properties over 1,427 generated examples.
* **Traceability:** six audit queries empty; 18/18 negative controls fire.

## Case B → L-DREA traceability

Machine-verified mapping to the published enforcement artifact
(`github.com/AGLakhowal/Gamma-Permit-Package`, commit `40fa8f0`, subtree
`realdatatestcode/`).

The artifact-runs memo asks for a "P1–P13" mapping. **No such family exists
there**: `P1`–`P4` are stress-test *scenarios*, not predicates. The real predicate
family has thirteen members — `Gate_A1`…`Gate_A7`, `Lambda_G`, `TOKEN_VALID`,
`AuthoritySignatureValid`, `HARM_RISK_THETA`, `STALE_CONTEXT`, `TELEMETRY_STALE` —
derived from that artifact's source and corroborated by three independent counts
and by its own single-deficit score of 1/13. **No identifiers were fabricated.**

Result: **4 exact correspondences, 3 by family, 2 declared gaps**, 0 verification
failures. Establishes continuity of predicate family only — not detection
performance, and the Case B bundle was never run against the 284,807-event corpus.

## What the artifact found

* A real determinism defect in `Φ`: the bundle hashed the derivation catalog *as
  authored*, so an equivalent ordering changed the bundle hash.
* The step harness ignored return codes, so a failing experiment would have
  reported OK — found by a dry run before the campaign, and fixed under an
  incremented freeze rather than patched in place.
* Audit query Q1 caught an undisposed obligation in the Case B fixture.

## Declared deviations from the manuscript

* **Monte Carlo distributions are author-specified, not panel-adjudicated.**
  Section XI-G attributes them to an adjudication panel; none has been convened.
* **`GD_min` depends partly on ratings the manuscript does not publish.** A full
  sweep shows it would range 2–5; the three fixture ratings must be printed.
* **Schema stays at v1.0.** The memo's "v1.1" has no manuscript basis and no
  revision was made.
* **No Case C.** The manuscript defines Cases A and B only; the memo's "nineteen
  Case C scenarios" has no basis in the manuscript or the referenced artifact.

All reconciled in `paper_update/`, with publication-ready wording.

## Not claimed

RQ5 is **preregistered and deferred** — no panel, no participants, no data; SNR
and DF report `DEFERRED`. Determinism is claimed across the *tested* environments,
never as platform independence. No DOI exists (`docs/ZENODO_RELEASE_STEPS.md`).

MIT licence. `MANIFEST.sha256` lists every file with its SHA-256 and Appendix C role.
