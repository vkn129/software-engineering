"""
Day 120 Practice: Palindrome DP

Fill in each TODO. Reference solutions in `_sol_*` functions.
Run this file; it should print Results: 6/6 passed.
"""


# ---------------------------------------------------------------------------
# Problem 1: Longest Palindromic Subsequence length
# ---------------------------------------------------------------------------

def lps_length(s):
    """
    TODO: Return the length of the longest palindromic subsequence of s.
    State: dp[i][j] = LPS of s[i..j].
    """
    pass


def _sol_lps_length(s):
    n = len(s)
    if n == 0:
        return 0
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
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Problem 2: Minimum insertions to make s a palindrome
# ---------------------------------------------------------------------------

def min_insertions_for_palindrome(s):
    """
    TODO: Return min insertions to make s a palindrome.
    Hint: answer = len(s) - LPS(s).
    """
    pass


def _sol_min_insertions_for_palindrome(s):
    return len(s) - _sol_lps_length(s)


# ---------------------------------------------------------------------------
# Problem 3: Longest palindromic substring (Manacher's)
# ---------------------------------------------------------------------------

def longest_palindromic_substring(s):
    """
    TODO: Return the longest palindromic substring of s.
    Implement Manacher's or O(n^2) DP.
    """
    pass


def _sol_longest_palindromic_substring(s):
    if not s:
        return ""
    t = "^#" + "#".join(s) + "#$"
    n = len(t)
    P = [0] * n
    C = R = 0
    for i in range(1, n - 1):
        mirror = 2 * C - i
        if i < R:
            P[i] = min(R - i, P[mirror])
        while t[i + P[i] + 1] == t[i - P[i] - 1]:
            P[i] += 1
        if i + P[i] > R:
            C, R = i, i + P[i]
    max_len = max(P)
    center = P.index(max_len)
    start = (center - max_len) // 2
    return s[start:start + max_len]


# ---------------------------------------------------------------------------
# Problem 4: Count distinct palindromic substrings (count all centers)
# ---------------------------------------------------------------------------

def count_palindromic_substrings(s):
    """
    TODO: Count all palindromic substrings (positions matter — duplicates OK).
    """
    pass


def _sol_count_palindromic_substrings(s):
    if not s:
        return 0
    t = "^#" + "#".join(s) + "#$"
    n = len(t)
    P = [0] * n
    C = R = 0
    for i in range(1, n - 1):
        mirror = 2 * C - i
        if i < R:
            P[i] = min(R - i, P[mirror])
        while t[i + P[i] + 1] == t[i - P[i] - 1]:
            P[i] += 1
        if i + P[i] > R:
            C, R = i, i + P[i]
    return sum((p + 1) // 2 for p in P[1:-1])


# ---------------------------------------------------------------------------
# Problem 5: Palindrome partitioning (min cuts)
# ---------------------------------------------------------------------------

def min_palindrome_cuts(s):
    """
    TODO: Min cuts so every piece is a palindrome.
    State: cuts[i] = min cuts for s[0..i].
    """
    pass


def _sol_min_palindrome_cuts(s):
    n = len(s)
    if n == 0:
        return 0
    pal = [[False] * n for _ in range(n)]
    for i in range(n):
        pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
    cuts = [0] * n
    for i in range(n):
        if pal[0][i]:
            cuts[i] = 0
        else:
            cuts[i] = min(cuts[j] + 1 for j in range(i) if pal[j + 1][i])
    return cuts[n - 1]


# ---------------------------------------------------------------------------
# Problem 6: Is s a palindrome after deleting at most one char?
# ---------------------------------------------------------------------------

def valid_palindrome_one_delete(s):
    """
    TODO: Two-pointer; on mismatch try skipping left or right once.
    """
    pass


def _sol_valid_palindrome_one_delete(s):
    def is_pal(a, b):
        while a < b:
            if s[a] != s[b]:
                return False
            a += 1
            b -= 1
        return True
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]:
            return is_pal(l + 1, r) or is_pal(l, r - 1)
        l += 1
        r -= 1
    return True


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    total = 6

    cases1 = [("bbbab", 4), ("cbbd", 2), ("a", 1), ("", 0), ("character", 5)]
    fn = lps_length if lps_length("a") is not None else _sol_lps_length
    if all(fn(s) == e for s, e in cases1):
        passed += 1; print("  [PASS] 1: lps_length")
    else:
        print("  [FAIL] 1: lps_length")

    cases2 = [("ab", 1), ("aa", 0), ("abcd", 3), ("aebcbda", 2)]
    fn = min_insertions_for_palindrome if min_insertions_for_palindrome("a") is not None else _sol_min_insertions_for_palindrome
    if all(fn(s) == e for s, e in cases2):
        passed += 1; print("  [PASS] 2: min_insertions_for_palindrome")
    else:
        print("  [FAIL] 2: min_insertions_for_palindrome")

    cases3 = [("babad", {"bab", "aba"}), ("cbbd", {"bb"}), ("a", {"a"}), ("racecar", {"racecar"})]
    fn = longest_palindromic_substring if longest_palindromic_substring("a") is not None else _sol_longest_palindromic_substring
    ok = all(fn(s) in e for s, e in cases3)
    if ok:
        passed += 1; print("  [PASS] 3: longest_palindromic_substring")
    else:
        print("  [FAIL] 3: longest_palindromic_substring")

    cases4 = [("abc", 3), ("aaa", 6), ("aaaa", 10), ("abacaba", 12)]
    fn = count_palindromic_substrings if count_palindromic_substrings("a") is not None else _sol_count_palindromic_substrings
    if all(fn(s) == e for s, e in cases4):
        passed += 1; print("  [PASS] 4: count_palindromic_substrings")
    else:
        print("  [FAIL] 4: count_palindromic_substrings")

    cases5 = [("aab", 1), ("a", 0), ("aba", 0), ("abcde", 4)]
    fn = min_palindrome_cuts if min_palindrome_cuts("a") is not None else _sol_min_palindrome_cuts
    if all(fn(s) == e for s, e in cases5):
        passed += 1; print("  [PASS] 5: min_palindrome_cuts")
    else:
        print("  [FAIL] 5: min_palindrome_cuts")

    cases6 = [("aba", True), ("abca", True), ("abc", False), ("deeee", True), ("cbbcc", True)]
    fn = valid_palindrome_one_delete if valid_palindrome_one_delete("a") is not None else _sol_valid_palindrome_one_delete
    if all(fn(s) == e for s, e in cases6):
        passed += 1; print("  [PASS] 6: valid_palindrome_one_delete")
    else:
        print("  [FAIL] 6: valid_palindrome_one_delete")

    print(f"\nResults: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
