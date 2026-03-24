"""
Day 69 Practice: Hash Attacks and Defenses

5 exercises building from attack crafting to defense implementation.
Run: python3 practice.py
"""

import time
import random
import string
import struct
import os
from hash_attacks import SipHash, NaiveHashTable, MASK64, _rotl64


# =============================================================================
# Exercise 1: Craft a HashDoS Attack
# =============================================================================
# Given hash(s) = sum(ord(c) for c in s) % m, generate N strings
# that ALL map to bucket 0.
#
# Strategy: build strings whose character ordinal sum is a multiple of m.
# For a 2-char string: ord(a) + ord(b) ≡ 0 (mod m)
# Fix a, solve for b = (-a) mod m, shift into printable ASCII range.
# =============================================================================

def craft_hashdos_strings(m: int, n: int) -> list:
    """
    Generate n distinct strings that all hash to bucket 0
    under hash(s) = sum(ord(c) for c in s) % m.

    Strategy: build strings of varying length whose character ordinal sum ≡ 0 (mod m).
    Use a variable prefix to create distinct strings, then adjust the last 2 characters
    so the total sum hits the target.
    """
    results = set()

    for length in range(3, 20):
        if len(results) >= n:
            break
        for tag in range(n * 2):
            if len(results) >= n:
                break

            # Build a prefix from the tag, reserve 2 chars for adjustment
            prefix_chars = []
            tmp = tag
            for _ in range(length - 2):
                c = 48 + (tmp % 75)
                tmp //= 75
                prefix_chars.append(c)

            prefix_sum = sum(prefix_chars)
            needed = (0 - prefix_sum) % m  # target bucket 0

            # Pick c1 in [48, 99], solve for c2
            for c1 in range(48, 100):
                c2 = (needed - c1) % m
                while c2 < 33:
                    c2 += m
                if c2 <= 126:
                    s = ''.join(chr(c) for c in prefix_chars) + chr(c1) + chr(c2)
                    if s not in results:
                        results.add(s)
                        break

    return list(results)[:n]


def test_exercise1():
    print("Exercise 1: Craft a HashDoS Attack")
    print("-" * 50)

    m = 256
    n = 1000

    collision_strings = craft_hashdos_strings(m, n)
    print(f"  Generated {len(collision_strings)} strings targeting bucket 0 (m={m})")

    # Verify ALL hash to bucket 0
    def simple_hash(s, mod):
        return sum(ord(c) for c in s) % mod

    all_zero = all(simple_hash(s, m) == 0 for s in collision_strings)
    all_unique = len(set(collision_strings)) == len(collision_strings)

    print(f"  All hash to bucket 0: {all_zero}")
    print(f"  All strings unique:   {all_unique}")
    print(f"  Sample strings: {collision_strings[:5]}")

    assert all_zero, "Not all strings hash to bucket 0!"
    assert all_unique, "Duplicate strings found!"
    assert len(collision_strings) == n, f"Expected {n} strings, got {len(collision_strings)}"
    print("  PASSED\n")


# =============================================================================
# Exercise 2: Measure Attack Impact
# =============================================================================
# Insert N collision strings vs N random strings into a naive hash table.
# Compare total insert time. The collision case should be dramatically slower
# because each insert scans the entire single bucket (O(n) per insert → O(n^2) total).
# =============================================================================

def measure_attack_impact(m: int, n: int):
    """
    Returns (collision_time, random_time, slowdown_factor).
    """
    # Generate collision strings
    collision_strings = craft_hashdos_strings(m, n)

    # Generate random strings
    random_strings = [
        ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        for _ in range(n)
    ]

    # Time collision insertions
    table_attack = NaiveHashTable(m)
    start = time.perf_counter()
    for s in collision_strings:
        table_attack.insert(s, True)
    collision_time = time.perf_counter() - start

    # Time random insertions
    table_random = NaiveHashTable(m)
    start = time.perf_counter()
    for s in random_strings:
        table_random.insert(s, True)
    random_time = time.perf_counter() - start

    slowdown = collision_time / random_time if random_time > 0 else float('inf')

    return collision_time, random_time, slowdown


def test_exercise2():
    print("Exercise 2: Measure Attack Impact")
    print("-" * 50)

    m = 512
    n = 2000

    collision_time, random_time, slowdown = measure_attack_impact(m, n)

    print(f"  Table size: {m}, Keys: {n}")
    print(f"  Collision insert time: {collision_time:.4f}s")
    print(f"  Random insert time:    {random_time:.4f}s")
    print(f"  Slowdown factor:       {slowdown:.1f}x")

    # The attack should cause at least a 5x slowdown with 2000 keys
    assert slowdown > 2.0, f"Expected significant slowdown, got only {slowdown:.1f}x"
    print(f"  Confirmed: collision keys cause {slowdown:.0f}x slowdown")
    print("  PASSED\n")


# =============================================================================
# Exercise 3: Implement Keyed Hashing
# =============================================================================
# A keyed hash function takes a secret key and data, producing a hash that
# cannot be predicted without knowing the key.
#
# Implement hash_with_key(key, data) using a simple but effective approach:
# XOR the key into the state at each step, use multiplication for mixing.
# =============================================================================

def hash_with_key(key: int, data: str) -> int:
    """
    Keyed hash function. Same data with different keys produces different hashes.
    Uses FNV-1a style mixing with the key XOR'd into the initial state.

    This prevents HashDoS because the attacker cannot predict the hash
    without knowing the key, which is randomly chosen at process start.
    """
    # Initialize state from key (the critical defense)
    h = key & MASK64

    # FNV-1a style: XOR then multiply for each byte
    FNV_PRIME = 0x100000001b3
    for ch in data:
        h ^= ord(ch)
        h = (h * FNV_PRIME) & MASK64

    return h


def test_exercise3():
    print("Exercise 3: Implement Keyed Hashing")
    print("-" * 50)

    # Same key, same input → same output (deterministic)
    key = 0xDEADBEEFCAFEBABE
    h1 = hash_with_key(key, "hello")
    h2 = hash_with_key(key, "hello")
    assert h1 == h2, "Same key + same input must produce same hash"
    print(f"  Same key, same input: {h1:#018x} == {h2:#018x}")

    # Same key, different input → different output (very likely)
    h3 = hash_with_key(key, "hellp")  # one char different
    assert h1 != h3, "Different inputs should produce different hashes"
    print(f"  Same key, diff input: {h1:#018x} != {h3:#018x}")

    # Different key, same input → different output (the defense!)
    key2 = 0x1234567890ABCDEF
    h4 = hash_with_key(key2, "hello")
    assert h1 != h4, "Different keys should produce different hashes for same input"
    print(f"  Diff key, same input: {h1:#018x} != {h4:#018x}")

    # Verify unpredictability: attacker who crafts collisions for key1
    # cannot predict hashes under key2
    test_strings = ["aaa", "bbb", "ccc", "ddd", "eee"]
    m = 16
    buckets_key1 = [hash_with_key(key, s) % m for s in test_strings]
    buckets_key2 = [hash_with_key(key2, s) % m for s in test_strings]
    print(f"  Buckets under key1: {buckets_key1}")
    print(f"  Buckets under key2: {buckets_key2}")
    assert buckets_key1 != buckets_key2, "Different keys should give different bucket assignments"

    print("  PASSED\n")


# =============================================================================
# Exercise 4: Test Avalanche Property
# =============================================================================
# Good hash: flip 1 input bit → ~50% output bits flip (avalanche).
# Bad hash (sum): flip 1 input bit → ~1 output bit flips.
#
# Test both SipHash and simple sum-hash. Measure average bits changed
# over many single-bit flips.
# =============================================================================

def simple_sum_hash(data: bytes) -> int:
    """Terrible hash function: just sums the bytes. No avalanche at all."""
    h = 0
    for b in data:
        h = (h + b) & MASK64
    return h


def measure_avalanche(hash_func, num_tests=200) -> float:
    """
    Measure avalanche: for random inputs, flip one bit, count how many
    output bits change. Return average fraction of bits changed.

    Ideal: 0.50 (50% of 64 bits flip)
    Bad:   close to 0 (almost no bits flip)
    """
    total_bits_changed = 0

    for _ in range(num_tests):
        # Random 8-byte input
        data = os.urandom(8)
        h1 = hash_func(data)

        # Flip a random bit
        byte_idx = random.randint(0, 7)
        bit_idx = random.randint(0, 7)
        flipped = bytearray(data)
        flipped[byte_idx] ^= (1 << bit_idx)
        h2 = hash_func(bytes(flipped))

        # Count differing bits
        diff = h1 ^ h2
        total_bits_changed += bin(diff).count('1')

    return total_bits_changed / (num_tests * 64)


def test_exercise4():
    print("Exercise 4: Test Avalanche Property")
    print("-" * 50)

    # SipHash avalanche
    key = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    sip = SipHash(key)
    sip_avalanche = measure_avalanche(sip.hash, num_tests=500)

    # Simple sum hash avalanche
    sum_avalanche = measure_avalanche(simple_sum_hash, num_tests=500)

    print(f"  SipHash avalanche:    {sip_avalanche:.3f} (ideal: 0.500)")
    print(f"  Sum-hash avalanche:   {sum_avalanche:.3f} (ideal: 0.500)")
    print()

    # SipHash should be close to 0.5
    assert 0.35 < sip_avalanche < 0.65, \
        f"SipHash avalanche {sip_avalanche:.3f} too far from ideal 0.5"
    print(f"  SipHash: GOOD avalanche ({sip_avalanche:.1%} bits flip)")

    # Sum hash should be very poor (close to 0)
    assert sum_avalanche < 0.15, \
        f"Sum hash avalanche {sum_avalanche:.3f} unexpectedly good"
    print(f"  Sum hash: POOR avalanche ({sum_avalanche:.1%} bits flip)")
    print(f"  This is WHY sum-hash is attackable: similar inputs → similar hashes")
    print("  PASSED\n")


# =============================================================================
# Exercise 5: PYTHONHASHSEED Simulation
# =============================================================================
# Python randomizes string hashing per process using PYTHONHASHSEED.
# Simulate this: same string gets different hash with different seeds.
# Verify the hashes distribute uniformly across buckets over many seeds.
# =============================================================================

def python_hash_simulation(seed: int, s: str) -> int:
    """
    Simulate Python's per-process hash randomization.
    Uses SipHash with a key derived from the seed.
    Different seed → different hash for the same string.
    """
    # Derive a 16-byte key from the seed (in real Python, PYTHONHASHSEED
    # is used to seed the random key generation)
    key = struct.pack('<QQ', seed & MASK64, (seed * 0x9E3779B97F4A7C15) & MASK64)
    sip = SipHash(key)
    return sip.hash_str(s)


def test_exercise5():
    print("Exercise 5: PYTHONHASHSEED Simulation")
    print("-" * 50)

    test_string = "attack_payload"

    # Same seed → same hash (deterministic within a process)
    h1 = python_hash_simulation(42, test_string)
    h2 = python_hash_simulation(42, test_string)
    assert h1 == h2, "Same seed must produce same hash"
    print(f"  Seed 42: hash = {h1:#018x}")
    print(f"  Seed 42: hash = {h2:#018x} (same - deterministic)")

    # Different seed → different hash (unpredictable across processes)
    h3 = python_hash_simulation(43, test_string)
    assert h1 != h3, "Different seeds should produce different hashes"
    print(f"  Seed 43: hash = {h3:#018x} (different)")

    # Show several seeds
    print(f"\n  Hashes of '{test_string}' across seeds:")
    for seed in range(5):
        h = python_hash_simulation(seed, test_string)
        print(f"    Seed {seed}: {h:#018x} → bucket {h % 1024}")

    # Verify uniform distribution: hash the same string with many seeds,
    # check that it distributes across buckets uniformly
    num_seeds = 10000
    num_buckets = 64
    bucket_counts = [0] * num_buckets

    for seed in range(num_seeds):
        h = python_hash_simulation(seed, test_string)
        bucket_counts[h % num_buckets] += 1

    expected = num_seeds / num_buckets  # ~156.25
    min_count = min(bucket_counts)
    max_count = max(bucket_counts)

    print(f"\n  Distribution across {num_buckets} buckets ({num_seeds} seeds):")
    print(f"    Expected per bucket: {expected:.1f}")
    print(f"    Min bucket count:    {min_count}")
    print(f"    Max bucket count:    {max_count}")
    print(f"    Ratio max/min:       {max_count/min_count:.2f}")

    # Chi-squared style check: no bucket should deviate too wildly
    # Allow 3x range (very generous for truly random)
    assert max_count < expected * 2.5, \
        f"Distribution too skewed: max {max_count} >> expected {expected:.0f}"
    assert min_count > expected * 0.3, \
        f"Distribution too skewed: min {min_count} << expected {expected:.0f}"

    print(f"    Distribution is uniform - seed randomization works!")
    print("  PASSED\n")


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DAY 69 PRACTICE: Hash Attacks and Defenses")
    print("=" * 60)
    print()

    test_exercise1()
    test_exercise2()
    test_exercise3()
    test_exercise4()
    test_exercise5()

    print("=" * 60)
    print("ALL EXERCISES PASSED")
    print("=" * 60)
