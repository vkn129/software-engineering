"""
Day 101: Non-Comparison Sorts — Counting, Radix (LSD/MSD), Bucket

Each algorithm breaks the Omega(n log n) lower bound by exploiting structure
in the keys (integer range, fixed-width digits, uniform distribution).
"""

import random
import time


# ---------------------------------------------------------------------------
# 1. Counting Sort
# ---------------------------------------------------------------------------

def counting_sort(a, k=None):
    """
    Sort non-negative integers in [0, k) in O(n + k) time.
    If k is None, set k = max(a) + 1.
    Stable: equal elements keep their input order.
    """
    if not a:
        return []
    if k is None:
        k = max(a) + 1

    count = [0] * k
    for x in a:
        count[x] += 1

    # Prefix sums → count[i] = number of elements <= i
    for i in range(1, k):
        count[i] += count[i - 1]

    out = [0] * len(a)
    # Iterate in reverse for stability
    for x in reversed(a):
        count[x] -= 1
        out[count[x]] = x
    return out


# ---------------------------------------------------------------------------
# 2. LSD Radix Sort
# ---------------------------------------------------------------------------

def radix_sort_lsd(a, base=10):
    """
    LSD radix sort for non-negative integers. base=10 is human-friendly;
    real systems use base=256 (byte-by-byte) for speed.
    """
    if not a:
        return []

    out = list(a)
    max_val = max(out)
    exp = 1
    while max_val // exp > 0:
        out = _counting_sort_by_digit(out, exp, base)
        exp *= base
    return out


def _counting_sort_by_digit(a, exp, base):
    """Stable counting sort using digit at position `exp` (base `base`)."""
    n = len(a)
    out = [0] * n
    count = [0] * base
    for x in a:
        count[(x // exp) % base] += 1
    for i in range(1, base):
        count[i] += count[i - 1]
    for x in reversed(a):  # reverse → stable
        d = (x // exp) % base
        count[d] -= 1
        out[count[d]] = x
    return out


# ---------------------------------------------------------------------------
# 3. MSD Radix Sort (works on variable-length strings)
# ---------------------------------------------------------------------------

def radix_sort_msd(strings):
    """MSD radix sort on lowercase ASCII strings."""
    if len(strings) <= 1:
        return list(strings)
    return _msd(list(strings), 0)


def _msd(a, d):
    """Recursively sort by character d. Strings shorter than d sort first."""
    if len(a) <= 1:
        return a
    # 26 letters + 1 "end-of-string" bucket
    buckets = [[] for _ in range(27)]
    for s in a:
        if d >= len(s):
            buckets[0].append(s)
        else:
            buckets[ord(s[d]) - ord('a') + 1].append(s)

    out = buckets[0]  # shorter strings already at right position
    for i in range(1, 27):
        if buckets[i]:
            out = out + _msd(buckets[i], d + 1)
    return out


# ---------------------------------------------------------------------------
# 4. Bucket Sort
# ---------------------------------------------------------------------------

def bucket_sort(a, n_buckets=None):
    """
    Bucket sort for floats in [0, 1). O(n) expected with uniform distribution,
    O(n^2) worst case when all keys land in one bucket.
    """
    if not a:
        return []
    if n_buckets is None:
        n_buckets = len(a)

    buckets = [[] for _ in range(n_buckets)]
    for x in a:
        # Clamp to last bucket for x = 1.0 edge case
        idx = min(int(x * n_buckets), n_buckets - 1)
        buckets[idx].append(x)

    out = []
    for b in buckets:
        _insertion_sort(b)
        out.extend(b)
    return out


def _insertion_sort(b):
    """In-place insertion sort — fast on small arrays."""
    for i in range(1, len(b)):
        v = b[i]
        j = i - 1
        while j >= 0 and b[j] > v:
            b[j + 1] = b[j]
            j -= 1
        b[j + 1] = v


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_counting():
    print("=" * 60)
    print("DEMO 1: Counting sort")
    print("=" * 60)
    a = [2, 5, 3, 0, 2, 3, 0, 3]
    out = counting_sort(a, k=6)
    print(f"\n  input:  {a}")
    print(f"  output: {out}")
    print(f"  correct: {out == sorted(a)}")


def demo_radix_lsd():
    print("\n" + "=" * 60)
    print("DEMO 2: LSD radix sort")
    print("=" * 60)
    a = [170, 45, 75, 90, 802, 24, 2, 66]
    out = radix_sort_lsd(a, base=10)
    print(f"\n  input:  {a}")
    print(f"  output: {out}")
    print(f"  correct: {out == sorted(a)}")


def demo_radix_msd():
    print("\n" + "=" * 60)
    print("DEMO 3: MSD radix sort on strings")
    print("=" * 60)
    words = ["she", "sells", "seashells", "by", "the", "seashore", "she", "sea"]
    out = radix_sort_msd(words)
    print(f"\n  input:  {words}")
    print(f"  output: {out}")
    print(f"  correct: {out == sorted(words)}")


def demo_bucket():
    print("\n" + "=" * 60)
    print("DEMO 4: Bucket sort on floats")
    print("=" * 60)
    random.seed(7)
    a = [random.random() for _ in range(15)]
    out = bucket_sort(a)
    print(f"\n  n={len(a)}, sample={a[:3]}")
    print(f"  sorted correctly: {out == sorted(a)}")


def demo_radix_beats_quicksort():
    print("\n" + "=" * 60)
    print("DEMO 5: Radix vs quicksort on 32-bit ints (n=100000)")
    print("=" * 60)
    random.seed(42)
    n = 100000
    data = [random.randint(0, 2**31 - 1) for _ in range(n)]

    start = time.perf_counter()
    out_radix = radix_sort_lsd(data, base=256)
    t_radix = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    out_python = sorted(data)
    t_python = (time.perf_counter() - start) * 1000

    print(f"\n  n = {n}, 32-bit ints, base=256 (4 passes)")
    print(f"  radix_sort_lsd (pure Python):   {t_radix:>8.2f} ms")
    print(f"  sorted()       (C Timsort):     {t_python:>8.2f} ms")
    print(f"  correct: {out_radix == out_python}")
    print("\n  Note: Python sorted() is in C; pure-Python radix loses on absolute")
    print("  time but has lower asymptotic count (~4n vs n log n ~= 17n).")
    print("  In C-speed contexts (numpy.argsort, DuckDB), radix wins by 3-5x.")


def demo_bucket_pathological():
    print("\n" + "=" * 60)
    print("DEMO 6: Bucket sort pathological case (all same key)")
    print("=" * 60)
    n = 5000
    a_uniform = [random.random() for _ in range(n)]
    a_clustered = [0.5] * n   # all in bucket n/2 → insertion sort O(n^2)

    random.seed(42)
    start = time.perf_counter()
    bucket_sort(a_uniform)
    t_uniform = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    bucket_sort(a_clustered)
    t_clustered = (time.perf_counter() - start) * 1000

    print(f"\n  n = {n}")
    print(f"  uniform   distribution: {t_uniform:>8.2f} ms  (expected O(n))")
    print(f"  all-equal (pathological): {t_clustered:>8.2f} ms  (degrades to O(n^2))")
    print(f"  slowdown: {t_clustered/t_uniform:.1f}x")


if __name__ == "__main__":
    demo_counting()
    demo_radix_lsd()
    demo_radix_msd()
    demo_bucket()
    demo_radix_beats_quicksort()
    demo_bucket_pathological()
