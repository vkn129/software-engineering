# Day 82: Dijkstra's Algorithm

## Phase 6: Graph Algorithms — Shortest Paths with Non-Negative Weights

### Why Dijkstra's Algorithm Matters

When you type an address into Google Maps, request a route from a ride-sharing app, or
your data packet traverses the internet, a variant of Dijkstra's algorithm is almost
certainly involved. It solves the **single-source shortest path** problem: given a
starting node, find the shortest path to every other node in a weighted graph.

Real systems that rely on Dijkstra's:

- **GPS navigation**: find fastest/shortest route between locations
- **Network routing (OSPF)**: routers compute shortest paths to all destinations
- **Game pathfinding**: NPC movement, A* is Dijkstra + heuristic
- **Social networks**: degrees of separation, influence propagation
- **Robotics**: path planning for autonomous vehicles
- **Airline routing**: cheapest flights between cities
- **Telecommunications**: minimum-cost circuit routing

The critical constraint: **all edge weights must be non-negative**. When negative weights
exist, Dijkstra's greedy approach breaks down (use Bellman-Ford instead, Day 83).

---

### The Core Idea: Greedy Relaxation

Dijkstra's algorithm is a **greedy** algorithm. It maintains a set of vertices whose
shortest distance from the source is already known. At each step, it picks the unvisited
vertex with the smallest tentative distance, marks it as visited, and relaxes all its
outgoing edges.

**Relaxation** is the key operation:
```
if dist[u] + weight(u, v) < dist[v]:
    dist[v] = dist[u] + weight(u, v)
    parent[v] = u
```

**Why greedy works here**: Once we process a vertex (the one with minimum tentative
distance), its distance is final. Why? Because all edge weights are non-negative, so
any other path to this vertex would go through an unprocessed vertex with an equal or
larger tentative distance, plus a non-negative edge weight. It cannot be shorter.

This is exactly why Dijkstra's fails with negative weights: a longer tentative distance
could become shorter via a negative-weight edge.

---

### Implementation 1: Naive (Adjacency Matrix)

```
1. Set dist[source] = 0, dist[v] = infinity for all other v
2. Mark all vertices as unvisited
3. Repeat V times:
   a. Pick unvisited vertex u with minimum dist[u]
   b. Mark u as visited
   c. For each neighbor v of u:
      - Relax edge (u, v)
```

**Complexity**: O(V^2) — the inner loop to find the minimum takes O(V) each time.

Best for **dense graphs** (E close to V^2) where the overhead of a priority queue
doesn't pay off.

---

### Implementation 2: Binary Heap (Priority Queue)

```
1. Set dist[source] = 0, dist[v] = infinity for all other v
2. Push (0, source) to min-heap
3. While heap is not empty:
   a. Pop (d, u) with minimum distance
   b. If d > dist[u]: skip (stale entry)
   c. For each neighbor v of u with weight w:
      - If dist[u] + w < dist[v]:
        - dist[v] = dist[u] + w
        - Push (dist[v], v) to heap
        - parent[v] = u
```

**Complexity**: O((V + E) log V) — each vertex extracted at most once, each edge
relaxed at most once, each heap operation is O(log V).

The "stale entry" check (step 3b) is crucial: since Python's heapq doesn't support
decrease-key, we push duplicates and skip them when popped.

---

### Implementation 3: Fibonacci Heap (Theoretical)

Using a Fibonacci heap for the priority queue gives O(V log V + E) amortized time,
because decrease-key is O(1) amortized. This is theoretically optimal but rarely used
in practice due to high constant factors and complexity.

---

### Path Reconstruction

Dijkstra's computes shortest distances, but we usually also want the actual path.
Maintain a `parent` dictionary: when relaxing edge (u, v), set `parent[v] = u`.
To reconstruct the path to any target, walk backwards from target to source through
parent pointers.

---

### Why Non-Negative Weights Are Required

Consider this graph: A --1--> B --(-3)--> C, and A --2--> C.

Dijkstra processes A first (dist=0), then C (dist=2), then B (dist=1).
But B->C has weight -3, so dist[C] should be 1+(-3)=-2, which is less than 2.
Since C was already marked as visited with dist=2, Dijkstra misses the shorter path.

The greedy invariant (processed vertex has final distance) breaks with negative weights.

---

### Dijkstra's vs Other Shortest Path Algorithms

| Algorithm | Time | Negative Weights | Negative Cycles | Use Case |
|---|---|---|---|---|
| Dijkstra (heap) | O((V+E) log V) | No | N/A | General SSSP, non-negative |
| Dijkstra (naive) | O(V^2) | No | N/A | Dense graphs |
| Bellman-Ford | O(VE) | Yes | Detects | Negative weights, small graphs |
| BFS | O(V+E) | Unweighted only | N/A | Unweighted graphs |
| Floyd-Warshall | O(V^3) | Yes | Detects | All-pairs shortest paths |
| A* | O((V+E) log V) | No | N/A | Dijkstra + heuristic |

---

### Real-World Usage

| System | How Dijkstra's Is Used |
|---|---|
| Google Maps / Waze | Road network shortest path (with A* heuristic) |
| OSPF routing | Routers compute shortest path tree to all destinations |
| Cisco / Juniper routers | IS-IS protocol uses Dijkstra's for link-state routing |
| Video games | Pathfinding for units and NPCs |
| Uber / Lyft | ETA estimation and route optimization |
| SDN controllers | Compute forwarding paths in software-defined networks |
| Social network analysis | Shortest social distance between users |
| Compiler optimization | Register allocation interference graphs |

---

### Complexity Summary

| Variant | Time | Space | When to Use |
|---|---|---|---|
| Naive (array) | O(V^2) | O(V) | Dense graphs, small V |
| Binary heap | O((V+E) log V) | O(V + E) | Sparse to moderate graphs |
| Fibonacci heap | O(V log V + E) | O(V + E) | Theoretical; rarely practical |
| Bidirectional | ~O(V log V) | O(V) | Point-to-point queries |

---

### Checkpoint Questions

1. **Why does Dijkstra's algorithm use a greedy approach, and why is it correct?** Prove informally that once a vertex is extracted from the priority queue with distance d, no shorter path to it exists.

2. **Compare the naive O(V^2) and heap-based O((V+E) log V) implementations.** For a graph with V=1000, E=5000 vs V=1000, E=500000, which implementation would you choose and why?

3. **Explain the "stale entry" problem** when using a binary heap without decrease-key. Why does pushing duplicates and skipping stale entries still give correct results, and what is the worst-case impact on time complexity?

4. **Dijkstra's fails with negative edge weights.** Construct a small graph (4 nodes) where Dijkstra produces an incorrect shortest path, and trace through the algorithm to show where it goes wrong.

5. **How would you modify Dijkstra's to find the K shortest paths** between two nodes instead of just the single shortest? What changes to the algorithm, and what is the new time complexity?

6. **OSPF routing uses Dijkstra's algorithm.** Each router computes a shortest path tree. If a link goes down, what must happen for the network to reconverge, and why is convergence speed critical?
