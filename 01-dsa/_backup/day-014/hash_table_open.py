"""
Day 14: Hash Table with Open Addressing -- Built from Scratch
==============================================================

Open addressing stores all entries directly in the array. No linked lists,
no pointer chasing, no per-entry heap allocation. When a collision occurs,
we probe for the next empty slot following a deterministic sequence.

We implement three probing strategies:
1. Linear probing -- simple but clustering-prone
2. Quadratic probing -- reduces clustering
3. Double hashing -- eliminates clustering

Then we explore tombstones, resize behavior, Robin Hood hashing,
and compare everything against Python's dict.

Run: python hash_table_open.py
"""

import time
import random


# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

EMPTY = object()      # sentinel for empty slots
TOMBSTONE = object()  # sentinel for deleted slots


# ---------------------------------------------------------------------------
# HASH TABLE WITH OPEN ADDRESSING
# ---------------------------------------------------------------------------

class HashTableOpen:
    """Hash table using open addressing with configurable probing strategy.

    All entries live in the main array. No external data structures.
    This is the approach Python's dict, Rust's HashMap, and Google's
    Swiss Table all use (with variations).

    The three probing strategies demonstrate the clustering trade-off:
    - linear:    fast but forms clusters, O(1/(1-alpha)^2) expected probes
    - quadratic: breaks primary clusters, but secondary clustering remains
    - double:    eliminates both, but requires a second hash function
    """

    LOAD_FACTOR_THRESHOLD = 0.7  # Must stay below 1.0 for open addressing

    def __init__(self, initial_capacity=16, probe_strategy='linear'):
        self._capacity = initial_capacity
        self._keys = [EMPTY] * self._capacity
        self._values = [EMPTY] * self._capacity
        self._size = 0           # live entries
        self._tombstones = 0     # deleted entries (still occupy probe chains)
        self._probe_strategy = probe_strategy
        self._total_probes = 0
        self._total_operations = 0
        self._resize_count = 0

    def _hash(self, key):
        """Primary hash function."""
        # Use Python's built-in hash for simplicity.
        # In production, you'd use SipHash, xxHash, etc.
        return hash(key) % self._capacity

    def _hash2(self, key):
        """Secondary hash function for double hashing.

        Must never return 0 (infinite loop). Must be coprime with capacity.
        Common approach: PRIME - (hash(key) % PRIME), where PRIME < capacity.
        """
        prime = max(1, self._capacity - 1)
        # Find a prime less than capacity for better distribution
        while prime > 1:
            is_prime = True
            for i in range(2, int(prime ** 0.5) + 1):
                if prime % i == 0:
                    is_prime = False
                    break
            if is_prime:
                break
            prime -= 1
        return prime - (hash(key) % prime) if prime > 1 else 1

    def _probe(self, key, step):
        """Compute the probe index for a given step number.

        Linear:    h(k) + step
        Quadratic: h(k) + step^2
        Double:    h(k) + step * h2(k)
        """
        h = self._hash(key)
        if self._probe_strategy == 'linear':
            return (h + step) % self._capacity
        elif self._probe_strategy == 'quadratic':
            return (h + step * step) % self._capacity
        elif self._probe_strategy == 'double':
            return (h + step * self._hash2(key)) % self._capacity
        else:
            raise ValueError(f"Unknown probe strategy: {self._probe_strategy}")

    @property
    def load_factor(self):
        """Effective load factor includes tombstones.

        Tombstones still participate in probe chains, so they contribute
        to the "fullness" that degrades performance. This is why we count
        them when deciding to resize.
        """
        return (self._size + self._tombstones) / self._capacity

    def put(self, key, value):
        """Insert or update a key-value pair.

        If we find a tombstone during insertion, we can reuse that slot.
        But we must continue probing to check for an existing key (to
        avoid duplicates).
        """
        if self.load_factor >= self.LOAD_FACTOR_THRESHOLD:
            self._resize(self._capacity * 2)

        self._total_operations += 1
        first_tombstone = None

        for step in range(self._capacity):
            idx = self._probe(key, step)
            self._total_probes += 1

            if self._keys[idx] is EMPTY:
                # Found an empty slot -- key does not exist
                if first_tombstone is not None:
                    # Reuse the tombstone slot (optimization)
                    self._keys[first_tombstone] = key
                    self._values[first_tombstone] = value
                    self._tombstones -= 1
                else:
                    self._keys[idx] = key
                    self._values[idx] = value
                self._size += 1
                return

            if self._keys[idx] is TOMBSTONE:
                if first_tombstone is None:
                    first_tombstone = idx
                continue

            if self._keys[idx] == key:
                # Key exists -- update value
                self._values[idx] = value
                return

        # Should not reach here if load factor is maintained properly
        raise RuntimeError("Hash table is full -- this should not happen")

    def get(self, key, default=None):
        """Retrieve the value for a key. O(1) average."""
        self._total_operations += 1

        for step in range(self._capacity):
            idx = self._probe(key, step)
            self._total_probes += 1

            if self._keys[idx] is EMPTY:
                return default  # Key not found

            if self._keys[idx] is TOMBSTONE:
                continue  # Skip tombstones, keep probing

            if self._keys[idx] == key:
                return self._values[idx]

        return default

    def delete(self, key):
        """Delete a key by replacing it with a tombstone.

        We CANNOT simply empty the slot because that would break the probe
        chain for keys that were inserted after this one and probed past
        this position.

        The tombstone tells future lookups "keep going, something was here."
        The tombstone tells future inserts "you can reuse this slot."
        """
        for step in range(self._capacity):
            idx = self._probe(key, step)

            if self._keys[idx] is EMPTY:
                return False  # Key not found

            if self._keys[idx] is TOMBSTONE:
                continue

            if self._keys[idx] == key:
                self._keys[idx] = TOMBSTONE
                self._values[idx] = TOMBSTONE
                self._size -= 1
                self._tombstones += 1
                return True

        return False

    def _resize(self, new_capacity):
        """Resize and rehash. Also cleans up tombstones.

        After resize, there are zero tombstones -- every slot is either
        EMPTY or holds a live entry. This is the "compaction" step that
        prevents tombstone accumulation from degrading performance.
        """
        self._resize_count += 1
        old_keys = self._keys
        old_values = self._values

        self._capacity = new_capacity
        self._keys = [EMPTY] * self._capacity
        self._values = [EMPTY] * self._capacity
        self._size = 0
        self._tombstones = 0

        for i in range(len(old_keys)):
            if old_keys[i] is not EMPTY and old_keys[i] is not TOMBSTONE:
                self.put(old_keys[i], old_values[i])

    def __contains__(self, key):
        return self.get(key, sentinel := object()) is not sentinel

    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        result = self.get(key, sentinel := object())
        if result is sentinel:
            raise KeyError(key)
        return result

    def __len__(self):
        return self._size

    def stats(self):
        """Return performance statistics."""
        return {
            'size': self._size,
            'capacity': self._capacity,
            'tombstones': self._tombstones,
            'load_factor': self.load_factor,
            'live_load_factor': self._size / self._capacity,
            'resizes': self._resize_count,
            'avg_probes': (
                self._total_probes / self._total_operations
                if self._total_operations > 0 else 0
            ),
            'probe_strategy': self._probe_strategy,
        }

    def visualize(self, max_slots=40):
        """Show the internal state of the table. Useful for understanding probing."""
        n = min(self._capacity, max_slots)
        cells = []
        for i in range(n):
            if self._keys[i] is EMPTY:
                cells.append('.')
            elif self._keys[i] is TOMBSTONE:
                cells.append('X')
            else:
                cells.append('#')
        suffix = f" ...({self._capacity - n} more)" if self._capacity > n else ""
        return '[' + ''.join(cells) + ']' + suffix


# ---------------------------------------------------------------------------
# SECTION 1: Basic Operations Demo
# ---------------------------------------------------------------------------

print("=" * 70)
print("SECTION 1: Open Addressing -- Basic Operations")
print("=" * 70)

ht = HashTableOpen(initial_capacity=16, probe_strategy='linear')

entries = [
    ("alice", 25), ("bob", 30), ("charlie", 35),
    ("diana", 28), ("eve", 22), ("frank", 40),
    ("grace", 33), ("henry", 29), ("ivy", 27),
]

for key, value in entries:
    ht.put(key, value)
    print(f"  put('{key}', {value:>2})  table: {ht.visualize()}")

print(f"\n  get('alice')   = {ht.get('alice')}")
print(f"  get('charlie') = {ht.get('charlie')}")
print(f"  get('missing') = {ht.get('missing', 'NOT FOUND')}")

print(f"\n  Deleting 'bob' and 'diana'...")
ht.delete('bob')
ht.delete('diana')
print(f"  table: {ht.visualize()}")
print(f"  (X = tombstone: slot is deleted but probe chain continues through it)")
print(f"  get('bob') = {ht.get('bob', 'NOT FOUND')}")
print(f"  get('eve') = {ht.get('eve')}  (still reachable past the tombstone)")


# ---------------------------------------------------------------------------
# SECTION 2: Clustering Visualization
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 2: Clustering Problem -- Linear vs Quadratic vs Double Hashing")
print("=" * 70)

print("""
  Linear probing creates clusters: runs of filled slots that grow
  because any key that hashes into a cluster must probe past it.
  Quadratic probing and double hashing break up these clusters.
""")

random.seed(42)
keys = [f"k{i}" for i in range(30)]

for strategy in ['linear', 'quadratic', 'double']:
    ht = HashTableOpen(initial_capacity=64, probe_strategy=strategy)
    for key in keys:
        ht.put(key, 0)
    s = ht.stats()
    print(f"\n  {strategy.upper()} probing ({len(keys)} entries in 64 slots):")
    print(f"    Visualization: {ht.visualize(64)}")
    print(f"    Avg probes per operation: {s['avg_probes']:.2f}")

    # Measure probe chain lengths for lookups
    ht._total_probes = 0
    ht._total_operations = 0
    for key in keys:
        ht.get(key)
    s = ht.stats()
    print(f"    Avg probes per lookup:    {s['avg_probes']:.2f}")


# ---------------------------------------------------------------------------
# SECTION 3: Probe Length vs Load Factor
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 3: How Load Factor Destroys Performance")
print("=" * 70)

print("""
  As load factor increases, average probe length grows.
  For linear probing, the growth is dramatic near LF=1.0.
  This is why open addressing MUST resize before getting full.
""")

print(f"\n  {'Load Factor':>12} {'Linear':>10} {'Quadratic':>12} {'Double':>10}")
print("  " + "-" * 50)

for target_lf in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]:
    results = {}
    for strategy in ['linear', 'quadratic', 'double']:
        capacity = 1000
        n = int(capacity * target_lf)
        ht = HashTableOpen(initial_capacity=capacity, probe_strategy=strategy)
        # Disable auto-resize for this experiment
        ht.LOAD_FACTOR_THRESHOLD = 1.0

        random.seed(42)
        test_keys = [f"loadtest_{i}" for i in range(n)]
        for key in test_keys:
            ht.put(key, 0)

        # Measure lookup probes
        ht._total_probes = 0
        ht._total_operations = 0
        for key in test_keys:
            ht.get(key)
        results[strategy] = ht.stats()['avg_probes']

    print(f"  {target_lf:>12.2f} {results['linear']:>10.2f} "
          f"{results['quadratic']:>12.2f} {results['double']:>10.2f}")


# ---------------------------------------------------------------------------
# SECTION 4: Tombstone Degradation
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 4: Tombstone Degradation -- The Cost of Deletion")
print("=" * 70)

print("""
  Inserting and deleting many entries accumulates tombstones.
  Tombstones extend probe chains without adding useful data.
  After enough churn, performance degrades even at low live load.
  Solution: periodic resize (compaction) removes all tombstones.
""")

ht = HashTableOpen(initial_capacity=1024, probe_strategy='linear')
ht.LOAD_FACTOR_THRESHOLD = 0.95  # High threshold to see degradation

# Insert 500 entries
keys_phase1 = [f"phase1_{i}" for i in range(500)]
for key in keys_phase1:
    ht.put(key, 0)

print(f"\n  After inserting 500 entries:")
print(f"    Live: {ht._size}, Tombstones: {ht._tombstones}, "
      f"LF: {ht.load_factor:.3f}")

# Delete 480 of them
for key in keys_phase1[:480]:
    ht.delete(key)

print(f"\n  After deleting 480 entries:")
print(f"    Live: {ht._size}, Tombstones: {ht._tombstones}, "
      f"LF: {ht.load_factor:.3f}")

# Measure lookup performance with all those tombstones
ht._total_probes = 0
ht._total_operations = 0
for key in keys_phase1[480:]:  # Look up the 20 remaining
    ht.get(key)
tombstone_probes = ht.stats()['avg_probes']
print(f"    Avg probes to find remaining entries: {tombstone_probes:.2f}")

# Now compact by forcing a resize
ht._resize(1024)
ht._total_probes = 0
ht._total_operations = 0
for key in keys_phase1[480:]:
    ht.get(key)
clean_probes = ht.stats()['avg_probes']
print(f"\n  After compaction (resize):")
print(f"    Live: {ht._size}, Tombstones: {ht._tombstones}, "
      f"LF: {ht.load_factor:.3f}")
print(f"    Avg probes to find remaining entries: {clean_probes:.2f}")
print(f"    Improvement: {tombstone_probes/clean_probes:.1f}x fewer probes")


# ---------------------------------------------------------------------------
# SECTION 5: Robin Hood Hashing
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 5: Robin Hood Hashing -- Fairer Probe Distribution")
print("=" * 70)

class RobinHoodHashTable:
    """Linear probing with Robin Hood insertion.

    Key idea: during insertion, if the new key has traveled FURTHER
    from its ideal slot than the current occupant, swap them. Continue
    inserting the displaced entry. This "steals from the rich (short
    probe) to give to the poor (long probe)."

    Result: much lower VARIANCE in probe lengths. The worst case is
    dramatically better, even though the average is similar.
    """

    def __init__(self, capacity=64):
        self._capacity = capacity
        self._keys = [EMPTY] * capacity
        self._values = [EMPTY] * capacity
        self._size = 0

    def _hash(self, key):
        return hash(key) % self._capacity

    def _probe_distance(self, stored_key, current_idx):
        """How far is this entry from its ideal slot?"""
        ideal = self._hash(stored_key)
        return (current_idx - ideal) % self._capacity

    def put(self, key, value):
        if (self._size / self._capacity) >= 0.7:
            self._resize(self._capacity * 2)

        idx = self._hash(key)
        dist = 0

        while True:
            if self._keys[idx] is EMPTY:
                self._keys[idx] = key
                self._values[idx] = value
                self._size += 1
                return

            if self._keys[idx] == key:
                self._values[idx] = value
                return

            # Robin Hood: if we've traveled further, swap
            existing_dist = self._probe_distance(self._keys[idx], idx)
            if dist > existing_dist:
                # Swap: we take this spot, displaced entry continues
                key, self._keys[idx] = self._keys[idx], key
                value, self._values[idx] = self._values[idx], value
                dist = existing_dist

            idx = (idx + 1) % self._capacity
            dist += 1

    def get(self, key, default=None):
        idx = self._hash(key)
        dist = 0

        while True:
            if self._keys[idx] is EMPTY:
                return default

            if self._keys[idx] == key:
                return self._values[idx]

            # Robin Hood optimization: if current entry's distance is less
            # than ours, the key cannot exist (it would have been swapped)
            if self._keys[idx] is not TOMBSTONE:
                existing_dist = self._probe_distance(self._keys[idx], idx)
                if dist > existing_dist:
                    return default  # Early termination!

            idx = (idx + 1) % self._capacity
            dist += 1

    def _resize(self, new_capacity):
        old_keys = self._keys
        old_values = self._values
        self._capacity = new_capacity
        self._keys = [EMPTY] * new_capacity
        self._values = [EMPTY] * new_capacity
        self._size = 0
        for i in range(len(old_keys)):
            if old_keys[i] is not EMPTY and old_keys[i] is not TOMBSTONE:
                self.put(old_keys[i], old_values[i])

    def probe_distances(self):
        """Return the probe distance for every live entry."""
        dists = []
        for i in range(self._capacity):
            if self._keys[i] is not EMPTY and self._keys[i] is not TOMBSTONE:
                dists.append(self._probe_distance(self._keys[i], i))
        return dists


# Compare probe distance distribution: standard vs Robin Hood
random.seed(42)
test_keys = [f"rh_{i}" for i in range(400)]

# Standard linear probing
ht_std = HashTableOpen(initial_capacity=1024, probe_strategy='linear')
for key in test_keys:
    ht_std.put(key, 0)

std_dists = []
for i in range(ht_std._capacity):
    if ht_std._keys[i] is not EMPTY and ht_std._keys[i] is not TOMBSTONE:
        ideal = hash(ht_std._keys[i]) % ht_std._capacity
        dist = (i - ideal) % ht_std._capacity
        std_dists.append(dist)

# Robin Hood
ht_rh = RobinHoodHashTable(capacity=1024)
for key in test_keys:
    ht_rh.put(key, 0)
rh_dists = ht_rh.probe_distances()

print(f"\n  400 entries in 1024 slots (LF = 0.39)")
print(f"\n  Standard Linear Probing:")
print(f"    Max probe distance: {max(std_dists)}")
print(f"    Avg probe distance: {sum(std_dists)/len(std_dists):.2f}")
print(f"    Std dev:            {(sum((d - sum(std_dists)/len(std_dists))**2 for d in std_dists)/len(std_dists))**0.5:.2f}")

print(f"\n  Robin Hood Hashing:")
print(f"    Max probe distance: {max(rh_dists)}")
print(f"    Avg probe distance: {sum(rh_dists)/len(rh_dists):.2f}")
print(f"    Std dev:            {(sum((d - sum(rh_dists)/len(rh_dists))**2 for d in rh_dists)/len(rh_dists))**0.5:.2f}")

print(f"\n  Robin Hood's max distance is much lower -- fairer distribution.")
print(f"  Rust's old HashMap used Robin Hood hashing for this reason.")


# ---------------------------------------------------------------------------
# SECTION 6: Python dict Probe Sequence
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 6: Python dict Probe Sequence Simulation")
print("=" * 70)

def python_dict_probe(hash_value, table_size, max_probes=20):
    """Simulate CPython's dict probe sequence.

    This is the actual algorithm from CPython's dictobject.c:
    - perturb starts as the full hash value
    - Each step: index = (5*index + perturb + 1) % table_size
    - perturb >>= 5 each step

    The perturb variable ensures early probes depend on ALL bits of the
    hash (not just the low bits used for the initial index). As perturb
    decays to 0, the sequence becomes (5*index + 1) % table_size, which
    is guaranteed to visit every slot when table_size is a power of 2.
    """
    perturb = hash_value
    index = perturb % table_size
    sequence = [index]

    for _ in range(max_probes - 1):
        perturb >>= 5
        index = (5 * index + perturb + 1) % table_size
        sequence.append(index)

    return sequence

print(f"\n  Python dict probe sequence for hash=42 in table of 16:")
seq = python_dict_probe(42, 16, 16)
print(f"    {seq}")
print(f"\n  Python dict probe sequence for hash=42 in table of 16 (another hash):")
seq2 = python_dict_probe(10000042, 16, 16)
print(f"    {seq2}")
print(f"\n  Same initial slot (42%16 = {42%16}, 10000042%16 = {10000042%16})")
print(f"  But the sequences diverge immediately because the full hash")
print(f"  value (perturb) is different. This is why it works better than")
print(f"  simple linear or quadratic probing.")


# ---------------------------------------------------------------------------
# SECTION 7: Performance Benchmark
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 7: Performance Benchmark -- All Strategies vs Python dict")
print("=" * 70)

N = 50_000
random.seed(42)
bench_keys = [f"bench_{i}" for i in range(N)]
random.shuffle(bench_keys)

for strategy in ['linear', 'quadratic', 'double']:
    ht = HashTableOpen(initial_capacity=64, probe_strategy=strategy)
    start = time.perf_counter()
    for key in bench_keys:
        ht.put(key, 1)
    insert_time = time.perf_counter() - start

    ht._total_probes = 0
    ht._total_operations = 0
    start = time.perf_counter()
    for key in bench_keys:
        ht.get(key)
    lookup_time = time.perf_counter() - start
    s = ht.stats()

    print(f"\n  {strategy.upper()} probing:")
    print(f"    Insert {N:,}: {insert_time*1000:.0f} ms, "
          f"Lookup {N:,}: {lookup_time*1000:.0f} ms, "
          f"Avg probes/lookup: {s['avg_probes']:.2f}, "
          f"Resizes: {s['resizes']}")

# Python dict baseline
d = {}
start = time.perf_counter()
for key in bench_keys:
    d[key] = 1
py_insert = time.perf_counter() - start

start = time.perf_counter()
for key in bench_keys:
    _ = d[key]
py_lookup = time.perf_counter() - start

print(f"\n  Python dict:")
print(f"    Insert {N:,}: {py_insert*1000:.0f} ms, "
      f"Lookup {N:,}: {py_lookup*1000:.0f} ms")
print(f"    (C implementation -- expect 10-50x faster than our Python)")


print("\n" + "=" * 70)
print("Done! You now understand both chaining and open addressing.")
print("Key insight: open addressing trades simpler memory layout")
print("(cache-friendly) for more complex deletion (tombstones)")
print("and sensitivity to load factor. Now work through practice.py.")
print("=" * 70)
