"""
Day 85: Minimum Spanning Trees — Prim's & Kruskal's From Scratch

Two greedy approaches to connect all vertices with minimum total edge weight.
Both exploit the cut property: the lightest edge across any cut is in the MST.
"""

import heapq
import math
from collections import defaultdict


# ---------------------------------------------------------------------------
# Union-Find (needed by Kruskal's — full version in Day 86)
# ---------------------------------------------------------------------------

class UnionFind:
    """Disjoint set with union by rank and path compression."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.components = n

    def find(self, x):
        # Path compression: point directly to root
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
        self.components -= 1
        return True


# ---------------------------------------------------------------------------
# 1. Prim's Algorithm (grow MST from a seed vertex)
# ---------------------------------------------------------------------------

def prims(adj, n, start=0):
    """
    Prim's MST using a min-heap.

    Like Dijkstra, but the heap key is EDGE WEIGHT (not total distance).
    We always add the cheapest edge connecting the tree to a non-tree vertex.

    Args:
        adj: adjacency list, adj[u] = [(v, weight), ...]
        n: number of vertices
        start: seed vertex

    Returns:
        mst_edges: list of (u, v, weight) in MST
        total_weight: sum of all MST edge weights
    """
    visited = [False] * n
    mst_edges = []
    total_weight = 0

    # Heap entries: (weight, from_vertex, to_vertex)
    heap = [(0, -1, start)]  # dummy edge to start

    while heap and len(mst_edges) < n - 1:
        weight, u, v = heapq.heappop(heap)

        if visited[v]:
            continue

        visited[v] = True
        if u != -1:  # skip the dummy initial edge
            mst_edges.append((u, v, weight))
            total_weight += weight

        for neighbor, w in adj[v]:
            if not visited[neighbor]:
                heapq.heappush(heap, (w, v, neighbor))

    return mst_edges, total_weight


# ---------------------------------------------------------------------------
# 2. Kruskal's Algorithm (sort edges, add if no cycle)
# ---------------------------------------------------------------------------

def kruskals(n, edges):
    """
    Kruskal's MST: sort all edges, greedily add if they don't create a cycle.

    Uses Union-Find to check cycle creation in near-O(1) time.

    Args:
        n: number of vertices (0 to n-1)
        edges: list of (u, v, weight)

    Returns:
        mst_edges: list of (u, v, weight) in MST
        total_weight: sum of all MST edge weights
    """
    sorted_edges = sorted(edges, key=lambda e: e[2])
    uf = UnionFind(n)
    mst_edges = []
    total_weight = 0

    for u, v, w in sorted_edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst_edges.append((u, v, w))
            total_weight += w
            if len(mst_edges) == n - 1:
                break

    return mst_edges, total_weight


# ---------------------------------------------------------------------------
# 3. MST-based Clustering
# ---------------------------------------------------------------------------

def mst_clustering(n, edges, k):
    """
    Cluster n points into k groups by removing k-1 heaviest MST edges.

    This is single-linkage hierarchical clustering. The MST captures
    the "nearest neighbor" structure; cutting heavy edges separates
    distant groups.

    Returns:
        clusters: list of sets, each set contains vertex indices
    """
    mst_edges, _ = kruskals(n, edges)

    # Sort MST edges by weight descending; remove the k-1 heaviest
    mst_edges.sort(key=lambda e: e[2])
    edges_to_keep = mst_edges[:len(mst_edges) - (k - 1)]

    # Build components from remaining edges
    uf = UnionFind(n)
    for u, v, _ in edges_to_keep:
        uf.union(u, v)

    # Group vertices by root
    groups = defaultdict(set)
    for v in range(n):
        groups[uf.find(v)].add(v)

    return list(groups.values())


# ---------------------------------------------------------------------------
# 4. Verify MST Properties
# ---------------------------------------------------------------------------

def verify_mst(n, all_edges, mst_edges):
    """
    Verify that a set of edges forms a valid MST:
    1. Exactly V-1 edges
    2. All vertices connected
    3. No lighter alternative exists (cycle property)
    """
    # Check edge count
    if len(mst_edges) != n - 1:
        return False, f"Expected {n-1} edges, got {len(mst_edges)}"

    # Check connectivity
    uf = UnionFind(n)
    for u, v, _ in mst_edges:
        uf.union(u, v)
    if uf.components != 1:
        return False, f"Not connected: {uf.components} components"

    # Check optimality: for each non-MST edge, it should be ≥ the heaviest
    # edge on the MST path between its endpoints (cycle property)
    mst_set = {(min(u, v), max(u, v)) for u, v, _ in mst_edges}
    mst_adj = defaultdict(list)
    for u, v, w in mst_edges:
        mst_adj[u].append((v, w))
        mst_adj[v].append((u, w))

    for u, v, w in all_edges:
        if (min(u, v), max(u, v)) in mst_set:
            continue
        # Find max edge weight on MST path from u to v (BFS)
        max_on_path = _max_edge_on_path(mst_adj, u, v, n)
        if max_on_path is not None and w < max_on_path:
            return False, f"Edge ({u},{v},{w}) lighter than path max {max_on_path}"

    return True, "Valid MST"


def _max_edge_on_path(adj, start, end, n):
    """Find maximum edge weight on the unique path in a tree."""
    visited = [False] * n
    stack = [(start, 0)]  # (vertex, max_weight_so_far)
    visited[start] = True

    parent = {start: (None, 0)}

    queue = [start]
    while queue:
        u = queue.pop(0)
        for v, w in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = (u, w)
                if v == end:
                    # Trace back to find max
                    max_w = 0
                    curr = end
                    while parent[curr][0] is not None:
                        max_w = max(max_w, parent[curr][1])
                        curr = parent[curr][0]
                    return max_w
                queue.append(v)
    return None


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Prim's vs Kruskal's on Same Graph")
    print("=" * 60)

    # Classic example graph
    edges = [
        (0, 1, 4), (0, 7, 8),
        (1, 2, 8), (1, 7, 11),
        (2, 3, 7), (2, 5, 4), (2, 8, 2),
        (3, 4, 9), (3, 5, 14),
        (4, 5, 10),
        (5, 6, 2),
        (6, 7, 1), (6, 8, 6),
        (7, 8, 7),
    ]
    n = 9

    # Build adjacency list for Prim's
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    prim_mst, prim_total = prims(adj, n)
    kruskal_mst, kruskal_total = kruskals(n, edges)

    print(f"\nGraph: {n} vertices, {len(edges)} edges")
    print(f"\nPrim's MST (total weight={prim_total}):")
    for u, v, w in prim_mst:
        print(f"  {u} -- {v} (weight {w})")

    print(f"\nKruskal's MST (total weight={kruskal_total}):")
    for u, v, w in kruskal_mst:
        print(f"  {u} -- {v} (weight {w})")

    # Both should have same total weight
    print(f"\nSame total: {prim_total == kruskal_total}")

    # Verify
    valid, msg = verify_mst(n, edges, kruskal_mst)
    print(f"MST valid: {valid} ({msg})")


def demo_clustering():
    print("\n" + "=" * 60)
    print("DEMO 2: MST-Based Clustering")
    print("=" * 60)

    # 9 points in 3 natural clusters
    # Cluster A: 0, 1, 2 (close together)
    # Cluster B: 3, 4, 5 (close together)
    # Cluster C: 6, 7, 8 (close together)
    edges = [
        # Within cluster A (short edges)
        (0, 1, 1), (1, 2, 2), (0, 2, 2),
        # Within cluster B
        (3, 4, 1), (4, 5, 1), (3, 5, 2),
        # Within cluster C
        (6, 7, 2), (7, 8, 1), (6, 8, 2),
        # Between clusters (long edges)
        (2, 3, 10), (5, 6, 12), (0, 8, 15),
        (1, 4, 11), (2, 7, 13),
    ]

    clusters = mst_clustering(9, edges, k=3)
    print(f"\nMST clustering into 3 groups:")
    for i, cluster in enumerate(sorted(clusters, key=min)):
        print(f"  Cluster {i}: {sorted(cluster)}")
    print(f"\nClusters match natural groupings: "
          f"{{0,1,2}}, {{3,4,5}}, {{6,7,8}}")


def demo_performance():
    print("\n" + "=" * 60)
    print("DEMO 3: Prim's vs Kruskal's Performance")
    print("=" * 60)

    import time
    import random

    random.seed(42)

    for label, n, density in [("Sparse", 2000, 0.005),
                               ("Dense", 500, 0.5)]:
        edges = []
        adj = defaultdict(list)
        for u in range(n):
            for v in range(u + 1, n):
                if random.random() < density:
                    w = random.randint(1, 100)
                    edges.append((u, v, w))
                    adj[u].append((v, w))
                    adj[v].append((u, w))

        start = time.perf_counter()
        _, prim_total = prims(adj, n)
        prim_time = time.perf_counter() - start

        start = time.perf_counter()
        _, kruskal_total = kruskals(n, edges)
        kruskal_time = time.perf_counter() - start

        print(f"\n  {label}: {n} vertices, {len(edges)} edges")
        print(f"    Prim's:    {prim_time:.4f}s (weight={prim_total})")
        print(f"    Kruskal's: {kruskal_time:.4f}s (weight={kruskal_total})")
        winner = "Prim's" if prim_time < kruskal_time else "Kruskal's"
        print(f"    Winner: {winner}")


if __name__ == "__main__":
    demo_basic()
    demo_clustering()
    demo_performance()
