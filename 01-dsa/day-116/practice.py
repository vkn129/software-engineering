"""
Day 116 Practice: 2D Dynamic Programming.

6 exercises across path counting and min path optimization.
Implement the TODO functions, then run: python practice.py
"""

import math


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Unique paths in m x n grid (right/down only)
# ===================================================================

def unique_paths(m, n):
    """Count paths from (0,0) to (m-1, n-1)."""
    # TODO: implement bottom-up DP
    pass


def _sol_unique_paths(m, n):
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[n - 1]


# ===================================================================
# Exercise 2: Unique paths with obstacles
# ===================================================================
# grid[i][j] = 1 means blocked. Return 0 if start or end is blocked.

def unique_paths_obstacles(grid):
    """Number of paths in a grid with obstacles."""
    # TODO: implement
    pass


def _sol_unique_paths_obstacles(grid):
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    if grid[0][0] == 1 or grid[m - 1][n - 1] == 1:
        return 0
    dp = [0] * n
    dp[0] = 1
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[n - 1]


# ===================================================================
# Exercise 3: Minimum path sum
# ===================================================================
# Move right or down; minimize sum of cell values.

def min_path_sum(grid):
    """Min sum from top-left to bottom-right."""
    # TODO: implement
    pass


def _sol_min_path_sum(grid):
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    dp[0] = grid[0][0]
    for j in range(1, n):
        dp[j] = dp[j - 1] + grid[0][j]
    for i in range(1, m):
        dp[0] += grid[i][0]
        for j in range(1, n):
            dp[j] = grid[i][j] + min(dp[j], dp[j - 1])
    return dp[n - 1]


# ===================================================================
# Exercise 4: Triangle minimum path sum
# ===================================================================
# Given a triangle (list of lists), at each step move to row+1 either same
# index or index+1. Return min top-to-bottom path sum.
# Recurrence (top-down or bottom-up). Bottom-up:
#   dp[j] = triangle[i][j] + min(dp[j], dp[j+1])  walking from last row up.

def triangle_min_path(triangle):
    """Min path sum from top to bottom of the triangle."""
    # TODO: implement
    pass


def _sol_triangle_min_path(triangle):
    if not triangle:
        return 0
    dp = list(triangle[-1])
    for i in range(len(triangle) - 2, -1, -1):
        for j in range(len(triangle[i])):
            dp[j] = triangle[i][j] + min(dp[j], dp[j + 1])
    return dp[0]


# ===================================================================
# Exercise 5: Maximal square of 1s
# ===================================================================
# Given a binary grid, find the side length of the largest all-1 square.
# Recurrence:
#   dp[i][j] = 0 if grid[i][j] == 0
#            = 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]) otherwise
# Track max as you fill. Edges initialise from grid directly.

def maximal_square(grid):
    """Side length of the largest all-1 square submatrix."""
    # TODO: implement
    pass


def _sol_maximal_square(grid):
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j - 1], dp[i - 1][j], dp[i][j - 1])
                best = max(best, dp[i][j])
    return best


# ===================================================================
# Exercise 6: Dungeon game (min initial health)
# ===================================================================
# Knight at top-left must reach bottom-right. Cell value is health delta
# (negative = damage). Health must remain >= 1 at every step. Return min
# starting health.
# Solve right-to-left, bottom-to-top:
#   need[i][j] = max(1, min(need[i+1][j], need[i][j+1]) - dungeon[i][j])
# Answer = need[0][0].

def min_initial_health(dungeon):
    """Minimum starting health required."""
    # TODO: implement
    pass


def _sol_min_initial_health(dungeon):
    if not dungeon or not dungeon[0]:
        return 1
    m, n = len(dungeon), len(dungeon[0])
    INF = math.inf
    need = [[INF] * (n + 1) for _ in range(m + 1)]
    need[m][n - 1] = need[m - 1][n] = 1
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            min_next = min(need[i + 1][j], need[i][j + 1])
            need[i][j] = max(1, min_next - dungeon[i][j])
    return need[0][0]


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

    print("Exercise 1: Unique paths")
    check("3x7 -> 28", try_or_sol("unique_paths", 3, 7), 28)
    check("3x3 -> 6", try_or_sol("unique_paths", 3, 3), 6)
    check("1x1 -> 1", try_or_sol("unique_paths", 1, 1), 1)

    print("\nExercise 2: Paths with obstacles")
    g1 = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    check("3x3 with center block", try_or_sol("unique_paths_obstacles", g1), 2)
    g2 = [[1]]
    check("start blocked", try_or_sol("unique_paths_obstacles", g2), 0)
    g3 = [[0, 0], [0, 0]]
    check("2x2 open", try_or_sol("unique_paths_obstacles", g3), 2)

    print("\nExercise 3: Min path sum")
    g4 = [[1, 3, 1], [1, 5, 1], [4, 2, 1]]
    check("classic 3x3", try_or_sol("min_path_sum", g4), 7)
    check("single cell", try_or_sol("min_path_sum", [[5]]), 5)
    check("row", try_or_sol("min_path_sum", [[1, 2, 3]]), 6)

    print("\nExercise 4: Triangle min path")
    t = [[2], [3, 4], [6, 5, 7], [4, 1, 8, 3]]
    check("classic triangle", try_or_sol("triangle_min_path", t), 11)
    check("single row", try_or_sol("triangle_min_path", [[7]]), 7)
    check("two rows", try_or_sol("triangle_min_path", [[1], [2, 3]]), 3)

    print("\nExercise 5: Maximal square")
    g5 = [[1, 0, 1, 0, 0],
          [1, 0, 1, 1, 1],
          [1, 1, 1, 1, 1],
          [1, 0, 0, 1, 0]]
    check("classic", try_or_sol("maximal_square", g5), 2)
    check("all zeros", try_or_sol("maximal_square", [[0, 0], [0, 0]]), 0)
    check("all ones", try_or_sol("maximal_square", [[1, 1], [1, 1]]), 2)

    print("\nExercise 6: Dungeon game")
    d = [[-2, -3, 3], [-5, -10, 1], [10, 30, -5]]
    check("classic dungeon", try_or_sol("min_initial_health", d), 7)
    check("all positive", try_or_sol("min_initial_health", [[1, 2], [3, 4]]), 1)
    check("single negative", try_or_sol("min_initial_health", [[-5]]), 6)

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
