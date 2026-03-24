"""
Day 48 Practice: Splay Tree Exercises
=======================================
Implement each function, then run: python practice.py

These exercises build intuition for amortized analysis and working-set behavior.

Rules:
- Do NOT use any external libraries.
- Solutions are at the bottom — try first.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from splay_tree import SplayTree, Node


# ─── Exercise 1: Count Rotations ───────────────────────────────────
#
# Modify a splay operation to count how many rotations occur when
# searching for a key. Don't modify the original SplayTree — wrap it.
#
# Return the number of rotations performed during a search.
# Hint: a zig is 1 rotation, zig-zig and zig-zag are 2 rotations each.

def count_rotations(tree, key):
    # TODO: return number of rotations to splay `key` to root
    pass


# ─── Exercise 2: Working Set Size ──────────────────────────────────
#
# The "working set" is the number of distinct elements accessed in the
# last k operations. Track accesses and return the working set size.
#
# Example: accesses = [1, 2, 3, 1, 2], k = 3 → working set = {3, 1, 2} → size 3
#          accesses = [1, 2, 3, 1, 2], k = 2 → working set = {1, 2} → size 2

def working_set_size(accesses, k):
    # TODO: return size of working set (distinct elements in last k accesses)
    pass


# ─── Exercise 3: Splay-Based LRU Cache ─────────────────────────────
#
# Build an LRU cache using a splay tree. The key insight: in a splay tree,
# recently accessed elements are near the root, and the least recently
# accessed element sinks toward the bottom.
#
# For eviction, the minimum or maximum node is a good candidate
# (it's been pushed down by splaying other nodes).
#
# Implement a cache with get(key) and put(key, value) with max capacity.

class SplayLRU:
    def __init__(self, capacity):
        self.capacity = capacity
        # TODO: initialize
        pass

    def get(self, key):
        # TODO: return value or -1 if not found. Access splays to root.
        pass

    def put(self, key, value):
        # TODO: insert/update. If over capacity, evict LRU.
        pass


# ─── Exercise 4: Amortized Cost Verification ───────────────────────
#
# Insert n elements (1 to n) in order, then access each element.
# Measure the total number of comparisons across all accesses.
# Verify that total_comparisons / n ≈ O(log n).
#
# Return (total_comparisons, average_per_access)

def measure_amortized_cost(n):
    # TODO: implement
    pass


# ─── Exercise 5: Sequential Access Theorem ─────────────────────────
#
# The sequential access theorem says: accessing all n elements in
# sorted order takes O(n) total time on a splay tree (amortized O(1) each).
#
# Verify this: insert n random elements, then access them in sorted order.
# Return total number of node visits (comparisons) for the sequential scan.
# It should be O(n), NOT O(n log n).

def verify_sequential_access(n):
    # TODO: return total comparisons for accessing all elements in sorted order
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_count_rotations(tree, key):
    """Count rotations by measuring depth before splay."""
    # Find the node's depth before splaying
    depth = 0
    node = tree.root
    while node:
        if key == node.key:
            break
        elif key < node.key:
            node = node.left
        else:
            node = node.right
        depth += 1

    if node is None:
        return 0

    # Splay it (this modifies the tree)
    tree.search(key)

    # Zig: 1 rotation (depth 1)
    # Zig-zig/zig-zag: 2 rotations per pair of levels
    # Total ≈ depth (each level contributes ~1 rotation)
    return depth


def _sol_working_set_size(accesses, k):
    if k <= 0 or not accesses:
        return 0
    window = accesses[-k:] if k <= len(accesses) else accesses
    return len(set(window))


class _SolSplayLRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = SplayTree()
        self.data = {}  # key → value (splay tree handles ordering)
        self.size = 0
        self._time = 0  # logical clock for LRU ordering

    def get(self, key):
        if key not in self.data:
            return -1
        self._time += 1
        # Update access time by reinserting in splay tree
        self.tree.delete(self.data[key][1])  # delete old time key
        self.tree.insert(self._time)
        self.data[key] = (self.data[key][0], self._time)
        return self.data[key][0]

    def put(self, key, value):
        if key in self.data:
            # Update existing
            old_time = self.data[key][1]
            self.tree.delete(old_time)
        elif self.size >= self.capacity:
            # Evict LRU — the minimum time in the splay tree
            lru_time = self.tree.minimum()
            self.tree.delete(lru_time)
            # Find which key has this time
            lru_key = None
            for k, (v, t) in self.data.items():
                if t == lru_time:
                    lru_key = k
                    break
            if lru_key is not None:
                del self.data[lru_key]
                self.size -= 1

        self._time += 1
        self.tree.insert(self._time)
        self.data[key] = (value, self._time)
        self.size += 1


def _sol_measure_amortized_cost(n):
    tree = SplayTree()
    for i in range(1, n + 1):
        tree.insert(i)

    total = 0
    for i in range(1, n + 1):
        # Count depth of node i (approximates comparisons)
        depth = 0
        node = tree.root
        while node and node.key != i:
            if i < node.key:
                node = node.left
            else:
                node = node.right
            depth += 1
        total += depth + 1  # +1 for the comparison at the found node
        tree.search(i)  # Splay to root

    return total, total / n


def _sol_verify_sequential_access(n):
    import random
    random.seed(42)
    tree = SplayTree()
    values = list(range(1, n + 1))
    random.shuffle(values)
    for v in values:
        tree.insert(v)

    # Access in sorted order
    total = 0
    for i in range(1, n + 1):
        depth = 0
        node = tree.root
        while node and node.key != i:
            if i < node.key:
                node = node.left
            else:
                node = node.right
            depth += 1
        total += depth + 1
        tree.search(i)

    return total


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

    def check_range(name, got, lo, hi):
        nonlocal passed, failed
        if lo <= got <= hi:
            passed += 1
            print(f"  ✓ {name} = {got} (in [{lo}, {hi}])")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected in [{lo}, {hi}]")

    # Exercise 1: Count Rotations
    print("\nExercise 1: Count Rotations")
    tree = SplayTree()
    for v in [5, 3, 7, 1, 4, 6, 8]:
        tree.insert(v)
    for fn in [count_rotations, _sol_count_rotations]:
        if fn is count_rotations and fn(SplayTree(), 1) is None:
            print("  (skipped — not implemented)")
            break
        t = SplayTree()
        for v in [5, 3, 7, 1, 4, 6, 8]:
            t.insert(v)
        r = fn(t, 1)
        check_range(f"{fn.__name__}(tree, 1) rotations", r, 0, 10)

    # Exercise 2: Working Set
    print("\nExercise 2: Working Set Size")
    for fn in [working_set_size, _sol_working_set_size]:
        if fn is working_set_size and fn([1, 2], 1) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}([1,2,3,1,2], 3)", fn([1, 2, 3, 1, 2], 3), 3)
        check(f"{fn.__name__}([1,2,3,1,2], 2)", fn([1, 2, 3, 1, 2], 2), 2)
        check(f"{fn.__name__}([1,1,1], 2)", fn([1, 1, 1], 2), 1)

    # Exercise 3: Splay LRU
    print("\nExercise 3: Splay-Based LRU Cache")
    for Cls in [SplayLRU, _SolSplayLRU]:
        cache = Cls(2)
        if not hasattr(cache, 'put') or not hasattr(cache, 'get'):
            print("  (skipped — not implemented)")
            break
        cache.put(1, 10)
        cache.put(2, 20)
        r = cache.get(1)
        if r is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} get(1)", r, 10)
        cache.put(3, 30)  # evicts key 2
        check(f"{Cls.__name__} get(2) after evict", cache.get(2), -1)
        check(f"{Cls.__name__} get(3)", cache.get(3), 30)

    # Exercise 4: Amortized Cost
    print("\nExercise 4: Amortized Cost Verification")
    for fn in [measure_amortized_cost, _sol_measure_amortized_cost]:
        if fn is measure_amortized_cost and fn(10) is None:
            print("  (skipped — not implemented)")
            break
        total, avg = fn(100)
        check_range(f"{fn.__name__}(100) avg", avg, 1, 50)

    # Exercise 5: Sequential Access
    print("\nExercise 5: Sequential Access Theorem")
    for fn in [verify_sequential_access, _sol_verify_sequential_access]:
        if fn is verify_sequential_access and fn(10) is None:
            print("  (skipped — not implemented)")
            break
        total = fn(100)
        # Sequential access should be O(n), so total << n*log(n) = 100*7 = 700
        check_range(f"{fn.__name__}(100) total", total, 1, 2000)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
