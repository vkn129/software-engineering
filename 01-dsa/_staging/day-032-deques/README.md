# Day 12: Deques -- Double-Ended Queues

## Why This Exists

Stacks give you O(1) at one end. Queues give you O(1) at opposite ends -- but only in one direction. A deque (pronounced "deck") gives you O(1) insertion and removal at BOTH ends. This sounds like a minor extension, but it unlocks an entire class of algorithms that neither stacks nor queues can handle efficiently.

The sliding window maximum problem appears constantly in real systems: "What is the maximum stock price in the last 5 minutes?" "What is the peak CPU load over the last 60 seconds?" "What is the largest request latency in the current monitoring window?" A naive approach recomputes the maximum over the entire window every time it slides -- O(n*k) for n elements and window size k. A deque-based solution does it in O(n) total, which is the difference between a monitoring system that keeps up with production traffic and one that falls behind and becomes useless.

Work-stealing schedulers in Go, Java's ForkJoinPool, and Tokio (Rust's async runtime) all use deques internally. Each worker thread has its own deque of tasks. It pushes and pops from one end (like a stack, for cache locality), but OTHER threads can steal from the opposite end when they run out of work. This is one of the most important concurrency patterns in modern computing, and it fundamentally requires a double-ended data structure.

Python's `collections.deque` is also the correct replacement for using a `list` as a queue. Calling `list.pop(0)` is O(n) because every element must shift left. `deque.popleft()` is O(1). If you have ever used `list.pop(0)` in production code, you have written an O(n) operation where an O(1) operation exists.

## Theory (40 min)

### 1. What Is a Deque?

A deque is a linear data structure that supports four core operations, all in O(1) time:

```
               Front                    Back
                |                        |
                v                        v
push_front -> [A] [B] [C] [D] [E] <- push_back
pop_front  <- [A] [B] [C] [D] [E] -> pop_back
```

- `push_front(x)` -- insert at the front
- `push_back(x)` -- insert at the back
- `pop_front()` -- remove from the front
- `pop_back()` -- remove from the back
- `peek_front()` / `peek_back()` -- look without removing

A deque subsumes both stacks (use only one end) and queues (push at one end, pop at the other).

### 2. Implementation: Doubly Linked List

The simplest way to get O(1) at both ends is a doubly linked list:

```
 None <-- [prev|A|next] <--> [prev|B|next] <--> [prev|C|next] --> None
           ^                                       ^
           head                                    tail
```

Every node has `prev` and `next` pointers. We maintain `head` and `tail` references. Pushing or popping at either end just updates 2-3 pointers. This gives guaranteed O(1) for all four operations.

The cost: every element carries two pointer overheads (16 bytes each on 64-bit systems), and nodes are scattered across memory, causing cache misses. For small elements, the pointers may use more memory than the data itself.

### 3. Implementation: Circular Buffer

An array-based approach with two indices:

```
  Indices:  0   1   2   3   4   5   6   7
  Array:  [ _ ] [C] [D] [E] [F] [ _ ] [ _ ] [B]
                 ^               ^           ^
                 front           back         (wraps around)

  Logical order: B, C, D, E, F
  front = 1, back = 4, capacity = 8
```

Both `front` and `back` wrap around using modular arithmetic: `index = (index + 1) % capacity`. When the buffer is full, allocate a new array (typically 2x) and copy elements.

Advantages: contiguous memory (cache-friendly), no pointer overhead. Disadvantage: amortized O(1) for push (occasional resize), and resize copies all elements.

### 4. Python's collections.deque Internals

Python's deque is neither a simple linked list nor a simple circular buffer. It is a **doubly linked list of fixed-size blocks**, where each block is an array of 64 element pointers. This hybrid design gives:

```
  Block 0         Block 1         Block 2
  [64 slots] <--> [64 slots] <--> [64 slots]
   ^                                ^
   leftblock                        rightblock
   leftindex                        rightindex
```

- O(1) push/pop at both ends (adjust index within block, or allocate/free a block)
- Good cache locality within each 64-element block
- No massive resize operation -- just add a new block
- O(n) random access (must traverse blocks) -- `deque[i]` is NOT O(1) in the implementation, though CPython optimizes it to be fast in practice

This is why `deque` has O(1) appendleft/popleft while `list` has O(n) insert(0)/pop(0). The list must shift all elements; the deque just decrements an index.

### 5. When Deque vs. List

| Operation | list | deque |
|---|---|---|
| append (right) | O(1) amortized | O(1) |
| pop (right) | O(1) | O(1) |
| insert(0, x) / appendleft | O(n) | O(1) |
| pop(0) / popleft | O(n) | O(1) |
| Random access [i] | O(1) | O(n) |
| Slice | O(k) | not supported |

Rule: if you need fast access at both ends, use deque. If you need random access by index, use list. If you are using a list as a FIFO queue, switch to deque immediately.

### 6. Applications

**Sliding window maximum**: Maintain a deque of indices. The front of the deque is always the maximum in the current window. When the window slides, remove elements from the front that have fallen out of the window, and remove elements from the back that are smaller than the new element (they can never be the maximum). O(n) total.

**Palindrome checking**: Push all characters onto a deque. Repeatedly pop from both ends and compare. If all pairs match, it is a palindrome.

**Work-stealing schedulers**: Each thread owns a deque of tasks. The owner pushes/pops from the bottom (like a stack). Thieves steal from the top. This balances load across threads without a central coordinator.

**BFS with 0-1 weights**: When edges have weight 0 or 1, use a deque instead of a priority queue. Push weight-0 neighbors to the front, weight-1 neighbors to the back. This gives O(V+E) instead of O((V+E) log V).

## Practice (20 min)

Work through the exercises in `practice.py`. Implement deque operations and use them to solve the sliding window maximum and palindrome problems.

## Daily Project

Run `deque_impl.py` to see three complete deque implementations (doubly linked list, circular buffer, and Python's collections.deque), along with performance benchmarks comparing them. Study how the sliding window maximum algorithm works -- it is one of the most common deque-based interview questions and a pattern you will see repeatedly in production monitoring systems.

## Checkpoint Questions

1. Why is `list.pop(0)` O(n) while `deque.popleft()` is O(1)? What physically happens in memory in each case?

2. Python's deque uses 64-element blocks. What would happen if the block size were 1 (pure linked list) or infinity (pure dynamic array)? Why is 64 a good trade-off?

3. In the sliding window maximum algorithm, why do we remove elements from the BACK of the deque that are smaller than the new element? Why can we guarantee they will never be needed?

4. A work-stealing scheduler uses a deque per thread instead of a shared queue. What concurrency advantage does this provide? (Hint: think about which operations need synchronization.)

5. If you needed a deque with O(1) random access AND O(1) push/pop at both ends, could you build one? What fundamental trade-off prevents this?
