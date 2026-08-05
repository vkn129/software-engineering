"""
Day 109 Practice: van Emde Boas Trees

6 exercises. Implement TODOs, then run: python practice.py

Every exercise here is one piece of the vEB machine, testable on its own.
Exercises 4 and 5 build a ONE-LEVEL vEB by hand -- buckets plus a summary of
non-empty buckets. Real vEB applies that same step recursively, which is where
log log U comes from.

"no such key" is reported as -1, never None: try_or_sol reads a None result as
"the student stub is unimplemented" and silently falls back to the solution.
"""


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
# Exercise 1: next_power_of_two
# ---------------------------------------------------------------------------
# vEB splits lg(u) bits in half, so u must be a power of two or the split
# misaligns. Round the requested universe up. Minimum universe is 2.

def next_power_of_two(n):
    """Smallest power of two >= n, but never less than 2."""
    # TODO: implement
    pass


def _sol_next_power_of_two(n):
    u = 2
    while u < n:
        u <<= 1
    return u


# ---------------------------------------------------------------------------
# Exercise 2: split_key
# ---------------------------------------------------------------------------
# The whole reason vEB dodges the comparison lower bound: a key is taken apart
# by its bits, not compared against another key. high = which cluster,
# low = slot inside it. lower_bits = floor(lg(u) / 2); the summary structure
# gets the ceiling half because there are 2^ceil clusters to describe.

def split_key(u, x):
    """Return (high, low) for key x in a universe of size u."""
    # TODO: implement using shifts and masks, no division
    pass


def _sol_split_key(u, x):
    lower_bits = (u.bit_length() - 1) // 2
    return (x >> lower_bits, x & ((1 << lower_bits) - 1))


# ---------------------------------------------------------------------------
# Exercise 3: cluster_layout
# ---------------------------------------------------------------------------
# Show where every key physically lands -- the picture drawn in the README.

def cluster_layout(u, keys):
    """Return {high: sorted list of lows} for all keys."""
    # TODO: implement
    pass


def _sol_cluster_layout(u, keys):
    lower_bits = (u.bit_length() - 1) // 2
    mask = (1 << lower_bits) - 1
    out = {}
    for k in keys:
        out.setdefault(k >> lower_bits, []).append(k & mask)
    for lows in out.values():
        lows.sort()
    return out


# ---------------------------------------------------------------------------
# Exercise 4: two_level_successor
# ---------------------------------------------------------------------------
# One level of the vEB recursion. Two cases, and only ever two:
#   (a) the answer sits in x's own cluster, above low(x);
#   (b) otherwise it is the min of the next non-empty cluster -- which is the
#       question the summary structure exists to answer.
# Return the successor key, or -1 if there is none.

def two_level_successor(u, keys, x):
    """Smallest key strictly greater than x, or -1."""
    # TODO: implement using the (a)/(b) case split above
    pass


def _sol_two_level_successor(u, keys, x):
    lower_bits = (u.bit_length() - 1) // 2
    buckets = _sol_cluster_layout(u, keys)
    h, l = _sol_split_key(u, x)
    # Case (a): stay inside the cluster x falls in.
    for low in buckets.get(h, []):
        if low > l:
            return (h << lower_bits) | low
    # Case (b): the sorted scan below stands in for the recursive summary
    # query. A real vEB answers it in O(log log sqrt(u)) and then reads the
    # found cluster's cached min in O(1) instead of searching it -- that
    # caching is what keeps the whole operation at one recursive call.
    for hb in sorted(buckets):
        if hb > h:
            return (hb << lower_bits) | buckets[hb][0]
    return -1


# ---------------------------------------------------------------------------
# Exercise 5: two_level_predecessor
# ---------------------------------------------------------------------------
# The mirror image. Note the asymmetry in a real vEB: min is cached outside
# the clusters, so predecessor needs one extra "is the answer just min?" check
# that successor does not.

def two_level_predecessor(u, keys, x):
    """Largest key strictly less than x, or -1."""
    # TODO: implement
    pass


def _sol_two_level_predecessor(u, keys, x):
    lower_bits = (u.bit_length() - 1) // 2
    buckets = _sol_cluster_layout(u, keys)
    h, l = _sol_split_key(u, x)
    for low in reversed(buckets.get(h, [])):
        if low < l:
            return (h << lower_bits) | low
    for hb in sorted(buckets, reverse=True):
        if hb < h:
            return (hb << lower_bits) | buckets[hb][-1]
    return -1


# ---------------------------------------------------------------------------
# Exercise 6: veb_depth
# ---------------------------------------------------------------------------
# Each level halves the *bit width* of the universe, not the key count. That
# is the whole reason the answer is log log U and not log U.

def veb_depth(u):
    """Number of recursion levels for universe u. Base case u == 2 is 1."""
    # TODO: implement
    pass


def _sol_veb_depth(u):
    bits = u.bit_length() - 1
    d = 1
    while bits > 1:
        bits = (bits + 1) // 2      # summary universe takes the ceiling half
        d += 1
    return d


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(label, got, want):
        nonlocal passed, failed
        if got == want:
            print(f"  PASS: {label}")
            passed += 1
        else:
            print(f"  FAIL: {label}")
            print(f"    expected: {want}")
            print(f"    got:      {got}")
            failed += 1

    U = 16
    KEYS = [2, 3, 4, 9, 15]

    print("Exercise 1: next_power_of_two")
    check("n=1 clamps to 2", try_or_sol("next_power_of_two", 1), 2)
    check("n=2 already power", try_or_sol("next_power_of_two", 2), 2)
    check("n=5 -> 8", try_or_sol("next_power_of_two", 5), 8)
    check("n=1000 -> 1024", try_or_sol("next_power_of_two", 1000), 1024)
    check("n=1024 stays", try_or_sol("next_power_of_two", 1024), 1024)

    print("\nExercise 2: split_key")
    # U=16 -> lg=4 -> lower_bits=2 -> 4 clusters of 4 slots each
    check("split 9", try_or_sol("split_key", U, 9), (2, 1))
    check("split 0", try_or_sol("split_key", U, 0), (0, 0))
    check("split 15", try_or_sol("split_key", U, 15), (3, 3))
    check("split 4", try_or_sol("split_key", U, 4), (1, 0))
    # Bigger universe: U=256 -> lg=8 -> lower_bits=4 -> 16 clusters of 16
    check("split 200 in U=256", try_or_sol("split_key", 256, 200), (12, 8))
    # Roundtrip: the decomposition must lose nothing
    h, l = try_or_sol("split_key", U, 13)
    check("roundtrip 13", (h << 2) | l, 13)

    print("\nExercise 3: cluster_layout")
    check("U=16 layout", try_or_sol("cluster_layout", U, KEYS),
          {0: [2, 3], 1: [0], 2: [1], 3: [3]})
    check("empty keys", try_or_sol("cluster_layout", U, []), {})
    check("all in one cluster", try_or_sol("cluster_layout", U, [8, 9, 10]),
          {2: [0, 1, 2]})

    print("\nExercise 4: two_level_successor")
    check("succ(0)=2", try_or_sol("two_level_successor", U, KEYS, 0), 2)
    check("succ(2)=3 same cluster", try_or_sol("two_level_successor", U, KEYS, 2), 3)
    check("succ(3)=4 next cluster", try_or_sol("two_level_successor", U, KEYS, 3), 4)
    check("succ(4)=9 skips empty", try_or_sol("two_level_successor", U, KEYS, 4), 9)
    check("succ(15)=-1", try_or_sol("two_level_successor", U, KEYS, 15), -1)
    check("succ on empty set", try_or_sol("two_level_successor", U, [], 5), -1)

    print("\nExercise 5: two_level_predecessor")
    check("pred(15)=9", try_or_sol("two_level_predecessor", U, KEYS, 15), 9)
    check("pred(4)=3 prev cluster", try_or_sol("two_level_predecessor", U, KEYS, 4), 3)
    check("pred(3)=2 same cluster", try_or_sol("two_level_predecessor", U, KEYS, 3), 2)
    check("pred(2)=-1", try_or_sol("two_level_predecessor", U, KEYS, 2), -1)
    check("pred on empty set", try_or_sol("two_level_predecessor", U, [], 5), -1)

    print("\nExercise 6: veb_depth")
    check("U=2 base case", try_or_sol("veb_depth", 2), 1)
    check("U=4", try_or_sol("veb_depth", 4), 2)
    check("U=16", try_or_sol("veb_depth", 16), 3)
    check("U=256", try_or_sol("veb_depth", 256), 4)
    check("U=2^32 (6 levels vs 32 binary probes)",
          try_or_sol("veb_depth", 1 << 32), 6)
    check("U=2^64", try_or_sol("veb_depth", 1 << 64), 7)

    print("\nCross-check: successor/predecessor agree with a sorted scan")
    # The point of the day is that the bit-decomposition answer is the SAME
    # answer a comparison scan gives -- only the cost model differs.
    ok = True
    for x in range(U):
        want_s = next((v for v in sorted(KEYS) if v > x), -1)
        want_p = next((v for v in sorted(KEYS, reverse=True) if v < x), -1)
        if try_or_sol("two_level_successor", U, KEYS, x) != want_s:
            ok = False
        if try_or_sol("two_level_predecessor", U, KEYS, x) != want_p:
            ok = False
    check("all 16 universe positions agree with brute force", ok, True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
