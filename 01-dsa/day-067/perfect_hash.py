"""
Day 67: Perfect Hashing — O(1) Worst-Case Lookup for Static Sets

Two implementations:
1. FKSPerfectHash: two-level scheme (Fredman-Komlós-Szemerédi)
   - First level: universal hash into n buckets
   - Second level: per-bucket perfect hash into ni^2 slots
   - Guarantees O(1) worst-case lookup, O(n) total space

2. MinimalPerfectHash: maps n keys bijectively to [0, n-1]
   - Brute-force approach for small n (demonstrates the concept)
   - Tries random hash functions until one is collision-free and covers [0, n-1]

Run:
    python perfect_hash.py
"""

import random
import time
import keyword


# ---------------------------------------------------------------------------
# Universal hash family: h(k) = ((a * k + b) mod p) mod m
# For string keys, we first convert to an integer via a polynomial hash.
# ---------------------------------------------------------------------------

def _string_to_int(s: str) -> int:
    """Convert a string to a large integer using polynomial rolling hash.
    We use a large base and do not take mod here — we want the full integer
    so the universal hash family can operate on it."""
    h = 0
    for ch in s:
        h = h * 1000003 + ord(ch)
    return h & ((1 << 61) - 1)  # keep it within 61-bit Mersenne range


# A large prime for universal hashing — Mersenne prime 2^61 - 1
_PRIME = (1 << 61) - 1


def _make_universal_hash(m: int):
    """Return a universal hash function mapping integers to [0, m-1].
    Uses h(k) = ((a*k + b) mod p) mod m with random a, b."""
    a = random.randint(1, _PRIME - 1)
    b = random.randint(0, _PRIME - 1)

    def h(key_int: int) -> int:
        return ((a * key_int + b) % _PRIME) % m

    return h, (a, b)


# ---------------------------------------------------------------------------
# FKS Perfect Hash Table
# ---------------------------------------------------------------------------

class FKSPerfectHash:
    """Two-level FKS perfect hash table for a static set of string keys.

    Construction:
        ph = FKSPerfectHash()
        ph.build(keys)

    Lookup:
        ph.lookup("some_key")  -> True/False, O(1) worst case
    """

    def __init__(self):
        self.n = 0
        self.m = 0                  # number of first-level buckets
        self._first_hash = None     # (function, params)
        self._second_hashes = []    # list of (function, params) per bucket
        self._tables = []           # list of second-level tables (lists)
        self._bucket_sizes = []     # ni^2 for each bucket
        self._key_ints = {}         # cache: key string -> integer
        self._keys = set()          # original key set for verification

    def build(self, keys: list[str]):
        """Build the two-level perfect hash structure.

        Args:
            keys: list of unique string keys (static set)
        """
        keys = list(set(keys))  # deduplicate
        self.n = len(keys)
        self._keys = set(keys)

        if self.n == 0:
            self.m = 0
            return

        self.m = self.n  # first-level table size = n

        # Precompute integer representations
        self._key_ints = {k: _string_to_int(k) for k in keys}

        # --- Level 1: find a first-level hash with sum(ni^2) <= 4n ---
        self._build_first_level(keys)

        # --- Level 2: for each bucket, find a collision-free hash ---
        self._build_second_level()

    def _build_first_level(self, keys: list[str]):
        """Find a first-level universal hash where sum(ni^2) <= 4n."""
        max_attempts = 100
        for _ in range(max_attempts):
            h_func, h_params = _make_universal_hash(self.m)

            # Distribute keys into buckets
            buckets = [[] for _ in range(self.m)]
            for k in keys:
                bucket_idx = h_func(self._key_ints[k])
                buckets[bucket_idx].append(k)

            # Check space bound: sum(ni^2) <= 4n
            total_sq = sum(len(b) ** 2 for b in buckets)
            if total_sq <= 4 * self.n:
                self._first_hash = (h_func, h_params)
                self._buckets = buckets
                return

        # Fallback — should almost never happen
        raise RuntimeError(
            f"Could not find first-level hash with good space bound "
            f"after {max_attempts} attempts"
        )

    def _build_second_level(self):
        """For each bucket, find a hash function with zero collisions
        into a table of size ni^2."""
        self._tables = []
        self._second_hashes = []
        self._bucket_sizes = []
        self.second_level_trials = []  # track trials per bucket

        for bucket in self._buckets:
            ni = len(bucket)
            if ni == 0:
                self._tables.append([])
                self._second_hashes.append((None, None))
                self._bucket_sizes.append(0)
                self.second_level_trials.append(0)
                continue

            if ni == 1:
                # Only one key — trivial, no collision possible
                table = [None]
                self._tables.append([bucket[0]])
                self._second_hashes.append((_make_universal_hash(1)))
                self._bucket_sizes.append(1)
                self.second_level_trials.append(1)
                continue

            table_size = ni * ni  # ni^2 slots
            key_ints = [self._key_ints[k] for k in bucket]
            trials = 0

            while True:
                trials += 1
                h_func, h_params = _make_universal_hash(table_size)

                # Check for collisions
                slots = [None] * table_size
                collision = False
                for i, k in enumerate(bucket):
                    idx = h_func(key_ints[i])
                    if slots[idx] is not None:
                        collision = True
                        break
                    slots[idx] = k

                if not collision:
                    self._tables.append(slots)
                    self._second_hashes.append((h_func, h_params))
                    self._bucket_sizes.append(table_size)
                    self.second_level_trials.append(trials)
                    break

    def lookup(self, key: str) -> bool:
        """Look up a key in O(1) worst case.

        Returns True if key is in the set, False otherwise.
        Exactly two hash computations — no loops, no chains.
        """
        if self.n == 0:
            return False

        key_int = _string_to_int(key)

        # Level 1: which bucket?
        h1 = self._first_hash[0]
        bucket_idx = h1(key_int)

        # Level 2: which slot in that bucket's table?
        table = self._tables[bucket_idx]
        if not table:
            return False

        h2 = self._second_hashes[bucket_idx][0]
        slot_idx = h2(key_int)

        if slot_idx >= len(table):
            return False

        return table[slot_idx] == key

    def total_space(self) -> int:
        """Return total number of second-level slots allocated."""
        return sum(self._bucket_sizes)

    def space_ratio(self) -> float:
        """Return total_space / n. Should be O(1), ideally <= 4."""
        if self.n == 0:
            return 0.0
        return self.total_space() / self.n


# ---------------------------------------------------------------------------
# Minimal Perfect Hash (brute-force for small n)
# ---------------------------------------------------------------------------

class MinimalPerfectHash:
    """Minimal perfect hash: maps n keys bijectively to [0, n-1].

    This is a brute-force approach — try random hash functions until one
    maps all keys to distinct values in [0, n-1]. Only practical for small n
    (say n <= 30), but demonstrates the concept clearly.

    For large n, use algorithms like CHD or BPZ.
    """

    def __init__(self):
        self.n = 0
        self._hash_func = None
        self._keys = set()
        self._mapping = {}  # key -> [0, n-1]
        self.trials = 0

    def build(self, keys: list[str]):
        """Build the minimal perfect hash by trial and error."""
        keys = list(set(keys))
        self.n = len(keys)
        self._keys = set(keys)

        if self.n == 0:
            return

        key_ints = [_string_to_int(k) for k in keys]
        self.trials = 0

        while True:
            self.trials += 1
            h_func, _ = _make_universal_hash(self.n)

            # Check if this hash is a bijection onto [0, n-1]
            seen = set()
            collision = False
            for ki in key_ints:
                val = h_func(ki)
                if val in seen:
                    collision = True
                    break
                seen.add(val)

            if not collision and len(seen) == self.n:
                # Found a bijection
                self._hash_func = h_func
                self._mapping = {k: h_func(ki) for k, ki in zip(keys, key_ints)}
                return

    def lookup(self, key: str) -> int | None:
        """Return the index [0, n-1] for a key, or None if not in set."""
        if key not in self._keys:
            return None
        return self._mapping[key]

    def reverse_lookup(self, idx: int) -> str | None:
        """Given an index, return the key (O(n) — for demonstration only)."""
        for k, v in self._mapping.items():
            if v == idx:
                return k
        return None


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_fks():
    """Demonstrate FKS perfect hashing with Python keywords."""
    print("=" * 70)
    print("FKS PERFECT HASHING — Python Keywords")
    print("=" * 70)

    # Python's reserved keywords as our static set
    keys = sorted(keyword.kwlist)
    n = len(keys)
    print(f"\nStatic key set: {n} Python keywords")
    print(f"Keys: {keys}\n")

    # Build perfect hash
    ph = FKSPerfectHash()
    ph.build(keys)

    # Verify all keys are found
    print("--- Correctness ---")
    all_found = all(ph.lookup(k) for k in keys)
    print(f"All {n} keywords found: {all_found}")

    # Verify non-keys are rejected
    non_keys = ["perfect", "hash", "table", "foo", "bar", "printf", "main"]
    all_rejected = all(not ph.lookup(k) for k in non_keys)
    print(f"All non-keys rejected: {all_rejected}")

    # Space analysis
    print(f"\n--- Space ---")
    print(f"Number of keys (n): {n}")
    print(f"First-level buckets (m): {ph.m}")
    print(f"Total second-level slots: {ph.total_space()}")
    print(f"Space ratio (total/n): {ph.space_ratio():.2f}x")
    print(f"  (should be <= 4.0 for O(n) guarantee)")

    # Second-level trial counts
    print(f"\n--- Construction Effort ---")
    nonzero = [t for t in ph.second_level_trials if t > 0]
    if nonzero:
        print(f"Second-level hash trials per non-empty bucket:")
        print(f"  min: {min(nonzero)}, max: {max(nonzero)}, "
              f"avg: {sum(nonzero)/len(nonzero):.1f}")
        print(f"  (expected ~2 trials per bucket by birthday paradox)")

    # Demonstrate O(1) worst-case: exactly 2 hash lookups, no loops
    print(f"\n--- O(1) Worst-Case Guarantee ---")
    test_key = keys[0]
    print(f"Looking up '{test_key}':")
    print(f"  Step 1: first-level hash -> bucket index (1 hash computation)")
    print(f"  Step 2: second-level hash -> slot index (1 hash computation)")
    print(f"  Step 3: compare stored key with query key (1 comparison)")
    print(f"  Total: exactly 2 hashes + 1 comparison. Always. No chains.")


def demo_minimal():
    """Demonstrate minimal perfect hashing."""
    print("\n" + "=" * 70)
    print("MINIMAL PERFECT HASHING — Bijection to [0, n-1]")
    print("=" * 70)

    keys = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
    n = len(keys)

    mph = MinimalPerfectHash()
    mph.build(keys)

    print(f"\nKeys: {keys}")
    print(f"Trials to find bijective hash: {mph.trials}")
    print(f"\nMapping (each key -> unique index in [0, {n-1}]):")
    for k in sorted(keys):
        print(f"  {k:>8s} -> {mph.lookup(k)}")

    # Verify bijection
    indices = sorted(mph.lookup(k) for k in keys)
    print(f"\nIndices used: {indices}")
    print(f"Is bijection to [0, {n-1}]: {indices == list(range(n))}")


def demo_performance_comparison():
    """Compare lookup performance: perfect hash vs dict vs binary search."""
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON — Static Lookup")
    print("=" * 70)

    import bisect

    # Build static key set — Python keywords
    keys = sorted(keyword.kwlist)
    n = len(keys)

    # Build structures
    ph = FKSPerfectHash()
    ph.build(keys)

    py_dict = {k: True for k in keys}

    sorted_keys = sorted(keys)

    def binary_search_lookup(key):
        idx = bisect.bisect_left(sorted_keys, key)
        return idx < len(sorted_keys) and sorted_keys[idx] == key

    # Test keys: mix of hits and misses
    test_keys = keys + ["notakeyword", "zzz", "aaa", "perfecthash"]
    random.shuffle(test_keys)

    iterations = 100_000

    # Perfect hash
    start = time.perf_counter()
    for _ in range(iterations):
        for k in test_keys:
            ph.lookup(k)
    ph_time = time.perf_counter() - start

    # Python dict
    start = time.perf_counter()
    for _ in range(iterations):
        for k in test_keys:
            k in py_dict
    dict_time = time.perf_counter() - start

    # Binary search
    start = time.perf_counter()
    for _ in range(iterations):
        for k in test_keys:
            binary_search_lookup(k)
    bs_time = time.perf_counter() - start

    total_lookups = iterations * len(test_keys)
    print(f"\n{total_lookups:,} lookups each ({n} static keys, "
          f"{len(test_keys)} test keys x {iterations:,} iterations)")
    print(f"\n  {'Method':<30s} {'Time (s)':>10s} {'ns/lookup':>12s}")
    print(f"  {'-'*52}")
    print(f"  {'FKS Perfect Hash':<30s} {ph_time:>10.3f} "
          f"{ph_time/total_lookups*1e9:>12.1f}")
    print(f"  {'Python dict (in operator)':<30s} {dict_time:>10.3f} "
          f"{dict_time/total_lookups*1e9:>12.1f}")
    print(f"  {'Sorted array + bisect':<30s} {bs_time:>10.3f} "
          f"{bs_time/total_lookups*1e9:>12.1f}")

    print(f"\nNote: Python's built-in dict is heavily optimized in C.")
    print(f"Our FKS implementation is pure Python — the point is the")
    print(f"O(1) worst-case guarantee, not raw speed vs C internals.")
    print(f"In C/C++, perfect hashing beats generic hash tables for")
    print(f"static sets because of better cache behavior and no")
    print(f"collision-resolution overhead.")


if __name__ == "__main__":
    random.seed(42)
    demo_fks()
    demo_minimal()
    demo_performance_comparison()
