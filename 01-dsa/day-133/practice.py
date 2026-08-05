"""
Day 133 Practice: Online vs Offline — Belady's Optimum & Competitive Ratio

6 exercises. Implement TODOs, then run: python practice.py

Self-contained on purpose: no day-070 import, so the suite is green wherever
it runs. The concept file is where LRU gets measured.
"""

import random
from bisect import bisect_right
from collections import defaultdict, deque
from functools import lru_cache

INF = float("inf")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


TRACE = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
ANOMALY = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def _random_trace(n, distinct, seed):
    rng = random.Random(seed)
    return [rng.randrange(distinct) for _ in range(n)]


# ---------------------------------------------------------------------------
# Exercise 1: Belady's MIN — the offline optimum
# ---------------------------------------------------------------------------

def belady_faults(requests, capacity):
    """
    Page faults when you can see the future: on a fault, evict the cached page
    whose NEXT use is farthest ahead (never used again = infinitely far).
    """
    # TODO: precompute where each page appears, then evict by next-use
    pass


def _sol_belady_faults(requests, capacity):
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    positions = defaultdict(list)
    for i, page in enumerate(requests):
        positions[page].append(i)

    def next_use(page, after):
        lst = positions[page]
        j = bisect_right(lst, after)
        return lst[j] if j < len(lst) else INF

    cache = set()
    faults = 0
    for i, page in enumerate(requests):
        if page in cache:
            continue
        faults += 1
        if len(cache) >= capacity:
            # The page we will need last is the cheapest one to lose now.
            cache.discard(max(cache, key=lambda q: next_use(q, i)))
        cache.add(page)
    return faults


# ---------------------------------------------------------------------------
# Exercise 2: FIFO — an online algorithm
# ---------------------------------------------------------------------------

def fifo_faults(requests, capacity):
    """Page faults under FIFO: evict whatever arrived first, hits change nothing."""
    # TODO: a set for membership, a queue for arrival order
    pass


def _sol_fifo_faults(requests, capacity):
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    cache = set()
    order = deque()
    faults = 0
    for page in requests:
        if page in cache:
            continue          # a hit does NOT refresh FIFO order — that is LRU
        faults += 1
        if len(cache) >= capacity:
            cache.discard(order.popleft())
        cache.add(page)
        order.append(page)
    return faults


# ---------------------------------------------------------------------------
# Exercise 3: Exhaustive offline optimum — the referee
# ---------------------------------------------------------------------------

def optimal_faults_bruteforce(requests, capacity):
    """
    Minimum possible faults, found by trying EVERY eviction choice.
    Exponential; short traces only. This is what proves Belady optimal.
    """
    # TODO: memoized recursion on (position, frozenset of cached pages)
    pass


def _sol_optimal_faults_bruteforce(requests, capacity):
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    seq = tuple(requests)

    @lru_cache(maxsize=None)
    def best(i, cache):
        if i == len(seq):
            return 0
        page = seq[i]
        if page in cache:
            return best(i + 1, cache)
        if len(cache) < capacity:
            return 1 + best(i + 1, cache | {page})
        return 1 + min(best(i + 1, (cache - {v}) | {page}) for v in cache)

    out = best(0, frozenset())
    best.cache_clear()   # the memo is keyed on this trace only
    return out


# ---------------------------------------------------------------------------
# Exercise 4: Competitive ratio
# ---------------------------------------------------------------------------

def competitive_ratio(online_cost, offline_cost):
    """
    online / offline for one sequence.
    Offline 0 with online > 0 is unbounded; both 0 is 1.0.
    """
    # TODO: guard the division
    pass


def _sol_competitive_ratio(online_cost, offline_cost):
    if offline_cost == 0:
        return INF if online_cost > 0 else 1.0
    return online_cost / offline_cost


# ---------------------------------------------------------------------------
# Exercise 5: The k-competitive guarantee
# ---------------------------------------------------------------------------

def satisfies_k_competitive(online_cost, offline_cost, k):
    """
    Sleator-Tarjan: ALG(s) <= k*OPT(s) + k for every sequence s.
    The additive term is not decoration — cold-start faults need it.
    """
    # TODO: one comparison
    pass


def _sol_satisfies_k_competitive(online_cost, offline_cost, k):
    return online_cost <= k * offline_cost + k


def _sol_cyclic_worst_case(k, rounds):
    """k+1 pages cycled through a k-page cache: the adversary's sequence."""
    return list(range(k + 1)) * rounds


# ---------------------------------------------------------------------------
# Exercise 6: Belady's anomaly detector
# ---------------------------------------------------------------------------

def find_anomaly(requests, max_capacity=8):
    """
    Capacity pairs (c, c+1) where FIFO faults MORE with the larger cache.
    Return a list of (c, faults_at_c, c+1, faults_at_c_plus_1).
    """
    # TODO: compare consecutive capacities
    pass


def _sol_find_anomaly(requests, max_capacity=8):
    out = []
    for c in range(1, max_capacity):
        a = _sol_fifo_faults(requests, c)
        b = _sol_fifo_faults(requests, c + 1)
        if b > a:  # more memory, more faults — only non-stack policies can
            out.append((c, a, c + 1, b))
    return out


def _monotone_in_capacity(fault_fn, requests, max_capacity=8):
    counts = [fault_fn(requests, c) for c in range(1, max_capacity + 1)]
    return all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: belady_faults")
    check("classic trace, capacity 3",
          try_or_sol("belady_faults", TRACE, 3), 7)
    # Capacity 1: every request for a page other than the last one faults.
    check("capacity 1", try_or_sol("belady_faults", TRACE, 1), 13)
    # Cache big enough for everything: only compulsory misses remain, one per
    # distinct page. Nothing an eviction policy does can beat that.
    check("capacity >= distinct pages leaves only compulsory misses",
          try_or_sol("belady_faults", TRACE, 9), len(set(TRACE)))
    check("empty request stream", try_or_sol("belady_faults", [], 3), 0)

    print("\nExercise 2: fifo_faults")
    check("classic trace, capacity 3", try_or_sol("fifo_faults", TRACE, 3), 10)
    check("capacity >= distinct pages",
          try_or_sol("fifo_faults", TRACE, 9), len(set(TRACE)))
    # The offline optimum can never be beaten by an online algorithm.
    check("FIFO never beats Belady",
          all(try_or_sol("fifo_faults", TRACE, c)
              >= try_or_sol("belady_faults", TRACE, c) for c in range(1, 8)),
          True)

    print("\nExercise 3: optimal_faults_bruteforce")
    check("agrees with Belady on the classic trace",
          try_or_sol("optimal_faults_bruteforce", TRACE, 3), 7)
    agree = True
    for seed in (1, 2, 3, 4):
        trace = _random_trace(14, 5, seed=seed)
        for capacity in (2, 3):
            if try_or_sol("optimal_faults_bruteforce", trace, capacity) \
                    != try_or_sol("belady_faults", trace, capacity):
                agree = False
    check("Belady is optimal on every random short trace", agree, True)
    # No online algorithm can beat the exhaustive offline optimum.
    check("optimum is a lower bound for FIFO",
          try_or_sol("optimal_faults_bruteforce", ANOMALY, 3) <=
          try_or_sol("fifo_faults", ANOMALY, 3), True)

    print("\nExercise 4: competitive_ratio")
    check("10 vs 5", try_or_sol("competitive_ratio", 10, 5), 2.0)
    check("equal costs", try_or_sol("competitive_ratio", 7, 7), 1.0)
    check("free for both", try_or_sol("competitive_ratio", 0, 0), 1.0)
    check("offline free, online not", try_or_sol("competitive_ratio", 3, 0), INF)

    print("\nExercise 5: satisfies_k_competitive")
    check("obeys the bound", try_or_sol("satisfies_k_competitive", 10, 3, 4), True)
    # 100 > 4*3 + 4 = 16
    check("violates the bound",
          try_or_sol("satisfies_k_competitive", 100, 3, 4), False)
    # Without the additive +k, 4 faults against an optimum of 0 would fail the
    # test at every c. The term is what makes the guarantee statable at all.
    check("additive term covers cold start",
          try_or_sol("satisfies_k_competitive", 4, 0, 4), True)
    # FIFO on the adversarial cycle: faults every request, and still obeys k.
    holds = True
    for k in (2, 3, 4, 5):
        seq = _sol_cyclic_worst_case(k, rounds=12)
        if not try_or_sol("satisfies_k_competitive",
                          try_or_sol("fifo_faults", seq, k),
                          try_or_sol("belady_faults", seq, k), k):
            holds = False
    check("FIFO stays k-competitive on the adversary sequence", holds, True)
    # And the adversary really does make FIFO fault on every single request.
    adv = _sol_cyclic_worst_case(3, rounds=12)
    check("adversary makes FIFO fault every time",
          try_or_sol("fifo_faults", adv, 3), len(adv))

    print("\nExercise 6: find_anomaly")
    check("FIFO anomaly at capacity 3 -> 4",
          try_or_sol("find_anomaly", ANOMALY), [(3, 9, 4, 10)])
    check("no anomaly on the classic trace",
          try_or_sol("find_anomaly", TRACE), [])
    # Belady is a stack algorithm: more memory never costs more faults.
    check("Belady is monotone in capacity",
          _monotone_in_capacity(lambda r, c: try_or_sol("belady_faults", r, c),
                                ANOMALY), True)
    check("FIFO is not",
          _monotone_in_capacity(lambda r, c: try_or_sol("fifo_faults", r, c),
                                ANOMALY), False)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
