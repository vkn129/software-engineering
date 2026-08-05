"""
Day 159 Practice: Reservoir Sampling

6 exercises. Run: python practice.py
"""

import random
import math
from collections import Counter


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: reservoir_one
# ===================================================================
# Algorithm A — return ONE uniformly random element from a stream.
def reservoir_one(stream):
    """Single uniform random element."""
    # TODO
    pass


def _sol_reservoir_one(stream):
    chosen = None
    for i, x in enumerate(stream, start=1):
        if random.randint(1, i) == 1:
            chosen = x
    return chosen


# ===================================================================
# Exercise 2: reservoir_k
# ===================================================================
# Algorithm R — return k uniformly random elements.
def reservoir_k(stream, k):
    """List of k uniform random elements (without replacement)."""
    # TODO
    pass


def _sol_reservoir_k(stream, k):
    reservoir = []
    for i, x in enumerate(stream):
        if i < k:
            reservoir.append(x)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = x
    return reservoir


# ===================================================================
# Exercise 3: prob_in_reservoir
# ===================================================================
# After seeing n items with reservoir size k, what's the probability
# that any specific item is in the reservoir? Return as a float.
def prob_in_reservoir(n, k):
    """Probability of inclusion after stream of length n."""
    # TODO
    pass


def _sol_prob_in_reservoir(n, k):
    if n <= 0:
        return 0.0
    if k >= n:
        return 1.0
    return k / n


# ===================================================================
# Exercise 4: reservoir_with_replacement
# ===================================================================
# Return k items sampled WITH replacement. Hint: run k independent
# reservoir-of-1 sampers in parallel.
def reservoir_with_replacement(stream, k):
    """k uniform samples WITH replacement."""
    # TODO
    pass


def _sol_reservoir_with_replacement(stream, k):
    samples = [None] * k
    for i, x in enumerate(stream, start=1):
        for s in range(k):
            if random.randint(1, i) == 1:
                samples[s] = x
    return samples


# ===================================================================
# Exercise 5: weighted_sample_one
# ===================================================================
# Pick ONE item from a stream of (item, weight) pairs proportional to weight.
# Use the "A-Res" log-key approach.
def weighted_sample_one(stream):
    """Return the chosen item."""
    # TODO
    pass


def _sol_weighted_sample_one(stream):
    best_key = -math.inf
    best_item = None
    for x, w in stream:
        if w <= 0:
            continue
        u = random.random()
        if u <= 0:
            u = 1e-300
        key = math.log(u) / w
        if key > best_key:
            best_key = key
            best_item = x
    return best_item


# ===================================================================
# Exercise 6: stream_count_uniform
# ===================================================================
# Helper to test uniformity: run `trials` reservoir_one samples on
# stream `range(n)` and return a list of counts of length n.
def stream_count_uniform(n, trials, sampler):
    """Return counts[i] = number of trials where sampler returned i."""
    # TODO
    pass


def _sol_stream_count_uniform(n, trials, sampler):
    counts = [0] * n
    for _ in range(trials):
        x = sampler(range(n))
        counts[x] += 1
    return counts


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

    print("Exercise 1: reservoir_one")
    val = try_or_sol("reservoir_one", iter([42]))
    check("single-element stream returns it", val == 42)
    # Uniformity
    counts = try_or_sol("stream_count_uniform", 10, 8000,
                        lambda s: _sol_reservoir_one(s))
    max_dev = max(abs(c - 800) for c in counts)
    check(f"uniform on 10 items (max dev {max_dev})", max_dev < 130)

    print("\nExercise 2: reservoir_k")
    res = try_or_sol("reservoir_k", iter(range(5)), 5)
    check("k=n returns whole stream", sorted(res) == list(range(5)))
    res = try_or_sol("reservoir_k", iter(range(100)), 10)
    check("k items from longer stream", len(res) == 10)
    check("all distinct", len(set(res)) == 10)

    # Uniformity: each item should appear in sample with prob k/n
    n, k, trials = 8, 3, 8000
    counts = [0] * n
    for _ in range(trials):
        for x in try_or_sol("reservoir_k", iter(range(n)), k):
            counts[x] += 1
    expected = trials * k / n
    max_dev = max(abs(c - expected) for c in counts)
    check(f"reservoir_k uniform (max dev {max_dev:.0f})", max_dev < 0.08 * expected)

    print("\nExercise 3: prob_in_reservoir")
    check("k=10, n=100 → 0.1", abs(try_or_sol("prob_in_reservoir", 100, 10) - 0.1) < 1e-9)
    check("k>=n → 1.0", try_or_sol("prob_in_reservoir", 5, 10) == 1.0)
    check("n=0 → 0.0", try_or_sol("prob_in_reservoir", 0, 5) == 0.0)

    print("\nExercise 4: reservoir_with_replacement")
    res = try_or_sol("reservoir_with_replacement", iter([1]), 5)
    check("singleton stream → all 1s", res == [1, 1, 1, 1, 1])
    n, k, trials = 5, 4, 5000
    counts = [0] * n
    for _ in range(trials):
        for x in try_or_sol("reservoir_with_replacement", iter(range(n)), k):
            counts[x] += 1
    # Each slot independently uniform → each item appears ~k*trials/n times
    expected = k * trials / n
    max_dev = max(abs(c - expected) for c in counts)
    check(f"empirically uniform (max dev {max_dev:.0f})", max_dev < 0.06 * expected)

    print("\nExercise 5: weighted_sample_one")
    trials = 12000
    counts = Counter()
    for _ in range(trials):
        x = try_or_sol("weighted_sample_one", iter([("A", 1), ("B", 3)]))
        counts[x] += 1
    ratio_b = counts["B"] / trials
    check(f"B chosen ~75% (got {ratio_b:.3f})", abs(ratio_b - 0.75) < 0.04)

    print("\nExercise 6: stream_count_uniform")
    counts = try_or_sol("stream_count_uniform", 5, 1000, lambda s: _sol_reservoir_one(s))
    check("length matches n", len(counts) == 5)
    check("sums to trials", sum(counts) == 1000)

    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
