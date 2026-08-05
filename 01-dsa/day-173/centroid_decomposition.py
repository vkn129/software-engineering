"""
Day 173: Centroid Decomposition — From Scratch

Build the centroid tree of an undirected tree, then use it to answer:
  - count pairs at distance exactly K
  - sum of all pairwise distances
  - closest-marked-node queries

Time: O(N log N) for the decomposition; queries vary by problem.
Builds on Day 80 (DFS) for subtree sizes.
"""

import sys
sys.setrecursionlimit(10**6)
from collections import defaultdict


# ---------------------------------------------------------------------------
# Centroid tree
# ---------------------------------------------------------------------------

class CentroidTree:
    """Centroid decomposition of an unweighted undirected tree."""

    def __init__(self, n, edges):
        self.n = n
        self.adj = [[] for _ in range(n)]
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.removed = [False] * n
        self.size = [0] * n
        self.parent_ct = [-1] * n   # parent in centroid tree
        self.depth_ct = [0] * n     # depth in centroid tree
        self._build(0, -1, 0)

    def _calc_size(self, u, par):
        self.size[u] = 1
        for v in self.adj[u]:
            if v == par or self.removed[v]:
                continue
            self._calc_size(v, u)
            self.size[u] += self.size[v]

    def _find_centroid(self, u, par, tree_size):
        for v in self.adj[u]:
            if v == par or self.removed[v]:
                continue
            if self.size[v] > tree_size // 2:
                return self._find_centroid(v, u, tree_size)
        return u

    def _build(self, u, ct_par, depth):
        self._calc_size(u, -1)
        c = self._find_centroid(u, -1, self.size[u])
        self.parent_ct[c] = ct_par
        self.depth_ct[c] = depth
        self.removed[c] = True
        for v in self.adj[c]:
            if not self.removed[v]:
                self._build(v, c, depth + 1)


# ---------------------------------------------------------------------------
# Count pairs at distance exactly K
# ---------------------------------------------------------------------------

def count_pairs_at_distance(n, edges, k):
    """
    Count unordered pairs (u, v), u != v, with shortest distance == k.
    Uses centroid decomposition for O(N log N).
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    removed = [False] * n
    size = [0] * n

    def calc_size(u, par):
        size[u] = 1
        for v in adj[u]:
            if v != par and not removed[v]:
                calc_size(v, u)
                size[u] += size[v]

    def find_c(u, par, ts):
        for v in adj[u]:
            if v != par and not removed[v] and size[v] > ts // 2:
                return find_c(v, u, ts)
        return u

    def collect_depths(u, par, d, bucket):
        if d > k:
            return
        bucket[d] += 1
        for v in adj[u]:
            if v != par and not removed[v]:
                collect_depths(v, u, d + 1, bucket)

    count = [0]

    def solve(start):
        calc_size(start, -1)
        c = find_c(start, -1, size[start])

        # Combined bucket = all depths from c (including c itself at depth 0)
        combined = defaultdict(int)
        combined[0] = 1
        for v in adj[c]:
            if removed[v]:
                continue
            sub = defaultdict(int)
            collect_depths(v, c, 1, sub)
            # Count pairs across centroid: subtract same-subtree pairs
            for d, cnt in sub.items():
                need = k - d
                if need in combined and need >= 0:
                    count[0] += cnt * combined[need]
            for d, cnt in sub.items():
                combined[d] += cnt

        removed[c] = True
        for v in adj[c]:
            if not removed[v]:
                solve(v)

    solve(0)
    return count[0]


# ---------------------------------------------------------------------------
# Sum of all pairwise distances (using centroid decomposition pattern)
# ---------------------------------------------------------------------------

def sum_all_pair_distances(n, edges):
    """
    Sum of dist(u, v) for all unordered pairs.
    O(N log N) using centroid decomposition.
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
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

    def collect(u, par, d, depths):
        depths.append(d)
        for v in adj[u]:
            if v != par and not removed[v]:
                collect(v, u, d + 1, depths)

    total = [0]

    def solve(start):
        calc_size(start, -1)
        c = find_c(start, -1, size[start])

        # All depths from c (including c at depth 0)
        all_depths = [0]
        subtree_depths_list = []
        for v in adj[c]:
            if removed[v]:
                continue
            sub = []
            collect(v, c, 1, sub)
            subtree_depths_list.append(sub)
            all_depths.extend(sub)

        # For every pair across centroid, distance = d_i + d_j.
        # Subtract same-subtree pairs.
        def pair_sum(depths):
            # sum over i<j of d_i + d_j = (len-1) * sum(d)
            return (len(depths) - 1) * sum(depths)

        total[0] += pair_sum(all_depths)
        for sub in subtree_depths_list:
            total[0] -= pair_sum(sub)
        # Each unordered pair was counted twice (i<j and j<i contributions).
        # Actually we computed sum_{i<j}(d_i + d_j) so no factor.

        removed[c] = True
        for v in adj[c]:
            if not removed[v]:
                solve(v)

    solve(0)
    return total[0]


def sum_all_pair_distances_brute(n, edges):
    """Reference O(N^2) using BFS from each node."""
    from collections import deque
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
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


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_centroid_tree():
    print("=" * 60)
    print("DEMO 1: Centroid Decomposition of a tree")
    print("=" * 60)
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]  # path of 7
    ct = CentroidTree(7, edges)
    print(f"  Path 0-1-2-3-4-5-6")
    print(f"  Centroid parents: {ct.parent_ct}")
    print(f"  Centroid depths:  {ct.depth_ct}")
    print(f"  Expected root: 3 (middle of path)")


def demo_count_pairs():
    print("\n" + "=" * 60)
    print("DEMO 2: Count pairs at distance K")
    print("=" * 60)
    #       0
    #      / \
    #     1   2
    #    / \   \
    #   3   4   5
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
    for k in range(1, 6):
        c = count_pairs_at_distance(6, edges, k)
        print(f"  k={k}: {c} pairs")


def demo_sum_distances():
    print("\n" + "=" * 60)
    print("DEMO 3: Sum of all pairwise distances")
    print("=" * 60)
    import random
    random.seed(42)
    for n in [5, 10, 20, 50]:
        edges = [(i, random.randint(0, i - 1)) for i in range(1, n)]
        a = sum_all_pair_distances(n, edges)
        b = sum_all_pair_distances_brute(n, edges)
        print(f"  n={n}: centroid={a}, brute={b}, match={a == b}")


if __name__ == "__main__":
    demo_centroid_tree()
    demo_count_pairs()
    demo_sum_distances()
