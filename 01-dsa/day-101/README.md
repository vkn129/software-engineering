# Day 101: Non-Comparison Sorts — Beating Ω(n log n)

## The Ω(n log n) Lower Bound (and How to Escape It)

**Theorem**: any sorting algorithm that only **compares pairs of elements**
requires Ω(n log n) comparisons in the worst case.

**Proof sketch (decision tree)**: a comparison sort with input of size n must
distinguish among n! possible orderings. A binary decision tree with n!
leaves has height ≥ log₂(n!) = Ω(n log n). Done.

This bound says **nothing** about algorithms that look at the *bits* or
*structure* of keys directly. Counting sort, radix sort, and bucket sort do
exactly that — and run in **O(n)** under the right conditions.

## 1. Counting Sort

Idea: if keys are integers in [0, k), count occurrences and reconstruct.

```
counting_sort(a, k):
    count = [0] * k
    for x in a: count[x] += 1
    # Compute prefix sums → final positions
    for i in 1..k: count[i] += count[i-1]
    out = [0] * len(a)
    for x in reverse(a):
        count[x] -= 1
        out[count[x]] = x
    return out
```

**Complexity**: O(n + k) time, O(n + k) space.

**When it wins**: k = O(n). For k ≫ n, counting sort wastes memory on empty
buckets and quicksort wins.

**Stable**: yes — iterate input in reverse and decrement.

### Real use: histogram-driven preprocessing

Counting sort is rarely used standalone but is the *engine* of radix sort.

## 2. Radix Sort (LSD — Least Significant Digit First)

Idea: sort by each digit from least significant to most, using a **stable**
sort per pass.

```
LSD radix sort:
    for digit d = 0, 1, 2, ... (least to most significant):
        stable sort a by digit d
```

**Complexity**: O(d·(n + b)) where d = number of digits, b = base.
For 32-bit ints with b=256: d=4, so ~4·n = O(n).

**Why LSD works**: at the end of pass d, elements are sorted on the first d+1
digits *because* prior passes left a stable ordering on lower digits.

## 3. Radix Sort (MSD — Most Significant Digit First)

Idea: bucket by top digit, recurse into each bucket.

**Pros**: handles variable-length keys (e.g., strings); can short-circuit.
**Cons**: more bookkeeping; cache-unfriendly recursion.

**Used by**: GNU coreutils `sort` (string sorting), DuckDB, ClickHouse.

## 4. Bucket Sort

Idea: distribute n keys uniformly into n buckets, sort each bucket, concatenate.

```
bucket_sort(a, n_buckets):
    buckets = [[] for _ in range(n_buckets)]
    for x in a:
        buckets[int(x * n_buckets)].append(x)   # assume x in [0,1)
    for b in buckets:
        insertion_sort(b)
    return [x for b in buckets for x in b]
```

**Complexity**: O(n) **expected** when keys are uniformly distributed.
Degrades to O(n²) when all keys land in one bucket.

**Real use**: distribution-aware sorting (e.g., postal code sorting,
priority queue scheduling in OS schedulers).

## The Math: Why Radix Is Not "Magic"

Counting sort treats the key value itself as the address. That's not
comparison — that's **indexing**, which costs O(1) per element. Radix sort
chains counting sorts together. The trick is real, but:

1. **Memory**: counting sort needs O(k) buckets. For 64-bit unsigned keys,
   k = 2⁶⁴ ≈ 1.8 · 10¹⁹ → impractical. Radix breaks the key into chunks.
2. **Locality**: each pass touches all of `count` and all of `a` → ~8·n
   cache misses on misaligned data. CPU-friendly only if k or base is small.
3. **Fixed-width assumption**: radix needs to know d (digit count) up front.
   Hard for variable-length data unless using MSD.

## Complexity Table

| Algorithm     | Time           | Space     | Stable | Constraint            |
|---------------|----------------|-----------|--------|-----------------------|
| Counting sort | O(n + k)       | O(n + k)  | Yes    | keys in [0, k)        |
| LSD radix     | O(d(n + b))    | O(n + b)  | Yes    | fixed-width keys      |
| MSD radix     | O(d(n + b))    | O(n + b)  | Yes    | works on strings      |
| Bucket sort   | O(n) expected  | O(n)      | depends| uniform distribution  |

For 32-bit ints, b=256: radix is ~4(n + 256) = ~4n + 1024 = **O(n)**.

## Pathological Inputs

| Algorithm     | Worst-case input                        | Behavior          |
|---------------|-----------------------------------------|-------------------|
| Counting sort | k=10⁹, n=10                             | **10⁹ space**     |
| LSD radix     | Keys with one huge digit (k=2⁶⁴)        | one giant counter |
| Bucket sort   | All keys identical                      | **O(n²)**         |

## Real-World Usage

| System / Library          | Algorithm     | Why                                 |
|---------------------------|---------------|-------------------------------------|
| GNU coreutils `sort`      | MSD radix (strings) | n is large, b is alphabet=256 |
| DuckDB, ClickHouse        | Radix on int cols   | Vectorized columns, ints      |
| Boost `spreadsort`        | Hybrid radix+quick  | Best of both                  |
| Python `int.bit_length()` | (no native sort)    | But float sort uses quicksort |
| `qsort()` for ints? **No production stdlib uses radix as default** because of variable-length keys, generic comparators, and stability concerns |

The pattern: radix wins when **you know the keys are integers/strings of
fixed alphabet** AND **n is large** (>10⁴) AND **k is moderate** (<n²).
General-purpose libraries can't assume that and so default to Timsort/Introsort.

## Why Radix Is Optimal for Specific Workloads

Sorting 10⁸ 32-bit integers:
- Quicksort: ~1.8 × 10⁹ comparisons → ~5 seconds
- LSD radix (base 256): ~4 × 10⁸ operations → ~1 second

This is why columnar databases default to radix on integer columns.

## Checkpoint Questions

1. The Ω(n log n) lower bound assumes a "comparison" model. Define precisely
   what counts as a comparison. Why doesn't `count[x] += 1` count?
2. Walk through counting sort on `[2, 5, 3, 0, 2, 3, 0, 3]` with k=6. Show
   the `count` array after each phase.
3. Why does LSD radix sort use a **stable** subroutine? Construct a 4-element
   input that breaks LSD if you swap in an unstable counting sort.
4. You have 10⁹ 64-bit integers to sort. Counting sort with k=2⁶⁴ is
   impossible. How would you parameterize LSD radix (digit width, base) to
   minimize total work?
5. Bucket sort is O(n) expected. Construct an input that makes it O(n²)
   and explain how `random.shuffle` *before* bucket sort would fix it.
6. CPython's `list.sort()` is Timsort (comparison-based, O(n log n)). Why
   doesn't CPython detect "all elements are ints" and switch to radix?
