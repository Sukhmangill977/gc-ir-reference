# Changelog

All notable changes to this artifact. Format follows Keep a Changelog; the project
uses semantic versioning.

## [1.0.0] — unreleased at time of writing

First public release: the reference implementation and empirical artifact for
"From Risk Register to Runtime Predicate".

### Added — implementation
* RFC 8785 JSON Canonicalization Scheme with ECMAScript `Number::toString`
  formatting and UTF-16 code-unit key ordering.
* GC-IR record family and the closed v1.0 vocabularies (dispositions, evaluation
  bases, gate types and sources, reason codes RC-01/02/03/05, warning code WC-01).
* `Ψ_K` support tooling: validates and assembles signed human selections; performs
  no inference from prose.
* Deterministic compiler `Φ` following the Appendix B pseudocode, with exact
  catalog lookup only.
* Authority closure, `C*` coverage rule CV, explicit precedence, signed lifecycle
  registry with `ValidAt`, temporal traceability with all six audit queries.
* All fourteen Appendix A cross-field constraints as individually testable functions.
* Ed25519 signing with domain separation; the envelope lives outside the hashed payload.

### Added — artifacts
* Case A: synthetic investment-research agent, 16 register rows, 13 runtime /
  3 non-runtime dispositions.
* Case B: forensic-reconstruction transaction-authorization agent, 6 rows.
* 13 JSON Schema documents; two approved catalogs; two invariant registers;
  lifecycle, receipt and actuation fixtures plus per-query negative controls.

### Added — evaluation
* 275 tests across four suites, including a static AST assertion that the compiler
  path imports no RNG, similarity or model library and reads no clock.
* Adversarial corpus of 59 cases (52 negative, 7 positive controls) shared by
  pytest and the experiment runner.
* Property-based suite over synthetic registers, `max_examples = 100`.
* Nine experiments plus one-command reproduction and a generated summary.
* Preregistration freeze material and the frozen, deferred RQ5 protocol.
* Three CI workflows including a cross-platform determinism matrix.

### Fixed during development
* **Determinism defect in `Φ`.** The compiled bundle hashed the Control Derivation
  Catalog as authored, so re-ordering catalog entries — which carries no meaning,
  since entries are addressed by `(event_type, template_id)` — changed the bundle
  hash. Section VI-C requires deterministic array ordering where order is not
  semantically meaningful. `Φ` now hashes a canonical projection of the catalog and
  of the `C*` profile. Found by the determinism experiment, not by inspection.
* **Compiler step order.** Authority closure now runs before template conformance,
  matching the order Section VI-A states.
* **Case B obligation `OSFI-E21-ORR-B` was undisposed.** Found by audit query Q1 on
  the clean fixtures; the register row that bears it now cites it.
* Migrated off the deprecated `jsonschema.RefResolver` to `referencing`.

### Declared deviations from the manuscript
* **Monte Carlo distributions are author-specified, not panel-adjudicated.**
  Section XI-G attributes them to the independent adjudication panel; no panel has
  been convened. Recorded in `docs/FIXTURE_PROVENANCE.md` FP-020 and in the freeze.
* **`GD_min` depends partly on ratings the manuscript does not state.** The three
  Case A non-runtime rows carry fixture ratings; the reported value is accompanied
  by a full sensitivity sweep (FP-014).

### Outstanding
* No Zenodo DOI — see `docs/ZENODO_RELEASE_STEPS.md`.
* Held-out-register hash not committed, because no held-out register has been
  authored — see `preregistration/HELD_OUT_REGISTER.md`.
* RQ5 preregistered and deferred; no participant data exists.
