"""
Day 67 Practice: Perfect Hashing Exercises

5 exercises to deepen your understanding of perfect hashing.
Each exercise has a description, starter code, and test cases.

Run:
    python practice.py

Rules:
- You may import from perfect_hash.py in this directory
- Implement the functions marked with TODO
- Solutions are at the bottom — try before looking
"""

import sys
import os
import random
import time
import bisect

# Add current directory to path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from perfect_hash import FKSPerfectHash, MinimalPerfectHash, _string_to_int, _make_universal_hash, _PRIME


# ---------------------------------------------------------------------------
# Exercise 1: Verify the FKS space bound
# ---------------------------------------------------------------------------

def exercise1_verify_space_bound(key_sets: list[list[str]]) -> list[dict]:
    """
    For each key set, build an FKS perfect hash and measure:
    - n (number of keys)
    - total second-level space (sum of ni^2)
    - space ratio (total_space / n)

    Verify that the space ratio is <= 4 for all sets.
    Return a list of dicts with keys: 'n', 'total_space', 'ratio', 'within_bound'.

    TODO: Implement this function.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 2: Count second-level construction trials
# ---------------------------------------------------------------------------

def exercise2_count_trials(keys: list[str], num_experiments: int = 10) -> dict:
    """
    Build the FKS perfect hash `num_experiments` times (with different random
    seeds) and collect statistics on second-level hash trials:
    - Average trials per non-empty bucket
    - Max trials across all buckets and experiments
    - Verify that average is close to 2 (as predicted by birthday paradox)

    Return dict with keys: 'avg_trials', 'max_trials', 'all_averages'.

    TODO: Implement this function.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 3: HTTP status code lookup table via perfect hashing
# ---------------------------------------------------------------------------

HTTP_STATUS_CODES = {
    "200": "OK",
    "201": "Created",
    "204": "No Content",
    "301": "Moved Permanently",
    "302": "Found",
    "304": "Not Modified",
    "400": "Bad Request",
    "401": "Unauthorized",
    "403": "Forbidden",
    "404": "Not Found",
    "405": "Method Not Allowed",
    "408": "Request Timeout",
    "429": "Too Many Requests",
    "500": "Internal Server Error",
    "502": "Bad Gateway",
    "503": "Service Unavailable",
    "504": "Gateway Timeout",
}


def exercise3_http_status_lookup(code: str) -> str | None:
    """
    Build a perfect hash table for HTTP status codes (build once, reuse).
    Given a status code string, return the description or None.

    Requirements:
    - Use FKSPerfectHash to determine membership
    - Store associated values so you can return the description
    - Must be O(1) worst case

    TODO: Implement this function (including building the structure).
    Hint: You need to augment FKSPerfectHash or build a parallel lookup.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 4: Ordered perfect hashing (rank queries)
# ---------------------------------------------------------------------------

def exercise4_ordered_perfect_hash(keys: list[str]) -> object:
    """
    Build an ordered minimal perfect hash: keys map to [0, n-1] in
    sorted order. This enables O(1) rank queries: "what is the rank
    of this key among all keys?"

    Return an object/dict with:
    - 'lookup(key)' -> rank (0-based index in sorted order), or None
    - 'mapping' -> dict of key -> rank for verification

    TODO: Implement this function.
    Hint: Build a MinimalPerfectHash, then create a remapping so that
    sorted_keys[i] maps to i.
    """
    pass


# ---------------------------------------------------------------------------
# Exercise 5: Performance comparison — perfect hash vs dict vs binary search
# ---------------------------------------------------------------------------

def exercise5_performance_comparison(keys: list[str], num_lookups: int = 500_000) -> dict:
    """
    Compare lookup performance for a static key set:
    1. FKS Perfect Hash
    2. Python dict
    3. Sorted array + binary search

    Perform num_lookups random lookups (mix of hits and misses).
    Return dict with timing results for each method.

    TODO: Implement this function.
    """
    pass


# ===========================================================================
# TESTS
# ===========================================================================

def test_exercise1():
    print("=" * 60)
    print("Exercise 1: Verify FKS Space Bound")
    print("=" * 60)

    import keyword
    key_sets = [
        keyword.kwlist,
        [f"key_{i}" for i in range(50)],
        [f"item_{i:04d}" for i in range(200)],
        ["alpha", "beta", "gamma", "delta", "epsilon"],
        [f"x{i}" for i in range(500)],
    ]

    results = exercise1_verify_space_bound(key_sets)
    if results is None:
        print("  NOT IMPLEMENTED\n")
        return False

    all_pass = True
    for i, r in enumerate(results):
        status = "PASS" if r['within_bound'] else "FAIL"
        print(f"  Set {i}: n={r['n']:>4d}, space={r['total_space']:>6d}, "
              f"ratio={r['ratio']:.2f}  [{status}]")
        if not r['within_bound']:
            all_pass = False

    print(f"\n  All within O(n) bound: {all_pass}\n")
    return all_pass


def test_exercise2():
    print("=" * 60)
    print("Exercise 2: Count Second-Level Construction Trials")
    print("=" * 60)

    import keyword
    keys = keyword.kwlist

    result = exercise2_count_trials(keys, num_experiments=20)
    if result is None:
        print("  NOT IMPLEMENTED\n")
        return False

    print(f"  Keys: {len(keys)} Python keywords")
    print(f"  Experiments: 20")
    print(f"  Average trials per bucket: {result['avg_trials']:.2f}")
    print(f"  Max trials in any bucket:  {result['max_trials']}")
    print(f"  Per-experiment averages:   "
          f"[{', '.join(f'{a:.1f}' for a in result['all_averages'][:5])}...]")

    close_to_two = result['avg_trials'] < 5.0  # generous bound
    print(f"\n  Average close to expected ~2: {close_to_two}\n")
    return close_to_two


def test_exercise3():
    print("=" * 60)
    print("Exercise 3: HTTP Status Code Lookup")
    print("=" * 60)

    test_cases = [
        ("200", "OK"),
        ("404", "Not Found"),
        ("500", "Internal Server Error"),
        ("999", None),
        ("", None),
        ("200x", None),
    ]

    all_pass = True
    for code, expected in test_cases:
        result = exercise3_http_status_lookup(code)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_pass = False
        print(f"  {code!r:>6s} -> {str(result):<30s} [{status}]")

    print(f"\n  All correct: {all_pass}\n")
    return all_pass


def test_exercise4():
    print("=" * 60)
    print("Exercise 4: Ordered Perfect Hashing (Rank Queries)")
    print("=" * 60)

    keys = ["banana", "apple", "cherry", "date", "elderberry", "fig", "grape"]
    sorted_keys = sorted(keys)

    result = exercise4_ordered_perfect_hash(keys)
    if result is None:
        print("  NOT IMPLEMENTED\n")
        return False

    mapping = result['mapping']
    lookup = result['lookup']

    all_pass = True
    for i, k in enumerate(sorted_keys):
        rank = lookup(k)
        status = "PASS" if rank == i else "FAIL"
        if rank != i:
            all_pass = False
        print(f"  rank('{k}') = {rank}  (expected {i})  [{status}]")

    # Test non-existent key
    none_result = lookup("zzz")
    none_pass = none_result is None
    print(f"  rank('zzz') = {none_result}  (expected None)  "
          f"[{'PASS' if none_pass else 'FAIL'}]")

    all_pass = all_pass and none_pass
    print(f"\n  All ranks correct: {all_pass}\n")
    return all_pass


def test_exercise5():
    print("=" * 60)
    print("Exercise 5: Performance Comparison")
    print("=" * 60)

    import keyword
    keys = keyword.kwlist

    result = exercise5_performance_comparison(keys, num_lookups=200_000)
    if result is None:
        print("  NOT IMPLEMENTED\n")
        return False

    print(f"  {'Method':<30s} {'Time (ms)':>10s} {'ns/lookup':>12s}")
    print(f"  {'-'*52}")
    for method, data in result.items():
        print(f"  {method:<30s} {data['time_ms']:>10.1f} "
              f"{data['ns_per_lookup']:>12.1f}")

    print(f"\n  (Python dict is C-optimized; FKS is pure Python.)")
    print(f"  The value is worst-case O(1) guarantee, not raw speed.\n")
    return True


# ===========================================================================
# SOLUTIONS (try to implement before looking!)
# ===========================================================================

def _solution_exercise1(key_sets):
    results = []
    for keys in key_sets:
        ph = FKSPerfectHash()
        ph.build(keys)
        n = ph.n
        total = ph.total_space()
        ratio = ph.space_ratio()
        results.append({
            'n': n,
            'total_space': total,
            'ratio': ratio,
            'within_bound': ratio <= 4.0,
        })
    return results


def _solution_exercise2(keys, num_experiments=10):
    all_avgs = []
    all_maxes = []

    for i in range(num_experiments):
        random.seed(i * 1000 + 7)
        ph = FKSPerfectHash()
        ph.build(keys)

        nonzero = [t for t in ph.second_level_trials if t > 0]
        if nonzero:
            all_avgs.append(sum(nonzero) / len(nonzero))
            all_maxes.append(max(nonzero))

    return {
        'avg_trials': sum(all_avgs) / len(all_avgs) if all_avgs else 0,
        'max_trials': max(all_maxes) if all_maxes else 0,
        'all_averages': all_avgs,
    }


# For exercise 3, we build the structure once at module level (static set)
_http_ph = None
_http_values = {}


def _build_http_lookup():
    global _http_ph, _http_values
    _http_ph = FKSPerfectHash()
    codes = list(HTTP_STATUS_CODES.keys())
    _http_ph.build(codes)
    _http_values = dict(HTTP_STATUS_CODES)


def _solution_exercise3(code):
    global _http_ph
    if _http_ph is None:
        _build_http_lookup()
    if _http_ph.lookup(code):
        return _http_values[code]
    return None


def _solution_exercise4(keys):
    sorted_keys = sorted(set(keys))
    # Direct mapping: sorted position is the rank
    rank_map = {k: i for i, k in enumerate(sorted_keys)}
    key_set = set(sorted_keys)

    def lookup(key):
        if key not in key_set:
            return None
        return rank_map[key]

    return {
        'lookup': lookup,
        'mapping': dict(rank_map),
    }


def _solution_exercise5(keys, num_lookups=500_000):
    # Build structures
    ph = FKSPerfectHash()
    ph.build(keys)

    py_dict = {k: True for k in keys}

    sorted_keys = sorted(keys)

    # Generate test keys: half hits, half misses
    test_keys = list(keys) + [f"__miss_{i}__" for i in range(len(keys))]

    results = {}

    # FKS Perfect Hash
    start = time.perf_counter()
    for i in range(num_lookups):
        ph.lookup(test_keys[i % len(test_keys)])
    elapsed = time.perf_counter() - start
    results['FKS Perfect Hash'] = {
        'time_ms': elapsed * 1000,
        'ns_per_lookup': elapsed / num_lookups * 1e9,
    }

    # Python dict
    start = time.perf_counter()
    for i in range(num_lookups):
        test_keys[i % len(test_keys)] in py_dict
    elapsed = time.perf_counter() - start
    results['Python dict'] = {
        'time_ms': elapsed * 1000,
        'ns_per_lookup': elapsed / num_lookups * 1e9,
    }

    # Binary search
    start = time.perf_counter()
    for i in range(num_lookups):
        k = test_keys[i % len(test_keys)]
        idx = bisect.bisect_left(sorted_keys, k)
        _ = idx < len(sorted_keys) and sorted_keys[idx] == k
    elapsed = time.perf_counter() - start
    results['Sorted array + bisect'] = {
        'time_ms': elapsed * 1000,
        'ns_per_lookup': elapsed / num_lookups * 1e9,
    }

    return results


# ===========================================================================
# Wire up solutions (replace with your implementations above!)
# ===========================================================================

# Comment out these lines and implement the functions above yourself:
exercise1_verify_space_bound = _solution_exercise1
exercise2_count_trials = _solution_exercise2
exercise3_http_status_lookup = _solution_exercise3
exercise4_ordered_perfect_hash = _solution_exercise4
exercise5_performance_comparison = _solution_exercise5


if __name__ == "__main__":
    random.seed(42)
    passed = 0
    total = 5

    if test_exercise1(): passed += 1
    if test_exercise2(): passed += 1
    if test_exercise3(): passed += 1
    if test_exercise4(): passed += 1
    if test_exercise5(): passed += 1

    print("=" * 60)
    print(f"Results: {passed}/{total} exercises passing")
    print("=" * 60)
