"""
Day 61 Practice: K-way Merge and Top-K Exercises
=================================================
Implement each function. Run this file to test your solutions.

Key mental model:
    K-way merge = "heap of size k tracking the frontier of k sorted streams."
    Top-K = "heap of size k as a gatekeeper — only the worthy survive."

Rules:
- You CAN use heapq for these exercises (unlike Day 50 where we built from scratch).
  The point today is the *patterns*, not reimplementing the heap.
- Solutions are at the bottom — try first.
"""

import heapq
import math


# ─── Exercise 1: Merge K Sorted Linked Lists ─────────────────────
#
# Given k sorted lists (simulating linked lists), merge into one sorted list.
# Use a heap with index tracking to know which list each element came from.
#
# Example: [[1,4,5], [1,3,4], [2,6]] → [1,1,2,3,4,4,5,6]
#
# The twist vs. basic merge: you must handle duplicate values across lists.
# The heap entry needs (value, list_index, element_index) to break ties
# deterministically (by list index, then by position).
#
# Time: O(n log k), Space: O(k) heap + O(n) output

def merge_k_sorted_lists(lists):
    # TODO: implement
    return None


# ─── Exercise 2: K Closest Points to Origin ──────────────────────
#
# Given a list of points [(x, y), ...] and k, return the k closest
# points to the origin (0, 0). Distance = sqrt(x^2 + y^2), but
# compare squared distances to avoid floating point.
#
# Example: points = [(1,3), (-2,2), (5,8), (0,1)], k = 2
#          → [(0,1), (-2,2)]  (distances: 1, sqrt(8), sqrt(89), sqrt(10))
#
# Approach: max-heap of size k. Use negative distance so heapq (min-heap)
# acts as max-heap. The "farthest" of our k candidates sits at the top
# for easy eviction.
#
# Time: O(n log k), Space: O(k)

def k_closest_points(points, k):
    # TODO: implement — return list of k closest points (any order)
    return None


# ─── Exercise 3: Median of Two Sorted Arrays ─────────────────────
#
# Given two sorted arrays nums1 and nums2, return the median of the
# combined sorted array. Must be O(log(min(m, n))).
#
# Example: nums1 = [1, 3], nums2 = [2] → 2.0
#          nums1 = [1, 2], nums2 = [3, 4] → 2.5
#
# Approach: Binary search on the shorter array. We partition both arrays
# such that all elements on the left side <= all elements on the right side.
# If nums1 has partition at i, nums2 must partition at j = (m+n+1)//2 - i
# to keep left and right halves balanced.
#
# The key insight: we only need to binary search on the shorter array.
# For each candidate partition i in nums1, j is determined. Then check:
#   nums1[i-1] <= nums2[j]  AND  nums2[j-1] <= nums1[i]
# If both hold, we found the correct partition.
#
# Time: O(log(min(m, n))), Space: O(1)

def median_of_two_sorted(nums1, nums2):
    # TODO: implement
    return None


# ─── Exercise 4: Top-K Frequent Elements ─────────────────────────
#
# Given an array of integers and k, return the k most frequent elements.
#
# Example: nums = [1,1,1,2,2,3], k = 2 → [1, 2]
#
# Approach:
# 1. Build frequency map: O(n)
# 2. Use min-heap of size k on (frequency, element) pairs: O(m log k)
#    where m = number of unique elements
#
# Why not just sort by frequency? Sorting is O(m log m). If k << m,
# the heap approach is O(m log k), which is faster.
#
# Time: O(n + m log k), Space: O(m) for freq map + O(k) for heap

def top_k_frequent(nums, k):
    # TODO: implement — return list of k most frequent elements (any order)
    return None


# ─── Exercise 5: Sort Nearly-Sorted Array ────────────────────────
#
# Given an array where each element is at most k positions from its
# sorted position, sort it in O(n log k).
#
# Example: arr = [6, 5, 3, 2, 8, 10, 9], k = 3
#          → [2, 3, 5, 6, 8, 9, 10]
#
# Approach: maintain a min-heap of size (k+1). The smallest element
# in any window of (k+1) consecutive elements MUST be the next element
# in sorted order (because no element is more than k positions away).
#
# Slide the window across the array, always popping the minimum.
#
# Time: O(n log k), Space: O(k)

def sort_nearly_sorted(arr, k):
    # TODO: implement — return sorted array
    return None


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS — try the exercises first!
# ════════════════════════════════════════════════════════════════════

def _sol_merge_k_sorted_lists(lists):
    heap = []
    for i, lst in enumerate(lists):
        if lst:
            # (value, list_index, element_index) — list_index breaks value ties
            heapq.heappush(heap, (lst[0], i, 0))

    result = []
    while heap:
        val, li, ei = heapq.heappop(heap)
        result.append(val)
        next_ei = ei + 1
        if next_ei < len(lists[li]):
            heapq.heappush(heap, (lists[li][next_ei], li, next_ei))

    return result


def _sol_k_closest_points(points, k):
    # Max-heap of size k using negative squared distance
    # Heap entries: (-squared_dist, x, y)
    heap = []
    for x, y in points:
        dist_sq = x * x + y * y
        if len(heap) < k:
            heapq.heappush(heap, (-dist_sq, x, y))
        elif -dist_sq > heap[0][0]:  # closer than farthest in heap
            heapq.heapreplace(heap, (-dist_sq, x, y))

    return [(x, y) for _, x, y in heap]


def _sol_median_of_two_sorted(nums1, nums2):
    # Ensure nums1 is the shorter array — we binary search on it
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    half = (m + n + 1) // 2  # size of left partition

    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2       # partition index in nums1
        j = half - i              # partition index in nums2

        # Elements at the partition boundary (use -inf/+inf for edges)
        left1 = nums1[i - 1] if i > 0 else float('-inf')
        right1 = nums1[i] if i < m else float('inf')
        left2 = nums2[j - 1] if j > 0 else float('-inf')
        right2 = nums2[j] if j < n else float('inf')

        # Check if partition is correct
        if left1 <= right2 and left2 <= right1:
            # Found correct partition
            if (m + n) % 2 == 1:
                return max(left1, left2)  # odd total: median is max of left side
            else:
                return (max(left1, left2) + min(right1, right2)) / 2
        elif left1 > right2:
            hi = i - 1  # too many elements from nums1 on left side
        else:
            lo = i + 1  # too few elements from nums1 on left side

    raise ValueError("Input arrays are not sorted")


def _sol_top_k_frequent(nums, k):
    # Step 1: frequency map
    freq = {}
    for num in nums:
        freq[num] = freq.get(num, 0) + 1

    # Step 2: min-heap of size k on (frequency, element)
    heap = []
    for elem, count in freq.items():
        if len(heap) < k:
            heapq.heappush(heap, (count, elem))
        elif count > heap[0][0]:
            heapq.heapreplace(heap, (count, elem))

    return [elem for count, elem in heap]


def _sol_sort_nearly_sorted(arr, k):
    # Heap of the first k+1 elements — the minimum must be the first output
    heap = arr[:k + 1]
    heapq.heapify(heap)

    result = []
    for i in range(k + 1, len(arr)):
        # Pop the smallest (it belongs at result[i - k - 1])
        result.append(heapq.heappop(heap))
        heapq.heappush(heap, arr[i])

    # Drain the remaining heap
    while heap:
        result.append(heapq.heappop(heap))

    return result


# ─── Test Runner ───────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0
    skipped = 0

    def check(name, got, expected, fuzzy=False, unordered=False):
        nonlocal passed, failed
        if fuzzy:
            ok = abs(got - expected) < 0.01
        elif unordered:
            ok = sorted(got) == sorted(expected)
        else:
            ok = got == expected
        if ok:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    def try_exercise(name, user_fn, sol_fn, tests):
        """Run tests for user function and solution. Skip user if not implemented."""
        nonlocal skipped
        print(f"\n{name}")

        for fn in [user_fn, sol_fn]:
            # Check if user function is implemented
            if fn is user_fn:
                try:
                    first_test = tests[0]
                    result = fn(*first_test["args"])
                    if result is None:
                        print("  ⬜ Not implemented yet — skipping")
                        skipped += 1
                        break
                except Exception:
                    print("  ⬜ Not implemented yet — skipping")
                    skipped += 1
                    break

            label = fn.__name__
            for t in tests:
                check(f"{label}({t['label']})", fn(*t["args"]), t["expected"],
                      fuzzy=t.get("fuzzy", False), unordered=t.get("unordered", False))

    # Exercise 1: Merge K Sorted Lists
    try_exercise(
        "Exercise 1: Merge K Sorted Lists",
        merge_k_sorted_lists, _sol_merge_k_sorted_lists,
        [
            {"args": ([[1, 4, 5], [1, 3, 4], [2, 6]],),
             "label": "[[1,4,5],[1,3,4],[2,6]]",
             "expected": [1, 1, 2, 3, 4, 4, 5, 6]},
            {"args": ([[], [1], []],),
             "label": "with empties",
             "expected": [1]},
            {"args": ([[5, 10], [1, 2, 3], [4, 7, 8, 9]],),
             "label": "unequal lengths",
             "expected": [1, 2, 3, 4, 5, 7, 8, 9, 10]},
        ]
    )

    # Exercise 2: K Closest Points
    try_exercise(
        "Exercise 2: K Closest Points to Origin",
        k_closest_points, _sol_k_closest_points,
        [
            {"args": ([(1, 3), (-2, 2), (5, 8), (0, 1)], 2),
             "label": "4 points, k=2",
             "expected": [(-2, 2), (0, 1)],
             "unordered": True},
            {"args": ([(3, 3), (5, -1), (-2, 4)], 1),
             "label": "3 points, k=1",
             "expected": [(3, 3)],
             "unordered": True},
        ]
    )

    # Exercise 3: Median of Two Sorted Arrays
    try_exercise(
        "Exercise 3: Median of Two Sorted Arrays",
        median_of_two_sorted, _sol_median_of_two_sorted,
        [
            {"args": ([1, 3], [2]),
             "label": "[1,3]+[2]",
             "expected": 2.0, "fuzzy": True},
            {"args": ([1, 2], [3, 4]),
             "label": "[1,2]+[3,4]",
             "expected": 2.5, "fuzzy": True},
            {"args": ([], [1]),
             "label": "[]+[1]",
             "expected": 1.0, "fuzzy": True},
            {"args": ([2], []),
             "label": "[2]+[]",
             "expected": 2.0, "fuzzy": True},
            {"args": ([1, 3, 5, 7], [2, 4, 6, 8]),
             "label": "interleaved",
             "expected": 4.5, "fuzzy": True},
        ]
    )

    # Exercise 4: Top-K Frequent Elements
    try_exercise(
        "Exercise 4: Top-K Frequent Elements",
        top_k_frequent, _sol_top_k_frequent,
        [
            {"args": ([1, 1, 1, 2, 2, 3], 2),
             "label": "[1,1,1,2,2,3] k=2",
             "expected": [1, 2],
             "unordered": True},
            {"args": ([4, 4, 4, 4, 5, 5, 5, 6, 6, 7], 1),
             "label": "k=1 (most frequent)",
             "expected": [4],
             "unordered": True},
            {"args": ([1, 2, 3, 4, 5], 3),
             "label": "all freq=1, k=3",
             "expected": [1, 2, 3],  # any 3 elements valid
             "unordered": True},
        ]
    )

    # Exercise 5: Sort Nearly Sorted
    try_exercise(
        "Exercise 5: Sort Nearly-Sorted Array",
        sort_nearly_sorted, _sol_sort_nearly_sorted,
        [
            {"args": ([6, 5, 3, 2, 8, 10, 9], 3),
             "label": "[6,5,3,2,8,10,9] k=3",
             "expected": [2, 3, 5, 6, 8, 9, 10]},
            {"args": ([1, 2, 3], 1),
             "label": "already sorted",
             "expected": [1, 2, 3]},
            {"args": ([3, 1, 2, 5, 4, 6], 2),
             "label": "[3,1,2,5,4,6] k=2",
             "expected": [1, 2, 3, 4, 5, 6]},
        ]
    )

    print(f"\n{'=' * 50}")
    print(f"Results: {passed} passed, {failed} failed, {skipped} not yet implemented")


if __name__ == "__main__":
    run_tests()
