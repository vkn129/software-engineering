# Day 7: Doubly Linked Lists & Sentinel Nodes

## Why This Exists

Yesterday you built a singly linked list. It works, but it has two frustrating limitations:

1. **You cannot delete a node in O(1) given only a pointer to it.** To delete node X, you need to update the previous node's `next` pointer. In a singly linked list, finding the previous node requires traversing from the head — O(n). This means algorithms that maintain pointers into the middle of the list (like LRU caches) cannot use singly linked lists efficiently.

2. **Edge cases are everywhere.** Inserting at the head is different from inserting in the middle. Deleting the only node is different from deleting one of many. Every operation needs an `if head is None` check, an `if node is head` check, an `if node is tail` check. These branches are bugs waiting to happen.

Doubly linked lists solve problem 1 by adding a `prev` pointer to each node. Given a pointer to any node, you can reach its neighbors in both directions and splice it out in O(1).

Sentinel nodes solve problem 2. Instead of the head and tail being `None`, you create permanent dummy nodes that are always present. The "real" data lives between the sentinels. This eliminates every `None` check because there is always a valid node on both sides of any real node. The code becomes simpler, shorter, and less buggy.

Together, doubly linked lists with sentinels form the backbone of the **LRU cache** — one of the most important data structures in systems programming. Every operating system, database, and web browser uses an LRU cache. The combination of a hash map (O(1) lookup) and a doubly linked list (O(1) move-to-front and eviction) gives O(1) for every LRU operation. Python's `functools.lru_cache` uses exactly this pattern.

Python's `collections.deque` is built on a doubly linked list of fixed-size blocks (a "block-linked list"), combining the modification speed of linked lists with better cache behavior than naive node-per-element linked lists. Understanding the doubly linked list helps you understand why deque operations are O(1) at both ends.

## Theory (40 min)

### From Singly to Doubly Linked

A singly linked node has one pointer: `next`. You can only move forward.

```
[prev?] <- [data|next] -> [data|next] -> [data|next] -> None
```

A doubly linked node has two pointers: `next` and `prev`. You can move in both directions.

```
None <- [prev|data|next] <-> [prev|data|next] <-> [prev|data|next] -> None
```

```python
class DNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None
```

The extra pointer costs memory (one more reference per node) but enables O(1) deletion given a node reference.

### Why O(1) Delete Matters

In a singly linked list, to delete node X:
```
... -> [A] -> [X] -> [B] -> ...
```
You need to set A.next = B. But you only have a pointer to X, not to A. Finding A requires traversal from the head: O(n).

In a doubly linked list:
```
... <-> [A] <-> [X] <-> [B] <-> ...
```
You have `X.prev = A` and `X.next = B`. So:
```python
X.prev.next = X.next   # A.next = B
X.next.prev = X.prev   # B.prev = A
```
Two pointer assignments. O(1). No traversal needed.

This is not a minor optimization. It changes what algorithms are possible. LRU cache requires moving a node to the front of the list on every access. If that move were O(n), the entire LRU cache would be O(n) per operation, which defeats the purpose.

### Sentinel Nodes: Eliminating Edge Cases

Without sentinels, every operation needs branching:
```python
def insert_after(self, node, data):
    new = DNode(data)
    new.prev = node
    new.next = node.next
    if node.next is not None:    # edge case: inserting at tail
        node.next.prev = new
    else:
        self.tail = new          # must update tail pointer
    node.next = new
    if node is self.head and ...:  # more edge cases
        ...
```

With sentinels, you create two permanent dummy nodes:
```
[SENTINEL_HEAD] <-> [real data] <-> [real data] <-> [SENTINEL_TAIL]
```

The sentinel head's `prev` is `None` (or points to sentinel tail in circular variant). The sentinel tail's `next` is `None` (or points to sentinel head). Real data lives between them.

Now insertion never hits an edge case:
```python
def insert_after(self, node, data):
    new = DNode(data)
    new.prev = node
    new.next = node.next
    node.next.prev = new    # always valid — sentinel tail is always there
    node.next = new
```

No `if` statements. No `None` checks. The sentinel guarantees that `node.next` is always a valid node object. This is not just cleaner — it is faster (fewer branch mispredictions) and less error-prone.

### Circular Doubly Linked Lists

Take the sentinel concept further: use a single sentinel where `sentinel.next` is the first real node and `sentinel.prev` is the last real node. The last real node's `next` points back to the sentinel, and the first real node's `prev` points back to the sentinel.

```
     +-> [SENTINEL] <-> [A] <-> [B] <-> [C] -+
     |                                         |
     +-----------------------------------------+
```

An empty list is just the sentinel pointing to itself:
```
[SENTINEL] <-> [SENTINEL]   (sentinel.next = sentinel.prev = sentinel)
```

This is the most elegant form. Every node (including the sentinel) always has valid `prev` and `next` pointers. The Linux kernel's `list_head` structure uses exactly this pattern.

### The LRU Cache: Hash Map + Doubly Linked List

An LRU (Least Recently Used) cache needs three O(1) operations:
1. **Get**: Look up a key and return its value. Move the accessed item to the front (most recently used).
2. **Put**: Insert a key-value pair. If the cache is full, evict the least recently used item (the one at the back).
3. **Evict**: Remove the tail node.

A hash map alone gives O(1) lookup but cannot track usage order. A doubly linked list alone gives O(1) insert/delete but cannot do O(1) lookup. Combine them:

```
Hash Map:  key -> pointer to DLL node
DLL:       most recent <-> ... <-> least recent

Get(key):
  1. Hash map lookup: O(1) -> get node pointer
  2. Move node to head of DLL: O(1) (delete + insert at head)
  3. Return node.value

Put(key, value):
  1. If key exists: update value, move to head
  2. If full: evict tail node, delete from hash map
  3. Create new node, insert at head, add to hash map

Every operation: O(1).
```

This is how your browser cache works. This is how database buffer pools work. This is how CPU caches work (conceptually). The LRU cache is everywhere.

### Python's collections.deque Internals

Python's `deque` is not a naive node-per-element doubly linked list. It uses a **doubly linked list of blocks**, where each block holds up to 64 elements in a contiguous array. This hybrid design gives:

- O(1) append/appendleft (like a linked list)
- Better cache behavior than naive linked lists (elements within a block are contiguous)
- O(n) random access (must traverse blocks)

The block-linked-list pattern is a common real-world optimization: use a linked list at the macro level for flexibility, and arrays at the micro level for cache performance.

### Memory Cost

Each doubly linked node carries two pointers instead of one:
```
Singly linked node: data + 1 pointer = data + 8 bytes
Doubly linked node: data + 2 pointers = data + 16 bytes
```

For small data types, this overhead is significant. For large objects (like cache entries with kilobytes of data), the extra 8 bytes per node is negligible. The choice depends on your data.

## Practice (20 min)

Work through `practice.py`. You will implement a doubly linked list with sentinel nodes and then build an LRU cache on top of it. Each exercise builds on the previous one.

## Daily Project

Run `doubly_linked_list.py` to see:
- A full doubly linked list implementation with sentinel nodes
- Visual comparisons of singly vs doubly linked list edge case handling
- A complete LRU cache implementation with step-by-step visualization
- Performance benchmarks showing O(1) LRU cache operations

Study how the sentinel nodes eliminate every `None` check. Then study how the LRU cache combines the hash map and doubly linked list — this pattern will appear repeatedly in systems programming.

## Checkpoint Questions

1. Why can you delete a node in O(1) with a doubly linked list but not a singly linked list? What specific information does the `prev` pointer provide that enables this?

2. Sentinel nodes eliminate edge cases, but they use memory even when the list is empty. Under what circumstances would you choose NOT to use sentinels? (Hint: think about millions of very small lists.)

3. In the LRU cache, why do we store the key in the DLL node even though the hash map also has the key? What operation would break if the node did not store its own key?

4. Python's `collections.deque` uses blocks of 64 elements instead of individual nodes. Why is 64 a good block size? (Hint: what is the typical CPU cache line size, and how does block size relate to it?)

5. You are building a text editor that needs to support insert-character, delete-character, and move-cursor-left/right efficiently. Would you use an array, a singly linked list, or a doubly linked list for the character buffer? Justify your answer with complexity analysis for each operation.
