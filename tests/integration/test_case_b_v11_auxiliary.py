"""Auxiliary checks A1-A4 against Case B v1.1's real actors and authority
matrix (runbook item 6): implement genuine fixtures where the mechanism
actually applies to this case, and report NOT_APPLICABLE -- never as a silent
PASS substitute -- where Case B's own design has no such mechanism.

Applicability determined from cases/case_b_v1_1's actual system_profile and
authority_matrix, not assumed:

  A1 actor-scope revocation: APPLICABLE. Case B's authority matrix admits
     release_payment/evaluate_transaction for named actors
     (transaction_agent, payment_operations_analyst, sanctions_officer); an
     actor's scope over release_payment can be revoked mid-session.
  A2 SafetyEvent correlation: NOT_APPLICABLE. Case B declares no
     safety_layers (no physical actuation) -- there is no independent runtime
     safety layer for a SafetyEvent to originate from.
  A3 delegation containment: NOT_APPLICABLE. Case B's authority matrix has no
     DELEGATE transition; nothing in this case issues a child permit.
  A4 HumanResponse coverage: NOT_APPLICABLE. A4 covers advisory permits whose
     governing predicate declares response_policy (Section VII-I); Case B's
     human_attestation predicates (ACS-B01-03, ACS-B02-02) are mandatory
     approval gates via concurrence_policy, not advisory outputs, and declare
     no response_policy.
"""

from __future__ import annotations

from gcir import auxiliary_checks


def test_a1_is_applicable_and_detects_revoked_actor_scope(case_b_v1_1):
    """A real fixture: sanctions_officer's scope over release_payment is
    revoked, then an actuation is attempted under it anyway."""
    _, inputs, _ = case_b_v1_1
    release_tuple = {
        "subject": "transaction_agent", "action": "release_payment",
        "resource": "payment_instruction", "destination": "payment_rail",
    }
    assert any(
        row["subject"] == release_tuple["subject"] and row["action"] == release_tuple["action"]
        for row in inputs.assessment.system_profile["authority_matrix"]
    ), "release_payment must be a real authority-matrix row for this fixture to be genuine"

    actuations = [{
        "actor_id": "sanctions_officer.k_diallo",
        "action_tuple": release_tuple,
        "authorization_time": "2026-03-10T14:00:00Z",
    }]
    revocations = [{
        "record_type": "ActorScopeRevocation",
        "actor_id": "sanctions_officer.k_diallo",
        "scope": [release_tuple],
        "effective_time": "2026-03-10T13:00:00Z",
        "authority": "compliance.sanctions_desk",
    }]
    passed, issues = auxiliary_checks.a1_actor_scope_revocation_validity(actuations, revocations)
    assert passed is False
    assert issues


def test_a1_clean_actuation_before_revocation_passes(case_b_v1_1):
    release_tuple = {
        "subject": "transaction_agent", "action": "release_payment",
        "resource": "payment_instruction", "destination": "payment_rail",
    }
    actuations = [{
        "actor_id": "sanctions_officer.k_diallo", "action_tuple": release_tuple,
        "authorization_time": "2026-03-10T10:00:00Z",
    }]
    revocations = [{
        "record_type": "ActorScopeRevocation", "actor_id": "sanctions_officer.k_diallo",
        "scope": [release_tuple], "effective_time": "2026-03-10T13:00:00Z",
        "authority": "compliance.sanctions_desk",
    }]
    passed, issues = auxiliary_checks.a1_actor_scope_revocation_validity(actuations, revocations)
    assert passed is True


def test_a2_a3_a4_are_genuinely_not_applicable_to_case_b(case_b_v1_1):
    """Confirmed from Case B v1.1's own declared system_profile and
    predicates -- not assumed."""
    _, inputs, result = case_b_v1_1
    system_profile = inputs.assessment.system_profile

    assert "safety_layers" not in system_profile or not system_profile["safety_layers"], (
        "A2 is NOT_APPLICABLE only if Case B truly declares no safety layer"
    )
    actions = {row["action"] for row in system_profile["authority_matrix"]}
    assert "delegate" not in actions, "A3 is NOT_APPLICABLE only if Case B truly has no DELEGATE transition"
    assert not any(p.get("response_policy") for p in result.bundle.predicates), (
        "A4 is NOT_APPLICABLE only if no Case B predicate declares response_policy"
    )

    results = auxiliary_checks.run_all_auxiliary_checks({})
    for name in ("A2", "A3", "A4"):
        passed, details = results[name]
        assert passed is True
        assert "NOT_APPLICABLE" in details[0]
