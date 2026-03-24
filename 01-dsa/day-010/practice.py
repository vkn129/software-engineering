"""
Day 10: Practice -- Combinatorics Exercises
=============================================

Fill in the TODO sections. Run this file to check your answers.
Each function has a docstring explaining what to implement and
test cases that verify correctness.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Factorial
# =============================================================================

def factorial(n):
    """Compute n! iteratively.

    Handle: n=0 -> 1, n<0 -> raise ValueError.
    Do NOT use recursion (stack overflow for large n).

    Examples:
        factorial(0)  -> 1
        factorial(5)  -> 120
        factorial(10) -> 3628800
    """
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 2: Binomial Coefficient
# =============================================================================

def binomial(n, k):
    """Compute C(n, k) without computing full factorials.

    Use the multiplicative formula: C(n,k) = product of (n-i)/(i+1) for i in 0..k-1.
    Apply symmetry: if k > n-k, use k = n-k.
    Return 0 if k < 0 or k > n.

    Examples:
        binomial(5, 2)   -> 10
        binomial(10, 3)  -> 120
        binomial(52, 5)  -> 2598960
        binomial(5, 0)   -> 1
        binomial(5, 5)   -> 1
        binomial(5, 6)   -> 0
    """
    # TODO: Implement this function
    # Hint: loop i from 0 to k-1, multiply by (n-i), integer-divide by (i+1)
    pass


# =============================================================================
# Exercise 3: Generate Permutations
# =============================================================================

def generate_permutations(elements):
    """Generate all permutations of elements using backtracking.

    Return a list of lists. Each inner list is one permutation.
    Elements should appear in lexicographic order if the input is sorted.

    Examples:
        generate_permutations([1, 2, 3]) ->
            [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
    """
    # TODO: Implement this function
    # Hint: use a 'used' boolean array and a 'current' list
    # At each step, try each unused element, recurse, then undo
    pass


# =============================================================================
# Exercise 4: Generate Combinations
# =============================================================================

def generate_combinations(elements, k):
    """Generate all combinations of k items from elements using backtracking.

    Return a list of lists. To avoid duplicates, only consider elements
    at index >= the last chosen index.

    Examples:
        generate_combinations([1,2,3,4], 2) ->
            [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
    """
    # TODO: Implement this function
    # Hint: backtrack(start) only loops from 'start' to n
    # This ensures elements are chosen in increasing index order
    pass


# =============================================================================
# Exercise 5: Count Anagrams
# =============================================================================

def count_anagrams(word):
    """Count the number of distinct anagrams of a word.

    Formula: n! / (c1! * c2! * ... * ck!) where ci is the count of letter i.
    Case-insensitive.

    Examples:
        count_anagrams("CAT")         -> 6   (3!/1 = 6)
        count_anagrams("BANANA")      -> 60  (6!/(3!*2!*1!) = 60)
        count_anagrams("MISSISSIPPI") -> 34650
        count_anagrams("AAA")         -> 1
    """
    # TODO: Implement this function
    # Hint: count letter frequencies, compute n! / product of freq factorials
    pass


# =============================================================================
# Exercise 6: Stars and Bars
# =============================================================================

def stars_and_bars(n, k):
    """Count ways to distribute n identical items into k distinct bins.

    Uses the formula: C(n + k - 1, k - 1).

    Examples:
        stars_and_bars(10, 3) -> 66    (10 cookies, 3 children)
        stars_and_bars(5, 4)  -> 56    (5 balls, 4 boxes)
        stars_and_bars(0, 3)  -> 1     (nothing to distribute, 1 way)
        stars_and_bars(3, 1)  -> 1     (only one bin)
    """
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 7: Password Strength Calculator
# =============================================================================

def password_combinations(length, charset_size):
    """Calculate total possible passwords of given length from charset.

    Each position has charset_size choices (rule of product).

    Examples:
        password_combinations(4, 10)  -> 10000  (4-digit PIN)
        password_combinations(8, 26)  -> 208827064576  (8 lowercase letters)
        password_combinations(8, 62)  -> 218340105584896  (alphanumeric)
    """
    # TODO: Implement this function
    pass


def password_bits_of_entropy(length, charset_size):
    """Calculate bits of entropy for a password.

    Entropy = log2(total_combinations).
    This measures how many yes/no questions an attacker needs to answer.

    Examples:
        password_bits_of_entropy(4, 10)  -> ~13.3  (4-digit PIN, very weak)
        password_bits_of_entropy(8, 62)  -> ~47.6  (alphanumeric, moderate)
        password_bits_of_entropy(12, 95) -> ~78.8  (12 chars, strong)
    """
    import math
    # TODO: Implement this function
    pass


# =============================================================================
# Exercise 8: Poker Hand Probabilities
# =============================================================================

def poker_probability(hand_type):
    """Calculate the probability of being dealt a specific poker hand.

    Use combinatorics to count favorable outcomes / total outcomes.
    Total 5-card hands from 52-card deck: C(52, 5) = 2,598,960.

    Supported hand_types:
        "four_of_a_kind" -> 624 / 2598960
        "full_house"     -> 3744 / 2598960
        "flush"          -> 5108 / 2598960

    Returns the probability as a float.

    Counting logic:
        four_of_a_kind: 13 ranks * C(4,4) * 48 remaining = 624
        full_house: 13 * C(4,3) * 12 * C(4,2) = 3744
        flush: 4 suits * C(13,5) - 40 straight flushes = 5108
    """
    # TODO: Implement this function
    pass


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run all tests and report results."""
    import math

    passed = 0
    failed = 0
    total = 0

    def check(name, got, expected):
        nonlocal passed, failed, total
        total += 1
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} -- expected {expected}, got {got}")

    def check_approx(name, got, expected, tolerance=0.01):
        nonlocal passed, failed, total
        total += 1
        if got is not None and abs(got - expected) < tolerance:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name} -- expected ~{expected}, got {got}")

    def check_raises(name, func, *args, exception=ValueError):
        nonlocal passed, failed, total
        total += 1
        try:
            func(*args)
            failed += 1
            print(f"  FAIL: {name} -- expected {exception.__name__}")
        except exception:
            passed += 1
            print(f"  PASS: {name}")

    print("=" * 55)
    print("Running Day 10 Practice Tests")
    print("=" * 55)

    # Exercise 1: Factorial
    print("\nExercise 1: Factorial")
    check("0!", factorial(0), 1)
    check("1!", factorial(1), 1)
    check("5!", factorial(5), 120)
    check("10!", factorial(10), 3628800)
    check_raises("(-1)! raises", factorial, -1)

    # Exercise 2: Binomial
    print("\nExercise 2: Binomial Coefficient")
    check("C(5,2)", binomial(5, 2), 10)
    check("C(10,3)", binomial(10, 3), 120)
    check("C(52,5)", binomial(52, 5), 2598960)
    check("C(5,0)", binomial(5, 0), 1)
    check("C(5,5)", binomial(5, 5), 1)
    check("C(5,6)", binomial(5, 6), 0)
    check("C(100,50)", binomial(100, 50), 100891344545564193334812497256)

    # Exercise 3: Permutations
    print("\nExercise 3: Generate Permutations")
    p3 = generate_permutations([1, 2, 3])
    if p3 is not None:
        check("perms([1,2,3]) count", len(p3), 6)
        check("first perm", p3[0], [1, 2, 3])
        check("last perm", p3[-1], [3, 2, 1])
    else:
        check("perms not None", p3, "not None")

    # Exercise 4: Combinations
    print("\nExercise 4: Generate Combinations")
    c42 = generate_combinations([1, 2, 3, 4], 2)
    if c42 is not None:
        check("combs([1..4],2) count", len(c42), 6)
        check("first comb", c42[0], [1, 2])
        check("last comb", c42[-1], [3, 4])
    else:
        check("combs not None", c42, "not None")

    c53 = generate_combinations([1, 2, 3, 4, 5], 3)
    if c53 is not None:
        check("combs([1..5],3) count", len(c53), 10)

    # Exercise 5: Anagrams
    print("\nExercise 5: Count Anagrams")
    check("CAT", count_anagrams("CAT"), 6)
    check("BANANA", count_anagrams("BANANA"), 60)
    check("MISSISSIPPI", count_anagrams("MISSISSIPPI"), 34650)
    check("AAA", count_anagrams("AAA"), 1)

    # Exercise 6: Stars and Bars
    print("\nExercise 6: Stars and Bars")
    check("(10,3)", stars_and_bars(10, 3), 66)
    check("(5,4)", stars_and_bars(5, 4), 56)
    check("(0,3)", stars_and_bars(0, 3), 1)
    check("(3,1)", stars_and_bars(3, 1), 1)

    # Exercise 7: Password Strength
    print("\nExercise 7: Password Strength")
    check("4-digit PIN", password_combinations(4, 10), 10000)
    check("8 lowercase", password_combinations(8, 26), 208827064576)
    check_approx("PIN entropy", password_bits_of_entropy(4, 10), 13.29, 0.1)
    check_approx("8 alphanum entropy", password_bits_of_entropy(8, 62), 47.63, 0.1)

    # Exercise 8: Poker
    print("\nExercise 8: Poker Probabilities")
    p4k = poker_probability("four_of_a_kind")
    if p4k is not None:
        check_approx("four_of_a_kind", p4k, 624 / 2598960, 0.00001)
    pfh = poker_probability("full_house")
    if pfh is not None:
        check_approx("full_house", pfh, 3744 / 2598960, 0.00001)

    # Summary
    print(f"\n{'=' * 55}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
    else:
        print(f"{failed} test(s) need attention.")
    print("=" * 55)


# =============================================================================
# SOLUTIONS (uncomment to verify tests pass)
# =============================================================================

"""
def factorial(n):
    if n < 0:
        raise ValueError("Factorial undefined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def binomial(n, k):
    if k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

def generate_permutations(elements):
    result = []
    n = len(elements)
    used = [False] * n
    current = []
    def backtrack():
        if len(current) == n:
            result.append(current[:])
            return
        for i in range(n):
            if not used[i]:
                used[i] = True
                current.append(elements[i])
                backtrack()
                current.pop()
                used[i] = False
    backtrack()
    return result

def generate_combinations(elements, k):
    result = []
    current = []
    n = len(elements)
    def backtrack(start):
        if len(current) == k:
            result.append(current[:])
            return
        for i in range(start, n):
            current.append(elements[i])
            backtrack(i + 1)
            current.pop()
    backtrack(0)
    return result

def count_anagrams(word):
    from collections import Counter
    counts = Counter(word.lower())
    n = len(word)
    result = factorial(n)
    for c in counts.values():
        result //= factorial(c)
    return result

def stars_and_bars(n, k):
    return binomial(n + k - 1, k - 1)

def password_combinations(length, charset_size):
    return charset_size ** length

def password_bits_of_entropy(length, charset_size):
    import math
    return math.log2(charset_size ** length)

def poker_probability(hand_type):
    total = binomial(52, 5)
    if hand_type == "four_of_a_kind":
        return (13 * 1 * 48) / total
    elif hand_type == "full_house":
        return (13 * binomial(4,3) * 12 * binomial(4,2)) / total
    elif hand_type == "flush":
        return (4 * binomial(13,5) - 40) / total
    return None
"""


if __name__ == "__main__":
    run_tests()
