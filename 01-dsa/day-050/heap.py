"""
Day 50: Binary Heap — Array-Based Priority Queue
=================================================
A complete binary tree stored in a flat array. No pointers, no allocations,
no cache misses — just arithmetic on indices.

    parent(i) = (i - 1) // 2
    left(i)   = 2 * i + 1
    right(i)  = 2 * i + 2

The heap property (min-heap): every node <= its children.
The root is always the minimum.

Why arrays beat pointers for heaps:
    - Cache locality: sequential memory access patterns
    - Zero pointer overhead: 2 words saved per node
    - Implicit structure: shape determined entirely by size
    - Fewer allocations: one realloc vs n mallocs

Run: python heap.py
"""


# ─── MinHeap ────────────────────────────────────────────────────────

class MinHeap:
    """
    Min-heap: smallest element always at index 0.

    The array stores a complete binary tree level-by-level:
        [root, left_child, right_child, left_left, left_right, ...]
    """

    def __init__(self):
        self._data = []

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return len(self._data) > 0

    def __repr__(self):
        return f"MinHeap({self._data})"

    def peek(self):
        """Return minimum element without removing it. O(1)."""
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def push(self, value):
        """
        Insert value into the heap. O(log n).

        Strategy: append to end (maintains completeness), then sift up
        to restore the heap property.
        """
        self._data.append(value)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        """
        Remove and return the minimum element. O(log n).

        Strategy: swap root with last element, remove last, then sift
        down the new root to restore the heap property.

        Why swap instead of just removing the root?
        Removing from the middle of an array is O(n) (shift everything).
        Removing from the end is O(1). So we swap to make the removal cheap,
        then fix the single violation at the root.
        """
        if not self._data:
            raise IndexError("pop from empty heap")
        # Swap root with last element
        self._swap(0, len(self._data) - 1)
        minimum = self._data.pop()  # O(1) removal from end
        if self._data:
            self._sift_down(0)
        return minimum

    def pushpop(self, value):
        """
        Push value, then pop and return the minimum. More efficient than
        push() followed by pop() because we avoid one sift operation.

        If value <= current min, just return value (it would be popped immediately).
        Otherwise, replace root with value and sift down.
        """
        if self._data and self._data[0] < value:
            value, self._data[0] = self._data[0], value
            self._sift_down(0)
        return value

    def replace(self, value):
        """
        Pop the minimum, then push value. More efficient than pop() + push().
        Replaces root directly and sifts down once.
        """
        if not self._data:
            raise IndexError("replace on empty heap")
        minimum = self._data[0]
        self._data[0] = value
        self._sift_down(0)
        return minimum

    @classmethod
    def heapify(cls, iterable):
        """
        Build a heap from an iterable in O(n) time.

        Floyd's algorithm: start from the last non-leaf and sift down each node.
        Why O(n) and not O(n log n)?

        Nodes at depth d have at most (h - d) levels to sift down:
            Level h   (n/2 nodes): sift 0 levels  → 0 work
            Level h-1 (n/4 nodes): sift 1 level   → n/4 work
            Level h-2 (n/8 nodes): sift 2 levels  → 2n/8 work
            ...
            Level 0   (1 node):    sift h levels   → h work

        Total = n * Σ(k/2^k) for k=0..∞ = n * 2 = O(n)
        """
        heap = cls()
        heap._data = list(iterable)
        # Start from last non-leaf: parent of last element
        for i in range(len(heap._data) // 2 - 1, -1, -1):
            heap._sift_down(i)
        return heap

    def _sift_up(self, i):
        """
        Move element at index i upward until heap property is restored.

        Compare with parent; if smaller, swap and continue.
        Stops when we reach the root (i == 0) or parent is smaller.
        """
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        """
        Move element at index i downward until heap property is restored.

        Compare with both children; swap with the SMALLER child (to maintain
        min-heap property for the other child too). Continue until we reach
        a leaf or both children are larger.
        """
        n = len(self._data)
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def to_list(self):
        """Return a copy of the internal array (for testing/debugging)."""
        return list(self._data)


# ─── MaxHeap ────────────────────────────────────────────────────────

class MaxHeap:
    """
    Max-heap: largest element always at index 0.

    Implementation: store negated values in a MinHeap.
    This is the standard trick — Python's heapq does the same.

    Alternative: duplicate all the comparison logic with reversed signs.
    The negation trick is simpler and less error-prone.
    """

    def __init__(self):
        self._heap = MinHeap()

    def __len__(self):
        return len(self._heap)

    def __bool__(self):
        return bool(self._heap)

    def peek(self):
        return -self._heap.peek()

    def push(self, value):
        self._heap.push(-value)

    def pop(self):
        return -self._heap.pop()

    @classmethod
    def heapify(cls, iterable):
        maxheap = cls()
        maxheap._heap = MinHeap.heapify(-x for x in iterable)
        return maxheap


# ─── Heapsort ───────────────────────────────────────────────────────

def heapsort(arr):
    """
    Sort array using heap operations. O(n log n), in-place, NOT stable.

    Strategy:
    1. Build max-heap in O(n)
    2. Repeatedly swap root (max) with last unsorted element,
       shrink heap by 1, sift down the new root

    Why max-heap for ascending sort?
    After each extraction, the max goes to the END of the array.
    So the sorted portion grows from right to left.

    Why heapsort is rarely used in practice:
    - Not stable (equal elements may be reordered)
    - Poor cache behavior (sift-down jumps around the array)
    - Quicksort is faster in practice due to better cache locality

    But heapsort guarantees O(n log n) worst case — quicksort doesn't.
    This matters in real-time systems where worst-case latency matters.
    """
    n = len(arr)

    # Phase 1: Build max-heap in O(n)
    for i in range(n // 2 - 1, -1, -1):
        _heapsort_sift_down(arr, n, i)

    # Phase 2: Extract max repeatedly
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]  # Move max to sorted region
        _heapsort_sift_down(arr, end, 0)      # Restore heap in unsorted region


def _heapsort_sift_down(arr, size, i):
    """Sift down for max-heap within arr[0:size]."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < size and arr[left] > arr[largest]:
            largest = left
        if right < size and arr[right] > arr[largest]:
            largest = right
        if largest == i:
            break
        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest


# ─── Visualization ──────────────────────────────────────────────────

def visualize_heap(data, label="Heap"):
    """
    Print a binary heap as a tree. Shows the array-tree duality.
    """
    if not data:
        print(f"{label}: (empty)")
        return

    print(f"\n{label} array: {data}")
    print(f"{label} tree:")

    n = len(data)
    height = 0
    while (1 << height) - 1 < n:
        height += 1

    idx = 0
    for level in range(height):
        count = min(1 << level, n - idx)
        spacing = " " * (2 ** (height - level) - 1)
        gap = " " * (2 ** (height - level + 1) - 1)

        values = []
        for j in range(count):
            values.append(str(data[idx + j]).center(3))

        print(spacing + gap.join(values))
        idx += count


# ─── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 50: Binary Heap — Array-Based Priority Queue")
    print("=" * 60)

    # Build heap by insertion
    print("\n--- Building MinHeap by sequential insertion ---")
    h = MinHeap()
    for val in [7, 3, 9, 1, 5, 2, 8]:
        h.push(val)
        print(f"  push({val}) → {h.to_list()}")

    visualize_heap(h.to_list(), "MinHeap")

    # Extract all in order
    print("\n--- Extracting all elements (should be sorted) ---")
    result = []
    while h:
        result.append(h.pop())
    print(f"  Extracted: {result}")
    assert result == sorted(result), "Not sorted!"

    # Build heap using heapify (O(n))
    print("\n--- Heapify: build from array in O(n) ---")
    data = [7, 3, 9, 1, 5, 2, 8, 4, 6]
    h = MinHeap.heapify(data)
    visualize_heap(h.to_list(), "Heapified")

    # MaxHeap
    print("\n--- MaxHeap (via negation trick) ---")
    mh = MaxHeap.heapify([7, 3, 9, 1, 5, 2, 8])
    print(f"  Max: {mh.peek()}")
    result = []
    while mh:
        result.append(mh.pop())
    print(f"  Extracted: {result}")
    assert result == sorted(result, reverse=True), "Not reverse sorted!"

    # Heapsort
    print("\n--- Heapsort (in-place, O(n log n) worst case) ---")
    arr = [38, 27, 43, 3, 9, 82, 10]
    print(f"  Before: {arr}")
    heapsort(arr)
    print(f"  After:  {arr}")
    assert arr == sorted(arr)

    # pushpop optimization
    print("\n--- pushpop: combined push+pop (one sift instead of two) ---")
    h = MinHeap.heapify([2, 5, 8, 10])
    print(f"  Heap: {h.to_list()}")
    result = h.pushpop(1)
    print(f"  pushpop(1) → returned {result}, heap now {h.to_list()}")
    result = h.pushpop(7)
    print(f"  pushpop(7) → returned {result}, heap now {h.to_list()}")

    print("\n✓ All demos passed")
