"""
Day 95 Practice: Cycle Detection — Directed & Undirected

6 exercises: undirected DFS, undirected Union-Find, directed 3-coloring,
cycle reporting, topo-sort failure as cycle detector, and deadlock detection.
"""

from collections import defaultdict, deque

WHITE, GRAY, BLACK = 0, 1, 2


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


# ===================================================================
# Exercise 1: Undirected Cycle (DFS)
# ===================================================================

def cycle_undirected_dfs(n, edges):
    """Return True iff undirected graph has any cycle. Self-loops count."""
    # TODO: DFS with parent (edge-id) tracking
    pass


def _sol_cycle_undirected_dfs(n, edges):
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        if u == v:
            return True
        adj[u].append((v, i))
        adj[v].append((u, i))
    visited = [False] * n

    def dfs(u, parent_eid):
        visited[u] = True
        for v, eid in adj[u]:
            if eid == parent_eid:
                continue
            if visited[v]:
                return True
            if dfs(v, eid):
                return True
        return False

    for s in range(n):
        if not visited[s] and dfs(s, -1):
            return True
    return False


# ===================================================================
# Exercise 2: Undirected Cycle (Union-Find)
# ===================================================================

def cycle_undirected_uf(n, edges):
    """Same problem, but solved with Union-Find."""
    # TODO: when union(u, v) returns False (already same root), cycle found
    pass


def _sol_cycle_undirected_uf(n, edges):
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for u, v in edges:
        if u == v:
            return True
        ru, rv = find(u), find(v)
        if ru == rv:
            return True
        if rank[ru] < rank[rv]:
            ru, rv = rv, ru
        parent[rv] = ru
        if rank[ru] == rank[rv]:
            rank[ru] += 1
    return False


# ===================================================================
# Exercise 3: Directed Cycle (3-Coloring DFS)
# ===================================================================

def cycle_directed(n, edges):
    """Return True iff directed graph has any cycle. Self-loops count."""
    # TODO: use WHITE/GRAY/BLACK coloring during DFS
    pass


def _sol_cycle_directed(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        if u == v:
            return True
        adj[u].append(v)
    color = [WHITE] * n

    def dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    for s in range(n):
        if color[s] == WHITE and dfs(s):
            return True
    return False


# ===================================================================
# Exercise 4: Report Cycle Vertices (Directed)
# ===================================================================

def report_cycle_directed(n, edges):
    """
    If a directed cycle exists, return the list of vertices on it
    (e.g. [2, 5, 7, 2]). Else return None.
    """
    # TODO: 3-color DFS, track parent map, reconstruct when GRAY hit
    pass


def _sol_report_cycle_directed(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    color = [WHITE] * n
    parent = [-1] * n
    cyc = []

    def dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                cur = u
                cyc.append(v)
                while cur != v:
                    cyc.append(cur)
                    cur = parent[cur]
                cyc.append(v)
                cyc.reverse()
                return True
            if color[v] == WHITE:
                parent[v] = u
                if dfs(v):
                    return True
        color[u] = BLACK
        return False

    for s in range(n):
        if color[s] == WHITE and dfs(s):
            return cyc
    return None


# ===================================================================
# Exercise 5: Topo Sort as Cycle Detector (Kahn's Algorithm)
# ===================================================================
# Run Kahn's algorithm. If output size < n, a cycle exists.

def cycle_via_topo(n, edges):
    """Return True iff Kahn's algorithm cannot produce a full topo order."""
    # TODO: implement Kahn's, compare output length to n
    pass


def _sol_cycle_via_topo(n, edges):
    adj = defaultdict(list)
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    q = deque(v for v in range(n) if indeg[v] == 0)
    count = 0
    while q:
        u = q.popleft()
        count += 1
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return count < n


# ===================================================================
# Exercise 6: Deadlock Detection
# ===================================================================
# Given transactions and a wait-for relationship, return True iff there's
# a deadlock (cycle in the wait-for graph).

def has_deadlock(n_tx, wait_for_edges):
    """
    wait_for_edges: list of (Ti, Tj) meaning Ti is blocked waiting on Tj.
    Returns True iff a deadlock cycle exists.
    """
    # TODO: directly call directed cycle detection
    pass


def _sol_has_deadlock(n_tx, wait_for_edges):
    return _sol_cycle_directed(n_tx, wait_for_edges)


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

    print("Exercise 1: Undirected Cycle (DFS)")
    check("tree", try_or_sol("cycle_undirected_dfs", 4,
          [(0, 1), (1, 2), (1, 3)]), False)
    check("triangle", try_or_sol("cycle_undirected_dfs", 3,
          [(0, 1), (1, 2), (2, 0)]), True)
    check("self-loop", try_or_sol("cycle_undirected_dfs", 2, [(0, 0)]), True)
    check("disconnected + cycle", try_or_sol("cycle_undirected_dfs", 5,
          [(0, 1), (2, 3), (3, 4), (4, 2)]), True)

    print("\nExercise 2: Undirected Cycle (Union-Find)")
    check("tree", try_or_sol("cycle_undirected_uf", 4,
          [(0, 1), (1, 2), (1, 3)]), False)
    check("triangle", try_or_sol("cycle_undirected_uf", 3,
          [(0, 1), (1, 2), (2, 0)]), True)
    check("disconnected + cycle", try_or_sol("cycle_undirected_uf", 5,
          [(0, 1), (2, 3), (3, 4), (4, 2)]), True)

    print("\nExercise 3: Directed Cycle (3-Coloring)")
    check("DAG", try_or_sol("cycle_directed", 3, [(0, 1), (1, 2), (0, 2)]), False)
    check("directed triangle", try_or_sol("cycle_directed", 3,
          [(0, 1), (1, 2), (2, 0)]), True)
    check("Y-shape no cycle", try_or_sol("cycle_directed", 3,
          [(0, 2), (1, 2)]), False)
    check("self-loop", try_or_sol("cycle_directed", 1, [(0, 0)]), True)

    print("\nExercise 4: Report Cycle (Directed)")
    res = try_or_sol("report_cycle_directed", 3, [(0, 1), (1, 2), (2, 0)])
    check("triangle has 3 cycle verts",
          res is not None and len(res) == 4 and res[0] == res[-1], True)
    res = try_or_sol("report_cycle_directed", 3, [(0, 1), (1, 2)])
    check("DAG returns None", res, None)

    print("\nExercise 5: Topo-Sort Cycle Detection")
    check("DAG", try_or_sol("cycle_via_topo", 3, [(0, 1), (1, 2), (0, 2)]), False)
    check("cycle", try_or_sol("cycle_via_topo", 3,
          [(0, 1), (1, 2), (2, 0)]), True)

    print("\nExercise 6: Deadlock Detection")
    # T1 -> T2 -> T3 -> T1 cycle
    check("3-way deadlock", try_or_sol("has_deadlock", 3,
          [(0, 1), (1, 2), (2, 0)]), True)
    check("no deadlock", try_or_sol("has_deadlock", 3,
          [(0, 1), (1, 2)]), False)
    check("self-wait", try_or_sol("has_deadlock", 1, [(0, 0)]), True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
