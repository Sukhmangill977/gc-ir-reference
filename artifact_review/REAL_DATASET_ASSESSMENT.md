# Does this paper need a real dataset?

An honest answer to a question that is easy to answer dishonestly in either
direction. Adding a real dataset would make the repository *look* stronger. The
question is whether it would make any **current claim** better tested.

---

## Verdict

# REAL DATASET NOT REQUIRED FOR CURRENT TIER-0 CLAIMS.

Every claim the article makes is reproducible from its actual declared inputs, and
no claim is of a kind that observational data could test. The reasoning is below,
claim class by claim class, followed by the candidate experiments that *were*
considered and what each would and would not buy.

---

## Why not — by claim class

The article's claims fall into four classes (`paper_update/FINAL_CLAIM_EVIDENCE_AUDIT.md`).

### C1 — Proved (Propositions 1–3)

These are mathematical statements about the non-representability of an approved
gate assignment by a monotone function of a scalar score. Their **premises** are
instantiated on a register — Case A exhibits a score inversion and a score
collision with divergent gates. A real register could also exhibit those premises,
but it could not make the propositions *more* proved: a proof is not strengthened
by additional instances. A real register that *failed* to exhibit the premise
would not refute the propositions either; it would just be a register where the
comparator happens to work, exactly as Case B already is (GD_min = 0, reported
rather than suppressed).

**Real data adds nothing to a proof.**

### C2 — Measured (DC, RCY, NDR, OPR, ODC, PTC, CV, GD, GD_min, TD, Monte Carlo)

These measure **properties of the compiler Φ and of the compiled bundle**, not
properties of the world:

* `DC = 1` holds *by construction* once dispositions are signed. On a real
  register it would still be 1, for the same structural reason.
* `OPR = 0`, `ODC = 1`, `PTC = 1`, `CV = 1` are compiler guarantees verified
  structurally. A real register cannot falsify them without falsifying Φ, and if Φ
  had a defect a synthetic adversarial case exposes it more cheaply and more
  precisely — which is what the 62-case corpus is for.
* `TD` measures whether semantically equivalent inputs produce the same canonical
  payload hash. This is a property of the serializer and the compiler. Real
  register content would exercise the same code path with different strings. The
  determinism experiment already varies input content structurally (row and key
  permutation, numeric re-encoding) across 62 runs on 8 environments; real prose
  would add volume, not a new failure mode. **Note:** this experiment did catch a
  genuine Φ defect — the catalog was hashed as authored rather than canonically —
  and it caught it with synthetic inputs.
* `GD` and `GD_min` measure divergence between an approved gate assignment and a
  declared heat-map comparator **on a given register**. Here a real register would
  genuinely add something — see Candidate 1 below — but it would be a *new claim*
  about prevalence, not better evidence for the existing one.
* The Monte Carlo analysis is explicitly a **sensitivity analysis under a declared
  model**, and the article says so. Real ratings would not validate the model; they
  would replace it, which is a different experiment.

**Real data would not improve the measurement of any C2 quantity as currently
claimed.**

### C3 — Argued (design and positioning)

Novelty positioning, the Ψ_K refinement boundary, the absence of inference inside
Φ, separability from the enforcement architecture. These are established by
reading the released implementation and by the literature review. No dataset
speaks to them.

### C4 — Deferred (RQ5)

The one genuine evidential gap — comparative superiority over unaided manual
translation — needs **human participants**, not a dataset. `SNR` and `DF` require
an adjudicated reference standard produced by a panel that has not been convened.
No amount of observational data substitutes for that study, and the study is
already preregistered and hash-committed.

**The gap that matters is a human study, and it cannot be closed with data.**

---

## Candidate real-data experiments considered

Each is assessed against the required fields. **None is required; one is
genuinely valuable.**

### Candidate 1 — A real enterprise AI risk register (prevalence of the Proposition 1/2 premises)

| Field | Assessment |
|---|---|
| **Claim tested** | *New claim*, not an existing one: that score inversions and divergent-gate score collisions occur in real enterprise registers at non-trivial frequency. The article currently claims only that they occur **in the pinned register**, which is measured and true. |
| **Dataset needed** | 20–100 real enterprise AI risk registers with approved ratings **and** an approved gate/consequence-class assignment. The gate assignment is the hard part: most organisations rate risks but never record a class-based gating decision. |
| **Availability** | **Very poor.** Approved risk registers are internal, commercially sensitive, and typically privileged. No public corpus exists. |
| **License** | Would require individual negotiated agreements per organisation. |
| **Privacy** | Registers name systems, business lines and sometimes individuals. Would need de-identification, which risks destroying the very rating/gate structure being studied. |
| **New methodology required** | Yes — substantial. A sampling frame, a de-identification protocol, an inter-organisation rating normalisation scheme, and a way to establish what the "approved gate" is when organisations do not record one. |
| **Changes the claim class?** | **Yes.** It would add a new C2 empirical-prevalence claim, moving the paper from "this structure is possible and here is a case" to "this structure is common". That is a stronger and more interesting paper. |
| **New prospective freeze required?** | **Yes.** New hypotheses, new outcomes, new analysis — a new preregistration and a new manuscript. |
| **Verdict** | **Valuable but out of scope.** It answers a question the paper does not currently ask, and answering it is a research programme, not a packaging task. |

### Candidate 2 — Executing the compiled Case B bundle against the 284,807-event corpus

| Field | Assessment |
|---|---|
| **Claim tested** | Would test **detection performance**, which this paper explicitly disclaims (§I-D, §X, §XI). It would not test any claim the paper makes. |
| **Dataset needed** | The corpus used by [15]. |
| **Availability** | Belongs to the prior work; obtainable. |
| **License / privacy** | Whatever governs that corpus; likely permissive, but irrelevant given the verdict. |
| **New methodology required** | Yes — a detection-performance evaluation protocol, ground-truth labelling semantics, and a decision on what a "correct" gate decision means per event. None exists here. |
| **Changes the claim class?** | **Yes, and dangerously.** It would move the paper into a claim class (C3/C4 → detection evidence) that its evaluation design does not support and that §XIV explicitly excludes. The 284,807-event run in [15] is a *golden-trace conformance* result with predicates pre-set from labels; re-running it here would either duplicate prior work or be mistaken for detection evidence. |
| **New prospective freeze required?** | Yes. |
| **Verdict** | **Do not do this.** It risks the exact overclaim the article has been carefully written to avoid. The 13 injection scenarios already establish the defensible version — that the compiled bundle refuses to permit under each published hazard class — and they are labelled as *not* detection evidence. |

### Candidate 3 — Real practitioner-authored registers for the deferred study

| Field | Assessment |
|---|---|
| **Claim tested** | SNR and DF — the deferred RQ5 primary outcomes. |
| **Dataset needed** | Not a dataset: **human participants** plus a held-out register and a three-person adjudication panel. |
| **Availability** | Requires recruitment and ethics review. |
| **Privacy** | Human-subject data; requires consent and an ethics protocol. |
| **New methodology required** | No — the protocol is already written and frozen in `preregistration/RQ5_DEFERRED_PROTOCOL.md`. |
| **Changes the claim class?** | Yes — it would convert the paper's one deferred claim into a measured one. |
| **New prospective freeze required?** | The Tier-1 freeze is already specified and must be published **before recruitment opens**. |
| **Verdict** | **This is the study that matters**, and it is already committed. It is a human-subjects study, not a dataset acquisition. |

### Candidate 4 — Public AI incident databases (e.g. incident repositories)

| Field | Assessment |
|---|---|
| **Claim tested** | None directly. Incident records describe harms that occurred; they do not contain approved risk ratings, approved gate assignments, or an authority matrix. |
| **Dataset needed** | A public incident corpus. |
| **Availability** | Good. |
| **License** | Generally permissive. |
| **Privacy** | Generally already public. |
| **New methodology required** | Yes — a mapping from narrative incident reports to a structured governance assessment. That mapping is *exactly the human interpretive step the paper declines to automate* (§I-D: "deterministic interpretation of unconstrained risk prose" is a non-contribution). Automating it would contradict the paper's central methodological position. |
| **Changes the claim class?** | Yes, and it would undermine Ψ_K's design premise. |
| **Verdict** | **Actively contrary to the method.** Rejected. |

---

## OPTIONAL FUTURE / TIER-0.5 VALIDATION

One experiment is worth describing as a genuine, bounded improvement. **It has not
been executed and requires author approval before any work begins.**

### Proposal: a second, independently authored synthetic register

**Not a real dataset** — a synthetic register authored by someone other than the
method's author, from a written brief, without seeing Case A or the catalog.

**What it would test.** The strongest reviewer objection to this artifact
(`FINAL_REVIEWER_RISK_REPORT.md` R-02) is that both cases were authored by the
party proposing the method, so metrics like `DC = 1.000` and `CV = 1.000` are
conformance of a self-authored artifact to its own constraints. A register
authored independently would test whether Φ's guarantees hold on inputs its author
did not shape — which is a real, currently untested question, and one that
requires no external data, no privacy review and no license.

**What it would NOT test.** Not comparative superiority (still RQ5). Not detection.
Not real-world prevalence. It narrows the self-authorship objection; it does not
eliminate it, since the register would still be synthetic.

| Field | Assessment |
|---|---|
| Dataset needed | None. A written system brief and an independent author. |
| Availability | Requires one qualified person, a few days. |
| License / privacy | None — fully synthetic. |
| New methodology required | Minimal: a blind-authoring protocol and a pre-declared success criterion. |
| Changes the claim class? | No new claim class. It **strengthens the existing C2 claims** by widening their input base. |
| New prospective freeze required? | **Yes.** New inputs and a new outcome must be frozen before execution, as Tier-0.5, published before it runs. |
| Cost if it fails | Informative either way. If Φ's guarantees do not hold on an independently authored register, that is a finding worth reporting. |

**Status: proposed, not executed. Awaiting author approval.** Nothing in the
repository has been changed in anticipation of it.

---

## What was explicitly not done

* No dataset was downloaded, added, or referenced to make the repository appear
  stronger.
* No synthetic input was relabelled as real.
* No experiment was run, tuned or re-run.
* The manuscript was not modified.

If a real-data experiment is later approved, it must be treated as a **new
empirical experiment with its own prospective freeze and its own manuscript
update** — never as an extension of `preregister-tier0-v2.2`.
