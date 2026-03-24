"""
Day 7: Mini-Project — Benchmark Suite

A from-scratch benchmarking framework that measures real algorithm performance,
compares it to theoretical complexity, and produces ASCII visualizations.

No external libraries. Everything is built from first principles.

Run: python benchmark_suite.py
"""

import time
import math
import random


# ---------------------------------------------------------------------------
# Section 1: Precision Timing
# ---------------------------------------------------------------------------
# WHY: time.time() has ~15ms resolution on some platforms. time.perf_counter()
# uses the highest-resolution clock available. We also need multiple trials
# because a single measurement includes OS scheduling noise.

def benchmark(func, input_generator, sizes, trials=5):
    """Time a function across multiple input sizes with multiple trials.

    Returns a list of (n, median_time) tuples.

    Why median instead of mean? A single OS interrupt or GC pause can make
    one trial 10x slower. The median is robust to these outliers. The mean
    would be dragged up by them, giving a misleading picture.

    Why multiple trials? Any single measurement includes noise from:
    - OS process scheduling
    - CPU cache state (cold vs warm)
    - Python garbage collection
    - CPU frequency scaling

    Multiple trials + median smooths this out.
    """
    results = []

    for n in sizes:
        times = []
        for _ in range(trials):
            # Generate fresh input each trial to avoid caching effects
            data = input_generator(n)

            # Measure only the function call, not input generation
            start = time.perf_counter()
            func(data)
            end = time.perf_counter()

            times.append(end - start)

        # Median: sort and take the middle value
        times.sort()
        median_time = times[len(times) // 2]
        results.append((n, median_time))

    return results


# ---------------------------------------------------------------------------
# Section 2: Growth Rate Analysis (Ratio Test)
# ---------------------------------------------------------------------------
# WHY: If T(n) = c * n^k, then T(2n)/T(n) = 2^k.
# This lets us empirically determine k without curve fitting.

def compute_ratios(results):
    """Compute the ratio T(n2)/T(n1) for consecutive measurements.

    Returns list of (n1, n2, ratio, implied_exponent) tuples.

    The implied exponent is log2(ratio) when sizes double, or more generally
    log(ratio) / log(n2/n1) for arbitrary size ratios.
    """
    ratios = []
    for i in range(1, len(results)):
        n1, t1 = results[i - 1]
        n2, t2 = results[i]

        if t1 > 0 and t2 > 0:
            ratio = t2 / t1
            size_ratio = n2 / n1
            # If T(n) = c * n^k, then ratio = size_ratio^k
            # So k = log(ratio) / log(size_ratio)
            if ratio > 0 and size_ratio > 1:
                implied_k = math.log(ratio) / math.log(size_ratio)
            else:
                implied_k = float('nan')
            ratios.append((n1, n2, ratio, implied_k))

    return ratios


def classify_complexity(ratios):
    """Guess the complexity class from observed growth ratios.

    Uses the median implied exponent to be robust against noise
    at small n (where constant factors dominate) or large n
    (where measurement noise increases).
    """
    if not ratios:
        return "unknown"

    exponents = [r[3] for r in ratios if not math.isnan(r[3])]
    if not exponents:
        return "unknown"

    exponents.sort()
    median_k = exponents[len(exponents) // 2]

    # Classify based on the exponent
    if median_k < 0.3:
        return "O(1) or O(log n)"
    elif median_k < 0.7:
        return "O(sqrt(n)) or O(n^0.5)"
    elif median_k < 1.3:
        return "O(n) or O(n log n)"
    elif median_k < 1.7:
        return "O(n log n) or O(n^1.5)"
    elif median_k < 2.3:
        return "O(n^2)"
    elif median_k < 2.7:
        return "O(n^2 log n) or O(n^2.5)"
    elif median_k < 3.3:
        return "O(n^3)"
    else:
        return f"O(n^{median_k:.1f})"


# ---------------------------------------------------------------------------
# Section 3: Theoretical Curve Fitting
# ---------------------------------------------------------------------------
# WHY: To overlay theory on measurement, we need to estimate the constant
# factor c in T(n) = c * f(n). We use least-squares fitting.

def fit_constant(results, complexity_func):
    """Estimate the constant c in T(n) = c * f(n).

    Uses least-squares: minimize sum of (T_measured - c * f(n))^2.
    The optimal c is: sum(T_i * f_i) / sum(f_i^2).

    This is the simplest possible curve fitting — no libraries needed.
    """
    numerator = 0.0
    denominator = 0.0

    for n, t in results:
        f_n = complexity_func(n)
        if f_n > 0:
            numerator += t * f_n
            denominator += f_n * f_n

    if denominator == 0:
        return 0.0
    return numerator / denominator


def predict(n, constant, complexity_func):
    """Predict time for input size n using T(n) = c * f(n)."""
    return constant * complexity_func(n)


# Common complexity functions
def f_constant(n):
    return 1.0

def f_log(n):
    return math.log2(max(n, 1))

def f_linear(n):
    return float(n)

def f_nlogn(n):
    return n * math.log2(max(n, 1))

def f_quadratic(n):
    return float(n * n)

def f_cubic(n):
    return float(n * n * n)


# ---------------------------------------------------------------------------
# Section 4: ASCII Plotting
# ---------------------------------------------------------------------------
# WHY: Visualization makes patterns obvious that tables of numbers hide.
# We build this from scratch because we cannot use matplotlib.

def ascii_plot(results, predictions=None, title="", width=60, height=20):
    """Render an ASCII scatter plot of timing results.

    Uses log-scale on the y-axis to handle the wide range of values
    that typical benchmark data spans (microseconds to seconds).

    Args:
        results: list of (n, time) tuples — the measured data
        predictions: optional list of (n, time) tuples — the theoretical curve
        title: plot title
        width: character width of the plot area
        height: character height of the plot area
    """
    if not results:
        print("No data to plot.")
        return

    all_data = results[:]
    if predictions:
        all_data.extend(predictions)

    # Extract ranges (use log scale for y-axis)
    ns = [n for n, t in all_data]
    ts = [t for n, t in all_data if t > 0]

    if not ts:
        print("All times are zero — nothing to plot.")
        return

    n_min, n_max = min(ns), max(ns)
    t_min, t_max = min(ts), max(ts)

    # Log scale for y-axis
    log_t_min = math.log10(t_min) if t_min > 0 else -10
    log_t_max = math.log10(t_max) if t_max > 0 else 0

    # Add margin
    log_range = log_t_max - log_t_min
    if log_range < 0.1:
        log_range = 1.0
    log_t_min -= log_range * 0.05
    log_t_max += log_range * 0.05

    n_range = n_max - n_min
    if n_range == 0:
        n_range = 1

    # Create the grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    def place(n, t, char):
        if t <= 0:
            return
        x = int((n - n_min) / n_range * (width - 1))
        log_t = math.log10(t)
        y = int((log_t - log_t_min) / (log_t_max - log_t_min) * (height - 1))
        y = height - 1 - y  # Flip so higher values are at the top
        if 0 <= x < width and 0 <= y < height:
            grid[y][x] = char

    # Place predictions first (they go behind measurements)
    if predictions:
        for n, t in predictions:
            place(n, t, '-')

    # Place measured data points
    for n, t in results:
        place(n, t, '*')

    # Print the plot
    print(f"\n  {title}")
    print(f"  {'Time (log scale)':^{width}}")

    # Y-axis labels
    for row in range(height):
        # Compute the log-time for this row
        frac = 1.0 - row / (height - 1)
        log_val = log_t_min + frac * (log_t_max - log_t_min)
        val = 10 ** log_val

        if row == 0 or row == height - 1 or row == height // 2:
            label = format_time(val)
            print(f"  {label:>10} |{''.join(grid[row])}")
        else:
            print(f"  {'':>10} |{''.join(grid[row])}")

    # X-axis
    print(f"  {'':>10} +{'-' * width}")
    print(f"  {'':>10}  {n_min:<{width // 2}}{n_max:>{width - width // 2}}")
    print(f"  {'':>10}  {'n (input size)':^{width}}")

    if predictions:
        print(f"  {'':>10}  * = measured, - = predicted")
    print()


def format_time(seconds):
    """Format a time value with appropriate units."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.0f}ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.0f}us"
    elif seconds < 1:
        return f"{seconds * 1e3:.1f}ms"
    else:
        return f"{seconds:.2f}s"


# ---------------------------------------------------------------------------
# Section 5: Results Table
# ---------------------------------------------------------------------------

def print_results_table(results, ratios, predictions=None, label=""):
    """Print a formatted table of benchmark results."""
    print(f"\n  {'n':>8} | {'Measured':>12} | {'Predicted':>12} | {'Ratio':>8} | {'Implied k':>10}")
    print(f"  {'-' * 8}-+-{'-' * 12}-+-{'-' * 12}-+-{'-' * 8}-+-{'-' * 10}")

    ratio_map = {r[0]: (r[2], r[3]) for r in ratios} if ratios else {}
    pred_map = {n: t for n, t in predictions} if predictions else {}

    for n, t in results:
        measured = format_time(t)
        predicted = format_time(pred_map.get(n, 0)) if n in pred_map else "—"
        if n in ratio_map:
            ratio, k = ratio_map[n]
            ratio_str = f"{ratio:.2f}"
            k_str = f"{k:.2f}"
        else:
            ratio_str = "—"
            k_str = "—"
        print(f"  {n:>8} | {measured:>12} | {predicted:>12} | {ratio_str:>8} | {k_str:>10}")


# ---------------------------------------------------------------------------
# Section 6: Algorithms to Benchmark
# ---------------------------------------------------------------------------
# WHY: We need a variety of known complexities to validate our framework.

def insertion_sort(arr):
    """O(n^2) worst/average case. O(n) best case (already sorted)."""
    arr = arr[:]  # Don't modify original
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr):
    """O(n log n) always. Stable. Uses O(n) extra space."""
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
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


def linear_search(arr):
    """O(n): search for a specific value. We search for -1 (not found) to force worst case."""
    target = -1
    for x in arr:
        if x == target:
            return True
    return False


def binary_search_repeated(arr):
    """O(log n): binary search on sorted input. We do the search once."""
    target = -1  # Not found — forces full depth
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


def bubble_sort(arr):
    """O(n^2) worst/average case. Here to compare against insertion sort."""
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def sum_all_pairs(arr):
    """O(n^2): compute sum of all pairs. Simple nested loop."""
    total = 0
    n = len(arr)
    for i in range(n):
        for j in range(i + 1, n):
            total += arr[i] + arr[j]
    return total


# Input generators
def random_array(n):
    """Generate a random array of n integers."""
    return [random.randint(0, n * 10) for _ in range(n)]

def sorted_array(n):
    """Generate a sorted array of n integers (best case for some sorts)."""
    return list(range(n))

def reversed_array(n):
    """Generate a reverse-sorted array (worst case for insertion sort)."""
    return list(range(n, 0, -1))


# ---------------------------------------------------------------------------
# Section 7: Full Benchmark Run
# ---------------------------------------------------------------------------

def run_benchmark(name, func, input_gen, sizes, complexity_func, complexity_name, trials=5):
    """Run a complete benchmark: measure, analyze, predict, and visualize."""
    print("=" * 70)
    print(f"BENCHMARK: {name}")
    print(f"Expected complexity: {complexity_name}")
    print("=" * 70)

    # Measure
    results = benchmark(func, input_gen, sizes, trials=trials)

    # Analyze growth rate
    ratios = compute_ratios(results)
    classification = classify_complexity(ratios)

    # Fit theoretical curve
    c = fit_constant(results, complexity_func)
    predictions = [(n, predict(n, c, complexity_func)) for n, _ in results]

    # Report
    print(f"\n  Empirical classification: {classification}")
    print(f"  Fitted constant c = {c:.2e}")
    print(f"  Model: T(n) = {c:.2e} * {complexity_name}")

    print_results_table(results, ratios, predictions)

    # Plot
    ascii_plot(results, predictions,
               title=f"{name}: measured (*) vs {complexity_name} (-)",
               width=55, height=15)

    return results, ratios


def demo_sorting_comparison():
    """Compare insertion sort vs merge sort — the classic O(n^2) vs O(n log n)."""
    print("\n" + "#" * 70)
    print("# DEMO 1: Insertion Sort vs Merge Sort")
    print("# The textbook O(n^2) vs O(n log n) comparison")
    print("#" * 70)

    sizes = [100, 200, 500, 1000, 2000, 5000]

    run_benchmark(
        "Insertion Sort (random input)", insertion_sort, random_array,
        sizes, f_quadratic, "O(n^2)", trials=3
    )

    run_benchmark(
        "Merge Sort (random input)", merge_sort, random_array,
        sizes, f_nlogn, "O(n log n)", trials=3
    )


def demo_best_vs_worst():
    """Show how input distribution affects real performance."""
    print("\n" + "#" * 70)
    print("# DEMO 2: Best Case vs Worst Case for Insertion Sort")
    print("# Same algorithm, dramatically different performance")
    print("#" * 70)

    sizes = [500, 1000, 2000, 4000, 8000]

    run_benchmark(
        "Insertion Sort (already sorted = best case)", insertion_sort, sorted_array,
        sizes, f_linear, "O(n)", trials=3
    )

    run_benchmark(
        "Insertion Sort (reverse sorted = worst case)", insertion_sort, reversed_array,
        sizes, f_quadratic, "O(n^2)", trials=3
    )


def demo_search():
    """Compare linear search O(n) vs binary search O(log n)."""
    print("\n" + "#" * 70)
    print("# DEMO 3: Linear Search vs Binary Search")
    print("# O(n) vs O(log n) — the dramatic gap")
    print("#" * 70)

    sizes = [1000, 5000, 10000, 50000, 100000, 500000]

    run_benchmark(
        "Linear Search (element not found)", linear_search, random_array,
        sizes, f_linear, "O(n)", trials=5
    )

    run_benchmark(
        "Binary Search (element not found)", binary_search_repeated, sorted_array,
        sizes, f_log, "O(log n)", trials=5
    )


def demo_constant_factors():
    """Show that constant factors matter in practice."""
    print("\n" + "#" * 70)
    print("# DEMO 4: When Theory Meets Reality — Constant Factors")
    print("# Bubble sort and insertion sort are both O(n^2),")
    print("# but insertion sort is significantly faster in practice")
    print("#" * 70)

    sizes = [200, 500, 1000, 2000, 3000]

    results_bubble, _ = run_benchmark(
        "Bubble Sort (random)", bubble_sort, random_array,
        sizes, f_quadratic, "O(n^2)", trials=3
    )

    results_insert, _ = run_benchmark(
        "Insertion Sort (random)", insertion_sort, random_array,
        sizes, f_quadratic, "O(n^2)", trials=3
    )

    # Compare the constants
    print("\n  Constant factor comparison (both are O(n^2)):")
    print(f"  {'n':>8} | {'Bubble':>12} | {'Insertion':>12} | {'Ratio B/I':>10}")
    print(f"  {'-' * 48}")
    for (n1, t1), (n2, t2) in zip(results_bubble, results_insert):
        ratio = t1 / t2 if t2 > 0 else float('inf')
        print(f"  {n1:>8} | {format_time(t1):>12} | {format_time(t2):>12} | {ratio:>10.2f}x")

    print("\n  INSIGHT: Same big-O does NOT mean same performance.")
    print("  Insertion sort does fewer swaps on average than bubble sort.")
    print("  The constant factor in bubble sort is roughly 2-3x larger.")
    print()


def demo_crossover():
    """Find where merge sort overtakes insertion sort."""
    print("\n" + "#" * 70)
    print("# DEMO 5: The Crossover Point")
    print("# Insertion sort is faster for small n despite worse big-O")
    print("#" * 70)

    sizes = [5, 10, 15, 20, 30, 50, 75, 100, 150, 200]

    results_insert = benchmark(insertion_sort, random_array, sizes, trials=7)
    results_merge = benchmark(merge_sort, random_array, sizes, trials=7)

    print(f"\n  {'n':>6} | {'Insertion':>12} | {'Merge':>12} | {'Winner':>12}")
    print(f"  {'-' * 48}")

    crossover = None
    for (n1, t1), (n2, t2) in zip(results_insert, results_merge):
        winner = "insertion" if t1 < t2 else "merge"
        if winner == "merge" and crossover is None:
            crossover = n1
        print(f"  {n1:>6} | {format_time(t1):>12} | {format_time(t2):>12} | {winner:>12}")

    if crossover:
        print(f"\n  Crossover point: around n = {crossover}")
        print("  Below this, insertion sort wins due to lower constant factors.")
        print("  Above this, merge sort's O(n log n) dominance takes over.")
    else:
        print("\n  No clear crossover in this range — try larger sizes.")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)

    print("=" * 70)
    print("DAY 7: BENCHMARK SUITE — MEASURING THEORY vs REALITY")
    print("=" * 70)
    print()
    print("This suite benchmarks algorithms, fits theoretical curves,")
    print("and shows where reality diverges from textbook predictions.")
    print()
    print("Using median of multiple trials to reduce noise.")
    print("Times measured with time.perf_counter() for best resolution.")
    print()

    demo_sorting_comparison()
    demo_best_vs_worst()
    demo_search()
    demo_constant_factors()
    demo_crossover()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Key takeaways from benchmarking:")
    print()
    print("  1. BIG-O IS ABOUT GROWTH RATE, NOT ABSOLUTE SPEED")
    print("     An O(n^2) algorithm can be faster than O(n log n) for small n.")
    print()
    print("  2. CONSTANT FACTORS MATTER")
    print("     Bubble sort and insertion sort are both O(n^2), but insertion")
    print("     sort is 2-3x faster in practice due to fewer operations.")
    print()
    print("  3. INPUT DISTRIBUTION MATTERS")
    print("     Insertion sort is O(n) on sorted input but O(n^2) on reversed.")
    print("     The same algorithm can have wildly different real performance.")
    print()
    print("  4. CACHE EFFECTS ARE REAL")
    print("     When data exceeds cache size, performance can drop suddenly.")
    print("     This is not captured by big-O analysis at all.")
    print()
    print("  5. MEASURE, DON'T GUESS")
    print("     Theory tells you the growth rate. Benchmarking tells you")
    print("     the actual time. You need both.")
