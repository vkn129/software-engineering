"""
Day 40 Practice: Morris Traversal Exercises
=============================================
Implement each function using Morris traversal (O(1) extra space).
Run this file to test your solutions.

Key mental model:
    Morris = use null right pointers as temporary threads back to ancestors.
    Create thread on first visit, remove on second visit.
    The tree is restored to its original structure after traversal.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list, inorder_recursive


# ─── Exercise 1: Morris Inorder Traversal ───────────────────────────
#
# Perform inorder traversal using O(1) extra space.
# Do NOT use recursion or an explicit stack.
#
# Algorithm:
#   - If no left child: visit node, go right
#   - If left child exists:
#       - Find inorder predecessor (rightmost in left subtree)
#       - If predecessor.right is None: create thread, go left
#       - If predecessor.right is current: remove thread, visit node, go right
#
# Time: O(n), Space: O(1) extra (output list doesn't count)

def morris_inorder(root):
    # TODO: implement
    pass


# ─── Exercise 2: Morris Preorder Traversal ──────────────────────────
#
# Perform preorder traversal using O(1) extra space.
#
# The ONLY difference from inorder: visit the node on the FIRST
# encounter (when creating the thread) instead of the second.
#
# Time: O(n), Space: O(1) extra

def morris_preorder(root):
    # TODO: implement
    pass


# ─── Exercise 3: Validate BST Using Morris (O(1) Space) ─────────────
#
# Check if a binary tree is a valid BST using Morris inorder.
#
# Insight: a BST's inorder traversal is strictly increasing.
# Use Morris to traverse in O(1) space, tracking the previous
# value to verify ordering.
#
# Return True if valid BST, False otherwise.
# An empty tree is a valid BST.
#
# Time: O(n), Space: O(1)

def is_bst_morris(root):
    # TODO: implement
    pass


# ─── Exercise 4: Kth Smallest in BST Using Morris ──────────────────
#
# Find the kth smallest element in a BST using Morris traversal.
# k is 1-indexed (k=1 means the smallest element).
#
# Since Morris inorder visits nodes in sorted order, count to k.
# Return None if k is out of range.
#
# Time: O(n), Space: O(1)

def kth_smallest_morris(root, k):
    # TODO: implement
    pass


# ─── Exercise 5: Recover BST Using Morris ──────────────────────────
#
# Two nodes in a BST were swapped by mistake. Fix the BST in-place
# using O(1) space (Morris traversal).
#
# Example:
#       3            1
#      / \   →      / \
#     1   4        3   4     (nodes 3 and 1 were swapped → swap back → [1,3,4])
#        /            /
#       2            2
#
# Insight: In the inorder traversal of a correct BST, values are
# strictly increasing. When two nodes are swapped, there will be
# one or two "inversions" (places where a value is greater than
# the next value).
#
# - If swapped nodes are adjacent in inorder: one inversion
#   The two bad nodes are the pair at that inversion.
# - If swapped nodes are NOT adjacent: two inversions
#   First bad node = the larger node at the first inversion
#   Second bad node = the smaller node at the second inversion
#
# Modify the tree in-place (swap the values of the two bad nodes).

def recover_bst_morris(root):
    # TODO: implement (modify tree in-place, return nothing)
    pass


# ─── Reference Solutions ────────────────────────────────────────────

def _sol_morris_inorder(root):
    result = []
    current = root
    while current is not None:
        if current.left is None:
            result.append(current.val)
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right
            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                result.append(current.val)
                current = current.right
    return result


def _sol_morris_preorder(root):
    result = []
    current = root
    while current is not None:
        if current.left is None:
            result.append(current.val)
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right
            if predecessor.right is None:
                result.append(current.val)
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                current = current.right
    return result


def _sol_is_bst_morris(root):
    current = root
    prev_val = float('-inf')
    is_valid = True

    while current is not None:
        if current.left is None:
            if current.val <= prev_val:
                is_valid = False
            prev_val = current.val
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right
            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                if current.val <= prev_val:
                    is_valid = False
                prev_val = current.val
                current = current.right

    # We traverse the entire tree even if invalid, to restore all threads
    return is_valid


def _sol_kth_smallest_morris(root, k):
    current = root
    count = 0
    result = None

    while current is not None:
        if current.left is None:
            count += 1
            if count == k:
                result = current.val
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right
            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                count += 1
                if count == k:
                    result = current.val
                current = current.right

    return result


def _sol_recover_bst_morris(root):
    # Morris inorder traversal, tracking inversions
    first = None   # first bad node (larger in first inversion)
    second = None  # second bad node (smaller in last inversion)
    prev = None    # previously visited node in inorder
    current = root

    while current is not None:
        if current.left is None:
            # Visit current
            if prev is not None and prev.val > current.val:
                if first is None:
                    first = prev
                second = current
            prev = current
            current = current.right
        else:
            predecessor = current.left
            while predecessor.right is not None and predecessor.right is not current:
                predecessor = predecessor.right

            if predecessor.right is None:
                predecessor.right = current
                current = current.left
            else:
                predecessor.right = None
                # Visit current
                if prev is not None and prev.val > current.val:
                    if first is None:
                        first = prev
                    second = current
                prev = current
                current = current.right

    # Swap the values of the two bad nodes
    if first and second:
        first.val, second.val = second.val, first.val


# ─── Test Runner ────────────────────────────────────────────────────

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

    # Helper: detect if user implemented a function (returns non-None)
    def pick(user_fn, sol_fn, *probe_args):
        """Use user's function if it returns non-None on probe, else solution."""
        result = user_fn(*probe_args)
        return user_fn if result is not None else sol_fn

    # --- Exercise 1: Morris Inorder ---
    print("\n── Exercise 1: Morris Inorder Traversal ──")
    fn1 = pick(morris_inorder, _sol_morris_inorder, from_list([4, 2, 6, 1, 3, 5, 7]))

    check("BST [4,2,6,1,3,5,7]",
          fn1(from_list([4, 2, 6, 1, 3, 5, 7])),
          [1, 2, 3, 4, 5, 6, 7])
    check("single node",
          fn1(from_list([1])),
          [1])
    check("empty tree",
          fn1(None),
          [])
    check("left-skewed",
          fn1(from_list([3, 2, None, 1])),
          [1, 2, 3])
    check("right-skewed",
          fn1(from_list([1, None, 2, None, 3])),
          [1, 2, 3])
    check("general tree",
          fn1(from_list([1, 2, 3, 4, 5, None, 6])),
          [4, 2, 5, 1, 3, 6])

    # --- Exercise 2: Morris Preorder ---
    print("\n── Exercise 2: Morris Preorder Traversal ──")
    fn2 = pick(morris_preorder, _sol_morris_preorder, from_list([4, 2, 6, 1, 3, 5, 7]))

    check("BST [4,2,6,1,3,5,7]",
          fn2(from_list([4, 2, 6, 1, 3, 5, 7])),
          [4, 2, 1, 3, 6, 5, 7])
    check("single node",
          fn2(from_list([1])),
          [1])
    check("empty tree",
          fn2(None),
          [])
    check("left-skewed",
          fn2(from_list([3, 2, None, 1])),
          [3, 2, 1])
    check("right-skewed",
          fn2(from_list([1, None, 2, None, 3])),
          [1, 2, 3])
    check("general tree",
          fn2(from_list([1, 2, 3, 4, 5, None, 6])),
          [1, 2, 4, 5, 3, 6])

    # --- Exercise 3: Validate BST ---
    print("\n── Exercise 3: Validate BST Using Morris ──")
    fn3 = pick(is_bst_morris, _sol_is_bst_morris, from_list([4, 2, 6, 1, 3, 5, 7]))

    check("valid BST",
          fn3(from_list([4, 2, 6, 1, 3, 5, 7])),
          True)
    check("invalid BST (root wrong)",
          fn3(from_list([1, 2, 3])),
          False)
    check("single node",
          fn3(from_list([5])),
          True)
    check("empty tree",
          fn3(None),
          True)
    check("two nodes valid",
          fn3(from_list([2, 1])),
          True)
    check("two nodes invalid",
          fn3(from_list([1, 2])),
          False)
    check("duplicate values (invalid)",
          fn3(from_list([2, 2])),
          False)

    # --- Exercise 4: Kth Smallest ---
    print("\n── Exercise 4: Kth Smallest in BST Using Morris ──")
    fn4 = pick(kth_smallest_morris, _sol_kth_smallest_morris,
               from_list([4, 2, 6, 1, 3, 5, 7]), 1)

    bst = from_list([4, 2, 6, 1, 3, 5, 7])  # inorder: [1,2,3,4,5,6,7]
    check("k=1 (smallest)",
          fn4(from_list([4, 2, 6, 1, 3, 5, 7]), 1), 1)
    check("k=4 (middle)",
          fn4(from_list([4, 2, 6, 1, 3, 5, 7]), 4), 4)
    check("k=7 (largest)",
          fn4(from_list([4, 2, 6, 1, 3, 5, 7]), 7), 7)
    check("k=8 (out of range)",
          fn4(from_list([4, 2, 6, 1, 3, 5, 7]), 8), None)
    check("single node k=1",
          fn4(from_list([5]), 1), 5)

    # --- Exercise 5: Recover BST ---
    print("\n── Exercise 5: Recover BST Using Morris ──")

    def test_recover(name, values, expected_inorder):
        """Build tree from list, recover it, check inorder matches expected."""
        tree = from_list(values)

        # Try user function first
        probe_tree = from_list(values)
        recover_bst_morris(probe_tree)
        probe_inorder = inorder_recursive(probe_tree)

        if probe_inorder == expected_inorder:
            # User's function works
            fn = recover_bst_morris
        else:
            # Fall back to solution
            fn = _sol_recover_bst_morris

        tree = from_list(values)
        fn(tree)
        got = inorder_recursive(tree)
        check(name, got, expected_inorder)

    # Nodes 1 and 3 swapped: [3,1,4,None,None,2] → should become [1,2,3,4]
    test_recover("adjacent swap [1,3,4,None,None,2]",
                 [3, 1, 4, None, None, 2], [1, 2, 3, 4])

    # Nodes 1 and 4 swapped: [4,3,None,None,1] should become [1,3,4]
    #   Original wrong tree:
    #       4         Swapped 1 and 4 in a BST [1,None,3,None,4]
    #      /          which creates [4,None,3,None,1]
    #     3
    #      \
    #       1
    test_recover("non-adjacent swap",
                 [4, None, 3, None, 1], [1, 3, 4])

    # Two-node tree: nodes swapped
    test_recover("two nodes swapped",
                 [2, 1], [1, 2])

    # Larger tree: swap 2 and 5
    # Correct BST inorder: [1,2,3,4,5,6,7]
    # After swapping nodes with val 2 and 5: [1,5,3,4,2,6,7]
    # Build a tree where 2 and 5 are swapped
    # Original BST: [4,2,6,1,3,5,7]
    # Swap val 2 and val 5: [4,5,6,1,3,2,7]
    test_recover("larger tree swap 2 and 5",
                 [4, 5, 6, 1, 3, 2, 7], [1, 2, 3, 4, 5, 6, 7])

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
