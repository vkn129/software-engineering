"""
Day 129: Greedy on Graphs — Dijkstra, Kruskal, Prim

All three are textbook greedy:
  - Dijkstra: settle the nearest unsettled vertex (cut = settled vs unsettled).
  - Kruskal:  take the cheapest edge that doesn't form a cycle.
  - Prim:     grow the tree by the cheapest cut-crossing edge.

References day 82 (shortest paths) and day 85 (MST).
"""

import heapq
from collections import defaultdict
from math import inf


# ---------------------------------------------------------------------------
# Dijkstra (greedy on settled cut)
# ---------------------------------------------------------------------------

def dijkstra(n, edges, source):
    """
    Single-source shortest paths from `source` to all other vertices.
    edges: list of (u, v, w) directed; for undirected, pass both directions.
    Returns: dist[] list of length n (inf if unreachable).

    The greedy choice: at each step, pop the unsettled vertex with the
    smallest tentative distance. Correct because non-negative weights mean
    no later relaxation can improve a settled distance.

    Time: O((V + E) log V)   Space: O(V + E)
    """
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))

    dist = [inf] * n
    dist[source] = 0
    pq = [(0, source)]  # (distance, vertex)

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue  # stale entry — greedy commitment already made
        for v, w in adj[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    return dist


# ---------------------------------------------------------------------------
# Union-Find for Kruskal
# ---------------------------------------------------------------------------

class _UnionFind:
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


# ---------------------------------------------------------------------------
# Kruskal (greedy: cheapest non-cycle-forming edge)
# ---------------------------------------------------------------------------

def kruskal(n, edges):
    """
    edges: list of (u, v, w) undirected. Returns (mst_edges, total_weight).
    If graph is disconnected, returns a minimum spanning forest.

    Time: O(E log E)
    """
    sorted_edges = sorted(edges, key=lambda e: e[2])
    uf = _UnionFind(n)
    mst = []
    total = 0
    for u, v, w in sorted_edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            total += w
    return mst, total


# ---------------------------------------------------------------------------
# Prim (greedy: cheapest edge leaving current tree)
# ---------------------------------------------------------------------------

def prim(n, edges, start=0):
    """
    edges: list of (u, v, w) undirected. Returns (mst_edges, total_weight).
    Skips stale entries by tracking which vertices are in the tree.

    Time: O(E log V)
    """
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((w, v))
        adj[v].append((w, u))

    in_tree = [False] * n
    in_tree[start] = True
    mst = []
    total = 0

    pq = []
    for w, v in adj[start]:
        heapq.heappush(pq, (w, start, v))

    while pq and len(mst) < n - 1:
        w, u, v = heapq.heappop(pq)
        if in_tree[v]:
            continue  # stale (v was added via a cheaper edge)
        in_tree[v] = True
        mst.append((u, v, w))
        total += w
        for nw, nb in adj[v]:
            if not in_tree[nb]:
                heapq.heappush(pq, (nw, v, nb))

    return mst, total


# ---------------------------------------------------------------------------
# Demo: trace the greedy choice
# ---------------------------------------------------------------------------

def demo():
    print("=" * 65)
    print("Day 129 — Greedy on Graphs: Dijkstra, Kruskal, Prim")
    print("=" * 65)

    # Dijkstra
    print("\n--- Dijkstra ---")
    n = 5
    # Directed weighted graph
    edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1),
             (2, 3, 5), (3, 4, 3)]
    print(f"  Vertices: 0..{n-1}, edges: {edges}")
    dist = dijkstra(n, edges, 0)
    print(f"  dist from 0: {dist}")
    print("  Greedy trace: settle 0(0) → 2(1) → 1(3) → 3(4) → 4(7)")

    # Why negative edges break Dijkstra (textbook decrease-key version).
    print("\n--- Why Dijkstra fails on negative edges (textbook variant) ---")
    print("  Our impl uses lazy re-push, so it can repair some negatives —")
    print("  but the textbook (settle-once-never-revisit) Dijkstra would here:")
    print("  Example: 0→1 (5), 0→2 (2), 2→1 (-10)")
    print("    Settle 0(0), then 2(2). Settle 1 at d=5 (via 0→1 direct).")
    print("    Now 2→1 = 2 + (-10) = -8 would improve 1, but 1 is settled.")
    print("    Settle-once Dijkstra: dist[1] = 5 (WRONG, true = -8).")
    print("  Moral: greedy 'commit and never revisit' breaks under negatives.")

    # MST: Kruskal and Prim should agree
    print("\n--- MST: Kruskal vs Prim ---")
    n = 5
    mst_edges = [(0, 1, 1), (0, 2, 4), (1, 2, 2), (1, 3, 5),
                 (2, 3, 3), (2, 4, 6), (3, 4, 7)]
    print(f"  Vertices: 0..{n-1}, edges: {mst_edges}")

    k_mst, k_total = kruskal(n, mst_edges)
    p_mst, p_total = prim(n, mst_edges)
    print(f"  Kruskal MST: {sorted((tuple(sorted([u, v])), w) for u, v, w in k_mst)}")
    print(f"  Kruskal total: {k_total}")
    print(f"  Prim MST:    {sorted((tuple(sorted([u, v])), w) for u, v, w in p_mst)}")
    print(f"  Prim total:  {p_total}")
    print(f"  Same weight? {k_total == p_total}")

    # Disconnected → forest
    print("\n--- Disconnected → spanning forest ---")
    forest_edges = [(0, 1, 1), (2, 3, 2)]
    f_mst, f_total = kruskal(4, forest_edges)
    print(f"  Edges: {forest_edges}")
    print(f"  Kruskal forest: {f_mst}, weight {f_total}")

    print("\n" + "=" * 65)
    print("Three algorithms, one greedy template: cut + lightest crossing edge.")


if __name__ == "__main__":
    demo()
