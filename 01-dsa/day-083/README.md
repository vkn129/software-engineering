# Day 83: Bellman-Ford Algorithm

## Why Bellman-Ford Matters

Dijkstra is faster, but it **breaks with negative edge weights**. Real systems
have negative weights:

- **Currency exchange**: log-transformed rates can be negative (arbitrage detection)
- **Network routing**: some paths have incentives (negative cost)
- **Game AI**: penalties as negative rewards in pathfinding
- **Economics**: discount factors in financial modeling

Bellman-Ford handles negative weights AND detects negative cycles — something
Dijkstra can't do at all.

## The Algorithm

### Core Idea: Relax All Edges, V-1 Times

```
Bellman-Ford(G, source):
    dist[source] = 0
    dist[everything else] = ∞

    repeat V-1 times:                    # V-1 rounds of relaxation
        for each edge (u, v, weight):
            if dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                parent[v] = u

    # Check for negative cycles (V-th round)
    for each edge (u, v, weight):
        if dist[u] + weight < dist[v]:
            return "NEGATIVE CYCLE"

    return dist
```

### Why V-1 Iterations?

The shortest path between any two vertices in a graph with V vertices has at
most V-1 edges (any more would mean revisiting a vertex = cycle).

- After round 1: correct distances for paths using ≤ 1 edge
- After round 2: correct distances for paths using ≤ 2 edges
- After round k: correct distances for paths using ≤ k edges
- After round V-1: all shortest paths found (if no negative cycle)

### Negative Cycle Detection

If round V would still relax an edge, it means we can keep reducing distances
forever by going around a negative-weight cycle. The shortest path is -∞.

## Comparison with Dijkstra

| Property | Dijkstra | Bellman-Ford |
|----------|---------|-------------|
| Time complexity | O((V + E) log V) | O(V × E) |
| Negative weights | Fails silently | Handles correctly |
| Negative cycle detection | Can't detect | Detects and reports |
| Best for | Non-negative weights (most cases) | Negative weights, arbitrage |
| Implementation | Priority queue | Simple nested loops |
| Early termination | Natural (visit each vertex once) | Can stop if no relaxation occurs |

## Optimizations

### Early Termination
If an entire round produces no relaxations, the algorithm has converged.
No need to continue to round V-1.

### SPFA (Shortest Path Faster Algorithm)
Only re-examine vertices whose distance changed in the previous round.
Uses a queue (like BFS). Average case is much faster than O(VE), but worst
case is still O(VE).

## Applications

### Currency Arbitrage Detection

Model currencies as vertices, exchange rates as edges. Use log-transformed
rates so multiplication becomes addition:

```
log(rate_A_to_B) + log(rate_B_to_C) + log(rate_C_to_A) > 0  →  arbitrage!
```

Negate the log-rates and run Bellman-Ford. A negative cycle = arbitrage opportunity.

### Distance Vector Routing (RIP Protocol)

Each router runs Bellman-Ford using information from neighbors:
```
dist[destination] = min over all neighbors n of:
    cost_to_n + n.dist[destination]
```

This is the distributed version of Bellman-Ford, used in the RIP routing protocol.

## Real-World Usage

| System | Application | Why Bellman-Ford |
|--------|------------|-----------------|
| **Currency trading** | Arbitrage detection | Negative cycle = free money |
| **RIP routing** | Network shortest paths | Distributed, handles varying costs |
| **Game engines** | Pathfinding with penalties | Some terrain has negative effects |
| **Supply chain** | Cost optimization | Rebates create "negative" costs |
| **Network analysis** | Detecting routing loops | Negative cycles = routing loops |

## Time Complexity Analysis

- **O(V × E)**: V-1 rounds, each examining all E edges
- For sparse graphs (E ≈ V): O(V²)
- For dense graphs (E ≈ V²): O(V³) — same as Floyd-Warshall
- With early termination: often much better in practice

## Checkpoint Questions

1. Why does Dijkstra fail with negative weights? Give a concrete 3-vertex example.
2. Why exactly V-1 iterations? What would happen with V-2? With V?
3. You run Bellman-Ford and round V still relaxes edges. What does this mean
   for the affected vertices' shortest path distances?
4. In currency arbitrage, why do we negate log-rates before running Bellman-Ford?
5. The SPFA optimization uses a queue. How is this different from Dijkstra's
   priority queue approach?
6. Can Bellman-Ford handle a graph where ALL edges have negative weights but
   there are no negative cycles? What would the shortest paths look like?
