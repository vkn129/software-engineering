"""
Day 38: Lowest Common Ancestor (LCA)
======================================
Three approaches to finding the deepest common ancestor of two nodes,
plus a preprocessor for O(log n) repeated queries.

Why LCA matters beyond interviews:
    - git merge-base: finds where branches diverged
    - Filesystems: common ancestor directory for relative paths
    - Networks: highest router that must handle traffic between two hosts
    - Phylogenetics: most recent common ancestor of two species

The core insight: LCA(u, v) is the node where the paths from u and v
to the root first converge. Every approach exploits this differently.
"""

import sys
import os
from collections import deque
from math import log2, ceil
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode, from_list


# ─── ParentTreeNode: TreeNode with parent pointer ───────────────────
#
# The base TreeNode uses __slots__ = ('val', 'left', 'right') for memory
# efficiency. We extend it to add a parent pointer for Approach 1.

class ParentTreeNode:
    """Tree node with parent pointer. Used for LCA with parent approach."""
    __slots__ = ('val', 'left', 'right', 'parent')

    def __init__(self, val, left=None, right=None, parent=None):
        self.val = val
        self.left = left
        self.right = right
        self.parent = parent

    def __repr__(self):
        return f"ParentTreeNode({self.val})"


def build_parent_tree(root: Optional[TreeNode]) -> Optional[ParentTreeNode]:
    """Build a parallel tree with parent pointers from a regular TreeNode tree.

    Returns a dict mapping original node values to ParentTreeNode nodes,
    plus the new root.
    """
    if root is None:
        return None, {}

    node_map = {}  # val -> ParentTreeNode
    new_root = ParentTreeNode(root.val)
    node_map[root.val] = new_root

    queue = deque([(root, new_root)])
    while queue:
        orig, new = queue.popleft()
        if orig.left:
            new_left = ParentTreeNode(orig.left.val, parent=new)
            new.left = new_left
            node_map[orig.left.val] = new_left
            queue.append((orig.left, new_left))
        if orig.right:
            new_right = ParentTreeNode(orig.right.val, parent=new)
            new.right = new_right
            node_map[orig.right.val] = new_right
            queue.append((orig.right, new_right))

    return new_root, node_map


# ─── Approach 1: Parent Pointers ────────────────────────────────────
#
# If each node has a .parent pointer, LCA reduces to "find intersection
# of two linked lists" — the exact same algorithm from Day 21.
#
# Why this works: the path from any node to root IS a linked list.
# Two such paths share a common suffix starting at the LCA.
#
# Time: O(h) where h = height  |  Space: O(1)

def lca_with_parent(p, q):
    """Find LCA when nodes have .parent pointers.

    Algorithm: like finding where two linked lists merge.
    1. Measure depth of both nodes.
    2. Advance the deeper node until both are at the same depth.
    3. Walk both up in lockstep until they meet.

    Why not use a hash set? We could walk p to root, store all ancestors
    in a set, then walk q to root checking membership. That's O(h) space.
    The two-pointer approach uses O(1) space.
    """
    # Measure depths
    def depth(node):
        d = 0
        while node.parent:
            node = node.parent
            d += 1
        return d

    dp, dq = depth(p), depth(q)

    # Advance the deeper node
    while dp > dq:
        p = p.parent
        dp -= 1
    while dq > dp:
        q = q.parent
        dq -= 1

    # Walk in lockstep until they meet
    while p is not q:
        p = p.parent
        q = q.parent

    return p


# ─── Approach 2: Recursive (General Binary Tree) ────────────────────
#
# The elegant O(n) solution that doesn't need parent pointers.
#
# Mental model: ask each node "are p and q in your subtree?"
# If both are in different subtrees → you are the LCA.
# If both are in the same subtree → delegate to that subtree.
#
# Time: O(n)  |  Space: O(h) for recursion stack

def lca_recursive(root: Optional[TreeNode], p: TreeNode, q: TreeNode) -> Optional[TreeNode]:
    """Find LCA by recursive decomposition.

    Base case: None or found one of the targets → return it.
    Recursive case: search left and right subtrees.

    The return value means: "the LCA if both found, or whichever
    target was found, or None if neither found."

    Why this handles the "p is ancestor of q" case:
    When we hit p, we return p immediately without searching deeper.
    q is somewhere in p's subtree, but we never find it separately.
    Since left_result=p and right_result=None, we return p — correct!
    """
    # Base cases
    if root is None:
        return None
    if root is p or root is q:
        return root

    # Recurse into both subtrees
    left_result = lca_recursive(root.left, p, q)
    right_result = lca_recursive(root.right, p, q)

    # If both subtrees returned a result, current node is the LCA
    # (p is in one subtree, q is in the other)
    if left_result and right_result:
        return root

    # Otherwise, return whichever subtree found something
    # (either both targets are in that subtree, or only one was found)
    return left_result if left_result else right_result


# ─── Approach 3: BST Optimization ───────────────────────────────────
#
# In a BST, we don't need to search — the values TELL us which way to go.
# The LCA is the first node whose value is between p.val and q.val
# (the "split point" where the search paths diverge).
#
# Time: O(h)  |  Space: O(1) iterative, O(h) recursive

def lca_bst(root: Optional[TreeNode], p: TreeNode, q: TreeNode) -> Optional[TreeNode]:
    """Find LCA in a BST using value comparisons.

    The BST property guarantees:
        - All values in left subtree < root.val
        - All values in right subtree > root.val

    So if both p.val and q.val < root.val, both are in the left subtree.
    If both > root.val, both are in the right subtree.
    Otherwise, we've found the split point = LCA.

    WARNING: This gives WRONG answers on non-BST trees. The correctness
    depends entirely on the BST ordering invariant.
    """
    current = root
    while current:
        if p.val < current.val and q.val < current.val:
            # Both targets in left subtree
            current = current.left
        elif p.val > current.val and q.val > current.val:
            # Both targets in right subtree
            current = current.right
        else:
            # Split point: p and q are on different sides
            # OR current node IS one of the targets
            return current
    return None


# ─── Approach 4: Binary Lifting (Preprocessing) ─────────────────────
#
# For repeated LCA queries on the same tree, O(n) per query is too slow.
# Binary lifting preprocesses ancestor relationships so each query is O(log n).
#
# Key idea: store "sparse" ancestors at powers of 2.
#   up[v][0] = parent of v
#   up[v][1] = grandparent of v (2^1 above)
#   up[v][2] = great-great-grandparent of v (2^2 above)
#   up[v][j] = ancestor 2^j levels above v
#
# To jump k levels: decompose k in binary, take corresponding jumps.
# Example: jump 13 levels = jump 8 + 4 + 1 (binary: 1101)
#
# Preprocessing: O(n log n) time and space
# Query: O(log n)

class LCAPreprocessor:
    """Preprocess a tree for O(log n) LCA queries using binary lifting.

    Usage:
        tree = from_list([3, 5, 1, 6, 2, 0, 8])
        proc = LCAPreprocessor(tree)
        lca_node = proc.query(node_6, node_2)  # O(log n)

    Why binary lifting works:
    Any integer k can be represented in binary with ceil(log2(k)) bits.
    By precomputing ancestors at power-of-2 distances, we can reach
    ANY ancestor in O(log n) jumps by combining the right powers.

    This is the same "doubling" trick used in:
    - Sparse tables for range minimum queries
    - Fast exponentiation (repeated squaring)
    - Skip lists (probabilistic version)
    """

    def __init__(self, root: Optional[TreeNode]):
        if root is None:
            self.depth = {}
            self.up = {}
            self.LOG = 0
            return

        # Step 1: BFS to compute depths and parent pointers
        # Why BFS? It naturally processes nodes level by level,
        # so parents are always processed before children.
        self.depth = {}
        parent = {}
        self.depth[root] = 0
        parent[root] = root  # root is its own ancestor (sentinel)

        queue = deque([root])
        n = 0
        while queue:
            node = queue.popleft()
            n += 1
            if node.left:
                self.depth[node.left] = self.depth[node] + 1
                parent[node.left] = node
                queue.append(node.left)
            if node.right:
                self.depth[node.right] = self.depth[node] + 1
                parent[node.right] = node
                queue.append(node.right)

        # Step 2: Build sparse ancestor table
        # LOG = max power of 2 we need. For n nodes, max depth is n-1,
        # so we need ceil(log2(n)) bits to represent any depth.
        self.LOG = max(1, ceil(log2(n + 1)))

        # up[node][j] = ancestor of node at distance 2^j
        self.up = {}
        # Initialize: up[node][0] = parent
        for node in self.depth:
            self.up[node] = [None] * self.LOG
            self.up[node][0] = parent[node]

        # Fill using the recurrence: up[v][j] = up[up[v][j-1]][j-1]
        # "To go 2^j up, first go 2^(j-1) up, then 2^(j-1) up again"
        for j in range(1, self.LOG):
            for node in self.depth:
                ancestor = self.up[node][j - 1]
                if ancestor is not None:
                    self.up[node][j] = self.up[ancestor][j - 1]

    def _lift(self, node, k):
        """Lift node up by k levels using binary decomposition.

        Example: lift by 13 = lift by 8, then 4, then 1
        Binary of 13 = 1101, so use jumps at positions 0, 2, 3
        """
        for j in range(self.LOG):
            if k & (1 << j):
                node = self.up[node][j]
        return node

    def query(self, u: TreeNode, v: TreeNode) -> Optional[TreeNode]:
        """Find LCA of u and v in O(log n).

        Algorithm:
        1. Bring both nodes to the same depth (lift the deeper one)
        2. If they're the same node, that's the LCA
        3. Binary search: simultaneously lift both nodes by decreasing
           powers of 2, but ONLY when they don't land on the same node.
           After this, both are one step below the LCA.
        4. Return the parent of either node.
        """
        if u not in self.depth or v not in self.depth:
            return None

        # Step 1: equalize depths
        du, dv = self.depth[u], self.depth[v]
        if du < dv:
            v = self._lift(v, dv - du)
        elif dv < du:
            u = self._lift(u, du - dv)

        # Step 2: same node = LCA
        if u is v:
            return u

        # Step 3: binary search for LCA
        # Try jumps from largest to smallest. If both land on the
        # SAME node, the jump is too big (we'd overshoot the LCA).
        # If they land on DIFFERENT nodes, take the jump.
        for j in range(self.LOG - 1, -1, -1):
            if self.up[u][j] is not self.up[v][j]:
                u = self.up[u][j]
                v = self.up[v][j]

        # Step 4: both are now direct children of the LCA
        return self.up[u][0]


# ─── Helper: Find node by value ─────────────────────────────────────

def find_node(root: Optional[TreeNode], val) -> Optional[TreeNode]:
    """BFS to find a node by value. Returns None if not found.

    Used for testing — in real applications you'd have direct references.
    """
    if root is None:
        return None
    queue = deque([root])
    while queue:
        node = queue.popleft()
        if node.val == val:
            return node
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return None


# ─── Helper: Build parent tree from existing tree ───────────────────
# (build_parent_tree is defined above, near ParentTreeNode)


# ─── Demonstration ──────────────────────────────────────────────────

if __name__ == "__main__":
    # Build example tree:
    #           3
    #          / \
    #         5   1
    #        / \ / \
    #       6  2 0  8
    #         / \
    #        7   4
    tree = from_list([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])

    print("═══ Day 38: Lowest Common Ancestor ═══\n")

    # --- Recursive LCA ---
    print("── Approach 1: Recursive (general binary tree) ──")
    node5 = find_node(tree, 5)
    node1 = find_node(tree, 1)
    node6 = find_node(tree, 6)
    node4 = find_node(tree, 4)
    node2 = find_node(tree, 2)
    node0 = find_node(tree, 0)

    result = lca_recursive(tree, node5, node1)
    print(f"  LCA(5, 1) = {result.val}  (expected 3 — different subtrees)")

    result = lca_recursive(tree, node5, node4)
    print(f"  LCA(5, 4) = {result.val}  (expected 5 — 5 is ancestor of 4)")

    result = lca_recursive(tree, node6, node4)
    print(f"  LCA(6, 4) = {result.val}  (expected 5 — both in left subtree)")

    # --- Parent Pointer LCA ---
    print("\n── Approach 2: Parent pointers ──")
    _, pmap = build_parent_tree(tree)

    result = lca_with_parent(pmap[5], pmap[1])
    print(f"  LCA(5, 1) = {result.val}  (expected 3)")

    result = lca_with_parent(pmap[6], pmap[4])
    print(f"  LCA(6, 4) = {result.val}  (expected 5)")

    # --- BST LCA ---
    print("\n── Approach 3: BST optimization ──")
    #     6
    #    / \
    #   2   8
    #  / \ / \
    # 0  4 7  9
    bst = from_list([6, 2, 8, 0, 4, 7, 9])
    bst_node2 = find_node(bst, 2)
    bst_node8 = find_node(bst, 8)
    bst_node4 = find_node(bst, 4)
    bst_node0 = find_node(bst, 0)

    result = lca_bst(bst, bst_node2, bst_node8)
    print(f"  LCA_BST(2, 8) = {result.val}  (expected 6 — split at root)")

    result = lca_bst(bst, bst_node0, bst_node4)
    print(f"  LCA_BST(0, 4) = {result.val}  (expected 2 — both in left)")

    # --- Binary Lifting ---
    print("\n── Approach 4: Binary lifting (preprocessed) ──")
    proc = LCAPreprocessor(tree)

    result = proc.query(node5, node1)
    print(f"  LCA(5, 1) = {result.val}  (expected 3)")

    result = proc.query(node5, node4)
    print(f"  LCA(5, 4) = {result.val}  (expected 5)")

    result = proc.query(node6, node4)
    print(f"  LCA(6, 4) = {result.val}  (expected 5)")

    result = proc.query(node0, find_node(tree, 8))
    print(f"  LCA(0, 8) = {result.val}  (expected 1)")

    # --- Performance comparison ---
    print("\n── Complexity Summary ──")
    print("  Approach          | Preprocessing | Per Query | Space")
    print("  ─────────────────────────────────────────────────────")
    print("  Parent pointers   | O(n)          | O(h)      | O(n) for pointers")
    print("  Recursive         | None          | O(n)      | O(h) stack")
    print("  BST optimized     | None          | O(h)      | O(h) stack / O(1)")
    print("  Binary lifting    | O(n log n)    | O(log n)  | O(n log n)")

    print("\nAll demonstrations passed!")
