# Day 24: Skip Lists

## Why This Exists

Redis — the most widely deployed in-memory data store — uses skip lists as its primary sorted data structure (sorted sets / ZSET). When Salvatore Sanfilippo (antirez) designed Redis, he chose skip lists over red-black trees for a reason: skip lists are simpler to implement, easier to reason about concurrently, and offer the same expected time complexity without the nightmare of rotation-based rebalancing.

Beyond Redis, skip lists appear in:
- **LevelDB / RocksDB**: The memtable (in-memory write buffer) is a skip list — every write to these storage engines hits a skip list first.
- **Apache Lucene**: Uses skip lists for posting list intersection in full-text search.
- **Concurrent programming**: Lock-free skip lists (like Java's `ConcurrentSkipListMap`) are far easier to build than lock-free balanced trees.

The core insight: instead of deterministic balancing (rotations, color flips), skip lists use **randomness** to achieve balance **in expectation**. This is a fundamentally different approach to the same problem — and understanding both approaches makes you a better engineer.

---

## Theory (40 min)

### What Is a Skip List?

A skip list is a layered linked list where higher layers act as "express lanes" that let you skip over large portions of the data.

```
Level 3:  HEAD -----------------------------------------> 50 -> NIL
Level 2:  HEAD -----------------> 20 ------------------> 50 -> NIL
Level 1:  HEAD -------> 10 -----> 20 -------> 40 ------> 50 -> NIL
Level 0:  HEAD -> 5 -> 10 -> 15 -> 20 -> 30 -> 40 -> 45 -> 50 -> NIL
```

- **Level 0** contains every element (it's a sorted linked list).
- Each higher level is a subset of the level below.
- A node at level `k` has `k+1` forward pointers (one for each level 0..k).

### Probabilistic Balancing via Coin Flips

When inserting a new node, we decide its height by flipping a (biased) coin:

```
level = 0
while random() < p and level < MAX_LEVEL:
    level += 1
```

With `p = 0.5`:
- 100% of nodes are at level 0
- ~50% are at level 1
- ~25% are at level 2
- ~12.5% are at level 3
- ...

This creates a geometric distribution. The expected number of nodes at level `k` is `n * p^k`. This mimics the structure of a balanced binary tree — each level roughly halves the search space — but without any deterministic rebalancing.

### Search Algorithm

To find key `k`:
1. Start at the highest level of the head node.
2. Move forward while the next node's key < `k`.
3. When you can't move forward, drop down one level.
4. Repeat until level 0. Check if you've found `k`.

This is analogous to binary search: each level skip roughly halves the remaining elements.

### Expected Complexity

| Operation | Expected  | Worst Case |
|-----------|-----------|------------|
| Search    | O(log n)  | O(n)       |
| Insert    | O(log n)  | O(n)       |
| Delete    | O(log n)  | O(n)       |
| Space     | O(n)      | O(n log n) |

**Why O(log n) expected?** At each level, you traverse at most `1/p` nodes on average before dropping down. With `log_{1/p}(n)` levels, total comparisons = `O((1/p) * log_{1/p}(n))` = `O(log n)`.

**Space**: Each node has on average `1/(1-p)` pointers. With `p = 0.5`, that's 2 pointers per node on average, so expected space is `O(2n) = O(n)`.

### Skip Lists vs Balanced BSTs (Red-Black Trees)

| Dimension               | Skip List                         | Red-Black Tree                 |
|--------------------------|-----------------------------------|--------------------------------|
| **Implementation**       | ~100 lines                        | ~300+ lines (rotations, cases) |
| **Balancing**            | Probabilistic (coin flips)        | Deterministic (rotations)      |
| **Concurrency**          | Easy lock-free versions exist     | Lock-free is extremely hard    |
| **Range queries**        | Natural (walk level 0)            | Requires in-order traversal    |
| **Cache behavior**       | Worse (pointer chasing)           | Better (tree locality)         |
| **Worst case**           | O(n) — astronomically unlikely    | O(log n) guaranteed            |
| **Memory per node**      | ~2 pointers avg (p=0.5)          | 3 pointers + color bit         |

### Why Redis Chose Skip Lists

From antirez himself (paraphrased):
1. **Simpler to implement** — fewer bugs, easier to maintain.
2. **Range operations are natural** — ZRANGEBYSCORE just walks level 0.
3. **Easy to modify** — changing the balancing probability or max level is trivial.
4. **Good enough performance** — the constant factors are similar to red-black trees in practice.
5. **Easier to debug** — the structure is visually intuitive.

---

## Practice (20 min)

Open `skip_list.py` and study the implementation. Then open `practice.py` and complete:

1. **Range query** — find all keys in [lo, hi] efficiently using the skip list structure.
2. **K-th smallest** — find the k-th smallest element (think about what extra data you need).
3. **Iterator** — build an in-order iterator over level 0.
4. **Benchmark** — compare skip list search vs Python's bisect on a sorted list.

---

## Daily Project

Implement a simple **in-memory sorted key-value store** using your skip list:
- `PUT key value` — insert or update
- `GET key` — retrieve value
- `DEL key` — delete
- `RANGE lo hi` — return all key-value pairs where lo <= key <= hi
- `RANK key` — return the 0-based rank of the key

This is essentially a mini Redis ZSET.

---

## Checkpoint Questions

**Q1: Why does a skip list use randomness instead of deterministic balancing?**

> Randomness eliminates the need for complex rebalancing operations (rotations, splits, color flips). The coin-flip approach achieves O(log n) expected time with much simpler code. The trade-off is that worst-case is O(n), but the probability of a bad structure decreases exponentially — for practical purposes it never happens.

**Q2: What is the expected height of a skip list with n elements and promotion probability p = 0.5?**

> Expected max level = log_{1/p}(n) = log_2(n). For 1 million elements, that's about 20 levels. This is why MAX_LEVEL is typically set to 16-32 — it's more than enough.

**Q3: How does search in a skip list compare to binary search on a sorted array?**

> Both are O(log n). Binary search on an array has better cache performance (contiguous memory) and is simpler. But a sorted array has O(n) insertion/deletion (shifting elements). Skip lists give O(log n) for all operations while supporting efficient range queries — they win when the data is dynamic.

**Q4: Why are skip lists preferred over balanced BSTs for concurrent data structures?**

> In a balanced BST, rebalancing after insert/delete can cascade through many nodes (rotations propagate up the tree), requiring locks on a large portion of the structure. In a skip list, insert only modifies local pointers at each level — the "rebalancing" (random level assignment) is decided at insert time with no propagation. This makes lock-free and fine-grained locking implementations much simpler.

**Q5: What happens if you set the promotion probability p to 1.0? To 0.0?**

> With p = 1.0, every node would be promoted to every level — you'd get n copies of the full list stacked on top of each other. Search degrades to O(n) with O(n * MAX_LEVEL) space. With p = 0.0, no node is ever promoted — you get a plain linked list at level 0. Search is O(n). The sweet spot is p = 0.25 to 0.5, balancing speed vs space. Redis uses p = 0.25 (ZSKIPLIST_P) to save memory.
