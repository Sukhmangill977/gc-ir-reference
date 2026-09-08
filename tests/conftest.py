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


@pytest.fixture(params=["case_a", "case_b"])
def any_case(request, compiled_cases):
    return compiled_cases[request.param]
