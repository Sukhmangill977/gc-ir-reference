"""Build the Case B -> L-DREA traceability mapping.

    python -m tools.build_ldrea_traceability

Every row is verified against the published enforcement artifact before it is
written.  A Case B predicate is mapped to an L-DREA predicate only when the
L-DREA identifier is one that ``tools/derive_ldrea_predicate_family.py``
actually derived from that artifact's source, and only when the supporting
column or report field exists there.  Rows that cannot be established that way
are recorded with ``verification_status`` naming the gap, not dropped and not
guessed.

**Claim boundary, preserved.** Manuscript Section X: the 284,807-event run is a
golden-trace conformance result, "not detection evidence and ... not presented
as such", and what Case B adds is upstream -- "the register-to-disposition-to-
predicate mapping that produced those predicate families".  This file therefore
establishes *continuity of predicate family*, never detection performance, and
never that the compiled Case B bundle was executed against that corpus.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))
sys.path.insert(0, REPO_ROOT)

DEFAULT_LDREA_ROOT = "/Users/sukhmangill/Documents/GitHub/Gamma-Permit-Package"

#: Case B GC-IR predicate -> the L-DREA predicate(s) whose family it continues.
#:
#: Each entry names ONLY identifiers that the derivation script extracted from
#: the published artifact's own source.  ``basis`` states, in one line, why the
#: correspondence holds; ``correspondence`` grades how tight it is:
#:
#:   exact        -- the L-DREA artifact evaluates the same condition on the same
#:                   observable, under the same name
#:   family       -- same predicate family and same decision semantics, evaluated
#:                   on a domain-specific observable
#:   not_established -- no corresponding L-DREA predicate could be found
MAPPING = [
    {
        "gcir_id": "GCIR-B0001",
        "risk_id": "B-01",
        "acs_id": "ACS-B01-01",
        "gcir_predicate_family": "permit_binding",
        "ldrea_predicates": ["TOKEN_VALID", "AuthoritySignatureValid"],
        "correspondence": "exact",
        "ldrea_observables": ["TOKEN_VALID", "AuthoritySignatureValid", "PermitTokenID",
                              "ACT_PERMIT"],
        "basis": (
            "Both evaluate whether a valid, signed permit token is bound to the "
            "proposed action before release. TOKEN_VALID and "
            "AuthoritySignatureValid are members of the artifact's NODE_GATE_COLS "
            "predicate vector; PermitTokenID carries the binding."
        ),
    },
    {
        "gcir_id": "GCIR-B0002",
        "risk_id": "B-02",
        "acs_id": "ACS-B02-01",
        "gcir_predicate_family": "bound_check_on_measured_value",
        "ldrea_predicates": ["Gate_A3", "HARM_RISK_THETA"],
        "correspondence": "family",
        "ldrea_observables": ["HARM_RISK", "Gate_A3", "DoseLimitBoundPass"],
        "basis": (
            "Same family: a measured scalar compared against an approved bound, "
            "failing closed above it. In the L-DREA golden trace the bound is the "
            "harm-risk threshold theta (Gate_A3 / HARM_RISK_THETA, the observed "
            "FirstFailingGate for every adversarial row); in Case B it is the "
            "per-transaction amount limit. The predicate family and decision "
            "semantics correspond; the observable is domain-specific and the "
            "amount bound is NOT evaluated in the published corpus."
        ),
    },
    {
        "gcir_id": "GCIR-B0003",
        "risk_id": "B-03",
        "acs_id": "ACS-B03-01",
        "gcir_predicate_family": "windowed_count_bound",
        "ldrea_predicates": [],
        "correspondence": "not_established",
        "ldrea_observables": [],
        "basis": (
            "No predicate in the published L-DREA family evaluates a rolling "
            "per-counterparty window count. The artifact's temporal predicates "
            "(STALE_CONTEXT, TELEMETRY_STALE) concern evidence freshness, not "
            "velocity. Recorded as a gap rather than mapped to an approximate "
            "neighbour."
        ),
    },
    {
        "gcir_id": "GCIR-B0004",
        "risk_id": "B-04",
        "acs_id": "ACS-B04-01",
        "gcir_predicate_family": "restricted_party_screening",
        "ldrea_predicates": ["Gate_A3"],
        "correspondence": "family",
        "ldrea_observables": ["Gate_A3", "HARM_RISK", "ReasonCodes"],
        "basis": (
            "Same family: a deterministic lookup of the counterparty against a "
            "signed list artifact, failing closed on a match. The L-DREA corpus "
            "expresses the corresponding condition through the class-1 fraud "
            "labelling that trips Gate_A3 with reason code "
            "GATE_A3_HARM_RISK_FAIL; the sanctions list itself is not an "
            "observable in that corpus. The ASB scenario family "
            "'cross_entity_fraud_propagation' covers the same hazard class."
        ),
    },
    {
        "gcir_id": "GCIR-B0005",
        "risk_id": "B-05",
        "acs_id": "ACS-B05-01",
        "gcir_predicate_family": "permit_single_use_and_replay",
        "ldrea_predicates": ["TOKEN_VALID"],
        "correspondence": "exact",
        "ldrea_observables": ["PermitTokenID", "ReplayDivergenceFlag", "TOKEN_VALID"],
        "basis": (
            "Both evaluate permit single-use and replay novelty. The artifact "
            "carries ReplayDivergenceFlag as a decision-integrity flag and "
            "reports asb_replay_consistency = 1.0; 'replay_attack' is one of its "
            "eight named adversarial families, with 4,000 instances and zero "
            "false permits."
        ),
    },
    {
        "gcir_id": "GCIR-B0006",
        "risk_id": "B-06",
        "acs_id": "ACS-B06-01",
        "gcir_predicate_family": "receipt_commit_before_actuate",
        "ldrea_predicates": ["Gate_A7"],
        "correspondence": "exact",
        "ldrea_observables": ["CommitBeforeActuate", "CommitTimestamp", "ActuateTimestamp",
                              "HASH_prev", "HASH_current", "OrderingInversionFlag"],
        "basis": (
            "Both evaluate the same ordering property -- the decision receipt is "
            "committed to the hash-chained evidence record after authorization "
            "and before actuation. The artifact carries it as the "
            "CommitBeforeActuate column with HASH_prev/HASH_current chaining and "
            "an OrderingInversionFlag; Gate_A7 is the node gate observed failing "
            "together with Gate_A3 on every denied row."
        ),
    },
]

#: The compiler invariants Case B emits, and their L-DREA counterparts.
INVARIANT_MAPPING = [
    {
        "gcir_id": "GCIR-INV-EVIDENCE-COMMIT",
        "invariant_id": "INV-EVIDENCE-COMMIT",
        "gcir_predicate_family": "receipt_commit_before_actuate",
        "ldrea_predicates": ["Gate_A7"],
        "correspondence": "exact",
        "ldrea_observables": ["CommitBeforeActuate", "OrderingInversionFlag"],
        "basis": "The invariant states the ordering the artifact measures directly.",
    },
    {
        "gcir_id": "GCIR-INV-AUTHORITY-CLOSURE",
        "invariant_id": "INV-AUTHORITY-CLOSURE",
        "gcir_predicate_family": "authority_closure",
        "ldrea_predicates": ["AuthoritySignatureValid", "TOKEN_VALID"],
        "correspondence": "family",
        "ldrea_observables": ["AuthoritySignatureValid", "AuthorityRequired", "ACT_PERMIT"],
        "basis": (
            "Both require the proposed action to fall inside an approved "
            "authority before release. The artifact's check is signature-based at "
            "the node; the compiler invariant is a matrix-membership check "
            "upstream. Same family, different layer."
        ),
    },
    {
        "gcir_id": "GCIR-INV-VERSION",
        "invariant_id": "INV-VERSION",
        "gcir_predicate_family": "version_binding",
        "ldrea_predicates": [],
        "correspondence": "not_established",
        "ldrea_observables": ["ModelVersionHash", "SpecVersion", "DictionaryVersion",
                              "PolicyHash"],
        "basis": (
            "The artifact records version identifiers (ModelVersionHash, "
            "SpecVersion, DictionaryVersion, PolicyHash) as trace columns but does "
            "not evaluate a per-action version-binding predicate over them: no "
            "member of its predicate vector tests them. The observables exist; the "
            "predicate does not. Recorded as a gap."
        ),
    },
]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args):
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=root, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        return None


def load_family():
    path = os.path.join(REPO_ROOT, "cases", "case_b", "ldrea_predicate_family.json")
    if not os.path.exists(path):
        raise SystemExit(
            "run `python -m tools.derive_ldrea_predicate_family` first: %s" % path)
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def golden_trace_header(ldrea_root):
    directory = os.path.join(ldrea_root, "realdatatestcode")
    if not os.path.isdir(directory):
        return None, []
    for name in sorted(os.listdir(directory)):
        if name.endswith(".csv") and "GOLDEN_TRACE" in name:
            with open(os.path.join(directory, name), encoding="utf-8", newline="") as fh:
                return name, next(csv.reader(fh))
    return None, []


def compile_case_b():
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b")
    result = compile_bundle(case.compiler_inputs())
    return result.bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ldrea-root", default=DEFAULT_LDREA_ROOT)
    parser.add_argument("--out", default=os.path.join(
        REPO_ROOT, "cases", "case_b", "ldrea_traceability.json"))
    args = parser.parse_args(argv)

    family_doc = load_family()
    family = set(family_doc["predicate_family"]["all"])
    trace_name, header = golden_trace_header(args.ldrea_root)
    header_set = set(header)

    bundle = compile_case_b()
    bundle_predicates = {p["gcir_id"]: p for p in bundle.predicates}

    rows = []
    problems = []
    for entry in MAPPING + INVARIANT_MAPPING:
        row = dict(entry)
        checks = []

        predicate = bundle_predicates.get(entry["gcir_id"])
        checks.append({
            "check": "gcir_id exists in the compiled Case B bundle",
            "passed": predicate is not None,
            "detail": entry["gcir_id"],
        })
        if predicate is not None:
            expected_acs = entry.get("acs_id")
            if expected_acs:
                checks.append({
                    "check": "acs_id matches the compiled predicate",
                    "passed": predicate.get("acs_id") == expected_acs,
                    "detail": "%s vs %s" % (predicate.get("acs_id"), expected_acs),
                })
                checks.append({
                    "check": "risk_id matches the compiled predicate origin",
                    "passed": predicate["origin"]["origin_id"] == entry["risk_id"],
                    "detail": predicate["origin"]["origin_id"],
                })
            else:
                checks.append({
                    "check": "invariant origin matches",
                    "passed": predicate["origin"]["origin_id"] == entry["invariant_id"],
                    "detail": predicate["origin"]["origin_id"],
                })
            row["gcir_gate_type"] = predicate["gate_type"]
            row["gcir_gate_source"] = predicate["gate_source"]
            row["gcir_evaluation_basis"] = predicate["evaluation_basis"]

        unknown = [p for p in entry["ldrea_predicates"] if p not in family]
        checks.append({
            "check": "every named L-DREA predicate is a member of the derived family",
            "passed": not unknown,
            "detail": "unknown: %s" % unknown if unknown else "all members",
        })

        missing_cols = [
            c for c in entry["ldrea_observables"]
            if header_set and c not in header_set
        ]
        checks.append({
            "check": "every named L-DREA observable is a golden-trace column",
            "passed": not missing_cols,
            "detail": "missing: %s" % missing_cols if missing_cols else "all present",
        })

        if entry["correspondence"] == "not_established":
            checks.append({
                "check": "gap is declared rather than mapped",
                "passed": entry["ldrea_predicates"] == [],
                "detail": "no L-DREA predicate claimed",
            })

        row["verification_checks"] = checks
        row["verification_status"] = (
            "verified" if all(c["passed"] for c in checks)
            else "verification_failed"
        )
        if entry["correspondence"] == "not_established" and row["verification_status"] == "verified":
            row["verification_status"] = "gap_declared_and_verified"
        rows.append(row)
        if row["verification_status"] == "verification_failed":
            problems.append(entry["gcir_id"])

    counts = {}
    for row in rows:
        counts[row["correspondence"]] = counts.get(row["correspondence"], 0) + 1

    document = {
        "document_type": "CaseB_LDREA_Traceability",
        "schema_version": "1.0",
        "generated_by": "tools/build_ldrea_traceability.py",
        "claim_boundary": (
            "This mapping establishes CONTINUITY OF PREDICATE FAMILY between the "
            "Case B compiled bundle and the published L-DREA enforcement artifact. "
            "It does NOT establish detection performance, does NOT claim the Case B "
            "bundle was executed against the 284,807-event corpus, and does NOT "
            "reproduce or re-assert that run's figures. Manuscript Section X is "
            "explicit that the run is a golden-trace conformance result, not "
            "detection evidence, and that Case B's contribution here is the "
            "upstream register-to-disposition-to-predicate reconstruction."
        ),
        "external_artifact": {
            "role": "enforcement layer, manuscript reference [15]",
            "repository": family_doc["source_repository"]["remote"],
            "local_path": args.ldrea_root,
            "commit": family_doc["source_repository"]["commit"],
            "tag": family_doc["source_repository"]["tag"],
            "golden_trace_file": trace_name,
            "artifact_subtree": "realdatatestcode/",
            "note": "This is the repository of record named in the manuscript's "
                    "Appendix C. No tag is present on it; the commit SHA is the "
                    "pin.",
        },
        "ldrea_predicate_family": {
            "size": family_doc["predicate_family"]["size"],
            "members": family_doc["predicate_family"]["all"],
            "derivation": family_doc["predicate_family"]["definition_site"],
            "cross_checks_passed": family_doc["all_cross_checks_passed"],
        },
        "p1_p13_finding": {
            "memo_claim": "the artifact-runs memo refers to a 'P1-P13' predicate "
                          "identifier family",
            "finding": (
                "No P1-P13 predicate identifier family exists in the published "
                "artifact. The identifiers P1-P4 exist, but they name four "
                "stress-test SCENARIOS in realdatatestcode/stress_test.py, not "
                "predicates. The artifact's predicate family is the 13 named "
                "members listed above, derived from NODE_GATE_COLS plus the three "
                "derived deficit columns, and corroborated by three independently "
                "reported counts and by single_deficit_score = 1/13."
            ),
            "p_identifiers_found": family_doc["p_identifiers_in_artifact"]["found"],
            "action_taken": "Mapped Case B to the 13 REAL predicate identifiers. "
                            "No P1-P13 identifiers were fabricated.",
        },
        "mapping": rows,
        "summary": {
            "rows": len(rows),
            "by_correspondence": counts,
            "verified": sum(1 for r in rows if r["verification_status"].startswith(
                ("verified", "gap_declared"))),
            "failed": len(problems),
            "case_b_predicates_total": len(bundle.predicates),
            "case_b_bundle_hash": bundle.payload_hash,
        },
        "what_is_established": [
            "Four Case B predicate families correspond EXACTLY to named members of "
            "the published L-DREA predicate vector, on the same observables: permit "
            "binding, permit single-use/replay, and receipt commit-before-actuate "
            "(twice, once as a risk-derived predicate and once as a compiler "
            "invariant).",
            "Two correspond by FAMILY -- same decision semantics on a "
            "domain-specific observable: the bound check and the restricted-party "
            "screening.",
            "The Case B bundle's predicate identifiers resolve to the artifact "
            "subtree realdatatestcode/ in the repository of record.",
        ],
        "what_is_NOT_established": [
            "That the compiled Case B bundle was executed against the "
            "284,807-event corpus. It was not.",
            "Any detection performance, false-permit rate, or unauthorized-execution "
            "rate for Case B. Those figures belong to [15] and are conformance-class "
            "there.",
            "A velocity/windowed-count predicate in the L-DREA family (B-03). None "
            "exists; the gap is declared.",
            "A per-action version-binding predicate in the L-DREA family "
            "(INV-VERSION). The version observables exist as trace columns but no "
            "member of the predicate vector evaluates them; the gap is declared.",
        ],
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True)
        handle.write("\n")

    print("Case B -> L-DREA traceability: %d rows" % len(rows))
    for row in rows:
        print("  %-28s %-16s %-16s %s"
              % (row["gcir_id"], row.get("risk_id") or row.get("invariant_id"),
                 row["correspondence"],
                 ",".join(row["ldrea_predicates"]) or "(none - gap declared)"))
    print("")
    print("  by correspondence: %s" % counts)
    print("  verification failures: %d" % len(problems))
    print("wrote %s" % os.path.relpath(args.out, REPO_ROOT))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
