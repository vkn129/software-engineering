"""
Day 142 Practice: Burrows-Wheeler Transform

6 exercises. Implement the TODOs, then run: python practice.py
"""

from collections import Counter

SENTINEL = "$"


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: Naive BWT via sorted rotations
# ---------------------------------------------------------------------------

def bwt(s):
    """Append SENTINEL, sort rotations, return last column."""
    # TODO
    pass


def _sol_bwt(s):
    s = s + SENTINEL
    n = len(s)
    rots = sorted(s[i:] + s[:i] for i in range(n))
    return "".join(r[-1] for r in rots)


# ---------------------------------------------------------------------------
# Exercise 2: Inverse BWT via LF mapping
# ---------------------------------------------------------------------------

def inverse_bwt(L):
    """Reconstruct the original string (WITHOUT sentinel) from its BWT L."""
    # TODO
    pass


def _sol_inverse_bwt(L):
    n = len(L)
    counts = Counter()
    rank_in_L = [0] * n
    for i, c in enumerate(L):
        rank_in_L[i] = counts[c]
        counts[c] += 1
    first_occ = {}
    pos = 0
    for c in sorted(counts):
        first_occ[c] = pos
        pos += counts[c]
    r = L.index(SENTINEL)
    out = []
    for _ in range(n):
        out.append(L[r])
        r = first_occ[L[r]] + rank_in_L[r]
    out.reverse()
    res = "".join(out)
    if res.endswith(SENTINEL):
        res = res[:-1]
    elif res.startswith(SENTINEL):
        res = res[1:]
    return res


# ---------------------------------------------------------------------------
# Exercise 3: MTF encode
# ---------------------------------------------------------------------------

def mtf_encode(s):
    """Move-To-Front encode. Alphabet = sorted unique chars in s.
    Return (list of ints, alphabet list)."""
    # TODO
    pass


def _sol_mtf_encode(s):
    table = sorted(set(s))
    alphabet = list(table)
    out = []
    for c in s:
        idx = table.index(c)
        out.append(idx)
        table.pop(idx)
        table.insert(0, c)
    return out, alphabet


# ---------------------------------------------------------------------------
# Exercise 4: MTF decode
# ---------------------------------------------------------------------------

def mtf_decode(codes, alphabet):
    """Inverse of mtf_encode. Return the decoded string."""
    # TODO
    pass


def _sol_mtf_decode(codes, alphabet):
    table = list(alphabet)
    out = []
    for idx in codes:
        c = table[idx]
        out.append(c)
        table.pop(idx)
        table.insert(0, c)
    return "".join(out)


# ---------------------------------------------------------------------------
# Exercise 5: Run-length encode a list of ints
# ---------------------------------------------------------------------------

def rle(nums):
    """Return list of (value, count) for consecutive equal runs."""
    # TODO
    pass


def _sol_rle(nums):
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


# ---------------------------------------------------------------------------
# Exercise 6: Round-trip pipeline (BWT -> MTF -> RLE -> reverse)
# ---------------------------------------------------------------------------

def roundtrip(s):
    """Apply bwt, mtf_encode, rle, then reverse all three. Return final string."""
    # TODO
    pass


def _sol_roundtrip(s):
    b = _sol_bwt(s)
    codes, alph = _sol_mtf_encode(b)
    pairs = _sol_rle(codes)
    # reverse
    flat = []
    for v, c in pairs:
        flat.extend([v] * c)
    bwt_back = _sol_mtf_decode(flat, alph)
    return _sol_inverse_bwt(bwt_back)


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
            print(f"  FAIL: {name}  got={got!r}  expected={expected!r}")
            failed += 1

    print("Exercise 1: bwt")
    check("banana", try_or_sol("bwt", "banana"), "annb$aa")
    check("abracadabra", try_or_sol("bwt", "abracadabra"), "ard$rcaaaabb")
    check("a", try_or_sol("bwt", "a"), "a$")

    print("\nExercise 2: inverse_bwt")
    check("invert banana", try_or_sol("inverse_bwt", "annb$aa"), "banana")
    check("invert abracadabra",
          try_or_sol("inverse_bwt", "ard$rcaaaabb"), "abracadabra")
    check("invert single", try_or_sol("inverse_bwt", "a$"), "a")

    print("\nExercise 3: mtf_encode")
    codes, alph = try_or_sol("mtf_encode", "aaabbc")
    check("aaabbc codes", codes, [0, 0, 0, 1, 0, 2])
    check("aaabbc alphabet", alph, ["a", "b", "c"])

    print("\nExercise 4: mtf_decode")
    check("decode aaabbc",
          try_or_sol("mtf_decode", [0, 0, 0, 1, 0, 2], ["a", "b", "c"]),
          "aaabbc")
    # idx 2 -> 'c' (table becomes [c,a,b]); idx 1 -> 'a' (table [a,c,b]); idx 0 -> 'a'
    check("decode after moves",
          try_or_sol("mtf_decode", [2, 1, 0], ["a", "b", "c"]),
          "caa")

    print("\nExercise 5: rle")
    check("empty", try_or_sol("rle", []), [])
    check("zeros and ones", try_or_sol("rle", [0, 0, 0, 1, 1, 2]),
          [(0, 3), (1, 2), (2, 1)])
    check("single", try_or_sol("rle", [5]), [(5, 1)])

    print("\nExercise 6: roundtrip")
    for s in ["banana", "mississippi", "AAABBB", "abracadabra"]:
        check(f"roundtrip {s!r}", try_or_sol("roundtrip", s), s)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
