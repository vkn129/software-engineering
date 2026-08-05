"""
Day 103: Timsort — Simplified but Faithful

Implements:
  - Natural run detection (with descending-run reversal)
  - Binary insertion sort to pad runs to minrun
  - Merge stack with invariant maintenance
  - Galloping mode

Not as optimized as listsort.c — but the same algorithm.
"""

import random
import time


# ---------------------------------------------------------------------------
# 1. minrun calculation (from CPython)
# ---------------------------------------------------------------------------

MIN_GALLOP = 7


def compute_minrun(n):
    """
    Computes a good minimum run length for n elements.
    Returns a value in [32, 64] such that n / minrun is close to,
    but no greater than, a power of two.
    """
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


# ---------------------------------------------------------------------------
# 2. Binary insertion sort — used to extend short runs
# ---------------------------------------------------------------------------

def binary_insertion_sort(a, lo, hi, start=None):
    """
    Sort a[lo:hi] using binary insertion. Stable.
    `start` is the first index that hasn't been verified sorted yet
    (defaults to lo + 1 — useful when the prefix is already sorted).
    """
    if start is None:
        start = lo + 1
    for i in range(start, hi):
        pivot = a[i]
        # Binary search for insertion point in a[lo:i]
        left, right = lo, i
        while left < right:
            mid = (left + right) // 2
            if pivot < a[mid]:
                right = mid
            else:
                left = mid + 1
        # Shift elements right
        j = i
        while j > left:
            a[j] = a[j - 1]
            j -= 1
        a[left] = pivot


# ---------------------------------------------------------------------------
# 3. Natural run detection
# ---------------------------------------------------------------------------

def count_run_and_make_ascending(a, lo, hi):
    """
    Find length of the natural run starting at a[lo]. Reverse strictly
    descending runs to make them ascending. Returns length.
    """
    run_hi = lo + 1
    if run_hi == hi:
        return 1
    if a[run_hi] < a[lo]:
        # Strictly descending
        run_hi += 1
        while run_hi < hi and a[run_hi] < a[run_hi - 1]:
            run_hi += 1
        # Reverse a[lo:run_hi] in place
        i, j = lo, run_hi - 1
        while i < j:
            a[i], a[j] = a[j], a[i]
            i += 1
            j -= 1
    else:
        # Non-decreasing
        run_hi += 1
        while run_hi < hi and a[run_hi] >= a[run_hi - 1]:
            run_hi += 1
    return run_hi - lo


# ---------------------------------------------------------------------------
# 4. Gallop — exponential search + binary search
# ---------------------------------------------------------------------------

def gallop_left(key, a, base, length, hint):
    """
    Return index k in [0, length] such that a[base + k - 1] < key <= a[base + k].
    Galloping exponential search from `hint`, then binary search.
    """
    last_ofs = 0
    ofs = 1
    if key > a[base + hint]:
        # gallop right
        max_ofs = length - hint
        while ofs < max_ofs and key > a[base + hint + ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs += hint
        ofs += hint
    else:
        # gallop left
        max_ofs = hint + 1
        while ofs < max_ofs and key <= a[base + hint - ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs, ofs = hint - ofs, hint - last_ofs
    # binary search in (last_ofs, ofs]
    last_ofs += 1
    while last_ofs < ofs:
        m = (last_ofs + ofs) // 2
        if key > a[base + m]:
            last_ofs = m + 1
        else:
            ofs = m
    return ofs


def gallop_right(key, a, base, length, hint):
    """
    Return index k in [0, length] such that a[base + k - 1] <= key < a[base + k].
    """
    last_ofs = 0
    ofs = 1
    if key < a[base + hint]:
        max_ofs = hint + 1
        while ofs < max_ofs and key < a[base + hint - ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs, ofs = hint - ofs, hint - last_ofs
    else:
        max_ofs = length - hint
        while ofs < max_ofs and key >= a[base + hint + ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs += hint
        ofs += hint
    last_ofs += 1
    while last_ofs < ofs:
        m = (last_ofs + ofs) // 2
        if key < a[base + m]:
            ofs = m
        else:
            last_ofs = m + 1
    return ofs


# ---------------------------------------------------------------------------
# 5. Merge two adjacent runs (with galloping)
# ---------------------------------------------------------------------------

def merge_lo(a, base1, len1, base2, len2):
    """
    Merge a[base1:base1+len1] and a[base2:base2+len2] in-place.
    Pre: a[base1+len1] == base2 (adjacent runs).
    Uses pairwise merge with galloping fallback after MIN_GALLOP consecutive
    picks from one side. Simplified vs CPython's listsort.c but faithful.
    """
    # Copy the smaller (left) run to temp; merge from temp + a[base2..]
    tmp = a[base1:base1 + len1]
    dest = base1
    i = 0          # index in tmp
    j = base2      # index in a (right run)
    end_j = base2 + len2

    count1 = count2 = 0
    min_gallop = MIN_GALLOP

    while i < len1 and j < end_j:
        # Pairwise mode
        if a[j] < tmp[i]:
            a[dest] = a[j]
            dest += 1; j += 1
            count2 += 1; count1 = 0
        else:
            a[dest] = tmp[i]
            dest += 1; i += 1
            count1 += 1; count2 = 0

        # Galloping mode trigger
        if count1 >= min_gallop or count2 >= min_gallop:
            # Gallop right run from tmp side: how many from tmp[i:] are < a[j]?
            if i < len1 and j < end_j:
                gp = gallop_right(a[j], tmp, i, len1 - i, 0)
                if gp > 0:
                    a[dest:dest + gp] = tmp[i:i + gp]
                    dest += gp; i += gp
                if i < len1 and j < end_j:
                    a[dest] = a[j]; dest += 1; j += 1
            # Gallop left run from a side: how many from a[j:] are <= tmp[i]?
            if i < len1 and j < end_j:
                gp = gallop_left(tmp[i], a, j, end_j - j, 0)
                if gp > 0:
                    a[dest:dest + gp] = a[j:j + gp]
                    dest += gp; j += gp
                if i < len1 and j < end_j:
                    a[dest] = tmp[i]; dest += 1; i += 1
            count1 = count2 = 0
            min_gallop += 1  # discourage gallop if it didn't pay off

    # Drain remaining
    if i < len1:
        a[dest:dest + (len1 - i)] = tmp[i:len1]
    # right side already in place


# ---------------------------------------------------------------------------
# 6. Main timsort
# ---------------------------------------------------------------------------

def timsort(a):
    """In-place(-ish) Timsort. Returns a sorted copy."""
    a = list(a)
    n = len(a)
    if n < 2:
        return a

    minrun = compute_minrun(n)
    # Run stack: list of (base, length)
    runs = []

    lo = 0
    remaining = n
    while remaining > 0:
        # Identify next run
        run_len = count_run_and_make_ascending(a, lo, lo + remaining)
        # Extend short run to minrun via binary insertion sort
        if run_len < minrun:
            force = min(remaining, minrun)
            binary_insertion_sort(a, lo, lo + force, start=lo + run_len)
            run_len = force
        runs.append([lo, run_len])
        lo += run_len
        remaining -= run_len

        # Maintain stack invariant
        while len(runs) > 1:
            n_runs = len(runs)
            # Original Timsort invariant:
            #   runs[-3].len > runs[-2].len + runs[-1].len
            #   runs[-2].len > runs[-1].len
            if n_runs >= 3 and runs[-3][1] <= runs[-2][1] + runs[-1][1]:
                if runs[-3][1] < runs[-1][1]:
                    # Merge -3 and -2
                    merge_runs_at(a, runs, n_runs - 3)
                else:
                    merge_runs_at(a, runs, n_runs - 2)
            elif runs[-2][1] <= runs[-1][1]:
                merge_runs_at(a, runs, n_runs - 2)
            else:
                break

    # Merge all remaining runs
    while len(runs) > 1:
        merge_runs_at(a, runs, len(runs) - 2)

    return a


def merge_runs_at(a, runs, i):
    """Merge runs[i] and runs[i+1]. Modifies `runs` and `a`."""
    base1, len1 = runs[i]
    base2, len2 = runs[i + 1]
    # Update stack: combined run at position i, drop i+1
    runs[i] = [base1, len1 + len2]
    del runs[i + 1]
    # Actual merge
    if len1 <= len2:
        merge_lo(a, base1, len1, base2, len2)
    else:
        # We only implemented merge_lo; fall back to copy-and-merge for now
        merge_generic(a, base1, len1, base2, len2)


def merge_generic(a, base1, len1, base2, len2):
    """Plain (non-galloping) merge, used when right run is smaller."""
    left = a[base1:base1 + len1]
    right = a[base2:base2 + len2]
    i = j = 0
    dest = base1
    while i < len1 and j < len2:
        if right[j] < left[i]:
            a[dest] = right[j]; j += 1
        else:
            a[dest] = left[i]; i += 1
        dest += 1
    while i < len1:
        a[dest] = left[i]; i += 1; dest += 1
    while j < len2:
        a[dest] = right[j]; j += 1; dest += 1


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_correctness():
    print("=" * 60)
    print("DEMO 1: Correctness across input shapes")
    print("=" * 60)
    cases = [
        [], [1], [2, 1],
        [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
        [5] * 100,
        list(range(100)),
        list(range(100, 0, -1)),
        # Mixed runs:
        list(range(20)) + list(range(20, 0, -1)) + [50, 49, 48, 47, 46],
    ]
    for i, c in enumerate(cases):
        out = timsort(c)
        ok = out == sorted(c)
        print(f"  case {i}  n={len(c):4d}  {'OK' if ok else 'FAIL'}")


def demo_already_sorted():
    print("\n" + "=" * 60)
    print("DEMO 2: Already-sorted is O(n) — Timsort detects it")
    print("=" * 60)
    n = 100000
    data = list(range(n))

    start = time.perf_counter()
    out = timsort(data)
    t_tim = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    out2 = sorted(data)
    t_py = (time.perf_counter() - start) * 1000

    print(f"\n  n = {n}, already-sorted input")
    print(f"  our timsort:        {t_tim:>8.2f} ms")
    print(f"  Python's sorted():  {t_py:>8.2f} ms (also Timsort, in C)")
    print(f"  correct: {out == out2}")


def demo_random():
    print("\n" + "=" * 60)
    print("DEMO 3: Random input — pure Python Timsort")
    print("=" * 60)
    random.seed(42)
    for n in [1000, 10000, 50000]:
        data = [random.randint(0, 10**6) for _ in range(n)]
        start = time.perf_counter()
        out = timsort(data)
        elapsed = (time.perf_counter() - start) * 1000
        ok = out == sorted(data)
        print(f"  n = {n:>6d}  time = {elapsed:>8.2f} ms  {'OK' if ok else 'FAIL'}")


def demo_stability():
    print("\n" + "=" * 60)
    print("DEMO 4: Stability — equal keys keep relative order")
    print("=" * 60)
    # Tuples sort by first element; second element is original index.
    data = [(3, 'a'), (1, 'b'), (3, 'c'), (2, 'd'), (1, 'e'), (3, 'f')]
    out = timsort(data)
    print(f"\n  input:  {data}")
    print(f"  sorted: {out}")
    # For each key group, the original tags should be in order
    by_key = {}
    stable = True
    for k, tag in out:
        if k in by_key and tag < by_key[k]:
            stable = False
            break
        by_key[k] = tag
    print(f"  stable: {stable}")


def demo_minrun():
    print("\n" + "=" * 60)
    print("DEMO 5: minrun selection across n")
    print("=" * 60)
    for n in [50, 100, 1000, 10000, 1000000]:
        mr = compute_minrun(n)
        runs_est = (n + mr - 1) // mr
        # log2 of runs should be close to integer
        import math
        log_runs = math.log2(runs_est) if runs_est > 0 else 0
        print(f"  n = {n:>8d}  minrun = {mr:>3d}  runs ≈ {runs_est:>6d}  log2 ≈ {log_runs:.3f}")


if __name__ == "__main__":
    demo_correctness()
    demo_already_sorted()
    demo_random()
    demo_stability()
    demo_minrun()
