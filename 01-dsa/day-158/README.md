# Day 158: Skip List Revisited — Why Redis Chose It

We built a skip list back in the basics phase. Now we revisit with the
question that matters in practice: **why does Redis use skip lists instead of
a red-black tree** for sorted sets (ZSET)? The answer reveals real engineering
trade-offs.

## Quick Recap

A skip list is a probabilistic alternative to balanced BSTs. Multiple "express
lanes" let you skip elements. Each node is promoted to higher levels with
probability `p` (typically 0.5).

```
L3: ──────────────────────────────►
L2: ─────────►───────────►─────────►
L1: ──►───►───►───►───►───►───►───►
L0: a   b   c   d   e   f   g   h
```

Search: start at top-left, drop down when overshoot. Expected O(log n)
comparisons. Insert: search + flip coins for promotion. Same bound.

## The Operations We Add Today

These are the operations Redis ZSET actually needs:

1. **Range queries**: "give me elements with score in [a, b]" — used for sorted-set scans.
2. **Rank queries**: "what's the position of element x?" — used for `ZRANK`.
3. **Range by rank**: "give me elements at positions 100 to 200" — used for `ZRANGE`.

Each requires keeping a **span** (number of L0 nodes skipped) on every
forward pointer. This is the key implementation detail.

## Skip List vs Red-Black Tree

| Aspect | Skip List | Red-Black Tree |
|---|---|---|
| **Avg search/insert** | O(log n) | O(log n) |
| **Worst case** | O(n) (extremely rare; ~10^-18 for n=2^31) | O(log n) deterministic |
| **Memory** | ~1.33n pointers (avg) | 2n pointers + color bit |
| **Cache locality** | Worse — random forward pointer jumps | Worse — pointer chasing too |
| **Implementation** | ~100 lines, no rotations | ~400+ lines, 6 rebalance cases |
| **Range queries** | Trivial — walk L0 | Need in-order traversal |
| **Rank queries** | Need span pointers (Redis does this) | Need size annotations |
| **Concurrency** | Lock-free implementations exist | Hard to make lock-free |

## Why Redis Picked Skip List (Antirez's stated reasons)

From Antirez (Salvatore Sanfilippo, Redis creator):

> "Skip lists are very simple to implement, debug, and modify."

> "Skip lists are more efficient in memory than balanced trees in the average
> case... and the average case is what matters."

> "Range operations on a skip list are as simple as walking a linked list."

> "I cannot make a balanced tree both simple AND efficient at the same time
> for sorted set operations."

The dominant Redis ZSET operations are:
- `ZRANGE key 0 -1` — full range scan
- `ZRANGEBYSCORE` — score-range scan
- `ZADD` / `ZREM` — point updates

Skip lists win on all of them in **wall-clock simplicity**.

## What We Measure Today

Honest benchmark: skip list vs an open-source-equivalent RB-tree implementation
(reused from day 47 conceptually; here we use Python's `SortedList` as a
balanced-tree-equivalent proxy, since it's a B-tree-based structure with
identical big-O).

Specifically:
- **Insert** N random elements
- **Lookup** N random elements
- **Range scan** of size K

Expect: comparable orders of magnitude. The point isn't to crown a winner —
it's to verify that the **average case** is competitive while the code is
half the length.

## The Probabilistic Argument

Why doesn't the worst case (a tall tower of promotions) actually happen?

Probability that a single node reaches level k is `p^k = (1/2)^k`. Probability
that *no* node in a sequence of n reaches level k is `(1 - p^k)^n`. Pick
`k = c log n`. Then height tail is `≈ n / 2^(c log n) = n^(1-c)`, which
vanishes for `c > 1`.

For n = 1 billion, the probability of a 100-level tower is about 10^-18 —
less likely than a CPU cosmic-ray bit flip.

## The Real Reason: Engineering Culture

Antirez explicitly said he picked the data structure that was **easy to debug
at 3am during an outage**. That's the kind of decision experienced engineers
make. The RB-tree's worst-case guarantee is a guarantee about pathological
inputs that don't exist; the skip list's expected-case guarantee is a
guarantee about the actual operating regime.

The phrase that matters: "Choose the algorithm whose **failure mode** you can
debug."

## Checkpoint Questions

1. Span pointers: at each level, why is the span equal to the sum of L0-distances skipped, not just the number of upper-level steps?
2. If you set p = 1/4 instead of p = 1/2, what changes? (Hint: memory, search time, constant factors.)
3. Construct an input that makes a skip list slow. Why is this not adversarial in practice but would be against a deterministic structure?
4. Redis cluster slots have ~16k buckets. Why is "average case" guaranteed here even more strongly than for a single skip list?
5. What's the one workload where you'd actively prefer an RB-tree over a skip list?
