"""
Day 111 Practice: Fractional Cascading

6 exercises. Implement TODOs, then run: python practice.py

Goal: lower_bound(x) in k sorted lists for O(log n + k) instead of
O(k log n). Exercises 2-5 build the structure, exercise 6 queries it.

Every function returns a list, never None: try_or_sol reads a None result as
"the student stub is unimplemented" and silently falls back.
"""


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


def lower_bound(a, x):
    """First index i with a[i] >= x, else len(a). Given -- Day 106 owns it.

    Worth noticing: the pointer arrays you build below are nothing more than
    this function tabulated at build time so the query never has to call it.
    """
    lo, hi = 0, len(a)
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def merge_sorted(a, b):
    """Two-pointer merge of two sorted lists. Given."""
    out, i, j = [], 0, 0
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
# Exercise 1: naive_multi_search
# ---------------------------------------------------------------------------
# The O(k log n) baseline to beat. Note what is wasteful: each search spends
# log n rediscovering where x sits in the value space, information the
# previous search already paid for and discarded.

def naive_multi_search(lists, x):
    """lower_bound(x) in each list, by k independent binary searches."""
    # TODO: implement
    pass


def _sol_naive_multi_search(lists, x):
    return [lower_bound(L, x) for L in lists]


# ---------------------------------------------------------------------------
# Exercise 2: promote_bridges
# ---------------------------------------------------------------------------
# Every SECOND element of an augmented list, starting at index 1.
# Promote all of them instead and each list doubles the next, so |A[0]| grows
# exponentially in k. Halving makes the total a convergent geometric series
# and keeps total space under 2N.

def promote_bridges(aug_next):
    """Elements of aug_next to borrow into the previous augmented list."""
    # TODO: implement
    pass


def _sol_promote_bridges(aug_next):
    return aug_next[1::2]


# ---------------------------------------------------------------------------
# Exercise 3: build_augmented
# ---------------------------------------------------------------------------
# A[k-1] = L[k-1]; A[i] = merge(L[i], promote_bridges(A[i+1])).
# Build BACKWARDS -- A[i] cannot be formed until A[i+1] exists.

def build_augmented(lists):
    """Return the list of augmented value lists, one per input list."""
    # TODO: implement
    pass


def _sol_build_augmented(lists):
    k = len(lists)
    aug = [[] for _ in range(k)]
    for i in range(k - 1, -1, -1):
        promoted = _sol_promote_bridges(aug[i + 1]) if i + 1 < k else []
        aug[i] = merge_sorted(list(lists[i]), promoted)
    return aug


# ---------------------------------------------------------------------------
# Exercise 4: build_own
# ---------------------------------------------------------------------------
# own[j] = lower_bound(L, A[j]) -- where entry j of the augmented list lands
# in the ORIGINAL list. Length must be len(A) + 1: the extra SENTINEL slot
# holds len(L), meaning "x is past everything here". That sentinel is what
# turns an empty list from a crash into an ordinary code path.

def build_own(original, aug):
    """Pointer array of length len(aug) + 1 into `original`."""
    # TODO: implement, including the sentinel
    pass


def _sol_build_own(original, aug):
    return [lower_bound(original, v) for v in aug] + [len(original)]


# ---------------------------------------------------------------------------
# Exercise 5: build_next
# ---------------------------------------------------------------------------
# next[j] = lower_bound(A_next, A[j]) -- the bridge. Same sentinel rule, with
# len(A_next) in the final slot. For the last list there is no next, so return
# zeros of the right length.

def build_next(aug, aug_next):
    """Bridge pointer array of length len(aug) + 1 into aug_next."""
    # TODO: implement, including the sentinel
    pass


def _sol_build_next(aug, aug_next):
    if aug_next is None:
        return [0] * (len(aug) + 1)
    return [lower_bound(aug_next, v) for v in aug] + [len(aug_next)]


# ---------------------------------------------------------------------------
# Exercise 6: cascade_query
# ---------------------------------------------------------------------------
# ONE binary search into aug[0], then hop. Two things to get right:
#   - the answer for list i is own[i][p] directly (see README for why the
#     lower bound of aug[i][p] is also the lower bound of x)
#   - nxt[i][p] points at the successor of aug[i][p], which is >= x, so it can
#     OVERSHOOT. Walk back while aug[i+1][q-1] >= x. That walk is O(1)
#     because at most 2 elements sit between consecutive bridges.

def cascade_query(lists, aug, own, nxt, x):
    """lower_bound(x) in every original list, using the built structure."""
    # TODO: implement
    pass


def _sol_cascade_query(lists, aug, own, nxt, x):
    k = len(lists)
    if k == 0:
        return []
    p = lower_bound(aug[0], x)          # the only log n you pay
    out = []
    for i in range(k):
        out.append(own[i][p])
        if i + 1 < k:
            q = nxt[i][p]
            while q > 0 and aug[i + 1][q - 1] >= x:
                q -= 1                  # correct the overshoot, O(1)
            p = q
    return out


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

def build_all(lists):
    """Assemble aug/own/nxt using the exercise functions under test."""
    aug = try_or_sol("build_augmented", lists)
    k = len(lists)
    own = [try_or_sol("build_own", lists[i], aug[i]) for i in range(k)]
    nxt = [try_or_sol("build_next", aug[i], aug[i + 1] if i + 1 < k else None)
           for i in range(k)]
    return aug, own, nxt


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

    LISTS = [
        [10, 40],
        [20, 30, 50],
        [25, 60],
    ]

    print("Exercise 1: naive_multi_search")
    check("x=5 below all", try_or_sol("naive_multi_search", LISTS, 5), [0, 0, 0])
    check("x=25 exact hit", try_or_sol("naive_multi_search", LISTS, 25), [1, 1, 0])
    check("x=99 above all", try_or_sol("naive_multi_search", LISTS, 99), [2, 3, 2])
    check("no lists", try_or_sol("naive_multi_search", [], 5), [])
    check("empty list yields 0", try_or_sol("naive_multi_search", [[], [5]], 5), [0, 0])

    print("\nExercise 2: promote_bridges")
    check("every second from index 1",
          try_or_sol("promote_bridges", [10, 20, 30, 40, 50]), [20, 40])
    check("single element promotes nothing",
          try_or_sol("promote_bridges", [7]), [])
    check("empty promotes nothing", try_or_sol("promote_bridges", []), [])
    check("two elements promote one",
          try_or_sol("promote_bridges", [1, 2]), [2])

    print("\nExercise 3: build_augmented")
    aug = try_or_sol("build_augmented", LISTS)
    check("A2 is L2 unchanged", aug[2], [25, 60])
    check("A1 = L1 + [60]", aug[1], [20, 30, 50, 60])
    check("A0 = L0 + [30, 60]", aug[0], [10, 30, 40, 60])
    # Space bound: the every-second rule keeps the total under 2N.
    check("total size <= 2 * raw size",
          sum(len(a) for a in aug) <= 2 * sum(len(L) for L in LISTS), True)
    # A1 has one element, so its [1::2] is empty and A0 stays empty too.
    check("empty-list chain", try_or_sol("build_augmented", [[], [5], []]),
          [[], [5], []])
    check("no lists", try_or_sol("build_augmented", []), [])

    print("\nExercise 4: build_own")
    check("own for L0", try_or_sol("build_own", [10, 40], [10, 30, 40, 60]),
          [0, 1, 1, 2, 2])
    check("own for L2", try_or_sol("build_own", [25, 60], [25, 60]), [0, 1, 2])
    check("sentinel length is len(aug)+1",
          len(try_or_sol("build_own", [10, 40], [10, 30, 40, 60])), 5)
    # The empty-list case: sentinel is the ONLY entry, and it reads 0.
    check("empty original -> sentinel only",
          try_or_sol("build_own", [], []), [0])

    print("\nExercise 5: build_next")
    check("next from A1 into A2",
          try_or_sol("build_next", [20, 30, 50, 60], [25, 60]), [0, 1, 1, 1, 2])
    check("last list has no next",
          try_or_sol("build_next", [25, 60], None), [0, 0, 0])
    check("sentinel is len(aug_next)",
          try_or_sol("build_next", [1], [4, 5, 6])[-1], 3)

    print("\nExercise 6: cascade_query")
    aug, own, nxt = build_all(LISTS)
    for x in [5, 10, 20, 25, 41, 60, 99]:
        check(f"x={x} matches naive",
              try_or_sol("cascade_query", LISTS, aug, own, nxt, x),
              _sol_naive_multi_search(LISTS, x))

    print("\nEmpty-list bridge cases (where naive builds crash)")
    # A[i] empty while A[i+1] is not -- p == 0 == len(A[i]) and there is no
    # entry to read a pointer from. Only the sentinel makes this work.
    for lists in ([[], [5], []], [[], []], [[], [1, 2, 3]],
                  [[7], [], [7]], [[]], []):
        a, o, n = build_all(lists)
        ok = all(try_or_sol("cascade_query", lists, a, o, n, x)
                 == _sol_naive_multi_search(lists, x)
                 for x in range(-1, 9))
        check(f"lists={lists}", ok, True)

    print("\nCross-check: many lists, many queries")
    big = [
        [1, 3, 5, 7, 9, 11],
        [2, 2, 2, 8],
        [],
        [0, 10, 20],
        [4],
        [3, 3, 3, 3, 3],
    ]
    a, o, n = build_all(big)
    check("every x in [-2, 24] matches naive",
          all(try_or_sol("cascade_query", big, a, o, n, x)
              == _sol_naive_multi_search(big, x)
              for x in range(-2, 25)), True)
    check("duplicates: lower_bound semantics kept",
          try_or_sol("cascade_query", big, a, o, n, 3),
          _sol_naive_multi_search(big, 3))

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
