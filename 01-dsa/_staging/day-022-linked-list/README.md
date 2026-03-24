# Day 6: Linked Lists — Singly Linked

## Why This Exists

You have arrays. They are fast, cache-friendly, and simple. So why would anyone voluntarily give up O(1) random access and spatial locality to store data in scattered heap-allocated nodes connected by pointers?

Because arrays have a fatal flaw: **insertion and deletion at arbitrary positions cost O(n)**. Every element after the insertion point must shift. When your array has 10 million elements and you need to insert at position 0, you are copying 10 million values one slot to the right. That is not a theoretical problem — it is a production outage waiting to happen.

Linked lists solve this by trading access speed for modification speed. Each element (node) lives independently in memory, pointing to the next. Insert at the head? Allocate a node, point it to the old head, done — O(1). Delete the head? Move the head pointer forward, done — O(1). No shifting. No copying.

The Linux kernel uses linked lists everywhere: the process scheduler maintains a linked list of runnable tasks, the filesystem layer chains buffer cache entries in linked lists, and the networking stack threads packets through linked lists of socket buffers. When you need to frequently add and remove elements from the front or middle of a collection, and you rarely need random access by index, a linked list is the right tool.

The deeper lesson is about **memory layout trade-offs**. Arrays give you contiguous memory and predictable cache behavior at the cost of rigid sizing. Linked lists give you flexible, dynamic structure at the cost of pointer chasing — every "next" dereference is potentially a cache miss, because the next node could be anywhere in RAM. Understanding this trade-off is understanding why hardware constraints shape data structure design.

## Theory (40 min)

### What Is a Linked List?

A linked list is a sequence of **nodes**, where each node contains:
1. **Data** — the value stored at this position.
2. **Next pointer** — a reference to the next node in the sequence (or `None`/`null` if this is the last node).

```
Head -> [data|next] -> [data|next] -> [data|next] -> None
```

There is no underlying array. There is no contiguous block of memory. Each node is a separate object on the heap, and they find each other through pointers.

### Node Structure

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None  # pointer to next node
```

That is the entire data structure at the node level. A linked list is just a pointer to the first node (the "head"). If the head is `None`, the list is empty.

```python
class LinkedList:
    def __init__(self):
        self.head = None  # pointer to first node
```

### Why Non-Contiguous Memory Matters

In an array:
```
Memory: [A][B][C][D][E]
         ^
         base address, every element at base + i * sizeof(element)
```

In a linked list:
```
Memory: ....[C]........[A]....[E].....[B]......[D]....
             |          |      ^       |        ^
             +-->addr   +------+       +--------+
```

Nodes can live anywhere in the heap. The "next" pointer in each node is literally a memory address. To find the 5th element, you cannot compute an offset — you must start at the head and follow 4 pointers. This is **pointer chasing**, and it is slow because each dereference may trigger a CPU cache miss.

### Operation Complexities

| Operation | Array | Singly Linked List |
|-----------|-------|--------------------|
| Access by index | O(1) | O(n) |
| Search | O(n) | O(n) |
| Insert at head | O(n) | **O(1)** |
| Insert at tail | O(1) amortized* | O(n) or O(1) with tail pointer |
| Insert at position k | O(n) | O(k) traversal + O(1) splice |
| Delete at head | O(n) | **O(1)** |
| Delete at tail | O(1) | O(n) — must find second-to-last |
| Delete at position k | O(n) | O(k) traversal + O(1) splice |

*Arrays with dynamic resizing (like Python lists) amortize tail insertion to O(1), but still pay O(n) for head insertion.

### Insert at Head — Why It Is O(1)

```python
def insert_at_head(self, data):
    new_node = Node(data)
    new_node.next = self.head  # point new node to old head
    self.head = new_node       # update head to new node
```

```
Before: Head -> [B] -> [C] -> None
After:  Head -> [A] -> [B] -> [C] -> None
```

Two pointer assignments. Done. No shifting. This is why linked lists exist.

### Delete at Head — Why It Is O(1)

```python
def delete_at_head(self):
    if self.head is None:
        return None
    data = self.head.data
    self.head = self.head.next  # skip over the old head
    return data
```

One pointer assignment. The old head node becomes garbage (collected by Python's GC or freed manually in C).

### The Traversal Pattern

Almost every linked list operation follows this pattern:

```python
current = self.head
while current is not None:
    # do something with current.data
    current = current.next
```

You start at the head and walk forward, one node at a time. You cannot skip ahead. You cannot go backward (that is Day 7). This is the fundamental limitation that makes random access O(n).

### Insert at Position — The Splice

To insert at position k, you need a pointer to the node at position k-1 (the node BEFORE the insertion point):

```python
def insert_at_position(self, data, position):
    if position == 0:
        return self.insert_at_head(data)
    current = self.head
    for _ in range(position - 1):
        if current is None:
            raise IndexError("Position out of range")
        current = current.next
    new_node = Node(data)
    new_node.next = current.next  # new node points to what was after current
    current.next = new_node       # current now points to new node
```

```
Before: ... -> [prev] -> [next_node] -> ...
After:  ... -> [prev] -> [NEW] -> [next_node] -> ...
```

The traversal to find position k-1 is O(k). The actual splice is O(1). This is the key insight: if you already have a reference to a node, insertion next to it is O(1). The cost is finding the node.

### Memory Overhead

Every node carries a "next" pointer in addition to the data. In Python, a reference is 8 bytes (64-bit pointer). For an integer node, the pointer overhead might exceed the data size. For large objects, the overhead is negligible.

In C:
```c
struct Node {
    int data;    // 4 bytes
    Node* next;  // 8 bytes on 64-bit systems
};
// 12 bytes per node, but with padding probably 16.
// An array of ints: 4 bytes per element. 4x less memory.
```

This overhead is real. Linked lists use more memory than arrays for the same data.

### Cache Behavior — The Hidden Cost

Modern CPUs do not fetch one byte at a time from RAM. They fetch **cache lines** (typically 64 bytes). When you access `arr[i]`, the CPU pulls `arr[i]` through `arr[i+15]` (for 4-byte ints) into the L1 cache. The next 15 accesses are essentially free.

With a linked list, `node.next` could be anywhere in memory. Each pointer dereference potentially fetches a new cache line, wasting the 63 other bytes. This is why iterating over a linked list is slower than iterating over an array *even though both are O(n)* — the constant factor is much larger for the linked list.

Benchmarks typically show linked list traversal is 5-20x slower than array traversal for the same number of elements, purely due to cache effects. Big-O notation hides this because it drops constant factors.

## Practice (20 min)

Work through `practice.py`. Implement a singly linked list from scratch with all core operations. Each function has a docstring explaining what to implement and test cases that verify your solution.

## Daily Project

Run `linked_list.py` to see a full singly linked list implementation with:
- Visual representation of list state after each operation
- Performance comparison between linked list and Python list for head insertions
- Memory layout demonstration showing non-contiguous allocation
- Cache behavior measurement showing the real cost of pointer chasing

Study the output. The performance comparison will make the trade-off concrete: linked lists destroy arrays at head insertion, but arrays destroy linked lists at random access and iteration.

## Checkpoint Questions

1. You have a list of 1 million elements and need to insert 100,000 elements at random positions. Would you use an array or a linked list? What if the insertions were all at position 0? What if they were all at the end?

2. A singly linked list cannot delete a node in O(1) given only a pointer to that node (you need the previous node to update its `next`). Can you think of a trick to effectively "delete" a node given only a pointer to it? What edge case does this trick fail on?

3. Why does the Linux kernel use linked lists extensively for the process scheduler, even though arrays have better cache behavior? What access pattern makes linked lists the right choice there?

4. If you store 1 billion 4-byte integers in a linked list vs an array, roughly how much more memory does the linked list use? (Consider both the pointer overhead and memory allocator overhead per allocation.)

5. You are told "this operation is O(1) for a linked list." Is that the full story? What does Big-O notation hide about linked list performance that matters in practice?
