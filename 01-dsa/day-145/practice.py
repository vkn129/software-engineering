"""
Day 145 Practice: Line Segment Intersection

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
# Exercise 1: signed orientation
# ---------------------------------------------------------------------------

def orient(p, q, r):
    """+1 CCW, -1 CW, 0 collinear."""
    # TODO
    pass


def _sol_orient(p, q, r):
    v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (v > 0) - (v < 0)


# ---------------------------------------------------------------------------
# Exercise 2: point on segment (assuming collinear)
# ---------------------------------------------------------------------------

def on_segment(p, q, r):
    """True if r lies in the bounding box of segment pq."""
    # TODO
    pass


def _sol_on_segment(p, q, r):
    return (min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and
            min(p[1], q[1]) <= r[1] <= max(p[1], q[1]))


# ---------------------------------------------------------------------------
# Exercise 3: do two segments intersect?
# ---------------------------------------------------------------------------

def segments_intersect(s1, s2):
    """s1, s2 are ((x,y),(x,y)). Return True iff they share at least one point."""
    # TODO
    pass


def _sol_segments_intersect(s1, s2):
    p1, p2 = s1
    p3, p4 = s2
    o1 = _sol_orient(p1, p2, p3)
    o2 = _sol_orient(p1, p2, p4)
    o3 = _sol_orient(p3, p4, p1)
    o4 = _sol_orient(p3, p4, p2)
    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and _sol_on_segment(p1, p2, p3): return True
    if o2 == 0 and _sol_on_segment(p1, p2, p4): return True
    if o3 == 0 and _sol_on_segment(p3, p4, p1): return True
    if o4 == 0 and _sol_on_segment(p3, p4, p2): return True
    return False


# ---------------------------------------------------------------------------
# Exercise 4: brute-force intersection pairs
# ---------------------------------------------------------------------------

def all_intersecting_pairs(segments):
    """Return sorted list of (i, j), i<j, of intersecting pairs."""
    # TODO
    pass


def _sol_all_intersecting_pairs(segments):
    pairs = []
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if _sol_segments_intersect(segments[i], segments[j]):
                pairs.append((i, j))
    return sorted(pairs)


# ---------------------------------------------------------------------------
# Exercise 5: compute intersection point (single-crossing case)
# ---------------------------------------------------------------------------

def intersection_point(s1, s2):
    """Return (x, y) float intersection point if segments cross at a unique
    point inside both, else None."""
    # TODO: parametric formula
    pass


def _sol_intersection_point(s1, s2):
    (x1, y1), (x2, y2) = s1
    (x3, y3), (x4, y4) = s2
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None


# ---------------------------------------------------------------------------
# Exercise 6: count intersections (just a count)
# ---------------------------------------------------------------------------

def count_intersections(segments):
    """Return the number of intersecting pairs."""
    # TODO
    pass


def _sol_count_intersections(segments):
    return len(_sol_all_intersecting_pairs(segments))


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

    print("Exercise 1: orient")
    check("CCW", try_or_sol("orient", (0, 0), (1, 0), (0, 1)), 1)
    check("CW", try_or_sol("orient", (0, 0), (0, 1), (1, 0)), -1)
    check("collinear", try_or_sol("orient", (0, 0), (1, 1), (2, 2)), 0)

    print("\nExercise 2: on_segment")
    check("midpoint", try_or_sol("on_segment", (0, 0), (4, 4), (2, 2)), True)
    check("outside",
          try_or_sol("on_segment", (0, 0), (4, 4), (5, 5)), False)
    check("endpoint",
          try_or_sol("on_segment", (0, 0), (4, 4), (0, 0)), True)

    print("\nExercise 3: segments_intersect")
    check("cross",
          try_or_sol("segments_intersect", ((0, 0), (4, 4)), ((0, 4), (4, 0))),
          True)
    check("parallel disjoint",
          try_or_sol("segments_intersect", ((0, 0), (4, 0)), ((0, 1), (4, 1))),
          False)
    check("share endpoint",
          try_or_sol("segments_intersect", ((0, 0), (1, 1)), ((1, 1), (2, 0))),
          True)
    check("collinear overlap",
          try_or_sol("segments_intersect", ((0, 0), (4, 0)), ((2, 0), (6, 0))),
          True)
    check("collinear gap",
          try_or_sol("segments_intersect", ((0, 0), (1, 0)), ((2, 0), (3, 0))),
          False)

    print("\nExercise 4: all_intersecting_pairs")
    segs = [((0, 0), (4, 4)),
            ((0, 4), (4, 0)),
            ((10, 10), (12, 12))]
    check("X plus isolated",
          try_or_sol("all_intersecting_pairs", segs), [(0, 1)])
    segs = [((0, 0), (4, 0)),
            ((1, -1), (1, 1)),
            ((3, -1), (3, 1))]
    check("two verticals cross horizontal",
          try_or_sol("all_intersecting_pairs", segs), [(0, 1), (0, 2)])

    print("\nExercise 5: intersection_point")
    pt = try_or_sol("intersection_point", ((0, 0), (4, 4)), ((0, 4), (4, 0)))
    check("X center", pt, (2.0, 2.0))
    pt = try_or_sol("intersection_point", ((0, 0), (1, 0)), ((2, 0), (3, 0)))
    check("collinear -> None", pt, None)

    print("\nExercise 6: count_intersections")
    segs = [((0, 0), (4, 4)),
            ((0, 4), (4, 0)),
            ((1, 2), (3, 2))]
    check("3 pairwise",
          try_or_sol("count_intersections", segs), 3)
    check("empty", try_or_sol("count_intersections", []), 0)
    segs = [((0, 0), (1, 1)), ((2, 2), (3, 3))]
    check("collinear no overlap",
          try_or_sol("count_intersections", segs), 0)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
