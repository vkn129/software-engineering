"""
Day 148 Practice: Collision Detection

6 exercises: AABB overlap, circle, broad phase, sweep-and-prune, AABB tree.
Implement the TODO functions, then run: python practice.py
"""


# ===================================================================
# Provided: minimal AABB used by exercises
# ===================================================================

class AABB:
    __slots__ = ("min_x", "min_y", "max_x", "max_y", "id")

    def __init__(self, min_x, min_y, max_x, max_y, id=None):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.id = id


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: AABB overlap test
# ===================================================================
# Return True iff the two AABBs share any area (edge touch counts).

def aabb_overlap(a, b):
    """a, b: AABB. Return True if they overlap."""
    # TODO: implement
    pass


def _sol_aabb_overlap(a, b):
    return (a.max_x >= b.min_x and b.max_x >= a.min_x and
            a.max_y >= b.min_y and b.max_y >= a.min_y)


# ===================================================================
# Exercise 2: Circle-vs-circle (squared-distance test)
# ===================================================================
# Use SQUARED distance — do not call sqrt.

def circles_overlap(cx1, cy1, r1, cx2, cy2, r2):
    """Return True if the two circles overlap (touching counts)."""
    # TODO: implement with squared distance
    pass


def _sol_circles_overlap(cx1, cy1, r1, cx2, cy2, r2):
    dx, dy = cx1 - cx2, cy1 - cy2
    rsum = r1 + r2
    return dx * dx + dy * dy <= rsum * rsum


# ===================================================================
# Exercise 3: Brute-force all-pairs collisions
# ===================================================================
# Return sorted list of (id_lo, id_hi) pairs that overlap.

def brute_force_pairs(boxes):
    """boxes: list of AABB with .id set. Returns sorted list of (lo, hi)."""
    # TODO: implement
    pass


def _sol_brute_force_pairs(boxes):
    pairs = []
    n = len(boxes)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = boxes[i], boxes[j]
            if (a.max_x >= b.min_x and b.max_x >= a.min_x and
                    a.max_y >= b.min_y and b.max_y >= a.min_y):
                lo, hi = (a.id, b.id) if a.id < b.id else (b.id, a.id)
                pairs.append((lo, hi))
    return sorted(pairs)


# ===================================================================
# Exercise 4: Sweep-and-prune
# ===================================================================
# Sort by min_x and prune by the active list. Output sorted (lo, hi) pairs.

def sweep_and_prune(boxes):
    """Return sorted list of (lo, hi) pairs that overlap."""
    # TODO: implement
    pass


def _sol_sweep_and_prune(boxes):
    sorted_b = sorted(boxes, key=lambda b: (b.min_x, b.id))
    active = []
    pairs = []
    for b in sorted_b:
        active = [a for a in active if a.max_x >= b.min_x]
        for a in active:
            if a.max_y >= b.min_y and b.max_y >= a.min_y:
                lo, hi = (a.id, b.id) if a.id < b.id else (b.id, a.id)
                pairs.append((lo, hi))
        active.append(b)
    return sorted(pairs)


# ===================================================================
# Exercise 5: AABB-vs-Circle (clamp-and-test)
# ===================================================================

def aabb_vs_circle(box, cx, cy, r):
    """Return True if the circle and AABB overlap."""
    # TODO: clamp (cx,cy) to box, check squared distance vs r*r
    pass


def _sol_aabb_vs_circle(box, cx, cy, r):
    qx = max(box.min_x, min(cx, box.max_x))
    qy = max(box.min_y, min(cy, box.max_y))
    dx, dy = cx - qx, cy - qy
    return dx * dx + dy * dy <= r * r


# ===================================================================
# Exercise 6: Build AABB tree, then query
# ===================================================================
# Build a tree from `boxes` and return list of leaf ids that overlap `query`.

class _Node:
    __slots__ = ("box", "left", "right", "leaf_id")

    def __init__(self, box, left=None, right=None, leaf_id=None):
        self.box = box
        self.left = left
        self.right = right
        self.leaf_id = leaf_id


def aabb_tree_query(boxes, query):
    """Build tree from `boxes`, return sorted leaf ids overlapping `query`."""
    # TODO: implement
    pass


def _sol_aabb_tree_query(boxes, query):
    def overlaps(a, b):
        return (a.max_x >= b.min_x and b.max_x >= a.min_x and
                a.max_y >= b.min_y and b.max_y >= a.min_y)

    def union(a, b):
        return AABB(min(a.min_x, b.min_x), min(a.min_y, b.min_y),
                    max(a.max_x, b.max_x), max(a.max_y, b.max_y))

    def build(items):
        if len(items) == 1:
            return _Node(items[0], leaf_id=items[0].id)
        bb = items[0]
        for b in items[1:]:
            bb = union(bb, b)
        if (bb.max_x - bb.min_x) >= (bb.max_y - bb.min_y):
            items.sort(key=lambda b: (b.min_x + b.max_x) * 0.5)
        else:
            items.sort(key=lambda b: (b.min_y + b.max_y) * 0.5)
        mid = len(items) // 2
        return _Node(bb, build(items[:mid]), build(items[mid:]))

    if not boxes:
        return []
    root = build(list(boxes))
    hits = []
    stack = [root]
    while stack:
        n = stack.pop()
        if not overlaps(n.box, query):
            continue
        if n.leaf_id is not None:
            hits.append(n.leaf_id)
        else:
            stack.append(n.left)
            stack.append(n.right)
    return sorted(hits)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    # --- Exercise 1 ---
    print("Exercise 1: AABB Overlap")
    a = AABB(0, 0, 10, 10)
    b = AABB(5, 5, 15, 15)
    c = AABB(20, 20, 30, 30)
    d = AABB(10, 10, 12, 12)  # edge-touch
    check("clear overlap", try_or_sol("aabb_overlap", a, b), True)
    check("disjoint", try_or_sol("aabb_overlap", a, c), False)
    check("edge touch", try_or_sol("aabb_overlap", a, d), True)

    # --- Exercise 2 ---
    print("\nExercise 2: Circle vs Circle")
    check("clear overlap", try_or_sol("circles_overlap", 0, 0, 5, 3, 4, 1), True)
    check("disjoint", try_or_sol("circles_overlap", 0, 0, 1, 10, 0, 1), False)
    check("touching", try_or_sol("circles_overlap", 0, 0, 5, 8, 0, 3), True)

    # --- Exercise 3 ---
    print("\nExercise 3: Brute Force Pairs")
    boxes = [
        AABB(0, 0, 10, 10, id=0),
        AABB(5, 5, 15, 15, id=1),
        AABB(20, 20, 30, 30, id=2),
        AABB(12, 12, 25, 25, id=3),
    ]
    pairs = try_or_sol("brute_force_pairs", boxes)
    check("expected pairs", pairs, [(0, 1), (1, 3), (2, 3)])

    # --- Exercise 4 ---
    print("\nExercise 4: Sweep and Prune")
    pairs = try_or_sol("sweep_and_prune", boxes)
    check("matches brute force", pairs, [(0, 1), (1, 3), (2, 3)])

    # --- Exercise 5 ---
    print("\nExercise 5: AABB vs Circle")
    box = AABB(0, 0, 10, 10)
    check("inside", try_or_sol("aabb_vs_circle", box, 5, 5, 1), True)
    check("corner hit", try_or_sol("aabb_vs_circle", box, 11, 11, 2), True)
    check("far", try_or_sol("aabb_vs_circle", box, 100, 100, 1), False)

    # --- Exercise 6 ---
    print("\nExercise 6: AABB Tree Query")
    boxes2 = [
        AABB(0, 0, 5, 5, id=0),
        AABB(10, 10, 15, 15, id=1),
        AABB(20, 20, 25, 25, id=2),
        AABB(2, 2, 12, 12, id=3),
    ]
    q = AABB(4, 4, 6, 6, id=-1)
    hits = try_or_sol("aabb_tree_query", boxes2, q)
    check("query hits", hits, [0, 3])

    q2 = AABB(30, 30, 40, 40, id=-1)
    check("no hits", try_or_sol("aabb_tree_query", boxes2, q2), [])

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
