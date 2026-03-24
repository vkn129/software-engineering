"""
Day 44 Practice: BST <-> Sorted Structure Conversions
======================================================
Implement each function. Run this file to test your solutions.

Key insight: a BST's inorder traversal is sorted, and a sorted sequence
can reconstruct a balanced BST. Every conversion exploits this duality.

    BST -> sorted array:   inorder traversal
    sorted array -> BST:   pick middle as root, recurse on halves
    BST -> DLL:            inorder with pointer rewiring
    merge two BSTs:        sorted arrays -> merge -> balanced BST
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list, inorder_recursive


# ─── Exercise 1: Sorted Array to Balanced BST ─────────────────────────
#
# Given a sorted (ascending) array of unique integers, build a
# height-balanced BST.
#
# "Height-balanced" means for every node, the depth of the left and
# right subtrees differ by at most 1.
#
# Strategy: the middle element becomes the root. The left half of the
# array becomes the left subtree, the right half becomes the right
# subtree. Recurse.
#
# Example:
#   [1, 2, 3, 4, 5, 6, 7] ->
#           4
#          / \
#         2   6
#        / \ / \
#       1  3 5  7
#
# Time: O(n), Space: O(log n) recursion

def sorted_array_to_bst(arr):
    # TODO: implement
    pass


# ─── Exercise 2: BST to Sorted Array ──────────────────────────────────
#
# Given the root of a BST, return all values in sorted order.
#
# This is just inorder traversal. The BST property guarantees
# left < root < right, so inorder = sorted.
#
# Time: O(n), Space: O(n)

def bst_to_sorted_array(root):
    # TODO: implement
    pass


# ─── Exercise 3: Merge Two BSTs into One Balanced BST ─────────────────
#
# Given roots of two BSTs, merge them into a single balanced BST
# containing all elements from both trees.
#
# Strategy:
#   1. Convert both BSTs to sorted arrays
#   2. Merge the two sorted arrays (like merge step in merge sort)
#   3. Convert merged sorted array to balanced BST
#
# Time: O(m + n), Space: O(m + n)

def merge_two_bsts(root1, root2):
    # TODO: implement
    pass


# ─── Exercise 4: Balance an Unbalanced BST ────────────────────────────
#
# Given a BST that may be unbalanced (possibly degenerate/skewed),
# return a new height-balanced BST with the same elements.
#
# Strategy: extract sorted array via inorder, then build balanced BST.
# This is the "sledgehammer" approach — simple and O(n).
#
# Time: O(n), Space: O(n)

def balance_bst(root):
    # TODO: implement
    pass


# ─── Exercise 5: Flatten BST to Right-Skewed Sorted List ──────────────
#
# Given a BST, flatten it IN-PLACE so that every node has:
#   - left = None
#   - right = next node in sorted order
#
# The result is a right-skewed "linked list" using tree nodes.
# Return the head (smallest element).
#
# Example:
#       4            1
#      / \            \
#     2   5    ->      2
#    / \                \
#   1   3                3
#                         \
#                          4
#                           \
#                            5
#
# Hint: collect nodes via inorder, then rewire pointers.
# Time: O(n), Space: O(n)

def flatten_bst(root):
    # TODO: implement
    pass


# ─── Exercise 6: Kth Smallest from Sorted Array Construction ──────────
#
# Given a sorted array and k (1-indexed), find the kth smallest element.
# BUT: you must do it by building a balanced BST first, then performing
# an inorder walk counting to k.
#
# This is intentionally roundabout — the point is to practice both
# conversions in sequence and verify correctness.
#
# Return None if k is out of range.
#
# Time: O(n) build + O(k) walk = O(n)

def kth_via_bst(arr, k):
    # TODO: implement
    pass


# ─── Reference Solutions ──────────────────────────────────────────────

def _sol_sorted_array_to_bst(arr):
    if not arr:
        return None

    def build(lo, hi):
        if lo > hi:
            return None
        mid = lo + (hi - lo) // 2
        node = TreeNode(arr[mid])
        node.left = build(lo, mid - 1)
        node.right = build(mid + 1, hi)
        return node

    return build(0, len(arr) - 1)


def _sol_bst_to_sorted_array(root):
    result = []
    def inorder(node):
        if node is None:
            return
        inorder(node.left)
        result.append(node.val)
        inorder(node.right)
    inorder(root)
    return result


def _sol_merge_two_bsts(root1, root2):
    arr1 = _sol_bst_to_sorted_array(root1)
    arr2 = _sol_bst_to_sorted_array(root2)

    # Merge two sorted arrays
    merged = []
    i, j = 0, 0
    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            merged.append(arr1[i])
            i += 1
        else:
            merged.append(arr2[j])
            j += 1
    merged.extend(arr1[i:])
    merged.extend(arr2[j:])

    return _sol_sorted_array_to_bst(merged)


def _sol_balance_bst(root):
    arr = _sol_bst_to_sorted_array(root)
    return _sol_sorted_array_to_bst(arr)


def _sol_flatten_bst(root):
    if root is None:
        return None
    nodes = []
    def inorder(node):
        if node is None:
            return
        inorder(node.left)
        nodes.append(node)
        inorder(node.right)
    inorder(root)
    for i in range(len(nodes) - 1):
        nodes[i].left = None
        nodes[i].right = nodes[i + 1]
    nodes[-1].left = None
    nodes[-1].right = None
    return nodes[0]


def _sol_kth_via_bst(arr, k):
    if not arr or k < 1 or k > len(arr):
        return None
    root = _sol_sorted_array_to_bst(arr)
    count = [0]
    result = [None]
    def inorder(node):
        if node is None or result[0] is not None:
            return
        inorder(node.left)
        count[0] += 1
        if count[0] == k:
            result[0] = node.val
            return
        inorder(node.right)
    inorder(root)
    return result[0]


# ─── Test Helpers ─────────────────────────────────────────────────────

def _get_height(node):
    if node is None:
        return -1
    return 1 + max(_get_height(node.left), _get_height(node.right))


def _is_balanced(node):
    def check(n):
        if n is None:
            return 0, True
        lh, lb = check(n.left)
        rh, rb = check(n.right)
        return 1 + max(lh, rh), lb and rb and abs(lh - rh) <= 1
    _, result = check(node)
    return result


def _is_bst(node, lo=float('-inf'), hi=float('inf')):
    if node is None:
        return True
    if node.val <= lo or node.val >= hi:
        return False
    return _is_bst(node.left, lo, node.val) and _is_bst(node.right, node.val, hi)


def _collect_right_skewed(root):
    result = []
    while root:
        if root.left is not None:
            return None  # not properly flattened
        result.append(root.val)
        root = root.right
    return result


# ─── Test Runner ──────────────────────────────────────────────────────

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

    def pick_tree_fn(user_fn, sol_fn, *probe_args):
        """Use user's function if it returns non-None on probe, else solution."""
        result = user_fn(*probe_args)
        return user_fn if result is not None else sol_fn

    def pick_fn(user_fn, sol_fn, *probe_args):
        """Use user's function if it returns non-None on probe, else solution."""
        result = user_fn(*probe_args)
        return user_fn if result is not None else sol_fn

    # ── Exercise 1: Sorted Array -> Balanced BST ──
    print("\n── Exercise 1: Sorted Array -> Balanced BST ──")
    fn1 = pick_tree_fn(sorted_array_to_bst, _sol_sorted_array_to_bst, [1, 2, 3])

    tree = fn1([1, 2, 3, 4, 5, 6, 7])
    check("7 elements — inorder correct",
          inorder_recursive(tree), [1, 2, 3, 4, 5, 6, 7])
    check("7 elements — balanced",
          _is_balanced(tree), True)
    check("7 elements — valid BST",
          _is_bst(tree), True)
    check("7 elements — height is 2",
          _get_height(tree), 2)

    tree2 = fn1([1])
    check("single element",
          inorder_recursive(tree2), [1])

    tree3 = fn1([])
    check("empty array",
          tree3, None)

    tree4 = fn1([1, 2, 3, 4, 5])
    check("5 elements — inorder correct",
          inorder_recursive(tree4), [1, 2, 3, 4, 5])
    check("5 elements — balanced",
          _is_balanced(tree4), True)

    tree5 = fn1([10, 20])
    check("2 elements — inorder correct",
          inorder_recursive(tree5), [10, 20])
    check("2 elements — balanced",
          _is_balanced(tree5), True)

    # ── Exercise 2: BST -> Sorted Array ──
    print("\n── Exercise 2: BST -> Sorted Array ──")
    fn2 = pick_fn(bst_to_sorted_array, _sol_bst_to_sorted_array,
                  from_list([4, 2, 6, 1, 3, 5, 7]))

    check("complete BST",
          fn2(from_list([4, 2, 6, 1, 3, 5, 7])),
          [1, 2, 3, 4, 5, 6, 7])
    check("single node",
          fn2(from_list([42])),
          [42])
    check("empty tree",
          fn2(None),
          [])
    check("left-skewed",
          fn2(from_list([3, 2, None, 1])),
          [1, 2, 3])
    check("right-skewed",
          fn2(from_list([1, None, 2, None, 3])),
          [1, 2, 3])

    # ── Exercise 3: Merge Two BSTs ──
    print("\n── Exercise 3: Merge Two BSTs ──")
    fn3 = pick_tree_fn(merge_two_bsts, _sol_merge_two_bsts,
                       from_list([2, 1, 3]), from_list([6, 5, 7]))

    merged = fn3(from_list([2, 1, 3]), from_list([6, 5, 7]))
    check("disjoint BSTs — inorder correct",
          inorder_recursive(merged), [1, 2, 3, 5, 6, 7])
    check("disjoint BSTs — balanced",
          _is_balanced(merged), True)
    check("disjoint BSTs — valid BST",
          _is_bst(merged), True)

    merged2 = fn3(from_list([4, 2, 6]), from_list([3, 1, 5]))
    check("interleaved BSTs — inorder correct",
          inorder_recursive(merged2), [1, 2, 3, 4, 5, 6])
    check("interleaved BSTs — balanced",
          _is_balanced(merged2), True)

    merged3 = fn3(from_list([5]), None)
    check("one empty BST",
          inorder_recursive(merged3), [5])

    merged4 = fn3(None, None)
    check("both empty",
          merged4, None)

    # ── Exercise 4: Balance BST ──
    print("\n── Exercise 4: Balance BST ──")
    # Build a right-skewed tree manually
    skewed = TreeNode(1)
    skewed.right = TreeNode(2)
    skewed.right.right = TreeNode(3)
    skewed.right.right.right = TreeNode(4)
    skewed.right.right.right.right = TreeNode(5)

    fn4 = pick_tree_fn(balance_bst, _sol_balance_bst, skewed)

    # Rebuild the skewed tree (fn4 may have mutated it)
    skewed = TreeNode(1)
    skewed.right = TreeNode(2)
    skewed.right.right = TreeNode(3)
    skewed.right.right.right = TreeNode(4)
    skewed.right.right.right.right = TreeNode(5)

    balanced = fn4(skewed)
    check("right-skewed 5 nodes — inorder preserved",
          inorder_recursive(balanced), [1, 2, 3, 4, 5])
    check("right-skewed 5 nodes — now balanced",
          _is_balanced(balanced), True)
    check("right-skewed 5 nodes — valid BST",
          _is_bst(balanced), True)
    check("right-skewed 5 nodes — height reduced",
          _get_height(balanced) <= 2, True)

    # Already balanced tree
    already = from_list([4, 2, 6, 1, 3, 5, 7])
    balanced2 = fn4(already)
    check("already balanced — inorder preserved",
          inorder_recursive(balanced2), [1, 2, 3, 4, 5, 6, 7])
    check("already balanced — still balanced",
          _is_balanced(balanced2), True)

    single = fn4(TreeNode(99))
    check("single node",
          inorder_recursive(single), [99])

    # ── Exercise 5: Flatten BST ──
    print("\n── Exercise 5: Flatten BST to Right-Skewed List ──")
    fn5 = pick_tree_fn(flatten_bst, _sol_flatten_bst,
                       from_list([4, 2, 5, 1, 3]))

    flat = fn5(from_list([4, 2, 5, 1, 3]))
    check("5-node BST flattened",
          _collect_right_skewed(flat), [1, 2, 3, 4, 5])

    flat2 = fn5(from_list([4, 2, 6, 1, 3, 5, 7]))
    check("7-node BST flattened",
          _collect_right_skewed(flat2), [1, 2, 3, 4, 5, 6, 7])

    flat3 = fn5(from_list([1]))
    check("single node flattened",
          _collect_right_skewed(flat3), [1])

    flat4 = fn5(None)
    check("empty tree",
          flat4, None)

    flat5 = fn5(from_list([3, 2, None, 1]))
    check("left-skewed flattened",
          _collect_right_skewed(flat5), [1, 2, 3])

    # ── Exercise 6: Kth via BST Round-Trip ──
    print("\n── Exercise 6: Kth Smallest via BST Round-Trip ──")
    fn6 = pick_fn(kth_via_bst, _sol_kth_via_bst, [1, 2, 3, 4, 5], 1)

    check("k=1 (smallest)",
          fn6([1, 2, 3, 4, 5, 6, 7], 1), 1)
    check("k=4 (middle)",
          fn6([1, 2, 3, 4, 5, 6, 7], 4), 4)
    check("k=7 (largest)",
          fn6([1, 2, 3, 4, 5, 6, 7], 7), 7)
    check("k=0 (out of range)",
          fn6([1, 2, 3], 0), None)
    check("k=4 (out of range)",
          fn6([1, 2, 3], 4), None)
    check("empty array",
          fn6([], 1), None)
    check("single element k=1",
          fn6([10], 1), 10)

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
