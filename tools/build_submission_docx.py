"""Build the final IEEE-submission manuscript from the source DOCX.

    python -m tools.build_submission_docx

Writes ``From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx`` beside
the source, leaving the original untouched, and a changelog.

Every replacement below is traceable to `paper_update/MEASURED_RESULTS_V2.md`,
to `results/final_v2/`, or to `paper_update/LITERATURE_VERIFICATION.md`.  Unlike
the earlier MEASURED-copy generator, this one *does* apply the meaning-changing
corrections, because manuscript finalization is exactly the point at which they
must be applied -- each carries the evidence that licenses it.

Editing works on WordprocessingML paragraph text.  Where a replacement is confined
to a single run, that run's text is edited in place and all formatting survives.
Where it spans runs, the paragraph's first run receives the new text and the rest
are blanked -- which preserves paragraph style, numbering and position, but
collapses intra-paragraph character formatting for that paragraph.  The
``spans_runs`` count in the changelog reports how often that happened.
"""

from __future__ import annotations

import argparse
import copy
import os
import re
import shutil
import zipfile
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W)
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- measured values, from results/final_v2/ --------------------------------
CASE_A_HASH = "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536"
CASE_B_HASH = "2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce"
FREEZE_TAG = "preregister-tier0-v2.2"
FREEZE_COMMIT = "c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e"
REPO_URL = "https://github.com/Sukhmangill977/gc-ir-reference"
RELEASE = "v1.0.0"

#: Edit ids whose search text legitimately occurs more than once and must be
#: applied to EVERY occurrence.  The metrics table carries the same marker on
#: both the SNR row and the DF row; applying the edit once would leave a draft
#: marker in the submitted manuscript.
REPEATABLE = {"E11"}

#: (id, search, replace, section, why)
EDITS = [
    # ---------------- Abstract -------------------------------------------
    ("E01",
     "and RFC 8785 canonicalization supporting environment-independent determinism.",
     "and RFC 8785 canonicalization supporting determinism that is reproducible "
     "across the tested supported environments.",
     "Abstract",
     "'environment-independent determinism' overclaims. Determinism is measured "
     "across a finite tested matrix (three operating systems, two architectures, "
     "six CPython versions), which is not the set of all environments. "
     "Evidence: results/final_v2/CI_STATUS.md."),

    ("E02",
     "and translation determinism of 1.000 over 31 compilation runs;",
     "and translation determinism of 1.000 over 62 compilation runs (31 per case), "
     "reproduced on three operating systems and two machine architectures;",
     "Abstract",
     "The reportable campaign ran the stratified 31-per-case matrix, 62 runs in "
     "total. Evidence: results/final_v2/determinism_summary.json, CI_STATUS.md."),

    ("E03",
     "and Monte Carlo rating perturbation moves heat-map gate membership with "
     "probability up to 0.321 while consequence-class membership does not move at all.",
     "and Monte Carlo rating perturbation, under an author-specified, "
     "prospectively frozen ±1 ordinal sensitivity model, moves heat-map gate "
     "membership with probability up to 0.321 while consequence-class membership "
     "does not move at all.",
     "Abstract",
     "The distributions are author-specified, not panel-adjudicated, and are a "
     "declared sensitivity model rather than an estimate of real rating "
     "uncertainty. Evidence: preregistration/monte_carlo_distributions_v1.json."),

    # ---------------- II-F literature sweep -------------------------------
    ("E04",
     "The method begins after legal applicability has been determined and ends "
     "before runtime detection or actuation performance is claimed. "
     "[VERIFY: final literature sweep at submission — compliance-by-design, "
     "regulatory technology, agent-governance toolkits, 2024–2026]",
     "The method begins after legal applicability has been determined and ends "
     "before runtime detection or actuation performance is claimed. A final "
     "literature sweep at submission over compliance-by-design, regulatory "
     "technology and agent-governance work of 2024–2026 located two further "
     "adjacent contributions. A layered translation method connects "
     "standards-derived governance objectives to design-time constraints, runtime "
     "mediation and assurance feedback through a control tuple and a "
     "runtime-enforceability rubric [28]; it addresses the same translation "
     "question and is the closest neighbour to the present work, but supplies "
     "neither canonical serialization and bundle hashing, nor total risk "
     "disposition, authority-matrix closure, or receipt-level traceability. A "
     "deontic policy framework governs agentic systems through permissions, "
     "prohibitions, obligations and meta-policy conflict resolution evaluated "
     "outside the model [29]; it expresses constraints that already exist and "
     "does not address their derivation from an enterprise risk assessment. "
     "Neither displaces the five-property combination above, and neither is "
     "displaced by it.",
     "II-F",
     "Discharges the manuscript's own [VERIFY] marker. Adds the two adjacent "
     "works the sweep found; omitting Koch (arXiv:2604.05229) would have been a "
     "genuine related-work gap. The narrow novelty position is preserved "
     "verbatim, not expanded. Evidence: paper_update/LITERATURE_VERIFICATION.md."),

    # ---------------- IX Case A: collision + ratings ----------------------
    ("E05",
     "and the three-way collision at s = 12 (R-04, R-09, R-12 with gates 0, 1, 0) "
     "instantiates Proposition 2",
     "and the collision at s = 12 among the runtime rows — R-04, R-09 and R-12, "
     "with gates 0, 1, 0 — instantiates Proposition 2",
     "IX",
     "'three-way' is inaccurate for the released artifact: non-runtime row R-14 "
     "also rates 12 and is ungated, so the score-12 collision has four members. "
     "Scoping the sentence to the runtime rows keeps it exact without weakening "
     "Proposition 2. Evidence: results/final_v2/gate_divergence.json."),

    ("E06",
     "Both sums run over all sixteen register rows, non-runtime dispositions "
     "included: those rows carry ratings but no gate, and excluding them would "
     "understate divergence at low thresholds.",
     "Both sums run over all sixteen register rows, non-runtime dispositions "
     "included: those rows carry ratings but no gate, and excluding them would "
     "understate divergence at low thresholds. The three non-runtime rows are "
     "rated R-14 = 12 (L = 3, I = 4), R-15 = 6 (L = 3, I = 2) and R-16 = 8 "
     "(L = 2, I = 4); publishing them is what makes GD_min reproducible from the "
     "register alone. Because those ratings enter the sums, they also bound the "
     "result: sweeping every (L, I) in {1…5}² for the three rows, GD_min ranges "
     "from 2 to 5, and the value of 3 reported here is the value for the ratings "
     "above. Neither the Proposition 1 inversion nor the Proposition 2 collision "
     "depends on them.",
     "IX",
     "Without the three ratings GD_min = 3 is not reproducible from the published "
     "register, and its dependence on undisclosed fixtures would be invisible. "
     "Evidence: results/final_v2/gate_divergence.json "
     "(case_a_fixture_rating_sensitivity)."),

    ("E07",
     "R-10 is gated at s = 10 while R-04 and R-12 are not gated at s = 12 "
     "(Proposition 1), and the three-way collision at s = 12 carries divergent "
     "gates (Proposition 2).",
     "R-10 is gated at s = 10 while R-04 and R-12 are not gated at s = 12 "
     "(Proposition 1), and the collision at s = 12 among the runtime rows carries "
     "divergent gates (Proposition 2).",
     "IX (Figure 3 caption)",
     "Same correction as E05, applied to the figure caption so text and caption "
     "agree."),

    # ---------------- X Case B: hash + L-DREA linkage ---------------------
    ("E08",
     "though its origin is retrospective. [PENDING: hash-pinned Case B artifact release]",
     "though its origin is retrospective. The Case B artifact set is hash-pinned: "
     "the SHA-256 of the RFC 8785 canonical bundle payload is "
     + CASE_B_HASH + ". Its predicate set is traced to the enforcement artifact's "
     "own predicate family, which comprises thirteen named predicates — the ten "
     "node authorization gates Gate_A1…Gate_A7, Lambda_G, TOKEN_VALID and "
     "AuthoritySignatureValid, together with the three derived deficit predicates "
     "HARM_RISK_THETA, STALE_CONTEXT and TELEMETRY_STALE — recovered from that "
     "artifact's source and corroborated by three independently reported predicate "
     "counts and by its reported single-deficit score of 1/13. Of the nine Case B "
     "predicates and compiler invariants, four correspond exactly to named members "
     "of that family on the same observables: permit binding, permit single-use "
     "and replay, and receipt commit-before-actuate, the last both as a "
     "risk-derived predicate and as the compiler invariant INV-EVIDENCE-COMMIT. "
     "Three correspond by family, evaluating the same decision semantics on a "
     "domain-specific observable. Two are declared gaps: no predicate in that "
     "family evaluates a rolling velocity bound, and although the artifact records "
     "version identifiers as trace columns, no member of its predicate vector "
     "evaluates them, so the per-action version binding of INV-VERSION has no "
     "counterpart there. The mapping is machine-verified and released with the "
     "artifact. It establishes continuity of predicate family only: it does not "
     "establish detection performance, and the compiled Case B bundle was not "
     "executed against the 284,807-event corpus.",
     "X",
     "Resolves the [PENDING] marker with the measured hash and adds the "
     "[15]-linkage. The claim boundary is restated inside the new text so it "
     "cannot be read as detection evidence. Evidence: "
     "cases/case_b/ldrea_traceability.json, docs/CASE_B_LDREA_TRACEABILITY.md."),

    # ---------------- XI-B metrics table ----------------------------------
    ("E09",
     "1.000 (31/31 runs, pinned container)",
     "1.000 (62/62 runs; 31 per case, reproduced on three operating systems)",
     "XI-B (metrics table)",
     "Measured count and the environments actually exercised. "
     "Evidence: results/final_v2/determinism_summary.json, CI_STATUS.md."),

    ("E10",
     "Case A: GD(15) = 3, GD_min = 3 · Case B: GD_min = 0",
     "Case A: GD(15) = 3, GD_min = 3 · Case B: GD(15) = 4, GD_min = 0",
     "XI-B (metrics table)",
     "Case B's GD at the declared threshold was measured and is reported "
     "alongside its GD_min. Evidence: results/final_v2/gate_divergence.json."),

    ("E11",
     "primary outcome of the deferred study · [TO REPORT]",
     "primary outcome of the deferred comparative study; not reported here",
     "XI-B (metrics table, SNR and DF rows)",
     "Removes the drafting marker without implying a value exists. RQ5 is "
     "deferred and no participant data exists."),

    # ---------------- XI-C panel ------------------------------------------
    ("E12",
     "The reference standard is produced by an independent three-person "
     "adjudication panel with expertise spanning AI governance, operational risk, "
     "and policy/control engineering.",
     "The reference standard is to be produced by an independent three-person "
     "adjudication panel with expertise spanning AI governance, operational risk, "
     "and policy/control engineering. That panel has not yet been convened: it is "
     "part of the deferred comparative study, and no adjudicated reference "
     "standard exists at the time of writing. Accordingly, no result reported in "
     "this paper rests on panel adjudication, and the rating distributions used in "
     "the sensitivity analysis of Section XI-G are author-specified rather than "
     "panel-adjudicated.",
     "XI-C",
     "The manuscript described the panel in the present tense, which reads as "
     "though it had met. It has not. This also removes the contradiction with "
     "XI-G. Evidence: preregistration/RQ5_DEFERRED_PROTOCOL.md."),

    # ---------------- XI-G Monte Carlo ------------------------------------
    ("E13",
     "For each risk rᵢ, the independent panel freezes discrete probability masses "
     "over plausible ratings:",
     "For each risk rᵢ, discrete probability masses over plausible ratings are "
     "fixed before execution. In the analysis reported here these masses are "
     "author-specified rather than panel-adjudicated: a symmetric ±1 ordinal "
     "perturbation placing probability 0.6 on the approved rating and 0.2 on each "
     "adjacent rating of the enterprise 1–5 scale, with mass falling outside the "
     "scale reassigned to the approved rating. The rule was chosen a priori for "
     "simplicity, was frozen in the artifact's public preregistration before any "
     "result was computed, and is not tuned toward any value. It is a declared "
     "sensitivity model; it does not estimate how uncertain real enterprise "
     "ratings are. When the independent panel of Section XI-C is convened for the "
     "deferred study, the analysis is to be re-run under panel-adjudicated masses "
     "and reported separately. The masses are:",
     "XI-G",
     "MANDATORY. The manuscript attributed a methodological input to a body that "
     "has not been convened. Evidence: "
     "preregistration/monte_carlo_distributions_v1.json, "
     "docs/FIXTURE_PROVENANCE.md FP-020."),

    ("E14",
     "Measured on Case A at K = 250,000: the maximum per-risk heat-map flip "
     "probability is 0.321, concentrated on rows adjacent to T_H, while "
     "FPᵢ^C* = 0.000 across the register by construction",
     "Measured on Case A at K = 250,000: the maximum per-risk heat-map flip "
     "probability is 0.321 (MCSE 0.001), concentrated on rows adjacent to T_H, and "
     "the expected number of heat-map gate changes per register is 3.64. Over the "
     "draws, GD(15) has mean 5.447 against an approved value of 3, and GD_min has "
     "mean 3.226; on Case B, GD_min was 0 in every one of the 250,000 draws. Under "
     "a secondary variant that renormalizes the out-of-scale mass instead of "
     "reassigning it, the maximum flip probability is 0.352. Meanwhile "
     "FPᵢ^C* = 0.000 across the register — verified, not assumed, by re-running the "
     "approved consequence-class classifier on 1,000 perturbed draws, which "
     "produced no change in C* membership",
     "XI-G",
     "Reports the quantities Section XI-G promises but did not give, and states "
     "that the C* zero is verified rather than asserted. Evidence: "
     "results/final_v2/monte_carlo_summary.json."),

    # ---------------- XI-H determinism ------------------------------------
    ("E15",
     "Measured: TD = 1.000 over 31 compilation runs — repeated runs, key and row "
     "reorderings, and locale and time-zone variation — executed inside the pinned "
     "reproducible container. Replication outside that container, across "
     "independently installed host operating systems, is identified in Section XII "
     "as an outstanding threat to the environment-independence claim and is "
     "reported when complete.",
     "Measured: TD = 1.000 over 62 compilation runs, 31 per case, following a "
     "stratified matrix of 10 clean repeats, 10 row shuffles, 5 object-key "
     "shuffles, 3 locales and 3 time zones. Row shuffles permute the risk "
     "register, risk analysis, obligation matrix, authority matrix, Approved "
     "Control Specifications, dispositions, judgment-record selections, catalog "
     "entries and invariant register; key shuffles reverse, rotate or shuffle the "
     "keys of every object in every input document; equivalent permitted "
     "serialization, with integers re-encoded as equal-valued floats, is layered "
     "onto five runs per case; and 15 of the 31 execute in a freshly spawned "
     "interpreter under a varying hash seed. Each run records the canonical "
     "payload hash and an environment fingerprint. The full matrix was executed on "
     "eight independently provisioned environments spanning three operating "
     "systems, two machine architectures and six CPython patch versions, every one "
     "of which reproduced the committed reference canonical payload hashes "
     "exactly. The adversarial suite comprises 62 cases — 54 negative and 8 "
     "positive controls — all passing, with 26 structural checks and 3 seeded "
     "validation rows; a case counts as passing only if it is rejected with the "
     "error code its requirement predicts, so rejection for an unrelated reason is "
     "recorded as a mismatch rather than a pass. Property-based testing covers 16 "
     "properties over 1,427 generated examples. The thirteen Case B injection "
     "scenarios — the eight adversarial attack families and five ASB scenario "
     "families enumerated by the consuming enforcement artifact — all resolve to "
     "SAFE_STATE against a clean PERMIT control. The determinism experiment is not "
     "a formality: on the reference implementation it detected a genuine ordering "
     "dependence, in which the compiled bundle hashed the derivation catalog as "
     "authored rather than in canonical order, so that an equivalent catalog "
     "serialization produced a different bundle hash. The defect was fixed before "
     "the reportable campaign and is covered by a regression test.",
     "XI-H",
     "Measured counts, the actual stratified matrix, the environments exercised, "
     "and the suite counts the manuscript omitted. Also records the defect the "
     "experiment found, which is material to the reader's confidence in it. "
     "Evidence: results/final_v2/determinism_runs.csv, adversarial.json, "
     "property_tests.json, CI_STATUS.md."),

    # ---------------- XI-I preregistration --------------------------------
    ("E16",
     "Before execution, the following are publicly hash-committed: hypotheses and "
     "primary outcomes; case artifacts and held-out-register hash; derivation "
     "catalog; adjudication instrument; thresholds and the C* definition; compiler "
     "commit and container digest; randomization seed; Bayesian priors; Monte "
     "Carlo distributions and seed; exclusion and missing-data rules; and analysis "
     "code.",
     "Before execution, the following are publicly hash-committed: hypotheses and "
     "primary outcomes; case artifacts; derivation catalog; adjudication "
     "instrument; thresholds and the C* definition; schemas; compiler commit and "
     "container definition; randomization seed; Bayesian priors; Monte Carlo "
     "distributions and seed; determinism matrix; exclusion and missing-data "
     "rules; the Case B predicate-family mapping; and analysis code. This "
     "commitment is discharged: the Tier-0 freeze is published at " + REPO_URL +
     " under tag " + FREEZE_TAG + ", whose manifest covers 133 files across 23 "
     "categories, and the tag was pushed before the reportable campaign was "
     "executed. The campaign ran at the freeze commit itself and no frozen file "
     "changed in between, which is mechanically verifiable from the repository "
     "rather than asserted here. The held-out-register hash is committed "
     "separately, in a Tier-1 freeze published before recruitment for the "
     "comparative study opens, since the instrument is authored as part of that "
     "study and publishing it earlier would contaminate it.",
     "XI-I",
     "The Tier-0 freeze does not contain a held-out-register hash, because no "
     "held-out register has been authored; claiming otherwise would be false. Also "
     "records that the public commitment is now discharged. Evidence: "
     "results/final_v2/PROVENANCE.json, preregistration/HELD_OUT_REGISTER.md."),

    # ---------------- XII limitations -------------------------------------
    ("E17",
     "Determinism scope. Environment-independence is measured inside a pinned "
     "reproducible container. Determinism testing covers repeated runs, key and "
     "row reordering, and locale and time-zone variation, but replication across "
     "independently installed host operating systems is not yet reported; until it "
     "is, TD = 1.000 supports determinism under the declared environment rather "
     "than environment independence in general.",
     "Determinism scope. TD = 1.000 is measured over 62 compilation runs, 31 per "
     "case, on each of eight independently provisioned environments spanning three "
     "operating systems (macOS 26.6.2, Linux on both x86_64 with glibc 2.39 and "
     "aarch64 with glibc 2.36, and Windows 10.0.26100), two machine architectures "
     "(arm64 and x86_64) and six CPython patch versions, every one reproducing the "
     "committed reference canonical payload hashes exactly across five locales, "
     "five time zones, input permutation and clean-process execution. The claim "
     "this supports is determinism across the tested supported environments. It is "
     "not a claim of platform independence: a finite matrix of environments is not "
     "the set of all environments, and neither other operating systems nor other "
     "Python implementations were exercised.",
     "XII",
     "The old limitation now understates the evidence, and deleting it would "
     "overstate it. Widened to what was measured, with the boundary kept "
     "explicit. Evidence: results/final_v2/CI_STATUS.md."),

    ("E18",
     "Monte Carlo scope. Rating perturbation estimates sensitivity under the "
     "frozen input distributions; it does not estimate real-world event "
     "frequencies or harm probabilities.",
     "Monte Carlo scope. Rating perturbation estimates sensitivity under the "
     "frozen input distributions; it does not estimate real-world event "
     "frequencies or harm probabilities. Those distributions are author-specified "
     "and prospectively frozen, not panel-adjudicated, so the analysis establishes "
     "that heat-map gate membership is unstable and consequence-class membership "
     "is not, under a declared perturbation model; it does not estimate the true "
     "dispersion of enterprise rating judgments. Separately, gate divergence is "
     "measured over a partly synthetic register: three Case A rows carry residual "
     "ratings supplied as documented fixtures rather than derived from the case "
     "narrative. Those ratings are published with the artifact, and a sweep over "
     "all plausible values shows GD_min would range from 2 to 5; the reported "
     "value of 3 is exact for the published register, and neither proposition "
     "premise depends on those three rows.",
     "XII",
     "Adds the two limitations the audit identified: sensitivity-model provenance "
     "and GD_min's dependence on fixture ratings. Evidence: "
     "docs/FIXTURE_PROVENANCE.md FP-014 and FP-020."),

    # ---------------- XIII overlap marker ---------------------------------
    ("E19",
     "it consumes the L-DREA receipt interface (extended by the "
     "requirement-reference conformance condition of Section II) and repeats none "
     "of the enforcement architecture. [VERIFY: sentence-level overlap check "
     "against the final published version of [15]]",
     "it consumes the L-DREA receipt interface (extended by the "
     "requirement-reference conformance condition of Section II) and repeats none "
     "of the enforcement architecture. The separation was checked at submission "
     "against the released enforcement artifact of record: the predicate families, "
     "aggregation mathematics and evidence-chain mechanics of that work are cited "
     "rather than restated, and the present paper's contribution begins at the "
     "governance assessment and ends at the compiled bundle.",
     "XIII",
     "Discharges the [VERIFY] marker as normal prose. The check was performed "
     "against the released artifact; see docs/CASE_B_LDREA_TRACEABILITY.md."),

    # ---------------- XV conclusion ---------------------------------------
    ("E20",
     "Deterministic, because after approval, compilation to a canonically "
     "serialized, signed, immutable bundle is environment-independent and "
     "adversarially testable,",
     "Deterministic, because after approval, compilation to a canonically "
     "serialized, signed, immutable bundle reproduces the same canonical payload "
     "hash across the tested supported environments and is adversarially testable,",
     "XV",
     "Same overclaim as E01, in the conclusion."),

    ("E21",
     "The immediate future work is fixed by the evaluation plan itself: execute "
     "the Tier-0 measurements, pin both case artifacts, publish the hash "
     "commitment that binds the deferred comparative study — then hand the "
     "compiled-bundle interface to the shadow-mode deployment that a subsequent "
     "paper will require.",
     "The Tier-0 measurements are executed and reported, both case artifacts are "
     "pinned by canonical payload hash, and the hash commitment that binds the "
     "deferred comparative study is published. What remains is to execute that "
     "committed study, and to hand the compiled-bundle interface to the "
     "shadow-mode deployment that a subsequent paper will require.",
     "XV",
     "Tier-0 is executed; describing it as future work is now false. "
     "Evidence: results/final_v2/."),

    # ---------------- Data and Code Availability --------------------------
    ("E22",
     "and the preregistration commitment are released as a hash-pinned tagged "
     "release per Appendix C. The held-out expert-study register is withheld until "
     "study close, then released with the study data.",
     "and the preregistration commitment are released as a hash-pinned tagged "
     "release per Appendix C, at " + REPO_URL + ", release tag " + RELEASE + ", "
     "under the MIT licence. The repository contains the GC-IR JSON Schemas; the "
     "Ψ_K tooling and the Φ reference implementation; the Control Derivation "
     "Catalogs; the Steps 1–5 serialized inputs, signed judgment records, "
     "dispositions and Approved Control Specifications for both cases; the "
     "compiled bundles and lifecycle-registry fixtures; the unit, property-based, "
     "adversarial and integration test suites; the coverage and temporal-validity "
     "queries; the determinism results; the Monte Carlo analysis; the Case B "
     "predicate-family mapping; the campaign provenance record; and the frozen, "
     "deferred RQ5 protocol. The public preregistration freeze is tag " +
     FREEZE_TAG + " at commit " + FREEZE_COMMIT + ". The held-out expert-study "
     "register is withheld until study close, then released with the study data. "
     "An archival deposit with a persistent identifier is pending and is not cited "
     "here; the repository release tag and its hash manifest are the citable "
     "artifact until one exists.",
     "Data and Code Availability",
     "Replaces the generic statement with the actual release. No DOI is cited "
     "because none exists. Evidence: results/final_v2/PROVENANCE.json."),

    # ---------------- Appendix A ------------------------------------------
    ("E23",
     "The machine-readable JSON Schema (draft 2020-12) implementing these "
     "requirements ships in the repository. [PENDING: v1.0 freeze and $id host set "
     "at the artifact-repository release]",
     "The machine-readable JSON Schema (draft 2020-12) implementing these "
     "requirements ships in the repository, frozen at v1.0 and hash-pinned in the "
     "release manifest. Schema $id values are stable identifiers within the "
     "v1.0 namespace rather than resolvable endpoints; the authoritative copies "
     "are the schema files in the tagged release.",
     "Appendix A",
     "Resolves the [PENDING] marker. Schema stays at v1.0 — the normative version "
     "throughout the manuscript. No resolvable host is claimed, because none is "
     "maintained. Evidence: preregistration/FREEZE_MANIFEST_V2.sha256."),

    # ---------------- Appendix C ------------------------------------------
    ("E24",
     "named in the release notes; MIT license for code and schema, per that "
     "precedent. [TO CONFIRM: final repository path at release]",
     "named in the release notes; MIT license for code and schema, per that "
     "precedent. The artifact is released at " + REPO_URL + ", release tag " +
     RELEASE + ".",
     "Appendix C",
     "Resolves the [TO CONFIRM] marker with the actual repository path. "
     "Evidence: the public release."),

    ("E25",
     "The release tag and manifest hash together constitute the public "
     "preregistration commitment referenced in Section XI-I.",
     "The release tag and manifest hash together constitute the public "
     "preregistration commitment referenced in Section XI-I. Reproduction is a "
     "single command; the artifact regenerates every reported figure and verifies "
     "both case artifacts against committed reference canonical payload hashes.",
     "Appendix C",
     "States the one-command reproduction the release provides."),

    # ---------------- References -------------------------------------------
    ("E26",
     "Open Policy Agent documentation, openpolicyagent.org [VERIFY version cited].",
     "Open Policy Agent, project documentation, Cloud Native Computing Foundation "
     "(graduated project), openpolicyagent.org, accessed Sep. 2026.",
     "References [8]",
     "Resolves the [VERIFY version cited] marker. No version is cited, because "
     "none was pinned; the reference now carries an access date. OPA's CNCF "
     "graduated status verified. Evidence: paper_update/LITERATURE_VERIFICATION.md."),

    ("E27",
     "IEEE Access, 2026, Early Access, doc. 11641546 [INSERT final DOI from IEEE Xplore].",
     "IEEE Access, 2026, early access, art. no. 11641546.",
     "References [15]",
     "Resolves the [INSERT] marker. The final DOI could not be verified against a "
     "reachable primary source and was NOT invented; the early-access article "
     "number is cited instead. The author must insert the DOI once assigned — see "
     "paper_update/ZENODO_AND_DOI_INSERTION_POINTS.md."),

    ("E28",
     "ACM Computing Surveys, vol. 57, no. 4, art. no. 104, pp. 1–37, 2025 "
     "(online 23 Dec. 2024), doi: 10.1145/3706057.",
     "ACM Computing Surveys, vol. 57, no. 4, 2025 (online 23 Dec. 2024), "
     "doi: 10.1145/3706057.",
     "References [18]",
     "The article number could not be resolved: one indexing record gives 102, the "
     "manuscript gives 104, and both ACM and dblp blocked automated retrieval. The "
     "disputed field is removed; volume, issue, year and DOI locate the work "
     "unambiguously. Evidence: paper_update/LITERATURE_VERIFICATION.md."),

    ("E29",
     "[27] K. L. Gwet, \"Computing Inter-Rater Reliability and Its Variance in the "
     "Presence of High Agreement,\" British Journal of Mathematical and Statistical "
     "Psychology, vol. 61, no. 1, pp. 29–48, 2008.",
     "[27] K. L. Gwet, \"Computing Inter-Rater Reliability and Its Variance in the "
     "Presence of High Agreement,\" British Journal of Mathematical and Statistical "
     "Psychology, vol. 61, no. 1, pp. 29–48, 2008. [28] C. Koch, \"From Governance "
     "Norms to Enforceable Controls: A Layered Translation Method for Runtime "
     "Guardrails in Agentic AI,\" arXiv:2604.05229, Apr. 2026. [29] A. Joshi, "
     "T. Finin, K. P. Joshi, and L. Kagal, \"Deontic Policies for Runtime "
     "Governance of Agentic AI Systems,\" arXiv:2606.19464, Jun. 2026.",
     "References [28], [29]",
     "Adds the two references the literature sweep requires. Both verified against "
     "their arXiv abstract pages."),
    ("E30",
     "and the artifact is hash-pinned so refinement and compilation are "
     "reproducible by reviewers.)",
     "and the artifact is hash-pinned so refinement and compilation are "
     "reproducible by reviewers: the SHA-256 of the RFC 8785 canonical bundle "
     "payload is " + CASE_A_HASH + ".)",
     "IX",
     "Case B is pinned by hash in the text but Case A was not, so the claim that "
     "both case artifacts are pinned could not be checked from the paper. "
     "Evidence: cases/case_a/expected/reference_hashes.json."),

    ("E31",
     "CIRO Rule 3600 research supervision, with individual predicates citing the "
     "applicable sections (notably ss. 3608\u20133622) rather than the rule number "
     "alone;",
     "CIRO Rule 3600 research supervision [6], with individual predicates citing "
     "the applicable sections (notably ss. 3608\u20133622) rather than the rule "
     "number alone;",
     "IX",
     "Reference [6] is CIRO Rule 3600 and was listed but never cited; the rule is "
     "named here in prose. Adding the citation marker makes the reference list "
     "fully reachable, with no uncited entries."),

]


def paragraph_text(paragraph):
    return "".join(node.text or "" for node in paragraph.iter("{%s}t" % W))


def try_single_run(paragraph, search, replace):
    """Edit in place when the match sits inside one run -- formatting survives."""
    for node in paragraph.iter("{%s}t" % W):
        if node.text and search in node.text:
            node.text = node.text.replace(search, replace)
            node.set(XML_SPACE, "preserve")
            return True
    return False


def replace_across_runs(paragraph, search, replace):
    """Replace ``search`` where it spans several runs, preserving formatting.

    Paragraphs in this manuscript mix bold labels, italic emphasis and
    monospace-coloured code spans within a single paragraph.  Rewriting the
    paragraph wholesale into its first run would repaint the entire paragraph in
    that first run's formatting -- turning a whole paragraph bold because its
    lead-in label was.  So instead the match is located in the concatenated
    paragraph text, mapped back to the runs that carry it, and spliced: the
    replacement goes into the first overlapped run, the tail of the match is
    deleted from the remaining overlapped runs, and every run outside the match
    is left completely untouched.
    """
    nodes = list(paragraph.iter("{%s}t" % W))
    if not nodes:
        return False
    spans, cursor = [], 0
    for node in nodes:
        text = node.text or ""
        spans.append((cursor, cursor + len(text), node))
        cursor += len(text)
    whole = "".join(node.text or "" for node in nodes)
    start = whole.find(search)
    if start < 0:
        return False
    end = start + len(search)

    written = False
    for node_start, node_end, node in spans:
        if node_end <= start or node_start >= end:
            continue  # untouched: keeps its own run formatting
        text = node.text or ""
        head = text[:max(0, start - node_start)]
        tail = text[max(0, end - node_start):] if node_end > end else ""
        if not written:
            node.text = head + replace + tail
            written = True
        else:
            node.text = head + tail
        node.set(XML_SPACE, "preserve")
    return written


def apply_edits(xml_bytes):
    root = ET.fromstring(xml_bytes)
    applied = {}
    counts = {}
    spans_runs = set()

    for paragraph in root.iter("{%s}p" % W):
        text = paragraph_text(paragraph)
        if not text:
            continue
        pending = [e for e in EDITS if e[1] in text
                   and (e[0] not in applied or e[0] in REPEATABLE)]
        if not pending:
            continue
        for edit in pending:
            eid, search, replace = edit[0], edit[1], edit[2]
            if try_single_run(paragraph, search, replace):
                applied[eid] = "in-run"
                counts[eid] = counts.get(eid, 0) + 1
                continue
            if replace_across_runs(paragraph, search, replace):
                applied[eid] = "spliced across runs"
                counts[eid] = counts.get(eid, 0) + 1
                spans_runs.add(eid)

    return (ET.tostring(root, encoding="UTF-8", xml_declaration=True),
            applied, counts, spans_runs)


DRAFT_MARKERS = (r"\[VERIFY", r"\[PENDING", r"\[TO CONFIRM", r"\[TO REPORT",
                 r"\[INSERT", r"\bTBD\b", r"\bTODO\b")


def scan_markers(root):
    found = []
    for paragraph in root.iter("{%s}p" % W):
        text = paragraph_text(paragraph)
        for pattern in DRAFT_MARKERS:
            for match in re.finditer(pattern, text):
                found.append((pattern, text[max(0, match.start() - 40):match.start() + 90]))
    return found


def build(source, destination, changelog_path):
    if os.path.abspath(source) == os.path.abspath(destination):
        raise SystemExit("refusing to overwrite the original manuscript")

    with zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        contents = {name: archive.read(name) for name in names}

    document, applied, counts, spans_runs = apply_edits(contents["word/document.xml"])
    contents["word/document.xml"] = document

    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.writestr(name, contents[name])

    remaining = scan_markers(ET.fromstring(document))
    unapplied = [e for e in EDITS if e[0] not in applied]

    lines = [
        "# FINAL_MANUSCRIPT_CHANGELOG.md",
        "",
        "Every substantive modification made to produce the IEEE-submission manuscript.",
        "",
        "| | |",
        "|---|---|",
        "| Source | `%s` (unmodified) |" % os.path.basename(source),
        "| Output | `%s` |" % os.path.basename(destination),
        "| Edits applied | **%d of %d** |" % (len(applied), len(EDITS)),
        "| Applied within a single run (formatting fully preserved) | %d |"
        % sum(1 for v in applied.values() if v == "in-run"),
        "| Applied by splicing across runs (all surrounding character formatting preserved) | %d |"
        % len(spans_runs),
        "| Draft markers remaining | **%d** |" % len(remaining),
        "",
        "Every replacement is traceable to `paper_update/MEASURED_RESULTS_V2.md`, to a "
        "file under `results/final_v2/`, or to `paper_update/LITERATURE_VERIFICATION.md`.",
        "",
        "---",
        "",
        "## Applied edits",
        "",
    ]
    for eid, search, replace, section, why in EDITS:
        if eid not in applied:
            continue
        lines += [
            "### %s — %s" % (eid, section),
            "",
            "**Was:** %s%s" % (search[:220].replace("\n", " "),
                               "…" if len(search) > 220 else ""),
            "",
            "**Now:** %s%s" % (replace[:320].replace("\n", " "),
                               "…" if len(replace) > 320 else ""),
            "",
            "**Why:** %s" % why,
            "",
            "*(applied %s%s)*" % (applied[eid],
                              "" if counts.get(eid, 1) == 1
                              else ", %d occurrences" % counts[eid]),
            "",
        ]

    if unapplied:
        lines += ["## NOT APPLIED — search text did not match (%d)" % len(unapplied), ""]
        for eid, search, replace, section, why in unapplied:
            lines += [
                "* **%s (%s)** — searched for: `%s`" % (eid, section, search[:150]),
                "  * intended: %s" % replace[:200],
                "  * **This must be applied by hand.**",
                "",
            ]

    lines += ["## Draft-marker scan of the OUTPUT document", ""]
    if remaining:
        lines.append("**%d marker(s) remain:**" % len(remaining))
        lines.append("")
        for pattern, context in remaining:
            lines.append("* `%s` — …%s…" % (pattern, context.replace("\n", " ")))
        lines.append("")
    else:
        lines += [
            "**None.** No `[VERIFY`, `[PENDING`, `[TO CONFIRM`, `[TO REPORT`, "
            "`[INSERT`, `TBD` or `TODO` remains anywhere in the submission "
            "manuscript.",
            "",
        ]

    lines += [
        "## Deliberately unchanged",
        "",
        "* Propositions 1–3, their statements and their proofs.",
        "* The claim boundary (Section XIV) and the non-contributions (Section I-D).",
        "* Every statement that RQ5 is preregistered and deferred; no comparative "
        "claim was added anywhere.",
        "* Case A's classification as synthetic and Case B's as a forensic "
        "reconstruction.",
        "* The evidence classification of the 284,807-event run as conformance-class "
        "work belonging to [15], not reproduced here.",
        "* The normative schema version, which remains **v1.0**.",
        "* The narrow novelty position in Section II-F: the paper still states that "
        "governance-to-code translation is not wholly unprecedented.",
        "",
    ]

    with open(changelog_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))

    return applied, unapplied, remaining, spans_runs


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", default=None)
    parser.add_argument("--changelog", default=os.path.join(
        REPO_ROOT, "paper_update", "FINAL_MANUSCRIPT_CHANGELOG.md"))
    args = parser.parse_args(argv)

    destination = args.out or os.path.join(
        os.path.dirname(os.path.abspath(args.source)),
        "From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx")

    applied, unapplied, remaining, spans = build(args.source, destination, args.changelog)

    print("wrote %s" % destination)
    print("wrote %s" % args.changelog)
    print("applied %d/%d edits (%d in-run, %d span runs)"
          % (len(applied), len(EDITS),
             sum(1 for v in applied.values() if v == "in-run"), len(spans)))
    for eid, search, _, section, _ in unapplied:
        print("  NOT APPLIED %s (%s): %s" % (eid, section, search[:90]))
    print("draft markers remaining in output: %d" % len(remaining))
    for pattern, context in remaining:
        print("  %s : ...%s..." % (pattern, context[:100]))
    return 0 if (not unapplied and not remaining) else 1


if __name__ == "__main__":
    raise SystemExit(main())
