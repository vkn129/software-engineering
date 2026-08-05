"""
Day 110 Practice: Staircase Search in Sorted 2D Matrices

6 exercises. Implement TODOs, then run: python practice.py

Precondition throughout: rows ascend left-to-right AND columns ascend
top-to-bottom. Nothing stronger -- the row-major flattening is not sorted, so
Day 020's flatten + binary search does not apply here.

"not found" is (-1, -1), never None: try_or_sol reads a None result as "the
student stub is unimplemented" and silently falls back.
"""


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


def dims(matrix):
    """(rows, cols). Both [] and [[]] must report zero work to do."""
    m = len(matrix)
    n = len(matrix[0]) if m else 0
    return m, n


# ---------------------------------------------------------------------------
# Exercise 1: search_staircase
# ---------------------------------------------------------------------------
# Start at the TOP-RIGHT corner. One comparison must retire a whole line:
#   v > target -> every cell below in this column is >= v, so the column dies
#   v < target -> every cell left in this row is <= v, so the row dies
# Return (row, col), or (-1, -1).

def search_staircase(matrix, target):
    """Top-right staircase search. Return (row, col) or (-1, -1)."""
    # TODO: implement
    pass


def _sol_search_staircase(matrix, target):
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


# ---------------------------------------------------------------------------
# Exercise 2: search_from_bottom_left
# ---------------------------------------------------------------------------
# The other corner that works. Only the two ANTI-DIAGONAL corners can
# eliminate: at top-left or bottom-right both moves point the same comparison
# direction, so a comparison prunes nothing.

def search_from_bottom_left(matrix, target):
    """Bottom-left staircase search. Return (row, col) or (-1, -1)."""
    # TODO: implement, mirroring exercise 1
    pass


def _sol_search_from_bottom_left(matrix, target):
    m, n = dims(matrix)
    r, c = m - 1, 0
    while r >= 0 and c < n:
        v = matrix[r][c]
        if v == target:
            return (r, c)
        if v > target:
            r -= 1
        else:
            c += 1
    return (-1, -1)


# ---------------------------------------------------------------------------
# Exercise 3: staircase_steps
# ---------------------------------------------------------------------------
# Count cells probed by the top-right walk, including the matching one.
# Each step drops a full row or a full column, so this can never exceed
# m + n - 1 -- that bound is the entire performance claim of the day.

def staircase_steps(matrix, target):
    """Number of cells the top-right walk probes."""
    # TODO: implement
    pass


def _sol_staircase_steps(matrix, target):
    m, n = dims(matrix)
    r, c, steps = 0, n - 1, 0
    while r < m and c >= 0:
        steps += 1
        v = matrix[r][c]
        if v == target:
            break
        if v > target:
            c -= 1
        else:
            r += 1
    return steps


# ---------------------------------------------------------------------------
# Exercise 4: count_le
# ---------------------------------------------------------------------------
# How many entries are <= x, in O(m + n). Walk from the BOTTOM-LEFT: a hit at
# row r means every cell above it in that column also qualifies, so r + 1
# cells are settled at once. The +1 is the 0-indexing.

def count_le(matrix, x):
    """Count of entries <= x."""
    # TODO: implement
    pass


def _sol_count_le(matrix, x):
    m, n = dims(matrix)
    r, c, total = m - 1, 0, 0
    while r >= 0 and c < n:
        if matrix[r][c] <= x:
            total += r + 1
            c += 1
        else:
            r -= 1
    return total


# ---------------------------------------------------------------------------
# Exercise 5: kth_smallest
# ---------------------------------------------------------------------------
# 1-indexed, duplicates counted separately. Day 106's search-on-answer-space
# fed by exercise 4: binary search the VALUE range for the smallest v with
# count_le(v) >= k. That v is always a real entry -- if it were not,
# count_le(v) would equal count_le(v-1) and v would not be smallest.

def kth_smallest(matrix, k):
    """k-th smallest entry (1-indexed)."""
    # TODO: implement
    pass


def _sol_kth_smallest(matrix, k):
    m, n = dims(matrix)
    lo, hi = matrix[0][0], matrix[m - 1][n - 1]
    while lo < hi:
        mid = lo + (hi - lo) // 2       # Day 106: overflow-safe midpoint
        if _sol_count_le(matrix, mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


# ---------------------------------------------------------------------------
# Exercise 6: is_row_col_sorted
# ---------------------------------------------------------------------------
# The precondition check. Every function above returns a confidently WRONG
# answer rather than an error when it is violated, so this is the guard you
# want at a trust boundary. Ragged rows are not a matrix and must fail.

def is_row_col_sorted(matrix):
    """True if every row ascends, every column ascends, rows are equal length."""
    # TODO: implement
    pass


def _sol_is_row_col_sorted(matrix):
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
# Test Runner
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(label, got, want):
        nonlocal passed, failed
        if got == want:
            print(f"  PASS: {label}")
            passed += 1
        else:
            print(f"  FAIL: {label}")
            print(f"    expected: {want}")
            print(f"    got:      {got}")
            failed += 1

    M = [
        [1, 4, 7, 11],
        [2, 5, 8, 12],
        [3, 6, 9, 16],
        [10, 13, 14, 17],
    ]

    print("Exercise 1: search_staircase")
    check("find 5", try_or_sol("search_staircase", M, 5), (1, 1))
    check("find 1 (top-left)", try_or_sol("search_staircase", M, 1), (0, 0))
    check("find 17 (bottom-right)", try_or_sol("search_staircase", M, 17), (3, 3))
    check("find 11 (start cell)", try_or_sol("search_staircase", M, 11), (0, 3))
    check("missing interior 15", try_or_sol("search_staircase", M, 15), (-1, -1))
    check("below range", try_or_sol("search_staircase", M, 0), (-1, -1))
    check("above range", try_or_sol("search_staircase", M, 99), (-1, -1))
    check("empty matrix", try_or_sol("search_staircase", [], 1), (-1, -1))
    check("empty row", try_or_sol("search_staircase", [[]], 1), (-1, -1))

    print("\nExercise 2: search_from_bottom_left")
    check("find 5", try_or_sol("search_from_bottom_left", M, 5), (1, 1))
    check("find 10", try_or_sol("search_from_bottom_left", M, 10), (3, 0))
    check("missing 15", try_or_sol("search_from_bottom_left", M, 15), (-1, -1))
    # The counterexample that kills a top-left start: 2 sits down-and-left of
    # (0,0), a direction the greedy top-left walk can never take.
    tricky = [[1, 4], [2, 5]]
    check("tricky 2 via top-right", try_or_sol("search_staircase", tricky, 2), (1, 0))
    check("tricky 2 via bottom-left",
          try_or_sol("search_from_bottom_left", tricky, 2), (1, 0))

    print("\nExercise 3: staircase_steps")
    check("found 5 in 4 probes", try_or_sol("staircase_steps", M, 5), 4)
    # 15 is absent: the walk goes (0,3) (1,3) (2,3) (2,2) (3,2) then falls off
    # the bottom -- 5 probes, comfortably under the m+n-1 = 7 ceiling.
    check("miss walks off the edge in 5", try_or_sol("staircase_steps", M, 15), 5)
    check("never exceeds m+n-1",
          all(try_or_sol("staircase_steps", M, t) <= 4 + 4 - 1
              for t in range(-1, 20)), True)
    check("empty matrix probes nothing", try_or_sol("staircase_steps", [], 1), 0)

    print("\nExercise 4: count_le")
    flat = sorted(v for row in M for v in row)
    check("count_le(0)", try_or_sol("count_le", M, 0), 0)
    check("count_le(5)", try_or_sol("count_le", M, 5), 5)
    check("count_le(9)", try_or_sol("count_le", M, 9), 9)
    check("count_le(17) = all", try_or_sol("count_le", M, 17), 16)
    check("count_le(100) = all", try_or_sol("count_le", M, 100), 16)
    check("agrees with brute force at every value",
          all(try_or_sol("count_le", M, x) == sum(1 for v in flat if v <= x)
              for x in range(-1, 20)), True)
    # Duplicates: counting must not collapse equal values
    dup = [[1, 1, 2], [1, 2, 2], [2, 2, 3]]
    check("duplicates counted separately", try_or_sol("count_le", dup, 1), 3)

    print("\nExercise 5: kth_smallest")
    check("k=1", try_or_sol("kth_smallest", M, 1), 1)
    check("k=5", try_or_sol("kth_smallest", M, 5), 5)
    check("k=8", try_or_sol("kth_smallest", M, 8), 8)
    check("k=16 (last)", try_or_sol("kth_smallest", M, 16), 17)
    check("every k matches the sorted flat list",
          all(try_or_sol("kth_smallest", M, k) == flat[k - 1]
              for k in range(1, 17)), True)
    dup_flat = sorted(v for row in dup for v in row)
    check("duplicates: every k",
          all(try_or_sol("kth_smallest", dup, k) == dup_flat[k - 1]
              for k in range(1, 10)), True)

    print("\nExercise 6: is_row_col_sorted")
    check("classic matrix is valid", try_or_sol("is_row_col_sorted", M), True)
    check("empty is vacuously valid", try_or_sol("is_row_col_sorted", []), True)
    check("row out of order",
          try_or_sol("is_row_col_sorted", [[1, 4], [2, 5], [3, 1]]), False)
    check("column out of order",
          try_or_sol("is_row_col_sorted", [[3, 4], [1, 5]]), False)
    check("ragged rows rejected",
          try_or_sol("is_row_col_sorted", [[1, 2, 3], [4, 5]]), False)
    # Row+column sorted, yet the row-major flattening is 1,4,2,5 -- unsorted.
    # That is exactly why Day 020's flatten trick cannot be reused here.
    check("row+col sorted but not globally sorted",
          try_or_sol("is_row_col_sorted", tricky), True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
