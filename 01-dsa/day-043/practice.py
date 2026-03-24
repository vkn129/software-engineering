"""
Day 43 Practice: BST Operation Exercises
==========================================
Implement each function. Run this file to test your solutions.

Key mental model:
    BST search = binary search on a tree.
    At every node you make a LEFT/RIGHT decision based on the key comparison.
    This eliminates half the remaining tree at each step — O(h) per operation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list


# ─── Helper: Build BST from sorted list ─────────────────────────────
# Used by test runner to construct BSTs for testing.

def bst_insert(root, key):
    """Insert a key into a BST rooted at root. Returns the new root."""
    if root is None:
        return TreeNode(key)
    if key < root.val:
        root.left = bst_insert(root.left, key)
    elif key > root.val:
        root.right = bst_insert(root.right, key)
    return root


def build_bst(keys):
    """Build a BST by inserting keys in the given order."""
    root = None
    for k in keys:
        root = bst_insert(root, k)
    return root


def inorder(root):
    """Inorder traversal — returns sorted keys for a valid BST."""
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


# ─── Exercise 1: Validate BST ───────────────────────────────────────
#
# Given a binary tree, determine if it is a valid BST.
#
# A valid BST means for EVERY node:
#   - All keys in the left subtree are strictly LESS than the node's key
#   - All keys in the right subtree are strictly GREATER than the node's key
#
# Common mistake: only checking node.left.val < node.val < node.right.val
# is NOT enough. You must check against the entire subtree.
#
#       5
#      / \
#     1   6       ← NOT a valid BST!
#        / \        (4 is in the right subtree of 5, but 4 < 5)
#       4   7
#
# Hint: pass down valid (min, max) bounds as you recurse.

def is_valid_bst(root):
    # TODO: implement
    pass


# ─── Exercise 2: Lowest Common Ancestor in BST ──────────────────────
#
# Given a BST and two keys p and q (both guaranteed to exist),
# find the lowest common ancestor (LCA).
#
# In a BST, the LCA is the node where p and q SPLIT — one goes left,
# the other goes right (or one of them IS the node).
#
#          6
#        /   \
#       2     8
#      / \   / \
#     0   4 7   9
#        / \
#       3   5
#
# LCA(2, 8) = 6  (split point)
# LCA(2, 4) = 2  (2 is ancestor of 4)
# LCA(3, 5) = 4  (split point)
#
# This is O(h), not O(n) — the BST invariant tells you which way to go.

def lca_bst(root, p, q):
    # TODO: implement — return the VALUE of the LCA node
    pass


# ─── Exercise 3: Kth Smallest Element ───────────────────────────────
#
# Find the kth smallest element in a BST (1-indexed).
#
#       3
#      / \
#     1   4
#      \
#       2
#
# k=1 → 1, k=2 → 2, k=3 → 3, k=4 → 4
#
# Approach: inorder traversal visits nodes in sorted order.
# Stop early after visiting k nodes — no need to traverse the whole tree.
#
# Time: O(h + k) — drill to leftmost (O(h)), then visit k nodes.

def kth_smallest(root, k):
    # TODO: implement — return the value
    pass


# ─── Exercise 4: BST from Sorted Array ──────────────────────────────
#
# Given a sorted array, build a HEIGHT-BALANCED BST.
#
# A height-balanced BST has the minimum possible height: O(log n).
# The trick: always pick the MIDDLE element as root. This splits the
# array into two equal halves — guaranteeing balance.
#
# Input:  [-10, -3, 0, 5, 9]
# Output:      0
#             / \
#           -10   5
#             \    \
#             -3    9
#
# (or any valid balanced BST with those values)
#
# This is the inverse of "inorder traversal gives sorted array."

def sorted_array_to_bst(nums):
    # TODO: implement — return root TreeNode
    pass


# ─── Exercise 5: Two Sum in BST ─────────────────────────────────────
#
# Given a BST and a target sum, determine if there exist two nodes
# whose values add up to the target.
#
#       5
#      / \
#     3   6
#    / \   \
#   2   4   7
#
# target=9 → True (2+7, or 3+6)
# target=28 → False
#
# Approach: get sorted array via inorder, then use two-pointer technique
# (left pointer at start, right pointer at end).
#
# Time: O(n) for inorder + O(n) for two-pointer = O(n).

def two_sum_bst(root, target):
    # TODO: implement — return True/False
    pass


# ─── Exercise 6: Delete Node in BST ─────────────────────────────────
#
# Implement BST deletion (the three-case algorithm).
#
# Given a BST root and a key to delete, return the new root.
#
# Three cases:
#   1. Leaf node: remove it
#   2. One child: replace node with its child
#   3. Two children: replace value with inorder successor,
#      then delete the successor from the right subtree
#
# Input tree:     Delete 3:       Delete 5:
#       5              5               6
#      / \            / \             / \
#     3   6          4   6           4   7
#    / \   \          \   \         /
#   2   4   7          2   7       2
#                        (replaced with successor 4)

def delete_node(root, key):
    # TODO: implement — return the new root
    pass


# ─── Reference Solutions (don't peek until you've tried!) ───────────

def _sol_is_valid_bst(root):
    def _validate(node, lo, hi):
        if node is None:
            return True
        if node.val <= lo or node.val >= hi:
            return False
        return (_validate(node.left, lo, node.val) and
                _validate(node.right, node.val, hi))

    return _validate(root, float('-inf'), float('inf'))


def _sol_lca_bst(root, p, q):
    node = root
    while node:
        if p < node.val and q < node.val:
            node = node.left
        elif p > node.val and q > node.val:
            node = node.right
        else:
            return node.val
    return None


def _sol_kth_smallest(root, k):
    # Iterative inorder — stop after k nodes
    stack = []
    current = root
    count = 0

    while current or stack:
        while current:
            stack.append(current)
            current = current.left

        current = stack.pop()
        count += 1
        if count == k:
            return current.val

        current = current.right

    return None  # k is larger than tree size


def _sol_sorted_array_to_bst(nums):
    if not nums:
        return None

    def _build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(nums[mid])
        node.left = _build(lo, mid - 1)
        node.right = _build(mid + 1, hi)
        return node

    return _build(0, len(nums) - 1)


def _sol_two_sum_bst(root, target):
    # Inorder to get sorted array, then two-pointer
    vals = inorder(root)
    left, right = 0, len(vals) - 1

    while left < right:
        s = vals[left] + vals[right]
        if s == target:
            return True
        elif s < target:
            left += 1
        else:
            right -= 1

    return False


def _sol_delete_node(root, key):
    if root is None:
        return None

    if key < root.val:
        root.left = _sol_delete_node(root.left, key)
    elif key > root.val:
        root.right = _sol_delete_node(root.right, key)
    else:
        # Found the node to delete
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left

        # Two children: find inorder successor (min of right subtree)
        successor = root.right
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = _sol_delete_node(root.right, successor.val)

    return root


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

    # --- Exercise 1: Validate BST ---
    print("\n── Exercise 1: Validate BST ──")
    fn1 = is_valid_bst if is_valid_bst(build_bst([5, 3, 7])) is not None else _sol_is_valid_bst

    check("valid BST", fn1(build_bst([8, 3, 10, 1, 5, 14])), True)
    check("single node", fn1(TreeNode(1)), True)
    check("empty tree", fn1(None), True)

    # Manually construct an invalid BST:
    #       5
    #      / \
    #     1   6
    #        / \
    #       4   7     ← 4 < 5 but in right subtree of 5
    invalid = TreeNode(5)
    invalid.left = TreeNode(1)
    invalid.right = TreeNode(6)
    invalid.right.left = TreeNode(4)
    invalid.right.right = TreeNode(7)
    check("invalid BST (4 in wrong subtree)", fn1(invalid), False)

    # Another invalid: left child > root
    invalid2 = TreeNode(5)
    invalid2.left = TreeNode(6)
    check("invalid BST (left > root)", fn1(invalid2), False)

    # Equal values (not valid in strict BST)
    equal = TreeNode(2)
    equal.left = TreeNode(2)
    check("equal values (invalid strict BST)", fn1(equal), False)

    # --- Exercise 2: LCA in BST ---
    print("\n── Exercise 2: Lowest Common Ancestor in BST ──")
    lca_tree = build_bst([6, 2, 8, 0, 4, 7, 9, 3, 5])
    fn2 = lca_bst if lca_bst(lca_tree, 2, 8) is not None else _sol_lca_bst

    check("LCA(2,8)=6 (split at root)", fn2(lca_tree, 2, 8), 6)
    check("LCA(2,4)=2 (ancestor)", fn2(lca_tree, 2, 4), 2)
    check("LCA(3,5)=4 (split)", fn2(lca_tree, 3, 5), 4)
    check("LCA(0,5)=2 (split)", fn2(lca_tree, 0, 5), 2)
    check("LCA(7,9)=8 (split)", fn2(lca_tree, 7, 9), 8)
    check("LCA(0,9)=6 (root)", fn2(lca_tree, 0, 9), 6)

    # --- Exercise 3: Kth Smallest ---
    print("\n── Exercise 3: Kth Smallest Element ──")
    kth_tree = build_bst([5, 3, 7, 1, 4, 6, 8, 2])
    # Sorted: [1, 2, 3, 4, 5, 6, 7, 8]
    fn3 = kth_smallest if kth_smallest(kth_tree, 1) is not None else _sol_kth_smallest

    check("k=1 (min)", fn3(kth_tree, 1), 1)
    check("k=2", fn3(kth_tree, 2), 2)
    check("k=4", fn3(kth_tree, 4), 4)
    check("k=8 (max)", fn3(kth_tree, 8), 8)
    check("single node k=1", fn3(TreeNode(42), 1), 42)

    # --- Exercise 4: Sorted Array to BST ---
    print("\n── Exercise 4: BST from Sorted Array ──")
    fn4 = sorted_array_to_bst if sorted_array_to_bst([1]) is not None else _sol_sorted_array_to_bst

    # Verify the result is a valid BST with correct elements
    t4a = fn4([-10, -3, 0, 5, 9])
    check("sorted array → BST inorder", inorder(t4a), [-10, -3, 0, 5, 9])
    check("root is middle element", t4a.val, 0)

    t4b = fn4([1, 2, 3, 4, 5, 6, 7])
    check("7 elements inorder", inorder(t4b), [1, 2, 3, 4, 5, 6, 7])
    check("7 elements root", t4b.val, 4)

    t4c = fn4([1])
    check("single element", t4c.val, 1)

    t4d = fn4([])
    check("empty array", t4d, None)

    # Check that it's balanced (height <= ceil(log2(n)))
    def tree_height(node):
        if node is None:
            return -1
        return 1 + max(tree_height(node.left), tree_height(node.right))

    h = tree_height(t4b)
    check("7 elements balanced (height <= 2)", h <= 2, True)

    # --- Exercise 5: Two Sum in BST ---
    print("\n── Exercise 5: Two Sum in BST ──")
    sum_tree = build_bst([5, 3, 6, 2, 4, 7])
    fn5 = two_sum_bst if two_sum_bst(sum_tree, 9) is not None else _sol_two_sum_bst

    check("target=9 (2+7)", fn5(sum_tree, 9), True)
    check("target=11 (4+7)", fn5(sum_tree, 11), True)
    check("target=5 (2+3)", fn5(sum_tree, 5), True)
    check("target=28 (impossible)", fn5(sum_tree, 28), False)
    check("target=10 (3+7)", fn5(sum_tree, 10), True)
    check("single node", fn5(TreeNode(5), 10), False)

    # --- Exercise 6: Delete Node ---
    print("\n── Exercise 6: Delete Node in BST ──")
    # Test by building, deleting, checking inorder
    def test_delete(keys, insert_order, del_key, expected_inorder):
        root = build_bst(insert_order)
        fn6 = delete_node if delete_node(build_bst([1, 2]), 1) is not None else _sol_delete_node
        new_root = fn6(root, del_key)
        return inorder(new_root) == expected_inorder

    # Detect which function to use
    probe = build_bst([5, 3, 7])
    fn6 = delete_node if delete_node(probe, 3) is not None else _sol_delete_node

    # Delete leaf
    r = build_bst([5, 3, 7, 2, 4])
    r = fn6(r, 2)
    check("delete leaf (2)", inorder(r), [3, 4, 5, 7])

    # Delete node with one child
    r = build_bst([5, 3, 7, 2])
    r = fn6(r, 3)
    check("delete one-child (3→2)", inorder(r), [2, 5, 7])

    # Delete node with two children
    r = build_bst([5, 3, 7, 2, 4, 6, 8])
    r = fn6(r, 5)
    check("delete two-children (5)", inorder(r), [2, 3, 4, 6, 7, 8])

    # Delete root
    r = build_bst([5, 3, 7])
    r = fn6(r, 5)
    check("delete root (5)", inorder(r), [3, 7])

    # Delete nonexistent key
    r = build_bst([5, 3, 7])
    r = fn6(r, 99)
    check("delete nonexistent (no change)", inorder(r), [3, 5, 7])

    # Delete only node
    r = fn6(TreeNode(1), 1)
    check("delete only node", inorder(r), [])

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
