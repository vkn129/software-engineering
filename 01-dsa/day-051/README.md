# Day 51: Heap Applications — Where Priority Queues Shine

## Why This Exists

Yesterday you built a heap. Today you see why it's one of the most-used data structures in production systems. The pattern is always the same: **maintain a small heap to track the most important elements from a large stream**.

This pattern appears everywhere:
- **Top-K problems**: Keep a min-heap of size k. After processing millions of items, the heap contains exactly the top k. Used in search ranking, recommendation engines, and monitoring dashboards.
- **Running median**: Two heaps splitting the data in half. Used in real-time analytics, financial trading, and health monitoring.
- **Event-driven simulation**: A min-heap of (timestamp, event) pairs. Used in network simulators, game engines, and discrete event systems.
- **Heapsort**: In-place O(n log n) with worst-case guarantee. Used when you can't afford quicksort's O(n²) worst case (real-time systems).

The key insight: heaps are NOT for searching. They're for repeatedly answering "what's the most extreme element?" in O(log n).

## Theory (40 min)

### Top-K Pattern

To find the k largest elements from n items:
- **Naive**: Sort everything → O(n log n)
- **Heap**: Min-heap of size k → O(n log k)

When k << n (e.g., top 10 from 1 billion), the heap approach is dramatically faster because log(10) ≈ 3.3 vs log(1B) ≈ 30.

### Two-Heap Median Pattern

```
MaxHeap (small half)    MinHeap (large half)
    [1, 2, 3]              [4, 5, 6]
     top: 3                 top: 4

Median = (3 + 4) / 2 = 3.5
```

Invariants:
1. max_heap.top() <= min_heap.top()
2. Sizes differ by at most 1
3. If odd count, max_heap has the extra element

### Heapsort Analysis

| Property | Value |
|----------|-------|
| Time (best) | O(n log n) |
| Time (worst) | O(n log n) |
| Space | O(1) in-place |
| Stable | No |
| Cache-friendly | No (sift-down jumps around) |

## Practice (20 min)

See `practice.py` — 5 exercises on frequency sort, k closest points, string reorganization, rope connection, and the IPO problem.

## Daily Project

`heap_applications.py` implements top-K extraction, running median, event simulation, and frequency-based sorting.

## Checkpoint Questions

1. Why use a min-heap (not max-heap) to find the top-K largest elements?
2. In the two-heap median, why does the max-heap store the smaller half?
3. When would you choose heapsort over quicksort in production?
4. How does the event-driven simulation pattern relate to Dijkstra's algorithm?
5. What's the time complexity of finding the median after n insertions using the two-heap approach?
