"""
Day 105: Mini-Project — Sorting Benchmark Harness

Days 99-104 built seven kinds of sort and asserted a lot of things about them.
This file does not re-explain any of them. It MEASURES them.

The harness loads each sibling day's module by path, runs every algorithm over
every input shape at every size, verifies each result, and reports medians. A
missing day is skipped, not fatal.

Three rules the harness enforces on itself, because a benchmark that lies is
worse than no benchmark at all:

  1. Verify before you time. An incorrect sort is not "fast".
  2. Identical input for every algorithm. Same seed, same list, fresh copy.
  3. Report the MEDIAN of repeated runs, never the mean. One GC pause moves a
     mean; it does not move a median.

Standard library only.
"""

import importlib.util
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DSA = HERE.parent


# ---------------------------------------------------------------------------
# Loading the sibling days
# ---------------------------------------------------------------------------
#
# Day directories are named `day-099`, which is not a legal Python identifier,
# so a normal import cannot reach them. Load by file path instead. Every one of
# those modules guards its demos behind `if __name__ == "__main__"`, so
# importing them produces no output and runs no benchmark of its own.

def load_day(day, filename):
    """Import a sibling day's module by path. Returns None if unavailable."""
    path = DSA / day / filename
    if not path.exists():
        return None
    name = f"_dsa_{day.replace('-', '_')}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:                     # reported, never swallowed
        del sys.modules[name]
        print(f"  [skip] {day}/{filename}: {type(exc).__name__}: {exc}")
        return None
    return module


# ---------------------------------------------------------------------------
# The registry
# ---------------------------------------------------------------------------
#
# `domain` is not decoration. counting_sort and radix_sort only accept
# non-negative integers; bucket_sort only accepts floats in [0, 1). Racing them
# against timsort on arbitrary data is not a fair fight, it is a category error
# — so the harness tracks what each algorithm is even allowed to see.

DOMAIN_ANY = "any"
DOMAIN_NONNEG_INT = "nonneg-int"
DOMAIN_UNIT_FLOAT = "unit-float"


class Algo:
    __slots__ = ("name", "day", "fn", "domain", "max_n")

    def __init__(self, name, day, fn, domain=DOMAIN_ANY, max_n=None):
        self.name = name
        self.day = day
        self.fn = fn
        self.domain = domain
        # `max_n` is for algorithms with a known linear recursion depth. Past it
        # they do not merely run slowly, they exhaust the interpreter stack.
        self.max_n = max_n


def build_registry():
    """Discover whichever sibling days are present. Order follows day order."""
    algos = []
    # Importing a module under test can change the interpreter out from under
    # the harness. Days 99 and 100 both call sys.setrecursionlimit(10**6) at
    # import time, which silently rewrites what "too deep to run" means for
    # every algorithm measured afterwards. Record it rather than be surprised.
    global RECURSION_LIMIT_AT_STARTUP
    RECURSION_LIMIT_AT_STARTUP = sys.getrecursionlimit()

    d99 = load_day("day-099", "comparison_sorts.py")
    if d99:
        algos.append(Algo("merge_sort", 99, d99.merge_sort))
        algos.append(Algo("heap_sort", 99, d99.heap_sort))
        algos.append(Algo("quicksort_random", 99, d99.quicksort_random))
        # First-element pivot: included precisely because it is the one that breaks.
        algos.append(Algo("quicksort_unsafe", 99, d99.quicksort_unsafe))

    d100 = load_day("day-100", "quicksort_deep.py")
    if d100:
        algos.append(Algo(
            "quicksort_median3", 100,
            lambda a, m=d100: m.quicksort(a, m.lomuto_partition, m.pivot_median_of_3)))
        algos.append(Algo("dual_pivot_quicksort", 100, d100.dual_pivot_quicksort))

    d101 = load_day("day-101", "noncomparison_sorts.py")
    if d101:
        algos.append(Algo("counting_sort", 101, d101.counting_sort, DOMAIN_NONNEG_INT))
        algos.append(Algo("radix_sort_lsd", 101, d101.radix_sort_lsd, DOMAIN_NONNEG_INT))
        algos.append(Algo("bucket_sort", 101, d101.bucket_sort, DOMAIN_UNIT_FLOAT))

    d102 = load_day("day-102", "external_sort.py")
    if d102:
        algos.append(Algo(
            "external_sort", 102,
            lambda a, m=d102: m.external_sort_inmemory(a, max(1, len(a) // 8))))

    d103 = load_day("day-103", "timsort.py")
    if d103:
        algos.append(Algo("timsort", 103, d103.timsort))

    d104 = load_day("day-104", "sorting_networks.py")
    if d104:
        algos.append(Algo("bitonic_sort", 104, d104.bitonic_sort))

    # The baseline everything is measured against: CPython's Timsort, in C.
    algos.append(Algo("sorted() [C]", 0, sorted))
    return algos


# ---------------------------------------------------------------------------
# Input shapes
# ---------------------------------------------------------------------------
#
# Shapes matter more than sizes. "n = 100k random ints" is one data point; the
# interesting question is which algorithms fall over on which STRUCTURE.

SHAPES = (
    "random",
    "sorted",
    "reverse",
    "all_equal",
    "few_unique",
    "nearly_sorted",
    "organ_pipe",
)


def make_shape(kind, n, seed=105):
    """
    Deterministic input generator. The same (kind, n, seed) always yields the
    same list — that determinism is what makes two runs comparable at all.

    Values are non-negative ints in [0, n) so the counting and radix sorts can
    be fed the same shapes as everything else.
    """
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
        for _ in range(max(1, n // 100)):          # ~1% of positions disturbed
            i, j = rng.randrange(n), rng.randrange(n)
            a[i], a[j] = a[j], a[i]
        return a
    if kind == "organ_pipe":
        half = n // 2
        return list(range(half)) + list(range(n - half - 1, -1, -1))
    raise ValueError(f"unknown shape {kind!r}")


def adapt(values, domain):
    """Project a shape into an algorithm's accepted domain, preserving order."""
    if domain in (DOMAIN_ANY, DOMAIN_NONNEG_INT):
        return list(values)
    if domain == DOMAIN_UNIT_FLOAT:
        hi = (max(values) + 1) if values else 1
        return [v / hi for v in values]
    raise ValueError(f"unknown domain {domain!r}")


# ---------------------------------------------------------------------------
# Correctness — checked BEFORE anything is timed
# ---------------------------------------------------------------------------

def is_sorted(seq):
    return all(seq[i] <= seq[i + 1] for i in range(len(seq) - 1))


def same_multiset(a, b):
    """
    Did the sort keep exactly the elements it was given?

    Sorted-ness alone is not correctness: `return []` is perfectly sorted, and
    so is `return [min(a)] * len(a)`. This is the check that catches those, and
    it is the reason a fast wrong answer cannot win a benchmark here.
    """
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


def verify(fn, data):
    """Return a list of problems with fn(data). An empty list means correct."""
    try:
        out = fn(list(data))
    except RecursionError:
        return ["RecursionError"]
    except Exception as exc:
        return [f"{type(exc).__name__}"]
    problems = []
    if not is_sorted(out):
        problems.append("not sorted")
    if not same_multiset(data, out):
        problems.append("elements changed")
    return problems


# ---------------------------------------------------------------------------
# Stability
# ---------------------------------------------------------------------------

class KeyOnly:
    """
    Compares by `key` alone; `tag` rides along untouched.

    Using plain `(key, index)` tuples here would be a classic self-deceiving
    test: tuple comparison falls through to the index, so even an unstable sort
    would come out looking perfectly stable.
    """
    __slots__ = ("key", "tag")

    def __init__(self, key, tag):
        self.key = key
        self.tag = tag

    # Returning NotImplemented against a foreign type is what lets day-104's
    # padding sentinel answer instead — Python then tries the reflected
    # operation. Raising here would make an algorithm look untestable when it
    # is merely padding its input.
    def __lt__(self, other):
        if not isinstance(other, KeyOnly):
            return NotImplemented
        return self.key < other.key

    def __gt__(self, other):
        if not isinstance(other, KeyOnly):
            return NotImplemented
        return self.key > other.key

    def __le__(self, other):
        if not isinstance(other, KeyOnly):
            return NotImplemented
        return self.key <= other.key

    def __ge__(self, other):
        if not isinstance(other, KeyOnly):
            return NotImplemented
        return self.key >= other.key

    def __eq__(self, other):
        return isinstance(other, KeyOnly) and self.key == other.key

    def __repr__(self):
        return f"({self.key},{self.tag})"


def measure_stability(fn, n=60, seed=105):
    """Return True/False, or None if the algorithm cannot accept these values."""
    rng = random.Random(seed)
    items = [KeyOnly(rng.randrange(5), i) for i in range(n)]
    try:
        out = fn(list(items))
    except Exception:
        return None
    if len(out) != n:
        return None
    last = {}
    for item in out:
        if item.key in last and item.tag < last[item.key]:
            return False
        last[item.key] = item.tag
    return True


# ---------------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------------

RESULT_CRASHED = "crash"
RESULT_SKIPPED = "skip"

# Set by build_registry() before any sibling day is imported.
RECURSION_LIMIT_AT_STARTUP = None


def median(xs):
    """Median of a list of numbers. Robust to the one slow run GC handed you."""
    if not xs:
        raise ValueError("median of empty sequence")
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2


def time_median(fn, data, repeats=3, warmup=1):
    """
    Median wall-clock seconds over `repeats` runs, after `warmup` untimed runs.

    Warm-up exists because the first call pays for allocator growth, method
    caches, and branch predictors that have never seen this code. Timing it
    measures the interpreter waking up, not the algorithm.

    `perf_counter` is the right clock: monotonic, highest available resolution,
    and it includes sleep — which is what a user actually experiences.
    """
    for _ in range(warmup):
        fn(list(data))
    samples = []
    for _ in range(repeats):
        payload = list(data)                     # copying is NOT timed
        start = time.perf_counter()
        fn(payload)
        samples.append(time.perf_counter() - start)
    return median(samples)


def rank_by(results):
    """
    Names ordered fastest-first. Ties break by name so the ranking is stable
    across runs — an unstable ranking makes two reports impossible to diff.

    Entries whose value is not a number (crashed, skipped) sort last, by name.
    """
    numeric = [(v, k) for k, v in results.items() if isinstance(v, (int, float))]
    other = sorted(k for k, v in results.items() if not isinstance(v, (int, float)))
    return [k for _v, k in sorted(numeric, key=lambda p: (p[0], p[1]))] + other


# ---------------------------------------------------------------------------
# The benchmark
# ---------------------------------------------------------------------------

def benchmark(algos, shape, n, repeats=3):
    """Run one shape at one size across all algorithms. Returns {name: value}."""
    base = make_shape(shape, n)
    out = {}
    for algo in algos:
        if algo.max_n is not None and n > algo.max_n:
            out[algo.name] = RESULT_SKIPPED
            continue
        data = adapt(base, algo.domain)
        problems = verify(algo.fn, data)
        if problems:
            out[algo.name] = RESULT_CRASHED if "Error" in problems[0] else problems[0]
            continue
        out[algo.name] = time_median(algo.fn, data, repeats=repeats)
    return out


def print_table(algos, results_by_shape, n):
    names = [a.name for a in algos]
    width = max(len(x) for x in names) + 1
    header = f"  {'algorithm':<{width}}" + "".join(f"{s:>15}" for s in results_by_shape)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for name in names:
        row = f"  {name:<{width}}"
        for shape in results_by_shape:
            v = results_by_shape[shape].get(name)
            if isinstance(v, float):
                row += f"{v * 1000:>14.3f}m"
            else:
                row += f"{str(v):>15}"
        print(row)
    print(f"  (median ms over repeats, n={n})")


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_discovery():
    print("=" * 78)
    print("DEMO 1: which days are present")
    print("=" * 78)
    algos = build_registry()
    print()
    for a in algos:
        origin = f"day-{a.day:03d}" if a.day else "stdlib"
        print(f"  {a.name:<22} {origin:<10} domain={a.domain}")
    print(f"\n  {len(algos)} algorithms discovered")

    now = sys.getrecursionlimit()
    if now != RECURSION_LIMIT_AT_STARTUP:
        print(f"\n  !! recursion limit changed by import: "
              f"{RECURSION_LIMIT_AT_STARTUP} -> {now}")
        print("     day-099/comparison_sorts.py:12 and day-100/quicksort_deep.py:12")
        print("     both call sys.setrecursionlimit(10**6) at module scope. Loading")
        print("     the code under test mutated the environment it is measured in.")
        print("     That is a benchmark-hygiene bug worth naming: a deep-recursion")
        print("     failure that WOULD occur at the default limit will not occur")
        print("     here, so the numbers below describe a machine no user has.")
    return algos


def demo_correctness(algos):
    print("\n" + "=" * 78)
    print("DEMO 2: correctness first — nothing is timed until it is right")
    print("=" * 78)
    print()
    bad = 0
    for a in algos:
        issues = []
        for shape in SHAPES:
            for n in (0, 1, 2, 33, 257):
                data = adapt(make_shape(shape, n), a.domain)
                problems = verify(a.fn, data)
                if problems:
                    issues.append(f"{shape}/n={n}: {','.join(problems)}")
        if issues:
            bad += 1
            print(f"  {a.name:<22} {len(issues)} failures, e.g. {issues[0]}")
        else:
            print(f"  {a.name:<22} correct on all {len(SHAPES)} shapes x 5 sizes")
    print(f"\n  algorithms with failures: {bad}")


def demo_stability(algos):
    print("\n" + "=" * 78)
    print("DEMO 3: measured stability (not claimed — measured)")
    print("=" * 78)
    print()
    for a in algos:
        verdict = measure_stability(a.fn)
        label = {True: "STABLE", False: "not stable", None: "n/a"}[verdict]
        print(f"  {a.name:<22} {label}")
    print("\n  'n/a' means the algorithm cannot accept a compare-only object at")
    print("  all: the integer-domain sorts READ the values (as array indices or")
    print("  digits), they do not merely compare them. Stability is not even a")
    print("  well-posed question for an input they cannot represent.")


def demo_shapes(algos, n=2000):
    print("\n" + "=" * 78)
    print(f"DEMO 4: shape matters more than size (n={n})")
    print("=" * 78)
    print()
    results = {shape: benchmark(algos, shape, n) for shape in SHAPES}
    print_table(algos, results, n)
    return results


def demo_ranking(results):
    print("\n" + "=" * 78)
    print("DEMO 5: rankings per shape")
    print("=" * 78)
    for shape, res in results.items():
        order = rank_by(res)
        print(f"\n  {shape:<14} {' > '.join(order[:4])}")
    print("\n  Read the ORDER, not the milliseconds. The absolute numbers are a")
    print("  fact about this machine at this moment; the ordering is a fact")
    print("  about the algorithms.")


def demo_growth(algos, sizes=(250, 500, 1000, 2000)):
    print("\n" + "=" * 78)
    print("DEMO 6: growth — does the measured curve match the claimed one?")
    print("=" * 78)
    print()
    header = (f"  {'algorithm':<22}" + "".join(f"{n:>10}" for n in sizes)
              + "   ratio(last/first)")
    print(header)
    print("  " + "-" * (len(header) - 2))
    for a in algos:
        row = f"  {a.name:<22}"
        vals = []
        for n in sizes:
            data = adapt(make_shape("random", n), a.domain)
            if verify(a.fn, data):
                row += f"{'crash':>10}"
                vals.append(None)
                continue
            t = time_median(a.fn, data, repeats=3)
            vals.append(t)
            row += f"{t * 1000:>9.2f}m"
        if vals[0] and vals[-1]:
            row += f"{vals[-1] / vals[0]:>16.1f}x"
        print(row)
    factor = sizes[-1] / sizes[0]
    print(f"\n  n grew {factor:.0f}x. An O(n log n) sort should grow about "
          f"{factor * 1.4:.0f}x; O(n^2) about {factor ** 2:.0f}x; O(n) about "
          f"{factor:.0f}x.")


def demo_pathology(algos):
    print("\n" + "=" * 78)
    print("DEMO 7: the pathological cases, measured rather than asserted")
    print("=" * 78)
    print()
    for n in (250, 1000):
        res = benchmark(algos, "sorted", n)
        print(f"  n={n} ALREADY SORTED input:")
        for name in rank_by(res):
            v = res[name]
            shown = f"{v * 1000:.3f} ms" if isinstance(v, float) else str(v)
            print(f"     {name:<22} {shown}")
        print()
    print("  quicksort_unsafe takes a first-element pivot, so ALREADY SORTED is")
    print("  its worst case: it is among the slowest here, while being one of the")
    print("  fastest on random input in DEMO 6. One algorithm, opposite verdicts,")
    print("  same size — which is the entire argument for benchmarking by shape.")
    print()
    print("  What it does NOT do is raise RecursionError, even though it recurses")
    print("  once per element. Days 99 and 100 raised the recursion limit to 10**6")
    print("  at import (see DEMO 1), so the stack failure a user would hit at the")
    print("  default limit of 1000 cannot happen inside this harness. Measured, not")
    print("  assumed — the first draft of this file asserted the crash and was wrong.")


def main():
    algos = demo_discovery()
    demo_correctness(algos)
    demo_stability(algos)
    results = demo_shapes(algos)
    demo_ranking(results)
    demo_growth(algos)
    demo_pathology(algos)


if __name__ == "__main__":
    main()
