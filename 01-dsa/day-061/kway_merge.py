"""
Day 61: K-way Merge and Top-K Problems
=======================================
Merging k sorted streams with a min-heap is O(n log k) — the backbone of
external sorting, MapReduce, and LSM-tree compaction.

Top-K finds the k largest/smallest without full sorting:
  - Min-heap of size k: O(n log k), works on streams
  - Quickselect: O(n) average, in-place, but needs all data in memory
  - Median-of-medians: O(n) worst case, large constant

Run: python kway_merge.py
"""

import heapq
import random
import time


# ─── K-way Merge ───────────────────────────────────────────────────

def merge_k_sorted(lists):
    """
    Merge k sorted lists into one sorted list using a min-heap.

    The heap holds at most k entries: (value, list_index, element_index).
    We include list_index as a tiebreaker so Python's tuple comparison
    never falls through to comparing elements from different lists
    (which could be incomparable types).

    Time:  O(n log k) where n = total elements across all lists
    Space: O(k) for the heap + O(n) for the output
    """
    heap = []
    # Seed the heap with the first element from each non-empty list
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        # If that list has more elements, push the next one
        next_idx = elem_idx + 1
        if next_idx < len(lists[list_idx]):
            heapq.heappush(heap, (lists[list_idx][next_idx], list_idx, next_idx))

    return result


# ─── Top-K Largest (Min-Heap) ──────────────────────────────────────

def top_k_largest(arr, k):
    """
    Return the k largest elements using a min-heap of size k.

    Why min-heap? We want to discard elements smaller than the k-th largest.
    The min-heap's root is the smallest of our k candidates — if a new element
    is larger than that root, it deserves a spot and the current root does not.

    Time:  O(n log k) — each of n elements may trigger a heap push/pop
    Space: O(k) for the heap
    """
    if k <= 0:
        return []
    if k >= len(arr):
        return sorted(arr, reverse=True)

    # Build initial heap from first k elements
    heap = arr[:k]
    heapq.heapify(heap)  # min-heap of size k

    # Process remaining elements
    for val in arr[k:]:
        if val > heap[0]:
            heapq.heapreplace(heap, val)  # pop min + push val in one operation

    # Return sorted descending
    return sorted(heap, reverse=True)


# ─── Top-K Smallest (Max-Heap via Negation) ────────────────────────

def top_k_smallest(arr, k):
    """
    Return the k smallest elements using a max-heap of size k.

    Python only has min-heap, so we negate values to simulate a max-heap.
    The "max" (most negative) is the largest of our k candidates — if a new
    element is smaller, the current largest does not belong in top-k smallest.

    Time:  O(n log k)
    Space: O(k)
    """
    if k <= 0:
        return []
    if k >= len(arr):
        return sorted(arr)

    # Max-heap via negation: negate values so heapq's min-heap acts as max-heap
    heap = [-val for val in arr[:k]]
    heapq.heapify(heap)

    for val in arr[k:]:
        if val < -heap[0]:  # val is smaller than the largest in our heap
            heapq.heapreplace(heap, -val)

    # Negate back and sort ascending
    return sorted([-x for x in heap])


# ─── Quickselect ───────────────────────────────────────────────────

def quickselect(arr, k):
    """
    Find the k-th smallest element (0-indexed) using quickselect.

    Like quicksort, but we only recurse into the partition that contains
    position k. Average case: n + n/2 + n/4 + ... = O(n).

    Uses random pivot to avoid O(n^2) worst case on sorted input.
    Operates in-place on a copy to avoid mutating the original.

    Time:  O(n) average, O(n^2) worst case
    Space: O(1) extra (in-place partitioning) + O(log n) call stack average
    """
    if k < 0 or k >= len(arr):
        raise IndexError(f"k={k} out of range for array of size {len(arr)}")

    data = list(arr)  # work on a copy
    return _quickselect(data, 0, len(data) - 1, k)


def _quickselect(arr, lo, hi, k):
    """Recursive quickselect on arr[lo..hi] looking for position k."""
    if lo == hi:
        return arr[lo]

    # Random pivot avoids worst case on sorted/nearly-sorted input
    pivot_idx = random.randint(lo, hi)
    pivot_idx = _partition(arr, lo, hi, pivot_idx)

    if k == pivot_idx:
        return arr[k]
    elif k < pivot_idx:
        return _quickselect(arr, lo, pivot_idx - 1, k)
    else:
        return _quickselect(arr, pivot_idx + 1, hi, k)


def _partition(arr, lo, hi, pivot_idx):
    """
    Lomuto partition scheme: move pivot to end, partition around it,
    move pivot to its final position. Returns the final pivot index.

    After partitioning:
      arr[lo..store-1] < pivot
      arr[store] == pivot
      arr[store+1..hi] >= pivot
    """
    pivot_val = arr[pivot_idx]
    # Move pivot to end
    arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]
    store = lo
    for i in range(lo, hi):
        if arr[i] < pivot_val:
            arr[store], arr[i] = arr[i], arr[store]
            store += 1
    # Move pivot to its final position
    arr[store], arr[hi] = arr[hi], arr[store]
    return store


# ─── External Sort Simulation ─────────────────────────────────────

def external_sort_simulation(data, memory_limit):
    """
    Simulate external sort: split data into sorted chunks that fit in
    "memory" (memory_limit elements), then k-way merge the chunks.

    In a real system:
      Phase 1: Read chunks from disk, sort in RAM, write sorted runs to disk
      Phase 2: Open all run files, k-way merge using a heap of size k

    Here we simulate with in-memory lists, but the algorithm is identical
    to what the Unix `sort` command does for large files.

    Time:  O(n log n) for sorting chunks + O(n log k) for merging
           where k = ceil(n / memory_limit) runs
    Space: O(memory_limit) working memory + O(n) for output
    """
    n = len(data)
    if n == 0:
        return []

    # Phase 1: Create sorted runs
    # In reality, each run would be written to a temporary file on disk
    runs = []
    for start in range(0, n, memory_limit):
        chunk = data[start:start + memory_limit]
        chunk.sort()  # Sort this chunk in "memory"
        runs.append(chunk)

    # Phase 2: K-way merge all runs
    # In reality, we would read from k file handles simultaneously
    return merge_k_sorted(runs)


# ─── Demo ──────────────────────────────────────────────────────────

def timed(label, fn, *args):
    """Run fn(*args) and print elapsed time."""
    start = time.perf_counter()
    result = fn(*args)
    elapsed = (time.perf_counter() - start) * 1000
    print(f"  {label}: {elapsed:.2f} ms")
    return result


if __name__ == "__main__":
    print("=" * 60)
    print("Day 61: K-way Merge and Top-K Problems")
    print("=" * 60)

    # ── K-way Merge Demo ──
    print("\n--- K-way Merge: merging 4 sorted lists ---")
    lists = [
        [1, 5, 9, 13],
        [2, 6, 10, 14],
        [3, 7, 11, 15],
        [4, 8, 12, 16],
    ]
    merged = merge_k_sorted(lists)
    print(f"  Input:  {lists}")
    print(f"  Output: {merged}")
    assert merged == list(range(1, 17)), "K-way merge failed!"

    # ── Top-K Demo ──
    print("\n--- Top-K Largest (min-heap of size k) ---")
    data = [38, 27, 43, 3, 9, 82, 10, 55, 71, 1]
    k = 3
    top3 = top_k_largest(data, k)
    print(f"  Data: {data}")
    print(f"  Top {k}: {top3}")
    assert top3 == [82, 71, 55], f"Expected [82, 71, 55], got {top3}"

    print("\n--- Top-K Smallest (max-heap via negation) ---")
    bot3 = top_k_smallest(data, k)
    print(f"  Data: {data}")
    print(f"  Bottom {k}: {bot3}")
    assert bot3 == [1, 3, 9], f"Expected [1, 3, 9], got {bot3}"

    # ── Quickselect Demo ──
    print("\n--- Quickselect: k-th smallest in O(n) average ---")
    arr = [7, 10, 4, 3, 20, 15]
    for kth in range(len(arr)):
        val = quickselect(arr, kth)
        print(f"  {kth}-th smallest of {arr} = {val}")
    sorted_arr = sorted(arr)
    for kth in range(len(arr)):
        assert quickselect(arr, kth) == sorted_arr[kth], f"Quickselect wrong at k={kth}"

    # ── External Sort Simulation ──
    print("\n--- External Sort Simulation ---")
    big_data = list(range(100, 0, -1))  # 100 elements in reverse order
    mem_limit = 10  # "RAM" can hold 10 elements at a time
    sorted_data = external_sort_simulation(big_data, mem_limit)
    print(f"  Data size: {len(big_data)} elements")
    print(f"  Memory limit: {mem_limit} elements")
    print(f"  Runs created: {len(big_data) // mem_limit}")
    print(f"  First 20 of sorted output: {sorted_data[:20]}")
    assert sorted_data == list(range(1, 101)), "External sort failed!"

    # ── Timing Comparisons ──
    print("\n--- Timing: Top-K approaches on 100,000 elements ---")
    n = 100_000
    k = 100
    random.seed(42)
    big_arr = [random.randint(1, 10_000_000) for _ in range(n)]

    # Heap approach: O(n log k)
    result_heap = timed(f"Min-heap top-{k}", top_k_largest, big_arr, k)

    # Quickselect approach: O(n) average, then sort top-k
    def quickselect_top_k(arr, k):
        data = list(arr)
        # Find the k-th largest = (n-k)-th smallest
        threshold = quickselect(data, len(data) - k)
        return sorted([x for x in arr if x >= threshold], reverse=True)[:k]

    result_qs = timed(f"Quickselect top-{k}", quickselect_top_k, big_arr, k)

    # Full sort approach: O(n log n)
    def full_sort_top_k(arr, k):
        return sorted(arr, reverse=True)[:k]

    result_sort = timed(f"Full sort top-{k}", full_sort_top_k, big_arr, k)

    # Verify all produce same result
    assert result_heap == result_sort[:k], "Heap and sort disagree!"
    print(f"\n  All approaches agree on top-{k} elements")

    # ── K-way Merge Timing ──
    print(f"\n--- Timing: K-way merge of k sorted lists ---")
    k_lists = 100
    list_size = 1000
    sorted_lists = [sorted(random.sample(range(10_000_000), list_size)) for _ in range(k_lists)]

    result_kway = timed(f"K-way merge ({k_lists} lists x {list_size})", merge_k_sorted, sorted_lists)

    def concat_and_sort(lists):
        combined = []
        for lst in lists:
            combined.extend(lst)
        combined.sort()
        return combined

    result_concat = timed(f"Concat-and-sort ({k_lists} lists x {list_size})", concat_and_sort, sorted_lists)

    assert result_kway == result_concat, "K-way merge and concat-sort disagree!"
    print(f"  Both approaches produce identical sorted output")

    print("\n" + "=" * 60)
    print("All demos and assertions passed")
    print("=" * 60)
