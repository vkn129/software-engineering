"""
Day 3: Recurrence Relations & Master Theorem — Visualized and Verified

This script does three things:
1. Builds recursion trees and shows work at each level (so you SEE the pattern).
2. Applies the Master Theorem to classify recurrences.
3. Times actual recursive functions to verify the theory empirically.

The goal: recurrences should stop being abstract algebra and become
something you can draw, predict, and measure.

Run: python recurrence_relations.py
"""

import time
import math


# ---------------------------------------------------------------------------
# Recursion tree visualization
# ---------------------------------------------------------------------------

def visualize_recursion_tree(a, b, d, n, label=""):
    """Build a recursion tree for T(n) = a*T(n/b) + O(n^d).

    At each level:
      - Number of subproblems: a^level
      - Size of each subproblem: n / b^level
      - Work per subproblem: (n / b^level)^d
      - Total work at level: a^level * (n / b^level)^d = n^d * (a / b^d)^level

    We print each level's work and show the geometric series pattern.
    """
    print(f"\n{'=' * 65}")
    print(f"  RECURSION TREE: T(n) = {a}T(n/{b}) + O(n^{d})  {label}")
    print(f"{'=' * 65}")
    print(f"  n = {n}")
    print()

    ratio = a / (b ** d)
    log_b_a = math.log(a) / math.log(b) if a > 0 else 0
    height = int(math.log(n) / math.log(b)) if n > 1 and b > 1 else 0

    total_work = 0
    level_works = []

    print(f"  {'Level':>6}  {'Subproblems':>12}  {'Size':>8}  {'Work/node':>12}  {'Level work':>12}  {'Ratio':>8}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*8}  {'-'*12}  {'-'*12}  {'-'*8}")

    for level in range(height + 1):
        num_subproblems = a ** level
        size = n / (b ** level)
        work_per_node = size ** d
        level_work = num_subproblems * work_per_node
        level_works.append(level_work)
        total_work += level_work

        if level == 0:
            ratio_str = "--"
        else:
            ratio_str = f"{level_work / level_works[level - 1]:.3f}"

        print(f"  {level:>6}  {num_subproblems:>12}  {size:>8.0f}  {work_per_node:>12.0f}  {level_work:>12.0f}  {ratio_str:>8}")

    # Leaf level
    leaves = a ** (height + 1)
    print(f"\n  Leaves: {leaves} subproblems of size 1")
    print(f"  Tree height: {height + 1} levels")
    print(f"  Total work (summed): {total_work:.0f}")

    # Classify
    print(f"\n  Master Theorem classification:")
    print(f"    a = {a}, b = {b}, d = {d}")
    print(f"    log_b(a) = log_{b}({a}) = {log_b_a:.3f}")

    if d < log_b_a:
        print(f"    d ({d}) < log_b(a) ({log_b_a:.3f})")
        print(f"    => CASE 1: Leaves dominate. T(n) = O(n^{log_b_a:.3f})")
        print(f"    Each level's work INCREASES — the bottom of the tree does most work.")
    elif abs(d - log_b_a) < 0.01:
        print(f"    d ({d}) = log_b(a) ({log_b_a:.3f})")
        print(f"    => CASE 2: Balanced. T(n) = O(n^{d} * log n)")
        print(f"    Each level does the SAME work — multiply by number of levels.")
    else:
        print(f"    d ({d}) > log_b(a) ({log_b_a:.3f})")
        print(f"    => CASE 3: Root dominates. T(n) = O(n^{d})")
        print(f"    Each level's work DECREASES — the top does most work.")

    return total_work


# ---------------------------------------------------------------------------
# Actual recursive functions to time and verify
# ---------------------------------------------------------------------------

def merge_sort_work(n):
    """T(n) = 2T(n/2) + n — Master Theorem Case 2.
    Simulates merge sort's work pattern by counting operations."""
    if n <= 1:
        return 1
    work = n  # the merge step does O(n) comparisons
    work += merge_sort_work(n // 2)
    work += merge_sort_work(n - n // 2)
    return work


def binary_search_work(n):
    """T(n) = T(n/2) + 1 — Master Theorem Case 2 (with d=0, a=1).
    Actually log_b(a) = 0 = d, so O(log n)."""
    if n <= 1:
        return 1
    return 1 + binary_search_work(n // 2)


def strassen_like_work(n):
    """T(n) = 7T(n/2) + n^2 — Case 1 (log_2(7) ≈ 2.81 > 2).
    Simulates Strassen's matrix multiplication pattern.
    The heavy branching means leaves dominate."""
    if n <= 1:
        return 1
    work = n * n  # O(n^2) non-recursive work
    # 7 recursive calls on n/2 — but we only simulate the count
    # Actually recursing 7 times would be too slow for large n
    return work + 7 * strassen_like_work(n // 2)


def root_dominant_work(n):
    """T(n) = 3T(n/4) + n^2 — Case 3 (log_4(3) ≈ 0.79 < 2).
    The root does O(n^2) work and subproblems shrink fast.
    Each level's work decreases geometrically — root dominates."""
    if n <= 1:
        return 1
    work = n * n
    return work + 3 * root_dominant_work(n // 4)


def linear_recursion_work(n):
    """T(n) = T(n-1) + O(1) — NOT Master Theorem form.
    This is a linear recurrence: T(n) = n.
    Equivalent to a simple loop."""
    if n <= 1:
        return 1
    return 1 + linear_recursion_work(n - 1)


def quadratic_recursion_work(n):
    """T(n) = T(n-1) + O(n) — NOT Master Theorem form.
    Total work: n + (n-1) + ... + 1 = n(n+1)/2 = O(n^2).
    This is what insertion sort looks like as a recurrence."""
    if n <= 1:
        return 1
    return n + quadratic_recursion_work(n - 1)


# ---------------------------------------------------------------------------
# Timing and verification
# ---------------------------------------------------------------------------

def time_function(func, arg, runs=3):
    """Time a function and return median time."""
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        func(arg)
        end = time.perf_counter()
        times.append(end - start)
    times.sort()
    return times[len(times) // 2]


def verify_growth(name, func, sizes, expected_ratio_desc):
    """Time a function at increasing sizes and print growth ratios."""
    print(f"\n  {name}")
    print(f"  Expected when doubling n: {expected_ratio_desc}")
    print(f"  {'n':>10}  {'Time (s)':>12}  {'Ratio':>8}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*8}")

    prev_t = None
    for n in sizes:
        t = time_function(func, n, runs=3)
        if prev_t and prev_t > 0:
            ratio_str = f"{t / prev_t:.2f}x"
        else:
            ratio_str = "--"
        print(f"  {n:>10}  {t:>12.6f}  {ratio_str:>8}")
        prev_t = t


# ---------------------------------------------------------------------------
# Solving recurrences step by step
# ---------------------------------------------------------------------------

def show_substitution_method():
    """Walk through the substitution method on T(n) = 2T(n/2) + n."""
    print(f"\n{'=' * 65}")
    print("  SUBSTITUTION METHOD: T(n) = 2T(n/2) + n")
    print(f"{'=' * 65}")
    print()
    print("  Step 1: Guess T(n) = O(n log n), i.e., T(n) <= c*n*log(n)")
    print()
    print("  Step 2: Assume T(k) <= c*k*log(k) for all k < n (inductive hypothesis)")
    print()
    print("  Step 3: Substitute into the recurrence:")
    print("    T(n) = 2*T(n/2) + n")
    print("         <= 2 * c*(n/2)*log(n/2) + n")
    print("         = c*n*(log(n) - log(2)) + n")
    print("         = c*n*log(n) - c*n + n")
    print("         = c*n*log(n) - (c-1)*n")
    print("         <= c*n*log(n)            [when c >= 1]")
    print()
    print("  Step 4: Verify base case. T(1) = 1 <= c*1*log(1) = 0.")
    print("    Hmm, log(1) = 0. We need T(2) as base: T(2) = 2*T(1) + 2 = 4.")
    print("    4 <= c*2*log(2) = 2c. So c >= 2 works.")
    print()
    print("  Conclusion: T(n) = O(n log n) with c = 2, base at n = 2. QED.")


def show_common_recurrences():
    """Print a reference table of common recurrences."""
    print(f"\n{'=' * 65}")
    print("  COMMON RECURRENCES — REFERENCE TABLE")
    print(f"{'=' * 65}")
    print()

    table = [
        ("T(n) = T(n-1) + O(1)",    "O(n)",       "Factorial, linear scan"),
        ("T(n) = T(n-1) + O(n)",     "O(n^2)",     "Insertion sort (worst)"),
        ("T(n) = 2T(n-1) + O(1)",    "O(2^n)",     "Towers of Hanoi"),
        ("T(n) = T(n/2) + O(1)",     "O(log n)",   "Binary search"),
        ("T(n) = T(n/2) + O(n)",     "O(n)",       "Quickselect (average)"),
        ("T(n) = 2T(n/2) + O(1)",    "O(n)",       "Binary tree traversal"),
        ("T(n) = 2T(n/2) + O(n)",    "O(n log n)", "Merge sort"),
        ("T(n) = 2T(n/2) + O(n^2)",  "O(n^2)",     "Silly sort (root dominant)"),
        ("T(n) = 4T(n/2) + O(n)",    "O(n^2)",     "Naive matrix multiply variant"),
        ("T(n) = 7T(n/2) + O(n^2)",  "O(n^2.81)",  "Strassen matrix multiply"),
        ("T(n) = 3T(n/4) + O(n^2)",  "O(n^2)",     "Root-dominant example"),
    ]

    print(f"  {'Recurrence':<30}  {'Solution':<14}  {'Example'}")
    print(f"  {'-'*30}  {'-'*14}  {'-'*30}")
    for rec, sol, ex in table:
        print(f"  {rec:<30}  {sol:<14}  {ex}")


# ---------------------------------------------------------------------------
# Mystery recurrence for the student to figure out
# ---------------------------------------------------------------------------

def mystery_work(n):
    """Mystery recurrence. Run it, observe the ratios, figure out the complexity.

    Hint: look at the structure — how many recursive calls?
    On what fraction of n? How much non-recursive work?
    """
    if n <= 1:
        return 1
    work = n  # O(n) non-recursive work
    # 4 recursive calls on n/2
    return work + 4 * mystery_work(n // 2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    sys.setrecursionlimit(100000)

    print("Day 3: Recurrence Relations & Master Theorem")
    print("=" * 65)
    print()
    print("We will visualize recursion trees, apply the Master Theorem,")
    print("and verify predictions with empirical measurements.")

    # --- Recursion tree visualizations ---

    visualize_recursion_tree(2, 2, 1, 64, label="(Merge sort)")
    visualize_recursion_tree(7, 2, 2, 64, label="(Strassen-like)")
    visualize_recursion_tree(3, 4, 2, 256, label="(Root dominant)")
    visualize_recursion_tree(1, 2, 0, 64, label="(Binary search)")
    visualize_recursion_tree(4, 2, 1, 64, label="(Mystery — figure it out!)")

    # --- Substitution method walkthrough ---

    show_substitution_method()

    # --- Common recurrences reference ---

    show_common_recurrences()

    # --- Empirical verification ---

    print(f"\n{'=' * 65}")
    print("  EMPIRICAL VERIFICATION")
    print(f"{'=' * 65}")
    print("  Timing actual recursive functions to verify Master Theorem predictions.")

    verify_growth(
        "merge_sort_work: T(n) = 2T(n/2) + n  [Case 2: O(n log n)]",
        merge_sort_work,
        [2000, 4000, 8000, 16000, 32000],
        "~2.2x (n*log(n) grows slightly faster than 2x)"
    )

    verify_growth(
        "binary_search_work: T(n) = T(n/2) + 1  [O(log n)]",
        binary_search_work,
        [10000, 20000, 40000, 80000, 160000],
        "barely grows (adding one more step)"
    )

    verify_growth(
        "root_dominant_work: T(n) = 3T(n/4) + n^2  [Case 3: O(n^2)]",
        root_dominant_work,
        [1000, 2000, 4000, 8000, 16000],
        "~4x (quadratic)"
    )

    # Linear and quadratic recurrences (NOT Master Theorem form)
    verify_growth(
        "linear_recursion_work: T(n) = T(n-1) + 1  [O(n)]",
        linear_recursion_work,
        [2000, 4000, 8000, 16000, 32000],
        "~2x (linear)"
    )

    verify_growth(
        "quadratic_recursion_work: T(n) = T(n-1) + n  [O(n^2)]",
        quadratic_recursion_work,
        [1000, 2000, 4000, 8000],
        "~4x (quadratic)"
    )

    # --- Mystery recurrence ---

    print(f"\n{'=' * 65}")
    print("  MYSTERY RECURRENCE")
    print(f"{'=' * 65}")

    verify_growth(
        "mystery_work: T(n) = 4T(n/2) + n  [What case? What complexity?]",
        mystery_work,
        [1000, 2000, 4000, 8000, 16000],
        "You tell me! (hint: a=4, b=2, d=1, log_2(4)=?)"
    )

    print()
    print("  ANSWER: a=4, b=2, d=1. log_2(4) = 2 > 1 = d.")
    print("  Case 1: Leaves dominate. T(n) = O(n^2).")
    print("  When you double n, time should ~quadruple (4x).")
    print("  Check the ratios above — do they match?")

    print("\n" + "=" * 65)
    print("KEY TAKEAWAYS:")
    print("  1. Every recursive function has a recurrence relation")
    print("  2. Recursion trees reveal WHERE the work happens")
    print("  3. Master Theorem: compare d with log_b(a)")
    print("  4. Case 1 = leaves win, Case 2 = balanced, Case 3 = root wins")
    print("  5. Some recurrences (T(n-1)) do NOT fit the Master Theorem")
    print("=" * 65)
