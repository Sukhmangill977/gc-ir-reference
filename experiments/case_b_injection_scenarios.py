"""The thirteen Case B injection scenarios.

The artifact-runs memo asks that "the thirteen Case B injection scenarios become
executable".  The thirteen are not invented here: they are the adversarial
scenario families the **published L-DREA enforcement artifact** actually
enumerates --

    8 adversarial attack families
      (concurbench_full_report.json :: adversarial_robustness.attack_families)
    5 ASB scenario families
      (concurbench_full_report.json :: asb.scenario_families)
    -------------------------------------------------------------------------
    13 families

Each scenario injects the corresponding failure into a Case B **decision** and
asserts that the compiled bundle's precedence relation resolves to `SAFE_STATE`.

**What this establishes.** That the Case B compiled bundle refuses to permit
under each hazard class the enforcement artifact enumerates -- i.e. that the
upstream compilation produced a gate set adequate to those classes.

**What it does not establish.** Detection performance. These are decision-level
injections against the compiled predicate set, not a run over the 284,807-event
corpus, and no figure from that corpus is reproduced or implied. Manuscript
Section X's claim boundary is preserved exactly.
"""

from __future__ import annotations

import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_ldrea_families():
    """The 13 family names, read from the published artifact's own report."""
    mapping_path = os.path.join(REPO_ROOT, "cases", "case_b", "ldrea_traceability.json")
    with open(mapping_path, encoding="utf-8") as handle:
        mapping = json.load(handle)
    ldrea_root = mapping["external_artifact"]["local_path"]
    report = os.path.join(ldrea_root, "realdatatestcode", "concurbench_full_report.json")
    if not os.path.exists(report):
        return None, None
    with open(report, encoding="utf-8") as handle:
        blob = json.load(handle)
    attack = blob["adversarial_robustness"]["attack_families"]
    asb = blob["asb"]["scenario_families"]
    return attack, asb


#: family name -> (which Case B predicate the injection must trip, how it is injected)
#:
#: ``outcome`` is the evaluation outcome injected for that predicate:
#:   "fail"    the condition is violated
#:   "unknown" the evidence is missing, stale or schema-invalid -- indeterminacy,
#:             which a mandatory gate must resolve to failure
SCENARIOS = {
    # -- the eight adversarial attack families -----------------------------
    "missing_predicate": {
        "target": "GCIR-B0001",
        "outcome": "unknown",
        "hazard": "the permit-binding evidence is absent at authorization time",
        "why_safe_state": "indeterminacy on a mandatory gate resolves to failure "
                          "(on_unknown = fail), never to a silent pass",
    },
    "corrupted_input": {
        "target": "GCIR-B0002",
        "outcome": "unknown",
        "hazard": "the signed instruction artifact is schema-invalid, so the "
                  "amount cannot be compared against the approved bound",
        "why_safe_state": "a corrupted artifact is indeterminacy, not a pass",
    },
    "toctou": {
        "target": "GCIR-B0006",
        "outcome": "fail",
        "hazard": "the evidence record is committed after actuation rather than "
                  "before it, so the state read at check time is not the state at "
                  "use time",
        "why_safe_state": "the commit-before-actuate ordering predicate fails",
    },
    "replay_attack": {
        "target": "GCIR-B0005",
        "outcome": "fail",
        "hazard": "a previously redeemed permit is presented again",
        "why_safe_state": "the single-use predicate fails on a redeemed permit",
    },
    "payload_mutation": {
        "target": "GCIR-B0001",
        "outcome": "fail",
        "hazard": "the instruction is altered after the permit was issued, so the "
                  "permit's bound hash no longer matches the transaction",
        "why_safe_state": "the permit-binding predicate fails on the hash mismatch",
    },
    "concurrency_conflict": {
        "target": "GCIR-B0003",
        "outcome": "fail",
        "hazard": "concurrent releases to one counterparty exceed the approved "
                  "window bound",
        "why_safe_state": "the velocity bound fails",
    },
    "network_partition_or_delay": {
        "target": "GCIR-B0004",
        "outcome": "unknown",
        "hazard": "the restricted-party screening service is unreachable, so no "
                  "signed screening artifact is available",
        "why_safe_state": "an unreachable evidence producer is indeterminacy; the "
                          "mandatory sanctions gate fails closed rather than "
                          "permitting an unscreened counterparty",
    },
    "adaptive_attacker": {
        "target": "GCIR-B0002",
        "outcome": "fail",
        "hazard": "an attacker splits a large payment into instructions shaped to "
                  "sit just under each individual bound",
        "why_safe_state": "the per-transaction bound still fails on the instruction "
                          "that crosses it; the residual -- structuring below every "
                          "bound -- is stated in the ACS warrant boundary and is "
                          "NOT claimed to be caught here",
    },
    # -- the five ASB scenario families ------------------------------------
    "identity_provenance_deception": {
        "target": "GCIR-B0001",
        "outcome": "fail",
        "hazard": "a forged authority signature is presented on the permit",
        "why_safe_state": "the permit-binding predicate verifies the signature",
    },
    "runtime_infrastructure_drift": {
        "target": "GCIR-INV-VERSION",
        "outcome": "fail",
        "hazard": "the runtime configuration fingerprint no longer matches the "
                  "assessed configuration",
        "why_safe_state": "the compiler invariant INV-VERSION fails per action -- "
                          "note this is a predicate the GC-IR bundle emits and the "
                          "published L-DREA family does NOT contain (see "
                          "docs/CASE_B_LDREA_TRACEABILITY.md, declared gap)",
    },
    "economic_logic_fragility": {
        "target": "GCIR-B0002",
        "outcome": "fail",
        "hazard": "the instruction amount exceeds the approved automated release "
                  "ceiling",
        "why_safe_state": "the amount bound fails",
    },
    "cross_entity_fraud_propagation": {
        "target": "GCIR-B0004",
        "outcome": "fail",
        "hazard": "the counterparty is a member of the restricted-party list",
        "why_safe_state": "the sanctions screening predicate fails and escalates",
    },
    "session_intent_compromise": {
        "target": "GCIR-B0001",
        "outcome": "unknown",
        "hazard": "the session's permit cannot be resolved to this transaction, so "
                  "the binding is indeterminate",
        "why_safe_state": "indeterminacy on a mandatory gate fails closed",
    },
}


def run(bundle):
    """Run all thirteen injections against a compiled Case B bundle."""
    from gcir.precedence import resolve

    attack, asb = load_ldrea_families()
    expected_names = (list(attack) + list(asb)) if attack else sorted(SCENARIOS)

    predicates = {p["gcir_id"] for p in bundle.predicates}
    rows = []

    for family in expected_names:
        spec = SCENARIOS.get(family)
        if spec is None:
            rows.append({
                "family": family,
                "status": "NO_SCENARIO_DEFINED",
                "detail": "the published artifact enumerates this family but no "
                          "Case B injection is defined for it",
                "decision": None,
                "passed": False,
            })
            continue
        if spec["target"] not in predicates:
            rows.append({
                "family": family,
                "status": "TARGET_NOT_IN_BUNDLE",
                "detail": spec["target"],
                "decision": None,
                "passed": False,
            })
            continue

        outcomes = {p["gcir_id"]: "pass" for p in bundle.predicates}
        outcomes[spec["target"]] = spec["outcome"]
        verdict = resolve(bundle, outcomes)

        # A clean control: with nothing injected the same bundle must PERMIT, so
        # a SAFE_STATE below is attributable to the injection and not to a bundle
        # that refuses everything.
        clean = resolve(bundle, {p["gcir_id"]: "pass" for p in bundle.predicates})

        passed = verdict["decision"] == "SAFE_STATE" and clean["decision"] == "PERMIT"
        rows.append({
            "family": family,
            "source": "adversarial_attack_family" if attack and family in attack
                      else "asb_scenario_family",
            "target_predicate": spec["target"],
            "injected_outcome": spec["outcome"],
            "hazard": spec["hazard"],
            "why_safe_state": spec["why_safe_state"],
            "decision": verdict["decision"],
            "deciding_class": verdict["deciding_class"],
            "clean_control_decision": clean["decision"],
            "status": "SAFE_STATE" if passed else "UNEXPECTED",
            "passed": passed,
        })

    return {
        "scenario_count": len(rows),
        "families_from_published_artifact": bool(attack),
        "adversarial_attack_families": attack,
        "asb_scenario_families": asb,
        "passed": sum(1 for r in rows if r["passed"]),
        "failed": sum(1 for r in rows if not r["passed"]),
        "scenarios": rows,
        "claim_boundary": (
            "Decision-level injections against the compiled Case B predicate set. "
            "These establish that the compiled bundle refuses to permit under each "
            "hazard class the published enforcement artifact enumerates. They are "
            "NOT a run over the 284,807-event corpus, establish NO detection "
            "performance, and reproduce no figure from [15]."
        ),
    }
