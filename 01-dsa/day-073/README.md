# Day 73: HyperLogLog — Cardinality Estimation with O(1) Space

## Why This Matters

Counting unique items exactly requires O(n) memory — you must remember every item you've seen.
For billions of items (unique visitors, distinct IPs, unique queries), that's impractical.
HyperLogLog estimates cardinality using **constant memory** (~16KB) with ~2% error.
This is one of the most widely deployed probabilistic data structures in production systems.

## Core Insight: Leading Zeros as a Cardinality Proxy

Hash each element to a uniformly distributed binary string. Count the number of leading zeros.

**Key probability argument:** For a truly random bit string:
- P(starts with `0`) = 1/2
- P(starts with `00`) = 1/4
- P(starts with `000`) = 1/8
- P(starts with k zeros) = 1/2^k

So if the **maximum** number of leading zeros you've ever seen is k, that suggests you've
seen approximately **2^k unique elements**. You needed ~2^k trials before one produced k
leading zeros.

This is the same logic as: "If I flipped a coin and got 20 heads in a row, I've probably
been flipping for a very long time."

## The Variance Problem and Stochastic Averaging

A single max-leading-zeros estimator has enormous variance. One unlucky hash could give
many leading zeros and wildly overestimate.

**Solution: use m = 2^b registers (stochastic averaging).**

1. Hash the element to get a bit string
2. Use the first **b bits** as a bucket/register index (m = 2^b buckets)
3. Use the **remaining bits** to count leading zeros
4. Store only the **maximum** leading zero count per register
5. Combine all registers using the **harmonic mean**

The harmonic mean is crucial — it's robust to outliers (one register with an unusually
high value won't dominate the estimate).

## The Formula

```
E = alpha_m * m^2 * (sum of 2^(-M[j]) for j=0..m-1)^(-1)
```

Where:
- `m = 2^p` is the number of registers
- `M[j]` is the max leading zeros in register j
- `alpha_m` is a bias correction constant: alpha_m = 0.7213 / (1 + 1.079/m) for m >= 128

## Bias Correction

The raw estimator is biased at small and large cardinalities:

- **Small cardinalities (E < 5/2 * m):** Use **LinearCounting** instead. Count the number
  of empty registers (zeros). Estimate = m * ln(m / V) where V = number of empty registers.
  This works because empty registers follow a Poisson process.

- **Medium cardinalities:** Use the raw HLL estimate with alpha correction.

- **Large cardinalities (E > 2^32 / 30):** Apply hash collision correction:
  E_corrected = -2^32 * ln(1 - E/2^32). This compensates for hash collisions in 32-bit space.

## Error Analysis

- **Standard error:** 1.04 / sqrt(m)
- With p=14 (m=16384 registers, 16KB memory): error ~ 0.81%
- With p=10 (m=1024 registers, 1KB memory): error ~ 3.25%
- Each register needs ~5 bits (max leading zeros in 32-bit hash is 32), but typically stored as 1 byte

## Memory Comparison

| Method            | Memory for 1B unique items | Error |
|-------------------|---------------------------|-------|
| Exact (HashSet)   | ~8 GB                     | 0%    |
| HLL (p=14)        | 16 KB                     | ~0.8% |
| HLL (p=10)        | 1 KB                      | ~3.2% |

That's a **500,000x** memory reduction for less than 1% error.

## Real-World Uses

- **Redis PFADD/PFCOUNT:** Built-in HLL with p=14 (16KB per key). Used for counting
  unique page views, unique users, unique events.
- **Google BigQuery:** `APPROX_COUNT_DISTINCT()` uses HLL++ (improved bias correction).
- **Apache Flink / Spark:** Streaming distinct count aggregations.
- **Network monitoring:** Counting unique source IPs, unique flows.
- **Analytics platforms:** Unique visitor counting across billions of events.

## Files

- `hyperloglog.py` — Full HLL implementation with add, count, merge, and demo
- `practice.py` — 5 exercises exploring HLL properties and applications

## Checkpoint Questions

1. **Why leading zeros?** What probability property makes the maximum number of leading
   zeros a useful estimator for cardinality?

2. **Why harmonic mean?** Why not use the arithmetic mean of the register values?
   What happens with outliers if you use arithmetic mean?

3. **Why does LinearCounting work better for small cardinalities?** What goes wrong
   with the raw HLL estimate when most registers are still zero?

4. **Memory vs accuracy trade-off:** If you double the number of registers, by what
   factor does the standard error decrease? (Hint: 1.04/sqrt(m))

5. **Merge operation:** Why can you merge two HLL sketches by taking the element-wise
   maximum of registers? What property of "max leading zeros" makes this valid?

6. **Hash quality:** What happens to HLL accuracy if the hash function has poor
   uniformity? Why is a good hash function critical?
