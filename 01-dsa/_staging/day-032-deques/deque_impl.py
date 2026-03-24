"""
Day 12: Deque Implementations -- Doubly Linked List, Circular Buffer, and Python's deque
=========================================================================================

Three implementations of a double-ended queue, each with different trade-offs:
1. Doubly linked list: guaranteed O(1), but pointer overhead and cache misses
2. Circular buffer: amortized O(1), cache-friendly, occasional resize cost
3. Python's collections.deque: block-based hybrid (64-element blocks in a doubly linked list)

We benchmark all three and then implement the classic sliding window maximum algorithm.

Run: python deque_impl.py
"""

import time
import collections


# ---------------------------------------------------------------------------
# IMPLEMENTATION 1: Doubly Linked List Deque
# ---------------------------------------------------------------------------
# Why a doubly linked list? Because we need O(1) operations at BOTH ends.
# A singly linked list gives O(1) at the head but O(n) at the tail (for removal).
# Double links let us go backwards from the tail, so pop_back is O(1).

class DLLNode:
    """A node in a doubly linked list.

    Each node carries the data plus two pointers. On a 64-bit system,
    each pointer is 8 bytes. For a Python object, the overhead is much
    higher (CPython objects have refcount, type pointer, etc.), but the
    principle is the same: two extra references per element.
    """
    __slots__ = ('data', 'prev', 'next')

    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DLLDeque:
    """Deque implemented with a doubly linked list.

    Every operation is guaranteed O(1) -- no amortization, no resizing.
    The cost is memory overhead (two pointers per node) and poor cache
    locality (nodes are scattered across the heap).
    """

    def __init__(self):
        # Sentinel nodes simplify edge cases: we never have to check
        # for None head/tail. The "real" data lives between the sentinels.
        self._head = DLLNode(None)  # sentinel
        self._tail = DLLNode(None)  # sentinel
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def push_front(self, data):
        """Insert at the front. O(1) guaranteed."""
        node = DLLNode(data)
        # Wire the new node between head sentinel and the first real node
        node.prev = self._head
        node.next = self._head.next
        self._head.next.prev = node
        self._head.next = node
        self._size += 1

    def push_back(self, data):
        """Insert at the back. O(1) guaranteed."""
        node = DLLNode(data)
        node.next = self._tail
        node.prev = self._tail.prev
        self._tail.prev.next = node
        self._tail.prev = node
        self._size += 1

    def pop_front(self):
        """Remove and return the front element. O(1) guaranteed."""
        if self.is_empty():
            raise IndexError("pop from empty deque")
        node = self._head.next
        self._head.next = node.next
        node.next.prev = self._head
        self._size -= 1
        return node.data

    def pop_back(self):
        """Remove and return the back element. O(1) guaranteed."""
        if self.is_empty():
            raise IndexError("pop from empty deque")
        node = self._tail.prev
        self._tail.prev = node.prev
        node.prev.next = self._tail
        self._size -= 1
        return node.data

    def peek_front(self):
        if self.is_empty():
            raise IndexError("peek at empty deque")
        return self._head.next.data

    def peek_back(self):
        if self.is_empty():
            raise IndexError("peek at empty deque")
        return self._tail.prev.data

    def __iter__(self):
        current = self._head.next
        while current is not self._tail:
            yield current.data
            current = current.next

    def __repr__(self):
        return f"DLLDeque([{', '.join(repr(x) for x in self)}])"


# ---------------------------------------------------------------------------
# IMPLEMENTATION 2: Circular Buffer Deque
# ---------------------------------------------------------------------------
# Why a circular buffer? Because arrays are stored contiguously in memory.
# The CPU's cache loads entire cache lines (64 bytes), so sequential access
# is fast. The trade-off: occasional O(n) resize when the buffer is full.

class CircularBufferDeque:
    """Deque implemented with a circular buffer (dynamic array).

    Operations are O(1) amortized. Resize doubles capacity, so the total
    cost of n insertions is O(n), giving O(1) amortized per insertion.
    Random access is O(1), unlike the linked list version.
    """

    def __init__(self, initial_capacity=8):
        self._capacity = initial_capacity
        self._buffer = [None] * self._capacity
        self._front = 0  # index of the front element
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        """Resize the buffer. O(n) -- copies all elements.

        This is the cost we pay for cache-friendly contiguous storage.
        It happens O(log n) times over n insertions, so amortized O(1).
        """
        new_buffer = [None] * new_capacity
        for i in range(self._size):
            new_buffer[i] = self._buffer[(self._front + i) % self._capacity]
        self._buffer = new_buffer
        self._front = 0
        self._capacity = new_capacity

    def push_front(self, data):
        """Insert at the front. O(1) amortized."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        # Move front index backward (wrapping around)
        self._front = (self._front - 1) % self._capacity
        self._buffer[self._front] = data
        self._size += 1

    def push_back(self, data):
        """Insert at the back. O(1) amortized."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        back = (self._front + self._size) % self._capacity
        self._buffer[back] = data
        self._size += 1

    def pop_front(self):
        """Remove and return the front element. O(1)."""
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
        if self.is_empty():
            raise IndexError("peek at empty deque")
        return self._buffer[self._front]

    def peek_back(self):
        if self.is_empty():
            raise IndexError("peek at empty deque")
        back = (self._front + self._size - 1) % self._capacity
        return self._buffer[back]

    def __getitem__(self, index):
        """O(1) random access -- an advantage over the linked list."""
        if index < 0 or index >= self._size:
            raise IndexError(f"index {index} out of range")
        return self._buffer[(self._front + index) % self._capacity]

    def __iter__(self):
        for i in range(self._size):
            yield self._buffer[(self._front + i) % self._capacity]

    def __repr__(self):
        return f"CircularBufferDeque([{', '.join(repr(x) for x in self)}])"


# ---------------------------------------------------------------------------
# SECTION 1: Basic Deque Operations Demo
# ---------------------------------------------------------------------------

print("=" * 70)
print("SECTION 1: Deque Operations -- Doubly Linked List vs Circular Buffer")
print("=" * 70)

dll = DLLDeque()
cb = CircularBufferDeque()

operations = [
    ("push_back(1)", lambda d: d.push_back(1)),
    ("push_back(2)", lambda d: d.push_back(2)),
    ("push_back(3)", lambda d: d.push_back(3)),
    ("push_front(0)", lambda d: d.push_front(0)),
    ("push_front(-1)", lambda d: d.push_front(-1)),
]

for desc, op in operations:
    op(dll)
    op(cb)
    print(f"  {desc:20s}  DLL: {dll}  CB: {cb}")

print(f"\n  pop_front(): DLL={dll.pop_front()}, CB={cb.pop_front()}")
print(f"  pop_back():  DLL={dll.pop_back()}, CB={cb.pop_back()}")
print(f"  After pops:  DLL: {dll}  CB: {cb}")
print(f"  peek_front: DLL={dll.peek_front()}, CB={cb.peek_front()}")
print(f"  peek_back:  DLL={dll.peek_back()}, CB={cb.peek_back()}")


# ---------------------------------------------------------------------------
# SECTION 2: Performance Comparison
# ---------------------------------------------------------------------------
# Why measure? Because theoretical complexity hides constant factors.
# Cache locality makes a 10x difference for the same O(1) operation.

print("\n" + "=" * 70)
print("SECTION 2: Performance Benchmark")
print("=" * 70)

N = 100_000

def benchmark_deque(deque_factory, name, n):
    """Benchmark push/pop operations."""
    d = deque_factory()

    # push_back
    start = time.perf_counter()
    for i in range(n):
        d.push_back(i)
    push_back_time = time.perf_counter() - start

    # push_front
    d2 = deque_factory()
    start = time.perf_counter()
    for i in range(n):
        d2.push_front(i)
    push_front_time = time.perf_counter() - start

    # pop_back
    start = time.perf_counter()
    for i in range(n):
        d.pop_back()
    pop_back_time = time.perf_counter() - start

    # pop_front
    start = time.perf_counter()
    for i in range(n):
        d2.pop_front()
    pop_front_time = time.perf_counter() - start

    print(f"\n  {name} ({n:,} operations each):")
    print(f"    push_back:  {push_back_time*1000:8.2f} ms")
    print(f"    push_front: {push_front_time*1000:8.2f} ms")
    print(f"    pop_back:   {pop_back_time*1000:8.2f} ms")
    print(f"    pop_front:  {pop_front_time*1000:8.2f} ms")

benchmark_deque(DLLDeque, "Doubly Linked List Deque", N)
benchmark_deque(CircularBufferDeque, "Circular Buffer Deque", N)

# Python's collections.deque -- the production choice
class DequeWrapper:
    """Thin wrapper to match our interface for benchmarking."""
    def __init__(self):
        self._d = collections.deque()
    def push_back(self, x):
        self._d.append(x)
    def push_front(self, x):
        self._d.appendleft(x)
    def pop_back(self):
        return self._d.pop()
    def pop_front(self):
        return self._d.popleft()

benchmark_deque(DequeWrapper, "collections.deque (CPython C impl)", N)

# Show why list is terrible as a queue
print(f"\n  list.pop(0) vs deque.popleft() -- {N:,} operations:")
lst = list(range(N))
start = time.perf_counter()
for _ in range(N):
    lst.pop(0)
list_time = time.perf_counter() - start

dq = collections.deque(range(N))
start = time.perf_counter()
for _ in range(N):
    dq.popleft()
deque_time = time.perf_counter() - start

print(f"    list.pop(0):      {list_time*1000:8.2f} ms")
print(f"    deque.popleft():  {deque_time*1000:8.2f} ms")
print(f"    Ratio: list is {list_time/deque_time:.1f}x slower")


# ---------------------------------------------------------------------------
# SECTION 3: Sliding Window Maximum -- The Classic Deque Algorithm
# ---------------------------------------------------------------------------
# Why this matters: monitoring systems, streaming analytics, and stock
# price analysis all need "what is the max/min in the last K values?"
# Naive: O(n*k). Deque: O(n). For K=60 (seconds) and N=86400 (day of
# data), that is 60x fewer operations.

print("\n" + "=" * 70)
print("SECTION 3: Sliding Window Maximum")
print("=" * 70)

def sliding_window_max_naive(arr, k):
    """O(n*k) naive approach: recompute max for every window position."""
    if not arr or k <= 0:
        return []
    result = []
    for i in range(len(arr) - k + 1):
        result.append(max(arr[i:i + k]))
    return result


def sliding_window_max_deque(arr, k):
    """O(n) deque approach: maintain a deque of indices in decreasing value order.

    Key insight: if arr[j] >= arr[i] and j > i, then arr[i] can NEVER be
    the maximum of any future window (because arr[j] is both larger and
    will stay in the window longer). So we can discard arr[i].

    The deque stores indices, not values. The front of the deque is always
    the index of the maximum in the current window.

    Invariants:
    1. Indices in deque are in increasing order (left to right)
    2. Values at those indices are in DECREASING order
    3. All indices are within the current window
    """
    if not arr or k <= 0:
        return []

    dq = collections.deque()  # stores indices
    result = []

    for i in range(len(arr)):
        # Remove indices that have fallen out of the window
        while dq and dq[0] <= i - k:
            dq.popleft()

        # Remove indices from the back whose values are <= arr[i]
        # (they can never be the maximum while arr[i] is in the window)
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()

        dq.append(i)

        # Once we have a full window, record the maximum
        if i >= k - 1:
            result.append(arr[dq[0]])

    return result


# Demonstrate with a small example
arr = [1, 3, -1, -3, 5, 3, 6, 7]
k = 3
print(f"\n  Array: {arr}")
print(f"  Window size: {k}")
print(f"  Naive result:  {sliding_window_max_naive(arr, k)}")
print(f"  Deque result:  {sliding_window_max_deque(arr, k)}")

# Walk through step by step
print(f"\n  Step-by-step walkthrough:")
dq = collections.deque()
for i in range(len(arr)):
    while dq and dq[0] <= i - k:
        dq.popleft()
    while dq and arr[dq[-1]] <= arr[i]:
        dq.pop()
    dq.append(i)
    window_start = max(0, i - k + 1)
    window = arr[window_start:i + 1]
    dq_vals = [arr[j] for j in dq]
    if i >= k - 1:
        print(f"    i={i}, window={window}, deque_vals={dq_vals}, max={arr[dq[0]]}")

# Benchmark naive vs deque
import random
random.seed(42)
big_arr = [random.randint(0, 10000) for _ in range(50_000)]
big_k = 100

print(f"\n  Benchmark: array of {len(big_arr):,}, window size {big_k}")

start = time.perf_counter()
r1 = sliding_window_max_naive(big_arr, big_k)
naive_time = time.perf_counter() - start

start = time.perf_counter()
r2 = sliding_window_max_deque(big_arr, big_k)
deque_time = time.perf_counter() - start

assert r1 == r2, "Results don't match!"
print(f"    Naive:  {naive_time*1000:8.2f} ms")
print(f"    Deque:  {deque_time*1000:8.2f} ms")
print(f"    Ratio:  Naive is {naive_time/deque_time:.1f}x slower")


# ---------------------------------------------------------------------------
# SECTION 4: Palindrome Checking with Deque
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 4: Palindrome Checking with Deque")
print("=" * 70)

def is_palindrome_deque(s):
    """Check if a string is a palindrome using a deque.

    Push all characters onto a deque. Pop from both ends and compare.
    This is more illustrative than efficient (string slicing is faster),
    but it demonstrates the "process from both ends" pattern.
    """
    # Clean: lowercase, letters only
    cleaned = [c.lower() for c in s if c.isalnum()]
    dq = collections.deque(cleaned)

    while len(dq) > 1:
        front = dq.popleft()
        back = dq.pop()
        if front != back:
            return False
    return True

test_strings = [
    "racecar",
    "A man a plan a canal Panama",
    "hello",
    "Was it a car or a cat I saw",
    "",
    "a",
]

for s in test_strings:
    result = is_palindrome_deque(s)
    print(f"  '{s}' -> {'palindrome' if result else 'not palindrome'}")


# ---------------------------------------------------------------------------
# SECTION 5: Bounded Deque (maxlen) -- For Sliding Windows
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 5: Bounded Deque -- Fixed-Size Buffers")
print("=" * 70)

print("""
  Python's collections.deque supports a maxlen parameter.
  When the deque is full, pushing to one end automatically
  discards from the other end. This is perfect for:
  - Recent history buffers ("last 100 log entries")
  - Moving averages ("average of last 60 seconds")
  - Rate limiters ("count requests in last N seconds")
""")

# Demonstrate bounded deque
recent = collections.deque(maxlen=5)
for i in range(10):
    recent.append(i)
    print(f"  Append {i}: {list(recent)}")

print(f"\n  Final deque: {list(recent)} (only last 5 elements)")
print(f"  This is O(1) per append with no manual size management.")


# ---------------------------------------------------------------------------
# SECTION 6: 0-1 BFS with Deque
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 6: 0-1 BFS -- Shortest Path with Deque")
print("=" * 70)

def bfs_01(graph, start, end):
    """Shortest path in a graph where edges have weight 0 or 1.

    Normal BFS works for unweighted graphs. Dijkstra works for any
    non-negative weights but costs O((V+E) log V). When weights are
    only 0 or 1, a deque gives O(V+E):
    - Weight-0 edges: push neighbor to the FRONT (same cost level)
    - Weight-1 edges: push neighbor to the BACK (next cost level)

    This maintains the invariant that the deque is sorted by distance,
    just like BFS maintains its level-order invariant.
    """
    dist = {start: 0}
    dq = collections.deque([start])

    while dq:
        node = dq.popleft()
        if node == end:
            return dist[end]
        for neighbor, weight in graph[node]:
            new_dist = dist[node] + weight
            if neighbor not in dist or new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                if weight == 0:
                    dq.appendleft(neighbor)  # front -- same distance
                else:
                    dq.append(neighbor)       # back -- next distance
    return float('inf')

# Example: grid where some moves are free (weight 0) and some cost 1
graph = {
    'A': [('B', 1), ('C', 0)],
    'B': [('D', 1)],
    'C': [('D', 0), ('E', 1)],
    'D': [('F', 1)],
    'E': [('F', 0)],
    'F': [],
}

print(f"\n  Graph: A->B(1), A->C(0), B->D(1), C->D(0), C->E(1), D->F(1), E->F(0)")
print(f"  Shortest path A->F: {bfs_01(graph, 'A', 'F')}")
print(f"  Path goes A->C(0)->E(1)->F(0) = cost 1")
print(f"  vs A->B(1)->D(1)->F(1) = cost 3")


print("\n" + "=" * 70)
print("Done! Study the sliding window maximum algorithm carefully --")
print("it appears in interviews and production systems constantly.")
print("Then work through practice.py.")
print("=" * 70)
