"""Observation diagnostics (Paper 2 v1.2 spec section 13).

    python -m experiments.observation_diagnostics_v12 --phase development

Two bounded software-simulation diagnostics, kept as supporting evidence
only -- explicitly NOT deployment validation. Both are deterministic,
fixed-scenario simulations directly instantiating
``gcir.contract_v12.OBSERVATION_SCOPES`` (spec 1K's Omega_r = (beta_r,
kappa_r, q_r)): the point of each is that an evaluator whose declared
observation scope does not cover the relevant history/cross-request/
evidence dimension cannot detect a violation that only manifests there,
while an evaluator whose scope does cover it can.

Diagnostic A: the SAME current grant request, evaluated against two
DIFFERENT prior-consumption histories, by an evaluator that lacks shared
consumption state (q_r = "event" only) -- it cannot distinguish the two
cases, even though one is compliant and the other is not.

Diagnostic B: authorized/requested amount 1,200 vs. a realized amount of
120,000 -- an observer whose beta_r omits the realized amount reports
compliant regardless; one whose beta_r includes it correctly detects the
breach.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src"))

from experiments.common import environment  # noqa: E402

APPROVED_CONSUMPTION_LIMIT = 10000


def _event_scoped_evaluator(current_request):
    """q_r = 'event': sees only the current request, no consumption history."""
    return {"decision": "PERMIT", "basis": "current_request_amount within per-request bound", "observed": {"current_request": current_request}}


def _bounded_history_scoped_evaluator(current_request, prior_consumption_total):
    """q_r = 'bounded-history': observes cumulative consumption over the
    declared bounded-history window, per Omega_r's beta_r requirement."""
    cumulative = prior_consumption_total + current_request
    compliant = cumulative <= APPROVED_CONSUMPTION_LIMIT
    return {
        "decision": "PERMIT" if compliant else "DENY",
        "basis": "cumulative consumption %s approved limit %s" % (cumulative, APPROVED_CONSUMPTION_LIMIT),
        "observed": {"current_request": current_request, "prior_consumption_total": prior_consumption_total, "cumulative": cumulative},
    }


def diagnostic_a():
    current_request = 3000
    history_compliant = 2000     # cumulative 5000, well within 10000
    history_noncompliant = 9500  # cumulative 12500, breaches 10000

    event_scoped_compliant = _event_scoped_evaluator(current_request)
    event_scoped_noncompliant = _event_scoped_evaluator(current_request)  # identical input either way -- that IS the gap
    history_scoped_compliant = _bounded_history_scoped_evaluator(current_request, history_compliant)
    history_scoped_noncompliant = _bounded_history_scoped_evaluator(current_request, history_noncompliant)

    event_scope_blind = event_scoped_compliant == event_scoped_noncompliant
    history_scope_distinguishes = history_scoped_compliant["decision"] != history_scoped_noncompliant["decision"]

    return {
        "diagnostic": "A",
        "description": "same current grant request, different prior consumption history, evaluator lacks shared consumption state",
        "current_request": current_request,
        "prior_consumption_histories": {"compliant_scenario": history_compliant, "noncompliant_scenario": history_noncompliant},
        "event_scoped_evaluator": {
            "q_r": "event",
            "decision_under_compliant_history": event_scoped_compliant["decision"],
            "decision_under_noncompliant_history": event_scoped_noncompliant["decision"],
            "cannot_distinguish_the_two_histories": event_scope_blind,
        },
        "bounded_history_scoped_evaluator": {
            "q_r": "bounded-history",
            "decision_under_compliant_history": history_scoped_compliant["decision"],
            "decision_under_noncompliant_history": history_scoped_noncompliant["decision"],
            "correctly_distinguishes_the_two_histories": history_scope_distinguishes,
        },
        "finding": (
            "An evaluator declaring q_r='event' (no shared consumption state) issues "
            "the identical PERMIT for the same current request regardless of prior "
            "consumption -- it structurally cannot observe the breach. An evaluator "
            "declaring the required q_r='bounded-history' scope (Omega_r, spec 1K) "
            "correctly distinguishes PERMIT from DENY across the two histories."
        ),
        "passed": event_scope_blind and history_scope_distinguishes,
        "claim_boundary": "Bounded software-simulation diagnostic. Not deployment validation.",
    }


def _observer(beta_r, requested, authorized, realized):
    evidence = {"requested": requested, "authorized": authorized}
    if "realized_amount" in beta_r:
        evidence["realized_amount"] = realized
        compliant = realized <= authorized
    else:
        compliant = requested <= authorized  # never looks at realized at all
    return {"beta_r": list(beta_r), "evidence_observed": evidence, "decision": "COMPLIANT" if compliant else "BREACH_DETECTED"}


def diagnostic_b():
    requested = 1200
    authorized = 1200
    realized = 120000  # two orders of magnitude beyond what was requested/authorized

    omits_realized = _observer(beta_r=["requested", "authorized"], requested=requested, authorized=authorized, realized=realized)
    includes_realized = _observer(beta_r=["requested", "authorized", "realized_amount"], requested=requested, authorized=authorized, realized=realized)

    return {
        "diagnostic": "B",
        "description": "authorized/requested 1,200; realized 120,000; observer omits realized amount",
        "requested": requested, "authorized": authorized, "realized": realized,
        "observer_omitting_realized_amount": omits_realized,
        "observer_including_realized_amount": includes_realized,
        "finding": (
            "An observer whose beta_r omits realized_amount reports COMPLIANT "
            "purely from requested<=authorized, never observing that the realized "
            "amount was 100x the authorized bound. An observer whose beta_r "
            "includes realized_amount (Omega_r's required binding information, "
            "spec 1K) correctly reports BREACH_DETECTED."
        ),
        "passed": omits_realized["decision"] == "COMPLIANT" and includes_realized["decision"] == "BREACH_DETECTED",
        "claim_boundary": "Bounded software-simulation diagnostic. Not deployment validation.",
    }


def run_all():
    a = diagnostic_a()
    b = diagnostic_b()
    return {"diagnostic_a": a, "diagnostic_b": b, "both_passed": a["passed"] and b["passed"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", default="development")
    parser.add_argument("--output", default=None)
    args = parser.parse_args(argv)

    report = run_all()
    document = {
        "result_name": "observation_diagnostics_v12", "phase": args.phase,
        "phase_note": "DEVELOPMENT result; not reportable." if args.phase == "development" else args.phase,
        "environment": environment(), "result": report,
    }
    out_dir = args.output or os.path.join(REPO_ROOT, "results", "development_v12")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "observation_diagnostics.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(document, handle, indent=2, sort_keys=True, ensure_ascii=False)
        handle.write("\n")

    print("diagnostic_a passed=%s  diagnostic_b passed=%s" % (report["diagnostic_a"]["passed"], report["diagnostic_b"]["passed"]))
    print("-> %s" % out_path)
    return 0 if report["both_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
