# Day 86: Union-Find (Disjoint Set Union)

## Why Union-Find Matters

Union-Find answers one question blazingly fast: **"Are these two things in the
same group?"** And lets you merge groups in near-constant time.

- **Kruskal's MST**: "Does adding this edge create a cycle?" = "Are u and v in the same component?"
- **Network connectivity**: "Can server A reach server B?" after link failures
- **Image processing**: connected component labeling in pixel grids
- **Social networks**: "Are users X and Y in the same friend cluster?"
- **Compilers**: type unification in Hindley-Milner type inference
- **Percolation**: "Does water flow from top to bottom?" (physics simulation)

Union-Find is deceptively simple — two arrays and two operations — but the
amortized analysis behind it is one of the deepest results in CS.

## The Data Structure

### Two Operations

1. **Find(x)**: Which group does x belong to? (Returns the group's representative/root)
2. **Union(x, y)**: Merge the groups containing x and y

### Naive Implementation (Forest of Trees)

Each element points to a parent. The root of each tree is the group representative.

```
parent = [0, 1, 2, 3, 4]    # everyone is their own root
       = [0, 0, 2, 2, 2]    # two groups: {0,1} and {2,3,4}
```

**Find**: follow parent pointers to root → O(n) worst case (tall tree)
**Union**: point one root to the other → O(1) after find

### Optimization 1: Union by Rank

Attach the shorter tree under the taller tree. This keeps trees shallow.

**Result**: tree height ≤ log(n), so Find is O(log n).

### Optimization 2: Path Compression

During Find, make every visited node point directly to the root.
Future finds on the same path become O(1).

```
Find(x):
    if parent[x] != x:
        parent[x] = Find(parent[x])    # path compression
    return parent[x]
```

### Combined: Near-Constant Time

With both optimizations, any sequence of m operations on n elements takes
**O(m × α(n))** time, where α is the inverse Ackermann function.

**α(n) ≤ 4** for any n up to 2^(2^(2^(2^16))) ≈ 10^19728.

For all practical purposes, each operation is **O(1)** amortized.

## The Inverse Ackermann Function

α(n) grows so slowly that it's effectively constant:

| n | α(n) |
|---|------|
| 1 | 0 |
| 2 | 1 |
| 4 | 2 |
| 16 | 3 |
| 65536 | 4 |
| 2^65536 | 5 |

You will never encounter a dataset where α(n) > 4. But the proof that
Union-Find achieves this bound (by Tarjan, 1975) is a masterwork of
amortized analysis.

## Variants

### Union by Size (Alternative to Rank)

Track subtree sizes instead of ranks. Attach smaller tree under larger.
Same O(α(n)) bound, but also lets you query component sizes.

### Weighted Union-Find

Track a "distance" or "weight" from each node to its root. Useful for:
- Relative positioning (node x is 3 units above its root)
- Maintaining offsets during merges

### Rollback (Offline Union-Find)

Don't use path compression — use union by rank only. This allows
"undo" operations by keeping a log of parent changes. Useful in
divide-and-conquer on queries.

## Applications Deep Dive

### Percolation

Given an n×n grid where each cell is open/blocked, does water flow from
top row to bottom row? Model as Union-Find:
- Each open cell is an element
- Union adjacent open cells
- Add virtual top/bottom nodes
- Percolates iff top and bottom are in the same component

### Kruskal's MST (Recap from Day 85)

```
for each edge (u, v, w) in sorted order:
    if Find(u) != Find(v):     # different components = no cycle
        Union(u, v)
        add to MST
```

Without Union-Find, cycle detection would require DFS per edge = O(E × V).
With Union-Find: O(E × α(V)) ≈ O(E).

## Real-World Usage

| System | Application | Why Union-Find |
|--------|------------|----------------|
| **Kruskal's MST** | Network design | Cycle detection in O(α(n)) |
| **Image processing** | Connected component labeling | Pixel grouping |
| **Compilers** | Type unification (ML, Haskell) | Merge type equivalence classes |
| **Physics engines** | Percolation simulation | Flow connectivity |
| **Databases** | Query optimization (equivalence classes) | Merge equivalent conditions |
| **Games** | Flood fill, territory calculation | Connected region detection |

## Checkpoint Questions

1. Why is path compression alone not enough for O(α(n))? What's the worst
   case without union by rank?
2. If you need to support "undo last union," which optimization must you
   give up and why?
3. Explain why Union-Find is better than BFS/DFS for dynamic connectivity
   (edges added one at a time).
4. In percolation, why add virtual top/bottom nodes instead of checking
   each top cell against each bottom cell?
5. How would you modify Union-Find to track the size of each component?
6. Two implementations: one uses union by rank + path compression, the other
   uses union by rank only. For 10 million operations, how do they compare
   in practice?
