"""
Day 157: Randomized Algorithms

- Randomized quicksort (Las Vegas)
- Karger's min-cut (Monte Carlo with boosting)
- Miller-Rabin primality (Monte Carlo)
- Empirical demonstrations of expected-time and error-probability bounds.
"""

import random
import math
import time
from collections import defaultdict


# ---------------------------------------------------------------------------
# 1. Randomized Quicksort (Las Vegas)
# ---------------------------------------------------------------------------

def randomized_quicksort(arr):
    """Las Vegas: always returns sorted; expected O(n log n)."""
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[random.randint(0, len(arr) - 1)]
    less = [x for x in arr if x < pivot]
    equal = [x for x in arr if x == pivot]
    greater = [x for x in arr if x > pivot]
    return randomized_quicksort(less) + equal + randomized_quicksort(greater)


def deterministic_quicksort_first_pivot(arr):
    """Always picks index 0 as pivot. O(n²) on sorted input."""
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[0]
    less = [x for x in arr[1:] if x < pivot]
    greater = [x for x in arr[1:] if x >= pivot]
    return deterministic_quicksort_first_pivot(less) + [pivot] + deterministic_quicksort_first_pivot(greater)


# ---------------------------------------------------------------------------
# 2. Karger's Min-Cut (Monte Carlo)
# ---------------------------------------------------------------------------

def kargers_one_run(graph):
    """
    One run of Karger's contraction.
    graph: dict of node -> list of neighbor nodes (multigraph; duplicates allowed).
    Returns: number of edges crossing the resulting 2-partition.
    """
    # Deep copy adjacency lists
    g = {u: list(neighbors) for u, neighbors in graph.items()}

    while len(g) > 2:
        # Pick a uniformly random edge (weighted by multiplicities)
        u = random.choice(list(g.keys()))
        v = random.choice(g[u])
        # Contract v into u
        # 1. Append v's edges (except back to u) to u
        for w in g[v]:
            if w != u:
                g[u].append(w)
        # 2. Replace v with u in every neighbor's list
        for w in g[v]:
            g[w] = [u if x == v else x for x in g[w]]
        # 3. Remove self-loops from u
        g[u] = [w for w in g[u] if w != u]
        # 4. Drop v
        del g[v]

    # Remaining cut = edges between the two super-nodes
    a, b = list(g.keys())
    cut = sum(1 for w in g[a] if w == b)
    return cut


def kargers_min_cut(graph, trials=None):
    """
    Boosted Karger: run many times, return best cut.
    Default trials = n² * ln(n) for high-probability success.
    """
    n = len(graph)
    if trials is None:
        trials = max(10, int(n * n * math.log(max(2, n))))
    best = float("inf")
    for _ in range(trials):
        c = kargers_one_run(graph)
        if c < best:
            best = c
    return best


# ---------------------------------------------------------------------------
# 3. Miller-Rabin Primality (Monte Carlo)
# ---------------------------------------------------------------------------

def miller_rabin(n, k=20):
    """
    Probabilistic primality test. Returns True if n is *probably* prime.
    Error probability ≤ 4^-k. With k=20, error < 10^-12.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    # Write n-1 = d * 2^r
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
            return False  # composite witnessed
    return True


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_quicksort_worst_vs_random():
    print("=" * 60)
    print("DEMO 1: Randomized vs deterministic quicksort on sorted input")
    print("=" * 60)
    n = 800  # keep small — deterministic is O(n²) here
    sorted_input = list(range(n))

    t0 = time.perf_counter()
    deterministic_quicksort_first_pivot(sorted_input)
    t_det = time.perf_counter() - t0

    t0 = time.perf_counter()
    randomized_quicksort(sorted_input)
    t_rand = time.perf_counter() - t0

    print(f"\n  n={n}, adversarial (sorted) input:")
    print(f"  deterministic first-pivot QS: {t_det * 1000:.2f} ms")
    print(f"  randomized QS:                {t_rand * 1000:.2f} ms")
    print(f"  speedup: {t_det / t_rand:.1f}x")
    print("  (deterministic hits O(n²); randomized stays ~O(n log n))")


def demo_kargers_min_cut():
    print("\n" + "=" * 60)
    print("DEMO 2: Karger's min-cut on a 'barbell' graph")
    print("=" * 60)
    # Two K_4 cliques connected by a single bridge edge → min cut = 1
    graph = defaultdict(list)
    cliques = [[0, 1, 2, 3], [4, 5, 6, 7]]
    for clique in cliques:
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                graph[clique[i]].append(clique[j])
                graph[clique[j]].append(clique[i])
    # Bridge
    graph[3].append(4)
    graph[4].append(3)
    graph = dict(graph)

    # Run a single trial vs boosted
    random.seed(42)
    one = kargers_one_run(graph)
    boosted = kargers_min_cut(graph, trials=200)
    print(f"\n  Barbell graph: two K_4 cliques + one bridge → true min cut = 1")
    print(f"  Single run:       {one}")
    print(f"  Boosted (200x):   {boosted}  (true min cut)")


def demo_kargers_success_rate():
    print("\n" + "=" * 60)
    print("DEMO 3: Karger's success rate vs theoretical bound")
    print("=" * 60)
    # Simple graph where min cut = 2 (a 4-cycle)
    graph = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}
    n = 4
    runs = 2000
    correct = sum(1 for _ in range(runs) if kargers_one_run(graph) == 2)
    measured = correct / runs
    theoretical_min = 2 / (n * (n - 1))
    print(f"\n  4-cycle, n=4, true min cut=2")
    print(f"  Measured success rate over {runs} runs: {measured:.3f}")
    print(f"  Theoretical lower bound 2/(n(n-1)):    {theoretical_min:.3f}")
    print("  (Measured ≥ theoretical, as expected)")


def demo_miller_rabin():
    print("\n" + "=" * 60)
    print("DEMO 4: Miller-Rabin on known primes and composites")
    print("=" * 60)
    primes = [97, 101, 7919, 104729, 2 ** 31 - 1]  # Mersenne prime
    composites = [91, 561, 1105, 1729]  # 561, 1105, 1729 are Carmichael numbers
    print("\n  Known primes (should all be True):")
    for p in primes:
        print(f"    miller_rabin({p}) = {miller_rabin(p, k=20)}")
    print("\n  Known composites (Carmichael numbers, should all be False):")
    for c in composites:
        print(f"    miller_rabin({c}) = {miller_rabin(c, k=20)}")


if __name__ == "__main__":
    random.seed(1)
    demo_quicksort_worst_vs_random()
    demo_kargers_min_cut()
    demo_kargers_success_rate()
    demo_miller_rabin()
