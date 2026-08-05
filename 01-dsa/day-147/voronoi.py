"""
Day 147: Voronoi Diagrams & Delaunay Triangulation

Implementation strategy:
  - Bowyer-Watson incremental Delaunay triangulation.
  - Voronoi diagram: per triangle compute circumcenter; connect circumcenters
    of triangles sharing a Delaunay edge.

Numerics: incircle test uses the 4x4 determinant, which stays integer-exact
when inputs are integers. Circumcenters are floats.
"""

import math


# ---------------------------------------------------------------------------
# 1. Geometric primitives
# ---------------------------------------------------------------------------

def orient(a, b, c):
    """+1 CCW, -1 CW, 0 collinear."""
    v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return (v > 0) - (v < 0)


def in_circle(a, b, c, d):
    """
    Return True iff d lies strictly inside the circumscribed circle of
    triangle (a, b, c). Assumes (a, b, c) is CCW.

    Determinant test:
      | ax-dx  ay-dy  (ax-dx)^2 + (ay-dy)^2 |
      | bx-dx  by-dy  (bx-dx)^2 + (by-dy)^2 | > 0
      | cx-dx  cy-dy  (cx-dx)^2 + (cy-dy)^2 |

    Integer-exact when inputs are integers.
    """
    ax, ay = a[0] - d[0], a[1] - d[1]
    bx, by = b[0] - d[0], b[1] - d[1]
    cx, cy = c[0] - d[0], c[1] - d[1]
    det = (ax * (by * (cx * cx + cy * cy) - cy * (bx * bx + by * by))
         - ay * (bx * (cx * cx + cy * cy) - cx * (bx * bx + by * by))
         + (ax * ax + ay * ay) * (bx * cy - by * cx))
    return det > 0


def circumcenter(a, b, c):
    """
    Return (cx, cy) — the circumcenter of triangle (a, b, c). Returns
    None for degenerate (collinear) triangles.
    """
    ax, ay = a
    bx, by = b
    cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if d == 0:
        return None
    ux = ((ax * ax + ay * ay) * (by - cy)
        + (bx * bx + by * by) * (cy - ay)
        + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx)
        + (bx * bx + by * by) * (ax - cx)
        + (cx * cx + cy * cy) * (bx - ax)) / d
    return (ux, uy)


# ---------------------------------------------------------------------------
# 2. Bowyer-Watson incremental Delaunay
# ---------------------------------------------------------------------------

def delaunay(points):
    """
    Return list of triangles, each a tuple of 3 point tuples.
    Assumes points have no duplicates and no 4-cocircular points.
    """
    if len(points) < 3:
        return []

    # Super-triangle: enclose all points with margin.
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    dx = maxx - minx
    dy = maxy - miny
    delta = max(dx, dy) * 10 + 10
    s1 = (minx - delta, miny - delta)
    s2 = (maxx + delta, miny - delta)
    s3 = ((minx + maxx) / 2, maxy + delta)
    super_pts = {s1, s2, s3}

    # Ensure CCW
    if orient(s1, s2, s3) < 0:
        s2, s3 = s3, s2

    triangles = [(s1, s2, s3)]

    for p in points:
        bad = []
        for t in triangles:
            a, b, c = t
            if orient(a, b, c) < 0:
                a, b, c = a, c, b
            if in_circle(a, b, c, p):
                bad.append(t)

        # Boundary of the cavity: edges of bad triangles not shared with another.
        edge_count = {}
        for t in bad:
            for e in _edges_of(t):
                key = tuple(sorted(e))
                edge_count[key] = edge_count.get(key, 0) + 1
        boundary = [e for e, c in edge_count.items() if c == 1]

        # Remove bad triangles
        triangles = [t for t in triangles if t not in bad]

        # Retriangulate cavity
        for e in boundary:
            a, b = e
            tri = (a, b, p)
            if orient(*tri) < 0:
                tri = (a, p, b)
            triangles.append(tri)

    # Drop triangles that touch any super-triangle vertex
    return [t for t in triangles if not (set(t) & super_pts)]


def _edges_of(t):
    a, b, c = t
    return [(a, b), (b, c), (c, a)]


# ---------------------------------------------------------------------------
# 3. Voronoi diagram from Delaunay
# ---------------------------------------------------------------------------

def voronoi(points):
    """
    Return (vertices, edges).
      vertices: list of (x, y) — Voronoi vertices = Delaunay circumcenters.
      edges: list of (i, j) — Voronoi edges as index pairs into vertices.
    Bounded edges only (no infinite rays).
    """
    tris = delaunay(points)
    centers = []
    tri_index = {}
    for t in tris:
        c = circumcenter(*t)
        if c is None:
            continue
        idx = len(centers)
        centers.append(c)
        # canonical key for the triangle (sorted vertices)
        tri_index[tuple(sorted(t))] = idx

    # For each pair of triangles sharing an edge, add a Voronoi edge.
    edge_to_tris = {}
    for t in tris:
        key = tuple(sorted(t))
        if key not in tri_index:
            continue
        for e in _edges_of(t):
            ek = tuple(sorted(e))
            edge_to_tris.setdefault(ek, []).append(key)

    voronoi_edges = []
    for ek, ts in edge_to_tris.items():
        if len(ts) == 2:
            i, j = tri_index[ts[0]], tri_index[ts[1]]
            voronoi_edges.append((i, j))
    return centers, voronoi_edges


# ---------------------------------------------------------------------------
# 4. Nearest-site query (brute force — for comparison)
# ---------------------------------------------------------------------------

def nearest_site(query, sites):
    """Return the site closest to query (Euclidean)."""
    best = None
    best_d = float("inf")
    for s in sites:
        d = (s[0] - query[0]) ** 2 + (s[1] - query[1]) ** 2
        if d < best_d:
            best_d = d
            best = s
    return best


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 147: Voronoi & Delaunay")
    print("=" * 60)

    pts = [(0, 0), (4, 0), (0, 4), (4, 4), (2, 2)]
    tris = delaunay(pts)
    print(f"\n  sites = {pts}")
    print(f"  Delaunay triangles ({len(tris)}):")
    for t in tris:
        print(f"    {t}")

    centers, edges = voronoi(pts)
    print(f"\n  Voronoi vertices ({len(centers)}):")
    for c in centers:
        print(f"    ({c[0]:.2f}, {c[1]:.2f})")
    print(f"  Voronoi edges ({len(edges)}):")
    for i, j in edges:
        print(f"    {centers[i]} -- {centers[j]}")

    print("\n--- 4-corners square (cocircular!) ---")
    pts = [(0, 0), (4, 0), (0, 4), (4, 4)]
    tris = delaunay(pts)
    print(f"  triangles: {len(tris)}  (cocircular -> either diagonal works)")
    for t in tris:
        print(f"    {t}")

    print("\n--- Nearest-site verification on random sites ---")
    import random
    random.seed(11)
    sites = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(8)]
    sites = list(set(sites))
    print(f"  {len(sites)} sites")
    for _ in range(5):
        q = (random.randint(0, 100), random.randint(0, 100))
        nearest = nearest_site(q, sites)
        print(f"    query {q} -> nearest site {nearest}")


if __name__ == "__main__":
    demo()
