"""
Day 162 Practice: Consistent Hashing with Virtual Nodes

Implement TODOs, run: python practice.py
"""

import hashlib
import bisect
from collections import defaultdict


def _hash(key: str) -> int:
    return int.from_bytes(hashlib.md5(key.encode()).digest()[:4], "big")


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ===================================================================
# Exercise 1: Build a ring with vnodes
# ===================================================================
# Return (sorted_positions, position_to_node) after adding the nodes.

def build_ring(nodes, vnodes_per_node):
    """
    nodes: list of node ids
    vnodes_per_node: int
    Returns (sorted_positions, dict pos -> node)
    """
    # TODO: implement
    pass


def _sol_build_ring(nodes, vnodes_per_node):
    pos_to_node = {}
    for n in nodes:
        for i in range(vnodes_per_node):
            p = _hash(f"{n}#{i}")
            while p in pos_to_node:
                p = (p + 1) & 0xFFFFFFFF
            pos_to_node[p] = n
    return sorted(pos_to_node), pos_to_node


# ===================================================================
# Exercise 2: Lookup primary owner
# ===================================================================

def primary_owner(ring_positions, pos_to_node, key):
    """Return the node that owns `key` on the ring."""
    # TODO: implement
    pass


def _sol_primary_owner(ring_positions, pos_to_node, key):
    p = _hash(key)
    i = bisect.bisect_right(ring_positions, p)
    if i == len(ring_positions):
        i = 0
    return pos_to_node[ring_positions[i]]


# ===================================================================
# Exercise 3: Find R replicas (distinct physical nodes clockwise)
# ===================================================================

def find_replicas(ring_positions, pos_to_node, key, r):
    """Return list of r distinct nodes starting at hash(key), walking clockwise."""
    # TODO: implement
    pass


def _sol_find_replicas(ring_positions, pos_to_node, key, r):
    p = _hash(key)
    i = bisect.bisect_right(ring_positions, p) % len(ring_positions)
    seen = []
    steps = 0
    while len(seen) < r and steps < len(ring_positions):
        node = pos_to_node[ring_positions[i]]
        if node not in seen:
            seen.append(node)
        i = (i + 1) % len(ring_positions)
        steps += 1
    return seen


# ===================================================================
# Exercise 4: Measure load distribution
# ===================================================================

def load_counts(ring_positions, pos_to_node, keys):
    """Return dict node -> count of keys owned."""
    # TODO: implement
    pass


def _sol_load_counts(ring_positions, pos_to_node, keys):
    counts = defaultdict(int)
    for k in keys:
        counts[_sol_primary_owner(ring_positions, pos_to_node, k)] += 1
    return dict(counts)


# ===================================================================
# Exercise 5: Fraction of keys moved on node-join
# ===================================================================

def fraction_moved_on_join(old_nodes, new_node, vnodes_per_node, keys):
    """
    Build ring with old_nodes, then with old_nodes + [new_node].
    Return fraction of `keys` whose owner changed.
    """
    # TODO: implement
    pass


def _sol_fraction_moved_on_join(old_nodes, new_node, vnodes_per_node, keys):
    pos_a, map_a = _sol_build_ring(old_nodes, vnodes_per_node)
    pos_b, map_b = _sol_build_ring(old_nodes + [new_node], vnodes_per_node)
    moved = 0
    for k in keys:
        if _sol_primary_owner(pos_a, map_a, k) != _sol_primary_owner(pos_b, map_b, k):
            moved += 1
    return moved / len(keys)


# ===================================================================
# Exercise 6: Weighted vnodes
# ===================================================================
# Build a ring where each node has `weight[n] * vnodes_per_node` vnodes.

def build_weighted_ring(node_weights, vnodes_per_node):
    """
    node_weights: dict node -> integer weight
    Returns (sorted_positions, dict pos -> node)
    """
    # TODO: implement
    pass


def _sol_build_weighted_ring(node_weights, vnodes_per_node):
    pos_to_node = {}
    for n, w in node_weights.items():
        for i in range(vnodes_per_node * w):
            p = _hash(f"{n}#{i}")
            while p in pos_to_node:
                p = (p + 1) & 0xFFFFFFFF
            pos_to_node[p] = n
    return sorted(pos_to_node), pos_to_node


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} expected={expected} got={got}")
            failed += 1

    # Ex 1
    print("Exercise 1: build_ring")
    pos, mp = try_or_sol("build_ring", ["a", "b", "c"], 50)
    check("ring size = 150", len(pos), 150)
    check("sorted", pos == sorted(pos), True)
    check("all 3 nodes present", set(mp.values()), {"a", "b", "c"})

    # Ex 2
    print("\nExercise 2: primary_owner")
    owner = try_or_sol("primary_owner", pos, mp, "hello")
    check("owner is one of nodes", owner in {"a", "b", "c"}, True)
    # determinism
    check("deterministic", try_or_sol("primary_owner", pos, mp, "hello"), owner)

    # Ex 3
    print("\nExercise 3: find_replicas")
    reps = try_or_sol("find_replicas", pos, mp, "hello", 3)
    check("3 distinct replicas", len(set(reps)) == 3, True)
    check("3 replicas total", len(reps), 3)
    reps2 = try_or_sol("find_replicas", pos, mp, "world", 2)
    check("2 replicas", len(reps2), 2)

    # Ex 4
    print("\nExercise 4: load_counts")
    keys = [f"k{i}" for i in range(3000)]
    counts = try_or_sol("load_counts", pos, mp, keys)
    check("sum equals keys", sum(counts.values()), 3000)
    check("all 3 nodes", set(counts.keys()), {"a", "b", "c"})

    # Ex 5
    print("\nExercise 5: fraction_moved_on_join")
    frac = try_or_sol("fraction_moved_on_join",
                      ["a", "b", "c", "d"], "e", 150, keys)
    # Ideal ~ 1/5 = 0.20; allow [0.10, 0.30]
    check("fraction in [0.10, 0.30]", 0.10 < frac < 0.30, True)

    # Ex 6
    print("\nExercise 6: build_weighted_ring")
    pos_w, mp_w = try_or_sol("build_weighted_ring",
                              {"small": 1, "big": 4}, 50)
    check("ring size = 250", len(pos_w), 250)
    big_share = sum(1 for v in mp_w.values() if v == "big") / len(mp_w)
    check("big has ~80% of vnodes", 0.75 < big_share < 0.85, True)

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
