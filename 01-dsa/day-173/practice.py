"""
Day 173 Practice: Centroid Decomposition

6 exercises covering subtree sizes, centroid finding, centroid tree,
pair counting, sum of distances, and centroid tree depth.
Run: python practice.py
"""

import sys
sys.setrecursionlimit(10**6)
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


def _build_adj(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    return adj


# ===================================================================
# Exercise 1: Subtree Size from a Root (excluding "removed" nodes)
# ===================================================================

def component_size(n, edges, start, removed):
    """
    Return number of nodes reachable from `start` ignoring nodes where
    removed[v] is True.
    """
    # TODO: BFS or DFS, skip removed
    pass


def _sol_component_size(n, edges, start, removed):
    adj = _build_adj(n, edges)
    if removed[start]:
        return 0
    visited = [False] * n
    visited[start] = True
    q = deque([start])
    count = 0
    while q:
        u = q.popleft(); count += 1
        for v in adj[u]:
            if not visited[v] and not removed[v]:
                visited[v] = True; q.append(v)
    return count


# ===================================================================
# Exercise 2: Find Centroid
# ===================================================================

def find_centroid(n, edges, start):
    """
    Return the centroid of the connected tree containing `start`.
    No nodes are removed.
    """
    # TODO: compute sizes, then walk to heaviest subtree until <= total//2.
    pass


def _sol_find_centroid(n, edges, start):
    adj = _build_adj(n, edges)
    removed = [False] * n
    size = [0] * n

    def dfs_size(u, par):
        size[u] = 1
        for v in adj[u]:
            if v != par and not removed[v]:
                dfs_size(v, u); size[u] += size[v]
    dfs_size(start, -1)
    total = size[start]

    def find(u, par):
        for v in adj[u]:
            if v != par and not removed[v] and size[v] > total // 2:
                return find(v, u)
        return u

    return find(start, -1)


# ===================================================================
# Exercise 3: Build Centroid Tree
# ===================================================================
# Return parent_in_centroid_tree[v] for each v.

def build_centroid_tree(n, edges):
    """
    Return list parent_ct where parent_ct[c] is the centroid-tree parent of c
    (or -1 for the centroid-tree root).
    """
    # TODO
    pass


def _sol_build_centroid_tree(n, edges):
    adj = _build_adj(n, edges)
    removed = [False] * n
    size = [0] * n
    par_ct = [-1] * n

    def dfs_size(u, par):
        size[u] = 1
        for v in adj[u]:
            if v != par and not removed[v]:
                dfs_size(v, u); size[u] += size[v]

    def find_c(u, par, ts):
        for v in adj[u]:
            if v != par and not removed[v] and size[v] > ts // 2:
                return find_c(v, u, ts)
        return u

    def decompose(start, ct_par):
        dfs_size(start, -1)
        c = find_c(start, -1, size[start])
        par_ct[c] = ct_par
        removed[c] = True
        for v in adj[c]:
            if not removed[v]:
                decompose(v, c)

    decompose(0, -1)
    return par_ct


# ===================================================================
# Exercise 4: Count Pairs at Exact Distance K
# ===================================================================

def count_pairs_distance_k(n, edges, k):
    """
    Count unordered pairs (u, v), u != v, with shortest distance == k.
    """
    # TODO: use centroid decomposition, or brute for small n.
    pass


def _sol_count_pairs_distance_k(n, edges, k):
    adj = _build_adj(n, edges)
    removed = [False] * n
    size = [0] * n

    def calc_size(u, par):
        size[u] = 1
        for v in adj[u]:
            if v != par and not removed[v]:
                calc_size(v, u); size[u] += size[v]

    def find_c(u, par, ts):
        for v in adj[u]:
            if v != par and not removed[v] and size[v] > ts // 2:
                return find_c(v, u, ts)
        return u

    def collect(u, par, d, bucket):
        if d > k: return
        bucket[d] += 1
        for v in adj[u]:
            if v != par and not removed[v]:
                collect(v, u, d + 1, bucket)

    count = [0]

    def solve(start):
        calc_size(start, -1)
        c = find_c(start, -1, size[start])
        combined = defaultdict(int)
        combined[0] = 1
        for v in adj[c]:
            if removed[v]:
                continue
            sub = defaultdict(int)
            collect(v, c, 1, sub)
            for d, cnt in sub.items():
                need = k - d
                if need >= 0 and need in combined:
                    count[0] += cnt * combined[need]
            for d, cnt in sub.items():
                combined[d] += cnt
        removed[c] = True
        for v in adj[c]:
            if not removed[v]:
                solve(v)

    solve(0)
    return count[0]


# ===================================================================
# Exercise 5: Sum of All-Pair Distances (brute is fine for small N)
# ===================================================================

def sum_distances(n, edges):
    """
    Sum over all unordered pairs (u, v) of dist(u, v).
    """
    # TODO
    pass


def _sol_sum_distances(n, edges):
    adj = _build_adj(n, edges)
    total = 0
    for s in range(n):
        dist = [-1] * n; dist[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    q.append(v)
        total += sum(d for d in dist if d > 0)
    return total // 2


# ===================================================================
# Exercise 6: Centroid Tree Depth
# ===================================================================

def centroid_tree_depth(n, edges):
    """
    Return the maximum depth in the centroid tree.
    For path of length n, expected = floor(log2 n).
    """
    # TODO
    pass


def _sol_centroid_tree_depth(n, edges):
    par = _sol_build_centroid_tree(n, edges)
    depth = [0] * n
    # compute via memoization
    def d(v):
        if par[v] == -1:
            return 0
        if depth[v]:
            return depth[v]
        depth[v] = 1 + d(par[v])
        return depth[v]
    return max(d(v) for v in range(n))


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

    # Path 0-1-2-3-4
    path_edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
    # Star: center 0, leaves 1..5
    star_edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]

    # --- Exercise 1 ---
    print("Exercise 1: Component Size")
    check("path full", try_or_sol("component_size", 5, path_edges, 0, [False]*5), 5)
    rem = [False, False, True, False, False]  # remove node 2 -> 2 components
    check("path split", try_or_sol("component_size", 5, path_edges, 0, rem), 2)
    check("path split right", try_or_sol("component_size", 5, path_edges, 3, rem), 2)

    # --- Exercise 2 ---
    print("\nExercise 2: Find Centroid")
    check("path centroid", try_or_sol("find_centroid", 5, path_edges, 0), 2)
    check("star centroid", try_or_sol("find_centroid", 6, star_edges, 0), 0)

    # --- Exercise 3 ---
    print("\nExercise 3: Build Centroid Tree")
    par = try_or_sol("build_centroid_tree", 5, path_edges)
    # Root of CT is the centroid of the whole tree (node 2 for path of 5)
    check("CT root is 2", par[2], -1)

    # --- Exercise 4 ---
    print("\nExercise 4: Count Pairs Distance K")
    #   star: all leaves at distance 2 from each other; 5 leaves -> C(5,2)=10
    check("star d=2", try_or_sol("count_pairs_distance_k", 6, star_edges, 2), 10)
    check("star d=1", try_or_sol("count_pairs_distance_k", 6, star_edges, 1), 5)
    # path d=1: 4 pairs (consecutive)
    check("path d=1", try_or_sol("count_pairs_distance_k", 5, path_edges, 1), 4)
    # path d=4: only (0,4) -> 1
    check("path d=4", try_or_sol("count_pairs_distance_k", 5, path_edges, 4), 1)

    # --- Exercise 5 ---
    print("\nExercise 5: Sum of Distances")
    # path 0-1-2-3-4: all pairs distances
    # (0,1)1,(0,2)2,(0,3)3,(0,4)4,(1,2)1,(1,3)2,(1,4)3,(2,3)1,(2,4)2,(3,4)1
    # = 1+2+3+4+1+2+3+1+2+1 = 20
    check("path sum", try_or_sol("sum_distances", 5, path_edges), 20)
    # star: each leaf-center=1 (5 pairs), each leaf-leaf=2 (C(5,2)=10 pairs)
    # = 5*1 + 10*2 = 25
    check("star sum", try_or_sol("sum_distances", 6, star_edges), 25)

    # --- Exercise 6 ---
    print("\nExercise 6: Centroid Tree Depth")
    # Path of 5: centroid tree depth = log2(5) rounded = 2
    check("path depth", try_or_sol("centroid_tree_depth", 5, path_edges), 2)
    # Star: center is root; all leaves are at depth 1
    check("star depth", try_or_sol("centroid_tree_depth", 6, star_edges), 1)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    run_tests()
