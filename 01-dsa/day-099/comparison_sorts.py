"""
Day 99: Comparison Sorts Review — Merge, Quick, Heap

Pure implementations. Same data through each. Pathological inputs called out.
The point: feel the constant-factor differences and watch quicksort die.
"""

import random
import time
import sys

sys.setrecursionlimit(10**6)


# ---------------------------------------------------------------------------
# 1. Merge Sort
# ---------------------------------------------------------------------------

def merge_sort(a):
    """Top-down recursive merge sort. Returns new sorted list (stable)."""
    if len(a) <= 1:
        return a[:]
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return _merge(left, right)


def _merge(left, right):
    """Merge two sorted lists. Stable: equal elements take from left first."""
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:  # <= preserves stability
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


# ---------------------------------------------------------------------------
# 2. Quicksort — Lomuto partition with FIRST-ELEMENT pivot (the unsafe one)
# ---------------------------------------------------------------------------

def quicksort_unsafe(a):
    """In-place quicksort with first-element pivot. O(n^2) on sorted input."""
    a = a[:]
    _qs_unsafe(a, 0, len(a) - 1)
    return a


def _qs_unsafe(a, lo, hi):
    if lo >= hi:
        return
    # Move pivot to end so Lomuto works
    a[lo], a[hi] = a[hi], a[lo]
    p = _lomuto(a, lo, hi)
    _qs_unsafe(a, lo, p - 1)
    _qs_unsafe(a, p + 1, hi)


def _lomuto(a, lo, hi):
    """Partition a[lo..hi] around pivot a[hi]. Returns final pivot index."""
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


# ---------------------------------------------------------------------------
# 3. Quicksort — Random pivot (the safe one)
# ---------------------------------------------------------------------------

def quicksort_random(a):
    """Random pivot — O(n log n) expected on any input."""
    a = a[:]
    _qs_random(a, 0, len(a) - 1)
    return a


def _qs_random(a, lo, hi):
    if lo >= hi:
        return
    k = random.randint(lo, hi)
    a[k], a[hi] = a[hi], a[k]
    p = _lomuto(a, lo, hi)
    _qs_random(a, lo, p - 1)
    _qs_random(a, p + 1, hi)


# ---------------------------------------------------------------------------
# 4. Heap Sort
# ---------------------------------------------------------------------------

def heap_sort(a):
    """In-place heap sort. O(n log n) worst case. Not stable."""
    a = a[:]
    n = len(a)
    # Build max-heap bottom-up: O(n)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(a, i, n)
    # Extract max repeatedly: O(n log n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        _sift_down(a, 0, end)
    return a


def _sift_down(a, i, size):
    """Push a[i] down within heap of given size to restore max-heap property."""
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        largest = i
        if left < size and a[left] > a[largest]:
            largest = left
        if right < size and a[right] > a[largest]:
            largest = right
        if largest == i:
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest


# ---------------------------------------------------------------------------
# Bench helper
# ---------------------------------------------------------------------------

def time_sort(fn, data, label):
    start = time.perf_counter()
    out = fn(data)
    elapsed = time.perf_counter() - start
    assert out == sorted(data), f"{label} produced incorrect result"
    return elapsed


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_correctness():
    print("=" * 60)
    print("DEMO 1: Correctness on small inputs")
    print("=" * 60)
    cases = [
        [],
        [1],
        [2, 1],
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
        [5, 5, 5, 5, 5],
        list(range(10, 0, -1)),
    ]
    for c in cases:
        ms = merge_sort(c)
        qs = quicksort_random(c)
        hs = heap_sort(c)
        ok = ms == qs == hs == sorted(c)
        print(f"  {c[:8]}{'...' if len(c) > 8 else ''}  ->  {'OK' if ok else 'FAIL'}")


def demo_random_benchmark():
    print("\n" + "=" * 60)
    print("DEMO 2: Random input (n=20000)")
    print("=" * 60)
    n = 20000
    random.seed(42)
    data = [random.randint(0, 10**6) for _ in range(n)]

    print(f"\n{'algorithm':20s} {'time (ms)':>10s}")
    print("-" * 32)
    for name, fn in [("merge_sort", merge_sort),
                     ("quicksort_random", quicksort_random),
                     ("quicksort_unsafe", quicksort_unsafe),
                     ("heap_sort", heap_sort)]:
        t = time_sort(fn, data, name)
        print(f"  {name:18s} {t*1000:>10.2f}")


def demo_pathological_sorted():
    print("\n" + "=" * 60)
    print("DEMO 3: Already-sorted input — quicksort_unsafe explodes")
    print("=" * 60)

    # Quicksort with first-pivot recurses n times on sorted input.
    # We must keep n small or hit recursion limit.
    n = 2000
    data = list(range(n))

    print(f"\nn = {n}, input = [0, 1, 2, ..., n-1]")
    print(f"{'algorithm':20s} {'time (ms)':>10s}")
    print("-" * 32)
    for name, fn in [("merge_sort", merge_sort),
                     ("quicksort_random", quicksort_random),
                     ("heap_sort", heap_sort)]:
        t = time_sort(fn, data, name)
        print(f"  {name:18s} {t*1000:>10.2f}")

    # quicksort_unsafe separately — measure but note O(n^2)
    t = time_sort(quicksort_unsafe, data, "quicksort_unsafe")
    print(f"  {'quicksort_unsafe':18s} {t*1000:>10.2f}  <- O(n^2), n={n}")

    print("\nDouble n to see quadratic blow-up:")
    for n2 in [500, 1000, 2000]:
        d = list(range(n2))
        t = time_sort(quicksort_unsafe, d, f"unsafe@{n2}")
        print(f"  unsafe(n={n2:5d}): {t*1000:>8.2f} ms")
    print("(ratio between consecutive rows should approach 4x — that's n^2)")


def demo_reverse_sorted():
    print("\n" + "=" * 60)
    print("DEMO 4: Reverse-sorted input")
    print("=" * 60)
    n = 1500
    data = list(range(n, 0, -1))
    print(f"\nn = {n}, input = [n, n-1, ..., 1]")
    for name, fn in [("merge_sort", merge_sort),
                     ("quicksort_random", quicksort_random),
                     ("heap_sort", heap_sort),
                     ("quicksort_unsafe", quicksort_unsafe)]:
        t = time_sort(fn, data, name)
        marker = "  <- O(n^2)" if name == "quicksort_unsafe" else ""
        print(f"  {name:18s} {t*1000:>10.2f}{marker}")


if __name__ == "__main__":
    demo_correctness()
    demo_random_benchmark()
    demo_pathological_sorted()
    demo_reverse_sorted()
