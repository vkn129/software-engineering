"""
Day 45 Practice: BST Degradation Exercises
===========================================
Implement each function. Run this file to test your solutions.

Key mental model:
    BST shape = f(insertion order), NOT f(data)
    Same values, different order → O(log n) vs O(n)
    You must MEASURE degradation to understand why balance matters.
"""

import sys
import os
import random
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode

sys.path.insert(0, os.path.dirname(__file__))
from bst_degradation import (
    build_bst_from_sequence, bst_insert, measure_height,
    measure_avg_depth, count_comparisons, is_degenerate,
)


# ─── Exercise 1: Detect Skew Direction ──────────────────────────────
#
# Given a BST root, determine if the tree is skewed and in which direction.
#
# Return:
#   "left"     — every internal node has only a left child (reverse-sorted input)
#   "right"    — every internal node has only a right child (sorted input)
#   "balanced" — the tree has at least one node with two children
#   "empty"    — the tree is None
#
# A single-node tree is "balanced" (no skew).
#
# Why this matters: knowing the skew direction tells you what input pattern
# caused the degradation (sorted vs reverse-sorted).

def detect_skew(root):
    # TODO: implement
    pass


# ─── Exercise 2: Count Nodes at Each Depth ──────────────────────────
#
# Return a list where index i contains the number of nodes at depth i.
#
# Example:
#         4
#        / \
#       2   6
#      /
#     1
#
# Result: [1, 2, 1]  (depth 0: 1 node, depth 1: 2 nodes, depth 2: 1 node)
#
# For a degenerate tree of n nodes: [1, 1, 1, ..., 1]  (n entries)
# For a perfect tree of height h: [1, 2, 4, ..., 2^h]
#
# This distribution reveals degradation: a healthy tree has exponentially
# growing counts, a degenerate tree has flat counts of 1.

def nodes_per_depth(root):
    # TODO: implement (hint: BFS is natural here)
    pass


# ─── Exercise 3: Minimum Insertions to Degenerate ───────────────────
#
# Given n, find the MINIMUM number of distinct sequences of n values
# that produce a degenerate (linked-list) BST.
#
# Actually, count HOW MANY permutations of [1..n] produce a degenerate BST.
#
# For n=1: 1 (just [1])
# For n=2: 2 ([1,2] and [2,1])
# For n=3: 4 ([1,2,3], [1,3,2] wait... no. Think carefully.)
#
# A degenerate BST means every node has at most one child.
# For [1..n], the degenerate sequences are exactly those where each
# new element is either the current min-1 or current max+1 of the
# already-inserted values. The first element can be anything from 1..n,
# but wait — not quite. Think about which first elements allow a full chain.
#
# Actually: for [1..n], a permutation produces a degenerate BST if and
# only if each inserted value extends the current range by 1 at either end.
# This means after the first element k, we must alternately pick from
# {k-1, k+1}, then {k-2, k+1} or {k-1, k+2}, etc.
#
# The count is 2^(n-1) for n >= 1.
#
# Implement a function that VERIFIES this by brute force for small n:
# generate all permutations of [1..n], build BST, check if degenerate.

def count_degenerate_permutations(n):
    # TODO: implement (brute force is fine for n <= 8)
    pass


# ─── Exercise 4: Rebalance an Existing BST ──────────────────────────
#
# Given the root of a (possibly degenerate) BST, rebalance it into
# a height-balanced BST containing the same values.
#
# Strategy (two-pass):
#   1. Inorder traversal to extract sorted values (BST property!)
#   2. Build balanced BST from sorted array (insert medians recursively)
#
# The second step is different from optimal_insertion_order:
# instead of computing an insertion order, directly BUILD the tree
# by choosing the median as root and recursing on halves.
#
# This is O(n) time and produces a perfectly balanced tree.
#
# Return the new root.

def rebalance_bst(root):
    # TODO: implement
    pass


# ─── Exercise 5: Height-to-Node Ratio ───────────────────────────────
#
# Compute the "degradation ratio" of a BST:
#   ratio = height / floor(log2(n))
#
# Where n is the number of nodes.
#
# Interpretation:
#   ratio = 1.0  → perfectly balanced (height = log2(n))
#   ratio ≈ 2-3  → reasonably balanced (typical for random BSTs)
#   ratio >> 10  → severely degraded
#   ratio = n/log2(n) → completely degenerate
#
# Return the ratio as a float, or 0.0 for empty/single-node trees
# (where the metric is undefined).

def degradation_ratio(root):
    # TODO: implement
    pass


# ─── Reference Solutions ─────────────────────────────────────────────

def _sol_detect_skew(root):
    if root is None:
        return "empty"

    # Single node — no skew
    if root.left is None and root.right is None:
        return "balanced"

    current = root
    has_left_only = True
    has_right_only = True

    while current is not None:
        has_left = current.left is not None
        has_right = current.right is not None

        if has_left and has_right:
            return "balanced"

        if has_right:
            has_left_only = False
        if has_left:
            has_right_only = False

        current = current.left if has_left else current.right

    if has_right_only:
        return "right"
    elif has_left_only:
        return "left"
    else:
        # Mixed single-child directions but never two children
        # This is still degenerate but not purely left or right
        return "balanced"


def _sol_nodes_per_depth(root):
    if root is None:
        return []

    from collections import deque
    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        result.append(level_size)
        for _ in range(level_size):
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result


def _sol_count_degenerate_permutations(n):
    from itertools import permutations

    if n == 0:
        return 0

    count = 0
    for perm in permutations(range(1, n + 1)):
        root = build_bst_from_sequence(perm)
        if is_degenerate(root):
            count += 1
    return count


def _sol_rebalance_bst(root):
    # Step 1: inorder traversal to get sorted values
    values = []

    def _inorder(node):
        if node is None:
            return
        _inorder(node.left)
        values.append(node.val)
        _inorder(node.right)

    _inorder(root)

    # Step 2: build balanced BST from sorted array
    def _build(arr, start, end):
        if start > end:
            return None
        mid = (start + end) // 2
        node = TreeNode(arr[mid])
        node.left = _build(arr, start, mid - 1)
        node.right = _build(arr, mid + 1, end)
        return node

    if not values:
        return None
    return _build(values, 0, len(values) - 1)


def _sol_degradation_ratio(root):
    if root is None:
        return 0.0

    # Count nodes
    def _count(node):
        if node is None:
            return 0
        return 1 + _count(node.left) + _count(node.right)

    n = _count(root)
    if n <= 1:
        return 0.0

    h = measure_height(root)
    optimal_h = math.floor(math.log2(n))

    if optimal_h == 0:
        return 0.0

    return h / optimal_h


# ─── Test Runner ─────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")
            failed += 1

    def check_approx(name, got, expected, tolerance=0.01):
        nonlocal passed, failed
        if abs(got - expected) <= tolerance:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    Expected: ~{expected} (tolerance {tolerance})")
            print(f"    Got:      {got}")
            failed += 1

    # ── Exercise 1: Detect Skew Direction ──
    print("\n── Exercise 1: Detect Skew Direction ──")
    fn1 = detect_skew if detect_skew(build_bst_from_sequence([1, 2, 3])) is not None else _sol_detect_skew

    check("sorted [1,2,3] → right", fn1(build_bst_from_sequence([1, 2, 3])), "right")
    check("reverse [3,2,1] → left", fn1(build_bst_from_sequence([3, 2, 1])), "left")
    check("balanced [2,1,3]", fn1(build_bst_from_sequence([2, 1, 3])), "balanced")
    check("single node", fn1(build_bst_from_sequence([42])), "balanced")
    check("empty", fn1(None), "empty")
    check("sorted [1,2,3,4,5] → right", fn1(build_bst_from_sequence([1, 2, 3, 4, 5])), "right")
    check("reverse [5,4,3,2,1] → left", fn1(build_bst_from_sequence([5, 4, 3, 2, 1])), "left")

    # ── Exercise 2: Nodes at Each Depth ──
    print("\n── Exercise 2: Nodes at Each Depth ──")
    fn2 = nodes_per_depth if nodes_per_depth(build_bst_from_sequence([4, 2, 6, 1])) is not None else _sol_nodes_per_depth

    check("balanced-ish tree",
          fn2(build_bst_from_sequence([4, 2, 6, 1, 3, 5, 7])),
          [1, 2, 4])
    check("degenerate [1,2,3,4]",
          fn2(build_bst_from_sequence([1, 2, 3, 4])),
          [1, 1, 1, 1])
    check("single node",
          fn2(build_bst_from_sequence([5])),
          [1])
    check("empty",
          fn2(None),
          [])
    check("two levels",
          fn2(build_bst_from_sequence([3, 1, 5])),
          [1, 2])

    # ── Exercise 3: Degenerate Permutation Count ──
    print("\n── Exercise 3: Degenerate Permutation Count ──")
    fn3 = count_degenerate_permutations if count_degenerate_permutations(1) is not None else _sol_count_degenerate_permutations

    check("n=1", fn3(1), 1)
    check("n=2", fn3(2), 2)
    check("n=3", fn3(3), 4)
    check("n=4", fn3(4), 8)
    # Pattern: 2^(n-1)
    check("n=5 (should be 16)", fn3(5), 16)

    # ── Exercise 4: Rebalance BST ──
    print("\n── Exercise 4: Rebalance BST ──")
    fn4 = rebalance_bst

    # Test: rebalance detects None return → use solution if needed
    test_root = build_bst_from_sequence([1, 2, 3, 4, 5, 6, 7])
    test_result = fn4(test_root)
    if test_result is None:
        fn4 = _sol_rebalance_bst

    # Rebalance a degenerate tree
    degen = build_bst_from_sequence([1, 2, 3, 4, 5, 6, 7])
    check("degenerate before", is_degenerate(degen), True)
    check("degenerate height before", measure_height(degen), 6)

    rebal = fn4(degen)
    check("rebalanced height", measure_height(rebal), 2)
    check("rebalanced not degenerate", is_degenerate(rebal), False)

    # Verify BST property preserved (inorder should be sorted)
    def inorder(node):
        if node is None:
            return []
        return inorder(node.left) + [node.val] + inorder(node.right)

    check("BST property preserved", inorder(rebal), [1, 2, 3, 4, 5, 6, 7])

    # Rebalance already balanced tree
    balanced = build_bst_from_sequence([4, 2, 6, 1, 3, 5, 7])
    rebal2 = fn4(balanced)
    check("already balanced → still balanced", measure_height(rebal2), 2)
    check("values preserved", inorder(rebal2), [1, 2, 3, 4, 5, 6, 7])

    # Empty tree
    check("empty tree", fn4(None), None)

    # Single node
    single = fn4(build_bst_from_sequence([42]))
    check("single node value", single.val, 42)

    # ── Exercise 5: Degradation Ratio ──
    print("\n── Exercise 5: Degradation Ratio ──")
    fn5 = degradation_ratio if degradation_ratio(build_bst_from_sequence([1, 2, 3, 4])) is not None else _sol_degradation_ratio

    # Perfectly balanced: height = 2, log2(7) = 2, ratio = 1.0
    check_approx("perfect tree ratio",
                 fn5(build_bst_from_sequence([4, 2, 6, 1, 3, 5, 7])),
                 1.0)

    # Degenerate [1..15]: height = 14, log2(15) = 3, ratio = 14/3 ≈ 4.67
    check_approx("degenerate ratio",
                 fn5(build_bst_from_sequence(range(1, 16))),
                 14.0 / 3.0, tolerance=0.1)

    # Empty / single node → 0.0
    check_approx("empty", fn5(None), 0.0)
    check_approx("single node", fn5(build_bst_from_sequence([1])), 0.0)

    # Random tree should have ratio between 1 and 4
    random.seed(123)
    rand_tree = build_bst_from_sequence(random.sample(range(1, 128), 127))
    ratio = fn5(rand_tree)
    ratio_ok = 1.0 <= ratio <= 4.0
    check("random tree ratio in [1, 4]", ratio_ok, True)

    # ── Summary ──
    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All exercises complete!")
    else:
        print(f"{failed} exercises need work — implement the TODO functions above")


if __name__ == "__main__":
    run_tests()
