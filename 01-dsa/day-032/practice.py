"""
Day 32 Practice: Deque Exercises
=================================

5 exercises progressing from basic deque usage to advanced sliding window patterns.
Each exercise has a TODO stub and a _sol_ solution. Try solving before peeking.

Run: python practice.py
"""

import collections


# ===========================================================================
# Exercise 1: Palindrome Checker Using Deque
# ===========================================================================
# Why deque for palindromes? The natural check is "compare first and last,
# then second and second-to-last, etc." A deque lets you pop from both ends
# in O(1), making this comparison loop clean and O(n) total.
#
# You could also use string slicing (s == s[::-1]), which is faster in Python
# because it runs in C. But the deque approach generalizes to streams where
# you don't have the full string upfront.

def palindrome_check(s):
    """Return True if s is a palindrome (ignoring case and non-alphanumeric chars).

    Approach: push cleaned characters into a deque, then pop from both ends
    and compare. If every pair matches, it is a palindrome.

    Args:
        s: input string
    Returns:
        True if palindrome, False otherwise
    """
    # TODO: implement
    pass


def _sol_palindrome_check(s):
    """Solution: push all cleaned chars onto deque, pop both ends and compare."""
    # Clean the string: lowercase, only alphanumeric characters.
    # Why clean first? "A man, a plan..." has spaces and punctuation that
    # are not part of the palindrome structure.
    cleaned = [c.lower() for c in s if c.isalnum()]
    dq = collections.deque(cleaned)

    # Pop from both ends. If the deque has odd length, the middle character
    # is left alone -- it trivially matches itself.
    while len(dq) > 1:
        front = dq.popleft()
        back = dq.pop()
        if front != back:
            return False
    return True


# ===========================================================================
# Exercise 2: Maximum of All Subarrays of Size K
# ===========================================================================
# This is the classic sliding window maximum. It appears in LeetCode 239,
# in monitoring dashboards ("max latency in last 60s"), and in financial
# systems ("highest price in last K ticks").
#
# Naive: O(n*k) -- recompute max for every window position.
# Deque: O(n) -- maintain a monotonic decreasing deque of indices.
#
# The key insight: if arr[j] >= arr[i] and j > i, then i can NEVER be the
# answer for any future window. j is both larger and will expire later.

def max_of_subarrays(arr, k):
    """Return a list of maximums for every contiguous subarray of size k.

    Example: arr=[1,3,-1,-3,5,3,6,7], k=3 -> [3,3,5,5,6,7]

    Args:
        arr: list of numbers
        k: window size (positive integer)
    Returns:
        list of maximums, length = len(arr) - k + 1
    """
    # TODO: implement using a deque of indices with decreasing values
    pass


def _sol_max_of_subarrays(arr, k):
    """Solution: monotonic decreasing deque of indices."""
    if not arr or k <= 0:
        return []

    dq = collections.deque()  # stores INDICES, not values
    result = []

    for i in range(len(arr)):
        # Remove indices outside the current window [i-k+1, i]
        while dq and dq[0] <= i - k:
            dq.popleft()

        # Remove indices from back whose VALUES are <= arr[i].
        # Why <=? Because if arr[dq[-1]] == arr[i], the older index expires
        # sooner, so the newer one is strictly better. Using < would also work
        # (keeping duplicates in the deque) but wastes space.
        while dq and arr[dq[-1]] <= arr[i]:
            dq.pop()

        dq.append(i)

        # Once we have at least k elements, the front of the deque is the max.
        if i >= k - 1:
            result.append(arr[dq[0]])

    return result


# ===========================================================================
# Exercise 3: First Negative in Every Window of Size K
# ===========================================================================
# Pattern: "find the first element satisfying some property in a sliding window."
# Instead of a monotonic deque, we use a simple queue of negative-valued indices.
# The front of the queue is always the first (leftmost) negative in the window.
#
# Real-world analogy: "first error in the last K log entries" -- you want the
# oldest unresolved error in your monitoring window.

def first_negative_in_window(arr, k):
    """Return the first negative number in every window of size k.
    If a window has no negatives, use 0 for that position.

    Example: arr=[-8,2,3,-6,10], k=2 -> [-8,-8,-6,-6]
      Window [-8,2]:  first negative = -8
      Window [2,3]:   no negative = 0   ... wait, let me re-check
      Actually: [-8,2]->-8, [2,3]->0, [3,-6]->-6, [-6,10]->-6

    Args:
        arr: list of numbers
        k: window size
    Returns:
        list of first negatives (or 0 if none), length = len(arr) - k + 1
    """
    # TODO: implement using a deque that tracks indices of negative numbers
    pass


def _sol_first_negative_in_window(arr, k):
    """Solution: queue of indices of negative numbers."""
    if not arr or k <= 0:
        return []

    # This deque holds indices of NEGATIVE elements only.
    # We don't need a monotonic invariant here -- we just need a FIFO queue
    # of negatives, and we expire indices that fall out of the window.
    neg_dq = collections.deque()
    result = []

    for i in range(len(arr)):
        # Only enqueue indices of negative numbers
        if arr[i] < 0:
            neg_dq.append(i)

        # Remove indices that have fallen out of the window
        while neg_dq and neg_dq[0] <= i - k:
            neg_dq.popleft()

        # Once we have a full window, report the first negative
        if i >= k - 1:
            if neg_dq:
                result.append(arr[neg_dq[0]])
            else:
                result.append(0)  # no negative in this window

    return result


# ===========================================================================
# Exercise 4: Shortest Subarray with Sum >= Target
# ===========================================================================
# This is LeetCode 862. Unlike the basic "minimum window sum" that only works
# for positive numbers, this version handles NEGATIVE numbers too.
#
# Why deque? We maintain a deque of prefix sum indices. For each position i,
# we want the largest j < i such that prefix[i] - prefix[j] >= target.
# A monotonic increasing deque of prefix sums lets us efficiently find and
# discard candidates.
#
# Without the deque: O(n^2) to check all pairs.
# With the deque: O(n) because each index enters and leaves at most once.

def shortest_subarray_sum(nums, target):
    """Return the length of the shortest subarray with sum >= target.
    Return -1 if no such subarray exists.

    This works with negative numbers too (unlike the two-pointer approach).

    Example: nums=[2,-1,2], target=3 -> 3 (the whole array sums to 3)
    Example: nums=[1], target=1 -> 1
    Example: nums=[1,2], target=4 -> -1

    Args:
        nums: list of integers (can be negative)
        target: target sum
    Returns:
        length of shortest qualifying subarray, or -1
    """
    # TODO: implement using prefix sums and a monotonic deque
    pass


def _sol_shortest_subarray_sum(nums, target):
    """Solution: prefix sums + monotonic increasing deque.

    Idea: compute prefix sums P where P[i] = nums[0] + ... + nums[i-1].
    Sum of subarray [j, i) = P[i] - P[j].
    We want the smallest (i - j) such that P[i] - P[j] >= target.

    For a fixed i, we want the LARGEST j (closest to i) such that P[j] <= P[i] - target.

    Deque strategy:
    1. Keep a deque of indices where prefix sums are INCREASING.
       Why? If P[j1] >= P[j2] and j1 < j2, then j1 is useless: j2 gives a
       shorter subarray AND a smaller prefix sum (so it is easier to satisfy
       P[i] - P[j] >= target).

    2. For each i, pop from the FRONT while P[i] - P[front] >= target.
       Each popped front gives a valid subarray -- track the minimum length.
       We can pop because no future i' > i would benefit from this front:
       i' - front > i - front, so the subarray would only be longer.
    """
    n = len(nums)
    # Prefix sum array: P[0] = 0, P[i] = nums[0] + ... + nums[i-1]
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]

    dq = collections.deque()  # stores indices into prefix array
    min_len = float('inf')

    for i in range(n + 1):
        # Pop from front: if prefix[i] - prefix[dq[0]] >= target,
        # we found a valid subarray. Record its length and pop (it won't
        # help any future i since the subarray would only get longer).
        while dq and prefix[i] - prefix[dq[0]] >= target:
            min_len = min(min_len, i - dq.popleft())

        # Pop from back: maintain increasing prefix sums.
        # If prefix[i] <= prefix[dq[-1]], then dq[-1] is useless (see above).
        while dq and prefix[i] <= prefix[dq[-1]]:
            dq.pop()

        dq.append(i)

    return min_len if min_len != float('inf') else -1


# ===========================================================================
# Exercise 5: Longest Subarray with Abs Diff <= Limit
# ===========================================================================
# LeetCode 1438. Find the longest contiguous subarray where the difference
# between the maximum and minimum elements is at most `limit`.
#
# Why TWO deques? We need to track both the sliding max and sliding min
# simultaneously. When max - min > limit, we shrink the window from the left.
#
# Without deques: O(n^2) to recompute max/min for every window.
# With deques: O(n) total -- each element enters/leaves each deque at most once.

def longest_subarray_limit(nums, limit):
    """Return the length of the longest subarray where max - min <= limit.

    Example: nums=[8,2,4,7], limit=4 -> 2 (subarray [2,4] has max-min=2<=4)
    Example: nums=[10,1,2,4,7,2], limit=5 -> 4 (subarray [2,4,7,2])
    Example: nums=[4,2,2,2,4,4,2,2], limit=0 -> 3 (subarray [2,2,2])

    Args:
        nums: list of integers
        limit: maximum allowed difference between max and min in the subarray
    Returns:
        length of the longest qualifying subarray
    """
    # TODO: implement using two deques (one for max, one for min) + sliding window
    pass


def _sol_longest_subarray_limit(nums, limit):
    """Solution: two monotonic deques + sliding window.

    We maintain:
    - max_dq: monotonic DECREASING deque (front = current window max)
    - min_dq: monotonic INCREASING deque (front = current window min)

    Expand the window to the right (add element). If max - min > limit,
    shrink from the left until the constraint is satisfied.
    """
    max_dq = collections.deque()  # decreasing: front = max
    min_dq = collections.deque()  # increasing: front = min
    left = 0
    best = 0

    for right in range(len(nums)):
        # Maintain decreasing deque for max
        while max_dq and nums[max_dq[-1]] <= nums[right]:
            max_dq.pop()
        max_dq.append(right)

        # Maintain increasing deque for min
        while min_dq and nums[min_dq[-1]] >= nums[right]:
            min_dq.pop()
        min_dq.append(right)

        # Shrink window from left until max - min <= limit
        while nums[max_dq[0]] - nums[min_dq[0]] > limit:
            left += 1
            # Remove expired indices from front of deques
            if max_dq[0] < left:
                max_dq.popleft()
            if min_dq[0] < left:
                min_dq.popleft()

        best = max(best, right - left + 1)

    return best


# ===========================================================================
# Test Runner
# ===========================================================================

def run_tests():
    """Run all exercise tests. Uses _sol_ solutions to verify correctness."""
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")
            print(f"        expected: {expected}")
            print(f"        got:      {got}")

    # --- Exercise 1: Palindrome Checker ---
    print("\n--- Exercise 1: Palindrome Checker ---")
    fn1 = palindrome_check if palindrome_check("racecar") is not None else _sol_palindrome_check
    if fn1 is _sol_palindrome_check:
        print("  (using solution -- implement palindrome_check to test yours)")
    check("racecar", fn1("racecar"), True)
    check("hello", fn1("hello"), False)
    check("A man a plan a canal Panama", fn1("A man a plan a canal Panama"), True)
    check("empty string", fn1(""), True)
    check("single char", fn1("a"), True)
    check("Was it a car or a cat I saw", fn1("Was it a car or a cat I saw"), True)
    check("ab", fn1("ab"), False)

    # --- Exercise 2: Max of All Subarrays ---
    print("\n--- Exercise 2: Max of All Subarrays of Size K ---")
    fn2 = max_of_subarrays if max_of_subarrays([1,3,-1], 2) is not None else _sol_max_of_subarrays
    if fn2 is _sol_max_of_subarrays:
        print("  (using solution -- implement max_of_subarrays to test yours)")
    check("basic", fn2([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7])
    check("k=1", fn2([1, 2, 3], 1), [1, 2, 3])
    check("k=len", fn2([3, 1, 2], 3), [3])
    check("all same", fn2([5, 5, 5, 5], 2), [5, 5, 5])
    check("decreasing", fn2([5, 4, 3, 2, 1], 3), [5, 4, 3])
    check("increasing", fn2([1, 2, 3, 4, 5], 3), [3, 4, 5])
    check("empty", fn2([], 3), [])
    check("negatives", fn2([-1, -3, -5, -2, -4], 2), [-1, -3, -2, -2])

    # --- Exercise 3: First Negative in Window ---
    print("\n--- Exercise 3: First Negative in Every Window of Size K ---")
    fn3 = first_negative_in_window if first_negative_in_window([-1, 2], 1) is not None else _sol_first_negative_in_window
    if fn3 is _sol_first_negative_in_window:
        print("  (using solution -- implement first_negative_in_window to test yours)")
    check("basic", fn3([-8, 2, 3, -6, 10], 2), [-8, 0, -6, -6])
    check("all negative", fn3([-1, -2, -3], 2), [-1, -2])
    check("no negatives", fn3([1, 2, 3, 4], 2), [0, 0, 0])
    check("k=1", fn3([1, -2, 3], 1), [0, -2, 0])
    check("single neg at end", fn3([1, 2, -3], 2), [0, -3])
    check("window = array", fn3([12, -1, -7, 8, -15, 30, 16, 28], 3),
          [-1, -1, -7, -15, -15, 0])

    # --- Exercise 4: Shortest Subarray with Sum >= Target ---
    print("\n--- Exercise 4: Shortest Subarray with Sum >= Target ---")
    fn4 = shortest_subarray_sum if shortest_subarray_sum([1], 1) is not None else _sol_shortest_subarray_sum
    if fn4 is _sol_shortest_subarray_sum:
        print("  (using solution -- implement shortest_subarray_sum to test yours)")
    check("basic", fn4([2, -1, 2], 3), 3)
    check("single element", fn4([1], 1), 1)
    check("impossible", fn4([1, 2], 4), -1)
    check("with negatives", fn4([1, -1, 5, -2, 3], 3), 1)
    check("all positive", fn4([1, 1, 1, 1, 1], 3), 3)
    check("large target single", fn4([10, 2, -2], 10), 1)
    check("negative then positive", fn4([-1, 4, -1, 2], 3), 2)

    # --- Exercise 5: Longest Subarray with Abs Diff <= Limit ---
    print("\n--- Exercise 5: Longest Subarray with Abs Diff <= Limit ---")
    fn5 = longest_subarray_limit if longest_subarray_limit([1,1], 0) is not None else _sol_longest_subarray_limit
    if fn5 is _sol_longest_subarray_limit:
        print("  (using solution -- implement longest_subarray_limit to test yours)")
    check("basic", fn5([8, 2, 4, 7], 4), 2)
    check("longer window", fn5([10, 1, 2, 4, 7, 2], 5), 4)
    check("all same", fn5([4, 2, 2, 2, 4, 4, 2, 2], 0), 3)
    check("limit=0 single", fn5([1, 2, 3], 0), 1)
    check("whole array", fn5([1, 2, 3], 10), 3)
    check("two elements", fn5([1, 5], 3), 1)
    check("decreasing", fn5([5, 4, 3, 2, 1], 2), 3)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
