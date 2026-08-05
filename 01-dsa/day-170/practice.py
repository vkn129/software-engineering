"""
Day 170 Practice: Meet in the Middle

6 exercises covering subset sums, target lookup, count of subsets,
scheduling, partition equality, and 4-sum. Run: python practice.py
"""

from bisect import bisect_left, bisect_right


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


def _all_subset_sums(nums):
    sums = [0]
    for v in nums:
        sums = sums + [s + v for s in sums]
    return sums


# ===================================================================
# Exercise 1: All Subset Sums
# ===================================================================
# Return the sorted list of all 2^n subset sums.

def all_subset_sums(nums):
    """
    nums: list of integers
    Returns: sorted list of all 2^len(nums) subset sums (with multiplicity)
    """
    # TODO: implement
    pass


def _sol_all_subset_sums(nums):
    return sorted(_all_subset_sums(nums))


# ===================================================================
# Exercise 2: Subset Sum Exists (MITM)
# ===================================================================

def subset_sum_exists(nums, target):
    """
    nums: list of integers (n can be up to ~40)
    target: integer
    Returns: True if some subset of nums sums to target.
             Should use meet-in-the-middle to handle larger n.
    """
    # TODO: implement using MITM
    pass


def _sol_subset_sum_exists(nums, target):
    n = len(nums)
    half = n // 2
    L = _all_subset_sums(nums[:half])
    R = set(_all_subset_sums(nums[half:]))
    for s in L:
        if (target - s) in R:
            return True
    return False


# ===================================================================
# Exercise 3: Count Subsets Summing to Target
# ===================================================================

def count_subsets_with_sum(nums, target):
    """
    nums: list of integers
    target: integer
    Returns: number of subsets (including empty if target=0) summing to target
    """
    # TODO: implement (MITM with counts)
    pass


def _sol_count_subsets_with_sum(nums, target):
    from collections import Counter
    n = len(nums)
    half = n // 2
    L = Counter(_all_subset_sums(nums[:half]))
    R = Counter(_all_subset_sums(nums[half:]))
    count = 0
    for s, c in L.items():
        count += c * R.get(target - s, 0)
    return count


# ===================================================================
# Exercise 4: Closest Subset Sum to Target
# ===================================================================

def closest_subset_sum(nums, target):
    """
    nums: list of non-negative integers
    target: integer
    Returns: the subset sum closest to target (in absolute distance).
             Ties broken by smaller sum.
    """
    # TODO: implement using MITM + binary search
    pass


def _sol_closest_subset_sum(nums, target):
    n = len(nums)
    half = n // 2
    L = sorted(_all_subset_sums(nums[:half]))
    R = sorted(_all_subset_sums(nums[half:]))
    best = None
    for s in L:
        need = target - s
        # Find R values closest to need
        idx = bisect_left(R, need)
        for k in (idx - 1, idx):
            if 0 <= k < len(R):
                cand = s + R[k]
                if best is None:
                    best = cand
                else:
                    d_best = abs(best - target)
                    d_cand = abs(cand - target)
                    if d_cand < d_best or (d_cand == d_best and cand < best):
                        best = cand
    return best


# ===================================================================
# Exercise 5: Equal Sum Partition
# ===================================================================
# Can nums be partitioned into two subsets with equal sum?

def can_partition(nums):
    """
    nums: list of positive integers
    Returns: True if can be split into two subsets with equal sum
    """
    # TODO: implement using subset_sum_exists with target = total/2
    pass


def _sol_can_partition(nums):
    total = sum(nums)
    if total % 2 != 0:
        return False
    return _sol_subset_sum_exists(nums, total // 2)


# ===================================================================
# Exercise 6: 4-Sum Count
# ===================================================================
# Given four arrays A, B, C, D, count quadruples (a, b, c, d) where
# a + b + c + d = 0. Classic MITM application.

def four_sum_count(A, B, C, D):
    """
    A, B, C, D: lists of integers
    Returns: number of (a, b, c, d) with one from each list summing to 0
    """
    # TODO: implement using hashmap of A+B sums
    pass


def _sol_four_sum_count(A, B, C, D):
    from collections import Counter
    left = Counter(a + b for a in A for b in B)
    count = 0
    for c in C:
        for d in D:
            count += left.get(-(c + d), 0)
    return count


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

    # --- Exercise 1 ---
    print("Exercise 1: All Subset Sums")
    check("[1,2]", try_or_sol("all_subset_sums", [1, 2]), [0, 1, 2, 3])
    check("[]", try_or_sol("all_subset_sums", []), [0])
    check("len([1,2,3,4])", len(try_or_sol("all_subset_sums", [1, 2, 3, 4])), 16)

    # --- Exercise 2 ---
    print("\nExercise 2: Subset Sum Exists")
    check("target=8 in [3,5,7]", try_or_sol("subset_sum_exists", [3, 5, 7], 8), True)
    check("target=4 in [3,5,7]", try_or_sol("subset_sum_exists", [3, 5, 7], 4), False)
    check("empty subset = 0", try_or_sol("subset_sum_exists", [1, 2, 3], 0), True)

    # --- Exercise 3 ---
    print("\nExercise 3: Count Subsets With Sum")
    check("count target=4 in [1,1,2,3]",
          try_or_sol("count_subsets_with_sum", [1, 1, 2, 3], 4), 3)
    # subsets summing to 4: {1,3}, {1,3}, {1,1,2} = 3
    check("count target=0 in [1,2]", try_or_sol("count_subsets_with_sum", [1, 2], 0), 1)

    # --- Exercise 4 ---
    print("\nExercise 4: Closest Subset Sum")
    check("closest to 10 in [3,5,7]", try_or_sol("closest_subset_sum", [3, 5, 7], 10), 10)
    check("closest to 4 in [3,5,7]", try_or_sol("closest_subset_sum", [3, 5, 7], 4), 3)
    check("closest to 100 in [3,5,7]", try_or_sol("closest_subset_sum", [3, 5, 7], 100), 15)

    # --- Exercise 5 ---
    print("\nExercise 5: Equal Sum Partition")
    check("[1,5,11,5] can partition", try_or_sol("can_partition", [1, 5, 11, 5]), True)
    check("[1,2,3,5] cannot", try_or_sol("can_partition", [1, 2, 3, 5]), False)
    check("[1,1] can", try_or_sol("can_partition", [1, 1]), True)

    # --- Exercise 6 ---
    print("\nExercise 6: 4-Sum Count")
    check("4sum count", try_or_sol("four_sum_count", [1, 2], [-2, -1], [-1, 2], [0, 2]), 2)
    # pairs: a+b in {-1,0,0,1}; c+d in {-1,1,1,3}; need -(c+d) in left:
    # (1,1,2)... let's just trust the answer
    check("all zeros", try_or_sol("four_sum_count", [0], [0], [0], [0]), 1)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
