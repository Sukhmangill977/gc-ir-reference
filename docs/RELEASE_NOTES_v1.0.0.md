# GC-IR Reference Implementation v1.0.0

Reference implementation and empirical artifact for **"From Risk Register to
Runtime Predicate: A Deterministic Method for Compiling AI Governance Assessments
into Enforceable Controls"**.

## Verify it in five minutes

```bash
make install && make test && make verify-hashes
```

`make reproduce` runs every non-CI experiment end to end in about 90 seconds and
regenerates `results/final/SUMMARY.md` from the result files.

## Measured results

Executed after the Tier-0 preregistration freeze (`preregister-tier0-v1`), at the
freeze commit, with **zero frozen files changed** in between
(`results/final/freeze_verification.json`).

| | Case A (synthetic) | Case B (forensic reconstruction) |
|---|---|---|
| canonical payload SHA-256 | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| register rows / predicates | 16 / 19 | 6 / 9 |
| DC · RCY · NDR | 1.000 · 0.8125 · 0.1875 | 1.000 · 1.000 · 0.000 |
| OPR · ODC · PTC · CV | 0.000 · 1.000 · 1.000 · 1.000 | 0.000 · 1.000 · 1.000 · 1.000 |
| GD(15) · GD_min | 3 · 3 | 4 · 0 |

* **TD = 1.000 over 60 compilation runs** (30 per case) across object-key and
  array ordering, integer→float re-encoding, five locales, five time zones and
  clean-process execution.
* **Monte Carlo, K = 250,000:** max heat-map flip probability **0.321** (MCSE
  0.001); **`FP^C*` = 0.000**, verified by re-running the consequence-class
  classifier on 1,000 perturbed draws with zero membership changes.
* **Adversarial:** 59/59 (52 negative, 7 positive controls), 24/24 structural
  checks, 3/3 seeded validation rows.
* **Tests:** 275 across four suites; 16 properties over 1,427 generated examples.
* **Traceability:** all six audit queries empty on clean fixtures; all 18 negative
  controls fire.

## What the artifact found

The determinism experiment detected a real defect in the compiler: the bundle
hashed the Control Derivation Catalog *as authored*, so an equivalent catalog
ordering produced a different bundle hash — the ordering dependence Section VI-C
forbids. Fixed before the reportable campaign, with regression tests at the unit
and end-to-end level. Two smaller findings: the compiler's step order did not match
Section VI-A, and audit query Q1 caught an undisposed obligation in the Case B
fixture.

## Declared deviations from the manuscript

* **The Monte Carlo rating distributions are author-specified, not
  panel-adjudicated.** Section XI-G attributes them to the independent adjudication
  panel; no panel has been convened. See `docs/FIXTURE_PROVENANCE.md` FP-020.
* **`GD_min` depends partly on ratings the manuscript does not publish.** The three
  Case A non-runtime rows carry documented fixture ratings; a full sweep shows
  `GD_min` would range over 2–5. See FP-014.

Both are reconciled in `paper_update/PLACEHOLDER_REPLACEMENT_TABLE.md`, with
publication-ready wording in `paper_update/MEASURED_RESULTS.md`.

## Not claimed

RQ5 (comparative superiority) is **preregistered and deferred** — no panel, no
participants, no data; SNR and DF are reported as `DEFERRED`. Cross-platform
determinism is a CI claim measured separately, and the supportable wording is
"deterministic across the tested supported environments", never "platform
independent". No DOI exists yet (`docs/ZENODO_RELEASE_STEPS.md`).

## Contents

GC-IR schemas (13) · `Ψ_K` tooling · `Φ` reference implementation · Control
Derivation Catalogs · Case A and Case B Steps 1–5 inputs, judgment records,
dispositions, ACS, compiled bundles and lifecycle fixtures · traceability queries ·
adversarial corpus · property-based tests · determinism, gate-divergence and Monte
Carlo experiments · the Tier-0 preregistration freeze and the frozen RQ5 protocol.

MIT licence. `MANIFEST.sha256` lists every file with its SHA-256 and Appendix C role.
