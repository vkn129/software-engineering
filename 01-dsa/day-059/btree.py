"""
Day 59: B-Tree — Disk-Optimized Search Tree
=============================================
A B-tree packs many keys per node to minimize disk I/O.
Where a BST needs O(log2 n) disk reads, a B-tree needs O(log_t n).

    t = minimum degree (each node has t-1 to 2t-1 keys, except root)

    Insert uses proactive splitting: split full nodes on the way DOWN,
    so we never need to backtrack upward. Single-pass, top-down.

    Search walks down the tree, scanning keys within each node to pick
    the correct child — each node visit = 1 disk read.

Run: python btree.py
"""


# ─── BTreeNode ─────────────────────────────────────────────────────

class BTreeNode:
    """A single node in the B-tree.

    keys:     sorted list of keys stored in this node
    children: list of child node pointers (len = len(keys) + 1 for internal nodes)
    leaf:     True if this is a leaf node (no children)
    """
    __slots__ = ('keys', 'children', 'leaf')

    def __init__(self, leaf=True):
        self.keys = []
        self.children = []
        self.leaf = leaf

    def __repr__(self):
        return f"BTreeNode(keys={self.keys}, leaf={self.leaf})"


# ─── BTree ─────────────────────────────────────────────────────────

class BTree:
    """
    B-tree with minimum degree t.

    Each node has:
      - At most 2t-1 keys (a "full" node)
      - At least t-1 keys (except root, which can have 1)
      - If internal: len(children) == len(keys) + 1

    Insert uses proactive splitting (split-on-descent):
      On the way down, if we hit a full node, split it BEFORE entering.
      This guarantees the leaf we reach has room for the new key.
    """

    def __init__(self, t=3):
        if t < 2:
            raise ValueError("Minimum degree t must be >= 2")
        self.t = t
        self.root = BTreeNode(leaf=True)

    # ── Search ──────────────────────────────────────────────────────

    def search(self, key, node=None):
        """
        Search for key in the B-tree.
        Returns (node, index) if found, None otherwise.

        Within each node, we do a linear scan of keys.
        (In production with large t, you'd use binary search.)
        """
        if node is None:
            node = self.root

        # Find the first key >= search key
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        # Check if we found the key
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)

        # If leaf, key doesn't exist
        if node.leaf:
            return None

        # Recurse into the appropriate child
        return self.search(key, node.children[i])

    # ── Insert ──────────────────────────────────────────────────────

    def insert(self, key):
        """
        Insert key using proactive splitting (split-on-descent).

        Special case: if root is full, split it first (this is the
        only way the tree grows taller — the root splits upward).
        """
        root = self.root

        # If root is full, split it — tree grows one level
        if len(root.keys) == 2 * self.t - 1:
            new_root = BTreeNode(leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root

        self._insert_non_full(self.root, key)

    def _split_child(self, parent, index):
        """
        Split parent.children[index] which must be full (2t-1 keys).

        1. Create new node z with the upper t-1 keys
        2. Promote the median key into parent at position index
        3. Original child keeps lower t-1 keys
        4. Fix child pointers
        """
        t = self.t
        full_child = parent.children[index]
        new_node = BTreeNode(leaf=full_child.leaf)

        # Median key goes up to parent
        median_key = full_child.keys[t - 1]

        # New node gets the upper t-1 keys
        new_node.keys = full_child.keys[t:]

        # If not leaf, new node gets the upper t children
        if not full_child.leaf:
            new_node.children = full_child.children[t:]
            full_child.children = full_child.children[:t]

        # Original child keeps only lower t-1 keys
        full_child.keys = full_child.keys[:t - 1]

        # Insert median key and new child into parent
        parent.keys.insert(index, median_key)
        parent.children.insert(index + 1, new_node)

    def _insert_non_full(self, node, key):
        """
        Insert key into a node that is guaranteed not full.

        If leaf: insert key in sorted position.
        If internal: find correct child, split it if full, then recurse.
        """
        if node.leaf:
            # Find insertion point and insert
            i = len(node.keys) - 1
            node.keys.append(None)  # Make room
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            # Find which child to descend into
            i = len(node.keys) - 1
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            # Proactive split: if the child is full, split it BEFORE descending
            if len(node.children[i].keys) == 2 * self.t - 1:
                self._split_child(node, i)
                # After split, the median moved up. Decide which side to go.
                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key)

    # ── Traverse ────────────────────────────────────────────────────

    def traverse(self, node=None):
        """
        In-order traversal yielding all keys in sorted order.

        For a node with keys [k0, k1, ..., kn-1] and children [c0, c1, ..., cn]:
            yield from c0, then k0, then c1, then k1, ..., then cn
        """
        if node is None:
            node = self.root

        for i in range(len(node.keys)):
            if not node.leaf:
                yield from self.traverse(node.children[i])
            yield node.keys[i]

        # Don't forget the last child
        if not node.leaf:
            yield from self.traverse(node.children[len(node.keys)])

    # ── Visualize ───────────────────────────────────────────────────

    def visualize(self):
        """Print tree structure showing keys at each node and level."""
        if not self.root.keys:
            print("(empty tree)")
            return

        # BFS level-by-level
        levels = []
        queue = [(self.root, 0)]
        while queue:
            node, level = queue.pop(0)
            if level == len(levels):
                levels.append([])
            levels[level].append(node.keys[:])
            if not node.leaf:
                for child in node.children:
                    queue.append((child, level + 1))

        for i, level in enumerate(levels):
            nodes_str = "  ".join(str(keys) for keys in level)
            tag = " (root)" if i == 0 else ""
            print(f"  Level {i}{tag}: {nodes_str}")

    # ── Utility ─────────────────────────────────────────────────────

    def height(self):
        """Return the height of the tree (0 for a single root node)."""
        h = 0
        node = self.root
        while not node.leaf:
            node = node.children[0]
            h += 1
        return h

    def __contains__(self, key):
        return self.search(key) is not None

    def __repr__(self):
        keys = list(self.traverse())
        return f"BTree(t={self.t}, keys={keys})"


# ─── Demo ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 59: B-Tree — Disk-Optimized Search Tree")
    print("=" * 60)

    # ── Build a B-tree and watch it grow ──

    bt = BTree(t=3)  # Each node holds 2-5 keys

    print(f"\nB-tree with minimum degree t={bt.t}")
    print(f"  Max keys per node: {2 * bt.t - 1}")
    print(f"  Min keys per node: {bt.t - 1} (except root)")

    # Insert keys one by one, showing splits
    keys = [10, 20, 5, 6, 12, 30, 7, 17, 3, 1, 15, 25, 35, 40, 8, 9, 11, 13, 14, 16]

    print(f"\nInserting: {keys}")
    for i, key in enumerate(keys):
        bt.insert(key)
        if i in [4, 9, 14, 19]:  # Show tree at key points
            print(f"\n  After inserting {keys[:i+1][-5:]}... ({i+1} keys total):")
            bt.visualize()

    print(f"\n  Final tree ({len(keys)} keys):")
    bt.visualize()
    print(f"  Height: {bt.height()}")

    # ── Search ──

    print(f"\n--- Search ---")
    for k in [12, 25, 99, 1]:
        result = bt.search(k)
        if result:
            node, idx = result
            print(f"  search({k}) -> found at index {idx} in node {node.keys}")
        else:
            print(f"  search({k}) -> not found")

    # ── Sorted traversal ──

    print(f"\n--- In-order Traversal ---")
    sorted_keys = list(bt.traverse())
    print(f"  {sorted_keys}")
    assert sorted_keys == sorted(keys), "Traversal should be sorted!"

    # ── Disk I/O comparison ──

    import math
    print(f"\n--- Disk I/O Comparison ---")
    for n in [1_000, 1_000_000, 1_000_000_000]:
        bst_depth = math.ceil(math.log2(n + 1))
        for t in [100, 500, 1000]:
            btree_depth = math.ceil(math.log(n) / math.log(t)) if n > 1 else 1
            print(f"  n={n:>13,}  BST depth={bst_depth:>2}  "
                  f"B-tree(t={t:>4}) depth={btree_depth}")
        print()

    print("Done.")
