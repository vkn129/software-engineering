"""
Day 104 Practice: Sorting Networks & Batcher's Bitonic Sort

7 exercises. Implement the TODOs, then run: python3 practice.py

A network is a list of comparators. A comparator (lo, hi) means: after this
step, wire `lo` holds the smaller of the two values and wire `hi` the larger.
Emitting a pair with lo > hi is how a DESCENDING comparator is written.
"""

from itertools import permutations, product


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: run a network
# ---------------------------------------------------------------------------

def apply_network(network, values):
    """
    Run every comparator over a COPY of `values` and return the copy.
    Do not mutate the caller's list.
    """
    # TODO: for each (lo, hi), put the smaller at lo and the larger at hi
    pass


def _sol_apply_network(network, values):
    a = list(values)
    for lo, hi in network:
        if a[lo] > a[hi]:
            a[lo], a[hi] = a[hi], a[lo]
    return a


# ---------------------------------------------------------------------------
# Exercise 2: depth
# ---------------------------------------------------------------------------

def network_depth(network, n):
    """
    Number of PARALLEL layers. Two comparators share a layer only if they touch
    no common wire.

    Depth, not size, is the latency of a hardware or SIMD implementation — you
    can always buy more comparators, but you cannot buy fewer dependent steps.
    """
    # TODO: track the earliest layer at which each wire becomes free
    pass


def _sol_network_depth(network, n):
    ready = [0] * n
    deepest = 0
    for lo, hi in network:
        layer = max(ready[lo], ready[hi])
        ready[lo] = ready[hi] = layer + 1
        deepest = max(deepest, layer + 1)
    return deepest


# ---------------------------------------------------------------------------
# Exercise 3: the 0-1 principle
# ---------------------------------------------------------------------------

def is_sorting_network(network, n):
    """
    Return True iff this network sorts EVERY input of n elements.

    Check only the 2^n binary inputs. That is sound because a comparator
    network commutes with every monotone function, so any counter-example can
    be thresholded down into a 0/1 counter-example.
    """
    # TODO: iterate over all 2^n bit vectors
    pass


def _sol_is_sorting_network(network, n):
    for bits in product((0, 1), repeat=n):
        out = _sol_apply_network(network, bits)
        if any(out[i] > out[i + 1] for i in range(n - 1)):
            return False
    return True


def _brute_is_sorting_network(network, n):
    """The O(n!) version, used only to confirm the 0-1 principle agrees."""
    for perm in permutations(range(n)):
        if _sol_apply_network(network, perm) != sorted(perm):
            return False
    return True


# ---------------------------------------------------------------------------
# Exercise 4: bitonic merge
# ---------------------------------------------------------------------------

def bitonic_merge_network(n):
    """
    Comparators that sort any BITONIC sequence of length n (n a power of 2).

    A bitonic sequence rises then falls, or is a rotation of one. The merge is
    log n rounds; the round with stride j compares every wire i against i ^ j.

    Return the comparator list. This is NOT a general sorting network — it is
    correct only on bitonic input, and the tests check both halves of that
    claim.
    """
    # TODO: strides n/2, n/4, ..., 1; within a stride, pair i with i ^ j
    pass


def _sol_bitonic_merge_network(n):
    net = []
    j = n >> 1
    while j > 0:
        for i in range(n):
            partner = i ^ j
            # `partner > i` emits each pair exactly once; without it every
            # comparator would be added twice, costing time and nothing else.
            if partner > i:
                net.append((i, partner))
        j >>= 1
    return net


# ---------------------------------------------------------------------------
# Exercise 5: the full bitonic network
# ---------------------------------------------------------------------------

def bitonic_network(n):
    """
    Batcher's bitonic sorting network on n wires (n a power of 2).

    Outer loop k = 2, 4, ..., n is the block size being made monotone. Inner
    loop j = k/2, k/4, ..., 1 is the stride. A block is ASCENDING when
    `i & k == 0` and descending otherwise; express a descending comparator by
    emitting the pair reversed.

    Expected shape: size  = (n/2) * log n * (log n + 1) / 2
                    depth =         log n * (log n + 1) / 2
    """
    # TODO: two nested loops over k and j, direction taken from the `i & k` bit
    pass


def _sol_bitonic_network(n):
    net = []
    k = 2
    while k <= n:
        j = k >> 1
        while j > 0:
            for i in range(n):
                partner = i ^ j
                if partner > i:
                    if (i & k) == 0:
                        net.append((i, partner))
                    else:
                        net.append((partner, i))
            j >>= 1
        k <<= 1
    return net


# ---------------------------------------------------------------------------
# Exercise 6: sorting real data with padding
# ---------------------------------------------------------------------------

class _Top:
    """Compares greater than everything. The padding sentinel."""
    __slots__ = ()

    def __lt__(self, other):
        return False

    def __gt__(self, other):
        return not isinstance(other, _Top)

    def __le__(self, other):
        return isinstance(other, _Top)

    def __ge__(self, other):
        return True


TOP = _Top()


def bitonic_sort(values):
    """
    Sort a list of any length with a bitonic network. Return a NEW list.

    Pad up to the next power of two with `TOP`, run the network, then drop the
    padding from the tail. Padding with `max(values)` would be a bug — with
    duplicates you cannot tell the padding apart from real data afterwards.
    """
    # TODO: pad to a power of two, apply, truncate back to len(values)
    pass


def _sol_bitonic_sort(values):
    n = len(values)
    if n < 2:
        return list(values)
    width = 1
    while width < n:
        width <<= 1
    padded = list(values) + [TOP] * (width - n)
    return _sol_apply_network(_sol_bitonic_network(width), padded)[:n]


# ---------------------------------------------------------------------------
# Exercise 7: the depth baseline
# ---------------------------------------------------------------------------

def transposition_network(n):
    """
    Odd-even transposition: n phases of adjacent compare-exchanges, alternating
    between starting at wire 0 and wire 1. Works for ANY n, not just powers of
    two, and provably sorts in exactly n phases.

    Depth n, size ~ n^2/2 — the yardstick bitonic's O(log^2 n) is measured
    against.
    """
    # TODO: for each phase, pair up (i, i+1) starting at phase % 2
    pass


def _sol_transposition_network(n):
    net = []
    for phase in range(n):
        for i in range(phase % 2, n - 1, 2):
            net.append((i, i + 1))
    return net


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: apply_network")
    check("single ascending comparator",
          try_or_sol("apply_network", [(0, 1)], [5, 2]), [2, 5])
    check("already ordered is untouched",
          try_or_sol("apply_network", [(0, 1)], [2, 5]), [2, 5])
    # A reversed pair puts the LARGER value first: a descending comparator.
    check("reversed pair sorts descending",
          try_or_sol("apply_network", [(1, 0)], [2, 5]), [5, 2])
    check("non-adjacent wires",
          try_or_sol("apply_network", [(0, 3)], [9, 1, 2, 0]), [0, 1, 2, 9])
    src = [3, 1]
    try_or_sol("apply_network", [(0, 1)], src)
    check("caller's list not mutated", src, [3, 1])
    check("empty network is the identity",
          try_or_sol("apply_network", [], [3, 1, 2]), [3, 1, 2])

    print("\nExercise 2: network_depth")
    check("disjoint comparators share a layer",
          try_or_sol("network_depth", [(0, 1), (2, 3)], 4), 1)
    check("a shared wire forces a new layer",
          try_or_sol("network_depth", [(0, 1), (1, 2)], 3), 2)
    check("empty network has depth 0",
          try_or_sol("network_depth", [], 4), 0)
    check("chain of 3 comparators is depth 3",
          try_or_sol("network_depth", [(0, 1), (1, 2), (2, 3)], 4), 3)
    check("transposition depth equals n",
          try_or_sol("network_depth", _sol_transposition_network(6), 6), 6)

    print("\nExercise 3: is_sorting_network")
    check("bitonic n=4 sorts everything",
          try_or_sol("is_sorting_network", _sol_bitonic_network(4), 4), True)
    check("bitonic n=8 sorts everything",
          try_or_sol("is_sorting_network", _sol_bitonic_network(8), 8), True)
    check("empty network on 2 wires does not sort",
          try_or_sol("is_sorting_network", [], 2), False)
    check("one comparator DOES sort 2 wires",
          try_or_sol("is_sorting_network", [(0, 1)], 2), True)
    # Two of the three comparators n=3 needs: catches an off-by-one network.
    check("incomplete 3-wire network rejected",
          try_or_sol("is_sorting_network", [(0, 1), (1, 2)], 3), False)
    # The whole point of the 0-1 principle: it must agree with the n! check.
    check("0-1 principle agrees with permutations (good network)",
          try_or_sol("is_sorting_network", _sol_bitonic_network(4), 4),
          _brute_is_sorting_network(_sol_bitonic_network(4), 4))
    broken = [c for c in _sol_bitonic_network(4) if c != (0, 1)]
    check("0-1 principle agrees with permutations (broken network)",
          try_or_sol("is_sorting_network", broken, 4),
          _brute_is_sorting_network(broken, 4))

    print("\nExercise 4: bitonic_merge_network")
    merge8 = try_or_sol("bitonic_merge_network", 8)
    check("size = (n/2) * log n", len(merge8), 12)
    check("depth = log n", _sol_network_depth(merge8, 8), 3)
    # Rises then falls -> bitonic.
    check("sorts an up-then-down sequence",
          _sol_apply_network(merge8, [1, 3, 5, 7, 6, 4, 2, 0]),
          [0, 1, 2, 3, 4, 5, 6, 7])
    # Falls then rises is a rotation of a bitonic sequence -> also handled.
    check("sorts a down-then-up sequence",
          _sol_apply_network(merge8, [7, 5, 3, 1, 0, 2, 4, 6]),
          [0, 1, 2, 3, 4, 5, 6, 7])
    check("sorts an already-ascending sequence",
          _sol_apply_network(merge8, [0, 1, 2, 3, 4, 5, 6, 7]),
          [0, 1, 2, 3, 4, 5, 6, 7])
    # The precondition is real: a merge network is NOT a sorting network.
    check("not a general sorting network",
          _sol_is_sorting_network(merge8, 8), False)

    print("\nExercise 5: bitonic_network")
    check("n=2 is one comparator", try_or_sol("bitonic_network", 2), [(0, 1)])
    n4 = try_or_sol("bitonic_network", 4)
    check("n=4 size", len(n4), 6)
    check("n=4 depth", _sol_network_depth(n4, 4), 3)
    check("n=4 sorts everything", _sol_is_sorting_network(n4, 4), True)
    n8 = try_or_sol("bitonic_network", 8)
    check("n=8 size", len(n8), 24)
    check("n=8 depth = log n (log n + 1) / 2", _sol_network_depth(n8, 8), 6)
    check("n=8 sorts everything", _sol_is_sorting_network(n8, 8), True)
    n16 = try_or_sol("bitonic_network", 16)
    check("n=16 size", len(n16), 80)
    check("n=16 depth", _sol_network_depth(n16, 16), 10)
    # Descending blocks must exist, or the merges point the wrong way.
    check("some comparator is emitted reversed",
          any(lo > hi for lo, hi in n8), True)
    # Obliviousness: the schedule is a function of n alone.
    check("schedule identical across two calls",
          try_or_sol("bitonic_network", 8), n8)

    print("\nExercise 6: bitonic_sort")
    check("empty", try_or_sol("bitonic_sort", []), [])
    check("single", try_or_sol("bitonic_sort", [42]), [42])
    check("power of two",
          try_or_sol("bitonic_sort", [3, 1, 4, 1, 5, 9, 2, 6]),
          [1, 1, 2, 3, 4, 5, 6, 9])
    check("n=5 needs padding to 8",
          try_or_sol("bitonic_sort", [10, 9, 8, 7, 6]), [6, 7, 8, 9, 10])
    check("n=13 needs padding to 16",
          try_or_sol("bitonic_sort", list(range(13, 0, -1))), list(range(1, 14)))
    check("heavy duplicates survive padding",
          try_or_sol("bitonic_sort", [5, 5, 1, 1, 9, 9, 1]),
          [1, 1, 1, 5, 5, 9, 9])
    check("already sorted", try_or_sol("bitonic_sort", [1, 2, 3]), [1, 2, 3])
    src = [3, 1, 2]
    try_or_sol("bitonic_sort", src)
    check("input not mutated", src, [3, 1, 2])
    check("negatives and zero",
          try_or_sol("bitonic_sort", [0, -5, 3, -1, 0]), [-5, -1, 0, 0, 3])

    print("\nExercise 7: transposition_network")
    check("n=1 is empty", try_or_sol("transposition_network", 1), [])
    check("n=2 is one comparator", try_or_sol("transposition_network", 2), [(0, 1)])
    check("n=4 size", len(try_or_sol("transposition_network", 4)), 6)
    for n in (2, 3, 4, 5, 6, 7):
        net = try_or_sol("transposition_network", n)
        check(f"n={n} sorts everything", _sol_is_sorting_network(net, n), True)
    # Odd n is exactly what bitonic cannot do, which is why this network exists.
    check("depth equals n for odd n",
          _sol_network_depth(try_or_sol("transposition_network", 5), 5), 5)
    check("only adjacent wires are used",
          all(hi - lo == 1 for lo, hi in try_or_sol("transposition_network", 7)),
          True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
