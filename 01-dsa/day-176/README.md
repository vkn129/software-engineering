# Day 176: Approximation Algorithms

## Why Approximation Exists

Some problems are NP-hard — no polynomial algorithm is known and none is
believed to exist. But businesses still need answers. Approximation
algorithms trade **exactness for tractability**: they run in polynomial
time and return a solution provably within a known factor of optimal.

The two algorithms here are classics:

- **2-approximation for Vertex Cover** via maximal matching (Gavril, 1974)
- **Christofides for Metric TSP** — 1.5-approximation (Christofides, 1976)

For 50 years, Christofides was the best known approximation for metric
TSP. In 2020, Karlin–Klein–Gharan beat it by a microscopic amount. That's
how hard improvement is.

## Approximation Ratio

For a minimization problem, an algorithm `A` has approximation ratio `ρ`
if for every input `I`:

```
A(I) <= ρ * OPT(I)
```

- `ρ = 1`: exact
- `ρ = 2`: at most twice optimal
- `ρ = 1.5`: at most 50% over optimal

Smaller is better. The ratio must be a **proven worst-case bound**, not
empirical average.

## Vertex Cover via Matching

**Problem:** Given graph `G=(V,E)`, find smallest `S ⊆ V` such that every
edge has at least one endpoint in `S`.

NP-hard. Best known approximation ratio is **2 - Θ(log log n / log n)**.
Beating `2 - ε` would refute the Unique Games Conjecture.

**The algorithm — disarmingly simple:**

```
S = {}
M = maximal matching of G   # greedy: pick edges, remove endpoints
for each edge (u, v) in M:
    add u and v to S
return S
```

**Why 2-approximation?**

1. `M` is a matching: edges in `M` share no endpoints, so `|S| = 2|M|`.
2. Any vertex cover must include at least one endpoint of each edge in
   `M`. Since `M`'s edges are disjoint, `OPT >= |M|`.
3. Therefore `|S| = 2|M| <= 2·OPT`.

That's the entire proof. Three lines. The algorithm is also `O(V+E)` —
faster than nearly any exact heuristic.

## Christofides for Metric TSP

**Problem:** Given complete graph with metric edge weights (triangle
inequality holds), find shortest Hamiltonian cycle.

**General TSP** is inapproximable within any constant factor (unless
P=NP). But for **metric TSP**, Christofides gives 1.5.

**The algorithm:**

```
1. Compute MST T of G.
2. O = vertices with odd degree in T.
   (Handshake lemma: |O| is even.)
3. Find minimum-weight perfect matching M on O (in G).
4. H = T ∪ M  -- multigraph where every vertex has even degree.
5. Find Eulerian circuit in H.
6. Shortcut repeated vertices to get Hamiltonian cycle.
```

**Why 1.5?**

- `cost(T) <= OPT` (MST is cheaper than any spanning subgraph of a
  Hamiltonian cycle minus one edge).
- `cost(M) <= OPT / 2` (the optimal tour restricted to `O` decomposes
  into two perfect matchings on `O`; the cheaper has cost `<= OPT/2`).
- Shortcutting only reduces cost (triangle inequality).
- Total: `<= OPT + OPT/2 = 1.5 * OPT`.

**Practical wrinkle:** step 3 — minimum-weight perfect matching — is
itself `O(n^3)` via Edmonds' blossom algorithm. Real-world Christofides
uses a greedy matching instead, giving a worse ratio but acceptable
runtime. We do the same here.

## Other Approximation Patterns

| Pattern | Example | Ratio |
|---|---|---|
| Greedy | Set cover | `H_n ≈ ln n` |
| LP relaxation + rounding | Vertex cover | 2 |
| Local search | Max cut | 0.5 (trivially) |
| Primal-dual | Steiner tree | 2 |
| PTAS | Euclidean TSP | `1+ε` (any ε) |
| FPTAS | Knapsack | `1+ε` in `poly(n, 1/ε)` |

## Failure Modes

1. **Worst-case isn't average-case.** Christofides averages much better
   than 1.5 in practice. The bound is pessimistic.
2. **The triangle inequality is load-bearing.** Drop it and Christofides
   gives no guarantee — the problem becomes inapproximable.
3. **Greedy matching != minimum matching.** Our greedy matching breaks
   the 1.5 proof. We get a heuristic, not an approximation.
4. **Reduction != approximation.** A polynomial reduction `A -> B` does
   NOT preserve approximation ratios in general. Need
   approximation-preserving reductions (L-reductions, AP-reductions).

## Checkpoint Questions

1. The vertex-cover algorithm pairs up matching endpoints — both go into
   the cover. Could you save by picking only one endpoint per matched
   edge? Why does the proof break?
2. Why is `|O|` (odd-degree vertices in MST) always even? State the
   theorem.
3. In Christofides, why does "shortcutting" the Eulerian circuit not
   increase cost?
4. What's the gap between Christofides and the new 1.5-ε bound? Why was
   that paper such a big deal?
5. Set cover's `ln n` ratio is tight unless P=NP. What does "tight"
   mean here — for the algorithm or for the problem?
6. When would you choose a slower exact solver (branch-and-bound, ILP)
   over a fast approximation? List two concrete situations.
