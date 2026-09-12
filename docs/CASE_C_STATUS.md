# Case C Status: Compiled, for the First Time, This Generation

**Status:** development artifact (schema v1.1). Not part of the frozen
`preregister-tier0-v3.1` campaign. `results/final_v3_1/` is untouched.

## What changed

Prior generations of this repository deliberately treated Case C as a
design/theoretical case and did **not** compile it —
`docs/MANUSCRIPT_5_5D_DELTA.md` §6 states plainly: *"Case C not compiled as
part of the artifact campaign"*, *"Do NOT invent or compile a Case C artifact
merely because 5.5d contains a design Case C."* `docs/RELEASE_NOTES_v1.0.0.md`
and `docs/ARTIFACT_RUNS_COMPLIANCE.md` record the same decision.

This generation revisits that decision because the brief explicitly requested
building Case C for real, and because schema v1.1 (this generation) now has
the mechanisms — state binding, concurrence, delegation containment,
actor-scope revocation, safety-event correlation, human response — that Case
C's design actually exercises. `cases/case_c/` is a genuinely compiled bundle:

```
Risks:                   16  (matches manuscript Tables V-VI exactly)
Runtime dispositions:    13  (C-01..C-05, C-08..C-15)
Non-runtime dispositions: 3  (C-06, C-07: RC-06 -> runtime_safety;
                               C-16: RC-03 -> human_process)
Approved Control Specs:  13  (one per runtime risk)
Compiled predicates:     16  (13 risk-derived + 3 compiler-invariant)
C*_cp-classified risks:   9  (7 runtime: C-01,02,03,04,05,09,12;
                               2 non-runtime, RC-06-exempted: C-06, C-07)
Schema version:         1.1
Payload hash: d7c7971156e3591b64567148ed8fc21cc1cbee21973d3646f59e439c74bf1dbd
(updated this session after the schema $id host change; the case's risk/ACS/
predicate structure and C* classification above are unaffected)
```

Canonical Q1-Q10: 10/10 PASS (see `tests/integration/test_case_c.py`).

## What did NOT change

- **The prior decision not to compile Case C for the frozen v3.1 campaign was
  correct at the time it was made** — v1.0's compiler and schema genuinely
  could not express several of Case C's mechanisms (state binding,
  concurrence, delegation, revocation, safety-event correlation). Compiling
  it then would have required either omitting those mechanisms (misrepresenting
  the design) or inventing ad-hoc fields with no schema behind them
  (exactly what this project's other audits have flagged as the failure mode
  to avoid). This generation's schema v1.1 removes that obstacle; the earlier
  decision is superseded, not shown to have been wrong.
- `results/final_v3_1/`, `preregister-tier0-v3.1`, and the historical Case A/B
  are untouched.
- No claim of clinical efficacy, certified surgical safety, hardware
  validation, or real deployment is made anywhere in this artifact. Case C
  remains synthetic and standards-anchored (ISO 14971, IEC 62304, IEC
  80601-2-77); no vendor's internal risk register, software, or telemetry is
  described, inferred, or claimed.

## Scope reductions relative to the manuscript's Tables V-VI (stated plainly)

1. **Predicate granularity.** Every compiled ACS here carries one context
   condition, the same granularity Case A and Case B already use. The
   manuscript's prose sketches some Case C predicates as multi-conjunct
   checks (e.g. C-03's seven-part supervisory-authority test). The
   *disposition*, *consequence classification*, *gate source*, and *v1.1
   mechanism* assigned to every one of the sixteen rows match the manuscript
   exactly; the internal structure of the compiled condition is schematic.
2. **C\* membership is now genuinely reversibility-qualified (fixed; no
   longer a materiality workaround).** `gcir.coverage.CStarProfile.evaluate()`
   reads an optional `required_reversibility` list on a classification rule
   (schema v1.1, `schemas/cstar_profile.schema.json`); Case C's
   `physical_harm_to_person` rule declares `["irreversible",
   "requires_intervention"]`, matching Section VII-A exactly. C-08 and C-10
   (genuinely reversible guidance/model rows) are excluded from C* by that
   real check, verified directly by
   `tests/unit/test_v1_1.py::test_case_c_reversible_guidance_rows_are_excluded_from_c_star_by_reversibility`
   and by unit tests proving materiality alone cannot substitute for it
   (`test_reversible_physical_harm_is_excluded_despite_material_materiality`).
   C-13 and C-16 use a distinct, non-member consequence kind
   (`clinical_oversight_defect`) rather than `physical_harm_to_person`,
   because their own reversibility value (`requires_intervention`) would
   otherwise *correctly* qualify them for C* under the real rule — and the
   manuscript's stated disposition for both is "mandatory (other)" / RC-03,
   not C*. That is a modeling choice (these are provenance/oversight defects,
   not direct physical-harm mechanisms), not a workaround of the coverage
   rule. Case A and Case B's profiles declare no `required_reversibility` on
   any rule and are verified unaffected by this mechanism
   (`test_case_a_and_case_b_cstar_profiles_declare_no_reversibility_qualifier`).
3. **RC-06 / AD-1 carve-out is new, minimal code.** `gcir.coverage.verify_cv`
   previously raised `CoverageError` for any C*-classified risk with no
   hazardous action path — meaning C-06 and C-07 (correctly C*-eligible by
   severity, correctly *ungated* because a control-loop-rate hazard cannot be
   an authorization-boundary gate) could not have compiled under the prior
   `verify_cv`. This generation adds an opt-in `rc06_risk_ids` parameter
   (default: no exemptions, so v1.0 behavior for Case A/B is unchanged) that
   exempts exactly the risks disposed non-runtime with reason code RC-06. See
   `gcir.coverage.verify_cv`'s docstring.
4. **Injection scenarios (E1-E19).** The manuscript names a 19-scenario
   failure-injection matrix for Case C. `experiments/case_c_injection_scenarios.py`
   (this generation) implements 12 scenarios exercising every v1.1 mechanism
   Case C's register uses (state-binding mismatch, concurrence pending/expiry,
   evaluation timeout, actor-scope revocation via auxiliary A1, delegation
   containment via auxiliary A3, safety-event correlation via auxiliary A2,
   human-response coverage via auxiliary A4, and known-fail/DENY cases on the
   deterministic-lookup and structural-check rows). It does **not** claim to
   be the full 19-scenario matrix the manuscript describes; the remaining
   scenarios (chiefly ones needing genuine multi-step runtime state — e.g. a
   live ROS 2 simulator — rather than a single evaluation call) are out of
   scope for this generation and are listed as NOT IMPLEMENTED in the final
   report, not silently omitted.

## Not implementable by software alone

- Trajectory or motion safety, or any substitution for a certified runtime
  safety layer.
- Clinical efficacy or fitness of any surgical system.
- The conformance harness described in the manuscript's Appendix D
  (synthetic simulator, dynamic surgical simulation, research hardware) —
  this requires physical or simulated infrastructure this repository does not
  contain, and is explicitly named future work in the manuscript itself.

## Verification

```
python -m tools.build_case_c
python -m pytest tests/integration/test_case_c.py -q
python -m experiments.case_c_injection_scenarios   # (if wired as a runnable script)
```
