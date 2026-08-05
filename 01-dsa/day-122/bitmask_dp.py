"""
Day 122: Bitmask DP — From Scratch

Track subsets of small sets (n <= 20) as integers.
Turns O(n!) brute force into O(2^n * poly(n)).

  1. Travelling Salesman — O(2^n * n^2)
  2. Task Assignment     — O(2^n * n)
"""

import time
import random
from itertools import permutations


# ---------------------------------------------------------------------------
# 1. Travelling Salesman Problem (TSP) — Held-Karp algorithm
# ---------------------------------------------------------------------------

def tsp(dist):
    """
    dist[i][j] = distance from city i to city j.
    Returns (min_cost, tour) where tour is list of city indices starting and
    ending at city 0.

    State: dp[mask][i] = min cost path visiting exactly cities in mask,
                        ending at city i, starting at city 0.
    """
    n = len(dist)
    if n == 0:
        return 0, []
    if n == 1:
        return 0, [0]

    INF = float("inf")
    FULL = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]
    parent = [[-1] * n for _ in range(1 << n)]

    dp[1][0] = 0  # start at city 0, only city 0 visited

    for mask in range(1, 1 << n):
        if not (mask & 1):
            continue  # must contain city 0
        for i in range(n):
            if not (mask & (1 << i)):
                continue
            if dp[mask][i] == INF:
                continue
            # Extend from i to j not in mask
            for j in range(n):
                if mask & (1 << j):
                    continue
                new_mask = mask | (1 << j)
                cand = dp[mask][i] + dist[i][j]
                if cand < dp[new_mask][j]:
                    dp[new_mask][j] = cand
                    parent[new_mask][j] = i

    # Close the tour: return to city 0
    best_cost = INF
    last = -1
    for i in range(1, n):
        cand = dp[FULL][i] + dist[i][0]
        if cand < best_cost:
            best_cost = cand
            last = i

    # Reconstruct tour
    tour = [0]
    mask = FULL
    cur = last
    path = []
    while cur != -1:
        path.append(cur)
        prev = parent[mask][cur]
        mask ^= (1 << cur)
        cur = prev
    tour = list(reversed(path)) + [0]
    return best_cost, tour


def tsp_brute(dist):
    """O(n!) brute force for comparison."""
    n = len(dist)
    if n <= 1:
        return 0, list(range(n))
    best = float("inf")
    best_perm = None
    for perm in permutations(range(1, n)):
        full = (0,) + perm + (0,)
        cost = sum(dist[full[k]][full[k + 1]] for k in range(len(full) - 1))
        if cost < best:
            best = cost
            best_perm = list(full)
    return best, best_perm


# ---------------------------------------------------------------------------
# 2. Task Assignment — minimum cost bipartite matching by bitmask
# ---------------------------------------------------------------------------

def task_assignment(cost):
    """
    n people, n tasks. cost[i][j] = cost of person i doing task j.
    Each person gets exactly one task; each task to exactly one person.

    State: dp[mask] = min cost to assign first popcount(mask) people
                     such that they took exactly the tasks in mask.

    Process people in order: person i = popcount(mask) - 1 when filling dp[mask].
    """
    n = len(cost)
    if n == 0:
        return 0
    INF = float("inf")
    dp = [INF] * (1 << n)
    dp[0] = 0

    for mask in range(1 << n):
        if dp[mask] == INF:
            continue
        i = bin(mask).count("1")  # next person
        if i == n:
            continue
        for j in range(n):
            if mask & (1 << j):
                continue
            new = mask | (1 << j)
            cand = dp[mask] + cost[i][j]
            if cand < dp[new]:
                dp[new] = cand

    return dp[(1 << n) - 1]


# ---------------------------------------------------------------------------
# 3. Demos
# ---------------------------------------------------------------------------

def random_symmetric_dist(n, seed=0, max_d=100):
    random.seed(seed)
    d = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            v = random.randint(1, max_d)
            d[i][j] = d[j][i] = v
    return d


def demo_tsp():
    print("=" * 60)
    print("DEMO 1: TSP — Held-Karp Bitmask DP")
    print("=" * 60)

    # Small example: 4 cities on a square
    dist = [
        [0, 1, 2, 1],
        [1, 0, 1, 2],
        [2, 1, 0, 1],
        [1, 2, 1, 0],
    ]
    cost, tour = tsp(dist)
    print(f"\n  4-city square: min cost = {cost}, tour = {tour}")

    # Random comparison vs brute force at n = 8
    n = 8
    d = random_symmetric_dist(n, seed=42)
    t0 = time.perf_counter()
    c_dp, _ = tsp(d)
    t1 = time.perf_counter()
    c_bf, _ = tsp_brute(d)
    t2 = time.perf_counter()
    print(f"\n  n = {n} random:  DP cost = {c_dp}, brute = {c_bf}")
    print(f"      DP time = {t1 - t0:.4f}s, brute = {t2 - t1:.4f}s")
    assert c_dp == c_bf

    # Larger n
    n = 14
    d = random_symmetric_dist(n, seed=1)
    t0 = time.perf_counter()
    c_dp, _ = tsp(d)
    t1 = time.perf_counter()
    print(f"\n  n = {n}: DP cost = {c_dp}, time = {t1 - t0:.3f}s")
    print(f"  (brute force would need {n-1}! = {1 * 2 * 3 * 4 * 5 * 6 * 7 * 8 * 9 * 10 * 11 * 12 * 13} permutations)")


def demo_assignment():
    print("\n" + "=" * 60)
    print("DEMO 2: Task Assignment")
    print("=" * 60)
    cost = [
        [9, 2, 7, 8],
        [6, 4, 3, 7],
        [5, 8, 1, 8],
        [7, 6, 9, 4],
    ]
    print("\n  cost matrix:")
    for row in cost:
        print("   ", row)
    ans = task_assignment(cost)
    print(f"\n  min total cost: {ans}")
    # Sanity: brute via permutations
    n = len(cost)
    brute = min(sum(cost[i][p[i]] for i in range(n)) for p in permutations(range(n)))
    print(f"  brute-force check: {brute}")
    assert ans == brute


if __name__ == "__main__":
    demo_tsp()
    demo_assignment()
