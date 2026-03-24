"""
Day 70: In-Memory Cache Mini-Project
=====================================
Week 10 capstone — LRU cache, TTL cache, sharded cache, all from scratch.

Core insight: a cache is a hash table with a size limit and an eviction policy.
LRU uses hash map + doubly linked list for O(1) everything.
"""

import time
import threading


# ---------------------------------------------------------------------------
# Building block: doubly linked list node
# ---------------------------------------------------------------------------

class _Node:
    """Doubly linked list node holding a key-value pair.

    Why store the key in the node? When we evict the tail, we need the key
    to delete the corresponding hash map entry. Without it we'd need an
    O(n) reverse lookup.
    """
    __slots__ = ('key', 'value', 'prev', 'next', 'expire_at', 'freq')

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None
        self.expire_at = None  # Used by TTLCache
        self.freq = 0          # Used by LFU in practice.py


class _DoublyLinkedList:
    """Doubly linked list with sentinel head/tail for clean edge cases.

    Sentinels eliminate all the 'if head is None' / 'if tail is None'
    branches. Every real node is always between head and tail.
    """

    def __init__(self):
        self.head = _Node()  # sentinel
        self.tail = _Node()  # sentinel
        self.head.next = self.tail
        self.tail.prev = self.head
        self._size = 0

    def __len__(self):
        return self._size

    def add_to_front(self, node: _Node) -> None:
        """Insert node right after head sentinel (most recently used position)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self._size += 1

    def remove(self, node: _Node) -> None:
        """Remove a node from anywhere in the list in O(1).

        This is why we need a DOUBLY linked list: removing a node requires
        updating both its predecessor and successor, which means we need
        the prev pointer.
        """
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1

    def remove_last(self) -> _Node:
        """Remove and return the tail node (least recently used)."""
        if self._size == 0:
            return None
        node = self.tail.prev
        self.remove(node)
        return node

    def move_to_front(self, node: _Node) -> None:
        """Move existing node to front (mark as most recently used)."""
        self.remove(node)
        self.add_to_front(node)

    def items(self):
        """Iterate from MRU to LRU. For debugging/display."""
        current = self.head.next
        while current is not self.tail:
            yield current
            current = current.next


# ---------------------------------------------------------------------------
# CacheStats: tracking hits, misses, evictions
# ---------------------------------------------------------------------------

class CacheStats:
    """Tracks cache performance metrics.

    Why track these? Without metrics you're flying blind. Hit rate tells you
    if your cache is the right size. Eviction count tells you if your working
    set exceeds capacity. Miss rate * recomputation cost = wasted work.
    """

    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0

    @property
    def total_requests(self):
        return self.hits + self.misses

    @property
    def hit_rate(self):
        total = self.total_requests
        return self.hits / total if total > 0 else 0.0

    def record_hit(self):
        self.hits += 1

    def record_miss(self):
        self.misses += 1

    def record_eviction(self):
        self.evictions += 1

    def record_expiration(self):
        self.expirations += 1

    def __repr__(self):
        return (
            f"CacheStats(hits={self.hits}, misses={self.misses}, "
            f"evictions={self.evictions}, expirations={self.expirations}, "
            f"hit_rate={self.hit_rate:.2%})"
        )


# ---------------------------------------------------------------------------
# LRUCache
# ---------------------------------------------------------------------------

class LRUCache:
    """Least Recently Used cache — hash map + doubly linked list.

    Every operation is O(1):
    - get:  hash lookup + move-to-front
    - put:  hash lookup + insert-at-front (+ evict-tail if over capacity)

    The doubly linked list maintains access order. The hash map gives O(1)
    key-to-node lookup. Together they give us O(1) for everything LRU needs.
    """

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self._map = {}                # key -> _Node
        self._list = _DoublyLinkedList()
        self.stats = CacheStats()

    def get(self, key):
        """Return value for key, or None if not present."""
        node = self._map.get(key)
        if node is None:
            self.stats.record_miss()
            return None
        # Move to front: this key was just accessed, so it's now MRU
        self._list.move_to_front(node)
        self.stats.record_hit()
        return node.value

    def put(self, key, value) -> None:
        """Insert or update key-value pair. Evicts LRU if over capacity."""
        node = self._map.get(key)
        if node is not None:
            # Update existing: change value, mark as recently used
            node.value = value
            self._list.move_to_front(node)
            return

        # New key: check if we need to evict
        if len(self._list) >= self.capacity:
            self._evict()

        new_node = _Node(key, value)
        self._map[key] = new_node
        self._list.add_to_front(new_node)

    def _evict(self) -> None:
        """Remove least recently used entry (tail of list)."""
        victim = self._list.remove_last()
        if victim:
            del self._map[victim.key]
            self.stats.record_eviction()

    def __len__(self):
        return len(self._list)

    def __contains__(self, key):
        return key in self._map

    def peek_order(self):
        """Return keys from MRU to LRU without changing order. For debugging."""
        return [node.key for node in self._list.items()]

    def __repr__(self):
        order = self.peek_order()
        return f"LRUCache(capacity={self.capacity}, items={order}, {self.stats})"


# ---------------------------------------------------------------------------
# TTLCache: LRU + per-key expiration
# ---------------------------------------------------------------------------

class TTLCache:
    """LRU cache with per-key time-to-live.

    Uses lazy expiration: expired keys are detected and removed on access.
    Also provides cleanup() for active expiration (background sweep).

    Why both? Lazy is cheap (no extra threads) but dead keys waste memory.
    Active frees memory proactively but costs CPU. Real systems use both.
    """

    def __init__(self, capacity: int, default_ttl: float = 60.0):
        self.capacity = capacity
        self.default_ttl = default_ttl
        self._map = {}
        self._list = _DoublyLinkedList()
        self.stats = CacheStats()

    def get(self, key):
        """Return value if present and not expired. Lazy expiration."""
        node = self._map.get(key)
        if node is None:
            self.stats.record_miss()
            return None

        # Lazy expiration: check TTL on every access
        if node.expire_at is not None and time.monotonic() > node.expire_at:
            self._remove_node(node)
            self.stats.record_miss()
            self.stats.record_expiration()
            return None

        self._list.move_to_front(node)
        self.stats.record_hit()
        return node.value

    def put(self, key, value, ttl: float = None) -> None:
        """Insert with optional per-key TTL (defaults to cache-level TTL)."""
        ttl = ttl if ttl is not None else self.default_ttl
        expire_at = time.monotonic() + ttl if ttl > 0 else None

        node = self._map.get(key)
        if node is not None:
            node.value = value
            node.expire_at = expire_at
            self._list.move_to_front(node)
            return

        if len(self._list) >= self.capacity:
            self._evict()

        new_node = _Node(key, value)
        new_node.expire_at = expire_at
        self._map[key] = new_node
        self._list.add_to_front(new_node)

    def _remove_node(self, node: _Node) -> None:
        self._list.remove(node)
        del self._map[node.key]

    def _evict(self) -> None:
        victim = self._list.remove_last()
        if victim:
            del self._map[victim.key]
            self.stats.record_eviction()

    def cleanup(self) -> int:
        """Active expiration: sweep all keys, remove expired ones.

        Returns count of expired keys removed. In production you'd run this
        periodically in a background thread, or sample randomly like Redis
        (check 20 random keys, if >25% expired, repeat).
        """
        now = time.monotonic()
        expired = []
        for node in self._list.items():
            if node.expire_at is not None and now > node.expire_at:
                expired.append(node)

        for node in expired:
            self._remove_node(node)
            self.stats.record_expiration()

        return len(expired)

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        return f"TTLCache(capacity={self.capacity}, size={len(self)}, {self.stats})"


# ---------------------------------------------------------------------------
# ShardedCache: distribute keys across N LRU shards
# ---------------------------------------------------------------------------

class ShardedCache:
    """Cache sharded across N independent LRU caches.

    Why shard? A single cache under concurrent access needs a global lock.
    With N shards, N threads can operate on different shards simultaneously.

    Shard selection: hash(key) % num_shards. We use Python's built-in hash
    which is deterministic within a process (sufficient for an in-memory cache).
    """

    def __init__(self, num_shards: int, capacity_per_shard: int):
        if num_shards <= 0:
            raise ValueError("num_shards must be positive")
        self.num_shards = num_shards
        self.shards = [LRUCache(capacity_per_shard) for _ in range(num_shards)]
        # One lock per shard for thread safety
        self._locks = [threading.Lock() for _ in range(num_shards)]

    def _get_shard(self, key) -> int:
        return hash(key) % self.num_shards

    def get(self, key):
        idx = self._get_shard(key)
        with self._locks[idx]:
            return self.shards[idx].get(key)

    def put(self, key, value) -> None:
        idx = self._get_shard(key)
        with self._locks[idx]:
            self.shards[idx].put(key, value)

    def aggregate_stats(self) -> CacheStats:
        """Combine stats across all shards."""
        total = CacheStats()
        for shard in self.shards:
            total.hits += shard.stats.hits
            total.misses += shard.stats.misses
            total.evictions += shard.stats.evictions
        return total

    def shard_distribution(self) -> dict:
        """Show how many items each shard holds."""
        return {i: len(shard) for i, shard in enumerate(self.shards)}

    def __len__(self):
        return sum(len(s) for s in self.shards)

    def __repr__(self):
        return (
            f"ShardedCache(shards={self.num_shards}, "
            f"total_items={len(self)}, {self.aggregate_stats()})"
        )


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_lru():
    print("=" * 60)
    print("DEMO 1: LRU Cache — Eviction Order")
    print("=" * 60)

    cache = LRUCache(capacity=3)

    # Fill to capacity
    cache.put("A", 1)
    cache.put("B", 2)
    cache.put("C", 3)
    print(f"After inserting A, B, C:  order = {cache.peek_order()}")
    print(f"  (C is MRU, A is LRU)")

    # Access A -> moves to front
    cache.get("A")
    print(f"After get(A):            order = {cache.peek_order()}")
    print(f"  (A moved to MRU, B is now LRU)")

    # Insert D -> evicts B (the LRU)
    cache.put("D", 4)
    print(f"After put(D):            order = {cache.peek_order()}")
    print(f"  B was evicted (it was LRU)")
    print(f"  'B' in cache? {'B' in cache}")

    # Insert E -> evicts C
    cache.put("E", 5)
    print(f"After put(E):            order = {cache.peek_order()}")
    print(f"  C was evicted")

    print(f"\n  Stats: {cache.stats}")
    print()


def demo_ttl():
    print("=" * 60)
    print("DEMO 2: TTL Cache — Expiration")
    print("=" * 60)

    cache = TTLCache(capacity=10, default_ttl=0.3)  # 300ms TTL

    cache.put("fast", "I expire in 100ms", ttl=0.1)
    cache.put("normal", "I expire in 300ms")
    cache.put("forever", "I never expire", ttl=0)  # ttl=0 means no expiry

    print(f"Immediately after insert:")
    print(f"  get('fast')    = {cache.get('fast')}")
    print(f"  get('normal')  = {cache.get('normal')}")
    print(f"  get('forever') = {cache.get('forever')}")

    # Wait for fast key to expire
    time.sleep(0.15)
    print(f"\nAfter 150ms (fast should be expired):")
    print(f"  get('fast')    = {cache.get('fast')}  <- expired (lazy removal)")
    print(f"  get('normal')  = {cache.get('normal')}")

    # Wait for normal key to expire
    time.sleep(0.2)
    print(f"\nAfter 350ms total (normal should be expired):")
    print(f"  get('normal')  = {cache.get('normal')}  <- expired")
    print(f"  get('forever') = {cache.get('forever')}  <- still alive (no TTL)")

    # Demonstrate active cleanup
    cache.put("expire1", "val", ttl=0.05)
    cache.put("expire2", "val", ttl=0.05)
    cache.put("expire3", "val", ttl=0.05)
    time.sleep(0.1)
    removed = cache.cleanup()
    print(f"\nActive cleanup removed {removed} expired keys")

    print(f"\n  Stats: {cache.stats}")
    print()


def demo_sharded():
    print("=" * 60)
    print("DEMO 3: Sharded Cache — Key Distribution")
    print("=" * 60)

    cache = ShardedCache(num_shards=4, capacity_per_shard=5)

    # Insert 20 keys, see how they distribute
    for i in range(20):
        cache.put(f"key_{i}", f"value_{i}")

    print(f"Inserted 20 keys across 4 shards (capacity 5 each):")
    dist = cache.shard_distribution()
    for shard_id, count in dist.items():
        bar = "#" * count
        print(f"  Shard {shard_id}: {count:2d} items  {bar}")

    print(f"\n  Total items: {len(cache)} (max possible: 20)")
    print(f"  Note: some keys were evicted if a shard got more than 5")

    # Verify lookups work
    hits = sum(1 for i in range(20) if cache.get(f"key_{i}") is not None)
    print(f"  Keys still retrievable: {hits}/20")

    print(f"\n  {cache.aggregate_stats()}")
    print()


def demo_hit_rate():
    print("=" * 60)
    print("DEMO 4: Hit Rate Analysis — Cache Size vs. Hit Rate")
    print("=" * 60)

    # Simulate a workload with Zipf-like distribution:
    # a few keys are accessed very frequently, most are rare
    import random
    random.seed(42)

    # Generate 10000 accesses with Zipfian-like pattern
    # Key 0 is most popular, key 99 least popular
    num_keys = 100
    num_accesses = 10000
    accesses = []
    for _ in range(num_accesses):
        # Zipf-like: probability proportional to 1/rank
        rank = int(random.paretovariate(1.0)) % num_keys
        accesses.append(f"key_{rank}")

    # Test different cache sizes
    print(f"Workload: {num_accesses} accesses, {num_keys} unique keys, Zipf-like distribution\n")
    print(f"  {'Cache Size':>12}  {'Hit Rate':>10}  {'Evictions':>10}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*10}")

    for size in [5, 10, 20, 50, 75, 100]:
        cache = LRUCache(capacity=size)
        for key in accesses:
            val = cache.get(key)
            if val is None:
                cache.put(key, "data")

        print(f"  {size:>12}  {cache.stats.hit_rate:>10.2%}  {cache.stats.evictions:>10}")

    print()
    print("  Key insight: a small cache captures most of the value because")
    print("  access patterns follow power laws. Doubling cache size gives")
    print("  diminishing returns after the working set is covered.")
    print()


if __name__ == "__main__":
    demo_lru()
    demo_ttl()
    demo_sharded()
    demo_hit_rate()
    print("All cache demos complete.")
