# Day 122: Bitmask DP

## When Bitmask DP

Bitmask DP solves problems where:
1. The state needs to track **which subset of elements** has been used / visited / assigned.
2. The number of elements is **small** (typically n ≤ 20).
3. The naive recursion would re-visit the same subset many times.

Why n ≤ 20? Because a subset of n elements becomes a bitmask in `[0, 2^n)`.
At n = 20, that's ~1M states. At n = 25, 33M — borderline.
At n = 30, 1B — too much.

Bitmask DP is the bridge between "obviously exponential" (try all
permutations: n!) and "polynomial in 2^n" (try all subsets and reuse
work). It turns O(n!) into O(2^n × poly(n)).

## State Design: Travelling Salesman (TSP)

n cities, distance matrix `dist[i][j]`. Find the shortest tour that
visits every city exactly once and returns to start.

**Naive**: n! permutations, way too many.

**State**: `dp[mask][i]` = min cost of a path that:
- Has visited exactly the cities in `mask`
- Ends at city `i` (where `i` must be in `mask`)

**Recurrence**:
```
dp[mask][i] = min over j in mask, j != i:
                 dp[mask ^ (1 << i)][j] + dist[j][i]
```

**Base**: `dp[{0}][0] = 0` — start at city 0 with only city 0 visited.

**Answer**: `min over i != 0: dp[full_mask][i] + dist[i][0]`.

**Complexity**: O(2^n × n^2). For n = 20: 4M × 400 = 1.6B ops, slow but doable.

### Subproblem Dependency Graph

```
            dp[mask][i]
                |
                v
       dp[mask ^ (1<<i)][j]    for every j in mask \ {i}
                |
                v
       smaller mask (fewer bits set)
```

Iterating masks in increasing order of value ensures every dependency
is computed first (smaller masks have lower numeric values when bit `i`
of `mask` is set and we look at `mask ^ (1 << i)`).

Actually — we iterate masks in any order **such that `mask ^ (1 << i) < mask`**,
which is always true because we're removing a set bit. So **plain ascending
numerical order** works.

## State Design: Task Assignment

n people, n tasks. `cost[i][j]` is cost of assigning person i to task j.
Each person gets exactly one task, each task assigned exactly once.
Minimize total cost.

**State**: process people in order. `dp[mask]` = min cost to assign
the first `popcount(mask)` people such that the set of tasks they took
is exactly `mask`.

**Recurrence**:
```
For each person i (= popcount(mask) - 1 at fill time):
   dp[mask] = min over j in mask:
                 dp[mask ^ (1 << j)] + cost[i][j]
```

**Base**: `dp[0] = 0` (no people, no tasks).

**Answer**: `dp[(1 << n) - 1]`.

**Complexity**: O(2^n × n). Much faster than TSP because we don't
need a "current location" — order doesn't matter.

### Why Fewer Dimensions Than TSP

In task assignment, the cost of person i taking task j is independent
of who took what before. So we don't need to track *who is currently
holding the pen* — only *which tasks are taken*.

In TSP, the next edge cost depends on the **current city**. That's why
TSP needs the extra `i` dimension.

## Bit Manipulation Primer (for DP)

| Op | Meaning |
|----|---------|
| `mask & (1 << i)` | is bit i set? |
| `mask | (1 << i)` | set bit i |
| `mask & ~(1 << i)` | clear bit i |
| `mask ^ (1 << i)` | toggle bit i |
| `bin(mask).count("1")` | popcount (slow); use `mask.bit_count()` Py 3.10+ |
| Iterate submasks: `s = mask; while s: s = (s - 1) & mask` | enumerates all proper submasks of mask |

The submask iteration is itself a beautiful trick — total work over all
masks is O(3^n), not O(4^n).

## Pitfalls

1. **Wrong base case**: forgetting `dp[{0}][0] = 0` in TSP gives garbage.
2. **Mask order**: if your recurrence depends on **larger** masks, you
   need descending order or memoization.
3. **Confusing "set i is visited" vs "set i is unvisited"**: pick one
   convention and stick to it.
4. **Off-by-one with n vs (1 << n)**: `(1 << n) - 1` is the full mask
   for n elements, NOT `1 << (n - 1)`.
5. **Forgetting return edge in TSP**: the tour must close.
6. **Trying n = 25+**: 2^25 = 33M, often too slow in Python without
   tight loops or numpy.

## Real-World Usage

| System | Application | Why Bitmask DP |
|--------|-------------|----------------|
| **Logistics** | TSP for last-mile delivery (n ≤ 20 stops) | Exact optimal route |
| **OR systems** | Job-shop scheduling, machine assignment | Subset of jobs assigned |
| **VLSI** | Gate placement minimizing wire length | Subset of placed gates |
| **Compilers** | Register allocation for small live-sets | Subset of allocated regs |
| **AI search** | Subset-sum, set cover for planners | Track visited states compactly |

## Checkpoint Questions

1. Why does TSP need `dp[mask][i]` while task assignment only needs
   `dp[mask]`? Connect the answer to the structure of the cost function.
2. What's the time complexity of iterating all submasks of all masks
   of an n-bit set? Why is it O(3^n), not O(2^n × 2^n)?
3. Give a problem where bitmask DP works for n = 25 but Python is
   too slow — and the same problem in C would work.
4. In TSP, prove that ascending numerical order of `mask` is a valid
   topological order for the DP.
5. Adapt the TSP recurrence to find the **number** of optimal tours
   (multiple tours tied for shortest).
