"""
Day 147 Practice: Voronoi & Delaunay

6 exercises. Implement TODOs, then run: python practice.py
"""


def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Exercise 1: orientation
# ---------------------------------------------------------------------------

def orient(a, b, c):
    """+1 CCW, -1 CW, 0 collinear."""
    # TODO
    pass


def _sol_orient(a, b, c):
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (v > 0) - (v < 0)


# ---------------------------------------------------------------------------
# Exercise 2: circumcenter of triangle
# ---------------------------------------------------------------------------

def circumcenter(a, b, c):
    """Return (cx, cy). Return None for collinear points."""
    # TODO
    pass


def _sol_circumcenter(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if d == 0:
        return None
    ux = ((ax*ax + ay*ay) * (by - cy)
        + (bx*bx + by*by) * (cy - ay)
        + (cx*cx + cy*cy) * (ay - by)) / d
    uy = ((ax*ax + ay*ay) * (cx - bx)
        + (bx*bx + by*by) * (ax - cx)
        + (cx*cx + cy*cy) * (bx - ax)) / d
    return (ux, uy)


# ---------------------------------------------------------------------------
# Exercise 3: incircle test
# ---------------------------------------------------------------------------

def in_circle(a, b, c, d):
    """True iff d lies strictly inside the circumcircle of CCW triangle (a,b,c)."""
    # TODO
    pass


def _sol_in_circle(a, b, c, d):
    ax, ay = a[0] - d[0], a[1] - d[1]
    bx, by = b[0] - d[0], b[1] - d[1]
    cx, cy = c[0] - d[0], c[1] - d[1]
    det = (ax * (by * (cx * cx + cy * cy) - cy * (bx * bx + by * by))
         - ay * (bx * (cx * cx + cy * cy) - cx * (bx * bx + by * by))
         + (ax * ax + ay * ay) * (bx * cy - by * cx))
    return det > 0


# ---------------------------------------------------------------------------
# Exercise 4: nearest site (brute)
# ---------------------------------------------------------------------------

def nearest_site(query, sites):
    """Return the site closest to query."""
    # TODO
    pass


def _sol_nearest_site(query, sites):
    best = None
    best_d = float("inf")
    for s in sites:
        d = (s[0] - query[0]) ** 2 + (s[1] - query[1]) ** 2
        if d < best_d:
            best_d = d
            best = s
    return best


# ---------------------------------------------------------------------------
# Exercise 5: is a triangle Delaunay vs a given set of other points?
# ---------------------------------------------------------------------------

def is_delaunay_triangle(triangle, other_points):
    """Return True iff no point in other_points lies strictly inside the
    circumcircle of `triangle`."""
    # TODO
    pass


def _sol_is_delaunay_triangle(triangle, other_points):
    a, b, c = triangle
    if _sol_orient(a, b, c) < 0:
        a, b, c = a, c, b
    elif _sol_orient(a, b, c) == 0:
        return False
    for p in other_points:
        if p in (a, b, c):
            continue
        if _sol_in_circle(a, b, c, p):
            return False
    return True


# ---------------------------------------------------------------------------
# Exercise 6: brute O(n^4) Delaunay
# ---------------------------------------------------------------------------

def delaunay_brute(points):
    """
    Return sorted list of Delaunay triangles. Each triangle is a sorted tuple
    of 3 point tuples. O(n^4): enumerate all triangles, keep Delaunay ones.
    """
    # TODO
    pass


def _sol_delaunay_brute(points):
    pts = list(points)
    n = len(pts)
    tris = []
    for i in range(n):
        for j in range(i + 1, n):
            for k in range(j + 1, n):
                t = (pts[i], pts[j], pts[k])
                others = [p for q, p in enumerate(pts) if q not in (i, j, k)]
                if _sol_is_delaunay_triangle(t, others):
                    tris.append(tuple(sorted(t)))
    return sorted(set(tris))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        ok = got == expected
        if isinstance(got, tuple) and isinstance(expected, tuple) \
                and len(got) == len(expected):
            ok = all(abs(a - b) < 1e-9 for a, b in zip(got, expected))
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got!r}  expected={expected!r}")
            failed += 1

    print("Exercise 1: orient")
    check("CCW", try_or_sol("orient", (0, 0), (1, 0), (0, 1)), 1)
    check("CW", try_or_sol("orient", (0, 0), (0, 1), (1, 0)), -1)
    check("collinear", try_or_sol("orient", (0, 0), (1, 1), (2, 2)), 0)

    print("\nExercise 2: circumcenter")
    check("unit triangle center",
          try_or_sol("circumcenter", (0, 0), (2, 0), (1, 2)),
          (1.0, 0.75))
    # right triangle: circumcenter at hypotenuse midpoint
    check("right triangle",
          try_or_sol("circumcenter", (0, 0), (4, 0), (0, 4)),
          (2.0, 2.0))
    check("collinear -> None",
          try_or_sol("circumcenter", (0, 0), (1, 1), (2, 2)), None)

    print("\nExercise 3: in_circle")
    a, b, c = (0, 0), (4, 0), (2, 4)
    check("origin near center",
          try_or_sol("in_circle", a, b, c, (2, 2)), True)
    check("far outside",
          try_or_sol("in_circle", a, b, c, (100, 100)), False)
    check("vertex itself -> not strictly inside",
          try_or_sol("in_circle", a, b, c, a), False)

    print("\nExercise 4: nearest_site")
    sites = [(0, 0), (10, 0), (5, 10)]
    check("near origin",
          try_or_sol("nearest_site", (1, 1), sites), (0, 0))
    check("near (10,0)",
          try_or_sol("nearest_site", (9, 1), sites), (10, 0))

    print("\nExercise 5: is_delaunay_triangle")
    tri = ((0, 0), (4, 0), (2, 4))
    check("no other points",
          try_or_sol("is_delaunay_triangle", tri, []), True)
    check("point inside circumcircle",
          try_or_sol("is_delaunay_triangle", tri, [(2, 2)]), False)
    check("point far outside",
          try_or_sol("is_delaunay_triangle", tri, [(100, 100)]), True)

    print("\nExercise 6: delaunay_brute")
    # 4 corners + center
    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
    tris = try_or_sol("delaunay_brute", pts)
    check("center triangulation has 4 triangles", len(tris), 4)
    # all triangles must include the center for this configuration
    center = (2, 2)
    check("all triangles include center",
          all(center in t for t in tris), True)
    # 3 collinear: no triangle
    check("3 collinear -> no triangles",
          try_or_sol("delaunay_brute", [(0, 0), (1, 1), (2, 2)]), [])

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
