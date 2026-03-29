"""
Day 73: HyperLogLog — Cardinality Estimation with O(1) Space

Core idea: hash each element, count leading zeros in the hash.
The maximum leading zeros across many elements estimates log2(cardinality).
Use multiple registers (stochastic averaging) to reduce variance.
Combine with harmonic mean for robust estimation.

No external dependencies — pure Python 3.
"""

import hashlib
import struct
import math
import sys


class HyperLogLog:
    """
    HyperLogLog cardinality estimator.

    Parameters:
        p (int): Precision parameter. Uses m = 2^p registers.
                 Higher p = more memory, less error.
                 Standard error = 1.04 / sqrt(2^p).
                 p=14 is the Redis default (16384 registers, ~16KB).

    Memory usage: 2^p bytes (one byte per register, storing max leading zeros).
    """

    def __init__(self, p=14):
        if not (4 <= p <= 16):
            raise ValueError(f"Precision p must be in [4, 16], got {p}")
        self.p = p
        self.m = 1 << p          # Number of registers = 2^p
        self.registers = bytearray(self.m)  # Each register: max leading zeros seen

        # Alpha constant for bias correction (depends on m)
        # Derived from the integral of the harmonic mean estimator's bias
        if self.m == 16:
            self.alpha = 0.673
        elif self.m == 32:
            self.alpha = 0.697
        elif self.m == 64:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1.0 + 1.079 / self.m)

    def _hash(self, item):
        """
        Hash an item to a 32-bit integer.

        Why 32 bits? It's enough for the leading-zero trick (max 32 leading zeros
        means we can estimate up to ~2^32 unique items). Using a cryptographic hash
        (md5) ensures good uniformity — critical for HLL accuracy.
        """
        # Use md5 for good distribution, take first 4 bytes as uint32
        h = hashlib.md5(str(item).encode('utf-8')).digest()
        return struct.unpack('<I', h[:4])[0]

    def _leading_zeros(self, value, max_bits):
        """
        Count leading zeros in the binary representation.

        Why this matters: P(k leading zeros) = 1/2^k for a uniform random hash.
        So seeing k leading zeros suggests ~2^k unique items hashed into this register.
        We add 1 because even zero leading zeros means we saw at least 1 element.
        """
        if value == 0:
            return max_bits  # All zeros
        count = 0
        # Check bits from the most significant end
        for i in range(max_bits - 1, -1, -1):
            if value & (1 << i):
                break
            count += 1
        return count

    def add(self, item):
        """
        Add an item to the HyperLogLog sketch.

        Steps:
        1. Hash the item to 32 bits
        2. First p bits -> register index (which bucket)
        3. Remaining (32-p) bits -> count leading zeros + 1
        4. Update register to max(current, new count)

        Why max? We want the maximum leading zeros ever seen per register.
        Adding the same item twice produces the same hash, same register,
        same leading zeros — so duplicates are naturally ignored.
        """
        x = self._hash(item)

        # First p bits determine the register index
        # Right-shift to get the top p bits
        j = x >> (32 - self.p)

        # Remaining (32 - p) bits are used for leading zero count
        # Mask off the top p bits, then count leading zeros in what remains
        remaining_bits = 32 - self.p
        w = x & ((1 << remaining_bits) - 1)  # Keep only the lower (32-p) bits

        # Count leading zeros + 1 (the +1 ensures minimum value of 1, not 0)
        rho = self._leading_zeros(w, remaining_bits) + 1

        # Store the maximum — this is the core of the probabilistic argument
        if rho > self.registers[j]:
            self.registers[j] = rho

    def count(self):
        """
        Estimate the cardinality (number of unique items added).

        Uses the harmonic mean of 2^(-register_value) across all registers.
        Harmonic mean is key: it's resistant to outlier registers that got
        lucky with many leading zeros.

        Three regimes with different corrections:
        1. Small range: LinearCounting (uses empty register count)
        2. Medium range: Raw HLL estimate with alpha correction
        3. Large range: Hash collision correction for 32-bit space
        """
        # Raw HLL estimate using harmonic mean
        # E = alpha * m^2 / sum(2^(-M[j]))
        indicator_sum = sum(2.0 ** (-reg) for reg in self.registers)
        estimate = self.alpha * self.m * self.m / indicator_sum

        # Small range correction: LinearCounting
        # When many registers are empty, the HLL estimate is biased low.
        # LinearCounting uses the fraction of empty registers, which follows
        # a Poisson model that's accurate for small cardinalities.
        if estimate <= 2.5 * self.m:
            empty_registers = self.registers.count(0)
            if empty_registers > 0:
                # LinearCounting: E = m * ln(m/V) where V = empty count
                estimate = self.m * math.log(self.m / empty_registers)
            # If no empty registers, use the raw estimate (it's fine)

        # Large range correction: hash collision adjustment
        # At very high cardinalities, 32-bit hashes start colliding,
        # making the estimate too low. This corrects for that.
        elif estimate > (1 << 32) / 30.0:
            estimate = -(1 << 32) * math.log(1.0 - estimate / (1 << 32))

        return int(estimate)

    def merge(self, other):
        """
        Merge another HyperLogLog into this one.

        Returns a new HLL estimating |A union B|.

        Why element-wise max works: each register tracks the maximum leading
        zeros seen. If item X went to register j in HLL_A, the same hash puts
        it in register j in HLL_B. Taking max(A[j], B[j]) is equivalent to
        having seen all items from both sets.

        This is what makes HLL so powerful for distributed systems —
        you can compute partial sketches on different machines and merge them.
        """
        if self.p != other.p:
            raise ValueError(
                f"Cannot merge HLLs with different precision: {self.p} vs {other.p}"
            )
        merged = HyperLogLog(self.p)
        for i in range(self.m):
            merged.registers[i] = max(self.registers[i], other.registers[i])
        return merged

    def memory_bytes(self):
        """Return memory used by registers in bytes."""
        return self.m  # One byte per register

    def standard_error(self):
        """Theoretical standard error for this precision."""
        return 1.04 / math.sqrt(self.m)

    def __repr__(self):
        return (
            f"HyperLogLog(p={self.p}, registers={self.m}, "
            f"memory={self.memory_bytes()}B, "
            f"std_error={self.standard_error():.4f})"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_basic_counting():
    """Show HLL counting 1M unique items with constant memory."""
    print("=" * 70)
    print("DEMO: HyperLogLog Basic Counting")
    print("=" * 70)

    hll = HyperLogLog(p=14)
    actual = 1_000_000

    print(f"\nAdding {actual:,} unique items to HyperLogLog (p=14)...")
    for i in range(actual):
        hll.add(f"item-{i}")

    estimate = hll.count()
    error_pct = abs(estimate - actual) / actual * 100

    print(f"  Actual unique items:    {actual:>12,}")
    print(f"  HLL estimate:           {estimate:>12,}")
    print(f"  Error:                  {error_pct:>11.2f}%")
    print(f"  Theoretical std error:  {hll.standard_error() * 100:>11.2f}%")
    print(f"  Memory used:            {hll.memory_bytes():>11,} bytes")
    print(f"  HashSet would need:     ~{actual * 60 // 1_000_000:>9,} MB")
    print(f"  Memory ratio:           ~{actual * 60 // hll.memory_bytes():>9,}x smaller")


def demo_constant_memory():
    """Show that memory stays constant regardless of cardinality."""
    print("\n" + "=" * 70)
    print("DEMO: Constant Memory Regardless of Cardinality")
    print("=" * 70)

    hll = HyperLogLog(p=10)
    print(f"\nHLL with p=10 ({hll.memory_bytes()} bytes always)")
    print(f"{'Items Added':>15} {'Estimate':>12} {'Error %':>10} {'Memory (bytes)':>16}")
    print("-" * 55)

    for n in [100, 1_000, 10_000, 100_000, 500_000]:
        hll_fresh = HyperLogLog(p=10)
        for i in range(n):
            hll_fresh.add(f"element-{i}")
        est = hll_fresh.count()
        err = abs(est - n) / n * 100
        print(f"{n:>15,} {est:>12,} {err:>9.2f}% {hll_fresh.memory_bytes():>16,}")


def demo_duplicates():
    """Show that duplicates don't affect the count."""
    print("\n" + "=" * 70)
    print("DEMO: Duplicates Are Ignored")
    print("=" * 70)

    hll = HyperLogLog(p=14)
    unique_items = 10_000

    # Add each item 100 times
    for i in range(unique_items):
        for _ in range(100):
            hll.add(f"user-{i}")

    estimate = hll.count()
    total_adds = unique_items * 100
    error_pct = abs(estimate - unique_items) / unique_items * 100

    print(f"\n  Total add() calls:      {total_adds:>12,}")
    print(f"  Actual unique items:    {unique_items:>12,}")
    print(f"  HLL estimate:           {estimate:>12,}")
    print(f"  Error:                  {error_pct:>11.2f}%")
    print(f"\n  Same hash -> same register -> same leading zeros -> no change.")


def demo_merge():
    """Show merging two HLL sketches."""
    print("\n" + "=" * 70)
    print("DEMO: Merging HyperLogLog Sketches")
    print("=" * 70)

    hll_a = HyperLogLog(p=12)
    hll_b = HyperLogLog(p=12)

    # A has items 0..49999, B has items 30000..79999
    # Union should be ~80000, intersection ~20000
    for i in range(50_000):
        hll_a.add(f"item-{i}")
    for i in range(30_000, 80_000):
        hll_b.add(f"item-{i}")

    merged = hll_a.merge(hll_b)

    est_a = hll_a.count()
    est_b = hll_b.count()
    est_union = merged.count()
    actual_union = 80_000

    print(f"\n  Set A: items 0..49,999      (actual: 50,000, est: {est_a:,})")
    print(f"  Set B: items 30,000..79,999 (actual: 50,000, est: {est_b:,})")
    print(f"  A union B:                  (actual: {actual_union:,}, est: {est_union:,})")
    print(f"  Error on union:             {abs(est_union - actual_union) / actual_union * 100:.2f}%")

    # Inclusion-exclusion for intersection
    est_intersection = est_a + est_b - est_union
    actual_intersection = 20_000
    print(f"\n  A intersect B (inclusion-exclusion):")
    print(f"    |A| + |B| - |A union B| = {est_a:,} + {est_b:,} - {est_union:,} = {est_intersection:,}")
    print(f"    Actual intersection:      {actual_intersection:,}")
    print(f"    (Note: intersection estimates have higher relative error)")


def demo_precision_tradeoff():
    """Show memory vs accuracy for different precision values."""
    print("\n" + "=" * 70)
    print("DEMO: Precision vs Accuracy Trade-off")
    print("=" * 70)

    actual = 100_000
    print(f"\n  Counting {actual:,} unique items at different precisions:\n")
    print(f"  {'p':>4} {'Registers':>10} {'Memory':>10} {'Estimate':>12} {'Error %':>10} {'Theory SE':>10}")
    print("  " + "-" * 60)

    for p in [4, 6, 8, 10, 12, 14]:
        hll = HyperLogLog(p=p)
        for i in range(actual):
            hll.add(f"x-{i}")
        est = hll.count()
        err = abs(est - actual) / actual * 100
        mem = hll.memory_bytes()
        se = hll.standard_error() * 100
        mem_str = f"{mem} B" if mem < 1024 else f"{mem // 1024} KB"
        print(f"  {p:>4} {hll.m:>10,} {mem_str:>10} {est:>12,} {err:>9.2f}% {se:>9.2f}%")


if __name__ == "__main__":
    demo_basic_counting()
    demo_constant_memory()
    demo_duplicates()
    demo_merge()
    demo_precision_tradeoff()
