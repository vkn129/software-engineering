"""
Day 88: Articulation Points & Bridges
Tarjan's algorithm — find cut vertices and cut edges in a single DFS pass.

Time: O(V + E)   Space: O(V)
"""
from collections import defaultdict
import sys
sys.setrecursionlimit(10**6)


def find_articulation_points(n, edges):
    """
    Return sorted list of articulation points in undirected graph (n vertices).
    A vertex v is an articulation point if removing it disconnects the graph.

    Rules:
      1. Root case: v is DFS root AND has >= 2 DFS children
      2. Non-root case: v has a child u with low[u] >= disc[v]
    """
    adj = defaultdict(set)
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)

    disc = [-1] * n
    low = [-1] * n
    parent = [-1] * n
    ap = set()
    timer = [0]

    def dfs(u):
        children = 0
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v in adj[u]:
            if disc[v] == -1:
                children += 1
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent[u] == -1 and children > 1:
                    ap.add(u)
                if parent[u] != -1 and low[v] >= disc[u]:
                    ap.add(u)
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i)
    return sorted(ap)


def find_bridges(n, edges):
    """
    Return sorted list of bridges (cut edges) as (u, v) tuples with u < v.

    Rule: edge (u, v) is a bridge iff low[v] > disc[u]  (strict).

    Note: we identify edges by their list index so multi-graphs work correctly —
    you can't filter by parent vertex alone when there are parallel edges.
    """
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))

    disc = [-1] * n
    low = [-1] * n
    bridges = []
    timer = [0]

    def dfs(u, parent_eid):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v, eid in adj[u]:
            if eid == parent_eid:
                continue
            if disc[v] == -1:
                dfs(v, eid)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append(tuple(sorted((u, v))))
            else:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return sorted(bridges)


def biconnected_components(n, edges):
    """
    Return list of biconnected components, each as a sorted list of edges (u, v).
    A biconnected component is a maximal subgraph with no articulation point.

    Uses an edge stack: push edges as we traverse, pop on AP discovery.
    """
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))

    disc = [-1] * n
    low = [-1] * n
    edge_stack = []
    components = []
    timer = [0]

    def dfs(u, parent_eid):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v, eid in adj[u]:
            if eid == parent_eid:
                continue
            if disc[v] == -1:
                edge_stack.append((u, v))
                dfs(v, eid)
                low[u] = min(low[u], low[v])
                if low[v] >= disc[u]:
                    comp = []
                    while edge_stack and edge_stack[-1] != (u, v):
                        comp.append(tuple(sorted(edge_stack.pop())))
                    if edge_stack:
                        comp.append(tuple(sorted(edge_stack.pop())))
                    components.append(sorted(set(comp)))
            elif disc[v] < disc[u]:
                edge_stack.append((u, v))
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return components


def demo():
    print("=" * 65)
    print("Day 88 — Articulation Points & Bridges (Tarjan's, single DFS)")
    print("=" * 65)

    print("\n--- Graph 1: Path 0-1-2-3-4 (a tree) ---")
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
    print(f"  Articulation points: {find_articulation_points(5, edges)}")
    print(f"  Bridges:             {find_bridges(5, edges)}")
    print("  Every internal vertex is AP. Every edge is a bridge.")

    print("\n--- Graph 2: Triangle 0-1-2-0 (cycle) ---")
    edges = [(0, 1), (1, 2), (2, 0)]
    print(f"  Articulation points: {find_articulation_points(3, edges)}")
    print(f"  Bridges:             {find_bridges(3, edges)}")
    print("  Cycle has no AP and no bridges — fully resilient.")

    print("\n--- Graph 3: Dumbbell (two triangles joined by one edge) ---")
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
    print(f"  Articulation points: {find_articulation_points(6, edges)}")
    print(f"  Bridges:             {find_bridges(6, edges)}")
    print("  Vertices 2 and 3 are AP. Edge (2,3) is the only bridge.")

    print("\n--- Graph 4: Real network with redundancy ---")
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (3, 4), (4, 5), (3, 5), (5, 6)]
    print(f"  Articulation points: {find_articulation_points(7, edges)}")
    print(f"  Bridges:             {find_bridges(7, edges)}")

    print("\n--- Graph 5: Biconnected components of dumbbell ---")
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
    for i, comp in enumerate(biconnected_components(6, edges)):
        print(f"  Component {i + 1}: {comp}")

    print("\n" + "=" * 65)
    print("Phase 6 graph mastery: cut analysis = network reliability primitive.")


if __name__ == "__main__":
    demo()
