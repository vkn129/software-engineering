"""
Day 149: Sieve of Eratosthenes — basic + segmented.

Basic: O(n log log n) time, O(n) space. Use when n <= ~1e8.
Segmented: same time, O(sqrt n) memory. Required for large n and cache-friendly.
"""

import math
import time


# ---------------------------------------------------------------------------
# 1. Basic sieve — O(n log log n)
# ---------------------------------------------------------------------------

def sieve_basic(n):
    """All primes p with 2 <= p <= n. Uses a bytearray (memory-cheap)."""
    if n < 2:
        return []
    # bytearray: each element is 1 byte (not 28 like list-of-bool in Python).
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0] = is_prime[1] = 0

    # Only need to cross multiples up to sqrt(n); past that everything
    # composite already has a smaller prime factor that already marked it.
    limit = int(math.isqrt(n))
    for i in range(2, limit + 1):
        if is_prime[i]:
            # Start at i*i: smaller multiples already killed by smaller primes.
            # Step by i (not 2*i): keep it general so it works for i = 2.
            is_prime[i * i:n + 1:i] = bytearray(len(range(i * i, n + 1, i)))

    return [i for i in range(2, n + 1) if is_prime[i]]


# ---------------------------------------------------------------------------
# 2. Linear sieve — O(n), also gives smallest prime factor (SPF)
# ---------------------------------------------------------------------------

def sieve_linear(n):
    """Returns (primes, spf) where spf[i] = smallest prime factor of i."""
    spf = [0] * (n + 1)
    primes = []
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        # Mark i*p for each prime p <= spf[i].
        # Stopping at p == spf[i] guarantees each composite marked once.
        for p in primes:
            if p > spf[i] or i * p > n:
                break
            spf[i * p] = p
    return primes, spf


# ---------------------------------------------------------------------------
# 3. Segmented sieve — primes in [lo, hi]
# ---------------------------------------------------------------------------

def sieve_segmented(lo, hi, segment_size=1 << 15):
    """
    Primes in [lo, hi]. Memory: O(sqrt(hi) + segment_size).
    `segment_size` chosen ~32 KB to fit L1 cache.
    """
    if hi < 2 or lo > hi:
        return []
    lo = max(lo, 2)

    # Small primes up to sqrt(hi): basic sieve.
    limit = int(math.isqrt(hi))
    small = sieve_basic(limit)

    result = []
    seg_lo = lo
    while seg_lo <= hi:
        seg_hi = min(seg_lo + segment_size - 1, hi)
        # bitset for this chunk
        is_prime = bytearray(b"\x01") * (seg_hi - seg_lo + 1)

        for p in small:
            # First multiple of p >= seg_lo, but not p itself.
            start = max(p * p, ((seg_lo + p - 1) // p) * p)
            for j in range(start, seg_hi + 1, p):
                is_prime[j - seg_lo] = 0

        for i in range(seg_lo, seg_hi + 1):
            if i >= 2 and is_prime[i - seg_lo]:
                result.append(i)

        seg_lo = seg_hi + 1

    return result


# ---------------------------------------------------------------------------
# 4. Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic Sieve")
    print("=" * 60)
    primes = sieve_basic(50)
    print(f"Primes <= 50: {primes}")
    primes = sieve_basic(100000)
    print(f"|primes <= 100000| = {len(primes)} (known: 9592)")


def demo_linear():
    print("\n" + "=" * 60)
    print("DEMO 2: Linear Sieve (with smallest prime factor)")
    print("=" * 60)
    primes, spf = sieve_linear(30)
    print(f"Primes <= 30: {primes}")
    print(f"SPF table:")
    for i in range(2, 21):
        print(f"  spf[{i:2d}] = {spf[i]}")


def demo_segmented():
    print("\n" + "=" * 60)
    print("DEMO 3: Segmented Sieve")
    print("=" * 60)
    # Primes in a high range
    lo, hi = 10**9, 10**9 + 200
    primes = sieve_segmented(lo, hi)
    print(f"Primes in [{lo}, {hi}]: {primes}")
    print(f"Count: {len(primes)}")


def demo_compare():
    print("\n" + "=" * 60)
    print("DEMO 4: Basic vs Segmented Performance")
    print("=" * 60)
    n = 5_000_000

    t = time.perf_counter()
    p1 = sieve_basic(n)
    t_basic = time.perf_counter() - t

    t = time.perf_counter()
    p2 = sieve_segmented(2, n)
    t_seg = time.perf_counter() - t

    print(f"Find all primes up to {n}:")
    print(f"  Basic:     {t_basic*1000:7.2f} ms  count={len(p1)}")
    print(f"  Segmented: {t_seg*1000:7.2f} ms  count={len(p2)}")
    print(f"  Same result: {p1 == p2}")


if __name__ == "__main__":
    demo_basic()
    demo_linear()
    demo_segmented()
    demo_compare()
