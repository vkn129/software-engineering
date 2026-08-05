"""
Day 104: Sorting Networks & Batcher's Bitonic Sort

A sorting network is a sorting algorithm with the `if` statements removed.

The comparator sequence is fixed BEFORE any data is seen. Same wires, same
order, same count — for a sorted input, a reversed input, or noise. That is what
"data-oblivious" means, and it is the entire point: an algorithm whose control
flow does not depend on its data can be laid out in silicon, unrolled onto SIMD
lanes, run in lockstep across GPU threads, or applied to a secret key without
leaking it through a timing channel.

Nothing here re-teaches a comparison sort — days 99-103 own those. Today the
object of study is the *fixed comparator sequence itself*: how many comparators
it needs, how deep it is, and how you prove one is correct.

Standard library only.
"""

from itertools import permutations, product


# ---------------------------------------------------------------------------
# 1. Comparators
# ---------------------------------------------------------------------------
#
# A comparator is a pair (lo, hi) of wire indices meaning:
#
#     after this step, wire `lo` holds the smaller value
#                      wire `hi` holds the larger
#
# There is no branch on the DATA in any meaningful sense: a hardware comparator
# is two multiplexers driven by one comparison, and it executes whether or not a
# swap occurs. The branch-free software form is `lo, hi = min(x, y), max(x, y)`.

def apply_comparator(a, lo, hi):
    """One compare-exchange, in place."""
    if a[lo] > a[hi]:
        a[lo], a[hi] = a[hi], a[lo]


def apply_network(network, values):
    """Run a whole network over a copy of `values`. Returns the copy."""
    a = list(values)
    for lo, hi in network:
        apply_comparator(a, lo, hi)
    return a


# ---------------------------------------------------------------------------
# 2. Depth — the number that actually matters
# ---------------------------------------------------------------------------

def layers(network, n):
    """
    Partition the comparators into parallel layers.

    Two comparators may share a layer iff they touch no common wire — sharing a
    wire is the only dependency a network has. Greedy earliest-placement is
    optimal here because a comparator's earliest possible layer is fully
    determined by when its two wires last became free.
    """
    ready = [0] * n           # earliest layer at which each wire is free
    out = []
    for lo, hi in network:
        layer = max(ready[lo], ready[hi])
        while len(out) <= layer:
            out.append([])
        out[layer].append((lo, hi))
        ready[lo] = ready[hi] = layer + 1
    return out


def depth(network, n):
    """Parallel step count. With unlimited comparators, this is the latency."""
    return len(layers(network, n))


def size(network):
    """Total comparator count. With a single comparator, this is the latency."""
    return len(network)


# ---------------------------------------------------------------------------
# 3. Verification — the 0-1 principle
# ---------------------------------------------------------------------------

def is_sorting_network(network, n):
    """
    Does this network sort EVERY input of n elements?

    By the **0-1 principle** it suffices to check the 2^n binary inputs. The
    argument: a comparator network commutes with any monotone function f — that
    is, running the network on f(x) gives f(run(x)), because min and max both
    commute with monotone f. So if some input x comes out unsorted at positions
    i < j, pick the threshold function `f(v) = 0 if v < out[i] else 1`. It is
    monotone, and it converts that counter-example into a BINARY
    counter-example.

    Hence: sorts all 0/1 inputs  <=>  sorts everything.

    That is 2^n cases instead of n!. For n = 16: 65,536 instead of
    20,922,789,888,000.
    """
    for bits in product((0, 1), repeat=n):
        out = apply_network(network, bits)
        if any(out[i] > out[i + 1] for i in range(n - 1)):
            return False
    return True


def is_sorting_network_by_permutations(network, n):
    """
    The naive O(n!) check, kept only so the 0-1 principle has something to be
    measured against. Do not use it past n = 8.
    """
    for perm in permutations(range(n)):
        out = apply_network(network, perm)
        if out != sorted(perm):
            return False
    return True


def failing_binary_input(network, n):
    """Return the first 0/1 input this network fails to sort, or None."""
    for bits in product((0, 1), repeat=n):
        out = apply_network(network, bits)
        if any(out[i] > out[i + 1] for i in range(n - 1)):
            return bits
    return None


# ---------------------------------------------------------------------------
# 4. Batcher's bitonic sort
# ---------------------------------------------------------------------------
#
# A **bitonic** sequence rises then falls, or is a rotation of one:
#   1 4 7 6 2  is bitonic;  1 4 2 5 3  is not.
#
# Batcher's insight (1968): a bitonic sequence of length n can be sorted in
# log n parallel layers. Take the half-length compare-exchange
#
#     for i in 0 .. n/2-1:   compare_exchange(a[i], a[i + n/2])
#
# Afterwards every element of the low half is <= every element of the high half,
# AND each half is itself bitonic. Recurse on the halves independently — they
# never interact again, which is exactly why the whole thing parallelises.
#
# Build a full sort from that: sort the first half ascending and the second half
# descending (their concatenation is then bitonic by construction), and bitonic-
# merge the result. log n merges, each of depth log n, so:
#
#     depth = 1 + 2 + ... + log n = log n (log n + 1) / 2  =  O(log^2 n)
#     size  = (n/2) * depth                                =  O(n log^2 n)


def is_power_of_two(n):
    return n > 0 and (n & (n - 1)) == 0


def bitonic_network(n):
    """
    Comparators for Batcher's bitonic sort on n wires. n must be a power of 2.

    The direction of each comparator is decided by a single bit of the wire
    index — `i & k` — which is precisely why the whole schedule can be computed
    without ever referring to the data.
    """
    if not is_power_of_two(n):
        raise ValueError(f"bitonic sort needs a power-of-two width, got {n}")
    net = []
    k = 2
    while k <= n:
        j = k >> 1
        while j > 0:
            for i in range(n):
                partner = i ^ j
                if partner > i:
                    # `i & k == 0` selects the ascending blocks. Emitting the
                    # pair reversed is how a DESCENDING block is expressed
                    # without needing a second kind of comparator at all.
                    if (i & k) == 0:
                        net.append((i, partner))
                    else:
                        net.append((partner, i))
            j >>= 1
        k <<= 1
    return net


def bitonic_merge_network(n):
    """Only the final stage: sort an already-bitonic sequence of length n."""
    if not is_power_of_two(n):
        raise ValueError(f"needs a power-of-two width, got {n}")
    net = []
    j = n >> 1
    while j > 0:
        for i in range(n):
            partner = i ^ j
            if partner > i:
                net.append((i, partner))
        j >>= 1
    return net


# ---------------------------------------------------------------------------
# 5. A depth baseline: the odd-even transposition network
# ---------------------------------------------------------------------------

def transposition_network(n):
    """
    n phases of alternating adjacent compare-exchanges. Provably sorts in n
    phases, so depth = n and size ~ n^2/2.

    Kept purely as the depth yardstick: O(n) depth against bitonic's
    O(log^2 n). Adjacent-only comparators are all a systolic array or a linear
    chain of hardware can wire up, which is why this shape still appears in real
    silicon despite the terrible asymptotics.
    """
    net = []
    for phase in range(n):
        for i in range(phase % 2, n - 1, 2):
            net.append((i, i + 1))
    return net


# ---------------------------------------------------------------------------
# 6. Using a network on real data
# ---------------------------------------------------------------------------

class _Top:
    """
    A value comparing greater than everything, used to pad a list up to a power
    of two. Padding with `max(values)` would be wrong: with duplicates, the
    padding becomes indistinguishable from real data on the way out.
    """
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
    Sort any list with a bitonic network, padding up to a power of two.

    Padding is the price of the fixed structure: 4097 items need a network built
    for 8192 wires. That is nearly 2x wasted work in the worst case, and it is a
    large part of why nobody uses a sorting network as a general-purpose sort.
    """
    n = len(values)
    if n < 2:
        return list(values)
    width = 1
    while width < n:
        width <<= 1
    padded = list(values) + [TOP] * (width - n)
    out = apply_network(bitonic_network(width), padded)
    return out[:n]


def comparator_trace(network, values):
    """
    Return the sequence of (lo, hi) wire pairs actually touched.

    For a sorting network this is IDENTICAL to `network` for every input — the
    first demo makes that concrete. For a data-dependent sort it would not be,
    and that difference is the timing side channel.
    """
    a = list(values)
    trace = []
    for lo, hi in network:
        trace.append((lo, hi))
        apply_comparator(a, lo, hi)
    return trace


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_oblivious():
    print("=" * 60)
    print("DEMO 1: the schedule does not depend on the data")
    print("=" * 60)
    net = bitonic_network(8)
    inputs = [
        [1, 2, 3, 4, 5, 6, 7, 8],
        [8, 7, 6, 5, 4, 3, 2, 1],
        [5, 5, 5, 5, 5, 5, 5, 5],
        [3, 1, 4, 1, 5, 9, 2, 6],
    ]
    traces = [comparator_trace(net, x) for x in inputs]
    print(f"\n  network size = {size(net)} comparators, depth = {depth(net, 8)}")
    for x, t in zip(inputs, traces):
        print(f"  {str(x):<26} -> {apply_network(net, x)}   ops={len(t)}")
    same = all(t == traces[0] for t in traces)
    print(f"\n  every trace identical: {same}")
    print("  A quicksort's comparison count varies with its input. This does not.")
    print("  That is what makes it constant-time and mappable onto hardware.")


def demo_structure():
    print("\n" + "=" * 60)
    print("DEMO 2: the layers of an 8-wire bitonic network")
    print("=" * 60)
    net = bitonic_network(8)
    for i, layer in enumerate(layers(net, 8)):
        print(f"  layer {i}: {layer}")
    print(f"\n  depth {depth(net, 8)} = 3*(3+1)/2 for n=8 (log n = 3)")
    print(f"  size  {size(net)} = (8/2) * 6")


def demo_zero_one_principle():
    print("\n" + "=" * 60)
    print("DEMO 3: the 0-1 principle — how you PROVE a network is correct")
    print("=" * 60)
    for n in (4, 8):
        net = bitonic_network(n)
        by_bits = is_sorting_network(net, n)
        by_perms = is_sorting_network_by_permutations(net, n)
        fact = 1
        for k in range(2, n + 1):
            fact *= k
        print(f"\n  n={n}: 0-1 check says {by_bits}, permutation check says {by_perms}")
        print(f"        cases: 2^{n} = {2**n}   vs   {n}! = {fact}")

    # A network that is ALMOST right, to show the check has teeth.
    broken = [c for c in bitonic_network(8) if c != (0, 1)]
    print("\n  drop one comparator from the 8-wire network:")
    print(f"    is_sorting_network -> {is_sorting_network(broken, 8)}")
    print(f"    first failing 0/1 input -> {failing_binary_input(broken, 8)}")


def demo_depth_growth():
    print("\n" + "=" * 60)
    print("DEMO 4: O(log^2 n) depth vs O(n) depth")
    print("=" * 60)
    print(f"\n  {'n':>5} | {'bitonic size':>12} {'depth':>6} | "
          f"{'transposition size':>18} {'depth':>6}")
    print("  " + "-" * 60)
    for n in (2, 4, 8, 16, 32, 64):
        b = bitonic_network(n)
        t = transposition_network(n)
        print(f"  {n:>5} | {size(b):>12} {depth(b, n):>6} | "
              f"{size(t):>18} {depth(t, n):>6}")
    print("\n  Both are valid sorting networks. Bitonic uses MORE comparators at")
    print("  small n and far fewer parallel steps as n grows — and depth is the")
    print("  currency once you have a comparator per wire pair in hardware.")


def demo_real_data():
    print("\n" + "=" * 60)
    print("DEMO 5: sorting real values, including non-powers of two")
    print("=" * 60)
    cases = [
        [3, 1, 4, 1, 5, 9, 2, 6],
        [42],
        [],
        [2, 1],
        [10, 9, 8, 7, 6],                 # n=5 -> padded to 8
        [5, 5, 1, 1, 9, 9, 1],            # n=7, heavy duplicates
        list(range(13, 0, -1)),           # n=13 -> padded to 16
    ]
    for c in cases:
        out = bitonic_sort(c)
        ok = out == sorted(c)
        print(f"  n={len(c):>2}  {'OK' if ok else 'FAIL'}  {out}")

    print("\n  padding overhead:")
    for n in (5, 9, 17, 33):
        width = 1
        while width < n:
            width <<= 1
        print(f"    n={n:>3} -> {width:>3} wires "
              f"({size(bitonic_network(width))} comparators for {n} real items)")


def demo_transposition_is_correct():
    print("\n" + "=" * 60)
    print("DEMO 6: verifying the baseline network too")
    print("=" * 60)
    for n in (2, 3, 4, 5, 6, 7, 8):
        net = transposition_network(n)
        print(f"  n={n}: sorts everything = {is_sorting_network(net, n)}   "
              f"(size {size(net)}, depth {depth(net, n)})")
    print("\n  n=3,5,6,7 work here but bitonic_network() refuses them —")
    print("  transposition needs no power-of-two width.")


if __name__ == "__main__":
    demo_oblivious()
    demo_structure()
    demo_zero_one_principle()
    demo_depth_growth()
    demo_real_data()
    demo_transposition_is_correct()
