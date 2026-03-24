"""
Day 47: Red-Black Tree — Full Implementation
==============================================
A self-balancing BST that trades perfect balance for cheaper mutations.

Red-black trees guarantee height <= 2*log2(n+1) through five invariants
enforced by recoloring and at most 2 rotations (insert) or 3 rotations
(delete). This is why Java's TreeMap, C++ std::map, and Linux's CFS
scheduler all choose red-black trees over AVL.

The key insight: a red-black tree is a binary encoding of a 2-3-4 tree.
Red nodes are "glued" to their black parent to form multi-key nodes.
The black-height invariant corresponds to all leaves of the 2-3-4 tree
being at the same depth.

Implementation notes:
- We use a sentinel NIL node (not None) to simplify boundary checks.
  Every leaf and the root's parent point to this single sentinel.
- Colors are encoded as constants: RED = True, BLACK = False.
"""

# ─── Color Constants ──────────────────────────────────────────────────

RED = True
BLACK = False


# ─── Node Class ───────────────────────────────────────────────────────

class RBNode:
    """A node in a red-black tree.

    Attributes:
        key:    The value stored (must be comparable).
        color:  RED or BLACK.
        left:   Left child (NIL sentinel if no child).
        right:  Right child (NIL sentinel if no child).
        parent: Parent node (NIL sentinel for root).
    """

    __slots__ = ('key', 'color', 'left', 'right', 'parent')

    def __init__(self, key, color=RED, left=None, right=None, parent=None):
        self.key = key
        self.color = color
        self.left = left
        self.right = right
        self.parent = parent

    def __repr__(self):
        c = "R" if self.color == RED else "B"
        return f"RBNode({self.key}, {c})"


# ─── Red-Black Tree ──────────────────────────────────────────────────

class RedBlackTree:
    """Red-black tree with insert, delete, search, and validation.

    Uses a single NIL sentinel node for all leaves and as the root's
    parent. This eliminates None checks throughout the code — every
    node always has valid left, right, and parent references.
    """

    def __init__(self):
        # Sentinel NIL node — shared by all leaves and root's parent.
        # Its color is BLACK (Property 3: all leaves are black).
        self.NIL = RBNode(key=None, color=BLACK)
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.NIL.parent = self.NIL
        self.root = self.NIL

    # ─── Rotations ────────────────────────────────────────────────

    def _left_rotate(self, x):
        """Left rotation around node x.

        Before:          After:
            x              y
           / \\            / \\
          a   y          x   c
             / \\        / \\
            b   c      a   b

        Preserves BST property. O(1) pointer updates.
        """
        y = x.right
        # Turn y's left subtree into x's right subtree.
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        # Link y's parent to x's parent.
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        # Put x on y's left.
        y.left = x
        x.parent = y

    def _right_rotate(self, y):
        """Right rotation around node y (mirror of left_rotate).

        Before:          After:
            y              x
           / \\            / \\
          x   c          a   y
         / \\                / \\
        a   b              b   c
        """
        x = y.left
        y.left = x.right
        if x.right is not self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is self.NIL:
            self.root = x
        elif y is y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        x.right = y
        y.parent = x

    # ─── Search ───────────────────────────────────────────────────

    def search(self, key):
        """Search for a key. Returns the node if found, NIL otherwise.

        Standard BST search — O(log n) because height is bounded.
        """
        node = self.root
        while node is not self.NIL:
            if key == node.key:
                return node
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return self.NIL

    # ─── Insert ───────────────────────────────────────────────────

    def insert(self, key):
        """Insert a key into the red-black tree.

        Phase 1: Standard BST insert — new node is colored RED.
            Why red? A red node doesn't change black-height on any path,
            so Property 5 is automatically maintained. The only possible
            violation is Property 4 (red parent with red child).

        Phase 2: Fix up — restore Property 4 via recoloring and rotations.
            At most 2 rotations, O(log n) recolorings.
        """
        # Create the new node.
        z = RBNode(key, color=RED, left=self.NIL, right=self.NIL, parent=self.NIL)

        # Phase 1: BST insert — find the correct position.
        y = self.NIL       # trailing parent pointer
        x = self.root      # current node
        while x is not self.NIL:
            y = x
            if z.key < x.key:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y is self.NIL:
            self.root = z           # tree was empty
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z

        # Phase 2: Fix red-red violation.
        self._insert_fixup(z)

    def _insert_fixup(self, z):
        """Restore red-black properties after insertion of z (colored red).

        We loop while z's parent is red (Property 4 violation).
        Three cases, mirrored for left/right:

        Case 1: Uncle is red.
            → Recolor parent and uncle to black, grandparent to red.
            → Move z up to grandparent. Repeat.

        Case 2: Uncle is black, z is inner child.
            → Rotate z's parent to convert to Case 3.

        Case 3: Uncle is black, z is outer child.
            → Rotate grandparent, recolor. Done.
        """
        while z.parent.color == RED:
            if z.parent is z.parent.parent.left:
                # Parent is a LEFT child of grandparent.
                uncle = z.parent.parent.right

                if uncle.color == RED:
                    # Case 1: Uncle is red — recolor.
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent  # move up

                else:
                    # Uncle is black.
                    if z is z.parent.right:
                        # Case 2: z is right child (inner) — left-rotate parent.
                        z = z.parent
                        self._left_rotate(z)
                    # Case 3: z is left child (outer) — right-rotate grandparent.
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._right_rotate(z.parent.parent)
            else:
                # MIRROR: Parent is a RIGHT child of grandparent.
                uncle = z.parent.parent.left

                if uncle.color == RED:
                    # Case 1 (mirror).
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent

                else:
                    if z is z.parent.left:
                        # Case 2 (mirror): z is left child — right-rotate parent.
                        z = z.parent
                        self._right_rotate(z)
                    # Case 3 (mirror): z is right child — left-rotate grandparent.
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._left_rotate(z.parent.parent)

        # Property 2: root must always be black.
        self.root.color = BLACK

    # ─── Delete ───────────────────────────────────────────────────

    def _transplant(self, u, v):
        """Replace subtree rooted at u with subtree rooted at v.

        Updates parent pointers. Does NOT update v's children.
        This is the building block for delete.
        """
        if u.parent is self.NIL:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        # Always update v's parent — even if v is NIL.
        # This is critical: during delete fixup, we need NIL.parent
        # to be correct so we can walk up the tree.
        v.parent = u.parent

    def _minimum(self, node):
        """Return the leftmost (minimum) node in the subtree rooted at node."""
        while node.left is not self.NIL:
            node = node.left
        return node

    def delete(self, key):
        """Delete a key from the red-black tree.

        Phase 1: Find the node z with the given key.
        Phase 2: Standard BST delete with bookkeeping:
            - Track the node y that is actually removed or moved.
            - Track y's original color — if it was BLACK, we need fixup.
            - Track x, the node that takes y's original position.
        Phase 3: If y's original color was BLACK, fix up from x.

        Returns True if the key was found and deleted, False otherwise.
        """
        z = self.search(key)
        if z is self.NIL:
            return False  # key not found

        y = z                       # y = node to be removed or moved
        y_original_color = y.color  # need this to decide if fixup is needed

        if z.left is self.NIL:
            # Case A: z has no left child — replace z with its right child.
            x = z.right
            self._transplant(z, z.right)

        elif z.right is self.NIL:
            # Case B: z has no right child — replace z with its left child.
            x = z.left
            self._transplant(z, z.left)

        else:
            # Case C: z has two children.
            # y = in-order successor (minimum of right subtree).
            y = self._minimum(z.right)
            y_original_color = y.color
            x = y.right  # x takes y's position

            if y.parent is z:
                # y is z's direct right child.
                x.parent = y  # important even if x is NIL
            else:
                # y is deeper in z's right subtree.
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y

            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color  # y takes z's color to maintain properties

        # If the removed/moved node was BLACK, we lost a black node on
        # some path, violating Property 5. Fix it.
        if y_original_color == BLACK:
            self._delete_fixup(x)

        return True

    def _delete_fixup(self, x):
        """Restore red-black properties after deleting a black node.

        x has an "extra blackness" — it counts as double-black.
        We push this extra blackness up or resolve it via rotations.

        Four cases, mirrored for left/right:

        Case 1: Sibling w is RED.
            → Rotate parent toward x, recolor. New sibling is black.
            → Fall into Cases 2-4.

        Case 2: Sibling w is BLACK with two BLACK children.
            → Remove one black from both x and w (recolor w red).
            → Push extra blackness up to parent. Repeat.

        Case 3: Sibling w is BLACK, w's far child is BLACK, near child is RED.
            → Rotate w away from x, recolor. Convert to Case 4.

        Case 4: Sibling w is BLACK, w's far child is RED.
            → Rotate parent toward x, recolor. Done.
        """
        while x is not self.root and x.color == BLACK:
            if x is x.parent.left:
                w = x.parent.right  # sibling

                if w.color == RED:
                    # Case 1: Sibling is red.
                    w.color = BLACK
                    x.parent.color = RED
                    self._left_rotate(x.parent)
                    w = x.parent.right  # new sibling is black

                if w.left.color == BLACK and w.right.color == BLACK:
                    # Case 2: Both of sibling's children are black.
                    w.color = RED
                    x = x.parent  # move extra blackness up

                else:
                    if w.right.color == BLACK:
                        # Case 3: Sibling's far child is black, near child is red.
                        w.left.color = BLACK
                        w.color = RED
                        self._right_rotate(w)
                        w = x.parent.right

                    # Case 4: Sibling's far child is red.
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self._left_rotate(x.parent)
                    x = self.root  # terminate loop

            else:
                # MIRROR: x is a right child.
                w = x.parent.left

                if w.color == RED:
                    # Case 1 (mirror).
                    w.color = BLACK
                    x.parent.color = RED
                    self._right_rotate(x.parent)
                    w = x.parent.left

                if w.right.color == BLACK and w.left.color == BLACK:
                    # Case 2 (mirror).
                    w.color = RED
                    x = x.parent

                else:
                    if w.left.color == BLACK:
                        # Case 3 (mirror).
                        w.right.color = BLACK
                        w.color = RED
                        self._left_rotate(w)
                        w = x.parent.left

                    # Case 4 (mirror).
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self._right_rotate(x.parent)
                    x = self.root

        # x absorbs the extra blackness.
        x.color = BLACK

    # ─── Traversal ────────────────────────────────────────────────

    def inorder(self):
        """Return keys in sorted order via in-order traversal."""
        result = []
        self._inorder_helper(self.root, result)
        return result

    def _inorder_helper(self, node, result):
        if node is not self.NIL:
            self._inorder_helper(node.left, result)
            result.append(node.key)
            self._inorder_helper(node.right, result)

    # ─── Validation ───────────────────────────────────────────────

    def black_height(self, node=None):
        """Compute the black-height of a node.

        Returns the black-height if it is consistent (same on all paths),
        or -1 if the black-height invariant is violated.

        Black-height = number of black nodes on any path from the node
        (exclusive) down to a NIL leaf (inclusive, since NIL is black).
        """
        if node is None:
            node = self.root
        if node is self.NIL:
            return 0

        left_bh = self.black_height(node.left)
        right_bh = self.black_height(node.right)

        if left_bh == -1 or right_bh == -1:
            return -1  # violation below
        if left_bh != right_bh:
            return -1  # Property 5 violated at this node

        # Add 1 if the current node is black (counts toward parent's path).
        return left_bh + (1 if node.color == BLACK else 0)

    def validate_rb_properties(self):
        """Verify all 5 red-black properties hold. Returns (valid, errors).

        Checks:
        1. Every node is red or black.
        2. Root is black.
        3. NIL leaves are black (guaranteed by sentinel).
        4. Red nodes have only black children.
        5. All root-to-NIL paths have equal black-height.
        """
        errors = []

        # Property 2: Root is black.
        if self.root is not self.NIL and self.root.color != BLACK:
            errors.append("Property 2 violated: root is red")

        # Property 3: NIL is black (sanity check on sentinel).
        if self.NIL.color != BLACK:
            errors.append("Property 3 violated: NIL sentinel is not black")

        # Walk the tree checking Properties 1, 4, and 5.
        def check(node):
            if node is self.NIL:
                return

            # Property 1: node color is valid.
            if node.color not in (RED, BLACK):
                errors.append(f"Property 1 violated: node {node.key} has invalid color")

            # Property 4: red node must have black children.
            if node.color == RED:
                if node.left.color != BLACK:
                    errors.append(
                        f"Property 4 violated: red node {node.key} "
                        f"has red left child {node.left.key}"
                    )
                if node.right.color != BLACK:
                    errors.append(
                        f"Property 4 violated: red node {node.key} "
                        f"has red right child {node.right.key}"
                    )

            check(node.left)
            check(node.right)

        check(self.root)

        # Property 5: consistent black-height.
        bh = self.black_height()
        if bh == -1:
            errors.append("Property 5 violated: inconsistent black-height across paths")

        return (len(errors) == 0, errors)

    # ─── Display ──────────────────────────────────────────────────

    def display(self, node=None, prefix="", is_left=True):
        """Print the tree structure with colors for debugging."""
        if node is None:
            node = self.root
        if node is self.NIL:
            return

        connector = "├── " if is_left else "└── "
        extension = "│   " if is_left else "    "

        # Print right subtree first (so it appears on top visually).
        if node.right is not self.NIL:
            self.display(node.right, prefix + (extension if node is not self.root else "    "), False)

        if node is self.root:
            print(f"{'R' if node.color == RED else 'B'}:{node.key}")
        else:
            print(f"{prefix}{connector}{'R' if node.color == RED else 'B'}:{node.key}")

        if node.left is not self.NIL:
            self.display(node.left, prefix + (extension if node is not self.root else "    "), True)


# ─── Demo ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Red-Black Tree — Demonstration")
    print("=" * 60)

    tree = RedBlackTree()

    # Insert sequence that triggers all fixup cases.
    keys = [10, 20, 30, 15, 25, 5, 1, 8, 12, 18, 22, 28, 35, 40, 3]
    print(f"\nInserting keys: {keys}\n")

    for key in keys:
        tree.insert(key)
        valid, errs = tree.validate_rb_properties()
        status = "VALID" if valid else f"INVALID: {errs}"
        color = "R" if tree.search(key).color == RED else "B"
        print(f"  Insert {key:2d} → color={color}  tree={status}")

    print(f"\nIn-order traversal (should be sorted): {tree.inorder()}")
    print(f"Black-height of root: {tree.black_height()}")

    print("\nTree structure:")
    tree.display()

    # Validate all properties.
    print("\n" + "-" * 60)
    valid, errors = tree.validate_rb_properties()
    print(f"All 5 RB properties valid: {valid}")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")

    # Delete some keys and re-validate.
    print("\n" + "-" * 60)
    delete_keys = [20, 10, 35, 1, 30]
    print(f"Deleting keys: {delete_keys}\n")

    for key in delete_keys:
        result = tree.delete(key)
        valid, errs = tree.validate_rb_properties()
        status = "VALID" if valid else f"INVALID: {errs}"
        print(f"  Delete {key:2d} → found={result}  tree={status}")

    print(f"\nIn-order after deletes: {tree.inorder()}")
    print(f"Black-height of root: {tree.black_height()}")

    print("\nTree structure after deletes:")
    tree.display()

    # Final validation.
    print("\n" + "-" * 60)
    valid, errors = tree.validate_rb_properties()
    print(f"Final validation — all 5 RB properties valid: {valid}")

    # Demonstrate search.
    print("\n" + "-" * 60)
    for key in [15, 99, 5, 40]:
        node = tree.search(key)
        if node is not tree.NIL:
            color = "RED" if node.color == RED else "BLACK"
            print(f"  Search {key:2d} → found, color={color}")
        else:
            print(f"  Search {key:2d} → not found")

    print()
