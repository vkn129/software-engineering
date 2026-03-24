"""
Day 16: Dynamic Arrays — Growth Strategies, Amortized O(1) Append

This script builds a dynamic array from scratch, then proves through measurement:
- Why multiplicative growth gives amortized O(1) but additive growth gives O(n)
- How CPython's list actually grows (and why it's not simple doubling)
- Array vs linked list: which wins and by how much
- Memory waste: the hidden cost of over-allocation

Every claim in the README gets an empirical test.

Run: python dynamic_array.py

Prerequisites: Day 15 (memory layout, contiguous storage, cache lines)
"""

import time
import sys


# ===========================================================================
# SECTION 1: Dynamic Array — Built From Scratch
# ===========================================================================

class DynamicArray:
    """A resizable array built on a fixed-size Python list.

    Why we use a raw list of None values instead of Python's built-in append:
    We are simulating what happens at the C level. A real dynamic array is
    backed by a malloc'd block of memory. We approximate that with a
    pre-allocated list of None slots. This lets us control and observe the
    resize behavior ourselves.

    Growth strategy is configurable: doubling, 1.5x, or additive.
    """

    def __init__(self, growth_strategy="double"):
        # The backing store: a fixed-size list simulating malloc'd memory
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity

        # Track resize events for analysis
        self._resize_count = 0
        self._total_copies = 0

        # Growth strategy determines how fast capacity increases
        self._growth_strategy = growth_strategy

    def _resize(self, new_capacity):
        """Allocate new backing array and copy all elements.

        This is the expensive operation. Every element must be copied because
        the new memory block is at a different address — you cannot extend
        contiguous memory in place (the bytes after it might belong to
        another allocation).
        """
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]

        self._total_copies += self._size
        self._resize_count += 1
        self._data = new_data
        self._capacity = new_capacity

    def _next_capacity(self):
        """Compute new capacity based on growth strategy.

        The choice here determines the amortized cost:
        - "double": new = 2 * old → amortized O(1), ~50% memory waste
        - "multiply_1_5": new = 1.5 * old → amortized O(1), ~33% waste
        - "additive_10": new = old + 10 → amortized O(n), ~constant waste
        - "additive_1": new = old + 1 → amortized O(n), zero waste
        - "cpython": mimics CPython's actual formula
        """
        if self._growth_strategy == "double":
            return self._capacity * 2
        elif self._growth_strategy == "multiply_1_5":
            return max(self._capacity + 1, int(self._capacity * 1.5))
        elif self._growth_strategy == "additive_10":
            return self._capacity + 10
        elif self._growth_strategy == "additive_1":
            return self._capacity + 1
        elif self._growth_strategy == "cpython":
            # Mirrors Objects/listobject.c: newsize + (newsize >> 3) + (3 if newsize < 9 else 6)
            newsize = self._size + 1
            return newsize + (newsize >> 3) + (3 if newsize < 9 else 6)
        else:
            return self._capacity * 2

    def append(self, value):
        """Add element to end. Amortized O(1) for multiplicative growth.

        When size == capacity, the array is full. We must resize before
        inserting. The resize is O(n), but it happens so rarely (for
        multiplicative growth) that the cost spreads across all appends.
        """
        if self._size == self._capacity:
            self._resize(self._next_capacity())
        self._data[self._size] = value
        self._size += 1

    def insert(self, index, value):
        """Insert at arbitrary position. O(n) always — must shift elements.

        Even with a dynamic array, inserting in the middle requires moving
        every element after the insertion point one slot to the right.
        This is the fundamental limitation of contiguous storage.
        """
        if index < 0 or index > self._size:
            raise IndexError(f"Index {index} out of range [0, {self._size}]")
        if self._size == self._capacity:
            self._resize(self._next_capacity())
        # Shift elements right, starting from the end to avoid overwrites
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def delete(self, index):
        """Remove element at index. O(n) — must shift elements left.

        Same problem as insert: maintaining contiguity requires moving
        elements. This is why linked lists exist — they can delete in O(1)
        if you have a pointer to the node.
        """
        if index < 0 or index >= self._size:
            raise IndexError(f"Index {index} out of range [0, {self._size})")
        # Shift elements left
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._size - 1] = None  # Help garbage collector
        self._size -= 1

        # Shrink if utilization drops below 25% (and capacity > initial)
        # Shrink to 50% capacity — NOT to 25%, to avoid thrashing
        if self._capacity > 4 and self._size < self._capacity // 4:
            self._resize(max(4, self._capacity // 2))

    def get(self, index):
        """O(1) random access — the whole point of contiguous storage.

        address = base + index * element_size. One multiply, one add.
        Does not depend on array size.
        """
        if index < 0 or index >= self._size:
            raise IndexError(f"Index {index} out of range [0, {self._size})")
        return self._data[index]

    def __len__(self):
        return self._size

    def __repr__(self):
        elements = [str(self._data[i]) for i in range(self._size)]
        return f"DynamicArray([{', '.join(elements)}], size={self._size}, cap={self._capacity})"

    @property
    def stats(self):
        """Return resize statistics for analysis."""
        waste = (self._capacity - self._size) / self._capacity if self._capacity > 0 else 0
        return {
            "size": self._size,
            "capacity": self._capacity,
            "resizes": self._resize_count,
            "total_copies": self._total_copies,
            "memory_waste": f"{waste:.1%}",
        }


# ===========================================================================
# SECTION 2: Linked List — For Comparison
# ===========================================================================

class _Node:
    """A linked list node. Each node is a separate heap allocation.

    In contrast to array elements which sit contiguously in memory,
    nodes are scattered across the heap. Accessing the next node
    requires following a pointer — a likely cache miss.
    """
    __slots__ = ('data', 'next')

    def __init__(self, data):
        self.data = data
        self.next = None


class SimpleLinkedList:
    """Singly linked list for benchmarking against dynamic array."""

    def __init__(self):
        self.head = None
        self._tail = None  # Track tail for O(1) append
        self._size = 0

    def append(self, value):
        """O(1) append — no resize ever needed."""
        node = _Node(value)
        if self._tail is None:
            self.head = node
            self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def iterate(self):
        """O(n) traversal — but with cache misses on every step."""
        current = self.head
        total = 0
        while current:
            total += current.data
            current = current.next
        return total


# ===========================================================================
# DEMONSTRATION 1: Growth Strategies Head-to-Head
# ===========================================================================

def demo_growth_strategies():
    """Compare different growth strategies on the same workload.

    This is the core experiment. Additive growth should show O(n^2) total
    time for n appends; multiplicative growth should show O(n).
    """
    print(f"\n{'=' * 70}")
    print("  DEMO 1: Growth Strategies — Additive vs Multiplicative")
    print(f"{'=' * 70}\n")

    strategies = [
        ("double (2x)", "double"),
        ("multiply (1.5x)", "multiply_1_5"),
        ("CPython formula", "cpython"),
        ("additive (+10)", "additive_10"),
    ]

    n = 100_000

    print(f"  Appending {n:,} elements with different growth strategies:\n")
    print(f"  {'Strategy':<22} {'Time (ms)':>10} {'Resizes':>8} {'Total Copies':>14} {'Waste':>8}")
    print(f"  {'-'*22} {'-'*10} {'-'*8} {'-'*14} {'-'*8}")

    for name, strategy in strategies:
        arr = DynamicArray(growth_strategy=strategy)
        start = time.perf_counter()
        for i in range(n):
            arr.append(i)
        elapsed = time.perf_counter() - start
        stats = arr.stats
        print(f"  {name:<22} {elapsed*1000:>10.1f} {stats['resizes']:>8} "
              f"{stats['total_copies']:>14,} {stats['memory_waste']:>8}")

    # Show additive_1 separately with smaller n (it's VERY slow)
    n_small = 10_000
    arr = DynamicArray(growth_strategy="additive_1")
    start = time.perf_counter()
    for i in range(n_small):
        arr.append(i)
    elapsed = time.perf_counter() - start
    stats = arr.stats

    print()
    print(f"  additive (+1) [{n_small:,} only] {elapsed*1000:>5.1f}ms, "
          f"{stats['resizes']} resizes, {stats['total_copies']:,} total copies")
    print(f"  ^ This is O(n^2). Extrapolating to {n:,}: "
          f"~{elapsed * (n/n_small)**2 * 1000:.0f}ms")

    print()
    print("  KEY INSIGHT: Multiplicative strategies (2x, 1.5x, CPython) are")
    print("  all fast — total copies ≈ O(n). Additive (+1) is catastrophic —")
    print("  total copies ≈ n^2/2 because EVERY append triggers a full copy.")


# ===========================================================================
# DEMONSTRATION 2: CPython's Internal Growth Pattern
# ===========================================================================

def demo_cpython_growth():
    """Reveal how Python's list actually grows by tracking sys.getsizeof().

    CPython's list overallocates using the formula:
        new = size + (size >> 3) + (3 if size < 9 else 6)
    We can observe this by watching memory jumps as we append.
    """
    print(f"\n{'=' * 70}")
    print("  DEMO 2: CPython's Internal Growth Pattern")
    print(f"{'=' * 70}\n")

    print("  Tracking sys.getsizeof() as we append to a real Python list:")
    print(f"  {'Size':>8} {'Bytes':>8} {'Capacity*':>10} {'Growth':>8} {'Factor':>8}")
    print(f"  {'-'*8} {'-'*8} {'-'*10} {'-'*8} {'-'*8}")

    lst = []
    prev_bytes = sys.getsizeof(lst)
    prev_capacity = 0

    # Python list: each element is an 8-byte pointer (on 64-bit)
    # The base overhead (empty list) is the header
    base_overhead = sys.getsizeof([])
    pointer_size = 8  # bytes per pointer on 64-bit

    resize_capacities = []

    for i in range(200):
        lst.append(i)
        current_bytes = sys.getsizeof(lst)
        if current_bytes != prev_bytes:
            capacity = (current_bytes - base_overhead) // pointer_size
            growth = capacity - prev_capacity
            factor = f"{capacity / prev_capacity:.2f}x" if prev_capacity > 0 else "—"
            if len(resize_capacities) < 20:  # Show first 20 resizes
                print(f"  {i+1:>8} {current_bytes:>8} {capacity:>10} "
                      f"{'+' + str(growth):>8} {factor:>8}")
            resize_capacities.append(capacity)
            prev_capacity = capacity
            prev_bytes = current_bytes

    print(f"  ... ({len(resize_capacities)} total resizes for 200 appends)")
    print()
    print("  The growth factor starts high (4x for tiny lists) and converges")
    print("  toward ~1.125x for large lists. This is intentional:")
    print("    - Small lists: resize often → be aggressive to avoid it")
    print("    - Large lists: each resize copies megabytes → be conservative")

    # Show the formula
    print()
    print("  CPython source (Objects/listobject.c):")
    print("    new_allocated = newsize + (newsize >> 3) + (newsize < 9 ? 3 : 6)")
    print()
    print("  For size 1000: new = 1000 + 125 + 6 = 1131 (growth factor ≈ 1.13)")
    print("  For size 1M:   new = 1M + 125K + 6 = 1.125M  (growth factor ≈ 1.125)")


# ===========================================================================
# DEMONSTRATION 3: Array vs Linked List — Append and Iterate
# ===========================================================================

def demo_array_vs_linked_list():
    """Head-to-head comparison: dynamic array vs linked list.

    Theory predicts:
    - Append: both O(1), but array has occasional O(n) resizes
    - Iteration: array wins massively due to cache locality
    - Memory: linked list uses more (node overhead + pointer per element)
    """
    print(f"\n{'=' * 70}")
    print("  DEMO 3: Dynamic Array vs Linked List — Append and Iterate")
    print(f"{'=' * 70}\n")

    n = 200_000

    # --- Append benchmark ---
    print(f"  Appending {n:,} elements:")

    # Python list (dynamic array)
    start = time.perf_counter()
    py_list = []
    for i in range(n):
        py_list.append(i)
    list_append_time = time.perf_counter() - start

    # Linked list
    start = time.perf_counter()
    ll = SimpleLinkedList()
    for i in range(n):
        ll.append(i)
    ll_append_time = time.perf_counter() - start

    print(f"    Python list append: {list_append_time*1000:.1f} ms")
    print(f"    Linked list append: {ll_append_time*1000:.1f} ms")
    print(f"    Ratio (LL / list):  {ll_append_time/list_append_time:.1f}x")
    print()
    print("    Linked list is slower despite never resizing, because each append")
    print("    allocates a new Node object on the heap. malloc() is expensive.")

    # --- Iteration benchmark ---
    print(f"\n  Iterating all {n:,} elements (summing values):")

    # Python list iteration
    start = time.perf_counter()
    total = 0
    for i in range(len(py_list)):
        total += py_list[i]
    list_iter_time = time.perf_counter() - start

    # Linked list iteration
    start = time.perf_counter()
    total = ll.iterate()
    ll_iter_time = time.perf_counter() - start

    print(f"    Python list iterate: {list_iter_time*1000:.1f} ms")
    print(f"    Linked list iterate: {ll_iter_time*1000:.1f} ms")
    print(f"    Ratio (LL / list):   {ll_iter_time/list_iter_time:.1f}x")
    print()
    print("    Array iteration is faster because elements are contiguous in memory.")
    print("    Each access loads ~8 adjacent pointers into the cache line (64 bytes).")
    print("    Linked list nodes are scattered — every ->next is a potential cache miss.")

    # --- Memory comparison ---
    print(f"\n  Memory usage for {n:,} elements:")
    list_mem = sys.getsizeof(py_list)  # Just the list object + pointer array
    # Linked list: each Node has data + next pointer + Python object overhead
    node_size = sys.getsizeof(_Node(0))
    ll_mem = n * node_size  # approximate
    print(f"    Python list (pointers only): {list_mem:>10,} bytes ({list_mem/1024:.0f} KB)")
    print(f"    Linked list (nodes only):    {ll_mem:>10,} bytes ({ll_mem/1024:.0f} KB)")
    print(f"    LL / list memory ratio:      {ll_mem/list_mem:.1f}x")
    print()
    print("    Linked list uses ~3-5x more memory per element because each node")
    print("    carries Python object overhead (refcount, type pointer) plus the")
    print("    next pointer. Arrays store only the data pointers, contiguously.")


# ===========================================================================
# DEMONSTRATION 4: Memory Waste Analysis
# ===========================================================================

def demo_memory_waste():
    """Show how much memory each growth strategy wastes at each point.

    Waste = (capacity - size) / capacity. A doubling strategy can waste up
    to 50% right after a resize (half the array is empty). CPython's
    conservative growth wastes much less.
    """
    print(f"\n{'=' * 70}")
    print("  DEMO 4: Memory Waste Over Time")
    print(f"{'=' * 70}\n")

    strategies = [
        ("double (2x)", "double"),
        ("multiply (1.5x)", "multiply_1_5"),
        ("CPython formula", "cpython"),
    ]

    n = 1000

    print(f"  Peak and average memory waste over {n:,} appends:\n")
    print(f"  {'Strategy':<22} {'Peak Waste':>12} {'Avg Waste':>12} {'Final Cap':>10}")
    print(f"  {'-'*22} {'-'*12} {'-'*12} {'-'*10}")

    for name, strategy in strategies:
        arr = DynamicArray(growth_strategy=strategy)
        wastes = []
        for i in range(n):
            arr.append(i)
            waste = (arr._capacity - arr._size) / arr._capacity
            wastes.append(waste)

        peak = max(wastes)
        avg = sum(wastes) / len(wastes)
        print(f"  {name:<22} {peak:>11.1%} {avg:>11.1%} {arr._capacity:>10,}")

    print()
    print("  Doubling wastes up to 50% — right after a resize, half the array")
    print("  is empty. CPython's ~12.5% growth keeps waste much lower.")
    print()
    print("  But waste is not always bad: more spare capacity = fewer resizes")
    print("  = fewer O(n) copies = faster average append. It is a trade-off.")


# ===========================================================================
# DEMONSTRATION 5: Amortized Cost — Visualized
# ===========================================================================

def demo_amortized_cost():
    """Show the cost of each individual append to visualize amortization.

    Most appends cost O(1). Occasionally one costs O(n) when resize triggers.
    The expensive ones are exponentially rare with multiplicative growth,
    which is exactly why the amortized cost is O(1).
    """
    print(f"\n{'=' * 70}")
    print("  DEMO 5: Per-Append Cost — Seeing Amortization")
    print(f"{'=' * 70}\n")

    # Track copies per append for doubling strategy
    arr = DynamicArray(growth_strategy="double")
    costs = []  # (index, copies_this_append)
    prev_copies = 0

    n = 1024
    for i in range(n):
        arr.append(i)
        copies_this_step = arr._total_copies - prev_copies
        if copies_this_step > 0:
            costs.append((i, copies_this_step))
        prev_copies = arr._total_copies

    print("  Doubling strategy — operations that trigger resize:")
    print(f"  {'Append #':>10} {'Elements Copied':>16} {'Capacity After':>16}")
    print(f"  {'-'*10} {'-'*16} {'-'*16}")

    for idx, copies in costs:
        # Reconstruct capacity: it doubles each time
        print(f"  {idx:>10} {copies:>16} {copies * 2:>16}")

    print()
    print(f"  Total appends: {n}")
    print(f"  Total copies:  {arr._total_copies}")
    print(f"  Amortized copies per append: {arr._total_copies / n:.2f}")
    print()
    print(f"  With doubling, resizes happen at powers of 2.")
    print(f"  Copies: 1 + 2 + 4 + 8 + ... + {n} = {2*n - 1} (geometric series)")
    print(f"  That is < 2n copies for n appends → amortized O(1).")


# ===========================================================================
# DEMONSTRATION 6: Shrinking and Thrashing
# ===========================================================================

def demo_shrinking():
    """Show what happens when a dynamic array shrinks, and the thrashing problem.

    If grow threshold = 100% and shrink threshold = 50%, alternating
    append/delete at the boundary causes a resize on every operation.
    Our implementation uses 25% shrink threshold to prevent this.
    """
    print(f"\n{'=' * 70}")
    print("  DEMO 6: Shrinking and the Thrashing Problem")
    print(f"{'=' * 70}\n")

    # Build up, then tear down
    arr = DynamicArray(growth_strategy="double")
    n = 1000
    for i in range(n):
        arr.append(i)

    print(f"  After {n} appends: size={arr._size}, capacity={arr._capacity}, "
          f"resizes={arr._resize_count}")

    resizes_before = arr._resize_count
    for i in range(n - 1):
        arr.delete(arr._size - 1)

    print(f"  After {n-1} deletes: size={arr._size}, capacity={arr._capacity}, "
          f"resizes={arr._resize_count}")
    print(f"  Shrink resizes: {arr._resize_count - resizes_before}")
    print()

    # Demonstrate thrashing protection
    print("  Thrashing test: append/delete at the resize boundary")
    arr2 = DynamicArray(growth_strategy="double")
    for i in range(100):
        arr2.append(i)

    resizes_before = arr2._resize_count
    # Rapidly add and remove near the capacity boundary
    for _ in range(1000):
        arr2.append(999)
        arr2.delete(arr2._size - 1)

    print(f"  1000 append/delete cycles at boundary: "
          f"{arr2._resize_count - resizes_before} resizes")
    print()
    print("  Because we grow at 100% and shrink at 25%, there is a buffer zone.")
    print("  The array does not thrash. If we shrank at 50%, every cycle would resize.")


# ===========================================================================
# DEMONSTRATION 7: Scaling Test — Proving O(n) Total vs O(n^2)
# ===========================================================================

def demo_scaling():
    """Double the input size and measure: O(n) should ~double, O(n^2) should ~4x."""
    print(f"\n{'=' * 70}")
    print("  DEMO 7: Scaling Test — Proving O(n) vs O(n^2)")
    print(f"{'=' * 70}\n")

    sizes = [25_000, 50_000, 100_000, 200_000]

    for strategy_name, strategy in [("double (2x)", "double"), ("additive (+10)", "additive_10")]:
        print(f"  {strategy_name}:")
        print(f"  {'n':>10} {'Time (ms)':>12} {'Ratio':>8}")
        print(f"  {'-'*10} {'-'*12} {'-'*8}")

        prev_time = None
        for n in sizes:
            arr = DynamicArray(growth_strategy=strategy)
            start = time.perf_counter()
            for i in range(n):
                arr.append(i)
            elapsed = time.perf_counter() - start
            ratio = f"{elapsed/prev_time:.2f}x" if prev_time else "—"
            print(f"  {n:>10} {elapsed*1000:>12.1f} {ratio:>8}")
            prev_time = elapsed
        print()

    print("  Doubling: ratio ≈ 2x when n doubles → O(n) total → O(1) amortized")
    print("  Additive: ratio ≈ 4x when n doubles → O(n^2) total → O(n) amortized")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  Day 16: Dynamic Arrays — Growth Strategies and Amortized Analysis")
    print("=" * 70)
    print()
    print("  A dynamic array is a fixed array that pretends to be resizable.")
    print("  The trick: over-allocate, and when full, allocate bigger + copy.")
    print("  The question: HOW MUCH bigger? The answer changes everything.")

    demo_growth_strategies()
    demo_cpython_growth()
    demo_array_vs_linked_list()
    demo_memory_waste()
    demo_amortized_cost()
    demo_shrinking()
    demo_scaling()

    print(f"\n{'=' * 70}")
    print("  KEY TAKEAWAYS:")
    print("  1. Multiplicative growth → amortized O(1) append (geometric series)")
    print("  2. Additive growth → O(n) per append (arithmetic series, quadratic total)")
    print("  3. CPython uses ~1.125x growth: less waste than 2x, still amortized O(1)")
    print("  4. Dynamic arrays beat linked lists for append AND iteration")
    print("  5. Shrinking needs hysteresis (25%/100%) to avoid thrashing")
    print("  6. Memory waste is the price of amortized O(1) — it is worth paying")
    print("=" * 70)
