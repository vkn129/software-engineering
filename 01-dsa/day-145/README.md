# Day 145: Line Segment Intersection (Sweep Line)

## Why It Matters

"Find all intersections among n line segments" is the workhorse of
computational geometry: map overlays in GIS, layout verification in VLSI
design, collision detection at coarse scale, and constructive solid
geometry.

Naive: check every pair, O(n^2). For 10^5 segments that's 10^10 checks —
intractable. The **Bentley-Ottmann sweep line** runs in O((n + k) log n)
where k is the number of intersections — output-sensitive and beautiful.

## The Sweep Line Idea

Imagine a vertical line sweeping left to right across the plane. The
algorithm tracks the segments currently intersecting the sweep line,
ordered by their y at the sweep's x. **Two segments can only intersect
when they are adjacent in this y-ordered set.** That's the key insight.

### Events

The sweep stops at three event types:

1. **Start event** (left endpoint): insert segment into active set.
2. **End event** (right endpoint): remove segment.
3. **Intersection event**: report it; swap the two segments' positions;
   check new neighbors for upcoming intersections.

Events are processed in left-to-right order using a priority queue.

### Why Adjacency Suffices

Two segments swap positions in the active set exactly at their
intersection. Just before the swap they must have been adjacent (sweeps
in y-order). So we only need to check each pair when they BECOME
neighbors, which happens O(n + k) times total.

## Simplified Version We Implement

Full Bentley-Ottmann requires a balanced BST keyed by y-on-sweep — that's
a lot of machinery in plain Python. We implement two variants:

1. **Brute force** O(n^2) — every pair, with proper segment-segment
   intersection geometry. Use this as ground truth.
2. **Simplified sweep**: event-driven, but keep the active set as a sorted
   list and re-sort lazily. O(n log n + k * something). Loses the optimal
   bound but is correct and easier to verify.

## Segment-Segment Intersection

Given segments AB and CD, they intersect iff the orientations
`(A, B, C)` and `(A, B, D)` differ in sign AND `(C, D, A)` and
`(C, D, B)` differ in sign — plus collinear-overlap cases.

Use integer cross products for exact orientation.

## Complexity

| Algorithm        | Time              | Notes                          |
|------------------|-------------------|--------------------------------|
| Brute force      | O(n^2)            | Check every pair               |
| Bentley-Ottmann  | O((n+k) log n)    | Output-sensitive               |
| Chazelle 1990    | O(n log n + k)    | Optimal, hugely complex        |

k = number of intersections.

## Failure Modes

- **Vertical segments**: x is constant; "y at sweep x" is undefined when
  sweep is on the segment. Need a careful comparator or jitter.
- **Multiple segments through one point**: classical BO has bugs here.
  Use the Bentley-Ottmann + Hopcroft variant or Mulmuley's randomized
  algorithm for robust handling.
- **Endpoint coincidences**: an endpoint of one segment lying ON another
  segment counts as an intersection, but degenerate handling differs by
  application.
- **Floating point**: cross products of double-precision coordinates can
  return tiny nonzero values for "obviously collinear" inputs. Stick to
  integers or rationals when possible.

## Checkpoint Questions

1. Why are only adjacent segments in the active set candidates for
   intersection?
2. What three event types does Bentley-Ottmann handle? In what order?
3. Why is the algorithm output-sensitive (depends on k)?
4. How do you handle a vertical segment?
5. Sketch the segment-segment intersection test using cross products only.
6. When would you prefer the brute O(n^2) algorithm?
