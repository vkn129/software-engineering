"""
Day 65: Hash Table Collision Resolution -- Four Strategies Compared
====================================================================

We implement four hash tables from scratch:
1. ChainingHashTable     -- linked lists per bucket
2. LinearProbingHashTable -- open addressing, step = 1
3. QuadraticProbingHashTable -- open addressing, step = i^2
4. DoubleHashingTable    -- open addressing, step = h2(key)

Then we run all four on the same workload and compare collision counts,
probe lengths, and timing.

Run: python3 hash_table.py
"""

import time
import random


# ---------------------------------------------------------------------------
# HASH UTILITIES
# ---------------------------------------------------------------------------

def _hash_key(key):
    """Convert any key to a non-negative integer.

    We use Python's built-in hash() but strip the sign bit.
    In production you would use SipHash or similar; here we need
    deterministic behavior within a single process run.
    """
    return hash(key) & 0x7FFFFFFFFFFFFFFF  # mask to positive 64-bit


# ---------------------------------------------------------------------------
# 1. CHAINING HASH TABLE
# ---------------------------------------------------------------------------

class _ChainNode:
    """Singly-linked list node for chaining buckets."""
    __slots__ = ('key', 'value', 'next')

    def __init__(self, key, value, nxt=None):
        self.key = key
        self.value = value
        self.next = nxt


class ChainingHashTable:
    """Hash table with separate chaining.

    Each bucket is the head of a linked list. Collisions just extend the
    chain. Insert is always O(1) (ignoring resize). Load factor can
    exceed 1.0 -- chains simply get longer.

    Trade-off: pointer overhead wastes memory; following pointers causes
    cache misses on every comparison.
    """

    LOAD_THRESHOLD = 0.75

    def __init__(self, capacity=16):
        self._cap = capacity
        self._buckets = [None] * self._cap
        self._size = 0
        self.collision_count = 0
        self.total_probes = 0
        self.total_lookups = 0

    # -- core operations ---------------------------------------------------

    def insert(self, key, value):
        if self._size >= self._cap * self.LOAD_THRESHOLD:
            self._resize(self._cap * 2)

        idx = _hash_key(key) % self._cap
        node = self._buckets[idx]

        # Walk chain looking for existing key
        while node is not None:
            if node.key == key:
                node.value = value  # update
                return
            node = node.next

        # Insert at head
        if self._buckets[idx] is not None:
            self.collision_count += 1
        self._buckets[idx] = _ChainNode(key, value, self._buckets[idx])
        self._size += 1

    def search(self, key):
        self.total_lookups += 1
        idx = _hash_key(key) % self._cap
        node = self._buckets[idx]
        probes = 0
        while node is not None:
            probes += 1
            if node.key == key:
                self.total_probes += probes
                return node.value
            node = node.next
        self.total_probes += max(probes, 1)
        return None

    def delete(self, key):
        idx = _hash_key(key) % self._cap
        node = self._buckets[idx]
        prev = None
        while node is not None:
            if node.key == key:
                if prev is None:
                    self._buckets[idx] = node.next
                else:
                    prev.next = node.next
                self._size -= 1
                return True
            prev = node
            node = node.next
        return False

    # -- resize ------------------------------------------------------------

    def _resize(self, new_cap):
        old = self._buckets
        self._cap = new_cap
        self._buckets = [None] * self._cap
        self._size = 0
        self.collision_count = 0
        for head in old:
            node = head
            while node is not None:
                self.insert(node.key, node.value)
                node = node.next

    # -- helpers -----------------------------------------------------------

    @property
    def load_factor(self):
        return self._size / self._cap

    def avg_probe_length(self):
        if self.total_lookups == 0:
            return 0.0
        return self.total_probes / self.total_lookups

    def __len__(self):
        return self._size

    def __repr__(self):
        return (f"ChainingHashTable(size={self._size}, cap={self._cap}, "
                f"lf={self.load_factor:.2f}, collisions={self.collision_count})")


# ---------------------------------------------------------------------------
# 2. LINEAR PROBING HASH TABLE
# ---------------------------------------------------------------------------

# Sentinel for deleted slots (tombstones)
_EMPTY = object()
_DELETED = object()


class LinearProbingHashTable:
    """Hash table with open addressing and linear probing.

    All entries live in the array itself. On collision, probe sequentially:
    h(k), h(k)+1, h(k)+2, ...

    Best cache locality of any probing strategy (sequential reads), but
    suffers from primary clustering: contiguous runs of occupied slots
    grow quadratically, degrading performance as load factor rises.

    Deletion uses tombstones (_DELETED sentinel). Tombstones tell search
    to keep probing but allow insert to reuse the slot.
    """

    LOAD_THRESHOLD = 0.65  # lower than chaining -- open addressing degrades faster

    def __init__(self, capacity=16):
        self._cap = capacity
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        self._tombstones = 0
        self.collision_count = 0
        self.total_probes = 0
        self.total_lookups = 0

    def insert(self, key, value):
        # Count tombstones in effective load to avoid probe degradation
        if (self._size + self._tombstones) >= self._cap * self.LOAD_THRESHOLD:
            self._resize(self._cap * 2)

        idx = _hash_key(key) % self._cap
        first_deleted = -1
        probes = 0

        while True:
            k = self._keys[idx]
            if k is _EMPTY:
                # Found empty slot -- key does not exist
                if first_deleted >= 0:
                    # Reuse tombstone slot
                    self._keys[first_deleted] = key
                    self._vals[first_deleted] = value
                    self._tombstones -= 1
                else:
                    self._keys[idx] = key
                    self._vals[idx] = value
                if probes > 0:
                    self.collision_count += 1
                self._size += 1
                return
            elif k is _DELETED:
                if first_deleted < 0:
                    first_deleted = idx
            elif k == key:
                self._vals[idx] = value  # update
                return
            probes += 1
            idx = (idx + 1) % self._cap

    def search(self, key):
        self.total_lookups += 1
        idx = _hash_key(key) % self._cap
        probes = 0

        while True:
            k = self._keys[idx]
            probes += 1
            if k is _EMPTY:
                self.total_probes += probes
                return None
            if k is not _DELETED and k == key:
                self.total_probes += probes
                return self._vals[idx]
            idx = (idx + 1) % self._cap
            if probes > self._cap:
                # Safety: full table scan without finding key or empty
                self.total_probes += probes
                return None

    def delete(self, key):
        """Delete using tombstone. Mark slot as _DELETED so probe chains
        remain intact for keys that were inserted past this slot."""
        idx = _hash_key(key) % self._cap
        probes = 0
        while True:
            k = self._keys[idx]
            if k is _EMPTY:
                return False
            if k is not _DELETED and k == key:
                self._keys[idx] = _DELETED
                self._vals[idx] = None
                self._size -= 1
                self._tombstones += 1
                return True
            probes += 1
            idx = (idx + 1) % self._cap
            if probes > self._cap:
                return False

    def _resize(self, new_cap):
        old_keys = self._keys
        old_vals = self._vals
        self._cap = new_cap
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        self._tombstones = 0
        self.collision_count = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY and k is not _DELETED:
                self.insert(k, old_vals[i])

    @property
    def load_factor(self):
        return self._size / self._cap

    def avg_probe_length(self):
        if self.total_lookups == 0:
            return 0.0
        return self.total_probes / self.total_lookups

    def __len__(self):
        return self._size

    def __repr__(self):
        return (f"LinearProbingHashTable(size={self._size}, cap={self._cap}, "
                f"lf={self.load_factor:.2f}, collisions={self.collision_count})")


# ---------------------------------------------------------------------------
# 3. QUADRATIC PROBING HASH TABLE
# ---------------------------------------------------------------------------

class QuadraticProbingHashTable:
    """Hash table with quadratic probing.

    Probe sequence: h(k), h(k)+1, h(k)+4, h(k)+9, ... (offsets = i^2)

    Eliminates primary clustering (probes jump further apart), but
    introduces secondary clustering (keys with the same hash follow
    the same probe sequence).

    Important: does NOT guarantee visiting all slots unless table size
    is prime and load factor < 0.5. We use prime-sized tables.
    """

    LOAD_THRESHOLD = 0.5  # must be <= 0.5 for quadratic probing to work

    def __init__(self, capacity=17):
        # Use a prime capacity for quadratic probing correctness
        self._cap = self._next_prime(capacity)
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        self._tombstones = 0
        self.collision_count = 0
        self.total_probes = 0
        self.total_lookups = 0

    @staticmethod
    def _next_prime(n):
        """Find the next prime >= n."""
        if n <= 2:
            return 2
        if n % 2 == 0:
            n += 1
        while True:
            if all(n % i != 0 for i in range(3, int(n**0.5) + 1, 2)):
                return n
            n += 2

    def insert(self, key, value):
        if (self._size + self._tombstones) >= self._cap * self.LOAD_THRESHOLD:
            self._resize(self._cap * 2)

        h = _hash_key(key) % self._cap
        first_deleted = -1
        i = 0

        while i < self._cap:
            idx = (h + i * i) % self._cap
            k = self._keys[idx]
            if k is _EMPTY:
                target = first_deleted if first_deleted >= 0 else idx
                self._keys[target] = key
                self._vals[target] = value
                if first_deleted >= 0:
                    self._tombstones -= 1
                if i > 0:
                    self.collision_count += 1
                self._size += 1
                return
            elif k is _DELETED:
                if first_deleted < 0:
                    first_deleted = idx
            elif k == key:
                self._vals[idx] = value
                return
            i += 1

        # Should not happen if load factor < 0.5 and table is prime
        self._resize(self._cap * 2)
        self.insert(key, value)

    def search(self, key):
        self.total_lookups += 1
        h = _hash_key(key) % self._cap
        i = 0
        probes = 0

        while i < self._cap:
            idx = (h + i * i) % self._cap
            k = self._keys[idx]
            probes += 1
            if k is _EMPTY:
                self.total_probes += probes
                return None
            if k is not _DELETED and k == key:
                self.total_probes += probes
                return self._vals[idx]
            i += 1

        self.total_probes += probes
        return None

    def delete(self, key):
        h = _hash_key(key) % self._cap
        i = 0
        while i < self._cap:
            idx = (h + i * i) % self._cap
            k = self._keys[idx]
            if k is _EMPTY:
                return False
            if k is not _DELETED and k == key:
                self._keys[idx] = _DELETED
                self._vals[idx] = None
                self._size -= 1
                self._tombstones += 1
                return True
            i += 1
        return False

    def _resize(self, new_cap):
        old_keys = self._keys
        old_vals = self._vals
        self._cap = self._next_prime(new_cap)
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        self._tombstones = 0
        self.collision_count = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY and k is not _DELETED:
                self.insert(k, old_vals[i])

    @property
    def load_factor(self):
        return self._size / self._cap

    def avg_probe_length(self):
        if self.total_lookups == 0:
            return 0.0
        return self.total_probes / self.total_lookups

    def __len__(self):
        return self._size

    def __repr__(self):
        return (f"QuadraticProbingHashTable(size={self._size}, cap={self._cap}, "
                f"lf={self.load_factor:.2f}, collisions={self.collision_count})")


# ---------------------------------------------------------------------------
# 4. DOUBLE HASHING TABLE
# ---------------------------------------------------------------------------

class DoubleHashingTable:
    """Hash table with double hashing.

    Probe sequence: h1(k), h1(k)+h2(k), h1(k)+2*h2(k), ...

    The second hash function h2(k) determines the step size. Since
    different keys have different step sizes, this virtually eliminates
    both primary and secondary clustering.

    h2(k) must never be 0 (would cause infinite loop). We use:
        h2(k) = prime2 - (hash(k) % prime2)
    where prime2 < table_size. This guarantees h2(k) in [1, prime2].
    """

    LOAD_THRESHOLD = 0.65

    def __init__(self, capacity=16):
        self._cap = QuadraticProbingHashTable._next_prime(capacity)
        # Choose a secondary prime smaller than capacity
        self._prime2 = QuadraticProbingHashTable._next_prime(max(self._cap // 2, 3))
        if self._prime2 >= self._cap:
            self._prime2 = max(3, self._cap - 2)
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        self._tombstones = 0
        self.collision_count = 0
        self.total_probes = 0
        self.total_lookups = 0

    def _h2(self, key):
        """Second hash function: determines step size.

        Returns a value in [1, prime2], never 0.
        """
        return self._prime2 - (_hash_key(key) % self._prime2)

    def insert(self, key, value):
        if (self._size + self._tombstones) >= self._cap * self.LOAD_THRESHOLD:
            self._resize(self._cap * 2)

        h1 = _hash_key(key) % self._cap
        step = self._h2(key)
        first_deleted = -1
        probes = 0

        idx = h1
        while probes < self._cap:
            k = self._keys[idx]
            if k is _EMPTY:
                target = first_deleted if first_deleted >= 0 else idx
                self._keys[target] = key
                self._vals[target] = value
                if first_deleted >= 0:
                    self._tombstones -= 1
                if probes > 0:
                    self.collision_count += 1
                self._size += 1
                return
            elif k is _DELETED:
                if first_deleted < 0:
                    first_deleted = idx
            elif k == key:
                self._vals[idx] = value
                return
            probes += 1
            idx = (h1 + probes * step) % self._cap

        # Fallback resize
        self._resize(self._cap * 2)
        self.insert(key, value)

    def search(self, key):
        self.total_lookups += 1
        h1 = _hash_key(key) % self._cap
        step = self._h2(key)
        probes = 0

        idx = h1
        while probes < self._cap:
            k = self._keys[idx]
            probes += 1
            if k is _EMPTY:
                self.total_probes += probes
                return None
            if k is not _DELETED and k == key:
                self.total_probes += probes
                return self._vals[idx]
            idx = (h1 + probes * step) % self._cap

        self.total_probes += probes
        return None

    def delete(self, key):
        h1 = _hash_key(key) % self._cap
        step = self._h2(key)
        probes = 0

        idx = h1
        while probes < self._cap:
            k = self._keys[idx]
            if k is _EMPTY:
                return False
            if k is not _DELETED and k == key:
                self._keys[idx] = _DELETED
                self._vals[idx] = None
                self._size -= 1
                self._tombstones += 1
                return True
            probes += 1
            idx = (h1 + probes * step) % self._cap
        return False

    def _resize(self, new_cap):
        old_keys = self._keys
        old_vals = self._vals
        self._cap = QuadraticProbingHashTable._next_prime(new_cap)
        self._prime2 = QuadraticProbingHashTable._next_prime(max(self._cap // 2, 3))
        if self._prime2 >= self._cap:
            self._prime2 = max(3, self._cap - 2)
        self._keys = [_EMPTY] * self._cap
        self._vals = [None] * self._cap
        self._size = 0
        self._tombstones = 0
        self.collision_count = 0
        for i, k in enumerate(old_keys):
            if k is not _EMPTY and k is not _DELETED:
                self.insert(k, old_vals[i])

    @property
    def load_factor(self):
        return self._size / self._cap

    def avg_probe_length(self):
        if self.total_lookups == 0:
            return 0.0
        return self.total_probes / self.total_lookups

    def __len__(self):
        return self._size

    def __repr__(self):
        return (f"DoubleHashingTable(size={self._size}, cap={self._cap}, "
                f"lf={self.load_factor:.2f}, collisions={self.collision_count})")


# ---------------------------------------------------------------------------
# DEMO: Compare all four on the same workload
# ---------------------------------------------------------------------------

def run_demo():
    print("=" * 70)
    print("HASH TABLE COLLISION RESOLUTION -- FOUR STRATEGIES COMPARED")
    print("=" * 70)

    # -----------------------------------------------------------------------
    # Section 1: Correctness check
    # -----------------------------------------------------------------------
    print("\n--- Section 1: Correctness Check ---\n")

    tables = {
        "Chaining":         ChainingHashTable(capacity=16),
        "Linear Probing":   LinearProbingHashTable(capacity=16),
        "Quadratic Probing": QuadraticProbingHashTable(capacity=17),
        "Double Hashing":   DoubleHashingTable(capacity=16),
    }

    test_data = [("alice", 25), ("bob", 30), ("charlie", 35),
                 ("diana", 28), ("eve", 22), ("frank", 40)]

    for name, table in tables.items():
        for k, v in test_data:
            table.insert(k, v)

        # Verify all keys present
        ok = all(table.search(k) == v for k, v in test_data)
        # Update a key
        table.insert("alice", 99)
        ok = ok and table.search("alice") == 99
        # Delete a key
        table.delete("bob")
        ok = ok and table.search("bob") is None
        ok = ok and len(table) == 5

        status = "PASS" if ok else "FAIL"
        print(f"  {name:20s}: {status}  {table}")

    # -----------------------------------------------------------------------
    # Section 2: Collision count comparison
    # -----------------------------------------------------------------------
    print("\n--- Section 2: Collision Counts (10,000 inserts) ---\n")

    random.seed(42)
    keys = [f"key_{i}" for i in range(10_000)]
    random.shuffle(keys)

    tables = {
        "Chaining":         ChainingHashTable(capacity=64),
        "Linear Probing":   LinearProbingHashTable(capacity=64),
        "Quadratic Probing": QuadraticProbingHashTable(capacity=67),
        "Double Hashing":   DoubleHashingTable(capacity=64),
    }

    for name, table in tables.items():
        for k in keys:
            table.insert(k, 1)
        print(f"  {name:20s}: collisions={table.collision_count:>5}, "
              f"size={len(table):>5}, lf={table.load_factor:.3f}")

    # -----------------------------------------------------------------------
    # Section 3: Average probe length comparison
    # -----------------------------------------------------------------------
    print("\n--- Section 3: Average Probe Length (search all keys) ---\n")

    for name, table in tables.items():
        # Reset probe counters
        table.total_probes = 0
        table.total_lookups = 0
        for k in keys:
            table.search(k)
        print(f"  {name:20s}: avg probes = {table.avg_probe_length():.2f} "
              f"over {table.total_lookups} lookups")

    # -----------------------------------------------------------------------
    # Section 4: Insert + Lookup timing
    # -----------------------------------------------------------------------
    print("\n--- Section 4: Timing Benchmark (50,000 inserts + lookups) ---\n")

    N = 50_000
    bench_keys = [f"bench_{i}" for i in range(N)]
    random.shuffle(bench_keys)

    results = {}
    for name, TableClass in [
        ("Chaining",         ChainingHashTable),
        ("Linear Probing",   LinearProbingHashTable),
        ("Quadratic Probing", QuadraticProbingHashTable),
        ("Double Hashing",   DoubleHashingTable),
    ]:
        table = TableClass()

        t0 = time.perf_counter()
        for k in bench_keys:
            table.insert(k, 1)
        insert_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        for k in bench_keys:
            table.search(k)
        lookup_ms = (time.perf_counter() - t0) * 1000

        results[name] = (insert_ms, lookup_ms, table)

    for name, (ins, lkp, table) in results.items():
        print(f"  {name:20s}: insert={ins:7.1f} ms, lookup={lkp:7.1f} ms, "
              f"avg_probe={table.avg_probe_length():.2f}")

    # -----------------------------------------------------------------------
    # Section 5: Delete and re-search (tombstone impact)
    # -----------------------------------------------------------------------
    print("\n--- Section 5: Tombstone Impact (delete half, then search) ---\n")

    for name, TableClass in [
        ("Linear Probing",   LinearProbingHashTable),
        ("Double Hashing",   DoubleHashingTable),
    ]:
        table = TableClass()
        for k in bench_keys:
            table.insert(k, 1)

        # Delete half the keys
        for k in bench_keys[:N // 2]:
            table.delete(k)

        # Reset counters and search for remaining keys
        table.total_probes = 0
        table.total_lookups = 0
        for k in bench_keys[N // 2:]:
            table.search(k)

        print(f"  {name:20s}: avg probes after 50% deletion = "
              f"{table.avg_probe_length():.2f}")

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS:")
    print("  - Chaining: simplest, never degrades insert, but pointer overhead")
    print("  - Linear probing: best cache locality, but clustering hurts at high load")
    print("  - Quadratic probing: reduces clustering, needs prime table size")
    print("  - Double hashing: eliminates clustering, slightly more computation")
    print("  - Tombstones degrade open addressing -- monitor and rehash periodically")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
