# Day 93: Minimum Cut & the Max-Flow Min-Cut Theorem

## The Big Duality

Day 90 built network flow (Ford-Fulkerson, Edmonds-Karp). Today we discover
that **every max-flow problem secretly solves a min-cut problem** — and
vice versa. This duality is one of the most useful results in CS because
it lets you **prove** that your flow is optimal by exhibiting a matching cut.

> **Max-Flow Min-Cut Theorem (Ford-Fulkerson, 1956)**:
> In any flow network, the maximum value of an s-t flow equals the minimum
> capacity of an s-t cut.

This isn't just a theoretical curiosity — it's how every modern image
segmentation pipeline works.

## What Is a Cut?

An **s-t cut** partitions vertices into two sets `S` (containing source `s`)
and `T` (containing sink `t`). The cut's **capacity** is the sum of
capacities of edges going **from S to T** (one direction only).

```
   S          T
  +---+ 5   +---+
  | s |---->| a |
  +---+     +---+
    | 3       | 2
    v         v
  +---+ 4   +---+
  | b |---->| t |
  +---+     +---+

Cut capacity = sum of edges S->T crossings.
```

If `S = {s, b}` and `T = {a, t}`, the crossing edges are `s->a` (cap 5)
and `b->t` (cap 4), so cut capacity = 9.

Note: edges **T->S** don't count toward capacity. Direction matters.

## Why the Duality Holds (Intuition)

Any flow from `s` to `t` must cross **every** s-t cut. So flow value <= cut
capacity for **every** cut. Therefore:

```
max flow <= min cut
```

The deep result: this is tight. There always exists a cut whose capacity
equals max flow.

**Constructive proof**: after running max-flow, define
- `S` = vertices reachable from `s` in the **residual graph**.
- `T` = everything else.

Then `t` must be in `T` (otherwise we'd have an augmenting path, contradicting
max flow). Every edge from `S` to `T` is **saturated** (capacity = flow).
Every edge from `T` to `S` carries 0 flow (otherwise the back-edge in the
residual would let us cross back into `S`). So `cut capacity = total flow
out of S = max flow`. QED.

## Finding the Min Cut

```
1. Compute max flow s -> t (using day-90 Edmonds-Karp / day-92 Hopcroft-Karp).
2. Build residual graph.
3. BFS from s in residual; let S = visited set.
4. Min cut = { (u, v) original edges : u in S, v not in S }.
```

The cut **capacity** is the max-flow value. The cut **edges** are the
saturated ones leaving S.

## Complexity Table

| Step | Time | Notes |
|------|------|-------|
| Max-flow (Edmonds-Karp) | O(V * E^2) | Day 90 |
| Residual BFS | O(V + E) | Identifies S |
| Edge enumeration | O(E) | Filter S -> T edges |
| **Total** | **O(V * E^2)** | Dominated by max-flow |

## Real-World: Image Segmentation

Given an image, partition pixels into **foreground** (e.g., a person) and
**background**. Build a graph:

- One vertex per pixel.
- A virtual `source` connected to each pixel with capacity = "foreground
  likelihood" (color similarity to known foreground).
- A virtual `sink` connected to each pixel with capacity = "background
  likelihood."
- Adjacent pixels connected by edges with capacity = "smoothness" (high if
  similar color — penalizes splitting them).

**Min s-t cut** = cheapest way to disconnect foreground from background =
optimal segmentation that respects pixel similarity. This is exactly how
GrabCut and many medical-imaging pipelines work.

```
  source
  / | \
 / .. \  foreground likelihood
v       v
P1 --- P2 --- P3   (smoothness edges)
v       v
 \ .. /  background likelihood
  \ | /
   sink
```

## Failure Modes

1. **Floating-point capacities**: never use float. Use integers (scale up if
   needed) — augmenting on floats can fail to terminate.
2. **Multiple min cuts**: there can be many; the residual-BFS choice gives
   the cut **nearest to s**. To find the one nearest to t, reverse BFS.
3. **No s-t path exists**: max flow = 0, min cut = 0 (empty cut). Edge case
   for naive code.
4. **Anti-parallel edges (u->v and v->u)**: handle each direction
   separately in the residual graph. Common bug.
5. **Disconnected graph**: harmless; t simply unreachable, flow = 0.
6. **Cut on undirected graphs**: replace each undirected edge with two
   directed edges of equal capacity. Min cut still works but semantics
   shift (it counts the undirected edge once).

## Real-World Usage

| System | Application | Why Min-Cut |
|--------|------------|-------------|
| **GrabCut / medical imaging** | Foreground/background segmentation | Pixel similarity = capacities |
| **VLSI design** | Partition circuit to minimize cross-chip wires | Min-cut = min wire crossings |
| **Network reliability** | Find bottleneck links | Min cut = weakest links |
| **Data center load** | Find cluster boundaries | Min cut = where to split traffic |
| **Project selection** | "Closure problem" (which projects to fund) | Reduces to min cut |
| **Stereo vision** | Disparity map smoothing | Multi-label graph cut |

## Comparison: Max-Flow vs Min-Cut Algorithms

| Goal | Algorithm | Complexity |
|------|-----------|-----------|
| Max flow | Edmonds-Karp | O(V*E^2) |
| Max flow | Dinic | O(V^2 * E) |
| Max flow | Push-relabel | O(V^2 * sqrt(E)) |
| Min cut (s-t) | Run max-flow + BFS | Same as max-flow |
| Global min cut | Stoer-Wagner | O(V^3) |

## Connection to Other Days

- **Day 90** (network flow) — direct foundation; min cut is dual.
- **Day 92** (Hopcroft-Karp) — bipartite matching is unit-capacity max flow;
  min vertex cover (Konig) is its min cut.
- **Day 87** (SCC) — uses similar two-pass DFS structure for residual
  reachability.
- **Day 79** (BFS) — used in the cut-finding step.
- **Day 86** (Union-Find) — alternative tool for connectivity post-cut.

## Checkpoint Questions

1. Why does max flow <= min cut **always** hold (the easy direction)? Show
   the one-line argument.
2. After running max flow, why must vertex `t` be unreachable from `s` in
   the residual graph?
3. In image segmentation, what happens if smoothness weights are too high
   relative to source/sink weights? What if too low?
4. There can be multiple min cuts. How do you find the one closest to the
   **sink** instead of the source?
5. For an undirected graph, why do we replace each edge `(u, v, w)` with
   **two** directed edges `(u, v, w)` and `(v, u, w)` rather than one?
6. The "project selection" problem: each project has revenue/cost; project
   A requires project B; maximize profit. Sketch how this reduces to min-cut.
