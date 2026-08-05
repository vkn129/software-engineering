"""
Day 160: Parallel Sort — Threaded vs Process-based

Three implementations of parallel mergesort:
1. Sequential baseline
2. Threaded (demonstrates GIL anti-speedup)
3. Multiprocessing (demonstrates real speedup with caveats)

Honest measurement: median of multiple runs, identical input.
"""

import random
import time
import threading
import multiprocessing as mp
from statistics import median


THRESHOLD = 50_000  # below this size, sort serially


# ---------------------------------------------------------------------------
# 1. Sequential mergesort baseline
# ---------------------------------------------------------------------------

def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def sequential_mergesort(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    return merge(sequential_mergesort(arr[:mid]),
                 sequential_mergesort(arr[mid:]))


# ---------------------------------------------------------------------------
# 2. Threaded parallel mergesort (GIL — expect anti-speedup)
# ---------------------------------------------------------------------------

def threaded_mergesort(arr, depth=0, max_depth=2):
    if len(arr) <= THRESHOLD or depth >= max_depth:
        return sequential_mergesort(arr)

    mid = len(arr) // 2
    left_result = [None]
    right_result = [None]

    def sort_left():
        left_result[0] = threaded_mergesort(arr[:mid], depth + 1, max_depth)

    def sort_right():
        right_result[0] = threaded_mergesort(arr[mid:], depth + 1, max_depth)

    t_left = threading.Thread(target=sort_left)
    t_right = threading.Thread(target=sort_right)
    t_left.start()
    t_right.start()
    t_left.join()
    t_right.join()

    return merge(left_result[0], right_result[0])


# ---------------------------------------------------------------------------
# 3. Multiprocessing parallel mergesort
# ---------------------------------------------------------------------------

def _sort_chunk(chunk):
    """Top-level for picklability."""
    return sequential_mergesort(chunk)


def process_mergesort(arr, num_workers=4):
    """
    Split into num_workers chunks, sort each in its own process,
    then merge sequentially (multi-way merge).
    """
    n = len(arr)
    if n <= THRESHOLD:
        return sequential_mergesort(arr)

    chunk_size = (n + num_workers - 1) // num_workers
    chunks = [arr[i:i + chunk_size] for i in range(0, n, chunk_size)]

    with mp.Pool(num_workers) as pool:
        sorted_chunks = pool.map(_sort_chunk, chunks)

    # Iterative two-way merge of all chunks
    while len(sorted_chunks) > 1:
        merged = []
        for i in range(0, len(sorted_chunks), 2):
            if i + 1 < len(sorted_chunks):
                merged.append(merge(sorted_chunks[i], sorted_chunks[i + 1]))
            else:
                merged.append(sorted_chunks[i])
        sorted_chunks = merged

    return sorted_chunks[0]


# ---------------------------------------------------------------------------
# Benchmark harness
# ---------------------------------------------------------------------------

def bench(fn, arr, runs=3):
    """Median wall-clock over `runs` trials. Discards first (warm-up)."""
    timings = []
    for _ in range(runs + 1):
        t0 = time.perf_counter()
        out = fn(arr)
        t1 = time.perf_counter()
        timings.append(t1 - t0)
    return median(timings[1:]), out


def verify(out, expected):
    assert out == expected, "sort produced wrong output!"


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_correctness():
    print("=" * 60)
    print("DEMO 1: Correctness check")
    print("=" * 60)
    random.seed(0)
    for n in [0, 1, 10, 100, 1000, 5000]:
        arr = [random.randint(0, 1000) for _ in range(n)]
        expected = sorted(arr)
        assert sequential_mergesort(arr) == expected
        assert threaded_mergesort(arr) == expected
        assert process_mergesort(arr, num_workers=2) == expected
    print("  All three implementations agree on lengths 0, 1, 10, 100, 1000, 5000")


def demo_speedup():
    print("\n" + "=" * 60)
    print("DEMO 2: Wall-clock speedup measurement")
    print("=" * 60)
    random.seed(0)
    n = 200_000
    arr = [random.randint(0, 10 ** 9) for _ in range(n)]
    expected = sorted(arr)

    print(f"\n  n={n} random ints; median of 3 runs (after warm-up)")
    print(f"  CPU count: {mp.cpu_count()}\n")

    t_seq, out = bench(sequential_mergesort, arr)
    verify(out, expected)
    print(f"  sequential mergesort:        {t_seq:.3f}s   (baseline)")

    t_th, out = bench(threaded_mergesort, arr)
    verify(out, expected)
    print(f"  threaded (max_depth=2):      {t_th:.3f}s   ({t_seq / t_th:.2f}x  {'speedup' if t_th < t_seq else 'anti-speedup (GIL)'})")

    for w in [2, 4]:
        t_proc, out = bench(lambda a, w=w: process_mergesort(a, num_workers=w), arr)
        verify(out, expected)
        print(f"  multiprocessing ({w} workers): {t_proc:.3f}s   ({t_seq / t_proc:.2f}x speedup)")

    # Reference: Python's built-in Timsort (C)
    t_ts, _ = bench(lambda a: sorted(a), arr)
    print(f"  sorted() (C Timsort):        {t_ts:.3f}s   ({t_seq / t_ts:.1f}x — different game)")


def demo_amdahl():
    print("\n" + "=" * 60)
    print("DEMO 3: Amdahl's law — diminishing returns")
    print("=" * 60)
    random.seed(0)
    n = 400_000
    arr = [random.randint(0, 10 ** 9) for _ in range(n)]
    expected = sorted(arr)

    print(f"\n  n={n} on {mp.cpu_count()}-core machine")
    print(f"  Workers | Time     | Speedup vs sequential")
    t_seq, _ = bench(sequential_mergesort, arr)
    print(f"     seq  | {t_seq:.3f}s | 1.00x")
    for w in [1, 2, 4, 8]:
        t_proc, out = bench(lambda a, w=w: process_mergesort(a, num_workers=w), arr)
        verify(out, expected)
        print(f"     {w:2d}   | {t_proc:.3f}s | {t_seq / t_proc:.2f}x")
    print("\n  Notice: speedup plateaus well before #workers = #cores.")
    print("  Pickling overhead + serial final merge are the bottlenecks.")


if __name__ == "__main__":
    demo_correctness()
    demo_speedup()
    demo_amdahl()
