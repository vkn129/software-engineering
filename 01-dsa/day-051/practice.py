"""
Day 51 Practice: Heap Application Exercises
=============================================
All exercises use heap patterns from today's lesson.
You MAY use Python's heapq module (we built our own yesterday).

Run: python practice.py
"""

import heapq
from collections import Counter


# ─── Exercise 1: Frequency Sort ─────────────────────────────────────
#
# Sort an array so elements with higher frequency come first.
# Among elements with the same frequency, sort by value ascending.
# Example: [1,1,2,2,2,3] → [2,2,2,1,1,3]
#
# Approach: count frequencies, use a max-heap keyed by (-freq, value).

def frequency_sort_array(nums):
    # TODO: implement
    pass


# ─── Exercise 2: Reorganize String ──────────────────────────────────
#
# Rearrange a string so no two adjacent characters are the same.
# Return "" if impossible.
# Example: "aab" → "aba"
# Example: "aaab" → "" (impossible)
#
# Approach: max-heap of (-count, char). Each step, pop the most frequent
# char, append it, then push the PREVIOUS char back (so it's not adjacent).
# Impossible when the most frequent char has count > (len+1)//2.

def reorganize_string(s):
    # TODO: implement
    pass


# ─── Exercise 3: Connect Ropes (Minimum Cost) ──────────────────────
#
# Given rope lengths, connect them into one rope. Cost of connecting
# two ropes = sum of their lengths. Find minimum total cost.
# Example: [4, 3, 2, 6] → connect 2+3=5 (cost 5), 4+5=9 (cost 9),
#          6+9=15 (cost 15) → total 29
#
# Greedy: always connect the two shortest ropes.
# This minimizes how many times each rope contributes to future costs.

def min_cost_ropes(ropes):
    # TODO: implement
    pass


# ─── Exercise 4: K Closest Points to Origin ────────────────────────
#
# Given points = [(x, y), ...] and k, return k closest to (0, 0).
# Distances compared by x² + y² (no need for sqrt).
#
# Use a MAX-heap of size k. If a new point is closer than the farthest
# in the heap, swap it in.

def k_closest(points, k):
    # TODO: return list of k closest (x, y) tuples
    pass


# ─── Exercise 5: IPO (Maximize Capital) ────────────────────────────
#
# You have initial capital W. Each project i has profit[i] and minimum
# capital required capital[i]. You can do at most k projects sequentially.
# After completing a project, you gain its profit (added to your capital).
# Maximize your total capital.
#
# Example: k=2, W=0, profits=[1,2,3], capital=[0,1,1]
# Do project 0 (needs 0, gain 1) → capital=1
# Do project 2 (needs 1, gain 3) → capital=4
#
# Approach:
# 1. Sort projects by capital requirement
# 2. For each round: push all affordable projects into a max-heap (by profit)
# 3. Pop the most profitable affordable project
# This is greedy: always pick the most profitable project you can afford.

def find_maximized_capital(k, W, profits, capital):
    # TODO: implement — return final capital
    pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_frequency_sort_array(nums):
    freq = Counter(nums)
    # Sort by (-frequency, value) so higher freq comes first, ties broken by value
    return sorted(nums, key=lambda x: (-freq[x], x))


def _sol_reorganize_string(s):
    freq = Counter(s)
    max_freq = max(freq.values())
    if max_freq > (len(s) + 1) // 2:
        return ""

    heap = [(-count, char) for char, count in freq.items()]
    heapq.heapify(heap)

    result = []
    prev_count, prev_char = 0, ''

    while heap:
        neg_count, char = heapq.heappop(heap)
        # Push back the previous character (it's now safe, not adjacent)
        if prev_count < 0:
            heapq.heappush(heap, (prev_count, prev_char))
        result.append(char)
        prev_count = neg_count + 1  # Used one occurrence
        prev_char = char

    return ''.join(result)


def _sol_min_cost_ropes(ropes):
    if len(ropes) <= 1:
        return 0
    heapq.heapify(ropes)
    total = 0
    while len(ropes) > 1:
        a = heapq.heappop(ropes)
        b = heapq.heappop(ropes)
        cost = a + b
        total += cost
        heapq.heappush(ropes, cost)
    return total


def _sol_k_closest(points, k):
    # Max-heap of size k using negative distances
    heap = []
    for x, y in points:
        dist = x * x + y * y
        if len(heap) < k:
            heapq.heappush(heap, (-dist, x, y))
        elif -dist > heap[0][0]:
            heapq.heapreplace(heap, (-dist, x, y))
    return [(x, y) for _, x, y in heap]


def _sol_find_maximized_capital(k, W, profits, capital):
    # Pair and sort by capital requirement
    projects = sorted(zip(capital, profits))
    heap = []  # max-heap of profits (negated)
    idx = 0

    for _ in range(k):
        # Push all affordable projects
        while idx < len(projects) and projects[idx][0] <= W:
            heapq.heappush(heap, -projects[idx][1])
            idx += 1
        if not heap:
            break
        W += -heapq.heappop(heap)  # Take the most profitable

    return W


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1
    print("\nExercise 1: Frequency Sort Array")
    for fn in [frequency_sort_array, _sol_frequency_sort_array]:
        if fn is frequency_sort_array and fn([1]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}([1,1,2,2,2,3])", fn([1, 1, 2, 2, 2, 3]), [2, 2, 2, 1, 1, 3])

    # Exercise 2
    print("\nExercise 2: Reorganize String")
    for fn in [reorganize_string, _sol_reorganize_string]:
        if fn is reorganize_string and fn("aab") is None:
            print("  (skipped — not implemented)")
            break
        result = fn("aab")
        # Valid if no adjacent same chars
        valid = all(result[i] != result[i + 1] for i in range(len(result) - 1))
        check(f"{fn.__name__}('aab') valid", valid and sorted(result) == sorted("aab"), True)
        check(f"{fn.__name__}('aaab') impossible", fn("aaab"), "")

    # Exercise 3
    print("\nExercise 3: Connect Ropes")
    for fn in [min_cost_ropes, _sol_min_cost_ropes]:
        if fn is min_cost_ropes and fn([1, 2]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}([4,3,2,6])", fn([4, 3, 2, 6]), 29)
        check(f"{fn.__name__}([1,2,3])", fn([1, 2, 3]), 9)

    # Exercise 4
    print("\nExercise 4: K Closest Points")
    for fn in [k_closest, _sol_k_closest]:
        if fn is k_closest and fn([(0, 0)], 1) is None:
            print("  (skipped — not implemented)")
            break
        result = fn([(1, 3), (-2, 2), (5, 8), (0, 1)], 2)
        dists = sorted(x * x + y * y for x, y in result)
        check(f"{fn.__name__} distances", dists, [1, 8])

    # Exercise 5
    print("\nExercise 5: IPO")
    for fn in [find_maximized_capital, _sol_find_maximized_capital]:
        if fn is find_maximized_capital and fn(1, 0, [1], [0]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}(k=2, W=0)", fn(2, 0, [1, 2, 3], [0, 1, 1]), 4)
        check(f"{fn.__name__}(k=1, W=0)", fn(1, 0, [1, 2, 3], [0, 1, 2]), 1)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
