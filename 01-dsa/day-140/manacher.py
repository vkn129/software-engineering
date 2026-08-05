"""
Day 140: Manacher's Algorithm — From Scratch

All 2n+1 palindrome radii of a string in O(n) time and O(n) space.

Structure, in the order the ideas actually appear:

  1. Naive baselines            — the O(n^2) reference we check against
  2. Two-loop Manacher          — d1 (odd centers) and d2 (even centers), written twice
  3. The interleave transform   — one loop instead of two, and why it is exact
  4. Interleaved Manacher       — the algorithm proper
  5. PalindromeIndex            — the radius array used as an O(1)-query index
  6. shortest_palindrome        — a real application of the longest palindromic prefix

day-120 owns palindrome DP and already ships a compact `manacher()` for the
"longest palindromic substring" question. This file exists to derive the thing:
why the transform is a bijection, why the `min` is load-bearing, and what the
radius array buys you once you stop throwing it away.
"""

import random


# ---------------------------------------------------------------------------
# 1. Naive baselines — slow, obviously correct, used as the oracle
# ---------------------------------------------------------------------------

def is_palindrome_naive(s, i, j):
    """True iff s[i..j] inclusive is a palindrome. O(j - i)."""
    while i < j:
        if s[i] != s[j]:
            return False
        i += 1
        j -= 1
    return True


def longest_palindrome_naive(s):
    """
    O(n^2): expand around each of the 2n-1 centers.

    This is already better than the O(n^3) "check every substring" version, and
    it is what most people write from memory. Manacher's beats it only because
    it refuses to re-compare characters a previous center already settled.
    """
    if not s:
        return ""
    best_start, best_len = 0, 1
    n = len(s)
    for center in range(n):
        for lo, hi in ((center, center), (center, center + 1)):
            while lo >= 0 and hi < n and s[lo] == s[hi]:
                lo -= 1
                hi += 1
            # the loop exits one step past the palindrome on both sides
            length = hi - lo - 1
            if length > best_len:
                best_start, best_len = lo + 1, length
    return s[best_start:best_start + best_len]


# ---------------------------------------------------------------------------
# 2. Two-loop Manacher — the duplication that motivates the transform
# ---------------------------------------------------------------------------

def manacher_odd(s):
    """
    d1[i] = number of odd-length palindromes centered at i.
    The longest of them has length 2*d1[i] - 1. Always >= 1.

    `l, r` is the palindrome found so far reaching furthest right (r inclusive).
    `l + r - i` is i's mirror across that palindrome's center.
    """
    n = len(s)
    d1 = [0] * n
    l, r = 0, -1  # r = -1 means "no box yet", so `i > r` holds at i = 0
    for i in range(n):
        # Inside the box we copy the mirror's radius, but never past the box's
        # right edge — beyond r nothing has been compared. Hence the min().
        k = 1 if i > r else min(d1[l + r - i], r - i + 1)
        while 0 <= i - k and i + k < n and s[i - k] == s[i + k]:
            k += 1
        d1[i] = k
        k -= 1  # k is now the radius excluding the center
        if i + k > r:
            l, r = i - k, i + k
    return d1


def manacher_even(s):
    """
    d2[i] = number of even-length palindromes centered in the gap BEFORE i,
    i.e. between s[i-1] and s[i]. The longest has length 2*d2[i].
    d2[0] is always 0 — there is no gap before the string.

    Same algorithm as manacher_odd with every left index shifted by one. That
    asymmetry is the whole reason the interleave trick was invented: this
    function is not conceptually different, only arithmetically nastier.
    """
    n = len(s)
    d2 = [0] * n
    l, r = 0, -1
    for i in range(n):
        k = 0 if i > r else min(d2[l + r - i + 1], r - i + 1)
        while 0 <= i - k - 1 and i + k < n and s[i - k - 1] == s[i + k]:
            k += 1
        d2[i] = k
        k -= 1
        if i + k > r:
            l, r = i - k - 1, i + k
    return d2


# ---------------------------------------------------------------------------
# 3. The interleave transform
# ---------------------------------------------------------------------------

GUARD_LEFT = "^"
GUARD_RIGHT = "$"
SEP = "#"


def transform(s):
    """
    "abba"  ->  "^#a#b#b#a#$"

    Separators make every palindrome odd-length: both ends of a palindrome share
    a parity, so in a strictly alternating string both ends are the same kind of
    character, which forces odd length. Guards make the expansion loop
    self-terminating — '^' never equals '$', so the comparison fails at the
    boundary without a bounds check in the hot loop.

    Length is 2*len(s) + 3 for non-empty s. (The empty string is the one
    degenerate case: "^##$", length 4 — manacher_radii short-circuits it.)
    """
    return GUARD_LEFT + SEP + SEP.join(s) + SEP + GUARD_RIGHT


def t_index_of_char(j):
    """Character s[j] lives at t[2j+2]."""
    return 2 * j + 2


def t_index_of_gap(j):
    """The gap before s[j] lives at t[2j+1]."""
    return 2 * j + 1


# ---------------------------------------------------------------------------
# 4. Interleaved Manacher — the algorithm proper
# ---------------------------------------------------------------------------

def manacher_radii(s):
    """
    Return P over the transformed string, where P[i] is the radius EXCLUDING the
    center. Because t alternates separator/character, P[i] is simultaneously the
    *length in s* of the longest palindrome centered there — no parity case, no
    division at the call site.

    C, R track the palindrome reaching furthest right. R never decreases, which
    is what makes the whole thing linear: every successful character comparison
    pushes R one step right, and R is bounded by len(t).
    """
    if not s:
        return []
    t = transform(s)
    n = len(t)
    P = [0] * n
    C = R = 0
    for i in range(1, n - 1):  # guards are never centers
        if i < R:
            mirror = 2 * C - i
            # min() is load-bearing: P[mirror] may describe a palindrome that
            # pokes out past the LEFT edge of the box, and the part outside the
            # box is not mirrored knowledge. See demo_why_min_matters().
            P[i] = min(R - i, P[mirror])
        # Expansion only ever reads past R. The guards stop it at the ends.
        while t[i + P[i] + 1] == t[i - P[i] - 1]:
            P[i] += 1
        if i + P[i] > R:
            C, R = i, i + P[i]
    return P


def radii_to_d1_d2(P, n):
    """
    Recover the two-loop arrays from the interleaved one. This is the proof that
    the transform loses nothing: the bijection runs both ways.
    """
    d1 = [(P[t_index_of_char(j)] + 1) // 2 for j in range(n)]
    d2 = [P[t_index_of_gap(j)] // 2 for j in range(n)]
    return d1, d2


def _radii_no_min(s):
    """
    Deliberately WRONG: copies the mirror's radius without capping it at R - i.

    Kept because the bug is invisible on most inputs — it needs a mirror
    palindrome that extends past the box's left edge. Explicit bounds checks
    replace the guards here, because the inflated radius can point off the end
    of t (in C that is an out-of-bounds read, not merely a wrong answer).
    """
    if not s:
        return []
    t = transform(s)
    n = len(t)
    P = [0] * n
    C = R = 0
    for i in range(1, n - 1):
        if i < R:
            P[i] = P[2 * C - i]  # BUG: missing min(R - i, ...)
        while (i + P[i] + 1 < n and i - P[i] - 1 >= 0
               and t[i + P[i] + 1] == t[i - P[i] - 1]):
            P[i] += 1
        if i + P[i] > R:
            C, R = i, i + P[i]
    return P


# ---------------------------------------------------------------------------
# 5. The radius array as an index
# ---------------------------------------------------------------------------

class PalindromeIndex:
    """
    O(n) preprocessing, O(n) space, O(1) per query.

    day-120's DP table answers is_palindrome(i, j) in O(1) too — but it stores
    n^2 booleans. For a 1 MB document that is 10^12 cells versus 2*10^6 ints.
    Same query, same asymptotic query cost, different universe of feasibility.
    """

    def __init__(self, s):
        self.s = s
        self.n = len(s)
        self.P = manacher_radii(s)

    def is_palindrome(self, i, j):
        """
        True iff s[i..j] inclusive is a palindrome.

        The t-center of s[i..j] is i + j + 2 (midpoint of t-indices 2i+2 and
        2j+2); the substring's length in s is j - i + 1. A palindrome of at
        least that length is centered there iff P[center] >= length.
        """
        if not (0 <= i <= j < self.n):
            raise IndexError(f"bad range ({i}, {j}) for length {self.n}")
        return self.P[i + j + 2] >= j - i + 1

    def longest_at_char(self, j):
        """Longest odd palindrome centered on s[j], as a string."""
        c = t_index_of_char(j)
        p = self.P[c]
        start = (c - p) // 2
        return self.s[start:start + p]

    def longest_at_gap(self, j):
        """Longest even palindrome centered in the gap before s[j]."""
        c = t_index_of_gap(j)
        p = self.P[c]
        start = (c - p) // 2
        return self.s[start:start + p]

    def longest(self):
        """The longest palindromic substring. One max over 2n+1 centers."""
        if not self.n:
            return ""
        best = max(range(len(self.P)), key=lambda i: self.P[i])
        p = self.P[best]
        start = (best - p) // 2
        return self.s[start:start + p]

    def maximal_palindromes(self):
        """
        Every maximal palindrome, one per center, in left-to-right center order.

        At most 2n+1 of them even though a string may contain Theta(n^2)
        palindromic substrings: every palindromic substring is one of these with
        equal numbers of characters trimmed off both ends.
        """
        out = []
        for i in range(1, len(self.P) - 1):
            p = self.P[i]
            if p > 0:
                start = (i - p) // 2
                out.append(self.s[start:start + p])
        return out

    def longest_palindromic_prefix(self):
        """A palindrome is a prefix iff its left end touches the left guard."""
        best = 0
        for i in range(1, len(self.P) - 1):
            if i - self.P[i] == 1 and self.P[i] > best:
                best = self.P[i]
        return self.s[:best]

    def longest_palindromic_suffix(self):
        """...and a suffix iff its right end touches the right guard."""
        end = len(self.P) - 2
        best = 0
        for i in range(1, len(self.P) - 1):
            if i + self.P[i] == end and self.P[i] > best:
                best = self.P[i]
        return self.s[self.n - best:] if best else ""


# ---------------------------------------------------------------------------
# 6. Application — fewest characters prepended to make s a palindrome
# ---------------------------------------------------------------------------

def shortest_palindrome(s):
    """
    Shortest palindrome having s as a prefix.

    Whatever sits after the longest palindromic *prefix* must be mirrored in
    front. Finding that prefix is a single O(n) Manacher pass; the obvious
    version is O(n^2) prefix checks.
    """
    if not s:
        return ""
    lpp = PalindromeIndex(s).longest_palindromic_prefix()
    tail = s[len(lpp):]
    return tail[::-1] + s


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_even_odd_problem():
    print("=" * 68)
    print("DEMO 1: the even/odd problem, and the two-loop answer")
    print("=" * 68)
    for s in ["aba", "abba", "aaaa", "abacaba"]:
        print(f"\n  s  = {s!r}")
        print(f"  d1 = {manacher_odd(s)}   (longest odd  at i has length 2*d1[i]-1)")
        print(f"  d2 = {manacher_even(s)}   (longest even before i has length 2*d2[i])")
    print("\n  Two arrays, two loops, two sets of index arithmetic.")
    print("  d2's `i - k - 1` vs d1's `i - k` is where the bugs live.")


def demo_transform():
    print("\n" + "=" * 68)
    print("DEMO 2: the interleave transform makes every palindrome odd")
    print("=" * 68)
    for s in ["abba", "aba"]:
        t = transform(s)
        P = manacher_radii(s)
        print(f"\n  s = {s!r}   ->   t = {t!r}   (len {len(s)} -> {len(t)})")
        print("  idx : " + " ".join(f"{i:2d}" for i in range(len(t))))
        print("  t   : " + " ".join(f"{c:>2}" for c in t))
        print("  P   : " + " ".join(f"{p:2d}" for p in P))
        print(f"  max P = {max(P)} = length of the longest palindrome in s "
              f"({PalindromeIndex(s).longest()!r})")
    print("\n  P[i] is a radius in t but reads directly as a LENGTH in s,")
    print("  because t alternates separator/character all the way across.")


def demo_transform_is_lossless():
    print("\n" + "=" * 68)
    print("DEMO 3: the transform is a bijection — recover d1/d2 from P")
    print("=" * 68)
    random.seed(140)
    checked = 0
    for _ in range(400):
        n = random.randint(1, 24)
        s = "".join(random.choice("abc") for _ in range(n))
        d1, d2 = radii_to_d1_d2(manacher_radii(s), n)
        assert d1 == manacher_odd(s), f"d1 mismatch on {s!r}"
        assert d2 == manacher_even(s), f"d2 mismatch on {s!r}"
        checked += 1
    print(f"\n  {checked} random strings: d1/d2 recovered from P match the")
    print("  hand-written two-loop versions exactly. Nothing is lost.")
    print("  If your 2j+1 / 2j+2 arithmetic is wrong, this is where you find out.")


def demo_why_min_matters():
    print("\n" + "=" * 68)
    print("DEMO 4: min(R - i, P[mirror]) is load-bearing")
    print("=" * 68)
    s = "abab"
    good = manacher_radii(s)
    bad = _radii_no_min(s)
    print(f"\n  s = {s!r}   t = {transform(s)!r}")
    print(f"  correct : {good}")
    print(f"  no-min  : {bad}")
    diffs = [i for i, (a, b) in enumerate(zip(good, bad)) if a != b]
    print(f"  differ at t-index {diffs}")
    for i in diffs:
        print(f"    P[{i}]: correct {good[i]}, no-min {bad[i]}  "
              f"-> claims a length-{bad[i]} palindrome centered at t[{i}]")
    print("\n  'abab' is the SHORTEST string that exposes this. The mirror's")
    print("  palindrome pokes past the box's left edge, so only R - i of it is")
    print("  trustworthy. In C the inflated radius is an out-of-bounds read.")

    random.seed(1)
    broken = 0
    for _ in range(2000):
        r = "".join(random.choice("ab") for _ in range(random.randint(1, 14)))
        if manacher_radii(r) != _radii_no_min(r):
            broken += 1
    print(f"  Over 2000 random strings the no-min version is wrong {broken} times.")


def demo_index_queries():
    print("\n" + "=" * 68)
    print("DEMO 5: the radius array as an O(1)-query index")
    print("=" * 68)
    s = "abacabadabacaba"
    idx = PalindromeIndex(s)
    print(f"\n  s = {s!r}  (n = {len(s)})")
    print(f"  longest palindromic substring : {idx.longest()!r}")
    print(f"  longest palindromic prefix    : {idx.longest_palindromic_prefix()!r}")
    print(f"  longest palindromic suffix    : {idx.longest_palindromic_suffix()!r}")
    print(f"  maximal palindromes           : {len(idx.maximal_palindromes())} "
          f"(<= 2n+1 = {2 * len(s) + 1})")
    print("  (this s is itself a palindrome, so all three coincide)")
    print("\n  O(1) range queries:")
    for i, j in [(0, 2), (0, 4), (4, 10), (0, 14), (1, 3)]:
        print(f"    is_palindrome({i:2d},{j:2d}) = "
              f"{str(idx.is_palindrome(i, j)):5s}  s[{i}..{j}] = {s[i:j + 1]!r}")

    # A string where longest / prefix / suffix genuinely differ.
    s2 = "aacecaaa"
    i2 = PalindromeIndex(s2)
    print(f"\n  s = {s2!r}  (n = {len(s2)})")
    print(f"  longest palindromic substring : {i2.longest()!r}")
    print(f"  longest palindromic prefix    : {i2.longest_palindromic_prefix()!r}")
    print(f"  longest palindromic suffix    : {i2.longest_palindromic_suffix()!r}")
    print(f"  longest_at_char(3)            : {i2.longest_at_char(3)!r}")
    print(f"  longest_at_gap(1)             : {i2.longest_at_gap(1)!r}")


def demo_cross_check():
    print("\n" + "=" * 68)
    print("DEMO 6: cross-check against the naive oracle")
    print("=" * 68)
    random.seed(7)
    ranges = 0
    for _ in range(300):
        n = random.randint(0, 20)
        s = "".join(random.choice("ab") for _ in range(n))
        assert len(PalindromeIndex(s).longest()) == len(longest_palindrome_naive(s)), s
        idx = PalindromeIndex(s)
        for i in range(n):
            for j in range(i, n):
                assert idx.is_palindrome(i, j) == is_palindrome_naive(s, i, j), \
                    f"{s!r} ({i},{j})"
                ranges += 1
    print(f"\n  300 random strings, {ranges} range queries: index == naive oracle.")
    for s in ["", "a", "aa", "ab", "aacecaaa", "abcd"]:
        print(f"  shortest_palindrome({s!r:12}) = {shortest_palindrome(s)!r}")


if __name__ == "__main__":
    demo_even_odd_problem()
    demo_transform()
    demo_transform_is_lossless()
    demo_why_min_matters()
    demo_index_queries()
    demo_cross_check()
