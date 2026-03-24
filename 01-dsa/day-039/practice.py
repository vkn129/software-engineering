"""
Day 39 Practice: Tree Diameter, Depth, Balance + Path Sum Exercises
====================================================================
Implement each function. Run this file to test your solutions.

Core pattern for ALL exercises:
    1. Base case: node is None -> return identity
    2. Recurse left and right
    3. Combine: update global answer + return value for parent

What you RETURN to parent != what you TRACK as the answer.
"""

import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list


# ─── Exercise 1: Tree Diameter ───────────────────────────────────────
#
# Return the diameter of a binary tree (longest path between any two
# nodes, measured in number of EDGES).
#
# The diameter may NOT pass through the root!
#
#         1
#        / \
#       2   3        Diameter = 3 (path: 4→2→5 or 4→2→1→3)
#      / \
#     4   5
#
# Approach: bottom-up. At each node, compute depth of left and right
# subtrees. The path through this node = left_depth + right_depth.
# Track the maximum across all nodes.
#
# Time: O(n), Space: O(h)

def tree_diameter(root):
    # TODO: implement
    pass


# ─── Exercise 2: Check Balanced (O(n) solution) ─────────────────────
#
# Return True if the tree is height-balanced: for EVERY node,
# |height(left) - height(right)| <= 1.
#
# REQUIREMENT: solve in O(n), not O(n²).
# Hint: compute height bottom-up. Return -1 as sentinel for "unbalanced".
#
# Balanced:          Unbalanced:
#       1                 1
#      / \               /
#     2   3             2
#    /                 /
#   4                 3

def check_balanced(root):
    # TODO: implement
    pass


# ─── Exercise 3: Path Sum (Root to Leaf) ─────────────────────────────
#
# Return True if any root-to-leaf path sums to target.
# A leaf is a node with no children.
#
#         5
#        / \
#       4   8
#      /   / \
#     11  13  4
#    / \       \
#   7   2       1
#
# target=22: True (5→4→11→2)
#
# Hint: subtract current node's value from target as you descend.
# At a leaf, check if remainder == 0.

def path_sum(root, target):
    # TODO: implement
    pass


# ─── Exercise 4: Count Paths with Target Sum (Any Node) ─────────────
#
# Count paths that sum to target_sum, where a path can start at ANY node
# and end at ANY descendant (must go downward).
#
#       10
#      /  \
#     5   -3
#    / \    \
#   3   2   11
#  / \   \
# 3  -2   1
#
# target=8: 3 paths (5→3, 5→2→1, -3→11)
#
# This is the tree analog of "subarray sum equals k" (prefix sums).
# Maintain running sum from root. At each node, check if
# (current_sum - target) exists in prefix map.
# CRITICAL: backtrack the prefix map after recursing.

def count_paths_with_sum(root, target_sum):
    # TODO: implement
    pass


# ─── Exercise 5: Longest Univalue Path ──────────────────────────────
#
# Find the length (in edges) of the longest path where every node has
# the same value. The path doesn't need to pass through the root.
#
#         5
#        / \
#       4   5
#      / \   \
#     1   1   5
#
# Answer: 2 (path: 5→5→5 on the right side)
#
# Approach: bottom-up. At each node, compute the longest univalue
# extension through left child and through right child.
# If child has same value, extend = child_extension + 1, else 0.
# Track max(left_ext + right_ext) globally.

def longest_univalue_path(root):
    # TODO: implement
    pass


# ─── Exercise 6: Sum of Left Leaves ─────────────────────────────────
#
# Return the sum of all LEFT LEAF values in the tree.
# A left leaf is a leaf node that is the LEFT child of its parent.
#
#         3
#        / \
#       9  20
#         / \
#        15  7
#
# Left leaves: 9 and 15. Sum = 24.
#
# Hint: pass a flag or check from the parent whether the child is left.

def sum_of_left_leaves(root):
    # TODO: implement
    pass


# ─── Reference Solutions ─────────────────────────────────────────────

def _sol_tree_diameter(root):
    max_diam = [0]

    def depth(node):
        if node is None:
            return 0
        left_d = depth(node.left)
        right_d = depth(node.right)
        # Path through this node = left_depth + right_depth
        max_diam[0] = max(max_diam[0], left_d + right_d)
        # Return depth of this subtree for parent
        return 1 + max(left_d, right_d)

    depth(root)
    return max_diam[0]


def _sol_check_balanced(root):
    def check_height(node):
        if node is None:
            return 0
        left_h = check_height(node.left)
        if left_h == -1:
            return -1
        right_h = check_height(node.right)
        if right_h == -1:
            return -1
        if abs(left_h - right_h) > 1:
            return -1
        return 1 + max(left_h, right_h)

    return check_height(root) != -1


def _sol_path_sum(root, target):
    if root is None:
        return False
    remainder = target - root.val
    if root.left is None and root.right is None:
        return remainder == 0
    return (_sol_path_sum(root.left, remainder) or
            _sol_path_sum(root.right, remainder))


def _sol_count_paths_with_sum(root, target_sum):
    count = [0]
    prefix_map = defaultdict(int)
    prefix_map[0] = 1

    def dfs(node, current_sum):
        if node is None:
            return
        current_sum += node.val
        count[0] += prefix_map[current_sum - target_sum]
        prefix_map[current_sum] += 1
        dfs(node.left, current_sum)
        dfs(node.right, current_sum)
        prefix_map[current_sum] -= 1  # backtrack

    dfs(root, 0)
    return count[0]


def _sol_longest_univalue_path(root):
    longest = [0]

    def extend(node):
        """Returns length of longest univalue extension downward from node."""
        if node is None:
            return 0

        left_ext = extend(node.left)
        right_ext = extend(node.right)

        # Can we extend through left child?
        left_arm = 0
        if node.left and node.left.val == node.val:
            left_arm = left_ext + 1

        # Can we extend through right child?
        right_arm = 0
        if node.right and node.right.val == node.val:
            right_arm = right_ext + 1

        # Path through this node = left_arm + right_arm
        longest[0] = max(longest[0], left_arm + right_arm)

        # Return best single-direction extension for parent
        return max(left_arm, right_arm)

    extend(root)
    return longest[0]


def _sol_sum_of_left_leaves(root):
    def helper(node, is_left):
        if node is None:
            return 0
        # If this is a left leaf, return its value
        if is_left and node.left is None and node.right is None:
            return node.val
        return helper(node.left, True) + helper(node.right, False)

    return helper(root, False)


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

    # Helper: pick user fn if it returns non-None, else use solution
    def pick(user_fn, sol_fn, *args):
        result = user_fn(*args)
        if result is not None:
            return user_fn
        return sol_fn

    # --- Exercise 1: Tree Diameter ---
    print("\n── Exercise 1: Tree Diameter ──")
    fn1 = pick(tree_diameter, _sol_tree_diameter, from_list([1, 2, 3, 4, 5]))
    check("basic (diam=3)", fn1(from_list([1, 2, 3, 4, 5])), 3)
    check("single node", fn1(from_list([1])), 0)
    check("empty", fn1(None), 0)
    check("left skewed", fn1(from_list([1, 2, None, 3, None, 4])), 3)
    # Diameter not through root
    #       1
    #      /
    #     2
    #    / \
    #   3   4
    #  /     \
    # 5       6
    t_diam = from_list([1, 2, None, 3, 4, 5, None, None, None, None, 6])
    check("not through root (diam=4)", fn1(t_diam), 4)

    # --- Exercise 2: Check Balanced ---
    print("\n── Exercise 2: Check Balanced ──")
    fn2 = pick(check_balanced, _sol_check_balanced, from_list([1, 2, 3]))
    check("balanced [1,2,3]", fn2(from_list([1, 2, 3])), True)
    check("balanced [1,2,3,4,5]", fn2(from_list([1, 2, 3, 4, 5])), True)
    check("single node", fn2(from_list([1])), True)
    check("empty", fn2(None), True)
    # Unbalanced: 1→2→3→4 (left chain)
    check("unbalanced chain", fn2(from_list([1, 2, None, 3])), False)
    # Subtree unbalanced but root looks OK
    #        1
    #       / \
    #      2   3
    #     /
    #    4
    #   /
    #  5
    check("deep unbalance", fn2(from_list([1, 2, 3, 4, None, None, None, 5])), False)

    # --- Exercise 3: Path Sum ---
    print("\n── Exercise 3: Path Sum (Root to Leaf) ──")
    t3 = from_list([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
    fn3 = pick(path_sum, _sol_path_sum, t3, 22)
    check("5→4→11→2=22", fn3(t3, 22), True)
    check("5→8→13=26", fn3(t3, 26), True)
    check("no path=99", fn3(t3, 99), False)
    check("empty tree", fn3(None, 0), False)
    check("single match", fn3(from_list([1]), 1), True)
    check("single no match", fn3(from_list([1]), 2), False)
    # Edge case: target matches root but root is not a leaf
    check("root val but not leaf", fn3(from_list([1, 2]), 1), False)

    # --- Exercise 4: Count Paths with Target Sum ---
    print("\n── Exercise 4: Count Paths with Target Sum ──")
    t4 = from_list([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1])
    fn4 = pick(count_paths_with_sum, _sol_count_paths_with_sum, t4, 8)
    check("target=8, 3 paths", fn4(t4, 8), 3)
    check("single node match", fn4(from_list([5]), 5), 1)
    check("single node no match", fn4(from_list([5]), 3), 0)
    check("empty", fn4(None, 1), 0)
    # Path with negatives: paths summing to 1: [1] at root, [1,-1,1] full path, [1] at leaf = 3
    t4b = from_list([1, -1, None, 1])
    check("with negatives target=1", fn4(t4b, 1), 3)
    # All zeros, target=0
    t4c = from_list([0, 0, 0])
    check("all zeros target=0", fn4(t4c, 0), 5)  # [], [0], [0], [0,0], [0,0] → actually 5

    # --- Exercise 5: Longest Univalue Path ---
    print("\n── Exercise 5: Longest Univalue Path ──")
    fn5 = pick(longest_univalue_path, _sol_longest_univalue_path, from_list([5, 4, 5, 1, 1, None, 5]))
    check("5→5→5 = 2 edges", fn5(from_list([5, 4, 5, 1, 1, None, 5])), 2)
    check("all same [1,1,1,1,1]", fn5(from_list([1, 1, 1, 1, 1])), 3)
    check("no match [1,2,3]", fn5(from_list([1, 2, 3])), 0)
    check("single node", fn5(from_list([1])), 0)
    check("empty", fn5(None), 0)
    # Left chain of same values
    check("left chain [4,4,4]", fn5(from_list([4, 4, None, 4])), 2)

    # --- Exercise 6: Sum of Left Leaves ---
    print("\n── Exercise 6: Sum of Left Leaves ──")
    fn6 = pick(sum_of_left_leaves, _sol_sum_of_left_leaves, from_list([3, 9, 20, None, None, 15, 7]))
    check("9+15=24", fn6(from_list([3, 9, 20, None, None, 15, 7])), 24)
    check("single node (no left leaves)", fn6(from_list([1])), 0)
    check("empty", fn6(None), 0)
    #     1
    #    / \
    #   2   3
    #  /
    # 4       → left leaves: 4. Sum = 4
    check("left leaf only", fn6(from_list([1, 2, 3, 4])), 4)
    # Right-only tree: no left leaves
    check("right-only [1,None,2,None,3]", fn6(from_list([1, None, 2, None, 3])), 0)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All exercises complete!")
    else:
        print(f"{failed} exercise(s) need work — implement the TODO functions above")


if __name__ == "__main__":
    run_tests()
