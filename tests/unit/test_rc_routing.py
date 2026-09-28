"""Unit tests for gcir.rc_routing (Paper 2 v1.2 spec section 1L).

Development-generation artifact; not part of any frozen preregister-tier0
campaign.
"""

from __future__ import annotations

import pytest

from gcir.models import REASON_CODES, RESERVED_UNUSED_REASON_CODES
from gcir.rc_routing import STANDING_SAFETY_RTA_ROUTE, route_control_layer_defect
from gcir.models import ValidationError


def test_rc04_is_no_longer_reserved_unused():
    assert "RC-04" not in RESERVED_UNUSED_REASON_CODES
    assert "compile-ineligible" in REASON_CODES["RC-04"]


def test_wrong_layer_routes_to_rc06_and_standing_safety():
    routing = route_control_layer_defect(is_discrete_gateable_action=False)
    assert routing.reason_code == "RC-06"
    assert routing.routed_to_control_family == STANDING_SAFETY_RTA_ROUTE


def test_missing_timing_assurance_routes_to_rc04_never_rta():
    routing = route_control_layer_defect(is_discrete_gateable_action=True, timing_assurance_established=False)
    assert routing.reason_code == "RC-04"
    assert routing.routed_to_control_family is None
    assert routing.routed_to_control_family != STANDING_SAFETY_RTA_ROUTE


def test_no_defect_raises_rather_than_silently_choosing_a_code():
    with pytest.raises(ValidationError):
        route_control_layer_defect(is_discrete_gateable_action=True, timing_assurance_established=True)


def test_rc04_and_rc06_are_never_the_same_routing_decision():
    """The distinction spec 1L is emphatic about: these two must never
    collapse into one routing outcome for the two different defect kinds."""
    wrong_layer = route_control_layer_defect(is_discrete_gateable_action=False)
    missing_timing = route_control_layer_defect(is_discrete_gateable_action=True, timing_assurance_established=False)
    assert wrong_layer.reason_code != missing_timing.reason_code
    assert wrong_layer.routed_to_control_family != missing_timing.routed_to_control_family
