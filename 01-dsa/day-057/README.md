# Day 57: Segment Trees — O(log n) Range Queries and Updates

## Why This Exists

You need to answer range queries on an array: "what's the sum of elements from index 3 to 7?" The naive approach scans the range in O(n). Prefix sums bring queries down to O(1), but there's a catch: when an element changes, you must rebuild the entire prefix sum array in O(n).

This is the **forcing function** for segment trees: when you need *both* range queries and point updates to be fast, prefix sums and brute force each sacrifice one operation. A segment tree gives O(log n) for both.

| Approach | Range Query | Point Update | Range Update |
|----------|-------------|--------------|--------------|
| Brute force | O(n) | O(1) | O(n) |
| Prefix sums | O(1) | O(n) | O(n) |
| **Segment tree** | **O(log n)** | **O(log n)** | O(n log n) |
| **Segment tree + lazy** | **O(log n)** | **O(log n)** | **O(log n)** |

## Theory (40 min)

### Tree Structure

A segment tree is a **complete binary tree** stored in a flat array (like a heap). Each node stores the aggregate (sum, min, max, etc.) of a range of the original array.

```
Array: [2, 1, 5, 3, 4]

                  [15]              range [0,4] — root stores total sum
                /      \
            [8]          [7]        [0,2] and [3,4]
           /   \        /   \
        [3]     [5]   [3]   [4]    [0,1], [2,2], [3,3], [4,4]
       /   \
    [2]     [1]                     [0,0] and [1,1] — leaves = original values
```

**Key insight**: leaves hold original array values. Each internal node holds the aggregate of its two children. The root holds the aggregate of the entire array.

### Array Layout

Using 1-indexed array (like heaps):
- **Root** at index 1
- **Left child** of node `i` at `2*i`
- **Right child** of node `i` at `2*i + 1`
- **Parent** of node `i` at `i // 2`

We allocate `4 * n` space to handle any array size safely (a complete binary tree on n leaves needs at most `2 * 2^(ceil(log2(n)))` nodes).

### Build: O(n)

Build bottom-up: set leaves to array values, then each internal node = merge(left_child, right_child). Despite the tree having O(n) nodes, we visit each exactly once.

### Query: O(log n)

To query range [l, r], start at the root and recurse:
- If the node's range is **completely inside** [l, r]: return its value
- If the node's range is **completely outside** [l, r]: return identity
- Otherwise: **split** — query both children and merge results

At each level of the tree, at most 2 nodes are "partially overlapping" (one on the left boundary, one on the right). So we visit O(log n) nodes total.

### Point Update: O(log n)

Update a leaf, then walk up to the root, recomputing each ancestor. Only O(log n) ancestors exist.

### Lazy Propagation — The Deferred Work Trick

Without lazy propagation, a range update (add 5 to all elements in [2, 7]) requires updating each element individually: O(n log n) in the worst case.

**Lazy propagation** defers updates: instead of pushing a change all the way to the leaves, we store it at the highest node whose range is fully covered by the update range. When a future query or update needs to go deeper, we **push down** the lazy value to the children first.

This is the same principle as copy-on-write in operating systems: don't do work until someone actually needs the result.

```
range_update(0, 4, +3):
  Node [0,4] gets lazy = 3, value += 3 * 5 = 15
  Children are NOT updated yet

query(2, 3):
  Need to descend through [0,4] → push lazy down to children
  [0,2].lazy += 3, [0,2].value += 3 * 3 = 9
  [3,4].lazy += 3, [3,4].value += 3 * 2 = 6
  [0,4].lazy = 0
  Continue query normally
```

Result: O(log n) for both range updates and range queries.

## Real Uses

- **Competitive programming**: The workhorse data structure for range query problems
- **Database engines**: Range aggregations (SUM, MIN, MAX) over indexed columns
- **Computational geometry**: Sweepline algorithms for rectangle union area, closest pair
- **Graphics**: Interval scheduling, visibility determination
- **Network monitoring**: Aggregate statistics over time windows with live updates

## Practice (20 min)

See `practice.py` — 5 exercises from range minimum queries to persistent segment trees.

## Daily Project

`segment_tree.py` implements both a basic SegmentTree and a LazySegmentTree with full range update/query support.

## Checkpoint Questions

1. Why do we allocate 4*n space instead of 2*n for the segment tree array? What goes wrong with 2*n when n is not a power of 2?
2. During a range query, why are at most O(log n) nodes visited even though the query range could span most of the array?
3. Lazy propagation defers work — what invariant must hold for the tree to still return correct answers before lazy values are pushed down?
4. Can you use a segment tree for range GCD queries? What's the merge operation, and does it need an identity element?
5. Why can't you use lazy propagation with a range minimum tree for "set all elements in [l,r] to value v" as easily as for "add v to all elements in [l,r]"? (Hint: you actually can, but the push-down logic differs — how?)
6. A Fenwick tree (BIT) also does range sum + point update in O(log n) with much less code. When would you still choose a segment tree over a BIT?
