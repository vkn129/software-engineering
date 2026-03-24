"""
Day 68 Practice: Cuckoo Hashing Exercises

Five exercises that build intuition for WHY cuckoo hashing behaves the way it does.
"""

import random
import time
import math
import statistics
from collections import defaultdict


# ---------------------------------------------------------------------------
# Exercise 1: Visualize Eviction Chains
# ---------------------------------------------------------------------------

def exercise_1_eviction_chains():
    """
    For each insert, show the full chain of displaced keys.

    WHY: Eviction chains are the core mechanism. Understanding them
    reveals why cuckoo hashing has O(1) amortized insert -- most chains
    are short, but occasionally they cascade.
    """
    print("=" * 70)
    print("EXERCISE 1: Visualize Eviction Chains")
    print("=" * 70)

    class TrackedCuckooHash:
        """Minimal cuckoo hash with full eviction chain tracking."""

        def __init__(self, capacity=8):
            self.capacity = capacity
            self.table1 = [None] * capacity
            self.table2 = [None] * capacity
            self._seed1 = random.randint(0, 2**32)
            self._seed2 = random.randint(0, 2**32)
            self.rehash_count = 0

        def _h1(self, key):
            return hash((key, self._seed1)) % self.capacity

        def _h2(self, key):
            return hash((key, self._seed2)) % self.capacity

        def insert(self, key, value):
            """Returns list of (displaced_key, from_table, to_table) tuples."""
            chain = []
            current = (key, value)
            use_t1 = True

            for step in range(self.capacity * 4):
                if use_t1:
                    idx = self._h1(current[0])
                    if self.table1[idx] is None:
                        self.table1[idx] = current
                        return chain
                    evicted = self.table1[idx]
                    chain.append((evicted[0], "T1", "T2"))
                    self.table1[idx] = current
                    current = evicted
                else:
                    idx = self._h2(current[0])
                    if self.table2[idx] is None:
                        self.table2[idx] = current
                        return chain
                    evicted = self.table2[idx]
                    chain.append((evicted[0], "T2", "T1"))
                    self.table2[idx] = current
                    current = evicted
                use_t1 = not use_t1

            # Rehash needed
            self.rehash_count += 1
            self._rehash_and_insert(current)
            chain.append(("REHASH", "-", "-"))
            return chain

        def _rehash_and_insert(self, leftover):
            items = [leftover]
            for e in self.table1:
                if e is not None:
                    items.append(e)
            for e in self.table2:
                if e is not None:
                    items.append(e)
            self.capacity *= 2
            self.table1 = [None] * self.capacity
            self.table2 = [None] * self.capacity
            self._seed1 = random.randint(0, 2**32)
            self._seed2 = random.randint(0, 2**32)
            for k, v in items:
                self.insert(k, v)

    ht = TrackedCuckooHash(capacity=8)
    names = ["alice", "bob", "carol", "dave", "eve", "frank", "grace",
             "heidi", "ivan", "judy"]

    for i, name in enumerate(names):
        chain = ht.insert(name, i)
        if not chain:
            print(f"  INSERT '{name}': placed directly")
        else:
            steps = []
            for displaced, from_t, to_t in chain:
                if displaced == "REHASH":
                    steps.append("REHASH!")
                else:
                    steps.append(f"evict '{displaced}' {from_t}->{to_t}")
            print(f"  INSERT '{name}': {' -> '.join(steps)}")

    print(f"\n  Total rehashes: {ht.rehash_count}")
    print(f"  Final capacity: {ht.capacity} x 2 tables")


# ---------------------------------------------------------------------------
# Exercise 2: Max Eviction Chain Length vs Load Factor
# ---------------------------------------------------------------------------

def exercise_2_chain_length_vs_load():
    """
    Measure how the maximum eviction chain length grows as the table fills up.

    WHY: This shows why the load factor limit exists. Near 50% for 2 tables,
    chain lengths explode -- the eviction graph develops cycles.
    """
    print("\n" + "=" * 70)
    print("EXERCISE 2: Max Eviction Chain Length vs Load Factor")
    print("=" * 70)

    class MeasuredCuckoo:
        def __init__(self, capacity):
            self.capacity = capacity
            self.table1 = [None] * capacity
            self.table2 = [None] * capacity
            self._seed1 = random.randint(0, 2**32)
            self._seed2 = random.randint(0, 2**32)
            self.size = 0

        def _h1(self, key):
            return hash((key, self._seed1)) % self.capacity

        def _h2(self, key):
            return hash((key, self._seed2)) % self.capacity

        def insert(self, key, value):
            """Returns chain length, or -1 if rehash needed."""
            current = (key, value)
            use_t1 = True
            max_steps = self.capacity * 6

            for step in range(max_steps):
                if use_t1:
                    idx = self._h1(current[0])
                    if self.table1[idx] is None:
                        self.table1[idx] = current
                        self.size += 1
                        return step
                    evicted = self.table1[idx]
                    self.table1[idx] = current
                    current = evicted
                else:
                    idx = self._h2(current[0])
                    if self.table2[idx] is None:
                        self.table2[idx] = current
                        self.size += 1
                        return step
                    evicted = self.table2[idx]
                    self.table2[idx] = current
                    current = evicted
                use_t1 = not use_t1

            return -1  # cycle detected

        def load_factor(self):
            return self.size / (2 * self.capacity)

    # Use a large table to see the pattern clearly
    capacity = 512
    trials = 10
    load_targets = [0.10, 0.20, 0.30, 0.35, 0.40, 0.45, 0.48]

    print(f"\n  Capacity: {capacity} x 2 tables, averaged over {trials} trials")
    print(f"  'Cycles' = how many trials hit an eviction loop (would need rehash)\n")
    print(f"  {'Load':>6} {'Avg Max Chain':>15} {'Max Chain':>11} {'Avg Chain':>11} {'Cycles':>8}")
    print(f"  {'-'*6} {'-'*15} {'-'*11} {'-'*11} {'-'*8}")

    for target_load in load_targets:
        n_items = int(target_load * 2 * capacity)
        max_chains = []
        avg_chains = []
        cycles = 0

        for _ in range(trials):
            ht = MeasuredCuckoo(capacity)
            trial_max = 0
            trial_chain_lengths = []
            trial_failed = False
            keys = random.sample(range(n_items * 10), n_items)

            for key in keys:
                chain_len = ht.insert(key, key)
                if chain_len == -1:
                    trial_failed = True
                    break
                if chain_len > 0:
                    trial_chain_lengths.append(chain_len)
                trial_max = max(trial_max, chain_len)

            max_chains.append(trial_max)
            if trial_chain_lengths:
                avg_chains.append(statistics.mean(trial_chain_lengths))
            if trial_failed:
                cycles += 1

        avg_max = statistics.mean(max_chains)
        overall_max = max(max_chains)
        avg_avg = statistics.mean(avg_chains) if avg_chains else 0.0
        print(f"  {target_load:>5.0%} {avg_max:>15.1f} {overall_max:>11} "
              f"{avg_avg:>11.2f} {cycles:>8}/{trials}")

    print("\n  Observation: as load factor approaches 50%, maximum eviction chain")
    print("  lengths grow and cycle frequency increases. This is why 2-table")
    print("  cuckoo hashing must stay below ~50% load factor.")


# ---------------------------------------------------------------------------
# Exercise 3: Cuckoo Filter (Probabilistic variant supporting deletion)
# ---------------------------------------------------------------------------

def exercise_3_cuckoo_filter():
    """
    Implement a cuckoo filter -- like a Bloom filter but supports deletion.

    WHY: Bloom filters cannot delete because clearing a bit might affect other
    elements. Cuckoo filters store fingerprints in a cuckoo hash table.
    Each fingerprint occupies one slot, so you can remove it without affecting
    others. The tradeoff: small false positive rate from fingerprint collisions.
    """
    print("\n" + "=" * 70)
    print("EXERCISE 3: Cuckoo Filter (Bloom filter + deletion support)")
    print("=" * 70)

    class CuckooFilter:
        """
        Stores fingerprints (short hashes) instead of full keys.
        Supports: insert, lookup (with false positives), DELETE (Bloom can't do this).

        Key trick: the alternate bucket is computed from the fingerprint itself,
        so we don't need to store the original key.
          alt_index = current_index XOR hash(fingerprint)
        This is called "partial-key cuckoo hashing".
        """

        def __init__(self, capacity=1024, fingerprint_bits=8, bucket_size=4):
            self.capacity = capacity
            self.fp_bits = fingerprint_bits
            self.fp_mask = (1 << fingerprint_bits) - 1
            self.bucket_size = bucket_size
            # Each bucket holds up to bucket_size fingerprints
            self.buckets = [[] for _ in range(capacity)]
            self.size = 0
            self.max_kicks = 500

        def _fingerprint(self, item):
            """Non-zero fingerprint from item."""
            fp = hash(("fp", item)) & self.fp_mask
            return fp if fp != 0 else 1  # 0 means empty

        def _index1(self, item):
            return hash(("idx", item)) % self.capacity

        def _alt_index(self, index, fingerprint):
            """Compute alternate index using XOR trick."""
            return (index ^ hash(("alt", fingerprint))) % self.capacity

        def insert(self, item):
            """Insert item into the filter. Returns True on success."""
            fp = self._fingerprint(item)
            i1 = self._index1(item)
            i2 = self._alt_index(i1, fp)

            # Try both buckets first
            if len(self.buckets[i1]) < self.bucket_size:
                self.buckets[i1].append(fp)
                self.size += 1
                return True
            if len(self.buckets[i2]) < self.bucket_size:
                self.buckets[i2].append(fp)
                self.size += 1
                return True

            # Must evict -- pick a random bucket
            idx = random.choice([i1, i2])
            for _ in range(self.max_kicks):
                # Evict a random entry from this bucket
                evict_pos = random.randint(0, self.bucket_size - 1)
                evicted_fp = self.buckets[idx][evict_pos]
                self.buckets[idx][evict_pos] = fp
                fp = evicted_fp
                idx = self._alt_index(idx, fp)

                if len(self.buckets[idx]) < self.bucket_size:
                    self.buckets[idx].append(fp)
                    self.size += 1
                    return True

            return False  # filter is too full

        def lookup(self, item):
            """
            Check if item might be in the set.
            False positives possible, false negatives impossible (if not deleted).
            """
            fp = self._fingerprint(item)
            i1 = self._index1(item)
            i2 = self._alt_index(i1, fp)
            return fp in self.buckets[i1] or fp in self.buckets[i2]

        def delete(self, item):
            """
            Delete item from the filter.

            THIS IS WHAT BLOOM FILTERS CANNOT DO.
            We simply remove the fingerprint from whichever bucket has it.
            """
            fp = self._fingerprint(item)
            i1 = self._index1(item)
            i2 = self._alt_index(i1, fp)

            if fp in self.buckets[i1]:
                self.buckets[i1].remove(fp)
                self.size -= 1
                return True
            if fp in self.buckets[i2]:
                self.buckets[i2].remove(fp)
                self.size -= 1
                return True
            return False

    # Demonstrate
    cf = CuckooFilter(capacity=256, fingerprint_bits=12, bucket_size=4)

    # Insert items
    items = [f"user_{i}" for i in range(500)]
    inserted = 0
    for item in items:
        if cf.insert(item):
            inserted += 1
    print(f"\n  Inserted {inserted}/{len(items)} items")

    # Check membership (should all be True)
    found = sum(1 for item in items[:inserted] if cf.lookup(item))
    print(f"  Lookup for inserted items: {found}/{inserted} found (expect all)")

    # Check false positives on items NOT inserted
    false_positives = 0
    n_test = 5000
    for i in range(n_test):
        if cf.lookup(f"nonexistent_{i}"):
            false_positives += 1
    fp_rate = false_positives / n_test
    print(f"  False positive rate: {fp_rate:.2%} ({false_positives}/{n_test})")

    # DELETE -- the killer feature vs Bloom filters
    deleted_items = items[:50]
    for item in deleted_items:
        cf.delete(item)
    # Verify deleted items are gone
    still_found = sum(1 for item in deleted_items if cf.lookup(item))
    print(f"\n  Deleted 50 items, still found: {still_found} (expect ~0, small FP possible)")
    # Verify remaining items still found
    remaining_found = sum(1 for item in items[50:inserted] if cf.lookup(item))
    print(f"  Remaining items still found: {remaining_found}/{inserted-50}")
    print("\n  Key insight: Bloom filters CANNOT delete because clearing a bit")
    print("  may affect other elements. Cuckoo filters store discrete fingerprints,")
    print("  so deletion removes exactly one fingerprint without side effects.")


# ---------------------------------------------------------------------------
# Exercise 4: Lookup Latency Variance Comparison
# ---------------------------------------------------------------------------

def exercise_4_latency_variance():
    """
    Compare lookup time VARIANCE across hash table strategies.
    Cuckoo hashing should have near-zero variance because every lookup
    does the same amount of work.

    WHY: Average latency is misleading. A system with 1ms average but
    occasional 100ms spikes is worse than one with 2ms average and no spikes,
    for latency-sensitive applications.
    """
    print("\n" + "=" * 70)
    print("EXERCISE 4: Lookup Latency Variance (Cuckoo vs Chaining vs Probing)")
    print("=" * 70)

    # --- Chaining hash table ---
    class ChainingHash:
        def __init__(self, capacity=64):
            self.capacity = capacity
            self.buckets = [[] for _ in range(capacity)]

        def insert(self, key, value):
            idx = hash(key) % self.capacity
            for i, (k, v) in enumerate(self.buckets[idx]):
                if k == key:
                    self.buckets[idx][i] = (key, value)
                    return
            self.buckets[idx].append((key, value))

        def lookup(self, key):
            idx = hash(key) % self.capacity
            for k, v in self.buckets[idx]:
                if k == key:
                    return v
            raise KeyError(key)

    # --- Linear probing hash table ---
    class LinearProbingHash:
        def __init__(self, capacity=256):
            self.capacity = capacity
            self.table = [None] * capacity

        def insert(self, key, value):
            idx = hash(key) % self.capacity
            for _ in range(self.capacity):
                if self.table[idx] is None or self.table[idx][0] == key:
                    self.table[idx] = (key, value)
                    return
                idx = (idx + 1) % self.capacity
            raise RuntimeError("Table full")

        def lookup(self, key):
            idx = hash(key) % self.capacity
            for _ in range(self.capacity):
                if self.table[idx] is None:
                    raise KeyError(key)
                if self.table[idx][0] == key:
                    return self.table[idx][1]
                idx = (idx + 1) % self.capacity
            raise KeyError(key)

    # --- Cuckoo hash (from main module) ---
    from cuckoo_hash import CuckooHashTable

    n_items = 80
    # Use small capacities to make variance visible
    # Chaining with small capacity -> long chains -> high variance
    chain_ht = ChainingHash(capacity=32)
    probe_ht = LinearProbingHash(capacity=256)
    cuckoo_ht = CuckooHashTable(capacity=128)

    keys = list(range(n_items))
    for k in keys:
        chain_ht.insert(k, k)
        probe_ht.insert(k, k)
        cuckoo_ht.insert(k, k)

    # Measure lookup times
    n_lookups = 2000
    lookup_keys = [random.choice(keys) for _ in range(n_lookups)]

    def measure_lookups(ht, lookup_keys):
        times = []
        for key in lookup_keys:
            start = time.perf_counter_ns()
            ht.lookup(key)
            elapsed = time.perf_counter_ns() - start
            times.append(elapsed)
        return times

    chain_times = measure_lookups(chain_ht, lookup_keys)
    probe_times = measure_lookups(probe_ht, lookup_keys)
    cuckoo_times = measure_lookups(cuckoo_ht, lookup_keys)

    def report(name, times):
        avg = statistics.mean(times)
        std = statistics.stdev(times)
        p50 = statistics.median(times)
        p99 = sorted(times)[int(0.99 * len(times))]
        max_t = max(times)
        cv = std / avg if avg > 0 else 0  # coefficient of variation
        print(f"  {name:<20} avg={avg:>7.0f}ns  std={std:>7.0f}ns  "
              f"p50={p50:>7.0f}ns  p99={p99:>7.0f}ns  max={max_t:>7.0f}ns  "
              f"CV={cv:.2f}")

    print(f"\n  {n_lookups} lookups on {n_items} items:\n")
    report("Chaining", chain_times)
    report("Linear Probing", probe_times)
    report("Cuckoo", cuckoo_times)

    print("\n  CV = coefficient of variation (std/mean). Lower = more consistent.")
    print("  Cuckoo hashing should have lower variance because every lookup")
    print("  performs the same 2 memory accesses regardless of key distribution.")
    print("  (Note: Python overhead may mask the difference; in C the gap is stark.)")


# ---------------------------------------------------------------------------
# Exercise 5: Bucketized Cuckoo Hashing
# ---------------------------------------------------------------------------

def exercise_5_bucketized_cuckoo():
    """
    Each slot holds b items instead of 1. This dramatically increases
    the maximum load factor.

    WHY: With bucket size 1, two tables max out at ~50%. With bucket size 4,
    you can reach ~95%+. The insight is that having b choices per position
    makes it exponentially less likely to need eviction.

    This is how real cuckoo hash tables work (e.g., in DPDK, MemC3).
    """
    print("\n" + "=" * 70)
    print("EXERCISE 5: Bucketized Cuckoo Hashing (b items per slot)")
    print("=" * 70)

    class BucketizedCuckooHash:
        """
        Each position in each table holds up to `bucket_size` items.
        Two tables, two hash functions, but each hash maps to a bucket
        that can hold multiple items.
        """

        MAX_EVICTIONS = 500

        def __init__(self, capacity=32, bucket_size=4):
            self.capacity = capacity
            self.bucket_size = bucket_size
            # Each bucket is a list of up to bucket_size (key, value) pairs
            self.table1 = [[] for _ in range(capacity)]
            self.table2 = [[] for _ in range(capacity)]
            self.size = 0
            self._seed1 = random.randint(0, 2**32)
            self._seed2 = random.randint(0, 2**32)

        def _h1(self, key):
            return hash((key, self._seed1)) % self.capacity

        def _h2(self, key):
            return hash((key, self._seed2)) % self.capacity

        def lookup(self, key):
            """Still O(1) worst case -- check 2 buckets of size b."""
            idx1 = self._h1(key)
            for k, v in self.table1[idx1]:
                if k == key:
                    return v

            idx2 = self._h2(key)
            for k, v in self.table2[idx2]:
                if k == key:
                    return v

            raise KeyError(key)

        def __contains__(self, key):
            try:
                self.lookup(key)
                return True
            except KeyError:
                return False

        def delete(self, key):
            idx1 = self._h1(key)
            for i, (k, v) in enumerate(self.table1[idx1]):
                if k == key:
                    self.table1[idx1].pop(i)
                    self.size -= 1
                    return

            idx2 = self._h2(key)
            for i, (k, v) in enumerate(self.table2[idx2]):
                if k == key:
                    self.table2[idx2].pop(i)
                    self.size -= 1
                    return

            raise KeyError(key)

        def insert(self, key, value):
            # Update if exists
            for table, h_fn in [(self.table1, self._h1), (self.table2, self._h2)]:
                idx = h_fn(key)
                for i, (k, v) in enumerate(table[idx]):
                    if k == key:
                        table[idx][i] = (key, value)
                        return

            # Try to fit in an unfull bucket
            idx1 = self._h1(key)
            if len(self.table1[idx1]) < self.bucket_size:
                self.table1[idx1].append((key, value))
                self.size += 1
                return

            idx2 = self._h2(key)
            if len(self.table2[idx2]) < self.bucket_size:
                self.table2[idx2].append((key, value))
                self.size += 1
                return

            # Both full -- eviction needed
            self._evict_and_insert(key, value)
            self.size += 1

        def _evict_and_insert(self, key, value):
            current = (key, value)
            use_t1 = True

            while True:
                placed = False
                for _ in range(self.MAX_EVICTIONS):
                    if use_t1:
                        idx = self._h1(current[0])
                        bucket = self.table1[idx]
                    else:
                        idx = self._h2(current[0])
                        bucket = self.table2[idx]

                    if len(bucket) < self.bucket_size:
                        bucket.append(current)
                        placed = True
                        break

                    # Evict a random item from the bucket
                    evict_pos = random.randint(0, self.bucket_size - 1)
                    evicted = bucket[evict_pos]
                    bucket[evict_pos] = current
                    current = evicted
                    use_t1 = not use_t1

                if placed:
                    return

                # Cycle -- rehash and retry
                self._rehash()
                use_t1 = True

        def _rehash(self):
            old_items = []
            for bucket in self.table1:
                old_items.extend(bucket)
            for bucket in self.table2:
                old_items.extend(bucket)

            total_slots = 2 * self.capacity * self.bucket_size
            if len(old_items) / total_slots > 0.85:
                self.capacity *= 2

            for _attempt in range(20):
                self.table1 = [[] for _ in range(self.capacity)]
                self.table2 = [[] for _ in range(self.capacity)]
                self._seed1 = random.randint(0, 2**32)
                self._seed2 = random.randint(0, 2**32)

                success = True
                for k, v in old_items:
                    if not self._try_insert_no_rehash(k, v):
                        success = False
                        break

                if success:
                    return

                self.capacity *= 2

            raise RuntimeError("Rehash failed after multiple attempts")

        def _try_insert_no_rehash(self, key, value):
            """Attempt insert without triggering rehash."""
            idx1 = self._h1(key)
            if len(self.table1[idx1]) < self.bucket_size:
                self.table1[idx1].append((key, value))
                return True
            idx2 = self._h2(key)
            if len(self.table2[idx2]) < self.bucket_size:
                self.table2[idx2].append((key, value))
                return True

            current = (key, value)
            use_t1 = True
            for _ in range(self.MAX_EVICTIONS):
                if use_t1:
                    idx = self._h1(current[0])
                    bucket = self.table1[idx]
                else:
                    idx = self._h2(current[0])
                    bucket = self.table2[idx]

                if len(bucket) < self.bucket_size:
                    bucket.append(current)
                    return True

                evict_pos = random.randint(0, self.bucket_size - 1)
                evicted = bucket[evict_pos]
                bucket[evict_pos] = current
                current = evicted
                use_t1 = not use_t1

            return False

        def load_factor(self):
            total_slots = 2 * self.capacity * self.bucket_size
            return self.size / total_slots

    # Compare bucket size 1 vs 4
    print("\n  Comparing load factor tolerance with different bucket sizes:\n")

    for bsize in [1, 2, 4]:
        # Try to insert as many items as possible before rehash
        cap = 64
        ht = BucketizedCuckooHash(capacity=cap, bucket_size=bsize)
        target = int(0.95 * 2 * cap * bsize)
        inserted = 0
        final_cap = cap

        for i in range(target):
            old_cap = ht.capacity
            ht.insert(i, i)
            inserted += 1
            if ht.capacity != old_cap:
                # Rehash happened -- capacity changed
                final_cap = ht.capacity
                break
            final_cap = ht.capacity

        actual_load = ht.load_factor()
        total_slots = 2 * final_cap * bsize
        print(f"  bucket_size={bsize}: inserted {inserted} items into "
              f"{2}x{final_cap}x{bsize}={total_slots} slots, "
              f"load={actual_load:.1%}")

        # Verify all lookups work
        for i in range(inserted):
            assert ht.lookup(i) == i
        print(f"    All {inserted} lookups verified correct.")

    # Demo with bucket_size=4
    print(f"\n  Bucketized cuckoo (b=4) in action:")
    ht = BucketizedCuckooHash(capacity=32, bucket_size=4)
    for i in range(200):
        ht.insert(f"item_{i}", i)

    print(f"    Inserted 200 items, load factor: {ht.load_factor():.1%}")
    print(f"    Capacity: {ht.capacity} x 2 tables x 4 per bucket "
          f"= {2 * ht.capacity * 4} total slots")

    # Delete test
    for i in range(50):
        ht.delete(f"item_{i}")
    print(f"    After deleting 50: load factor = {ht.load_factor():.1%}")
    assert f"item_0" not in ht
    assert f"item_100" in ht
    print(f"    Delete correctness verified.")

    print("\n  Key insight: bucket size b=4 is the sweet spot in practice.")
    print("  It gives ~95%+ load factor while keeping lookups fast")
    print("  (scan 4 items in a cache line is essentially free on modern CPUs).")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)  # reproducible results

    exercise_1_eviction_chains()
    exercise_2_chain_length_vs_load()
    exercise_3_cuckoo_filter()
    exercise_4_latency_variance()
    exercise_5_bucketized_cuckoo()

    print("\n" + "=" * 70)
    print("ALL EXERCISES COMPLETE")
    print("=" * 70)
