"""
Day 6: Singly Linked List — Full Implementation with Visualization

A singly linked list built from scratch with every operation explained.
This file demonstrates WHY linked lists exist by measuring the performance
trade-off against Python's built-in list (which is a dynamic array).

The key insight: linked lists trade random access speed for modification speed.
When you need frequent insertions/deletions at the head (or near it), a linked
list wins. When you need random access or iteration speed, an array wins.

Run: python linked_list.py
"""

import time
import sys
import random


# ---------------------------------------------------------------------------
# Node — the fundamental building block
# ---------------------------------------------------------------------------

class Node:
    """A single node in a singly linked list.

    Each node holds a piece of data and a reference to the next node.
    This is the simplest possible container: data + one pointer.

    In memory, each Node is a separate heap-allocated object. This is the
    source of both the linked list's flexibility (nodes can be anywhere)
    and its weakness (pointer chasing = cache misses).
    """

    __slots__ = ('data', 'next')  # save memory by avoiding __dict__

    def __init__(self, data):
        self.data = data
        self.next = None

    def __repr__(self):
        return f"Node({self.data!r})"


# ---------------------------------------------------------------------------
# Singly Linked List — the full implementation
# ---------------------------------------------------------------------------

class SinglyLinkedList:
    """A singly linked list with head pointer.

    WHY only a head pointer? Because a singly linked list is defined by the
    ability to traverse forward from the beginning. Adding a tail pointer is
    an optimization (it makes append O(1) instead of O(n)), but it adds
    complexity. We keep it minimal here to understand the fundamentals.

    Every operation falls into one of two categories:
    1. O(1) operations: anything at the head (insert, delete, peek)
    2. O(n) operations: anything that requires traversal (search, access by
       index, insert/delete at position, operations at the tail)
    """

    def __init__(self):
        self.head = None
        self._size = 0  # track size to avoid O(n) length computation

    # --- Core operations ---------------------------------------------------

    def insert_at_head(self, data):
        """Insert a new node at the beginning of the list.

        This is the linked list's superpower: O(1) insertion at the front.
        Compare to Python list's insert(0, x) which is O(n) because it
        shifts every existing element one position to the right.

        Two pointer assignments. No memory copying. No shifting.
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def delete_at_head(self):
        """Remove and return the first element.

        O(1). The old head becomes unreachable and will be garbage collected.
        In C, you would need to explicitly free() the old head node.
        """
        if self.head is None:
            raise IndexError("delete from empty list")
        data = self.head.data
        self.head = self.head.next
        self._size -= 1
        return data

    def insert_at_tail(self, data):
        """Insert at the end of the list.

        O(n) because we must traverse the entire list to find the last node.
        If we maintained a tail pointer, this would be O(1). That is a common
        optimization, but we omit it here to show the raw cost.
        """
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:
                current = current.next
            current.next = new_node
        self._size += 1

    def delete_at_tail(self):
        """Remove and return the last element.

        O(n) — we need the second-to-last node to update its next pointer.
        This is a fundamental limitation of singly linked lists. Doubly
        linked lists (Day 7) solve this with a backward pointer.
        """
        if self.head is None:
            raise IndexError("delete from empty list")
        if self.head.next is None:
            data = self.head.data
            self.head = None
            self._size -= 1
            return data
        current = self.head
        while current.next.next is not None:
            current = current.next
        data = current.next.data
        current.next = None
        self._size -= 1
        return data

    def insert_at_position(self, data, position):
        """Insert at a specific position (0-indexed).

        The traversal to position is O(k). The actual insertion (pointer
        reassignment) is O(1). Total: O(k) where k is the position.

        If you already have a reference to the node before the insertion
        point, the insertion itself is O(1). This is important for algorithms
        that maintain cursors into the list.
        """
        if position < 0 or position > self._size:
            raise IndexError(f"position {position} out of range [0, {self._size}]")
        if position == 0:
            return self.insert_at_head(data)
        current = self.head
        for _ in range(position - 1):
            current = current.next
        new_node = Node(data)
        new_node.next = current.next
        current.next = new_node
        self._size += 1

    def delete_at_position(self, position):
        """Delete the node at a specific position and return its data.

        Same pattern as insert_at_position: O(k) traversal + O(1) deletion.
        """
        if position < 0 or position >= self._size:
            raise IndexError(f"position {position} out of range [0, {self._size})")
        if position == 0:
            return self.delete_at_head()
        current = self.head
        for _ in range(position - 1):
            current = current.next
        data = current.next.data
        current.next = current.next.next
        self._size -= 1
        return data

    def search(self, data):
        """Return the position of the first node with the given data, or -1.

        O(n) — must potentially traverse the entire list. Same as array
        linear search, but without the cache-friendly sequential access.
        """
        current = self.head
        position = 0
        while current is not None:
            if current.data == data:
                return position
            current = current.next
            position += 1
        return -1

    def get(self, position):
        """Return the data at a specific position.

        O(k) — must traverse from the head. This is the fundamental weakness:
        arrays do this in O(1) with simple arithmetic (base + offset).
        """
        if position < 0 or position >= self._size:
            raise IndexError(f"position {position} out of range [0, {self._size})")
        current = self.head
        for _ in range(position):
            current = current.next
        return current.data

    def reverse(self):
        """Reverse the list in-place.

        The classic three-pointer technique: prev, current, next_node.
        Walk through the list, reversing each pointer as you go.

        This is O(n) time, O(1) space — no new nodes are created.
        It is one of the most common linked list interview questions.
        """
        prev = None
        current = self.head
        while current is not None:
            next_node = current.next   # save the next pointer
            current.next = prev        # reverse the link
            prev = current             # advance prev
            current = next_node        # advance current
        self.head = prev

    # --- Utility methods ---------------------------------------------------

    def __len__(self):
        return self._size

    def __repr__(self):
        """Visual representation of the list."""
        if self.head is None:
            return "Head -> None"
        parts = []
        current = self.head
        while current is not None:
            parts.append(str(current.data))
            current = current.next
        return "Head -> " + " -> ".join(parts) + " -> None"

    def to_list(self):
        """Convert to Python list for easy comparison."""
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def is_empty(self):
        return self.head is None


# ---------------------------------------------------------------------------
# Demonstration: Visual operations
# ---------------------------------------------------------------------------

def demo_operations():
    """Show each operation with a visual before/after."""
    print("=" * 70)
    print("  SINGLY LINKED LIST — OPERATION DEMONSTRATIONS")
    print("=" * 70)

    ll = SinglyLinkedList()
    print(f"\nEmpty list:        {ll}")
    print(f"Size: {len(ll)}")

    # Insert at head
    print("\n--- Insert at Head ---")
    for val in [30, 20, 10]:
        ll.insert_at_head(val)
        print(f"  insert_at_head({val}): {ll}")

    # Insert at tail
    print("\n--- Insert at Tail ---")
    for val in [40, 50]:
        ll.insert_at_tail(val)
        print(f"  insert_at_tail({val}): {ll}")

    # Insert at position
    print("\n--- Insert at Position ---")
    ll.insert_at_position(25, 2)
    print(f"  insert_at_position(25, 2): {ll}")
    ll.insert_at_position(5, 0)
    print(f"  insert_at_position(5, 0):  {ll}")

    # Search
    print("\n--- Search ---")
    for val in [25, 99]:
        pos = ll.search(val)
        print(f"  search({val}): position {pos}")

    # Get by index
    print("\n--- Access by Index ---")
    for i in [0, 3, len(ll) - 1]:
        print(f"  get({i}): {ll.get(i)}")

    # Delete at head
    print("\n--- Delete at Head ---")
    val = ll.delete_at_head()
    print(f"  delete_at_head() returned {val}: {ll}")

    # Delete at tail
    print("\n--- Delete at Tail ---")
    val = ll.delete_at_tail()
    print(f"  delete_at_tail() returned {val}: {ll}")

    # Delete at position
    print("\n--- Delete at Position ---")
    val = ll.delete_at_position(2)
    print(f"  delete_at_position(2) returned {val}: {ll}")

    # Reverse
    print("\n--- Reverse ---")
    print(f"  Before: {ll}")
    ll.reverse()
    print(f"  After:  {ll}")
    ll.reverse()  # reverse back
    print(f"  Back:   {ll}")

    print(f"\nFinal size: {len(ll)}")


# ---------------------------------------------------------------------------
# Performance comparison: Linked List vs Python list (dynamic array)
# ---------------------------------------------------------------------------

def benchmark_head_insertion():
    """Compare head insertion: linked list O(1) vs array O(n).

    This is where linked lists shine. Each Python list insert(0, x) shifts
    every existing element. The linked list just updates two pointers.
    """
    print("\n" + "=" * 70)
    print("  BENCHMARK: Head Insertion — Linked List vs Array")
    print("=" * 70)
    print("\n  Inserting N elements at position 0.")
    print("  Linked list: O(1) per insert -> O(N) total")
    print("  Array:       O(k) per insert (k = current size) -> O(N^2) total\n")

    sizes = [5000, 10000, 20000, 40000]
    print(f"  {'N':>8}  {'Linked List':>14}  {'Python list':>14}  {'Speedup':>10}")
    print(f"  {'-'*8}  {'-'*14}  {'-'*14}  {'-'*10}")

    for n in sizes:
        # Linked list
        ll = SinglyLinkedList()
        start = time.perf_counter()
        for i in range(n):
            ll.insert_at_head(i)
        t_ll = time.perf_counter() - start

        # Python list (dynamic array)
        arr = []
        start = time.perf_counter()
        for i in range(n):
            arr.insert(0, i)
        t_arr = time.perf_counter() - start

        speedup = t_arr / t_ll if t_ll > 0 else float('inf')
        print(f"  {n:>8}  {t_ll:>12.6f}s  {t_arr:>12.6f}s  {speedup:>8.1f}x")

    print("\n  Notice: array time grows quadratically (4x when N doubles),")
    print("  while linked list time grows linearly (2x when N doubles).")


def benchmark_random_access():
    """Compare random access: array O(1) vs linked list O(n).

    This is where arrays dominate. Array index is a single memory offset
    computation. Linked list must traverse from the head every time.
    """
    print("\n" + "=" * 70)
    print("  BENCHMARK: Random Access — Array vs Linked List")
    print("=" * 70)
    print("\n  Accessing 1000 random positions in a list of size N.\n")

    sizes = [1000, 2000, 4000, 8000]
    num_accesses = 1000

    print(f"  {'N':>8}  {'Array':>14}  {'Linked List':>14}  {'Slowdown':>10}")
    print(f"  {'-'*8}  {'-'*14}  {'-'*14}  {'-'*10}")

    for n in sizes:
        # Build both structures
        arr = list(range(n))
        ll = SinglyLinkedList()
        for i in range(n):
            ll.insert_at_head(i)

        # Random positions to access
        positions = [random.randint(0, n - 1) for _ in range(num_accesses)]

        # Array access
        start = time.perf_counter()
        for pos in positions:
            _ = arr[pos]
        t_arr = time.perf_counter() - start

        # Linked list access
        start = time.perf_counter()
        for pos in positions:
            _ = ll.get(pos)
        t_ll = time.perf_counter() - start

        slowdown = t_ll / t_arr if t_arr > 0 else float('inf')
        print(f"  {n:>8}  {t_arr:>12.6f}s  {t_ll:>12.6f}s  {slowdown:>8.1f}x")

    print("\n  Array access is constant time regardless of position.")
    print("  Linked list access grows linearly with position depth.")


# ---------------------------------------------------------------------------
# Memory layout demonstration
# ---------------------------------------------------------------------------

def demo_memory_layout():
    """Show that linked list nodes are scattered in memory.

    Python's id() returns the memory address of an object. For an array
    (Python list), elements are stored in a contiguous buffer of pointers.
    For a linked list, each node is a separate heap allocation.
    """
    print("\n" + "=" * 70)
    print("  MEMORY LAYOUT: Contiguous Array vs Scattered Linked List")
    print("=" * 70)

    # Array: contiguous pointer buffer
    arr = [1, 2, 3, 4, 5]
    print("\n  Python list internal pointer buffer:")
    addresses = [id(x) for x in arr]
    for i, (val, addr) in enumerate(zip(arr, addresses)):
        gap = f"  (gap: {addresses[i] - addresses[i-1]} bytes)" if i > 0 else ""
        print(f"    [{i}] value={val}  address=0x{addr:012x}{gap}")

    # Linked list: scattered nodes
    ll = SinglyLinkedList()
    for v in reversed([1, 2, 3, 4, 5]):
        ll.insert_at_head(v)

    print("\n  Linked list node addresses:")
    current = ll.head
    prev_addr = None
    i = 0
    while current is not None:
        addr = id(current)
        gap = f"  (gap: {addr - prev_addr} bytes)" if prev_addr is not None else ""
        print(f"    [{i}] value={current.data}  node_address=0x{addr:012x}{gap}")
        prev_addr = addr
        current = current.next
        i += 1

    print("\n  Note: small integers in CPython are cached (interned), so the")
    print("  value addresses may look similar. The NODE addresses show the")
    print("  scattered allocation pattern. Gaps between nodes are unpredictable")
    print("  — each node was independently allocated on the heap.")


# ---------------------------------------------------------------------------
# Iteration speed: cache effects
# ---------------------------------------------------------------------------

def benchmark_iteration():
    """Measure pure traversal speed to expose cache effects.

    Both array and linked list traversal are O(n), but the constant factors
    differ dramatically because of CPU cache behavior.
    """
    print("\n" + "=" * 70)
    print("  BENCHMARK: Iteration Speed (Cache Effects)")
    print("=" * 70)
    print("\n  Summing all elements. Both are O(n), but cache behavior differs.\n")

    n = 100000

    # Build structures
    arr = list(range(n))
    ll = SinglyLinkedList()
    for i in range(n):
        ll.insert_at_head(i)

    # Time array iteration
    times_arr = []
    for _ in range(5):
        start = time.perf_counter()
        total = sum(arr)
        times_arr.append(time.perf_counter() - start)

    # Time linked list iteration
    times_ll = []
    for _ in range(5):
        start = time.perf_counter()
        current = ll.head
        total = 0
        while current is not None:
            total += current.data
            current = current.next
        times_ll.append(time.perf_counter() - start)

    t_arr = sorted(times_arr)[2]  # median
    t_ll = sorted(times_ll)[2]

    print(f"  N = {n:,}")
    print(f"  Array iteration:       {t_arr:.6f}s")
    print(f"  Linked list iteration: {t_ll:.6f}s")
    print(f"  Linked list is {t_ll/t_arr:.1f}x slower")
    print()
    print("  Same Big-O, different real-world performance.")
    print("  This is the cache miss penalty: each node->next dereference")
    print("  potentially fetches a new 64-byte cache line from main memory.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Day 6: Singly Linked List — Implementation & Analysis")
    print("=" * 70)
    print()
    print("A linked list stores elements in scattered heap nodes connected")
    print("by pointers. It trades O(1) random access for O(1) head insertion.")
    print("Today we build one from scratch and measure the trade-offs.\n")

    demo_operations()
    benchmark_head_insertion()
    benchmark_random_access()
    demo_memory_layout()
    benchmark_iteration()

    print("\n" + "=" * 70)
    print("  KEY TAKEAWAYS")
    print("=" * 70)
    print("""
  1. Linked lists excel at head insertion/deletion: O(1) vs array's O(n).
  2. Arrays excel at random access: O(1) vs linked list's O(n).
  3. Arrays excel at iteration despite same Big-O, due to cache locality.
  4. Linked lists use more memory: each node carries a pointer overhead.
  5. Choose based on ACCESS PATTERN: if you mostly add/remove at the
     front and iterate sequentially, linked list wins. If you need
     random access by index, use an array.
  6. Big-O hides constant factors. A "slower" O(n) array traversal
     beats a "faster" O(n) linked list traversal because of hardware.
""")
