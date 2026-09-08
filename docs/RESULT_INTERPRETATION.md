# RESULT_INTERPRETATION.md

What each measured result means, and — more importantly — what it does not.

The manuscript's own claim boundary (Sections I-D, XII, XIV) is the governing
document. This file applies it to the specific numbers this artifact produces, so
that a number cannot be lifted out of `SUMMARY.md` and used to support something it
does not support.

---

## Evidence classes used here

| Class | Meaning | Where it appears |
|---|---|---|
| **Formally derived** | Proved in the manuscript; the artifact checks that the pinned data instantiates the premise. | Propositions 1–3 |
| **Synthetic case fixture** | Fully specified, reproducible, not a deployed system. | Case A |
| **Forensic reconstruction** | A retrospective mapping, pinned so it is reproducible going forward. | Case B |
| **Author-operated measurement (C1)** | Measured by the author under declared conditions. | DC, RCY, NDR, OPR, ODC, PTC, CV, TD, GD, GD_min, Monte Carlo, adversarial, property, traceability |
| **Cross-platform conformance (C2)** | A conformance run against a declared, versioned profile with reported bounds. | CI determinism matrix |
| **Deferred human study** | Preregistered, not executed, no data. | RQ5: SNR, DF |

Per Section XI-I, **no C3 (independently verified) or C4 (consensus-bound) claim is
made anywhere in this artifact.**

---

## Metric by metric

### DC = 1.000 — disposition completeness
**Means.** Every register row carries exactly one runtime, non-runtime or accepted
disposition, so the bundle is release-admissible.

**Does not mean.** That any disposition is *correct*. `DC` is a completeness
property of the record, not a quality property of the judgment. The manuscript is
explicit that "`DC = 1` by construction once dispositions are signed" — what the
artifact adds is that the construction is mechanically enforced and that a bundle
with a missing, duplicated or unresolved disposition is rejected (ADV-006, ADV-007,
ADV-008).

### RCY = 0.8125 (Case A) — runtime compilability yield
**Means.** 13 of 16 rows yielded runtime predicates.

**Does not mean.** Anything about quality. The manuscript: "RCY is descriptive, not
a quality target; forcing it toward 1 would incorrectly encourage non-runtime risks
to be translated into unsuitable predicates." A higher RCY is not a better result.
Case B's `RCY = 1.000` reflects a register every row of which happens to have an
authorization-time observable, not a better translation.

### OPR = 0.000 — orphan predicate rate
**Means.** Within `Φ`-produced bundles, every predicate resolves to a register row
or to an approved invariant in `INV`.

**Does not mean.** That a deployment has no orphan controls. This is a **compiler
guarantee**, and Section VI-F states the condition under which it extends to a
deployment: the runtime authority loads only bundles verifying as signed `Φ`
outputs and accepts no policy content through any other channel. Where an operator
can inject controls through a separate channel, the guarantee stays scoped to the
compiled bundle. The artifact tests both sides
(`check_runtime_acceptance`, structural checks 8–10).

### ODC = 1.000 and PTC = 1.000
**Means.** Every obligation is traceable to an approved disposition, and every
predicate to a risk or a compiler invariant.

**Does not mean.** That every obligation is *satisfied*. Section VIII:
"Traceability completeness does not require every obligation to produce a
predicate." An obligation discharged by a non-runtime disposition counts as
disposed — that is the method working correctly, not a gap.

### CV = 1.000 — C* coverage
**Means.** Every `C*`-classified risk has at least one decisive mandatory gate over
each of its authorized hazardous action paths, and `Φ` rejects bundles where it does
not (ADV-041 through ADV-044).

**Does not mean.** That the `C*` classification itself is right. `C*` membership is
a governance judgment; the method makes it explicit, materiality-qualified and
auditable — not automatic (Section XII).

### TD = 1.000 over 60 runs
**Means.** Across 30 permutations per case — key ordering, row ordering, catalog
ordering, numeric re-encoding, five locales, five time zones, and clean-process
execution with varying `PYTHONHASHSEED` — every compilation produced that case's
reference canonical payload hash.

**Does not mean.**
* **Not** platform independence. This ran on one host operating system. The
  cross-platform question is answered by the CI matrix, separately, and the
  supportable wording is "deterministic across the tested supported environments".
* **Not** that signature bytes are reproducible. `TD` is a property of the canonical
  payload hash; the envelope carries signing time and key identity and is expected
  to differ (Section VI-C).
* **Not** that human refinement is deterministic. `Φ` is deterministic *after*
  approved inputs are fixed; `Ψ_K` is single-valued only given the signed judgment
  record `J`.

**Worth stating plainly:** this experiment earned its keep. It found a real defect —
the bundle hashed the catalog as authored, so re-ordering catalog entries changed
the bundle hash. That is exactly the ordering dependence Section VI-C forbids, and
it would not have surfaced from repeated identical runs.

### GD(15) = 3 and GD_min = 3 (Case A)
**Means.** Against the enterprise's predeclared threshold, three rows diverge —
R-09, R-10 and R-13 carry mandatory gates by class while scoring below 15 — and no
scalar threshold reproduces the approved assignment more closely than the declared
one.

**Carries a caveat.** Both sums run over all sixteen rows, including three
non-runtime rows whose `L × I` the manuscript does not state. Those are documented
fixtures (FP-014), and the sensitivity sweep shows `GD_min` would range over **2 to
5** across all plausible ratings for them. `GD(15) = 3` is *not* sensitive to that
choice, and neither proposition premise depends on it. The honest report states
`GD_min = 3` **together with the three ratings that produce it.**

**Does not mean.** That the propositions are proved by measurement. They are proved
analytically in the manuscript. What is measured is that this register instantiates
their premises: six inverted pairs, and a three-way collision at `s = 12` where
R-09 is gated while R-04, R-12 and R-14 are not.

### Case B GD_min = 0
**Means.** Every Case B row carries a mandatory gate, so any threshold `t ≤ 5`
reproduces the gate set. Confirmed at every one of 250,000 Monte Carlo draws.

**Does not mean.** That Case B undermines the separation results. Section X says so
directly: Case B "is not used by itself to establish `GD_min > 0`. The separation
results rest on Case A; Case B contributes gate-source diversity and the domain
where enforcement-layer evidence exists."

### Monte Carlo: max FP^heat ≈ 0.321, FP^C* = 0.000
**Means.** Under the declared ±1 ordinal perturbation, heat-map gate membership for
the most threshold-adjacent row flips with probability about 0.32, while `C*`
membership does not move at all — verified by re-running the real classifier on
1,000 perturbed draws per case, with zero changes observed.

**Does not mean.**
* **Not** an estimate of real rating uncertainty. It is a sensitivity analysis under
  a perturbation model the author specified.
* **Not** an independently adjudicated result. **No adjudication panel has been
  convened.** The manuscript's Section XI-G attributes the distributions to the
  panel; that attribution must change. See FP-020 and
  `paper_update/MEASURED_RESULTS.md`.
* **Not** an estimate of real-world event frequencies or harm probabilities
  (Section XII, "Monte Carlo scope").

`FP^{C*} = 0` is structural — the coverage rule reads the consequence descriptor and
never reads `L` or `I`. The experiment verifies the structure rather than assuming it.

### Adversarial: 59/59, structural checks 20/20, seeds 3/3
**Means.** Every mutation in the corpus produced the outcome its manuscript
requirement predicts, with an expected error code; every positive control still
compiled.

**Does not mean.** Completeness over the space of possible defects. The corpus
covers the failure classes Section XI-H enumerates plus the ones the schema and
Appendix A imply. It is a finite list of known failure modes, not a proof of
robustness.

### Property tests: 16 properties, 1,427 generated examples
**Means.** The seven properties Section XI-H names, plus four more, held over
generated synthetic registers.

**Does not mean.** A proof. Hypothesis samples; it does not verify. The two
properties whose input spaces it *exhausts* (18 and 9 examples) are the exception —
those are complete over their finite domains.

### Traceability: all six queries empty, 18/18 negative controls detected
**Means.** No orphan or temporally invalid link exists in the committed fixtures,
and each query demonstrably fires on the violation it exists to detect.

**Does not mean.** Legal compliance, semantic correctness, or control effectiveness.
Section VIII says this in as many words, and the artifact repeats it in the result
file rather than leaving it to the reader.

---

## Claims this artifact cannot support, and must never be read as supporting

| Not supported | Why |
|---|---|
| Comparative superiority over unaided manual practice | RQ5 is preregistered and **deferred**. No participant data exists. |
| An independently adjudicated reference standard | No panel convened. |
| Silent-narrowing rate (SNR) or derivation fidelity (DF) | RQ5 outcomes. Reported as `DEFERRED`. |
| Universal platform independence | Only the tested environments are measured. |
| Detection capability, false-denial rates, production impact | Out of scope; requires shadow-mode deployment. |
| Semantic correctness or completeness over the harm space | Authorization-soundness only. Compilation warrants fidelity to the approved specification, not that the specification is complete. |
| That a permitted action is the right action in the world | Section XII, "Authorization-soundness, not semantic correctness". |
| That upstream evidence is true | Section XII, "Epistemic bounding". Compiled predicates evaluate the evidence declared to them, not the reality it purports to describe. |
| Legal compliance from empty traceability queries | Explicitly disclaimed in Section VIII. |
| Orphan-control impossibility in a deployment | Holds within `Φ`-produced bundles; extends to a deployment only under the runtime acceptance condition. |
| Anything about the 284,807-event run of [15] | Not reproduced here; belongs to that paper and is conformance-class there. |

---

## Development results vs final results

`results/development/` holds exploratory numbers produced while the implementation
was being built and debugged. **They are not reportable.** They are committed
because deleting them would hide the development history that the freeze is
supposed to separate the final campaign from.

`results/final/` holds the frozen reportable campaign, executed after the public
timestamped preregistration commit. Section XI-I: "The internal selection of frozen
elements is not a freeze — the public timestamped commitment is."

If any final number differs from a development number, the final one is the
reportable value and the difference is explained in
`paper_update/PLACEHOLDER_REPLACEMENT_TABLE.md`.
