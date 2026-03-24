# Day 61: K-way Merge and Top-K Problems

## Why This Exists

You have a min-heap from Day 50 that extracts the minimum in O(log n). Now consider a deceptively simple question: you have k sorted streams of data and you need to merge them into one sorted stream. How?

The naive approach scans all k stream heads to find the minimum, picks it, advances that stream, and repeats. Every extraction costs O(k) because you compare k heads. With n total elements, that is O(n*k). When k is large (thousands of sorted files in an external sort), this is brutal.

The insight: **a min-heap of size k can find the minimum of k elements in O(log k), not O(k)**. Push all k stream heads into a heap. Pop the minimum, push the next element from that stream. Each of the n elements enters and leaves the heap exactly once, at O(log k) per operation. Total: **O(n log k)**.

This is not a textbook exercise. It is the algorithm behind:
- **External sorting**: when data does not fit in RAM, you split it into sorted chunks (runs), write them to disk, then k-way merge the runs back. The Unix `sort` command does exactly this for large files.
- **MapReduce merge phase**: each mapper produces a sorted partition. The reducer k-way merges them.
- **Database merge joins**: merging sorted runs from disk during a sort-merge join.
- **LSM-tree compaction**: LevelDB, RocksDB, and Cassandra merge sorted SSTables during compaction using k-way merge.
- **Lucene segment merging**: search indices merge posting list segments the same way.

## Theory

### K-way Merge

Given k sorted lists with n total elements:

```
List 0: [1, 5, 9]
List 1: [2, 6, 10]
List 2: [3, 7, 11]
List 3: [4, 8, 12]

Heap initially: [(1,0), (2,1), (3,2), (4,3)]   ← (value, list_index)

Pop (1,0) → output 1, push (5,0) from list 0
Pop (2,1) → output 2, push (6,1) from list 1
Pop (3,2) → output 3, push (7,2) from list 2
Pop (4,3) → output 4, push (8,3) from list 3
Pop (5,0) → output 5, push (9,0) from list 0
...
```

The heap always has at most k elements. Each pop and push is O(log k). With n total elements, the merge is **O(n log k)**.

Compare to concatenate-and-sort: O(n log n). When k << n, n log k << n log n. For 1000 sorted files of 1M records each: log(1000) ~ 10 vs log(10^9) ~ 30. Three times faster, and more importantly, you can stream the output without holding everything in RAM.

### Top-K Problems

Finding the k largest (or smallest) elements without fully sorting. Three approaches, each with different trade-offs:

**Approach 1: Min-heap of size k — O(n log k)**

Maintain a min-heap of size k. For each element: if heap has fewer than k elements, push it. Otherwise, if the element is larger than the heap's minimum, pop the minimum and push the new element. After processing all n elements, the heap contains the k largest.

Why min-heap for top-k *largest*? Because you want to evict the *smallest* of your k candidates. The min-heap exposes the smallest for O(1) comparison and O(log k) removal.

```
Finding top 3 from [5, 1, 8, 3, 9, 2, 7]:

Process 5 → heap: [5]
Process 1 → heap: [1, 5]
Process 8 → heap: [1, 5, 8]         ← heap full (size k=3)
Process 3 → 3 > min(1), replace  → heap: [3, 5, 8]
Process 9 → 9 > min(3), replace  → heap: [5, 8, 9]
Process 2 → 2 < min(5), skip
Process 7 → 7 > min(5), replace  → heap: [7, 8, 9]
```

**Approach 2: Quickselect — O(n) average**

Partition the array around a pivot (like quicksort, but recurse on only one side). After partitioning, elements left of the pivot are smaller, elements right are larger. If the pivot lands at position k, you are done. Otherwise recurse into the half that contains position k.

Average case: n + n/2 + n/4 + ... = O(n). But worst case (bad pivots every time): O(n^2).

**Approach 3: Median-of-medians — O(n) guaranteed**

Choose the pivot deterministically: divide into groups of 5, find each group's median, then recursively find the median of those medians. This guarantees the pivot eliminates at least 30% of elements each time, giving O(n) worst case. But the constant factor is large (~5x), so quickselect with random pivots is faster in practice.

### When Each Approach Wins

| Scenario | Best approach | Why |
|----------|--------------|-----|
| Streaming data (unknown n) | Min-heap | Can process elements one at a time, O(k) memory |
| In-memory array, average case | Quickselect | O(n) with small constant, in-place |
| Need guaranteed O(n) | Median-of-medians | No worst case, but large constant |
| Need sorted top-k | Min-heap | Already maintains sorted-ish structure |
| k is close to n | Full sort | Top-k savings vanish when k ~ n |

### External Sort

When data exceeds RAM, external sort works in two phases:

**Phase 1 — Run generation**: Read chunks that fit in RAM, sort each chunk in memory (using quicksort, mergesort, whatever), write sorted "runs" to disk.

**Phase 2 — Merge**: Open all run files simultaneously, k-way merge them using a min-heap of size k. Each heap entry tracks which run it came from. When you pop the minimum, read the next element from that run's file.

```
1 GB RAM, 100 GB file:
  Phase 1: Create ~100 sorted runs of ~1 GB each
  Phase 2: k-way merge 100 runs, heap size = 100
           Each extraction: O(log 100) ~ 7 comparisons
```

If k is too large (too many runs to merge at once), you do multi-pass merging: merge groups of runs first, then merge the merged results.

## Practice

See `practice.py` — 5 exercises from k-way merge variants to the classic median-of-two-sorted-arrays.

## Daily Project

`kway_merge.py` implements k-way merge, top-k with heaps and quickselect, and an external sort simulation with timing comparisons.

## Checkpoint Questions

1. Why does k-way merge use a min-heap of size k rather than size n? What is the memory and time complexity difference?
2. For finding the top-k largest elements, why do you use a *min*-heap, not a max-heap? What would go wrong with a max-heap?
3. Quickselect is O(n) average for finding the k-th element. Why is it O(n^2) worst case, and how does median-of-medians fix this?
4. In an external sort with 1 TB of data and 1 GB of RAM, how many runs are created in phase 1? What is the heap size during the merge phase?
5. Why does LevelDB/RocksDB use k-way merge during compaction rather than just re-sorting the combined data? What constraint makes merge essential?
6. If you need the top-k elements from a stream where you cannot store all elements, which approach must you use and why are the other approaches impossible?
