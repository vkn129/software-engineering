"""
Day 108 Practice: Interpolation Search

6 exercises. Implement the TODOs, then run: python practice.py
"""


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
# Exercise 1: interpolation_search
# ===================================================================
# Return index of x in sorted a, or -1.

def interpolation_search(a, x):
    """Interpolation search returning index or -1."""
    # TODO: implement
    pass


def _sol_interpolation_search(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi and a[lo] <= x <= a[hi]:
        if a[hi] == a[lo]:
            return lo if a[lo] == x else -1
        pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        pos = max(lo, min(hi, pos))
        if a[pos] == x:
            return pos
        if a[pos] < x:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


# ===================================================================
# Exercise 2: interpolation_lower_bound
# ===================================================================
# Return first index i with a[i] >= x, or len(a).

def interpolation_lower_bound(a, x):
    """First index with a[i] >= x."""
    # TODO: implement (you may fall back to a final binary-search step,
    # or just use linear scan in the narrowed range)
    pass


def _sol_interpolation_lower_bound(a, x):
    n = len(a)
    if n == 0:
        return 0
    if x <= a[0]:
        return 0
    if x > a[-1]:
        return n
    lo, hi = 0, n - 1
    # Narrow to a small window using interpolation, then linear sweep
    while hi - lo > 4 and a[lo] < x <= a[hi]:
        if a[hi] == a[lo]:
            break
        pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        # Clamp to [lo, hi-1], NOT [lo, hi]. The else-branch below does
        # `hi = pos`, so a probe landing exactly on `hi` leaves the window
        # unchanged and the loop spins forever. Duplicates make that probe
        # likely: on [1,2,2,2,3,5,5,8,8,8,8,10] searching 8, interpolation
        # picks index 8 == hi on every pass. The loop guard `hi - lo > 4`
        # means hi-1 >= lo, so this clamp always leaves a legal probe and
        # both branches now shrink the window by at least one slot.
        pos = max(lo, min(hi - 1, pos))
        if a[pos] < x:
            lo = pos + 1
        else:
            hi = pos
    while lo < n and a[lo] < x:
        lo += 1
    return lo


# ===================================================================
# Exercise 3: contains (predicate)
# ===================================================================

def contains(a, x):
    """Return True if x is in sorted a."""
    # TODO: implement using interpolation_search
    pass


def _sol_contains(a, x):
    return _sol_interpolation_search(a, x) != -1


# ===================================================================
# Exercise 4: count_occurrences
# ===================================================================
# Count how many times x appears in sorted a.

def count_occurrences(a, x):
    """Count of x in sorted a."""
    # TODO: implement
    pass


def _sol_count_occurrences(a, x):
    n = len(a)
    if n == 0:
        return 0
    # Lower bound of x
    lb = _sol_interpolation_lower_bound(a, x)
    # Upper bound of x = lower bound of x+1 (works for integer keys here)
    ub = _sol_interpolation_lower_bound(a, x + 1) if isinstance(x, int) else None
    if ub is None:
        # Generic: linear count from lb
        cnt = 0
        while lb < n and a[lb] == x:
            cnt += 1
            lb += 1
        return cnt
    return ub - lb


# ===================================================================
# Exercise 5: find_in_skewed (failure-mode-aware)
# ===================================================================
# Same task as exercise 1, but guard against the all-duplicates failure
# mode and skewed data by capping iterations.

def find_in_skewed(a, x, max_iters=64):
    """
    Search x in sorted a; if iteration count exceeds max_iters,
    fall back to a sub-array binary search. Return index or -1.
    """
    # TODO: implement
    pass


def _sol_find_in_skewed(a, x, max_iters=64):
    lo, hi = 0, len(a) - 1
    iters = 0
    while lo <= hi and a[lo] <= x <= a[hi]:
        if iters >= max_iters:
            # Binary fallback on remaining range
            while lo <= hi:
                mid = (lo + hi) // 2
                if a[mid] == x:
                    return mid
                if a[mid] < x:
                    lo = mid + 1
                else:
                    hi = mid - 1
            return -1
        if a[hi] == a[lo]:
            return lo if a[lo] == x else -1
        pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        pos = max(lo, min(hi, pos))
        if a[pos] == x:
            return pos
        if a[pos] < x:
            lo = pos + 1
        else:
            hi = pos - 1
        iters += 1
    return -1


# ===================================================================
# Exercise 6: nearest_value
# ===================================================================
# Return the value in sorted a closest to x (any of ties).

def nearest_value(a, x):
    """Closest a[i] to x by absolute difference."""
    # TODO: implement
    pass


def _sol_nearest_value(a, x):
    if not a:
        return None
    i = _sol_interpolation_lower_bound(a, x)
    candidates = []
    if i < len(a):
        candidates.append(a[i])
    if i > 0:
        candidates.append(a[i - 1])
    return min(candidates, key=lambda v: abs(v - x))


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

    a = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    # --- Exercise 1 ---
    print("Exercise 1: interpolation_search")
    check("hit at start", try_or_sol("interpolation_search", a, 10), 0)
    check("hit at end", try_or_sol("interpolation_search", a, 100), 9)
    check("hit middle", try_or_sol("interpolation_search", a, 50), 4)
    check("miss in range", try_or_sol("interpolation_search", a, 35), -1)
    check("miss below", try_or_sol("interpolation_search", a, 0), -1)
    check("miss above", try_or_sol("interpolation_search", a, 200), -1)

    # --- Exercise 2 ---
    print("\nExercise 2: interpolation_lower_bound")
    check("lb(35)", try_or_sol("interpolation_lower_bound", a, 35), 3)
    check("lb(40)", try_or_sol("interpolation_lower_bound", a, 40), 3)
    check("lb(0)", try_or_sol("interpolation_lower_bound", a, 0), 0)
    check("lb(200)", try_or_sol("interpolation_lower_bound", a, 200), 10)

    # --- Exercise 3 ---
    print("\nExercise 3: contains")
    check("contains 50", try_or_sol("contains", a, 50), True)
    check("missing 55", try_or_sol("contains", a, 55), False)
    check("empty array", try_or_sol("contains", [], 1), False)

    # --- Exercise 4 ---
    print("\nExercise 4: count_occurrences")
    b = [1, 2, 2, 2, 3, 5, 5, 8, 8, 8, 8, 10]
    check("count 2 -> 3", try_or_sol("count_occurrences", b, 2), 3)
    check("count 8 -> 4", try_or_sol("count_occurrences", b, 8), 4)
    check("count missing", try_or_sol("count_occurrences", b, 4), 0)
    check("count 1", try_or_sol("count_occurrences", b, 1), 1)

    # --- Exercise 5 ---
    print("\nExercise 5: find_in_skewed")
    # All-duplicates failure mode
    dup = [7] * 100
    check("all dups, hit", try_or_sol("find_in_skewed", dup, 7) >= 0, True)
    check("all dups, miss", try_or_sol("find_in_skewed", dup, 8), -1)
    # Heavy skew: dense low + outlier high
    skew = list(range(1, 1001)) + [10**9]
    check("skewed hit", try_or_sol("find_in_skewed", skew, 500), 499)
    check("skewed outlier", try_or_sol("find_in_skewed", skew, 10**9), 1000)

    # --- Exercise 6 ---
    print("\nExercise 6: nearest_value")
    check("nearest 33", try_or_sol("nearest_value", a, 33), 30)
    check("nearest 37", try_or_sol("nearest_value", a, 37), 40)
    check("nearest below all", try_or_sol("nearest_value", a, -100), 10)
    check("nearest above all", try_or_sol("nearest_value", a, 1000), 100)

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
