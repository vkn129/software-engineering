"""
Day 113 Practice: DP mental model.

6 exercises stretching the recursion -> memo -> tabulation pipeline.
Implement the TODO functions, then run: python practice.py
"""


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


# ===================================================================
# Exercise 1: Memoized Fibonacci
# ===================================================================
# Implement memoized Fibonacci. Each F(k) must be computed at most once.

def fib_memo(n):
    """Return F(n). F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)."""
    # TODO: implement using top-down memoization
    pass


def _sol_fib_memo(n):
    memo = {}

    def go(k):
        if k < 2:
            return k
        if k in memo:
            return memo[k]
        memo[k] = go(k - 1) + go(k - 2)
        return memo[k]

    return go(n)


# ===================================================================
# Exercise 2: Tabulated Fibonacci with O(1) space
# ===================================================================
# Bottom-up Fibonacci using only two variables, not a full array.

def fib_tab(n):
    """Return F(n) using O(1) extra space."""
    # TODO: implement
    pass


def _sol_fib_tab(n):
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


# ===================================================================
# Exercise 3: Tribonacci
# ===================================================================
# T(0)=0, T(1)=1, T(2)=1, T(n)=T(n-1)+T(n-2)+T(n-3).
# State space O(n). Implement bottom-up.

def tribonacci(n):
    """Return the n-th Tribonacci number."""
    # TODO: implement
    pass


def _sol_tribonacci(n):
    if n == 0:
        return 0
    if n <= 2:
        return 1
    a, b, c = 0, 1, 1
    for _ in range(3, n + 1):
        a, b, c = b, c, a + b + c
    return c


# ===================================================================
# Exercise 4: Count paths in a recurrence DAG
# ===================================================================
# A frog can jump 1 or 2 steps. How many distinct ways to reach step n?
# Recurrence: ways(n) = ways(n-1) + ways(n-2).  ways(0) = ways(1) = 1.
# (Yes, this is Fibonacci-shaped. Reuse the pattern.)

def count_ways(n):
    """Number of ways to climb n steps with jumps of 1 or 2."""
    # TODO: implement
    pass


def _sol_count_ways(n):
    if n <= 1:
        return 1
    a, b = 1, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# ===================================================================
# Exercise 5: Identify whether a recurrence has overlapping subproblems
# ===================================================================
# Given a recurrence f(n) = sum_{k in deps(n)} f(k), count how many
# distinct subproblems are visited by naive recursion for n.
# If that count equals n+1, the recursion has no overlap (still linear).
# If it exceeds n+1, subproblems overlap and DP would help.

def count_distinct_subproblems(n, deps_fn):
    """
    deps_fn(k) returns list of subproblem indices f(k) depends on (each < k).
    Walk the recursion tree from n; return |{distinct k visited}|.
    """
    # TODO: implement (hint: use a set, recurse from n, stop at k <= 0)
    pass


def _sol_count_distinct_subproblems(n, deps_fn):
    seen = set()

    def go(k):
        if k <= 0:
            return
        if k in seen:
            return
        seen.add(k)
        for d in deps_fn(k):
            go(d)

    go(n)
    return len(seen)


# ===================================================================
# Exercise 6: Min cost climbing stairs (warm-up for Day 114)
# ===================================================================
# cost[i] is the cost to STAND on step i. From step i you can move 1 or 2
# steps up. You may start at step 0 or step 1. Return the min cost to reach
# the top (just past the last index).
# Recurrence: dp[i] = cost[i] + min(dp[i-1], dp[i-2])
# Answer: min(dp[n-1], dp[n-2])

def min_cost_stairs(cost):
    """Min cost to reach the top of the staircase."""
    # TODO: implement bottom-up
    pass


def _sol_min_cost_stairs(cost):
    n = len(cost)
    if n == 0:
        return 0
    if n == 1:
        return cost[0]
    prev2, prev1 = cost[0], cost[1]
    for i in range(2, n):
        prev2, prev1 = prev1, cost[i] + min(prev1, prev2)
    return min(prev1, prev2)


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

    print("Exercise 1: Memoized Fibonacci")
    check("F(0)", try_or_sol("fib_memo", 0), 0)
    check("F(10)", try_or_sol("fib_memo", 10), 55)
    check("F(30)", try_or_sol("fib_memo", 30), 832040)

    print("\nExercise 2: Tabulated Fibonacci O(1) space")
    check("F(0)", try_or_sol("fib_tab", 0), 0)
    check("F(1)", try_or_sol("fib_tab", 1), 1)
    check("F(20)", try_or_sol("fib_tab", 20), 6765)

    print("\nExercise 3: Tribonacci")
    check("T(0)", try_or_sol("tribonacci", 0), 0)
    check("T(4)", try_or_sol("tribonacci", 4), 4)
    check("T(10)", try_or_sol("tribonacci", 10), 149)

    print("\nExercise 4: Frog jumps")
    check("ways(0)", try_or_sol("count_ways", 0), 1)
    check("ways(3)", try_or_sol("count_ways", 3), 3)
    check("ways(5)", try_or_sol("count_ways", 5), 8)

    print("\nExercise 5: Distinct subproblems")
    fib_deps = lambda k: [k - 1, k - 2]
    check("fib(5) -> 5 nodes", try_or_sol("count_distinct_subproblems", 5, fib_deps), 5)
    check("fib(10) -> 10 nodes", try_or_sol("count_distinct_subproblems", 10, fib_deps), 10)
    # Chain dep: each f(k) only calls f(k-1). 5 nodes (1..5).
    chain = lambda k: [k - 1]
    check("chain(5) -> 5 nodes", try_or_sol("count_distinct_subproblems", 5, chain), 5)

    print("\nExercise 6: Min cost stairs")
    check("[10,15,20]", try_or_sol("min_cost_stairs", [10, 15, 20]), 15)
    check("[1,100,1,1,1,100,1,1,100,1]",
          try_or_sol("min_cost_stairs", [1, 100, 1, 1, 1, 100, 1, 1, 100, 1]), 6)
    check("single step", try_or_sol("min_cost_stairs", [7]), 7)

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
