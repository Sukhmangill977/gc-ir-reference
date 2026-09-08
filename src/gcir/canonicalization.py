"""RFC 8785 JSON Canonicalization Scheme (JCS) + SHA-256 payload hashing.

This module is deliberately dependency-free and contains no randomness, no clock
access, and no locale-sensitive operation.  It is the determinism anchor of the
whole artifact (manuscript Section VI-C).

Two things are implemented here:

1. ``canonicalize`` -- RFC 8785 serialization: UTF-8 output, object keys sorted by
   UTF-16 code unit, and ECMAScript ``Number::toString`` numeric formatting
   (RFC 8785 s3.2.2.3).

2. ``canonical_order`` (in ``gcir.compiler``) -- a *separate* concern the
   manuscript also requires: deterministic ordering of arrays whose order is not
   semantically meaningful.  RFC 8785 preserves array order, so the compiler must
   impose the order before serializing.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any

__all__ = [
    "canonicalize",
    "canonical_json_string",
    "sha256_hex",
    "hash_payload",
    "es6_number_to_string",
    "CanonicalizationError",
]


class CanonicalizationError(ValueError):
    """Raised when a value cannot be canonicalized under RFC 8785."""


# ---------------------------------------------------------------------------
# Number formatting: ECMAScript Number::toString, as required by RFC 8785 3.2.2.3
# ---------------------------------------------------------------------------

_EXP_RE = re.compile(r"^(-?)(\d)(?:\.(\d+))?e([+-]\d+)$")


def es6_number_to_string(value):
    """Serialize a JSON number exactly as ECMAScript ``Number::toString`` does.

    RFC 8785 requires this exact algorithm.  Python's ``repr`` already produces
    the shortest round-tripping decimal (the same property ECMAScript relies on),
    so the work here is converting Python's presentation of that shortest form
    into ECMAScript's presentation of it.
    """
    if isinstance(value, bool):  # bool subclasses int -- never a JSON number here
        raise CanonicalizationError("bool is not a JSON number")

    if isinstance(value, int):
        # RFC 8785 permits I-JSON integers, but agreement across implementations
        # is only guaranteed inside the IEEE-754 exactly-representable range.
        if abs(value) > 2**53 - 1:
            raise CanonicalizationError(
                "integer %d exceeds the IEEE-754 exactly-representable range; "
                "represent it as a string to keep canonicalization portable" % value
            )
        return str(value)

    if not isinstance(value, float):
        raise CanonicalizationError("not a number: %r" % (value,))

    if math.isnan(value) or math.isinf(value):
        raise CanonicalizationError("NaN and Infinity are not permitted in JSON")

    if value == 0.0:
        # ECMAScript renders both +0 and -0 as "0".
        return "0"

    if value == int(value) and abs(value) < 1e21:
        # ECMAScript prints integral doubles without a fractional part.
        return str(int(value))

    text = repr(value)  # shortest round-tripping decimal

    if "e" not in text and "E" not in text:
        return text

    match = _EXP_RE.match(text.replace("E", "e"))
    if match is None:  # pragma: no cover - repr always matches one of these forms
        raise CanonicalizationError("unhandled float presentation: %s" % text)

    sign, lead, frac, exp_text = match.groups()
    digits = lead + (frac or "")
    # ECMAScript Number::toString works from (s, k, n), where the value is
    # s * 10**(n - k) and s has k digits.  Python's repr gives the same shortest
    # digit string with the exponent expressed as n - 1.
    k = len(digits)
    n = int(exp_text) + 1

    if k <= n <= 21:
        return sign + digits + "0" * (n - k)
    if 0 < n <= 21:
        return sign + digits[:n] + "." + digits[n:]
    if -6 < n <= 0:
        return sign + "0." + "0" * (-n) + digits
    # Exponential notation.  ECMAScript always writes an explicit exponent sign.
    exponent = n - 1
    mantissa = digits if k == 1 else digits[0] + "." + digits[1:]
    return "%s%se%s%d" % (sign, mantissa, "+" if exponent >= 0 else "-", abs(exponent))


# ---------------------------------------------------------------------------
# String escaping: RFC 8785 3.2.2.2
# ---------------------------------------------------------------------------

_ESCAPES = {
    0x08: "\\b",
    0x09: "\\t",
    0x0A: "\\n",
    0x0C: "\\f",
    0x0D: "\\r",
    0x22: '\\"',
    0x5C: "\\\\",
}


def _escape_string(value):
    out = ['"']
    for char in value:
        code = ord(char)
        escape = _ESCAPES.get(code)
        if escape is not None:
            out.append(escape)
        elif code < 0x20:
            out.append("\\u%04x" % code)
        else:
            out.append(char)
    out.append('"')
    return "".join(out)


def _sort_key(key):
    """RFC 8785 sorts object keys by their UTF-16 code units, not code points."""
    return tuple(key.encode("utf-16-be"))


def _serialize(value, out, path):
    if value is None:
        out.append("null")
    elif value is True:
        out.append("true")
    elif value is False:
        out.append("false")
    elif isinstance(value, str):
        out.append(_escape_string(value))
    elif isinstance(value, (int, float)):
        out.append(es6_number_to_string(value))
    elif isinstance(value, (list, tuple)):
        out.append("[")
        for index, item in enumerate(value):
            if index:
                out.append(",")
            _serialize(item, out, "%s[%d]" % (path, index))
        out.append("]")
    elif isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                raise CanonicalizationError(
                    "non-string object key %r at %s" % (key, path)
                )
        out.append("{")
        for index, key in enumerate(sorted(value, key=_sort_key)):
            if index:
                out.append(",")
            out.append(_escape_string(key))
            out.append(":")
            _serialize(value[key], out, "%s.%s" % (path, key))
        out.append("}")
    else:
        raise CanonicalizationError(
            "value of type %s at %s is not JSON" % (type(value).__name__, path)
        )


def canonical_json_string(value):
    """Return the RFC 8785 canonical form of ``value`` as a ``str``."""
    out = []
    _serialize(value, out, "$")
    return "".join(out)


def canonicalize(value):
    """Return the RFC 8785 canonical form of ``value`` as UTF-8 bytes."""
    return canonical_json_string(value).encode("utf-8")


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def hash_payload(payload):
    """SHA-256 over the RFC 8785 canonical serialization of ``payload``."""
    return sha256_hex(canonicalize(payload))
