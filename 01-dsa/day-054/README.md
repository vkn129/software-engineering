# Day 54: Compressed Tries & Radix Trees — Space Efficiency

## Why This Exists

A basic trie wastes memory on chains of single-child nodes. The word "internationalization" creates 20 nodes, most with just one child. A **radix tree** (Patricia trie) compresses these chains: instead of one node per character, an edge can store an entire string.

```
Basic trie for ["romane", "romanus", "romulus"]:
    r → o → m → a → n → e(end)
                    → u → s(end)
            → u → l → u → s(end)

Radix tree:
    rom ──┬── an ──┬── e(end)
          │        └── us(end)
          └── ulus(end)
```

3 internal nodes vs 13. This compression matters at scale:
- **Linux kernel routing**: radix trees store millions of IP routes. The kernel's `struct radix_tree_root` is one of the most performance-critical data structures in the kernel.
- **Redis**: uses a radix tree variant (rax) for key storage and cluster slot mapping.
- **Git**: object storage uses prefix-compressed structures.

## Theory (40 min)

### Compression Rules

1. Any chain of nodes where each node has exactly one child gets compressed into a single edge with a multi-character label.
2. Branching nodes (≥2 children) and end-of-key nodes are preserved.
3. On insert, if the new key diverges mid-edge, **split** the edge.

### Edge Split on Insert

```
Before insert("roman"):
    rom → ane(end)

After insert("roman"):
    rom → an ─┬─ e(end)
              └─ (end)  ← "roman" ends here
```

### Complexity

Same as basic trie — O(k) for all operations — but with much lower memory. In practice, memory usage is proportional to the total number of unique key bytes, not the number of characters across all keys.

## Practice (20 min)

See `practice.py` — 5 exercises on radix tree operations and memory comparison.

## Daily Project

`radix_tree.py` implements a compressed trie (radix tree) with insert, search, delete, and prefix operations.

## Checkpoint Questions

1. When does a radix tree degenerate to a basic trie? (When no two keys share a prefix.)
2. Why does the Linux kernel use radix trees for page cache lookup?
3. How does edge splitting work when inserting a key that diverges mid-edge?
4. What's the maximum number of nodes in a radix tree with n keys?
5. How does a radix tree compare to a hash table for IP routing?
