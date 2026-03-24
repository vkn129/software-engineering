"""
Day 10: Combinatorics -- Permutations, Combinations, Counting Principles
==========================================================================

This file builds combinatorial tools from first principles. No libraries.
We implement counting functions, then generators that enumerate arrangements,
then apply these to real problems.

Run: python combinatorics.py
"""


# =============================================================================
# SECTION 1: Factorial and Basic Counting
# =============================================================================

print("=" * 65)
print("SECTION 1: Factorial -- The Foundation of Counting")
print("=" * 65)


def factorial(n):
    """Compute n! iteratively.

    Why iterative? Recursive factorial hits Python's stack limit around n=1000.
    Real systems need to handle larger inputs, so we avoid recursion.

    n! grows absurdly fast:
      10! = 3,628,800
      20! = 2,432,902,008,176,640,000
      100! has 158 digits
      1000! has 2568 digits
    """
    if n < 0:
        raise ValueError("Factorial undefined for negative numbers")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# Show how fast factorial grows
print("\nFactorial growth (why brute force dies):")
print(f"  {'n':>4} {'n!':>25} {'digits':>8}")
print("  " + "-" * 40)
for n in [1, 5, 10, 15, 20, 25, 30]:
    f = factorial(n)
    digits = len(str(f))
    display = str(f) if digits <= 20 else f"{str(f)[:15]}...({digits} digits)"
    print(f"  {n:>4} {display:>25} {digits:>8}")

print("\nWhy this matters: sorting n items requires examining n! orderings.")
print("At n=20, that's 2.4 quintillion -- no computer can enumerate them all.")


# =============================================================================
# SECTION 2: Permutations
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 2: Permutations -- When Order Matters")
print("=" * 65)


def permutation_count(n, k=None):
    """P(n, k) = n! / (n-k)! = number of ways to arrange k items from n.

    If k is None, compute n! (arrange all n items).

    Physical interpretation: "How many ways to seat k people in k specific
    chairs, chosen from n candidates?"
    """
    if k is None:
        k = n
    if k > n or k < 0:
        return 0
    # Compute n * (n-1) * ... * (n-k+1) directly to avoid large factorials
    result = 1
    for i in range(n, n - k, -1):
        result *= i
    return result


print("\nP(n, k) -- k-permutations of n:")
print(f"  {'n':>4} {'k':>4} {'P(n,k)':>15}")
print("  " + "-" * 28)
for n, k in [(5, 3), (10, 2), (10, 5), (52, 5), (26, 3)]:
    print(f"  {n:>4} {k:>4} {permutation_count(n, k):>15}")

print("\n  P(52, 5) = number of ways to draw 5 cards in order from a deck")
print(f"  = {permutation_count(52, 5):,}")


def generate_permutations(elements):
    """Generate all permutations of a list using backtracking.

    The algorithm:
    1. Pick each unused element for the current position
    2. Recurse to fill remaining positions
    3. Backtrack: undo the choice and try the next element

    This is the fundamental backtracking pattern. Every exhaustive search
    algorithm (Sudoku solvers, SAT solvers, etc.) uses a variant of this.
    """
    result = []
    n = len(elements)
    used = [False] * n
    current = []

    def backtrack():
        if len(current) == n:
            result.append(current[:])  # Copy! Don't append a reference.
            return

        for i in range(n):
            if not used[i]:
                # Choose
                used[i] = True
                current.append(elements[i])

                # Explore
                backtrack()

                # Un-choose (backtrack)
                current.pop()
                used[i] = False

    backtrack()
    return result


print("\nAll permutations of [1, 2, 3]:")
perms = generate_permutations([1, 2, 3])
for i, p in enumerate(perms):
    print(f"  {i+1:>2}. {p}")
print(f"  Total: {len(perms)} (expected: 3! = {factorial(3)})")

print("\nPermutations of ['A', 'B', 'C', 'D']:")
perms4 = generate_permutations(['A', 'B', 'C', 'D'])
print(f"  Total: {len(perms4)} (expected: 4! = {factorial(4)})")
print(f"  First 5: {perms4[:5]}")
print(f"  Last 5:  {perms4[-5:]}")


def generate_k_permutations(elements, k):
    """Generate all k-permutations: ordered selections of k items from elements."""
    result = []
    n = len(elements)
    used = [False] * n
    current = []

    def backtrack():
        if len(current) == k:
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


print("\n2-permutations of [1, 2, 3, 4]:")
kperms = generate_k_permutations([1, 2, 3, 4], 2)
for p in kperms:
    print(f"  {p}")
print(f"  Total: {len(kperms)} (expected: P(4,2) = {permutation_count(4, 2)})")


# =============================================================================
# SECTION 3: Combinations
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 3: Combinations -- When Order Doesn't Matter")
print("=" * 65)


def binomial(n, k):
    """C(n, k) = n! / (k! * (n-k)!) computed without factorial overflow.

    We compute this as a product: C(n,k) = (n * (n-1) * ... * (n-k+1)) / k!

    We divide as we go to keep intermediate values small. This works because
    the binomial coefficient is always an integer, so the running product
    is always divisible by the next divisor.

    Why not just factorial(n) // (factorial(k) * factorial(n-k))?
    Because factorial(1000) has 2568 digits. This approach keeps numbers
    manageable even for large n.
    """
    if k < 0 or k > n:
        return 0
    # Use symmetry: C(n, k) = C(n, n-k). Choose the smaller k.
    if k > n - k:
        k = n - k
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


print("\nBinomial coefficients C(n, k):")
print(f"  {'n':>4} {'k':>4} {'C(n,k)':>15}")
print("  " + "-" * 28)
for n, k in [(5, 2), (10, 3), (52, 5), (100, 50), (20, 7)]:
    print(f"  {n:>4} {k:>4} {binomial(n, k):>15}")

# Verify symmetry: C(n, k) = C(n, n-k)
print("\nSymmetry: C(n, k) = C(n, n-k)")
for n, k in [(10, 3), (52, 5), (20, 7)]:
    print(f"  C({n},{k}) = {binomial(n, k)},  C({n},{n-k}) = {binomial(n, n-k)}")


def generate_combinations(elements, k):
    """Generate all combinations of k items from elements using backtracking.

    Key difference from permutations: we enforce an ordering constraint.
    Each recursive call only considers elements at index >= start, which
    prevents generating the same subset in different orders.

    {A,B,C} is the same combination as {C,B,A}, so we only generate
    the one where indices are increasing.
    """
    result = []
    n = len(elements)
    current = []

    def backtrack(start):
        if len(current) == k:
            result.append(current[:])
            return

        # Only consider elements after the last chosen one
        # This is what eliminates duplicate subsets
        for i in range(start, n):
            current.append(elements[i])
            backtrack(i + 1)  # i+1, not i -- no reuse
            current.pop()

    backtrack(0)
    return result


print("\nAll combinations of 2 from [1, 2, 3, 4]:")
combs = generate_combinations([1, 2, 3, 4], 2)
for c in combs:
    print(f"  {c}")
print(f"  Total: {len(combs)} (expected: C(4,2) = {binomial(4, 2)})")

print("\nCombinations of 3 from [A, B, C, D, E]:")
combs3 = generate_combinations(['A', 'B', 'C', 'D', 'E'], 3)
for c in combs3:
    print(f"  {c}")
print(f"  Total: {len(combs3)} (expected: C(5,3) = {binomial(5, 3)})")


# =============================================================================
# SECTION 4: Pascal's Triangle
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 4: Pascal's Triangle -- Dynamic Programming for C(n,k)")
print("=" * 65)

print("""
Pascal's Triangle encodes all binomial coefficients:
    C(n, k) = C(n-1, k-1) + C(n-1, k)

This recurrence says: to choose k items from n, either include the nth item
(and choose k-1 from the remaining n-1) or exclude it (and choose k from n-1).

This is the same "include or exclude" pattern that appears in dynamic
programming problems like the knapsack problem.
""")


def pascals_triangle(rows):
    """Build Pascal's Triangle row by row.

    Each entry is the sum of the two entries above it.
    This is O(n^2) time and space, but avoids factorial computation entirely.
    """
    triangle = []
    for n in range(rows):
        row = [1]  # C(n, 0) = 1
        for k in range(1, n):
            # C(n, k) = C(n-1, k-1) + C(n-1, k)
            row.append(triangle[n - 1][k - 1] + triangle[n - 1][k])
        if n > 0:
            row.append(1)  # C(n, n) = 1
        triangle.append(row)
    return triangle


# Print Pascal's Triangle
triangle = pascals_triangle(10)
print("First 10 rows:")
for i, row in enumerate(triangle):
    padding = " " * (30 - 3 * len(row))
    values = "  ".join(f"{v:>3}" for v in row)
    print(f"  n={i}: {padding}{values}")

# Verify against our binomial function
print("\nVerification: Pascal's Triangle vs binomial formula:")
for n in range(8):
    for k in range(n + 1):
        assert triangle[n][k] == binomial(n, k), \
            f"Mismatch at C({n},{k})"
print("  All entries match for n=0..7!")


# =============================================================================
# SECTION 5: Counting Applications
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 5: Counting Applications")
print("=" * 65)

# Application 1: Password strength
print("\n--- Password Strength ---")
charsets = [
    ("digits only (0-9)", 10),
    ("lowercase (a-z)", 26),
    ("alphanumeric (a-z, A-Z, 0-9)", 62),
    ("+ special chars", 95),
]
print(f"  {'Charset':<35} {'Len=6':>15} {'Len=8':>15} {'Len=12':>18}")
print("  " + "-" * 88)
for name, size in charsets:
    # Each position has `size` choices, rule of product
    n6 = size ** 6
    n8 = size ** 8
    n12 = size ** 12
    print(f"  {name:<35} {n6:>15,} {n8:>15,} {n12:>18,}")

# Application 2: Committee selection
print("\n--- Committee Selection ---")
print("  Choose a committee of 5 from 20 people:")
print(f"  Unordered (who's on it): C(20,5) = {binomial(20, 5):,}")
print(f"  Ordered (with roles):    P(20,5) = {permutation_count(20, 5):,}")
print(f"  Ratio: {permutation_count(20, 5) / binomial(20, 5):.0f}x "
      f"(= 5! = {factorial(5)}, the number of role assignments)")

# Application 3: Poker hands
print("\n--- Poker Hands ---")
total_hands = binomial(52, 5)
print(f"  Total 5-card hands: C(52,5) = {total_hands:,}")

# Royal flush: 4 suits, 1 way each
royal_flushes = 4
print(f"  Royal flushes: {royal_flushes} "
      f"(probability: {royal_flushes/total_hands:.8f})")

# Four of a kind: choose the rank (13 ways), choose which 4 suits (1 way),
# choose the kicker (48 remaining cards)
four_of_kind = 13 * 1 * 48
print(f"  Four of a kind: {four_of_kind} "
      f"(probability: {four_of_kind/total_hands:.6f})")

# Full house: choose the triple rank (13), choose 3 suits from 4, choose
# pair rank (12), choose 2 suits from 4
full_house = 13 * binomial(4, 3) * 12 * binomial(4, 2)
print(f"  Full house: {full_house} "
      f"(probability: {full_house/total_hands:.6f})")

# Application 4: Anagram counting
print("\n--- Anagram Counting ---")


def count_anagrams(word):
    """Count distinct anagrams of a word.

    For a word with n letters where letter i appears c_i times:
    anagrams = n! / (c_1! * c_2! * ... * c_k!)

    This is a multinomial coefficient. We divide by the factorials of
    repeated letters because swapping identical letters doesn't create
    a new arrangement.
    """
    from collections import Counter
    counts = Counter(word.lower())
    n = len(word)
    result = factorial(n)
    for c in counts.values():
        result //= factorial(c)
    return result, dict(Counter(word.lower()))


words = ["CAT", "BANANA", "MISSISSIPPI", "AABB", "ABCDE"]
for word in words:
    count, freq = count_anagrams(word)
    print(f"  '{word}': {count:>12,} anagrams  (letter freq: {freq})")


# =============================================================================
# SECTION 6: Stars and Bars
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 6: Stars and Bars -- Distributing Identical Objects")
print("=" * 65)

print("""
Problem: distribute n identical items into k distinct bins.
Equivalent: count non-negative integer solutions to x1 + x2 + ... + xk = n.

Visualization: arrange n stars (*) and k-1 bars (|) in a line.
    Example: 5 items, 3 bins: **|*|** means bins get (2, 1, 2)
    Total symbols: n + k - 1. Choose where to put the k-1 bars.
    Answer: C(n + k - 1, k - 1)
""")


def stars_and_bars(n, k):
    """Number of ways to distribute n identical items into k distinct bins."""
    return binomial(n + k - 1, k - 1)


problems = [
    (10, 3, "10 cookies among 3 children"),
    (5, 4, "5 identical balls into 4 boxes"),
    (20, 5, "20 dollars among 5 funds"),
    (3, 2, "3 items into 2 bins"),
]
for n, k, desc in problems:
    print(f"  {desc}: C({n+k-1}, {k-1}) = {stars_and_bars(n, k)}")

# Show actual distributions for a small case
print("\n  All distributions of 3 items into 2 bins:")


def enumerate_distributions(n, k):
    """Generate all distributions of n identical items into k bins."""
    result = []
    current = []

    def backtrack(remaining, bins_left):
        if bins_left == 1:
            current.append(remaining)
            result.append(current[:])
            current.pop()
            return
        for i in range(remaining + 1):
            current.append(i)
            backtrack(remaining - i, bins_left - 1)
            current.pop()

    backtrack(n, k)
    return result


dists = enumerate_distributions(3, 2)
for d in dists:
    stars = " | ".join("*" * x if x > 0 else " " for x in d)
    print(f"    {d}  ->  {stars}")
print(f"  Total: {len(dists)} (formula: C({3+2-1},{2-1}) = {stars_and_bars(3, 2)})")


# =============================================================================
# SECTION 7: Complexity Connection -- Why Sorting is O(n log n)
# =============================================================================

print("\n" + "=" * 65)
print("SECTION 7: Why Comparison Sort Can't Beat O(n log n)")
print("=" * 65)

import math

print("""
A comparison-based sort on n elements must distinguish between n! permutations.
Each comparison gives 1 bit of information (yes/no).
So you need at least ceil(log2(n!)) comparisons.

By Stirling's approximation: log2(n!) ≈ n*log2(n) - n*log2(e)
This is Theta(n log n).
""")

print(f"  {'n':>6} {'n!':>20} {'log2(n!)':>10} {'n*log2(n)':>10}")
print("  " + "-" * 50)
for n in [5, 10, 20, 50, 100, 1000]:
    f = factorial(n)
    log2_f = math.log2(f)
    n_logn = n * math.log2(n) if n > 1 else 0
    f_str = str(f) if len(str(f)) <= 15 else f"({len(str(f))} digits)"
    print(f"  {n:>6} {f_str:>20} {log2_f:>10.1f} {n_logn:>10.1f}")

print("\n  The lower bound and n*log2(n) grow at the same rate.")
print("  This proves no comparison sort can be faster than O(n log n).")


print("\n" + "=" * 65)
print("All demonstrations complete.")
print("=" * 65)
