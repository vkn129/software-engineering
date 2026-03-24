# Day 65: Hash Table Collision Resolution

## Why This Matters

Day 13 built hash tables with separate chaining. Now we confront the full design space: **chaining vs open addressing**. Every production hash table picks one of these families, and the choice determines memory layout, cache behavior, deletion complexity, and failure modes under load. Python's `dict` uses open addressing. Java's `HashMap` uses chaining. Rust's `HashMap` uses Robin Hood hashing. Understanding why requires understanding the trade-offs at the hardware level.

## Two Collision Strategies

### 1. Chaining (Separate Chaining)

Each bucket holds a linked list of all entries that hash to that index.

```
Bucket 0: -> (k3, v3) -> (k7, v7) -> None
Bucket 1: -> (k1, v1) -> None
Bucket 2: -> None
Bucket 3: -> (k9, v9) -> (k4, v4) -> (k2, v2) -> None
```

**How it works:**
- **Insert**: Hash the key, append to the list at that bucket. O(1) always — you never run out of space in the bucket, you just extend the chain.
- **Search**: Hash the key, walk the list comparing keys. O(chain length).
- **Delete**: Hash the key, find and unlink from the list. Standard linked list removal.

**Trade-offs:**
- Insert **never degrades** — you always just append to a list, regardless of load factor. Even at load factor 10.0, insert is O(1).
- Wastes memory on **pointers** — each node needs a `next` pointer (8 bytes on 64-bit systems). For small key-value pairs (e.g., two ints = 8 bytes), the pointer overhead doubles memory usage.
- **Poor cache locality** — following linked list pointers causes cache misses. Each node can live anywhere in the heap. Walking a chain of length 5 can mean 5 cache misses at ~100 cycles each = 500 cycles, vs 5 sequential reads at ~4 cycles each = 20 cycles.
- Load factor can exceed 1.0 — chains just get longer. The table never "fills up."

### 2. Open Addressing

All entries live directly in the table array. No pointers, no linked lists. When a collision occurs, you **probe** for the next available slot using a deterministic sequence.

#### Linear Probing
Probe sequence: `h(k), h(k)+1, h(k)+2, ...`

```
Insert key with h(k) = 3, but slot 3 is occupied:
  Try slot 4 -> occupied
  Try slot 5 -> empty, insert here
```

- **Best cache locality** — sequential memory access, CPU prefetcher loads the next cache line before you need it.
- **Primary clustering** — occupied slots form long contiguous runs. A new key hashing anywhere into a cluster extends it. A cluster of size `s` has probability `(s+1)/m` of growing by 1 on the next insert. Clusters grow quadratically — this is the fundamental weakness.

#### Quadratic Probing
Probe sequence: `h(k), h(k)+1^2, h(k)+2^2, h(k)+3^2, ...`

- Eliminates primary clustering — probes jump further apart, so hitting a cluster does not extend it linearly.
- Introduces **secondary clustering** — keys with the same hash still follow the same probe sequence, creating subtler clustering.
- Does **not** guarantee visiting all slots unless table size is prime and load factor < 0.5.

#### Double Hashing
Probe sequence: `h1(k), h1(k)+h2(k), h1(k)+2*h2(k), ...`

- Second hash function `h2(k)` determines step size, unique per key.
- Virtually eliminates all clustering — even keys with the same primary hash follow different probe sequences.
- `h2(k)` must never return 0 (infinite loop). Common choice: `h2(k) = prime - (k % prime)` where `prime < table_size`.
- Slightly worse cache performance than linear probing due to non-sequential memory access.

## The Clustering Problem in Linear Probing

Linear probing's primary clustering is a feedback loop:

1. A contiguous block of occupied slots (a "cluster") forms by chance.
2. Any new key whose hash lands **anywhere in the cluster, or at the slot just before it**, extends the cluster by one.
3. A bigger cluster captures a larger fraction of the hash space, so it grows even faster.
4. Two nearby clusters can merge into one giant cluster, making things dramatically worse.

The math: at load factor alpha, the expected number of probes for an unsuccessful search under linear probing is approximately `0.5 * (1 + 1/(1 - alpha)^2)`. At alpha = 0.9, that is ~50 probes. Under double hashing, it is `1/(1 - alpha)` = ~10 probes. The squared term in linear probing's formula is the clustering penalty.

## Tombstones for Deletion in Open Addressing

Deleting in open addressing is tricky. You cannot simply empty a slot — it would break the probe chain for keys inserted past that slot.

**Tombstone approach:**
- Mark deleted slots with a sentinel value (`DELETED` / `TOMBSTONE`).
- **Search** treats tombstones as "occupied, keep probing."
- **Insert** can reuse tombstone slots (first tombstone in the probe sequence).
- Problem: tombstones accumulate and never reduce probe lengths. A table that has seen many insert/delete cycles can have O(n) probes even at low actual load factor.
- Solution: periodic rehashing to clear tombstones, or resize triggers that count tombstones.

**Backward shift deletion (tombstone-free):**
- When deleting key at slot `i`, check if the next slot's key "belongs" at or before slot `i`.
- If yes, shift it back. Continue shifting until you hit an empty slot or a key that is already in its home position.
- No tombstones, no degradation over time, but more complex to implement correctly.

## Load Factor Analysis

| Load Factor | Linear Probing (avg probes) | Double Hashing (avg probes) | Chaining (avg chain) |
|-------------|----------------------------|-----------------------------|----------------------|
| 0.25        | ~1.17                      | ~1.15                       | 0.25                 |
| 0.50        | ~1.50                      | ~1.39                       | 0.50                 |
| 0.75        | ~2.50                      | ~1.85                       | 0.75                 |
| 0.90        | ~5.50                      | ~2.56                       | 0.90                 |
| 0.95        | ~10.50                     | ~3.15                       | 0.95                 |

Key insight: chaining degrades **linearly** with load factor. Open addressing degrades **hyperbolically** — it hits a wall as alpha approaches 1.0. This is why open addressing implementations must resize aggressively (typically at alpha = 0.5 to 0.75) while chaining can tolerate higher load factors.

## When to Use Which

| Property                | Chaining              | Open Addressing          |
|-------------------------|-----------------------|--------------------------|
| Cache performance       | Poor (pointer chasing)| Excellent (sequential)   |
| Memory overhead         | High (pointers/nodes) | Low (inline storage)     |
| Max load factor         | Can exceed 1.0        | Must stay well below 1.0 |
| Deletion complexity     | Simple (unlink node)  | Complex (tombstones/shift)|
| Worst-case insert       | O(1) always           | O(n) when nearly full    |
| Implementation          | Simpler               | More subtle edge cases   |
| Best for                | Unknown/variable load | Known, controlled load   |

**Real-world choices:**
- **Python `dict`**: open addressing with perturbation-based probing
- **Java `HashMap`**: chaining (with tree-ification at chain length 8)
- **Go `map`**: chaining with 8-entry inline buckets (bucket fits a cache line)
- **Rust `HashMap`**: Swiss Table / Robin Hood hashing (open addressing)
- **C++ `std::unordered_map`**: chaining (standard requires it)

## Checkpoint Questions

1. **Why does linear probing suffer from primary clustering but double hashing does not?** Linear probing uses a fixed step of 1 for all keys, so any key landing in a contiguous block extends that block. Double hashing uses a key-dependent step size from a second hash function, so different keys follow different probe sequences even when they collide, breaking the clustering feedback loop.

2. **Why can't you simply set a slot to empty when deleting in open addressing?** A key may have been inserted past that slot during its own probe sequence. Emptying the slot breaks the probe chain — future searches for that key would stop at the empty slot and incorrectly report "not found."

3. **At load factor 0.9, linear probing averages ~5.5 probes while chaining averages 0.9 comparisons per lookup. Why might linear probing still be faster in wall-clock time?** Cache locality. Linear probing reads sequential memory addresses that fit in cache lines (L1 hit ~4 cycles). Chaining follows heap pointers where each dereference is likely a cache miss (~100 cycles). Five sequential hits (20 cycles) beat one cache miss (100 cycles).

4. **What is the fundamental problem with tombstones, and how does backward shift deletion solve it?** Tombstones permanently inflate probe lengths — they say "keep searching" even when nothing useful is ahead. Over many insert/delete cycles, tombstones accumulate and degrade all lookups. Backward shift deletion physically moves entries to fill gaps, keeping probe chains minimal without sentinel markers.

5. **Why must the table size and `h2(k)` be coprime in double hashing?** If they share a common factor `d`, the probe sequence cycles through only `m/d` slots instead of all `m` — it never visits most of the table. Making the table size prime and ensuring `h2(k) > 0` guarantees full coverage.

6. **Robin Hood hashing keeps the same average probe length as standard linear probing but reduces variance. Why does lower variance matter in practice?** Lower variance means no single lookup is catastrophically slow. The expected maximum probe length drops from O(log n) to O(log log n). This matters for latency-sensitive systems where tail latency (p99, p999) determines user experience — you want predictable performance, not just good average performance.
