"""
Day 84: Floyd-Warshall Algorithm — From Scratch

All-pairs shortest paths via dynamic programming on intermediate vertices.
Simple triple loop, O(V³), handles negative weights.
"""

import math


# ---------------------------------------------------------------------------
# 1. Standard Floyd-Warshall
# ---------------------------------------------------------------------------

def floyd_warshall(n, edges):
    """
    All-pairs shortest paths.

    Args:
        n: number of vertices (0 to n-1)
        edges: list of (u, v, weight) tuples (directed)

    Returns:
        dist: V×V matrix of shortest distances
        next_hop: V×V matrix for path reconstruction
    """
    INF = math.inf

    # Initialize distance matrix
    dist = [[INF] * n for _ in range(n)]
    next_hop = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0

    for u, v, w in edges:
        dist[u][v] = w
        next_hop[u][v] = v

    # The DP: for each intermediate vertex k
    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue  # small optimization: skip unreachable
            for j in range(n):
                new_dist = dist[i][k] + dist[k][j]
                if new_dist < dist[i][j]:
                    dist[i][j] = new_dist
                    next_hop[i][j] = next_hop[i][k]

    return dist, next_hop


def reconstruct_path(next_hop, u, v):
    """Reconstruct shortest path from u to v using next_hop matrix."""
    if next_hop[u][v] is None:
        return []  # no path
    path = [u]
    while u != v:
        u = next_hop[u][v]
        path.append(u)
    return path


# ---------------------------------------------------------------------------
# 2. Negative Cycle Detection
# ---------------------------------------------------------------------------

def detect_negative_cycles(n, edges):
    """
    Run Floyd-Warshall and identify vertices on negative cycles.

    A vertex i is on a negative cycle if dist[i][i] < 0 after the algorithm.
    A vertex j is AFFECTED by a negative cycle if there exists i on a negative
    cycle such that dist[i][j] < INF (reachable from the cycle).
    """
    dist, _ = floyd_warshall(n, edges)

    # Vertices directly on negative cycles
    on_cycle = [i for i in range(n) if dist[i][i] < 0]

    # Vertices affected (reachable from a cycle vertex)
    affected = set(on_cycle)
    for i in on_cycle:
        for j in range(n):
            if dist[i][j] < math.inf:
                affected.add(j)

    return on_cycle, affected


# ---------------------------------------------------------------------------
# 3. Transitive Closure (Warshall's Algorithm)
# ---------------------------------------------------------------------------

def transitive_closure(n, edges):
    """
    Boolean reachability: can vertex i reach vertex j?

    Same structure as Floyd-Warshall but with OR instead of min/+.
    """
    reach = [[False] * n for _ in range(n)]

    for i in range(n):
        reach[i][i] = True

    for u, v, _ in edges:
        reach[u][v] = True

    for k in range(n):
        for i in range(n):
            if not reach[i][k]:
                continue
            for j in range(n):
                if reach[k][j]:
                    reach[i][j] = True

    return reach


# ---------------------------------------------------------------------------
# 4. Minimax Paths (Bottleneck Shortest Paths)
# ---------------------------------------------------------------------------

def minimax_paths(n, edges):
    """
    Find the path from i to j that minimizes the MAXIMUM edge weight.

    Modification: replace + with max, and min remains min.
    dist[i][j] = min over all paths of (max edge weight on path)
    """
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0

    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                through_k = max(dist[i][k], dist[k][j])
                if through_k < dist[i][j]:
                    dist[i][j] = through_k

    return dist


# ---------------------------------------------------------------------------
# 5. Counting Shortest Paths
# ---------------------------------------------------------------------------

def count_shortest_paths(n, edges):
    """
    Count the number of distinct shortest paths between all pairs.

    Track both distance and count. When a shorter path is found, reset count.
    When an equally short path is found, add to count.
    """
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]
    count = [[0] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
        count[i][i] = 1

    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
            count[u][v] = 1
        elif w == dist[u][v]:
            count[u][v] += 1

    for k in range(n):
        for i in range(n):
            for j in range(n):
                new_dist = dist[i][k] + dist[k][j]
                if new_dist < dist[i][j]:
                    dist[i][j] = new_dist
                    count[i][j] = count[i][k] * count[k][j]
                elif new_dist == dist[i][j] and new_dist < INF:
                    count[i][j] += count[i][k] * count[k][j]

    return dist, count


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def print_matrix(matrix, label, fmt="{:>5}"):
    print(f"\n{label}:")
    n = len(matrix)
    header = "     " + "  ".join(f"{j:>5}" for j in range(n))
    print(header)
    for i in range(n):
        row = f"{i:>3}  "
        for j in range(n):
            val = matrix[i][j]
            if val == math.inf:
                row += "  INF"
            else:
                row += fmt.format(val)
            row += "  "
        print(row)


def demo_basic():
    print("=" * 60)
    print("DEMO 1: All-Pairs Shortest Paths")
    print("=" * 60)

    # 4 vertices, some negative weights, no negative cycles
    edges = [
        (0, 1, 3), (0, 3, 7),
        (1, 0, 8), (1, 2, 2),
        (2, 0, 5), (2, 3, 1),
        (3, 0, 2),
    ]

    dist, next_hop = floyd_warshall(4, edges)
    print_matrix(dist, "Shortest distances")

    # Show some paths
    for u, v in [(0, 2), (3, 1), (1, 3)]:
        path = reconstruct_path(next_hop, u, v)
        print(f"  Path {u}→{v}: {' → '.join(map(str, path))}, distance={dist[u][v]}")


def demo_negative_cycle():
    print("\n" + "=" * 60)
    print("DEMO 2: Negative Cycle Detection")
    print("=" * 60)

    edges = [
        (0, 1, 1),
        (1, 2, -3),
        (2, 0, 1),   # cycle 0→1→2→0, weight = 1+(-3)+1 = -1
        (2, 3, 2),
    ]

    on_cycle, affected = detect_negative_cycles(4, edges)
    print(f"\nEdges: {edges}")
    print(f"Vertices on negative cycle: {on_cycle}")
    print(f"Vertices affected (distance = -∞): {sorted(affected)}")


def demo_transitive_closure():
    print("\n" + "=" * 60)
    print("DEMO 3: Transitive Closure (Reachability)")
    print("=" * 60)

    # Can vertex i reach vertex j?
    edges = [(0, 1, 1), (1, 2, 1), (3, 0, 1)]  # 3→0→1→2, but 2 can't reach anyone

    reach = transitive_closure(4, edges)
    print(f"\nEdges: {edges}")
    print_matrix([["Y" if reach[i][j] else "." for j in range(4)] for i in range(4)],
                 "Reachability (Y = reachable)", fmt="{:>5}")

    print("\n  3 can reach 2: " + str(reach[3][2]) + " (3→0→1→2)")
    print("  2 can reach 0: " + str(reach[2][0]) + " (no outgoing edges from 2)")


def demo_vs_dijkstra():
    print("\n" + "=" * 60)
    print("DEMO 4: Floyd-Warshall vs V×Dijkstra (Performance)")
    print("=" * 60)

    import time
    import heapq
    import random

    random.seed(42)
    n = 200

    # Build dense random graph
    edges = []
    for u in range(n):
        for v in range(n):
            if u != v and random.random() < 0.3:
                edges.append((u, v, random.randint(1, 100)))

    # Floyd-Warshall
    start = time.perf_counter()
    fw_dist, _ = floyd_warshall(n, edges)
    fw_time = time.perf_counter() - start

    # V × Dijkstra
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))

    start = time.perf_counter()
    dijk_dist = [[math.inf] * n for _ in range(n)]
    for src in range(n):
        d = [math.inf] * n
        d[src] = 0
        heap = [(0, src)]
        while heap:
            du, u = heapq.heappop(heap)
            if du > d[u]:
                continue
            for v, w in adj[u]:
                if d[u] + w < d[v]:
                    d[v] = d[u] + w
                    heapq.heappush(heap, (d[v], v))
        dijk_dist[src] = d
    dijk_time = time.perf_counter() - start

    # Verify same results
    match = all(fw_dist[i][j] == dijk_dist[i][j] for i in range(n) for j in range(n))

    print(f"\nDense graph: {n} vertices, {len(edges)} edges (~30% density)")
    print(f"Floyd-Warshall: {fw_time:.3f}s")
    print(f"V × Dijkstra:   {dijk_time:.3f}s")
    print(f"Results match:  {match}")
    print(f"\nFloyd-Warshall's triple loop is cache-friendly and has minimal overhead.")
    print(f"For dense graphs, it often beats V × Dijkstra despite same O(V³) complexity.")


def demo_path_counting():
    print("\n" + "=" * 60)
    print("DEMO 5: Counting Shortest Paths")
    print("=" * 60)

    #    0 --2--> 1
    #    |        |
    #    3        1
    #    |        |
    #    v        v
    #    2 --2--> 3
    # Two shortest paths from 0→3: 0→1→3 (cost 3) and 0→2→3 (cost 5)
    # But if we adjust: 0→1 cost 3, 0→2 cost 2, 1→3 cost 2, 2→3 cost 3
    # Then 0→1→3 = 5, 0→2→3 = 5, TWO paths!
    edges = [
        (0, 1, 3), (0, 2, 2),
        (1, 3, 2), (2, 3, 3),
    ]

    dist, count = count_shortest_paths(4, edges)
    print(f"\nEdges: {edges}")
    print_matrix(dist, "Shortest distances")
    print_matrix(count, "Number of shortest paths")
    print(f"\n  0→3: distance={dist[0][3]}, number of shortest paths={count[0][3]}")


if __name__ == "__main__":
    demo_basic()
    demo_negative_cycle()
    demo_transitive_closure()
    demo_vs_dijkstra()
    demo_path_counting()
