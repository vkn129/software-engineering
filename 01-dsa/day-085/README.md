# Day 85: Minimum Spanning Trees — Prim's & Kruskal's

## Why MST Matters

A Minimum Spanning Tree connects all vertices in a weighted undirected graph
using the minimum total edge weight, with no cycles. This models:

- **Network design**: cheapest way to connect all offices with fiber
- **Circuit design**: minimum wire to connect all components on a PCB
- **Clustering**: remove the longest MST edges to get natural clusters
- **Approximation algorithms**: MST gives a 2-approximation for TSP
- **Image segmentation**: pixels as vertices, similarity as edge weights

## The Cut Property (Why MST Algorithms Work)

**Theorem**: For any cut (partition of vertices into two sets), the minimum-weight
edge crossing the cut MUST be in every MST.

This one property justifies both Prim's and Kruskal's:
- **Prim's**: at each step, the "cut" is {vertices in tree} vs {vertices not in tree}
- **Kruskal's**: at each step, the "cut" is {one component} vs {everything else}

Both greedily pick the minimum crossing edge — and the cut property guarantees
this is always safe.

## Prim's Algorithm

**Strategy**: Grow the MST from a single vertex, always adding the cheapest edge
that connects a new vertex.

```
Prim(G, start):
    mst_edges = []
    visited = {start}
    heap = [(weight, start, neighbor) for neighbor of start]

    while heap and len(visited) < V:
        weight, u, v = heap.pop_min()
        if v in visited: continue
        visited.add(v)
        mst_edges.append((u, v, weight))
        for neighbor, w of v:
            if neighbor not in visited:
                heap.push((w, v, neighbor))

    return mst_edges
```

**Time**: O((V + E) log V) with a binary heap. Same as Dijkstra — and the
algorithm looks almost identical. The difference: Dijkstra tracks total distance
from source; Prim tracks edge weight to the nearest tree vertex.

## Kruskal's Algorithm

**Strategy**: Sort all edges by weight. Add each edge if it doesn't create a cycle.

```
Kruskal(G):
    sort edges by weight
    mst_edges = []
    uf = UnionFind(V)

    for (u, v, weight) in sorted_edges:
        if uf.find(u) != uf.find(v):    # different components?
            uf.union(u, v)
            mst_edges.append((u, v, weight))
            if len(mst_edges) == V - 1: break

    return mst_edges
```

**Time**: O(E log E) for sorting, plus O(E α(V)) for Union-Find operations.
Since α(V) ≤ 4 for any practical V, it's effectively O(E log E).

**Key insight**: Kruskal's needs the Union-Find data structure (Day 86) to
efficiently check "does adding this edge create a cycle?"

## Comparison

| Property | Prim's | Kruskal's |
|----------|--------|-----------|
| Strategy | Grow from one vertex | Sort all edges globally |
| Data structure | Priority queue (min-heap) | Union-Find |
| Time | O((V+E) log V) | O(E log E) |
| Better for | Dense graphs (E ≈ V²) | Sparse graphs (E ≈ V) |
| Edge list needed? | No (adjacency list works) | Yes (need all edges sorted) |
| Works on disconnected? | One component only | Yes (gives minimum spanning forest) |
| Incremental | Easy to add vertices | Easy to add edges |

## MST Properties

1. **Uniqueness**: If all edge weights are distinct, the MST is unique
2. **Cycle property**: The heaviest edge in any cycle is NOT in the MST
3. **Cut property**: The lightest edge across any cut IS in the MST
4. **V-1 edges**: An MST of V vertices always has exactly V-1 edges
5. **Substructure**: Every subtree of an MST is an MST of that subgraph

## Applications Beyond Connectivity

### Clustering (Single-Linkage)
Build the MST, then remove the K-1 heaviest edges → K natural clusters.
This is exactly single-linkage hierarchical clustering.

### TSP Approximation
MST weight ≤ optimal TSP tour ≤ 2 × MST weight.
Double the MST edges and shortcut repeated vertices for a 2-approximation.

### Bottleneck Spanning Tree
The MST minimizes the maximum edge weight among all spanning trees.
(This is the "minimax path" property.)

## Real-World Usage

| System | Application | Which Algorithm |
|--------|------------|-----------------|
| **Telecom** | Minimum cost to lay cable | Kruskal's (sparse network) |
| **VLSI** | Wire routing on chips | Prim's (dense, from chip center) |
| **Biology** | Phylogenetic trees | Kruskal's (evolutionary distance) |
| **Image processing** | Segmentation via edge removal | Either (depends on density) |
| **Network planning** | Redundancy analysis (MST = backbone) | Kruskal's |

## Checkpoint Questions

1. If all edge weights are equal, how many different MSTs can a graph have?
2. You add a new edge to a graph. How do you update the MST efficiently
   without recomputing from scratch?
3. Why is Prim's better for dense graphs and Kruskal's for sparse?
   Show the complexity comparison for E = V² vs E = V.
4. Explain why removing the heaviest edge from a cycle is safe (cycle property).
5. A company has 50 offices and wants to connect them with minimum fiber cost.
   10 offices are already connected. How would you modify Kruskal's algorithm?
6. Can Prim's or Kruskal's work with negative edge weights? Why or why not?
