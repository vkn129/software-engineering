# Day 173: Centroid Decomposition

## Why Centroid Decomposition Matters

HLD (Day 172) decomposes a tree for **path queries**.
Centroid decomposition decomposes a tree for **distance-based queries**:

- "Count pairs (u, v) with dist(u, v) = k"
- "Closest red node to query node u"
- "Sum of distances from u to all other nodes"
- "K-th closest node to u"

It powers algorithms like:
- Tree edit distance (in some formulations)
- IOI-level problems involving path counting
- Bioinformatics: phylogenetic queries
- Compiler: dominator-related distances

**Key insight**: any path in a tree of N nodes either passes through the
centroid of the whole tree, or lies entirely in a subtree after centroid
removal. Recursing gives a tree of depth O(log N), and each level of the
recursion processes O(N) work → **total O(N log N)** for many problems.

## Centroid of a Tree

A node c is a **centroid** if removing c leaves no component with > N/2
nodes. Every tree has at least one and at most two centroids.

### Why a centroid exists

Start at any node. Walk toward the heaviest neighbor. The total size of the
"current side" decreases each step. Eventually, no neighbor's subtree
exceeds N/2 — that's the centroid.

```python
def centroid(adj, n, removed):
    # Find sizes
    size = [0] * n
    def dfs_size(u, par):
        size[u] = 1
        for v in adj[u]:
            if v != par and not removed[v]:
                size[u] += dfs_size(v, u)
        return size[u]
    total = dfs_size(start, -1)

    def find(u, par):
        for v in adj[u]:
            if v != par and not removed[v] and size[v] > total // 2:
                # Subtree at v too big; descend
                return find(v, u)
        return u

    return find(start, -1)
```

## The Decomposition

```
def decompose(tree):
    c = centroid(tree)
    remove c
    for each component formed:
        recurse on component
    return tree of centroids
```

Each level of recursion the tree halves in size (centroid splits ≤ N/2 per
piece). So decomposition has **depth O(log N)**.

This gives the **centroid tree**: a rooted tree of centroids where parent
of centroid c is the centroid of its parent component.

### Properties

1. Depth of centroid tree ≤ ⌈log₂ N⌉
2. Every node v has at most log N ancestors in the centroid tree
3. The path from u to v in the **original** tree passes through their LCA
   in the **centroid** tree (after distance bookkeeping)

## Distance Queries via Centroid Decomposition

To answer "shortest path from u to all 'special' nodes":

For each centroid c on the path from u up the centroid tree:
1. Compute d = dist(u, c) in the original tree
2. Look up "closest special node to c at distance d_c" using a precomputed
   structure keyed on c
3. The answer is min over all c-ancestors of (d + d_c)

Each ancestor query is O(log N) ancestors × O(1) lookup = **O(log N)**.

## Application: Count Pairs at Distance K

```python
def count_pairs_at_distance(tree, k):
    total = 0

    def solve(c):
        # All paths through c
        # 1. compute distances from c to all nodes in its component
        # 2. count pairs (d1, d2) with d1 + d2 = k, removing same-subtree pairs
        ...
        # recurse into sub-components
        for each child centroid c':
            solve(c')

    solve(root_centroid)
    return total
```

Time: O(N log N) total because each node appears in O(log N) levels and
work per level is O(N).

## Centroid Decomposition vs HLD

| Aspect | HLD | Centroid Decomposition |
|--------|-----|------------------------|
| Best for | path queries (sum/max on u→v) | distance/counting queries |
| Depth | O(log N) light edges | O(log N) levels |
| Combines with | segment tree | hash maps, sorted arrays |
| Subtree queries | yes via Euler tour | indirect |
| Implementation | medium complexity | medium-high complexity |

Both are O(log² N) class techniques. They solve different problems.

## Building the Centroid Tree

```python
def build_centroid_tree(adj, n):
    removed = [False] * n
    parent_in_ct = [-1] * n
    size = [0] * n

    def dfs_size(u, par):
        size[u] = 1
        for v in adj[u]:
            if v != par and not removed[v]:
                size[u] += dfs_size(v, u)

    def find_centroid(u, par, tree_size):
        for v in adj[u]:
            if v != par and not removed[v] and size[v] > tree_size // 2:
                return find_centroid(v, u, tree_size)
        return u

    def decompose(u, par):
        dfs_size(u, -1)
        c = find_centroid(u, -1, size[u])
        parent_in_ct[c] = par
        removed[c] = True
        for v in adj[c]:
            if not removed[v]:
                decompose(v, c)

    decompose(0, -1)
    return parent_in_ct
```

The returned `parent_in_ct` describes the centroid tree.

## Connection to Earlier Days

- **Day 18 DFS**: centroid finding is DFS-based
- **Day 80 DFS classification**: subtree sizes via post-order
- **Day 81 LCA**: centroid decomposition gives O(log N) LCA-like queries
- **Day 86 Union-Find**: alternative offline-style approach for some problems
- **Day 172 HLD**: complementary tree decomposition

## Failure Modes

- **Recursion depth on path graph**: N=10^5 path → recursion depth log N ≈ 17.
  Safe even in Python.
- **Recomputing sizes**: must recompute subtree sizes each level — they
  change after centroid removal.
- **Not finding the centroid**: subtle bug when the heaviest neighbor's
  subtree size is computed against the WRONG total. Always recompute total
  per level.
- **Adjacency mutability**: don't actually delete edges. Use a `removed[]`
  array to "block" centroids virtually.
- **Worst-case constant**: centroid decomposition can be 5-10x slower than
  HLD in practice for the same operation, due to bookkeeping overhead.

## Real-World Usage

| System | Application | Why centroid |
|--------|-------------|--------------|
| Phylogenetics | Pairwise distance summaries | Counting under distance constraints |
| Compiler analysis | Function call tree metrics | Distance-bounded reachability |
| Game AI | Closest-of-class queries on game tree | Multi-source nearest queries |
| Bioinformatics | Tree of life shortest-path stats | All-pairs distance distributions |

## Checkpoint Questions

1. Why does centroid decomposition have depth O(log N)?
2. Why does every tree have a centroid where each subtree has ≤ N/2 nodes?
3. In count-pairs-at-distance-k, why subtract same-subtree pairs?
4. Why must subtree sizes be recomputed at every recursion level?
5. Could you use centroid decomposition for path sum queries? How vs HLD?
6. A path graph 0—1—2—...—N-1: where is the centroid?
