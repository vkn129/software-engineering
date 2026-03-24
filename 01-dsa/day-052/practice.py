"""
Day 52 Practice: Advanced Heap Exercises
=========================================
Exercises on d-ary heaps, indexed priority queues, and Dijkstra.

Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from advanced_heaps import DaryHeap, IndexedMinPQ


# ─── Exercise 1: Implement D-ary Heapify ───────────────────────────
#
# Build a d-ary min-heap from an unsorted array in O(n).
# Same as Floyd's algorithm but with d children per node.
#
# Hint: last non-leaf index = (n - 2) // d

def dary_heapify(arr, d=4):
    # TODO: return a sorted array using a d-ary heap built via heapify
    pass


# ─── Exercise 2: Compare D Values ──────────────────────────────────
#
# For n random pushes followed by n pops, measure the time for
# d = 2, 3, 4, 8, 16. Return the d that gives the best time.
#
# This demonstrates the trade-off: larger d = faster sift-up, slower sift-down.
# For push-heavy workloads, larger d wins.

def find_best_d(n=5000):
    # TODO: benchmark and return the best d value
    pass


# ─── Exercise 3: Dijkstra Without Indexed PQ ───────────────────────
#
# Implement Dijkstra using a simple binary heap (heapq) with lazy deletion.
# Instead of decrease_key, push duplicate (dist, vertex) entries.
# Skip stale entries when popping.
#
# This is how most practical Dijkstra implementations work — the indexed PQ
# approach is cleaner but the lazy deletion approach is simpler to code.

def dijkstra_lazy(adj, source):
    # TODO: return dist array, adj[u] = [(v, weight), ...]
    pass


# ─── Exercise 4: Shortest Path With Indexed PQ ─────────────────────
#
# Use the IndexedMinPQ from advanced_heaps.py to implement Dijkstra
# and also reconstruct the actual shortest PATH (not just distance).
# Return (dist, path) where path is a list of vertices from source to target.

def shortest_path(adj, source, target):
    # TODO: return (distance, [path]) or (float('inf'), []) if unreachable
    pass


# ─── Exercise 5: Merge K Sorted Arrays Using D-ary Heap ────────────
#
# Merge k sorted arrays into one sorted array using a d-ary heap
# where d = k (optimal for this workload since we do k pushes per extraction).

def merge_k_sorted_dary(arrays):
    # TODO: return merged sorted array
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_dary_heapify(arr, d=4):
    h = DaryHeap(d=d)
    h._data = list(arr)
    n = len(h._data)
    for i in range((n - 2) // d, -1, -1):
        h._sift_down(i)
    result = []
    while h:
        result.append(h.pop())
    return result


def _sol_find_best_d(n=5000):
    import time
    import random
    random.seed(42)
    data = [random.randint(0, 100000) for _ in range(n)]

    best_d = 2
    best_time = float('inf')

    for d in [2, 3, 4, 8, 16]:
        h = DaryHeap(d=d)
        t0 = time.perf_counter()
        for val in data:
            h.push(val)
        while h:
            h.pop()
        elapsed = time.perf_counter() - t0
        if elapsed < best_time:
            best_time = elapsed
            best_d = d

    return best_d


def _sol_dijkstra_lazy(adj, source):
    import heapq
    n = len(adj)
    dist = [float('inf')] * n
    dist[source] = 0
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue  # Stale entry — skip
        for v, w in adj[u]:
            new_dist = d + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))

    return dist


def _sol_shortest_path(adj, source, target):
    n = len(adj)
    dist = [float('inf')] * n
    prev = [-1] * n
    dist[source] = 0

    pq = IndexedMinPQ(n)
    pq.push(source, 0)

    while pq:
        u, d = pq.pop()
        if u == target:
            break
        for v, w in adj[u]:
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                if v in pq:
                    pq.decrease_key(v, new_dist)
                else:
                    pq.push(v, new_dist)

    if dist[target] == float('inf'):
        return float('inf'), []

    # Reconstruct path
    path = []
    v = target
    while v != -1:
        path.append(v)
        v = prev[v]
    path.reverse()
    return dist[target], path


def _sol_merge_k_sorted_dary(arrays):
    k = len(arrays)
    d = max(2, k)
    heap = DaryHeap(d=d)

    # Push (value, array_idx, elem_idx)
    for i, arr in enumerate(arrays):
        if arr:
            heap.push((arr[0], i, 0))

    result = []
    while heap:
        val, ai, ei = heap.pop()
        result.append(val)
        if ei + 1 < len(arrays[ai]):
            heap.push((arrays[ai][ei + 1], ai, ei + 1))

    return result


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1
    print("\nExercise 1: D-ary Heapify")
    for fn in [dary_heapify, _sol_dary_heapify]:
        if fn is dary_heapify and fn([3, 1, 2]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}([5,3,8,1,4])", fn([5, 3, 8, 1, 4]), [1, 3, 4, 5, 8])

    # Exercise 2
    print("\nExercise 2: Find Best D")
    for fn in [find_best_d, _sol_find_best_d]:
        if fn is find_best_d and fn(100) is None:
            print("  (skipped — not implemented)")
            break
        d = fn(100)
        check(f"{fn.__name__}(100) returns valid d", d in [2, 3, 4, 8, 16], True)

    # Exercise 3
    print("\nExercise 3: Dijkstra Lazy")
    adj = [[(1, 4), (2, 2)], [(0, 4), (3, 1)], [(0, 2), (3, 5)], [(1, 1), (2, 5)]]
    for fn in [dijkstra_lazy, _sol_dijkstra_lazy]:
        if fn is dijkstra_lazy and fn(adj, 0) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}", fn(adj, 0), [0, 4, 2, 5])

    # Exercise 4
    print("\nExercise 4: Shortest Path")
    adj = [[(1, 4), (2, 2)], [(0, 4), (3, 1)], [(0, 2), (3, 5)], [(1, 1), (2, 5)]]
    for fn in [shortest_path, _sol_shortest_path]:
        if fn is shortest_path and fn(adj, 0, 3) is None:
            print("  (skipped — not implemented)")
            break
        dist, path = fn(adj, 0, 3)
        check(f"{fn.__name__} distance", dist, 5)
        check(f"{fn.__name__} path", path, [0, 1, 3])

    # Exercise 5
    print("\nExercise 5: Merge K Sorted (D-ary)")
    for fn in [merge_k_sorted_dary, _sol_merge_k_sorted_dary]:
        if fn is merge_k_sorted_dary and fn([[1]]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}",
              fn([[1, 4, 7], [2, 5, 8], [3, 6, 9]]),
              [1, 2, 3, 4, 5, 6, 7, 8, 9])

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
