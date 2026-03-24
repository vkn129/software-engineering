"""
Day 31: Queue Implementations

Why queues matter: they enforce FIFO (first-in, first-out), which is the
foundation of fairness in computing. BFS, scheduling, message passing,
and rate limiting all depend on this ordering guarantee.
"""


class CircularQueue:
    """
    Fixed-size queue backed by an array with modular indexing.

    Why circular? A naive array queue has O(n) dequeue because you shift
    every element left. By tracking head/tail pointers and wrapping them
    with modular arithmetic, both enqueue and dequeue become O(1).

    Why fixed-size? Bounded queues prevent memory exhaustion. In production
    systems (LMAX Disruptor, Linux kernel ring buffers), bounded buffers
    give predictable latency — no malloc/GC during operation.
    """

    def __init__(self, capacity):
        self._data = [None] * capacity  # Pre-allocate — no resizing
        self._capacity = capacity
        self._head = 0   # Index of front element
        self._tail = 0   # Index of next empty slot
        self._size = 0   # Tracks count to distinguish full vs empty
        # Without _size, head == tail is ambiguous: could be full or empty.
        # Alternative: waste one slot (full when (tail+1) % cap == head).
        # We use size because it's simpler to reason about.

    def enqueue(self, item):
        """Add to the back. O(1)."""
        if self._size == self._capacity:
            raise OverflowError("Queue is full")
        self._data[self._tail] = item
        # Modular wrap: when tail reaches end, it wraps to 0.
        # Same math as clock arithmetic: 11 + 2 = 1 (mod 12).
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1

    def dequeue(self):
        """Remove from the front. O(1)."""
        if self._size == 0:
            raise IndexError("Queue is empty")
        item = self._data[self._head]
        self._data[self._head] = None  # Help GC, prevent stale references
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        return item

    def peek(self):
        """Look at front without removing. O(1)."""
        if self._size == 0:
            raise IndexError("Queue is empty")
        return self._data[self._head]

    def is_empty(self):
        return self._size == 0

    def is_full(self):
        return self._size == self._capacity

    def __len__(self):
        return self._size

    def __repr__(self):
        # Reconstruct logical order from physical array
        items = []
        idx = self._head
        for _ in range(self._size):
            items.append(repr(self._data[idx]))
            idx = (idx + 1) % self._capacity
        return f"CircularQueue([{', '.join(items)}])"


class _Node:
    """Singly-linked node. Minimal — just data and a next pointer."""
    __slots__ = ('data', 'next')  # Save memory: no __dict__ per node

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedQueue:
    """
    Unbounded queue using a singly-linked list.

    Why linked? When you don't know the max size upfront, a linked queue
    grows on demand. Trade-off: each node is a separate allocation (GC
    pressure, cache misses), unlike the contiguous circular buffer.

    We maintain both head and tail pointers so enqueue and dequeue are O(1).
    Without a tail pointer, enqueue would be O(n) — you'd walk the entire list.
    """

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def enqueue(self, item):
        """Add to the back via tail pointer. O(1)."""
        node = _Node(item)
        if self._tail is None:
            # Empty queue: head and tail both point to the single node
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def dequeue(self):
        """Remove from the front via head pointer. O(1)."""
        if self._head is None:
            raise IndexError("Queue is empty")
        item = self._head.data
        self._head = self._head.next
        if self._head is None:
            # Queue became empty — tail must also be None
            # Forgetting this is a classic bug: stale tail reference
            self._tail = None
        self._size -= 1
        return item

    def peek(self):
        if self._head is None:
            raise IndexError("Queue is empty")
        return self._head.data

    def is_empty(self):
        return self._head is None

    def __len__(self):
        return self._size

    def __repr__(self):
        items = []
        current = self._head
        while current:
            items.append(repr(current.data))
            current = current.next
        return f"LinkedQueue([{', '.join(items)}])"


class PriorityTaskScheduler:
    """
    Simple priority queue using sorted insertion.

    Why not heaps? Heaps are Day 35+. This teaches the concept first:
    - Enqueue: O(n) — find the right position by priority
    - Dequeue: O(1) — highest priority is always at the front

    In production you'd use a binary heap (O(log n) both ops), but
    understanding the naive version shows WHY heaps were invented:
    sorted insertion doesn't scale.

    Real-world: OS task schedulers, hospital triage, network QoS.
    """

    def __init__(self):
        # Stored sorted by priority (highest priority = lowest number at front)
        self._tasks = []

    def add_task(self, name, priority):
        """
        Insert task in sorted position. O(n) because we shift elements.
        Lower priority number = higher priority (like Unix nice values).
        """
        task = (priority, name)
        # Linear scan to find insertion point
        # Why not bisect? We're teaching the concept, not optimizing yet.
        inserted = False
        for i in range(len(self._tasks)):
            if priority < self._tasks[i][0]:
                self._tasks.insert(i, task)
                inserted = True
                break
        if not inserted:
            self._tasks.append(task)

    def get_next_task(self):
        """Dequeue highest-priority task. O(1) since list is sorted."""
        if not self._tasks:
            raise IndexError("No tasks in scheduler")
        priority, name = self._tasks.pop(0)
        return name, priority

    def peek_next(self):
        if not self._tasks:
            raise IndexError("No tasks in scheduler")
        priority, name = self._tasks[0]
        return name, priority

    def is_empty(self):
        return len(self._tasks) == 0

    def __len__(self):
        return len(self._tasks)

    def __repr__(self):
        tasks_str = ", ".join(f"{name}(p={p})" for p, name in self._tasks)
        return f"PriorityTaskScheduler([{tasks_str}])"


def bfs(graph, start):
    """
    Breadth-First Search — THE canonical queue algorithm.

    Why BFS needs a queue: the queue ensures we process ALL nodes at
    distance d before ANY node at distance d+1. This level-by-level
    guarantee is what gives BFS its shortest-path property in
    unweighted graphs.

    If you replaced the queue with a stack, you'd get DFS — completely
    different traversal order, no shortest-path guarantee.

    Returns:
        visited_order: list of nodes in BFS traversal order
        distances: dict mapping each node to its distance from start
    """
    # We use our own LinkedQueue to prove it works
    queue = LinkedQueue()
    queue.enqueue(start)

    visited = {start}
    visited_order = [start]
    distances = {start: 0}

    while not queue.is_empty():
        node = queue.dequeue()
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                visited_order.append(neighbor)
                distances[neighbor] = distances[node] + 1
                queue.enqueue(neighbor)

    return visited_order, distances


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("CIRCULAR QUEUE DEMO")
    print("=" * 60)

    cq = CircularQueue(5)
    for i in range(1, 6):
        cq.enqueue(i * 10)
        print(f"  enqueue({i * 10}): {cq}")

    print(f"\n  Full? {cq.is_full()}")

    try:
        cq.enqueue(99)
    except OverflowError as e:
        print(f"  enqueue(99) -> OverflowError: {e}")

    print()
    for _ in range(3):
        val = cq.dequeue()
        print(f"  dequeue() -> {val}: {cq}")

    # Wrap-around: enqueue into the freed slots
    cq.enqueue(60)
    cq.enqueue(70)
    print(f"\n  After wrap-around enqueues: {cq}")

    print("\n" + "=" * 60)
    print("LINKED QUEUE DEMO")
    print("=" * 60)

    lq = LinkedQueue()
    for item in ["alpha", "beta", "gamma", "delta"]:
        lq.enqueue(item)
    print(f"  After enqueues: {lq}")

    while not lq.is_empty():
        print(f"  dequeue() -> {lq.dequeue()}")

    print("\n" + "=" * 60)
    print("PRIORITY TASK SCHEDULER DEMO")
    print("=" * 60)

    scheduler = PriorityTaskScheduler()
    tasks = [
        ("Send email", 3),
        ("Fix crash", 1),       # Highest priority
        ("Update docs", 5),
        ("Deploy hotfix", 1),   # Same priority as Fix crash
        ("Code review", 2),
    ]
    for name, priority in tasks:
        scheduler.add_task(name, priority)
        print(f"  add_task('{name}', priority={priority})")

    print(f"\n  Scheduler state: {scheduler}")
    print("\n  Processing order (highest priority first):")
    while not scheduler.is_empty():
        name, priority = scheduler.get_next_task()
        print(f"    [{priority}] {name}")

    print("\n" + "=" * 60)
    print("BFS DEMO")
    print("=" * 60)

    # Graph: a simple social network
    #   A -- B -- D
    #   |    |
    #   C -- E -- F
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'E'],
        'D': ['B'],
        'E': ['B', 'C', 'F'],
        'F': ['E'],
    }

    print("  Graph (adjacency list):")
    for node, neighbors in sorted(graph.items()):
        print(f"    {node} -> {neighbors}")

    order, dist = bfs(graph, 'A')
    print(f"\n  BFS from 'A': {order}")
    print(f"  Distances:    {dist}")
    print(f"\n  Shortest path A->F: {dist['F']} hops")
    # Why this works: BFS guarantees that when we first reach F,
    # we've taken the minimum number of edges to get there.
