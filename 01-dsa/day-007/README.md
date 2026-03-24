# Day 7: Mini-Project — Benchmark Suite

## Why This Exists

Theory says merge sort is O(n log n) and insertion sort is O(n^2). But what does that actually MEAN on real hardware? Theory abstracts away constants, cache behavior, branch prediction, memory allocation patterns, and a dozen other factors that determine actual wall-clock time. Today we build a benchmark suite that measures reality and compares it to theory.

This matters because the gap between theory and practice is where engineering lives. A theoretically slower algorithm can beat a theoretically faster one for small inputs (insertion sort beats merge sort for n < ~30, which is why Timsort uses insertion sort for small runs). Cache-friendly algorithms with worse big-O can outperform cache-hostile algorithms with better big-O (array traversal vs linked list traversal). Constant factors that theory ignores can be 10x or 100x.

Building a benchmark suite also teaches you to measure carefully. Naive benchmarking produces garbage results: you measure the JIT warming up, the garbage collector running, the OS scheduling other processes, or the CPU throttling. Good benchmarking requires understanding what you are measuring and controlling for confounding variables.

By the end of today, you will have a tool that takes any function, runs it on increasing input sizes, measures wall-clock time, and fits the results to theoretical complexity curves. You will be able to look at any algorithm and answer: "Does reality match theory? If not, why?"

## Theory (40 min)

### From Big-O to Wall-Clock Time

Big-O notation hides constants: O(n log n) means there exist constants c and n0 such that T(n) <= c * n * log(n) for all n > n0. The actual time is:

```
T(n) = c * f(n) + lower_order_terms + noise
```

Our job is to estimate c and verify that f(n) matches the predicted growth rate.

### Methodology: Ratio Test

If T(n) = c * n^k, then T(2n) / T(n) = 2^k. This ratio test lets you empirically determine k:

- If the ratio converges to 2, the algorithm is O(n)
- If the ratio converges to 4, the algorithm is O(n^2)
- If the ratio converges to 8, the algorithm is O(n^3)
- If the ratio converges to 2 * (1 + 1/log2(n)), approximately O(n log n)

### Confounding Factors

**Cache effects:** Modern CPUs have L1/L2/L3 caches. Sequential array access is fast (cache-friendly). Random pointer chasing is slow (cache-hostile). When your input exceeds cache size, performance drops discontinuously — this shows up as a bump in your timing curve.

**Memory allocation:** Creating lists, appending, and slicing all allocate memory. The allocator and garbage collector add unpredictable overhead. Pre-allocating data before timing helps.

**CPU frequency scaling:** Modern CPUs boost to higher frequencies under load and throttle under thermal pressure. Short benchmarks may measure the boost; long benchmarks may measure throttling.

**Python overhead:** Python is interpreted with significant per-operation overhead. The constant factor is large, which means asymptotic behavior only dominates at larger n than you might expect.

### Text-Based Plotting

We cannot use matplotlib (no external libraries), so we build ASCII plots. The key insight: map data values to character positions in a fixed-width grid. Log-scale on the y-axis makes exponential growth linear and helps visualize wide ranges.

## Practice (20 min)

Work through `practice.py`. Benchmark 5 different algorithms, analyze their growth rates, and explain where theory matches reality and where it diverges.

Also run `benchmark_suite.py` to see the complete framework in action with built-in demonstrations.

## Daily Project

Build `benchmark_suite.py` — a reusable benchmarking framework that:

1. Times any function on increasing input sizes with multiple trials
2. Computes growth rate ratios (doubling test)
3. Fits measured times to theoretical curves
4. Produces ASCII plots of actual vs predicted performance
5. Detects when real performance deviates from theoretical predictions

## Checkpoint Questions

1. You benchmark insertion sort and get these times: n=1000 -> 0.05s, n=2000 -> 0.20s, n=4000 -> 0.81s. What is the ratio T(2n)/T(n)? Does this match the theoretical O(n^2)?

2. Merge sort and insertion sort both sort correctly. For what input size might insertion sort actually be faster? Why?

3. You benchmark a function and find that it runs in 0.001s for n=100 and 0.1s for n=1000. The ratio T(10n)/T(n) is 100. What is the likely complexity? What if the ratio were 10?

4. Your benchmark shows a sudden slowdown at n=65536 that is not predicted by the algorithm's complexity. What hardware factor might explain this?

5. Why do we take the median of multiple trials rather than the mean? What kinds of noise does median handle better?
