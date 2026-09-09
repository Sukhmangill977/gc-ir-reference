# v1.0.3

v1.0.3 contains presentation and reviewer-usability improvements only:
terminal result display, auto-generated README measured-results table, and
staleness verification. The scientific Tier-0 v2.2 campaign, frozen code,
inputs and results are unchanged.

- `make results` prints the complete machine-derived report; `--json` uses the same loader.
- `make readme-results` updates only the marked README block; `make verify-readme-results` checks without writing. CI rejects stale results.
- Source provenance and temporary-copy corruption tests audit the presentation layer.
- The manuscript release references change from v1.0.2 to v1.0.3 only. No empirical number or scientific claim changes.

Scientific freeze: `preregister-tier0-v2.2`. Authoritative evidence: `results/final_v2/`.
Previous releases and the freeze tag remain immutable. Deposit v1.0.3 on Zenodo after the release gate passes.
