"""Bundle lifecycle registry and ``ValidAt`` (manuscript Sections VI-F, VIII).

    reg_entry = (bundle_hash, action in {retire, supersede, revoke},
                 effective_time, authority, successor_hash?, signature)

The payload is immutable after signing; retirement, supersession and emergency
revocation are *separately signed registry records*, never payload mutation.

    ValidAt(t, b, REG) = SignatureValid(t)
                       and t.bundle_hash = H(b.payload)
                       and b.effective_from <= t.decision_time
                       and not Retired(REG, H(b.payload), t.decision_time)

``Retired(REG, h, tau)`` holds iff REG contains a *validly signed* retirement,
supersession or revocation record for ``h`` with ``effective_time <= tau``.

A historical receipt is not drift merely because its bundle is now retired.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .canonicalization import hash_payload
from .models import LIFECYCLE_ACTIONS, SignatureError, ValidationError
from .signatures import strip_envelope
from .temporal import parse_time


class LifecycleRegistry:
    """A signed append-only registry.  Never mutates a bundle payload."""

    def __init__(self, document, keyring=None, authorized_key_ids=None):
        self._doc = document
        self._keyring = keyring
        self._authorized = set(authorized_key_ids or [])
        self._entries = list(document.get("entries", []))
        for entry in self._entries:
            if entry["action"] not in LIFECYCLE_ACTIONS:
                raise ValidationError(
                    "lifecycle action %r is outside {retire, supersede, revoke}"
                    % entry["action"],
                    code="LIFECYCLE_ACTION_UNKNOWN",
                )
            if entry["action"] == "supersede" and not entry.get("successor_hash"):
                raise ValidationError(
                    "supersede record for %s carries no successor_hash"
                    % entry["bundle_hash"],
                    code="LIFECYCLE_SUCCESSOR_MISSING",
                )

    @property
    def registry_id(self):
        return self._doc["registry_id"]

    @property
    def entries(self):
        return list(self._entries)

    @property
    def document(self):
        return self._doc

    # -- signing authority --------------------------------------------------

    def entry_signature_valid(self, entry):
        """True iff the record is signed by a key with valid signing authority.

        Query 6 of Section VIII tests exactly this: "lifecycle-registry records
        lacking a valid signing authority".
        """
        if self._keyring is None:
            return False
        envelope = entry.get("signature")
        if not envelope:
            return False
        key_id = envelope.get("key_id")
        if self._authorized and key_id not in self._authorized:
            return False
        try:
            self._keyring.verify(strip_envelope(entry), envelope, domain="lifecycle")
        except SignatureError:
            return False
        return True

    def invalid_authority_entries(self):
        return [
            {
                "bundle_hash": entry["bundle_hash"],
                "action": entry["action"],
                "effective_time": entry["effective_time"],
                "authority": entry.get("authority"),
                "key_id": (entry.get("signature") or {}).get("key_id"),
            }
            for entry in self._entries
            if not self.entry_signature_valid(entry)
        ]

    # -- lifecycle state ----------------------------------------------------

    def retirement_records(self, bundle_hash, at_time):
        """Validly signed retire/supersede/revoke records effective at or before
        ``at_time``."""
        boundary = parse_time(at_time)
        found = []
        for entry in self._entries:
            if entry["bundle_hash"] != bundle_hash:
                continue
            if parse_time(entry["effective_time"]) > boundary:
                continue
            if not self.entry_signature_valid(entry):
                # An invalidly signed record does not retire a bundle; it is a
                # Query-6 finding instead.
                continue
            found.append(entry)
        return sorted(found, key=lambda e: (e["effective_time"], e["action"]))

    def is_retired(self, bundle_hash, at_time):
        return bool(self.retirement_records(bundle_hash, at_time))

    def successor_of(self, bundle_hash):
        for entry in self._entries:
            if entry["bundle_hash"] == bundle_hash and entry["action"] == "supersede":
                return entry.get("successor_hash")
        return None


def valid_at(receipt, bundle, registry, keyring=None):
    """``ValidAt(t, b, REG)`` -- returns ``(bool, reasons)``.

    ``reasons`` names every failing conjunct, so a test can assert *which* clause
    rejected a scenario rather than only that it did.
    """
    reasons = []

    # 1. SignatureValid(t)
    signature_ok = False
    if keyring is not None and receipt.get("signature"):
        try:
            keyring.verify(strip_envelope(receipt), receipt["signature"], domain="receipt")
            signature_ok = True
        except SignatureError as exc:
            reasons.append("receipt signature invalid: %s" % exc)
    else:
        reasons.append("receipt signature absent or no keyring supplied")
    if signature_ok:
        pass

    # 2. t.bundle_hash == H(b.payload)
    actual = hash_payload(bundle.payload) if hasattr(bundle, "payload") else hash_payload(bundle)
    if receipt.get("bundle_hash") != actual:
        reasons.append(
            "receipt bundle_hash %s does not match H(b.payload) %s"
            % (receipt.get("bundle_hash"), actual)
        )

    # 3. b.effective_from <= t.decision_time
    payload = bundle.payload if hasattr(bundle, "payload") else bundle
    effective_from = payload["validity"]["effective_from"]
    decision_time = receipt["decision_time"]
    if parse_time(effective_from) > parse_time(decision_time):
        reasons.append(
            "bundle effective_from %s is later than decision_time %s"
            % (effective_from, decision_time)
        )

    # 4. not Retired(REG, H(b.payload), t.decision_time)
    if registry is not None and registry.is_retired(actual, decision_time):
        records = registry.retirement_records(actual, decision_time)
        reasons.append(
            "bundle retired by %s effective %s"
            % (records[0]["action"], records[0]["effective_time"])
        )

    return (not reasons), reasons


def payload_is_unmutated(bundle, expected_hash):
    """An in-place payload edit changes the hash and breaks every citing receipt."""
    payload = bundle.payload if hasattr(bundle, "payload") else bundle
    return hash_payload(payload) == expected_hash
