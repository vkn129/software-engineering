"""
Day 54 Practice: Radix Tree Exercises
======================================
Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from radix_tree import RadixTree

# Also import basic trie for comparison
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-053'))
from trie import Trie


# ─── Exercise 1: IP Longest Prefix Match ───────────────────────────
#
# Given a routing table as a list of (prefix, next_hop) pairs,
# find the longest matching prefix for an IP address.
# IP addresses are strings like "192.168.1.1"
#
# Example:
#   routes = [("192.168", "A"), ("192.168.1", "B"), ("10", "C")]
#   lookup("192.168.1.100") → "B" (longest match = "192.168.1")
#   lookup("192.168.2.1")   → "A" (longest match = "192.168")

def build_routing_table(routes):
    # TODO: build a radix tree from routes, return the tree
    pass

def ip_lookup(tree, ip):
    # TODO: return next_hop for longest matching prefix
    pass


# ─── Exercise 2: Memory Comparison ─────────────────────────────────
#
# Given a list of words, compare the node count of a basic trie vs
# a radix tree. Return (trie_nodes, radix_nodes, compression_ratio).
#
# This quantifies the memory savings from compression.

def compare_memory(words):
    # TODO: return (trie_node_count, radix_node_count, ratio)
    pass


# ─── Exercise 3: Radix Tree from Sorted Keys ───────────────────────
#
# Given sorted keys, build a radix tree. Verify that inserting in
# sorted order produces the same tree as inserting in random order.
# Return True if all_keys() matches for both.

def verify_order_independence(keys):
    # TODO: return True if sorted and shuffled insertion give same keys
    pass


# ─── Exercise 4: Prefix Frequency Map ──────────────────────────────
#
# Build a radix tree where each key has a frequency count.
# Support: increment(key), top_by_prefix(prefix, k) → top k keys by frequency.
#
# This is the core of search query suggestion systems.

class PrefixFrequencyMap:
    def __init__(self):
        # TODO: initialize
        pass

    def increment(self, key):
        # TODO: increment frequency of key
        pass

    def top_by_prefix(self, prefix, k=5):
        # TODO: return top k keys by frequency matching prefix
        pass


# ─── Exercise 5: Shared Prefix Analysis ────────────────────────────
#
# Given a list of strings, compute stats about prefix sharing:
# - Total characters across all strings
# - Characters saved by prefix compression (shared prefix chars)
# - Compression percentage
# Return (total_chars, saved_chars, pct_saved)

def prefix_sharing_stats(strings):
    # TODO: implement
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_build_routing_table(routes):
    tree = RadixTree()
    for prefix, next_hop in routes:
        tree.insert(prefix, next_hop)
    return tree

def _sol_ip_lookup(tree, ip):
    node = tree.root
    best_hop = None
    i = 0

    while i < len(ip):
        found = False
        for label, child in node.children.items():
            plen = min(len(label), len(ip) - i)
            if label[:plen] == ip[i:i + plen]:
                if child.is_end:
                    best_hop = child.value
                if plen < len(label):
                    return best_hop
                node = child
                i += len(label)
                found = True
                break
        if not found:
            break

    if node.is_end:
        best_hop = node.value
    return best_hop


def _sol_compare_memory(words):
    # Count trie nodes
    t = Trie()
    for w in words:
        t.insert(w)
    trie_count = [0]
    def count_trie(node):
        trie_count[0] += 1
        for c in node.children.values():
            count_trie(c)
    count_trie(t.root)

    # Count radix nodes
    rt = RadixTree()
    for w in words:
        rt.insert(w)
    radix_count = rt.node_count()

    ratio = trie_count[0] / radix_count if radix_count > 0 else 0
    return trie_count[0], radix_count, round(ratio, 2)


def _sol_verify_order_independence(keys):
    import random
    rt1 = RadixTree()
    for k in sorted(keys):
        rt1.insert(k)

    rt2 = RadixTree()
    shuffled = list(keys)
    random.shuffle(shuffled)
    for k in shuffled:
        rt2.insert(k)

    return rt1.all_keys() == rt2.all_keys()


class _SolPrefixFrequencyMap:
    def __init__(self):
        self.tree = RadixTree()
        self.freq = {}

    def increment(self, key):
        self.freq[key] = self.freq.get(key, 0) + 1
        self.tree.insert(key, self.freq[key])

    def top_by_prefix(self, prefix, k=5):
        keys = self.tree.keys_with_prefix(prefix)
        pairs = [(key, self.freq.get(key, 0)) for key in keys]
        pairs.sort(key=lambda x: -x[1])
        return [(key, freq) for key, freq in pairs[:k]]


def _sol_prefix_sharing_stats(strings):
    if not strings:
        return 0, 0, 0.0

    total_chars = sum(len(s) for s in strings)

    # Build radix tree and count edge label characters
    rt = RadixTree()
    for s in strings:
        rt.insert(s)

    edge_chars = [0]
    def count_edges(node):
        for label, child in node.children.items():
            edge_chars[0] += len(label)
            count_edges(child)
    count_edges(rt.root)

    saved = total_chars - edge_chars[0]
    pct = round(saved / total_chars * 100, 1) if total_chars > 0 else 0
    return total_chars, saved, pct


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1
    print("\nExercise 1: IP Longest Prefix Match")
    routes = [("192.168", "A"), ("192.168.1", "B"), ("10", "C")]
    for build_fn, lookup_fn in [(build_routing_table, ip_lookup), (_sol_build_routing_table, _sol_ip_lookup)]:
        tree = build_fn(routes)
        if tree is None:
            print("  (skipped — not implemented)")
            break
        r = lookup_fn(tree, "192.168.1.100")
        if r is None and lookup_fn is ip_lookup:
            print("  (skipped — not implemented)")
            break
        check(f"{lookup_fn.__name__}(192.168.1.100)", r, "B")
        check(f"{lookup_fn.__name__}(192.168.2.1)", lookup_fn(tree, "192.168.2.1"), "A")
        check(f"{lookup_fn.__name__}(10.0.0.1)", lookup_fn(tree, "10.0.0.1"), "C")

    # Exercise 2
    print("\nExercise 2: Memory Comparison")
    words = ["romane", "romanus", "romulus", "rubens", "ruber", "rubicon"]
    for fn in [compare_memory, _sol_compare_memory]:
        if fn is compare_memory and fn(words) is None:
            print("  (skipped — not implemented)")
            break
        t, r, ratio = fn(words)
        check(f"{fn.__name__} trie > radix", t > r, True)
        check(f"{fn.__name__} ratio > 1", ratio > 1, True)

    # Exercise 3
    print("\nExercise 3: Order Independence")
    for fn in [verify_order_independence, _sol_verify_order_independence]:
        if fn is verify_order_independence and fn(["a", "b"]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}", fn(["apple", "app", "bat", "bar", "baz"]), True)

    # Exercise 4
    print("\nExercise 4: Prefix Frequency Map")
    for Cls in [PrefixFrequencyMap, _SolPrefixFrequencyMap]:
        pf = Cls()
        if not hasattr(pf, 'increment'):
            print("  (skipped — not implemented)")
            break
        pf.increment("search")
        pf.increment("search")
        pf.increment("sell")
        r = pf.top_by_prefix("se", 2)
        if r is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} top", r[0], ("search", 2))

    # Exercise 5
    print("\nExercise 5: Prefix Sharing Stats")
    for fn in [prefix_sharing_stats, _sol_prefix_sharing_stats]:
        if fn is prefix_sharing_stats and fn(["a"]) is None:
            print("  (skipped — not implemented)")
            break
        total, saved, pct = fn(["international", "internet", "internal"])
        check(f"{fn.__name__} saved > 0", saved > 0, True)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
