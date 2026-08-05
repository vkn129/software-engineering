"""
Day 96 Practice: Hungarian Algorithm — Optimal Assignment

6 exercises: square minimization, square maximization, rectangular padding,
forbidden assignments, brute-force verification, and an MOT tracking task.
"""

from itertools import permutations

INF = float("inf")


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


def _hungarian(cost):
    """Internal solver (square, n_rows <= n_cols)."""
    n = len(cost)
    if n == 0:
        return 0, []
    m = len(cost[0])
    u = [0] * (n + 1)
    v = [0] * (m + 1)
    p = [0] * (m + 1)
    way = [0] * (m + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = -1
            for j in range(1, m + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while j0 != 0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    assignment = [-1] * n
    for j in range(1, m + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1
    total = sum(cost[i][assignment[i]] for i in range(n) if assignment[i] != -1)
    return total, assignment


# ===================================================================
# Exercise 1: Minimum-Cost Assignment (Square)
# ===================================================================

def min_cost_assignment(cost):
    """
    cost: n x n matrix, n >= 1. Return (total, assignment).
    """
    # TODO: call _hungarian
    pass


def _sol_min_cost_assignment(cost):
    return _hungarian(cost)


# ===================================================================
# Exercise 2: Maximum-Profit Assignment
# ===================================================================

def max_profit_assignment(profit):
    """
    Same shape as min_cost_assignment but maximize. Return (total, assignment).
    """
    # TODO: negate or subtract from max, then call _hungarian
    pass


def _sol_max_profit_assignment(profit):
    if not profit:
        return 0, []
    M = max(max(row) for row in profit)
    cost = [[M - x for x in row] for row in profit]
    _, assign = _hungarian(cost)
    total = sum(profit[i][assign[i]] for i in range(len(profit)) if assign[i] != -1)
    return total, assign


# ===================================================================
# Exercise 3: Rectangular Assignment
# ===================================================================
# When n_workers != n_jobs, pad the smaller dimension with zeros.

def rectangular_assignment(cost):
    """
    cost: rectangular matrix (n_workers x n_jobs). Return (total, assignment)
    of length n_workers; if n_workers > n_jobs, the extras are -1 (no job).
    """
    # TODO: pad to square with zeros, solve, strip padding
    pass


def _sol_rectangular_assignment(cost):
    if not cost or not cost[0]:
        return 0, []
    n = len(cost)
    m = len(cost[0])
    size = max(n, m)
    padded = [[0] * size for _ in range(size)]
    for i in range(n):
        for j in range(m):
            padded[i][j] = cost[i][j]
    _, assign = _hungarian(padded)
    # Truncate to n; mark assignments to dummy columns as -1
    result = [-1] * n
    total = 0
    for i in range(n):
        j = assign[i]
        if j < m:
            result[i] = j
            total += cost[i][j]
    return total, result


# ===================================================================
# Exercise 4: Brute-Force Verification (small n)
# ===================================================================

def brute_force_min_cost(cost):
    """For n <= 8, enumerate all permutations and return min total cost."""
    # TODO: iterate over permutations
    pass


def _sol_brute_force_min_cost(cost):
    n = len(cost)
    m = len(cost[0]) if cost else 0
    best = INF
    for perm in permutations(range(m), n):
        c = sum(cost[i][perm[i]] for i in range(n))
        best = min(best, c)
    return best


# ===================================================================
# Exercise 5: Forbidden Assignments
# ===================================================================
# Given a list of forbidden (worker, job) pairs, encode them as Big-M
# entries and solve. Return -1 if no feasible assignment exists.

def assignment_with_forbidden(cost, forbidden):
    """
    cost: n x n matrix
    forbidden: list of (worker, job) pairs that are illegal
    Return (total, assignment), or (-1, []) if no feasible assignment exists.
    """
    # TODO: copy cost, set forbidden entries to a big sentinel, then run.
    # Check if any final assignment uses a forbidden entry.
    pass


def _sol_assignment_with_forbidden(cost, forbidden):
    BIG = 10**9
    n = len(cost)
    c = [row[:] for row in cost]
    forbid_set = set(forbidden)
    for i, j in forbid_set:
        c[i][j] = BIG
    total, assign = _hungarian(c)
    # Check if any chosen edge was forbidden
    for i in range(n):
        if (i, assign[i]) in forbid_set:
            return -1, []
    return total, assign


# ===================================================================
# Exercise 6: Multi-Object Tracking (MOT) — frame-to-frame association
# ===================================================================
# Tracks have last known centroids (x, y). New detections also have (x, y).
# Cost = Euclidean distance squared. Find the minimum-total-distance match.

def mot_associate(tracks, detections):
    """
    tracks, detections: each is a list of (x, y) tuples (same length).
    Return: list `assign` where assign[i] = j means track i matches
    detection j.
    """
    # TODO: build cost matrix of squared distances, call min_cost_assignment
    pass


def _sol_mot_associate(tracks, detections):
    cost = [[(t[0] - d[0])**2 + (t[1] - d[1])**2 for d in detections] for t in tracks]
    _, assign = _hungarian(cost)
    return assign


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

    print("Exercise 1: Min-Cost Assignment (Square)")
    c = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    total, _ = try_or_sol("min_cost_assignment", c)
    check("3x3 min cost = 5", total, 5)
    c = [[1, 2], [4, 3]]
    total, _ = try_or_sol("min_cost_assignment", c)
    check("2x2", total, 4)

    print("\nExercise 2: Max-Profit Assignment")
    p = [[10, 5, 8], [3, 9, 4], [7, 6, 11]]
    total, _ = try_or_sol("max_profit_assignment", p)
    check("3x3 max", total, 30)  # 10+9+11
    p = [[1, 2], [3, 4]]
    total, _ = try_or_sol("max_profit_assignment", p)
    check("2x2 max", total, 5)  # 1+4 or 2+3 (both equal)

    print("\nExercise 3: Rectangular Assignment")
    c = [[9, 2, 7, 8], [6, 4, 3, 7]]  # 2 workers, 4 jobs
    total, assign = try_or_sol("rectangular_assignment", c)
    check("2x4 min total = 5", total, 5)  # 2 + 3
    c = [[1, 2], [3, 4], [5, 6]]  # 3 workers, 2 jobs (1 idle)
    total, assign = try_or_sol("rectangular_assignment", c)
    # 1 and 3 sit in the same column, so they can never both be chosen. The two
    # legal optima are (w0->j0)+(w1->j1) = 1+4 and (w1->j0)+(w0->j1) = 3+2 = 5.
    check("3x2 has idle worker",
          assign.count(-1) == 1 and total == 5, True)

    print("\nExercise 4: Brute-Force Verification")
    check("brute 3x3", try_or_sol("brute_force_min_cost",
          [[4, 1, 3], [2, 0, 5], [3, 2, 2]]), 5)
    check("brute matches hungarian",
          try_or_sol("brute_force_min_cost", [[7, 5, 11], [9, 14, 10], [13, 2, 4]]),
          _sol_min_cost_assignment([[7, 5, 11], [9, 14, 10], [13, 2, 4]])[0])

    print("\nExercise 5: Forbidden Assignments")
    c = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    # Forbid (0, 0): forces worker 0 off job 0
    total, assign = try_or_sol("assignment_with_forbidden", c, [(0, 0)])
    check("(0,0) avoided", assign != [] and assign[0] != 0, True)
    # Infeasible: forbid every job for worker 0
    total, assign = try_or_sol("assignment_with_forbidden", c, [(0, 0), (0, 1), (0, 2)])
    check("infeasible", total, -1)

    print("\nExercise 6: MOT Frame-to-Frame")
    tracks = [(0, 0), (10, 10), (5, 20)]
    detections = [(1, 0), (12, 9), (4, 21)]
    # Each track should match its near detection (same index)
    check("mot identity match", try_or_sol("mot_associate", tracks, detections),
          [0, 1, 2])

    # Shuffled order — Hungarian should still recover the right mapping
    tracks = [(5, 20), (0, 0), (10, 10)]
    detections = [(12, 9), (4, 21), (1, 0)]
    assign = try_or_sol("mot_associate", tracks, detections)
    # track 0 (5,20) -> detection 1 (4,21)
    # track 1 (0,0)  -> detection 2 (1,0)
    # track 2 (10,10) -> detection 0 (12,9)
    check("mot shuffled", assign, [1, 2, 0])

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
