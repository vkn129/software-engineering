"""
Day 125 Practice: DP Optimization — Knuth & Divide-and-Conquer

Targets the functions in dp_optimization.py:
  optimal_bst_cost_naive, optimal_bst_cost_knuth, split_into_k_groups_min_cost

6 exercises. Implement TODOs, then run: python practice.py
"""

INF = float("inf")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: Prefix sums — the weight both DPs are built on
# ---------------------------------------------------------------------------

def prefix_sums(arr):
    """
    Return p of length len(arr)+1 with p[0] = 0 and p[i+1] = p[i] + arr[i],
    so that sum(arr[i:j]) == p[j] - p[i].
    """
    # TODO: implement
    pass


def _sol_prefix_sums(arr):
    # The +1 length is what makes the empty range p[i] - p[i] == 0 work
    # without a special case anywhere downstream.
    p = [0] * (len(arr) + 1)
    for i, x in enumerate(arr):
        p[i + 1] = p[i] + x
    return p


# ---------------------------------------------------------------------------
# Exercise 2: Optimal BST cost, naive O(n^3)
# ---------------------------------------------------------------------------

def optimal_bst_cost_naive(freq):
    """
    Minimum expected search cost of a BST over keys with the given access
    frequencies (keys are already in sorted order).

    dp[i][j] = min over root k in i..j of dp[i][k-1] + dp[k+1][j] + w(i, j),
    where w(i, j) is the total frequency in the interval. The +w term is the
    "everything in this subtree gets one level deeper" charge.
    """
    # TODO: interval DP, every root tried
    pass


def _sol_optimal_bst_cost_naive(freq):
    n = len(freq)
    if n == 0:
        return 0
    prefix = _sol_prefix_sums(freq)
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


# ---------------------------------------------------------------------------
# Exercise 3: Optimal BST cost, Knuth O(n^2)
# ---------------------------------------------------------------------------

def optimal_bst_cost_knuth(freq):
    """
    Same answer, one order of magnitude cheaper.

    Knuth's observation: the best root is monotone, so
        opt[i][j-1] <= opt[i][j] <= opt[i+1][j]
    and the inner scan only has to cover that window instead of all of i..j.
    """
    # TODO: same DP, but bound k by opt[i][j-1] .. opt[i+1][j]
    pass


def _sol_optimal_bst_cost_knuth(freq):
    n = len(freq)
    if n == 0:
        return 0
    prefix = _sol_prefix_sums(freq)
    dp = [[0] * n for _ in range(n)]
    opt = [[0] * n for _ in range(n)]
    for i in range(n):
        opt[i][i] = i
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            w = prefix[j + 1] - prefix[i]
            dp[i][j] = INF
            lo = opt[i][j - 1]
            hi = opt[i + 1][j] if i + 1 <= j else j
            # The windows telescope: summed over one diagonal they collapse to
            # O(n), which is where the whole n^3 -> n^2 saving comes from.
            for k in range(lo, hi + 1):
                left = dp[i][k - 1] if k > i else 0
                right = dp[k + 1][j] if k < j else 0
                cost = left + right + w
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    opt[i][j] = k
    return dp[0][n - 1]


# ---------------------------------------------------------------------------
# Exercise 4: The root table, and the property that licenses Knuth
# ---------------------------------------------------------------------------

def opt_root_table(freq):
    """
    Return the table opt[i][j] = index of the best root for keys i..j
    (opt[i][i] = i). This is the object Knuth's bound is a claim about.
    """
    # TODO: same as exercise 3, but return opt instead of the cost
    pass


def _sol_opt_root_table(freq):
    n = len(freq)
    if n == 0:
        return []
    prefix = _sol_prefix_sums(freq)
    dp = [[0] * n for _ in range(n)]
    opt = [[0] * n for _ in range(n)]
    for i in range(n):
        opt[i][i] = i
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            w = prefix[j + 1] - prefix[i]
            dp[i][j] = INF
            lo = opt[i][j - 1]
            hi = opt[i + 1][j] if i + 1 <= j else j
            for k in range(lo, hi + 1):
                left = dp[i][k - 1] if k > i else 0
                right = dp[k + 1][j] if k < j else 0
                cost = left + right + w
                if cost < dp[i][j]:
                    dp[i][j] = cost
                    opt[i][j] = k
    return opt


def _is_root_monotone(opt):
    """opt[i][j-1] <= opt[i][j] <= opt[i+1][j] for every interval of length>=2."""
    n = len(opt)
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if not (opt[i][j - 1] <= opt[i][j] <= opt[i + 1][j]):
                return False
    return True


# ---------------------------------------------------------------------------
# Exercise 5: k-group split, naive O(n^2 k)
# ---------------------------------------------------------------------------

def split_into_k_groups_naive(arr, k):
    """
    Split arr into k contiguous groups minimising the sum of (group sum)^2.
    Baseline: for every group count and every endpoint, try every split point.
    """
    # TODO: dp[g][i] = min over j < i of dp[g-1][j] + (prefix[i]-prefix[j])^2
    pass


def _sol_split_into_k_groups_naive(arr, k):
    n = len(arr)
    if n == 0 or k == 0:
        return 0
    prefix = _sol_prefix_sums(arr)
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
# Exercise 6: k-group split with divide-and-conquer optimization
# ---------------------------------------------------------------------------

def split_into_k_groups_min_cost(arr, k):
    """
    Same answer in O(n k log n).

    The cost function is convex in the split point, so the best split for the
    middle index BOUNDS the best split for everything left and right of it.
    Recurse on (range of indices, range of candidate split points) and the
    candidate ranges shrink geometrically.
    """
    # TODO: divide and conquer over (lo, hi, opt_lo, opt_hi)
    pass


def _sol_split_into_k_groups_min_cost(arr, k):
    n = len(arr)
    if n == 0 or k == 0:
        return 0
    prefix = _sol_prefix_sums(arr)
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
            # Everything left of mid splits at or before best_k; everything
            # right splits at or after it. That is the whole recursion.
            solve(lo, mid - 1, opt_lo, best_k)
            solve(mid + 1, hi, best_k, opt_hi)

        solve(g, n, g - 1, n)
        dp_prev = dp_cur

    return dp_prev[n]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    BIG_FREQ = [34, 8, 50, 100, 45, 5, 80, 60, 25, 11]

    print("Exercise 1: prefix_sums")
    check("basic", try_or_sol("prefix_sums", [1, 2, 3, 4]), [0, 1, 3, 6, 10])
    check("empty", try_or_sol("prefix_sums", []), [0])
    # The invariant every interval DP on this page depends on.
    arr = [3, 1, 4, 1, 5]
    p = try_or_sol("prefix_sums", arr)
    check("p[j]-p[i] is the interval sum",
          all(p[j] - p[i] == sum(arr[i:j])
              for i in range(len(arr) + 1) for j in range(i, len(arr) + 1)),
          True)

    print("\nExercise 2: optimal_bst_cost_naive")
    check("three keys", try_or_sol("optimal_bst_cost_naive", [34, 8, 50]), 92)
    check("ten keys", try_or_sol("optimal_bst_cost_naive", BIG_FREQ), 882)
    check("single key costs nothing extra",
          try_or_sol("optimal_bst_cost_naive", [7]), 0)
    check("empty", try_or_sol("optimal_bst_cost_naive", []), 0)
    check("two equal keys", try_or_sol("optimal_bst_cost_naive", [1, 1]), 2)

    print("\nExercise 3: optimal_bst_cost_knuth")
    check("three keys", try_or_sol("optimal_bst_cost_knuth", [34, 8, 50]), 92)
    check("ten keys", try_or_sol("optimal_bst_cost_knuth", BIG_FREQ), 882)
    # The only claim that matters: the fast one is not a different algorithm.
    cases = [[], [7], [1, 1], [10, 12, 20], [5, 1, 1, 5, 9, 2], BIG_FREQ]
    check("agrees with the naive DP on every case",
          all(try_or_sol("optimal_bst_cost_knuth", f)
              == _sol_optimal_bst_cost_naive(f) for f in cases),
          True)
    check("empty", try_or_sol("optimal_bst_cost_knuth", []), 0)

    print("\nExercise 4: opt_root_table")
    check("three keys", try_or_sol("opt_root_table", [34, 8, 50]),
          [[0, 0, 1], [0, 1, 1], [0, 0, 2]])
    check("diagonal is the key itself",
          all(try_or_sol("opt_root_table", BIG_FREQ)[i][i] == i
              for i in range(len(BIG_FREQ))),
          True)
    # This is the quadrangle-inequality consequence that licenses the narrowed
    # scan. If it failed, Knuth's bound would cut off the true optimum.
    check("root choice is monotone on every case",
          all(_is_root_monotone(try_or_sol("opt_root_table", f))
              for f in cases if f),
          True)
    check("empty", try_or_sol("opt_root_table", []), [])

    print("\nExercise 5: split_into_k_groups_naive")
    check("[1,2,3,4] into 2",
          try_or_sol("split_into_k_groups_naive", [1, 2, 3, 4], 2), 52)
    # One group is the whole array: 10^2.
    check("[1,2,3,4] into 1",
          try_or_sol("split_into_k_groups_naive", [1, 2, 3, 4], 1), 100)
    # One group per element: 1+4+9+16.
    check("[1,2,3,4] into 4",
          try_or_sol("split_into_k_groups_naive", [1, 2, 3, 4], 4), 30)
    check("empty array", try_or_sol("split_into_k_groups_naive", [], 3), 0)

    print("\nExercise 6: split_into_k_groups_min_cost")
    check("[1,2,3,4] into 2",
          try_or_sol("split_into_k_groups_min_cost", [1, 2, 3, 4], 2), 52)
    check("[5,1,1,5] into 2",
          try_or_sol("split_into_k_groups_min_cost", [5, 1, 1, 5], 2), 72)
    check("[3,1,4,1,5,9,2,6] into 3",
          try_or_sol("split_into_k_groups_min_cost", [3, 1, 4, 1, 5, 9, 2, 6], 3), 341)
    split_cases = [([1, 2, 3, 4], 2), ([1, 2, 3, 4], 1), ([1, 2, 3, 4], 4),
                   ([5, 1, 1, 5], 2), ([3, 1, 4, 1, 5, 9, 2, 6], 3),
                   ([7], 1), ([2, 2, 2, 2, 2, 2], 3)]
    check("agrees with the naive DP on every case",
          all(try_or_sol("split_into_k_groups_min_cost", a, k)
              == _sol_split_into_k_groups_naive(a, k) for a, k in split_cases),
          True)
    # More groups can never cost more: cut one group in two and the two
    # squares sum to less than the square of the whole.
    check("cost is non-increasing in k",
          all(try_or_sol("split_into_k_groups_min_cost", [3, 1, 4, 1, 5, 9], k)
              >= try_or_sol("split_into_k_groups_min_cost", [3, 1, 4, 1, 5, 9], k + 1)
              for k in range(1, 6)),
          True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
