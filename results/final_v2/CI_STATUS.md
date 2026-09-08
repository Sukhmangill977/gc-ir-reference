# Cross-platform determinism — MEASURED

Generated from real GitHub Actions run artifacts by
`experiments/check_ci_agreement.py`. Run:
<https://github.com/Sukhmangill977/gc-ir-reference/actions/runs/34261657261>

## Result

**TD = 1.000 on every environment, with byte-identical reference canonical
payload hashes: 6 CI legs plus two local environments.**

| Environment | OS | Arch | CPython | Runs | TD | Case A | Case B |
|---|---|---|---|---|---|---|---|
| local host | macOS 26.6.2 | arm64 | 3.11.15 | 62 | **1.0** | match | match |
| pinned container | Linux-6.12.76-linuxkit-aarch64 | aarch64 | 3.11.11 | 62 | **1.0** | match | match |
| CI `macos-latest-py3.11` | macOS-26.6.2-arm64-arm-64bit | arm64 | 3.11.9 | 62 | **1.0** | match | match |
| CI `macos-latest-py3.12` | macOS-26.6.2-arm64-arm-64bit | arm64 | 3.12.10 | 62 | **1.0** | match | match |
| CI `ubuntu-latest-py3.11` | Linux-6.17.0-1022-azure-x86_64 | x86_64 | 3.11.16 | 62 | **1.0** | match | match |
| CI `ubuntu-latest-py3.12` | Linux-6.17.0-1022-azure-x86_64 | x86_64 | 3.12.14 | 62 | **1.0** | match | match |
| CI `windows-latest-py3.11` | Windows-10-10.0.26100-SP0 | AMD64 | 3.11.9 | 62 | **1.0** | match | match |
| CI `windows-latest-py3.12` | Windows-2025Server-10.0.26100-SP0 | AMD64 | 3.12.10 | 62 | **1.0** | match | match |

Reference hashes, identical everywhere:

| Case | canonical payload SHA-256 |
|---|---|
| A | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` |
| B | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` |

All legs ran the frozen stratified matrix: {"key_shuffle": 5, "locale": 3, "repeat": 10, "row_shuffle": 10, "timezone": 3}.

## Coverage achieved

| Dimension | Values exercised |
|---|---|
| Operating systems | **3** — macOS 26.6.2, Linux (Ubuntu 6.17 / glibc 2.39, and Debian bookworm / glibc 2.36 in the container), Windows 10.0.26100 |
| Architectures | **2** — arm64/aarch64 and x86_64/AMD64 |
| CPython versions | **6** — 3.11.9, 3.11.11, 3.11.15, 3.11.16, 3.12.10, 3.12.14 |
| Locales | C, C.UTF-8, en_US, de_DE, tr_TR, ja_JP |
| Time zones | UTC, America/Edmonton, Asia/Kolkata, Pacific/Chatham, Europe/Berlin |
| Total compilations | **496** across all environments |

## Wording this licenses

> Translation determinism was measured as TD = 1.000 over 62 compilation runs
> (31 per case) on each of 8 independently provisioned environments spanning
> three operating systems, two machine architectures and six CPython patch
> versions, all reproducing the committed reference canonical payload hashes
> exactly.

**Still not licensed:** *platform independence*. Three operating systems and
two architectures are not the set of all environments. The supportable claim
remains **deterministic across the tested supported environments** — which is
now a substantially wider set than the manuscript's current "inside the pinned
reproducible container".

## Reproduce

```bash
gh run download <run id> --dir downloaded
python -m experiments.check_ci_agreement downloaded --out CI_STATUS.md
```
