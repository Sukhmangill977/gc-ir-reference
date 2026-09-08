"""Ed25519 detached signatures over RFC 8785 canonical payloads.

Two rules from the manuscript govern this module:

* Signed governance artifacts (M, S, O, R, A, K, D, Delta, INV, J, and every
  lifecycle-registry record) must have verifiable signatures before Phi will
  compile (Section VI-A, step 1).
* The bundle's signature *envelope* carries signing time and key identifier and
  therefore lives outside the hashed payload; ``TD`` is a property of the
  canonical payload hash, not of envelope bytes (Section VI-C).

The keys generated here are RESEARCH FIXTURES.  ``keys/README.md`` and every
generated key file are marked TEST ONLY / NOT FOR PRODUCTION.
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from .canonicalization import canonicalize, hash_payload
from .models import SignatureError

TEST_KEY_BANNER = "TEST ONLY / NOT FOR PRODUCTION -- research fixture key"

#: Signature is computed over the canonical bytes of the payload with this
#: domain-separation prefix, so a signature over a bundle can never be replayed
#: as a signature over a lifecycle record.
DOMAIN_PREFIXES = {
    "assessment": b"gcir-v1/assessment\x00",
    "catalog": b"gcir-v1/catalog\x00",
    "judgment_record": b"gcir-v1/judgment\x00",
    "dispositions": b"gcir-v1/dispositions\x00",
    "acs": b"gcir-v1/acs\x00",
    "invariants": b"gcir-v1/invariants\x00",
    "bundle": b"gcir-v1/bundle\x00",
    "lifecycle": b"gcir-v1/lifecycle\x00",
    "receipt": b"gcir-v1/receipt\x00",
    "cstar_profile": b"gcir-v1/cstar\x00",
}


class KeyRing:
    """A named set of Ed25519 research keys, loaded from or written to disk."""

    def __init__(self, keys=None):
        self._private = {}
        self._public = {}
        for key_id, key in (keys or {}).items():
            self.add(key_id, key)

    # -- construction -------------------------------------------------------

    def add(self, key_id, private_key):
        self._private[key_id] = private_key
        self._public[key_id] = private_key.public_key()

    def add_public(self, key_id, public_key):
        self._public[key_id] = public_key

    @classmethod
    def generate(cls, key_ids, seed_material=None):
        """Generate deterministic research keys.

        ``seed_material`` makes fixture keys reproducible across a fresh clone so
        that a reviewer regenerating the case artifacts obtains the same public
        keys.  It never touches the hashed payload.
        """
        ring = cls()
        for key_id in key_ids:
            if seed_material is None:
                private = Ed25519PrivateKey.generate()
            else:
                import hashlib

                seed = hashlib.sha256(
                    ("%s|%s" % (seed_material, key_id)).encode("utf-8")
                ).digest()
                private = Ed25519PrivateKey.from_private_bytes(seed)
            ring.add(key_id, private)
        return ring

    # -- persistence --------------------------------------------------------

    def write(self, directory):
        os.makedirs(directory, exist_ok=True)
        index = {}
        for key_id, private in sorted(self._private.items()):
            raw = private.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
            path = os.path.join(directory, "%s.ed25519.json" % key_id)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "key_id": key_id,
                        "algorithm": "Ed25519",
                        "warning": TEST_KEY_BANNER,
                        "private_key_b64": base64.b64encode(raw).decode("ascii"),
                        "public_key_b64": self.public_key_b64(key_id),
                    },
                    handle,
                    indent=2,
                    sort_keys=True,
                )
                handle.write("\n")
            index[key_id] = self.public_key_b64(key_id)
        with open(os.path.join(directory, "public_keys.json"), "w", encoding="utf-8") as handle:
            json.dump(
                {"warning": TEST_KEY_BANNER, "keys": index},
                handle,
                indent=2,
                sort_keys=True,
            )
            handle.write("\n")
        return index

    @classmethod
    def load(cls, directory):
        ring = cls()
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".ed25519.json"):
                continue
            with open(os.path.join(directory, name), encoding="utf-8") as handle:
                blob = json.load(handle)
            raw = base64.b64decode(blob["private_key_b64"])
            ring.add(blob["key_id"], Ed25519PrivateKey.from_private_bytes(raw))
        return ring

    @classmethod
    def load_public(cls, path):
        ring = cls()
        with open(path, encoding="utf-8") as handle:
            blob = json.load(handle)
        for key_id, b64 in blob["keys"].items():
            ring.add_public(
                key_id, Ed25519PublicKey.from_public_bytes(base64.b64decode(b64))
            )
        return ring

    # -- accessors ----------------------------------------------------------

    def public_key_b64(self, key_id):
        raw = self._public[key_id].public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return base64.b64encode(raw).decode("ascii")

    def key_ids(self):
        return sorted(self._public)

    def has(self, key_id):
        return key_id in self._public

    # -- signing / verification --------------------------------------------

    def sign(self, payload, key_id, domain, signing_time=None, extra=None):
        """Produce a detached signature envelope over ``payload``.

        The envelope holds the payload hash, the key identifier and (optionally)
        the signing time.  None of that is part of the hashed payload.
        """
        if domain not in DOMAIN_PREFIXES:
            raise SignatureError("unknown signature domain %r" % domain)
        if key_id not in self._private:
            raise SignatureError("no private key %r in ring" % key_id)
        message = DOMAIN_PREFIXES[domain] + canonicalize(payload)
        signature = self._private[key_id].sign(message)
        envelope = {
            "algorithm": "Ed25519",
            "domain": domain,
            "key_id": key_id,
            "payload_hash": hash_payload(payload),
            "signature_b64": base64.b64encode(signature).decode("ascii"),
        }
        if signing_time is not None:
            envelope["signing_time"] = signing_time
        if extra:
            envelope.update(extra)
        return envelope

    def verify(self, payload, envelope, domain=None, expected_key_id=None):
        """Verify a detached envelope, raising ``SignatureError`` on failure."""
        if not isinstance(envelope, dict):
            raise SignatureError("missing signature envelope")
        domain = domain or envelope.get("domain")
        if domain not in DOMAIN_PREFIXES:
            raise SignatureError("unknown signature domain %r" % domain)
        if envelope.get("domain") != domain:
            raise SignatureError(
                "signature domain mismatch: envelope=%r expected=%r"
                % (envelope.get("domain"), domain)
            )
        key_id = envelope.get("key_id")
        if expected_key_id is not None and key_id != expected_key_id:
            raise SignatureError(
                "signature key %r is not the expected authority %r"
                % (key_id, expected_key_id)
            )
        if key_id not in self._public:
            raise SignatureError("unknown signing key %r" % key_id)
        actual_hash = hash_payload(payload)
        if envelope.get("payload_hash") != actual_hash:
            raise SignatureError(
                "payload hash mismatch: envelope=%s actual=%s"
                % (envelope.get("payload_hash"), actual_hash)
            )
        message = DOMAIN_PREFIXES[domain] + canonicalize(payload)
        try:
            self._public[key_id].verify(
                base64.b64decode(envelope["signature_b64"]), message
            )
        except (InvalidSignature, KeyError, ValueError) as exc:
            raise SignatureError("Ed25519 verification failed: %s" % exc)
        return True


def strip_envelope(document):
    """Return ``document`` without its ``signature`` field.

    Signed artifacts are stored as ``{..., "signature": {...}}``; the signature is
    computed over the document *minus* that field, so verification is exact.
    """
    return {k: v for k, v in document.items() if k != "signature"}
