# Day 148: Collision Detection (2D Game Objects)

## Why Collision Detection Matters

Every physics engine, every game, every robotics simulation, every CAD tool
must answer one question: **"Did A hit B?"** And it must do so for thousands
of pairs per frame, 60 times per second.

The naive answer — test every pair — is O(n²). For 1000 objects that's
1,000,000 tests per frame, every frame. We need cleverer geometry.

## The Two-Phase Architecture

Real engines split the work:

1. **Broad phase**: Cheap overlap test using simple proxies (AABBs).
   Output: candidate pairs that *might* collide.
2. **Narrow phase**: Exact geometry test (SAT, GJK, polygon clip).
   Output: actual collision data (point, normal, depth).

Broad phase culls 99% of pairs. The narrow phase only sees plausible candidates.

## Axis-Aligned Bounding Boxes (AABB)

An AABB is a rectangle aligned to the world axes — just `(min_x, min_y, max_x, max_y)`.
Two AABBs overlap iff they overlap on *both* axes:

```
A.max_x >= B.min_x  and  B.max_x >= A.min_x
A.max_y >= B.min_y  and  B.max_y >= A.min_y
```

Four float comparisons. The cheapest overlap test you can write. That's why
broad phase uses AABBs even for circles and polygons.

## Broad Phase: Three Algorithms

### 1. Brute Force — O(n²)

Test all pairs. Baseline.

### 2. Sweep and Prune (SAP) — O(n log n + k)

Sort objects by their min_x. Sweep left to right. Maintain an "active list"
of objects whose interval on x overlaps the current sweep position.

**Why it works**: Two AABBs disjoint on x cannot collide. By sorting on x,
we batch all x-coherent objects together. Only those pairs need a full
AABB test.

In games, frame-to-frame coherence makes this near-O(n) — most objects
barely move between frames, so the sorted list stays nearly sorted
(insertion sort is O(n) on nearly-sorted data).

### 3. AABB Tree (BVH) — O(log n) per query

A binary tree where every internal node's AABB encloses both children.
To find collisions for object X:
- Start at root
- Recurse into children whose AABB overlaps X's AABB
- Prune entire subtrees that miss

Build cost: O(n log n). Query: O(log n) amortized. Used by Bullet, Box2D
(dynamic tree), and most modern physics engines.

## Narrow Phase: AABB-vs-AABB and Circle-vs-Circle

This day stays simple: AABBs and circles. The exact tests:

- **AABB vs AABB**: the four-comparison test above.
- **Circle vs Circle**: distance between centers <= sum of radii.
  Use *squared* distance to avoid `sqrt` — faster and avoids precision loss
  near zero.
- **AABB vs Circle**: clamp circle center to the AABB's bounds; check
  distance to clamped point <= radius.

## Failure Modes

1. **Tunneling**: a fast-moving small object passes *through* a thin wall
   between frames. Fix: continuous collision detection (CCD) — test the
   *swept* AABB across the timestep.
2. **Stacked sort instability**: SAP with floating-point coords on equal
   keys can flip-flop, churning the active list. Fix: tie-break by id.
3. **AABB bloat**: rotated long objects have a huge AABB that's mostly
   empty. Fix: OBBs (oriented bounding boxes) or capsules — but lose the
   cheap overlap test.
4. **Tree imbalance**: naive insertion order produces tall trees. Fix:
   surface-area heuristic (SAH) for builds, tree balancing on insert.

## Complexity Summary

| Algorithm | Build | Query (one object) | All-pairs | Space |
|-----------|-------|--------------------|-----------|-------|
| Brute force | — | O(n) | O(n²) | O(1) |
| Sweep and prune | O(n log n) | O(log n + k) | O(n log n + K) | O(n) |
| AABB tree | O(n log n) | O(log n) | O(n log n + K) | O(n) |

K = number of actual overlapping pairs.

## Real-World Usage

| Engine | Broad phase | Narrow phase |
|--------|-------------|--------------|
| Box2D | Dynamic AABB tree | SAT + clipping |
| Bullet | btDbvtBroadphase (AABB tree) | GJK + EPA |
| PhysX | SAP + tree hybrid | GJK + SAT |
| Unity (built-in) | Sweep and prune | Various |

## Checkpoint Questions

1. Why is AABB-vs-AABB four comparisons and not eight (one per corner)?
2. Sweep and prune sorts on x only. Why not sort on both x and y?
3. What's the worst case for an AABB tree, and how does SAH avoid it?
4. Squared-distance circle test: when is it wrong to skip `sqrt`?
5. How does tunneling break collision detection, and why does halving the
   timestep not fully fix it?
6. Why does Box2D use a *dynamic* tree (rebalance on move) instead of a
   static one?
