"""
Day 45: BST Degradation — Why Insertion Order Determines Performance
====================================================================
Core insight: the same n values can produce a balanced O(log n) tree
or a degenerate O(n) linked list, depending entirely on insertion order.

This module measures the difference experimentally, making the case
for self-balancing trees (Days 46-48) visceral rather than theoretical.
"""

import sys
import os
import random
import time

# Import TreeNode from Day 36 — the shared tree building block
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-036'))
from binary_tree import TreeNode


# ─── BST Construction ────────────────────────────────────────────────

def bst_insert(root, val):
    """Insert a value into a BST rooted at `root`. Return the root.

    Standard BST insertion: walk left/right based on comparison,
    attach new node at the first empty spot.

    This is O(h) where h = height — which is the whole problem.
    If the tree is balanced, h = O(log n). If degenerate, h = O(n).
    """
    if root is None:
        return TreeNode(val)

    current = root
    while True:
        if val < current.val:
            if current.left is None:
                current.left = TreeNode(val)
                return root
            current = current.left
        else:
            if current.right is None:
                current.right = TreeNode(val)
                return root
            current = current.right


def build_bst_from_sequence(values):
    """Insert values one by one into an empty BST, return root.

    The ORDER of `values` completely determines the tree shape.
    Same set of values in different order → wildly different trees.

    This is the fundamental demonstration: data doesn't determine
    performance, insertion order does.
    """
    root = None
    for val in values:
        root = bst_insert(root, val)
    return root


# ─── Measurement Functions ───────────────────────────────────────────

def measure_height(root):
    """Return the height of the tree (longest root-to-leaf path in edges).

    Empty tree → -1, single node → 0.
    This is the key metric: balanced = O(log n), degenerate = O(n).
    """
    if root is None:
        return -1
    return 1 + max(measure_height(root.left), measure_height(root.right))


def measure_avg_depth(root):
    """Return the average depth of all nodes in the tree.

    Depth of a node = number of edges from root to that node.
    Average depth directly correlates with expected search cost
    for a random lookup.

    Returns 0.0 for empty tree.
    """
    if root is None:
        return 0.0

    total_depth = 0
    node_count = 0

    # Iterative BFS to avoid stack overflow on degenerate trees
    queue = [(root, 0)]  # (node, depth)
    while queue:
        node, depth = queue.pop(0)
        total_depth += depth
        node_count += 1
        if node.left:
            queue.append((node.left, depth + 1))
        if node.right:
            queue.append((node.right, depth + 1))

    return total_depth / node_count


def count_comparisons(root, key):
    """Count how many comparisons are needed to search for `key`.

    Returns the number of nodes visited during BST search.
    For a balanced tree: O(log n). For degenerate: O(n).

    Returns 0 if tree is empty.
    Returns the count whether or not the key is found.
    """
    count = 0
    current = root
    while current is not None:
        count += 1
        if key == current.val:
            return count
        elif key < current.val:
            current = current.left
        else:
            current = current.right
    return count  # key not found, but we still counted comparisons


# ─── Benchmarking ────────────────────────────────────────────────────

def benchmark_random_vs_sorted(n):
    """Compare BST performance for random vs sorted insertion of n values.

    This is the core demonstration. For n = 10,000:
    - Sorted: height ≈ 9,999 (a linked list!)
    - Random: height ≈ 28 (close to log₂(10000) ≈ 13)

    Returns a dict with detailed metrics for both insertion orders.
    """
    values = list(range(1, n + 1))

    # ── Sorted insertion (worst case) ──
    # Use iterative insertion to avoid recursion limit
    sys.setrecursionlimit(max(sys.getrecursionlimit(), n + 100))
    sorted_root = build_bst_from_sequence(values)
    sorted_height = measure_height(sorted_root)

    # For large n, avg_depth of degenerate tree is ~n/2 (skip measurement
    # for very large n to avoid slow BFS on a linked list)
    if n <= 5000:
        sorted_avg_depth = measure_avg_depth(sorted_root)
    else:
        sorted_avg_depth = (n - 1) / 2.0  # exact for a linked list

    # Comparisons to find the last element (worst case search)
    sorted_worst_search = count_comparisons(sorted_root, n)

    # ── Random insertion (expected case) ──
    random.seed(42)  # reproducible
    shuffled = values[:]
    random.shuffle(shuffled)
    random_root = build_bst_from_sequence(shuffled)
    random_height = measure_height(random_root)
    random_avg_depth = measure_avg_depth(random_root)

    # Comparisons to find same element
    random_worst_search = count_comparisons(random_root, n)

    # ── Optimal (median-first) insertion ──
    optimal_order = optimal_insertion_order(values)
    optimal_root = build_bst_from_sequence(optimal_order)
    optimal_height = measure_height(optimal_root)
    optimal_avg_depth = measure_avg_depth(optimal_root)
    optimal_worst_search = count_comparisons(optimal_root, n)

    import math
    theoretical_optimal = math.floor(math.log2(n)) if n > 0 else 0

    return {
        'n': n,
        'theoretical_optimal_height': theoretical_optimal,
        'sorted': {
            'height': sorted_height,
            'avg_depth': round(sorted_avg_depth, 1),
            'worst_search': sorted_worst_search,
        },
        'random': {
            'height': random_height,
            'avg_depth': round(random_avg_depth, 1),
            'worst_search': random_worst_search,
        },
        'optimal': {
            'height': optimal_height,
            'avg_depth': round(optimal_avg_depth, 1),
            'worst_search': optimal_worst_search,
        },
    }


# ─── Optimal Insertion Order ─────────────────────────────────────────

def optimal_insertion_order(sorted_arr):
    """Reorder a sorted array so that inserting values in this order
    into a BST produces a perfectly balanced tree.

    Strategy: insert the median first (it becomes the root),
    then recursively insert medians of left and right halves.

    This is a BFS-order collection of medians:
        [4, 2, 6, 1, 3, 5, 7] for input [1,2,3,4,5,6,7]

    Why this works: the median splits remaining elements evenly,
    so left and right subtrees have equal (±1) size at every level.

    This requires knowing all values upfront — which is why
    self-balancing trees are needed for online insertion.
    """
    if not sorted_arr:
        return []

    result = []

    # Use a queue for BFS-style median extraction
    # Each entry is a (start, end) range representing a subarray
    queue = [(0, len(sorted_arr) - 1)]

    while queue:
        next_queue = []
        for start, end in queue:
            if start > end:
                continue
            mid = (start + end) // 2
            result.append(sorted_arr[mid])
            next_queue.append((start, mid - 1))
            next_queue.append((mid + 1, end))
        queue = next_queue

    return result


# ─── Degenerate Detection ────────────────────────────────────────────

def is_degenerate(root):
    """Check if a BST is essentially a linked list.

    A tree is degenerate if every internal node has at most one child.
    This means height == n - 1 (every node adds to the depth).

    In practice, we check: does any node have two children?
    If not, the tree is a chain.

    Returns True if tree is degenerate (or empty/single node).
    """
    if root is None:
        return True

    current = root
    # Walk the tree — in a degenerate tree, there's exactly one path
    while current is not None:
        has_left = current.left is not None
        has_right = current.right is not None

        if has_left and has_right:
            # Found a node with two children — not degenerate
            return False

        # Move to the single child (or None if leaf)
        current = current.left if has_left else current.right

    return True


# ─── Balance Visualization ───────────────────────────────────────────

def visualize_balance(root):
    """Return an ASCII visualization showing balance factors at each node.

    Balance factor = height(left) - height(right)
    - 0: perfectly balanced at this node
    - +1/-1: slightly unbalanced (still acceptable for AVL)
    - Large positive: left-heavy
    - Large negative: right-heavy

    Output format:
        val(bf)
    where bf is the balance factor.

    Uses an indented tree format for readability.
    """
    lines = []

    def _build(node, prefix, is_left, is_root):
        if node is None:
            return

        # Compute balance factor
        lh = measure_height(node.left)
        rh = measure_height(node.right)
        bf = lh - rh

        # Format: connector + val(bf)
        if is_root:
            connector = ""
        elif is_left:
            connector = prefix + "├── "
        else:
            connector = prefix + "└── "

        # Color-code balance factor in the label
        if abs(bf) <= 1:
            label = f"{node.val}(bf={bf})"
        else:
            label = f"{node.val}(bf={bf}) ***"  # flag imbalanced nodes

        if is_root:
            lines.append(label)
        else:
            lines.append(connector + label)

        # Determine prefix extension for children
        if is_root:
            child_prefix = ""
        elif is_left:
            child_prefix = prefix + "│   "
        else:
            child_prefix = prefix + "    "

        # Recurse: left first, then right
        if node.left or node.right:
            _build(node.left, child_prefix, True, False) if node.left else None
            _build(node.right, child_prefix, False, False) if node.right else None

    _build(root, "", True, True)
    return "\n".join(lines)


# ─── Demonstration ───────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("Day 45: BST Degradation — Why Insertion Order Matters")
    print("=" * 65)

    # ── Small example: visual comparison ──
    print("\n── Visual Comparison (7 nodes) ──\n")

    sorted_vals = [1, 2, 3, 4, 5, 6, 7]
    sorted_tree = build_bst_from_sequence(sorted_vals)
    print("Sorted insertion [1,2,3,4,5,6,7]:")
    print(f"  Height: {measure_height(sorted_tree)}")
    print(f"  Degenerate: {is_degenerate(sorted_tree)}")
    print(f"  Comparisons to find 7: {count_comparisons(sorted_tree, 7)}")
    print(f"  Balance factors:")
    for line in visualize_balance(sorted_tree).split("\n"):
        print(f"    {line}")

    print()
    optimal = optimal_insertion_order(sorted_vals)
    balanced_tree = build_bst_from_sequence(optimal)
    print(f"Optimal insertion order {optimal}:")
    print(f"  Height: {measure_height(balanced_tree)}")
    print(f"  Degenerate: {is_degenerate(balanced_tree)}")
    print(f"  Comparisons to find 7: {count_comparisons(balanced_tree, 7)}")
    print(f"  Balance factors:")
    for line in visualize_balance(balanced_tree).split("\n"):
        print(f"    {line}")

    # ── Benchmark at various sizes ──
    print("\n── Benchmark: Random vs Sorted vs Optimal ──\n")
    print(f"{'n':>7} │ {'Metric':<14} │ {'Sorted':>8} │ {'Random':>8} │ {'Optimal':>8} │ {'Theory':>8}")
    print("─" * 72)

    for n in [100, 1000, 5000]:
        results = benchmark_random_vs_sorted(n)
        s = results['sorted']
        r = results['random']
        o = results['optimal']
        t = results['theoretical_optimal_height']

        print(f"{n:>7} │ {'height':<14} │ {s['height']:>8} │ {r['height']:>8} │ {o['height']:>8} │ {t:>8}")
        print(f"{'':>7} │ {'avg_depth':<14} │ {s['avg_depth']:>8} │ {r['avg_depth']:>8} │ {o['avg_depth']:>8} │ {'':>8}")
        print(f"{'':>7} │ {'worst_search':<14} │ {s['worst_search']:>8} │ {r['worst_search']:>8} │ {o['worst_search']:>8} │ {'':>8}")
        print("─" * 72)

    # ── The punchline ──
    print("\n── The Punchline ──\n")
    r = benchmark_random_vs_sorted(1000)
    ratio = r['sorted']['height'] / max(r['optimal']['height'], 1)
    print(f"For n=1000:")
    print(f"  Sorted insertion height:  {r['sorted']['height']}")
    print(f"  Optimal insertion height: {r['optimal']['height']}")
    print(f"  Degradation factor:       {ratio:.0f}x")
    print(f"\n  Same data. Same tree type. {ratio:.0f}x worse performance.")
    print(f"  This is why self-balancing trees exist.")

    # ── Degenerate detection ──
    print("\n── Degenerate Detection ──\n")
    cases = [
        ("sorted [1..10]", build_bst_from_sequence(range(1, 11))),
        ("reverse [10..1]", build_bst_from_sequence(range(10, 0, -1))),
        ("random 10 values", build_bst_from_sequence(random.sample(range(1, 11), 10))),
        ("optimal order", build_bst_from_sequence(optimal_insertion_order(list(range(1, 11))))),
        ("single node", build_bst_from_sequence([42])),
        ("empty", build_bst_from_sequence([])),
    ]
    for name, tree in cases:
        print(f"  {name:<25} degenerate={is_degenerate(tree)}, height={measure_height(tree)}")
