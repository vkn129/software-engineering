"""
Day 105 Practice: Sorting Benchmark Harness

7 exercises. Implement the TODOs, then run: python3 practice.py

Every test here asserts CORRECTNESS or an ORDERING property. None of them
assert a wall-clock number: timings vary with machine, load, and thermal state,
so a test that pins one is a test that fails for reasons nobody can fix.
"""

import random


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: is_sorted
# ---------------------------------------------------------------------------

def is_sorted(seq):
    """Return True iff seq is non-decreasing. Empty and single-element: True."""
    # TODO: compare each adjacent pair
    pass


def _sol_is_sorted(seq):
    return all(seq[i] <= seq[i + 1] for i in range(len(seq) - 1))


# ---------------------------------------------------------------------------
# Exercise 2: same_multiset
# ---------------------------------------------------------------------------

def same_multiset(a, b):
    """
    Return True iff a and b contain the same elements with the same
    multiplicities, order ignored.

    Sorted-ness alone is NOT correctness: `return []` is sorted, and so is
    `[min(a)] * len(a)`. This is the check that catches a fast wrong answer.
    """
    # TODO: count elements in a, then decrement for each element of b
    pass


def _sol_same_multiset(a, b):
    if len(a) != len(b):
        return False
    counts = {}
    for x in a:
        counts[x] = counts.get(x, 0) + 1
    for x in b:
        if x not in counts:
            return False
        counts[x] -= 1
        if counts[x] == 0:
            del counts[x]
    return not counts


# ---------------------------------------------------------------------------
# Exercise 3: verify_sort
# ---------------------------------------------------------------------------

def verify_sort(fn, data):
    """
    Run fn(data) and return a list of problems. Empty list means correct.

    Emit exactly these strings, in this order when both apply:
      "not sorted"        output is not non-decreasing
      "elements changed"  output is not a permutation of the input

    An exception becomes a single-element list holding the exception's class
    name, e.g. ["RecursionError"]. A benchmark that lets a crash through as a
    fast time is worse than no benchmark.
    """
    # TODO: guard the call, then apply both checks
    pass


def _sol_verify_sort(fn, data):
    try:
        out = fn(list(data))
    except Exception as exc:
        return [type(exc).__name__]
    problems = []
    if not _sol_is_sorted(out):
        problems.append("not sorted")
    if not _sol_same_multiset(data, out):
        problems.append("elements changed")
    return problems


# ---------------------------------------------------------------------------
# Exercise 4: make_shape
# ---------------------------------------------------------------------------

SHAPES = ("random", "sorted", "reverse", "all_equal",
          "few_unique", "nearly_sorted", "organ_pipe")


def make_shape(kind, n, seed=105):
    """
    Deterministic input generator returning a list of n non-negative ints.

      random         n draws from [0, n)
      sorted         0, 1, ..., n-1
      reverse        n-1, ..., 1, 0
      all_equal      n copies of n // 2
      few_unique     n draws from [0, 4)
      nearly_sorted  range(n) with max(1, n // 100) random swaps applied
      organ_pipe     up then down: range(n//2) + range(n - n//2 - 1, -1, -1)

    Same (kind, n, seed) must always give the same list — that determinism is
    what makes two benchmark runs comparable at all. Raise ValueError on an
    unknown kind. n <= 0 returns [].
    """
    # TODO: build each shape from a random.Random(seed)
    pass


def _sol_make_shape(kind, n, seed=105):
    rng = random.Random(seed)
    if n <= 0:
        return []
    if kind == "random":
        return [rng.randrange(n) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n - 1, -1, -1))
    if kind == "all_equal":
        return [n // 2] * n
    if kind == "few_unique":
        return [rng.randrange(4) for _ in range(n)]
    if kind == "nearly_sorted":
        a = list(range(n))
        for _ in range(max(1, n // 100)):
            i, j = rng.randrange(n), rng.randrange(n)
            a[i], a[j] = a[j], a[i]
        return a
    if kind == "organ_pipe":
        half = n // 2
        return list(range(half)) + list(range(n - half - 1, -1, -1))
    raise ValueError(f"unknown shape {kind!r}")


# ---------------------------------------------------------------------------
# Exercise 5: stability of a result
# ---------------------------------------------------------------------------

class KeyOnly:
    """
    Compares by `key` alone; `tag` rides along untouched.

    Measuring stability with plain `(key, index)` tuples is a classic
    self-deceiving test: tuple comparison falls through to the index, so even an
    unstable sort comes out looking perfectly stable. The comparison has to
    ignore the tag for the question to mean anything.
    """
    __slots__ = ("key", "tag")

    def __init__(self, key, tag):
        self.key = key
        self.tag = tag

    def __lt__(self, other):
        return self.key < other.key

    def __gt__(self, other):
        return self.key > other.key

    def __le__(self, other):
        return self.key <= other.key

    def __ge__(self, other):
        return self.key >= other.key

    def __eq__(self, other):
        return isinstance(other, KeyOnly) and self.key == other.key

    def __repr__(self):
        return f"({self.key},{self.tag})"


def is_stable_result(result):
    """
    Given a list of KeyOnly already sorted by key, return True iff within every
    key group the tags appear in ascending order — i.e. equal elements kept
    their input order. This checks only the tie-break.
    """
    # TODO: track the last tag seen for each key
    pass


def _sol_is_stable_result(result):
    last = {}
    for item in result:
        if item.key in last and item.tag < last[item.key]:
            return False
        last[item.key] = item.tag
    return True


# ---------------------------------------------------------------------------
# Exercise 6: median
# ---------------------------------------------------------------------------

def median(xs):
    """
    Median of a list of numbers. Even length averages the middle two.
    Raise ValueError on empty input.

    The harness reports medians rather than means because one GC pause moves a
    mean and does not move a median.
    """
    # TODO: sort a copy, then take the middle
    pass


def _sol_median(xs):
    if not xs:
        raise ValueError("median of empty sequence")
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


# ---------------------------------------------------------------------------
# Exercise 7: rank_by
# ---------------------------------------------------------------------------

def rank_by(results):
    """
    `results` maps name -> measurement. Return the names ordered
    smallest-measurement-first.

    Two rules that matter more than they look:
      * ties break by NAME, so the ranking is identical across runs — an
        unstable ranking makes two reports impossible to diff.
      * entries whose value is not a number (a crash marker, a skip marker)
        sort LAST, among themselves by name. A crash is not a fast result.
    """
    # TODO: partition numeric from non-numeric, sort each, concatenate
    pass


def _sol_rank_by(results):
    numeric = [(v, k) for k, v in results.items() if isinstance(v, (int, float))]
    other = sorted(k for k, v in results.items() if not isinstance(v, (int, float)))
    return [k for _v, k in sorted(numeric, key=lambda p: (p[0], p[1]))] + other


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: is_sorted")
    check("empty", try_or_sol("is_sorted", []), True)
    check("single", try_or_sol("is_sorted", [7]), True)
    check("ascending", try_or_sol("is_sorted", [1, 2, 3]), True)
    check("equal elements count as sorted",
          try_or_sol("is_sorted", [2, 2, 2]), True)
    check("descending", try_or_sol("is_sorted", [3, 2, 1]), False)
    check("one inversion at the end",
          try_or_sol("is_sorted", [1, 2, 3, 0]), False)

    print("\nExercise 2: same_multiset")
    check("same elements reordered",
          try_or_sol("same_multiset", [1, 2, 3], [3, 1, 2]), True)
    check("both empty", try_or_sol("same_multiset", [], []), True)
    check("dropped element",
          try_or_sol("same_multiset", [1, 2, 3], [1, 2]), False)
    check("invented element",
          try_or_sol("same_multiset", [1, 2], [1, 2, 3]), False)
    # Multiplicity is the point: same SET, different multiset.
    check("duplicate count matters",
          try_or_sol("same_multiset", [1, 1, 2], [1, 2, 2]), False)
    check("substituted element",
          try_or_sol("same_multiset", [1, 2, 3], [1, 2, 9]), False)

    print("\nExercise 3: verify_sort")
    check("a correct sort has no problems",
          try_or_sol("verify_sort", sorted, [3, 1, 2]), [])
    check("identity function is not a sort",
          try_or_sol("verify_sort", lambda a: a, [3, 1, 2]), ["not sorted"])
    # Sorted AND wrong: returning [] is perfectly ordered and loses everything.
    check("empty output caught by the multiset check",
          try_or_sol("verify_sort", lambda a: [], [3, 1, 2]),
          ["elements changed"])
    check("constant output caught",
          try_or_sol("verify_sort", lambda a: [min(a)] * len(a), [3, 1, 2]),
          ["elements changed"])
    check("both problems reported together",
          try_or_sol("verify_sort", lambda a: [9, 0], [3, 1, 2]),
          ["not sorted", "elements changed"])
    check("exception becomes its class name",
          try_or_sol("verify_sort", lambda a: 1 / 0, [3, 1, 2]),
          ["ZeroDivisionError"])
    src = [3, 1, 2]
    try_or_sol("verify_sort", sorted, src)
    check("caller's data not mutated", src, [3, 1, 2])

    print("\nExercise 4: make_shape")
    check("sorted shape", try_or_sol("make_shape", "sorted", 5), [0, 1, 2, 3, 4])
    check("reverse shape", try_or_sol("make_shape", "reverse", 5), [4, 3, 2, 1, 0])
    check("all_equal shape", try_or_sol("make_shape", "all_equal", 4), [2, 2, 2, 2])
    check("organ_pipe rises then falls",
          try_or_sol("make_shape", "organ_pipe", 8), [0, 1, 2, 3, 3, 2, 1, 0])
    check("n=0 is empty", try_or_sol("make_shape", "random", 0), [])
    for kind in SHAPES:
        got = try_or_sol("make_shape", kind, 50)
        check(f"{kind} has length n", len(got), 50)
    check("few_unique has at most 4 distinct values",
          len(set(try_or_sol("make_shape", "few_unique", 200))) <= 4, True)
    check("nearly_sorted is a permutation of range(n)",
          sorted(try_or_sol("make_shape", "nearly_sorted", 100)),
          list(range(100)))
    # Determinism is the whole contract: two runs must be comparable.
    check("same seed gives the same list",
          try_or_sol("make_shape", "random", 40, 7),
          try_or_sol("make_shape", "random", 40, 7))
    check("different seed gives a different list",
          try_or_sol("make_shape", "random", 40, 7)
          == try_or_sol("make_shape", "random", 40, 8), False)
    try:
        try_or_sol("make_shape", "spiral", 10)
        check("unknown shape raises", False, True)
    except ValueError:
        check("unknown shape raises", True, True)

    print("\nExercise 5: is_stable_result")
    stable = [KeyOnly(1, 0), KeyOnly(1, 5), KeyOnly(2, 2), KeyOnly(2, 9)]
    check("tags ascending within each key",
          try_or_sol("is_stable_result", stable), True)
    unstable = [KeyOnly(1, 5), KeyOnly(1, 0), KeyOnly(2, 2)]
    check("swapped equal keys detected",
          try_or_sol("is_stable_result", unstable), False)
    check("empty result", try_or_sol("is_stable_result", []), True)
    check("all keys distinct is trivially stable",
          try_or_sol("is_stable_result",
                     [KeyOnly(1, 9), KeyOnly(2, 0), KeyOnly(3, 4)]), True)
    # Non-adjacent groups: the check must be per-key, not global.
    check("interleaved keys tracked separately",
          try_or_sol("is_stable_result",
                     [KeyOnly(1, 0), KeyOnly(1, 1), KeyOnly(2, 0), KeyOnly(2, 1)]),
          True)
    # sorted() is stable, so sorting KeyOnly by key must preserve tag order.
    items = [KeyOnly(k, i) for i, k in enumerate([2, 1, 2, 1, 3, 1] * 5)]
    check("stdlib sorted() measures as stable",
          try_or_sol("is_stable_result", sorted(items)), True)
    # Reversing each key group is the counter-example that must NOT pass.
    reversed_groups = sorted(items, key=lambda it: (it.key, -it.tag))
    check("deliberately destabilised order is caught",
          try_or_sol("is_stable_result", reversed_groups), False)

    print("\nExercise 6: median")
    check("odd length", try_or_sol("median", [3, 1, 2]), 2)
    check("even length averages the middle two",
          try_or_sol("median", [1, 2, 3, 4]), 2.5)
    check("single value", try_or_sol("median", [5]), 5)
    check("unsorted input", try_or_sol("median", [9, 1, 5]), 5)
    # The reason medians are used at all: one huge outlier must not move it.
    check("outlier does not move the median",
          try_or_sol("median", [1.0, 1.1, 1.2, 1.1, 900.0]), 1.1)
    try:
        try_or_sol("median", [])
        check("empty raises", False, True)
    except ValueError:
        check("empty raises", True, True)

    print("\nExercise 7: rank_by")
    check("fastest first",
          try_or_sol("rank_by", {"a": 3.0, "b": 1.0, "c": 2.0}), ["b", "c", "a"])
    check("ties break by name",
          try_or_sol("rank_by", {"z": 1.0, "a": 1.0, "m": 1.0}), ["a", "m", "z"])
    check("crash markers sort last",
          try_or_sol("rank_by", {"a": "crash", "b": 5.0}), ["b", "a"])
    check("several non-numeric entries ordered by name",
          try_or_sol("rank_by", {"z": "skip", "a": "crash", "m": 2.0}),
          ["m", "a", "z"])
    check("empty input", try_or_sol("rank_by", {}), [])
    check("all crashed", try_or_sol("rank_by", {"b": "crash", "a": "crash"}),
          ["a", "b"])
    # Ranking must be a pure function of the mapping — two calls, one answer.
    same = {"a": 2.0, "b": 2.0, "c": 1.0}
    check("ranking is reproducible",
          try_or_sol("rank_by", same), try_or_sol("rank_by", same))

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
