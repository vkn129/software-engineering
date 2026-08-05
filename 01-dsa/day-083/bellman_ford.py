"""
Day 83: Bellman-Ford Algorithm — From Scratch

Handles negative edge weights and detects negative cycles.
Where Dijkstra greedily commits, Bellman-Ford iterates patiently.
"""

import math


# ---------------------------------------------------------------------------
# 1. Standard Bellman-Ford
# ---------------------------------------------------------------------------

def bellman_ford(vertices, edges, source):
    """
    Single-source shortest paths with negative weight support.

    Args:
        vertices: list of vertex labels
        edges: list of (u, v, weight) tuples
        source: starting vertex

    Returns:
        (dist, parent, negative_cycle):
            dist: dict of shortest distances from source
            parent: dict for path reconstruction
            negative_cycle: True if negative cycle reachable from source
    """
    dist = {v: math.inf for v in vertices}
    parent = {v: None for v in vertices}
    dist[source] = 0

    # V-1 rounds of relaxation
    for i in range(len(vertices) - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                updated = True
        # Early termination: no relaxation means we've converged
        if not updated:
            break

    # V-th round: check for negative cycles
    negative_cycle = False
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            negative_cycle = True
            break

    return dist, parent, negative_cycle


def reconstruct_path(parent, target):
    """Trace back from target to source using parent pointers."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


# ---------------------------------------------------------------------------
# 2. Bellman-Ford with negative cycle extraction
# ---------------------------------------------------------------------------

def find_negative_cycle(vertices, edges):
    """
    Find and return one negative cycle if it exists.

    Trick: run Bellman-Ford from a virtual source connected to all vertices
    with weight 0, then check for relaxation in round V.
    """
    # Add virtual source connected to all vertices
    dist = {v: 0 for v in vertices}  # equivalent to virtual source
    parent = {v: None for v in vertices}

    # V-1 rounds
    for _ in range(len(vertices) - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u

    # V-th round: find a vertex that can still be relaxed
    cycle_vertex = None
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            cycle_vertex = v
            break

    if cycle_vertex is None:
        return None  # no negative cycle

    # Walk back V times to ensure we're inside the cycle
    v = cycle_vertex
    for _ in range(len(vertices)):
        v = parent[v]

    # Now v is definitely on the cycle — trace it
    cycle = []
    u = v
    while True:
        cycle.append(u)
        u = parent[u]
        if u == v:
            cycle.append(v)
            break
    cycle.reverse()
    return cycle


# ---------------------------------------------------------------------------
# 3. SPFA — Shortest Path Faster Algorithm (queue-based optimization)
# ---------------------------------------------------------------------------

def spfa(adj, vertices, source):
    """
    SPFA: only re-relax vertices whose distance changed.

    Average case: O(E), much faster than standard Bellman-Ford.
    Worst case: still O(VE).

    Uses a queue of vertices to re-examine (like BFS meets Bellman-Ford).
    Detects negative cycles by counting relaxations per vertex.
    """
    from collections import deque

    dist = {v: math.inf for v in vertices}
    parent = {v: None for v in vertices}
    in_queue = {v: False for v in vertices}
    relax_count = {v: 0 for v in vertices}

    dist[source] = 0
    queue = deque([source])
    in_queue[source] = True

    while queue:
        u = queue.popleft()
        in_queue[u] = False

        for v, w in adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                relax_count[v] += 1

                # If a vertex is relaxed V times, negative cycle exists
                if relax_count[v] >= len(vertices):
                    return dist, parent, True  # negative cycle

                if not in_queue[v]:
                    queue.append(v)
                    in_queue[v] = True

    return dist, parent, False


# ---------------------------------------------------------------------------
# 4. Currency Arbitrage Detection
# ---------------------------------------------------------------------------

def detect_arbitrage(currencies, rates):
    """
    Detect currency arbitrage using Bellman-Ford on log-transformed rates.

    rates: dict of (from_currency, to_currency) -> exchange_rate
    Arbitrage exists if: rate_AB * rate_BC * rate_CA > 1
    Equivalently: log(rate_AB) + log(rate_BC) + log(rate_CA) > 0
    Negate: -log(rate_AB) + ... < 0, which is a negative cycle.
    """
    import math

    # Build edge list with negated log-rates
    edges = []
    for (u, v), rate in rates.items():
        edges.append((u, v, -math.log(rate)))

    # Run Bellman-Ford from each currency
    for source in currencies:
        _, _, has_neg_cycle = bellman_ford(currencies, edges, source)
        if has_neg_cycle:
            # Find the actual cycle for reporting
            cycle = find_negative_cycle(currencies, edges)
            return True, cycle

    return False, None


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic Bellman-Ford")
    print("=" * 60)

    vertices = [0, 1, 2, 3, 4]
    edges = [
        (0, 1, 6), (0, 3, 7),
        (1, 2, 5), (1, 3, 8), (1, 4, -4),
        (2, 1, -2),
        (3, 2, -3), (3, 4, 9),
        (4, 0, 2), (4, 2, 7),
    ]

    dist, parent, neg_cycle = bellman_ford(vertices, edges, 0)
    print(f"\nGraph has negative weights but no negative cycles")
    print(f"Edges: {edges}")
    print(f"\nShortest distances from vertex 0:")
    for v in vertices:
        path = reconstruct_path(parent, v)
        print(f"  0 → {v}: distance={dist[v]}, path={path}")
    print(f"Negative cycle: {neg_cycle}")


def demo_negative_cycle():
    print("\n" + "=" * 60)
    print("DEMO 2: Negative Cycle Detection")
    print("=" * 60)

    vertices = [0, 1, 2, 3]
    edges = [
        (0, 1, 1),
        (1, 2, -3),   # Negative cycle: 1 → 2 → 3 → 1
        (2, 3, 2),    # Total weight: -3 + 2 + (-1) = -2
        (3, 1, -1),
    ]

    dist, _, neg_cycle = bellman_ford(vertices, edges, 0)
    print(f"\nGraph with negative cycle: 1 → 2 → 3 → 1 (weight: -2)")
    print(f"Negative cycle detected: {neg_cycle}")

    cycle = find_negative_cycle(vertices, edges)
    if cycle:
        total = 0
        parts = []
        for i in range(len(cycle) - 1):
            for u, v, w in edges:
                if u == cycle[i] and v == cycle[i + 1]:
                    total += w
                    parts.append(f"{u}→{v}({w})")
                    break
        print(f"Cycle: {cycle}")
        print(f"Cycle edges: {', '.join(parts)}, total weight: {total}")


def demo_vs_dijkstra():
    print("\n" + "=" * 60)
    print("DEMO 3: Where Dijkstra Fails, Bellman-Ford Succeeds")
    print("=" * 60)

    # Classic counterexample for Dijkstra with negative weights
    #     0 --5--> 1
    #     |        |
    #     3       -4
    #     |        |
    #     v        v
    #     2 --1--> 3
    vertices = [0, 1, 2, 3]
    edges = [(0, 1, 5), (0, 2, 3), (1, 3, -4), (2, 3, 1)]

    dist, parent, _ = bellman_ford(vertices, edges, 0)
    print(f"\n0→1(5), 0→2(3), 1→3(-4), 2→3(1)")
    print(f"\nDijkstra would find: 0→2→3 = cost 4")
    print(f"  (greedily picks 0→2 first since 3 < 5)")
    print(f"\nBellman-Ford correctly finds: 0→1→3 = cost {dist[3]}")
    print(f"  Path: {reconstruct_path(parent, 3)}")
    print(f"  (The -4 edge makes the longer initial path cheaper)")


def demo_arbitrage():
    print("\n" + "=" * 60)
    print("DEMO 4: Currency Arbitrage Detection")
    print("=" * 60)

    currencies = ["USD", "EUR", "GBP", "JPY"]

    # These rates create an arbitrage opportunity:
    # USD → EUR → GBP → USD: 0.9 * 0.8 * 1.5 = 1.08 (8% profit!)
    rates = {
        ("USD", "EUR"): 0.9,
        ("EUR", "GBP"): 0.8,
        ("GBP", "USD"): 1.5,
        ("USD", "JPY"): 110.0,
        ("JPY", "USD"): 1 / 112.0,
        ("EUR", "JPY"): 120.0,
        ("JPY", "EUR"): 1 / 122.0,
        ("GBP", "JPY"): 150.0,
        ("JPY", "GBP"): 1 / 152.0,
        ("EUR", "USD"): 1 / 0.9,
        ("GBP", "EUR"): 1 / 0.8,
        ("USD", "GBP"): 1 / 1.5,
    }

    found, cycle = detect_arbitrage(currencies, rates)
    print(f"\nExchange rates (partial):")
    print(f"  USD → EUR: 0.9")
    print(f"  EUR → GBP: 0.8")
    print(f"  GBP → USD: 1.5")
    print(f"\nArbitrage detected: {found}")
    if cycle:
        print(f"Cycle: {' → '.join(str(c) for c in cycle)}")
        # Calculate profit
        product = 1.0
        for i in range(len(cycle) - 1):
            rate = rates.get((cycle[i], cycle[i + 1]), 0)
            if rate:
                product *= rate
                print(f"  {cycle[i]} → {cycle[i+1]}: ×{rate}")
        print(f"Round-trip multiplier: {product:.4f}")
        print(f"Profit per unit: {(product - 1) * 100:.1f}%")


def demo_spfa():
    print("\n" + "=" * 60)
    print("DEMO 5: SPFA (Optimized Bellman-Ford)")
    print("=" * 60)

    from collections import defaultdict
    import time

    n = 500
    # Build sparse graph with some negative weights
    import random
    random.seed(42)

    adj = defaultdict(list)
    edge_list = []
    verts = list(range(n))
    for u in range(n):
        for _ in range(3):  # ~3 edges per vertex
            v = random.randint(0, n - 1)
            w = random.randint(-5, 20)
            adj[u].append((v, w))
            edge_list.append((u, v, w))

    # Time standard Bellman-Ford
    start = time.perf_counter()
    dist1, _, _ = bellman_ford(verts, edge_list, 0)
    bf_time = time.perf_counter() - start

    # Time SPFA
    start = time.perf_counter()
    dist2, _, _ = spfa(adj, verts, 0)
    spfa_time = time.perf_counter() - start

    print(f"\nSparse graph: {n} vertices, {len(edge_list)} edges")
    print(f"Bellman-Ford: {bf_time:.4f}s")
    print(f"SPFA:         {spfa_time:.4f}s")
    print(f"Speedup:      {bf_time / spfa_time:.1f}x")

    # Verify same results
    match = sum(1 for v in verts if abs(dist1[v] - dist2[v]) < 1e-9)
    print(f"Results match: {match}/{n} vertices")


if __name__ == "__main__":
    demo_basic()
    demo_negative_cycle()
    demo_vs_dijkstra()
    demo_arbitrage()
    demo_spfa()
