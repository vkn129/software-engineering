# Day 76: Quotient Filters

## Why Quotient Filters Exist

Bloom filters are great for approximate membership queries, but they have three painful limitations: you cannot delete elements, you cannot merge two filters efficiently, and you cannot resize without rehashing everything from scratch. Quotient filters solve all three problems while maintaining similar false positive guarantees.

The key economic insight: Bloom filters waste bits by scattering information across multiple hash positions (k hash functions). Quotient filters concentrate all information from a single hash into one contiguous region of memory, which is better for CPU cache lines and enables structural operations like merge and resize.

## Core Idea: Splitting the Hash

Given a hash h(x) of fingerprint_bits = q + r bits:

```
h(x) = [ quotient (q bits) | remainder (r bits) ]
         ^                    ^
         bucket index          stored value
```

- **Quotient (q bits)**: determines the "canonical slot" -- where this element wants to live
- **Remainder (r bits)**: the value actually stored in the table

The table has 2^q slots. Each slot stores one r-bit remainder plus 3 metadata bits.

## The Three Metadata Bits

This is where the cleverness lives. Each slot has:

| Bit | Name | Meaning |
|-----|------|---------|
| `is_occupied` | Occupation flag | Some element with this canonical slot exists *somewhere* in the table |
| `is_continuation` | Run continuation | This slot is NOT the first element in its run (i.e., it continues a run) |
| `is_shifted` | Displacement flag | The element stored here has been displaced from its canonical slot |

### Why three bits?

These bits let you reconstruct which elements belong to which bucket during lookup, even after elements have been shifted around by collisions. Without them, you could not tell whether a remainder in slot 5 actually belongs to bucket 5 or was pushed there from bucket 3.

### Runs and Clusters

- **Run**: A maximal sequence of elements that all share the same canonical slot (same quotient). Runs are stored contiguously and sorted by remainder.
- **Cluster**: A maximal sequence of consecutive occupied slots. A cluster contains one or more runs.

The metadata bits encode the structure:

```
Slot:         [0]  [1]  [2]  [3]  [4]  [5]  [6]  [7]
Remainder:     A    B    C    D    E    --   --   --
Canonical:     0    0    2    2    2    --   --   --
is_occupied:   1    0    1    0    0    0    0    0
is_continuation: 0  1    0    1    1    0    0    0
is_shifted:    0    1    0    1    1    0    0    0
```

Reading this: Slot 0 is occupied (something hashes to 0) and holds element A which is not shifted. Slot 1 holds element B which is shifted (from slot 0) and is a continuation of the run starting at slot 0. Slot 2 is occupied and holds element C which is not shifted. Slots 3-4 hold elements D, E which are shifted and continue the run from slot 2.

## Lookup Algorithm

To check if element x is in the filter:

1. Compute h(x), split into quotient q and remainder r
2. If `is_occupied[q]` is 0, element is definitely not present
3. Otherwise, find the start of the run for quotient q by scanning backward through the cluster to find where runs begin, then forward to the correct run
4. Scan the run for remainder r. If found, element is (probably) present

## Insert Algorithm

1. Compute quotient q and remainder r
2. Find where r should be inserted within the run for q (runs are sorted)
3. Shift subsequent elements right to make room
4. Update all three metadata bits for affected slots

## Delete Algorithm

1. Find the element (same as lookup)
2. Remove it and shift subsequent elements left
3. Update metadata bits

This is the key advantage over Bloom filters: deletion is straightforward because each element occupies exactly one slot.

## Comparison with Bloom Filters

| Property | Bloom Filter | Quotient Filter |
|----------|-------------|----------------|
| Space per element | ~1.44 * log2(1/epsilon) bits | ~log2(1/epsilon) + 3 bits |
| Deletion | Not supported (without counting) | Supported natively |
| Merge | Requires OR of bit arrays (same size only) | Merge-sort of sorted runs |
| Resize | Must rehash everything | Can double size incrementally |
| Cache locality | Poor (k random probes) | Excellent (linear probing, contiguous) |
| False positive rate | Tunable via k and m | Tunable via r_bits |
| Practical speed | Fast for low k | Fast due to cache effects |

## Real-World Applications

1. **SSTables in storage engines** (e.g., RocksDB): Quotient filters sit in front of on-disk sorted runs. Before doing an expensive disk read, check the filter. Deletion support matters because keys get deleted/compacted.

2. **Network packet deduplication**: Routers need to detect duplicate packets. The ability to delete old entries (via TTL expiry) makes quotient filters preferable to Bloom filters.

3. **Filesystem metadata**: Checking if a file exists in a directory without reading the full directory listing.

4. **Database query optimization**: Approximate set membership for join optimization where the working set changes over time (needs deletion).

## Checkpoint Questions

1. **Why does a quotient filter need three metadata bits instead of just one?** How would lookup break if you only had `is_occupied`?

2. **What happens to the false positive rate as the filter fills up?** At what occupancy does performance degrade significantly, and why?

3. **Why can quotient filters be merged but Bloom filters (with different hash functions) cannot?** What structural property enables merge-sort of two quotient filters?

4. **How does cache locality differ between Bloom filters and quotient filters?** Draw the memory access pattern for a lookup in each.

5. **What is the relationship between `r_bits` and the false positive rate?** Derive the formula.

6. **Why must runs be stored in sorted order by remainder?** What would break if they were unsorted?
