# LITERATURE_VERIFICATION.md

The final literature sweep the manuscript requests at Section II-F
(`[VERIFY: final literature sweep at submission — compliance-by-design,
regulatory technology, agent-governance toolkits, 2024–2026]`), plus verification
of every citation-dependent statement and every reference.

**Method.** Primary sources where reachable (arXiv abstract pages, CNCF, IETF,
NIST). Where a publisher blocked automated retrieval (ACM Digital Library and
dblp returned 403; IEEE Xplore returned no content), that is recorded as
*unverified* rather than assumed correct. **No bibliographic data was invented.**

**Date of sweep:** September 2026.

---

## Part 1 — Citation-dependent claims

| # | Manuscript location | Claim | Source | Verified / modified | Reason |
|---|---|---|---|---|---|
| L1 | II-F | "Natural-language access-control research extracts authorization policies from requirements or user stories, but its target is normally an access-control rule and its principal validity question is extraction accuracy [18], [19]." | [18] Jayasundara et al., *ACM Comput. Surv.* 57(4), 2025, doi 10.1145/3706057 (arXiv:2310.03292); [19] Narouei et al., *IEEE TDSC* 17(3), 2020 | **Verified** | Both exist and the characterisation is accurate. [18] is an SLR of 49 publications on access-control policy generation; its validity question is indeed generation/extraction quality. |
| L2 | II-F | "Policy Cards express operational and regulatory constraints in a versioned machine-readable artifact suitable for runtime use [20]." | [20] J. Mavračić, arXiv:2510.24383, submitted 28 Oct 2025 | **Verified** | Abstract confirms a machine-readable, deployment-layer, version-controlled artifact encoding allow/deny rules, obligations and evidentiary requirements, with crosswalks to NIST AI RMF, ISO/IEC 42001 and the EU AI Act. Characterisation is accurate and not overstated. |
| L3 | II-F | "OSCAL-based approaches structure AI-assurance evidence and connect policy, assessment, and enforcement records [21]." | [21] arXiv:2604.13767 | **UNVERIFIED — flagged** | The arXiv abstract page could not be retrieved during the sweep. Identifier format is well-formed (April 2026). The author must confirm the identifier, author list and title before submission. |
| L4 | II-F | "Ontological Knowledge Blocks compile structured regulatory records into executable SHACL constraints over provenance-linked evidence graphs [22]." | [22] arXiv:2605.23297 | **UNVERIFIED — flagged** | Not retrievable during the sweep. Same action required. |
| L5 | II-F | "Recent pre-action authorization work specifies deterministic tool-call gating for autonomous agents at the enforcement layer [23], leaving the derivation of its policy artifacts from enterprise assessments — the question addressed here — open." | [23] U. Uchibeke, arXiv:2603.20953, Mar 2026 | **Verified (exists)** | The identifier resolves to "Before the Tool Call: Deterministic Pre-Action Authorization for Autonomous AI Agents". The characterisation — enforcement-layer gating, derivation left open — is consistent with the title and scope. |
| L6 | **II-F (NEW)** | The five-property combination is "not found together in the reviewed approaches". | See Part 2 | **MODIFIED — citation added** | The sweep found a directly adjacent 2026 paper the manuscript did not cite (Koch, arXiv:2604.05229). The claim survives, but leaving the paper uncited would have been a genuine related-work gap. Section II-F now cites and positions against it. |
| L7 | I-A, I-C | "No published method specifies, with the properties claimed here, how the document becomes the code." | Part 2 sweep | **Verified as worded** | The qualifier "with the properties claimed here" is doing necessary work and is retained verbatim. Nothing found in the sweep supplies the full five-property combination. |
| L8 | II-F | "consequently, the present paper does not claim that governance-to-code translation is wholly unprecedented." | — | **Verified — preserved unchanged** | This is exactly the narrow position the instruction requires. It is strengthened, not weakened, by the new citations. |
| L9 | III / Step 1 | Knight Capital: "≈USD 440M in losses in ~45 minutes", stale deployment flag, no malware. | [14] SEC Admin. Proc. File No. 3-15570 (16 Oct 2013) | **Verified as consistent** | The SEC order and Market Access Rule citation are correctly identified. The loss figure and mechanism are the widely reported facts of that matter. |
| L10 | VII-G | "a 32.98% false-permit rate under gate ablation on a 360,000-item adversarial corpus" attributed to [15], [16] and "taken as given". | [15], [16] | **Verified as attribution only** | The manuscript does not re-derive or re-measure this; it is explicitly cited as prior work. No change needed. This artifact does not reproduce it and must not be read as corroborating it. |
| L11 | II | "the permit-token and trace-record constructs of [15] do not themselves specify a requirement-reference field" | [15] | **Verified against the released artifact** | Confirmed against the enforcement artifact of record (`Gamma-Permit-Package`, commit `40fa8f0`): its predicate vector and trace schema carry no requirement-reference field. See `docs/CASE_B_LDREA_TRACEABILITY.md`. |

## Part 2 — The requested sweep: compliance-by-design, regulatory technology, agent-governance toolkits, 2024–2026

Searched: policy generation from natural language; machine-readable compliance;
runtime governance for agentic AI; governance-to-control translation;
agent-governance toolkits; deontic/normative policy engines.

| Work | Identifier / date | Relation to this paper | Action |
|---|---|---|---|
| **Koch, "From Governance Norms to Enforceable Controls: A Layered Translation Method for Runtime Guardrails in Agentic AI"** | arXiv:2604.05229, 6 Apr 2026 | **The closest adjacent work found.** Same problem statement: connecting standards-derived governance objectives to runtime controls, via four layers (governance objectives, design-time constraints, runtime mediation, assurance feedback), with a control tuple and a runtime-enforceability rubric, demonstrated on a procurement-agent case. **Does not** provide canonical serialization, bundle hashing, total risk disposition, authority-matrix closure, or receipt-level traceability. | **CITED AND POSITIONED** in Section II-F. Its existence is why the sweep mattered. |
| Joshi, Finin, Joshi, Kagal, "Deontic Policies for Runtime Governance of Agentic AI Systems" (AgenticRei) | arXiv:2606.19464, 17 Jun 2026 | Deontic policy language (OWL/Rei) with obligation lifecycle and meta-policy conflict resolution, evaluated outside the LLM. Explicitly **expresses constraints that already exist** and does not address deriving them from enterprise risk assessments or risk registers. | **CITED** as the nearest normative-policy-engine neighbour; directly supports the manuscript's claim that the *upstream derivation* question is open. |
| Microsoft Agent Governance Toolkit | open-sourced 2 Apr 2026 | An engineering toolkit (policy enforcement, zero-trust identity, sandboxing) covering the OWASP Agentic Top 10. Tooling, not a derivation method; supplies no register-to-predicate mapping. | Not cited. Recorded here as swept; adding it would not change any claim. |
| "Governance by Construction for Generalist Agents"; "Runtime Governance for AI Agents: Policies on Paths"; "Prose2Policy" | arXiv:2605.20874; 2603.16586; 2603.15799 | Structural checkpoints, path policies, and LLM natural-language→Rego translation respectively. All are enforcement-side or extraction-side; none assigns a disposition to every register row or closes predicates against an approved authority matrix. | Not cited individually. Recorded as swept. |

**Conclusion of the sweep.** The manuscript's narrow position holds. Governance-to-code
translation is **not** unprecedented — and the manuscript already says so. What the
sweep confirms is that the *specific combination* of (i) total disposition,
(ii) no prose treated as executable semantics, (iii) gate membership independent
of scalar priority, (iv) authority-matrix and version closure, and (v) temporally
valid traceability to receipts, is not supplied together by any work found.
**No novelty claim was expanded.** One citation was added because omitting it
would have been a defect.

## Part 3 — Reference audit

| Ref | Field checked | Finding | Action |
|---|---|---|---|
| [1] NIST AI RMF 1.0, NIST AI 100-1, Jan 2023 | number, date | Correct | none |
| [2] ISO/IEC 42001:2023, Dec 2023 | number, date | Correct | none |
| [3] ISO 31000:2018, Feb 2018 | number, date | Correct | none |
| [4] OSFI E-23 (pub. 11 Sep 2025, eff. 1 May 2027); B-10 (2023); B-13 (2022); E-21 (2024); Jul 2026 agentic-AI bulletin | dates | Consistent throughout the manuscript. The Jul 2026 bulletin postdates automated verification; **flagged for author confirmation**. | flag |
| [5] SR 11-7 / OCC 2011-12, 4 Apr 2011 | number, date | Correct | none |
| [6] CIRO Rule 3600, ss. 3608–3622 | rule range | Consistent with the Case A obligation set | none |
| [7] Reg. (EU) 2024/1689 Art. 113; Reg. (EU) 2026/1744 Digital Omnibus | numbers, dates | 2024/1689 correct. The 2026/1744 amendment and its deferral dates postdate automated verification; **flagged for author confirmation** against the Official Journal. | flag |
| [8] XACML 3.0, OASIS Standard, Jan 2013; **OPA `[VERIFY version cited]`** | version marker | XACML correct. OPA: **marker resolved** — no version is cited; the reference now points to the documentation with an access date. OPA is a CNCF *graduated* project (graduated 29 Jan 2021). | **RESOLVED** |
| [9] GSN Community Standard v3, SCSC-141C, 2021 | number | Correct | none |
| [10] Rose, Borchert, Mitchell, Connelly, NIST SP 800-207, Aug 2020 | authors, number, date | Correct | none |
| [11] J. P. Anderson, ESD-TR-73-51, Oct 1972 | number, date | Correct | none |
| [12] IEC 61511:2016 / ANSI/ISA-84.00.01 | numbers | Correct | none |
| [13] NIST TACIP COI discussion draft, 3 Aug 2026 | status | Already correctly qualified in-text as unpublished and COI-distributed, cited by date and hash. Postdates verification; **flagged**. | flag |
| [14] SEC Admin. Proc. 3-15570, 16 Oct 2013; 17 CFR §240.15c3-5 | numbers, date | Correct | none |
| [15] IEEE Access, doc. 11641546, **`[INSERT final DOI from IEEE Xplore]`** | DOI | **Could not be verified** — IEEE Xplore returned no content to automated retrieval. **No DOI was invented.** Marker resolved by citing the early-access article number without a DOI. **Author must insert the final DOI once assigned.** Separately: [15] gives the author as "A. Gill" while [16] gives "A. Gill-Lakhowal"; an indexing record for [15] shows "Gill-Lakhowal". **Flagged for the author to make consistent** — not changed, because an author's published byline is theirs to confirm. | **RESOLVED + 2 flags** |
| [16] Zenodo, doi 10.5281/zenodo.20369438 | DOI format | Well-formed Zenodo DOI; **flagged for author confirmation** | flag |
| [17] US 2026/0127298 A1, pub. 7 May 2026 | number, date | Postdates verification; **flagged for author confirmation** | flag |
| [18] Jayasundara et al., ACM Comput. Surv. 57(4), **art. no. 104**, pp. 1–37, 2025 | article number | **DISCREPANCY.** The DOI, authors, title, volume, issue and year all verify. One indexing record gives the article number as **102** (pages 102:1–102:37), not 104. ACM and dblp both blocked automated retrieval, so this could not be resolved authoritatively. **Action: the disputed article number is removed**; volume, issue, year and DOI are retained, which locate the work unambiguously. | **MODIFIED** |
| [19] Narouei et al., IEEE TDSC 17(3):506–517, 2020, doi 10.1109/TDSC.2018.2818708 | all | Consistent | none |
| [20] Mavračić, arXiv:2510.24383, 2025 | author, id, year | **Verified** (submitted 28 Oct 2025) | none |
| [21] arXiv:2604.13767, 2026 | id | **Unverified** — not retrievable | flag |
| [22] Sharma & Kunkel, arXiv:2605.23297, 2026 | id | **Unverified** — not retrievable | flag |
| [23] Uchibeke, arXiv:2603.20953, Mar 2026 | id, title | **Verified** (identifier resolves to the cited title) | none |
| [24] Rundgren, Jordan, Erdtman, RFC 8785 (JCS), Jun 2020 | authors, number, date | Correct — and the artifact implements it, with conformance tests against the RFC's own vectors | none |
| [25] Fleiss, *Psychol. Bull.* 76(5):378–382, 1971 | all | Correct | none |
| [26] Krippendorff, *Content Analysis*, 4th ed., SAGE, 2018 | all | Correct | none |
| [27] Gwet, *Br. J. Math. Stat. Psychol.* 61(1):29–48, 2008 | all | Correct | none |
| **[28] NEW** | Koch, arXiv:2604.05229, Apr 2026 | **Verified** against the arXiv abstract page | **ADDED** |
| **[29] NEW** | Joshi, Finin, Joshi, Kagal, arXiv:2606.19464, Jun 2026 | **Verified** against the arXiv abstract page | **ADDED** |

### Summary

* **Markers resolved:** 2 (`[VERIFY version cited]` on OPA; `[INSERT final DOI]` on [15]).
* **References corrected:** 1 ([18], disputed article number removed).
* **References added:** 2 ([28], [29]) — required by the sweep.
* **Flagged for author confirmation, not invented:** 7 — [4] Jul 2026 bulletin,
  [7] Reg. 2026/1744, [13] TACIP draft, [15] final DOI *and* author-name
  consistency, [16] Zenodo DOI, [17] patent publication, [21] and [22] arXiv
  identifiers.

Every flagged item postdates what could be checked against a reachable primary
source, or sits behind a publisher that refused automated retrieval. **None was
guessed at.** Each is listed in `paper_update/FINAL_REVIEWER_RISK_REPORT.md` with
a severity.
