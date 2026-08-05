"""
Day 140 Practice: Manacher's Algorithm

6 exercises. Implement TODOs, then run: python practice.py

Exercises 1-2 are the two-loop version (odd and even centers written
separately). Exercises 3-4 are the interleave trick that collapses them into
one loop. Exercises 5-6 use the resulting radius array as an index.

day-120 owns the palindrome-DP exercises (LPS, min cuts, min insertions,
counting). Nothing here repeats them.
"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: odd-center radii (d1)
# ---------------------------------------------------------------------------

def manacher_odd(s):
    """
    Return d1 where d1[i] = number of odd-length palindromes centered at i.
    The longest such palindrome has length 2*d1[i] - 1, so d1[i] >= 1 always.

    Use the l/r box: inside it, seed from the mirror but cap at r - i + 1.
    """
    # TODO: implement in O(n) with the mirror trick
    pass


def _sol_manacher_odd(s):
    n = len(s)
    d1 = [0] * n
    l, r = 0, -1
    for i in range(n):
        # Cap at r - i + 1: past r nothing has been compared yet.
        k = 1 if i > r else min(d1[l + r - i], r - i + 1)
        while 0 <= i - k and i + k < n and s[i - k] == s[i + k]:
            k += 1
        d1[i] = k
        k -= 1
        if i + k > r:
            l, r = i - k, i + k
    return d1


# ---------------------------------------------------------------------------
# Exercise 2: even-center radii (d2)
# ---------------------------------------------------------------------------

def manacher_even(s):
    """
    Return d2 where d2[i] = number of even-length palindromes centered in the
    gap BEFORE i (between s[i-1] and s[i]). Longest has length 2*d2[i].
    d2[0] == 0 always — there is no gap before the string.

    Same shape as exercise 1 but every left index shifts by one. That asymmetry
    is exactly what the interleave trick in exercise 3 exists to delete.
    """
    # TODO: implement in O(n)
    pass


def _sol_manacher_even(s):
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
# Exercise 3: the interleave transform
# ---------------------------------------------------------------------------

def transform(s):
    """
    Return "^#" + "#".join(s) + "#$".

    "abba" -> "^#a#b#b#a#$". Separators force every palindrome to odd length;
    the distinct guards let the expansion loop terminate without bounds checks.
    """
    # TODO: implement
    pass


def _sol_transform(s):
    return "^#" + "#".join(s) + "#$"


# ---------------------------------------------------------------------------
# Exercise 4: radii on the transformed string
# ---------------------------------------------------------------------------

def manacher_radii(s):
    """
    Return P over transform(s), where P[i] is the radius EXCLUDING the center —
    which equals the length, in s, of the longest palindrome centered there.
    Return [] for the empty string.

    The `min(R - i, P[mirror])` is not optional: on s = "abab" the no-min
    version reports P[8] = 3 instead of 1.
    """
    # TODO: implement with the C/R box and the mirror trick
    pass


def _sol_manacher_radii(s):
    if not s:
        return []
    t = _sol_transform(s)
    n = len(t)
    P = [0] * n
    C = R = 0
    for i in range(1, n - 1):
        if i < R:
            # Only the part of the mirror's palindrome inside the box is
            # trustworthy; beyond R nothing has been compared.
            P[i] = min(R - i, P[2 * C - i])
        while t[i + P[i] + 1] == t[i - P[i] - 1]:
            P[i] += 1
        if i + P[i] > R:
            C, R = i, i + P[i]
    return P


# ---------------------------------------------------------------------------
# Exercise 5: O(1) palindrome range query from the radius array
# ---------------------------------------------------------------------------

def is_palindrome_query(P, i, j):
    """
    Given P from manacher_radii(s), return True iff s[i..j] (inclusive) is a
    palindrome. Must be O(1) — one lookup, one comparison. No slicing, no loop.

    Hint: s[i] sits at t-index 2i+2, so the center of s[i..j] is at i+j+2.
    """
    # TODO: implement in O(1)
    pass


def _sol_is_palindrome_query(P, i, j):
    # A palindrome of length >= (j-i+1) is centered at t[i+j+2] iff the radius
    # there reaches that far. The radius IS the length in s, so no conversion.
    return P[i + j + 2] >= j - i + 1


# ---------------------------------------------------------------------------
# Exercise 6: shortest palindrome having s as a prefix
# ---------------------------------------------------------------------------

def shortest_palindrome(s):
    """
    Prepend the fewest characters to make s a palindrome.
    "abcd" -> "dcbabcd";  "aacecaaa" -> "aaacecaaa";  "" -> "".

    Find the longest palindromic PREFIX, then mirror everything after it in
    front. O(n) with one Manacher pass; the obvious way is O(n^2).
    """
    # TODO: implement using manacher_radii
    pass


def _sol_shortest_palindrome(s):
    if not s:
        return ""
    P = _sol_manacher_radii(s)
    best = 0
    for i in range(1, len(P) - 1):
        # A palindrome is a prefix exactly when its left end hits the guard.
        if i - P[i] == 1 and P[i] > best:
            best = P[i]
    return s[best:][::-1] + s


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: manacher_odd (d1)")
    check("aba", try_or_sol("manacher_odd", "aba"), [1, 2, 1])
    check("abba (no long odd)", try_or_sol("manacher_odd", "abba"), [1, 1, 1, 1])
    check("aaaa", try_or_sol("manacher_odd", "aaaa"), [1, 2, 2, 1])
    check("abacaba", try_or_sol("manacher_odd", "abacaba"), [1, 2, 1, 4, 1, 2, 1])

    print("\nExercise 2: manacher_even (d2)")
    check("abba", try_or_sol("manacher_even", "abba"), [0, 0, 2, 0])
    check("aaaa", try_or_sol("manacher_even", "aaaa"), [0, 1, 2, 1])
    check("aba (none)", try_or_sol("manacher_even", "aba"), [0, 0, 0])
    check("abab (none)", try_or_sol("manacher_even", "abab"), [0, 0, 0, 0])

    print("\nExercise 3: transform")
    check("abba", try_or_sol("transform", "abba"), "^#a#b#b#a#$")
    check("a", try_or_sol("transform", "a"), "^#a#$")
    check("length is 2n+3", len(try_or_sol("transform", "abcde")), 2 * 5 + 3)

    print("\nExercise 4: manacher_radii")
    check("abba", try_or_sol("manacher_radii", "abba"),
          [0, 0, 1, 0, 1, 4, 1, 0, 1, 0, 0])
    check("aba", try_or_sol("manacher_radii", "aba"), [0, 0, 1, 0, 3, 0, 1, 0, 0])
    # The min() case: without it, P[8] comes out as 3.
    check("abab (needs min)", try_or_sol("manacher_radii", "abab"),
          [0, 0, 1, 0, 3, 0, 3, 0, 1, 0, 0])
    check("empty", try_or_sol("manacher_radii", ""), [])
    check("max P == longest palindrome length",
          max(try_or_sol("manacher_radii", "forgeeksskeegfor")), 10)

    print("\nExercise 5: is_palindrome_query")
    s = "aacecaaa"
    P = _sol_manacher_radii(s)
    check("(0,1) 'aa'", try_or_sol("is_palindrome_query", P, 0, 1), True)
    check("(0,6) 'aacecaa'", try_or_sol("is_palindrome_query", P, 0, 6), True)
    check("(0,7) 'aacecaaa'", try_or_sol("is_palindrome_query", P, 0, 7), False)
    check("(5,7) 'aaa'", try_or_sol("is_palindrome_query", P, 5, 7), True)
    check("(2,4) 'cec'", try_or_sol("is_palindrome_query", P, 2, 4), True)
    check("(1,3) 'ace'", try_or_sol("is_palindrome_query", P, 1, 3), False)
    check("(3,3) single char", try_or_sol("is_palindrome_query", P, 3, 3), True)

    print("\nExercise 6: shortest_palindrome")
    check("abcd", try_or_sol("shortest_palindrome", "abcd"), "dcbabcd")
    check("aacecaaa", try_or_sol("shortest_palindrome", "aacecaaa"), "aaacecaaa")
    check("already palindrome", try_or_sol("shortest_palindrome", "aba"), "aba")
    check("empty", try_or_sol("shortest_palindrome", ""), "")
    check("ab", try_or_sol("shortest_palindrome", "ab"), "bab")

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    print('=' * 50)


if __name__ == "__main__":
    run_tests()
