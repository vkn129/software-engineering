"""
Day 161: Parallel Merge — From Scratch

Day 160 ended on its own ceiling: the final merge is serial, so parallel
mergesort tops out at ~log n speedup. The fix is to partition the OUTPUT before
merging, so the merge itself splits into independent pieces.

  1. serial_merge          the O(n)-span baseline being replaced
  2. co_rank               THE algorithm — one binary search, O(1) space
  3. merge_path_partition  P co-ranks => P disjoint (A-slice, B-slice) jobs
  4. parallel_merge        two-way, threaded
  5. multiseq_partition    the k-way generalisation, incl. the tie handling
  6. parallel_kway_merge   k runs, one pass
  7. work/span model       what actually transfers off CPython

HONESTY NOTE, stated once and meant:
CPython's GIL means pure-Python threads do not run bytecode in parallel. The
threaded functions here MODEL the algorithm; they will be SLOWER than the serial
baseline. Nothing in this file claims wall-clock speedup. What is measured is
correctness, partition disjointness, and work/span — properties of the
algorithm, which is what carries over to C++/CUDA/Rust.
"""

import math
import random
import time
from bisect import bisect_left, bisect_right
from concurrent.futures import ThreadPoolExecutor
from heapq import merge as heap_merge


# ---------------------------------------------------------------------------
# 1. The serial baseline — O(n) work, O(n) span
# ---------------------------------------------------------------------------

def serial_merge(a, b):
    """Two-way merge. Stable: on ties `a` wins, matching co_rank's convention."""
    out = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])
    out.extend(b[j:])
    return out


# ---------------------------------------------------------------------------
# 2. Co-rank — the whole idea, in one binary search
# ---------------------------------------------------------------------------

def co_rank(k, a, b, counter=None):
    """
    How many of the first k merged elements come from `a`?

    Returns i, with j = k - i, such that merging a[:i] with b[:j] gives exactly
    the first k elements of merge(a, b). Valid iff

        a[i-1] <= b[j]     and     b[j-1] < a[i]

    The asymmetry (<= vs <) makes the split stable AND unique — swap either one
    and adjacent chunks duplicate or drop an equal element.

    O(log min(len(a), len(b))) comparisons, O(1) space, no writes.
    `counter` is an optional 1-element list used as a comparison counter.
    """
    m, n = len(a), len(b)
    if not 0 <= k <= m + n:
        raise ValueError(f"k={k} outside [0, {m + n}]")
    # j = k - i must land inside b, and i inside a — hence these bounds, not [0, m].
    lo = max(0, k - n)
    hi = min(k, m)
    while True:
        i = (lo + hi) // 2
        j = k - i
        if counter is not None:
            counter[0] += 1
        if i > 0 and j < n and a[i - 1] > b[j]:
            hi = i - 1          # took too much from a
        elif j > 0 and i < m and b[j - 1] >= a[i]:
            lo = i + 1          # took too little from a
        else:
            return i


def merge_path_partition(a, b, parts, counter=None):
    """
    Cut the output into `parts` contiguous chunks and report, for each, the
    slice of `a` and of `b` that produces it.

    Returns [((a_lo, a_hi), (b_lo, b_hi)), ...]. By construction the a-slices
    tile a exactly, the b-slices tile b exactly, and the chunk outputs
    concatenate in order — that disjointness IS the parallelism.
    """
    total = len(a) + len(b)
    parts = max(1, min(parts, total)) if total else 1
    bounds = [total * t // parts for t in range(parts + 1)]  # evenly spaced diagonals
    ranks = [co_rank(k, a, b, counter) for k in bounds]
    jobs = []
    for t in range(parts):
        i0, i1 = ranks[t], ranks[t + 1]
        j0, j1 = bounds[t] - i0, bounds[t + 1] - i1
        jobs.append(((i0, i1), (j0, j1)))
    return jobs


# ---------------------------------------------------------------------------
# 3. Parallel two-way merge
# ---------------------------------------------------------------------------

def parallel_merge(a, b, workers=4, threshold=1024):
    """
    Merge via merge-path partitioning across `workers` threads.

    Below `threshold` the partitioning costs more than the merge saves — the
    same knob as day-160's THRESHOLD. Above it, each worker merges a disjoint
    output chunk with zero coordination.

    GIL: this is the algorithm's shape, not a speedup. See the module docstring.
    """
    if len(a) + len(b) <= threshold or workers <= 1:
        return serial_merge(a, b)
    jobs = merge_path_partition(a, b, workers)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        chunks = pool.map(
            lambda job: serial_merge(a[job[0][0]:job[0][1]], b[job[1][0]:job[1][1]]),
            jobs,
        )
    out = []
    for c in chunks:
        out.extend(c)
    return out


# ---------------------------------------------------------------------------
# 4. k-way partitioning
# ---------------------------------------------------------------------------

def multiseq_partition(runs, r):
    """
    Index vector (i_1..i_k) with sum == r, splitting k sorted runs consistently:
    everything before the cuts is <= everything after.

    Binary-search the splitter value v = smallest value with count_le(v) >= r.
    Then bisect_left gives a prefix of size < r, and the entire deficit consists
    of elements EQUAL to v — distributed by a fixed rule (run order). That rule
    is the whole difficulty: with duplicates no single value separates the runs,
    and an inconsistent tie-break duplicates or drops elements while leaving the
    output sorted, so the bug ships silently.

    ponytail: binary-searches the integer value range, O(k log n log V). A pure
    comparison version is O(k log(n/k)) but 3x the code; swap it in when keys
    stop being integers.
    """
    k = len(runs)
    total = sum(len(x) for x in runs)
    if not 0 <= r <= total:
        raise ValueError(f"r={r} outside [0, {total}]")
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
    need = r - sum(idx)                    # every missing element equals v
    for t, run in enumerate(runs):
        if need == 0:
            break
        take = min(bisect_right(run, v) - idx[t], need)
        idx[t] += take
        need -= take
    assert need == 0, "splitter search failed to reach rank r"
    return idx


def parallel_kway_merge(runs, workers=4):
    """
    Merge k sorted runs in ONE pass: cut every run at `workers` consistent
    positions, then merge each output chunk independently.

    A binary merge tree needs log k passes over the data. Same asymptotic work,
    but k-way touches each element once — which is what matters when the runs
    live on disk (LSM compaction, external sort).
    """
    total = sum(len(x) for x in runs)
    if total == 0:
        return []
    workers = max(1, min(workers, total))
    bounds = [total * t // workers for t in range(workers + 1)]
    cuts = [multiseq_partition(runs, r) for r in bounds]

    def do_chunk(t):
        lo_v, hi_v = cuts[t], cuts[t + 1]
        # heapq.merge is the stdlib k-way merge; this day's content is the
        # PARTITIONING above, not re-deriving a loser tree.
        return list(heap_merge(*(runs[s][lo_v[s]:hi_v[s]] for s in range(len(runs)))))

    with ThreadPoolExecutor(max_workers=workers) as pool:
        chunks = pool.map(do_chunk, range(workers))
    out = []
    for c in chunks:
        out.extend(c)
    return out


# ---------------------------------------------------------------------------
# 5. Work / span model — the numbers that survive leaving CPython
# ---------------------------------------------------------------------------

def merge_work_span(m, n, workers):
    """(work, span) in comparisons for a merge-path parallel merge."""
    total = m + n
    if total == 0:
        return 0, 0
    search = math.ceil(math.log2(min(m, n) + 1)) + 1
    work = total + (workers + 1) * search       # local merges + P+1 co-ranks
    span = search + math.ceil(total / workers)  # one search, then one chunk
    return work, span


def mergesort_work_span(n, parallel_merge_used):
    """
    The README's recurrences, evaluated numerically.

        Work(n) = 2 Work(n/2) + n                   -> n log n either way
        Span(n) = Span(n/2)   + (n  or  log^2 n)
    """
    if n <= 1:
        return 0, 0
    work = 0
    span = 0
    size = n
    while size > 1:
        work += n                       # one full pass per level
        if parallel_merge_used:
            span += max(1, int(math.log2(size)) ** 2)
        else:
            span += size                # the serial merge at this level
        size //= 2
    return work, span


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_why_input_splitting_fails():
    print("=" * 70)
    print("DEMO 1: why you must partition the OUTPUT, not the input")
    print("=" * 70)
    a, b = [1, 9], [2, 3]
    print(f"\n  a = {a}, b = {b}")
    print(f"  true merge          : {serial_merge(a, b)}")
    naive = serial_merge(a[:1], b[:1]) + serial_merge(a[1:], b[1:])
    print(f"  split inputs in half: {naive}   <- NOT SORTED")
    print("\n  Halving each input gives chunks that do not merge into a")
    print("  contiguous run of the output. Co-ranking inverts the question:")
    print("  for output position k, how much of it came from a?")

    jobs = merge_path_partition(a, b, 2)
    print(f"\n  merge_path_partition(a, b, 2) = {jobs}")
    fixed = []
    for (i0, i1), (j0, j1) in jobs:
        fixed.extend(serial_merge(a[i0:i1], b[j0:j1]))
    print(f"  chunks concatenated : {fixed}   <- correct")
    assert fixed == serial_merge(a, b)


def demo_co_rank():
    print("\n" + "=" * 70)
    print("DEMO 2: the co-rank binary search, step by step")
    print("=" * 70)
    a = [1, 3, 5, 7, 9]
    b = [2, 4, 6, 8, 10]
    merged = serial_merge(a, b)
    print(f"\n  a = {a}")
    print(f"  b = {b}")
    print(f"  merge = {merged}\n")
    print("   k | i=co_rank | j=k-i | a[:i]        b[:j]        first k of merge")
    for k in range(0, len(a) + len(b) + 1, 2):
        i = co_rank(k, a, b)
        j = k - i
        assert serial_merge(a[:i], b[:j]) == merged[:k]
        print(f"  {k:2d} |    {i:2d}     |  {j:2d}   | {str(a[:i]):12s} "
              f"{str(b[:j]):12s} {merged[:k]}")
    print("\n  Every row verified against the true merge. One binary search")
    print(f"  each: ~{math.ceil(math.log2(len(a) + 1))} comparisons, no writes.")


def demo_ties():
    print("\n" + "=" * 70)
    print("DEMO 3: ties — where the naive implementation loses elements")
    print("=" * 70)
    a = [2, 2, 2, 5]
    b = [2, 2, 7, 9]
    print(f"\n  a = {a}\n  b = {b}")
    print(f"  sorted(a+b) = {sorted(a + b)}")
    for parts in (2, 3, 4):
        jobs = merge_path_partition(a, b, parts)
        out = []
        for (i0, i1), (j0, j1) in jobs:
            out.extend(serial_merge(a[i0:i1], b[j0:j1]))
        ok = out == sorted(a + b)
        print(f"  parts={parts}: {jobs}")
        print(f"           -> {out}  len={len(out)} {'OK' if ok else 'BROKEN'}")
        assert ok
    print("\n  co_rank uses  a[i-1] <= b[j]  and  b[j-1] < a[i].")
    print("  Make both <= and two chunks claim the same 2; make both < and one")
    print("  2 vanishes. Either way the output is still SORTED, so the bug")
    print("  survives every 'is it sorted?' test you write.")


def demo_correctness():
    print("\n" + "=" * 70)
    print("DEMO 4: correctness sweep vs sorted(a+b)")
    print("=" * 70)
    random.seed(161)
    cases = 0
    for _ in range(400):
        m, n = random.randint(0, 30), random.randint(0, 30)
        # narrow value range => many duplicates, which is the hard case
        a = sorted(random.randint(0, 8) for _ in range(m))
        b = sorted(random.randint(0, 8) for _ in range(n))
        want = sorted(a + b)
        for parts in (1, 2, 3, 5, 8):
            out = []
            for (i0, i1), (j0, j1) in merge_path_partition(a, b, parts):
                out.extend(serial_merge(a[i0:i1], b[j0:j1]))
            assert out == want, (a, b, parts, out)
            cases += 1
        assert parallel_merge(a, b, workers=4, threshold=0) == want
    print(f"\n  {cases} partitionings over duplicate-heavy random inputs: all exact.")
    print("  Edge cases included: empty a, empty b, both empty, parts > total.")


def demo_kway():
    print("\n" + "=" * 70)
    print("DEMO 5: k-way partitioning across many runs")
    print("=" * 70)
    runs = [[1, 4, 9], [2, 3, 10], [5, 6], [], [7, 8, 11, 12]]
    total = sum(len(r) for r in runs)
    flat = sorted(sum(runs, []))
    print(f"\n  runs   = {runs}  (total {total}, one deliberately empty)")
    print(f"  merged = {flat}\n")
    print("    r | cut vector          | prefix taken")
    for r in range(0, total + 1, 3):
        idx = multiseq_partition(runs, r)
        prefix = sorted(sum((runs[t][:idx[t]] for t in range(len(runs))), []))
        assert sum(idx) == r and prefix == flat[:r]
        print(f"   {r:2d} | {str(idx):20s}| {prefix}")

    print(f"\n  parallel_kway_merge = {parallel_kway_merge(runs, workers=3)}")

    # The duplicate stress test named in the README's failure modes.
    dup = [[5] * 10, [5] * 10, [5] * 10]
    got = parallel_kway_merge(dup, workers=4)
    print(f"\n  duplicate stress [[5]*10]*3 -> len {len(got)} (want 30), "
          f"all fives: {set(got) == {5}}")
    assert len(got) == 30 and set(got) == {5}

    random.seed(7)
    for _ in range(200):
        k = random.randint(1, 6)
        rs = [sorted(random.randint(0, 6) for _ in range(random.randint(0, 12)))
              for _ in range(k)]
        assert parallel_kway_merge(rs, workers=3) == sorted(sum(rs, []))
    print("  200 random k-way merges (k <= 6, heavy duplicates): all exact.")


def demo_work_span():
    print("\n" + "=" * 70)
    print("DEMO 6: work and span — the numbers that leave CPython intact")
    print("=" * 70)
    print("\n  One merge of 2n elements, P workers (comparisons):\n")
    print("        n |    P |    work |   span | parallelism")
    n = 1 << 20
    for p in (1, 2, 8, 64, 1024):
        w, s = merge_work_span(n, n, p)
        print(f"  {n:7d} | {p:4d} | {w:7d} | {s:6d} | {w / s:9.1f}x")
    print("\n  Work barely moves (P+1 extra binary searches). Span collapses.")

    print("\n  Full mergesort, serial merge vs parallel merge:\n")
    print("          n |       work |   span (serial) | span (parallel) | ratio")
    for n in (1 << 10, 1 << 15, 1 << 20):
        w1, s1 = mergesort_work_span(n, False)
        w2, s2 = mergesort_work_span(n, True)
        assert w1 == w2, "parallel merge must not change the WORK"
        print(f"  {n:9d} | {w1:10d} | {s1:15d} | {s2:15d} | "
              f"{s1 / s2:7.1f}x better")
    print("\n  Same work, far less span. That is why this is a strictly better")
    print("  schedule, not a trade-off. day-160's ~log n ceiling is gone.")


def demo_gil_honesty():
    print("\n" + "=" * 70)
    print("DEMO 7: the GIL — what this file does NOT claim")
    print("=" * 70)
    random.seed(3)
    n = 200_000
    a = sorted(random.randint(0, 10 ** 9) for _ in range(n))
    b = sorted(random.randint(0, 10 ** 9) for _ in range(n))
    want = sorted(a + b)

    t0 = time.perf_counter()
    s = serial_merge(a, b)
    t1 = time.perf_counter()
    p = parallel_merge(a, b, workers=4, threshold=0)
    t2 = time.perf_counter()
    assert s == want and p == want

    print(f"\n  merging 2 x {n} sorted ints, both outputs verified correct")
    print(f"    serial_merge        : {t1 - t0:.3f}s")
    print(f"    parallel_merge (4)  : {t2 - t1:.3f}s")
    ratio = (t1 - t0) / (t2 - t1)
    print(f"    ratio               : {ratio:.2f}x  (with 4 threads)")
    print("\n  Whatever that ratio came out as, DO NOT read it as parallel")
    print("  speedup. The GIL serialises pure-Python bytecode, so the threads")
    print("  cannot overlap any comparison work at all. Any ratio above 1.0 is")
    print("  an artefact of merging 8 short lists instead of 2 long ones —")
    print("  better cache locality and cheaper list growth, measured on one")
    print("  core. Any ratio below 1.0 is thread overhead. Both measure")
    print("  CPython, neither measures the algorithm.")
    print("\n  DEMO 6's work/span table is the transferable result: it holds in")
    print("  C++/OpenMP or CUDA, where the same partitioning does scale.")


if __name__ == "__main__":
    demo_why_input_splitting_fails()
    demo_co_rank()
    demo_ties()
    demo_correctness()
    demo_kway()
    demo_work_span()
    demo_gil_honesty()
