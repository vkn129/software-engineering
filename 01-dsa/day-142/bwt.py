"""
Day 142: Burrows-Wheeler Transform

Forward: build sorted rotations matrix, take last column.
Inverse: LF mapping reconstructs original from BWT alone.
Plus MTF and a tiny end-to-end compression pipeline.
"""

from collections import Counter


SENTINEL = "$"   # must be lexicographically less than every input character


# ---------------------------------------------------------------------------
# 1. Naive BWT — sort all rotations
# ---------------------------------------------------------------------------

def bwt_naive(s):
    """
    Append sentinel, build n rotations, sort, return last column.
    O(n^2 log n) time, O(n^2) space. Use only for small inputs / teaching.
    """
    assert SENTINEL not in s, f"Input must not contain sentinel '{SENTINEL}'"
    s += SENTINEL
    n = len(s)
    rotations = [s[i:] + s[:i] for i in range(n)]
    rotations.sort()
    return "".join(r[-1] for r in rotations)


# ---------------------------------------------------------------------------
# 2. BWT via suffix array — O(n log^2 n) using the trick L[i] = S[SA[i]-1]
# ---------------------------------------------------------------------------

def suffix_array(s):
    """Simple O(n log^2 n) suffix array via doubling + sort."""
    n = len(s)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    k = 1
    while True:
        def key(i):
            return (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        new_rank = [0] * n
        new_rank[sa[0]] = 0
        for i in range(1, n):
            new_rank[sa[i]] = new_rank[sa[i - 1]]
            if key(sa[i]) != key(sa[i - 1]):
                new_rank[sa[i]] += 1
        rank = new_rank
        if rank[sa[-1]] == n - 1:
            break
        k *= 2
    return sa


def bwt_via_sa(s):
    """BWT via suffix array. O(n log^2 n)."""
    assert SENTINEL not in s
    s += SENTINEL
    sa = suffix_array(s)
    n = len(s)
    return "".join(s[(sa[i] - 1) % n] for i in range(n))


# ---------------------------------------------------------------------------
# 3. Inverse BWT via LF mapping
# ---------------------------------------------------------------------------

def inverse_bwt(bwt):
    """
    Reconstruct original string (including sentinel) from BWT.

    Build:
      F = sorted(L) — first column
      rank_in_L[i] = number of L[j] == L[i] for j < i
      first_occ[c] = first index in F where char c starts

    LF(i) = first_occ[L[i]] + rank_in_L[i]
    Start from the row whose F-char is sentinel (LF chain ends at sentinel).
    Walk LF backwards to reconstruct.
    """
    L = bwt
    n = len(L)

    # rank_in_L[i] = occurrences of L[i] in L[0..i-1]
    counts = Counter()
    rank_in_L = [0] * n
    for i, c in enumerate(L):
        rank_in_L[i] = counts[c]
        counts[c] += 1

    # first_occ[c] = first index in F (sorted L) where c appears
    first_occ = {}
    pos = 0
    for c in sorted(counts):
        first_occ[c] = pos
        pos += counts[c]

    # The row in M that starts with $ is at index first_occ[$].
    # In that row, the last char is L[first_occ[$]] = the char before $ in S,
    # which is the LAST char of original S. So we walk LF from that row.
    # Easier: start from row whose L-char is the char preceding sentinel in the
    # original, by starting at the row beginning with $ and walking LF.
    # Equivalent and simpler: find the row where L[i] == sentinel, then walk LF
    # collecting L[i] each step — this yields original in forward order.

    # Row r where L[r] == sentinel: the cyclic rotation that ends with $ is the
    # row whose rotation is exactly S$ — so picking that row and walking LF in
    # reverse rebuilds S from the end.
    r = L.index(SENTINEL)
    out = []
    for _ in range(n):
        out.append(L[r])
        r = first_occ[L[r]] + rank_in_L[r]
    # `out` ends up as S with sentinel at index 0 (we collected in reverse).
    out.reverse()
    result = "".join(out)
    # depending on walk start, sentinel ends up at the boundary — strip either end
    if result.endswith(SENTINEL):
        result = result[:-1]
    elif result.startswith(SENTINEL):
        result = result[1:]
    return result


# ---------------------------------------------------------------------------
# 4. Move-To-Front transform
# ---------------------------------------------------------------------------

def mtf_encode(s, alphabet=None):
    """
    Move-To-Front encode s. Returns list of ints.
    Default alphabet: bytes 0..255 (or all chars in s, sorted).
    """
    if alphabet is None:
        alphabet = sorted(set(s))
    table = list(alphabet)
    out = []
    for c in s:
        idx = table.index(c)
        out.append(idx)
        # move to front
        table.pop(idx)
        table.insert(0, c)
    return out, alphabet


def mtf_decode(codes, alphabet):
    """Inverse of mtf_encode."""
    table = list(alphabet)
    out = []
    for idx in codes:
        c = table[idx]
        out.append(c)
        table.pop(idx)
        table.insert(0, c)
    return "".join(out)


# ---------------------------------------------------------------------------
# 5. Run-length encoding (numeric, for after MTF)
# ---------------------------------------------------------------------------

def rle_encode(nums):
    """[0,0,0,1,1,2] -> [(0,3),(1,2),(2,1)]"""
    if not nums:
        return []
    out = []
    cur = nums[0]
    cnt = 1
    for x in nums[1:]:
        if x == cur:
            cnt += 1
        else:
            out.append((cur, cnt))
            cur = x
            cnt = 1
    out.append((cur, cnt))
    return out


def rle_decode(pairs):
    out = []
    for v, c in pairs:
        out.extend([v] * c)
    return out


# ---------------------------------------------------------------------------
# 6. End-to-end pipeline (toy)
# ---------------------------------------------------------------------------

def compress(s):
    """BWT -> MTF -> RLE. Returns (rle_pairs, alphabet) suitable for round-trip."""
    bwt = bwt_via_sa(s)
    codes, alphabet = mtf_encode(bwt)
    pairs = rle_encode(codes)
    return pairs, alphabet


def decompress(pairs, alphabet):
    codes = rle_decode(pairs)
    bwt = mtf_decode(codes, alphabet)
    return inverse_bwt(bwt)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 142: Burrows-Wheeler Transform")
    print("=" * 60)

    for s in ["banana", "abracadabra", "mississippi"]:
        b1 = bwt_naive(s)
        b2 = bwt_via_sa(s)
        inv = inverse_bwt(b1)
        print(f"\n  S       = {s!r}")
        print(f"  BWT     = {b1!r}")
        print(f"  via SA  = {b2!r}  match={b1 == b2}")
        print(f"  inverse = {inv!r}  match={inv == s}")

    print("\n--- Clustering effect ---")
    s = "the_quick_brown_fox_jumps_over_the_lazy_dog_" * 5
    b = bwt_via_sa(s)
    # count runs in BWT vs original
    def runs(x):
        return sum(1 for i in range(1, len(x)) if x[i] != x[i - 1]) + 1
    print(f"  orig runs: {runs(s)},  BWT runs: {runs(b)}")
    print(f"  (lower BWT runs => better RLE compression)")

    print("\n--- MTF round-trip ---")
    bwt = bwt_via_sa("mississippi")
    codes, alph = mtf_encode(bwt)
    print(f"  BWT('mississippi') = {bwt!r}")
    print(f"  MTF codes = {codes}")
    print(f"  decoded   = {mtf_decode(codes, alph)!r}")

    print("\n--- Full pipeline round-trip ---")
    for s in ["banana", "mississippi", "AAAAABBBBBCCCCC"]:
        pairs, alph = compress(s)
        rec = decompress(pairs, alph)
        print(f"  '{s}' -> rle={pairs} -> '{rec}'  ok={rec == s}")


if __name__ == "__main__":
    demo()
