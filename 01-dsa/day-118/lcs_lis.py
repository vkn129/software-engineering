"""
Day 118: Longest Common Subsequence (O(n*m)) and
         Longest Increasing Subsequence (O(n^2) and O(n log n) via patience sort).
"""

from bisect import bisect_left


# ---------------------------------------------------------------------------
# 1. Longest Common Subsequence — length
# ---------------------------------------------------------------------------

def lcs_length(a, b):
    """Length of the longest common subsequence of a and b."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


def lcs_length_compressed(a, b):
    """O(min(n,m)) space."""
    if len(a) < len(b):
        a, b = b, a
    n, m = len(a), len(b)
    prev = [0] * (m + 1)
    for i in range(1, n + 1):
        curr = [0] * (m + 1)
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = 1 + prev[j - 1]
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr
    return prev[m]


# ---------------------------------------------------------------------------
# 2. LCS — recover the actual subsequence
# ---------------------------------------------------------------------------

def lcs_string(a, b):
    """Return one valid LCS as a string."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    out = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))


# ---------------------------------------------------------------------------
# 3. LIS — O(n^2) DP
# ---------------------------------------------------------------------------

def lis_length_n2(a):
    """LIS length using O(n^2) DP."""
    n = len(a)
    if n == 0:
        return 0
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if a[j] < a[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
    return max(dp)


# ---------------------------------------------------------------------------
# 4. LIS — O(n log n) via patience sorting
# ---------------------------------------------------------------------------
# tails[k] = smallest possible tail of an increasing subseq of length k+1
# seen so far. Always strictly increasing.

def lis_length_nlogn(a):
    """Strictly increasing LIS length via patience sort."""
    tails = []
    for x in a:
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)


def lis_recover(a):
    """Return one valid LIS sequence (strictly increasing) using patience sort + back-ptrs."""
    if not a:
        return []
    n = len(a)
    tails = []
    tails_idx = []        # index of element at each tails position
    prev = [-1] * n       # predecessor index in the chosen LIS

    for i, x in enumerate(a):
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
            tails_idx.append(i)
        else:
            tails[pos] = x
            tails_idx[pos] = i
        if pos > 0:
            prev[i] = tails_idx[pos - 1]

    # Reconstruct from the tail of the longest piece
    out = []
    i = tails_idx[-1]
    while i != -1:
        out.append(a[i])
        i = prev[i]
    out.reverse()
    return out


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_lcs():
    print("=" * 60)
    print("DEMO 1: Longest Common Subsequence")
    print("=" * 60)
    pairs = [
        ("ABCBDAB", "BDCAB"),
        ("AGGTAB", "GXTXAYB"),
        ("abcdef", "xyz"),
        ("same", "same"),
    ]
    for a, b in pairs:
        length = lcs_length(a, b)
        seq = lcs_string(a, b)
        print(f"  '{a}' vs '{b}': len={length}, one LCS = '{seq}'")


def demo_lis():
    print("\n" + "=" * 60)
    print("DEMO 2: Longest Increasing Subsequence")
    print("=" * 60)
    arrays = [
        [10, 9, 2, 5, 3, 7, 101, 18],
        [3, 10, 2, 1, 20],
        [3, 3, 3, 3],
        [],
        [50, 3, 10, 7, 40, 80],
    ]
    for a in arrays:
        n2 = lis_length_n2(a)
        nlog = lis_length_nlogn(a)
        actual = lis_recover(a)
        print(f"  {a}")
        print(f"    O(n^2) = {n2}, O(n log n) = {nlog}, one LIS = {actual}")


def demo_patience():
    print("\n" + "=" * 60)
    print("DEMO 3: Patience Sort Walkthrough")
    print("=" * 60)
    a = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    tails = []
    print(f"\nInput: {a}\n")
    print(f"  step | x | action            | tails")
    print(f"  ----- + - + ----------------- + --------")
    for i, x in enumerate(a):
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
            action = f"extend at len {pos}"
        else:
            tails[pos] = x
            action = f"replace tails[{pos}]"
        print(f"   {i:3}  | {x} | {action:17} | {tails}")
    print(f"\nLIS length = {len(tails)}")


def demo_lcs_vs_substring():
    print("\n" + "=" * 60)
    print("DEMO 4: LCS vs Longest Common SUBSTRING (contiguous)")
    print("=" * 60)
    a, b = "ABABC", "BABCA"
    print(f"  a='{a}', b='{b}'")
    print(f"  LCS length:      {lcs_length(a, b)}  (one LCS = '{lcs_string(a, b)}')")
    # Quick longest common substring DP for comparison
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    best = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
                best = max(best, dp[i][j])
    print(f"  Substring length: {best}")


if __name__ == "__main__":
    demo_lcs()
    demo_lis()
    demo_patience()
    demo_lcs_vs_substring()
