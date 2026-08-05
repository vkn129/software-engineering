"""
Day 116: 2D Dynamic Programming on grids.

Three grid problems with the SAME recurrence shape, different operators:
  1. Unique paths       — sum
  2. Paths with obstacles — sum with zero gate
  3. Minimum path sum    — min
"""

import math


# ---------------------------------------------------------------------------
# 1. Unique paths in an m x n grid
# ---------------------------------------------------------------------------
# dp[i][j] = dp[i-1][j] + dp[i][j-1].  Closed form C(m+n-2, m-1).

def unique_paths(m, n):
    """Distinct paths from (0,0) to (m-1, n-1) moving right or down."""
    dp = [[0] * n for _ in range(m)]
    for i in range(m):
        dp[i][0] = 1
    for j in range(n):
        dp[0][j] = 1
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]


def unique_paths_compressed(m, n):
    """O(n) space version."""
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]


def unique_paths_closed_form(m, n):
    """C(m+n-2, m-1) — combinatorial verification."""
    return math.comb(m + n - 2, m - 1)


# ---------------------------------------------------------------------------
# 2. Unique paths with obstacles
# ---------------------------------------------------------------------------

def unique_paths_obstacles(grid):
    """grid[i][j] = 1 means blocked. Return path count."""
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[m - 1][n - 1] == 1:
        return 0
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = 1
    for j in range(1, n):
        dp[0][j] = 0 if grid[0][j] == 1 else dp[0][j - 1]
    for i in range(1, m):
        dp[i][0] = 0 if grid[i][0] == 1 else dp[i - 1][0]
    for i in range(1, m):
        for j in range(1, n):
            if grid[i][j] == 1:
                dp[i][j] = 0
            else:
                dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]


# ---------------------------------------------------------------------------
# 3. Minimum path sum
# ---------------------------------------------------------------------------
# dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1]).

def min_path_sum(grid):
    """Min sum path from top-left to bottom-right moving right/down."""
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grid[0][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j - 1] + grid[0][j]
    for i in range(1, m):
        dp[i][0] = dp[i - 1][0] + grid[i][0]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i - 1][j], dp[i][j - 1])
    return dp[m - 1][n - 1]


def min_path_sum_with_trace(grid):
    """Return (cost, path_of_(i,j)_tuples)."""
    if not grid or not grid[0]:
        return 0, []
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    dp[0][0] = grid[0][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j - 1] + grid[0][j]
    for i in range(1, m):
        dp[i][0] = dp[i - 1][0] + grid[i][0]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = grid[i][j] + min(dp[i - 1][j], dp[i][j - 1])

    # Backtrace
    path = []
    i, j = m - 1, n - 1
    while (i, j) != (0, 0):
        path.append((i, j))
        if i == 0:
            j -= 1
        elif j == 0:
            i -= 1
        elif dp[i - 1][j] < dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    path.append((0, 0))
    return dp[m - 1][n - 1], list(reversed(path))


def min_path_sum_greedy_wrong(grid):
    """Greedy take-smaller-neighbor. Demonstrates failure on adversarial grids."""
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    i = j = 0
    total = grid[0][0]
    while (i, j) != (m - 1, n - 1):
        right = grid[i][j + 1] if j + 1 < n else math.inf
        down = grid[i + 1][j] if i + 1 < m else math.inf
        if right <= down:
            j += 1
            total += right
        else:
            i += 1
            total += down
    return total


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_unique_paths():
    print("=" * 60)
    print("DEMO 1: Unique Paths in m x n grid")
    print("=" * 60)
    print("\n m,n  | DP        | C(m+n-2, m-1)")
    print("-" * 40)
    for m, n in [(2, 2), (3, 3), (3, 7), (18, 18)]:
        a = unique_paths_compressed(m, n)
        b = unique_paths_closed_form(m, n)
        match = "OK" if a == b else "MISMATCH"
        print(f" {m},{n:<3} | {a:<9} | {b:<11} {match}")


def demo_obstacles():
    print("\n" + "=" * 60)
    print("DEMO 2: Paths with Obstacles")
    print("=" * 60)
    grid1 = [[0, 0, 0],
             [0, 1, 0],
             [0, 0, 0]]
    grid2 = [[0, 1],
             [0, 0]]
    grid3 = [[1, 0]]  # blocked start
    for g in (grid1, grid2, grid3):
        for row in g:
            print("  ", row)
        print(f"  paths = {unique_paths_obstacles(g)}\n")


def demo_min_path():
    print("\n" + "=" * 60)
    print("DEMO 3: Minimum Path Sum (and where greedy fails)")
    print("=" * 60)
    grids = [
        [[1, 3, 1],
         [1, 5, 1],
         [4, 2, 1]],
        [[1, 2, 3],
         [4, 5, 6]],
        [[1, 100, 1],
         [1, 100, 1],
         [1, 1, 1]],
    ]
    for g in grids:
        cost, path = min_path_sum_with_trace(g)
        greedy = min_path_sum_greedy_wrong(g)
        for row in g:
            print("  ", row)
        flag = "ok" if greedy == cost else f"WRONG ({greedy})"
        print(f"  optimal cost = {cost}  path = {path}  greedy = {flag}\n")


if __name__ == "__main__":
    demo_unique_paths()
    demo_obstacles()
    demo_min_path()
