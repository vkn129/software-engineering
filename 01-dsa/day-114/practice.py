"""
Day 114 Practice: 1D Dynamic Programming.

6 exercises on stairs, house robber, and Kadane variations.
Implement the TODO functions, then run: python practice.py
"""


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Climbing stairs with variable step sizes
# ===================================================================
# Steps allowed: any value in `steps` (e.g., [1, 2, 3]).
# Recurrence: ways(n) = sum(ways(n-s) for s in steps if n-s >= 0)
# Base: ways(0) = 1.

def climb_stairs_variable(n, steps):
    """Number of distinct ways to reach step n using any step size in `steps`."""
    # TODO: implement bottom-up
    pass


def _sol_climb_stairs_variable(n, steps):
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for s in steps:
            if i - s >= 0:
                dp[i] += dp[i - s]
    return dp[n]


# ===================================================================
# Exercise 2: House Robber (linear)
# ===================================================================
# Max sum picking non-adjacent elements.

def house_robber(values):
    """Max loot without robbing adjacent houses."""
    # TODO: implement O(1) space
    pass


def _sol_house_robber(values):
    if not values:
        return 0
    if len(values) == 1:
        return values[0]
    prev2 = values[0]
    prev1 = max(values[0], values[1])
    for i in range(2, len(values)):
        prev2, prev1 = prev1, max(prev1, prev2 + values[i])
    return prev1


# ===================================================================
# Exercise 3: House Robber II (circular)
# ===================================================================
# Houses arranged in a CIRCLE. House 0 and house n-1 are adjacent.
# Trick: answer = max(rob(values[0..n-2]), rob(values[1..n-1])).
# We exclude either the first or the last house, then run linear robber.

def house_robber_circular(values):
    """Max loot when houses form a circle."""
    # TODO: implement using the linear robber as a subroutine
    pass


def _sol_house_robber_circular(values):
    n = len(values)
    if n == 0:
        return 0
    if n == 1:
        return values[0]

    def linear(arr):
        if not arr:
            return 0
        if len(arr) == 1:
            return arr[0]
        a, b = arr[0], max(arr[0], arr[1])
        for i in range(2, len(arr)):
            a, b = b, max(b, a + arr[i])
        return b

    return max(linear(values[:-1]), linear(values[1:]))


# ===================================================================
# Exercise 4: Maximum subarray (Kadane)
# ===================================================================
# Largest sum of any contiguous subarray. Works for all-negative inputs too.

def max_subarray(a):
    """Largest contiguous subarray sum."""
    # TODO: implement Kadane in O(n) time, O(1) space
    pass


def _sol_max_subarray(a):
    if not a:
        return 0
    best_here = a[0]
    best = a[0]
    for x in a[1:]:
        best_here = max(x, best_here + x)
        best = max(best, best_here)
    return best


# ===================================================================
# Exercise 5: Maximum product subarray
# ===================================================================
# Like Kadane, but for product. Key trick: track both max and min, because
# multiplying by a negative number flips them.
# Recurrence:
#   max_here = max(a[i], max_here_prev * a[i], min_here_prev * a[i])
#   min_here = min(a[i], max_here_prev * a[i], min_here_prev * a[i])
# answer = max over all i of max_here.

def max_product_subarray(a):
    """Largest contiguous subarray PRODUCT."""
    # TODO: implement, tracking both max and min
    pass


def _sol_max_product_subarray(a):
    if not a:
        return 0
    max_here = min_here = best = a[0]
    for x in a[1:]:
        candidates = (x, max_here * x, min_here * x)
        max_here = max(candidates)
        min_here = min(candidates)
        best = max(best, max_here)
    return best


# ===================================================================
# Exercise 6: Best time to buy and sell stock (single transaction)
# ===================================================================
# Given prices[i] for day i, buy one day and sell on a LATER day.
# Return max profit (0 if no profitable trade).
# DP state: min price seen so far. Recurrence:
#   min_so_far = min(min_so_far, prices[i])
#   best_profit = max(best_profit, prices[i] - min_so_far)
# This is Kadane in disguise — applied to daily price *deltas*.

def max_profit_one_transaction(prices):
    """Max profit from one buy + one sell."""
    # TODO: implement O(n) time, O(1) space
    pass


def _sol_max_profit_one_transaction(prices):
    if not prices:
        return 0
    min_so_far = prices[0]
    best = 0
    for p in prices[1:]:
        best = max(best, p - min_so_far)
        min_so_far = min(min_so_far, p)
    return best


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

    print("Exercise 1: Climbing stairs (variable steps)")
    check("n=4, steps=[1,2]", try_or_sol("climb_stairs_variable", 4, [1, 2]), 5)
    check("n=4, steps=[1,2,3]", try_or_sol("climb_stairs_variable", 4, [1, 2, 3]), 7)
    check("n=0", try_or_sol("climb_stairs_variable", 0, [1, 2]), 1)

    print("\nExercise 2: House robber linear")
    check("[2,7,9,3,1]", try_or_sol("house_robber", [2, 7, 9, 3, 1]), 12)
    check("[2,1,1,2]", try_or_sol("house_robber", [2, 1, 1, 2]), 4)
    check("single", try_or_sol("house_robber", [5]), 5)
    check("empty", try_or_sol("house_robber", []), 0)

    print("\nExercise 3: House robber circular")
    check("[2,3,2]", try_or_sol("house_robber_circular", [2, 3, 2]), 3)
    check("[1,2,3,1]", try_or_sol("house_robber_circular", [1, 2, 3, 1]), 4)
    check("[1,2,3]", try_or_sol("house_robber_circular", [1, 2, 3]), 3)

    print("\nExercise 4: Max subarray (Kadane)")
    check("mixed", try_or_sol("max_subarray", [-2, 1, -3, 4, -1, 2, 1, -5, 4]), 6)
    check("all negative", try_or_sol("max_subarray", [-3, -2, -5, -1]), -1)
    check("all positive", try_or_sol("max_subarray", [1, 2, 3]), 6)

    print("\nExercise 5: Max product subarray")
    check("[2,3,-2,4]", try_or_sol("max_product_subarray", [2, 3, -2, 4]), 6)
    check("[-2,0,-1]", try_or_sol("max_product_subarray", [-2, 0, -1]), 0)
    check("[-2,3,-4]", try_or_sol("max_product_subarray", [-2, 3, -4]), 24)

    print("\nExercise 6: Buy and sell stock once")
    check("[7,1,5,3,6,4]", try_or_sol("max_profit_one_transaction", [7, 1, 5, 3, 6, 4]), 5)
    check("descending", try_or_sol("max_profit_one_transaction", [7, 6, 4, 3, 1]), 0)
    check("two days", try_or_sol("max_profit_one_transaction", [1, 5]), 4)

    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
