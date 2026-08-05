"""
Day 161 Practice: Parallel Merge (k-way merge with partitioning)

6 exercises. Implement TODOs, then run: python practice.py

Exercise 1 is the serial baseline. Exercise 2 is co_rank — the whole idea.
Exercise 3 turns co-ranks into disjoint jobs. Exercise 4 assembles the parallel
merge. Exercises 5-6 generalise to k runs, where duplicates get dangerous.

No test here times anything. The GIL makes wall-clock meaningless in CPython;
what is testable is correctness, disjointness, and work/span.
"""

import math
from bisect import bisect_left, bisect_right


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
# Exercise 1: serial merge (the O(n)-span baseline)
# ---------------------------------------------------------------------------

def serial_merge(a, b):
    """
    Merge two sorted lists. Must be STABLE with `a` winning ties, so it agrees
    with co_rank's convention — otherwise chunk boundaries and chunk contents
    disagree and elements move between chunks.
    """
    # TODO: implement
    pass


def _sol_serial_merge(a, b):
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:      # <= not < : ties go to `a`, matching co_rank
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


# ---------------------------------------------------------------------------
# Exercise 2: co_rank — the binary search that makes merging parallel
# ---------------------------------------------------------------------------

def co_rank(k, a, b):
    """
    Of the first k elements of merge(a, b), how many came from `a`?

    Return i (with j = k - i) satisfying
        a[i-1] <= b[j]   and   b[j-1] < a[i]
    using the obvious conventions when i or j hits 0 or the end.

    Search i over [max(0, k - len(b)), min(k, len(a))] — NOT [0, len(a)], or
    j = k - i leaves b. O(log min(m, n)) comparisons, O(1) space.
    """
    # TODO: implement by binary search
    pass


def _sol_co_rank(k, a, b):
    m, n = len(a), len(b)
    lo = max(0, k - n)
    hi = min(k, m)
    while True:
        i = (lo + hi) // 2
        j = k - i
        if i > 0 and j < n and a[i - 1] > b[j]:
            hi = i - 1          # took too much from a
        elif j > 0 and i < m and b[j - 1] >= a[i]:
            lo = i + 1          # took too little from a
        else:
            return i


# ---------------------------------------------------------------------------
# Exercise 3: merge-path partition
# ---------------------------------------------------------------------------

def merge_path_partition(a, b, parts):
    """
    Split the OUTPUT into `parts` contiguous chunks; return, per chunk, the
    slices of a and b that produce it:  [((a_lo,a_hi), (b_lo,b_hi)), ...]

    The a-slices must tile a exactly and the b-slices must tile b exactly —
    that gap-free, overlap-free tiling is what makes the merge parallel.
    """
    # TODO: implement using co_rank at each chunk boundary
    pass


def _sol_merge_path_partition(a, b, parts):
    total = len(a) + len(b)
    parts = max(1, min(parts, total)) if total else 1
    bounds = [total * t // parts for t in range(parts + 1)]
    ranks = [_sol_co_rank(k, a, b) for k in bounds]
    return [((ranks[t], ranks[t + 1]),
             (bounds[t] - ranks[t], bounds[t + 1] - ranks[t + 1]))
            for t in range(parts)]


# ---------------------------------------------------------------------------
# Exercise 4: the parallel merge itself
# ---------------------------------------------------------------------------

def partitioned_merge(a, b, parts):
    """
    Merge a and b by partitioning into `parts` chunks, merging each chunk
    independently, then concatenating. Must equal serial_merge(a, b).

    In a real runtime the per-chunk merges run on separate cores. Here they run
    in a loop — the point is that they COULD, because no chunk reads another
    chunk's data.
    """
    # TODO: implement
    pass


def _sol_partitioned_merge(a, b, parts):
    out = []
    for (i0, i1), (j0, j1) in _sol_merge_path_partition(a, b, parts):
        out.extend(_sol_serial_merge(a[i0:i1], b[j0:j1]))
    return out


# ---------------------------------------------------------------------------
# Exercise 5: k-way splitter (multiseq_partition)
# ---------------------------------------------------------------------------

def multiseq_partition(runs, r):
    """
    Cut k sorted runs at a consistent global rank r: return an index vector
    with sum == r such that every element before a cut is <= every element
    after.

    Find v = smallest value with sum(bisect_right(run, v)) >= r. Then
    bisect_left gives a prefix shorter than r, and the entire shortfall is made
    of elements EQUAL to v — hand them out by a fixed rule (run order). Get
    that rule wrong and you duplicate or drop elements while the output stays
    sorted, so nothing catches it.
    """
    # TODO: implement
    pass


def _sol_multiseq_partition(runs, r):
    k = len(runs)
    nonempty = [x for x in runs if x]
    if r == 0 or not nonempty:
        return [0] * k
    lo = min(x[0] for x in nonempty)
    hi = max(x[-1] for x in nonempty)
    while lo < hi:
        v = (lo + hi) // 2
        if sum(bisect_right(x, v) for x in runs) >= r:
            hi = v
        else:
            lo = v + 1
    v = lo
    idx = [bisect_left(x, v) for x in runs]
    need = r - sum(idx)          # every one of these equals v
    for t, run in enumerate(runs):
        if need == 0:
            break
        take = min(bisect_right(run, v) - idx[t], need)
        idx[t] += take
        need -= take
    return idx


# ---------------------------------------------------------------------------
# Exercise 6: parallelism of a merge
# ---------------------------------------------------------------------------

def merge_parallelism(m, n, workers):
    """
    Return work // span for a merge-path parallel merge, counting comparisons:
        search = ceil(log2(min(m,n) + 1)) + 1
        work   = (m + n) + (workers + 1) * search
        span   = search + ceil((m + n) / workers)
    Return 0 if m + n == 0.

    This is the number that survives leaving CPython: work and span are
    properties of the algorithm; wall-clock is a property of the interpreter.
    """
    # TODO: implement
    pass


def _sol_merge_parallelism(m, n, workers):
    total = m + n
    if total == 0:
        return 0
    search = math.ceil(math.log2(min(m, n) + 1)) + 1
    work = total + (workers + 1) * search
    span = search + math.ceil(total / workers)
    return work // span


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

    print("Exercise 1: serial_merge")
    check("interleaved", try_or_sol("serial_merge", [1, 3, 5], [2, 4, 6]),
          [1, 2, 3, 4, 5, 6])
    check("empty a", try_or_sol("serial_merge", [], [2, 4]), [2, 4])
    check("empty both", try_or_sol("serial_merge", [], []), [])
    check("all duplicates", try_or_sol("serial_merge", [2, 2], [2, 2]),
          [2, 2, 2, 2])
    check("disjoint ranges", try_or_sol("serial_merge", [1, 2], [8, 9]),
          [1, 2, 8, 9])

    print("\nExercise 2: co_rank")
    a, b = [1, 3, 5, 7, 9], [2, 4, 6, 8, 10]
    check("k=0 -> 0", try_or_sol("co_rank", 0, a, b), 0)
    check("k=1 -> 1 (a[0]=1 is smallest)", try_or_sol("co_rank", 1, a, b), 1)
    check("k=4 -> 2", try_or_sol("co_rank", 4, a, b), 2)
    check("k=10 -> 5 (everything)", try_or_sol("co_rank", 10, a, b), 5)
    # Bounds matter: with a short `a`, i cannot exceed len(a).
    check("short a, k beyond len(a)", try_or_sol("co_rank", 5, [1, 2], [3, 4, 5]), 2)
    # Ties resolve toward `a` — this is what makes the merge stable.
    check("ties go to a", try_or_sol("co_rank", 2, [2, 2], [2, 2]), 2)
    # Every co_rank must reproduce the true merge prefix.
    merged = _sol_serial_merge(a, b)
    ok = True
    for k in range(len(a) + len(b) + 1):
        i = try_or_sol("co_rank", k, a, b)
        if _sol_serial_merge(a[:i], b[:k - i]) != merged[:k]:
            ok = False
    check("all k reproduce merge prefix", ok, True)

    print("\nExercise 3: merge_path_partition")
    jobs = try_or_sol("merge_path_partition", a, b, 2)
    # merged[:5] = [1,2,3,4,5] takes 1,3,5 from a and 2,4 from b -> co_rank=3.
    check("2 parts", jobs, [((0, 3), (0, 2)), ((3, 5), (2, 5))])
    check("a-slices tile a with no gap",
          [jobs[0][0][0], jobs[0][0][1] == jobs[1][0][0], jobs[1][0][1]],
          [0, True, 5])
    check("b-slices tile b with no gap",
          [jobs[0][1][0], jobs[0][1][1] == jobs[1][1][0], jobs[1][1][1]],
          [0, True, 5])
    check("1 part is the whole merge",
          try_or_sol("merge_path_partition", a, b, 1), [((0, 5), (0, 5))])
    check("empty inputs", try_or_sol("merge_path_partition", [], [], 4),
          [((0, 0), (0, 0))])

    print("\nExercise 4: partitioned_merge")
    want = _sol_serial_merge(a, b)
    for parts in (1, 2, 3, 10):
        check(f"parts={parts}", try_or_sol("partitioned_merge", a, b, parts), want)
    # Duplicate-heavy: the case where a wrong tie rule silently loses elements.
    da, db = [2, 2, 2, 5], [2, 2, 7, 9]
    for parts in (2, 3, 4):
        check(f"duplicates, parts={parts}",
              try_or_sol("partitioned_merge", da, db, parts), sorted(da + db))
    check("uneven lengths",
          try_or_sol("partitioned_merge", [1], [0, 2, 3, 4, 5], 3),
          [0, 1, 2, 3, 4, 5])
    check("empty a", try_or_sol("partitioned_merge", [], [1, 2, 3], 2), [1, 2, 3])

    print("\nExercise 5: multiseq_partition")
    runs = [[1, 4, 9], [2, 3, 10], [5, 6], [], [7, 8, 11, 12]]
    flat = sorted(sum(runs, []))
    check("r=0", try_or_sol("multiseq_partition", runs, 0), [0, 0, 0, 0, 0])
    check("r=total", try_or_sol("multiseq_partition", runs, len(flat)),
          [3, 3, 2, 0, 4])
    idx = try_or_sol("multiseq_partition", runs, 6)
    check("r=6 sums to 6", sum(idx), 6)
    check("r=6 prefix is the true prefix",
          sorted(sum((runs[t][:idx[t]] for t in range(len(runs))), [])), flat[:6])
    # The failure mode from the README: identical values across every run.
    dup = [[5] * 4, [5] * 4, [5] * 4]
    d5 = try_or_sol("multiseq_partition", dup, 5)
    check("all-equal runs sum to r", sum(d5), 5)
    check("all-equal runs stay in range", all(0 <= v <= 4 for v in d5), True)
    check("empty runs only", try_or_sol("multiseq_partition", [[], []], 0), [0, 0])

    print("\nExercise 6: merge_parallelism")
    check("1 worker is serial", try_or_sol("merge_parallelism", 1024, 1024, 1), 1)
    check("empty input", try_or_sol("merge_parallelism", 0, 0, 8), 0)
    vals = [try_or_sol("merge_parallelism", 1 << 20, 1 << 20, p)
            for p in (1, 2, 8, 64, 1024)]
    check("monotone in workers", vals == sorted(vals), True)
    check("64 workers ~ 64x",
          try_or_sol("merge_parallelism", 1 << 20, 1 << 20, 64), 64)
    check("1024 workers ~ 1024x",
          try_or_sol("merge_parallelism", 1 << 20, 1 << 20, 1024), 1024)

    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed + failed} passed")
    print('=' * 50)


if __name__ == "__main__":
    run_tests()
