"""
Day 32: Deque Implementations -- Circular Buffer ArrayDeque + Sliding Window Algorithms
========================================================================================

Core implementation: ArrayDeque using a circular buffer with automatic resizing.
Also includes sliding_window_maximum and sliding_window_minimum, both O(n).

We benchmark against Python's collections.deque to see how the C implementation
compares to our pure-Python circular buffer.

Run: python deque_impl.py
"""

import time
import collections
import random


# ---------------------------------------------------------------------------
# ArrayDeque: Circular Buffer Implementation
# ---------------------------------------------------------------------------
# Why a circular buffer? Because arrays are stored contiguously in memory.
# The CPU's cache loads entire cache lines (64 bytes), so sequential array
# access is fast. A linked list scatters nodes across the heap, causing
# cache misses on every traversal.
#
# The circular buffer avoids shifting elements on push_front/pop_front by
# using modular arithmetic to wrap indices around the array. The trade-off
# is occasional O(n) resize when the buffer fills up, but this is amortized
# O(1) because we double the capacity each time.

class ArrayDeque:
    """Double-ended queue backed by a circular buffer (dynamic array).

    All operations are O(1) amortized. Random access is O(1) -- an advantage
    over linked-list-based deques. Resize doubles capacity, so the total cost
    of n insertions is O(n), giving O(1) amortized per insertion.

    Memory layout:
        Physical: [_, _, C, D, E, _, _, A, B]
                          ^front=2         ^wraps: indices 7,8 -> 7,0
        Logical:  [A, B, C, D, E]
    """

    def __init__(self, initial_capacity=8):
        # Why power of 2? Because (index % capacity) can be replaced with
        # (index & (capacity - 1)) -- a single bitwise AND instead of an
        # expensive modulo. We don't do this optimization here for clarity,
        # but CPython's deque and C implementations do.
        self._capacity = initial_capacity
        self._buffer = [None] * self._capacity
        self._front = 0  # index of the front element
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        """Reallocate and copy all elements to a new buffer. O(n).

        This is the price of contiguous storage. It happens after 8, 16, 32...
        insertions. Total copy cost over n insertions: 8+16+32+...+n = O(n),
        so amortized O(1) per insertion.

        After resize, elements are laid out contiguously starting at index 0,
        which resets the circular wrapping and maximizes cache benefit.
        """
        new_buffer = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[(self._front + i) % self._capacity]
        self._buffer = new_buffer
        self._front = 0
        self._capacity = new_capacity

    def push_front(self, data):
        """Insert at the front. O(1) amortized.

        Moves front index backward (wrapping around via modulo).
        If front is at 0, it wraps to capacity-1. This is why it is
        called a CIRCULAR buffer -- there is no "beginning" or "end"
        in the physical array.
        """
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._front = (self._front - 1) % self._capacity
        self._buffer[self._front] = data
        self._size += 1

    def push_back(self, data):
        """Insert at the back. O(1) amortized.

        The back position is (front + size) % capacity. No shifting needed --
        just place the element and increment size.
        """
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        back = (self._front + self._size) % self._capacity
        self._buffer[back] = data
        self._size += 1

    def pop_front(self):
        """Remove and return the front element. O(1).

        We null out the slot to help garbage collection -- otherwise the
        buffer holds a reference to the object, preventing it from being freed.
        """
        if self.is_empty():
            raise IndexError("pop from empty deque")
        data = self._buffer[self._front]
        self._buffer[self._front] = None  # help GC
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return data

    def pop_back(self):
        """Remove and return the back element. O(1)."""
        if self.is_empty():
            raise IndexError("pop from empty deque")
        back = (self._front + self._size - 1) % self._capacity
        data = self._buffer[back]
        self._buffer[back] = None
        self._size -= 1
        return data

    def peek_front(self):
        """Return the front element without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("peek at empty deque")
        return self._buffer[self._front]

    def peek_back(self):
        """Return the back element without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("peek at empty deque")
        back = (self._front + self._size - 1) % self._capacity
        return self._buffer[back]

    def __getitem__(self, index):
        """O(1) random access -- an advantage over linked-list deques.

        This is why databases use array-based buffers: you can jump to any
        position without traversing from the head.
        """
        if index < 0 or index >= self._size:
            raise IndexError(f"index {index} out of range")
        return self._buffer[(self._front + index) % self._capacity]

    def __iter__(self):
        for i in range(self._size):
            yield self._buffer[(self._front + i) % self._capacity]

    def __repr__(self):
        return f"ArrayDeque([{', '.join(repr(x) for x in self)}])"


# ---------------------------------------------------------------------------
# Sliding Window Maximum -- O(n)
# ---------------------------------------------------------------------------
# Why this matters: monitoring systems, streaming analytics, and stock price
# analysis all need "what is the max in the last K values?" Naive: O(n*k).
# Deque: O(n). For K=60 (seconds) and N=86400 (one day), that is 60x fewer
# operations -- the difference between real-time and falling behind.

def sliding_window_maximum(arr, k):
    """Return the maximum of every contiguous subarray of size k.

    Algorithm: maintain a deque of INDICES whose values are in DECREASING order.
    The front of the deque is always the index of the current window's maximum.

    Key insight: if arr[j] >= arr[i] and j > i, then arr[i] can NEVER be the
    maximum of any future window. arr[j] is both larger AND will remain in the
    window longer. So we discard arr[i] from the back of the deque.

    Each element enters the deque once and leaves once -> O(n) total.

    Invariants maintained:
    1. Indices in deque are in increasing order (left to right)
    2. Values at those indices are in DECREASING order
    3. All indices are within the current window [i-k+1, i]
    """
    if not arr or k <= 0:
        return []
    if k == 1:
        return list(arr)

    n = len(arr)
    dq = collections.deque()  # stores indices, not values
    result = []

    for i in range(n):
        # STEP 1: Remove indices that have fallen out of the window.
        # The window is [i-k+1, i]. If dq[0] < i-k+1, it is expired.
        while dq and dq[0] <= i - k:
            dq.popleft()

        # STEP 2: Remove indices from the back whose values are <= arr[i].
        # These elements can never be the maximum while arr[i] exists in
        # the window, because arr[i] is both larger and newer (will stay longer).
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()

        # STEP 3: Add current index.
        dq.append(i)

        # STEP 4: Once we have processed at least k elements, record the max.
        # The front of the deque is the index of the maximum.
        if i >= k - 1:
            result.append(arr[dq[0]])

    return result


def sliding_window_minimum(arr, k):
    """Return the minimum of every contiguous subarray of size k.

    Identical to sliding_window_maximum but with the deque invariant flipped:
    values are maintained in INCREASING order. The front is always the minimum.

    The only change from maximum: we pop from the back when arr[dq[-1]] >= arr[i]
    instead of <= arr[i]. Everything else is symmetric.
    """
    if not arr or k <= 0:
        return []
    if k == 1:
        return list(arr)

    n = len(arr)
    dq = collections.deque()
    result = []

    for i in range(n):
        # Remove expired indices
        while dq and dq[0] <= i - k:
            dq.popleft()

        # Remove indices from back whose values are >= arr[i]
        # (they can never be the minimum while arr[i] is in the window)
        while dq and arr[dq[-1]] >= arr[i]:
            dq.pop()

        dq.append(i)

        if i >= k - 1:
            result.append(arr[dq[0]])

    return result


# ===========================================================================
# DEMO AND BENCHMARKS
# ===========================================================================

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # SECTION 1: ArrayDeque Operations
    # -----------------------------------------------------------------------
    print("=" * 70)
    print("SECTION 1: ArrayDeque -- Circular Buffer Operations")
    print("=" * 70)

    dq = ArrayDeque()

    operations = [
        ("push_back(1)", lambda d: d.push_back(1)),
        ("push_back(2)", lambda d: d.push_back(2)),
        ("push_back(3)", lambda d: d.push_back(3)),
        ("push_front(0)", lambda d: d.push_front(0)),
        ("push_front(-1)", lambda d: d.push_front(-1)),
    ]

    for desc, op in operations:
        op(dq)
        print(f"  {desc:20s}  -> {dq}")

    print(f"\n  pop_front(): {dq.pop_front()}")
    print(f"  pop_back():  {dq.pop_back()}")
    print(f"  After pops:  {dq}")
    print(f"  peek_front(): {dq.peek_front()}")
    print(f"  peek_back():  {dq.peek_back()}")
    print(f"  Random access [1]: {dq[1]}")
    print(f"  Length: {len(dq)}")

    # Demonstrate resize
    print("\n  Resize demonstration:")
    dq2 = ArrayDeque(initial_capacity=4)
    for i in range(10):
        dq2.push_back(i)
        print(f"    push_back({i}): size={len(dq2)}, capacity={dq2._capacity}")

    # -----------------------------------------------------------------------
    # SECTION 2: Performance Benchmark
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SECTION 2: Performance -- ArrayDeque vs collections.deque vs list")
    print("=" * 70)

    N = 100_000

    def benchmark(name, push_back_fn, push_front_fn, pop_back_fn, pop_front_fn, n):
        """Benchmark the four core deque operations."""
        start = time.perf_counter()
        for i in range(n):
            push_back_fn(i)
        pb_time = time.perf_counter() - start

        start = time.perf_counter()
        for i in range(n):
            pop_back_fn()
        pob_time = time.perf_counter() - start

        start = time.perf_counter()
        for i in range(n):
            push_front_fn(i)
        pf_time = time.perf_counter() - start

        start = time.perf_counter()
        for i in range(n):
            pop_front_fn()
        pof_time = time.perf_counter() - start

        print(f"\n  {name} ({n:,} ops each):")
        print(f"    push_back:  {pb_time*1000:8.2f} ms")
        print(f"    push_front: {pf_time*1000:8.2f} ms")
        print(f"    pop_back:   {pob_time*1000:8.2f} ms")
        print(f"    pop_front:  {pof_time*1000:8.2f} ms")

    # ArrayDeque
    ad = ArrayDeque()
    benchmark("ArrayDeque (circular buffer)",
              ad.push_back, ad.push_front, ad.pop_back, ad.pop_front, N)

    # collections.deque
    cd = collections.deque()
    benchmark("collections.deque (C implementation)",
              cd.append, cd.appendleft, cd.pop, cd.popleft, N)

    # list -- to show why list is terrible as a deque
    print(f"\n  list.pop(0) vs deque.popleft() -- {N:,} operations:")
    lst = list(range(N))
    start = time.perf_counter()
    for _ in range(N):
        lst.pop(0)
    list_time = time.perf_counter() - start

    cdq = collections.deque(range(N))
    start = time.perf_counter()
    for _ in range(N):
        cdq.popleft()
    deque_time = time.perf_counter() - start

    print(f"    list.pop(0):      {list_time*1000:8.2f} ms")
    print(f"    deque.popleft():  {deque_time*1000:8.2f} ms")
    print(f"    Ratio: list is {list_time/deque_time:.1f}x slower")

    # -----------------------------------------------------------------------
    # SECTION 3: Sliding Window Maximum
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SECTION 3: Sliding Window Maximum -- O(n) with Deque")
    print("=" * 70)

    arr = [1, 3, -1, -3, 5, 3, 6, 7]
    k = 3
    print(f"\n  Array: {arr}")
    print(f"  Window size: {k}")
    print(f"  Maximums: {sliding_window_maximum(arr, k)}")
    print(f"  Expected: [3, 3, 5, 5, 6, 7]")

    # Step-by-step trace
    print(f"\n  Step-by-step trace:")
    trace_dq = collections.deque()
    for i in range(len(arr)):
        while trace_dq and trace_dq[0] <= i - k:
            trace_dq.popleft()
        while trace_dq and arr[trace_dq[-1]] <= arr[i]:
            trace_dq.pop()
        trace_dq.append(i)
        dq_vals = [arr[j] for j in trace_dq]
        window_start = max(0, i - k + 1)
        window = arr[window_start:i + 1]
        status = f"max={arr[trace_dq[0]]}" if i >= k - 1 else "window not full"
        print(f"    i={i}, val={arr[i]:2d}, window={str(window):16s} "
              f"deque_vals={dq_vals}, {status}")

    # -----------------------------------------------------------------------
    # SECTION 4: Sliding Window Minimum
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SECTION 4: Sliding Window Minimum -- O(n) with Deque")
    print("=" * 70)

    print(f"\n  Array: {arr}")
    print(f"  Window size: {k}")
    print(f"  Minimums: {sliding_window_minimum(arr, k)}")
    print(f"  Expected: [-1, -3, -3, -3, 3, 3]")

    # -----------------------------------------------------------------------
    # SECTION 5: Benchmark -- Naive vs Deque for Sliding Window
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SECTION 5: Benchmark -- Naive O(n*k) vs Deque O(n)")
    print("=" * 70)

    random.seed(42)
    big_arr = [random.randint(0, 10000) for _ in range(50_000)]
    big_k = 100

    def sliding_window_max_naive(arr, k):
        """O(n*k) baseline: recompute max for every window."""
        return [max(arr[i:i + k]) for i in range(len(arr) - k + 1)]

    print(f"\n  Array size: {len(big_arr):,}, window size: {big_k}")

    start = time.perf_counter()
    r1 = sliding_window_max_naive(big_arr, big_k)
    naive_time = time.perf_counter() - start

    start = time.perf_counter()
    r2 = sliding_window_maximum(big_arr, big_k)
    deque_time = time.perf_counter() - start

    assert r1 == r2, "Results don't match!"
    print(f"    Naive:  {naive_time*1000:8.2f} ms")
    print(f"    Deque:  {deque_time*1000:8.2f} ms")
    print(f"    Speedup: {naive_time/deque_time:.1f}x")

    # Verify minimum too
    def sliding_window_min_naive(arr, k):
        return [min(arr[i:i + k]) for i in range(len(arr) - k + 1)]

    r3 = sliding_window_min_naive(big_arr, big_k)
    r4 = sliding_window_minimum(big_arr, big_k)
    assert r3 == r4, "Minimum results don't match!"
    print(f"\n  Sliding window minimum also verified correct.")

    print("\n" + "=" * 70)
    print("Done! Study the ArrayDeque resize behavior and the sliding window")
    print("algorithms. Then work through practice.py for 5 deque exercises.")
    print("=" * 70)
