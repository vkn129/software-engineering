# Day 32: Deques -- Double-Ended Queues

## Why This Exists

Stacks give you O(1) at one end. Queues give you O(1) at opposite ends -- but only in one direction. A deque (pronounced "deck") gives you O(1) insertion and removal at BOTH ends. This sounds like a minor extension, but it unlocks an entire class of algorithms that neither stacks nor queues can handle efficiently.

**Sliding window maximum** appears constantly in real systems: "What is the maximum stock price in the last 5 minutes?" "What is the peak CPU load over the last 60 seconds?" "What is the largest request latency in the current monitoring window?" A naive approach recomputes the maximum over the entire window every time it slides -- O(n*k) for n elements and window size k. A deque-based solution does it in O(n) total, which is the difference between a monitoring system that keeps up with production traffic and one that falls behind and becomes useless.

**Work-stealing schedulers** in Go, Java's ForkJoinPool, and Tokio (Rust's async runtime) all use deques internally. Each worker thread has its own deque of tasks. It pushes and pops from one end (like a stack, for cache locality), but OTHER threads can steal from the opposite end when they run out of work. This is one of the most important concurrency patterns in modern computing, and it fundamentally requires a double-ended data structure.

Python's `collections.deque` is also the correct replacement for using a `list` as a queue. Calling `list.pop(0)` is O(n) because every element must shift left. `deque.popleft()` is O(1). If you have ever used `list.pop(0)` in production code, you have written an O(n) operation where an O(1) operation exists.

## Theory

### 1. Double-Ended Operations

A deque supports four core operations, all in O(1) time:

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

A deque subsumes both stacks (use only one end) and queues (push at one end, pop at the other). This generality is not just theoretical -- every deque algorithm exploits the ability to manipulate both ends.

### 2. Implementation: Doubly Linked List

The simplest way to get O(1) at both ends:

```
 None <-- [prev|A|next] <--> [prev|B|next] <--> [prev|C|next] --> None
           ^                                       ^
           head                                    tail
```

Every node has `prev` and `next` pointers. We maintain `head` and `tail` references. Pushing or popping at either end updates 2-3 pointers, giving guaranteed O(1) for all four operations.

The cost: every element carries two pointer overheads (16 bytes each on 64-bit systems), and nodes are scattered across memory, causing cache misses. For small elements, the pointers may use more memory than the data itself.

### 3. Implementation: Circular Buffer Deque

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

**Why modular arithmetic works**: The circular buffer is conceptually a ring. Position `i` maps to physical index `(front + i) % capacity`. This avoids ever shifting elements -- the "empty" slots rotate around the buffer as elements are pushed and popped from different ends.

**Resize strategy**: When full, double the capacity. This means resize happens after 8, 16, 32, 64... insertions. The total copy cost across n insertions is 8 + 16 + 32 + ... + n = O(n), so amortized cost per insertion is O(1).

Advantages: contiguous memory (cache-friendly), no pointer overhead, O(1) random access. Disadvantage: amortized O(1) for push (occasional resize copies all elements).

### 4. How collections.deque Works Internally

Python's deque is neither a simple linked list nor a simple circular buffer. It is a **doubly linked list of fixed-size blocks**, where each block is an array of 64 element pointers:

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
- O(n) random access (must traverse blocks) -- `deque[i]` walks through blocks

This hybrid captures the best of both worlds: linked-list flexibility at the block level, array cache-friendliness within blocks. The block size of 64 is a sweet spot -- large enough for cache efficiency, small enough that allocating a new block is cheap.

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

### 6. Sliding Window Maximum -- O(n) with Deque

This is the canonical deque algorithm. Maintain a deque of indices where values are in **decreasing** order:

```
Array: [1, 3, -1, -3, 5, 3, 6, 7],  k=3

Step 0: i=0, val=1   deque=[0]          (just 1)
Step 1: i=1, val=3   deque=[1]          (3 > 1, pop 0, push 1)
Step 2: i=2, val=-1  deque=[1,2]        window full -> max=arr[1]=3
Step 3: i=3, val=-3  deque=[1,2,3]      max=arr[1]=3
Step 4: i=4, val=5   deque=[4]          (5 > all, clear and push 4) max=5
Step 5: i=5, val=3   deque=[4,5]        max=5
Step 6: i=6, val=6   deque=[6]          max=6
Step 7: i=7, val=7   deque=[7]          max=7

Result: [3, 3, 5, 5, 6, 7]
```

**Key insight**: if `arr[j] >= arr[i]` and `j > i`, then `arr[i]` can NEVER be the maximum of any future window (because `arr[j]` is both larger and will stay in the window longer). So we discard `arr[i]` from the back of the deque.

Each element enters and leaves the deque at most once, so total work is O(n).

The same pattern works for **sliding window minimum** by maintaining values in increasing order instead.

### 7. Applications

- **Sliding window max/min**: Monitoring, streaming analytics, stock analysis
- **Palindrome checking**: Pop from both ends and compare
- **Work-stealing schedulers**: Owner pushes/pops from bottom, thieves steal from top
- **0-1 BFS**: Weight-0 edges push to front, weight-1 edges push to back -- O(V+E) instead of Dijkstra's O((V+E) log V)
- **Shortest subarray with sum >= target**: Deque maintains candidates for optimal left boundary
- **Constrained sliding windows**: Max-min deques track range constraints in O(n)

## Practice

Work through the 5 exercises in `practice.py`:
1. Palindrome checker using deque
2. Max of all subarrays of size k (sliding window maximum)
3. First negative in every window of size k
4. Shortest subarray with sum >= target
5. Longest subarray with abs diff <= limit

## Daily Project

Run `deque_impl.py` to see the ArrayDeque (circular buffer) implementation with push/pop at both ends, automatic resizing, and both sliding window maximum and minimum algorithms. Includes performance benchmarks against `collections.deque`.

## Checkpoint Questions

1. Why is `list.pop(0)` O(n) while `deque.popleft()` is O(1)? What physically happens in memory in each case?

2. In a circular buffer deque, what happens when `front` is at index 0 and you call `push_front`? Trace the modular arithmetic.

3. Python's deque uses 64-element blocks. What would happen if the block size were 1 (pure linked list) or infinity (pure dynamic array)? Why is 64 a good trade-off?

4. In the sliding window maximum algorithm, why do we remove elements from the BACK of the deque that are smaller than the new element? Why can we guarantee they will never be needed?

5. A work-stealing scheduler uses a deque per thread instead of a shared queue. What concurrency advantage does this provide? (Hint: think about which operations need synchronization.)

6. How would you modify the sliding window maximum to compute sliding window minimum? What changes in the deque invariant?

7. If you needed a deque with O(1) random access AND O(1) push/pop at both ends, could you build one? What fundamental trade-off prevents this?
