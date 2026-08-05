"""
Day 145: Line Segment Intersection (Sweep Line)

Two implementations:
  - Brute force O(n^2): exact-integer cross-product intersection tests.
  - Simplified Bentley-Ottmann sweep: event queue + active set.

Active set is a plain sorted list (not a BBST) for clarity; this loses the
optimal log-factor but keeps the algorithm transparent.
"""

import heapq


# ---------------------------------------------------------------------------
# 1. Orientation primitive
# ---------------------------------------------------------------------------

def orient(p, q, r):
    """+1 CCW, -1 CW, 0 collinear. Integer-exact for integer inputs."""
    v = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (v > 0) - (v < 0)


def on_segment(p, q, r):
    """True if r lies on segment pq (assumes collinearity already established)."""
    return (min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and
            min(p[1], q[1]) <= r[1] <= max(p[1], q[1]))


# ---------------------------------------------------------------------------
# 2. Segment-segment intersection test (boolean)
# ---------------------------------------------------------------------------

def segments_intersect(s1, s2):
    """
    s1 = (p1, p2), s2 = (p3, p4). Return True iff the closed segments share
    at least one point. Handles all collinear-overlap and endpoint-touch cases.
    """
    p1, p2 = s1
    p3, p4 = s2
    o1 = orient(p1, p2, p3)
    o2 = orient(p1, p2, p4)
    o3 = orient(p3, p4, p1)
    o4 = orient(p3, p4, p2)

    # General case
    if o1 != o2 and o3 != o4:
        return True

    # Collinear cases
    if o1 == 0 and on_segment(p1, p2, p3):
        return True
    if o2 == 0 and on_segment(p1, p2, p4):
        return True
    if o3 == 0 and on_segment(p3, p4, p1):
        return True
    if o4 == 0 and on_segment(p3, p4, p2):
        return True

    return False


# ---------------------------------------------------------------------------
# 3. Find the actual intersection point (when segments cross properly)
# ---------------------------------------------------------------------------

def intersection_point(s1, s2):
    """
    Return (x, y) of the intersection if segments cross at a single point,
    else None. Uses the standard parametric formula. Returns floats.
    """
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
# 4. Brute-force enumeration (ground truth)
# ---------------------------------------------------------------------------

def find_intersections_brute(segments):
    """
    Return sorted list of (i, j) pairs with i < j where segments[i] and
    segments[j] intersect (boolean).
    """
    pairs = []
    for i in range(len(segments)):
        for j in range(i + 1, len(segments)):
            if segments_intersect(segments[i], segments[j]):
                pairs.append((i, j))
    return sorted(pairs)


# ---------------------------------------------------------------------------
# 5. Simplified sweep line
# ---------------------------------------------------------------------------

def normalize(segments):
    """Ensure each segment's first endpoint has smaller x (ties: smaller y)."""
    out = []
    for p, q in segments:
        if (p[0], p[1]) <= (q[0], q[1]):
            out.append((p, q))
        else:
            out.append((q, p))
    return out


def find_intersections_sweep(segments):
    """
    Event-driven sweep. Active set kept as a plain list; we check neighbors
    by y-at-sweep-x whenever a segment is inserted/removed.

    Returns sorted list of intersecting (i, j) pairs.
    """
    segs = normalize(segments)
    n = len(segs)

    # Event types: 0=start, 1=end. (Process start before end at same x.)
    events = []
    for i, (p, q) in enumerate(segs):
        events.append((p[0], 0, p[1], i))   # start
        events.append((q[0], 1, q[1], i))   # end
    heapq.heapify(events)

    active = []   # list of segment indices, sorted by current y-at-sweep
    found = set()

    def y_at(i, x):
        """y of segment i at sweep x. For vertical segments use endpoint y."""
        (x1, y1), (x2, y2) = segs[i]
        if x2 == x1:
            return (y1 + y2) / 2.0   # vertical: midpoint heuristic
        t = (x - x1) / (x2 - x1)
        return y1 + t * (y2 - y1)

    def check_pair(i, j):
        a, b = min(i, j), max(i, j)
        if (a, b) in found:
            return
        if segments_intersect(segs[a], segs[b]):
            found.add((a, b))

    while events:
        x, kind, y, idx = heapq.heappop(events)
        if kind == 0:
            active.append(idx)
        else:
            if idx in active:
                active.remove(idx)
        # Re-sort active by y at the current sweep x (lazy approach)
        active.sort(key=lambda i: y_at(i, x))
        # Check every adjacent pair currently in the active set
        for k in range(len(active) - 1):
            check_pair(active[k], active[k + 1])

    return sorted(found)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 145: Line Segment Intersection")
    print("=" * 60)

    # X pattern
    segs = [((0, 0), (4, 4)),
            ((0, 4), (4, 0)),
            ((1, 2), (3, 2))]
    print("\n--- X with horizontal bar ---")
    print(f"  brute: {find_intersections_brute(segs)}")
    print(f"  sweep: {find_intersections_sweep(segs)}")

    # Grid of horizontal + vertical
    segs = []
    for y in range(0, 5):
        segs.append(((0, y), (4, y)))
    for x in range(0, 5):
        segs.append(((x, 0), (x, 4)))
    print("\n--- 5x5 grid (5 horizontals + 5 verticals) ---")
    b = find_intersections_brute(segs)
    s = find_intersections_sweep(segs)
    print(f"  brute count = {len(b)}, sweep count = {len(s)}")
    print(f"  match: {b == s}")

    print("\nNote: the simplified sweep above only checks adjacency in the")
    print("currently-active y-ordered set. Real Bentley-Ottmann inserts an")
    print("intersection event for every detected crossing and SWAPS the two")
    print("segments at that event so later neighbors are also checked. The")
    print("brute-force result is the ground truth; the sweep is a teaching")
    print("scaffold that demonstrates the event-driven structure.")

    # Show actual intersection points
    print("\n--- Intersection points ---")
    segs = [((0, 0), (10, 10)),
            ((0, 10), (10, 0)),
            ((5, 0), (5, 10))]
    for i, j in find_intersections_brute(segs):
        pt = intersection_point(segs[i], segs[j])
        print(f"  seg{i} x seg{j}: {pt}")


if __name__ == "__main__":
    demo()
