"""
Day 81: Topological Sort — From Scratch

Two algorithms for ordering vertices so every edge u→v has u before v.
Only works on DAGs. Cycle detection is a natural byproduct.
"""

from collections import defaultdict, deque
import heapq


def make_digraph(edges):
    """Build directed adjacency list."""
    adj = defaultdict(list)
    vertices = set()
    for u, v in edges:
        adj[u].append(v)
        vertices.update([u, v])
    for v in vertices:
        if v not in adj:
            adj[v] = []
    return adj, sorted(vertices)


# ---------------------------------------------------------------------------
# 1. Kahn's Algorithm (BFS-based)
# ---------------------------------------------------------------------------

def kahns_topo_sort(adj, vertices):
    """
    Kahn's algorithm: repeatedly remove vertices with in-degree 0.

    Returns (order, has_cycle):
        order: topological ordering if DAG, partial ordering if cycle
        has_cycle: True if cycle detected
    """
    # Step 1: compute in-degrees
    in_degree = {v: 0 for v in vertices}
    for u in vertices:
        for v in adj[u]:
            in_degree[v] += 1

    # Step 2: enqueue all vertices with in-degree 0
    queue = deque(v for v in vertices if in_degree[v] == 0)
    order = []

    # Step 3: process queue
    while queue:
        u = queue.popleft()
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    # If not all vertices processed, there's a cycle
    has_cycle = len(order) != len(vertices)
    return order, has_cycle


# ---------------------------------------------------------------------------
# 2. DFS-based Topological Sort (Reverse Post-Order)
# ---------------------------------------------------------------------------

WHITE, GRAY, BLACK = 0, 1, 2


def dfs_topo_sort(adj, vertices):
    """
    DFS-based: vertices are added to result in reverse finish order.

    Returns (order, has_cycle):
        order: topological ordering if DAG
        has_cycle: True if back edge found (cycle)
    """
    color = {v: WHITE for v in vertices}
    result = []
    has_cycle = [False]

    def _dfs(u):
        if has_cycle[0]:
            return
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                has_cycle[0] = True  # back edge = cycle
                return
            if color[v] == WHITE:
                _dfs(v)
        color[u] = BLACK
        result.append(u)  # add to result when FINISHED

    for v in vertices:
        if color[v] == WHITE:
            _dfs(v)

    result.reverse()  # reverse post-order
    return result, has_cycle[0]


# ---------------------------------------------------------------------------
# 3. Lexicographic Topological Sort (smallest ordering)
# ---------------------------------------------------------------------------

def lexicographic_topo_sort(adj, vertices):
    """
    Kahn's with a min-heap: always pick the smallest available vertex.
    Useful when you need a deterministic, "canonical" ordering.

    O((V + E) log V) due to heap operations.
    """
    in_degree = {v: 0 for v in vertices}
    for u in vertices:
        for v in adj[u]:
            in_degree[v] += 1

    # Min-heap instead of queue
    heap = [v for v in vertices if in_degree[v] == 0]
    heapq.heapify(heap)
    order = []

    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    has_cycle = len(order) != len(vertices)
    return order, has_cycle


# ---------------------------------------------------------------------------
# 4. Parallel scheduling levels (which tasks can run concurrently?)
# ---------------------------------------------------------------------------

def parallel_levels(adj, vertices):
    """
    Group vertices into levels where all vertices in a level can execute
    in parallel (all their dependencies are in earlier levels).

    This is BFS layer-by-layer — the number of levels is the critical
    path length (longest chain of dependencies).
    """
    in_degree = {v: 0 for v in vertices}
    for u in vertices:
        for v in adj[u]:
            in_degree[v] += 1

    current_level = [v for v in vertices if in_degree[v] == 0]
    levels = []

    while current_level:
        levels.append(sorted(current_level))
        next_level = []
        for u in current_level:
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    next_level.append(v)
        current_level = next_level

    processed = sum(len(level) for level in levels)
    has_cycle = processed != len(vertices)
    return levels, has_cycle


# ---------------------------------------------------------------------------
# 5. Find one cycle (for error reporting)
# ---------------------------------------------------------------------------

def find_cycle(adj, vertices):
    """
    If the graph has a cycle, return it as a list of vertices.
    Useful for error messages: "circular dependency: A → B → C → A"
    """
    color = {v: WHITE for v in vertices}
    parent = {}

    def _dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                # Reconstruct cycle from v back to v
                cycle = [v]
                node = u
                while node != v:
                    cycle.append(node)
                    node = parent[node]
                cycle.append(v)
                cycle.reverse()
                return cycle
            if color[v] == WHITE:
                parent[v] = u
                result = _dfs(v)
                if result:
                    return result
        color[u] = BLACK
        return None

    for v in vertices:
        if color[v] == WHITE:
            cycle = _dfs(v)
            if cycle:
                return cycle
    return None


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Basic Topological Sort")
    print("=" * 60)

    # Course prerequisites: 0→1, 0→2, 1→3, 2→3
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    adj, verts = make_digraph(edges)

    print(f"\nDAG: {edges}")
    print(f"(0 and 2 are prerequisites for their targets)")

    kahn_order, cycle = kahns_topo_sort(adj, verts)
    print(f"\nKahn's algorithm:     {kahn_order}  (cycle: {cycle})")

    dfs_order, cycle = dfs_topo_sort(adj, verts)
    print(f"DFS reverse post-ord: {dfs_order}  (cycle: {cycle})")

    lex_order, cycle = lexicographic_topo_sort(adj, verts)
    print(f"Lexicographic:        {lex_order}  (cycle: {cycle})")


def demo_cycle():
    print("\n" + "=" * 60)
    print("DEMO 2: Cycle Detection")
    print("=" * 60)

    # Circular dependency: A→B→C→A
    edges = [("A", "B"), ("B", "C"), ("C", "A"), ("A", "D")]
    adj, verts = make_digraph(edges)

    print(f"\nGraph with cycle: A→B→C→A, A→D")

    kahn_order, cycle = kahns_topo_sort(adj, verts)
    print(f"\nKahn's: processed {len(kahn_order)}/{len(verts)} vertices")
    print(f"  Cycle detected: {cycle}")

    dfs_order, cycle = dfs_topo_sort(adj, verts)
    print(f"DFS: cycle detected: {cycle}")

    cycle_path = find_cycle(adj, verts)
    print(f"Cycle path: {' → '.join(str(v) for v in cycle_path)}")


def demo_build_system():
    print("\n" + "=" * 60)
    print("DEMO 3: Build System — Parallel Scheduling")
    print("=" * 60)

    # Simulated build dependencies
    deps = [
        ("parse", "typecheck"),
        ("parse", "lint"),
        ("typecheck", "optimize"),
        ("lint", "optimize"),
        ("optimize", "codegen"),
        ("codegen", "link"),
        ("stdlib", "link"),
    ]
    adj, verts = make_digraph(deps)

    print(f"\nBuild dependencies:")
    for u, v in deps:
        print(f"  {u} → {v}")

    order, _ = lexicographic_topo_sort(adj, verts)
    print(f"\nSequential build order: {order}")

    levels, _ = parallel_levels(adj, verts)
    print(f"\nParallel schedule ({len(levels)} levels):")
    for i, level in enumerate(levels):
        print(f"  Level {i}: {level}  (run in parallel)")
    print(f"\nCritical path length: {len(levels)} steps")
    print(f"Sequential would take: {len(verts)} steps")
    print(f"Speedup: {len(verts)/len(levels):.1f}x")


def demo_comparison():
    print("\n" + "=" * 60)
    print("DEMO 4: Kahn's vs DFS ordering differences")
    print("=" * 60)

    # Diamond pattern with extra edges — multiple valid orderings
    edges = [(1, 3), (1, 4), (2, 4), (2, 5), (3, 6), (4, 6), (5, 6)]
    adj, verts = make_digraph(edges)

    print(f"\nDiamond DAG: {edges}")

    kahn_order, _ = kahns_topo_sort(adj, verts)
    dfs_order, _ = dfs_topo_sort(adj, verts)
    lex_order, _ = lexicographic_topo_sort(adj, verts)

    print(f"\nKahn's (FIFO):        {kahn_order}")
    print(f"DFS (reverse post):   {dfs_order}")
    print(f"Lexicographic (heap): {lex_order}")

    # Verify all are valid topological orders
    for name, order in [("Kahn's", kahn_order), ("DFS", dfs_order),
                        ("Lex", lex_order)]:
        pos = {v: i for i, v in enumerate(order)}
        valid = all(pos[u] < pos[v] for u in adj for v in adj[u])
        print(f"  {name} valid: {valid}")


if __name__ == "__main__":
    demo_basic()
    demo_cycle()
    demo_build_system()
    demo_comparison()
