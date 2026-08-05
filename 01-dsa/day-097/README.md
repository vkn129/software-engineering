# Day 97: Min-Cost Max-Flow

## A Note On What Day 95 Promised

`day-095/README.md:162` lists "**Day 97** (2-SAT, coming)". That material was
delivered early: **day-087 already ships a complete Tarjan-based 2-SAT solver**
with assignment extraction (`day-087/scc.py:210-222`) and a practice exercise
that reimplements it (`day-087/practice.py:183`). Rather than re-tread it, day 97
takes the other open thread — the one day 92 and day 96 both point at.

## Why It Matters

Day 90 answered *how much* can flow from source to sink. Almost no real system
stops there. Bandwidth has a price. Drivers burn fuel. Shipping a container from
Rotterdam costs more than from Hamburg. The real question is:

> Of all the ways to push the maximum amount, which one is **cheapest**?

That is min-cost max-flow (MCMF), and it is the workhorse behind:

- **Ride dispatch** (Uber, Lyft) — riders to drivers minimising total ETA, where
  one driver may be offered several sequential trips (capacity > 1, so it is not
  a plain matching).
- **Airline crew pairing** — pilots to legs subject to duty-hour caps.
- **CDN / traffic engineering** — Google's B4 and similar WAN controllers solve
  cost-weighted flow to route traffic across expensive and cheap links.
- **Warehouse-to-store replenishment** — the classical *transportation problem*,
  which is MCMF with supplies on one side and demands on the other.
- **Multi-object tracking** — day 96 mentioned SORT/DeepSORT; the "tracking as
  network flow" formulation (Zhang et al. 2008) is literally MCMF over a
  detection graph.

## The Method: Successive Shortest Paths

Ford-Fulkerson says "find *any* augmenting path". Edmonds-Karp narrows it to
"find the path with the *fewest hops*". MCMF narrows it differently:

```
while an augmenting path exists:
    find the CHEAPEST source->sink path in the residual graph
    push the bottleneck amount along it
```

**Why cheapest-first is optimal, informally.** Maintain the invariant *the
current flow is a minimum-cost flow of its own value*. Zero flow trivially
satisfies it. If you augment along a cheapest path and the invariant somehow
broke, there would have to be a negative-cost cycle in the new residual graph —
and a negative residual cycle can only appear if you had *not* taken the cheapest
path. So the invariant survives every step, and it still holds when you stop.

## The Problem: Residual Edges Have Negative Cost

Day 90's residual graph has a reverse edge for every forward edge. In MCMF that
reverse edge carries cost `-c`: pushing flow back must refund what pushing it
forward charged, or the accounting is wrong.

So the residual graph has negative edges **even when the input does not**. That
kills Dijkstra. Dijkstra's whole argument is "the nearest unsettled node is
final" — one negative edge later in the graph makes that false.

Plain Bellman-Ford every iteration works, but costs `O(V*E)` per augmentation.

## Johnson Potentials — The Fix

Keep a **potential** `pot[v]` per node and search on the *reduced cost*:

```
w'(u, v) = w(u, v) + pot[u] - pot[v]
```

Two facts make this work:

1. **Non-negativity.** If `pot` holds valid shortest-path distances then
   `pot[v] <= pot[u] + w(u,v)` for every residual edge, so `w' >= 0`. Dijkstra is
   legal again.
2. **Ranking is preserved.** Along any path `s -> ... -> v`, the potential terms
   telescope:
   `sum w'  =  sum w + pot[s] - pot[v]`.
   Every `s->v` path shifts by the *same* constant, so the cheapest path under
   `w'` is the cheapest path under `w`. The reweighting changes the numbers, not
   the answer.

**Seeding the potentials.** The very first `pot` must come from Bellman-Ford,
because the *input* graph may itself contain negative-cost edges (a subsidy, a
negative-log-probability, a profit encoded as negative cost). One `O(V*E)` pass,
once.

**Maintaining them.** After each Dijkstra returns reduced distances `d`, set
`pot[v] += d[v]`. That keeps `pot` a valid shortest-distance vector for the *new*
residual graph, so the next Dijkstra is legal too. Newly created reverse edges
land at reduced cost exactly 0, which is what makes the update safe.

```
Bellman-Ford once   -> O(V*E)
then, per augmentation:
    Dijkstra        -> O(E log V)
    reprice pot     -> O(V)
    push bottleneck -> O(V)
```

## Termination

The loop ends when Dijkstra reports `dist[sink] == INF` — the sink is unreachable
in the residual graph, meaning **no augmenting path exists**. That is precisely
max-flow's stopping condition, so MCMF terminates whenever Edmonds-Karp would.

`min_cost_flow(s, t, max_flow=k)` adds a second exit: stop once `k` units are
sent. If it returns fewer than `k`, the network genuinely cannot carry more —
`min_cost_flow_exact` turns that into an explicit infeasibility answer instead of
a quietly short flow.

## Hungarian Is The Special Case

Day 96's Hungarian algorithm is not a different idea. It is MCMF on one specific
graph:

| MCMF, general | Hungarian (day 96) |
|---|---|
| any digraph | bipartite: workers one side, jobs the other |
| arbitrary capacities | every capacity is **1** |
| flow of any value | flow of exactly `n` (a perfect matching) |
| Johnson potentials `pot[v]` | dual variables `u[i]`, `v[j]` |
| zero-reduced-cost edge | **tight** edge, `u[i] + v[j] == C[i][j]` |
| Dijkstra per augmentation | Dijkstra per worker (`day-096/README.md:56-59`) |

Hungarian's `O(n^3)` comes from exploiting that structure — dense square matrix,
unit capacities, exactly `n` augmentations. MCMF gives up the structure and pays
for the generality. **Use Hungarian when the problem is one-to-one and square;
reach for MCMF the moment a worker can take two jobs, a job needs two workers, or
a route has a capacity of its own.**

`assignment_via_mcmf()` in the concept file solves day 96's matrices through the
flow engine and checks the totals against brute force, so the equivalence is
demonstrated rather than asserted.

## Relationship To Min-Cut (Day 93)

Day 93's duality still holds: the *value* of the flow MCMF finds is the min-cut
capacity, exactly as before. Cost does not change which cut is minimum — it only
selects **among the many maximum flows** that all saturate that same cut.
Max-flow picks one arbitrarily; MCMF picks the cheapest one. Cost has a dual of
its own (the potentials are it), but the *capacity* min-cut answer is untouched.

## Complexity

| Step | Time | Notes |
|------|------|-------|
| Bellman-Ford seeding | O(V·E) | once; tolerates negative input costs |
| Dijkstra per augmentation | O(E log V) | binary heap; legal thanks to potentials |
| Augmentations (integer capacities) | O(F) | F = value of the max flow |
| **Total (successive shortest paths)** | **O(V·E + F·E·log V)** | pseudo-polynomial in F |
| Capacity-scaling MCMF | O(E² log V log U) | strongly better for huge capacities |
| Hungarian (assignment only) | O(n³) | the special case above |
| Cycle-cancelling | O(V·E²·C·U) | handles negative cycles; we refuse them |

`F` in the bound is why this is only *pseudo*-polynomial: capacities of `10^9` on
a graph of ten edges mean up to `10^9` augmentations in the pathological case.
Capacity scaling exists for exactly that.

## Failure Modes

1. **Negative cycles in the input.** Successive shortest paths assumes the zero
   flow is already cost-optimal for its value; a negative cycle makes that false
   and the answer is silently wrong. We detect it in the Bellman-Ford seed and
   raise `NegativeCycleError`. Cycle-cancelling algorithms are the real fix.
2. **Floating-point costs.** Same lesson as `day-093/README.md:115`: reduced-cost
   comparisons accumulate error, the "non-negative" invariant fails by `1e-16`,
   and Dijkstra settles a node too early. Use integers — scale to cents, grams,
   milliseconds.
3. **`INF - INF` on unreachable nodes.** Nodes Bellman-Ford never reached hold
   `INF`; computing a reduced cost across them yields `nan` and corrupts the heap
   ordering. Skip those edges explicitly.
4. **Forgetting to reprice after each Dijkstra.** The code still runs, produces
   plausible-looking flows, and returns wrong costs — the worst failure shape.
   The `reduced_costs_nonnegative` exercise in the practice file exists to catch
   it.
5. **Accepting a short flow.** `min_cost_flow(s, t, 10)` returning `(7, ...)`
   means the demand cannot be met. An assignment that leaves a job unstaffed is
   not a cheap assignment; it is a different problem.
6. **Unit-capacity blindness.** Modelling "worker takes at most one job" needs
   capacity 1 on the source→worker edge. Leave it unbounded and the optimiser
   happily hands every job to the single cheapest worker.
7. **Anti-parallel edges (`u->v` and `v->u` both in the input).** The `i ^ 1`
   pairing handles them correctly *because* each `add_edge` allocates its own
   pair — but sharing one slot between the two directions, a common
   "optimisation", silently merges them.

## Checkpoint Questions

1. Why can't you run Dijkstra directly on a residual graph, even when every
   *input* cost is non-negative?
2. Show that `sum w'` along an `s->v` path equals `sum w + pot[s] - pot[v]`. Which
   step of that derivation guarantees the cheapest path is unchanged?
3. After augmenting, a new reverse edge appears with cost `-c`. Show its reduced
   cost is exactly 0 under the repriced potentials. Why does that matter?
4. Why is Bellman-Ford needed for the *first* potential vector but never again?
5. State the graph transformation that turns day 96's `n x n` cost matrix into a
   flow network. Which single parameter, if changed, stops it being a matching?
6. Max-flow and MCMF find flows of the same value on the same graph. What
   exactly does the cost function decide, given that the min cut is unaffected?
7. Capacities are `10^9` and there are twelve edges. Estimate the augmentation
   count for successive shortest paths, and explain why that is a real problem
   rather than a theoretical one.
8. You need "each worker gets at most 3 jobs, each job needs exactly 2 workers."
   Sketch the network. Why can Hungarian not express this?
