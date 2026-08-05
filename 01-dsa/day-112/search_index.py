"""
Day 112: Mini-Project -- Searchable Sorted Index

One immutable index over integer keys, four interchangeable search backends,
and a measured comparison that says which to use.

Backends re-implement days 106 / 108 / 109 / 110 rather than importing across
day directories -- each day stands alone, same as day-168's kv_store.py.

Measurement rule: PROBE COUNTS are the metric. They are exact, deterministic
integers. Wall-clock is printed for context and never asserted, because in
Python it measures the interpreter, not the algorithm.

Run: python3 search_index.py
"""

import random
import time

ABSENT = -1             # "no such key" -- never None, so callers cannot
                        # confuse it with an unimplemented stub


# ---------------------------------------------------------------------------
# Backends. Each answers lower_bound(key) and counts its own probes.
# ---------------------------------------------------------------------------

class BinaryBackend:
    """Day 106. No preconditions; worst case equals average case."""

    name = "binary"

    def __init__(self, keys):
        self.keys = keys

    def lower_bound(self, x):
        """(index of first key >= x, probes)."""
        lo, hi, probes = 0, len(self.keys), 0
        while lo < hi:
            mid = lo + (hi - lo) // 2       # overflow-safe in fixed-width ints
            probes += 1
            if self.keys[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        return lo, probes


class InterpolationBackend:
    """Day 108, with the two guards that make it safe to ship.

    Guard 1: bail out when a[lo] == a[hi], or the probe divides by zero.
    Guard 2: clamp the probe to [lo, hi-1]. Clamping to [lo, hi] instead lets
    a probe land on hi, leave the window unchanged and spin forever -- the
    exact defect found in day-108's practice.py. The iteration cap below is a
    belt-and-braces bound on skewed data, NOT the fix for that hang; a cap
    would have turned an infinite loop into a slow loop and hidden the bug.
    """

    name = "interp"

    def __init__(self, keys, max_iters=8):
        self.keys = keys
        self.max_iters = max_iters

    def lower_bound(self, x):
        a = self.keys
        n = len(a)
        probes = 0
        if n == 0:
            return 0, probes
        # Settle the out-of-range cases first. That establishes
        # a[lo] < x <= a[hi], which is what lets the window below be trusted.
        probes += 1
        if x <= a[0]:
            return 0, probes
        probes += 1
        if x > a[n - 1]:
            return n, probes
        lo, hi = 0, n - 1
        iters = 0
        while hi - lo > 4 and iters < self.max_iters:
            if a[hi] == a[lo]:
                break                       # zero denominator, nothing to gain
            pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
            pos = max(lo, min(hi - 1, pos))  # hi-1, not hi: guarantees shrink
            probes += 1
            if a[pos] < x:
                lo = pos + 1                # every index <= pos is < x
            else:
                hi = pos                    # a[pos] >= x
            iters += 1
        # Invariant held by both branches above: the answer is inside [lo, hi].
        # Binary search only THAT window -- searching [lo, n) instead would
        # throw away the interpolation work and cost a full log n every time.
        w_lo, w_hi = lo, hi + 1
        while w_lo < w_hi:
            mid = w_lo + (w_hi - w_lo) // 2
            probes += 1
            if a[mid] < x:
                w_lo = mid + 1
            else:
                w_hi = mid
        return w_lo, probes


class VEBBackend:
    """Day 109. Cost tracks the universe, not the key count.

    Keys are shifted by a build-time offset so the tree only ever sees
    non-negative values -- vEB has no representation for a negative key, and
    the right layer to fix that is the caller, not the data structure.
    """

    name = "veb"

    def __init__(self, keys):
        self.keys = keys
        self.offset = -keys[0] if keys and keys[0] < 0 else 0
        span = (keys[-1] + self.offset + 1) if keys else 1
        self.u = _next_power_of_two(span)
        self.tree = _VEB(self.u)
        for k in keys:
            self.tree.insert(k + self.offset)
        self.rank = {k: i for i, k in enumerate(keys)}

    def lower_bound(self, x):
        n = len(self.keys)
        if n == 0:
            return 0, 0
        shifted = x + self.offset
        if shifted < 0:
            return 0, 1                     # below the universe: before all
        if shifted >= self.u:
            return n, 1                     # above the universe: after all
        probes = [0]
        if self.tree.member(shifted, probes):
            return self.rank[x], probes[0]
        s = self.tree.successor(shifted, probes)
        return (n if s is None else self.rank[s - self.offset]), probes[0]


class GridBackend:
    """Day 110, applied where it is deliberately the wrong tool.

    A sorted array reshaped row-major into a grid is row+column sorted, so the
    staircase is valid -- it is just wasteful, because reshaping discards the
    total order we already had. O(sqrt n) is the price of that discard.
    The tail row is padded with a sentinel above every real key so the column
    ordering survives a row count that does not divide n.
    """

    name = "grid"

    def __init__(self, keys):
        self.keys = keys
        n = len(keys)
        self.cols = max(1, int(n ** 0.5))
        self.rows = (n + self.cols - 1) // self.cols
        pad = self.rows * self.cols - n
        sentinel = (keys[-1] + 1) if keys else 0
        padded = list(keys) + [sentinel] * pad
        self.grid = [padded[r * self.cols:(r + 1) * self.cols]
                     for r in range(self.rows)]

    def lower_bound(self, x):
        n = len(self.keys)
        if n == 0:
            return 0, 0
        # Staircase from the bottom-left counting cells strictly below x:
        # that count IS the lower-bound index in the flattened order.
        r, c, probes, below = self.rows - 1, 0, 0, 0
        while r >= 0 and c < self.cols:
            probes += 1
            if self.grid[r][c] < x:
                below += r + 1
                c += 1
            else:
                r -= 1
        return min(below, n), probes


# ---------------------------------------------------------------------------
# Minimal vEB, lifted from Day 109 and instrumented with a probe counter.
# ---------------------------------------------------------------------------

def _next_power_of_two(n):
    u = 2
    while u < n:
        u <<= 1
    return u


class _VEB:
    def __init__(self, u):
        self.u = u
        self.min = None
        self.max = None
        if u > 2:
            lg = u.bit_length() - 1
            self.lower_bits = lg // 2
            self.lower_sqrt = 1 << self.lower_bits
            self.upper_sqrt = u >> self.lower_bits
            self.summary = None
            self.clusters = {}

    def _high(self, x):
        return x >> self.lower_bits

    def _low(self, x):
        return x & (self.lower_sqrt - 1)

    def _index(self, h, l):
        return (h << self.lower_bits) | l

    def insert(self, x):
        if self.min is None:
            self.min = self.max = x
            return
        if x == self.min:
            return
        if x < self.min:
            x, self.min = self.min, x       # min never lives in a cluster
        if self.u > 2:
            h, l = self._high(x), self._low(x)
            c = self.clusters.get(h)
            if c is None:
                c = self.clusters[h] = _VEB(self.lower_sqrt)
            if c.min is None:
                if self.summary is None:
                    self.summary = _VEB(self.upper_sqrt)
                self.summary.insert(h)
                c.min = c.max = l           # empty-cluster insert is O(1)
            else:
                c.insert(l)
        if x > self.max:
            self.max = x

    def member(self, x, probes):
        probes[0] += 1
        if self.min is None or x < 0 or x >= self.u:
            return False
        if x == self.min or x == self.max:
            return True
        if self.u == 2:
            return False
        c = self.clusters.get(self._high(x))
        return c is not None and c.member(self._low(x), probes)

    def successor(self, x, probes):
        probes[0] += 1
        if self.u == 2:
            if self.min is not None and x < self.min:
                return self.min
            if self.max is not None and x < self.max:
                return self.max
            return None
        if self.min is not None and x < self.min:
            return self.min
        h, l = self._high(x), self._low(x)
        c = self.clusters.get(h)
        if c is not None and c.max is not None and l < c.max:
            return self._index(h, c.successor(l, probes))
        if self.summary is None:
            return None
        sc = self.summary.successor(h, probes)
        if sc is None:
            return None
        return self._index(sc, self.clusters[sc].min)


# ---------------------------------------------------------------------------
# The index
# ---------------------------------------------------------------------------

class SortedIndex:
    """Immutable index over integer keys. Any write invalidates it -- rebuild.

    That is not a shortcut: every technique in days 106-111 is a build-time
    trade, which is exactly why real read-optimised stores use immutable runs
    plus background compaction.
    """

    BACKENDS = ("binary", "interp", "veb", "grid")

    def __init__(self, keys):
        self.keys = sorted(set(keys))       # dedup: positions are unambiguous
        self.backends = {
            "binary": BinaryBackend(self.keys),
            "interp": InterpolationBackend(self.keys),
            "veb": VEBBackend(self.keys),
            "grid": GridBackend(self.keys),
        }
        self.last_probes = 0

    def __len__(self):
        return len(self.keys)

    def _lb(self, x, backend):
        idx, probes = self.backends[backend].lower_bound(x)
        self.last_probes = probes
        return idx

    def lookup(self, x, backend="binary"):
        """Index of x, or ABSENT."""
        i = self._lb(x, backend)
        if i < len(self.keys) and self.keys[i] == x:
            return i
        return ABSENT

    def contains(self, x, backend="binary"):
        return self.lookup(x, backend) != ABSENT

    def successor(self, x, backend="binary"):
        """Smallest key strictly greater than x, or ABSENT."""
        i = self._lb(x + 1, backend)
        return self.keys[i] if i < len(self.keys) else ABSENT

    def predecessor(self, x, backend="binary"):
        """Largest key strictly less than x, or ABSENT."""
        i = self._lb(x, backend)
        return self.keys[i - 1] if i > 0 else ABSENT

    def range_query(self, lo, hi, backend="binary"):
        """All keys in the inclusive range [lo, hi]."""
        i = self._lb(lo, backend)
        out = []
        while i < len(self.keys) and self.keys[i] <= hi:
            out.append(self.keys[i])
            i += 1
        return out


# ---------------------------------------------------------------------------
# Sharded index: Day 111 against k independent binary searches
# ---------------------------------------------------------------------------

def _lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


class ShardedIndex:
    """k sorted shards; one query wants its position in every one of them."""

    def __init__(self, shards):
        self.shards = [sorted(set(s)) for s in shards]
        k = len(self.shards)
        self.aug = [[] for _ in range(k)]
        self.own = [[] for _ in range(k)]
        self.nxt = [[] for _ in range(k)]
        for i in range(k - 1, -1, -1):
            promoted = self.aug[i + 1][1::2] if i + 1 < k else []
            self.aug[i] = sorted(self.shards[i] + promoted)
            # Sentinel slot at index len(aug[i]) -- what makes an empty shard
            # an ordinary code path instead of an IndexError (Day 111).
            self.own[i] = ([_lower_bound(self.shards[i], v)
                            for v in self.aug[i]] + [len(self.shards[i])])
            self.nxt[i] = ([_lower_bound(self.aug[i + 1], v)
                            for v in self.aug[i]] + [len(self.aug[i + 1])]
                           if i + 1 < k else [0] * (len(self.aug[i]) + 1))

    def naive_positions(self, x):
        """O(k log n): k independent binary searches."""
        return [_lower_bound(s, x) for s in self.shards]

    def cascade_positions(self, x):
        """O(log n + k): one binary search, then constant-time hops."""
        k = len(self.shards)
        if k == 0:
            return []
        p = _lower_bound(self.aug[0], x)
        out = []
        for i in range(k):
            out.append(self.own[i][p])
            if i + 1 < k:
                q = self.nxt[i][p]
                while q > 0 and self.aug[i + 1][q - 1] >= x:
                    q -= 1              # correct the bridge overshoot, O(1)
                p = q
        return out


# ---------------------------------------------------------------------------
# Measurement
# ---------------------------------------------------------------------------

def uniform_keys(n, rng):
    """Interpolation's best case: keys spread evenly over their range."""
    return sorted(rng.sample(range(n * 10), n))


def clustered_keys(n, rng):
    """Interpolation's worst case: a dense clump plus one far outlier."""
    return sorted([rng.randrange(1000) for _ in range(n - 1)] + [10 ** 9])


def compare_backends(keys, queries, label):
    """Average probes per lookup for each backend. Correctness checked too."""
    idx = SortedIndex(keys)
    positions = {k: i for i, k in enumerate(idx.keys)}
    print(f"\n  {label}: n={len(idx)}")
    print(f"    {'backend':10s} {'avg probes':>11s}  {'ms':>7s}")
    for name in SortedIndex.BACKENDS:
        total = 0
        t0 = time.perf_counter()
        for q in queries:
            got = idx.lookup(q, backend=name)
            total += idx.last_probes
            want = positions.get(q, ABSENT)
            assert got == want, f"{name} wrong on {q}: {got} != {want}"
        ms = (time.perf_counter() - t0) * 1000
        # ms is printed for context only. Nothing asserts it -- see README.
        print(f"    {name:10s} {total / len(queries):11.2f}  {ms:7.1f}")


def demo_backend_comparison():
    print("--- Backends: probes per lookup (asserted) and ms (context only) ---")
    rng = random.Random(112)
    for n in [1000, 10000]:
        keys = uniform_keys(n, rng)
        queries = [rng.choice(keys) for _ in range(200)]
        compare_backends(keys, queries, "uniform keys")
    keys = clustered_keys(5000, rng)
    queries = [rng.choice(keys) for _ in range(200)]
    compare_backends(keys, queries, "clustered keys + outlier")
    print("\n  binary is flat and unconditional; interp wins on uniform and")
    print("  loses on clustered; veb tracks the universe not n; grid is")
    print("  O(sqrt n) because reshaping threw the total order away")


def demo_veb_flat_in_n():
    print("\n--- vEB probes: flat in n, growing in the universe ---")
    rng = random.Random(1122)
    print("    n        max key      avg veb probes   avg binary probes")
    for n in [100, 1000, 10000]:
        keys = sorted(rng.sample(range(1 << 20), n))
        idx = SortedIndex(keys)
        vt = bt = 0
        qs = [rng.choice(keys) for _ in range(100)]
        for q in qs:
            idx.lookup(q, backend="veb")
            vt += idx.last_probes
            idx.lookup(q, backend="binary")
            bt += idx.last_probes
        print(f"    {n:<8d} {keys[-1]:<12d} {vt/len(qs):14.2f}"
              f"   {bt/len(qs):17.2f}")
    print("    binary grows with n; veb does not")


def demo_sharded():
    print("\n--- Sharded reads: k binary searches vs fractional cascading ---")
    rng = random.Random(11222)
    print("    k     naive k*log2(n)   cascade log2(N0)+k")
    for k in [2, 8, 32, 128]:
        shards = [sorted(rng.sample(range(100000), 200)) for _ in range(k)]
        si = ShardedIndex(shards)
        naive = k * (200).bit_length()
        cascade = len(si.aug[0]).bit_length() + k
        for _ in range(50):
            x = rng.randrange(100000)
            assert si.cascade_positions(x) == si.naive_positions(x)
        print(f"    {k:<5d} {naive:15d}   {cascade:15d}")
    print("    crossover is early -- cascading wins past a small constant k")


def demo_edge_cases():
    print("\n--- Edge cases every backend must survive ---")
    cases = [
        ("empty", []),
        ("single", [42]),
        ("all identical (dedups to 1)", [7] * 200),
        ("all negative", list(range(-500, -400))),
        ("spans zero", list(range(-50, 50))),
        ("huge gaps", [0, 10 ** 6, 10 ** 9]),
    ]
    for label, keys in cases:
        idx = SortedIndex(keys)
        positions = {k: i for i, k in enumerate(idx.keys)}
        probes = [-2, -1, 0, 1, 7, 42, -450, 10 ** 6, 10 ** 9, 10 ** 12]
        ok = True
        for name in SortedIndex.BACKENDS:
            for q in probes:
                if idx.lookup(q, backend=name) != positions.get(q, ABSENT):
                    ok = False
        # successor / predecessor / range against a brute-force oracle
        for q in probes:
            s = next((v for v in idx.keys if v > q), ABSENT)
            p = next((v for v in reversed(idx.keys) if v < q), ABSENT)
            if idx.successor(q) != s or idx.predecessor(q) != p:
                ok = False
        if idx.range_query(-1000, 1000) != [v for v in idx.keys
                                            if -1000 <= v <= 1000]:
            ok = False
        print(f"    {label:30s} n={len(idx):<4d} all backends agree: {ok}")
        assert ok, f"edge case failed: {label}"

    # Grid padding: n rarely divides evenly into rows x cols.
    ragged_ok = True
    for n in range(0, 41):
        idx = SortedIndex(list(range(0, 2 * n, 2)))
        positions = {k: i for i, k in enumerate(idx.keys)}
        for q in range(-1, 2 * n + 2):
            if idx.lookup(q, backend="grid") != positions.get(q, ABSENT):
                ragged_ok = False
    print(f"    {'grid tail padding, n = 0..40':30s} correct: {ragged_ok}")
    assert ragged_ok

    # Cascading with empty shards in every position.
    empty_ok = True
    for shards in ([[], [1, 2], [3]], [[1], [], [3]], [[1], [2], []],
                   [[], [], []], [], [[]]):
        si = ShardedIndex(shards)
        for x in range(-1, 6):
            if si.cascade_positions(x) != si.naive_positions(x):
                empty_ok = False
    print(f"    {'empty shards in any position':30s} correct: {empty_ok}")
    assert empty_ok


def demo_randomized_agreement():
    print("\n--- Randomized agreement across all backends ---")
    rng = random.Random(1112)
    mismatches = 0
    for _ in range(300):
        n = rng.randint(0, 60)
        keys = [rng.randint(-30, 90) for _ in range(n)]
        idx = SortedIndex(keys)
        positions = {k: i for i, k in enumerate(idx.keys)}
        for q in range(-32, 95):
            want = positions.get(q, ABSENT)
            for name in SortedIndex.BACKENDS:
                if idx.lookup(q, backend=name) != want:
                    mismatches += 1
    print(f"    300 random key sets x 127 queries x 4 backends: "
          f"mismatches={mismatches}")
    assert mismatches == 0, "a backend disagreed with the oracle"


def demo():
    demo_backend_comparison()
    demo_veb_flat_in_n()
    demo_sharded()
    demo_edge_cases()
    demo_randomized_agreement()
    print("\nAll backends agree. Probe counts asserted, timings only printed.")


if __name__ == "__main__":
    demo()
