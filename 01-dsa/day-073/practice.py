"""
Day 73 Practice: HyperLogLog Exercises

5 exercises exploring HLL properties, accuracy, merging, and trade-offs.
All pure Python 3, no external dependencies.
"""

import random
import math
import sys
import string

# Import our HyperLogLog implementation
sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
from hyperloglog import HyperLogLog


# ---------------------------------------------------------------------------
# Exercise 1: Unique Word Counter — HLL vs HashSet Memory Comparison
# ---------------------------------------------------------------------------

def exercise_1_unique_word_counter():
    """
    Count distinct words in a synthetic text stream using HLL vs a hash set.
    Compare memory usage.

    Real-world analogy: counting unique search queries, unique URLs visited,
    unique words in a corpus — anywhere exact counting is too expensive.
    """
    print("=" * 70)
    print("Exercise 1: Unique Word Counter — HLL vs HashSet")
    print("=" * 70)

    # Generate a synthetic text stream with controlled unique word count
    # Zipf-like distribution: some words appear very often, most appear rarely
    vocab_size = 50_000  # Number of unique words
    stream_size = 500_000  # Total words in stream

    print(f"\n  Generating stream: {stream_size:,} words, {vocab_size:,} unique...")

    # Create vocabulary
    random.seed(42)
    vocabulary = [
        ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 10)))
        for _ in range(vocab_size)
    ]

    # Generate stream with Zipf-like frequencies (common words repeat more)
    # Word i appears with probability proportional to 1/(i+1)
    weights = [1.0 / (i + 1) for i in range(vocab_size)]
    total_weight = sum(weights)
    weights = [w / total_weight for w in weights]

    # Cumulative weights for sampling
    cum_weights = []
    running = 0.0
    for w in weights:
        running += w
        cum_weights.append(running)

    def sample_word():
        r = random.random()
        lo, hi = 0, len(cum_weights) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cum_weights[mid] < r:
                lo = mid + 1
            else:
                hi = mid
        return vocabulary[lo]

    # Count with both methods
    hll = HyperLogLog(p=14)
    exact_set = set()

    for _ in range(stream_size):
        word = sample_word()
        hll.add(word)
        exact_set.add(word)

    exact_count = len(exact_set)
    hll_count = hll.count()

    # Memory comparison
    # HashSet: each Python string ~50 bytes overhead + chars, set entry ~72 bytes
    # Conservative estimate: ~100 bytes per unique word
    set_memory_est = exact_count * 100
    hll_memory = hll.memory_bytes()

    print(f"\n  {'Method':<20} {'Count':>10} {'Memory':>12} {'Error':>8}")
    print("  " + "-" * 52)
    print(f"  {'Exact (HashSet)':<20} {exact_count:>10,} {set_memory_est:>10,} B {'0.00%':>8}")
    print(f"  {'HyperLogLog p=14':<20} {hll_count:>10,} {hll_memory:>10,} B "
          f"{abs(hll_count - exact_count) / exact_count * 100:>7.2f}%")
    print(f"\n  Memory ratio: {set_memory_est / hll_memory:,.0f}x less memory with HLL")
    print(f"  Actual unique words in stream: {exact_count:,} (out of {vocab_size:,} possible)")


# ---------------------------------------------------------------------------
# Exercise 2: Measure Standard Error Empirically
# ---------------------------------------------------------------------------

def exercise_2_standard_error():
    """
    Run 100 trials of HLL on N random items.
    Compute std(estimates) / N and compare to theoretical 1.04/sqrt(m).

    This validates the theoretical error bound experimentally.
    """
    print("\n" + "=" * 70)
    print("Exercise 2: Empirical Standard Error Measurement")
    print("=" * 70)

    num_trials = 100
    N = 50_000  # Items per trial

    for p in [6, 8, 10, 12, 14]:
        estimates = []
        for trial in range(num_trials):
            hll = HyperLogLog(p=p)
            # Use different random seeds per trial to get different hashes
            for i in range(N):
                hll.add(f"trial{trial}-item{i}")
            estimates.append(hll.count())

        # Compute empirical standard error
        mean_est = sum(estimates) / len(estimates)
        variance = sum((e - mean_est) ** 2 for e in estimates) / len(estimates)
        empirical_se = math.sqrt(variance) / N
        theoretical_se = 1.04 / math.sqrt(1 << p)

        print(f"\n  p={p:>2}, m={1 << p:>6,}:")
        print(f"    Mean estimate:     {mean_est:>10,.0f}  (actual: {N:,})")
        print(f"    Empirical SE:      {empirical_se:>10.4f}  ({empirical_se * 100:.2f}%)")
        print(f"    Theoretical SE:    {theoretical_se:>10.4f}  ({theoretical_se * 100:.2f}%)")
        print(f"    Ratio (emp/theo):  {empirical_se / theoretical_se:>10.3f}")


# ---------------------------------------------------------------------------
# Exercise 3: Merge and Verify
# ---------------------------------------------------------------------------

def exercise_3_merge():
    """
    Create two HLLs with overlapping sets, merge them, verify the result
    approximates |A union B|.

    This simulates distributed counting: different servers count their local
    users, then merge sketches to get global unique count.
    """
    print("\n" + "=" * 70)
    print("Exercise 3: Merge and Verify |A union B|")
    print("=" * 70)

    random.seed(123)
    p = 12

    # Test with varying overlap percentages
    test_cases = [
        ("No overlap",      range(0, 10000),     range(10000, 20000)),
        ("25% overlap",     range(0, 10000),     range(7500, 17500)),
        ("50% overlap",     range(0, 10000),     range(5000, 15000)),
        ("75% overlap",     range(0, 10000),     range(2500, 12500)),
        ("100% overlap",    range(0, 10000),     range(0, 10000)),
    ]

    print(f"\n  Using p={p} (m={1 << p:,} registers)")
    print(f"\n  {'Scenario':<18} {'|A|':>7} {'|B|':>7} {'|AuB| actual':>13} {'|AuB| est':>11} {'Error':>8}")
    print("  " + "-" * 66)

    for name, range_a, range_b in test_cases:
        hll_a = HyperLogLog(p=p)
        hll_b = HyperLogLog(p=p)

        set_a = set()
        set_b = set()
        for i in range_a:
            hll_a.add(f"item-{i}")
            set_a.add(i)
        for i in range_b:
            hll_b.add(f"item-{i}")
            set_b.add(i)

        merged = hll_a.merge(hll_b)
        actual_union = len(set_a | set_b)
        est_union = merged.count()
        err = abs(est_union - actual_union) / actual_union * 100

        print(f"  {name:<18} {len(set_a):>7,} {len(set_b):>7,} "
              f"{actual_union:>13,} {est_union:>11,} {err:>7.2f}%")

    # Verify merge is commutative and associative
    print("\n  Verifying merge properties:")
    hll_x = HyperLogLog(p=10)
    hll_y = HyperLogLog(p=10)
    hll_z = HyperLogLog(p=10)
    for i in range(5000):
        hll_x.add(f"x-{i}")
    for i in range(3000, 8000):
        hll_y.add(f"x-{i}")  # Overlaps with X
    for i in range(6000, 11000):
        hll_z.add(f"x-{i}")  # Overlaps with Y

    xy = hll_x.merge(hll_y)
    yx = hll_y.merge(hll_x)
    print(f"    Commutative: merge(X,Y)={xy.count():,} == merge(Y,X)={yx.count():,}? "
          f"{'YES' if xy.count() == yx.count() else 'NO'}")

    xy_z = xy.merge(hll_z)
    yz = hll_y.merge(hll_z)
    x_yz = hll_x.merge(yz)
    print(f"    Associative: merge(XY,Z)={xy_z.count():,} == merge(X,YZ)={x_yz.count():,}? "
          f"{'YES' if xy_z.count() == x_yz.count() else 'NO'}")


# ---------------------------------------------------------------------------
# Exercise 4: Cardinality of Intersection via Inclusion-Exclusion
# ---------------------------------------------------------------------------

def exercise_4_intersection():
    """
    Estimate |A intersect B| using inclusion-exclusion:
        |A intersect B| = |A| + |B| - |A union B|

    Important caveat: intersection estimates amplify error.
    If |A intersect B| is small relative to |A| and |B|, the relative
    error on the intersection can be very large.
    """
    print("\n" + "=" * 70)
    print("Exercise 4: Intersection via Inclusion-Exclusion")
    print("=" * 70)

    p = 14  # Use high precision since intersection amplifies errors

    print(f"\n  Using p={p} for best accuracy")
    print(f"\n  {'Overlap':>10} {'|A|':>7} {'|B|':>7} {'|AnB| actual':>13} "
          f"{'|AnB| est':>11} {'Abs Error':>10} {'Rel Error':>10}")
    print("  " + "-" * 72)

    for overlap_frac in [0.1, 0.25, 0.5, 0.75, 0.9]:
        size = 50_000
        overlap = int(size * overlap_frac)

        hll_a = HyperLogLog(p=p)
        hll_b = HyperLogLog(p=p)

        # A = [0, size), B = [size - overlap, 2*size - overlap)
        for i in range(size):
            hll_a.add(f"v-{i}")
        for i in range(size - overlap, 2 * size - overlap):
            hll_b.add(f"v-{i}")

        merged = hll_a.merge(hll_b)

        est_a = hll_a.count()
        est_b = hll_b.count()
        est_union = merged.count()

        # Inclusion-exclusion
        est_intersection = est_a + est_b - est_union
        actual_intersection = overlap
        abs_err = abs(est_intersection - actual_intersection)
        rel_err = abs_err / actual_intersection * 100 if actual_intersection > 0 else float('inf')

        print(f"  {overlap_frac * 100:>9.0f}% {size:>7,} {size:>7,} "
              f"{actual_intersection:>13,} {est_intersection:>11,} "
              f"{abs_err:>10,} {rel_err:>9.2f}%")

    print(f"\n  Key insight: small intersections have high relative error because")
    print(f"  we're subtracting two large similar numbers (catastrophic cancellation).")
    print(f"  For reliable intersection estimates, use MinHash (Jaccard) instead.")


# ---------------------------------------------------------------------------
# Exercise 5: Precision Trade-off — Memory vs Error Rate
# ---------------------------------------------------------------------------

def exercise_5_precision_tradeoff():
    """
    Measure actual error for p = 4, 6, 8, 10, 12, 14.
    Run multiple trials to get reliable error measurements.
    Show memory vs error trade-off as a text plot.
    """
    print("\n" + "=" * 70)
    print("Exercise 5: Precision Trade-off — Memory vs Error Rate")
    print("=" * 70)

    N = 100_000
    num_trials = 20
    precisions = [4, 6, 8, 10, 12, 14]

    print(f"\n  {num_trials} trials, {N:,} unique items each\n")
    print(f"  {'p':>4} {'m':>7} {'Memory':>10} {'Theo SE':>10} {'Emp SE':>10} "
          f"{'Mean Est':>12} {'Mean Err%':>10}")
    print("  " + "-" * 65)

    results = []
    for p in precisions:
        estimates = []
        for trial in range(num_trials):
            hll = HyperLogLog(p=p)
            for i in range(N):
                hll.add(f"t{trial}-i{i}")
            estimates.append(hll.count())

        mean_est = sum(estimates) / len(estimates)
        errors = [abs(e - N) / N for e in estimates]
        mean_err = sum(errors) / len(errors) * 100
        variance = sum((e - mean_est) ** 2 for e in estimates) / len(estimates)
        emp_se = math.sqrt(variance) / N * 100
        theo_se = 1.04 / math.sqrt(1 << p) * 100
        mem = 1 << p
        mem_str = f"{mem} B" if mem < 1024 else f"{mem // 1024} KB"

        results.append((p, mem, theo_se, emp_se, mean_err))

        print(f"  {p:>4} {1 << p:>7,} {mem_str:>10} {theo_se:>9.2f}% "
              f"{emp_se:>9.2f}% {mean_est:>12,.0f} {mean_err:>9.2f}%")

    # Text-based visualization
    print(f"\n  Memory vs Error Rate (text plot):")
    print(f"  {'':>10} 0%      5%      10%     15%     20%     25%")
    print(f"  {'':>10} |-------|-------|-------|-------|-------|")

    for p, mem, theo_se, emp_se, mean_err in results:
        mem_str = f"{mem} B" if mem < 1024 else f"{mem // 1024} KB"
        bar_len = min(int(mean_err * 2), 50)  # Scale: 1 char = 0.5%
        bar = "#" * bar_len
        print(f"  p={p:>2} {mem_str:>5} |{bar} {mean_err:.1f}%")

    print(f"\n  Doubling registers (p+1) reduces error by factor of ~sqrt(2) = ~1.41")
    print(f"  This is the fundamental memory-accuracy trade-off of HyperLogLog.")

    # Show the sqrt(2) relationship
    print(f"\n  Error reduction when doubling m:")
    for i in range(len(results) - 1):
        p1, _, _, _, err1 = results[i]
        p2, _, _, _, err2 = results[i + 1]
        if err2 > 0:
            ratio = err1 / err2
            print(f"    p={p1} -> p={p2}: error ratio = {ratio:.2f} (ideal: {math.sqrt(4):.2f})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    exercise_1_unique_word_counter()
    exercise_2_standard_error()
    exercise_3_merge()
    exercise_4_intersection()
    exercise_5_precision_tradeoff()
