"""
Day 52: Advanced Heaps — D-ary Heaps and Indexed Priority Queues
================================================================
Two heap variants that solve real limitations of binary heaps:

1. D-ary heap: tune branching factor for cache behavior and workload
2. Indexed PQ: O(log n) decrease-key for Dijkstra/Prim algorithms

Run: python advanced_heaps.py
"""


# ─── D-ary Heap ─────────────────────────────────────────────────────

class DaryHeap:
    """
    A d-ary min-heap. Each node has up to d children.

    Index arithmetic (0-based):
        parent(i)     = (i - 1) // d
        k-th child(i) = d * i + k + 1,  k ∈ [0, d)

    Why vary d?
        d=2: standard binary heap (balanced sift-up vs sift-down)
        d=4: fewer cache lines touched on sift-up (database buffer pools)
        d=E/V: optimal for Dijkstra on specific graph densities
    """

    def __init__(self, d=4):
        if d < 2:
            raise ValueError("d must be >= 2")
        self._d = d
        self._data = []

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return len(self._data) > 0

    def peek(self):
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def push(self, value):
        self._data.append(value)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        if not self._data:
            raise IndexError("pop from empty heap")
        self._swap(0, len(self._data) - 1)
        val = self._data.pop()
        if self._data:
            self._sift_down(0)
        return val

    def _parent(self, i):
        return (i - 1) // self._d

    def _children(self, i):
        """Return indices of all children of node i."""
        start = self._d * i + 1
        end = min(start + self._d, len(self._data))
        return range(start, end)

    def _sift_up(self, i):
        while i > 0:
            p = self._parent(i)
            if self._data[i] < self._data[p]:
                self._swap(i, p)
                i = p
            else:
                break

    def _sift_down(self, i):
        """
        Compare with ALL d children and swap with the smallest.
        Cost per level: O(d) comparisons × O(log_d n) levels = O(d · log_d n)
        """
        while True:
            smallest = i
            for c in self._children(i):
                if self._data[c] < self._data[smallest]:
                    smallest = c
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    @property
    def height(self):
        """Height of the d-ary tree."""
        import math
        if not self._data:
            return 0
        return int(math.log(len(self._data) * (self._d - 1) + 1) / math.log(self._d))


# ─── Indexed Priority Queue ────────────────────────────────────────

class IndexedMinPQ:
    """
    Priority queue where each element has a unique integer ID (0 to maxN-1).
    Supports O(log n) decrease_key — essential for Dijkstra and Prim.

    Three parallel arrays maintain the mapping:
        _heap[pos] = id          (position in heap → element ID)
        _pos[id]   = pos         (element ID → position in heap)
        _keys[id]  = priority    (element ID → priority value)

    When we swap two elements in the heap, we update both _heap and _pos
    to keep the bidirectional mapping consistent.

    Why is this needed?
    In Dijkstra's, when we relax an edge u→v with weight w:
        new_dist = dist[u] + w
        if new_dist < dist[v]:
            dist[v] = new_dist
            pq.decrease_key(v, new_dist)  ← need to find v in O(1), sift in O(log n)

    Without an indexed PQ, you'd either:
    - Scan the heap for v: O(n) per relaxation → Dijkstra becomes O(VE)
    - Push duplicate entries: O((V+E) log(V+E)) — works but wastes memory
    """

    def __init__(self, max_n):
        self._max_n = max_n
        self._n = 0
        self._heap = [0] * max_n       # heap[pos] = id
        self._pos = [-1] * max_n       # pos[id] = position in heap (-1 = absent)
        self._keys = [None] * max_n    # keys[id] = priority

    def __len__(self):
        return self._n

    def __bool__(self):
        return self._n > 0

    def __contains__(self, id):
        return 0 <= id < self._max_n and self._pos[id] != -1

    def peek(self):
        """Return (id, key) of the minimum element."""
        if self._n == 0:
            raise IndexError("peek from empty PQ")
        id = self._heap[0]
        return id, self._keys[id]

    def push(self, id, key):
        """Insert element with given id and priority key."""
        if id in self:
            raise ValueError(f"ID {id} already in PQ")
        self._keys[id] = key
        self._heap[self._n] = id
        self._pos[id] = self._n
        self._n += 1
        self._sift_up(self._n - 1)

    def pop(self):
        """Remove and return (id, key) of the minimum element."""
        if self._n == 0:
            raise IndexError("pop from empty PQ")
        id = self._heap[0]
        key = self._keys[id]
        self._n -= 1
        self._swap(0, self._n)
        self._pos[id] = -1
        self._keys[id] = None
        if self._n > 0:
            self._sift_down(0)
        return id, key

    def decrease_key(self, id, new_key):
        """
        Decrease the priority of element id to new_key.
        O(log n) — look up position in O(1), sift up in O(log n).
        """
        if id not in self:
            raise KeyError(f"ID {id} not in PQ")
        if new_key > self._keys[id]:
            raise ValueError("New key must be smaller than current key")
        self._keys[id] = new_key
        self._sift_up(self._pos[id])

    def key_of(self, id):
        """Return current priority of element id."""
        if id not in self:
            raise KeyError(f"ID {id} not in PQ")
        return self._keys[id]

    def _sift_up(self, pos):
        while pos > 0:
            parent = (pos - 1) // 2
            if self._keys[self._heap[pos]] < self._keys[self._heap[parent]]:
                self._swap(pos, parent)
                pos = parent
            else:
                break

    def _sift_down(self, pos):
        while True:
            smallest = pos
            left = 2 * pos + 1
            right = 2 * pos + 2
            if left < self._n and self._keys[self._heap[left]] < self._keys[self._heap[smallest]]:
                smallest = left
            if right < self._n and self._keys[self._heap[right]] < self._keys[self._heap[smallest]]:
                smallest = right
            if smallest == pos:
                break
            self._swap(pos, smallest)
            pos = smallest

    def _swap(self, i, j):
        # Swap in heap array
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]
        # Update position mappings
        self._pos[self._heap[i]] = i
        self._pos[self._heap[j]] = j


# ─── Dijkstra with Indexed PQ ──────────────────────────────────────

def dijkstra(adj, source):
    """
    Shortest paths from source using an Indexed Priority Queue.

    adj: adjacency list, adj[u] = [(v, weight), ...]
    Returns: dist array where dist[v] = shortest distance from source to v

    Time: O((V + E) log V) — each vertex extracted once, each edge relaxed once,
    each decrease_key is O(log V).
    """
    n = len(adj)
    dist = [float('inf')] * n
    dist[source] = 0

    pq = IndexedMinPQ(n)
    pq.push(source, 0)

    while pq:
        u, d = pq.pop()
        if d > dist[u]:
            continue  # Stale entry

        for v, w in adj[u]:
            new_dist = dist[u] + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                if v in pq:
                    pq.decrease_key(v, new_dist)
                else:
                    pq.push(v, new_dist)

    return dist


# ─── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import time

    print("=" * 60)
    print("Day 52: Advanced Heaps")
    print("=" * 60)

    # D-ary heap comparison
    print("\n--- D-ary Heap: Branching Factor Comparison ---")
    import random
    random.seed(42)
    data = [random.randint(0, 100000) for _ in range(10000)]

    for d in [2, 3, 4, 8, 16]:
        h = DaryHeap(d=d)
        t0 = time.perf_counter()
        for val in data:
            h.push(val)
        result = []
        while h:
            result.append(h.pop())
        elapsed = time.perf_counter() - t0
        assert result == sorted(data), f"d={d} sorting failed!"
        print(f"  d={d:2d}: {elapsed*1000:.1f}ms  (height={DaryHeap(d=d).height} for n=0)")

    # Indexed PQ
    print("\n--- Indexed Priority Queue ---")
    pq = IndexedMinPQ(10)
    items = [(0, "A", 5), (1, "B", 3), (2, "C", 8), (3, "D", 1), (4, "E", 7)]
    for id, name, key in items:
        pq.push(id, key)
        print(f"  push(id={id}/{name}, priority={key})")

    print(f"  Min: id={pq.peek()[0]} priority={pq.peek()[1]}")

    print("  decrease_key(id=2/C, 0)")  # C: 8 → 0
    pq.decrease_key(2, 0)
    print(f"  Min: id={pq.peek()[0]} priority={pq.peek()[1]}")

    print("  Extracting all:")
    while pq:
        id, key = pq.pop()
        name = items[id][1]
        print(f"    id={id}/{name} priority={key}")

    # Dijkstra with Indexed PQ
    print("\n--- Dijkstra with Indexed PQ ---")
    # Graph:  0 --4-- 1 --1-- 3
    #         |       |       |
    #         2       2       5
    #         |       |       |
    #         2 --3-- 4 --1-- 5
    adj = [
        [(1, 4), (2, 2)],          # 0
        [(0, 4), (3, 1), (4, 2)],  # 1
        [(0, 2), (4, 3)],          # 2
        [(1, 1), (5, 5)],          # 3
        [(1, 2), (2, 3), (5, 1)],  # 4
        [(3, 5), (4, 1)],          # 5
    ]
    dist = dijkstra(adj, 0)
    print(f"  Shortest distances from vertex 0:")
    for v, d in enumerate(dist):
        print(f"    → vertex {v}: {d}")

    print("\n✓ All demos complete")
