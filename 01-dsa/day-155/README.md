# Day 155: Parallel Prefix Sum (Scan)

## Why Scan Matters

Prefix sum sounds trivial — given `[3, 1, 4, 1, 5]`, produce `[3, 4, 8, 9, 14]`.
Sequentially it's a single `for` loop. But **parallel scan** is the workhorse
primitive behind nearly every GPU kernel: sorting (radix), stream compaction,
sparse matrix products, Bloom filter construction, lexer DFAs.

If you understand scan, you understand the shape of every fast GPU algorithm.

## The Sequential Version

```
out[0] = in[0]
out[i] = out[i-1] + in[i]
```

O(n) work, O(n) depth. **Depth = n** is the killer: no matter how many cores
you have, you wait for n sequential additions. On a GPU with 10,000 cores,
you would idle 9,999 of them.

## Two Parallel Scans

Both compute prefix sums but with different work/depth trade-offs.

### Hillis-Steele (1986) — Step-Efficient

For `d = 0, 1, 2, ..., log n - 1`:
  for each `i` in parallel: `a[i] += a[i - 2^d]` if `i >= 2^d`

```
step 0:   [3, 1, 4, 1, 5, 9, 2, 6]
step 1:   [3, 4, 5, 5, 6,14,11, 8]
step 2:   [3, 4, 8, 9,11,19,17,13]
step 3:   [3, 4, 8, 9,14,23,25,22]
```

- **Depth**: O(log n) — log n synchronization rounds
- **Work**: O(n log n) — each step touches n elements
- **Verdict**: Great when you have ≥ n cores. Wastes work otherwise.

### Blelloch (1990) — Work-Efficient

Two passes over a balanced binary tree:

1. **Up-sweep (reduce)**: build sums of power-of-two segments
2. **Down-sweep**: distribute partial sums to produce exclusive scan

```
input:        [3, 1, 4, 1, 5, 9, 2, 6]

up-sweep:     [3, 4, 4, 5, 5,14, 2, 8]     # pairs summed at leaves
              [3, 4, 4, 9, 5,14, 2,22]     # next level
              [3, 4, 4, 9, 5,14, 2,31]     # root = total = 31

set root to 0 (identity for exclusive scan)
down-sweep:   propagate left=parent, right=parent+leftOld

output (exclusive): [0, 3, 4, 8, 9, 14, 23, 25]
```

- **Depth**: O(log n)
- **Work**: O(n) — each element visited twice (up then down)
- **Verdict**: Optimal work. Slightly more synchronization complexity.

## Why This Maps to GPUs

A GPU executes warps of 32 threads in lock-step. A binary-tree scan fits:

- Within a warp: shuffle-based Hillis-Steele (no shared memory).
- Across a block: Blelloch in shared memory.
- Across the grid: scan of block totals, then re-add.

CUDA's `cub::DeviceScan` is exactly this three-level hierarchy.

## Python's GIL

Python threads cannot execute pure-Python bytecode in parallel. We measure
**logical depth** (sync rounds) and **work** (total ops), not wall-clock
speedup. For real parallelism in Python: `multiprocessing`, NumPy, or numba.

We do show actual thread timing for a fair-but-honest demonstration —
expect anti-speedup because the GIL serializes everything.

## Inclusive vs Exclusive

- **Inclusive**: `out[i] = a[0] + ... + a[i]` — Hillis-Steele's natural output.
- **Exclusive**: `out[i] = a[0] + ... + a[i-1]`, `out[0] = 0` — Blelloch's natural output.

Convert by shifting and adding/subtracting `a[i]`.

## Applications

| Use case | How scan helps |
|---|---|
| Stream compaction | Predicate → 0/1 → scan → write index |
| Radix sort | Per-digit histogram + scan = bucket starts |
| Sparse-matrix × vector (CSR) | Row pointers built by scan |
| Polynomial evaluation | Horner's rule as scan (semiring) |
| Lexing | Scan with state-transition monoid |

Scan generalizes to **any associative operator**: max, min, gcd, matrix product.
This is the **monoid scan** — the deepest form of the algorithm.

## Checkpoint Questions

1. Why does Hillis-Steele do O(n log n) work when the sequential version is O(n)?
2. In Blelloch up-sweep, which array indices are *written* at each level? Why does this avoid races?
3. You have an input of length 1 million and only 4 cores. Which scan wins, why?
4. Generalize Blelloch scan to `max`. What's the identity element? Why must the operator be associative but not necessarily commutative?
5. Why is exclusive scan more useful than inclusive scan for stream compaction?
