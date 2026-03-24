"""
Day 69: Hash Attacks and Defenses

Demonstrates HashDoS attacks, SipHash implementation, and randomized hash tables.

Why this matters: any system that puts user-controlled keys into a hash table
is vulnerable to algorithmic complexity attacks unless the hash function is
keyed with a secret random seed.
"""

import struct
import time
import os
import random
import string


# =============================================================================
# Part 1: Demonstrate HashDoS Attack
# =============================================================================

class NaiveHashTable:
    """
    Hash table using a simple, deterministic, predictable hash function.
    This is what languages used before 2011 — and it's trivially attackable.
    """

    def __init__(self, size=1024):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.num_items = 0

    def _hash(self, key: str) -> int:
        """
        Simple sum-of-characters hash. Deterministic and predictable.
        An attacker can trivially compute this and craft collisions.
        """
        h = 0
        for ch in key:
            h = (h + ord(ch)) % self.size
        return h

    def insert(self, key: str, value):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        # Linear scan through bucket — O(bucket_size) per insert
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.num_items += 1

    def get(self, key: str):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def max_bucket_size(self) -> int:
        return max(len(b) for b in self.buckets)

    def bucket_distribution(self) -> dict:
        """Returns {bucket_size: count_of_buckets_with_that_size}."""
        dist = {}
        for b in self.buckets:
            sz = len(b)
            if sz > 0:
                dist[sz] = dist.get(sz, 0) + 1
        return dist


def craft_collision_strings(table_size: int, target_bucket: int, count: int) -> list:
    """
    Craft strings that all hash to the same bucket under sum-of-chars hash.

    Strategy: for hash(s) = sum(ord(c) for c in s) % table_size,
    any two strings with the same character sum mod table_size collide.

    We build strings of varying lengths whose ASCII sum ≡ target (mod table_size).
    Use a fixed "base character" (e.g., 'a'=97) for padding, then adjust the
    last 1-2 characters to hit the exact target sum.
    """
    collisions = set()
    base_char = 97  # 'a'

    # For each unique prefix, compute what suffix is needed to hit target
    for length in range(3, 20):
        if len(collisions) >= count:
            break
        # Generate distinct prefixes by varying a "tag" portion
        for tag in range(count * 2):
            if len(collisions) >= count:
                break

            # Build prefix: use base_char repeated, then encode tag into
            # a couple of characters. This gives us many distinct strings.
            # Reserve 2 chars at the end for adjustment.
            if length < 4:
                prefix_len = length - 2
            else:
                prefix_len = length - 2

            # Encode tag into the prefix characters (vary them)
            prefix_chars = []
            tmp = tag
            for i in range(prefix_len):
                # Cycle through printable chars 48-122
                c = 48 + (tmp % 75)
                tmp //= 75
                prefix_chars.append(c)

            prefix_sum = sum(prefix_chars)
            # Need last 2 chars (c1, c2) such that prefix_sum + c1 + c2 ≡ target (mod table_size)
            needed = (target_bucket - prefix_sum) % table_size
            # Pick c1 in range [48, 122], solve for c2
            found = False
            for c1 in range(48, 100):
                c2 = (needed - c1) % table_size
                # Shift c2 into printable range
                while c2 < 33:
                    c2 += table_size
                if c2 <= 126:
                    s = ''.join(chr(c) for c in prefix_chars) + chr(c1) + chr(c2)
                    if s not in collisions:
                        collisions.add(s)
                        found = True
                        break
            if not found:
                # Try with 3 adjustment chars
                for c1 in range(48, 80):
                    for c2 in range(48, 80):
                        c3 = (needed - c1 - c2) % table_size
                        while c3 < 33:
                            c3 += table_size
                        if c3 <= 126:
                            s = ''.join(chr(c) for c in prefix_chars) + chr(c1) + chr(c2) + chr(c3)
                            if s not in collisions:
                                collisions.add(s)
                                break
                    else:
                        continue
                    break

    return list(collisions)[:count]


def demonstrate_hashdos():
    """
    Show the devastating effect of HashDoS: O(n^2) total time for n insertions
    when all keys collide, vs O(n) total time for random keys.
    """
    print("=" * 70)
    print("HASHDOS ATTACK DEMONSTRATION")
    print("=" * 70)

    table_size = 1024
    n = 3000  # number of keys

    # --- Attack: all keys collide ---
    print(f"\n[1] Crafting {n} strings that ALL hash to bucket 0...")
    collision_keys = craft_collision_strings(table_size, 0, n)
    print(f"    Generated {len(collision_keys)} collision strings")

    # Verify they all collide
    naive = NaiveHashTable(table_size)
    buckets_hit = set()
    for k in collision_keys:
        buckets_hit.add(naive._hash(k))
    assert len(buckets_hit) == 1, f"Expected 1 bucket, got {len(buckets_hit)}"
    print(f"    All strings hash to bucket: {buckets_hit.pop()}")

    print(f"\n[2] Inserting {n} collision keys into naive hash table...")
    naive_attack = NaiveHashTable(table_size)
    start = time.perf_counter()
    for k in collision_keys:
        naive_attack.insert(k, True)
    attack_time = time.perf_counter() - start
    print(f"    Time: {attack_time:.4f}s")
    print(f"    Max bucket size: {naive_attack.max_bucket_size()}")
    print(f"    This is O(n^2) total work: each insert scans all previous keys")

    # --- Normal: random keys ---
    print(f"\n[3] Inserting {n} random keys into naive hash table...")
    random_keys = [''.join(random.choices(string.ascii_letters, k=10)) for _ in range(n)]
    naive_normal = NaiveHashTable(table_size)
    start = time.perf_counter()
    for k in random_keys:
        naive_normal.insert(k, True)
    normal_time = time.perf_counter() - start
    print(f"    Time: {normal_time:.4f}s")
    print(f"    Max bucket size: {naive_normal.max_bucket_size()}")

    # --- Comparison ---
    if normal_time > 0:
        slowdown = attack_time / normal_time
        print(f"\n[4] Attack slowdown: {slowdown:.1f}x slower")
    print(f"    With collision keys, the hash table degenerates into a linked list.")

    # --- Lookup timing ---
    print(f"\n[5] Lookup timing comparison...")

    start = time.perf_counter()
    for k in collision_keys[:500]:
        naive_attack.get(k)
    attack_lookup = time.perf_counter() - start

    start = time.perf_counter()
    for k in random_keys[:500]:
        naive_normal.get(k)
    normal_lookup = time.perf_counter() - start

    print(f"    500 lookups (collision table): {attack_lookup:.4f}s")
    print(f"    500 lookups (normal table):    {normal_lookup:.4f}s")
    if normal_lookup > 0:
        print(f"    Lookup slowdown: {attack_lookup / normal_lookup:.1f}x")

    return attack_time, normal_time


# =============================================================================
# Part 2: SipHash-2-4 Implementation
# =============================================================================

MASK64 = (1 << 64) - 1


def _rotl64(x, b):
    """64-bit left rotation."""
    return ((x << b) | (x >> (64 - b))) & MASK64


class SipHash:
    """
    Simplified SipHash-2-4 implementation.

    SipHash is a keyed pseudorandom function designed for hash table defense.
    It uses a 128-bit key and produces a 64-bit output.

    SipHash-c-d means: c rounds per message block, d finalization rounds.
    Standard is SipHash-2-4.

    Why SipHash and not SHA-256?
    - SipHash: ~1 cycle/byte on short inputs, 128-bit key, 64-bit output
    - SHA-256: ~10 cycles/byte on short inputs, no key, 256-bit output
    Hash tables need speed and keyed unpredictability, not collision resistance.
    """

    def __init__(self, key: bytes = None):
        """
        Initialize with a 128-bit (16-byte) key.
        If no key provided, generates a random one.
        """
        if key is None:
            key = os.urandom(16)
        if len(key) != 16:
            raise ValueError("SipHash key must be exactly 16 bytes")
        self.key = key
        # Split 128-bit key into two 64-bit halves (little-endian)
        self.k0, self.k1 = struct.unpack('<QQ', key)

    def _sip_round(self, v0, v1, v2, v3):
        """
        The core mixing function of SipHash.
        Each round performs 4 additions, 4 XORs, and 4 rotations.
        This provides diffusion: every input bit affects every output bit.
        """
        v0 = (v0 + v1) & MASK64
        v1 = _rotl64(v1, 13)
        v1 ^= v0
        v0 = _rotl64(v0, 32)

        v2 = (v2 + v3) & MASK64
        v3 = _rotl64(v3, 16)
        v3 ^= v2

        v0 = (v0 + v3) & MASK64
        v3 = _rotl64(v3, 21)
        v3 ^= v0

        v2 = (v2 + v1) & MASK64
        v1 = _rotl64(v1, 17)
        v1 ^= v2
        v2 = _rotl64(v2, 32)

        return v0, v1, v2, v3

    def hash(self, data: bytes) -> int:
        """
        Compute SipHash-2-4 of the given data.
        Returns a 64-bit integer.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        # Initialize state from key
        v0 = self.k0 ^ 0x736f6d6570736575  # "somepseu" in little-endian
        v1 = self.k1 ^ 0x646f72616e646f6d  # "dorandom"
        v2 = self.k0 ^ 0x6c7967656e657261  # "lygenera"
        v3 = self.k1 ^ 0x7465646279746573  # "tedbytes"

        # Process full 8-byte blocks
        length = len(data)
        num_blocks = length // 8
        for i in range(num_blocks):
            m = struct.unpack_from('<Q', data, i * 8)[0]
            v3 ^= m
            # 2 compression rounds (the "2" in SipHash-2-4)
            for _ in range(2):
                v0, v1, v2, v3 = self._sip_round(v0, v1, v2, v3)
            v0 ^= m

        # Process final partial block (padded with length byte)
        # Last byte is (length mod 256), remaining bytes from input
        last = (length & 0xff) << 56
        remaining = length - num_blocks * 8
        for i in range(remaining):
            last |= data[num_blocks * 8 + i] << (i * 8)

        v3 ^= last
        for _ in range(2):
            v0, v1, v2, v3 = self._sip_round(v0, v1, v2, v3)
        v0 ^= last

        # Finalization: 4 rounds (the "4" in SipHash-2-4)
        v2 ^= 0xff
        for _ in range(4):
            v0, v1, v2, v3 = self._sip_round(v0, v1, v2, v3)

        return v0 ^ v1 ^ v2 ^ v3

    def hash_str(self, s: str) -> int:
        """Convenience: hash a string."""
        return self.hash(s.encode('utf-8'))


# =============================================================================
# Part 3: Randomized Hash Table (DoS-resistant)
# =============================================================================

class RandomizedHashTable:
    """
    Hash table that uses SipHash with a random key generated at creation time.

    The key is chosen randomly when the table is created. Since the attacker
    cannot read process memory, they cannot predict the hash function, and
    therefore cannot craft collision strings.

    This is what Python, Rust, and Ruby do internally.
    """

    def __init__(self, size=1024):
        self.size = size
        self.buckets = [[] for _ in range(size)]
        self.num_items = 0
        # Random key generated ONCE at creation — the core defense
        self.hasher = SipHash()  # random 128-bit key

    def _hash(self, key: str) -> int:
        """Keyed hash — unpredictable without knowing the secret key."""
        return self.hasher.hash_str(key) % self.size

    def insert(self, key: str, value):
        idx = self._hash(key)
        bucket = self.buckets[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self.num_items += 1

    def get(self, key: str):
        idx = self._hash(key)
        for k, v in self.buckets[idx]:
            if k == key:
                return v
        raise KeyError(key)

    def max_bucket_size(self) -> int:
        return max(len(b) for b in self.buckets)

    def bucket_distribution(self) -> dict:
        dist = {}
        for b in self.buckets:
            sz = len(b)
            if sz > 0:
                dist[sz] = dist.get(sz, 0) + 1
        return dist


def demonstrate_defense():
    """
    Show that the same collision strings that devastate a naive table
    distribute uniformly in a randomized table.
    """
    print("\n" + "=" * 70)
    print("RANDOMIZED HASH TABLE DEFENSE")
    print("=" * 70)

    table_size = 1024
    n = 3000

    # Craft strings that collide under the naive sum-hash
    collision_keys = craft_collision_strings(table_size, 0, n)

    # --- Attack the naive table ---
    print(f"\n[1] Naive table with {n} collision keys:")
    naive = NaiveHashTable(table_size)
    start = time.perf_counter()
    for k in collision_keys:
        naive.insert(k, True)
    naive_time = time.perf_counter() - start
    print(f"    Insert time: {naive_time:.4f}s")
    print(f"    Max bucket size: {naive.max_bucket_size()} (all in one bucket!)")

    # --- Same keys against randomized table ---
    print(f"\n[2] Randomized table with the SAME {n} collision keys:")
    secure = RandomizedHashTable(table_size)
    start = time.perf_counter()
    for k in collision_keys:
        secure.insert(k, True)
    secure_time = time.perf_counter() - start
    print(f"    Insert time: {secure_time:.4f}s")
    print(f"    Max bucket size: {secure.max_bucket_size()} (well distributed!)")

    # Show distribution
    dist = secure.bucket_distribution()
    sorted_dist = sorted(dist.items())
    print(f"\n    Bucket size distribution (randomized table):")
    for sz, count in sorted_dist[:10]:
        print(f"      Size {sz}: {count} buckets")

    print(f"\n[3] The attack strings are useless against the randomized table.")
    print(f"    Attacker would need to know the 128-bit SipHash key to craft")
    print(f"    collisions, which requires reading process memory.")

    if naive_time > 0 and secure_time > 0:
        print(f"\n    Speed ratio: naive took {naive_time / secure_time:.1f}x longer")

    return naive_time, secure_time


def demonstrate_siphash():
    """Show SipHash properties."""
    print("\n" + "=" * 70)
    print("SIPHASH DEMONSTRATION")
    print("=" * 70)

    # Same key, same input → same output (deterministic given key)
    key = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    sip = SipHash(key)

    print("\n[1] Deterministic with same key:")
    for s in ["hello", "world", "hello"]:
        h = sip.hash_str(s)
        print(f'    SipHash("{s}") = {h:#018x}')

    # Different key, same input → different output
    print("\n[2] Different key → different hash (the defense):")
    for i in range(3):
        sip_i = SipHash()  # random key each time
        h = sip_i.hash_str("attack_string")
        print(f'    Key {i}: SipHash("attack_string") = {h:#018x}')

    # Avalanche: flip one bit, see massive output change
    print("\n[3] Avalanche property (flip 1 input bit → ~50% output bits flip):")
    sip_test = SipHash(key)
    base = b"test1234"
    h1 = sip_test.hash(base)
    # Flip lowest bit of first byte
    modified = bytes([base[0] ^ 1]) + base[1:]
    h2 = sip_test.hash(modified)
    diff = h1 ^ h2
    bits_changed = bin(diff).count('1')
    print(f'    hash("{base.decode()}") = {h1:#018x}')
    print(f'    hash("{modified.decode()}") = {h2:#018x}')
    print(f'    XOR                    = {diff:#018x}')
    print(f'    Bits changed: {bits_changed}/64 ({bits_changed/64*100:.1f}%)')
    print(f'    Ideal: ~32/64 (50%)')


# =============================================================================
# Main: Run all demonstrations
# =============================================================================

if __name__ == "__main__":
    demonstrate_hashdos()
    demonstrate_defense()
    demonstrate_siphash()

    print("\n" + "=" * 70)
    print("KEY TAKEAWAYS")
    print("=" * 70)
    print("""
    1. Deterministic hash functions let attackers craft O(n) collisions
    2. HashDoS turns O(1) hash table ops into O(n), giving O(n^2) total
    3. Defense: randomize the hash function with a per-process secret key
    4. SipHash: fast, keyed, provably secure — the standard defense
    5. Python, Rust, Ruby, Redis all use SipHash for exactly this reason
    """)
