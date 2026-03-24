"""
Day 19: Searching — Linear and Binary Search from Scratch

This script implements both search algorithms with step-by-step visualization,
comparison counting, and empirical timing. The goal is to make the theory
visceral: you will SEE binary search's logarithmic behavior in the numbers.

Why build search from scratch? Because every higher-level construct — database
indexes, routing tables, autocomplete, git bisect — is a variation on these
two ideas. You cannot reason about systems if you do not understand the
primitive they are built on.

Run: python searching.py
"""

import time
import random
import math


# ---------------------------------------------------------------------------
# Linear Search — the baseline
# ---------------------------------------------------------------------------

def linear_search(arr, target):
    """Search by examining each element in order.

    Returns (index, comparisons). Index is -1 if not found.

    Why this exists: when data is unsorted, this is your ONLY option.
    It is also optimal for small arrays because of CPU cache effects —
    sequential memory access is fast, and the overhead of maintaining
    sorted order may exceed the cost of scanning.
    """
    comparisons = 0
    for i in range(len(arr)):
        comparisons += 1
        if arr[i] == target:
            return i, comparisons
    return -1, comparisons


def linear_search_visualized(arr, target):
    """Linear search with step-by-step output."""
    print(f"\n  Linear Search for target={target} in array of size {len(arr)}")
    print(f"  Array (first 20): {arr[:20]}{'...' if len(arr) > 20 else ''}")
    print()

    comparisons = 0
    for i in range(len(arr)):
        comparisons += 1
        if len(arr) <= 20:
            # Show the scan visually
            markers = ['  '] * len(arr)
            markers[i] = '>>'
            line = ' '.join(f'{markers[j]}{arr[j]}' for j in range(len(arr)))
            status = "FOUND!" if arr[i] == target else "miss"
            print(f"    Step {comparisons}: check index {i} → {arr[i]} [{status}]")

        if arr[i] == target:
            print(f"  Result: FOUND at index {i} after {comparisons} comparisons")
            return i, comparisons

    print(f"  Result: NOT FOUND after {comparisons} comparisons (checked every element)")
    return -1, comparisons


# ---------------------------------------------------------------------------
# Binary Search — the most important algorithm in CS
# ---------------------------------------------------------------------------

def binary_search(arr, target):
    """Binary search on a sorted array.

    Returns (index, comparisons). Index is -1 if not found.

    Loop invariant: if target exists in arr, then target is in arr[lo..hi].
    Each iteration eliminates at least half the search space.

    Why lo + (hi - lo) // 2 instead of (lo + hi) // 2:
    In C/Java, (lo + hi) can overflow a 32-bit integer when both are large.
    Python has arbitrary-precision ints so it won't overflow, but writing it
    the safe way builds the right habit for every language.
    """
    lo, hi = 0, len(arr) - 1
    comparisons = 0

    while lo <= hi:
        mid = lo + (hi - lo) // 2
        comparisons += 1

        if arr[mid] == target:
            return mid, comparisons
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, comparisons


def binary_search_recursive(arr, target, lo=None, hi=None, depth=0):
    """Recursive binary search — same logic, different control flow.

    Returns (index, comparisons).

    The recursive version is often easier to reason about because each
    call has its own lo/hi on the stack, making the invariant explicit.
    The cost is O(log n) stack frames — negligible for search, but the
    iterative version is preferred in production for consistency.
    """
    if lo is None:
        lo, hi = 0, len(arr) - 1

    if lo > hi:
        return -1, 0

    mid = lo + (hi - lo) // 2

    if arr[mid] == target:
        return mid, 1
    elif arr[mid] < target:
        idx, comps = binary_search_recursive(arr, target, mid + 1, hi, depth + 1)
        return idx, comps + 1
    else:
        idx, comps = binary_search_recursive(arr, target, lo, mid - 1, depth + 1)
        return idx, comps + 1


def binary_search_visualized(arr, target):
    """Binary search with step-by-step output showing the shrinking search space."""
    print(f"\n  Binary Search for target={target} in sorted array of size {len(arr)}")
    if len(arr) <= 20:
        print(f"  Array: {arr}")
    print()

    lo, hi = 0, len(arr) - 1
    comparisons = 0

    while lo <= hi:
        mid = lo + (hi - lo) // 2
        comparisons += 1
        space_size = hi - lo + 1

        print(f"    Step {comparisons}: lo={lo}, hi={hi}, mid={mid}, "
              f"arr[mid]={arr[mid]}, search space={space_size}")

        if arr[mid] == target:
            print(f"    → arr[mid] == {target} → FOUND!")
            print(f"  Result: FOUND at index {mid} after {comparisons} comparisons")
            return mid, comparisons
        elif arr[mid] < target:
            print(f"    → {arr[mid]} < {target} → eliminate left half, set lo={mid + 1}")
            lo = mid + 1
        else:
            print(f"    → {arr[mid]} > {target} → eliminate right half, set hi={mid - 1}")
            hi = mid - 1

    print(f"    → lo ({lo}) > hi ({hi}) → search space empty")
    print(f"  Result: NOT FOUND after {comparisons} comparisons")
    return -1, comparisons


# ---------------------------------------------------------------------------
# The classic bug: off-by-one demonstration
# ---------------------------------------------------------------------------

def binary_search_buggy_v1(arr, target):
    """BUGGY: uses lo < hi instead of lo <= hi.
    Misses single-element search spaces."""
    lo, hi = 0, len(arr) - 1
    while lo < hi:  # BUG: should be lo <= hi
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def binary_search_buggy_v2(arr, target):
    """BUGGY: uses lo = mid instead of lo = mid + 1.
    Can loop forever."""
    lo, hi = 0, len(arr) - 1
    iterations = 0
    while lo <= hi:
        iterations += 1
        if iterations > 100:  # safety valve
            return -2  # indicates infinite loop detected
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid  # BUG: should be mid + 1
        else:
            hi = mid - 1
    return -1


def demonstrate_bugs():
    """Show exactly how off-by-one errors manifest in binary search."""
    print("\n" + "=" * 70)
    print("  THE CLASSIC BINARY SEARCH BUGS")
    print("=" * 70)

    # Bug 1: lo < hi misses single-element search space
    arr = [1, 3, 5, 7, 9]
    print("\n  Bug 1: lo < hi (should be lo <= hi)")
    print(f"  Array: {arr}")
    print(f"  Searching for 9 (last element)...")

    correct = binary_search(arr, 9)
    buggy = binary_search_buggy_v1(arr, 9)
    print(f"  Correct implementation: found at index {correct[0]}")
    print(f"  Buggy implementation:   found at index {buggy}")
    print(f"  → The bug misses elements that end up alone in the search space.")

    # Bug 2: lo = mid causes infinite loop
    print(f"\n  Bug 2: lo = mid (should be lo = mid + 1)")
    print(f"  Array: {arr}")
    print(f"  Searching for 4 (not present)...")

    correct = binary_search(arr, 4)
    buggy = binary_search_buggy_v2(arr, 4)
    status = "INFINITE LOOP (stopped at 100 iterations)" if buggy == -2 else f"index {buggy}"
    print(f"  Correct implementation: not found (index {correct[0]})")
    print(f"  Buggy implementation:   {status}")
    print(f"  → When lo == mid (which happens when lo + 1 == hi),")
    print(f"    setting lo = mid does not shrink the search space. Loop forever.")


# ---------------------------------------------------------------------------
# Comparison counting experiment
# ---------------------------------------------------------------------------

def comparison_experiment():
    """Empirically verify that binary search uses ~log2(n) comparisons."""
    print("\n" + "=" * 70)
    print("  COMPARISON COUNTING: Theory vs Reality")
    print("=" * 70)
    print(f"\n  {'n':>12}  {'Linear (worst)':>16}  {'Binary (worst)':>16}  {'log2(n)':>10}  {'Ratio':>8}")
    print(f"  {'-'*12}  {'-'*16}  {'-'*16}  {'-'*10}  {'-'*8}")

    sizes = [10, 100, 1_000, 10_000, 100_000, 1_000_000]

    for n in sizes:
        arr = list(range(n))

        # Worst case: search for element not present (larger than all)
        _, linear_comps = linear_search(arr, n)  # not in array
        _, binary_comps = binary_search(arr, n)  # not in array

        theoretical = math.ceil(math.log2(n + 1))

        print(f"  {n:>12,}  {linear_comps:>16,}  {binary_comps:>16}  "
              f"{theoretical:>10}  {linear_comps / max(binary_comps, 1):>8.0f}x")

    print(f"\n  Binary search uses ~log2(n) comparisons regardless of array size.")
    print(f"  For 1,000,000 elements: ~20 comparisons vs 1,000,000 for linear.")
    print(f"  That is a 50,000x improvement.")


# ---------------------------------------------------------------------------
# Timing experiment
# ---------------------------------------------------------------------------

def timing_experiment():
    """Time both algorithms across increasing input sizes."""
    print("\n" + "=" * 70)
    print("  TIMING: Linear vs Binary Search")
    print("=" * 70)

    sizes = [1_000, 10_000, 100_000, 1_000_000, 10_000_000]

    print(f"\n  Worst case: searching for an element NOT in the array")
    print(f"\n  {'n':>12}  {'Linear (s)':>14}  {'Binary (s)':>14}  {'Speedup':>10}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*14}  {'-'*10}")

    for n in sizes:
        arr = list(range(n))
        target = n  # not in array — forces worst case

        # Time linear search
        start = time.perf_counter()
        for _ in range(3):
            linear_search(arr, target)
        linear_time = (time.perf_counter() - start) / 3

        # Time binary search
        start = time.perf_counter()
        for _ in range(10000):
            binary_search(arr, target)
        binary_time = (time.perf_counter() - start) / 10000

        speedup = linear_time / binary_time if binary_time > 0 else float('inf')

        print(f"  {n:>12,}  {linear_time:>14.6f}  {binary_time:>14.8f}  {speedup:>10,.0f}x")

    print(f"\n  Notice: binary search time barely changes as n grows by 10x each step.")
    print(f"  That is the power of O(log n) — doubling n adds only ONE more step.")


# ---------------------------------------------------------------------------
# When linear search beats binary search
# ---------------------------------------------------------------------------

def small_array_crossover():
    """Demonstrate that linear search can beat binary search on small arrays."""
    print("\n" + "=" * 70)
    print("  CROSSOVER POINT: When Does Binary Search Become Faster?")
    print("=" * 70)
    print(f"\n  For small arrays, linear search benefits from sequential cache access")
    print(f"  and lower per-iteration overhead. Let's find the crossover point.\n")

    for n in [2, 4, 8, 16, 32, 64, 128, 256]:
        arr = list(range(n))
        target = n  # worst case — not found
        iterations = 100_000

        start = time.perf_counter()
        for _ in range(iterations):
            linear_search(arr, target)
        linear_time = (time.perf_counter() - start)

        start = time.perf_counter()
        for _ in range(iterations):
            binary_search(arr, target)
        binary_time = (time.perf_counter() - start)

        winner = "LINEAR" if linear_time < binary_time else "BINARY"
        ratio = linear_time / binary_time if binary_time > 0 else 0

        print(f"    n={n:>4}  linear={linear_time:.4f}s  binary={binary_time:.4f}s  "
              f"ratio={ratio:.2f}  winner={winner}")

    print(f"\n  The crossover varies by hardware, but typically around n=16-64.")
    print(f"  This is why real-world search implementations (like B-trees) use")
    print(f"  linear search within individual nodes.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("  Day 19: Searching — Linear and Binary Search from Scratch")
    print("=" * 70)

    # --- Step-by-step visualizations ---
    print("\n" + "=" * 70)
    print("  STEP-BY-STEP VISUALIZATION")
    print("=" * 70)

    small = [2, 5, 8, 11, 14, 17, 20, 23, 26, 29]

    # Linear search — found
    linear_search_visualized(small, 17)

    # Linear search — not found
    linear_search_visualized(small, 12)

    # Binary search — found
    binary_search_visualized(small, 17)

    # Binary search — not found
    binary_search_visualized(small, 12)

    # Binary search on larger array
    medium = list(range(0, 100, 3))  # [0, 3, 6, 9, ..., 99]
    binary_search_visualized(medium, 72)

    # --- The classic bugs ---
    demonstrate_bugs()

    # --- Recursive vs iterative comparison ---
    print("\n" + "=" * 70)
    print("  RECURSIVE vs ITERATIVE — Same Results")
    print("=" * 70)
    test_arr = list(range(0, 1000, 7))
    for target in [0, 350, 700, 999, 42]:
        idx_iter, comp_iter = binary_search(test_arr, target)
        idx_rec, comp_rec = binary_search_recursive(test_arr, target)
        print(f"  target={target:>4}  iterative=(idx={idx_iter:>4}, comps={comp_iter:>2})  "
              f"recursive=(idx={idx_rec:>4}, comps={comp_rec:>2})")

    # --- Comparison counting ---
    comparison_experiment()

    # --- Timing ---
    timing_experiment()

    # --- Small array crossover ---
    small_array_crossover()

    print("\n" + "=" * 70)
    print("  KEY TAKEAWAYS")
    print("=" * 70)
    print("""
  1. Linear search: O(n). Only option for unsorted data. Cache-friendly.
  2. Binary search: O(log n). Requires sorted data. Eliminates half each step.
  3. The loop invariant is everything: "target is in arr[lo..hi]."
  4. Off-by-one errors are the #1 source of binary search bugs.
  5. For small n, linear search wins due to lower constant factors.
  6. For large n, binary search is ~50,000x faster at n=1,000,000.
  7. Each doubling of n adds only ONE more comparison to binary search.
    """)
