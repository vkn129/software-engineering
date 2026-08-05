"""
Day 110: Staircase Search in Sorted 2D Matrices

Precondition, and it is the whole story:

    M[r][c] <= M[r][c+1]     rows ascend left to right
    M[r][c] <= M[r+1][c]     columns ascend top to bottom

Nothing stronger. In particular the row-major flattening is NOT sorted, so the
flatten-plus-binary-search approach for globally sorted matrices (Day 020)
gives wrong answers here, not slow ones.

Starting at an anti-diagonal corner, one comparison retires an entire row or
an entire column, so search costs O(m + n) with O(1) space.

Run: python3 matrix_search.py
"""

import random


def dims(matrix):
    """(rows, cols). Both [] and [[]] must report zero work to do."""
    m = len(matrix)
    n = len(matrix[0]) if m else 0
    return m, n


def is_row_col_sorted(matrix):
    """Validate the precondition. Ragged rows are not a matrix and fail here.

    Worth calling once at a trust boundary: every algorithm below returns a
    confidently wrong answer rather than an error on a matrix that violates it.
    """
    m, n = dims(matrix)
    # Length check must finish BEFORE any matrix[r+1][c] probe: on a ragged
    # input the column comparison would index off the end of a short row and
    # raise instead of returning False.
    if any(len(row) != n for row in matrix):
        return False
    for r in range(m):
        for c in range(n):
            if c + 1 < n and matrix[r][c] > matrix[r][c + 1]:
                return False
            if r + 1 < m and matrix[r][c] > matrix[r + 1][c]:
                return False
    return True


# ---------------------------------------------------------------------------
# 1. The staircase walk
# ---------------------------------------------------------------------------

def search_staircase(matrix, target):
    """Search from the top-right corner. Return (row, col) or (-1, -1).

    At (r, c): v > target kills column c, because every cell below it in that
    column is >= v and every row above r is already gone. v < target kills
    row r by the mirror argument. Either way one full line disappears per
    comparison, so this terminates in at most m + n - 1 probes.
    """
    m, n = dims(matrix)
    r, c = 0, n - 1
    while r < m and c >= 0:
        v = matrix[r][c]
        if v == target:
            return (r, c)
        if v > target:
            c -= 1
        else:
            r += 1
    return (-1, -1)


def search_staircase_bottom_left(matrix, target):
    """Same algorithm from the other working corner. Return (row, col)."""
    m, n = dims(matrix)
    r, c = m - 1, 0
    while r >= 0 and c < n:
        v = matrix[r][c]
        if v == target:
            return (r, c)
        if v > target:
            r -= 1          # this row and everything below it is too large
        else:
            c += 1          # this column and everything left of it is too small
    return (-1, -1)


def staircase_path(matrix, target):
    """Every cell the top-right walk probes, in order. Length <= m + n - 1."""
    m, n = dims(matrix)
    path = []
    r, c = 0, n - 1
    while r < m and c >= 0:
        path.append((r, c))
        v = matrix[r][c]
        if v == target:
            break
        if v > target:
            c -= 1
        else:
            r += 1
    return path


def search_from_top_left_broken(matrix, target):
    """Deliberately wrong: the same greedy walk started at the top-left.

    Kept because the failure is instructive. At (0,0) both legal moves lead to
    larger values, so a comparison eliminates nothing and the walk can stride
    straight past the target. demo_corners() exhibits a matrix where it does.
    """
    m, n = dims(matrix)
    r, c = 0, 0
    while r < m and c < n:
        v = matrix[r][c]
        if v == target:
            return (r, c)
        if v < target:
            c += 1
        else:
            r += 1
    return (-1, -1)


# ---------------------------------------------------------------------------
# 2. Binary search per row, with a telescoping bound
# ---------------------------------------------------------------------------

def search_rows_telescoping(matrix, target):
    """Binary search each row, shrinking the window as rows descend.

    The boundary column "first entry >= target" is non-increasing down the
    rows, because M[r+1][c] >= M[r][c]. So once row r reports its boundary at
    column b (and M[r][b] != target), no later row can hold the target at
    column b or beyond -- those cells are only larger. That telescoping is
    what turns O(m log n) into O(m log(n/m)) on wide matrices.
    """
    m, n = dims(matrix)
    bound = n                       # exclusive: search columns [0, bound)
    for r in range(m):
        lo, hi = 0, bound - 1
        while lo <= hi:             # lower_bound within the live window
            mid = (lo + hi) // 2
            if matrix[r][mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        if lo < bound:
            if matrix[r][lo] == target:
                return (r, lo)
            bound = lo              # M[r][lo] > target, so are all cells below
            if bound == 0:
                break               # whole matrix from here on exceeds target
    return (-1, -1)


def brute_force_search(matrix, target):
    """O(m*n) oracle. Assumes nothing, always right, used to check the rest."""
    for r, row in enumerate(matrix):
        for c, v in enumerate(row):
            if v == target:
                return (r, c)
    return (-1, -1)


# ---------------------------------------------------------------------------
# 3. Counting, and kth smallest on top of it
# ---------------------------------------------------------------------------

def count_le(matrix, x):
    """Number of entries <= x, in O(m + n). Walk from the bottom-left.

    A hit at row r means every cell above it in this column is also <= x
    (columns ascend downward), so r + 1 cells are accounted for at once. The
    +1 is the 0-indexing: row r is the (r+1)-th cell from the top.
    """
    m, n = dims(matrix)
    r, c, total = m - 1, 0, 0
    while r >= 0 and c < n:
        if matrix[r][c] <= x:
            total += r + 1
            c += 1
        else:
            r -= 1
    return total


def kth_smallest(matrix, k):
    """k-th smallest entry, 1-indexed, counting duplicates separately.

    Day 106's search-on-answer-space applied to the counting oracle above:
    binary search the VALUE range for the smallest v with count_le(v) >= k.
    That v is always a real matrix entry -- if it were not, count_le(v) would
    equal count_le(v - 1), so v - 1 would also satisfy the predicate and v
    could not be the smallest such value.
    """
    m, n = dims(matrix)
    if m == 0 or n == 0 or k < 1 or k > m * n:
        raise ValueError(f"k={k} out of range for a {m}x{n} matrix")
    lo, hi = matrix[0][0], matrix[m - 1][n - 1]
    while lo < hi:
        mid = lo + (hi - lo) // 2       # Day 106: avoids overflow in C-likes
        if count_le(matrix, mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

CLASSIC = [
    [1, 4, 7, 11],
    [2, 5, 8, 12],
    [3, 6, 9, 16],
    [10, 13, 14, 17],
]


def random_sorted_matrix(m, n, rng, max_step=4):
    """Row+column-sorted matrix built from non-negative increments.

    Prefix-summing non-negative steps along rows and then down columns makes
    both orderings true by construction -- no rejection sampling needed.
    """
    grid = [[rng.randint(0, max_step) for _ in range(n)] for _ in range(m)]
    for r in range(m):
        for c in range(1, n):
            grid[r][c] += grid[r][c - 1]
    for c in range(n):
        for r in range(1, m):
            grid[r][c] += grid[r - 1][c]
    return grid


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_walk():
    print("--- The staircase walk, target = 5 ---")
    for row in CLASSIC:
        print("   " + " ".join(f"{v:3d}" for v in row))
    path = staircase_path(CLASSIC, 5)
    print(f"  probed {len(path)} cells: {path}")
    m, n = dims(CLASSIC)
    print(f"  bound is m + n - 1 = {m + n - 1}; brute force would probe {m*n}")
    print(f"  result: {search_staircase(CLASSIC, 5)}")


def demo_corners():
    print("\n--- Why the top-left corner cannot work ---")
    bad = [[1, 4],
           [2, 5]]
    print("   1  4")
    print("   2  5      target = 2, actually at (1,0)")
    print(f"  top-right staircase:   {search_staircase(bad, 2)}  (correct)")
    print(f"  bottom-left staircase: {search_staircase_bottom_left(bad, 2)}  (correct)")
    print(f"  greedy from top-left:  {search_from_top_left_broken(bad, 2)}  (WRONG)")
    print("  from (0,0) both moves lead to larger values, so 1 < 2 says")
    print("  nothing about whether to go right or down")
    print("  same matrix flattened row-major is 1,4,2,5 -- not sorted, so")
    print("  Day 020's flatten + binary search does not apply here either")


def demo_count_and_kth():
    print("\n--- count_le and kth_smallest ---")
    flat = sorted(v for row in CLASSIC for v in row)
    for x in [0, 5, 9, 17, 100]:
        got, want = count_le(CLASSIC, x), sum(1 for v in flat if v <= x)
        print(f"  count_le({x:3d}) = {got:2d}   (brute force {want:2d})"
              f"  [{'OK' if got == want else 'MISMATCH'}]")
    for k in [1, 5, 8, 16]:
        got, want = kth_smallest(CLASSIC, k), flat[k - 1]
        print(f"  kth_smallest({k:2d}) = {got:2d}   (sorted flat {want:2d})"
              f"  [{'OK' if got == want else 'MISMATCH'}]")


def demo_probe_counts():
    print("\n--- Probes by matrix shape ---")
    rng = random.Random(110)
    print("  shape        worst staircase walk      brute force (m*n)")
    for m, n in [(4, 4), (16, 16), (64, 64), (4, 256), (256, 4)]:
        grid = random_sorted_matrix(m, n, rng)
        worst = 0
        for _ in range(50):
            t = rng.randint(0, grid[m - 1][n - 1])
            worst = max(worst, len(staircase_path(grid, t)))
        print(f"  {m:4d}x{n:<6d} {worst:5d} (bound {m + n - 1:5d})"
              f"        {m * n}")
    print("  wide matrices are where binary-search-per-row wins: the")
    print("  staircase pays one probe for every one of those n columns")


def demo_agreement():
    print("\n--- Randomized agreement across all four searches ---")
    rng = random.Random(1100)
    mismatches = 0
    for _ in range(300):
        m, n = rng.randint(1, 8), rng.randint(1, 8)
        grid = random_sorted_matrix(m, n, rng)
        assert is_row_col_sorted(grid), "generator broke the precondition"
        hi = grid[m - 1][n - 1]
        for t in range(-1, hi + 2):
            want_found = brute_force_search(grid, t) != (-1, -1)
            for fn in (search_staircase, search_staircase_bottom_left,
                       search_rows_telescoping):
                r, c = fn(grid, t)
                if (r, c) == (-1, -1):
                    if want_found:
                        mismatches += 1
                elif grid[r][c] != t:       # any correct cell is acceptable
                    mismatches += 1
            if len(staircase_path(grid, t)) > m + n - 1:
                mismatches += 1
            if count_le(grid, t) != sum(1 for row in grid for v in row if v <= t):
                mismatches += 1
        flat = sorted(v for row in grid for v in row)
        for k in range(1, m * n + 1):
            if kth_smallest(grid, k) != flat[k - 1]:
                mismatches += 1
    print(f"  300 random matrices, every target and every k: "
          f"mismatches={mismatches}")
    assert mismatches == 0, "a search disagreed with brute force"


def demo():
    demo_walk()
    demo_corners()
    demo_count_and_kth()
    demo_probe_counts()
    demo_agreement()
    print("\nAll demos consistent with brute force.")


if __name__ == "__main__":
    demo()
