# Day 19: Prefix Sums & Difference Arrays — O(1) Range Queries

## Why This Exists

The brute-force approach to range queries is straightforward: loop from index i to j and accumulate. That is O(n) per query. If you have Q queries on an array of length n, you pay O(nQ). For 10 million queries on a million-element array, that is 10 trillion operations. Prefix sums reduce every range query to O(1) after a single O(n) preprocessing pass, giving O(n + Q) total.

This is not a clever trick — it is the discrete version of the Fundamental Theorem of Calculus. A prefix sum is a discrete integral: `prefix[i] = sum(arr[0..i])`. A difference array is a discrete derivative: `diff[i] = arr[i] - arr[i-1]`. Just as integration and differentiation are inverses in calculus, prefix sums and difference arrays are inverses in discrete math. Computing a prefix sum "integrates" the array; computing differences "differentiates" it. The range sum `arr[i..j]` is `prefix[j] - prefix[i-1]`, exactly like `integral(a,b) = F(b) - F(a)`.

This pattern is everywhere in production:
- **Databases**: aggregate queries (`SELECT SUM(revenue) WHERE date BETWEEN ...`) use prefix-sum-like structures in OLAP cubes and columnar stores. A pre-aggregated cumulative column turns an O(n) scan into an O(1) lookup.
- **Image processing**: integral images (summed-area tables) are 2D prefix sums. Viola-Jones face detection uses them to compute Haar features in O(1) per rectangle, making real-time face detection possible.
- **Networking**: cumulative byte counters on interfaces. To find bytes transferred in a time range, subtract two cumulative readings — that is a prefix sum query.
- **Difference arrays** appear in scheduling (applying range updates for overlapping bookings), genomics (marking regions of interest), and any problem where you apply many range increments and read the final state once.

### What If This Didn't Exist?

Without prefix sums, every range sum query requires a linear scan from index i to j. If your monitoring dashboard fires 10,000 queries per second against a million-element time series, you are doing 10 billion operations per second just for summation. Databases without pre-aggregated cumulative structures must re-scan entire columns for every GROUP BY with a date range. Image processing algorithms like Viola-Jones face detection would drop from real-time (30fps) to unusable, because each Haar feature evaluation would cost O(width * height) instead of O(1). The entire field of real-time analytics collapses back to batch processing.

### Why This Name?

"Prefix sum" comes from the concept of a "prefix" in sequence theory -- the first k elements of a sequence form a prefix. The sum of a prefix is literally the sum of the first k elements. The term has been standard in computer science since at least the 1960s, appearing in parallel computing literature where "parallel prefix" algorithms (Blelloch, 1990) compute all prefix sums simultaneously. "Difference array" mirrors the calculus term "difference quotient" -- it is the discrete derivative, measuring how the array changes between consecutive positions. The pairing of these names reflects their mathematical duality as discrete integral and discrete derivative.

### The Physics Connection

Prefix sums exploit sequential memory access, which aligns perfectly with how DRAM and CPU caches work. Computing a prefix sum array is a single linear pass -- the hardware prefetcher predicts every access, and every 64-byte cache line is fully utilized. The difference array technique is even better: range updates become two O(1) writes (at the boundaries), meaning you touch exactly two cache lines per update instead of potentially thousands. In networking hardware, cumulative byte counters on interfaces are physically implemented as prefix sums in silicon -- the counter increments with each packet, and range queries are just subtraction. The entire structure respects the physics of sequential access being 10-100x faster than random access.

### The Mathematics Connection

The prefix sum is the discrete analog of the definite integral, and the Fundamental Theorem of Calculus transfers directly: `sum(arr[i..j]) = prefix[j+1] - prefix[i]`, exactly as `integral(f, a, b) = F(b) - F(a)`. Information-theoretically, you are preprocessing O(n) bits of information into a structure that answers O(n^2) possible range queries in O(1) each -- a compression of the query space. The 2D extension uses inclusion-exclusion from combinatorics, and the formula's 2^k terms in k dimensions connects to the Mobius inversion on the lattice of subsets. Lower bound: you cannot answer arbitrary range sum queries in O(1) with less than O(n) preprocessing, because each element independently affects query answers.

### The Economics Connection

Prefix sums are the classic compute-once-query-many trade-off. You spend O(n) upfront to save O(n) on every subsequent query -- the break-even point is just two queries. In production, this means OLAP cubes pre-compute aggregates at ingestion time (paying write amplification) to make analytical queries instantaneous. The difference array inverts this: it is cheaper to defer computation, batching all updates and reconstructing once. The choice between prefix sums (read-optimized) and difference arrays (write-optimized) mirrors the read-vs-write optimization trade-off that defines entire database architectures (OLAP vs OLTP). Developer time is also saved: the code is simpler and less error-prone than maintaining running totals manually.

### When Does This Break?

Prefix sums are static -- if the underlying array changes, you must rebuild the entire prefix array in O(n). A single element update invalidates every prefix sum after it. For floating-point data, catastrophic cancellation accumulates: after summing a million floats, the prefix values may have lost several digits of precision, and subtracting two large, nearly-equal prefix values amplifies the error (Kahan summation mitigates this). 2D prefix sums on very large matrices hit memory limits (O(mn) auxiliary space). If the array contains values that overflow your integer type, prefix sums overflow silently in languages like C. Adversarially, if an attacker controls the query pattern and can trigger rebuilds, they can force O(n) work per query.

### When Should You Violate This?

If your data is dynamic (frequent inserts, deletes, or updates interleaved with queries), prefix sums are the wrong tool -- use a Fenwick tree or segment tree that supports O(log n) updates and queries. If you only ever need one or two range queries, the O(n) preprocessing is wasted and a direct scan is simpler. For streaming data where elements arrive one at a time and you need running aggregates, a simple accumulator variable is sufficient -- no need for the full prefix array. If memory is extremely constrained and you cannot afford the O(n) auxiliary array, compute sums on the fly. In distributed systems where the array is sharded across machines, maintaining a global prefix sum requires coordination that may not be worth the latency.

---

## Theory (40 min)

### 1. 1D Prefix Sums (10 min)

**The problem:** Given an array `arr` of n numbers, answer multiple queries of the form "what is the sum of elements from index i to index j?"

**Brute force:** Loop from i to j. O(j - i + 1) per query.

**Prefix sum:** Build an auxiliary array where `prefix[k]` = sum of `arr[0..k-1]`.

```
arr:    [3, 1, 4, 1, 5, 9]
prefix: [0, 3, 4, 8, 9, 14, 23]
         ^
         sentinel zero — makes the formula clean
```

**Range sum query:** `sum(arr[i..j]) = prefix[j+1] - prefix[i]`

Example: sum of arr[1..3] = prefix[4] - prefix[1] = 9 - 3 = 6. Check: 1 + 4 + 1 = 6.

**Why the sentinel zero:** Without it, you need a special case for queries starting at index 0. The sentinel `prefix[0] = 0` means the formula works uniformly for all ranges. This is the same reason mathematicians define the empty sum as 0 — it makes the algebra consistent.

**Build time:** O(n). **Query time:** O(1). **Space:** O(n).

### 2. 2D Prefix Sums (15 min)

**The problem:** Given an m x n matrix, answer "what is the sum of all elements in the rectangle from (r1,c1) to (r2,c2)?"

**The idea:** Extend 1D prefix sums to two dimensions using inclusion-exclusion.

```
prefix[i][j] = sum of all elements in the rectangle from (0,0) to (i-1,j-1)
```

**Build:** For each cell, apply inclusion-exclusion:
```
prefix[i][j] = matrix[i-1][j-1]
             + prefix[i-1][j]     (everything above)
             + prefix[i][j-1]     (everything to the left)
             - prefix[i-1][j-1]   (double-counted corner)
```

**Query:** Sum of rectangle from (r1,c1) to (r2,c2):
```
sum = prefix[r2+1][c2+1]
    - prefix[r1][c2+1]       (above the rectangle)
    - prefix[r2+1][c1]       (left of the rectangle)
    + prefix[r1][c1]         (subtracted twice, add back)
```

This is inclusion-exclusion from combinatorics: |A ∪ B| = |A| + |B| - |A ∩ B|, applied geometrically.

**Build time:** O(mn). **Query time:** O(1). **Space:** O(mn).

**Why this matters for databases:** OLAP cubes pre-aggregate data along multiple dimensions. A 2D prefix sum is a two-dimensional OLAP cube. The same inclusion-exclusion principle extends to k dimensions, though the formula has 2^k terms.

### 3. Difference Arrays (10 min)

**The problem:** Given an array of n elements (initially all zero), apply Q updates of the form "add value v to every element from index i to index j." Then read the final array.

**Brute force:** Each update touches O(j - i + 1) elements. Total: O(nQ) in the worst case.

**Difference array:** Instead of updating every element in the range, record the *change at the boundaries*:
```
diff[i] += v       (the increment starts here)
diff[j+1] -= v     (the increment stops after j)
```

After all updates, reconstruct the array by taking a prefix sum of `diff`.

```
Range update: add 5 to indices [1..3] on array of length 6

diff: [0, +5, 0, 0, -5, 0]

Prefix sum of diff: [0, 5, 5, 5, 0, 0]  — exactly what we wanted
```

**Why this works:** The difference array is the "derivative" of the array. Adding v to a range creates a step function: it jumps up by v at the start and drops by v after the end. Taking the prefix sum "integrates" these jumps back into the actual values.

**Update time:** O(1). **Reconstruct time:** O(n). **Total for Q updates:** O(Q + n).

### 4. The Calculus Connection (5 min)

| Continuous | Discrete |
|---|---|
| f(x) | arr[i] |
| F(x) = integral(f, 0, x) | prefix[i] = sum(arr[0..i-1]) |
| f(x) = F'(x) | diff[i] = prefix[i] - prefix[i-1] |
| integral(f, a, b) = F(b) - F(a) | sum(arr[i..j]) = prefix[j+1] - prefix[i] |
| Adding a constant to f on [a,b] | diff[a] += v, diff[b+1] -= v |

This is not an analogy — it is the same mathematical structure. The prefix sum operator and the difference operator are exact inverses, just as integration and differentiation are inverses. If you apply a difference array to a prefix sum array, you recover the original. If you apply a prefix sum to a difference array, you recover the original.

---

## Practice (20 min)

Complete the exercises in `practice.py`:

1. **Subarray sum equals K** — Count subarrays whose sum equals K using prefix sums + hash map. This is LeetCode 560 and tests whether you understand that `sum(arr[i..j]) = prefix[j+1] - prefix[i]`, so finding subarrays with sum K becomes finding pairs where `prefix[j] - prefix[i] = K`.

2. **Count ranges with sum in [lo, hi]** — Count subarrays whose sum falls within a given range. Extends problem 1 from equality to a range constraint.

3. **2D prefix sum for image blur** — Apply a box blur to a 2D grid using a 2D prefix sum to compute each neighborhood average in O(1).

4. **Difference array for range increments** — Process a list of range update operations and return the final array. Classic difference array application.

5. **Equilibrium index** — Find the index where the sum of elements to its left equals the sum to its right. Prefix sums let you check each candidate in O(1).

---

## Daily Project

Build a **RangeQueryEngine** that supports:
- 1D range sum queries
- 2D rectangle sum queries
- Batch range updates using a difference array
- A method to demonstrate the calculus connection by showing that `difference(prefix_sum(arr)) == arr`

This is the `prefix_sums.py` file — run it to see all demonstrations.

---

## Checkpoint Questions

1. Why does the prefix sum array have length n+1 instead of n? What goes wrong if you use length n?
2. In the 2D prefix sum query formula, why do you add back `prefix[r1][c1]`? Draw the rectangles.
3. If you need to support both range updates AND range queries (not just one batch of updates followed by reconstruction), prefix sums and difference arrays alone are not enough. What data structure handles both? (Hint: it is a tree.)
4. A prefix sum array is a running total. What happens to floating-point accuracy after millions of additions? How would you mitigate this in production? (Hint: Kahan summation.)
5. Explain why `sum(arr[i..j]) = prefix[j+1] - prefix[i]` is the discrete analog of the Fundamental Theorem of Calculus.
