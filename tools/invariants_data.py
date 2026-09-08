"""The approved invariant register INV (manuscript Section VI-B).

    "A compiler-invariant predicate cites an approved system requirement such as
     INV-VERSION (per-action version-binding check), INV-EVIDENCE-COMMIT (receipt
     committed after authorization and before actuation), or
     INV-AUTHORITY-CLOSURE (action tuple within the approved matrix).  Compiler
     invariants are not orphan controls; they are separately authorized
     requirements included in M or S and recorded in the approved invariant
     register INV."

The register is parameterised by case because each invariant is bound to a
specific ``M.version_binding`` and to a specific authorized action path.
"""


def build_invariant_register(register_id, binding, approver, approval_time,
                             effective_from, action_tuple, parameter_schema_ref,
                             action_parameters, fingerprint):
    """Return the three manuscript-named invariants, bound to one case."""
    common = {
        "approved_by": approver,
        "approval_time": approval_time,
        "effective_from": effective_from,
        "version_binding_ref": binding,
        "subject": action_tuple["subject"],
        "action": action_tuple["action"],
        "resource": action_tuple["resource"],
        "destination": action_tuple["destination"],
        "action_parameters": dict(action_parameters),
        "parameter_schema_ref": parameter_schema_ref,
    }

    invariants = [
        dict(
            common,
            invariant_id="INV-VERSION",
            gcir_id="GCIR-INV-VERSION",
            title="Per-action version-binding check",
            authorizing_requirement={
                "source": "M",
                "reference": "M.version_binding and M.triggers -- the assessment covers exactly one configuration; an action taken under any other configuration is unauthorized by construction.",
            },
            obligation_refs=[],
            context_conditions=[
                {
                    "attribute": "runtime_fingerprint",
                    "operator": "==",
                    "value": fingerprint,
                    "value_from": "M.version_binding",
                    "unit": None,
                    "on_unknown": "fail",
                    "required": True,
                    "evidence_producer": "deployment_attestation_service_v1",
                    "evidence_schema_ref": "ES-VERSION-FINGERPRINT",
                    "threshold_contract_ref": None,
                    "temporal_window": None,
                }
            ],
            evidence_producer="deployment_attestation_service_v1",
            evidence_schema_ref="ES-VERSION-FINGERPRINT",
            evaluation_basis="deterministic_lookup",
            escalation={"route": "technology_change_management", "sla_hours": 1},
            evidence_requirements=[
                "model_version", "prompt_version", "dataset_version",
                "policy_version", "fingerprint", "artifact_signature",
            ],
            evidence_semantics="A signed deployment attestation reporting the configuration actually loaded at authorization time.",
            decision_semantics="PERMIT requires the runtime fingerprint to equal M.version_binding.fingerprint. Indeterminate or absent evidence fails.",
            warrant_boundary="Establishes that the running configuration is the assessed configuration. It does not establish that the assessed configuration is safe. This is the per-action form of the version-drift argument: no action is authorized under a configuration the assessment never covered.",
        ),
        dict(
            common,
            invariant_id="INV-EVIDENCE-COMMIT",
            gcir_id="GCIR-INV-EVIDENCE-COMMIT",
            title="Receipt committed after authorization and before actuation",
            authorizing_requirement={
                "source": "S",
                "reference": "S.architecture -- the consuming enforcement pipeline issues a permit, commits the trace record, and only then releases the interlock. The ordering is a system requirement, not a per-risk treatment choice.",
            },
            obligation_refs=[],
            context_conditions=[
                {
                    "attribute": "receipt_committed_between_authorization_and_actuation",
                    "operator": "==",
                    "value": True,
                    "unit": None,
                    "on_unknown": "fail",
                    "required": True,
                    "evidence_producer": "evidence_chain_service_v2",
                    "evidence_schema_ref": "ES-RECEIPT-CHAIN",
                    "threshold_contract_ref": None,
                    "temporal_window": None,
                }
            ],
            evidence_producer="evidence_chain_service_v2",
            evidence_schema_ref="ES-RECEIPT-CHAIN",
            evaluation_basis="structural_check",
            escalation={"route": "compliance_records_desk", "sla_hours": 1},
            evidence_requirements=[
                "receipt_id", "authorization_time", "evidence_commit_time",
                "chain_prev_hash",
            ],
            evidence_semantics="A signed evidence-chain artifact carrying the authorization, commit and actuation instants for this decision.",
            decision_semantics="PERMIT requires authorization_time <= evidence_commit_time < actuation_time, with the receipt chained to its predecessor.",
            warrant_boundary="Establishes the temporal ordering and chaining of the evidence record. It does not establish the truth of the receipt's content, nor that the trusted time source is honest.",
        ),
        dict(
            common,
            invariant_id="INV-AUTHORITY-CLOSURE",
            gcir_id="GCIR-INV-AUTHORITY-CLOSURE",
            title="Action tuple within the approved authority matrix",
            authorizing_requirement={
                "source": "S",
                "reference": "S.authority_matrix -- the accountable executive's signature over what the system may cause. An action outside the matrix is unauthorized irrespective of any risk treatment.",
            },
            obligation_refs=[],
            context_conditions=[
                {
                    "attribute": "action_tuple_within_approved_matrix",
                    "operator": "==",
                    "value": True,
                    "unit": None,
                    "on_unknown": "fail",
                    "required": True,
                    "evidence_producer": "authority_matrix_service_v1",
                    "evidence_schema_ref": "ES-AUTHORITY-CLOSURE",
                    "threshold_contract_ref": None,
                    "temporal_window": None,
                }
            ],
            evidence_producer="authority_matrix_service_v1",
            evidence_schema_ref="ES-AUTHORITY-CLOSURE",
            evaluation_basis="deterministic_lookup",
            escalation={"route": "governance_forum_urgent", "sla_hours": 1},
            evidence_requirements=[
                "subject", "action", "resource", "destination",
                "matrix_version", "artifact_signature",
            ],
            evidence_semantics="A signed lookup artifact reporting whether the proposed action tuple and its bound parameters are present in the approved authority matrix at the stated matrix version.",
            decision_semantics="PERMIT requires the proposed tuple and parameters to resolve exactly to an approved matrix row. Indeterminate or absent evidence fails.",
            warrant_boundary="Establishes closure of the proposed action against the approved matrix. It does not establish that the matrix itself is correctly scoped -- that is a governance judgment recorded in S.",
        ),
    ]

    return {
        "register_id": register_id,
        "version": "1.0",
        "version_binding_ref": binding,
        "invariants": invariants,
    }
