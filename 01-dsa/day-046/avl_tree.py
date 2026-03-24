"""
Day 46: AVL Tree — Full Implementation

A self-balancing binary search tree where the height difference between
left and right subtrees of any node is at most 1. Invented by Adelson-Velsky
and Landis in 1962 — the first self-balancing BST.

Key idea: after every insert/delete, walk back up the tree updating heights
and rebalancing any node whose balance factor reaches +2 or -2. Rebalancing
uses rotations — local restructuring operations that fix the height imbalance
without violating the BST ordering invariant.
"""


class AVLNode:
    """A node in the AVL tree.

    Stores value, left/right children, and height.
    Height of a leaf is 0; height of None is -1.
    """
    __slots__ = ('val', 'left', 'right', 'height')

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 0  # leaf node starts at height 0

    def __repr__(self):
        return f"AVLNode({self.val})"


class AVLTree:
    """AVL Tree with insert, delete, search, and traversal operations.

    All operations are O(log n) guaranteed because the tree maintains
    the AVL balance invariant: |height(left) - height(right)| <= 1
    for every node.
    """

    def __init__(self):
        self.root = None

    # ------------------------------------------------------------------
    # Height and balance utilities
    # ------------------------------------------------------------------

    def _height(self, node):
        """Return the height of a node. None has height -1."""
        if node is None:
            return -1
        return node.height

    def _update_height(self, node):
        """Recalculate a node's height from its children.

        Must be called after any structural change (rotation, insert, delete).
        Always update the lower node first — the node that moved down in a
        rotation must have its height updated before the node that moved up.
        """
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _get_balance(self, node):
        """Return the balance factor: height(left) - height(right).

        Legal values in a balanced AVL tree: -1, 0, +1.
        A value of +2 means left-heavy; -2 means right-heavy.
        """
        if node is None:
            return 0
        return self._height(node.left) - self._height(node.right)

    # ------------------------------------------------------------------
    # Rotations
    # ------------------------------------------------------------------

    def _right_rotate(self, z):
        """Perform a right rotation at node z.

              z                 y
             / \\              / \\
            y   T4   =>      x   z
           / \\              / \\ / \\
          x   T3           T1 T2 T3 T4
         / \\
        T1  T2

        Returns the new root of this subtree (y).
        CRITICAL: update z's height first (it moved down), then y's.
        """
        y = z.left
        t3 = y.right

        # Perform rotation
        y.right = z
        z.left = t3

        # Update heights — z first (child), then y (new parent)
        self._update_height(z)
        self._update_height(y)

        return y

    def _left_rotate(self, z):
        """Perform a left rotation at node z.

            z                   y
           / \\                / \\
          T1   y     =>      z   x
              / \\          / \\ / \\
             T2  x        T1 T2 T3 T4
                / \\
               T3  T4

        Returns the new root of this subtree (y).
        """
        y = z.right
        t2 = y.left

        # Perform rotation
        y.left = z
        z.right = t2

        # Update heights — z first (child), then y (new parent)
        self._update_height(z)
        self._update_height(y)

        return y

    # ------------------------------------------------------------------
    # Rebalance
    # ------------------------------------------------------------------

    def _rebalance(self, node):
        """Check balance factor and apply the appropriate rotation(s).

        Four cases:
        1. LL (balance +2, left child balance >= 0): right rotate
        2. LR (balance +2, left child balance < 0): left rotate left child, then right rotate
        3. RR (balance -2, right child balance <= 0): left rotate
        4. RL (balance -2, right child balance > 0): right rotate right child, then left rotate

        Returns the (possibly new) root of this subtree.
        """
        balance = self._get_balance(node)

        # Left-heavy
        if balance > 1:
            if self._get_balance(node.left) < 0:
                # LR case: left child is right-heavy
                node.left = self._left_rotate(node.left)
            # LL case (or LR after first rotation)
            return self._right_rotate(node)

        # Right-heavy
        if balance < -1:
            if self._get_balance(node.right) > 0:
                # RL case: right child is left-heavy
                node.right = self._right_rotate(node.right)
            # RR case (or RL after first rotation)
            return self._left_rotate(node)

        return node

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert(self, val):
        """Insert a value into the AVL tree. Duplicates are ignored."""
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        """Recursive insert that rebalances on the way back up.

        1. Standard BST insert (recurse left or right).
        2. Update this node's height.
        3. Rebalance if needed.
        """
        # Base case: found the insertion point
        if node is None:
            return AVLNode(val)

        # Standard BST insert
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        else:
            # Duplicate — do not insert
            return node

        # Update height of this ancestor node
        self._update_height(node)

        # Rebalance if this node became unbalanced
        return self._rebalance(node)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(self, val):
        """Delete a value from the AVL tree. No-op if not found."""
        self.root = self._delete(self.root, val)

    def _delete(self, node, val):
        """Recursive delete with rebalancing on the way back up.

        Unlike insertion (which causes at most one rebalance point),
        deletion can cause imbalances all the way up to the root.
        The recursive approach handles this naturally — every ancestor
        gets rebalanced as the recursion unwinds.
        """
        if node is None:
            return None

        # Standard BST delete — find the node
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            # Found the node to delete
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Node has two children: replace with inorder successor
                # (smallest value in right subtree)
                successor = self._find_min(node.right)
                node.val = successor.val
                node.right = self._delete(node.right, successor.val)

        # Update height
        self._update_height(node)

        # Rebalance — deletion can cascade imbalances up the tree
        return self._rebalance(node)

    def _find_min(self, node):
        """Find the node with the minimum value in a subtree."""
        while node.left is not None:
            node = node.left
        return node

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, val):
        """Search for a value. Returns True if found, False otherwise.

        O(log n) guaranteed because AVL height is at most ~1.44 * log2(n).
        """
        return self._search(self.root, val)

    def _search(self, node, val):
        if node is None:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._search(node.left, val)
        else:
            return self._search(node.right, val)

    # ------------------------------------------------------------------
    # Traversals
    # ------------------------------------------------------------------

    def inorder(self):
        """Return values in sorted order (left, root, right).

        If the AVL tree is correct, this always produces a sorted list.
        """
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node is not None:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

    def preorder(self):
        """Return values in preorder (root, left, right).

        Useful for verifying tree structure — preorder uniquely
        identifies a BST's shape.
        """
        result = []
        self._preorder(self.root, result)
        return result

    def _preorder(self, node, result):
        if node is not None:
            result.append(node.val)
            self._preorder(node.left, result)
            self._preorder(node.right, result)

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def visualize(self):
        """Print the tree showing each node's value and balance factor.

        Format: value(bf) where bf is the balance factor.
        Indentation shows depth; right children are printed above left.
        """
        if self.root is None:
            print("<empty tree>")
            return
        lines = []
        self._build_visual(self.root, "", True, lines)
        print("\n".join(lines))

    def _build_visual(self, node, prefix, is_last, lines):
        """Recursively build a visual representation of the tree.

        Prints right subtree first (top of output), then current node,
        then left subtree (bottom of output). This gives a sideways
        tree view that reads naturally.
        """
        if node is None:
            return

        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        # Print right child first (appears above in output)
        if node.right is not None:
            self._build_visual(
                node.right,
                prefix + extension,
                False if node.left is not None else True,
                lines,
            )

        # Print current node with balance factor
        bf = self._get_balance(node)
        bf_str = f"+{bf}" if bf > 0 else str(bf)
        lines.append(f"{prefix}{connector}{node.val}(bf={bf_str})")

        # Print left child (appears below in output)
        if node.left is not None:
            self._build_visual(node.left, prefix + extension, True, lines)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def is_valid_avl(self):
        """Verify the tree satisfies both BST and AVL invariants.

        Returns True if:
        1. BST property holds (inorder traversal is strictly increasing).
        2. Every node's balance factor is in {-1, 0, +1}.
        3. Every node's stored height is correct.
        """
        # Check BST property
        values = self.inorder()
        for i in range(1, len(values)):
            if values[i] <= values[i - 1]:
                return False

        # Check AVL invariant and height correctness
        return self._check_avl(self.root)

    def _check_avl(self, node):
        if node is None:
            return True

        # Check height is correct
        expected_height = 1 + max(self._height(node.left), self._height(node.right))
        if node.height != expected_height:
            return False

        # Check balance factor
        if abs(self._get_balance(node)) > 1:
            return False

        return self._check_avl(node.left) and self._check_avl(node.right)

    def __len__(self):
        return self._count(self.root)

    def _count(self, node):
        if node is None:
            return 0
        return 1 + self._count(node.left) + self._count(node.right)


# ======================================================================
# Demo
# ======================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("AVL Tree Demo")
    print("=" * 60)

    tree = AVLTree()

    # Insert sorted values — this would destroy a plain BST
    # but the AVL tree stays balanced via rotations
    print("\n--- Inserting 1 through 15 in order ---")
    print("(A plain BST would degenerate into a linked list)")
    print()
    for i in range(1, 16):
        tree.insert(i)

    tree.visualize()

    print(f"\nTree size: {len(tree)}")
    print(f"Root value: {tree.root.val}")
    print(f"Tree height: {tree.root.height}")
    print(f"Inorder (should be sorted): {tree.inorder()}")
    print(f"Valid AVL? {tree.is_valid_avl()}")

    # Demonstrate search
    print("\n--- Search ---")
    for val in [1, 8, 15, 16]:
        print(f"  search({val}): {tree.search(val)}")

    # Demonstrate deletion with rebalancing
    print("\n--- Deleting 1, 5, 10 ---")
    for val in [1, 5, 10]:
        tree.delete(val)
        print(f"\nAfter deleting {val}:")
        tree.visualize()
        print(f"Valid AVL? {tree.is_valid_avl()}")

    print(f"\nFinal inorder: {tree.inorder()}")
    print(f"Final size: {len(tree)}")

    # Show that worst-case sorted insertion still gives O(log n) height
    print("\n--- Stress test: insert 1 to 1000 in order ---")
    big_tree = AVLTree()
    for i in range(1, 1001):
        big_tree.insert(i)
    print(f"Nodes: {len(big_tree)}")
    print(f"Height: {big_tree.root.height}")
    print(f"Theoretical max AVL height for n=1000: ~14.4 (1.44 * log2(1000))")
    print(f"Valid AVL? {big_tree.is_valid_avl()}")
