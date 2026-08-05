"""
Day 109: van Emde Boas Trees

O(log log U) insert / delete / member / successor / predecessor on integer
keys drawn from the bounded universe {0, 1, ..., U-1}.

Why this is allowed to beat Omega(log n): we never compare two keys. We split
a key's bits -- high half selects a cluster, low half selects a slot inside it
-- which is arithmetic on the key, not a comparison. The comparison lower
bound simply does not apply, the same way it does not apply to radix sort.

Clusters are allocated lazily (a dict, not a fixed array). The textbook layout
is Theta(U) space whether you store 3 keys or 3 billion; lazily we pay
O(n log log U) and keep every time bound. See README for x-fast / y-fast
tries, which get all the way down to O(n).

Run: python3 van_emde_boas.py
"""

import random


def next_power_of_two(n):
    """Smallest power of two >= max(n, 2).

    The bit split needs sqrt(U) to be an integer, so U must be a power of two.
    Rounding up is free here because unused clusters are never allocated.
    """
    u = 2
    while u < n:
        u <<= 1
    return u


class VEB:
    """A van Emde Boas tree over the universe {0, ..., u-1}.

    Set semantics: inserting a key twice is a no-op, deleting an absent key
    is a no-op. u must be a power of two and at least 2.
    """

    def __init__(self, u):
        if u < 2 or (u & (u - 1)) != 0:
            raise ValueError(f"universe must be a power of two >= 2, got {u}")
        self.u = u
        # min and max live in the node itself. min is deliberately NOT stored
        # in any cluster -- that is what buys the single recursive call.
        self.min = None
        self.max = None
        if u > 2:
            # lg(u) bits split as floor/ceil. The *summary* gets the ceiling
            # half because there are 2^ceil clusters to describe.
            lg = u.bit_length() - 1
            self.lower_bits = lg // 2
            self.lower_sqrt = 1 << self.lower_bits      # keys per cluster
            self.upper_sqrt = u >> self.lower_bits      # number of clusters
            self.summary = None                          # built on first need
            self.clusters = {}                           # lazy: index -> VEB

    # -- bit decomposition -------------------------------------------------

    def _high(self, x):
        return x >> self.lower_bits

    def _low(self, x):
        return x & (self.lower_sqrt - 1)

    def _index(self, h, l):
        return (h << self.lower_bits) | l

    def _get_cluster(self, h, create=False):
        c = self.clusters.get(h)
        if c is None and create:
            c = VEB(self.lower_sqrt)
            self.clusters[h] = c
        return c

    def _get_summary(self, create=False):
        if self.summary is None and create:
            self.summary = VEB(self.upper_sqrt)
        return self.summary

    # -- queries -----------------------------------------------------------

    def minimum(self):
        """O(1): the smallest key, cached in the node. No recursion at all."""
        return self.min

    def maximum(self):
        """O(1): the largest key."""
        return self.max

    def member(self, x):
        """True if x is stored. O(log log u)."""
        if self.min is None or x < 0 or x >= self.u:
            return False
        if x == self.min or x == self.max:
            return True
        if self.u == 2:
            return False
        c = self.clusters.get(self._high(x))
        return c is not None and c.member(self._low(x))

    def successor(self, x):
        """Smallest stored key strictly greater than x, or None.

        Exactly one recursive call on a universe of size sqrt(u), so
        T(u) = T(sqrt(u)) + O(1) = O(log log u).
        """
        if self.u == 2:
            # Base case: the node IS the answer, no children exist.
            if self.min is not None and x < self.min:
                return self.min
            if self.max is not None and x < self.max:
                return self.max
            return None
        if self.min is not None and x < self.min:
            # min is not in any cluster, so it can only be found here.
            return self.min
        h, l = self._high(x), self._low(x)
        c = self.clusters.get(h)
        if c is not None and c.max is not None and l < c.max:
            # Answer is inside this cluster. One recursive call, then stop.
            return self._index(h, c.successor(l))
        if self.summary is None:
            return None
        succ_cluster = self.summary.successor(h)
        if succ_cluster is None:
            return None
        # O(1) because the found cluster caches its own min -- this is the
        # step that would otherwise cost a second recursive call.
        return self._index(succ_cluster, self.clusters[succ_cluster].min)

    def predecessor(self, x):
        """Largest stored key strictly less than x, or None. O(log log u)."""
        if self.u == 2:
            if self.max is not None and x > self.max:
                return self.max
            if self.min is not None and x > self.min:
                return self.min
            return None
        if self.max is not None and x > self.max:
            return self.max
        h, l = self._high(x), self._low(x)
        c = self.clusters.get(h)
        if c is not None and c.min is not None and l > c.min:
            return self._index(h, c.predecessor(l))
        pred_cluster = self.summary.predecessor(h) if self.summary else None
        if pred_cluster is None:
            # No cluster below: the only remaining candidate is min, which is
            # stored outside the clusters and would otherwise be missed.
            if self.min is not None and x > self.min:
                return self.min
            return None
        return self._index(pred_cluster, self.clusters[pred_cluster].max)

    # -- updates -----------------------------------------------------------

    def insert(self, x):
        """Insert x. O(log log u). Returns True if the set changed."""
        if x < 0 or x >= self.u:
            raise ValueError(f"key {x} outside universe [0, {self.u})")
        if self.member(x):
            return False
        self._insert(x)
        return True

    def _insert(self, x):
        if self.min is None:
            self.min = self.max = x
            return
        if x < self.min:
            # Evict the old min downward: min never lives in a cluster, so the
            # value being displaced is the one that must be pushed down.
            x, self.min = self.min, x
        if self.u > 2:
            h, l = self._high(x), self._low(x)
            c = self._get_cluster(h, create=True)
            if c.min is None:
                # Inserting into an EMPTY cluster is O(1) -- just set its
                # min/max. Only then do we touch the summary. That keeps the
                # whole insert at one real recursive call.
                self._get_summary(create=True)._insert(h)
                c.min = c.max = l
            else:
                c._insert(l)
        if x > self.max:
            self.max = x

    def delete(self, x):
        """Delete x. O(log log u). Returns True if the set changed.

        The membership check is not decoration: the recursive body below
        assumes x is present and will corrupt min/max if it is not.
        """
        if not self.member(x):
            return False
        self._delete(x)
        return True

    def _delete(self, x):
        if self.min == self.max:
            self.min = self.max = None
            return
        if self.u == 2:
            # Two possible keys, one of them is leaving; the other becomes
            # both min and max.
            self.min = 1 if x == 0 else 0
            self.max = self.min
            return
        if x == self.min:
            # min is not stored below, so there is nothing to remove from a
            # cluster yet. Promote the next smallest key into the min slot and
            # delete *that* key from its cluster instead.
            first = self.summary.min
            x = self._index(first, self.clusters[first].min)
            self.min = x
        h, l = self._high(x), self._low(x)
        c = self.clusters[h]
        c._delete(l)
        if c.min is None:
            del self.clusters[h]            # lazy layout: drop the empty child
            self.summary._delete(h)
            if x == self.max:
                summary_max = self.summary.max
                if summary_max is None:
                    self.max = self.min     # only min is left
                else:
                    self.max = self._index(summary_max,
                                           self.clusters[summary_max].max)
        elif x == self.max:
            self.max = self._index(h, c.max)

    # -- iteration and introspection ---------------------------------------

    def keys(self):
        """Ascending iteration by repeated successor. O(n log log u)."""
        x = self.min
        while x is not None:
            yield x
            x = self.successor(x)

    def node_count(self):
        """Allocated VEB nodes. Shows what lazy clusters save vs Theta(U)."""
        n = 1
        if self.u > 2:
            if self.summary is not None:
                n += self.summary.node_count()
            for c in self.clusters.values():
                n += c.node_count()
        return n


def theoretical_depth(u):
    """Levels a vEB of universe u needs. Equals ceil(log2 log2 u) + 1.

    Each level halves the *bit width*, so the count is logarithmic in lg(u),
    which is where the second log comes from.
    """
    bits = u.bit_length() - 1
    d = 1
    while bits > 1:
        bits = (bits + 1) // 2      # summary takes the ceiling half
        d += 1
    return d


# ---------------------------------------------------------------------------
# Reference oracle: a plain sorted list. Slow, obviously correct.
# ---------------------------------------------------------------------------

class SortedListOracle:
    def __init__(self):
        self.items = []

    def insert(self, x):
        if x in self.items:
            return False
        self.items.append(x)
        self.items.sort()
        return True

    def delete(self, x):
        if x not in self.items:
            return False
        self.items.remove(x)
        return True

    def member(self, x):
        return x in self.items

    def successor(self, x):
        for v in self.items:
            if v > x:
                return v
        return None

    def predecessor(self, x):
        best = None
        for v in self.items:
            if v < x:
                best = v
        return best


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_structure():
    print("--- Structure: U=16, keys {2,3,4,9,15} ---")
    t = VEB(16)
    for k in [2, 3, 4, 9, 15]:
        t.insert(k)
    print(f"  min={t.minimum()}  max={t.maximum()}  sqrt(U)={t.lower_sqrt}")
    print(f"  summary holds cluster ids: {sorted(t.summary.keys())}")
    for h in sorted(t.clusters):
        lows = sorted(t.clusters[h].keys())
        actual = [t._index(h, l) for l in lows]
        print(f"  cluster[{h}] lows={lows} -> keys {actual}")
    print("  note: min=2 appears in NO cluster -- that is the log log trick")


def demo_successor():
    print("\n--- successor / predecessor vs sorted-list oracle ---")
    t, o = VEB(64), SortedListOracle()
    for k in [3, 5, 17, 18, 40, 63]:
        t.insert(k)
        o.insert(k)
    for x in [0, 3, 4, 17, 39, 62, 63]:
        s_v, s_o = t.successor(x), o.successor(x)
        p_v, p_o = t.predecessor(x), o.predecessor(x)
        ok = "OK" if (s_v == s_o and p_v == p_o) else "MISMATCH"
        print(f"  x={x:2d}  succ={str(s_v):>4s}  pred={str(p_v):>4s}  [{ok}]")


def demo_depth():
    print("\n--- Depth is log log U, not log n ---")
    print("  universe U                levels   binary probes over U keys")
    for bits in [1, 2, 4, 8, 16, 32, 64]:
        u = 1 << bits
        print(f"  2^{bits:<2d} = {u:<20d} {theoretical_depth(u):<8d} {bits}")
    print("  a vEB over 2^64 keys answers successor in 7 levels; binary")
    print("  search over the same sorted keys needs 64 probes")


def demo_space():
    print("\n--- Lazy clusters vs textbook Theta(U) ---")
    u = 1 << 16
    for n in [1, 10, 100, 1000]:
        t = VEB(u)
        rng = random.Random(n)
        for _ in range(n):
            t.insert(rng.randrange(u))
        print(f"  n={n:<5d} allocated nodes={t.node_count():<7d} "
              f"textbook would allocate ~{u}")
    print("  space tracks n, not U. y-fast tries push this to a true O(n).")


def demo_randomized_agreement():
    print("\n--- Randomized agreement with the oracle (1500 ops) ---")
    u = 1 << 8
    t, o = VEB(u), SortedListOracle()
    rng = random.Random(109)
    mismatches = 0
    for _ in range(1500):
        x = rng.randrange(u)
        op = rng.random()
        if op < 0.45:
            if t.insert(x) != o.insert(x):
                mismatches += 1
        elif op < 0.70:
            if t.delete(x) != o.delete(x):
                mismatches += 1
        else:
            if (t.member(x) != o.member(x)
                    or t.successor(x) != o.successor(x)
                    or t.predecessor(x) != o.predecessor(x)):
                mismatches += 1
    if list(t.keys()) != o.items:
        mismatches += 1
    print(f"  final size={len(o.items)}  mismatches={mismatches}")
    assert mismatches == 0, "vEB disagreed with the sorted-list oracle"


def demo():
    demo_structure()
    demo_successor()
    demo_depth()
    demo_space()
    demo_randomized_agreement()
    print("\nAll demos consistent with the oracle.")


if __name__ == "__main__":
    demo()
