"""
Day 64: Hash Functions Deep Dive — Implementation and Analysis
===============================================================
Three hash function families, distribution testing, and avalanche analysis.

    DJB2:          hash = hash * 33 + c        (Bernstein, shift-and-add)
    FNV-1a:        hash = (hash ^ c) * prime   (XOR-then-multiply)
    Multiplicative: hash = (key * golden) >> shift (Knuth, golden ratio)

Why these three? They represent different design philosophies:
    - DJB2: simplicity, widely used, reasonable quality
    - FNV-1a: better avalanche via XOR-first design
    - Multiplicative: exploits golden ratio for bit mixing

Run: python hash_functions.py
"""

import struct
import math
import random
import string


# ─── Hash Function Implementations ──────────────────────────────────

def djb2(key: str, table_size: int = None) -> int:
    """
    DJB2 hash by Daniel J. Bernstein.

    Why 5381? It's an odd prime. Why 33? It's 2^5 + 1, so the multiply
    can be done as (hash << 5) + hash — a shift and an add.
    Empirically these constants give good distribution on English text.
    """
    h = 5381
    for c in key.encode('utf-8'):
        h = ((h << 5) + h + c) & 0xFFFFFFFF  # Keep to 32 bits
    return h if table_size is None else h % table_size


def fnv1a(key: str, table_size: int = None) -> int:
    """
    FNV-1a (Fowler-Noll-Vo variant 1a), 32-bit.

    The "1a" variant XORs before multiplying. This gives better avalanche
    because the XOR happens on the full accumulated state, and the multiply
    then disperses the change across all bits.

    The FNV prime 16777619 = 2^24 + 2^8 + 0x93 was chosen to have specific
    dispersion properties with the offset basis.
    """
    FNV_OFFSET_BASIS = 2166136261
    FNV_PRIME = 16777619

    h = FNV_OFFSET_BASIS
    for c in key.encode('utf-8'):
        h = h ^ c                        # XOR first (the "1a" difference)
        h = (h * FNV_PRIME) & 0xFFFFFFFF  # Then multiply, keep 32-bit
    return h if table_size is None else h % table_size


def multiplicative_hash(key: str, table_size: int = 256) -> int:
    """
    Knuth's multiplicative hash.

    Convert string to integer, multiply by a constant close to 2^32/phi,
    then extract the top bits. The golden ratio constant ensures that
    consecutive integers spread out maximally across the range.

    Why golden ratio? Because phi is the most irrational number — its
    continued fraction converges the slowest, meaning multiples of phi
    mod 1 are maximally spread in [0,1).
    """
    KNUTH_CONSTANT = 2654435761  # Close to 2^32 / phi

    # Convert string to integer by treating bytes as a number
    k = 0
    for c in key.encode('utf-8'):
        k = (k * 31 + c) & 0xFFFFFFFF

    h = (k * KNUTH_CONSTANT) & 0xFFFFFFFF
    # Use top bits (they're better mixed than low bits)
    bits_needed = max(1, table_size.bit_length())
    return (h >> (32 - bits_needed)) % table_size


# ─── Distribution Quality: Chi-Squared Test ─────────────────────────

def chi_squared_test(hash_fn, keys, num_buckets):
    """
    Measure distribution quality using Pearson's chi-squared test.

    If the hash function is perfectly uniform, each bucket should have
    E = len(keys) / num_buckets items. Chi-squared measures how far
    the actual distribution deviates from expected.

    chi^2 = sum((observed_i - expected)^2 / expected)

    For a good hash: chi^2 ~ num_buckets (degrees of freedom).
    Much larger = poor distribution. Much smaller = suspiciously perfect.

    Returns (chi_squared, p_value_interpretation).
    """
    buckets = [0] * num_buckets
    for key in keys:
        idx = hash_fn(key, num_buckets)
        buckets[idx] += 1

    expected = len(keys) / num_buckets
    chi_sq = sum((b - expected) ** 2 / expected for b in buckets)

    # Degrees of freedom = num_buckets - 1
    # For large df, chi^2/df should be close to 1.0
    ratio = chi_sq / (num_buckets - 1)

    if ratio < 0.5:
        quality = "SUSPICIOUS (too uniform)"
    elif ratio < 1.5:
        quality = "GOOD (close to expected)"
    elif ratio < 2.0:
        quality = "ACCEPTABLE"
    elif ratio < 3.0:
        quality = "POOR"
    else:
        quality = "BAD (significant clustering)"

    return chi_sq, ratio, quality, buckets


# ─── Avalanche Test ──────────────────────────────────────────────────

def avalanche_test(hash_fn, num_trials=1000, key_length=8):
    """
    Test the avalanche effect: flip 1 bit in input, measure what % of
    output bits change.

    Ideal hash: flipping 1 input bit changes ~50% of output bits.
    This is the Strict Avalanche Criterion (SAC).

    Returns average percentage of output bits that flip.
    """
    total_bit_changes = 0
    total_bits = 0

    for _ in range(num_trials):
        # Generate random key
        key_bytes = bytearray(random.randint(0, 255) for _ in range(key_length))
        original_key = bytes(key_bytes).decode('latin-1')
        original_hash = hash_fn(original_key) & 0xFFFFFFFF

        # Flip each bit in one random byte position
        byte_pos = random.randint(0, key_length - 1)
        bit_pos = random.randint(0, 7)

        modified_bytes = bytearray(key_bytes)
        modified_bytes[byte_pos] ^= (1 << bit_pos)
        modified_key = bytes(modified_bytes).decode('latin-1')
        modified_hash = hash_fn(modified_key) & 0xFFFFFFFF

        # Count differing bits (Hamming distance)
        diff = original_hash ^ modified_hash
        bit_changes = bin(diff).count('1')
        total_bit_changes += bit_changes
        total_bits += 32  # 32-bit hash

    return (total_bit_changes / total_bits) * 100


# ─── Visual Distribution Comparison ─────────────────────────────────

def visualize_distribution(hash_fn, name, keys, num_buckets=40):
    """Show a text-based histogram of bucket distribution."""
    _, _, quality, buckets = chi_squared_test(hash_fn, keys, num_buckets)

    max_count = max(buckets) if buckets else 1
    expected = len(keys) / num_buckets
    bar_width = 50

    print(f"\n{'=' * 60}")
    print(f"  {name} — {len(keys)} keys into {num_buckets} buckets")
    print(f"  Expected per bucket: {expected:.1f}  |  Quality: {quality}")
    print(f"{'=' * 60}")

    for i, count in enumerate(buckets):
        bar_len = int(count / max_count * bar_width) if max_count > 0 else 0
        bar = '#' * bar_len
        marker = " <--" if count > expected * 2 or count < expected * 0.3 else ""
        print(f"  [{i:3d}] {bar:50s} {count:4d}{marker}")

    # Summary stats
    counts = buckets
    mean = sum(counts) / len(counts)
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    std_dev = math.sqrt(variance)
    empty = sum(1 for c in counts if c == 0)
    print(f"\n  Mean: {mean:.1f}  StdDev: {std_dev:.1f}  "
          f"Empty buckets: {empty}/{num_buckets}  "
          f"Min: {min(counts)}  Max: {max(counts)}")


# ─── Demo ────────────────────────────────────────────────────────────

def generate_test_keys(n=2000):
    """Generate a mix of realistic keys for testing."""
    keys = set()

    # Sequential strings (tests sensitivity to similar inputs)
    for i in range(n // 4):
        keys.add(f"key_{i:06d}")

    # Random strings
    for _ in range(n // 4):
        length = random.randint(4, 20)
        keys.add(''.join(random.choices(string.ascii_lowercase, k=length)))

    # Common English-like prefixes (tests prefix clustering)
    prefixes = ["user_", "item_", "order_", "session_", "cache_"]
    for _ in range(n // 4):
        prefix = random.choice(prefixes)
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        keys.add(prefix + suffix)

    # Short keys (edge case: 1-3 chars)
    for c1 in string.ascii_lowercase:
        for c2 in string.ascii_lowercase[:10]:
            keys.add(c1 + c2)

    return list(keys)[:n]


if __name__ == "__main__":
    print("=" * 60)
    print("Day 64: Hash Functions Deep Dive")
    print("=" * 60)

    keys = generate_test_keys(2000)
    hash_functions = [
        (djb2, "DJB2"),
        (fnv1a, "FNV-1a"),
        (multiplicative_hash, "Multiplicative (Knuth)"),
    ]

    # ── 1. Distribution comparison ──
    print("\n" + "~" * 60)
    print("  PART 1: Distribution Quality (Chi-Squared Test)")
    print("~" * 60)

    num_buckets = 64
    for fn, name in hash_functions:
        chi_sq, ratio, quality, _ = chi_squared_test(fn, keys, num_buckets)
        print(f"\n  {name:30s}  chi^2={chi_sq:8.1f}  "
              f"chi^2/df={ratio:.3f}  {quality}")

    # ── 2. Visual distribution (condensed) ──
    print("\n" + "~" * 60)
    print("  PART 2: Visual Distribution (20 buckets)")
    print("~" * 60)

    for fn, name in hash_functions:
        visualize_distribution(fn, name, keys, num_buckets=20)

    # ── 3. Avalanche test ──
    print("\n" + "~" * 60)
    print("  PART 3: Avalanche Effect (flip 1 input bit)")
    print("~" * 60)
    print(f"\n  {'Function':30s}  {'Avg bits changed':>20s}  {'Ideal: 50%':>12s}")
    print(f"  {'-' * 30}  {'-' * 20}  {'-' * 12}")

    for fn, name in hash_functions:
        pct = avalanche_test(fn, num_trials=2000)
        verdict = "GOOD" if 40 <= pct <= 60 else "POOR" if 30 <= pct <= 70 else "BAD"
        print(f"  {name:30s}  {pct:19.1f}%  {verdict:>12s}")

    # ── 4. Collision counting ──
    print("\n" + "~" * 60)
    print("  PART 4: Collision Count (2000 keys, various table sizes)")
    print("~" * 60)

    for table_size in [128, 256, 512, 1024, 2048]:
        print(f"\n  Table size = {table_size}:")
        for fn, name in hash_functions:
            seen = set()
            collisions = 0
            for key in keys:
                h = fn(key, table_size)
                if h in seen:
                    collisions += 1
                seen.add(h)
            print(f"    {name:30s}  collisions: {collisions:5d} / {len(keys)} "
                  f"({collisions / len(keys) * 100:.1f}%)")

    # ── 5. Birthday paradox illustration ──
    print("\n" + "~" * 60)
    print("  PART 5: Birthday Paradox — When Does First Collision Happen?")
    print("~" * 60)

    for table_size in [256, 1024, 65536, 1_000_000]:
        theoretical = 1.177 * math.sqrt(table_size)
        # Simulate with FNV-1a
        trials = 50
        first_collisions = []
        for t in range(trials):
            seen = set()
            for i in range(table_size * 10):
                key = f"trial{t}_item{i}_{random.randint(0, 999999)}"
                h = fnv1a(key, table_size)
                if h in seen:
                    first_collisions.append(i + 1)
                    break
                seen.add(h)

        avg = sum(first_collisions) / len(first_collisions) if first_collisions else 0
        print(f"\n  m = {table_size:>10,d}  |  "
              f"Theoretical: ~{theoretical:,.0f}  |  "
              f"Observed avg: ~{avg:,.0f}  (over {trials} trials)")

    print(f"\n{'=' * 60}")
    print("All demos complete")
