"""
Day 41: Binary Tree Views
=========================
Views are projections of a tree onto different 2D planes.
Each view answers: "which nodes are visible from this perspective?"

The key insight: every node has a (column, level) coordinate.
    column: root=0, left child=col-1, right child=col+1
    level:  root=0, children=level+1

Different views = different grouping/filtering of these coordinates.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list

from collections import deque, defaultdict
from typing import Optional


# ─── Left View ──────────────────────────────────────────────────────
#
# Leftmost node at each level. BFS approach: first node in each level.

def left_view(root: Optional[TreeNode]) -> list:
    """Return the leftmost node value at each level.

    BFS processes nodes left-to-right at each level.
    The first node we see at each level is the leftmost.

    Time: O(n) — visit every node once
    Space: O(w) — max width of tree (queue size)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == 0:  # first node at this level = leftmost
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result


# ─── Right View ─────────────────────────────────────────────────────
#
# Rightmost node at each level. BFS approach: last node in each level.

def right_view(root: Optional[TreeNode]) -> list:
    """Return the rightmost node value at each level.

    Same as left view, but we take the LAST node at each level.

    Time: O(n), Space: O(w)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.popleft()
            if i == level_size - 1:  # last node at this level = rightmost
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)

    return result


# ─── Top View ───────────────────────────────────────────────────────
#
# First node seen at each column when looking from above.
# BFS is REQUIRED here: we need the shallowest node at each column.

def top_view(root: Optional[TreeNode]) -> list:
    """Return nodes visible from the top, ordered left-to-right by column.

    Why BFS, not DFS? BFS processes by level, guaranteeing we see
    the shallowest (topmost) node at each column first. DFS would
    visit deep-left nodes before shallow-right nodes at the same column.

    Algorithm:
        1. BFS with (node, column) pairs
        2. First time we see a column → record it (that's the top view)
        3. Output columns in sorted order (left-to-right)

    Time: O(n), Space: O(n)
    """
    if not root:
        return []

    column_map = {}  # column → node value (first seen wins)
    queue = deque([(root, 0)])  # (node, column)

    while queue:
        node, col = queue.popleft()

        # Only record the first node at each column (shallowest = topmost)
        if col not in column_map:
            column_map[col] = node.val

        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))

    # Return values sorted by column (left-to-right)
    return [column_map[c] for c in sorted(column_map)]


# ─── Bottom View ────────────────────────────────────────────────────
#
# Last node seen at each column when looking from below.

def bottom_view(root: Optional[TreeNode]) -> list:
    """Return nodes visible from the bottom, ordered left-to-right by column.

    Opposite of top view: we want the DEEPEST (last seen in BFS) node
    at each column. Simply overwrite the column map instead of checking
    for first occurrence.

    Time: O(n), Space: O(n)
    """
    if not root:
        return []

    column_map = {}  # column → node value (last seen wins)
    queue = deque([(root, 0)])

    while queue:
        node, col = queue.popleft()

        # Always overwrite — last BFS visit at each column is deepest
        column_map[col] = node.val

        if node.left:
            queue.append((node.left, col - 1))
        if node.right:
            queue.append((node.right, col + 1))

    return [column_map[c] for c in sorted(column_map)]


# ─── Boundary Traversal ────────────────────────────────────────────
#
# Anti-clockwise walk around the tree perimeter:
#   left boundary (top-down, excluding leaves)
#   + leaves (left-to-right)
#   + right boundary (bottom-up, excluding leaves)

def boundary_traversal(root: Optional[TreeNode]) -> list:
    """Return anti-clockwise boundary of the tree.

    Three parts, combined carefully to avoid double-counting:
    1. Left boundary: walk from root down the left edge (exclude leaves)
    2. Leaves: all leaf nodes left-to-right (DFS preorder finds them in order)
    3. Right boundary: walk from root down the right edge (exclude leaves),
       then REVERSE (we want bottom-up order)

    Edge case: root is both left boundary and right boundary.
    We add root separately, then collect left boundary (excluding root),
    leaves (excluding root if it's a leaf — but root with children isn't a leaf),
    and right boundary (excluding root).

    Time: O(n), Space: O(n)
    """
    if not root:
        return []

    # Single node: it's the entire boundary
    if not root.left and not root.right:
        return [root.val]

    result = [root.val]  # root is always first

    # 1. Left boundary (excluding root and excluding leaves)
    _collect_left_boundary(root.left, result)

    # 2. All leaves, left-to-right
    _collect_leaves(root, result)

    # 3. Right boundary (excluding root and excluding leaves), reversed
    right_boundary = []
    _collect_right_boundary(root.right, right_boundary)
    result.extend(reversed(right_boundary))

    return result


def _collect_left_boundary(node: Optional[TreeNode], result: list):
    """Walk down the left edge, collecting non-leaf nodes.

    At each step: prefer left child. If no left child, go right.
    Stop when we hit a leaf (leaves are collected separately).
    """
    while node:
        # Stop at leaves — they'll be collected by _collect_leaves
        if not node.left and not node.right:
            break
        result.append(node.val)
        # Prefer left child; if absent, go right
        node = node.left if node.left else node.right


def _collect_right_boundary(node: Optional[TreeNode], result: list):
    """Walk down the right edge, collecting non-leaf nodes.

    Mirror of _collect_left_boundary: prefer right child, fallback to left.
    Result will be reversed by the caller (we want bottom-up order).
    """
    while node:
        if not node.left and not node.right:
            break
        result.append(node.val)
        node = node.right if node.right else node.left


def _collect_leaves(node: Optional[TreeNode], result: list):
    """Collect all leaf nodes left-to-right using preorder DFS.

    Preorder guarantees left-to-right order because we visit left subtree
    before right subtree, and process the node before its children.
    """
    if not node:
        return
    if not node.left and not node.right:
        result.append(node.val)
        return
    _collect_leaves(node.left, result)
    _collect_leaves(node.right, result)


# ─── Vertical Order Traversal ──────────────────────────────────────
#
# Group nodes by column, ordered by level within each column.

def vertical_order_traversal(root: Optional[TreeNode]) -> list[list]:
    """Return nodes grouped by column, sorted by level within each column.

    Uses BFS to naturally process nodes level-by-level.
    Within the same (column, level), nodes appear in left-to-right BFS order.

    Returns: list of lists, one per column, ordered from leftmost to rightmost column.

    Time: O(n log n) due to sorting columns, Space: O(n)
    """
    if not root:
        return []

    # column → list of (level, value) pairs
    columns = defaultdict(list)
    queue = deque([(root, 0, 0)])  # (node, column, level)

    while queue:
        node, col, level = queue.popleft()
        columns[col].append((level, node.val))

        if node.left:
            queue.append((node.left, col - 1, level + 1))
        if node.right:
            queue.append((node.right, col + 1, level + 1))

    # Sort columns by column index, within each column sort by level
    result = []
    for col in sorted(columns):
        # Sort by level; BFS already gives left-to-right order within same level
        col_nodes = sorted(columns[col], key=lambda x: x[0])
        result.append([val for _, val in col_nodes])

    return result


# ─── Diagonal Traversal ────────────────────────────────────────────
#
# Nodes on the same diagonal have the same (column - level) value.
# Going right: col+1, level+1 → difference unchanged (same diagonal)
# Going left: col-1, level+1 → difference decreases by 2 (new diagonal)

def diagonal_traversal(root: Optional[TreeNode]) -> list[list]:
    """Return nodes grouped by diagonal (col - level = constant).

    Diagonals run from upper-left to lower-right.
    Within each diagonal, nodes are ordered by level (BFS order).

    Returns: list of lists, one per diagonal, ordered from top-right to bottom-left.

    Time: O(n log n), Space: O(n)
    """
    if not root:
        return []

    diagonals = defaultdict(list)
    queue = deque([(root, 0, 0)])  # (node, column, level)

    while queue:
        node, col, level = queue.popleft()
        diag = col - level
        diagonals[diag].append((level, node.val))

        if node.left:
            queue.append((node.left, col - 1, level + 1))
        if node.right:
            queue.append((node.right, col + 1, level + 1))

    # Sort diagonals: highest diagonal value first (top-right → bottom-left)
    result = []
    for d in sorted(diagonals, reverse=True):
        nodes = sorted(diagonals[d], key=lambda x: x[0])
        result.append([val for _, val in nodes])

    return result


# ─── Demonstration ──────────────────────────────────────────────────

if __name__ == "__main__":
    # Build example tree:
    #
    #            1
    #           / \
    #          2   3
    #         / \   \
    #        4   5   6
    #       /
    #      7
    #
    # Column assignments:
    #   col -3: 7
    #   col -2: 4
    #   col -1: 2
    #   col  0: 1, 5
    #   col +1: 3
    #   col +2: 6

    tree = from_list([1, 2, 3, 4, 5, None, 6, 7])

    print("Tree structure:")
    print("        1")
    print("       / \\")
    print("      2   3")
    print("     / \\   \\")
    print("    4   5   6")
    print("   /")
    print("  7")
    print()

    print("─── Views ───────────────────────────────────")
    print(f"Left view:     {left_view(tree)}")
    print(f"Right view:    {right_view(tree)}")
    print(f"Top view:      {top_view(tree)}")
    print(f"Bottom view:   {bottom_view(tree)}")
    print(f"Boundary:      {boundary_traversal(tree)}")
    print()

    print("─── Vertical Order ──────────────────────────")
    vo = vertical_order_traversal(tree)
    print(f"Columns: {vo}")
    for i, col_idx in enumerate(sorted(range(len(vo)), key=lambda x: x)):
        min_col = -3  # we know the leftmost column for this tree
        print(f"  column {min_col + col_idx}: {vo[col_idx]}")
    print()

    print("─── Diagonal Traversal ──────────────────────")
    diags = diagonal_traversal(tree)
    print(f"Diagonals: {diags}")
    print()

    # ─── Verify correctness ──────────────────────────────────────────
    print("─── Verification ────────────────────────────")

    assert left_view(tree) == [1, 2, 4, 7], f"Left view failed: {left_view(tree)}"
    print("Left view:     PASSED")

    assert right_view(tree) == [1, 3, 6, 7], f"Right view failed: {right_view(tree)}"
    print("Right view:    PASSED")

    assert top_view(tree) == [7, 4, 2, 1, 3, 6], f"Top view failed: {top_view(tree)}"
    print("Top view:      PASSED")

    assert bottom_view(tree) == [7, 4, 2, 5, 3, 6], f"Bottom view failed: {bottom_view(tree)}"
    print("Bottom view:   PASSED")

    assert boundary_traversal(tree) == [1, 2, 4, 7, 5, 6, 3], \
        f"Boundary failed: {boundary_traversal(tree)}"
    print("Boundary:      PASSED")

    assert vertical_order_traversal(tree) == [[7], [4], [2], [1, 5], [3], [6]], \
        f"Vertical order failed: {vertical_order_traversal(tree)}"
    print("Vertical order: PASSED")

    assert diagonal_traversal(tree) == [[1, 3, 6], [2, 5], [4], [7]], \
        f"Diagonal failed: {diagonal_traversal(tree)}"
    print("Diagonal:      PASSED")

    # Edge cases
    assert left_view(None) == []
    assert right_view(None) == []
    assert top_view(None) == []
    assert bottom_view(None) == []
    assert boundary_traversal(None) == []
    assert vertical_order_traversal(None) == []
    assert diagonal_traversal(None) == []
    print("\nEmpty tree:    ALL PASSED")

    single = from_list([42])
    assert left_view(single) == [42]
    assert right_view(single) == [42]
    assert top_view(single) == [42]
    assert bottom_view(single) == [42]
    assert boundary_traversal(single) == [42]
    assert vertical_order_traversal(single) == [[42]]
    assert diagonal_traversal(single) == [[42]]
    print("Single node:   ALL PASSED")

    print("\nAll verifications passed!")
