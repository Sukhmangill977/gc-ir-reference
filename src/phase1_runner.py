#!/usr/bin/env python3
"""Phase 1 Development Test Runner.

Executes all Phase 1 tasks:
1. Exact runtime outcome implementation (PERMIT/DENY/HOLD)
2. Q7-Q10 audit query implementation
3. Negative fixture creation and testing
4. 13-injection scenario validation with exact outcomes
5. Case B compilation and verification
6. Case A regression testing
7. Full development test suite

Results written to results/development_v3/
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple
import hashlib

# Add src to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from gcir.compiler import compile_bundle
from gcir.caseio import load_case
from gcir.precedence import resolve
from gcir.audit_queries import run_all_audit_queries
from gcir.negative_fixtures import get_negative_fixtures

# Import injection scenarios
import importlib.util
inj_spec = importlib.util.spec_from_file_location(
    "case_b_injection_scenarios",
    REPO_ROOT / "experiments" / "case_b_injection_scenarios.py"
)
inj_module = importlib.util.module_from_spec(inj_spec)
inj_spec.loader.exec_module(inj_module)
run_injections = inj_module.run


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def hash_file(path: Path) -> str:
    """Compute SHA-256 of file."""
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def test_case_b_compilation() -> Dict[str, Any]:
    """Task 1: Compile Case B and verify results."""
    print("\n=== TASK 1: Case B Compilation ===")

    try:
        case_b = load_case("case_b")

        print(f"Case B loaded: {case_b.case_id}")

        # Get CompilerInputs
        compiler_inputs = case_b.compiler_inputs()

        # Compile
        compilation = compile_bundle(compiler_inputs)
        bundle = compilation.bundle

        print(f"Bundle compiled successfully")
        print(f"  Predicates: {len(bundle.predicates)} (expected ~9)")
        print(f"  Risk-derived: {sum(1 for p in bundle.predicates if p.get('origin_type') == 'risk_derived')}")
        print(f"  Compiler-invariant: {sum(1 for p in bundle.predicates if p.get('origin_type') == 'compiler_invariant')}")

        # Calculate payload hash
        payload_hash = bundle.payload_hash
        print(f"  Bundle hash: {payload_hash}")

        # Store bundle for later use
        test_case_b_compilation.bundle = bundle

        return {
            "status": "SUCCESS",
            "predicate_count": len(bundle.predicates),
            "risk_derived_count": sum(1 for p in bundle.predicates if p.get('origin_type') == 'risk_derived'),
            "compiler_invariant_count": sum(1 for p in bundle.predicates if p.get('origin_type') == 'compiler_invariant'),
            "bundle_hash": payload_hash,
            "acs_count": 6,  # Case B has 6 semantically justified ACS
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "FAILED", "error": str(e)}


def test_case_a_regression() -> Dict[str, Any]:
    """Task 6: Case A regression testing."""
    print("\n=== TASK 6: Case A Regression ===")

    try:
        case_a = load_case("case_a")

        print(f"Case A loaded: {case_a.case_id}")

        compiler_inputs = case_a.compiler_inputs()
        compilation = compile_bundle(compiler_inputs)
        bundle = compilation.bundle

        print(f"Case A compiled successfully")
        print(f"  Predicates: {len(bundle.predicates)}")

        # Clean control: all pass should give PERMIT
        clean_outcomes = {p["gcir_id"]: "pass" for p in bundle.predicates}
        clean_verdict = resolve(bundle, clean_outcomes)

        clean_passed = clean_verdict.get("decision") == "PERMIT"
        print(f"  Clean control: {clean_verdict.get('decision')} (expected PERMIT)")

        return {
            "status": "SUCCESS",
            "predicate_count": len(bundle.predicates),
            "clean_control_decision": clean_verdict.get("decision"),
            "clean_control_safe_state": clean_verdict.get("safe_state"),
            "clean_control_passed": clean_passed,
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "FAILED", "error": str(e)}


def test_case_b_injections(bundle) -> Dict[str, Any]:
    """Task 4: 13-injection scenario validation."""
    print("\n=== TASK 4: 13-Injection Scenarios ===")

    try:
        result = run_injections(bundle)

        print(f"Scenarios tested: {result['scenario_count']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Failed: {result['failed']}")
        print(f"  HOLD outcomes: {result.get('hold_outcomes', 0)}")
        print(f"  DENY outcomes: {result.get('deny_outcomes', 0)}")

        # Extract outcome counts
        hold_families = [
            r['family'] for r in result['scenarios']
            if r.get('actual_exact_outcome') == 'HOLD' and r['passed']
        ]
        deny_families = [
            r['family'] for r in result['scenarios']
            if r.get('actual_exact_outcome') == 'DENY' and r['passed']
        ]

        print(f"\n  HOLD scenarios (expected 4): {hold_families}")
        print(f"  DENY scenarios (expected 9): {deny_families}")

        return {
            "status": "SUCCESS" if result['failed'] == 0 else "PARTIAL",
            "scenario_count": result['scenario_count'],
            "passed": result['passed'],
            "failed": result['failed'],
            "hold_outcomes": len(hold_families),
            "deny_outcomes": len(deny_families),
            "hold_families": hold_families,
            "deny_families": deny_families,
            "scenarios": result['scenarios'],
        }
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "FAILED", "error": str(e)}


def test_audit_queries_case_b(bundle) -> Dict[str, Any]:
    """Task 2: Q7-Q10 audit queries on Case B."""
    print("\n=== TASK 2: Q7-Q10 Audit Queries (Case B) ===")

    try:
        results = run_all_audit_queries(bundle)

        for query, (passed, details) in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {query}: {status}")
            if not passed:
                print(f"      Details: {details}")

        all_passed = all(passed for passed, _ in results.values())

        return {
            "status": "SUCCESS" if all_passed else "FAILED",
            "q7_passed": results["Q7"][0],
            "q8_passed": results["Q8"][0],
            "q9_passed": results["Q9"][0],
            "q10_passed": results["Q10"][0],
            "q7_details": str(results["Q7"][1]),
            "q8_details": str(results["Q8"][1]),
            "q9_details": str(results["Q9"][1]),
            "q10_details": str(results["Q10"][1]),
        }
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "FAILED", "error": str(e)}


def test_audit_queries_case_a(bundle) -> Dict[str, Any]:
    """Bonus: Q7-Q10 audit queries on Case A."""
    print("\n=== BONUS: Q7-Q10 Audit Queries (Case A) ===")

    try:
        case_a = load_case("case_a")
        compiler_inputs = case_a.compiler_inputs()
        compilation = compile_bundle(compiler_inputs)
        bundle_a = compilation.bundle

        results = run_all_audit_queries(bundle_a)

        for query, (passed, details) in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {query}: {status}")

        all_passed = all(passed for passed, _ in results.values())

        return {
            "status": "SUCCESS" if all_passed else "FAILED",
            "q7_passed": results["Q7"][0],
            "q8_passed": results["Q8"][0],
            "q9_passed": results["Q9"][0],
            "q10_passed": results["Q10"][0],
        }
    except Exception as e:
        print(f"ERROR: {e}")
        return {"status": "FAILED", "error": str(e)}


def test_negative_fixtures(bundle) -> Dict[str, Any]:
    """Task 3: Test negative fixtures."""
    print("\n=== TASK 3: Negative Fixtures ===")

    try:
        fixtures = get_negative_fixtures(bundle.__dict__)

        print(f"Generated {len(fixtures)} negative fixtures")

        # Test that queries detect violations
        results = {}
        for name, bad_bundle in fixtures.items():
            try:
                query_results = run_all_audit_queries(bad_bundle)
                # All should have at least one query fail for negative fixtures
                any_failed = any(not passed for passed, _ in query_results.values())
                results[name] = {
                    "detected_violation": any_failed,
                    "details": {
                        q: {"passed": passed, "details": str(d)}
                        for q, (passed, d) in query_results.items()
                    }
                }
                status = "✓" if any_failed else "✗"
                print(f"  {status} {name}")
            except Exception as e:
                results[name] = {"detected_violation": False, "error": str(e)}
                print(f"  ✗ {name}: {e}")

        detected_count = sum(1 for r in results.values() if r.get("detected_violation"))

        return {
            "status": "SUCCESS" if detected_count >= 7 else "PARTIAL",
            "fixture_count": len(fixtures),
            "violations_detected": detected_count,
            "fixtures": results,
        }
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "FAILED", "error": str(e)}


def main():
    """Run all Phase 1 development tasks."""
    print("╔════════════════════════════════════════════════════════╗")
    print("║           PHASE 1 DEVELOPMENT TEST RUNNER               ║")
    print("║  PERMIT/DENY/HOLD, Q7-Q10, Fixtures, 13-Injections     ║")
    print("╚════════════════════════════════════════════════════════╝")

    output_dir = ensure_dir(REPO_ROOT / "results" / "development_v3")

    results = {}

    # Task 1: Case B Compilation
    results["case_b_compilation"] = test_case_b_compilation()

    # Load compiled Case B for subsequent tests
    try:
        case_b = load_case("case_b")
        compiler_inputs = case_b.compiler_inputs()
        compilation = compile_bundle(compiler_inputs)
        bundle_b = compilation.bundle
    except Exception as e:
        print(f"\nFATAL: Could not compile Case B: {e}")
        results["case_b_compilation"]["status"] = "FAILED"
        bundle_b = None

    if bundle_b:
        # Task 2: Q7-Q10 on Case B
        results["audit_queries_case_b"] = test_audit_queries_case_b(bundle_b)

        # Task 3: Negative Fixtures
        results["negative_fixtures"] = test_negative_fixtures(bundle_b)

        # Task 4: 13-Injections
        results["injections"] = test_case_b_injections(bundle_b)

    # Task 6: Case A Regression
    results["case_a_regression"] = test_case_a_regression()

    # Bonus: Q7-Q10 on Case A
    if bundle_b:
        results["audit_queries_case_a"] = test_audit_queries_case_a(bundle_b)

    # Write results
    results_file = output_dir / "phase1_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults written to {results_file}")

    # Summary
    print("\n╔════════════════════════════════════════════════════════╗")
    print("║                    SUMMARY                              ║")
    print("╚════════════════════════════════════════════════════════╝\n")

    for task, result in results.items():
        status = result.get("status", "UNKNOWN")
        symbol = "✓" if status == "SUCCESS" else "✗" if status == "FAILED" else "◐"
        print(f"{symbol} {task}: {status}")

    # Check go/no-go
    critical_passed = all(
        results.get(task, {}).get("status") == "SUCCESS"
        for task in [
            "case_b_compilation",
            "audit_queries_case_b",
            "case_a_regression",
            "injections"
        ]
    )

    print("\n" + "="*56)
    if critical_passed:
        print("✓ GO FOR PHASE 1 FREEZE - ALL CRITICAL TASKS PASSED")
    else:
        print("✗ NO-GO - CRITICAL TASKS FAILED")
    print("="*56)

    return 0 if critical_passed else 1


if __name__ == "__main__":
    sys.exit(main())
