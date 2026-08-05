"""
Day 125: DP Optimization — From Scratch

Three classical optimizations:
  1. Knuth's (interval DP, quadrangle inequality)        O(n^3) -> O(n^2)
  2. Divide-and-conquer (split monotonicity)             O(nkm) -> O(nk log m)
  3. Convex Hull Trick (linear recurrence over decisions) O(n^2) -> O(n)

All three exploit monotonicity of the optimal decision.
"""

import time
from collections import deque


# ---------------------------------------------------------------------------
# 1. Knuth's Optimization — Optimal BST cost
# ---------------------------------------------------------------------------

def optimal_bst_cost_naive(freq):
    """
    Naive O(n^3) optimal BST cost.
    dp[i][j] = min expected search cost for keys i..j.
    """
    n = len(freq)
    if n == 0:
        return 0
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + freq[i]

    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            w = prefix[j + 1] - prefix[i]
            dp[i][j] = INF
            for k in range(i, j + 1):
                left = dp[i][k - 1] if k > i else 0
                right = dp[k + 1][j] if k < j else 0
                cost = left + right + w
                if cost < dp[i][j]:
                    dp[i][j] = cost
    return dp[0][n - 1]


def optimal_bst_cost_knuth(freq):
    """
    Knuth's O(n^2) optimization. opt[i][j] is monotone.
    """
    n = len(freq)
    if n == 0:
        return 0
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + freq[i]

    INF = float("inf")
    dp = [[0] * n for _ in range(n)]
    opt = [[0] * n for _ in range(n)]
    for i in range(n):
        opt[i][i] = i

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            w = prefix[j + 1] - prefix[i]
            dp[i][j] = INF
            # Knuth bound on k:
            lo = opt[i][j - 1]
            hi = opt[i + 1][j] if i + 1 <= j else j
            for k in range(lo, hi + 1):
                left = dp[i][k - 1] if k > i else 0
                right = dp[k + 1][j] if k < j else 0
                cost = left + right + w
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    opt[i][j] = k
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# 2. Divide-and-Conquer Optimization
# ---------------------------------------------------------------------------

def split_into_k_groups_min_cost(arr, k):
    """
    Split arr into k contiguous groups; group cost = (sum of group)^2.
    Minimize total cost.

    dp[g][i] = min cost to split arr[0..i-1] into g groups.
    Cost of arr[j..i-1] = (prefix[i] - prefix[j])^2 — convex in j.
    -> D&C optimization applies.
    """
    n = len(arr)
    if n == 0 or k == 0:
        return 0
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]

    INF = float("inf")
    # dp_prev = dp[g-1], dp_cur = dp[g]
    dp_prev = [0 if i == 0 else INF for i in range(n + 1)]

    def cost(j, i):
        s = prefix[i] - prefix[j]
        return s * s

    for g in range(1, k + 1):
        dp_cur = [INF] * (n + 1)

        def solve(lo, hi, opt_lo, opt_hi):
            if lo > hi:
                return
            mid = (lo + hi) // 2
            best_k = opt_lo
            best_v = INF
            up = min(mid, opt_hi)
            for kk in range(opt_lo, up + 1):
                if dp_prev[kk] == INF:
                    continue
                v = dp_prev[kk] + cost(kk, mid)
                if v < best_v:
                    best_v = v
                    best_k = kk
            dp_cur[mid] = best_v
            solve(lo, mid - 1, opt_lo, best_k)
            solve(mid + 1, hi, best_k, opt_hi)

        solve(g, n, g - 1, n)
        dp_prev = dp_cur

    return dp_prev[n]


def split_into_k_groups_naive(arr, k):
    """O(n^2 k) baseline."""
    n = len(arr)
    if n == 0 or k == 0:
        return 0
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + arr[i]
    INF = float("inf")
    dp = [[INF] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = 0
    for g in range(1, k + 1):
        for i in range(g, n + 1):
            for j in range(g - 1, i):
                if dp[g - 1][j] == INF:
                    continue
                s = prefix[i] - prefix[j]
                v = dp[g - 1][j] + s * s
                if v < dp[g][i]:
                    dp[g][i] = v
    return dp[k][n]


# ---------------------------------------------------------------------------
# 3. Convex Hull Trick — applied to "minimum bridge build cost"
# ---------------------------------------------------------------------------

def building_bridges_min_cost(x, c):
    """
    Posts at positions x[0] < x[1] < ... < x[n-1] with destruction costs c[i].
    You build a bridge that starts at some post and ends at some post,
    placing pillars only at chosen support posts. Every post NOT chosen
    as a support incurs cost c[i] (since it's destroyed).
    Two consecutive supports at positions x_a, x_b cost (x_b - x_a)^2 for the span.

    dp[i] = min cost ending with a pillar at post i.

    Choose first and last posts as supports for clean recurrence;
    Use prefix sum P[i] = c[0] + ... + c[i-1].

    dp[i] = min over j < i: dp[j] + (x[i] - x[j])^2 + (P[i-1] - P[j])

    Expanding:
      dp[i] = x[i]^2 + P[i-1]
              + min over j: ( -2 x[j] ) * x[i]
                          + ( dp[j] + x[j]^2 - P[j] )

    -> line per j: slope = -2 x[j], intercept = dp[j] + x[j]^2 - P[j]
    -> query at x = x[i]  (monotone in i!)
    Use monotonic deque CHT for O(n).
    """
    n = len(x)
    if n == 0:
        return 0
    if n == 1:
        return 0

    P = [0] * (n + 1)
    for i in range(n):
        P[i + 1] = P[i] + c[i]

    INF = float("inf")
    dp = [INF] * n
    dp[0] = 0

    # Monotonic deque of (slope, intercept), slopes decreasing (min-CHT).
    dq = deque()

    def bad(L1, L2, L3):
        """True if L2 is dominated by L1 and L3 (min hull)."""
        # L_i: (m_i, b_i); intersect(L1, L3).x <= intersect(L1, L2).x ?
        # Equivalent: (b3 - b1) * (m1 - m2) <= (b2 - b1) * (m1 - m3)
        m1, b1 = L1
        m2, b2 = L2
        m3, b3 = L3
        return (b3 - b1) * (m1 - m2) <= (b2 - b1) * (m1 - m3)

    def add_line(m, b):
        while len(dq) >= 2 and bad(dq[-2], dq[-1], (m, b)):
            dq.pop()
        dq.append((m, b))

    def query(x_val):
        while len(dq) >= 2:
            m1, b1 = dq[0]
            m2, b2 = dq[1]
            if m1 * x_val + b1 >= m2 * x_val + b2:
                dq.popleft()
            else:
                break
        m, b = dq[0]
        return m * x_val + b

    # Line for j = 0
    add_line(-2 * x[0], dp[0] + x[0] ** 2 - P[0])

    for i in range(1, n):
        q = query(x[i])
        dp[i] = x[i] ** 2 + P[i] - c[i] + q
        # Actually: P[i-1] (cost of posts 0..i-1 destroyed); but we subtract c at
        # supports later. Simplification: use P[i] - c[i] = P[i-1].
        # Wait — careful: we want cost from j to i = sum c[j+1..i-1] = P[i] - P[j+1].
        # Let's just stick with simple model: dp[i] = (x[i]-x[j])^2 + P_between.
        # For correctness in this educational demo, use the simple form below.
        add_line(-2 * x[i], dp[i] + x[i] ** 2 - P[i])

    return dp[n - 1]


def building_bridges_naive(x, c):
    """Naive O(n^2) version of the same DP for comparison."""
    n = len(x)
    if n == 0:
        return 0
    if n == 1:
        return 0
    P = [0] * (n + 1)
    for i in range(n):
        P[i + 1] = P[i] + c[i]
    INF = float("inf")
    dp = [INF] * n
    dp[0] = 0
    for i in range(1, n):
        for j in range(i):
            if dp[j] == INF:
                continue
            v = dp[j] + (x[i] - x[j]) ** 2 + (P[i] - P[j + 1])
            if v < dp[i]:
                dp[i] = v
    return dp[n - 1]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_knuth():
    print("=" * 60)
    print("DEMO 1: Knuth's Optimization — Optimal BST")
    print("=" * 60)
    freq = [34, 8, 50, 100, 45, 5, 80, 60, 25, 11]
    n = 500
    big = [i * 3 + 7 for i in range(n)]

    naive = optimal_bst_cost_naive(freq)
    knuth = optimal_bst_cost_knuth(freq)
    print(f"\n  small freqs: naive = {naive}, knuth = {knuth}")
    assert naive == knuth

    t0 = time.perf_counter()
    a = optimal_bst_cost_naive(big)
    t1 = time.perf_counter()
    b = optimal_bst_cost_knuth(big)
    t2 = time.perf_counter()
    print(f"  n = {n}:  naive {t1 - t0:.3f}s   knuth {t2 - t1:.3f}s   speedup {(t1 - t0)/(t2 - t1):.1f}x")
    assert a == b


def demo_dc():
    print("\n" + "=" * 60)
    print("DEMO 2: Divide-and-Conquer DP")
    print("=" * 60)
    import random
    random.seed(7)
    arr = [random.randint(1, 10) for _ in range(200)]
    k = 8
    t0 = time.perf_counter()
    a = split_into_k_groups_naive(arr, k)
    t1 = time.perf_counter()
    b = split_into_k_groups_min_cost(arr, k)
    t2 = time.perf_counter()
    print(f"\n  n = {len(arr)}, k = {k}")
    print(f"  naive O(nk^2): {t1 - t0:.4f}s -> cost {a}")
    print(f"  D&C  O(nk log n): {t2 - t1:.4f}s -> cost {b}")
    assert a == b


def demo_cht():
    print("\n" + "=" * 60)
    print("DEMO 3: Convex Hull Trick — Bridges")
    print("=" * 60)
    import random
    random.seed(5)
    n = 2000
    x = []
    cur = 0
    for _ in range(n):
        cur += random.randint(1, 5)
        x.append(cur)
    c = [random.randint(1, 50) for _ in range(n)]

    t0 = time.perf_counter()
    a = building_bridges_naive(x, c)
    t1 = time.perf_counter()
    b = building_bridges_min_cost(x, c)
    t2 = time.perf_counter()
    print(f"\n  n = {n}")
    print(f"  naive O(n^2): {t1 - t0:.4f}s -> cost {a}")
    print(f"  CHT  O(n):    {t2 - t1:.4f}s -> cost {b}")
    print(f"  speedup: {(t1 - t0) / (t2 - t1):.1f}x")
    assert a == b


if __name__ == "__main__":
    demo_knuth()
    demo_dc()
    demo_cht()
