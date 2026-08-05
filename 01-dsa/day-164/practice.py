"""
Day 164 Practice: CRDTs (G-Counter, PN-Counter, LWW-Register)

Implement TODOs, run: python practice.py
"""


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ===================================================================
# Exercise 1: G-Counter value
# ===================================================================
# State is dict[replica_id] -> count. value = sum of all slots.

def gcounter_value(state):
    """state: dict. Return integer sum."""
    # TODO
    pass


def _sol_gcounter_value(state):
    return sum(state.values())


# ===================================================================
# Exercise 2: G-Counter merge
# ===================================================================
# Return new dict with elementwise max of two states.

def gcounter_merge(a, b):
    """a, b: dict[str]->int. Return merged dict."""
    # TODO
    pass


def _sol_gcounter_merge(a, b):
    out = dict(a)
    for k, v in b.items():
        out[k] = max(out.get(k, 0), v)
    return out


# ===================================================================
# Exercise 3: PN-Counter value
# ===================================================================
# state = {'P': {...}, 'N': {...}}.  value = sum(P) - sum(N).

def pncounter_value(state):
    # TODO
    pass


def _sol_pncounter_value(state):
    return sum(state["P"].values()) - sum(state["N"].values())


# ===================================================================
# Exercise 4: PN-Counter merge
# ===================================================================

def pncounter_merge(a, b):
    """Merge two PN states. Return new state {'P':..., 'N':...}."""
    # TODO
    pass


def _sol_pncounter_merge(a, b):
    return {
        "P": _sol_gcounter_merge(a["P"], b["P"]),
        "N": _sol_gcounter_merge(a["N"], b["N"]),
    }


# ===================================================================
# Exercise 5: LWW-Register merge
# ===================================================================
# Each register is (value, ts, writer). Larger (ts, writer) wins.

def lww_merge(a, b):
    """a, b: tuple (value, ts, writer). Return tuple after merge."""
    # TODO
    pass


def _sol_lww_merge(a, b):
    return a if (a[1], a[2]) >= (b[1], b[2]) else b


# ===================================================================
# Exercise 6: convergence check
# ===================================================================
# Given a list of G-Counter states, all replicas must converge to the same
# merged state regardless of merge order. Return True if any permutation of
# merges yields the same dict as left-fold merging in input order.

def converges(states):
    """states: list of dicts. Return True if all merge orders converge."""
    # TODO
    pass


def _sol_converges(states):
    if not states:
        return True
    from functools import reduce
    base = reduce(_sol_gcounter_merge, states)
    # reversed order
    rev = reduce(_sol_gcounter_merge, reversed(states))
    return base == rev


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
    print("Exercise 1: gcounter_value")
    check("sum of slots", try_or_sol("gcounter_value", {"a": 3, "b": 2, "c": 5}), 10)
    check("empty -> 0", try_or_sol("gcounter_value", {}), 0)

    # Ex 2
    print("\nExercise 2: gcounter_merge")
    m = try_or_sol("gcounter_merge", {"a": 3, "b": 2}, {"b": 5, "c": 1})
    check("merge correct", m, {"a": 3, "b": 5, "c": 1})
    # idempotent
    again = try_or_sol("gcounter_merge", m, m)
    check("idempotent", again, m)

    # Ex 3
    print("\nExercise 3: pncounter_value")
    state = {"P": {"a": 10, "b": 5}, "N": {"a": 2, "b": 1}}
    check("P - N", try_or_sol("pncounter_value", state), 12)

    # Ex 4
    print("\nExercise 4: pncounter_merge")
    a = {"P": {"a": 5}, "N": {"a": 1}}
    b = {"P": {"a": 3, "b": 4}, "N": {"a": 2}}
    merged = try_or_sol("pncounter_merge", a, b)
    check("P merged", merged["P"], {"a": 5, "b": 4})
    check("N merged", merged["N"], {"a": 2})

    # Ex 5
    print("\nExercise 5: lww_merge")
    check("higher ts wins",
          try_or_sol("lww_merge", ("old", 1, "A"), ("new", 5, "B")),
          ("new", 5, "B"))
    check("tie -> writer id wins",
          try_or_sol("lww_merge", ("a", 5, "B"), ("b", 5, "A")),
          ("a", 5, "B"))

    # Ex 6
    print("\nExercise 6: converges")
    states = [{"a": 1}, {"b": 2}, {"a": 3}, {"c": 5}]
    check("converges across order", try_or_sol("converges", states), True)
    check("empty list", try_or_sol("converges", []), True)

    print(f"\n{'='*50}")
    total = passed + failed
    print(f"Results: {passed}/{total} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
