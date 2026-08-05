"""
Day 172: Heavy-Light Decomposition (HLD) — From Scratch

Decompose a tree into heavy paths so any u-v path crosses O(log N) of them.
Combine with a segment tree (Day 52) for O(log^2 N) path queries.

Time:
  build: O(N)
  query/update: O(log^2 N)
Space: O(N)
"""

import sys
sys.setrecursionlimit(10**6)


# ---------------------------------------------------------------------------
# Iterative max segment tree (reuse pattern from Day 52)
# ---------------------------------------------------------------------------

class SegTreeMax:
    """Point update, range max query, iterative."""
    NEG_INF = -(10**18)

    def __init__(self, n):
        self.n = n
        self.t = [self.NEG_INF] * (2 * n)

    def build(self, values):
        for i, v in enumerate(values):
            self.t[self.n + i] = v
        for i in range(self.n - 1, 0, -1):
            self.t[i] = max(self.t[2*i], self.t[2*i + 1])

    def update(self, pos, val):
        pos += self.n
        self.t[pos] = val
        pos //= 2
        while pos:
            self.t[pos] = max(self.t[2*pos], self.t[2*pos + 1])
            pos //= 2

    def query(self, l, r):
        """Max over [l, r] inclusive."""
        res = self.NEG_INF
        l += self.n; r += self.n + 1
        while l < r:
            if l & 1:
                res = max(res, self.t[l]); l += 1
            if r & 1:
                r -= 1; res = max(res, self.t[r])
            l //= 2; r //= 2
        return res


class SegTreeSum:
    """Point update, range sum, iterative."""

    def __init__(self, n):
        self.n = n
        self.t = [0] * (2 * n)

    def build(self, values):
        for i, v in enumerate(values):
            self.t[self.n + i] = v
        for i in range(self.n - 1, 0, -1):
            self.t[i] = self.t[2*i] + self.t[2*i + 1]

    def update(self, pos, val):
        pos += self.n
        self.t[pos] = val
        pos //= 2
        while pos:
            self.t[pos] = self.t[2*pos] + self.t[2*pos + 1]
            pos //= 2

    def query(self, l, r):
        res = 0
        l += self.n; r += self.n + 1
        while l < r:
            if l & 1:
                res += self.t[l]; l += 1
            if r & 1:
                r -= 1; res += self.t[r]
            l //= 2; r //= 2
        return res


# ---------------------------------------------------------------------------
# Heavy-Light Decomposition
# ---------------------------------------------------------------------------

class HLD:
    """
    Heavy-Light Decomposition over a rooted tree.
    Node values supported via 'values' constructor arg.
    """

    def __init__(self, n, edges, values, root=0, mode="sum"):
        self.n = n
        self.adj = [[] for _ in range(n)]
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.parent = [-1] * n
        self.depth = [0] * n
        self.heavy = [-1] * n
        self.size = [1] * n
        self.head = [0] * n
        self.pos = [0] * n
        self.root = root
        self._values = values

        self._dfs_size(root, -1)
        self._cur_pos = 0
        self._dfs_hld(root, root)

        ordered = [0] * n
        for v in range(n):
            ordered[self.pos[v]] = values[v]

        self.mode = mode
        if mode == "sum":
            self.seg = SegTreeSum(n)
        else:
            self.seg = SegTreeMax(n)
        self.seg.build(ordered)

    # ----- build (recursive; could be iterative) -----
    def _dfs_size(self, u, par):
        self.parent[u] = par
        max_sub = 0
        for v in self.adj[u]:
            if v == par:
                continue
            self.depth[v] = self.depth[u] + 1
            self._dfs_size(v, u)
            self.size[u] += self.size[v]
            if self.size[v] > max_sub:
                max_sub = self.size[v]
                self.heavy[u] = v

    def _dfs_hld(self, u, h):
        self.head[u] = h
        self.pos[u] = self._cur_pos
        self._cur_pos += 1
        if self.heavy[u] != -1:
            self._dfs_hld(self.heavy[u], h)
        for v in self.adj[u]:
            if v == self.parent[u] or v == self.heavy[u]:
                continue
            self._dfs_hld(v, v)

    # ----- operations -----
    def update_node(self, v, new_val):
        self._values[v] = new_val
        self.seg.update(self.pos[v], new_val)

    def _combine(self, a, b):
        if self.mode == "sum":
            return a + b
        return max(a, b)

    def path_query(self, u, v):
        """Combine all node values on path u..v."""
        if self.mode == "sum":
            result = 0
        else:
            result = SegTreeMax.NEG_INF
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            # query segment [pos[head[u]] .. pos[u]]
            chunk = self.seg.query(self.pos[self.head[u]], self.pos[u])
            result = self._combine(result, chunk)
            u = self.parent[self.head[u]]
        if self.pos[u] > self.pos[v]:
            u, v = v, u
        result = self._combine(result, self.seg.query(self.pos[u], self.pos[v]))
        return result

    def lca(self, u, v):
        """LCA via HLD."""
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            u = self.parent[self.head[u]]
        return u if self.depth[u] < self.depth[v] else v


# ---------------------------------------------------------------------------
# Brute force reference for verification
# ---------------------------------------------------------------------------

def path_brute(n, edges, values, u, v, mode):
    """Recompute path query by walking parent chain — O(N)."""
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b); adj[b].append(a)
    par = [-1] * n
    depth = [0] * n
    # BFS from root=0
    from collections import deque
    visited = [False] * n
    visited[0] = True
    q = deque([0])
    while q:
        x = q.popleft()
        for y in adj[x]:
            if not visited[y]:
                visited[y] = True
                par[y] = x
                depth[y] = depth[x] + 1
                q.append(y)

    # Walk up from both to LCA, collect nodes
    nodes = set()
    a, b = u, v
    while a != b:
        if depth[a] < depth[b]:
            a, b = b, a
        nodes.add(a)
        a = par[a]
    nodes.add(a)
    nodes.update([u, v])
    if mode == "sum":
        return sum(values[x] for x in nodes)
    return max(values[x] for x in nodes)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: HLD on a 9-node tree")
    print("=" * 60)
    #         0
    #       / | \
    #      1  2  3
    #     /\     \
    #    4  5     6
    #   /\
    #  7  8
    edges = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 5),
             (3, 6), (4, 7), (4, 8)]
    values = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    hld = HLD(9, edges, values, root=0, mode="sum")

    print(f"  Parent: {hld.parent}")
    print(f"  Depth:  {hld.depth}")
    print(f"  Heavy:  {hld.heavy}")
    print(f"  Head:   {hld.head}")
    print(f"  Pos:    {hld.pos}")

    print(f"\n  Path sum 7->6: {hld.path_query(7, 6)} "
          f"(brute: {path_brute(9, edges, values, 7, 6, 'sum')})")
    print(f"  Path sum 8->5: {hld.path_query(8, 5)} "
          f"(brute: {path_brute(9, edges, values, 8, 5, 'sum')})")
    print(f"  LCA(7, 6) = {hld.lca(7, 6)} (expected 0)")
    print(f"  LCA(7, 8) = {hld.lca(7, 8)} (expected 4)")


def demo_max_and_update():
    print("\n" + "=" * 60)
    print("DEMO 2: HLD with max + point update")
    print("=" * 60)
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
    values = [5, 3, 7, 2, 8, 1]
    hld = HLD(6, edges, values, root=0, mode="max")
    print(f"  values: {values}")
    print(f"  Max on path 4->5: {hld.path_query(4, 5)} "
          f"(brute: {path_brute(6, edges, values, 4, 5, 'max')})")
    hld.update_node(0, 100)
    values[0] = 100
    print(f"  After set values[0]=100")
    print(f"  Max on path 4->5: {hld.path_query(4, 5)} "
          f"(brute: {path_brute(6, edges, values, 4, 5, 'max')})")


def demo_random_verify():
    print("\n" + "=" * 60)
    print("DEMO 3: Random verification vs brute force")
    print("=" * 60)
    import random
    random.seed(7)
    n = 30
    edges = [(i, random.randint(0, i - 1)) for i in range(1, n)]
    values = [random.randint(1, 100) for _ in range(n)]
    hld = HLD(n, edges, values, mode="sum")
    ok = True
    for _ in range(100):
        u, v = random.randint(0, n-1), random.randint(0, n-1)
        a = hld.path_query(u, v)
        b = path_brute(n, edges, values, u, v, "sum")
        if a != b:
            ok = False
            print(f"  MISMATCH u={u} v={v} hld={a} brute={b}")
    print(f"  100 random queries on n={n} tree: {'ALL MATCH' if ok else 'FAILURES'}")


if __name__ == "__main__":
    demo_basic()
    demo_max_and_update()
    demo_random_verify()
