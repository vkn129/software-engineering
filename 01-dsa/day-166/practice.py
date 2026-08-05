"""
Day 166 Practice: Write-Ahead Log

Implement TODOs, run: python practice.py
"""

import os
import json
import tempfile


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ===================================================================
# Exercise 1: Append a record to a WAL file
# ===================================================================
# Append JSON line (record dict + newline). Caller fsyncs.

def wal_append(path, record):
    """Append a record (dict) as one JSON line. Return new file size."""
    # TODO
    pass


def _sol_wal_append(path, record):
    with open(path, "ab") as f:
        f.write((json.dumps(record) + "\n").encode())
    return os.path.getsize(path)


# ===================================================================
# Exercise 2: Iterate WAL records, skipping torn tail
# ===================================================================

def wal_read_all(path):
    """Return list of records, skipping malformed lines."""
    # TODO
    pass


def _sol_wal_read_all(path):
    out = []
    with open(path, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


# ===================================================================
# Exercise 3: Replay WAL into a dict
# ===================================================================
# Records: {"type":"put","k":..,"v":..} or {"type":"del","k":..}.
# Return final state dict.

def replay(records):
    """Apply records in order. Return resulting dict."""
    # TODO
    pass


def _sol_replay(records):
    state = {}
    for r in records:
        if r.get("type") == "put":
            state[r["k"]] = r["v"]
        elif r.get("type") == "del":
            state.pop(r["k"], None)
    return state


# ===================================================================
# Exercise 4: Find the latest checkpoint LSN
# ===================================================================

def latest_checkpoint_lsn(records):
    """Return the LSN of the last checkpoint record, or 0 if none."""
    # TODO
    pass


def _sol_latest_checkpoint_lsn(records):
    return max((r["lsn"] for r in records if r.get("type") == "checkpoint"),
               default=0)


# ===================================================================
# Exercise 5: Replay after last checkpoint
# ===================================================================
# Start from the snapshot in the latest checkpoint record, then apply
# all op records with lsn > checkpoint_lsn.

def recover(records):
    """Return final state, starting from latest checkpoint snapshot."""
    # TODO
    pass


def _sol_recover(records):
    snap = {}
    snap_lsn = 0
    for r in records:
        if r.get("type") == "checkpoint":
            snap = dict(r["snapshot"])
            snap_lsn = r["lsn"]
    state = snap
    for r in records:
        if r.get("lsn", 0) <= snap_lsn:
            continue
        if r.get("type") == "put":
            state[r["k"]] = r["v"]
        elif r.get("type") == "del":
            state.pop(r["k"], None)
    return state


# ===================================================================
# Exercise 6: Simulate crash + recovery
# ===================================================================
# Given a list of operations, write them to a WAL, simulate crash,
# reopen and recover. Return the recovered dict.

def simulate_crash_recovery(operations):
    """
    operations: list of ("put", k, v) or ("del", k) or ("checkpoint",).
    Apply, then drop state, then recover from WAL on disk.
    """
    # TODO
    pass


def _sol_simulate_crash_recovery(operations):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "wal.log")
        open(path, "wb").close()
        lsn = 0
        state = {}
        for op in operations:
            lsn += 1
            if op[0] == "put":
                rec = {"lsn": lsn, "type": "put", "k": op[1], "v": op[2]}
                state[op[1]] = op[2]
            elif op[0] == "del":
                rec = {"lsn": lsn, "type": "del", "k": op[1]}
                state.pop(op[1], None)
            elif op[0] == "checkpoint":
                rec = {"lsn": lsn, "type": "checkpoint", "snapshot": dict(state)}
            else:
                raise ValueError(op)
            _sol_wal_append(path, rec)
        # CRASH: discard in-memory state
        state = None
        records = _sol_wal_read_all(path)
        return _sol_recover(records)


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

    # Ex 1
    print("Exercise 1: wal_append")
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "w.log")
        open(path, "wb").close()
        size = try_or_sol("wal_append", path, {"lsn": 1, "type": "put", "k": "a", "v": 1})
        check("file grew", size > 0, True)
        try_or_sol("wal_append", path, {"lsn": 2, "type": "put", "k": "b", "v": 2})
        recs = try_or_sol("wal_read_all", path)
        check("two records", len(recs), 2)

    # Ex 2
    print("\nExercise 2: wal_read_all (torn tail)")
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "torn.log")
        with open(path, "wb") as f:
            f.write(b'{"lsn":1,"type":"put","k":"a","v":1}\n')
            f.write(b'{"lsn":2,"type":"put","k":"b","v":')   # torn
        recs = try_or_sol("wal_read_all", path)
        check("ignores torn line", len(recs), 1)

    # Ex 3
    print("\nExercise 3: replay")
    state = try_or_sol("replay", [
        {"type": "put", "k": "a", "v": 1},
        {"type": "put", "k": "b", "v": 2},
        {"type": "del", "k": "a"},
        {"type": "put", "k": "c", "v": 3},
    ])
    check("final state", state, {"b": 2, "c": 3})

    # Ex 4
    print("\nExercise 4: latest_checkpoint_lsn")
    recs = [
        {"lsn": 1, "type": "put", "k": "a", "v": 1},
        {"lsn": 2, "type": "checkpoint", "snapshot": {"a": 1}},
        {"lsn": 3, "type": "put", "k": "b", "v": 2},
        {"lsn": 4, "type": "checkpoint", "snapshot": {"a": 1, "b": 2}},
        {"lsn": 5, "type": "put", "k": "c", "v": 3},
    ]
    check("latest checkpoint lsn", try_or_sol("latest_checkpoint_lsn", recs), 4)
    check("no checkpoint -> 0",
          try_or_sol("latest_checkpoint_lsn",
                     [{"lsn": 1, "type": "put", "k": "a", "v": 1}]),
          0)

    # Ex 5
    print("\nExercise 5: recover")
    state = try_or_sol("recover", recs)
    check("recovers via checkpoint+tail", state, {"a": 1, "b": 2, "c": 3})

    # Ex 6
    print("\nExercise 6: simulate_crash_recovery")
    ops = [
        ("put", "x", 1), ("put", "y", 2), ("checkpoint",),
        ("put", "z", 3), ("del", "x"),
    ]
    final = try_or_sol("simulate_crash_recovery", ops)
    check("post-crash state", final, {"y": 2, "z": 3})

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
