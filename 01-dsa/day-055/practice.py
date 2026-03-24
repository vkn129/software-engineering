"""
Day 55 Practice: Suffix Array Exercises
========================================
Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from suffix_structures import build_suffix_array, build_lcp_array, search_pattern


# ─── Exercise 1: Find All Occurrences ──────────────────────────────
#
# Given a text and pattern, return all starting positions where the
# pattern occurs. Use suffix array + binary search.
# Example: text = "abcabcabc", pattern = "abc" → [0, 3, 6]

def find_all_occurrences(text, pattern):
    # TODO: implement using suffix array
    pass


# ─── Exercise 2: Longest Repeated Substring ────────────────────────
#
# Find the longest substring that appears at least twice.
# Use: max(LCP array) gives the length, SA gives the position.
# Example: "abcabc" → "abc"

def longest_repeated(text):
    # TODO: implement
    pass


# ─── Exercise 3: LCP Array Construction ────────────────────────────
#
# Implement Kasai's algorithm from scratch.
# Given text and its suffix array, return the LCP array.

def kasai_lcp(text, sa):
    # TODO: implement Kasai's algorithm
    pass


# ─── Exercise 4: Longest Common Substring of Two Strings ───────────
#
# Find the longest common substring between two strings.
# Approach: concatenate as s1 + "$" + s2 + "#", build suffix array + LCP.
# The answer is the max LCP where adjacent suffixes come from different strings.
#
# Example: "abcdef", "bcdegh" → "bcde"

def longest_common_substring(s1, s2):
    # TODO: implement
    pass


# ─── Exercise 5: Count Distinct Substrings ─────────────────────────
#
# Count distinct non-empty substrings of a string.
# Formula: n*(n+1)/2 - sum(LCP)
# Example: "abc" → 6 (a, ab, abc, b, bc, c)
# Example: "aaa" → 3 (a, aa, aaa)

def count_distinct(text):
    # TODO: implement
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_find_all_occurrences(text, pattern):
    sa = build_suffix_array(text)
    return search_pattern(text, sa, pattern)


def _sol_longest_repeated(text):
    if len(text) <= 1:
        return ""
    sa = build_suffix_array(text)
    lcp = build_lcp_array(text, sa)
    max_lcp = 0
    max_idx = 0
    for i in range(1, len(lcp)):
        if lcp[i] > max_lcp:
            max_lcp = lcp[i]
            max_idx = i
    if max_lcp == 0:
        return ""
    return text[sa[max_idx]:sa[max_idx] + max_lcp]


def _sol_kasai_lcp(text, sa):
    n = len(text)
    rank = [0] * n
    lcp = [0] * n
    for i in range(n):
        rank[sa[i]] = i
    h = 0
    for i in range(n):
        if rank[i] > 0:
            j = sa[rank[i] - 1]
            while i + h < n and j + h < n and text[i + h] == text[j + h]:
                h += 1
            lcp[rank[i]] = h
            if h > 0:
                h -= 1
        else:
            h = 0
    return lcp


def _sol_longest_common_substring(s1, s2):
    combined = s1 + "$" + s2 + "#"
    n1 = len(s1)
    sa = build_suffix_array(combined)
    lcp = build_lcp_array(combined, sa)

    best_len = 0
    best_pos = 0

    for i in range(1, len(sa)):
        # Check if adjacent suffixes come from different strings
        pos1 = sa[i - 1]
        pos2 = sa[i]
        from_s1_1 = pos1 < n1
        from_s1_2 = pos2 < n1
        if from_s1_1 != from_s1_2 and lcp[i] > best_len:
            best_len = lcp[i]
            best_pos = sa[i]

    return combined[best_pos:best_pos + best_len]


def _sol_count_distinct(text):
    n = len(text)
    if n == 0:
        return 0
    sa = build_suffix_array(text)
    lcp = build_lcp_array(text, sa)
    return n * (n + 1) // 2 - sum(lcp)


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1
    print("\nExercise 1: Find All Occurrences")
    for fn in [find_all_occurrences, _sol_find_all_occurrences]:
        if fn is find_all_occurrences and fn("abc", "a") is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}('abcabcabc', 'abc')", fn("abcabcabc", "abc"), [0, 3, 6])
        check(f"{fn.__name__}('hello', 'xyz')", fn("hello", "xyz"), [])

    # Exercise 2
    print("\nExercise 2: Longest Repeated Substring")
    for fn in [longest_repeated, _sol_longest_repeated]:
        if fn is longest_repeated and fn("ab") is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}('abcabc')", fn("abcabc"), "abc")
        check(f"{fn.__name__}('abcd')", fn("abcd"), "")

    # Exercise 3
    print("\nExercise 3: Kasai LCP")
    text = "banana$"
    sa = build_suffix_array(text)
    expected_lcp = build_lcp_array(text, sa)
    for fn in [kasai_lcp, _sol_kasai_lcp]:
        if fn is kasai_lcp and fn(text, sa) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}('banana$')", fn(text, sa), expected_lcp)

    # Exercise 4
    print("\nExercise 4: Longest Common Substring")
    for fn in [longest_common_substring, _sol_longest_common_substring]:
        if fn is longest_common_substring and fn("a", "b") is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}('abcdef', 'bcdegh')", fn("abcdef", "bcdegh"), "bcde")

    # Exercise 5
    print("\nExercise 5: Count Distinct Substrings")
    for fn in [count_distinct, _sol_count_distinct]:
        if fn is count_distinct and fn("a") is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}('abc')", fn("abc"), 6)
        check(f"{fn.__name__}('aaa')", fn("aaa"), 3)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
