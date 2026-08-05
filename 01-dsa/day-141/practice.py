"""
Day 141 Practice: Levenshtein Automaton

6 exercises. Implement TODOs, then run: python practice.py
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
# Exercise 1: Wagner-Fischer edit distance
# ---------------------------------------------------------------------------

def edit_distance(a, b):
    """Return Levenshtein distance between a and b."""
    # TODO: implement using DP
    pass


def _sol_edit_distance(a, b):
    m, n = len(a), len(b)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            cur[j] = min(cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + cost)
        prev = cur
    return prev[n]


# ---------------------------------------------------------------------------
# Exercise 2: DP column step
# ---------------------------------------------------------------------------

def step_column(prev, pattern, c, k):
    """
    Given previous DP column (tuple of len m+1), pattern P, input char c,
    edit cap k, return next column as a tuple. Cap every entry at k+1.
    """
    # TODO: implement
    pass


def _sol_step_column(prev, pattern, c, k):
    m = len(pattern)
    cap = k + 1
    nxt = [min(prev[0] + 1, cap)]
    for i in range(1, m + 1):
        match_cost = 0 if pattern[i - 1] == c else 1
        v = min(nxt[i - 1] + 1, prev[i] + 1, prev[i - 1] + match_cost)
        nxt.append(min(v, cap))
    return tuple(nxt)


# ---------------------------------------------------------------------------
# Exercise 3: Column-DP acceptance check
# ---------------------------------------------------------------------------

def within_distance_column_dp(pattern, candidate, k):
    """
    Use repeated step_column to decide if edit_distance(pattern, candidate) <= k.
    Early-exit when all entries exceed k.
    """
    # TODO: implement
    pass


def _sol_within_distance_column_dp(pattern, candidate, k):
    m = len(pattern)
    col = tuple(min(i, k + 1) for i in range(m + 1))
    for c in candidate:
        col = _sol_step_column(col, pattern, c, k)
        if min(col) > k:
            return False
    return col[-1] <= k


# ---------------------------------------------------------------------------
# Exercise 4: Fuzzy dictionary filter
# ---------------------------------------------------------------------------

def fuzzy_filter(pattern, words, k):
    """Return list of words from `words` within edit distance k of pattern.
    Preserve input order."""
    # TODO: implement
    pass


def _sol_fuzzy_filter(pattern, words, k):
    return [w for w in words if _sol_within_distance_column_dp(pattern, w, k)]


# ---------------------------------------------------------------------------
# Exercise 5: Hamming distance (substitutions only)
# ---------------------------------------------------------------------------

def hamming_distance(a, b):
    """Return number of positions where a and b differ. -1 if lengths differ."""
    # TODO: implement
    pass


def _sol_hamming_distance(a, b):
    if len(a) != len(b):
        return -1
    return sum(1 for x, y in zip(a, b) if x != y)


# ---------------------------------------------------------------------------
# Exercise 6: One-edit-away check (fast Levenshtein for k=1)
# ---------------------------------------------------------------------------

def one_edit_away(a, b):
    """Return True iff edit_distance(a, b) <= 1. O(len) using length pivot."""
    # TODO: implement without full DP
    pass


def _sol_one_edit_away(a, b):
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a  # ensure len(a) <= len(b)
    i = j = 0
    found = False
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            if found:
                return False
            found = True
            if len(a) == len(b):
                i += 1
                j += 1
            else:
                j += 1
        else:
            i += 1
            j += 1
    return True


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

    print("Exercise 1: edit_distance")
    check("kitten vs sitting", try_or_sol("edit_distance", "kitten", "sitting"), 3)
    check("empty vs abc", try_or_sol("edit_distance", "", "abc"), 3)
    check("same string", try_or_sol("edit_distance", "hello", "hello"), 0)
    check("flaw vs lawn", try_or_sol("edit_distance", "flaw", "lawn"), 2)

    print("\nExercise 2: step_column")
    # pattern='ab', k=1, initial col = (0,1,2) capped at 2
    col0 = (0, 1, 2)
    col1 = try_or_sol("step_column", col0, "ab", "a", 1)
    # After reading 'a': col[0]=1 (deleted 1 cand char), col[1]=0 (match), col[2]=1
    check("step on 'a'", col1, (1, 0, 1))
    col2 = try_or_sol("step_column", col1, "ab", "b", 1)
    check("step on 'b'", col2, (2, 1, 0))
    # mismatch char
    col_x = try_or_sol("step_column", col0, "ab", "x", 1)
    check("mismatch step caps at 2", col_x, (1, 1, 2))

    print("\nExercise 3: within_distance_column_dp")
    check("kitten/sitting k=3", try_or_sol("within_distance_column_dp", "kitten", "sitting", 3), True)
    check("kitten/sitting k=2", try_or_sol("within_distance_column_dp", "kitten", "sitting", 2), False)
    check("hello/hello k=0", try_or_sol("within_distance_column_dp", "hello", "hello", 0), True)
    check("hi/world k=2", try_or_sol("within_distance_column_dp", "hi", "world", 2), False)

    print("\nExercise 4: fuzzy_filter")
    words = ["cat", "bat", "rat", "car", "cab", "dog"]
    check("cat k=1", try_or_sol("fuzzy_filter", "cat", words, 1),
          ["cat", "bat", "rat", "car", "cab"])
    check("dog k=0", try_or_sol("fuzzy_filter", "dog", words, 0), ["dog"])

    print("\nExercise 5: hamming_distance")
    check("equal", try_or_sol("hamming_distance", "abc", "abc"), 0)
    check("two diffs", try_or_sol("hamming_distance", "abcd", "abef"), 2)
    check("len mismatch", try_or_sol("hamming_distance", "ab", "abc"), -1)

    print("\nExercise 6: one_edit_away")
    check("same", try_or_sol("one_edit_away", "pale", "pale"), True)
    check("substitute", try_or_sol("one_edit_away", "pale", "bale"), True)
    check("insert", try_or_sol("one_edit_away", "pale", "ple"), True)
    check("two edits", try_or_sol("one_edit_away", "pale", "bake"), False)
    check("len diff > 1", try_or_sol("one_edit_away", "pale", "pales!"), False)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
