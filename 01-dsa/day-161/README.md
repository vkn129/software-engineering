# Day 161: Parallel Merge — k-Way Merge With Partitioning

## Why It Matters

Day 160 built a parallel mergesort, measured it honestly, and then named its own
ceiling (`day-160/README.md:64-68`):

> For mergesort, the final merge over n elements is O(n) — and that's a serial
> bottleneck. With unlimited cores, speedup tops out at ~log n (the number of
> merge layers). This is why **parallel merge** (k-way merge by partitioning)
> exists in real implementations — but it's a Day-161+ topic.

This is that day. The fix is one idea: **you can split a merge into independent
pieces before doing any of it**, by computing where each output chunk's inputs
begin. That computation is called **co-ranking** (equivalently, finding a point
on the **merge path**), and it costs a binary search.

Where it actually runs:

- **NVIDIA CUB / Thrust** — `MergePath` partitioning is how GPU merge and merge
  sort assign work to thread blocks. It is the reference implementation.
- **GNU libstdc++ parallel mode** — `multiseq_partition` is a real function in
  `<parallel/multiseq_selection.h>`, used by its parallel merge sort.
- **Database merge joins and LSM compaction** — RocksDB / Cassandra compact k
  sorted SSTables; partitioning by key range is the same trick at file scale.
- **External sorting** — the final k-way merge of sorted runs is exactly this
  problem when the runs live on disk.

## The Bottleneck, Stated Precisely

Three terms, all already used on day 155:

- **Work** = total operations across all processors. What you pay for.
- **Span** (also called depth) = the longest chain of dependent operations. What
  you wait for, even with infinite processors.
- **Parallelism** = work / span. The speedup ceiling, by Brent's theorem.

Parallel mergesort with a **serial** merge:

```
Work(n)  = 2·Work(n/2) + Θ(n)   =  Θ(n log n)
Span(n)  = Span(n/2)   + Θ(n)   =  Θ(n)        <- the merge dominates
Parallelism = Θ(n log n) / Θ(n) = Θ(log n)
```

That `Θ(log n)` is day-160's ceiling, derived rather than asserted. For
`n = 10^6` it is about 20 — so a 64-core machine cannot possibly be more than
~20x faster, however perfect the rest of the implementation is. The recursion
parallelizes beautifully and then everything waits on one thread doing an `O(n)`
scan.

## The Fix: Partition The Output, Not The Input

The naive instinct is to split the *inputs* — give worker 0 the first half of A
and the first half of B. That is wrong: those two halves do not merge into a
contiguous run of the output.

Invert it. Split the **output** into P equal contiguous chunks, then ask, for
each chunk boundary `k`:

> Of the first `k` elements of the merged result, how many came from A?

Call that number `i`. Then `j = k - i` came from B, and chunk `t` is produced by
merging `A[i_t : i_{t+1}]` with `B[j_t : j_{t+1}]` — no communication, no shared
state, no overlap. Every worker writes a disjoint output range.

`i` is the **co-rank** of `k`.

## Computing The Co-Rank

`(i, j)` with `i + j = k` is the correct split iff:

```
A[i-1] <= B[j]        (nothing in A's prefix belongs after B's cut)
B[j-1] <  A[i]        (nothing in B's prefix belongs after A's cut)
```

with the obvious conventions when `i = 0`, `j = 0`, `i = m`, or `j = n`. The
asymmetry — `<=` on one side, `<` on the other — is what makes the merge
**stable** (equal elements take A first). It is not cosmetic; see Failure Modes.

Both conditions are monotone in `i`, so binary search finds it:

```
lo = max(0, k - n)          # j = k - i cannot exceed len(B)
hi = min(k, m)              # i cannot exceed len(A) nor k
loop:
    i = (lo + hi) // 2;  j = k - i
    if   i > 0 and j < n and A[i-1] >  B[j]:  hi = i - 1     # took too much A
    elif j > 0 and i < m and B[j-1] >= A[i]:  lo = i + 1     # took too little A
    else:                                     return i
```

`O(log min(m, n))` comparisons, `O(1)` space, no writes. That is the entire
algorithm. Everything else is bookkeeping.

### Picture: The Merge Path

Draw a grid, A along one axis, B along the other. A merge is a monotone
staircase from the top-left corner to the bottom-right: step right when you take
from A, down when you take from B. The path has exactly `m + n` steps.

The anti-diagonal `i + j = k` crosses that path in exactly one place. The
co-rank binary search *is* a search along that anti-diagonal for the crossing.
`P` evenly spaced diagonals cut the path into `P` equal-length segments — the
work assignment. Hence the name **merge path** (Odeh et al., 2012); Green,
McColl & Bader (2012) call the same quantity the co-rank.

## Work And Span, Fixed

```
ParallelMerge on m+n elements with P processors:
    Span  = O(log(m+n))    (one binary search)  +  O((m+n)/P)  (local merge)
    Work  = O(P log(m+n))  (P binary searches)  +  O(m+n)      (all local merges)
```

The work overhead is `P log n` extra comparisons — negligible when
`P << n / log n`. With `P = m+n` processors the span is `O(log n)`: the merge is
no longer serial.

Feed that back into mergesort:

| | serial merge | parallel merge |
|---|---|---|
| Merge span | `Θ(n)` | `Θ(log n)` |
| Sort work | `Θ(n log n)` | `Θ(n log n)` (same!) |
| Sort span | `Θ(n)` | `Θ(log^3 n)` |
| Parallelism | `Θ(log n)` | `Θ(n / log^2 n)` |

For `n = 10^6`, parallelism goes from ~20 to ~2,500. **The work is unchanged** —
this is not a trade, it is a strictly better schedule. That is rare and worth
noticing.

(`Θ(log^3 n)` is the standard CLRS bound for the recursive divide-and-conquer
merge. Flattening the whole merge into a single partition step, which is what GPU
implementations do, reaches `Θ(log^2 n)`.)

## Going k-Way: `multiseq_partition`

A binary merge tree over `k` runs costs `log k` passes over the data. A **k-way**
merge does it in one pass — but only if you can cut all `k` runs at consistent
positions.

Same question, more lists: given global output rank `r`, find an index vector
`(i_1, ..., i_k)` with `Σ i_t = r` such that everything before the cuts is `<=`
everything after. Binary-search the **splitter value** `v`:

```
count_le(v) = Σ_t  bisect_right(L_t, v)      # monotone nondecreasing in v
v   = smallest value with count_le(v) >= r
i_t = bisect_left(L_t, v)                    # now Σ i_t < r; the deficit is all == v
distribute the remaining (r - Σ i_t) picks among the runs' equal-to-v blocks
```

That last line is the whole difficulty. With duplicates, the rank `r` can land
*inside* a block of equal values spread across several runs, and no single value
separates them. You must break the tie by an explicit, deterministic rule (we
assign greedily in run order). Skip it and you either duplicate elements or lose
them — silently, because the output is still sorted.

libstdc++'s `multiseq_partition` carries the same tie-handling logic, for exactly
this reason.

## Python's GIL — What This File Does And Does Not Claim

**This implementation models the algorithm. It does not deliver wall-clock
speedup, and no number printed here should be read as if it did.**

CPython holds a global interpreter lock, so pure-Python threads do not execute
bytecode in parallel (`day-160/README.md:34-46` covers this). Comparing sorted
integers is pure-Python bytecode. Running `parallel_merge` on 8 threads will be
*slower* than the serial version — thread overhead with none of the benefit.

What the demos measure instead:

1. **Correctness** — the partitioned merge equals `sorted(a + b)` exactly,
   including on duplicate-heavy and empty inputs.
2. **Disjointness** — the partitions tile the output with no gap and no overlap.
   That is the property which makes the algorithm parallel, and it is checkable
   with zero parallelism.
3. **Work and span**, counted directly: comparisons performed, and the longest
   dependency chain. These are properties of the algorithm, not of the machine,
   and they are what transfers to C++, CUDA, or Rust.

Measuring the right thing on the wrong runtime beats measuring the wrong thing on
the right one. The same partitioning in C++ with OpenMP scales near-linearly —
the algorithm is not the limitation here, the interpreter is.

## Complexity

| Operation | Work | Span | Space |
|---|---|---|---|
| `serial_merge(m, n)` | `O(m+n)` | `O(m+n)` | `O(m+n)` output |
| `co_rank(k, A, B)` | `O(log min(m,n))` | `O(log min(m,n))` | `O(1)` |
| `merge_path_partition` into P | `O(P log n)` | `O(log n)` | `O(P)` |
| `parallel_merge`, P workers | `O(m + n + P log n)` | `O(log n + (m+n)/P)` | `O(m+n)` |
| `multiseq_partition`, k runs | `O(k log n · log V)` | same | `O(k)` |
| `parallel_kway_merge`, P workers | `O(n log k + P k log n log V)` | `O(k log n log V + (n/P) log k)` | `O(n)` |
| Mergesort + serial merge | `O(n log n)` | `O(n)` | `O(n)` |
| Mergesort + parallel merge | `O(n log n)` | `O(log^3 n)` | `O(n)` |

`V` is the size of the key range searched by `multiseq_partition`. A purely
comparison-based k-way partition achieves `O(k log(n/k))` instead; we take the
value-search version because it is a third of the code and the tie handling —
the part that is actually hard — is identical either way.

## Failure Modes

1. **Splitting the inputs instead of the output.** The most common wrong
   instinct. `merge(A[:m/2], B[:n/2])` is not a prefix of `merge(A, B)`. The
   output-partition formulation is the whole idea.

2. **Symmetric tie comparisons.** Using `<=` on both sides of the co-rank test
   makes two adjacent chunks both claim an equal element — duplicated in the
   output. Using `<` on both drops it. The output is still sorted either way, so
   the bug ships. `co_rank` uses `A[i-1] <= B[j]` and `B[j-1] < A[i]`, which also
   yields stability.

3. **Off-by-one in the search bounds.** `i` lives in
   `[max(0, k - n), min(k, m)]`, not `[0, m]`. Get it wrong and `j = k - i` goes
   negative or past the end of B — an index error if you are lucky, a wrong split
   if you are not.

4. **Duplicates across runs in the k-way case.** Covered above. Test with
   `[[5]*10, [5]*10, [5]*10]`: if the total output length changes, the tie rule
   is broken.

5. **Assuming equal output chunks mean equal time.** True for merging, where cost
   is linear in output size. False for a general k-way reduce with variable
   per-element cost. Partition by *estimated work*, not by count, when elements
   are not uniform.

6. **Partitioning cost swamping the merge.** `P log n` binary searches to
   parallelize an `O(n)` scan only pays when `n/P >> log n`. Merging 100 elements
   across 8 threads is pure loss. Real implementations set a threshold and fall
   back to serial — the same knob as day-160's `THRESHOLD`.

7. **Believing a Python thread benchmark.** Stated above; repeated because it is
   the mistake this file is most likely to invite.

8. **Unstable output when stability was assumed.** A merge is stable only if ties
   resolve toward the earlier run consistently at *every* boundary. One chunk
   resolving the other way makes the whole merge unstable, which then breaks any
   LSD radix sort built on top of it.

## Checkpoint Questions

1. Derive `Parallelism = Θ(log n)` for mergesort with a serial merge from the
   work and span recurrences. Which term dominates the span, and why does adding
   cores not help?
2. Why can you not simply give worker 0 the first half of A and the first half of
   B? Give a 4-element counterexample.
3. State the two co-rank conditions. Show that exactly one `i` in
   `[max(0,k-n), min(k,m)]` satisfies both, so the binary search is well posed.
4. Which side of the co-rank test uses `<` and which uses `<=`? Construct an
   input where swapping them duplicates an element in the output.
5. Parallel merge *adds* `O(P log n)` work. Under what relationship between `P`
   and `n` is that overhead negligible? At what point does it dominate?
6. In `multiseq_partition`, the deficit after `bisect_left` consists entirely of
   elements equal to the splitter `v`. Prove it, and explain why the distribution
   rule must be deterministic.
7. Mergesort's span drops from `Θ(n)` to `Θ(log^3 n)` while the work stays
   `Θ(n log n)`. Why is "same work, less span" unusual? Name one algorithm where
   reducing span genuinely costs extra work.
8. This file's threaded demo is slower than its serial baseline. Explain in one
   sentence why that is expected and why it says nothing about the algorithm.
9. You are merging 64 sorted SSTables during an LSM compaction. Binary merge tree
   or 64-way `multiseq_partition`? What does the answer depend on — CPU, memory
   bandwidth, or disk?
