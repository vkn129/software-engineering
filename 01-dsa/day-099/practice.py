"""
Day 99 Practice: Comparison Sorts

6 exercises covering merge, quick, heap, stability, and pathological cases.
Implement each TODO, then run: python practice.py
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
# Exercise 1: Merge two sorted lists (stable)
# ===================================================================

def merge_two(left, right):
    """Merge two pre-sorted lists into one sorted list, stable."""
    # TODO: implement
    pass


def _sol_merge_two(left, right):
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


# ===================================================================
# Exercise 2: Top-down merge sort
# ===================================================================

def merge_sort(a):
    """Return new sorted list. Use recursion."""
    # TODO: implement
    pass


def _sol_merge_sort(a):
    if len(a) <= 1:
        return a[:]
    mid = len(a) // 2
    return _sol_merge_two(_sol_merge_sort(a[:mid]),
                          _sol_merge_sort(a[mid:]))


# ===================================================================
# Exercise 3: Lomuto partition
# ===================================================================
# Partition a[lo..hi] around pivot = a[hi]. Return final pivot index.
# Mutates the input list.

def lomuto_partition(a, lo, hi):
    """Partition in-place. a[hi] is pivot. Return final pivot index."""
    # TODO: implement
    pass


def _sol_lomuto_partition(a, lo, hi):
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


# ===================================================================
# Exercise 4: Quicksort with random pivot
# ===================================================================

def quicksort(a):
    """In-place-ish quicksort. Return sorted list (work on a copy)."""
    # TODO: implement using random pivot to avoid O(n^2) on sorted input
    pass


def _sol_quicksort(a):
    a = a[:]
    def qs(lo, hi):
        if lo >= hi:
            return
        k = random.randint(lo, hi)
        a[k], a[hi] = a[hi], a[k]
        p = _sol_lomuto_partition(a, lo, hi)
        qs(lo, p - 1)
        qs(p + 1, hi)
    qs(0, len(a) - 1)
    return a


# ===================================================================
# Exercise 5: Heap sort
# ===================================================================
# Build a max-heap in-place, then extract repeatedly.

def heap_sort(a):
    """In-place-ish heap sort. Return sorted list (work on a copy)."""
    # TODO: implement
    pass


def _sol_heap_sort(a):
    a = a[:]
    n = len(a)

    def sift_down(i, size):
        while True:
            l, r = 2*i + 1, 2*i + 2
            big = i
            if l < size and a[l] > a[big]:
                big = l
            if r < size and a[r] > a[big]:
                big = r
            if big == i:
                return
            a[i], a[big] = a[big], a[i]
            i = big

    for i in range(n // 2 - 1, -1, -1):
        sift_down(i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(0, end)
    return a


# ===================================================================
# Exercise 6: Is this sort stable?
# ===================================================================
# Given a sort function, check whether it preserves the relative order of
# equal keys. Test on records [(key, original_index), ...].

def is_stable(sort_fn):
    """Return True iff sort_fn(records) preserves order of equal keys."""
    # TODO: build a test input with duplicates, sort by key, check indices
    pass


class _KeyOnly:
    """Wraps a value but only compares by `key` — secondary `tag` is ignored.
    Lets us detect whether a sort is stable on equal keys."""
    __slots__ = ("key", "tag")
    def __init__(self, key, tag):
        self.key = key
        self.tag = tag
    def __lt__(self, other): return self.key < other.key
    def __le__(self, other): return self.key <= other.key
    def __gt__(self, other): return self.key > other.key
    def __ge__(self, other): return self.key >= other.key
    def __eq__(self, other): return self.key == other.key
    def __repr__(self): return f"({self.key},{self.tag})"


def _sol_is_stable(sort_fn):
    """Run sort on many duplicate-heavy inputs. If any run reorders equal
    keys, declare unstable. Stable sorts NEVER reorder; unstable ones almost
    always will on heavy duplicates."""
    rng = random.Random(12345)
    for _ in range(15):
        # Lots of duplicates → unstable sorts will reorder equals
        records = [_KeyOnly(rng.randint(0, 3), tag) for tag in range(40)]
        out = sort_fn(records)
        seen = {}
        for rec in out:
            if rec.key in seen and rec.tag < seen[rec.key]:
                return False
            seen[rec.key] = rec.tag
    return True


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

    print("Exercise 1: merge_two")
    check("empty + empty", try_or_sol("merge_two", [], []), [])
    check("empty + nonempty", try_or_sol("merge_two", [], [1, 2]), [1, 2])
    check("interleaved", try_or_sol("merge_two", [1, 3, 5], [2, 4, 6]),
          [1, 2, 3, 4, 5, 6])
    check("duplicates stable", try_or_sol("merge_two", [1, 2], [2, 3]),
          [1, 2, 2, 3])

    print("\nExercise 2: merge_sort")
    check("empty", try_or_sol("merge_sort", []), [])
    check("one", try_or_sol("merge_sort", [42]), [42])
    check("reverse", try_or_sol("merge_sort", [5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])
    check("with dups", try_or_sol("merge_sort", [3, 1, 4, 1, 5, 9, 2, 6, 5]),
          [1, 1, 2, 3, 4, 5, 5, 6, 9])

    print("\nExercise 3: lomuto_partition")
    a = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    p = try_or_sol("lomuto_partition", a, 0, len(a) - 1)
    # Everything left of p should be <= pivot, everything right should be > pivot
    pivot_val = a[p]
    left_ok = all(x <= pivot_val for x in a[:p])
    right_ok = all(x > pivot_val for x in a[p+1:])
    check("partition invariant holds", left_ok and right_ok, True)

    a2 = [1, 2, 3, 4, 5]
    p2 = try_or_sol("lomuto_partition", a2, 0, 4)
    check("sorted input pivot=last", p2, 4)

    print("\nExercise 4: quicksort")
    random.seed(7)
    check("empty", try_or_sol("quicksort", []), [])
    check("random", try_or_sol("quicksort", [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]),
          [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])
    big = [random.randint(0, 1000) for _ in range(200)]
    check("random size 200", try_or_sol("quicksort", big), sorted(big))
    check("already sorted (no blow up)", try_or_sol("quicksort", list(range(100))),
          list(range(100)))

    print("\nExercise 5: heap_sort")
    check("empty", try_or_sol("heap_sort", []), [])
    check("one", try_or_sol("heap_sort", [1]), [1])
    check("reverse", try_or_sol("heap_sort", [5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])
    check("dups", try_or_sol("heap_sort", [2, 2, 2, 1, 1, 3]),
          [1, 1, 2, 2, 2, 3])

    print("\nExercise 6: is_stable")
    check("merge_sort is stable", try_or_sol("is_stable", _sol_merge_sort), True)
    # quicksort_random is NOT stable in general — we detect that.
    check("quicksort_random not stable",
          try_or_sol("is_stable", _sol_quicksort), False)

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
