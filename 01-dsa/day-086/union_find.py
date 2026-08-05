"""
Day 86: Union-Find (Disjoint Set Union) — From Scratch

Near-O(1) amortized operations for dynamic connectivity.
Two optimizations turn a naive O(n) into O(α(n)) ≈ O(1).
"""

import time
import random


# ---------------------------------------------------------------------------
# 1. Naive Union-Find (for comparison)
# ---------------------------------------------------------------------------

class NaiveUnionFind:
    """No optimizations — follow parent chain to root."""

    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx != ry:
            self.parent[ry] = rx  # arbitrary attachment
            return True
        return False


# ---------------------------------------------------------------------------
# 2. Optimized Union-Find (rank + path compression)
# ---------------------------------------------------------------------------

class UnionFind:
    """
    Union by rank + path compression = O(α(n)) per operation.

    rank: upper bound on tree height (doesn't shrink with compression)
    path compression: every find makes nodes point directly to root
    """

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of components

    def find(self, x):
        # Path compression: make every node on the path point to root
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        # Union by rank: attach shorter tree under taller
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1

        self.count -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def component_count(self):
        return self.count


# ---------------------------------------------------------------------------
# 3. Union-Find with Size Tracking
# ---------------------------------------------------------------------------

class UnionFindSize:
    """
    Union by size + path compression.
    Tracks component sizes — useful for queries like "how big is x's group?"
    """

    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False

        # Attach smaller to larger
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]

        self.count -= 1
        return True

    def component_size(self, x):
        return self.size[self.find(x)]

    def largest_component(self):
        return max(self.size[self.find(i)] for i in range(len(self.parent)))


# ---------------------------------------------------------------------------
# 4. Weighted Union-Find (track relative offsets)
# ---------------------------------------------------------------------------

class WeightedUnionFind:
    """
    Track a weight/distance from each element to its root.
    Useful for: "what's the relative position of x vs y?"

    Invariant: actual_weight[x] = weight[x] + weight[parent[x]] + ... + weight[root]
    """

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.weight = [0] * n  # weight from node to parent

    def find(self, x):
        """Returns (root, weight_from_x_to_root)."""
        if self.parent[x] == x:
            return x, 0
        root, w = self.find(self.parent[x])
        self.weight[x] += w  # accumulate weight to root
        self.parent[x] = root  # path compression
        return root, self.weight[x]

    def union(self, x, y, w):
        """
        Assert that weight[x] - weight[y] = w.
        i.e., x is w units "above" y.
        """
        rx, wx = self.find(x)
        ry, wy = self.find(y)
        if rx == ry:
            return wx - wy == w  # check consistency

        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
            self.weight[rx] = wy - wx + w
        else:
            self.parent[ry] = rx
            self.weight[ry] = wx - wy - w
            if self.rank[rx] == self.rank[ry]:
                self.rank[rx] += 1
        return True

    def diff(self, x, y):
        """Return weight[x] - weight[y], or None if not connected."""
        rx, wx = self.find(x)
        ry, wy = self.find(y)
        if rx != ry:
            return None
        return wx - wy


# ---------------------------------------------------------------------------
# 5. Percolation Simulation
# ---------------------------------------------------------------------------

def percolation(n, open_cells):
    """
    n×n grid. open_cells is list of (row, col) to open.
    Returns the number of cells opened when the grid first percolates
    (water flows from top row to bottom row).

    Uses virtual top (n*n) and virtual bottom (n*n+1) nodes.
    """
    uf = UnionFind(n * n + 2)
    VIRTUAL_TOP = n * n
    VIRTUAL_BOTTOM = n * n + 1

    grid = [[False] * n for _ in range(n)]

    def idx(r, c):
        return r * n + c

    for step, (r, c) in enumerate(open_cells, 1):
        grid[r][c] = True
        cell = idx(r, c)

        # Connect to virtual nodes
        if r == 0:
            uf.union(cell, VIRTUAL_TOP)
        if r == n - 1:
            uf.union(cell, VIRTUAL_BOTTOM)

        # Connect to open neighbors
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc]:
                uf.union(cell, idx(nr, nc))

        if uf.connected(VIRTUAL_TOP, VIRTUAL_BOTTOM):
            return step

    return -1  # never percolated


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic Union-Find Operations")
    print("=" * 60)

    uf = UnionFind(10)
    print(f"\n10 elements, each in its own set")
    print(f"Components: {uf.component_count()}")

    unions = [(0, 1), (2, 3), (4, 5), (6, 7), (0, 2), (4, 6), (0, 4)]
    for u, v in unions:
        uf.union(u, v)
        print(f"  Union({u}, {v}) → {uf.component_count()} components")

    print(f"\nConnected(0, 7): {uf.connected(0, 7)}")
    print(f"Connected(0, 8): {uf.connected(0, 8)}")
    print(f"Connected(8, 9): {uf.connected(8, 9)}")


def demo_naive_vs_optimized():
    print("\n" + "=" * 60)
    print("DEMO 2: Naive vs Optimized Performance")
    print("=" * 60)

    n = 100000
    random.seed(42)
    ops = [(random.randint(0, n-1), random.randint(0, n-1)) for _ in range(n)]

    # Naive
    naive = NaiveUnionFind(n)
    start = time.perf_counter()
    for u, v in ops:
        naive.union(u, v)
    for u, v in ops[:1000]:
        naive.find(u)
    naive_time = time.perf_counter() - start

    # Optimized
    opt = UnionFind(n)
    start = time.perf_counter()
    for u, v in ops:
        opt.union(u, v)
    for u, v in ops[:1000]:
        opt.find(u)
    opt_time = time.perf_counter() - start

    print(f"\n{n} union + 1000 find operations:")
    print(f"  Naive:     {naive_time:.4f}s")
    print(f"  Optimized: {opt_time:.4f}s")
    print(f"  Speedup:   {naive_time/opt_time:.1f}x")


def demo_component_sizes():
    print("\n" + "=" * 60)
    print("DEMO 3: Component Size Tracking")
    print("=" * 60)

    uf = UnionFindSize(10)

    # Build some components
    for u, v in [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7), (7, 8)]:
        uf.union(u, v)

    print(f"\nComponents: {uf.count}")
    for v in range(10):
        print(f"  Vertex {v}: component size = {uf.component_size(v)}")
    print(f"Largest component: {uf.largest_component()}")


def demo_weighted():
    print("\n" + "=" * 60)
    print("DEMO 4: Weighted Union-Find (Relative Offsets)")
    print("=" * 60)

    # Scenario: measuring relative heights
    # A is 3 above B, B is 2 above C, D is 5 above E
    wuf = WeightedUnionFind(5)  # A=0, B=1, C=2, D=3, E=4

    wuf.union(0, 1, 3)   # A is 3 above B
    wuf.union(1, 2, 2)   # B is 2 above C

    print(f"\nA is 3 above B, B is 2 above C")
    print(f"  A - C = {wuf.diff(0, 2)} (should be 5)")
    print(f"  B - A = {wuf.diff(1, 0)} (should be -3)")

    wuf.union(3, 4, 5)   # D is 5 above E
    print(f"\nD is 5 above E")
    print(f"  D - E = {wuf.diff(3, 4)} (should be 5)")
    print(f"  A - D = {wuf.diff(0, 3)} (should be None, different groups)")


def demo_percolation():
    print("\n" + "=" * 60)
    print("DEMO 5: Percolation Simulation")
    print("=" * 60)

    n = 10
    random.seed(42)

    # Generate random opening order
    all_cells = [(r, c) for r in range(n) for c in range(n)]
    random.shuffle(all_cells)

    step = percolation(n, all_cells)
    threshold = step / (n * n)

    print(f"\n{n}×{n} grid, opening cells randomly")
    print(f"Percolated after opening {step}/{n*n} cells")
    print(f"Percolation threshold: {threshold:.3f}")
    print(f"(Theoretical threshold for 2D grid: ~0.593)")


if __name__ == "__main__":
    demo_basic()
    demo_naive_vs_optimized()
    demo_component_sizes()
    demo_weighted()
    demo_percolation()
