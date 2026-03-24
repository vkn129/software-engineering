"""
Day 58 Practice: Fenwick Tree Exercises
========================================
Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from fenwick_tree import FenwickTree, FenwickTree2D


# ─── Exercise 1: Count Inversions ─────────────────────────────────
#
# An inversion is a pair (i, j) where i < j but arr[i] > arr[j].
# Count inversions using a Fenwick tree.
#
# Approach:
#   1. Coordinate compress values to [0, m)
#   2. Process left to right; for each element with rank r,
#      inversions += (elements inserted so far) - prefix_sum(r)
#   3. Then insert r into the BIT
#
# Example: [2, 4, 1, 3, 5] → 3 inversions: (2,1), (4,1), (4,3)

def count_inversions(arr):
    # TODO: return the number of inversions
    pass


# ─── Exercise 2: Range Update + Point Query ──────────────────────
#
# Support two operations on an array of zeros:
#   range_add(l, r, val): add val to every element in [l..r]
#   point_query(i): return current value at index i
#
# Trick: maintain a Fenwick tree over the DIFFERENCE array.
#   range_add(l, r, val) → BIT.update(l, +val), BIT.update(r+1, -val)
#   point_query(i) → BIT.prefix_sum(i)
#
# Example:
#   n=5, range_add(1, 3, 10), range_add(2, 4, 5)
#   point_query(0)=0, point_query(2)=15, point_query(4)=5

class RangeUpdatePointQuery:
    def __init__(self, n):
        # TODO: initialize
        self.n = n

    def range_add(self, l, r, val):
        # TODO: add val to all positions in [l..r] (0-indexed)
        pass

    def point_query(self, i):
        # TODO: return value at position i (0-indexed)
        pass


# ─── Exercise 3: Count Elements Less Than X in Range ─────────────
#
# Given an array, answer offline queries of the form:
#   "How many elements in arr[l..r] are strictly less than x?"
#
# Approach (offline with coordinate compression):
#   1. Compress all values + query x's to ranks
#   2. Sort queries by x
#   3. Process: insert array elements with value < current x threshold
#      into a BIT keyed by position, then answer count via range sum
#
# Example:
#   arr = [3, 1, 4, 1, 5]
#   query(0, 4, 3) → 2  (elements 1, 1 are < 3)
#   query(2, 4, 5) → 1  (element 1 at index 3 is < 5... wait, also 4)
#                    → 2  (elements 4, 1 at indices 2,3 — but 4 < 5 and 1 < 5)

def count_less_than(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r, x) tuples, 0-indexed
    returns: list of answers, one per query
    """
    # TODO: return list of counts
    pass


# ─── Exercise 4: 2D Range Sum Queries ────────────────────────────
#
# Given a matrix, support:
#   update(r, c, val): set matrix[r][c] to val
#   range_sum(r1, c1, r2, c2): sum of submatrix
#
# Use a 2D Fenwick tree. Update uses delta = new_val - old_val.
#
# Example:
#   matrix = [[1,2],[3,4]]
#   range_sum(0,0,1,1) → 10
#   update(0,0,5)  (was 1, delta = +4)
#   range_sum(0,0,1,1) → 14

class Matrix2D:
    def __init__(self, matrix):
        # TODO: initialize from matrix (list of lists)
        pass

    def update(self, r, c, val):
        # TODO: set position (r,c) to val
        pass

    def range_sum(self, r1, c1, r2, c2):
        # TODO: sum of submatrix [(r1,c1)..(r2,c2)]
        pass


# ─── Exercise 5: K-th Smallest Element ───────────────────────────
#
# Maintain a multiset of integers supporting:
#   insert(val): add val to the set
#   kth_smallest(k): return the k-th smallest element (1-indexed)
#
# Approach: Fenwick tree as frequency array + binary search on prefix sums.
# To find k-th smallest: find smallest index i where prefix_sum(i) >= k.
# Can do this in O(log^2 n) with binary search on prefix_sum,
# or O(log n) by walking the BIT structure directly.
#
# Example:
#   insert(3), insert(1), insert(4), insert(1)
#   kth_smallest(1) → 1
#   kth_smallest(3) → 3
#   kth_smallest(4) → 4

class OrderStatistic:
    def __init__(self, max_val):
        """max_val: maximum value that can be inserted (values in [0, max_val])."""
        # TODO: initialize
        pass

    def insert(self, val):
        # TODO: insert val into the multiset
        pass

    def kth_smallest(self, k):
        # TODO: return k-th smallest element (1-indexed)
        pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_count_inversions(arr):
    if not arr:
        return 0
    sorted_unique = sorted(set(arr))
    rank = {v: i for i, v in enumerate(sorted_unique)}
    m = len(sorted_unique)
    bit = FenwickTree(m)
    inversions = 0
    for val in arr:
        r = rank[val]
        total_inserted = bit.prefix_sum(m - 1)
        leq = bit.prefix_sum(r)
        inversions += total_inserted - leq
        bit.update(r, 1)
    return inversions


class _SolRangeUpdatePointQuery:
    def __init__(self, n):
        self.n = n
        self.bit = FenwickTree(n)

    def range_add(self, l, r, val):
        self.bit.update(l, val)
        if r + 1 < self.n:
            self.bit.update(r + 1, -val)

    def point_query(self, i):
        return self.bit.prefix_sum(i)


def _sol_count_less_than(arr, queries):
    if not arr or not queries:
        return [0] * len(queries)

    n = len(arr)
    # Pair each element with its index: (value, index)
    elements = sorted((arr[i], i) for i in range(n))

    # Attach original query index for output ordering
    # (x, l, r, original_index)
    indexed_queries = sorted((x, l, r, qi) for qi, (l, r, x) in enumerate(queries))

    answers = [0] * len(queries)
    bit = FenwickTree(n)
    ei = 0  # pointer into sorted elements

    for x, l, r, qi in indexed_queries:
        # Insert all elements with value < x
        while ei < n and elements[ei][0] < x:
            bit.update(elements[ei][1], 1)
            ei += 1
        answers[qi] = bit.range_sum(l, r)

    return answers


class _SolMatrix2D:
    def __init__(self, matrix):
        self.R = len(matrix)
        self.C = len(matrix[0]) if self.R > 0 else 0
        self.data = [row[:] for row in matrix]
        self.bit = FenwickTree2D(self.R, self.C)
        for r in range(self.R):
            for c in range(self.C):
                self.bit.update(r, c, matrix[r][c])

    def update(self, r, c, val):
        delta = val - self.data[r][c]
        self.data[r][c] = val
        self.bit.update(r, c, delta)

    def range_sum(self, r1, c1, r2, c2):
        return self.bit.range_sum(r1, c1, r2, c2)


class _SolOrderStatistic:
    def __init__(self, max_val):
        self.max_val = max_val
        self.bit = FenwickTree(max_val + 1)

    def insert(self, val):
        self.bit.update(val, 1)

    def kth_smallest(self, k):
        # Binary search: find smallest i where prefix_sum(i) >= k
        lo, hi = 0, self.max_val
        while lo < hi:
            mid = (lo + hi) // 2
            if self.bit.prefix_sum(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0
    skipped = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  \u2713 {name}")
        else:
            failed += 1
            print(f"  \u2717 {name}: got {got}, expected {expected}")

    # Exercise 1: Count Inversions
    print("\nExercise 1: Count Inversions")
    user_result = count_inversions([2, 4, 1, 3, 5])
    if user_result is None:
        print("  \u2b1c Not implemented yet")
        skipped += 1
    else:
        check("inversions([2,4,1,3,5])", user_result, 3)
        check("inversions([5,4,3,2,1])", count_inversions([5, 4, 3, 2, 1]), 10)
        check("inversions([1,2,3])", count_inversions([1, 2, 3]), 0)
        check("inversions([])", count_inversions([]), 0)
    # Solution verification
    check("sol_inversions([2,4,1,3,5])", _sol_count_inversions([2, 4, 1, 3, 5]), 3)
    check("sol_inversions([5,4,3,2,1])", _sol_count_inversions([5, 4, 3, 2, 1]), 10)

    # Exercise 2: Range Update + Point Query
    print("\nExercise 2: Range Update + Point Query")
    rup = RangeUpdatePointQuery(5)
    test_result = rup.point_query(0) if hasattr(rup, 'point_query') else None
    if test_result is None:
        print("  \u2b1c Not implemented yet")
        skipped += 1
    else:
        rup.range_add(1, 3, 10)
        rup.range_add(2, 4, 5)
        check("point_query(0)", rup.point_query(0), 0)
        check("point_query(1)", rup.point_query(1), 10)
        check("point_query(2)", rup.point_query(2), 15)
        check("point_query(3)", rup.point_query(3), 15)
        check("point_query(4)", rup.point_query(4), 5)
    # Solution verification
    sol_rup = _SolRangeUpdatePointQuery(5)
    sol_rup.range_add(1, 3, 10)
    sol_rup.range_add(2, 4, 5)
    check("sol_point_query(2)", sol_rup.point_query(2), 15)
    check("sol_point_query(4)", sol_rup.point_query(4), 5)

    # Exercise 3: Count Less Than
    print("\nExercise 3: Count Elements Less Than X")
    arr3 = [3, 1, 4, 1, 5]
    queries3 = [(0, 4, 3), (2, 4, 5), (0, 1, 2)]
    user_result = count_less_than(arr3, queries3)
    if user_result is None:
        print("  \u2b1c Not implemented yet")
        skipped += 1
    else:
        check("count_less(0,4,3)", user_result[0], 2)  # 1,1 are < 3
        check("count_less(2,4,5)", user_result[1], 2)  # 4,1 are < 5
        check("count_less(0,1,2)", user_result[2], 1)  # 1 is < 2
    # Solution verification
    sol_result = _sol_count_less_than(arr3, queries3)
    check("sol_count_less(0,4,3)", sol_result[0], 2)
    check("sol_count_less(2,4,5)", sol_result[1], 2)
    check("sol_count_less(0,1,2)", sol_result[2], 1)

    # Exercise 4: 2D Range Sum
    print("\nExercise 4: 2D Range Sum Queries")
    matrix = [[1, 2], [3, 4]]
    try:
        m2d = Matrix2D(matrix)
        test_result = m2d.range_sum(0, 0, 1, 1)
    except Exception:
        test_result = None
    if test_result is None:
        print("  \u2b1c Not implemented yet")
        skipped += 1
    else:
        check("range_sum(0,0,1,1)", test_result, 10)
        m2d.update(0, 0, 5)
        check("after update(0,0,5) range_sum(0,0,1,1)", m2d.range_sum(0, 0, 1, 1), 14)
        check("range_sum(1,0,1,1)", m2d.range_sum(1, 0, 1, 1), 7)
    # Solution verification
    sol_m2d = _SolMatrix2D(matrix)
    check("sol_range_sum(0,0,1,1)", sol_m2d.range_sum(0, 0, 1, 1), 10)
    sol_m2d.update(0, 0, 5)
    check("sol_after_update range_sum(0,0,1,1)", sol_m2d.range_sum(0, 0, 1, 1), 14)

    # Exercise 5: K-th Smallest
    print("\nExercise 5: K-th Smallest Element")
    try:
        os_user = OrderStatistic(10)
        for v in [3, 1, 4, 1]:
            os_user.insert(v)
        test_result = os_user.kth_smallest(1)
    except Exception:
        test_result = None
    if test_result is None:
        print("  \u2b1c Not implemented yet")
        skipped += 1
    else:
        check("kth_smallest(1)", test_result, 1)
        check("kth_smallest(2)", os_user.kth_smallest(2), 1)
        check("kth_smallest(3)", os_user.kth_smallest(3), 3)
        check("kth_smallest(4)", os_user.kth_smallest(4), 4)
    # Solution verification
    sol_os = _SolOrderStatistic(10)
    for v in [3, 1, 4, 1]:
        sol_os.insert(v)
    check("sol_kth_smallest(1)", sol_os.kth_smallest(1), 1)
    check("sol_kth_smallest(3)", sol_os.kth_smallest(3), 3)
    check("sol_kth_smallest(4)", sol_os.kth_smallest(4), 4)

    print(f"\n{'=' * 40}")
    total = passed + failed
    print(f"Results: {passed} passed, {failed} failed, {skipped} not implemented")
    if skipped > 0:
        print(f"\nHint: {skipped} exercises still need your implementation!")


if __name__ == "__main__":
    run_tests()
