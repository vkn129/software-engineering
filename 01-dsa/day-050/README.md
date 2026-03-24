# Day 50: Binary Heaps — The Array-Based Priority Queue

## Why This Exists

You have BSTs, AVL trees, and red-black trees — all O(log n) for insert/delete/search. So why do we need yet another tree-shaped data structure?

Because **priority queues don't need search**. A priority queue only needs two operations: insert an element with a priority, and extract the element with the highest (or lowest) priority. If you don't need arbitrary search, you can exploit a much simpler structure that fits entirely in a contiguous array — no pointers, no allocations, no cache misses.

A binary heap is a **complete binary tree stored in an array**. "Complete" means every level is fully filled except possibly the last, which is filled left-to-right. This completeness guarantee means the tree's shape is entirely determined by its size — you don't need left/right/parent pointers because you can compute them arithmetically:

```
parent(i) = (i - 1) // 2
left(i)   = 2 * i + 1
right(i)  = 2 * i + 2
```

This is not just a cute trick. It means the heap lives in a single contiguous block of memory with zero pointer overhead. Modern CPUs prefetch sequential memory — when you sift down a heap, you're walking through array indices that are close together, hitting L1/L2 cache. A red-black tree storing the same data scatters nodes across the heap (memory heap, not data structure heap), causing cache misses on every pointer dereference.

This is why the OS scheduler uses a heap for its ready queue, Dijkstra's algorithm uses a heap for its frontier, and Python's `heapq` is one of the most-used standard library modules.

## Theory (40 min)

### The Heap Property

A **min-heap** satisfies: every node's key is ≤ its children's keys. The minimum is always at the root (index 0).

A **max-heap** satisfies: every node's key is ≥ its children's keys. The maximum is always at the root.

```
Min-heap:              Array: [1, 3, 2, 7, 6, 5, 4]
       1
      / \             Index:  0  1  2  3  4  5  6
     3   2
    / \ / \           parent(3) = (3-1)//2 = 1 → value 3 ✓
   7  6 5  4          left(1)   = 2*1+1    = 3 → value 7
                      right(1)  = 2*1+2    = 4 → value 6
```

### Sift Up (Bubble Up)

When you insert at the end, the heap property might be violated between the new node and its parent. Sift up swaps the node with its parent repeatedly until the property is restored.

Time: O(log n) — at most the height of the tree.

### Sift Down (Bubble Down)

When you extract the root (min/max), you replace it with the last element and sift down — swap with the smaller (min-heap) or larger (max-heap) child until the property is restored.

Time: O(log n) — at most the height of the tree.

### Heapify — Building a Heap in O(n)

The naive approach: insert n elements one by one → O(n log n).

The clever approach (Floyd's algorithm): start from the last non-leaf node and sift down each node. This is O(n), not O(n log n).

**Why O(n)?** Most nodes are near the bottom and sift down a short distance:
- n/2 nodes at the bottom sift 0 levels
- n/4 nodes sift at most 1 level
- n/8 nodes sift at most 2 levels
- ...
- 1 node (root) sifts at most log n levels

Total work: Σ (n/2^(k+1)) * k for k=0..log(n) = O(n)

This is the same series as 1/2 + 2/4 + 3/8 + 4/16 + ... which converges to 2.

### Complexity Summary

| Operation | Time | Why |
|-----------|------|-----|
| insert | O(log n) | Sift up from bottom |
| extract_min/max | O(log n) | Sift down from top |
| peek | O(1) | Root is always min/max |
| heapify (build) | O(n) | Floyd's bottom-up |
| decrease_key | O(log n) | Sift up from position |
| delete arbitrary | O(log n) | Decrease to -∞, then extract |

## Practice (20 min)

See `practice.py` — 6 exercises from heap basics to production patterns like k-way merge and streaming median.

## Daily Project

`heap.py` implements MinHeap and MaxHeap from scratch with full sift operations, heapify, and demonstrations showing the array-tree duality.

## Checkpoint Questions

1. Why is a binary heap always stored in an array rather than with pointers? What's the performance difference?
2. Prove that Floyd's heapify is O(n), not O(n log n). Where does the key insight come from?
3. Why can't you do O(log n) search in a heap? What's the fundamental difference from a BST?
4. If you need both insert and extract-min to be O(log n), but also need O(log n) decrease-key, what data structure do you need beyond a basic heap?
5. Python's heapq only provides a min-heap. How would you implement a max-heap using heapq? What's the trade-off?
6. Why does Dijkstra's algorithm need a priority queue? What happens if you use a regular queue instead?
