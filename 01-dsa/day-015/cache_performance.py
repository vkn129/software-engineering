"""
Day 15: Cache Performance — Measuring the Impact of Memory Access Patterns

This script demonstrates that HOW you traverse memory matters as much as
WHAT algorithm you use. Cache-friendly access can be 5-10x faster than
cache-unfriendly access on the same data.

WHY THIS MATTERS:
Two O(n) algorithms can have wildly different wall-clock times.
Understanding cache behavior explains why — and helps you write
code that works WITH the hardware instead of against it.

Run: python cache_performance.py
"""

import array
import random
import time


def measure_time(func, *args, repeats=5):
    """Run a function multiple times and return the minimum time."""
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)
    return min(times), result


# ---------------------------------------------------------------------------
# 1. Sequential vs Random Access
# ---------------------------------------------------------------------------

def sequential_sum(arr):
    """Sum elements in order — exploits spatial locality."""
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total


def random_sum(arr, indices):
    """Sum elements in random order — destroys spatial locality."""
    total = 0
    for i in indices:
        total += arr[i]
    return total


def benchmark_access_patterns():
    """
    Compare sequential vs random access on a large array.
    Both do the same amount of work (sum N elements), but
    sequential access is much faster due to cache hits.
    """
    print("=" * 70)
    print("1. SEQUENTIAL vs RANDOM ACCESS")
    print("=" * 70)

    # Use array module for true contiguous storage
    n = 500_000
    arr = array.array('l', range(n))

    # Create random permutation of indices
    indices = list(range(n))
    random.shuffle(indices)

    seq_time, seq_result = measure_time(sequential_sum, arr)
    rand_time, rand_result = measure_time(random_sum, arr, indices)

    print(f"\nArray size: {n:,} elements ({n * arr.itemsize:,} bytes)")
    print(f"\nSequential access: {seq_time * 1000:8.2f} ms")
    print(f"Random access:     {rand_time * 1000:8.2f} ms")
    print(f"Slowdown:          {rand_time / seq_time:.1f}x")
    print()

    assert seq_result == rand_result, "Both should compute the same sum"
    print("Both computed the same sum — same work, different speed.")
    print("Random access causes cache misses on nearly every element.\n")


# ---------------------------------------------------------------------------
# 2. Row-Major vs Column-Major Traversal
# ---------------------------------------------------------------------------

def sum_row_major(matrix, rows, cols):
    """
    Traverse row by row: matrix[0][0], matrix[0][1], ..., matrix[1][0], ...
    In row-major layout (Python/C), adjacent column elements are adjacent
    in memory. This is CACHE-FRIENDLY.
    """
    total = 0
    for r in range(rows):
        for c in range(cols):
            total += matrix[r][c]
    return total


def sum_col_major(matrix, rows, cols):
    """
    Traverse column by column: matrix[0][0], matrix[1][0], ..., matrix[0][1], ...
    In row-major layout, this jumps by `cols` elements each step.
    This is CACHE-UNFRIENDLY.
    """
    total = 0
    for c in range(cols):
        for r in range(rows):
            total += matrix[r][c]
    return total


def benchmark_2d_traversal():
    """
    Demonstrate that traversal order matters for 2D arrays.

    Python lists-of-lists aren't truly contiguous, so the effect
    is smaller than in C. But the principle is identical, and the
    effect is still measurable.
    """
    print("=" * 70)
    print("2. ROW-MAJOR vs COLUMN-MAJOR TRAVERSAL (2D)")
    print("=" * 70)

    rows, cols = 1000, 1000

    # Use array.array rows for better contiguity within each row
    # (Python list-of-lists is list of pointers to lists of pointers to ints,
    #  but this still demonstrates the principle)
    matrix = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            matrix[r][c] = r * cols + c

    row_time, row_result = measure_time(sum_row_major, matrix, rows, cols)
    col_time, col_result = measure_time(sum_col_major, matrix, rows, cols)

    print(f"\nMatrix: {rows} x {cols} = {rows * cols:,} elements")
    print(f"\nRow-major traversal:    {row_time * 1000:8.2f} ms  (cache-friendly)")
    print(f"Column-major traversal: {col_time * 1000:8.2f} ms  (cache-unfriendly)")
    print(f"Slowdown:               {col_time / row_time:.1f}x")
    print()

    assert row_result == col_result
    print("Same result, same number of additions — different memory pattern.")
    print()

    # Explain why
    print("WHY THIS HAPPENS:")
    print("-" * 40)
    print("Row-major (Python/C) stores rows contiguously:")
    print("  memory: [row0_col0, row0_col1, row0_col2, ..., row1_col0, ...]")
    print()
    print("Row-major traversal: visits adjacent memory locations")
    print("  → CPU prefetcher loads the next cache line ahead of time")
    print("  → almost zero cache misses")
    print()
    print("Column-major traversal: jumps by `cols` elements each step")
    print(f"  → each access jumps {cols * 8} bytes (for 8-byte pointers)")
    print("  → nearly every access misses the cache")
    print()


# ---------------------------------------------------------------------------
# 3. Stride Effects — How Skip Size Affects Performance
# ---------------------------------------------------------------------------

def sum_with_stride(arr, stride):
    """Sum every stride-th element."""
    total = 0
    i = 0
    while i < len(arr):
        total += arr[i]
        i += stride
    return total


def benchmark_stride():
    """
    Show how increasing stride (distance between accesses) degrades
    performance. Once the stride exceeds the cache line size, every
    access is a miss.
    """
    print("=" * 70)
    print("3. STRIDE EFFECTS — Skip Size vs Performance")
    print("=" * 70)

    n = 1_000_000
    arr = array.array('l', range(n))
    cache_line = 64
    elem_size = arr.itemsize
    elems_per_cache_line = cache_line // elem_size

    print(f"\nArray: {n:,} elements, {elem_size} bytes each")
    print(f"Cache line: {cache_line} bytes = {elems_per_cache_line} elements")
    print(f"\n{'Stride':>8} {'Elements':>10} {'Time (ms)':>10} {'Note':>20}")
    print("-" * 55)

    strides = [1, 2, 4, 8, 16, 32, 64, 128]
    base_time = None

    for stride in strides:
        t, _ = measure_time(sum_with_stride, arr, stride)
        if base_time is None:
            base_time = t

        # How many elements we actually touched
        count = (n + stride - 1) // stride
        note = ""
        if stride * elem_size == cache_line:
            note = "← 1 per cache line"
        elif stride * elem_size > cache_line:
            note = "← skipping cache lines"
        elif stride == 1:
            note = "← fully sequential"

        print(f"{stride:>8} {count:>10,} {t * 1000:>10.2f} {note:>20}")

    print()
    print("KEY INSIGHT: Time doesn't drop proportionally to elements touched.")
    print("With stride=1, you access N elements but the cache prefetcher helps.")
    print(f"Once stride > {elems_per_cache_line} (cache line / elem_size), "
          "every access is a cache miss.\n")


# ---------------------------------------------------------------------------
# 4. Contiguous (array) vs Non-Contiguous (list) Access
# ---------------------------------------------------------------------------

def benchmark_list_vs_array():
    """
    Compare traversal of a Python list vs array.array.
    The array is truly contiguous; the list is an array of pointers
    to scattered int objects.
    """
    print("=" * 70)
    print("4. LIST vs ARRAY — Contiguous Values vs Scattered Objects")
    print("=" * 70)

    n = 500_000

    py_list = list(range(n))
    py_array = array.array('l', range(n))

    def traverse_list(lst):
        total = 0
        for x in lst:
            total += x
        return total

    def traverse_array(arr):
        total = 0
        for x in arr:
            total += x
        return total

    list_time, _ = measure_time(traverse_list, py_list)
    arr_time, _ = measure_time(traverse_array, py_array)

    print(f"\nSize: {n:,} elements")
    print(f"\nPython list traversal:   {list_time * 1000:8.2f} ms")
    print(f"array.array traversal:   {arr_time * 1000:8.2f} ms")
    ratio = list_time / arr_time if arr_time > 0 else float('inf')
    print(f"Ratio:                   {ratio:.2f}x")
    print()
    print("NOTE: In CPython, the array module still creates Python int objects")
    print("when you iterate, so the speedup is less dramatic than in C.")
    print("For true contiguous performance in Python, use numpy.\n")


if __name__ == "__main__":
    print("CACHE PERFORMANCE BENCHMARKS")
    print("Demonstrating why memory access patterns matter.\n")

    benchmark_access_patterns()
    benchmark_2d_traversal()
    benchmark_stride()
    benchmark_list_vs_array()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
1. Sequential access is faster than random access (cache hits vs misses)
2. Row-major traversal is faster in row-major languages (C, Python, Java)
3. Larger strides mean more cache misses
4. Contiguous data (array) is faster than pointer-chased data (list)

These effects are HARDWARE-LEVEL — they apply to any programming language.
Understanding them helps you write code that works WITH the CPU, not against it.
""")
