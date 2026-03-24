"""
Day 50 Practice: Binary Heap Exercises
=======================================
Implement each function. Run this file to test your solutions.

Key mental model:
    A heap is just a sorted-ish array where the minimum bubbles to the top.
    Every heap problem = "maintain a heap of the right size/type to track what matters."

Rules:
- Do NOT use heapq or any library — implement using the MinHeap/MaxHeap from heap.py
- Solutions are at the bottom — try first.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from heap import MinHeap, MaxHeap


# ─── Exercise 1: Kth Largest Element ────────────────────────────────
#
# Given an unsorted array and k, return the kth largest element.
# Example: nums = [3, 2, 1, 5, 6, 4], k = 2 → 5
#
# Approach: use a min-heap of size k. After processing all elements,
# the heap's minimum is the kth largest.
#
# Why min-heap of size k? Because we want to DISCARD elements smaller
# than the kth largest. A min-heap lets us efficiently check and remove
# the smallest of our k candidates.

def kth_largest(nums, k):
    # TODO: implement
    pass


# ─── Exercise 2: Merge K Sorted Lists ──────────────────────────────
#
# Given k sorted lists, merge them into one sorted list.
# Example: [[1, 4, 7], [2, 5, 8], [3, 6, 9]] → [1, 2, 3, 4, 5, 6, 7, 8, 9]
#
# Approach: use a min-heap of size k, storing (value, list_index, element_index).
# Pop the smallest, then push the next element from that list.
#
# Time: O(N log k) where N = total elements across all lists.
# This beats concatenate-and-sort O(N log N) when k << N.

def merge_k_sorted(lists):
    # TODO: implement
    pass


# ─── Exercise 3: Running Median ────────────────────────────────────
#
# Design a data structure that supports:
#   add_num(num) — add a number from a data stream
#   find_median() — return the median of all numbers added so far
#
# Approach: two heaps
#   max_heap: stores the smaller half (top = largest of small half)
#   min_heap: stores the larger half (top = smallest of large half)
#   Median = top of max_heap (odd count) or average of both tops (even count)
#
# Keep heaps balanced: sizes differ by at most 1.

class MedianFinder:
    def __init__(self):
        # TODO: initialize two heaps
        pass

    def add_num(self, num):
        # TODO: implement
        pass

    def find_median(self):
        # TODO: implement
        pass


# ─── Exercise 4: Sort Nearly Sorted Array ──────────────────────────
#
# An array where each element is at most k positions away from its
# sorted position. Sort it in O(n log k).
#
# Example: arr = [6, 5, 3, 2, 8, 10, 9], k = 3
# Each element is within 3 positions of where it belongs.
#
# Approach: maintain a min-heap of size k+1. The minimum of the window
# must be the next element in sorted order (since elements can't be
# more than k positions away).

def sort_nearly_sorted(arr, k):
    # TODO: implement — return sorted array
    pass


# ─── Exercise 5: Task Scheduler ────────────────────────────────────
#
# Given tasks with frequencies and a cooldown period n, find the minimum
# time to execute all tasks. Same tasks must have at least n intervals between them.
#
# Example: tasks = ['A','A','A','B','B','B'], n = 2
# One valid schedule: A B _ A B _ A B → 8 intervals
#
# Approach: use a max-heap of frequencies. Each round, pop up to (n+1)
# tasks, execute them, and push back any with remaining count.
# If fewer than (n+1) tasks available, we have idle slots.

def task_scheduler(tasks, n):
    # TODO: implement — return minimum intervals
    pass


# ─── Exercise 6: K Closest Points to Origin ────────────────────────
#
# Given a list of points [(x, y), ...] and k, return the k closest
# points to the origin (0, 0).
#
# Example: points = [(1,3), (-2,2), (5,8), (0,1)], k = 2 → [(0,1), (-2,2)]
#
# Approach: use a max-heap of size k storing (-distance, point).
# For each point, if heap size < k, push it. Otherwise, if point is
# closer than the farthest in the heap, replace.

def k_closest_points(points, k):
    # TODO: implement — return list of k closest points
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS — try the exercises first!
# ════════════════════════════════════════════════════════════════════

def _sol_kth_largest(nums, k):
    heap = MinHeap()
    for num in nums:
        heap.push(num)
        if len(heap) > k:
            heap.pop()
    return heap.peek()


def _sol_merge_k_sorted(lists):
    # Since our MinHeap doesn't support tuples natively with custom comparison,
    # we use a simple approach: push (value, list_idx, elem_idx) as a comparable tuple
    heap = MinHeap()
    for i, lst in enumerate(lists):
        if lst:
            heap.push((lst[0], i, 0))

    result = []
    while heap:
        val, li, ei = heap.pop()
        result.append(val)
        if ei + 1 < len(lists[li]):
            heap.push((lists[li][ei + 1], li, ei + 1))
    return result


class _SolMedianFinder:
    def __init__(self):
        self.lo = MaxHeap()  # smaller half
        self.hi = MinHeap()  # larger half

    def add_num(self, num):
        # Always push to lo first, then rebalance
        self.lo.push(num)
        # Ensure lo's max <= hi's min
        if self.hi and self.lo.peek() > self.hi.peek():
            self.hi.push(self.lo.pop())
        # Balance sizes: lo can have at most 1 more than hi
        if len(self.lo) > len(self.hi) + 1:
            self.hi.push(self.lo.pop())
        elif len(self.hi) > len(self.lo):
            self.lo.push(self.hi.pop())

    def find_median(self):
        if len(self.lo) > len(self.hi):
            return self.lo.peek()
        return (self.lo.peek() + self.hi.peek()) / 2


def _sol_sort_nearly_sorted(arr, k):
    heap = MinHeap()
    result = []
    for num in arr:
        heap.push(num)
        if len(heap) > k:
            result.append(heap.pop())
    while heap:
        result.append(heap.pop())
    return result


def _sol_task_scheduler(tasks, n):
    # Count frequencies
    freq = {}
    for t in tasks:
        freq[t] = freq.get(t, 0) + 1

    heap = MaxHeap()
    for count in freq.values():
        heap.push(count)

    time = 0
    while heap:
        cycle = []
        for _ in range(n + 1):
            if heap:
                count = heap.pop()
                if count > 1:
                    cycle.append(count - 1)
            time += 1
            if not heap and not cycle:
                break
        for remaining in cycle:
            heap.push(remaining)

    return time


def _sol_k_closest_points(points, k):
    # Max-heap of size k, keyed by negative distance (so farthest is at top)
    heap = MaxHeap()
    results = []

    for x, y in points:
        dist = x * x + y * y
        if len(results) < k:
            heap.push(dist)
            results.append((x, y))
        elif dist < heap.peek():
            # Find and remove the farthest point
            old_dist = heap.pop()
            # Remove the point with that distance
            for i, (px, py) in enumerate(results):
                if px * px + py * py == old_dist:
                    results.pop(i)
                    break
            heap.push(dist)
            results.append((x, y))
    return results


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected, fuzzy=False):
        nonlocal passed, failed
        if fuzzy:
            ok = abs(got - expected) < 0.01
        elif isinstance(expected, (set, frozenset)):
            ok = set(got) == expected if isinstance(got, list) else got == expected
        else:
            ok = got == expected
        if ok:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1: Kth Largest
    print("\nExercise 1: Kth Largest Element")
    for fn in [kth_largest, _sol_kth_largest]:
        if fn is kth_largest and fn([1], 1) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}([3,2,1,5,6,4], 2)", fn([3, 2, 1, 5, 6, 4], 2), 5)
        check(f"{fn.__name__}([3,2,3,1,2,4,5,5,6], 4)", fn([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4)
        check(f"{fn.__name__}([1], 1)", fn([1], 1), 1)

    # Exercise 2: Merge K Sorted Lists
    print("\nExercise 2: Merge K Sorted Lists")
    for fn in [merge_k_sorted, _sol_merge_k_sorted]:
        if fn is merge_k_sorted and fn([[1]]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}(3 lists)",
              fn([[1, 4, 7], [2, 5, 8], [3, 6, 9]]),
              [1, 2, 3, 4, 5, 6, 7, 8, 9])
        check(f"{fn.__name__}(empty)", fn([[], [1], []]), [1])

    # Exercise 3: Running Median
    print("\nExercise 3: Running Median")
    for Cls in [MedianFinder, _SolMedianFinder]:
        mf = Cls()
        if not hasattr(mf, 'add_num') or not hasattr(mf, 'find_median'):
            print("  (skipped — not implemented)")
            break
        mf.add_num(1)
        r1 = mf.find_median()
        if r1 is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} after [1]", r1, 1, fuzzy=True)
        mf.add_num(2)
        check(f"{Cls.__name__} after [1,2]", mf.find_median(), 1.5, fuzzy=True)
        mf.add_num(3)
        check(f"{Cls.__name__} after [1,2,3]", mf.find_median(), 2, fuzzy=True)
        mf.add_num(4)
        check(f"{Cls.__name__} after [1,2,3,4]", mf.find_median(), 2.5, fuzzy=True)

    # Exercise 4: Sort Nearly Sorted
    print("\nExercise 4: Sort Nearly Sorted")
    for fn in [sort_nearly_sorted, _sol_sort_nearly_sorted]:
        if fn is sort_nearly_sorted and fn([1], 1) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}([6,5,3,2,8,10,9], 3)",
              fn([6, 5, 3, 2, 8, 10, 9], 3),
              [2, 3, 5, 6, 8, 9, 10])
        check(f"{fn.__name__}([1,2,3], 1)", fn([1, 2, 3], 1), [1, 2, 3])

    # Exercise 5: Task Scheduler
    print("\nExercise 5: Task Scheduler")
    for fn in [task_scheduler, _sol_task_scheduler]:
        if fn is task_scheduler and fn(['A'], 0) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}(AAABBB, n=2)", fn(['A','A','A','B','B','B'], 2), 8)
        check(f"{fn.__name__}(AAABBB, n=0)", fn(['A','A','A','B','B','B'], 0), 6)

    # Exercise 6: K Closest Points
    print("\nExercise 6: K Closest Points")
    for fn in [k_closest_points, _sol_k_closest_points]:
        if fn is k_closest_points and fn([(0,0)], 1) is None:
            print("  (skipped — not implemented)")
            break
        result = fn([(1, 3), (-2, 2), (5, 8), (0, 1)], 2)
        dists = sorted([x*x + y*y for x, y in result])
        check(f"{fn.__name__} distances", dists, [1, 8])

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
