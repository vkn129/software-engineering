# Day 88: Articulation Points & Bridges

## Why This Matters

Every network has **single points of failure**. An articulation point (cut vertex)
is a node whose removal disconnects the graph. A bridge (cut edge) is an edge
whose removal disconnects the graph. Finding these is critical for:

- **Network infrastructure**: Which router, if it fails, splits the network?
- **Social networks**: Which user, if they leave, breaks a community apart?
- **Circuit design**: Which wire, if cut, kills the circuit?
- **Road networks**: Which road closure isolates a town?

The naive approach — remove each vertex/edge and check connectivity — costs
O(V * (V + E)). Tarjan's algorithm finds all of them in a single DFS: O(V + E).

## Tarjan's Algorithm: The Core Idea

The algorithm uses a DFS traversal and tracks two values per vertex:

```
disc[v] = discovery time of vertex v (when DFS first visits it)
low[v]  = lowest discovery time reachable from v's subtree via back edges
```

A **back edge** (u, ancestor) lets vertex u "reach back" to an earlier vertex
without using the tree edge. The `low` value propagates this reachability upward.

### Finding Articulation Points

A vertex `u` is an articulation point if:

1. **Root case**: `u` is the DFS root AND has 2+ children in the DFS tree.
   Removing the root splits its independent subtrees.

2. **Non-root case**: `u` has a child `v` where `low[v] >= disc[u]`.
   This means v's subtree has NO back edge reaching above u — removing u
   disconnects v's subtree from the rest of the graph.

```
DFS Tree:          Back edge:
    A (disc=0)         A (disc=0, low=0)
   / \                / \
  B   C              B   C (disc=2, low=0)  <- back edge C->A
  |                  |                          means low[C]=0
  D                  D (disc=3, low=3)

B is articulation: low[D]=3 >= disc[B]=1, and D can't reach above B
A is NOT articulation (as root with 2 children... but C reaches back to A)
Actually A IS articulation: root with 2+ DFS children
```

### Finding Bridges

An edge (u, v) is a bridge if `low[v] > disc[u]`.

Note the **strict inequality** — unlike articulation points which use `>=`.
If `low[v] == disc[u]`, there's a back edge from v's subtree to u itself,
so removing (u, v) doesn't disconnect v from u. But if `low[v] > disc[u]`,
v's subtree has absolutely no way to reach u or anything above it.

```
Bridge:                 Not a bridge:
A ------- B             A ------- B
(disc=0)  (disc=1)      |         |
          |              +----C----+
          C              Back edge A-C means
          (low=1)        low[C] = 0 = disc[A]
low[B]=1 > disc[A]=0    Not > disc[A], so not bridge
So A-B is a bridge
```

## Biconnected Components

A **biconnected component** is a maximal subgraph with no articulation points —
every pair of vertices has two vertex-disjoint paths between them. The graph
decomposes into biconnected components that share only articulation points.

This decomposition is useful for:
- **Redundancy analysis**: Each biconnected component is internally resilient
- **Block-cut tree**: Represents the structure of biconnected components as a tree
- **2-edge-connected components**: Similar but for bridges (edge-disjoint paths)

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Find all articulation points | O(V + E) | O(V) |
| Find all bridges | O(V + E) | O(V) |
| Biconnected components | O(V + E) | O(V + E) |

All are single-pass DFS — you can find articulation points AND bridges
simultaneously in one traversal.

## Connection to Other Graph Concepts

- **SCC (Day 87)**: Tarjan's SCC algorithm uses the same disc/low technique
  but on directed graphs. Articulation points are for undirected graphs.
- **Union-Find (Day 86)**: Can check connectivity but can't efficiently find
  articulation points — you'd need to remove each vertex and rebuild.
- **DFS (Day 80)**: This is a DFS application. The back edges in DFS are what
  make the algorithm work — they encode "reachability" information.

## Checkpoint Questions

1. **Why does the root of the DFS tree have a special case?** The root has no
   parent, so the `low[v] >= disc[u]` condition is meaningless — what actually
   determines if the root is an articulation point?

2. **Why is the bridge condition strictly `>` while the articulation point
   condition is `>=`?** Give a concrete example where an edge satisfies `==`
   but is NOT a bridge.

3. **Can a bridge's endpoints be non-articulation points?** If the bridge
   connects two vertices each with degree 1 (a simple path), are those vertices
   articulation points?

4. **What happens to Tarjan's algorithm on a tree (no back edges)?** Which
   vertices are articulation points in a tree? Which edges are bridges?

5. **How would you modify the algorithm for a directed graph?** Why doesn't the
   concept of "articulation point" directly transfer to directed graphs?

6. **A network has 1000 nodes and you find 50 articulation points. Your manager
   asks you to add the minimum number of edges to eliminate ALL articulation
   points. How do you approach this?**
