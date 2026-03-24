# Day 31: Queue

## Why This Exists

Queues enforce **fairness** — first-come, first-served. This constraint appears everywhere:

- **BFS (Breadth-First Search)**: Explore nodes level by level. Without a queue, you cannot guarantee shortest-path discovery in unweighted graphs. BFS is the canonical queue algorithm.
- **Message Queues**: Kafka, RabbitMQ, SQS — producers enqueue work, consumers dequeue it. Decouples systems in time and space. Without FIFO ordering, you lose causal consistency.
- **CPU Scheduling**: OS ready queues decide which process runs next. Round-robin scheduling is literally a circular queue. Priority queues extend this for real-time deadlines.
- **Rate Limiting / Sliding Windows**: "How many requests in the last N milliseconds?" is a queue problem — enqueue timestamps, dequeue expired ones.
- **Print Spoolers, IO Buffers, Network Packets**: Anything where arrival order must equal processing order.

The deeper insight: **stacks model function calls (depth), queues model workflows (breadth)**. Every system that coordinates independent actors needs queues.

## Theory

### FIFO (First-In, First-Out)

The defining property. Two operations:
- `enqueue(item)` — add to the back
- `dequeue()` — remove from the front

Both must be O(1) for the queue to be useful. If either is O(n), you have a list pretending to be a queue.

### Circular Buffer with Modular Indexing

The array-based queue problem: naive dequeue shifts all elements (O(n)). Solution — don't shift, just move the head pointer forward.

```
Physical array: [_, _, C, D, E, _, _]
                      ^head    ^tail

After enqueue(F):    [_, _, C, D, E, F, _]
                           ^head       ^tail

After dequeue():    [_, _, _, D, E, F, _]
                           ^head    ^tail
```

When tail reaches the end, wrap around: `tail = (tail + 1) % capacity`. This is **modular arithmetic** — the same math behind clock arithmetic, hash tables, and ring buffers in networking.

**Full vs. Empty ambiguity**: When `head == tail`, is the queue full or empty? Two solutions:
1. Track a `size` counter (simple, what we implement)
2. Waste one slot — full when `(tail + 1) % capacity == head`

**Why fixed-size?** Bounded queues prevent memory exhaustion. In production systems (Disruptor, LMAX), bounded ring buffers give predictable latency because no malloc/GC happens during operation.

### Linked Queue

Each node points to the next. Enqueue at tail, dequeue at head. Both O(1) with head and tail pointers.

**Trade-offs vs. circular buffer:**
| | Circular Buffer | Linked Queue |
|---|---|---|
| Memory | Contiguous, cache-friendly | Scattered nodes, pointer overhead |
| Size | Fixed (or resize = O(n) copy) | Unbounded (until OOM) |
| Allocation | One upfront | Per-enqueue (GC pressure) |
| Use case | Known max size, low latency | Unknown size, simplicity |

### BFS: The Canonical Queue Algorithm

```
BFS(graph, start):
    queue = [start]
    visited = {start}
    while queue not empty:
        node = dequeue()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                enqueue(neighbor)
```

Why BFS needs a queue: the queue ensures we process all nodes at distance `d` before any node at distance `d+1`. A stack would give DFS instead — completely different traversal order.

BFS gives **shortest path in unweighted graphs** because of this level-by-level guarantee. This is why network routing (OSPF), social network "degrees of separation", and puzzle solvers (Rubik's cube) all use BFS.

## Practice

See `queue_impl.py` for implementations:
- `CircularQueue` — fixed array with modular indexing
- `LinkedQueue` — pointer-based, unbounded
- `PriorityTaskScheduler` — sorted insertion (O(n) enqueue, O(1) dequeue)
- BFS graph traversal demo

See `practice.py` for exercises:
1. Queue using two stacks
2. Stack using two queues
3. Generate binary numbers 1 to n
4. Hot potato / Josephus simulation
5. Recent counter (sliding window)

## Checkpoint Questions

1. **Why is dequeue from a Python list O(n)?** — `list.pop(0)` shifts every element left. `collections.deque` uses a doubly-linked list of fixed blocks, giving O(1) popleft.

2. **When would you choose a circular buffer over a linked queue?** — When you know the max size upfront and need predictable latency (no allocation during operation). Examples: audio buffers, network packet rings, LMAX Disruptor.

3. **Why does BFS guarantee shortest path in unweighted graphs but not weighted?** — BFS processes nodes in order of hop count. In weighted graphs, fewer hops doesn't mean shorter distance. You need Dijkstra (priority queue) for weighted shortest paths.

4. **What happens if your circular queue's capacity is a power of 2?** — You can replace `% capacity` with `& (capacity - 1)`, which is faster. This is why real ring buffers (Linux kernel, Disruptor) use power-of-2 sizes.

5. **How do message queues like Kafka differ from in-memory queues?** — Persistence (survives restarts), distribution (multiple consumers), partitioning (parallel consumption), and offset tracking (consumers control their position). But the core abstraction is still FIFO enqueue/dequeue.
