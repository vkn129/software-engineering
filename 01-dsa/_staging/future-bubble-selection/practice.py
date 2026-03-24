"""
Day 22 Practice: Bubble Sort & Selection Sort

Complete each TODO. Run with: python practice.py

All tests at the bottom will verify your implementations.
"""


def bubble_sort_with_counts(arr):
    """
    TODO 1: Implement bubble sort with the early-exit optimization.

    Return a tuple: (sorted_array, comparison_count, swap_count)

    The early-exit optimization: if a full pass makes zero swaps, the array
    is already sorted — break out of the outer loop immediately.

    Work on a COPY of arr (don't modify the original).
    """
    a = arr[:]
    n = len(a)
    comparisons = 0
    swaps = 0

    # TODO: Implement bubble sort here
    # Outer loop: passes 0 to n-2
    #   Track whether any swap happened this pass
    #   Inner loop: compare adjacent elements in unsorted region
    #     If out of order, swap and increment swap counter
    #   If no swaps happened, break early

    return a, comparisons, swaps


def selection_sort_with_counts(arr):
    """
    TODO 2: Implement selection sort.

    Return a tuple: (sorted_array, comparison_count, swap_count)

    Work on a COPY of arr.
    """
    a = arr[:]
    n = len(a)
    comparisons = 0
    swaps = 0

    # TODO: Implement selection sort here
    # For each position i from 0 to n-2:
    #   Find the index of the minimum element in a[i..n-1]
    #   If min_idx != i, swap a[i] and a[min_idx]

    return a, comparisons, swaps


def count_exact_operations(arr):
    """
    TODO 3: For bubble sort (with early exit) on the given array,
    return the EXACT number of (comparisons, swaps, passes).

    A "pass" is one complete traversal of the inner loop.
    """
    a = arr[:]
    comparisons = 0
    swaps = 0
    passes = 0

    # TODO: Modify your bubble sort to also count passes

    return comparisons, swaps, passes


def stable_selection_sort(arr, key=None):
    """
    TODO 4: Implement a STABLE version of selection sort.

    Regular selection sort is unstable because swapping can move equal elements
    past each other. To make it stable:

    Instead of SWAPPING the minimum into position i, SHIFT all elements from
    position i to min_idx-1 one position to the right, then place the minimum
    at position i. This is like an insertion — it preserves relative order.

    If key is provided, use key(element) for comparisons.
    If key is None, compare elements directly.

    Work on a COPY of arr.
    """
    a = arr[:]
    n = len(a)

    # TODO: Implement stable selection sort
    # Hint: Instead of a[i], a[min_idx] = a[min_idx], a[i]
    # Do: save = a[min_idx], shift a[i:min_idx] right by 1, place save at a[i]

    return a


# =============================================================================
# TESTS — Do not modify below this line
# =============================================================================

def run_tests():
    import random

    print("Testing bubble_sort_with_counts...")
    # Basic correctness
    assert bubble_sort_with_counts([])[0] == []
    assert bubble_sort_with_counts([1])[0] == [1]
    assert bubble_sort_with_counts([2, 1])[0] == [1, 2]
    assert bubble_sort_with_counts([3, 2, 1])[0] == [1, 2, 3]
    assert bubble_sort_with_counts([1, 2, 3])[0] == [1, 2, 3]

    # Early exit: sorted array should have n-1 comparisons and 0 swaps
    _, comps, swps = bubble_sort_with_counts([1, 2, 3, 4, 5])
    assert comps == 4, f"Sorted array: expected 4 comparisons (one pass), got {comps}"
    assert swps == 0, f"Sorted array: expected 0 swaps, got {swps}"

    # Random correctness
    for _ in range(20):
        arr = [random.randint(-50, 50) for _ in range(random.randint(0, 30))]
        assert bubble_sort_with_counts(arr)[0] == sorted(arr)
    print("  PASSED!")

    print("Testing selection_sort_with_counts...")
    assert selection_sort_with_counts([])[0] == []
    assert selection_sort_with_counts([1])[0] == [1]
    assert selection_sort_with_counts([2, 1])[0] == [1, 2]

    # Selection sort always does n(n-1)/2 comparisons
    _, comps, _ = selection_sort_with_counts([1, 2, 3, 4, 5])
    assert comps == 10, f"Expected 10 comparisons for n=5, got {comps}"

    # Swaps should be at most n-1
    _, _, swps = selection_sort_with_counts([5, 4, 3, 2, 1])
    assert swps <= 4, f"Expected at most 4 swaps for n=5, got {swps}"

    for _ in range(20):
        arr = [random.randint(-50, 50) for _ in range(random.randint(0, 30))]
        assert selection_sort_with_counts(arr)[0] == sorted(arr)
    print("  PASSED!")

    print("Testing count_exact_operations...")
    c, s, p = count_exact_operations([1, 2, 3, 4, 5])
    assert c == 4 and s == 0 and p == 1, f"Sorted [1..5]: expected (4,0,1), got ({c},{s},{p})"

    c, s, p = count_exact_operations([2, 1])
    assert c == 1 and s == 1 and p == 1, f"[2,1]: expected (1,1,1), got ({c},{s},{p})"
    print("  PASSED!")

    print("Testing stable_selection_sort...")
    # Basic correctness
    assert stable_selection_sort([3, 1, 2]) == [1, 2, 3]
    assert stable_selection_sort([]) == []

    # Stability test: sort tuples by first element only
    data = [(3, 'A'), (1, 'B'), (3, 'C'), (2, 'D'), (1, 'E')]
    result = stable_selection_sort(data, key=lambda x: x[0])
    expected = [(1, 'B'), (1, 'E'), (2, 'D'), (3, 'A'), (3, 'C')]
    assert result == expected, f"Stability failed: {result} != {expected}"

    # Another stability test
    data2 = [(2, 'x'), (1, 'y'), (2, 'z'), (1, 'w')]
    result2 = stable_selection_sort(data2, key=lambda x: x[0])
    expected2 = [(1, 'y'), (1, 'w'), (2, 'x'), (2, 'z')]
    assert result2 == expected2, f"Stability failed: {result2} != {expected2}"
    print("  PASSED!")

    print("\nAll tests passed!")


if __name__ == "__main__":
    run_tests()
