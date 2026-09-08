# Research signing keys — TEST ONLY / NOT FOR PRODUCTION

**Every private key in this directory is a research fixture. None of them protects
anything. Do not reuse any of them for any purpose.**

The keys are Ed25519 and are derived deterministically from a fixed seed string
recorded in `tools/build_cases.py` (`KEY_SEED`) and in
`docs/FIXTURE_PROVENANCE.md` (FP-030), so that a reviewer regenerating the case
artifacts from a fresh clone obtains byte-identical public keys and signatures.
That reproducibility is the reason the private keys are committed; it is also the
reason they must never be used outside this artifact.

| key id | role |
|---|---|
| `key.assessor` | signs the approved assessment (M, S, O, R, A) |
| `key.governance_forum_a` | Case A governance forum: catalog, C\* profile, judgment record, dispositions, ACS set, invariant register, compiled bundle |
| `key.governance_forum_b` | the same, for Case B |
| `key.lifecycle_authority_a` / `_b` | the only keys with lifecycle-registry signing authority |
| `key.runtime_authority_a` / `_b` | signs decision receipts |
| `key.unauthorized_party` | **negative control**: used only to sign fixtures that audit query Q6 and the adversarial suite must reject |

Regenerate with:

    python -m tools.build_cases
