# Security

## This is a research artifact

Nothing in this repository is intended for production use, and nothing in it should
be deployed. It implements the compilation half of a governance method: it emits a
signed policy bundle. It is **not** a runtime enforcement engine, and it makes no
authorization decision about anything real.

## The committed keys are test fixtures

`keys/` contains Ed25519 **private** keys. They are committed deliberately, and this
is not a leak:

* They are derived from a fixed seed string recorded in `tools/build_cases.py`, so
  that a reviewer regenerating the case artifacts from a fresh clone obtains
  byte-identical public keys and signatures. That reproducibility is the entire
  reason they exist.
* Every key file and `keys/README.md` carry the banner
  **TEST ONLY / NOT FOR PRODUCTION**.
* They protect nothing. There is no system, account, or datum anywhere that any of
  them grants access to.
* `key.unauthorized_party` is a deliberate negative control: it exists only to sign
  fixtures that audit query Q6 and the adversarial suite must reject.

**Never reuse any of these keys for any purpose.** If you fork this repository for
real work, regenerate the keyring with fresh entropy
(`KeyRing.generate(key_ids)` with `seed_material=None`) and do not commit the
private material.

## What the artifact does and does not verify

It verifies Ed25519 signatures over RFC 8785 canonical bytes with domain separation,
so a signature over a bundle cannot be replayed as a signature over a lifecycle
record. It checks payload-hash binding, lifecycle-registry state and temporal
ordering.

It does **not** establish that any upstream evidence producer is honest, that a
trusted time source is trustworthy, or that a signed attestation reflects a
substantive human judgment. The manuscript states these bounds explicitly
(Section XII, "Epistemic bounding" and "Temporal evidence dependence") and every
Approved Control Specification in the cases carries a `warrant_boundary` field
saying what its predicate does not establish.

## Reporting a problem

For a defect in this artifact — a determinism failure, a constraint that does not
fire, a schema that admits something it should reject — open a GitHub issue with
the platform, Python version, and the failing command's output. A determinism
mismatch in particular is a genuine finding and is worth reporting.

For anything you believe is a real security issue rather than a research defect,
email sovran@lakhowal.com rather than opening a public issue.

## Supply chain

Dependencies are pinned in `requirements.lock` and the Docker base image is pinned
by digest. The compiler path imports no network client, no model library, and no
random-number generator; `tests/adversarial/test_no_inference.py` asserts that
statically over the shipped source and fails the build if it stops being true.
