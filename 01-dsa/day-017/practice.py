"""
Day 17 Practice: Two-Pointer Technique
========================================
Implement these exercises to build two-pointer intuition.
Each problem states which pattern applies.
"""


# =============================================================================
# Exercise 1: Valid Palindrome (converging pointers)
# =============================================================================
def is_palindrome(s):
    """
    Check if string is a palindrome, ignoring non-alphanumeric characters.

    Pattern: converging pointers from both ends.

    TODO: Implement
    - left starts at 0, right starts at end
    - Skip non-alphanumeric characters
    - Compare characters (case-insensitive)

    Examples:
        "A man, a plan, a canal: Panama" → True
        "race a car" → False
    """
    pass


# =============================================================================
# Exercise 2: Sort Colors / Dutch National Flag (three-way partition)
# =============================================================================
def sort_colors(nums):
    """
    Sort array containing only 0, 1, 2 in-place. ONE pass, O(1) space.

    This is Dijkstra's Dutch National Flag problem.
    Three pointers: low (0s boundary), mid (current), high (2s boundary)

    TODO: Implement
    - low = 0, mid = 0, high = len(nums) - 1
    - If nums[mid] == 0: swap with low, advance both
    - If nums[mid] == 1: advance mid
    - If nums[mid] == 2: swap with high, shrink high (don't advance mid!)

    Why not advance mid when swapping with high?
    Because the swapped element from high hasn't been examined yet.
    """
    pass


# =============================================================================
# Exercise 3: Trapping Rain Water (converging pointers)
# =============================================================================
def trap_rain_water(heights):
    """
    Given elevation map, compute how much rain water can be trapped.

    Pattern: converging pointers with running max from each side.

    TODO: Implement
    - Track left_max and right_max
    - Water at position i = min(left_max, right_max) - heights[i]
    - Process the side with the smaller max (that's the bottleneck)

    Example: [0,1,0,2,1,0,1,3,2,1,2,1] → 6 units
    """
    pass


# =============================================================================
# Exercise 4: Partition Array (same-direction, like quicksort partition)
# =============================================================================
def partition(arr, pivot):
    """
    Rearrange arr so elements < pivot come before elements >= pivot.
    Return the partition index. In-place, O(n) time, O(1) space.

    Pattern: same-direction pointers.
    - slow marks the boundary of "< pivot" region
    - fast scans for elements that belong in the left partition

    TODO: Implement
    """
    pass


# =============================================================================
# Exercise 5: Move Zeroes (same-direction)
# =============================================================================
def move_zeroes(nums):
    """
    Move all zeroes to end of array while maintaining order of non-zero elements.
    In-place, O(n) time, O(1) space.

    TODO: Implement
    - slow = position to place next non-zero
    - fast = scanner
    - After placing all non-zeros, fill rest with zeros
    """
    pass


# =============================================================================
# SOLUTIONS
# =============================================================================

def _sol_is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        while left < right and not s[left].isalnum():
            left += 1
        while left < right and not s[right].isalnum():
            right -= 1
        if s[left].lower() != s[right].lower():
            return False
        left += 1
        right -= 1
    return True


def _sol_sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1


def _sol_trap_rain_water(heights):
    if len(heights) < 3:
        return 0
    left, right = 0, len(heights) - 1
    left_max, right_max = heights[left], heights[right]
    water = 0
    while left < right:
        if left_max <= right_max:
            left += 1
            left_max = max(left_max, heights[left])
            water += left_max - heights[left]
        else:
            right -= 1
            right_max = max(right_max, heights[right])
            water += right_max - heights[right]
    return water


def _sol_partition(arr, pivot):
    slow = 0
    for fast in range(len(arr)):
        if arr[fast] < pivot:
            arr[slow], arr[fast] = arr[fast], arr[slow]
            slow += 1
    return slow


def _sol_move_zeroes(nums):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1


# =============================================================================
# Tests
# =============================================================================

def run_tests():
    print("=" * 60)
    print("Day 17 Practice Tests: Two Pointers")
    print("=" * 60)

    # Test palindrome
    assert _sol_is_palindrome("A man, a plan, a canal: Panama")
    assert not _sol_is_palindrome("race a car")
    assert _sol_is_palindrome("")
    print("✓ Exercise 1: Valid palindrome")

    # Test sort colors
    nums = [2, 0, 2, 1, 1, 0]
    _sol_sort_colors(nums)
    assert nums == [0, 0, 1, 1, 2, 2]
    print("✓ Exercise 2: Sort colors (Dutch National Flag)")

    # Test trapping rain water
    assert _sol_trap_rain_water([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]) == 6
    assert _sol_trap_rain_water([4, 2, 0, 3, 2, 5]) == 9
    print("✓ Exercise 3: Trapping rain water")

    # Test partition
    arr = [3, 1, 4, 1, 5, 9, 2, 6]
    idx = _sol_partition(arr, 4)
    assert all(x < 4 for x in arr[:idx])
    assert all(x >= 4 for x in arr[idx:])
    print("✓ Exercise 4: Partition array")

    # Test move zeroes
    nums = [0, 1, 0, 3, 12]
    _sol_move_zeroes(nums)
    assert nums == [1, 3, 12, 0, 0]
    print("✓ Exercise 5: Move zeroes")

    print("\nAll tests passed!")


if __name__ == "__main__":
    run_tests()
