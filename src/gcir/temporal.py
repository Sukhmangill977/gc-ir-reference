"""Timestamp handling with no locale or local-timezone dependence.

Every time value in this artifact is an RFC 3339 instant in UTC with a ``Z``
suffix.  Parsing is done here, once, so that no other module can accidentally
introduce a locale-sensitive or local-timezone-sensitive comparison -- one of the
nondeterminism sources Section VI-C requires to be closed.

Times are compared, never *generated*, inside anything that reaches a hashed
payload.
"""

from __future__ import annotations

import datetime as _dt
import re

from .models import ValidationError

_RFC3339_Z = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d{1,9}))?Z$"
)


def parse_time(value):
    """Parse an RFC 3339 UTC instant.  Rejects anything else.

    Offsets other than ``Z`` are rejected rather than normalized: an artifact that
    records ``2026-01-01T00:00:00+01:00`` in one place and the same instant as
    ``Z`` elsewhere would serialize to two different canonical strings, and the
    manuscript forbids local-time dependence in the payload.
    """
    if not isinstance(value, str):
        raise ValidationError(
            "timestamp %r is not a string" % (value,), code="TIMESTAMP_INVALID"
        )
    match = _RFC3339_Z.match(value)
    if match is None:
        raise ValidationError(
            "timestamp %r is not an RFC 3339 UTC instant of the form "
            "YYYY-MM-DDThh:mm:ssZ" % value,
            code="TIMESTAMP_INVALID",
        )
    year, month, day, hour, minute, second, fraction = match.groups()
    micro = int((fraction or "0").ljust(6, "0")[:6])
    try:
        return _dt.datetime(
            int(year),
            int(month),
            int(day),
            int(hour),
            int(minute),
            int(second),
            micro,
            tzinfo=_dt.timezone.utc,
        )
    except ValueError as exc:
        raise ValidationError(
            "timestamp %r is not a valid instant: %s" % (value, exc),
            code="TIMESTAMP_INVALID",
        )


def is_within(instant, start, end):
    """``start <= instant <= end``; ``end`` may be ``None`` for an open interval."""
    point = parse_time(instant)
    if start is not None and point < parse_time(start):
        return False
    if end is not None and point > parse_time(end):
        return False
    return True


def commit_before_actuate(receipt):
    """Section VIII: ``authorization_time <= evidence_commit_time < actuation_time``.

    Returns ``(ok, reasons)``.  The second inequality is strict: the receipt must
    be committed *before* actuation, not simultaneously with it.
    """
    reasons = []
    authorization = parse_time(receipt["authorization_time"])
    commit = parse_time(receipt["evidence_commit_time"])
    if authorization > commit:
        reasons.append(
            "authorization_time %s is later than evidence_commit_time %s"
            % (receipt["authorization_time"], receipt["evidence_commit_time"])
        )
    actuation = receipt.get("actuation_time")
    if actuation is not None:
        if commit >= parse_time(actuation):
            reasons.append(
                "evidence_commit_time %s is not strictly before actuation_time %s"
                % (receipt["evidence_commit_time"], actuation)
            )
    return (not reasons), reasons
