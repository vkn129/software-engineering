"""
Day 72: Count-Min Sketch — Frequency Estimation in Streaming Data

A Count-Min Sketch uses d rows x w columns of counters with d hash functions
to estimate item frequencies in O(1) time and fixed space.

Guarantee: estimate(x) <= true_count(x) + epsilon * N
           with probability >= 1 - delta

where w = ceil(e/epsilon), d = ceil(ln(1/delta)), N = total items added.
"""

import math
import hashlib
import struct
from collections import Counter


class CountMinSketch:
    """
    Probabilistic frequency estimator.

    Parameters:
        epsilon: error factor — estimate can overcount by at most epsilon * N
        delta: failure probability — the bound holds with probability >= 1 - delta

    The sketch never undercounts. It can only overcount due to hash collisions.
    """

    def __init__(self, epsilon=0.01, delta=0.01):
        if epsilon <= 0 or epsilon >= 1:
            raise ValueError("epsilon must be in (0, 1)")
        if delta <= 0 or delta >= 1:
            raise ValueError("delta must be in (0, 1)")

        self.epsilon = epsilon
        self.delta = delta

        # w = ceil(e / epsilon) controls accuracy
        # d = ceil(ln(1 / delta)) controls confidence
        self.w = math.ceil(math.e / epsilon)
        self.d = math.ceil(math.log(1.0 / delta))

        # d rows, each with w counters initialized to 0
        self.table = [[0] * self.w for _ in range(self.d)]

        # Total count of all items added (used for error bound calculations)
        self.total_count = 0

        # Generate d independent hash seeds
        # Each row uses a different seed so hash functions are independent
        self._seeds = [i * 0xDEADBEEF + 0xCAFEBABE for i in range(self.d)]

    def _hash(self, item, row):
        """
        Hash item to a column index for the given row.

        Uses MD5 with a row-specific seed for independence between rows.
        MD5 is not cryptographically needed here — we just need good distribution.
        """
        # Combine seed with item to get a row-specific hash
        key = struct.pack(">Q", self._seeds[row]) + str(item).encode("utf-8")
        digest = hashlib.md5(key).digest()
        # Interpret first 8 bytes as unsigned 64-bit integer
        value = struct.unpack(">Q", digest[:8])[0]
        return value % self.w

    def add(self, item, count=1):
        """
        Record 'count' occurrences of item.

        Increments the counter at table[row][hash_row(item)] for each row.
        Time: O(d) where d = ceil(ln(1/delta))
        """
        if count < 0:
            raise ValueError("Count must be non-negative (CMS doesn't support deletion)")

        self.total_count += count
        for row in range(self.d):
            col = self._hash(item, row)
            self.table[row][col] += count

    def estimate(self, item):
        """
        Estimate the frequency of item.

        Returns the minimum counter across all d rows.
        This is always >= true count (never undercounts)
        and <= true_count + epsilon * N with probability >= 1 - delta.

        Time: O(d)
        """
        return min(self.table[row][self._hash(item, row)] for row in range(self.d))

    def merge(self, other):
        """
        Merge another CMS into this one (in-place).

        Both sketches must have the same dimensions and hash seeds.
        After merging, this sketch estimates frequencies over the union of both streams.

        Why this works: addition is commutative over the counters.
        If sketch A tracked stream S1 and sketch B tracked stream S2,
        then A + B tracks S1 + S2.
        """
        if self.w != other.w or self.d != other.d:
            raise ValueError(
                f"Cannot merge: dimensions differ. "
                f"Self: {self.d}x{self.w}, Other: {other.d}x{other.w}"
            )
        if self._seeds != other._seeds:
            raise ValueError("Cannot merge: hash seeds differ (different epsilon/delta)")

        for row in range(self.d):
            for col in range(self.w):
                self.table[row][col] += other.table[row][col]

        self.total_count += other.total_count

    def __repr__(self):
        return (
            f"CountMinSketch(epsilon={self.epsilon}, delta={self.delta}, "
            f"width={self.w}, depth={self.d}, total_count={self.total_count})"
        )


class HeavyHitters:
    """
    Find items whose frequency exceeds a threshold fraction of total items.

    Uses a Count-Min Sketch for frequency estimation and maintains a candidate
    set of potential heavy hitters.

    An item is a heavy hitter if its true frequency > threshold * N.

    Why CMS works well here: CMS overcounts, so if estimate(x) <= threshold * N,
    we know the true count is also <= threshold * N. We might have false positives
    (items that appear heavy but aren't) but no false negatives.
    """

    def __init__(self, threshold=0.01, epsilon=0.001, delta=0.01):
        """
        threshold: fraction of total — items with freq > threshold * N are heavy hitters
        epsilon: CMS error factor (should be < threshold for meaningful results)
        delta: CMS failure probability
        """
        if epsilon >= threshold:
            # If error is larger than threshold, we can't distinguish heavy hitters
            # from noise. Warn but allow it for experimentation.
            print(
                f"Warning: epsilon ({epsilon}) >= threshold ({threshold}). "
                f"Results may have many false positives."
            )

        self.threshold = threshold
        self.cms = CountMinSketch(epsilon=epsilon, delta=delta)
        # Candidate set: items that might be heavy hitters
        # We track these because CMS can't enumerate items — it only answers
        # point queries. We need to remember which items to check.
        self.candidates = set()

    def add(self, item, count=1):
        """Add item and check if it becomes a heavy hitter candidate."""
        self.cms.add(item, count)

        # Check if estimated frequency exceeds threshold
        # We check on every add because an item might cross the threshold at any time
        estimated = self.cms.estimate(item)
        if estimated >= self.threshold * self.cms.total_count:
            self.candidates.add(item)

    def get_heavy_hitters(self):
        """
        Return items whose estimated frequency exceeds the threshold.

        Re-checks all candidates because the threshold is relative to total_count,
        which changes as items are added. An item that was a candidate earlier
        might no longer qualify.
        """
        if self.cms.total_count == 0:
            return []

        cutoff = self.threshold * self.cms.total_count
        results = []
        for item in self.candidates:
            est = self.cms.estimate(item)
            if est >= cutoff:
                results.append((item, est))

        # Sort by estimated frequency, descending
        results.sort(key=lambda x: -x[1])
        return results

    @property
    def total_count(self):
        return self.cms.total_count


# ---------------------------------------------------------------------------
# Demo: Word frequency estimation — CMS vs exact counts
# ---------------------------------------------------------------------------

def demo_word_frequency():
    """
    Count word frequencies in a text using both CMS and exact counting.
    Compare estimates to show CMS accuracy.
    """
    text = """
    the quick brown fox jumps over the lazy dog the fox the fox jumped
    over the fence and the dog chased the fox through the park the dog
    barked at the fox and the fox ran away the cat watched from the tree
    the bird flew over the park and the dog barked again the fox returned
    to the park and the dog chased the fox once more the cat yawned the
    sun set over the park and all the animals went home the end the fox
    the dog the cat the bird the park the tree the sun the moon the stars
    """

    words = text.lower().split()

    # Exact counts for comparison
    exact = Counter(words)

    # CMS with different accuracy levels
    print("=" * 70)
    print("COUNT-MIN SKETCH: Word Frequency Estimation")
    print("=" * 70)
    print(f"\nTotal words: {len(words)}")
    print(f"Distinct words: {len(exact)}")
    print(f"\nTop 10 words (exact counts):")
    for word, count in exact.most_common(10):
        print(f"  {word:12s} -> {count}")

    # CMS estimates
    for eps_label, epsilon in [("high accuracy (eps=0.01)", 0.01),
                                ("low accuracy (eps=0.1)", 0.1)]:
        cms = CountMinSketch(epsilon=epsilon, delta=0.01)
        for word in words:
            cms.add(word)

        print(f"\n--- CMS {eps_label} ---")
        print(f"Sketch size: {cms.d} rows x {cms.w} cols = {cms.d * cms.w} counters")

        total_error = 0
        max_error = 0
        for word in exact:
            est = cms.estimate(word)
            true_count = exact[word]
            error = est - true_count  # Always >= 0 (CMS never undercounts)
            total_error += error
            max_error = max(max_error, error)

        print(f"Average overcount: {total_error / len(exact):.2f}")
        print(f"Max overcount: {max_error}")
        print(f"Error bound (eps * N): {epsilon * len(words):.1f}")

        print(f"\nTop 10 estimates vs exact:")
        for word, true_count in exact.most_common(10):
            est = cms.estimate(word)
            marker = " *" if est > true_count else ""
            print(f"  {word:12s} -> est={est:3d}  exact={true_count:3d}{marker}")


def demo_heavy_hitters():
    """
    Find heavy hitters in a word stream.
    """
    print("\n" + "=" * 70)
    print("HEAVY HITTERS: Find Frequent Words")
    print("=" * 70)

    words = (
        ["the"] * 100 +
        ["and"] * 50 +
        ["of"] * 40 +
        ["to"] * 30 +
        ["in"] * 20 +
        # Long tail of infrequent words
        [f"word_{i}" for i in range(200)]
    )

    # Shuffle to simulate a stream (deterministic for reproducibility)
    import random
    rng = random.Random(42)
    rng.shuffle(words)

    hh = HeavyHitters(threshold=0.05, epsilon=0.005, delta=0.01)
    for word in words:
        hh.add(word)

    print(f"\nTotal items: {hh.total_count}")
    print(f"Threshold: {hh.threshold} ({hh.threshold * hh.total_count:.0f} occurrences)")
    print(f"\nHeavy hitters found:")
    for item, est_count in hh.get_heavy_hitters():
        print(f"  {item:12s} -> estimated count: {est_count}")


def demo_merge():
    """
    Demonstrate merging two CMS sketches.
    """
    print("\n" + "=" * 70)
    print("MERGE: Combining Two Sketches")
    print("=" * 70)

    # Partition data into two halves
    data = ["apple"] * 50 + ["banana"] * 30 + ["cherry"] * 20 + ["date"] * 10

    mid = len(data) // 2
    part1 = data[:mid]
    part2 = data[mid:]

    # Single-pass CMS over all data
    cms_full = CountMinSketch(epsilon=0.01, delta=0.01)
    for item in data:
        cms_full.add(item)

    # Two separate CMS, then merge
    cms_a = CountMinSketch(epsilon=0.01, delta=0.01)
    cms_b = CountMinSketch(epsilon=0.01, delta=0.01)
    for item in part1:
        cms_a.add(item)
    for item in part2:
        cms_b.add(item)

    cms_a.merge(cms_b)

    print(f"\nSingle-pass vs Merged estimates:")
    for item in ["apple", "banana", "cherry", "date"]:
        est_full = cms_full.estimate(item)
        est_merged = cms_a.estimate(item)
        print(f"  {item:10s} -> single={est_full:3d}  merged={est_merged:3d}  match={'yes' if est_full == est_merged else 'NO'}")


if __name__ == "__main__":
    demo_word_frequency()
    demo_heavy_hitters()
    demo_merge()
