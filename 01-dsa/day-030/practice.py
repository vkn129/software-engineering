"""
Day 30: Monotonic Stack — Practice Exercises

5 exercises with TODO stubs followed by solutions.
All use monotonic stack patterns. No external libraries.
"""


# ---------------------------------------------------------------------------
# Exercise 1: Trapping Rain Water (Stack Approach)
# ---------------------------------------------------------------------------
# Given elevation map as a list of non-negative integers, compute how much
# water it can trap after raining.
#
# Why stack approach? Each time we find a bar taller than the top of stack,
# we know there's a "basin" between the current bar and the bar below the
# popped element. We compute water layer by layer (horizontally), unlike
# the two-pointer approach which works column by column (vertically).
# ---------------------------------------------------------------------------

def trap_rain_water(height):
    """Return total units of trapped rain water."""
    # TODO: implement using a monotonic stack
    pass


def _sol_trap_rain_water(height):
    """
    Stack-based approach: maintain a decreasing stack of indices.
    When height[i] > height[stack[-1]], we found the right wall of a basin.
    Pop the bottom of the basin, then compute the water trapped in that
    horizontal layer between the new stack top (left wall) and i (right wall).

    Why horizontal layers? Because that's what naturally falls out of the
    stack approach — each pop reveals one layer of water sitting on top of
    the popped bar, bounded by the walls on each side.
    """
    stack = []
    water = 0

    for i in range(len(height)):
        while stack and height[i] > height[stack[-1]]:
            bottom = stack.pop()
            if not stack:
                # No left wall — water spills out
                break
            left = stack[-1]
            # Width between left wall and right wall (exclusive)
            w = i - left - 1
            # Height is limited by the shorter wall, minus the bottom
            h = min(height[left], height[i]) - height[bottom]
            water += w * h
        stack.append(i)

    return water


# ---------------------------------------------------------------------------
# Exercise 2: Remove K Digits
# ---------------------------------------------------------------------------
# Given a non-negative integer as a string and integer k, remove k digits
# to make the number as small as possible. Return the result as a string.
#
# Why monotonic stack? To minimize the number, we want the leftmost digits
# to be as small as possible. Whenever a digit is smaller than the previous
# one, we should remove the previous (larger) one. This is exactly what
# a monotonic increasing stack does.
# ---------------------------------------------------------------------------

def remove_k_digits(num, k):
    """Return smallest number after removing k digits."""
    # TODO: implement using a monotonic stack
    pass


def _sol_remove_k_digits(num, k):
    """
    Maintain an increasing stack of digits. When the current digit is smaller
    than the top, pop the top (counts as a removal). After the pass, if we
    still need more removals, trim from the end (the remaining digits are
    in increasing order, so removing from the end removes the largest).

    Why increasing? Because a number like "1432" → removing '4' gives "132",
    which is smaller than removing any other single digit. The first place
    where a digit is followed by something smaller is the optimal removal point.
    """
    stack = []
    removals = 0

    for digit in num:
        while stack and removals < k and digit < stack[-1]:
            stack.pop()
            removals += 1
        stack.append(digit)

    # If we haven't removed enough, trim from the right
    # (remaining digits are non-decreasing, so rightmost are largest)
    while removals < k:
        stack.pop()
        removals += 1

    # Build result, stripping leading zeros
    result = "".join(stack).lstrip("0")
    return result if result else "0"


# ---------------------------------------------------------------------------
# Exercise 3: Sum of Subarray Minimums
# ---------------------------------------------------------------------------
# Given an array, return the sum of min(subarray) for all contiguous subarrays.
# Return result modulo 10^9 + 7.
#
# Why monotonic stack? For each element arr[i], we need to count how many
# subarrays have arr[i] as their minimum. This requires knowing how far
# left and right arr[i] can extend while remaining the minimum — exactly
# the "previous smaller" and "next smaller" element boundaries.
# ---------------------------------------------------------------------------

def sum_subarray_minimums(arr):
    """Return sum of minimums of all subarrays, mod 10^9+7."""
    # TODO: implement using monotonic stack
    pass


def _sol_sum_subarray_minimums(arr):
    """
    For each element arr[i]:
    - left[i] = number of subarrays ending at i where arr[i] is the minimum
      (distance to previous smaller element)
    - right[i] = number of subarrays starting at i where arr[i] is the minimum
      (distance to next smaller-or-equal element)

    arr[i]'s contribution = arr[i] * left[i] * right[i]

    Why "smaller" on left but "smaller-or-equal" on right?
    To avoid double-counting subarrays when duplicate values exist.
    If both boundaries used strict <, a subarray with equal endpoints
    would be counted by both endpoints.
    """
    MOD = 10**9 + 7
    n = len(arr)
    left = [0] * n   # distance to previous strictly smaller
    right = [0] * n  # distance to next smaller-or-equal

    # Previous smaller element (strictly less)
    stack = []
    for i in range(n):
        while stack and arr[stack[-1]] >= arr[i]:
            stack.pop()
        left[i] = i - stack[-1] if stack else i + 1
        stack.append(i)

    # Next smaller-or-equal element
    stack = []
    for i in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] > arr[i]:
            stack.pop()
        right[i] = stack[-1] - i if stack else n - i
        stack.append(i)

    total = 0
    for i in range(n):
        total = (total + arr[i] * left[i] * right[i]) % MOD

    return total


# ---------------------------------------------------------------------------
# Exercise 4: Maximum Width Ramp
# ---------------------------------------------------------------------------
# A ramp is a pair (i, j) with i < j and arr[i] <= arr[j].
# Find the maximum width j - i of any ramp. Return 0 if none exists.
#
# Why monotonic stack? Build a decreasing stack of candidates for the left
# endpoint (i). Then scan from the right: for each j, pop stack entries where
# arr[stack[-1]] <= arr[j] — each pop gives a valid ramp, and since j is
# decreasing, we want to pop eagerly (later j values will be smaller width).
# ---------------------------------------------------------------------------

def max_width_ramp(arr):
    """Return maximum j - i such that arr[i] <= arr[j], or 0."""
    # TODO: implement using monotonic stack
    pass


def _sol_max_width_ramp(arr):
    """
    Step 1: Build a strictly decreasing stack of indices (left-to-right).
    Only indices that are smaller than all previous values can ever be the
    optimal left endpoint of a ramp. If arr[i] >= arr[j] for some j < i,
    then j is always a better or equal left endpoint than i.

    Step 2: Scan from right to left. For each j, pop stack entries where
    arr[stack[-1]] <= arr[j]. Each popped entry gives a valid ramp.
    We go right-to-left because we want the widest ramp — larger j values
    give wider ramps for the same i.

    Why can we pop? Once an index i is paired with j, no later j' < j can
    give a wider ramp with i (since j' - i < j - i). So i is "consumed."
    """
    n = len(arr)
    stack = []

    # Build decreasing stack of left-endpoint candidates
    for i in range(n):
        if not stack or arr[i] < arr[stack[-1]]:
            stack.append(i)

    max_width = 0

    # Scan from right, greedily matching with leftmost valid endpoint
    for j in range(n - 1, -1, -1):
        while stack and arr[stack[-1]] <= arr[j]:
            max_width = max(max_width, j - stack.pop())

    return max_width


# ---------------------------------------------------------------------------
# Exercise 5: 132 Pattern
# ---------------------------------------------------------------------------
# Given an array, return True if there exists i < j < k such that
# arr[i] < arr[k] < arr[j] (a "132 pattern" where arr[i]=1, arr[j]=3, arr[k]=2).
#
# Why monotonic stack? Traverse from right to left, maintaining a decreasing
# stack. When we pop elements (because current value is larger), the popped
# value becomes the best candidate for the "2" (arr[k]). If we ever see a
# value less than this candidate, we've found arr[i] < arr[k] < arr[j].
# ---------------------------------------------------------------------------

def find_132_pattern(nums):
    """Return True if a 132 pattern exists."""
    # TODO: implement using monotonic stack
    pass


def _sol_find_132_pattern(nums):
    """
    Traverse right-to-left. Maintain a decreasing stack representing
    candidates for the "3" (arr[j]). When nums[i] > stack top, we pop —
    the popped value is a candidate for "2" (arr[k]). Track the maximum
    popped value as 'second' (best arr[k] so far).

    If we ever encounter nums[i] < second, then:
    - second = arr[k] was popped because some arr[j] > arr[k] existed to its left
    - nums[i] < second means nums[i] < arr[k] < arr[j] — found the pattern!

    Why right-to-left? We need j < k in position, but arr[j] > arr[k] in value.
    Going right-to-left lets us build up the "3,2" pair first, then look for "1".
    """
    stack = []
    second = float("-inf")  # best candidate for the "2" in 132

    for i in range(len(nums) - 1, -1, -1):
        # If current value is less than our best "2", we found "1"
        if nums[i] < second:
            return True
        # Current value is a "3" candidate; pop smaller values as "2" candidates
        while stack and nums[i] > stack[-1]:
            second = stack.pop()
        stack.append(nums[i])

    return False


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

def run_tests():
    # Map stub functions to their solutions for testing
    exercises = [
        ("Trapping Rain Water", trap_rain_water, _sol_trap_rain_water),
        ("Remove K Digits", remove_k_digits, _sol_remove_k_digits),
        ("Sum of Subarray Minimums", sum_subarray_minimums, _sol_sum_subarray_minimums),
        ("Maximum Width Ramp", max_width_ramp, _sol_max_width_ramp),
        ("132 Pattern", find_132_pattern, _sol_find_132_pattern),
    ]

    # --- Exercise 1: Trapping Rain Water ---
    test_cases_1 = [
        ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], 6),
        ([4, 2, 0, 3, 2, 5], 9),
        ([1, 2, 3, 4], 0),
        ([], 0),
        ([3, 0, 3], 3),
    ]

    # --- Exercise 2: Remove K Digits ---
    test_cases_2 = [
        (("1432219", 3), "1219"),
        (("10200", 1), "200"),
        (("10", 2), "0"),
        (("9", 1), "0"),
        (("112", 1), "11"),
    ]

    # --- Exercise 3: Sum of Subarray Minimums ---
    test_cases_3 = [
        ([3, 1, 2, 4], 17),      # subarrays: [3]=3,[1]=1,[2]=2,[4]=4,[3,1]=1,[1,2]=1,[2,4]=2,[3,1,2]=1,[1,2,4]=1,[3,1,2,4]=1 => 17
        ([11, 81, 94, 43, 3], 444),
        ([1], 1),
    ]

    # --- Exercise 4: Maximum Width Ramp ---
    test_cases_4 = [
        ([6, 0, 8, 2, 1, 5], 4),  # i=1(0) j=5(5) => width 4
        ([9, 8, 1, 0, 1, 9, 4, 0, 4, 1], 7),  # i=2, j=9... actually i=2(1), j=9(1) => 7
        ([5, 4, 3, 2, 1], 0),     # strictly decreasing, no ramp
        ([1, 2], 1),
    ]

    # --- Exercise 5: 132 Pattern ---
    test_cases_5 = [
        ([1, 2, 3, 4], False),
        ([3, 1, 4, 2], True),     # 1 < 2 < 4 at indices 1,2,3
        ([-1, 3, 2, 0], True),    # -1 < 2 < 3
        ([1, 0, 1, -4, -3], False),
        ([3, 5, 0, 3, 4], True),  # 0 < 3 < 5
    ]

    all_test_cases = [test_cases_1, test_cases_2, test_cases_3, test_cases_4, test_cases_5]

    for (name, stub_fn, sol_fn), test_cases in zip(exercises, all_test_cases):
        print(f"\n--- {name} ---")

        # Decide which function to test: use stub if implemented, else solution
        fn = stub_fn
        using_solution = False
        # Quick check: if stub returns None on a simple call, use solution
        try:
            if name == "Remove K Digits":
                test_result = stub_fn(*test_cases[0][0])
            else:
                test_result = stub_fn(test_cases[0][0])
            if test_result is None:
                fn = sol_fn
                using_solution = True
        except Exception:
            fn = sol_fn
            using_solution = True

        if using_solution:
            print(f"  (using reference solution — implement the TODO!)")

        passed = 0
        total = len(test_cases)

        for i, tc in enumerate(test_cases):
            if name == "Remove K Digits":
                args, expected = tc
                result = fn(*args)
            else:
                inp, expected = tc
                result = fn(inp)

            status = "PASS" if result == expected else "FAIL"
            if status == "PASS":
                passed += 1
            else:
                print(f"  Test {i+1}: {status} — got {result}, expected {expected}")

        print(f"  {passed}/{total} tests passed")

    print()


if __name__ == "__main__":
    run_tests()
