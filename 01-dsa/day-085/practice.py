"""
Day 85 Practice: Minimum Spanning Trees

6 exercises covering Prim's, Kruskal's, and MST applications.
Implement the TODO functions, then run: python practice.py
"""

import heapq
from collections import defaultdict


# Simple Union-Find for exercises
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True


# ===================================================================
# Exercise 1: Kruskal's Algorithm
# ===================================================================
# Sort edges by weight, add if no cycle (using Union-Find).

def kruskal_mst(n, edges):
    """
    n: number of vertices (0 to n-1)
    edges: list of (u, v, weight) — undirected
    Returns: total weight of MST
    """
    # TODO: implement Kruskal's
    pass


def _sol_kruskal_mst(n, edges):
    sorted_edges = sorted(edges, key=lambda e: e[2])
    uf = UnionFind(n)
    total = 0
    count = 0
    for u, v, w in sorted_edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            total += w
            count += 1
            if count == n - 1:
                break
    return total


# ===================================================================
# Exercise 2: Prim's Algorithm
# ===================================================================
# Grow MST from vertex 0 using a min-heap.

def prim_mst(n, edges):
    """
    n: number of vertices (0 to n-1)
    edges: list of (u, v, weight) — undirected
    Returns: total weight of MST
    """
    # TODO: implement Prim's with min-heap
    pass


def _sol_prim_mst(n, edges):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))

    visited = [False] * n
    total = 0
    heap = [(0, 0)]  # (weight, vertex)
    edges_added = 0

    while heap and edges_added < n:
        w, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        total += w
        edges_added += 1
        for v, wt in adj[u]:
            if not visited[v]:
                heapq.heappush(heap, (wt, v))

    return total


# ===================================================================
# Exercise 3: MST Edge Check
# ===================================================================
# Given an MST, determine if a specific edge is in the MST.
# Hint: an edge (u,v,w) is in the MST iff it's the lightest edge
# crossing some cut.

def is_mst_edge(n, all_edges, query_u, query_v, query_w):
    """
    Return True if edge (query_u, query_v, query_w) is in the MST.
    Assume all edge weights are distinct.
    """
    # TODO: build MST and check if edge is included
    pass


def _sol_is_mst_edge(n, all_edges, query_u, query_v, query_w):
    sorted_edges = sorted(all_edges, key=lambda e: e[2])
    uf = UnionFind(n)
    for u, v, w in sorted_edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            if (min(u, v) == min(query_u, query_v) and
                max(u, v) == max(query_u, query_v) and
                w == query_w):
                return True
    return False


# ===================================================================
# Exercise 4: Minimum Cost to Connect All Cities
# ===================================================================
# Some cities are already connected. Find minimum additional cost.

def min_cost_connect(n, existing_connections, new_connections):
    """
    n: number of cities (0 to n-1)
    existing_connections: list of (u, v) already connected (cost 0)
    new_connections: list of (u, v, cost) possible new connections
    Returns: minimum cost to connect all cities
    """
    # TODO: pre-union existing connections, then run Kruskal's
    pass


def _sol_min_cost_connect(n, existing_connections, new_connections):
    uf = UnionFind(n)
    for u, v in existing_connections:
        uf.union(u, v)

    sorted_new = sorted(new_connections, key=lambda e: e[2])
    total = 0
    for u, v, w in sorted_new:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            total += w
    return total


# ===================================================================
# Exercise 5: MST-Based Clustering
# ===================================================================
# Cluster n points into k groups by removing k-1 heaviest MST edges.

def cluster(n, edges, k):
    """
    Return list of sets, where each set is a cluster of vertex indices.
    """
    # TODO: build MST, remove k-1 heaviest edges, find components
    pass


def _sol_cluster(n, edges, k):
    # Build MST
    sorted_edges = sorted(edges, key=lambda e: e[2])
    uf_mst = UnionFind(n)
    mst_edges = []
    for u, v, w in sorted_edges:
        if uf_mst.find(u) != uf_mst.find(v):
            uf_mst.union(u, v)
            mst_edges.append((u, v, w))

    # Sort MST edges by weight, keep all but the k-1 heaviest
    mst_edges.sort(key=lambda e: e[2])
    keep = mst_edges[:len(mst_edges) - (k - 1)]

    # Find components
    uf = UnionFind(n)
    for u, v, _ in keep:
        uf.union(u, v)

    groups = defaultdict(set)
    for v in range(n):
        groups[uf.find(v)].add(v)
    return list(groups.values())


# ===================================================================
# Exercise 6: Second-Best MST
# ===================================================================
# Find the MST with the second-smallest total weight.
# Strategy: for each MST edge, try replacing it with the best non-MST edge.

def second_best_mst_weight(n, edges):
    """
    Return the weight of the second-best spanning tree.
    Assume the graph is connected and has at least n edges.
    """
    # TODO: find MST, then for each MST edge, find best replacement
    pass


def _sol_second_best_mst_weight(n, edges):
    # Build MST via Kruskal's
    sorted_edges = sorted(edges, key=lambda e: e[2])
    uf = UnionFind(n)
    mst_edges = []
    mst_set = set()
    mst_total = 0

    for u, v, w in sorted_edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            mst_edges.append((u, v, w))
            mst_set.add((min(u, v), max(u, v)))
            mst_total += w

    # For each MST edge, try removing it and finding the best replacement
    import math
    best_second = math.inf

    for remove_u, remove_v, remove_w in mst_edges:
        # Build MST without this edge
        uf2 = UnionFind(n)
        new_total = 0
        count = 0
        for u, v, w in sorted_edges:
            if u == remove_u and v == remove_v and w == remove_w:
                continue
            if uf2.find(u) != uf2.find(v):
                uf2.union(u, v)
                new_total += w
                count += 1

        if count == n - 1:  # still connected
            best_second = min(best_second, new_total)

    return best_second


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")

    def try_or_sol(student_fn, sol_fn, *args, **kwargs):
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
        return sol_fn(*args, **kwargs)

    # --- Exercise 1: Kruskal's ---
    print("\nExercise 1: Kruskal's MST")
    edges = [(0, 1, 4), (0, 2, 3), (1, 2, 1), (1, 3, 2), (2, 3, 5)]
    check("basic MST weight",
          try_or_sol(kruskal_mst, _sol_kruskal_mst, 4, edges), 6)  # 1+2+3

    # --- Exercise 2: Prim's ---
    print("\nExercise 2: Prim's MST")
    check("same graph, same weight",
          try_or_sol(prim_mst, _sol_prim_mst, 4, edges), 6)

    larger = [(0,1,10), (0,2,6), (0,3,5), (1,3,15), (2,3,4)]
    check("larger graph",
          try_or_sol(prim_mst, _sol_prim_mst, 4, larger), 19)  # 5+4+10

    # --- Exercise 3: MST Edge Check ---
    print("\nExercise 3: MST Edge Check")
    edges = [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (1, 3, 5)]
    check("edge (0,1,1) in MST",
          try_or_sol(is_mst_edge, _sol_is_mst_edge, 4, edges, 0, 1, 1), True)
    check("edge (1,3,5) not in MST",
          try_or_sol(is_mst_edge, _sol_is_mst_edge, 4, edges, 1, 3, 5), False)

    # --- Exercise 4: Connect with Existing ---
    print("\nExercise 4: Min Cost to Connect Cities")
    check("with existing connections",
          try_or_sol(min_cost_connect, _sol_min_cost_connect,
                     4, [(0, 1)], [(1, 2, 5), (2, 3, 3), (0, 3, 10)]), 8)
    check("all connected already",
          try_or_sol(min_cost_connect, _sol_min_cost_connect,
                     3, [(0, 1), (1, 2)], [(0, 2, 100)]), 0)

    # --- Exercise 5: Clustering ---
    print("\nExercise 5: MST Clustering")
    edges = [(0, 1, 1), (1, 2, 2), (2, 3, 10), (3, 4, 1), (4, 5, 2)]
    clusters = try_or_sol(cluster, _sol_cluster, 6, edges, 2)
    cluster_sets = [frozenset(c) for c in clusters]
    check("2 clusters",
          frozenset({0, 1, 2}) in cluster_sets and frozenset({3, 4, 5}) in cluster_sets,
          True)

    # --- Exercise 6: Second-Best MST ---
    print("\nExercise 6: Second-Best MST")
    edges = [(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (1, 3, 5)]
    # MST: 1+2+4=7. Second best: replace 2 with 3 → 1+3+4=8
    check("second-best MST",
          try_or_sol(second_best_mst_weight, _sol_second_best_mst_weight, 4, edges), 8)

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")


if __name__ == "__main__":
    run_tests()
