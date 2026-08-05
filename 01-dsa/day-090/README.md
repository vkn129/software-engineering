# Day 90: Network Flow

## Why This Matters

Network flow is one of the most powerful algorithmic frameworks in computer science.
The core question: **how much "stuff" can you push through a network from a source
to a sink?** The "stuff" can be data packets, water, traffic, or even abstract
assignments. What makes flow theory remarkable is that a single algorithmic idea
solves a huge family of seemingly unrelated problems:

- **Network routing**: Maximum bandwidth between two servers
- **Bipartite matching**: Assigning workers to jobs, students to projects
- **Image segmentation**: Separating foreground from background (min cut)
- **Baseball elimination**: Can a team still win the league?
- **Airline scheduling**: Maximum flights with crew constraints

The key insight: **max-flow and min-cut are the same number** (the max-flow
min-cut theorem). This duality is one of the deepest results in combinatorial
optimization.

## The Max-Flow Problem

Given a directed graph with edge capacities, find the maximum flow from source `s`
to sink `t` such that:
1. **Capacity constraint**: Flow on each edge <= its capacity
2. **Flow conservation**: For every vertex (except s and t), flow in = flow out

```
        capacity
    A ----10----> B
   /|              |\
  / |              | \
s --8--> C --5--> D --7--> t
  \      |        ^      /
   \     3        |     /
    \    |        6    /
     +-> E ---4--+  <-+

Question: What's the maximum total flow from s to t?
```

## Residual Graphs and Augmenting Paths

The **residual graph** tracks remaining capacity. For each edge with capacity `c`
and current flow `f`:
- **Forward edge**: residual capacity = `c - f` (room to push more)
- **Reverse edge**: residual capacity = `f` (room to "undo" flow)

```
Original:             Residual (after sending 3 units A->B):
A --[cap=5]--> B      A --[2]--> B      (5-3 = 2 remaining)
                      A <--[3]-- B      (can undo 3 units)
```

An **augmenting path** is any path from s to t in the residual graph.
The bottleneck (minimum residual capacity along the path) is how much
additional flow we can push.

## Ford-Fulkerson Method

The general approach:
1. Start with zero flow
2. While there exists an augmenting path from s to t in the residual graph:
   - Find the bottleneck capacity along the path
   - Push that much flow along the path
   - Update the residual graph
3. Return total flow

**Problem**: If augmenting paths are chosen poorly (e.g., via DFS), the algorithm
may take O(E * max_flow) time -- which can be exponential in the input size.

## Edmonds-Karp Algorithm (BFS-based)

Edmonds-Karp fixes Ford-Fulkerson by always choosing the **shortest augmenting
path** (fewest edges) using BFS. This guarantees O(VE^2) time regardless of
capacity values.

```
Why BFS works better:

DFS might find:          BFS always finds:
s -> A -> B -> t         s -> t  (shortest first)
  long winding path        direct path

BFS guarantees shortest path distances never decrease,
so after at most O(VE) augmentations, we're done.
Each BFS is O(E), giving O(VE^2) total.
```

## Max-Flow Min-Cut Theorem

**Theorem**: The maximum flow from s to t equals the minimum capacity of any
s-t cut (a partition of vertices into S and T where s is in S and t is in T).

```
Min cut example:
    A ---10--- B
   / \          \
  s   5    cut   t
   \ /    here  /
    C ---3--- D

If we cut edges A->B (10) and C->D (3), total = 13.
The max flow is also 13. They're always equal.
```

**Finding the min cut**: After running max flow, do BFS/DFS from s in the
residual graph. Vertices reachable from s form set S; the rest form set T.
The cut edges go from S to T in the original graph.

## Bipartite Matching as Flow

Any bipartite matching problem reduces to max flow:

```
Original bipartite graph:     Flow network:
L1 --- R1                     s -> L1 -> R1 -> t
L1 --- R2                     s -> L1 -> R2 -> t
L2 --- R2                     s -> L2 -> R2 -> t
L2 --- R3                     s -> L2 -> R3 -> t
L3 --- R3                     s -> L3 -> R3 -> t

All edge capacities = 1
Max flow = max matching size
```

Add a super-source connected to all left vertices and a super-sink connected
to all right vertices. Each edge has capacity 1. The max flow equals the
maximum matching size, and the flow on edges reveals the matching.

## Complexity

| Algorithm | Time | Space | Notes |
|-----------|------|-------|-------|
| Ford-Fulkerson (DFS) | O(E * max_flow) | O(V + E) | Can be slow with large capacities |
| Edmonds-Karp (BFS) | O(VE^2) | O(V + E) | Polynomial, practical for moderate graphs |
| Dinic's | O(V^2 * E) | O(V + E) | Better for dense graphs |
| Push-relabel | O(V^2 * E) or O(V^3) | O(V + E) | Best for very dense graphs |
| Find min cut | O(VE^2) | O(V + E) | Run Edmonds-Karp + one BFS |
| Bipartite matching via flow | O(V * E) | O(V + E) | Special structure helps |

## Connection to Other Days

- **BFS/DFS (Day 80)**: Edmonds-Karp is BFS applied to residual graphs.
  Ford-Fulkerson with DFS can be pathologically slow.
- **Shortest paths (Day 82)**: Augmenting paths are shortest paths in
  unweighted residual graphs. Min-cost flow uses Bellman-Ford instead.
- **Bipartite matching (Day 90 practice)**: Hopcroft-Karp is faster than
  flow-based matching, but flow reduction proves correctness.
- **SCC / Tarjan (Day 87)**: Both are graph decomposition techniques.
  Condensation DAG relates to flow structure.
- **Articulation points (Day 88)**: Min cut generalizes the idea of
  finding critical edges/vertices that disconnect the graph.

## Checkpoint Questions

1. **Why do we need reverse edges in the residual graph?** Give a concrete
   example where Ford-Fulkerson without reverse edges finds a suboptimal flow.

2. **Why does BFS (Edmonds-Karp) guarantee O(VE^2) while DFS (basic
   Ford-Fulkerson) doesn't?** What property of shortest paths makes BFS
   terminate in O(VE) augmentations?

3. **Prove intuitively why max-flow = min-cut.** Why can't the max flow
   exceed the min cut? Why can't the min cut exceed the max flow?

4. **How does the bipartite matching reduction to flow work?** Why must all
   capacities be 1? What would happen with capacity > 1?

5. **Can Edmonds-Karp handle graphs with cycles?** How do residual graph
   reverse edges interact with existing cycles in the original graph?

6. **Your company's network has 500 routers and 2000 links. The CEO asks:
   what's the minimum number of links an attacker must cut to disconnect
   headquarters from the data center? How do you solve this, and what's
   the runtime?**
