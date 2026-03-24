"""
Day 19 Practice: Prefix Sums & Difference Arrays
==================================================

These exercises apply prefix sums and difference arrays to solve classic
array problems in O(n) time. The core insight: prefix sums are discrete
integrals, difference arrays are discrete derivatives, and they are inverses.

Fill in the TODO sections. Run this file to check your answers.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Subarray Sum Equals K
# =============================================================================

def subarray_sum_k(arr, k):
    """Count the number of contiguous subarrays that sum to exactly k.

    Brute force is O(n^2) -- check every (i, j) pair. We do O(n) using
    prefix sums and a hash map.

    Key insight: if prefix[j] - prefix[i] == k, then arr[i..j-1] sums to k.
    Rearranging: prefix[i] == prefix[j] - k. So for each j, we need to know
    how many earlier prefix sums equal prefix[j] - k.

    This is the same idea behind two-sum: instead of checking all pairs,
    store what you have seen and query for the complement.

    Args:
        arr: list of integers (can be negative)
        k: target sum

    Returns:
        dict with:
        - 'count': number of subarrays summing to k
        - 'prefix_sums': the prefix sum array (for debugging)

    TODO: Implement using prefix sums and a hash map (dict).
    """
    # TODO: Initialize prefix sum and a dict counting occurrences of each prefix sum
    # The dict starts with {0: 1} because an empty prefix has sum 0
    count = 0
    prefix_sum = 0
    prefix_counts = {}  # FIX THIS -- should start with {0: 1}
    prefix_sums = [0]

    for num in arr:
        # TODO: Update prefix_sum
        # TODO: Check how many times (prefix_sum - k) appeared before
        # TODO: Record current prefix_sum in the dict
        pass  # FIX THIS
        prefix_sums.append(prefix_sum)

    return {
        'count': count,
        'prefix_sums': prefix_sums,
    }


# =============================================================================
# Exercise 2: 2D Prefix Sum for Rectangle Queries
# =============================================================================

class PrefixSum2D:
    """Build a 2D prefix sum table for O(1) rectangle sum queries.

    The 2D prefix sum at (r, c) stores the sum of all elements in the
    rectangle from (0,0) to (r-1, c-1). We use 1-indexed prefix sums
    with a row and column of zeros as sentinels, same reason as 1D:
    it eliminates boundary special cases.

    Building uses inclusion-exclusion:
    prefix[r][c] = matrix[r-1][c-1] + prefix[r-1][c] + prefix[r][c-1] - prefix[r-1][c-1]
                   ^new cell          ^above           ^left             ^double-counted corner

    Querying a rectangle (r1,c1) to (r2,c2) inclusive:
    sum = prefix[r2+1][c2+1] - prefix[r1][c2+1] - prefix[r2+1][c1] + prefix[r1][c1]
    This is 2D inclusion-exclusion: total - top - left + corner (added back).
    """

    def __init__(self, matrix):
        """Build the 2D prefix sum table.

        TODO: Fill in the prefix table using the recurrence above.
        """
        if not matrix or not matrix[0]:
            self.prefix = [[0]]
            return

        rows = len(matrix)
        cols = len(matrix[0])
        # 1-indexed: prefix has (rows+1) x (cols+1) with row 0 and col 0 all zeros
        self.prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                # TODO: Compute prefix[r][c] using inclusion-exclusion
                self.prefix[r][c] = 0  # FIX THIS

    def query(self, r1, c1, r2, c2):
        """Return sum of matrix[r1..r2][c1..c2] inclusive.

        TODO: Implement using 2D inclusion-exclusion on the prefix table.
        """
        # TODO: Apply the query formula
        return 0  # FIX THIS


# =============================================================================
# Exercise 3: Difference Array for Range Increment Operations
# =============================================================================

def range_increment(n, operations):
    """Apply multiple range increment operations efficiently using a difference array.

    Naive approach: for each operation (l, r, val), iterate from l to r and
    add val. This is O(n * q) for q operations.

    Difference array approach: O(n + q).
    The difference array diff[i] = arr[i] - arr[i-1] (with diff[0] = arr[0]).
    A range increment of val on [l, r] only changes two difference values:
        diff[l] += val   (the increment starts here)
        diff[r+1] -= val (the increment stops after r)

    After all operations, reconstruct arr by taking prefix sums of diff.
    This works because adding val to diff[l] propagates forward through
    all prefix sums from index l onward, and subtracting at r+1 cancels it.

    Args:
        n: array length (initialized to all zeros)
        operations: list of (left, right, value) tuples, 0-indexed inclusive

    Returns:
        dict with:
        - 'result': the final array after all operations
        - 'diff_array': the difference array before reconstruction

    TODO: Implement using a difference array.
    """
    # TODO: Create difference array of size n+1 (extra slot for the r+1 cancellation)
    diff = [0] * (n + 1)

    for left, right, val in operations:
        # TODO: Apply the range update to the difference array
        pass  # FIX THIS

    # TODO: Reconstruct the result array by taking prefix sums of diff
    result = [0] * n
    # FIX THIS

    return {
        'result': result,
        'diff_array': diff[:n],  # trim the extra slot for display
    }


# =============================================================================
# Exercise 4: Equilibrium Index
# =============================================================================

def equilibrium_index(arr):
    """Find all indices where the left sum equals the right sum.

    An index i is an equilibrium index if:
        arr[0] + ... + arr[i-1] == arr[i+1] + ... + arr[n-1]

    The element at i itself is NOT included in either sum.

    Naive approach: for each i, compute left and right sums -> O(n^2).
    With prefix sums: O(n).

    Key insight: left_sum = prefix[i], right_sum = total - prefix[i] - arr[i].
    So equilibrium when prefix[i] == total - prefix[i] - arr[i],
    i.e., 2 * prefix[i] + arr[i] == total.

    Args:
        arr: list of integers

    Returns:
        dict with:
        - 'indices': list of equilibrium indices (sorted)
        - 'prefix_sums': the prefix sum array used

    TODO: Implement using prefix sums.
    """
    # TODO: Compute total sum and prefix sums, find equilibrium indices
    indices = []
    prefix_sums = []

    # FIX THIS

    return {
        'indices': indices,
        'prefix_sums': prefix_sums,
    }


# =============================================================================
# Reference Solutions (scroll down after attempting!)
# =============================================================================
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# SPOILER SPACE -- try the exercises before looking below!
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#


def _solution_1_subarray_sum(arr, k):
    count = 0
    prefix_sum = 0
    # {0: 1} because the empty prefix sums to 0 -- this handles subarrays
    # starting at index 0 that sum exactly to k.
    prefix_counts = {0: 1}
    prefix_sums = [0]

    for num in arr:
        prefix_sum += num
        # How many earlier prefixes have sum (prefix_sum - k)?
        # Each such prefix i means arr[i+1..current] sums to k.
        target = prefix_sum - k
        count += prefix_counts.get(target, 0)
        prefix_counts[prefix_sum] = prefix_counts.get(prefix_sum, 0) + 1
        prefix_sums.append(prefix_sum)

    return {
        'count': count,
        'prefix_sums': prefix_sums,
    }


class _SolutionPrefixSum2D:
    def __init__(self, matrix):
        if not matrix or not matrix[0]:
            self.prefix = [[0]]
            return

        rows = len(matrix)
        cols = len(matrix[0])
        self.prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                # Inclusion-exclusion: add top and left, subtract overlap, add new cell
                self.prefix[r][c] = (
                    matrix[r - 1][c - 1]
                    + self.prefix[r - 1][c]
                    + self.prefix[r][c - 1]
                    - self.prefix[r - 1][c - 1]
                )

    def query(self, r1, c1, r2, c2):
        # 2D inclusion-exclusion on prefix sums
        return (
            self.prefix[r2 + 1][c2 + 1]
            - self.prefix[r1][c2 + 1]
            - self.prefix[r2 + 1][c1]
            + self.prefix[r1][c1]
        )


def _solution_3_range_increment(n, operations):
    # The difference array encodes increments as deltas at boundaries.
    # This is the discrete derivative: applying all updates in O(q),
    # then integrating (prefix sum) to recover the array in O(n).
    diff = [0] * (n + 1)

    for left, right, val in operations:
        diff[left] += val
        if right + 1 <= n:
            diff[right + 1] -= val

    # Reconstruct by prefix sum (discrete integration)
    result = [0] * n
    running = 0
    for i in range(n):
        running += diff[i]
        result[i] = running

    return {
        'result': result,
        'diff_array': diff[:n],
    }


def _solution_4_equilibrium(arr):
    n = len(arr)
    total = sum(arr)

    # Build prefix sums: prefix[i] = sum of arr[0..i-1]
    prefix_sums = [0] * (n + 1)
    for i in range(n):
        prefix_sums[i + 1] = prefix_sums[i] + arr[i]

    indices = []
    for i in range(n):
        left_sum = prefix_sums[i]
        right_sum = total - prefix_sums[i + 1]
        if left_sum == right_sum:
            indices.append(i)

    return {
        'indices': indices,
        'prefix_sums': prefix_sums,
    }


# =============================================================================
# Self-check
# =============================================================================

def run_checks():
    print("=" * 70)
    print("DAY 19 PRACTICE -- Checking your solutions")
    print("=" * 70)

    # Exercise 1: Subarray Sum Equals K
    print("\n--- Exercise 1: Subarray Sum Equals K ---")
    # [1,1,1] with k=2: subarrays [1,1] at positions (0,1) and (1,2) -> count=2
    r1 = subarray_sum_k([1, 1, 1], 2)
    # [1,2,3,-1,2] with k=4: [1,2,3,-1,2] has subarrays [1,3], [2,3,-1], etc.
    r2 = subarray_sum_k([1, 2, 3, -1, 2], 4)
    # [3,4,7,2,-3,1,4,2] with k=7: multiple subarrays
    r3 = subarray_sum_k([3, 4, 7, 2, -3, 1, 4, 2], 7)

    if r1['count'] == 0 and r2['count'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        checks = [
            (r1['count'], 2, "[1,1,1], k=2"),
            (r2['count'], 3, "[1,2,3,-1,2], k=4"),
            (r3['count'], 4, "[3,4,7,2,-3,1,4,2], k=7"),
        ]
        all_pass = True
        for got, expected, desc in checks:
            status = "PASS" if got == expected else "FAIL"
            if got != expected:
                all_pass = False
            print(f"  {status}: {desc} -> count={got} (expected {expected})")
        if all_pass:
            print("  All subarray sum tests passed!")

    # Exercise 2: 2D Prefix Sum
    print("\n--- Exercise 2: 2D Prefix Sum ---")
    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]
    ps2d = PrefixSum2D(matrix)
    # Full matrix sum: 1+2+...+12 = 78
    q1 = ps2d.query(0, 0, 2, 3)
    # Top-left 2x2: 1+2+5+6 = 14
    q2 = ps2d.query(0, 0, 1, 1)
    # Bottom-right 2x2: 7+8+11+12 = 38
    q3 = ps2d.query(1, 2, 2, 3)
    # Middle element: 6
    q4 = ps2d.query(1, 1, 1, 1)

    if q1 == 0 and q2 == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        checks = [
            (q1, 78, "full matrix"),
            (q2, 14, "top-left 2x2"),
            (q3, 38, "bottom-right 2x2"),
            (q4, 6, "single element (1,1)"),
        ]
        all_pass = True
        for got, expected, desc in checks:
            status = "PASS" if got == expected else "FAIL"
            if got != expected:
                all_pass = False
            print(f"  {status}: {desc} = {got} (expected {expected})")
        if all_pass:
            print("  All 2D prefix sum queries passed!")

    # Exercise 3: Difference Array
    print("\n--- Exercise 3: Difference Array Range Increments ---")
    # Array of size 6, apply several range increments
    ops = [
        (1, 3, 10),   # add 10 to indices 1-3
        (2, 5, 5),    # add 5 to indices 2-5
        (0, 2, -3),   # add -3 to indices 0-2
    ]
    # Expected result: [-3, 7, 12, 15, 5, 5]
    # Index 0: -3
    # Index 1: 10 + (-3) = 7
    # Index 2: 10 + 5 + (-3) = 12
    # Index 3: 10 + 5 = 15
    # Index 4: 5
    # Index 5: 5
    result = range_increment(6, ops)
    expected_arr = [-3, 7, 12, 15, 5, 5]
    if result['result'] == [0] * 6:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  Result: {result['result']}")
        print(f"  Expected: {expected_arr}")
        if result['result'] == expected_arr:
            print("  PASS: Difference array range increments correct!")
        else:
            print("  FAIL: Check your difference array logic.")

    # Exercise 4: Equilibrium Index
    print("\n--- Exercise 4: Equilibrium Index ---")
    # [-7, 1, 5, 2, -4, 3, 0] -> index 3: left=(-7+1+5)=-1, right=(-4+3+0)=-1
    r1 = equilibrium_index([-7, 1, 5, 2, -4, 3, 0])
    # [1, 2, 3] -> no equilibrium
    r2 = equilibrium_index([1, 2, 3])
    # [0, 0, 0, 0] -> all indices are equilibrium (left=right=0 for edges)
    r3 = equilibrium_index([0, 0, 0, 0])
    # [1, -1, 1, -1, 1] -> index 0: left=0, right=0; index 4: left=0, right=0; index 2: left=0, right=0
    r4 = equilibrium_index([1, -1, 1, -1, 1])

    if not r1['indices'] and not r3['indices']:
        print("  NOT YET IMPLEMENTED")
    else:
        checks = [
            (r1['indices'], [3], "[-7,1,5,2,-4,3,0]"),
            (r2['indices'], [], "[1,2,3]"),
            (r3['indices'], [0, 1, 2, 3], "[0,0,0,0]"),
            (r4['indices'], [0, 2, 4], "[1,-1,1,-1,1]"),
        ]
        all_pass = True
        for got, expected, desc in checks:
            status = "PASS" if got == expected else "FAIL"
            if got != expected:
                all_pass = False
            print(f"  {status}: {desc} -> indices={got} (expected {expected})")
        if all_pass:
            print("  All equilibrium index tests passed!")


if __name__ == "__main__":
    run_checks()
