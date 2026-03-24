# Day 49: Mini-Project — Ordered Key-Value Store with Range Queries

## Week 7 Capstone: BSTs, AVL Trees, and Balancing Meet the Real World

This is where the tree concepts from Days 43-48 come together. We build one of the most important data structures in databases, caches, and real-time systems: an **ordered key-value store** — the same abstraction behind Redis Sorted Sets (ZSET), database indexes, and time-series storage.

## Why Ordered Key-Value Stores Matter

A hash table gives you O(1) point lookups: "give me the value for key X." But it cannot answer:

- "Give me all keys between A and M" (range query)
- "What is the smallest key?" (min)
- "What key comes just before X?" (floor)
- "What is the 50th smallest key?" (rank/select)

These are **order-dependent queries**, and they require a data structure that maintains key ordering. Hash tables destroy ordering — that is the fundamental trade-off that makes them fast for point lookups but useless for range operations.

### Real Systems That Need This

| System | What It Stores | Why Order Matters |
|--------|---------------|-------------------|
| **Redis ZSET** | Members with scores | Leaderboards, top-N queries, score ranges |
| **Database B-Tree index** | Row pointers keyed by column value | `WHERE price BETWEEN 10 AND 50` |
| **Time-series DB** | Events keyed by timestamp | "All events in the last hour" |
| **LSM-tree memtable** | Key-value pairs before flush | Sorted merge into on-disk segments |
| **OS scheduler** | Tasks keyed by priority/deadline | Next task to run = min key |

### The Interface

An ordered key-value store supports two families of operations:

**Point operations** (same as a hash table):
- `put(key, value)` — insert or update
- `get(key)` — retrieve value
- `delete(key)` — remove key

**Order operations** (impossible with a hash table):
- `min_key()`, `max_key()` — extremes
- `floor(key)`, `ceil(key)` — nearest keys <= and >= a target
- `range_query(lo, hi)` — all key-value pairs in [lo, hi]
- `rank(key)` — number of keys strictly less than key
- `select(k)` — the kth smallest key (0-indexed)

The point operations need O(log n). The order operations also need O(log n) — plus O(k) for range queries returning k results. A hash table gives O(1) for point operations but O(n log n) for anything order-related (must sort all keys first).

## Why Hash Tables Cannot Do Range Queries

A hash table maps keys to buckets using a hash function: `bucket = hash(key) % num_buckets`. The hash function deliberately **destroys ordering** — keys "Alice" and "Bob" may land in buckets 7 and 2. To find all keys between "Alice" and "Charlie", you must scan every bucket: O(n).

```
Hash table bucket layout (no key ordering):
  Bucket 0: "Eve"
  Bucket 1: (empty)
  Bucket 2: "Bob"
  Bucket 3: "Dave"
  Bucket 4: (empty)
  Bucket 5: (empty)
  Bucket 6: (empty)
  Bucket 7: "Alice", "Charlie"   ← hash collision, not alphabetical proximity
```

A BST preserves key ordering in its structure:
```
           "Charlie"
          /         \
      "Bob"        "Eve"
      /               \
  "Alice"           "Dave"
```

In-order traversal gives sorted output. Range query [Bob, Eve] just walks the in-order sequence starting at "Bob" and stopping after "Eve": O(log n + k).

## Implementation Choices

Three data structures can back an ordered key-value store:

| Structure | Insert | Delete | Range | Rank/Select | Real-World Use |
|-----------|--------|--------|-------|-------------|----------------|
| **AVL Tree** | O(log n) | O(log n) | O(log n + k) | O(log n) with subtree sizes | Academic, Java TreeMap (Red-Black) |
| **Red-Black Tree** | O(log n) | O(log n) | O(log n + k) | O(log n) with augmentation | Linux kernel, Java, C++ std::map |
| **Skip List** | O(log n) avg | O(log n) avg | O(log n + k) | O(log n) with span counts | **Redis ZSET** |

### Why Redis Chose Skip Lists Over Balanced BSTs

Redis author Salvatore Sanfilippo (antirez) gave the reason directly:

1. **Simpler to implement.** A skip list is ~100 lines of code. A Red-Black tree with deletion is ~300+.
2. **Range queries are trivial.** Once you find the start node, you just walk forward pointers. No need for in-order traversal logic.
3. **Concurrent-friendly.** Skip list levels can be locked independently. BST rotations touch multiple nodes atomically.
4. **Same asymptotic complexity.** Both are O(log n) for all operations.

### Our Choice: AVL Tree

We use an AVL tree because:
- We just learned AVL trees (Days 45-47)
- It demonstrates that the same balancing concepts solve real problems
- We augment nodes with subtree sizes for O(log n) rank/select
- The height guarantee (≤ 1.44 log n) gives tight worst-case bounds

## Transaction Log for Crash Recovery

Real databases do not trust in-memory state alone. Every mutation is first appended to a **write-ahead log (WAL)** before being applied to the tree. If the process crashes:

1. On restart, replay the log from the beginning
2. Each log entry is a (operation, key, value) tuple
3. Replaying rebuilds the exact same tree state

Our implementation includes a simplified version:
- `log` list stores every put/delete operation
- `replay()` rebuilds the store from the log
- This is the same principle behind Redis AOF (Append Only File), PostgreSQL WAL, and every serious database

### Why Append-Only?

Appending to a file is the fastest durable write operation. It is sequential I/O (no seeking), and the OS can batch it efficiently. Updating the tree in-place on disk would require random I/O — orders of magnitude slower.

## Failure Modes

| Failure | What Happens | Mitigation |
|---------|-------------|------------|
| Unbalanced tree (bug in rotation) | O(n) operations instead of O(log n) | Height checks, invariant assertions |
| Crash before log flush | Lost operations | fsync after each write (slow but safe) |
| Crash during replay | Partial state | Idempotent operations, checksums |
| Memory exhaustion | OOM kill | Size limits, eviction policy |
| Key comparison failure | TypeError at runtime | Type-check keys or require homogeneous types |
| Concurrent modification | Corrupted tree structure | Locks, MVCC, or single-threaded (Redis approach) |

## Checkpoint Questions

Before implementing, answer these:

1. **Why can't you implement `range_query(lo, hi)` efficiently with a Python `dict`?** What would the time complexity be?

2. **If you have 1 million keys and want the 500th smallest, what is the complexity with (a) a sorted array, (b) a hash table, (c) an augmented AVL tree?**

3. **`floor("Charlie")` in a BST containing {"Alice", "Bob", "Dave", "Eve"} — trace the search path and explain why you go right at "Bob".**

4. **Why does Redis use a skip list instead of a Red-Black tree? Would an AVL tree be better or worse than Red-Black for Redis's use case?**

5. **If the transaction log has [put(A,1), put(B,2), delete(A), put(A,3)], what is the final state after replay? Why must the log be replayed in order?**

## Complexity Summary

| Operation | Our Implementation | Hash Table |
|-----------|-------------------|------------|
| `put` | O(log n) | O(1) amortized |
| `get` | O(log n) | O(1) amortized |
| `delete` | O(log n) | O(1) amortized |
| `min_key` | O(log n) | O(n) |
| `max_key` | O(log n) | O(n) |
| `floor` | O(log n) | O(n) |
| `ceil` | O(log n) | O(n) |
| `range_query` | O(log n + k) | O(n log n) |
| `rank` | O(log n) | O(n) |
| `select` | O(log n) | O(n log n) |

The hash table wins on point operations. The ordered store wins on everything else. Choose based on your query patterns.
