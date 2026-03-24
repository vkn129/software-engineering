"""
Day 26: Unrolled Linked List — Full Implementation

An unrolled linked list stores multiple elements per node to reduce pointer
chasing and exploit CPU cache lines. This is the same insight behind B-trees
(multiple keys per node to minimize disk seeks) applied to a linear list.

The block size controls the trade-off:
  - Large blocks = better cache behavior, worse insert/delete (more shifting)
  - Small blocks = worse cache behavior, better insert/delete
  - sqrt(n) blocks = balanced O(sqrt(n)) for both

Python's collections.deque uses exactly this idea: a doubly linked list of
64-element blocks. We build the singly-linked version here to understand
the mechanics before the optimization.

Run: python unrolled_linked_list.py
"""

import math


# ---------------------------------------------------------------------------
# Node: holds an array of elements instead of a single element
# ---------------------------------------------------------------------------

class UnrolledNode:
    """A node in an unrolled linked list.

    Each node holds up to max_size elements in a contiguous Python list.
    In C, this would be an inline array — truly contiguous in memory.
    In Python, the list object's internal array still gives us better
    locality than separate node objects scattered across the heap.
    """

    __slots__ = ('elements', 'next', 'max_size')

    def __init__(self, max_size):
        self.elements = []       # holds up to max_size items
        self.next = None         # pointer to the next UnrolledNode
        self.max_size = max_size

    @property
    def count(self):
        """Number of elements currently in this node."""
        return len(self.elements)

    def is_full(self):
        return self.count >= self.max_size

    def is_underfull(self):
        """A node is underfull when it has fewer than half its capacity.

        This threshold ensures nodes stay reasonably packed, preventing
        degeneration into a one-element-per-node linked list. The factor
        of 2 is the same threshold B-trees use for the same reason.
        """
        return self.count < self.max_size // 2

    def __repr__(self):
        return f"UnrolledNode({self.elements})"


# ---------------------------------------------------------------------------
# Unrolled Linked List
# ---------------------------------------------------------------------------

class UnrolledLinkedList:
    """An unrolled linked list with automatic block splitting and merging.

    Stores n elements across ceil(n / max_size) nodes. Each node holds
    a Python list of up to max_size elements. Traversal to find the right
    node is O(n / max_size), and operations within a node are O(max_size).

    With max_size = sqrt(n), both terms are O(sqrt(n)), giving O(sqrt(n))
    insert, delete, and index access.
    """

    def __init__(self, max_size=None):
        """Initialize an empty unrolled linked list.

        Args:
            max_size: Maximum elements per node. If None, defaults to 4.
                      In practice, choose based on cache line size or sqrt(n).
        """
        # Default to a small block size; callers can tune this.
        # A real implementation would pick based on sizeof(element) and
        # the CPU's cache line width (typically 64 bytes).
        self.max_size = max_size if max_size is not None else 4
        self.head = None
        self._size = 0  # total element count across all nodes

    def __len__(self):
        return self._size

    # -----------------------------------------------------------------------
    # Insert
    # -----------------------------------------------------------------------

    def insert(self, index, value):
        """Insert value at the given index (0-based).

        Strategy:
          1. Walk the node chain to find which node contains position `index`.
          2. Insert into that node's element array.
          3. If the node overflows (count > max_size), split it.

        Time: O(n / B + B) where B = max_size.
        """
        # Clamp index to valid range — same behavior as Python's list.insert()
        if index < 0:
            index = max(0, self._size + index)
        if index > self._size:
            index = self._size

        # Empty list: create the first node
        if self.head is None:
            self.head = UnrolledNode(self.max_size)
            self.head.elements.append(value)
            self._size += 1
            return

        # Walk to the node that contains position `index`.
        # We track how many elements we've passed to know the local offset.
        node = self.head
        pos = index
        while node.next is not None and pos > node.count:
            # Why > and not >=: if pos == node.count, we insert at the end
            # of this node rather than the beginning of the next. This keeps
            # the current node packed and avoids unnecessary traversal.
            pos -= node.count
            node = node.next

        # Edge case: pos might exceed this (last) node's count if we're
        # appending past the end. Clamp to the node's count.
        if pos > node.count:
            pos = node.count

        # Insert into this node's array. This is an O(B) shift operation —
        # Python's list.insert does the memmove internally.
        node.elements.insert(pos, value)
        self._size += 1

        # Split if the node overflowed
        if node.count > self.max_size:
            self._split(node)

    def append(self, value):
        """Append to the end. Convenience wrapper around insert."""
        self.insert(self._size, value)

    def _split(self, node):
        """Split a node that has exceeded max_size.

        Move the second half of elements to a new node. This is the key
        operation that keeps the structure balanced — without it, one node
        would grow without bound and we'd degenerate to an array.

        Analogous to B-tree node splitting: when a node has too many keys,
        split it and push the median up. Here we just split; there's no
        tree structure to propagate to.
        """
        mid = node.count // 2
        new_node = UnrolledNode(self.max_size)

        # Move second half to the new node.
        # Slicing creates a new list — O(B) but unavoidable.
        new_node.elements = node.elements[mid:]
        node.elements = node.elements[:mid]

        # Wire the new node into the chain
        new_node.next = node.next
        node.next = new_node

    # -----------------------------------------------------------------------
    # Delete
    # -----------------------------------------------------------------------

    def delete(self, index):
        """Delete the element at the given index.

        Strategy:
          1. Walk to the node containing position `index`.
          2. Remove the element from the node's array.
          3. If the node becomes underfull, merge or rebalance with neighbor.
          4. If the node becomes empty, remove it from the chain.

        Time: O(n / B + B) where B = max_size.
        """
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError(f"delete index {index} out of range for size {self._size}")

        # Walk to the right node
        node = self.head
        prev = None
        pos = index
        while pos >= node.count:
            pos -= node.count
            prev = node
            node = node.next

        # Remove from the node's array — O(B) shift
        removed = node.elements.pop(pos)
        self._size -= 1

        # If the node is now empty, unlink it entirely
        if node.count == 0:
            if prev is None:
                # Removing the head node
                self.head = node.next
            else:
                prev.next = node.next
            return removed

        # If underfull, try to merge with the next node or rebalance
        if node.is_underfull() and node.next is not None:
            self._merge_or_rebalance(node)

        return removed

    def _merge_or_rebalance(self, node):
        """Merge an underfull node with its neighbor, or rebalance.

        Merging keeps nodes well-packed, which is critical for cache
        performance. If every deletion left nodes half-empty, we'd waste
        half our memory and double our cache misses.

        Two cases:
          1. Combined count fits in one node -> merge (absorb next into node).
          2. Combined count too large -> steal elements from next node until
             this node is at least half full.
        """
        next_node = node.next
        if next_node is None:
            return

        combined = node.count + next_node.count

        if combined <= self.max_size:
            # Case 1: merge — absorb next node's elements
            node.elements.extend(next_node.elements)
            node.next = next_node.next
        else:
            # Case 2: rebalance — steal from next until we're half full
            # We want this node to have at least max_size // 2 elements.
            while node.count < self.max_size // 2 and next_node.count > 0:
                node.elements.append(next_node.elements.pop(0))

            # If we drained the next node, remove it
            if next_node.count == 0:
                node.next = next_node.next

    # -----------------------------------------------------------------------
    # Search
    # -----------------------------------------------------------------------

    def search(self, value):
        """Find the first index of value, or -1 if not found.

        Must check every element — no ordering guarantees, so this is O(n).
        The only advantage over a regular linked list is fewer cache misses
        during traversal (elements within each node are contiguous).
        """
        global_index = 0
        node = self.head
        while node is not None:
            for i, elem in enumerate(node.elements):
                if elem == value:
                    return global_index + i
            global_index += node.count
            node = node.next
        return -1

    # -----------------------------------------------------------------------
    # Index-based access
    # -----------------------------------------------------------------------

    def get(self, index):
        """Get the element at the given index.

        Walks the node chain, skipping whole nodes at a time. This is why
        unrolled linked lists are better than regular linked lists for
        random access: you skip B elements per pointer chase instead of 1.

        Time: O(n / B) where B = max_size.
        """
        if index < 0:
            index = self._size + index
        if index < 0 or index >= self._size:
            raise IndexError(f"index {index} out of range for size {self._size}")

        node = self.head
        pos = index
        while pos >= node.count:
            pos -= node.count
            node = node.next

        return node.elements[pos]

    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------

    def to_list(self):
        """Flatten all elements into a single Python list.

        Useful for debugging and testing. Visits every node sequentially.
        """
        result = []
        node = self.head
        while node is not None:
            result.extend(node.elements)
            node = node.next
        return result

    def __repr__(self):
        """Show the internal block structure — reveals how elements are distributed."""
        blocks = []
        node = self.head
        while node is not None:
            blocks.append(str(node.elements))
            node = node.next
        return " -> ".join(blocks) if blocks else "[]"

    def node_count(self):
        """Count the number of nodes. Useful for verifying split/merge behavior."""
        count = 0
        node = self.head
        while node is not None:
            count += 1
            node = node.next
        return count


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_basic_operations():
    """Show insert, delete, search, get, and the internal block structure."""
    print("=" * 60)
    print("BASIC OPERATIONS")
    print("=" * 60)

    ull = UnrolledLinkedList(max_size=4)

    # Insert elements 0..9
    print("\nInserting 0 through 9:")
    for i in range(10):
        ull.append(i)
    print(f"  Structure: {ull}")
    print(f"  Flat list: {ull.to_list()}")
    print(f"  Length: {len(ull)}, Nodes: {ull.node_count()}")

    # Index-based access
    print(f"\n  get(0) = {ull.get(0)}")
    print(f"  get(5) = {ull.get(5)}")
    print(f"  get(9) = {ull.get(9)}")

    # Search
    print(f"\n  search(7) = index {ull.search(7)}")
    print(f"  search(99) = index {ull.search(99)}")

    # Delete
    print(f"\n  Deleting index 0 (value {ull.get(0)}):")
    ull.delete(0)
    print(f"  Structure: {ull}")

    print(f"\n  Deleting index 4 (value {ull.get(4)}):")
    ull.delete(4)
    print(f"  Structure: {ull}")
    print(f"  Flat list: {ull.to_list()}")
    print(f"  Length: {len(ull)}, Nodes: {ull.node_count()}")


def demo_splitting():
    """Show how block splitting works as we insert into a full node."""
    print("\n" + "=" * 60)
    print("BLOCK SPLITTING")
    print("=" * 60)

    ull = UnrolledLinkedList(max_size=4)

    for i in range(1, 5):
        ull.append(i)
    print(f"\n  After inserting 1-4: {ull}")
    print(f"  Nodes: {ull.node_count()} (one node, full)")

    ull.append(5)
    print(f"\n  After inserting 5 (triggers split): {ull}")
    print(f"  Nodes: {ull.node_count()} (two nodes after split)")

    for i in range(6, 10):
        ull.append(i)
    print(f"\n  After inserting 6-9: {ull}")
    print(f"  Nodes: {ull.node_count()}")


def demo_merging():
    """Show how block merging works when nodes become underfull."""
    print("\n" + "=" * 60)
    print("BLOCK MERGING")
    print("=" * 60)

    ull = UnrolledLinkedList(max_size=4)

    for i in range(8):
        ull.append(i)
    print(f"\n  Initial: {ull}")
    print(f"  Nodes: {ull.node_count()}")

    # Delete from the first node until it's underfull
    print(f"\n  Deleting index 0 (value 0):")
    ull.delete(0)
    print(f"  Structure: {ull}")

    print(f"\n  Deleting index 0 (value 1):")
    ull.delete(0)
    print(f"  Structure: {ull}")
    print(f"  Nodes: {ull.node_count()} (may have merged)")


def demo_cache_argument():
    """Illustrate WHY cache locality matters with a simple timing test."""
    print("\n" + "=" * 60)
    print("CACHE LOCALITY ARGUMENT")
    print("=" * 60)

    import time

    n = 50_000

    # Regular linked list: each node is a separate object
    class LLNode:
        __slots__ = ('val', 'next')
        def __init__(self, val):
            self.val = val
            self.next = None

    # Build linked list
    ll_head = LLNode(0)
    current = ll_head
    for i in range(1, n):
        current.next = LLNode(i)
        current = current.next

    # Build unrolled linked list
    ull = UnrolledLinkedList(max_size=64)
    for i in range(n):
        ull.append(i)

    # Build Python list
    py_list = list(range(n))

    # Time traversal: linked list
    start = time.perf_counter()
    total = 0
    node = ll_head
    while node:
        total += node.val
        node = node.next
    ll_time = time.perf_counter() - start

    # Time traversal: unrolled linked list
    start = time.perf_counter()
    total = 0
    nd = ull.head
    while nd:
        for elem in nd.elements:
            total += elem
        nd = nd.next
    ull_time = time.perf_counter() - start

    # Time traversal: Python list
    start = time.perf_counter()
    total = 0
    for elem in py_list:
        total += elem
    list_time = time.perf_counter() - start

    print(f"\n  Traversal of {n:,} elements:")
    print(f"    Linked list:   {ll_time*1000:.2f} ms")
    print(f"    Unrolled (B=64): {ull_time*1000:.2f} ms")
    print(f"    Python list:   {list_time*1000:.2f} ms")
    print(f"\n  Unrolled is ~{ll_time/ull_time:.1f}x faster than regular linked list")
    print(f"  (Python list wins overall because it's a C array under the hood)")


if __name__ == "__main__":
    demo_basic_operations()
    demo_splitting()
    demo_merging()
    demo_cache_argument()
    print("\n" + "=" * 60)
    print("All demos complete.")
    print("=" * 60)
