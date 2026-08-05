"""
Day 177 Practice: Query Engine Building Blocks (4 exercises)

Light practice — the main work is in query_engine.py.
"""

import bisect
from collections import defaultdict


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        r = student_fn(*args, **kwargs)
        if r is not None:
            return r
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Sequential filter scan
# ===================================================================
# Walk rows, return those matching predicate.

def seq_scan_filter(rows, column, op, value):
    """rows: list of dicts. Return rows where row[column] op value."""
    # TODO: implement
    pass


def _sol_seq_scan_filter(rows, column, op, value):
    if op == '=':
        return [r for r in rows if r[column] == value]
    if op == '>':
        return [r for r in rows if r[column] > value]
    if op == '<':
        return [r for r in rows if r[column] < value]
    if op == '>=':
        return [r for r in rows if r[column] >= value]
    if op == '<=':
        return [r for r in rows if r[column] <= value]
    return []


# ===================================================================
# Exercise 2: Sorted index range lookup
# ===================================================================
# Use bisect on sorted (key, row_id) list. Range op '>' for value `v`
# means: return all row_ids whose key > v.

def index_range_gt(sorted_index, value):
    """sorted_index: list of (key, row_id) sorted by key.
       Return row_ids with key > value."""
    # TODO: implement
    pass


def _sol_index_range_gt(sorted_index, value):
    keys = [p[0] for p in sorted_index]
    lo = bisect.bisect_right(keys, value)
    return [sorted_index[i][1] for i in range(lo, len(sorted_index))]


# ===================================================================
# Exercise 3: Hash join (equi-join)
# ===================================================================
# Build hash on left, probe with right.

def hash_join(left, right, left_key, right_key):
    """left, right: lists of dicts.
       Returns list of merged dicts (left ∪ right) where left[lk] == right[rk]."""
    # TODO: implement
    pass


def _sol_hash_join(left, right, left_key, right_key):
    ht = defaultdict(list)
    for l in left:
        ht[l[left_key]].append(l)
    out = []
    for r in right:
        for l in ht.get(r[right_key], ()):
            merged = dict(l)
            merged.update(r)
            out.append(merged)
    return out


# ===================================================================
# Exercise 4: Sort-merge join
# ===================================================================
# Sort both sides, then linear merge.

def sort_merge_join(left, right, left_key, right_key):
    """Same contract as hash_join, but uses sort+merge."""
    # TODO: implement
    pass


def _sol_sort_merge_join(left, right, left_key, right_key):
    L = sorted(left, key=lambda r: r[left_key])
    R = sorted(right, key=lambda r: r[right_key])
    i = j = 0
    out = []
    while i < len(L) and j < len(R):
        lk, rk = L[i][left_key], R[j][right_key]
        if lk < rk:
            i += 1
        elif lk > rk:
            j += 1
        else:
            i_end = i
            while i_end < len(L) and L[i_end][left_key] == lk:
                i_end += 1
            j_end = j
            while j_end < len(R) and R[j_end][right_key] == rk:
                j_end += 1
            for a in range(i, i_end):
                for b in range(j, j_end):
                    merged = dict(L[a])
                    merged.update(R[b])
                    out.append(merged)
            i, j = i_end, j_end
    return out


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    passed = failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  expected={expected}  got={got}")
            failed += 1

    rows = [{'id': 1, 'salary': 100}, {'id': 2, 'salary': 200},
            {'id': 3, 'salary': 300}]

    print("Exercise 1: Sequential Filter")
    out = try_or_sol("seq_scan_filter", rows, 'salary', '>', 150)
    check("filter > 150", [r['id'] for r in out], [2, 3])
    out = try_or_sol("seq_scan_filter", rows, 'salary', '=', 200)
    check("filter = 200", [r['id'] for r in out], [2])

    print("\nExercise 2: Index Range")
    idx = [(100, 0), (200, 1), (300, 2)]
    check("> 150", try_or_sol("index_range_gt", idx, 150), [1, 2])
    check("> 300", try_or_sol("index_range_gt", idx, 300), [])
    check("> 99", try_or_sol("index_range_gt", idx, 99), [0, 1, 2])

    print("\nExercise 3: Hash Join")
    L = [{'a': 1, 'x': 'a1'}, {'a': 2, 'x': 'a2'}]
    R = [{'b': 1, 'y': 'b1'}, {'b': 2, 'y': 'b2'}, {'b': 2, 'y': 'b2b'}]
    out = try_or_sol("hash_join", L, R, 'a', 'b')
    check("join row count", len(out), 3)

    print("\nExercise 4: Sort-Merge Join")
    out = try_or_sol("sort_merge_join", L, R, 'a', 'b')
    check("sort-merge same count", len(out), 3)
    # Same join — same multiset of rows
    h = try_or_sol("hash_join", L, R, 'a', 'b')
    check("sort-merge matches hash",
          sorted(tuple(sorted(d.items())) for d in out),
          sorted(tuple(sorted(d.items())) for d in h))

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
