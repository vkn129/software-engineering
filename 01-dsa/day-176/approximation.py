"""
Day 176: Approximation Algorithms — From Scratch

Two classics:
  1. 2-approximation for Vertex Cover via maximal matching.
  2. Christofides 1.5-approximation for metric TSP.

Both stdlib-only. Christofides uses a greedy matching (not Edmonds'),
trading the strict 1.5 bound for tractable code.
"""

import math
import itertools
import random


# ---------------------------------------------------------------------------
# 1. 2-Approximation for Vertex Cover (matching-based)
# ---------------------------------------------------------------------------

def vertex_cover_2approx(n, edges):
    """
    Returns a vertex cover S with |S| <= 2 * |OPT|.

    Greedy maximal matching: walk edges, take any edge whose endpoints
    are not yet covered; cover both endpoints.
    """
    covered = [False] * n
    cover = set()
    matching = []
    for u, v in edges:
        if not covered[u] and not covered[v]:
            covered[u] = True
            covered[v] = True
            cover.add(u)
            cover.add(v)
            matching.append((u, v))
    return cover, matching


def is_valid_cover(n, edges, cover):
    """Verify every edge has at least one endpoint in cover."""
    for u, v in edges:
        if u not in cover and v not in cover:
            return False
    return True


def vertex_cover_brute_force(n, edges):
    """
    Exact vertex cover by trying every subset. O(2^n * |E|).
    Only feasible for tiny n. Used to verify the 2-approx bound.
    """
    for k in range(n + 1):
        for subset in itertools.combinations(range(n), k):
            s = set(subset)
            if is_valid_cover(n, edges, s):
                return s
    return set(range(n))  # should never happen


# ---------------------------------------------------------------------------
# 2. Christofides 1.5-Approximation for Metric TSP
# ---------------------------------------------------------------------------

def metric_distance(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def build_distance_matrix(points):
    n = len(points)
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = metric_distance(points[i], points[j])
            d[i][j] = w
            d[j][i] = w
    return d


def mst_prim(n, dist):
    """
    Prim's MST returning adjacency list of tree edges.
    O(n^2) — fine for the sizes we care about.
    """
    in_tree = [False] * n
    key = [math.inf] * n
    parent = [-1] * n
    key[0] = 0

    for _ in range(n):
        # pick min-key vertex not in tree
        u = -1
        best = math.inf
        for v in range(n):
            if not in_tree[v] and key[v] < best:
                best = key[v]
                u = v
        if u == -1:
            break
        in_tree[u] = True
        for v in range(n):
            if not in_tree[v] and dist[u][v] < key[v]:
                key[v] = dist[u][v]
                parent[v] = u

    adj = [[] for _ in range(n)]
    for v in range(1, n):
        u = parent[v]
        adj[u].append(v)
        adj[v].append(u)
    return adj


def odd_degree_vertices(adj):
    return [v for v, nbrs in enumerate(adj) if len(nbrs) % 2 == 1]


def greedy_matching(odd, dist):
    """
    Greedy minimum-weight perfect matching on the odd-degree set.
    Pair the two closest unmatched, repeat.

    Note: this is NOT Edmonds' blossom — so the strict 1.5 bound is lost.
    Empirically very close to optimal on small instances.
    """
    remaining = set(odd)
    matching = []
    while remaining:
        u = next(iter(remaining))
        remaining.remove(u)
        # find closest partner
        best = None
        best_d = math.inf
        for v in remaining:
            if dist[u][v] < best_d:
                best_d = dist[u][v]
                best = v
        if best is not None:
            remaining.remove(best)
            matching.append((u, best))
    return matching


def eulerian_circuit(n, multigraph):
    """
    Hierholzer's algorithm. multigraph: list of sets-with-counts.
    Returns sequence of vertices forming Eulerian circuit from vertex 0.

    We represent multigraph as adjacency dict-of-counts to allow
    duplicate edges from matching ∪ MST.
    """
    # deep copy
    adj = [dict(d) for d in multigraph]
    circuit = []
    stack = [0]
    while stack:
        u = stack[-1]
        if adj[u]:
            v = next(iter(adj[u]))
            adj[u][v] -= 1
            if adj[u][v] == 0:
                del adj[u][v]
            adj[v][u] -= 1
            if adj[v][u] == 0:
                del adj[v][u]
            stack.append(v)
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    return circuit


def shortcut_to_hamiltonian(circuit):
    """Skip already-visited vertices. Triangle inequality => cost can only drop."""
    visited = set()
    tour = []
    for v in circuit:
        if v not in visited:
            visited.add(v)
            tour.append(v)
    tour.append(tour[0])  # close the loop
    return tour


def tour_cost(tour, dist):
    return sum(dist[tour[i]][tour[i + 1]] for i in range(len(tour) - 1))


def christofides(points):
    """
    1.5-approx (in spirit; uses greedy matching) for metric TSP.
    points: list of (x, y).
    Returns (tour, cost).
    """
    n = len(points)
    if n < 2:
        return list(range(n)), 0.0
    dist = build_distance_matrix(points)

    # Step 1: MST
    mst_adj = mst_prim(n, dist)

    # Step 2: odd-degree vertices
    odd = odd_degree_vertices(mst_adj)

    # Step 3: greedy matching on odd set
    matching = greedy_matching(odd, dist)

    # Step 4: combine into multigraph (counts allow duplicate edges)
    multi = [dict() for _ in range(n)]
    for u, nbrs in enumerate(mst_adj):
        for v in nbrs:
            multi[u][v] = multi[u].get(v, 0) + 1
    for u, v in matching:
        multi[u][v] = multi[u].get(v, 0) + 1
        multi[v][u] = multi[v].get(u, 0) + 1

    # Step 5: Eulerian circuit
    euler = eulerian_circuit(n, multi)

    # Step 6: shortcut
    tour = shortcut_to_hamiltonian(euler)
    return tour, tour_cost(tour, dist)


def nearest_neighbor_tsp(points):
    """Baseline: nearest-neighbor heuristic. Often 25% over OPT in practice."""
    n = len(points)
    if n < 2:
        return list(range(n)), 0.0
    dist = build_distance_matrix(points)
    visited = [False] * n
    tour = [0]
    visited[0] = True
    for _ in range(n - 1):
        last = tour[-1]
        best = -1
        best_d = math.inf
        for v in range(n):
            if not visited[v] and dist[last][v] < best_d:
                best_d = dist[last][v]
                best = v
        tour.append(best)
        visited[best] = True
    tour.append(tour[0])
    return tour, tour_cost(tour, dist)


def brute_force_tsp(points):
    """Exact TSP by trying all permutations. O(n!). Only for n <= 9."""
    n = len(points)
    if n < 2:
        return list(range(n)), 0.0
    dist = build_distance_matrix(points)
    best_tour = None
    best_cost = math.inf
    for perm in itertools.permutations(range(1, n)):
        tour = [0] + list(perm) + [0]
        c = tour_cost(tour, dist)
        if c < best_cost:
            best_cost = c
            best_tour = tour
    return best_tour, best_cost


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_vertex_cover():
    print("=" * 60)
    print("DEMO 1: 2-Approximation Vertex Cover")
    print("=" * 60)
    # Small graph, edges define structure.
    # 0 - 1 - 2 - 3, plus 0-2 cross edge.
    n = 6
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (0, 2)]
    cover, matching = vertex_cover_2approx(n, edges)
    print(f"\nGraph: n={n}, {len(edges)} edges")
    print(f"  Matching used: {matching}")
    print(f"  Approx cover:  {sorted(cover)}  (|S|={len(cover)})")
    print(f"  Valid cover?   {is_valid_cover(n, edges, cover)}")

    opt = vertex_cover_brute_force(n, edges)
    print(f"  Optimal cover: {sorted(opt)}  (|OPT|={len(opt)})")
    print(f"  Ratio:         {len(cover) / max(1, len(opt)):.2f} (proven <= 2)")


def demo_christofides():
    print("\n" + "=" * 60)
    print("DEMO 2: Christofides Metric TSP")
    print("=" * 60)

    random.seed(7)
    points = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(8)]

    chr_tour, chr_cost = christofides(points)
    nn_tour, nn_cost = nearest_neighbor_tsp(points)
    bf_tour, bf_cost = brute_force_tsp(points)

    print(f"\n{len(points)} random points in [0,100]^2")
    print(f"  Brute force (OPT):  cost={bf_cost:.2f}")
    print(f"  Christofides:       cost={chr_cost:.2f}  ratio={chr_cost/bf_cost:.3f}")
    print(f"  Nearest neighbor:   cost={nn_cost:.2f}  ratio={nn_cost/bf_cost:.3f}")
    print(f"\n  Christofides tour: {chr_tour}")


def demo_scaling():
    print("\n" + "=" * 60)
    print("DEMO 3: How Approximation Scales")
    print("=" * 60)

    random.seed(42)
    for n in [10, 20, 40]:
        pts = [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(n)]
        _, chr_c = christofides(pts)
        _, nn_c = nearest_neighbor_tsp(pts)
        print(f"  n={n:3d}: Christofides={chr_c:7.2f}  NN={nn_c:7.2f}  "
              f"NN/Chr={nn_c/chr_c:.3f}")


if __name__ == "__main__":
    demo_vertex_cover()
    demo_christofides()
    demo_scaling()
