"""
Day 148: Collision Detection — 2D Game Objects

Broad phase (cheap culling) + narrow phase (exact test).
Three broad-phase algorithms: brute force, sweep-and-prune, AABB tree.
"""

import math
import random
import time


# ---------------------------------------------------------------------------
# 1. AABB primitive
# ---------------------------------------------------------------------------

class AABB:
    """Axis-aligned bounding box. (min_x, min_y, max_x, max_y)."""

    __slots__ = ("min_x", "min_y", "max_x", "max_y", "id")

    def __init__(self, min_x, min_y, max_x, max_y, id=None):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.id = id

    def overlaps(self, other):
        # Four float comparisons. Cheapest geometry test in 2D.
        return (self.max_x >= other.min_x and other.max_x >= self.min_x and
                self.max_y >= other.min_y and other.max_y >= self.min_y)

    def area(self):
        return (self.max_x - self.min_x) * (self.max_y - self.min_y)

    def union(self, other):
        return AABB(
            min(self.min_x, other.min_x), min(self.min_y, other.min_y),
            max(self.max_x, other.max_x), max(self.max_y, other.max_y),
        )

    def __repr__(self):
        return f"AABB({self.min_x:.1f},{self.min_y:.1f},{self.max_x:.1f},{self.max_y:.1f})"


# ---------------------------------------------------------------------------
# 2. Narrow-phase exact tests
# ---------------------------------------------------------------------------

def circle_vs_circle(cx1, cy1, r1, cx2, cy2, r2):
    """Squared-distance test — avoid sqrt for speed and precision."""
    dx, dy = cx1 - cx2, cy1 - cy2
    rsum = r1 + r2
    return dx * dx + dy * dy <= rsum * rsum


def aabb_vs_circle(box, cx, cy, r):
    """Clamp center to AABB, then check distance to clamped point."""
    qx = max(box.min_x, min(cx, box.max_x))
    qy = max(box.min_y, min(cy, box.max_y))
    dx, dy = cx - qx, cy - qy
    return dx * dx + dy * dy <= r * r


# ---------------------------------------------------------------------------
# 3. Brute force broad phase — O(n^2)
# ---------------------------------------------------------------------------

def brute_force_pairs(boxes):
    """Test every pair. Baseline."""
    pairs = []
    n = len(boxes)
    for i in range(n):
        for j in range(i + 1, n):
            if boxes[i].overlaps(boxes[j]):
                pairs.append((boxes[i].id, boxes[j].id))
    return pairs


# ---------------------------------------------------------------------------
# 4. Sweep and Prune — O(n log n + k)
# ---------------------------------------------------------------------------

def sweep_and_prune(boxes):
    """
    Sort by min_x. Sweep left to right with an active list of boxes
    whose x-interval still extends past the sweep position.
    Only pairs in the active list need a full AABB test.
    """
    # Sort by min_x. Tie-break by id to avoid sort instability churn.
    sorted_boxes = sorted(boxes, key=lambda b: (b.min_x, b.id))
    active = []  # boxes whose max_x >= current sweep
    pairs = []

    for b in sorted_boxes:
        # Prune: drop boxes from active list that ended before b begins.
        active = [a for a in active if a.max_x >= b.min_x]
        # Test b against all still-active boxes (x overlap guaranteed).
        for a in active:
            # x overlap is guaranteed; only need y check.
            if a.max_y >= b.min_y and b.max_y >= a.min_y:
                lo, hi = (a.id, b.id) if a.id < b.id else (b.id, a.id)
                pairs.append((lo, hi))
        active.append(b)
    return pairs


# ---------------------------------------------------------------------------
# 5. AABB Tree (BVH) — O(log n) per query
# ---------------------------------------------------------------------------

class AABBNode:
    __slots__ = ("box", "left", "right", "leaf_id")

    def __init__(self, box, left=None, right=None, leaf_id=None):
        self.box = box
        self.left = left
        self.right = right
        self.leaf_id = leaf_id  # set on leaves only


class AABBTree:
    """
    Top-down BVH build. Splits on the longer axis using the median.
    Query collects all leaves whose AABB overlaps the query box.
    """

    def __init__(self, boxes):
        self.root = self._build(list(boxes)) if boxes else None

    def _build(self, boxes):
        if len(boxes) == 1:
            b = boxes[0]
            return AABBNode(b, leaf_id=b.id)

        # Enclosing AABB
        bb = boxes[0]
        for b in boxes[1:]:
            bb = bb.union(b)

        # Split on longer axis
        if (bb.max_x - bb.min_x) >= (bb.max_y - bb.min_y):
            boxes.sort(key=lambda b: (b.min_x + b.max_x) * 0.5)
        else:
            boxes.sort(key=lambda b: (b.min_y + b.max_y) * 0.5)

        mid = len(boxes) // 2
        return AABBNode(bb, self._build(boxes[:mid]), self._build(boxes[mid:]))

    def query(self, box):
        """All leaf ids whose AABB overlaps `box`."""
        hits = []
        if self.root is None:
            return hits
        stack = [self.root]
        while stack:
            node = stack.pop()
            if not node.box.overlaps(box):
                continue
            if node.leaf_id is not None:
                if node.leaf_id != box.id:
                    hits.append(node.leaf_id)
            else:
                stack.append(node.left)
                stack.append(node.right)
        return hits

    def all_pairs(self, boxes):
        """All overlapping pairs by querying each box."""
        seen = set()
        for b in boxes:
            for other_id in self.query(b):
                lo, hi = (b.id, other_id) if b.id < other_id else (other_id, b.id)
                seen.add((lo, hi))
        return sorted(seen)


# ---------------------------------------------------------------------------
# 6. Demos
# ---------------------------------------------------------------------------

def make_random_boxes(n, world=1000.0, max_size=20.0, seed=42):
    random.seed(seed)
    boxes = []
    for i in range(n):
        x = random.uniform(0, world)
        y = random.uniform(0, world)
        w = random.uniform(1, max_size)
        h = random.uniform(1, max_size)
        boxes.append(AABB(x, y, x + w, y + h, id=i))
    return boxes


def demo_basics():
    print("=" * 60)
    print("DEMO 1: AABB and Narrow-Phase Primitives")
    print("=" * 60)
    a = AABB(0, 0, 10, 10, id="A")
    b = AABB(5, 5, 15, 15, id="B")
    c = AABB(20, 20, 30, 30, id="C")
    print(f"A overlaps B: {a.overlaps(b)} (expect True)")
    print(f"A overlaps C: {a.overlaps(c)} (expect False)")
    print(f"Circle (0,0,r=5) vs Circle (3,4,r=1): "
          f"{circle_vs_circle(0,0,5,3,4,1)} (expect True)")
    print(f"AABB A vs Circle (12,12,r=3): {aabb_vs_circle(a,12,12,3)} (expect True)")


def demo_compare_broadphase():
    print("\n" + "=" * 60)
    print("DEMO 2: Brute Force vs Sweep-and-Prune vs AABB Tree")
    print("=" * 60)
    boxes = make_random_boxes(500, world=200, max_size=8)

    t0 = time.perf_counter()
    bf = sorted(brute_force_pairs(boxes))
    t_bf = time.perf_counter() - t0

    t0 = time.perf_counter()
    sap = sorted(sweep_and_prune(boxes))
    t_sap = time.perf_counter() - t0

    t0 = time.perf_counter()
    tree = AABBTree(boxes)
    bvh = tree.all_pairs(boxes)
    t_bvh = time.perf_counter() - t0

    print(f"500 boxes:")
    print(f"  Brute force:    {t_bf*1000:7.2f} ms  pairs={len(bf)}")
    print(f"  Sweep-and-prune:{t_sap*1000:7.2f} ms  pairs={len(sap)}")
    print(f"  AABB tree:      {t_bvh*1000:7.2f} ms  pairs={len(bvh)}")
    print(f"  Results agree:  {bf == sap == bvh}")


def demo_tree_query():
    print("\n" + "=" * 60)
    print("DEMO 3: AABB Tree single-object query")
    print("=" * 60)
    boxes = make_random_boxes(200, world=100, max_size=5)
    tree = AABBTree(boxes)
    probe = AABB(40, 40, 60, 60, id=-1)
    hits = tree.query(probe)
    print(f"Probe {probe} hits {len(hits)} boxes")


if __name__ == "__main__":
    demo_basics()
    demo_compare_broadphase()
    demo_tree_query()
