"""
Day 43: Binary Search Tree Operations
=======================================
Full BST implementation: insert, search, delete, min, max,
successor, predecessor, floor, ceil, rank, select, range_query.

The BST invariant:
    For every node: all keys in left subtree < node.val < all keys in right subtree

This single rule gives sorted iteration (inorder traversal), O(h) search
(binary search on a tree), and efficient range queries. The catch: h can be
O(n) if the tree degrades to a linked list. Self-balancing trees (Days 46-48)
fix this.

We reuse TreeNode from Day 36 — a BST is just a binary tree with the
ordering invariant enforced on every insertion.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode


class BST:
    """
    Binary Search Tree with order-statistic support.

    Each node stores a value (the key) and a size field (number of nodes
    in its subtree, including itself). The size field enables O(h) rank
    and select operations.

    Duplicates are not allowed — inserting an existing key is a no-op.
    This mirrors the semantics of a sorted set.
    """

    def __init__(self):
        self.root = None

    # ─── Size Tracking ───────────────────────────────────────────────
    # We augment TreeNode with a _size attribute for rank/select.
    # This is the standard "order-statistic tree" augmentation.

    @staticmethod
    def _size(node):
        """Return subtree size. None nodes have size 0."""
        if node is None:
            return 0
        return getattr(node, '_size', 1)

    @staticmethod
    def _update_size(node):
        """Recompute size from children. Call after any structural change."""
        if node is not None:
            node._size = 1 + BST._size(node.left) + BST._size(node.right)

    # ─── Insert ──────────────────────────────────────────────────────
    # Walk down the tree following the BST invariant.
    # New keys always become leaf nodes.
    # Time: O(h) where h = height.

    def insert(self, key):
        """Insert a key into the BST. Duplicates are ignored."""
        self.root = self._insert(self.root, key)

    def _insert(self, node, key):
        """Recursive insert. Returns the (possibly new) root of the subtree."""
        if node is None:
            new_node = TreeNode(key)
            new_node._size = 1
            return new_node

        if key < node.val:
            node.left = self._insert(node.left, key)
        elif key > node.val:
            node.right = self._insert(node.right, key)
        # key == node.val: duplicate, do nothing

        self._update_size(node)
        return node

    # ─── Search ──────────────────────────────────────────────────────
    # Binary search on a tree: go left if key < node, right if key > node.
    # Time: O(h).

    def search(self, key):
        """Return the node with the given key, or None if not found."""
        return self._search(self.root, key)

    def _search(self, node, key):
        if node is None:
            return None
        if key == node.val:
            return node
        elif key < node.val:
            return self._search(node.left, key)
        else:
            return self._search(node.right, key)

    def __contains__(self, key):
        """Support 'key in bst' syntax."""
        return self.search(key) is not None

    # ─── Min / Max ───────────────────────────────────────────────────
    # Min = leftmost node (keep going left until you can't).
    # Max = rightmost node (keep going right until you can't).
    # Time: O(h).

    def min(self):
        """Return the minimum key, or None if tree is empty."""
        if self.root is None:
            return None
        return self._min_node(self.root).val

    def _min_node(self, node):
        """Return the leftmost node in the subtree rooted at node."""
        while node.left is not None:
            node = node.left
        return node

    def max(self):
        """Return the maximum key, or None if tree is empty."""
        if self.root is None:
            return None
        return self._max_node(self.root).val

    def _max_node(self, node):
        """Return the rightmost node in the subtree rooted at node."""
        while node.right is not None:
            node = node.right
        return node

    # ─── Delete ──────────────────────────────────────────────────────
    # Three cases:
    #   1. Leaf: just remove it
    #   2. One child: replace node with that child
    #   3. Two children: replace value with inorder successor, then
    #      delete the successor (which has at most one child)
    #
    # Why inorder successor? It's the smallest value in the right subtree —
    # swapping it in preserves the BST invariant for both subtrees.
    # Time: O(h).

    def delete(self, key):
        """Delete a key from the BST. No-op if key doesn't exist."""
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        """Recursive delete. Returns the (possibly new) root of the subtree."""
        if node is None:
            return None  # key not found

        if key < node.val:
            node.left = self._delete(node.left, key)
        elif key > node.val:
            node.right = self._delete(node.right, key)
        else:
            # Found the node to delete
            # Case 1 & 2: zero or one child
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left

            # Case 3: two children
            # Find inorder successor (smallest in right subtree)
            successor = self._min_node(node.right)
            # Copy successor's value into this node
            node.val = successor.val
            # Delete the successor from the right subtree
            node.right = self._delete(node.right, successor.val)

        self._update_size(node)
        return node

    # ─── Successor / Predecessor ─────────────────────────────────────
    # Successor(key): smallest key strictly greater than key.
    # Predecessor(key): largest key strictly less than key.
    #
    # These don't require the key to exist in the tree — they find the
    # nearest greater/lesser value regardless.
    # Time: O(h).

    def successor(self, key):
        """Return the smallest key strictly greater than key, or None."""
        result = self._successor(self.root, key)
        return result

    def _successor(self, node, key):
        """
        Walk down the tree tracking the best candidate.

        When we go LEFT (key < node), the current node COULD be the successor,
        so we record it. When we go RIGHT (key >= node), the successor must
        be in the right subtree (current node is too small).
        """
        candidate = None
        while node is not None:
            if key < node.val:
                candidate = node.val  # this node might be the successor
                node = node.left      # look for something smaller
            else:
                node = node.right     # need something bigger
        return candidate

    def predecessor(self, key):
        """Return the largest key strictly less than key, or None."""
        return self._predecessor(self.root, key)

    def _predecessor(self, node, key):
        """
        Mirror of successor: track candidate when going RIGHT.

        When we go RIGHT (key > node), the current node COULD be the predecessor.
        When we go LEFT (key <= node), the predecessor must be in the left subtree.
        """
        candidate = None
        while node is not None:
            if key > node.val:
                candidate = node.val  # this node might be the predecessor
                node = node.right     # look for something bigger
            else:
                node = node.left      # need something smaller
        return candidate

    # ─── Floor / Ceil ────────────────────────────────────────────────
    # Floor(key): largest key in BST that is <= key.
    # Ceil(key): smallest key in BST that is >= key.
    #
    # Unlike successor/predecessor, these INCLUDE the key itself if present.
    # Time: O(h).

    def floor(self, key):
        """Return the largest key <= key, or None if no such key exists."""
        return self._floor(self.root, key)

    def _floor(self, node, key):
        """
        If key == node: floor is node itself.
        If key < node: floor must be in left subtree.
        If key > node: floor is either in right subtree, or node itself
                       (if right subtree has nothing <= key).
        """
        if node is None:
            return None
        if key == node.val:
            return node.val
        if key < node.val:
            return self._floor(node.left, key)
        # key > node.val: try right subtree, fall back to current node
        right_floor = self._floor(node.right, key)
        return right_floor if right_floor is not None else node.val

    def ceil(self, key):
        """Return the smallest key >= key, or None if no such key exists."""
        return self._ceil(self.root, key)

    def _ceil(self, node, key):
        """
        Mirror of floor:
        If key == node: ceil is node itself.
        If key > node: ceil must be in right subtree.
        If key < node: ceil is either in left subtree, or node itself.
        """
        if node is None:
            return None
        if key == node.val:
            return node.val
        if key > node.val:
            return self._ceil(node.right, key)
        # key < node.val: try left subtree, fall back to current node
        left_ceil = self._ceil(node.left, key)
        return left_ceil if left_ceil is not None else node.val

    # ─── Rank ────────────────────────────────────────────────────────
    # rank(key): how many keys in the BST are strictly less than key.
    # Uses the _size augmentation on each node.
    # Time: O(h).

    def rank(self, key):
        """Return the number of keys strictly less than key."""
        return self._rank(self.root, key)

    def _rank(self, node, key):
        """
        If key == node: rank = size of left subtree (everything left is smaller).
        If key < node: rank is entirely determined by left subtree.
        If key > node: rank = left_size + 1 (current node) + rank in right subtree.
        """
        if node is None:
            return 0
        if key < node.val:
            return self._rank(node.left, key)
        elif key > node.val:
            return 1 + self._size(node.left) + self._rank(node.right, key)
        else:
            return self._size(node.left)

    # ─── Select ──────────────────────────────────────────────────────
    # select(k): find the kth smallest key (0-indexed).
    # Time: O(h).

    def select(self, k):
        """Return the kth smallest key (0-indexed), or None if k is out of range."""
        if k < 0 or k >= self._size(self.root):
            return None
        node = self._select(self.root, k)
        return node.val if node else None

    def _select(self, node, k):
        """
        Left subtree has left_size elements, all smaller than current node.
        If k < left_size: answer is in left subtree.
        If k == left_size: current node is the answer (it has exactly k smaller keys).
        If k > left_size: answer is in right subtree with adjusted k.
        """
        if node is None:
            return None
        left_size = self._size(node.left)
        if k < left_size:
            return self._select(node.left, k)
        elif k == left_size:
            return node
        else:
            return self._select(node.right, k - left_size - 1)

    # ─── Range Query ─────────────────────────────────────────────────
    # Collect all keys in [lo, hi] using a pruned inorder traversal.
    # Prune left subtree if node.val <= lo (nothing smaller can be in range).
    # Prune right subtree if node.val >= hi (nothing larger can be in range).
    # Time: O(h + k) where k = number of keys in range.

    def range_query(self, lo, hi):
        """Return a sorted list of all keys in [lo, hi] inclusive."""
        result = []
        self._range_query(self.root, lo, hi, result)
        return result

    def _range_query(self, node, lo, hi, result):
        """Pruned inorder traversal collecting keys in [lo, hi]."""
        if node is None:
            return

        # Only go left if there might be keys >= lo in the left subtree
        if node.val > lo:
            self._range_query(node.left, lo, hi, result)

        # Include current node if in range
        if lo <= node.val <= hi:
            result.append(node.val)

        # Only go right if there might be keys <= hi in the right subtree
        if node.val < hi:
            self._range_query(node.right, lo, hi, result)

    # ─── Inorder Traversal ───────────────────────────────────────────
    # Returns all keys in sorted order. Time: O(n).

    def inorder(self):
        """Return all keys in sorted (ascending) order."""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is None:
            return
        self._inorder(node.left, result)
        result.append(node.val)
        self._inorder(node.right, result)

    # ─── Utility ─────────────────────────────────────────────────────

    def __len__(self):
        return self._size(self.root)

    def is_empty(self):
        return self.root is None

    def __repr__(self):
        return f"BST({self.inorder()})"


# ─── Visual Printing ────────────────────────────────────────────────

def print_bst(node, prefix="", is_left=True):
    """Visual tree printing for debugging."""
    if node is None:
        return
    print_bst(node.right, prefix + ("│   " if is_left else "    "), False)
    connector = "└── " if is_left else "┌── "
    print(f"{prefix}{connector}{node.val}")
    print_bst(node.left, prefix + ("    " if is_left else "│   "), True)


# ─── Demonstration ──────────────────────────────────────────────────

if __name__ == "__main__":
    bst = BST()

    # Insert keys in a non-sorted order to get a reasonably balanced tree
    #
    #          8
    #        /   \
    #       3     10
    #      / \      \
    #     1   5      14
    #        / \    /
    #       4   7  13

    for key in [8, 3, 10, 1, 5, 14, 4, 7, 13]:
        bst.insert(key)

    print("BST structure:")
    print_bst(bst.root)
    print()

    print("─── Basic Operations ──────────────────────────")
    print(f"Inorder (sorted): {bst.inorder()}")
    print(f"Size: {len(bst)}")
    print(f"Min: {bst.min()}")
    print(f"Max: {bst.max()}")
    print()

    print("─── Search ────────────────────────────────────")
    print(f"Search 5:  {bst.search(5)}")
    print(f"Search 99: {bst.search(99)}")
    print(f"5 in bst:  {5 in bst}")
    print(f"99 in bst: {99 in bst}")
    print()

    print("─── Successor / Predecessor ───────────────────")
    for key in [1, 5, 8, 13, 14]:
        print(f"  successor({key:2d}) = {bst.successor(key)}, "
              f"predecessor({key:2d}) = {bst.predecessor(key)}")
    print()

    print("─── Floor / Ceil ──────────────────────────────")
    for key in [0, 1, 2, 5, 6, 8, 14, 15]:
        print(f"  floor({key:2d}) = {bst.floor(key)}, ceil({key:2d}) = {bst.ceil(key)}")
    print()

    print("─── Rank / Select ─────────────────────────────")
    for key in [1, 3, 5, 8, 10, 14]:
        print(f"  rank({key:2d}) = {bst.rank(key)}")
    for k in range(len(bst)):
        print(f"  select({k}) = {bst.select(k)}")
    print()

    print("─── Range Query ───────────────────────────────")
    print(f"  range_query(3, 10) = {bst.range_query(3, 10)}")
    print(f"  range_query(5, 14) = {bst.range_query(5, 14)}")
    print(f"  range_query(0, 2)  = {bst.range_query(0, 2)}")
    print(f"  range_query(6, 9)  = {bst.range_query(6, 9)}")
    print()

    print("─── Deletion ──────────────────────────────────")
    # Case 1: delete leaf (7)
    print("Delete 7 (leaf):")
    bst.delete(7)
    print(f"  Inorder: {bst.inorder()}")

    # Case 2: delete node with one child (10 → only child 14)
    print("Delete 10 (one child):")
    bst.delete(10)
    print(f"  Inorder: {bst.inorder()}")

    # Case 3: delete node with two children (3)
    print("Delete 3 (two children — replaced by successor 4):")
    bst.delete(3)
    print(f"  Inorder: {bst.inorder()}")

    print("\nFinal tree:")
    print_bst(bst.root)

    # Verify BST invariant by checking inorder is sorted
    keys = bst.inorder()
    assert keys == sorted(keys), "BST invariant violated!"
    assert len(bst) == len(keys), "Size tracking broken!"
    print("\nBST invariant: VERIFIED")
    print(f"Size tracking: VERIFIED ({len(bst)} nodes)")

    # Demonstrate worst case: sorted insertion
    print("\n─── Worst Case: Sorted Insertion ───────────────")
    degenerate = BST()
    for key in [1, 2, 3, 4, 5]:
        degenerate.insert(key)
    print("Inserting [1, 2, 3, 4, 5] produces a linked list:")
    print_bst(degenerate.root)
    print(f"Height is {4} for {len(degenerate)} nodes — O(n), not O(log n)")
