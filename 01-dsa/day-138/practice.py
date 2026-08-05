"""
Day 138 Practice: Suffix Arrays & LCP

6 exercises: SA build, LCP via Kasai, distinct substrings, longest
repeated, longest common substring, indexed search.
"""


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Build Suffix Array (any correct method)
# ===================================================================

def build_sa(s):
    """Return suffix array as a list of starting indices."""
    # TODO
    pass


def _sol_build_sa(s):
    n = len(s)
    if n == 0:
        return []
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
            break
        k *= 2
    return sa


# ===================================================================
# Exercise 2: Build LCP Array via Kasai
# ===================================================================

def build_lcp(s, sa):
    """Return LCP array; lcp[0] = 0 by convention."""
    # TODO
    pass


def _sol_build_lcp(s, sa):
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


# ===================================================================
# Exercise 3: Count Distinct Substrings
# ===================================================================

def distinct_substring_count(s):
    """Number of distinct non-empty substrings of s."""
    # TODO
    pass


def _sol_distinct_substring_count(s):
    n = len(s)
    if n == 0:
        return 0
    sa = _sol_build_sa(s)
    lcp = _sol_build_lcp(s, sa)
    return n * (n + 1) // 2 - sum(lcp)


# ===================================================================
# Exercise 4: Longest Repeated Substring
# ===================================================================

def longest_repeated(s):
    """One longest substring appearing at least twice; '' if none."""
    # TODO
    pass


def _sol_longest_repeated(s):
    if len(s) < 2:
        return ""
    sa = _sol_build_sa(s)
    lcp = _sol_build_lcp(s, sa)
    best = max(lcp)
    if best == 0:
        return ""
    i = lcp.index(best)
    return s[sa[i]:sa[i] + best]


# ===================================================================
# Exercise 5: Longest Common Substring of Two Strings
# ===================================================================

def lcs_two(a, b):
    """Longest substring appearing in both a and b."""
    # TODO
    pass


def _sol_lcs_two(a, b):
    if not a or not b:
        return ""
    SA_, SB_ = "\x01", "\x02"
    s = a + SA_ + b + SB_
    cut = len(a)
    sa = _sol_build_sa(s)
    lcp = _sol_build_lcp(s, sa)
    best = ""
    for i in range(1, len(s)):
        a1 = sa[i - 1] < cut
        a2 = sa[i] < cut
        if a1 != a2 and lcp[i] > len(best):
            best = s[sa[i]:sa[i] + lcp[i]]
    return best


# ===================================================================
# Exercise 6: Substring Search via SA Binary Search
# ===================================================================

def indexed_search(s, sa, pattern):
    """Find all positions of pattern in s using sa. O(m log n)."""
    # TODO
    pass


def _sol_indexed_search(s, sa, pattern):
    n, m = len(s), len(pattern)
    if m == 0:
        return list(range(n + 1))

    def cmp(idx):
        sub = s[idx:idx + m]
        if sub == pattern:
            return 0
        return -1 if sub < pattern else 1

    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if cmp(sa[mid]) < 0:
            lo = mid + 1
        else:
            hi = mid
    left = lo
    lo, hi = 0, n
    while lo < hi:
        mid = (lo + hi) // 2
        if cmp(sa[mid]) <= 0:
            lo = mid + 1
        else:
            hi = mid
    right = lo
    return sorted(sa[left:right])


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

    print("Exercise 1: Suffix Array")
    check("banana", try_or_sol("build_sa", "banana"), [5, 3, 1, 0, 4, 2])
    check("abc", try_or_sol("build_sa", "abc"), [0, 1, 2])
    check("empty", try_or_sol("build_sa", ""), [])
    check("aaaa", try_or_sol("build_sa", "aaaa"), [3, 2, 1, 0])

    print("\nExercise 2: LCP Array")
    sa = _sol_build_sa("banana")
    check("banana lcp", try_or_sol("build_lcp", "banana", sa), [0, 1, 3, 0, 0, 2])
    sa = _sol_build_sa("aaaa")
    check("aaaa lcp", try_or_sol("build_lcp", "aaaa", sa), [0, 1, 2, 3])
    sa = _sol_build_sa("abc")
    check("abc lcp", try_or_sol("build_lcp", "abc", sa), [0, 0, 0])

    print("\nExercise 3: Distinct Substrings")
    check("banana", try_or_sol("distinct_substring_count", "banana"), 15)
    check("aaaa", try_or_sol("distinct_substring_count", "aaaa"), 4)
    check("abc", try_or_sol("distinct_substring_count", "abc"), 6)

    print("\nExercise 4: Longest Repeated")
    check("banana", try_or_sol("longest_repeated", "banana"), "ana")
    check("aabcaabd", try_or_sol("longest_repeated", "aabcaabd"), "aab")
    check("abcdef", try_or_sol("longest_repeated", "abcdef"), "")

    print("\nExercise 5: LCS of Two Strings")
    check("banana/ananas", try_or_sol("lcs_two", "banana", "ananas"), "anana")
    check("hello/world", len(try_or_sol("lcs_two", "hello", "world")), 1)
    check("none", try_or_sol("lcs_two", "abc", "xyz"), "")

    print("\nExercise 6: Indexed Search")
    s = "abracadabra"
    sa = _sol_build_sa(s)
    check("abra positions", try_or_sol("indexed_search", s, sa, "abra"), [0, 7])
    check("cad", try_or_sol("indexed_search", s, sa, "cad"), [4])
    check("xyz", try_or_sol("indexed_search", s, sa, "xyz"), [])

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
