"""
Day 135: KMP (Knuth-Morris-Pratt) — From Scratch

Failure function (LPS array) preprocesses the pattern in O(m).
Matching phase scans text in O(n) — text pointer never moves back.
Worst-case O(n+m), adversary-safe (unlike Rabin-Karp).
"""

import time


# ---------------------------------------------------------------------------
# 1. Failure Function (LPS Array)
# ---------------------------------------------------------------------------

def build_failure(pattern):
    """
    fail[j] = length of the longest proper prefix of pattern[0..j]
              that is also a suffix of pattern[0..j].

    Time: O(m) amortized.
    """
    m = len(pattern)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        # Walk back through prior LPS lengths until we find a match
        # or hit 0. This is the recursive fall-through.
        while k > 0 and pattern[k] != pattern[i]:
            k = fail[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        fail[i] = k
    return fail


# ---------------------------------------------------------------------------
# 2. KMP Search
# ---------------------------------------------------------------------------

def kmp_search(text, pattern):
    """
    Find all start positions of pattern in text. O(n + m).
    """
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    if m > n:
        return []

    fail = build_failure(pattern)
    matches = []
    j = 0
    for i in range(n):
        # On mismatch, fall back through the failure chain.
        while j > 0 and pattern[j] != text[i]:
            j = fail[j - 1]
        if pattern[j] == text[i]:
            j += 1
        if j == m:
            matches.append(i - m + 1)
            j = fail[j - 1]  # set up to find next (possibly overlapping) match
    return matches


# ---------------------------------------------------------------------------
# 3. Naive Search (for comparison)
# ---------------------------------------------------------------------------

def naive_search(text, pattern):
    """O(n*m) — for benchmarking against KMP."""
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    matches = []
    for i in range(n - m + 1):
        k = 0
        while k < m and text[i + k] == pattern[k]:
            k += 1
        if k == m:
            matches.append(i)
    return matches


# ---------------------------------------------------------------------------
# 4. KMP Automaton (full DFA — no while loop in match phase)
# ---------------------------------------------------------------------------

def build_kmp_automaton(pattern, alphabet):
    """
    Convert failure function into a DFA: delta[state][char] = next state.
    O(m * |alphabet|) space and time to build.
    Match phase becomes truly O(n) per character — one table lookup.
    """
    m = len(pattern)
    delta = [{c: 0 for c in alphabet} for _ in range(m + 1)]
    fail = build_failure(pattern) if m > 0 else []

    for j in range(m + 1):
        for c in alphabet:
            if j < m and pattern[j] == c:
                delta[j][c] = j + 1
            elif j == 0:
                delta[j][c] = 0
            else:
                # Same as KMP fall-through, but precomputed.
                delta[j][c] = delta[fail[j - 1]][c]
    return delta


def automaton_search(text, pattern, alphabet):
    """Use precomputed DFA for searching. Per-char: 1 dict lookup."""
    delta = build_kmp_automaton(pattern, alphabet)
    m = len(pattern)
    state = 0
    matches = []
    for i, c in enumerate(text):
        if c in delta[state]:
            state = delta[state][c]
        else:
            state = 0
        if state == m:
            matches.append(i - m + 1)
    return matches


# ---------------------------------------------------------------------------
# 5. Period of a String (via KMP)
# ---------------------------------------------------------------------------

def smallest_period(s):
    """
    Smallest p such that s = (prefix of length p) repeated.
    If s has no proper period, returns len(s).

    Fact: the smallest period of s equals m - fail[m-1] IF (m - fail[m-1])
    divides m. Else the string isn't a repetition; period == m.
    """
    if not s:
        return 0
    fail = build_failure(s)
    m = len(s)
    p = m - fail[m - 1]
    return p if m % p == 0 else m


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_failure_function():
    print("=" * 65)
    print("DEMO 1: Failure Function Construction")
    print("=" * 65)
    for p in ["ababaca", "aaaa", "abcdef", "abababab", "abcabd"]:
        f = build_failure(p)
        print(f"  pattern = {p!r:12s}  fail = {f}")


def demo_search():
    print("\n" + "=" * 65)
    print("DEMO 2: KMP Search")
    print("=" * 65)
    text = "abababcabababcab"
    pat = "ababc"
    print(f"  text:    {text!r}")
    print(f"  pattern: {pat!r}")
    print(f"  kmp:     {kmp_search(text, pat)}")
    print(f"  naive:   {naive_search(text, pat)}")


def demo_catastrophic_input():
    print("\n" + "=" * 65)
    print("DEMO 3: Where Naive Catastrophically Fails")
    print("=" * 65)
    # Naive's worst case: long run of matches, then mismatch at end.
    text = "a" * 50000 + "b"
    pat = "a" * 100 + "b"

    t0 = time.perf_counter()
    naive_search(text, pat)
    naive_t = time.perf_counter() - t0

    t0 = time.perf_counter()
    kmp_search(text, pat)
    kmp_t = time.perf_counter() - t0

    print(f"  text: a^50000 + b, pattern: a^100 + b")
    print(f"  naive: {naive_t:.4f}s")
    print(f"  kmp:   {kmp_t:.4f}s")
    print(f"  speedup: {naive_t / kmp_t:.1f}x")


def demo_automaton():
    print("\n" + "=" * 65)
    print("DEMO 4: KMP Automaton (Full DFA)")
    print("=" * 65)
    pat = "abab"
    alphabet = set("abc")
    delta = build_kmp_automaton(pat, alphabet)
    print(f"  pattern: {pat!r}")
    print(f"  DFA transitions:")
    for state, trans in enumerate(delta):
        print(f"    state {state}: {trans}")
    print(f"  search 'cababab' -> {automaton_search('cababab', pat, alphabet)}")


def demo_periods():
    print("\n" + "=" * 65)
    print("DEMO 5: Smallest Period via KMP")
    print("=" * 65)
    for s in ["abcabcabc", "abab", "aaaa", "hello", "abcabd", ""]:
        print(f"  {s!r:12s}  smallest period: {smallest_period(s)}")


if __name__ == "__main__":
    demo_failure_function()
    demo_search()
    demo_catastrophic_input()
    demo_automaton()
    demo_periods()
