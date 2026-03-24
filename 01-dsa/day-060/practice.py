"""
Day 60 Practice: B+ Tree Exercises
====================================
Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from bplus_tree import BPlusTree, BPlusLeaf


# ─── Exercise 1: Range Count via Leaf Chain ───────────────────────
#
# Given a B+ tree and bounds (lo, hi), count the number of keys
# in [lo, hi] using ONLY the leaf chain. Do NOT traverse the tree
# structure recursively — navigate to the starting leaf, then walk
# the linked list.
#
# Why: this is exactly how a database answers COUNT(*) WHERE col
# BETWEEN lo AND hi using an index scan.
#
# Example:
#   tree has keys [1, 5, 10, 15, 20, 25, 30]
#   range_count(tree, 10, 25) → 4  (keys: 10, 15, 20, 25)

def range_count(tree, lo, hi):
    # TODO: use tree._find_leaf(lo) to get starting leaf,
    #       then walk leaf.next_leaf chain counting keys in [lo, hi]
    pass


# ─── Exercise 2: Bulk Load from Sorted Data ──────────────────────
#
# Build a B+ tree bottom-up from already-sorted (key, value) pairs.
# This is much faster than repeated inserts:
#   1. Pack keys into leaf nodes (each leaf gets `order` keys, except last)
#   2. Link the leaves together
#   3. Build internal nodes layer by layer from the leaf level up
#
# Real databases use this for CREATE INDEX on existing data —
# sort the data first, then bulk-load the B+ tree.
#
# Example:
#   data = [(1,"a"), (2,"b"), (3,"c"), (4,"d"), (5,"e"), (6,"f")]
#   tree = bulk_load(data, order=3)
#   tree.traverse() → [(1,"a"), (2,"b"), (3,"c"), (4,"d"), (5,"e"), (6,"f")]

def bulk_load(sorted_data, order=4):
    # TODO: build a B+ tree bottom-up
    # 1. Create leaf nodes, packing `order-1` keys per leaf (leave room)
    #    Actually, pack leaves to their natural fill — up to order-1 keys
    # 2. Link leaves via next_leaf
    # 3. Build internal levels: for each pair of children, promote separator
    # Return the BPlusTree
    pass


# ─── Exercise 3: Predecessor and Successor ───────────────────────
#
# Find the predecessor (largest key < given key) and successor
# (smallest key > given key) using the B+ tree structure.
#
# Why: databases use this for queries like "find the row just before/
# after this value" — e.g., pagination with WHERE id > last_seen LIMIT 1.
#
# Example:
#   tree has keys [5, 10, 15, 20, 25]
#   find_predecessor(tree, 15) → 10
#   find_successor(tree, 15) → 20
#   find_predecessor(tree, 5) → None  (no key < 5)

def find_predecessor(tree, key):
    # TODO: find the largest key strictly less than `key`
    pass

def find_successor(tree, key):
    # TODO: find the smallest key strictly greater than `key`
    pass


# ─── Exercise 4: SQL Index Simulation ────────────────────────────
#
# Given a "table" (list of dicts representing rows), build a B+ tree
# index on a specified column and answer range queries.
#
# Simulates: CREATE INDEX idx ON users(age);
#            SELECT * FROM users WHERE age BETWEEN 25 AND 35;
#
# Example:
#   table = [
#       {"id": 1, "name": "Alice", "age": 30},
#       {"id": 2, "name": "Bob", "age": 22},
#       {"id": 3, "name": "Carol", "age": 35},
#       {"id": 4, "name": "Dave", "age": 28},
#   ]
#   index, indexed_table = build_index(table, "age")
#   query_range(index, indexed_table, 25, 35)
#   → [{"id": 4, ...age:28}, {"id": 1, ...age:30}, {"id": 3, ...age:35}]
#     (sorted by age because the index returns them in order)

def build_index(table, column, order=4):
    # TODO: build a B+ tree where key=row[column], value=row index
    # Return (tree, table) so query_range can look up rows
    pass

def query_range(index_tree, table, lo, hi):
    # TODO: use index_tree.range_query(lo, hi) to get row indices,
    # then return the actual rows from the table
    pass


# ─── Exercise 5: Amplification Factor ────────────────────────────
#
# Measure the "overhead" of B+ trees: how many keys are stored in
# internal nodes (as separator copies) vs leaf nodes (as actual data).
#
# The amplification factor = (internal keys) / (leaf keys).
# For large trees with high branching factor, this should be small.
#
# Example:
#   tree with 100 leaf keys and 15 internal separator keys
#   → amplification = 15 / 100 = 0.15 (15% overhead)

def measure_amplification(tree):
    # TODO: walk the tree and count:
    #   - total keys in leaf nodes
    #   - total keys in internal nodes (separator copies)
    # Return (leaf_keys, internal_keys, ratio)
    # ratio = internal_keys / leaf_keys (or 0.0 if leaf_keys == 0)
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_range_count(tree, lo, hi):
    """Walk the leaf chain from the leaf containing lo until we pass hi."""
    leaf = tree._find_leaf(lo)
    count = 0
    while leaf is not None:
        for k in leaf.keys:
            if k > hi:
                return count
            if k >= lo:
                count += 1
        leaf = leaf.next_leaf
    return count


def _sol_bulk_load(sorted_data, order=4):
    """Build a B+ tree bottom-up from sorted data."""
    if not sorted_data:
        return BPlusTree(order)

    # Maximum keys per leaf: order - 1 (leave room so we don't trigger split)
    max_keys = order - 1

    # Step 1: Create leaf nodes
    leaves = []
    for i in range(0, len(sorted_data), max_keys):
        chunk = sorted_data[i:i + max_keys]
        leaf = BPlusLeaf()
        leaf.keys = [kv[0] for kv in chunk]
        leaf.values = [kv[1] for kv in chunk]
        leaves.append(leaf)

    # Step 2: Link leaves
    for i in range(len(leaves) - 1):
        leaves[i].next_leaf = leaves[i + 1]

    # Step 3: Build internal nodes bottom-up
    if len(leaves) == 1:
        tree = BPlusTree(order)
        tree.root = leaves[0]
        return tree

    current_level = leaves
    from bplus_tree import BPlusInternal

    while len(current_level) > 1:
        next_level = []
        i = 0
        while i < len(current_level):
            node = BPlusInternal()
            # Take up to `order` children per internal node
            end = min(i + order, len(current_level))
            node.children = current_level[i:end]
            # Separator keys: first key of each child except the first
            for child in node.children:
                child.parent = node
            for j in range(1, len(node.children)):
                child = node.children[j]
                if child.is_leaf():
                    node.keys.append(child.keys[0])
                else:
                    # For internal children, use the smallest key reachable
                    c = child
                    while not c.is_leaf():
                        c = c.children[0]
                    node.keys.append(c.keys[0])
            next_level.append(node)
            i = end
        current_level = next_level

    tree = BPlusTree(order)
    tree.root = current_level[0]
    return tree


def _sol_find_predecessor(tree, key):
    """Find largest key strictly less than key."""
    leaf = tree._find_leaf(key)
    # Check current leaf for predecessor
    pred = None
    for k in leaf.keys:
        if k < key:
            pred = k

    if pred is not None:
        return pred

    # Need to go to previous leaf — walk from leftmost leaf
    # (In a full implementation we'd have prev_leaf pointers;
    # here we walk the chain from the start)
    node = tree.root
    while not node.is_leaf():
        node = node.children[0]

    best = None
    while node is not None:
        for k in node.keys:
            if k < key:
                best = k
            elif k >= key:
                return best
        node = node.next_leaf
    return best


def _sol_find_successor(tree, key):
    """Find smallest key strictly greater than key."""
    leaf = tree._find_leaf(key)
    # Check current leaf
    for k in leaf.keys:
        if k > key:
            return k
    # Walk to next leaves
    leaf = leaf.next_leaf
    while leaf is not None:
        if leaf.keys:
            return leaf.keys[0]
        leaf = leaf.next_leaf
    return None


def _sol_build_index(table, column, order=4):
    """Build a B+ tree index on a column."""
    tree = BPlusTree(order)
    for i, row in enumerate(table):
        tree.insert(row[column], i)
    return tree, table


def _sol_query_range(index_tree, table, lo, hi):
    """Use the index to answer a range query."""
    results = index_tree.range_query(lo, hi)
    rows = [table[row_idx] for _, row_idx in results]
    return rows


def _sol_measure_amplification(tree):
    """Count keys in internal vs leaf nodes."""
    leaf_keys = 0
    internal_keys = 0

    def walk(node):
        nonlocal leaf_keys, internal_keys
        if node.is_leaf():
            leaf_keys += len(node.keys)
        else:
            internal_keys += len(node.keys)
            for child in node.children:
                walk(child)

    walk(tree.root)
    ratio = internal_keys / leaf_keys if leaf_keys > 0 else 0.0
    return (leaf_keys, internal_keys, ratio)


# ─── Test Runner ────────────────────────────────────────────────────

def _build_test_tree(keys=None, order=4):
    """Helper to build a tree for testing."""
    if keys is None:
        keys = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    tree = BPlusTree(order)
    for k in keys:
        tree.insert(k, f"v{k}")
    return tree


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

    # ── Exercise 1: Range Count ──
    print("\nExercise 1: Range Count via Leaf Chain")
    tree1 = _build_test_tree()
    for fn_name, fn in [("yours", range_count), ("solution", _sol_range_count)]:
        result = fn(tree1, 10, 30)
        if fn_name == "yours" and result is None:
            print("  \u2b1c Not implemented yet")
            skipped += 1
            break
        check(f"{fn_name}: count [10,30]", result, 5)
        check(f"{fn_name}: count [1,100]", fn(tree1, 1, 100), 10)
        check(f"{fn_name}: count [25,25]", fn(tree1, 25, 25), 1)
        check(f"{fn_name}: count [26,29]", fn(tree1, 26, 29), 0)

    # ── Exercise 2: Bulk Load ──
    print("\nExercise 2: Bulk Load from Sorted Data")
    data = [(i, f"v{i}") for i in range(1, 21)]
    for fn_name, fn in [("yours", bulk_load), ("solution", _sol_bulk_load)]:
        result = fn(data, order=4)
        if fn_name == "yours" and result is None:
            print("  \u2b1c Not implemented yet")
            skipped += 1
            break
        all_kv = result.traverse()
        check(f"{fn_name}: all keys present", [k for k, v in all_kv], list(range(1, 21)))
        check(f"{fn_name}: search(10)", result.search(10), "v10")
        rq = result.range_query(5, 15)
        check(f"{fn_name}: range [5,15]", [k for k, v in rq], [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

    # ── Exercise 3: Predecessor / Successor ──
    print("\nExercise 3: Predecessor and Successor")
    tree3 = _build_test_tree()
    for fn_name, fn_pred, fn_succ in [
        ("yours", find_predecessor, find_successor),
        ("solution", _sol_find_predecessor, _sol_find_successor),
    ]:
        pred = fn_pred(tree3, 25)
        if fn_name == "yours" and pred is None and fn_succ(tree3, 5) is None:
            print("  \u2b1c Not implemented yet")
            skipped += 1
            break
        check(f"{fn_name}: pred(25)", pred, 20)
        check(f"{fn_name}: succ(25)", fn_succ(tree3, 25), 30)
        check(f"{fn_name}: pred(5)", fn_pred(tree3, 5), None)
        check(f"{fn_name}: succ(50)", fn_succ(tree3, 50), None)
        check(f"{fn_name}: succ(5)", fn_succ(tree3, 5), 10)

    # ── Exercise 4: SQL Index Simulation ──
    print("\nExercise 4: SQL Index Simulation")
    table = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 22},
        {"id": 3, "name": "Carol", "age": 35},
        {"id": 4, "name": "Dave", "age": 28},
        {"id": 5, "name": "Eve", "age": 31},
    ]
    for fn_name, fn_build, fn_query in [
        ("yours", build_index, query_range),
        ("solution", _sol_build_index, _sol_query_range),
    ]:
        result = fn_build(table, "age")
        if fn_name == "yours" and result is None:
            print("  \u2b1c Not implemented yet")
            skipped += 1
            break
        idx, tbl = result
        rows = fn_query(idx, tbl, 25, 32)
        ages = [r["age"] for r in rows]
        check(f"{fn_name}: ages in [25,32]", ages, [28, 30, 31])
        names = [r["name"] for r in rows]
        check(f"{fn_name}: names in [25,32]", names, ["Dave", "Alice", "Eve"])

    # ── Exercise 5: Amplification Factor ──
    print("\nExercise 5: Amplification Factor")
    tree5 = BPlusTree(order=4)
    for i in range(1, 101):
        tree5.insert(i, f"v{i}")
    for fn_name, fn in [("yours", measure_amplification), ("solution", _sol_measure_amplification)]:
        result = fn(tree5)
        if fn_name == "yours" and result is None:
            print("  \u2b1c Not implemented yet")
            skipped += 1
            break
        leaf_k, internal_k, ratio = result
        check(f"{fn_name}: leaf_keys", leaf_k, 100)
        check(f"{fn_name}: internal_keys > 0", internal_k > 0, True)
        check(f"{fn_name}: ratio < 1.0", ratio < 1.0, True)
        print(f"        Leaf keys: {leaf_k}, Internal keys: {internal_k}, Ratio: {ratio:.3f}")
        print(f"        → {ratio * 100:.1f}% overhead from separator key duplication")

    # ── Summary ──
    print(f"\n{'=' * 50}")
    total = passed + failed + skipped
    print(f"Results: {passed} passed, {failed} failed, {skipped} not implemented")
    if skipped > 0:
        print(f"\nFill in the TODO stubs above, then run again!")
    if failed == 0 and skipped == 0:
        print(f"\nAll exercises complete!")


if __name__ == "__main__":
    run_tests()
