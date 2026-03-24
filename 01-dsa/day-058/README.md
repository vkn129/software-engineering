# Day 58: Fenwick Trees (Binary Indexed Trees) — Prefix Sums in O(log n)

## Why This Exists

You have an array and need to answer prefix sum queries while also updating individual elements. A naive approach: precompute a prefix sum array for O(1) queries, but every update requires O(n) to rebuild. A segment tree solves both in O(log n), but it uses 4n space and requires ~100 lines of code with lazy propagation.

A **Fenwick tree** (Binary Indexed Tree / BIT) does the same thing — O(log n) prefix queries and O(log n) point updates — with **half the memory** (exactly n+1 slots) and code so short you can write it from memory in a contest.

The trade-off: Fenwick trees only work for **invertible operations** (addition, XOR). You can compute `sum(l, r)` because `sum(l, r) = prefix(r) - prefix(l-1)` — subtraction undoes addition. But `min(l, r)` cannot be derived from prefix mins, because min has no inverse. For non-invertible operations, you still need a segment tree.

## The Key Insight: Bit Manipulation Determines Ranges

Every index `i` in the Fenwick array stores the sum of a specific range of the original array. The range size equals the **lowest set bit** of `i`.

```
i & -i  extracts the lowest set bit of i
```

Why does this work? In two's complement, `-i` flips all bits of `i` and adds 1. The AND with the original keeps only the lowest bit that was set.

```
i = 12 = 1100 in binary
-i     = 0100 (flip → 0011, add 1 → 0100)
i & -i = 0100 = 4

So tree[12] stores the sum of 4 elements: arr[9..12]
```

### What each index covers

```
Index (binary)  | Lowest bit | Range stored
----------------|------------|------------------
  1  (0001)     |     1      | arr[1..1]
  2  (0010)     |     2      | arr[1..2]
  3  (0011)     |     1      | arr[3..3]
  4  (0100)     |     4      | arr[1..4]
  5  (0101)     |     1      | arr[5..5]
  6  (0110)     |     2      | arr[5..6]
  7  (0111)     |     1      | arr[7..7]
  8  (1000)     |     8      | arr[1..8]
```

### Prefix query: walk toward root

To get `prefix_sum(7)`, add up contributions by stripping the lowest set bit each step:

```
tree[7] (covers arr[7])    → 7 - (7 & -7) = 7 - 1 = 6
tree[6] (covers arr[5..6]) → 6 - (6 & -6) = 6 - 2 = 4
tree[4] (covers arr[1..4]) → 4 - (4 & -4) = 4 - 4 = 0  → stop
```

At most log2(n) steps because each step clears one bit.

### Point update: walk toward leaves' parents

To update index `3`, propagate upward by adding the lowest set bit:

```
tree[3]  → 3 + (3 & -3) = 3 + 1 = 4
tree[4]  → 4 + (4 & -4) = 4 + 4 = 8
tree[8]  → 8 + (8 & -8) = 8 + 8 = 16 → stop (> n)
```

### Building in O(n), NOT n * O(log n)

The naive build calls update() n times for O(n log n). The O(n) build exploits the parent relationship directly: after setting `tree[i]`, propagate its value to `tree[i + (i & -i)]` (its immediate parent) in a single pass.

## Range Sum via Prefix Difference

```
range_sum(l, r) = prefix_sum(r) - prefix_sum(l - 1)
```

This is why invertibility matters. For sum, subtraction gives us arbitrary range queries from prefix queries. For min, `prefix_min(r) - prefix_min(l-1)` is meaningless.

## Comparison with Segment Tree

| Property | Fenwick Tree | Segment Tree |
|----------|-------------|--------------|
| Memory | n + 1 | 2n to 4n |
| Code complexity | ~15 lines | ~50-100 lines |
| Prefix query | O(log n) | O(log n) |
| Point update | O(log n) | O(log n) |
| Arbitrary range query | O(log n) via difference | O(log n) directly |
| Operations supported | Invertible only (sum, XOR) | Any (sum, min, max, GCD) |
| Range update | With tricks (difference array) | Lazy propagation |
| 2D extension | Straightforward | Complex |
| Cache performance | Slightly better (flat array) | Worse (tree nodes) |

**Rule of thumb**: If the operation is invertible (especially sum), prefer Fenwick. Otherwise, use a segment tree.

## Real Uses

- **Competitive programming**: The go-to for prefix sum queries — fast to code, fast to run
- **Frequency tables**: Count elements in ranges for order statistics
- **Counting inversions**: How unsorted is an array? Process elements and count how many previously seen elements are larger
- **2D prefix sums with updates**: Extend naturally to 2D for matrix region queries
- **Coordinate compression**: Combine with value remapping for problems on large value ranges

## Practice (20 min)

See `practice.py` — 5 exercises from counting inversions to k-th smallest via binary search on the tree.

## Daily Project

`fenwick_tree.py` implements 1D and 2D Fenwick trees with O(n) build, visual demos of the bit structure, and an inversion counting application.

## Checkpoint Questions

1. Why does `i & -i` extract the lowest set bit? Explain in terms of two's complement.
2. Why can Fenwick trees handle sum queries but not min queries?
3. How does the O(n) build work, and why is it O(n) rather than O(n log n)?
4. How would you support range updates and point queries using a Fenwick tree? (Hint: difference array)
5. Why does a 2D Fenwick tree use O(log n * log m) per query instead of O(log(nm))?
6. When would you choose a segment tree over a Fenwick tree despite the extra complexity?
