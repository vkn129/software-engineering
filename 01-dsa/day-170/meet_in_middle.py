"""
Day 170: Meet in the Middle — From Scratch

Split 2^n search into two halves of 2^(n/2). Combine via sort + binary search.
Applied to subset sum and a scheduling/knapsack variant.

Time: O(2^(n/2) * n)   Space: O(2^(n/2))
"""

import time
import random
from bisect import bisect_right


# ---------------------------------------------------------------------------
# 1. Subset sum — brute force O(2^n)
# ---------------------------------------------------------------------------

def subset_sum_brute(nums, target):
    """Return True if any subset of nums sums to target. O(2^n) time."""
    n = len(nums)
    for mask in range(1 << n):
        s = 0
        for i in range(n):
            if mask >> i & 1:
                s += nums[i]
        if s == target:
            return True
    return False


# ---------------------------------------------------------------------------
# 2. Subset sum — meet in the middle, O(2^(n/2))
# ---------------------------------------------------------------------------

def _all_subset_sums(nums):
    """Return sorted list of all 2^len(nums) subset sums."""
    sums = [0]
    for v in nums:
        sums = sums + [s + v for s in sums]
    sums.sort()
    return sums


def subset_sum_mitm(nums, target):
    """Return True if any subset sums to target. O(2^(n/2) * n)."""
    n = len(nums)
    half = n // 2
    left_sums = _all_subset_sums(nums[:half])
    right_sums = _all_subset_sums(nums[half:])
    right_set = set(right_sums)
    for s in left_sums:
        if (target - s) in right_set:
            return True
    return False


def subset_sum_mitm_reconstruct(nums, target):
    """
    Return a subset of nums (as a list) that sums to target, or None.
    Uses MITM with explicit mask tracking.
    """
    n = len(nums)
    half = n // 2
    left, right = nums[:half], nums[half:]

    def enumerate_subsets(arr):
        # Returns dict sum -> mask (one canonical mask per sum)
        result = {0: 0}
        for i, v in enumerate(arr):
            new_items = {}
            for s, m in result.items():
                ns = s + v
                if ns not in result and ns not in new_items:
                    new_items[ns] = m | (1 << i)
            result.update(new_items)
        return result

    L = enumerate_subsets(left)
    R = enumerate_subsets(right)
    for s_l, m_l in L.items():
        need = target - s_l
        if need in R:
            m_r = R[need]
            subset = []
            for i in range(len(left)):
                if m_l >> i & 1:
                    subset.append(left[i])
            for i in range(len(right)):
                if m_r >> i & 1:
                    subset.append(right[i])
            return subset
    return None


# ---------------------------------------------------------------------------
# 3. Scheduling: max value subset under time budget (0/1 knapsack via MITM)
# ---------------------------------------------------------------------------

def _enumerate_pareto(jobs):
    """
    Enumerate (time, value) for all 2^k subsets, return Pareto frontier
    sorted by time, with running-max value.
    """
    pts = [(0, 0)]
    for t, v in jobs:
        pts = pts + [(pt + t, pv + v) for pt, pv in pts]
    pts.sort()
    # Build Pareto: for ties in time, keep max value; then running max
    pruned = []
    best = -1
    for t, v in pts:
        if pruned and pruned[-1][0] == t:
            if v > pruned[-1][1]:
                pruned[-1] = (t, v)
        else:
            pruned.append((t, v))
    running = []
    best = -1
    for t, v in pruned:
        if v > best:
            best = v
            running.append((t, best))
        else:
            running.append((t, best))
    return running


def max_value_schedule(jobs, deadline):
    """
    Pick a subset of jobs (each (time, value)) with total time <= deadline,
    maximizing total value. Returns the max value.

    Uses meet in the middle: O(2^(n/2) * n) time, O(2^(n/2)) space.
    """
    n = len(jobs)
    half = n // 2
    L = _enumerate_pareto(jobs[:half])
    R = _enumerate_pareto(jobs[half:])
    # For right half, build separate sorted-by-time array for binary search
    times_R = [t for t, _ in R]

    best = 0
    for tL, vL in L:
        if tL > deadline:
            continue
        budget = deadline - tL
        # Largest index with times_R[i] <= budget
        idx = bisect_right(times_R, budget) - 1
        if idx >= 0:
            total = vL + R[idx][1]
            if total > best:
                best = total
    return best


def max_value_schedule_brute(jobs, deadline):
    """Reference O(2^n) implementation."""
    n = len(jobs)
    best = 0
    for mask in range(1 << n):
        t = v = 0
        for i in range(n):
            if mask >> i & 1:
                t += jobs[i][0]
                v += jobs[i][1]
        if t <= deadline and v > best:
            best = v
    return best


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_subset_sum():
    print("=" * 60)
    print("DEMO 1: Subset Sum — Brute vs MITM")
    print("=" * 60)
    random.seed(7)
    n = 24
    nums = [random.randint(1, 100) for _ in range(n)]
    target = sum(random.sample(nums, n // 3))

    t1 = time.perf_counter()
    a = subset_sum_brute(nums, target)
    bt = time.perf_counter() - t1

    t1 = time.perf_counter()
    b = subset_sum_mitm(nums, target)
    mt = time.perf_counter() - t1

    print(f"  n={n}, target={target}")
    print(f"    Brute force: {a}  in {bt:.3f}s")
    print(f"    MITM:        {b}  in {mt:.3f}s")
    print(f"    Speedup:     {bt/mt:.1f}x")


def demo_subset_reconstruct():
    print("\n" + "=" * 60)
    print("DEMO 2: Subset Sum Reconstruction")
    print("=" * 60)
    nums = [3, 5, 7, 2, 1, 9, 11, 4]
    target = 19
    sub = subset_sum_mitm_reconstruct(nums, target)
    print(f"  nums={nums}, target={target}")
    print(f"  subset = {sub}, sum = {sum(sub) if sub else None}")


def demo_schedule():
    print("\n" + "=" * 60)
    print("DEMO 3: Scheduling Problem (Knapsack via MITM)")
    print("=" * 60)
    random.seed(42)
    n = 30
    jobs = [(random.randint(1, 10**6), random.randint(1, 1000))
            for _ in range(n)]
    # Use big deadline so it's interesting
    deadline = sum(t for t, _ in jobs) // 2

    t1 = time.perf_counter()
    val_mitm = max_value_schedule(jobs, deadline)
    mt = time.perf_counter() - t1

    # Verify against brute force on smaller subset
    small_jobs = jobs[:18]
    small_deadline = sum(t for t, _ in small_jobs) // 2

    t1 = time.perf_counter()
    val_brute = max_value_schedule_brute(small_jobs, small_deadline)
    bt = time.perf_counter() - t1

    t1 = time.perf_counter()
    val_check = max_value_schedule(small_jobs, small_deadline)
    ct = time.perf_counter() - t1

    print(f"  Large: n={n}, MITM best value = {val_mitm} in {mt:.3f}s")
    print(f"  Small: n=18, brute={val_brute} ({bt:.3f}s), "
          f"MITM={val_check} ({ct:.3f}s) — match: {val_brute == val_check}")


if __name__ == "__main__":
    demo_subset_sum()
    demo_subset_reconstruct()
    demo_schedule()
