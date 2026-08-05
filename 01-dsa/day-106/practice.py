"""
Day 106 Practice: Binary Search Variations

6 exercises. Implement the TODOs, then run: python practice.py
"""

from math import ceil


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


def _partition_point(lo, hi, predicate):
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if predicate(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


# ===================================================================
# Exercise 1: lower_bound
# ===================================================================
# Return the first index i with a[i] >= x. Return len(a) if none.

def lower_bound(a, x):
    """First index with value >= x."""
    # TODO: implement
    pass


def _sol_lower_bound(a, x):
    return _partition_point(0, len(a), lambda i: a[i] >= x)


# ===================================================================
# Exercise 2: upper_bound
# ===================================================================
# First index i with a[i] > x. Return len(a) if none.

def upper_bound(a, x):
    """First index with value > x."""
    # TODO: implement
    pass


def _sol_upper_bound(a, x):
    return _partition_point(0, len(a), lambda i: a[i] > x)


# ===================================================================
# Exercise 3: count_in_range
# ===================================================================
# Count how many a[i] are in [lo, hi] (inclusive on both ends).

def count_in_range(a, lo, hi):
    """Count of elements with lo <= a[i] <= hi in sorted a."""
    # TODO: implement using lower/upper bound
    pass


def _sol_count_in_range(a, lo, hi):
    return _sol_upper_bound(a, hi) - _sol_lower_bound(a, lo)


# ===================================================================
# Exercise 4: integer_sqrt
# ===================================================================
# Floor of sqrt(n) via binary search. No floating point.

def integer_sqrt(n):
    """Largest x with x*x <= n."""
    # TODO: implement
    pass


def _sol_integer_sqrt(n):
    if n < 2:
        return n
    i = _partition_point(0, n + 1, lambda x: x * x > n)
    return i - 1


# ===================================================================
# Exercise 5: min_eating_speed (Koko bananas)
# ===================================================================
# Each hour Koko picks one pile and eats up to k bananas.
# Minimum k such that she finishes all piles within h hours.

def min_eating_speed(piles, h):
    """Minimum bananas/hour to finish all piles in h hours."""
    # TODO: binary search on answer space
    pass


def _sol_min_eating_speed(piles, h):
    def can_finish(k):
        return sum(ceil(p / k) for p in piles) <= h
    return _partition_point(1, max(piles) + 1, can_finish)


# ===================================================================
# Exercise 6: ship_within_days
# ===================================================================
# Weights must be shipped in order over D days. Each day the ship's capacity
# is C. Find the minimum C.

def ship_within_days(weights, D):
    """Minimum ship capacity to ship all weights (in order) in D days."""
    # TODO: implement
    pass


def _sol_ship_within_days(weights, D):
    def feasible(cap):
        days, cur = 1, 0
        for w in weights:
            if w > cap:
                return False
            if cur + w > cap:
                days += 1
                cur = w
            else:
                cur += w
        return days <= D

    return _partition_point(max(weights), sum(weights) + 1, feasible)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    # --- Exercise 1 ---
    print("Exercise 1: lower_bound")
    a = [1, 2, 4, 4, 4, 5, 7, 9]
    check("lb(4) on duplicates", try_or_sol("lower_bound", a, 4), 2)
    check("lb(0) below all", try_or_sol("lower_bound", a, 0), 0)
    check("lb(10) above all", try_or_sol("lower_bound", a, 10), 8)
    check("lb(3) missing middle", try_or_sol("lower_bound", a, 3), 2)

    # --- Exercise 2 ---
    print("\nExercise 2: upper_bound")
    check("ub(4) on duplicates", try_or_sol("upper_bound", a, 4), 5)
    check("ub(0) below all", try_or_sol("upper_bound", a, 0), 0)
    check("ub(9) topmost", try_or_sol("upper_bound", a, 9), 8)

    # --- Exercise 3 ---
    print("\nExercise 3: count_in_range")
    check("count [4,7]", try_or_sol("count_in_range", a, 4, 7), 5)
    check("count [4,4]", try_or_sol("count_in_range", a, 4, 4), 3)
    check("count [-1, 100]", try_or_sol("count_in_range", a, -1, 100), 8)

    # --- Exercise 4 ---
    print("\nExercise 4: integer_sqrt")
    check("isqrt(0)", try_or_sol("integer_sqrt", 0), 0)
    check("isqrt(1)", try_or_sol("integer_sqrt", 1), 1)
    check("isqrt(8)", try_or_sol("integer_sqrt", 8), 2)
    check("isqrt(9)", try_or_sol("integer_sqrt", 9), 3)
    check("isqrt(15241383935)", try_or_sol("integer_sqrt", 15241383935), 123455)

    # --- Exercise 5 ---
    print("\nExercise 5: min_eating_speed")
    check("Koko 3,6,7,11 h=8", try_or_sol("min_eating_speed", [3, 6, 7, 11], 8), 4)
    check("Koko 30,11,23,4,20 h=5", try_or_sol("min_eating_speed", [30, 11, 23, 4, 20], 5), 30)
    check("Koko 30,11,23,4,20 h=6", try_or_sol("min_eating_speed", [30, 11, 23, 4, 20], 6), 23)

    # --- Exercise 6 ---
    print("\nExercise 6: ship_within_days")
    check("ship 1..10 D=5", try_or_sol("ship_within_days", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5), 15)
    check("ship 3,2,2,4,1,4 D=3", try_or_sol("ship_within_days", [3, 2, 2, 4, 1, 4], 3), 6)
    check("ship 1,2,3,1,1 D=4", try_or_sol("ship_within_days", [1, 2, 3, 1, 1], 4), 3)

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
