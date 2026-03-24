# Day 52: Advanced Heaps — Beyond Binary

## Why This Exists

Binary heaps are great, but they have a fundamental limitation: **decrease-key is O(n)** because you can't find an element by value — you'd need to scan the whole array. For algorithms like Dijkstra's that call decrease-key on every edge relaxation, this matters.

Three variants address different limitations:
- **D-ary heaps**: More children per node → shallower tree → faster sift-up but slower sift-down. Database buffer pool managers use 4-ary heaps because they hit fewer cache lines.
- **Indexed priority queues**: Track element positions so decrease-key is O(log n). Essential for Dijkstra and Prim.
- **Fibonacci heaps**: Amortized O(1) decrease-key. Theoretically optimal for dense-graph Dijkstra. In practice, the constant factors are too high — they're a teaching tool, not a production tool.

## Theory (40 min)

### D-ary Heaps

A d-ary heap is a complete d-ary tree (each node has up to d children) stored in an array.

```
d=4 heap:                Array indices:
         1                parent(i) = (i - 1) // d
      / | | \             child_k(i) = d * i + k + 1   (k = 0..d-1)
     3  5  2  8
    /|
   9 7
```

**Trade-off**: height = O(log_d n)
- Sift-up: O(log_d n) — fewer levels, so faster
- Sift-down: O(d · log_d n) — must compare with all d children at each level

Optimal d depends on the workload:
- More inserts than extracts → larger d (sift-up is cheaper)
- Dijkstra with binary heap: O((V+E) log V). With d=E/V: O(E log_{E/V} V)

### Indexed Priority Queue

An indexed PQ maps a key ID to its priority and tracks positions:

```
id_to_priority: {A: 5, B: 3, C: 8, D: 1}
heap:           [D, B, A, C]  (sorted by priority)
id_to_pos:      {A: 2, B: 1, C: 3, D: 0}
pos_to_id:      [D, B, A, C]
```

decrease_key(B, 0): look up B's position → sift up → update mappings. O(log n).

### Fibonacci Heap (Conceptual)

| Operation | Binary Heap | Fibonacci Heap |
|-----------|-------------|----------------|
| insert | O(log n) | O(1) amortized |
| find-min | O(1) | O(1) |
| extract-min | O(log n) | O(log n) amortized |
| decrease-key | O(n) or O(log n)* | **O(1) amortized** |
| merge | O(n) | O(1) |

*O(log n) with indexed PQ

The O(1) decrease-key makes Dijkstra's run in O(V log V + E) instead of O((V+E) log V). For dense graphs (E ≈ V²), this is significant.

In practice, Fibonacci heaps are slower than binary heaps for graphs up to millions of vertices due to high constant factors and poor cache behavior.

## Practice (20 min)

See `practice.py` — 5 exercises on d-ary heaps, indexed PQ, and comparative analysis.

## Daily Project

`advanced_heaps.py` implements a D-ary heap and an Indexed Priority Queue with full decrease-key support.

## Checkpoint Questions

1. For what ratio of insert vs extract-min operations does a 4-ary heap beat a binary heap?
2. Why does an indexed priority queue need both id_to_pos and pos_to_id mappings?
3. Why are Fibonacci heaps rarely used despite their superior theoretical bounds?
4. How does the choice of d in a d-ary heap affect Dijkstra's running time?
5. What's the relationship between decrease-key and Dijkstra's edge relaxation?
