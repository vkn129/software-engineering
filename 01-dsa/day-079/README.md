# Day 79: Breadth-First Search (BFS)

## Why BFS Matters

Imagine you are trying to find the closest coffee shop. You would not walk 10 miles in
one direction before checking the shop around the corner. You would naturally explore
nearby locations first, then gradually expand outward. That is exactly what BFS does --
it explores a graph in **concentric layers of increasing distance** from the source.

This "explore by distance" property makes BFS the **only correct algorithm for finding
shortest paths in unweighted graphs**. DFS might find *a* path, but it could wander deep
into the graph and return a path 100 edges long when a 3-edge path exists. BFS guarantees
the first time it reaches any vertex, it has found the shortest path to that vertex.

BFS is the backbone of:
- **Web crawlers**: discover pages layer by layer from a seed URL
- **Social network analysis**: "degrees of separation" is literally BFS depth
- **GPS navigation**: shortest path on unweighted road segments
- **Network broadcasting**: packets propagate outward from source
- **AI state-space search**: find the minimum number of moves to solve a puzzle

The key insight: BFS uses a **queue** (FIFO), which ensures vertices are processed in
the exact order they were discovered. This order equals their distance from the source.

---

## The Algorithm

### Core BFS

```
BFS(graph, source):
    queue = [source]
    visited = {source}
    while queue is not empty:
        vertex = queue.popleft()
        process(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

**Why a queue?** A queue processes vertices in FIFO order. All vertices at distance d
are enqueued before any vertex at distance d+1. This guarantees level-by-level exploration.

**Why mark visited when enqueuing (not when dequeuing)?** If you wait until dequeuing,
a vertex might be added to the queue multiple times by different predecessors, wasting
time and potentially breaking shortest-path guarantees.

### Complexity

| Aspect     | Complexity |
|------------|------------|
| Time       | O(V + E)   |
| Space      | O(V)       |

Every vertex is enqueued and dequeued exactly once: O(V). Every edge is examined exactly
once (twice for undirected): O(E). Total: O(V + E).

Space is O(V) for the visited set and queue. In the worst case (star graph), the queue
holds V-1 vertices simultaneously.

---

## BFS Applications

### 1. Shortest Path in Unweighted Graphs

Track the predecessor of each vertex. When BFS reaches the target, reconstruct the path
by following predecessors back to the source.

```
BFS_shortest_path(graph, source, target):
    queue = [source]
    visited = {source}
    parent = {source: None}
    while queue:
        vertex = queue.popleft()
        if vertex == target:
            return reconstruct_path(parent, target)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = vertex
                queue.append(neighbor)
    return None  # no path exists
```

### 2. Level-Order Grouping

Process vertices grouped by their distance from the source. Useful for "minimum rounds"
problems and tree level-order traversal.

```
BFS_levels(graph, source):
    queue = [source]
    visited = {source}
    levels = []
    while queue:
        level_size = len(queue)
        current_level = []
        for _ in range(level_size):
            vertex = queue.popleft()
            current_level.append(vertex)
            for neighbor in graph[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        levels.append(current_level)
    return levels
```

### 3. Connected Components

Run BFS from each unvisited vertex. Each BFS call discovers one connected component.

### 4. Bipartite Checking

A graph is bipartite if and only if it contains no odd-length cycles. BFS can check this
by trying to 2-color the graph: assign alternating colors at each level. If any edge
connects two same-colored vertices, the graph is not bipartite.

### 5. Multi-Source BFS

Start BFS from multiple sources simultaneously. Used for "minimum distance to nearest
source" problems (e.g., rotten oranges spreading rot, fire spreading in a grid).

---

## BFS vs. DFS Comparison

| Property           | BFS              | DFS               |
|--------------------|------------------|--------------------|
| Data structure     | Queue (FIFO)     | Stack (LIFO)       |
| Exploration order  | By distance      | By depth           |
| Shortest path      | Yes (unweighted) | No                 |
| Space (tree)       | O(width)         | O(height)          |
| Space (worst case) | O(V)             | O(V)               |
| Cycle detection    | Yes              | Yes (more natural) |
| Topological sort   | Kahn's algorithm | Standard approach  |

---

## Real-World Usage

| System / Domain          | BFS Application                           | Why BFS                              |
|--------------------------|-------------------------------------------|--------------------------------------|
| Google web crawler        | Discover pages by link distance           | Prioritize nearby pages first        |
| Facebook friend suggestions | Friends-of-friends (2-hop BFS)         | Explore social distance layers       |
| GPS shortest route       | Unweighted grid/road segment paths        | Guaranteed shortest path             |
| Network packet routing   | Broadcast storm prevention                | Layer-by-layer propagation           |
| Chess/puzzle solvers     | Minimum moves to reach target state       | BFS finds optimal move count         |
| Garbage collection       | Mark phase in mark-and-sweep GC           | Discover all reachable objects        |
| Image processing         | Flood fill algorithm                      | Fill connected region layer by layer |
| Compiler analysis        | Reaching definitions, dominance frontiers | Level-order traversal of CFG         |

---

## Common Pitfalls

1. **Forgetting to mark visited on enqueue**: Leads to duplicate processing and O(V*E) time.
2. **Using a list as a queue**: Python `list.pop(0)` is O(n). Use `collections.deque`.
3. **Not handling disconnected graphs**: BFS from one source only finds its component.
4. **Grid BFS without bounds checking**: Leads to index errors on boundary cells.
5. **Confusing BFS with Dijkstra**: BFS works for unweighted graphs only. For weighted
   graphs, use Dijkstra's algorithm.

---

## Checkpoint Questions

1. Why does BFS guarantee the shortest path in unweighted graphs but not in weighted graphs?
   What breaks when edges have different weights?

2. A BFS queue contains vertices [A, B, C]. Vertex A has neighbors D and E. After
   processing A, what does the queue look like and why?

3. You run BFS on a graph with 1 million vertices and 5 million edges. What is the time
   and space complexity? Would DFS be faster?

4. Explain why multi-source BFS (starting from multiple sources simultaneously) correctly
   finds the minimum distance from each cell to its nearest source.

5. A graph has V vertices and E = V-1 edges and is connected. What is the graph structure?
   How does BFS behave on it?

6. You are implementing a web crawler. Why is BFS preferred over DFS for discovering pages?
   What happens if you use DFS instead?
