"""
Day 78 Practice: Graph Representations

6 exercises to build intuition for graph storage trade-offs.
Implement the TODO functions, then run: python practice.py
"""

from collections import defaultdict, deque


# ===================================================================
# Exercise 1: Build Adjacency List from Edge List
# ===================================================================
# Given a list of edges [(u, v), ...], build an adjacency list (dict of lists).
# For undirected graphs, each edge appears in both directions.

def build_adj_list(edges, directed=False):
    """Build adjacency list from edge tuples. Returns dict[vertex] -> [neighbors]."""
    # TODO: implement this
    pass


def _sol_build_adj_list(edges, directed=False):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    return dict(adj)


# ===================================================================
# Exercise 2: Transpose a Directed Graph
# ===================================================================
# Reverse every edge direction: if u->v exists, create v->u instead.
# The transpose is used in Kosaraju's SCC algorithm and web link analysis.

def transpose_graph(adj):
    """Given adj list {u: [v1, v2, ...]}, return transposed graph."""
    # TODO: implement this
    pass


def _sol_transpose_graph(adj):
    # Every vertex must appear even if it has no outgoing edges in transpose
    transposed = {v: [] for v in adj}
    for u in adj:
        for v in adj[u]:
            transposed[v].append(u)
    return transposed


# ===================================================================
# Exercise 3: Compute Degree Sequence
# ===================================================================
# For a directed graph, compute in-degree and out-degree of every vertex.
# Degree sequence reveals graph structure: a tree has exactly one vertex
# with in-degree 0, a DAG may have several.

def degree_sequence(adj):
    """Returns dict[vertex] -> (in_degree, out_degree) for directed graph."""
    # TODO: implement this
    pass


def _sol_degree_sequence(adj):
    degrees = {v: [0, 0] for v in adj}  # [in_degree, out_degree]
    for u in adj:
        degrees[u][1] = len(adj[u])  # out-degree = number of outgoing edges
        for v in adj[u]:
            degrees[v][0] += 1       # increment in-degree of target
    return {v: tuple(d) for v, d in degrees.items()}


# ===================================================================
# Exercise 4: Bipartite Check via BFS
# ===================================================================
# A graph is bipartite if you can 2-color it: every edge connects different
# colors. Social networks, scheduling, matching problems use this property.
# Use BFS to attempt 2-coloring; if any neighbor has the same color, not bipartite.

def is_bipartite(adj):
    """Check if undirected graph (adj list) is bipartite. Returns bool."""
    # TODO: implement using BFS 2-coloring
    pass


def _sol_is_bipartite(adj):
    color = {}
    for start in adj:
        if start in color:
            continue
        # BFS from each unvisited vertex (handles disconnected graphs)
        queue = deque([start])
        color[start] = 0
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in color:
                    color[v] = 1 - color[u]  # alternate color
                    queue.append(v)
                elif color[v] == color[u]:
                    return False  # same color on both ends = not bipartite
    return True


# ===================================================================
# Exercise 5: Recommend Representation by Density
# ===================================================================
# Given V and E, recommend the best representation.
# Key insight: the crossover point is roughly E = V^2 / log(V).
# Below that -> adjacency list. Above -> adjacency matrix.
# Edge list is best when you only need to iterate all edges (Kruskal's).

def recommend_representation(num_vertices, num_edges, algorithm="general"):
    """
    Returns one of: "adjacency_list", "adjacency_matrix", "edge_list"

    algorithm can be: "general", "kruskals", "floyd_warshall", "bfs_dfs"
    """
    # TODO: implement recommendation logic
    pass


def _sol_recommend_representation(num_vertices, num_edges, algorithm="general"):
    # Some algorithms dictate the representation regardless of density
    if algorithm == "kruskals":
        return "edge_list"       # Kruskal's needs sorted edges
    if algorithm == "floyd_warshall":
        return "adjacency_matrix"  # Floyd-Warshall reads matrix[i][j] for all pairs
    if algorithm == "bfs_dfs":
        return "adjacency_list"  # BFS/DFS iterate neighbors

    # For general use, decide by density
    max_edges = num_vertices * (num_vertices - 1) / 2  # undirected
    density = num_edges / max_edges if max_edges > 0 else 0

    if density > 0.5:
        return "adjacency_matrix"  # dense -> O(1) edge check worth the O(V^2) space
    return "adjacency_list"        # sparse -> save memory, fast neighbor iteration


# ===================================================================
# Exercise 6: Graph Equality
# ===================================================================
# Two graphs are equal if they have the same vertices and edges,
# regardless of storage order. Compare an adjacency list to an edge list.

def graphs_equal(adj_list, edge_list, directed=False):
    """
    adj_list: dict[vertex] -> [neighbors]
    edge_list: [(u, v), ...]
    Returns True if they represent the same graph.
    """
    # TODO: implement this
    pass


def _sol_graphs_equal(adj_list, edge_list, directed=False):
    # Convert both to canonical edge sets for comparison
    # Adjacency list -> edge set
    adj_edges = set()
    for u in adj_list:
        for v in adj_list[u]:
            if directed:
                adj_edges.add((u, v))
            else:
                adj_edges.add((min(u, v), max(u, v)))

    # Edge list -> edge set
    el_edges = set()
    for u, v in edge_list:
        if directed:
            el_edges.add((u, v))
        else:
            el_edges.add((min(u, v), max(u, v)))

    return adj_edges == el_edges


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

    # Helper: use student impl if it returns non-None, else fall back to solution
    def try_or_sol(student_fn, sol_fn, *args, **kwargs):
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
        return sol_fn(*args, **kwargs)

    # --- Exercise 1: Build Adjacency List ---
    print("\nExercise 1: Build Adjacency List")
    result = try_or_sol(build_adj_list, _sol_build_adj_list,
                        [(0, 1), (1, 2), (0, 2)], directed=False)
    check("undirected 3 edges", set(result[0]), {1, 2})
    check("undirected symmetry", set(result[1]), {0, 2})

    result_d = try_or_sol(build_adj_list, _sol_build_adj_list,
                          [(0, 1), (1, 2)], directed=True)
    check("directed: 0->1 exists", 1 in result_d.get(0, []), True)
    check("directed: 1->0 absent", 0 in result_d.get(1, []), False)

    # --- Exercise 2: Transpose Graph ---
    print("\nExercise 2: Transpose Graph")
    adj = {0: [1, 2], 1: [2], 2: []}
    t = try_or_sol(transpose_graph, _sol_transpose_graph, adj)
    check("transpose: 0 has no incoming", t[0], [])
    check("transpose: 2 receives from 0,1", sorted(t[2]), [0, 1])
    check("transpose: 1 receives from 0", t[1], [0])

    # --- Exercise 3: Degree Sequence ---
    print("\nExercise 3: Degree Sequence")
    adj = {0: [1, 2], 1: [2], 2: [0]}
    deg = try_or_sol(degree_sequence, _sol_degree_sequence, adj)
    check("vertex 0: in=1, out=2", deg[0], (1, 2))
    check("vertex 1: in=1, out=1", deg[1], (1, 1))
    check("vertex 2: in=2, out=1", deg[2], (2, 1))

    # --- Exercise 4: Bipartite Check ---
    print("\nExercise 4: Bipartite Check")
    check("4-cycle is bipartite",
          try_or_sol(is_bipartite, _sol_is_bipartite,
                     {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [2, 0]}), True)
    check("triangle is not bipartite",
          try_or_sol(is_bipartite, _sol_is_bipartite,
                     {0: [1, 2], 1: [0, 2], 2: [0, 1]}), False)
    check("disconnected bipartite",
          try_or_sol(is_bipartite, _sol_is_bipartite,
                     {0: [1], 1: [0], 2: [3], 3: [2]}), True)

    # --- Exercise 5: Recommend Representation ---
    print("\nExercise 5: Recommend Representation")
    check("sparse general -> adj list",
          try_or_sol(recommend_representation, _sol_recommend_representation,
                     1000, 2000, "general"), "adjacency_list")
    check("kruskal's -> edge list",
          try_or_sol(recommend_representation, _sol_recommend_representation,
                     100, 5000, "kruskals"), "edge_list")
    check("floyd-warshall -> matrix",
          try_or_sol(recommend_representation, _sol_recommend_representation,
                     100, 200, "floyd_warshall"), "adjacency_matrix")
    check("dense general -> adj matrix",
          try_or_sol(recommend_representation, _sol_recommend_representation,
                     100, 4000, "general"), "adjacency_matrix")

    # --- Exercise 6: Graph Equality ---
    print("\nExercise 6: Graph Equality")
    adj = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
    edges = [(0, 1), (1, 2), (0, 2)]
    check("same triangle graph",
          try_or_sol(graphs_equal, _sol_graphs_equal, adj, edges), True)
    check("different graphs",
          try_or_sol(graphs_equal, _sol_graphs_equal, adj, [(0, 1), (1, 2)]), False)
    check("directed equality",
          try_or_sol(graphs_equal, _sol_graphs_equal,
                     {0: [1], 1: [2], 2: []}, [(0, 1), (1, 2)], directed=True), True)

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")


if __name__ == "__main__":
    run_tests()
