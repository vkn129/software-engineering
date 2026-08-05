# Day 96: Hungarian Algorithm — Optimal Assignment

## The Problem

You have **n workers** and **n jobs**. Worker `i` doing job `j` has cost
`C[i][j]`. Find the **one-to-one assignment** of workers to jobs that
**minimizes total cost** (or maximizes profit — same problem with negated
costs).

This is the **assignment problem**, a special case of weighted bipartite
matching. Day 92's Hopcroft-Karp solves the **unweighted** version. When
edges carry weights, we need something stronger.

The **Hungarian algorithm** (Kuhn 1955, Munkres 1957) solves it in **O(n^3)**.
That's a huge deal: the brute force (try all `n!` permutations) is
astronomical at n=15 already.

## Why O(n^3) Is Optimal-ish

The assignment problem can be cast as an LP:
```
min sum_{i,j} C[i,j] * x[i,j]
s.t. sum_j x[i,j] = 1 forall i
     sum_i x[i,j] = 1 forall j
     x[i,j] >= 0
```

Although LP in general is polynomial but heavy, this LP has integral
optimum (totally unimodular constraint matrix), and Hungarian exploits the
structure to hit O(n^3). The best known bound is O(n^3) — many decades of
research haven't improved it asymptotically.

## Core Idea: Potentials and Tight Edges

Maintain dual variables `u[i]` (per worker) and `v[j]` (per job) such that:
```
u[i] + v[j] <= C[i][j]    for all i, j   (feasibility)
```

An edge `(i, j)` is **tight** iff `u[i] + v[j] == C[i][j]`. The Hungarian
algorithm finds a **perfect matching on tight edges**. By LP duality, such
a matching minimizes total cost.

The algorithm alternates between:
1. **Primal step**: try to extend the matching by augmenting on tight edges.
2. **Dual step**: when no augmenting path on tight edges exists, adjust
   `u, v` so that **new** tight edges appear (in the direction the BFS
   was extending), without breaking feasibility.

After O(n) rounds, we have a perfect matching of minimum cost.

## The Compact O(n^3) Variant

We implement a popular Russian-Olympiad-style version:
- Iterate over workers `i = 0..n-1` (one per outer loop).
- For each `i`, run a single-source shortest-path tree (modified Dijkstra)
  in the residual bipartite graph with **reduced costs**
  `c[i][j] - u[i] - v[j]` (these are non-negative by feasibility).
- Augment along the found path; update potentials.

This avoids the labyrinthine "primal/dual" formulation in textbooks while
keeping the same complexity.

## Complexity Table

| Algorithm | Time | Space | Notes |
|-----------|------|-------|-------|
| Brute force | O(n!) | O(n) | unusable past n=12 |
| Hopcroft-Karp (unweighted) | O(E*sqrt(V)) | O(V+E) | ignores weights |
| Min-cost max-flow | O(V*E*log V) | O(V+E) | more general |
| **Hungarian (this day)** | **O(n^3)** | O(n^2) | weighted, dense, square |
| Jonker-Volgenant | O(n^3) | O(n^2) | constant-factor faster |
| Auction algorithm | O(n^3 log nC) | O(n) | online, parallelizable |

## Rectangular Variants

If you have `m` workers and `n` jobs with `m != n`, pad the smaller side
with dummy entries of cost 0 (or +infinity if "not assigning" is forbidden).
Then solve the n x n version.

## Failure Modes

1. **Floating-point**: dual updates accumulate errors. Use integers when
   possible; in finance/logistics, costs are often cents/grams anyway.
2. **Infeasible (forbidden assignments)**: set those entries to a huge
   sentinel (`10**9`) so they're never picked. Pure `inf` can cause NaN
   arithmetic.
3. **Cost matrix not square**: must pad. Forgetting to pad gives garbage.
4. **Maximizing instead of minimizing**: negate the cost matrix
   (after offsetting to keep non-negative if your impl assumes that).
5. **Degenerate ties**: many tight edges -> many valid matchings, all
   optimal. Algorithm picks deterministically; downstream must not
   assume a specific one.
6. **Large n**: O(n^3) means n=1000 is ~10^9 ops — borderline. n=300 fine.

## Real-World Usage

| System | Application | Why Hungarian |
|--------|------------|---------------|
| **Uber dispatch** | Drivers to riders minimizing ETA-cost | Many constrained pairings |
| **NFL / NBA scheduling** | Teams to game slots | Optimal cost matching |
| **Manufacturing** | Tasks to machines minimizing setup time | Classic assignment |
| **Crew scheduling** | Pilots to flights minimizing overtime | Cost-aware bipartite |
| **Wedding seating** | Guests to seats with preferences | "Stable" extensions |
| **Cloud orchestration** | Pods to nodes minimizing latency | k8s scheduler primitives |
| **Computer vision** | Track-to-detection across video frames | Hungarian = MOT algorithm |

## A Word on MOT (Multi-Object Tracking)

Modern object trackers (e.g., SORT, DeepSORT) use Hungarian every frame to
associate **previously tracked objects** to **new detections**. Cost = IoU
distance or appearance embedding distance. Without Hungarian, your tracker
would jitter; with it, IDs stay stable.

## Connection to Other Days

- **Day 89** (bipartite matching, basic) — unweighted ancestor.
- **Day 92** (Hopcroft-Karp) — unweighted, fastest in V.
- **Day 90** (network flow) — Hungarian is a primal-dual special case;
  min-cost max-flow generalizes it.
- **Day 84** (Dijkstra) — the Hungarian variant we implement is a Dijkstra
  in disguise on the reduced-cost graph.
- **Day 86** (Union-Find) — not directly used here, but its potentials
  technique is conceptually similar to ranks.
- **Day 98** (task assigner capstone, coming) — combines this with
  constraints.

## Checkpoint Questions

1. Why is the brute-force O(n!) and not O(n^n)? Walk through the counting.
2. What does it mean for an edge to be **tight**, and why must the optimal
   matching use only tight edges?
3. In the dual update step, you change `u` and `v` by some `delta`. Where
   does `delta` come from? (Hint: minimum slack.)
4. For rectangular matrices, you pad with zeros. What if the "real" entries
   could be 0 too? Why is that fine?
5. Compare Hungarian vs min-cost max-flow for the assignment problem. When
   would you choose MCMF instead?
6. In Uber's dispatch, the cost matrix changes every few seconds. Why don't
   they incrementally maintain the assignment — what algorithmic property
   makes that hard?
