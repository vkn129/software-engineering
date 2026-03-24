"""
Day 4 Practice: Master Theorem — Solve 10 Recurrence Relations

For each recurrence below:
1. Determine a, b, d (and log_power p if applicable)
2. Compute log_b(a)
3. Compare d with log_b(a) to determine the case
4. State the complexity
5. If the Master Theorem does NOT apply, explain WHY and solve another way

Fill in the TODO sections, then run this file to check your answers.

Run: python practice.py
"""

import math
from master_theorem import MasterTheoremChecker


# ---------------------------------------------------------------------------
# Exercise 1: T(n) = 4T(n/2) + n
# ---------------------------------------------------------------------------
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_b(a) = ?
# Compare d vs log_b(a): ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 2: T(n) = 2T(n/4) + sqrt(n)
# ---------------------------------------------------------------------------
# Hint: sqrt(n) = n^{1/2}, so d = 0.5
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_b(a) = ?
# Compare d vs log_b(a): ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 3: T(n) = 16T(n/4) + n
# ---------------------------------------------------------------------------
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_b(a) = ?
# Compare d vs log_b(a): ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 4: T(n) = 2T(n/2) + n * log(n)
# ---------------------------------------------------------------------------
# Hint: This has a log factor. Does the basic theorem apply?
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_power = ?
# log_b(a) = ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 5: T(n) = 7T(n/3) + n^2
# ---------------------------------------------------------------------------
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_b(a) = ?
# Compare d vs log_b(a): ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 6: T(n) = T(2n/3) + 1
# ---------------------------------------------------------------------------
# Hint: "2n/3" means b = 3/2 (size shrinks by factor 3/2 each time)
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_b(a) = ?
# Compare d vs log_b(a): ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 7: T(n) = T(n-2) + n^2
# ---------------------------------------------------------------------------
# Hint: Does the Master Theorem apply here?
# TODO: Your analysis
# Does MT apply? Why or why not?
# Solve using another method:
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 8: T(n) = 3T(n/3) + n/2
# ---------------------------------------------------------------------------
# Hint: n/2 = (1/2)*n, so f(n) = Theta(n). Constants do not change d.
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_b(a) = ?
# Compare d vs log_b(a): ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 9: T(n) = 4T(n/2) + n^2 * log(n)
# ---------------------------------------------------------------------------
# Hint: log_b(a) = 2 and d = 2, but there is a log factor.
# TODO: Your analysis
# a = ?
# b = ?
# d = ?
# log_power = ?
# log_b(a) = ?
# Case: ?
# Complexity: ?


# ---------------------------------------------------------------------------
# Exercise 10: T(n) = T(n/2) + T(n/3) + n
# ---------------------------------------------------------------------------
# Hint: Are the subproblems the same size?
# TODO: Your analysis
# Does MT apply? Why or why not?
# Solve using another method:
# Complexity: ?


# ===========================================================================
# SOLUTIONS — scroll down only after attempting all exercises above
# ===========================================================================


SOLUTIONS = {
    1: {
        'recurrence': 'T(n) = 4T(n/2) + n',
        'a': 4, 'b': 2, 'd': 1, 'log_power': 0,
        'log_b_a': 2.0,
        'case': 1,
        'complexity': 'Theta(n^2)',
        'explanation': (
            'log_2(4) = 2 > 1 = d. Case 1: leaves dominate.\n'
            'The tree branches 4 ways but each subproblem only halves.\n'
            'Leaves grow as n^2, overwhelming the linear work at each level.'
        ),
    },
    2: {
        'recurrence': 'T(n) = 2T(n/4) + sqrt(n)',
        'a': 2, 'b': 4, 'd': 0.5, 'log_power': 0,
        'log_b_a': 0.5,
        'case': 2,
        'complexity': 'Theta(sqrt(n) * log(n))',
        'explanation': (
            'log_4(2) = 0.5 = d. Case 2: balanced.\n'
            'Each level does sqrt(n) work, and there are log_4(n) levels.\n'
            'Total = sqrt(n) * log(n).'
        ),
    },
    3: {
        'recurrence': 'T(n) = 16T(n/4) + n',
        'a': 16, 'b': 4, 'd': 1, 'log_power': 0,
        'log_b_a': 2.0,
        'case': 1,
        'complexity': 'Theta(n^2)',
        'explanation': (
            'log_4(16) = 2 > 1 = d. Case 1: leaves dominate.\n'
            '16 subproblems of size n/4 each — the branching is explosive.\n'
            'n^{log_4(16)} = n^2 leaves, each doing O(1).'
        ),
    },
    4: {
        'recurrence': 'T(n) = 2T(n/2) + n*log(n)',
        'a': 2, 'b': 2, 'd': 1, 'log_power': 1,
        'log_b_a': 1.0,
        'case': '2-extended',
        'complexity': 'Theta(n * (log n)^2)',
        'explanation': (
            'log_2(2) = 1 = d, and f(n) = n*log(n) = n^1 * (log n)^1.\n'
            'Extended Case 2 with p = 1 > -1: Theta(n * (log n)^{1+1}) = Theta(n * (log n)^2).\n'
            'The basic Master Theorem does NOT directly handle this log factor.\n'
            'The log(n) extra factor at each level accumulates over log(n) levels.'
        ),
    },
    5: {
        'recurrence': 'T(n) = 7T(n/3) + n^2',
        'a': 7, 'b': 3, 'd': 2, 'log_power': 0,
        'log_b_a': round(math.log(7) / math.log(3), 4),
        'case': 3,
        'complexity': 'Theta(n^2)',
        'explanation': (
            f'log_3(7) = {math.log(7)/math.log(3):.4f} < 2 = d. Case 3: root dominates.\n'
            'The n^2 work at the root dwarfs the 7 subproblems of size n/3.\n'
            'Geometric series: n^2 * (1 + 7/9 + (7/9)^2 + ...) converges.'
        ),
    },
    6: {
        'recurrence': 'T(n) = T(2n/3) + 1',
        'a': 1, 'b': 1.5, 'd': 0, 'log_power': 0,
        'log_b_a': 0.0,
        'case': 2,
        'complexity': 'Theta(log(n))',
        'explanation': (
            'a=1, b=3/2, d=0. log_{3/2}(1) = 0 = d. Case 2: balanced.\n'
            'Each level does O(1) work, there are log_{3/2}(n) levels.\n'
            'This is like binary search but with a 2/3 split instead of 1/2.\n'
            'Same complexity class: Theta(log n).'
        ),
    },
    7: {
        'recurrence': 'T(n) = T(n-2) + n^2',
        'a': None, 'b': None, 'd': None, 'log_power': 0,
        'log_b_a': None,
        'case': 'inapplicable',
        'complexity': 'Theta(n^3)',
        'explanation': (
            'Master Theorem does NOT apply: subproblem size is n-2 (subtraction),\n'
            'not n/b (division). The input shrinks by a constant, not a factor.\n'
            '\n'
            'Solve by telescoping:\n'
            'T(n) = n^2 + (n-2)^2 + (n-4)^2 + ... + 4 + 0\n'
            '     = sum of k^2 for k = 0, 2, 4, ..., n (about n/2 terms)\n'
            '     ~ (1/2) * integral_0^n x^2 dx = n^3/6\n'
            '     = Theta(n^3).'
        ),
    },
    8: {
        'recurrence': 'T(n) = 3T(n/3) + n/2',
        'a': 3, 'b': 3, 'd': 1, 'log_power': 0,
        'log_b_a': 1.0,
        'case': 2,
        'complexity': 'Theta(n * log(n))',
        'explanation': (
            'log_3(3) = 1 = d. Case 2: balanced.\n'
            'The constant 1/2 in f(n) = n/2 does not change d.\n'
            'Big-O absorbs constants. Each level does Theta(n) work,\n'
            'there are log_3(n) levels. Total = Theta(n * log n).'
        ),
    },
    9: {
        'recurrence': 'T(n) = 4T(n/2) + n^2 * log(n)',
        'a': 4, 'b': 2, 'd': 2, 'log_power': 1,
        'log_b_a': 2.0,
        'case': '2-extended',
        'complexity': 'Theta(n^2 * (log n)^2)',
        'explanation': (
            'log_2(4) = 2 = d, and f(n) = n^2 * log(n).\n'
            'Extended Case 2 with p = 1 > -1: Theta(n^2 * (log n)^{1+1}).\n'
            'Without the extended form, you would incorrectly say Case 2 gives\n'
            'Theta(n^2 * log n), missing the extra log factor.'
        ),
    },
    10: {
        'recurrence': 'T(n) = T(n/2) + T(n/3) + n',
        'a': None, 'b': None, 'd': None, 'log_power': 0,
        'log_b_a': None,
        'case': 'inapplicable',
        'complexity': 'Theta(n)',
        'explanation': (
            'Master Theorem does NOT apply: the two subproblems have different sizes\n'
            '(n/2 and n/3). Cannot express as a*T(n/b) for a single b.\n'
            '\n'
            'Use recursion tree: level 0 work = n, level 1 = n/2 + n/3 = 5n/6,\n'
            'level 2 = n/4 + n/6 + n/6 + n/9 = ... each level sums to at most (5/6)*previous.\n'
            'Geometric series with ratio 5/6 < 1: root dominates.\n'
            'Total = n * (1 + 5/6 + (5/6)^2 + ...) = n * 6 = Theta(n).\n'
            '\n'
            'Alternatively, use Akra-Bazzi: sum of (1/2)^p + (1/3)^p = 1 gives p ≈ 0.79,\n'
            'and integral of n^{-0.79} * n / n dn gives Theta(n), confirming.'
        ),
    },
}


def print_solution(num):
    """Pretty-print one solution."""
    sol = SOLUTIONS[num]
    print(f"\n  Exercise {num}: {sol['recurrence']}")

    if sol['a'] is not None:
        print(f"    a={sol['a']}, b={sol['b']}, d={sol['d']}", end="")
        if sol['log_power'] != 0:
            print(f", log_power={sol['log_power']}", end="")
        print()
        if sol['log_b_a'] is not None:
            print(f"    log_b(a) = {sol['log_b_a']}")

    print(f"    Case: {sol['case']}")
    print(f"    Complexity: {sol['complexity']}")
    print(f"    Reasoning:")
    for line in sol['explanation'].split('\n'):
        print(f"      {line}")


def verify_with_checker():
    """Run the MasterTheoremChecker on exercises where it applies."""
    print("\n  Automated verification using MasterTheoremChecker:")
    print(f"  {'-'*55}")

    checkable = [
        (1, 4, 2, 1, 0),
        (2, 2, 4, 0.5, 0),
        (3, 16, 4, 1, 0),
        (4, 2, 2, 1, 1),
        (5, 7, 3, 2, 0),
        (6, 1, 1.5, 0, 0),
        (8, 3, 3, 1, 0),
        (9, 4, 2, 2, 1),
    ]

    for num, a, b, d, p in checkable:
        checker = MasterTheoremChecker(a, b, d, p)
        result = checker.classify()
        expected = SOLUTIONS[num]

        match = str(result['case']) == str(expected['case'])
        status = "OK" if match else "MISMATCH"

        p_str = f"*(log n)^{p}" if p != 0 else ""
        print(f"    Ex {num}: T={a}T(n/{b})+n^{d}{p_str}  "
              f"=> Case {result['case']}: {result['complexity']}  [{status}]")


if __name__ == "__main__":
    print("Day 4 Practice: Master Theorem — 10 Recurrence Relations")
    print("=" * 60)
    print()
    print("Have you filled in your answers in the TODO comments above?")
    print("Running verification and showing solutions...")

    # Show all solutions
    print(f"\n{'=' * 60}")
    print("  SOLUTIONS")
    print(f"{'=' * 60}")

    for i in range(1, 11):
        print_solution(i)

    # Verify with automated checker
    print(f"\n{'=' * 60}")
    print("  AUTOMATED VERIFICATION")
    print(f"{'=' * 60}")
    verify_with_checker()

    print(f"\n{'=' * 60}")
    print("KEY INSIGHTS:")
    print("  - Exercises 1,3: High branching (a >> b^d) makes leaves dominate")
    print("  - Exercises 2,6,8: When d = log_b(a), multiply by log(n)")
    print("  - Exercises 4,9: Log factors need the EXTENDED form")
    print("  - Exercise 5: Root dominates even with 7 subproblems (n^2 is big)")
    print("  - Exercises 7,10: Master Theorem has LIMITS — know them")
    print("=" * 60)
