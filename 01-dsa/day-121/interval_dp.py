"""
Day 121: Interval DP — From Scratch

Choose a split point within an interval; the optimal cost of [i, j]
depends on optimal costs of [i, k] and [k+1, j].

  1. Matrix Chain Multiplication — minimize scalar multiplications
     + reconstruction of optimal parenthesization
  2. Burst Balloons — reverse the question: "last to burst", not first
"""


# ---------------------------------------------------------------------------
# 1. Matrix Chain Multiplication
# ---------------------------------------------------------------------------

def matrix_chain_order(dims):
    """
    dims[i] is matrix A_i's row count (= A_{i-1}'s col count).
    n matrices means len(dims) == n + 1.

    Returns (min_ops, split_table) where split_table[i][j] is the
    optimal k to split the product A_i ... A_j.
    """
    n = len(dims) - 1
    if n <= 1:
        return 0, [[0] * n for _ in range(n)]

    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]

    # length-major
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = INF
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    split[i][j] = k

    return dp[0][n - 1], split


def matrix_chain_parens(dims, names=None):
    """
    Returns a string showing optimal parenthesization.
    names: list of matrix names (defaults to A1, A2, ...).
    """
    n = len(dims) - 1
    if n == 0:
        return ""
    if names is None:
        names = [f"A{i+1}" for i in range(n)]
    _, split = matrix_chain_order(dims)

    def build(i, j):
        if i == j:
            return names[i]
        k = split[i][j]
        left = build(i, k)
        right = build(k + 1, j)
        return f"({left} {right})"

    return build(0, n - 1)


# ---------------------------------------------------------------------------
# 2. Burst Balloons
# ---------------------------------------------------------------------------

def burst_balloons_max(nums):
    """
    Max coins by bursting balloons. Bursting i earns nums[i-1]*nums[i]*nums[i+1]
    (treating out-of-range as 1).

    State: dp[i][j] = max coins from bursting all balloons in [i, j]
                     where i, j are 1-indexed positions in padded array.
    Trick: k is the LAST balloon burst in [i, j].
    Then its neighbors at burst time are i-1 and j+1 (interval boundaries).
    """
    padded = [1] + list(nums) + [1]
    n = len(padded)
    dp = [[0] * n for _ in range(n)]

    # length-major over inner interval [i, j]
    for length in range(1, n - 1):
        for i in range(1, n - length):
            j = i + length - 1
            best = 0
            for k in range(i, j + 1):
                # k burst last in [i, j]; neighbors at that moment are i-1, j+1
                coins = padded[i - 1] * padded[k] * padded[j + 1]
                coins += dp[i][k - 1] + dp[k + 1][j]
                if coins > best:
                    best = coins
            dp[i][j] = best

    return dp[1][n - 2]


# ---------------------------------------------------------------------------
# 3. Bonus: Stone Merge (classic interval DP)
# ---------------------------------------------------------------------------

def stone_merge_min(stones):
    """
    n piles in a row. Merging two adjacent piles costs their sum.
    Continue until one pile. Minimize total cost.

    State: dp[i][j] = min cost to merge [i, j] into one pile.
    Cost of final merge = prefix_sum[j+1] - prefix_sum[i].
    """
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
                cost = dp[i][k] + dp[k + 1][j] + (prefix[j + 1] - prefix[i])
                if cost < dp[i][j]:
                    dp[i][j] = cost
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_mcm():
    print("=" * 60)
    print("DEMO 1: Matrix Chain Multiplication")
    print("=" * 60)

    # 4 matrices: 40x20, 20x30, 30x10, 10x30
    dims = [40, 20, 30, 10, 30]
    cost, _ = matrix_chain_order(dims)
    parens = matrix_chain_parens(dims)
    print(f"\n  dims = {dims}")
    print(f"  min scalar multiplications: {cost}")
    print(f"  optimal parenthesization:   {parens}")

    # Compare with naive left-to-right
    naive = 0
    for i in range(len(dims) - 2):
        naive += dims[0] * dims[i + 1] * dims[i + 2]
    print(f"  naive left-to-right cost:    {naive}")


def demo_burst():
    print("\n" + "=" * 60)
    print("DEMO 2: Burst Balloons")
    print("=" * 60)

    cases = [
        [3, 1, 5, 8],     # expected 167
        [1, 5],           # 10
        [7],              # 7
    ]
    for nums in cases:
        print(f"  nums = {nums}  ->  max coins = {burst_balloons_max(nums)}")


def demo_stone():
    print("\n" + "=" * 60)
    print("DEMO 3: Stone Merge (min cost)")
    print("=" * 60)
    for stones in [[4, 1, 1, 4], [3, 5, 1, 2, 6], [1, 2, 3]]:
        print(f"  stones = {stones}  ->  min cost = {stone_merge_min(stones)}")


if __name__ == "__main__":
    demo_mcm()
    demo_burst()
    demo_stone()
