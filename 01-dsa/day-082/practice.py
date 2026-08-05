"""
Day 82 Practice: Dijkstra's Algorithm Problems

Five exercises covering shortest path variants, constrained shortest paths,
and multi-source/multi-destination queries.
"""

import heapq
from collections import defaultdict


# ---------------------------------------------------------------------------
# Exercise 1: Network Delay Time (LeetCode 743)
# ---------------------------------------------------------------------------
# Given a network of n nodes and times[i] = (u, v, w) representing directed
# edges with travel time w, find how long until all nodes receive a signal
# sent from node k. Return -1 if not all nodes are reachable.

def network_delay_time(times, n, k):
    """
    Find the time for a signal from node k to reach all n nodes.

    This is Dijkstra's algorithm where the answer is the maximum shortest
    distance to any node (the last node to receive the signal).

    Args:
        times: list of [u, v, w] directed edges with weight w
        n: number of nodes (1-indexed, 1 to n)
        k: source node

    Returns:
        Minimum time for all nodes to receive signal, or -1 if impossible.

    Example:
        network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2) -> 2
    """
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0
    heap = [(0, k)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    max_dist = max(dist.values())
    return max_dist if max_dist < float('inf') else -1


# ---------------------------------------------------------------------------
# Exercise 2: Cheapest Flights Within K Stops (LeetCode 787)
# ---------------------------------------------------------------------------
# Find the cheapest price from src to dst with at most k stops.
# This is a constrained shortest path — standard Dijkstra doesn't work directly.

def find_cheapest_price(n, flights, src, dst, k):
    """
    Find cheapest flight from src to dst with at most k stops.

    Modified Dijkstra: track (cost, stops, node) in the heap. We allow
    revisiting a node if we arrive with fewer stops, since a more expensive
    path with fewer stops might lead to a cheaper total via future edges.

    Args:
        n: number of cities (0-indexed)
        flights: list of [from, to, price]
        src: source city
        dst: destination city
        k: maximum number of stops (intermediate cities)

    Returns:
        Cheapest price, or -1 if no valid route exists.

    Example:
        find_cheapest_price(4, [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]],
                            0, 3, 1) -> 700
    """
    graph = defaultdict(list)
    for u, v, w in flights:
        graph[u].append((v, w))

    # (cost, stops_used, node)
    heap = [(0, 0, src)]
    # best_stops[node] = minimum stops we've reached this node with
    # We skip a state only if we've seen this node with fewer or equal stops
    best_stops = {i: float('inf') for i in range(n)}

    while heap:
        cost, stops, u = heapq.heappop(heap)

        if u == dst:
            return cost

        if stops > k:
            continue

        # Skip if we've reached this node with fewer stops already
        if stops >= best_stops[u]:
            continue
        best_stops[u] = stops

        for v, w in graph[u]:
            heapq.heappush(heap, (cost + w, stops + 1, v))

    return -1


# ---------------------------------------------------------------------------
# Exercise 3: Path With Minimum Effort (LeetCode 1631)
# ---------------------------------------------------------------------------
# Given a 2D grid of heights, find the path from top-left to bottom-right
# that minimizes the maximum absolute difference in heights between
# consecutive cells.

def minimum_effort_path(heights):
    """
    Find the path minimizing maximum effort (height difference between steps).

    Modified Dijkstra where the "distance" is the maximum effort along the path.
    Relaxation: if max(effort_so_far, |heights[r1][c1] - heights[r2][c2]|) < dist[r2][c2],
    update.

    Args:
        heights: 2D list of cell heights

    Returns:
        Minimum possible maximum effort.

    Example:
        minimum_effort_path([[1,2,2],[3,8,2],[5,3,5]]) -> 2
    """
    rows, cols = len(heights), len(heights[0])
    dist = [[float('inf')] * cols for _ in range(rows)]
    dist[0][0] = 0

    # (effort, row, col)
    heap = [(0, 0, 0)]
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while heap:
        effort, r, c = heapq.heappop(heap)

        if r == rows - 1 and c == cols - 1:
            return effort

        if effort > dist[r][c]:
            continue

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                new_effort = max(effort, abs(heights[r][c] - heights[nr][nc]))
                if new_effort < dist[nr][nc]:
                    dist[nr][nc] = new_effort
                    heapq.heappush(heap, (new_effort, nr, nc))

    return dist[rows - 1][cols - 1]


# ---------------------------------------------------------------------------
# Exercise 4: Minimum Cost to Destination with Fuel Constraint
# ---------------------------------------------------------------------------
# Given cities connected by roads with distances, and gas stations at some
# cities, find the minimum distance from source to destination. Your tank
# holds max_fuel. Each unit of distance costs 1 unit of fuel. Refueling
# fills the tank completely and is free.

def min_cost_with_fuel(n, edges, source, destination, max_fuel, gas_stations):
    """
    Find shortest path from source to destination respecting fuel constraints.

    State: (distance, fuel_remaining, city). We can refuel at gas stations.

    Args:
        n: number of cities (0-indexed)
        edges: list of [u, v, distance] (undirected)
        source: starting city (starts with full tank)
        destination: target city
        max_fuel: tank capacity
        gas_stations: set of cities with gas stations

    Returns:
        Minimum distance, or -1 if impossible.

    Example:
        min_cost_with_fuel(4, [[0,1,3],[1,2,4],[0,3,10],[3,2,1]],
                           0, 2, 6, {1}) -> 7
    """
    graph = defaultdict(list)
    for u, v, d in edges:
        graph[u].append((v, d))
        graph[v].append((u, d))

    # State: (total_distance, fuel_remaining, city)
    heap = [(0, max_fuel, source)]
    # visited[(city, fuel)] to avoid reprocessing
    visited = set()

    while heap:
        dist, fuel, city = heapq.heappop(heap)

        if city == destination:
            return dist

        if (city, fuel) in visited:
            continue
        visited.add((city, fuel))

        # Option: refuel if at a gas station
        if city in gas_stations and fuel < max_fuel:
            if (city, max_fuel) not in visited:
                heapq.heappush(heap, (dist, max_fuel, city))

        # Move to neighbors
        for neighbor, edge_dist in graph[city]:
            if fuel >= edge_dist:
                new_fuel = fuel - edge_dist
                if (neighbor, new_fuel) not in visited:
                    heapq.heappush(heap, (dist + edge_dist, new_fuel, neighbor))

    return -1


# ---------------------------------------------------------------------------
# Exercise 5: Multi-Destination Shortest Paths
# ---------------------------------------------------------------------------
# Given a graph, a source, and multiple destinations, find the shortest path
# to each destination and the optimal order to visit all destinations
# (nearest-first greedy).

def multi_destination_paths(n, edges, source, destinations):
    """
    Find shortest paths from source to multiple destinations and suggest visit order.

    Runs Dijkstra once from source, then extracts paths to all destinations.
    Also returns a greedy visit order (nearest destination first).

    Args:
        n: number of nodes (0-indexed)
        edges: list of [u, v, weight] (directed)
        source: starting node
        destinations: list of destination nodes

    Returns:
        dict with:
            'paths': {dest: (distance, path_list)},
            'visit_order': list of (dest, distance) in nearest-first order

    Example:
        multi_destination_paths(5, [[0,1,2],[0,2,5],[1,3,1],[2,3,2],[1,4,7]],
                                0, [3, 4]) -> paths to 3 (dist=3) and 4 (dist=9)
    """
    graph = defaultdict(list)
    vertices = set(range(n))
    for u, v, w in edges:
        graph[u].append((v, w))

    dist = {v: float('inf') for v in vertices}
    parent = {v: None for v in vertices}
    dist[source] = 0

    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))

    # Reconstruct paths
    def get_path(target):
        if dist[target] == float('inf'):
            return []
        path = []
        cur = target
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path

    paths = {}
    for dest in destinations:
        paths[dest] = (dist[dest], get_path(dest))

    # Greedy visit order (nearest first)
    visit_order = sorted(
        [(dest, dist[dest]) for dest in destinations],
        key=lambda x: x[1]
    )

    return {'paths': paths, 'visit_order': visit_order}


# ===========================================================================
# Tests
# ===========================================================================

def test_network_delay():
    assert network_delay_time([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2) == 2
    assert network_delay_time([[1, 2, 1]], 2, 1) == 1
    assert network_delay_time([[1, 2, 1]], 2, 2) == -1  # Node 1 unreachable from 2
    assert network_delay_time([[1, 2, 1], [2, 3, 2], [1, 3, 4]], 3, 1) == 3
    print("  [PASS] Network Delay Time")


def test_cheapest_flights():
    assert find_cheapest_price(
        4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]],
        0, 3, 1
    ) == 700

    # Direct flight cheaper
    assert find_cheapest_price(
        3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]],
        0, 2, 0
    ) == 500

    # No valid route
    assert find_cheapest_price(
        3, [[0, 1, 100], [1, 2, 100]],
        0, 2, 0
    ) == -1

    # With enough stops, use cheaper path
    assert find_cheapest_price(
        3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]],
        0, 2, 1
    ) == 200

    print("  [PASS] Cheapest Flights Within K Stops")


def test_minimum_effort():
    assert minimum_effort_path([[1, 2, 2], [3, 8, 2], [5, 3, 5]]) == 2
    assert minimum_effort_path([[1, 2, 3], [3, 8, 4], [5, 3, 5]]) == 1
    assert minimum_effort_path([[1, 2, 1, 1, 1], [1, 2, 1, 2, 1], [1, 2, 1, 2, 1],
                                 [1, 2, 1, 2, 1], [1, 1, 1, 2, 1]]) == 0
    assert minimum_effort_path([[1]]) == 0
    print("  [PASS] Path With Minimum Effort")


def test_fuel_constraint():
    # Can reach via 0->1->2 (distance 7, needs refuel at 1)
    assert min_cost_with_fuel(
        4, [[0, 1, 3], [1, 2, 4], [0, 3, 10], [3, 2, 1]],
        0, 2, 6, {1}
    ) == 7

    # Direct path possible with enough fuel
    assert min_cost_with_fuel(
        2, [[0, 1, 5]], 0, 1, 5, set()
    ) == 5

    # Not enough fuel and no gas stations
    assert min_cost_with_fuel(
        2, [[0, 1, 10]], 0, 1, 5, set()
    ) == -1

    # Source == destination
    assert min_cost_with_fuel(
        2, [[0, 1, 5]], 0, 0, 5, set()
    ) == 0

    print("  [PASS] Minimum Cost with Fuel Constraint")


def test_multi_destination():
    result = multi_destination_paths(
        5, [[0, 1, 2], [0, 2, 5], [1, 3, 1], [2, 3, 2], [1, 4, 7]],
        0, [3, 4]
    )
    assert result['paths'][3][0] == 3  # 0->1->3
    assert result['paths'][4][0] == 9  # 0->1->4
    assert result['paths'][3][1] == [0, 1, 3]
    assert result['visit_order'][0] == (3, 3)  # Nearest first

    # Unreachable destination
    result = multi_destination_paths(
        3, [[0, 1, 1]], 0, [1, 2]
    )
    assert result['paths'][1][0] == 1
    assert result['paths'][2][0] == float('inf')
    assert result['paths'][2][1] == []

    print("  [PASS] Multi-Destination Shortest Paths")


if __name__ == "__main__":
    print("Running Day 82 practice tests...\n")
    test_network_delay()
    test_cheapest_flights()
    test_minimum_effort()
    test_fuel_constraint()
    test_multi_destination()
    print("\nAll tests passed!")
