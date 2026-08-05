"""
Day 113: Dynamic Programming Mental Model — Fibonacci three ways.

Same recurrence, three runtimes: O(phi^n), O(n), O(n) — last with O(1) space.
The DAG of subproblems is the key insight.
"""

import sys
import time


# ---------------------------------------------------------------------------
# 1. Naive recursion — exponential
# ---------------------------------------------------------------------------

def fib_naive(n):
    """T(n) = T(n-1) + T(n-2) + O(1) = O(phi^n) where phi ~ 1.618."""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# Counter version: prove the recursion tree is exponential
def fib_naive_counted(n, counter=None):
    if counter is None:
        counter = [0]
    counter[0] += 1
    if n < 2:
        return n, counter[0]
    a, _ = fib_naive_counted(n - 1, counter)
    b, _ = fib_naive_counted(n - 2, counter)
    return a + b, counter[0]


# ---------------------------------------------------------------------------
# 2. Top-down: memoization
# ---------------------------------------------------------------------------

def fib_memo(n, memo=None):
    """Cache subproblem results. Each F(k) computed exactly once."""
    if memo is None:
        memo = {}
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


# ---------------------------------------------------------------------------
# 3. Bottom-up: tabulation
# ---------------------------------------------------------------------------

def fib_tab(n):
    """Build a table from base cases upward. No recursion."""
    if n < 2:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def fib_tab_compressed(n):
    """Only the last two values are needed — O(1) space."""
    if n < 2:
        return n
    prev, curr = 0, 1
    for _ in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr


# ---------------------------------------------------------------------------
# 4. State transition trace — print the DAG of subproblems
# ---------------------------------------------------------------------------

def fib_dag(n):
    """
    Show that subproblems form a DAG with topological order 0..n.
    Each node F(i) depends only on F(i-1) and F(i-2).
    """
    edges = []
    for i in range(2, n + 1):
        edges.append((i - 1, i))
        edges.append((i - 2, i))
    return edges


# ---------------------------------------------------------------------------
# 5. Demos
# ---------------------------------------------------------------------------

def demo_explosion():
    print("=" * 60)
    print("DEMO 1: Naive recursion explosion")
    print("=" * 60)
    print("\nn  | F(n)        | calls")
    print("-" * 40)
    for n in [5, 10, 15, 20, 25, 30]:
        val, calls = fib_naive_counted(n)
        print(f"{n:3} | {val:11} | {calls:,}")
    print("\nCall count ~ phi^n (phi = 1.618...). Try n=40: ~200M calls.")


def demo_three_methods():
    print("\n" + "=" * 60)
    print("DEMO 2: Same answer, three runtimes (n=30)")
    print("=" * 60)

    n = 30
    t = time.perf_counter()
    a = fib_naive(n)
    t_naive = time.perf_counter() - t

    t = time.perf_counter()
    b = fib_memo(n)
    t_memo = time.perf_counter() - t

    t = time.perf_counter()
    c = fib_tab(n)
    t_tab = time.perf_counter() - t

    print(f"\nNaive recursion : F({n}) = {a}, took {t_naive*1000:.2f} ms")
    print(f"Memoized        : F({n}) = {b}, took {t_memo*1000:.4f} ms")
    print(f"Tabulated       : F({n}) = {c}, took {t_tab*1000:.4f} ms")
    print(f"\nSpeedup memo vs naive: {t_naive/max(t_memo,1e-9):.0f}x")


def demo_large_n():
    print("\n" + "=" * 60)
    print("DEMO 3: Tabulated with O(1) space — n=1000")
    print("=" * 60)
    n = 1000
    val = fib_tab_compressed(n)
    print(f"\nF({n}) has {len(str(val))} digits")
    print(f"First 50: {str(val)[:50]}...")
    print(f"Last 50:  ...{str(val)[-50:]}")


def demo_dag():
    print("\n" + "=" * 60)
    print("DEMO 4: Subproblem DAG (n=5)")
    print("=" * 60)
    edges = fib_dag(5)
    print("\nEdges (predecessor -> dependent):")
    for u, v in edges:
        print(f"  F({u}) -> F({v})")
    print("\nTopological order: F(0), F(1), F(2), F(3), F(4), F(5)")
    print("Bottom-up computes nodes in this order; each one needs only "
          "values already computed.")


def demo_recursion_limit():
    print("\n" + "=" * 60)
    print("DEMO 5: Top-down hits Python's recursion limit")
    print("=" * 60)
    print(f"\nDefault recursion limit: {sys.getrecursionlimit()}")
    print("Trying fib_memo(2000) without raising limit...")
    try:
        fib_memo(2000)
        print("  OK (Python's limit must be high)")
    except RecursionError:
        print("  RecursionError. This is why bottom-up is safer for large n.")


if __name__ == "__main__":
    demo_explosion()
    demo_three_methods()
    demo_large_n()
    demo_dag()
    demo_recursion_limit()
