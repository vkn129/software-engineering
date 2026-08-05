"""
Day 133 Mini-Project: Online vs Offline — Belady's Optimum & Competitive Ratio

The question this project answers is not "which cache eviction policy is
fastest". It is: **how much does not knowing the future cost you?**

  OFFLINE  — the whole request sequence is known in advance.
             Belady's MIN is the optimal offline paging algorithm.
  ONLINE   — decisions must be made request by request, with no lookahead.
             LRU (day-070) is the canonical online algorithm.

The gap between them, measured as a worst-case ratio, is the COMPETITIVE
RATIO. It puts a number on the price of ignorance.

LRU lives in day-070 and is imported, not rewritten. FIFO is defined here
because it is the vehicle for Belady's ANOMALY, which is a different
phenomenon that happens to share his name.

Standard library only.
"""

import importlib.util
import os
import random
from bisect import bisect_right
from collections import defaultdict, deque
from functools import lru_cache

INF = float("inf")


# ---------------------------------------------------------------------------
# Reuse day-070's LRU rather than reimplementing it
# ---------------------------------------------------------------------------

_LRU_CLASS = None
_LRU_LOADED = False


def load_lru_class():
    """
    Import LRUCache from day-070/cache.py.

    Day directories are not importable package names ("day-070" has a hyphen),
    so we load the file by path. Returns None if day-070 is not next to us —
    the caller decides whether that is fatal, rather than this function
    silently substituting a different cache.
    """
    global _LRU_CLASS, _LRU_LOADED
    if _LRU_LOADED:
        return _LRU_CLASS
    _LRU_LOADED = True
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.normpath(os.path.join(here, "..", "day-070", "cache.py"))
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location("_day070_cache", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _LRU_CLASS = module.LRUCache
    return _LRU_CLASS


def lru_faults(requests, capacity):
    """
    Page faults under LRU, using day-070's implementation verbatim.
    Raises if day-070 is unavailable — a missing baseline is not a zero.
    """
    LRUCache = load_lru_class()
    if LRUCache is None:
        raise FileNotFoundError(
            "day-070/cache.py not found; LRU is defined there, not here")
    cache = LRUCache(capacity)
    for page in requests:
        if cache.get(page) is None:      # `is None`: page id 0 is a real page
            cache.put(page, page)
    return cache.stats.misses


# ---------------------------------------------------------------------------
# 1. FIFO — the other online algorithm, and the anomaly vehicle
# ---------------------------------------------------------------------------

def fifo_faults(requests, capacity):
    """
    Page faults under FIFO. Evict whatever arrived first, regardless of use.

    FIFO is here because of Belady's ANOMALY: giving FIFO MORE memory can
    make it fault MORE. LRU cannot do that, and neither can Belady's MIN.
    """
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    cache = set()
    order = deque()
    faults = 0
    for page in requests:
        if page in cache:
            continue                     # FIFO ignores hits entirely
        faults += 1
        if len(cache) >= capacity:
            evicted = order.popleft()
            cache.discard(evicted)
        cache.add(page)
        order.append(page)
    return faults


# ---------------------------------------------------------------------------
# 2. Belady's MIN — the offline optimum
# ---------------------------------------------------------------------------

def _next_use_table(requests):
    """page -> sorted list of the indices where it is requested."""
    positions = defaultdict(list)
    for i, page in enumerate(requests):
        positions[page].append(i)
    return positions


def _next_use(positions, page, after):
    """First index strictly greater than `after` where `page` appears, else INF."""
    lst = positions[page]
    j = bisect_right(lst, after)
    return lst[j] if j < len(lst) else INF


def belady_faults(requests, capacity):
    """
    Page faults under Belady's MIN: on a fault, evict the page whose NEXT use
    is farthest in the future (never used again = infinitely far).

    Unimplementable in a real system — it needs the future — which is exactly
    why it is useful. It is the yardstick, not the product.
    """
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    positions = _next_use_table(requests)
    cache = set()
    faults = 0
    for i, page in enumerate(requests):
        if page in cache:
            continue
        faults += 1
        if len(cache) >= capacity:
            victim = max(cache, key=lambda q: _next_use(positions, q, i))
            cache.discard(victim)
        cache.add(page)
    return faults


def belady_trace(requests, capacity):
    """
    Same algorithm, but returns the story: one row per request as
    (page, "hit"/"fault", evicted_or_None, cache_after_sorted).
    """
    positions = _next_use_table(requests)
    cache = set()
    rows = []
    for i, page in enumerate(requests):
        if page in cache:
            rows.append((page, "hit", None, sorted(cache, key=str)))
            continue
        evicted = None
        if len(cache) >= capacity:
            evicted = max(cache, key=lambda q: _next_use(positions, q, i))
            cache.discard(evicted)
        cache.add(page)
        rows.append((page, "fault", evicted, sorted(cache, key=str)))
    return rows


def optimal_faults_bruteforce(requests, capacity):
    """
    Independent ground truth: search EVERY eviction choice with memoization.

    State is (position, frozenset of cached pages). Exponential in the number
    of distinct pages, so this is a referee for short traces only — but it is
    the only honest way to show Belady's greedy rule really is optimal rather
    than merely plausible.
    """
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

    result = best(0, frozenset())
    best.cache_clear()
    return result


# ---------------------------------------------------------------------------
# 3. Competitive ratio
# ---------------------------------------------------------------------------

def competitive_ratio(online_cost, offline_cost):
    """
    online / offline for one sequence. The COMPETITIVE RATIO of an algorithm
    is the worst case of this over all sequences, so a single number here is
    evidence, never a proof.

    Offline cost 0 with nonzero online cost means unbounded ratio; both zero
    means the sequence cost nothing and the ratio is 1.
    """
    if offline_cost == 0:
        return INF if online_cost > 0 else 1.0
    return online_cost / offline_cost


def satisfies_k_competitive(online_cost, offline_cost, k):
    """
    The Sleator-Tarjan guarantee: ALG(s) <= k*OPT(s) + k for every sequence s.

    The additive `+ k` matters. Without it the claim is false on short
    sequences, where cold-start faults dominate and no policy can avoid them.
    """
    return online_cost <= k * offline_cost + k


def cyclic_worst_case(k, rounds):
    """
    The sequence that proves no deterministic online algorithm beats k.

    Cycle through k+1 distinct pages with a cache of size k. Whatever the
    online algorithm keeps, the next request is the one it just threw away,
    so it faults every single time. Belady, seeing the whole cycle, faults
    about once every k requests.
    """
    return list(range(k + 1)) * rounds


# ---------------------------------------------------------------------------
# 4. Belady's anomaly (FIFO only)
# ---------------------------------------------------------------------------

ANOMALY_SEQUENCE = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def find_anomaly(requests, max_capacity=8):
    """
    Capacities (c, c+1) where FIFO faults MORE with the larger cache.
    Returns a list of (c, faults_c, c+1, faults_c_plus_1).
    """
    out = []
    for c in range(1, max_capacity):
        a = fifo_faults(requests, c)
        b = fifo_faults(requests, c + 1)
        if b > a:
            out.append((c, a, c + 1, b))
    return out


def is_stack_algorithm(fault_fn, requests, max_capacity=8):
    """
    A STACK algorithm's cache with k frames is always a subset of its cache
    with k+1 frames, which forces faults to be non-increasing in capacity.
    LRU and Belady are stack algorithms; FIFO is not. We test the observable
    consequence: more memory never costs more faults.
    """
    counts = [fault_fn(requests, c) for c in range(1, max_capacity + 1)]
    return all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))


def random_trace(n, distinct, seed):
    """Reproducible random request sequence. Seeded so results are stable."""
    rng = random.Random(seed)
    return [rng.randrange(distinct) for _ in range(n)]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_belady_trace():
    print("=" * 70)
    print("DEMO 1: Belady's MIN, step by step")
    print("=" * 70)
    requests = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    capacity = 3
    print(f"\n  requests = {requests}   capacity = {capacity}\n")
    print("   req  outcome  evicted  cache after")
    for page, outcome, evicted, cache in belady_trace(requests, capacity):
        print(f"   {page:3}  {outcome:7s}  {str(evicted):7s}  {cache}")
    faults = belady_faults(requests, capacity)
    print(f"\n  Belady faults: {faults}")
    print("  Every eviction is the page needed farthest in the future.")


def demo_online_vs_offline():
    print("\n" + "=" * 70)
    print("DEMO 2: What not knowing the future costs")
    print("=" * 70)
    LRUCache = load_lru_class()
    trace = random_trace(400, 12, seed=17)
    print("\n  400 requests over 12 distinct pages (seed 17)\n")
    print("   cap   Belady(offline)   FIFO(online)   LRU(online)   LRU/Belady")
    for capacity in (2, 3, 4, 6, 8):
        opt = belady_faults(trace, capacity)
        fifo = fifo_faults(trace, capacity)
        if LRUCache is None:
            print(f"   {capacity:3}   {opt:15}   {fifo:12}   "
                  f"{'unavailable':>11}   -")
            continue
        lru = lru_faults(trace, capacity)
        ratio = competitive_ratio(lru, opt)
        print(f"   {capacity:3}   {opt:15}   {fifo:12}   {lru:11}   {ratio:10.2f}")
    if LRUCache is None:
        print("\n  NOTE: day-070/cache.py is not beside this file, so the LRU")
        print("  column is blank. LRU is defined there and deliberately not")
        print("  reimplemented here.")


def demo_lower_bound():
    print("\n" + "=" * 70)
    print("DEMO 3: Why no deterministic online algorithm beats k")
    print("=" * 70)
    print("\n  Cache of size k, cycling through k+1 pages. The next request is")
    print("  always the page the online algorithm just evicted.\n")
    print("    k   requests   FIFO   Belady   ratio   k-competitive?")
    for k in (2, 3, 4, 5):
        seq = cyclic_worst_case(k, rounds=12)
        fifo = fifo_faults(seq, k)
        opt = belady_faults(seq, k)
        ok = satisfies_k_competitive(fifo, opt, k)
        print(f"    {k}   {len(seq):8}   {fifo:4}   {opt:6}   "
              f"{competitive_ratio(fifo, opt):5.2f}   {ok}")
    print("\n  FIFO faults on every request; Belady faults roughly once per k.")
    print("  The ratio walks toward k, and Sleator-Tarjan (1985) proved no")
    print("  deterministic online algorithm can do better.")


def demo_anomaly():
    print("\n" + "=" * 70)
    print("DEMO 4: Belady's anomaly — more memory, more faults")
    print("=" * 70)
    seq = ANOMALY_SEQUENCE
    print(f"\n  requests = {seq}\n")
    print("   cap   FIFO   Belady")
    for c in range(1, 6):
        print(f"   {c:3}   {fifo_faults(seq, c):4}   {belady_faults(seq, c):6}")

    hits = find_anomaly(seq)
    print(f"\n  FIFO anomalies (capacity pairs where bigger is worse): {hits}")
    assert hits, "this sequence was chosen to exhibit the anomaly"
    print(f"  FIFO is a stack algorithm?   {is_stack_algorithm(fifo_faults, seq)}")
    print(f"  Belady is a stack algorithm? {is_stack_algorithm(belady_faults, seq)}")
    print("\n  Same name, different phenomenon: Belady's MIN is the optimum,")
    print("  Belady's anomaly is FIFO misbehaving. Only the surname is shared.")


def demo_referee():
    print("\n" + "=" * 70)
    print("DEMO 5: Belady checked against exhaustive search")
    print("=" * 70)
    print("\n   capacity  Belady  exhaustive  trace")
    for seed in (1, 2, 3):
        trace = random_trace(14, 5, seed=seed)
        for capacity in (2, 3):
            greedy = belady_faults(trace, capacity)
            exact = optimal_faults_bruteforce(trace, capacity)
            mark = "OK" if greedy == exact else "MISMATCH"
            print(f"   {capacity:8}  {greedy:6}  {exact:10}  {mark}  {trace}")
            assert greedy == exact, "Belady's greedy rule must be optimal"


if __name__ == "__main__":
    demo_belady_trace()
    demo_online_vs_offline()
    demo_lower_bound()
    demo_anomaly()
    demo_referee()
    print("\nAll day-133 demos complete.")
