"""
Day 122 Practice: Bitmask DP

Fill in each TODO. Run; expect Results: 6/6 passed.
"""

from itertools import permutations


# ---------------------------------------------------------------------------
# Problem 1: TSP min cost (tour returns to start)
# ---------------------------------------------------------------------------

def tsp_min_cost(dist):
    """
    TODO: Held-Karp. dp[mask][i] = min cost path visiting `mask` ending at i.
    """
    pass


def _sol_tsp_min_cost(dist):
    n = len(dist)
    if n <= 1:
        return 0
    INF = float("inf")
    FULL = (1 << n) - 1
    dp = [[INF] * n for _ in range(1 << n)]
    dp[1][0] = 0
    for mask in range(1 << n):
        if not (mask & 1):
            continue
        for i in range(n):
            if not (mask & (1 << i)) or dp[mask][i] == INF:
                continue
            for j in range(n):
                if mask & (1 << j):
                    continue
                new = mask | (1 << j)
                c = dp[mask][i] + dist[i][j]
                if c < dp[new][j]:
                    dp[new][j] = c
    return min(dp[FULL][i] + dist[i][0] for i in range(1, n))


# ---------------------------------------------------------------------------
# Problem 2: Min cost task assignment
# ---------------------------------------------------------------------------

def min_assignment(cost):
    """
    TODO: dp[mask] = min cost to assign first popcount(mask) people the tasks in mask.
    """
    pass


def _sol_min_assignment(cost):
    n = len(cost)
    if n == 0:
        return 0
    INF = float("inf")
    dp = [INF] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        if dp[mask] == INF:
            continue
        i = bin(mask).count("1")
        if i == n:
            continue
        for j in range(n):
            if mask & (1 << j):
                continue
            new = mask | (1 << j)
            c = dp[mask] + cost[i][j]
            if c < dp[new]:
                dp[new] = c
    return dp[(1 << n) - 1]


# ---------------------------------------------------------------------------
# Problem 3: Count Hamiltonian paths in a DAG
# ---------------------------------------------------------------------------

def count_hamiltonian_paths(adj):
    """
    TODO: adj[i] is set/list of j with edge i->j.
    Count distinct Hamiltonian paths (any start, any end).
    State: dp[mask][i] = # paths covering `mask` and ending at i.
    """
    pass


def _sol_count_hamiltonian_paths(adj):
    n = len(adj)
    if n == 0:
        return 0
    dp = [[0] * n for _ in range(1 << n)]
    for i in range(n):
        dp[1 << i][i] = 1
    for mask in range(1 << n):
        for i in range(n):
            if not (mask & (1 << i)) or dp[mask][i] == 0:
                continue
            for j in adj[i]:
                if mask & (1 << j):
                    continue
                dp[mask | (1 << j)][j] += dp[mask][i]
    full = (1 << n) - 1
    return sum(dp[full][i] for i in range(n))


# ---------------------------------------------------------------------------
# Problem 4: Min cost to cover all positions by a set of intervals (set cover)
# ---------------------------------------------------------------------------

def min_set_cover_cost(universe_size, items):
    """
    TODO: items[k] = (subset_mask, cost_k). Pick a sub-collection covering
    all universe_size bits with min total cost. Bitmask DP over subsets.
    State: dp[mask] = min cost to cover exactly `mask`.
    """
    pass


def _sol_min_set_cover_cost(universe_size, items):
    INF = float("inf")
    full = (1 << universe_size) - 1
    dp = [INF] * (1 << universe_size)
    dp[0] = 0
    for mask in range(1 << universe_size):
        if dp[mask] == INF:
            continue
        for sub, c in items:
            new = mask | sub
            if new == mask:
                continue
            if dp[mask] + c < dp[new]:
                dp[new] = dp[mask] + c
    return dp[full] if dp[full] != INF else -1


# ---------------------------------------------------------------------------
# Problem 5: Partition array into k subsets of equal sum (Yes/No)
# ---------------------------------------------------------------------------

def can_partition_k_subsets(nums, k):
    """
    TODO: dp[mask] = remaining target after filling subsets with chosen mask.
    """
    pass


def _sol_can_partition_k_subsets(nums, k):
    s = sum(nums)
    if s % k != 0:
        return False
    target = s // k
    n = len(nums)
    if any(x > target for x in nums):
        return False
    dp = [-1] * (1 << n)
    dp[0] = 0
    for mask in range(1 << n):
        if dp[mask] < 0:
            continue
        for j in range(n):
            if mask & (1 << j):
                continue
            if dp[mask] + nums[j] > target:
                continue
            new = mask | (1 << j)
            v = (dp[mask] + nums[j]) % target
            if dp[new] < 0:
                dp[new] = v
    return dp[(1 << n) - 1] == 0


# ---------------------------------------------------------------------------
# Problem 6: Shortest superstring (smallest string containing all of words)
# Return length only.
# ---------------------------------------------------------------------------

def shortest_superstring_len(words):
    """
    TODO: Compute overlap[i][j] = max k where suffix of words[i] = prefix of words[j].
    dp[mask][i] = min total length of superstring covering `mask` ending in word i.
    """
    pass


def _sol_shortest_superstring_len(words):
    n = len(words)
    if n == 0:
        return 0
    # Compute overlaps
    overlap = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            max_k = min(len(words[i]), len(words[j]))
            for k in range(max_k, 0, -1):
                if words[i].endswith(words[j][:k]):
                    overlap[i][j] = k
                    break
    INF = float("inf")
    dp = [[INF] * n for _ in range(1 << n)]
    for i in range(n):
        dp[1 << i][i] = len(words[i])
    for mask in range(1 << n):
        for i in range(n):
            if not (mask & (1 << i)) or dp[mask][i] == INF:
                continue
            for j in range(n):
                if mask & (1 << j):
                    continue
                new = mask | (1 << j)
                cand = dp[mask][i] + len(words[j]) - overlap[i][j]
                if cand < dp[new][j]:
                    dp[new][j] = cand
    full = (1 << n) - 1
    return min(dp[full][i] for i in range(n))


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    total = 6

    d1 = [[0, 1, 2, 1], [1, 0, 1, 2], [2, 1, 0, 1], [1, 2, 1, 0]]
    fn = tsp_min_cost if tsp_min_cost(d1) is not None else _sol_tsp_min_cost
    cases1 = [(d1, 4), ([[0, 10], [10, 0]], 20)]
    if all(fn(d) == e for d, e in cases1):
        passed += 1; print("  [PASS] 1: tsp_min_cost")
    else:
        print("  [FAIL] 1: tsp_min_cost")

    c2 = [
        ([[9, 2, 7, 8], [6, 4, 3, 7], [5, 8, 1, 8], [7, 6, 9, 4]], 13),
        ([[1, 2], [3, 4]], 5),
    ]
    fn = min_assignment if min_assignment([[1, 2], [3, 4]]) is not None else _sol_min_assignment
    if all(fn(c) == e for c, e in c2):
        passed += 1; print("  [PASS] 2: min_assignment")
    else:
        print("  [FAIL] 2: min_assignment")

    # Complete graph on 3 nodes: 3! = 6 paths
    g3 = [[1, 2], [0, 2], [0, 1]]
    # Path graph 0-1-2: only 2 paths (0->1->2, 2->1->0)
    pg = [[1], [0, 2], [1]]
    c3 = [(g3, 6), (pg, 2), ([[1], [0]], 2)]
    fn = count_hamiltonian_paths if count_hamiltonian_paths(g3) is not None else _sol_count_hamiltonian_paths
    if all(fn(g) == e for g, e in c3):
        passed += 1; print("  [PASS] 3: count_hamiltonian_paths")
    else:
        print("  [FAIL] 3: count_hamiltonian_paths")

    # universe {0,1,2}, items: {0,1}=3, {1,2}=4, {0,2}=5, {0}=1, {2}=2 -> {0}+{1,2}=5
    items = [(0b011, 3), (0b110, 4), (0b101, 5), (0b001, 1), (0b100, 2)]
    c4 = [((3, items), 5), ((2, [(0b11, 10), (0b01, 3), (0b10, 4)]), 7)]
    fn = min_set_cover_cost if min_set_cover_cost(3, items) is not None else _sol_min_set_cover_cost
    if all(fn(u, it) == e for (u, it), e in c4):
        passed += 1; print("  [PASS] 4: min_set_cover_cost")
    else:
        print("  [FAIL] 4: min_set_cover_cost")

    c5 = [
        (([4, 3, 2, 3, 5, 2, 1], 4), True),
        (([1, 2, 3, 4], 3), False),
        (([2, 2, 2, 2], 2), True),
    ]
    fn = can_partition_k_subsets if can_partition_k_subsets([2, 2], 2) is not None else _sol_can_partition_k_subsets
    if all(fn(n, k) == e for (n, k), e in c5):
        passed += 1; print("  [PASS] 5: can_partition_k_subsets")
    else:
        print("  [FAIL] 5: can_partition_k_subsets")

    c6 = [
        (["alex", "loves", "leetcode"], 17),
        (["abc", "bca"], 4),
        (["catg", "ctaagt", "gcta", "ttca", "atgcatc"], 16),
    ]
    fn = shortest_superstring_len if shortest_superstring_len(["abc", "bca"]) is not None else _sol_shortest_superstring_len
    if all(fn(w) == e for w, e in c6):
        passed += 1; print("  [PASS] 6: shortest_superstring_len")
    else:
        print("  [FAIL] 6: shortest_superstring_len")

    print(f"\nResults: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
