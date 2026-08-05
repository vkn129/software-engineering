"""
Day 136 Practice: Z-Algorithm

6 exercises: Z-array, pattern search, count occurrences, longest prefix
match, smallest period via Z, distinct substring count.
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
# Exercise 1: Build Z-Array
# ===================================================================
# Convention: Z[0] = len(s).

def z_array(s):
    """Build the Z-array."""
    # TODO: O(n) with Z-box
    pass


def _sol_z_array(s):
    n = len(s)
    if n == 0:
        return []
    z = [0] * n
    z[0] = n
    l = r = 0
    for i in range(1, n):
        if i <= r:
            z[i] = min(r - i + 1, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] - 1 > r:
            l, r = i, i + z[i] - 1
    return z


# ===================================================================
# Exercise 2: Pattern Search via Z
# ===================================================================

def z_find(text, pattern):
    """Return list of start positions of pattern in text."""
    # TODO: use Z-array on pattern + sentinel + text
    pass


def _sol_z_find(text, pattern):
    if not pattern:
        return list(range(len(text) + 1))
    SENT = "\x01"
    if SENT in pattern or SENT in text:
        SENT = "\x02"
    combined = pattern + SENT + text
    z = _sol_z_array(combined)
    m = len(pattern)
    out = []
    for i in range(m + 1, len(combined)):
        if z[i] >= m:
            out.append(i - m - 1)
    return out


# ===================================================================
# Exercise 3: Maximum Z-Value (Excluding Z[0])
# ===================================================================
# Useful for: "what's the longest substring starting at i>=1 matching prefix?"

def max_z(s):
    """Return max(Z[1:]) or 0 if s has length < 2."""
    # TODO
    pass


def _sol_max_z(s):
    if len(s) < 2:
        return 0
    z = _sol_z_array(s)
    return max(z[1:])


# ===================================================================
# Exercise 4: Smallest Period via Z
# ===================================================================
# Smallest p where s = (s[:p]) repeated. If Z[p] + p == n, then period is p.
# Iterate p from 1 upward; first p satisfying the condition where n % p == 0.

def smallest_period_z(s):
    """Smallest period p (1 <= p <= n) such that s is p-periodic."""
    # TODO
    pass


def _sol_smallest_period_z(s):
    if not s:
        return 0
    n = len(s)
    z = _sol_z_array(s)
    for p in range(1, n + 1):
        if n % p == 0 and (p == n or z[p] + p >= n):
            return p
    return n


# ===================================================================
# Exercise 5: Sum of Z-Array
# ===================================================================
# A measure of "prefix self-similarity" of the string.

def z_sum(s):
    """Sum of Z[0..n-1]."""
    # TODO
    pass


def _sol_z_sum(s):
    return sum(_sol_z_array(s))


# ===================================================================
# Exercise 6: Longest Common Prefix between s and Every Suffix
# ===================================================================
# Return list lcp[i] = length of longest common prefix of s and s[i:].
# By definition this is exactly Z[i] (with lcp[0] = len(s)).

def lcp_with_prefix(s):
    """List of len(s) entries: lcp[i] = |LCP(s, s[i:])|."""
    # TODO
    pass


def _sol_lcp_with_prefix(s):
    return _sol_z_array(s)


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

    print("Exercise 1: Z-Array")
    check("aaaa", try_or_sol("z_array", "aaaa"), [4, 3, 2, 1])
    check("abcdef", try_or_sol("z_array", "abcdef"), [6, 0, 0, 0, 0, 0])
    check("aabcaab", try_or_sol("z_array", "aabcaab"), [7, 1, 0, 0, 3, 1, 0])
    check("empty", try_or_sol("z_array", ""), [])

    print("\nExercise 2: Pattern Search")
    check("simple", try_or_sol("z_find", "abracadabra", "abra"), [0, 7])
    check("overlap", try_or_sol("z_find", "aaaa", "aa"), [0, 1, 2])
    check("no match", try_or_sol("z_find", "hello", "world"), [])

    print("\nExercise 3: Max Z")
    check("aaaa", try_or_sol("max_z", "aaaa"), 3)
    check("abcdef", try_or_sol("max_z", "abcdef"), 0)
    check("abcabcabc", try_or_sol("max_z", "abcabcabc"), 6)

    print("\nExercise 4: Smallest Period via Z")
    check("abcabcabc", try_or_sol("smallest_period_z", "abcabcabc"), 3)
    check("aaaa", try_or_sol("smallest_period_z", "aaaa"), 1)
    check("abcabd", try_or_sol("smallest_period_z", "abcabd"), 6)
    check("abab", try_or_sol("smallest_period_z", "abab"), 2)

    print("\nExercise 5: Z-Sum")
    check("aaaa", try_or_sol("z_sum", "aaaa"), 10)
    check("abcdef", try_or_sol("z_sum", "abcdef"), 6)
    check("aabcaab", try_or_sol("z_sum", "aabcaab"), 12)

    print("\nExercise 6: LCP with Prefix")
    check("aaaa", try_or_sol("lcp_with_prefix", "aaaa"), [4, 3, 2, 1])
    check("abcabc", try_or_sol("lcp_with_prefix", "abcabc"), [6, 0, 0, 3, 0, 0])

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
