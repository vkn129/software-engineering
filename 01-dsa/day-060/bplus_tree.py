"""
Day 60: B+ Tree — Data Only in Leaves, Leaves Linked Together
==============================================================
Internal nodes are pure routing: keys act as separators/fences.
Leaf nodes hold all the actual (key, value) data and form a linked list.

Range query: find the starting leaf in O(log n), then walk the leaf
chain in O(k) — no backtracking up the tree.

This is how MySQL InnoDB, PostgreSQL, SQLite, and virtually every
relational database implements its indexes.

Run: python bplus_tree.py
"""


# ─── Node Classes ──────────────────────────────────────────────────

class BPlusLeaf:
    """Leaf node: holds actual key-value data. Linked to next leaf."""
    __slots__ = ('keys', 'values', 'next_leaf', 'parent')

    def __init__(self):
        self.keys = []       # Sorted keys
        self.values = []     # Corresponding values (same index)
        self.next_leaf = None  # Pointer to right sibling leaf
        self.parent = None

    def is_leaf(self):
        return True

    def is_full(self, order):
        """A leaf is full when it has `order` keys (max capacity)."""
        return len(self.keys) >= order


class BPlusInternal:
    """Internal node: routing only. Keys are separator/fence keys."""
    __slots__ = ('keys', 'children', 'parent')

    def __init__(self):
        self.keys = []       # Separator keys
        self.children = []   # Child pointers (len = len(keys) + 1)
        self.parent = None

    def is_leaf(self):
        return False

    def is_full(self, order):
        """An internal node is full when it has `order` keys."""
        return len(self.keys) >= order


# ─── B+ Tree ──────────────────────────────────────────────────────

class BPlusTree:
    """
    B+ tree of given order (max keys per node).

    Invariants:
    - All data lives in leaf nodes.
    - Leaf nodes form a singly linked list (left to right).
    - Internal nodes contain only separator keys for routing.
    - For internal node with keys [k0, k1, ...]:
      children[i] contains keys < keys[i]
      children[i+1] contains keys >= keys[i]
    """

    def __init__(self, order=4):
        """
        order: maximum number of keys per node.
        A node splits when it reaches `order` keys.
        """
        if order < 3:
            raise ValueError("Order must be >= 3 for B+ tree to work")
        self.order = order
        self.root = BPlusLeaf()  # Start with an empty leaf as root

    # ── Public API ───────────────────────────────────────────────

    def search(self, key):
        """Find value for key, or None if not present. O(log n)."""
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None

    def insert(self, key, value):
        """
        Insert (key, value) into the tree.
        If key exists, update its value.
        Splits nodes as needed to maintain balance.
        """
        leaf = self._find_leaf(key)

        # Check if key already exists — update in place
        for i, k in enumerate(leaf.keys):
            if k == key:
                leaf.values[i] = value
                return

        # Find insertion position to maintain sorted order
        pos = 0
        while pos < len(leaf.keys) and leaf.keys[pos] < key:
            pos += 1
        leaf.keys.insert(pos, key)
        leaf.values.insert(pos, value)

        # Split if the leaf is overfull
        if leaf.is_full(self.order):
            self._split_leaf(leaf)

    def range_query(self, lo, hi):
        """
        Return all (key, value) pairs where lo <= key <= hi.
        O(log n) to find starting leaf, then O(k) along the leaf chain.
        This is the operation that justifies B+ trees over B-trees.
        """
        results = []
        leaf = self._find_leaf(lo)

        # Walk the leaf chain
        while leaf is not None:
            for i, k in enumerate(leaf.keys):
                if k > hi:
                    return results
                if k >= lo:
                    results.append((k, leaf.values[i]))
            leaf = leaf.next_leaf

        return results

    def traverse(self):
        """
        Walk the entire leaf chain to get all key-value pairs in order.
        O(n) — pure sequential scan, no tree navigation needed.
        """
        result = []
        # Find the leftmost leaf
        node = self.root
        while not node.is_leaf():
            node = node.children[0]

        # Walk the chain
        while node is not None:
            for i, k in enumerate(node.keys):
                result.append((k, node.values[i]))
            node = node.next_leaf

        return result

    def visualize(self, node=None, indent=0, prefix="ROOT"):
        """Print tree structure, distinguishing internal vs leaf nodes."""
        if node is None:
            node = self.root
            print()
            print("B+ Tree Visualization (order={})".format(self.order))
            print("=" * 50)

        spacer = "    " * indent

        if node.is_leaf():
            link = " -> [...]" if node.next_leaf else " -> NULL"
            print(f"{spacer}{prefix} LEAF {node.keys}{link}")
        else:
            print(f"{spacer}{prefix} INTERNAL {node.keys}")
            for i, child in enumerate(node.children):
                if i == 0:
                    child_prefix = f"<{node.keys[0]}:"
                elif i == len(node.keys):
                    child_prefix = f">={node.keys[-1]}:"
                else:
                    child_prefix = f"[{node.keys[i-1]},{node.keys[i]}):"
                self.visualize(child, indent + 1, child_prefix)

    # ── Internal Helpers ─────────────────────────────────────────

    def _find_leaf(self, key):
        """
        Navigate from root to the leaf that should contain `key`.
        At each internal node, find the child pointer to follow.
        O(log n) — one comparison per level.
        """
        node = self.root
        while not node.is_leaf():
            # Find the correct child to descend into
            # children[i] covers keys where keys[i-1] <= k < keys[i]
            found = False
            for i, separator in enumerate(node.keys):
                if key < separator:
                    node = node.children[i]
                    found = True
                    break
            if not found:
                # Key is >= all separators, go to rightmost child
                node = node.children[-1]
        return node

    def _split_leaf(self, leaf):
        """
        Split a full leaf into two leaves.
        The first key of the right leaf is COPIED UP to the parent
        as a separator key. (Copy, not move — the key stays in the leaf
        because leaf keys are actual data.)
        """
        mid = len(leaf.keys) // 2

        # Create new right leaf
        new_leaf = BPlusLeaf()
        new_leaf.keys = leaf.keys[mid:]
        new_leaf.values = leaf.values[mid:]

        # Truncate old leaf to left half
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        # Maintain the leaf chain
        new_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = new_leaf

        # The separator to promote is the first key of the new (right) leaf
        # This is a COPY — the key remains in the leaf as data
        separator = new_leaf.keys[0]

        # Insert separator into parent
        self._insert_into_parent(leaf, separator, new_leaf)

    def _split_internal(self, node):
        """
        Split a full internal node.
        The middle key is PUSHED UP to the parent (not copied — internal
        keys are just separators, so the middle key moves out of this node
        entirely).
        """
        mid = len(node.keys) // 2
        push_up_key = node.keys[mid]

        # Create new right internal node
        new_node = BPlusInternal()
        new_node.keys = node.keys[mid + 1:]       # Keys after the middle
        new_node.children = node.children[mid + 1:]  # Corresponding children

        # Update parent pointers for moved children
        for child in new_node.children:
            child.parent = new_node

        # Truncate old node to left half (middle key is pushed up, not kept)
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]

        # Insert pushed-up key into parent
        self._insert_into_parent(node, push_up_key, new_node)

    def _insert_into_parent(self, left_node, key, right_node):
        """
        Insert a separator key and right child pointer into the parent
        of left_node. If left_node is the root, create a new root.
        """
        if left_node.parent is None:
            # left_node is the root — create a new root
            new_root = BPlusInternal()
            new_root.keys = [key]
            new_root.children = [left_node, right_node]
            left_node.parent = new_root
            right_node.parent = new_root
            self.root = new_root
            return

        parent = left_node.parent
        right_node.parent = parent

        # Find position to insert the new separator
        pos = parent.children.index(left_node) + 1
        parent.keys.insert(pos - 1, key)
        parent.children.insert(pos, right_node)

        # Split parent if it's overfull
        if parent.is_full(self.order):
            self._split_internal(parent)


# ─── Demo ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 60: B+ Tree — Leaves Linked, Internals Route")
    print("=" * 60)

    # ── Build a tree with sequential inserts ──
    print("\n--- Building B+ Tree (order=4) ---")
    tree = BPlusTree(order=4)

    keys_to_insert = [10, 20, 5, 15, 25, 30, 35, 40, 3, 7, 12, 18, 22, 28, 33, 38]

    for i, key in enumerate(keys_to_insert):
        tree.insert(key, f"val_{key}")
        # Show the tree after the first few inserts and after splits
        if i < 5 or (i + 1) % 4 == 0:
            print(f"\nAfter inserting {key}:")
            tree.visualize()

    # ── Point lookup ──
    print("\n--- Point Lookups ---")
    for k in [10, 25, 99]:
        result = tree.search(k)
        print(f"  search({k}) = {result}")

    # ── Range query — the whole reason B+ trees exist ──
    print("\n--- Range Query (the B+ tree advantage) ---")
    print("  Query: WHERE key BETWEEN 12 AND 30")
    results = tree.range_query(12, 30)
    print(f"  Results: {results}")
    print(f"  Process: O(log n) to find leaf with 12, then follow")
    print(f"  leaf chain until we pass 30. No backtracking!")

    # ── Full traversal via leaf chain ──
    print("\n--- Full Traversal (via leaf chain) ---")
    all_pairs = tree.traverse()
    print(f"  All data: {all_pairs}")
    print(f"  Pure sequential scan — no tree navigation needed.")

    # ── Comparison with B-tree ──
    print("\n--- B+ Tree vs B-Tree: Range Query Cost ---")
    n = len(keys_to_insert)
    k = len(results)
    print(f"  n = {n} keys, range query returns k = {k} results")
    print(f"  B-tree:  O(k * log n) = O({k} * {n.bit_length()}) = O({k * n.bit_length()}) node visits")
    print(f"  B+ tree: O(log n + k)  = O({n.bit_length()} + {k})  = O({n.bit_length() + k}) node visits")
    print(f"  For large k, B+ tree wins dramatically.")
    print(f"  On disk: B-tree needs random seeks; B+ tree reads sequential pages.")

    # ── Demonstrate update ──
    print("\n--- Update existing key ---")
    print(f"  Before: search(10) = {tree.search(10)}")
    tree.insert(10, "UPDATED_10")
    print(f"  After:  search(10) = {tree.search(10)}")

    # ── Larger tree to show structure depth ──
    print("\n--- Larger Tree (50 keys, order=5) ---")
    big_tree = BPlusTree(order=5)
    for i in range(1, 51):
        big_tree.insert(i, f"row_{i}")
    big_tree.visualize()

    range_result = big_tree.range_query(20, 30)
    print(f"\n  range_query(20, 30) = {[k for k, v in range_result]}")
    print(f"  Returned {len(range_result)} results by following the leaf chain")

    print("\nDone.")
