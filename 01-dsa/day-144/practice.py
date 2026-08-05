"""
Day 144 Practice: Convex Hull

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
# Exercise 1: cross product orientation test
# ---------------------------------------------------------------------------

def cross(o, a, b):
    """Cross product (a-o) x (b-o). Positive = CCW at a, negative = CW."""
    # TODO
    pass


def _sol_cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


# ---------------------------------------------------------------------------
# Exercise 2: orientation classifier (returns 1, -1, 0)
# ---------------------------------------------------------------------------

def orientation(o, a, b):
    """Return 1 if CCW, -1 if CW, 0 if collinear."""
    # TODO
    pass


def _sol_orientation(o, a, b):
    c = _sol_cross(o, a, b)
    if c > 0:
        return 1
    if c < 0:
        return -1
    return 0


# ---------------------------------------------------------------------------
# Exercise 3: Andrew's monotone chain
# ---------------------------------------------------------------------------

def convex_hull(points):
    """Return convex hull in CCW order starting from lowest-leftmost.
    Drop collinear vertices (strict turn test)."""
    # TODO
    pass


def _sol_convex_hull(points):
    pts = sorted(set(points))
    if len(pts) <= 1:
        return pts
    lower = []
    for p in pts:
        while len(lower) >= 2 and _sol_cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and _sol_cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


# ---------------------------------------------------------------------------
# Exercise 4: shoelace polygon area
# ---------------------------------------------------------------------------

def polygon_area(poly):
    """Unsigned area of a simple polygon. Return float."""
    # TODO
    pass


def _sol_polygon_area(poly):
    n = len(poly)
    if n < 3:
        return 0.0
    s = 0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


# ---------------------------------------------------------------------------
# Exercise 5: is point inside convex polygon? (CCW order assumed)
# ---------------------------------------------------------------------------

def point_in_convex(point, poly):
    """Return True if point is strictly inside or on the boundary of the
    CCW-ordered convex polygon `poly`."""
    # TODO: every edge should be a left turn (>= 0) for the point
    pass


def _sol_point_in_convex(point, poly):
    n = len(poly)
    if n < 3:
        return False
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        if _sol_cross(a, b, point) < 0:
            return False
    return True


# ---------------------------------------------------------------------------
# Exercise 6: hull size (number of vertices)
# ---------------------------------------------------------------------------

def hull_size(points):
    """Return the number of vertices of the convex hull."""
    # TODO
    pass


def _sol_hull_size(points):
    return len(_sol_convex_hull(points))


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
            print(f"  FAIL: {name}  got={got!r}  expected={expected!r}")
            failed += 1

    print("Exercise 1: cross")
    check("CCW right angle", try_or_sol("cross", (0, 0), (1, 0), (0, 1)), 1)
    check("CW right angle", try_or_sol("cross", (0, 0), (0, 1), (1, 0)), -1)
    check("collinear", try_or_sol("cross", (0, 0), (1, 1), (2, 2)), 0)

    print("\nExercise 2: orientation")
    check("CCW", try_or_sol("orientation", (0, 0), (1, 0), (0, 1)), 1)
    check("CW", try_or_sol("orientation", (0, 0), (0, 1), (1, 0)), -1)
    check("collinear", try_or_sol("orientation", (0, 0), (1, 1), (2, 2)), 0)

    print("\nExercise 3: convex_hull")
    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]
    check("unit square + interior", set(try_or_sol("convex_hull", pts)),
          {(0, 0), (4, 0), (4, 4), (0, 4)})
    pts2 = [(0, 0), (1, 1), (2, 2)]
    check("collinear -> endpoints",
          set(try_or_sol("convex_hull", pts2)), {(0, 0), (2, 2)})
    check("single point",
          try_or_sol("convex_hull", [(5, 5)]), [(5, 5)])

    print("\nExercise 4: polygon_area")
    check("unit square", try_or_sol("polygon_area",
          [(0, 0), (1, 0), (1, 1), (0, 1)]), 1.0)
    check("triangle 3x4",
          try_or_sol("polygon_area", [(0, 0), (3, 0), (0, 4)]), 6.0)
    check("degenerate", try_or_sol("polygon_area", [(0, 0), (1, 1)]), 0.0)

    print("\nExercise 5: point_in_convex")
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    check("inside", try_or_sol("point_in_convex", (2, 2), square), True)
    check("on edge", try_or_sol("point_in_convex", (2, 0), square), True)
    check("outside",
          try_or_sol("point_in_convex", (5, 5), square), False)
    check("corner",
          try_or_sol("point_in_convex", (0, 0), square), True)

    print("\nExercise 6: hull_size")
    check("square + interior",
          try_or_sol("hull_size", [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2)]), 4)
    check("collinear",
          try_or_sol("hull_size", [(0, 0), (1, 0), (2, 0), (3, 0)]), 2)
    check("triangle",
          try_or_sol("hull_size", [(0, 0), (10, 0), (5, 10)]), 3)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
