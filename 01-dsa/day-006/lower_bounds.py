"""
Day 6: Lower Bounds — Why Comparison Sorting Can't Beat O(n log n)

This script builds the mathematical machinery of lower bound proofs
from scratch: decision trees, Stirling's approximation, information-
theoretic arguments, and adversary strategies.

Every proof is both stated mathematically AND verified computationally,
so you can see that the math actually matches reality.

Run: python lower_bounds.py
"""

import math
import time
import random


# ---------------------------------------------------------------------------
# Section 1: Factorial and Stirling's Approximation
# ---------------------------------------------------------------------------
# WHY: The sorting lower bound rests on log2(n!). We need to compute this
# exactly and via approximation to see that Stirling's formula is tight.

def exact_log2_factorial(n):
    """Compute log2(n!) exactly using Python's arbitrary-precision integers.

    We compute n! first (Python handles big integers natively), then take
    log2. This is the ground truth we compare approximations against.
    """
    factorial_n = math.factorial(n)
    return math.log2(factorial_n)


def stirling_log2_factorial(n):
    """Stirling's approximation: log2(n!) ~ n*log2(n) - n*log2(e) + 0.5*log2(2*pi*n)

    This comes from Stirling's formula: n! ~ sqrt(2*pi*n) * (n/e)^n
    Taking log2 of both sides gives us the expression above.

    The first two terms dominate, giving the familiar n*log2(n) bound.
    The third term is a lower-order correction.
    """
    if n <= 1:
        return 0.0
    # Full Stirling: log2(sqrt(2*pi*n)) + n*log2(n/e)
    return 0.5 * math.log2(2 * math.pi * n) + n * math.log2(n / math.e)


def simple_lower_bound(n):
    """The simplified bound: log2(n!) >= n*log2(n) - n*log2(e)

    This drops the sqrt(2*pi*n) correction term.
    It is a lower bound on the number of comparisons any comparison
    sort must make in the worst case.
    """
    if n <= 1:
        return 0.0
    return n * math.log2(n) - n * math.log2(math.e)


def demo_stirling():
    """Show how Stirling's approximation converges to the exact value."""
    print("=" * 70)
    print("STIRLING'S APPROXIMATION vs EXACT log2(n!)")
    print("=" * 70)
    print()
    print(f"{'n':>6} | {'Exact log2(n!)':>16} | {'Stirling':>16} | {'Simple':>16} | {'Stirling Err%':>14}")
    print("-" * 75)

    for n in [3, 5, 7, 10, 15, 20, 50, 100, 1000]:
        exact = exact_log2_factorial(n)
        stirling = stirling_log2_factorial(n)
        simple = simple_lower_bound(n)
        err_pct = abs(stirling - exact) / exact * 100 if exact > 0 else 0

        print(f"{n:>6} | {exact:>16.4f} | {stirling:>16.4f} | {simple:>16.4f} | {err_pct:>13.6f}%")

    print()
    print("KEY INSIGHT: Stirling's error shrinks rapidly. Even for n=10,")
    print("the approximation is within 1%. The n*log2(n) term dominates.")
    print()


# ---------------------------------------------------------------------------
# Section 2: Decision Tree Model
# ---------------------------------------------------------------------------
# WHY: The decision tree is the formal model that makes the lower bound
# proof rigorous. We build one explicitly for small n to see it work.

class DecisionTreeNode:
    """A node in a comparison-based decision tree.

    Internal nodes represent comparisons (is arr[i] < arr[j]?).
    Leaves represent the algorithm's output (a specific permutation).

    The tree's height = worst-case number of comparisons.
    """
    def __init__(self, comparison=None, left=None, right=None, result=None):
        # comparison is a tuple (i, j) meaning "compare positions i and j"
        self.comparison = comparison
        self.left = left        # taken when arr[i] < arr[j]
        self.right = right      # taken when arr[i] >= arr[j]
        self.result = result    # leaf: the sorted permutation


def build_sorting_tree_3():
    """Build the OPTIMAL decision tree for sorting 3 elements.

    For n=3, there are 3! = 6 permutations. A binary tree needs at least
    ceil(log2(6)) = 3 levels. Can we achieve height 3? Yes!

    This tree sorts elements at indices 0, 1, 2 using exactly 3 comparisons
    in the worst case, which matches the lower bound.
    """
    # The tree compares a[0] vs a[1], then branches based on the result,
    # making further comparisons to determine the full ordering.
    #
    # Each leaf is the sorted order as indices: e.g., (1, 0, 2) means
    # the sorted order is a[1] <= a[0] <= a[2].

    tree = DecisionTreeNode(
        comparison=(0, 1),  # Compare a[0] vs a[1]
        left=DecisionTreeNode(  # a[0] < a[1]
            comparison=(1, 2),  # Compare a[1] vs a[2]
            left=DecisionTreeNode(result=(0, 1, 2)),   # a[0] < a[1] < a[2]
            right=DecisionTreeNode(  # a[0] < a[1], a[1] >= a[2]
                comparison=(0, 2),  # Compare a[0] vs a[2]
                left=DecisionTreeNode(result=(0, 2, 1)),   # a[0] < a[2] <= a[1]
                right=DecisionTreeNode(result=(2, 0, 1)),  # a[2] <= a[0] < a[1]
            ),
        ),
        right=DecisionTreeNode(  # a[0] >= a[1]
            comparison=(0, 2),  # Compare a[0] vs a[2]
            left=DecisionTreeNode(result=(1, 0, 2)),   # a[1] <= a[0] < a[2]
            right=DecisionTreeNode(  # a[1] <= a[0], a[0] >= a[2]
                comparison=(1, 2),  # Compare a[1] vs a[2]
                left=DecisionTreeNode(result=(1, 2, 0)),   # a[1] < a[2] <= a[0]
                right=DecisionTreeNode(result=(2, 1, 0)),  # a[2] <= a[1] <= a[0]
            ),
        ),
    )
    return tree


def tree_height(node):
    """Compute the height of a decision tree (max comparisons on any path)."""
    if node is None or node.result is not None:
        return 0
    return 1 + max(tree_height(node.left), tree_height(node.right))


def count_leaves(node):
    """Count the number of leaves (distinct outcomes) in the tree."""
    if node is None:
        return 0
    if node.result is not None:
        return 1
    return count_leaves(node.left) + count_leaves(node.right)


def sort_with_tree(tree, arr):
    """Use the decision tree to sort an array of 3 elements.

    This demonstrates that the tree IS a sorting algorithm:
    traverse from root to leaf, making comparisons at each node,
    and the leaf tells you the sorted order.
    """
    node = tree
    comparisons = 0

    while node.result is None:
        i, j = node.comparison
        comparisons += 1
        if arr[i] < arr[j]:
            node = node.left
        else:
            node = node.right

    # node.result is a tuple of indices in sorted order
    sorted_arr = [arr[idx] for idx in node.result]
    return sorted_arr, comparisons


def demo_decision_tree():
    """Build and verify the optimal decision tree for sorting 3 elements."""
    print("=" * 70)
    print("DECISION TREE MODEL FOR SORTING 3 ELEMENTS")
    print("=" * 70)
    print()

    tree = build_sorting_tree_3()
    h = tree_height(tree)
    leaves = count_leaves(tree)
    theoretical_min = math.ceil(math.log2(math.factorial(3)))

    print(f"Tree properties:")
    print(f"  Leaves (distinct outcomes):  {leaves}")
    print(f"  Required leaves (3! = 6):    {math.factorial(3)}")
    print(f"  Tree height (worst case):    {h}")
    print(f"  Theoretical minimum height:  ceil(log2(6)) = {theoretical_min}")
    print(f"  Tree is optimal:             {h == theoretical_min}")
    print()

    # Verify the tree correctly sorts ALL permutations of 3 elements
    print("Verifying tree sorts all permutations correctly:")
    from itertools import permutations
    all_correct = True
    for perm in permutations([1, 2, 3]):
        arr = list(perm)
        sorted_arr, comps = sort_with_tree(tree, arr)
        correct = sorted_arr == sorted(arr)
        all_correct = all_correct and correct
        status = "OK" if correct else "FAIL"
        print(f"  Input: {arr} -> {sorted_arr} ({comps} comparisons) [{status}]")

    print(f"\nAll permutations sorted correctly: {all_correct}")
    print()

    # Show the lower bound for larger n
    print("Lower bound on comparisons for sorting n elements:")
    print(f"{'n':>6} | {'n!':>20} | {'ceil(log2(n!))':>16} | {'Best known':>12}")
    print("-" * 60)
    # Best known upper bounds for small n (comparison count for optimal sorting networks)
    best_known = {3: 3, 4: 5, 5: 7, 6: 10, 7: 13, 8: 16, 10: 22, 12: 30}
    for n in [3, 4, 5, 6, 7, 8, 10, 12]:
        fact = math.factorial(n)
        lower = math.ceil(math.log2(fact))
        upper = best_known.get(n, "?")
        print(f"{n:>6} | {fact:>20} | {lower:>16} | {upper:>12}")

    print()
    print("INSIGHT: The lower bound and best known are very close.")
    print("For n=3, they match exactly — the tree we built IS optimal.")
    print("For larger n, there is a small gap, meaning we do not know")
    print("if the lower bound or the upper bound (or both) can be improved.")
    print()


# ---------------------------------------------------------------------------
# Section 3: Information-Theoretic Argument
# ---------------------------------------------------------------------------
# WHY: The information-theoretic view generalizes the decision tree argument.
# Each comparison reveals at most 1 bit. To distinguish K outcomes, you
# need at least log2(K) bits, hence log2(K) comparisons.

def information_lower_bound(num_outcomes):
    """Compute the information-theoretic lower bound.

    If there are K possible outcomes and each query reveals 1 bit,
    we need at least ceil(log2(K)) queries.
    """
    if num_outcomes <= 1:
        return 0
    return math.ceil(math.log2(num_outcomes))


def demo_information_theory():
    """Show information-theoretic lower bounds for various problems."""
    print("=" * 70)
    print("INFORMATION-THEORETIC LOWER BOUNDS")
    print("=" * 70)
    print()
    print("Each comparison reveals at most 1 bit of information.")
    print("To distinguish K outcomes, we need >= ceil(log2(K)) comparisons.")
    print()

    problems = [
        ("Sorting 3 elements", math.factorial(3), "3! permutations"),
        ("Sorting 5 elements", math.factorial(5), "5! permutations"),
        ("Sorting 10 elements", math.factorial(10), "10! permutations"),
        ("Binary search in 8", 8, "8 possible positions"),
        ("Binary search in 1024", 1024, "1024 possible positions"),
        ("Binary search in 1000", 1000, "1000 possible positions"),
        ("Finding max of 5", 5, "5 candidates"),
        ("Finding 2nd largest of 5", 5 * 4, "5*4 ordered pairs"),
        ("Guessing a number 1-100", 100, "100 possibilities"),
    ]

    print(f"{'Problem':<30} | {'Outcomes (K)':>14} | {'Lower bound':>12} | {'Why'}")
    print("-" * 85)
    for name, k, reason in problems:
        lb = information_lower_bound(k)
        print(f"{name:<30} | {k:>14} | {lb:>12} | {reason}")

    print()
    print("SUBTLETY: For finding the maximum, the information-theoretic bound")
    print("gives ceil(log2(n)) = ceil(log2(5)) = 3, but the true lower bound")
    print("is n-1 = 4. Information theory gives a NECESSARY but not always")
    print("SUFFICIENT bound. The adversary argument gives the tight bound here.")
    print()


# ---------------------------------------------------------------------------
# Section 4: Adversary Argument for Finding Maximum
# ---------------------------------------------------------------------------
# WHY: The adversary argument is the most powerful technique for proving
# lower bounds. It works by constructing a worst-case opponent who forces
# the algorithm to gather maximum information.

class MaxFindingAdversary:
    """An adversary that forces any max-finding algorithm to make n-1 comparisons.

    Strategy: maintain a set of elements that could still be the maximum.
    Answer each comparison in the way that eliminates the FEWEST candidates.

    The key insight is that each comparison can eliminate at most 1 candidate
    from being the maximum (the loser). Starting with n candidates and needing
    to reduce to 1, we need at least n-1 comparisons.
    """

    def __init__(self, n):
        self.n = n
        # Track which elements have lost at least one comparison.
        # An element can only be confirmed "not the max" if it has lost.
        self.has_lost = [False] * n
        self.comparison_count = 0
        # We maintain a consistent assignment of values
        # that matches all answers given so far.
        # Start with all elements equal (value n).
        self.values = [n] * n
        self._next_lower = n - 1

    def compare(self, i, j):
        """Compare elements i and j. Returns True if values[i] < values[j].

        The adversary answers to maximize the number of comparisons needed.
        Strategy: if neither has lost, make one of them lose for the first time.
        If one has already lost, make that one lose again (no new information).
        """
        self.comparison_count += 1

        i_lost = self.has_lost[i]
        j_lost = self.has_lost[j]

        if not i_lost and not j_lost:
            # Neither has lost: we must make one lose for the first time.
            # This is the "expensive" case — we reveal 1 new bit.
            # Arbitrarily make i lose (i < j).
            self.has_lost[i] = True
            self.values[i] = self._next_lower
            self._next_lower -= 1
            return True  # i < j
        elif i_lost and not j_lost:
            # i already lost, make i lose again (no new info for the algorithm)
            return True  # i < j
        elif not i_lost and j_lost:
            # j already lost, make j lose again
            return False  # i > j (j < i)
        else:
            # Both have lost — answer consistently with current values
            return self.values[i] < self.values[j]

    def undefeated_count(self):
        """How many elements have never lost a comparison?"""
        return sum(1 for lost in self.has_lost if not lost)


def find_max_any_algorithm(adversary, n):
    """A generic max-finding algorithm facing an adversary.

    This simulates a reasonable (but not necessarily optimal) strategy:
    compare elements pairwise, tracking the current "champion."
    """
    champion = 0
    for i in range(1, n):
        if adversary.compare(champion, i):
            # champion < i, so i becomes new champion
            champion = i
    return champion


def demo_adversary():
    """Demonstrate the adversary argument for finding the maximum."""
    print("=" * 70)
    print("ADVERSARY ARGUMENT: FINDING THE MAXIMUM REQUIRES n-1 COMPARISONS")
    print("=" * 70)
    print()
    print("The adversary answers comparisons to force maximum work.")
    print("Key insight: each comparison eliminates at most 1 candidate.")
    print("We start with n candidates and need to reduce to 1.")
    print()

    for n in [5, 10, 20, 50]:
        adversary = MaxFindingAdversary(n)
        result = find_max_any_algorithm(adversary, n)
        undefeated = adversary.undefeated_count()

        print(f"n = {n:>3}: comparisons made = {adversary.comparison_count:>3}, "
              f"lower bound (n-1) = {n - 1:>3}, "
              f"undefeated elements = {undefeated}")

    print()
    print("The linear scan uses exactly n-1 comparisons, matching the lower bound.")
    print("This proves the simple algorithm IS optimal for finding the maximum.")
    print()

    # Demonstrate that fewer comparisons leave ambiguity
    print("What happens if we stop early?")
    n = 8
    adversary = MaxFindingAdversary(n)
    # Make only 5 comparisons (less than n-1 = 7)
    for i in range(5):
        adversary.compare(i, i + 1)

    print(f"After only 5 comparisons with n={n}:")
    print(f"  Undefeated elements: {adversary.undefeated_count()}")
    print(f"  Any of {adversary.undefeated_count()} elements could be the maximum!")
    print(f"  The algorithm CANNOT determine the max without more comparisons.")
    print()


# ---------------------------------------------------------------------------
# Section 5: Empirical Verification — No Comparison Sort Beats the Bound
# ---------------------------------------------------------------------------
# WHY: Theory is convincing, but seeing it hold against actual implementations
# makes the proof visceral. We instrument comparison sorts to count comparisons.

class CountingComparator:
    """Wraps a value to count the number of comparisons made.

    This lets us instrument ANY comparison-based sort to measure
    its actual comparison count without modifying the sort itself.
    """
    total_comparisons = 0

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        CountingComparator.total_comparisons += 1
        return self.value < other.value

    def __le__(self, other):
        CountingComparator.total_comparisons += 1
        return self.value <= other.value

    def __gt__(self, other):
        CountingComparator.total_comparisons += 1
        return self.value > other.value

    def __ge__(self, other):
        CountingComparator.total_comparisons += 1
        return self.value >= other.value

    def __eq__(self, other):
        CountingComparator.total_comparisons += 1
        return self.value == other.value

    @classmethod
    def reset(cls):
        cls.total_comparisons = 0


def insertion_sort(arr):
    """Insertion sort: O(n^2) worst case, O(n) best case."""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def merge_sort(arr):
    """Merge sort: O(n log n) always."""
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def demo_empirical():
    """Count actual comparisons vs the theoretical lower bound."""
    print("=" * 70)
    print("EMPIRICAL VERIFICATION: ACTUAL COMPARISONS vs LOWER BOUND")
    print("=" * 70)
    print()
    print("We instrument sorts to count comparisons and compare to ceil(log2(n!)).")
    print()

    print(f"{'n':>6} | {'Lower bound':>12} | {'Merge sort':>12} | {'Insert sort':>12} | {'Python sort':>12}")
    print("-" * 62)

    for n in [5, 10, 20, 50, 100, 500]:
        lower = math.ceil(exact_log2_factorial(n))

        # Merge sort
        data = [CountingComparator(x) for x in random.sample(range(n * 10), n)]
        CountingComparator.reset()
        merge_sort(data)
        merge_comps = CountingComparator.total_comparisons

        # Insertion sort
        data = [CountingComparator(x) for x in random.sample(range(n * 10), n)]
        CountingComparator.reset()
        insertion_sort(data)
        insert_comps = CountingComparator.total_comparisons

        # Python's built-in sort (Timsort)
        data = [CountingComparator(x) for x in random.sample(range(n * 10), n)]
        CountingComparator.reset()
        sorted(data)
        python_comps = CountingComparator.total_comparisons

        print(f"{n:>6} | {lower:>12} | {merge_comps:>12} | {insert_comps:>12} | {python_comps:>12}")

    print()
    print("OBSERVATIONS:")
    print("  1. No algorithm uses fewer comparisons than the lower bound")
    print("  2. Merge sort is close to optimal (within a small constant factor)")
    print("  3. Python's Timsort is highly optimized and sometimes beats merge sort")
    print("  4. Insertion sort is far above the bound for large n (it is O(n^2))")
    print()


# ---------------------------------------------------------------------------
# Section 6: The Escape Hatch — Non-Comparison Sorts
# ---------------------------------------------------------------------------
# WHY: Understanding what the model EXCLUDES is as important as what it proves.
# Non-comparison sorts bypass the bound by using different operations.

def counting_sort(arr, max_val):
    """Counting sort: O(n + k) where k is the range of values.

    This does NOT use comparisons between elements. Instead, it uses
    array indexing (which is O(1) random access) to place elements.
    This is why it can beat O(n log n) — it operates outside the
    comparison model.
    """
    count = [0] * (max_val + 1)
    for x in arr:
        count[x] += 1

    result = []
    for val in range(max_val + 1):
        result.extend([val] * count[val])
    return result


def demo_non_comparison():
    """Show that non-comparison sorts beat the bound."""
    print("=" * 70)
    print("ESCAPING THE BOUND: NON-COMPARISON SORTS")
    print("=" * 70)
    print()
    print("Counting sort uses ZERO comparisons between elements.")
    print("It exploits the structure of integer keys instead.")
    print()

    for n in [100, 1000, 10000]:
        lower_bound_comps = math.ceil(exact_log2_factorial(n))

        data = [random.randint(0, n * 2) for _ in range(n)]

        start = time.perf_counter()
        counting_sort(data, n * 2)
        elapsed = time.perf_counter() - start

        print(f"n = {n:>6}: lower bound for comparison sort = {lower_bound_comps:>10} comparisons")
        print(f"          counting sort: 0 comparisons, {elapsed:.6f} seconds")
        print()

    print("KEY TAKEAWAY: Lower bounds are about a MODEL, not about a problem.")
    print("Sorting CANNOT be done in O(n) with comparisons alone.")
    print("Sorting CAN be done in O(n) if you know the value range and use indexing.")
    print("The bound tells you: 'within this set of rules, this is the best possible.'")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    random.seed(42)  # Reproducible output

    demo_stirling()
    demo_decision_tree()
    demo_information_theory()
    demo_adversary()
    demo_empirical()
    demo_non_comparison()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print("Three techniques for proving lower bounds:")
    print("  1. DECISION TREE: model computation as a tree, count leaves")
    print("  2. INFORMATION THEORY: each query reveals limited bits")
    print("  3. ADVERSARY: construct worst-case inputs that force work")
    print()
    print("The comparison sorting lower bound Omega(n log n) follows from:")
    print("  - n! possible permutations (leaves needed)")
    print("  - Binary tree with n! leaves has height >= log2(n!)")
    print("  - log2(n!) = Theta(n log n) by Stirling's approximation")
    print()
    print("This bound is TIGHT: merge sort achieves O(n log n),")
    print("matching the lower bound up to constant factors.")
