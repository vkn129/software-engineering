"""
Day 144: Convex Hull

Two O(n log n) algorithms:
  - Graham scan (polar-angle sort, then stack walk)
  - Andrew's monotone chain (sort by x,y, upper + lower hulls)

The orientation test is integer-exact when inputs are integers — prefer
that over atan2 for robustness.
"""

from functools import cmp_to_key


# ---------------------------------------------------------------------------
# Core primitive: orientation via cross product
# ---------------------------------------------------------------------------

def cross(o, a, b):
    """
    Signed area * 2 of triangle (o, a, b).
    > 0  CCW (left turn at a)
    < 0  CW  (right turn at a)
    = 0  collinear
    Integer-exact when inputs are integers.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


# ---------------------------------------------------------------------------
# 1. Andrew's monotone chain
# ---------------------------------------------------------------------------

def convex_hull_andrew(points):
    """
    Return hull vertices in CCW order, starting from the lowest-then-leftmost.
    Collinear hull points are dropped (strict cross > 0 in the keep test).
    """
    pts = sorted(set(points))   # dedupe + sort by (x, y)
    if len(pts) <= 1:
        return pts

    # Lower hull
    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Upper hull
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenate: last of each list is first of the other, drop duplicates
    return lower[:-1] + upper[:-1]


# ---------------------------------------------------------------------------
# 2. Graham scan
# ---------------------------------------------------------------------------

def convex_hull_graham(points):
    """
    Graham scan: find lowest point, sort the rest by polar angle around it
    (using a cross-product comparator — no atan2), then stack-walk.
    """
    pts = list(set(points))
    if len(pts) <= 1:
        return pts

    # Pivot: lowest y, then leftmost x
    pivot = min(pts, key=lambda p: (p[1], p[0]))
    rest = [p for p in pts if p != pivot]

    def compare(a, b):
        # Sort by angle around pivot; ties broken by distance (closer first).
        c = cross(pivot, a, b)
        if c > 0:
            return -1  # a is more CW... wait, cross>0 means CCW from pivot:a to pivot:b
        if c < 0:
            return 1
        # collinear: closer one first
        da = (a[0] - pivot[0]) ** 2 + (a[1] - pivot[1]) ** 2
        db = (b[0] - pivot[0]) ** 2 + (b[1] - pivot[1]) ** 2
        return -1 if da < db else (1 if da > db else 0)

    rest.sort(key=cmp_to_key(compare))

    # Drop interior collinear points: when several points share an angle with
    # pivot, keep only the farthest. After our sort, collinear groups appear
    # contiguously with the farthest LAST.
    filtered = []
    i = 0
    while i < len(rest):
        j = i
        while j + 1 < len(rest) and cross(pivot, rest[i], rest[j + 1]) == 0:
            j += 1
        filtered.append(rest[j])
        i = j + 1

    stack = [pivot]
    for p in filtered:
        while len(stack) >= 2 and cross(stack[-2], stack[-1], p) <= 0:
            stack.pop()
        stack.append(p)
    return stack


# ---------------------------------------------------------------------------
# 3. Hull area and perimeter (shoelace)
# ---------------------------------------------------------------------------

def polygon_area(poly):
    """
    Shoelace formula. Returns unsigned area. Works for any simple polygon
    given in order (CW or CCW).
    """
    n = len(poly)
    if n < 3:
        return 0.0
    s = 0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        s += x1 * y2 - x2 * y1
    return abs(s) / 2.0


def polygon_perimeter(poly):
    n = len(poly)
    if n < 2:
        return 0.0
    total = 0.0
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        total += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return total


# ---------------------------------------------------------------------------
# 4. ASCII visualization
# ---------------------------------------------------------------------------

def visualize(points, hull, width=40, height=20):
    """Render points as '.' and hull vertices as 'O' on an ASCII canvas."""
    if not points:
        return ""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    dx = max(xmax - xmin, 1)
    dy = max(ymax - ymin, 1)
    grid = [[" "] * width for _ in range(height)]

    def project(p):
        col = int((p[0] - xmin) / dx * (width - 1))
        row = int((p[1] - ymin) / dy * (height - 1))
        row = height - 1 - row    # flip y
        return row, col

    for p in points:
        r, c = project(p)
        grid[r][c] = "."
    for p in hull:
        r, c = project(p)
        grid[r][c] = "O"

    return "\n".join("".join(row) for row in grid)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 144: Convex Hull")
    print("=" * 60)

    pts = [(0, 0), (4, 0), (4, 4), (0, 4), (2, 2), (1, 1), (3, 3), (2, 0), (4, 2)]
    h_a = convex_hull_andrew(pts)
    h_g = convex_hull_graham(pts)
    print(f"\n  square + interior, n={len(pts)}")
    print(f"  Andrew:  {h_a}")
    print(f"  Graham:  {h_g}")
    print(f"  area = {polygon_area(h_a)}  perimeter = {polygon_perimeter(h_a):.4f}")

    print("\n  ASCII view (O=hull, .=point):")
    print(visualize(pts, h_a, 30, 12))

    # Collinear case
    print("\n--- All-collinear test ---")
    pts = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    print(f"  Andrew: {convex_hull_andrew(pts)}  (should be endpoints only)")
    print(f"  Graham: {convex_hull_graham(pts)}")

    # Random scatter
    import random
    random.seed(7)
    pts = [(random.randint(0, 50), random.randint(0, 20)) for _ in range(60)]
    h = convex_hull_andrew(pts)
    print(f"\n--- 60 random points (50x20) ---")
    print(f"  hull size = {len(h)}, area = {polygon_area(h):.1f}")
    print(visualize(pts, h, 50, 16))


if __name__ == "__main__":
    demo()
