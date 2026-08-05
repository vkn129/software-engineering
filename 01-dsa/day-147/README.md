# Day 147: Voronoi Diagrams & Delaunay Triangulation

## Why It Matters

Given n "sites" in the plane, the **Voronoi diagram** partitions the plane
into n cells, where cell i contains all points closer to site i than to any
other site. The **Delaunay triangulation** is its dual graph (edge between
sites whose Voronoi cells share an edge).

- **Nearest-neighbor queries**: which post office is closest? Build the
  Voronoi diagram once, locate query points in O(log n).
- **Mesh generation**: Delaunay triangulation maximizes the minimum angle —
  the gold standard for FEM meshes.
- **Cellular network planning**: Voronoi cells model coverage areas.
- **Forest growth / cell biology**: tissue modeling, crystal growth.
- **Robotics path planning**: navigate along Voronoi edges (maximally far
  from obstacles).

## Construction

Three classical O(n log n) algorithms:

1. **Fortune's sweep line (1987)** — the canonical method. A horizontal
   sweep line moves down; a "beach line" of parabolic arcs tracks the
   frontier. Site and circle events drive updates. Robust but intricate.
2. **Divide and conquer** (Shamos-Hoey 1975). Recursive merge of half
   diagrams along a zig-zag.
3. **Incremental** (Bowyer-Watson for Delaunay) — add sites one at a time,
   "flip" edges to restore the Delaunay property. O(n^2) worst case but
   O(n log n) expected for random insertion order.

We implement:

- **Brute O(n^3) Delaunay**: enumerate all triangles, keep those whose
  circumcircle contains no other point. Slow but pedagogically clear.
- **Bowyer-Watson incremental Delaunay**: add sites one at a time,
  remove all triangles whose circumcircle contains the new site, retriangulate
  the resulting "cavity".
- **Voronoi from Delaunay**: each Delaunay triangle's circumcenter is a
  Voronoi vertex; circumcenters of adjacent triangles are connected.

## The Empty Circle Property

A triangle (a, b, c) is Delaunay iff its circumscribed circle contains no
other site in its interior. This is equivalent to the **InCircle** predicate:

```
| ax  ay  ax^2 + ay^2  1 |
| bx  by  bx^2 + by^2  1 |
| cx  cy  cx^2 + cy^2  1 |   > 0   (d inside circle abc, abc CCW)
| dx  dy  dx^2 + dy^2  1 |
```

Or equivalently the "lifted" determinant — paraboloid lift trick. The 4x4
determinant works directly with integers if your inputs are integers.

## Bowyer-Watson Step

To insert site p into the current Delaunay triangulation:

1. Find every triangle T whose circumcircle contains p. These are "bad".
2. The union of bad triangles forms a star-shaped polygon (the **cavity**).
3. Find the **boundary edges** of the cavity (edges of bad triangles that
   are NOT shared with another bad triangle).
4. Remove all bad triangles. Connect p to each boundary edge endpoint.

The whole triangulation must start from a "super-triangle" big enough to
contain all sites; remove super-triangle vertices and their incident
triangles at the end.

## Voronoi from Delaunay

For each Delaunay triangle, compute the circumcenter (the point equidistant
from all three vertices). For each Delaunay edge (a, b), the two triangles
sharing it produce two circumcenters; the segment between them is a Voronoi
edge. Convex-hull edges produce semi-infinite Voronoi rays.

## Complexity

| Operation                   | Best       | This impl       |
|-----------------------------|------------|-----------------|
| Delaunay (Fortune)          | O(n log n) | n/a             |
| Delaunay (Bowyer-Watson)    | O(n log n) expected | O(n^2) here |
| Voronoi from Delaunay       | O(n)       | O(n)            |
| Nearest-site query          | O(log n)   | n/a             |

## Failure Modes

- **Cocircular sites**: four or more sites on one circle make the Delaunay
  triangulation non-unique. Pick any consistent tiebreaker.
- **Three collinear sites**: degenerate — no triangle. Most real
  implementations perturb sites symbolically (SoS technique).
- **Super-triangle too small**: must contain ALL sites with margin. If a
  query circumcircle intersects super-triangle vertices, results are wrong.
- **Float incircle test**: classic source of bugs. Use exact rational
  arithmetic for integer inputs.

## Checkpoint Questions

1. Why is a Voronoi cell always convex?
2. State the InCircle predicate. What sign convention does it use?
3. What's the dual relationship between Voronoi and Delaunay edges?
4. Why does Bowyer-Watson need a super-triangle?
5. When does Delaunay fail to be unique?
6. How does Fortune's algorithm represent the beach line?
