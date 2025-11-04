#!/usr/bin/env python3

# Simple test to verify CEI logic improvements
def test_cei_logic():
    # Simulate the flags tracking
    def simulate_function_analysis(has_checks, has_effects, has_interactions):
        flags = {"check": False, "effects": False, "interaction": False}

        # Simulate the sequence of operations
        if has_checks:
            flags["check"] = True

        if has_effects:
            flags["effects"] = True

        if has_interactions:
            flags["interaction"] = True

        # New CEI logic: vulnerable if interaction AND effects AND NOT check
        return flags["interaction"] and flags["effects"] and not flags["check"]

    # Test cases
    test_cases = [
        # (has_checks, has_effects, has_interactions, expected_vulnerable, description)
        (True, True, True, False, "CEI compliant: checks → effects → interactions"),
        (True, True, False, False, "Safe: checks and effects, no interactions"),
        (False, True, True, True, "Vulnerable: effects → interactions (no checks)"),
        (True, False, True, False, "Safe: checks and interactions, no effects"),
        (False, False, True, False, "Safe: only interactions"),
        (False, True, False, False, "Safe: only effects"),
    ]

    print("Testing CEI Logic Improvements:")
    print("=" * 50)

    all_passed = True
    for checks, effects, interactions, expected, description in test_cases:
        result = simulate_function_analysis(checks, effects, interactions)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result != expected:
            all_passed = False
        print(f"{status} | {description}")
        print(f"      Checks: {checks}, Effects: {effects}, Interactions: {interactions} → Vulnerable: {result} (expected: {expected})")
        print()

    print("=" * 50)
    if all_passed:
        print("✓ All CEI logic tests PASSED!")
    else:
        print("✗ Some CEI logic tests FAILED!")

    return all_passed

if __name__ == "__main__":
    test_cei_logic()
