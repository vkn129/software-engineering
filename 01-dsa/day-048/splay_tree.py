"""
Day 48: Splay Tree — Self-Adjusting Binary Search Tree

A splay tree is a BST that moves every accessed node to the root via rotations.
No extra metadata (height, color) is stored. The amortized cost of each
operation is O(log n), proven via the potential method.

The key property: recently accessed elements stay near the root. This makes
splay trees ideal for workloads with temporal locality — caches, garbage
collectors, network routers, anything where a small working set is hot.

Run: python splay_tree.py
"""

import time
import random


# ---------------------------------------------------------------------------
# Node
# ---------------------------------------------------------------------------

class Node:
    """A splay tree node. Note: no height, no color, no balance factor.
    The only structural information is parent/left/right pointers.
    """

    __slots__ = ('key', 'value', 'left', 'right', 'parent')

    def __init__(self, key, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None

    def __repr__(self):
        return f"Node({self.key})"


# ---------------------------------------------------------------------------
# Splay Tree
# ---------------------------------------------------------------------------

class SplayTree:
    """A splay tree: self-adjusting BST with amortized O(log n) operations.

    Every access (search, insert, delete) splays the accessed node to the
    root. This gives the working set property: recently accessed nodes are
    near the root and fast to find again.

    Operations:
    - insert(key, value): Insert a key-value pair, splay to root.
    - search(key): Find a key, splay to root, return value or None.
    - delete(key): Remove a key, splay predecessor/successor.
    - split(key): Split tree into (< key) and (>= key) subtrees.
    - merge(other): Merge another splay tree (all keys must be greater).

    The access_count tracks how many nodes are visited during operations,
    demonstrating the working set property empirically.
    """

    def __init__(self):
        self.root = None
        self.size = 0
        self.access_count = 0  # counts node visits to demonstrate locality

    # --- Rotations ---------------------------------------------------------

    def _left_rotate(self, x):
        """Left rotation around node x.

             x              y
            / \\            / \\
           A   y    ->    x   C
              / \\        / \\
             B   C      A   B

        Preserves BST property. Updates parent pointers.
        """
        y = x.right
        if y is None:
            return

        # Move y's left subtree to x's right
        x.right = y.left
        if y.left is not None:
            y.left.parent = x

        # Update y's parent
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y

        # Put x on y's left
        y.left = x
        x.parent = y

    def _right_rotate(self, x):
        """Right rotation around node x.

             x            y
            / \\          / \\
           y   C   ->   A   x
          / \\              / \\
         A   B            B   C

        Preserves BST property. Updates parent pointers.
        """
        y = x.left
        if y is None:
            return

        # Move y's right subtree to x's left
        x.left = y.right
        if y.right is not None:
            y.right.parent = x

        # Update y's parent
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y

        # Put x on y's right
        y.right = x
        x.parent = y

    # --- Splay Cases -------------------------------------------------------

    def _zig(self, x):
        """Zig: x is a child of the root. Single rotation.

        This is the base case — only used when x's parent is the root.
        """
        p = x.parent
        if x is p.left:
            self._right_rotate(p)
        else:
            self._left_rotate(p)

    def _zig_zig(self, x):
        """Zig-zig: x and parent are both left children (or both right).

        Rotate parent first, then x. The order is critical — rotating
        parent first flattens the path, giving amortized O(log n).
        Rotating x first (naive move-to-root) gives O(n) amortized.
        """
        p = x.parent
        g = p.parent
        if x is p.left and p is g.left:
            # Both left children: rotate g right, then p right
            self._right_rotate(g)
            self._right_rotate(p)
        else:
            # Both right children: rotate g left, then p left
            self._left_rotate(g)
            self._left_rotate(p)

    def _zig_zag(self, x):
        """Zig-zag: x and parent are on opposite sides.

        Rotate x twice — once around parent, once around grandparent.
        Like an AVL double rotation.
        """
        p = x.parent
        g = p.parent
        if x is p.right and p is g.left:
            # x is right child, p is left child
            self._left_rotate(p)
            self._right_rotate(g)
        else:
            # x is left child, p is right child
            self._right_rotate(p)
            self._left_rotate(g)

    # --- Splay (the core operation) ----------------------------------------

    def splay(self, x):
        """Splay node x to the root.

        Repeatedly apply zig, zig-zig, or zig-zag based on x's position
        relative to its parent and grandparent. Each step moves x up by
        1 (zig) or 2 (zig-zig, zig-zag) levels.

        After splaying, x is the root of the tree.
        """
        if x is None:
            return

        while x.parent is not None:
            p = x.parent
            g = p.parent

            if g is None:
                # Parent is the root — zig (single rotation)
                self._zig(x)
            elif (x is p.left and p is g.left) or (x is p.right and p is g.right):
                # Same side — zig-zig
                self._zig_zig(x)
            else:
                # Opposite sides — zig-zag
                self._zig_zag(x)

    # --- BST Operations (all end with a splay) ----------------------------

    def search(self, key):
        """Search for key. Splay the found node (or last visited) to root.

        Returns the value if found, None if not found.
        The working set property means recently searched keys are near the
        root and will be found faster on subsequent searches.
        """
        node = self.root
        last = None

        while node is not None:
            self.access_count += 1
            last = node
            if key == node.key:
                self.splay(node)
                return node.value
            elif key < node.key:
                node = node.left
            else:
                node = node.right

        # Key not found — splay the last visited node
        if last is not None:
            self.splay(last)
        return None

    def insert(self, key, value=None):
        """Insert a key-value pair. Splay the new node to the root.

        If the key already exists, update its value and splay it.
        """
        if self.root is None:
            self.root = Node(key, value)
            self.size += 1
            return

        # Walk down to find insertion point
        node = self.root
        parent = None
        while node is not None:
            self.access_count += 1
            parent = node
            if key == node.key:
                # Key exists — update value and splay
                node.value = value
                self.splay(node)
                return
            elif key < node.key:
                node = node.left
            else:
                node = node.right

        # Create new node and attach
        new_node = Node(key, value)
        new_node.parent = parent
        if key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self.size += 1
        self.splay(new_node)

    def delete(self, key):
        """Delete a key from the tree.

        Strategy:
        1. Splay the key to the root.
        2. If the root's key does not match, key is not in the tree.
        3. Remove the root:
           a. If no left subtree, the right subtree becomes the new tree.
           b. Otherwise, splay the maximum of the left subtree to the
              left subtree's root (so it has no right child), then
              attach the right subtree as its right child.

        Returns True if deleted, False if not found.
        """
        if self.root is None:
            return False

        # Splay the key to the root
        self.search(key)

        if self.root.key != key:
            return False

        # Root now holds the key to delete
        left_subtree = self.root.left
        right_subtree = self.root.right

        if left_subtree is None:
            # No left subtree — right becomes the whole tree
            self.root = right_subtree
            if right_subtree is not None:
                right_subtree.parent = None
        else:
            # Detach both subtrees
            left_subtree.parent = None
            if right_subtree is not None:
                right_subtree.parent = None

            # Splay max of left subtree to its root
            # (walk right until no right child)
            max_node = left_subtree
            while max_node.right is not None:
                max_node = max_node.right

            # Make left subtree a temporary splay tree and splay max to root
            self.root = left_subtree
            self.splay(max_node)

            # Now max_node is root of left subtree with no right child
            # Attach right subtree
            self.root.right = right_subtree
            if right_subtree is not None:
                right_subtree.parent = self.root

        self.size -= 1
        return True

    def split(self, key):
        """Split the tree into two trees around key.

        Returns (left_tree, right_tree) where:
        - left_tree contains all keys < key
        - right_tree contains all keys >= key

        The original tree is consumed (emptied).

        Strategy: splay key (or its successor) to root, then detach.
        """
        if self.root is None:
            return SplayTree(), SplayTree()

        # Splay key or the nearest node to root
        self.search(key)

        left_tree = SplayTree()
        right_tree = SplayTree()

        if self.root.key < key:
            # Root < key: root and left subtree go to left_tree
            # Right subtree goes to right_tree
            right_tree.root = self.root.right
            if right_tree.root is not None:
                right_tree.root.parent = None
            left_tree.root = self.root
            left_tree.root.right = None
        else:
            # Root >= key: root and right subtree go to right_tree
            # Left subtree goes to left_tree
            left_tree.root = self.root.left
            if left_tree.root is not None:
                left_tree.root.parent = None
            right_tree.root = self.root
            right_tree.root.left = None

        # Count sizes
        left_tree.size = _count_nodes(left_tree.root)
        right_tree.size = _count_nodes(right_tree.root)

        # Consume original tree
        self.root = None
        self.size = 0

        return left_tree, right_tree

    @staticmethod
    def merge(tree1, tree2):
        """Merge two splay trees where all keys in tree1 < all keys in tree2.

        Strategy:
        1. Splay the maximum of tree1 to its root (no right child).
        2. Attach tree2's root as tree1's right child.

        Both input trees are consumed. Returns a new SplayTree.
        """
        if tree1.root is None:
            return tree2
        if tree2.root is None:
            return tree1

        # Splay max of tree1 to root
        max_node = tree1.root
        while max_node.right is not None:
            max_node = max_node.right
        tree1.splay(max_node)

        # Attach tree2 as right subtree
        tree1.root.right = tree2.root
        if tree2.root is not None:
            tree2.root.parent = tree1.root

        tree1.size = tree1.size + tree2.size

        # Consume tree2
        tree2.root = None
        tree2.size = 0

        return tree1

    def reset_access_count(self):
        """Reset the access counter. Used for benchmarking."""
        self.access_count = 0

    # --- Utility -----------------------------------------------------------

    def minimum(self):
        """Return the minimum key in the tree."""
        if self.root is None:
            return None
        node = self.root
        while node.left is not None:
            node = node.left
        self.splay(node)
        return node.key

    def maximum(self):
        """Return the maximum key in the tree."""
        if self.root is None:
            return None
        node = self.root
        while node.right is not None:
            node = node.right
        self.splay(node)
        return node.key

    def inorder(self):
        """Return keys in sorted order via inorder traversal."""
        result = []
        _inorder_helper(self.root, result)
        return result

    def height(self):
        """Return the height of the tree (for analysis, not used in operations)."""
        return _height(self.root)

    def __len__(self):
        return self.size

    def __contains__(self, key):
        return self.search(key) is not None

    def __repr__(self):
        if self.root is None:
            return "SplayTree(empty)"
        return f"SplayTree(root={self.root.key}, size={self.size})"


# ---------------------------------------------------------------------------
# Helper functions (outside the class to keep it clean)
# ---------------------------------------------------------------------------

def _count_nodes(node):
    """Count nodes in a subtree."""
    if node is None:
        return 0
    return 1 + _count_nodes(node.left) + _count_nodes(node.right)


def _inorder_helper(node, result):
    """Collect keys in sorted order."""
    if node is None:
        return
    _inorder_helper(node.left, result)
    result.append(node.key)
    _inorder_helper(node.right, result)


def _height(node):
    """Compute height of a subtree."""
    if node is None:
        return -1
    return 1 + max(_height(node.left), _height(node.right))


def _print_tree(node, prefix="", is_left=True, is_root=True):
    """Print a visual representation of the tree."""
    if node is None:
        return
    if is_root:
        print(f"    {node.key}")
    else:
        connector = "|-- " if is_left else "`-- "
        print(f"    {prefix}{connector}{node.key}")

    new_prefix = prefix + ("|   " if is_left and not is_root else "    ")
    if node.left is not None or node.right is not None:
        if node.left is not None:
            _print_tree(node.left, new_prefix, True, False)
        else:
            print(f"    {new_prefix}|-- (nil)")
        if node.right is not None:
            _print_tree(node.right, new_prefix, False, False)
        else:
            print(f"    {new_prefix}`-- (nil)")


# ---------------------------------------------------------------------------
# Demonstration: Splay operations visualized
# ---------------------------------------------------------------------------

def demo_splay_operations():
    """Show how the splay operation restructures the tree."""
    print("=" * 70)
    print("  SPLAY TREE — SPLAY OPERATION DEMONSTRATION")
    print("=" * 70)

    tree = SplayTree()
    # Insert in sorted order to create a degenerate tree (worst case for BST)
    for k in [1, 2, 3, 4, 5, 6, 7]:
        tree.insert(k)

    print("\n  After inserting 1-7 (each insert splays to root):")
    print(f"  Root: {tree.root.key}, Height: {tree.height()}")
    print(f"  Inorder: {tree.inorder()}")
    _print_tree(tree.root)

    print(f"\n  Now searching for 1 (splays 1 to root):")
    tree.search(1)
    print(f"  Root: {tree.root.key}, Height: {tree.height()}")
    _print_tree(tree.root)

    print(f"\n  Now searching for 4 (splays 4 to root):")
    tree.search(4)
    print(f"  Root: {tree.root.key}, Height: {tree.height()}")
    _print_tree(tree.root)

    print(f"\n  Key observation: the tree reshapes itself around the access")
    print(f"  pattern. No height or color metadata needed.\n")


# ---------------------------------------------------------------------------
# Demonstration: Split and Merge
# ---------------------------------------------------------------------------

def demo_split_merge():
    """Show split and merge operations."""
    print("=" * 70)
    print("  SPLAY TREE — SPLIT AND MERGE")
    print("=" * 70)

    tree = SplayTree()
    for k in [3, 1, 5, 2, 7, 4, 6]:
        tree.insert(k)
    print(f"\n  Original tree: {tree.inorder()}")

    left, right = tree.split(4)
    print(f"\n  After split(4):")
    print(f"    Left tree  (< 4): {left.inorder()}")
    print(f"    Right tree (>= 4): {right.inorder()}")

    merged = SplayTree.merge(left, right)
    print(f"\n  After merge:")
    print(f"    Merged tree: {merged.inorder()}")
    print(f"    Size: {merged.size}\n")


# ---------------------------------------------------------------------------
# Demonstration: Working set property
# ---------------------------------------------------------------------------

def demo_working_set():
    """Demonstrate that recently accessed elements are cheaper to find."""
    print("=" * 70)
    print("  SPLAY TREE — WORKING SET PROPERTY")
    print("=" * 70)

    n = 1000
    tree = SplayTree()
    keys = list(range(n))
    random.seed(42)
    random.shuffle(keys)
    for k in keys:
        tree.insert(k)

    print(f"\n  Tree with {n} nodes.\n")

    # Access a key, then immediately re-access it
    print("  Experiment 1: Access a key, then immediately re-access it.")
    print("  (The second access should be much cheaper.)\n")

    test_keys = [random.randint(0, n - 1) for _ in range(10)]
    print(f"  {'Key':>6}  {'1st access':>12}  {'2nd access':>12}  {'Speedup':>10}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*12}  {'-'*10}")

    for key in test_keys:
        tree.reset_access_count()
        tree.search(key)
        first = tree.access_count

        tree.reset_access_count()
        tree.search(key)
        second = tree.access_count

        speedup = f"{first / second:.1f}x" if second > 0 else "inf"
        print(f"  {key:>6}  {first:>12}  {second:>12}  {speedup:>10}")

    # Hot set vs cold set
    print(f"\n  Experiment 2: Hot set (10 keys) vs cold set (random keys).")
    print(f"  Access the hot set 100 times, then compare access costs.\n")

    hot_keys = random.sample(range(n), 10)

    # Warm up the hot set
    for _ in range(100):
        for k in hot_keys:
            tree.search(k)

    # Measure hot set access cost
    tree.reset_access_count()
    for k in hot_keys:
        tree.search(k)
    hot_cost = tree.access_count

    # Measure cold set access cost
    cold_keys = random.sample(range(n), 10)
    tree.reset_access_count()
    for k in cold_keys:
        tree.search(k)
    cold_cost = tree.access_count

    print(f"  Hot set  (10 keys, recently accessed): {hot_cost:>6} node visits")
    print(f"  Cold set (10 random keys):             {cold_cost:>6} node visits")
    if hot_cost > 0:
        print(f"  Cold/Hot ratio:                        {cold_cost / hot_cost:>6.1f}x")
    print(f"\n  Hot keys stay near the root — that is the working set property.\n")


# ---------------------------------------------------------------------------
# Benchmark: Temporal locality vs uniform random
# ---------------------------------------------------------------------------

def benchmark_locality():
    """Compare splay tree performance: temporal locality vs uniform random."""
    print("=" * 70)
    print("  BENCHMARK: Temporal Locality vs Uniform Random Access")
    print("=" * 70)

    n = 5000
    num_ops = 20000
    tree_locality = SplayTree()
    tree_uniform = SplayTree()

    # Build identical trees
    keys = list(range(n))
    random.seed(42)
    random.shuffle(keys)
    for k in keys:
        tree_locality.insert(k)
        tree_uniform.insert(k)

    # Temporal locality pattern: access a small window that shifts over time
    tree_locality.reset_access_count()
    random.seed(123)
    window_start = 0
    window_size = 50
    for i in range(num_ops):
        # Every 200 ops, shift the window
        if i % 200 == 0:
            window_start = random.randint(0, n - window_size)
        key = random.randint(window_start, window_start + window_size - 1)
        tree_locality.search(key)
    locality_accesses = tree_locality.access_count

    # Uniform random pattern: access any key with equal probability
    tree_uniform.reset_access_count()
    random.seed(456)
    for _ in range(num_ops):
        key = random.randint(0, n - 1)
        tree_uniform.search(key)
    uniform_accesses = tree_uniform.access_count

    print(f"\n  Tree size: {n}, Operations: {num_ops}")
    print(f"\n  {'Pattern':>20}  {'Total node visits':>20}  {'Avg per search':>16}")
    print(f"  {'-'*20}  {'-'*20}  {'-'*16}")
    print(f"  {'Temporal locality':>20}  {locality_accesses:>20,}  "
          f"{locality_accesses / num_ops:>14.1f}")
    print(f"  {'Uniform random':>20}  {uniform_accesses:>20,}  "
          f"{uniform_accesses / num_ops:>14.1f}")
    print(f"\n  Locality advantage: {uniform_accesses / locality_accesses:.1f}x fewer "
          f"node visits with temporal locality.")
    print(f"  This is why caches love splay trees — they adapt to the working set.\n")


# ---------------------------------------------------------------------------
# Benchmark: Splay tree vs sorted dict (wall-clock time)
# ---------------------------------------------------------------------------

def benchmark_wall_clock():
    """Wall-clock comparison of splay tree with and without locality."""
    print("=" * 70)
    print("  BENCHMARK: Wall-Clock Time — Locality vs No Locality")
    print("=" * 70)

    n = 10000
    num_ops = 50000

    tree = SplayTree()
    keys = list(range(n))
    random.seed(42)
    random.shuffle(keys)
    for k in keys:
        tree.insert(k)

    # Temporal locality: repeatedly access a hot set
    hot_set = random.sample(range(n), 20)
    random.seed(100)
    start = time.perf_counter()
    for _ in range(num_ops):
        tree.search(random.choice(hot_set))
    t_locality = time.perf_counter() - start

    # Rebuild tree for fair comparison
    tree2 = SplayTree()
    random.seed(42)
    random.shuffle(keys)
    for k in keys:
        tree2.insert(k)

    # Uniform random
    random.seed(200)
    start = time.perf_counter()
    for _ in range(num_ops):
        tree2.search(random.randint(0, n - 1))
    t_uniform = time.perf_counter() - start

    print(f"\n  Tree size: {n}, Operations: {num_ops}")
    print(f"\n  {'Pattern':>20}  {'Time (s)':>12}  {'us/op':>10}")
    print(f"  {'-'*20}  {'-'*12}  {'-'*10}")
    print(f"  {'Temporal locality':>20}  {t_locality:>12.6f}  "
          f"{t_locality / num_ops * 1_000_000:>8.2f}us")
    print(f"  {'Uniform random':>20}  {t_uniform:>12.6f}  "
          f"{t_uniform / num_ops * 1_000_000:>8.2f}us")
    print(f"\n  Locality speedup: {t_uniform / t_locality:.1f}x\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Day 48: Splay Trees — Amortized O(log n), Why Caches Love Them")
    print("=" * 70)
    print()
    print("Splay trees have no height or color metadata. Instead, every access")
    print("moves the accessed node to the root via rotations. This gives")
    print("amortized O(log n) and the working set property: recently accessed")
    print("elements are near the root and fast to find again.\n")

    demo_splay_operations()
    demo_split_merge()
    demo_working_set()
    benchmark_locality()
    benchmark_wall_clock()

    print("=" * 70)
    print("  KEY TAKEAWAYS")
    print("=" * 70)
    print("""
  1. Splay trees store NO extra metadata — no height, no color, no balance
     factor. The splay operation is the only balancing mechanism.
  2. Three splay cases: zig (single), zig-zig (same side, rotate parent
     first), zig-zag (opposite sides, double rotation).
  3. Amortized O(log n) per operation via the potential method. Individual
     operations can be O(n), but expensive ones restructure the tree.
  4. Working set property: recently accessed elements are near the root.
     This makes splay trees ideal for workloads with temporal locality.
  5. Split and merge decompose into splay operations — the tree can be
     efficiently broken apart and recombined.
  6. Failure modes: sequential access gives O(n) individual operations,
     uniform random access gains no benefit from splaying, and every
     read mutates the tree (hostile to concurrent access).
""")
