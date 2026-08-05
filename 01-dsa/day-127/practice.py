"""
Day 127 Practice: Greedy Strategy

6 exercises covering activity selection, interval partitioning,
and counterexample reasoning. Implement TODOs, then: python practice.py
"""

from math import inf


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
# Exercise 1: Activity Selection (count)
# ===================================================================
# Return the maximum number of non-overlapping intervals.
# Strategy: sort by finish time, greedy pick.

def max_activities(intervals):
    """
    intervals: list of (start, finish) with start < finish
    Returns: int — max number of non-overlapping intervals selectable
    """
    # TODO: implement
    pass


def _sol_max_activities(intervals):
    if not intervals:
        return 0
    sorted_iv = sorted(intervals, key=lambda x: x[1])
    count = 0
    last_end = -inf
    for s, f in sorted_iv:
        if s >= last_end:
            count += 1
            last_end = f
    return count


# ===================================================================
# Exercise 2: Minimum Platforms
# ===================================================================
# Given arrival and departure times, return the minimum number of
# platforms so no train waits. Equivalent to max overlap at any instant.

def min_platforms(arrivals, departures):
    """
    arrivals, departures: parallel lists of times (departures[i] > arrivals[i])
    Returns: int — minimum platforms needed
    """
    # TODO: implement
    pass


def _sol_min_platforms(arrivals, departures):
    a = sorted(arrivals)
    d = sorted(departures)
    i = j = 0
    cur = peak = 0
    while i < len(a):
        if a[i] < d[j]:
            cur += 1
            peak = max(peak, cur)
            i += 1
        else:
            cur -= 1
            j += 1
    return peak


# ===================================================================
# Exercise 3: Counterexample for sort-by-start
# ===================================================================
# Sort-by-start fails when one early-starting long interval blocks many.
# Return ANY 3 intervals where sort-by-start picks fewer than sort-by-finish.

def counterexample_sort_by_start():
    """
    Returns: list of 3 (start, finish) intervals such that
             greedy-by-finish picks more than greedy-by-start.
    """
    # TODO: implement — return a valid counterexample
    pass


def _sol_counterexample_sort_by_start():
    # (0, 10) blocks (1, 2) and (3, 4) under sort-by-start
    return [(0, 10), (1, 2), (3, 4)]


# Verifier used by tests
def _verify_counterexample_by_start(intervals):
    """Returns True if greedy-by-finish > greedy-by-start on these intervals."""
    # by finish
    iv_f = sorted(intervals, key=lambda x: x[1])
    le = -inf
    cf = 0
    for s, f in iv_f:
        if s >= le:
            cf += 1
            le = f
    # by start
    iv_s = sorted(intervals, key=lambda x: x[0])
    le = -inf
    cs = 0
    for s, f in iv_s:
        if s >= le:
            cs += 1
            le = f
    return cf > cs


# ===================================================================
# Exercise 4: Non-overlapping Intervals (remove minimum)
# ===================================================================
# Given intervals, return the minimum number to REMOVE so the rest
# are non-overlapping. Equivalent to: total - max_activities.

def erase_overlap_intervals(intervals):
    """
    intervals: list of (start, finish)
    Returns: int — minimum number to remove
    """
    # TODO: implement
    pass


def _sol_erase_overlap_intervals(intervals):
    if not intervals:
        return 0
    iv = sorted(intervals, key=lambda x: x[1])
    kept = 0
    last_end = -inf
    for s, f in iv:
        if s >= last_end:
            kept += 1
            last_end = f
    return len(intervals) - kept


# ===================================================================
# Exercise 5: Maximum Meetings — return the indices
# ===================================================================
# Like activity_selection, but return the 1-indexed positions of the
# original meetings in any valid maximum schedule (sorted ascending).

def max_meetings_indices(intervals):
    """
    intervals: list of (start, finish), 1-indexed by position
    Returns: list of int — original positions (1-indexed) of chosen meetings
    """
    # TODO: implement
    pass


def _sol_max_meetings_indices(intervals):
    indexed = [(s, f, i + 1) for i, (s, f) in enumerate(intervals)]
    indexed.sort(key=lambda x: (x[1], x[2]))  # by finish, then index for stability
    chosen = []
    last_end = -inf
    for s, f, idx in indexed:
        if s >= last_end:
            chosen.append(idx)
            last_end = f
    return sorted(chosen)


# ===================================================================
# Exercise 6: Minimum Arrows to Burst Balloons
# ===================================================================
# Balloons are intervals on the x-axis. An arrow shot at x bursts every
# balloon that contains x. Find the minimum arrows to burst all balloons.
# Equivalent to: minimum number of points piercing every interval =
# max number of pairwise-disjoint intervals (by finish-time greedy).

def min_arrows(balloons):
    """
    balloons: list of (start, end) inclusive intervals
    Returns: int — minimum arrows to burst all
    """
    # TODO: implement
    pass


def _sol_min_arrows(balloons):
    if not balloons:
        return 0
    iv = sorted(balloons, key=lambda x: x[1])
    arrows = 0
    last_arrow = -inf
    for s, e in iv:
        if s > last_arrow:  # strictly past previous arrow → need new one
            arrows += 1
            last_arrow = e
    return arrows


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
    print("Exercise 1: Max Activities")
    check("classic", try_or_sol("max_activities",
          [(1, 4), (3, 5), (0, 6), (5, 7), (3, 9), (5, 9),
           (6, 10), (8, 11), (8, 12), (2, 14), (12, 16)]), 4)
    check("empty", try_or_sol("max_activities", []), 0)
    check("all overlap", try_or_sol("max_activities", [(0, 5), (1, 6), (2, 7)]), 1)
    check("all disjoint", try_or_sol("max_activities", [(0, 1), (2, 3), (4, 5)]), 3)

    # --- Exercise 2 ---
    print("\nExercise 2: Min Platforms")
    check("classic", try_or_sol("min_platforms",
          [900, 940, 950, 1100, 1500, 1800],
          [910, 1200, 1120, 1130, 1900, 2000]), 3)
    check("single train", try_or_sol("min_platforms", [100], [200]), 1)
    check("no overlap", try_or_sol("min_platforms", [0, 10, 20], [5, 15, 25]), 1)

    # --- Exercise 3 ---
    print("\nExercise 3: Counterexample for sort-by-start")
    ce = try_or_sol("counterexample_sort_by_start")
    ok = isinstance(ce, list) and len(ce) == 3 and _verify_counterexample_by_start(ce)
    check("valid 3-interval counterexample", ok, True)

    # --- Exercise 4 ---
    print("\nExercise 4: Erase Overlap Intervals")
    check("two overlap", try_or_sol("erase_overlap_intervals",
          [(1, 2), (2, 3), (3, 4), (1, 3)]), 1)
    check("none overlap", try_or_sol("erase_overlap_intervals",
          [(1, 2), (2, 3)]), 0)
    check("all overlap", try_or_sol("erase_overlap_intervals",
          [(1, 2), (1, 2), (1, 2)]), 2)

    # --- Exercise 5 ---
    print("\nExercise 5: Max Meetings Indices")
    # meetings: (1,2), (3,4), (0,6), (5,7), (8,9), (5,9)
    # by finish: m1(1-2), m2(3-4), m4(5-7), m5(8-9) → indices [1,2,4,5]
    check("4 meetings", try_or_sol("max_meetings_indices",
          [(1, 2), (3, 4), (0, 6), (5, 7), (8, 9), (5, 9)]),
          [1, 2, 4, 5])
    check("empty", try_or_sol("max_meetings_indices", []), [])

    # --- Exercise 6 ---
    print("\nExercise 6: Min Arrows")
    check("two groups", try_or_sol("min_arrows",
          [(10, 16), (2, 8), (1, 6), (7, 12)]), 2)
    check("nested", try_or_sol("min_arrows",
          [(1, 2), (3, 4), (5, 6), (7, 8)]), 4)
    check("all overlap", try_or_sol("min_arrows",
          [(1, 10), (2, 9), (3, 8)]), 1)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
