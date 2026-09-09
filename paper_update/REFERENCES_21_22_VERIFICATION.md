# References [21] and [22] — primary-source verification

Both were previously flagged as unverifiable because their arXiv pages could not
be reached. **Both are now verified against their primary sources.**

Verified 2026-09-09. Sources used, in order of authority:

1. `http://export.arxiv.org/api/query?id_list=…` — the arXiv API, authoritative
   for structured metadata (`journal_ref`, `doi`, dates, author list)
2. `https://arxiv.org/abs/<id>v1` — the abstract page, for the `Comments:` field
3. `https://dblp.org/search/publ/api` — for any indexed publication record

---

## [21] — VERIFIED, one correction applied

| Field | Verified value | Manuscript before | Status |
|---|---|---|---|
| Title | *Making AI Compliance Evidence Machine-Readable* | identical | ✅ |
| Authors | Rodrigo Cilla Ugarte; Miguel Ángel Patricio Guisado; Antonio Berlanga de Jesús; José Manuel Molina López | R. Cilla Ugarte, M. Á. Patricio Guisado, A. Berlanga de Jesús, and J. M. Molina López | ✅ exact, order preserved |
| arXiv ID | `2604.13767` (v1) | `arXiv:2604.13767` | ✅ |
| Submitted | 2026-04-15T11:51:54Z | year only: "2026" | ⚠️ **corrected → "Apr. 2026"** |
| Primary category | cs.CY | — | ✅ |
| `journal_ref` | **absent** | not cited | ✅ correctly absent |
| Registered DOI | **absent** (API reports no DOI) | not cited | ✅ correctly absent |
| `Comments:` | "9 pages, 2 figures, 3 tables. **Submitted to** IEEE Computer, Special Issue on AI Governance and Compliance" | — | ⚠️ see note |

**Note on the venue.** The comments field says *submitted to* IEEE Computer —
submitted, not accepted, not published. It is therefore cited as an arXiv
preprint. **No venue was added**, because doing so would assert a publication
that does not exist.

**Correction applied:** month added, matching the style already used for [23]
(`arXiv:2603.20953, Mar. 2026`).

> `[21] R. Cilla Ugarte, M. Á. Patricio Guisado, A. Berlanga de Jesús, and J. M. Molina López, "Making AI Compliance Evidence Machine-Readable," arXiv:2604.13767, Apr. 2026.`

### Dependent manuscript claim

§II-F: *"OSCAL-based approaches structure AI-assurance evidence and connect
policy, assessment, and enforcement records [21]."*

**Supported.** The abstract proposes OSCAL as an interchange format for AI
governance, defines "a three-layer Compliance-as-Code architecture (policy,
evidence, enforcement)", and states that the SDK "produces native OSCAL
**Assessment Results** validated against the NIST JSON schema".

The paper's own three layers are *policy, evidence, enforcement*; the manuscript
says *policy, assessment, and enforcement*. Both are accurate descriptions —
the artifact it emits is literally an OSCAL Assessment Result — so **no change
was made to the body text**. Recorded here so the difference is visible rather
than silent.

The claim is used only to establish that adjacent machine-readable-compliance
work exists, which supports the manuscript's *narrowing* of its own novelty. It
carries no empirical weight.

---

## [22] — VERIFIED, one correction applied, one item flagged

| Field | Verified value | Manuscript before | Status |
|---|---|---|---|
| Title | *Ontological Knowledge Blocks: Executable Compliance and Profile-Based Validation for Trustworthy AI Systems* | identical | ✅ |
| Authors | Aasish Kumar Sharma; Julian M. Kunkel | A. K. Sharma and J. M. Kunkel | ✅ exact |
| arXiv ID | `2605.23297` (v1) | `arXiv:2605.23297` | ✅ |
| Submitted | 2026-05-22T07:14:31Z | year only: "2026" | ⚠️ **corrected → "May 2026"** |
| Primary category | cs.AI (also cs.DC) | — | ✅ |
| `journal_ref` | **absent** (arXiv API: not present) | not cited | ✅ correctly absent |
| Registered DOI | **absent** (arXiv API: not present) | not cited | ✅ correctly absent |
| `Comments:` | "6 pages, 3 figures. **Accepted at** the Security, Trust and Privacy for Software and Applications (STPSA) Workshop, IEEE COMPSAC 2026, Madrid, Spain, July 7-10, 2026" | — | 🚩 **FLAGGED — see below** |

**Correction applied:** month added.

> `[22] A. K. Sharma and J. M. Kunkel, "Ontological Knowledge Blocks: Executable Compliance and Profile-Based Validation for Trustworthy AI Systems," arXiv:2605.23297, May 2026.`

### 🚩 FLAGGED — a possible venue upgrade that could NOT be verified

The author-supplied `Comments:` field asserts acceptance at the **STPSA
Workshop, IEEE COMPSAC 2026** (Madrid, 7–10 July 2026), and a COMPSAC 2026
program page appears in search results. **No published record exists that I could
verify:**

* arXiv's `journal_ref` field is **absent** — it is the author's Comments field
  that carries the acceptance text, not a registered publication reference;
* arXiv reports **no DOI**;
* **dblp returns no hits** for the title or authors;
* IEEE Xplore was **not readable**.

An acceptance stated in a free-text comments field is an author's assertion, not
a publication record. Adding proceedings details — pages, DOI, "in *Proc. IEEE
COMPSAC*" — would mean inventing bibliographic data, so **it was not done**.

**Action for the author (optional, not blocking).** COMPSAC 2026 took place in
July 2026. If the proceedings are now indexed, the citation can be upgraded to
the published version. Verify against IEEE Xplore or dblp first; do not rely on
the arXiv comments field alone.

### Dependent manuscript claim

§II-F: *"Ontological Knowledge Blocks compile structured regulatory records into
executable SHACL constraints over provenance-linked evidence graphs [22]."*

**Fully supported**, element by element, against the abstract:

| Manuscript element | Abstract |
|---|---|
| "structured regulatory records" | "converts regulatory requirements into machine-verifiable constraints" |
| "executable SHACL constraints" | "SHACL validation rules" |
| "provenance-linked" | "PROV-O provenance tracking" |
| "evidence graphs" | "structured evidence graphs" |

Like [21], it is cited only to establish adjacent prior art and carries no
empirical weight.

---

## Summary

| | [21] | [22] |
|---|---|---|
| Primary source reachable | ✅ | ✅ |
| Title exact | ✅ | ✅ |
| Author list exact and complete | ✅ | ✅ |
| arXiv identifier correct | ✅ | ✅ |
| Date | corrected to **Apr. 2026** | corrected to **May 2026** |
| DOI | none assigned — **none cited** | none assigned — **none cited** |
| Venue | "submitted to" only — **none cited** | acceptance asserted in comments, no indexed record — **none cited, flagged** |
| Dependent claim supported | ✅ | ✅ |

**Two corrections applied, both dates. No bibliographic data was inferred or
invented.** Neither reference carries any empirical weight: both appear once, in
§II-F, in the passage where the paper *narrows* its own novelty claim by
acknowledging adjacent work. Nothing in the results depends on either.
