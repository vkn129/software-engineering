"""
Day 84 Practice: Floyd-Warshall Algorithm

6 exercises covering all-pairs shortest paths, transitive closure, and variants.
Implement the TODO functions, then run: python practice.py
"""

import math


# ===================================================================
# Exercise 1: Basic Floyd-Warshall
# ===================================================================
# Implement all-pairs shortest paths with the classic triple loop.

def all_pairs_shortest(n, edges):
    """
    n: number of vertices (0 to n-1)
    edges: list of (u, v, weight) — directed
    Returns: V×V distance matrix (math.inf for unreachable)
    """
    # TODO: implement Floyd-Warshall
    pass


def _sol_all_pairs_shortest(n, edges):
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)

    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


# ===================================================================
# Exercise 2: Path Reconstruction
# ===================================================================
# Track next-hop matrix to reconstruct actual shortest paths.

def shortest_path_between(n, edges, src, dst):
    """
    Return (distance, path) where path is list of vertices from src to dst.
    Return (math.inf, []) if no path exists.
    """
    # TODO: implement Floyd-Warshall with next-hop tracking
    pass


def _sol_shortest_path_between(n, edges, src, dst):
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        if w < dist[u][v]:
            dist[u][v] = w
            nxt[u][v] = v

    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]

    if nxt[src][dst] is None:
        return INF, []

    path = [src]
    while src != dst:
        src = nxt[src][dst]
        path.append(src)
    return dist[path[0]][dst], path


# ===================================================================
# Exercise 3: Negative Cycle Detection
# ===================================================================
# After Floyd-Warshall, check if dist[i][i] < 0 for any vertex.

def has_negative_cycle(n, edges):
    """Return True if graph contains a negative-weight cycle."""
    # TODO: implement using Floyd-Warshall diagonal check
    pass


def _sol_has_negative_cycle(n, edges):
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)

    for k in range(n):
        for i in range(n):
            if dist[i][k] == INF:
                continue
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    return any(dist[i][i] < 0 for i in range(n))


# ===================================================================
# Exercise 4: Transitive Closure
# ===================================================================
# Boolean reachability: can i reach j? Use OR instead of min/+.

def reachability(n, edges):
    """
    Return V×V boolean matrix: reach[i][j] = True if i can reach j.
    """
    # TODO: implement Warshall's algorithm
    pass


def _sol_reachability(n, edges):
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


# ===================================================================
# Exercise 5: Diameter of Graph
# ===================================================================
# The diameter is the longest shortest path between any two vertices.
# Only consider vertices that can actually reach each other.

def graph_diameter(n, edges):
    """
    Return the diameter (longest shortest path) of the graph.
    Return -1 if the graph is disconnected.
    """
    # TODO: use Floyd-Warshall then find the max finite distance
    pass


def _sol_graph_diameter(n, edges):
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
        dist[v][u] = min(dist[v][u], w)  # undirected for diameter

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    max_dist = 0
    for i in range(n):
        for j in range(i + 1, n):
            if dist[i][j] == INF:
                return -1  # disconnected
            max_dist = max(max_dist, dist[i][j])
    return max_dist


# ===================================================================
# Exercise 6: Minimax Path
# ===================================================================
# Find path from i to j minimizing the MAXIMUM edge weight on the path.
# Replace + with max in Floyd-Warshall.

def minimax_distance(n, edges, src, dst):
    """
    Return the minimax distance from src to dst.
    The minimax distance is the minimum over all paths of the maximum edge weight.
    Return math.inf if no path exists.
    """
    # TODO: modify Floyd-Warshall: use max instead of +, min remains
    pass


def _sol_minimax_distance(n, edges, src, dst):
    INF = math.inf
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
        dist[v][u] = min(dist[v][u], w)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                through_k = max(dist[i][k], dist[k][j])
                if through_k < dist[i][j]:
                    dist[i][j] = through_k
    return dist[src][dst]


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

    # --- Exercise 1 ---
    print("\nExercise 1: Basic Floyd-Warshall")
    edges = [(0, 1, 3), (1, 2, 1), (0, 2, 10)]
    dist = try_or_sol(all_pairs_shortest, _sol_all_pairs_shortest, 3, edges)
    check("0→2 via 1", dist[0][2], 4)
    check("0→1 direct", dist[0][1], 3)
    check("2→0 unreachable", dist[2][0], math.inf)

    # --- Exercise 2 ---
    print("\nExercise 2: Path Reconstruction")
    edges = [(0, 1, 2), (1, 2, 3), (0, 2, 10), (2, 3, 1)]
    d, path = try_or_sol(shortest_path_between, _sol_shortest_path_between,
                         4, edges, 0, 3)
    check("distance 0→3", d, 6)
    check("path 0→3", path, [0, 1, 2, 3])
    d2, path2 = try_or_sol(shortest_path_between, _sol_shortest_path_between,
                           4, edges, 3, 0)
    check("unreachable", d2, math.inf)

    # --- Exercise 3 ---
    print("\nExercise 3: Negative Cycle Detection")
    check("no neg cycle",
          try_or_sol(has_negative_cycle, _sol_has_negative_cycle,
                     3, [(0, 1, -1), (1, 2, -2)]), False)
    check("has neg cycle",
          try_or_sol(has_negative_cycle, _sol_has_negative_cycle,
                     3, [(0, 1, 1), (1, 2, -3), (2, 0, 1)]), True)

    # --- Exercise 4 ---
    print("\nExercise 4: Transitive Closure")
    reach = try_or_sol(reachability, _sol_reachability,
                       4, [(0, 1, 1), (1, 2, 1), (3, 0, 1)])
    check("3 can reach 2", reach[3][2], True)
    check("2 cannot reach 0", reach[2][0], False)
    check("self-reachable", reach[0][0], True)

    # --- Exercise 5 ---
    print("\nExercise 5: Graph Diameter")
    # Path graph: 0-1-2-3, diameter = 3
    check("path graph diameter",
          try_or_sol(graph_diameter, _sol_graph_diameter,
                     4, [(0, 1, 1), (1, 2, 1), (2, 3, 1)]), 3)
    # Disconnected
    check("disconnected = -1",
          try_or_sol(graph_diameter, _sol_graph_diameter,
                     4, [(0, 1, 1)]), -1)

    # --- Exercise 6 ---
    print("\nExercise 6: Minimax Path")
    # 0--(5)--1--(3)--2  vs  0--(10)--2
    # Minimax 0→2: path 0-1-2 has max edge 5, direct has max edge 10
    edges = [(0, 1, 5), (1, 2, 3), (0, 2, 10)]
    check("minimax via intermediate",
          try_or_sol(minimax_distance, _sol_minimax_distance, 3, edges, 0, 2), 5)

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")


if __name__ == "__main__":
    run_tests()
