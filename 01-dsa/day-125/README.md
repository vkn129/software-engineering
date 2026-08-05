# Day 125: DP Optimization Techniques

## Why Optimize DP

You've designed a correct DP and it's `O(n^3)` or `O(n × k × m)`. The
constraints push you over time limits. You need to **either prune the
recurrence** (Knuth, divide-and-conquer) **or change the data structure
underneath** (CHT, segment tree, deque).

Three classical optimizations covered today:

| Optimization | Reduces | Requires |
|--------------|---------|----------|
| **Knuth's** | O(n^3) -> O(n^2) | Quadrangle inequality + monotonicity of optimal split |
| **Divide-and-conquer** | O(n × k × m) -> O(n × k × log m) | Monotonicity of optimal split across the outer index |
| **Convex Hull Trick (CHT)** | O(n × m) -> O(n) or O(n log n) | Recurrence of form `dp[i] = min_j(a_j × x_i + b_j)` |

All three rest on **monotonicity properties** of the optimal decision
function. Identify the monotonicity, exploit it.

## Knuth's Optimization

For interval DP of form:
```
dp[i][j] = min over k in [i, j-1]: dp[i][k] + dp[k+1][j] + w(i, j)
```

If `w` satisfies the **quadrangle inequality** (`w(a,c)+w(b,d) ≤ w(a,d)+w(b,c)`
for `a ≤ b ≤ c ≤ d`) and is monotone, then the optimal split point
`opt[i][j]` is monotone:

```
opt[i][j-1] ≤ opt[i][j] ≤ opt[i+1][j]
```

Restrict the inner k-loop to this range. **Amortized O(n^2)** instead
of O(n^3).

Classical application: **optimal binary search tree** (Knuth 1971).
Also: stone merge (when applicable), some MCM variants.

## Divide-and-Conquer Optimization

For DP of form:
```
dp[i][j] = min over k in [0, j]: dp[i-1][k] + C(k, j)
```

(One outer dimension i, inner choice k that depends on j.)

If `opt[i][j]` is monotone non-decreasing in j (for fixed i), then a
divide-and-conquer over j-positions gives O(n log n) per outer layer
instead of O(n^2).

```
def solve(lo, hi, opt_lo, opt_hi):
    if lo > hi: return
    mid = (lo + hi) // 2
    best_k = -1
    best_val = INF
    for k in range(opt_lo, min(mid, opt_hi) + 1):
        v = dp[i-1][k] + C(k, mid)
        if v < best_val:
            best_val = v
            best_k = k
    dp[i][mid] = best_val
    solve(lo, mid - 1, opt_lo, best_k)
    solve(mid + 1, hi, best_k, opt_hi)
```

Each k-position is amortized visited O(log n) times across all recursive
calls. Total: O(n log n) per outer i; overall O(n × k × log n).

Used in: balloon collection, partitioning problems with concave cost.

## Convex Hull Trick (CHT)

For DP of form:
```
dp[i] = min over j < i: a_j × x_i + b_j
```

where `(a_j, b_j)` depend on the j-th DP state and `x_i` depends on i.

This is `n` queries of "evaluate a set of lines at a point and take min."

**Data structure**: maintain the **lower envelope** of the lines. For
each new line, pop dominated lines from a stack/deque. For each query,
binary search (or use a pointer if queries are monotone).

**Complexity**:
- Lines added in slope-monotone order, queries in x-monotone order:
  **O(n)** amortized with deque.
- General case: O(n log n) with sorted structure.

**Classic application**: factory line construction —
```
dp[i] = min over j < i: dp[j] + a[i] × (x[i] - x[j]) + ...
       = a[i] × x[i] + min over j: -a[i] × x[j] + (dp[j] + extras)
```

Each j contributes a line of slope `-x[j]`, intercept `dp[j] + extras`;
each i is a query at `x = a[i]`.

## Real Problem with CHT: Building Bridges

Given posts at positions `x_1 < x_2 < ... < x_n` with costs `c_1, ..., c_n`.
You must place a stake at every position. Connecting consecutive stakes
at positions `i` and `j` (with `i < j`) costs `(x_j - x_i)^2`. Once
connected to the previous stake, every position covered by the segment
gets a "+c" cost too (placed posts).

Recurrence (one common form):
```
dp[i] = min over j < i: dp[j] + (x[i] - x[j])^2 + (cost_prefix[i-1] - cost_prefix[j])
```

Expanding `(x[i] - x[j])^2 = x[i]^2 - 2 x[i] x[j] + x[j]^2`:

```
dp[i] = x[i]^2 + cost_prefix[i-1] + min over j:
            ( -2 x[j] ) × x[i] + ( dp[j] + x[j]^2 - cost_prefix[j] )
```

That's a **line per j**: slope `-2 x[j]`, intercept `dp[j] + x[j]^2 - cost_prefix[j]`.
Query at `x = x[i]`. Since `x[i]` is monotone increasing in i, we can use
a **monotonic deque** and the entire DP runs in O(n).

## Subproblem Dependency Graph

```
   dp[i]
     |
     v
   query min over lines L_0, L_1, ..., L_{i-1}
     |
     v
   each L_j was constructed from dp[j]
```

Linear dependency in i; the trick is the **batch query** structure.

## Pitfalls

1. **Wrong quadrangle direction**: max-version vs min-version of Knuth
   uses opposite inequality.
2. **CHT line ordering**: deque-based CHT requires monotone slope **and**
   monotone query x. Violate one, you need Li Chao tree or sorted set.
3. **Floating-point in CHT intersections**: use cross-product comparisons
   (integer arithmetic) when possible.
4. **D&C monotonicity proof**: NOT every DP that looks like `min_k(...)`
   admits D&C. The cost function must be concave/convex appropriately.
5. **Off-by-one in D&C bounds**: `opt_lo`/`opt_hi` carry over carefully.

## When NOT to Optimize

- If `n ≤ 500` and you have O(n^3) — accept it (1.25 × 10^8 ops, often fine in C).
- If the problem is one-off — code clarity > speed.
- If the constant factor of CHT/Li Chao exceeds the saving — measure first.

## Real-World Usage

| System | Application | Why optimize |
|--------|-------------|--------------|
| **Compilers** | Optimal instruction scheduling DP | n could be 10^4+ |
| **Logistics** | Optimal warehouse partitioning | Concave costs → D&C |
| **Manufacturing** | Production-line bridge problem | CHT in O(n) for 10^6 stages |
| **Finance** | Optimal portfolio rebalancing schedule | Convex cost → CHT |
| **Algorithms research** | Optimal BST | Knuth's original application |

## Checkpoint Questions

1. Prove that quadrangle inequality implies monotonicity of `opt[i][j]`.
2. Give a DP that looks like the D&C pattern but where `opt[i][j]` is
   NOT monotone in j — and show the optimization gives wrong answer.
3. In CHT, why does the deque trick require monotone query x? What
   happens with random query x?
4. For the bridges problem above, prove the lines you add have
   monotone slope.
5. The Li Chao segment tree handles general (non-monotone) CHT in
   O(log V) per query. Sketch how it works.
