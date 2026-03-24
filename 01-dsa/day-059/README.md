# Day 59: B-Trees — Why Databases Don't Use Binary Trees

## Why This Exists

Binary search trees are designed for RAM, where every comparison costs ~1 CPU cycle (~1 nanosecond). But databases live on disk, where every page read costs ~10 milliseconds — **ten million times slower**. A BST with 1 million keys needs ~20 levels, meaning ~20 disk reads per lookup. At 10ms each, that's 200ms for a single query. Unacceptable.

B-trees solve this by **packing hundreds or thousands of keys into each node**, sized to match a disk page (4KB-16KB). A B-tree of order 1000 holding 1 million keys needs only ~2 levels. Two disk reads. 20ms instead of 200ms.

This is not a theoretical curiosity. **Every major filesystem and database uses B-trees:**
- **Filesystems**: ext4, NTFS, HFS+, APFS, Btrfs (literally named after B-trees)
- **Databases**: SQLite, MySQL InnoDB, PostgreSQL, Oracle, SQL Server
- **Key-value stores**: LMDB, BoltDB, WiredTiger (MongoDB)

The forcing function is physics: rotational latency and seek time on HDDs, page-granularity reads on SSDs. The data structure must match the hardware.

## Theory (40 min)

### Properties

A B-tree of minimum degree `t` (where `t >= 2`):

1. **Every node** has at most `2t - 1` keys and `2t` children
2. **Every non-root node** has at least `t - 1` keys
3. **The root** has at least 1 key (unless tree is empty)
4. **All leaves** are at the same depth (perfect balance)
5. A node with `k` keys has exactly `k + 1` children (if not a leaf)
6. Keys within a node are sorted; child `i` contains keys between `key[i-1]` and `key[i]`

### Why Minimum Degree t?

`t` controls the branching factor. With `t = 1000`:
- Each node holds 999 to 1999 keys
- Each internal node has 1000 to 2000 children
- Node size ~= disk page size (8KB-16KB)
- Tree height for n keys: `O(log_t n)`

| n keys | BST depth (log2) | B-tree depth (t=1000) |
|--------|-------------------|-----------------------|
| 1,000 | 10 | 1 |
| 1,000,000 | 20 | 2 |
| 1,000,000,000 | 30 | 3 |

### Operations

| Operation | Time Complexity | Disk I/O |
|-----------|----------------|----------|
| search | O(t * log_t n) | O(log_t n) |
| insert | O(t * log_t n) | O(log_t n) |
| delete | O(t * log_t n) | O(log_t n) |

Within each node, we do O(t) work scanning keys (linear scan or binary search). But the number of nodes visited is O(log_t n), and disk I/O is the bottleneck.

### Insert with Proactive Splitting

The naive approach: insert at a leaf, then split upward if the leaf is full. Problem: splits can cascade all the way to the root, requiring **two passes** (down to find the leaf, up to fix splits).

**Proactive splitting** (Cormen et al.): split every full node **on the way down**. When descending to find the insertion point, if we encounter a full node (2t-1 keys), split it immediately — before entering it. This guarantees that when we reach the leaf, it has room. **Single pass, top-down, no backtracking.**

Why this matters in practice: a single downward pass means we can release locks on parent nodes as we descend, enabling better concurrency in database systems.

### Split Operation

Splitting a full child `y` of node `x` at index `i`:
1. Create new node `z` with the upper `t-1` keys of `y`
2. Move the **median key** of `y` up into `x` at position `i`
3. `y` keeps only its lower `t-1` keys
4. Fix child pointers: `z` gets `y`'s upper `t` children

```
Before split (t=3, full child has 5 keys):
  x: [... M ...]
       |
  y: [A B C D E]     ← full (2t-1 = 5 keys)

After split:
  x: [... C M ...]   ← median C promoted
       |   |
  y: [A B] z: [D E]  ← split into two nodes with t-1 = 2 keys each
```

### B-trees vs Red-Black Trees

Both are balanced. The difference is **what they optimize for**:

| Property | Red-Black Tree | B-Tree |
|----------|---------------|--------|
| Balance | O(log2 n) height | O(log_t n) height |
| Optimized for | Comparisons (RAM) | Block I/O (disk) |
| Keys per node | 1 | t-1 to 2t-1 |
| Branching factor | 2 | t to 2t |
| Use case | In-memory maps/sets | Databases, filesystems |
| Rotation/split | O(1) rotations | O(t) per split |

Red-black trees are actually a special case: a red-black tree is isomorphic to a 2-3-4 tree (B-tree with t=2).

## Practice (20 min)

See `practice.py` — 5 exercises from path tracing to disk I/O simulation.

## Daily Project

`btree.py` implements a B-tree with insert (proactive splitting), search, in-order traversal, and visualization.

## Checkpoint Questions

1. Why does a B-tree pack multiple keys per node instead of one key like a BST?
2. What is the minimum degree `t` and how does it relate to disk page size?
3. Why does proactive splitting (split-on-descent) avoid the need for a second pass up the tree?
4. A B-tree with t=500 and 1 billion keys — what is the maximum height? How many disk reads for a search?
5. Why are all leaves at the same depth? What invariant during insertion maintains this?
6. How is a red-black tree related to a B-tree with t=2?
