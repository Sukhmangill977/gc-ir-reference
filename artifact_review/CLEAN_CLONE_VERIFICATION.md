# Clean-clone verification

Evidence from a **fresh clone of the public repository**, running exactly the
commands an IEEE artifact reviewer is given. Every exit code and timing below was
observed; nothing is estimated.

---

## Environment

| | |
|---|---|
| Date (UTC) | 2026-09-09T05:09:08Z |
| Commit | `b4d7c67c1c17825889fba436fd31c81fade5b21d` |
| Source | `https://github.com/Sukhmangill977/gc-ir-reference.git` (public clone, no local state) |
| Tags present after clone | `preregister-tier0-v2`, `preregister-tier0-v2.1`, `preregister-tier0-v2.2`, `v1.0.0` |
| OS | Darwin 25.6.0 (macOS 26.6.2) |
| Architecture | arm64 |
| Python | CPython 3.11.15 |
| git | 2.50.1 (Apple Git-155) |
| Docker | 29.6.2, build dfc4efb |

The clone was made into an empty temporary directory. No file was copied from the
development checkout.

---

## Host results

| # | Command | Exit | Time | Outcome |
|---|---|---|---|---|
| 1 | `git clone …` | **0** | 59 s | 4 tags fetched, HEAD `b4d7c67` |
| 2 | `make install PYTHON=python3.11` | **0** | 15 s | `.venv` created, pinned dependencies installed |
| 3 | `make test` | **0** | 13 s | **301 passed** |
| 4 | `make verify-hashes` | **0** | <1 s | Both reference hashes **MATCH** |
| 5 | `python tools/freeze_check.py --final-v2` | **0** | 4 s | **FREEZE CHECK PASSED — 24 checks, 0 failures** |
| 6 | `python tools/verify_reported_results.py` | **0** | <1 s | **48/48 paper-facing claims verified, 22 cross-checks passed** |
| 7 | `make ieee-check` | **0** | 16 s | **ALL 8 STAGES PASSED** |

Total from clone to full verification: **under two minutes.**

### Detail worth recording

**`make verify-hashes`** recompiled both cases from the committed governance
artifacts and reproduced:

```
case_a  f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536   MATCH
case_b  2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce   MATCH
```

**`freeze_check.py --final-v2`** verified the Case B → L-DREA mapping against the
external artifact of record: 9 rows, `{exact: 4, family: 3, not_established: 2}`,
0 failures — including the two gaps, which are declared rather than hidden.

**`verify_reported_results.py`** confirmed, among the 22 cross-checks, that
`SNR` and `DF` remain `status=DEFERRED, value=null` for both cases.

---

## Container results

| # | Command | Exit | Time |
|---|---|---|---|
| 8 | `docker build -t gcir .` | **0** | 20 s |
| 9 | `docker run --rm gcir make reproduce` | **0** | 47 s |

**Container environment**, reported by the container itself:

```
Linux-6.12.76-linuxkit-aarch64-with-glibc2.36
aarch64
CPython 3.11.11
```

All eleven reproduction steps completed:

```
OK   1. Regenerate case artifacts and verify the committed tree      0.35 s
OK   2. Compile Case A and Case B                                    0.26 s
OK   3. Test suites (unit, property-based, adversarial, integration) 12.59 s
OK   4. Adversarial corpus, structural checks, validation seeds       4.74 s
OK   5. Traceability audit queries and negative controls              0.46 s
OK   6. Primary metrics                                               0.10 s
OK   7. Gate divergence and Proposition 1/2 premises                  0.69 s
OK   8. Determinism experiment (31 runs per case)                     5.37 s
OK   9. Monte Carlo rating robustness                                22.53 s
OK  10. Hash manifest                                                 0.01 s
OK  11. SUMMARY.md                                                    0.01 s
```

**Values produced inside the container**, from a different OS, libc and
architecture than the host:

```
case_a  f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536
case_b  2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce
TD      1.0   62/62
```

Byte-identical to the committed reference hashes and to the host run. This is a
second architecture (aarch64 Linux, glibc 2.36) reproducing the same canonical
payload hashes as macOS/arm64 — consistent with, and independent of, the eight
environments recorded in `results/final_v2/CI_STATUS.md`.

---

## A defect this test found and its fix

The first clean-clone attempt used the machine's default `python3`, which was
**3.9.6**. `make install` failed with:

```
ERROR: Could not find a version that satisfies the requirement cffi==2.1.1
ERROR: No matching distribution found for cffi==2.1.1
make: *** [install] Error 1
```

That message never mentions the Python version, so a reviewer would have had no
way to diagnose it. A `check-python` guard was added: `make install` now stops
immediately with the interpreter it found and how to override it. Verified in
both directions — exit 2 with a clear message on 3.9.6, exit 0 on 3.11.15. The
run recorded above is from the clone **after** that fix.

This is the reason for running the clean-clone test rather than assuming it
would work.

---

## What this does and does not establish

**Establishes.** The artifact installs, tests, compiles, verifies its frozen
evidence and reproduces its reference hashes from a fresh public clone, on both a
macOS/arm64 host and an aarch64 Linux container, with no hidden local state and
no manual intervention.

**Does not establish.** Platform independence — this is two environments out of
the eight tested, and a finite matrix is not the set of all environments. Nor does
it establish anything about the *content* of the results; it establishes that they
regenerate. What the numbers mean, and what they do not, is in
[`PAPER_TO_ARTIFACT_RESULTS.md`](PAPER_TO_ARTIFACT_RESULTS.md).
