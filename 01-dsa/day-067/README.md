# Day 67: Perfect Hashing

## Why This Exists

Regular hash tables give you O(1) **expected** lookup time. That "expected" hides a lie: with adversarial inputs or bad luck, you get O(n) worst case from collisions piling into the same bucket. For most applications this is fine. But when you have a **static set of keys** — keys that never change after construction — you can do something extraordinary: build a hash table with O(1) **worst case** lookup. Zero collisions. Guaranteed.

This is perfect hashing. It is not a clever trick — it is a mathematical construction that exploits the fact that when you know all the keys upfront, you can spend time at build phase to find hash functions that produce no collisions at query time. The trade-off is stark: you give up the ability to insert or delete keys, and in exchange you get the strongest possible lookup guarantee.

Perfect hashing shows up in places where static lookup dominates: compiler keyword tables (the set of reserved words in C never changes at runtime), read-only databases, network protocol parsers (HTTP method lookup, status code tables), and embedded systems where deterministic worst-case timing matters for safety.

## Theory

### The Problem

Given a static set S of n keys, construct a data structure that:
- Answers "is key k in S?" in O(1) worst case
- Uses O(n) space
- Has zero collisions for any key in S

A regular hash table cannot guarantee this. Even with a good hash function, two keys might collide, and resolving that collision costs extra time (chaining costs a pointer traversal, open addressing costs probing).

### FKS Perfect Hashing (Fredman, Komlós, Szemerédi, 1984)

The FKS scheme uses a **two-level** construction:

**Level 1: Hash into buckets**

Pick a universal hash function h that maps n keys into m = n buckets. Some buckets will have collisions — multiple keys landing in the same bucket. Call the number of keys in bucket i "ni".

```
Key set S = {k1, k2, ..., kn}
        |
    h(k) mod m     (m = n)
        |
  +---------+---------+---------+
  | bucket 0| bucket 1| bucket 2| ...
  |  n0 keys|  n1 keys|  n2 keys|
  +---------+---------+---------+
```

**Level 2: Perfect hash per bucket**

For each bucket i with ni keys, allocate a second-level table of size ni^2. Then search for a hash function hi that maps those ni keys into ni^2 slots with **zero** collisions.

Why ni^2? The birthday paradox in reverse. If you throw ni balls into ni^2 bins, the probability of any collision is at most 1/2. So on average, you need to try only about 2 random hash functions before finding one with no collisions. Construction is fast.

```
bucket i (ni = 3 keys):
  -> second-level table of size 9
  -> try random hash functions until one gives 0 collisions
  -> expected ~2 trials
```

**Space analysis: Why O(n) total**

The total second-level space is the sum of ni^2 across all buckets. A key theorem shows that if the first-level hash is chosen from a universal family, then:

E[sum of ni^2] <= 2n

So the expected total space is O(n). If a particular first-level hash gives too much total space (say > 4n), just pick a different one — you will find a good one quickly.

### Why It Only Works for Static Sets

The entire construction depends on knowing all n keys upfront. The second-level hash functions are chosen specifically for the keys in each bucket. If you insert a new key:
- It might collide in its second-level table (the hash function was not designed for it)
- You would need to rebuild that bucket's second-level table
- This rebuild could cascade if it changes the space budget

Dynamic perfect hashing exists (Dietzfelbinger et al.) but is significantly more complex. For practical dynamic sets, regular hash tables with O(1) expected time are usually good enough.

### Minimal Perfect Hashing

A perfect hash function maps n keys to a table of size O(n) with no collisions. A **minimal** perfect hash function does something stronger: it maps n keys to exactly the integers [0, n-1] with no gaps.

```
Regular perfect hash:   n keys -> table of size ~2n (some empty slots)
Minimal perfect hash:   n keys -> table of size exactly n (no empty slots)
```

This is optimal — you cannot use less space than n slots for n keys.

**Why minimal matters:**
- Space efficiency: no wasted slots
- Enables rank queries: if keys map to [0, n-1] in sorted order, you get the rank of any key in O(1)
- Compact representations: associated values can be stored in a dense array indexed by the hash

**The CHD Algorithm (Compress, Hash, and Displace)**

CHD is a practical minimal perfect hashing algorithm:
1. Hash all keys into buckets using a first-level hash
2. Process buckets from largest to smallest
3. For each bucket, try displacement values d = 0, 1, 2, ... until all keys in that bucket map to unoccupied slots in the output array using h(key, d)
4. Store the displacement value for each bucket

CHD achieves near-optimal space (about 2.07 bits per key for the hash function description) and construction is fast — O(n) expected time.

### Real-World Uses

| Application | Why Perfect Hashing | Alternative |
|---|---|---|
| Compiler keyword tables | ~50 fixed keywords, millions of lookups/sec | Switch/case or trie |
| gperf (GNU perfect hash generator) | Static string sets in generated C code | Hand-written lookup |
| Read-only databases | Static key sets with guaranteed latency | B-tree (O(log n)) |
| Network protocol parsing | Fixed set of methods/headers | Linear scan |
| Embedded systems | Deterministic worst-case timing | Sorted array + binary search |
| Succinct data structures | Minimal perfect hash as building block | Larger index structures |

### Complexity Summary

| Operation | FKS Perfect Hash | Regular Hash Table | Sorted Array |
|---|---|---|---|
| Build | O(n) expected | O(n) expected | O(n log n) |
| Lookup | **O(1) worst case** | O(1) expected, O(n) worst | O(log n) |
| Insert | Not supported | O(1) expected | O(n) |
| Space | O(n) | O(n) | O(n) |

## Checkpoint Questions

1. **Why does the second-level table need ni^2 slots instead of ni?** What probability result guarantees we can find a collision-free hash function quickly?

2. **Prove intuitively that the total space across all second-level tables is O(n).** What would happen if we used ni (not ni^2) sized second-level tables?

3. **Why can't you insert a new key into an FKS perfect hash table?** What specifically breaks?

4. **What is the difference between a perfect hash function and a minimal perfect hash function?** When does the "minimal" property matter in practice?

5. **A compiler has 50 reserved keywords. Why is perfect hashing better than a balanced BST for keyword lookup?** Quantify the difference.

6. **Could you use perfect hashing for a spell-checker dictionary that gets updated monthly?** What would the workflow look like?
