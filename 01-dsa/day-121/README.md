# Day 121: Interval DP

## What Makes a Problem "Interval DP"

You have a sequence and decisions are made by **choosing a split point**
within a contiguous interval. The optimal cost of `[i, j]` depends on
the optimal cost of every smaller sub-interval `[i, k]` and `[k+1, j]`.

The signature:

```
dp[i][j] = best over all k in (i, j) of dp[i][k] + dp[k+1][j] + cost(i, k, j)
```

Two classic forms:
- **Matrix Chain Multiplication (MCM)** — minimize scalar multiplications
- **Burst Balloons** — maximize coins by choosing burst order

## State Design: Matrix Chain Multiplication

You have matrices `A1, A2, ..., An` with dimensions `d[0]×d[1], d[1]×d[2], ...,
d[n-1]×d[n]`. Multiplying `A_i ... A_j` requires choosing where to split.

**State**: `dp[i][j]` = min scalar multiplications to compute `A_i ... A_j`.

**Recurrence**:
```
dp[i][j] = min over k in [i, j-1]:
              dp[i][k] + dp[k+1][j] + d[i] * d[k+1] * d[j+1]
```

**Base**: `dp[i][i] = 0` (single matrix, no multiplication).

**Order**: increasing length `j - i + 1`, same as palindrome DP.

### Subproblem Dependency Graph

```
   dp[i][j]
     |
     +----- depends on dp[i][k] and dp[k+1][j] for all k in [i, j-1]
                |
                v
            shorter intervals (already computed)
```

Crucially, BOTH children of every split are smaller intervals — so by
filling in length-major order, every dependency is ready.

### Parenthesization Output

To reconstruct the optimal product structure, store the **argmin** k:

```
split[i][j] = argmin_k of dp[i][k] + dp[k+1][j] + ...
```

Then recursively print `( A_i..A_k ) ( A_{k+1}..A_j )`.

## State Design: Burst Balloons

You have balloons with values `nums`. Bursting balloon `i` gives
`nums[i-1] * nums[i] * nums[i+1]` coins (using 1 for out-of-range).
Maximize total coins.

**Naive state attempt**: `dp[i][j]` = max coins from bursting subset `[i, j]`.
**Problem**: when bursting balloon `k` in `[i, j]`, its neighbors depend on
**which balloons outside `[i, j]` are still standing**. The state hides
external dependencies. This is the most common interval DP trap.

**Fix — reverse the question**:
> "What if `k` is the **LAST** balloon to be burst in `[i, j]`?"

If `k` is last in `[i, j]`, then when it bursts, `nums[i-1]` and `nums[j+1]`
are its neighbors (everything inside `[i, j]` except `k` is already gone).

**Recurrence**:
```
dp[i][j] = max over k in [i, j]:
             dp[i][k-1] + dp[k+1][j] + nums[i-1] * nums[k] * nums[j+1]
```

With padding `nums = [1] + nums + [1]`, this gives a clean O(n^3) DP.

### Why Reversing the Question Works

The forward question ("which to burst first?") makes neighbors at the
moment of bursting depend on **what is still inside the interval**,
which the state cannot capture without exponential blow-up.

The reversed question ("which to burst last?") makes neighbors at the
moment of bursting **the boundaries of the interval** — fully determined
by the state. This is a recurring DP technique: when the natural ordering
gives bad dependencies, flip it.

## Pitfalls

1. **MCM dimension indexing**: matrix `A_i` has dimensions `d[i] × d[i+1]`.
   Confusing `d[i]` vs `d[i-1]` is the #1 source of bugs.
2. **Burst balloons forward direction**: defining `dp[i][j]` as "burst
   first" fails because the state doesn't know external balloons.
3. **Loop order**: must iterate by interval length, NOT by `i` then `j`
   in their natural orders. Try a small example to convince yourself.
4. **Off-by-one in split range**: `k` ranges over `[i, j-1]` for MCM
   (split between left and right groups) but `[i, j]` for burst balloons
   (k itself is burst last).

## Complexity

Both: **O(n^3)** time, **O(n^2)** space. Knuth's optimization (day 125)
brings some interval DPs down to O(n^2) when the cost function has the
quadrangle inequality property.

## Real-World Usage

| System | Application | Why Interval DP |
|--------|-------------|-----------------|
| **Compilers** | Optimal join order in SQL query planner | Same MCM recurrence |
| **Graphics** | Polygon triangulation cost minimization | Split polygon into triangles |
| **Bioinformatics** | RNA secondary structure (Nussinov) | Maximize base pair matches over intervals |
| **NLP** | CKY parsing for context-free grammars | Build parse trees bottom-up |
| **Robotics** | Optimal manipulator chain ordering | Minimize joint stress |

## Checkpoint Questions

1. In MCM, why does `k` range over `[i, j-1]` and not `[i, j]`?
2. In burst balloons, what specifically breaks if you define
   `dp[i][j]` as "max coins from bursting `[i, j]` in some order
   with `k` first"?
3. CKY parsing is interval DP for grammar parsing. What plays the
   role of `cost(i, k, j)`?
4. How does the dependency pattern of interval DP differ from
   knapsack-style DP? Why does it force length-major iteration?
5. Reconstruct one optimal parenthesization for matrix dims
   `[40, 20, 30, 10, 30]`.
