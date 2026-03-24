"""
Day 17: Two-Pointer Technique
==============================
Why it works: When a problem has a monotonic relationship between two indices,
we can avoid checking all O(n²) pairs by moving pointers intelligently.

The key insight: if moving one pointer in a direction can only make the answer
better/worse monotonically, we never need to backtrack — giving us O(n).
"""


# =============================================================================
# Pattern 1: Opposite-direction pointers (converging)
# =============================================================================
# Two pointers start at opposite ends and move toward each other.
# Works when: the contribution of each end is monotonically ordered.

def two_sum_sorted(arr, target):
    """
    Find two numbers in a SORTED array that sum to target.

    Why two pointers work here:
    - If arr[left] + arr[right] > target, arr[right] is too big → move right down
    - If arr[left] + arr[right] < target, arr[left] is too small → move left up
    - Monotonicity: moving left up increases the sum, moving right down decreases it

    Time: O(n)  Space: O(1)
    Brute force would be O(n²) — checking all pairs.
    """
    left, right = 0, len(arr) - 1

    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return (left, right)
        elif current_sum < target:
            left += 1
        else:
            right -= 1

    return None


def container_with_most_water(heights):
    """
    Given heights of vertical lines, find two that form a container holding the most water.

    Why two pointers: area = min(h[l], h[r]) * (r - l).
    Moving the shorter line inward is the only way to potentially increase area,
    because width decreases — we need a taller line to compensate.

    Time: O(n)  Space: O(1)
    """
    left, right = 0, len(heights) - 1
    max_area = 0

    while left < right:
        width = right - left
        height = min(heights[left], heights[right])
        area = width * height
        max_area = max(max_area, area)

        # Move the shorter side — it's the bottleneck
        if heights[left] < heights[right]:
            left += 1
        else:
            right -= 1

    return max_area


# =============================================================================
# Pattern 2: Same-direction pointers (fast/slow or sliding)
# =============================================================================
# Both pointers move in the same direction. One leads, one follows.
# Works when: we need to maintain some invariant over a subarray.

def remove_duplicates_sorted(arr):
    """
    Remove duplicates in-place from a sorted array. Return new length.

    Slow pointer: marks the end of the "clean" region.
    Fast pointer: scans ahead for new unique elements.

    Time: O(n)  Space: O(1)
    """
    if not arr:
        return 0

    slow = 0  # Last position of unique element

    for fast in range(1, len(arr)):
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]

    return slow + 1  # Length of unique portion


def merge_sorted_arrays(arr1, arr2):
    """
    Merge two sorted arrays into one sorted array.

    Two pointers, one per array, both moving forward.
    Always pick the smaller element — both arrays are sorted so
    the smaller front element is globally the next smallest.

    Time: O(n + m)  Space: O(n + m)
    This is the merge step in merge sort.
    """
    result = []
    i, j = 0, 0

    while i < len(arr1) and j < len(arr2):
        if arr1[i] <= arr2[j]:
            result.append(arr1[i])
            i += 1
        else:
            result.append(arr2[j])
            j += 1

    # One array is exhausted — append the rest of the other
    result.extend(arr1[i:])
    result.extend(arr2[j:])
    return result


# =============================================================================
# Pattern 3: Three pointers (reducing to two-pointer subproblem)
# =============================================================================

def three_sum(arr, target=0):
    """
    Find all unique triplets that sum to target.

    Strategy: sort, then for each element, run two-sum on the remaining array.
    Sorting takes O(n log n), then n iterations of O(n) two-pointer = O(n²).

    Without sorting: O(n³) brute force or O(n²) with hash set (but duplicates are messy).
    Two pointers on sorted array handles duplicates cleanly.
    """
    arr.sort()
    result = []

    for i in range(len(arr) - 2):
        # Skip duplicate first elements
        if i > 0 and arr[i] == arr[i - 1]:
            continue

        left, right = i + 1, len(arr) - 1

        while left < right:
            total = arr[i] + arr[left] + arr[right]

            if total == target:
                result.append([arr[i], arr[left], arr[right]])
                # Skip duplicates for second and third elements
                while left < right and arr[left] == arr[left + 1]:
                    left += 1
                while left < right and arr[right] == arr[right - 1]:
                    right -= 1
                left += 1
                right -= 1
            elif total < target:
                left += 1
            else:
                right -= 1

    return result


# =============================================================================
# When Two Pointers FAIL
# =============================================================================

def when_two_pointers_fail():
    """
    Two pointers require MONOTONICITY — moving a pointer in one direction
    must consistently move the answer in one direction.

    Fails when:
    1. Array is unsorted and problem needs order
    2. No monotonic relationship between pointer movement and answer
    3. Need to consider non-contiguous elements
    """
    print("Two pointers FAIL when:")
    print("  1. Two-sum on UNSORTED array — no monotonic relationship")
    print("     → Use hash map instead: O(n) time, O(n) space")
    print("  2. Finding pairs with XOR = k — XOR isn't monotonic")
    print("     → Use hash map")
    print("  3. Longest subsequence (non-contiguous) problems")
    print("     → Use DP instead")
    print()
    print("Rule of thumb: if sorting the input doesn't destroy information")
    print("you need, two pointers probably works. If it does, use a hash map.")


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Day 17: Two-Pointer Technique")
    print("=" * 60)

    # Pattern 1: Converging pointers
    print("\n--- Pattern 1: Opposite-direction (converging) ---")
    arr = [2, 7, 11, 15]
    result = two_sum_sorted(arr, 9)
    print(f"Two sum sorted {arr}, target=9: indices {result}")

    heights = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    print(f"Container with most water {heights}: {container_with_most_water(heights)}")

    # Pattern 2: Same-direction pointers
    print("\n--- Pattern 2: Same-direction (fast/slow) ---")
    arr = [1, 1, 2, 2, 3, 4, 4, 5]
    new_len = remove_duplicates_sorted(arr)
    print(f"Remove duplicates: {arr[:new_len]} (length {new_len})")

    merged = merge_sorted_arrays([1, 3, 5, 7], [2, 4, 6, 8])
    print(f"Merge sorted: {merged}")

    # Pattern 3: Three pointers
    print("\n--- Pattern 3: Three-sum (reduce to two-pointer) ---")
    arr = [-1, 0, 1, 2, -1, -4]
    print(f"Three sum {arr}, target=0: {three_sum(arr)}")

    # When it fails
    print("\n--- When Two Pointers Fail ---")
    when_two_pointers_fail()
