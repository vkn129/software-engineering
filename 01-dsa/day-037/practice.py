"""
Day 37 Practice: Tree Construction & Serialization Exercises
=============================================================
Implement each function. Run this file to test your solutions.

Key mental model:
    Reconstruction = figuring out which node is the root, then recursively
    determining what belongs to the left vs right subtree.
    The "trick" in each problem is HOW you identify the root and split.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import (TreeNode, from_list, to_list,
                         inorder_recursive, preorder_recursive, postorder_recursive)
from collections import deque


# ─── Exercise 1: Construct from Preorder and Inorder ────────────────
#
# Given preorder and inorder traversal arrays, reconstruct the binary tree.
#
# preorder = [3, 9, 20, 15, 7]
# inorder  = [9, 3, 15, 20, 7]
#
# Result:
#         3
#        / \
#       9  20
#         / \
#        15  7
#
# Hint: preorder[0] is the root. Find it in inorder to split left/right.
# Use a hash map for O(1) lookup in inorder.

def build_from_preorder_inorder(preorder, inorder):
    # TODO: implement
    pass


# ─── Exercise 2: Construct from Postorder and Inorder ───────────────
#
# Given postorder and inorder traversal arrays, reconstruct the binary tree.
#
# postorder = [9, 15, 7, 20, 3]
# inorder   = [9, 3, 15, 20, 7]
#
# Same result as Exercise 1.
#
# Hint: postorder[-1] is the root. Read postorder right-to-left,
# and build RIGHT subtree before left.

def build_from_postorder_inorder(postorder, inorder):
    # TODO: implement
    pass


# ─── Exercise 3: Serialize and Deserialize (Round-Trip) ─────────────
#
# Implement serialize() and deserialize() such that:
#     deserialize(serialize(root)) produces an identical tree
#
# Use preorder traversal with '#' as sentinel for None.
# Format: "1,2,#,#,3,4,#,#,5,#,#"
#
# Why preorder? Because the root comes first, so the deserializer
# can build top-down without needing to buffer anything.

def my_serialize(root):
    # TODO: implement — return a string
    pass


def my_deserialize(data):
    # TODO: implement — return a TreeNode (or None)
    pass


# ─── Exercise 4: Construct Maximum Binary Tree ──────────────────────
#
# Given an integer array with no duplicates, construct a "maximum binary tree":
#   1. The root is the maximum element in the array
#   2. The left subtree is the maximum tree of the subarray LEFT of the max
#   3. The right subtree is the maximum tree of the subarray RIGHT of the max
#
# nums = [3, 2, 1, 6, 0, 5]
#
# Result:
#            6
#          /   \
#         3     5
#          \   /
#           2 0
#            \
#             1
#
# Why this exists: this is a Cartesian tree — used in range-minimum-query
# data structures and treaps. The max element "dominates" its range,
# creating a natural hierarchical decomposition.
#
# Time: O(n²) worst case (sorted input), O(n log n) average.

def construct_max_tree(nums):
    # TODO: implement
    pass


# ─── Exercise 5: Construct Tree from String ─────────────────────────
#
# Parse a tree from a string representation:
#     "4(2(3)(1))(6(5))"
#
# Rules:
#   - A number is a node value (can be negative or multi-digit)
#   - Parentheses enclose children: first pair = left, second pair = right
#   - A node with no parentheses has no children
#
# Result:
#         4
#        / \
#       2   6
#      / \ /
#     3  1 5
#
# This is how expression trees appear in compiler debug output and
# how some serialization formats work (S-expressions in Lisp).
#
# Hint: Use a stack. When you see '(', push current node.
# When you see ')', pop. Track whether you're assigning left or right child.

def tree_from_string(s):
    # TODO: implement
    pass


# ─── Exercise 6: Verify Serialization of a Binary Tree ──────────────
#
# Given a preorder serialization string (with '#' for null), determine
# if it represents a VALID serialization WITHOUT actually building the tree.
#
# Valid:   "9,3,4,#,#,1,#,#,2,#,6,#,#"
# Invalid: "1,#"
# Invalid: "9,#,#,1"
#
# Key insight: In a valid binary tree with n nodes, there are exactly
# n+1 null pointers (external nodes). Use an "available slots" counter:
#   - Start with 1 slot (for the root)
#   - Each non-null node consumes 1 slot but creates 2 → net +1
#   - Each '#' consumes 1 slot and creates 0 → net -1
#   - At the end, slots should be exactly 0
#   - At NO point during traversal should slots go below 0

def is_valid_serialization(preorder_str):
    # TODO: implement — return True or False
    pass


# ─── Reference Solutions (don't peek until you've tried!) ───────────

def _sol_build_from_preorder_inorder(preorder, inorder):
    if not preorder or not inorder:
        return None

    inorder_index = {val: idx for idx, val in enumerate(inorder)}
    pre_idx = [0]

    def _build(in_left, in_right):
        if in_left > in_right:
            return None
        root_val = preorder[pre_idx[0]]
        pre_idx[0] += 1
        root = TreeNode(root_val)
        in_root = inorder_index[root_val]
        root.left = _build(in_left, in_root - 1)
        root.right = _build(in_root + 1, in_right)
        return root

    return _build(0, len(inorder) - 1)


def _sol_build_from_postorder_inorder(postorder, inorder):
    if not postorder or not inorder:
        return None

    inorder_index = {val: idx for idx, val in enumerate(inorder)}
    post_idx = [len(postorder) - 1]

    def _build(in_left, in_right):
        if in_left > in_right:
            return None
        root_val = postorder[post_idx[0]]
        post_idx[0] -= 1
        root = TreeNode(root_val)
        in_root = inorder_index[root_val]
        # Build right subtree FIRST (postorder reads right-to-left)
        root.right = _build(in_root + 1, in_right)
        root.left = _build(in_left, in_root - 1)
        return root

    return _build(0, len(inorder) - 1)


def _sol_my_serialize(root):
    tokens = []

    def _preorder(node):
        if node is None:
            tokens.append('#')
            return
        tokens.append(str(node.val))
        _preorder(node.left)
        _preorder(node.right)

    _preorder(root)
    return ','.join(tokens)


def _sol_my_deserialize(data):
    if not data:
        return None

    tokens = iter(data.split(','))

    def _build():
        val = next(tokens)
        if val == '#':
            return None
        node = TreeNode(int(val))
        node.left = _build()
        node.right = _build()
        return node

    return _build()


def _sol_construct_max_tree(nums):
    if not nums:
        return None

    max_idx = 0
    for i in range(len(nums)):
        if nums[i] > nums[max_idx]:
            max_idx = i

    root = TreeNode(nums[max_idx])
    root.left = _sol_construct_max_tree(nums[:max_idx])
    root.right = _sol_construct_max_tree(nums[max_idx + 1:])
    return root


def _sol_tree_from_string(s):
    if not s:
        return None

    # Find end of the number (root value)
    i = 0
    # Handle negative numbers
    if s[i] == '-':
        i += 1
    while i < len(s) and s[i].isdigit():
        i += 1

    root = TreeNode(int(s[:i]))

    if i >= len(s):
        return root

    # Find matching parenthesis for left child
    if s[i] == '(':
        # Count parentheses to find the matching close
        depth = 0
        start = i
        while i < len(s):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
            if depth == 0:
                break
            i += 1
        root.left = _sol_tree_from_string(s[start + 1:i])
        i += 1  # skip closing ')'

    # Right child
    if i < len(s) and s[i] == '(':
        depth = 0
        start = i
        while i < len(s):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
            if depth == 0:
                break
            i += 1
        root.right = _sol_tree_from_string(s[start + 1:i])

    return root


def _sol_is_valid_serialization(preorder_str):
    if not preorder_str:
        return False

    tokens = preorder_str.split(',')
    # Available slots: start with 1 (room for the root)
    slots = 1

    for token in tokens:
        # Every token (node or '#') consumes one slot
        slots -= 1
        if slots < 0:
            return False  # more nodes than available positions

        if token != '#':
            # A real node creates 2 new slots (left + right children)
            slots += 2

    # All slots must be filled exactly
    return slots == 0


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

    # --- Exercise 1: Build from Preorder + Inorder ---
    print("\n── Exercise 1: Build from Preorder + Inorder ──")
    pre1 = [3, 9, 20, 15, 7]
    ino1 = [9, 3, 15, 20, 7]
    fn1 = build_from_preorder_inorder
    result1 = fn1(pre1, ino1)
    if result1 is None:
        fn1 = _sol_build_from_preorder_inorder
        result1 = fn1(pre1, ino1)
    check("basic tree", to_list(result1), [3, 9, 20, None, None, 15, 7])
    check("single node", to_list(fn1([1], [1])), [1])
    check("left skewed", to_list(fn1([3, 2, 1], [1, 2, 3])), [3, 2, None, 1])
    check("right skewed", to_list(fn1([1, 2, 3], [1, 2, 3])), [1, None, 2, None, 3])
    check("empty", fn1([], []), None)

    # --- Exercise 2: Build from Postorder + Inorder ---
    print("\n── Exercise 2: Build from Postorder + Inorder ──")
    post2 = [9, 15, 7, 20, 3]
    ino2 = [9, 3, 15, 20, 7]
    fn2 = build_from_postorder_inorder
    result2 = fn2(post2, ino2)
    if result2 is None:
        fn2 = _sol_build_from_postorder_inorder
        result2 = fn2(post2, ino2)
    check("basic tree", to_list(result2), [3, 9, 20, None, None, 15, 7])
    check("single node", to_list(fn2([1], [1])), [1])
    check("left skewed", to_list(fn2([1, 2, 3], [1, 2, 3])), [3, 2, None, 1])
    check("empty", fn2([], []), None)

    # --- Exercise 3: Serialize/Deserialize Round-Trip ---
    print("\n── Exercise 3: Serialize/Deserialize Round-Trip ──")
    ser_fn = my_serialize
    deser_fn = my_deserialize
    # Test if user implemented: serialize should return a non-None string
    test_tree = from_list([1, 2, 3])
    user_ser = ser_fn(test_tree)
    if user_ser is None:
        ser_fn = _sol_my_serialize
        deser_fn = _sol_my_deserialize

    tree3a = from_list([1, 2, 3, None, None, 4, 5])
    serialized3a = ser_fn(tree3a)
    restored3a = deser_fn(serialized3a)
    check("round-trip basic", to_list(restored3a), to_list(tree3a))

    check("round-trip empty", deser_fn(ser_fn(None)), None)

    tree3b = from_list([1])
    check("round-trip single", to_list(deser_fn(ser_fn(tree3b))), [1])

    tree3c = from_list([1, 2, None, 3, None, 4])
    check("round-trip left-skewed", to_list(deser_fn(ser_fn(tree3c))), to_list(tree3c))

    tree3d = from_list([-1, -2, -3])
    check("round-trip negative vals", to_list(deser_fn(ser_fn(tree3d))), [-1, -2, -3])

    # --- Exercise 4: Maximum Binary Tree ---
    print("\n── Exercise 4: Maximum Binary Tree ──")
    fn4 = construct_max_tree
    result4 = fn4([3, 2, 1, 6, 0, 5])
    if result4 is None:
        fn4 = _sol_construct_max_tree

    tree4a = fn4([3, 2, 1, 6, 0, 5])
    check("basic", to_list(tree4a), [6, 3, 5, None, 2, 0, None, None, 1])
    check("single", to_list(fn4([5])), [5])
    check("sorted ascending", to_list(fn4([1, 2, 3])), [3, 2, None, 1])
    check("sorted descending", to_list(fn4([3, 2, 1])), [3, None, 2, None, 1])
    check("empty", fn4([]), None)

    # --- Exercise 5: Tree from String ---
    print("\n── Exercise 5: Tree from String ──")
    fn5 = tree_from_string
    result5 = fn5("4(2(3)(1))(6(5))")
    if result5 is None:
        fn5 = _sol_tree_from_string

    check("basic", to_list(fn5("4(2(3)(1))(6(5))")), [4, 2, 6, 3, 1, 5])
    check("single node", to_list(fn5("1")), [1])
    check("left child only", to_list(fn5("1(2)")), [1, 2])
    check("nested", to_list(fn5("1(2(3))")), [1, 2, None, 3])
    check("negative value", to_list(fn5("-1(2)(3)")), [-1, 2, 3])
    check("empty string", fn5(""), None)

    # --- Exercise 6: Verify Serialization ---
    print("\n── Exercise 6: Verify Serialization ──")
    fn6 = is_valid_serialization
    result6 = fn6("9,3,4,#,#,1,#,#,2,#,6,#,#")
    if result6 is None:
        fn6 = _sol_is_valid_serialization

    check("valid full tree", fn6("9,3,4,#,#,1,#,#,2,#,6,#,#"), True)
    check("valid single node", fn6("#"), True)
    check("valid simple", fn6("1,#,#"), True)
    check("invalid incomplete", fn6("1,#"), False)
    check("invalid extra nodes", fn6("9,#,#,1"), False)
    check("invalid empty", fn6(""), False)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All exercises complete!")
    else:
        print(f"{failed} exercises need work — implement the TODO functions above")


if __name__ == "__main__":
    run_tests()
