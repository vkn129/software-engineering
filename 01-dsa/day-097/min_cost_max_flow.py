"""
Day 97: Min-Cost Max-Flow — successive shortest paths with Johnson potentials.

Day 90 asked "how much can I push?". Today asks "how much can I push, and what
does the cheapest way to push it look like?".

The method: repeatedly send flow along the CHEAPEST augmenting path (not the
fewest-hops one Edmonds-Karp uses). Because residual reverse edges carry
NEGATIVE cost, plain Dijkstra cannot be used directly. Johnson's potentials
reweight every edge to be non-negative without changing which path is cheapest,
so Dijkstra works after all — Bellman-Ford runs exactly once, to seed them.

Standard library only.
"""

import heapq
from itertools import permutations

INF = float("inf")


class NegativeCycleError(ValueError):
    """Raised when the input graph has a negative-cost cycle.

    Successive-shortest-paths assumes the zero flow is already optimal for its
    value. A negative cycle breaks that assumption: you could spin flow around
    the cycle forever and keep getting cheaper. Cycle-cancelling algorithms
    handle it; we refuse loudly rather than return a wrong number.
    """


class MinCostMaxFlow:
    """
    Min-cost max-flow over integer capacities and integer (possibly negative)
    costs.

    Edges live in one flat list; edge `i` and edge `i ^ 1` are a residual pair,
    so the reverse of any edge is one XOR away. Same trick day 90 used, with a
    cost field bolted on.
    """

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]   # node -> list of edge indices
        self.edges = []                     # flat [to, capacity, cost] triples

    # -- construction --------------------------------------------------------

    def add_edge(self, u, v, capacity, cost):
        """Add a directed edge u->v. Returns the forward edge's index."""
        if capacity < 0:
            raise ValueError("capacity must be non-negative")
        idx = len(self.edges)
        self.adj[u].append(idx)
        self.edges.append([v, capacity, cost])
        self.adj[v].append(idx + 1)
        # The reverse edge starts saturated (cap 0) and refunds the cost when
        # flow is pushed back along it — that refund is how the algorithm
        # un-commits an earlier, in-hindsight-wrong routing decision.
        self.edges.append([u, 0, -cost])
        return idx

    def flow_on(self, idx):
        """Flow carried by forward edge `idx` == its reverse edge's capacity."""
        return self.edges[idx ^ 1][1]

    # -- potentials ----------------------------------------------------------

    def _initial_potentials(self, source):
        """
        Bellman-Ford single-source shortest distances on the ORIGINAL graph.

        Why Bellman-Ford and not Dijkstra: input costs may be negative, and
        Dijkstra's "the closest unvisited node is final" argument collapses the
        moment a later edge can lower an already-settled distance. We pay
        O(V*E) once; every iteration after that is a Dijkstra.
        """
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
        else:
            # Reaching here means n-1 passes never settled. One more relaxing
            # pass that still improves something proves a path used >= n edges,
            # i.e. repeated a vertex: a negative cycle.
            for idx in range(0, len(self.edges), 2):
                v, cap, cost = self.edges[idx]
                if cap <= 0:
                    continue
                u = self.edges[idx ^ 1][0]
                if pot[u] < INF and pot[u] + cost < pot[v]:
                    raise NegativeCycleError(
                        "negative-cost cycle reachable from the source"
                    )
        # Unreachable nodes keep INF. They can never carry s-t flow, and the
        # reduced-cost formula below skips them rather than computing INF - INF.
        return pot

    # -- one cheapest-path search -------------------------------------------

    def _dijkstra(self, source, pot):
        """
        Dijkstra on REDUCED costs  w'(u,v) = w(u,v) + pot[u] - pot[v].

        Feasibility of `pot` (pot[v] <= pot[u] + w on every residual edge) makes
        every w' >= 0. And because the pot terms telescope along any s->v path,
        w'-shortest and w-shortest paths are the SAME paths — the reweighting
        changes the numbers, never the ranking.
        """
        dist = [INF] * self.n
        prev_edge = [-1] * self.n
        dist[source] = 0
        pq = [(0, source)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue          # stale heap entry
            if pot[u] == INF:
                continue
            for idx in self.adj[u]:
                v, cap, cost = self.edges[idx]
                if cap <= 0 or pot[v] == INF:
                    continue
                nd = d + cost + pot[u] - pot[v]
                if nd < dist[v]:
                    dist[v] = nd
                    prev_edge[v] = idx
                    heapq.heappush(pq, (nd, v))
        return dist, prev_edge

    # -- the main loop -------------------------------------------------------

    def min_cost_flow(self, source, sink, max_flow=INF):
        """
        Push at most `max_flow` units source->sink as cheaply as possible.

        Returns (flow_sent, total_cost). With the default `max_flow` this is
        min-cost MAX-flow; with a finite `max_flow` it is min-cost flow of a
        bounded value, and `flow_sent < max_flow` means the network simply
        cannot carry more.

        Terminates when the sink becomes unreachable in the residual graph —
        exactly the max-flow stopping condition, so this is Edmonds-Karp with
        "cheapest" swapped in for "fewest hops".
        """
        if source == sink:
            raise ValueError("source and sink must differ")
        pot = self._initial_potentials(source)
        total_flow = 0
        total_cost = 0

        while total_flow < max_flow:
            dist, prev_edge = self._dijkstra(source, pot)
            if dist[sink] == INF:
                break             # no augmenting path left: we are done

            # Fold this round's distances into the potentials so the next
            # Dijkstra again sees non-negative reduced costs.
            for v in range(self.n):
                if dist[v] < INF and pot[v] < INF:
                    pot[v] += dist[v]

            # Walk the path backwards once to find the bottleneck, once to apply.
            bottleneck = max_flow - total_flow
            v = sink
            while v != source:
                idx = prev_edge[v]
                bottleneck = min(bottleneck, self.edges[idx][1])
                v = self.edges[idx ^ 1][0]

            v = sink
            path_cost = 0
            while v != source:
                idx = prev_edge[v]
                self.edges[idx][1] -= bottleneck
                self.edges[idx ^ 1][1] += bottleneck
                path_cost += self.edges[idx][2]
                v = self.edges[idx ^ 1][0]

            total_flow += bottleneck
            total_cost += bottleneck * path_cost

        return total_flow, total_cost

    def min_cost_flow_exact(self, source, sink, required):
        """
        Send exactly `required` units, or report infeasibility.

        Returns (cost, True) or (None, False). Callers that silently accept a
        short flow ship wrong answers: an assignment leaving a job unstaffed is
        not a cheap assignment, it is a different problem.
        """
        sent, cost = self.min_cost_flow(source, sink, required)
        if sent < required:
            return None, False
        return cost, True


# ---------------------------------------------------------------------------
# The bipartite assignment special case
# ---------------------------------------------------------------------------

def assignment_via_mcmf(cost_matrix):
    """
    Solve the assignment problem by min-cost max-flow.

    Day 96's Hungarian algorithm is exactly this graph specialised: bipartite,
    every capacity 1, perfect matching demanded. Hungarian's dual variables
    u[i], v[j] ARE Johnson potentials, and its "tight edge"
    (u[i] + v[j] == C[i][j]) is a zero-reduced-cost edge here. Hungarian gets
    O(n^3) by exploiting that structure; MCMF is more general and pays for it.

    Returns (total_cost, assignment) with assignment[i] = j, or -1 if unmatched.
    """
    n = len(cost_matrix)
    if n == 0:
        return 0, []
    m = len(cost_matrix[0])
    source, sink = n + m, n + m + 1
    g = MinCostMaxFlow(n + m + 2)
    for i in range(n):
        g.add_edge(source, i, 1, 0)
    for j in range(m):
        g.add_edge(n + j, sink, 1, 0)
    worker_edges = []
    for i in range(n):
        worker_edges.append(
            [g.add_edge(i, n + j, 1, cost_matrix[i][j]) for j in range(m)]
        )

    _, total = g.min_cost_flow(source, sink)
    assignment = [-1] * n
    for i in range(n):
        for j in range(m):
            if g.flow_on(worker_edges[i][j]) > 0:
                assignment[i] = j
                break
    return total, assignment


def brute_force_assignment(cost_matrix):
    """O(n!) reference for small matrices — the ground truth in the demos."""
    n = len(cost_matrix)
    if n == 0:
        return 0
    m = len(cost_matrix[0])
    best = INF
    for perm in permutations(range(m), n):
        best = min(best, sum(cost_matrix[i][perm[i]] for i in range(n)))
    return best


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: cheapest way to push the max flow")
    print("=" * 60)
    # Two parallel routes s->t: one narrow and cheap, one wide and expensive.
    g = MinCostMaxFlow(4)
    g.add_edge(0, 1, 2, 1)    # s -> a  cap 2, cost 1
    g.add_edge(0, 2, 3, 4)    # s -> b  cap 3, cost 4
    g.add_edge(1, 3, 2, 1)    # a -> t  cap 2, cost 1
    g.add_edge(2, 3, 3, 1)    # b -> t  cap 3, cost 1
    flow, cost = g.min_cost_flow(0, 3)
    print(f"\n  max flow = {flow}   (capacity-limited: 2 + 3)")
    print(f"  min cost = {cost}   (2 units at 2 each, 3 units at 5 each)")

    # Capping the flow proves the CHEAP route is taken first.
    g2 = MinCostMaxFlow(4)
    g2.add_edge(0, 1, 2, 1)
    g2.add_edge(0, 2, 3, 4)
    g2.add_edge(1, 3, 2, 1)
    g2.add_edge(2, 3, 3, 1)
    flow2, cost2 = g2.min_cost_flow(0, 3, max_flow=2)
    print(f"\n  capped at 2 units: flow={flow2} cost={cost2} "
          f"(uses only the cheap route)")


def demo_negative_edge():
    print("\n" + "=" * 60)
    print("DEMO 2: a negative-cost edge — why Bellman-Ford seeds potentials")
    print("=" * 60)
    # s->a is a subsidy (cost -5). Dijkstra alone would be unsound; Bellman-Ford
    # produces potentials that make every reduced cost non-negative.
    g = MinCostMaxFlow(4)
    g.add_edge(0, 1, 1, -5)
    g.add_edge(0, 2, 1, 2)
    g.add_edge(1, 3, 1, 1)
    g.add_edge(2, 3, 1, 1)
    pot = g._initial_potentials(0)
    print(f"\n  Bellman-Ford potentials: {pot}")
    print("  reduced cost of every edge (all must be >= 0):")
    for idx in range(0, len(g.edges), 2):
        v, cap, cost = g.edges[idx]
        u = g.edges[idx ^ 1][0]
        print(f"    {u}->{v}  w={cost:>3}  w' = {cost + pot[u] - pot[v]}")
    flow, cost = g.min_cost_flow(0, 3)
    print(f"\n  flow={flow} cost={cost}   ((-5+1) + (2+1))")


def demo_no_augmenting_path():
    print("\n" + "=" * 60)
    print("DEMO 3: clean termination when no augmenting path exists")
    print("=" * 60)
    g = MinCostMaxFlow(4)
    g.add_edge(0, 1, 5, 1)     # nothing ever reaches node 3
    g.add_edge(2, 3, 5, 1)
    flow, cost = g.min_cost_flow(0, 3)
    print(f"\n  disconnected sink -> flow={flow} cost={cost} (returns, no hang)")

    g2 = MinCostMaxFlow(3)
    g2.add_edge(0, 1, 2, 1)
    g2.add_edge(1, 2, 2, 1)
    ok_cost, ok = g2.min_cost_flow_exact(0, 2, 2)
    g3 = MinCostMaxFlow(3)
    g3.add_edge(0, 1, 2, 1)
    g3.add_edge(1, 2, 2, 1)
    bad_cost, feasible = g3.min_cost_flow_exact(0, 2, 99)
    print(f"  exact flow of 2  -> cost={ok_cost} feasible={ok}")
    print(f"  exact flow of 99 -> cost={bad_cost} feasible={feasible}")


def demo_assignment():
    print("\n" + "=" * 60)
    print("DEMO 4: Hungarian is the unit-capacity bipartite special case")
    print("=" * 60)
    matrices = [
        [[4, 1, 3], [2, 0, 5], [3, 2, 2]],
        [[7, 5, 11], [9, 14, 10], [13, 2, 4]],
        [[1, 2], [4, 3]],
    ]
    for c in matrices:
        total, assign = assignment_via_mcmf(c)
        truth = brute_force_assignment(c)
        mark = "OK" if total == truth else "MISMATCH"
        print(f"\n  matrix {c}")
        print(f"    mcmf cost = {total}  brute force = {truth}  [{mark}]")
        print(f"    assignment = {assign}")


def demo_negative_cycle_refused():
    print("\n" + "=" * 60)
    print("DEMO 5: a negative cycle is refused, not silently mis-answered")
    print("=" * 60)
    g = MinCostMaxFlow(4)
    g.add_edge(0, 1, 1, 1)
    g.add_edge(1, 2, 1, -3)
    g.add_edge(2, 1, 1, 1)     # cycle 1->2->1 costs -2 per lap
    g.add_edge(2, 3, 1, 1)
    try:
        g.min_cost_flow(0, 3)
        print("\n  ERROR: should have raised")
    except NegativeCycleError as e:
        print(f"\n  NegativeCycleError: {e}")


if __name__ == "__main__":
    demo_basic()
    demo_negative_edge()
    demo_no_augmenting_path()
    demo_assignment()
    demo_negative_cycle_refused()
