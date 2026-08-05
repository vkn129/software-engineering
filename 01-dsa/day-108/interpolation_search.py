"""
Day 108: Interpolation Search — From Scratch

Probes where the key 'should' be in a uniformly distributed array.
O(log log n) expected on uniform data; O(n) worst case on skewed.
"""

import time
import random
import math


# ---------------------------------------------------------------------------
# 1. Interpolation search
# ---------------------------------------------------------------------------

def interpolation_search(a, x):
    """
    Return index of x in sorted array a, or -1.
    O(log log n) expected on uniform data, O(n) worst case.
    """
    lo, hi = 0, len(a) - 1
    while lo <= hi and a[lo] <= x <= a[hi]:
        # Guard against degenerate range (all duplicates)
        if a[hi] == a[lo]:
            return lo if a[lo] == x else -1

        # Interpolate: assume a[i] is linear in i
        pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])

        # Clamp (defensive — should be in range by invariant, but floats/skew
        # can push it out)
        if pos < lo:
            pos = lo
        elif pos > hi:
            pos = hi

        if a[pos] == x:
            return pos
        elif a[pos] < x:
            lo = pos + 1
        else:
            hi = pos - 1
    return -1


# ---------------------------------------------------------------------------
# 2. Binary search (for benchmarking)
# ---------------------------------------------------------------------------

def binary_search(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if a[mid] == x:
            return mid
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ---------------------------------------------------------------------------
# 3. Hybrid: interpolation with binary fallback
# ---------------------------------------------------------------------------

def hybrid_search(a, x, hybrid_threshold_iters=None):
    """
    Use interpolation while it shrinks the range fast; if too many iterations,
    fall back to binary search. Caps worst case at O(log n).
    """
    n = len(a)
    if n == 0:
        return -1
    # Cap interpolation iterations at log(log(n)) * 4 — generous.
    if hybrid_threshold_iters is None:
        hybrid_threshold_iters = max(8, int(math.log2(max(2, math.log2(n + 2))) * 4))

    lo, hi = 0, n - 1
    iters = 0
    while lo <= hi and a[lo] <= x <= a[hi]:
        if iters >= hybrid_threshold_iters:
            # Fall back to binary on the remaining range
            sub = a[lo:hi + 1]
            idx = binary_search(sub, x)
            return -1 if idx == -1 else lo + idx

        if a[hi] == a[lo]:
            return lo if a[lo] == x else -1

        pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        if pos < lo:
            pos = lo
        elif pos > hi:
            pos = hi

        if a[pos] == x:
            return pos
        elif a[pos] < x:
            lo = pos + 1
        else:
            hi = pos - 1
        iters += 1
    return -1


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic interpolation search")
    print("=" * 60)

    a = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    print(f"\narray: {a}")
    for x in [10, 70, 100, 35, 0, 110]:
        idx = interpolation_search(a, x)
        print(f"  search({x:>3}) = {idx}")


def demo_benchmark_uniform():
    print("\n" + "=" * 60)
    print("DEMO 2: Uniform data — interpolation vs binary")
    print("=" * 60)

    n = 1_000_000
    a = list(range(0, n * 3, 3))   # uniform with step 3
    queries = [random.choice(a) for _ in range(50_000)]

    t = time.perf_counter()
    for x in queries:
        interpolation_search(a, x)
    interp_time = time.perf_counter() - t

    t = time.perf_counter()
    for x in queries:
        binary_search(a, x)
    binary_time = time.perf_counter() - t

    print(f"\n  n={n}, 50k queries, uniform distribution:")
    print(f"  Interpolation: {interp_time*1000:7.1f} ms")
    print(f"  Binary       : {binary_time*1000:7.1f} ms")
    print(f"  Ratio        : {binary_time/interp_time:.2f}x")
    print("  (Interpolation tends to win on truly uniform data, but the gap")
    print("   is narrower than theory predicts because of cache effects.)")


def demo_benchmark_skewed():
    print("\n" + "=" * 60)
    print("DEMO 3: Skewed data — interpolation degrades")
    print("=" * 60)

    # Exponentially distributed: values grow like 2^i
    n = 10_000
    a = sorted([int(math.exp(random.uniform(0, 20))) for _ in range(n)])
    queries = random.sample(a, 1000)

    t = time.perf_counter()
    for x in queries:
        interpolation_search(a, x)
    interp_time = time.perf_counter() - t

    t = time.perf_counter()
    for x in queries:
        binary_search(a, x)
    binary_time = time.perf_counter() - t

    t = time.perf_counter()
    for x in queries:
        hybrid_search(a, x)
    hybrid_time = time.perf_counter() - t

    print(f"\n  n={n}, exponentially distributed:")
    print(f"  Interpolation: {interp_time*1000:7.2f} ms  (suffers)")
    print(f"  Binary       : {binary_time*1000:7.2f} ms  (predictable)")
    print(f"  Hybrid       : {hybrid_time*1000:7.2f} ms  (capped at O(log n))")


def demo_pathological():
    print("\n" + "=" * 60)
    print("DEMO 4: Pathological case (count comparisons)")
    print("=" * 60)

    # Construct a worst-case array: most values clustered near 0, one outlier
    a = list(range(1, 1001)) + [10**9]
    # Searching for 10**9 — interpolation will guess far right immediately,
    # but for values in the middle it must scan one by one.

    # We'll count comparisons explicitly.
    def interp_with_count(arr, x):
        comps = 0
        lo, hi = 0, len(arr) - 1
        while lo <= hi and arr[lo] <= x <= arr[hi]:
            if arr[hi] == arr[lo]:
                comps += 1
                return comps
            pos = lo + ((x - arr[lo]) * (hi - lo)) // (arr[hi] - arr[lo])
            pos = max(lo, min(hi, pos))
            comps += 1
            if arr[pos] == x:
                return comps
            if arr[pos] < x:
                lo = pos + 1
            else:
                hi = pos - 1
        return comps

    def binary_with_count(arr, x):
        comps = 0
        lo, hi = 0, len(arr) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            comps += 1
            if arr[mid] == x:
                return comps
            if arr[mid] < x:
                lo = mid + 1
            else:
                hi = mid - 1
        return comps

    # Search for a value in the dense low region
    target = 500
    c_interp = interp_with_count(a, target)
    c_binary = binary_with_count(a, target)
    print(f"\n  Skewed array of size {len(a)}, search for {target}:")
    print(f"  Interpolation comparisons: {c_interp}")
    print(f"  Binary search comparisons: {c_binary}")
    print(f"  Interpolation degenerates because the outlier 10^9 makes")
    print(f"  each probe land near the start.")


if __name__ == "__main__":
    demo_basic()
    demo_benchmark_uniform()
    demo_benchmark_skewed()
    demo_pathological()
