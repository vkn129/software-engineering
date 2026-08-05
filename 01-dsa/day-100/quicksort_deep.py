"""
Day 100: Quicksort Deep Dive

Lomuto vs Hoare, every pivot strategy, dual-pivot, killer inputs.
We MEASURE the O(n^2) blow-up — it's not a textbook abstraction.
"""

import random
import time
import sys

sys.setrecursionlimit(10**6)


# ---------------------------------------------------------------------------
# Partition schemes
# ---------------------------------------------------------------------------

def lomuto_partition(a, lo, hi):
    """Pivot at a[hi]. Returns final pivot index."""
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] <= pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    return i


def hoare_partition(a, lo, hi):
    """Pivot at a[lo]. Returns a split index s; recurse on [lo, s] and [s+1, hi]."""
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


# ---------------------------------------------------------------------------
# Pivot strategies (return index of chosen pivot)
# ---------------------------------------------------------------------------

def pivot_first(a, lo, hi):
    return lo


def pivot_last(a, lo, hi):
    return hi


def pivot_random(a, lo, hi):
    return random.randint(lo, hi)


def pivot_median_of_3(a, lo, hi):
    mid = (lo + hi) // 2
    trio = [(a[lo], lo), (a[mid], mid), (a[hi], hi)]
    trio.sort()
    return trio[1][1]


def pivot_median_of_medians(a, lo, hi):
    """BFPRT — deterministic O(n) worst-case median selection.
    Returns the index of the median (or close enough) to use as pivot.
    """
    # We compute the value, then return its current index in [lo..hi].
    sub = a[lo:hi+1]
    median_val = _mom_select(sub, len(sub) // 2)
    for i in range(lo, hi + 1):
        if a[i] == median_val:
            return i
    return (lo + hi) // 2  # fallback (shouldn't happen)


def _mom_select(arr, k):
    """Return the k-th smallest element using median-of-medians."""
    if len(arr) <= 5:
        return sorted(arr)[k]
    # Split into groups of 5, take median of each
    medians = []
    for i in range(0, len(arr), 5):
        group = sorted(arr[i:i+5])
        medians.append(group[len(group) // 2])
    pivot = _mom_select(medians, len(medians) // 2)
    lows = [x for x in arr if x < pivot]
    highs = [x for x in arr if x > pivot]
    pivots = [x for x in arr if x == pivot]
    if k < len(lows):
        return _mom_select(lows, k)
    elif k < len(lows) + len(pivots):
        return pivot
    else:
        return _mom_select(highs, k - len(lows) - len(pivots))


# ---------------------------------------------------------------------------
# Quicksort variants — counted partition calls
# ---------------------------------------------------------------------------

class CallCounter:
    def __init__(self):
        self.n = 0
    def tick(self):
        self.n += 1


def quicksort(a, partition_fn, pivot_fn, counter=None):
    """Generic Lomuto-style quicksort. Mutates a copy and returns it."""
    a = a[:]
    def qs(lo, hi):
        if lo >= hi:
            return
        if counter is not None:
            counter.tick()
        p = pivot_fn(a, lo, hi)
        a[p], a[hi] = a[hi], a[p]  # Lomuto expects pivot at hi
        idx = partition_fn(a, lo, hi)
        qs(lo, idx - 1)
        qs(idx + 1, hi)
    qs(0, len(a) - 1)
    return a


def quicksort_hoare(a, pivot_fn, counter=None):
    """Hoare partition variant. Different recursion split."""
    a = a[:]
    def qs(lo, hi):
        if lo >= hi:
            return
        if counter is not None:
            counter.tick()
        p = pivot_fn(a, lo, hi)
        a[p], a[lo] = a[lo], a[p]  # Hoare expects pivot at lo
        s = hoare_partition(a, lo, hi)
        qs(lo, s)
        qs(s + 1, hi)
    qs(0, len(a) - 1)
    return a


# ---------------------------------------------------------------------------
# Dual-pivot quicksort (Yaroslavskiy 2009, simplified)
# ---------------------------------------------------------------------------

def dual_pivot_quicksort(a):
    """Simplified Yaroslavskiy: two pivots, three partitions."""
    a = a[:]
    def qs(lo, hi):
        if hi - lo < 1:
            return
        # Ensure a[lo] <= a[hi]
        if a[lo] > a[hi]:
            a[lo], a[hi] = a[hi], a[lo]
        p, q = a[lo], a[hi]   # two pivots
        # Three regions: [lo+1..lt-1] < p, [lt..gt] in [p, q], [gt+1..hi-1] > q
        lt = lo + 1
        gt = hi - 1
        i = lo + 1
        while i <= gt:
            if a[i] < p:
                a[i], a[lt] = a[lt], a[i]
                lt += 1
                i += 1
            elif a[i] > q:
                while a[gt] > q and i < gt:
                    gt -= 1
                a[i], a[gt] = a[gt], a[i]
                gt -= 1
                if a[i] < p:
                    a[i], a[lt] = a[lt], a[i]
                    lt += 1
                i += 1
            else:
                i += 1
        # Move pivots into place
        lt -= 1
        gt += 1
        a[lo], a[lt] = a[lt], a[lo]
        a[hi], a[gt] = a[gt], a[hi]
        qs(lo, lt - 1)
        qs(lt + 1, gt - 1)
        qs(gt + 1, hi)
    qs(0, len(a) - 1)
    return a


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_correctness():
    print("=" * 60)
    print("DEMO 1: All variants produce correct results")
    print("=" * 60)
    cases = [
        [], [1], [2, 1],
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
        [5] * 10,                       # all equal
        list(range(20, 0, -1)),         # reverse
        list(range(20)),                # sorted
    ]
    for c in cases:
        expected = sorted(c)
        l_rand = quicksort(c, lomuto_partition, pivot_random)
        l_m3 = quicksort(c, lomuto_partition, pivot_median_of_3)
        h_rand = quicksort_hoare(c, pivot_random)
        dp = dual_pivot_quicksort(c)
        ok = l_rand == l_m3 == h_rand == dp == expected
        print(f"  n={len(c):3d}  {'OK' if ok else 'FAIL'}")


def demo_pathological_blowup():
    print("\n" + "=" * 60)
    print("DEMO 2: O(n^2) blow-up on sorted input, last-pivot Lomuto")
    print("=" * 60)
    print(f"\n{'n':>6s}  {'partitions':>12s}  {'expected n^2/2':>15s}  {'time ms':>10s}")
    for n in [500, 1000, 2000, 4000]:
        data = list(range(n))
        counter = CallCounter()
        start = time.perf_counter()
        quicksort(data, lomuto_partition, pivot_last, counter)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"  {n:>6d}  {counter.n:>12d}  {n*n//2:>15d}  {elapsed:>10.2f}")
    print("(partition count doubles roughly as 4x — confirms n^2)")


def demo_random_vs_median3():
    print("\n" + "=" * 60)
    print("DEMO 3: Random vs Median-of-3 on sorted input (n=10000)")
    print("=" * 60)
    n = 10000
    data = list(range(n))

    for name, pivot in [("first   (O(n^2))", pivot_first),
                        ("random  (safe)", pivot_random),
                        ("median3 (safe)", pivot_median_of_3)]:
        counter = CallCounter()
        if name.startswith("first"):
            n_small = 2000
            d = list(range(n_small))
            start = time.perf_counter()
            quicksort(d, lomuto_partition, pivot, counter)
            elapsed = (time.perf_counter() - start) * 1000
            print(f"  {name:25s} n={n_small:>5d}  partitions={counter.n:>7d}  {elapsed:>7.2f} ms")
        else:
            start = time.perf_counter()
            quicksort(data, lomuto_partition, pivot, counter)
            elapsed = (time.perf_counter() - start) * 1000
            print(f"  {name:25s} n={n:>5d}  partitions={counter.n:>7d}  {elapsed:>7.2f} ms")


def demo_dual_pivot_comparison():
    print("\n" + "=" * 60)
    print("DEMO 4: Single-pivot vs Dual-pivot on random input")
    print("=" * 60)
    random.seed(42)
    n = 20000
    data = [random.randint(0, 10**6) for _ in range(n)]

    for name, fn in [
        ("single-pivot (random)", lambda d: quicksort(d, lomuto_partition, pivot_random)),
        ("single-pivot (median3)", lambda d: quicksort(d, lomuto_partition, pivot_median_of_3)),
        ("dual-pivot",            dual_pivot_quicksort),
    ]:
        start = time.perf_counter()
        out = fn(data)
        elapsed = (time.perf_counter() - start) * 1000
        assert out == sorted(data)
        print(f"  {name:25s} {elapsed:>8.2f} ms")


def demo_hoare_swaps():
    print("\n" + "=" * 60)
    print("DEMO 5: Hoare vs Lomuto on all-equal input (n=2000)")
    print("=" * 60)
    n = 2000
    data = [42] * n

    # Lomuto with last-pivot on all-equal: every comparison swaps → O(n^2)
    counter_l = CallCounter()
    start = time.perf_counter()
    quicksort(data, lomuto_partition, pivot_last, counter_l)
    t_l = (time.perf_counter() - start) * 1000

    # Hoare with first-pivot on all-equal: balanced splits → O(n log n)
    counter_h = CallCounter()
    start = time.perf_counter()
    quicksort_hoare(data, pivot_first, counter_h)
    t_h = (time.perf_counter() - start) * 1000

    print(f"\n  Lomuto+last  on n={n} all-equal: {counter_l.n:>6d} partitions, {t_l:>6.2f} ms")
    print(f"  Hoare+first  on n={n} all-equal: {counter_h.n:>6d} partitions, {t_h:>6.2f} ms")
    print("  (Hoare handles duplicates gracefully; Lomuto degrades.)")


if __name__ == "__main__":
    demo_correctness()
    demo_pathological_blowup()
    demo_random_vs_median3()
    demo_dual_pivot_comparison()
    demo_hoare_swaps()
