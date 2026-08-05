# Day 84: Floyd-Warshall Algorithm

## Why Floyd-Warshall Matters

Dijkstra and Bellman-Ford find shortest paths from **one source**. Floyd-Warshall
finds shortest paths between **every pair of vertices** simultaneously. This is
essential when you need a complete distance table:

- **GPS navigation**: pre-compute all-pairs distances for a city map
- **Network routing**: every router needs distances to every other router
- **Social networks**: degrees of separation between all users
- **Game AI**: pathfinding cost lookup tables for NPCs
- **Transitive closure**: "can vertex A reach vertex B?" for all A, B

## The Algorithm

### Core Idea: Dynamic Programming on Intermediate Vertices

For each vertex k, ask: "Does going through k improve the path from i to j?"

```
Floyd-Warshall(G):
    dist = adjacency matrix (∞ for no edge)
    dist[i][i] = 0 for all i

    for k = 0 to V-1:              # try each vertex as intermediate
        for i = 0 to V-1:          # for each source
            for j = 0 to V-1:      # for each destination
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return dist
```

### Why It Works

Define `dist_k[i][j]` = shortest path from i to j using only vertices {0, 1, ..., k}
as intermediates.

- `dist_0[i][j]` = direct edge weight (or ∞)
- `dist_k[i][j]` = min(dist_{k-1}[i][j], dist_{k-1}[i][k] + dist_{k-1}[k][j])

Either the shortest path through {0..k} goes through k (split into i→k and k→j)
or it doesn't (same as using {0..k-1}).

After V iterations, we've considered ALL possible intermediates = true shortest paths.

## Negative Cycle Detection

After running Floyd-Warshall, check the diagonal: if `dist[i][i] < 0` for any i,
there's a negative cycle through vertex i.

## Transitive Closure (Warshall's Algorithm)

Replace + with OR, min with OR: "can i reach j through k?"

```
reach[i][j] = reach[i][j] OR (reach[i][k] AND reach[k][j])
```

This gives the boolean reachability matrix in O(V³).

## Comparison with Other Algorithms

| Algorithm | Problem | Time | Handles Neg Weights | Best For |
|-----------|---------|------|-------------------|----------|
| BFS | Single-source, unweighted | O(V + E) | N/A | Unweighted graphs |
| Dijkstra | Single-source, non-negative | O((V+E) log V) | No | Most shortest path problems |
| Bellman-Ford | Single-source, any weights | O(VE) | Yes | Negative weights |
| **Floyd-Warshall** | **All-pairs** | **O(V³)** | **Yes** | **Dense graphs, all-pairs** |

### When Floyd-Warshall Beats Running Dijkstra V Times

- Dijkstra from every vertex: O(V(V+E) log V) = O(V²E log V) for sparse, O(V³ log V) for dense
- Floyd-Warshall: always O(V³), with very small constant factor
- For **dense graphs**, Floyd-Warshall wins due to its simple triple loop (cache-friendly)
- For **sparse graphs**, V × Dijkstra wins

## Space Optimization

The algorithm can be done **in-place** on the distance matrix — no need for
separate dist_k and dist_{k-1} arrays, because:
- `dist[i][k]` and `dist[k][j]` don't change during iteration k
- (They use k as endpoint, not intermediate)

## Path Reconstruction

Track a `next[i][j]` matrix: the first vertex after i on the shortest path to j.

```
next[i][j] = j    (initial: direct edge)

if dist[i][k] + dist[k][j] < dist[i][j]:
    next[i][j] = next[i][k]   (go toward k first)
```

Reconstruct: i → next[i][j] → next[next[i][j]][j] → ... → j

## Real-World Usage

| System | Application | Why Floyd-Warshall |
|--------|------------|-------------------|
| **Google Maps** | Pre-computed distance tables for regions | All-pairs needed |
| **OSPF routing** | Network topology distance matrix | Complete routing table |
| **Compiler optimization** | Reaching definitions analysis | Transitive closure |
| **Database query planning** | Join ordering via graph distances | Small vertex count |
| **Game maps** | NPC pathfinding lookup tables | Pre-compute once, query O(1) |

## Checkpoint Questions

1. Floyd-Warshall uses O(V²) space. Can you explain why we don't need O(V³)
   space (one matrix per k value)?
2. If you need shortest paths from only one source in a sparse graph, why is
   Floyd-Warshall a poor choice compared to Dijkstra?
3. How would you modify Floyd-Warshall to count the NUMBER of shortest paths
   between each pair of vertices?
4. After running Floyd-Warshall, how do you detect which vertices are part of
   a negative cycle? (Hint: it's not just checking dist[i][i] < 0.)
5. The "minimax path" problem asks: what's the path from i to j that minimizes
   the maximum edge weight? How would you modify Floyd-Warshall for this?
6. For a graph with 1000 vertices and 2000 edges, would you use Floyd-Warshall
   or run Dijkstra 1000 times? Show the math.
