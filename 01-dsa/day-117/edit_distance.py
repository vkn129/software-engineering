"""
Day 117: Edit Distance (Levenshtein) with backtrace.

dp[i][j] = edit distance between a[:i] and b[:j].
Recurrence enumerates the last operation: match, substitute, delete, insert.
Total: O(n*m) time and space; O(min(n,m)) space possible.
"""


# ---------------------------------------------------------------------------
# 1. Basic edit distance
# ---------------------------------------------------------------------------

def edit_distance(a, b):
    """Levenshtein distance between strings a and b."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],     # delete a[i-1]
                    dp[i][j - 1],     # insert b[j-1]
                    dp[i - 1][j - 1], # substitute
                )
    return dp[n][m]


def edit_distance_compressed(a, b):
    """O(min(n,m)) space version."""
    # Ensure b is the shorter string for less memory
    if len(a) < len(b):
        a, b = b, a
    n, m = len(a), len(b)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[m]


# ---------------------------------------------------------------------------
# 2. Edit distance with backtrace
# ---------------------------------------------------------------------------

def edit_distance_with_ops(a, b):
    """
    Return (distance, list_of_ops) where each op is one of:
      ('match', char)   - keep a[i-1] == b[j-1]
      ('sub', from, to) - substitute a[i-1] -> b[j-1]
      ('del', char)     - delete a[i-1]
      ('ins', char)     - insert b[j-1]
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1],
                )

    # Backtrace
    ops = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and dp[i][j] == dp[i - 1][j - 1]:
            ops.append(("match", a[i - 1]))
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            ops.append(("sub", a[i - 1], b[j - 1]))
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            ops.append(("del", a[i - 1]))
            i -= 1
        else:
            ops.append(("ins", b[j - 1]))
            j -= 1

    ops.reverse()
    return dp[n][m], ops


# ---------------------------------------------------------------------------
# 3. Damerau-Levenshtein (adjacent-transpose adds one op)
# ---------------------------------------------------------------------------

def damerau_levenshtein(a, b):
    """Like Levenshtein but with an extra 'swap adjacent' op of cost 1."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)
    return dp[n][m]


# ---------------------------------------------------------------------------
# 4. Spell-checker demo using brute force over a small dictionary
# ---------------------------------------------------------------------------

def spell_suggest(word, dictionary, max_distance=2, top_k=5):
    """Return up to top_k dictionary words within max_distance."""
    scored = []
    for w in dictionary:
        d = edit_distance(word, w)
        if d <= max_distance:
            scored.append((d, w))
    scored.sort()
    return scored[:top_k]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Edit Distance")
    print("=" * 60)
    pairs = [
        ("kitten", "sitting"),
        ("intention", "execution"),
        ("abc", "yabcd"),
        ("", "abc"),
        ("abc", ""),
        ("same", "same"),
    ]
    for a, b in pairs:
        print(f"  d('{a}', '{b}') = {edit_distance(a, b)}")


def demo_ops():
    print("\n" + "=" * 60)
    print("DEMO 2: Edit Operations (backtrace)")
    print("=" * 60)
    pairs = [("kitten", "sitting"), ("flaw", "lawn")]
    for a, b in pairs:
        d, ops = edit_distance_with_ops(a, b)
        print(f"\n  '{a}' -> '{b}' (distance {d})")
        for op in ops:
            print(f"    {op}")


def demo_damerau():
    print("\n" + "=" * 60)
    print("DEMO 3: Damerau-Levenshtein (transposes)")
    print("=" * 60)
    pairs = [("teh", "the"), ("acer", "racer"), ("trial", "trail")]
    for a, b in pairs:
        lev = edit_distance(a, b)
        dam = damerau_levenshtein(a, b)
        print(f"  '{a}' vs '{b}': Levenshtein={lev}, Damerau={dam}")


def demo_spellcheck():
    print("\n" + "=" * 60)
    print("DEMO 4: Tiny Spell Checker")
    print("=" * 60)
    dictionary = [
        "receive", "relieve", "recover", "deceive", "perceive",
        "the", "then", "than", "they", "them",
        "system", "syntax", "symbol",
    ]
    typos = ["recieve", "teh", "systme"]
    for t in typos:
        suggestions = spell_suggest(t, dictionary, max_distance=2, top_k=3)
        print(f"  '{t}' -> {suggestions}")


def demo_compression():
    print("\n" + "=" * 60)
    print("DEMO 5: O(n*m) vs O(min(n,m)) Space — same answer")
    print("=" * 60)
    a, b = "exponential", "polynomial"
    full = edit_distance(a, b)
    comp = edit_distance_compressed(a, b)
    print(f"  d('{a}', '{b}') full table = {full}, compressed = {comp}")


if __name__ == "__main__":
    demo_basic()
    demo_ops()
    demo_damerau()
    demo_spellcheck()
    demo_compression()
