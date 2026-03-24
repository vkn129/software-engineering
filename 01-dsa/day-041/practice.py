"""
Day 41 Practice: Binary Tree Views
====================================
Implement each function. Run this file to test your solutions.

Key mental model:
    Every view = BFS with a coordinate system.
    Left/right views group by LEVEL, take first/last.
    Top/bottom views group by COLUMN, take first/last.
    Boundary traversal = left edge + leaves + right edge (reversed).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list


# ─── Exercise 1: Left Side View ────────────────────────────────────
#
# Return the leftmost node at each level (what you'd see standing
# on the left side of the tree).
#
#         1
#        / \
#       2   3          Left view: [1, 2, 4, 7]
#      / \   \
#     4   5   6
#    /
#   7
#
# Approach: BFS, take the FIRST node at each level.

def left_side_view(root):
    # TODO: implement
    pass


# ─── Exercise 2: Right Side View ───────────────────────────────────
#
# Return the rightmost node at each level (what you'd see standing
# on the right side of the tree).
#
#         1
#        / \
#       2   3          Right view: [1, 3, 6, 7]
#      / \   \
#     4   5   6
#    /
#   7
#
# Approach: BFS, take the LAST node at each level.

def right_side_view(root):
    # TODO: implement
    pass


# ─── Exercise 3: Top View ──────────────────────────────────────────
#
# Looking down from above: the first node visible at each column.
# Column assignment: root=0, left child=col-1, right child=col+1.
#
#         1  (col=0)
#        / \
#       2   3          Top view: [4, 2, 1, 3, 6]
#      / \   \         (columns -2, -1, 0, +1, +2)
#     4   5   6
#
# Node 5 (col=0) is hidden by node 1 (col=0, shallower level).
#
# IMPORTANT: Use BFS so that shallower nodes are recorded first.

def top_view(root):
    # TODO: implement
    pass


# ─── Exercise 4: Bottom View ───────────────────────────────────────
#
# Looking up from below: the last node visible at each column.
#
#         1  (col=0)
#        / \
#       2   3          Bottom view: [4, 2, 5, 3, 6]
#      / \   \         (columns -2, -1, 0, +1, +2)
#     4   5   6
#
# Node 5 (col=0) replaces node 1 because it's deeper.
#
# Approach: like top view, but always OVERWRITE the column map.

def bottom_view(root):
    # TODO: implement
    pass


# ─── Exercise 5: Vertical Order Traversal ──────────────────────────
#
# Group nodes by column, sorted by level within each column.
# Return as list of lists, from leftmost to rightmost column.
#
#         1
#        / \
#       2   3          Vertical order: [[4], [2], [1, 5], [3], [6]]
#      / \   \
#     4   5   6
#
# Column -2: [4]
# Column -1: [2]
# Column  0: [1, 5]   (1 at level 0, 5 at level 2)
# Column +1: [3]
# Column +2: [6]

def vertical_order(root):
    # TODO: implement
    pass


# ─── Exercise 6: Boundary Traversal (Anti-clockwise) ───────────────
#
# Walk around the tree anti-clockwise:
#   1. Root
#   2. Left boundary (top-down, non-leaf nodes)
#   3. Leaves (left-to-right)
#   4. Right boundary (bottom-up, non-leaf nodes)
#
#         1
#        / \
#       2   3          Boundary: [1, 2, 4, 5, 6, 3]
#      / \   \
#     4   5   6
#
# Left boundary (excl root, excl leaves): [2]
# Leaves: [4, 5, 6]
# Right boundary (excl root, excl leaves, reversed): [3]
#
# Watch out for double-counting! Leaves should NOT appear in
# the left/right boundary lists.

def boundary_traversal(root):
    # TODO: implement
    pass


# ─── Reference Solutions ────────────────────────────────────────────

def _sol_left_side_view(root):
    if not root:
        return []
    from collections import deque
    result = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == 0:
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result


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
            if i == level_size - 1:
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result


def _sol_top_view(root):
    if not root:
        return []
    from collections import deque
    column_map = {}
    queue = deque([(root, 0)])
    while queue:
        node, col = queue.popleft()
        if col not in column_map:
            column_map[col] = node.val
        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))
    return [column_map[c] for c in sorted(column_map)]


def _sol_bottom_view(root):
    if not root:
        return []
    from collections import deque
    column_map = {}
    queue = deque([(root, 0)])
    while queue:
        node, col = queue.popleft()
        column_map[col] = node.val
        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))
    return [column_map[c] for c in sorted(column_map)]


def _sol_vertical_order(root):
    if not root:
        return []
    from collections import deque, defaultdict
    columns = defaultdict(list)
    queue = deque([(root, 0, 0)])
    while queue:
        node, col, level = queue.popleft()
        columns[col].append((level, node.val))
        if node.left:
            queue.append((node.left, col - 1, level + 1))
        if node.right:
            queue.append((node.right, col + 1, level + 1))
    result = []
    for col in sorted(columns):
        col_nodes = sorted(columns[col], key=lambda x: x[0])
        result.append([val for _, val in col_nodes])
    return result


def _sol_boundary_traversal(root):
    if not root:
        return []
    if not root.left and not root.right:
        return [root.val]

    result = [root.val]

    # Left boundary (excluding root and leaves)
    node = root.left
    while node:
        if not node.left and not node.right:
            break
        result.append(node.val)
        node = node.left if node.left else node.right

    # Leaves (left-to-right via preorder DFS)
    def collect_leaves(n):
        if not n:
            return
        if not n.left and not n.right:
            result.append(n.val)
            return
        collect_leaves(n.left)
        collect_leaves(n.right)

    collect_leaves(root)

    # Right boundary (excluding root and leaves), collected top-down then reversed
    right_boundary = []
    node = root.right
    while node:
        if not node.left and not node.right:
            break
        right_boundary.append(node.val)
        node = node.right if node.right else node.left

    result.extend(reversed(right_boundary))
    return result


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

    #
    # Tree used for most tests:
    #         1
    #        / \
    #       2   3
    #      / \   \
    #     4   5   6
    #    /
    #   7
    #
    tree = from_list([1, 2, 3, 4, 5, None, 6, 7])

    #
    # Simpler tree for boundary:
    #         1
    #        / \
    #       2   3
    #      / \   \
    #     4   5   6
    #
    simple = from_list([1, 2, 3, 4, 5, None, 6])

    # --- Exercise 1: Left Side View ---
    print("\n── Exercise 1: Left Side View ──")
    fn1 = left_side_view if left_side_view(tree) is not None else _sol_left_side_view
    check("standard tree", fn1(tree), [1, 2, 4, 7])
    check("single node", fn1(from_list([1])), [1])
    check("empty tree", fn1(None), [])
    check("right-skewed", fn1(from_list([1, None, 2, None, 3])), [1, 2, 3])

    # --- Exercise 2: Right Side View ---
    print("\n── Exercise 2: Right Side View ──")
    fn2 = right_side_view if right_side_view(tree) is not None else _sol_right_side_view
    check("standard tree", fn2(tree), [1, 3, 6, 7])
    check("single node", fn2(from_list([1])), [1])
    check("empty tree", fn2(None), [])
    check("left-skewed", fn2(from_list([1, 2, None, 3])), [1, 2, 3])

    # --- Exercise 3: Top View ---
    print("\n── Exercise 3: Top View ──")
    fn3 = top_view if top_view(tree) is not None else _sol_top_view
    check("standard tree", fn3(tree), [7, 4, 2, 1, 3, 6])
    check("simple tree", fn3(simple), [4, 2, 1, 3, 6])
    check("single node", fn3(from_list([1])), [1])
    check("empty tree", fn3(None), [])

    # --- Exercise 4: Bottom View ---
    print("\n── Exercise 4: Bottom View ──")
    fn4 = bottom_view if bottom_view(tree) is not None else _sol_bottom_view
    check("standard tree", fn4(tree), [7, 4, 2, 5, 3, 6])
    check("simple tree", fn4(simple), [4, 2, 5, 3, 6])
    check("single node", fn4(from_list([1])), [1])
    check("empty tree", fn4(None), [])

    # --- Exercise 5: Vertical Order Traversal ---
    print("\n── Exercise 5: Vertical Order Traversal ──")
    fn5 = vertical_order if vertical_order(tree) is not None else _sol_vertical_order
    check("standard tree", fn5(tree), [[7], [4], [2], [1, 5], [3], [6]])
    check("simple tree", fn5(simple), [[4], [2], [1, 5], [3], [6]])
    check("single node", fn5(from_list([1])), [[1]])
    check("empty tree", fn5(None), [])

    # --- Exercise 6: Boundary Traversal ---
    print("\n── Exercise 6: Boundary Traversal ──")
    fn6 = boundary_traversal if boundary_traversal(tree) is not None else _sol_boundary_traversal
    check("standard tree", fn6(tree), [1, 2, 4, 7, 5, 6, 3])
    check("simple tree", fn6(simple), [1, 2, 4, 5, 6, 3])
    check("single node", fn6(from_list([1])), [1])
    check("empty tree", fn6(None), [])
    # Left-only tree: boundary is just the path down and back
    check("left-skewed", fn6(from_list([1, 2, None, 3])), [1, 2, 3])

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
