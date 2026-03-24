"""
Day 3 Practice: Writing and Solving Recurrence Relations

For each function below:
1. Write the recurrence relation T(n) = ...
2. Identify: does the Master Theorem apply? If so, which case?
3. Solve for the Big-Theta complexity.
4. Fill in your answer in the TODO comment.

After you fill in all answers, run this file to check against solutions.

Run: python practice.py
"""

import sys
sys.setrecursionlimit(100000)


# ---------------------------------------------------------------------------
# Exercise 1: Write the recurrence and solve
# ---------------------------------------------------------------------------
def ex1(n):
    """What is the recurrence? What is the complexity?"""
    if n <= 1:
        return 1
    return ex1(n // 2) + ex1(n // 2) + n

# TODO: Your analysis for ex1
# Recurrence: T(n) =
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 2: Write the recurrence and solve
# ---------------------------------------------------------------------------
def ex2(n):
    """What is the recurrence? What is the complexity?"""
    if n <= 1:
        return 1
    total = 0
    for i in range(n):  # O(n) work
        total += i
    return total + ex2(n // 3)

# TODO: Your analysis for ex2
# Recurrence: T(n) =
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 3: Write the recurrence and solve
# ---------------------------------------------------------------------------
def ex3(n):
    """What is the recurrence? What is the complexity?"""
    if n <= 1:
        return 1
    return ex3(n // 2) + 1

# TODO: Your analysis for ex3
# Recurrence: T(n) =
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 4: Write the recurrence and solve
# ---------------------------------------------------------------------------
def ex4(n):
    """What is the recurrence? What is the complexity?"""
    if n <= 1:
        return 1
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1    # O(n^2) work
    return total + ex4(n // 2) + ex4(n // 2)

# TODO: Your analysis for ex4
# Recurrence: T(n) =
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 5: Write the recurrence and solve
# ---------------------------------------------------------------------------
def ex5(n):
    """What is the recurrence? What is the complexity?
    WARNING: This does NOT fit the Master Theorem. Explain why."""
    if n <= 1:
        return 1
    return ex5(n - 1) + ex5(n - 1)

# TODO: Your analysis for ex5
# Recurrence: T(n) =
# Does Master Theorem apply? Why or why not?
# Solve using another method:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 6: Write the recurrence and solve
# ---------------------------------------------------------------------------
def ex6(n):
    """What is the recurrence? What is the complexity?"""
    if n <= 1:
        return 1
    return ex6(n // 4) + ex6(n // 4) + ex6(n // 4) + n

# TODO: Your analysis for ex6
# Recurrence: T(n) =
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 7: Given the recurrence, determine the complexity
# (No code — pure math)
# ---------------------------------------------------------------------------
# T(n) = 9T(n/3) + n^2
#
# TODO: Your analysis
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:


# ---------------------------------------------------------------------------
# Exercise 8: Given the recurrence, determine the complexity
# (No code — pure math. This one is tricky.)
# ---------------------------------------------------------------------------
# T(n) = T(n/2) + n
#
# TODO: Your analysis
# Master Theorem: a=?, b=?, d=?, log_b(a)=?
# Case:
# Complexity:
# Draw the recursion tree to convince yourself.


# ===========================================================================
# SOLUTIONS — scroll down only after attempting all exercises above
# ===========================================================================


SOLUTIONS = """
+=====================================================================+
|                          SOLUTIONS                                    |
+=====================================================================+

Exercise 1: T(n) = 2T(n/2) + n
  a=2, b=2, d=1. log_2(2) = 1 = d.
  Case 2: T(n) = Theta(n log n).
  This is the merge sort recurrence.

Exercise 2: T(n) = T(n/3) + n
  a=1, b=3, d=1. log_3(1) = 0 < 1.
  Case 3: Root dominates. T(n) = Theta(n).
  The root does n work, next level does n/3, then n/9...
  Geometric series: n(1 + 1/3 + 1/9 + ...) = n * 3/2 = Theta(n).

Exercise 3: T(n) = T(n/2) + 1
  a=1, b=2, d=0. log_2(1) = 0 = d.
  Case 2: T(n) = Theta(log n).
  This is the binary search recurrence.

Exercise 4: T(n) = 2T(n/2) + n^2
  a=2, b=2, d=2. log_2(2) = 1 < 2.
  Case 3: Root dominates. T(n) = Theta(n^2).
  The n^2 work at the root dwarfs the rest of the tree.
  Total: n^2 + 2(n/2)^2 + 4(n/4)^2 + ...
       = n^2(1 + 1/2 + 1/4 + ...) = 2n^2 = Theta(n^2).

Exercise 5: T(n) = 2T(n-1) + 1
  Master Theorem does NOT apply: the subproblem size is n-1
  (subtraction), not n/b (division). The Master Theorem requires
  dividing n by a constant factor.

  Solve by expansion:
    T(n) = 2T(n-1) + 1
         = 2(2T(n-2) + 1) + 1 = 4T(n-2) + 3
         = 8T(n-3) + 7
         = 2^k * T(n-k) + (2^k - 1)
  When k = n-1: T(n) = 2^(n-1) * T(1) + 2^(n-1) - 1 = Theta(2^n).

Exercise 6: T(n) = 3T(n/4) + n
  a=3, b=4, d=1. log_4(3) = ln(3)/ln(4) ≈ 0.793 < 1.
  Case 3: Root dominates. T(n) = Theta(n).

Exercise 7: T(n) = 9T(n/3) + n^2
  a=9, b=3, d=2. log_3(9) = 2 = d.
  Case 2: T(n) = Theta(n^2 * log n).
  Balanced — each level does n^2 work, and there are log_3(n) levels.

Exercise 8: T(n) = T(n/2) + n
  a=1, b=2, d=1. log_2(1) = 0 < 1.
  Case 3: Root dominates. T(n) = Theta(n).

  Recursion tree:
    Level 0: n
    Level 1: n/2
    Level 2: n/4
    ...
    Total: n + n/2 + n/4 + ... = 2n = Theta(n).

  This surprises people who think "halving + linear work = n log n".
  The key: there is only ONE recursive call. The work halves each
  level, forming a convergent geometric series. Compare with merge
  sort's TWO calls — that is what creates log(n) levels of EQUAL work.
"""


def verify_solutions():
    """Run functions to check they work, then show timing + solutions."""
    import time

    print("Empirical verification — timing each exercise function:\n")

    funcs_with_sizes = [
        ("ex1: T(n)=2T(n/2)+n",     ex1, [2000, 4000, 8000, 16000],    "~2.2x (n log n)"),
        ("ex2: T(n)=T(n/3)+n",      ex2, [5000, 10000, 20000, 40000],  "~2x (linear, root dominant)"),
        ("ex3: T(n)=T(n/2)+1",      ex3, [10000, 20000, 40000, 80000], "barely grows (log n)"),
        ("ex4: T(n)=2T(n/2)+n^2",   ex4, [250, 500, 1000, 2000],       "~4x (quadratic, root dominant)"),
        ("ex6: T(n)=3T(n/4)+n",     ex6, [5000, 10000, 20000, 40000],  "~2x (linear, root dominant)"),
    ]

    for name, func, sizes, expected in funcs_with_sizes:
        print(f"  {name}")
        print(f"  Expected ratio when doubling n: {expected}")
        prev_t = None
        for n in sizes:
            start = time.perf_counter()
            func(n)
            t = time.perf_counter() - start
            ratio = f"{t/prev_t:.2f}x" if prev_t and prev_t > 0 else "--"
            print(f"    n={n:>6}  time={t:.6f}s  ratio={ratio}")
            prev_t = t
        print()

    # Exercise 5 — exponential, use tiny inputs
    print("  ex5: T(n)=2T(n-1)+1")
    print("  Expected: each +1 doubles time (exponential)")
    prev_t = None
    for n in [12, 14, 16, 18, 20]:
        start = time.perf_counter()
        ex5(n)
        t = time.perf_counter() - start
        ratio = f"{t/prev_t:.2f}x" if prev_t and prev_t > 0 else "--"
        print(f"    n={n:>6}  time={t:.6f}s  ratio={ratio}")
        prev_t = t
    print("  Each +2 should ~quadruple (2^2 = 4x)\n")

    print(SOLUTIONS)


if __name__ == "__main__":
    print("Day 3 Practice: Recurrence Relations")
    print("=" * 60)
    print()
    print("Have you written your answers in the TODO comments above?")
    print("Running verification and showing solutions...\n")
    verify_solutions()
