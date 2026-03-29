"""
Day 71: Bloom Filter Implementation

A Bloom filter is a space-efficient probabilistic data structure for set
membership testing. It can tell you "definitely not in set" or "probably
in set" — never the reverse. The trade-off: a tunable false positive rate
in exchange for dramatic space savings.

Key insight: we use double hashing to simulate k independent hash functions
from just 2 base hashes. h_i(x) = h1(x) + i * h2(x) mod m. This is
mathematically proven to give the same false positive guarantees as truly
independent hash functions (Kirsch & Mitzenmacher, 2004).
"""

import math
import hashlib
import struct


class BloomFilter:
    """
    Standard Bloom filter with configurable capacity and false positive rate.

    The filter auto-computes optimal m (number of bits) and k (number of
    hash functions) from the desired capacity and false positive rate.
    """

    def __init__(self, capacity: int, fp_rate: float = 0.01):
        """
        Args:
            capacity: Expected number of elements to insert.
            fp_rate: Desired false positive rate (0 < fp_rate < 1).
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if not (0 < fp_rate < 1):
            raise ValueError("False positive rate must be between 0 and 1")

        self.capacity = capacity
        self.fp_rate = fp_rate
        self._count = 0

        # Optimal bit array size: m = -(n * ln(p)) / (ln(2))^2
        self.m = self._optimal_m(capacity, fp_rate)

        # Optimal hash count: k = (m/n) * ln(2)
        self.k = self._optimal_k(self.m, capacity)

        # Bit array stored as a bytearray for memory efficiency
        # We need ceil(m / 8) bytes
        self._bits = bytearray((self.m + 7) // 8)

    @staticmethod
    def _optimal_m(n: int, p: float) -> int:
        """Compute optimal number of bits for n items at FP rate p."""
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return max(1, int(math.ceil(m)))

    @staticmethod
    def _optimal_k(m: int, n: int) -> int:
        """Compute optimal number of hash functions."""
        k = (m / n) * math.log(2)
        return max(1, int(round(k)))

    def _hashes(self, item: str) -> list:
        """
        Generate k hash positions using double hashing.

        We compute two independent hashes from the item using MD5
        (split the 128-bit digest into two 64-bit halves), then derive
        k positions as: h_i = (h1 + i * h2) mod m.

        Why MD5? Not for security — for uniform distribution. We need
        hash values that spread bits evenly across the array.
        """
        # Encode item and compute MD5 (128 bits = 16 bytes)
        digest = hashlib.md5(item.encode("utf-8")).digest()

        # Split into two 64-bit integers
        h1 = struct.unpack_from("<Q", digest, 0)[0]
        h2 = struct.unpack_from("<Q", digest, 8)[0]

        # Ensure h2 is odd so (h1 + i*h2) mod m cycles through more positions
        # when m is even. Small optimization for better distribution.
        if h2 % 2 == 0:
            h2 += 1

        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def _get_bit(self, pos: int) -> bool:
        """Check if bit at position pos is set."""
        byte_index = pos // 8
        bit_offset = pos % 8
        return bool(self._bits[byte_index] & (1 << bit_offset))

    def _set_bit(self, pos: int):
        """Set the bit at position pos."""
        byte_index = pos // 8
        bit_offset = pos % 8
        self._bits[byte_index] |= (1 << bit_offset)

    def add(self, item: str):
        """
        Add an item to the Bloom filter.

        Sets k bit positions determined by the hash functions.
        Once a bit is set, it can never be cleared (in a standard Bloom filter).
        """
        if not isinstance(item, str):
            item = str(item)

        already_present = True
        for pos in self._hashes(item):
            if not self._get_bit(pos):
                already_present = False
            self._set_bit(pos)

        # Only increment count if item wasn't already (probably) present.
        # This is an estimate — we can't know for sure due to false positives.
        if not already_present:
            self._count += 1

    def contains(self, item: str) -> bool:
        """
        Test if an item is (probably) in the set.

        Returns:
            False — item is DEFINITELY NOT in the set (no false negatives).
            True  — item is PROBABLY in the set (false positives possible).
        """
        if not isinstance(item, str):
            item = str(item)
        return all(self._get_bit(pos) for pos in self._hashes(item))

    def __contains__(self, item: str) -> bool:
        """Support 'in' operator: item in bloom_filter."""
        return self.contains(item)

    def estimated_count(self) -> int:
        """
        Return the estimated number of items inserted.

        This uses the count of set bits to estimate n:
        n_est = -(m/k) * ln(1 - X/m)
        where X = number of bits set to 1.
        """
        # Count set bits
        set_bits = 0
        for byte in self._bits:
            set_bits += bin(byte).count("1")

        if set_bits == 0:
            return 0
        if set_bits >= self.m:
            return self.capacity  # Saturated

        # Mathematical estimate based on bit saturation
        ratio = set_bits / self.m
        return int(round(-(self.m / self.k) * math.log(1 - ratio)))

    def false_positive_rate(self) -> float:
        """
        Compute the current theoretical false positive rate based on
        the number of items inserted.

        FP = (1 - e^(-k * n / m))^k

        This differs from the design FP rate because it uses the actual
        count of inserted items rather than the expected capacity.
        """
        n = self._count
        if n == 0:
            return 0.0
        exponent = -self.k * n / self.m
        return (1 - math.exp(exponent)) ** self.k

    def bits_per_element(self) -> float:
        """Return bits used per element inserted."""
        if self._count == 0:
            return float("inf")
        return self.m / self._count

    def saturation(self) -> float:
        """Return fraction of bits that are set (0.0 to 1.0)."""
        set_bits = sum(bin(byte).count("1") for byte in self._bits)
        return set_bits / self.m

    def __repr__(self) -> str:
        return (
            f"BloomFilter(capacity={self.capacity}, fp_rate={self.fp_rate}, "
            f"m={self.m} bits, k={self.k} hashes, "
            f"count~{self._count}, saturation={self.saturation():.2%})"
        )


class CountingBloomFilter:
    """
    Counting Bloom Filter — supports deletion by using 4-bit counters
    instead of single bits.

    Each slot is a 4-bit counter (0-15). Insert increments, delete
    decrements. This allows removal of elements without corrupting
    other entries. The trade-off: 4x the space of a standard Bloom filter.

    Why 4 bits? In practice, counters rarely exceed 16 even with high
    load factors. Overflow is handled by capping at 15 (the counter
    becomes "sticky" and can never be decremented below 15).
    """

    MAX_COUNT = 15  # 4-bit counter maximum

    def __init__(self, capacity: int, fp_rate: float = 0.01):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if not (0 < fp_rate < 1):
            raise ValueError("False positive rate must be between 0 and 1")

        self.capacity = capacity
        self.fp_rate = fp_rate
        self._count = 0

        self.m = BloomFilter._optimal_m(capacity, fp_rate)
        self.k = BloomFilter._optimal_k(self.m, capacity)

        # 4-bit counters stored as a list of ints (simple and clear)
        # In production, you'd pack two counters per byte.
        self._counters = [0] * self.m

    def _hashes(self, item: str) -> list:
        """Same double-hashing scheme as BloomFilter."""
        if not isinstance(item, str):
            item = str(item)
        digest = hashlib.md5(item.encode("utf-8")).digest()
        h1 = struct.unpack_from("<Q", digest, 0)[0]
        h2 = struct.unpack_from("<Q", digest, 8)[0]
        if h2 % 2 == 0:
            h2 += 1
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item: str):
        """Insert an item by incrementing k counter positions."""
        if not isinstance(item, str):
            item = str(item)

        for pos in self._hashes(item):
            if self._counters[pos] < self.MAX_COUNT:
                self._counters[pos] += 1
            # If counter == MAX_COUNT, it becomes sticky (never decrements)
            # to prevent underflow from corrupting the filter.

        self._count += 1

    def remove(self, item: str) -> bool:
        """
        Remove an item by decrementing k counter positions.

        Returns True if the item was (probably) present, False otherwise.

        WARNING: Removing an item that was never inserted will corrupt
        the filter by decrementing counters that belong to other items.
        Always check contains() before removing if unsure.
        """
        if not isinstance(item, str):
            item = str(item)

        positions = self._hashes(item)

        # Check membership first
        if not all(self._counters[pos] > 0 for pos in positions):
            return False  # Definitely not present

        # Decrement counters (skip sticky ones at MAX_COUNT)
        for pos in positions:
            if self._counters[pos] < self.MAX_COUNT:
                self._counters[pos] -= 1
            # Sticky counters at MAX_COUNT are not decremented to prevent
            # underflow — once saturated, the slot is permanently "on."

        self._count -= 1
        return True

    def contains(self, item: str) -> bool:
        """Test if item is probably in the set."""
        if not isinstance(item, str):
            item = str(item)
        return all(self._counters[pos] > 0 for pos in self._hashes(item))

    def __contains__(self, item: str) -> bool:
        return self.contains(item)

    def __repr__(self) -> str:
        return (
            f"CountingBloomFilter(capacity={self.capacity}, fp_rate={self.fp_rate}, "
            f"m={self.m} slots, k={self.k} hashes, count={self._count})"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo():
    """Demonstrate Bloom filter behavior with 100K items."""
    print("=" * 70)
    print("BLOOM FILTER DEMO: 100K items, 1% target FP rate")
    print("=" * 70)

    n = 100_000
    target_fp = 0.01
    bf = BloomFilter(capacity=n, fp_rate=target_fp)

    print(f"\nFilter parameters:")
    print(f"  Capacity (n):       {n:,}")
    print(f"  Target FP rate:     {target_fp:.2%}")
    print(f"  Bit array size (m): {bf.m:,} bits ({bf.m / 8 / 1024:.1f} KB)")
    print(f"  Hash functions (k): {bf.k}")
    print(f"  Bits per element:   {bf.m / n:.1f}")

    # Insert 100K items
    print(f"\nInserting {n:,} items...")
    for i in range(n):
        bf.add(f"item-{i}")

    print(f"  Estimated count:    {bf.estimated_count():,}")
    print(f"  Actual count:       {bf._count:,}")
    print(f"  Saturation:         {bf.saturation():.2%}")
    print(f"  Theoretical FP:     {bf.false_positive_rate():.4%}")

    # No false negatives — verify every inserted item is found
    print(f"\nVerifying no false negatives...")
    false_negatives = sum(1 for i in range(n) if f"item-{i}" not in bf)
    print(f"  False negatives:    {false_negatives} (must be 0)")

    # Measure actual false positive rate with items NOT in the set
    test_count = 100_000
    print(f"\nMeasuring actual FP rate with {test_count:,} non-member queries...")
    false_positives = sum(
        1 for i in range(n, n + test_count)
        if f"item-{i}" in bf
    )
    actual_fp = false_positives / test_count
    print(f"  False positives:    {false_positives:,} / {test_count:,}")
    print(f"  Actual FP rate:     {actual_fp:.4%}")
    print(f"  Theoretical FP:     {bf.false_positive_rate():.4%}")
    print(f"  Target FP rate:     {target_fp:.4%}")

    # Compare across different FP rates
    print(f"\n{'=' * 70}")
    print("COMPARISON: Same 100K items, different FP rates")
    print(f"{'=' * 70}")
    print(f"{'FP Rate':>10} | {'Bits (m)':>12} | {'Hashes (k)':>10} | {'Size (KB)':>10} | {'Bits/elem':>10}")
    print("-" * 62)
    for fp in [0.1, 0.05, 0.01, 0.001, 0.0001]:
        test_bf = BloomFilter(capacity=n, fp_rate=fp)
        size_kb = test_bf.m / 8 / 1024
        bpe = test_bf.m / n
        print(f"{fp:>10.4f} | {test_bf.m:>12,} | {test_bf.k:>10} | {size_kb:>10.1f} | {bpe:>10.1f}")

    # Counting Bloom Filter demo
    print(f"\n{'=' * 70}")
    print("COUNTING BLOOM FILTER: Deletion support")
    print(f"{'=' * 70}")

    cbf = CountingBloomFilter(capacity=1000, fp_rate=0.01)
    test_items = [f"url-{i}" for i in range(100)]

    for item in test_items:
        cbf.add(item)

    print(f"\nInserted {len(test_items)} items")
    print(f"  'url-0' present?    {cbf.contains('url-0')}")
    print(f"  'url-99' present?   {cbf.contains('url-99')}")

    # Delete half
    for item in test_items[:50]:
        cbf.remove(item)

    print(f"\nDeleted first 50 items")
    print(f"  'url-0' present?    {cbf.contains('url-0')}  (was deleted)")
    print(f"  'url-49' present?   {cbf.contains('url-49')} (was deleted)")
    print(f"  'url-50' present?   {cbf.contains('url-50')} (still present)")
    print(f"  'url-99' present?   {cbf.contains('url-99')} (still present)")

    print(f"\nSpace comparison for Counting vs Standard:")
    std = BloomFilter(capacity=n, fp_rate=0.01)
    cbf_large = CountingBloomFilter(capacity=n, fp_rate=0.01)
    print(f"  Standard:  {std.m / 8 / 1024:.1f} KB (1 bit per slot)")
    print(f"  Counting:  {cbf_large.m * 4 / 8 / 1024:.1f} KB (4 bits per slot)")
    print(f"  Ratio:     4x space for deletion support")


if __name__ == "__main__":
    demo()
