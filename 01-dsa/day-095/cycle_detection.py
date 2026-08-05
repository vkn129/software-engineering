"""
Day 95: Cycle Detection — Directed & Undirected

Linear-time algorithms:
  - Undirected: DFS with parent tracking, or Union-Find.
  - Directed:   DFS with 3-coloring (WHITE/GRAY/BLACK).

Failure modes covered: self-loops, multi-edges, disconnected graphs.

Real-world angle: deadlock detection in PostgreSQL-style wait-for graphs.
"""

from collections import defaultdict
import sys

sys.setrecursionlimit(10**6)

WHITE, GRAY, BLACK = 0, 1, 2


# ---------------------------------------------------------------------------
# 1. Undirected — DFS with edge-id (handles multi-edges)
# ---------------------------------------------------------------------------

def has_cycle_undirected_dfs(n, edges):
    """
    Returns True iff the undirected (multi)graph has a cycle.
    Each edge is identified by its index so parallel edges count as cycles.
    Self-loops count as cycles.
    """
    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        if u == v:
            return True  # self-loop is a 1-cycle
        adj[u].append((v, i))
        adj[v].append((u, i))

    visited = [False] * n

    def dfs(u, parent_edge):
        visited[u] = True
        for v, eid in adj[u]:
            if eid == parent_edge:
                continue
            if visited[v]:
                return True
            if dfs(v, eid):
                return True
        return False

    for start in range(n):
        if not visited[start]:
            if dfs(start, -1):
                return True
    return False


# ---------------------------------------------------------------------------
# 2. Undirected — Union-Find
# ===========================================================================

class _UF:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        return True


def has_cycle_undirected_uf(n, edges):
    """Same as has_cycle_undirected_dfs but using Union-Find."""
    uf = _UF(n)
    for u, v in edges:
        if u == v:
            return True
        if not uf.union(u, v):
            return True
    return False


# ---------------------------------------------------------------------------
# 3. Directed — 3-color DFS
# ---------------------------------------------------------------------------

def has_cycle_directed(n, edges):
    """
    Returns True iff the directed graph contains a cycle.
    Self-loops are cycles. Uses iterative DFS to avoid recursion limits.
    """
    adj = defaultdict(list)
    for u, v in edges:
        if u == v:
            return True
        adj[u].append(v)

    color = [WHITE] * n

    # Iterative DFS with an explicit "exit" marker
    for start in range(n):
        if color[start] != WHITE:
            continue
        stack = [(start, iter(adj[start]))]
        color[start] = GRAY
        while stack:
            u, it = stack[-1]
            v = next(it, None)
            if v is None:
                color[u] = BLACK
                stack.pop()
                continue
            if color[v] == GRAY:
                return True
            if color[v] == WHITE:
                color[v] = GRAY
                stack.append((v, iter(adj[v])))
    return False


def find_cycle_directed(n, edges):
    """
    If a cycle exists, return the vertex list along it
    (e.g. [3, 5, 2, 3] means 3 -> 5 -> 2 -> 3). Else return None.

    Recursive variant to keep the parent map straightforward.
    """
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)

    color = [WHITE] * n
    parent = [-1] * n
    cycle = []

    def dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                # Reconstruct cycle: v ... u -> v
                cur = u
                cycle.append(v)
                while cur != v:
                    cycle.append(cur)
                    cur = parent[cur]
                cycle.append(v)
                cycle.reverse()
                return True
            if color[v] == WHITE:
                parent[v] = u
                if dfs(v):
                    return True
        color[u] = BLACK
        return False

    for start in range(n):
        if color[start] == WHITE:
            if dfs(start):
                return cycle
    return None


# ---------------------------------------------------------------------------
# 4. Deadlock detection — wait-for graph
# ---------------------------------------------------------------------------

def detect_deadlock(transactions, locks_held, waits_for):
    """
    Build wait-for graph from current state and check for a cycle.

    transactions: list of transaction ids (just for labels)
    locks_held:   dict {tx_id: resource_id}
    waits_for:    dict {tx_id: resource_id} — what tx is *blocked on*

    Edge T -> T' iff T waits for a resource held by T'.
    Returns the list of transactions in the deadlock cycle, or None.
    """
    # Map resource_id -> tx that holds it
    holder = {res: tx for tx, res in locks_held.items()}

    # Index transactions
    idx = {tx: i for i, tx in enumerate(transactions)}
    n = len(transactions)
    edges = []
    for tx, res in waits_for.items():
        if res in holder and holder[res] != tx:
            edges.append((idx[tx], idx[holder[res]]))

    cyc = find_cycle_directed(n, edges)
    if cyc is None:
        return None
    return [transactions[i] for i in cyc]


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_undirected():
    print("=" * 65)
    print("DEMO 1: Undirected Cycle Detection")
    print("=" * 65)
    # Tree (no cycle)
    edges = [(0, 1), (1, 2), (1, 3)]
    print(f"  Tree [(0,1),(1,2),(1,3)]:")
    print(f"    DFS: {has_cycle_undirected_dfs(4, edges)}  UF: {has_cycle_undirected_uf(4, edges)}")
    # Triangle (cycle)
    edges = [(0, 1), (1, 2), (2, 0)]
    print(f"  Triangle:")
    print(f"    DFS: {has_cycle_undirected_dfs(3, edges)}  UF: {has_cycle_undirected_uf(3, edges)}")
    # Self-loop
    edges = [(0, 0)]
    print(f"  Self-loop on 0:")
    print(f"    DFS: {has_cycle_undirected_dfs(1, edges)}")


def demo_directed():
    print("\n" + "=" * 65)
    print("DEMO 2: Directed Cycle Detection (3-Coloring DFS)")
    print("=" * 65)
    # DAG (no cycle)
    edges = [(0, 1), (1, 2), (0, 2)]
    print(f"  DAG [(0,1),(1,2),(0,2)]:  cycle? {has_cycle_directed(3, edges)}")
    # Cycle
    edges = [(0, 1), (1, 2), (2, 0)]
    print(f"  Cycle [(0,1),(1,2),(2,0)]:  cycle? {has_cycle_directed(3, edges)}")
    print(f"  Cycle path: {find_cycle_directed(3, edges)}")
    # 'Y'-shaped DAG: same vertex visited from two parents, no cycle
    edges = [(0, 2), (1, 2)]
    print(f"  Y-shape [(0,2),(1,2)]:  cycle? {has_cycle_directed(3, edges)}  "
          f"(visited != cycle for directed)")


def demo_deadlock():
    print("\n" + "=" * 65)
    print("DEMO 3: Database Deadlock Detection (Wait-For Graph)")
    print("=" * 65)
    transactions = ["T1", "T2", "T3"]
    locks_held = {"T1": "R1", "T2": "R2", "T3": "R3"}
    waits_for = {"T1": "R2", "T2": "R3", "T3": "R1"}
    print("  T1 holds R1, waits for R2")
    print("  T2 holds R2, waits for R3")
    print("  T3 holds R3, waits for R1")
    cycle = detect_deadlock(transactions, locks_held, waits_for)
    print(f"  Deadlock cycle: {cycle}")
    print(f"  -> PostgreSQL would abort the youngest victim in this cycle.")

    print("\n  Same setup but T3 releases R3 (no wait):")
    waits_for2 = {"T1": "R2", "T2": "R3"}
    cycle = detect_deadlock(transactions, locks_held, waits_for2)
    print(f"  Deadlock cycle: {cycle}  (no deadlock)")


def demo_edge_classification():
    print("\n" + "=" * 65)
    print("DEMO 4: Edge Classification via 3-Coloring")
    print("=" * 65)
    # Classic CLRS example
    edges = [(0, 1), (0, 3), (1, 2), (2, 0), (3, 2)]
    # 0 -> 1, 0 -> 3
    # 1 -> 2
    # 2 -> 0  (back-edge -> cycle)
    # 3 -> 2  (cross-edge once 2 is BLACK)
    print(f"  Edges: {edges}")
    print(f"  Has cycle: {has_cycle_directed(4, edges)}")
    print("  Edge (2,0) is the back-edge closing the cycle 0->1->2->0.")


if __name__ == "__main__":
    demo_undirected()
    demo_directed()
    demo_deadlock()
    demo_edge_classification()
