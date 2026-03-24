"""
Day 11 Practice: Probability in Algorithms
===========================================

These exercises build intuition for randomized algorithms and probabilistic
analysis. You will implement classic algorithms that trade certainty for speed,
and use simulation to verify theoretical expected values.

Fill in the TODO sections. Run this file to check your answers.

Run: python practice.py
"""

import random
import math


# =============================================================================
# Exercise 1: Fermat Primality Test
# =============================================================================

def fermat_primality_test(n, k=20):
    """Test whether n is (probably) prime using Fermat's Little Theorem.

    Fermat's Little Theorem: if p is prime and 1 <= a < p, then
        a^(p-1) === 1 (mod p)

    Strategy: pick k random witnesses a in [2, n-2]. If ANY witness
    fails the test (a^(n-1) % n != 1), n is definitely composite.
    If all pass, n is "probably prime" -- but Carmichael numbers fool
    this test, which is why Miller-Rabin exists.

    Args:
        n: integer to test (n >= 2)
        k: number of random witnesses to try

    Returns:
        dict with:
        - 'probably_prime': bool
        - 'witnesses_tried': list of a values tested
        - 'failed_witness': the first a where a^(n-1) % n != 1, or None

    TODO: Implement the Fermat test. Use Python's built-in pow(a, exp, mod)
    for modular exponentiation -- it uses repeated squaring internally.
    """
    # Edge cases
    if n < 2:
        return {'probably_prime': False, 'witnesses_tried': [], 'failed_witness': None}
    if n <= 3:
        return {'probably_prime': True, 'witnesses_tried': [], 'failed_witness': None}
    if n % 2 == 0:
        return {'probably_prime': False, 'witnesses_tried': [], 'failed_witness': None}

    witnesses_tried = []
    failed_witness = None

    for _ in range(k):
        # TODO: Pick a random witness a in [2, n-2]
        a = 0  # FIX THIS

        witnesses_tried.append(a)

        # TODO: Check if a^(n-1) % n == 1 using pow(a, n-1, n)
        # If the test fails, set failed_witness and break
        pass  # FIX THIS

    return {
        'probably_prime': failed_witness is None,
        'witnesses_tried': witnesses_tried,
        'failed_witness': failed_witness,
    }


# =============================================================================
# Exercise 2: Monte Carlo Pi Estimation
# =============================================================================

def monte_carlo_pi(num_samples):
    """Estimate pi by throwing random darts at a unit square.

    Why this works: A quarter-circle of radius 1 fits inside the unit square
    [0,1] x [0,1]. The area of the quarter-circle is pi/4, the area of the
    square is 1. So the fraction of points landing inside the circle
    converges to pi/4. Multiply by 4 to get pi.

    A point (x, y) is inside the unit circle if x^2 + y^2 <= 1.

    The convergence rate is O(1/sqrt(n)) -- you need 100x more samples
    for one more digit of accuracy. This is why Monte Carlo is a last resort,
    but it works in ANY number of dimensions (unlike numerical integration).

    Args:
        num_samples: how many random points to generate

    Returns:
        dict with:
        - 'estimate': the pi estimate (4 * inside / total)
        - 'inside_count': number of points inside the quarter-circle
        - 'error': absolute difference from math.pi
        - 'samples': num_samples

    TODO: Implement the simulation.
    """
    inside_count = 0

    for _ in range(num_samples):
        # TODO: Generate random (x, y) in [0, 1) x [0, 1)
        # TODO: Check if x^2 + y^2 <= 1, increment inside_count
        pass  # FIX THIS

    # TODO: Compute estimate as 4 * inside_count / num_samples
    estimate = 0.0  # FIX THIS

    return {
        'estimate': estimate,
        'inside_count': inside_count,
        'error': abs(estimate - math.pi),
        'samples': num_samples,
    }


# =============================================================================
# Exercise 3: Coupon Collector Simulation
# =============================================================================

def coupon_collector(n, trials=1000):
    """Simulate the coupon collector problem and verify the expected value.

    Problem: there are n distinct coupon types. Each draw gives a uniformly
    random coupon. How many draws until you have all n types?

    Theory: expected draws = n * H(n) where H(n) = 1 + 1/2 + 1/3 + ... + 1/n
    (the n-th harmonic number).

    Why? After collecting k distinct types, the probability of getting a new
    type on the next draw is (n-k)/n. The expected draws in this phase is
    n/(n-k). Summing over k=0..n-1 gives n * sum(1/i for i=1..n) = n*H(n).

    This is a key result: it explains why hash table load factors matter and
    why randomized algorithms need O(n log n) samples for full coverage.

    Args:
        n: number of distinct coupon types
        trials: number of independent simulations to average

    Returns:
        dict with:
        - 'average_draws': empirical average draws to collect all n
        - 'expected_draws': theoretical n * H(n)
        - 'relative_error': |average - expected| / expected
        - 'min_draws': minimum draws across all trials
        - 'max_draws': maximum draws across all trials

    TODO: Implement the simulation.
    """
    harmonic_n = sum(1.0 / i for i in range(1, n + 1))
    expected_draws = n * harmonic_n

    draw_counts = []

    for _ in range(trials):
        # TODO: Simulate one trial
        # Keep drawing random coupons (random.randint(0, n-1)) until
        # you have all n types. Count the total draws needed.
        # Use a set to track which types you have collected.
        draws = 0  # FIX THIS
        draw_counts.append(draws)

    average_draws = sum(draw_counts) / len(draw_counts) if draw_counts else 0

    return {
        'average_draws': average_draws,
        'expected_draws': expected_draws,
        'relative_error': abs(average_draws - expected_draws) / expected_draws if expected_draws else 0,
        'min_draws': min(draw_counts) if draw_counts else 0,
        'max_draws': max(draw_counts) if draw_counts else 0,
    }


# =============================================================================
# Exercise 4: Randomized Partition -- Comparison Counting
# =============================================================================

def randomized_quicksort_analysis(arr):
    """Sort using randomized quicksort and count comparisons.

    In randomized quicksort, the pivot is chosen uniformly at random.
    This ensures that no adversarial input can force O(n^2) behavior.

    Expected comparisons: approximately 2n*ln(n) ~ 1.39 * n * log2(n).
    This comes from the probability that elements i and j are compared:
    exactly 2/(j-i+1) when the array is sorted, summing to 2*n*H(n).

    TODO: Implement randomized quicksort with comparison counting.
    Return the sorted array and the total number of element comparisons.

    Args:
        arr: list of comparable elements

    Returns:
        dict with:
        - 'sorted': the sorted list
        - 'comparisons': total number of element comparisons made
        - 'n': length of input
        - 'expected_comparisons': 2 * n * ln(n) (theoretical expected)
        - 'ratio': comparisons / (n * log2(n)) -- should be near 1.39
    """
    comparisons = [0]  # mutable container so nested function can modify it

    def quicksort(a):
        if len(a) <= 1:
            return a

        # TODO: Choose a random pivot index, get pivot value
        pivot = 0  # FIX THIS -- pick random element from a

        # TODO: Partition into [less than pivot], [equal], [greater than pivot]
        # Count each comparison (each time you compare an element with the pivot)
        less, equal, greater = [], [], []
        # FIX THIS -- partition and count comparisons

        # TODO: Recursively sort less and greater, concatenate
        return []  # FIX THIS

    sorted_arr = quicksort(list(arr))

    n = len(arr)
    # Expected comparisons: 2 * n * ln(n) for large n
    expected = 2 * n * math.log(n) if n > 1 else 0
    nlogn = n * math.log2(n) if n > 1 else 1

    return {
        'sorted': sorted_arr,
        'comparisons': comparisons[0],
        'n': n,
        'expected_comparisons': expected,
        'ratio': comparisons[0] / nlogn if nlogn > 0 else 0,
    }


# =============================================================================
# Reference Solutions (scroll down after attempting!)
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
# SPOILER SPACE -- try the exercises before looking below!
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


def _solution_1_fermat(n, k=20):
    if n < 2:
        return {'probably_prime': False, 'witnesses_tried': [], 'failed_witness': None}
    if n <= 3:
        return {'probably_prime': True, 'witnesses_tried': [], 'failed_witness': None}
    if n % 2 == 0:
        return {'probably_prime': False, 'witnesses_tried': [], 'failed_witness': None}

    witnesses_tried = []
    failed_witness = None

    for _ in range(k):
        a = random.randint(2, n - 2)
        witnesses_tried.append(a)

        # Fermat's Little Theorem: a^(p-1) === 1 (mod p) for prime p
        if pow(a, n - 1, n) != 1:
            failed_witness = a
            break

    return {
        'probably_prime': failed_witness is None,
        'witnesses_tried': witnesses_tried,
        'failed_witness': failed_witness,
    }


def _solution_2_pi(num_samples):
    inside_count = 0
    for _ in range(num_samples):
        x = random.random()
        y = random.random()
        # Distance from origin squared: x^2 + y^2.
        # If <= 1, point is inside the quarter-circle of radius 1.
        if x * x + y * y <= 1.0:
            inside_count += 1

    estimate = 4.0 * inside_count / num_samples
    return {
        'estimate': estimate,
        'inside_count': inside_count,
        'error': abs(estimate - math.pi),
        'samples': num_samples,
    }


def _solution_3_coupon(n, trials=1000):
    harmonic_n = sum(1.0 / i for i in range(1, n + 1))
    expected_draws = n * harmonic_n

    draw_counts = []
    for _ in range(trials):
        collected = set()
        draws = 0
        while len(collected) < n:
            collected.add(random.randint(0, n - 1))
            draws += 1
        draw_counts.append(draws)

    average_draws = sum(draw_counts) / len(draw_counts)
    return {
        'average_draws': average_draws,
        'expected_draws': expected_draws,
        'relative_error': abs(average_draws - expected_draws) / expected_draws,
        'min_draws': min(draw_counts),
        'max_draws': max(draw_counts),
    }


def _solution_4_quicksort(arr):
    comparisons = [0]

    def quicksort(a):
        if len(a) <= 1:
            return a

        # Random pivot prevents adversarial worst-case
        pivot = a[random.randint(0, len(a) - 1)]

        less, equal, greater = [], [], []
        for x in a:
            comparisons[0] += 1  # each element is compared to pivot
            if x < pivot:
                less.append(x)
            elif x == pivot:
                equal.append(x)
            else:
                greater.append(x)

        return quicksort(less) + equal + quicksort(greater)

    sorted_arr = quicksort(list(arr))
    n = len(arr)
    expected = 2 * n * math.log(n) if n > 1 else 0
    nlogn = n * math.log2(n) if n > 1 else 1

    return {
        'sorted': sorted_arr,
        'comparisons': comparisons[0],
        'n': n,
        'expected_comparisons': expected,
        'ratio': comparisons[0] / nlogn if nlogn > 0 else 0,
    }


# =============================================================================
# Self-check
# =============================================================================

def run_checks():
    print("=" * 70)
    print("DAY 11 PRACTICE -- Checking your solutions")
    print("=" * 70)

    # Exercise 1: Fermat Primality Test
    print("\n--- Exercise 1: Fermat Primality Test ---")
    primes = [2, 3, 7, 61, 97, 101, 541, 7919]
    composites = [4, 6, 15, 100, 561]  # 561 is a Carmichael number!

    result_prime = fermat_primality_test(97)
    result_comp = fermat_primality_test(100)
    if not result_prime['witnesses_tried'] and not result_comp['witnesses_tried']:
        print("  NOT YET IMPLEMENTED")
    else:
        all_correct = True
        for p in primes:
            r = fermat_primality_test(p)
            if not r['probably_prime']:
                print(f"  FAIL: {p} is prime but test said composite")
                all_correct = False
        for c in [4, 6, 15, 100]:
            r = fermat_primality_test(c)
            if r['probably_prime']:
                print(f"  FAIL: {c} is composite but test said prime")
                all_correct = False
        if all_correct:
            print("  PASS: Correctly identified primes and composites!")
        # Note about Carmichael numbers
        r561 = fermat_primality_test(561)
        print(f"  Note: 561 (Carmichael number) reported as "
              f"{'prime' if r561['probably_prime'] else 'composite'} -- "
              f"Fermat test is fooled by Carmichael numbers.")

    # Exercise 2: Monte Carlo Pi
    print("\n--- Exercise 2: Monte Carlo Pi Estimation ---")
    result = monte_carlo_pi(100000)
    if result['estimate'] == 0.0:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  Estimate: {result['estimate']:.6f}")
        print(f"  True pi:  {math.pi:.6f}")
        print(f"  Error:    {result['error']:.6f}")
        if result['error'] < 0.1:
            print("  PASS: Estimate within 0.1 of true pi!")
        else:
            print("  FAIL: Error too large. Check your geometry.")

    # Exercise 3: Coupon Collector
    print("\n--- Exercise 3: Coupon Collector Simulation ---")
    result = coupon_collector(10, trials=2000)
    if result['average_draws'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  n=10 coupons, 2000 trials")
        print(f"  Average draws: {result['average_draws']:.1f}")
        print(f"  Expected (n*H(n)): {result['expected_draws']:.1f}")
        print(f"  Relative error: {result['relative_error']:.3f}")
        print(f"  Range: [{result['min_draws']}, {result['max_draws']}]")
        if result['relative_error'] < 0.10:
            print("  PASS: Empirical average close to theoretical expected value!")
        else:
            print("  FAIL: Average too far from expected. Check simulation logic.")

    # Exercise 4: Randomized Quicksort
    print("\n--- Exercise 4: Randomized Quicksort Comparisons ---")
    test_arr = list(range(500))
    random.shuffle(test_arr)
    result = randomized_quicksort_analysis(test_arr)
    if not result['sorted']:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  n={result['n']} elements")
        print(f"  Comparisons: {result['comparisons']}")
        print(f"  Expected ~2n*ln(n): {result['expected_comparisons']:.0f}")
        print(f"  Ratio (comparisons / n*log2(n)): {result['ratio']:.2f}")
        if result['sorted'] == sorted(test_arr):
            print("  Sort correctness: PASS")
        else:
            print("  Sort correctness: FAIL")
        # Ratio should be near 1.39 for randomized quicksort
        if 0.5 < result['ratio'] < 3.0:
            print("  PASS: Comparison count in expected range!")
        else:
            print("  FAIL: Comparison count looks off.")


if __name__ == "__main__":
    run_checks()
