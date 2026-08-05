"""
Day 168 Practice: Durable KV Store primitives

Implement TODOs, run: python practice.py
"""

import os
import json
import tempfile


TOMBSTONE = "__TOMB__"


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ===================================================================
# Exercise 1: Write an SSTable atomically (temp + rename)
# ===================================================================
# Write a sorted list of (k, v) to <path>.tmp, then rename to <path>.

def write_sstable_atomic(path, entries):
    """Write entries to path atomically. Return path on success."""
    # TODO
    pass


def _sol_write_sstable_atomic(path, entries):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps({"entries": entries}).encode())
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)
    return path


# ===================================================================
# Exercise 2: Read SSTable back
# ===================================================================

def read_sstable(path):
    """Return list of (k, v) tuples (as tuples, not lists)."""
    # TODO
    pass


def _sol_read_sstable(path):
    with open(path, "rb") as f:
        data = json.loads(f.read())
    return [tuple(e) for e in data["entries"]]


# ===================================================================
# Exercise 3: WAL replay into memtable dict
# ===================================================================
# Iterate WAL records and produce final memtable state.
# Tombstones stay as TOMBSTONE in the memtable.

def replay_wal(records):
    """Return memtable dict including tombstones."""
    # TODO
    pass


def _sol_replay_wal(records):
    state = {}
    for r in records:
        if r.get("type") == "put":
            state[r["k"]] = r["v"]
        elif r.get("type") == "del":
            state[r["k"]] = TOMBSTONE
    return state


# ===================================================================
# Exercise 4: Resolve a get across memtable + SSTables
# ===================================================================
# memtable: dict (may hold TOMBSTONE).
# sstables: list of [(k,v), ...] from oldest to newest.
# Newer sources win. Return value (resolving TOMBSTONE to None) or None.

def kv_get(memtable, sstables, key):
    """Return the resolved value for key."""
    # TODO
    pass


def _sol_kv_get(memtable, sstables, key):
    if key in memtable:
        v = memtable[key]
        return None if v == TOMBSTONE else v
    for sst in reversed(sstables):
        for k, v in sst:
            if k == key:
                return None if v == TOMBSTONE else v
    return None


# ===================================================================
# Exercise 5: Simulate full crash-and-recover cycle
# ===================================================================
# Apply operations [("put",k,v) | ("del",k)] via a WAL file. After each
# call, simulate a crash, then recover and return final state (resolved,
# tombstones excluded).

def crash_and_recover(operations):
    """Apply ops, simulate crash, recover, return dict (no tombstones)."""
    # TODO
    pass


def _sol_crash_and_recover(operations):
    with tempfile.TemporaryDirectory() as d:
        wal = os.path.join(d, "wal.log")
        open(wal, "wb").close()
        for op in operations:
            if op[0] == "put":
                rec = {"type": "put", "k": op[1], "v": op[2]}
            elif op[0] == "del":
                rec = {"type": "del", "k": op[1]}
            else:
                raise ValueError(op)
            with open(wal, "ab") as f:
                f.write((json.dumps(rec) + "\n").encode())
                f.flush()
                os.fsync(f.fileno())
        # CRASH — drop everything. Reopen:
        records = []
        with open(wal, "rb") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
        mt = _sol_replay_wal(records)
        return {k: v for k, v in mt.items() if v != TOMBSTONE}


# ===================================================================
# Exercise 6: Compaction-style merge of multiple SSTables
# ===================================================================
# sstables ordered oldest -> newest. Merge with newer-wins, drop
# tombstones at the bottom level. Return sorted list of (k, v).

def compact(sstables):
    """Merge SSTables, drop tombstones. Return sorted (k, v) list."""
    # TODO
    pass


def _sol_compact(sstables):
    merged = {}
    for sst in sstables:
        for k, v in sst:
            merged[k] = v
    return sorted(((k, v) for k, v in merged.items() if v != TOMBSTONE),
                  key=lambda kv: kv[0])


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} expected={expected} got={got}")
            failed += 1

    # Ex 1 + 2
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "sst.json")
        print("Exercise 1: write_sstable_atomic")
        entries = [("a", 1), ("b", 2), ("c", 3)]
        ret = try_or_sol("write_sstable_atomic", path, entries)
        check("file exists", os.path.exists(path), True)
        check("no leftover .tmp", os.path.exists(path + ".tmp"), False)

        print("\nExercise 2: read_sstable")
        loaded = try_or_sol("read_sstable", path)
        check("roundtrip", loaded, entries)

    # Ex 3
    print("\nExercise 3: replay_wal")
    state = try_or_sol("replay_wal", [
        {"type": "put", "k": "a", "v": 1},
        {"type": "put", "k": "b", "v": 2},
        {"type": "del", "k": "a"},
        {"type": "put", "k": "c", "v": 3},
    ])
    check("tombstone preserved", state, {"a": TOMBSTONE, "b": 2, "c": 3})

    # Ex 4
    print("\nExercise 4: kv_get")
    memtable = {"hot": 99, "deleted": TOMBSTONE}
    sstables = [
        [("a", 0), ("hot", 10)],     # older
        [("a", 1), ("b", 2)],        # newer
    ]
    check("memtable wins", try_or_sol("kv_get", memtable, sstables, "hot"), 99)
    check("tombstone -> None",
          try_or_sol("kv_get", memtable, sstables, "deleted"), None)
    check("newer sstable wins",
          try_or_sol("kv_get", memtable, sstables, "a"), 1)
    check("only in older", try_or_sol("kv_get", memtable, sstables, "b"), 2)   # newer has b
    check("absent", try_or_sol("kv_get", memtable, sstables, "zz"), None)

    # Ex 5 — THE CRASH TEST
    print("\nExercise 5: crash_and_recover (THE crash test)")
    ops = [("put", "user:1", "alice"),
           ("put", "user:2", "bob"),
           ("del", "user:1"),
           ("put", "user:3", "carol")]
    recovered = try_or_sol("crash_and_recover", ops)
    check("crash recovered correctly",
          recovered, {"user:2": "bob", "user:3": "carol"})

    # Ex 6
    print("\nExercise 6: compact")
    ssts = [
        [("a", 0), ("b", 1), ("c", 2)],            # oldest
        [("b", TOMBSTONE), ("d", 4)],
        [("c", 99)],                                # newest
    ]
    out = try_or_sol("compact", ssts)
    check("compacted, tombstones dropped",
          out, [("a", 0), ("c", 99), ("d", 4)])

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
