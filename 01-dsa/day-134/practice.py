"""
Day 134 Practice: Rabin-Karp & Rolling Hash

6 exercises: rolling hash, substring search, prefix hash queries,
multi-pattern search, longest duplicated substring, anagram windows.
"""

MOD = (1 << 61) - 1
BASE = 131


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Compute Polynomial Hash
# ===================================================================
# Implement poly hash: h = sum(s[i] * base^(m-1-i)) mod p.

def compute_hash(s, base=BASE, mod=MOD):
    """Compute polynomial hash of string s."""
    # TODO
    pass


def _sol_compute_hash(s, base=BASE, mod=MOD):
    h = 0
    for ch in s:
        h = (h * base + ord(ch)) % mod
    return h


# ===================================================================
# Exercise 2: Rabin-Karp Substring Search
# ===================================================================
# Return all start positions where pattern occurs in text.

def rk_search(text, pattern):
    """Return list of all start positions of pattern in text."""
    # TODO: implement rolling hash + verify
    pass


def _sol_rk_search(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    bmm1 = pow(BASE, m - 1, MOD)
    ph = _sol_compute_hash(pattern)
    wh = _sol_compute_hash(text[:m])
    out = []
    for i in range(n - m + 1):
        if wh == ph and text[i:i + m] == pattern:
            out.append(i)
        if i < n - m:
            wh = ((wh - ord(text[i]) * bmm1) * BASE + ord(text[i + m])) % MOD
    return out


# ===================================================================
# Exercise 3: Count Distinct Substrings of Length k
# ===================================================================
# Use rolling hash to enumerate substrings, dedupe by hash.
# Caveat: verify if needed; for this problem we accept single-hash dedup.

def count_distinct_k(s, k):
    """Number of distinct substrings of length k in s."""
    # TODO
    pass


def _sol_count_distinct_k(s, k):
    n = len(s)
    if k == 0 or k > n:
        return 0
    seen = set()
    bmm1 = pow(BASE, k - 1, MOD)
    h = _sol_compute_hash(s[:k])
    seen.add((h, s[:k]))  # store window for verify-on-collision
    for i in range(n - k):
        h = ((h - ord(s[i]) * bmm1) * BASE + ord(s[i + k])) % MOD
        seen.add((h, s[i + 1:i + 1 + k]))
    # Dedup by actual string (the tuple just avoided hash-only dedup risk)
    return len({s for _, s in seen})


# ===================================================================
# Exercise 4: Longest Common Substring of Two Strings
# ===================================================================
# Binary search on length L; for each L, hash all length-L substrings
# of A, check if any length-L substring of B matches. O((n+m) log min).

def longest_common_substring(a, b):
    """Return one longest common substring of a and b (empty if none)."""
    # TODO
    pass


def _sol_longest_common_substring(a, b):
    def has_common(L):
        if L == 0:
            return ""
        bmm1 = pow(BASE, L - 1, MOD)
        # Hash all length-L windows of a
        seen = {}
        h = _sol_compute_hash(a[:L])
        seen[h] = 0
        for i in range(len(a) - L):
            h = ((h - ord(a[i]) * bmm1) * BASE + ord(a[i + L])) % MOD
            seen.setdefault(h, i + 1)
        # Scan b
        h = _sol_compute_hash(b[:L])
        if h in seen and a[seen[h]:seen[h] + L] == b[:L]:
            return b[:L]
        for i in range(len(b) - L):
            h = ((h - ord(b[i]) * bmm1) * BASE + ord(b[i + L])) % MOD
            if h in seen:
                cand = b[i + 1:i + 1 + L]
                if a[seen[h]:seen[h] + L] == cand:
                    return cand
        return None

    lo, hi = 0, min(len(a), len(b))
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        got = has_common(mid)
        if got:
            best = got
            lo = mid + 1
        else:
            hi = mid - 1
    return best


# ===================================================================
# Exercise 5: Multi-Pattern Search (Equal Lengths)
# ===================================================================
# Given patterns of equal length, return dict pattern -> [start positions].

def multi_search(text, patterns):
    """Return dict mapping each pattern to list of start positions."""
    # TODO
    pass


def _sol_multi_search(text, patterns):
    if not patterns:
        return {}
    m = len(patterns[0])
    n = len(text)
    results = {p: [] for p in patterns}
    if m > n:
        return results
    bmm1 = pow(BASE, m - 1, MOD)
    table = {}
    for p in patterns:
        table.setdefault(_sol_compute_hash(p), []).append(p)
    wh = _sol_compute_hash(text[:m])
    for i in range(n - m + 1):
        if wh in table:
            window = text[i:i + m]
            for cand in table[wh]:
                if cand == window:
                    results[cand].append(i)
        if i < n - m:
            wh = ((wh - ord(text[i]) * bmm1) * BASE + ord(text[i + m])) % MOD
    return results


# ===================================================================
# Exercise 6: Longest Repeated Substring
# ===================================================================
# Find the longest substring appearing >= 2 times in s.
# Binary search on length + rolling hash to detect duplicates.

def longest_repeated(s):
    """Return longest substring that appears at least twice in s."""
    # TODO
    pass


def _sol_longest_repeated(s):
    def find_dup(L):
        if L == 0:
            return ""
        n = len(s)
        if L > n:
            return None
        bmm1 = pow(BASE, L - 1, MOD)
        seen = {}
        h = _sol_compute_hash(s[:L])
        seen[h] = 0
        for i in range(n - L):
            h = ((h - ord(s[i]) * bmm1) * BASE + ord(s[i + L])) % MOD
            start = i + 1
            cand = s[start:start + L]
            if h in seen:
                prev = seen[h]
                if s[prev:prev + L] == cand:
                    return cand
            seen[h] = start
        return None

    lo, hi = 0, len(s) - 1
    best = ""
    while lo <= hi:
        mid = (lo + hi) // 2
        got = find_dup(mid)
        if got:
            best = got
            lo = mid + 1
        else:
            hi = mid - 1
    return best


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    print("Exercise 1: Polynomial Hash")
    check("empty", try_or_sol("compute_hash", ""), 0)
    check("same string same hash",
          try_or_sol("compute_hash", "hello") == try_or_sol("compute_hash", "hello"),
          True)
    check("different strings different hash",
          try_or_sol("compute_hash", "abc") != try_or_sol("compute_hash", "abd"),
          True)

    print("\nExercise 2: Rabin-Karp Search")
    check("simple", try_or_sol("rk_search", "abracadabra", "abra"), [0, 7])
    check("no match", try_or_sol("rk_search", "hello", "world"), [])
    check("overlapping", try_or_sol("rk_search", "aaaa", "aa"), [0, 1, 2])

    print("\nExercise 3: Distinct Substrings of Length k")
    check("aaaa k=2", try_or_sol("count_distinct_k", "aaaa", 2), 1)
    check("abab k=2", try_or_sol("count_distinct_k", "abab", 2), 2)
    check("abcde k=3", try_or_sol("count_distinct_k", "abcde", 3), 3)

    print("\nExercise 4: Longest Common Substring")
    r = try_or_sol("longest_common_substring", "abcdef", "xbcdyz")
    check("bcd shared", r, "bcd")
    r = try_or_sol("longest_common_substring", "abc", "xyz")
    check("no common", r, "")
    r = try_or_sol("longest_common_substring", "banana", "ananas")
    check("anana", r, "anana")

    print("\nExercise 5: Multi-Pattern Search")
    r = try_or_sol("multi_search", "the cat sat on the mat", ["cat", "mat", "rat"])
    check("cat at 4", r["cat"], [4])
    check("mat at 19", r["mat"], [19])
    check("rat absent", r["rat"], [])

    print("\nExercise 6: Longest Repeated Substring")
    check("banana", try_or_sol("longest_repeated", "banana"), "ana")
    check("aabcaabdaab last", try_or_sol("longest_repeated", "aabcaabdaab"), "aab")
    check("abcdef none", try_or_sol("longest_repeated", "abcdef"), "")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
