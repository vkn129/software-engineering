"""
Day 100 Practice: Quicksort Deep Dive

6 exercises: partition schemes, pivots, dual-pivot, killer inputs.
"""

import random


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Hoare partition
# ===================================================================

def hoare_partition(a, lo, hi):
    """Hoare-style partition with pivot = a[lo]. Returns split index j
    such that all of a[lo..j] <= all of a[j+1..hi]."""
    # TODO: implement
    pass


def _sol_hoare_partition(a, lo, hi):
    pivot = a[lo]
    i, j = lo - 1, hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]


# ===================================================================
# Exercise 2: Median-of-3 pivot
# ===================================================================

def median_of_3_index(a, lo, hi):
    """Return the index (lo, mid, or hi) of the median of a[lo], a[mid], a[hi]."""
    # TODO: implement
    pass


def _sol_median_of_3_index(a, lo, hi):
    mid = (lo + hi) // 2
    trio = [(a[lo], lo), (a[mid], mid), (a[hi], hi)]
    trio.sort()
    return trio[1][1]


# ===================================================================
# Exercise 3: Quicksort with random pivot
# ===================================================================

def quicksort_random(a):
    """Return sorted list. Use Lomuto partition with random pivot."""
    # TODO: implement
    pass


def _sol_quicksort_random(a):
    a = a[:]
    def qs(lo, hi):
        if lo >= hi: return
        k = random.randint(lo, hi)
        a[k], a[hi] = a[hi], a[k]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        qs(lo, i - 1)
        qs(i + 1, hi)
    qs(0, len(a) - 1)
    return a


# ===================================================================
# Exercise 4: Three-way partition (Dutch National Flag)
# ===================================================================
# Partition a around pivot value into three regions: <p, ==p, >p.
# Useful when there are many duplicates.

def three_way_partition(a, pivot):
    """Return new list with all values <pivot first, then ==pivot, then >pivot."""
    # TODO: implement
    pass


def _sol_three_way_partition(a, pivot):
    lows  = [x for x in a if x < pivot]
    eqs   = [x for x in a if x == pivot]
    highs = [x for x in a if x > pivot]
    return lows + eqs + highs


# ===================================================================
# Exercise 5: Count partition calls (worst-case detector)
# ===================================================================
# Run quicksort with last-element pivot on a list. Return the number of
# partition calls made. On sorted input of length n, this should be ~n-1.

def count_partitions_last_pivot(a):
    """Run last-pivot quicksort on a copy; return number of partition calls."""
    # TODO: implement
    pass


def _sol_count_partitions_last_pivot(a):
    a = a[:]
    count = [0]
    def qs(lo, hi):
        if lo >= hi: return
        count[0] += 1
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        qs(lo, i - 1)
        qs(i + 1, hi)
    qs(0, len(a) - 1)
    return count[0]


# ===================================================================
# Exercise 6: kth smallest via Quickselect
# ===================================================================

def quickselect(a, k):
    """Return the k-th smallest element (0-indexed) without sorting fully."""
    # TODO: implement using random pivot
    pass


def _sol_quickselect(a, k):
    a = a[:]
    lo, hi = 0, len(a) - 1
    while lo < hi:
        idx = random.randint(lo, hi)
        a[idx], a[hi] = a[hi], a[idx]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        if i == k:
            return a[i]
        elif i < k:
            lo = i + 1
        else:
            hi = i - 1
    return a[lo]


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = failed = 0

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

    print("Exercise 1: hoare_partition")
    a = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    a_copy = a[:]
    s = try_or_sol("hoare_partition", a_copy, 0, len(a_copy) - 1)
    pivot = a[0]
    left_ok = all(x <= pivot for x in a_copy[:s+1])
    right_ok = all(x >= pivot for x in a_copy[s+1:])
    check("partition invariant", left_ok and right_ok, True)
    # All-equal — should NOT trigger O(n^2) loop, returns valid split
    a2 = [5, 5, 5, 5, 5]
    s2 = try_or_sol("hoare_partition", a2, 0, 4)
    check("hoare on all-equal returns mid-ish split", 0 <= s2 <= 3, True)

    print("\nExercise 2: median_of_3_index")
    check("median in middle", try_or_sol("median_of_3_index", [1, 5, 3], 0, 2), 2)
    check("median at lo",     try_or_sol("median_of_3_index", [3, 1, 5], 0, 2), 0)
    check("median at hi",     try_or_sol("median_of_3_index", [1, 3, 2], 0, 2), 2)
    check("equal values",     try_or_sol("median_of_3_index", [4, 4, 4], 0, 2) in (0, 1, 2), True)

    print("\nExercise 3: quicksort_random")
    random.seed(0)
    check("empty", try_or_sol("quicksort_random", []), [])
    check("single", try_or_sol("quicksort_random", [42]), [42])
    check("sorted input no blowup",
          try_or_sol("quicksort_random", list(range(500))),
          list(range(500)))
    big = [random.randint(-1000, 1000) for _ in range(300)]
    check("random size 300", try_or_sol("quicksort_random", big), sorted(big))
    dups = [5, 1, 5, 2, 5, 3, 5, 4, 5]
    check("with duplicates", try_or_sol("quicksort_random", dups), sorted(dups))

    print("\nExercise 4: three_way_partition")
    check("standard",
          try_or_sol("three_way_partition", [3, 1, 4, 1, 5, 9, 2, 6, 5], 5),
          [3, 1, 4, 1, 2, 5, 5, 9, 6])
    check("all less",
          try_or_sol("three_way_partition", [1, 2, 3], 10),
          [1, 2, 3])
    check("all equal",
          try_or_sol("three_way_partition", [5, 5, 5], 5),
          [5, 5, 5])

    print("\nExercise 5: count_partitions_last_pivot")
    # Sorted input → degenerate, ~n-1 partition calls
    check("sorted input degenerates",
          try_or_sol("count_partitions_last_pivot", list(range(20))), 19)
    # Already worst-case shaped
    check("reverse input also degenerates",
          try_or_sol("count_partitions_last_pivot", list(range(20, 0, -1))), 19)
    # Random input → roughly O(n log n) but always less than n-1 in expectation
    random.seed(99)
    rdata = [random.randint(0, 100) for _ in range(20)]
    n_random = try_or_sol("count_partitions_last_pivot", rdata)
    check("random input far below n-1", n_random < 19, True)

    print("\nExercise 6: quickselect")
    random.seed(1)
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    s = sorted(arr)
    check("k=0 (min)", try_or_sol("quickselect", arr, 0), s[0])
    check("k=5 (median)", try_or_sol("quickselect", arr, 5), s[5])
    check("k=last (max)", try_or_sol("quickselect", arr, len(arr) - 1), s[-1])
    big = [random.randint(0, 1000) for _ in range(200)]
    check("random k", try_or_sol("quickselect", big, 50), sorted(big)[50])

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
