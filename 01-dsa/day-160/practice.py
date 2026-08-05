"""
Day 160 Practice: Parallel Sort

6 exercises covering merge, sequential mergesort, partitioning, and
speedup arithmetic. Run: python practice.py
"""

import threading
import math


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: merge_two
# ===================================================================
# Classic two-way merge of pre-sorted lists.
def merge_two(a, b):
    """Merge two sorted lists into one sorted list."""
    # TODO
    pass


def _sol_merge_two(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


# ===================================================================
# Exercise 2: mergesort_seq
# ===================================================================
def mergesort_seq(arr):
    """Sequential mergesort."""
    # TODO
    pass


def _sol_mergesort_seq(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    return _sol_merge_two(_sol_mergesort_seq(arr[:mid]),
                          _sol_mergesort_seq(arr[mid:]))


# ===================================================================
# Exercise 3: partition
# ===================================================================
# Split arr into k equal-ish chunks. Last chunk may be larger.
def partition(arr, k):
    """Return list of k lists (last may be longer if not divisible)."""
    # TODO
    pass


def _sol_partition(arr, k):
    if k <= 0:
        return []
    n = len(arr)
    chunk = n // k
    parts = [arr[i * chunk:(i + 1) * chunk] for i in range(k)]
    if n % k:
        parts[-1].extend(arr[k * chunk:])
    return parts


# ===================================================================
# Exercise 4: merge_k
# ===================================================================
# k-way merge of pre-sorted lists. Iterative 2-way pairwise merge OK.
def merge_k(lists):
    """Merge k sorted lists into one."""
    # TODO
    pass


def _sol_merge_k(lists):
    if not lists:
        return []
    while len(lists) > 1:
        merged = []
        for i in range(0, len(lists), 2):
            if i + 1 < len(lists):
                merged.append(_sol_merge_two(lists[i], lists[i + 1]))
            else:
                merged.append(lists[i])
        lists = merged
    return lists[0]


# ===================================================================
# Exercise 5: parallel_sort_threaded
# ===================================================================
# Top-level orchestrator: partition into `num_workers` chunks, sort each
# in a thread (GIL anti-speedup expected), merge. Use mergesort_seq inside.
def parallel_sort_threaded(arr, num_workers=4):
    """Sort arr by sharding across threads."""
    # TODO
    pass


def _sol_parallel_sort_threaded(arr, num_workers=4):
    chunks = _sol_partition(arr, num_workers)
    sorted_chunks = [None] * len(chunks)

    def worker(i, chunk):
        sorted_chunks[i] = _sol_mergesort_seq(chunk)

    threads = [threading.Thread(target=worker, args=(i, c)) for i, c in enumerate(chunks)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return _sol_merge_k(sorted_chunks)


# ===================================================================
# Exercise 6: amdahl_speedup
# ===================================================================
# Amdahl's law: S = 1 / (s + p/N), where s = serial fraction, p = 1 - s,
# N = number of processors. Return computed speedup as float.
def amdahl_speedup(serial_fraction, num_processors):
    """Predicted speedup."""
    # TODO
    pass


def _sol_amdahl_speedup(serial_fraction, num_processors):
    if num_processors <= 0:
        return 0.0
    parallel = 1 - serial_fraction
    return 1.0 / (serial_fraction + parallel / num_processors)


# ===================================================================
# Test runner
# ===================================================================
def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        ok = got == expected if not isinstance(expected, float) else abs(got - expected) < 1e-6
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  expected {expected}, got {got}")
            failed += 1

    print("Exercise 1: merge_two")
    check("basic", try_or_sol("merge_two", [1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6])
    check("empty left", try_or_sol("merge_two", [], [1, 2]), [1, 2])
    check("duplicates", try_or_sol("merge_two", [1, 1], [1, 1]), [1, 1, 1, 1])

    print("\nExercise 2: mergesort_seq")
    check("basic", try_or_sol("mergesort_seq", [3, 1, 4, 1, 5, 9, 2, 6]), [1, 1, 2, 3, 4, 5, 6, 9])
    check("empty", try_or_sol("mergesort_seq", []), [])
    check("single", try_or_sol("mergesort_seq", [42]), [42])

    print("\nExercise 3: partition")
    check("4 into 2", try_or_sol("partition", [1, 2, 3, 4], 2), [[1, 2], [3, 4]])
    check("5 into 2", try_or_sol("partition", [1, 2, 3, 4, 5], 2), [[1, 2], [3, 4, 5]])
    check("3 into 3", try_or_sol("partition", [1, 2, 3], 3), [[1], [2], [3]])

    print("\nExercise 4: merge_k")
    check("3 lists", try_or_sol("merge_k", [[1, 4], [2, 5], [3, 6]]), [1, 2, 3, 4, 5, 6])
    check("empty list", try_or_sol("merge_k", []), [])
    check("one list", try_or_sol("merge_k", [[1, 2, 3]]), [1, 2, 3])

    print("\nExercise 5: parallel_sort_threaded")
    import random
    random.seed(0)
    arr = [random.randint(0, 1000) for _ in range(500)]
    check("matches sorted", try_or_sol("parallel_sort_threaded", arr, 4), sorted(arr))
    check("empty", try_or_sol("parallel_sort_threaded", [], 4), [])

    print("\nExercise 6: amdahl_speedup")
    check("s=0 N=4 → 4.0", try_or_sol("amdahl_speedup", 0.0, 4), 4.0)
    check("s=1 N=4 → 1.0", try_or_sol("amdahl_speedup", 1.0, 4), 1.0)
    # s=0.5, N=4 → 1/(0.5 + 0.5/4) = 1/0.625 = 1.6
    check("s=0.5 N=4 → 1.6", try_or_sol("amdahl_speedup", 0.5, 4), 1.6)

    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
