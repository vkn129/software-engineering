# Day 26: Unrolled Linked Lists

## Why This Exists

Regular linked lists have a dirty secret: they are catastrophically bad for modern CPUs. Every node is a separate heap allocation scattered randomly in memory. Following a `next` pointer almost always triggers a cache miss — the CPU stalls for ~100 nanoseconds waiting for RAM while it could have executed ~400 instructions. For a list of n elements, traversal causes O(n) cache misses. An array causes O(n/16) cache misses (assuming 64-byte cache lines holding 4-byte integers). The linked list is 16x slower *in wall-clock time* despite having the same O(n) complexity.

The unrolled linked list fixes this by storing **multiple elements per node**. Instead of one element and one pointer, each node holds an array of up to B elements and one pointer. Traversing within a node is sequential memory access — the CPU prefetcher handles it perfectly. You only pay a cache miss when jumping between nodes.

**Where this matters in practice:**

1. **Text editors.** The rope data structure (used in VS Code, Emacs, Xi editor) is essentially an unrolled linked list of character arrays. Inserting a character in the middle of a 10MB file needs to shift elements within one small block, not reallocate the entire buffer. The block-linked structure gives O(sqrt(n)) insert/delete while maintaining good cache behavior for sequential reads.

2. **Database index pages.** B-trees store multiple keys per node for exactly the same reason — maximize useful data per cache line fetch. An unrolled linked list is a simplified, linear version of this insight.

3. **Python's `collections.deque`.** CPython implements deque as a doubly linked list of 64-element blocks. This is an unrolled linked list. That is why `deque` has O(1) append/pop at both ends AND better iteration performance than a naive node-per-element linked list.

4. **Memory allocators.** Free lists in allocators (like glibc's `malloc`) often group free chunks into blocks to reduce pointer-chasing overhead during allocation.

## Theory (40 min)

### Structure: Multiple Elements Per Node

A regular linked list node:
```
[data | next] -> [data | next] -> [data | next] -> None
```
3 elements = 3 nodes = 3 pointer chases.

An unrolled linked list node with block size B=4:
```
[ [d0, d1, d2, d3] | count=4 | next ] -> [ [d4, d5, d6] | count=3 | next ] -> None
```
7 elements = 2 nodes = 1 pointer chase. Elements within each node are contiguous in memory.

```python
class UnrolledNode:
    def __init__(self, max_size):
        self.elements = []      # array of up to max_size elements
        self.next = None
        self.max_size = max_size
```

### Optimal Block Size: sqrt(n)

The block size B controls the trade-off:
- **B = 1**: Degenerates to a regular linked list. O(n) nodes, O(1) per-node work.
- **B = n**: Degenerates to a single array. O(1) nodes, O(n) per-node work (shifting elements).
- **B = sqrt(n)**: The sweet spot. O(n/sqrt(n)) = O(sqrt(n)) nodes to traverse, O(sqrt(n)) elements to shift within a node. Total: O(sqrt(n)) for insert/delete.

In practice, B is often chosen based on cache line size rather than n. A cache line is typically 64 bytes. If elements are 4-byte integers, B = 16 fills one cache line exactly. For 8-byte pointers/references, B = 8. The goal: one node's elements should fit in one or two cache lines.

### Block Splitting

When a node reaches capacity (count == max_size) and you need to insert:

1. Create a new node.
2. Move the second half of the full node's elements to the new node.
3. Insert the new node after the full node in the linked list.
4. Insert the new element into whichever half it belongs to.

```
Before (max_size=4, inserting X at position 2):
  [ [A, B, C, D] | 4 | next ] -> ...

Split:
  [ [A, B] | 2 | ] -> [ [C, D] | 2 | next ] -> ...

Insert X at position 2:
  [ [A, B, X] | 3 | ] -> [ [C, D] | 2 | next ] -> ...
```

This is analogous to B-tree node splitting. The key insight: splitting is O(B) work, but it happens only once every B insertions (amortized O(1) splits per insert).

### Block Merging

When a node becomes too empty (count < max_size / 2) after a deletion:

- **If the next node exists and combined count fits in one node:** merge the two nodes.
- **If the next node exists but combined count is too large:** rebalance by stealing elements from the next node.

This prevents degeneration back into a regular linked list (one element per node).

```
Before (max_size=4, delete from first node):
  [ [A] | 1 | ] -> [ [B, C] | 2 | next ] -> ...

Merge (1 + 2 <= 4):
  [ [A, B, C] | 3 | next ] -> ...
```

### Cache Performance Analysis

| Operation | Regular Linked List | Unrolled (B = sqrt(n)) | Array |
|-----------|-------------------|----------------------|-------|
| Traverse all | O(n) misses | O(n/B) misses | O(n/L) misses |
| Insert at index | O(n) time, O(n) misses | O(sqrt(n)) time | O(n) time, O(n/L) misses |
| Delete at index | O(n) time, O(n) misses | O(sqrt(n)) time | O(n) time, O(n/L) misses |
| Search | O(n) time | O(n) time | O(n) time |
| Index access | O(n) time | O(sqrt(n)) time | O(1) time |
| Memory overhead | ~2x (pointer per element) | ~1.1x (pointer per B elements) | 1x |

Where L = elements per cache line. The unrolled linked list sits between arrays and linked lists in every dimension — a genuine space-time-cache trade-off.

### Complexity Summary

With block size B:
- **Insert at index i**: O(i/B + B) — traverse i/B nodes, shift up to B elements
- **Delete at index i**: O(i/B + B) — same traversal + potential merge
- **Get index i**: O(i/B) — traverse nodes, index into the right one
- **Search**: O(n) — must check every element
- **Space**: O(n + n/B) — n elements + n/B node overhead pointers

With B = sqrt(n): insert, delete, and index access are all O(sqrt(n)).

## Practice (80 min)

1. **Implement `unrolled_linked_list.py`** — Build UnrolledNode and UnrolledLinkedList from scratch with insert, delete, search, get, and block splitting/merging.

2. **Complete `practice.py`** — Four exercises:
   - Exercise 1: Index-based access with O(sqrt(n)) traversal
   - Exercise 2: Benchmark unrolled linked list vs regular linked list vs Python list
   - Exercise 3: Implement the `__iter__` protocol for Pythonic iteration
   - Exercise 4: Find the optimal block size empirically through benchmarking

## Checkpoint Questions

Before moving on, you should be able to answer:

1. **Why does storing multiple elements per node improve cache performance?** Because elements within a node are contiguous in memory, so accessing one loads nearby elements into the same cache line. The CPU prefetcher can predict sequential access patterns within a node. You only pay a cache miss when following the `next` pointer to a different node.

2. **Why is sqrt(n) the optimal block size for minimizing worst-case time?** With B nodes of size B (where B = sqrt(n)), you traverse at most sqrt(n) nodes to find the right one, then shift at most sqrt(n) elements within that node. Any other block size makes one of these terms larger. This is the AM-GM inequality applied to data structures.

3. **What triggers a block split, and why is it amortized O(1)?** A split happens when inserting into a full node (count == max_size). After splitting, both resulting nodes are half full, so you need max_size/2 more insertions before either one needs splitting again. Over a sequence of n insertions, you get at most 2n/max_size splits, each costing O(max_size) work. Total split cost: O(n). Amortized per insertion: O(1).

4. **When should you merge vs. rebalance blocks?** Merge when the combined element count of two adjacent nodes fits within max_size. Rebalance (steal elements from the neighbor) when merging would overflow. The threshold for triggering either is typically count < max_size/2 — this ensures nodes stay at least half full, which bounds memory waste to 2x.

5. **How does this relate to B-trees?** A B-tree is an unrolled linked list generalized to a tree. Each B-tree node stores multiple keys (like an unrolled linked list node stores multiple elements) and has multiple children. The motivation is identical: minimize pointer chases by packing more useful data per node, which aligns with cache line and disk page boundaries. B-trees optimize for disk I/O; unrolled linked lists optimize for CPU cache.
