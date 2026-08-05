# Day 78: Graph Representations

## Why Graphs Matter

Graphs are the most general-purpose data structure in computer science. Every
relationship-based problem — social networks, road maps, dependency chains, the
internet itself — is a graph. The choice of **how you store a graph in memory**
determines the performance of every algorithm you run on it.

Pick the wrong representation and an O(V + E) traversal becomes O(V²). Pick the
right one and you save gigabytes of RAM on sparse real-world networks.

## The Four Representations

### 1. Adjacency List

Store a list of neighbors for each vertex. The most common choice for sparse
graphs (E << V²), which is most real-world graphs.

```
0: [1, 2]
1: [0, 3]
2: [0, 3]
3: [1, 2]
```

- **Space**: O(V + E)
- **Check edge (u,v)**: O(degree(u)) — scan u's neighbor list
- **Iterate neighbors of u**: O(degree(u)) — just walk the list
- **Add edge**: O(1) — append to list
- **Best for**: BFS, DFS, most graph algorithms on sparse graphs

### 2. Adjacency Matrix

A V×V matrix where `matrix[u][v] = 1` (or weight) if edge exists.

```
  0 1 2 3
0 0 1 1 0
1 1 0 0 1
2 1 0 0 1
3 0 1 1 0
```

- **Space**: O(V²) — wasteful for sparse graphs, fine for dense
- **Check edge (u,v)**: O(1) — direct index lookup
- **Iterate neighbors of u**: O(V) — must scan entire row
- **Add edge**: O(1)
- **Best for**: dense graphs, frequent edge-existence queries, Floyd-Warshall

### 3. Edge List

Simply a list of all edges as (u, v) pairs (with optional weight).

```
[(0,1), (0,2), (1,3), (2,3)]
```

- **Space**: O(E)
- **Check edge (u,v)**: O(E) — linear scan (or O(log E) if sorted)
- **Iterate neighbors of u**: O(E) — must scan all edges
- **Add edge**: O(1)
- **Best for**: Kruskal's MST (sort edges by weight), simple input parsing

### 4. Incidence Matrix

A V×E matrix where `matrix[v][e] = 1` if vertex v is an endpoint of edge e.
For directed graphs: `+1` for tail, `-1` for head.

- **Space**: O(V × E)
- **Best for**: theoretical analysis, certain linear algebra approaches
- **Rarely used in practice** due to space requirements

## When to Use What

| Representation | Space | Edge Check | Neighbors | Use When |
|---------------|-------|------------|-----------|----------|
| Adjacency List | O(V+E) | O(deg) | O(deg) | Default choice, sparse graphs |
| Adjacency Matrix | O(V²) | O(1) | O(V) | Dense graphs, edge queries |
| Edge List | O(E) | O(E) | O(E) | Kruskal's, simple storage |
| Incidence Matrix | O(VE) | O(E) | O(E) | Theoretical work only |

## Real-World Usage

| System | Representation | Why |
|--------|---------------|-----|
| **Social networks** | Adjacency list | Billions of users but avg ~200 connections — extremely sparse |
| **Google Maps** | Adjacency list with weights | Road network is sparse; need fast neighbor iteration for Dijkstra |
| **GPU graph algorithms** | Adjacency matrix | GPUs excel at matrix operations; dense representation maps to SIMD |
| **Network routing tables** | Adjacency list | Routers store neighbor links, not all-pairs connectivity |

## Directed vs Undirected

For undirected graphs, each edge appears twice in an adjacency list (once per
endpoint) and the adjacency matrix is symmetric. For directed graphs, edge (u,v)
only appears in u's list, and `matrix[u][v]` doesn't imply `matrix[v][u]`.

## Weighted Graphs

- **Adjacency list**: store `(neighbor, weight)` tuples instead of just neighbors
- **Adjacency matrix**: store weights instead of 0/1
- **Edge list**: store `(u, v, weight)` triples

## Checkpoint Questions

1. A social network has 1 billion users with an average of 200 friends each.
   Which representation would you use and why? How much memory?
2. Why is the adjacency matrix representation O(V) to find all neighbors of a
   vertex, even if that vertex has only 2 neighbors?
3. For which algorithm is the edge list representation ideal, and why?
4. How does the adjacency list representation change for a weighted directed graph?
5. If you need to frequently check whether edge (u,v) exists, which representation
   is best? What's the trade-off?
6. What's the relationship between graph density (E/V²) and the relative efficiency
   of adjacency list vs adjacency matrix?
