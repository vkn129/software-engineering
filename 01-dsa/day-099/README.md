# Day 99: Comparison Sorts Review — Merge, Quick, Heap

## Why Revisit the Big Three

Every modern sorting routine in production (CPython's Timsort, V8's Timsort,
Java's Dual-Pivot Quicksort, libstdc++'s Introsort) is a **hybrid** built on
top of these three. Before studying the hybrids, you must feel — in your
hands — where each pure algorithm shines and where it dies.

- **Merge sort**: stable, predictable O(n log n), but needs O(n) extra space
- **Quicksort**: in-place, smallest constants, but O(n²) worst case and not stable
- **Heap sort**: in-place AND O(n log n) worst case, but poor cache behavior

The answer to "which sort is best?" is always **"depends on the input."**
Today we measure exactly that on the same dataset.

## The Three Algorithms

### Merge Sort (1945, von Neumann)

Divide the array in half, sort each half recursively, merge.

```
merge_sort(A):
    if len(A) <= 1: return A
    mid = len(A) // 2
    L = merge_sort(A[:mid])
    R = merge_sort(A[mid:])
    return merge(L, R)
```

**Recurrence**: T(n) = 2·T(n/2) + O(n)  →  O(n log n)

**Stable**: equal elements keep their relative order (matters for sort-by-key).

**Worst-case guarantee**: O(n log n) on every input — no adversary can hurt you.

### Quicksort (1959, Hoare)

Pick a pivot, partition into "< pivot" and "> pivot", recurse on each side.

```
quicksort(A, lo, hi):
    if lo >= hi: return
    p = partition(A, lo, hi)
    quicksort(A, lo, p-1)
    quicksort(A, p+1, hi)
```

**Average**: O(n log n) with random pivot.
**Worst**: O(n²) — already-sorted input + first-element pivot is the classic killer.
**In-place**: O(log n) extra for recursion stack only.

### Heap Sort (1964, Williams)

Build a max-heap, then repeatedly extract max to the end.

```
heap_sort(A):
    build_max_heap(A)              # O(n)
    for i from n-1 down to 1:
        swap(A[0], A[i])
        sift_down(A, 0, i)         # O(log i)
```

**Worst-case**: O(n log n) — guaranteed.
**In-place**: O(1) extra.
**Cache-unfriendly**: heap accesses jump around the array → ~2-3× slower than
quicksort in practice despite same asymptotics.

## Complexity Table

| Algorithm | Best     | Average  | Worst    | Space  | Stable | In-place |
|-----------|----------|----------|----------|--------|--------|----------|
| Merge     | n log n  | n log n  | n log n  | O(n)   | Yes    | No       |
| Quick     | n log n  | n log n  | n²       | O(log n) | No   | Yes      |
| Heap      | n log n  | n log n  | n log n  | O(1)   | No     | Yes      |

## Pathological Inputs (Today's Headline)

| Input pattern         | Merge | Quick (first-pivot) | Heap |
|-----------------------|-------|---------------------|------|
| Random                | OK    | Fast                | OK   |
| Already sorted        | Fast  | **O(n²)**           | OK   |
| Reverse sorted        | Fast  | **O(n²)**           | OK   |
| All duplicates        | OK    | **O(n²)** (Lomuto)  | OK   |
| Nearly sorted (k swaps) | Fast | OK                  | OK   |

**The lesson**: pure quicksort with a deterministic pivot is unsafe on
adversarial input. This is why every production quicksort uses randomization
or median-of-3 (covered tomorrow).

## Real-World Usage

| System / Library            | Sort algorithm                    | Why                          |
|-----------------------------|-----------------------------------|------------------------------|
| CPython `list.sort()`       | Timsort (merge variant)           | Stability + adaptive runs    |
| Java `Arrays.sort(int[])`   | Dual-pivot quicksort              | Cache + few moves on ints    |
| Java `Arrays.sort(Object[])`| Timsort                           | Stability required by spec   |
| libstdc++ `std::sort`       | Introsort (quick + heap fallback) | O(n log n) worst guarantee   |
| V8 `Array.prototype.sort`   | Timsort (since 2018)              | Stability + real-world data  |
| Linux kernel `sort()`       | Heap sort                         | O(1) space, deterministic    |
| `qsort` in glibc            | Merge sort with insertion fallback| Stability-ish, no O(n²)      |

Note: glibc's `qsort` is *not* quicksort despite the name — it's been merge sort
since the 1990s.

## Why Heap Sort Is Slow in Practice

Modern CPUs love sequential memory access. Merge sort reads/writes sequentially.
Quicksort partitions sequentially. Heap sort jumps: parent at `i`, children at
`2i+1` and `2i+2` — for n=10^7 these can be megabytes apart, blowing the L1/L2
cache on every comparison.

Measured on this implementation (n=10⁵, random ints):
- Quick: ~30 ms
- Merge: ~50 ms
- Heap: ~100 ms

Same asymptotic, 3× difference. **Constants matter.**

## Checkpoint Questions

1. Why is merge sort *stable* but quicksort is not? Walk through a 4-element
   example where quicksort reorders equal keys.
2. Construct an adversarial input of size 8 that forces Lomuto-partition
   quicksort with first-element pivot into O(n²) behavior.
3. Heap sort and merge sort are both O(n log n) worst case. Why does heap sort
   consistently lose to merge sort in benchmarks?
4. CPython chose Timsort (merge-based) over quicksort for `list.sort()`. Name
   two language-design reasons (not just performance).
5. The Linux kernel uses heap sort in `lib/sort.c`. Given the cache-unfriendly
   nature of heap sort, why is this the right call in kernel space?
6. You're sorting an array of 10⁹ records that don't fit in RAM. Which of the
   three algorithms applies most naturally and why? (Foreshadows day 102.)
