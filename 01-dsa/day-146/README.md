# Day 146: Closest Pair of Points

## Why It Matters

"Find the two closest points among n in the plane" is a classic divide-and-
conquer success story. Naive: O(n^2) pairwise. Shamos & Hoey (1975):
**O(n log n)** by exploiting the geometric structure.

- **Air-traffic control**: predicted collisions between aircraft.
- **Particle simulation**: nearest-neighbor forces in molecular dynamics.
- **Clustering**: bootstrap step for single-linkage hierarchical clustering.
- **Database joins**: spatial range queries.
- **Robotics**: nearest obstacle in configuration space.

## Divide and Conquer

1. Sort points by x.
2. Split into left half L and right half R at median x.
3. Recursively find closest pair in L (distance dL) and in R (distance dR).
4. Let d = min(dL, dR). The closest pair might still straddle the dividing
   line, with one point in L and one in R. Only points within horizontal
   distance d of the median can be in such a pair.
5. **Strip step**: collect points within d of the median, sort them by y,
   and for each point check the next 7 in y-order. That's O(n) total.

### Why 7 Neighbors Suffice

Consider the strip of width 2d around the median. Inside this strip, no two
points are within distance d of each other (otherwise they'd have been
detected as the closest in their half). Tile the strip with d/2 × d/2
squares; each contains at most 1 point. A point can have a partner within
d only in its own row or the next ~3 rows. Counting unique boxes gives at
most 7 candidates ahead in y-sorted order.

The constant 7 depends on whether you use ≤ d (closed) or < d (open). Some
texts say 6, some 8 — all are correct upper bounds.

## Complexity

| Algorithm     | Time             | Notes                            |
|---------------|------------------|----------------------------------|
| Brute force   | O(n^2)           | All pairs                        |
| D&C           | O(n log n)       | This file                        |
| Randomized    | O(n) expected    | Khuller-Matias 1995              |

Recurrence: T(n) = 2T(n/2) + O(n) -> O(n log n).

To avoid an extra sort in the merge: presort once by y, then split into
upper/lower y-sorted halves during recursion.

## Failure Modes

- **Off-by-one in strip**: include points with `|x - mid| <= d`, not `< d`.
  Points exactly on the line are eligible.
- **Constant in inner loop**: scanning 7 vs 8 vs unlimited matters for big
  inputs. But going past `dy > d` in the y-sorted strip is correct anytime.
- **Distance overflow**: returns float; consider returning squared distance
  if you don't need the actual value (avoids sqrt for n-1 returns).
- **Ties**: multiple pairs at the minimum distance; algorithm should
  consistently return one, but applications might want them all.

## Checkpoint Questions

1. Why does sorting by x make the merge step work?
2. Prove that 7 candidates suffice in the strip step.
3. What if your points lie in 3D — does this approach still give O(n log n)?
4. When would the brute O(n^2) algorithm be faster in practice?
5. How would you adapt to find the closest k pairs?
6. What about closest pair on a sphere (great-circle distance)?
