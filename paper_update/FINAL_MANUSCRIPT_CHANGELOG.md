# FINAL_MANUSCRIPT_CHANGELOG.md

Every substantive modification made to produce the IEEE-submission manuscript.

| | |
|---|---|
| Source | `From_Risk_Register_to_Runtime_Predicate_FINAL.docx` (unmodified) |
| Output | `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx` |
| Edits applied | **31 of 31** |
| Applied within a single run (formatting fully preserved) | 24 |
| Applied by splicing across runs (all surrounding character formatting preserved) | 8 |
| Draft markers remaining | **0** |

Every replacement is traceable to `paper_update/MEASURED_RESULTS_V2.md`, to a file under `results/final_v2/`, or to `paper_update/LITERATURE_VERIFICATION.md`.

---

## Applied edits

### E01 — Abstract

**Was:** and RFC 8785 canonicalization supporting environment-independent determinism.

**Now:** and RFC 8785 canonicalization supporting determinism that is reproducible across the tested supported environments.

**Why:** 'environment-independent determinism' overclaims. Determinism is measured across a finite tested matrix (three operating systems, two architectures, six CPython versions), which is not the set of all environments. Evidence: results/final_v2/CI_STATUS.md.

*(applied in-run)*

### E02 — Abstract

**Was:** and translation determinism of 1.000 over 31 compilation runs;

**Now:** and translation determinism of 1.000 over 62 compilation runs (31 per case), reproduced on three operating systems and two machine architectures;

**Why:** The reportable campaign ran the stratified 31-per-case matrix, 62 runs in total. Evidence: results/final_v2/determinism_summary.json, CI_STATUS.md.

*(applied in-run)*

### E03 — Abstract

**Was:** and Monte Carlo rating perturbation moves heat-map gate membership with probability up to 0.321 while consequence-class membership does not move at all.

**Now:** and Monte Carlo rating perturbation, under an author-specified, prospectively frozen ±1 ordinal sensitivity model, moves heat-map gate membership with probability up to 0.321 while consequence-class membership does not move at all.

**Why:** The distributions are author-specified, not panel-adjudicated, and are a declared sensitivity model rather than an estimate of real rating uncertainty. Evidence: preregistration/monte_carlo_distributions_v1.json.

*(applied in-run)*

### E04 — II-F

**Was:** The method begins after legal applicability has been determined and ends before runtime detection or actuation performance is claimed. [VERIFY: final literature sweep at submission — compliance-by-design, regulatory tech…

**Now:** The method begins after legal applicability has been determined and ends before runtime detection or actuation performance is claimed. A final literature sweep at submission over compliance-by-design, regulatory technology and agent-governance work of 2024–2026 located two further adjacent contributions. A layered tran…

**Why:** Discharges the manuscript's own [VERIFY] marker. Adds the two adjacent works the sweep found; omitting Koch (arXiv:2604.05229) would have been a genuine related-work gap. The narrow novelty position is preserved verbatim, not expanded. Evidence: paper_update/LITERATURE_VERIFICATION.md.

*(applied spliced across runs)*

### E05 — IX

**Was:** and the three-way collision at s = 12 (R-04, R-09, R-12 with gates 0, 1, 0) instantiates Proposition 2

**Now:** and the collision at s = 12 among the runtime rows — R-04, R-09 and R-12, with gates 0, 1, 0 — instantiates Proposition 2

**Why:** 'three-way' is inaccurate for the released artifact: non-runtime row R-14 also rates 12 and is ungated, so the score-12 collision has four members. Scoping the sentence to the runtime rows keeps it exact without weakening Proposition 2. Evidence: results/final_v2/gate_divergence.json.

*(applied in-run)*

### E06 — IX

**Was:** Both sums run over all sixteen register rows, non-runtime dispositions included: those rows carry ratings but no gate, and excluding them would understate divergence at low thresholds.

**Now:** Both sums run over all sixteen register rows, non-runtime dispositions included: those rows carry ratings but no gate, and excluding them would understate divergence at low thresholds. The three non-runtime rows are rated R-14 = 12 (L = 3, I = 4), R-15 = 6 (L = 3, I = 2) and R-16 = 8 (L = 2, I = 4); publishing them is …

**Why:** Without the three ratings GD_min = 3 is not reproducible from the published register, and its dependence on undisclosed fixtures would be invisible. Evidence: results/final_v2/gate_divergence.json (case_a_fixture_rating_sensitivity).

*(applied in-run)*

### E07 — IX (Figure 3 caption)

**Was:** R-10 is gated at s = 10 while R-04 and R-12 are not gated at s = 12 (Proposition 1), and the three-way collision at s = 12 carries divergent gates (Proposition 2).

**Now:** R-10 is gated at s = 10 while R-04 and R-12 are not gated at s = 12 (Proposition 1), and the collision at s = 12 among the runtime rows carries divergent gates (Proposition 2).

**Why:** Same correction as E05, applied to the figure caption so text and caption agree.

*(applied in-run)*

### E08 — X

**Was:** though its origin is retrospective. [PENDING: hash-pinned Case B artifact release]

**Now:** though its origin is retrospective. The Case B artifact set is hash-pinned: the SHA-256 of the RFC 8785 canonical bundle payload is 2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce. Its predicate set is traced to the enforcement artifact's own predicate family, which comprises thirteen named predicates …

**Why:** Resolves the [PENDING] marker with the measured hash and adds the [15]-linkage. The claim boundary is restated inside the new text so it cannot be read as detection evidence. Evidence: cases/case_b/ldrea_traceability.json, docs/CASE_B_LDREA_TRACEABILITY.md.

*(applied spliced across runs)*

### E09 — XI-B (metrics table)

**Was:** 1.000 (31/31 runs, pinned container)

**Now:** 1.000 (62/62 runs; 31 per case, reproduced on three operating systems)

**Why:** Measured count and the environments actually exercised. Evidence: results/final_v2/determinism_summary.json, CI_STATUS.md.

*(applied in-run)*

### E10 — XI-B (metrics table)

**Was:** Case A: GD(15) = 3, GD_min = 3 · Case B: GD_min = 0

**Now:** Case A: GD(15) = 3, GD_min = 3 · Case B: GD(15) = 4, GD_min = 0

**Why:** Case B's GD at the declared threshold was measured and is reported alongside its GD_min. Evidence: results/final_v2/gate_divergence.json.

*(applied in-run)*

### E11 — XI-B (metrics table, SNR and DF rows)

**Was:** primary outcome of the deferred study · [TO REPORT]

**Now:** primary outcome of the deferred comparative study; not reported here

**Why:** Removes the drafting marker without implying a value exists. RQ5 is deferred and no participant data exists.

*(applied in-run, 2 occurrences)*

### E12 — XI-C

**Was:** The reference standard is produced by an independent three-person adjudication panel with expertise spanning AI governance, operational risk, and policy/control engineering.

**Now:** The reference standard is to be produced by an independent three-person adjudication panel with expertise spanning AI governance, operational risk, and policy/control engineering. That panel has not yet been convened: it is part of the deferred comparative study, and no adjudicated reference standard exists at the time…

**Why:** The manuscript described the panel in the present tense, which reads as though it had met. It has not. This also removes the contradiction with XI-G. Evidence: preregistration/RQ5_DEFERRED_PROTOCOL.md.

*(applied in-run)*

### E13 — XI-G

**Was:** For each risk rᵢ, the independent panel freezes discrete probability masses over plausible ratings:

**Now:** For each risk rᵢ, discrete probability masses over plausible ratings are fixed before execution. In the analysis reported here these masses are author-specified rather than panel-adjudicated: a symmetric ±1 ordinal perturbation placing probability 0.6 on the approved rating and 0.2 on each adjacent rating of the enterp…

**Why:** MANDATORY. The manuscript attributed a methodological input to a body that has not been convened. Evidence: preregistration/monte_carlo_distributions_v1.json, docs/FIXTURE_PROVENANCE.md FP-020.

*(applied in-run)*

### E14 — XI-G

**Was:** Measured on Case A at K = 250,000: the maximum per-risk heat-map flip probability is 0.321, concentrated on rows adjacent to T_H, while FPᵢ^C* = 0.000 across the register by construction

**Now:** Measured on Case A at K = 250,000: the maximum per-risk heat-map flip probability is 0.321 (MCSE 0.001), concentrated on rows adjacent to T_H, and the expected number of heat-map gate changes per register is 3.64. Over the draws, GD(15) has mean 5.447 against an approved value of 3, and GD_min has mean 3.226; on Case B…

**Why:** Reports the quantities Section XI-G promises but did not give, and states that the C* zero is verified rather than asserted. Evidence: results/final_v2/monte_carlo_summary.json.

*(applied in-run)*

### E15 — XI-H

**Was:** Measured: TD = 1.000 over 31 compilation runs — repeated runs, key and row reorderings, and locale and time-zone variation — executed inside the pinned reproducible container. Replication outside that container, across i…

**Now:** Measured: TD = 1.000 over 62 compilation runs, 31 per case, following a stratified matrix of 10 clean repeats, 10 row shuffles, 5 object-key shuffles, 3 locales and 3 time zones. Row shuffles permute the risk register, risk analysis, obligation matrix, authority matrix, Approved Control Specifications, dispositions, ju…

**Why:** Measured counts, the actual stratified matrix, the environments exercised, and the suite counts the manuscript omitted. Also records the defect the experiment found, which is material to the reader's confidence in it. Evidence: results/final_v2/determinism_runs.csv, adversarial.json, property_tests.json, CI_STATUS.md.

*(applied in-run)*

### E16 — XI-I

**Was:** Before execution, the following are publicly hash-committed: hypotheses and primary outcomes; case artifacts and held-out-register hash; derivation catalog; adjudication instrument; thresholds and the C* definition; comp…

**Now:** Before execution, the following are publicly hash-committed: hypotheses and primary outcomes; case artifacts; derivation catalog; adjudication instrument; thresholds and the C* definition; schemas; compiler commit and container definition; randomization seed; Bayesian priors; Monte Carlo distributions and seed; determi…

**Why:** The Tier-0 freeze does not contain a held-out-register hash, because no held-out register has been authored; claiming otherwise would be false. Also records that the public commitment is now discharged. Evidence: results/final_v2/PROVENANCE.json, preregistration/HELD_OUT_REGISTER.md.

*(applied in-run)*

### E17 — XII

**Was:** Determinism scope. Environment-independence is measured inside a pinned reproducible container. Determinism testing covers repeated runs, key and row reordering, and locale and time-zone variation, but replication across…

**Now:** Determinism scope. TD = 1.000 is measured over 62 compilation runs, 31 per case, on each of eight independently provisioned environments spanning three operating systems (macOS 26.6.2, Linux on both x86_64 with glibc 2.39 and aarch64 with glibc 2.36, and Windows 10.0.26100), two machine architectures (arm64 and x86_64)…

**Why:** The old limitation now understates the evidence, and deleting it would overstate it. Widened to what was measured, with the boundary kept explicit. Evidence: results/final_v2/CI_STATUS.md.

*(applied spliced across runs)*

### E18 — XII

**Was:** Monte Carlo scope. Rating perturbation estimates sensitivity under the frozen input distributions; it does not estimate real-world event frequencies or harm probabilities.

**Now:** Monte Carlo scope. Rating perturbation estimates sensitivity under the frozen input distributions; it does not estimate real-world event frequencies or harm probabilities. Those distributions are author-specified and prospectively frozen, not panel-adjudicated, so the analysis establishes that heat-map gate membership …

**Why:** Adds the two limitations the audit identified: sensitivity-model provenance and GD_min's dependence on fixture ratings. Evidence: docs/FIXTURE_PROVENANCE.md FP-014 and FP-020.

*(applied spliced across runs)*

### E19 — XIII

**Was:** it consumes the L-DREA receipt interface (extended by the requirement-reference conformance condition of Section II) and repeats none of the enforcement architecture. [VERIFY: sentence-level overlap check against the fin…

**Now:** it consumes the L-DREA receipt interface (extended by the requirement-reference conformance condition of Section II) and repeats none of the enforcement architecture. The separation was checked at submission against the released enforcement artifact of record: the predicate families, aggregation mathematics and evidenc…

**Why:** Discharges the [VERIFY] marker as normal prose. The check was performed against the released artifact; see docs/CASE_B_LDREA_TRACEABILITY.md.

*(applied spliced across runs)*

### E20 — XV

**Was:** Deterministic, because after approval, compilation to a canonically serialized, signed, immutable bundle is environment-independent and adversarially testable,

**Now:** Deterministic, because after approval, compilation to a canonically serialized, signed, immutable bundle reproduces the same canonical payload hash across the tested supported environments and is adversarially testable,

**Why:** Same overclaim as E01, in the conclusion.

*(applied in-run)*

### E21 — XV

**Was:** The immediate future work is fixed by the evaluation plan itself: execute the Tier-0 measurements, pin both case artifacts, publish the hash commitment that binds the deferred comparative study — then hand the compiled-b…

**Now:** The Tier-0 measurements are executed and reported, both case artifacts are pinned by canonical payload hash, and the hash commitment that binds the deferred comparative study is published. What remains is to execute that committed study, and to hand the compiled-bundle interface to the shadow-mode deployment that a sub…

**Why:** Tier-0 is executed; describing it as future work is now false. Evidence: results/final_v2/.

*(applied in-run)*

### E22 — Data and Code Availability

**Was:** and the preregistration commitment are released as a hash-pinned tagged release per Appendix C. The held-out expert-study register is withheld until study close, then released with the study data.

**Now:** and the preregistration commitment are released as a hash-pinned tagged release per Appendix C, at https://github.com/Sukhmangill977/gc-ir-reference, release tag v1.0.0, under the MIT licence. The repository contains the GC-IR JSON Schemas; the Ψ_K tooling and the Φ reference implementation; the Control Derivation Cata…

**Why:** Replaces the generic statement with the actual release. No DOI is cited because none exists. Evidence: results/final_v2/PROVENANCE.json.

*(applied in-run)*

### E23 — Appendix A

**Was:** The machine-readable JSON Schema (draft 2020-12) implementing these requirements ships in the repository. [PENDING: v1.0 freeze and $id host set at the artifact-repository release]

**Now:** The machine-readable JSON Schema (draft 2020-12) implementing these requirements ships in the repository, frozen at v1.0 and hash-pinned in the release manifest. Schema $id values are stable identifiers within the v1.0 namespace rather than resolvable endpoints; the authoritative copies are the schema files in the tagg…

**Why:** Resolves the [PENDING] marker. Schema stays at v1.0 — the normative version throughout the manuscript. No resolvable host is claimed, because none is maintained. Evidence: preregistration/FREEZE_MANIFEST_V2.sha256.

*(applied spliced across runs)*

### E24 — Appendix C

**Was:** named in the release notes; MIT license for code and schema, per that precedent. [TO CONFIRM: final repository path at release]

**Now:** named in the release notes; MIT license for code and schema, per that precedent. The artifact is released at https://github.com/Sukhmangill977/gc-ir-reference, release tag v1.0.0.

**Why:** Resolves the [TO CONFIRM] marker with the actual repository path. Evidence: the public release.

*(applied spliced across runs)*

### E25 — Appendix C

**Was:** The release tag and manifest hash together constitute the public preregistration commitment referenced in Section XI-I.

**Now:** The release tag and manifest hash together constitute the public preregistration commitment referenced in Section XI-I. Reproduction is a single command; the artifact regenerates every reported figure and verifies both case artifacts against committed reference canonical payload hashes.

**Why:** States the one-command reproduction the release provides.

*(applied in-run)*

### E26 — References [8]

**Was:** Open Policy Agent documentation, openpolicyagent.org [VERIFY version cited].

**Now:** Open Policy Agent, project documentation, Cloud Native Computing Foundation (graduated project), openpolicyagent.org, accessed Sep. 2026.

**Why:** Resolves the [VERIFY version cited] marker. No version is cited, because none was pinned; the reference now carries an access date. OPA's CNCF graduated status verified. Evidence: paper_update/LITERATURE_VERIFICATION.md.

*(applied in-run)*

### E27 — References [15]

**Was:** IEEE Access, 2026, Early Access, doc. 11641546 [INSERT final DOI from IEEE Xplore].

**Now:** IEEE Access, 2026, early access, art. no. 11641546.

**Why:** Resolves the [INSERT] marker. The final DOI could not be verified against a reachable primary source and was NOT invented; the early-access article number is cited instead. The author must insert the DOI once assigned — see paper_update/ZENODO_AND_DOI_INSERTION_POINTS.md.

*(applied in-run)*

### E28 — References [18]

**Was:** ACM Computing Surveys, vol. 57, no. 4, art. no. 104, pp. 1–37, 2025 (online 23 Dec. 2024), doi: 10.1145/3706057.

**Now:** ACM Computing Surveys, vol. 57, no. 4, 2025 (online 23 Dec. 2024), doi: 10.1145/3706057.

**Why:** The article number could not be resolved: one indexing record gives 102, the manuscript gives 104, and both ACM and dblp blocked automated retrieval. The disputed field is removed; volume, issue, year and DOI locate the work unambiguously. Evidence: paper_update/LITERATURE_VERIFICATION.md.

*(applied in-run)*

### E29 — References [28], [29]

**Was:** [27] K. L. Gwet, "Computing Inter-Rater Reliability and Its Variance in the Presence of High Agreement," British Journal of Mathematical and Statistical Psychology, vol. 61, no. 1, pp. 29–48, 2008.

**Now:** [27] K. L. Gwet, "Computing Inter-Rater Reliability and Its Variance in the Presence of High Agreement," British Journal of Mathematical and Statistical Psychology, vol. 61, no. 1, pp. 29–48, 2008. [28] C. Koch, "From Governance Norms to Enforceable Controls: A Layered Translation Method for Runtime Guardrails in Agent…

**Why:** Adds the two references the literature sweep requires. Both verified against their arXiv abstract pages.

*(applied in-run)*

### E30 — IX

**Was:** and the artifact is hash-pinned so refinement and compilation are reproducible by reviewers.)

**Now:** and the artifact is hash-pinned so refinement and compilation are reproducible by reviewers: the SHA-256 of the RFC 8785 canonical bundle payload is f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536.)

**Why:** Case B is pinned by hash in the text but Case A was not, so the claim that both case artifacts are pinned could not be checked from the paper. Evidence: cases/case_a/expected/reference_hashes.json.

*(applied in-run)*

### E31 — IX

**Was:** CIRO Rule 3600 research supervision, with individual predicates citing the applicable sections (notably ss. 3608–3622) rather than the rule number alone;

**Now:** CIRO Rule 3600 research supervision [6], with individual predicates citing the applicable sections (notably ss. 3608–3622) rather than the rule number alone;

**Why:** Reference [6] is CIRO Rule 3600 and was listed but never cited; the rule is named here in prose. Adding the citation marker makes the reference list fully reachable, with no uncited entries.

*(applied in-run)*

## Draft-marker scan of the OUTPUT document

**None.** No `[VERIFY`, `[PENDING`, `[TO CONFIRM`, `[TO REPORT`, `[INSERT`, `TBD` or `TODO` remains anywhere in the submission manuscript.

## Deliberately unchanged

* Propositions 1–3, their statements and their proofs.
* The claim boundary (Section XIV) and the non-contributions (Section I-D).
* Every statement that RQ5 is preregistered and deferred; no comparative claim was added anywhere.
* Case A's classification as synthetic and Case B's as a forensic reconstruction.
* The evidence classification of the 284,807-event run as conformance-class work belonging to [15], not reproduced here.
* The normative schema version, which remains **v1.0**.
* The narrow novelty position in Section II-F: the paper still states that governance-to-code translation is not wholly unprecedented.
