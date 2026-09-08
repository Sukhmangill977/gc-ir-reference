# FIXTURE_PROVENANCE.md

Every value in this artifact that the method requires but the manuscript does not
state, recorded with the reason it was needed and the basis on which it was chosen.

**Why this file exists.** Case A is described in the manuscript as "synthetic but
fully specified". Fully specifying it means supplying fields the manuscript's prose
does not contain — an obligation's clause reference, a threshold contract's
uncertainty method, a non-runtime row's residual rating. Those values are research
fixtures. They are consistent with the manuscript, they are documented here, and
**none of them is a production observation or a measurement of anything.**

Three rules govern every entry:

1. A fixture is supplied only where the *method* requires a value. Where the
   manuscript is silent and the method does not need a value, nothing is invented.
2. A fixture is chosen on its own merits — plausibility for the described system —
   never to make a measured result come out a particular way.
3. Where a fixture choice could move a reported number, the sensitivity is
   measured and reported. See FP-014.

**Legend**

| Class | Meaning |
|---|---|
| **STATED** | The manuscript states this; reproduced, not invented. |
| **DERIVED** | Follows necessarily from something the manuscript states. |
| **FIXTURE** | The method requires a value; the manuscript does not state one. |
| **STRUCTURAL** | Required by the machine-readable schema, not by the method's substance. |

---

## Case A — investment research agent (evidence class: **synthetic**)

### FP-001 — Register rows, events, consequence classes and residual products — STATED
Source: manuscript Section IX table. The 13 runtime rows' `L × I` products, their
consequence classes, their gate sources and their `on_unknown` values are
reproduced exactly. The three non-runtime rows and their reason codes (R-14 RC-01,
R-15 RC-03, R-16 RC-01) are likewise stated.

### FP-002 — Profile scale and authority — STATED
"~220 analysts, ~3,200 briefs/month; draft-only authority (analyst approval
required); no trading connectivity in scope" (Section IX).

### FP-003 — R-10 rating decomposition L=2, I=5 — STATED
Section VII opens with "A rare unauthorized trade may score L=2, I=5 → 10", which
is R-10. The decomposition is taken from there rather than chosen.

### FP-004 — Rating decompositions for the other 12 runtime rows — **FIXTURE**
**Why needed.** The manuscript gives the *product* `s_i = L_i · I_i` for each row
but not the factors. The Monte Carlo experiment perturbs `L` and `I` separately
(Section XI-G), so it cannot run on products alone.

**Basis.** Each product was factored into the pair most consistent with the row's
described consequence: rows whose consequence is severe but whose event is
constrained take the higher impact and the lower likelihood; rows describing a
frequent generative failure take the higher likelihood.

| risk | product (stated) | L × I (fixture) |
|---|---|---|
| R-01 hallucinated facts | 20 | 4 × 5 |
| R-02 citation failure | 16 | 4 × 4 |
| R-03 stale data | 16 | 4 × 4 |
| R-04 biased framing | 12 | 3 × 4 |
| R-05 MNPI leakage | 15 | 3 × 5 |
| R-06 missing disclosures | 15 | 3 × 5 |
| R-07 prompt injection | 15 | 3 × 5 |
| R-08 unauthorized publication | 15 | 3 × 5 |
| R-09 unauthorized recommendation | 12 | 3 × 4 |
| R-10 unauthorized trading | 10 | **2 × 5 (STATED)** |
| R-11 model/vendor change | 16 | 4 × 4 |
| R-12 weak oversight | 12 | 3 × 4 |
| R-13 evidence failure | 10 | 2 × 5 |

**Effect on reported results.** The factorisation does not affect `DC`, `RCY`,
`NDR`, `OPR`, `ODC`, `PTC`, `CV`, `TD`, `GD(T_H)` or `GD_min` — all of those read
the product or the gate assignment only. It *does* affect the Monte Carlo flip
probabilities, because the perturbation acts on the factors. `results/final/monte_carlo_per_risk.csv`
reports the per-risk result for every row so the dependence is visible.

### FP-005 — Inherent ratings and control effectiveness — **FIXTURE**
**Why needed.** Step 5 requires inherent ratings, control effectiveness and
residual ratings as three separate concepts (Section III). The manuscript reports
only residual ratings ("L×I values are residual ratings", Section IX).

**Basis.** Inherent ratings are set at or above the residual on each dimension,
with `control_effectiveness` recording the gap. No reported metric reads them; they
are present so the record is structurally complete.

### FP-006 — Residual ratings for the three non-runtime rows R-14, R-15, R-16 — **FIXTURE**
See **FP-014** below — this is the one fixture that can move a reported number.

### FP-007 — Obligation matrix content — **FIXTURE** (framework identities STATED)
**Why needed.** Section IX names the obligation *sources* — "OSFI B-13/E-21/B-10/
E-23-readiness; CIRO Rule 3600 research supervision, with individual predicates
citing the applicable sections (notably ss. 3608–3622); privacy statutes;
securities/information-barrier requirements" — but Step 3 requires fourteen fields
per obligation including a clause anchor, an applicability basis, a deciding
authority and a legal-source version.

**Basis.** Twelve obligations were constructed over exactly the named sources. The
CIRO section anchors (ss. 3608, 3616, 3622) fall inside the range the manuscript
names. Three internal requirements (`INT-RES-QA`, `INT-EVID-CHAIN`,
`INT-NO-TRADE-CONN`) were added because the register contains rows whose authority
is internal rather than statutory, and the manuscript's obligation class
vocabulary includes `internal`.

**Not claimed.** The `requirement_text_hash` values are hashes of a fixture string,
not of real regulatory text. This is stated in the generator and is why the field
is populated with a clearly derived value rather than a plausible-looking one.

### FP-008 — Named individuals and organisational units — **STRUCTURAL FIXTURE**
Identities such as `forum.chair_l_tremblay`, `compliance.head_information_barriers`
and `exec.head_of_research` are role labels for a fictional organisation. They exist
so that separation-of-duty (Appendix A constraint 10) and approval-authority checks
have something to resolve against. No real person is named.

### FP-009 — The version-binding fingerprint — **STRUCTURAL FIXTURE**
`sha256:8f3a1d…` is an opaque fixture value. Nothing computes it from real
artifacts; it exists so `INV-VERSION` has a value to compare against.

### FP-010 — Catalog K entries — **FIXTURE** (predicate sketches STATED)
**Why needed.** Section IX gives a one-line "predicate sketch" per row. The method
requires each to resolve to a catalog entry with nine fields
(`event_type, observable_class, allowed_producers, triple_template,
allowed_operators, value_schema, evaluation_basis, evidence_schema,
permitted_responses`).

**Basis.** One entry per sketch, with the `evaluation_basis` that the sketch's
wording implies and that the closed set admits. Where the manuscript names a
producer it is used verbatim — `entity_resolution_service_v3` appears in the
Section V GC-IR example and is used for R-05.

### FP-011 — Threshold contracts — **FIXTURE**
**Why needed.** Section V requires that every numeric or temporal bound ship with
nine fields. Case A has three numeric conditions (R-03 freshness, R-04 skew, R-12
review dwell); the manuscript states none of the nine fields for any of them.

**Basis.** Each contract states a bound, a rationale for that bound, an explicit
uncertainty method, and a reproduction procedure. The values (2160 hours, 0.6,
180 seconds) are plausible for the described system.

**Not claimed.** These are not measured thresholds and no data supports the
specific numbers. What the artifact demonstrates is that the *contract structure* is
enforced — `tests/adversarial` ADV-029 through ADV-032 show that an incomplete
contract is rejected.

### FP-012 — Hazardous action path declarations — **DERIVED**
The coverage rule is stated over "each authorized hazardous action path associated
with `r_i`". The association must be recorded somewhere machine-readable, so each
register row carries `hazardous_action_paths`, and the authority matrix marks which
entries are hazardous. Which paths are hazardous follows from the manuscript's own
criterion — externally effective or non-rescindable — applied to Case A's matrix:
`publish_report` (a distributed brief is not rescindable from readers who have
acted on it) and `invoke_tool` (a tool target outside the manifest would be an
unauthorized authority exercise).

### FP-013 — RC-04 is reserved and unused — **DERIVED**
The manuscript names RC-01, RC-02, RC-03 and RC-05 and says the codes are "closed
at schema v1.0". RC-04 is never defined. Rather than invent a meaning for it or
renumber the others, `RC-04` is recorded as reserved-unused in
`src/gcir/models.py` and excluded from the schema enum. A disposition citing RC-04
is rejected (ADV-053).

### FP-014 — Residual ratings for R-14, R-15, R-16, and their effect on `GD_min` — **FIXTURE WITH MEASURED SENSITIVITY**

**Why needed.** Section IX states that "Both sums run over all sixteen register
rows, non-runtime dispositions included: those rows carry ratings but no gate".
So `GD(T_H)` and `GD_min` require ratings for R-14, R-15 and R-16 — and the
manuscript's Section IX table gives `L × I` only for the 13 runtime rows.

**Committed fixture values.**

| risk | L × I | product | basis |
|---|---|---|---|
| R-14 concentration / resilience (single-vendor retrieval stack) | 3 × 4 | 12 | A material third-party concentration on a service supporting a critical business operation; OSFI B-10 and E-21 treat such concentration as a significant exposure. |
| R-15 unprofessional or damaging tone | 3 × 2 | 6 | Reasonably likely given unconstrained generation, but low impact: the brief is reviewed and internally distributed, and tone is correctable before it reaches anyone. |
| R-16 third-party vendor commercial viability | 2 × 4 | 8 | Unlikely over the review cycle for a contracted vendor, but a withdrawal would remove the model capability the pipeline depends on. |

**Measured sensitivity.** Because these three rows enter both `GD` sums, their
ratings can move `GD_min`. `experiments/run_gate_divergence.py` therefore sweeps
every `(L, I)` in `{1..5}²` for each of the three rows — 15,625 combinations — and
reports the resulting `GD_min` distribution in `results/final/gate_divergence.json`
and in `SUMMARY.md`.

**Measured result:** with the committed ratings `GD_min = 3`; across the full
sweep `GD_min` ranges over **2 to 5**. `GD(15) = 3` is *not* sensitive to these
rows (any product below 15 leaves them in agreement with the heat-map rule at the
declared threshold), and neither Proposition 1 nor Proposition 2 depends on them —
both premises are instantiated entirely by runtime rows the manuscript states
(R-10 gated at 10 vs R-04 ungated at 12; the collision at s = 12).

**What this means for the manuscript.** `GD_min = 3` is a correct measurement of
the pinned artifact, but it is partly a function of three ratings the manuscript
does not publish. `paper_update/MEASURED_RESULTS.md` recommends wording that
states the ratings alongside the result.

### FP-015 — Case A validation seeds (VS-01, VS-02, VS-03) — **DERIVED**
Section IX: "WC-01 and RC-05 handling are exercised in the machine-readable
artifact's deliberately seeded validation rows." Those rows must therefore exist
and must sit *outside* the release-admissible register, or Case A's disposition
counts would not be 13/3/0/0. They are constructed in
`experiments/run_adversarial.py::run_validation_seeds` and their outcomes recorded
in `results/*/adversarial.json`. VS-03 (RC-02) was added for completeness so that
all four live reason codes are exercised.

---

## Case B — transaction authorization agent (evidence class: **forensic reconstruction**)

### FP-016 — Register rows, consequence classes, gate sources and products — STATED
Section X table, including **B-04's stated decomposition L=1, I=5**.

### FP-017 — Authority matrix — DERIVED from STATED
"The authority matrix admits exactly one external action (`release_payment`) with
bound parameters" (Section X). The matrix contains exactly one hazardous entry.
The bound parameters (`transaction_hash`, `currency`, `rail`) are a structural
fixture; the manuscript says the parameters are bound but not which they are.

### FP-018 — Obligations, catalog, threshold contracts, identities — **FIXTURE**
Constructed on the same basis as Case A's. The two numeric bounds
(CAD 250,000.00 per transaction; 20 releases per counterparty per hour) are
plausible fixtures with stated rationales, not measured values.

### FP-019 — What Case B does *not* contain — **deliberate absence**
The 284,807-event golden-trace conformance run reported in [15] is **not**
reproduced, re-run, or cited as evidence for any claim in this artifact. Section X
is explicit that that run "is not detection evidence and is not presented as such",
and that what Case B adds here is upstream: the register-to-disposition-to-predicate
mapping. `cases/case_b/inputs/assessment.json` carries
`"case_class": "forensic_reconstruction"` and its `method` field records that the
register was reconstructed retrospectively.

---

## Experiment parameters

### FP-020 — Monte Carlo rating distributions are AUTHOR-SPECIFIED, not panel-adjudicated — **METHODOLOGICAL DEVIATION**

**The manuscript says** (Section XI-G): "For each risk `r_i`, the independent panel
freezes discrete probability masses over plausible ratings."

**The fact is:** no independent adjudication panel has been convened. The panel
described in Section XI-C is part of the deferred RQ5 protocol. Supplying
distributions and attributing them to a panel that has not met would be fabrication.

**What this artifact does instead.** It supplies a single, simple, a-priori
perturbation rule, frozen in `preregistration/monte_carlo_distributions_v1.json`
before any result was computed, and labels it what it is:

> symmetric ±1 ordinal perturbation with clamping — probability 0.6 on the approved
> rating and 0.2 on each adjacent rating on the 1–5 scale, with mass that would fall
> outside the scale reassigned to the approved rating.

The rule was chosen because it is the simplest defensible model of ordinal rating
disagreement, not because it produces any particular number. A secondary variant
(renormalising the boundary mass instead of reassigning it) is also run and reported,
so the reader can see how much the boundary convention matters.

**Consequence for the claim.** The Monte Carlo result is a **sensitivity analysis
under a declared perturbation model**. It supports the qualitative claim that
heat-map gate membership moves under rating uncertainty while `C*` membership does
not. It does **not** estimate how uncertain real enterprise ratings are, and it must
not be reported as an independently adjudicated result.
`paper_update/MEASURED_RESULTS.md` gives the exact wording change this requires.

### FP-021 — The `C*` flip probability is verified, not assumed
`FP^{C*} = 0` is a structural consequence of the coverage rule, which reads the
consequence descriptor and never reads `L` or `I`. The experiment nevertheless
re-runs the real `C*` classifier on 1,000 randomly selected perturbed draws per case
and reports how many changed. A non-zero count would mean a rating dependence had
leaked into gate assignment. The count is a measurement.

### FP-022 — The declared heat-map threshold `T_H = 15`
Stated for Case A ("against the enterprise's predeclared threshold `T_H = 15`",
Section IX). The manuscript does not state a `T_H` for Case B; the same value is
used there for comparability, and `GD(15)` for Case B is reported as a new
measurement rather than as a manuscript value.

### FP-023 — Determinism run matrix — **DESIGN CHOICE**
The manuscript reports 31 runs. This artifact runs ≥ 30 per case (≥ 60 total),
generated from a fixed matrix seed so the matrix is identical on every execution and
on every CI platform. The dimensions exercised are listed in
`docs/EXPERIMENT_PROTOCOL.md`.

### FP-024 — Determinism permutations are re-signed
A signature binds an exact document. Re-ordering an object's *keys* leaves the
document unchanged under RFC 8785, so those signatures still verify. Re-ordering an
*array* changes the document and the signature correctly stops verifying — so the
permuted inputs are re-signed **by the same authority key** named in
`compile_parameters.signing_authorities`. This models an equivalent authoring order
that the same governance authority would have signed. Nothing about the signature
check is bypassed: `tests/adversarial` ADV-018/019/020 confirm that a document
edited after signing, a document signed by an unauthorized key, and an unsigned
document are all still rejected.

---

## Cryptographic material

### FP-030 — Research signing keys are deterministic and TEST ONLY
The Ed25519 keys in `keys/` are derived from the fixed seed string in
`tools/build_cases.py` (`KEY_SEED`), so a reviewer regenerating the case artifacts
from a fresh clone obtains byte-identical public keys and signatures. That
reproducibility is why the private keys are committed, and it is also why they must
never be used for anything else. Every key file and `keys/README.md` carry the
banner **TEST ONLY / NOT FOR PRODUCTION**.

`key.unauthorized_party` is a deliberate negative control: it exists only to sign
fixtures that audit query Q6 and the adversarial suite must reject.

---

## What was NOT invented

For completeness, values the artifact deliberately leaves absent rather than
filling in:

* **SNR and DF** — RQ5 outcomes. Reported as `DEFERRED` with a reason, never as numbers.
* **Inter-rater reliability statistics** (Fleiss' κ, Krippendorff's α, Gwet's AC1) —
  require raters. None exist.
* **Bayesian posterior estimates** for the comparative analysis — require the study.
* **Any DOI** — no Zenodo deposit has been made. `docs/ZENODO_RELEASE_STEPS.md`
  records the remaining manual steps instead of inventing an identifier.
* **RC-04** — see FP-013.
* **Detection, false-denial or production-impact figures** — out of scope.
* **The 284,807-event run** — belongs to [15]; see FP-019.
