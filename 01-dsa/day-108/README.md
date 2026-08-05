# Day 108: Interpolation Search

## The Pitch: O(log log n)

Binary search probes the **middle**. Interpolation search probes where
it *expects* the key to be, assuming the data is uniformly distributed:

```
guess = lo + (x - a[lo]) * (hi - lo) / (a[hi] - a[lo])
```

If `a` is uniformly distributed over its range, this estimate is very close
to the true position. Each probe shrinks the search range by a quadratic
factor — `O(log log n)` expected comparisons.

For n = 1 billion:
- Binary search: ~30 comparisons
- Interpolation: ~5 comparisons (uniform data)

That's the **theoretical** win. In practice it rarely wins because:
1. Each step has a `*` and `/` (binary search has a `>>`).
2. Real-world data is rarely uniform.
3. Cache misses dominate either way.

## The Math: Why log log n?

Assume `a[i]` is sampled uniformly from `[a[lo], a[hi]]`. After one probe,
the expected size of the remaining range satisfies:

```
E[size_{k+1}] = sqrt(E[size_k])
```

(quadratic shrinkage). Starting from `n`:

```
n -> sqrt(n) -> n^(1/4) -> n^(1/8) -> ...
```

After `k` steps, size is `n^(1/2^k)`. Setting that to constant gives
`k = log_2(log_2 n) = O(log log n)`.

Proven by Yao & Yao (1976) and Perl, Itai, Avni (1978).

## When It Wins, When It Loses

| Distribution | Result | Why |
|--------------|--------|-----|
| Uniform integers 1..N | O(log log n) | Estimate is accurate |
| Sorted timestamps in a hot table | O(log log n) | Approximately uniform |
| Exponentially distributed | O(n) — *worse than linear* | Estimate keeps pointing to one end |
| Few unique values | O(n) | Division by `a[hi] - a[lo]` near zero |
| Adversarial (geometric, log-normal) | O(n) | Probe never converges |

The worst case `O(n)` is a real failure mode. Knuth, *TAOCP* Vol 3, §6.2.1:
> "Interpolation search is good only when the data is known to be uniformly
> distributed; otherwise, its asymptotic behaviour degrades catastrophically."

## Variants

### Interpolation + Sequential Fallback

Hybrid: try one interpolation step. If it doesn't narrow the range enough,
fall back to binary search. Bounds worst case at O(log n).

### Block-level interpolation in databases

Postgres BRIN indexes use interpolation-like estimates over block ranges
to choose which blocks to scan first when bounds are roughly correlated
with insertion order.

## Failure Modes

| Failure | When | Fix |
|---------|------|-----|
| Divide by zero | `a[lo] == a[hi]` (all duplicates) | Check before division; fall back to linear |
| Overflow | `(x - a[lo]) * (hi - lo)` in 32-bit | Use 64-bit math or floats |
| O(n) on skew | Exponential / log-normal data | Hybrid with binary search |
| Wrong probe | Negative numbers and signed math | Use absolute math or guard |
| Off-by-one with floats | Floating-point `pos` casts to int incorrectly | Clamp probe to `[lo, hi]` |

## Why Production Almost Always Uses Binary

`std::lower_bound` and Python's `bisect` don't use interpolation. Reasons:
- Binary search is **branch-predictor friendly** and SIMD-friendly.
- Modern CPUs do a multiply in 3-5 cycles, but the *cache miss* of jumping
  to a far position dominates either way — interpolation doesn't help.
- Robustness: a single skewed dataset gives O(n). Engineers prefer
  predictable O(log n) over best-case O(log log n) + worst-case O(n).

Interpolation search **does** show up in:
- **In-memory time-series databases** (TSDB), e.g. some VictoriaMetrics
  hot-path lookups on monotonic timestamps.
- **GPU-side lookups** where divergence cost is low but extra probes are
  expensive.

## Complexity

| Case | Time |
|------|------|
| Uniform data, average | O(log log n) |
| Uniform data, worst | O(log n) |
| Skewed data, worst | O(n) |
| Space | O(1) |

## Checkpoint Questions

1. Why does the recurrence `T(n) = T(sqrt(n)) + 1` solve to O(log log n)?
2. Construct an input where interpolation search degrades to O(n).
3. Why don't `bisect` and `lower_bound` use interpolation?
4. How does the "hybrid" approach guarantee O(log n) worst case while
   keeping O(log log n) average?
5. What single line in the implementation can divide by zero, and how
   do you guard against it?
6. Postgres BRIN indexes use a similar idea at *block* granularity. Why
   block-level rather than row-level?
