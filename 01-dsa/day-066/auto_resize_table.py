"""
Day 66: Load Factor and Rehashing — Auto-Resizing Hash Tables

Two implementations:
1. AutoResizeHashTable: standard chaining with grow (load > 0.75) and shrink (load < 0.25)
2. IncrementalResizeTable: Redis-style incremental migration between old and new tables

Both track rehash statistics to demonstrate amortized cost.
"""

from __future__ import annotations
from typing import Any


# ---------------------------------------------------------------------------
# 1. AutoResizeHashTable — immediate full rehash on threshold breach
# ---------------------------------------------------------------------------

class AutoResizeHashTable:
    """
    Chaining-based hash table that automatically grows when load > 0.75
    and shrinks when load < 0.25 (with a minimum size floor).
    """

    GROW_THRESHOLD = 0.75
    SHRINK_THRESHOLD = 0.25
    MIN_SIZE = 8  # never shrink below this

    def __init__(self, initial_size: int = 8):
        self._size = max(initial_size, self.MIN_SIZE)
        self._buckets: list[list[tuple[Any, Any]]] = [[] for _ in range(self._size)]
        self._count = 0

        # --- stats ---
        self.rehash_count = 0
        self.total_items_moved = 0
        self._total_ops = 0  # inserts + deletes
        self._rehash_log: list[dict] = []

    # --- public API ---------------------------------------------------------

    def put(self, key: Any, value: Any) -> None:
        self._total_ops += 1
        idx = hash(key) % self._size
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx][i] = (key, value)
                return
        self._buckets[idx].append((key, value))
        self._count += 1
        if self.load_factor > self.GROW_THRESHOLD:
            self._rehash(self._size * 2)

    def get(self, key: Any, default: Any = None) -> Any:
        idx = hash(key) % self._size
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return default

    def delete(self, key: Any) -> bool:
        self._total_ops += 1
        idx = hash(key) % self._size
        for i, (k, v) in enumerate(self._buckets[idx]):
            if k == key:
                self._buckets[idx].pop(i)
                self._count -= 1
                if self._size > self.MIN_SIZE and self.load_factor < self.SHRINK_THRESHOLD:
                    new_size = max(self._size // 2, self.MIN_SIZE)
                    if new_size != self._size:
                        self._rehash(new_size)
                return True
        return False

    def __contains__(self, key: Any) -> bool:
        return self.get(key, _SENTINEL) is not _SENTINEL

    def __len__(self) -> int:
        return self._count

    # --- properties ---------------------------------------------------------

    @property
    def load_factor(self) -> float:
        return self._count / self._size if self._size else 0.0

    @property
    def bucket_count(self) -> int:
        return self._size

    @property
    def amortized_cost(self) -> float:
        """Total work (ops + items moved during rehashes) / total ops."""
        if self._total_ops == 0:
            return 0.0
        return (self._total_ops + self.total_items_moved) / self._total_ops

    # --- internals ----------------------------------------------------------

    def _rehash(self, new_size: int) -> None:
        old_buckets = self._buckets
        old_size = self._size
        self._size = new_size
        self._buckets = [[] for _ in range(new_size)]
        moved = 0
        for chain in old_buckets:
            for key, value in chain:
                idx = hash(key) % self._size
                self._buckets[idx].append((key, value))
                moved += 1
        self.rehash_count += 1
        self.total_items_moved += moved
        direction = "GROW" if new_size > old_size else "SHRINK"
        self._rehash_log.append({
            "event": direction,
            "old_size": old_size,
            "new_size": new_size,
            "items_moved": moved,
            "load_after": self.load_factor,
        })


_SENTINEL = object()


# ---------------------------------------------------------------------------
# 2. IncrementalResizeTable — Redis-style gradual migration
# ---------------------------------------------------------------------------

class IncrementalResizeTable:
    """
    Chaining-based hash table with incremental (lazy) rehashing.

    During a resize, both old and new tables coexist. Each mutating
    operation migrates `migrate_k` buckets from the old table to the new one.
    This bounds worst-case per-operation latency.
    """

    GROW_THRESHOLD = 0.75
    SHRINK_THRESHOLD = 0.25
    MIN_SIZE = 8

    def __init__(self, initial_size: int = 8, migrate_k: int = 4):
        self._size = max(initial_size, self.MIN_SIZE)
        self._buckets: list[list[tuple[Any, Any]]] = [[] for _ in range(self._size)]
        self._count = 0
        self._migrate_k = migrate_k

        # migration state
        self._new_buckets: list[list[tuple[Any, Any]]] | None = None
        self._new_size: int = 0
        self._migrate_idx: int = 0  # next old-table bucket to migrate
        self._migrating: bool = False

        # --- stats ---
        self.rehash_count = 0
        self.total_items_moved = 0
        self._total_ops = 0
        self._rehash_log: list[dict] = []
        self._items_moved_this_rehash = 0

    # --- public API ---------------------------------------------------------

    def put(self, key: Any, value: Any) -> None:
        self._total_ops += 1
        self._step_migration()

        if self._migrating:
            # Insert into new table only
            idx = hash(key) % self._new_size
            for i, (k, v) in enumerate(self._new_buckets[idx]):
                if k == key:
                    self._new_buckets[idx][i] = (key, value)
                    return
            self._new_buckets[idx].append((key, value))
            self._count += 1
        else:
            idx = hash(key) % self._size
            for i, (k, v) in enumerate(self._buckets[idx]):
                if k == key:
                    self._buckets[idx][i] = (key, value)
                    return
            self._buckets[idx].append((key, value))
            self._count += 1
            # Check if we need to start a migration
            if self._count / self._size > self.GROW_THRESHOLD:
                self._begin_migration(self._size * 2)

    def get(self, key: Any, default: Any = None) -> Any:
        if self._migrating:
            # Check new table first, then old
            idx = hash(key) % self._new_size
            for k, v in self._new_buckets[idx]:
                if k == key:
                    return v
            idx = hash(key) % self._size
            for k, v in self._buckets[idx]:
                if k == key:
                    return v
            return default
        else:
            idx = hash(key) % self._size
            for k, v in self._buckets[idx]:
                if k == key:
                    return v
            return default

    def delete(self, key: Any) -> bool:
        self._total_ops += 1
        self._step_migration()

        if self._migrating:
            # Try new table first
            idx = hash(key) % self._new_size
            for i, (k, v) in enumerate(self._new_buckets[idx]):
                if k == key:
                    self._new_buckets[idx].pop(i)
                    self._count -= 1
                    return True
            # Try old table
            idx = hash(key) % self._size
            for i, (k, v) in enumerate(self._buckets[idx]):
                if k == key:
                    self._buckets[idx].pop(i)
                    self._count -= 1
                    return True
            return False
        else:
            idx = hash(key) % self._size
            for i, (k, v) in enumerate(self._buckets[idx]):
                if k == key:
                    self._buckets[idx].pop(i)
                    self._count -= 1
                    if self._size > self.MIN_SIZE and self._count / self._size < self.SHRINK_THRESHOLD:
                        new_size = max(self._size // 2, self.MIN_SIZE)
                        if new_size != self._size:
                            self._begin_migration(new_size)
                    return True
            return False

    def __contains__(self, key: Any) -> bool:
        return self.get(key, _SENTINEL) is not _SENTINEL

    def __len__(self) -> int:
        return self._count

    # --- properties ---------------------------------------------------------

    @property
    def load_factor(self) -> float:
        effective_size = self._new_size if self._migrating else self._size
        return self._count / effective_size if effective_size else 0.0

    @property
    def bucket_count(self) -> int:
        return self._new_size if self._migrating else self._size

    @property
    def is_migrating(self) -> bool:
        return self._migrating

    @property
    def migration_progress(self) -> float:
        """Fraction of old buckets migrated (0.0 to 1.0)."""
        if not self._migrating:
            return 1.0
        return self._migrate_idx / self._size

    @property
    def amortized_cost(self) -> float:
        if self._total_ops == 0:
            return 0.0
        return (self._total_ops + self.total_items_moved) / self._total_ops

    # --- internals ----------------------------------------------------------

    def _begin_migration(self, new_size: int) -> None:
        self._new_size = new_size
        self._new_buckets = [[] for _ in range(new_size)]
        self._migrate_idx = 0
        self._migrating = True
        self._items_moved_this_rehash = 0
        self.rehash_count += 1
        direction = "GROW" if new_size > self._size else "SHRINK"
        self._rehash_log.append({
            "event": direction,
            "old_size": self._size,
            "new_size": new_size,
            "items_at_start": self._count,
        })

    def _step_migration(self) -> None:
        """Migrate up to k buckets from old table to new table."""
        if not self._migrating:
            return
        buckets_done = 0
        while buckets_done < self._migrate_k and self._migrate_idx < self._size:
            chain = self._buckets[self._migrate_idx]
            for key, value in chain:
                idx = hash(key) % self._new_size
                self._new_buckets[idx].append((key, value))
                self.total_items_moved += 1
                self._items_moved_this_rehash += 1
            self._buckets[self._migrate_idx] = []  # free old chain
            self._migrate_idx += 1
            buckets_done += 1

        # Check if migration is complete
        if self._migrate_idx >= self._size:
            self._rehash_log[-1]["items_moved"] = self._items_moved_this_rehash
            self._buckets = self._new_buckets
            self._size = self._new_size
            self._new_buckets = None
            self._new_size = 0
            self._migrating = False


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_auto_resize():
    print("=" * 70)
    print("DEMO: AutoResizeHashTable — insert 10,000 items, then delete them")
    print("=" * 70)

    ht = AutoResizeHashTable()
    print(f"\nInitial: {ht.bucket_count} buckets, {len(ht)} items, "
          f"load={ht.load_factor:.3f}")

    # Insert phase
    for i in range(10_000):
        ht.put(f"key-{i}", i)

    print(f"\nAfter 10,000 inserts:")
    print(f"  Buckets: {ht.bucket_count}")
    print(f"  Items:   {len(ht)}")
    print(f"  Load:    {ht.load_factor:.3f}")
    print(f"  Rehash events (grow): {sum(1 for e in ht._rehash_log if e['event'] == 'GROW')}")
    print(f"  Total items moved:    {ht.total_items_moved}")
    print(f"  Amortized cost/op:    {ht.amortized_cost:.3f}")

    print("\n  Grow events:")
    for e in ht._rehash_log:
        if e["event"] == "GROW":
            print(f"    {e['old_size']:>6} -> {e['new_size']:>6}  "
                  f"(moved {e['items_moved']:>5}, load after: {e['load_after']:.3f})")

    # Delete phase
    for i in range(9_500):
        ht.delete(f"key-{i}")

    print(f"\nAfter deleting 9,500 items:")
    print(f"  Buckets: {ht.bucket_count}")
    print(f"  Items:   {len(ht)}")
    print(f"  Load:    {ht.load_factor:.3f}")
    print(f"  Shrink events: {sum(1 for e in ht._rehash_log if e['event'] == 'SHRINK')}")

    print("\n  Shrink events:")
    for e in ht._rehash_log:
        if e["event"] == "SHRINK":
            print(f"    {e['old_size']:>6} -> {e['new_size']:>6}  "
                  f"(moved {e['items_moved']:>5}, load after: {e['load_after']:.3f})")

    print(f"\n  Final amortized cost/op: {ht.amortized_cost:.3f}")


def demo_incremental_resize():
    print("\n" + "=" * 70)
    print("DEMO: IncrementalResizeTable — gradual migration")
    print("=" * 70)

    ht = IncrementalResizeTable(initial_size=8, migrate_k=4)

    # Insert until first migration triggers, then show progress
    print("\nInserting items and tracking migration progress:")
    migration_triggered = False
    for i in range(200):
        ht.put(f"key-{i}", i)
        if ht.is_migrating and not migration_triggered:
            print(f"\n  Migration triggered at insert #{i+1}!")
            migration_triggered = True
        if ht.is_migrating and i % 5 == 0:
            print(f"    Insert #{i+1}: migrating... "
                  f"{ht.migration_progress*100:.0f}% done, "
                  f"buckets: old={ht._size} new={ht._new_size}")
        if migration_triggered and not ht.is_migrating:
            print(f"    Insert #{i+1}: migration complete!")
            migration_triggered = False

    print(f"\nAfter 200 inserts:")
    print(f"  Buckets: {ht.bucket_count}")
    print(f"  Items:   {len(ht)}")
    print(f"  Load:    {ht.load_factor:.3f}")
    print(f"  Rehash events: {ht.rehash_count}")
    print(f"  Total items moved: {ht.total_items_moved}")
    print(f"  Amortized cost/op: {ht.amortized_cost:.3f}")

    # Now insert many more items to show multiple migrations
    print("\nInserting 10,000 more items...")
    for i in range(200, 10_200):
        ht.put(f"key-{i}", i)

    print(f"  Buckets: {ht.bucket_count}")
    print(f"  Items:   {len(ht)}")
    print(f"  Load:    {ht.load_factor:.3f}")
    print(f"  Rehash events: {ht.rehash_count}")
    print(f"  Total items moved: {ht.total_items_moved}")
    print(f"  Amortized cost/op: {ht.amortized_cost:.3f}")

    # Verify all items are retrievable
    found = sum(1 for i in range(10_200) if f"key-{i}" in ht)
    print(f"\n  Correctness check: {found}/10200 items found")


def demo_comparison():
    print("\n" + "=" * 70)
    print("COMPARISON: Full rehash vs. Incremental rehash")
    print("=" * 70)

    import time

    N = 50_000

    # Full rehash
    ht_full = AutoResizeHashTable()
    t0 = time.perf_counter()
    for i in range(N):
        ht_full.put(f"k{i}", i)
    t_full = time.perf_counter() - t0

    # Incremental rehash
    ht_inc = IncrementalResizeTable(migrate_k=8)
    t0 = time.perf_counter()
    for i in range(N):
        ht_inc.put(f"k{i}", i)
    t_inc = time.perf_counter() - t0

    print(f"\n  {'Metric':<30} {'Full':>12} {'Incremental':>12}")
    print(f"  {'-'*54}")
    print(f"  {'Total time (ms)':<30} {t_full*1000:>12.1f} {t_inc*1000:>12.1f}")
    print(f"  {'Rehash events':<30} {ht_full.rehash_count:>12} {ht_inc.rehash_count:>12}")
    print(f"  {'Items moved':<30} {ht_full.total_items_moved:>12} {ht_inc.total_items_moved:>12}")
    print(f"  {'Amortized cost/op':<30} {ht_full.amortized_cost:>12.3f} {ht_inc.amortized_cost:>12.3f}")
    print(f"  {'Final buckets':<30} {ht_full.bucket_count:>12} {ht_inc.bucket_count:>12}")


if __name__ == "__main__":
    demo_auto_resize()
    demo_incremental_resize()
    demo_comparison()
