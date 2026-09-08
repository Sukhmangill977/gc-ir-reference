# Cross-platform determinism — CI status

**STATUS: CONFIGURED, NOT YET EXECUTED.**

`.github/workflows/determinism.yml` compiles Case A and Case B on
`ubuntu-latest`, `windows-latest` and `macos-latest` under CPython 3.11 and 3.12
— each leg with a different locale and time zone — and compares the resulting
canonical payload hashes against the values committed in
`cases/*/expected/reference_hashes.json`. A second job then asserts that every leg
agreed, via `experiments/check_ci_agreement.py`, and regenerates this file from
the uploaded result artifacts.

**At the time this artifact was assembled, the workflow had not run**, because the
repository had not been pushed to GitHub (the CLI was installed but not
authenticated, and the environment could not run an interactive OAuth flow).

## What this means for the claim

The manuscript's Section XII limitation stands **unchanged**:

> Determinism scope. Environment-independence is measured under the declared
> environment. Determinism testing covers repeated runs, key and row reordering,
> and locale and time-zone variation, but replication across independently
> installed host operating systems is not yet reported; until it is, TD = 1.000
> supports determinism under the declared environment rather than environment
> independence in general.

**Do not upgrade that wording until this file reports actual passing runs.** Even
then, the supportable claim is *"deterministic across the tested supported
environments"* — three runner images are not the set of all environments.

## What has been measured

| | |
|---|---|
| Environment | macOS 26.6.2, arm64, CPython 3.11.15 |
| Runs | 60 (30 per case) |
| TD | 1.000 (60/60) |
| Case A reference hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| Case B reference hash | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |
| Dimensions varied | object-key order, risk/obligation/ACS/disposition/catalog/invariant/authority ordering, integer→float re-encoding, 5 locales, 5 time zones, clean-process execution with varying `PYTHONHASHSEED` |

Evidence: `results/final/determinism_runs.csv`, `determinism_summary.json`.

## To discharge this

```bash
gh auth login                    # once, interactively
git push -u origin main
git push origin --tags
gh workflow run determinism.yml  # or wait for the push-triggered run
```

Then download the run artifacts and regenerate this file:

```bash
gh run download --name 'determinism-*' --dir downloaded
python -m experiments.check_ci_agreement downloaded --out results/final/CI_STATUS.md
```
