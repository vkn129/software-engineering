"""
Day 39: Tree Diameter, Depth, Balance Checking + Path Sum Problems
===================================================================
All these problems share one recursive skeleton:
    1. Base case: node is None -> return identity value
    2. Compute result for left and right children
    3. Combine at current node (update global answer + return value for parent)

The subtle part: what you RETURN (for parent) differs from what you TRACK (global answer).
    - diameter: return depth, track max(left_depth + right_depth)
    - max_path_sum: return max single-direction gain, track max turning path
    - balance: return height, track whether any subtree failed
"""

import sys
import os
from collections import defaultdict
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list, print_tree


# ─── Diameter ────────────────────────────────────────────────────────
#
# Diameter = longest path between any two nodes (in edges).
# Key insight: the longest path through a node = left_depth + right_depth.
# The overall diameter is the max of this across ALL nodes.
#
# Common mistake: assuming the path goes through the root. It might not.
#
#        1
#       / \
#      2   3       Diameter = 4 (path 5→4→2→6→7), doesn't touch node 3
#     / \
#    4   6
#   /     \
#  5       7

def diameter(root: Optional[TreeNode]) -> int:
    """Compute tree diameter in O(n) using bottom-up depth computation.

    We track the max diameter as a side effect while returning depth
    to the parent. Each node is visited exactly once.

    Returns the diameter (number of edges on the longest path).
    """
    max_diam = [0]  # mutable container for closure access

    def _depth(node):
        """Returns depth (number of edges) of subtree rooted at node.
        Updates max_diam as a side effect.
        """
        if node is None:
            return 0

        left_d = _depth(node.left)
        right_d = _depth(node.right)

        # The path through this node has length left_d + right_d
        max_diam[0] = max(max_diam[0], left_d + right_d)

        # Return depth of this subtree for parent to use
        # +1 because we add the edge from parent to this node
        return 1 + max(left_d, right_d)

    _depth(root)
    return max_diam[0]


# ─── Max Depth & Min Depth ───────────────────────────────────────────

def max_depth(root: Optional[TreeNode]) -> int:
    """Maximum depth = number of nodes on the longest root-to-leaf path.

    Note: this counts NODES, not edges. max_depth = height + 1.
    An empty tree has max_depth 0.
    """
    if root is None:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))


def min_depth(root: Optional[TreeNode]) -> int:
    """Minimum depth = number of nodes on the shortest root-to-leaf path.

    GOTCHA: if a node has only one child, we can't count the missing
    child as a "path to a leaf" — it's not a leaf, it's nothing.
    We must go through the existing child.

    Example:
        1
         \
          2     min_depth = 2 (not 1, because root is NOT a leaf)
    """
    if root is None:
        return 0

    # If one child is missing, we MUST go through the other child
    if root.left is None:
        return 1 + min_depth(root.right)
    if root.right is None:
        return 1 + min_depth(root.left)

    return 1 + min(min_depth(root.left), min_depth(root.right))


# ─── Balance Checking ────────────────────────────────────────────────
#
# Naive approach: call height() at every node → O(n²)
# Better: compute height bottom-up, return -1 sentinel if unbalanced → O(n)

def is_balanced(root: Optional[TreeNode]) -> bool:
    """Check if tree is height-balanced in O(n) single pass.

    Returns True if for EVERY node, |height(left) - height(right)| <= 1.

    Uses -1 as a sentinel to short-circuit: once any subtree is found
    unbalanced, we propagate -1 upward without further computation.
    """
    def _check_height(node):
        """Returns height if balanced, -1 if any subtree is unbalanced."""
        if node is None:
            return 0

        left_h = _check_height(node.left)
        if left_h == -1:
            return -1  # short-circuit: left subtree already failed

        right_h = _check_height(node.right)
        if right_h == -1:
            return -1  # short-circuit: right subtree already failed

        if abs(left_h - right_h) > 1:
            return -1  # this node is unbalanced

        return 1 + max(left_h, right_h)

    return _check_height(root) != -1


# ─── Path Sum: Root to Leaf ─────────────────────────────────────────
#
# Does any root-to-leaf path sum to exactly target?
# Technique: subtract node value as you descend; at a leaf, check if remainder == 0.

def path_sum_root_to_leaf(root: Optional[TreeNode], target: int) -> bool:
    """Returns True if any root-to-leaf path sums to target.

    Key: a "path" must end at a LEAF (node with no children).
    An empty tree has no paths, so returns False for any target.
    """
    if root is None:
        return False

    remainder = target - root.val

    # If leaf node, check if path sum matches
    if root.left is None and root.right is None:
        return remainder == 0

    # Otherwise, check both subtrees with reduced target
    return (path_sum_root_to_leaf(root.left, remainder) or
            path_sum_root_to_leaf(root.right, remainder))


# ─── All Root-to-Leaf Paths ─────────────────────────────────────────

def all_root_to_leaf_paths(root: Optional[TreeNode]) -> list[list[int]]:
    """Return all root-to-leaf paths as lists of node values.

    Uses backtracking: build path as we descend, copy at leaves,
    then remove current node when returning (backtrack).

    Time: O(n * h) — visit every node, and at each leaf copy a path of length h.
    For a balanced tree: O(n log n). Worst case (skewed): O(n²).
    """
    if root is None:
        return []

    result = []
    path = []

    def _backtrack(node):
        path.append(node.val)

        # Leaf: record a copy of the current path
        if node.left is None and node.right is None:
            result.append(path[:])  # copy!
        else:
            if node.left:
                _backtrack(node.left)
            if node.right:
                _backtrack(node.right)

        path.pop()  # backtrack

    _backtrack(root)
    return result


# ─── Path Sum Count (Any Node to Any Descendant) ────────────────────
#
# Count paths that sum to target, where path can start at ANY node and
# end at ANY descendant. This is the tree analog of "subarray sum = k".
#
# Technique: prefix sums + hash map.
# Running sum from root to current node. If (current_sum - target) exists
# in the prefix map, that many paths ending here sum to target.
#
# CRITICAL: backtrack the prefix map after recursing (remove current sum).
# Without this, sibling subtrees would see stale prefix sums from branches
# they're not connected to.

def path_sum_count(root: Optional[TreeNode], target: int) -> int:
    """Count paths summing to target from any node to any descendant.

    Uses prefix sum technique for O(n) time.

    The prefix_map stores {prefix_sum: count_of_times_seen}.
    At each node, if (current_sum - target) is in the map, those many
    paths end at the current node with the desired sum.
    """
    count = [0]
    prefix_map = defaultdict(int)
    prefix_map[0] = 1  # empty prefix (path starting from root)

    def _dfs(node, current_sum):
        if node is None:
            return

        current_sum += node.val

        # How many prefix sums equal (current_sum - target)?
        # Each one represents a valid path ending here.
        count[0] += prefix_map[current_sum - target]

        # Record this prefix sum for descendants
        prefix_map[current_sum] += 1

        _dfs(node.left, current_sum)
        _dfs(node.right, current_sum)

        # BACKTRACK: remove this prefix sum so sibling subtrees
        # don't incorrectly use it
        prefix_map[current_sum] -= 1

    _dfs(root, 0)
    return count[0]


# ─── Maximum Path Sum (Any to Any) ──────────────────────────────────
#
# Find the maximum sum path between any two nodes.
# A path visits each node at most once and can "turn" at one node.
#
# At each node, we compute:
#   - max_gain: best sum going DOWN through this node (one direction only)
#   - path_through: best path that TURNS here (left + node + right)
#
# We RETURN max_gain to the parent (parent can only extend in one direction).
# We TRACK max of path_through across all nodes (the global answer).
#
# Negative children: clamp to 0 (better to not include them).
# But the answer itself CAN be negative (tree of all negatives).

def max_path_sum(root: Optional[TreeNode]) -> int:
    """Find maximum sum path between any two nodes. O(n) time.

    Each node can appear at most once in the path. The path can
    start and end at any node (not necessarily root or leaf).
    """
    if root is None:
        return 0

    best = [float('-inf')]

    def _max_gain(node):
        """Returns max sum going DOWN from this node (single direction).
        Updates best[] as a side effect with the turning path.
        """
        if node is None:
            return 0

        # Max gain from left/right children, clamped to 0
        # (don't take a path if it reduces the sum)
        left_gain = max(_max_gain(node.left), 0)
        right_gain = max(_max_gain(node.right), 0)

        # Path that TURNS at this node: left arm + node + right arm
        path_through = left_gain + node.val + right_gain
        best[0] = max(best[0], path_through)

        # Return to parent: node + best single direction
        # (parent can only extend the path in one direction)
        return node.val + max(left_gain, right_gain)

    _max_gain(root)
    return best[0]


# ─── Demonstration ───────────────────────────────────────────────────

if __name__ == "__main__":
    # ── Diameter Demo ──
    #         1
    #        / \
    #       2   3
    #      / \
    #     4   5
    #    /
    #   6
    print("=" * 55)
    print("TREE DIAMETER")
    print("=" * 55)
    t1 = from_list([1, 2, 3, 4, 5, None, None, 6])
    print("\nTree:")
    print_tree(t1)
    d = diameter(t1)
    print(f"\nDiameter: {d}")
    print("  (path: 6 → 4 → 2 → 1 → 3, length = 4 edges)")
    print(f"  The longest path passes through the root here")

    # Diameter that doesn't pass through root
    #     1
    #    /
    #   2
    #  / \
    # 3   4
    t1b = from_list([1, 2, None, 3, 4])
    print(f"\nSkewed tree diameter: {diameter(t1b)}")
    print("  (path: 3 → 2 → 4, length = 2 edges, never touches root)")

    # ── Depth Demo ──
    print("\n" + "=" * 55)
    print("MAX DEPTH & MIN DEPTH")
    print("=" * 55)
    #       1
    #      / \
    #     2   3
    #    /
    #   4
    t2 = from_list([1, 2, 3, 4])
    print("\nTree:")
    print_tree(t2)
    print(f"\nmax_depth: {max_depth(t2)}  (path: 1→2→4, 3 nodes)")
    print(f"min_depth: {min_depth(t2)}  (path: 1→3, 2 nodes)")

    # min_depth gotcha: single-child node
    t2b = from_list([1, None, 2])
    print(f"\nTree [1, None, 2]:")
    print(f"  min_depth: {min_depth(t2b)}  (must go through right child, NOT 1)")

    # ── Balance Demo ──
    print("\n" + "=" * 55)
    print("BALANCE CHECKING")
    print("=" * 55)
    balanced = from_list([1, 2, 3, 4, 5])
    unbalanced = from_list([1, 2, None, 3, None, None, None, 4])
    print(f"\n[1,2,3,4,5] balanced? {is_balanced(balanced)}")
    print(f"[1,2,None,3,None,...,4] balanced? {is_balanced(unbalanced)}")

    # ── Path Sum: Root to Leaf ──
    print("\n" + "=" * 55)
    print("PATH SUM (ROOT TO LEAF)")
    print("=" * 55)
    #         5
    #        / \
    #       4   8
    #      /   / \
    #     11  13  4
    #    / \       \
    #   7   2       1
    t3 = from_list([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
    print("\nTree:")
    print_tree(t3)
    print(f"\npath_sum(22): {path_sum_root_to_leaf(t3, 22)}  (5→4→11→2)")
    print(f"path_sum(26): {path_sum_root_to_leaf(t3, 26)}  (5→8→13)")
    print(f"path_sum(99): {path_sum_root_to_leaf(t3, 99)}  (no such path)")

    # ── All Root-to-Leaf Paths ──
    print("\n" + "=" * 55)
    print("ALL ROOT-TO-LEAF PATHS")
    print("=" * 55)
    paths = all_root_to_leaf_paths(t3)
    for p in paths:
        print(f"  {' → '.join(map(str, p))}  (sum = {sum(p)})")

    # ── Path Sum Count (Any Node) ──
    print("\n" + "=" * 55)
    print("PATH SUM COUNT (ANY NODE → ANY DESCENDANT)")
    print("=" * 55)
    #       10
    #      /  \
    #     5   -3
    #    / \    \
    #   3   2   11
    #  / \   \
    # 3  -2   1
    t4 = from_list([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1])
    print("\nTree:")
    print_tree(t4)
    print(f"\nPaths summing to 8: {path_sum_count(t4, 8)}")
    print("  Paths: 5→3, 5→2→1, -3→11, 10→5→3→-2→...wait let's enumerate:")
    print("  1) 10 → 5 → 3  (but 10+5+3=18, no)")
    print("  Actually: 5→3, 5→2→1, -3→11 = 3 paths")

    # ── Max Path Sum ──
    print("\n" + "=" * 55)
    print("MAX PATH SUM (ANY TO ANY)")
    print("=" * 55)
    #     -10
    #     / \
    #    9  20
    #      / \
    #     15  7
    t5 = from_list([-10, 9, 20, None, None, 15, 7])
    print("\nTree:")
    print_tree(t5)
    print(f"\nMax path sum: {max_path_sum(t5)}")
    print("  Best path: 15 → 20 → 7 = 42")

    # All negatives
    t5b = from_list([-3, -2, -1])
    print(f"\nAll-negative tree [-3,-2,-1]: max_path_sum = {max_path_sum(t5b)}")
    print("  Best: single node -1")

    # ── Summary ──
    print("\n" + "=" * 55)
    print("KEY TAKEAWAY")
    print("=" * 55)
    print("""
All these problems share ONE skeleton:
    def solve(node):
        left = solve(node.left)
        right = solve(node.right)
        update_global_answer(left, right, node)  # track answer
        return value_for_parent(left, right, node)  # return to parent

The distinction between "what you track" and "what you return" is
the entire insight. Master this pattern and every tree property
problem becomes a fill-in-the-blank exercise.
""")
