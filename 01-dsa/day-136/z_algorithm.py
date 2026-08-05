"""
Day 136: Z-Algorithm — From Scratch

Z[i] = length of the longest substring starting at i that matches a prefix.
Build in O(n) using the Z-box trick. Equivalent power to KMP's failure
function, different mental model.
"""

import time


# ---------------------------------------------------------------------------
# 1. Z-Array Construction
# ---------------------------------------------------------------------------

def z_array(s):
    """
    Build the Z-array in O(n).

    Invariant: [l, r] is the rightmost-ending interval [i, i+Z[i]-1]
    known so far. For positions inside the box, copy from earlier work.
    """
    n = len(s)
    if n == 0:
        return []
    z = [0] * n
    z[0] = n  # convention; whole string matches its own prefix
    l = r = 0
    for i in range(1, n):
        if i <= r:
            # Inside the Z-box: bound by min(remaining-in-box, mirrored Z)
            z[i] = min(r - i + 1, z[i - l])
        # Try to extend
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        # Update box if we found a further-right match
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z


# ---------------------------------------------------------------------------
# 2. Pattern Matching via Z (with sentinel)
# ---------------------------------------------------------------------------

def z_search(text, pattern, sentinel="\x01"):
    """
    Find pattern in text using Z-array of (pattern + sentinel + text).
    Sentinel MUST not appear in either string.
    Returns list of start positions in `text`.
    """
    if not pattern:
        return list(range(len(text) + 1))
    if sentinel in pattern or sentinel in text:
        raise ValueError("sentinel collides with input")

    combined = pattern + sentinel + text
    z = z_array(combined)
    m = len(pattern)
    offset = m + 1  # skip pattern and sentinel
    matches = []
    for i in range(offset, len(combined)):
        if z[i] >= m:
            matches.append(i - offset)
    return matches


# ---------------------------------------------------------------------------
# 3. Convert Z-Array to KMP Failure Function
# ---------------------------------------------------------------------------

def z_to_failure(z):
    """
    Convert Z-array to KMP failure function. O(n).
    For each i, the Z-box at i contributes to fail[i + z[i] - 1].
    """
    n = len(z)
    fail = [0] * n
    for i in range(1, n):
        if z[i] == 0:
            continue
        # The match at position i tells us: pattern[0..z[i]-1] is a suffix
        # ending at index i + z[i] - 1.
        end = i + z[i] - 1
        # We want the LONGEST such match for each end position.
        # Process i in increasing order; the first writer wins for "shortest i"
        # which corresponds to the LONGEST overlap from earlier in the string.
        if fail[end] == 0:
            fail[end] = z[i]
        # But the actual KMP failure value at index end is the maximum prefix
        # that equals a suffix. We may need to take a max over contributors.
        else:
            fail[end] = max(fail[end], z[i])
    return fail


# ---------------------------------------------------------------------------
# 4. Tandem Repeat Detection
# ---------------------------------------------------------------------------

def find_tandem_repeats(s, min_period=2):
    """
    Find positions where s[i:] starts with at least 2 copies of some period p.
    A tandem repeat at i with period p means s[i:i+2p] consists of two
    identical halves.

    Uses Z-array: if Z[i+p] >= p, then s[i:i+p] == s[i+p:i+2p].
    Returns list of (position, period) pairs.
    """
    n = len(s)
    z = z_array(s)
    results = []
    for i in range(n):
        for p in range(min_period, (n - i) // 2 + 1):
            # check if s[i:i+p] == s[i+p:i+2p] using Z
            # Need Z value of suffix starting at i+p (in shifted context).
            # Trick: compute Z on s[i:] for each i — too slow. Instead, this
            # demo uses direct comparison; for production use suffix arrays.
            if s[i:i + p] == s[i + p:i + 2 * p]:
                results.append((i, p))
                break  # only smallest period at each position
    return results


# ---------------------------------------------------------------------------
# 5. Distinct Substrings via Z (O(n^2) but instructive)
# ---------------------------------------------------------------------------

def count_distinct_substrings_z(s):
    """
    Count distinct substrings using Z-array of each suffix.
    Demonstrates Z's relation to suffix structure.
    Inefficient O(n^2); the proper tool is suffix array + LCP (Day 138).
    """
    n = len(s)
    total = 0
    for start in range(n):
        suf = s[start:]
        z = z_array(suf)
        # Suffix `suf` contributes (len(suf) - max(z[1:] union {0})) new
        # substrings beyond what shorter suffixes contribute.
        # Simpler conceptually: every starting position generates len-prefix
        # substrings minus overlap with earlier suffixes.
        max_overlap = max(z[1:], default=0)
        total += len(suf) - max_overlap
    return total


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_z_array():
    print("=" * 65)
    print("DEMO 1: Z-Array Construction")
    print("=" * 65)
    for s in ["aabcaabxaaaz", "aaaa", "abcdef", "abababab", "abacabad"]:
        print(f"  {s!r:14s} z = {z_array(s)}")


def demo_search():
    print("\n" + "=" * 65)
    print("DEMO 2: Pattern Matching via Z")
    print("=" * 65)
    print(f"  search 'abcabcabc' for 'abc' -> {z_search('abcabcabc', 'abc')}")
    print(f"  search 'aaaa' for 'aa' (overlap) -> {z_search('aaaa', 'aa')}")
    print(f"  search 'hello world' for 'xyz' -> {z_search('hello world', 'xyz')}")


def demo_z_vs_kmp():
    print("\n" + "=" * 65)
    print("DEMO 3: Z-Array vs Naive (Catastrophic Case)")
    print("=" * 65)
    s = "a" * 50000 + "b"
    p = "a" * 100 + "b"
    combined = p + "\x01" + s

    t0 = time.perf_counter()
    z_search(s, p)
    z_t = time.perf_counter() - t0

    print(f"  text: a^50000+b, pattern: a^100+b")
    print(f"  z-algorithm: {z_t:.4f}s")
    print(f"  (matches KMP in linear-time guarantee)")


def demo_conversion():
    print("\n" + "=" * 65)
    print("DEMO 4: Z-Array <-> KMP Failure Function")
    print("=" * 65)
    for p in ["ababaca", "aabaabaaa", "abcabd"]:
        z = z_array(p)
        f = z_to_failure(z)
        print(f"  pattern: {p!r:14s} z = {z}")
        print(f"                       fail = {f}")


def demo_tandem():
    print("\n" + "=" * 65)
    print("DEMO 5: Tandem Repeat Detection")
    print("=" * 65)
    for s in ["abcabcxyz", "aaaa", "abcabcabcdef"]:
        repeats = find_tandem_repeats(s)
        print(f"  {s!r:14s} tandem (pos, period): {repeats[:5]}")


if __name__ == "__main__":
    demo_z_array()
    demo_search()
    demo_z_vs_kmp()
    demo_conversion()
    demo_tandem()
