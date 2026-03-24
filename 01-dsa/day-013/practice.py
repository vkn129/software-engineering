"""
Day 13: Practice -- Induction & Loop Invariants
================================================

Fill in the TODO sections. Each exercise asks you to either write a loop
invariant, prove correctness using the three-part framework, or identify
a bug by analyzing which part of the invariant is violated.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Write the Loop Invariant for Linear Search
# =============================================================================

def linear_search(arr, target):
    """Find the index of target in arr, or return -1 if not found.

    YOUR TASK: Fill in the loop invariant in the comments below, then
    implement the function so the invariant holds.

    LOOP INVARIANT:
        # TODO: State the invariant here.
        # Hint: What can you say about arr[0..i-1] at the start of
        # iteration i?

    INITIALIZATION:
        # TODO: Why is the invariant true before the loop starts (i=0)?

    MAINTENANCE:
        # TODO: If the invariant holds at iteration i, why does it hold
        # at iteration i+1?

    TERMINATION:
        # TODO: What happens when the loop exits? How does the invariant
        # + exit condition give you the postcondition?

    Examples:
        linear_search([3, 1, 4, 1, 5], 4) -> 2
        linear_search([3, 1, 4, 1, 5], 9) -> -1
        linear_search([], 1)               -> -1
    """
    # TODO: Implement linear search and verify the invariant holds
    pass


# =============================================================================
# Exercise 2: Prove Insertion Sort by Writing Invariant Checks
# =============================================================================

def insertion_sort_with_proof(arr):
    """Sort arr using insertion sort. At each step, assert the invariant.

    YOUR TASK: Fill in the invariant assertion inside the loop.
    The function should raise AssertionError if the invariant is violated.

    INVARIANT: At the start of iteration i (outer loop), arr[0..i-1]
    is sorted and is a permutation of the original arr[0..i-1].

    Examples:
        insertion_sort_with_proof([5, 3, 1, 4, 2]) -> [1, 2, 3, 4, 5]
        insertion_sort_with_proof([1])              -> [1]
        insertion_sort_with_proof([])               -> []
    """
    arr = arr.copy()
    n = len(arr)
    original = arr.copy()

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

        # TODO: Assert the loop invariant here.
        # Check two things:
        # 1. arr[0..i] is sorted
        # 2. arr[0..i] is a permutation of original[0..i]
        # (Hint: sorted(arr[:i+1]) == sorted(original[:i+1]) checks permutation)
        pass

    return arr


# =============================================================================
# Exercise 3: Find the Bug Using Invariant Analysis
# =============================================================================

def buggy_binary_search(arr, target):
    """This binary search has a bug. Find it using invariant analysis.

    INVARIANT: If target is in arr, then target is in arr[lo..hi].

    YOUR TASK:
    1. Run this on the test cases below.
    2. Identify which part of the invariant framework is violated
       (initialization, maintenance, or termination).
    3. Fix the bug in fixed_binary_search below.

    The bug is subtle -- it does not cause wrong answers for all inputs,
    only for specific ones.
    """
    lo, hi = 0, len(arr) - 1

    while lo <= hi:
        mid = (lo + hi) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid  # <-- Is this correct? Analyze using the invariant.

    return -1


def fixed_binary_search(arr, target):
    """Fix the bug from buggy_binary_search.

    YOUR TASK: Implement the correct version and explain in a comment
    which invariant property was violated and why the fix restores it.

    Examples:
        fixed_binary_search([1, 3, 5, 7, 9], 5)  -> 2
        fixed_binary_search([1, 3, 5, 7, 9], 1)  -> 0
        fixed_binary_search([1, 3, 5, 7, 9], 9)  -> 4
        fixed_binary_search([1, 3, 5, 7, 9], 4)  -> -1
        fixed_binary_search([2, 4], 2)            -> 0
    """
    # TODO: Fix the bug. Explain which invariant property was violated.
    # YOUR EXPLANATION HERE:
    #
    pass


# =============================================================================
# Exercise 4: Write Invariant for Selection Sort
# =============================================================================

def selection_sort_with_invariant(arr):
    """Sort arr using selection sort with invariant verification.

    YOUR TASK:
    1. State the loop invariant in comments.
    2. Implement selection sort.
    3. Add an assertion that checks the invariant after each iteration.

    LOOP INVARIANT:
        # TODO: State the invariant.
        # Hint: After i iterations, what is true about arr[0..i-1]
        # relative to arr[i..n-1]?

    Examples:
        selection_sort_with_invariant([64, 25, 12, 22, 11]) -> [11, 12, 22, 25, 64]
        selection_sort_with_invariant([1])                   -> [1]
        selection_sort_with_invariant([])                    -> []
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n - 1):
        # TODO: Find the minimum element in arr[i..n-1]
        # TODO: Swap it with arr[i]
        # TODO: Assert the invariant
        pass

    return arr


# =============================================================================
# Exercise 5: Prove Correctness of Exponentiation by Squaring
# =============================================================================

def power_with_proof(base, exp):
    """Compute base^exp using the binary method with invariant checks.

    YOUR TASK: Implement binary exponentiation and verify the invariant
    at each step using assertions.

    INVARIANT: result * base^exp = original_base^original_exp

    After each iteration, assert this invariant holds. Use Python's **
    operator to compute the right side for verification.

    Examples:
        power_with_proof(2, 10) -> 1024
        power_with_proof(3, 0)  -> 1
        power_with_proof(5, 3)  -> 125
        power_with_proof(7, 1)  -> 7
    """
    original_base, original_exp = base, exp
    expected = original_base ** original_exp

    # TODO: Implement binary exponentiation with invariant assertions
    # At each step: assert result * (base ** exp) == expected
    pass


# =============================================================================
# SOLUTIONS (scroll down only after attempting!)
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
#
#
#
# SOLUTIONS BELOW -- Try the exercises first!
#
#
#
#
#


def _solution_linear_search(arr, target):
    """
    LOOP INVARIANT: At the start of iteration i, target is NOT in arr[0..i-1].

    INITIALIZATION (i=0): arr[0..-1] is empty. target is trivially not in
    an empty range. True.

    MAINTENANCE: At iteration i, we check arr[i].
    - If arr[i] == target, we return i. Correct.
    - If arr[i] != target, then target is not in arr[0..i] (by invariant,
      not in arr[0..i-1], and arr[i] != target). So invariant holds for i+1.

    TERMINATION: When i = n, the invariant says target is not in arr[0..n-1],
    which is the entire array. Return -1.
    """
    for i in range(len(arr)):
        # Invariant: target is not in arr[0..i-1]
        if arr[i] == target:
            return i
    return -1


def _solution_insertion_sort_with_proof(arr):
    arr = arr.copy()
    n = len(arr)
    original = arr.copy()

    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

        # Invariant check: arr[0..i] is sorted and is a permutation of original[0..i]
        assert arr[:i + 1] == sorted(arr[:i + 1]), \
            f"Not sorted at i={i}: {arr[:i + 1]}"
        assert sorted(arr[:i + 1]) == sorted(original[:i + 1]), \
            f"Not a permutation at i={i}"

    return arr


def _solution_fixed_binary_search(arr, target):
    """
    BUG ANALYSIS: hi = mid violates TERMINATION.
    When lo == hi == mid, setting hi = mid does not shrink the range.
    The loop condition lo <= hi is still true, so we loop forever.

    It also weakens MAINTENANCE: we know arr[mid] > target, so target
    cannot be at index mid. But hi = mid keeps mid in the search range,
    violating the invariant's precision (though not its truth).

    FIX: hi = mid - 1. This excludes mid (which we know is not target)
    and strictly shrinks the range, guaranteeing termination.
    """
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1  # FIX: exclude mid
    return -1


def _solution_selection_sort_with_invariant(arr):
    """
    LOOP INVARIANT: After i iterations, arr[0..i-1] contains the i smallest
    elements of the original array in sorted order, and every element in
    arr[0..i-1] <= every element in arr[i..n-1].

    INITIALIZATION (i=0): arr[0..-1] is empty. Trivially true.

    MAINTENANCE: We find the minimum of arr[i..n-1] and swap it into
    position i. Now arr[0..i] contains the (i+1) smallest elements in
    sorted order (the new element is >= all of arr[0..i-1] because those
    were the i smallest, and it is <= all of arr[i+1..n-1] because it
    was the minimum of arr[i..n-1]).

    TERMINATION: i goes from 0 to n-2. After n-1 iterations, arr[0..n-2]
    are the (n-1) smallest in sorted order, so arr[n-1] must be the largest.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

        # Invariant: arr[0..i] is sorted and all <= arr[i+1..n-1]
        assert arr[:i + 1] == sorted(arr[:i + 1]), f"Not sorted at i={i}"
        if i + 1 < n:
            assert arr[i] <= min(arr[i + 1:]), \
                f"Boundary violation at i={i}: {arr[i]} > {min(arr[i + 1:])}"

    return arr


def _solution_power_with_proof(base, exp):
    original_base, original_exp = base, exp
    expected = original_base ** original_exp
    result = 1

    while exp > 0:
        # Verify invariant: result * base^exp == original_base^original_exp
        assert result * (base ** exp) == expected, \
            f"Invariant violated: {result} * {base}^{exp} != {expected}"

        if exp % 2 == 1:
            result *= base
            exp -= 1
        else:
            base *= base
            exp //= 2

    assert result == expected, f"Final check: {result} != {expected}"
    return result


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests. Uses solutions if student functions return None."""
    print("=" * 60)
    print("RUNNING TESTS")
    print("=" * 60)

    all_passed = True

    # --- Exercise 1: Linear Search ---
    print("\n--- Exercise 1: Linear Search ---")
    test_cases_1 = [
        ([3, 1, 4, 1, 5], 4, 2),
        ([3, 1, 4, 1, 5], 9, -1),
        ([], 1, -1),
        ([7], 7, 0),
        ([1, 2, 3, 4, 5], 5, 4),
    ]
    for arr, target, expected in test_cases_1:
        result = linear_search(arr, target)
        if result is None:
            result = _solution_linear_search(arr, target)
            tag = "(solution)"
        else:
            tag = "(yours)"
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"  {status} {tag}: linear_search({arr}, {target}) = {result} (expected {expected})")

    # --- Exercise 2: Insertion Sort with Proof ---
    print("\n--- Exercise 2: Insertion Sort with Proof ---")
    test_cases_2 = [
        [5, 3, 1, 4, 2],
        [1],
        [],
        [3, 3, 3],
        [5, 4, 3, 2, 1],
    ]
    for arr in test_cases_2:
        try:
            result = insertion_sort_with_proof(arr)
            if result is None or result == arr:
                result = _solution_insertion_sort_with_proof(arr)
                tag = "(solution)"
            else:
                tag = "(yours)"
            expected = sorted(arr)
            status = "PASS" if result == expected else "FAIL"
            if status == "FAIL":
                all_passed = False
            print(f"  {status} {tag}: insertion_sort({arr}) = {result}")
        except AssertionError as e:
            print(f"  FAIL: Invariant violated for {arr}: {e}")
            all_passed = False

    # --- Exercise 3: Fix Binary Search ---
    print("\n--- Exercise 3: Fixed Binary Search ---")
    test_cases_3 = [
        ([1, 3, 5, 7, 9], 5, 2),
        ([1, 3, 5, 7, 9], 1, 0),
        ([1, 3, 5, 7, 9], 9, 4),
        ([1, 3, 5, 7, 9], 4, -1),
        ([2, 4], 2, 0),
        ([], 1, -1),
    ]

    print("  Testing buggy version (may hang on some inputs, skipping hang-prone):")
    safe_cases = [([1, 3, 5, 7, 9], 5, 2), ([1, 3, 5, 7, 9], 4, -1)]
    # The buggy version hangs when target < arr[mid] and lo == hi == mid,
    # so we only test safe cases to demonstrate
    for arr, target, expected in safe_cases:
        result = buggy_binary_search(arr, target)
        status = "PASS" if result == expected else "FAIL"
        print(f"    {status}: buggy_search({arr}, {target}) = {result}")

    print("  Testing fixed version:")
    for arr, target, expected in test_cases_3:
        result = fixed_binary_search(arr, target)
        if result is None:
            result = _solution_fixed_binary_search(arr, target)
            tag = "(solution)"
        else:
            tag = "(yours)"
        status = "PASS" if result == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"    {status} {tag}: fixed_search({arr}, {target}) = {result}")

    # --- Exercise 4: Selection Sort ---
    print("\n--- Exercise 4: Selection Sort with Invariant ---")
    test_cases_4 = [
        [64, 25, 12, 22, 11],
        [1],
        [],
        [3, 1, 4, 1, 5, 9],
    ]
    for arr in test_cases_4:
        try:
            result = selection_sort_with_invariant(arr)
            if result is None or result == arr:
                result = _solution_selection_sort_with_invariant(arr)
                tag = "(solution)"
            else:
                tag = "(yours)"
            expected = sorted(arr)
            status = "PASS" if result == expected else "FAIL"
            if status == "FAIL":
                all_passed = False
            print(f"  {status} {tag}: selection_sort({arr}) = {result}")
        except AssertionError as e:
            print(f"  FAIL: Invariant violated for {arr}: {e}")
            all_passed = False

    # --- Exercise 5: Power with Proof ---
    print("\n--- Exercise 5: Power with Proof ---")
    test_cases_5 = [
        (2, 10, 1024),
        (3, 0, 1),
        (5, 3, 125),
        (7, 1, 7),
        (2, 20, 1048576),
    ]
    for base, exp, expected in test_cases_5:
        try:
            result = power_with_proof(base, exp)
            if result is None:
                result = _solution_power_with_proof(base, exp)
                tag = "(solution)"
            else:
                tag = "(yours)"
            status = "PASS" if result == expected else "FAIL"
            if status == "FAIL":
                all_passed = False
            print(f"  {status} {tag}: power({base}, {exp}) = {result} (expected {expected})")
        except AssertionError as e:
            print(f"  FAIL: Invariant violated for {base}^{exp}: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED -- review the exercises above")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
