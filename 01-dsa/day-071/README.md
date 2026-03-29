# Day 71: Bloom Filters

## What Is a Bloom Filter?

A Bloom filter is a **probabilistic data structure** for set membership testing. It answers one question: "Is this element in the set?" But the answer comes with a caveat:

- **"Definitely not in set"** — guaranteed correct (no false negatives)
- **"Probably in set"** — might be wrong (false positives possible)

This asymmetry is the key insight. When you can tolerate occasional false positives but never false negatives, a Bloom filter gives you massive space savings over exact data structures.

## How It Works

1. Start with a **bit array** of `m` bits, all set to 0.
2. Choose `k` independent hash functions, each mapping elements to a position in `[0, m)`.
3. **Insert**: Hash the element with all `k` functions, set those `k` bit positions to 1.
4. **Query**: Hash the element with all `k` functions, check if ALL `k` positions are 1.
   - If any bit is 0 → element is **definitely not** in the set.
   - If all bits are 1 → element is **probably** in the set (those bits might have been set by other elements).

## The Math

Given `n` items to store in a filter with `m` bits and `k` hash functions:

**Optimal number of hash functions:**
```
k = (m / n) * ln(2)
```

**False positive rate:**
```
FP ≈ (1 - e^(-kn/m))^k
```

**Optimal bit array size for a target FP rate `p`:**
```
m = -(n * ln(p)) / (ln(2))^2
```

**Bits per element for 1% FP rate:** ~9.6 bits per element (regardless of element size!)

This is remarkable — whether you're storing 4-byte integers or 1KB URLs, each element costs the same number of bits in the filter.

## Why You Cannot Delete From a Standard Bloom Filter

Consider elements A and B that share a hash position (bit index 5):

```
Insert A: sets bits {2, 5, 9}
Insert B: sets bits {3, 5, 7}

Bit array: ...0 0 1 1 0 1 0 1 0 1 0...
                 ^   ^     ^   ^   ^
```

If you "delete" A by clearing bits {2, 5, 9}, you also clear bit 5 — which B needs. Now `contains(B)` returns false, violating the no-false-negatives guarantee. This is why **Counting Bloom Filters** exist: replace each bit with a counter, increment on insert, decrement on delete.

## Space Comparison

Storing **1 billion URLs** (average 50 bytes each):

| Structure | Space | False Positives |
|-----------|-------|-----------------|
| HashSet (exact) | ~80 GB (objects + pointers + overhead) | 0% |
| Sorted array of hashes | ~8 GB (8-byte hashes) | ~0% |
| Bloom filter (1% FP) | ~1.2 GB | 1% |
| Bloom filter (0.1% FP) | ~1.8 GB | 0.1% |

The Bloom filter uses **~1.2 GB at 1% FP** vs roughly **~80 GB** for a full hash set in a language with object overhead. Even compared to a packed hash array (~8 GB), the savings are significant.

## Real-World Uses

### Chrome Safe Browsing
Google maintains a list of ~1M malicious URLs. Instead of downloading the full list to every Chrome install, they ship a Bloom filter (~25 MB). When you visit a URL, Chrome checks the local filter first. Only if the filter says "probably yes" does it make a network request to verify against the full database.

### Cassandra / LevelDB / RocksDB (Skip Disk Reads)
LSM-tree storage engines have data spread across multiple SSTables on disk. Before doing an expensive disk read to look for a key, they check a Bloom filter for each SSTable. If the filter says "not here," they skip that file entirely. This turns many disk seeks into cheap in-memory bit checks.

### Medium (Avoid Re-Recommending Articles)
Medium tracks which articles each user has already seen. A Bloom filter per user avoids showing the same article twice. A false positive means occasionally hiding an unread article (acceptable) — but a false negative would mean annoying the user with repeated recommendations (unacceptable).

### Bitcoin SPV (Simplified Payment Verification) Clients
Lightweight Bitcoin wallets use Bloom filters to tell full nodes which transactions they care about, without revealing their exact addresses. The full node filters the blockchain and sends back only matching transactions.

### Akamai (One-Hit-Wonder Filter)
Akamai found that ~75% of URLs are requested only once. They use a Bloom filter as a "first-seen" gate: only cache a URL on the second request. This prevents one-hit wonders from polluting the cache.

## Checkpoint Questions

1. **Why can a Bloom filter have false positives but never false negatives?** Think about what it means for all k bits to be set vs at least one bit being unset.

2. **If you double the number of hash functions k beyond the optimal value, what happens to the false positive rate?** Does it always improve with more hash functions?

3. **A system needs to check if a user has seen a notification. Why is a Bloom filter appropriate here, and what would a false positive mean in practice?**

4. **Why does the optimal number of hash functions depend on the ratio m/n?** What happens if k is too small or too large?

5. **How does a Counting Bloom Filter solve the deletion problem, and what new issue does it introduce?** Think about space and overflow.

6. **You have two Bloom filters with the same m and k but different elements. What does their bitwise OR represent? What about bitwise AND?** Are both operations useful?
