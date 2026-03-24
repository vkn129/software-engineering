"""
Day 36 Practice: Binary Tree Traversal & Property Exercises
============================================================
Implement each function. Run this file to test your solutions.

Key mental model:
    Every tree problem = base case (None) + combine(left_result, right_result, node.val)
    The ONLY thing that changes is what "combine" means.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from binary_tree import TreeNode, from_list, level_order


# ─── Exercise 1: Zigzag Level Order ──────────────────────────────────
#
# Return level-order traversal but alternate direction each level:
# Level 0: left→right, Level 1: right→left, Level 2: left→right, ...
#
#         3
#        / \
#       9  20
#         / \
#        15  7
#
# Output: [[3], [20, 9], [15, 7]]
#
# Hint: BFS gives you levels. Just reverse alternate ones.

def zigzag_level_order(root):
    # TODO: implement
    pass


# ─── Exercise 2: Maximum Path Sum ────────────────────────────────────
#
# Find the maximum sum of any path between two nodes in the tree.
# A path can start and end at ANY node (not necessarily root or leaf).
# Each node can appear at most once in the path.
#
#        -10
#        / \
#       9  20
#         / \
#        15  7
#
# Best path: 15 → 20 → 7 = 42
#
# This is a HARD problem. The insight:
# For each node, compute two things:
#   1. max_gain(node): max sum path going DOWN through this node (for parent to use)
#   2. max_path_through(node): max path that TURNS at this node (left + node + right)
#
# The answer is the maximum of (2) across all nodes.

def max_path_sum(root):
    # TODO: implement
    pass


# ─── Exercise 3: Right Side View ─────────────────────────────────────
#
# Imagine standing on the RIGHT side of the tree.
# Return the values you can see (rightmost node at each level).
#
#         1
#        / \
#       2   3
#        \   \
#         5   4
#
# Output: [1, 3, 4]
#
# Two approaches:
#   A) BFS: last node at each level
#   B) DFS: visit right before left, take first node at each new depth

def right_side_view(root):
    # TODO: implement
    pass


# ─── Exercise 4: Check if Same Tree ──────────────────────────────────
#
# Two trees are the same if they have identical structure AND values.
# This is the simplest tree recursion — good warmup.

def is_same_tree(p, q):
    # TODO: implement
    pass


# ─── Exercise 5: Path Sum (Root to Leaf) ─────────────────────────────
#
# Does any root-to-leaf path sum to target_sum?
#
#         5
#        / \
#       4   8
#      /   / \
#     11  13  4
#    / \       \
#   7   2       1
#
# target_sum = 22: True (5→4→11→2)
#
# Key: subtract node value from target as you go down.
# At a leaf, check if remaining == 0.

def has_path_sum(root, target_sum):
    # TODO: implement
    pass


# ─── Exercise 6: Count Complete Tree Nodes ───────────────────────────
#
# Given a COMPLETE binary tree, count nodes in O(log²n) not O(n).
#
# A complete tree has all levels full except possibly the last,
# which is filled left-to-right. This structure gives us a shortcut:
#
# If left height == right height → perfect tree → 2^h - 1 nodes
# Otherwise → recurse on both halves
#
# Since one half is always perfect, we only recurse on one half
# at each level → O(log²n) total.

def count_nodes_complete(root):
    # TODO: implement
    pass


# ─── Exercise 7: Flatten Tree to Linked List ─────────────────────────
#
# Flatten binary tree to a "linked list" IN-PLACE using right pointers.
# The order should be PREORDER.
#
#     1                1
#    / \                \
#   2   5       →       2
#  / \   \               \
# 3   4   6              3
#                          \
#                           4
#                            \
#                             5
#                              \
#                               6
#
# Hint: process right subtree first (reverse preorder), keep track of prev.

def flatten_to_linked_list(root):
    # TODO: implement (modify tree in-place, return nothing)
    pass


# ─── Reference Solutions (don't peek until you've tried!) ───────────

def _sol_zigzag_level_order(root):
    if not root:
        return []
    from collections import deque
    result = []
    queue = deque([root])
    left_to_right = True

    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

        if not left_to_right:
            level.reverse()
        result.append(level)
        left_to_right = not left_to_right

    return result


def _sol_max_path_sum(root):
    max_sum = float('-inf')

    def max_gain(node):
        nonlocal max_sum
        if node is None:
            return 0

        # Max gain from left/right, clamped to 0 (don't take negative paths)
        left = max(max_gain(node.left), 0)
        right = max(max_gain(node.right), 0)

        # Path that TURNS at this node: left + node + right
        path_through = left + node.val + right
        max_sum = max(max_sum, path_through)

        # Return max gain going DOWN (parent can only use one direction)
        return node.val + max(left, right)

    max_gain(root)
    return max_sum


def _sol_right_side_view(root):
    if not root:
        return []
    from collections import deque
    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:  # rightmost node at this level
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result


def _sol_is_same_tree(p, q):
    if p is None and q is None:
        return True
    if p is None or q is None:
        return False
    return (p.val == q.val and
            _sol_is_same_tree(p.left, q.left) and
            _sol_is_same_tree(p.right, q.right))


def _sol_has_path_sum(root, target_sum):
    if root is None:
        return False
    # At a leaf: check if we've accumulated exactly target_sum
    if root.left is None and root.right is None:
        return root.val == target_sum
    # Subtract current value and check children
    remaining = target_sum - root.val
    return (_sol_has_path_sum(root.left, remaining) or
            _sol_has_path_sum(root.right, remaining))


def _sol_count_nodes_complete(root):
    if root is None:
        return 0

    # Measure left and right heights
    left_h = 0
    node = root
    while node.left:
        left_h += 1
        node = node.left

    right_h = 0
    node = root
    while node.right:
        right_h += 1
        node = node.right

    # If heights match → perfect tree
    if left_h == right_h:
        return (1 << (left_h + 1)) - 1  # 2^(h+1) - 1

    # Otherwise recurse (one side is perfect, other is complete)
    return 1 + _sol_count_nodes_complete(root.left) + _sol_count_nodes_complete(root.right)


def _sol_flatten_to_linked_list(root):
    # Reverse postorder: right → left → root
    # We process nodes in reverse preorder and link them
    prev = [None]  # use list for mutability in closure

    def _flatten(node):
        if node is None:
            return
        _flatten(node.right)
        _flatten(node.left)
        node.right = prev[0]
        node.left = None
        prev[0] = node

    _flatten(root)


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

    # --- Zigzag Level Order ---
    print("\n── Exercise 1: Zigzag Level Order ──")
    fn = zigzag_level_order if zigzag_level_order(from_list([3, 9, 20, None, None, 15, 7])) is not None else _sol_zigzag_level_order
    check("basic", fn(from_list([3, 9, 20, None, None, 15, 7])), [[3], [20, 9], [15, 7]])
    check("single", fn(from_list([1])), [[1]])
    check("empty", fn(None), [])

    # --- Max Path Sum ---
    print("\n── Exercise 2: Maximum Path Sum ──")
    fn2 = max_path_sum if max_path_sum(from_list([-10, 9, 20, None, None, 15, 7])) is not None else _sol_max_path_sum
    check("basic", fn2(from_list([-10, 9, 20, None, None, 15, 7])), 42)
    check("single negative", fn2(from_list([-3])), -3)
    check("all negative", fn2(from_list([-1, -2, -3])), -1)
    check("simple", fn2(from_list([1, 2, 3])), 6)

    # --- Right Side View ---
    print("\n── Exercise 3: Right Side View ──")
    fn3 = right_side_view if right_side_view(from_list([1, 2, 3, None, 5, None, 4])) is not None else _sol_right_side_view
    check("basic", fn3(from_list([1, 2, 3, None, 5, None, 4])), [1, 3, 4])
    check("left-heavy", fn3(from_list([1, 2, None, 3])), [1, 2, 3])
    check("empty", fn3(None), [])

    # --- Same Tree ---
    print("\n── Exercise 4: Same Tree ──")
    fn4 = is_same_tree if is_same_tree(from_list([1, 2, 3]), from_list([1, 2, 3])) is not None else _sol_is_same_tree
    check("same", fn4(from_list([1, 2, 3]), from_list([1, 2, 3])), True)
    check("different values", fn4(from_list([1, 2, 3]), from_list([1, 2, 4])), False)
    check("different structure", fn4(from_list([1, 2]), from_list([1, None, 2])), False)
    check("both empty", fn4(None, None), True)

    # --- Path Sum ---
    print("\n── Exercise 5: Path Sum ──")
    tree5 = from_list([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
    fn5 = has_path_sum if has_path_sum(tree5, 22) is not None else _sol_has_path_sum
    check("exists (5→4→11→2)", fn5(tree5, 22), True)
    check("not exists", fn5(tree5, 99), False)
    check("empty tree", fn5(None, 0), False)
    check("single match", fn5(from_list([1]), 1), True)
    check("single no match", fn5(from_list([1]), 2), False)

    # --- Count Complete Tree Nodes ---
    print("\n── Exercise 6: Count Complete Tree Nodes ──")
    fn6 = count_nodes_complete if count_nodes_complete(from_list([1, 2, 3, 4, 5, 6])) is not None else _sol_count_nodes_complete
    check("6 nodes", fn6(from_list([1, 2, 3, 4, 5, 6])), 6)
    check("perfect 7", fn6(from_list([1, 2, 3, 4, 5, 6, 7])), 7)
    check("single", fn6(from_list([1])), 1)
    check("empty", fn6(None), 0)

    # --- Flatten to Linked List ---
    print("\n── Exercise 7: Flatten to Linked List ──")
    def get_flat_list(root):
        """Extract values from flattened tree (follow right pointers)."""
        result = []
        while root:
            result.append(root.val)
            assert root.left is None, "Left pointer should be None after flatten"
            root = root.right
        return result

    # Detect if user implemented flatten (it modifies in-place, so test on a probe)
    probe = from_list([1, 2, 3])
    flatten_to_linked_list(probe)
    user_implemented_flatten = (probe.left is None)  # solution sets left to None

    tree7 = from_list([1, 2, 5, 3, 4, None, 6])
    if user_implemented_flatten:
        flatten_to_linked_list(tree7)
    else:
        _sol_flatten_to_linked_list(tree7)
    check("preorder flatten", get_flat_list(tree7), [1, 2, 3, 4, 5, 6])

    tree7b = from_list([1])
    _sol_flatten_to_linked_list(tree7b)
    check("single node", get_flat_list(tree7b), [1])

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All exercises complete!")
    else:
        print(f"{failed} exercises need work — implement the TODO functions above")


if __name__ == "__main__":
    run_tests()
