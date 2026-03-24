"""
Day 24 Practice: Skip List Exercises

4 exercises building on the skip list implementation.
Each has a TODO stub and a reference solution prefixed with _sol_.

Run: python practice.py
"""

import random
import time
import bisect
from skip_list import SkipList, Node


# ============================================================================
# Exercise 1: Range Query — find all keys in [lo, hi]
# ============================================================================
# WHY this matters:
# Range queries are THE killer feature of skip lists over hash tables.
# Redis ZRANGEBYSCORE uses exactly this approach. The skip list structure
# lets you jump to 'lo' in O(log n), then walk level 0 to collect results.
# A hash table would need O(n) to scan all keys.

def range_query(sl, lo, hi):
    """Return a list of (key, value) pairs where lo <= key <= hi, in sorted order.

    Approach:
    1. Use the skip list levels to find the first node with key >= lo (O(log n)).
    2. Walk level 0 forward, collecting nodes while key <= hi (O(k) where k = results).

    Total: O(log n + k) — much better than scanning all n elements.

    TODO: Implement this.
    """
    pass


def _sol_range_query(sl, lo, hi):
    """Reference solution for range query."""
    results = []
    # Use skip list structure to jump close to 'lo'
    # Start from header, traverse top-down to find the predecessor of 'lo'
    current = sl.header
    for i in range(sl.level, -1, -1):
        while current.forward[i] and current.forward[i].key < lo:
            current = current.forward[i]

    # Now current is the last node with key < lo at level 0.
    # Move to the first candidate.
    current = current.forward[0]

    # Walk level 0, collecting nodes in range
    while current and current.key <= hi:
        results.append((current.key, current.value))
        current = current.forward[0]

    return results


# ============================================================================
# Exercise 2: Find the k-th smallest element (0-indexed)
# ============================================================================
# WHY this matters:
# This is Redis's ZRANK / ZRANGE by index. A naive approach walks level 0
# counting nodes — O(n). A smarter approach augments nodes with span counts
# at each level, enabling O(log n) rank lookup. For this exercise, implement
# the O(n) walk first — the augmented version is a great follow-up project.

def kth_smallest(sl, k):
    """Return the (key, value) of the k-th smallest element (0-indexed).

    Return None if k is out of bounds (k < 0 or k >= size).

    Approach (simple O(n)):
    Walk level 0 from the header, counting nodes until you reach position k.

    TODO: Implement this.
    """
    pass


def _sol_kth_smallest(sl, k):
    """Reference solution for k-th smallest."""
    if k < 0 or k >= len(sl):
        return None

    current = sl.header.forward[0]
    for _ in range(k):
        current = current.forward[0]

    return (current.key, current.value)


# ============================================================================
# Exercise 3: Skip List Iterator (in-order traversal at level 0)
# ============================================================================
# WHY this matters:
# Iterators are the standard interface for traversing data structures in
# production code. Python's iterator protocol (__iter__ + __next__) lets
# skip lists plug into for-loops, list comprehensions, and generator pipelines.
# This is how you'd integrate a skip list into a larger system.

class SkipListIterator:
    """An iterator that yields (key, value) pairs from a skip list in sorted order.

    Must support:
    - __iter__() returning self
    - __next__() returning next (key, value) or raising StopIteration
    - has_next() returning bool (convenience method, not part of protocol)

    TODO: Implement the three methods.
    """

    def __init__(self, skip_list):
        # WHY start at header.forward[0]?
        # The header is a sentinel — it doesn't hold data. The first real
        # node is header.forward[0]. Level 0 has ALL nodes in sorted order.
        self._current = skip_list.header.forward[0]

    def __iter__(self):
        pass

    def __next__(self):
        pass

    def has_next(self):
        pass


class _SolSkipListIterator:
    """Reference solution for skip list iterator."""

    def __init__(self, skip_list):
        self._current = skip_list.header.forward[0]

    def __iter__(self):
        return self

    def __next__(self):
        if self._current is None:
            raise StopIteration
        key, value = self._current.key, self._current.value
        self._current = self._current.forward[0]
        return (key, value)

    def has_next(self):
        return self._current is not None


# ============================================================================
# Exercise 4: Benchmark skip list search vs sorted list with bisect
# ============================================================================
# WHY this matters:
# Theory says both are O(log n), but constants differ enormously.
# Sorted arrays have perfect cache locality (contiguous memory); skip lists
# chase pointers across the heap. This benchmark reveals the real-world
# cost of pointer chasing — essential knowledge for choosing data structures
# in production systems.

def benchmark(n=50000, num_searches=10000):
    """Compare skip list search vs bisect on a sorted list.

    Steps:
    1. Insert n random unique integers into both a skip list and a sorted list.
    2. Pick num_searches random keys that exist in the data.
    3. Time searching for all of them in both structures.
    4. Print the results.

    TODO: Implement this. Use time.perf_counter() for timing.

    Expected result: bisect is faster due to cache locality, but skip list
    supports O(log n) insert/delete while sorted list insert is O(n).
    """
    pass


def _sol_benchmark(n=50000, num_searches=10000):
    """Reference solution for benchmark."""
    # Generate n unique random keys
    keys = random.sample(range(n * 10), n)

    # Build skip list
    sl = SkipList(max_level=20, p=0.5)
    for k in keys:
        sl.insert(k, k)

    # Build sorted list
    sorted_keys = sorted(keys)

    # Pick search targets (keys that exist)
    search_targets = random.choices(keys, k=num_searches)

    # Benchmark skip list search
    start = time.perf_counter()
    for k in search_targets:
        sl.search(k)
    sl_time = time.perf_counter() - start

    # Benchmark bisect search on sorted list
    start = time.perf_counter()
    for k in search_targets:
        idx = bisect.bisect_left(sorted_keys, k)
        # Verify it's actually found (equivalent to skip list's check)
        _ = idx < len(sorted_keys) and sorted_keys[idx] == k
    bisect_time = time.perf_counter() - start

    print(f"\n{'='*50}")
    print(f"Benchmark: {n:,} elements, {num_searches:,} searches")
    print(f"{'='*50}")
    print(f"  Skip List search:  {sl_time:.4f}s ({num_searches/sl_time:,.0f} ops/sec)")
    print(f"  Bisect search:     {bisect_time:.4f}s ({num_searches/bisect_time:,.0f} ops/sec)")
    print(f"  Ratio (SL/bisect): {sl_time/bisect_time:.2f}x")
    print(f"\n  WHY bisect wins on search: contiguous memory = CPU cache friendly.")
    print(f"  WHY skip list still matters: insert/delete are O(log n) vs O(n).")
    print(f"  For 50k elements, inserting into sorted list costs ~25k shifts on avg.")


# ============================================================================
# Test runner
# ============================================================================

def run_tests():
    """Run all exercises against reference solutions and report results."""
    print("=" * 60)
    print("Day 24 Practice: Skip List Exercises")
    print("=" * 60)

    # Build a shared skip list for testing
    sl = SkipList(max_level=8, p=0.5)
    test_data = [(5, "e"), (10, "j"), (15, "o"), (20, "t"), (25, "y"),
                 (30, "dd"), (35, "ii"), (40, "nn"), (45, "ss"), (50, "xx")]
    for k, v in test_data:
        sl.insert(k, v)

    passed = 0
    total = 4

    # --- Exercise 1: Range Query ---
    print("\n[Exercise 1] Range Query")
    try:
        user = range_query(sl, 15, 35)
        expected = _sol_range_query(sl, 15, 35)
        if user == expected:
            print(f"  PASS: range_query(15, 35) = {user}")
            passed += 1
        elif user is None:
            print(f"  SKIP: Not implemented yet (returned None)")
            print(f"  Expected: {expected}")
        else:
            print(f"  FAIL: Got {user}, expected {expected}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Edge cases for range query
    edge1 = _sol_range_query(sl, 0, 3)   # empty range (no keys < 5)
    edge2 = _sol_range_query(sl, 50, 100)  # single element at boundary
    print(f"  Edge: range(0,3) = {edge1}, range(50,100) = {edge2}")

    # --- Exercise 2: K-th Smallest ---
    print("\n[Exercise 2] K-th Smallest")
    try:
        user = kth_smallest(sl, 3)
        expected = _sol_kth_smallest(sl, 3)
        if user == expected:
            print(f"  PASS: kth_smallest(3) = {user}")
            passed += 1
        elif user is None and expected is not None:
            print(f"  SKIP: Not implemented yet (returned None)")
            print(f"  Expected: {expected}")
        else:
            print(f"  FAIL: Got {user}, expected {expected}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Boundary checks
    edge_first = _sol_kth_smallest(sl, 0)
    edge_last = _sol_kth_smallest(sl, len(sl) - 1)
    edge_oob = _sol_kth_smallest(sl, len(sl))
    print(f"  Edge: 0th={edge_first}, last={edge_last}, out-of-bounds={edge_oob}")

    # --- Exercise 3: Iterator ---
    print("\n[Exercise 3] Skip List Iterator")
    try:
        it = SkipListIterator(sl)
        user_items = list(it)
        sol_items = list(_SolSkipListIterator(sl))
        if user_items == sol_items:
            print(f"  PASS: Iterator produced {len(user_items)} items in order")
            passed += 1
        elif len(user_items) == 0:
            print(f"  SKIP: Not implemented yet (empty iteration)")
            print(f"  Expected: {sol_items[:3]}...")
        else:
            print(f"  FAIL: Got {user_items[:3]}..., expected {sol_items[:3]}...")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Test has_next
    sol_it = _SolSkipListIterator(sl)
    print(f"  has_next() before iteration: {sol_it.has_next()}")
    for _ in sol_it:
        pass
    print(f"  has_next() after exhaustion: {sol_it.has_next()}")

    # --- Exercise 4: Benchmark ---
    print("\n[Exercise 4] Benchmark: Skip List vs Sorted List")
    try:
        result = benchmark(n=10000, num_searches=5000)
        if result is None:
            print("  SKIP: Not implemented yet")
            print("  Running reference solution instead...")
            _sol_benchmark(n=10000, num_searches=5000)
        else:
            passed += 1
    except Exception as e:
        print(f"  ERROR: {e}")
        print("  Running reference solution instead...")
        _sol_benchmark(n=10000, num_searches=5000)

    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} exercises passing")
    if passed == total:
        print("All exercises complete!")
    else:
        print("Keep going — fill in the TODO stubs and re-run.")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_tests()
