# Day 100: Quicksort Deep Dive

## Why Spend a Day on One Sort

Quicksort is the **most-studied algorithm in computer science**. Sedgewick's
1975 PhD thesis was 159 pages. The reason: every choice — partition scheme,
pivot strategy, recursion management — has measurable performance impact, and
the worst case can be 10⁴× slower than the average case. Modern production
sorts (V8's Dual-Pivot, GCC's Introsort) are direct descendants of these
analyses.

## The Two Partition Schemes

### Lomuto (the textbook version)

Pivot at the end. Single index `i` walks the "less-than-or-equal" zone.

```
lomuto(a, lo, hi):
    pivot = a[hi]
    i = lo
    for j in [lo, hi):
        if a[j] <= pivot:
            swap(a[i], a[j])
            i += 1
    swap(a[i], a[hi])
    return i
```

**Pros**: simple, easy to prove correct, taught in every textbook.
**Cons**: O(n²) on **all-equal input** (every element triggers a swap and an
increment, partitioning becomes [n-1, 0] every level).

### Hoare (the original — 1959)

Two pointers walking toward each other.

```
hoare(a, lo, hi):
    pivot = a[lo]
    i, j = lo - 1, hi + 1
    while True:
        i += 1; while a[i] < pivot: i += 1
        j -= 1; while a[j] > pivot: j -= 1
        if i >= j: return j
        swap(a[i], a[j])
```

**Pros**: roughly **3× fewer swaps** than Lomuto on random data; handles
all-equal input in O(n log n).
**Cons**: harder to reason about; returns a *split point*, not the final
pivot index; recursion args are `(lo, p)` and `(p+1, hi)` — different from
Lomuto.

## Pivot Strategies

| Strategy           | Sorted input | Reverse input | Random input | All equal |
|--------------------|--------------|---------------|--------------|-----------|
| First element      | **O(n²)**    | **O(n²)**     | O(n log n)   | depends   |
| Last element       | **O(n²)**    | **O(n²)**     | O(n log n)   | depends   |
| Middle element     | O(n log n)   | O(n log n)    | O(n log n)   | depends   |
| Random             | O(n log n)*  | O(n log n)*   | O(n log n)*  | O(n log n)* |
| Median-of-3        | O(n log n)   | O(n log n)    | O(n log n)   | depends   |
| Median-of-medians  | **O(n log n)** | **O(n log n)** | **O(n log n)** | O(n log n) |

*expected, not worst-case

### Median-of-3

Compare `a[lo]`, `a[mid]`, `a[hi]` and use the median as pivot. Defeats all
"sorted" adversaries that real systems care about. Used in GCC's introsort.

### Median-of-medians (the BFPRT 1973 trick)

Divides array into groups of 5, finds median of each group, then recursively
finds median of those medians. Gives a **deterministic O(n log n) worst case**
but with constants so large that it's pedagogical, not practical. Knuth: "of
theoretical interest only."

### Dual-Pivot (Yaroslavskiy 2009)

Pick two pivots p₁ ≤ p₂, partition into three regions: `< p₁`, `p₁ ≤ x ≤ p₂`,
`> p₂`. ~20% fewer comparisons on average than single-pivot. **Java
`Arrays.sort(int[])` switched to this in JDK 7** and it's now the default for
primitive arrays. Real measurement: 5-10% faster on random data.

## The O(n²) Worst Case — Real, Not Theoretical

Take quicksort with **last-element pivot** on input `[1, 2, 3, ..., n]`:

```
Level 0: pivot=n, partition gives [1..n-1] | n          (n comparisons)
Level 1: pivot=n-1, partition gives [1..n-2] | n-1      (n-1 comparisons)
...
Level n: 1 element                                       (1 comparison)
Total: n + (n-1) + ... + 1 = n(n+1)/2 = O(n²)
```

For n=10⁴ this is **~10⁸ operations**, ~100× slower than the expected 1.3×10⁵.

Today's `demo_pathological_blowup()` measures this directly.

## How Production Systems Defend Against O(n²)

| System                     | Defense                                  |
|----------------------------|------------------------------------------|
| GCC `std::sort` (introsort)| Switch to heapsort after 2·log₂(n) depth |
| Java `Arrays.sort(int[])`  | Dual-pivot quicksort                     |
| .NET `Array.Sort`          | Introsort (since 4.5)                    |
| PostgreSQL `tuplesort.c`   | Median-of-3, fallback to merge for big   |
| Linux kernel               | Heap sort (avoids quicksort entirely)    |

The lesson: **no production code uses pure quicksort**. Either randomize,
median-of-3, or fall back to heap/merge.

## Complexity Table

| Variant                   | Best     | Average  | Worst   | Stable | Notes |
|---------------------------|----------|----------|---------|--------|-------|
| Lomuto + first pivot      | n log n  | n log n  | n²      | No     | Dies on sorted |
| Lomuto + random pivot     | n log n  | n log n  | n² (P→0)| No     | Safe in expectation |
| Hoare + random pivot      | n log n  | n log n  | n² (P→0)| No     | Fewer swaps |
| Median-of-3               | n log n  | n log n  | n² (rare)| No    | Standard prod choice |
| Dual-pivot                | n log n  | n log n  | n²      | No     | ~20% fewer cmps |
| Median-of-medians         | n log n  | n log n  | n log n | No     | Slow constants |

## Real-World Usage

| System          | Algorithm        | Worst-case defense          |
|-----------------|------------------|-----------------------------|
| Java `Arrays.sort(int[])`  | Dual-pivot QS | Insertion sort for n<47, dual pivot otherwise |
| GCC libstdc++ `std::sort`  | Introsort     | depth>2·log₂(n) → heapsort  |
| LLVM libc++ `std::sort`    | Introsort     | same with median-of-3 pivot |
| .NET `Array.Sort`          | Introsort     | depth>2·log₂(n) → heapsort  |
| Go `sort.Slice`            | Pattern-defeating QS (pdqsort) | Multiple heuristics, O(n log n) bound |
| Rust `slice::sort_unstable`| pdqsort       | Block-quicksort + heuristics |

## Checkpoint Questions

1. Walk through Lomuto partition on `[3, 1, 4, 1, 5]` step by step. Show `i`
   and the array after each iteration of `j`.
2. Construct a 6-element input that makes Lomuto with last-element pivot
   perform exactly O(n²) operations. Verify your construction by counting
   partition calls.
3. Hoare's partition returns a value that is **not** the final pivot index.
   How do the recursive calls differ from Lomuto's? Why doesn't the pivot
   end up in its final position?
4. Median-of-3 prevents the "sorted input" attack. Can you construct an
   adversarial input that defeats median-of-3? (Hint: McIlroy's "killer
   adversary" 1999.)
5. Dual-pivot quicksort has 3 partitions but only 2 comparisons per element
   in the common case. Sketch why that's still ~20% fewer comparisons total.
6. Why does GCC's introsort use **heapsort** (not merge sort) as its O(n log n)
   fallback? List two reasons.
