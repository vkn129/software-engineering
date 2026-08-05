"""
Day 118 Practice: LCS, LIS, and related sequence DPs.

6 exercises. Implement the TODO functions, then run: python practice.py
"""

from bisect import bisect_left, bisect_right


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: LCS length
# ===================================================================

def lcs_length(a, b):
    """Length of longest common subsequence of a and b."""
    # TODO: implement bottom-up DP
    pass


def _sol_lcs_length(a, b):
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


# ===================================================================
# Exercise 2: LIS length via O(n^2) DP
# ===================================================================
# Strictly increasing.

def lis_length_n2(a):
    """LIS length using O(n^2) DP."""
    # TODO: implement
    pass


def _sol_lis_length_n2(a):
    n = len(a)
    if n == 0:
        return 0
    dp = [1] * n
    for i in range(1, n):
        for j in range(i):
            if a[j] < a[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


# ===================================================================
# Exercise 3: LIS length via patience sort O(n log n)
# ===================================================================
# Use bisect_left for strictly increasing.

def lis_length_nlogn(a):
    """LIS length in O(n log n)."""
    # TODO: implement using patience sort
    pass


def _sol_lis_length_nlogn(a):
    tails = []
    for x in a:
        pos = bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)


# ===================================================================
# Exercise 4: Longest non-decreasing subsequence O(n log n)
# ===================================================================
# Same as LIS but ties are allowed (a[j] <= a[i]). Use bisect_RIGHT.

def lnds_length(a):
    """Length of longest non-decreasing subsequence."""
    # TODO: implement
    pass


def _sol_lnds_length(a):
    tails = []
    for x in a:
        pos = bisect_right(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)


# ===================================================================
# Exercise 5: Longest common substring (contiguous)
# ===================================================================
# Different from LCS — contiguous required.
# Recurrence:
#   dp[i][j] = dp[i-1][j-1] + 1 if a[i-1] == b[j-1] else 0.
# Answer = max over the table.

def longest_common_substring(a, b):
    """Length of the longest contiguous substring shared by a and b."""
    # TODO: implement
    pass


def _sol_longest_common_substring(a, b):
    n, m = len(a), len(b)
    if n == 0 or m == 0:
        return 0
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    best = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]
    return best


# ===================================================================
# Exercise 6: Number of LIS
# ===================================================================
# Count distinct LIS in a (by their picked-index sequences, not by values).
# Use parallel arrays: length[i] = LIS ending at i, count[i] = #LIS ending at i.
# Transitions:
#   for j < i with a[j] < a[i]:
#     if length[j] + 1 > length[i]: length[i] = length[j]+1; count[i] = count[j]
#     elif length[j] + 1 == length[i]: count[i] += count[j]
# answer = sum(count[i] for i where length[i] == max_length)

def number_of_lis(a):
    """Count number of distinct LIS (by chosen index sequences)."""
    # TODO: implement
    pass


def _sol_number_of_lis(a):
    n = len(a)
    if n == 0:
        return 0
    length = [1] * n
    count = [1] * n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]:
                if length[j] + 1 > length[i]:
                    length[i] = length[j] + 1
                    count[i] = count[j]
                elif length[j] + 1 == length[i]:
                    count[i] += count[j]
    max_len = max(length)
    return sum(c for c, l in zip(count, length) if l == max_len)


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

    print("Exercise 1: LCS length")
    check("ABCBDAB/BDCAB", try_or_sol("lcs_length", "ABCBDAB", "BDCAB"), 4)
    check("AGGTAB/GXTXAYB", try_or_sol("lcs_length", "AGGTAB", "GXTXAYB"), 4)
    check("disjoint", try_or_sol("lcs_length", "abc", "xyz"), 0)
    check("identical", try_or_sol("lcs_length", "abcd", "abcd"), 4)

    print("\nExercise 2: LIS O(n^2)")
    check("classic", try_or_sol("lis_length_n2", [10, 9, 2, 5, 3, 7, 101, 18]), 4)
    check("all equal", try_or_sol("lis_length_n2", [3, 3, 3, 3]), 1)
    check("strictly increasing", try_or_sol("lis_length_n2", [1, 2, 3, 4, 5]), 5)
    check("empty", try_or_sol("lis_length_n2", []), 0)

    print("\nExercise 3: LIS O(n log n)")
    check("classic", try_or_sol("lis_length_nlogn", [10, 9, 2, 5, 3, 7, 101, 18]), 4)
    check("descending", try_or_sol("lis_length_nlogn", [5, 4, 3, 2, 1]), 1)
    check("mixed", try_or_sol("lis_length_nlogn", [3, 1, 4, 1, 5, 9, 2, 6]), 4)

    print("\nExercise 4: Longest non-decreasing")
    check("plateau", try_or_sol("lnds_length", [3, 3, 3, 3]), 4)
    check("classic non-strict",
          try_or_sol("lnds_length", [1, 2, 2, 3, 3, 4]), 6)
    check("descending", try_or_sol("lnds_length", [5, 4, 3, 2]), 1)

    print("\nExercise 5: Longest common substring")
    check("ABABC/BABCA",
          try_or_sol("longest_common_substring", "ABABC", "BABCA"), 4)
    check("disjoint",
          try_or_sol("longest_common_substring", "abc", "xyz"), 0)
    check("identical",
          try_or_sol("longest_common_substring", "abcd", "abcd"), 4)

    print("\nExercise 6: Number of LIS")
    check("[1,3,5,4,7] -> 2",
          try_or_sol("number_of_lis", [1, 3, 5, 4, 7]), 2)
    check("[2,2,2,2,2] -> 5", try_or_sol("number_of_lis", [2, 2, 2, 2, 2]), 5)
    check("[1,2,4,3,5,4,7,2] -> 3",
          try_or_sol("number_of_lis", [1, 2, 4, 3, 5, 4, 7, 2]), 3)

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
