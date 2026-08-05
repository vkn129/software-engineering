"""
Day 158 Practice: Skip List with Span Pointers

6 exercises on skip-list internals + rank/range queries. Run: python practice.py
"""

import random


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Provided: minimal skip list (no spans) for exercises 4-6
# ===================================================================

MAX_LEVEL = 16
P = 0.5


class Node:
    __slots__ = ("key", "forward")

    def __init__(self, key, level):
        self.key = key
        self.forward = [None] * (level + 1)


def make_skiplist():
    return {"header": Node(None, MAX_LEVEL), "level": 0, "length": 0}


def _random_level():
    lvl = 0
    while random.random() < P and lvl < MAX_LEVEL:
        lvl += 1
    return lvl


def sl_insert(sl, key):
    update = [None] * (MAX_LEVEL + 1)
    x = sl["header"]
    for i in range(sl["level"], -1, -1):
        while x.forward[i] is not None and x.forward[i].key < key:
            x = x.forward[i]
        update[i] = x
    lvl = _random_level()
    if lvl > sl["level"]:
        for i in range(sl["level"] + 1, lvl + 1):
            update[i] = sl["header"]
        sl["level"] = lvl
    node = Node(key, lvl)
    for i in range(lvl + 1):
        node.forward[i] = update[i].forward[i]
        update[i].forward[i] = node
    sl["length"] += 1


# ===================================================================
# Exercise 1: random_level
# ===================================================================
# Geometric distribution: keep flipping coin while heads. Cap at MAX_LEVEL.
def random_level(max_level, p):
    """Return the level for a new node."""
    # TODO
    pass


def _sol_random_level(max_level, p):
    lvl = 0
    while random.random() < p and lvl < max_level:
        lvl += 1
    return lvl


# ===================================================================
# Exercise 2: skiplist_contains
# ===================================================================
# Search top-down: drop down when next key >= target.
def skiplist_contains(sl, key):
    """Return True iff key is present."""
    # TODO
    pass


def _sol_skiplist_contains(sl, key):
    x = sl["header"]
    for i in range(sl["level"], -1, -1):
        while x.forward[i] is not None and x.forward[i].key < key:
            x = x.forward[i]
    x = x.forward[0]
    return x is not None and x.key == key


# ===================================================================
# Exercise 3: skiplist_to_list
# ===================================================================
# Walk L0 and return all keys in sorted order.
def skiplist_to_list(sl):
    """Return list of keys in ascending order."""
    # TODO
    pass


def _sol_skiplist_to_list(sl):
    out = []
    x = sl["header"].forward[0]
    while x is not None:
        out.append(x.key)
        x = x.forward[0]
    return out


# ===================================================================
# Exercise 4: skiplist_range
# ===================================================================
# Return all keys with lo <= key <= hi.
def skiplist_range(sl, lo, hi):
    """Sorted list of keys in [lo, hi]."""
    # TODO
    pass


def _sol_skiplist_range(sl, lo, hi):
    out = []
    x = sl["header"]
    for i in range(sl["level"], -1, -1):
        while x.forward[i] is not None and x.forward[i].key < lo:
            x = x.forward[i]
    x = x.forward[0]
    while x is not None and x.key <= hi:
        out.append(x.key)
        x = x.forward[0]
    return out


# ===================================================================
# Exercise 5: expected_height
# ===================================================================
# Theoretical expected max level for n nodes with promotion prob p:
# height ≈ log_{1/p}(n). Return as int (floor).
import math


def expected_height(n, p):
    """Floor of log base (1/p) of n. n=1 → 0."""
    # TODO
    pass


def _sol_expected_height(n, p):
    if n <= 1:
        return 0
    return int(math.log(n) / math.log(1 / p))


# ===================================================================
# Exercise 6: skiplist_delete
# ===================================================================
# Delete a key. Return True if deleted, False if absent.
def skiplist_delete(sl, key):
    """Remove key from skip list."""
    # TODO
    pass


def _sol_skiplist_delete(sl, key):
    update = [None] * (MAX_LEVEL + 1)
    x = sl["header"]
    for i in range(sl["level"], -1, -1):
        while x.forward[i] is not None and x.forward[i].key < key:
            x = x.forward[i]
        update[i] = x
    target = x.forward[0]
    if target is None or target.key != key:
        return False
    for i in range(sl["level"] + 1):
        if update[i].forward[i] == target:
            update[i].forward[i] = target.forward[i]
    while sl["level"] > 0 and sl["header"].forward[sl["level"]] is None:
        sl["level"] -= 1
    sl["length"] -= 1
    return True


# ===================================================================
# Test runner
# ===================================================================
def run_tests():
    passed = 0
    failed = 0

    def check(name, cond):
        nonlocal passed, failed
        if cond:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            failed += 1

    random.seed(0)

    print("Exercise 1: random_level")
    levels = [try_or_sol("random_level", 16, 0.5) for _ in range(2000)]
    check("all in range", all(0 <= L <= 16 for L in levels))
    # Half should be exactly 0 (failed first coin flip)
    zeros = sum(1 for L in levels if L == 0)
    check(f"~50% are zero (got {zeros}/2000)", 850 < zeros < 1150)

    print("\nExercise 2: skiplist_contains")
    sl = make_skiplist()
    for k in [5, 2, 8, 1, 9, 3, 7]:
        sl_insert(sl, k)
    check("5 present", try_or_sol("skiplist_contains", sl, 5) is True)
    check("4 absent", try_or_sol("skiplist_contains", sl, 4) is False)
    check("9 present", try_or_sol("skiplist_contains", sl, 9) is True)

    print("\nExercise 3: skiplist_to_list")
    check("sorted", try_or_sol("skiplist_to_list", sl) == [1, 2, 3, 5, 7, 8, 9])

    print("\nExercise 4: skiplist_range")
    check("[3,8]", try_or_sol("skiplist_range", sl, 3, 8) == [3, 5, 7, 8])
    check("[0,2]", try_or_sol("skiplist_range", sl, 0, 2) == [1, 2])
    check("[10,20]", try_or_sol("skiplist_range", sl, 10, 20) == [])

    print("\nExercise 5: expected_height")
    check("n=1", try_or_sol("expected_height", 1, 0.5) == 0)
    check("n=1024 p=0.5", try_or_sol("expected_height", 1024, 0.5) == 10)
    check("n=10000 p=0.25", try_or_sol("expected_height", 10000, 0.25) == 6)

    print("\nExercise 6: skiplist_delete")
    check("delete 5", try_or_sol("skiplist_delete", sl, 5) is True)
    check("5 gone", _sol_skiplist_contains(sl, 5) is False)
    check("delete missing", try_or_sol("skiplist_delete", sl, 42) is False)
    check("remaining order", _sol_skiplist_to_list(sl) == [1, 2, 3, 7, 8, 9])

    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
