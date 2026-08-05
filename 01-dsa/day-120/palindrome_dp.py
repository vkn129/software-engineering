"""
Day 120: Palindrome DP — From Scratch

Two palindrome problems, two DP families:
  1. Longest Palindromic Subsequence — 2D interval DP, O(n^2)
  2. Longest Palindromic Substring   — Manacher's, O(n)

Most DP bugs are state design bugs. Get state right; recurrence follows.
"""

import time
import random


# ---------------------------------------------------------------------------
# 1. Longest Palindromic Subsequence (LPS) — interval DP
# ---------------------------------------------------------------------------

def lps_length(s):
    """
    State: dp[i][j] = length of LPS in s[i..j]
    Recurrence:
      s[i] == s[j]: dp[i][j] = dp[i+1][j-1] + 2
      else:         dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    Order: increasing substring length.
    """
    n = len(s)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    # Fill by length
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = (dp[i + 1][j - 1] if length > 2 else 0) + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
    return dp[0][n - 1]


def lps_reconstruct(s):
    """Return one LPS (as a string), built by backtracking."""
    n = len(s)
    if n == 0:
        return ""
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = (dp[i + 1][j - 1] if length > 2 else 0) + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])

    # Backtrack
    left, right = [], []
    i, j = 0, n - 1
    while i < j:
        if s[i] == s[j]:
            left.append(s[i])
            right.append(s[j])
            i += 1
            j -= 1
        elif dp[i + 1][j] >= dp[i][j - 1]:
            i += 1
        else:
            j -= 1
    mid = s[i] if i == j else ""
    return "".join(left) + mid + "".join(reversed(right))


# ---------------------------------------------------------------------------
# 2. Longest Palindromic Substring — Naive O(n^2) DP (for comparison)
# ---------------------------------------------------------------------------

def lp_substring_naive(s):
    """
    State: dp[i][j] = True iff s[i..j] is a palindrome.
    O(n^2) time, O(n^2) space.
    """
    n = len(s)
    if n == 0:
        return ""
    dp = [[False] * n for _ in range(n)]
    best_i, best_j = 0, 0
    for i in range(n):
        dp[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or dp[i + 1][j - 1]):
                dp[i][j] = True
                if j - i > best_j - best_i:
                    best_i, best_j = i, j
    return s[best_i:best_j + 1]


# ---------------------------------------------------------------------------
# 3. Manacher's Algorithm — O(n) longest palindromic substring
# ---------------------------------------------------------------------------

def manacher(s):
    """
    Returns (longest_palindromic_substring, P_array_on_transformed)
    where P[i] is the palindrome radius around t[i].

    Transform: t = "^#a#b#c#$"  — sentinels prevent boundary checks.
    """
    if not s:
        return "", []

    # Transform
    t = "^#" + "#".join(s) + "#$"
    n = len(t)
    P = [0] * n
    C = R = 0  # center, right edge of rightmost palindrome

    for i in range(1, n - 1):
        i_mirror = 2 * C - i
        if i < R:
            P[i] = min(R - i, P[i_mirror])
        # Expand around i
        while t[i + P[i] + 1] == t[i - P[i] - 1]:
            P[i] += 1
        # Update C, R if expanded past R
        if i + P[i] > R:
            C, R = i, i + P[i]

    # Find max
    max_len = max(P)
    center = P.index(max_len)
    # Translate back to s indices
    start = (center - max_len) // 2
    return s[start:start + max_len], P


def count_palindromic_substrings(s):
    """Count all palindromic substrings using Manacher's radii."""
    if not s:
        return 0
    _, P = manacher(s)
    # Each P[i] contributes ceil(P[i] / 2) palindromes when i is at a
    # real (non-#) center, and floor(P[i] / 2) when at a '#' center.
    # Simpler: total = sum((P[i] + 1) // 2 for i in 1..n-2)
    return sum((p + 1) // 2 for p in P[1:-1])


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_lps():
    print("=" * 60)
    print("DEMO 1: Longest Palindromic Subsequence (interval DP)")
    print("=" * 60)
    cases = ["bbbab", "cbbd", "agbdba", "character"]
    for s in cases:
        n = lps_length(s)
        seq = lps_reconstruct(s)
        print(f"  s = {s!r:14} LPS len = {n}, LPS = {seq!r}")


def demo_manacher():
    print("\n" + "=" * 60)
    print("DEMO 2: Manacher's Longest Palindromic Substring")
    print("=" * 60)
    cases = ["babad", "cbbd", "racecar", "abacdfgdcaba", "forgeeksskeegfor"]
    for s in cases:
        sub, _ = manacher(s)
        print(f"  s = {s!r:22} LPSubstring = {sub!r}")


def demo_naive_vs_manacher():
    print("\n" + "=" * 60)
    print("DEMO 3: Naive O(n^2) vs Manacher O(n)")
    print("=" * 60)
    random.seed(0)
    n = 5000
    s = "".join(random.choice("ab") for _ in range(n))

    t0 = time.perf_counter()
    r1 = lp_substring_naive(s)
    t1 = time.perf_counter()
    r2, _ = manacher(s)
    t2 = time.perf_counter()

    print(f"\n  n = {n}, alphabet = 'ab'")
    print(f"  Naive:    {t1 - t0:.4f}s  -> len {len(r1)}")
    print(f"  Manacher: {t2 - t1:.4f}s  -> len {len(r2)}")
    print(f"  Speedup:  {(t1 - t0)/(t2 - t1):.1f}x")
    # Sanity
    assert len(r1) == len(r2)


def demo_count():
    print("\n" + "=" * 60)
    print("DEMO 4: Count Palindromic Substrings")
    print("=" * 60)
    cases = ["abc", "aaa", "aaaa", "abacaba"]
    for s in cases:
        c = count_palindromic_substrings(s)
        print(f"  s = {s!r:10} count = {c}")


if __name__ == "__main__":
    demo_lps()
    demo_manacher()
    demo_naive_vs_manacher()
    demo_count()
