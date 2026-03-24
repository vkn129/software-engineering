# Day 33: Min-Stack / Max-Queue

## Why This Exists

Every monitoring dashboard, streaming analytics pipeline, and trading system needs the same
primitive: **track an extreme value (min or max) over a changing window of data — fast.**

Real examples:
- **Server monitoring**: "What's the minimum response time in the last 5 minutes?" You can't
  re-scan millions of data points every second.
- **Stock trading**: "What's the max price seen since market open?" Must be O(1) per query
  because latency = money.
- **Streaming median / percentiles**: The building block for sliding-window statistics is a
  structure that maintains order information as elements arrive and leave.

The naive approach — scan the entire collection on every query — is O(n). We need O(1).

## Theory

### Min-Stack with Auxiliary Stack

**Core insight**: A stack only removes from the top. So the minimum of the elements *below*
any given element never changes while that element is on the stack.

We keep a second "min stack" where each entry records the minimum of all elements from the
bottom up to that position.

| Operation | Time | Space |
|-----------|------|-------|
| push      | O(1) | O(n) extra worst-case |
| pop       | O(1) | — |
| top       | O(1) | — |
| get_min   | O(1) | — |

**Why not just store a single variable?** Because when you pop the current minimum, you'd
need to scan the whole stack to find the new minimum — back to O(n).

**Space optimization**: Only push onto the min-stack when the new element is <= current min.
Pop from it only when the popped value equals the current min. Worst-case space is still O(n)
(descending input), but average-case is much better.

### Max-Queue with Two Stacks — Amortized O(1)

A queue is FIFO, but we want O(1) max. The trick uses two ideas:

1. **Queue from two stacks**: One "in-stack" for enqueue, one "out-stack" for dequeue.
   When out-stack is empty, reverse in-stack into out-stack. Each element is moved at most
   once, so amortized O(1) per operation.

2. **Each stack tracks its own max**: Both the in-stack and out-stack are min/max-stacks.
   The queue's max is simply `max(in_stack.max, out_stack.max)`.

**Amortization argument**: Every element enters in-stack exactly once and leaves out-stack
exactly once. The "expensive" transfer (popping all of in-stack into out-stack) happens
only when out-stack is empty. Over n operations, total work is O(n) => O(1) amortized.

### Lazy vs Eager Tracking

| Strategy | How it works | Trade-off |
|----------|-------------|-----------|
| **Eager** | Update the extreme on every push/pop | O(1) query, but pop may be O(n) if you only stored one variable |
| **Lazy (auxiliary stack)** | Store per-position extremes | O(1) everything, O(n) extra space |
| **Lazy (monotonic deque)** | Only keep "useful" candidates | O(1) amortized, less space on average |

The auxiliary-stack approach is the sweet spot for stacks: simple, O(1) worst-case, easy to reason about.

## Practice

See `practice.py` for four exercises:

1. **MinMaxStack** — O(1) push, pop, getMin, AND getMax simultaneously
2. **Sliding window median** — two-heap preview using the min/max tracking idea
3. **Online stock span** — using a max-stack to look backward efficiently
4. **Validate stack sequences** — given push/pop sequences, determine if they're valid

## Checkpoint Questions

1. Why can't a single variable replace the auxiliary min-stack?
   > Because popping the current min leaves you with no record of the *previous* min.

2. What's the worst-case space for the auxiliary min-stack, and when does it happen?
   > O(n) extra, when elements arrive in non-increasing order (every element is a new min).

3. Why does the two-stack queue give amortized O(1) and not worst-case O(1)?
   > The transfer from in-stack to out-stack is O(k) for k elements, but each element
   > is transferred at most once across all operations, so total cost is O(n).

4. Could you build an O(1) worst-case min-queue? How?
   > Yes — use a monotonic deque (decreasing for max, increasing for min). Elements that
   > can never be the answer are discarded eagerly. This gives O(1) worst-case for all ops.

5. How does this connect to sliding-window problems?
   > A sliding window is conceptually a queue (elements enter from one end, leave from the
   > other). A max-queue lets you track the window's max/min as it slides — the foundation
   > of problems like "sliding window maximum."
