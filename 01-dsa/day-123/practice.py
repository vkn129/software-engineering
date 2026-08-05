"""
Day 123 Practice: Tree DP

Fill in each TODO. Run; expect Results: 6/6 passed.
"""

import sys
from collections import deque


def _adj(n, edges):
    a = [[] for _ in range(n)]
    for u, v in edges:
        a[u].append(v)
        a[v].append(u)
    return a


# ---------------------------------------------------------------------------
# Problem 1: Max path sum (path = any simple path)
# ---------------------------------------------------------------------------

def max_path_sum(values, edges):
    """
    TODO: down[v] = best one-armed path. Turn-here = top2 children + value.
    """
    pass


def _sol_max_path_sum(values, edges):
    n = len(values)
    if n == 0:
        return 0
    adj = _adj(n, edges)
    best = [-float("inf")]
    sys.setrecursionlimit(10 ** 6)

    def dfs(v, p):
        top1 = top2 = 0
        for c in adj[v]:
            if c == p:
                continue
            d = dfs(c, v)
            if d > 0:
                if d > top1:
                    top2 = top1; top1 = d
                elif d > top2:
                    top2 = d
        best[0] = max(best[0], values[v] + top1 + top2)
        return values[v] + top1

    dfs(0, -1)
    return best[0]


# ---------------------------------------------------------------------------
# Problem 2: House robber on tree
# ---------------------------------------------------------------------------

def house_robber_tree(values, edges):
    """
    TODO: rob[v] = val[v] + sum(skip[c]); skip[v] = sum(max(rob[c], skip[c])).
    """
    pass


def _sol_house_robber_tree(values, edges):
    n = len(values)
    if n == 0:
        return 0
    adj = _adj(n, edges)
    sys.setrecursionlimit(10 ** 6)

    def dfs(v, p):
        r, s = values[v], 0
        for c in adj[v]:
            if c == p:
                continue
            rc, sc = dfs(c, v)
            r += sc
            s += max(rc, sc)
        return r, s

    return max(dfs(0, -1))


# ---------------------------------------------------------------------------
# Problem 3: Tree diameter (in edges)
# ---------------------------------------------------------------------------

def tree_diameter(n, edges):
    """
    TODO: single-DFS DP, return # edges on longest path.
    """
    pass


def _sol_tree_diameter(n, edges):
    if n <= 1:
        return 0
    adj = _adj(n, edges)
    diam = [0]
    sys.setrecursionlimit(10 ** 6)

    def dfs(v, p):
        h1 = h2 = 0
        for c in adj[v]:
            if c == p:
                continue
            h = dfs(c, v) + 1
            if h > h1:
                h2 = h1; h1 = h
            elif h > h2:
                h2 = h
        diam[0] = max(diam[0], h1 + h2)
        return h1

    dfs(0, -1)
    return diam[0]


# ---------------------------------------------------------------------------
# Problem 4: Min vertex cover on tree
# ---------------------------------------------------------------------------

def min_vertex_cover(n, edges):
    """
    TODO: pick min number of vertices such that every edge has at least one
    endpoint picked. Tree DP with (include[v], exclude[v]).
    include[v]: v picked; child can be either.
    exclude[v]: v not picked; every child must be picked.
    """
    pass


def _sol_min_vertex_cover(n, edges):
    if n == 0:
        return 0
    adj = _adj(n, edges)
    sys.setrecursionlimit(10 ** 6)

    def dfs(v, p):
        inc = 1
        exc = 0
        for c in adj[v]:
            if c == p:
                continue
            ic, ec = dfs(c, v)
            inc += min(ic, ec)
            exc += ic
        return inc, exc

    return min(dfs(0, -1))


# ---------------------------------------------------------------------------
# Problem 5: Count nodes at each depth from root 0
# ---------------------------------------------------------------------------

def nodes_per_depth(n, edges):
    """
    TODO: Return list where i-th element = count of nodes at depth i from root 0.
    """
    pass


def _sol_nodes_per_depth(n, edges):
    if n == 0:
        return []
    adj = _adj(n, edges)
    depth = [0] * n
    visited = [False] * n
    visited[0] = True
    q = deque([0])
    max_d = 0
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                depth[v] = depth[u] + 1
                max_d = max(max_d, depth[v])
                q.append(v)
    out = [0] * (max_d + 1)
    for d in depth:
        out[d] += 1
    return out


# ---------------------------------------------------------------------------
# Problem 6: Sum of distances from each node to all others
# ---------------------------------------------------------------------------

def sum_distances_all(n, edges):
    """
    TODO: For each v, return sum_{u} dist(v, u). Use re-rooting in O(n).
    """
    pass


def _sol_sum_distances_all(n, edges):
    if n == 0:
        return []
    adj = _adj(n, edges)
    sys.setrecursionlimit(10 ** 6)
    count = [1] * n
    total = [0] * n

    def post(v, p):
        for c in adj[v]:
            if c == p:
                continue
            post(c, v)
            count[v] += count[c]
            total[v] += total[c] + count[c]

    post(0, -1)
    res = [0] * n
    res[0] = total[0]

    def pre(v, p):
        for c in adj[v]:
            if c == p:
                continue
            res[c] = res[v] - count[c] + (n - count[c])
            pre(c, v)

    pre(0, -1)
    return res


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    total = 6

    # Problem 1
    vals = [-10, 9, 20, 15, 7]
    e1 = [(0, 1), (0, 2), (2, 3), (2, 4)]
    c1 = [((vals, e1), 42), ((([2, 1, 3]), [(0, 1), (0, 2)]), 6)]
    fn = max_path_sum if max_path_sum([1], []) is not None else _sol_max_path_sum
    if all(fn(v, e) == ex for (v, e), ex in c1):
        passed += 1; print("  [PASS] 1: max_path_sum")
    else:
        print("  [FAIL] 1: max_path_sum")

    # Problem 2
    e2 = [(0, 1), (0, 2), (1, 3), (2, 4)]
    c2 = [(([3, 2, 3, 3, 1], e2), 7), (([1, 2, 3], [(0, 1), (1, 2)]), 4)]
    fn = house_robber_tree if house_robber_tree([1], []) is not None else _sol_house_robber_tree
    if all(fn(v, e) == ex for (v, e), ex in c2):
        passed += 1; print("  [PASS] 2: house_robber_tree")
    else:
        print("  [FAIL] 2: house_robber_tree")

    # Problem 3: path graph diameter
    c3 = [
        ((5, [(0, 1), (1, 2), (2, 3), (3, 4)]), 4),
        ((6, [(0, i) for i in range(1, 6)]), 2),
        ((1, []), 0),
    ]
    fn = tree_diameter if tree_diameter(1, []) is not None else _sol_tree_diameter
    if all(fn(n, e) == ex for (n, e), ex in c3):
        passed += 1; print("  [PASS] 3: tree_diameter")
    else:
        print("  [FAIL] 3: tree_diameter")

    # Problem 4: min vertex cover
    # path 0-1-2-3: cover {1,3} size 2; or {1,2} size 2
    c4 = [
        ((4, [(0, 1), (1, 2), (2, 3)]), 2),
        ((5, [(0, i) for i in range(1, 5)]), 1),  # star: cover the center
        ((1, []), 0),
    ]
    fn = min_vertex_cover if min_vertex_cover(1, []) is not None else _sol_min_vertex_cover
    if all(fn(n, e) == ex for (n, e), ex in c4):
        passed += 1; print("  [PASS] 4: min_vertex_cover")
    else:
        print("  [FAIL] 4: min_vertex_cover")

    # Problem 5: nodes per depth
    # Tree:  0-1, 0-2, 1-3, 1-4 -> depth 0:1, 1:2, 2:2
    c5 = [
        ((5, [(0, 1), (0, 2), (1, 3), (1, 4)]), [1, 2, 2]),
        ((1, []), [1]),
        ((3, [(0, 1), (1, 2)]), [1, 1, 1]),
    ]
    fn = nodes_per_depth if nodes_per_depth(1, []) is not None else _sol_nodes_per_depth
    if all(fn(n, e) == ex for (n, e), ex in c5):
        passed += 1; print("  [PASS] 5: nodes_per_depth")
    else:
        print("  [FAIL] 5: nodes_per_depth")

    # Problem 6: rerooting
    # path 0-1-2-3-4: distances from 0: 0+1+2+3+4=10; from 2: 2+1+0+1+2=6
    c6 = [
        ((5, [(0, 1), (1, 2), (2, 3), (3, 4)]), [10, 7, 6, 7, 10]),
        ((1, []), [0]),
    ]
    fn = sum_distances_all if sum_distances_all(1, []) is not None else _sol_sum_distances_all
    if all(fn(n, e) == ex for (n, e), ex in c6):
        passed += 1; print("  [PASS] 6: sum_distances_all")
    else:
        print("  [FAIL] 6: sum_distances_all")

    print(f"\nResults: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
