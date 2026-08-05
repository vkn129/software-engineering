"""
Day 165 Practice: LSM Tree primitives

Implement TODOs, run: python practice.py
"""

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
# Exercise 1: Flush memtable to a sorted SSTable
# ===================================================================
# Given a dict, return a sorted list of (key, value) tuples.

def flush_memtable(memtable):
    """Return sorted list of (key, value)."""
    # TODO
    pass


def _sol_flush_memtable(memtable):
    return sorted(memtable.items(), key=lambda kv: kv[0])


# ===================================================================
# Exercise 2: Binary-search SSTable
# ===================================================================
# entries is a sorted list of (key, value). Return value or None.

def sstable_get(entries, key):
    """Binary search. Returns value (may be TOMBSTONE) or None."""
    # TODO
    pass


def _sol_sstable_get(entries, key):
    if not entries:
        return None
    lo, hi = 0, len(entries) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        k, v = entries[mid]
        if k == key:
            return v
        if k < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


# ===================================================================
# Exercise 3: LSM read path
# ===================================================================
# Layers ordered newest-first: [memtable_dict, sstable_entries_newest, ..., oldest]
# Return value (resolving TOMBSTONE to None) or None.

def lsm_get(layers, key):
    """layers: list. Each item is dict (memtable) or list[(k,v)] (sstable)."""
    # TODO
    pass


def _sol_lsm_get(layers, key):
    for layer in layers:
        if isinstance(layer, dict):
            if key in layer:
                v = layer[key]
                return None if v == TOMBSTONE else v
        else:
            v = _sol_sstable_get(layer, key)
            if v is not None:
                return None if v == TOMBSTONE else v
    return None


# ===================================================================
# Exercise 4: Merge two SSTables (k-way for k=2)
# ===================================================================
# Newer (a) wins on duplicates. Output sorted entries.

def merge_sstables(a_newer, b_older):
    """Two sorted lists -> one sorted list with newer winning on duplicates."""
    # TODO
    pass


def _sol_merge_sstables(a_newer, b_older):
    out = []
    i = j = 0
    while i < len(a_newer) and j < len(b_older):
        ka, _ = a_newer[i]
        kb, _ = b_older[j]
        if ka < kb:
            out.append(a_newer[i]); i += 1
        elif ka > kb:
            out.append(b_older[j]); j += 1
        else:
            out.append(a_newer[i])   # newer wins
            i += 1; j += 1
    out.extend(a_newer[i:])
    out.extend(b_older[j:])
    return out


# ===================================================================
# Exercise 5: Drop tombstones (only when at bottom level)
# ===================================================================

def drop_tombstones(entries):
    """Remove any (k, TOMBSTONE) entries from sorted list."""
    # TODO
    pass


def _sol_drop_tombstones(entries):
    return [(k, v) for k, v in entries if v != TOMBSTONE]


# ===================================================================
# Exercise 6: Compute write amplification
# ===================================================================
# Given a record of user writes and total bytes written to disk
# (memtable flushes + compaction rewrites), return ratio disk/user.

def write_amplification(user_writes_bytes, disk_writes_bytes):
    """Return float ratio. If user_writes_bytes == 0, return 0.0."""
    # TODO
    pass


def _sol_write_amplification(user_writes_bytes, disk_writes_bytes):
    if user_writes_bytes == 0:
        return 0.0
    return disk_writes_bytes / user_writes_bytes


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
    print("Exercise 1: flush_memtable")
    out = try_or_sol("flush_memtable", {"b": 2, "a": 1, "c": 3})
    check("sorted by key", out, [("a", 1), ("b", 2), ("c", 3)])

    # Ex 2
    print("\nExercise 2: sstable_get")
    sst = [("a", 1), ("b", 2), ("d", 4), ("z", 99)]
    check("hit", try_or_sol("sstable_get", sst, "d"), 4)
    check("miss", try_or_sol("sstable_get", sst, "c"), None)
    check("tombstone returned",
          try_or_sol("sstable_get", [("x", TOMBSTONE)], "x"), TOMBSTONE)

    # Ex 3
    print("\nExercise 3: lsm_get")
    layers = [
        {"hot": 99, "miss": TOMBSTONE},          # memtable (newest)
        [("a", 1), ("hot", 10)],                  # L0 SSTable
        [("a", 0), ("b", 2)],                     # L1 SSTable (oldest)
    ]
    check("memtable wins on hot", try_or_sol("lsm_get", layers, "hot"), 99)
    check("tombstone -> None", try_or_sol("lsm_get", layers, "miss"), None)
    check("L0 wins over L1", try_or_sol("lsm_get", layers, "a"), 1)
    check("only in L1", try_or_sol("lsm_get", layers, "b"), 2)
    check("absent", try_or_sol("lsm_get", layers, "zzz"), None)

    # Ex 4
    print("\nExercise 4: merge_sstables")
    a = [("a", 10), ("c", 30)]
    b = [("a", 1), ("b", 2), ("c", 3), ("d", 4)]
    merged = try_or_sol("merge_sstables", a, b)
    check("merge with newer winning", merged,
          [("a", 10), ("b", 2), ("c", 30), ("d", 4)])

    # Ex 5
    print("\nExercise 5: drop_tombstones")
    cleaned = try_or_sol("drop_tombstones",
                         [("a", 1), ("b", TOMBSTONE), ("c", 3)])
    check("tombstone gone", cleaned, [("a", 1), ("c", 3)])

    # Ex 6
    print("\nExercise 6: write_amplification")
    check("3x amp", try_or_sol("write_amplification", 100, 300), 3.0)
    check("zero user", try_or_sol("write_amplification", 0, 100), 0.0)

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
