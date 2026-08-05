"""
Day 169 Practice: Backtracking Patterns

6 exercises covering N-queens, subsets, permutations, sudoku validation,
word search, and palindrome partitioning. Run: python practice.py
"""


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
# Exercise 1: Count N-Queens Solutions
# ===================================================================
# Return the number of distinct N-queens placements.

def count_n_queens(n):
    """
    n: board size
    Returns: number of valid placements of n queens on n x n board.
    """
    # TODO: implement using backtracking (cols + 2 diagonals)
    pass


def _sol_count_n_queens(n):
    count = [0]
    cols, d1, d2 = set(), set(), set()

    def backtrack(row):
        if row == n:
            count[0] += 1
            return
        for c in range(n):
            if c in cols or (row + c) in d1 or (row - c) in d2:
                continue
            cols.add(c); d1.add(row + c); d2.add(row - c)
            backtrack(row + 1)
            cols.remove(c); d1.remove(row + c); d2.remove(row - c)

    backtrack(0)
    return count[0]


# ===================================================================
# Exercise 2: All Subsets
# ===================================================================
# Generate all subsets (power set) of nums.

def all_subsets(nums):
    """
    nums: list of distinct integers
    Returns: list of all subsets (each as a sorted list), sorted lexicographically
    """
    # TODO: implement
    pass


def _sol_all_subsets(nums):
    result = []
    nums_sorted = sorted(nums)
    cur = []

    def backtrack(i):
        if i == len(nums_sorted):
            result.append(cur[:])
            return
        # Exclude
        backtrack(i + 1)
        # Include
        cur.append(nums_sorted[i])
        backtrack(i + 1)
        cur.pop()

    backtrack(0)
    return sorted(result)


# ===================================================================
# Exercise 3: All Permutations
# ===================================================================
# Generate all permutations of nums.

def all_permutations(nums):
    """
    nums: list of distinct integers
    Returns: list of all permutations, sorted lexicographically
    """
    # TODO: implement
    pass


def _sol_all_permutations(nums):
    result = []
    used = [False] * len(nums)
    cur = []
    nums_sorted = sorted(nums)

    def backtrack():
        if len(cur) == len(nums_sorted):
            result.append(cur[:])
            return
        for i in range(len(nums_sorted)):
            if used[i]:
                continue
            used[i] = True
            cur.append(nums_sorted[i])
            backtrack()
            cur.pop()
            used[i] = False

    backtrack()
    return result


# ===================================================================
# Exercise 4: Validate Sudoku Board
# ===================================================================
# Check if a 9x9 board with some cells filled is currently consistent.
# (Not "is it solvable" — only "do current cells violate any rule".)

def is_valid_sudoku(board):
    """
    board: 9x9 list, 0 = empty, 1-9 = filled
    Returns: True if no row/col/box has a duplicate among filled cells
    """
    # TODO: implement
    pass


def _sol_is_valid_sudoku(board):
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    for r in range(9):
        for c in range(9):
            v = board[r][c]
            if v == 0:
                continue
            b = (r // 3) * 3 + c // 3
            if v in rows[r] or v in cols[c] or v in boxes[b]:
                return False
            rows[r].add(v); cols[c].add(v); boxes[b].add(v)
    return True


# ===================================================================
# Exercise 5: Word Search in Grid
# ===================================================================
# Given a 2D grid of letters and a word, check if the word exists by
# moving up/down/left/right between adjacent cells (no cell reuse).

def word_search(grid, word):
    """
    grid: list of list of single-char strings
    word: target string
    Returns: True if word can be traced in grid
    """
    # TODO: implement DFS + backtracking with visited tracking
    pass


def _sol_word_search(grid, word):
    if not grid or not grid[0] or not word:
        return False
    rows, cols = len(grid), len(grid[0])

    def dfs(r, c, i):
        if i == len(word):
            return True
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return False
        if grid[r][c] != word[i]:
            return False
        saved = grid[r][c]
        grid[r][c] = '#'
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or
                 dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        grid[r][c] = saved
        return found

    for r in range(rows):
        for c in range(cols):
            if dfs(r, c, 0):
                return True
    return False


# ===================================================================
# Exercise 6: Palindrome Partitioning
# ===================================================================
# Partition string s such that every substring is a palindrome.
# Return all such partitions.

def palindrome_partitions(s):
    """
    s: string
    Returns: list of partitions, each a list of palindrome substrings.
             Output sorted lexicographically.
    """
    # TODO: implement
    pass


def _sol_palindrome_partitions(s):
    result = []
    cur = []

    def is_pal(t):
        return t == t[::-1]

    def backtrack(i):
        if i == len(s):
            result.append(cur[:])
            return
        for j in range(i + 1, len(s) + 1):
            piece = s[i:j]
            if is_pal(piece):
                cur.append(piece)
                backtrack(j)
                cur.pop()

    backtrack(0)
    return sorted(result)


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
    print("Exercise 1: Count N-Queens")
    check("n=4", try_or_sol("count_n_queens", 4), 2)
    check("n=5", try_or_sol("count_n_queens", 5), 10)
    check("n=8", try_or_sol("count_n_queens", 8), 92)

    # --- Exercise 2 ---
    print("\nExercise 2: All Subsets")
    check("[1,2]", try_or_sol("all_subsets", [1, 2]), [[], [1], [1, 2], [2]])
    check("[]", try_or_sol("all_subsets", []), [[]])
    r = try_or_sol("all_subsets", [1, 2, 3])
    check("len([1,2,3])", len(r), 8)

    # --- Exercise 3 ---
    print("\nExercise 3: All Permutations")
    check("[1,2]", try_or_sol("all_permutations", [1, 2]), [[1, 2], [2, 1]])
    r = try_or_sol("all_permutations", [1, 2, 3])
    check("len([1,2,3])", len(r), 6)
    check("first perm sorted", r[0], [1, 2, 3])

    # --- Exercise 4 ---
    print("\nExercise 4: Validate Sudoku")
    valid = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    check("valid puzzle", try_or_sol("is_valid_sudoku", valid), True)
    bad = [row[:] for row in valid]
    bad[0][1] = 5  # duplicate 5 in box (0,0)
    check("invalid: dup in box", try_or_sol("is_valid_sudoku", bad), False)

    # --- Exercise 5 ---
    print("\nExercise 5: Word Search")
    grid = [
        ['A', 'B', 'C', 'E'],
        ['S', 'F', 'C', 'S'],
        ['A', 'D', 'E', 'E'],
    ]
    check("ABCCED", try_or_sol("word_search", [r[:] for r in grid], "ABCCED"), True)
    check("SEE", try_or_sol("word_search", [r[:] for r in grid], "SEE"), True)
    check("ABCB (reuse)", try_or_sol("word_search", [r[:] for r in grid], "ABCB"), False)

    # --- Exercise 6 ---
    print("\nExercise 6: Palindrome Partitioning")
    check("aab", try_or_sol("palindrome_partitions", "aab"),
          sorted([["a", "a", "b"], ["aa", "b"]]))
    check("a", try_or_sol("palindrome_partitions", "a"), [["a"]])
    r = try_or_sol("palindrome_partitions", "aba")
    check("aba partitions", sorted(r), sorted([["a", "b", "a"], ["aba"]]))

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
