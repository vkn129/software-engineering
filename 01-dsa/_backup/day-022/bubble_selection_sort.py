"""
Day 22: Bubble Sort & Selection Sort — Complete Implementation with Visualization

Run: python bubble_selection_sort.py

Covers:
- Bubble sort with early-exit optimization
- Selection sort with minimum-swap strategy
- Step-by-step array state printing after each swap
- Comparison and swap counting
- Stability demonstration
- Performance comparison on different input patterns
"""

import time
import random


# =============================================================================
# BUBBLE SORT
# =============================================================================

def bubble_sort(arr, visualize=False):
    """
    Bubble sort with early-exit optimization.

    Loop invariant: After pass i, the largest i elements occupy their final
    positions at the end of the array.

    Why early exit works: If no swaps occur during a pass, every adjacent pair
    is already in order, meaning the entire array is sorted. This makes bubble
    sort O(n) on already-sorted input — the ONLY O(n^2) sort with this property.
    """
    a = arr[:]  # work on a copy
    n = len(a)
    comparisons = 0
    swaps = 0

    for i in range(n - 1):
        swapped = False

        if visualize:
            print(f"\n  Pass {i + 1} (sorting into position {n - 1 - i}):")

        for j in range(n - 1 - i):
            comparisons += 1

            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True

                if visualize:
                    # Show the swap and current array state
                    marker = ['  '] * n
                    marker[j] = '^^'
                    marker[j + 1] = '^^'
                    print(f"    Swap indices {j},{j + 1}: {a}")
                    print(f"                       {''.join(f'{m:>4}' for m in marker)}")

        if not swapped:
            if visualize:
                print(f"    No swaps — array is sorted! (early exit)")
            break

        if visualize:
            sorted_part = f"  sorted: {a[n - 1 - i:]}" if i < n - 1 else ""
            print(f"    End of pass: {a}{sorted_part}")

    return a, comparisons, swaps


def bubble_sort_no_optimization(arr):
    """Naive bubble sort WITHOUT early exit — always does n-1 passes."""
    a = arr[:]
    n = len(a)
    comparisons = 0
    swaps = 0

    for i in range(n - 1):
        for j in range(n - 1 - i):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1

    return a, comparisons, swaps


# =============================================================================
# SELECTION SORT
# =============================================================================

def selection_sort(arr, visualize=False):
    """
    Selection sort: find the minimum in the unsorted region, swap it into place.

    Loop invariant: After iteration i, positions [0..i-1] contain the i smallest
    elements in sorted order.

    Key property: Always exactly n-1 swaps (or fewer if an element is already
    in position). This makes it ideal when WRITES are expensive.
    """
    a = arr[:]
    n = len(a)
    comparisons = 0
    swaps = 0

    for i in range(n - 1):
        min_idx = i

        # Find minimum in unsorted region [i..n-1]
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[min_idx]:
                min_idx = j

        if min_idx != i:
            if visualize:
                print(f"  Step {i + 1}: min in {a[i:]} is {a[min_idx]} at index {min_idx}")
                print(f"    Swap arr[{i}]={a[i]} with arr[{min_idx}]={a[min_idx]}")

            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1

            if visualize:
                print(f"    Result: {a}  (sorted: {a[:i + 1]})")
        else:
            if visualize:
                print(f"  Step {i + 1}: {a[i]} already in correct position")
                print(f"    Result: {a}  (sorted: {a[:i + 1]})")

    return a, comparisons, swaps


# =============================================================================
# STABILITY DEMONSTRATION
# =============================================================================

def demonstrate_stability():
    """
    Stability means: if two elements are EQUAL by the sort key, they keep their
    original relative order.

    This matters when you sort by multiple criteria. Example: sort students by
    grade, then by name. If the name-sort is stable, students with the same name
    stay in grade-order.
    """
    print("=" * 70)
    print("STABILITY DEMONSTRATION")
    print("=" * 70)

    # We use tuples: (value, label) and sort by value only
    data = [(3, 'A'), (1, 'B'), (3, 'C'), (2, 'D'), (1, 'E')]

    print(f"\nOriginal: {data}")
    print("Sorting by the NUMBER only. Watch what happens to equal elements.\n")

    # --- Bubble sort (stable) ---
    print("BUBBLE SORT (stable):")
    a = data[:]
    n = len(a)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            # Compare ONLY the number (index 0 of tuple)
            if a[j][0] > a[j + 1][0]:
                a[j], a[j + 1] = a[j + 1], a[j]
    print(f"  Result: {a}")
    print(f"  The two 1s: B comes before E (original order preserved)")
    print(f"  The two 3s: A comes before C (original order preserved)")

    # --- Selection sort (unstable) ---
    print("\nSELECTION SORT (unstable):")
    a = data[:]
    n = len(a)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if a[j][0] < a[min_idx][0]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]

    print(f"  Result: {a}")
    # Walk through what happened
    print(f"  Step-by-step on original {data}:")
    a2 = data[:]
    for i in range(len(a2) - 1):
        min_idx = i
        for j in range(i + 1, len(a2)):
            if a2[j][0] < a2[min_idx][0]:
                min_idx = j
        if min_idx != i:
            print(f"    Swap index {i} ({a2[i]}) with index {min_idx} ({a2[min_idx]})")
            a2[i], a2[min_idx] = a2[min_idx], a2[i]
            print(f"    -> {a2}")

    print(f"\n  Notice: The two 1s are now E,B (reversed from original B,E).")
    print(f"  This is because the swap of (1,B) with (3,A) moved B to index 2,")
    print(f"  past E which was at index 4. The long-distance swap broke stability.")


# =============================================================================
# STEP-BY-STEP VISUALIZATION
# =============================================================================

def full_visualization():
    """Show both algorithms working on the same array, step by step."""
    print("=" * 70)
    print("STEP-BY-STEP VISUALIZATION")
    print("=" * 70)

    arr = [5, 3, 8, 1, 2]

    print(f"\nOriginal array: {arr}")

    print(f"\n{'─' * 35}")
    print("BUBBLE SORT:")
    print(f"{'─' * 35}")
    result, comps, swps = bubble_sort(arr, visualize=True)
    print(f"\n  Final: {result}")
    print(f"  Comparisons: {comps}, Swaps: {swps}")

    print(f"\n{'─' * 35}")
    print("SELECTION SORT:")
    print(f"{'─' * 35}")
    result, comps, swps = selection_sort(arr, visualize=True)
    print(f"\n  Final: {result}")
    print(f"  Comparisons: {comps}, Swaps: {swps}")


# =============================================================================
# PERFORMANCE COMPARISON
# =============================================================================

def performance_comparison():
    """Compare bubble sort and selection sort on different input patterns."""
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON (comparisons / swaps)")
    print("=" * 70)

    sizes = [100, 500, 1000]

    for n in sizes:
        print(f"\n  n = {n}:")

        # Already sorted
        arr = list(range(n))
        _, bc, bs = bubble_sort(arr)
        _, sc, ss = selection_sort(arr)
        print(f"    Already sorted:   Bubble({bc:>7} comp, {bs:>7} swap)  "
              f"Selection({sc:>7} comp, {ss:>7} swap)")

        # Reverse sorted
        arr = list(range(n, 0, -1))
        _, bc, bs = bubble_sort(arr)
        _, sc, ss = selection_sort(arr)
        print(f"    Reverse sorted:   Bubble({bc:>7} comp, {bs:>7} swap)  "
              f"Selection({sc:>7} comp, {ss:>7} swap)")

        # Random
        arr = [random.randint(1, n) for _ in range(n)]
        _, bc, bs = bubble_sort(arr)
        _, sc, ss = selection_sort(arr)
        print(f"    Random:           Bubble({bc:>7} comp, {bs:>7} swap)  "
              f"Selection({sc:>7} comp, {ss:>7} swap)")

    print("\n  Key takeaway:")
    print("  - Bubble sort with early exit: O(n) comparisons on sorted input!")
    print("  - Selection sort: ALWAYS n(n-1)/2 comparisons, but max n-1 swaps")
    print("  - Selection sort wins when writes >> reads (e.g., flash memory)")


# =============================================================================
# CORRECTNESS VERIFICATION
# =============================================================================

def verify_correctness():
    """Test both sorts against Python's built-in sort on random inputs."""
    print("\n" + "=" * 70)
    print("CORRECTNESS VERIFICATION")
    print("=" * 70)

    test_cases = [
        [],
        [1],
        [2, 1],
        [1, 2, 3],
        [3, 2, 1],
        [5, 5, 5, 5],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
    ]

    # Add random test cases
    for _ in range(10):
        test_cases.append([random.randint(-100, 100) for _ in range(random.randint(0, 50))])

    all_pass = True
    for tc in test_cases:
        expected = sorted(tc)
        bubble_result, _, _ = bubble_sort(tc)
        selection_result, _, _ = selection_sort(tc)

        if bubble_result != expected:
            print(f"  FAIL bubble sort: {tc} -> {bubble_result} (expected {expected})")
            all_pass = False
        if selection_result != expected:
            print(f"  FAIL selection sort: {tc} -> {selection_result} (expected {expected})")
            all_pass = False

    if all_pass:
        print(f"\n  All {len(test_cases)} test cases passed for both algorithms!")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    full_visualization()
    demonstrate_stability()
    performance_comparison()
    verify_correctness()
