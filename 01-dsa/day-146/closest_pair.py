"""
Day 146: Closest Pair of Points

Divide-and-conquer O(n log n) with the strip optimization.
Returns (distance, (p, q)).

Uses squared distance internally to avoid sqrt in the inner loop;
returns Euclidean distance at the top.
"""

import math


# ---------------------------------------------------------------------------
# 1. Brute force baseline
# ---------------------------------------------------------------------------

def dist2(p, q):
    """Squared Euclidean distance — avoid sqrt for comparisons."""
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def closest_pair_brute(points):
    """O(n^2). Return (distance, (p, q))."""
    n = len(points)
    if n < 2:
        return (float("inf"), None)
    best = float("inf")
    bp = None
    for i in range(n):
        for j in range(i + 1, n):
            d = dist2(points[i], points[j])
            if d < best:
                best = d
                bp = (points[i], points[j])
    return (math.sqrt(best), bp)


# ---------------------------------------------------------------------------
# 2. Divide-and-conquer O(n log n)
# ---------------------------------------------------------------------------

def closest_pair(points):
    """O(n log n) divide & conquer. Returns (distance, (p, q))."""
    if len(points) < 2:
        return (float("inf"), None)
    Px = sorted(points)            # by x then y
    Py = sorted(points, key=lambda p: (p[1], p[0]))
    sq, pair = _closest_pair_rec(Px, Py)
    return (math.sqrt(sq), pair)


def _closest_pair_rec(Px, Py):
    """
    Returns (squared_distance, (p, q)).
    Px: points sorted by x. Py: same points sorted by y.
    """
    n = len(Px)
    if n <= 3:
        # brute
        best = float("inf")
        bp = None
        for i in range(n):
            for j in range(i + 1, n):
                d = dist2(Px[i], Px[j])
                if d < best:
                    best = d
                    bp = (Px[i], Px[j])
        return best, bp

    mid = n // 2
    midx = Px[mid][0]
    Lx, Rx = Px[:mid], Px[mid:]
    Lset = set(Lx)
    # Partition Py into Ly and Ry preserving y order, O(n).
    Ly = [p for p in Py if p in Lset]
    Ry = [p for p in Py if p not in Lset]

    d_left, pair_left = _closest_pair_rec(Lx, Ly)
    d_right, pair_right = _closest_pair_rec(Rx, Ry)

    if d_left < d_right:
        d = d_left
        pair = pair_left
    else:
        d = d_right
        pair = pair_right

    # Strip: points with |x - midx| < sqrt(d). Compare squared.
    d_sqrt = math.sqrt(d)
    strip = [p for p in Py if (p[0] - midx) ** 2 < d]
    for i in range(len(strip)):
        # j only needs to scan while dy^2 < d; this stays O(n) across recursion
        j = i + 1
        while j < len(strip) and (strip[j][1] - strip[i][1]) ** 2 < d:
            dd = dist2(strip[i], strip[j])
            if dd < d:
                d = dd
                pair = (strip[i], strip[j])
            j += 1

    return d, pair


# ---------------------------------------------------------------------------
# 3. K-nearest pairs (small k)
# ---------------------------------------------------------------------------

def k_closest_pairs(points, k):
    """Return the k closest pairs, sorted by distance ascending.
    O(n^2) — for educational comparison vs the O(n log n) single-pair version.
    """
    n = len(points)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((dist2(points[i], points[j]), points[i], points[j]))
    pairs.sort()
    return [(math.sqrt(d), p, q) for d, p, q in pairs[:k]]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo():
    print("=" * 60)
    print("Day 146: Closest Pair of Points")
    print("=" * 60)

    pts = [(0, 0), (4, 4), (1, 1), (5, 1), (3, 2)]
    print(f"\n  points = {pts}")
    d, pair = closest_pair_brute(pts)
    print(f"  brute:   d = {d:.4f}, pair = {pair}")
    d, pair = closest_pair(pts)
    print(f"  D&C:     d = {d:.4f}, pair = {pair}")

    # randomized check vs brute
    import random
    random.seed(123)
    for trial in range(5):
        n = random.randint(2, 50)
        pts = list({(random.randint(0, 200), random.randint(0, 200))
                    for _ in range(n)})
        if len(pts) < 2:
            continue
        d_brute, _ = closest_pair_brute(pts)
        d_dc, _ = closest_pair(pts)
        agree = abs(d_brute - d_dc) < 1e-9
        print(f"  random trial n={len(pts):3d}: brute={d_brute:.4f} "
              f"dc={d_dc:.4f} agree={agree}")

    # performance peek
    import time
    random.seed(7)
    pts = [(random.random(), random.random()) for _ in range(2000)]
    t = time.perf_counter()
    d1, _ = closest_pair_brute(pts)
    t_brute = time.perf_counter() - t
    t = time.perf_counter()
    d2, _ = closest_pair(pts)
    t_dc = time.perf_counter() - t
    print(f"\n  n=2000: brute {t_brute:.3f}s, dc {t_dc:.3f}s, "
          f"same={abs(d1 - d2) < 1e-9}, speedup {t_brute / t_dc:.1f}x")


if __name__ == "__main__":
    demo()
