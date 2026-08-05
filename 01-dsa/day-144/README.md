# Day 144: Convex Hull

## Why It Matters

The convex hull of a point set P is the smallest convex polygon containing
all points in P. It is the most fundamental computational-geometry
primitive — almost every other algorithm in the field calls it as a
subroutine.

- **Collision detection** (GJK uses convex hulls of meshes).
- **Pattern recognition**: shape signatures, image moments.
- **Robotics**: configuration-space obstacles are convex hulls of forbidden
  poses.
- **Statistics**: outlier detection via hull peeling.
- **GIS**: bounding regions for points of interest, smallest enclosing region.

We implement two O(n log n) algorithms:

1. **Graham scan** (1972) — sort by polar angle around the lowest point,
   then walk and pop right turns with a stack.
2. **Andrew's monotone chain** (1979) — sort by (x, y), build upper and
   lower hulls separately. Simpler. No angle arithmetic.

## The Orientation Test (the load-bearing primitive)

Given three points A, B, C, are they a left turn, right turn, or collinear?
Use the **cross product** of (B-A) and (C-B):

```
cross = (B.x - A.x) * (C.y - A.y) - (B.y - A.y) * (C.x - A.x)
> 0  -> counterclockwise (left turn)
< 0  -> clockwise        (right turn)
= 0  -> collinear
```

**Use integers when you can.** Floating-point cross products near zero
silently misclassify collinear points and cause hull bugs that are
impossible to reproduce. For lattice points, this stays exact.

## Graham Scan

1. Find the lowest point P0 (ties broken by leftmost).
2. Sort the rest by polar angle around P0 (atan2 or by cross-product
   comparator). Ties (same angle) sort by distance — keep only the
   farthest.
3. Walk through the sorted points with a stack. While the top two stack
   points plus the new point form a non-left turn, pop.

Time: O(n log n) dominated by sort. O(n) walk.

## Andrew's Monotone Chain

1. Sort by (x, y) ascending.
2. Lower hull: for each point in order, while last two + new form a
   non-left turn, pop. Push.
3. Upper hull: for each point in reverse order, same rule.
4. Concatenate (drop duplicate endpoints).

Time: O(n log n). Code is shorter and only uses cross products — no atan2.

## Edge Cases

- **All points collinear**: the "hull" is a line segment. Algorithms must
  return both endpoints, not the whole segment.
- **Duplicate points**: dedupe first, or the `<= 0` / `< 0` choice in the
  turn predicate matters.
- **n < 3**: hull is the input itself.
- **Numerical**: if you read floating-point coordinates from a file, scale
  to integers (multiply by 10^k, round) before orientation tests.

## Complexity

| Algorithm  | Time         | Space  | Notes                       |
|------------|--------------|--------|-----------------------------|
| Brute      | O(n^3)       | O(1)   | Check every triple          |
| Graham     | O(n log n)   | O(n)   | One sort by angle           |
| Andrew     | O(n log n)   | O(n)   | One sort by coordinates     |
| Chan       | O(n log h)   | O(n)   | h = hull size; output-sensitive |

## Failure Modes (real war stories)

- **Float cross product near zero**: 3 collinear points may give cross
  = 1e-17 due to rounding; a `> 0` predicate then includes them, but the
  symmetric < 0 predicate excludes them. Hull becomes inconsistent.
- **Polar-angle sort with atan2**: 0 and 2π are the same direction but
  atan2 returns -π for some, π for others.
- **Strict vs non-strict turn**: choosing `cross < 0` vs `cross <= 0`
  changes whether collinear hull-edge points are kept.

## Checkpoint Questions

1. Why does sorting by polar angle work for Graham scan?
2. Why does monotone chain need both upper and lower passes?
3. Show via cross product why a left turn means CCW.
4. If you have 10 million 2D points, which algorithm? Why?
5. What's the output if all points are on a line? On a single point?
6. When would you choose strict (> 0) vs non-strict (>= 0) in the pop test?
