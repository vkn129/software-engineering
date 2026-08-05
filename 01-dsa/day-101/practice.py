"""
Day 101 Practice: Non-Comparison Sorts

6 exercises: counting, radix (LSD/MSD), bucket, distribution-aware sorting.
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
# Exercise 1: Counting sort
# ===================================================================

def counting_sort(a, k):
    """Sort non-negative ints in [0, k). Must be stable. Return new list."""
    # TODO: implement
    pass


def _sol_counting_sort(a, k):
    if not a:
        return []
    count = [0] * k
    for x in a:
        count[x] += 1
    for i in range(1, k):
        count[i] += count[i - 1]
    out = [0] * len(a)
    for x in reversed(a):
        count[x] -= 1
        out[count[x]] = x
    return out


# ===================================================================
# Exercise 2: LSD radix sort
# ===================================================================

def radix_sort(a, base=10):
    """LSD radix sort for non-negative integers. Return new sorted list."""
    # TODO: implement
    pass


def _sol_radix_sort(a, base=10):
    if not a:
        return []
    out = list(a)
    m = max(out)
    exp = 1
    while m // exp > 0:
        # stable counting sort by digit
        n = len(out)
        new = [0] * n
        count = [0] * base
        for x in out:
            count[(x // exp) % base] += 1
        for i in range(1, base):
            count[i] += count[i - 1]
        for x in reversed(out):
            d = (x // exp) % base
            count[d] -= 1
            new[count[d]] = x
        out = new
        exp *= base
    return out


# ===================================================================
# Exercise 3: Bucket sort
# ===================================================================

def bucket_sort(a):
    """Bucket sort floats in [0, 1). Return new sorted list."""
    # TODO: implement
    pass


def _sol_bucket_sort(a):
    if not a:
        return []
    n = len(a)
    buckets = [[] for _ in range(n)]
    for x in a:
        idx = min(int(x * n), n - 1)
        buckets[idx].append(x)
    out = []
    for b in buckets:
        # Insertion sort each bucket
        for i in range(1, len(b)):
            v = b[i]; j = i - 1
            while j >= 0 and b[j] > v:
                b[j + 1] = b[j]; j -= 1
            b[j + 1] = v
        out.extend(b)
    return out


# ===================================================================
# Exercise 4: Sort negative ints with counting sort
# ===================================================================
# Trick: shift by -min(a) so all values become non-negative.

def counting_sort_signed(a):
    """Counting sort that works on negative integers too."""
    # TODO: shift, sort, shift back
    pass


def _sol_counting_sort_signed(a):
    if not a:
        return []
    lo = min(a)
    shifted = [x - lo for x in a]
    sorted_shifted = _sol_counting_sort(shifted, max(shifted) + 1)
    return [x + lo for x in sorted_shifted]


# ===================================================================
# Exercise 5: Sort strings by length
# ===================================================================
# Use counting sort by length (which is bounded by max_len).

def sort_strings_by_length(strings):
    """Sort strings by length, stable (preserve order within same length)."""
    # TODO: implement using counting sort on lengths
    pass


def _sol_sort_strings_by_length(strings):
    if not strings:
        return []
    max_len = max(len(s) for s in strings)
    count = [0] * (max_len + 1)
    for s in strings:
        count[len(s)] += 1
    for i in range(1, max_len + 1):
        count[i] += count[i - 1]
    out = [None] * len(strings)
    for s in reversed(strings):
        count[len(s)] -= 1
        out[count[len(s)]] = s
    return out


# ===================================================================
# Exercise 6: Maximum gap (using bucket sort idea)
# ===================================================================
# Given n unsorted integers, find the maximum gap between consecutive
# elements in their sorted form — in O(n) time.
# Pigeonhole: place n elements into n-1 buckets spanning [min, max].
# Max gap must occur BETWEEN buckets (not within), so only track each bucket's
# min and max.

def maximum_gap(a):
    """Return max difference between consecutive elements after sorting."""
    # TODO: implement using bucket-based linear approach
    pass


def _sol_maximum_gap(a):
    if len(a) < 2:
        return 0
    lo, hi = min(a), max(a)
    if lo == hi:
        return 0
    n = len(a)
    bucket_size = max(1, (hi - lo) // (n - 1))
    bucket_count = (hi - lo) // bucket_size + 1
    bucket_min = [None] * bucket_count
    bucket_max = [None] * bucket_count
    for x in a:
        idx = (x - lo) // bucket_size
        if bucket_min[idx] is None or x < bucket_min[idx]:
            bucket_min[idx] = x
        if bucket_max[idx] is None or x > bucket_max[idx]:
            bucket_max[idx] = x
    max_gap = 0
    prev_max = lo
    for i in range(bucket_count):
        if bucket_min[i] is None:
            continue
        max_gap = max(max_gap, bucket_min[i] - prev_max)
        prev_max = bucket_max[i]
    return max_gap


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

    print("Exercise 1: counting_sort")
    check("empty", try_or_sol("counting_sort", [], 5), [])
    check("basic", try_or_sol("counting_sort", [2, 5, 3, 0, 2, 3, 0, 3], 6),
          [0, 0, 2, 2, 3, 3, 3, 5])
    check("all same", try_or_sol("counting_sort", [4, 4, 4, 4], 5), [4, 4, 4, 4])
    check("range", try_or_sol("counting_sort", list(range(9, -1, -1)), 10), list(range(10)))

    print("\nExercise 2: radix_sort")
    check("empty", try_or_sol("radix_sort", []), [])
    check("basic", try_or_sol("radix_sort", [170, 45, 75, 90, 802, 24, 2, 66]),
          [2, 24, 45, 66, 75, 90, 170, 802])
    check("base 2", try_or_sol("radix_sort", [3, 1, 4, 1, 5, 9, 2, 6], 2),
          [1, 1, 2, 3, 4, 5, 6, 9])
    big = [random.Random(0).randint(0, 10000) for _ in range(200)]
    check("size 200", try_or_sol("radix_sort", big), sorted(big))

    print("\nExercise 3: bucket_sort")
    rng = random.Random(0)
    floats = [rng.random() for _ in range(50)]
    check("uniform floats", try_or_sol("bucket_sort", floats), sorted(floats))
    check("empty", try_or_sol("bucket_sort", []), [])
    check("singleton", try_or_sol("bucket_sort", [0.5]), [0.5])

    print("\nExercise 4: counting_sort_signed")
    check("with negatives", try_or_sol("counting_sort_signed", [3, -1, 4, -1, 5, -9, 2, 6]),
          [-9, -1, -1, 2, 3, 4, 5, 6])
    check("all negative", try_or_sol("counting_sort_signed", [-3, -1, -4, -1, -5]),
          [-5, -4, -3, -1, -1])
    check("empty", try_or_sol("counting_sort_signed", []), [])

    print("\nExercise 5: sort_strings_by_length")
    check("basic", try_or_sol("sort_strings_by_length", ["aaa", "b", "cc", "dddd", "e"]),
          ["b", "e", "cc", "aaa", "dddd"])
    # Stability: within same length, order preserved
    check("stability", try_or_sol("sort_strings_by_length", ["bb", "aa", "cc"]),
          ["bb", "aa", "cc"])

    print("\nExercise 6: maximum_gap")
    check("basic", try_or_sol("maximum_gap", [3, 6, 9, 1]), 3)
    check("single elt", try_or_sol("maximum_gap", [10]), 0)
    check("all same", try_or_sol("maximum_gap", [5, 5, 5]), 0)
    check("two elts", try_or_sol("maximum_gap", [1, 10000]), 9999)
    check("five elts", try_or_sol("maximum_gap", [1, 3, 100, 200, 250]), 100)

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
