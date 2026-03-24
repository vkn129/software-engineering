"""
Day 57 Practice: Segment Tree Exercises
========================================
Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from segment_tree import SegmentTree, LazySegmentTree


# ─── Exercise 1: Range Minimum Query ────────────────────────────────
#
# Adapt the segment tree for range minimum queries. Given an array,
# answer queries of the form "what is the minimum value in [l, r]?"
#
# The key change: the merge operation is min() instead of +,
# and the identity element is float('inf') (any real value is less).
#
# Example:
#   arr = [3, 1, 4, 1, 5, 9, 2, 6]
#   rmq(0, 3) → 1   (min of [3, 1, 4, 1])
#   rmq(4, 7) → 2   (min of [5, 9, 2, 6])

def build_rmq(arr):
    """Return a SegmentTree configured for range minimum queries."""
    # TODO: create and return a SegmentTree with the right merge/identity
    pass

def rmq(tree, l, r):
    """Query minimum in [l, r] using the tree from build_rmq."""
    # TODO: use tree.query
    pass


# ─── Exercise 2: Count Elements in Range [lo, hi] ──────────────────
#
# Given an array of integers, count how many elements in subarray
# [l, r] fall within value range [lo, hi].
#
# Approach: coordinate compression + multiple segment trees, OR
# a simpler approach: build a segment tree where each query counts
# elements satisfying a predicate.
#
# Simpler approach for this exercise: sort + binary search + BIT/segment tree.
# But the most instructive approach is: for each unique value v, maintain
# a prefix count. Then count_in_range(l, r, lo, hi) =
#   count of elements in [l,r] with value in [lo, hi].
#
# Easiest correct approach: build a segment tree on a 0/1 array where
# arr[i] = 1 if original[i] is in [lo, hi], else 0. This gives O(n) build
# per query. For multiple queries with same [lo, hi], this is fine.
#
# Example:
#   arr = [3, 1, 4, 1, 5, 9, 2, 6]
#   count_in_range(arr, 0, 7, 2, 5) → 4  (elements 3, 4, 5, 2 are in [2,5])

def count_in_range(arr, l, r, lo, hi):
    """
    Count elements in arr[l..r] whose values are in [lo, hi].
    Use a segment tree on a filtered 0/1 array.
    """
    # TODO: build a segment tree on [1 if lo <= x <= hi else 0 for x in arr]
    # then query [l, r]
    pass


# ─── Exercise 3: Range Update + Range Query ─────────────────────────
#
# Use LazySegmentTree to solve this classic problem:
# Given an array, support two operations:
#   1. add(l, r, val) — add val to all elements in [l, r]
#   2. query(l, r) — return sum of elements in [l, r]
#
# This is exactly what LazySegmentTree does. The exercise is to
# use it correctly and verify understanding.
#
# Example:
#   arr = [1, 2, 3, 4, 5]
#   add(1, 3, 10)  → arr becomes [1, 12, 13, 14, 5]
#   query(0, 4)    → 45
#   add(0, 4, -1)  → arr becomes [0, 11, 12, 13, 4]
#   query(2, 3)    → 25

class RangeAddRangeSum:
    def __init__(self, arr):
        # TODO: initialize using LazySegmentTree
        pass

    def add(self, l, r, val):
        # TODO: range update
        pass

    def query(self, l, r):
        # TODO: range query
        pass


# ─── Exercise 4: Merge Sort Tree ────────────────────────────────────
#
# A merge sort tree is a segment tree where each node stores the SORTED
# subarray for its range (not just a single aggregate). This enables:
#   - Count of elements < k in range [l, r]   → O(log^2 n)
#   - Kth smallest element in range [l, r]     → O(log^3 n) with binary search
#
# Structure:
#   Leaves store [arr[i]]
#   Internal nodes store sorted merge of children's arrays
#   (This is literally the merge step of merge sort, hence the name)
#
# Space: O(n log n) — each element appears in O(log n) nodes
# Build: O(n log n) — merge at each of O(log n) levels
#
# Example:
#   arr = [3, 1, 4, 1, 5, 9]
#   count_less_than(0, 5, 4) → 3  (elements 3, 1, 1 are < 4)
#   count_less_than(2, 5, 5) → 2  (elements 4, 1 are < 5)

class MergeSortTree:
    def __init__(self, arr):
        # TODO: build the merge sort tree
        # self.n = len(arr)
        # self.tree = [[] for _ in range(4 * self.n)]
        # self._build(arr, 1, 0, self.n - 1)
        pass

    def _build(self, arr, node, start, end):
        # TODO: leaves = [arr[start]], internal = sorted merge of children
        pass

    def count_less_than(self, l, r, k):
        """Count elements in arr[l..r] that are strictly less than k."""
        # TODO: query the tree, using bisect on each visited node's sorted array
        pass

    def _query(self, node, start, end, l, r, k):
        # TODO: implement
        pass


# ─── Exercise 5: Persistent Segment Tree (Conceptual) ───────────────
#
# A persistent segment tree keeps ALL previous versions after updates.
# Key insight: a point update only changes O(log n) nodes (the path
# from root to the updated leaf). So we create new nodes only for that
# path and reuse all other nodes from the previous version.
#
# This gives:
#   - O(log n) time per update (same as regular)
#   - O(log n) extra space per update (only new path nodes)
#   - O(log n) query on ANY historical version
#
# Implementation: instead of array-based storage, use node objects with
# left/right pointers. Each version is identified by its root node.
#
# Example:
#   v0: build([1, 2, 3, 4, 5])
#   v1: update(v0, index=2, val=10) → creates new path, old tree intact
#   query(v0, 0, 4) → 15  (original)
#   query(v1, 0, 4) → 22  (with index 2 changed to 10)

class PersistentSegTree:
    """
    Persistent segment tree using linked nodes.
    Each update creates a new version by copying only the O(log n)
    nodes on the root-to-leaf path.
    """

    class Node:
        __slots__ = ('val', 'left', 'right')

        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def __init__(self, arr):
        # TODO: build initial tree, store root as version 0
        # self.n = len(arr)
        # self.versions = []
        # root = self._build(arr, 0, self.n - 1)
        # self.versions.append(root)
        pass

    def _build(self, arr, start, end):
        # TODO: recursive build returning Node
        pass

    def update(self, version, idx, val):
        """
        Create a new version by updating index idx to val.
        Returns the version number of the new version.
        """
        # TODO: create new path nodes, reuse unchanged subtrees
        pass

    def _update(self, prev, start, end, idx, val):
        # TODO: if this node is on the update path, create new node
        # otherwise reuse prev
        pass

    def query(self, version, l, r):
        """Query sum on range [l, r] for the given version."""
        # TODO: standard range query on the version's root
        pass

    def _query(self, node, start, end, l, r):
        # TODO: implement
        pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_build_rmq(arr):
    return SegmentTree(arr, merge=min, identity=float('inf'))

def _sol_rmq(tree, l, r):
    return tree.query(l, r)


def _sol_count_in_range(arr, l, r, lo, hi):
    # Build a 0/1 array: 1 if value in [lo, hi], else 0
    filtered = [1 if lo <= x <= hi else 0 for x in arr]
    tree = SegmentTree(filtered)
    return tree.query(l, r)


class _SolRangeAddRangeSum:
    def __init__(self, arr):
        self.tree = LazySegmentTree(arr)

    def add(self, l, r, val):
        self.tree.range_update(l, r, val)

    def query(self, l, r):
        return self.tree.query(l, r)


import bisect

class _SolMergeSortTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [[] for _ in range(4 * self.n)]
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = [arr[start]]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node, start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        # Merge two sorted arrays — this IS the merge step of merge sort
        left, right = self.tree[2 * node], self.tree[2 * node + 1]
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        self.tree[node] = merged

    def count_less_than(self, l, r, k):
        if l > r:
            return 0
        return self._query(1, 0, self.n - 1, l, r, k)

    def _query(self, node, start, end, l, r, k):
        if l > end or r < start:
            return 0
        if l <= start and end <= r:
            # Count elements < k using binary search on sorted array
            return bisect.bisect_left(self.tree[node], k)
        mid = (start + end) // 2
        return (self._query(2 * node, start, mid, l, r, k) +
                self._query(2 * node + 1, mid + 1, end, l, r, k))


class _SolPersistentSegTree:
    class Node:
        __slots__ = ('val', 'left', 'right')

        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right

    def __init__(self, arr):
        self.n = len(arr)
        self.versions = []
        if self.n > 0:
            root = self._build(arr, 0, self.n - 1)
            self.versions.append(root)

    def _build(self, arr, start, end):
        if start == end:
            return self.Node(val=arr[start])
        mid = (start + end) // 2
        left = self._build(arr, start, mid)
        right = self._build(arr, mid + 1, end)
        return self.Node(val=left.val + right.val, left=left, right=right)

    def update(self, version, idx, val):
        old_root = self.versions[version]
        new_root = self._update(old_root, 0, self.n - 1, idx, val)
        self.versions.append(new_root)
        return len(self.versions) - 1

    def _update(self, prev, start, end, idx, val):
        if start == end:
            # New leaf with updated value
            return self.Node(val=val)
        mid = (start + end) // 2
        if idx <= mid:
            # Update goes left — create new left child, reuse right
            new_left = self._update(prev.left, start, mid, idx, val)
            return self.Node(
                val=new_left.val + prev.right.val,
                left=new_left,
                right=prev.right  # REUSE — this is what makes it persistent
            )
        else:
            # Update goes right — reuse left, create new right child
            new_right = self._update(prev.right, mid + 1, end, idx, val)
            return self.Node(
                val=prev.left.val + new_right.val,
                left=prev.left,  # REUSE
                right=new_right
            )

    def query(self, version, l, r):
        if not self.versions:
            return 0
        return self._query(self.versions[version], 0, self.n - 1, l, r)

    def _query(self, node, start, end, l, r):
        if node is None or l > end or r < start:
            return 0
        if l <= start and end <= r:
            return node.val
        mid = (start + end) // 2
        return (self._query(node.left, start, mid, l, r) +
                self._query(node.right, mid + 1, end, l, r))


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0
    skipped = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  \u2713 {name}")
        else:
            failed += 1
            print(f"  \u2717 {name}: got {got}, expected {expected}")

    def is_unimplemented(val):
        return val is None

    # Exercise 1: Range Minimum Query
    print("\nExercise 1: Range Minimum Query")
    arr1 = [3, 1, 4, 1, 5, 9, 2, 6]
    user_tree = build_rmq(arr1)
    if is_unimplemented(user_tree):
        print("  \u2b1c not implemented yet")
        skipped += 1
    else:
        user_result = rmq(user_tree, 0, 3)
        if is_unimplemented(user_result):
            print("  \u2b1c not implemented yet")
            skipped += 1
        else:
            check("rmq(0, 3) = 1", user_result, 1)
            check("rmq(4, 7) = 2", rmq(user_tree, 4, 7), 2)
            check("rmq(0, 7) = 1", rmq(user_tree, 0, 7), 1)
            check("rmq(5, 5) = 9", rmq(user_tree, 5, 5), 9)

    # Verify with solution
    sol_tree = _sol_build_rmq(arr1)
    check("sol rmq(0, 3) = 1", _sol_rmq(sol_tree, 0, 3), 1)
    check("sol rmq(4, 7) = 2", _sol_rmq(sol_tree, 4, 7), 2)

    # Exercise 2: Count Elements in Value Range
    print("\nExercise 2: Count Elements in Range [lo, hi]")
    arr2 = [3, 1, 4, 1, 5, 9, 2, 6]
    user_result = count_in_range(arr2, 0, 7, 2, 5)
    if is_unimplemented(user_result):
        print("  \u2b1c not implemented yet")
        skipped += 1
    else:
        check("count_in_range(0,7, 2,5) = 4", user_result, 4)
        check("count_in_range(0,3, 1,1) = 2", count_in_range(arr2, 0, 3, 1, 1), 2)
        check("count_in_range(4,7, 6,10) = 2", count_in_range(arr2, 4, 7, 6, 10), 2)

    check("sol count(0,7, 2,5) = 4", _sol_count_in_range(arr2, 0, 7, 2, 5), 4)
    check("sol count(0,3, 1,1) = 2", _sol_count_in_range(arr2, 0, 3, 1, 1), 2)

    # Exercise 3: Range Update + Range Query
    print("\nExercise 3: Range Update + Range Query")
    arr3 = [1, 2, 3, 4, 5]
    try:
        user_rars = RangeAddRangeSum(arr3)
        user_rars.add(1, 3, 10)
        result = user_rars.query(0, 4)
        if is_unimplemented(result):
            print("  \u2b1c not implemented yet")
            skipped += 1
        else:
            check("after add(1,3,10): query(0,4) = 45", result, 45)
            user_rars.add(0, 4, -1)
            check("after add(0,4,-1): query(2,3) = 25", user_rars.query(2, 3), 25)
    except (TypeError, AttributeError):
        print("  \u2b1c not implemented yet")
        skipped += 1

    sol_rars = _SolRangeAddRangeSum(arr3)
    sol_rars.add(1, 3, 10)
    check("sol add(1,3,10): query(0,4) = 45", sol_rars.query(0, 4), 45)
    sol_rars.add(0, 4, -1)
    check("sol add(0,4,-1): query(2,3) = 25", sol_rars.query(2, 3), 25)

    # Exercise 4: Merge Sort Tree
    print("\nExercise 4: Merge Sort Tree")
    arr4 = [3, 1, 4, 1, 5, 9]
    try:
        user_mst = MergeSortTree(arr4)
        result = user_mst.count_less_than(0, 5, 4)
        if is_unimplemented(result):
            print("  \u2b1c not implemented yet")
            skipped += 1
        else:
            check("count_less_than(0,5, 4) = 3", result, 3)
            check("count_less_than(2,5, 5) = 2", user_mst.count_less_than(2, 5, 5), 2)
            check("count_less_than(0,5, 10) = 6", user_mst.count_less_than(0, 5, 10), 6)
    except (TypeError, AttributeError):
        print("  \u2b1c not implemented yet")
        skipped += 1

    sol_mst = _SolMergeSortTree(arr4)
    check("sol count_less_than(0,5, 4) = 3", sol_mst.count_less_than(0, 5, 4), 3)
    check("sol count_less_than(2,5, 5) = 2", sol_mst.count_less_than(2, 5, 5), 2)

    # Exercise 5: Persistent Segment Tree
    print("\nExercise 5: Persistent Segment Tree")
    arr5 = [1, 2, 3, 4, 5]
    try:
        user_pst = PersistentSegTree(arr5)
        v1 = user_pst.update(0, 2, 10)
        result_v0 = user_pst.query(0, 0, 4)
        if is_unimplemented(v1) or is_unimplemented(result_v0):
            print("  \u2b1c not implemented yet")
            skipped += 1
        else:
            check("query(v0, 0, 4) = 15", result_v0, 15)
            check("query(v1, 0, 4) = 22", user_pst.query(v1, 0, 4), 22)
            check("query(v0, 2, 2) = 3", user_pst.query(0, 2, 2), 3)
            check("query(v1, 2, 2) = 10", user_pst.query(v1, 2, 2), 10)
    except (TypeError, AttributeError, IndexError):
        print("  \u2b1c not implemented yet")
        skipped += 1

    sol_pst = _SolPersistentSegTree(arr5)
    sv1 = sol_pst.update(0, 2, 10)
    check("sol query(v0, 0, 4) = 15", sol_pst.query(0, 0, 4), 15)
    check("sol query(v1, 0, 4) = 22", sol_pst.query(sv1, 0, 4), 22)
    check("sol v0 unchanged after update: query(v0, 2, 2) = 3", sol_pst.query(0, 2, 2), 3)
    check("sol v1 has update: query(v1, 2, 2) = 10", sol_pst.query(sv1, 2, 2), 10)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} not yet implemented")
    if skipped > 0:
        print(f"\nHint: exercises marked \u2b1c are waiting for your implementation!")


if __name__ == "__main__":
    run_tests()
