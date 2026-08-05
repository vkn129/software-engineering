"""
Day 92: Hopcroft-Karp Bipartite Matching — From Scratch

O(E * sqrt(V)) maximum bipartite matching via phased BFS + DFS.

Compare to Day 89's basic O(V * E) augmenting-path matching:
this finds *many* vertex-disjoint shortest augmenting paths per phase.
"""

from collections import defaultdict, deque
import sys
import time
import random

sys.setrecursionlimit(10**6)

INF = float("inf")
NIL = -1  # sentinel for "unmatched"


# ---------------------------------------------------------------------------
# 1. Hopcroft-Karp core
# ---------------------------------------------------------------------------

class HopcroftKarp:
    """
    Bipartite graph with left vertices [0..nL) and right vertices [0..nR).
    edges: list of (u, v) with u in left, v in right.

    pair_L[u] = matched right vertex, or NIL
    pair_R[v] = matched left vertex, or NIL
    dist[u]   = BFS layer of left vertex u (INF if unreachable this phase)
    """

    def __init__(self, nL, nR, edges):
        self.nL = nL
        self.nR = nR
        self.adj = defaultdict(list)
        for u, v in edges:
            self.adj[u].append(v)
        self.pair_L = [NIL] * nL
        self.pair_R = [NIL] * nR
        self.dist = [INF] * nL

    def _bfs(self):
        """
        Layer left vertices by alternating-path distance from unmatched ones.
        Returns True iff an augmenting path exists (reaches an unmatched R).
        """
        q = deque()
        for u in range(self.nL):
            if self.pair_L[u] == NIL:
                self.dist[u] = 0
                q.append(u)
            else:
                self.dist[u] = INF

        found = False
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                pair = self.pair_R[v]
                if pair == NIL:
                    # Reached an unmatched right vertex -> augmenting path exists
                    found = True
                elif self.dist[pair] == INF:
                    self.dist[pair] = self.dist[u] + 1
                    q.append(pair)
        return found

    def _dfs(self, u):
        """
        Try to extend an augmenting path from left vertex u along the BFS
        layering. Augments and returns True on success.
        """
        for v in self.adj[u]:
            pair = self.pair_R[v]
            # Follow only edges that go to next BFS layer (or to unmatched R)
            if pair == NIL or (self.dist[pair] == self.dist[u] + 1 and self._dfs(pair)):
                self.pair_L[u] = v
                self.pair_R[v] = u
                return True
        # Mark this node dead for this phase so other DFS calls skip it
        self.dist[u] = INF
        return False

    def max_matching(self):
        matching = 0
        while self._bfs():
            for u in range(self.nL):
                if self.pair_L[u] == NIL:
                    if self._dfs(u):
                        matching += 1
        return matching

    def matched_pairs(self):
        return [(u, self.pair_L[u]) for u in range(self.nL) if self.pair_L[u] != NIL]


# ---------------------------------------------------------------------------
# 2. Basic augmenting-path matching (Day 89 style) for benchmark
# ---------------------------------------------------------------------------

def basic_bipartite_matching(nL, nR, edges):
    """Standard O(V*E) Kuhn's algorithm — one augmenting path at a time."""
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    pair_R = [NIL] * nR

    def try_augment(u, visited):
        for v in adj[u]:
            if visited[v]:
                continue
            visited[v] = True
            if pair_R[v] == NIL or try_augment(pair_R[v], visited):
                pair_R[v] = u
                return True
        return False

    matching = 0
    for u in range(nL):
        visited = [False] * nR
        if try_augment(u, visited):
            matching += 1
    return matching


# ---------------------------------------------------------------------------
# 3. Helpers / problem encoders
# ---------------------------------------------------------------------------

def random_bipartite(nL, nR, p, seed=0):
    """Erdos-Renyi-style random bipartite graph; each edge with prob p."""
    rng = random.Random(seed)
    edges = []
    for u in range(nL):
        for v in range(nR):
            if rng.random() < p:
                edges.append((u, v))
    return edges


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Small bipartite example")
    print("=" * 60)
    # Left = 4 workers (0..3); Right = 4 jobs (0..3)
    edges = [(0, 0), (0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 3)]
    hk = HopcroftKarp(4, 4, edges)
    print(f"  Max matching: {hk.max_matching()}")
    print(f"  Pairs: {hk.matched_pairs()}")


def demo_perfect_vs_imperfect():
    print("\n" + "=" * 60)
    print("DEMO 2: Perfect vs imperfect matching")
    print("=" * 60)

    # Hall's condition violated: left = 3, right = 2
    edges = [(0, 0), (1, 0), (2, 1)]
    hk = HopcroftKarp(3, 2, edges)
    m = hk.max_matching()
    print(f"  3 workers, 2 jobs: max = {m} (not perfect; 1 worker idle)")

    # Perfect matching exists
    edges = [(0, 0), (1, 1), (2, 2)]
    hk = HopcroftKarp(3, 3, edges)
    m = hk.max_matching()
    print(f"  3-3 identity edges: max = {m} (perfect)")


def demo_benchmark():
    print("\n" + "=" * 60)
    print("DEMO 3: Hopcroft-Karp vs Basic Kuhn — speed")
    print("=" * 60)

    for nL, p in [(100, 0.1), (300, 0.05), (500, 0.03), (1000, 0.02)]:
        nR = nL
        edges = random_bipartite(nL, nR, p, seed=42)

        t = time.perf_counter()
        m1 = basic_bipartite_matching(nL, nR, edges)
        t_basic = time.perf_counter() - t

        t = time.perf_counter()
        m2 = HopcroftKarp(nL, nR, edges).max_matching()
        t_hk = time.perf_counter() - t

        assert m1 == m2, f"Mismatch: basic={m1}, hk={m2}"
        speedup = t_basic / t_hk if t_hk > 0 else float("inf")
        print(f"  n={nL:5d} p={p:.3f} |E|={len(edges):6d}  "
              f"basic={t_basic:.4f}s  hk={t_hk:.4f}s  speedup={speedup:.2f}x")


def demo_use_case_scheduling():
    print("\n" + "=" * 60)
    print("DEMO 4: Application — driver-to-rider dispatch")
    print("=" * 60)
    # 5 drivers, 5 riders; each driver can serve only nearby riders.
    nearby = {
        0: [0, 1, 4],
        1: [0, 2],
        2: [1, 2, 3],
        3: [3, 4],
        4: [2, 4],
    }
    edges = [(d, r) for d, rs in nearby.items() for r in rs]
    hk = HopcroftKarp(5, 5, edges)
    m = hk.max_matching()
    print(f"  Max simultaneous trips: {m}")
    for d, r in hk.matched_pairs():
        print(f"    Driver {d} -> Rider {r}")


if __name__ == "__main__":
    demo_basic()
    demo_perfect_vs_imperfect()
    demo_benchmark()
    demo_use_case_scheduling()
