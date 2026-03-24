"""
Day 13: Induction & Loop Invariants -- Proving Algorithms Correct
=================================================================

This file demonstrates how to formally prove algorithms correct using
loop invariants. For each algorithm, we state the invariant, prove
initialization/maintenance/termination, and run demonstrations that
make the invariant visible at each iteration.

The goal is not just to write correct code, but to KNOW it is correct
and be able to explain why to another engineer.

Run: python induction_invariants.py
"""


# ===========================================================================
# SECTION 1: Mathematical Induction -- Foundations
# ===========================================================================

print("=" * 70)
print("SECTION 1: Mathematical Induction")
print("=" * 70)


def sum_by_formula(n):
    """Compute sum(1..n) using the closed-form formula.

    PROOF BY WEAK INDUCTION:
    Claim: sum(1..n) = n*(n+1)/2 for all n >= 1.

    Base case (n=1): 1 = 1*2/2 = 1.  Holds.

    Inductive step: Assume sum(1..k) = k*(k+1)/2.
    Then sum(1..k+1) = sum(1..k) + (k+1)
                     = k*(k+1)/2 + (k+1)
                     = (k+1)*(k/2 + 1)
                     = (k+1)*(k+2)/2.  QED.

    Why this matters: the formula gives O(1) computation instead of O(n).
    But we need the PROOF to trust the formula for all n, not just the
    values we tested.
    """
    return n * (n + 1) // 2


def sum_by_loop(n):
    """Compute sum(1..n) by looping, with invariant checking."""
    total = 0
    for i in range(1, n + 1):
        total += i
        # Invariant: total = i*(i+1)/2 after adding i
        assert total == i * (i + 1) // 2, f"Invariant violated at i={i}"
    return total


print("\nProof that sum(1..n) = n*(n+1)/2:")
for n in [1, 5, 10, 100, 1000]:
    by_formula = sum_by_formula(n)
    by_loop = sum_by_loop(n)
    print(f"  n={n:>4}: formula={by_formula:>6}, loop={by_loop:>6}, match={by_formula == by_loop}")


# ---------------------------------------------------------------------------
# Strong Induction Example: Fibonacci
# ---------------------------------------------------------------------------

print("\n--- Strong Induction: Fibonacci Closed Form (Binet's Approximation) ---")


def fibonacci_recursive(n):
    """Compute F(n) recursively.

    PROOF BY STRONG INDUCTION that F(n) = F(n-1) + F(n-2):
    Base cases: F(0) = 0, F(1) = 1.

    Inductive step (strong form): Assume F(j) is correct for ALL j <= k
    where k >= 1. Then F(k+1) = F(k) + F(k-1), which are both correct
    by the inductive hypothesis (since k <= k and k-1 <= k).

    We need STRONG induction because F(k+1) depends on two previous
    values, not just the immediately preceding one.
    """
    if n <= 1:
        return n
    # Iterative to avoid stack overflow
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


# Verify Fibonacci values
print(f"  F(0)..F(10): {[fibonacci_recursive(i) for i in range(11)]}")


# ===========================================================================
# SECTION 2: Binary Search -- Proving It Correct
# ===========================================================================

print("\n" + "=" * 70)
print("SECTION 2: Binary Search with Loop Invariant")
print("=" * 70)


def binary_search_proven(arr, target, verbose=False):
    """Binary search with formal correctness proof.

    PRECONDITION: arr is sorted in non-decreasing order.
    POSTCONDITION: returns index i where arr[i] == target, or -1 if not found.

    LOOP INVARIANT: If target exists in arr, then target is in arr[lo..hi]
    (inclusive on both ends).

    INITIALIZATION: lo=0, hi=len(arr)-1. The entire array is arr[lo..hi],
    so if target exists, it is certainly in this range.

    MAINTENANCE: We compute mid = (lo + hi) // 2.
    - If arr[mid] == target: we found it, return mid.
    - If arr[mid] < target: target cannot be in arr[lo..mid] (because arr
      is sorted and all elements arr[lo..mid] <= arr[mid] < target).
      So we set lo = mid + 1. The invariant holds: if target exists,
      it is in arr[mid+1..hi] = arr[new_lo..hi].
    - If arr[mid] > target: symmetrically, set hi = mid - 1.

    TERMINATION: The quantity (hi - lo) decreases by at least 1 each
    iteration (because we always exclude mid). Since hi - lo >= 0 is
    required for the loop to continue, and it strictly decreases, the
    loop must terminate.

    CORRECTNESS AT TERMINATION: If we exit the loop (lo > hi), the
    invariant says "if target exists, it is in arr[lo..hi]" but this
    range is empty. Therefore target does not exist. Return -1.
    """
    lo, hi = 0, len(arr) - 1

    iteration = 0
    while lo <= hi:
        mid = lo + (hi - lo) // 2  # Avoids integer overflow in other languages

        if verbose:
            print(f"  Iter {iteration}: lo={lo}, hi={hi}, mid={mid}, "
                  f"arr[mid]={arr[mid]}, searching for {target}")
            print(f"    Invariant: target (if exists) is in arr[{lo}..{hi}]")

        if arr[mid] == target:
            if verbose:
                print(f"    Found target at index {mid}")
            return mid
        elif arr[mid] < target:
            lo = mid + 1  # Exclude left half including mid
        else:
            hi = mid - 1  # Exclude right half including mid

        iteration += 1

    if verbose:
        print(f"  Loop exited: lo={lo} > hi={hi}, range is empty. Target not found.")
    return -1


arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(f"\nArray: {arr}")
print(f"\nSearching for 23:")
result = binary_search_proven(arr, 23, verbose=True)
print(f"Result: index {result}")

print(f"\nSearching for 50 (not present):")
result = binary_search_proven(arr, 50, verbose=True)
print(f"Result: {result}")


# ---------------------------------------------------------------------------
# The classic off-by-one bug and which invariant part it violates
# ---------------------------------------------------------------------------

print("\n--- The Classic Binary Search Bug ---")
print("  Bug: using hi = mid instead of hi = mid - 1")
print("  This violates TERMINATION: if lo == hi == mid, then setting")
print("  hi = mid does not shrink the range, causing an infinite loop.")
print("  The maintenance of the invariant also weakens: mid is NOT excluded,")
print("  so we might repeatedly check the same element.\n")


# ===========================================================================
# SECTION 3: Insertion Sort -- Proving It Correct
# ===========================================================================

print("=" * 70)
print("SECTION 3: Insertion Sort with Loop Invariant")
print("=" * 70)


def insertion_sort_proven(arr, verbose=False):
    """Insertion sort with formal correctness proof.

    LOOP INVARIANT (outer loop, index i):
    At the start of each iteration, arr[0..i-1] is a sorted permutation
    of the original arr[0..i-1].

    INITIALIZATION (i=1): arr[0..0] is a single element, which is trivially
    sorted and is a permutation of itself.

    MAINTENANCE: The inner loop shifts elements right to make room for
    arr[i] (called 'key'). After insertion, arr[0..i] is sorted and contains
    exactly the original elements (we only moved elements, never created or
    destroyed any).

    INNER LOOP INVARIANT (index j, going from i-1 down to 0):
    arr[j+1..i] contains the elements that were originally in arr[j..i-1],
    each shifted right by one position, and key < all of arr[j+1..i].

    TERMINATION (outer): i goes from 1 to n-1, incrementing by 1. Terminates.
    TERMINATION (inner): j decreases by 1 each iteration and stops at -1
    or when arr[j] <= key.

    CORRECTNESS AT TERMINATION: When i = n, the invariant says arr[0..n-1]
    is sorted and is a permutation of the original array. That is exactly
    the postcondition of sorting.
    """
    arr = arr.copy()  # Don't mutate input
    n = len(arr)
    original_sorted = sorted(arr)  # For verification

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        # Inner loop: shift elements right to make room for key
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

        # Verify invariant: arr[0..i] is sorted
        assert arr[:i + 1] == sorted(arr[:i + 1]), \
            f"Invariant violated at i={i}: arr[0..{i}] = {arr[:i + 1]} is not sorted"

        if verbose:
            print(f"  i={i}: inserted {key} -> {arr}")
            print(f"    Invariant: arr[0..{i}] = {arr[:i + 1]} is sorted: True")

    # Verify postcondition
    assert arr == original_sorted, "Postcondition violated: result is not sorted"
    return arr


data = [64, 25, 12, 22, 11]
print(f"\nOriginal: {data}")
result = insertion_sort_proven(data, verbose=True)
print(f"Sorted:   {result}")


# ===========================================================================
# SECTION 4: Bubble Sort -- Proving It Correct
# ===========================================================================

print("\n" + "=" * 70)
print("SECTION 4: Bubble Sort with Loop Invariant")
print("=" * 70)


def bubble_sort_proven(arr, verbose=False):
    """Bubble sort with formal correctness proof.

    LOOP INVARIANT (outer loop, pass i, i = 0, 1, 2, ...):
    After pass i, the largest (i+1) elements are in their correct final
    positions at the end of the array. That is, arr[n-1-i..n-1] contains
    the (i+1) largest elements in sorted order.

    INITIALIZATION (before pass 0): No passes done, no claim about any
    suffix. Trivially true (empty suffix).

    MAINTENANCE: During pass i, we bubble from index 0 to n-1-i. The
    largest element in arr[0..n-1-i] "bubbles up" to position n-1-i
    through adjacent swaps. After the pass, arr[n-1-i] holds the largest
    of arr[0..n-1-i], which is the (i+1)-th largest overall. Combined
    with the invariant that arr[n-i..n-1] was already correct, now
    arr[n-1-i..n-1] is correct.

    TERMINATION: i goes from 0 to n-2. After n-1 passes, the loop ends.
    The quantity (n - 1 - i) decreases each pass.

    CORRECTNESS AT TERMINATION: After pass n-2 (the last pass), the
    invariant guarantees arr[1..n-1] are in their final positions. Since
    arr[0] is the only remaining element and all larger elements are to
    its right, arr[0] is also correct. The entire array is sorted.
    """
    arr = arr.copy()
    n = len(arr)

    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True

        # Verify invariant: arr[n-1-i..n-1] are the largest (i+1) elements, sorted
        suffix = arr[n - 1 - i:]
        assert suffix == sorted(suffix), f"Invariant violated at pass {i}"

        if verbose:
            print(f"  Pass {i}: {arr}")
            print(f"    Invariant: last {i + 1} elements {suffix} are in final position")

        # Early termination optimization (does not affect correctness)
        if not swapped:
            if verbose:
                print(f"    No swaps in pass {i} -- array is sorted, terminating early.")
            break

    return arr


data = [64, 34, 25, 12, 22, 11, 90]
print(f"\nOriginal: {data}")
result = bubble_sort_proven(data, verbose=True)
print(f"Sorted:   {result}")


# ===========================================================================
# SECTION 5: Euclid's GCD -- Proving It Correct
# ===========================================================================

print("\n" + "=" * 70)
print("SECTION 5: Euclid's GCD with Loop Invariant")
print("=" * 70)


def gcd_proven(a, b, verbose=False):
    """Euclid's GCD algorithm with formal correctness proof.

    PRECONDITION: a >= 0, b >= 0, not both zero.
    POSTCONDITION: returns gcd(a, b).

    LOOP INVARIANT: gcd(a, b) = gcd(original_a, original_b) at the start
    of every iteration.

    INITIALIZATION: a = original_a, b = original_b. Trivially true.

    MAINTENANCE: We replace (a, b) with (b, a % b).
    Key mathematical fact: gcd(a, b) = gcd(b, a mod b).
    Proof of this fact: Let d = gcd(a, b). Then d | a and d | b.
    Since a mod b = a - (a // b) * b, we have d | (a mod b).
    So d | b and d | (a mod b), meaning d | gcd(b, a mod b).
    Conversely, let e = gcd(b, a mod b). Then e | b and e | (a mod b).
    Since a = (a // b) * b + (a mod b), we have e | a.
    So e | a and e | b, meaning e | gcd(a, b). Therefore d = e.

    TERMINATION: b strictly decreases each iteration.
    Since a mod b < b (by definition of modulo), the new b (which is
    a mod b) is strictly less than the old b. Since b >= 0 and the loop
    continues while b > 0, the loop must terminate.

    CORRECTNESS AT TERMINATION: When b = 0, the invariant gives
    gcd(a, 0) = gcd(original_a, original_b). Since gcd(a, 0) = a,
    we return a.
    """
    original_a, original_b = a, b

    iteration = 0
    while b != 0:
        if verbose:
            print(f"  Iter {iteration}: a={a}, b={b}")
            print(f"    Invariant: gcd({a}, {b}) = gcd({original_a}, {original_b})")

        a, b = b, a % b
        iteration += 1

    if verbose:
        print(f"  Iter {iteration}: a={a}, b={b} (b=0, loop ends)")
        print(f"    Result: gcd({original_a}, {original_b}) = {a}")

    return a


print(f"\ngcd(48, 18):")
result = gcd_proven(48, 18, verbose=True)
print(f"Result: {result}")

print(f"\ngcd(252, 105):")
result = gcd_proven(252, 105, verbose=True)
print(f"Result: {result}")

# Verify against known values
test_cases = [(48, 18, 6), (252, 105, 21), (17, 13, 1), (100, 0, 100), (0, 5, 5)]
print("\nVerification:")
for a, b, expected in test_cases:
    result = gcd_proven(a, b)
    status = "PASS" if result == expected else "FAIL"
    print(f"  gcd({a}, {b}) = {result}, expected {expected}: {status}")


# ===========================================================================
# SECTION 6: Fast Exponentiation -- Proving It Correct
# ===========================================================================

print("\n" + "=" * 70)
print("SECTION 6: Fast Exponentiation (Binary Method) with Loop Invariant")
print("=" * 70)


def fast_power_proven(base, exp, verbose=False):
    """Compute base^exp using binary exponentiation with correctness proof.

    PRECONDITION: exp >= 0, base is any number.
    POSTCONDITION: returns base^exp.

    LOOP INVARIANT: result * base^exp = original_base^original_exp
    at the start of every iteration.

    INITIALIZATION: result=1, base=original_base, exp=original_exp.
    So result * base^exp = 1 * original_base^original_exp. True.

    MAINTENANCE: Two cases.
    Case 1 (exp is odd): We set result = result * base, exp = exp - 1.
      New: (result * base) * base^(exp - 1)
         = result * base^1 * base^(exp - 1)
         = result * base^exp. Same as before.
    Case 2 (exp is even): We set base = base * base, exp = exp // 2.
      New: result * (base * base)^(exp // 2)
         = result * base^(2 * exp // 2)
         = result * base^exp. Same as before.

    TERMINATION: exp is a non-negative integer that strictly decreases.
    In case 1, exp decreases by 1. In case 2, exp halves. Since we enter
    case 2 only when exp > 0 and is even, exp // 2 < exp. When exp = 0,
    the loop exits.

    CORRECTNESS AT TERMINATION: When exp = 0, the invariant gives
    result * base^0 = original_base^original_exp, so
    result = original_base^original_exp.

    TIME COMPLEXITY: O(log exp) because exp halves at least every two
    iterations (if exp is odd, we subtract 1 making it even, then halve).
    """
    original_base, original_exp = base, exp
    result = 1

    iteration = 0
    while exp > 0:
        if verbose:
            print(f"  Iter {iteration}: result={result}, base={base}, exp={exp}")
            print(f"    Invariant: {result} * {base}^{exp} = "
                  f"{original_base}^{original_exp} = {original_base ** original_exp}")
            # Verify the invariant numerically
            assert result * (base ** exp) == original_base ** original_exp, \
                "Invariant violated!"

        if exp % 2 == 1:  # exp is odd
            result *= base
            exp -= 1
        else:  # exp is even
            base *= base
            exp //= 2

        iteration += 1

    if verbose:
        print(f"  Iter {iteration}: result={result}, base={base}, exp={exp}")
        print(f"    exp=0, loop ends. result = {result}")

    return result


print(f"\n2^10:")
result = fast_power_proven(2, 10, verbose=True)
print(f"Result: {result} (expected {2 ** 10})")

print(f"\n3^7:")
result = fast_power_proven(3, 7, verbose=True)
print(f"Result: {result} (expected {3 ** 7})")

# Verify against Python's built-in
print("\nVerification against Python's ** operator:")
test_cases = [(2, 0), (2, 1), (2, 10), (3, 7), (5, 5), (7, 3), (1, 100)]
for b, e in test_cases:
    ours = fast_power_proven(b, e)
    expected = b ** e
    status = "PASS" if ours == expected else "FAIL"
    print(f"  {b}^{e} = {ours}, expected {expected}: {status}")


# ===========================================================================
# SECTION 7: Why This Matters -- The Bigger Picture
# ===========================================================================

print("\n" + "=" * 70)
print("SECTION 7: Why Formal Proofs Matter")
print("=" * 70)

print("""
KEY TAKEAWAYS:

1. EVERY LOOP IS INDUCTION IN DISGUISE
   The loop variable is the induction variable. The loop body is the
   inductive step. Initialization is the base case. If you can state
   the invariant, you can prove the loop correct.

2. THE THREE-PART FRAMEWORK
   Initialization: true before the first iteration.
   Maintenance: if true before an iteration, still true after.
   Termination: combined with the exit condition, gives you the answer.

   This is exactly weak induction where P(k) is "the invariant holds
   after iteration k."

3. TERMINATION IS NOT FREE
   You must identify a quantity that STRICTLY DECREASES and is bounded
   below. Without this, your "algorithm" might loop forever.
   - Binary search: hi - lo decreases
   - Bubble sort: n - 1 - i decreases (and early exit if no swaps)
   - Euclid's GCD: b decreases (a mod b < b)
   - Fast exponentiation: exp decreases

4. DIJKSTRA WAS RIGHT
   "Testing shows the presence of bugs, not their absence."
   Binary search was published in 1946. The first correct implementation
   was not published until 1962. Jon Bentley found that 90% of
   professional programmers could not write a correct binary search.
   Java's Arrays.binarySearch had an overflow bug for 9 YEARS (2006).

   Loop invariants would have caught all of these bugs.

5. THE PRACTICE
   For every algorithm you write from now on, ask:
   - What is the loop invariant?
   - Why is it true before the loop?
   - Why does each iteration preserve it?
   - Why does the loop terminate?
   - How does the invariant + termination give me the postcondition?
""")
