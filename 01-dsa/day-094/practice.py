"""
Day 94 Practice: Hierholzer's Algorithm — Euler Paths & Circuits

6 exercises: existence checks, Hierholzer's algorithm (directed & undirected),
de Bruijn reconstruction, and Chinese-postman counting.
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


# ===================================================================
# Exercise 1: Has Euler Circuit (Undirected)
# ===================================================================

def has_euler_circuit_undirected(n, edges):
    """
    Return True iff the undirected (multi)graph has an Euler circuit:
    - All edges form a single connected component (ignoring isolated vertices).
    - All vertices have even degree.
    """
    # TODO: implement
    pass


def _sol_has_euler_circuit_undirected(n, edges):
    deg = [0] * n
    adj = defaultdict(list)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        adj[u].append(v)
        adj[v].append(u)
        if u == v:
            deg[u] += 1
    if any(d % 2 == 1 for d in deg):
        return False
    has_edge = [v for v in range(n) if deg[v] > 0]
    if not has_edge:
        return True
    start = has_edge[0]
    visited = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in visited:
                visited.add(w)
                q.append(w)
    return all(v in visited for v in has_edge)


# ===================================================================
# Exercise 2: Has Euler Path (Undirected)
# ===================================================================

def has_euler_path_undirected(n, edges):
    """
    Return True iff exactly 0 or 2 vertices have odd degree AND
    the edge-bearing vertices are connected.
    """
    # TODO: implement
    pass


def _sol_has_euler_path_undirected(n, edges):
    deg = [0] * n
    adj = defaultdict(list)
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        adj[u].append(v)
        adj[v].append(u)
        if u == v:
            deg[u] += 1
    odd_count = sum(1 for d in deg if d % 2 == 1)
    if odd_count not in (0, 2):
        return False
    has_edge = [v for v in range(n) if deg[v] > 0]
    if not has_edge:
        return True
    start = has_edge[0]
    visited = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for w in adj[u]:
            if w not in visited:
                visited.add(w)
                q.append(w)
    return all(v in visited for v in has_edge)


# ===================================================================
# Exercise 3: Hierholzer (Directed)
# ===================================================================

def euler_path_directed(n, edges):
    """
    Return list of vertices forming an Euler path/circuit on the directed
    multigraph, or None if none exists.
    """
    # TODO: implement Hierholzer iteratively
    pass


def _sol_euler_path_directed(n, edges):
    indeg = [0] * n
    outdeg = [0] * n
    adj = defaultdict(deque)
    for u, v in edges:
        outdeg[u] += 1
        indeg[v] += 1
        adj[u].append(v)

    start_extra = []
    end_extra = []
    for v in range(n):
        d = outdeg[v] - indeg[v]
        if d == 1:
            start_extra.append(v)
        elif d == -1:
            end_extra.append(v)
        elif d != 0:
            return None
    nonzero = [v for v in range(n) if indeg[v] + outdeg[v] > 0]
    if not nonzero:
        return [0]

    if not start_extra and not end_extra:
        start = nonzero[0]
    elif len(start_extra) == 1 and len(end_extra) == 1:
        start = start_extra[0]
    else:
        return None

    stack = [start]
    circuit = []
    while stack:
        v = stack[-1]
        if adj[v]:
            stack.append(adj[v].popleft())
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    # Length check: should have used every edge
    if len(circuit) - 1 != len(edges):
        return None
    return circuit


# ===================================================================
# Exercise 4: Hierholzer (Undirected)
# ===================================================================

def euler_path_undirected(n, edges):
    """
    Return list of vertices forming an Euler path/circuit on the undirected
    multigraph, or None if none exists. Edges must be tracked by index.
    """
    # TODO: implement Hierholzer iteratively with edge-index marking
    pass


def _sol_euler_path_undirected(n, edges):
    if not _sol_has_euler_path_undirected(n, edges):
        return None
    deg = [0] * n
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
        deg[u] += 1
        deg[v] += 1

    odd = [v for v in range(n) if deg[v] % 2 == 1]
    has_edge = [v for v in range(n) if deg[v] > 0]
    if not has_edge:
        return [0]
    start = odd[0] if odd else has_edge[0]

    used = [False] * len(edges)
    ptr = [0] * n
    stack = [start]
    circuit = []
    while stack:
        v = stack[-1]
        while ptr[v] < len(adj[v]) and used[adj[v][ptr[v]][1]]:
            ptr[v] += 1
        if ptr[v] < len(adj[v]):
            u, eid = adj[v][ptr[v]]
            used[eid] = True
            ptr[v] += 1
            stack.append(u)
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    return circuit


# ===================================================================
# Exercise 5: Genome Reconstruction
# ===================================================================
# Given k-mers (substrings of length k), reconstruct the original string
# by finding an Euler path on the de Bruijn graph.

def reconstruct_from_kmers(kmers):
    """
    kmers: list of equal-length strings, each consecutive pair overlaps by k-1.
    Returns: original string, or None if no valid reconstruction.
    """
    # TODO: build de Bruijn graph and call euler_path_directed
    pass


def _sol_reconstruct_from_kmers(kmers):
    if not kmers:
        return ""
    k = len(kmers[0])
    node_id = {}

    def gid(s):
        if s not in node_id:
            node_id[s] = len(node_id)
        return node_id[s]

    edges = []
    for kmer in kmers:
        edges.append((gid(kmer[:-1]), gid(kmer[1:])))
    path = _sol_euler_path_directed(len(node_id), edges)
    if path is None:
        return None
    id_to_node = {i: s for s, i in node_id.items()}
    result = id_to_node[path[0]]
    for nid in path[1:]:
        result += id_to_node[nid][-1]
    return result


# ===================================================================
# Exercise 6: Min Edges to Add for Euler Circuit
# ===================================================================
# How many edges must you add to make an undirected graph Eulerian?
# Answer: count odd-degree vertices, divide by 2 (you can pair them up).
# (Assumes graph is connected and has at least one edge.)

def min_edges_for_euler_circuit(n, edges):
    """
    Return minimum number of edges to add so all vertices have even degree.
    """
    # TODO: count odd-degree vertices
    pass


def _sol_min_edges_for_euler_circuit(n, edges):
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        if u == v:
            deg[u] += 1
    return sum(1 for d in deg if d % 2 == 1) // 2


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

    print("Exercise 1: Has Euler Circuit (Undirected)")
    # Triangle: all degrees 2 -> yes
    check("triangle", try_or_sol("has_euler_circuit_undirected", 3,
          [(0, 1), (1, 2), (2, 0)]), True)
    # Path 0-1-2: degrees 1,2,1 -> no
    check("path", try_or_sol("has_euler_circuit_undirected", 3,
          [(0, 1), (1, 2)]), False)
    # Konigsberg: 4 odd vertices
    konigsberg = [(0, 1), (0, 1), (0, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
    check("konigsberg", try_or_sol("has_euler_circuit_undirected", 4, konigsberg), False)

    print("\nExercise 2: Has Euler Path (Undirected)")
    check("path 0-1-2", try_or_sol("has_euler_path_undirected", 3,
          [(0, 1), (1, 2)]), True)
    check("4 odd verts", try_or_sol("has_euler_path_undirected", 4, konigsberg), False)
    check("circuit also has path", try_or_sol("has_euler_path_undirected", 3,
          [(0, 1), (1, 2), (2, 0)]), True)

    print("\nExercise 3: Hierholzer (Directed)")
    # 0 -> 1 -> 2 -> 0 circuit
    res = try_or_sol("euler_path_directed", 3, [(0, 1), (1, 2), (2, 0)])
    check("triangle circuit length", res is not None and len(res) == 4, True)
    # 0->1->2 path
    res = try_or_sol("euler_path_directed", 3, [(0, 1), (1, 2)])
    check("directed path", res, [0, 1, 2])
    # Non-Eulerian: 0->1, 0->2
    res = try_or_sol("euler_path_directed", 3, [(0, 1), (0, 2)])
    check("non-eulerian none", res, None)

    print("\nExercise 4: Hierholzer (Undirected)")
    res = try_or_sol("euler_path_undirected", 3, [(0, 1), (1, 2), (2, 0)])
    check("triangle length", res is not None and len(res) == 4, True)
    res = try_or_sol("euler_path_undirected", 3, [(0, 1), (1, 2)])
    check("undirected path length", res is not None and len(res) == 3, True)

    print("\nExercise 5: Genome Reconstruction")
    # Use a sequence with all-unique k-mers so reconstruction is deterministic.
    original = "AAGATTCTCTACG"
    k = 3
    kmers = [original[i:i+k] for i in range(len(original) - k + 1)]
    result = try_or_sol("reconstruct_from_kmers", kmers)
    # Reconstruction may differ from original if multiple paths; ensure
    # it produces a string with the same multiset of k-mers.
    def kmers_of(s, k):
        return sorted(s[i:i+k] for i in range(len(s) - k + 1))
    check("reconstruction kmers match",
          result is not None and kmers_of(result, k) == sorted(kmers), True)

    print("\nExercise 6: Min Edges for Euler Circuit")
    # All even -> 0
    check("triangle 0", try_or_sol("min_edges_for_euler_circuit", 3,
          [(0, 1), (1, 2), (2, 0)]), 0)
    # Path 0-1-2: 2 odd -> 1 edge needed
    check("path 1", try_or_sol("min_edges_for_euler_circuit", 3,
          [(0, 1), (1, 2)]), 1)
    # Konigsberg: 4 odd -> 2 edges
    check("konigsberg 2", try_or_sol("min_edges_for_euler_circuit", 4, konigsberg), 2)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
