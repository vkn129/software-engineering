"""
Day 119 Practice: Subset-Sum, Partition & Bounded Knapsack

6 exercises. Implement TODOs, then run: python practice.py
"""

from itertools import product


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: Subset-sum existence
# ---------------------------------------------------------------------------

def subset_sum_exists(nums, target):
    """True iff some subset of non-negative ints `nums` sums to exactly target."""
    # TODO: implement with a 1D reach[] table; watch the loop DIRECTION
    pass


def _sol_subset_sum_exists(nums, target):
    if target < 0:
        return False
    reach = [False] * (target + 1)
    reach[0] = True
    for x in nums:
        if x > target:
            continue
        # Downward: reach[s - x] must still mean "before x was offered",
        # otherwise x gets reused and this becomes unbounded knapsack.
        for s in range(target, x - 1, -1):
            if reach[s - x]:
                reach[s] = True
    return reach[target]


# ---------------------------------------------------------------------------
# Exercise 2: Binary splitting of a multiplicity
# ---------------------------------------------------------------------------

def binary_split_counts(m):
    """
    Split multiplicity m into packages whose subset sums are EXACTLY 0..m.
    Return the package sizes in ascending-power order, remainder last.
    binary_split_counts(5) -> [1, 2, 2]
    """
    # TODO: implement; the parts must sum to exactly m
    pass


def _sol_binary_split_counts(m):
    parts = []
    k = 1
    while k <= m:
        parts.append(k)
        m -= k       # subtracting keeps the running total at exactly m
        k *= 2
    if m > 0:        # a zero remainder is not a package
        parts.append(m)
    return parts


def _reachable(parts):
    """Every subset total of `parts`. Used by the tests to prove exactness."""
    reach = {0}
    for p in parts:
        reach |= {r + p for r in reach}
    return reach


# ---------------------------------------------------------------------------
# Exercise 3: Equal-sum partition
# ---------------------------------------------------------------------------

def can_partition_equal_sum(nums):
    """True iff nums splits into two groups with the same sum."""
    # TODO: parity check first, then reuse the subset-sum table
    pass


def _sol_can_partition_equal_sum(nums):
    total = sum(nums)
    if total % 2:
        return False  # an odd total can never split into two equal integer sums
    return _sol_subset_sum_exists(nums, total // 2)


# ---------------------------------------------------------------------------
# Exercise 4: Minimum subset-sum difference
# ---------------------------------------------------------------------------

def min_subset_sum_difference(nums):
    """Minimum |sum(A) - sum(B)| over all 2-way splits of nums."""
    # TODO: find the largest reachable sum <= total // 2
    pass


def _sol_min_subset_sum_difference(nums):
    total = sum(nums)
    half = total // 2
    reach = [False] * (half + 1)
    reach[0] = True
    for x in nums:
        if x > half:
            continue
        for s in range(half, x - 1, -1):
            if reach[s - x]:
                reach[s] = True
    for s in range(half, -1, -1):
        if reach[s]:
            # group A sums to s, group B to total - s
            return total - 2 * s
    return total


# ---------------------------------------------------------------------------
# Exercise 5: Count subsets with a given sum
# ---------------------------------------------------------------------------

def count_subsets_with_sum(nums, target):
    """Number of distinct index-subsets of nums summing to target."""
    # TODO: same table shape, but accumulate counts instead of booleans
    pass


def _sol_count_subsets_with_sum(nums, target):
    if target < 0:
        return 0
    ways = [0] * (target + 1)
    ways[0] = 1
    for x in nums:
        for s in range(target, x - 1, -1):
            ways[s] += ways[s - x]
    return ways[target]


# ---------------------------------------------------------------------------
# Exercise 6: Bounded knapsack via binary splitting
# ---------------------------------------------------------------------------

def bounded_knapsack(items, capacity):
    """
    items: list of (value, weight, count). Each item may be taken 0..count times.
    Return the maximum total value with total weight <= capacity.
    """
    # TODO: split each item into packages, then run one 0/1 pass
    pass


def _sol_bounded_knapsack(items, capacity):
    if capacity < 0:
        return 0
    pairs = []
    for value, weight, count in items:
        # A package of size c is "c copies bought together".
        for c in _sol_binary_split_counts(count):
            pairs.append((value * c, weight * c))
    dp = [0] * (capacity + 1)
    for value, weight in pairs:
        if weight > capacity:
            continue
        for w in range(capacity, weight - 1, -1):
            cand = dp[w - weight] + value
            if cand > dp[w]:
                dp[w] = cand
    return dp[capacity]


def _brute_bounded_knapsack(items, capacity):
    """Independent ground truth for tiny inputs."""
    best = 0
    for combo in product(*[range(c + 1) for _, _, c in items]):
        w = sum(c * items[i][1] for i, c in enumerate(combo))
        if w <= capacity:
            v = sum(c * items[i][0] for i, c in enumerate(combo))
            best = max(best, v)
    return best


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: subset_sum_exists")
    nums = [3, 34, 4, 12, 5, 2]
    check("target 9", try_or_sol("subset_sum_exists", nums, 9), True)
    check("target 30", try_or_sol("subset_sum_exists", nums, 30), False)
    check("target 0 always reachable", try_or_sol("subset_sum_exists", nums, 0), True)
    # Downward-vs-upward loop check: with [2] only 0 and 2 are reachable.
    # An upward loop would wrongly report 4 (reusing the single 2).
    check("no item reuse", try_or_sol("subset_sum_exists", [2], 4), False)

    print("\nExercise 2: binary_split_counts")
    check("m=5", try_or_sol("binary_split_counts", 5), [1, 2, 2])
    check("m=7 (no remainder)", try_or_sol("binary_split_counts", 7), [1, 2, 4])
    check("m=0", try_or_sol("binary_split_counts", 0), [])
    # The property that actually matters: reachable totals are EXACTLY 0..m.
    exact_all = True
    sums_all = True
    for m in range(0, 40):
        parts = try_or_sol("binary_split_counts", m)
        if _reachable(parts) != set(range(m + 1)):
            exact_all = False
        if sum(parts) != m:
            sums_all = False
    check("reaches exactly 0..m for m<40", exact_all, True)
    check("parts sum to exactly m (no extra copy)", sums_all, True)

    print("\nExercise 3: can_partition_equal_sum")
    check("[1,5,11,5]", try_or_sol("can_partition_equal_sum", [1, 5, 11, 5]), True)
    check("[1,2,3,5] odd total", try_or_sol("can_partition_equal_sum", [1, 2, 3, 5]), False)
    check("[2,2,2,2]", try_or_sol("can_partition_equal_sum", [2, 2, 2, 2]), True)
    check("[1,1,1] odd total", try_or_sol("can_partition_equal_sum", [1, 1, 1]), False)

    print("\nExercise 4: min_subset_sum_difference")
    check("[1,6,11,5]", try_or_sol("min_subset_sum_difference", [1, 6, 11, 5]), 1)
    check("[1,5,11,5] splits evenly",
          try_or_sol("min_subset_sum_difference", [1, 5, 11, 5]), 0)
    check("[10] alone", try_or_sol("min_subset_sum_difference", [10]), 10)
    check("[3,1,4,2,2,1]", try_or_sol("min_subset_sum_difference", [3, 1, 4, 2, 2, 1]), 1)

    print("\nExercise 5: count_subsets_with_sum")
    check("[1,1,2,3] -> 3", try_or_sol("count_subsets_with_sum", [1, 1, 2, 3], 3), 3)
    check("[2,3,5,6,8,10] -> 10",
          try_or_sol("count_subsets_with_sum", [2, 3, 5, 6, 8, 10], 10), 3)
    check("empty target 0", try_or_sol("count_subsets_with_sum", [], 0), 1)
    # A zero doubles every count: {} and {0} are different index-subsets.
    check("zero doubles counts", try_or_sol("count_subsets_with_sum", [0, 3], 3), 2)

    print("\nExercise 6: bounded_knapsack")
    items = [(10, 1, 3), (7, 2, 2), (25, 5, 1)]
    check("capacity 3", try_or_sol("bounded_knapsack", items, 3), 30)
    check("capacity 6", try_or_sol("bounded_knapsack", items, 6), 37)
    check("capacity 10", try_or_sol("bounded_knapsack", items, 10), 62)
    # Capacity far exceeds what the counts allow: the answer must cap at
    # 3 copies (value 30), never 4. This is the off-by-one that binary
    # splitting has to get right.
    check("count is a hard ceiling", try_or_sol("bounded_knapsack", [(10, 1, 3)], 10), 30)
    # Cross-check against exhaustive search on a small instance.
    small = [(4, 3, 2), (5, 4, 3), (9, 7, 1)]
    agree = all(
        try_or_sol("bounded_knapsack", small, cap) == _brute_bounded_knapsack(small, cap)
        for cap in range(0, 20)
    )
    check("matches brute force for cap 0..19", agree, True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
