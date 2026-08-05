"""
Day 83 Practice: Bellman-Ford Algorithm

6 exercises covering negative weights, cycle detection, and real-world applications.
Implement the TODO functions, then run: python practice.py
"""

import math
from collections import defaultdict, deque


# ===================================================================
# Exercise 1: Basic Bellman-Ford
# ===================================================================
# Implement single-source shortest paths using V-1 rounds of edge relaxation.

def shortest_paths(vertices, edges, source):
    """
    Return dict of shortest distances from source to all vertices.
    edges: list of (u, v, weight) tuples.
    Return math.inf for unreachable vertices.
    """
    # TODO: implement Bellman-Ford
    pass


def _sol_shortest_paths(vertices, edges, source):
    dist = {v: math.inf for v in vertices}
    dist[source] = 0
    for _ in range(len(vertices) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break
    return dist


# ===================================================================
# Exercise 2: Negative Cycle Detection
# ===================================================================
# After V-1 rounds, check if a V-th round would still relax any edge.

def has_negative_cycle(vertices, edges):
    """Return True if the graph contains a negative-weight cycle."""
    # TODO: implement using Bellman-Ford's V-th round check
    pass


def _sol_has_negative_cycle(vertices, edges):
    dist = {v: 0 for v in vertices}  # start all at 0 to find any cycle
    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    # V-th round: if any edge can still relax, negative cycle exists
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            return True
    return False


# ===================================================================
# Exercise 3: Path Reconstruction
# ===================================================================
# Track parent pointers during relaxation to reconstruct shortest paths.

def shortest_path_with_route(vertices, edges, source, target):
    """
    Return (distance, path) where path is list of vertices from source to target.
    Return (math.inf, []) if unreachable.
    """
    # TODO: implement Bellman-Ford with parent tracking
    pass


def _sol_shortest_path_with_route(vertices, edges, source, target):
    dist = {v: math.inf for v in vertices}
    parent = {v: None for v in vertices}
    dist[source] = 0

    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u

    if dist[target] == math.inf:
        return math.inf, []

    path = []
    current = target
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return dist[target], path


# ===================================================================
# Exercise 4: Early Termination Optimization
# ===================================================================
# If no edge is relaxed in a round, the algorithm has converged.
# Return the number of rounds needed (measure convergence speed).

def bellman_ford_rounds(vertices, edges, source):
    """
    Run Bellman-Ford with early termination.
    Return (dist_dict, rounds_used) where rounds_used <= V-1.
    """
    # TODO: implement with round counting and early exit
    pass


def _sol_bellman_ford_rounds(vertices, edges, source):
    dist = {v: math.inf for v in vertices}
    dist[source] = 0
    rounds = 0

    for i in range(len(vertices) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        rounds = i + 1
        if not updated:
            break

    return dist, rounds


# ===================================================================
# Exercise 5: Currency Arbitrage
# ===================================================================
# Given exchange rates, detect if an arbitrage opportunity exists.
# Hint: use -log(rate) as edge weights, then find negative cycles.

def has_arbitrage(currencies, rates):
    """
    currencies: list of currency names
    rates: dict of (from, to) -> exchange_rate

    Return True if there's a sequence of trades that yields profit.
    """
    # TODO: implement using Bellman-Ford on log-transformed rates
    pass


def _sol_has_arbitrage(currencies, rates):
    edges = []
    for (u, v), rate in rates.items():
        edges.append((u, v, -math.log(rate)))

    EPS = 1e-9  # tolerance for floating-point log arithmetic
    dist = {c: 0 for c in currencies}
    for _ in range(len(currencies) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v] - EPS:
                dist[v] = dist[u] + w

    for u, v, w in edges:
        if dist[u] + w < dist[v] - EPS:
            return True
    return False


# ===================================================================
# Exercise 6: Cheapest Flight with K Stops
# ===================================================================
# Find cheapest flight from src to dst with at most K intermediate stops.
# This is a modified Bellman-Ford that runs exactly K+1 rounds
# and uses the PREVIOUS round's distances (not current) for relaxation.

def cheapest_flight(n, flights, src, dst, k):
    """
    n: number of cities (0 to n-1)
    flights: list of (from, to, price)
    src, dst: source and destination cities
    k: max intermediate stops allowed

    Return minimum cost, or -1 if impossible within K stops.
    """
    # TODO: implement modified Bellman-Ford with K+1 rounds
    pass


def _sol_cheapest_flight(n, flights, src, dst, k):
    dist = [math.inf] * n
    dist[src] = 0

    # K+1 rounds (K stops = K+1 edges)
    for _ in range(k + 1):
        # Use a COPY of previous round's distances
        # This prevents using paths discovered in the current round
        prev = dist[:]
        for u, v, w in flights:
            if prev[u] + w < dist[v]:
                dist[v] = prev[u] + w

    return dist[dst] if dist[dst] != math.inf else -1


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if isinstance(expected, float):
            if got is not None and abs(got - expected) < 1e-9:
                passed += 1
                print(f"  PASS: {name}")
                return
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")

    def try_or_sol(student_fn, sol_fn, *args, **kwargs):
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
        return sol_fn(*args, **kwargs)

    # --- Exercise 1: Basic Shortest Paths ---
    print("\nExercise 1: Basic Bellman-Ford")
    verts = [0, 1, 2, 3]
    edges = [(0, 1, 4), (0, 2, 5), (1, 2, -3), (2, 3, 2)]
    dist = try_or_sol(shortest_paths, _sol_shortest_paths, verts, edges, 0)
    check("dist to 0", dist[0], 0)
    check("dist to 1", dist[1], 4)
    check("dist to 2 (via negative edge)", dist[2], 1)  # 0→1→2 = 4+(-3) = 1
    check("dist to 3", dist[3], 3)  # 0→1→2→3 = 4+(-3)+2 = 3

    # --- Exercise 2: Negative Cycle ---
    print("\nExercise 2: Negative Cycle Detection")
    no_cycle_edges = [(0, 1, -1), (1, 2, -2), (0, 2, 5)]
    check("no negative cycle",
          try_or_sol(has_negative_cycle, _sol_has_negative_cycle,
                     [0, 1, 2], no_cycle_edges), False)

    cycle_edges = [(0, 1, 1), (1, 2, -3), (2, 0, 1)]  # total: -1
    check("has negative cycle",
          try_or_sol(has_negative_cycle, _sol_has_negative_cycle,
                     [0, 1, 2], cycle_edges), True)

    # --- Exercise 3: Path Reconstruction ---
    print("\nExercise 3: Path Reconstruction")
    verts = [0, 1, 2, 3]
    edges = [(0, 1, 2), (1, 2, 3), (0, 2, 10), (2, 3, 1)]
    d, path = try_or_sol(shortest_path_with_route, _sol_shortest_path_with_route,
                         verts, edges, 0, 3)
    check("distance 0→3", d, 6)  # 0→1→2→3 = 2+3+1
    check("path 0→3", path, [0, 1, 2, 3])

    d2, path2 = try_or_sol(shortest_path_with_route, _sol_shortest_path_with_route,
                           verts, [], 0, 3)
    check("unreachable distance", d2, math.inf)
    check("unreachable path", path2, [])

    # --- Exercise 4: Early Termination ---
    print("\nExercise 4: Early Termination")
    # Simple chain: converges in 3 rounds (not 4)
    verts = list(range(5))
    edges = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)]
    dist, rounds = try_or_sol(bellman_ford_rounds, _sol_bellman_ford_rounds,
                              verts, edges, 0)
    check("chain dist to 4", dist[4], 4)
    check("chain converges early", rounds <= 4, True)

    # --- Exercise 5: Currency Arbitrage ---
    print("\nExercise 5: Currency Arbitrage")
    currencies = ["USD", "EUR", "GBP"]
    # Arbitrage: USD→EUR→GBP→USD = 0.9 * 0.85 * 1.4 = 1.071 > 1
    arb_rates = {
        ("USD", "EUR"): 0.9, ("EUR", "GBP"): 0.85, ("GBP", "USD"): 1.4,
        ("EUR", "USD"): 1/0.9, ("GBP", "EUR"): 1/0.85, ("USD", "GBP"): 1/1.4,
    }
    check("arbitrage exists",
          try_or_sol(has_arbitrage, _sol_has_arbitrage, currencies, arb_rates), True)

    # Fair rates: no arbitrage (exact inverses, only 2 currencies)
    fair_currencies = ["USD", "EUR"]
    fair_rates = {
        ("USD", "EUR"): 0.9, ("EUR", "USD"): 1.0 / 0.9,
    }
    check("no arbitrage with fair rates",
          try_or_sol(has_arbitrage, _sol_has_arbitrage, fair_currencies, fair_rates), False)

    # --- Exercise 6: Cheapest Flight with K Stops ---
    print("\nExercise 6: Cheapest Flight with K Stops")
    flights = [(0, 1, 100), (1, 2, 100), (0, 2, 500)]
    check("k=1: can use stopover",
          try_or_sol(cheapest_flight, _sol_cheapest_flight, 3, flights, 0, 2, 1), 200)
    check("k=0: must go direct",
          try_or_sol(cheapest_flight, _sol_cheapest_flight, 3, flights, 0, 2, 0), 500)

    flights2 = [(0, 1, 1), (1, 2, 1), (2, 3, 1)]
    check("k=0: no direct flight",
          try_or_sol(cheapest_flight, _sol_cheapest_flight, 4, flights2, 0, 3, 0), -1)
    check("k=2: enough stops",
          try_or_sol(cheapest_flight, _sol_cheapest_flight, 4, flights2, 0, 3, 2), 3)

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")


if __name__ == "__main__":
    run_tests()
