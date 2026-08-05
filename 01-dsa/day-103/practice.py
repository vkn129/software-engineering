"""
Day 103 Practice: Timsort

9 exercises, one per moving part of `timsort.py`. Implement the TODOs, then
run: python3 practice.py

Everything here is self-contained — no import from timsort.py — so you can
break things freely without touching the reference implementation.
"""

MIN_GALLOP = 7


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
# Exercise 1: compute_minrun
# ---------------------------------------------------------------------------

def compute_minrun(n):
    """
    Return the minimum run length for an array of n elements, in [32, 64]
    for n >= 64 (and n itself below that).
    """
    # TODO: shift n right until it is < 64, OR-ing the discarded bits into r
    pass


def _sol_compute_minrun(n):
    # The +r rounds up whenever we shifted away a set bit. That is what keeps
    # n/minrun just under a power of two, so the final merge tree stays balanced
    # — an unbalanced tree is what makes naive mergesort merge unequal runs.
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r


# ---------------------------------------------------------------------------
# Exercise 2: count_run_and_make_ascending
# ---------------------------------------------------------------------------

def count_run_and_make_ascending(a, lo, hi):
    """
    Find the natural run starting at a[lo] within a[lo:hi]. Reverse it in place
    if it is strictly descending. Return the run length.
    """
    # TODO: walk forward while the order holds; reverse if descending
    pass


def _sol_count_run_and_make_ascending(a, lo, hi):
    run_hi = lo + 1
    if run_hi == hi:
        return 1
    if a[run_hi] < a[lo]:
        # STRICTLY descending only. Reversing a run containing equal neighbours
        # would swap equal elements past each other and destroy stability.
        run_hi += 1
        while run_hi < hi and a[run_hi] < a[run_hi - 1]:
            run_hi += 1
        i, j = lo, run_hi - 1
        while i < j:
            a[i], a[j] = a[j], a[i]
            i += 1
            j -= 1
    else:
        run_hi += 1
        while run_hi < hi and a[run_hi] >= a[run_hi - 1]:
            run_hi += 1
    return run_hi - lo


# ---------------------------------------------------------------------------
# Exercise 3: binary_insertion_sort
# ---------------------------------------------------------------------------

def binary_insertion_sort(a, lo, hi, start=None):
    """
    Sort a[lo:hi] in place, stably. a[lo:start] is already sorted, so only
    a[start:hi] needs inserting. `start` defaults to lo + 1.
    """
    # TODO: binary-search the insertion point, then shift right
    pass


def _sol_binary_insertion_sort(a, lo, hi, start=None):
    if start is None:
        start = lo + 1
    for i in range(start, hi):
        pivot = a[i]
        left, right = lo, i
        while left < right:
            mid = (left + right) // 2
            # `pivot < a[mid]` (not <=) sends equal keys to the RIGHT half, so a
            # later element never jumps ahead of an equal earlier one: stable.
            if pivot < a[mid]:
                right = mid
            else:
                left = mid + 1
        j = i
        while j > left:
            a[j] = a[j - 1]
            j -= 1
        a[left] = pivot


# ---------------------------------------------------------------------------
# Exercise 4: gallop_left
# ---------------------------------------------------------------------------

def gallop_left(key, a, base, length, hint):
    """
    Return k in [0, length] with a[base+k-1] < key <= a[base+k].
    That is: the LEFTMOST slot where key could be inserted.
    Exponential search outward from `hint`, then binary search the bracket.
    """
    # TODO: double the offset until the key is bracketed, then binary search
    pass


def _sol_gallop_left(key, a, base, length, hint):
    last_ofs = 0
    ofs = 1
    if key > a[base + hint]:
        max_ofs = length - hint
        while ofs < max_ofs and key > a[base + hint + ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:          # overflow guard, faithful to listsort.c
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs += hint
        ofs += hint
    else:
        max_ofs = hint + 1
        while ofs < max_ofs and key <= a[base + hint - ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs, ofs = hint - ofs, hint - last_ofs
    last_ofs += 1
    while last_ofs < ofs:
        m = (last_ofs + ofs) // 2
        if key > a[base + m]:
            last_ofs = m + 1
        else:
            ofs = m
    return ofs


# ---------------------------------------------------------------------------
# Exercise 5: gallop_right
# ---------------------------------------------------------------------------

def gallop_right(key, a, base, length, hint):
    """
    Return k in [0, length] with a[base+k-1] <= key < a[base+k].
    That is: the RIGHTMOST slot where key could be inserted.
    """
    # TODO: mirror gallop_left with the comparison flipped
    pass


def _sol_gallop_right(key, a, base, length, hint):
    last_ofs = 0
    ofs = 1
    if key < a[base + hint]:
        max_ofs = hint + 1
        while ofs < max_ofs and key < a[base + hint - ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs, ofs = hint - ofs, hint - last_ofs
    else:
        max_ofs = length - hint
        while ofs < max_ofs and key >= a[base + hint + ofs]:
            last_ofs = ofs
            ofs = (ofs << 1) + 1
            if ofs <= 0:
                ofs = max_ofs
        if ofs > max_ofs:
            ofs = max_ofs
        last_ofs += hint
        ofs += hint
    last_ofs += 1
    while last_ofs < ofs:
        m = (last_ofs + ofs) // 2
        if key < a[base + m]:
            ofs = m
        else:
            last_ofs = m + 1
    return ofs


# ---------------------------------------------------------------------------
# Exercise 6: merge_generic
# ---------------------------------------------------------------------------

def merge_generic(a, base1, len1, base2, len2):
    """
    Stable in-place merge of the ADJACENT runs a[base1:base1+len1] and
    a[base2:base2+len2] (base2 == base1 + len1). No galloping.
    """
    # TODO: copy both runs out, then write the merged order back
    pass


def _sol_merge_generic(a, base1, len1, base2, len2):
    left = a[base1:base1 + len1]
    right = a[base2:base2 + len2]
    i = j = 0
    dest = base1
    while i < len1 and j < len2:
        # Strict `<` on the right element sends ties to the LEFT run, which came
        # first in the input. That one comparison is the whole of merge stability.
        if right[j] < left[i]:
            a[dest] = right[j]
            j += 1
        else:
            a[dest] = left[i]
            i += 1
        dest += 1
    while i < len1:
        a[dest] = left[i]
        i += 1
        dest += 1
    while j < len2:
        a[dest] = right[j]
        j += 1
        dest += 1


# ---------------------------------------------------------------------------
# Exercise 7: merge_lo
# ---------------------------------------------------------------------------

def merge_lo(a, base1, len1, base2, len2):
    """
    Merge adjacent runs when the LEFT run is the smaller one. Copy only the
    left run to scratch (O(len1) extra space instead of O(len1+len2)) and merge
    into the hole it leaves behind. Must stay stable.
    Galloping is an optimisation, not a requirement — correctness first.
    """
    # TODO: tmp = left run; merge tmp against the right run back into `a`
    pass


def _sol_merge_lo(a, base1, len1, base2, len2):
    # Copying only the smaller side is the point: the merge-stack invariant keeps
    # run lengths within a constant factor, so scratch space stays small.
    tmp = a[base1:base1 + len1]
    dest = base1
    i = 0
    j = base2
    end_j = base2 + len2
    count1 = count2 = 0
    min_gallop = MIN_GALLOP

    while i < len1 and j < end_j:
        if a[j] < tmp[i]:
            a[dest] = a[j]
            dest += 1
            j += 1
            count2 += 1
            count1 = 0
        else:
            a[dest] = tmp[i]
            dest += 1
            i += 1
            count1 += 1
            count2 = 0

        if count1 >= min_gallop or count2 >= min_gallop:
            # One side has been winning steadily, so stop comparing one at a time
            # and binary-search how far it keeps winning.
            if i < len1 and j < end_j:
                gp = _sol_gallop_right(a[j], tmp, i, len1 - i, 0)
                if gp > 0:
                    a[dest:dest + gp] = tmp[i:i + gp]
                    dest += gp
                    i += gp
                if i < len1 and j < end_j:
                    a[dest] = a[j]
                    dest += 1
                    j += 1
            if i < len1 and j < end_j:
                gp = _sol_gallop_left(tmp[i], a, j, end_j - j, 0)
                if gp > 0:
                    a[dest:dest + gp] = a[j:j + gp]
                    dest += gp
                    j += gp
                if i < len1 and j < end_j:
                    a[dest] = tmp[i]
                    dest += 1
                    i += 1
            count1 = count2 = 0
            min_gallop += 1  # galloping did not pay off; raise the bar

    if i < len1:
        a[dest:dest + (len1 - i)] = tmp[i:len1]
    # Anything left in the right run already sits in its final place.


# ---------------------------------------------------------------------------
# Exercise 8: merge_runs_at
# ---------------------------------------------------------------------------

def merge_runs_at(a, runs, i):
    """
    Merge the adjacent stack entries runs[i] and runs[i+1] (each a
    [base, length] pair), collapse them into one entry at index i, and sort the
    underlying slice of `a`. Return None.
    """
    # TODO: update the run stack first, then merge the two slices
    pass


def _sol_merge_runs_at(a, runs, i):
    base1, len1 = runs[i]
    base2, len2 = runs[i + 1]
    runs[i] = [base1, len1 + len2]
    del runs[i + 1]
    # Pick the variant that copies the smaller side to scratch.
    if len1 <= len2:
        _sol_merge_lo(a, base1, len1, base2, len2)
    else:
        _sol_merge_generic(a, base1, len1, base2, len2)


# ---------------------------------------------------------------------------
# Exercise 9: timsort
# ---------------------------------------------------------------------------

def timsort(a):
    """
    Full Timsort. Return a NEW sorted list; do not mutate the caller's input.
    Detect natural runs, pad short ones to minrun, and merge under the stack
    invariant.
    """
    # TODO: run detection -> pad -> push -> restore invariant -> final collapse
    pass


def _sol_timsort(a):
    a = list(a)
    n = len(a)
    if n < 2:
        return a

    minrun = _sol_compute_minrun(n)
    runs = []
    lo = 0
    remaining = n
    while remaining > 0:
        run_len = _sol_count_run_and_make_ascending(a, lo, lo + remaining)
        if run_len < minrun:
            force = min(remaining, minrun)
            _sol_binary_insertion_sort(a, lo, lo + force, start=lo + run_len)
            run_len = force
        runs.append([lo, run_len])
        lo += run_len
        remaining -= run_len

        # The invariant (len[-3] > len[-2] + len[-1] and len[-2] > len[-1])
        # forces run lengths to grow at least Fibonacci-fast, which bounds the
        # stack at O(log n) and keeps every merge between comparable sizes.
        while len(runs) > 1:
            n_runs = len(runs)
            if n_runs >= 3 and runs[-3][1] <= runs[-2][1] + runs[-1][1]:
                if runs[-3][1] < runs[-1][1]:
                    _sol_merge_runs_at(a, runs, n_runs - 3)
                else:
                    _sol_merge_runs_at(a, runs, n_runs - 2)
            elif runs[-2][1] <= runs[-1][1]:
                _sol_merge_runs_at(a, runs, n_runs - 2)
            else:
                break

    while len(runs) > 1:
        _sol_merge_runs_at(a, runs, len(runs) - 2)

    return a


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

    print("Exercise 1: compute_minrun")
    check("n=63 -> n itself", try_or_sol("compute_minrun", 63), 63)
    check("n=64 -> 32", try_or_sol("compute_minrun", 64), 32)
    check("n=65 -> 33 (rounds up)", try_or_sol("compute_minrun", 65), 33)
    check("n=1000 -> 63", try_or_sol("compute_minrun", 1000), 63)
    check("in [32,64] for large n",
          all(32 <= try_or_sol("compute_minrun", k) <= 64
              for k in (64, 100, 4096, 10**6)), True)

    print("\nExercise 2: count_run_and_make_ascending")
    a = [1, 2, 3, 9, 0]
    check("ascending run length",
          try_or_sol("count_run_and_make_ascending", a, 0, len(a)), 4)
    a = [5, 4, 3, 1, 7]
    check("descending run length",
          try_or_sol("count_run_and_make_ascending", a, 0, len(a)), 4)
    check("descending run reversed in place", a[:4], [1, 3, 4, 5])
    a = [2, 2, 2, 1]
    check("equal run counts as ascending",
          try_or_sol("count_run_and_make_ascending", a, 0, len(a)), 3)
    # Equal neighbours must NOT be treated as descending, or stability breaks.
    a = [(1, 'a'), (1, 'b'), (0, 'c')]
    try_or_sol("count_run_and_make_ascending", a, 0, len(a))
    check("equal keys keep original order", a[:2], [(1, 'a'), (1, 'b')])
    a = [7]
    check("single element", try_or_sol("count_run_and_make_ascending", a, 0, 1), 1)

    print("\nExercise 3: binary_insertion_sort")
    a = [3, 1, 4, 1, 5, 9, 2, 6]
    try_or_sol("binary_insertion_sort", a, 0, len(a))
    check("sorts whole slice", a, [1, 1, 2, 3, 4, 5, 6, 9])
    a = [1, 3, 5, 4, 2]
    try_or_sol("binary_insertion_sort", a, 0, len(a), 3)  # a[0:3] already sorted
    check("honours pre-sorted prefix", a, [1, 2, 3, 4, 5])
    a = [(1, 'a'), (1, 'b'), (0, 'c')]
    try_or_sol("binary_insertion_sort", a, 0, len(a))
    check("stable on equal keys", a, [(0, 'c'), (1, 'a'), (1, 'b')])
    a = [4, 5, 6, 1, 2, 3]
    try_or_sol("binary_insertion_sort", a, 2, 5)  # only touch a[2:5]
    check("respects lo/hi bounds", a, [4, 5, 1, 2, 6, 3])

    print("\nExercise 4: gallop_left")
    arr = [0, 2, 4, 6, 8, 10, 12, 14]
    check("key below all", try_or_sol("gallop_left", -1, arr, 0, len(arr), 0), 0)
    check("key above all", try_or_sol("gallop_left", 99, arr, 0, len(arr), 0), 8)
    check("between elements", try_or_sol("gallop_left", 7, arr, 0, len(arr), 0), 4)
    check("hint far from answer", try_or_sol("gallop_left", 7, arr, 0, len(arr), 7), 4)
    dup = [1, 1, 1, 1, 5, 5, 5, 5]
    check("leftmost slot among duplicates",
          try_or_sol("gallop_left", 5, dup, 0, len(dup), 0), 4)

    print("\nExercise 5: gallop_right")
    check("key below all", try_or_sol("gallop_right", -1, arr, 0, len(arr), 0), 0)
    check("key above all", try_or_sol("gallop_right", 99, arr, 0, len(arr), 0), 8)
    check("between elements", try_or_sol("gallop_right", 7, arr, 0, len(arr), 3), 4)
    check("rightmost slot among duplicates",
          try_or_sol("gallop_right", 5, dup, 0, len(dup), 0), 8)
    # left <= right for every key is what makes the pair safe inside a merge.
    check("gallop_left <= gallop_right",
          all(try_or_sol("gallop_left", k, dup, 0, len(dup), 0)
              <= try_or_sol("gallop_right", k, dup, 0, len(dup), 0)
              for k in (0, 1, 3, 5, 9)), True)

    print("\nExercise 6: merge_generic")
    a = [1, 4, 7, 2, 3, 9, 11]
    try_or_sol("merge_generic", a, 0, 3, 3, 4)
    check("merges adjacent runs", a, [1, 2, 3, 4, 7, 9, 11])
    a = [(1, 'L'), (2, 'L'), (1, 'R'), (2, 'R')]
    try_or_sol("merge_generic", a, 0, 2, 2, 2)
    check("ties keep left run first", a, [(1, 'L'), (1, 'R'), (2, 'L'), (2, 'R')])
    a = [5, 6, 1, 2]
    try_or_sol("merge_generic", a, 0, 2, 2, 2)
    check("fully disjoint runs", a, [1, 2, 5, 6])

    print("\nExercise 7: merge_lo")
    a = [2, 5, 1, 3, 4, 6, 7]
    try_or_sol("merge_lo", a, 0, 2, 2, 5)
    check("small left run", a, [1, 2, 3, 4, 5, 6, 7])
    a = [(1, 'L'), (2, 'L'), (1, 'R'), (2, 'R')]
    try_or_sol("merge_lo", a, 0, 2, 2, 2)
    check("stable on ties", a, [(1, 'L'), (1, 'R'), (2, 'L'), (2, 'R')])
    # A long one-sided right run is what drives the gallop branch.
    a = [50, 60] + list(range(0, 40))
    try_or_sol("merge_lo", a, 0, 2, 2, 40)
    check("long right run triggers gallop path", a, list(range(0, 40)) + [50, 60])

    print("\nExercise 8: merge_runs_at")
    a = [1, 4, 7, 2, 3, 9]
    runs = [[0, 3], [3, 3]]
    try_or_sol("merge_runs_at", a, runs, 0)
    check("array merged", a, [1, 2, 3, 4, 7, 9])
    check("stack collapsed to one entry", runs, [[0, 6]])
    a = [0, 5, 9, 2, 8, 1, 3]
    runs = [[0, 3], [3, 2], [5, 2]]
    try_or_sol("merge_runs_at", a, runs, 1)  # merge the middle pair only
    check("merges the requested pair", a[3:7], [1, 2, 3, 8])
    check("leaves untouched run alone", a[:3], [0, 5, 9])
    check("stack shrinks by one", runs, [[0, 3], [3, 4]])

    print("\nExercise 9: timsort")
    check("empty", try_or_sol("timsort", []), [])
    check("single", try_or_sol("timsort", [1]), [1])
    check("reversed", try_or_sol("timsort", [5, 4, 3, 2, 1]), [1, 2, 3, 4, 5])
    check("duplicates", try_or_sol("timsort", [3, 1, 3, 1, 3]), [1, 1, 3, 3, 3])
    check("all equal", try_or_sol("timsort", [7] * 50), [7] * 50)

    import random
    random.seed(103)
    big = [random.randint(0, 500) for _ in range(3000)]
    check("3000 random ints", try_or_sol("timsort", big), sorted(big))
    # Real natural runs, longer than minrun: exercises the merge stack.
    shaped = (list(range(200)) + list(range(300, 100, -1))
              + [random.randint(0, 400) for _ in range(200)])
    check("mixed run shapes", try_or_sol("timsort", shaped), sorted(shaped))

    src = [4, 2, 4, 1]
    try_or_sol("timsort", src)
    check("input not mutated", src, [4, 2, 4, 1])

    # Stability: sort (key, tag) pairs; within a key the tags must stay ascending.
    pairs = [(k, i) for i, k in enumerate([2, 1, 2, 1, 2, 1, 3, 3, 1] * 12)]
    keyed = try_or_sol("timsort", pairs)
    tags_by_key = {}
    stable = True
    for k, tag in keyed:
        if k in tags_by_key and tag < tags_by_key[k]:
            stable = False
            break
        tags_by_key[k] = tag
    check("stable across a full sort", stable, True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
