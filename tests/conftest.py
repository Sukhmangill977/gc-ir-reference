"""Shared fixtures.  Cases are loaded and compiled once per session."""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for path in (os.path.join(REPO_ROOT, "src"), REPO_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def compiled_cases():
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    compiled = {}
    for case_id in ("case_a", "case_b"):
        case = load_case(case_id)
        inputs = case.compiler_inputs()
        compiled[case_id] = (case, inputs, compile_bundle(inputs))
    return compiled


@pytest.fixture(scope="session")
def case_a(compiled_cases):
    return compiled_cases["case_a"]


@pytest.fixture(scope="session")
def case_b(compiled_cases):
    return compiled_cases["case_b"]


@pytest.fixture(scope="session")
def case_b_v1_1():
    """Development-generation artifact (schema v1.1); not part of the frozen
    preregister-tier0-v3.1 campaign.  See docs/CASE_B_V1_1_RATIONALE.md."""
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_b_v1_1")
    inputs = case.compiler_inputs()
    return case, inputs, compile_bundle(inputs)


@pytest.fixture(scope="session")
def case_c():
    """Development-generation artifact (schema v1.1, cyber-physical worked
    case). See docs/CASE_C_STATUS.md."""
    from gcir.caseio import load_case
    from gcir.compiler import compile_bundle

    case = load_case("case_c")
    inputs = case.compiler_inputs()
    return case, inputs, compile_bundle(inputs)


@pytest.fixture(params=["case_a", "case_b"])
def any_case(request, compiled_cases):
    return compiled_cases[request.param]
