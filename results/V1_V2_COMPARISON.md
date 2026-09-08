# v1 vs v2 campaign comparison

Two complete reportable campaigns were executed.

| | v1 | v2 |
|---|---|---|
| Results | `results/final/` | `results/final_v2/` |
| Freeze | `preregister-tier0-v1` | `preregister-tier0-v2.1` |
| Freeze was public **at execution time** | **No** — local tag only | **Yes** — pushed and remote-verified first |
| Determinism runs | 30 per case (60) | 31 per case (62) |
| Reportable | **No** — superseded | **Yes** |

**Why v1 is not reported.** Its freeze was never pushed before the campaign ran. A later push cannot convert a past experiment into a prospectively public preregistered one, so v1 was superseded rather than relabelled. Its files are retained unedited; its metadata was not altered and `public_commitment_discharged` was not flipped retroactively.

---

## Value-by-value

| Quantity | v1 | v2 | Same? | Explanation |
|---|---|---|---|---|
| case_a canonical payload hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | yes | identical |
| case_a predicate count | `19` | `19` | yes | identical |
| case_b canonical payload hash | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | yes | identical |
| case_b predicate count | `9` | `9` | yes | identical |
| case_a DC | `1.000000` | `1.000000` | yes | identical |
| case_a RCY | `0.812500` | `0.812500` | yes | identical |
| case_a NDR | `0.187500` | `0.187500` | yes | identical |
| case_a OPR | `0.000000` | `0.000000` | yes | identical |
| case_a ODC | `1.000000` | `1.000000` | yes | identical |
| case_a PTC | `1.000000` | `1.000000` | yes | identical |
| case_a CV | `1.000000` | `1.000000` | yes | identical |
| case_a GD(T_H) | `3` | `3` | yes | identical |
| case_a GD_min | `3` | `3` | yes | identical |
| case_b DC | `1.000000` | `1.000000` | yes | identical |
| case_b RCY | `1.000000` | `1.000000` | yes | identical |
| case_b NDR | `0.000000` | `0.000000` | yes | identical |
| case_b OPR | `0.000000` | `0.000000` | yes | identical |
| case_b ODC | `1.000000` | `1.000000` | yes | identical |
| case_b PTC | `1.000000` | `1.000000` | yes | identical |
| case_b CV | `1.000000` | `1.000000` | yes | identical |
| case_b GD(T_H) | `4` | `4` | yes | identical |
| case_b GD_min | `0` | `0` | yes | identical |
| TD value | `1.000000` | `1.000000` | yes | identical |
| TD numerator | `60` | `62` | **no** | v1 ran 30 runs per case (60); v2 runs the examiner's stratified 31 per case (62). |
| TD denominator | `60` | `62` | **no** | v1 ran 30 runs per case (60); v2 runs the examiner's stratified 31 per case (62). |
| determinism runs per case | `30` | `31` | **no** | 30 -> 31, per the artifact-runs memo's 10+10+5+3+3 breakdown. |
| case_a determinism reference hash | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | `f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536` | yes | identical |
| case_b determinism reference hash | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | `2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce` | yes | identical |
| case_a Monte Carlo K | `250000` | `250000` | yes | identical |
| case_a max FP^heat | `0.321268` | `0.321268` | yes | identical |
| case_a max FP^C* | `0.000000` | `0.000000` | yes | identical |
| case_b Monte Carlo K | `250000` | `250000` | yes | identical |
| case_b max FP^heat | `0.317980` | `0.317980` | yes | identical |
| case_b max FP^C* | `0.000000` | `0.000000` | yes | identical |
| adversarial corpus size | `59` | `62` | **no** | v1 had 59 cases; v2 adds ADV-055, ADV-056 (the timeout class) and POS-006, giving 62. |
| adversarial failures | `0` | `0` | yes | identical |
| adversarial code mismatches | `0` | `0` | yes | identical |
| structural checks passed | `24` | `26` | **no** | v1 had 24; v2 adds the omitted-mandatory-predicate direction of state mismatch, giving 26. |
| Case B injection scenarios | `—` | `13` | **no** | new in v2; absent from v1. |
| tests total | `275` | `280` | **no** | v2 adds the timeout adversarial cases to the parametrised suite. |
| tests failed | `0` | `0` | yes | identical |
| properties | `16` | `16` | yes | identical |
| generated examples | `1427` | `1427` | yes | identical |
| traceability clean queries empty | `True` | `True` | yes | identical |
| traceability controls all detected | `True` | `True` | yes | identical |

## Summary

| | Count |
|---|---|
| Quantities compared | 45 |
| Identical | 38 |
| Differing, with a stated reason | 7 |
| **Differing, unexplained** | **0** |

**Every difference between the two campaigns has a stated cause, and every substantive measured value is identical.** The bundle hashes, all seven per-case metrics, GD, GD_min, TD = 1.000, the Monte Carlo flip probabilities and the traceability outcomes are unchanged; what changed is the number of determinism runs, the size of the adversarial corpus, and the addition of the Case B injection scenarios — all of them deliberate scope increases made *before* the v2 freeze.

That the measured values are identical across two independently executed campaigns, at different corpus sizes and run counts, is itself corroboration: the numbers are properties of the artifacts, not of a particular execution.
