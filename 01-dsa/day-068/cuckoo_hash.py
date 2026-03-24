"""
Day 68: Cuckoo Hashing

O(1) WORST CASE lookup. Not amortized. Not expected. Worst case.
Two hash functions, two tables. Lookup checks exactly two slots, always.
Insert evicts occupants into their alternate table, like a cuckoo bird
pushing eggs out of other birds' nests.
"""

import random
import math


class CuckooHashTable:
    """
    Two-table cuckoo hash table.

    Why two tables instead of one table with two regions?
    Conceptual clarity: each key has exactly one slot per table.
    In practice, you can use one array with two hash functions mapping
    to different halves -- the logic is identical.
    """

    MAX_EVICTIONS = 500  # cycle detection threshold

    def __init__(self, capacity=16):
        # capacity per table, so total space is 2 * capacity
        self.capacity = capacity
        self.size = 0
        self.table1 = [None] * capacity  # stores (key, value) tuples
        self.table2 = [None] * capacity
        # random seeds for hash functions -- changed on rehash
        self._seed1 = random.randint(0, 2**32)
        self._seed2 = random.randint(0, 2**32)

    def _hash1(self, key):
        """First hash function. Maps key to table1 index."""
        # Multiply-shift hashing with a random seed
        h = hash((key, self._seed1))
        return h % self.capacity

    def _hash2(self, key):
        """Second hash function. Must be independent from _hash1."""
        h = hash((key, self._seed2))
        return h % self.capacity

    def lookup(self, key):
        """
        O(1) WORST CASE lookup.

        Check exactly two slots. No loops, no chains, no traversals.
        This is the entire point of cuckoo hashing.
        """
        idx1 = self._hash1(key)
        if self.table1[idx1] is not None and self.table1[idx1][0] == key:
            return self.table1[idx1][1]

        idx2 = self._hash2(key)
        if self.table2[idx2] is not None and self.table2[idx2][0] == key:
            return self.table2[idx2][1]

        raise KeyError(key)

    def __contains__(self, key):
        try:
            self.lookup(key)
            return True
        except KeyError:
            return False

    def delete(self, key):
        """
        O(1) WORST CASE delete.

        Same logic as lookup: check two slots, clear if found.
        """
        idx1 = self._hash1(key)
        if self.table1[idx1] is not None and self.table1[idx1][0] == key:
            self.table1[idx1] = None
            self.size -= 1
            return

        idx2 = self._hash2(key)
        if self.table2[idx2] is not None and self.table2[idx2][0] == key:
            self.table2[idx2] = None
            self.size -= 1
            return

        raise KeyError(key)

    def insert(self, key, value):
        """
        O(1) amortized insert.

        Try table1 first. If occupied, evict the occupant and re-insert it
        into table2. The evicted key may in turn evict another key, creating
        an eviction chain. If the chain exceeds MAX_EVICTIONS, we have a cycle
        and must rehash with new hash functions.
        """
        # Check if key already exists -- update in place
        idx1 = self._hash1(key)
        if self.table1[idx1] is not None and self.table1[idx1][0] == key:
            self.table1[idx1] = (key, value)
            return

        idx2 = self._hash2(key)
        if self.table2[idx2] is not None and self.table2[idx2][0] == key:
            self.table2[idx2] = (key, value)
            return

        # New key -- insert with eviction chain
        self._do_insert(key, value)
        self.size += 1

    def _do_insert(self, key, value):
        """
        Core insertion with eviction chain logic.

        Returns the eviction chain for observability (used in demo/practice).
        """
        eviction_chain = []
        current_key, current_value = key, value
        use_table1 = True  # alternate between tables

        while True:
            placed = False
            for _ in range(self.MAX_EVICTIONS):
                if use_table1:
                    idx = self._hash1(current_key)
                    if self.table1[idx] is None:
                        self.table1[idx] = (current_key, current_value)
                        placed = True
                        break
                    # Evict the occupant
                    evicted = self.table1[idx]
                    eviction_chain.append(evicted[0])
                    self.table1[idx] = (current_key, current_value)
                    current_key, current_value = evicted
                else:
                    idx = self._hash2(current_key)
                    if self.table2[idx] is None:
                        self.table2[idx] = (current_key, current_value)
                        placed = True
                        break
                    evicted = self.table2[idx]
                    eviction_chain.append(evicted[0])
                    self.table2[idx] = (current_key, current_value)
                    current_key, current_value = evicted

                use_table1 = not use_table1

            if placed:
                return eviction_chain

            # Eviction loop detected -- rehash and retry the displaced key
            self._rehash()
            use_table1 = True

    def insert_tracked(self, key, value):
        """
        Insert and return the eviction chain (for visualization/debugging).
        """
        idx1 = self._hash1(key)
        if self.table1[idx1] is not None and self.table1[idx1][0] == key:
            self.table1[idx1] = (key, value)
            return []
        idx2 = self._hash2(key)
        if self.table2[idx2] is not None and self.table2[idx2][0] == key:
            self.table2[idx2] = (key, value)
            return []

        chain = self._do_insert(key, value)
        self.size += 1
        return chain

    def _rehash(self):
        """
        Pick new hash functions and re-insert everything.

        Why new hash functions? The current functions created a cycle in the
        eviction graph. Different functions produce a different graph topology
        that (probably) has no cycle for the current key set.

        Uses a retry loop instead of recursion to avoid stack overflow.
        """
        old_items = []
        for entry in self.table1:
            if entry is not None:
                old_items.append(entry)
        for entry in self.table2:
            if entry is not None:
                old_items.append(entry)

        # Double capacity if load factor is too high
        load_factor = len(old_items) / (2 * self.capacity)
        if load_factor > 0.4:
            self.capacity *= 2

        # Retry with new hash functions until all items fit without cycles
        for _attempt in range(20):
            self.table1 = [None] * self.capacity
            self.table2 = [None] * self.capacity
            self._seed1 = random.randint(0, 2**32)
            self._seed2 = random.randint(0, 2**32)

            success = True
            for key, value in old_items:
                if not self._try_insert_no_rehash(key, value):
                    success = False
                    break

            if success:
                return

            # Failed -- try again with bigger capacity
            self.capacity *= 2

        raise RuntimeError("Rehash failed after multiple attempts")

    def _try_insert_no_rehash(self, key, value):
        """Attempt insert without triggering rehash. Returns False if cycle detected."""
        current_key, current_value = key, value
        use_table1 = True

        for _ in range(self.MAX_EVICTIONS):
            if use_table1:
                idx = self._hash1(current_key)
                if self.table1[idx] is None:
                    self.table1[idx] = (current_key, current_value)
                    return True
                evicted = self.table1[idx]
                self.table1[idx] = (current_key, current_value)
                current_key, current_value = evicted
            else:
                idx = self._hash2(current_key)
                if self.table2[idx] is None:
                    self.table2[idx] = (current_key, current_value)
                    return True
                evicted = self.table2[idx]
                self.table2[idx] = (current_key, current_value)
                current_key, current_value = evicted

            use_table1 = not use_table1

        return False  # cycle detected

    def load_factor(self):
        return self.size / (2 * self.capacity)

    def items(self):
        for entry in self.table1:
            if entry is not None:
                yield entry
        for entry in self.table2:
            if entry is not None:
                yield entry

    def __repr__(self):
        return (
            f"CuckooHashTable(size={self.size}, capacity={self.capacity}x2, "
            f"load={self.load_factor():.1%})"
        )


class CuckooHashTable3:
    """
    Three-table variant of cuckoo hashing.

    Why three tables? With 2 tables, the max load factor is ~50%.
    With 3 tables and 3 hash functions, the threshold rises to ~91%.
    The tradeoff: lookup now checks 3 slots instead of 2 (still O(1) worst case).

    This is the version used in practice (e.g., DPDK for network packet processing).
    """

    MAX_EVICTIONS = 500

    def __init__(self, capacity=16):
        self.capacity = capacity
        self.size = 0
        self.table1 = [None] * capacity
        self.table2 = [None] * capacity
        self.table3 = [None] * capacity
        self._seed1 = random.randint(0, 2**32)
        self._seed2 = random.randint(0, 2**32)
        self._seed3 = random.randint(0, 2**32)

    def _hash1(self, key):
        return hash((key, self._seed1)) % self.capacity

    def _hash2(self, key):
        return hash((key, self._seed2)) % self.capacity

    def _hash3(self, key):
        return hash((key, self._seed3)) % self.capacity

    def lookup(self, key):
        """O(1) worst case -- checks exactly 3 slots."""
        idx1 = self._hash1(key)
        if self.table1[idx1] is not None and self.table1[idx1][0] == key:
            return self.table1[idx1][1]

        idx2 = self._hash2(key)
        if self.table2[idx2] is not None and self.table2[idx2][0] == key:
            return self.table2[idx2][1]

        idx3 = self._hash3(key)
        if self.table3[idx3] is not None and self.table3[idx3][0] == key:
            return self.table3[idx3][1]

        raise KeyError(key)

    def __contains__(self, key):
        try:
            self.lookup(key)
            return True
        except KeyError:
            return False

    def delete(self, key):
        """O(1) worst case delete -- checks exactly 3 slots."""
        for table, hash_fn in [
            (self.table1, self._hash1),
            (self.table2, self._hash2),
            (self.table3, self._hash3),
        ]:
            idx = hash_fn(key)
            if table[idx] is not None and table[idx][0] == key:
                table[idx] = None
                self.size -= 1
                return
        raise KeyError(key)

    def insert(self, key, value):
        # Update if exists
        for table, hash_fn in [
            (self.table1, self._hash1),
            (self.table2, self._hash2),
            (self.table3, self._hash3),
        ]:
            idx = hash_fn(key)
            if table[idx] is not None and table[idx][0] == key:
                table[idx] = (key, value)
                return

        self._do_insert(key, value)
        self.size += 1

    def _do_insert(self, key, value):
        current_key, current_value = key, value
        table_idx = 0

        while True:
            tables = [self.table1, self.table2, self.table3]
            hash_fns = [self._hash1, self._hash2, self._hash3]
            placed = False

            for _ in range(self.MAX_EVICTIONS):
                table = tables[table_idx]
                idx = hash_fns[table_idx](current_key)

                if table[idx] is None:
                    table[idx] = (current_key, current_value)
                    placed = True
                    break

                evicted = table[idx]
                table[idx] = (current_key, current_value)
                current_key, current_value = evicted
                table_idx = (table_idx + 1) % 3

            if placed:
                return

            self._rehash()
            table_idx = 0

    def _rehash(self):
        old_items = []
        for table in [self.table1, self.table2, self.table3]:
            for entry in table:
                if entry is not None:
                    old_items.append(entry)

        load_factor = len(old_items) / (3 * self.capacity)
        if load_factor > 0.8:
            self.capacity *= 2

        for _attempt in range(20):
            self.table1 = [None] * self.capacity
            self.table2 = [None] * self.capacity
            self.table3 = [None] * self.capacity
            self._seed1 = random.randint(0, 2**32)
            self._seed2 = random.randint(0, 2**32)
            self._seed3 = random.randint(0, 2**32)

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
        """Attempt insert without triggering rehash. Returns False if cycle detected."""
        tables = [self.table1, self.table2, self.table3]
        hash_fns = [self._hash1, self._hash2, self._hash3]
        current_key, current_value = key, value
        table_idx = 0

        for _ in range(self.MAX_EVICTIONS):
            table = tables[table_idx]
            idx = hash_fns[table_idx](current_key)

            if table[idx] is None:
                table[idx] = (current_key, current_value)
                return True

            evicted = table[idx]
            table[idx] = (current_key, current_value)
            current_key, current_value = evicted
            table_idx = (table_idx + 1) % 3

        return False

    def load_factor(self):
        return self.size / (3 * self.capacity)

    def items(self):
        for table in [self.table1, self.table2, self.table3]:
            for entry in table:
                if entry is not None:
                    yield entry

    def __repr__(self):
        return (
            f"CuckooHashTable3(size={self.size}, capacity={self.capacity}x3, "
            f"load={self.load_factor():.1%})"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    print("=" * 70)
    print("CUCKOO HASHING -- O(1) WORST CASE LOOKUP")
    print("=" * 70)

    # --- 2-table variant ---
    print("\n--- 2-Table Cuckoo Hash ---\n")
    ht = CuckooHashTable(capacity=8)

    # Insert with eviction chain tracking
    keys_to_insert = [
        ("alice", 100), ("bob", 200), ("carol", 300), ("dave", 400),
        ("eve", 500), ("frank", 600), ("grace", 700),
    ]

    rehash_count = 0
    for key, val in keys_to_insert:
        old_cap = ht.capacity
        chain = ht.insert_tracked(key, val)
        if ht.capacity != old_cap:
            rehash_count += 1
            print(f"  INSERT '{key}' -> REHASH triggered! "
                  f"(capacity {old_cap} -> {ht.capacity})")
        elif chain:
            print(f"  INSERT '{key}' -> eviction chain: {chain}")
        else:
            print(f"  INSERT '{key}' -> placed directly (no eviction)")

    print(f"\n  {ht}")
    print(f"  Rehash events: {rehash_count}")

    # Demonstrate O(1) worst-case lookup
    print("\n  Lookup (O(1) worst case, always checks exactly 2 slots):")
    for key in ["alice", "dave", "grace"]:
        val = ht.lookup(key)
        print(f"    lookup('{key}') = {val}")

    # Delete
    print("\n  Delete (O(1) worst case):")
    ht.delete("bob")
    print(f"    deleted 'bob', 'bob' in table: {'bob' in ht}")

    # --- 3-table variant ---
    print("\n--- 3-Table Cuckoo Hash (higher load factor) ---\n")
    ht3 = CuckooHashTable3(capacity=8)

    # Insert more items -- 3 tables tolerate higher load
    for i in range(15):
        ht3.insert(f"key_{i}", i * 10)

    print(f"  {ht3}")
    print(f"  All lookups succeed:")
    for i in range(15):
        val = ht3.lookup(f"key_{i}")
        assert val == i * 10
    print(f"    Verified all 15 keys with correct values.")

    # --- Compare load factor tolerance ---
    print("\n--- Load Factor Comparison ---\n")

    # 2-table: insert until rehash
    ht2_test = CuckooHashTable(capacity=32)
    for i in range(25):
        ht2_test.insert(i, i)
    print(f"  2-table: {ht2_test}")

    # 3-table: insert more before needing rehash
    ht3_test = CuckooHashTable3(capacity=32)
    for i in range(70):
        ht3_test.insert(i, i)
    print(f"  3-table: {ht3_test}")

    print("\n  The 3-table variant sustains much higher load factors")
    print("  before rehashing, at the cost of 3 probes per lookup instead of 2.")

    # --- Guaranteed O(1) proof ---
    print("\n--- O(1) Worst Case Proof ---\n")
    print("  In chaining, a bad hash function can put all N keys in one bucket.")
    print("  Lookup becomes O(N). In cuckoo hashing, lookup ALWAYS checks")
    print("  exactly 2 (or 3) slots regardless of how many keys are stored.")
    print("  This is the key insight: deterministic, not probabilistic, performance.")

    print("\n" + "=" * 70)
    print("END OF DEMO")
    print("=" * 70)


if __name__ == "__main__":
    demo()
