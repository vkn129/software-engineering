"""
Day 146 Practice: Closest Pair of Points

6 exercises. Implement TODOs, then run: python practice.py
"""

import math


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: squared distance
# ---------------------------------------------------------------------------

def dist2(p, q):
    """Return squared Euclidean distance."""
    # TODO
    pass


def _sol_dist2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


# ---------------------------------------------------------------------------
# Exercise 2: brute closest pair (squared distance)
# ---------------------------------------------------------------------------

def closest_pair_sq_brute(points):
    """Return squared distance of closest pair. Return inf if fewer than 2."""
    # TODO
    pass


def _sol_closest_pair_sq_brute(points):
    n = len(points)
    if n < 2:
        return float("inf")
    best = float("inf")
    for i in range(n):
        for j in range(i + 1, n):
            d = _sol_dist2(points[i], points[j])
            if d < best:
                best = d
    return best


# ---------------------------------------------------------------------------
# Exercise 3: closest pair (returns distance + pair)
# ---------------------------------------------------------------------------

def closest_pair_brute(points):
    """Return (distance, (p, q)) using brute force."""
    # TODO
    pass


def _sol_closest_pair_brute(points):
    n = len(points)
    if n < 2:
        return (float("inf"), None)
    best = float("inf")
    bp = None
    for i in range(n):
        for j in range(i + 1, n):
            d = _sol_dist2(points[i], points[j])
            if d < best:
                best = d
                bp = (points[i], points[j])
    return (math.sqrt(best), bp)


# ---------------------------------------------------------------------------
# Exercise 4: strip step — given a y-sorted strip and bound d, refine
# ---------------------------------------------------------------------------

def strip_closest(strip, d_sq):
    """
    strip: list of points sorted by y, all within sqrt(d_sq) of dividing x.
    d_sq: current best squared distance.
    Return the new best squared distance after scanning the strip.
    Inner scan stops when (strip[j].y - strip[i].y)^2 >= d_sq.
    """
    # TODO
    pass


def _sol_strip_closest(strip, d_sq):
    best = d_sq
    n = len(strip)
    for i in range(n):
        j = i + 1
        while j < n and (strip[j][1] - strip[i][1]) ** 2 < best:
            dd = _sol_dist2(strip[i], strip[j])
            if dd < best:
                best = dd
            j += 1
    return best


# ---------------------------------------------------------------------------
# Exercise 5: divide & conquer closest pair (squared distance)
# ---------------------------------------------------------------------------

def closest_pair_dc_sq(points):
    """Return squared distance of closest pair via divide & conquer."""
    # TODO
    pass


def _sol_closest_pair_dc_sq(points):
    if len(points) < 2:
        return float("inf")
    Px = sorted(points)
    Py = sorted(points, key=lambda p: (p[1], p[0]))
    return _rec(Px, Py)


def _rec(Px, Py):
    n = len(Px)
    if n <= 3:
        best = float("inf")
        for i in range(n):
            for j in range(i + 1, n):
                best = min(best, _sol_dist2(Px[i], Px[j]))
        return best
    mid = n // 2
    midx = Px[mid][0]
    Lx, Rx = Px[:mid], Px[mid:]
    Lset = set(Lx)
    Ly = [p for p in Py if p in Lset]
    Ry = [p for p in Py if p not in Lset]
    d = min(_rec(Lx, Ly), _rec(Rx, Ry))
    strip = [p for p in Py if (p[0] - midx) ** 2 < d]
    return _sol_strip_closest(strip, d)


# ---------------------------------------------------------------------------
# Exercise 6: minimum-distance value (Euclidean, not squared)
# ---------------------------------------------------------------------------

def closest_pair_distance(points):
    """Return Euclidean distance of the closest pair, or inf if fewer than 2."""
    # TODO
    pass


def _sol_closest_pair_distance(points):
    return math.sqrt(_sol_closest_pair_dc_sq(points))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        ok = got == expected
        if isinstance(got, float) and isinstance(expected, float):
            ok = abs(got - expected) < 1e-9 or (got == expected)
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got!r}  expected={expected!r}")
            failed += 1

    print("Exercise 1: dist2")
    check("(0,0)-(3,4) -> 25", try_or_sol("dist2", (0, 0), (3, 4)), 25)
    check("same point", try_or_sol("dist2", (5, 5), (5, 5)), 0)

    print("\nExercise 2: closest_pair_sq_brute")
    check("simple",
          try_or_sol("closest_pair_sq_brute",
                     [(0, 0), (3, 4), (0, 1)]), 1)
    check("one point",
          try_or_sol("closest_pair_sq_brute", [(0, 0)]), float("inf"))
    check("empty",
          try_or_sol("closest_pair_sq_brute", []), float("inf"))

    print("\nExercise 3: closest_pair_brute")
    d, pair = try_or_sol("closest_pair_brute",
                         [(0, 0), (3, 4), (0, 1)])
    check("distance", d, 1.0)
    check("pair set", set(pair), {(0, 0), (0, 1)})

    print("\nExercise 4: strip_closest")
    # strip points all within d; should reduce d when finding closer pair
    strip = [(0, 0), (0, 2), (0, 5)]
    check("d=10 strip finds 4",
          try_or_sol("strip_closest", strip, 10), 4)
    strip = [(0, 0), (0, 3)]
    check("no closer than d=1",
          try_or_sol("strip_closest", strip, 1), 1)

    print("\nExercise 5: closest_pair_dc_sq")
    check("simple",
          try_or_sol("closest_pair_dc_sq",
                     [(0, 0), (3, 4), (0, 1)]), 1)
    check("square corners",
          try_or_sol("closest_pair_dc_sq",
                     [(0, 0), (10, 0), (10, 10), (0, 10)]), 100)
    # randomized check vs brute
    import random
    random.seed(99)
    for _ in range(3):
        n = random.randint(4, 30)
        pts = list({(random.randint(0, 100), random.randint(0, 100))
                    for _ in range(n)})
        if len(pts) < 2:
            continue
        a = _sol_closest_pair_sq_brute(pts)
        b = try_or_sol("closest_pair_dc_sq", pts)
        check(f"random n={len(pts)} dc==brute", b, a)

    print("\nExercise 6: closest_pair_distance")
    check("3-4-5 pair",
          try_or_sol("closest_pair_distance", [(0, 0), (3, 4)]), 5.0)
    check("empty", try_or_sol("closest_pair_distance", []), float("inf"))
    check("unit step",
          try_or_sol("closest_pair_distance",
                     [(0, 0), (1, 0), (5, 5)]), 1.0)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
