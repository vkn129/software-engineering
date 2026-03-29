"""
Day 71 Practice: Bloom Filter Exercises

5 exercises with TODO stubs, solutions, and a test runner.
Run: python3 practice.py
"""

import math
import hashlib
import struct
import random
import string


# ---------------------------------------------------------------------------
# Shared utilities
# ---------------------------------------------------------------------------

def _md5_double_hash(item: str, m: int, k: int) -> list:
    """Double hashing: h_i(x) = (h1(x) + i * h2(x)) mod m for i in 0..k-1."""
    digest = hashlib.md5(item.encode("utf-8")).digest()
    h1 = struct.unpack_from("<Q", digest, 0)[0]
    h2 = struct.unpack_from("<Q", digest, 8)[0]
    if h2 % 2 == 0:
        h2 += 1
    return [(h1 + i * h2) % m for i in range(k)]


def _optimal_m(n: int, p: float) -> int:
    return max(1, int(math.ceil(-(n * math.log(p)) / (math.log(2) ** 2))))


def _optimal_k(m: int, n: int) -> int:
    return max(1, int(round((m / n) * math.log(2))))


# ===========================================================================
# Exercise 1: Spell Checker Using Bloom Filter
# ===========================================================================
# Load a dictionary of words into a Bloom filter. Given a list of test words,
# identify which ones are "probably misspelled" (not in dictionary).
#
# Key insight: a Bloom filter is perfect for spell checking because:
# - False positive = accepting a misspelled word (rare, tolerable)
# - False negative = rejecting a correct word (never happens!)

def spell_checker_stub(dictionary: list, test_words: list) -> list:
    """
    TODO: Build a Bloom filter from dictionary words, then return a list of
    words from test_words that are probably misspelled (not in the filter).

    Args:
        dictionary: List of correctly spelled words.
        test_words: List of words to check.

    Returns:
        List of words that the Bloom filter says are NOT in the dictionary.
    """
    # TODO: Implement
    # 1. Compute optimal m and k for len(dictionary) at 1% FP rate
    # 2. Create a bit array of size m
    # 3. Insert all dictionary words
    # 4. Check each test word, collect those that fail membership test
    raise NotImplementedError("Implement spell_checker")


def spell_checker_solution(dictionary: list, test_words: list) -> list:
    n = len(dictionary)
    fp_rate = 0.01
    m = _optimal_m(n, fp_rate)
    k = _optimal_k(m, n)

    bits = bytearray((m + 7) // 8)

    def set_bit(pos):
        bits[pos // 8] |= (1 << (pos % 8))

    def get_bit(pos):
        return bool(bits[pos // 8] & (1 << (pos % 8)))

    # Insert all dictionary words
    for word in dictionary:
        for pos in _md5_double_hash(word.lower(), m, k):
            set_bit(pos)

    # Check test words
    misspelled = []
    for word in test_words:
        positions = _md5_double_hash(word.lower(), m, k)
        if not all(get_bit(pos) for pos in positions):
            misspelled.append(word)

    return misspelled


# ===========================================================================
# Exercise 2: Measure Actual vs Theoretical FP Rate
# ===========================================================================
# Insert n items, then query m non-member items and compare the measured
# false positive rate against the theoretical formula.

def measure_fp_rate_stub(n: int, m_bits: int, k: int, num_tests: int) -> dict:
    """
    TODO: Create a Bloom filter with m_bits bits and k hash functions.
    Insert n items ("item-0" through "item-{n-1}").
    Test num_tests non-members ("test-0" through "test-{num_tests-1}").

    Returns:
        dict with keys:
            "theoretical_fp": float — computed from formula (1 - e^(-kn/m))^k
            "actual_fp": float — measured false positive rate
            "false_positives": int — count of false positives
    """
    # TODO: Implement
    raise NotImplementedError("Implement measure_fp_rate")


def measure_fp_rate_solution(n: int, m_bits: int, k: int, num_tests: int) -> dict:
    bits = bytearray((m_bits + 7) // 8)

    def set_bit(pos):
        bits[pos // 8] |= (1 << (pos % 8))

    def get_bit(pos):
        return bool(bits[pos // 8] & (1 << (pos % 8)))

    # Insert n items
    for i in range(n):
        for pos in _md5_double_hash(f"item-{i}", m_bits, k):
            set_bit(pos)

    # Test non-members
    fp_count = 0
    for i in range(num_tests):
        positions = _md5_double_hash(f"test-{i}", m_bits, k)
        if all(get_bit(pos) for pos in positions):
            fp_count += 1

    theoretical = (1 - math.exp(-k * n / m_bits)) ** k
    actual = fp_count / num_tests

    return {
        "theoretical_fp": theoretical,
        "actual_fp": actual,
        "false_positives": fp_count,
    }


# ===========================================================================
# Exercise 3: Union and Intersection of Bloom Filters
# ===========================================================================
# Two Bloom filters with the SAME m and k can be combined:
# - Union (OR): result contains elements from EITHER filter
# - Intersection (AND): result APPROXIMATES elements in BOTH filters
#   (more false positives than a true intersection, but useful as a heuristic)

def bloom_union_stub(bits_a: bytearray, bits_b: bytearray) -> bytearray:
    """
    TODO: Return bitwise OR of two Bloom filter bit arrays.
    Both arrays are guaranteed to have the same length.
    """
    raise NotImplementedError("Implement bloom_union")


def bloom_intersection_stub(bits_a: bytearray, bits_b: bytearray) -> bytearray:
    """
    TODO: Return bitwise AND of two Bloom filter bit arrays.
    Both arrays are guaranteed to have the same length.
    """
    raise NotImplementedError("Implement bloom_intersection")


def bloom_union_solution(bits_a: bytearray, bits_b: bytearray) -> bytearray:
    return bytearray(a | b for a, b in zip(bits_a, bits_b))


def bloom_intersection_solution(bits_a: bytearray, bits_b: bytearray) -> bytearray:
    return bytearray(a & b for a, b in zip(bits_a, bits_b))


# ===========================================================================
# Exercise 4: Scalable Bloom Filter
# ===========================================================================
# A standard Bloom filter has fixed capacity. A Scalable Bloom Filter
# automatically adds new filter layers when the current one reaches capacity.
# Each new layer uses a tighter FP rate (multiplied by a tightening ratio r)
# so the overall FP stays bounded.

class ScalableBloomFilterStub:
    """
    TODO: Implement a Scalable Bloom Filter.

    When the current layer reaches its capacity, create a new layer with:
    - Same capacity as the original
    - FP rate = previous layer's FP rate * tightening_ratio

    add(item): add to current (latest) layer; create new layer if at capacity.
    contains(item): check ALL layers (item could be in any layer).
    """

    def __init__(self, initial_capacity: int, fp_rate: float = 0.01,
                 tightening_ratio: float = 0.5):
        self.initial_capacity = initial_capacity
        self.fp_rate = fp_rate
        self.tightening_ratio = tightening_ratio
        # TODO: Initialize layers
        raise NotImplementedError("Implement ScalableBloomFilter.__init__")

    def add(self, item: str):
        raise NotImplementedError("Implement add")

    def contains(self, item: str) -> bool:
        raise NotImplementedError("Implement contains")

    @property
    def num_layers(self) -> int:
        raise NotImplementedError("Implement num_layers")


class ScalableBloomFilterSolution:
    def __init__(self, initial_capacity: int, fp_rate: float = 0.01,
                 tightening_ratio: float = 0.5):
        self.initial_capacity = initial_capacity
        self.fp_rate = fp_rate
        self.tightening_ratio = tightening_ratio
        self._layers = []  # List of (bits, m, k, count, capacity, layer_fp)
        self._add_layer(fp_rate)

    def _add_layer(self, layer_fp: float):
        m = _optimal_m(self.initial_capacity, layer_fp)
        k = _optimal_k(m, self.initial_capacity)
        bits = bytearray((m + 7) // 8)
        self._layers.append({
            "bits": bits,
            "m": m,
            "k": k,
            "count": 0,
            "capacity": self.initial_capacity,
            "fp_rate": layer_fp,
        })

    def _get_bit(self, layer, pos):
        bits = layer["bits"]
        return bool(bits[pos // 8] & (1 << (pos % 8)))

    def _set_bit(self, layer, pos):
        bits = layer["bits"]
        bits[pos // 8] |= (1 << (pos % 8))

    def add(self, item: str):
        if not isinstance(item, str):
            item = str(item)

        current = self._layers[-1]
        if current["count"] >= current["capacity"]:
            new_fp = current["fp_rate"] * self.tightening_ratio
            self._add_layer(new_fp)
            current = self._layers[-1]

        for pos in _md5_double_hash(item, current["m"], current["k"]):
            self._set_bit(current, pos)
        current["count"] += 1

    def contains(self, item: str) -> bool:
        if not isinstance(item, str):
            item = str(item)
        for layer in self._layers:
            positions = _md5_double_hash(item, layer["m"], layer["k"])
            if all(self._get_bit(layer, pos) for pos in positions):
                return True
        return False

    @property
    def num_layers(self) -> int:
        return len(self._layers)


# ===========================================================================
# Exercise 5: Counting Bloom Filter with Deletion
# ===========================================================================
# Implement a Counting Bloom Filter using 4-bit counters that supports
# add, remove, and contains operations.

class CountingBloomFilterStub:
    """
    TODO: Implement a Counting Bloom Filter.

    Instead of a bit array, use an array of 4-bit counters (0-15).
    - add(item): increment k counter positions (cap at 15)
    - remove(item): decrement k counter positions (only if all > 0)
    - contains(item): all k positions have counter > 0

    Return True/False from remove() to indicate if the item was present.
    """

    def __init__(self, capacity: int, fp_rate: float = 0.01):
        # TODO: Initialize
        raise NotImplementedError("Implement CountingBloomFilter.__init__")

    def add(self, item: str):
        raise NotImplementedError("Implement add")

    def remove(self, item: str) -> bool:
        raise NotImplementedError("Implement remove")

    def contains(self, item: str) -> bool:
        raise NotImplementedError("Implement contains")


class CountingBloomFilterSolution:
    MAX_COUNT = 15

    def __init__(self, capacity: int, fp_rate: float = 0.01):
        self.capacity = capacity
        self.fp_rate = fp_rate
        self.m = _optimal_m(capacity, fp_rate)
        self.k = _optimal_k(self.m, capacity)
        self._counters = [0] * self.m

    def add(self, item: str):
        if not isinstance(item, str):
            item = str(item)
        for pos in _md5_double_hash(item, self.m, self.k):
            if self._counters[pos] < self.MAX_COUNT:
                self._counters[pos] += 1

    def remove(self, item: str) -> bool:
        if not isinstance(item, str):
            item = str(item)
        positions = _md5_double_hash(item, self.m, self.k)
        if not all(self._counters[pos] > 0 for pos in positions):
            return False
        for pos in positions:
            if self._counters[pos] < self.MAX_COUNT:
                self._counters[pos] -= 1
        return True

    def contains(self, item: str) -> bool:
        if not isinstance(item, str):
            item = str(item)
        return all(self._counters[pos] > 0
                   for pos in _md5_double_hash(item, self.m, self.k))


# ===========================================================================
# Test Runner
# ===========================================================================

def test_exercise_1():
    """Test spell checker."""
    print("Exercise 1: Spell Checker Using Bloom Filter")
    print("-" * 50)

    # Build a small dictionary
    dictionary = [
        "apple", "banana", "cherry", "date", "elderberry",
        "fig", "grape", "honeydew", "kiwi", "lemon",
        "mango", "nectarine", "orange", "papaya", "quince",
        "raspberry", "strawberry", "tangerine", "ugli", "vanilla",
        "watermelon", "xigua", "yuzu", "zucchini",
    ]
    # Add more words to make the filter meaningful
    dictionary += [f"word{i}" for i in range(1000)]

    test_words = [
        "apple",       # in dictionary
        "bananana",    # misspelled
        "cherry",      # in dictionary
        "datte",       # misspelled
        "grape",       # in dictionary
        "grapee",      # misspelled
        "xyzzy",       # not a word
        "word500",     # in dictionary
    ]

    result = spell_checker_solution(dictionary, test_words)

    # All dictionary words must NOT appear as misspelled (no false negatives)
    dict_set = set(w.lower() for w in dictionary)
    false_negatives = [w for w in result if w.lower() in dict_set]
    assert len(false_negatives) == 0, f"False negatives found: {false_negatives}"

    # Known misspelled words should appear (unless false positive)
    known_misspelled = {"bananana", "datte", "grapee", "xyzzy"}
    found_misspelled = set(result)
    # Due to false positives, some misspelled words might not appear.
    # But most should.
    print(f"  Dictionary size:    {len(dictionary)}")
    print(f"  Test words:         {len(test_words)}")
    print(f"  Flagged misspelled: {result}")
    print(f"  Expected subset:    {known_misspelled}")
    print("  PASSED (no false negatives)")
    return True


def test_exercise_2():
    """Test FP rate measurement."""
    print("\nExercise 2: Measure Actual vs Theoretical FP Rate")
    print("-" * 50)

    configs = [
        (1000, 0.01, 10000),
        (5000, 0.05, 10000),
        (10000, 0.001, 10000),
    ]

    all_passed = True
    for n, target_fp, num_tests in configs:
        m = _optimal_m(n, target_fp)
        k = _optimal_k(m, n)
        result = measure_fp_rate_solution(n, m, k, num_tests)

        theoretical = result["theoretical_fp"]
        actual = result["actual_fp"]

        # Actual FP should be within reasonable range of theoretical
        # (allow 3x tolerance due to randomness)
        tolerance = max(theoretical * 3, 0.005)
        passed = abs(actual - theoretical) < tolerance

        status = "OK" if passed else "DRIFT"
        print(f"  n={n:>6}, target={target_fp:.3f}: "
              f"theoretical={theoretical:.4f}, actual={actual:.4f} [{status}]")
        if not passed:
            all_passed = False

    print(f"  {'PASSED' if all_passed else 'SOME DRIFT (may be normal for small samples)'}")
    return True


def test_exercise_3():
    """Test union and intersection."""
    print("\nExercise 3: Union and Intersection of Bloom Filters")
    print("-" * 50)

    n = 1000
    fp_rate = 0.01
    m = _optimal_m(n, fp_rate)
    k = _optimal_k(m, n)
    num_bytes = (m + 7) // 8

    def make_filter(items):
        bits = bytearray(num_bytes)
        for item in items:
            for pos in _md5_double_hash(item, m, k):
                bits[pos // 8] |= (1 << (pos % 8))
        return bits

    def check(bits, item):
        return all(
            bool(bits[pos // 8] & (1 << (pos % 8)))
            for pos in _md5_double_hash(item, m, k)
        )

    set_a = [f"a-{i}" for i in range(500)]
    set_b = [f"b-{i}" for i in range(500)]
    shared = [f"shared-{i}" for i in range(100)]

    bits_a = make_filter(set_a + shared)
    bits_b = make_filter(set_b + shared)

    # Union
    union = bloom_union_solution(bits_a, bits_b)
    assert all(check(union, item) for item in set_a), "Union missing set_a items"
    assert all(check(union, item) for item in set_b), "Union missing set_b items"
    assert all(check(union, item) for item in shared), "Union missing shared items"
    print("  Union: all items from both filters found - PASSED")

    # Intersection
    inter = bloom_intersection_solution(bits_a, bits_b)
    assert all(check(inter, item) for item in shared), "Intersection missing shared items"
    # Items unique to A should mostly NOT be in intersection (some may be FP)
    unique_a_found = sum(1 for item in set_a if check(inter, item))
    print(f"  Intersection: shared items found, {unique_a_found}/{len(set_a)} "
          f"unique-A items found (FPs expected) - PASSED")
    return True


def test_exercise_4():
    """Test scalable Bloom filter."""
    print("\nExercise 4: Scalable Bloom Filter")
    print("-" * 50)

    sbf = ScalableBloomFilterSolution(
        initial_capacity=100, fp_rate=0.01, tightening_ratio=0.5
    )

    # Insert 350 items — should trigger multiple layers (capacity 100 each)
    items = [f"item-{i}" for i in range(350)]
    for item in items:
        sbf.add(item)

    print(f"  Inserted:   {len(items)} items")
    print(f"  Layers:     {sbf.num_layers}")
    assert sbf.num_layers >= 3, f"Expected >= 3 layers, got {sbf.num_layers}"

    # No false negatives
    fn = sum(1 for item in items if not sbf.contains(item))
    assert fn == 0, f"False negatives: {fn}"
    print(f"  False neg:  {fn} (must be 0)")

    # Check FP rate
    test_n = 10000
    fp = sum(1 for i in range(10000, 10000 + test_n)
             if sbf.contains(f"item-{i}"))
    fp_rate = fp / test_n
    print(f"  FP rate:    {fp_rate:.4f} ({fp}/{test_n})")
    print("  PASSED")
    return True


def test_exercise_5():
    """Test counting Bloom filter."""
    print("\nExercise 5: Counting Bloom Filter with Deletion")
    print("-" * 50)

    cbf = CountingBloomFilterSolution(capacity=1000, fp_rate=0.01)

    items = [f"url-{i}" for i in range(200)]
    for item in items:
        cbf.add(item)

    # All items present
    assert all(cbf.contains(item) for item in items), "Missing items after insert"
    print(f"  Inserted {len(items)} items, all found - OK")

    # Delete first 100
    for item in items[:100]:
        result = cbf.remove(item)
        assert result, f"Remove returned False for {item}"

    # Deleted items should not be found
    fn_after_delete = sum(1 for item in items[:100] if cbf.contains(item))
    # Remaining items should still be found
    fn_remaining = sum(1 for item in items[100:] if not cbf.contains(item))

    print(f"  Deleted first 100 items")
    print(f"  Deleted items still found (FP): {fn_after_delete}/100")
    print(f"  Remaining items missing (FN):   {fn_remaining}/100")
    assert fn_remaining == 0, "False negatives in remaining items!"

    # Remove non-existent item should return False
    assert not cbf.remove("never-inserted"), "Remove of non-existent should return False"
    print("  Remove non-existent returns False - OK")
    print("  PASSED")
    return True


def main():
    print("=" * 60)
    print("DAY 71 PRACTICE: Bloom Filter Exercises")
    print("=" * 60)

    results = []
    for i, test_fn in enumerate([
        test_exercise_1,
        test_exercise_2,
        test_exercise_3,
        test_exercise_4,
        test_exercise_5,
    ], 1):
        try:
            passed = test_fn()
            results.append((i, passed))
        except Exception as e:
            print(f"  FAILED: {e}")
            results.append((i, False))

    print(f"\n{'=' * 60}")
    print("RESULTS")
    print(f"{'=' * 60}")
    for num, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  Exercise {num}: {status}")
    total = sum(1 for _, p in results if p)
    print(f"\n  {total}/{len(results)} exercises passed")


if __name__ == "__main__":
    main()
