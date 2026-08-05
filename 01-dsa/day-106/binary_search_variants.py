"""
Day 106: Binary Search Variations — From Scratch

One unified template, many variants. Every binary search reduces to:
'find the first index where a monotonic predicate becomes True.'
"""

from math import ceil
import time
import random


# ---------------------------------------------------------------------------
# 1. Unified template: first index where predicate(i) is True
# ---------------------------------------------------------------------------

def partition_point(lo, hi, predicate):
    """
    Find the smallest i in [lo, hi) with predicate(i) == True.
    Assumes predicate is monotonic: False...False, True...True.
    Returns hi if no such index exists.

    This is the single primitive — every variant below is built on this.
    """
    while lo < hi:
        # Overflow-safe mid (matters in C/Java; harmless in Python)
        mid = lo + (hi - lo) // 2
        if predicate(mid):
            hi = mid          # answer at mid or to the left
        else:
            lo = mid + 1      # answer strictly to the right
    return lo


# ---------------------------------------------------------------------------
# 2. Classic variants built on partition_point
# ---------------------------------------------------------------------------

def lower_bound(a, x):
    """First index i with a[i] >= x. Same as Python's bisect_left."""
    return partition_point(0, len(a), lambda i: a[i] >= x)


def upper_bound(a, x):
    """First index i with a[i] > x. Same as Python's bisect_right."""
    return partition_point(0, len(a), lambda i: a[i] > x)


def contains(a, x):
    """Standard binary search membership."""
    i = lower_bound(a, x)
    return i < len(a) and a[i] == x


def count_equal(a, x):
    """How many copies of x in sorted a?"""
    return upper_bound(a, x) - lower_bound(a, x)


def first_geq(a, x):
    """Smallest a[i] >= x, or None."""
    i = lower_bound(a, x)
    return a[i] if i < len(a) else None


def last_leq(a, x):
    """Largest a[i] <= x, or None."""
    i = upper_bound(a, x)
    return a[i - 1] if i > 0 else None


# ---------------------------------------------------------------------------
# 3. Search on answer space
# ---------------------------------------------------------------------------

def koko_min_speed(piles, h):
    """
    Koko eats bananas. Each hour she picks ONE pile and eats up to k bananas
    from it. Minimum k so she finishes all piles in <= h hours.

    Input piles aren't sorted, but feasibility(k) is monotonic in k:
    faster speed -> fewer hours.
    """
    def can_finish(k):
        return sum(ceil(p / k) for p in piles) <= h

    # Search k in [1, max(piles)]. predicate is can_finish.
    # partition_point over [1, max+1) — first k where can_finish is True.
    return partition_point(1, max(piles) + 1, can_finish)


def split_array_largest_sum(nums, k):
    """
    Split nums into k contiguous subarrays. Minimize the largest subarray sum.

    Binary search the answer (the largest sum). Feasibility: can we split
    into <= k chunks each with sum <= cap?
    """
    def feasible(cap):
        chunks, cur = 1, 0
        for x in nums:
            if x > cap:
                return False
            if cur + x > cap:
                chunks += 1
                cur = x
            else:
                cur += x
        return chunks <= k

    return partition_point(max(nums), sum(nums) + 1, feasible)


def integer_sqrt(n):
    """
    Floor of sqrt(n) via binary search. No floating point.
    Newton's method is faster in practice, but this shows the pattern.
    """
    if n < 2:
        return n
    # Find first x where (x+1)^2 > n, then return x.
    # Equivalent: partition_point on x*x > n, then subtract 1.
    i = partition_point(0, n + 1, lambda x: x * x > n)
    return i - 1


# ---------------------------------------------------------------------------
# 4. The classic broken-binary-search bug
# ---------------------------------------------------------------------------

def broken_binary_search_c_style(a, x):
    """
    Demonstration of the JDK bug fixed in 2006.

    In Python this works because ints are arbitrary precision. In C with
    32-bit ints, (lo + hi) overflows to negative when both are near INT_MAX,
    and a[mid] dereferences a negative index = undefined behavior.

    Joshua Bloch, 'Extra, Extra - Read All About It: Nearly All Binary
    Searches and Mergesorts Are Broken', Google Research, 2006.
    """
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2   # the line that overflows in C
        if a[mid] == x:
            return mid
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_variants():
    print("=" * 60)
    print("DEMO 1: lower_bound / upper_bound / counts")
    print("=" * 60)

    a = [1, 2, 4, 4, 4, 5, 7, 9]
    print(f"\narray: {a}")
    print(f"  lower_bound(4) = {lower_bound(a, 4)}  (first index with value >= 4)")
    print(f"  upper_bound(4) = {upper_bound(a, 4)}  (first index with value > 4)")
    print(f"  count_equal(4) = {count_equal(a, 4)}")
    print(f"  first_geq(6)   = {first_geq(a, 6)}")
    print(f"  last_leq(6)    = {last_leq(a, 6)}")
    print(f"  contains(3)    = {contains(a, 3)}")


def demo_answer_space():
    print("\n" + "=" * 60)
    print("DEMO 2: Search on answer space")
    print("=" * 60)

    piles = [3, 6, 7, 11]
    h = 8
    print(f"\nKoko: piles={piles}, h={h}")
    print(f"  min speed = {koko_min_speed(piles, h)} bananas/hour")

    nums = [7, 2, 5, 10, 8]
    k = 2
    print(f"\nSplit array: nums={nums}, k={k}")
    print(f"  min largest sum = {split_array_largest_sum(nums, k)}")

    for n in [0, 1, 2, 9, 10, 100, 12345]:
        print(f"  integer_sqrt({n:>5}) = {integer_sqrt(n)}")


def demo_overflow():
    print("\n" + "=" * 60)
    print("DEMO 3: The (lo + hi) // 2 overflow story")
    print("=" * 60)
    print("\nIn Python ints are arbitrary precision -> no overflow.")
    print("In C/Java with int32:")
    INT_MAX = 2**31 - 1
    lo, hi = INT_MAX - 2, INT_MAX
    mid_naive_c = ((lo + hi) % (2**32))   # wrap as if int32
    if mid_naive_c >= 2**31:
        mid_naive_c -= 2**32
    mid_safe = lo + (hi - lo) // 2
    print(f"  lo={lo}, hi={hi}")
    print(f"  (lo+hi)//2 with int32 wraparound = {mid_naive_c // 2}  (negative!)")
    print(f"  lo + (hi-lo)//2 (safe)           = {mid_safe}")


def demo_benchmark():
    print("\n" + "=" * 60)
    print("DEMO 4: Binary search vs linear scan")
    print("=" * 60)

    n = 1_000_000
    a = list(range(n))
    queries = [random.randint(0, n - 1) for _ in range(10_000)]

    t = time.perf_counter()
    for q in queries:
        lower_bound(a, q)
    bs_time = time.perf_counter() - t

    t = time.perf_counter()
    for q in queries[:100]:   # only 100, otherwise minutes
        a.index(q)
    linear_time_scaled = (time.perf_counter() - t) * 100   # extrapolate

    print(f"\nn={n}, 10k queries:")
    print(f"  binary search: {bs_time*1000:.2f} ms")
    print(f"  linear  (extrapolated): {linear_time_scaled*1000:.0f} ms")
    print(f"  speedup ~ {linear_time_scaled/bs_time:.0f}x")


if __name__ == "__main__":
    demo_variants()
    demo_answer_space()
    demo_overflow()
    demo_benchmark()
