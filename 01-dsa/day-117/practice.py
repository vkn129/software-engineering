"""
Day 117 Practice: Edit Distance and friends.

6 exercises on Levenshtein, variants, and applications.
Implement the TODO functions, then run: python practice.py
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
# Exercise 1: Levenshtein distance
# ===================================================================

def edit_distance(a, b):
    """Min edits (insert, delete, sub) to convert a to b."""
    # TODO: implement bottom-up DP
    pass


def _sol_edit_distance(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    return dp[n][m]


# ===================================================================
# Exercise 2: Edit distance with O(min(n,m)) space
# ===================================================================
# Use two rolling rows (or one row + temp) instead of full table.

def edit_distance_compressed(a, b):
    """Same as edit_distance but uses O(min(n,m)) extra space."""
    # TODO: implement
    pass


def _sol_edit_distance_compressed(a, b):
    if len(a) < len(b):
        a, b = b, a
    n, m = len(a), len(b)
    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [i] + [0] * m
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                curr[j] = prev[j - 1]
            else:
                curr[j] = 1 + min(prev[j], curr[j - 1], prev[j - 1])
        prev = curr
    return prev[m]


# ===================================================================
# Exercise 3: One-edit distance check
# ===================================================================
# Return True iff edit_distance(a, b) == 1. Cheaper than full DP:
# - if |len(a) - len(b)| > 1 -> False
# - if same length: exactly one substitution position
# - if differ by 1: exactly one insertion position

def is_one_edit(a, b):
    """True iff a and b differ by exactly one edit."""
    # TODO: implement in O(n) without full DP
    pass


def _sol_is_one_edit(a, b):
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a  # a is now shorter or same
    diffs = 0
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            if diffs == 1:
                return False
            diffs += 1
            if len(a) == len(b):
                i += 1
                j += 1
            else:
                j += 1  # insert in a / delete from b
        else:
            i += 1
            j += 1
    if j < len(b):
        diffs += 1
    return diffs == 1


# ===================================================================
# Exercise 4: Damerau-Levenshtein (with transposition)
# ===================================================================
# Like Levenshtein but adjacent transposition of two chars is one op.

def damerau_levenshtein(a, b):
    """Edit distance with adjacent transpose as a single op."""
    # TODO: implement
    pass


def _sol_damerau_levenshtein(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)
    return dp[n][m]


# ===================================================================
# Exercise 5: Delete-only distance (no substitutions)
# ===================================================================
# Min deletions in EITHER string to make them equal.
# Equivalent to: n + m - 2 * LCS(a, b).
# Direct DP:
#   dp[i][j] = 0 if i == 0 and j == 0
#   dp[i][0] = i, dp[0][j] = j
#   dp[i][j] = dp[i-1][j-1] if a[i-1] == b[j-1]
#            = 1 + min(dp[i-1][j], dp[i][j-1])

def min_deletions_to_equal(a, b):
    """Min deletions across both strings to make them equal."""
    # TODO: implement
    pass


def _sol_min_deletions_to_equal(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


# ===================================================================
# Exercise 6: Spell suggest from a small dictionary
# ===================================================================
# Return list of dictionary words within edit_distance <= max_distance,
# sorted by (distance, word).

def spell_suggest(word, dictionary, max_distance):
    """List of (distance, word) tuples sorted ascending, distance <= max."""
    # TODO: implement using edit_distance from above
    pass


def _sol_spell_suggest(word, dictionary, max_distance):
    out = []
    for w in dictionary:
        d = _sol_edit_distance(word, w)
        if d <= max_distance:
            out.append((d, w))
    out.sort()
    return out


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

    print("Exercise 1: Edit distance")
    check("kitten/sitting", try_or_sol("edit_distance", "kitten", "sitting"), 3)
    check("intention/execution", try_or_sol("edit_distance", "intention", "execution"), 5)
    check("empty/abc", try_or_sol("edit_distance", "", "abc"), 3)
    check("identical", try_or_sol("edit_distance", "same", "same"), 0)

    print("\nExercise 2: Edit distance compressed")
    check("flaw/lawn", try_or_sol("edit_distance_compressed", "flaw", "lawn"), 2)
    check("horse/ros", try_or_sol("edit_distance_compressed", "horse", "ros"), 3)
    check("empty/empty", try_or_sol("edit_distance_compressed", "", ""), 0)

    print("\nExercise 3: One-edit distance")
    check("'cat'/'cats'", try_or_sol("is_one_edit", "cat", "cats"), True)
    check("'cat'/'cut'", try_or_sol("is_one_edit", "cat", "cut"), True)
    check("'cat'/'cat'", try_or_sol("is_one_edit", "cat", "cat"), False)
    check("'cat'/'catsx'", try_or_sol("is_one_edit", "cat", "catsx"), False)
    check("'a'/'b'", try_or_sol("is_one_edit", "a", "b"), True)

    print("\nExercise 4: Damerau-Levenshtein")
    check("'teh'/'the'", try_or_sol("damerau_levenshtein", "teh", "the"), 1)
    check("'ca'/'ac'", try_or_sol("damerau_levenshtein", "ca", "ac"), 1)
    check("'abcd'/'acbd'", try_or_sol("damerau_levenshtein", "abcd", "acbd"), 1)

    print("\nExercise 5: Delete-only distance")
    check("'sea'/'eat'", try_or_sol("min_deletions_to_equal", "sea", "eat"), 2)
    check("'leetcode'/'etco'",
          try_or_sol("min_deletions_to_equal", "leetcode", "etco"), 4)
    check("equal strings", try_or_sol("min_deletions_to_equal", "abc", "abc"), 0)

    print("\nExercise 6: Spell suggest")
    dictionary = ["receive", "deceive", "perceive", "recover", "the", "then"]
    check("recieve d<=2",
          try_or_sol("spell_suggest", "recieve", dictionary, 2),
          [(2, "receive")])
    check("teh d<=2",
          try_or_sol("spell_suggest", "teh", dictionary, 2),
          [(2, "the"), (2, "then")])

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
