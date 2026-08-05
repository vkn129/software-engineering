"""
Day 129 Practice: Greedy on Graphs

6 exercises covering Dijkstra, Kruskal, Prim, and their greedy edge cases.
Implement TODOs, then: python practice.py
"""

import heapq
from collections import defaultdict
from math import inf


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


class UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.r[rx] < self.r[ry]:
            rx, ry = ry, rx
        self.p[ry] = rx
        if self.r[rx] == self.r[ry]:
            self.r[rx] += 1
        return True


# ===================================================================
# Exercise 1: Dijkstra (return distances)
# ===================================================================

def dijkstra_distances(n, edges, source):
    """
    n: number of vertices (0..n-1)
    edges: list of (u, v, w) DIRECTED, non-negative weights
    source: starting vertex
    Returns: list of length n with shortest distances (inf if unreachable)
    """
    # TODO: implement
    pass


def _sol_dijkstra_distances(n, edges, source):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = [inf] * n
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


# ===================================================================
# Exercise 2: Dijkstra with Path Reconstruction
# ===================================================================
# Return the actual shortest path from source to target as a list of vertices.
# If unreachable, return [].

def dijkstra_path(n, edges, source, target):
    """
    n, edges (directed, non-negative), source, target → list of vertices.
    """
    # TODO: implement
    pass


def _sol_dijkstra_path(n, edges, source, target):
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = [inf] * n
    prev = [-1] * n
    dist[source] = 0
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        if u == target:
            break
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if dist[target] == inf:
        return []
    path = []
    cur = target
    while cur != -1:
        path.append(cur)
        cur = prev[cur]
    return list(reversed(path))


# ===================================================================
# Exercise 3: Kruskal MST (total weight)
# ===================================================================

def kruskal_mst_weight(n, edges):
    """
    n: number of vertices.
    edges: list of (u, v, w) undirected.
    Returns: total weight of MST (or spanning forest if disconnected).
    """
    # TODO: implement
    pass


def _sol_kruskal_mst_weight(n, edges):
    uf = UF(n)
    total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if uf.union(u, v):
            total += w
    return total


# ===================================================================
# Exercise 4: Prim MST (total weight)
# ===================================================================
# Must agree with Kruskal on the same input.

def prim_mst_weight(n, edges):
    """
    n: number of vertices.
    edges: list of (u, v, w) undirected. Assume connected.
    Returns: total weight of MST.
    """
    # TODO: implement
    pass


def _sol_prim_mst_weight(n, edges):
    if n == 0:
        return 0
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))
    in_tree = [False] * n
    in_tree[0] = True
    pq = [(w, v) for w, v in adj[0]]
    heapq.heapify(pq)
    total = 0
    added = 1
    while pq and added < n:
        w, v = heapq.heappop(pq)
        if in_tree[v]:
            continue
        in_tree[v] = True
        total += w
        added += 1
        for nw, nb in adj[v]:
            if not in_tree[nb]:
                heapq.heappush(pq, (nw, nb))
    return total


# ===================================================================
# Exercise 5: Detect Negative Edge (Dijkstra precondition check)
# ===================================================================

def has_negative_edge(edges):
    """
    edges: list of (u, v, w)
    Returns: True if any w < 0, else False.
    """
    # TODO: implement
    pass


def _sol_has_negative_edge(edges):
    return any(w < 0 for _, _, w in edges)


# ===================================================================
# Exercise 6: Number of Connected Components (via Kruskal-style union)
# ===================================================================
# Use Union-Find to count components of an undirected graph.

def num_components(n, edges):
    """
    n: number of vertices.
    edges: list of (u, v) undirected.
    Returns: number of connected components.
    """
    # TODO: implement
    pass


def _sol_num_components(n, edges):
    uf = UF(n)
    components = n
    for u, v in edges:
        if uf.union(u, v):
            components -= 1
    return components


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
    print("Exercise 1: Dijkstra Distances")
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]
    check("5-node graph",
          try_or_sol("dijkstra_distances", 5, edges, 0),
          [0, 3, 1, 4, 7])
    check("unreachable",
          try_or_sol("dijkstra_distances", 3, [(0, 1, 5)], 0),
          [0, 5, inf])
    check("self-source",
          try_or_sol("dijkstra_distances", 1, [], 0),
          [0])

    # --- Exercise 2 ---
    print("\nExercise 2: Dijkstra Path")
    check("path 0→4",
          try_or_sol("dijkstra_path", 5, edges, 0, 4),
          [0, 2, 1, 3, 4])
    check("no path",
          try_or_sol("dijkstra_path", 3, [(0, 1, 5)], 0, 2),
          [])
    check("source==target",
          try_or_sol("dijkstra_path", 3, [(0, 1, 5)], 0, 0),
          [0])

    # --- Exercise 3 ---
    print("\nExercise 3: Kruskal MST Weight")
    mst_edges = [(0, 1, 1), (0, 2, 4), (1, 2, 2), (1, 3, 5),
                 (2, 3, 3), (2, 4, 6), (3, 4, 7)]
    check("5-vertex MST", try_or_sol("kruskal_mst_weight", 5, mst_edges), 12)
    check("triangle",
          try_or_sol("kruskal_mst_weight", 3, [(0, 1, 1), (1, 2, 2), (0, 2, 5)]),
          3)
    check("forest of 3 components",
          try_or_sol("kruskal_mst_weight", 5, [(0, 1, 1), (2, 3, 2)]),
          3)

    # --- Exercise 4 ---
    print("\nExercise 4: Prim MST Weight")
    check("matches Kruskal", try_or_sol("prim_mst_weight", 5, mst_edges), 12)
    check("triangle",
          try_or_sol("prim_mst_weight", 3, [(0, 1, 1), (1, 2, 2), (0, 2, 5)]),
          3)

    # --- Exercise 5 ---
    print("\nExercise 5: Has Negative Edge")
    check("yes negative",
          try_or_sol("has_negative_edge", [(0, 1, 5), (1, 2, -3)]), True)
    check("no negative",
          try_or_sol("has_negative_edge", [(0, 1, 5), (1, 2, 3)]), False)
    check("empty", try_or_sol("has_negative_edge", []), False)

    # --- Exercise 6 ---
    print("\nExercise 6: Num Components")
    check("two components",
          try_or_sol("num_components", 5, [(0, 1), (1, 2), (3, 4)]), 2)
    check("all isolated", try_or_sol("num_components", 5, []), 5)
    check("one component",
          try_or_sol("num_components", 3, [(0, 1), (1, 2)]), 1)

    # --- Summary ---
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
