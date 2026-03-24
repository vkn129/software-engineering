"""
Day 62 Practice: Median Maintenance and Advanced Heaps

5 exercises — from sliding window median to percentile tracking.
Each has a TODO stub, a solution, and a test.

Run: python3 practice.py
"""

import heapq
import random


# =============================================================================
# Exercise 1: Sliding Window Median
#
# Given an array and window size k, return the median of each window as it
# slides across the array. For example:
#   nums = [1, 3, -1, -3, 5, 3, 6, 7], k = 3
#   windows: [1,3,-1], [3,-1,-3], [-1,-3,5], [-3,5,3], [5,3,6], [3,6,7]
#   medians: [1, -1, -1, 3, 5, 6]
#
# Hint: Use a two-heap approach, but you also need to handle removals.
#       Lazy deletion — mark elements as removed, clean up when they surface.
# =============================================================================

def sliding_window_median(nums, k):
    """Return list of medians for each window of size k."""
    return None  # TODO


def _sliding_window_median_solution(nums, k):
    """
    Two-heap with lazy deletion.

    We maintain a max-heap (lo) for the lower half and min-heap (hi) for the
    upper half, just like MedianFinder. But when we slide the window, instead
    of truly removing the outgoing element, we record it in a 'to_remove' dict
    and only actually pop it when it surfaces at the top of a heap.
    """
    if not nums or k == 0:
        return []

    lo = []   # max-heap (negated)
    hi = []   # min-heap
    to_remove = {}  # value -> count of pending removals
    lo_size = 0
    hi_size = 0
    result = []

    def get_median():
        if lo_size > hi_size:
            return float(-lo[0])
        return (-lo[0] + hi[0]) / 2.0

    def remove_top(heap, is_max_heap):
        """Pop elements from top that are pending removal."""
        while heap:
            val = -heap[0] if is_max_heap else heap[0]
            if to_remove.get(val, 0) > 0:
                to_remove[val] -= 1
                if to_remove[val] == 0:
                    del to_remove[val]
                heapq.heappop(heap)
            else:
                break

    def rebalance():
        nonlocal lo_size, hi_size
        # lo can be at most 1 larger than hi
        if lo_size > hi_size + 1:
            val = -heapq.heappop(lo)
            heapq.heappush(hi, val)
            lo_size -= 1
            hi_size += 1
            remove_top(lo, True)
        elif hi_size > lo_size:
            val = heapq.heappop(hi)
            heapq.heappush(lo, -val)
            hi_size -= 1
            lo_size += 1
            remove_top(hi, False)

    # Initialize with first k elements
    initial = sorted(nums[:k])
    half = k // 2
    for val in initial[:k - half]:
        heapq.heappush(lo, -val)
        lo_size += 1
    for val in initial[k - half:]:
        heapq.heappush(hi, val)
        hi_size += 1

    result.append(get_median())

    for i in range(k, len(nums)):
        outgoing = nums[i - k]
        incoming = nums[i]

        # Mark outgoing for lazy deletion
        to_remove[outgoing] = to_remove.get(outgoing, 0) + 1

        # Determine which heap the outgoing logically belongs to
        if outgoing <= -lo[0]:
            lo_size -= 1
        else:
            hi_size -= 1

        # Insert incoming
        if lo and incoming <= -lo[0]:
            heapq.heappush(lo, -incoming)
            lo_size += 1
        else:
            heapq.heappush(hi, incoming)
            hi_size += 1

        rebalance()
        remove_top(lo, True)
        remove_top(hi, False)

        result.append(get_median())

    return result


# =============================================================================
# Exercise 2: Median Finder with Remove
#
# Like the standard MedianFinder, but also supports remove_num(num).
# Removing a number that doesn't exist should raise ValueError.
#
# Hint: Use the same lazy deletion trick as the sliding window.
# =============================================================================

class MedianFinderWithRemove:
    """MedianFinder that also supports removing numbers."""

    def __init__(self):
        pass  # TODO

    def add_num(self, num):
        return None  # TODO

    def remove_num(self, num):
        return None  # TODO

    def find_median(self):
        return None  # TODO


class _MedianFinderWithRemoveSolution:
    def __init__(self):
        self.lo = []       # max-heap (negated)
        self.hi = []       # min-heap
        self.lo_size = 0   # logical size (excluding lazily deleted)
        self.hi_size = 0
        self.to_remove = {}
        self.all_counts = {}  # track actual element counts for validation

    def _clean_tops(self):
        while self.lo:
            val = -self.lo[0]
            if self.to_remove.get(val, 0) > 0:
                self.to_remove[val] -= 1
                if self.to_remove[val] == 0:
                    del self.to_remove[val]
                heapq.heappop(self.lo)
            else:
                break
        while self.hi:
            val = self.hi[0]
            if self.to_remove.get(val, 0) > 0:
                self.to_remove[val] -= 1
                if self.to_remove[val] == 0:
                    del self.to_remove[val]
                heapq.heappop(self.hi)
            else:
                break

    def _rebalance(self):
        if self.lo_size > self.hi_size + 1:
            self._clean_tops()
            val = -heapq.heappop(self.lo)
            heapq.heappush(self.hi, val)
            self.lo_size -= 1
            self.hi_size += 1
        elif self.hi_size > self.lo_size:
            self._clean_tops()
            val = heapq.heappop(self.hi)
            heapq.heappush(self.lo, -val)
            self.hi_size -= 1
            self.lo_size += 1
        self._clean_tops()

    def add_num(self, num):
        self.all_counts[num] = self.all_counts.get(num, 0) + 1
        if not self.lo or num <= -self.lo[0]:
            heapq.heappush(self.lo, -num)
            self.lo_size += 1
        else:
            heapq.heappush(self.hi, num)
            self.hi_size += 1
        self._rebalance()

    def remove_num(self, num):
        if self.all_counts.get(num, 0) == 0:
            raise ValueError(f"{num} not in the collection")
        self.all_counts[num] -= 1
        if self.all_counts[num] == 0:
            del self.all_counts[num]

        self._clean_tops()
        if self.lo and num <= -self.lo[0]:
            self.to_remove[num] = self.to_remove.get(num, 0) + 1
            self.lo_size -= 1
        else:
            self.to_remove[num] = self.to_remove.get(num, 0) + 1
            self.hi_size -= 1
        self._clean_tops()
        self._rebalance()

    def find_median(self):
        if self.lo_size + self.hi_size == 0:
            raise ValueError("Empty")
        self._clean_tops()
        if self.lo_size > self.hi_size:
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2.0


# =============================================================================
# Exercise 3: Dijkstra Decrease-Key Counter
#
# Implement Dijkstra's shortest path and count how many decrease-key
# operations occur. Compare the count for a dense vs sparse graph.
# This shows WHY Fibonacci heaps matter for dense graphs.
#
# Return: (distances_dict, decrease_key_count)
# =============================================================================

def dijkstra_with_stats(graph, source):
    """
    Run Dijkstra on graph (adjacency dict: {node: [(neighbor, weight), ...]}).
    Return (distances, decrease_key_count).
    """
    return None  # TODO


def _dijkstra_with_stats_solution(graph, source):
    dist = {node: float('inf') for node in graph}
    dist[source] = 0
    decrease_key_count = 0
    visited = set()
    # Standard binary-heap Dijkstra. We count "decrease-key" as any time we
    # find a shorter path and push a new entry.
    pq = [(0, source)]

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        for v, w in graph.get(u, []):
            new_dist = d + w
            if new_dist < dist[v]:
                dist[v] = new_dist
                decrease_key_count += 1
                heapq.heappush(pq, (new_dist, v))

    return dist, decrease_key_count


# =============================================================================
# Exercise 4: Binomial Heap
#
# Implement a Binomial Heap with: insert, find_min, extract_min, merge.
# A binomial heap is a collection of binomial trees, where each tree of
# order k has exactly 2^k nodes. Simpler than Fibonacci, good stepping stone.
#
# A BinomialTree of order k:
#   - Root with k children: trees of order k-1, k-2, ..., 0
#   - Has exactly 2^k nodes
# =============================================================================

class BinomialNode:
    def __init__(self, key):
        self.key = key
        self.degree = 0
        self.children = []  # list of BinomialNode, ordered by degree
        self.parent = None


class BinomialHeap:
    """Binomial heap: a list of binomial trees with unique degrees."""

    def __init__(self):
        self.trees = []  # list of BinomialNode roots, sorted by degree
        self.n = 0

    def insert(self, key):
        return None  # TODO

    def find_min(self):
        return None  # TODO

    def extract_min(self):
        return None  # TODO

    def merge(self, other):
        return None  # TODO


class _BinomialHeapSolution:
    def __init__(self):
        self.trees = []
        self.n = 0

    @staticmethod
    def _merge_trees(t1, t2):
        """Merge two binomial trees of same degree. Smaller key becomes root."""
        if t1.key > t2.key:
            t1, t2 = t2, t1
        t2.parent = t1
        t1.children.append(t2)
        t1.degree += 1
        return t1

    def _merge_tree_lists(self, trees1, trees2):
        """Merge two sorted-by-degree lists of binomial trees."""
        merged = []
        i, j = 0, 0
        while i < len(trees1) and j < len(trees2):
            if trees1[i].degree <= trees2[j].degree:
                merged.append(trees1[i])
                i += 1
            else:
                merged.append(trees2[j])
                j += 1
        merged.extend(trees1[i:])
        merged.extend(trees2[j:])

        # Now consolidate: combine trees of same degree
        if not merged:
            return []
        result = []
        carry = None
        for tree in merged:
            if carry is None:
                carry = tree
            elif carry.degree == tree.degree:
                carry = self._merge_trees(carry, tree)
            else:
                result.append(carry)
                carry = tree
        if carry:
            # Check if carry conflicts with last in result
            while result and result[-1].degree == carry.degree:
                carry = self._merge_trees(result.pop(), carry)
            result.append(carry)
        return result

    def insert(self, key):
        new_node = BinomialNode(key)
        self.trees = self._merge_tree_lists(self.trees, [new_node])
        self.n += 1
        return new_node

    def find_min(self):
        if not self.trees:
            raise ValueError("Heap is empty")
        return min(t.key for t in self.trees)

    def extract_min(self):
        if not self.trees:
            raise ValueError("Heap is empty")
        # Find tree with minimum root
        min_idx = 0
        for i, t in enumerate(self.trees):
            if t.key < self.trees[min_idx].key:
                min_idx = i
        min_tree = self.trees.pop(min_idx)
        # Children of min_tree form a new binomial heap
        for child in min_tree.children:
            child.parent = None
        self.trees = self._merge_tree_lists(self.trees, min_tree.children)
        self.n -= 1
        return min_tree.key

    def merge(self, other):
        self.trees = self._merge_tree_lists(self.trees, other.trees)
        self.n += other.n
        other.trees = []
        other.n = 0


# =============================================================================
# Exercise 5: Percentile Tracker
#
# Generalize MedianFinder: given a percentile p (0-100), maintain a running
# stream and return the p-th percentile at any time.
#   - p=50 is the median
#   - p=25 is the first quartile
#   - p=99 is the 99th percentile
#
# Strategy: keep two heaps where the lower heap holds roughly p% of elements.
# =============================================================================

class PercentileTracker:
    """Track any percentile of a running stream."""

    def __init__(self, percentile):
        """percentile: integer 1-99"""
        self.percentile = percentile  # TODO: complete init

    def add_num(self, num):
        return None  # TODO

    def get_percentile(self):
        return None  # TODO


class _PercentileTrackerSolution:
    def __init__(self, percentile):
        if not (1 <= percentile <= 99):
            raise ValueError("Percentile must be between 1 and 99")
        self.p = percentile / 100.0
        self.lo = []   # max-heap (negated), stores lower p fraction
        self.hi = []   # min-heap, stores upper (1-p) fraction
        self.count = 0

    def _target_lo_size(self):
        """How many elements should be in lo for current count."""
        # For percentile p, lo should have ceil(count * p/100) elements
        import math
        return max(1, math.ceil(self.count * self.p))

    def add_num(self, num):
        self.count += 1
        # Insert into appropriate heap
        if not self.lo or num <= -self.lo[0]:
            heapq.heappush(self.lo, -num)
        else:
            heapq.heappush(self.hi, num)

        # Rebalance to maintain target lo size
        target = self._target_lo_size()
        while len(self.lo) > target:
            val = -heapq.heappop(self.lo)
            heapq.heappush(self.hi, val)
        while len(self.lo) < target:
            if self.hi:
                val = heapq.heappop(self.hi)
                heapq.heappush(self.lo, -val)
            else:
                break

    def get_percentile(self):
        if not self.lo:
            raise ValueError("No data")
        return float(-self.lo[0])


# =============================================================================
# Test Runner
# =============================================================================

def run_tests():
    results = []

    # --- Test 1: Sliding Window Median ---
    def test_sliding_window_median():
        user_fn = sliding_window_median
        sol_fn = _sliding_window_median_solution

        cases = [
            ([1, 3, -1, -3, 5, 3, 6, 7], 3),
            ([1, 2, 3, 4, 5], 2),
            ([5, 5, 5, 5], 3),
            ([1], 1),
            ([1, 2], 1),
            ([7, 0, 3, 9, 2, 8, 1], 4),
        ]
        for nums, k in cases:
            user_result = user_fn(nums, k)
            expected = sol_fn(nums, k)
            if user_result is None:
                return None  # not implemented
            assert user_result == expected, f"Failed for {nums}, k={k}: got {user_result}, expected {expected}"
        return True

    # --- Test 2: Median Finder with Remove ---
    def test_median_with_remove():
        user = MedianFinderWithRemove()
        sol = _MedianFinderWithRemoveSolution()

        ops = [
            ('add', 1), ('add', 2), ('add', 3),
            ('median', None),  # expect 2.0
            ('remove', 2),
            ('median', None),  # expect 2.0 (avg of 1,3)
            ('add', 4), ('add', 5),
            ('median', None),  # expect 3.0 -> [1,3,4,5] median = (3+4)/2 = 3.5
            ('remove', 1),
            ('median', None),  # [3,4,5] median = 4.0
        ]
        for op, val in ops:
            if op == 'add':
                ur = user.add_num(val)
                sol.add_num(val)
                if ur is None and val is not None:
                    # Check if it's truly unimplemented
                    try:
                        user.find_median()
                    except:
                        return None
            elif op == 'remove':
                ur = user.remove_num(val)
                sol.remove_num(val)
                if ur is None:
                    return None
            elif op == 'median':
                user_med = user.find_median()
                sol_med = sol.find_median()
                if user_med is None:
                    return None
                assert abs(user_med - sol_med) < 1e-9, f"Median mismatch: {user_med} vs {sol_med}"
        return True

    # --- Test 3: Dijkstra with stats ---
    def test_dijkstra_stats():
        # Sparse graph
        sparse = {
            0: [(1, 4), (2, 1)],
            1: [(3, 1)],
            2: [(1, 2), (3, 5)],
            3: [],
        }
        result = dijkstra_with_stats(sparse, 0)
        if result is None:
            return None
        dist, dk_count = result
        assert dist[0] == 0
        assert dist[1] == 3  # 0->2->1
        assert dist[2] == 1
        assert dist[3] == 4  # 0->2->1->3
        assert dk_count > 0

        # Dense graph: complete graph with 20 nodes
        n = 20
        dense = {i: [] for i in range(n)}
        random.seed(123)
        for i in range(n):
            for j in range(n):
                if i != j:
                    dense[i].append((j, random.randint(1, 100)))
        dist_d, dk_dense = dijkstra_with_stats(dense, 0)
        assert all(d < float('inf') for d in dist_d.values())
        return True, dk_count, dk_dense

    # --- Test 4: Binomial Heap ---
    def test_binomial_heap():
        user_heap = BinomialHeap()
        sol_heap = _BinomialHeapSolution()

        vals = [5, 3, 8, 1, 7, 2, 9, 4, 6, 0]
        for v in vals:
            r = user_heap.insert(v)
            sol_heap.insert(v)
            if r is None:
                return None

        user_min = user_heap.find_min()
        if user_min is None:
            return None
        assert user_min == 0, f"find_min: expected 0, got {user_min}"

        extracted_user = []
        for _ in range(len(vals)):
            v = user_heap.extract_min()
            if v is None:
                return None
            extracted_user.append(v)
        assert extracted_user == sorted(vals), f"Extract order wrong: {extracted_user}"

        # Test merge
        h1 = BinomialHeap()
        h2 = BinomialHeap()
        for v in [3, 1, 5]:
            h1.insert(v)
        for v in [2, 4, 0]:
            h2.insert(v)
        mr = h1.merge(h2)
        if mr is None:
            return None
        merged_result = []
        for _ in range(6):
            merged_result.append(h1.extract_min())
        assert merged_result == [0, 1, 2, 3, 4, 5], f"Merge extract wrong: {merged_result}"
        return True

    # --- Test 5: Percentile Tracker ---
    def test_percentile_tracker():
        # Test p50 (median)
        pt50 = PercentileTracker(50)
        for v in [1, 2, 3, 4, 5]:
            r = pt50.add_num(v)
        result = pt50.get_percentile()
        if result is None:
            return None
        assert result == 3.0, f"p50 of [1..5] should be 3.0, got {result}"

        # Test p25
        pt25 = _PercentileTrackerSolution(25)
        for v in range(1, 101):
            pt25.add_num(v)
        p25_val = pt25.get_percentile()

        user_pt25 = PercentileTracker(25)
        for v in range(1, 101):
            user_pt25.add_num(v)
        user_p25 = user_pt25.get_percentile()
        assert abs(user_p25 - p25_val) < 2, f"p25 too far off: {user_p25} vs {p25_val}"

        # Test p99
        pt99 = PercentileTracker(99)
        for v in range(1, 101):
            pt99.add_num(v)
        p99_val = pt99.get_percentile()
        assert p99_val >= 95, f"p99 should be near 99, got {p99_val}"
        return True

    # --- Run all tests ---
    tests = [
        ("1. Sliding Window Median", test_sliding_window_median),
        ("2. Median Finder with Remove", test_median_with_remove),
        ("3. Dijkstra Decrease-Key Stats", test_dijkstra_stats),
        ("4. Binomial Heap", test_binomial_heap),
        ("5. Percentile Tracker", test_percentile_tracker),
    ]

    print("=" * 70)
    print("Day 62 Practice — Median Maintenance & Advanced Heaps")
    print("=" * 70)

    for name, test_fn in tests:
        try:
            result = test_fn()
            if result is None:
                print(f"\u2b1c {name} — not implemented yet")
            elif name == "3. Dijkstra Decrease-Key Stats" and isinstance(result, tuple):
                _, dk_sparse, dk_dense = result
                print(f"\u2705 {name} — passed (sparse dk={dk_sparse}, dense dk={dk_dense})")
            else:
                print(f"\u2705 {name} — passed")
        except Exception as e:
            print(f"\u274c {name} — FAILED: {e}")

    print()


if __name__ == "__main__":
    run_tests()
