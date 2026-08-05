"""
Day 166: Write-Ahead Log

Append-only log with checkpointing and crash-replay recovery.

Demo simulates:
  - A KV store that survives crashes by replaying the WAL.
  - Checkpointing to bound replay cost.
  - Recovery rebuilds in-memory state from the log.

Production refs: Postgres pg_wal, InnoDB redo log, SQLite WAL,
Cassandra commitlog, Kafka partition log.
"""

import os
import json
import tempfile


# ---------------------------------------------------------------------------
# WAL — append-only newline-delimited JSON
# ---------------------------------------------------------------------------

class WAL:
    """
    Each line is one record. fsync after every commit-style flush.
    Records: {"lsn": int, "type": "put"|"del"|"checkpoint", ...}
    """

    def __init__(self, path: str):
        self.path = path
        # ensure file exists
        if not os.path.exists(path):
            open(path, "wb").close()
        self.next_lsn = self._scan_max_lsn() + 1
        self._file = open(path, "ab")

    def _scan_max_lsn(self) -> int:
        max_lsn = 0
        if os.path.getsize(self.path) == 0:
            return 0
        with open(self.path, "rb") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("lsn", 0) > max_lsn:
                        max_lsn = rec["lsn"]
                except Exception:
                    # ignore torn / malformed tail line
                    pass
        return max_lsn

    def append(self, record: dict) -> int:
        lsn = self.next_lsn
        self.next_lsn += 1
        rec = dict(record)
        rec["lsn"] = lsn
        line = (json.dumps(rec) + "\n").encode()
        self._file.write(line)
        return lsn

    def fsync(self) -> None:
        """Flush + fsync — only after this call is the record durable."""
        self._file.flush()
        os.fsync(self._file.fileno())

    def close(self) -> None:
        try:
            self._file.close()
        except Exception:
            pass

    # -- iteration for recovery --

    def iter_records(self):
        """Yield records in order, skipping torn/malformed lines."""
        with open(self.path, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue  # torn tail


# ---------------------------------------------------------------------------
# Tiny KV store backed by WAL
# ---------------------------------------------------------------------------

class WALKVStore:
    """
    In-memory dict, every mutation persisted to a WAL.
    Recovery reads the WAL and replays operations after the last checkpoint.
    """

    def __init__(self, wal_path: str):
        self.wal = WAL(wal_path)
        self.data: dict = {}
        self._last_checkpoint_lsn = 0
        self._recover()

    def _recover(self) -> None:
        """Replay WAL: snapshot at latest checkpoint, then ops after it."""
        snapshot = {}
        snap_lsn = 0
        # First pass: find the last checkpoint
        for rec in self.wal.iter_records():
            if rec["type"] == "checkpoint":
                snapshot = dict(rec["snapshot"])
                snap_lsn = rec["lsn"]
        # Second pass: replay ops AFTER the snapshot
        self.data = snapshot
        self._last_checkpoint_lsn = snap_lsn
        for rec in self.wal.iter_records():
            if rec["lsn"] <= snap_lsn:
                continue
            if rec["type"] == "put":
                self.data[rec["k"]] = rec["v"]
            elif rec["type"] == "del":
                self.data.pop(rec["k"], None)

    def put(self, k, v) -> None:
        self.wal.append({"type": "put", "k": k, "v": v})
        self.wal.fsync()
        self.data[k] = v

    def delete(self, k) -> None:
        self.wal.append({"type": "del", "k": k})
        self.wal.fsync()
        self.data.pop(k, None)

    def get(self, k):
        return self.data.get(k)

    def checkpoint(self) -> None:
        self.wal.append({"type": "checkpoint", "snapshot": dict(self.data)})
        self.wal.fsync()
        self._last_checkpoint_lsn = self.wal.next_lsn - 1

    def close(self) -> None:
        self.wal.close()


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Put + get with WAL durability")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "kv.wal")
        kv = WALKVStore(path)
        kv.put("a", 1)
        kv.put("b", 2)
        kv.put("c", 3)
        kv.delete("b")
        print(f"  a={kv.get('a')} b={kv.get('b')} c={kv.get('c')}")
        kv.close()


def demo_crash_recovery():
    print("\n" + "=" * 60)
    print("DEMO 2: Crash recovery — drop the in-memory state, reopen")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "kv.wal")
        kv = WALKVStore(path)
        kv.put("user:1", "alice")
        kv.put("user:2", "bob")
        kv.put("user:3", "carol")
        kv.delete("user:2")
        # Simulate crash: close without flushing data files; only WAL persists.
        kv.close()
        print("  CRASH (in-memory state lost)")

        kv2 = WALKVStore(path)   # recovery happens here
        print(f"  recovered user:1 = {kv2.get('user:1')}")
        print(f"  recovered user:2 = {kv2.get('user:2')}  (expected None)")
        print(f"  recovered user:3 = {kv2.get('user:3')}")
        kv2.close()


def demo_checkpoint_speeds_recovery():
    print("\n" + "=" * 60)
    print("DEMO 3: Checkpoint shrinks replay cost")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "kv.wal")
        kv = WALKVStore(path)
        for i in range(100):
            kv.put(f"k{i}", i)
        kv.checkpoint()
        for i in range(100, 110):
            kv.put(f"k{i}", i)
        kv.close()

        # Inspect: count records after last checkpoint
        records = list(WAL(path).iter_records())
        last_ckpt = max((r["lsn"] for r in records if r["type"] == "checkpoint"),
                        default=0)
        replay_count = sum(1 for r in records if r["lsn"] > last_ckpt)
        print(f"  total records: {len(records)}")
        print(f"  replay-on-recovery records: {replay_count}")

        kv2 = WALKVStore(path)
        print(f"  recovered k0={kv2.get('k0')}  k99={kv2.get('k99')}"
              f"  k105={kv2.get('k105')}")
        kv2.close()


def demo_torn_tail():
    print("\n" + "=" * 60)
    print("DEMO 4: Torn WAL tail — last line incomplete after crash")
    print("=" * 60)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "kv.wal")
        kv = WALKVStore(path)
        kv.put("safe", 1)
        kv.close()
        # Manually append a torn line (simulate power loss mid-write).
        with open(path, "ab") as f:
            f.write(b'{"type":"put","k":"unsafe","v":')   # truncated
        # Recovery must ignore the torn record and keep going.
        kv2 = WALKVStore(path)
        print(f"  recovered safe = {kv2.get('safe')}")
        print(f"  recovered unsafe = {kv2.get('unsafe')}  (expected None)")
        kv2.close()


if __name__ == "__main__":
    demo_basic()
    demo_crash_recovery()
    demo_checkpoint_speeds_recovery()
    demo_torn_tail()
