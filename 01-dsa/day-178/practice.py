"""
Day 178 Practice: Query Optimizer building blocks (4 exercises).
"""

import math


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        r = student_fn(*args, **kwargs)
        if r is not None:
            return r
    return sol_fn(*args, **kwargs)


# ===================================================================
# Ex 1: Equality selectivity
# ===================================================================
# sel(col = v) = 1 / ndv(col), clamped to [0,1].

def equality_selectivity(ndv):
    """Return 1/ndv (with ndv at least 1)."""
    # TODO: implement
    pass


def _sol_equality_selectivity(ndv):
    return 1.0 / max(1, ndv)


# ===================================================================
# Ex 2: Range selectivity
# ===================================================================
# For 'col > v': (max - v) / (max - min), clamped.

def range_gt_selectivity(min_v, max_v, value):
    """Fraction of rows with col > value, assuming uniform distribution."""
    # TODO: implement
    pass


def _sol_range_gt_selectivity(min_v, max_v, value):
    if max_v == min_v:
        return 0.0 if value >= max_v else 1.0
    sel = (max_v - value) / (max_v - min_v)
    return max(0.0, min(1.0, sel))


# ===================================================================
# Ex 3: Plan choice — index vs seq scan
# ===================================================================
# Compare costs:
#   seq_scan(n)        = 1.0 * n
#   index_scan(n*sel)  = 4.0 * n * sel
# Return 'index' if index_scan cost < seq_scan cost, else 'seq'.

def pick_access(n_rows, selectivity):
    """Return 'index' or 'seq' based on cost comparison."""
    # TODO: implement
    pass


def _sol_pick_access(n_rows, selectivity):
    seq = 1.0 * n_rows
    idx = 4.0 * n_rows * selectivity
    return 'index' if idx < seq else 'seq'


# ===================================================================
# Ex 4: 2-way join order — which side as build?
# ===================================================================
# Hash join builds on the smaller side. Given two estimated cardinalities,
# return 'left' or 'right' — the side we should hash on (smaller one).

def hash_build_side(n_left, n_right):
    """Return 'left' if left is smaller (or tied), else 'right'."""
    # TODO: implement
    pass


def _sol_hash_build_side(n_left, n_right):
    return 'left' if n_left <= n_right else 'right'


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    passed = failed = 0

    def check(name, got, expected, tol=0):
        nonlocal passed, failed
        ok = (got == expected) if tol == 0 else (abs(got - expected) < tol)
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  expected={expected}  got={got}")
            failed += 1

    print("Exercise 1: Equality Selectivity")
    check("ndv=4 -> 0.25", try_or_sol("equality_selectivity", 4), 0.25, tol=1e-9)
    check("ndv=1 -> 1.0", try_or_sol("equality_selectivity", 1), 1.0, tol=1e-9)
    check("ndv=0 -> 1.0 (clamped)", try_or_sol("equality_selectivity", 0), 1.0, tol=1e-9)

    print("\nExercise 2: Range Selectivity")
    check("> 50 of [0,100] -> 0.5",
          try_or_sol("range_gt_selectivity", 0, 100, 50), 0.5, tol=1e-9)
    check("> -10 -> 1.0 (clamped)",
          try_or_sol("range_gt_selectivity", 0, 100, -10), 1.0, tol=1e-9)
    check("> 200 -> 0.0 (clamped)",
          try_or_sol("range_gt_selectivity", 0, 100, 200), 0.0, tol=1e-9)

    print("\nExercise 3: Access Path Choice")
    # n=1000, sel=0.01: seq=1000, idx=40 -> index
    check("selective -> index",
          try_or_sol("pick_access", 1000, 0.01), 'index')
    # n=1000, sel=0.5: seq=1000, idx=2000 -> seq
    check("non-selective -> seq",
          try_or_sol("pick_access", 1000, 0.5), 'seq')

    print("\nExercise 4: Hash Build Side")
    check("smaller left -> left",
          try_or_sol("hash_build_side", 10, 1000), 'left')
    check("smaller right -> right",
          try_or_sol("hash_build_side", 1000, 10), 'right')
    check("equal -> left",
          try_or_sol("hash_build_side", 100, 100), 'left')

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
