"""
Day 7 Practice: Benchmark and Analyze 5 Algorithms

For each exercise:
1. Read the algorithm
2. Predict its complexity (write your prediction in the TODO comment)
3. Fill in the benchmark code to measure it
4. Run this file to see if reality matches your prediction
5. Explain any discrepancies

The benchmark framework from benchmark_suite.py is reimplemented here
in minimal form so this file is self-contained.

Run: python practice.py
"""

import time
import math
import random


# ---------------------------------------------------------------------------
# Minimal benchmark utilities (self-contained)
# ---------------------------------------------------------------------------

def measure(func, input_gen, sizes, trials=5):
    """Time a function across sizes, return list of (n, median_time)."""
    results = []
    for n in sizes:
        times = []
        for _ in range(trials):
            data = input_gen(n)
            start = time.perf_counter()
            func(data)
            elapsed = time.perf_counter() - start
            times.append(elapsed)
        times.sort()
        results.append((n, times[len(times) // 2]))
    return results


def doubling_ratios(results):
    """Compute T(n2)/T(n1) ratios for consecutive measurements."""
    ratios = []
    for i in range(1, len(results)):
        n1, t1 = results[i - 1]
        n2, t2 = results[i]
        if t1 > 0:
            ratio = t2 / t1
            size_ratio = n2 / n1
            k = math.log(ratio) / math.log(size_ratio) if ratio > 0 and size_ratio > 1 else 0
            ratios.append((n1, n2, ratio, k))
    return ratios


def format_time(s):
    if s < 1e-6:
        return f"{s*1e9:.0f}ns"
    elif s < 1e-3:
        return f"{s*1e6:.0f}us"
    elif s < 1:
        return f"{s*1e3:.1f}ms"
    return f"{s:.2f}s"


def print_analysis(name, results, ratios, expected_k):
    """Print benchmark results with analysis."""
    print(f"\n  {'n':>8} | {'Time':>12} | {'Ratio':>8} | {'Implied k':>10}")
    print(f"  {'-' * 46}")
    ratio_map = {r[0]: (r[2], r[3]) for r in ratios}
    for n, t in results:
        if n in ratio_map:
            r, k = ratio_map[n]
            print(f"  {n:>8} | {format_time(t):>12} | {r:>8.2f} | {k:>10.2f}")
        else:
            print(f"  {n:>8} | {format_time(t):>12} | {'—':>8} | {'—':>10}")

    observed_ks = [r[3] for r in ratios if r[3] > 0]
    if observed_ks:
        observed_ks.sort()
        median_k = observed_ks[len(observed_ks) // 2]
        print(f"\n  Expected k (exponent): {expected_k}")
        print(f"  Observed k (median):   {median_k:.2f}")
        if abs(median_k - expected_k) < 0.5:
            print(f"  MATCH: Theory matches reality!")
        else:
            print(f"  MISMATCH: Observed k differs from expected.")
            print(f"  Think about why this might be the case.")


def random_array(n):
    return [random.randint(0, n * 10) for _ in range(n)]

def sorted_array(n):
    return list(range(n))

def reversed_array(n):
    return list(range(n, 0, -1))


# ---------------------------------------------------------------------------
# Exercise 1: Selection Sort — Predict and Verify
# ---------------------------------------------------------------------------
# ALGORITHM: Find the minimum of the unsorted portion, swap it to the front.
# Repeat for each position.
#
# TODO: What is the complexity?
# Your prediction: O(???)
# Reasoning: ???

def selection_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


def test_exercise_1():
    print("=" * 60)
    print("Exercise 1: Selection Sort")
    print("=" * 60)

    # TODO: Fill in the expected exponent k where T(n) ~ n^k
    # For O(n^2), k = 2. For O(n log n), k ~ 1. For O(n), k = 1.
    expected_k = 0  # TODO: Replace 0 with your prediction

    sizes = [500, 1000, 2000, 4000, 8000]
    results = measure(selection_sort, random_array, sizes, trials=3)
    ratios = doubling_ratios(results)
    print_analysis("Selection Sort", results, ratios, expected_k)

    # TODO: Answer these questions in comments:
    # Q1: Does selection sort's performance change with input order?
    #     (Try: replace random_array with sorted_array or reversed_array)
    # Q2: How does selection sort compare to insertion sort on random input?
    # Q3: Selection sort always does exactly n*(n-1)/2 comparisons regardless
    #     of input. Why is this? (Hint: look at the inner loop.)
    print()


# ---------------------------------------------------------------------------
# Exercise 2: Two Sum (Brute Force vs Sort+Search)
# ---------------------------------------------------------------------------
# Compare two approaches to the same problem.
#
# TODO: Predict complexity of each approach.
# Brute force: O(???)
# Sort + binary search: O(???)

def two_sum_brute(arr):
    """Find if any two elements sum to a target. Brute force."""
    target = -1  # Force worst case (not found)
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] + arr[j] == target:
                return (i, j)
    return None


def two_sum_sorted(arr):
    """Find if any two elements sum to a target. Sort + two pointers."""
    target = -1  # Force worst case (not found)
    sorted_arr = sorted(arr)
    lo, hi = 0, len(sorted_arr) - 1
    while lo < hi:
        s = sorted_arr[lo] + sorted_arr[hi]
        if s == target:
            return (lo, hi)
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return None


def test_exercise_2():
    print("=" * 60)
    print("Exercise 2: Two Sum — Brute Force vs Sort+Search")
    print("=" * 60)

    # TODO: Fill in expected exponents
    expected_k_brute = 0   # TODO: Replace with your prediction
    expected_k_sorted = 0  # TODO: Replace with your prediction

    sizes = [500, 1000, 2000, 4000, 8000]

    print("\n  --- Brute Force ---")
    results_brute = measure(two_sum_brute, random_array, sizes, trials=3)
    ratios_brute = doubling_ratios(results_brute)
    print_analysis("Two Sum (brute)", results_brute, ratios_brute, expected_k_brute)

    print("\n  --- Sort + Two Pointers ---")
    results_sorted = measure(two_sum_sorted, random_array, sizes, trials=3)
    ratios_sorted = doubling_ratios(results_sorted)
    print_analysis("Two Sum (sorted)", results_sorted, ratios_sorted, expected_k_sorted)

    # Speedup
    print("\n  Speedup comparison:")
    for (n1, t1), (n2, t2) in zip(results_brute, results_sorted):
        speedup = t1 / t2 if t2 > 0 else float('inf')
        print(f"  n={n1:>6}: brute={format_time(t1):>10}, sorted={format_time(t2):>10}, speedup={speedup:.1f}x")

    # TODO: Answer in comments:
    # Q1: At what n does the speedup become dramatic?
    # Q2: The sorted approach includes sorting (O(n log n)) + scanning (O(n)).
    #     Why is the observed k closer to 1 than to 2?
    print()


# ---------------------------------------------------------------------------
# Exercise 3: Has Duplicate — Three Approaches
# ---------------------------------------------------------------------------
# Check if an array contains any duplicate element.
#
# TODO: Predict complexity of each approach.

def has_duplicate_brute(arr):
    """O(???) — compare every pair."""
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            if arr[i] == arr[j]:
                return True
    return False


def has_duplicate_sort(arr):
    """O(???) — sort, then check adjacent elements."""
    sorted_arr = sorted(arr)
    for i in range(1, len(sorted_arr)):
        if sorted_arr[i] == sorted_arr[i - 1]:
            return True
    return False


def has_duplicate_set(arr):
    """O(???) — use a hash set. (This uses Python's built-in set,
    which is a hash table. We include it to show the power of
    hashing, which you will study in depth later.)"""
    seen = set()
    for x in arr:
        if x in seen:
            return True
        seen.add(x)
    return False


def unique_array(n):
    """Generate array with all unique elements (worst case for duplicate check)."""
    return list(range(n))


def test_exercise_3():
    print("=" * 60)
    print("Exercise 3: Has Duplicate — Three Approaches")
    print("=" * 60)

    # TODO: Fill in expected exponents for each approach
    expected_k_brute = 0  # TODO
    expected_k_sort = 0   # TODO
    expected_k_set = 0    # TODO

    sizes = [500, 1000, 2000, 4000, 8000]

    print("\n  --- Brute Force (all pairs) ---")
    results = measure(has_duplicate_brute, unique_array, sizes, trials=3)
    ratios = doubling_ratios(results)
    print_analysis("Has Duplicate (brute)", results, ratios, expected_k_brute)

    print("\n  --- Sort + Scan ---")
    results = measure(has_duplicate_sort, unique_array, sizes, trials=3)
    ratios = doubling_ratios(results)
    print_analysis("Has Duplicate (sort)", results, ratios, expected_k_sort)

    print("\n  --- Hash Set ---")
    results = measure(has_duplicate_set, unique_array, sizes, trials=3)
    ratios = doubling_ratios(results)
    print_analysis("Has Duplicate (set)", results, ratios, expected_k_set)

    # TODO: Answer in comments:
    # Q1: The hash set approach is O(n) in theory. Does the observed k match?
    # Q2: Why might the hash set approach show k slightly above 1?
    #     (Hint: think about hash collisions and memory allocation as n grows.)
    # Q3: At what n is the brute force approach roughly 100x slower than the set?
    print()


# ---------------------------------------------------------------------------
# Exercise 4: Matrix Operations — O(n^2) vs O(n^3)
# ---------------------------------------------------------------------------
# Compare operations on n x n matrices represented as lists of lists.
#
# TODO: Predict complexity.

def matrix_add(data):
    """Add two n x n matrices. TODO: What complexity?"""
    a, b = data
    n = len(a)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            result[i][j] = a[i][j] + b[i][j]
    return result


def matrix_multiply(data):
    """Multiply two n x n matrices (naive). TODO: What complexity?"""
    a, b = data
    n = len(a)
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            s = 0
            for k in range(n):
                s += a[i][k] * b[k][j]
            result[i][j] = s
    return result


def matrix_pair(n):
    """Generate a pair of random n x n matrices."""
    a = [[random.randint(0, 100) for _ in range(n)] for _ in range(n)]
    b = [[random.randint(0, 100) for _ in range(n)] for _ in range(n)]
    return (a, b)


def test_exercise_4():
    print("=" * 60)
    print("Exercise 4: Matrix Addition vs Multiplication")
    print("=" * 60)

    # IMPORTANT: n here is the matrix dimension, so the input "size"
    # is n^2 elements. But we measure T as a function of the dimension n.
    # TODO: What is k for matrix addition in terms of dimension n?
    # TODO: What is k for matrix multiplication in terms of dimension n?
    expected_k_add = 0      # TODO: Fill in (hint: n^2 elements to add)
    expected_k_multiply = 0  # TODO: Fill in (hint: three nested loops of size n)

    sizes = [10, 20, 40, 80, 160]

    print("\n  --- Matrix Addition ---")
    results = measure(matrix_add, matrix_pair, sizes, trials=3)
    ratios = doubling_ratios(results)
    print_analysis("Matrix Addition", results, ratios, expected_k_add)

    print("\n  --- Matrix Multiplication (naive) ---")
    sizes_mult = [10, 20, 40, 80, 120]  # Smaller sizes because O(n^3) is slow
    results = measure(matrix_multiply, matrix_pair, sizes_mult, trials=3)
    ratios = doubling_ratios(results)
    print_analysis("Matrix Multiplication", results, ratios, expected_k_multiply)

    # TODO: Answer in comments:
    # Q1: Strassen's algorithm does matrix multiplication in O(n^2.807).
    #     How much faster would that be for n=1000 compared to naive O(n^3)?
    # Q2: Why does the observed k for matrix add sometimes appear greater
    #     than 2? (Hint: memory allocation for the result matrix.)
    print()


# ---------------------------------------------------------------------------
# Exercise 5: The Crossover Experiment
# ---------------------------------------------------------------------------
# Find the EXACT input size where merge sort becomes faster than insertion sort.
# This demonstrates that big-O is about ASYMPTOTIC behavior — for small inputs,
# the "worse" algorithm can win.

def test_exercise_5():
    print("=" * 60)
    print("Exercise 5: Find the Crossover Point")
    print("=" * 60)
    print()
    print("  At what n does merge sort become consistently faster than")
    print("  insertion sort? This is the crossover point.")
    print()

    def insertion_sort_bench(arr):
        arr = arr[:]
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            while j >= 0 and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        return arr

    def merge_sort_bench(arr):
        if len(arr) <= 1:
            return arr[:]
        mid = len(arr) // 2
        left = merge_sort_bench(arr[:mid])
        right = merge_sort_bench(arr[mid:])
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result.extend(left[i:])
        result.extend(right[j:])
        return result

    # TODO: Adjust sizes to zoom in on the crossover point.
    # Start with a broad range, then narrow down.
    sizes = [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300, 500]

    results_insert = measure(insertion_sort_bench, random_array, sizes, trials=7)
    results_merge = measure(merge_sort_bench, random_array, sizes, trials=7)

    print(f"  {'n':>6} | {'Insertion':>12} | {'Merge':>12} | {'Faster':>10} | {'Ratio I/M':>10}")
    print(f"  {'-' * 56}")

    crossover = None
    for (n1, t1), (n2, t2) in zip(results_insert, results_merge):
        faster = "insertion" if t1 <= t2 else "merge"
        ratio = t1 / t2 if t2 > 0 else float('inf')
        marker = " <-- crossover?" if crossover is None and faster == "merge" else ""
        if faster == "merge" and crossover is None:
            crossover = n1
        print(f"  {n1:>6} | {format_time(t1):>12} | {format_time(t2):>12} | {faster:>10} | {ratio:>10.2f}{marker}")

    if crossover:
        print(f"\n  Approximate crossover point: n ~ {crossover}")
    else:
        print(f"\n  No crossover found in this range — insertion sort may be faster throughout.")

    # TODO: Answer in comments:
    # Q1: Why does insertion sort win for small n?
    #     (Hint: think about the overhead of recursion and list slicing in merge sort.)
    # Q2: If you were implementing a production sort (like Timsort), how would
    #     you use this crossover point?
    # Q3: Does the crossover point change if you use sorted_array instead of
    #     random_array? Why?
    print()


# ---------------------------------------------------------------------------
# Solutions (expected k values)
# ---------------------------------------------------------------------------
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# SOLUTIONS BELOW — TRY THE EXERCISES FIRST!
#
#
#
#
#
#
#
#
#
#

# Exercise 1: Selection Sort
#   k = 2 (O(n^2) — always exactly n*(n-1)/2 comparisons regardless of input)
#   Does NOT vary with input order — the inner loop always runs fully.

# Exercise 2: Two Sum
#   Brute force: k = 2 (O(n^2) — nested loop over all pairs)
#   Sort + search: k ≈ 1.0-1.3 (O(n log n) dominated by sorting)

# Exercise 3: Has Duplicate
#   Brute force: k = 2 (O(n^2))
#   Sort + scan: k ≈ 1.0-1.3 (O(n log n))
#   Hash set: k ≈ 1.0 (O(n) expected)

# Exercise 4: Matrix Operations (n = matrix dimension)
#   Matrix add: k = 2 (O(n^2) — two nested loops)
#   Matrix multiply: k = 3 (O(n^3) — three nested loops)

# Exercise 5: Crossover Point
#   Typically around n = 20-60 on Python, depending on hardware.
#   Insertion sort wins below this due to lower constant factors:
#   no recursion overhead, no list slicing, simple inner loop.


# ---------------------------------------------------------------------------
# Run all exercises
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)

    print("=" * 60)
    print("DAY 7 PRACTICE: Benchmark and Analyze 5 Algorithms")
    print("=" * 60)
    print()
    print("Fill in the TODO predictions, then run to verify.")
    print("Compare your predicted k (exponent) with the observed k.")
    print()

    test_exercise_1()
    test_exercise_2()
    test_exercise_3()
    test_exercise_4()
    test_exercise_5()

    print("=" * 60)
    print("Check the solutions at the bottom of this file to see")
    print("the expected k values and explanations.")
    print("=" * 60)
