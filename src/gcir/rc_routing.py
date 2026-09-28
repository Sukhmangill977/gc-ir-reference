"""RC-04 / RC-06 control-layer defect routing (Paper 2 v1.2 spec section 1L).

The spec is emphatic that these two reason codes must be kept distinct and
must never be conflated by an automatic routing shortcut:

    RC-06: wrong control layer -- a continuous-control function that should
           not be compiled as a pre-action authorization predicate at all.
           Routed to the declared standing safety / runtime assurance (RTA)
           layer. This is the existing v1.1 reason code (Section III:
           "continuous control -- belongs to the runtime safety layer, fails
           AD-1"), unchanged by this module.

    RC-04: right control layer -- the discrete action *is* gateable, but the
           timing assurance the profile requires has not been established.
           Compile-ineligible. This must NEVER be automatically routed to
           RTA: RC-04 is a defect in the compiled control's readiness, not a
           claim that the action belongs to a different control layer.

This module holds the one routing decision the spec singles out as easy to
get wrong (spec 1L: "Do not route a missing timing-assurance case
automatically to RTA"), so it is exercised directly by its own dedicated
tests rather than folded into ``gcir.contract_v12``.
"""

from __future__ import annotations

from typing import NamedTuple, Optional

from .models import REASON_CODES, ValidationError

#: Where a wrong-control-layer (RC-06) defect is routed. Mirrors the
#: ``routed_to_control_family`` vocabulary already used by
#: ``NonRuntimeDisposition`` records (``gcir.compiler._disposition_record``).
STANDING_SAFETY_RTA_ROUTE = "standing_safety_rta"


class ControlLayerDefectRouting(NamedTuple):
    """The routing decision for one control-layer defect."""

    reason_code: str
    routed_to_control_family: Optional[str]
    rationale: str


def route_control_layer_defect(
    is_discrete_gateable_action: bool,
    timing_assurance_established: Optional[bool] = None,
) -> ControlLayerDefectRouting:
    """Decide RC-04 vs. RC-06 for one requirement, per spec section 1L.

    ``is_discrete_gateable_action``: False means the requirement is a
    continuous-control function (a feedback/monitoring loop, not a discrete
    pre-action decision) -- the wrong layer for a pre-action authorization
    predicate at all, regardless of timing. True means it *is* a discrete,
    gateable action.

    ``timing_assurance_established``: only consulted when the action is
    discrete/gateable. False means the profile's required timing assurance
    (e.g. a declared ``evaluation_latency_bound`` with an evidence path that
    can actually meet it) has not been established for this action.

    Raises ``ValidationError`` if called for a requirement with no control-
    layer defect at all (discrete, gateable, and timing assurance
    established) -- this function is a routing decision for an already-
    identified defect, not a defect detector.
    """
    if not is_discrete_gateable_action:
        return ControlLayerDefectRouting(
            reason_code="RC-06",
            routed_to_control_family=STANDING_SAFETY_RTA_ROUTE,
            rationale=REASON_CODES["RC-06"],
        )

    if timing_assurance_established is False:
        return ControlLayerDefectRouting(
            reason_code="RC-04",
            # Deliberately None, never STANDING_SAFETY_RTA_ROUTE: a missing
            # timing assurance is a readiness defect on the correct control
            # layer, not a wrong-layer condition, and spec 1L forbids
            # auto-routing it to RTA.
            routed_to_control_family=None,
            rationale=REASON_CODES["RC-04"],
        )

    raise ValidationError(
        "route_control_layer_defect called for a requirement with no "
        "control-layer defect (discrete, gateable, timing assurance "
        "established); RC-04/RC-06 routing does not apply here",
        code="NO_CONTROL_LAYER_DEFECT",
    )
