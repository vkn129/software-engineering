# Day 66: Load Factor and Rehashing

## Why This Exists

You have a hash table. You chose a size — say, 16 buckets. You start inserting items. At first, collisions are rare and everything is fast. But as the table fills up, collisions become frequent, chains grow longer, and your O(1) lookups degrade toward O(n). The question becomes: **when do you resize, and how?**

This is the load factor problem, and the answer has deep implications for both correctness and performance. Every production hash map — Python's `dict`, Java's `HashMap`, Go's `map`, Redis's hash tables — implements automatic resizing. Understanding the mechanics reveals why hash tables deliver amortized O(1) despite occasional expensive operations, and why naive implementations can cause latency spikes that crash production systems.

## Theory

### Load Factor: The Health Metric

The **load factor** (alpha) of a hash table is:

```
alpha = n / m
```

where `n` = number of items stored and `m` = number of buckets.

This single number tells you how crowded the table is:

| Load Factor | Meaning | Performance Impact |
|-------------|---------|-------------------|
| 0.0 | Empty table | Wasting memory |
| 0.25 | Sparse | Fast but memory-inefficient |
| 0.5 | Half full | Good balance |
| 0.75 | Getting crowded | Sweet spot threshold |
| 1.0 | Full (chaining) / impossible (open addressing) | Chains averaging 1 item each |
| 2.0 | Overcrowded (chaining only) | Chains averaging 2 items each |

### Why 0.75 Is the Magic Threshold

For **chaining**, the expected chain length equals the load factor. If alpha = 0.75, the average chain has 0.75 items. This means:

- **~75% of buckets** have exactly one item (or zero).
- The probability of a collision on the next insert is approximately `1 - e^(-alpha)` which at alpha = 0.75 is about **0.53** — roughly a coin flip. But the expected chain length is still under 1.
- At alpha = 1.0, every bucket has one item on average, but the **variance** means some chains are length 2-3, degrading cache performance.

The 0.75 threshold balances:
1. **Space**: only 33% overhead (m/n = 1/0.75 = 1.33 buckets per item).
2. **Time**: expected probe/chain length stays near 1.
3. **Collision probability**: ~25% chance that a given insert hits an occupied bucket (under uniform hashing, the probability that a specific bucket is occupied is n/m = 0.75, but for "any collision" the math uses the birthday problem approximation).

For **open addressing**, the situation is worse. Expected probes = `1 / (1 - alpha)`. At alpha = 0.75, that is 4 probes. At alpha = 0.9, that is 10 probes. Open-addressing tables typically resize at lower thresholds (0.5-0.7).

### Rehashing: The Expensive Necessity

When the load factor exceeds the threshold, you must **rehash**:

1. Allocate a new table with **2x** the number of buckets.
2. For every item in the old table, compute `hash(key) % new_size` and insert it into the new table.
3. Discard the old table.

This is an **O(n)** operation — you touch every item. But it happens rarely enough that the cost is amortized.

### Amortized O(1): The Accounting Argument

Think of it like a piggy bank. Each regular O(1) insert "saves" a small constant of extra work. When a rehash happens (O(n) work), the savings accumulated over the previous n/2 inserts pay for it.

Formally: if you double at every power of 2, inserting N items costs:
```
N regular inserts + (1 + 2 + 4 + 8 + ... + N) rehash work
                  = N + (2N - 1) = 3N - 1
```

So the amortized cost per insert is **3N/N = 3 = O(1)**.

This only works because the table **doubles** (geometric growth). If you grew by a fixed amount (e.g., +100 buckets each time), the amortized cost would be O(n), not O(1). This is the same reason Python lists use geometric growth for `append`.

### Shrinking: The Forgotten Direction

Most tutorials only discuss growing. But if you insert 1 million items and then delete 999,999 of them, you are left with a table of 1 million+ buckets holding 1 item. That is a massive waste of memory.

**Shrink when the load factor drops below 0.25** (one quarter full). Why 0.25 and not 0.5?

**Hysteresis**: if you shrink at 0.5 and the shrunken table has load factor 1.0 (since you halve the size), the very next insert triggers a grow. If the next operation is a delete, you shrink again. This **thrashing** — alternating grow/shrink — is O(n) per operation, destroying amortized performance.

By shrinking at 0.25, the shrunken table has load factor 0.5, which is far from both the grow threshold (0.75) and the shrink threshold (0.25). You need many inserts or deletes before the next resize. The gap between 0.25 and 0.75 is the hysteresis band.

### Incremental Rehashing: The Redis Approach

Standard rehashing is a **stop-the-world** operation. If your hash table has 10 million entries, rehashing pauses all operations while you move them. For a real-time system (database, cache server, game server), this latency spike is unacceptable.

**Redis** solves this with **incremental rehashing**:

1. Maintain **two** hash tables: `ht[0]` (old) and `ht[1]` (new, 2x size).
2. Set a migration index starting at bucket 0 of the old table.
3. On every insert/lookup/delete operation, migrate **k entries** (typically 1-10 buckets) from the old table to the new table.
4. New inserts always go into the new table.
5. Lookups check both tables (new first, then old).
6. When all old buckets are migrated, free the old table and swap.

**Trade-off**: each operation is slightly slower during migration (checking two tables, plus migration work), but no single operation is catastrophically slow. The worst-case latency is bounded by k, not n.

### Table Size: Powers of 2 vs. Primes

**Powers of 2** (16, 32, 64, ...): `hash % m` becomes `hash & (m-1)` — a single bitwise AND, which is faster than modulo. But if the hash function has patterns in low bits, collisions cluster.

**Primes** (17, 37, 79, ...): `hash % m` distributes more uniformly even with mediocre hash functions, because prime moduli break up patterns. But modulo is slower than bitwise AND.

Modern approach: use a good hash function (e.g., SipHash, used in Python 3.4+) and power-of-2 table sizes. The hash function handles distribution; the table size handles speed.

## Checkpoint Questions

1. **Why does doubling the table size give amortized O(1) inserts, but adding a fixed increment does not?** Think about the geometric series vs. arithmetic series of rehash costs.

2. **If you set the shrink threshold at 0.5 instead of 0.25, what specific sequence of operations causes O(n) amortized cost per operation?** Construct the adversarial sequence.

3. **During Redis-style incremental rehashing, why must new inserts go into the new table rather than the old one?** What would go wrong if you inserted into the old table?

4. **A hash table uses open addressing with load factor threshold 0.7. After inserting 70 items into 100 slots, a rehash occurs. What is the load factor immediately after rehashing?** (Assume new size is 200.)

5. **You have a hash table with 1 million entries and need to rehash. Your system has a 10ms latency budget per operation. If each entry takes 100ns to migrate, can you do a full rehash in one operation? How would you structure incremental rehashing to meet the latency budget?**

6. **Why do most hash table implementations use a minimum table size (e.g., 8 or 16) and never shrink below it?** What would happen if you allowed the table to shrink to size 1?
