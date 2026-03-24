"""
Day 26 Practice: Unrolled Linked List Exercises

Four exercises that deepen your understanding of unrolled linked lists.
Each exercise has a TODO stub and a _sol_ solution. Try the TODO first.

Run: python practice.py

Rules:
- Do NOT use any external libraries.
- Build on the UnrolledLinkedList from unrolled_linked_list.py.
"""

import time
import math


# ---------------------------------------------------------------------------
# Base implementation (imported concept — self-contained here for practice)
# ---------------------------------------------------------------------------

class UnrolledNode:
    __slots__ = ('elements', 'next', 'max_size')

    def __init__(self, max_size):
        self.elements = []
        self.next = None
        self.max_size = max_size

    @property
    def count(self):
        return len(self.elements)

    def is_full(self):
        return self.count >= self.max_size

    def is_underfull(self):
        return self.count < self.max_size // 2

    def __repr__(self):
        return f"UnrolledNode({self.elements})"


class UnrolledLinkedList:
    """Minimal unrolled linked list — insert and append only.

    Exercises below will extend this with additional capabilities.
    """

    def __init__(self, max_size=4):
        self.max_size = max_size
        self.head = None
        self._size = 0

    def __len__(self):
        return self._size

    def append(self, value):
        self.insert(self._size, value)

    def insert(self, index, value):
        if index < 0:
            index = max(0, self._size + index)
        if index > self._size:
            index = self._size

        if self.head is None:
            self.head = UnrolledNode(self.max_size)
            self.head.elements.append(value)
            self._size += 1
            return

        node = self.head
        pos = index
        while node.next is not None and pos > node.count:
            pos -= node.count
            node = node.next

        if pos > node.count:
            pos = node.count

        node.elements.insert(pos, value)
        self._size += 1

        if node.count > self.max_size:
            self._split(node)

    def _split(self, node):
        mid = node.count // 2
        new_node = UnrolledNode(self.max_size)
        new_node.elements = node.elements[mid:]
        node.elements = node.elements[:mid]
        new_node.next = node.next
        node.next = new_node

    def to_list(self):
        result = []
        node = self.head
        while node is not None:
            result.extend(node.elements)
            node = node.next
        return result

    def __repr__(self):
        blocks = []
        node = self.head
        while node is not None:
            blocks.append(str(node.elements))
            node = node.next
        return " -> ".join(blocks) if blocks else "[]"

    def node_count(self):
        count = 0
        node = self.head
        while node is not None:
            count += 1
            node = node.next
        return count


# ---------------------------------------------------------------------------
# Regular linked list for benchmarking comparison
# ---------------------------------------------------------------------------

class LLNode:
    """A simple singly linked list node for benchmarking."""
    __slots__ = ('val', 'next')

    def __init__(self, val):
        self.val = val
        self.next = None


class LinkedList:
    """A minimal singly linked list for benchmarking against the unrolled version."""

    def __init__(self):
        self.head = None
        self._size = 0

    def append(self, val):
        new_node = LLNode(val)
        if self.head is None:
            self.head = new_node
        else:
            # Walk to the tail. This is O(n) — one reason regular linked lists
            # are slow. A tail pointer would fix this, but we keep it simple.
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1

    def get(self, index):
        current = self.head
        for _ in range(index):
            current = current.next
        return current.val

    def __len__(self):
        return self._size


# ===========================================================================
# Exercise 1: Index-based access — O(sqrt(n)) with block skipping
# ===========================================================================

def ex1_get_element(ull, index):
    """Return the element at `index` in the unrolled linked list.

    The key insight: you can skip entire nodes by comparing `index` against
    each node's count. This means you traverse at most n/B nodes instead of
    n individual elements. With B = sqrt(n), that's O(sqrt(n)).

    Args:
        ull: An UnrolledLinkedList instance.
        index: 0-based index of the element to retrieve.

    Returns:
        The element at that index.

    Raises:
        IndexError: if index is out of range.
    """
    # TODO: implement this
    # Hint: walk the node chain. At each node, if index >= node.count,
    #       subtract node.count from index and move to node.next.
    #       When index < node.count, return node.elements[index].
    pass


def _sol_ex1_get_element(ull, index):
    """Solution: index-based access by skipping whole blocks."""
    if index < 0:
        index = len(ull) + index
    if index < 0 or index >= len(ull):
        raise IndexError(f"index {index} out of range for size {len(ull)}")

    # Walk the chain, subtracting each node's count.
    # This is the "unrolled" advantage: we skip B elements per node
    # instead of 1 element per node in a regular linked list.
    node = ull.head
    pos = index
    while pos >= node.count:
        pos -= node.count
        node = node.next
    return node.elements[pos]


# ===========================================================================
# Exercise 2: Benchmark — unrolled vs linked list vs Python list
# ===========================================================================

def ex2_benchmark(n=5000, block_size=64):
    """Benchmark sequential traversal: unrolled linked list vs regular linked
    list vs Python list.

    Build all three structures with n elements, then time how long it takes
    to sum every element by traversal.

    Print results showing the relative speed difference.

    Args:
        n: number of elements to insert.
        block_size: max_size for the unrolled linked list.

    Returns:
        Tuple of (linked_list_time, unrolled_time, python_list_time) in seconds.
    """
    # TODO: implement this
    # Steps:
    # 1. Build a regular linked list of n elements
    # 2. Build an unrolled linked list of n elements with the given block_size
    # 3. Build a Python list of n elements
    # 4. Time summing all elements in each (use time.perf_counter())
    # 5. Print the results and return the tuple of times
    pass


def _sol_ex2_benchmark(n=5000, block_size=64):
    """Solution: benchmark traversal of three list types."""
    # Build regular linked list — O(n^2) because we walk to tail each time.
    # For benchmarking purposes this is fine; we're timing traversal, not build.
    ll = LinkedList()
    for i in range(n):
        ll.append(i)

    # Build unrolled linked list
    ull = UnrolledLinkedList(max_size=block_size)
    for i in range(n):
        ull.append(i)

    # Build Python list
    py_list = list(range(n))

    # Time linked list traversal
    start = time.perf_counter()
    total = 0
    node = ll.head
    while node:
        total += node.val
        node = node.next
    ll_time = time.perf_counter() - start

    # Time unrolled linked list traversal — iterate blocks, then elements
    start = time.perf_counter()
    total = 0
    node = ull.head
    while node:
        for elem in node.elements:
            total += elem
        node = node.next
    ull_time = time.perf_counter() - start

    # Time Python list traversal
    start = time.perf_counter()
    total = 0
    for elem in py_list:
        total += elem
    py_time = time.perf_counter() - start

    print(f"  Traversal of {n:,} elements:")
    print(f"    Linked list:     {ll_time*1000:.2f} ms")
    print(f"    Unrolled (B={block_size}): {ull_time*1000:.2f} ms")
    print(f"    Python list:     {py_time*1000:.2f} ms")
    if ull_time > 0:
        print(f"    Unrolled is ~{ll_time/ull_time:.1f}x faster than linked list")

    return ll_time, ull_time, py_time


# ===========================================================================
# Exercise 3: __iter__ protocol — make the unrolled list work with for loops
# ===========================================================================

class IterableUnrolledLinkedList(UnrolledLinkedList):
    """An unrolled linked list that supports Python's iteration protocol.

    After implementing __iter__, you can write:
        for element in my_unrolled_list:
            print(element)

    The iterator should yield elements in order, traversing each node's
    elements array before moving to the next node. This is efficient because
    iterating within a node is sequential memory access.
    """

    def __iter__(self):
        """Yield each element in order across all nodes.

        TODO: implement this as a generator.

        Hint: use a while loop over nodes, and a for loop over each
        node's elements. The `yield` keyword makes this a generator.
        """
        # TODO: implement this
        pass


class _Sol_IterableUnrolledLinkedList(UnrolledLinkedList):
    """Solution: iterable unrolled linked list."""

    def __iter__(self):
        """Yield elements by walking nodes, then elements within each node.

        This is a generator — each `yield` suspends execution and returns
        the next value. The caller sees a seamless stream of elements,
        but internally we're exploiting block structure: sequential access
        within each node, pointer chase only between nodes.
        """
        node = self.head
        while node is not None:
            # Iterating over node.elements is sequential memory access —
            # the CPU prefetcher loves this. This is the cache win.
            for elem in node.elements:
                yield elem
            # Only this step causes a potential cache miss:
            # following the pointer to the next node.
            node = node.next


# ===========================================================================
# Exercise 4: Optimal block size — find it empirically
# ===========================================================================

def ex4_find_optimal_block_size(n=5000, block_sizes=None):
    """Benchmark different block sizes to find the empirically optimal one.

    For each block size, build an unrolled linked list with n elements,
    then time sequential traversal (summing all elements).

    Theory predicts sqrt(n) is optimal for insert/delete, but for pure
    traversal, larger blocks are better (fewer pointer chases). This
    exercise lets you see the trade-off empirically.

    Args:
        n: number of elements.
        block_sizes: list of block sizes to test. If None, uses a default range.

    Returns:
        Tuple of (best_block_size, results_dict) where results_dict maps
        block_size -> traversal_time_seconds.
    """
    # TODO: implement this
    # Steps:
    # 1. Default block_sizes to [2, 4, 8, 16, 32, 64, 128, 256, 512]
    # 2. For each block size:
    #    a. Build an unrolled linked list with n elements
    #    b. Time how long it takes to sum all elements (traverse the list)
    #    c. Store the time in a results dict
    # 3. Print a table of results
    # 4. Return (best_block_size, results_dict)
    pass


def _sol_ex4_find_optimal_block_size(n=5000, block_sizes=None):
    """Solution: benchmark block sizes to find the sweet spot."""
    if block_sizes is None:
        block_sizes = [2, 4, 8, 16, 32, 64, 128, 256, 512]

    results = {}

    for bs in block_sizes:
        # Build
        ull = UnrolledLinkedList(max_size=bs)
        for i in range(n):
            ull.append(i)

        # Time traversal (multiple runs for stability)
        runs = 5
        best_time = float('inf')
        for _ in range(runs):
            start = time.perf_counter()
            total = 0
            node = ull.head
            while node:
                for elem in node.elements:
                    total += elem
                node = node.next
            elapsed = time.perf_counter() - start
            best_time = min(best_time, elapsed)

        results[bs] = best_time

    # Print results table
    print(f"  Block size benchmark ({n:,} elements, best of 5 runs):")
    print(f"  {'Block Size':>12} {'Nodes':>8} {'Time (ms)':>12} {'Relative':>10}")
    print(f"  {'-'*12} {'-'*8} {'-'*12} {'-'*10}")

    min_time = min(results.values())
    for bs in block_sizes:
        t = results[bs]
        node_count = math.ceil(n / bs)
        relative = t / min_time
        marker = " <-- best" if t == min_time else ""
        print(f"  {bs:>12} {node_count:>8} {t*1000:>12.3f} {relative:>10.2f}x{marker}")

    best_bs = min(results, key=results.get)
    sqrt_n = int(math.sqrt(n))
    print(f"\n  Optimal block size for traversal: {best_bs}")
    print(f"  sqrt({n}) = {sqrt_n}")
    print(f"  (For pure traversal, larger blocks win because fewer pointer chases.)")
    print(f"  (sqrt(n) optimizes for insert/delete, not traversal.)")

    return best_bs, results


# ===========================================================================
# Test runner
# ===========================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} — got {got!r}, expected {expected!r}")
            failed += 1

    # --- Exercise 1 tests ---
    print("\n" + "=" * 60)
    print("Exercise 1: Index-based access")
    print("=" * 60)

    ull = UnrolledLinkedList(max_size=4)
    for i in range(10):
        ull.append(i * 10)

    # Test the student's implementation
    fn = ex1_get_element if ex1_get_element(ull, 0) is not None else _sol_ex1_get_element
    if ex1_get_element(ull, 0) is None:
        print("  (Using solution — implement ex1_get_element to see your results)")
        fn = _sol_ex1_get_element
    else:
        fn = ex1_get_element

    check("get(0)", fn(ull, 0), 0)
    check("get(5)", fn(ull, 5), 50)
    check("get(9)", fn(ull, 9), 90)
    check("get(-1)", fn(ull, -1), 90)

    try:
        fn(ull, 10)
        print("  FAIL: get(10) should raise IndexError")
        failed += 1
    except IndexError:
        print("  PASS: get(10) raises IndexError")
        passed += 1

    # --- Exercise 2 tests ---
    print("\n" + "=" * 60)
    print("Exercise 2: Benchmark traversal")
    print("=" * 60)

    result = ex2_benchmark(n=3000, block_size=32)
    if result is None:
        print("  (Using solution — implement ex2_benchmark to see your results)")
        result = _sol_ex2_benchmark(n=3000, block_size=32)

    ll_t, ull_t, py_t = result
    check("all times are positive", all(t > 0 for t in result), True)

    # --- Exercise 3 tests ---
    print("\n" + "=" * 60)
    print("Exercise 3: __iter__ protocol")
    print("=" * 60)

    # Try student's version first, fall back to solution
    test_list = IterableUnrolledLinkedList(max_size=4)
    for i in range(8):
        test_list.append(i)

    items = list(test_list)
    if items == []:
        print("  (Using solution — implement __iter__ to see your results)")
        test_list = _Sol_IterableUnrolledLinkedList(max_size=4)
        for i in range(8):
            test_list.append(i)
        items = list(test_list)

    check("iter produces all elements", items, [0, 1, 2, 3, 4, 5, 6, 7])

    # Test that for-loop works
    collected = []
    for x in test_list:
        collected.append(x)
    check("for-loop works", collected, [0, 1, 2, 3, 4, 5, 6, 7])

    # Test empty list iteration
    empty = _Sol_IterableUnrolledLinkedList(max_size=4)
    check("empty iteration", list(empty), [])

    # Test sum() works (uses __iter__ under the hood)
    check("sum() works via __iter__", sum(test_list), 28)

    # --- Exercise 4 tests ---
    print("\n" + "=" * 60)
    print("Exercise 4: Optimal block size")
    print("=" * 60)

    result = ex4_find_optimal_block_size(n=3000)
    if result is None:
        print("  (Using solution — implement ex4_find_optimal_block_size to see your results)")
        result = _sol_ex4_find_optimal_block_size(n=3000)

    best_bs, times = result
    check("found a best block size", best_bs in times, True)
    check("all times are positive", all(t > 0 for t in times.values()), True)
    check("tested multiple block sizes", len(times) >= 5, True)

    # --- Summary ---
    print("\n" + "=" * 60)
    total = passed + failed
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
