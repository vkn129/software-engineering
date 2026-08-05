"""
Day 97 Practice: Min-Cost Max-Flow

6 exercises. Implement the TODOs, then run: python3 practice.py

Graphs arrive as `n` (node count) plus a list of (u, v, capacity, cost) tuples.
"""

import heapq
from itertools import permutations

INF = float("inf")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Shared internal engine (used by the reference solutions)
# ---------------------------------------------------------------------------

class _MCMF:
    """Residual graph with paired edges: the reverse of edge i is edge i ^ 1."""

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]
        self.edges = []

    def add_edge(self, u, v, cap, cost):
        idx = len(self.edges)
        self.adj[u].append(idx)
        self.edges.append([v, cap, cost])
        self.adj[v].append(idx + 1)
        self.edges.append([u, 0, -cost])
        return idx

    def flow_on(self, idx):
        return self.edges[idx ^ 1][1]

    def potentials(self, source):
        pot = [INF] * self.n
        pot[source] = 0
        for _ in range(self.n - 1):
            changed = False
            for idx in range(0, len(self.edges), 2):
                v, cap, cost = self.edges[idx]
                if cap <= 0:
                    continue
                u = self.edges[idx ^ 1][0]
                if pot[u] < INF and pot[u] + cost < pot[v]:
                    pot[v] = pot[u] + cost
                    changed = True
            if not changed:
                break
        return pot

    def run(self, source, sink, limit=INF):
        pot = self.potentials(source)
        flow = cost_total = 0
        while flow < limit:
            dist = [INF] * self.n
            prev = [-1] * self.n
            dist[source] = 0
            pq = [(0, source)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u] or pot[u] == INF:
                    continue
                for idx in self.adj[u]:
                    v, cap, c = self.edges[idx]
                    if cap <= 0 or pot[v] == INF:
                        continue
                    nd = d + c + pot[u] - pot[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = idx
                        heapq.heappush(pq, (nd, v))
            if dist[sink] == INF:
                break
            for v in range(self.n):
                if dist[v] < INF and pot[v] < INF:
                    pot[v] += dist[v]
            push = limit - flow
            v = sink
            while v != source:
                idx = prev[v]
                push = min(push, self.edges[idx][1])
                v = self.edges[idx ^ 1][0]
            v = sink
            path_cost = 0
            while v != source:
                idx = prev[v]
                self.edges[idx][1] -= push
                self.edges[idx ^ 1][1] += push
                path_cost += self.edges[idx][2]
                v = self.edges[idx ^ 1][0]
            flow += push
            cost_total += push * path_cost
        return flow, cost_total


def _build(n, edges):
    g = _MCMF(n)
    for u, v, cap, cost in edges:
        g.add_edge(u, v, cap, cost)
    return g


# ---------------------------------------------------------------------------
# Exercise 1: Bellman-Ford potentials
# ---------------------------------------------------------------------------

def bellman_ford_potentials(n, edges, source):
    """
    Return a list `pot` of length n where pot[v] is the cheapest cost of any
    source->v path using only edges with capacity > 0. Unreachable nodes get
    float('inf').

    Costs may be NEGATIVE, which is exactly why this is Bellman-Ford and not
    Dijkstra.
    """
    # TODO: relax every edge n-1 times; stop early if a pass changes nothing
    pass


def _sol_bellman_ford_potentials(n, edges, source):
    pot = [INF] * n
    pot[source] = 0
    for _ in range(n - 1):
        changed = False
        for u, v, cap, cost in edges:
            if cap <= 0:
                continue
            if pot[u] < INF and pot[u] + cost < pot[v]:
                pot[v] = pot[u] + cost
                changed = True
        # Early exit is not only a speed-up: it distinguishes "settled" from
        # "still improving", which is the negative-cycle signal.
        if not changed:
            break
    return pot


# ---------------------------------------------------------------------------
# Exercise 2: reduced costs are non-negative
# ---------------------------------------------------------------------------

def reduced_costs_nonnegative(n, edges, pot):
    """
    Return True iff  cost + pot[u] - pot[v] >= 0  for every edge with capacity
    > 0 and both endpoints reachable (finite potential).

    This is the property that licenses Dijkstra. If it fails, the potentials are
    wrong and every shortest-path answer after that is garbage.
    """
    # TODO: check the reduced cost of each usable edge
    pass


def _sol_reduced_costs_nonnegative(n, edges, pot):
    for u, v, cap, cost in edges:
        if cap <= 0 or pot[u] == INF or pot[v] == INF:
            continue
        if cost + pot[u] - pot[v] < 0:
            return False
    return True


# ---------------------------------------------------------------------------
# Exercise 3: min-cost MAX-flow
# ---------------------------------------------------------------------------

def min_cost_max_flow(n, edges, source, sink):
    """
    Return (max_flow, min_cost_of_that_flow).

    Repeatedly augment along the cheapest source->sink path in the residual
    graph. Stop when the sink is unreachable — the same termination condition
    as plain max-flow.
    """
    # TODO: build the residual graph, then loop: Dijkstra on reduced costs,
    # reprice potentials, find the bottleneck, push it.
    pass


def _sol_min_cost_max_flow(n, edges, source, sink):
    return _build(n, edges).run(source, sink)


# ---------------------------------------------------------------------------
# Exercise 4: min-cost flow of a bounded value
# ---------------------------------------------------------------------------

def min_cost_flow_bounded(n, edges, source, sink, limit):
    """
    Push at most `limit` units. Return (flow_sent, cost).

    `flow_sent < limit` means the network cannot carry more — report it, do not
    pretend the target was met.
    """
    # TODO: same loop as exercise 3, but stop once `limit` units are sent
    pass


def _sol_min_cost_flow_bounded(n, edges, source, sink, limit):
    return _build(n, edges).run(source, sink, limit)


# ---------------------------------------------------------------------------
# Exercise 5: assignment problem via MCMF
# ---------------------------------------------------------------------------

def assignment_cost(matrix):
    """
    Minimum-cost perfect assignment of n workers to n jobs, solved as a
    unit-capacity bipartite min-cost max-flow. Return the total cost.

    This is precisely the graph day 96's Hungarian algorithm solves directly.
    """
    # TODO: source -> worker (cap 1, cost 0), worker -> job (cap 1, cost C[i][j]),
    #       job -> sink (cap 1, cost 0); then min-cost max-flow.
    pass


def _sol_assignment_cost(matrix):
    n = len(matrix)
    if n == 0:
        return 0
    m = len(matrix[0])
    src, snk = n + m, n + m + 1
    g = _MCMF(n + m + 2)
    for i in range(n):
        g.add_edge(src, i, 1, 0)
    for j in range(m):
        g.add_edge(n + j, snk, 1, 0)
    for i in range(n):
        for j in range(m):
            # Capacity 1 is what forces "one job per worker". Raise it and the
            # answer stops being a matching.
            g.add_edge(i, n + j, 1, matrix[i][j])
    _, cost = g.run(src, snk)
    return cost


def _brute_assignment(matrix):
    n = len(matrix)
    m = len(matrix[0]) if matrix else 0
    best = INF
    for perm in permutations(range(m), n):
        best = min(best, sum(matrix[i][perm[i]] for i in range(n)))
    return best


# ---------------------------------------------------------------------------
# Exercise 6: transportation problem
# ---------------------------------------------------------------------------

def transportation_cost(supply, demand, cost):
    """
    Warehouses hold `supply[i]` units, stores need `demand[j]` units, shipping
    costs `cost[i][j]` per unit. Ship every unit of demand as cheaply as
    possible.

    Return (total_cost, True) if all demand can be met, else (None, False).
    Unlike assignment, one warehouse may serve many stores — the only thing
    that changes is the capacities.
    """
    # TODO: source -> warehouse (cap supply[i]), warehouse -> store
    #       (cap large, cost[i][j]), store -> sink (cap demand[j]).
    #       Feasible iff the flow reaches sum(demand).
    pass


def _sol_transportation_cost(supply, demand, cost):
    n, m = len(supply), len(demand)
    need = sum(demand)
    src, snk = n + m, n + m + 1
    g = _MCMF(n + m + 2)
    for i in range(n):
        g.add_edge(src, i, supply[i], 0)
    for j in range(m):
        g.add_edge(n + j, snk, demand[j], 0)
    big = sum(supply) or 1   # a lane is never the binding constraint here
    for i in range(n):
        for j in range(m):
            g.add_edge(i, n + j, big, cost[i][j])
    sent, total = g.run(src, snk, need)
    if sent < need:
        return None, False
    return total, True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    # s=0, a=1, b=2, t=3
    diamond = [(0, 1, 2, 1), (0, 2, 3, 4), (1, 3, 2, 1), (2, 3, 3, 1)]

    print("Exercise 1: bellman_ford_potentials")
    check("simple diamond", try_or_sol("bellman_ford_potentials", 4, diamond, 0),
          [0, 1, 4, 2])
    neg = [(0, 1, 1, -5), (0, 2, 1, 2), (1, 3, 1, 1), (2, 3, 1, 1)]
    check("negative edge handled",
          try_or_sol("bellman_ford_potentials", 4, neg, 0), [0, -5, 2, -4])
    check("unreachable node is INF",
          try_or_sol("bellman_ford_potentials", 3, [(0, 1, 1, 5)], 0),
          [0, 5, INF])
    check("zero-capacity edge is not usable",
          try_or_sol("bellman_ford_potentials", 2, [(0, 1, 0, 5)], 0),
          [0, INF])

    print("\nExercise 2: reduced_costs_nonnegative")
    pot = _sol_bellman_ford_potentials(4, neg, 0)
    check("Bellman-Ford potentials are feasible",
          try_or_sol("reduced_costs_nonnegative", 4, neg, pot), True)
    check("all-zero potentials fail on a negative edge",
          try_or_sol("reduced_costs_nonnegative", 4, neg, [0, 0, 0, 0]), False)
    check("all-zero potentials fine when no cost is negative",
          try_or_sol("reduced_costs_nonnegative", 4, diamond, [0, 0, 0, 0]), True)

    print("\nExercise 3: min_cost_max_flow")
    check("diamond: 2 cheap + 3 dear",
          try_or_sol("min_cost_max_flow", 4, diamond, 0, 3), (5, 19))
    check("single edge",
          try_or_sol("min_cost_max_flow", 2, [(0, 1, 7, 3)], 0, 1), (7, 21))
    # No s-t path at all: must return, not hang.
    check("disconnected sink terminates",
          try_or_sol("min_cost_max_flow", 4, [(0, 1, 5, 1), (2, 3, 5, 1)], 0, 3),
          (0, 0))
    # Reverse edges matter here: the cheapest single path (0-1-2-3, cost 3) can
    # only carry 1 unit once the flow is maximal, so some of it must be undone.
    # Enumerating the three routes gives max flow 5 at cost 27 — a greedy
    # "saturate the cheapest path first" run gets a worse number.
    undo = [(0, 1, 3, 1), (0, 2, 3, 5), (1, 2, 2, 1), (1, 3, 2, 5), (2, 3, 3, 1)]
    flow, cost = try_or_sol("min_cost_max_flow", 4, undo, 0, 3)
    check("full capacity reached", flow, 5)
    check("cost is the optimum for that flow", cost, 27)

    print("\nExercise 4: min_cost_flow_bounded")
    check("cap at 2 takes the cheap route only",
          try_or_sol("min_cost_flow_bounded", 4, diamond, 0, 3, 2), (2, 4))
    check("cap above capacity returns what exists",
          try_or_sol("min_cost_flow_bounded", 4, diamond, 0, 3, 99), (5, 19))
    check("cap of 0 does nothing",
          try_or_sol("min_cost_flow_bounded", 4, diamond, 0, 3, 0), (0, 0))
    # Successive shortest paths sends cheap units first, so a partial flow can
    # never cost more than the full flow.
    f_small, c_small = try_or_sol("min_cost_flow_bounded", 4, diamond, 0, 3, 3)
    check("partial flow costs no more than the full flow",
          f_small == 3 and c_small <= 19, True)

    print("\nExercise 5: assignment_cost")
    m1 = [[4, 1, 3], [2, 0, 5], [3, 2, 2]]
    check("3x3 matches brute force",
          try_or_sol("assignment_cost", m1), _brute_assignment(m1))
    m2 = [[7, 5, 11], [9, 14, 10], [13, 2, 4]]
    check("another 3x3 matches brute force",
          try_or_sol("assignment_cost", m2), _brute_assignment(m2))
    check("2x2", try_or_sol("assignment_cost", [[1, 2], [4, 3]]), 4)
    check("1x1", try_or_sol("assignment_cost", [[9]]), 9)
    # Diagonal is obviously optimal; a greedy impl grabs a cheap off-diagonal.
    m3 = [[1, 100, 100], [100, 1, 100], [100, 100, 1]]
    check("forced diagonal", try_or_sol("assignment_cost", m3), 3)

    print("\nExercise 6: transportation_cost")
    # 7 units w0->s0 (7) + 3 units w0->s1 (9) + 5 units w1->s1 (10) = 26.
    check("balanced supply/demand",
          try_or_sol("transportation_cost", [10, 5], [7, 8], [[1, 3], [4, 2]]),
          (26, True))
    check("supply short of demand is infeasible",
          try_or_sol("transportation_cost", [1], [5], [[2]]), (None, False))
    check("one warehouse serves many stores",
          try_or_sol("transportation_cost", [10], [3, 4], [[2, 5]]), (26, True))
    check("surplus supply is fine",
          try_or_sol("transportation_cost", [100, 100], [1, 1], [[1, 9], [9, 1]]),
          (2, True))

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
