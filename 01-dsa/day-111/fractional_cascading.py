"""
Day 111: Fractional Cascading

Query k sorted lists with one value and get its lower_bound in every one of
them, in O(log n + k) instead of O(k log n).

The idea: k independent binary searches each spend log n rediscovering where x
sits in the value space. Pay it once. Every augmented list borrows every
SECOND element of the next list, and each borrowed element carries a pointer
to where it lands there. A search in list 0 therefore lands next to a
precomputed answer for list 1, and so on down the chain.

Chazelle & Guibas, 1986.

Run: python3 fractional_cascading.py
"""

import random


def lower_bound(a, x):
    """First index i with a[i] >= x, else len(a). Written out rather than
    using bisect, because the pointer arrays below are exactly this function
    tabulated ahead of time."""
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2       # Day 106: overflow-safe in C-likes
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def naive_multi_search(lists, x):
    """The O(k log n) baseline: one independent binary search per list."""
    return [lower_bound(L, x) for L in lists]


def merge_sorted(a, b):
    """Standard two-pointer merge. O(len(a) + len(b))."""
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


class FractionalCascade:
    """Query-only structure over k sorted lists.

    Not updatable: the pointers encode global positions, so any insert into
    any list invalidates the whole chain. Rebuild instead.
    """

    def __init__(self, lists):
        for i, L in enumerate(lists):
            if any(L[j] > L[j + 1] for j in range(len(L) - 1)):
                raise ValueError(f"list {i} is not sorted")
        self.lists = [list(L) for L in lists]
        k = len(self.lists)
        self.aug = [[] for _ in range(k)]     # augmented values
        self.own = [[] for _ in range(k)]     # -> index in self.lists[i]
        self.nxt = [[] for _ in range(k)]     # -> index in self.aug[i+1]
        self.last_walk_steps = 0              # instrumentation for the demo

        # Build backwards: A[i] needs A[i+1] to exist first.
        for i in range(k - 1, -1, -1):
            # Every SECOND element. Taking all of them makes each list double
            # the next and blow up exponentially in k; halving makes the total
            # a convergent geometric series, i.e. O(N) space overall.
            promoted = self.aug[i + 1][1::2] if i + 1 < k else []
            self.aug[i] = merge_sorted(self.lists[i], promoted)

            # Both pointer arrays get one extra SENTINEL slot at index
            # len(aug[i]). That is what makes an empty list -- or an x past
            # every element -- a normal code path instead of a special case.
            self.own[i] = ([lower_bound(self.lists[i], v) for v in self.aug[i]]
                           + [len(self.lists[i])])
            if i + 1 < k:
                self.nxt[i] = ([lower_bound(self.aug[i + 1], v)
                                for v in self.aug[i]]
                               + [len(self.aug[i + 1])])
            else:
                self.nxt[i] = [0] * (len(self.aug[i]) + 1)

    def query(self, x):
        """lower_bound(x) in every original list. O(log n + k)."""
        k = len(self.lists)
        self.last_walk_steps = 0
        if k == 0:
            return []
        # The one and only binary search.
        p = lower_bound(self.aug[0], x)
        out = []
        for i in range(k):
            # own[i][p] is the lower bound of aug[i][p], not of x -- but they
            # are the same index. No element of lists[i] can lie in
            # [x, aug[i][p]), or it would itself be an aug[i] entry >= x
            # sitting below p, contradicting p's minimality.
            out.append(self.own[i][p])
            if i + 1 < k:
                q = self.nxt[i][p]
                # The bridge points at the successor of aug[i][p], which is
                # >= x, so it can overshoot. Correct backwards. At most 2
                # elements of aug[i+1] sit between consecutive bridges, so
                # this is O(1) -- the claim the whole bound rests on.
                nxt_vals = self.aug[i + 1]
                while q > 0 and nxt_vals[q - 1] >= x:
                    q -= 1
                    self.last_walk_steps += 1
                p = q
        return out

    def total_size(self):
        """Entries across all augmented lists, vs the raw input size."""
        return sum(len(a) for a in self.aug), sum(len(L) for L in self.lists)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

EXAMPLE = [
    [10, 40],
    [20, 30, 50],
    [25, 60],
]


def demo_structure():
    print("--- Augmented lists and bridges ---")
    fc = FractionalCascade(EXAMPLE)
    for i, L in enumerate(fc.lists):
        print(f"  L{i} = {L}")
    print()
    for i in range(len(fc.aug)):
        promoted = fc.aug[i + 1][1::2] if i + 1 < len(fc.aug) else []
        print(f"  A{i} = {fc.aug[i]}   (borrowed from A{i+1}: {promoted})")
        print(f"       own  = {fc.own[i]}   <- last entry is the sentinel")
        print(f"       next = {fc.nxt[i]}")
    aug_n, raw_n = fc.total_size()
    print(f"  total augmented={aug_n}, raw={raw_n}  (bound is 2*raw={2*raw_n})")


def demo_query():
    print("\n--- Query: cascade vs k independent binary searches ---")
    fc = FractionalCascade(EXAMPLE)
    for x in [5, 20, 25, 41, 60, 99]:
        got = fc.query(x)
        want = naive_multi_search(EXAMPLE, x)
        flag = "OK" if got == want else "MISMATCH"
        print(f"  x={x:3d} -> {got}  naive {want}  "
              f"walk_steps={fc.last_walk_steps}  [{flag}]")


def demo_empty_lists():
    print("\n--- The empty-list bridge case ---")
    # A1 has one element, so A1[1::2] is empty; with L0 empty too, A0 is
    # empty while A1 is not. Without the sentinel this indexes off the end.
    cases = [
        [[], [5], []],
        [[], []],
        [[], [1, 2, 3]],
        [[7], [], [7]],
        [[]],
        [],
    ]
    for lists in cases:
        fc = FractionalCascade(lists)
        sizes = [len(a) for a in fc.aug]
        ok = all(fc.query(x) == naive_multi_search(lists, x)
                 for x in range(-1, 9))
        print(f"  lists={lists}  |A[i]|={sizes}  agrees={ok}")
        assert ok, f"empty-list handling broke on {lists}"


def demo_bridge_walk():
    print("\n--- The backward walk is O(1), measured not asserted ---")
    rng = random.Random(111)
    for k, n in [(4, 50), (8, 200), (16, 400), (32, 800)]:
        lists = [sorted(rng.randrange(4 * n) for _ in range(n))
                 for _ in range(k)]
        fc = FractionalCascade(lists)
        worst = 0
        total = 0
        trials = 200
        for _ in range(trials):
            fc.query(rng.randrange(4 * n))
            worst = max(worst, fc.last_walk_steps)
            total += fc.last_walk_steps
        aug_n, raw_n = fc.total_size()
        print(f"  k={k:3d} n={n:4d}  worst total walk={worst:3d} "
              f"(<= ~2k={2*k:3d})  avg per level={total/(trials*k):.2f}  "
              f"space {aug_n}/{raw_n}")


def demo_probe_counts():
    print("\n--- Comparisons: O(k log n) vs O(log n + k) ---")
    rng = random.Random(1111)
    print("   k    n   naive k*log2(n)   cascade log2(N0)+k")
    for k, n in [(4, 1024), (16, 1024), (64, 1024), (256, 1024)]:
        lists = [sorted(rng.randrange(10 * n) for _ in range(n))
                 for _ in range(k)]
        fc = FractionalCascade(lists)
        naive = k * n.bit_length()
        cascade = len(fc.aug[0]).bit_length() + k
        print(f"  {k:4d} {n:4d}   {naive:12d}   {cascade:12d}")
    print("  the crossover is early: cascading wins as soon as k is more")
    print("  than a small constant, which is the usual geometry case")


def demo_agreement():
    print("\n--- Randomized agreement with k independent binary searches ---")
    rng = random.Random(11111)
    mismatches = 0
    for _ in range(400):
        k = rng.randint(0, 6)
        lists = []
        for _ in range(k):
            n = rng.randint(0, 6)           # 0 exercises the empty case often
            lists.append(sorted(rng.randrange(0, 12) for _ in range(n)))
        fc = FractionalCascade(lists)
        for x in range(-2, 15):
            if fc.query(x) != naive_multi_search(lists, x):
                mismatches += 1
    print(f"  400 random configurations x 17 queries: mismatches={mismatches}")
    assert mismatches == 0, "cascade disagreed with the naive baseline"


def demo():
    demo_structure()
    demo_query()
    demo_empty_lists()
    demo_bridge_walk()
    demo_probe_counts()
    demo_agreement()
    print("\nAll demos consistent with the naive baseline.")


if __name__ == "__main__":
    demo()
