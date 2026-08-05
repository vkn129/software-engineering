"""
Day 157 Practice: Randomized Algorithms

6 exercises. Run: python practice.py
"""

import random
import math


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: rand_quicksort
# ===================================================================
def rand_quicksort(arr):
    """Sort arr using a uniformly random pivot at each level."""
    # TODO
    pass


def _sol_rand_quicksort(arr):
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[random.randint(0, len(arr) - 1)]
    less = [x for x in arr if x < pivot]
    eq = [x for x in arr if x == pivot]
    gt = [x for x in arr if x > pivot]
    return _sol_rand_quicksort(less) + eq + _sol_rand_quicksort(gt)


# ===================================================================
# Exercise 2: rand_kth_smallest (quickselect with random pivot)
# ===================================================================
# Expected O(n).
def rand_kth_smallest(arr, k):
    """Return the k-th smallest element (1-indexed)."""
    # TODO
    pass


def _sol_rand_kth_smallest(arr, k):
    if not arr:
        return None
    pivot = arr[random.randint(0, len(arr) - 1)]
    less = [x for x in arr if x < pivot]
    eq = [x for x in arr if x == pivot]
    gt = [x for x in arr if x > pivot]
    if k <= len(less):
        return _sol_rand_kth_smallest(less, k)
    if k <= len(less) + len(eq):
        return pivot
    return _sol_rand_kth_smallest(gt, k - len(less) - len(eq))


# ===================================================================
# Exercise 3: reservoir_sample_1
# ===================================================================
# Pick a single uniformly random element from a stream of unknown length.
# Algorithm R, k=1: keep current with prob 1/i at element i.
def reservoir_sample_1(stream):
    """Return one uniformly random element."""
    # TODO
    pass


def _sol_reservoir_sample_1(stream):
    chosen = None
    for i, x in enumerate(stream, start=1):
        if random.randint(1, i) == 1:
            chosen = x
    return chosen


# ===================================================================
# Exercise 4: estimate_pi
# ===================================================================
# Monte Carlo estimation: ratio of points in unit quarter-circle to
# points in unit square = pi/4. Multiply by 4.
def estimate_pi(n_samples):
    """Return Monte Carlo estimate of pi using n_samples points."""
    # TODO
    pass


def _sol_estimate_pi(n_samples):
    inside = 0
    for _ in range(n_samples):
        x = random.random()
        y = random.random()
        if x * x + y * y <= 1:
            inside += 1
    return 4 * inside / n_samples


# ===================================================================
# Exercise 5: is_probably_prime (Miller-Rabin)
# ===================================================================
def is_probably_prime(n, k=10):
    """Miller-Rabin with k random witnesses."""
    # TODO
    pass


def _sol_is_probably_prime(n, k=10):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


# ===================================================================
# Exercise 6: shuffle_fisher_yates
# ===================================================================
# Produce a uniformly random permutation in place. O(n).
def shuffle_fisher_yates(arr):
    """Return a uniformly shuffled copy of arr."""
    # TODO
    pass


def _sol_shuffle_fisher_yates(arr):
    out = arr[:]
    for i in range(len(out) - 1, 0, -1):
        j = random.randint(0, i)
        out[i], out[j] = out[j], out[i]
    return out


# ===================================================================
# Test runner
# ===================================================================
def run_tests():
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            failed += 1

    random.seed(0)

    print("Exercise 1: rand_quicksort")
    a = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    check("sorted", try_or_sol("rand_quicksort", a) == sorted(a))
    check("empty", try_or_sol("rand_quicksort", []) == [])

    print("\nExercise 2: rand_kth_smallest")
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    check("k=1", try_or_sol("rand_kth_smallest", a, 1) == 1)
    check("k=4", try_or_sol("rand_kth_smallest", a, 4) == 3)
    check("k=8", try_or_sol("rand_kth_smallest", a, 8) == 9)

    print("\nExercise 3: reservoir_sample_1")
    # Empirical uniformity: 5000 samples from {0..9}; each freq should be ~500
    counts = [0] * 10
    for _ in range(5000):
        x = try_or_sol("reservoir_sample_1", iter(range(10)))
        counts[x] += 1
    max_dev = max(abs(c - 500) for c in counts)
    check(f"approx uniform (max dev {max_dev})", max_dev < 120)

    print("\nExercise 4: estimate_pi")
    est = try_or_sol("estimate_pi", 20000)
    check(f"within 0.05 of pi (got {est:.4f})", abs(est - math.pi) < 0.05)

    print("\nExercise 5: is_probably_prime")
    check("97 prime", try_or_sol("is_probably_prime", 97) is True)
    check("100 not prime", try_or_sol("is_probably_prime", 100) is False)
    check("7919 prime", try_or_sol("is_probably_prime", 7919) is True)
    check("561 (Carmichael) not prime", try_or_sol("is_probably_prime", 561) is False)

    print("\nExercise 6: shuffle_fisher_yates")
    a = list(range(20))
    s = try_or_sol("shuffle_fisher_yates", a)
    check("preserves multiset", sorted(s) == a)
    check("doesn't mutate input", a == list(range(20)))

    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
