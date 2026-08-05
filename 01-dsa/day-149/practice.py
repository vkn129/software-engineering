"""
Day 149 Practice: Sieve of Eratosthenes

6 exercises: basic sieve, prime check, count, sum, segmented, SPF.
Implement the TODO functions, then run: python practice.py
"""

import math


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
# Exercise 1: Basic Sieve
# ===================================================================
# Return list of all primes up to n.

def primes_up_to(n):
    """Return list of primes p with 2 <= p <= n."""
    # TODO: implement
    pass


def _sol_primes_up_to(n):
    if n < 2:
        return []
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(math.isqrt(n)) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, n + 1) if is_prime[i]]


# ===================================================================
# Exercise 2: Is Prime (using a sieve cache)
# ===================================================================
# Build a sieve, then answer queries in O(1).

def is_prime_sieve(n, queries):
    """For each q in queries, return True iff q is prime. q <= n."""
    # TODO: build sieve up to n, then answer each query
    pass


def _sol_is_prime_sieve(n, queries):
    if n < 2:
        is_prime = bytearray(n + 1)
    else:
        is_prime = bytearray(b"\x01") * (n + 1)
        is_prime[0] = is_prime[1] = 0
        for i in range(2, int(math.isqrt(n)) + 1):
            if is_prime[i]:
                for j in range(i * i, n + 1, i):
                    is_prime[j] = 0
    return [bool(is_prime[q]) for q in queries]


# ===================================================================
# Exercise 3: Count Primes Up To n
# ===================================================================
# Return how many primes are <= n.

def count_primes(n):
    """Return the count of primes p with 2 <= p <= n."""
    # TODO: implement
    pass


def _sol_count_primes(n):
    return len(_sol_primes_up_to(n))


# ===================================================================
# Exercise 4: Sum of Primes
# ===================================================================
# Sum all primes up to n.

def sum_primes(n):
    """Return the sum of all primes p with 2 <= p <= n."""
    # TODO: implement
    pass


def _sol_sum_primes(n):
    return sum(_sol_primes_up_to(n))


# ===================================================================
# Exercise 5: Segmented sieve over [lo, hi]
# ===================================================================
# Return primes in [lo, hi]. May be a huge range; must NOT allocate hi+1 bytes.
# Hint: precompute small primes up to sqrt(hi), then sieve the segment.

def primes_in_range(lo, hi):
    """Return list of primes p with lo <= p <= hi."""
    # TODO: implement segmented sieve
    pass


def _sol_primes_in_range(lo, hi):
    if hi < 2 or lo > hi:
        return []
    lo = max(lo, 2)
    small = _sol_primes_up_to(int(math.isqrt(hi)))
    is_prime = bytearray(b"\x01") * (hi - lo + 1)
    for p in small:
        start = max(p * p, ((lo + p - 1) // p) * p)
        for j in range(start, hi + 1, p):
            is_prime[j - lo] = 0
    return [i for i in range(lo, hi + 1) if is_prime[i - lo]]


# ===================================================================
# Exercise 6: Smallest Prime Factor table
# ===================================================================
# Return list spf where spf[i] is the smallest prime factor of i (for 2<=i<=n).
# spf[0] = spf[1] = 0. Useful for fast factorization.

def smallest_prime_factors(n):
    """Return list of length n+1 with spf[i] = smallest prime factor of i."""
    # TODO: implement (any correct method)
    pass


def _sol_smallest_prime_factors(n):
    spf = [0] * (n + 1)
    for i in range(2, n + 1):
        if spf[i] == 0:
            for j in range(i, n + 1, i):
                if spf[j] == 0:
                    spf[j] = i
    return spf


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
    print("Exercise 1: Primes up to n")
    check("primes <= 20", try_or_sol("primes_up_to", 20),
          [2, 3, 5, 7, 11, 13, 17, 19])
    check("primes <= 1", try_or_sol("primes_up_to", 1), [])
    check("primes <= 2", try_or_sol("primes_up_to", 2), [2])

    # --- Exercise 2 ---
    print("\nExercise 2: is_prime via sieve")
    res = try_or_sol("is_prime_sieve", 30, [2, 4, 17, 25, 29])
    check("queries", res, [True, False, True, False, True])

    # --- Exercise 3 ---
    print("\nExercise 3: Count Primes")
    check("count <= 10", try_or_sol("count_primes", 10), 4)
    check("count <= 100", try_or_sol("count_primes", 100), 25)
    check("count <= 1000", try_or_sol("count_primes", 1000), 168)

    # --- Exercise 4 ---
    print("\nExercise 4: Sum of Primes")
    check("sum <= 10", try_or_sol("sum_primes", 10), 17)  # 2+3+5+7
    check("sum <= 20", try_or_sol("sum_primes", 20), 77)
    check("sum <= 1", try_or_sol("sum_primes", 1), 0)

    # --- Exercise 5 ---
    print("\nExercise 5: Segmented Sieve")
    check("[100, 130]", try_or_sol("primes_in_range", 100, 130),
          [101, 103, 107, 109, 113, 127])
    check("[1, 10]", try_or_sol("primes_in_range", 1, 10), [2, 3, 5, 7])
    # Big range, just check count
    p = try_or_sol("primes_in_range", 10**6, 10**6 + 1000)
    check("[1e6, 1e6+1000] count", len(p), 75)

    # --- Exercise 6 ---
    print("\nExercise 6: Smallest Prime Factors")
    spf = try_or_sol("smallest_prime_factors", 20)
    check("spf[12]", spf[12], 2)
    check("spf[15]", spf[15], 3)
    check("spf[17]", spf[17], 17)
    check("spf[1]", spf[1], 0)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
