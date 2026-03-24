"""
Day 47 Practice: Red-Black Tree Exercises
==========================================
Implement each function, then run: python practice.py

These exercises build intuition for red-black invariants without requiring
you to implement the full insert/delete fixup (you did that in red_black_tree.py).

Rules:
- Do NOT use any external libraries.
- Solutions are at the bottom — try first.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from red_black_tree import RedBlackTree, RBNode, RED, BLACK


# ─── Helper: Build a simple tree for testing ────────────────────────

def _build_test_tree(keys):
    """Build an RB tree by inserting keys in order."""
    tree = RedBlackTree()
    for k in keys:
        tree.insert(k)
    return tree


# ─── Exercise 1: Validate Red-Black Properties ─────────────────────
#
# Check all 5 red-black invariants:
# 1. Every node is red or black
# 2. Root is black
# 3. Every leaf (NIL) is black
# 4. Red node → both children are black (no red-red)
# 5. All paths from a node to its descendant NILs have the same black count
#
# Return (is_valid, violation_message) — ("" if valid)

def validate_rb_properties(tree):
    # TODO: implement
    pass


# ─── Exercise 2: Count Red and Black Nodes ─────────────────────────
#
# Return (red_count, black_count) for all internal nodes (not NIL sentinel).

def count_colors(tree):
    # TODO: return (red_count, black_count)
    pass


# ─── Exercise 3: Compute Black-Height ──────────────────────────────
#
# The black-height of a node = number of black nodes on any path from
# that node to a leaf (NIL), NOT counting the node itself.
# If the tree violates the black-height invariant, return -1.

def black_height(tree):
    # TODO: return black-height of the root, or -1 if invalid
    pass


# ─── Exercise 4: Red-Black to 2-3-4 Tree ───────────────────────────
#
# Convert the RB tree to its 2-3-4 tree equivalent.
# A red-black tree is a binary encoding of a 2-3-4 tree:
#   - A black node alone = 2-node (1 key, 2 children)
#   - A black node + 1 red child = 3-node (2 keys, 3 children)
#   - A black node + 2 red children = 4-node (3 keys, 4 children)
#
# Return a list of tuples: [(keys_in_node, num_children), ...]
# representing each node of the equivalent 2-3-4 tree.

def to_234_tree(tree):
    # TODO: return list of (keys_tuple, child_count) for each 2-3-4 node
    pass


# ─── Exercise 5: Build RB Tree from Sorted Array ───────────────────
#
# Given a sorted array, construct a valid red-black tree.
# Strategy: build a perfect BST, color all nodes black, then color
# the deepest level red if needed to keep black-height consistent.
# Return a RedBlackTree instance.

def rb_from_sorted(arr):
    # TODO: implement
    pass


# ─── Exercise 6: Could This BST Be Colored as a Valid RB Tree? ─────
#
# Given a plain BST (as nested tuples: (val, left, right) or None),
# determine if there exists a valid red-black coloring.
# A BST can be colored as RB iff:
#   - Its height h satisfies: h <= 2 * floor(log2(n+1))
#   - All root-to-leaf path lengths differ by at most a factor of 2
# (Simplified check: just verify path lengths are within factor of 2)

def can_be_rb_colored(bst_tuple):
    # TODO: return True/False
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_validate_rb_properties(tree):
    nil = tree.NIL
    root = tree.root

    # Property 2: root is black
    if root != nil and root.color != BLACK:
        return False, "Root is not black"

    # Walk tree and check properties 1, 4, 5
    def check(node):
        if node == nil:
            return 1  # NIL is black, contributes 1 to black height

        # Property 4: red node's children must be black
        if node.color == RED:
            if (node.left != nil and node.left.color == RED) or \
               (node.right != nil and node.right.color == RED):
                return -1  # Red-red violation

        left_bh = check(node.left)
        right_bh = check(node.right)

        if left_bh == -1 or right_bh == -1:
            return -1
        if left_bh != right_bh:
            return -1  # Black height mismatch

        return left_bh + (1 if node.color == BLACK else 0)

    bh = check(root)
    if bh == -1:
        return False, "Invariant violation (red-red or black-height mismatch)"
    return True, ""


def _sol_count_colors(tree):
    nil = tree.NIL
    red = 0
    black = 0

    def walk(node):
        nonlocal red, black
        if node == nil:
            return
        if node.color == RED:
            red += 1
        else:
            black += 1
        walk(node.left)
        walk(node.right)

    walk(tree.root)
    return red, black


def _sol_black_height(tree):
    nil = tree.NIL

    def bh(node):
        if node == nil:
            return 0
        left = bh(node.left)
        right = bh(node.right)
        if left == -1 or right == -1 or left != right:
            return -1
        return left + (1 if node.color == BLACK else 0)

    return bh(tree.root)


def _sol_to_234_tree(tree):
    nil = tree.NIL
    nodes = []

    def walk(node):
        if node == nil:
            return
        # Skip red nodes — they'll be grouped with their black parent
        if node.color == RED:
            return

        # This is a black node — find its red children to form 2-3-4 node
        keys = []
        children = []

        # Left red child?
        if node.left != nil and node.left.color == RED:
            # Left red: part of this 2-3-4 node
            children.append(node.left.left)
            keys.append(node.left.key)
            children.append(node.left.right)
        else:
            children.append(node.left)

        keys.append(node.key)

        # Right red child?
        if node.right != nil and node.right.color == RED:
            children.append(node.right.left)
            keys.append(node.right.key)
            children.append(node.right.right)
        else:
            children.append(node.right)

        real_children = sum(1 for c in children if c != nil)
        nodes.append((tuple(keys), len(children)))

        # Recurse into children
        for c in children:
            walk(c)

    walk(tree.root)
    return nodes


def _sol_rb_from_sorted(arr):
    import math
    tree = RedBlackTree()
    if not arr:
        return tree

    # Simple approach: just insert in balanced order
    def insert_balanced(lo, hi):
        if lo > hi:
            return
        mid = (lo + hi) // 2
        tree.insert(arr[mid])
        insert_balanced(lo, mid - 1)
        insert_balanced(mid + 1, hi)

    insert_balanced(0, len(arr) - 1)
    return tree


def _sol_can_be_rb_colored(bst_tuple):
    if bst_tuple is None:
        return True

    # Collect all root-to-leaf path lengths
    paths = []

    def walk(node, depth):
        if node is None:
            paths.append(depth)
            return
        val, left, right = node
        walk(left, depth + 1)
        walk(right, depth + 1)

    walk(bst_tuple, 0)

    if not paths:
        return True

    shortest = min(paths)
    longest = max(paths)
    # In a valid RB tree, longest path <= 2 * shortest path
    return longest <= 2 * shortest


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

    tree = _build_test_tree([10, 20, 30, 15, 25, 5, 1])

    # Exercise 1: Validate
    print("\nExercise 1: Validate RB Properties")
    for fn in [validate_rb_properties, _sol_validate_rb_properties]:
        if fn is validate_rb_properties and fn(tree) is None:
            print("  (skipped — not implemented)")
            break
        valid, msg = fn(tree)
        check(f"{fn.__name__} valid", valid, True)

    # Exercise 2: Count Colors
    print("\nExercise 2: Count Colors")
    for fn in [count_colors, _sol_count_colors]:
        if fn is count_colors and fn(tree) is None:
            print("  (skipped — not implemented)")
            break
        r, b = fn(tree)
        check(f"{fn.__name__} total nodes", r + b, 7)
        check(f"{fn.__name__} has both colors", r > 0 and b > 0, True)

    # Exercise 3: Black Height
    print("\nExercise 3: Black Height")
    for fn in [black_height, _sol_black_height]:
        if fn is black_height and fn(tree) is None:
            print("  (skipped — not implemented)")
            break
        bh = fn(tree)
        check(f"{fn.__name__} >= 1", bh >= 1, True)
        check(f"{fn.__name__} valid (not -1)", bh != -1, True)

    # Exercise 4: 2-3-4 Tree
    print("\nExercise 4: Red-Black to 2-3-4 Tree")
    for fn in [to_234_tree, _sol_to_234_tree]:
        if fn is to_234_tree and fn(tree) is None:
            print("  (skipped — not implemented)")
            break
        nodes = fn(tree)
        check(f"{fn.__name__} produces nodes", len(nodes) > 0, True)
        # All keys should sum to original keys
        all_keys = sorted(k for keys, _ in nodes for k in keys)
        check(f"{fn.__name__} all keys present", all_keys, [1, 5, 10, 15, 20, 25, 30])

    # Exercise 5: From Sorted Array
    print("\nExercise 5: RB from Sorted Array")
    for fn in [rb_from_sorted, _sol_rb_from_sorted]:
        if fn is rb_from_sorted and fn([1, 2, 3]) is None:
            print("  (skipped — not implemented)")
            break
        t = fn([1, 2, 3, 4, 5, 6, 7])
        valid, _ = _sol_validate_rb_properties(t)
        check(f"{fn.__name__} valid RB tree", valid, True)

    # Exercise 6: Can Be Colored
    print("\nExercise 6: Can BST Be RB Colored?")
    balanced = (4, (2, (1, None, None), (3, None, None)), (6, (5, None, None), (7, None, None)))
    degenerate = (1, None, (2, None, (3, None, (4, None, None))))
    for fn in [can_be_rb_colored, _sol_can_be_rb_colored]:
        if fn is can_be_rb_colored and fn(balanced) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__} balanced", fn(balanced), True)
        check(f"{fn.__name__} degenerate", fn(degenerate), False)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
