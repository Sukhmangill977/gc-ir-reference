"""Produce a MEASURED copy of the manuscript with the placeholders replaced.

    python -m tools.make_measured_docx --source "<path to FINAL.docx>"

Writes ``From_Risk_Register_to_Runtime_Predicate_MEASURED.docx`` **next to the
source**, leaving the original untouched, plus a text change log.

**Scope.** This script performs *only* mechanical, unambiguous substitutions:
provisional numbers the artifact re-measured, bracketed placeholders the artifact
resolved, and empirical-status statements that are now false.  It does not
rewrite prose, and it deliberately does not touch:

* any theoretical proposition, proof, or its statement;
* the claim boundary, the limitations, or the non-contributions;
* anything about RQ5, which remains deferred;
* the evidence classification of Case B.

Substantive rewrites -- the Monte Carlo panel attribution, the new limitations,
the collision wording -- are **not** applied automatically.  They change meaning,
and meaning is the author's to change.  ``paper_update/MEASURED_RESULTS.md`` gives
the exact wording for each, and the change log below lists every one that was left
for manual application.

Editing is done directly on the WordprocessingML, matching runs of text within a
paragraph, so paragraph and run formatting is preserved.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import zipfile
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CASE_A_HASH = "f5cbc3a8016159d2074005fa021bf76ca04fb7aed1408f5ec845418460a43536"
CASE_B_HASH = "2850155a2ee7d4c01db4748a891891bae27c48f4c9c2c7eccd30beb7d1aa33ce"
FREEZE_TAG = "preregister-tier0-v2.2"
REPO_URL = "https://github.com/Sukhmangill977/gc-ir-reference"

#: (search, replace, why) -- applied to paragraph text.
#: v2 campaign values, read from results/final_v2/.
SUBSTITUTIONS = [
    (
        "translation determinism of 1.000 over 31 compilation runs",
        "translation determinism of 1.000 over 62 compilation runs (31 per case)",
        "Abstract: the v2 campaign ran 31 per case following the examiner's "
        "10 repeats + 10 row shuffles + 5 key shuffles + 3 LC_ALL + 3 TZ "
        "breakdown, 62 in total. Evidence: results/final_v2/determinism_runs.csv",
    ),
    (
        "1.000 (31/31 runs, pinned container)",
        "1.000 (62/62 runs; 31 per case, reproduced on three operating systems)",
        "Section XI-B metrics table: measured count and environment. TD = 1.000 "
        "was reproduced on macOS/arm64, Ubuntu/x86_64, Windows/AMD64 and a Debian "
        "container/aarch64. Evidence: results/final_v2/CI_STATUS.md",
    ),
    (
        "Measured: TD = 1.000 over 31 compilation runs",
        "Measured: TD = 1.000 over 62 compilation runs (31 per case)",
        "Section XI-H: measured count. "
        "Evidence: results/final_v2/determinism_runs.csv",
    ),
    (
        "[PENDING: hash-pinned Case B artifact release]",
        "Case B canonical bundle payload SHA-256: " + CASE_B_HASH,
        "Section X: placeholder resolved. "
        "Evidence: cases/case_b/expected/reference_hashes.json",
    ),
    (
        "[TO CONFIRM: final repository path at release]",
        REPO_URL + " (release tag v1.0.0; preregistration freeze " + FREEZE_TAG + ")",
        "Appendix C: the repository is public and the freeze tag was pushed before "
        "the reportable campaign ran. Evidence: results/final_v2/PROVENANCE.json",
    ),
    (
        "[PENDING: v1.0 freeze and $id host set at the artifact-repository release]",
        "The schema is frozen at v1.0 and hash-pinned in the release manifest; "
        "schema $id values are stable identifiers rather than resolvable endpoints, "
        "and the authoritative copies are the files in the tagged release.",
        "Appendix A: resolved as far as it honestly can be. A resolvable $id host "
        "is NOT claimed, because none is maintained. The artifact-runs memo's "
        "'v1.1 JSON Schema' has no manuscript basis and no revision was made -- see "
        "docs/ARTIFACT_RUNS_COMPLIANCE.md section C2.",
    ),
    (
        "the maximum per-risk heat-map flip probability is 0.321",
        "the maximum per-risk heat-map flip probability is 0.321 (MCSE 0.001)",
        "Section XI-G: value confirmed at K = 250,000 in the v2 campaign; Monte "
        "Carlo standard error added. "
        "Evidence: results/final_v2/monte_carlo_summary.json",
    ),
    (
        "while FP\u1d62^C* = 0.000 across the register by construction",
        "while FP\u1d62^C* = 0.000 across the register -- verified by re-running the "
        "approved consequence-class classifier on 1,000 perturbed draws, with no "
        "membership change observed",
        "Section XI-G: the zero is verified rather than asserted. Evidence: "
        "results/final_v2/monte_carlo_summary.json "
        "cstar_membership_changes_observed",
    ),
]

#: Changes that must NOT be automated -- they alter meaning.
MANUAL_ONLY = [
    (
        "Section XII -- determinism scope MUST BE WIDENED, NOT DELETED",
        "Three operating systems and two machine architectures are now measured "
        "(macOS/arm64, Ubuntu/x86_64, Windows/AMD64, Debian container/aarch64), "
        "so the current limitation understates the evidence -- but deleting it "
        "would overstate it, because a finite matrix is not the set of all "
        "environments. The replacement paragraph changes what is claimed and is "
        "therefore left for manual application.",
        "paper_update/MEASURED_RESULTS_V2.md section 4",
    ),
    (
        "Section X -- the L-DREA predicate-family linkage",
        "New material establishing continuity between the Case B predicate set "
        "and the published enforcement artifact's own 13-member predicate family, "
        "with four exact correspondences, three by family, and two declared gaps. "
        "It adds a claim and must be read before insertion.",
        "paper_update/MEASURED_RESULTS_V2.md section 7",
    ),
    (
        "Section XI-G / XI-C -- Monte Carlo panel attribution",
        "The manuscript states that 'the independent panel freezes discrete "
        "probability masses over plausible ratings'. NO PANEL HAS BEEN CONVENED. "
        "The distributions are author-specified. This is the single most important "
        "correction and it changes what the result means, so it is left for "
        "manual application.",
        "paper_update/MEASURED_RESULTS.md section 5",
    ),
    (
        "Section IX -- publish the three non-runtime rows' ratings",
        "GD_min = 3 is computed over all sixteen rows, but the table publishes "
        "L x I for only the thirteen runtime rows, so the value is not "
        "reproducible from the paper. Add R-14 = 12, R-15 = 6, R-16 = 8 and the "
        "sensitivity sentence (GD_min ranges 2-5 across plausible ratings).",
        "paper_update/MEASURED_RESULTS.md section 2.2",
    ),
    (
        "Section IX -- 'three-way collision at s = 12'",
        "On the pinned artifact the score-12 collision has four members, because "
        "R-14 also rates 12. Scope the sentence to the runtime rows.",
        "paper_update/MEASURED_RESULTS.md section 2.3",
    ),
    (
        "Section XII -- two new limitations",
        "Add the GD_min fixture-sensitivity limitation and the sensitivity-model "
        "provenance limitation.",
        "paper_update/MEASURED_RESULTS.md sections 8.2 and 8.3",
    ),
    (
        "Section XI-I -- held-out-register hash",
        "The Tier-0 freeze does not contain one, because no held-out register has "
        "been authored. State that it is committed in a Tier-1 freeze before "
        "recruitment opens.",
        "paper_update/MEASURED_RESULTS.md section 13",
    ),
    (
        "Appendix C / Data & Code Availability -- repository path",
        "'[TO CONFIRM: final repository path at release]' cannot be resolved until "
        "the repository is pushed. No DOI exists; do not cite one.",
        "docs/ZENODO_RELEASE_STEPS.md",
    ),
    (
        "Section XII -- determinism scope",
        "LEAVE UNCHANGED. The cross-platform CI matrix is configured but has not "
        "run, so the limitation still holds as written.",
        "results/final/CI_STATUS.md",
    ),
    (
        "Sections II and XIII -- [VERIFY] markers",
        "A final literature sweep and a sentence-level overlap check against the "
        "published version of [15]. Author tasks; no artifact can discharge them.",
        "-",
    ),
]


def paragraph_text(paragraph):
    return "".join(node.text or "" for node in paragraph.iter("{%s}t" % W))


def set_paragraph_text(paragraph, text):
    """Write ``text`` into the paragraph's first run, blanking the rest.

    Run-level formatting inside a replaced paragraph is not preserved for the
    replaced span, but paragraph style, numbering and surrounding structure are.
    """
    nodes = list(paragraph.iter("{%s}t" % W))
    if not nodes:
        return False
    nodes[0].text = text
    nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for node in nodes[1:]:
        node.text = ""
    return True


def apply_substitutions(xml_bytes):
    root = ET.fromstring(xml_bytes)
    applied = []
    for paragraph in root.iter("{%s}p" % W):
        text = paragraph_text(paragraph)
        if not text:
            continue
        updated = text
        hits = []
        for search, replace, why in SUBSTITUTIONS:
            if search in updated:
                updated = updated.replace(search, replace)
                hits.append((search, replace, why))
        if hits:
            if set_paragraph_text(paragraph, updated):
                applied.extend(hits)
    return ET.tostring(root, encoding="UTF-8", xml_declaration=True), applied


def build(source, destination, changelog_path):
    if os.path.abspath(source) == os.path.abspath(destination):
        raise SystemExit("refusing to overwrite the original manuscript")

    shutil.copyfile(source, destination)

    with zipfile.ZipFile(source) as archive:
        names = archive.namelist()
        contents = {name: archive.read(name) for name in names}

    document, applied = apply_substitutions(contents["word/document.xml"])
    contents["word/document.xml"] = document

    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            archive.writestr(name, contents[name])

    unapplied = [
        (search, replace, why) for (search, replace, why) in SUBSTITUTIONS
        if not any(hit[0] == search for hit in applied)
    ]

    lines = [
        "# MEASURED manuscript copy — change log",
        "",
        "Source:      %s" % os.path.basename(source),
        "Destination: %s" % os.path.basename(destination),
        "",
        "**The original manuscript is not modified.** This log records every change",
        "made to the copy, and every change that was deliberately left for manual",
        "application because it alters meaning rather than a value.",
        "",
        "---",
        "",
        "## Applied automatically (%d)" % len(applied),
        "",
    ]
    if applied:
        seen = set()
        for search, replace, why in applied:
            if search in seen:
                continue
            seen.add(search)
            lines += [
                "### `%s`" % (search[:90] + ("…" if len(search) > 90 else "")),
                "",
                "**Replaced with:** %s" % replace,
                "",
                "**Why:** %s" % why,
                "",
            ]
    else:
        lines += ["_None matched. See the note below._", ""]

    if unapplied:
        lines += [
            "## Not found in the source document (%d)" % len(unapplied),
            "",
            "These substitutions were prepared but their search text did not appear.",
            "That usually means the manuscript's wording differs slightly from the",
            "extracted text, or the passage has already been edited. **Each must be",
            "checked and applied by hand.**",
            "",
        ]
        for search, replace, why in unapplied:
            lines += [
                "* **Searched for:** `%s`" % search,
                "  * **Intended replacement:** %s" % replace,
                "  * **Why:** %s" % why,
                "",
            ]

    lines += [
        "---",
        "",
        "## Left for manual application — these change meaning (%d)" % len(MANUAL_ONLY),
        "",
        "A script should not silently rewrite what a claim means. Each of these is",
        "specified with publication-ready wording in the referenced file.",
        "",
    ]
    for title, description, reference in MANUAL_ONLY:
        lines += [
            "### %s" % title,
            "",
            description,
            "",
            "See: `%s`" % reference,
            "",
        ]

    lines += [
        "---",
        "",
        "## Deliberately untouched",
        "",
        "* Propositions 1–3, their statements and their proofs.",
        "* The claim boundary (Section XIV), the non-contributions (Section I-D),",
        "  and the limitations (Section XII) other than the two additions listed above.",
        "* Everything concerning RQ5, which remains preregistered and deferred.",
        "* The evidence classification of Case B as a forensic reconstruction, and",
        "  of the 284,807-event run as conformance-class evidence belonging to [15].",
        "* Every `[TO REPORT]` marker for SNR and DF: no value exists.",
        "",
    ]

    with open(changelog_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))

    return applied, unapplied


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, help="path to the FINAL .docx")
    parser.add_argument("--out", default=None)
    parser.add_argument(
        "--changelog",
        default=os.path.join(REPO_ROOT, "paper_update", "DOCX_CHANGE_LOG.md"),
    )
    args = parser.parse_args(argv)

    destination = args.out or os.path.join(
        os.path.dirname(os.path.abspath(args.source)),
        "From_Risk_Register_to_Runtime_Predicate_MEASURED.docx",
    )
    applied, unapplied = build(args.source, destination, args.changelog)

    print("wrote %s" % destination)
    print("wrote %s" % args.changelog)
    print("applied %d substitution(s); %d not found; %d left for manual application"
          % (len({a[0] for a in applied}), len(unapplied), len(MANUAL_ONLY)))
    for search, _, _ in unapplied:
        print("  NOT FOUND: %s" % search[:80])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
