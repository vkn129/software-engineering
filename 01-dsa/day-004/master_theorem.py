"""
Day 4: Master Theorem — Deep Dive and Automation

This script builds a Master Theorem checker from scratch. Given a, b, and
a description of f(n), it determines which case applies, explains WHY,
and verifies the prediction empirically.

The core insight: the Master Theorem is about whether a geometric series
grows, stays flat, or shrinks. We make that visible.

Run: python master_theorem.py
"""

import math
import time


# ---------------------------------------------------------------------------
# The Master Theorem Checker
# ---------------------------------------------------------------------------

class MasterTheoremChecker:
    """Analyzes recurrences of the form T(n) = a*T(n/b) + f(n).

    The checker encodes ALL the edge cases that textbooks gloss over:
    - What if a = 0? (no recursion — just f(n))
    - What if b = 1? (subproblem never shrinks — diverges)
    - What if f(n) has a log factor? (extended form needed)
    - What if f(n) is not polynomial? (theorem does not apply)

    Each check is a constraint from the theorem's preconditions.
    Missing any one of them leads to wrong answers in practice.
    """

    def __init__(self, a, b, d, log_power=0):
        """Initialize with recurrence parameters.

        T(n) = a * T(n/b) + Theta(n^d * (log n)^p)

        Args:
            a: Number of subproblems (must be >= 1 for recursion to exist)
            b: Factor by which subproblem size shrinks (must be > 1)
            d: Exponent of n in the non-recursive work
            log_power: Exponent p of the log factor (0 means no log factor)
        """
        self.a = a
        self.b = b
        self.d = d
        self.log_power = log_power

        # Precompute the critical exponent — this is the ENTIRE key to
        # the Master Theorem. Everything is a comparison against this number.
        if a > 0 and b > 1:
            self.log_b_a = math.log(a) / math.log(b)
        else:
            self.log_b_a = None

    def validate(self):
        """Check preconditions. Returns (is_valid, error_message).

        These preconditions are NOT arbitrary — each corresponds to a
        physical constraint on the recursion tree:
        - a >= 1: you must have at least one recursive call (otherwise no recurrence)
        - b > 1: each call must handle a strictly smaller input (otherwise no progress)
        - d >= 0: polynomial work must be non-negative
        """
        errors = []

        if self.a < 1:
            errors.append(
                f"a = {self.a}: Need a >= 1. With a < 1 there are no recursive calls, "
                f"so T(n) = f(n) directly — no recurrence to solve."
            )

        if self.b <= 1:
            errors.append(
                f"b = {self.b}: Need b > 1. If b <= 1, subproblems do not shrink, "
                f"so the recursion never terminates. This is an infinite loop, not an algorithm."
            )

        if self.d < 0:
            errors.append(
                f"d = {self.d}: Need d >= 0. Negative d means f(n) = n^d -> 0 as n grows, "
                f"which is unusual but technically valid. Proceeding with caution."
            )

        if not isinstance(self.a, int) or (not isinstance(self.b, int) and not isinstance(self.b, float)):
            # Non-integer a is allowed in the general theorem but unusual
            pass

        return len(errors) == 0, errors

    def classify(self):
        """Determine which case of the Master Theorem applies.

        Returns a dict with:
            'case': 1, 2, 3, or 'extended' or 'inapplicable'
            'complexity': string representation of the bound
            'explanation': why this case applies
            'geometric_ratio': the ratio a/b^d that determines everything
        """
        is_valid, errors = self.validate()
        if not is_valid:
            return {
                'case': 'inapplicable',
                'complexity': 'Cannot determine',
                'explanation': 'Precondition violated: ' + '; '.join(errors),
                'geometric_ratio': None
            }

        ratio = self.a / (self.b ** self.d)
        epsilon = 1e-9  # floating point tolerance

        # The three cases correspond to whether the geometric series
        # sum_{k=0}^{L} r^k (where r = a/b^d, L = log_b(n))
        # is dominated by its last term, is flat, or is dominated by first term.

        if abs(self.d - self.log_b_a) < epsilon:
            # Case 2 territory: d = log_b(a), possibly with log factors
            return self._classify_case2(ratio)
        elif self.d < self.log_b_a - epsilon:
            # Case 1: leaves dominate
            return self._classify_case1(ratio)
        else:
            # Case 3: root dominates
            return self._classify_case3(ratio)

    def _classify_case1(self, ratio):
        """Case 1: d < log_b(a). Leaves dominate.

        The geometric series ratio r = a/b^d > 1, so the series GROWS.
        The last term (leaves) dominates. Total work = Theta(n^{log_b(a)}).

        The log factor in f(n) does not matter here — leaves overwhelm
        everything regardless of polylog factors at the root.
        """
        complexity = f"Theta(n^{self.log_b_a:.4f})"
        if abs(self.log_b_a - round(self.log_b_a)) < 1e-9:
            complexity = f"Theta(n^{int(round(self.log_b_a))})"

        return {
            'case': 1,
            'complexity': complexity,
            'explanation': (
                f"d = {self.d} < log_{self.b}({self.a}) = {self.log_b_a:.4f}\n"
                f"  Geometric ratio r = a/b^d = {ratio:.4f} > 1\n"
                f"  The series GROWS: each level does MORE work than the previous.\n"
                f"  Leaves dominate. There are n^{{log_b(a)}} = n^{self.log_b_a:.4f} leaves,\n"
                f"  each doing O(1) work. Total = {complexity}."
            ),
            'geometric_ratio': ratio
        }

    def _classify_case2(self, ratio):
        """Case 2: d = log_b(a). Balanced — every level does equal work.

        The geometric series ratio r = 1, so all log_b(n) terms are equal.
        With a log factor (log n)^p in f(n), the extended form applies:
        - p > -1: Theta(n^d * (log n)^{p+1})
        - p = -1: Theta(n^d * log(log n))
        - p < -1: Theta(n^d)
        """
        p = self.log_power

        if p == 0:
            # Standard Case 2: no log factor
            complexity = f"Theta(n^{self.d} * log(n))"
            if self.d == 0:
                complexity = "Theta(log(n))"
            elif self.d == 1:
                complexity = "Theta(n * log(n))"

            return {
                'case': 2,
                'complexity': complexity,
                'explanation': (
                    f"d = {self.d} = log_{self.b}({self.a}) = {self.log_b_a:.4f}\n"
                    f"  Geometric ratio r = a/b^d = {ratio:.4f} = 1\n"
                    f"  The series is FLAT: every level does Theta(n^{self.d}) work.\n"
                    f"  There are log_{self.b}(n) levels.\n"
                    f"  Total = n^{self.d} * log(n) = {complexity}."
                ),
                'geometric_ratio': ratio
            }
        elif p > -1:
            new_p = p + 1
            if new_p == 1:
                complexity = f"Theta(n^{self.d} * log(n))"
            else:
                complexity = f"Theta(n^{self.d} * (log n)^{new_p})"

            return {
                'case': '2-extended',
                'complexity': complexity,
                'explanation': (
                    f"d = {self.d} = log_{self.b}({self.a}), with f(n) = n^{self.d} * (log n)^{p}\n"
                    f"  Extended Case 2 with p = {p} > -1.\n"
                    f"  Each level's work is n^{self.d} * (log(n/b^k))^{p}.\n"
                    f"  Summing over log_b(n) levels: {complexity}."
                ),
                'geometric_ratio': ratio
            }
        elif abs(p - (-1)) < 1e-9:
            complexity = f"Theta(n^{self.d} * log(log n))"
            return {
                'case': '2-extended',
                'complexity': complexity,
                'explanation': (
                    f"d = {self.d} = log_{self.b}({self.a}), with f(n) = n^{self.d} / log(n)\n"
                    f"  Extended Case 2 with p = -1 (critical boundary).\n"
                    f"  The sum becomes a harmonic-like series: {complexity}."
                ),
                'geometric_ratio': ratio
            }
        else:
            complexity = f"Theta(n^{self.d})"
            return {
                'case': '2-extended',
                'complexity': complexity,
                'explanation': (
                    f"d = {self.d} = log_{self.b}({self.a}), with f(n) = n^{self.d} * (log n)^{p}\n"
                    f"  Extended Case 2 with p = {p} < -1.\n"
                    f"  The log factor shrinks fast enough that leaves dominate: {complexity}."
                ),
                'geometric_ratio': ratio
            }

    def _classify_case3(self, ratio):
        """Case 3: d > log_b(a). Root dominates.

        The geometric series ratio r = a/b^d < 1, so the series SHRINKS.
        The first term (root) dominates. Total work = Theta(f(n)).

        IMPORTANT: This case requires the regularity condition:
        a * f(n/b) <= c * f(n) for some c < 1.
        For f(n) = n^d, regularity holds when d > log_b(a) because
        a * (n/b)^d = a/b^d * n^d = r * n^d with r < 1.
        """
        p = self.log_power
        if p == 0:
            complexity = f"Theta(n^{self.d})"
        else:
            complexity = f"Theta(n^{self.d} * (log n)^{p})"

        # Verify regularity condition for polynomial f(n)
        regularity_c = self.a / (self.b ** self.d)
        regularity_holds = regularity_c < 1

        reg_note = ""
        if not regularity_holds:
            reg_note = (
                "\n  WARNING: Regularity condition may not hold! "
                "a*f(n/b)/f(n) = {regularity_c:.4f} >= 1."
            )

        return {
            'case': 3,
            'complexity': complexity,
            'explanation': (
                f"d = {self.d} > log_{self.b}({self.a}) = {self.log_b_a:.4f}\n"
                f"  Geometric ratio r = a/b^d = {ratio:.4f} < 1\n"
                f"  The series SHRINKS: each level does LESS work than the previous.\n"
                f"  Root dominates. The top level does Theta(n^{self.d}) work,\n"
                f"  and everything below sums to a constant fraction of that.\n"
                f"  Regularity: a*f(n/b)/f(n) = {regularity_c:.4f} < 1. OK.\n"
                f"  Total = {complexity}.{reg_note}"
            ),
            'geometric_ratio': ratio
        }

    def show_geometric_series(self, n):
        """Visualize the geometric series at each tree level.

        This is the CORE visualization: you can literally SEE whether
        the series grows (Case 1), stays flat (Case 2), or shrinks (Case 3).
        """
        if self.log_b_a is None:
            print("  Cannot visualize: invalid parameters.")
            return

        height = int(math.log(n) / math.log(self.b)) if n > 1 else 0
        ratio = self.a / (self.b ** self.d)

        print(f"\n  Geometric series visualization for n = {n}:")
        print(f"  Ratio r = a/b^d = {self.a}/{self.b}^{self.d} = {ratio:.4f}")
        print()

        max_bar = 50  # max width of bar chart
        level_works = []

        for k in range(min(height + 1, 20)):  # cap at 20 levels for display
            # Work at level k: n^d * (a/b^d)^k
            work = (n ** self.d) * (ratio ** k)
            level_works.append(work)

        if not level_works:
            return

        max_work = max(level_works)

        for k, work in enumerate(level_works):
            bar_len = int((work / max_work) * max_bar) if max_work > 0 else 0
            bar = '#' * bar_len
            subproblems = self.a ** k
            size = n / (self.b ** k)
            print(f"  Level {k:>2}: {bar:<50}  work={work:>12.0f}  ({subproblems} x {size:.0f}^{self.d})")

        total = sum(level_works)
        print(f"\n  Sum of all levels: {total:.0f}")
        if ratio > 1:
            print(f"  Series GROWS (r={ratio:.3f} > 1) — last level dominates.")
        elif abs(ratio - 1) < 1e-9:
            print(f"  Series FLAT (r={ratio:.3f} = 1) — all levels contribute equally.")
        else:
            print(f"  Series SHRINKS (r={ratio:.3f} < 1) — first level dominates.")


# ---------------------------------------------------------------------------
# Demonstrate all three cases with proofs
# ---------------------------------------------------------------------------

def demonstrate_case(a, b, d, label, log_power=0):
    """Run the full analysis for one recurrence."""
    p_str = ""
    if log_power != 0:
        p_str = f" * (log n)^{log_power}"

    print(f"\n{'=' * 70}")
    print(f"  T(n) = {a}T(n/{b}) + Theta(n^{d}{p_str})    [{label}]")
    print(f"{'=' * 70}")

    checker = MasterTheoremChecker(a, b, d, log_power)
    result = checker.classify()

    print(f"\n  Case: {result['case']}")
    print(f"  Complexity: {result['complexity']}")
    print(f"\n  Analysis:")
    for line in result['explanation'].split('\n'):
        print(f"    {line}")

    checker.show_geometric_series(1024)

    return checker, result


# ---------------------------------------------------------------------------
# Empirical verification
# ---------------------------------------------------------------------------

def make_recursive_counter(a, b, d):
    """Create a function that counts work for T(n) = a*T(n/b) + n^d.

    We cannot actually recurse with a=7 on large n (exponential blowup),
    so we compute the work ANALYTICALLY using the recursion tree formula.
    This is exact — no approximation.
    """
    def count_work(n):
        if n <= 1:
            return 1
        total = 0
        level = 0
        size = n
        while size >= 1:
            # Work at this level: a^level * size^d
            work = (a ** level) * (size ** d)
            total += work
            level += 1
            size = n / (b ** level)
        return total
    return count_work


def verify_empirically(a, b, d, label, sizes):
    """Time the work counter at increasing sizes and show growth ratios."""
    counter = make_recursive_counter(a, b, d)

    print(f"\n  Empirical verification: {label}")
    print(f"  {'n':>10}  {'Work':>15}  {'Ratio':>8}")
    print(f"  {'-'*10}  {'-'*15}  {'-'*8}")

    prev_work = None
    for n in sizes:
        work = counter(n)
        if prev_work and prev_work > 0:
            ratio_str = f"{work / prev_work:.3f}x"
        else:
            ratio_str = "--"
        print(f"  {n:>10}  {work:>15.0f}  {ratio_str:>8}")
        prev_work = work


# ---------------------------------------------------------------------------
# Proof of the leaf count identity
# ---------------------------------------------------------------------------

def prove_leaf_identity():
    """Demonstrate that a^{log_b(n)} = n^{log_b(a)}.

    This identity is the KEY to the Master Theorem. Without it,
    you cannot express the leaf count in terms of n.

    Proof:
      Let x = log_b(n), so n = b^x.
      a^{log_b(n)} = a^x
      n^{log_b(a)} = (b^x)^{log_b(a)} = b^{x * log_b(a)} = (b^{log_b(a)})^x = a^x

    Both sides equal a^x. QED.
    """
    print(f"\n{'=' * 70}")
    print("  PROOF: a^{log_b(n)} = n^{log_b(a)}  (Leaf Count Identity)")
    print(f"{'=' * 70}")
    print()
    print("  This identity lets us express the number of leaves in terms of n.")
    print("  The recursion tree for T(n) = aT(n/b) + f(n) has:")
    print("    - Height: log_b(n)")
    print("    - Branching factor: a at each node")
    print("    - Leaves: a^{height} = a^{log_b(n)}")
    print()
    print("  Proof that a^{log_b(n)} = n^{log_b(a)}:")
    print("    Let x = log_b(n), so n = b^x.")
    print("    LHS = a^{log_b(n)} = a^x")
    print("    RHS = n^{log_b(a)} = (b^x)^{log_b(a)} = b^{x * log_b(a)}")
    print("        = (b^{log_b(a)})^x = a^x")
    print("    LHS = RHS. QED.")
    print()
    print("  Numerical verification:")

    test_cases = [(2, 2, 64), (3, 4, 256), (7, 2, 128), (5, 3, 243)]
    for a, b, n in test_cases:
        lhs = a ** (math.log(n) / math.log(b))
        rhs = n ** (math.log(a) / math.log(b))
        print(f"    a={a}, b={b}, n={n}: a^{{log_b(n)}} = {lhs:.4f}, n^{{log_b(a)}} = {rhs:.4f}, match: {abs(lhs - rhs) < 0.01}")


# ---------------------------------------------------------------------------
# Edge cases and failure modes
# ---------------------------------------------------------------------------

def show_failure_modes():
    """Demonstrate inputs where the Master Theorem breaks down.

    Every theorem has boundary conditions. Knowing WHERE it fails
    is just as important as knowing where it works.
    """
    print(f"\n{'=' * 70}")
    print("  FAILURE MODES: When the Master Theorem Does NOT Apply")
    print(f"{'=' * 70}")

    # Failure 1: Subtraction instead of division
    print(f"\n  --- Failure 1: Subtraction recurrence ---")
    print(f"  T(n) = T(n-1) + n")
    print(f"  The Master Theorem requires T(n/b) with b > 1.")
    print(f"  T(n-1) means subproblem shrinks by 1, not by a factor.")
    print(f"  This is a LINEAR recurrence: T(n) = n + (n-1) + ... + 1 = n(n+1)/2 = Theta(n^2).")
    print(f"  Use telescoping, not the Master Theorem.")

    # Failure 2: Unequal subproblems
    print(f"\n  --- Failure 2: Unequal subproblems ---")
    print(f"  T(n) = T(n/3) + T(2n/3) + n")
    print(f"  Both subproblems divide n, but by DIFFERENT factors.")
    print(f"  Cannot express as a*T(n/b) because a and b are not consistent.")
    print(f"  Use Akra-Bazzi theorem: T(n) = Theta(n * log n).")
    print(f"  (The longest path has log_{3/2}(n) levels, each doing O(n) total work.)")

    # Failure 3: Exponential f(n)
    print(f"\n  --- Failure 3: Non-polynomial f(n) ---")
    print(f"  T(n) = 2T(n/2) + 2^n")
    print(f"  f(n) = 2^n is not Theta(n^d) for any d.")
    print(f"  Exponential functions grow faster than ANY polynomial.")
    print(f"  The Master Theorem's polynomial comparison does not apply.")
    print(f"  Solution: f(n) = 2^n dominates everything. T(n) = Theta(2^n).")

    # Failure 4: Variable number of subproblems
    print(f"\n  --- Failure 4: Variable branching ---")
    print(f"  T(n) = n * T(n/2) + n")
    print(f"  a = n is not a constant! The Master Theorem requires a to be")
    print(f"  independent of n. Here the tree fans out more at each level,")
    print(f"  making the analysis much harder. Use generating functions.")

    # Failure 5: The log gap
    print(f"\n  --- Failure 5: The log gap ---")
    print(f"  T(n) = 2T(n/2) + n * log(n)")
    print(f"  Here a=2, b=2, and f(n) = n*log(n).")
    print(f"  log_b(a) = 1, and f(n) = n^1 * log(n).")
    print(f"  f(n) is LARGER than n^1 but NOT polynomially larger (only by log).")
    print(f"  Falls in the 'gap' between Case 2 and Case 3.")
    print(f"  Extended form: d=1 = log_b(a), p=1 > -1. Theta(n * (log n)^2).")

    checker = MasterTheoremChecker(2, 2, 1, log_power=1)
    result = checker.classify()
    print(f"  Our checker says: {result['complexity']}")


# ---------------------------------------------------------------------------
# Batch analysis — solve many recurrences at once
# ---------------------------------------------------------------------------

def batch_analysis():
    """Analyze a collection of famous recurrences."""
    print(f"\n{'=' * 70}")
    print("  BATCH ANALYSIS: Famous Recurrences")
    print(f"{'=' * 70}")
    print()

    recurrences = [
        # (a, b, d, p, label)
        (2, 2, 1, 0, "Merge sort"),
        (1, 2, 0, 0, "Binary search"),
        (2, 2, 0, 0, "Tree traversal"),
        (7, 2, 2, 0, "Strassen multiplication"),
        (4, 2, 2, 0, "Karatsuba-like (a=4, d=2)"),
        (3, 2, 2, 0, "Karatsuba (a=3, b=2, d=2)"),
        (3, 4, 1, 0, "Root-dominant example"),
        (8, 2, 1, 0, "Heavy branching"),
        (9, 3, 2, 0, "Balanced (9 subs, /3, n^2)"),
        (1, 2, 1, 0, "Quickselect average"),
        (2, 2, 1, 1, "Extended: n*log(n) merge variant"),
        (4, 2, 2, 1, "Extended: n^2*log(n) with a=4"),
        (2, 2, 1, -1, "Extended: n/log(n) in gap"),
    ]

    print(f"  {'Recurrence':<40} {'Case':<12} {'Complexity':<30}")
    print(f"  {'-'*40} {'-'*12} {'-'*30}")

    for a, b, d, p, label in recurrences:
        checker = MasterTheoremChecker(a, b, d, p)
        result = checker.classify()

        p_str = ""
        if p != 0:
            p_str = f"*(log n)^{p}"
        rec_str = f"T={a}T(n/{b})+n^{d}{p_str}"

        print(f"  {rec_str:<40} {str(result['case']):<12} {result['complexity']:<30}  [{label}]")


# ---------------------------------------------------------------------------
# Interactive checker — feed it your own recurrences
# ---------------------------------------------------------------------------

def interactive_demo():
    """Show how to use the checker on custom recurrences."""
    print(f"\n{'=' * 70}")
    print("  HOW TO USE THE CHECKER")
    print(f"{'=' * 70}")
    print()
    print("  To analyze your own recurrence in Python:")
    print()
    print("    from master_theorem import MasterTheoremChecker")
    print()
    print("    # T(n) = 3T(n/2) + n^2")
    print("    checker = MasterTheoremChecker(a=3, b=2, d=2)")
    print("    result = checker.classify()")
    print("    print(result['case'], result['complexity'])")
    print()
    print("    # Extended: T(n) = 4T(n/2) + n^2 * log(n)")
    print("    checker = MasterTheoremChecker(a=4, b=2, d=2, log_power=1)")
    print("    result = checker.classify()")
    print("    print(result['case'], result['complexity'])")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Day 4: Master Theorem — Deep Dive and Automation")
    print("=" * 70)
    print()
    print("We build a Master Theorem checker, prove WHY each case works,")
    print("and explore every edge case where the theorem breaks down.")

    # --- Prove the leaf count identity first ---
    prove_leaf_identity()

    # --- Case 1: Leaves dominate ---
    demonstrate_case(8, 2, 1, "Case 1 — Leaves dominate (heavy branching)")
    verify_empirically(8, 2, 1, "8T(n/2) + n: should see ~8x when doubling (n^3)",
                       [64, 128, 256, 512, 1024])

    # --- Case 2: Balanced ---
    demonstrate_case(2, 2, 1, "Case 2 — Balanced (merge sort)")
    verify_empirically(2, 2, 1, "2T(n/2) + n: should see ~2.2x when doubling (n log n)",
                       [1000, 2000, 4000, 8000, 16000])

    # --- Case 3: Root dominates ---
    demonstrate_case(3, 4, 2, "Case 3 — Root dominates")
    verify_empirically(3, 4, 2, "3T(n/4) + n^2: should see ~4x when doubling (n^2)",
                       [1000, 2000, 4000, 8000, 16000])

    # --- Extended Case 2 with log factor ---
    demonstrate_case(4, 2, 2, "Case 2 with log factor", log_power=1)

    # --- Failure modes ---
    show_failure_modes()

    # --- Batch analysis ---
    batch_analysis()

    # --- How to use ---
    interactive_demo()

    # --- Empirical comparison of all three cases side by side ---
    print(f"\n{'=' * 70}")
    print("  SIDE-BY-SIDE COMPARISON: Three Cases")
    print(f"{'=' * 70}")
    print()
    print("  All three recurrences have b=2 and f(n)=n. Only 'a' changes.")
    print("  This isolates the effect of branching factor.")
    print()

    for a, case_label in [(4, "Case 1: a=4, leaves win"), (2, "Case 2: a=2, balanced"), (1, "Case 3: a=1, root wins")]:
        verify_empirically(a, 2, 1, f"{a}T(n/2) + n: {case_label}",
                           [1000, 2000, 4000, 8000, 16000])

    print(f"\n{'=' * 70}")
    print("KEY TAKEAWAYS:")
    print("  1. The Master Theorem is about one geometric series: r = a/b^d")
    print("  2. r > 1: leaves dominate (Case 1)")
    print("  3. r = 1: balanced, multiply by log n (Case 2)")
    print("  4. r < 1: root dominates (Case 3)")
    print("  5. Extended form handles log factors in f(n)")
    print("  6. The theorem FAILS for: subtraction recurrences, unequal splits,")
    print("     non-polynomial f(n), variable branching")
    print("  7. Always verify with empirical measurement — theory without")
    print("     measurement is faith, not engineering")
    print("=" * 70)
