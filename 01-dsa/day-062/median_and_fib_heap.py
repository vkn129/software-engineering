"""
Day 62: Median Maintenance and Fibonacci Heaps

Two core ideas:
1. Streaming median via two heaps — O(log n) insert, O(1) query
2. Fibonacci heap — theoretically optimal heap for decrease-key-heavy algorithms

No external dependencies. Python 3.6+.
"""

import heapq
import time
import random
import math


# =============================================================================
# Part 1: MedianFinder — Two-Heap Approach
# =============================================================================

class MedianFinder:
    """
    Maintain a running median as numbers arrive one by one.

    Strategy: split all numbers into a lower half (max-heap) and upper half
    (min-heap). The median is always at the top of one or both heaps.

    Python's heapq is a min-heap, so we negate values to simulate a max-heap.
    """

    def __init__(self):
        # max-heap for lower half (stored as negated values)
        self.lo = []
        # min-heap for upper half
        self.hi = []

    def add_num(self, num: int) -> None:
        """Insert a number and rebalance. O(log n)."""
        # Decide which heap to push to.
        # If lo is empty or num belongs in the lower half, push to lo.
        if not self.lo or num <= -self.lo[0]:
            heapq.heappush(self.lo, -num)
        else:
            heapq.heappush(self.hi, num)

        # Rebalance: sizes must differ by at most 1, with lo allowed to be
        # one larger (so median comes from lo when count is odd).
        if len(self.lo) > len(self.hi) + 1:
            val = -heapq.heappop(self.lo)
            heapq.heappush(self.hi, val)
        elif len(self.hi) > len(self.lo):
            val = heapq.heappop(self.hi)
            heapq.heappush(self.lo, -val)

    def find_median(self) -> float:
        """Return the current median. O(1)."""
        if not self.lo:
            raise ValueError("No numbers added yet")
        if len(self.lo) > len(self.hi):
            return float(-self.lo[0])
        else:
            return (-self.lo[0] + self.hi[0]) / 2.0

    def __len__(self):
        return len(self.lo) + len(self.hi)


# =============================================================================
# Part 2: Fibonacci Heap
# =============================================================================

class FibNode:
    """Node in a Fibonacci heap. Part of a circular doubly-linked list."""

    __slots__ = ['key', 'degree', 'parent', 'child', 'mark', 'prev', 'next']

    def __init__(self, key):
        self.key = key
        self.degree = 0       # number of children
        self.parent = None
        self.child = None     # pointer to one child (head of child list)
        self.mark = False     # has this node lost a child since becoming a child itself?
        # Circular doubly-linked list pointers (initially points to self)
        self.prev = self
        self.next = self

    def __repr__(self):
        return f"FibNode({self.key})"


class FibonacciHeap:
    """
    Simplified but functional Fibonacci heap.

    Amortized complexities:
      insert:       O(1)
      find_min:     O(1)
      extract_min:  O(log n)
      decrease_key: O(1)
      merge:        O(1)
    """

    def __init__(self):
        self.min_node = None
        self.n = 0

    def __len__(self):
        return self.n

    def __bool__(self):
        return self.n > 0

    # --- Circular list helpers -----------------------------------------------

    @staticmethod
    def _insert_into_list(head, node):
        """Insert node into the circular list that head belongs to. Returns new head (unchanged)."""
        if head is None:
            node.prev = node
            node.next = node
            return node
        node.next = head.next
        node.prev = head
        head.next.prev = node
        head.next = node
        return head

    @staticmethod
    def _remove_from_list(node):
        """Remove node from its circular list. Returns a remaining node, or None if list is now empty."""
        if node.next is node:
            return None  # was the only node
        node.prev.next = node.next
        node.next.prev = node.prev
        remaining = node.next
        node.prev = node
        node.next = node
        return remaining

    @staticmethod
    def _merge_lists(a, b):
        """Concatenate two circular doubly-linked lists. Returns head of merged list."""
        if a is None:
            return b
        if b is None:
            return a
        # Splice b's list right after a
        a_next = a.next
        b_prev = b.prev
        a.next = b
        b.prev = a
        a_next.prev = b_prev
        b_prev.next = a_next
        return a

    @staticmethod
    def _iterate_list(head):
        """Yield all nodes in the circular list starting from head."""
        if head is None:
            return
        node = head
        while True:
            yield node
            node = node.next
            if node is head:
                break

    # --- Core operations -----------------------------------------------------

    def insert(self, key) -> FibNode:
        """Insert a key. O(1) — just add to root list."""
        node = FibNode(key)
        self.min_node = self._insert_into_list(self.min_node, node)
        if node.key < self.min_node.key:
            self.min_node = node
        self.n += 1
        return node

    def find_min(self):
        """Return the minimum key. O(1)."""
        if self.min_node is None:
            raise ValueError("Heap is empty")
        return self.min_node.key

    def extract_min(self) -> FibNode:
        """Remove and return the node with minimum key. O(log n) amortized."""
        z = self.min_node
        if z is None:
            raise ValueError("Heap is empty")

        # Add all children of z to root list
        if z.child:
            children = list(self._iterate_list(z.child))
            for child in children:
                child.parent = None
            # Merge children into root list
            self.min_node = self._merge_lists(self.min_node, z.child)
            z.child = None

        # Remove z from root list
        if z.next is z:
            # z was the only root and had no children (those are already merged)
            self.min_node = None
        else:
            self.min_node = self._remove_from_list(z)
            self._consolidate()

        self.n -= 1
        z.prev = z
        z.next = z
        return z

    def decrease_key(self, node: FibNode, new_key) -> None:
        """Decrease the key of a node. O(1) amortized via cascading cuts."""
        if new_key > node.key:
            raise ValueError(f"New key {new_key} is greater than current key {node.key}")
        node.key = new_key
        parent = node.parent

        if parent and node.key < parent.key:
            self._cut(node, parent)
            self._cascading_cut(parent)

        if node.key < self.min_node.key:
            self.min_node = node

    def merge(self, other: 'FibonacciHeap') -> 'FibonacciHeap':
        """Merge another Fibonacci heap into this one. O(1). Destroys other."""
        if not other or other.n == 0:
            return self
        self.min_node = self._merge_lists(self.min_node, other.min_node)
        if other.min_node and (self.min_node is None or other.min_node.key < self.min_node.key):
            self.min_node = other.min_node
        self.n += other.n
        # Invalidate the other heap
        other.min_node = None
        other.n = 0
        return self

    def delete(self, node: FibNode) -> None:
        """Delete an arbitrary node. O(log n) amortized."""
        self.decrease_key(node, float('-inf'))
        self.extract_min()

    # --- Internal helpers ----------------------------------------------------

    def _cut(self, child, parent):
        """Cut child from parent and add to root list."""
        # Remove child from parent's child list
        if child.next is child:
            parent.child = None
        else:
            if parent.child is child:
                parent.child = child.next
            self._remove_from_list(child)
        parent.degree -= 1
        child.parent = None
        child.mark = False
        # Add child to root list
        self.min_node = self._insert_into_list(self.min_node, child)

    def _cascading_cut(self, node):
        """
        If node's parent exists and node was already marked (lost a child before),
        cut it too. This cascading behavior is what gives O(1) amortized decrease-key.

        The intuition: a node can lose at most one child before being cut itself.
        This limits tree shapes and keeps maximum degree O(log n).
        """
        parent = node.parent
        if parent:
            if not node.mark:
                node.mark = True
            else:
                self._cut(node, parent)
                self._cascading_cut(parent)

    def _consolidate(self):
        """
        Merge trees of the same degree until no two roots share the same degree.

        Uses an array indexed by degree. When two trees of degree d collide,
        link the larger-root under the smaller-root, creating degree d+1.

        This is the "lazy" part — all the restructuring deferred from insert
        happens here during extract_min.
        """
        if self.min_node is None:
            return

        # Upper bound on max degree: floor(log_phi(n)) + 1
        max_degree = int(math.log(max(self.n, 1)) / math.log(1.618)) + 2
        degree_table = [None] * (max_degree + 1)

        # Collect all roots (must snapshot because we'll mutate the list)
        roots = list(self._iterate_list(self.min_node))

        for root in roots:
            root.parent = None
            d = root.degree
            while d < len(degree_table) and degree_table[d] is not None:
                other = degree_table[d]
                # Make the larger key a child of the smaller key
                if root.key > other.key:
                    root, other = other, root
                self._link(other, root)
                degree_table[d] = None
                d += 1
            # Grow table if needed
            while d >= len(degree_table):
                degree_table.append(None)
            degree_table[d] = root

        # Rebuild root list from degree table
        self.min_node = None
        for node in degree_table:
            if node is not None:
                node.prev = node
                node.next = node
                node.parent = None
                if self.min_node is None:
                    self.min_node = node
                else:
                    self.min_node = self._insert_into_list(self.min_node, node)
                    if node.key < self.min_node.key:
                        self.min_node = node

    def _link(self, child, parent):
        """Make child a child of parent."""
        # child should already be isolated or we isolate it
        child.prev = child
        child.next = child
        child.parent = parent
        child.mark = False
        parent.child = self._insert_into_list(parent.child, child)
        parent.degree += 1


# =============================================================================
# Demos
# =============================================================================

def demo_median_finder():
    """Show streaming median vs naive sort-each-time approach."""
    print("=" * 70)
    print("DEMO: Streaming Median — Two-Heap vs Naive Sort")
    print("=" * 70)

    # Correctness demo
    mf = MedianFinder()
    stream = [5, 15, 1, 3, 8, 7, 9, 2, 6, 10]
    print(f"\nStream: {stream}\n")
    print(f"{'Step':<6} {'Num':<6} {'Median':<10} {'All sorted'}")
    print("-" * 50)

    all_nums = []
    for i, num in enumerate(stream):
        mf.add_num(num)
        all_nums.append(num)
        s = sorted(all_nums)
        n = len(s)
        naive_median = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2
        heap_median = mf.find_median()
        assert heap_median == naive_median, f"Mismatch: {heap_median} != {naive_median}"
        print(f"{i+1:<6} {num:<6} {heap_median:<10.1f} {s}")

    print("\nAll medians match between two-heap and naive approaches.")

    # Performance comparison
    print(f"\n{'--- Performance Comparison ---':^70}")
    sizes = [1000, 5000, 10000]
    for size in sizes:
        data = [random.randint(1, 1_000_000) for _ in range(size)]

        # Two-heap approach
        start = time.perf_counter()
        mf = MedianFinder()
        for num in data:
            mf.add_num(num)
            mf.find_median()
        two_heap_time = time.perf_counter() - start

        # Naive sort approach
        start = time.perf_counter()
        running = []
        for num in data:
            running.append(num)
            running_sorted = sorted(running)
            n = len(running_sorted)
            _ = running_sorted[n // 2] if n % 2 == 1 else (running_sorted[n // 2 - 1] + running_sorted[n // 2]) / 2
        naive_time = time.perf_counter() - start

        speedup = naive_time / two_heap_time if two_heap_time > 0 else float('inf')
        print(f"  n={size:>6}: two-heap={two_heap_time:.4f}s  naive={naive_time:.4f}s  speedup={speedup:.1f}x")


def demo_fibonacci_heap():
    """Demonstrate Fibonacci heap operations."""
    print("\n" + "=" * 70)
    print("DEMO: Fibonacci Heap Operations")
    print("=" * 70)

    fh = FibonacciHeap()

    # Insert
    print("\n--- Insert 10 elements ---")
    nodes = []
    values = [7, 3, 12, 1, 9, 5, 15, 2, 8, 6]
    for v in values:
        node = fh.insert(v)
        nodes.append((v, node))
        print(f"  Inserted {v:>3}, min = {fh.find_min()}, size = {len(fh)}")

    # Extract min
    print("\n--- Extract min (triggers consolidation) ---")
    for _ in range(3):
        node = fh.extract_min()
        print(f"  Extracted {node.key}, new min = {fh.find_min() if fh else 'empty'}, size = {len(fh)}")

    # Decrease key
    print("\n--- Decrease key ---")
    # Find a node we haven't extracted (pick the one that was 15)
    target_val, target_node = nodes[6]  # value 15
    print(f"  Decreasing key of node with key={target_node.key} to 0")
    fh.decrease_key(target_node, 0)
    print(f"  New min = {fh.find_min()}, size = {len(fh)}")

    # Merge two heaps
    print("\n--- Merge two heaps ---")
    fh2 = FibonacciHeap()
    for v in [100, 200, -5]:
        fh2.insert(v)
    print(f"  Heap 1: min={fh.find_min()}, size={len(fh)}")
    print(f"  Heap 2: min={fh2.find_min()}, size={len(fh2)}")
    fh.merge(fh2)
    print(f"  Merged:  min={fh.find_min()}, size={len(fh)}")

    # Drain the heap
    print("\n--- Extract all in order ---")
    result = []
    while fh:
        node = fh.extract_min()
        result.append(node.key)
    print(f"  Extracted order: {result}")
    assert result == sorted(result), "ERROR: not in sorted order!"
    print("  Verified: elements extracted in sorted order.")

    # Larger-scale correctness test
    print("\n--- Correctness test: 1000 random inserts + extract all ---")
    fh = FibonacciHeap()
    data = [random.randint(-10000, 10000) for _ in range(1000)]
    for v in data:
        fh.insert(v)
    extracted = []
    while fh:
        extracted.append(fh.extract_min().key)
    assert extracted == sorted(data), "ERROR: Fibonacci heap sort failed!"
    print(f"  Inserted and extracted 1000 elements in correct sorted order.")

    # Decrease-key stress test
    print("\n--- Decrease-key stress test ---")
    fh = FibonacciHeap()
    node_list = []
    for i in range(100):
        node_list.append(fh.insert(i * 10))
    # Decrease many keys
    decreased = 0
    for node in node_list[50:]:
        new_key = node.key - 500
        fh.decrease_key(node, new_key)
        decreased += 1
    print(f"  Decreased {decreased} keys. Min is now {fh.find_min()}")
    extracted = []
    while fh:
        extracted.append(fh.extract_min().key)
    assert extracted == sorted(extracted), "ERROR: order violated after decrease-key!"
    print(f"  All {len(extracted)} elements extracted in sorted order after decrease-key.")


if __name__ == "__main__":
    random.seed(42)
    demo_median_finder()
    demo_fibonacci_heap()
    print("\n" + "=" * 70)
    print("All demos passed.")
    print("=" * 70)
