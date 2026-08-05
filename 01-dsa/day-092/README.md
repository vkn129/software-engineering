# Day 92: Hopcroft-Karp Bipartite Matching

## Why a Better Matching Algorithm

Day 89 built basic bipartite matching via repeated DFS augmenting paths:
**O(V * E)** in the worst case. That's fine for thousands of nodes, but the
moment you push toward 10^5 vertices it stalls — and bipartite matching is
the backbone of real scheduling systems (driver-to-ride, ad-to-slot,
nurse-to-shift). Hopcroft-Karp pushes the bound to **O(E * sqrt(V))**, which
in practice is 10-100x faster on dense instances.

The trick: instead of finding **one** augmenting path per iteration,
Hopcroft-Karp finds a **maximal set of vertex-disjoint shortest augmenting
paths** in one BFS+DFS phase.

## The Math: Why sqrt(V)?

Hopcroft and Karp (1973) proved two key facts:

1. After O(sqrt(V)) phases, every remaining augmenting path has length
   > sqrt(V).
2. There can be at most O(sqrt(V)) augmenting paths left at that point
   (because they're vertex-disjoint and each consumes >= sqrt(V) vertices).

So total phases <= 2 * sqrt(V), and each phase is O(E). Total: **O(E * sqrt(V))**.

The deeper intuition: long augmenting paths are "rare" once the matching is
mostly built. Length bounds + disjointness gives the sqrt.

## Algorithm Structure

```
1. M = empty matching
2. Repeat:
     a. BFS from all unmatched left vertices, layering by alternating-path
        distance. Stop when first unmatched right vertex is reached at
        layer L.
     b. If no such L found -> M is maximum, return.
     c. DFS from each unmatched left vertex, finding vertex-disjoint
        augmenting paths of length exactly L. Augment along each.
```

Each phase: O(V + E) for BFS, O(V + E) for DFS layer. So O(E) per phase
(assuming E >= V — usually true).

## Comparison to Day 89 (Basic Bipartite)

| Aspect | Basic (Day 89) | Hopcroft-Karp (Day 92) |
|--------|----------------|------------------------|
| Approach | One augmenting path per iter | Many disjoint paths per phase |
| Phases | O(V) | O(sqrt(V)) |
| Per phase | O(E) DFS | O(E) BFS + O(E) DFS |
| Total time | O(V * E) | O(E * sqrt(V)) |
| Code complexity | Low | Medium |
| When to use | V < 1000 | V > 10000, dense E |

## Complexity Table

| Operation | Time | Space |
|-----------|------|-------|
| BFS phase | O(V + E) | O(V) |
| DFS phase | O(V + E) | O(V) recursion |
| Total | **O(E * sqrt(V))** | O(V + E) |

## Failure Modes

1. **Disconnected graphs**: harmless — phases just skip unreachable nodes.
2. **Multi-edges**: not allowed; use adjacency sets to dedupe.
3. **Self-loops**: undefined for bipartite; reject in preprocessing.
4. **Recursion depth**: DFS can hit Python's 1000-frame limit on huge V.
   Either bump `sys.setrecursionlimit` or convert DFS to an explicit stack.
5. **Sparse graphs (E ~ V)**: speedup is modest — basic Hungarian-ish DFS
   may even win on tiny inputs due to constant factors.
6. **Worst-case adversarial input**: bipartite graphs with all augmenting
   paths of equal length still hit the sqrt(V) bound — no degenerate case
   exists (this is the theorem's strength).

## Real-World Usage

| System | Application | Why Hopcroft-Karp |
|--------|------------|-------------------|
| **Uber/Lyft dispatch** | Driver-rider matching per time slice | Many disjoint pairs, low latency |
| **Google Ads** | Ad-impression to bidder slot assignment | 10^6 bidders, must be sub-second |
| **Hospital scheduling** | Nurses to shifts (with eligibility constraints) | Dense feasibility graph |
| **Compiler register allocation** | Variables to physical registers (interference-free) | Speed matters in JIT |
| **Recommender systems** | Pairing content slots with users in a batch | Throughput per phase |
| **Network flow preconditioner** | Initial matching before max-flow refinement | Faster cold start |

## Connection to Other Days

- **Day 89** (basic bipartite matching) — direct ancestor; we beat its bound.
- **Day 90** (network flow) — bipartite matching is a unit-capacity flow
  instance; Hopcroft-Karp is essentially Dinic's algorithm specialized to
  unit-capacity bipartite graphs.
- **Day 91** (dependency resolver capstone) — assignment with constraints
  uses matching as a primitive.
- **Day 79-80** (BFS/DFS) — the two phases are layered BFS + layer-DFS.
- **Day 96** (Hungarian, coming) — weighted variant; Hopcroft-Karp is the
  unweighted special case.
- **Day 98** (task assigner capstone) — combines matching with cost.

## Checkpoint Questions

1. Why is finding **shortest** augmenting paths (not arbitrary ones) the
   key to the sqrt(V) bound? What goes wrong if BFS layers aren't enforced?
2. In the DFS phase, why do we require paths to be **vertex-disjoint**
   instead of edge-disjoint?
3. Suppose every augmenting path has length 1 (i.e., a perfect matching is
   one edge away). How many phases does Hopcroft-Karp run? Why?
4. If E = V (very sparse), is Hopcroft-Karp still faster than basic? When
   does the crossover happen?
5. Hopcroft-Karp is Dinic's algorithm in disguise. What's the unit-capacity
   property that makes Dinic O(E * sqrt(V)) here?
6. In Uber's dispatch, why re-run matching every few seconds rather than
   maintaining an incremental matching as drivers/riders arrive?
