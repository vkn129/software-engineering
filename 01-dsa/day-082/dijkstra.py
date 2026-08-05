"""
Dijkstra's Algorithm — Greedy shortest path for non-negative weights.

Core idea: greedily expand the closest unvisited vertex. Once a vertex is
finalized, its distance is optimal because all remaining paths go through
vertices with equal or larger tentative distances, plus non-negative edges.

Two implementations:
  1. Naive O(V^2) — scan all vertices to find minimum
  2. Binary heap O((V+E) log V) — priority queue for efficient minimum extraction
"""

import heapq
import time
import random
from collections import defaultdict


class WeightedGraph:
    """Adjacency list representation of a weighted directed graph."""

    def __init__(self):
        self.graph = defaultdict(list)  # node -> [(neighbor, weight), ...]
        self.vertices = set()

    def add_edge(self, u, v, weight):
        """Add directed edge from u to v with given weight."""
        self.graph[u].append((v, weight))
        self.vertices.add(u)
        self.vertices.add(v)

    def add_undirected_edge(self, u, v, weight):
        """Add undirected edge between u and v."""
        self.add_edge(u, v, weight)
        self.add_edge(v, u, weight)


def dijkstra_naive(graph, source):
    """
    Dijkstra's algorithm — naive O(V^2) implementation.

    Uses linear scan to find the unvisited vertex with minimum distance.
    Optimal for dense graphs where E is close to V^2.

    Time:  O(V^2)
    Space: O(V)

    Returns:
        (dist, parent): dist[v] is shortest distance from source to v,
                        parent[v] is the predecessor on the shortest path.
    """
    dist = {v: float('inf') for v in graph.vertices}
    parent = {v: None for v in graph.vertices}
    visited = set()

    dist[source] = 0

    for _ in range(len(graph.vertices)):
        # Find unvisited vertex with minimum distance
        u = None
        min_dist = float('inf')
        for v in graph.vertices:
            if v not in visited and dist[v] < min_dist:
                min_dist = dist[v]
                u = v

        if u is None:
            break  # Remaining vertices are unreachable

        visited.add(u)

        # Relax all outgoing edges from u
        for v, weight in graph.graph[u]:
            if v not in visited and dist[u] + weight < dist[v]:
                dist[v] = dist[u] + weight
                parent[v] = u

    return dist, parent


def dijkstra_heap(graph, source):
    """
    Dijkstra's algorithm — binary heap (priority queue) implementation.

    Uses a min-heap to efficiently extract the vertex with minimum distance.
    Since Python's heapq doesn't support decrease-key, we push duplicate
    entries and skip stale ones when popped.

    Time:  O((V + E) log V)
    Space: O(V + E)

    Returns:
        (dist, parent): dist[v] is shortest distance from source to v,
                        parent[v] is the predecessor on the shortest path.
    """
    dist = {v: float('inf') for v in graph.vertices}
    parent = {v: None for v in graph.vertices}

    dist[source] = 0
    # Min-heap of (distance, vertex)
    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)

        # Skip stale entries: if we already found a shorter path to u
        if d > dist[u]:
            continue

        for v, weight in graph.graph[u]:
            new_dist = dist[u] + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                parent[v] = u
                heapq.heappush(heap, (new_dist, v))

    return dist, parent


def reconstruct_path(parent, source, target):
    """
    Reconstruct the shortest path from source to target using parent pointers.

    Returns:
        List of vertices from source to target, or [] if no path exists.
    """
    if parent.get(target) is None and target != source:
        return []  # No path exists

    path = []
    current = target
    while current is not None:
        path.append(current)
        current = parent[current]

    path.reverse()

    # Verify path starts at source
    if path and path[0] == source:
        return path
    return []


def dijkstra_with_path(graph, source, target):
    """
    Convenience function: run Dijkstra's and return both distance and path.

    Returns:
        (distance, path): shortest distance and the path as a list of vertices.
    """
    dist, parent = dijkstra_heap(graph, source)
    path = reconstruct_path(parent, source, target)
    return dist.get(target, float('inf')), path


def dijkstra_multi_target(graph, source, targets):
    """
    Find shortest paths from source to multiple targets.

    Runs Dijkstra once and extracts paths to all targets.
    More efficient than running Dijkstra separately for each target.

    Returns:
        Dict mapping each target to (distance, path).
    """
    dist, parent = dijkstra_heap(graph, source)
    results = {}
    for t in targets:
        path = reconstruct_path(parent, source, t)
        results[t] = (dist.get(t, float('inf')), path)
    return results


# ---------------------------------------------------------------------------
# Demo: Road Network Shortest Path
# ---------------------------------------------------------------------------

def demo_road_network():
    """
    Model a small road network and find shortest paths.

    Cities and distances (miles):
        A --4-- B --3-- C
        |       |       |
        2       1       5
        |       |       |
        D --7-- E --2-- F
                |
                6
                |
                G
    """
    print("=" * 60)
    print("DEMO: Road Network Shortest Path")
    print("=" * 60)

    g = WeightedGraph()
    roads = [
        ("A", "B", 4), ("A", "D", 2),
        ("B", "C", 3), ("B", "E", 1),
        ("C", "F", 5),
        ("D", "E", 7),
        ("E", "F", 2), ("E", "G", 6),
    ]
    for u, v, w in roads:
        g.add_undirected_edge(u, v, w)

    print("\nRoad network:")
    for u, v, w in roads:
        print(f"  {u} <--{w}--> {v}")

    source = "A"
    dist, parent = dijkstra_heap(g, source)

    print(f"\nShortest distances from {source}:")
    for v in sorted(dist.keys()):
        path = reconstruct_path(parent, source, v)
        print(f"  {source} -> {v}: distance={dist[v]}, path={' -> '.join(path)}")

    # Specific query
    target = "G"
    distance, path = dijkstra_with_path(g, source, target)
    print(f"\nDetailed: {source} to {target}")
    print(f"  Shortest distance: {distance}")
    print(f"  Path: {' -> '.join(path)}")

    # Multi-target query
    targets = ["C", "F", "G"]
    results = dijkstra_multi_target(g, source, targets)
    print(f"\nMulti-target from {source}:")
    for t in targets:
        d, p = results[t]
        print(f"  -> {t}: distance={d}, path={' -> '.join(p)}")


# ---------------------------------------------------------------------------
# Demo: Naive vs Heap Performance Comparison
# ---------------------------------------------------------------------------

def generate_random_graph(num_vertices, num_edges, max_weight=100):
    """Generate a random weighted directed graph."""
    g = WeightedGraph()
    for i in range(num_vertices):
        g.add_edge(i, i, 0)  # Ensure vertex exists
        g.vertices.add(i)

    edges_added = 0
    while edges_added < num_edges:
        u = random.randint(0, num_vertices - 1)
        v = random.randint(0, num_vertices - 1)
        if u != v:
            w = random.randint(1, max_weight)
            g.add_edge(u, v, w)
            edges_added += 1

    # Remove self-loops we added for vertex tracking
    for v in g.vertices:
        g.graph[v] = [(n, w) for n, w in g.graph[v] if not (n == v and w == 0)]

    return g


def demo_performance_comparison():
    """
    Compare naive O(V^2) vs heap-based O((V+E)logV) on different graph densities.
    """
    print("\n" + "=" * 60)
    print("DEMO: Naive vs Heap Performance Comparison")
    print("=" * 60)

    random.seed(42)

    test_cases = [
        ("Sparse (V=500, E=1500)", 500, 1500),
        ("Medium (V=500, E=25000)", 500, 25000),
        ("Dense  (V=500, E=100000)", 500, 100000),
    ]

    for name, v, e in test_cases:
        g = generate_random_graph(v, e)

        # Naive
        start = time.perf_counter()
        dist_naive, _ = dijkstra_naive(g, 0)
        time_naive = time.perf_counter() - start

        # Heap
        start = time.perf_counter()
        dist_heap, _ = dijkstra_heap(g, 0)
        time_heap = time.perf_counter() - start

        # Verify both produce same results
        match = all(
            abs(dist_naive.get(v, float('inf')) - dist_heap.get(v, float('inf'))) < 1e-9
            for v in g.vertices
        )

        print(f"\n{name}:")
        print(f"  Naive: {time_naive:.4f}s")
        print(f"  Heap:  {time_heap:.4f}s")
        print(f"  Speedup: {time_naive / time_heap:.1f}x")
        print(f"  Results match: {match}")


if __name__ == "__main__":
    demo_road_network()
    demo_performance_comparison()
