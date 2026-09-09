# Archival checklist — Zenodo deposition

IEEE Access Reproducibility review expects a persistently versioned artifact.
This records what is ready, what was fixed, and the exact manual steps that
remain.

**No DOI has been minted, and none is asserted anywhere in the repository or the
manuscript.**

---

## Metadata audit

| Item | Status | Notes |
|---|---|---|
| `LICENSE` | ✅ | MIT, © 2026 Abhinandan Gill-Lakhowal. Matches the precedent named in the article's Appendix C. |
| `CITATION.cff` — parses | ✅ | Valid CFF 1.2.0; all required keys present. |
| `CITATION.cff` — author | ✅ | Abhinandan Gill-Lakhowal, ORCID `0009-0004-2089-7262`, Gillian Holdings Incorporated. |
| `CITATION.cff` — `repository-code` | ✅ **FIXED** | Was `https://github.com/AGLakhowal/gc-ir-reference`, **which does not exist** (verified: GitHub returns "Could not resolve to a Repository"). Corrected to `https://github.com/Sukhmangill977/gc-ir-reference`. `AGLakhowal` is the organisation holding the *prior work* `Gamma-Permit-Package`, not this artifact. |
| `CITATION.cff` — `version` | ✅ | `1.0.1`, matching the release below. |
| `CITATION.cff` — `date-released`, `commit` | ✅ **ADDED** | Pins the citation to a specific commit. |
| `CITATION.cff` — paper DOI | ✅ | Recorded as "to be added once assigned"; **no DOI asserted**. |
| `.zenodo.json` | ✅ **ADDED** | Explicit deposition metadata so Zenodo does not have to infer title, license, ORCID or description from the repository. Carries the claim boundary in the description. |
| Repository visibility | ✅ | Public. |
| Release `v1.0.0` | ✅ | Published 2026-09-08. **Not rewritten.** |
| Release `v1.0.1` | ✅ | Packaging/documentation release; see `IEEE_REPRODUCIBILITY_SELF_REVIEW.md`. |
| Freeze tag `preregister-tier0-v2.2` | ✅ | Public, at `c44f25d6fdb67e0bc4ac73a6217125dec8da1c0e`. **Not moved.** |
| `MANIFEST.sha256` | ✅ | Current; verified by `make verify-manifest` and by CI. |
| `FREEZE_MANIFEST_V2.sha256` | ✅ | Untouched — it proves the frozen experiment and must never be regenerated. |
| Secrets | ✅ | `keys/` holds Ed25519 **research fixtures** marked TEST ONLY / NOT FOR PRODUCTION, committed so signatures reproduce byte-identically. No production key is present. |

---

## What gets archived

The Zenodo deposit should be **the `v1.0.1` release tarball**, not a snapshot of
`main` at some later time. The release tag, its `MANIFEST.sha256` and the
preregistration freeze tag are what make the deposit self-verifying.

Approximate size: the repository is ~312 files. The largest single item is the
submission manuscript under `paper_update/` (~2.2 MB).

---

## Manual steps — these require a browser and cannot be automated from here

Zenodo deposition needs an authenticated browser session and an explicit consent
click. **Stop here and perform these by hand:**

1. **Sign in to Zenodo** at <https://zenodo.org> using the GitHub account that
   owns `Sukhmangill977/gc-ir-reference`.

2. **Enable the repository for archiving.** Go to
   <https://zenodo.org/account/settings/github/>, find
   `Sukhmangill977/gc-ir-reference` in the list, and switch the toggle **ON**.
   *(If it does not appear, click "Sync now" — Zenodo only lists repositories the
   authorised GitHub App can see.)*

3. **Create the release that Zenodo will capture.** Zenodo archives *new*
   releases created after the toggle is on; it does **not** retroactively archive
   `v1.0.0` or `v1.0.1` if they already existed. So either:

   * **(a)** enable the toggle first and then publish the next release, or
   * **(b)** archive manually: on Zenodo choose *New upload*, attach the release
     tarball from
     `https://github.com/Sukhmangill977/gc-ir-reference/archive/refs/tags/v1.0.1.tar.gz`,
     and let `.zenodo.json` populate the metadata.

   **(b) is what applies here**, because `v1.0.1` is created before the toggle.

4. **Check the metadata Zenodo picked up** against `.zenodo.json`: title, MIT
   license, ORCID, version `1.0.1`, and the description including the claim
   boundary. Correct anything Zenodo guessed differently.

5. **Publish.** This mints the DOI. It is irreversible: a published Zenodo record
   cannot be deleted, only a new version added.

6. **Record the DOI** — do **not** type it into the manuscript directly. Follow
   `../paper_update/ZENODO_AND_DOI_INSERTION_POINTS.md`, which names the three
   insertion points and the rules. Then:
   * add the DOI badge to `README.md`;
   * add an `identifiers:` block with the DOI to `CITATION.cff`;
   * regenerate `MANIFEST.sha256` (`make manifest`) and commit.

7. **Do not** insert a reserved-but-unpublished DOI. Zenodo lets you reserve one
   before publishing; it is not resolvable until you publish, and an unresolvable
   DOI in a submitted manuscript is worse than none.

---

## Blocking issues

**None.** The repository is ready to deposit. Everything above that could be done
without a browser has been done.

## Explicitly not done

* No DOI was invented, reserved or written anywhere.
* `v1.0.0` was not rewritten.
* `preregister-tier0-v2.2` was not moved.
* No scientific result was touched.
