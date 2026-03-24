"""
Day 66 Practice: Load Factor and Rehashing Exercises

5 exercises exploring resize strategies, amortized analysis, and advanced
techniques like prime-sized tables, consistent resize, and split-ordered lists.
"""

from __future__ import annotations
import math
import time
from typing import Any


# ===========================================================================
# Exercise 1: Amortized Cost Analysis
#
# Insert N items into an auto-resizing table for increasing N.
# Track (total work) / N — it should converge to a constant.
# "Work" = number of insert operations + number of items moved during rehashes.
# ===========================================================================

class TrackedHashTable:
    """Minimal chaining hash table that counts every unit of work."""

    GROW_THRESHOLD = 0.75
    MIN_SIZE = 8

    def __init__(self):
        self._size = self.MIN_SIZE
        self._buckets: list[list[tuple]] = [[] for _ in range(self._size)]
        self._count = 0
        self.work = 0  # total units of work

    def put(self, key, value):
        self.work += 1  # the insert itself
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._count += 1
        if self._count / self._size > self.GROW_THRESHOLD:
            self._rehash(self._size * 2)

    def _rehash(self, new_size):
        old = self._buckets
        self._size = new_size
        self._buckets = [[] for _ in range(new_size)]
        for chain in old:
            for key, value in chain:
                idx = hash(key) % self._size
                self._buckets[idx].append((key, value))
                self.work += 1  # each move is one unit of work


def exercise_1_amortized_cost():
    """
    Plot amortized cost (total_work / N) as N grows.
    Should approach a constant (~3 for doubling strategy).
    """
    print("=" * 70)
    print("Exercise 1: Amortized Cost Analysis")
    print("=" * 70)
    print(f"\n  {'N':>8}  {'Total Work':>12}  {'Work/N (amortized)':>20}")
    print(f"  {'-'*44}")

    sample_points = [100, 500, 1000, 2000, 5000, 10000, 20000, 50000]

    for target_n in sample_points:
        ht = TrackedHashTable()
        for i in range(target_n):
            ht.put(i, i)
        amortized = ht.work / target_n
        bar = "#" * int(amortized * 10)
        print(f"  {target_n:>8}  {ht.work:>12}  {amortized:>18.4f}  {bar}")

    print("\n  As N grows, amortized cost converges to ~3.0 (constant).")
    print("  This confirms O(1) amortized insert with doubling strategy.")


# ===========================================================================
# Exercise 2: Prime Table Sizes
#
# Instead of doubling to the next power of 2, find the next prime >= 2 * current.
# Prime sizes give better distribution with weaker hash functions.
# ===========================================================================

def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def _next_prime(n: int) -> int:
    """Find the smallest prime >= n."""
    if n <= 2:
        return 2
    candidate = n if n % 2 != 0 else n + 1
    while not _is_prime(candidate):
        candidate += 2
    return candidate


class PrimeSizeHashTable:
    """Hash table that uses prime-number table sizes."""

    GROW_THRESHOLD = 0.75
    SHRINK_THRESHOLD = 0.25
    MIN_SIZE = 7  # smallest prime we allow

    def __init__(self):
        self._size = self.MIN_SIZE
        self._buckets: list[list[tuple]] = [[] for _ in range(self._size)]
        self._count = 0
        self.rehash_count = 0
        self.size_history: list[int] = [self._size]

    def put(self, key, value):
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._count += 1
        if self._count / self._size > self.GROW_THRESHOLD:
            self._rehash(_next_prime(self._size * 2))

    def get(self, key, default=None):
        idx = hash(key) % self._size
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def delete(self, key) -> bool:
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx].pop(i)
                self._count -= 1
                if self._size > self.MIN_SIZE and self._count / self._size < self.SHRINK_THRESHOLD:
                    new = _next_prime(max(self._size // 2, self.MIN_SIZE))
                    if new < self._size:
                        self._rehash(new)
                return True
        return False

    def _rehash(self, new_size):
        old = self._buckets
        self._size = new_size
        self._buckets = [[] for _ in range(new_size)]
        for chain in old:
            for key, value in chain:
                self._buckets[hash(key) % self._size].append((key, value))
        self.rehash_count += 1
        self.size_history.append(new_size)

    @property
    def load_factor(self):
        return self._count / self._size

    def chain_lengths(self) -> list[int]:
        return [len(b) for b in self._buckets]


def exercise_2_prime_sizes():
    print("\n" + "=" * 70)
    print("Exercise 2: Prime Table Sizes")
    print("=" * 70)

    ht = PrimeSizeHashTable()
    for i in range(5000):
        ht.put(f"key-{i}", i)

    print(f"\n  After 5000 inserts:")
    print(f"  Table size: {ht._size} (prime)")
    print(f"  Items: {ht._count}")
    print(f"  Load factor: {ht.load_factor:.3f}")
    print(f"  Rehashes: {ht.rehash_count}")
    print(f"\n  Size progression (all primes):")
    print(f"  {' -> '.join(str(s) for s in ht.size_history)}")

    # Compare chain distribution vs power-of-2
    chains = ht.chain_lengths()
    non_empty = [c for c in chains if c > 0]
    print(f"\n  Chain length stats:")
    print(f"    Empty buckets: {chains.count(0)} / {len(chains)}")
    print(f"    Max chain: {max(chains)}")
    print(f"    Avg non-empty chain: {sum(non_empty)/len(non_empty):.2f}")

    # Verify correctness
    found = sum(1 for i in range(5000) if ht.get(f"key-{i}") == i)
    print(f"\n  Correctness: {found}/5000 items verified")


# ===========================================================================
# Exercise 3: Consistent Resize (dual-bucket lookup during migration)
#
# During incremental migration, for any key we can compute both
# hash(key) % old_size and hash(key) % new_size to determine
# which table holds it — without scanning both.
#
# Key insight: if new_size = 2 * old_size, then for a bucket b in the old table,
# all its entries will go to either bucket b or bucket b + old_size in the new
# table. This is because (hash % (2*m)) is either (hash % m) or (hash % m) + m.
# ===========================================================================

class ConsistentResizeTable:
    """
    During incremental migration, uses the mathematical relationship between
    old and new bucket indices to determine exactly where a key lives,
    without probing both tables blindly.
    """

    GROW_THRESHOLD = 0.75
    MIN_SIZE = 8

    def __init__(self, migrate_k: int = 4):
        self._size = self.MIN_SIZE
        self._buckets: list[list[tuple]] = [[] for _ in range(self._size)]
        self._count = 0
        self._migrate_k = migrate_k

        # migration state
        self._new_buckets: list[list[tuple]] | None = None
        self._new_size: int = 0
        self._migrate_idx: int = 0
        self._migrating: bool = False

        self.lookups_single = 0  # lookups that checked exactly one table
        self.lookups_total = 0

    def put(self, key, value):
        self._step_migration()
        if self._migrating:
            idx = hash(key) % self._new_size
            for i, (k, _) in enumerate(self._new_buckets[idx]):
                if k == key:
                    self._new_buckets[idx][i] = (key, value)
                    return
            # Also check if it exists in old table (un-migrated bucket)
            old_idx = hash(key) % self._size
            if old_idx >= self._migrate_idx:
                for i, (k, _) in enumerate(self._buckets[old_idx]):
                    if k == key:
                        self._buckets[old_idx][i] = (key, value)
                        return
            self._new_buckets[idx].append((key, value))
            self._count += 1
        else:
            idx = hash(key) % self._size
            for i, (k, _) in enumerate(self._buckets[idx]):
                if k == key:
                    self._buckets[idx][i] = (key, value)
                    return
            self._buckets[idx].append((key, value))
            self._count += 1
            if self._count / self._size > self.GROW_THRESHOLD:
                self._begin_migration(self._size * 2)

    def get(self, key, default=None):
        """
        Consistent lookup: during migration, we know whether a key is still
        in the old table based on whether its old-table bucket has been migrated.
        """
        self.lookups_total += 1

        if not self._migrating:
            self.lookups_single += 1
            idx = hash(key) % self._size
            for k, v in self._buckets[idx]:
                if k == key:
                    return v
            return default

        # During migration: determine which table holds this key
        old_idx = hash(key) % self._size
        if old_idx < self._migrate_idx:
            # This old bucket has already been migrated -> key is in new table
            self.lookups_single += 1
            new_idx = hash(key) % self._new_size
            for k, v in self._new_buckets[new_idx]:
                if k == key:
                    return v
            return default
        else:
            # This old bucket has NOT been migrated -> key is in old table
            # (unless it was inserted after migration started, then it is in new)
            new_idx = hash(key) % self._new_size
            for k, v in self._new_buckets[new_idx]:
                if k == key:
                    self.lookups_single += 1
                    return v
            # Not in new table, check old
            for k, v in self._buckets[old_idx]:
                if k == key:
                    return v
            return default

    def __len__(self):
        return self._count

    def _begin_migration(self, new_size):
        self._new_size = new_size
        self._new_buckets = [[] for _ in range(new_size)]
        self._migrate_idx = 0
        self._migrating = True

    def _step_migration(self):
        if not self._migrating:
            return
        done = 0
        while done < self._migrate_k and self._migrate_idx < self._size:
            for key, value in self._buckets[self._migrate_idx]:
                idx = hash(key) % self._new_size
                self._new_buckets[idx].append((key, value))
            self._buckets[self._migrate_idx] = []
            self._migrate_idx += 1
            done += 1
        if self._migrate_idx >= self._size:
            self._buckets = self._new_buckets
            self._size = self._new_size
            self._new_buckets = None
            self._new_size = 0
            self._migrating = False


def exercise_3_consistent_resize():
    print("\n" + "=" * 70)
    print("Exercise 3: Consistent Resize (smart bucket lookup)")
    print("=" * 70)

    ht = ConsistentResizeTable(migrate_k=2)

    # Insert items
    for i in range(500):
        ht.put(f"key-{i}", i)

    # Now do lookups — some will happen during migration
    for i in range(500):
        val = ht.get(f"key-{i}")
        assert val == i, f"Expected {i}, got {val}"

    # Also look up non-existent keys
    for i in range(500, 600):
        val = ht.get(f"key-{i}")
        assert val is None

    print(f"\n  Total lookups: {ht.lookups_total}")
    print(f"  Single-table lookups: {ht.lookups_single}")
    pct = ht.lookups_single / ht.lookups_total * 100 if ht.lookups_total else 0
    print(f"  Efficiency: {pct:.1f}% of lookups checked only one table")
    print(f"\n  Key insight: when new_size = 2 * old_size, bucket `b` in the old")
    print(f"  table maps to either bucket `b` or `b + old_size` in the new table.")
    print(f"  By tracking migrate_idx, we know which buckets have moved.")
    print(f"\n  Correctness: all 500 lookups returned correct values.")


# ===========================================================================
# Exercise 4: Benchmark grow-only vs grow-and-shrink
#
# Workload: insert N items, then delete N-100 items.
# Compare memory usage (bucket count) and timing.
# ===========================================================================

class GrowOnlyHashTable:
    """Hash table that grows but NEVER shrinks."""

    GROW_THRESHOLD = 0.75
    MIN_SIZE = 8

    def __init__(self):
        self._size = self.MIN_SIZE
        self._buckets: list[list[tuple]] = [[] for _ in range(self._size)]
        self._count = 0

    def put(self, key, value):
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._count += 1
        if self._count / self._size > self.GROW_THRESHOLD:
            self._rehash(self._size * 2)

    def delete(self, key) -> bool:
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx].pop(i)
                self._count -= 1
                return True
        return False

    def get(self, key, default=None):
        idx = hash(key) % self._size
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def _rehash(self, new_size):
        old = self._buckets
        self._size = new_size
        self._buckets = [[] for _ in range(new_size)]
        for chain in old:
            for key, value in chain:
                self._buckets[hash(key) % self._size].append((key, value))

    @property
    def bucket_count(self):
        return self._size

    @property
    def load_factor(self):
        return self._count / self._size if self._size else 0


class GrowShrinkHashTable:
    """Hash table that grows AND shrinks."""

    GROW_THRESHOLD = 0.75
    SHRINK_THRESHOLD = 0.25
    MIN_SIZE = 8

    def __init__(self):
        self._size = self.MIN_SIZE
        self._buckets: list[list[tuple]] = [[] for _ in range(self._size)]
        self._count = 0

    def put(self, key, value):
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._count += 1
        if self._count / self._size > self.GROW_THRESHOLD:
            self._rehash(self._size * 2)

    def delete(self, key) -> bool:
        idx = hash(key) % self._size
        for i, (k, _) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx].pop(i)
                self._count -= 1
                if self._size > self.MIN_SIZE and self._count / self._size < self.SHRINK_THRESHOLD:
                    self._rehash(max(self._size // 2, self.MIN_SIZE))
                return True
        return False

    def get(self, key, default=None):
        idx = hash(key) % self._size
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def _rehash(self, new_size):
        old = self._buckets
        self._size = new_size
        self._buckets = [[] for _ in range(new_size)]
        for chain in old:
            for key, value in chain:
                self._buckets[hash(key) % self._size].append((key, value))

    @property
    def bucket_count(self):
        return self._size

    @property
    def load_factor(self):
        return self._count / self._size if self._size else 0


def exercise_4_benchmark():
    print("\n" + "=" * 70)
    print("Exercise 4: Grow-Only vs Grow-and-Shrink Benchmark")
    print("=" * 70)

    N = 20_000
    KEEP = 100

    # Grow-only
    ht_go = GrowOnlyHashTable()
    t0 = time.perf_counter()
    for i in range(N):
        ht_go.put(i, i)
    for i in range(N - KEEP):
        ht_go.delete(i)
    t_go = time.perf_counter() - t0

    # Grow-and-shrink
    ht_gs = GrowShrinkHashTable()
    t0 = time.perf_counter()
    for i in range(N):
        ht_gs.put(i, i)
    for i in range(N - KEEP):
        ht_gs.delete(i)
    t_gs = time.perf_counter() - t0

    print(f"\n  Workload: insert {N}, delete {N - KEEP}, keep {KEEP}")
    print(f"\n  {'Metric':<30} {'Grow-Only':>12} {'Grow+Shrink':>12}")
    print(f"  {'-'*54}")
    print(f"  {'Total time (ms)':<30} {t_go*1000:>12.1f} {t_gs*1000:>12.1f}")
    print(f"  {'Final buckets':<30} {ht_go.bucket_count:>12} {ht_gs.bucket_count:>12}")
    print(f"  {'Final items':<30} {KEEP:>12} {KEEP:>12}")
    print(f"  {'Final load factor':<30} {ht_go.load_factor:>12.6f} {ht_gs.load_factor:>12.6f}")
    ratio = ht_go.bucket_count / ht_gs.bucket_count if ht_gs.bucket_count else 0
    print(f"  {'Memory ratio (GO/GS)':<30} {ratio:>12.1f}x")

    print(f"\n  Grow-only wastes {ht_go.bucket_count} buckets for {KEEP} items.")
    print(f"  Grow+shrink reclaims memory down to {ht_gs.bucket_count} buckets.")
    print(f"  Trade-off: shrinking costs CPU time during the delete phase.")


# ===========================================================================
# Exercise 5: Split-Ordered Lists
#
# A lock-free-friendly resize strategy. Instead of moving items between
# bucket arrays, all items live in a single sorted linked list. The bucket
# array is just an array of pointers into this list. Doubling the bucket
# array only requires setting new pointers — no items move.
#
# Key idea: items are ordered by bit-reverse of their hash. When the table
# doubles from m to 2m buckets, bucket b splits into b and b+m. Because
# of bit-reversal ordering, the items for b and b+m are already contiguous
# in the list — you just insert a new sentinel node to split them.
# ===========================================================================

def _bit_reverse(n: int, width: int) -> int:
    """Reverse the lowest `width` bits of n."""
    result = 0
    for _ in range(width):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result


class SplitOrderedNode:
    """Node in the split-ordered list. Sentinel nodes mark bucket boundaries."""

    __slots__ = ("key", "value", "order_key", "is_sentinel", "next")

    def __init__(self, key, value, order_key: int, is_sentinel: bool = False):
        self.key = key
        self.value = value
        self.order_key = order_key  # bit-reversed hash (sentinels use bit-reversed bucket id)
        self.is_sentinel = is_sentinel
        self.next: SplitOrderedNode | None = None


class SplitOrderedList:
    """
    Split-ordered list hash table.

    All entries live in a single linked list sorted by bit-reversed hash.
    The bucket array holds pointers into this list. Resizing only adds
    new sentinel nodes — no items are moved.

    This is a simplified single-threaded version demonstrating the concept.
    The real value is in concurrent settings where this avoids locks during resize.
    """

    GROW_THRESHOLD = 0.75
    INITIAL_BITS = 3  # start with 2^3 = 8 buckets

    def __init__(self):
        self._bits = self.INITIAL_BITS
        self._size = 1 << self._bits
        self._count = 0

        # Head of the sorted list — a sentinel for bucket 0
        self._head = SplitOrderedNode(None, None, 0, is_sentinel=True)

        # Bucket array: each entry points to the sentinel node for that bucket
        self._buckets: list[SplitOrderedNode | None] = [None] * self._size
        self._buckets[0] = self._head

        self.split_count = 0  # number of bucket splits performed

    def _order_key_for_bucket(self, bucket: int) -> int:
        """Sentinel order key: bit-reverse of bucket index (always even-like)."""
        return _bit_reverse(bucket, self._bits) << 1  # shift left to make room

    def _order_key_for_item(self, h: int) -> int:
        """Item order key: bit-reverse of (hash mod size), with low bit set."""
        bucket = h % self._size
        return (_bit_reverse(bucket, self._bits) << 1) | 1

    def _ensure_bucket(self, bucket: int) -> SplitOrderedNode:
        """Lazily initialize a bucket's sentinel if it doesn't exist."""
        if self._buckets[bucket] is not None:
            return self._buckets[bucket]

        # Find the parent bucket (bucket with one fewer bit)
        parent = bucket & ((1 << (self._bits - 1)) - 1) if bucket >= (1 << (self._bits - 1)) else bucket
        # Fallback: walk from a known bucket
        parent_node = self._buckets[0]  # always exists

        # Find the right place for the sentinel
        sentinel_key = self._order_key_for_bucket(bucket)
        sentinel = SplitOrderedNode(None, None, sentinel_key, is_sentinel=True)

        # Insert sentinel into sorted position
        prev = self._head
        curr = prev.next
        while curr is not None and curr.order_key < sentinel_key:
            prev = curr
            curr = curr.next

        sentinel.next = curr
        prev.next = sentinel
        self._buckets[bucket] = sentinel
        self.split_count += 1
        return sentinel

    def put(self, key, value) -> None:
        h = hash(key) & 0x7FFFFFFF  # positive hash
        bucket = h % self._size
        sentinel = self._ensure_bucket(bucket)

        order = self._order_key_for_item(h)

        # Search from sentinel
        prev = sentinel
        curr = prev.next
        while curr is not None and not curr.is_sentinel and curr.order_key <= order:
            if not curr.is_sentinel and curr.key == key:
                curr.value = value
                return
            prev = curr
            curr = curr.next

        # Insert new node
        node = SplitOrderedNode(key, value, order)
        node.next = curr
        prev.next = node
        self._count += 1

        # Check load and grow
        if self._count / self._size > self.GROW_THRESHOLD:
            self._grow()

    def get(self, key, default=None):
        h = hash(key) & 0x7FFFFFFF
        bucket = h % self._size
        sentinel = self._ensure_bucket(bucket)

        order = self._order_key_for_item(h)

        curr = sentinel.next
        while curr is not None and not curr.is_sentinel and curr.order_key <= order:
            if curr.key == key:
                return curr.value
            curr = curr.next
        return default

    def delete(self, key) -> bool:
        h = hash(key) & 0x7FFFFFFF
        bucket = h % self._size
        sentinel = self._ensure_bucket(bucket)

        order = self._order_key_for_item(h)

        prev = sentinel
        curr = prev.next
        while curr is not None and not curr.is_sentinel and curr.order_key <= order:
            if curr.key == key:
                prev.next = curr.next
                self._count -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def _grow(self):
        """Double the bucket array. No items move — just new sentinel slots."""
        old_size = self._size
        self._bits += 1
        self._size = 1 << self._bits
        # Extend bucket array — new slots are None (lazily initialized)
        self._buckets.extend([None] * old_size)

    def __len__(self):
        return self._count

    def __contains__(self, key):
        return self.get(key, _SENTINEL) is not _SENTINEL

    @property
    def bucket_count(self):
        return self._size

    @property
    def load_factor(self):
        return self._count / self._size if self._size else 0

    @property
    def initialized_buckets(self):
        return sum(1 for b in self._buckets if b is not None)


_SENTINEL = object()


def exercise_5_split_ordered():
    print("\n" + "=" * 70)
    print("Exercise 5: Split-Ordered Lists")
    print("=" * 70)

    ht = SplitOrderedList()

    N = 2000
    for i in range(N):
        ht.put(f"key-{i}", i)

    print(f"\n  After {N} inserts:")
    print(f"  Bucket count: {ht.bucket_count}")
    print(f"  Initialized buckets: {ht.initialized_buckets}")
    print(f"  Items: {len(ht)}")
    print(f"  Load factor: {ht.load_factor:.3f}")
    print(f"  Bucket splits: {ht.split_count}")

    # Verify correctness
    found = 0
    for i in range(N):
        if ht.get(f"key-{i}") == i:
            found += 1
    print(f"\n  Correctness: {found}/{N} items verified")

    # Delete half
    for i in range(0, N, 2):
        ht.delete(f"key-{i}")

    remaining = sum(1 for i in range(N) if f"key-{i}" in ht)
    print(f"\n  After deleting even-indexed items:")
    print(f"  Items remaining: {remaining}")
    print(f"  Bucket count (unchanged — no shrink needed): {ht.bucket_count}")

    print(f"\n  Key insight: resizing only extends the bucket pointer array.")
    print(f"  No items are moved. Sentinels are inserted lazily into the sorted")
    print(f"  list. In concurrent settings, this means readers are never blocked")
    print(f"  by a resize — they just follow list pointers as usual.")


# ===========================================================================
# Run all exercises
# ===========================================================================

if __name__ == "__main__":
    exercise_1_amortized_cost()
    exercise_2_prime_sizes()
    exercise_3_consistent_resize()
    exercise_4_benchmark()
    exercise_5_split_ordered()
