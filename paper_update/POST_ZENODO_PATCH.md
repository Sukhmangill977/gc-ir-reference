# Post-Zenodo patch — the exact substitutions to make once a real DOI exists

**No DOI exists yet, and none appears anywhere in the manuscript.** There is no
`DOI: XXXXX`, no reserved identifier, no placeholder. The submission manuscript is
complete and submittable exactly as it stands; this file is only needed if and
when a DOI is minted.

Read `artifact_review/ARCHIVAL_CHECKLIST.md` first for the deposition steps.

---

## Prerequisite

Do not apply any substitution below until the DOI **resolves in a browser**.
Zenodo lets you *reserve* a DOI before publishing; a reserved DOI is not
resolvable, and an unresolvable DOI in a submitted manuscript is worse than none.

Throughout, `⟨DOI⟩` means the bare identifier in the form
`10.5281/zenodo.NNNNNNNN`.

---

## Substitution 1 — Data and Code Availability *(required)*

**Find** the final sentence of the Data and Code Availability section, currently:

> An archival deposit with a persistent identifier is pending and is not cited
> here; the repository release tag and its hash manifest are the citable artifact
> until one exists.

**Replace with:**

> The artifact is archived at doi: ⟨DOI⟩, which resolves to the `v1.0.2` release
> and its hash manifest.

This is the only substitution that is strictly required. If you make no other
change, the manuscript is correct.

## Substitution 2 — Appendix C, artifact release *(optional)*

**Find:**

> The artifact is released at https://github.com/Sukhmangill977/gc-ir-reference,
> release tag v1.0.2.

**Replace with:**

> The artifact is released at https://github.com/Sukhmangill977/gc-ir-reference,
> release tag v1.0.2, and archived at doi: ⟨DOI⟩.

Apply only if the venue wants the identifier in the artifact appendix as well as
in availability. One DOI in two places is fine; two *different* DOIs is not.

## Substitution 3 — Section XI-I preregistration *(conditional — usually skip)*

Apply **only** if you deposit the preregistration freeze **separately**, giving it
its own distinct DOI.

**Find:**

> the Tier-0 freeze is published at https://github.com/Sukhmangill977/gc-ir-reference
> under tag preregister-tier0-v2.2

**Append:**

> , and archived at doi: ⟨preregistration DOI⟩

If a single deposit covers both the release and the freeze — the normal case —
**skip this entirely.** Citing one DOI in two roles invites the reader to think
two deposits exist.

---

## Separate and unrelated: reference [15]

Reference [15] is the L-DREA paper, in IEEE Access early access. Its final DOI
could not be verified from a reachable primary source and **was not invented**. It
currently reads:

> IEEE Access, 2026, early access, art. no. 11641546.

Once IEEE Xplore assigns the DOI, append `, doi: ⟨DOI⟩.` This is a bibliographic
completion, entirely independent of the Zenodo deposit above.

## Separate and unrelated: reference [22]

The arXiv `Comments:` field asserts acceptance at the STPSA Workshop, IEEE COMPSAC
2026. **No indexed proceedings record, `journal_ref` or publication DOI exists**
(arXiv API and dblp both checked), so it is cited as a preprint. If the
proceedings are now indexed, upgrade the citation — verify against IEEE Xplore or
dblp first, not the arXiv comments field. See
`paper_update/REFERENCES_21_22_VERIFICATION.md`.

---

## How to apply them

The manuscript is generated, not hand-edited. Preferred route:

1. Edit `tools/build_submission_docx.py` — add the substitutions to the `EDITS`
   list, each with its evidence line, exactly as every other edit carries one.
2. Rebuild:

   ```bash
   python -m tools.build_submission_docx \
     --source "<path>/From_Risk_Register_to_Runtime_Predicate_FINAL.docx"
   ```

   The source manuscript is never written to; the builder refuses to overwrite it.
3. Confirm the run reports **`draft markers remaining in output: 0`** and that the
   applied-edit count rose by exactly the number you added.
4. Check that no `⟨` or `⟩` survives in the output.
5. Regenerate the manifest and commit:

   ```bash
   make manifest
   git add -A && git commit
   ```

Editing the `.docx` by hand also works, but then
`paper_update/FINAL_MANUSCRIPT_CHANGELOG.md` no longer describes how the file was
produced, and the build stops being reproducible.

---

## Rules

1. **Never insert a DOI that does not resolve.**
2. **Change no number, claim, or hash** while doing this. The scientific content
   is frozen; this is a bibliographic edit only.
3. **Do not re-run any experiment.** Nothing here touches `results/final_v2/`.
4. **The deposit must be the `v1.0.2` release**, not a later state of `main`. If
   the repository has moved on, mint the DOI from the tag.
5. **If no DOI ever materialises, submit as is.** The repository release plus its
   hash manifest is a complete availability statement, and nothing in the paper
   depends on a DOI existing.
