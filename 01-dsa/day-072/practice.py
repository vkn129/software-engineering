"""
Day 72 Practice: Count-Min Sketch Exercises

5 exercises building on the CMS implementation.
All exercises are self-contained — run this file to execute all of them.
"""

import math
import hashlib
import struct
import heapq
import random
from collections import Counter


# ---------------------------------------------------------------------------
# Shared CMS implementation (duplicated here so practice.py is standalone)
# ---------------------------------------------------------------------------

class CountMinSketch:
    """Count-Min Sketch for frequency estimation."""

    def __init__(self, epsilon=0.01, delta=0.01):
        self.epsilon = epsilon
        self.delta = delta
        self.w = math.ceil(math.e / epsilon)
        self.d = math.ceil(math.log(1.0 / delta))
        self.table = [[0] * self.w for _ in range(self.d)]
        self.total_count = 0
        self._seeds = [i * 0xDEADBEEF + 0xCAFEBABE for i in range(self.d)]

    def _hash(self, item, row):
        key = struct.pack(">Q", self._seeds[row]) + str(item).encode("utf-8")
        digest = hashlib.md5(key).digest()
        value = struct.unpack(">Q", digest[:8])[0]
        return value % self.w

    def add(self, item, count=1):
        self.total_count += count
        for row in range(self.d):
            col = self._hash(item, row)
            self.table[row][col] += count

    def estimate(self, item):
        return min(self.table[row][self._hash(item, row)] for row in range(self.d))

    def merge(self, other):
        if self.w != other.w or self.d != other.d:
            raise ValueError("Cannot merge: dimensions differ")
        if self._seeds != other._seeds:
            raise ValueError("Cannot merge: hash seeds differ")
        for row in range(self.d):
            for col in range(self.w):
                self.table[row][col] += other.table[row][col]
        self.total_count += other.total_count


# ===========================================================================
# Exercise 1: Top-K Frequent Words Using CMS + Min-Heap
# ===========================================================================

def exercise_1_top_k_streaming():
    """
    Find top-k frequent words in streaming text using CMS + min-heap.

    The challenge: in a true stream, you can't store all distinct items.
    CMS estimates frequencies, but it can't enumerate items.
    We maintain a min-heap of size k to track the top candidates.

    Approach:
    - For each word in the stream, update CMS
    - Maintain a min-heap of (estimated_count, word) with at most k entries
    - When a word's estimate exceeds the heap minimum, swap it in
    """
    print("=" * 70)
    print("Exercise 1: Top-K Frequent Words (CMS + Min-Heap)")
    print("=" * 70)

    # Generate a stream with known frequency distribution (Zipf-like)
    rng = random.Random(42)
    vocabulary = [f"word_{i}" for i in range(500)]
    # Zipf: word_i appears proportional to 1/(i+1)
    weights = [1.0 / (i + 1) for i in range(500)]
    total_weight = sum(weights)
    probs = [w / total_weight for w in weights]

    # Generate 50K words from this distribution
    stream = rng.choices(vocabulary, weights=probs, k=50000)
    exact = Counter(stream)

    k = 10
    cms = CountMinSketch(epsilon=0.001, delta=0.01)

    # Min-heap: (estimated_count, word)
    # We keep the k largest. A min-heap lets us efficiently evict the smallest.
    top_k_heap = []
    # Set for O(1) membership check
    in_heap = set()

    for word in stream:
        cms.add(word)
        est = cms.estimate(word)

        if word in in_heap:
            # Word is already tracked — rebuild heap periodically would be ideal,
            # but for simplicity we just let duplicates accumulate and deduplicate at the end.
            # A production system would use an indexed priority queue.
            continue

        if len(top_k_heap) < k:
            heapq.heappush(top_k_heap, (est, word))
            in_heap.add(word)
        elif est > top_k_heap[0][0]:
            # New word has higher estimate than the current k-th largest
            _, evicted = heapq.heapreplace(top_k_heap, (est, word))
            in_heap.discard(evicted)
            in_heap.add(word)

    # Re-estimate all candidates (estimates improve as more data is added)
    final_top_k = [(cms.estimate(word), word) for _, word in top_k_heap]
    final_top_k.sort(reverse=True)

    # Compare with exact top-k
    exact_top_k = exact.most_common(k)

    print(f"\nStream size: {len(stream)}, Vocabulary: {len(vocabulary)}")
    print(f"\n{'Rank':<6}{'CMS Top-K':<20}{'Est Count':<12}{'Exact Top-K':<20}{'True Count':<12}")
    print("-" * 70)
    for i in range(k):
        cms_word = final_top_k[i][1] if i < len(final_top_k) else "?"
        cms_est = final_top_k[i][0] if i < len(final_top_k) else 0
        exact_word = exact_top_k[i][0]
        exact_count = exact_top_k[i][1]
        match = "*" if cms_word == exact_word else " "
        print(f"{i+1:<6}{cms_word:<20}{cms_est:<12}{exact_word:<20}{exact_count:<12}{match}")

    # Count how many of the true top-k were found
    cms_top_set = {word for _, word in final_top_k}
    exact_top_set = {word for word, _ in exact_top_k}
    overlap = cms_top_set & exact_top_set
    print(f"\nPrecision: {len(overlap)}/{k} of true top-{k} found")


# ===========================================================================
# Exercise 2: Error Distribution Analysis
# ===========================================================================

def exercise_2_error_distribution():
    """
    Measure error distribution: CMS estimate vs exact count for 10K items.

    Key insight: most items have zero or tiny error. The error bound
    epsilon * N is a worst case — the typical case is much better because
    most items don't collide with heavy hitters.
    """
    print("\n" + "=" * 70)
    print("Exercise 2: Error Distribution (CMS vs Exact for 10K Items)")
    print("=" * 70)

    rng = random.Random(123)
    n_items = 10000
    n_total = 100000

    # Generate items with varying frequencies
    # Some items are very frequent, most are rare
    items = []
    exact = Counter()
    for _ in range(n_total):
        # Power-law: most items are rare, few are very common
        item_id = int(rng.paretovariate(1.5)) % n_items
        items.append(item_id)
        exact[item_id] += 1

    # Test different epsilon values
    for epsilon in [0.1, 0.01, 0.001]:
        cms = CountMinSketch(epsilon=epsilon, delta=0.01)
        for item in items:
            cms.add(item)

        errors = []
        for item_id in range(n_items):
            if exact[item_id] > 0:
                est = cms.estimate(item_id)
                true_count = exact[item_id]
                error = est - true_count  # Always >= 0
                errors.append(error)

        errors.sort()
        n = len(errors)

        print(f"\nepsilon={epsilon}, sketch size={cms.d}x{cms.w} = {cms.d * cms.w} counters")
        print(f"  Error bound (eps * N): {epsilon * n_total:.0f}")
        print(f"  Items measured: {n}")
        print(f"  Zero-error items: {sum(1 for e in errors if e == 0)} ({100*sum(1 for e in errors if e == 0)/n:.1f}%)")
        print(f"  Mean error: {sum(errors)/n:.2f}")
        print(f"  Median error: {errors[n//2]}")
        print(f"  95th percentile: {errors[int(n*0.95)]}")
        print(f"  99th percentile: {errors[int(n*0.99)]}")
        print(f"  Max error: {errors[-1]}")
        violations = sum(1 for e in errors if e > epsilon * n_total)
        print(f"  Bound violations: {violations}/{n} ({100*violations/n:.2f}%)")


# ===========================================================================
# Exercise 3: Conservative Update CMS
# ===========================================================================

class ConservativeUpdateCMS:
    """
    Count-Min Sketch with Conservative Update optimization.

    Standard CMS increments ALL d counters blindly. Conservative Update
    only increments counters up to (current_min + count), avoiding
    unnecessary inflation of counters that are already above the true count.

    This reduces overcounting without changing space or time complexity.
    The key insight: if a counter already reads higher than necessary,
    inflating it further only hurts accuracy.
    """

    def __init__(self, epsilon=0.01, delta=0.01):
        self.epsilon = epsilon
        self.delta = delta
        self.w = math.ceil(math.e / epsilon)
        self.d = math.ceil(math.log(1.0 / delta))
        self.table = [[0] * self.w for _ in range(self.d)]
        self.total_count = 0
        self._seeds = [i * 0xDEADBEEF + 0xCAFEBABE for i in range(self.d)]

    def _hash(self, item, row):
        key = struct.pack(">Q", self._seeds[row]) + str(item).encode("utf-8")
        digest = hashlib.md5(key).digest()
        value = struct.unpack(">Q", digest[:8])[0]
        return value % self.w

    def add(self, item, count=1):
        """
        Conservative Update: compute current minimum estimate, then
        set each counter to max(current_value, min_estimate + count).

        This means counters that are already above the new target
        are left unchanged — they don't get inflated further.
        """
        self.total_count += count

        # First, compute current minimum (the best estimate before this update)
        cols = [self._hash(item, row) for row in range(self.d)]
        current_min = min(self.table[row][cols[row]] for row in range(self.d))

        # New target: the minimum + the count we're adding
        new_value = current_min + count

        # Only raise counters that are below the new target
        for row in range(self.d):
            col = cols[row]
            self.table[row][col] = max(self.table[row][col], new_value)

    def estimate(self, item):
        return min(self.table[row][self._hash(item, row)] for row in range(self.d))


def exercise_3_conservative_update():
    """
    Compare standard CMS vs Conservative Update CMS.
    Conservative Update should have lower average error.
    """
    print("\n" + "=" * 70)
    print("Exercise 3: Conservative Update vs Standard CMS")
    print("=" * 70)

    rng = random.Random(456)

    # Generate Zipf-distributed data
    n_total = 50000
    n_distinct = 5000
    items = []
    for _ in range(n_total):
        item_id = int(rng.paretovariate(1.2)) % n_distinct
        items.append(item_id)

    exact = Counter(items)

    # Standard CMS
    std_cms = CountMinSketch(epsilon=0.01, delta=0.01)
    for item in items:
        std_cms.add(item)

    # Conservative Update CMS
    cu_cms = ConservativeUpdateCMS(epsilon=0.01, delta=0.01)
    for item in items:
        cu_cms.add(item)

    # Compare errors
    std_errors = []
    cu_errors = []
    for item_id in exact:
        true_count = exact[item_id]
        std_est = std_cms.estimate(item_id)
        cu_est = cu_cms.estimate(item_id)
        std_errors.append(std_est - true_count)
        cu_errors.append(cu_est - true_count)

    n = len(std_errors)
    std_errors.sort()
    cu_errors.sort()

    print(f"\nItems: {n_total}, Distinct: {len(exact)}")
    print(f"Sketch: {std_cms.d} rows x {std_cms.w} cols")

    print(f"\n{'Metric':<25}{'Standard':<15}{'Conservative':<15}{'Improvement':<15}")
    print("-" * 70)

    std_mean = sum(std_errors) / n
    cu_mean = sum(cu_errors) / n
    improvement = ((std_mean - cu_mean) / std_mean * 100) if std_mean > 0 else 0
    print(f"{'Mean error':<25}{std_mean:<15.2f}{cu_mean:<15.2f}{improvement:<15.1f}%")

    print(f"{'Median error':<25}{std_errors[n//2]:<15}{cu_errors[n//2]:<15}")

    std_p95 = std_errors[int(n * 0.95)]
    cu_p95 = cu_errors[int(n * 0.95)]
    print(f"{'95th pct error':<25}{std_p95:<15}{cu_p95:<15}")

    print(f"{'Max error':<25}{std_errors[-1]:<15}{cu_errors[-1]:<15}")

    std_zero = sum(1 for e in std_errors if e == 0)
    cu_zero = sum(1 for e in cu_errors if e == 0)
    print(f"{'Zero-error items':<25}{std_zero:<15}{cu_zero:<15}")


# ===========================================================================
# Exercise 4: Network Anomaly Detection
# ===========================================================================

def exercise_4_network_anomaly_detection():
    """
    Track IP address frequencies and flag IPs exceeding a threshold.

    Simulates a network packet stream where most IPs are normal but
    a few are anomalous (DDoS, port scan, etc.) with unusually high frequency.

    CMS lets us monitor this in O(1) space per IP, which is critical when
    the IP space is effectively unbounded (2^32 for IPv4, 2^128 for IPv6).
    """
    print("\n" + "=" * 70)
    print("Exercise 4: Network Anomaly Detection")
    print("=" * 70)

    rng = random.Random(789)

    # Simulate network traffic
    # Normal IPs: ~1-5 packets each
    # Anomalous IPs: 500+ packets (DDoS sources)
    normal_ips = [f"192.168.{rng.randint(0,255)}.{rng.randint(1,254)}" for _ in range(2000)]
    attacker_ips = [f"10.0.{rng.randint(0,5)}.{rng.randint(1,254)}" for _ in range(5)]

    # Build packet stream
    packets = []
    # Normal traffic: each IP sends 1-5 packets
    for ip in normal_ips:
        count = rng.randint(1, 5)
        packets.extend([ip] * count)
    # Attack traffic: each attacker sends many packets
    for ip in attacker_ips:
        count = rng.randint(500, 1000)
        packets.extend([ip] * count)

    rng.shuffle(packets)

    exact = Counter(packets)
    total_packets = len(packets)
    print(f"\nTotal packets: {total_packets}")
    print(f"Distinct IPs: {len(exact)}")
    print(f"Attacker IPs: {attacker_ips}")

    # Threshold: flag IPs with more than 0.5% of total traffic
    threshold_fraction = 0.005
    threshold_count = threshold_fraction * total_packets

    cms = CountMinSketch(epsilon=0.001, delta=0.01)
    flagged = {}  # ip -> estimated count

    # Process packet stream
    # In a real system, we'd only see each packet once (no going back)
    seen_ips = set()
    for ip in packets:
        cms.add(ip)
        seen_ips.add(ip)

        # Periodically check this IP (every time we see it)
        est = cms.estimate(ip)
        if est >= threshold_count:
            flagged[ip] = est

    print(f"\nThreshold: {threshold_fraction*100:.1f}% of traffic = {threshold_count:.0f} packets")
    print(f"\nFlagged IPs ({len(flagged)}):")
    print(f"{'IP Address':<25}{'Estimated':<15}{'Exact':<15}{'Status':<15}")
    print("-" * 70)

    for ip, est in sorted(flagged.items(), key=lambda x: -x[1]):
        true_count = exact[ip]
        is_attacker = ip in attacker_ips
        status = "ATTACKER" if is_attacker else "false positive"
        print(f"{ip:<25}{est:<15}{true_count:<15}{status:<15}")

    # Check for missed attackers (false negatives)
    missed = []
    for ip in attacker_ips:
        if ip not in flagged:
            missed.append(ip)

    if missed:
        print(f"\nMissed attackers: {missed}")
    else:
        print(f"\nAll {len(attacker_ips)} attacker IPs detected!")

    # Count false positives
    fp = sum(1 for ip in flagged if ip not in attacker_ips)
    print(f"False positives: {fp}")


# ===========================================================================
# Exercise 5: Mergeable Sketches
# ===========================================================================

def exercise_5_mergeable_sketches():
    """
    Create CMS on two data partitions, merge, and verify that estimates
    match a single-pass CMS over the full data.

    This demonstrates the key distributed computing property of CMS:
    each node can independently build a sketch, then merge for a global view.
    No coordination needed during counting — only a single merge at the end.

    Merge is exact: merged_sketch[i][j] = sketch_a[i][j] + sketch_b[i][j]
    This works because each cell is a sum of counts of items that hash there.
    """
    print("\n" + "=" * 70)
    print("Exercise 5: Mergeable Sketches (Distributed Counting)")
    print("=" * 70)

    rng = random.Random(101)

    # Generate a dataset and split into two partitions
    # Simulates data distributed across two nodes
    items = []
    for _ in range(100000):
        item_id = rng.choice(["apple", "banana", "cherry", "date", "elderberry",
                               "fig", "grape", "honeydew", "kiwi", "lemon"])
        # Non-uniform frequencies
        if item_id == "apple":
            items.extend([item_id] * 3)  # apple is 3x more likely
        else:
            items.append(item_id)

    rng.shuffle(items)
    exact = Counter(items)

    # Split into two partitions (simulating two nodes)
    mid = len(items) // 2
    partition_1 = items[:mid]
    partition_2 = items[mid:]

    epsilon = 0.01
    delta = 0.01

    # Approach 1: Single-pass CMS over all data
    cms_full = CountMinSketch(epsilon=epsilon, delta=delta)
    for item in items:
        cms_full.add(item)

    # Approach 2: Two separate CMS, then merge
    cms_node1 = CountMinSketch(epsilon=epsilon, delta=delta)
    cms_node2 = CountMinSketch(epsilon=epsilon, delta=delta)

    for item in partition_1:
        cms_node1.add(item)
    for item in partition_2:
        cms_node2.add(item)

    # Merge node2 into node1
    cms_node1.merge(cms_node2)
    cms_merged = cms_node1

    print(f"\nTotal items: {len(items)}")
    print(f"Partition 1: {len(partition_1)} items")
    print(f"Partition 2: {len(partition_2)} items")
    print(f"Sketch: {cms_full.d} rows x {cms_full.w} cols")

    print(f"\n{'Item':<15}{'Exact':<10}{'Single-Pass':<15}{'Merged':<15}{'Match?':<10}")
    print("-" * 65)

    all_match = True
    for item in sorted(exact.keys()):
        true_count = exact[item]
        est_full = cms_full.estimate(item)
        est_merged = cms_merged.estimate(item)
        match = est_full == est_merged
        if not match:
            all_match = False
        print(f"{item:<15}{true_count:<10}{est_full:<15}{est_merged:<15}{'yes' if match else 'NO':<10}")

    print(f"\nTotal count match: {cms_full.total_count} vs {cms_merged.total_count} -> "
          f"{'yes' if cms_full.total_count == cms_merged.total_count else 'NO'}")

    if all_match:
        print("\nAll estimates match! Merge is exact for CMS.")
    else:
        print("\nSome estimates differ — this should NOT happen. Check implementation.")

    # Verify the mathematical property: cell-by-cell equality
    cells_match = all(
        cms_full.table[r][c] == cms_merged.table[r][c]
        for r in range(cms_full.d)
        for c in range(cms_full.w)
    )
    print(f"Cell-by-cell equality: {'VERIFIED' if cells_match else 'FAILED'}")


# ===========================================================================
# Main
# ===========================================================================

if __name__ == "__main__":
    exercise_1_top_k_streaming()
    exercise_2_error_distribution()
    exercise_3_conservative_update()
    exercise_4_network_anomaly_detection()
    exercise_5_mergeable_sketches()
