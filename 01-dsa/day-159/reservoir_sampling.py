"""
Day 159: Reservoir Sampling

- Algorithm R (uniform, k items from unknown-length stream)
- Algorithm A (single-element special case)
- Algorithm L (skip-ahead variant, fewer RNG calls)
- Weighted reservoir sampling (Efraimidis-Spirakis)
- Empirical uniformity verification
"""

import random
import heapq
import math
from collections import Counter


# ---------------------------------------------------------------------------
# 1. Algorithm A — single item from a stream
# ---------------------------------------------------------------------------

def algorithm_a(stream):
    """Return one uniformly random element from stream (unknown length)."""
    chosen = None
    for i, x in enumerate(stream, start=1):
        # Keep current with probability 1/i
        if random.randint(1, i) == 1:
            chosen = x
    return chosen


# ---------------------------------------------------------------------------
# 2. Algorithm R — k items, one RNG call per element
# ---------------------------------------------------------------------------

def algorithm_r(stream, k):
    """
    Return k uniformly random elements from stream (unknown length).
    O(n) time, O(k) memory, one RNG call per element after the first k.
    """
    reservoir = []
    for i, x in enumerate(stream):
        if i < k:
            reservoir.append(x)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = x
    return reservoir


# ---------------------------------------------------------------------------
# 3. Algorithm L — skip-ahead, fewer RNG calls
# ---------------------------------------------------------------------------

def algorithm_l(stream, k):
    """
    Vitter's Algorithm L. Same uniform distribution as Algorithm R but
    skips ahead by sampling from the geometric "next-replacement" distribution.
    """
    it = iter(stream)
    reservoir = []
    try:
        for _ in range(k):
            reservoir.append(next(it))
    except StopIteration:
        return reservoir  # stream shorter than k

    W = math.exp(math.log(random.random()) / k)
    i = k  # 0-indexed position of last item considered

    while True:
        # Skip ahead by `skip` items, then replace at position i + skip + 1
        skip = math.floor(math.log(random.random()) / math.log(1 - W))
        try:
            for _ in range(skip):
                next(it)
                i += 1
            x = next(it)
            i += 1
        except StopIteration:
            break
        reservoir[random.randint(0, k - 1)] = x
        W *= math.exp(math.log(random.random()) / k)

    return reservoir


# ---------------------------------------------------------------------------
# 4. Weighted Reservoir Sampling (Efraimidis-Spirakis)
# ---------------------------------------------------------------------------

def weighted_reservoir(stream, k):
    """
    Sample k items where each (item, weight) has probability proportional to weight.
    stream: iterable of (item, weight) with weight > 0.
    Uses a min-heap of size k keyed by U^(1/w).
    """
    heap = []  # min-heap of (key, item)
    for x, w in stream:
        if w <= 0:
            continue
        u = random.random()
        if u <= 0:
            u = 1e-300  # guard against log(0)
        key = math.log(u) / w  # use log-key for numerical stability
        if len(heap) < k:
            heapq.heappush(heap, (key, x))
        elif key > heap[0][0]:
            heapq.heapreplace(heap, (key, x))
    return [x for _, x in heap]


# ---------------------------------------------------------------------------
# 5. Distributed reservoir sampling — merge per-shard samples
# ---------------------------------------------------------------------------

def distributed_reservoir(shards, k):
    """
    Each shard returns (local_sample, items_seen_in_shard).
    Coordinator picks k from the union, weighted by relative shard size.
    """
    # Treat each shard's sample as a population whose items have equal weight
    # within the shard; the weight per item = shard_size / k (so the shard
    # contributes proportionally to its size when merged).
    weighted_pool = []
    for sample, shard_size in shards:
        if not sample:
            continue
        w = shard_size / len(sample)
        for x in sample:
            weighted_pool.append((x, w))
    return weighted_reservoir(weighted_pool, k)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_uniformity_k1():
    print("=" * 60)
    print("DEMO 1: Algorithm A — empirical uniformity (k=1)")
    print("=" * 60)
    n = 10
    trials = 50_000
    counts = Counter()
    for _ in range(trials):
        counts[algorithm_a(range(n))] += 1
    expected = trials / n
    print(f"\n  Stream = 0..{n-1}, {trials} trials")
    print(f"  Expected count per element: {expected:.0f}")
    print(f"  Item | Count   | Deviation from expected")
    max_dev = 0
    for x in range(n):
        dev = abs(counts[x] - expected)
        max_dev = max(max_dev, dev)
        print(f"   {x:3d} | {counts[x]:7d} | {dev:+.0f}")
    print(f"  Max deviation: {max_dev:.0f} (<3% of {expected:.0f} = uniform)")


def demo_uniformity_r():
    print("\n" + "=" * 60)
    print("DEMO 2: Algorithm R — uniformity for k>1")
    print("=" * 60)
    n = 8
    k = 3
    trials = 30_000
    counts = Counter()
    for _ in range(trials):
        for x in algorithm_r(range(n), k):
            counts[x] += 1
    expected = trials * k / n
    print(f"\n  Stream = 0..{n-1}, k={k}, {trials} trials")
    print(f"  Expected count per element: {expected:.0f}")
    for x in range(n):
        dev = abs(counts[x] - expected)
        bar = "█" * int(counts[x] / expected * 30)
        print(f"   {x}: {counts[x]:6d}  {bar}  (dev {dev:+.0f})")


def demo_algorithm_l_speed():
    print("\n" + "=" * 60)
    print("DEMO 3: Algorithm L — fewer RNG calls than R")
    print("=" * 60)
    import time
    n = 1_000_000
    k = 100

    t0 = time.perf_counter()
    algorithm_r(range(n), k)
    t_r = time.perf_counter() - t0

    t0 = time.perf_counter()
    algorithm_l(range(n), k)
    t_l = time.perf_counter() - t0

    print(f"\n  n={n}, k={k}")
    print(f"  Algorithm R:  {t_r:.4f}s   (~n RNG calls)")
    print(f"  Algorithm L:  {t_l:.4f}s   (~k log(n/k) RNG calls)")
    print(f"  Speedup:      {t_r / t_l:.1f}x")


def demo_weighted():
    print("\n" + "=" * 60)
    print("DEMO 4: Weighted reservoir sampling")
    print("=" * 60)
    # Items with relative weights 1:2:3:4 — should appear in that ratio
    stream = [("A", 1), ("B", 2), ("C", 3), ("D", 4)]
    trials = 20_000
    counts = Counter()
    for _ in range(trials):
        sample = weighted_reservoir(stream, k=1)
        counts[sample[0]] += 1

    total_weight = sum(w for _, w in stream)
    print(f"\n  Items with weights 1:2:3:4 — sample size 1, {trials} trials")
    print(f"  Item | Count   | Empirical  | Expected (weight/total)")
    for x, w in stream:
        emp = counts[x] / trials
        exp = w / total_weight
        print(f"   {x}  | {counts[x]:6d}  |  {emp:.3f}    |  {exp:.3f}")


def demo_distributed():
    print("\n" + "=" * 60)
    print("DEMO 5: Distributed reservoir sampling across shards")
    print("=" * 60)
    random.seed(0)
    # 3 shards of different sizes; sample 5 from each
    shards_raw = [
        list(range(0, 1000)),
        list(range(1000, 1500)),
        list(range(1500, 2500)),
    ]
    shard_samples = [(algorithm_r(s, 5), len(s)) for s in shards_raw]
    final = distributed_reservoir(shard_samples, k=10)
    print(f"\n  3 shards (sizes {[len(s) for s in shards_raw]}), local samples of 5 each")
    print(f"  Final merged sample (k=10): {sorted(final)}")
    print("  Items from larger shards should dominate.")


if __name__ == "__main__":
    random.seed(42)
    demo_uniformity_k1()
    demo_uniformity_r()
    demo_algorithm_l_speed()
    demo_weighted()
    demo_distributed()
