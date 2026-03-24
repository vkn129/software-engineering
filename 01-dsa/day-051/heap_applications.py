"""
Day 51: Heap Applications — Where Priority Queues Shine
========================================================
Practical applications of heaps beyond basic insert/extract:
    - Top-K extraction
    - Running median (two-heap technique)
    - Event-driven simulation
    - Frequency sort

All implementations use Python's heapq for brevity (we built our own yesterday).
Today is about the PATTERNS, not the heap itself.

Run: python heap_applications.py
"""

import heapq
from collections import Counter


# ─── Top-K Extraction ───────────────────────────────────────────────

def top_k_largest(nums, k):
    """
    Return the k largest elements from nums using a min-heap of size k.

    Why min-heap? We want to DISCARD small elements. The min-heap's root
    is the smallest of our k candidates — if a new element is larger,
    we replace the root. After scanning all elements, only the k largest remain.

    Time: O(n log k) — each of n elements may trigger a heap operation of O(log k)
    Space: O(k)
    """
    heap = []
    for num in nums:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heapreplace(heap, num)  # pop smallest, push new (one sift)
    return sorted(heap, reverse=True)


def top_k_frequent(nums, k):
    """
    Return the k most frequent elements.

    Two-phase approach:
    1. Count frequencies: O(n)
    2. Use min-heap of size k on frequencies: O(n log k)

    This is how search engines find "trending" terms — count occurrences
    in a time window, then extract top-k.
    """
    freq = Counter(nums)
    heap = []
    for num, count in freq.items():
        if len(heap) < k:
            heapq.heappush(heap, (count, num))
        elif count > heap[0][0]:
            heapq.heapreplace(heap, (count, num))
    return [num for _, num in sorted(heap, reverse=True)]


# ─── Running Median (Two-Heap Technique) ────────────────────────────

class RunningMedian:
    """
    Maintain the median of a stream of numbers using two heaps.

    Insight: split the numbers into two halves at the median.
    - Left half (smaller numbers) → max-heap (want quick access to the largest of the small half)
    - Right half (larger numbers) → min-heap (want quick access to the smallest of the large half)

    The median is either:
    - The top of the left max-heap (odd count)
    - The average of both tops (even count)

    Python only has min-heap, so we negate values for the max-heap.

    Real-world use:
    - Financial: rolling median price (more robust to outliers than mean)
    - Health: median heart rate over a window
    - Monitoring: median response time (P50)
    """

    def __init__(self):
        self._lo = []  # max-heap (negated values) — smaller half
        self._hi = []  # min-heap — larger half

    def add(self, num):
        # Step 1: Add to appropriate heap
        if not self._lo or num <= -self._lo[0]:
            heapq.heappush(self._lo, -num)
        else:
            heapq.heappush(self._hi, num)

        # Step 2: Rebalance — sizes differ by at most 1, lo gets the extra
        if len(self._lo) > len(self._hi) + 1:
            heapq.heappush(self._hi, -heapq.heappop(self._lo))
        elif len(self._hi) > len(self._lo):
            heapq.heappush(self._lo, -heapq.heappop(self._hi))

    @property
    def median(self):
        if not self._lo:
            raise ValueError("No data")
        if len(self._lo) > len(self._hi):
            return -self._lo[0]
        return (-self._lo[0] + self._hi[0]) / 2

    @property
    def count(self):
        return len(self._lo) + len(self._hi)


# ─── Event-Driven Simulation ────────────────────────────────────────

class EventSimulator:
    """
    A simple discrete event simulator using a min-heap of (time, event).

    This is the core pattern behind:
    - Network simulators (ns-3): packet arrival/departure events
    - Game engines: scheduled actions, timers, cooldowns
    - OS scheduling: timer interrupts
    - Dijkstra's algorithm: "process cheapest unvisited node"

    Events are processed in chronological order. Processing an event
    may schedule new future events.
    """

    def __init__(self):
        self._queue = []
        self._time = 0
        self._counter = 0  # Tie-breaker for same-time events

    def schedule(self, time, event_type, data=None):
        """Schedule an event at the given time."""
        self._counter += 1
        heapq.heappush(self._queue, (time, self._counter, event_type, data))

    def run(self, handler, max_events=1000):
        """
        Process events by calling handler(time, event_type, data, scheduler).
        Handler can schedule new events via the scheduler callback.
        """
        processed = 0
        while self._queue and processed < max_events:
            time, _, event_type, data = heapq.heappop(self._queue)
            self._time = time
            handler(time, event_type, data, self.schedule)
            processed += 1
        return processed

    @property
    def current_time(self):
        return self._time

    @property
    def pending(self):
        return len(self._queue)


# ─── Frequency Sort ─────────────────────────────────────────────────

def frequency_sort(s):
    """
    Sort characters in a string by frequency, descending.
    Example: "tree" → "eert" (or "eetr")

    Uses a max-heap keyed by (-count, char) so most frequent comes first.
    """
    freq = Counter(s)
    heap = [(-count, char) for char, count in freq.items()]
    heapq.heapify(heap)

    result = []
    while heap:
        neg_count, char = heapq.heappop(heap)
        result.append(char * (-neg_count))
    return ''.join(result)


# ─── Merge K Sorted Streams ────────────────────────────────────────

def merge_k_sorted(iterables):
    """
    Merge k sorted iterables into a single sorted sequence.

    This is heapq.merge() — used in external sorting when data doesn't
    fit in memory. Sort chunks that fit in RAM, write to disk, then
    merge the sorted chunks using a k-way merge with a heap.

    Time: O(N log k) where N = total elements
    """
    return list(heapq.merge(*iterables))


# ─── Demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 51: Heap Applications")
    print("=" * 60)

    # Top-K
    print("\n--- Top-K Largest ---")
    data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    print(f"  Data: {data}")
    print(f"  Top 3: {top_k_largest(data, 3)}")
    print(f"  Top 5: {top_k_largest(data, 5)}")

    # Top-K Frequent
    print("\n--- Top-K Most Frequent ---")
    data = [1, 1, 1, 2, 2, 3, 3, 3, 3, 4]
    print(f"  Data: {data}")
    print(f"  Top 2 frequent: {top_k_frequent(data, 2)}")

    # Running Median
    print("\n--- Running Median ---")
    rm = RunningMedian()
    stream = [2, 1, 5, 7, 2, 0, 5]
    for val in stream:
        rm.add(val)
        print(f"  Add {val} → median = {rm.median}")

    # Event Simulation
    print("\n--- Event-Driven Simulation (Simple Server) ---")
    # Simulate a server processing requests with arrival/completion events
    log = []

    def server_handler(time, event_type, data, schedule):
        if event_type == "arrive":
            log.append(f"  t={time:.1f}: Request {data} arrived, processing...")
            # Schedule completion 2 time units later
            schedule(time + 2, "complete", data)
        elif event_type == "complete":
            log.append(f"  t={time:.1f}: Request {data} completed")

    sim = EventSimulator()
    sim.schedule(0, "arrive", "A")
    sim.schedule(1, "arrive", "B")
    sim.schedule(3, "arrive", "C")
    sim.run(server_handler)
    for line in log:
        print(line)

    # Frequency Sort
    print("\n--- Frequency Sort ---")
    for s in ["tree", "cccaaa", "Aabb"]:
        print(f"  '{s}' → '{frequency_sort(s)}'")

    # K-way Merge
    print("\n--- K-way Merge ---")
    lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    print(f"  Lists: {lists}")
    print(f"  Merged: {merge_k_sorted(lists)}")

    print("\n✓ All demos complete")
