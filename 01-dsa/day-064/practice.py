"""
Day 64 Practice: Hash Function Exercises
=========================================
Run: python practice.py
"""

import random
import string
import math
import time


# ─── Exercise 1: Polynomial Rolling Hash ─────────────────────────────
#
# Implement a polynomial rolling hash for strings:
#   h(s) = (s[0]*p^(n-1) + s[1]*p^(n-2) + ... + s[n-1]*p^0) mod m
#
# Where p = 31 (good prime for lowercase letters), m = 10^9 + 7.
# This is the hash used in Rabin-Karp string matching.
#
# Example:
#   rolling_hash("abc") should return a deterministic integer
#   rolling_hash("abc") == rolling_hash("abc")  (deterministic)
#   rolling_hash("abc") != rolling_hash("abd")  (usually)

def rolling_hash(s, p=31, m=10**9 + 7):
    # TODO: return the polynomial hash of string s
    # Hint: iterate through characters, accumulate hash = hash * p + ord(c)
    return None


# ─── Exercise 2: Collision Rate Measurement ──────────────────────────
#
# Hash N random strings into M buckets using a simple hash.
# Count how many collisions occur (a collision = inserting into a
# bucket that already has at least one item).
#
# Return (total_collisions, collision_rate) where rate = collisions / N
#
# Example:
#   measure_collisions(1000, 500) might return (498, 0.498)

def measure_collisions(n, m, hash_fn=None):
    # TODO: generate n random strings of length 8
    # Hash each into m buckets, count collisions
    # If hash_fn is None, use: hash(key) % m
    # Return (collision_count, collision_rate)
    return None


# ─── Exercise 3: Birthday Paradox Simulator ──────────────────────────
#
# For a hash table of size m, keep inserting random items until the
# first collision occurs. Return how many items were inserted.
# Run this many trials and return the average.
#
# Theory predicts: ~1.177 * sqrt(m) items until first collision.
#
# Example:
#   birthday_paradox(365, trials=1000) should return ~24 (close to 23.9)

def birthday_paradox(m, trials=500):
    # TODO: for each trial, insert random ints (0..m-1) until collision
    # Return the average number of inserts until first collision
    return None


# ─── Exercise 4: Deliberately Bad Hash Function ─────────────────────
#
# Implement a hash that maps EVERYTHING to bucket 0 (or the same bucket).
# Then benchmark: insert N items into a dict-like structure using
# (a) the bad hash and (b) Python's built-in hash.
# Return the timing ratio (bad_time / good_time).
#
# This demonstrates why O(1) average assumes good distribution.
# With a bad hash, lookup degrades to O(n) — a linked list in every bucket.

def bad_hash_demo(n=5000):
    # TODO:
    # 1. Define bad_hash(key) that always returns 0
    # 2. Simulate a hash table as a list of lists (separate chaining)
    # 3. Insert n items with bad_hash, time it
    # 4. Insert n items with hash(), time it
    # 5. Return (bad_time, good_time, ratio)
    return None


# ─── Exercise 5: Universal Hashing Family ────────────────────────────
#
# Implement the Carter-Wegman universal hash family:
#   h_{a,b}(x) = ((a * x + b) mod p) mod m
#
# Where p is a prime larger than the universe, a is random in [1, p-1],
# and b is random in [0, p-1].
#
# Create a class that generates random hash functions from this family.
# Verify universality: for any two distinct keys x, y, the probability
# of collision across many random functions should be close to 1/m.
#
# Example:
#   family = UniversalHashFamily(m=100, p=104729)
#   h = family.generate()
#   h(42)  # some integer in [0, 99]

class UniversalHashFamily:
    def __init__(self, m=100, p=104729):
        # TODO: store m and p
        pass

    def generate(self):
        # TODO: return a new hash function with random a, b
        # h(x) = ((a * x + b) % p) % m
        return None

    def verify_universality(self, x, y, num_functions=5000):
        # TODO: generate num_functions random hash functions
        # Count how many times h(x) == h(y)
        # Return (collision_count, collision_rate, expected_rate=1/m)
        return None


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_rolling_hash(s, p=31, m=10**9 + 7):
    """Polynomial rolling hash: h = sum(ord(c) * p^(n-1-i)) mod m."""
    h = 0
    for c in s:
        h = (h * p + ord(c)) % m
    return h


def _sol_measure_collisions(n, m, hash_fn=None):
    """Hash n random strings into m buckets, count collisions."""
    if hash_fn is None:
        hash_fn = lambda key, size: hash(key) % size

    buckets = set()
    collisions = 0
    for _ in range(n):
        key = ''.join(random.choices(string.ascii_lowercase, k=8))
        idx = hash_fn(key, m)
        if idx in buckets:
            collisions += 1
        buckets.add(idx)

    return (collisions, collisions / n)


def _sol_birthday_paradox(m, trials=500):
    """Simulate birthday paradox: avg inserts until first collision."""
    total = 0
    for _ in range(trials):
        seen = set()
        count = 0
        while True:
            val = random.randint(0, m - 1)
            count += 1
            if val in seen:
                break
            seen.add(val)
        total += count
    return total / trials


def _sol_bad_hash_demo(n=5000):
    """Compare deliberately bad hash (all to bucket 0) vs good hash."""
    num_buckets = 1024

    # Bad hash: everything goes to bucket 0
    def bad_hash(key):
        return 0

    # Simulate separate chaining hash table
    def build_and_search(hash_func, keys):
        table = [[] for _ in range(num_buckets)]
        # Insert
        for key in keys:
            idx = hash_func(key) % num_buckets
            table[idx].append(key)
        # Search for all keys (forces traversal)
        found = 0
        for key in keys:
            idx = hash_func(key) % num_buckets
            for item in table[idx]:
                if item == key:
                    found += 1
                    break
        return found

    keys = [f"key_{i}" for i in range(n)]

    start = time.perf_counter()
    build_and_search(bad_hash, keys)
    bad_time = time.perf_counter() - start

    start = time.perf_counter()
    build_and_search(hash, keys)
    good_time = time.perf_counter() - start

    ratio = bad_time / good_time if good_time > 0 else float('inf')
    return (bad_time, good_time, ratio)


class _SolUniversalHashFamily:
    def __init__(self, m=100, p=104729):
        self.m = m
        self.p = p  # Must be prime and > universe size

    def generate(self):
        """Return a random hash function from the Carter-Wegman family."""
        a = random.randint(1, self.p - 1)  # a != 0
        b = random.randint(0, self.p - 1)
        p, m = self.p, self.m
        return lambda x, _a=a, _b=b: ((_a * x + _b) % p) % m

    def verify_universality(self, x, y, num_functions=5000):
        """
        For universal hashing, P(h(x) == h(y)) should be <= 1/m.
        Generate many random hash functions and measure collision rate.
        """
        collisions = 0
        for _ in range(num_functions):
            h = self.generate()
            if h(x) == h(y):
                collisions += 1

        rate = collisions / num_functions
        expected = 1 / self.m
        return (collisions, rate, expected)


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0
    skipped = 0

    def check(name, got, expected, approx=False, tolerance=0.3):
        nonlocal passed, failed
        if approx and got is not None and expected is not None:
            if abs(got - expected) / max(abs(expected), 1) < tolerance:
                passed += 1
                print(f"  ✓ {name} (got {got:.2f}, expected ~{expected:.2f})")
                return
            else:
                failed += 1
                print(f"  ✗ {name}: got {got:.2f}, expected ~{expected:.2f}")
                return
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    def skip(name):
        nonlocal skipped
        skipped += 1
        print(f"  ⬜ {name} — not implemented")

    # Exercise 1: Rolling Hash
    print("\nExercise 1: Polynomial Rolling Hash")
    for fn, label in [(rolling_hash, "yours"), (_sol_rolling_hash, "solution")]:
        result = fn("abc")
        if result is None and fn is rolling_hash:
            skip("rolling_hash")
            break
        # Deterministic check
        check(f"{label}: deterministic", fn("abc"), fn("abc"))
        # Different inputs should (almost always) differ
        r1, r2 = fn("abc"), fn("abd")
        check(f"{label}: different inputs differ", r1 != r2, True)
        # Known computation: h("a") = ord('a') = 97
        check(f"{label}: single char", fn("a"), ord('a'))

    # Exercise 2: Collision Rate
    print("\nExercise 2: Collision Rate Measurement")
    for fn, label in [(measure_collisions, "yours"), (_sol_measure_collisions, "solution")]:
        result = fn(1000, 500)
        if result is None and fn is measure_collisions:
            skip("measure_collisions")
            break
        count, rate = result
        # With 1000 items in 500 buckets, expect significant collisions
        check(f"{label}: collision count > 0", count > 0, True)
        check(f"{label}: rate reasonable", 0.1 < rate < 0.9, True)

    # Exercise 3: Birthday Paradox
    print("\nExercise 3: Birthday Paradox Simulator")
    for fn, label in [(birthday_paradox, "yours"), (_sol_birthday_paradox, "solution")]:
        result = fn(365, trials=200)
        if result is None and fn is birthday_paradox:
            skip("birthday_paradox")
            break
        theoretical = 1.177 * math.sqrt(365)  # ~24.6
        check(f"{label}: avg ~24 for m=365", result, theoretical,
              approx=True, tolerance=0.25)

    # Exercise 4: Bad Hash Demo
    print("\nExercise 4: Bad Hash Performance Degradation")
    for fn, label in [(bad_hash_demo, "yours"), (_sol_bad_hash_demo, "solution")]:
        result = fn(2000)
        if result is None and fn is bad_hash_demo:
            skip("bad_hash_demo")
            break
        bad_time, good_time, ratio = result
        # Bad hash should be significantly slower
        check(f"{label}: bad hash slower (ratio={ratio:.1f}x)", ratio > 2.0, True)
        print(f"    (bad={bad_time:.4f}s  good={good_time:.4f}s  ratio={ratio:.1f}x)")

    # Exercise 5: Universal Hashing
    print("\nExercise 5: Universal Hashing Family")
    for Cls, label in [(UniversalHashFamily, "yours"), (_SolUniversalHashFamily, "solution")]:
        family = Cls(m=100, p=104729)
        h = family.generate()
        if h is None and Cls is UniversalHashFamily:
            skip("UniversalHashFamily")
            break
        # Check that generate produces a callable
        try:
            val = h(42)
            check(f"{label}: h(42) in range [0, 100)", 0 <= val < 100, True)
        except Exception as e:
            failed += 1
            print(f"  ✗ {label}: h(42) raised {e}")
            continue

        # Verify universality
        result = family.verify_universality(42, 99, num_functions=3000)
        if result is None:
            skip(f"{label}: verify_universality")
            continue
        collisions, rate, expected = result
        # Rate should be close to 1/m = 0.01
        check(f"{label}: collision rate ~1/m", rate, expected,
              approx=True, tolerance=0.5)
        print(f"    (collisions={collisions}/3000  rate={rate:.4f}  expected={expected:.4f})")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} not yet implemented")
    if skipped > 0:
        print(f"\nHint: Replace 'return None' with your implementation!")


if __name__ == "__main__":
    run_tests()
