"""
Day 70 Practice: Advanced Cache Exercises
==========================================
5 exercises building on the cache fundamentals from cache.py.

Each exercise tackles a real-world cache design challenge.
"""

import time
import threading
import random
from collections import defaultdict


# ===================================================================
# Exercise 1: LFU (Least Frequently Used) Cache
# ===================================================================
# LFU evicts the key with the lowest access count.
# If there's a tie, evict the least recently used among them.
#
# Data structure: hash map + frequency buckets.
# Each frequency level has its own doubly linked list of keys.
#
#   freq_map:
#     1 -> [key_D, key_E]     (accessed once)
#     2 -> [key_B]            (accessed twice)
#     5 -> [key_A, key_C]     (accessed five times)
#
#   min_freq tracks the lowest non-empty frequency bucket.
#   Eviction: remove tail of freq_map[min_freq].

class _LFUNode:
    __slots__ = ('key', 'value', 'freq', 'prev', 'next')

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.freq = 1
        self.prev = None
        self.next = None


class _LFUList:
    """Doubly linked list for one frequency bucket."""

    def __init__(self):
        self.head = _LFUNode()
        self.tail = _LFUNode()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def add_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self.size -= 1

    def remove_last(self):
        if self.size == 0:
            return None
        node = self.tail.prev
        self.remove(node)
        return node

    def is_empty(self):
        return self.size == 0


class LFUCache:
    """Least Frequently Used cache with O(1) get/put/evict.

    Uses three hash maps:
    - key_map: key -> node (for O(1) lookup)
    - freq_map: frequency -> doubly linked list of nodes at that frequency
    - min_freq: tracks current minimum frequency for O(1) eviction
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.key_map = {}           # key -> _LFUNode
        self.freq_map = defaultdict(lambda: _LFUList())  # freq -> _LFUList
        self.min_freq = 0
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _increment_freq(self, node: _LFUNode):
        """Move node from its current frequency bucket to freq+1 bucket."""
        old_freq = node.freq
        self.freq_map[old_freq].remove(node)

        # If the old bucket is now empty and it was the min, bump min_freq
        if self.freq_map[old_freq].is_empty():
            del self.freq_map[old_freq]
            if self.min_freq == old_freq:
                self.min_freq = old_freq + 1

        node.freq += 1
        self.freq_map[node.freq].add_front(node)

    def get(self, key):
        node = self.key_map.get(key)
        if node is None:
            self.misses += 1
            return None
        self.hits += 1
        self._increment_freq(node)
        return node.value

    def put(self, key, value):
        if self.capacity <= 0:
            return

        node = self.key_map.get(key)
        if node is not None:
            node.value = value
            self._increment_freq(node)
            return

        if len(self.key_map) >= self.capacity:
            # Evict from the min-frequency bucket (LRU within that bucket)
            victim = self.freq_map[self.min_freq].remove_last()
            if victim:
                del self.key_map[victim.key]
                if self.freq_map[self.min_freq].is_empty():
                    del self.freq_map[self.min_freq]
                self.evictions += 1

        new_node = _LFUNode(key, value)
        self.key_map[key] = new_node
        self.freq_map[1].add_front(new_node)
        self.min_freq = 1  # New node always has freq=1, which is the new min

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __len__(self):
        return len(self.key_map)


def exercise_1_demo():
    print("=" * 60)
    print("Exercise 1: LFU Cache")
    print("=" * 60)

    cache = LFUCache(capacity=3)

    # A accessed 3 times, B accessed 2 times, C accessed 1 time
    cache.put("A", 1)
    cache.get("A")
    cache.get("A")  # freq=3

    cache.put("B", 2)
    cache.get("B")  # freq=2

    cache.put("C", 3)  # freq=1

    print(f"A freq=3, B freq=2, C freq=1")
    print(f"Cache size: {len(cache)}")

    # Insert D -> should evict C (lowest frequency)
    cache.put("D", 4)
    print(f"After put(D): C evicted (lowest freq)")
    print(f"  get(C) = {cache.get('C')}  <- evicted")
    print(f"  get(A) = {cache.get('A')}  <- still here (freq=3)")
    print(f"  get(B) = {cache.get('B')}  <- still here (freq=2)")

    # Compare LFU vs LRU on frequency-skewed workload
    print(f"\nComparing LFU vs LRU on frequency-skewed workload:")
    print(f"  Keys 0-4 accessed 100 times each, keys 5-99 accessed once each")

    from cache import LRUCache

    random.seed(42)
    accesses = []
    # Hot keys accessed frequently
    for _ in range(500):
        accesses.append(f"key_{random.randint(0, 4)}")
    # Cold keys accessed once
    for i in range(5, 100):
        accesses.append(f"key_{i}")
    random.shuffle(accesses)

    for CacheClass, name in [(LFUCache, "LFU"), (LRUCache, "LRU")]:
        c = CacheClass(capacity=10)
        for key in accesses:
            val = c.get(key)
            if val is None:
                c.put(key, "data")
        rate = c.hit_rate if hasattr(c, 'hit_rate') else c.stats.hit_rate
        print(f"  {name}: hit rate = {rate:.2%}")

    print()


# ===================================================================
# Exercise 2: Write-Through vs Write-Back Cache
# ===================================================================
# Write-through: every write goes to cache AND backing store immediately.
#   Pro: backing store is always consistent.
#   Con: writes are slow (wait for backing store).
#
# Write-back: writes go to cache only; dirty entries flushed later.
#   Pro: writes are fast (only update cache).
#   Con: data loss risk if cache crashes before flush.

class BackingStore:
    """Simulates a slow backing store (like a database or disk)."""

    def __init__(self, latency: float = 0.001):
        self.data = {}
        self.write_count = 0
        self.read_count = 0
        self.latency = latency

    def read(self, key):
        self.read_count += 1
        time.sleep(self.latency)
        return self.data.get(key)

    def write(self, key, value):
        self.write_count += 1
        time.sleep(self.latency)
        self.data[key] = value


class WriteThroughCache:
    """Every write updates both cache and backing store immediately."""

    def __init__(self, capacity: int, store: BackingStore):
        self.cache = {}
        self.capacity = capacity
        self.store = store

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        # Cache miss: read from store
        val = self.store.read(key)
        if val is not None and len(self.cache) < self.capacity:
            self.cache[key] = val
        return val

    def put(self, key, value):
        # Write to BOTH cache and store (synchronous)
        self.cache[key] = value
        self.store.write(key, value)
        # Simple eviction if over capacity: remove arbitrary key
        if len(self.cache) > self.capacity:
            oldest = next(iter(self.cache))
            del self.cache[oldest]


class WriteBackCache:
    """Writes go to cache only; dirty entries are flushed on eviction or flush().

    Tracks which entries are 'dirty' (modified in cache but not yet written
    to the backing store).
    """

    def __init__(self, capacity: int, store: BackingStore):
        self.cache = {}
        self.dirty = set()  # Keys modified in cache but not flushed
        self.capacity = capacity
        self.store = store

    def get(self, key):
        if key in self.cache:
            return self.cache[key]
        val = self.store.read(key)
        if val is not None and len(self.cache) < self.capacity:
            self.cache[key] = val
        return val

    def put(self, key, value):
        # Write to cache only — much faster
        self.cache[key] = value
        self.dirty.add(key)
        if len(self.cache) > self.capacity:
            self._evict_one()

    def _evict_one(self):
        """Evict one entry. If dirty, flush to store first."""
        victim_key = next(iter(self.cache))
        if victim_key in self.dirty:
            self.store.write(victim_key, self.cache[victim_key])
            self.dirty.discard(victim_key)
        del self.cache[victim_key]

    def flush(self):
        """Write all dirty entries to backing store."""
        for key in list(self.dirty):
            self.store.write(key, self.cache[key])
        count = len(self.dirty)
        self.dirty.clear()
        return count


def exercise_2_demo():
    print("=" * 60)
    print("Exercise 2: Write-Through vs Write-Back Cache")
    print("=" * 60)

    num_writes = 100

    # Write-through
    store_wt = BackingStore(latency=0.0005)
    wt_cache = WriteThroughCache(capacity=20, store=store_wt)
    t0 = time.monotonic()
    for i in range(num_writes):
        wt_cache.put(f"key_{i % 20}", f"val_{i}")
    wt_time = time.monotonic() - t0

    # Write-back
    store_wb = BackingStore(latency=0.0005)
    wb_cache = WriteBackCache(capacity=20, store=store_wb)
    t0 = time.monotonic()
    for i in range(num_writes):
        wb_cache.put(f"key_{i % 20}", f"val_{i}")
    wb_cache.flush()
    wb_time = time.monotonic() - t0

    print(f"  {num_writes} writes with 0.5ms backing store latency:\n")
    print(f"  Write-through: {wt_time*1000:.1f}ms, {store_wt.write_count} store writes")
    print(f"  Write-back:    {wb_time*1000:.1f}ms, {store_wb.write_count} store writes")
    print(f"  Speedup:       {wt_time/wb_time:.1f}x fewer store writes with write-back")
    print()
    print(f"  Why? Write-through: every put() -> store write ({num_writes} total)")
    print(f"  Write-back: only dirty keys flushed ({store_wb.write_count} unique keys)")
    print(f"  Trade-off: write-back risks data loss if process crashes before flush")
    print()


# ===================================================================
# Exercise 3: Cache Stampede Prevention (Single-Flight Pattern)
# ===================================================================
# When a popular key expires, N threads all see a cache miss and all
# try to recompute the value. The single-flight pattern ensures only
# ONE thread recomputes; the rest wait for its result.

class SingleFlight:
    """Deduplicates concurrent calls for the same key.

    Only one thread executes the compute function; others wait for
    the result. This prevents cache stampede.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._in_flight = {}  # key -> (Event, result_container)

    def do(self, key, compute_fn):
        """Execute compute_fn for key, deduplicating concurrent calls.

        If another thread is already computing this key, wait for its result.
        """
        with self._lock:
            if key in self._in_flight:
                # Someone else is already computing this key — wait for them
                event, result = self._in_flight[key]
                waiting = True
            else:
                # We're the first — register ourselves
                event = threading.Event()
                result = [None]  # Mutable container to share result
                self._in_flight[key] = (event, result)
                waiting = False

        if waiting:
            event.wait()  # Block until the computing thread is done
            return result[0]
        else:
            # We're the computing thread
            try:
                value = compute_fn()
                result[0] = value
                return value
            finally:
                event.set()  # Wake up all waiting threads
                with self._lock:
                    del self._in_flight[key]


class StampedeProtectedCache:
    """Cache with single-flight stampede prevention."""

    def __init__(self, capacity: int):
        self.data = {}
        self.capacity = capacity
        self.flight = SingleFlight()
        self.recompute_count = 0
        self._lock = threading.Lock()

    def get(self, key, compute_fn):
        """Get key from cache. On miss, use single-flight to recompute."""
        with self._lock:
            if key in self.data:
                return self.data[key]

        # Cache miss — use single-flight
        value = self.flight.do(key, compute_fn)

        with self._lock:
            self.data[key] = value
        return value


def exercise_3_demo():
    print("=" * 60)
    print("Exercise 3: Cache Stampede Prevention")
    print("=" * 60)

    recompute_counter = {"with_sf": 0, "without_sf": 0}

    # Simulate expensive computation
    def expensive_compute(counter_key):
        recompute_counter[counter_key] += 1
        time.sleep(0.05)  # 50ms to "compute"
        return "computed_value"

    # --- Without single-flight: all threads recompute ---
    results_no_sf = [None] * 10
    barrier = threading.Barrier(10)

    def worker_no_sf(idx):
        barrier.wait()  # All threads start simultaneously
        results_no_sf[idx] = expensive_compute("without_sf")

    threads = [threading.Thread(target=worker_no_sf, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # --- With single-flight: only one thread recomputes ---
    sf = SingleFlight()
    results_sf = [None] * 10
    barrier2 = threading.Barrier(10)

    def worker_sf(idx):
        barrier2.wait()
        results_sf[idx] = sf.do("hot_key", lambda: expensive_compute("with_sf"))

    threads = [threading.Thread(target=worker_sf, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"  10 threads request the same expired key simultaneously:\n")
    print(f"  Without single-flight: {recompute_counter['without_sf']} recomputations")
    print(f"  With single-flight:    {recompute_counter['with_sf']} recomputation")
    print(f"  All threads got result? {all(r == 'computed_value' for r in results_sf)}")
    print()
    print(f"  Impact: at 1000 req/s with 2s recomputation time,")
    print(f"  stampede causes 2000 redundant calls to backing store.")
    print(f"  Single-flight reduces this to exactly 1.")
    print()


# ===================================================================
# Exercise 4: Adaptive Replacement Cache (ARC) — Simplified
# ===================================================================
# ARC balances between recency (LRU) and frequency (LFU) automatically.
#
# It maintains 4 lists:
#   T1: recently accessed once (recency)
#   T2: accessed more than once (frequency)
#   B1: ghost entries evicted from T1 (tracks what recency would have kept)
#   B2: ghost entries evicted from T2 (tracks what frequency would have kept)
#
# Adaptive parameter p:
#   - Hit in B1 -> recency was useful -> increase p (give T1 more space)
#   - Hit in B2 -> frequency was useful -> decrease p (give T2 more space)

class SimpleARC:
    """Simplified Adaptive Replacement Cache.

    Automatically adapts between favoring recency vs frequency based
    on the workload. Uses ghost lists to learn from eviction mistakes.
    """

    def __init__(self, capacity: int):
        self.c = capacity
        self.p = 0  # Adaptive parameter: target size for T1

        # Real caches (contain actual data)
        self.t1 = {}  # Recently seen once (key -> value)
        self.t1_order = []  # LRU order for T1
        self.t2 = {}  # Seen more than once (key -> value)
        self.t2_order = []  # LRU order for T2

        # Ghost lists (metadata only, no values)
        self.b1 = []  # Ghost of T1 evictions
        self.b2 = []  # Ghost of T2 evictions

        self.hits = 0
        self.misses = 0

    def _replace(self, in_b2: bool):
        """Evict one entry from T1 or T2."""
        if self.t1 and (len(self.t1) > self.p or (in_b2 and len(self.t1) == self.p)):
            # Evict from T1 (recency list)
            old = self.t1_order.pop(0)
            del self.t1[old]
            self.b1.append(old)
            if len(self.b1) > self.c:
                self.b1.pop(0)
        elif self.t2:
            # Evict from T2 (frequency list)
            old = self.t2_order.pop(0)
            del self.t2[old]
            self.b2.append(old)
            if len(self.b2) > self.c:
                self.b2.pop(0)

    def get(self, key):
        # Case 1: hit in T1 -> promote to T2 (now accessed twice)
        if key in self.t1:
            val = self.t1.pop(key)
            self.t1_order.remove(key)
            self.t2[key] = val
            self.t2_order.append(key)
            self.hits += 1
            return val

        # Case 2: hit in T2 -> move to MRU of T2
        if key in self.t2:
            self.t2_order.remove(key)
            self.t2_order.append(key)
            self.hits += 1
            return self.t2[key]

        self.misses += 1
        return None

    def put(self, key, value):
        # Already in T1 or T2? Update.
        if key in self.t1:
            self.t1.pop(key)
            self.t1_order.remove(key)
            self.t2[key] = value
            self.t2_order.append(key)
            return

        if key in self.t2:
            self.t2[key] = value
            self.t2_order.remove(key)
            self.t2_order.append(key)
            return

        # Ghost hit in B1 -> recency was useful, increase p
        if key in self.b1:
            delta = max(1, len(self.b2) // max(len(self.b1), 1))
            self.p = min(self.p + delta, self.c)
            self.b1.remove(key)
            if len(self.t1) + len(self.t2) >= self.c:
                self._replace(in_b2=False)
            self.t2[key] = value
            self.t2_order.append(key)
            return

        # Ghost hit in B2 -> frequency was useful, decrease p
        if key in self.b2:
            delta = max(1, len(self.b1) // max(len(self.b2), 1))
            self.p = max(self.p - delta, 0)
            self.b2.remove(key)
            if len(self.t1) + len(self.t2) >= self.c:
                self._replace(in_b2=True)
            self.t2[key] = value
            self.t2_order.append(key)
            return

        # Complete miss: insert into T1
        if len(self.t1) + len(self.t2) >= self.c:
            self._replace(in_b2=False)

        # Also cap ghost lists
        total_ghost = len(self.b1) + len(self.b2)
        if total_ghost >= self.c:
            if self.b1:
                self.b1.pop(0)
            elif self.b2:
                self.b2.pop(0)

        self.t1[key] = value
        self.t1_order.append(key)

    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __len__(self):
        return len(self.t1) + len(self.t2)


def exercise_4_demo():
    print("=" * 60)
    print("Exercise 4: Adaptive Replacement Cache (ARC)")
    print("=" * 60)

    from cache import LRUCache

    random.seed(42)
    capacity = 20

    # Workload: mix of recency-friendly and frequency-friendly patterns
    # Phase 1: sequential scan (hurts LRU, recency pattern)
    # Phase 2: repeated hot keys (frequency pattern)
    # Phase 3: mix
    accesses = []
    # Phase 1: scan through 50 keys sequentially
    accesses.extend([f"scan_{i}" for i in range(50)])
    # Phase 2: access 5 hot keys repeatedly
    for _ in range(200):
        accesses.append(f"hot_{random.randint(0, 4)}")
    # Phase 3: interleaved
    for _ in range(300):
        if random.random() < 0.3:
            accesses.append(f"scan_{random.randint(0, 49)}")
        else:
            accesses.append(f"hot_{random.randint(0, 4)}")

    # Run both caches
    lru = LRUCache(capacity=capacity)
    arc = SimpleARC(capacity=capacity)

    for key in accesses:
        # LRU
        if lru.get(key) is None:
            lru.put(key, "data")
        # ARC
        if arc.get(key) is None:
            arc.put(key, "data")

    print(f"  Mixed workload: scan + hot keys, cache size={capacity}\n")
    print(f"  LRU hit rate: {lru.stats.hit_rate:.2%}")
    print(f"  ARC hit rate: {arc.hit_rate:.2%}")
    print(f"  ARC adaptive parameter p={arc.p} (T1 target size)")
    print(f"  ARC T1 size={len(arc.t1)}, T2 size={len(arc.t2)}")
    print()
    print(f"  ARC adapts: when scans pollute the cache, it shifts weight")
    print(f"  toward frequency (T2). When recency matters, it shifts to T1.")
    print()


# ===================================================================
# Exercise 5: Cache Warming
# ===================================================================
# Given historical access frequency data, pre-populate the cache with
# the most likely needed items. Measure the improvement in hit rate
# during a "warm-up" period.

def exercise_5_demo():
    print("=" * 60)
    print("Exercise 5: Cache Warming")
    print("=" * 60)

    from cache import LRUCache

    random.seed(42)

    # Historical access frequency data (collected from previous runs)
    num_keys = 200
    frequency_data = {}
    for i in range(num_keys):
        # Zipf-like: few keys are very popular
        frequency_data[f"key_{i}"] = int(1000 / (i + 1))

    # Generate a new workload following similar distribution
    new_accesses = []
    for _ in range(5000):
        rank = int(random.paretovariate(1.0)) % num_keys
        new_accesses.append(f"key_{rank}")

    cache_size = 30

    # --- Cold cache (no warming) ---
    cold_cache = LRUCache(capacity=cache_size)
    cold_hits_over_time = []
    for i, key in enumerate(new_accesses):
        if cold_cache.get(key) is None:
            cold_cache.put(key, "data")
        if (i + 1) % 100 == 0:
            cold_hits_over_time.append(cold_cache.stats.hit_rate)

    # --- Warm cache (pre-populated with top-K keys by frequency) ---
    warm_cache = LRUCache(capacity=cache_size)

    # Sort keys by historical frequency, pick top cache_size
    top_keys = sorted(frequency_data.keys(),
                      key=lambda k: frequency_data[k],
                      reverse=True)[:cache_size]
    for key in top_keys:
        warm_cache.put(key, "data")

    # Reset stats after warming (warming itself isn't real traffic)
    warm_cache.stats = __import__('cache').CacheStats()

    warm_hits_over_time = []
    for i, key in enumerate(new_accesses):
        if warm_cache.get(key) is None:
            warm_cache.put(key, "data")
        if (i + 1) % 100 == 0:
            warm_hits_over_time.append(warm_cache.stats.hit_rate)

    print(f"  {num_keys} unique keys, cache size={cache_size}, {len(new_accesses)} accesses\n")
    print(f"  Hit rate over time (every 100 accesses):")
    print(f"  {'Requests':>10}  {'Cold Cache':>12}  {'Warm Cache':>12}  {'Improvement':>12}")
    print(f"  {'-'*10}  {'-'*12}  {'-'*12}  {'-'*12}")

    for i, (cold, warm) in enumerate(zip(cold_hits_over_time, warm_hits_over_time)):
        req = (i + 1) * 100
        improvement = warm - cold
        marker = " <<<" if req <= 500 else ""
        print(f"  {req:>10}  {cold:>12.2%}  {warm:>12.2%}  {improvement:>+12.2%}{marker}")
        if req >= 2000:  # Show enough to see convergence
            if i < len(cold_hits_over_time) - 1:
                continue

    print()
    print(f"  Final cold cache hit rate: {cold_cache.stats.hit_rate:.2%}")
    print(f"  Final warm cache hit rate: {warm_cache.stats.hit_rate:.2%}")
    print()
    print(f"  Key insight: warming helps most in the first few hundred requests")
    print(f"  (marked with <<<). After the cold cache 'learns' the working set,")
    print(f"  both converge to similar hit rates. Warming matters most for")
    print(f"  services that restart frequently or can't afford the cold-start penalty.")
    print()


# ===================================================================
# Main
# ===================================================================

if __name__ == "__main__":
    exercise_1_demo()
    exercise_2_demo()
    exercise_3_demo()
    exercise_4_demo()
    exercise_5_demo()
    print("All practice exercises complete.")
