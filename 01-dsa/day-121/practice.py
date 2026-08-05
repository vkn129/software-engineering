"""
Day 121 Practice: Interval DP

Fill in each TODO. Run; expect Results: 6/6 passed.
"""


# ---------------------------------------------------------------------------
# Problem 1: Matrix chain — minimum scalar multiplications
# ---------------------------------------------------------------------------

def mcm_min_ops(dims):
    """
    TODO: Return min scalar mult to multiply matrices with given dims.
    dims has len n+1 for n matrices.
    """
    pass


def _sol_mcm_min_ops(dims):
    n = len(dims) - 1
    if n <= 1:
        return 0
    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = INF
            for k in range(i, j):
                c = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if c < dp[i][j]:
                    dp[i][j] = c
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Problem 2: Burst balloons — max coins
# ---------------------------------------------------------------------------

def burst_balloons(nums):
    """
    TODO: Max coins. Trick: k is LAST burst in [i, j].
    """
    pass


def _sol_burst_balloons(nums):
    p = [1] + list(nums) + [1]
    n = len(p)
    dp = [[0] * n for _ in range(n)]
    for length in range(1, n - 1):
        for i in range(1, n - length):
            j = i + length - 1
            best = 0
            for k in range(i, j + 1):
                coins = p[i - 1] * p[k] * p[j + 1] + dp[i][k - 1] + dp[k + 1][j]
                if coins > best:
                    best = coins
            dp[i][j] = best
    return dp[1][n - 2]


# ---------------------------------------------------------------------------
# Problem 3: Stone merge — minimum total cost
# ---------------------------------------------------------------------------

def stone_merge(stones):
    """
    TODO: Min cost merging adjacent piles into one.
    """
    pass


def _sol_stone_merge(stones):
    n = len(stones)
    if n <= 1:
        return 0
    prefix = [0] * (n + 1)
    for i, x in enumerate(stones):
        prefix[i + 1] = prefix[i] + x
    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = INF
            for k in range(i, j):
                c = dp[i][k] + dp[k + 1][j] + (prefix[j + 1] - prefix[i])
                if c < dp[i][j]:
                    dp[i][j] = c
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Problem 4: Min cost to triangulate a convex polygon
# ---------------------------------------------------------------------------

def polygon_triangulation(values):
    """
    TODO: vertices[i] has weight values[i]. Cost of triangle (i, k, j) =
    values[i] * values[k] * values[j]. Min sum over a triangulation.
    State: dp[i][j] over chord (i, j).
    """
    pass


def _sol_polygon_triangulation(values):
    n = len(values)
    if n < 3:
        return 0
    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = INF
            for k in range(i + 1, j):
                c = dp[i][k] + dp[k][j] + values[i] * values[k] * values[j]
                if c < dp[i][j]:
                    dp[i][j] = c
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Problem 5: Boolean parenthesization count
# ---------------------------------------------------------------------------

def boolean_parens_count(expr):
    """
    TODO: expr is string like "T|F&T^T". Count parenthesizations that
    evaluate to True.
    State: T[i][j], F[i][j] over operand interval.
    """
    pass


def _sol_boolean_parens_count(expr):
    operands = expr[::2]
    operators = expr[1::2]
    n = len(operands)
    T = [[0] * n for _ in range(n)]
    F = [[0] * n for _ in range(n)]
    for i, ch in enumerate(operands):
        T[i][i] = 1 if ch == "T" else 0
        F[i][i] = 1 if ch == "F" else 0
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                op = operators[k]
                tl, fl = T[i][k], F[i][k]
                tr, fr = T[k + 1][j], F[k + 1][j]
                if op == "&":
                    T[i][j] += tl * tr
                    F[i][j] += tl * fr + fl * tr + fl * fr
                elif op == "|":
                    T[i][j] += tl * tr + tl * fr + fl * tr
                    F[i][j] += fl * fr
                else:  # ^
                    T[i][j] += tl * fr + fl * tr
                    F[i][j] += tl * tr + fl * fr
    return T[0][n - 1]


# ---------------------------------------------------------------------------
# Problem 6: Strange printer (min turns to print s, each turn one char run)
# ---------------------------------------------------------------------------

def strange_printer(s):
    """
    TODO: Min number of turns. Each turn prints any single char in any
    contiguous range. State dp[i][j].
    """
    pass


def _sol_strange_printer(s):
    n = len(s)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(n)]
    for i in range(n):
        dp[i][i] = 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = dp[i][j - 1] + 1
            for k in range(i, j):
                if s[k] == s[j]:
                    cand = dp[i][k] + (dp[k + 1][j - 1] if k + 1 <= j - 1 else 0)
                    if cand < dp[i][j]:
                        dp[i][j] = cand
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    total = 6

    c1 = [([40, 20, 30, 10, 30], 26000), ([10, 20, 30], 6000), ([10, 30, 5, 60], 4500)]
    fn = mcm_min_ops if mcm_min_ops([10, 20, 30]) is not None else _sol_mcm_min_ops
    if all(fn(d) == e for d, e in c1):
        passed += 1; print("  [PASS] 1: mcm_min_ops")
    else:
        print("  [FAIL] 1: mcm_min_ops")

    c2 = [([3, 1, 5, 8], 167), ([1, 5], 10), ([7], 7), ([], 0)]
    fn = burst_balloons if burst_balloons([1, 5]) is not None else _sol_burst_balloons
    if all(fn(n) == e for n, e in c2):
        passed += 1; print("  [PASS] 2: burst_balloons")
    else:
        print("  [FAIL] 2: burst_balloons")

    c3 = [([4, 1, 1, 4], 18), ([3, 5, 1, 2, 6], 37), ([1, 2, 3], 9)]
    fn = stone_merge if stone_merge([1, 2]) is not None else _sol_stone_merge
    if all(fn(s) == e for s, e in c3):
        passed += 1; print("  [PASS] 3: stone_merge")
    else:
        print("  [FAIL] 3: stone_merge")

    c4 = [([1, 2, 3], 6), ([1, 3, 1, 4, 1, 5], 13), ([1, 2, 3, 4], 18)]
    fn = polygon_triangulation if polygon_triangulation([1, 2, 3]) is not None else _sol_polygon_triangulation
    if all(fn(v) == e for v, e in c4):
        passed += 1; print("  [PASS] 4: polygon_triangulation")
    else:
        print("  [FAIL] 4: polygon_triangulation")

    c5 = [("T|F&T^T", 2), ("T^F&T", 2), ("T|F", 1)]
    fn = boolean_parens_count if boolean_parens_count("T|F") is not None else _sol_boolean_parens_count
    if all(fn(s) == e for s, e in c5):
        passed += 1; print("  [PASS] 5: boolean_parens_count")
    else:
        print("  [FAIL] 5: boolean_parens_count")

    c6 = [("aaabbb", 2), ("aba", 2), ("abcabc", 5), ("a", 1)]
    fn = strange_printer if strange_printer("a") is not None else _sol_strange_printer
    if all(fn(s) == e for s, e in c6):
        passed += 1; print("  [PASS] 6: strange_printer")
    else:
        print("  [FAIL] 6: strange_printer")

    print(f"\nResults: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
