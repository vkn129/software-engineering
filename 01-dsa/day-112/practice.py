"""
Day 112 Practice: Searchable Sorted Index (mini-project)

6 exercises. Implement TODOs, then run: python practice.py

Each exercise is one piece of the index: build it, probe it three ways, then
shard it. Tests assert CORRECTNESS and probe counts only -- never wall-clock.
Probe counts are exact reproducible integers; timings measure the interpreter.

ABSENT is -1, never None: try_or_sol reads a None result as "the student stub
is unimplemented" and silently falls back.
"""

ABSENT = -1


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
# Exercise 1: build_index
# ---------------------------------------------------------------------------
# Sorted and DEDUPLICATED. Deduplication is what makes a returned position
# unambiguous -- with duplicates, "the index of x" has no single answer and
# every backend below would need its own tie-breaking rule.

def build_index(keys):
    """Return the sorted, deduplicated key array."""
    # TODO: implement
    pass


def _sol_build_index(keys):
    return sorted(set(keys))


# ---------------------------------------------------------------------------
# Exercise 2: binary_lower_bound
# ---------------------------------------------------------------------------
# Day 106's baseline. Return (index of first key >= x, probes used).
# This is the number every other backend has to beat.

def binary_lower_bound(keys, x):
    """Return (lower_bound index, probe count)."""
    # TODO: implement
    pass


def _sol_binary_lower_bound(keys, x):
    lo, hi, probes = 0, len(keys), 0
    while lo < hi:
        mid = lo + (hi - lo) // 2       # overflow-safe in fixed-width ints
        probes += 1
        if keys[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo, probes


# ---------------------------------------------------------------------------
# Exercise 3: interp_lower_bound
# ---------------------------------------------------------------------------
# Day 108, made safe. Three things must be right:
#   1. settle x <= keys[0] and x > keys[-1] up front, so the loop can rely on
#      the answer living inside [lo, hi]
#   2. clamp the probe to [lo, hi-1]. Clamping to [lo, hi] lets a probe land
#      on hi, leave the window unchanged, and SPIN FOREVER -- that is the real
#      defect that was hiding in day-108's practice.py
#   3. finish with a binary search over [lo, hi], not over [lo, n) -- the
#      wider window throws the interpolation work away

def interp_lower_bound(keys, x, max_iters=8):
    """Return (lower_bound index, probe count). Must terminate on duplicates."""
    # TODO: implement
    pass


def _sol_interp_lower_bound(keys, x, max_iters=8):
    a, n, probes = keys, len(keys), 0
    if n == 0:
        return 0, probes
    probes += 1
    if x <= a[0]:
        return 0, probes
    probes += 1
    if x > a[n - 1]:
        return n, probes
    lo, hi, iters = 0, n - 1, 0
    while hi - lo > 4 and iters < max_iters:
        if a[hi] == a[lo]:
            break                       # zero denominator, nothing to gain
        pos = lo + ((x - a[lo]) * (hi - lo)) // (a[hi] - a[lo])
        pos = max(lo, min(hi - 1, pos))  # hi-1, not hi: guarantees a shrink
        probes += 1
        if a[pos] < x:
            lo = pos + 1                # every index <= pos is < x
        else:
            hi = pos                    # a[pos] >= x
        iters += 1
    w_lo, w_hi = lo, hi + 1             # answer is inside [lo, hi]
    while w_lo < w_hi:
        mid = w_lo + (w_hi - w_lo) // 2
        probes += 1
        if a[mid] < x:
            w_lo = mid + 1
        else:
            w_hi = mid
    return w_lo, probes


# ---------------------------------------------------------------------------
# Exercise 4: grid_lower_bound
# ---------------------------------------------------------------------------
# Day 110 applied where it is deliberately WRONG, to price the mistake.
# Reshape the sorted array row-major into rows x cols; the result is
# row+column sorted, so the staircase is valid -- but we threw away the total
# order we already had, and O(sqrt n) is what that costs.
# Counting cells strictly below x from the bottom-left gives the lower bound.
# The tail row is padded with a sentinel above every real key so the column
# ordering survives when cols does not divide n.

def grid_lower_bound(keys, x):
    """Return (lower_bound index, probe count) via a staircase walk."""
    # TODO: implement
    pass


def _sol_grid_lower_bound(keys, x):
    n = len(keys)
    if n == 0:
        return 0, 0
    cols = max(1, int(n ** 0.5))
    rows = (n + cols - 1) // cols
    padded = list(keys) + [keys[-1] + 1] * (rows * cols - n)
    grid = [padded[r * cols:(r + 1) * cols] for r in range(rows)]
    r, c, probes, below = rows - 1, 0, 0, 0
    while r >= 0 and c < cols:
        probes += 1
        if grid[r][c] < x:
            below += r + 1              # +1 is the 0-indexing of rows
            c += 1
        else:
            r -= 1
    return min(below, n), probes


# ---------------------------------------------------------------------------
# Exercise 5: range_query
# ---------------------------------------------------------------------------
# Inclusive [lo, hi]. One lower_bound to find the start, then a forward scan.
# This is why an ordered structure earns its keep: a hash set answers
# membership faster and cannot answer this at all.

def range_query(keys, lo, hi):
    """All keys in the inclusive range [lo, hi], ascending."""
    # TODO: implement
    pass


def _sol_range_query(keys, lo, hi):
    i, _ = _sol_binary_lower_bound(keys, lo)
    out = []
    while i < len(keys) and keys[i] <= hi:
        out.append(keys[i])
        i += 1
    return out


# ---------------------------------------------------------------------------
# Exercise 6: cascade_positions
# ---------------------------------------------------------------------------
# Day 111 across k shards: one binary search, then O(1) hops. Build the
# augmented lists backwards, borrowing every SECOND element, and give both
# pointer arrays a SENTINEL slot at index len(aug[i]) -- that sentinel is what
# makes an EMPTY shard an ordinary code path instead of an IndexError.

def cascade_positions(shards, x):
    """lower_bound(x) in every shard, via fractional cascading."""
    # TODO: implement
    pass


def _sol_cascade_positions(shards, x):
    k = len(shards)
    if k == 0:
        return []
    aug = [[] for _ in range(k)]
    own = [[] for _ in range(k)]
    nxt = [[] for _ in range(k)]
    for i in range(k - 1, -1, -1):
        promoted = aug[i + 1][1::2] if i + 1 < k else []
        aug[i] = sorted(list(shards[i]) + promoted)
        own[i] = ([_sol_binary_lower_bound(shards[i], v)[0] for v in aug[i]]
                  + [len(shards[i])])
        nxt[i] = ([_sol_binary_lower_bound(aug[i + 1], v)[0] for v in aug[i]]
                  + [len(aug[i + 1])]) if i + 1 < k else [0] * (len(aug[i]) + 1)
    p = _sol_binary_lower_bound(aug[0], x)[0]   # the only log n paid
    out = []
    for i in range(k):
        out.append(own[i][p])
        if i + 1 < k:
            q = nxt[i][p]
            while q > 0 and aug[i + 1][q - 1] >= x:
                q -= 1                  # correct the bridge overshoot, O(1)
            p = q
    return out


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(label, got, want):
        nonlocal passed, failed
        if got == want:
            print(f"  PASS: {label}")
            passed += 1
        else:
            print(f"  FAIL: {label}")
            print(f"    expected: {want}")
            print(f"    got:      {got}")
            failed += 1

    def lb_oracle(keys, x):
        return sum(1 for v in keys if v < x)

    print("Exercise 1: build_index")
    check("sorts", try_or_sol("build_index", [5, 1, 3]), [1, 3, 5])
    check("deduplicates", try_or_sol("build_index", [2, 2, 2, 1]), [1, 2])
    check("empty", try_or_sol("build_index", []), [])
    check("all identical collapse to one",
          try_or_sol("build_index", [7] * 200), [7])
    check("negatives sort correctly",
          try_or_sol("build_index", [3, -1, -50, 0]), [-50, -1, 0, 3])

    K = _sol_build_index([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

    print("\nExercise 2: binary_lower_bound")
    check("exact hit", try_or_sol("binary_lower_bound", K, 50)[0], 4)
    check("between keys", try_or_sol("binary_lower_bound", K, 35)[0], 3)
    check("below all", try_or_sol("binary_lower_bound", K, 0)[0], 0)
    check("above all", try_or_sol("binary_lower_bound", K, 999)[0], 10)
    check("empty index", try_or_sol("binary_lower_bound", [], 5)[0], 0)
    check("probes <= ceil(log2(n))+1",
          try_or_sol("binary_lower_bound", K, 35)[1] <= 5, True)
    check("agrees with oracle everywhere",
          all(try_or_sol("binary_lower_bound", K, x)[0] == lb_oracle(K, x)
              for x in range(-5, 110)), True)

    print("\nExercise 3: interp_lower_bound")
    check("exact hit", try_or_sol("interp_lower_bound", K, 50)[0], 4)
    check("between keys", try_or_sol("interp_lower_bound", K, 35)[0], 3)
    check("below all", try_or_sol("interp_lower_bound", K, 0)[0], 0)
    check("above all", try_or_sol("interp_lower_bound", K, 999)[0], 10)
    check("empty index", try_or_sol("interp_lower_bound", [], 5)[0], 0)
    check("agrees with oracle everywhere",
          all(try_or_sol("interp_lower_bound", K, x)[0] == lb_oracle(K, x)
              for x in range(-5, 110)), True)
    # The hang case. A probe clamped to [lo, hi] instead of [lo, hi-1] never
    # shrinks the window here and loops forever. Reaching this line at all is
    # part of the assertion; a wrong implementation never returns.
    dupheavy = [1, 2, 2, 2, 3, 5, 5, 8, 8, 8, 8, 10]
    check("duplicate-heavy input terminates",
          all(try_or_sol("interp_lower_bound", dupheavy, x)[0]
              == lb_oracle(dupheavy, x) for x in range(0, 12)), True)
    allsame = [7] * 200
    check("all-identical input terminates",
          all(try_or_sol("interp_lower_bound", allsame, x)[0]
              == lb_oracle(allsame, x) for x in (6, 7, 8)), True)
    # Uniform keys are interpolation's bet: it should beat binary here.
    uni = list(range(0, 100000, 10))
    ip = sum(try_or_sol("interp_lower_bound", uni, x)[1]
             for x in range(0, 100000, 4999))
    bp = sum(try_or_sol("binary_lower_bound", uni, x)[1]
             for x in range(0, 100000, 4999))
    check("fewer probes than binary on uniform keys", ip < bp, True)

    print("\nExercise 4: grid_lower_bound")
    check("exact hit", try_or_sol("grid_lower_bound", K, 50)[0], 4)
    check("between keys", try_or_sol("grid_lower_bound", K, 35)[0], 3)
    check("below all", try_or_sol("grid_lower_bound", K, 0)[0], 0)
    check("above all", try_or_sol("grid_lower_bound", K, 999)[0], 10)
    check("empty index", try_or_sol("grid_lower_bound", [], 5)[0], 0)
    check("agrees with oracle everywhere",
          all(try_or_sol("grid_lower_bound", K, x)[0] == lb_oracle(K, x)
              for x in range(-5, 110)), True)
    # Ragged tail: cols rarely divides n, so the last row needs padding.
    ragged_ok = True
    for n in range(0, 41):
        keys = list(range(0, 2 * n, 2))
        for x in range(-1, 2 * n + 2):
            if try_or_sol("grid_lower_bound", keys, x)[0] != lb_oracle(keys, x):
                ragged_ok = False
    check("ragged tail padding, n = 0..40", ragged_ok, True)
    # The whole point: discarding the total order costs sqrt(n), not log(n).
    big = list(range(10000))
    check("more probes than binary (sqrt n vs log n)",
          try_or_sol("grid_lower_bound", big, 5000)[1]
          > try_or_sol("binary_lower_bound", big, 5000)[1], True)

    print("\nExercise 5: range_query")
    check("interior range", try_or_sol("range_query", K, 30, 60), [30, 40, 50, 60])
    check("inclusive at both ends", try_or_sol("range_query", K, 10, 10), [10])
    check("empty range", try_or_sol("range_query", K, 31, 39), [])
    check("lo above everything", try_or_sol("range_query", K, 500, 900), [])
    check("hi below everything", try_or_sol("range_query", K, -50, -1), [])
    check("whole index", try_or_sol("range_query", K, -999, 999), K)
    check("empty index", try_or_sol("range_query", [], 0, 10), [])
    check("inverted bounds give nothing", try_or_sol("range_query", K, 60, 30), [])

    print("\nExercise 6: cascade_positions")
    shards = [[10, 40], [20, 30, 50], [25, 60]]

    def naive(sh, x):
        return [lb_oracle(s, x) for s in sh]

    for x in [5, 20, 25, 41, 60, 99]:
        check(f"x={x} matches k binary searches",
              try_or_sol("cascade_positions", shards, x), naive(shards, x))
    # Day 111's sentinel case: an empty shard in any position.
    for sh in ([[], [1, 2], [3]], [[1], [], [3]], [[1], [2], []],
               [[], [], []], [], [[]]):
        check(f"empty shard case {sh}",
              all(try_or_sol("cascade_positions", sh, x) == naive(sh, x)
                  for x in range(-1, 6)), True)

    print("\nCross-check: all three backends agree on every input")
    ok = True
    for keys in ([], [42], [7] * 5, list(range(-50, 50)),
                 [0, 10 ** 6, 10 ** 9], [1, 1, 2, 3, 5, 8, 13, 21]):
        idx = _sol_build_index(keys)
        for x in range(-5, 30):
            want = lb_oracle(idx, x)
            for fn in ("binary_lower_bound", "interp_lower_bound",
                       "grid_lower_bound"):
                if try_or_sol(fn, idx, x)[0] != want:
                    ok = False
    check("binary == interp == grid on every input", ok, True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
