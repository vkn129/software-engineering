"""
Day 138: Suffix Arrays & LCP — From Scratch

Build SA via prefix doubling: O(n log^2 n).
Compute LCP via Kasai: O(n) given SA.
Applications: longest repeated substring, longest common substring,
distinct substring count, indexed pattern search.
"""

import time
from bisect import bisect_left, bisect_right


# ---------------------------------------------------------------------------
# 1. Suffix Array — Naive (for verification only)
# ---------------------------------------------------------------------------

def suffix_array_naive(s):
    """O(n^2 log n). Trivially correct; use for testing."""
    return sorted(range(len(s)), key=lambda i: s[i:])


# ---------------------------------------------------------------------------
# 2. Suffix Array — Prefix Doubling
# ---------------------------------------------------------------------------

def suffix_array(s):
    """
    Build the suffix array of s in O(n log^2 n) via prefix doubling.

    Round k: sort suffixes by their first 2^k characters using rank pairs
    (rank[i], rank[i+2^(k-1)]). Each round halves the number of equivalence
    classes; we stop when all suffixes are uniquely ranked.
    """
    n = len(s)
    if n == 0:
        return []
    # Initial rank = character code (compress to dense indices later for speed)
    sa = list(range(n))
    rank = [ord(c) for c in s]
    tmp = [0] * n
    k = 1
    while True:
        def key(i):
            return (rank[i], rank[i + k] if i + k < n else -1)
        sa.sort(key=key)
        tmp[sa[0]] = 0
        for i in range(1, n):
            tmp[sa[i]] = tmp[sa[i - 1]] + (key(sa[i]) > key(sa[i - 1]))
        rank = tmp[:]
        if rank[sa[-1]] == n - 1:
            break  # all distinct ranks
        k *= 2
    return sa


# ---------------------------------------------------------------------------
# 3. LCP Array via Kasai's Algorithm
# ---------------------------------------------------------------------------

def lcp_kasai(s, sa):
    """
    O(n) LCP construction given SA.
    lcp[i] = |LCP(s[sa[i-1]:], s[sa[i]:])|, with lcp[0] = 0 by convention.
    """
    n = len(s)
    rank = [0] * n
    for i in range(n):
        rank[sa[i]] = i
    lcp = [0] * n
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and s[i + h] == s[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
    return lcp


# ---------------------------------------------------------------------------
# 4. Substring Search via Suffix Array Binary Search
# ---------------------------------------------------------------------------

def sa_search(s, sa, pattern):
    """
    Find all start positions of pattern in s using SA binary search.
    O(m log n) per query.
    """
    n, m = len(s), len(pattern)
    if m == 0:
        return list(range(n + 1))

    def cmp_suffix(idx, pat):
        # Compare s[idx:idx+m] with pat; -1, 0, 1
        end = min(idx + m, n)
        sub = s[idx:end]
        # Pad sub with min char if shorter? We rely on suffix being shorter.
        if sub == pat:
            return 0
        return -1 if sub < pat else 1

    # Binary search for left boundary
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if cmp_suffix(sa[mid], pattern) < 0:
            lo = mid + 1
        else:
            hi = mid
    left = lo
    # Binary search for right boundary
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if cmp_suffix(sa[mid], pattern) <= 0:
            lo = mid + 1
        else:
            hi = mid
    right = lo
    return sorted(sa[left:right])


# ---------------------------------------------------------------------------
# 5. Longest Repeated Substring
# ---------------------------------------------------------------------------

def longest_repeated_substring(s):
    """O(n log^2 n + n) — return one longest substring appearing >= 2 times."""
    if len(s) < 2:
        return ""
    sa = suffix_array(s)
    lcp = lcp_kasai(s, sa)
    best_len = max(lcp)
    if best_len == 0:
        return ""
    best_i = lcp.index(best_len)
    start = sa[best_i]
    return s[start:start + best_len]


# ---------------------------------------------------------------------------
# 6. Longest Common Substring of Two Strings
# ---------------------------------------------------------------------------

def longest_common_substring(a, b):
    """O((n+m) log^2 (n+m)) — via SA + LCP on a + '\\x01' + b + '\\x02'."""
    if not a or not b:
        return ""
    SENT_A, SENT_B = "\x01", "\x02"
    s = a + SENT_A + b + SENT_B
    n = len(s)
    cut = len(a)  # positions [0..cut) are from a; (cut..end) from b
    sa = suffix_array(s)
    lcp = lcp_kasai(s, sa)
    best = ""
    for i in range(1, n):
        a1 = sa[i - 1] < cut
        a2 = sa[i] < cut
        if a1 != a2 and lcp[i] > len(best):
            start = sa[i]
            best = s[start:start + lcp[i]]
    return best


# ---------------------------------------------------------------------------
# 7. Distinct Substring Count
# ---------------------------------------------------------------------------

def count_distinct_substrings(s):
    """O(n log^2 n) — n(n+1)/2 - sum(lcp)."""
    n = len(s)
    if n == 0:
        return 0
    sa = suffix_array(s)
    lcp = lcp_kasai(s, sa)
    return n * (n + 1) // 2 - sum(lcp)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 65)
    print("DEMO 1: Suffix Array of 'banana'")
    print("=" * 65)
    s = "banana"
    sa = suffix_array(s)
    print(f"  s = {s!r}")
    print(f"  sa = {sa}")
    print(f"  sorted suffixes:")
    for i in sa:
        print(f"    {i}: {s[i:]!r}")
    print(f"  matches naive: {sa == suffix_array_naive(s)}")


def demo_lcp():
    print("\n" + "=" * 65)
    print("DEMO 2: LCP Array via Kasai")
    print("=" * 65)
    for s in ["banana", "abracadabra", "mississippi"]:
        sa = suffix_array(s)
        lcp = lcp_kasai(s, sa)
        print(f"  s = {s!r:14s} sa = {sa}")
        print(f"                       lcp = {lcp}")


def demo_search():
    print("\n" + "=" * 65)
    print("DEMO 3: SA-Based Substring Search")
    print("=" * 65)
    s = "abracadabra-abracadabra"
    sa = suffix_array(s)
    print(f"  text:   {s!r}")
    for p in ["abra", "cad", "xyz", "bra"]:
        print(f"  {p!r:6s}: {sa_search(s, sa, p)}")


def demo_apps():
    print("\n" + "=" * 65)
    print("DEMO 4: Applications")
    print("=" * 65)
    s = "abcabcabc"
    print(f"  s = {s!r}")
    print(f"    longest repeated: {longest_repeated_substring(s)!r}")
    print(f"    distinct substrings: {count_distinct_substrings(s)}")
    print(f"    LCS(banana, ananas): {longest_common_substring('banana', 'ananas')!r}")
    print(f"    LCS(GATTACA, TACAGAT): {longest_common_substring('GATTACA', 'TACAGAT')!r}")


def demo_perf():
    print("\n" + "=" * 65)
    print("DEMO 5: Naive vs Prefix-Doubling SA")
    print("=" * 65)
    import random
    random.seed(0)
    text = "".join(random.choice("acgt") for _ in range(5000))

    t0 = time.perf_counter()
    sa_naive = suffix_array_naive(text)
    t_naive = time.perf_counter() - t0

    t0 = time.perf_counter()
    sa_pd = suffix_array(text)
    t_pd = time.perf_counter() - t0

    print(f"  n = 5000 random DNA")
    print(f"  naive (O(n^2 log n) sort): {t_naive:.4f}s")
    print(f"  prefix-doubling:           {t_pd:.4f}s")
    assert sa_naive == sa_pd


if __name__ == "__main__":
    demo_basic()
    demo_lcp()
    demo_search()
    demo_apps()
    demo_perf()
