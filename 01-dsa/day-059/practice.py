"""
Day 59 Practice: B-Tree Exercises
===================================
Run: python practice.py
"""

import sys
import os
import math
sys.path.insert(0, os.path.dirname(__file__))
from btree import BTree, BTreeNode


# ─── Exercise 1: Search with Path Tracing ─────────────────────────
#
# Search for a key in a B-tree and return the path of nodes traversed
# (to count "disk reads"). Each node visited = 1 disk page read.
#
# Return a list of (node.keys, found_bool) tuples for each node visited.
# The last tuple has found_bool=True if key was found, False if not.
#
# Example (t=3, keys [1..20]):
#   search_path(tree, 15) -> [([10], False), ([13, 16], False), ([14, 15], True)]
#   That's 3 disk reads.

def search_path(tree, key):
    # TODO: return list of (node_keys_copy, found) tuples
    pass


# ─── Exercise 2: Bulk Load from Sorted Data ───────────────────────
#
# Build a B-tree optimally from already-sorted data.
# Instead of inserting one key at a time (which causes many splits),
# fill leaves left-to-right, promoting medians to build parents bottom-up.
#
# For simplicity: given sorted keys, pack leaves with (2t-1) keys each
# (maximally full), then build parent levels by taking medians.
#
# Return a BTree with the data loaded.
#
# Example:
#   bulk_load([1,2,3,4,5,6,7,8,9], t=2)
#   -> a B-tree containing all 9 keys with minimal height

def bulk_load(sorted_keys, t=3):
    # TODO: return a BTree populated with sorted_keys
    pass


# ─── Exercise 3: Range Query ──────────────────────────────────────
#
# Find all keys in the B-tree within the range [lo, hi] (inclusive).
# Use the tree structure to skip subtrees that can't contain keys in range.
#
# Don't just traverse all keys and filter — prune branches where
# all keys are < lo or > hi.
#
# Example:
#   tree has keys [1, 3, 5, 7, 9, 11, 13, 15]
#   range_query(tree, 5, 11) -> [5, 7, 9, 11]

def range_query(tree, lo, hi):
    # TODO: return sorted list of keys in [lo, hi]
    pass


# ─── Exercise 4: Verify B-Tree Properties ─────────────────────────
#
# Given a BTree, verify:
#   1. All leaves are at the same depth
#   2. Every non-root node has between t-1 and 2t-1 keys
#   3. Root has between 1 and 2t-1 keys (if non-empty)
#   4. Keys within each node are sorted
#   5. Internal nodes have len(keys)+1 children
#   6. For internal nodes, child[i] keys < keys[i] < child[i+1] keys
#
# Return (is_valid, message) where message describes the first violation
# found, or "Valid B-tree" if all checks pass.

def verify_btree(tree):
    # TODO: return (bool, str)
    pass


# ─── Exercise 5: Disk I/O Simulator ───────────────────────────────
#
# Compare disk reads between a BST and a B-tree for the same data.
#
# Given n keys (1 to n) and a list of search queries:
#   1. Build a B-tree with minimum degree t
#   2. For each query, count how many nodes are visited (= disk reads)
#   3. Compare with BST depth for the same n (ceil(log2(n+1)))
#
# Return a dict:
#   {
#     "btree_total_reads": total disk reads across all queries,
#     "bst_total_reads": total BST reads (depth per query) across all queries,
#     "btree_avg": average reads per query,
#     "bst_avg": average reads per query for BST,
#     "speedup": bst_avg / btree_avg
#   }

def disk_io_compare(n, queries, t=100):
    # TODO: return dict with comparison stats
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_search_path(tree, key):
    path = []
    node = tree.root
    while True:
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1

        if i < len(node.keys) and key == node.keys[i]:
            path.append((node.keys[:], True))
            return path

        path.append((node.keys[:], False))

        if node.leaf:
            return path

        node = node.children[i]


def _sol_bulk_load(sorted_keys, t=3):
    tree = BTree(t=t)
    if not sorted_keys:
        return tree

    # Simple approach: leaves get up to (2t-1) keys, build parents from medians
    max_keys = 2 * t - 1

    # Build leaf nodes
    leaves = []
    for i in range(0, len(sorted_keys), max_keys):
        chunk = sorted_keys[i:i + max_keys]
        node = BTreeNode(leaf=True)
        node.keys = list(chunk)
        leaves.append(node)

    # If only one leaf, it's the root
    if len(leaves) == 1:
        tree.root = leaves[0]
        return tree

    # Build parent levels bottom-up
    current_level = leaves
    while len(current_level) > 1:
        parents = []
        i = 0
        while i < len(current_level):
            parent = BTreeNode(leaf=False)

            # Take up to 2t children for this parent
            max_children = 2 * t
            group = current_level[i:i + max_children]

            if len(group) == 1:
                # If only one node left, let the previous parent absorb it
                if parents:
                    prev = parents[-1]
                    # Promote a key from the single child and attach it
                    median = group[0].keys[0]
                    prev.keys.append(median)
                    if group[0].leaf:
                        # Absorb keys directly if possible, otherwise add as child
                        prev.children.append(group[0])
                    else:
                        prev.children.append(group[0])
                    i += 1
                    continue
                else:
                    tree.root = group[0]
                    return tree

            # First child always added
            parent.children.append(group[0])
            for j in range(1, len(group)):
                # Promote the smallest key from this child as separator
                median = group[j].keys[0]
                parent.keys.append(median)
                # Remove promoted key from child
                child = group[j]
                child_copy = BTreeNode(leaf=child.leaf)
                child_copy.keys = child.keys[1:]
                child_copy.children = child.children[1:] if not child.leaf else []
                # If removing the key leaves the child empty, just keep original
                if not child_copy.keys:
                    parent.children.append(child)
                else:
                    parent.children.append(child_copy)

            parents.append(parent)
            i += len(group)

        current_level = parents

    tree.root = current_level[0]
    return tree


def _sol_range_query(tree, lo, hi):
    results = []

    def _range(node, lo, hi):
        i = 0
        # Skip keys less than lo
        while i < len(node.keys) and node.keys[i] < lo:
            # But still check the child — it might have keys in range
            if not node.leaf:
                _range(node.children[i], lo, hi)
            i += 1

        # Collect keys in range
        while i < len(node.keys) and node.keys[i] <= hi:
            if not node.leaf:
                _range(node.children[i], lo, hi)
            results.append(node.keys[i])
            i += 1

        # Check the rightmost relevant child
        if not node.leaf and i <= len(node.children) - 1:
            # Only if there might be keys in range in this subtree
            if i < len(node.keys) or (i > 0 and node.keys[i - 1] <= hi):
                _range(node.children[i], lo, hi)

    _range(tree.root, lo, hi)
    return sorted(results)


def _sol_verify_btree(tree):
    t = tree.t

    # Check empty tree
    if not tree.root.keys:
        return (True, "Valid B-tree (empty)")

    # Check root key count
    if len(tree.root.keys) > 2 * t - 1:
        return (False, f"Root has {len(tree.root.keys)} keys, max is {2 * t - 1}")

    # Collect leaf depths
    leaf_depths = []
    errors = []

    def check(node, depth, is_root):
        # Keys must be sorted
        for i in range(len(node.keys) - 1):
            if node.keys[i] >= node.keys[i + 1]:
                errors.append(f"Keys not sorted in node: {node.keys}")
                return

        # Key count bounds
        if not is_root:
            if len(node.keys) < t - 1:
                errors.append(f"Node has {len(node.keys)} keys, min is {t - 1}: {node.keys}")
                return
        if len(node.keys) > 2 * t - 1:
            errors.append(f"Node has {len(node.keys)} keys, max is {2 * t - 1}: {node.keys}")
            return

        if node.leaf:
            leaf_depths.append(depth)
        else:
            # Internal node must have len(keys)+1 children
            if len(node.children) != len(node.keys) + 1:
                errors.append(
                    f"Node has {len(node.keys)} keys but {len(node.children)} children: {node.keys}")
                return

            # Check ordering: child[i] < keys[i] < child[i+1]
            for i, child in enumerate(node.children):
                # All keys in child[i] must be < keys[i] (if i < len(keys))
                if i < len(node.keys):
                    for ck in child.keys:
                        if ck >= node.keys[i]:
                            errors.append(
                                f"Child key {ck} >= parent key {node.keys[i]}")
                            return
                # All keys in child[i] must be > keys[i-1] (if i > 0)
                if i > 0:
                    for ck in child.keys:
                        if ck <= node.keys[i - 1]:
                            errors.append(
                                f"Child key {ck} <= parent key {node.keys[i - 1]}")
                            return

                check(child, depth + 1, False)
                if errors:
                    return

    check(tree.root, 0, True)

    if errors:
        return (False, errors[0])

    if len(set(leaf_depths)) > 1:
        return (False, f"Leaves at different depths: {sorted(set(leaf_depths))}")

    return (True, "Valid B-tree")


def _sol_disk_io_compare(n, queries, t=100):
    # Build B-tree
    tree = BTree(t=t)
    for k in range(1, n + 1):
        tree.insert(k)

    # Count disk reads for each query using path tracing
    btree_reads = []
    for q in queries:
        path = _sol_search_path(tree, q)
        btree_reads.append(len(path))

    btree_total = sum(btree_reads)
    btree_avg = btree_total / len(queries) if queries else 0

    # BST comparison: balanced BST has depth ceil(log2(n+1))
    bst_depth = math.ceil(math.log2(n + 1)) if n > 0 else 0
    bst_total = bst_depth * len(queries)
    bst_avg = bst_depth

    speedup = bst_avg / btree_avg if btree_avg > 0 else float('inf')

    return {
        "btree_total_reads": btree_total,
        "bst_total_reads": bst_total,
        "btree_avg": round(btree_avg, 2),
        "bst_avg": bst_avg,
        "speedup": round(speedup, 2),
    }


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0
    skipped = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  \u2713 {name}")
        else:
            failed += 1
            print(f"  \u2717 {name}: got {got}, expected {expected}")

    # Helper B-tree for exercises
    def make_tree(keys, t=3):
        tree = BTree(t=t)
        for k in keys:
            tree.insert(k)
        return tree

    # ── Exercise 1: Search with Path Tracing ──

    print("\nExercise 1: Search with Path Tracing")
    tree1 = make_tree([10, 20, 5, 6, 12, 30, 7, 17])
    result = search_path(tree1, 12)
    if result is None:
        skipped += 1
        print("  \u2b1c Not implemented")
    else:
        sol = _sol_search_path(tree1, 12)
        check("search_path finds 12", result[-1][1], True)
        check("search_path correct length", len(result), len(sol))

    result_miss = search_path(tree1, 99) if result is not None else None
    if result_miss is None and result is not None:
        pass  # already counted
    elif result_miss is not None:
        check("search_path misses 99", result_miss[-1][1], False)

    # ── Exercise 2: Bulk Load ──

    print("\nExercise 2: Bulk Load")
    sorted_data = list(range(1, 21))
    tree2 = bulk_load(sorted_data, t=3)
    if tree2 is None:
        skipped += 1
        print("  \u2b1c Not implemented")
    else:
        loaded_keys = sorted(tree2.traverse())
        check("bulk_load contains all keys", loaded_keys, sorted_data)
        # Verify it's a valid B-tree structure
        valid, msg = _sol_verify_btree(tree2)
        check(f"bulk_load produces valid B-tree: {msg}", valid, True)

    # ── Exercise 3: Range Query ──

    print("\nExercise 3: Range Query")
    tree3 = make_tree([1, 3, 5, 7, 9, 11, 13, 15, 17, 19])
    result3 = range_query(tree3, 5, 13)
    if result3 is None:
        skipped += 1
        print("  \u2b1c Not implemented")
    else:
        check("range_query [5,13]", result3, [5, 7, 9, 11, 13])
        check("range_query [1,3]", range_query(tree3, 1, 3), [1, 3])
        check("range_query [18,25]", range_query(tree3, 18, 25), [19])
        check("range_query [100,200]", range_query(tree3, 100, 200), [])

    # ── Exercise 4: Verify B-Tree Properties ──

    print("\nExercise 4: Verify B-Tree Properties")
    tree4 = make_tree(list(range(1, 30)), t=3)
    result4 = verify_btree(tree4)
    if result4 is None:
        skipped += 1
        print("  \u2b1c Not implemented")
    else:
        check("valid tree passes", result4[0], True)

        # Create an invalid tree (tamper with it)
        bad_tree = make_tree([1, 2, 3, 4, 5], t=2)
        bad_tree.root.keys.append(999)  # Violate key count or ordering
        result_bad = verify_btree(bad_tree)
        check("tampered tree fails", result_bad[0], False)

    # ── Exercise 5: Disk I/O Simulator ──

    print("\nExercise 5: Disk I/O Simulator")
    queries5 = [1, 250, 500, 750, 1000]
    result5 = disk_io_compare(1000, queries5, t=10)
    if result5 is None:
        skipped += 1
        print("  \u2b1c Not implemented")
    else:
        sol5 = _sol_disk_io_compare(1000, queries5, t=10)
        check("btree total reads", result5["btree_total_reads"], sol5["btree_total_reads"])
        check("bst total reads", result5["bst_total_reads"], sol5["bst_total_reads"])
        check("speedup > 1", result5["speedup"] > 1, True)
        print(f"  \u2139 B-tree avg: {result5['btree_avg']} reads, "
              f"BST avg: {result5['bst_avg']} reads, "
              f"Speedup: {result5['speedup']}x")

    # ── Summary ──

    print(f"\n{'=' * 50}")
    total = passed + failed + skipped
    print(f"Results: {passed} passed, {failed} failed, {skipped} not implemented")
    if skipped > 0:
        print(f"  ({skipped} exercise(s) still need your implementation)")


if __name__ == "__main__":
    print("=" * 60)
    print("Day 59: B-Tree Practice Exercises")
    print("=" * 60)
    run_tests()
