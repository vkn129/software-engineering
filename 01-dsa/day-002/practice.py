"""
Day 2 Practice: Deriving Complexity from Code
==============================================

These exercises train you to look at code and determine its time complexity.
This is NOT about memorizing rules — it is about understanding WHY.

The core reasoning: complexity = how many times does the most-executed
statement run, as a function of input size n?

Fill in the TODO sections. Run this file to check your answers.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Annotate Loop Complexity
# =============================================================================

def exercise_1_single_loop(n):
    """What is the time complexity of this function?

    The loop runs n times. Each iteration does O(1) work.
    Total: O(n).

    TODO: Return the complexity as a string.
    """
    total = 0
    for i in range(n):
        total += i
    # What is the time complexity?
    return "TODO"  # Replace with "O(1)", "O(n)", "O(n^2)", "O(log n)", etc.


def exercise_1_nested_loop(n):
    """What is the time complexity of this function?

    Outer loop runs n times. For EACH outer iteration, the inner loop
    also runs n times. The inner statement executes n * n = n^2 times.

    TODO: Return the complexity as a string.
    """
    total = 0
    for i in range(n):
        for j in range(n):
            total += i * j
    return "TODO"  # Replace with the correct complexity


def exercise_1_dependent_nested(n):
    """What is the time complexity of this function?

    Outer loop runs n times. Inner loop runs i times (depends on outer).
    Total inner iterations: 0 + 1 + 2 + ... + (n-1) = n(n-1)/2.

    The summation formula matters here: sum from i=0 to n-1 of i = n(n-1)/2.
    n(n-1)/2 is in Theta(n^2) because we drop the constant 1/2 and lower terms.

    TODO: Return the complexity as a string.
    """
    total = 0
    for i in range(n):
        for j in range(i):
            total += 1
    return "TODO"


def exercise_1_halving_loop(n):
    """What is the time complexity of this function?

    Each iteration, i doubles. How many times can you double 1 before
    exceeding n? That is: 2^k > n => k > log2(n). So the loop runs
    O(log n) times.

    Equivalently: how many times can you halve n before reaching 1?
    Same answer: log2(n).

    TODO: Return the complexity as a string.
    """
    i = 1
    while i < n:
        i *= 2
    return "TODO"


def exercise_1_linear_times_log(n):
    """What is the time complexity of this function?

    Outer loop: O(n) iterations.
    Inner loop: starts at i, halves each time => O(log i) <= O(log n).
    Total: O(n) outer * O(log n) inner = O(n log n).

    This is the same pattern that makes merge sort O(n log n):
    you do O(n) work at each of O(log n) levels.

    TODO: Return the complexity as a string.
    """
    total = 0
    for i in range(1, n + 1):
        j = i
        while j > 0:
            total += 1
            j //= 2
    return "TODO"


# =============================================================================
# Exercise 2: Recursion Tree Analysis
# =============================================================================

def exercise_2_linear_recursion_complexity():
    """Analyze this recursive function:

        def f(n):
            if n <= 0:
                return 0
            return 1 + f(n - 1)

    Recursion tree:
        f(n) -> f(n-1) -> f(n-2) -> ... -> f(0)

    Each call does O(1) work. There are n+1 calls.
    Recurrence: T(n) = T(n-1) + O(1)
    Unrolling:  T(n) = T(n-1) + c = T(n-2) + 2c = ... = T(0) + nc = O(n)

    TODO: Return the time complexity as a string.
    """
    return "TODO"


def exercise_2_binary_recursion_complexity():
    """Analyze this recursive function (naive Fibonacci):

        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)

    Recursion tree for fib(5):
                    fib(5)
                   /      \\
              fib(4)        fib(3)
             /     \\       /     \\
          fib(3)  fib(2)  fib(2)  fib(1)
          /   \\   /  \\    /  \\
       fib(2) fib(1) ...  ...

    Each node does O(1) work. How many nodes are there?
    At depth d, there are at most 2^d nodes.
    Max depth is n. Total nodes <= 2^0 + 2^1 + ... + 2^n = 2^(n+1) - 1.

    The exact bound is O(phi^n) where phi = (1+sqrt(5))/2 ≈ 1.618,
    because the two branches are not equal size. But O(2^n) is the
    standard answer for interview purposes.

    Recurrence: T(n) = T(n-1) + T(n-2) + O(1)

    TODO: Return the time complexity as a string.
    """
    return "TODO"


def exercise_2_divide_and_conquer_complexity():
    """Analyze merge sort:

        def merge_sort(arr):
            if len(arr) <= 1:
                return arr
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            return merge(left, right)   # merge is O(n)

    Recursion tree for n=8:
        Level 0: 1 problem of size 8         -> 8 work
        Level 1: 2 problems of size 4        -> 8 work
        Level 2: 4 problems of size 2        -> 8 work
        Level 3: 8 problems of size 1        -> 8 work (base case)

    Each level does O(n) total work. There are log2(n) levels.
    Total: O(n log n).

    Recurrence: T(n) = 2T(n/2) + O(n)

    TODO: Return the time complexity as a string.
    """
    return "TODO"


# =============================================================================
# Exercise 3: Derive T(n) from Recursive Code
# =============================================================================

def exercise_3_derive_recurrence_a():
    """Given this function:

        def mystery_a(n):
            if n <= 1:
                return 1
            return mystery_a(n // 2) + n

    Step 1 — Write the recurrence:
        T(n) = T(n/2) + O(n)

    Step 2 — Unroll:
        T(n) = T(n/2) + n
             = T(n/4) + n/2 + n
             = T(n/8) + n/4 + n/2 + n
             = ...
             = n + n/2 + n/4 + ... + 1   (geometric series)
             = n * (1 + 1/2 + 1/4 + ...) = n * 2 = O(n)

    The geometric series sum converges to 2n. This is a KEY insight:
    even though there are log(n) levels, the work DECREASES so fast
    that it is dominated by the first level.

    TODO: Return the time complexity as a string.
    """
    return "TODO"


def exercise_3_derive_recurrence_b():
    """Given this function:

        def mystery_b(n):
            if n <= 1:
                return 1
            return mystery_b(n // 2) + mystery_b(n // 2) + n

    Step 1 — Write the recurrence:
        T(n) = 2T(n/2) + O(n)

    Step 2 — This is merge sort's recurrence! Each level does O(n)
    total work across all subproblems, and there are O(log n) levels.

    TODO: Return the time complexity as a string.
    """
    return "TODO"


def exercise_3_derive_recurrence_c():
    """Given this function:

        def mystery_c(n):
            if n <= 1:
                return 1
            return mystery_c(n - 1) + mystery_c(n - 1)

    Step 1 — Write the recurrence:
        T(n) = 2T(n-1) + O(1)

    Step 2 — Unroll:
        T(n) = 2T(n-1) + 1
             = 2(2T(n-2) + 1) + 1 = 4T(n-2) + 3
             = 4(2T(n-3) + 1) + 3 = 8T(n-3) + 7
             = 2^k * T(n-k) + (2^k - 1)

    When k = n: T(n) = 2^n * T(0) + 2^n - 1 = O(2^n)

    DANGER: shrinking by 1 with 2 branches = exponential.
    Shrinking by half with 2 branches = O(n log n).
    The shrinkage rate makes all the difference.

    TODO: Return the time complexity as a string.
    """
    return "TODO"


# =============================================================================
# Exercise 4: Space Complexity of Recursion
# =============================================================================

def exercise_4_space_linear_recursion():
    """What is the SPACE complexity of this function?

        def f(n):
            if n <= 0:
                return 0
            return 1 + f(n - 1)

    Each call adds one frame to the call stack. Maximum depth is n.
    Each frame uses O(1) space. Total space: O(n).

    TODO: Return the space complexity as a string.
    """
    return "TODO"


def exercise_4_space_binary_recursion():
    """What is the SPACE complexity of naive Fibonacci?

        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)

    TRAP: You might think O(2^n) because there are O(2^n) total calls.
    But the call stack does not hold all calls simultaneously!

    The left branch fib(n-1) fully completes and its frames are popped
    BEFORE fib(n-2) starts. The maximum depth at any moment is n.

    Space = maximum stack depth = O(n), NOT O(2^n).

    This is a crucial distinction: time counts ALL operations,
    space counts the MAXIMUM simultaneous usage.

    TODO: Return the space complexity as a string.
    """
    return "TODO"


def exercise_4_space_merge_sort():
    """What is the SPACE complexity of merge sort?

        def merge_sort(arr):
            if len(arr) <= 1: return arr
            mid = len(arr) // 2
            left = merge_sort(arr[:mid])
            right = merge_sort(arr[mid:])
            return merge(left, right)

    Two sources of space:
    1. Call stack depth: O(log n) — the recursion halves each time.
    2. Merge creates a new array of size n at each level.

    The dominant term is O(n) for the merged arrays.
    (Some implementations are O(n log n) space if they are not careful.)

    TODO: Return the space complexity as a string.
    """
    return "TODO"


# =============================================================================
# Exercise 5: Implement and Analyze
# =============================================================================

def power_naive(base, exp):
    """Compute base^exp using naive recursion.

    Recurrence: T(n) = T(n-1) + O(1) => O(n)
    where n = exp.

    TODO: Implement this. Do NOT use ** or pow().
    """
    # Hint: base^0 = 1, base^n = base * base^(n-1)
    pass


def power_fast(base, exp):
    """Compute base^exp using fast exponentiation (repeated squaring).

    Key insight: base^n = (base^(n/2))^2        if n is even
                 base^n = base * (base^(n/2))^2  if n is odd

    Recurrence: T(n) = T(n/2) + O(1) => O(log n)

    This is the same idea behind modular exponentiation in cryptography.
    RSA computes base^exp mod m where exp can be 2048 bits long.
    Naive recursion would take 2^2048 steps (heat death of universe).
    Fast exponentiation takes 2048 steps.

    TODO: Implement this. Do NOT use ** or pow().
    """
    # Hint: if exp == 0 return 1
    #        if exp is even: half = power_fast(base, exp // 2); return half * half
    #        if exp is odd:  return base * power_fast(base, exp - 1)
    pass


def count_paths(m, n):
    """Count paths in an m x n grid from top-left to bottom-right.

    You can only move right or down.

    Recurrence: paths(m, n) = paths(m-1, n) + paths(m, n-1)
    Base cases: paths(1, n) = 1, paths(m, 1) = 1

    What is the time complexity of this naive recursive solution?
    The recursion tree branches into 2 at each step, and the depth
    is m + n - 2. So T(m,n) is exponential: O(2^(m+n)).

    TODO: Implement the naive recursive solution.
    (Day 29+ will show how memoization fixes this.)
    """
    pass


# =============================================================================
# Exercise 6: Complexity Comparison
# =============================================================================

def exercise_6_rank_complexities():
    """Rank these complexities from fastest to slowest growing:

    O(n^2), O(1), O(2^n), O(n log n), O(n), O(log n), O(n!)

    TODO: Return a list of strings in order from fastest to slowest.
    Example: ["O(1)", "O(log n)", ...]
    """
    return []  # TODO: fill in the correct order


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    passed = 0
    failed = 0
    total = 0

    def check(name, got, expected):
        nonlocal passed, failed, total
        total += 1
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"        Expected: {expected}")
            print(f"        Got:      {got}")
            failed += 1

    print("=" * 65)
    print("Day 2 Practice: Complexity Analysis")
    print("=" * 65)

    # Exercise 1: Loop Complexity
    print("\n--- Exercise 1: Loop Complexity ---")
    check("single_loop", exercise_1_single_loop(100), "O(n)")
    check("nested_loop", exercise_1_nested_loop(100), "O(n^2)")
    check("dependent_nested", exercise_1_dependent_nested(100), "O(n^2)")
    check("halving_loop", exercise_1_halving_loop(100), "O(log n)")
    check("linear_times_log", exercise_1_linear_times_log(100), "O(n log n)")

    # Exercise 2: Recursion Tree
    print("\n--- Exercise 2: Recursion Tree Analysis ---")
    check("linear_recursion", exercise_2_linear_recursion_complexity(), "O(n)")
    check("binary_recursion (fib)", exercise_2_binary_recursion_complexity(), "O(2^n)")
    check("divide_and_conquer (merge sort)", exercise_2_divide_and_conquer_complexity(), "O(n log n)")

    # Exercise 3: Derive T(n)
    print("\n--- Exercise 3: Derive Recurrence ---")
    check("T(n) = T(n/2) + O(n)", exercise_3_derive_recurrence_a(), "O(n)")
    check("T(n) = 2T(n/2) + O(n)", exercise_3_derive_recurrence_b(), "O(n log n)")
    check("T(n) = 2T(n-1) + O(1)", exercise_3_derive_recurrence_c(), "O(2^n)")

    # Exercise 4: Space Complexity
    print("\n--- Exercise 4: Space Complexity ---")
    check("linear recursion space", exercise_4_space_linear_recursion(), "O(n)")
    check("binary recursion space (fib)", exercise_4_space_binary_recursion(), "O(n)")
    check("merge sort space", exercise_4_space_merge_sort(), "O(n)")

    # Exercise 5: Implement and Analyze
    print("\n--- Exercise 5: Implement Functions ---")
    if power_naive is not None and power_naive(2, 10) is not None:
        check("power_naive(2, 10)", power_naive(2, 10), 1024)
        check("power_naive(3, 0)", power_naive(3, 0), 1)
        check("power_naive(5, 3)", power_naive(5, 3), 125)
    else:
        print("  SKIP: power_naive not implemented yet")
        failed += 3
        total += 3

    if power_fast is not None and power_fast(2, 10) is not None:
        check("power_fast(2, 10)", power_fast(2, 10), 1024)
        check("power_fast(2, 20)", power_fast(2, 20), 1048576)
        check("power_fast(3, 0)", power_fast(3, 0), 1)
        check("power_fast(5, 3)", power_fast(5, 3), 125)
    else:
        print("  SKIP: power_fast not implemented yet")
        failed += 4
        total += 4

    if count_paths is not None and count_paths(2, 2) is not None:
        check("count_paths(1, 1)", count_paths(1, 1), 1)
        check("count_paths(2, 2)", count_paths(2, 2), 2)
        check("count_paths(3, 3)", count_paths(3, 3), 6)
        check("count_paths(3, 7)", count_paths(3, 7), 28)
    else:
        print("  SKIP: count_paths not implemented yet")
        failed += 4
        total += 4

    # Exercise 6: Rank Complexities
    print("\n--- Exercise 6: Rank Complexities ---")
    expected_order = ["O(1)", "O(log n)", "O(n)", "O(n log n)", "O(n^2)", "O(2^n)", "O(n!)"]
    check("complexity ranking", exercise_6_rank_complexities(), expected_order)

    # Summary
    print(f"\n{'=' * 65}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0 and total > 0:
        print("All exercises complete! You understand complexity analysis.")
    elif passed == 0:
        print("No tests passed yet. Replace the TODO values!")
    else:
        print(f"Keep going -- {failed} more to solve.")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
