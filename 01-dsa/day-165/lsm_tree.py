"""
Day 165: LSM Tree — Simplified Memtable + SSTable + Compaction

In-memory simulation of an LSM-tree storage engine.
  - Memtable: sorted dict, capped capacity.
  - SSTable: immutable sorted list, with min/max key index for skip.
  - Flush: when memtable hits capacity, push to L0.
  - Compaction: merge L0 -> L1 when L0 has too many SSTables.
  - Tombstones for deletes.

Production refs: LevelDB, RocksDB, Cassandra, ScyllaDB, HBase.
"""

from collections import OrderedDict


TOMBSTONE = object()  # marker for "deleted"


# ---------------------------------------------------------------------------
# SSTable — immutable sorted run
# ---------------------------------------------------------------------------

class SSTable:
    """Immutable sorted list of (key, value-or-tombstone). Indexed by min/max."""

    _counter = 0

    def __init__(self, entries):
        SSTable._counter += 1
        self.id = SSTable._counter
        # entries assumed already sorted by caller; keep as list of tuples
        self.entries = list(entries)
        self.min_key = self.entries[0][0] if self.entries else None
        self.max_key = self.entries[-1][0] if self.entries else None

    def get(self, key):
        """Binary search. Returns value, TOMBSTONE, or None."""
        if self.min_key is None or key < self.min_key or key > self.max_key:
            return None
        lo, hi = 0, len(self.entries) - 1
        while lo <= hi:
            mid = (lo + hi) // 2
            k, v = self.entries[mid]
            if k == key:
                return v
            if k < key:
                lo = mid + 1
            else:
                hi = mid - 1
        return None

    def __len__(self):
        return len(self.entries)


# ---------------------------------------------------------------------------
# LSM Tree
# ---------------------------------------------------------------------------

class LSMTree:
    def __init__(self, memtable_capacity: int = 4, l0_compaction_trigger: int = 4):
        self.memtable_capacity = memtable_capacity
        self.l0_trigger = l0_compaction_trigger
        # Memtable: OrderedDict to keep insertion semantics; sort on flush.
        self.memtable: "OrderedDict[str, object]" = OrderedDict()
        # Each level is a list of SSTables, newest first within L0,
        # for L1+ they are non-overlapping by key.
        self.levels: list[list[SSTable]] = [[]]   # start with L0
        # Stats for observability
        self.stats = {"writes": 0, "flushes": 0, "compactions": 0}

    # -------------------- Public API --------------------

    def put(self, key, value) -> None:
        self.memtable[key] = value
        self.stats["writes"] += 1
        if len(self.memtable) >= self.memtable_capacity:
            self._flush_memtable()

    def delete(self, key) -> None:
        self.put(key, TOMBSTONE)

    def get(self, key):
        # 1. Memtable
        if key in self.memtable:
            v = self.memtable[key]
            return None if v is TOMBSTONE else v
        # 2. Each level (L0 newest-first, L1+ deterministic)
        for level in self.levels:
            # L0 may overlap; check newest -> oldest
            for sst in reversed(level):
                v = sst.get(key)
                if v is None:
                    continue
                return None if v is TOMBSTONE else v
        return None

    # -------------------- Internals --------------------

    def _flush_memtable(self) -> None:
        if not self.memtable:
            return
        entries = sorted(self.memtable.items(), key=lambda kv: kv[0])
        sst = SSTable(entries)
        self.levels[0].append(sst)
        self.memtable.clear()
        self.stats["flushes"] += 1
        if len(self.levels[0]) >= self.l0_trigger:
            self._compact_l0_to_l1()

    def _compact_l0_to_l1(self) -> None:
        """K-way merge of all L0 SSTables (plus L1 if present) into a new L1.
        Newest write wins on duplicate keys. Tombstones are dropped only at
        the bottom level; here we keep them in case lower levels still exist."""
        # All sources: L0 oldest-first (so newer values overwrite), then L1
        sources = list(self.levels[0])   # already oldest-first append order
        if len(self.levels) > 1:
            sources.extend(self.levels[1])

        merged: dict = {}
        for sst in sources:
            for k, v in sst.entries:
                merged[k] = v   # later writes overwrite earlier

        # Drop tombstones (single-level demo; in real LSM, only when last lvl)
        cleaned = [(k, v) for k, v in sorted(merged.items()) if v is not TOMBSTONE]
        new_l1 = SSTable(cleaned) if cleaned else None

        self.levels[0] = []
        if len(self.levels) < 2:
            self.levels.append([])
        self.levels[1] = [new_l1] if new_l1 else []
        self.stats["compactions"] += 1

    # -------------------- Inspection --------------------

    def describe(self) -> str:
        out = [f"memtable={len(self.memtable)} entries"]
        for i, lvl in enumerate(self.levels):
            counts = [len(s) for s in lvl]
            out.append(f"L{i}: {len(lvl)} SSTables, sizes={counts}")
        out.append(f"stats={self.stats}")
        return " | ".join(out)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Put / Get / Delete")
    print("=" * 60)
    lsm = LSMTree(memtable_capacity=4, l0_compaction_trigger=3)
    for k, v in [("a", 1), ("b", 2), ("c", 3), ("d", 4)]:
        lsm.put(k, v)
    print(f"  after first batch: {lsm.describe()}")
    print(f"  get('a') = {lsm.get('a')}")
    print(f"  get('zz') = {lsm.get('zz')}")
    lsm.delete("a")
    print(f"  delete('a'); get('a') = {lsm.get('a')}")


def demo_flush_and_compact():
    print("\n" + "=" * 60)
    print("DEMO 2: Flush and compaction")
    print("=" * 60)
    lsm = LSMTree(memtable_capacity=3, l0_compaction_trigger=3)
    # Insert 12 keys to trigger multiple flushes + a compaction.
    for i in range(12):
        lsm.put(f"k{i:02d}", i)
    print(f"  {lsm.describe()}")
    # All keys still readable
    miss = [i for i in range(12) if lsm.get(f"k{i:02d}") != i]
    print(f"  missing keys after compaction: {miss}")


def demo_overwrite_wins():
    print("\n" + "=" * 60)
    print("DEMO 3: Newest write wins after compaction")
    print("=" * 60)
    lsm = LSMTree(memtable_capacity=2, l0_compaction_trigger=3)
    for i in range(5):
        lsm.put("hot", i)            # rewrite same key 5 times
        lsm.put(f"cold{i}", i)
    print(f"  get('hot') = {lsm.get('hot')} (expected 4)")
    print(f"  {lsm.describe()}")


def demo_tombstone_drops():
    print("\n" + "=" * 60)
    print("DEMO 4: Tombstones drop on compaction")
    print("=" * 60)
    lsm = LSMTree(memtable_capacity=2, l0_compaction_trigger=2)
    lsm.put("x", 1)
    lsm.put("y", 2)         # triggers flush
    lsm.put("z", 3)
    lsm.delete("x")         # triggers flush (tombstone on disk)
    lsm.put("w", 0)         # may trigger compaction
    lsm.put("v", -1)
    print(f"  get('x') = {lsm.get('x')}  (expected None)")
    print(f"  get('y') = {lsm.get('y')}  (expected 2)")
    print(f"  {lsm.describe()}")


def demo_write_amplification():
    print("\n" + "=" * 60)
    print("DEMO 5: Compaction rewrites = write amplification")
    print("=" * 60)
    lsm = LSMTree(memtable_capacity=8, l0_compaction_trigger=4)
    n = 200
    for i in range(n):
        lsm.put(f"k{i:04d}", i)
    print(f"  user writes={lsm.stats['writes']}, "
          f"flushes={lsm.stats['flushes']}, "
          f"compactions={lsm.stats['compactions']}")
    total_rows = sum(len(s) for lvl in lsm.levels for s in lvl)
    print(f"  rows currently on disk: {total_rows}")


if __name__ == "__main__":
    demo_basic()
    demo_flush_and_compact()
    demo_overwrite_wins()
    demo_tombstone_drops()
    demo_write_amplification()
