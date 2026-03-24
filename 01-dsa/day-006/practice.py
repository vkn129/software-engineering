"""
Day 6 Practice: Prove Lower Bounds for Fundamental Problems

For each exercise:
1. Read the problem description
2. Fill in the TODO with your proof/implementation
3. Run the file — test cases verify your reasoning computationally

The goal is to think like a theorist: before asking "how fast CAN I solve this?"
ask "how fast MUST any algorithm be?"

Run: python practice.py
"""

import math


# ---------------------------------------------------------------------------
# Exercise 1: Lower Bound for Search in a Sorted Array
# ---------------------------------------------------------------------------
# PROBLEM: Prove that searching for an element in a sorted array of n elements
# requires at least ceil(log2(n+1)) comparisons in the worst case.
#
# HINT: There are n+1 possible outcomes: the element is at position 0, 1, ..., n-1,
# or the element is not present. Each comparison is a yes/no question.

def search_lower_bound(n):
    """Return the minimum number of comparisons needed to search a sorted array of n elements.

    TODO: Implement this using the information-theoretic argument.
    Think: how many distinct outcomes are there? How many bits do you need?
    """
    # TODO: Replace with your implementation
    pass


# Verification: binary search achieves this bound
def binary_search_with_count(arr, target):
    """Binary search that counts comparisons."""
    lo, hi = 0, len(arr) - 1
    comparisons = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        comparisons += 1
        if arr[mid] == target:
            return mid, comparisons
        comparisons += 1  # The direction comparison
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons


def test_search_lower_bound():
    """Verify search lower bounds."""
    print("Exercise 1: Search Lower Bound")
    print("-" * 40)

    test_cases = [
        (1, 1),    # 1 element: need 1 comparison (is it here or not?)
        (2, 2),    # 2 elements: need 2 comparisons
        (3, 2),    # 3 elements: ceil(log2(4)) = 2
        (7, 3),    # 7 elements: ceil(log2(8)) = 3
        (8, 4),    # 8 elements: ceil(log2(9)) = 4
        (15, 4),   # 15 elements: ceil(log2(16)) = 4
        (100, 7),  # 100 elements: ceil(log2(101)) = 7
        (1000, 10), # 1000 elements: ceil(log2(1001)) = 10
    ]

    all_pass = True
    for n, expected in test_cases:
        result = search_lower_bound(n)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_pass = False
        print(f"  n={n:>5}: your answer={result}, expected={expected} [{status}]")

    print(f"  Result: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print()


# ---------------------------------------------------------------------------
# Exercise 2: Lower Bound for Merging Two Sorted Lists
# ---------------------------------------------------------------------------
# PROBLEM: You have two sorted lists of size m and n. Prove that merging them
# into one sorted list requires at least m + n - 1 comparisons in the worst case.
#
# HINT: Use an adversary argument. Consider interleaving: a1 < b1 < a2 < b2 < ...
# In this worst case, every consecutive pair must be compared.

def merge_lower_bound(m, n):
    """Return the minimum number of comparisons needed to merge two sorted lists
    of sizes m and n.

    TODO: Implement this. The answer is a simple formula.
    Think: what is the worst-case interleaving pattern?
    """
    # TODO: Replace with your implementation
    pass


def merge_with_count(a, b):
    """Merge two sorted lists, counting comparisons."""
    result = []
    i = j = 0
    comparisons = 0
    while i < len(a) and j < len(b):
        comparisons += 1
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result, comparisons


def test_merge_lower_bound():
    """Verify merge lower bounds."""
    print("Exercise 2: Merge Lower Bound")
    print("-" * 40)

    test_cases = [
        (1, 1, 1),   # Merging [a] and [b]: need 1 comparison
        (2, 2, 3),   # Merging [a1,a2] and [b1,b2]: worst case needs 3
        (3, 3, 5),   # m + n - 1 = 5
        (5, 5, 9),
        (10, 10, 19),
        (1, 10, 10), # Merging 1 element into 10: might need to compare against all 10? No: just binary search. But with sequential merge: m + n - 1 = 10
    ]

    all_pass = True
    for m, n, expected in test_cases:
        result = merge_lower_bound(m, n)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_pass = False
        print(f"  m={m}, n={n}: your answer={result}, expected={expected} [{status}]")

    # Verify with worst-case inputs
    print("\n  Verification: worst-case merge uses exactly m+n-1 comparisons")
    a = [1, 3, 5, 7, 9]   # Perfect interleaving forces max comparisons
    b = [2, 4, 6, 8, 10]
    _, comps = merge_with_count(a, b)
    print(f"  Interleaved [1,3,5,7,9] + [2,4,6,8,10]: {comps} comparisons (bound: {len(a)+len(b)-1})")

    print(f"  Result: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print()


# ---------------------------------------------------------------------------
# Exercise 3: Lower Bound for Finding the Maximum
# ---------------------------------------------------------------------------
# PROBLEM: Prove that finding the maximum of n elements requires at least
# n - 1 comparisons. Use the adversary / tournament argument.
#
# HINT: Think of it as a tournament. Every element except the winner must
# lose at least one "match." Each comparison produces at most one new loser.

def max_lower_bound(n):
    """Return the minimum number of comparisons needed to find the maximum of n elements.

    TODO: Implement this using the tournament argument.
    """
    # TODO: Replace with your implementation
    pass


def find_max_with_count(arr):
    """Find maximum, counting comparisons."""
    if len(arr) == 0:
        return None, 0
    current_max = arr[0]
    comparisons = 0
    for i in range(1, len(arr)):
        comparisons += 1
        if arr[i] > current_max:
            current_max = arr[i]
    return current_max, comparisons


def test_max_lower_bound():
    """Verify max-finding lower bounds."""
    print("Exercise 3: Maximum Lower Bound")
    print("-" * 40)

    test_cases = [
        (1, 0),    # 1 element: it IS the max, 0 comparisons needed
        (2, 1),    # 2 elements: 1 comparison
        (3, 2),    # 3 elements: 2 comparisons
        (10, 9),   # n-1
        (100, 99),
        (1000, 999),
    ]

    all_pass = True
    for n, expected in test_cases:
        result = max_lower_bound(n)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_pass = False
        print(f"  n={n:>5}: your answer={result}, expected={expected} [{status}]")

    # Verify that the simple algorithm achieves this
    import random
    random.seed(42)
    arr = random.sample(range(10000), 100)
    _, comps = find_max_with_count(arr)
    print(f"\n  Verification: linear scan of 100 elements uses {comps} comparisons")
    print(f"  Lower bound: {max_lower_bound(100)}")
    print(f"  Algorithm is optimal: {comps == max_lower_bound(100)}")

    print(f"  Result: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print()


# ---------------------------------------------------------------------------
# Exercise 4: Lower Bound for Finding Both Min and Max
# ---------------------------------------------------------------------------
# PROBLEM: Finding the max alone requires n-1 comparisons. Finding the min
# alone requires n-1 comparisons. But finding BOTH simultaneously can be done
# in fewer than 2(n-1) comparisons! What is the tight lower bound?
#
# HINT: Process elements in PAIRS. Each pair comparison gives you a candidate
# for min AND max. Then find the min among min-candidates and max among
# max-candidates. Count: ceil(n/2) pair comparisons + ceil(n/2)-1 for min
# + ceil(n/2)-1 for max.
#
# The lower bound is ceil(3n/2) - 2 comparisons.

def minmax_lower_bound(n):
    """Return the minimum number of comparisons to find both min and max of n elements.

    TODO: Implement the formula ceil(3n/2) - 2.
    This bound is tight: the pair-comparison algorithm achieves it.
    """
    # TODO: Replace with your implementation
    pass


def find_minmax_optimal(arr):
    """Find min and max using the optimal ceil(3n/2) - 2 comparisons.

    Strategy: compare pairs, send smaller to min-candidates, larger to max-candidates.
    Then find min of min-candidates and max of max-candidates.
    """
    n = len(arr)
    if n == 0:
        return None, None, 0
    if n == 1:
        return arr[0], arr[0], 0

    comparisons = 0

    # Initialize: compare first pair
    comparisons += 1
    if arr[0] < arr[1]:
        current_min, current_max = arr[0], arr[1]
    else:
        current_min, current_max = arr[1], arr[0]

    # Process remaining elements in pairs
    i = 2
    while i + 1 < n:
        comparisons += 1  # Compare the pair
        if arr[i] < arr[i + 1]:
            small, large = arr[i], arr[i + 1]
        else:
            small, large = arr[i + 1], arr[i]

        comparisons += 1  # Compare small with current_min
        if small < current_min:
            current_min = small

        comparisons += 1  # Compare large with current_max
        if large > current_max:
            current_max = large

        i += 2

    # Handle odd element
    if i < n:
        comparisons += 1
        if arr[i] < current_min:
            current_min = arr[i]
        comparisons += 1
        if arr[i] > current_max:
            current_max = arr[i]

    return current_min, current_max, comparisons


def test_minmax_lower_bound():
    """Verify min-max lower bounds."""
    print("Exercise 4: Simultaneous Min-Max Lower Bound")
    print("-" * 40)

    test_cases = [
        (2, 1),    # 1 comparison to find both
        (3, 3),    # ceil(3*3/2) - 2 = 3
        (4, 4),    # ceil(3*4/2) - 2 = 4
        (5, 6),    # ceil(3*5/2) - 2 = 6
        (10, 13),  # ceil(3*10/2) - 2 = 13
        (100, 148), # ceil(3*100/2) - 2 = 148
    ]

    all_pass = True
    for n, expected in test_cases:
        result = minmax_lower_bound(n)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_pass = False
        print(f"  n={n:>5}: your answer={result}, expected={expected} [{status}]")

    # Compare naive (2n-3) vs optimal
    print(f"\n  For n=100: naive needs 2*99 = 197 comparisons")
    print(f"  Optimal needs {minmax_lower_bound(100) if minmax_lower_bound(100) else '?'} comparisons")
    print(f"  Savings: {197 - (minmax_lower_bound(100) or 0)} fewer comparisons ({(197 - (minmax_lower_bound(100) or 0)) / 197 * 100:.1f}% reduction)")

    # Verify optimal algorithm
    import random
    random.seed(42)
    arr = list(range(20))
    random.shuffle(arr)
    mn, mx, comps = find_minmax_optimal(arr)
    expected_comps = math.ceil(3 * 20 / 2) - 2
    print(f"\n  Verification on 20 elements: min={mn}, max={mx}, comparisons={comps}")
    print(f"  Lower bound: {expected_comps}, algorithm used: {comps}")

    print(f"  Result: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print()


# ---------------------------------------------------------------------------
# Exercise 5: Decision Tree Height Calculator
# ---------------------------------------------------------------------------
# PROBLEM: Given n (number of elements to sort), compute the minimum height
# of ANY comparison-based sorting decision tree.
#
# This is the core of the sorting lower bound: height >= ceil(log2(n!))

def sorting_decision_tree_min_height(n):
    """Return the minimum height of a comparison-based sorting decision tree for n elements.

    TODO: Implement this. Remember:
    - The tree must have at least n! leaves (one per permutation)
    - A binary tree of height h has at most 2^h leaves
    - Therefore h >= ceil(log2(n!))
    """
    # TODO: Replace with your implementation
    pass


def test_sorting_tree_height():
    """Verify decision tree height calculations."""
    print("Exercise 5: Sorting Decision Tree Minimum Height")
    print("-" * 40)

    test_cases = [
        (1, 0),    # 1 element: already sorted, 0 comparisons
        (2, 1),    # 2 elements: 1 comparison
        (3, 3),    # ceil(log2(6)) = 3
        (4, 5),    # ceil(log2(24)) = 5
        (5, 7),    # ceil(log2(120)) = 7
        (6, 10),   # ceil(log2(720)) = 10
        (7, 13),   # ceil(log2(5040)) = 13
        (10, 22),  # ceil(log2(3628800)) = 22
        (12, 29),  # ceil(log2(479001600)) = 29
    ]

    all_pass = True
    for n, expected in test_cases:
        result = sorting_decision_tree_min_height(n)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_pass = False
        print(f"  n={n:>3}: your answer={result}, expected={expected} [{status}]")

    print(f"\n  For n=10: at least {sorting_decision_tree_min_height(10) or '?'} comparisons to sort")
    print(f"  This is the ABSOLUTE MINIMUM — no comparison sort can use fewer")

    print(f"  Result: {'ALL PASSED' if all_pass else 'SOME FAILED'}")
    print()


# ---------------------------------------------------------------------------
# Solutions (scroll down only after attempting!)
# ---------------------------------------------------------------------------
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# SOLUTIONS BELOW — TRY THE EXERCISES FIRST!
#
#
#
#
#
#
#
#
#
#

def search_lower_bound_solution(n):
    """n+1 outcomes (n positions + not found), each comparison gives 1 bit."""
    if n <= 0:
        return 0
    return math.ceil(math.log2(n + 1))

def merge_lower_bound_solution(m, n):
    """In worst case (perfect interleaving), every consecutive pair in the
    merged output comes from different lists, requiring a comparison."""
    return m + n - 1

def max_lower_bound_solution(n):
    """Tournament argument: n-1 elements must each lose at least once.
    Each comparison creates at most 1 new loser."""
    if n <= 1:
        return 0
    return n - 1

def minmax_lower_bound_solution(n):
    """Process in pairs: ceil(n/2) pair comparisons, then find min of
    ceil(n/2) candidates and max of ceil(n/2) candidates."""
    if n <= 1:
        return 0
    return math.ceil(3 * n / 2) - 2

def sorting_decision_tree_min_height_solution(n):
    """Binary tree with n! leaves has height >= ceil(log2(n!))."""
    if n <= 1:
        return 0
    return math.ceil(math.log2(math.factorial(n)))


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("DAY 6 PRACTICE: Lower Bound Proofs")
    print("=" * 60)
    print()
    print("Fill in each TODO function, then run this file to verify.")
    print("The test cases check your formulas against known results.")
    print()

    test_search_lower_bound()
    test_merge_lower_bound()
    test_max_lower_bound()
    test_minmax_lower_bound()
    test_sorting_tree_height()

    print("=" * 60)
    print("To check solutions, look at the *_solution functions at the")
    print("bottom of this file. But try to derive them yourself first!")
    print("=" * 60)
