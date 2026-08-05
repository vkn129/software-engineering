"""
Day 88 Practice: Articulation Points & Bridges
6 exercises on cut vertices, cut edges, biconnected components, and applications.
"""
from collections import defaultdict
import sys
sys.setrecursionlimit(10**6)


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Find articulation points
# ===================================================================

def articulation_points(n, edges):
    pass


def _sol_articulation_points(n, edges):
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


# ===================================================================
# Exercise 2: Find bridges
# ===================================================================

def bridges(n, edges):
    pass


def _sol_bridges(n, edges):
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))
    disc = [-1] * n
    low = [-1] * n
    br = []
    timer = [0]

    def dfs(u, pe):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        for v, eid in adj[u]:
            if eid == pe:
                continue
            if disc[v] == -1:
                dfs(v, eid)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    br.append(tuple(sorted((u, v))))
            else:
                low[u] = min(low[u], disc[v])

    for i in range(n):
        if disc[i] == -1:
            dfs(i, -1)
    return sorted(br)


# ===================================================================
# Exercise 3: Critical routers in a network
# ===================================================================

def critical_routers(n, links):
    """Find routers whose failure would split the network."""
    pass


def _sol_critical_routers(n, links):
    return _sol_articulation_points(n, links)


# ===================================================================
# Exercise 4: Must-have roads — closure would isolate a town
# ===================================================================

def must_have_roads(n, roads):
    pass


def _sol_must_have_roads(n, roads):
    return _sol_bridges(n, roads)


# ===================================================================
# Exercise 5: 2-edge-connected components
# ===================================================================

def two_edge_connected_components(n, edges):
    """Group vertices into 2-edge-connected components (bridge-removed CCs).
    Return sorted list of components, each a sorted list."""
    pass


def _sol_two_edge_connected_components(n, edges):
    bridge_set = set(_sol_bridges(n, edges))
    adj = defaultdict(set)
    for u, v in edges:
        if tuple(sorted((u, v))) in bridge_set:
            continue
        adj[u].add(v)
        adj[v].add(u)
    visited = [False] * n
    components = []
    for start in range(n):
        if visited[start]:
            continue
        comp = [start]
        visited[start] = True
        stack = [start]
        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    comp.append(v)
                    stack.append(v)
        components.append(sorted(comp))
    return sorted(components)


# ===================================================================
# Exercise 6: Minimum edges to make graph biconnected
# (= ceil(leaves_in_bridge_tree / 2))
# ===================================================================

def edges_to_make_biconnected(n, edges):
    """If we contract each 2-edge-CC, we get the bridge tree.
    Minimum edges to add to eliminate all bridges = ceil(leaves / 2)."""
    pass


def _sol_edges_to_make_biconnected(n, edges):
    bridge_set = set(_sol_bridges(n, edges))
    components = _sol_two_edge_connected_components(n, edges)
    if len(components) <= 1:
        return 0
    node_comp = {}
    for cid, comp in enumerate(components):
        for u in comp:
            node_comp[u] = cid
    tree_deg = defaultdict(int)
    for u, v in bridge_set:
        c1, c2 = node_comp[u], node_comp[v]
        if c1 != c2:
            tree_deg[c1] += 1
            tree_deg[c2] += 1
    leaves = sum(1 for c in range(len(components)) if tree_deg[c] <= 1)
    return (leaves + 1) // 2


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    print("Day 88 — Articulation Points & Bridges Practice")
    print("=" * 55)
    passed = total = 0

    total += 1
    chain = [(0, 1), (1, 2), (2, 3), (3, 4)]
    if _sol_articulation_points(5, chain) == [1, 2, 3]:
        print("  PASS: articulation points on chain")
        passed += 1
    else:
        print(f"  FAIL: {_sol_articulation_points(5, chain)}")

    total += 1
    if _sol_bridges(5, chain) == [(0, 1), (1, 2), (2, 3), (3, 4)]:
        print("  PASS: bridges on chain")
        passed += 1
    else:
        print(f"  FAIL: bridges {_sol_bridges(5, chain)}")

    total += 1
    tri = [(0, 1), (1, 2), (2, 0)]
    if _sol_articulation_points(3, tri) == [] and _sol_bridges(3, tri) == []:
        print("  PASS: triangle has no AP or bridges")
        passed += 1
    else:
        print(f"  FAIL: triangle AP={_sol_articulation_points(3, tri)} br={_sol_bridges(3, tri)}")

    total += 1
    if _sol_critical_routers(5, chain) == [1, 2, 3]:
        print("  PASS: critical routers identified")
        passed += 1
    else:
        print(f"  FAIL: critical routers")

    total += 1
    dumbbell = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
    comps = _sol_two_edge_connected_components(6, dumbbell)
    if comps == [[0, 1, 2], [3, 4, 5]]:
        print(f"  PASS: 2-edge-CCs — {comps}")
        passed += 1
    else:
        print(f"  FAIL: 2-edge-CCs got {comps}")

    total += 1
    n_to_add = _sol_edges_to_make_biconnected(6, dumbbell)
    if n_to_add == 1:
        print(f"  PASS: edges to biconnected = {n_to_add}")
        passed += 1
    else:
        print(f"  FAIL: expected 1, got {n_to_add}")

    print("=" * 55)
    print(f"Results: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
