# TIER0_FREEZE_V2.md — Public preregistration freeze for the v2 reportable campaign

**Freeze version:** `tier0-v2`
**Git tag:** `preregister-tier0-v2`
**Supersedes:** `tier0-v1` / `preregister-tier0-v1`

---

## Why there is a v2

The v1 freeze was created, tagged and verified **locally**, and the v1 campaign
executed against it. Every substantive guarantee held: 117 frozen files matched
the manifest at the freeze commit, the results were produced at that commit, and
no frozen file changed in between.

**But the v1 tag had not been pushed when the v1 campaign ran.** Section XI-I is
explicit:

> "The internal selection of frozen elements is not a freeze — the public
> timestamped commitment is."

A local tag's date is author-settable. **A later push cannot convert a past
experiment into a prospectively public preregistered one.** Backdating the claim
by pushing v1 afterwards and calling the v1 campaign publicly preregistered would
be exactly the kind of retroactive relabelling preregistration exists to prevent.

So the v1 campaign is **not** relabelled, its metadata is **not** edited, and
`public_commitment_discharged` is **not** flipped retroactively. Instead this v2
freeze is pushed publicly *first*, and a **completely new campaign** is executed
against it afterwards.

`results/final/` (v1) is retained, unedited, marked superseded. `results/final_v2/`
carries the reportable numbers. `results/V1_V2_COMPARISON.md` compares them.

## The ordering this freeze asserts, and how to check it

| # | Step | Verifiable by |
|---|---|---|
| 1 | All code and artifact changes complete | this commit's tree |
| 2 | Freeze v2 manifest generated over the frozen set | `preregistration/FREEZE_MANIFEST_V2.sha256` |
| 3 | Freeze committed | the commit this tag points at |
| 4 | Tag `preregister-tier0-v2` created | `git rev-list -n 1 preregister-tier0-v2` |
| 5 | **Commit and tag PUSHED to GitHub** | `git ls-remote --tags origin preregister-tier0-v2` |
| 6 | Remote tag verified present | `results/final_v2/PROVENANCE.json` → `public_freeze.remote_tag_verified` |
| 7 | **Only then**: the v2 campaign executed | every `results/final_v2/*.json` records its execution commit |
| 8 | Results committed afterwards, separately | the commit after this tag |

`python -m experiments.verify_freeze --tag preregister-tier0-v2` checks 2, 3, 5,
6 and 7 mechanically, including the substantive property a timestamp cannot fake:
**no frozen file changed between the freeze commit and the commit the campaign ran
at.**

## What changed between v1 and v2 (all before this freeze)

Driven by the audit in `docs/ARTIFACT_RUNS_COMPLIANCE.md`:

1. **Determinism matrix restratified to 31 per case, 62 total** — the examiner's
   10 repeats + 10 row shuffles + 5 key shuffles + 3 `LC_ALL` + 3 `TZ` breakdown,
   replacing the v1 unstratified 30 per case. Each run now also records an
   environment fingerprint.
2. **Case B → L-DREA traceability** — machine-verified mapping to the **thirteen
   real** predicate identifiers derived from the published artifact
   (`Gate_A1`…`Gate_A7`, `Lambda_G`, `TOKEN_VALID`, `AuthoritySignatureValid`,
   `HARM_RISK_THETA`, `STALE_CONTEXT`, `TELEMETRY_STALE`). No `P1–P13` identifiers
   were fabricated; see `docs/CASE_B_LDREA_TRACEABILITY.md`.
3. **Thirteen Case B injection scenarios** — the published artifact's own 8
   adversarial + 5 ASB families, each executable and each asserted to resolve to
   `SAFE_STATE` against a clean PERMIT control.
4. **New `timeout` failure class** — `constraint_03b`: a mandatory condition
   declaring a temporal window must carry a threshold contract stating the
   freshness bound and its unit, or "stale" is undefined and stale evidence
   cannot fail closed. Cases ADV-055, ADV-056, POS-006.
5. **State-mismatch detection** — a receipt that *omits* mandatory predicates the
   bundle requires is now detected, complementing the injected-predicate direction.
6. **Reproduction entry points at the memo's paths** — `tools/freeze_check.py`,
   `tools/montecarlo.py`, `tools/td_crossenv.py`, `run_all.py`. All are thin
   documented wrappers; no freeze or analysis logic is duplicated.

**Retained unchanged from v1, deliberately:** the schema at **v1.0** (the
manuscript is normative at v1.0 in three places; the memo's "v1.1" has no stated
revision — see `ARTIFACT_RUNS_COMPLIANCE.md` §C2), and the **author-specified**
Monte Carlo distributions (§D).

## Hypotheses and primary outcomes (frozen)

| RQ | Question | Primary outcome | Status |
|---|---|---|---|
| RQ1 | Does every risk receive exactly one approved disposition? | `DC` | measured |
| RQ2 | Do semantically equivalent inputs produce the same canonical payload hash? | `TD` over **62 runs** | measured |
| RQ3 | Does consequence-class coverage differ from the heat-map comparator? | `GD(T_H)`, `GD_min` | measured |
| RQ4 | Traceability without orphan or temporally invalid links | six audit queries empty | measured |
| RQ5 | Comparative superiority over unaided manual practice | `SNR`, incorrect-gate rate, `DC` | **DEFERRED — no panel, no participants, no data** |

**Success criteria, fixed before execution.** `DC = 1.000`, `OPR = 0.000` and
`CV = 1.000` are required and `Φ` refuses to emit a bundle otherwise.
`TD = 1.000` over 62 runs is the RQ2 criterion. **`GD(T_H)`, `GD_min` and the
Monte Carlo flip probabilities have no predicted value**; whatever they measure is
what is reported, and no script reads a manuscript figure.

## Determinism matrix (frozen)

**31 executions per case, 62 total**, from matrix seed `20260101` so the matrix is
byte-identical on every execution and every platform.

| Stratum | Runs | What varies |
|---|---|---|
| `repeat` | 10 | clean repeat executions, identical inputs |
| `row_shuffle` | 10 | every semantically unordered array permuted, cycled so all are covered |
| `key_shuffle` | 5 | object-key order reversed / shuffled / rotated over every object in every input |
| `locale` | 3 | `LC_ALL` ∈ {en_US, de_DE, tr_TR}.UTF-8, permutation held fixed |
| `timezone` | 3 | `TZ` ∈ {America/Edmonton, Asia/Kolkata, Pacific/Chatham}, permutation held fixed |

Equivalent permitted serialization (integers re-encoded as equal-valued floats)
has no stratum of its own in the examiner's arithmetic, so it is layered onto a
documented subset — 5 runs per case — and recorded in its own CSV column. 15 of
the 31 run in a freshly spawned interpreter under a varying `PYTHONHASHSEED`.

Success criterion: every run reproduces its case's committed reference canonical
payload hash. **Signature-envelope bytes are not required to match** (Section VI-C).

## Thresholds, seeds and definitions (frozen)

| Item | Value |
|---|---|
| Declared heat-map threshold `T_H` (both cases) | **15** |
| `𝒯` for `GD_min` | distinct observed scores plus the boundary value above and below each |
| GD summation scope | **all register rows**, non-runtime included |
| `C*` base profile | the four manuscript kinds, materiality-qualified at `material` |
| Reason codes | RC-01, RC-02, RC-03, RC-05 (RC-04 reserved-unused) |
| Schema version | **v1.0** |
| Monte Carlo seed | **20260201**, `K = 250,000`, no adaptive stopping |
| Determinism matrix seed | **20260101** |
| Research key derivation seed | the `KEY_SEED` string in `tools/build_cases.py` |
| RQ5 participant randomization | **not drawn** — Tier-1, at recruitment close |

## Monte Carlo specification (frozen) — attribution corrected

Symmetric ±1 ordinal perturbation with clamping: 0.6 on the approved rating, 0.2
on each adjacent rating of the 1–5 scale, out-of-range mass reassigned to the
approved rating. `MCSE(p̂) = √(p̂(1−p̂)/K)`, bounded above by 0.001 at this `K`.
No exclusions of any kind.

> **DECLARED DEVIATION.** Manuscript Section XI-G attributes these distributions
> to the independent adjudication panel of Section XI-C, and the artifact-runs
> memo treats panel sign-off as a prerequisite. **No panel has been convened.**
> These are author-specified synthetic sensitivity distributions, chosen a priori
> and frozen before any result was computed. They must never be described as
> independently adjudicated. The memo's own "0.6/0.2/0.2 model" is exactly this
> rule — independent corroboration that the a-priori choice was the natural one,
> not evidence of panel involvement. See `docs/FIXTURE_PROVENANCE.md` FP-020.

## Exclusion and missing-data rules (frozen)

**Tier-0 measurements: no exclusions.** Every register row, compiled predicate,
determinism run, injection scenario and Monte Carlo draw is included. A failed
determinism run is reported as a failure, never dropped. An adversarial case
rejected with the wrong error code is `CODE_MISMATCH`, never a silent pass.

## Held-out register hash — STILL OPENLY OUTSTANDING

No held-out register has been authored, so no hash is committed.
`preregistration/HELD_OUT_REGISTER.md` records the gap rather than committing a
hash of a placeholder. To be discharged in a Tier-1 freeze before RQ5 recruitment.

## Amendment procedure

If a defect is found in frozen code **after** the v2 campaign has run:

1. **STOP.** Do not patch v2 in place.
2. Document the defect and its effect on every reported number.
3. Increment to `tier0-v3`, regenerate the manifest, push a new public tag.
4. Re-run the campaign from scratch against v3.
5. Record the amendment in `CHANGELOG.md` and the reconciliation table.

**A frozen number is never edited in place.**

---

## Supersession: `preregister-tier0-v2` → `preregister-tier0-v2.1`

**This is the amendment procedure above, executed.**

`preregister-tier0-v2` was created, committed and **pushed publicly** at
2026-09-08T17:52:54Z, pointing at commit `33a610c850b2847b88d3667e0706a457a3e37307`.
It remains on the public repository and is not deleted or moved.

**Before any campaign ran against it**, a defect was found in a frozen file:

> `experiments/verify_freeze.py` compared the remote tag's **tag-object** SHA
> against the freeze **commit** SHA. For an annotated tag those are different
> objects, so the remote-verification check could never pass — it would have
> reported the public commitment as undischarged even when it was correctly
> discharged. `git ls-remote --tags <name>` with an exact tag name returns only
> the tag object; the dereferenced `refs/tags/<tag>^{}` line must be requested
> explicitly.

Two further defects were found in the same window by a full dry run:
`experiments/run_properties.py` used `phase_of` without importing it, and the
results-directory default did not follow the freeze tag.

Per the amendment procedure, these were **not patched in place under the v2 tag**.
The freeze was incremented:

| | |
|---|---|
| Superseded tag | `preregister-tier0-v2` (public, retained, no campaign ran against it) |
| Governing tag | **`preregister-tier0-v2.1`** |
| Reason | defect in frozen verification tooling, found before execution |
| Campaign | `results/final_v2/` — the second reportable campaign, governed by v2.1 |

Everything else in this document — the hypotheses, the 31-per-case determinism
matrix, the thresholds, the seeds, the Monte Carlo specification and its declared
attribution deviation, the exclusion rules — is unchanged between v2 and v2.1.
`FREEZE_MANIFEST_V2.sha256` is regenerated over the corrected state and covers
the two analysis scripts added with it (`make_provenance.py`,
`compare_campaigns.py`).

**The naming.** The results directory is `results/final_v2` because it is the
*second campaign*; the freeze governing it is `v2.1` because it is the *corrected
second freeze*. `results/final_v2/PROVENANCE.json` records both explicitly so the
pairing is never ambiguous.
