"""RFC 8785 (JSON Canonicalization Scheme) conformance tests.

Vectors are taken from RFC 8785 itself:
  * section 3.2.3   -- the worked serialization example (UTF-16 key ordering)
  * section 3.2.2.2 -- literal escaping rules
  * appendix B      -- ECMAScript ``Number::toString`` values
"""

import hashlib
import json

import pytest

from gcir.canonicalization import (
    CanonicalizationError,
    canonical_json_string,
    canonicalize,
    es6_number_to_string,
    hash_payload,
)


# ---------------------------------------------------------------- key ordering

def test_rfc8785_section_323_worked_example_key_order():
    """RFC 8785 s3.2.3: keys sort by UTF-16 code unit, not by code point.

    U+1F600 GRINNING FACE encodes as the surrogate pair D83D DE00, so it must
    sort *before* U+FB33 even though its code point is larger.  A naive
    code-point sort puts it last and fails this test.
    """
    value = {
        "€": "Euro Sign",
        "\r": "Carriage Return",
        "דּ": "Hebrew Letter Dalet With Dagesh",
        "1": "One",
        "\U0001f600": "Emoji: Grinning Face",
        "\u0080": "Control",
        "ö": "Latin Small Letter O With Diaeresis",
    }
    out = canonical_json_string(value)
    assert list(json.loads(out).keys()) == [
        "\r",
        "1",
        "\u0080",
        "ö",
        "€",
        "\U0001f600",
        "דּ",
    ]
    # and the emoji really does precede the Hebrew letter in the byte stream
    assert out.index("Emoji") < out.index("Hebrew")


def test_ascii_keys_sort_by_code_unit():
    assert canonical_json_string({"b": 1, "a": 2, "A": 3, "0": 4}) == (
        '{"0":4,"A":3,"a":2,"b":1}'
    )


def test_nested_objects_are_sorted_recursively():
    value = {"z": {"b": 1, "a": 2}, "a": [{"y": 1, "x": 2}]}
    assert canonical_json_string(value) == '{"a":[{"x":2,"y":1}],"z":{"a":2,"b":1}}'


def test_array_order_is_preserved_by_jcs():
    """RFC 8785 never reorders arrays -- semantic ordering is the caller's job."""
    assert canonical_json_string([3, 1, 2]) == "[3,1,2]"


# ------------------------------------------------------------------- escaping

@pytest.mark.parametrize(
    "raw,expected",
    [
        (chr(0x08), '"\\b"'),
        (chr(0x09), '"\\t"'),
        (chr(0x0A), '"\\n"'),
        (chr(0x0C), '"\\f"'),
        (chr(0x0D), '"\\r"'),
        (chr(0x22), '"\\""'),
        (chr(0x5C), '"\\\\"'),
        (chr(0x00), '"\\u0000"'),
        (chr(0x07), '"\\u0007"'),
        (chr(0x1F), '"\\u001f"'),
        # Not escaped: everything at or above U+0020 except quote and backslash
        (chr(0x20), '" "'),
        ("/", '"/"'),
        ("", '""'),
        ("\u00e9", '"\u00e9"'),
        # C1 controls are >= U+0080 and are therefore emitted literally
        (chr(0x80), '"\u0080"'),
    ],
)
def test_string_escaping(raw, expected):
    assert canonical_json_string(raw) == expected


def test_output_is_utf8_without_bom():
    data = canonicalize({"k": "é€"})
    assert data == b'{"k":"\xc3\xa9\xe2\x82\xac"}'
    assert not data.startswith(b"\xef\xbb\xbf")


# ---------------------------------------------------------- number formatting

@pytest.mark.parametrize(
    "value,expected",
    [
        (0, "0"),
        (0.0, "0"),
        (-0.0, "0"),
        (1, "1"),
        (-1, "-1"),
        (1.0, "1"),
        (1.5, "1.5"),
        (-1.5, "-1.5"),
        (1e21, "1e+21"),
        (1e20, "100000000000000000000"),
        (1e-6, "0.000001"),
        (1e-7, "1e-7"),
        (5e-324, "5e-324"),
        (1.7976931348623157e308, "1.7976931348623157e+308"),
        (9007199254740992.0, "9007199254740992"),
        (333333333.33333329, "333333333.3333333"),
        (2.2250738585072014e-308, "2.2250738585072014e-308"),
        (1.1, "1.1"),
        (100.0, "100"),
        (-1e-7, "-1e-7"),
    ],
)
def test_es6_number_to_string(value, expected):
    assert es6_number_to_string(value) == expected


def test_numbers_round_trip_through_python_float():
    for text in ["1e+21", "1e-7", "5e-324", "1.7976931348623157e+308"]:
        assert es6_number_to_string(float(text)) == text


# --------------------------------------------------------------- rejections

def test_nan_and_infinity_are_rejected():
    for bad in [float("nan"), float("inf"), float("-inf")]:
        with pytest.raises(CanonicalizationError):
            canonical_json_string(bad)


def test_non_string_keys_are_rejected():
    with pytest.raises(CanonicalizationError):
        canonical_json_string({1: "a"})


def test_unrepresentable_types_are_rejected():
    with pytest.raises(CanonicalizationError):
        canonical_json_string({"k": {1, 2}})


def test_oversized_integers_are_rejected():
    with pytest.raises(CanonicalizationError):
        canonical_json_string(2**53)


def test_booleans_are_not_numbers():
    assert canonical_json_string({"a": True, "b": False}) == '{"a":true,"b":false}'
    with pytest.raises(CanonicalizationError):
        es6_number_to_string(True)


# ------------------------------------------------------------------- hashing

def test_hash_is_stable_under_key_insertion_order():
    a = {"alpha": 1, "beta": {"x": [1, 2], "y": "z"}}
    b = {"beta": {"y": "z", "x": [1, 2]}, "alpha": 1}
    assert hash_payload(a) == hash_payload(b)


def test_hash_is_sha256_of_canonical_bytes():
    value = {"b": 2, "a": 1}
    assert hash_payload(value) == hashlib.sha256(b'{"a":1,"b":2}').hexdigest()
