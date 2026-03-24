# Day 62: Median Maintenance and Fibonacci Heaps

## Why This Exists

You know how to use a heap as a priority queue. But what happens when the question isn't "give me the min" or "give me the max" — it's "give me the median, and keep giving it to me as new numbers arrive"?

The naive approach — sort the data after every insertion — costs O(n log n) per query. With n insertions, that's O(n^2 log n) total. For a million-element stream, that's catastrophic. The trick is to realize that the median splits data into two halves, and you can maintain each half with its own heap: a **max-heap** for the lower half and a **min-heap** for the upper half. The median is always sitting at the top of one (or both) of these heaps. Insertion becomes O(log n) and median query becomes O(1).

This day also covers Fibonacci heaps — theoretically the most powerful heap variant. You'll almost never implement one in production, but understanding *why* it exists reveals deep truths about amortized analysis and why Dijkstra's algorithm has the complexity it does.

## Theory (40 min)

### The Streaming Median Problem

Numbers arrive one at a time. After each arrival, report the current median of all numbers seen so far.

**Naive approach**: Keep a sorted list. Insert with binary search + shift = O(n). Median = O(1) by indexing the middle.
Total for n insertions: O(n^2).

**Two-heap approach**: O(log n) per insertion, O(1) median query.

### The Two-Heap Solution

Maintain two heaps:
- `max_heap`: stores the **lower half** of all numbers. The top is the largest of the small numbers.
- `min_heap`: stores the **upper half** of all numbers. The top is the smallest of the large numbers.

```
Numbers seen: [1, 5, 3, 8, 2, 7]
Sorted:       [1, 2, 3, | 5, 7, 8]
               ^^^^^^^^    ^^^^^^^^
               max_heap    min_heap
               top = 3     top = 5

Median = (3 + 5) / 2 = 4.0
```

**Invariants**:
1. Every element in `max_heap` <= every element in `min_heap`
2. Sizes differ by at most 1: `|len(max_heap) - len(min_heap)| <= 1`

**Insertion algorithm**:
1. If the new number <= top of max_heap, push to max_heap. Otherwise, push to min_heap.
2. Rebalance: if one heap has 2+ more elements than the other, pop from the larger and push to the smaller.

**Median retrieval**:
- If heaps are same size: average of both tops.
- If one is larger: top of the larger heap.

**Why this works**: The median is the value that splits data into equal halves. The max of the lower half and the min of the upper half always bracket the median. By keeping the heaps balanced, at least one top *is* the median.

### Complexity

| Operation | Two-Heap | Naive Sort | Sorted List + bisect |
|-----------|----------|------------|---------------------|
| Insert | O(log n) | O(n log n) | O(n) (shift cost) |
| Find median | O(1) | O(1) | O(1) |
| Total for n ops | O(n log n) | O(n^2 log n) | O(n^2) |

### Fibonacci Heaps — Theoretical Importance

A Fibonacci heap is a collection of heap-ordered trees with two key innovations: **lazy consolidation** and **cascading cuts**. These give it the best amortized bounds of any known heap:

| Operation | Binary Heap | Binomial Heap | Fibonacci Heap |
|-----------|-------------|---------------|----------------|
| insert | O(log n) | O(log n) | **O(1)** amortized |
| find-min | O(1) | O(log n) | **O(1)** |
| extract-min | O(log n) | O(log n) | **O(log n)** amortized |
| decrease-key | O(log n) | O(log n) | **O(1)** amortized |
| merge | O(n) | O(log n) | **O(1)** |
| delete | O(log n) | O(log n) | **O(log n)** amortized |

### Why Dijkstra Cares

Dijkstra's algorithm does V extract-min operations and up to E decrease-key operations:

- **Binary heap**: O((V + E) log V) — because each decrease-key costs O(log V)
- **Fibonacci heap**: O(V log V + E) — because decrease-key is O(1) amortized

For dense graphs where E ~ V^2, this is the difference between O(V^2 log V) and O(V^2 + V log V) = O(V^2). The Fibonacci heap turns the bottleneck from decrease-key into extract-min.

### Fibonacci Heap Structure

```
Root list: circular doubly-linked list of tree roots
           ┌──→ [3] ──→ [1] ──→ [7] ──→ [3] ──┐
           └────────────────────────────────────┘
                        ↓ min
                       [1]
                      / | \
                    [5] [6] [9]
                    |
                   [8]
```

**Key ideas**:
1. **Lazy insertion**: Just add new node to root list. Don't restructure anything.
2. **Lazy consolidation**: Only merge trees of equal degree during extract-min. Use an array indexed by degree to find pairs.
3. **Cascading cuts**: When decrease-key violates heap order, cut the node and move it to the root list. If its parent was already marked (lost one child before), cut the parent too — recursively. This is what gives O(1) amortized decrease-key.
4. **Mark bit**: A node is "marked" when it loses a child. If it loses a second child, it gets cut. This limits the maximum degree to O(log n), which is what makes consolidation work.

### Why Fibonacci Heaps Are Rarely Used in Practice

Despite superior asymptotic complexity:
1. **High constant factors**: Every node needs parent, child, left, right pointers plus degree and mark fields. A binary heap node is just... an array slot.
2. **Poor cache behavior**: Pointer-chasing through a doubly-linked circular list destroys cache locality. Binary heaps walk sequential array memory.
3. **Complex implementation**: ~300 lines for a correct Fibonacci heap vs ~30 for a binary heap. More code = more bugs.
4. **Real-world graphs aren't dense enough**: For the graphs programmers actually encounter, a binary heap with O((V+E) log V) is fast enough. The constant-factor advantage of cache-friendly array access beats the asymptotic advantage of Fibonacci heaps.

Pairing heaps and Brodal queues offer simpler alternatives with similar (or matching) theoretical bounds.

## Practice (20 min)

See `practice.py` — 5 exercises from sliding window median to percentile tracking.

## Daily Project

`median_and_fib_heap.py` implements MedianFinder with the two-heap approach and a simplified but functional Fibonacci heap, with demos comparing approaches.

## Checkpoint Questions

1. In the two-heap median solution, why must the max-heap store the lower half? What breaks if you swap the heap types?
2. You insert 1, 2, 3, 4, 5 into a MedianFinder. Trace the state of both heaps and the median after each insertion.
3. Fibonacci heap decrease-key is O(1) amortized. What is the worst case for a *single* decrease-key call, and why doesn't this matter amortized?
4. Why does the Fibonacci heap mark bit exist? What invariant does it maintain, and what breaks without it?
5. If your graph has V = 1000 and E = 5000 (sparse), would you expect Fibonacci heap Dijkstra to outperform binary heap Dijkstra in practice? Why or why not?
6. The two-heap solution generalizes to maintaining any order statistic. How would you modify it to always return the k-th smallest element instead of the median?
