# ZENODO_RELEASE_STEPS.md

**No Zenodo deposit has been made and no DOI exists for this artifact.**

This file records the exact remaining manual steps instead of inventing an
identifier. A fabricated or placeholder DOI in a manuscript is worse than an
acknowledged gap: it is uncheckable and it will eventually resolve to nothing.

---

## Why this is manual

Zenodo's GitHub integration requires an authenticated Zenodo account linked to the
GitHub account that owns the repository, and the link must be enabled **before** the
release is published. Neither the account link nor the Zenodo credential is
available to the process that built this artifact.

---

## Steps

1. **Link the account.** Sign in at <https://zenodo.org> with the GitHub account
   that owns `AGLakhowal/gc-ir-reference`. Go to **Settings → GitHub** and toggle
   the repository **on**. The toggle must be on before the release is published;
   Zenodo does not retroactively archive earlier releases.

2. **Publish the release.** If `v1.0.0` was already published before the toggle was
   enabled, publish a new patch release (`v1.0.1`) so Zenodo has a release event to
   archive. Zenodo then creates a deposition automatically within a few minutes.

3. **Complete the deposition metadata.** Zenodo pre-fills from `CITATION.cff`, but
   confirm:
   * **Title:** GC-IR Reference Implementation — reproducibility artifact for
     "From Risk Register to Runtime Predicate"
   * **Authors / ORCID:** Abhinandan Gill-Lakhowal, 0009-0004-2089-7262
   * **Type:** Software
   * **Licence:** MIT
   * **Related identifiers:** `isSupplementTo` the paper's DOI once IEEE assigns
     it; `isDerivedFrom` / `references` the cited prior work
   * **Keywords:** as in `CITATION.cff`

4. **Record the DOI.** Zenodo mints two: a **concept DOI** that always resolves to
   the latest version, and a **version DOI** for this release. Cite the **concept
   DOI** in the paper unless a specific version is meant.

   Then, in this repository:
   * add the DOI badge to `README.md`;
   * add `doi:` and `identifiers:` to `CITATION.cff`;
   * record both DOIs in `CHANGELOG.md` under the release;
   * update `paper_update/PLACEHOLDER_REPLACEMENT_TABLE.md`, which currently marks
     the Appendix C repository identifier as outstanding.

5. **Update the manuscript.** Appendix C currently reads
   `[TO CONFIRM: final repository path at release]`. Replace it with the resolved
   repository URL, the release tag, the `MANIFEST.sha256` hash, and the concept DOI.
   `paper_update/MEASURED_RESULTS.md` gives the wording.

---

## Until all of that is done

The manuscript must say what is true: that the artifact is released as a
hash-pinned tagged release at a named repository path, and that archival deposit is
pending. **It must not cite a DOI.**

The release tag and the `MANIFEST.sha256` hash together already constitute the
public preregistration commitment Section XI-I requires — that commitment does not
depend on Zenodo. The DOI adds archival permanence, not the commitment itself.
