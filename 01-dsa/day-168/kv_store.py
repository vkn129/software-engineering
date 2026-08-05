"""
Day 168: Mini-Project — Durable Key-Value Store

Pulls together:
  - WAL (day 166) for write durability
  - Memtable + SSTable + compaction (day 165) for sorted storage
  - Crash recovery: WAL replay on open

Single-writer, single-threaded. JSON serialization for clarity.
Production refs: LevelDB, RocksDB, Cassandra.

File layout under <db_dir>/:
  wal.log
  sstables/sst-<generation>.json
"""

import os
import json
import shutil
import tempfile


TOMBSTONE = "__TOMB__"


# ---------------------------------------------------------------------------
# WAL — minimal (re-used from day 166 with small tweaks)
# ---------------------------------------------------------------------------

class WAL:
    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            open(path, "wb").close()
        self._fh = open(path, "ab")

    def append(self, rec: dict) -> None:
        line = (json.dumps(rec) + "\n").encode()
        self._fh.write(line)

    def fsync(self) -> None:
        self._fh.flush()
        os.fsync(self._fh.fileno())

    def iter_records(self):
        with open(self.path, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue   # torn tail

    def truncate(self) -> None:
        """Wipe the WAL (after a successful flush)."""
        self._fh.close()
        open(self.path, "wb").close()
        self._fh = open(self.path, "ab")

    def close(self) -> None:
        try:
            self._fh.close()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# SSTable on disk — JSON sorted list with min/max in same file
# ---------------------------------------------------------------------------

class SSTable:
    def __init__(self, path: str):
        self.path = path
        with open(path, "rb") as f:
            payload = json.loads(f.read())
        self.entries = payload["entries"]   # list of [k, v]
        self.min_key = payload["min_key"]
        self.max_key = payload["max_key"]

    @staticmethod
    def write_atomic(path: str, entries: list) -> None:
        """temp-then-rename so we never expose a half-written file."""
        payload = {
            "min_key": entries[0][0] if entries else None,
            "max_key": entries[-1][0] if entries else None,
            "entries": entries,
        }
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(json.dumps(payload).encode())
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)   # atomic on POSIX

    def get(self, key):
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


# ---------------------------------------------------------------------------
# Durable KV store
# ---------------------------------------------------------------------------

class KVStore:
    def __init__(self, db_dir: str,
                 memtable_capacity: int = 8,
                 l0_compaction_trigger: int = 3):
        self.db_dir = db_dir
        self.sst_dir = os.path.join(db_dir, "sstables")
        os.makedirs(self.sst_dir, exist_ok=True)
        self.wal_path = os.path.join(db_dir, "wal.log")
        self.memtable_capacity = memtable_capacity
        self.l0_compaction_trigger = l0_compaction_trigger

        self.memtable: dict = {}
        self.sstables: list[SSTable] = []   # oldest first
        self._next_gen = 0

        self._load_sstables()
        self.wal = WAL(self.wal_path)
        self._replay_wal()

    # ---------- recovery ----------

    def _load_sstables(self) -> None:
        names = sorted(os.listdir(self.sst_dir))
        for n in names:
            if not n.startswith("sst-") or not n.endswith(".json"):
                continue
            full = os.path.join(self.sst_dir, n)
            self.sstables.append(SSTable(full))
            try:
                gen = int(n[4:-5])
                self._next_gen = max(self._next_gen, gen + 1)
            except ValueError:
                pass

    def _replay_wal(self) -> None:
        for rec in self.wal.iter_records():
            if rec.get("type") == "put":
                self.memtable[rec["k"]] = rec["v"]
            elif rec.get("type") == "del":
                self.memtable[rec["k"]] = TOMBSTONE

    # ---------- public API ----------

    def put(self, k, v) -> None:
        self.wal.append({"type": "put", "k": k, "v": v})
        self.wal.fsync()
        self.memtable[k] = v
        if len(self.memtable) >= self.memtable_capacity:
            self._flush()

    def delete(self, k) -> None:
        self.wal.append({"type": "del", "k": k})
        self.wal.fsync()
        self.memtable[k] = TOMBSTONE
        if len(self.memtable) >= self.memtable_capacity:
            self._flush()

    def get(self, k):
        if k in self.memtable:
            v = self.memtable[k]
            return None if v == TOMBSTONE else v
        # newest SSTable first
        for sst in reversed(self.sstables):
            v = sst.get(k)
            if v is not None:
                return None if v == TOMBSTONE else v
        return None

    def close(self) -> None:
        self.wal.close()

    # ---------- internals ----------

    def _flush(self) -> None:
        if not self.memtable:
            return
        entries = sorted(self.memtable.items(), key=lambda kv: kv[0])
        gen = self._next_gen
        self._next_gen += 1
        path = os.path.join(self.sst_dir, f"sst-{gen:08d}.json")
        SSTable.write_atomic(path, entries)
        self.sstables.append(SSTable(path))
        # Safe to drop the WAL now — everything is on disk.
        self.wal.truncate()
        self.memtable.clear()
        if len(self.sstables) >= self.l0_compaction_trigger:
            self._compact()

    def _compact(self) -> None:
        """Merge all current SSTables into one, atomic-rename, delete olds."""
        merged: dict = {}
        for sst in self.sstables:
            for k, v in sst.entries:
                merged[k] = v   # later overwrites earlier
        # drop tombstones at the bottom level
        cleaned = [(k, v) for k, v in sorted(merged.items()) if v != TOMBSTONE]
        gen = self._next_gen
        self._next_gen += 1
        new_path = os.path.join(self.sst_dir, f"sst-{gen:08d}.json")
        SSTable.write_atomic(new_path, cleaned)
        new_sst = SSTable(new_path)
        # remove old files only after the new one is durable
        old_paths = [sst.path for sst in self.sstables]
        self.sstables = [new_sst]
        for p in old_paths:
            try:
                os.remove(p)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Demos — includes the simulated-crash test
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic put / get / delete")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        kv = KVStore(d, memtable_capacity=4, l0_compaction_trigger=3)
        for k, v in [("a", 1), ("b", 2), ("c", 3)]:
            kv.put(k, v)
        kv.delete("b")
        print(f"  a={kv.get('a')} b={kv.get('b')} c={kv.get('c')} z={kv.get('z')}")
        kv.close()


def demo_crash_before_flush():
    print("\n" + "=" * 60)
    print("DEMO 2: Crash before memtable flush — recover from WAL")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        kv = KVStore(d, memtable_capacity=100, l0_compaction_trigger=3)
        for i in range(5):
            kv.put(f"k{i}", i * 10)
        # Simulate crash: just close (no flush since memtable not full)
        kv.close()
        sst_files_before = os.listdir(os.path.join(d, "sstables"))

        kv2 = KVStore(d, memtable_capacity=100, l0_compaction_trigger=3)
        for i in range(5):
            v = kv2.get(f"k{i}")
            assert v == i * 10, f"k{i} lost!"
        print(f"  recovered all 5 keys after crash")
        print(f"  sstables on disk: {sst_files_before}  (none — only WAL)")
        kv2.close()


def demo_crash_after_flush():
    print("\n" + "=" * 60)
    print("DEMO 3: Crash after flush + delete + more writes")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        kv = KVStore(d, memtable_capacity=3, l0_compaction_trigger=10)
        # First batch triggers a flush
        for i in range(3):
            kv.put(f"k{i}", i)
        # Now SSTable on disk. Add more keys + a delete in memtable.
        kv.put("k99", 99)
        kv.delete("k1")
        kv.close()
        print(f"  state pre-crash: SSTable on disk + WAL with new ops")

        kv2 = KVStore(d, memtable_capacity=3, l0_compaction_trigger=10)
        print(f"  k0 = {kv2.get('k0')}   (from SSTable)")
        print(f"  k1 = {kv2.get('k1')}   (deleted -- WAL tombstone)")
        print(f"  k2 = {kv2.get('k2')}   (from SSTable)")
        print(f"  k99 = {kv2.get('k99')} (from WAL replay)")
        assert kv2.get('k0') == 0
        assert kv2.get('k1') is None
        assert kv2.get('k99') == 99
        kv2.close()


def demo_compaction_survives_crash():
    print("\n" + "=" * 60)
    print("DEMO 4: Compaction is atomic — survives crash mid-compact")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        kv = KVStore(d, memtable_capacity=2, l0_compaction_trigger=4)
        for i in range(20):
            kv.put(f"k{i:03d}", i)
        kv.close()

        # Simulate the worst-case partial state: an .tmp lying around.
        sst_dir = os.path.join(d, "sstables")
        with open(os.path.join(sst_dir, "sst-99999999.json.tmp"), "wb") as f:
            f.write(b'{"corrupt": true')  # malformed

        # Reopen — must ignore the .tmp and load real SSTables.
        kv2 = KVStore(d, memtable_capacity=2, l0_compaction_trigger=4)
        ok = all(kv2.get(f"k{i:03d}") == i for i in range(20))
        print(f"  all 20 keys recoverable: {ok}")
        kv2.close()


def demo_torn_wal_tail():
    print("\n" + "=" * 60)
    print("DEMO 5: Torn WAL tail does not corrupt recovery")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        kv = KVStore(d, memtable_capacity=10, l0_compaction_trigger=3)
        kv.put("safe1", 1)
        kv.put("safe2", 2)
        kv.close()
        # Append a torn record
        with open(os.path.join(d, "wal.log"), "ab") as f:
            f.write(b'{"type":"put","k":"corrupt","v":')

        kv2 = KVStore(d, memtable_capacity=10, l0_compaction_trigger=3)
        print(f"  safe1 = {kv2.get('safe1')}")
        print(f"  safe2 = {kv2.get('safe2')}")
        print(f"  corrupt = {kv2.get('corrupt')}  (expected None)")
        kv2.close()


if __name__ == "__main__":
    demo_basic()
    demo_crash_before_flush()
    demo_crash_after_flush()
    demo_compaction_survives_crash()
    demo_torn_wal_tail()
