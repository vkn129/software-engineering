# Day 14: Hash Tables Part 2 -- Open Addressing and Resize

## Why This Exists

Yesterday you learned chaining: each bucket holds a linked list of colliding entries. It works, but it has a cost -- every entry is a heap-allocated node with a pointer overhead, and traversing chains means jumping through scattered memory addresses. On modern CPUs where a cache miss costs 100+ cycles, those pointer chases are expensive.

Open addressing takes a fundamentally different approach: store everything directly in the array. When a collision occurs, you probe -- you look at the next slot, or the slot after that, following a deterministic sequence until you find an empty one. No linked lists, no heap allocation per entry, no pointer chasing. The data sits in contiguous memory, and the CPU's cache prefetcher is happy.

This is not academic preference. Python's dict uses open addressing. So does Rust's HashMap, Go's map, and most high-performance hash table implementations. Google's Swiss Table (absl::flat_hash_map), which is considered the state-of-the-art hash table, uses open addressing with SIMD instructions to probe 16 slots simultaneously. When you profile real systems, cache behavior dominates, and open addressing wins.

But open addressing introduces new problems. Deletion becomes tricky -- you cannot just empty a slot, or you will break the probe chain for other entries. Clustering means that groups of filled slots tend to grow, making probes longer. The load factor must stay lower than with chaining (typically below 0.7), or performance falls off a cliff. And resizing is the same O(n) cost, happening at a lower occupancy.

Understanding both chaining and open addressing -- their strengths, failure modes, and engineering trade-offs -- is what separates someone who USES hash tables from someone who UNDERSTANDS them.

## Theory (40 min)

### 1. Open Addressing: The Idea

Instead of storing collisions in linked lists, we find another empty slot in the main array:

```
  hash("alice") = 3
  hash("charlie") = 3  -- collision!

  Chaining:  slot 3 -> [alice] -> [charlie]  (linked list)
  Open addr: slot 3 = [alice], slot 4 = [charlie]  (probe forward)
```

All entries live in the array itself. The array is both the index structure and the storage. This means the load factor can never exceed 1.0 (every slot holds at most one entry).

### 2. Linear Probing

The simplest probing strategy: if slot h is taken, try h+1, h+2, h+3, ...

```
  probe(key, i) = (hash(key) + i) % table_size

  Insert "alice" -> hash=3, slot 3 empty, place at 3
  Insert "charlie" -> hash=3, slot 3 taken, try 4, empty, place at 4
  Insert "eve" -> hash=4, slot 4 taken, try 5, empty, place at 5

  Table: [   ] [   ] [   ] [alice] [charlie] [eve] [   ] [   ]
                             ^3       ^4       ^5
```

**The clustering problem**: Filled slots tend to form contiguous runs. A new key that hashes anywhere into a run must probe past the entire run. Longer runs attract more insertions, making them grow faster. This is **primary clustering**, and it degrades performance significantly as the table fills.

At load factor 0.5 with linear probing, the average successful search examines about 1.5 slots. At 0.75, it examines about 2.5 slots. At 0.9, it examines about 5.5 slots. At 0.95, it examines about 10.5 slots. The curve is non-linear -- performance does not degrade gracefully.

### 3. Quadratic Probing

Instead of stepping by 1 each time, step by increasing amounts: try h+1, h+4, h+9, h+16, ...

```
  probe(key, i) = (hash(key) + i^2) % table_size
```

This breaks up primary clusters because entries that hash to the same initial slot spread out quickly. However, entries that hash to the SAME slot still follow the same probe sequence (secondary clustering).

Caveat: quadratic probing is not guaranteed to visit every slot. It only visits all slots when table_size is prime and the table is less than half full. This is why many implementations use prime table sizes.

### 4. Double Hashing

Use a second hash function to determine the step size:

```
  probe(key, i) = (hash1(key) + i * hash2(key)) % table_size
```

Two keys that collide at the same slot will (with high probability) have different step sizes, so their probe sequences diverge immediately. This eliminates both primary and secondary clustering.

The requirement: hash2(key) must never return 0 (infinite loop), and should be coprime with table_size. A common choice: `hash2(key) = prime - (hash(key) % prime)` where prime < table_size.

### 5. The Deletion Problem: Tombstones

With chaining, deletion is simple -- remove a node from the linked list. With open addressing, you CANNOT simply empty a slot:

```
  Insert "alice" at slot 3
  Insert "charlie" at slot 3 -> probes to slot 4
  Delete "alice" (empty slot 3)
  Lookup "charlie": hash=3, slot 3 is empty -> "not found"!  WRONG.
```

The probe chain for "charlie" passes through slot 3. If we empty slot 3, the lookup stops early and misses "charlie".

**Solution: tombstones**. Instead of emptying the slot, mark it as DELETED. During lookup, DELETED slots are treated as occupied (keep probing). During insertion, DELETED slots can be reused.

The cost: tombstones degrade performance over time. A table with many tombstones has long probe chains even at low real load factors. Periodic compaction (rebuild the table without tombstones) is necessary.

### 6. Resize: When and How

With open addressing, you MUST resize before the table is full (load factor < 1.0). In practice:

- Resize when load factor > 0.7 (common threshold)
- Double the table size (or go to the next prime)
- Rehash ALL entries -- both live entries and removing tombstones

```
  Before resize (capacity 8, 6 entries, LF = 0.75):
  [ ] [A] [B] [X] [C] [D] [E] [ ]    (X = tombstone)

  After resize (capacity 16, 5 entries, LF = 0.3125):
  [ ] [ ] [A] [ ] [C] [ ] [ ] [B] [ ] [D] [ ] [ ] [E] [ ] [ ] [ ]
```

Resize removes tombstones and redistributes entries for shorter probe chains. It is O(n) work but happens O(log n) times over n insertions, giving O(1) amortized cost.

### 7. Python Dict Internals

Python's dict uses open addressing with a cleverly designed probe sequence:

```python
# Simplified Python dict probing (actual CPython code)
perturb = hash_value
index = perturb % table_size
while table[index] is not EMPTY:
    perturb >>= 5
    index = (5 * index + perturb + 1) % table_size
```

The `perturb` variable starts as the full hash value and is shifted right each iteration. This means early probes depend on ALL bits of the hash (not just the low bits used for the initial index), giving excellent distribution. As perturb approaches zero, it degrades to a linear-like sequence that is guaranteed to visit every slot.

Python dicts also maintain insertion order (since 3.7) by using a separate compact array for the key-value pairs and an index array for the hash table itself. This is a space optimization: the index array holds only 1-byte or 4-byte indices instead of full key-value entries.

### 8. Robin Hood Hashing

A clever refinement of linear probing: when inserting a new key, if the new key has traveled FURTHER from its ideal slot than the current occupant, SWAP them and continue inserting the displaced entry.

```
  Slot 3: "alice" (0 away from ideal slot 3)
  Insert "charlie" (ideal slot 3, now 1 away at slot 4):
    Slot 4: "bob" (0 away from ideal slot 4)
    "charlie" has traveled 1, "bob" has traveled 0
    Since 1 > 0, swap: put "charlie" at 4, continue inserting "bob"
```

This equalizes probe distances -- no entry is much farther from its ideal slot than any other. The variance of probe lengths drops dramatically, making worst-case lookups much better. Rust's standard HashMap used Robin Hood hashing before switching to Swiss Table.

### 9. Consistent Hashing (Distributed Systems)

When you have N servers and hash keys to servers with `hash(key) % N`, adding or removing a server remaps almost ALL keys. Consistent hashing arranges servers on a ring (hash them onto [0, 2^32)). A key maps to the first server clockwise from its position.

```
     0
    / \
  S3   S1    Key K hashes between S1 and S2
  |     |    -> maps to S2
  S2
```

Adding a server only remaps keys between it and its predecessor. Removing a server only remaps its keys to its successor. This is how DynamoDB, Cassandra, and consistent hash rings in load balancers work.

## Practice (20 min)

Work through `practice.py`. Implement open addressing with linear probing, handle tombstones for deletion, and measure how clustering affects probe chain lengths.

## Daily Project

Run `hash_table_open.py` to see a complete open addressing hash table with linear probing, quadratic probing, and double hashing. It measures probe chain lengths, demonstrates the clustering problem visually, shows tombstone degradation, and benchmarks against Python's dict. Study how different probing strategies handle the same data -- the difference in probe lengths is dramatic.

## Checkpoint Questions

1. Why does linear probing suffer from clustering while double hashing does not? Draw what happens when five keys all hash to slot 3 under each strategy.

2. Why can the load factor never reach 1.0 with open addressing? What happens to lookup time as load factor approaches 1.0, and why is the degradation worse than with chaining?

3. A hash table uses tombstones for deletion. After 1 million insertions and 999,990 deletions, the table has only 10 live entries but 999,990 tombstones. What is the performance like? How do you fix this?

4. Python's dict probe sequence uses `perturb >>= 5` to shift the perturbation. Why use all bits of the hash instead of just the low bits? Give an example of data that would cause problems with only low-bit probing.

5. In consistent hashing, why do systems use "virtual nodes" (multiple hash positions per server)? What problem does this solve? (Hint: what happens when servers have different capacities, or when you only have 3 servers?)
