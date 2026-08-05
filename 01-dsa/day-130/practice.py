"""
Day 130 Practice: Fractional Knapsack + 0/1 Comparison

6 exercises. Implement TODOs, then: python practice.py
"""

from math import isclose


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Fractional Knapsack — Max Value
# ===================================================================

def fractional_max_value(items, capacity):
    """
    items: list of (value, weight), weight > 0
    capacity: float >= 0
    Returns: max achievable value (float)
    """
    # TODO: implement
    pass


def _sol_fractional_max_value(items, capacity):
    if capacity <= 0 or not items:
        return 0.0
    sorted_items = sorted(items, key=lambda x: x[0] / x[1], reverse=True)
    total = 0.0
    rem = capacity
    for v, w in sorted_items:
        if rem <= 0:
            break
        if w <= rem:
            total += v
            rem -= w
        else:
            total += v * (rem / w)
            rem = 0
    return total


# ===================================================================
# Exercise 2: Fractional Knapsack — Selection
# ===================================================================
# Return list of (original_index, fraction_taken). Order by density desc.

def fractional_selection(items, capacity):
    """
    Returns: list of (idx, fraction) in density-descending order,
             excluding items with fraction == 0.
    """
    # TODO: implement
    pass


def _sol_fractional_selection(items, capacity):
    if capacity <= 0 or not items:
        return []
    indexed = [(v, w, i) for i, (v, w) in enumerate(items)]
    indexed.sort(key=lambda x: x[0] / x[1], reverse=True)
    out = []
    rem = capacity
    for v, w, i in indexed:
        if rem <= 0:
            break
        if w <= rem:
            out.append((i, 1.0))
            rem -= w
        else:
            out.append((i, rem / w))
            rem = 0
    return out


# ===================================================================
# Exercise 3: 0/1 Knapsack DP (optimal)
# ===================================================================
# Integer weights, integer capacity.

def knapsack_01(items, capacity):
    """
    items: list of (value, weight) with integer weight
    capacity: integer >= 0
    Returns: max value (integer)
    """
    # TODO: implement
    pass


def _sol_knapsack_01(items, capacity):
    dp = [0] * (capacity + 1)
    for v, w in items:
        for c in range(capacity, w - 1, -1):
            if dp[c - w] + v > dp[c]:
                dp[c] = dp[c - w] + v
    return dp[capacity]


# ===================================================================
# Exercise 4: Show Greedy Fails on 0/1
# ===================================================================
# Return ANY 3-item, integer-capacity instance where density-greedy
# differs from optimal 0/1.

def counterexample_01_greedy():
    """
    Returns: (items, capacity) tuple with len(items) == 3, integer capacity,
             integer weights, such that:
               density_greedy_01(items, cap) < knapsack_01(items, cap)
    """
    # TODO: return your counterexample
    pass


def _sol_counterexample_01_greedy():
    return ([(60, 10), (100, 20), (120, 30)], 50)


def _verify_01_counterexample(items, capacity):
    """True iff density-greedy < DP optimum."""
    if len(items) != 3:
        return False
    if not isinstance(capacity, int) or capacity <= 0:
        return False
    g_sorted = sorted(items, key=lambda x: x[0] / x[1], reverse=True)
    g = 0
    rem = capacity
    for v, w in g_sorted:
        if w <= rem:
            g += v
            rem -= w
    opt = _sol_knapsack_01(items, capacity)
    return g < opt


# ===================================================================
# Exercise 5: Density Ratio Comparison
# ===================================================================
# For the same items + capacity, return (fractional_val, dp_01_val).
# Always: fractional_val >= dp_01_val.

def compare_fractional_vs_01(items, capacity):
    """
    Returns: tuple (frac_value: float, opt_01_value: int)
    """
    # TODO: implement (use the prior solutions)
    pass


def _sol_compare_fractional_vs_01(items, capacity):
    return (_sol_fractional_max_value(items, capacity),
            _sol_knapsack_01(items, capacity))


# ===================================================================
# Exercise 6: Single-Item Greedy 2-Approximation
# ===================================================================
# Return max(density_greedy_01, best single item that fits alone).

def knapsack_01_2approx(items, capacity):
    """
    Returns: int — max of:
      a) density-greedy total value
      b) single largest-value item that fits within capacity
    """
    # TODO: implement
    pass


def _sol_knapsack_01_2approx(items, capacity):
    sorted_items = sorted(items, key=lambda x: x[0] / x[1], reverse=True)
    g = 0
    rem = capacity
    for v, w in sorted_items:
        if w <= rem:
            g += v
            rem -= w
    best_single = 0
    for v, w in items:
        if w <= capacity and v > best_single:
            best_single = v
    return max(g, best_single)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        ok = (isclose(got, expected, abs_tol=1e-6)
              if isinstance(expected, float) or isinstance(got, float)
              else got == expected)
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    # --- Exercise 1 ---
    print("Exercise 1: Fractional Max Value")
    # Classic: 60+100+(2/3)*120 = 240
    check("classic",
          try_or_sol("fractional_max_value",
                     [(60, 10), (100, 20), (120, 30)], 50),
          240.0)
    check("empty items",
          try_or_sol("fractional_max_value", [], 100), 0.0)
    check("zero capacity",
          try_or_sol("fractional_max_value", [(100, 10)], 0), 0.0)
    check("capacity exceeds all",
          try_or_sol("fractional_max_value",
                     [(50, 5), (60, 6)], 1000),
          110.0)

    # --- Exercise 2 ---
    print("\nExercise 2: Fractional Selection")
    sel = try_or_sol("fractional_selection",
                     [(60, 10), (100, 20), (120, 30)], 50)
    # Density desc: idx0(6.0), idx1(5.0), idx2(4.0)
    check("first is idx 0 full", sel[0], (0, 1.0))
    check("second is idx 1 full", sel[1], (1, 1.0))
    check("third is idx 2 fractional",
          (sel[2][0] == 2 and isclose(sel[2][1], 2/3, abs_tol=1e-6)), True)

    # --- Exercise 3 ---
    print("\nExercise 3: 0/1 Knapsack DP")
    check("classic", try_or_sol("knapsack_01",
                                [(60, 10), (100, 20), (120, 30)], 50), 220)
    check("can't fit",
          try_or_sol("knapsack_01", [(100, 50)], 10), 0)
    check("take all", try_or_sol("knapsack_01",
                                [(10, 1), (20, 2), (30, 3)], 6), 60)

    # --- Exercise 4 ---
    print("\nExercise 4: 0/1 Greedy Counterexample")
    ce = try_or_sol("counterexample_01_greedy")
    ok = (isinstance(ce, tuple) and len(ce) == 2
          and _verify_01_counterexample(ce[0], ce[1]))
    check("greedy < optimal", ok, True)

    # --- Exercise 5 ---
    print("\nExercise 5: Fractional vs 0/1")
    f, o = try_or_sol("compare_fractional_vs_01",
                      [(60, 10), (100, 20), (120, 30)], 50)
    check("fractional value", isclose(f, 240.0, abs_tol=1e-6), True)
    check("0/1 value", o, 220)
    check("fractional >= 0/1", f >= o, True)

    # --- Exercise 6 ---
    print("\nExercise 6: 2-Approximation")
    # Items (1,1), (999, 1000) with cap 1000:
    # density-greedy picks (1,1) then can't fit (999, 1000) → 1.
    # best single = 999. 2-approx returns 999.
    check("rescue with single item",
          try_or_sol("knapsack_01_2approx",
                     [(1, 1), (999, 1000)], 1000), 999)
    check("classic 2-approx",
          try_or_sol("knapsack_01_2approx",
                     [(60, 10), (100, 20), (120, 30)], 50), 160)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
