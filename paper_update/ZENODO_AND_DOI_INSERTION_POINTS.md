# ZENODO_AND_DOI_INSERTION_POINTS.md

**No DOI has been minted for this artifact, and none is cited in the manuscript.**
This file records exactly where a persistent identifier goes once one exists, so that
insertion is a mechanical edit rather than a judgment call — and so that no placeholder
DOI ever sits in the submitted document.

This file is deliberately **outside** the manuscript.

---

## Status

| | |
|---|---|
| Archival deposit | **Not created.** |
| DOI | **Does not exist.** |
| Citable artifact today | `https://github.com/Sukhmangill977/gc-ir-reference`, release tag `v1.0.0` |
| Preregistration freeze | tag `preregister-tier0-v2.2` at commit `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e` |

The manuscript currently states, in Data and Code Availability:

> *An archival deposit with a persistent identifier is pending and is not cited here;
> the repository release tag and its hash manifest are the citable artifact until one
> exists.*

That sentence is accurate as written and requires no action unless a DOI is minted.

---

## Insertion point 1 — Data and Code Availability (primary)

**Locate:** the final sentence of the Data and Code Availability section, quoted above.

**Replace with:**

> The artifact is archived at DOI ⟨DOI⟩, which resolves to the `v1.0.0` release and its
> hash manifest.

**Do not** add a DOI anywhere else in that section; one archival identifier is enough.

## Insertion point 2 — Appendix C, artifact release

**Locate:** *"The artifact is released at https://github.com/Sukhmangill977/gc-ir-reference,
release tag v1.0.0."*

**Append:** *"and archived under DOI ⟨DOI⟩."*

Optional. Only do this if the venue requires the identifier to appear in the artifact
appendix as well as in availability.

## Insertion point 3 — §XI-I preregistration (conditional)

Only if the **preregistration freeze itself** is deposited separately from the release,
which would give it its own DOI.

**Locate:** *"the Tier-0 freeze is published at … under tag `preregister-tier0-v2.2`"*

**Append:** *"and archived under DOI ⟨preregistration DOI⟩"*

If a single deposit covers both the release and the freeze — the normal case — **skip
this point entirely**. Citing one DOI in two roles invites the reader to think two
deposits exist.

---

## Reference [15] — a separate, unrelated pending identifier

Reference [15] is the L-DREA paper, in IEEE Access early access. Its final DOI could not
be verified against a reachable primary source and **was not invented**. The reference
currently reads:

> IEEE Access, 2026, early access, art. no. 11641546.

**Once the DOI is assigned by IEEE Xplore,** append `, doi: ⟨DOI⟩.` This is a
bibliographic completion, not an artifact deposit, and is independent of everything
above.

---

## Rules for whoever performs the insertion

1. **Do not insert a DOI that has not been minted.** A reserved-but-unpublished Zenodo
   identifier is not yet resolvable; wait until it resolves.
2. **The deposit must be the `v1.0.0` release,** not a later state of the repository.
   If the repository has moved on, mint the DOI from the tag, not from `HEAD`.
3. **Do not change any number, claim or hash** while inserting the DOI. The scientific
   content is frozen; this is a bibliographic edit only.
4. **Re-run the marker scan afterwards** — `python -m tools.build_submission_docx` will
   report zero draft markers — and confirm the ⟨DOI⟩ angle brackets are gone.
5. If the DOI never materialises, **the manuscript is submittable as it stands.** The
   repository release plus hash manifest is a complete availability statement, and
   nothing in the paper depends on a DOI existing.
