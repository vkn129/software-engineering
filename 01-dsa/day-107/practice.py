"""
Day 107 Practice: Ternary Search

6 exercises. Implement the TODOs, then run: python practice.py
"""

import math


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


def _approx(a, b, tol=1e-4):
    return abs(a - b) <= tol


# ===================================================================
# Exercise 1: ternary_max
# ===================================================================
# Find x in [lo, hi] maximizing the unimodal function f. Return x.

def ternary_max(f, lo, hi, eps=1e-9):
    """Argmax of a unimodal continuous function on [lo, hi]."""
    # TODO: implement
    pass


def _sol_ternary_max(f, lo, hi, eps=1e-9):
    for _ in range(300):
        if hi - lo < eps:
            break
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if f(m1) < f(m2):
            lo = m1
        else:
            hi = m2
    return (lo + hi) / 2


# ===================================================================
# Exercise 2: ternary_min
# ===================================================================
# Argmin via negation trick or symmetric loop.

def ternary_min(f, lo, hi, eps=1e-9):
    """Argmin of a unimodal continuous function on [lo, hi]."""
    # TODO: implement
    pass


def _sol_ternary_min(f, lo, hi, eps=1e-9):
    return _sol_ternary_max(lambda x: -f(x), lo, hi, eps)


# ===================================================================
# Exercise 3: ternary_int_max
# ===================================================================
# Integer ternary search: max of unimodal int-function on [lo, hi].

def ternary_int_max(f, lo, hi):
    """Argmax over integers."""
    # TODO: implement
    pass


def _sol_ternary_int_max(f, lo, hi):
    while hi - lo >= 3:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if f(m1) < f(m2):
            lo = m1 + 1
        else:
            hi = m2 - 1
    best_x = lo
    best_v = f(lo)
    for x in range(lo + 1, hi + 1):
        v = f(x)
        if v > best_v:
            best_v = v
            best_x = x
    return best_x


# ===================================================================
# Exercise 4: closest_point_on_parabola
# ===================================================================
# Given a parabola y = x^2 and a target (tx, ty), find the x on the
# parabola that minimizes Euclidean distance to (tx, ty).
# Hint: distance squared is unimodal in x.

def closest_point_on_parabola(tx, ty):
    """Return x on parabola y=x^2 closest to (tx, ty)."""
    # TODO: implement
    pass


def _sol_closest_point_on_parabola(tx, ty):
    def dist_sq(x):
        return (x - tx) ** 2 + (x * x - ty) ** 2
    return _sol_ternary_max(lambda x: -dist_sq(x), -1000, 1000)


# ===================================================================
# Exercise 5: peak_index_in_mountain
# ===================================================================
# Find the peak index in a "mountain" array (strictly increasing then
# strictly decreasing). a[0] < a[1] < ... < a[k] > a[k+1] > ... > a[n-1]

def peak_index_in_mountain(a):
    """Index of the unique peak."""
    # TODO: implement (binary or ternary search both work; ternary is direct)
    pass


def _sol_peak_index_in_mountain(a):
    lo, hi = 0, len(a) - 1
    while hi - lo >= 3:
        m1 = lo + (hi - lo) // 3
        m2 = hi - (hi - lo) // 3
        if a[m1] < a[m2]:
            lo = m1 + 1
        else:
            hi = m2 - 1
    best_i = lo
    for i in range(lo + 1, hi + 1):
        if a[i] > a[best_i]:
            best_i = i
    return best_i


# ===================================================================
# Exercise 6: max_profit_quadratic
# ===================================================================
# Profit(p) = -2*p^2 + 40*p - 100 for price p in [0, 30]
# Find the price that maximizes profit.
# This is a classic price-elasticity problem.

def max_profit_quadratic(a, b, c, lo, hi):
    """
    Maximize f(p) = -a*p^2 + b*p + c on [lo, hi].
    Returns the optimal price p.
    """
    # TODO: implement using ternary_max
    pass


def _sol_max_profit_quadratic(a, b, c, lo, hi):
    return _sol_ternary_max(lambda p: -a * p * p + b * p + c, lo, hi)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, ok):
        nonlocal passed, failed
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            failed += 1

    def check_eq(name, got, expected, tol=1e-3):
        if isinstance(expected, int):
            check(name, got == expected)
        else:
            check(name, _approx(got, expected, tol))

    # --- Exercise 1 ---
    print("Exercise 1: ternary_max")
    x = try_or_sol("ternary_max", lambda x: -(x - 3) ** 2 + 7, -10, 10)
    check_eq("parabola max at 3", x, 3.0)
    x = try_or_sol("ternary_max", lambda x: -(x + 5) ** 2, -10, 0)
    check_eq("parabola max at -5", x, -5.0)
    x = try_or_sol("ternary_max", lambda x: -x * x, -1, 1)
    check_eq("max at 0", x, 0.0)

    # --- Exercise 2 ---
    print("\nExercise 2: ternary_min")
    x = try_or_sol("ternary_min", lambda x: (x - 2) ** 2, -10, 10)
    check_eq("parabola min at 2", x, 2.0)
    x = try_or_sol("ternary_min", lambda x: (x + 7) ** 2 + 3, -20, 0)
    check_eq("min at -7", x, -7.0)

    # --- Exercise 3 ---
    print("\nExercise 3: ternary_int_max")
    f = lambda k: -abs(k - 42) * 3 + 200
    check_eq("int max at 42", try_or_sol("ternary_int_max", f, 0, 100), 42)
    f2 = lambda k: 10 * k - k * k    # max at k = 5
    check_eq("int max of 10k - k^2", try_or_sol("ternary_int_max", f2, 0, 20), 5)

    # --- Exercise 4 ---
    print("\nExercise 4: closest_point_on_parabola")
    x = try_or_sol("closest_point_on_parabola", 0, 10)   # closest to (0,10)
    # By symmetry around x=0; derivative -> 2(x*x - 10)*2x + 2x = 0 -> x*(2x^2 - 19) = 0
    # Either x=0 or x = sqrt(19/2) ≈ 3.082. For (0,10), point above vertex,
    # the closest x lies near +/- sqrt(19/2).
    expected = math.sqrt(19 / 2)
    check("closest to (0,10) is ±sqrt(19/2)", _approx(abs(x), expected, 1e-2))

    # --- Exercise 5 ---
    print("\nExercise 5: peak_index_in_mountain")
    check_eq("peak idx of [1,3,5,4,2]", try_or_sol("peak_index_in_mountain", [1, 3, 5, 4, 2]), 2)
    check_eq("peak idx of [0,2,1]", try_or_sol("peak_index_in_mountain", [0, 2, 1]), 1)
    check_eq("peak idx of [1,2,3,4,5,3,1]", try_or_sol("peak_index_in_mountain", [1, 2, 3, 4, 5, 3, 1]), 4)

    # --- Exercise 6 ---
    print("\nExercise 6: max_profit_quadratic")
    # f(p) = -2p^2 + 40p - 100, optimal at p = 40 / (2*2) = 10
    p = try_or_sol("max_profit_quadratic", 2, 40, -100, 0, 30)
    check_eq("argmax of -2p^2+40p-100 is 10", p, 10.0)
    # f(p) = -p^2 + 6p + 1, optimal at p = 3
    p = try_or_sol("max_profit_quadratic", 1, 6, 1, 0, 10)
    check_eq("argmax of -p^2+6p+1 is 3", p, 3.0)

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
