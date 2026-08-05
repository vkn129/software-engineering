"""
Day 123: Tree DP — From Scratch

Trees make DP easy: subproblems align with subtrees, post-order DFS gives
a free topological order.

  1. Max path sum (any node to any node)
  2. House robber on tree (no two adjacent picks)
  3. Tree diameter — both DP and two-BFS approaches
"""

import sys
from collections import deque


# ---------------------------------------------------------------------------
# Tree representation: adjacency list (undirected for general tree problems)
# ---------------------------------------------------------------------------

def adj_from_edges(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


# ---------------------------------------------------------------------------
# 1. Max Path Sum (path = any sequence of connected nodes)
# ---------------------------------------------------------------------------

def max_path_sum(values, edges, root=0):
    """
    Returns the max sum over all simple paths in the tree.
    values[i] is the value at node i.
    """
    n = len(values)
    if n == 0:
        return 0
    adj = adj_from_edges(n, edges)
    best = [-float("inf")]

    sys.setrecursionlimit(10 ** 6)

    def dfs(v, parent):
        # down[v] = best one-armed path starting at v going down
        top1 = top2 = 0  # top two positive child-downs
        for c in adj[v]:
            if c == parent:
                continue
            d = dfs(c, v)
            if d > 0:
                if d > top1:
                    top2 = top1
                    top1 = d
                elif d > top2:
                    top2 = d
        # turn-at-v path
        best[0] = max(best[0], values[v] + top1 + top2)
        return values[v] + top1

    dfs(root, -1)
    return best[0]


# ---------------------------------------------------------------------------
# 2. House Robber on Tree
# ---------------------------------------------------------------------------

def house_robber_tree(values, edges, root=0):
    """
    Cannot rob two adjacent nodes. Max total robbed.
    Returns max(rob[root], skip[root]).
    """
    n = len(values)
    if n == 0:
        return 0
    adj = adj_from_edges(n, edges)

    sys.setrecursionlimit(10 ** 6)

    def dfs(v, parent):
        rob_v = values[v]
        skip_v = 0
        for c in adj[v]:
            if c == parent:
                continue
            rc, sc = dfs(c, v)
            rob_v += sc           # if I rob v, child must be skipped
            skip_v += max(rc, sc)  # if I skip v, child takes best
        return rob_v, skip_v

    return max(dfs(root, -1))


# ---------------------------------------------------------------------------
# 3. Tree Diameter
# ---------------------------------------------------------------------------

def tree_diameter_dp(n, edges):
    """
    Longest path in tree (counted in EDGES).
    Single DFS, O(n).
    """
    if n <= 1:
        return 0
    adj = adj_from_edges(n, edges)
    diameter = [0]

    sys.setrecursionlimit(10 ** 6)

    def dfs(v, parent):
        h1 = h2 = 0
        for c in adj[v]:
            if c == parent:
                continue
            h = dfs(c, v) + 1
            if h > h1:
                h2 = h1
                h1 = h
            elif h > h2:
                h2 = h
        diameter[0] = max(diameter[0], h1 + h2)
        return h1

    dfs(0, -1)
    return diameter[0]


def tree_diameter_two_bfs(n, edges):
    """Two BFS — alternative O(n) diameter algorithm."""
    if n <= 1:
        return 0
    adj = adj_from_edges(n, edges)

    def bfs_farthest(start):
        dist = [-1] * n
        dist[start] = 0
        q = deque([start])
        far, far_d = start, 0
        while q:
            u = q.popleft()
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = dist[u] + 1
                    if dist[v] > far_d:
                        far_d = dist[v]
                        far = v
                    q.append(v)
        return far, far_d

    u, _ = bfs_farthest(0)
    _, d = bfs_farthest(u)
    return d


# ---------------------------------------------------------------------------
# 4. Bonus: Rerooting — sum of distances from each node to all others
# ---------------------------------------------------------------------------

def sum_of_distances(n, edges):
    """
    res[v] = sum over u of dist(v, u). Solved via re-rooting in O(n).
    """
    if n == 0:
        return []
    adj = adj_from_edges(n, edges)
    count = [1] * n        # subtree size with 0 as root
    total = [0] * n        # sum of distances from 0 within v's subtree
    sys.setrecursionlimit(10 ** 6)

    def post(v, parent):
        for c in adj[v]:
            if c == parent:
                continue
            post(c, v)
            count[v] += count[c]
            total[v] += total[c] + count[c]

    post(0, -1)

    res = [0] * n
    res[0] = total[0]

    def pre(v, parent):
        for c in adj[v]:
            if c == parent:
                continue
            # Move root from v to c
            res[c] = res[v] - count[c] + (n - count[c])
            pre(c, v)

    pre(0, -1)
    return res


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_path_sum():
    print("=" * 60)
    print("DEMO 1: Max Path Sum")
    print("=" * 60)
    # Tree:
    #      -10
    #      /  \
    #     9    20
    #          / \
    #        15   7
    values = [-10, 9, 20, 15, 7]
    edges = [(0, 1), (0, 2), (2, 3), (2, 4)]
    ans = max_path_sum(values, edges, root=0)
    print(f"\n  Tree values: {values}")
    print(f"  Max path sum: {ans}  (expected 42 = 15+20+7)")


def demo_robber():
    print("\n" + "=" * 60)
    print("DEMO 2: House Robber on Tree")
    print("=" * 60)
    # Tree:
    #        3
    #       / \
    #      2   3
    #       \   \
    #        3   1
    values = [3, 2, 3, 3, 1]
    edges = [(0, 1), (0, 2), (1, 3), (2, 4)]
    ans = house_robber_tree(values, edges)
    print(f"\n  values: {values}")
    print(f"  max robbed: {ans}  (expected 7 = 3 + 3 + 1)")


def demo_diameter():
    print("\n" + "=" * 60)
    print("DEMO 3: Tree Diameter")
    print("=" * 60)
    # 0-1-2-3-4 (path), diameter = 4
    n = 5
    edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
    d1 = tree_diameter_dp(n, edges)
    d2 = tree_diameter_two_bfs(n, edges)
    print(f"\n  path graph 0-1-2-3-4: DP={d1}, two-BFS={d2}")

    # Star: center 0, leaves 1..5  -> diameter = 2
    n = 6
    edges = [(0, i) for i in range(1, 6)]
    d1 = tree_diameter_dp(n, edges)
    d2 = tree_diameter_two_bfs(n, edges)
    print(f"  star of 5 leaves:     DP={d1}, two-BFS={d2}")


def demo_reroot():
    print("\n" + "=" * 60)
    print("DEMO 4: Rerooting — Sum of Distances from Each Node")
    print("=" * 60)
    n = 6
    edges = [(0, 1), (0, 2), (2, 3), (2, 4), (2, 5)]
    res = sum_of_distances(n, edges)
    print(f"\n  tree edges: {edges}")
    for v in range(n):
        print(f"  node {v}: total dist = {res[v]}")


if __name__ == "__main__":
    demo_path_sum()
    demo_robber()
    demo_diameter()
    demo_reroot()
