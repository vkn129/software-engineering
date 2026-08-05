# Day 172: Heavy-Light Decomposition (HLD)

## Why HLD Matters

Trees are not arrays. A "range query" on a tree is a **path query**: find the
max/sum/min along the path from u to v. Linear data structures (BIT,
segment tree) don't directly apply.

**Heavy-Light Decomposition** maps a tree onto a flat array such that any
path from u to v crosses at most **O(log N) contiguous segments**. Each
segment becomes a range query on a segment tree → total query is
**O(log² N)**.

Applications:
- Network routing: max bandwidth along path
- Compiler dominator queries
- Phylogenetic tree analyses
- Competitive programming "tree + range op" problems
- Source control tools (LCA, path metrics in commit trees)

## The Idea

For each non-leaf node, pick its child with the **largest subtree** as the
"heavy child". The edge to that child is a **heavy edge**; all others are
**light edges**.

**Heavy path**: maximal chain of heavy edges starting at some node. The tree
decomposes into a forest of disjoint heavy paths connected by light edges.

### Key Property

Walking up from any node to the root crosses at most **O(log N)** light edges.

**Proof**: each light edge halves the subtree size (if it weren't half,
the other child would be heavier and the edge would be heavy). So depth
in terms of light edges is at most log N.

### What This Buys Us

A path u → v decomposes via LCA. Each side is a sequence of heavy paths
joined at light edges. Total heavy paths visited = O(log N).

If each heavy path is laid out **contiguously** in an array, we can run a
segment tree on the array and answer **range queries per heavy path**.

Result: path query in **O(log² N)** = O(log N) heavy paths × O(log N) seg tree.

## Building HLD

Two DFS passes:

### Pass 1: subtree sizes + heavy child

```
size[v]  = 1 + sum size[c] for c in children
heavy[v] = argmax size[c] (the child with biggest subtree)
```

### Pass 2: assign positions + chain heads

Walk the tree, but always **descend into the heavy child first** before
exploring other children. The resulting DFS order places each heavy path
contiguously.

```
pos[v]   = DFS index in the flat array
head[v]  = top of the heavy path that v lies on
depth[v] = depth from root
parent[v]
```

## Path Query: u → v

```python
def path_query(u, v):
    result = identity
    while head[u] != head[v]:
        if depth[head[u]] < depth[head[v]]:
            u, v = v, u
        # u is on a deeper chain head; query [pos[head[u]] .. pos[u]]
        result = combine(result, seg.query(pos[head[u]], pos[u]))
        u = parent[head[u]]
    # Now both on same chain; query [min pos .. max pos]
    if pos[u] > pos[v]:
        u, v = v, u
    result = combine(result, seg.query(pos[u], pos[v]))
    return result
```

Each iteration of the while loop moves to a shallower chain (via the light
edge `parent[head[u]]`). At most **O(log N)** iterations.

## Worked Example

Tree:
```
            1
          / | \
         2  3  4
        / \    \
       5   6    7
      / \
     8   9
```

Subtree sizes: size[1]=9, size[2]=5, size[5]=3, ...

Heavy edges (largest subtree child): 1-2, 2-5, 5-8 (or 5-9).
Heavy paths: {1,2,5,8}, {3}, {4,7}, {6}, {9}.

To query path from 9 to 7:
- 9 is on path {9}, head=9.
- 7 is on path {4,7}, head=4.
- Decompose: jump up via light edges across 3 heavy paths.

## Point Update + Path Query

To **update a node value** at v: `seg.update(pos[v], newval)`. O(log N).

To **add x to all nodes on path u → v**: same path-decomposition trick,
but with a lazy segment tree (range update + range query). Still O(log² N).

## HLD vs Other Tree Approaches

| Approach | Path query | Subtree query | Updates |
|----------|-----------|---------------|---------|
| Euler tour + segment tree | hard | O(log N) | O(log N) |
| HLD + segment tree | **O(log² N)** | O(log N) | O(log² N) |
| Link-cut tree (Tarjan) | O(log N) amort | O(log N) | O(log N) amort |
| Centroid decomposition | O(log² N) | not direct | O(log² N) |

HLD is the **goldilocks** choice: simpler than link-cut trees, more powerful
than Euler tour for path queries.

## Implementation Pitfalls

- **0/1 indexing**: be consistent. Off-by-one bugs are vicious in HLD.
- **Edges vs vertices**: if values live on edges, store them at the
  deeper endpoint and **skip the LCA itself** when querying.
- **Iterative vs recursive DFS**: deep trees blow Python's stack (1000 default).
  Use sys.setrecursionlimit or iterative DFS.
- **Heavy child tie**: doesn't matter which one you pick — pick any.
- **Multiple values per node**: lay out multiple segment trees, one per
  attribute, but share the HLD positions.

## Connection to Earlier Days

- **Day 52 Segment trees**: HLD is "segment tree on heavy paths"
- **Day 56 Fenwick tree**: lighter alternative for sum-only path queries
- **Day 80 DFS**: HLD uses two DFS passes to assign positions
- **Day 81 LCA**: not strictly needed inside HLD, but useful for path semantics

## Failure Modes

- **Star graph** (one center, N-1 leaves): every leaf is its own heavy path of
  length 1. HLD degenerates but is still O(log² N).
- **Caterpillar / path graph**: one long heavy path. Range queries become
  O(log N) — better than worst case.
- **Dynamic trees** (edges inserted/deleted): HLD can't handle structural
  changes. Use link-cut trees instead.

## Real-World Usage

| System | Application | Why HLD |
|--------|-------------|---------|
| Routers | OSPF/BGP path computation | Tree shape predictable |
| File systems | Inode hierarchy queries | Static tree, many path queries |
| Build systems | Dependency path costs | Static DAG turned into spanning tree |
| Genetics | Tree-of-life ancestry | Phylogenetic queries |
| Game AI | Behavior tree path metrics | Static behavior tree |

## Checkpoint Questions

1. Why does walking up from any node cross at most O(log N) light edges?
2. Why is path query O(log² N) and not O(log N)?
3. What's the memory cost of HLD on a tree with N nodes?
4. How does HLD differ from centroid decomposition?
5. Why must heavy paths be laid out contiguously in the flat array?
6. Adapt HLD to handle "max edge weight on path u→v" — what changes?
