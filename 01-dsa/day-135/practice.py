"""
Day 135 Practice: KMP

6 exercises: failure function, search, count occurrences, smallest period,
overlapping matches, longest prefix-suffix.
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
# Exercise 1: Build Failure Function (LPS Array)
# ===================================================================

def build_lps(pattern):
    """fail[j] = length of longest proper prefix of pattern[0..j] that is also a suffix."""
    # TODO
    pass


def _sol_build_lps(pattern):
    m = len(pattern)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = fail[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        fail[i] = k
    return fail


# ===================================================================
# Exercise 2: KMP Search — Return All Match Positions
# ===================================================================

def kmp_find(text, pattern):
    """Return list of starting indices where pattern occurs in text."""
    # TODO
    pass


def _sol_kmp_find(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    if m > n:
        return []
    fail = _sol_build_lps(pattern)
    out = []
    j = 0
    for i in range(n):
        while j > 0 and pattern[j] != text[i]:
            j = fail[j - 1]
        if pattern[j] == text[i]:
            j += 1
        if j == m:
            out.append(i - m + 1)
            j = fail[j - 1]
    return out


# ===================================================================
# Exercise 3: Count Occurrences (Including Overlapping)
# ===================================================================

def count_occurrences(text, pattern):
    """Number of (possibly overlapping) occurrences."""
    # TODO
    pass


def _sol_count_occurrences(text, pattern):
    return len(_sol_kmp_find(text, pattern))


# ===================================================================
# Exercise 4: Smallest Period of a String
# ===================================================================
# Smallest p where s = (s[:p]) repeated. Returns len(s) if no proper period.

def smallest_period(s):
    """Smallest p such that s = (s[:p]) * k for some k >= 1."""
    # TODO
    pass


def _sol_smallest_period(s):
    if not s:
        return 0
    fail = _sol_build_lps(s)
    m = len(s)
    p = m - fail[m - 1]
    return p if m % p == 0 else m


# ===================================================================
# Exercise 5: Longest Proper Prefix that is Also a Suffix
# ===================================================================
# Return the longest substring that is both a proper prefix and proper suffix.

def longest_prefix_suffix(s):
    """Return the longest proper prefix of s that is also a suffix."""
    # TODO
    pass


def _sol_longest_prefix_suffix(s):
    if len(s) < 2:
        return ""
    fail = _sol_build_lps(s)
    return s[:fail[-1]]


# ===================================================================
# Exercise 6: Rotation Check via KMP
# ===================================================================
# Is `b` a rotation of `a`? Trick: b is a rotation of a iff b is a substring of a+a.

def is_rotation(a, b):
    """True if b is a rotation of a."""
    # TODO: use KMP
    pass


def _sol_is_rotation(a, b):
    if len(a) != len(b):
        return False
    if not a:
        return True
    return len(_sol_kmp_find(a + a, b)) > 0


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

    print("Exercise 1: LPS Array")
    check("ababaca", try_or_sol("build_lps", "ababaca"), [0, 0, 1, 2, 3, 0, 1])
    check("aaaa", try_or_sol("build_lps", "aaaa"), [0, 1, 2, 3])
    check("abcdef", try_or_sol("build_lps", "abcdef"), [0, 0, 0, 0, 0, 0])

    print("\nExercise 2: KMP Search")
    check("simple", try_or_sol("kmp_find", "abxabcabcaby", "abcaby"), [6])
    check("overlapping", try_or_sol("kmp_find", "aaaa", "aa"), [0, 1, 2])
    check("no match", try_or_sol("kmp_find", "hello", "world"), [])
    check("multi", try_or_sol("kmp_find", "abcabcabc", "abc"), [0, 3, 6])

    print("\nExercise 3: Count Occurrences")
    check("aaaa/aa", try_or_sol("count_occurrences", "aaaa", "aa"), 3)
    check("abracadabra/abra", try_or_sol("count_occurrences", "abracadabra", "abra"), 2)
    check("none", try_or_sol("count_occurrences", "hello", "xyz"), 0)

    print("\nExercise 4: Smallest Period")
    check("abcabcabc", try_or_sol("smallest_period", "abcabcabc"), 3)
    check("aaaa", try_or_sol("smallest_period", "aaaa"), 1)
    check("abab", try_or_sol("smallest_period", "abab"), 2)
    check("abcabd", try_or_sol("smallest_period", "abcabd"), 6)

    print("\nExercise 5: Longest Prefix-Suffix")
    check("ababa", try_or_sol("longest_prefix_suffix", "ababa"), "aba")
    check("abcd", try_or_sol("longest_prefix_suffix", "abcd"), "")
    check("aaaa", try_or_sol("longest_prefix_suffix", "aaaa"), "aaa")

    print("\nExercise 6: Rotation Check")
    check("rotation", try_or_sol("is_rotation", "abcde", "cdeab"), True)
    check("not rotation", try_or_sol("is_rotation", "abcde", "abced"), False)
    check("equal", try_or_sol("is_rotation", "abc", "abc"), True)
    check("diff length", try_or_sol("is_rotation", "ab", "abc"), False)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
