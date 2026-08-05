"""
Day 96: Hungarian Algorithm — Optimal Assignment

Implements the compact O(n^3) variant: for each row, run Dijkstra-like
shortest-augmenting-path on reduced costs, update potentials.

Works on rectangular matrices via internal padding.
"""

import math


INF = float("inf")


# ---------------------------------------------------------------------------
# 1. Hungarian algorithm (Jonker-Volgenant style — clean O(n^3))
# ---------------------------------------------------------------------------

def hungarian(cost):
    """
    cost: 2D list of nonnegative numbers, n_rows rows, n_cols columns.
          n_rows <= n_cols (algorithm assigns every row).
    Returns: (total_cost, assignment) where assignment[i] = j means row i
             is matched to column j.

    Time: O(n_rows^2 * n_cols).
    """
    n = len(cost)
    if n == 0:
        return 0, []
    m = len(cost[0])
    assert n <= m, "Need at least as many columns as rows; pad if needed."

    # Potentials
    u = [0] * (n + 1)   # row potentials (1-indexed conceptually)
    v = [0] * (m + 1)   # col potentials
    p = [0] * (m + 1)   # p[j] = row currently assigned to column j (or 0)
    way = [0] * (m + 1) # backpointer: way[j] = previous column on path

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [INF] * (m + 1)
        used = [False] * (m + 1)
        # Repeatedly find next column to extend tree
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = INF
            j1 = -1
            for j in range(1, m + 1):
                if not used[j]:
                    # Reduced cost from row i0 to column j-1
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            # Update potentials
            for j in range(m + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        # Augment along the path
        while j0 != 0:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1

    # Build row-to-column assignment
    assignment = [-1] * n
    for j in range(1, m + 1):
        if p[j] != 0:
            assignment[p[j] - 1] = j - 1

    total = sum(cost[i][assignment[i]] for i in range(n) if assignment[i] != -1)
    return total, assignment


# ---------------------------------------------------------------------------
# 2. Helpers
# ---------------------------------------------------------------------------

def hungarian_max(profit):
    """
    Maximize profit instead of minimize cost. Negates internally.
    Returns (max_profit, assignment).
    """
    if not profit:
        return 0, []
    M = max(max(row) for row in profit)
    cost = [[M - x for x in row] for row in profit]
    _, assignment = hungarian(cost)
    total = sum(profit[i][assignment[i]] for i in range(len(profit)) if assignment[i] != -1)
    return total, assignment


def pad_square(matrix, fill=0):
    """
    Pad a rectangular matrix to square with `fill` entries. Useful when
    workers != jobs.
    """
    if not matrix:
        return []
    n = len(matrix)
    m = len(matrix[0])
    size = max(n, m)
    padded = [[fill] * size for _ in range(size)]
    for i in range(n):
        for j in range(m):
            padded[i][j] = matrix[i][j]
    return padded


# ---------------------------------------------------------------------------
# 3. Brute-force reference (for tests)
# ---------------------------------------------------------------------------

def brute_force_assignment(cost):
    """Used for verification on small n."""
    from itertools import permutations
    n = len(cost)
    best = INF
    best_perm = None
    for perm in permutations(range(len(cost[0])), n):
        c = sum(cost[i][perm[i]] for i in range(n))
        if c < best:
            best = c
            best_perm = perm
    return best, list(best_perm)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 65)
    print("DEMO 1: Basic Assignment")
    print("=" * 65)
    # 3 workers, 3 jobs
    # rows = workers, cols = jobs
    cost = [
        [4, 1, 3],
        [2, 0, 5],
        [3, 2, 2],
    ]
    total, assign = hungarian(cost)
    print(f"  Cost matrix: {cost}")
    print(f"  Min total cost: {total}")
    print(f"  Assignment: worker -> job: {list(enumerate(assign))}")
    print(f"  Brute force: {brute_force_assignment(cost)}")


def demo_max_profit():
    print("\n" + "=" * 65)
    print("DEMO 2: Maximize Profit Variant")
    print("=" * 65)
    profit = [
        [10, 5, 8],
        [3, 9, 4],
        [7, 6, 11],
    ]
    total, assign = hungarian_max(profit)
    print(f"  Profit matrix: {profit}")
    print(f"  Max total profit: {total}")
    print(f"  Assignment: {list(enumerate(assign))}")


def demo_rectangular():
    print("\n" + "=" * 65)
    print("DEMO 3: Rectangular — Fewer Workers Than Jobs")
    print("=" * 65)
    # 2 workers, 4 jobs — workers will each take 1 job, 2 jobs go undone.
    cost = [
        [9, 2, 7, 8],
        [6, 4, 3, 7],
    ]
    total, assign = hungarian(cost)
    print(f"  Cost: {cost}")
    print(f"  Min total: {total}")
    print(f"  Worker 0 -> job {assign[0]}, Worker 1 -> job {assign[1]}")


def demo_forbidden():
    print("\n" + "=" * 65)
    print("DEMO 4: Forbidden Assignments via Big-M")
    print("=" * 65)
    BIG = 10**6
    # Worker 0 CANNOT do job 0 (e.g., conflict-of-interest)
    cost = [
        [BIG, 4, 5],
        [2,   3, 6],
        [4,   5, 2],
    ]
    total, assign = hungarian(cost)
    print(f"  Min cost: {total} (would be lower without the forbidden pair)")
    print(f"  Assignment: {list(enumerate(assign))}")
    print(f"  Worker 0 forbidden from job 0: did we avoid it? "
          f"{assign[0] != 0}")


def demo_mot_tracking():
    print("\n" + "=" * 65)
    print("DEMO 5: Multi-Object Tracking — frame-to-frame data association")
    print("=" * 65)
    # 3 tracks, 3 detections; cost = squared distance between centroids
    tracks = [(0, 0), (10, 10), (5, 20)]
    detections = [(1, 0), (12, 9), (4, 21)]
    cost = [[(t[0] - d[0])**2 + (t[1] - d[1])**2 for d in detections] for t in tracks]
    total, assign = hungarian(cost)
    print(f"  Tracks:     {tracks}")
    print(f"  Detections: {detections}")
    print(f"  Cost matrix: {cost}")
    print(f"  Optimal: total squared dist = {total}")
    for i, j in enumerate(assign):
        print(f"    Track {i} {tracks[i]} -> Detection {j} {detections[j]}")


if __name__ == "__main__":
    demo_basic()
    demo_max_profit()
    demo_rectangular()
    demo_forbidden()
    demo_mot_tracking()
