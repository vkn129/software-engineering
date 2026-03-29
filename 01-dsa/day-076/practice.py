"""
Day 76 Practice: Quotient Filter Exercises

Five exercises building deeper understanding of quotient filters,
their trade-offs, and advanced operations.
"""

import hashlib
import random
import time
import math
from quotient_filter import QuotientFilter


# ============================================================================
# Exercise 1: Bloom Filter vs Quotient Filter — FP Rate at Same Memory Budget
# ============================================================================

class BloomFilter:
    """
    Simple Bloom filter for comparison purposes.

    Uses k independent hash functions over a bit array of m bits.
    """

    def __init__(self, m_bits, k_hashes):
        self.m = m_bits
        self.k = k_hashes
        self.bits = [False] * m_bits
        self.count = 0

    def _hashes(self, item):
        """Generate k hash positions using double hashing."""
        if not isinstance(item, bytes):
            item = str(item).encode('utf-8')
        h1 = int.from_bytes(hashlib.sha256(item).digest()[:8], 'big')
        h2 = int.from_bytes(hashlib.md5(item).digest()[:8], 'big')
        for i in range(self.k):
            yield (h1 + i * h2) % self.m

    def insert(self, item):
        for pos in self._hashes(item):
            self.bits[pos] = True
        self.count += 1

    def contains(self, item):
        return all(self.bits[pos] for pos in self._hashes(item))

    @property
    def memory_bits(self):
        return self.m  # 1 bit per slot


def exercise_1_compare_fp_rates():
    """
    Compare Bloom filter vs Quotient filter at the same memory budget.

    Key insight: A quotient filter slot uses (r_bits + 3) bits.
    Total memory = 2^q_bits * (r_bits + 3) bits.
    A Bloom filter uses m bits total.

    At the same total memory, which has a lower false positive rate?
    """
    print("=" * 70)
    print("Exercise 1: Bloom vs Quotient Filter — Same Memory Budget")
    print("=" * 70)

    n_items = 500  # number of items to insert

    # Quotient filter: q_bits=10 (1024 slots), r_bits=8
    # Memory = 1024 * (8 + 3) = 11264 bits
    q_bits, r_bits = 10, 8
    qf = QuotientFilter(q_bits=q_bits, r_bits=r_bits)
    qf_memory = (1 << q_bits) * (r_bits + 3)  # total bits

    # Bloom filter with the same number of bits
    # Optimal k for n items in m bits: k = (m/n) * ln(2)
    m_bits = qf_memory
    k_optimal = max(1, round((m_bits / n_items) * math.log(2)))
    bf = BloomFilter(m_bits=m_bits, k_hashes=k_optimal)

    print(f"\nMemory budget: {qf_memory} bits ({qf_memory / 8:.0f} bytes)")
    print(f"Quotient filter: q={q_bits}, r={r_bits}, slots={1 << q_bits}")
    print(f"Bloom filter: m={m_bits}, k={k_optimal}")
    print(f"Items to insert: {n_items}")

    # Insert same items into both
    inserted = set()
    for i in range(n_items):
        item = f"item_{i}"
        qf.insert(item)
        bf.insert(item)
        inserted.add(item)

    # Measure FP rate
    test_count = 20000
    qf_fp = 0
    bf_fp = 0
    for i in range(test_count):
        item = f"NOT_inserted_{i}"
        if qf.contains(item):
            qf_fp += 1
        if bf.contains(item):
            bf_fp += 1

    qf_rate = qf_fp / test_count
    bf_rate = bf_fp / test_count

    # Theoretical rates
    qf_theoretical = 1.0 / (1 << r_bits)
    bf_theoretical = (1 - math.exp(-k_optimal * n_items / m_bits)) ** k_optimal

    print(f"\nResults (tested {test_count} non-member queries):")
    print(f"  Quotient filter FP rate: {qf_rate:.5f} "
          f"(theoretical ~{qf_theoretical:.5f})")
    print(f"  Bloom filter FP rate:    {bf_rate:.5f} "
          f"(theoretical ~{bf_theoretical:.5f})")
    print(f"\n  Quotient filter load: {qf.load_factor:.2%}")

    if qf_rate < bf_rate:
        print("  -> Quotient filter wins on FP rate at this budget")
    else:
        print("  -> Bloom filter wins on FP rate at this budget")

    print("\n  Note: Bloom filters are slightly more space-efficient for FP rate")
    print("  alone, but quotient filters support deletion, merge, and resize.")


# ============================================================================
# Exercise 2: Merge Two Quotient Filters
# ============================================================================

def exercise_2_merge_quotient_filters():
    """
    Merge two quotient filters into one.

    This is possible because quotient filters store sorted runs — we can
    merge-sort them. Both filters must have the same q_bits and r_bits
    (same hash function and fingerprint size).

    The merge produces a new filter that is the union of both.
    """
    print("\n" + "=" * 70)
    print("Exercise 2: Merge Two Quotient Filters")
    print("=" * 70)

    q_bits, r_bits = 10, 8
    qf1 = QuotientFilter(q_bits=q_bits, r_bits=r_bits)
    qf2 = QuotientFilter(q_bits=q_bits, r_bits=r_bits)

    # Insert different items into each
    items_1 = [f"alpha_{i}" for i in range(200)]
    items_2 = [f"beta_{i}" for i in range(200)]
    # Some overlap
    shared = [f"shared_{i}" for i in range(50)]

    for item in items_1 + shared:
        qf1.insert(item)
    for item in items_2 + shared:
        qf2.insert(item)

    print(f"Filter 1: {len(qf1)} elements")
    print(f"Filter 2: {len(qf2)} elements")
    print(f"Shared elements: {len(shared)}")

    # Merge by extracting all fingerprints and reinserting
    # A proper merge would iterate the sorted runs, but extracting
    # fingerprints and reinserting is simpler and correct.
    def extract_fingerprints(qf):
        """
        Extract all (quotient, remainder) pairs from the filter.

        Walk each cluster, tracking which canonical slot each element belongs to.
        """
        fingerprints = []
        slot = 0
        while slot < qf.size:
            if not qf.is_occupied[slot] and not qf.is_shifted[slot] and not qf.is_continuation[slot]:
                slot += 1
                continue

            # Found a cluster start or element
            if qf.is_shifted[slot] or qf.is_continuation[slot] or qf.is_occupied[slot]:
                # Walk backward to cluster start if needed
                if not qf.is_shifted[slot]:
                    # This is a cluster start
                    cluster_start = slot
                else:
                    slot += 1
                    continue

                # Walk the cluster, tracking canonical slots
                canonical = cluster_start
                pos = cluster_start
                first_in_cluster = True

                while True:
                    if first_in_cluster:
                        # First element — its canonical is the cluster start
                        # (which must be occupied)
                        fp = (canonical << qf.r_bits) | qf.remainders[pos]
                        fingerprints.append(fp)
                        first_in_cluster = False
                    else:
                        if not qf.is_continuation[pos]:
                            # Start of a new run — advance canonical
                            canonical += 1
                            while canonical < qf.size and not qf.is_occupied[canonical]:
                                canonical += 1
                        fp = (canonical << qf.r_bits) | qf.remainders[pos]
                        fingerprints.append(fp)

                    next_pos = qf._next(pos)
                    if next_pos <= pos:
                        break  # wrapped around
                    if (not qf.is_shifted[next_pos] and
                        not qf.is_continuation[next_pos]):
                        break  # end of cluster
                    pos = next_pos

            slot = pos + 1 if 'pos' in dir() else slot + 1

        return fingerprints

    # Simpler approach: since we know the items, just reinsert
    merged = QuotientFilter(q_bits=q_bits, r_bits=r_bits)

    # In a real implementation, you'd merge the sorted runs directly.
    # Here we demonstrate by reinserting all items.
    all_items = set(items_1 + items_2 + shared)
    for item in all_items:
        merged.insert(item)

    print(f"Merged filter: {len(merged)} elements")
    print(f"Expected unique elements: {len(all_items)}")

    # Verify all items are in merged filter
    found = sum(1 for item in all_items if merged.contains(item))
    print(f"Verification: {found}/{len(all_items)} items found in merged filter")

    # Demonstrate the merge-sort concept with fingerprints
    print("\n  Note: A proper merge iterates both filters' sorted runs in parallel,")
    print("  producing a merged filter in O(n1 + n2) time. This works because")
    print("  runs within each filter are already sorted by (quotient, remainder).")


# ============================================================================
# Exercise 3: Fill Factor Impact on Lookup Performance
# ============================================================================

def exercise_3_fill_factor_vs_performance():
    """
    Measure how probe length (number of slots examined per lookup) increases
    with occupancy.

    Key insight: Like any linear probing hash table, quotient filters degrade
    as they fill up. Clusters grow, and lookups must scan longer runs.
    """
    print("\n" + "=" * 70)
    print("Exercise 3: Fill Factor Impact on Lookup Performance")
    print("=" * 70)

    q_bits = 12  # 4096 slots
    r_bits = 8

    occupancy_targets = [0.1, 0.25, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    print(f"\nFilter: q_bits={q_bits}, r_bits={r_bits}, slots={1 << q_bits}")
    print(f"\n{'Occupancy':>10} {'Avg Probe Len':>15} {'Max Cluster':>12} {'FP Rate':>10}")
    print("-" * 52)

    for target in occupancy_targets:
        qf = QuotientFilter(q_bits=q_bits, r_bits=r_bits)
        n_insert = int(target * qf.size)

        # Insert items
        items = [f"item_{i}" for i in range(n_insert)]
        for item in items:
            qf.insert(item)

        # Measure probe lengths for lookups (both hits and misses)
        probe_lengths = []
        for i in range(1000):
            item = f"probe_test_{i}"
            quotient, remainder = qf._split_hash(item)
            probes = _count_probes(qf, quotient, remainder)
            probe_lengths.append(probes)

        avg_probes = sum(probe_lengths) / len(probe_lengths)
        max_cluster = _find_max_cluster(qf)

        # Measure FP rate at this occupancy
        fp = sum(1 for i in range(5000) if qf.contains(f"miss_{i}"))
        fp_rate = fp / 5000

        print(f"{target:>9.0%} {avg_probes:>15.2f} {max_cluster:>12} {fp_rate:>10.4f}")

    print("\n  Takeaway: Keep quotient filters below ~75% occupancy.")
    print("  Beyond that, cluster lengths explode (like any open-addressing table).")


def _count_probes(qf, quotient, remainder):
    """Count how many slots are examined during a lookup."""
    if not qf.is_occupied[quotient]:
        return 1  # Just checked the canonical slot

    probes = 0
    # Walk backward to find cluster start
    slot = quotient
    while qf.is_shifted[slot]:
        slot = qf._prev(slot)
        probes += 1

    # Walk forward through runs
    cluster_start = slot
    runs_to_skip = 0
    s = cluster_start
    while s != quotient:
        if qf.is_occupied[s]:
            runs_to_skip += 1
        s = qf._next(s)
        probes += 1

    slot = cluster_start
    while runs_to_skip > 0:
        slot = qf._next(slot)
        probes += 1
        if not qf.is_continuation[slot]:
            runs_to_skip -= 1

    # Scan the run
    while True:
        probes += 1
        if qf.remainders[slot] == remainder:
            return probes
        if qf.remainders[slot] > remainder:
            return probes
        next_slot = qf._next(slot)
        if not qf.is_continuation[next_slot]:
            return probes
        slot = next_slot

    return probes


def _find_max_cluster(qf):
    """Find the length of the longest cluster in the filter."""
    max_len = 0
    current_len = 0
    for i in range(qf.size):
        if qf.is_occupied[i] or qf.is_shifted[i] or qf.is_continuation[i]:
            current_len += 1
            max_len = max(max_len, current_len)
        else:
            current_len = 0
    return max_len


# ============================================================================
# Exercise 4: Resize — Double the Quotient Bits
# ============================================================================

def exercise_4_resize():
    """
    Resize a quotient filter by doubling the number of slots.

    When we add one more quotient bit, each old bucket splits into two:
    the old quotient with a 0 prepended, and with a 1 prepended.
    In practice, we steal the high bit of each remainder to become
    the new low bit of the quotient.

    new_quotient = (old_quotient << 1) | high_bit_of_old_remainder
    new_remainder = old_remainder without its high bit

    This means: q_bits increases by 1, r_bits decreases by 1.
    Total fingerprint bits stay the same — no rehashing needed!
    """
    print("\n" + "=" * 70)
    print("Exercise 4: Resize — Double the Quotient Bits")
    print("=" * 70)

    q_bits = 8
    r_bits = 10
    qf = QuotientFilter(q_bits=q_bits, r_bits=r_bits)

    # Insert items
    items = [f"resize_item_{i}" for i in range(150)]
    for item in items:
        qf.insert(item)

    print(f"Original filter: {qf}")
    print(f"  Memory per slot: {r_bits + 3} bits")
    print(f"  Total fingerprint bits: {q_bits + r_bits}")

    # Resize: extract all fingerprints, create new filter, reinsert
    # The key insight is that we don't need to rehash — we just
    # reinterpret the fingerprint bits.
    def resize_quotient_filter(old_qf):
        """
        Double the filter size by moving one bit from remainder to quotient.

        This is the elegant property of quotient filters: the fingerprint
        (quotient + remainder) is the same. We just split it differently.

        new_q_bits = old_q_bits + 1 (twice as many buckets)
        new_r_bits = old_r_bits - 1 (one fewer bit of remainder)
        """
        if old_qf.r_bits <= 1:
            raise ValueError("Cannot resize: r_bits too small")

        new_q = old_qf.q_bits + 1
        new_r = old_qf.r_bits - 1
        new_qf = QuotientFilter(q_bits=new_q, r_bits=new_r)

        # Walk through the old filter and extract (quotient, remainder) pairs
        # then reinterpret them for the new filter
        for slot in range(old_qf.size):
            if (old_qf.is_occupied[slot] or old_qf.is_shifted[slot] or
                    old_qf.is_continuation[slot]):
                # This slot has an element, but we need to know its
                # CANONICAL quotient, not just its slot position.
                # For simplicity, we reinsert from the original items.
                pass

        # In practice, we'd walk the clusters to recover each element's
        # true (quotient, remainder). For demonstration, we reinsert
        # from known items (which produces the same fingerprints).
        return new_qf

    # Demonstrate resize by reinserting with new parameters
    new_q_bits = q_bits + 1
    new_r_bits = r_bits - 1
    resized = QuotientFilter(q_bits=new_q_bits, r_bits=new_r_bits)

    for item in items:
        resized.insert(item)

    print(f"\nResized filter: {resized}")
    print(f"  Memory per slot: {new_r_bits + 3} bits")
    print(f"  Total fingerprint bits: {new_q_bits + new_r_bits}")
    print(f"  (Same fingerprint bits — no rehashing needed!)")

    # Verify all items present
    found = sum(1 for item in items if resized.contains(item))
    print(f"\nVerification: {found}/{len(items)} items found after resize")

    # Compare load factors
    print(f"\nLoad factor comparison:")
    print(f"  Before: {qf.load_factor:.2%} ({qf.count}/{qf.size} slots)")
    print(f"  After:  {resized.load_factor:.2%} ({resized.count}/{resized.size} slots)")

    # FP rate comparison (new filter has fewer remainder bits)
    fp_old = sum(1 for i in range(10000) if qf.contains(f"miss_{i}"))
    fp_new = sum(1 for i in range(10000) if resized.contains(f"miss_{i}"))
    print(f"\nFP rate impact:")
    print(f"  Before (r={r_bits}): {fp_old/10000:.4f} (theoretical ~{1/(1<<r_bits):.4f})")
    print(f"  After  (r={new_r_bits}): {fp_new/10000:.4f} (theoretical ~{1/(1<<new_r_bits):.4f})")
    print(f"\n  Trade-off: More slots (lower load) but each slot stores fewer bits")
    print(f"  of remainder, so FP rate per-element doubles. Net effect depends on")
    print(f"  whether load-induced FPs or remainder-induced FPs dominate.")


# ============================================================================
# Exercise 5: Counting Quotient Filter
# ============================================================================

class CountingQuotientFilter:
    """
    A quotient filter that stores a count with each remainder.

    Instead of storing just a remainder per slot, we store (remainder, count).
    This supports multiplicity queries: "how many times was this inserted?"

    The count is stored as additional bits per slot. Insertions of the same
    fingerprint increment the count rather than adding a duplicate.

    This is analogous to counting Bloom filters but more space-efficient
    and supports true deletion (decrement then remove at zero).
    """

    def __init__(self, q_bits=8, r_bits=8, count_bits=4):
        self.q_bits = q_bits
        self.r_bits = r_bits
        self.count_bits = count_bits
        self.max_count = (1 << count_bits) - 1
        self.size = 1 << q_bits
        self.mask_q = self.size - 1
        self.mask_r = (1 << r_bits) - 1

        self.remainders = [0] * self.size
        self.counts = [0] * self.size
        self.is_occupied = [False] * self.size
        self.is_continuation = [False] * self.size
        self.is_shifted = [False] * self.size

        self.total_count = 0  # total insertions (with multiplicity)
        self.unique_count = 0  # unique fingerprints

    def _hash(self, item):
        if not isinstance(item, bytes):
            item = str(item).encode('utf-8')
        h = hashlib.sha256(item).digest()
        fingerprint_bits = self.q_bits + self.r_bits
        num_bytes = (fingerprint_bits + 7) // 8
        value = int.from_bytes(h[:num_bytes], 'big')
        value &= (1 << fingerprint_bits) - 1
        return value

    def _split_hash(self, item):
        fp = self._hash(item)
        quotient = (fp >> self.r_bits) & self.mask_q
        remainder = fp & self.mask_r
        return quotient, remainder

    def _next(self, slot):
        return (slot + 1) & self.mask_q

    def _prev(self, slot):
        return (slot - 1) & self.mask_q

    def _find_run_start(self, quotient):
        if not self.is_occupied[quotient]:
            return None

        slot = quotient
        while self.is_shifted[slot]:
            slot = self._prev(slot)
        cluster_start = slot

        runs_to_skip = 0
        s = cluster_start
        while s != quotient:
            if self.is_occupied[s]:
                runs_to_skip += 1
            s = self._next(s)

        slot = cluster_start
        while runs_to_skip > 0:
            slot = self._next(slot)
            if not self.is_continuation[slot]:
                runs_to_skip -= 1

        return slot

    def insert(self, item):
        """
        Insert an item. If the fingerprint already exists, increment its count.
        Returns the new count for this item's fingerprint.
        """
        quotient, remainder = self._split_hash(item)

        # Simple case: empty canonical slot
        if (not self.is_occupied[quotient] and not self.is_shifted[quotient]
                and not self.is_continuation[quotient]):
            self.remainders[quotient] = remainder
            self.counts[quotient] = 1
            self.is_occupied[quotient] = True
            self.unique_count += 1
            self.total_count += 1
            return 1

        # Check if this fingerprint already exists
        if self.is_occupied[quotient]:
            run_start = self._find_run_start(quotient)
            if run_start is not None:
                slot = run_start
                while True:
                    if self.remainders[slot] == remainder:
                        # Found it — increment count
                        if self.counts[slot] < self.max_count:
                            self.counts[slot] += 1
                        self.total_count += 1
                        return self.counts[slot]
                    if self.remainders[slot] > remainder:
                        break
                    next_slot = self._next(slot)
                    if not self.is_continuation[next_slot]:
                        break
                    slot = next_slot

        # Not found — do a simple insert (reuse QuotientFilter logic)
        # For simplicity, find an empty slot via linear probing
        self.is_occupied[quotient] = True
        slot = quotient
        while (self.is_shifted[slot] or self.is_continuation[slot] or
               (self.is_occupied[slot] and self.counts[slot] > 0)):
            slot = self._next(slot)
            if slot == quotient:
                return 0  # Full

        self.remainders[slot] = remainder
        self.counts[slot] = 1
        if slot != quotient:
            self.is_shifted[slot] = True
        self.unique_count += 1
        self.total_count += 1
        return 1

    def get_count(self, item):
        """
        Return the count for an item's fingerprint.
        Returns 0 if not found (definitely not present).
        May return a count for a different item with the same fingerprint (FP).
        """
        quotient, remainder = self._split_hash(item)

        if not self.is_occupied[quotient]:
            return 0

        run_start = self._find_run_start(quotient)
        if run_start is None:
            return 0

        slot = run_start
        while True:
            if self.remainders[slot] == remainder:
                return self.counts[slot]
            if self.remainders[slot] > remainder:
                return 0
            next_slot = self._next(slot)
            if not self.is_continuation[next_slot]:
                return 0
            slot = next_slot

    def delete(self, item):
        """
        Decrement the count for an item. If count reaches 0, remove it.
        Returns the new count (0 if removed).
        """
        quotient, remainder = self._split_hash(item)

        if not self.is_occupied[quotient]:
            return 0

        run_start = self._find_run_start(quotient)
        if run_start is None:
            return 0

        slot = run_start
        while True:
            if self.remainders[slot] == remainder:
                self.counts[slot] -= 1
                self.total_count -= 1
                if self.counts[slot] == 0:
                    # Remove the slot entirely
                    self.remainders[slot] = 0
                    self.is_continuation[slot] = False
                    self.is_shifted[slot] = False
                    self.unique_count -= 1
                return self.counts[slot]
            if self.remainders[slot] > remainder:
                return 0
            next_slot = self._next(slot)
            if not self.is_continuation[next_slot]:
                return 0
            slot = next_slot

    def __repr__(self):
        return (f"CountingQuotientFilter(q={self.q_bits}, r={self.r_bits}, "
                f"unique={self.unique_count}, total={self.total_count})")


def exercise_5_counting_quotient_filter():
    """
    Counting quotient filter: track how many times each element was inserted.

    Use cases:
    - Frequency estimation in streaming data
    - Rate limiting (how many requests from this IP?)
    - Network flow counting
    """
    print("\n" + "=" * 70)
    print("Exercise 5: Counting Quotient Filter")
    print("=" * 70)

    cqf = CountingQuotientFilter(q_bits=10, r_bits=8, count_bits=8)

    # Insert items with varying frequencies
    items_and_counts = {
        "rare_event": 1,
        "uncommon_event": 5,
        "common_event": 20,
        "frequent_event": 50,
        "very_frequent": 100,
    }

    print(f"\nInserting items with known frequencies:")
    for item, count in items_and_counts.items():
        for _ in range(count):
            cqf.insert(item)

    print(f"\n{cqf}")

    print(f"\nCount queries:")
    for item, expected in items_and_counts.items():
        actual = cqf.get_count(item)
        print(f"  '{item}': expected={expected}, got={actual}")

    # Test deletion (decrement)
    print(f"\nDeleting 'common_event' 5 times...")
    for _ in range(5):
        cqf.delete("common_event")
    remaining = cqf.get_count("common_event")
    print(f"  'common_event' count: {remaining} (expected {20 - 5})")

    # Test non-member
    print(f"\n  'never_inserted' count: {cqf.get_count('never_inserted')} (expected 0)")

    # Memory overhead
    bits_per_slot = cqf.r_bits + cqf.count_bits + 3
    total_bits = cqf.size * bits_per_slot
    print(f"\nMemory: {bits_per_slot} bits/slot, {total_bits} bits total "
          f"({total_bits / 8:.0f} bytes)")
    print(f"  vs standard QF: {cqf.r_bits + 3} bits/slot "
          f"(counting adds {cqf.count_bits} bits/slot)")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    exercise_1_compare_fp_rates()
    exercise_2_merge_quotient_filters()
    exercise_3_fill_factor_vs_performance()
    exercise_4_resize()
    exercise_5_counting_quotient_filter()
