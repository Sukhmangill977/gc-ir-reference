# Cross-environment determinism — measured status

Two distinct claims, with two very different amounts of evidence behind them.

---

## 1. Two independently installed operating systems — **MEASURED**

The determinism experiment has been executed to completion on two different
operating systems, with two different CPython patch versions, and both reproduce
the committed reference canonical payload hashes exactly.

| | Host | Pinned container |
|---|---|---|
| Operating system | macOS 26.6.2 | Linux 6.12.76 (Debian bookworm, glibc 2.36) |
| Architecture | arm64 | aarch64 |
| CPython | 3.11.15 | 3.11.11 |
| Baseline locale / TZ | inherited from the host | `C.UTF-8` / `UTC` |
| Runs | 60 (30 per case) | 60 (30 per case) |
| **TD** | **1.000 (60/60)** | **1.000 (60/60)** |
| Case A reference hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | *identical* |
| Case B reference hash | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | *identical* |

Both runs additionally varied, within themselves, five locales
(C, en_US.UTF-8, de_DE.UTF-8, tr_TR.UTF-8, ja_JP.UTF-8), five time zones
(UTC, America/Edmonton, Asia/Kolkata, Pacific/Chatham, Europe/Berlin),
object-key ordering, every semantically unordered array's ordering,
integer→float re-encoding, and clean-process execution under varying
`PYTHONHASHSEED`.

**Evidence**

* Host: `results/final/determinism_summary.json`, `determinism_runs.csv`
* Container: `results/final/cross_environment/determinism_summary_container_linux.json`,
  `determinism_runs_container_linux.csv`
* Container image id: `sha256:4900d778ea34b3f1882a5da9fd6971862d6fb040e6d2251c12264936e25a75d4`
  (built from the `Dockerfile`, whose base image is pinned by digest)

**Reproduce it**

```bash
make docker-build
docker run --rm gcir python -m experiments.verify_hashes
docker run --rm gcir python -m experiments.run_determinism --runs-per-case 30
```

**What this licenses.** The compiler produces identical canonical payload hashes
on macOS/arm64 and on Linux/aarch64 under two CPython patch versions. That is
genuine cross-operating-system evidence, and it is stronger than the manuscript's
current "inside the pinned reproducible container" statement, which describes only
one environment.

**What it does not license.** Two operating systems on one machine architecture is
not platform independence. Windows is untested. x86-64 is untested. Other CPython
implementations are untested.

---

## 2. The full CI matrix — **CONFIGURED, NOT YET EXECUTED**

`.github/workflows/determinism.yml` compiles both cases on `ubuntu-latest`,
`windows-latest` and `macos-latest` under CPython 3.11 and 3.12 — each leg with a
different locale and time zone — and a second job asserts every leg agreed with
the committed reference hashes.

**It has not run**, because the repository has not been pushed to GitHub: the
GitHub CLI was installed but not authenticated, and the environment could not run
an interactive OAuth flow.

Until it does, **Windows and x86-64 remain untested**, and no claim covering them
may be made.

### To discharge it

```bash
gh auth login                    # once, interactively
bash tools/publish.sh            # pushes main + the freeze tag, creates the release
# then, once the workflow finishes:
gh run download --name 'determinism-*' --dir downloaded
python -m experiments.check_ci_agreement downloaded --out results/final/CI_STATUS.md
```

---

## Wording the evidence supports

**Now, on the strength of section 1:**

> Translation determinism was measured as TD = 1.000 over 60 compilation runs on
> each of two independently installed operating systems — macOS 26.6.2 (arm64,
> CPython 3.11.15) and a pinned Debian-based container (Linux 6.12, aarch64,
> CPython 3.11.11) — with both reproducing the committed reference canonical
> payload hashes exactly, across five locales, five time zones, input permutation
> and clean-process execution.

**Only after section 2 passes:**

> …deterministic across the tested supported environments.

**Never, on any evidence in this artifact:**

> …platform independent.
