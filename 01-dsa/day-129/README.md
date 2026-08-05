# Day 129: Greedy on Graphs — Dijkstra, Kruskal, Prim

## Three Classical Greedy Graph Algorithms

These are not "DP that happens to live on a graph". They are **textbook
greedy**: at each step, pick the locally best edge or vertex, commit, and
never revisit. The correctness proofs are all variations on the exchange
argument.

| Algorithm | Greedy choice | Output |
|-----------|--------------|--------|
| **Dijkstra** | Settle nearest unvisited vertex | Shortest-path tree from source |
| **Kruskal** | Cheapest edge that doesn't form a cycle | Minimum spanning tree |
| **Prim** | Cheapest edge leaving the current tree | Minimum spanning tree |

References: day 82 (shortest paths) and day 85 (MST).

## Dijkstra as Greedy

### The greedy choice
At each step, among all unvisited vertices, pick the one whose tentative
distance is **smallest**. Mark it settled. Relax outgoing edges.

### Why is that greedy?
Because once settled, the algorithm never reconsiders that vertex. The
commitment is irrevocable.

### Correctness — exchange argument (sketch)
Let `S` = settled set. Let `u` be the next vertex picked (min `dist[u]`
among unsettled). Suppose for contradiction there's a shorter path to `u`
than `dist[u]`. That path must leave `S` at some edge `(x, y)` where
`x ∈ S, y ∉ S`. But `dist[y] >= dist[u]` (else we'd have picked `y`), so
the alleged shorter path is at least `dist[y] >= dist[u]`. Contradiction.

### Why does it require **non-negative** weights?
The exchange argument uses `dist[y] >= dist[u] >= dist[x]`. With negative
weights, an edge later in the path can decrease the total, breaking the
inequality. That's why Bellman-Ford (DP) is needed for negative weights.

### Real failure mode
Routing protocols (OSPF) use Dijkstra. They forbid negative metrics by
design — link cost is always `>= 1`. Otherwise they'd get count-to-infinity
loops, which is what RIP (Bellman-Ford) suffers from.

## MST: Both Algorithms Use the Same Cut Property

### The cut property (the heart of MST greediness)
**Theorem**: For any cut `(S, V\S)` of the graph, the **lightest edge**
crossing the cut is in **some** MST.

**Proof (exchange argument)**: Let `e = (u, v)` be the lightest edge across
the cut, `u ∈ S, v ∉ S`. Take any MST `T`. If `e ∈ T`, done. Else, adding
`e` to `T` creates a cycle. That cycle must cross the cut at least twice;
let `f` be another edge of the cycle crossing the cut. Then `weight(f) >= weight(e)`.
Replace `f` with `e` in `T` → still a spanning tree, weight no greater →
also an MST. ∎

Both Kruskal and Prim are direct applications of this.

### Kruskal's algorithm

```
sort edges by weight ascending
for each edge (u, v):
    if u and v are in different components:
        add (u, v) to MST
        union(u, v)
```

The greedy choice is "cheapest edge that doesn't form a cycle". The cut
property is applied with cut `(component(u), V \ component(u))`.

Uses **Union-Find** (day 86) for the component check.

Complexity: `O(E log E)` from the sort. The union-find operations are
`O(α(V))`, negligible.

### Prim's algorithm

```
start with any vertex in tree T = {s}
for V - 1 iterations:
    among all edges (u, v) with u ∈ T, v ∉ T:
        pick the lightest one
    add v to T
```

The greedy choice is "lightest edge crossing the current tree's cut".

Uses a **min-heap** keyed on best edge weight to each unvisited vertex.

Complexity: `O(E log V)` with a binary heap. With a Fibonacci heap,
`O(E + V log V)` (rarely worth the constants).

### Kruskal vs Prim — when each wins

| Use Kruskal when | Use Prim when |
|------------------|---------------|
| Edges are pre-sorted or sparse | Graph is dense, adj list is fast |
| You think edge-by-edge | You think tree-grows-vertex-by-vertex |
| You already need Union-Find | You already need a heap |

Both have the **same asymptotic** complexity on most representations. Both
make the **same greedy choice** under a different cut at each step.

## A Worked MST Example

```
Vertices: A B C D E
Edges (u, v, w):
    A-B 1
    A-C 4
    B-C 2
    B-D 5
    C-D 3
    C-E 6
    D-E 7
```

**Kruskal trace** (sort ascending: AB=1, BC=2, CD=3, AC=4, BD=5, CE=6, DE=7):
```
AB(1): A,B disjoint → take. Tree: {AB}
BC(2): A,C disjoint → take. Tree: {AB, BC}
CD(3): components {A,B,C}, {D} → take. Tree: {AB, BC, CD}
AC(4): A,C same → skip
BD(5): same → skip
CE(6): {A,B,C,D}, {E} → take. Tree: {AB, BC, CD, CE}
Done. Weight = 1+2+3+6 = 12
```

**Prim trace** (start at A; min-heap of frontier edges):
```
T = {A}; frontier: AB(1), AC(4)
Pick AB(1). T = {A,B}; frontier: BC(2), AC(4), BD(5)
Pick BC(2). T = {A,B,C}; frontier: CD(3), AC(4) [redundant], BD(5), CE(6)
Pick CD(3). T = {A,B,C,D}; frontier: CE(6), BD(5) [redundant], DE(7)
Pick CE(6). T = {A,B,C,D,E}. Done.
Weight = 1+2+3+6 = 12
```

Same MST. Same weight. Different traversal order.

## The Greedy Choice Property Trace

Every greedy step in these three algorithms is justified by **one shared
template**:

1. Identify the **right cut or frontier** (settled set, current MST, etc.)
2. Across that cut, the **lightest edge / nearest vertex** is in some
   optimal solution.
3. By induction, the algorithm builds an optimal solution.

If you ever forget the proof, just remember: cut + lightest edge + exchange.

## Failure Modes / Sharp Edges

- **Dijkstra with negative edges**: silently wrong. Use Bellman-Ford or SPFA.
- **Disconnected graph for MST**: get a *minimum spanning forest*. Both
  Kruskal and Prim handle this if you wrap them in a "for each unvisited
  vertex, restart" loop.
- **Non-unique MST**: if there are ties in edge weights, MST may not be
  unique. Both algorithms still find an MST, just possibly different ones.
- **Priority queue with stale entries**: in Prim/Dijkstra, when you decrease
  a key by inserting a new entry without removing the old one, you must
  skip stale entries on pop. Forgetting this is a classic bug.

## Checkpoint

1. State the cut property in your own words.
2. Why does Dijkstra fail on negative-weight edges? Give a 3-vertex example.
3. In Kruskal, why does the cycle check require Union-Find rather than DFS?
4. In Prim, after popping a stale heap entry, what do you do?
5. Suppose two edges have equal weight at a cut. Does the algorithm care?
   Does the MST cost care?
6. Sketch a graph where Kruskal builds the MST in a very different order
   than Prim does — but the result is the same.
