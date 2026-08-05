"""
Day 172 Practice: Heavy-Light Decomposition

6 exercises covering subtree sizes, heavy edges, HLD positions,
LCA via HLD, path sum, and path max with updates.
Run: python practice.py
"""

import sys
sys.setrecursionlimit(10**6)


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


def _build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    return adj


# ===================================================================
# Exercise 1: Subtree Sizes
# ===================================================================
# Compute subtree size for every node (root = 0).

def subtree_sizes(n, edges):
    """
    n: nodes 0..n-1
    edges: undirected edges
    Returns: list size[v] = number of nodes in subtree of v rooted at 0
    """
    # TODO: DFS + accumulate
    pass


def _sol_subtree_sizes(n, edges):
    adj = _build_adj(n, edges)
    size = [1] * n
    visited = [False] * n
    order = []
    # iterative DFS to get postorder
    stack = [(0, -1, False)]
    while stack:
        u, par, processed = stack.pop()
        if processed:
            for v in adj[u]:
                if v != par:
                    size[u] += size[v]
            continue
        if visited[u]:
            continue
        visited[u] = True
        stack.append((u, par, True))
        for v in adj[u]:
            if v != par:
                stack.append((v, u, False))
    return size


# ===================================================================
# Exercise 2: Heavy Child
# ===================================================================

def heavy_child(n, edges):
    """
    n: nodes 0..n-1, root = 0
    edges: undirected
    Returns: list heavy[v] = child of v with largest subtree, or -1 if leaf.
             On ties, pick the smallest-indexed child.
    """
    # TODO
    pass


def _sol_heavy_child(n, edges):
    size = _sol_subtree_sizes(n, edges)
    adj = _build_adj(n, edges)
    # Determine parent via BFS
    from collections import deque
    parent = [-1] * n
    visited = [False] * n
    visited[0] = True
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                q.append(v)
    heavy = [-1] * n
    for v in range(n):
        best = -1
        for c in sorted(adj[v]):
            if c == parent[v]:
                continue
            if best == -1 or size[c] > size[best]:
                best = c
        heavy[v] = best
    return heavy


# ===================================================================
# Exercise 3: HLD Positions
# ===================================================================
# Assign DFS positions descending into the heavy child first.

def hld_positions(n, edges):
    """
    n: nodes 0..n-1, root = 0
    Returns: pos array where pos[v] is the DFS index when descending
             heavy child first.
    """
    # TODO
    pass


def _sol_hld_positions(n, edges):
    heavy = _sol_heavy_child(n, edges)
    adj = _build_adj(n, edges)
    from collections import deque
    parent = [-1] * n
    visited = [False] * n
    visited[0] = True
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True; parent[v] = u; q.append(v)
    pos = [-1] * n
    cur = [0]

    def dfs(u):
        pos[u] = cur[0]; cur[0] += 1
        if heavy[u] != -1:
            dfs(heavy[u])
        for v in adj[u]:
            if v == parent[u] or v == heavy[u]:
                continue
            dfs(v)

    dfs(0)
    return pos


# ===================================================================
# Exercise 4: LCA via HLD-style climbing
# ===================================================================

def lca_hld(n, edges, queries):
    """
    n, edges define a rooted tree (root=0).
    queries: list of (u, v)
    Returns: list of LCAs using head-jumping.
    """
    # TODO
    pass


def _sol_lca_hld(n, edges, queries):
    heavy = _sol_heavy_child(n, edges)
    adj = _build_adj(n, edges)
    from collections import deque
    parent = [-1] * n
    depth = [0] * n
    visited = [False] * n
    visited[0] = True
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True; parent[v] = u; depth[v] = depth[u] + 1
                q.append(v)
    head = [0] * n
    cur = [0]
    pos = [0] * n

    def dfs(u, h):
        head[u] = h
        pos[u] = cur[0]; cur[0] += 1
        if heavy[u] != -1:
            dfs(heavy[u], h)
        for v in adj[u]:
            if v == parent[u] or v == heavy[u]:
                continue
            dfs(v, v)
    dfs(0, 0)

    ans = []
    for u, v in queries:
        while head[u] != head[v]:
            if depth[head[u]] < depth[head[v]]:
                u, v = v, u
            u = parent[head[u]]
        ans.append(u if depth[u] < depth[v] else v)
    return ans


# ===================================================================
# Exercise 5: Path Sum via HLD
# ===================================================================

def hld_path_sums(n, edges, values, queries):
    """
    Returns: list of path sums (inclusive of both endpoints).
    """
    # TODO: use HLD with a segment tree (or even a flat prefix sum on the layout).
    pass


def _sol_hld_path_sums(n, edges, values, queries):
    # Just brute force for small cases (problem is the practice of pattern)
    adj = _build_adj(n, edges)
    from collections import deque
    parent = [-1] * n; depth = [0] * n
    visited = [False] * n; visited[0] = True
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True; parent[v] = u; depth[v] = depth[u] + 1
                q.append(v)
    ans = []
    for u, v in queries:
        nodes = set()
        a, b = u, v
        while a != b:
            if depth[a] < depth[b]:
                a, b = b, a
            nodes.add(a); a = parent[a]
        nodes.add(a)
        nodes.update([u, v])
        ans.append(sum(values[x] for x in nodes))
    return ans


# ===================================================================
# Exercise 6: Path Max with Point Updates
# ===================================================================

def hld_path_max_with_updates(n, edges, values, ops):
    """
    ops: list of either ('update', v, new_val) or ('query', u, v)
    Returns: list of answers, one per 'query' op (path max).
    """
    # TODO
    pass


def _sol_hld_path_max_with_updates(n, edges, values, ops):
    vals = values[:]
    adj = _build_adj(n, edges)
    from collections import deque
    parent = [-1] * n; depth = [0] * n
    visited = [False] * n; visited[0] = True
    q = deque([0])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True; parent[v] = u; depth[v] = depth[u] + 1
                q.append(v)

    def path_max(u, v):
        a, b = u, v
        nodes = set()
        while a != b:
            if depth[a] < depth[b]:
                a, b = b, a
            nodes.add(a); a = parent[a]
        nodes.add(a)
        nodes.update([u, v])
        return max(vals[x] for x in nodes)

    out = []
    for op in ops:
        if op[0] == 'update':
            _, v, nv = op
            vals[v] = nv
        else:
            _, u, v = op
            out.append(path_max(u, v))
    return out


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

    # Tree:    0
    #         / \
    #        1   2
    #       /|   |
    #      3 4   5
    n = 6
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
    values = [10, 20, 30, 40, 50, 60]

    # --- Exercise 1 ---
    print("Exercise 1: Subtree Sizes")
    check("sizes", try_or_sol("subtree_sizes", n, edges), [6, 3, 2, 1, 1, 1])

    # --- Exercise 2 ---
    print("\nExercise 2: Heavy Child")
    # 0's children: 1(size 3), 2(size 2) -> heavy = 1
    # 1's children: 3(1), 4(1) -> tie, smallest = 3
    # 2's children: 5(1) -> 5
    check("heavy", try_or_sol("heavy_child", n, edges), [1, 3, 5, -1, -1, -1])

    # --- Exercise 3 ---
    print("\nExercise 3: HLD Positions")
    pos = try_or_sol("hld_positions", n, edges)
    # 0 (pos 0) -> heavy=1 (pos 1) -> heavy=3 (pos 2) -> backtrack -> 4 (pos 3)
    # backtrack -> 2 (pos 4) -> heavy=5 (pos 5)
    check("positions", pos, [0, 1, 4, 2, 3, 5])

    # --- Exercise 4 ---
    print("\nExercise 4: LCA via HLD")
    qs = [(3, 4), (3, 5), (4, 2), (0, 5)]
    check("LCAs", try_or_sol("lca_hld", n, edges, qs), [1, 0, 0, 0])

    # --- Exercise 5 ---
    print("\nExercise 5: HLD Path Sums")
    qs = [(3, 4), (3, 5), (4, 5)]
    # path 3->4: 3,1,4 -> 40+20+50=110
    # path 3->5: 3,1,0,2,5 -> 40+20+10+30+60=160
    # path 4->5: 4,1,0,2,5 -> 50+20+10+30+60=170
    check("path sums", try_or_sol("hld_path_sums", n, edges, values, qs),
          [110, 160, 170])

    # --- Exercise 6 ---
    print("\nExercise 6: HLD Path Max with Updates")
    ops = [('query', 3, 5), ('update', 0, 99), ('query', 3, 5), ('query', 4, 4)]
    # initial path 3->5: 3,1,0,2,5 vals 40,20,10,30,60 -> max=60
    # after 0=99: max=99
    # query 4->4: just 50
    check("path max ops", try_or_sol("hld_path_max_with_updates", n, edges, values, ops),
          [60, 99, 50])

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
