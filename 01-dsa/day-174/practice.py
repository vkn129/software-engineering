"""
Day 174 Practice: Persistent Data Structures

6 exercises covering versioned set, range sum across versions, undo,
inversions count, and k-th smallest in range.
Run: python practice.py
"""

import sys
sys.setrecursionlimit(10**6)


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


class Node:
    __slots__ = ('left', 'right', 'sum')

    def __init__(self, left=None, right=None, sum=0):
        self.left = left; self.right = right; self.sum = sum


def _build(arr, l, r):
    if l == r:
        return Node(sum=arr[l])
    m = (l + r) // 2
    lc = _build(arr, l, m); rc = _build(arr, m + 1, r)
    return Node(lc, rc, lc.sum + rc.sum)


def _update(node, l, r, idx, val):
    if l == r:
        return Node(sum=val)
    m = (l + r) // 2
    if idx <= m:
        nl = _update(node.left, l, m, idx, val)
        return Node(nl, node.right, nl.sum + node.right.sum)
    nr = _update(node.right, m + 1, r, idx, val)
    return Node(node.left, nr, node.left.sum + nr.sum)


def _query(node, l, r, ql, qr):
    if qr < l or r < ql:
        return 0
    if ql <= l and r <= qr:
        return node.sum
    m = (l + r) // 2
    return _query(node.left, l, m, ql, qr) + _query(node.right, m + 1, r, ql, qr)


# ===================================================================
# Exercise 1: Versioned Set Value
# ===================================================================
# Given initial array and a list of (version_to_branch_from, idx, val),
# return a list of resulting roots' total sum.

def versioned_total_sums(arr, ops):
    """
    arr: list of ints (version 0)
    ops: list of (base_version, idx, new_val); each appends a new version
    Returns: list of total sums for every version (including v0)
    """
    # TODO
    pass


def _sol_versioned_total_sums(arr, ops):
    n = len(arr)
    versions = [_build(arr, 0, n - 1)] if n > 0 else [Node(sum=0)]
    results = [versions[0].sum]
    for base, idx, val in ops:
        nr = _update(versions[base], 0, n - 1, idx, val)
        versions.append(nr)
        results.append(nr.sum)
    return results


# ===================================================================
# Exercise 2: Range Sum on a Specific Version
# ===================================================================

def versioned_range_sum(arr, ops, queries):
    """
    Each op appends a new version. Each query is (version, l, r).
    Returns: list of answers.
    """
    # TODO
    pass


def _sol_versioned_range_sum(arr, ops, queries):
    n = len(arr)
    versions = [_build(arr, 0, n - 1)]
    for base, idx, val in ops:
        versions.append(_update(versions[base], 0, n - 1, idx, val))
    out = []
    for v, l, r in queries:
        out.append(_query(versions[v], 0, n - 1, l, r))
    return out


# ===================================================================
# Exercise 3: Undo Last K Updates
# ===================================================================
# After a sequence of updates branching linearly (each from the previous
# version), return the array state from `K` updates ago.

def undo_k(arr, updates, k):
    """
    arr: initial array
    updates: list of (idx, val), applied in order
    k: undo last k updates
    Returns: list = state of array after applying len(updates) - k updates.
    """
    # TODO: build persistent versions linearly, then read version len-k.
    pass


def _sol_undo_k(arr, updates, k):
    n = len(arr)
    versions = [_build(arr, 0, n - 1)]
    for idx, val in updates:
        versions.append(_update(versions[-1], 0, n - 1, idx, val))
    target = len(updates) - k
    if target < 0:
        target = 0
    root = versions[target]
    return [_query(root, 0, n - 1, i, i) for i in range(n)]


# ===================================================================
# Exercise 4: Count Inversions via Persistent Segtree
# ===================================================================
# Count pairs (i, j) with i < j and arr[i] > arr[j].

def count_inversions(arr):
    """
    arr: list of ints
    Returns: number of inversions
    """
    # TODO: use compression + insert each element + count > arr[j] already in
    pass


def _sol_count_inversions(arr):
    sorted_vals = sorted(set(arr))
    rank = {v: i for i, v in enumerate(sorted_vals)}
    n = len(sorted_vals)
    if n == 0:
        return 0
    # Use a single (non-persistent) BIT-style segment tree for simplicity
    tree = [0] * (4 * n)

    def update(node, l, r, idx):
        if l == r:
            tree[node] += 1; return
        m = (l + r) // 2
        if idx <= m:
            update(2*node, l, m, idx)
        else:
            update(2*node+1, m+1, r, idx)
        tree[node] = tree[2*node] + tree[2*node+1]

    def query(node, l, r, ql, qr):
        if qr < l or r < ql:
            return 0
        if ql <= l and r <= qr:
            return tree[node]
        m = (l + r) // 2
        return query(2*node, l, m, ql, qr) + query(2*node+1, m+1, r, ql, qr)

    inv = 0
    for x in arr:
        rx = rank[x]
        # count elements already inserted with rank > rx
        inv += query(1, 0, n-1, rx+1, n-1) if rx+1 <= n-1 else 0
        update(1, 0, n-1, rx)
    return inv


# ===================================================================
# Exercise 5: K-th Smallest in Range
# ===================================================================

def kth_smallest_in_range(arr, queries):
    """
    arr: list of ints
    queries: list of (l, r, k) with 1 <= k <= r - l + 1
    Returns: list of k-th smallest values for each query (1-indexed k)
    """
    # TODO: persistent segment tree over compressed values
    pass


def _sol_kth_smallest_in_range(arr, queries):
    n = len(arr)
    if n == 0:
        return [0 for _ in queries]
    sorted_vals = sorted(set(arr))
    rank = {v: i for i, v in enumerate(sorted_vals)}
    V = len(sorted_vals)

    def build(l, r):
        if l == r:
            return Node(sum=0)
        m = (l + r) // 2
        return Node(build(l, m), build(m + 1, r), 0)

    def upd(node, l, r, idx):
        if l == r:
            return Node(sum=node.sum + 1)
        m = (l + r) // 2
        if idx <= m:
            nl = upd(node.left, l, m, idx)
            return Node(nl, node.right, nl.sum + node.right.sum)
        nr = upd(node.right, m + 1, r, idx)
        return Node(node.left, nr, node.left.sum + nr.sum)

    versions = [build(0, V - 1)]
    for x in arr:
        versions.append(upd(versions[-1], 0, V - 1, rank[x]))

    def kth(ln, rn, l, r, k):
        if l == r:
            return sorted_vals[l]
        m = (l + r) // 2
        left_c = rn.left.sum - ln.left.sum
        if k <= left_c:
            return kth(ln.left, rn.left, l, m, k)
        return kth(ln.right, rn.right, m + 1, r, k - left_c)

    out = []
    for l, r, k in queries:
        out.append(kth(versions[l], versions[r + 1], 0, V - 1, k))
    return out


# ===================================================================
# Exercise 6: Sum of Versions
# ===================================================================
# Just compute sum of total array values across a sequence of branched
# versions (test of correct version pointer management).

def sum_of_all_versions(arr, ops):
    """
    Apply ops where each op (base_version, idx, val) makes a new version
    by setting arr[idx] = val in base_version's state. Return sum over all
    resulting version totals (initial counted once).
    """
    # TODO
    pass


def _sol_sum_of_all_versions(arr, ops):
    sums = _sol_versioned_total_sums(arr, ops)
    return sum(sums)


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
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    arr = [1, 2, 3, 4, 5]

    # --- Exercise 1 ---
    print("Exercise 1: Versioned Total Sums")
    ops = [(0, 0, 10), (0, 2, 100), (1, 4, 50)]
    # v0 sum=15; v1 (arr[0]=10) sum=24; v2 (arr[2]=100) sum=112; v3 (from v1, arr[4]=50) sum=24-5+50=69
    check("totals", try_or_sol("versioned_total_sums", arr, ops),
          [15, 24, 112, 69])

    # --- Exercise 2 ---
    print("\nExercise 2: Versioned Range Sum")
    queries = [(0, 0, 4), (1, 0, 4), (2, 0, 2), (3, 2, 4)]
    # v0 sum[0..4]=15; v1 sum[0..4]=24; v2 sum[0..2]=1+2+100=103; v3 sum[2..4]=3+4+50=57
    check("range sums", try_or_sol("versioned_range_sum", arr, ops, queries),
          [15, 24, 103, 57])

    # --- Exercise 3 ---
    print("\nExercise 3: Undo K")
    updates = [(0, 10), (1, 20), (2, 30)]
    # after all: [10,20,30,4,5]; undo 1 -> [10,20,3,4,5]; undo 2 -> [10,2,3,4,5]
    check("undo 1", try_or_sol("undo_k", arr, updates, 1), [10, 20, 3, 4, 5])
    check("undo 2", try_or_sol("undo_k", arr, updates, 2), [10, 2, 3, 4, 5])
    check("undo all", try_or_sol("undo_k", arr, updates, 3), [1, 2, 3, 4, 5])

    # --- Exercise 4 ---
    print("\nExercise 4: Count Inversions")
    check("[2,1]", try_or_sol("count_inversions", [2, 1]), 1)
    check("[5,4,3,2,1]", try_or_sol("count_inversions", [5, 4, 3, 2, 1]), 10)
    check("sorted", try_or_sol("count_inversions", [1, 2, 3, 4, 5]), 0)
    check("with dup", try_or_sol("count_inversions", [3, 1, 2, 3, 1]), 5)

    # --- Exercise 5 ---
    print("\nExercise 5: K-th Smallest in Range")
    nums = [5, 1, 4, 2, 8, 3, 7, 6]
    qs = [(0, 7, 1), (0, 7, 4), (2, 5, 2), (3, 6, 3)]
    # 1st in [0..7] = 1; 4th in [0..7] = 4; 2nd in [4,2,8,3] sorted=[2,3,4,8] -> 3; 3rd in [2,8,3,7] sorted=[2,3,7,8] -> 7
    check("kth queries", try_or_sol("kth_smallest_in_range", nums, qs),
          [1, 4, 3, 7])

    # --- Exercise 6 ---
    print("\nExercise 6: Sum of All Versions")
    check("sum of versions", try_or_sol("sum_of_all_versions", arr, ops),
          15 + 24 + 112 + 69)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
