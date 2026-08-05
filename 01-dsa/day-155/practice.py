"""
Day 155 Practice: Parallel Prefix Sum

6 exercises on scan primitives. Implement TODOs, then `python practice.py`.
"""


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Sequential inclusive scan
# ===================================================================
def inclusive_scan(a):
    """Return [a[0], a[0]+a[1], ..., sum(a)]. Empty input → []."""
    # TODO
    pass


def _sol_inclusive_scan(a):
    out = []
    s = 0
    for x in a:
        s += x
        out.append(s)
    return out


# ===================================================================
# Exercise 2: Exclusive scan
# ===================================================================
def exclusive_scan(a):
    """out[0] = 0, out[i] = a[0] + ... + a[i-1]."""
    # TODO
    pass


def _sol_exclusive_scan(a):
    out = [0] * len(a)
    for i in range(1, len(a)):
        out[i] = out[i - 1] + a[i - 1]
    return out


# ===================================================================
# Exercise 3: Hillis-Steele inclusive scan
# ===================================================================
# log n synchronization rounds; each round doubles the offset.
def hillis_steele(a):
    """Same result as inclusive_scan, computed in log n parallel rounds."""
    # TODO
    pass


def _sol_hillis_steele(a):
    cur = a[:]
    offset = 1
    n = len(a)
    while offset < n:
        prev = cur[:]
        for i in range(n):
            if i >= offset:
                cur[i] = prev[i] + prev[i - offset]
        offset *= 2
    return cur


# ===================================================================
# Exercise 4: Blelloch exclusive scan (sum)
# ===================================================================
# Up-sweep + down-sweep on power-of-two-padded buffer.
def blelloch(a):
    """Same result as exclusive_scan, using up/down sweep."""
    # TODO
    pass


def _sol_blelloch(a):
    n = len(a)
    if n == 0:
        return []
    size = 1
    while size < n:
        size *= 2
    buf = a[:] + [0] * (size - n)
    d = 1
    while d < size:
        for i in range(0, size, 2 * d):
            buf[i + 2 * d - 1] = buf[i + d - 1] + buf[i + 2 * d - 1]
        d *= 2
    buf[size - 1] = 0
    d = size // 2
    while d >= 1:
        for i in range(0, size, 2 * d):
            t = buf[i + d - 1]
            buf[i + d - 1] = buf[i + 2 * d - 1]
            buf[i + 2 * d - 1] = t + buf[i + 2 * d - 1]
        d //= 2
    return buf[:n]


# ===================================================================
# Exercise 5: Stream compaction with scan
# ===================================================================
# Given values and a predicate, produce the kept values in order using
# exactly one exclusive scan over the 0/1 flags.
def compact(values, pred):
    """Return [v for v in values if pred(v)] using exclusive_scan."""
    # TODO
    pass


def _sol_compact(values, pred):
    flags = [1 if pred(v) else 0 for v in values]
    offsets = _sol_exclusive_scan(flags)
    total = (offsets[-1] + flags[-1]) if flags else 0
    out = [0] * total
    for i, v in enumerate(values):
        if flags[i]:
            out[offsets[i]] = v
    return out


# ===================================================================
# Exercise 6: Segmented scan
# ===================================================================
# Given values and segment-head flags (1 = new segment starts here),
# produce per-segment inclusive sums.
# Example: values=[1,2,3,4,5], heads=[1,0,1,0,0] → [1,3,3,7,12]
def segmented_scan(values, heads):
    """Per-segment inclusive scan."""
    # TODO
    pass


def _sol_segmented_scan(values, heads):
    out = []
    running = 0
    for v, h in zip(values, heads):
        if h:
            running = v
        else:
            running += v
        out.append(running)
    return out


# ===================================================================
# Test runner
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
            print(f"  FAIL: {name}  expected {expected}, got {got}")
            failed += 1

    print("Exercise 1: inclusive_scan")
    check("basic", try_or_sol("inclusive_scan", [3, 1, 4, 1, 5]), [3, 4, 8, 9, 14])
    check("empty", try_or_sol("inclusive_scan", []), [])

    print("\nExercise 2: exclusive_scan")
    check("basic", try_or_sol("exclusive_scan", [3, 1, 4, 1, 5]), [0, 3, 4, 8, 9])
    check("single", try_or_sol("exclusive_scan", [7]), [0])

    print("\nExercise 3: hillis_steele")
    check("power of 2", try_or_sol("hillis_steele", [1, 2, 3, 4]), [1, 3, 6, 10])
    check("non-pow2", try_or_sol("hillis_steele", [3, 1, 4, 1, 5]), [3, 4, 8, 9, 14])

    print("\nExercise 4: blelloch")
    check("power of 2", try_or_sol("blelloch", [1, 2, 3, 4]), [0, 1, 3, 6])
    check("non-pow2", try_or_sol("blelloch", [3, 1, 4, 1, 5]), [0, 3, 4, 8, 9])

    print("\nExercise 5: compact")
    check("keep evens", try_or_sol("compact", [1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0), [2, 4, 6])
    check("keep none", try_or_sol("compact", [1, 3, 5], lambda x: x % 2 == 0), [])

    print("\nExercise 6: segmented_scan")
    check("basic", try_or_sol("segmented_scan", [1, 2, 3, 4, 5], [1, 0, 1, 0, 0]), [1, 3, 3, 7, 12])
    check("all heads", try_or_sol("segmented_scan", [5, 5, 5], [1, 1, 1]), [5, 5, 5])

    total = passed + failed
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
