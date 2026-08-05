"""
Day 115 Practice: 1D DP with Decisions.

6 exercises on min coins, ways to make change, and decoding.
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
# Exercise 1: Min coins
# ===================================================================
# Return min coins to make `amount`, or -1 if impossible. Unlimited coins.

def min_coins(coins, amount):
    """Min coins to sum to amount; -1 if impossible."""
    # TODO: implement bottom-up DP
    pass


def _sol_min_coins(coins, amount):
    INF = amount + 1
    dp = [INF] * (amount + 1)
    dp[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1


# ===================================================================
# Exercise 2: Count combinations summing to amount
# ===================================================================
# Each coin can be used any number of times. Order doesn't matter.

def count_combinations(coins, amount):
    """Number of distinct unordered combinations summing to amount."""
    # TODO: implement (outer loop coins, inner loop amounts)
    pass


def _sol_count_combinations(coins, amount):
    dp = [0] * (amount + 1)
    dp[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            dp[a] += dp[a - c]
    return dp[amount]


# ===================================================================
# Exercise 3: Decode Ways
# ===================================================================
# Digit string s, A=1..Z=26. Count distinct decodings.
# Leading zeros invalidate. dp[i] = ways for prefix of length i.

def decode_ways(s):
    """Number of decodings of digit string s."""
    # TODO: implement
    pass


def _sol_decode_ways(s):
    n = len(s)
    if n == 0 or s[0] == "0":
        return 0
    prev2, prev1 = 1, 1
    for i in range(2, n + 1):
        curr = 0
        if s[i - 1] != "0":
            curr += prev1
        pair = int(s[i - 2:i])
        if 10 <= pair <= 26:
            curr += prev2
        prev2, prev1 = prev1, curr
    return prev1


# ===================================================================
# Exercise 4: Perfect squares — min count summing to n
# ===================================================================
# Find min number of perfect squares (1, 4, 9, 16, ...) summing to n.
# Recurrence: dp[i] = 1 + min(dp[i - j*j]) for all j with j*j <= i.

def num_squares(n):
    """Min count of perfect squares summing to n."""
    # TODO: implement
    pass


def _sol_num_squares(n):
    if n <= 0:
        return 0
    dp = [n + 1] * (n + 1)
    dp[0] = 0
    j = 1
    squares = []
    while j * j <= n:
        squares.append(j * j)
        j += 1
    for i in range(1, n + 1):
        for sq in squares:
            if sq > i:
                break
            if dp[i - sq] + 1 < dp[i]:
                dp[i] = dp[i - sq] + 1
    return dp[n]


# ===================================================================
# Exercise 5: Word break (boolean)
# ===================================================================
# Can s be segmented as a sequence of dictionary words (with reuse)?
# dp[i] = True iff s[:i] can be segmented.
# dp[i] = OR over j<i of (dp[j] AND s[j:i] in dict).

def word_break(s, words):
    """True iff s can be segmented into dictionary words."""
    # TODO: implement
    pass


def _sol_word_break(s, words):
    word_set = set(words)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    return dp[n]


# ===================================================================
# Exercise 6: Integer break
# ===================================================================
# Split integer n (>= 2) into a sum of AT LEAST TWO positive integers.
# Maximize product of those parts.
# Recurrence: dp[i] = max over j in 1..i-1 of max(j*(i-j), j*dp[i-j]).
# (j*(i-j) = split into exactly 2 parts; j*dp[i-j] = split further.)

def integer_break(n):
    """Maximum product after splitting n into >= 2 positive parts."""
    # TODO: implement
    pass


def _sol_integer_break(n):
    if n < 2:
        return 0
    dp = [0] * (n + 1)
    for i in range(2, n + 1):
        best = 0
        for j in range(1, i):
            best = max(best, j * (i - j), j * dp[i - j])
        dp[i] = best
    return dp[n]


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

    print("Exercise 1: Min coins")
    check("[1,2,5], 11", try_or_sol("min_coins", [1, 2, 5], 11), 3)
    check("[1,3,4], 6 (greedy trap)", try_or_sol("min_coins", [1, 3, 4], 6), 2)
    check("[2], 3 impossible", try_or_sol("min_coins", [2], 3), -1)

    print("\nExercise 2: Count combinations")
    check("[1,2,5], 5", try_or_sol("count_combinations", [1, 2, 5], 5), 4)
    check("[2], 3", try_or_sol("count_combinations", [2], 3), 0)
    check("[10], 10", try_or_sol("count_combinations", [10], 10), 1)

    print("\nExercise 3: Decode ways")
    check("'12'", try_or_sol("decode_ways", "12"), 2)
    check("'226'", try_or_sol("decode_ways", "226"), 3)
    check("'06'", try_or_sol("decode_ways", "06"), 0)
    check("'11106'", try_or_sol("decode_ways", "11106"), 2)

    print("\nExercise 4: Perfect squares")
    check("12 -> 3 (4+4+4)", try_or_sol("num_squares", 12), 3)
    check("13 -> 2 (4+9)", try_or_sol("num_squares", 13), 2)
    check("1 -> 1", try_or_sol("num_squares", 1), 1)

    print("\nExercise 5: Word break")
    check("'leetcode'", try_or_sol("word_break", "leetcode", ["leet", "code"]), True)
    check("'applepenapple'", try_or_sol("word_break", "applepenapple", ["apple", "pen"]), True)
    check("'catsandog' fail", try_or_sol("word_break", "catsandog",
                                          ["cats", "dog", "sand", "and", "cat"]), False)

    print("\nExercise 6: Integer break")
    check("2 -> 1", try_or_sol("integer_break", 2), 1)
    check("10 -> 36 (3*3*4)", try_or_sol("integer_break", 10), 36)
    check("4 -> 4 (2*2)", try_or_sol("integer_break", 4), 4)

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
