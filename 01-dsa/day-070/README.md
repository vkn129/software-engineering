# Day 70: In-Memory Cache Mini-Project

Week 10 capstone — tying together every hash table concept into a production-grade cache.

## Why Caches Exist

The entire reason caches exist is the **memory hierarchy**:

```
Register  ~0.3 ns    64-128 bytes      (fastest, smallest)
L1 Cache  ~1 ns      32-64 KB
L2 Cache  ~4 ns      256 KB - 1 MB
L3 Cache  ~12 ns     4-32 MB
RAM       ~100 ns    8-64 GB
SSD       ~100 us    256 GB - 4 TB
HDD       ~10 ms     1-16 TB            (slowest, largest)
Network   ~1-100 ms  unlimited
```

Each level down is roughly **10-100x slower** but **10-1000x larger**. A cache
sits between a fast layer and a slow layer, keeping recently- or frequently-used
data in the fast layer so we avoid the slow path.

This is not just a software concept. CPU caches, TLBs, page tables, browser
caches, CDNs, DNS caches, database buffer pools — they are all the same idea
applied at different scales. The physics constraint is the speed of light: data
that is physically closer (smaller storage) can be reached faster.

## Cache = Hash Table + Eviction Policy

A cache is fundamentally a **hash table with a size limit**. When the table is
full and a new entry arrives, something must be evicted. The eviction policy is
what distinguishes different cache designs:

| Policy | Evicts | Good for | Weakness |
|--------|--------|----------|----------|
| LRU (Least Recently Used) | Oldest access | Temporal locality | Scan pollution |
| LFU (Least Frequently Used) | Lowest access count | Frequency-skewed workloads | Stale popular items |
| FIFO | Oldest insertion | Simple, predictable | Ignores access patterns |
| ARC (Adaptive Replacement) | Adaptive | Mixed workloads | More memory overhead |
| Random | Random victim | When access is uniform | Unpredictable worst case |

## LRU: Hash Map + Doubly Linked List

LRU is the workhorse of caching. The insight: maintain a **doubly linked list**
ordered by access time, plus a **hash map** from key to list node.

```
Hash Map                  Doubly Linked List (MRU ... LRU)
┌─────────┐
│ key_A ──────► [A] <──> [C] <──> [B]    ← B is next eviction victim
│ key_B ──────► [B]       ^
│ key_C ──────► [C]     HEAD             TAIL
└─────────┘
```

- **get(key)**: hash lookup O(1) -> move node to head O(1) -> return value
- **put(key, val)**: hash lookup O(1) -> if exists, update + move to head; if
  new, insert at head, if over capacity evict tail O(1)
- **evict()**: remove tail node O(1) -> delete from hash map O(1)

Every operation is **O(1)**. This is why LRU is ubiquitous.

## TTL (Time-to-Live)

Data goes stale. TTL assigns each key an expiration timestamp.

Two expiration strategies:

1. **Lazy expiration**: check if expired on every `get()`. Simple but dead keys
   consume memory until accessed.
2. **Active expiration**: background thread periodically scans and removes
   expired keys. Frees memory proactively but adds CPU overhead and needs
   synchronization.

Real systems (Redis) use both: lazy on access + periodic random sampling of keys
to actively expire a fraction each cycle.

## Sharding

A single hash table becomes a bottleneck under concurrent access (lock
contention). Solution: **shard** the keyspace across N independent hash tables:

```
shard_index = hash(key) % N
```

Each shard has its own lock, so N threads can operate on N different shards
simultaneously. This is exactly how Java's `ConcurrentHashMap` and Go's
`sync.Map` (partially) work.

Trade-off: more shards = less contention, but more memory overhead and harder to
get global stats (like total size).

## Cache Stampede

When a popular key expires, many threads simultaneously discover the miss and
all try to recompute the value at once. This can overwhelm the backing store.

Mitigations:
- **Single-flight / request coalescing**: only one thread recomputes; others
  wait for its result
- **Early expiration (stale-while-revalidate)**: return stale value while one
  thread refreshes in the background
- **Locking**: acquire a per-key lock before recomputation
- **Jitter**: add random offset to TTLs so keys don't expire simultaneously

## Real Systems

- **Redis**: in-memory key-value store, LRU/LFU eviction, single-threaded event
  loop, used as cache and database
- **Memcached**: distributed memory cache, LRU eviction, slab allocator to avoid
  fragmentation, multi-threaded
- **Guava Cache / Caffeine**: JVM in-process caches, Caffeine uses Window-TinyLFU
  (near-optimal hit rate)
- **CPU cache lines**: hardware LRU approximation (pseudo-LRU with tree bits),
  64-byte cache lines, write-back with MESI protocol

## Checkpoint Questions

1. Why does LRU require a doubly linked list rather than a singly linked list?
   (Hint: what operation on the list needs O(1) that a singly linked list cannot
   provide?)

2. If your cache has 1000 keys each with random TTLs between 1-60 seconds, what
   fraction of keys are expired but still in memory at any given time under
   lazy-only expiration? How does this change with active expiration every 5
   seconds?

3. A sharded cache with 16 shards sees uneven load: shard 3 gets 40% of
   requests. What went wrong and how would you fix it?

4. You have a cache stampede on a key that takes 2 seconds to recompute and gets
   1000 requests/second. How many redundant recomputations happen without
   single-flight? With single-flight?

5. Your LRU cache has a 95% hit rate but a sequential scan of 10,000 keys just
   flushed the entire working set. What cache policy would have handled this
   better, and why?

6. Redis is single-threaded yet handles 100K+ ops/sec. Why doesn't it need
   sharding internally? When would you shard Redis externally?
