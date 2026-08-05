"""
Day 158: Skip List Revisited — Redis-style with span pointers

This skip list supports:
- insert / delete / contains (O(log n) expected)
- rank(x): position of x (1-indexed)
- by_rank(k): element at rank k
- range_by_score(lo, hi): all elements with score in [lo, hi]

The span trick (carrying the L0-distance covered by each forward pointer)
is exactly how Redis implements ZSET.
"""

import random
import time
import bisect


MAX_LEVEL = 32
P = 0.5


class SkipNode:
    __slots__ = ("score", "value", "forward", "span")

    def __init__(self, score, value, level):
        self.score = score
        self.value = value
        # forward[i] = next node at level i
        self.forward = [None] * (level + 1)
        # span[i] = number of L0 steps that forward[i] hops over
        self.span = [0] * (level + 1)


class SkipList:
    """Redis-style sorted set keyed by (score, value)."""

    def __init__(self):
        # Header is a sentinel — score doesn't matter, never read
        self.header = SkipNode(score=float("-inf"), value=None, level=MAX_LEVEL)
        self.level = 0  # current highest level in use
        self.length = 0

    @staticmethod
    def _random_level():
        lvl = 0
        while random.random() < P and lvl < MAX_LEVEL:
            lvl += 1
        return lvl

    @staticmethod
    def _lt(a_score, a_val, b_score, b_val):
        """Lexicographic on (score, value)."""
        if a_score != b_score:
            return a_score < b_score
        return a_val < b_val

    def insert(self, score, value):
        update = [None] * (MAX_LEVEL + 1)
        rank = [0] * (MAX_LEVEL + 1)
        x = self.header
        for i in range(self.level, -1, -1):
            rank[i] = 0 if i == self.level else rank[i + 1]
            while (x.forward[i] is not None
                   and self._lt(x.forward[i].score, x.forward[i].value, score, value)):
                rank[i] += x.span[i]
                x = x.forward[i]
            update[i] = x

        lvl = self._random_level()
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                rank[i] = 0
                update[i] = self.header
                update[i].span[i] = self.length
            self.level = lvl

        node = SkipNode(score, value, lvl)
        for i in range(lvl + 1):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node
            # Span fixups
            node.span[i] = update[i].span[i] - (rank[0] - rank[i])
            update[i].span[i] = (rank[0] - rank[i]) + 1

        # Levels above lvl: just extend span by 1 (this insert is "in" their hop)
        for i in range(lvl + 1, self.level + 1):
            update[i].span[i] += 1

        self.length += 1

    def contains(self, score, value):
        x = self.header
        for i in range(self.level, -1, -1):
            while (x.forward[i] is not None
                   and self._lt(x.forward[i].score, x.forward[i].value, score, value)):
                x = x.forward[i]
        x = x.forward[0]
        return x is not None and x.score == score and x.value == value

    def rank(self, score, value):
        """1-indexed rank of (score, value). 0 if absent."""
        r = 0
        x = self.header
        for i in range(self.level, -1, -1):
            while (x.forward[i] is not None
                   and (self._lt(x.forward[i].score, x.forward[i].value, score, value)
                        or (x.forward[i].score == score and x.forward[i].value == value))):
                r += x.span[i]
                x = x.forward[i]
                if x.score == score and x.value == value:
                    return r
        return 0

    def by_rank(self, k):
        """1-indexed."""
        if k < 1 or k > self.length:
            return None
        traversed = 0
        x = self.header
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and traversed + x.span[i] <= k:
                traversed += x.span[i]
                x = x.forward[i]
                if traversed == k:
                    return (x.score, x.value)
        return None

    def range_by_score(self, lo, hi):
        out = []
        x = self.header
        for i in range(self.level, -1, -1):
            while x.forward[i] is not None and x.forward[i].score < lo:
                x = x.forward[i]
        x = x.forward[0]
        while x is not None and x.score <= hi:
            out.append((x.score, x.value))
            x = x.forward[0]
        return out

    def delete(self, score, value):
        update = [None] * (MAX_LEVEL + 1)
        x = self.header
        for i in range(self.level, -1, -1):
            while (x.forward[i] is not None
                   and self._lt(x.forward[i].score, x.forward[i].value, score, value)):
                x = x.forward[i]
            update[i] = x

        target = x.forward[0]
        if target is None or target.score != score or target.value != value:
            return False

        for i in range(self.level + 1):
            if update[i].forward[i] == target:
                update[i].span[i] += target.span[i] - 1
                update[i].forward[i] = target.forward[i]
            else:
                update[i].span[i] -= 1

        while self.level > 0 and self.header.forward[self.level] is None:
            self.level -= 1

        self.length -= 1
        return True

    def __len__(self):
        return self.length


# ---------------------------------------------------------------------------
# Reference: sorted list as a balanced-tree proxy (logarithmic ops)
# ---------------------------------------------------------------------------

class BalancedTreeProxy:
    """
    Uses bisect on a Python list — strictly speaking O(n) insert because
    of array shifts, BUT comparisons are O(log n) and the constant factor
    is dominated by memmove. Good baseline for "structured order" cost.
    """
    def __init__(self):
        self.data = []

    def insert(self, key):
        bisect.insort(self.data, key)

    def contains(self, key):
        i = bisect.bisect_left(self.data, key)
        return i < len(self.data) and self.data[i] == key

    def range(self, lo, hi):
        l = bisect.bisect_left(self.data, (lo,))
        r = bisect.bisect_right(self.data, (hi, float("inf")))
        return self.data[l:r]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Skip list with span pointers")
    print("=" * 60)
    sl = SkipList()
    pairs = [(3.0, "carol"), (1.0, "alice"), (4.0, "dave"),
             (1.5, "amy"), (2.0, "bob"), (5.0, "eve")]
    for s, v in pairs:
        sl.insert(s, v)

    print(f"\n  Inserted {len(sl)} elements")
    print(f"  rank('bob',2.0)   = {sl.rank(2.0, 'bob')}     (expected 3)")
    print(f"  by_rank(1)        = {sl.by_rank(1)}")
    print(f"  by_rank(4)        = {sl.by_rank(4)}")
    print(f"  range_by_score(1.5, 4.0) = {sl.range_by_score(1.5, 4.0)}")

    sl.delete(2.0, "bob")
    print(f"\n  After delete bob:")
    print(f"  contains bob?     = {sl.contains(2.0, 'bob')}")
    print(f"  length            = {len(sl)}")


def demo_perf():
    print("\n" + "=" * 60)
    print("DEMO 2: Skip list vs sorted-array proxy (balanced-tree analog)")
    print("=" * 60)
    n = 20000
    random.seed(0)
    items = [(random.random() * 1000, f"v{i}") for i in range(n)]

    sl = SkipList()
    t0 = time.perf_counter()
    for s, v in items:
        sl.insert(s, v)
    t_insert_sl = time.perf_counter() - t0

    bt = BalancedTreeProxy()
    t0 = time.perf_counter()
    for s, v in items:
        bt.insert((s, v))
    t_insert_bt = time.perf_counter() - t0

    # Lookups
    t0 = time.perf_counter()
    for s, v in items[:5000]:
        sl.contains(s, v)
    t_lookup_sl = time.perf_counter() - t0

    t0 = time.perf_counter()
    for s, v in items[:5000]:
        bt.contains((s, v))
    t_lookup_bt = time.perf_counter() - t0

    # Range
    t0 = time.perf_counter()
    for _ in range(1000):
        sl.range_by_score(100, 300)
    t_range_sl = time.perf_counter() - t0

    t0 = time.perf_counter()
    for _ in range(1000):
        bt.range(100, 300)
    t_range_bt = time.perf_counter() - t0

    print(f"\n  n={n}")
    print(f"                    Skip list      Sorted-array proxy")
    print(f"  {n} inserts:    {t_insert_sl:8.3f}s     {t_insert_bt:8.3f}s")
    print(f"  5000 lookups:    {t_lookup_sl:8.3f}s     {t_lookup_bt:8.3f}s")
    print(f"  1000 ranges:     {t_range_sl:8.3f}s     {t_range_bt:8.3f}s")
    print("\n  Same big-O. The point is correctness + simplicity — skip lists are")
    print("  ~100 lines without rebalancing logic.")


def demo_level_distribution():
    print("\n" + "=" * 60)
    print("DEMO 3: Level distribution matches geometric law")
    print("=" * 60)
    random.seed(42)
    n = 10000
    sl = SkipList()
    for i in range(n):
        sl.insert(random.random(), f"v{i}")

    # Count nodes by max level
    counts = [0] * (MAX_LEVEL + 1)
    x = sl.header.forward[0]
    while x:
        max_lvl = len(x.forward) - 1
        counts[max_lvl] += 1
        x = x.forward[0]

    print(f"\n  n={n}, p={P}")
    print(f"  Level | Count    | Expected (n * p^L * (1-p))")
    for L in range(8):
        expected = int(n * (P ** L) * (1 - P))
        print(f"   {L:4d} | {counts[L]:8d} | {expected:8d}")
    print(f"  Highest level reached: {sl.level}")


if __name__ == "__main__":
    demo_basic()
    demo_perf()
    demo_level_distribution()
