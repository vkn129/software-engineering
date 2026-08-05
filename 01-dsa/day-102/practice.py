"""
Day 102 Practice: External Sorting

6 exercises: K-way merge, run creation, replacement selection.
"""

import heapq
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
# Exercise 1: Two-way merge
# ===================================================================
# Merge two sorted iterables into one sorted list.

def merge_two_sorted(a, b):
    """Merge two sorted iterables. Return a sorted list."""
    # TODO: implement
    pass


def _sol_merge_two_sorted(a, b):
    out = []
    ia, ib = iter(a), iter(b)
    va = next(ia, None)
    vb = next(ib, None)
    while va is not None and vb is not None:
        if va <= vb:
            out.append(va); va = next(ia, None)
        else:
            out.append(vb); vb = next(ib, None)
    while va is not None:
        out.append(va); va = next(ia, None)
    while vb is not None:
        out.append(vb); vb = next(ib, None)
    return out


# ===================================================================
# Exercise 2: K-way merge with a heap
# ===================================================================

def k_way_merge(runs):
    """Merge a list of sorted iterables. Return a sorted list. Use a heap."""
    # TODO: implement using heapq
    pass


def _sol_k_way_merge(runs):
    out = []
    iters = [iter(r) for r in runs]
    heap = []
    for i, it in enumerate(iters):
        try:
            heap.append((next(it), i))
        except StopIteration:
            pass
    heapq.heapify(heap)
    while heap:
        val, i = heapq.heappop(heap)
        out.append(val)
        try:
            heapq.heappush(heap, (next(iters[i]), i))
        except StopIteration:
            pass
    return out


# ===================================================================
# Exercise 3: Create sorted runs from a stream
# ===================================================================
# Given a stream and a chunk_size, produce list of sorted runs.

def make_runs(stream, chunk_size):
    """Return list of sorted runs of length up to chunk_size."""
    # TODO: implement
    pass


def _sol_make_runs(stream, chunk_size):
    runs = []
    chunk = []
    for x in stream:
        chunk.append(x)
        if len(chunk) >= chunk_size:
            chunk.sort()
            runs.append(chunk)
            chunk = []
    if chunk:
        chunk.sort()
        runs.append(chunk)
    return runs


# ===================================================================
# Exercise 4: Full external sort
# ===================================================================

def external_sort(stream, chunk_size):
    """Run-creation + K-way merge. Return fully sorted list."""
    # TODO: implement by composing make_runs and k_way_merge
    pass


def _sol_external_sort(stream, chunk_size):
    runs = _sol_make_runs(stream, chunk_size)
    return _sol_k_way_merge(runs)


# ===================================================================
# Exercise 5: Count runs (replacement selection style)
# ===================================================================
# A "run" in a stream is a maximal non-decreasing subsequence.
# Count how many runs the input naturally contains. This is the
# baseline that replacement selection improves upon.

def count_natural_runs(stream):
    """Count maximal non-decreasing runs in the stream."""
    # TODO: implement
    pass


def _sol_count_natural_runs(stream):
    it = iter(stream)
    first = next(it, None)
    if first is None:
        return 0
    runs = 1
    prev = first
    for x in it:
        if x < prev:
            runs += 1
        prev = x
    return runs


# ===================================================================
# Exercise 6: Top-K from a huge stream
# ===================================================================
# You can't load the whole stream into memory. Use a heap of size K
# to find the K smallest elements. (Classic external problem.)

def top_k_smallest(stream, k):
    """Return the K smallest elements (sorted ascending) from a stream
    you can only iterate once. Memory: O(K)."""
    # TODO: implement using a max-heap of size K
    pass


def _sol_top_k_smallest(stream, k):
    if k <= 0:
        return []
    # Python's heapq is a min-heap; we negate to simulate a max-heap.
    heap = []
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, -x)
        elif x < -heap[0]:
            heapq.heapreplace(heap, -x)
    return sorted(-y for y in heap)


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

    print("Exercise 1: merge_two_sorted")
    check("empty + empty", try_or_sol("merge_two_sorted", [], []), [])
    check("interleaved", try_or_sol("merge_two_sorted", [1, 3, 5], [2, 4, 6]),
          [1, 2, 3, 4, 5, 6])
    check("one empty", try_or_sol("merge_two_sorted", [1, 2, 3], []),
          [1, 2, 3])
    check("dups", try_or_sol("merge_two_sorted", [1, 1, 2], [1, 2, 3]),
          [1, 1, 1, 2, 2, 3])

    print("\nExercise 2: k_way_merge")
    check("3 runs", try_or_sol("k_way_merge", [[1, 4, 7], [2, 5, 8], [3, 6, 9]]),
          [1, 2, 3, 4, 5, 6, 7, 8, 9])
    check("empty list", try_or_sol("k_way_merge", []), [])
    check("with empty runs", try_or_sol("k_way_merge", [[], [1, 2], [], [3]]),
          [1, 2, 3])
    check("uneven sizes", try_or_sol("k_way_merge", [[1], [2, 3, 4, 5], [0]]),
          [0, 1, 2, 3, 4, 5])

    print("\nExercise 3: make_runs")
    runs = try_or_sol("make_runs", [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5], 3)
    check("right number of runs", len(runs), 4)
    check("each run sorted", all(r == sorted(r) for r in runs), True)
    check("preserves all elements",
          sorted(sum(runs, [])), [1, 1, 2, 3, 3, 4, 5, 5, 5, 6, 9])

    print("\nExercise 4: external_sort")
    rng = random.Random(0)
    data = [rng.randint(0, 1000) for _ in range(100)]
    check("100 items, chunk=10", try_or_sol("external_sort", iter(data), 10),
          sorted(data))
    check("chunk > n", try_or_sol("external_sort", iter([3, 1, 2]), 100),
          [1, 2, 3])
    check("empty stream", try_or_sol("external_sort", iter([]), 10), [])

    print("\nExercise 5: count_natural_runs")
    check("sorted has 1 run", try_or_sol("count_natural_runs", [1, 2, 3, 4]), 1)
    check("reverse has n runs", try_or_sol("count_natural_runs", [4, 3, 2, 1]), 4)
    check("typical", try_or_sol("count_natural_runs", [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]), 6)
    check("empty", try_or_sol("count_natural_runs", []), 0)
    check("all equal = 1 run", try_or_sol("count_natural_runs", [5, 5, 5, 5]), 1)

    print("\nExercise 6: top_k_smallest")
    check("basic", try_or_sol("top_k_smallest", [3, 1, 4, 1, 5, 9, 2, 6], 3),
          [1, 1, 2])
    check("k=0", try_or_sol("top_k_smallest", [3, 1, 4], 0), [])
    check("k > n", try_or_sol("top_k_smallest", [3, 1, 4], 10), [1, 3, 4])
    check("with duplicates", try_or_sol("top_k_smallest", [5, 5, 5, 1, 1], 3),
          [1, 1, 5])

    print("\n" + "=" * 50)
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    run_tests()
