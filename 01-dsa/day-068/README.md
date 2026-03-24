# Day 68: Cuckoo Hashing

## Why Cuckoo Hashing Exists

Most hash tables offer O(1) *amortized* or *expected* lookup. That means *on average* lookups are fast, but any single lookup might be slow (e.g., traversing a long chain). For some systems, "usually fast" is not good enough. Network routers processing millions of packets per second need *guaranteed* constant-time lookup -- every single time, no exceptions. Cuckoo hashing solves this.

## Core Idea

Cuckoo hashing achieves **O(1) worst-case lookup** (not amortized -- truly worst case) with **O(1) amortized insert**.

The name comes from the cuckoo bird, which pushes other birds' eggs out of their nests to make room for its own.

### Structure

- Maintain **2 (or more) separate hash tables**, each with its own hash function.
- Every key has exactly 2 possible locations: `table1[h1(key)]` and `table2[h2(key)]`.
- Lookup checks exactly 2 slots. Always. That is O(1) worst case.

### Insert Algorithm

1. Compute `h1(key)`. Try to place in `table1[h1(key)]`.
2. If that slot is occupied, **evict** the existing key and place the new key there.
3. The evicted key now needs a home. Insert it into its *alternate* table.
4. This may cascade -- each eviction displaces another key, creating an **eviction chain**.
5. If the chain exceeds a threshold (cycle detected / eviction loop), **rehash** everything with new hash functions.

### Why It Works

- Lookup: check `table1[h1(key)]` and `table2[h2(key)]`. Two memory accesses, always. O(1) worst case.
- Delete: same two checks, clear the slot. O(1) worst case.
- Insert: amortized O(1). Individual inserts may trigger eviction chains or rehashes, but averaged over many inserts, the cost is constant.

## Key Constraints

| Parameter | 2-table variant | 3-table variant |
|-----------|----------------|-----------------|
| Max load factor | ~50% | ~91% |
| Lookup probes | 2 | 3 |
| Rehash frequency | Higher | Lower |

Load factor must stay below ~50% for the 2-table variant. Beyond that, eviction cycles become too frequent and rehashing dominates. The 3-table variant pushes this to ~91%, which is why it is used in practice.

## Real-World Uses

- **Network routers**: Packet forwarding tables need deterministic lookup time. You cannot have a packet wait while you traverse a chain.
- **GPU hash tables**: GPU threads run in lockstep (SIMT). Variable-time lookups cause thread divergence, killing performance. Cuckoo hashing guarantees uniform access patterns.
- **Cuckoo filters**: A probabilistic data structure (like Bloom filters) that supports deletion. Uses the cuckoo eviction idea on fingerprints.
- **Database join operations**: When you need guaranteed-time probes into a hash table during a hash join.

## Trade-offs

**Advantages over chaining:**
- O(1) worst case lookup (chaining is O(n) worst case)
- Cache-friendly (no pointer chasing)
- Deterministic timing

**Advantages over open addressing (linear/quadratic probing):**
- O(1) worst case (probing is O(n) worst case with clustering)
- No clustering problems

**Disadvantages:**
- ~50% space utilization for 2 tables (wasteful compared to ~70-80% for open addressing)
- Inserts can be expensive when eviction chains are long
- Rehashing is expensive when it happens
- More complex implementation

## Connection to Physics/Economics

This is a **space-time-determinism tradeoff**. You are paying with extra space (two half-full tables) to buy deterministic time. In networking hardware, the cost of a buffer overflow from a slow lookup far exceeds the cost of extra SRAM for two tables. Economics: pay upfront (space) to eliminate tail risk (slow lookups).

## Checkpoint Questions

1. Why does cuckoo hashing guarantee O(1) worst-case lookup while chaining and open addressing cannot?
2. What causes an eviction chain, and when does it become a cycle requiring rehash?
3. Why must the load factor stay below ~50% for the 2-table variant? What changes with 3 tables?
4. In what scenario would you choose cuckoo hashing over a standard hash map? When would you not?
5. How does a cuckoo filter differ from a Bloom filter, and why can cuckoo filters support deletion?
6. If you are designing a hash table for a network router ASIC, why does worst-case vs amortized matter?

## Files

- `cuckoo_hash.py` — Full implementation of 2-table and 3-table cuckoo hashing with demo
- `practice.py` — Five exercises exploring eviction chains, cuckoo filters, latency variance, and bucketized cuckoo hashing
