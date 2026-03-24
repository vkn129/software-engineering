"""
Day 1: Complexity Basics — Empirical Measurement of Growth Rates

This script defines functions of known complexity classes, times them
across increasing input sizes, and prints a comparison table. The goal
is to build intuition: when you SEE the numbers double, quadruple, or
explode, the theory becomes real.

Run: python complexity_basics.py
"""

import time
import random
import math


# ---------------------------------------------------------------------------
# Functions of known complexity classes
# ---------------------------------------------------------------------------

def constant_time(arr):
    """O(1) — always does the same amount of work regardless of input size."""
    if len(arr) > 0:
        return arr[0]
    return None


def logarithmic_time(arr):
    """O(log n) — binary search on a sorted array.
    Each iteration eliminates half the remaining search space.
    That halving is the signature of logarithmic growth."""
    target = arr[-1]  # search for last element (worst case for binary search)
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def linear_time(arr):
    """O(n) — visits every element exactly once.
    Double the input, double the time."""
    total = 0
    for x in arr:
        total += x
    return total


def n_log_n_time(arr):
    """O(n log n) — simulates merge sort's work pattern.
    We iterate n elements, and for each we do log(n) work."""
    n = len(arr)
    if n == 0:
        return 0
    log_n = int(math.log2(n)) if n > 0 else 1
    total = 0
    for i in range(n):
        for j in range(log_n):
            total += 1
    return total


def quadratic_time(arr):
    """O(n^2) — nested loop over all pairs.
    Double the input, quadruple the time. This is why naive sorting is slow."""
    n = len(arr)
    count = 0
    for i in range(n):
        for j in range(n):
            count += 1
    return count


def cubic_time(arr):
    """O(n^3) — triple nested loop. Grows devastatingly fast.
    We only test small inputs here or we'd be waiting all day."""
    n = len(arr)
    count = 0
    for i in range(n):
        for j in range(n):
            for k in range(n):
                count += 1
    return count


def exponential_time(n_val):
    """O(2^n) — counts all subsets of a set of size n.
    This is why brute-force solutions to NP-hard problems are impractical.
    Note: takes an integer, not an array, because arrays would be too large."""
    if n_val <= 0:
        return 1
    # Count by actually recursing — each call branches into two
    return exponential_time(n_val - 1) + exponential_time(n_val - 1)


# ---------------------------------------------------------------------------
# Timing utility
# ---------------------------------------------------------------------------

def time_function(func, arg, runs=3):
    """Time a function over multiple runs and return the median time.
    We use median (not mean) to reduce noise from OS scheduling jitter."""
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        func(arg)
        end = time.perf_counter()
        times.append(end - start)
    times.sort()
    return times[len(times) // 2]  # median


# ---------------------------------------------------------------------------
# Main demonstration
# ---------------------------------------------------------------------------

def print_table(name, sizes, times):
    """Print a formatted row showing times and growth ratios."""
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"{'=' * 60}")
    print(f"  {'n':>10}  {'Time (s)':>12}  {'Ratio':>8}  {'Expected Ratio':>16}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*8}  {'-'*16}")

    for i, (n, t) in enumerate(zip(sizes, times)):
        if i == 0 or times[i - 1] == 0:
            ratio_str = "—"
        else:
            ratio_str = f"{t / times[i - 1]:.2f}x"
        # Expected ratio when doubling n:
        # O(1): 1x, O(log n): ~1+, O(n): 2x, O(n log n): ~2x,
        # O(n^2): 4x, O(n^3): 8x, O(2^n): squares
        print(f"  {n:>10}  {t:>12.6f}  {ratio_str:>8}")


if __name__ == "__main__":
    print("Complexity Basics: Empirical Growth Rate Measurement")
    print("=" * 60)
    print("We time each complexity class at increasing input sizes")
    print("and observe how the ratios match theoretical predictions.")
    print()
    print("KEY INSIGHT: When you double n...")
    print("  O(1)       -> time stays ~same    (ratio ~1x)")
    print("  O(log n)   -> time barely grows   (ratio ~1.x)")
    print("  O(n)       -> time doubles         (ratio ~2x)")
    print("  O(n log n) -> time ~doubles        (ratio ~2x)")
    print("  O(n^2)     -> time quadruples      (ratio ~4x)")
    print("  O(n^3)     -> time octuples        (ratio ~8x)")

    # --- O(1) ---
    sizes_const = [1000, 2000, 4000, 8000, 16000]
    arrays_const = [list(range(n)) for n in sizes_const]
    times_const = [time_function(constant_time, a, runs=5) for a in arrays_const]
    print_table("O(1) — Constant Time", sizes_const, times_const)

    # --- O(log n) ---
    sizes_log = [1000, 2000, 4000, 8000, 16000]
    arrays_log = [list(range(n)) for n in sizes_log]  # already sorted
    times_log = [time_function(logarithmic_time, a, runs=5) for a in arrays_log]
    print_table("O(log n) — Logarithmic Time", sizes_log, times_log)

    # --- O(n) ---
    sizes_lin = [10000, 20000, 40000, 80000, 160000]
    arrays_lin = [list(range(n)) for n in sizes_lin]
    times_lin = [time_function(linear_time, a, runs=5) for a in arrays_lin]
    print_table("O(n) — Linear Time", sizes_lin, times_lin)

    # --- O(n log n) ---
    sizes_nlogn = [10000, 20000, 40000, 80000, 160000]
    arrays_nlogn = [list(range(n)) for n in sizes_nlogn]
    times_nlogn = [time_function(n_log_n_time, a, runs=3) for a in arrays_nlogn]
    print_table("O(n log n) — Linearithmic Time", sizes_nlogn, times_nlogn)

    # --- O(n^2) ---
    sizes_quad = [500, 1000, 2000, 4000]
    arrays_quad = [list(range(n)) for n in sizes_quad]
    times_quad = [time_function(quadratic_time, a, runs=3) for a in arrays_quad]
    print_table("O(n^2) — Quadratic Time", sizes_quad, times_quad)

    # --- O(n^3) ---
    sizes_cub = [50, 100, 200, 400]
    arrays_cub = [list(range(n)) for n in sizes_cub]
    times_cub = [time_function(cubic_time, a, runs=3) for a in arrays_cub]
    print_table("O(n^3) — Cubic Time", sizes_cub, times_cub)

    # --- O(2^n) ---
    print(f"\n{'=' * 60}")
    print(f"  O(2^n) — Exponential Time")
    print(f"{'=' * 60}")
    print(f"  {'n':>10}  {'Time (s)':>12}  {'Ratio':>8}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*8}")
    exp_sizes = [10, 12, 14, 16, 18, 20]
    prev_t = None
    for n in exp_sizes:
        t = time_function(exponential_time, n, runs=1)
        if prev_t and prev_t > 0:
            ratio_str = f"{t / prev_t:.2f}x"
        else:
            ratio_str = "—"
        print(f"  {n:>10}  {t:>12.6f}  {ratio_str:>8}")
        prev_t = t
    print("\n  Note: Each +1 to n doubles the time (ratio ~2x).")
    print("  Each +2 to n quadruples the time (ratio ~4x).")

    print("\n" + "=" * 60)
    print("EXERCISE: Add an O(n * sqrt(n)) function and measure it.")
    print("Hint: outer loop n times, inner loop int(sqrt(n)) times.")
    print("Expected ratio when doubling n: ~2 * sqrt(2) = ~2.83x")
    print("=" * 60)
