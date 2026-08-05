# Day 80: Depth-First Search (DFS)

## Why DFS Matters

If BFS is "explore level by level like a careful surveyor," DFS is "dive as deep
as possible, then backtrack." This simple difference makes DFS the foundation for:

- **Cycle detection** — compilers use DFS to detect circular dependencies
- **Topological sorting** — build systems (Make, Bazel) order tasks via DFS
- **Strongly connected components** — social network cluster analysis
- **Maze generation** — randomized DFS creates perfect mazes with long corridors
- **Compiler analysis** — dominator trees, liveness analysis, dead code elimination

BFS finds shortest paths. DFS finds *structure* — cycles, components, ordering.

## The Algorithm

### Core Idea

Start at a vertex. Go as deep as possible along each branch before backtracking.
Uses a **stack** (explicit or via recursion's call stack).

### Recursive DFS

```
DFS(G, u):
    mark u as visited
    pre-visit(u)                    # discovery time
    for each neighbor v of u:
        if v not visited:
            DFS(G, v)
    post-visit(u)                   # finish time
```

### Iterative DFS

```
DFS-Iterative(G, start):
    stack = [start]
    while stack not empty:
        u = stack.pop()
        if u not visited:
            mark u as visited
            process(u)
            for each neighbor v of u:
                if v not visited:
                    stack.push(v)
```

**Key difference from BFS**: swap the queue for a stack. That's it. But the
traversal order changes dramatically — DFS goes deep, BFS goes wide.

## Edge Classification

DFS on a directed graph classifies every edge into exactly one of four types.
This classification is the source of DFS's analytical power.

| Edge Type | Definition | What It Means |
|-----------|-----------|---------------|
| **Tree edge** | u → v where v is first discovered via u | Forms the DFS tree |
| **Back edge** | u → v where v is an ancestor of u in DFS tree | **Proves a cycle exists** |
| **Forward edge** | u → v where v is a descendant (not child) of u | Shortcut down the tree |
| **Cross edge** | u → v where v is in a different subtree | Connects separate branches |

### The Three-Color Trick

Track vertex state with colors to classify edges:
- **WHITE**: undiscovered
- **GRAY**: discovered but not finished (still exploring descendants)
- **BLACK**: finished (all descendants explored)

When processing edge u → v:
- v is WHITE → **tree edge** (discovering v for the first time)
- v is GRAY → **back edge** (v is an ancestor, we found a cycle!)
- v is BLACK → **forward or cross edge**

**Critical insight**: A directed graph has a cycle **if and only if** DFS finds
a back edge. This is why compilers use DFS for dependency analysis.

## Pre-order and Post-order

DFS assigns two timestamps to each vertex:
- **Discovery time** (pre-order): when the vertex is first visited
- **Finish time** (post-order): when all descendants are fully explored

```
Example:       0 → 1 → 3
               ↓       ↑
               2 ------+

DFS from 0:
  Vertex:     0    1    3    2
  Discovery:  1    2    3    5
  Finish:     8    4    4    6
```

### Why Timestamps Matter

1. **Parenthesis theorem**: For any two vertices u, v, their discovery/finish
   intervals are either nested or disjoint — never partially overlapping
2. **Topological sort**: Sort by decreasing finish time = valid topological order
3. **Ancestor check**: u is ancestor of v iff `disc[u] < disc[v] < fin[v] < fin[u]`

## DFS vs BFS — When to Use Which

| Property | BFS | DFS |
|----------|-----|-----|
| Data structure | Queue (FIFO) | Stack (LIFO) / recursion |
| Exploration pattern | Level by level | Branch by branch |
| Shortest path (unweighted) | Yes | No |
| Cycle detection | Possible but awkward | Natural (back edges) |
| Topological sort | Kahn's algorithm | Reverse post-order |
| Connected components | Works | Works |
| Memory | O(width of graph) | O(depth of graph) |
| Maze solving | Finds shortest path | Finds *a* path (not shortest) |
| Maze generation | Poor (too uniform) | Great (long corridors) |

## Time Complexity

- **O(V + E)** — every vertex and edge visited exactly once
- Same as BFS, but the *order* of visits differs

## Real-World Usage

| System | DFS Application | Why DFS |
|--------|----------------|---------|
| **Git** | Detecting merge conflicts | Finds common ancestors via DFS on commit graph |
| **Make/Bazel** | Build ordering | Topological sort via DFS on dependency graph |
| **React** | Component tree reconciliation | DFS traversal of virtual DOM tree |
| **Garbage collectors** | Mark phase | DFS from roots marks all reachable objects |
| **Puzzle solvers** | Sudoku, N-Queens | DFS with backtracking explores solution space |
| **Network analysis** | Finding bridges/articulation points | Tarjan's algorithm uses DFS timestamps |

## Checkpoint Questions

1. Why does DFS use O(depth) memory while BFS uses O(width)? For which graph
   shapes is each more memory-efficient?
2. Explain why a back edge in DFS on a directed graph proves a cycle exists.
   Why don't forward or cross edges prove cycles?
3. In an undirected graph, can DFS produce forward or cross edges? Why or why not?
4. How would you modify DFS to find all paths between two vertices?
   What's the time complexity in the worst case?
5. Why is randomized DFS good for maze generation but bad for maze solving?
6. A DFS on a DAG produces vertices with finish times [8, 6, 4, 7, 3, 5, 2, 1].
   What's the topological order?
