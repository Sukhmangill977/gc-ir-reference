# FINAL_REVIEWER_RISK_REPORT.md

An adversarial read of `From_Risk_Register_to_Runtime_Predicate_IEEE_SUBMISSION.docx`,
written as a hostile reviewer would write it.

The goal is **not** to make the limitations disappear. It is to establish that every
limitation is honestly bounded in the manuscript, and to name the ones that are not.

| Class | Meaning |
|---|---|
| **BLOCKER** | Must be resolved before submission. The paper is not submittable while it stands. |
| **MAJOR** | A reviewer will raise it. It is disclosed and bounded, but it constrains what the paper can claim, and may still cost a recommendation at a demanding venue. |
| **MINOR** | Worth fixing or watching. Does not threaten the contribution. |
| **ACCEPTABLE LIMITATION** | Disclosed, bounded, and legitimate for a method paper at this stage. |

---

## BLOCKERS

**None identified.**

Specifically checked and clear: no fabricated result, hash, timestamp or execution; no
DOI invented; no human-panel involvement claimed; no detection, production or
independent-validation evidence claimed; no comparative-superiority claim; no draft
marker remaining; the original manuscript file is byte-identical to what it was
(`003db273…aa4869`); and the frozen artifact passes all 24 checks of
`tools/freeze_check.py --final-v2` after finalization.

Two items below (R-01 and R-02) are **author action items** rather than blockers, but
they require the author's own confirmation and I cannot discharge them.

---

## MAJOR

### R-01 — Three references could not be verified against a reachable primary source

**The attack.** *"Reference [21] and [22] are arXiv preprints with 2026 identifiers I
cannot locate, and [15] is cited without a DOI."*

**Status.** [21] (Cilla Ugarte et al., arXiv:2604.13767), [22] (Sharma and Kunkel,
arXiv:2605.23297) and the final DOI of [15] could not be confirmed from a reachable
primary source during the verification sweep — arXiv listing pages and IEEE Xplore were
not retrievable. **No bibliographic data was invented to fill the gap**; [15] now cites
its early-access article number instead of a DOI.

**Required action — author only.** Confirm the arXiv identifiers, author lists and
titles of [21] and [22] against the actual abstract pages, and insert [15]'s DOI once
IEEE assigns it (see `ZENODO_AND_DOI_INSERTION_POINTS.md`). If either arXiv identifier
is wrong, correct it; a wrong preprint number is the kind of error a reviewer treats as
carelessness about the whole reference list.

### R-02 — Both cases are authored by the same party as the method

**The attack.** *"Case A is synthetic and Case B is a forensic reconstruction. Both were
authored by the person proposing the method. Of course the method achieves DC = 1.000
and CV = 1.000 on them."*

**This is the strongest objection in the paper and it is substantially correct.** DC = 1
is achieved *by construction* once dispositions are signed — the manuscript says so
explicitly — so measuring it demonstrates that the artifact conforms to its own
constraint, not that the method disposes of risks a practitioner would have missed. The
same holds for CV, ODC, PTC and OPR: they are conformance checks on a self-authored
artifact.

**What the paper can legitimately claim,** and does: these metrics establish that the
compiler enforces its declared invariants and that no orphan predicate or undisposed
risk can survive compilation. That is a real property of Φ, and the adversarial corpus
(62 cases, each required to fail with its *predicted* error code) is what makes it more
than self-report.

**Bounded in:** §I-D non-contributions, §IX ("Case is synthetic"), §X ("forensic
reconstruction — stated openly"), §XII limitations, §XI-C.

**Residual risk.** A reviewer may still hold that n = 2 self-authored cases is
insufficient evaluation for the venue. Nothing in this artifact can answer that; only
the deferred study can.

### R-03 — The paper's central practical claim is untested

**The attack.** *"You claim manual translation is unreliable and that this method fixes
it. Where is the evidence a human analyst does worse?"*

**Status.** There is none, and the paper does not claim any. RQ5 is preregistered,
publicly hash-committed and deferred; SNR and DF report *"primary outcome of the
deferred comparative study; not reported here"*; §XI-C now states that the adjudication
panel **has not been convened** and no reference standard exists.

**Residual risk.** This is a venue-fit risk, not an integrity risk. A reviewer who
expects an empirical comparison will find the evaluation incomplete regardless of how
honestly the gap is stated. The mitigation is that the paper is positioned as a method
and formalization paper, and its C1/C2 claims stand without the study.

### R-04 — "Determinism" is reproducibility of one implementation, not of a specification

**The attack.** *"Eight environments all run the same source tree from the same
lockfile. You have shown one program is deterministic, not that the specification admits
only one output."*

**This is correct and is the sharpest technical objection.** No second, independent
implementation of Φ was written, so specification-level determinism — that any conformant
implementation produces the same canonical payload hash — is **not** established. What
is established is that this implementation reproduces identical hashes across three
operating systems, two architectures, six CPython patch versions, five locales, five time
zones, input permutation and clean-process execution.

**Partially bounded.** §XII states the claim is *"determinism across the tested supported
environments"* and denies platform independence. It does **not** currently distinguish
implementation determinism from specification determinism.

**Recommended,** if the author wishes to close this: one sentence in §XII noting that a
second independent implementation would be required to establish specification-level
determinism, and that RFC 8785 conformance is what makes that plausible rather than
demonstrated. I have **not** added it, because it is a substantive scope statement and
the author should decide whether to make it.

**Genuine mitigating evidence:** the determinism experiment found a real ordering defect
in Φ (the catalog was hashed as authored rather than canonically), which is reported in
§XI-H. An experiment that catches its own implementation's bug is not a rubber stamp.

### R-05 — The Monte Carlo model is chosen by the party whose result it supports

**The attack.** *"A ±1 symmetric perturbation with mass 0.6/0.2/0.2 is your choice. A
wider model might move C* membership too."*

**Status.** The distributions are author-specified, prospectively frozen in the public
preregistration before any result was computed, and now labelled as such in the abstract,
§XI-C, §XI-G and §XII (edits E03, E12, E13, E18). A secondary variant that renormalizes
out-of-scale mass instead of reassigning it is reported (0.352 versus 0.321), which
demonstrates the result is not knife-edge on that particular choice.

**Residual risk.** Only sensitivity *under a declared model* is claimed; the true
dispersion of enterprise rating judgment is not estimated, and the manuscript says so.
That FP^C* = 0.000 is structural — C* membership is not a function of the perturbed
ratings — is arguably the point, but a reviewer may fairly call the result close to
tautological. Proposition 3 is what carries the claim; the simulation corroborates.

### R-06 — Novelty against very recent adjacent work

**The attack.** *"Koch [28] proposes a layered translation method from governance norms
to runtime guardrails. How is this different?"*

**Status.** [28] (arXiv:2604.05229, Apr. 2026) was found during the final sweep and is
now cited and distinguished in §II-F as the closest neighbour: it addresses the same
translation question but supplies neither canonical serialization and bundle hashing, nor
total risk disposition, authority-matrix closure, or receipt-level traceability. [29]
(deontic policies for agentic systems) is cited as governing constraints that already
exist rather than deriving them.

**Residual risk.** The novelty position is now a *combination* claim over five
properties, which is weaker than an absence-of-prior-art claim but defensible and, more
importantly, true. Failing to cite [28] would have been the more dangerous outcome.

### R-07 — Self-citation and the risk of a salami-slicing charge

**The attack.** *"[15], [16] and [17] appear to be the same author's prior work, and this
paper consumes their interfaces. Is this a distinct contribution?"*

**Status.** §XIII exists for exactly this and states the separation contribution by
contribution: this paper supplies the upstream refinement and compilation method, the
gate-coverage formalization with its three propositions, and the temporally valid
traceability model, and repeats none of the enforcement architecture. The separation was
checked at submission against the released artifact (edit E19).

**Recommended.** §XIII does not currently state that [15]–[17] are the author's own prior
work; it reads as third-party related work. At a single-blind venue, making the
relationship explicit strengthens the section rather than weakening it, and pre-empts the
charge. **Author's call** — it is a disclosure decision, not a correction, so I have not
made it.

---

## MINOR

### R-08 — GD_min depends on three undisclosed-until-now fixture ratings

Case A rows R-14, R-15 and R-16 carry residual ratings supplied as documented fixtures
rather than derived from the case narrative. The ratings are now published in §IX
(R-14 = 12, R-15 = 6, R-16 = 8), and a sweep over all plausible (L, I) values shows
GD_min would range from 2 to 5. §XII discloses this. Neither proposition premise depends
on those rows. **Bounded; a reviewer can now check the number.**

### R-09 — The s = 12 collision was described as "three-way"

Non-runtime row R-14 also rates 12, so the collision has four members over the full
register. Corrected in both the body and the figure caption (edits E05, E07) by scoping
the sentence to the runtime rows. Proposition 2 is unaffected. **Resolved.**

### R-10 — Schema `$id` values are not resolvable

Appendix A now states this plainly: the `$id` values are stable identifiers within the
v1.0 namespace, not endpoints, and the authoritative copies are the schema files in the
tagged release. A reviewer may prefer resolvable URIs; none is maintained, so none is
claimed. **Bounded.**

### R-11 — Reference [18]'s article number is disputed

One indexing record gives art. 102, the manuscript gave 104, and neither ACM nor dblp was
retrievable to settle it. The disputed field was removed; volume, issue, year and DOI
locate the work unambiguously. **Resolved by removal rather than by guessing.**

### R-12 — T_H = 15 is author-declared

Gate divergence at a declared threshold inherits that threshold's arbitrariness. The
mitigation is already in the paper: GD_min is the threshold-free minimum over all
thresholds, and it is GD_min > 0 that carries Proposition 1's premise. **Bounded by
construction.**

### R-13 — Propositions 1 and 2 may be read as elementary

A reviewer may observe that "no monotone scalar threshold reproduces a non-monotone
assignment" is close to immediate once stated. The paper's value there is the
formalization and the demonstration that a real enterprise register exhibits the premise,
not the depth of the proof. **Presentational risk only.**

---

## ACCEPTABLE LIMITATIONS

These are disclosed, bounded and appropriate for a method paper at this stage. No action.

| # | Limitation | Where bounded |
|---|---|---|
| A-1 | Legal applicability determination remains a human function; Step 3 is not automated. | §I-D, §II-F |
| A-2 | Human interpretation is never claimed deterministic; Ψ_K is closed only by a signed judgment record. | §V |
| A-3 | Runtime detection performance is out of scope and belongs to [15]. | §I-D, §X, §XI |
| A-4 | The 284,807-event run is conformance-class evidence from prior work, not reproduced here, and the compiled Case B bundle was **not** executed against that corpus. | §X |
| A-5 | Case B's L-DREA mapping establishes continuity of predicate family only. Two gaps are declared, not glossed: no rolling-velocity predicate exists in that family, and version identifiers appear as trace columns but not in its predicate vector. | §X |
| A-6 | The orphan-control guarantee is a compiler guarantee and extends to deployment only under the explicit runtime acceptance condition. | §VI, App. A |
| A-7 | The held-out register is not authored and is committed in a Tier-1 freeze before recruitment opens. | §XI-I |
| A-8 | No archival DOI exists; the release tag and hash manifest are the citable artifact. | Data & Code Availability |
| A-9 | Shadow-mode deployment is future work for a subsequent paper. | §XV |

---

## Verdict

**No blocker.** The manuscript makes no claim its evidence does not support, every
limitation identified above is either bounded in the text or listed here as an
author action item, and the frozen scientific artifact was not modified during
finalization.

**Before submitting, the author must:**

1. Verify references [21] and [22] against their arXiv abstract pages (R-01).
2. Decide on the two optional strengthenings — the specification-versus-implementation
   determinism sentence (R-04) and explicit self-citation disclosure in §XIII (R-07).

Neither is a correctness defect. The first is a verification I could not complete; the
second two are the author's editorial and disclosure judgment.

**The realistic reviewer outcome** is a challenge on evaluation sufficiency (R-02, R-03)
rather than on integrity. That challenge is answered by the deferred study, not by
anything that could have been added here — and the paper is explicit that it has not been
answered yet.
