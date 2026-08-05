"""
Day 171 Practice: Mo's Algorithm + Sqrt Decomposition

6 exercises covering sqrt decomp sum/min, Mo's distinct, Mo's sum,
range mode, and pair count. Run: python practice.py
"""

from collections import defaultdict


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


# ===================================================================
# Exercise 1: Sqrt Decomp Range Sum (no updates)
# ===================================================================

def sqrt_range_sum(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r) inclusive
    Returns: list of range sums using sqrt decomposition (O(sqrt(N)) per query)
    """
    # TODO: implement sqrt decomposition with precomputed block sums
    pass


def _sol_sqrt_range_sum(arr, queries):
    n = len(arr)
    if n == 0:
        return [0 for _ in queries]
    b = max(1, int(n ** 0.5))
    blocks = [0] * ((n + b - 1) // b)
    for i, v in enumerate(arr):
        blocks[i // b] += v
    out = []
    for l, r in queries:
        bl, br = l // b, r // b
        total = 0
        if bl == br:
            for i in range(l, r + 1):
                total += arr[i]
        else:
            for i in range(l, (bl + 1) * b):
                total += arr[i]
            for k in range(bl + 1, br):
                total += blocks[k]
            for i in range(br * b, r + 1):
                total += arr[i]
        out.append(total)
    return out


# ===================================================================
# Exercise 2: Sqrt Decomp Range Min
# ===================================================================

def sqrt_range_min(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r) inclusive
    Returns: list of range minima using sqrt decomposition
    """
    # TODO: implement
    pass


def _sol_sqrt_range_min(arr, queries):
    n = len(arr)
    if n == 0:
        return []
    b = max(1, int(n ** 0.5))
    nb = (n + b - 1) // b
    block_min = [float('inf')] * nb
    for i, v in enumerate(arr):
        if v < block_min[i // b]:
            block_min[i // b] = v
    out = []
    for l, r in queries:
        bl, br = l // b, r // b
        m = float('inf')
        if bl == br:
            for i in range(l, r + 1):
                m = min(m, arr[i])
        else:
            for i in range(l, (bl + 1) * b):
                m = min(m, arr[i])
            for k in range(bl + 1, br):
                m = min(m, block_min[k])
            for i in range(br * b, r + 1):
                m = min(m, arr[i])
        out.append(m)
    return out


# ===================================================================
# Exercise 3: Mo's Algorithm — Distinct Count
# ===================================================================

def mo_distinct(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r) inclusive
    Returns: list of distinct counts per query, using Mo's algorithm
    """
    # TODO: implement Mo's algorithm
    pass


def _sol_mo_distinct(arr, queries):
    n = len(arr)
    if n == 0:
        return [0 for _ in queries]
    block = max(1, int(n ** 0.5))
    idx = list(enumerate(queries))
    idx.sort(key=lambda it: (it[1][0] // block, it[1][1]))
    freq = defaultdict(int)
    distinct = 0
    L, R = 0, -1
    ans = [0] * len(queries)
    for qi, (l, r) in idx:
        while R < r:
            R += 1
            if freq[arr[R]] == 0: distinct += 1
            freq[arr[R]] += 1
        while L > l:
            L -= 1
            if freq[arr[L]] == 0: distinct += 1
            freq[arr[L]] += 1
        while R > r:
            freq[arr[R]] -= 1
            if freq[arr[R]] == 0: distinct -= 1
            R -= 1
        while L < l:
            freq[arr[L]] -= 1
            if freq[arr[L]] == 0: distinct -= 1
            L += 1
        ans[qi] = distinct
    return ans


# ===================================================================
# Exercise 4: Mo's Algorithm — Range Sum (just to practice the pattern)
# ===================================================================

def mo_range_sum(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r) inclusive
    Returns: range sums using Mo's algorithm (pattern practice).
    """
    # TODO: implement
    pass


def _sol_mo_range_sum(arr, queries):
    n = len(arr)
    if n == 0:
        return [0 for _ in queries]
    block = max(1, int(n ** 0.5))
    idx = list(enumerate(queries))
    idx.sort(key=lambda it: (it[1][0] // block, it[1][1]))
    total = 0
    L, R = 0, -1
    ans = [0] * len(queries)
    for qi, (l, r) in idx:
        while R < r:
            R += 1; total += arr[R]
        while L > l:
            L -= 1; total += arr[L]
        while R > r:
            total -= arr[R]; R -= 1
        while L < l:
            total -= arr[L]; L += 1
        ans[qi] = total
    return ans


# ===================================================================
# Exercise 5: Mo's Algorithm — Mode Count
# ===================================================================
# For each query, return the FREQUENCY of the most-frequent element.

def mo_mode_frequency(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r) inclusive
    Returns: list of max frequency in each range
    """
    # TODO: implement (maintain freq + bucket of "count of elements with freq f")
    pass


def _sol_mo_mode_frequency(arr, queries):
    n = len(arr)
    if n == 0:
        return [0 for _ in queries]
    block = max(1, int(n ** 0.5))
    idx = list(enumerate(queries))
    idx.sort(key=lambda it: (it[1][0] // block, it[1][1]))
    freq = defaultdict(int)
    cnt_at = defaultdict(int)  # how many elements have frequency f
    cnt_at[0] = float('inf')
    max_f = 0
    L, R = 0, -1
    ans = [0] * len(queries)

    def add(x):
        nonlocal max_f
        f = freq[x]
        cnt_at[f] -= 1
        freq[x] = f + 1
        cnt_at[f + 1] += 1
        if f + 1 > max_f:
            max_f = f + 1

    def remove(x):
        nonlocal max_f
        f = freq[x]
        cnt_at[f] -= 1
        freq[x] = f - 1
        cnt_at[f - 1] += 1
        if cnt_at[max_f] == 0:
            max_f -= 1

    for qi, (l, r) in idx:
        while R < r:
            R += 1; add(arr[R])
        while L > l:
            L -= 1; add(arr[L])
        while R > r:
            remove(arr[R]); R -= 1
        while L < l:
            remove(arr[L]); L += 1
        ans[qi] = max_f
    return ans


# ===================================================================
# Exercise 6: Count Equal Pairs in Range
# ===================================================================
# Count pairs (i, j) with l <= i < j <= r and arr[i] == arr[j].
# = sum_x C(freq_x, 2) = sum_x freq_x*(freq_x - 1) / 2

def mo_equal_pairs(arr, queries):
    """
    Returns: list of count(i<j in [l,r] with arr[i]==arr[j]) for each query.
    """
    # TODO: implement
    pass


def _sol_mo_equal_pairs(arr, queries):
    n = len(arr)
    if n == 0:
        return [0 for _ in queries]
    block = max(1, int(n ** 0.5))
    idx = list(enumerate(queries))
    idx.sort(key=lambda it: (it[1][0] // block, it[1][1]))
    freq = defaultdict(int)
    total = 0  # sum of C(f, 2)
    L, R = 0, -1
    ans = [0] * len(queries)

    def add(x):
        nonlocal total
        total += freq[x]  # C(f+1,2) - C(f,2) = f
        freq[x] += 1

    def remove(x):
        nonlocal total
        freq[x] -= 1
        total -= freq[x]  # C(f-1,2) - C(f,2) = -(f-1)

    for qi, (l, r) in idx:
        while R < r:
            R += 1; add(arr[R])
        while L > l:
            L -= 1; add(arr[L])
        while R > r:
            remove(arr[R]); R -= 1
        while L < l:
            remove(arr[L]); L += 1
        ans[qi] = total
    return ans


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

    arr = [1, 3, 2, 7, 5, 3, 1, 4, 2, 3]
    queries = [(0, 9), (2, 5), (1, 1), (4, 8), (0, 4)]

    # --- Exercise 1 ---
    print("Exercise 1: Sqrt Range Sum")
    expected_sum = [sum(arr[l:r+1]) for l, r in queries]
    check("range sums", try_or_sol("sqrt_range_sum", arr, queries), expected_sum)
    check("single elem", try_or_sol("sqrt_range_sum", [5], [(0, 0)]), [5])

    # --- Exercise 2 ---
    print("\nExercise 2: Sqrt Range Min")
    expected_min = [min(arr[l:r+1]) for l, r in queries]
    check("range mins", try_or_sol("sqrt_range_min", arr, queries), expected_min)

    # --- Exercise 3 ---
    print("\nExercise 3: Mo's Distinct Count")
    expected_dist = [len(set(arr[l:r+1])) for l, r in queries]
    check("distinct counts", try_or_sol("mo_distinct", arr, queries), expected_dist)

    # --- Exercise 4 ---
    print("\nExercise 4: Mo's Range Sum")
    check("mo sums", try_or_sol("mo_range_sum", arr, queries), expected_sum)

    # --- Exercise 5 ---
    print("\nExercise 5: Mo's Mode Frequency")
    def brute_mode(l, r):
        c = defaultdict(int)
        for x in arr[l:r+1]:
            c[x] += 1
        return max(c.values())
    expected_mode = [brute_mode(l, r) for l, r in queries]
    check("mode freq", try_or_sol("mo_mode_frequency", arr, queries), expected_mode)

    # --- Exercise 6 ---
    print("\nExercise 6: Mo's Equal Pairs")
    def brute_pairs(l, r):
        c = defaultdict(int)
        for x in arr[l:r+1]:
            c[x] += 1
        return sum(v*(v-1)//2 for v in c.values())
    expected_pairs = [brute_pairs(l, r) for l, r in queries]
    check("equal pairs", try_or_sol("mo_equal_pairs", arr, queries), expected_pairs)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
