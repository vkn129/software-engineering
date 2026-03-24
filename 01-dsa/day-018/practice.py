"""
Day 18 Practice: Sliding Window Exercises

Complete each TODO function. Run this file to verify your solutions
against the test cases. Solutions are at the bottom — try before peeking.

Run: python practice.py
"""


# ---------------------------------------------------------------------------
# Exercise 1: Fixed-Width Sliding Window — Max Sum of K Elements
# ---------------------------------------------------------------------------

def max_sum_k(arr, k):
    """Return the maximum sum of any k consecutive elements in arr.

    Approach: compute the first window sum, then slide by subtracting
    the element leaving and adding the element entering.

    Args:
        arr: list of integers (can be negative)
        k: window size (1 <= k <= len(arr))

    Returns:
        Maximum sum of k consecutive elements.

    Example:
        max_sum_k([2, 1, 5, 1, 3, 2], 3) -> 10  # [5, 1, 3]... wait, [5,3,2]=10? Let's check: [5,1,3]=9, [1,3,2]=6. Actually [2,1,5]=8,[1,5,1]=7,[5,1,3]=9,[1,3,2]=6 -> 9
        max_sum_k([2, 1, 5, 1, 3, 2], 3) -> 9    # [5, 1, 3]
    """
    # TODO: Implement fixed-width sliding window
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Kadane's Algorithm — Maximum Subarray Sum
# ---------------------------------------------------------------------------

def max_subarray(arr):
    """Return the maximum sum of any contiguous subarray.

    At each position, decide: extend the current subarray or start fresh.
    If the running sum is negative, the prefix is a liability — discard it.

    Args:
        arr: non-empty list of integers (can be negative)

    Returns:
        Maximum subarray sum.

    Example:
        max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) -> 6  # [4, -1, 2, 1]
        max_subarray([-1, -2, -3]) -> -1  # single element
    """
    # TODO: Implement Kadane's algorithm
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Longest Substring Without Repeating Characters
# ---------------------------------------------------------------------------

def longest_unique_substring(s):
    """Return the length of the longest substring with all unique characters.

    Use a variable-width sliding window: expand right to explore, contract
    left when a duplicate is found, maintaining a character count map.

    Args:
        s: a string

    Returns:
        Length of the longest substring without repeating characters.

    Example:
        longest_unique_substring("abcabcbb") -> 3  # "abc"
        longest_unique_substring("bbbbb") -> 1      # "b"
        longest_unique_substring("pwwkew") -> 3     # "wke"
        longest_unique_substring("") -> 0
    """
    # TODO: Implement variable-width sliding window
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Minimum Window Substring
# ---------------------------------------------------------------------------

def min_window(s, t):
    """Return the minimum window in s that contains all characters of t.

    Strategy:
    1. Build a frequency map of characters needed from t.
    2. Expand right until all characters are covered.
    3. Contract left to find the smallest valid window.
    4. Track 'formed' = number of distinct chars from t with sufficient count.

    Args:
        s: source string
        t: target string (all characters must appear in the window)

    Returns:
        The minimum window substring, or "" if no valid window exists.

    Example:
        min_window("ADOBECODEBANC", "ABC") -> "BANC"
        min_window("a", "a") -> "a"
        min_window("a", "aa") -> ""
    """
    # TODO: Implement minimum window substring
    pass


# ---------------------------------------------------------------------------
# Exercise 5 (BONUS): Max Consecutive Ones III
# ---------------------------------------------------------------------------

def max_ones_after_flips(arr, k):
    """Given a binary array, return the maximum number of consecutive 1s
    if you can flip at most k 0s to 1s.

    This is a variable-width sliding window problem: maintain a window
    where the count of 0s is at most k. When zero_count exceeds k,
    shrink from left.

    Args:
        arr: list of 0s and 1s
        k: max number of 0s you can flip

    Returns:
        Maximum length of consecutive 1s after at most k flips.

    Example:
        max_ones_after_flips([1,1,1,0,0,0,1,1,1,1,0], 2) -> 6
        max_ones_after_flips([0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], 3) -> 10
    """
    # TODO: Implement using variable-width sliding window
    pass


# ===========================================================================
# TEST CASES
# ===========================================================================

def run_tests():
    """Run all test cases and report results."""
    print("Day 18 Practice: Sliding Window Exercises")
    print("=" * 60)
    print()

    all_passed = True

    # --- Exercise 1: Max Sum K ---
    print("Exercise 1: Max Sum of K Consecutive Elements")
    tests_1 = [
        ([2, 1, 5, 1, 3, 2], 3, 9),
        ([1, 2, 3, 4, 5], 2, 9),
        ([5], 1, 5),
        ([-1, -2, -3, -4], 2, -3),
        ([1, 4, 2, 10, 23, 3, 1, 0, 20], 4, 39),
        ([100, 200, 300, 400], 4, 1000),
    ]
    for arr, k, expected in tests_1:
        result = max_sum_k(arr, k)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {status}: max_sum_k({arr}, {k}) = {result} (expected {expected})")
    print()

    # --- Exercise 2: Kadane's ---
    print("Exercise 2: Maximum Subarray Sum (Kadane's)")
    tests_2 = [
        ([-2, 1, -3, 4, -1, 2, 1, -5, 4], 6),
        ([1], 1),
        ([-1], -1),
        ([-1, -2, -3], -1),
        ([5, 4, -1, 7, 8], 23),
        ([-2, -3, 4, -1, -2, 1, 5, -3], 7),
    ]
    for arr, expected in tests_2:
        result = max_subarray(arr)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {status}: max_subarray({arr}) = {result} (expected {expected})")
    print()

    # --- Exercise 3: Longest Unique Substring ---
    print("Exercise 3: Longest Substring Without Repeating Characters")
    tests_3 = [
        ("abcabcbb", 3),
        ("bbbbb", 1),
        ("pwwkew", 3),
        ("", 0),
        ("abcdef", 6),
        ("aab", 2),
        ("dvdf", 3),
        (" ", 1),
    ]
    for s, expected in tests_3:
        result = longest_unique_substring(s)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {status}: longest_unique_substring(\"{s}\") = {result} (expected {expected})")
    print()

    # --- Exercise 4: Minimum Window Substring ---
    print("Exercise 4: Minimum Window Substring")
    tests_4 = [
        ("ADOBECODEBANC", "ABC", "BANC"),
        ("a", "a", "a"),
        ("a", "aa", ""),
        ("aa", "aa", "aa"),
        ("abc", "b", "b"),
        ("cabwefgewcwaefgcf", "cae", "cwae"),
    ]
    for s, t, expected in tests_4:
        result = min_window(s, t)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {status}: min_window(\"{s}\", \"{t}\") = \"{result}\" (expected \"{expected}\")")
    print()

    # --- Exercise 5: Max Ones After Flips ---
    print("Exercise 5 (BONUS): Max Consecutive Ones III")
    tests_5 = [
        ([1,1,1,0,0,0,1,1,1,1,0], 2, 6),
        ([0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], 3, 10),
        ([1,1,1,1], 0, 4),
        ([0,0,0], 3, 3),
        ([0,0,0], 0, 0),
    ]
    for arr, k, expected in tests_5:
        result = max_ones_after_flips(arr, k)
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {status}: max_ones_after_flips({arr}, {k}) = {result} (expected {expected})")
    print()

    # --- Summary ---
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("Some tests failed. Keep working on the TODO functions.")
        print("Solutions are below — try before peeking!")

    return all_passed


# ===========================================================================
# SOLUTIONS — scroll down only after attempting all exercises above
# ===========================================================================


SOLUTIONS = """
+======================================================================+
|                           SOLUTIONS                                   |
+======================================================================+

Exercise 1: Max Sum of K Consecutive Elements
----------------------------------------------
def max_sum_k(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum
    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i - k] + arr[i]
        max_sum = max(max_sum, window_sum)
    return max_sum

Why: The recurrence S(i+1) = S(i) - arr[i] + arr[i+k] gives O(1) per
slide. Each element is added once and subtracted once: O(n) total.


Exercise 2: Maximum Subarray Sum (Kadane's)
---------------------------------------------
def max_subarray(arr):
    max_sum = current = arr[0]
    for i in range(1, len(arr)):
        current = max(arr[i], current + arr[i])
        max_sum = max(max_sum, current)
    return max_sum

Why: At each position, if current + arr[i] < arr[i], the accumulated
sum is negative — a liability. Starting fresh at arr[i] is strictly
better than carrying the negative prefix. This is optimal because any
maximum subarray must end somewhere, and for each ending position we
compute the best possible starting point.


Exercise 3: Longest Substring Without Repeating Characters
------------------------------------------------------------
def longest_unique_substring(s):
    char_count = {}
    left = 0
    best = 0
    for right in range(len(s)):
        ch = s[right]
        char_count[ch] = char_count.get(ch, 0) + 1
        while char_count[ch] > 1:
            left_ch = s[left]
            char_count[left_ch] -= 1
            if char_count[left_ch] == 0:
                del char_count[left_ch]
            left += 1
        best = max(best, right - left + 1)
    return best

Why: The window [left..right] is always duplicate-free. When adding
s[right] creates a duplicate, we shrink from left until it is gone.
left moves at most n times total across all iterations: O(n).


Exercise 4: Minimum Window Substring
---------------------------------------
def min_window(s, t):
    if not s or not t:
        return ""
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    required = len(need)
    formed = 0
    have = {}
    left = 0
    best_len = float('inf')
    best_start = 0
    for right in range(len(s)):
        ch = s[right]
        have[ch] = have.get(ch, 0) + 1
        if ch in need and have[ch] == need[ch]:
            formed += 1
        while formed == required:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                best_start = left
            left_ch = s[left]
            have[left_ch] -= 1
            if left_ch in need and have[left_ch] < need[left_ch]:
                formed -= 1
            left += 1
    return s[best_start:best_start + best_len] if best_len != float('inf') else ""

Why: We expand right to gain coverage, contract left to minimize the
window. 'formed' tracks how many distinct characters from t are fully
satisfied. Monotonicity: removing from left can only reduce coverage.


Exercise 5: Max Consecutive Ones III
---------------------------------------
def max_ones_after_flips(arr, k):
    left = 0
    zero_count = 0
    best = 0
    for right in range(len(arr)):
        if arr[right] == 0:
            zero_count += 1
        while zero_count > k:
            if arr[left] == 0:
                zero_count -= 1
            left += 1
        best = max(best, right - left + 1)
    return best

Why: The window contains at most k zeros. When adding a zero exceeds k,
shrink from left until a zero is removed. Monotonicity: expanding the
window can only add zeros (making it worse), shrinking can only remove
them (making it better). Classic variable-width sliding window.
"""


def show_solutions():
    """Print solutions for reference."""
    print(SOLUTIONS)


if __name__ == "__main__":
    passed = run_tests()
    if not passed:
        print("\n" + "-" * 60)
        print("Scroll down in practice.py to see solutions (or run with --solutions)")
        print("-" * 60)

    import sys
    if "--solutions" in sys.argv:
        show_solutions()
