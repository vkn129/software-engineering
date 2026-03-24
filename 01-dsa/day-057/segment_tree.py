"""
Day 57: Segment Tree — O(log n) Range Queries and Point/Range Updates
======================================================================
A segment tree is a complete binary tree stored in a flat array where each
node holds the aggregate of a range. Leaves = original values; each parent
= merge(left_child, right_child).

Why not prefix sums?
    Prefix sums give O(1) queries but O(n) updates. Segment trees give
    O(log n) for BOTH — the right trade-off when the array is mutable.

Why flat array, not linked nodes?
    Cache locality. The parent/child relationship is just arithmetic
    (2*i, 2*i+1, i//2), same as binary heaps. No pointer overhead.

Run: python segment_tree.py
"""

import operator
from typing import List, Callable, Optional


# ─── Basic Segment Tree ─────────────────────────────────────────────

class SegmentTree:
    """
    Segment tree with configurable merge operation.

    Supports:
        - build(arr):       O(n) construction
        - query(l, r):      O(log n) range query on [l, r] inclusive
        - update(i, val):   O(log n) point update (set arr[i] = val)

    The merge function and identity element define what the tree computes:
        - Sum:  merge=operator.add, identity=0
        - Min:  merge=min,          identity=float('inf')
        - Max:  merge=max,          identity=float('-inf')
    """

    def __init__(self, arr: List[int],
                 merge: Callable = operator.add,
                 identity: int = 0):
        self.n = len(arr)
        self.merge = merge
        self.identity = identity
        # 4*n is safe for any n — a tighter bound is 2 * next_power_of_2(n),
        # but 4*n avoids the bit math and wastes at most 2x space
        self.tree = [identity] * (4 * self.n)
        self._data = arr[:]  # keep a copy for reference
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    # ── Build ────────────────────────────────────────────────────────

    def _build(self, arr, node, start, end):
        """
        Recursive build. Each call fills one node of the tree.
        Total work = O(n) because we visit each of the ~2n nodes once.
        """
        if start == end:
            # Leaf: store the original value
            self.tree[node] = arr[start]
            return

        mid = (start + end) // 2
        self._build(arr, 2 * node, start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        # Internal node = merge of children
        self.tree[node] = self.merge(self.tree[2 * node], self.tree[2 * node + 1])

    # ── Query ────────────────────────────────────────────────────────

    def query(self, l: int, r: int) -> int:
        """
        Range query on [l, r] inclusive. O(log n).

        The recursion has 3 cases at each node:
        1. Node's range entirely within [l, r] → return node's value
        2. Node's range entirely outside [l, r] → return identity
        3. Partial overlap → recurse on both children, merge results

        At each tree level, at most 2 nodes have partial overlap (one at
        each boundary of [l, r]), so total nodes visited = O(log n).
        """
        if l > r:
            return self.identity
        return self._query(1, 0, self.n - 1, l, r)

    def _query(self, node, start, end, l, r):
        if l > end or r < start:
            # Completely outside
            return self.identity
        if l <= start and end <= r:
            # Completely inside
            return self.tree[node]
        mid = (start + end) // 2
        left_val = self._query(2 * node, start, mid, l, r)
        right_val = self._query(2 * node + 1, mid + 1, end, l, r)
        return self.merge(left_val, right_val)

    # ── Point Update ─────────────────────────────────────────────────

    def update(self, idx: int, val: int):
        """
        Set arr[idx] = val and propagate changes up. O(log n).
        Only nodes on the root-to-leaf path are affected.
        """
        self._data[idx] = val
        self._update(1, 0, self.n - 1, idx, val)

    def _update(self, node, start, end, idx, val):
        if start == end:
            # Leaf — set the new value
            self.tree[node] = val
            return
        mid = (start + end) // 2
        if idx <= mid:
            self._update(2 * node, start, mid, idx, val)
        else:
            self._update(2 * node + 1, mid + 1, end, idx, val)
        # Recompute this node from its (now-updated) children
        self.tree[node] = self.merge(self.tree[2 * node], self.tree[2 * node + 1])

    # ── Visualization ────────────────────────────────────────────────

    def print_tree(self):
        """Print the segment tree level by level for debugging."""
        if self.n == 0:
            print("  (empty tree)")
            return

        # BFS through the tree array
        level_nodes = [(1, 0, self.n - 1)]
        level = 0
        while level_nodes:
            items = []
            next_level = []
            for node, start, end in level_nodes:
                if node < len(self.tree):
                    items.append(f"[{start},{end}]={self.tree[node]}")
                    if start < end:
                        mid = (start + end) // 2
                        next_level.append((2 * node, start, mid))
                        next_level.append((2 * node + 1, mid + 1, end))
            indent = "  " * level
            print(f"  L{level}: {indent}{' | '.join(items)}")
            level_nodes = next_level
            level += 1


# ─── Lazy Segment Tree ──────────────────────────────────────────────

class LazySegmentTree:
    """
    Segment tree with lazy propagation for O(log n) range updates.

    Supports:
        - build(arr):            O(n) construction
        - query(l, r):           O(log n) range sum query on [l, r]
        - update(i, val):        O(log n) point update (add val to arr[i])
        - range_update(l, r, v): O(log n) add v to all elements in [l, r]

    Lazy propagation principle:
        When a range update covers a node's entire range, we DON'T recurse
        to children. Instead, we store the pending update in a "lazy" array.
        Before any operation that needs to examine children, we "push down"
        the lazy value — like copy-on-write in an OS.
    """

    def __init__(self, arr: List[int]):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._data = arr[:]
        if self.n > 0:
            self._build(arr, 1, 0, self.n - 1)

    # ── Build ────────────────────────────────────────────────────────

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
            return
        mid = (start + end) // 2
        self._build(arr, 2 * node, start, mid)
        self._build(arr, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    # ── Push Down (the core of lazy propagation) ─────────────────────

    def _push_down(self, node, start, end):
        """
        If this node has a pending lazy update, apply it to children.

        Why this works: a lazy value of +v on a node covering [start, end]
        means "every element in [start, end] has +v pending." The node's
        own value is already correct (updated when the lazy was set).
        We just need to propagate to children before accessing them.
        """
        if self.lazy[node] != 0:
            mid = (start + end) // 2
            left, right = 2 * node, 2 * node + 1

            # Apply pending update to left child
            self.tree[left] += self.lazy[node] * (mid - start + 1)
            self.lazy[left] += self.lazy[node]

            # Apply pending update to right child
            self.tree[right] += self.lazy[node] * (end - mid)
            self.lazy[right] += self.lazy[node]

            # Clear this node's lazy — it's been pushed down
            self.lazy[node] = 0

    # ── Range Update ─────────────────────────────────────────────────

    def range_update(self, l: int, r: int, val: int):
        """
        Add val to every element in [l, r]. O(log n).

        Without lazy propagation this would be O(n log n) — updating each
        element individually. With lazy, we stop as soon as a node's range
        is fully covered and defer the rest.
        """
        if l > r:
            return
        self._range_update(1, 0, self.n - 1, l, r, val)

    def _range_update(self, node, start, end, l, r, val):
        if l > end or r < start:
            return
        if l <= start and end <= r:
            # This node's range is fully covered — apply and stop
            self.tree[node] += val * (end - start + 1)
            self.lazy[node] += val
            return
        # Partial overlap — must go deeper, so push lazy down first
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self._range_update(2 * node, start, mid, l, r, val)
        self._range_update(2 * node + 1, mid + 1, end, l, r, val)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    # ── Query ────────────────────────────────────────────────────────

    def query(self, l: int, r: int) -> int:
        """Range sum query on [l, r]. O(log n) with lazy push-down."""
        if l > r:
            return 0
        return self._query(1, 0, self.n - 1, l, r)

    def _query(self, node, start, end, l, r):
        if l > end or r < start:
            return 0
        if l <= start and end <= r:
            return self.tree[node]
        # Must go deeper — push lazy down first
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return (self._query(2 * node, start, mid, l, r) +
                self._query(2 * node + 1, mid + 1, end, l, r))

    # ── Point Update ─────────────────────────────────────────────────

    def update(self, idx: int, val: int):
        """Add val to arr[idx]. O(log n)."""
        self._range_update(1, 0, self.n - 1, idx, idx, val)

    # ── Visualization ────────────────────────────────────────────────

    def print_tree(self):
        """Print the lazy segment tree level by level."""
        if self.n == 0:
            print("  (empty tree)")
            return

        level_nodes = [(1, 0, self.n - 1)]
        level = 0
        while level_nodes:
            items = []
            next_level = []
            for node, start, end in level_nodes:
                if node < len(self.tree):
                    lazy_str = f" lazy={self.lazy[node]}" if self.lazy[node] != 0 else ""
                    items.append(f"[{start},{end}]={self.tree[node]}{lazy_str}")
                    if start < end:
                        mid = (start + end) // 2
                        next_level.append((2 * node, start, mid))
                        next_level.append((2 * node + 1, mid + 1, end))
            indent = "  " * level
            print(f"  L{level}: {indent}{' | '.join(items)}")
            level_nodes = next_level
            level += 1


# ─── Demo ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 57: Segment Trees")
    print("=" * 60)

    # === Basic Segment Tree (Sum) ===
    arr = [2, 1, 5, 3, 4]
    print(f"\nOriginal array: {arr}")

    print(f"\n--- Sum Segment Tree ---")
    st = SegmentTree(arr)
    st.print_tree()

    print(f"\n  Range queries (sum):")
    for l, r in [(0, 4), (1, 3), (2, 2), (0, 2), (3, 4)]:
        print(f"    query({l}, {r}) = {st.query(l, r)}")

    print(f"\n  Point update: set index 2 from 5 to 10")
    st.update(2, 10)
    print(f"  After update:")
    st.print_tree()
    print(f"    query(0, 4) = {st.query(0, 4)} (was 15, now 20)")
    print(f"    query(1, 3) = {st.query(1, 3)} (was 9, now 14)")

    # === Min Segment Tree ===
    print(f"\n--- Min Segment Tree ---")
    st_min = SegmentTree(arr, merge=min, identity=float('inf'))
    print(f"  Array: {arr}")
    for l, r in [(0, 4), (1, 3), (0, 1)]:
        print(f"    min_query({l}, {r}) = {st_min.query(l, r)}")

    # === Max Segment Tree ===
    print(f"\n--- Max Segment Tree ---")
    st_max = SegmentTree(arr, merge=max, identity=float('-inf'))
    for l, r in [(0, 4), (1, 3), (3, 4)]:
        print(f"    max_query({l}, {r}) = {st_max.query(l, r)}")

    # === Lazy Segment Tree ===
    arr2 = [1, 3, 5, 7, 9, 11]
    print(f"\n--- Lazy Segment Tree ---")
    print(f"  Array: {arr2}")

    lst = LazySegmentTree(arr2)
    lst.print_tree()

    print(f"\n  query(1, 4) = {lst.query(1, 4)}  (3+5+7+9 = 24)")

    print(f"\n  range_update(1, 3, +10):  add 10 to indices 1..3")
    lst.range_update(1, 3, 10)
    print(f"  After range update:")
    lst.print_tree()

    print(f"\n  query(1, 4) = {lst.query(1, 4)}  (13+15+17+9 = 54)")
    print(f"  query(0, 5) = {lst.query(0, 5)}  (1+13+15+17+9+11 = 66)")

    print(f"\n  Another range_update(0, 5, +1):  add 1 to everything")
    lst.range_update(0, 5, 1)
    print(f"  query(0, 5) = {lst.query(0, 5)}  (66 + 6 = 72)")

    # === Performance demonstration ===
    import time

    sizes = [1_000, 10_000, 100_000]
    print(f"\n--- Performance: 10,000 queries + 10,000 updates ---")
    for n in sizes:
        data = list(range(n))
        t0 = time.perf_counter()
        tree = SegmentTree(data)
        build_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        for i in range(10_000):
            tree.query(i % n, (i + n // 2) % n if (i + n // 2) % n >= i % n else n - 1)
        query_time = time.perf_counter() - t0

        t0 = time.perf_counter()
        for i in range(10_000):
            tree.update(i % n, i)
        update_time = time.perf_counter() - t0

        print(f"  n={n:>7,}: build={build_time:.4f}s  "
              f"10k queries={query_time:.4f}s  10k updates={update_time:.4f}s")

    print("\n--- Lazy vs Non-Lazy: 10,000 range updates ---")
    n = 10_000
    data = list(range(n))

    lst = LazySegmentTree(data)
    t0 = time.perf_counter()
    for i in range(10_000):
        lst.range_update(i % n, (i + 100) % n if (i + 100) % n >= i % n else n - 1, 1)
    lazy_time = time.perf_counter() - t0
    print(f"  Lazy range updates:     {lazy_time:.4f}s")

    st = SegmentTree(data)
    t0 = time.perf_counter()
    for i in range(10_000):
        l = i % n
        r = (i + 100) % n if (i + 100) % n >= l else n - 1
        for j in range(l, min(r + 1, l + 100)):
            st.update(j, st._data[j] + 1)
            st._data[j] += 1
    naive_time = time.perf_counter() - t0
    print(f"  Naive point updates:    {naive_time:.4f}s")
    print(f"  Lazy speedup:           {naive_time / lazy_time:.1f}x")

    print("\nAll demos complete")
