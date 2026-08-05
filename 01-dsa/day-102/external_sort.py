"""
Day 102: External Sorting — Merge Sort Beyond RAM

Simulates disk pages with in-memory chunks. Real implementations would
read/write files; we use lists/iterators to focus on the algorithm.
"""

import heapq
import random
import tempfile
import os
import time


# ---------------------------------------------------------------------------
# 1. K-way merge using a min-heap
# ---------------------------------------------------------------------------

def k_way_merge(runs):
    """
    Merge K sorted iterables. Yields elements in sorted order.
    O(N log K) total work; O(K) memory.
    Each run is consumed lazily — never loaded all at once.
    """
    heap = []
    iterators = [iter(r) for r in runs]
    for i, it in enumerate(iterators):
        try:
            heap.append((next(it), i))
        except StopIteration:
            pass
    heapq.heapify(heap)

    while heap:
        val, i = heapq.heappop(heap)
        yield val
        try:
            heapq.heappush(heap, (next(iterators[i]), i))
        except StopIteration:
            pass


# ---------------------------------------------------------------------------
# 2. External sort with in-memory "disk" (lists as pages)
# ---------------------------------------------------------------------------

def external_sort_inmemory(data, chunk_size):
    """
    External-sort simulation. data is a streaming iterable.
    chunk_size = how many elements fit in 'RAM' at once.

    Phase 1: produce sorted runs (in-memory chunks).
    Phase 2: K-way merge them.
    """
    # Phase 1: create sorted runs
    runs = []
    chunk = []
    for x in data:
        chunk.append(x)
        if len(chunk) >= chunk_size:
            chunk.sort()
            runs.append(chunk)
            chunk = []
    if chunk:
        chunk.sort()
        runs.append(chunk)

    # Phase 2: K-way merge
    return list(k_way_merge(runs))


# ---------------------------------------------------------------------------
# 3. External sort using actual temp files (real disk simulation)
# ---------------------------------------------------------------------------

def external_sort_files(input_iter, chunk_size, tmp_dir=None):
    """
    Real external sort that writes runs to temp files on disk.
    Returns iterator over sorted output.
    """
    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp(prefix="extsort_")

    run_files = []
    chunk = []

    # Phase 1: write sorted runs to disk
    for x in input_iter:
        chunk.append(x)
        if len(chunk) >= chunk_size:
            run_files.append(_write_run(chunk, tmp_dir))
            chunk = []
    if chunk:
        run_files.append(_write_run(chunk, tmp_dir))

    # Phase 2: K-way merge from disk
    readers = [_read_run(f) for f in run_files]
    try:
        for val in k_way_merge(readers):
            yield val
    finally:
        # Cleanup
        for f in run_files:
            try:
                os.unlink(f)
            except OSError:
                pass


def _write_run(chunk, tmp_dir):
    chunk.sort()
    fd, path = tempfile.mkstemp(dir=tmp_dir, suffix=".run")
    with os.fdopen(fd, "w") as f:
        for x in chunk:
            f.write(f"{x}\n")
    return path


def _read_run(path):
    """Generator that yields ints from a run file, one at a time."""
    with open(path, "r") as f:
        for line in f:
            yield int(line)


# ---------------------------------------------------------------------------
# 4. Replacement selection — double-length runs
# ---------------------------------------------------------------------------

def replacement_selection_runs(data, heap_size):
    """
    Generate longer runs using replacement selection.
    Returns list of sorted runs. Average run length ~ 2 * heap_size.
    """
    it = iter(data)
    # Initialize heap with first heap_size elements
    primary = []
    for _ in range(heap_size):
        try:
            primary.append(next(it))
        except StopIteration:
            break
    heapq.heapify(primary)

    runs = []
    current_run = []
    secondary = []  # items reserved for next run
    last_emitted = None

    while primary or secondary:
        if not primary:
            # Current run done; start new run with secondary
            runs.append(current_run)
            current_run = []
            primary = secondary
            heapq.heapify(primary)
            secondary = []
            last_emitted = None
            continue

        smallest = heapq.heappop(primary)
        current_run.append(smallest)
        last_emitted = smallest

        try:
            nxt = next(it)
            if nxt >= last_emitted:
                heapq.heappush(primary, nxt)
            else:
                heapq.heappush(secondary, nxt)
        except StopIteration:
            pass

    if current_run:
        runs.append(current_run)
    return runs


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_k_way_merge():
    print("=" * 60)
    print("DEMO 1: K-way merge of 4 sorted runs")
    print("=" * 60)
    runs = [
        [1, 4, 7, 10],
        [2, 5, 8, 11],
        [3, 6, 9, 12],
        [0, 13, 14, 15],
    ]
    out = list(k_way_merge(runs))
    print(f"\n  inputs: {runs}")
    print(f"  merged: {out}")
    print(f"  correct: {out == sorted(sum(runs, []))}")


def demo_external_inmemory():
    print("\n" + "=" * 60)
    print("DEMO 2: External sort (in-memory pages), chunk=100")
    print("=" * 60)
    random.seed(42)
    n = 5000
    data = [random.randint(0, 100000) for _ in range(n)]

    out = external_sort_inmemory(iter(data), chunk_size=100)
    print(f"\n  n = {n}, chunk_size = 100, runs ≈ {n // 100}")
    print(f"  sorted correctly: {out == sorted(data)}")


def demo_external_files():
    print("\n" + "=" * 60)
    print("DEMO 3: External sort with real temp files on disk")
    print("=" * 60)
    random.seed(7)
    n = 2000
    data = [random.randint(0, 100000) for _ in range(n)]

    start = time.perf_counter()
    out = list(external_sort_files(iter(data), chunk_size=200))
    elapsed = (time.perf_counter() - start) * 1000

    print(f"\n  n = {n}, chunk_size = 200, runs = 10 (on disk)")
    print(f"  elapsed: {elapsed:.1f} ms")
    print(f"  sorted correctly: {out == sorted(data)}")


def demo_chunk_size_tradeoff():
    print("\n" + "=" * 60)
    print("DEMO 4: Chunk size tradeoff (in-memory simulation)")
    print("=" * 60)
    random.seed(42)
    n = 50000
    data = [random.randint(0, 10**6) for _ in range(n)]

    print(f"\n  n = {n}")
    print(f"  {'chunk_size':>12s}  {'num_runs':>10s}  {'time ms':>10s}")
    for cs in [10, 100, 1000, 10000]:
        start = time.perf_counter()
        out = external_sort_inmemory(iter(data), chunk_size=cs)
        elapsed = (time.perf_counter() - start) * 1000
        runs = (n + cs - 1) // cs
        assert out == sorted(data)
        print(f"  {cs:>12d}  {runs:>10d}  {elapsed:>10.2f}")
    print("\n  Larger chunks → fewer runs → cheaper merge phase.")
    print("  But each chunk must fit in memory.")


def demo_replacement_selection():
    print("\n" + "=" * 60)
    print("DEMO 5: Replacement selection produces ~2x longer runs")
    print("=" * 60)
    random.seed(11)
    n = 5000
    data = [random.randint(0, 10**6) for _ in range(n)]
    heap_size = 100

    # Naive chunking
    naive_runs = (n + heap_size - 1) // heap_size

    # Replacement selection
    rs_runs = replacement_selection_runs(data, heap_size)

    # Verify each rs run is sorted
    for r in rs_runs:
        assert r == sorted(r), "run not sorted"
    avg_rs_len = sum(len(r) for r in rs_runs) / len(rs_runs)

    print(f"\n  n = {n}, heap_size = {heap_size}")
    print(f"  Naive chunking:           {naive_runs} runs of size {heap_size}")
    print(f"  Replacement selection:    {len(rs_runs)} runs, avg len = {avg_rs_len:.1f}")
    print(f"  RS produced ~{avg_rs_len/heap_size:.1f}x longer runs (Knuth predicts 2x)")


if __name__ == "__main__":
    demo_k_way_merge()
    demo_external_inmemory()
    demo_external_files()
    demo_chunk_size_tradeoff()
    demo_replacement_selection()
