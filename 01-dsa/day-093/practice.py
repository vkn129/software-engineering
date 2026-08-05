"""
Day 93 Practice: Min Cut & Max-Flow Min-Cut Theorem

6 exercises covering max flow, residual reachability, min-cut recovery,
bottleneck detection, edge connectivity, and project-selection reduction.
"""

from collections import defaultdict, deque


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


def _build_network(n, edges):
    """Return (cap, adj) where cap[u][v] is residual, adj is undirected adj."""
    cap = defaultdict(lambda: defaultdict(int))
    adj = defaultdict(set)
    for u, v, c in edges:
        cap[u][v] += c
        adj[u].add(v)
        adj[v].add(u)
    return cap, adj


def _bfs_augment(cap, adj, s, t, n):
    parent = [-1] * n
    parent[s] = s
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if parent[v] == -1 and cap[u][v] > 0:
                parent[v] = u
                if v == t:
                    return parent
                q.append(v)
    return None


def _max_flow_residual(n, edges, s, t):
    cap, adj = _build_network(n, edges)
    flow = 0
    while True:
        parent = _bfs_augment(cap, adj, s, t, n)
        if parent is None:
            break
        bottleneck = float("inf")
        v = t
        while v != s:
            u = parent[v]
            bottleneck = min(bottleneck, cap[u][v])
            v = u
        v = t
        while v != s:
            u = parent[v]
            cap[u][v] -= bottleneck
            cap[v][u] += bottleneck
            v = u
        flow += bottleneck
    return flow, cap, adj


# ===================================================================
# Exercise 1: Max Flow Value
# ===================================================================

def max_flow_value(n, edges, s, t):
    """edges: list of (u, v, c). Return max flow from s to t."""
    # TODO: implement Edmonds-Karp
    pass


def _sol_max_flow_value(n, edges, s, t):
    flow, _, _ = _max_flow_residual(n, edges, s, t)
    return flow


# ===================================================================
# Exercise 2: Min Cut Value
# ===================================================================

def min_cut_value(n, edges, s, t):
    """Return min s-t cut capacity (== max flow by duality)."""
    # TODO: just call max_flow_value
    pass


def _sol_min_cut_value(n, edges, s, t):
    return _sol_max_flow_value(n, edges, s, t)


# ===================================================================
# Exercise 3: Min Cut Edges
# ===================================================================

def min_cut_edges(n, edges, s, t):
    """
    Return a sorted list of (u, v) original edges crossing the min cut
    (those with u reachable from s in residual, v not).
    """
    # TODO: run max flow, BFS in residual from s, collect crossings.
    pass


def _sol_min_cut_edges(n, edges, s, t):
    flow, cap, adj = _max_flow_residual(n, edges, s, t)

    # Residual reachability from s
    visited = {s}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in visited and cap[u][v] > 0:
                visited.add(v)
                q.append(v)

    # Original-edge crossings
    original = defaultdict(int)
    for u, v, c in edges:
        original[(u, v)] += c

    result = []
    for (u, v), c in original.items():
        if u in visited and v not in visited and c > 0:
            result.append((u, v))
    return sorted(result)


# ===================================================================
# Exercise 4: Bottleneck Detection
# ===================================================================
# Return all edges that, if their capacity increased by 1, would increase
# max flow. (i.e. edges in EVERY min cut.)

def critical_edges(n, edges, s, t):
    """
    Return sorted list of (u, v) edges such that increasing their capacity
    increases max flow. Hint: edges saturated AND on min cut count.
    Simpler: increase each edge's capacity, recompute flow, compare.
    """
    # TODO: brute-force OK here
    pass


def _sol_critical_edges(n, edges, s, t):
    base = _sol_max_flow_value(n, edges, s, t)
    out = []
    for i, (u, v, c) in enumerate(edges):
        new_edges = list(edges)
        new_edges[i] = (u, v, c + 1)
        if _sol_max_flow_value(n, new_edges, s, t) > base:
            out.append((u, v))
    return sorted(set(out))


# ===================================================================
# Exercise 5: Edge Connectivity (undirected)
# ===================================================================
# The edge connectivity of an undirected graph is the min number of edges
# to remove to disconnect it. For a fixed source s, it equals the min
# s-t cut over all t != s.

def edge_connectivity(n, undirected_edges, s):
    """
    undirected_edges: list of (u, v).
    Returns: min over t!=s of min-cut(s, t), each undirected edge having
    capacity 1 in both directions.
    """
    # TODO: build directed edges (u,v,1) and (v,u,1) for each undirected,
    # iterate over all t.
    pass


def _sol_edge_connectivity(n, undirected_edges, s):
    directed = []
    for u, v in undirected_edges:
        directed.append((u, v, 1))
        directed.append((v, u, 1))
    best = float("inf")
    for t in range(n):
        if t == s:
            continue
        f = _sol_max_flow_value(n, directed, s, t)
        best = min(best, f)
    return best


# ===================================================================
# Exercise 6: Project Selection Profit
# ===================================================================
# n projects. project i has profit p_i (can be negative if it's a cost).
# Some projects have prerequisites (if you take i, you must also take j).
# Return: maximum total profit subset.
#
# Reduction:
#   source -> i with cap p_i  (for projects with profit > 0)
#   i -> sink with cap |p_i|  (for projects with profit < 0)
#   for each prereq (i requires j): edge i -> j with capacity INF
#   max_profit = sum(positive profits) - min_cut(source, sink)

def project_selection(profits, prereqs):
    """
    profits: list of int, one per project (positive or negative)
    prereqs: list of (i, j) meaning project i requires project j
    Returns: maximum achievable total profit
    """
    # TODO: build the reduction and solve via min cut
    pass


def _sol_project_selection(profits, prereqs):
    n = len(profits)
    SOURCE = n
    SINK = n + 1
    INF = 10**9
    edges = []
    total_pos = 0
    for i, p in enumerate(profits):
        if p > 0:
            edges.append((SOURCE, i, p))
            total_pos += p
        elif p < 0:
            edges.append((i, SINK, -p))
    for i, j in prereqs:
        edges.append((i, j, INF))

    cut = _sol_max_flow_value(n + 2, edges, SOURCE, SINK)
    return total_pos - cut


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

    # Classic CLRS example: max flow = 23
    clrs_edges = [
        (0, 1, 16), (0, 2, 13),
        (1, 2, 10), (2, 1, 4),
        (1, 3, 12),
        (2, 4, 14),
        (3, 2, 9),
        (4, 3, 7),
        (3, 5, 20), (4, 5, 4),
    ]

    print("Exercise 1: Max Flow Value")
    check("CLRS example", try_or_sol("max_flow_value", 6, clrs_edges, 0, 5), 23)
    check("disconnected", try_or_sol("max_flow_value", 3, [(0, 1, 5)], 0, 2), 0)
    check("single edge", try_or_sol("max_flow_value", 2, [(0, 1, 7)], 0, 1), 7)

    print("\nExercise 2: Min Cut Value")
    check("matches max flow", try_or_sol("min_cut_value", 6, clrs_edges, 0, 5), 23)
    check("bottleneck", try_or_sol("min_cut_value", 4,
          [(0, 1, 100), (1, 2, 5), (2, 3, 100)], 0, 3), 5)

    print("\nExercise 3: Min Cut Edges")
    res = try_or_sol("min_cut_edges", 4,
                     [(0, 1, 100), (1, 2, 5), (2, 3, 100)], 0, 3)
    check("bottleneck edge", res, [(1, 2)])

    print("\nExercise 4: Critical Edges")
    # Single narrow bottleneck: only (1,2) is critical
    # Adding capacity to the wide edges doesn't change flow.
    res = try_or_sol("critical_edges", 4,
                     [(0, 1, 100), (1, 2, 5), (2, 3, 100)], 0, 3)
    check("single bottleneck", res, [(1, 2)])

    print("\nExercise 5: Edge Connectivity")
    # Triangle: connectivity is 2 (need to remove 2 edges to isolate a vertex)
    tri = [(0, 1), (1, 2), (0, 2)]
    check("triangle", try_or_sol("edge_connectivity", 3, tri, 0), 2)
    # Path: connectivity is 1
    path = [(0, 1), (1, 2), (2, 3)]
    check("path", try_or_sol("edge_connectivity", 4, path, 0), 1)

    print("\nExercise 6: Project Selection")
    # 3 projects: A=+10, B=+5, C=-8. A requires C. B no deps.
    # Best: B alone = 5, or A+C = 10-8 = 2, or B+A+C = 7. Best = 7.
    profits = [10, 5, -8]
    prereqs = [(0, 2)]
    check("3-project mix", try_or_sol("project_selection", profits, prereqs), 7)

    # All negative -> take nothing
    profits = [-5, -3]
    prereqs = []
    check("all negative", try_or_sol("project_selection", profits, prereqs), 0)

    # All positive -> take all
    profits = [4, 2, 7]
    prereqs = []
    check("all positive", try_or_sol("project_selection", profits, prereqs), 13)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
