# Day 89: Bipartite Graphs & A* Search

## Why This Matters

Two fundamental graph techniques that power real systems:

**Bipartite graphs** model any "two-sided" relationship: workers to tasks, students
to courses, buyers to sellers. Checking bipartiteness tells you if a fair
two-coloring exists (e.g., can you split a network into two non-conflicting groups?).
Maximum matching solves assignment problems — pairing entities optimally.

**A\* search** is THE pathfinding algorithm in games, robotics, and navigation.
It combines Dijkstra's guaranteed optimality with a heuristic that focuses the
search toward the goal, exploring far fewer nodes. Every GPS navigation system
uses some variant of A*.

## Bipartite Graph Checking: 2-Coloring via BFS

A graph is **bipartite** if you can color every vertex with one of two colors
such that no edge connects two vertices of the same color. Equivalently: the
graph has no odd-length cycle.

Algorithm: BFS from any uncolored vertex, alternating colors. If you find a
neighbor already colored the same as the current vertex, the graph is NOT bipartite.

```
Bipartite:              NOT Bipartite:
  A --- B                 A --- B
  |     |                 |   / |
  C --- D                 C --- D

Color: A=0, B=1          Color: A=0, B=1, C=1
       C=1, D=0          D should be 0... but D-B edge:
No conflicts!            D=0, B=1 OK. But C=1, B=1
                         and C-B edge exists -> CONFLICT
                         (triangle A-B-C is odd cycle)
```

## Maximum Bipartite Matching: Hopcroft-Karp

Given a bipartite graph, a **matching** is a set of edges with no shared vertices.
The **maximum matching** has the largest possible size.

**Hopcroft-Karp** finds maximum matching in O(E * sqrt(V)) by finding multiple
augmenting paths simultaneously using BFS (to find shortest augmenting path length)
followed by DFS (to find vertex-disjoint augmenting paths of that length).

```
Workers    Tasks         Maximum Matching:
  W1 ----> T1             W1 ----> T1
  W1 ----> T2             W2 ----> T2
  W2 ----> T2             W3 ----> T3
  W2 ----> T3
  W3 ----> T3           3 pairs matched (maximum)
```

### Konig's Theorem

In a bipartite graph:
**minimum vertex cover = maximum matching size**

This means the fewest vertices needed to "touch" every edge equals the size of
the largest matching. This duality doesn't hold in general graphs.

## A* Search Algorithm

A* is a best-first search that uses: **f(n) = g(n) + h(n)**

- `g(n)`: actual cost from start to n (like Dijkstra)
- `h(n)`: estimated cost from n to goal (the heuristic)
- `f(n)`: estimated total cost through n

```
Grid with obstacle (#):     A* explores (marked with .):
  S . . . .                   S . . . .
  . . # # .                   . . # # .
  . . . # .                   . . . # .
  . . . . G                   . . . . G

Dijkstra explores:          A* with Manhattan heuristic:
  S . . . .                   S . . . .
  . . # # .                   . . # # .
  . . . # .                     . . # .
  . . . . G                     . . . G

Dijkstra: explores outward     A*: focuses toward goal
in all directions              explores FAR fewer nodes
```

### Key insight: A* with h(n) = 0 is Dijkstra

Dijkstra doesn't know where the goal is — it expands in all directions equally.
A* uses the heuristic to bias exploration toward the goal.

### Admissible Heuristics

A heuristic is **admissible** if it never overestimates the true cost.
Admissibility guarantees A* finds the optimal path.

| Heuristic | Formula | When to Use |
|-----------|---------|-------------|
| Manhattan | \|x1-x2\| + \|y1-y2\| | 4-directional grid movement |
| Euclidean | sqrt((x1-x2)^2 + (y1-y2)^2) | Any-angle movement |
| Chebyshev | max(\|x1-x2\|, \|y1-y2\|) | 8-directional grid movement |
| Zero | 0 | Reduces to Dijkstra |

**Why admissibility guarantees optimality**: If h never overestimates, then
f(n) = g(n) + h(n) <= g(n) + true_remaining_cost = true_total_cost through n.
So A* will never skip a node on the optimal path in favor of a worse one.

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Bipartite check (BFS 2-coloring) | O(V + E) | O(V) |
| Maximum matching (Hopcroft-Karp) | O(E * sqrt(V)) | O(V) |
| A* search | O(E * log V) worst case | O(V) |
| Dijkstra (A* with h=0) | O(E * log V) | O(V) |

A*'s practical performance depends on heuristic quality — a better heuristic
means fewer nodes explored, even though worst-case complexity is the same as
Dijkstra.

## Connection to Other Days

- **BFS (Day 80)**: Bipartite checking is a BFS application. A* uses a priority
  queue like Dijkstra but with heuristic-augmented priorities.
- **Dijkstra (Day 83)**: A* generalizes Dijkstra. Setting h=0 recovers Dijkstra
  exactly. Both use a min-heap ordered by cost.
- **Union-Find (Day 86)**: Can check bipartiteness via weighted union-find
  (tracking parity of path lengths), but BFS 2-coloring is simpler.
- **SCC (Day 87)**: SCC is for directed graphs; bipartiteness is for undirected.
  Both reveal fundamental graph structure.

## Checkpoint Questions

1. **Why does an odd-length cycle make a graph non-bipartite?** Walk through a
   3-cycle and show how 2-coloring fails.

2. **Why is Hopcroft-Karp faster than the naive augmenting path approach?** The
   naive approach finds one augmenting path at a time (O(V * E)). What does
   Hopcroft-Karp do differently to achieve O(E * sqrt(V))?

3. **What happens if you use an inadmissible heuristic with A\*?** Give an example
   where an overestimating heuristic causes A* to find a suboptimal path.

4. **A\* with Manhattan distance on a grid always finds the shortest path. But what
   if edges have different weights?** Is Manhattan still admissible?

5. **Konig's theorem says min vertex cover = max matching in bipartite graphs.
   Why does this fail for general (non-bipartite) graphs?** Give a counterexample.

6. **You're building a ride-sharing system that matches drivers to riders. Why is
   this a bipartite matching problem, and what real-world constraints would make
   it harder than the textbook version?**
