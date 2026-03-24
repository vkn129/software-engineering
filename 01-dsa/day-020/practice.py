"""
Day 19 Practice: Search Implementation Exercises

Implement each function below. Every function has:
- A docstring explaining what to implement
- Test cases that run automatically
- Solutions at the bottom (revealed when you run the file)

Work through these in order. Do NOT look at the solutions until you have
tried each one yourself. The point is to build muscle memory for the
invariants and boundary conditions.

Run: python practice.py
"""


# ---------------------------------------------------------------------------
# Exercise 1: Linear Search
# ---------------------------------------------------------------------------

def linear_search(arr, target):
    """Search for target in arr by examining each element in order.

    Return the INDEX of the first occurrence of target, or -1 if not found.

    This is the simplest search. Get it right before moving on.
    """
    # TODO: Implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Binary Search (Iterative)
# ---------------------------------------------------------------------------

def binary_search(arr, target):
    """Search for target in a SORTED array using binary search.

    Return the INDEX of target, or -1 if not found.

    Key details to get right:
    - Initialize lo and hi correctly
    - Use lo <= hi (not lo < hi)
    - Compute mid without overflow: lo + (hi - lo) // 2
    - Update lo and hi to EXCLUDE mid (mid+1 or mid-1)
    """
    # TODO: Implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 3: Binary Search (Recursive)
# ---------------------------------------------------------------------------

def binary_search_recursive(arr, target, lo=None, hi=None):
    """Same as binary_search but using recursion.

    Return the INDEX of target, or -1 if not found.

    On first call, lo and hi will be None — set them to 0 and len(arr)-1.
    Base case: if lo > hi, return -1.
    """
    # TODO: Implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Count Occurrences with Linear Search
# ---------------------------------------------------------------------------

def count_occurrences(arr, target):
    """Count how many times target appears in arr (unsorted).

    Return the count (0 if not found).

    This is a case where linear search is the right tool — the array
    is unsorted and we need ALL occurrences, not just the first.
    """
    # TODO: Implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Find Minimum in Unsorted Array
# ---------------------------------------------------------------------------

def find_minimum(arr):
    """Find and return the minimum value in an unsorted array.

    Return None if the array is empty.

    This requires linear search — you cannot do better than O(n) on
    unsorted data. Think about why: to guarantee you have the minimum,
    you must examine every element. Skipping any element means it
    could have been the minimum.
    """
    # TODO: Implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 6: Binary Search — Find Insertion Point
# ---------------------------------------------------------------------------

def find_insertion_point(arr, target):
    """Find the index where target should be inserted to keep arr sorted.

    If target already exists in arr, return the index of the existing element.
    If target does not exist, return the index where it would be inserted.

    Example:
        arr = [1, 3, 5, 7, 9]
        find_insertion_point(arr, 5) → 2 (already exists at index 2)
        find_insertion_point(arr, 6) → 3 (would be inserted at index 3)
        find_insertion_point(arr, 0) → 0 (would be inserted at index 0)
        find_insertion_point(arr, 10) → 5 (would be inserted at end)

    Hint: this is binary search, but when the element is not found,
    lo is exactly the insertion point. Think about why.
    """
    # TODO: Implement this
    pass


# ---------------------------------------------------------------------------
# Exercise 7: Search in Sorted Matrix (CHALLENGE)
# ---------------------------------------------------------------------------

def search_matrix(matrix, target):
    """Search for target in a matrix where:
    - Each row is sorted in ascending order
    - The first element of each row is greater than the last element
      of the previous row

    Return (row, col) tuple if found, or (-1, -1) if not found.

    Example:
        matrix = [
            [1,  3,  5,  7],
            [10, 11, 16, 20],
            [23, 30, 34, 60]
        ]
        search_matrix(matrix, 16) → (1, 2)

    Hint: treat the 2D matrix as a flattened 1D sorted array.
    If the matrix has m rows and n cols, element at flat index i
    is at row i // n, col i % n.
    """
    # TODO: Implement this
    pass


# ===========================================================================
# TEST RUNNER
# ===========================================================================

def run_tests():
    """Run all test cases and report results."""
    print("Day 19 Practice: Search Implementations")
    print("=" * 60)

    all_passed = True

    # --- Exercise 1: Linear Search ---
    print("\n  Exercise 1: Linear Search")
    tests_1 = [
        ([4, 2, 7, 1, 9], 7, 2),
        ([4, 2, 7, 1, 9], 4, 0),
        ([4, 2, 7, 1, 9], 9, 4),
        ([4, 2, 7, 1, 9], 5, -1),
        ([], 1, -1),
        ([1], 1, 0),
        ([1], 2, -1),
        ([3, 3, 3, 3], 3, 0),  # returns first occurrence
    ]
    for arr, target, expected in tests_1:
        result = linear_search(arr, target)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        print(f"    linear_search({arr}, {target}) = {result}  [{status}]")

    # --- Exercise 2: Binary Search (Iterative) ---
    print("\n  Exercise 2: Binary Search (Iterative)")
    tests_2 = [
        ([1, 3, 5, 7, 9], 5, 2),
        ([1, 3, 5, 7, 9], 1, 0),
        ([1, 3, 5, 7, 9], 9, 4),
        ([1, 3, 5, 7, 9], 4, -1),
        ([1, 3, 5, 7, 9], 0, -1),
        ([1, 3, 5, 7, 9], 10, -1),
        ([], 1, -1),
        ([5], 5, 0),
        ([5], 3, -1),
        ([2, 4], 2, 0),
        ([2, 4], 4, 1),
        ([2, 4], 3, -1),
    ]
    for arr, target, expected in tests_2:
        result = binary_search(arr, target)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        print(f"    binary_search({arr}, {target}) = {result}  [{status}]")

    # --- Exercise 3: Binary Search (Recursive) ---
    print("\n  Exercise 3: Binary Search (Recursive)")
    for arr, target, expected in tests_2:
        result = binary_search_recursive(arr, target)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        print(f"    binary_search_recursive({arr}, {target}) = {result}  [{status}]")

    # --- Exercise 4: Count Occurrences ---
    print("\n  Exercise 4: Count Occurrences")
    tests_4 = [
        ([1, 3, 5, 3, 7, 3, 9], 3, 3),
        ([1, 3, 5, 3, 7, 3, 9], 1, 1),
        ([1, 3, 5, 3, 7, 3, 9], 10, 0),
        ([], 1, 0),
        ([5, 5, 5, 5, 5], 5, 5),
    ]
    for arr, target, expected in tests_4:
        result = count_occurrences(arr, target)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        print(f"    count_occurrences({arr}, {target}) = {result}  [{status}]")

    # --- Exercise 5: Find Minimum ---
    print("\n  Exercise 5: Find Minimum")
    tests_5 = [
        ([4, 2, 7, 1, 9], 1),
        ([10], 10),
        ([5, 3, 8, 1, 2], 1),
        ([-3, -1, -7, -2], -7),
        ([], None),
    ]
    for arr, expected in tests_5:
        result = find_minimum(arr)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        print(f"    find_minimum({arr}) = {result}  [{status}]")

    # --- Exercise 6: Insertion Point ---
    print("\n  Exercise 6: Find Insertion Point")
    tests_6 = [
        ([1, 3, 5, 7, 9], 5, 2),
        ([1, 3, 5, 7, 9], 6, 3),
        ([1, 3, 5, 7, 9], 0, 0),
        ([1, 3, 5, 7, 9], 10, 5),
        ([1, 3, 5, 7, 9], 1, 0),
        ([1, 3, 5, 7, 9], 9, 4),
        ([], 5, 0),
        ([5], 3, 0),
        ([5], 7, 1),
    ]
    for arr, target, expected in tests_6:
        result = find_insertion_point(arr, target)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        print(f"    find_insertion_point({arr}, {target}) = {result}  [{status}]")

    # --- Exercise 7: Search Matrix ---
    print("\n  Exercise 7: Search in Sorted Matrix (CHALLENGE)")
    matrix = [
        [1, 3, 5, 7],
        [10, 11, 16, 20],
        [23, 30, 34, 60]
    ]
    tests_7 = [
        (matrix, 16, (1, 2)),
        (matrix, 1, (0, 0)),
        (matrix, 60, (2, 3)),
        (matrix, 11, (1, 1)),
        (matrix, 15, (-1, -1)),
        (matrix, 0, (-1, -1)),
        (matrix, 100, (-1, -1)),
        ([], 1, (-1, -1)),
    ]
    for mat, target, expected in tests_7:
        result = search_matrix(mat, target)
        status = "PASS" if result == expected else f"FAIL (got {result}, expected {expected})"
        if result != expected:
            all_passed = False
        mat_desc = f"{len(mat)}x{len(mat[0]) if mat else 0} matrix" if mat else "empty"
        print(f"    search_matrix({mat_desc}, {target}) = {result}  [{status}]")

    # --- Summary ---
    print("\n" + "=" * 60)
    if all_passed:
        print("  ALL TESTS PASSED!")
    else:
        print("  Some tests failed. Keep working — check your boundary conditions.")
    print("=" * 60)

    return all_passed


# ===========================================================================
# SOLUTIONS — Do not read until you have attempted all exercises
# ===========================================================================

SOLUTIONS = """
╔══════════════════════════════════════════════════════════════╗
║                        SOLUTIONS                            ║
╚══════════════════════════════════════════════════════════════╝

Exercise 1: Linear Search
    def linear_search(arr, target):
        for i in range(len(arr)):
            if arr[i] == target:
                return i
        return -1

Exercise 2: Binary Search (Iterative)
    def binary_search(arr, target):
        lo, hi = 0, len(arr) - 1
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1

Exercise 3: Binary Search (Recursive)
    def binary_search_recursive(arr, target, lo=None, hi=None):
        if lo is None:
            lo, hi = 0, len(arr) - 1
        if lo > hi:
            return -1
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            return binary_search_recursive(arr, target, mid + 1, hi)
        else:
            return binary_search_recursive(arr, target, lo, mid - 1)

Exercise 4: Count Occurrences
    def count_occurrences(arr, target):
        count = 0
        for x in arr:
            if x == target:
                count += 1
        return count

Exercise 5: Find Minimum
    def find_minimum(arr):
        if not arr:
            return None
        minimum = arr[0]
        for i in range(1, len(arr)):
            if arr[i] < minimum:
                minimum = arr[i]
        return minimum

Exercise 6: Find Insertion Point
    def find_insertion_point(arr, target):
        lo, hi = 0, len(arr) - 1
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return lo  # lo is the insertion point when element not found

Exercise 7: Search Matrix
    def search_matrix(matrix, target):
        if not matrix or not matrix[0]:
            return (-1, -1)
        rows, cols = len(matrix), len(matrix[0])
        lo, hi = 0, rows * cols - 1
        while lo <= hi:
            mid = lo + (hi - lo) // 2
            row, col = mid // cols, mid % cols
            if matrix[row][col] == target:
                return (row, col)
            elif matrix[row][col] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return (-1, -1)
"""


def show_solutions():
    """Print solutions after test run."""
    print("\nWould you like to see solutions? Scroll down...\n")
    print(SOLUTIONS)


if __name__ == "__main__":
    passed = run_tests()
    if not passed:
        show_solutions()
    else:
        print("\n  All exercises complete! Run 'searching.py' for the full demo.")
