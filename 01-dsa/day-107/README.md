# Day 107: Ternary Search

## Why Ternary Search Exists

Binary search needs a **monotonic** predicate. What if the function isn't
monotonic but has a single peak or valley — *unimodal*?

```
        peak
         /\
        /  \
       /    \
      /      \
     /        \
```

You can't binary search this — `f(m)` doesn't tell you which half holds the
peak. But ternary search does: probe **two** points, compare, and discard
*one third* of the interval each step.

Real-world uses:
- **Convex optimization** with no gradient (black-box function)
- **1D parameter tuning**: find batch size, learning rate, threshold that
  optimizes a single objective
- **Computational geometry**: maximum distance from a point to a moving target
- **Game theory**: finding the saddle point of a 1D payoff
- **Physics simulation**: finding the angle that maximizes range

For *differentiable* convex problems, gradient descent or Brent's method
(used in `scipy.optimize`) is faster. Ternary search shines when the
function is **black-box** and you can only evaluate it pointwise.

## How It Works

Given a unimodal function `f` on `[lo, hi]` (maximum somewhere inside):

1. Pick two probes: `m1 = lo + (hi - lo)/3`, `m2 = hi - (hi - lo)/3`.
2. Evaluate `f(m1)` and `f(m2)`.
3. If `f(m1) < f(m2)`, peak lies in `[m1, hi]` -> set `lo = m1`.
4. Else peak lies in `[lo, m2]` -> set `hi = m2`.
5. Repeat until `hi - lo < eps`.

Each iteration shrinks the interval by 1/3. After `k` iterations the interval
is `(2/3)^k` of the original.

## Why 1/3? Why Two Probes?

You need **two** probes because a single sample at the midpoint tells you
the value but not the slope. With two probes, comparing `f(m1)` and `f(m2)`
gives you the slope information needed to prune.

You don't strictly need exact thirds — *golden section search* picks probes
at the golden ratio (`phi = (sqrt(5)-1)/2 ≈ 0.618`) so one of the two probes
gets reused on the next iteration. That cuts function calls by half compared
to naive thirds, and is the algorithm `scipy.optimize.minimize_scalar(method='golden')` uses.

## Complexity

| Metric | Value |
|--------|-------|
| Iterations to shrink to eps | `log(initial / eps) / log(3/2) ≈ 1.71 · log₂(initial / eps)` |
| Function evaluations per iter | 2 (naive) or 1 (golden section) |
| Total f() calls (golden) | `log_phi(initial / eps)` |

For integer ternary search on `[1, N]`: `O(log_{3/2} N)` ≈ 1.71 · log₂ N
iterations, each O(1).

## Failure Modes

| Failure | When | Fix |
|---------|------|-----|
| **Wrong answer** | Function is not unimodal (multiple peaks) | Bracket the right peak first, or switch to global optimization |
| **Stuck on plateau** | `f(m1) == f(m2)` on a flat region | Add a tiebreak: shrink both sides toward the centre |
| **Floating point eps too small** | `hi - lo < eps` never triggers because float spacing is larger than eps | Use fixed iteration count (~200) instead of eps |
| **Integer rounding loops** | On `[lo, hi]` with `hi - lo == 2`, `m1` and `m2` collapse to same index | Stop early when `hi - lo < 3`, scan remaining points directly |
| **Convexity not strict** | Function has flat top | Returns *a* maximum, not necessarily the leftmost/rightmost |

## Connection to Convexity (Math)

A function is unimodal on `[a, b]` if it strictly increases up to some `c*`
then strictly decreases. Concave (or convex) functions are unimodal.

**Concave** function `f`: for any `x < y < z`,
```
f(y) >= ((z-y) * f(x) + (y-x) * f(z)) / (z - x)
```
That's why probing two interior points and comparing them lets you discard
a third of the interval — concavity guarantees the peak isn't in the
"losing" third.

Ternary search is a **derivative-free** optimization method; gradient
descent uses `f'(x)` and converges faster but needs differentiability.

## Real Systems

- **`scipy.optimize.minimize_scalar(method='golden')`** — golden section search.
- **Game AI**: Quake's mouse-acceleration curve tuning during gameplay.
- **Compiler tuning**: LLVM PGO has historically used golden section to pick
  optimal block reorder thresholds.
- **Hyperparameter search** (1D): when grid search is too coarse and the
  loss surface is roughly unimodal, ternary/golden converges in ~30 evals.

## Checkpoint Questions

1. Why can't you do binary search on a unimodal function?
2. After 20 iterations on `[0, 1]`, how small is the interval?
3. Why does golden section search save one function evaluation per iteration?
4. What happens if the function has *two* peaks? Does ternary search find
   either? How would you detect that case?
5. For integer ternary search on `[0, N]`, when must you stop and scan
   the remaining points directly?
6. When would you use ternary search over Brent's method or gradient descent?
