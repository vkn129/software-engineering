"""
Day 13: Hash Table with Separate Chaining -- Built from Scratch
================================================================

We build a complete hash table from the ground up:
1. Hash functions -- how to turn any key into an array index
2. Separate chaining -- linked lists for collision resolution
3. Dynamic resizing -- keeping the load factor bounded
4. Collision statistics -- see the birthday paradox in action

This is the most important data structure in practical programming.
Every dict, set, cache, and symbol table is a hash table underneath.

Run: python hash_table_chaining.py
"""

import time
import random
import math


# ---------------------------------------------------------------------------
# HASH FUNCTIONS
# ---------------------------------------------------------------------------
# A hash function converts an arbitrary key into an integer. The quality
# of the hash function determines whether entries spread evenly across
# buckets (fast) or pile up in a few buckets (slow, vulnerable to attacks).

def hash_naive(key, table_size):
    """Terrible hash: just use the first character. DO NOT USE.

    This clusters all strings starting with the same letter into one bucket.
    "alice", "anna", "alex" all go to the same slot.
    """
    if isinstance(key, str) and len(key) > 0:
        return ord(key[0]) % table_size
    return hash(key) % table_size


def hash_sum(key, table_size):
    """Bad hash: sum of character values. Anagram-blind.

    "abc" and "bca" hash to the same value because addition is commutative.
    Any permutation of the same letters collides.
    """
    if isinstance(key, str):
        return sum(ord(c) for c in key) % table_size
    return hash(key) % table_size


def hash_polynomial(key, table_size, base=31):
    """Good hash: polynomial rolling hash.

    h = c0 * base^(n-1) + c1 * base^(n-2) + ... + c(n-1) * base^0

    This is position-dependent ("abc" != "bca") and distributes well.
    Base 31 is chosen because:
    - It is prime (reduces collision patterns)
    - 31 = 32 - 1 = 2^5 - 1, so h*31 = (h<<5) - h (fast on hardware)
    - Empirically good distribution for natural language strings

    Java's String.hashCode() uses exactly this formula with base 31.
    """
    if isinstance(key, str):
        h = 0
        for char in key:
            h = h * base + ord(char)
        return h % table_size
    return hash(key) % table_size


def hash_djb2(key, table_size):
    """DJB2 hash by Daniel J. Bernstein. Simple, fast, decent distribution.

    The magic number 5381 and the multiplier 33 were chosen empirically.
    h * 33 = (h << 5) + h, which is fast.
    """
    if isinstance(key, str):
        h = 5381
        for char in key:
            h = ((h << 5) + h) + ord(char)  # h * 33 + ord(char)
        return h % table_size
    return hash(key) % table_size


def hash_fnv1a(key, table_size):
    """FNV-1a hash. Used in many real systems for non-cryptographic hashing.

    XOR-then-multiply gives better avalanche than multiply-then-XOR.
    The FNV offset basis and prime are carefully chosen constants.
    """
    if isinstance(key, str):
        h = 2166136261  # FNV offset basis (32-bit)
        for char in key:
            h = h ^ ord(char)
            h = (h * 16777619) & 0xFFFFFFFF  # FNV prime, keep 32-bit
        return h % table_size
    return hash(key) % table_size


# ---------------------------------------------------------------------------
# HASH TABLE WITH SEPARATE CHAINING
# ---------------------------------------------------------------------------

class ChainNode:
    """A node in the chain (linked list) at each bucket."""
    __slots__ = ('key', 'value', 'next')

    def __init__(self, key, value, next_node=None):
        self.key = key
        self.value = value
        self.next = next_node


class HashTableChaining:
    """Hash table with separate chaining for collision resolution.

    This is conceptually how Java's HashMap works (pre-Java 8 used linked
    lists; Java 8+ converts long chains to balanced trees for worst-case
    O(log n) instead of O(n) per bucket).

    We implement:
    - put(key, value) -- insert or update
    - get(key) -- retrieve value
    - delete(key) -- remove entry
    - Automatic resize when load factor exceeds threshold
    - Collision statistics for analysis
    """

    # Why 0.75? It is a trade-off. Lower = faster lookups, more memory.
    # Higher = slower lookups, less memory. Java's HashMap uses 0.75.
    # At alpha=0.75, the average chain length is 0.75, meaning most lookups
    # check fewer than 2 entries.
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, initial_capacity=16, hash_func=None):
        """Initialize with a given capacity (should be a power of 2 for fast modulo).

        Why power of 2? Because h % (2^k) = h & (2^k - 1), which is a
        single AND instruction instead of an expensive division.
        """
        self._capacity = initial_capacity
        self._buckets = [None] * self._capacity
        self._size = 0
        self._hash_func = hash_func or hash_polynomial
        self._collision_count = 0
        self._resize_count = 0
        self._total_probes = 0
        self._total_lookups = 0

    def _hash(self, key):
        """Compute bucket index for a key."""
        return self._hash_func(key, self._capacity)

    @property
    def load_factor(self):
        return self._size / self._capacity

    def put(self, key, value):
        """Insert or update a key-value pair. O(1) average, O(n) worst case.

        Worst case occurs when all keys hash to the same bucket, creating
        a single linked list of length n. This is the HashDoS attack vector.
        """
        if self.load_factor >= self.LOAD_FACTOR_THRESHOLD:
            self._resize(self._capacity * 2)

        index = self._hash(key)
        node = self._buckets[index]

        # Walk the chain to check for existing key
        while node is not None:
            if node.key == key:
                node.value = value  # update existing
                return
            node = node.next

        # Key not found -- insert at head of chain (O(1))
        if self._buckets[index] is not None:
            self._collision_count += 1
        self._buckets[index] = ChainNode(key, value, self._buckets[index])
        self._size += 1

    def get(self, key, default=None):
        """Retrieve the value for a key. O(1) average."""
        self._total_lookups += 1
        index = self._hash(key)
        node = self._buckets[index]
        probes = 0

        while node is not None:
            probes += 1
            if node.key == key:
                self._total_probes += probes
                return node.value
            node = node.next

        self._total_probes += max(probes, 1)
        return default

    def delete(self, key):
        """Remove a key-value pair. O(1) average.

        With chaining, deletion is simple: find the node and unlink it.
        No tombstones needed (unlike open addressing, Day 14).
        """
        index = self._hash(key)
        node = self._buckets[index]
        prev = None

        while node is not None:
            if node.key == key:
                if prev is None:
                    self._buckets[index] = node.next
                else:
                    prev.next = node.next
                self._size -= 1
                return True
            prev = node
            node = node.next
        return False

    def __contains__(self, key):
        return self.get(key, sentinel := object()) is not sentinel

    def __setitem__(self, key, value):
        self.put(key, value)

    def __getitem__(self, key):
        result = self.get(key, sentinel := object())
        if result is sentinel:
            raise KeyError(key)
        return result

    def __delitem__(self, key):
        if not self.delete(key):
            raise KeyError(key)

    def __len__(self):
        return self._size

    def _resize(self, new_capacity):
        """Resize the hash table. O(n) -- must rehash every entry.

        Why rehash? Because the bucket index is hash(key) % capacity.
        When capacity changes, the same hash maps to a different bucket.
        Entries must be redistributed.
        """
        self._resize_count += 1
        old_buckets = self._buckets
        self._capacity = new_capacity
        self._buckets = [None] * self._capacity
        self._size = 0
        self._collision_count = 0

        for head in old_buckets:
            node = head
            while node is not None:
                self.put(node.key, node.value)
                node = node.next

    def chain_lengths(self):
        """Return the length of each chain. For collision analysis."""
        lengths = []
        for head in self._buckets:
            length = 0
            node = head
            while node is not None:
                length += 1
                node = node.next
            lengths.append(length)
        return lengths

    def stats(self):
        """Return detailed statistics about the hash table's state."""
        lengths = self.chain_lengths()
        non_empty = [l for l in lengths if l > 0]
        return {
            'size': self._size,
            'capacity': self._capacity,
            'load_factor': self.load_factor,
            'empty_buckets': lengths.count(0),
            'max_chain': max(lengths) if lengths else 0,
            'avg_chain': sum(non_empty) / len(non_empty) if non_empty else 0,
            'collisions': self._collision_count,
            'resizes': self._resize_count,
            'avg_probes_per_lookup': (
                self._total_probes / self._total_lookups
                if self._total_lookups > 0 else 0
            ),
        }

    def keys(self):
        for head in self._buckets:
            node = head
            while node is not None:
                yield node.key
                node = node.next

    def values(self):
        for head in self._buckets:
            node = head
            while node is not None:
                yield node.value
                node = node.next

    def items(self):
        for head in self._buckets:
            node = head
            while node is not None:
                yield (node.key, node.value)
                node = node.next


# ---------------------------------------------------------------------------
# SECTION 1: Basic Operations Demo
# ---------------------------------------------------------------------------

print("=" * 70)
print("SECTION 1: Hash Table Basic Operations")
print("=" * 70)

ht = HashTableChaining(initial_capacity=8)
entries = [
    ("alice", 25), ("bob", 30), ("charlie", 35),
    ("diana", 28), ("eve", 22), ("frank", 40),
]

for key, value in entries:
    idx = hash_polynomial(key, 8)
    ht.put(key, value)
    print(f"  put('{key}', {value})  -> bucket {idx}, load_factor={ht.load_factor:.2f}")

print(f"\n  get('alice') = {ht.get('alice')}")
print(f"  get('bob')   = {ht.get('bob')}")
print(f"  get('zz')    = {ht.get('zz', 'NOT FOUND')}")
print(f"  'charlie' in ht = {'charlie' in ht}")

ht.delete("bob")
print(f"\n  After delete('bob'): get('bob') = {ht.get('bob', 'NOT FOUND')}")
print(f"  Size: {len(ht)}")


# ---------------------------------------------------------------------------
# SECTION 2: Hash Function Quality Comparison
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 2: Hash Function Quality Comparison")
print("=" * 70)

# Generate test keys
random.seed(42)
test_keys = [f"key_{i}" for i in range(1000)]

hash_funcs = {
    "naive (first char)": hash_naive,
    "sum (order-blind)": hash_sum,
    "polynomial (base 31)": hash_polynomial,
    "DJB2": hash_djb2,
    "FNV-1a": hash_fnv1a,
}

TABLE_SIZE = 128

for name, func in hash_funcs.items():
    ht = HashTableChaining(initial_capacity=TABLE_SIZE, hash_func=func)
    for key in test_keys:
        ht.put(key, 0)

    s = ht.stats()
    lengths = ht.chain_lengths()
    print(f"\n  {name}:")
    print(f"    Load factor:     {s['load_factor']:.2f}")
    print(f"    Max chain:       {s['max_chain']}")
    print(f"    Avg chain:       {s['avg_chain']:.2f}")
    print(f"    Empty buckets:   {s['empty_buckets']}/{TABLE_SIZE}")
    print(f"    Collisions:      {s['collisions']}")

    # Distribution histogram
    max_len = min(max(lengths), 20)
    hist = [0] * (max_len + 1)
    for l in lengths:
        hist[min(l, max_len)] += 1
    print(f"    Distribution: ", end="")
    for i, count in enumerate(hist[:8]):
        print(f"[{i}]={count} ", end="")
    print()


# ---------------------------------------------------------------------------
# SECTION 3: Birthday Paradox Demonstration
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 3: Birthday Paradox -- When Do Collisions Start?")
print("=" * 70)

print("""
  The birthday paradox: in a room of 23 people, there is a >50% chance
  that two share a birthday (out of 365 days). Generalized: for a hash
  table with m slots, the first collision is expected after ~sqrt(pi*m/2)
  insertions.
""")

for table_size in [100, 1000, 10000, 100000]:
    expected = math.sqrt(math.pi * table_size / 2)

    # Simulate: insert random keys until first collision
    trials = 100
    first_collisions = []
    for _ in range(trials):
        seen = set()
        count = 0
        while True:
            count += 1
            h = random.randint(0, table_size - 1)
            if h in seen:
                first_collisions.append(count)
                break
            seen.add(h)

    avg_first = sum(first_collisions) / len(first_collisions)
    print(f"  Table size {table_size:>7,}: expected first collision at ~{expected:.0f}, "
          f"measured avg = {avg_first:.0f}")


# ---------------------------------------------------------------------------
# SECTION 4: Resize Behavior
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 4: Resize Behavior")
print("=" * 70)

ht = HashTableChaining(initial_capacity=4)
print(f"\n  Starting with capacity 4, load_factor threshold = {ht.LOAD_FACTOR_THRESHOLD}")

for i in range(20):
    key = f"item_{i}"
    old_cap = ht._capacity
    ht.put(key, i)
    new_cap = ht._capacity
    if new_cap != old_cap:
        print(f"  Insert #{i+1}: RESIZED {old_cap} -> {new_cap} "
              f"(load_factor was {(i) / old_cap:.2f})")
    elif i < 5 or i >= 18:
        print(f"  Insert #{i+1}: capacity={new_cap}, "
              f"load_factor={ht.load_factor:.2f}")

s = ht.stats()
print(f"\n  Final: size={s['size']}, capacity={s['capacity']}, "
      f"load_factor={s['load_factor']:.2f}, resizes={s['resizes']}")


# ---------------------------------------------------------------------------
# SECTION 5: Performance vs Python dict
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 5: Performance Benchmark -- Our Table vs Python dict")
print("=" * 70)

N = 50_000
keys = [f"key_{i}" for i in range(N)]
random.shuffle(keys)

# Our hash table
ht = HashTableChaining()
start = time.perf_counter()
for key in keys:
    ht.put(key, 1)
our_insert = time.perf_counter() - start

start = time.perf_counter()
for key in keys:
    ht.get(key)
our_lookup = time.perf_counter() - start

# Python dict
d = {}
start = time.perf_counter()
for key in keys:
    d[key] = 1
py_insert = time.perf_counter() - start

start = time.perf_counter()
for key in keys:
    _ = d[key]
py_lookup = time.perf_counter() - start

print(f"\n  {N:,} operations:")
print(f"    Our insert:  {our_insert*1000:8.2f} ms")
print(f"    dict insert: {py_insert*1000:8.2f} ms")
print(f"    Ratio:       {our_insert/py_insert:.1f}x slower (expected -- C vs Python)")
print(f"\n    Our lookup:  {our_lookup*1000:8.2f} ms")
print(f"    dict lookup: {py_lookup*1000:8.2f} ms")
print(f"    Ratio:       {our_lookup/py_lookup:.1f}x slower")

s = ht.stats()
print(f"\n    Our table stats: max_chain={s['max_chain']}, "
      f"avg_chain={s['avg_chain']:.2f}, "
      f"avg_probes={s['avg_probes_per_lookup']:.2f}")


# ---------------------------------------------------------------------------
# SECTION 6: HashDoS Attack Simulation
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("SECTION 6: HashDoS Attack -- Why Hash Quality Matters for Security")
print("=" * 70)

print("""
  A HashDoS attack crafts keys that all hash to the same bucket.
  With n entries in one bucket, every lookup is O(n) instead of O(1).
  A single HTTP request with ~10,000 crafted POST parameters can pin
  a CPU at 100% for seconds. This is why Python 3.3+ randomizes hashes.
""")

# Simulate: normal distribution vs adversarial
N_ATTACK = 5000

# Normal case
ht_normal = HashTableChaining(initial_capacity=1024)
normal_keys = [f"normal_{i}" for i in range(N_ATTACK)]
for key in normal_keys:
    ht_normal.put(key, 0)

# Adversarial: all keys hash to the same bucket
# We simulate this by using a hash function that always returns 0
def adversarial_hash(key, table_size):
    return 0

ht_attack = HashTableChaining(initial_capacity=1024, hash_func=adversarial_hash)
attack_keys = [f"attack_{i}" for i in range(N_ATTACK)]
for key in attack_keys:
    ht_attack.put(key, 0)

# Benchmark lookup times
start = time.perf_counter()
for key in normal_keys[:1000]:
    ht_normal.get(key)
normal_time = time.perf_counter() - start

start = time.perf_counter()
for key in attack_keys[:1000]:
    ht_attack.get(key)
attack_time = time.perf_counter() - start

print(f"  Lookup 1000 keys:")
print(f"    Normal distribution: {normal_time*1000:8.2f} ms "
      f"(max chain = {ht_normal.stats()['max_chain']})")
print(f"    Adversarial (all same bucket): {attack_time*1000:8.2f} ms "
      f"(max chain = {ht_attack.stats()['max_chain']})")
print(f"    Attack is {attack_time/normal_time:.0f}x slower")
print(f"    In production, this means one request can DOS your server.")


print("\n" + "=" * 70)
print("Done! Key takeaway: a hash table is only as good as its hash function.")
print("Tomorrow: open addressing, where we eliminate the linked lists entirely.")
print("Now work through practice.py.")
print("=" * 70)
