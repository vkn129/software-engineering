"""
Day 90: Network Flow — From Scratch

Edmonds-Karp (BFS-based max flow), min cut finding, and bipartite matching
reduced to max flow. All built on the residual graph abstraction.
"""

from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# 1. Edmonds-Karp Algorithm (BFS-based Max Flow)
# ---------------------------------------------------------------------------

def edmonds_karp(capacity, source, sink):
    """
    Find maximum flow from source to sink using Edmonds-Karp (BFS augmenting paths).

    Args:
        capacity: dict of dict, capacity[u][v] = edge capacity (0 if no edge)
        source: source vertex
        sink: sink vertex

    Returns:
        (max_flow_value, flow_dict) where flow_dict[u][v] = flow on edge u->v

    Time: O(VE^2) — at most O(VE) augmentations, each BFS is O(E).
    """
    # Build residual capacity graph (modifiable copy)
    # We need all vertices that appear in capacity
    vertices = set()
    for u in capacity:
        vertices.add(u)
        for v in capacity[u]:
            vertices.add(v)

    residual = defaultdict(lambda: defaultdict(int))
    for u in capacity:
        for v in capacity[u]:
            residual[u][v] += capacity[u][v]

    # Track flow on original edges
    flow = defaultdict(lambda: defaultdict(int))

    total_flow = 0

    while True:
        # BFS to find shortest augmenting path in residual graph
        parent = {source: None}
        visited = {source}
        queue = deque([source])

        while queue:
            u = queue.popleft()
            if u == sink:
                break
            for v in vertices:
                if v not in visited and residual[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)

        if sink not in parent:
            break  # No augmenting path — we're done

        # Find bottleneck along the path
        bottleneck = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            bottleneck = min(bottleneck, residual[u][v])
            v = u

        # Update residual capacities and flow along the path
        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
            flow[u][v] += bottleneck
            flow[v][u] -= bottleneck
            v = u

        total_flow += bottleneck

    # Clean up flow dict: only keep positive flows
    clean_flow = {}
    for u in flow:
        for v in flow[u]:
            if flow[u][v] > 0:
                if u not in clean_flow:
                    clean_flow[u] = {}
                clean_flow[u][v] = flow[u][v]

    return total_flow, clean_flow


# ---------------------------------------------------------------------------
# 2. Min Cut Finding
# ---------------------------------------------------------------------------

def find_min_cut(capacity, source, sink):
    """
    Find the minimum s-t cut using max flow.

    After computing max flow, BFS from source in the residual graph.
    Reachable vertices form set S, unreachable form set T.
    Cut edges are those from S to T with positive capacity in the original graph.

    Returns:
        (max_flow_value, S_set, T_set, cut_edges)
        where cut_edges is list of (u, v, capacity) tuples
    """
    # Collect all vertices
    vertices = set()
    for u in capacity:
        vertices.add(u)
        for v in capacity[u]:
            vertices.add(v)

    # Build residual graph and run Edmonds-Karp
    residual = defaultdict(lambda: defaultdict(int))
    for u in capacity:
        for v in capacity[u]:
            residual[u][v] += capacity[u][v]

    total_flow = 0

    while True:
        parent = {source: None}
        visited = {source}
        queue = deque([source])

        while queue:
            u = queue.popleft()
            if u == sink:
                break
            for v in vertices:
                if v not in visited and residual[u][v] > 0:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)

        if sink not in parent:
            break

        bottleneck = float('inf')
        v = sink
        while v != source:
            u = parent[v]
            bottleneck = min(bottleneck, residual[u][v])
            v = u

        v = sink
        while v != source:
            u = parent[v]
            residual[u][v] -= bottleneck
            residual[v][u] += bottleneck
            v = u

        total_flow += bottleneck

    # BFS from source in residual graph to find reachable set S
    s_set = set()
    queue = deque([source])
    s_set.add(source)
    while queue:
        u = queue.popleft()
        for v in vertices:
            if v not in s_set and residual[u][v] > 0:
                s_set.add(v)
                queue.append(v)

    t_set = vertices - s_set

    # Find cut edges: from S to T with positive original capacity
    cut_edges = []
    for u in s_set:
        if u in capacity:
            for v in capacity[u]:
                if v in t_set and capacity[u][v] > 0:
                    cut_edges.append((u, v, capacity[u][v]))

    return total_flow, s_set, t_set, cut_edges


# ---------------------------------------------------------------------------
# 3. Bipartite Matching via Max Flow Reduction
# ---------------------------------------------------------------------------

def max_bipartite_matching_flow(left, right, edges):
    """
    Find maximum bipartite matching by reducing to max flow.

    Creates a flow network:
    - Super-source S connected to all left vertices (capacity 1)
    - All right vertices connected to super-sink T (capacity 1)
    - Each edge (u, v) from left to right (capacity 1)

    Max flow = max matching size.

    Args:
        left: list of left vertex labels
        right: list of right vertex labels
        edges: list of (left_vertex, right_vertex) pairs

    Returns:
        (matching_size, matching_dict) where matching_dict maps left -> right
    """
    source = "__source__"
    sink = "__sink__"

    capacity = defaultdict(lambda: defaultdict(int))

    # Source -> left vertices
    for u in left:
        capacity[source][u] = 1

    # Right vertices -> sink
    for v in right:
        capacity[v][sink] = 1

    # Left -> right edges
    for u, v in edges:
        capacity[u][v] = 1

    max_flow, flow = edmonds_karp(capacity, source, sink)

    # Extract matching from flow
    matching = {}
    for u in left:
        if u in flow:
            for v in flow[u]:
                if v in set(right) and flow[u][v] > 0:
                    matching[u] = v

    return max_flow, matching


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic_max_flow():
    print("=" * 60)
    print("DEMO 1: Basic Max Flow (Edmonds-Karp)")
    print("=" * 60)

    # Build a flow network:
    #
    #     A --10--> B
    #    / \        |  \
    #   8   4       6   10
    #  /     \      |     \
    # s       C -+  v      t
    #  \     /  |   D ----/
    #   6   /   +-> |   7
    #    \ /   9    |  /
    #     E -------/
    #         8

    capacity = {
        's': {'A': 8, 'E': 6},
        'A': {'B': 10, 'C': 4},
        'B': {'D': 6, 't': 10},
        'C': {'D': 9},
        'D': {'t': 7},
        'E': {'C': 3, 'D': 8},
    }

    max_flow, flow = edmonds_karp(capacity, 's', 't')

    print(f"\nNetwork:")
    print(f"  s -> A (cap 8), s -> E (cap 6)")
    print(f"  A -> B (cap 10), A -> C (cap 4)")
    print(f"  B -> D (cap 6), B -> t (cap 10)")
    print(f"  C -> D (cap 9)")
    print(f"  D -> t (cap 7)")
    print(f"  E -> C (cap 3), E -> D (cap 8)")

    print(f"\nMaximum flow: {max_flow}")

    print(f"\nFlow on each edge:")
    for u in sorted(flow.keys()):
        for v in sorted(flow[u].keys()):
            print(f"  {u} -> {v}: {flow[u][v]}")

    # Verify flow conservation
    all_verts = set()
    for u in capacity:
        all_verts.add(u)
        for v in capacity[u]:
            all_verts.add(v)

    print(f"\nFlow conservation check:")
    for v in sorted(all_verts):
        if v in ('s', 't'):
            continue
        inflow = sum(flow.get(u, {}).get(v, 0) for u in all_verts)
        outflow = sum(flow.get(v, {}).get(w, 0) for w in all_verts)
        status = "OK" if inflow == outflow else "VIOLATED"
        print(f"  {v}: in={inflow}, out={outflow} [{status}]")


def demo_min_cut():
    print("\n" + "=" * 60)
    print("DEMO 2: Min Cut Finding")
    print("=" * 60)

    # Simple network where the min cut is easy to verify
    #
    #     A --3--> B
    #    /          \
    #   4            2
    #  /              \
    # s                t
    #  \              /
    #   5            3
    #    \          /
    #     C --4--> D

    capacity = {
        's': {'A': 4, 'C': 5},
        'A': {'B': 3},
        'B': {'t': 2},
        'C': {'D': 4},
        'D': {'t': 3},
    }

    max_flow, s_set, t_set, cut_edges = find_min_cut(capacity, 's', 't')

    print(f"\nNetwork:")
    for u in sorted(capacity.keys()):
        for v in sorted(capacity[u].keys()):
            print(f"  {u} -> {v} (cap {capacity[u][v]})")

    print(f"\nMax flow = Min cut = {max_flow}")

    print(f"\nPartition:")
    print(f"  S (source side): {sorted(s_set)}")
    print(f"  T (sink side):   {sorted(t_set)}")

    print(f"\nCut edges (crossing from S to T):")
    total_cut = 0
    for u, v, cap in cut_edges:
        print(f"  {u} -> {v} (cap {cap})")
        total_cut += cap
    print(f"  Total cut capacity: {total_cut}")

    # Visual partition
    print(f"\nVisualization:")
    print(f"  [{' '.join(sorted(s_set))}]  ||CUT||  [{' '.join(sorted(t_set))}]")


def demo_bipartite_matching():
    print("\n" + "=" * 60)
    print("DEMO 3: Bipartite Matching via Max Flow")
    print("=" * 60)

    # Workers and tasks
    workers = ["W1", "W2", "W3", "W4"]
    tasks = ["T1", "T2", "T3", "T4"]
    skills = [
        ("W1", "T1"), ("W1", "T2"),
        ("W2", "T1"), ("W2", "T3"),
        ("W3", "T2"), ("W3", "T4"),
        ("W4", "T3"), ("W4", "T4"),
    ]

    print(f"\nWorkers: {workers}")
    print(f"Tasks:   {tasks}")
    print(f"Skills:  {skills}")

    size, matching = max_bipartite_matching_flow(workers, tasks, skills)

    print(f"\nMaximum matching size: {size}")
    print(f"Assignment:")
    for w in sorted(matching.keys()):
        print(f"  {w} -> {matching[w]}")

    # Compare: all workers matched?
    unmatched = [w for w in workers if w not in matching]
    if unmatched:
        print(f"Unmatched workers: {unmatched}")
    else:
        print(f"All workers matched!")


def demo_network_routing():
    print("\n" + "=" * 60)
    print("DEMO 4: Network Routing Capacity Analysis")
    print("=" * 60)

    # Simulate a network of routers with link bandwidths (Gbps)
    #
    # HQ ----10----> R1 ----5----> R3 ----8----> DC
    #   \            |  \          ^            /
    #    \           3   7        6           /
    #     \          |    \      /           /
    #      +--8---> R2 ----4--> R4 ---10---+
    #

    capacity = {
        'HQ': {'R1': 10, 'R2': 8},
        'R1': {'R3': 5, 'R2': 3, 'R4': 7},
        'R2': {'R4': 4},
        'R3': {'DC': 8},
        'R4': {'R3': 6, 'DC': 10},
    }

    max_bw, flow = edmonds_karp(capacity, 'HQ', 'DC')
    _, s_set, t_set, bottleneck_links = find_min_cut(capacity, 'HQ', 'DC')

    print(f"\nNetwork topology (bandwidths in Gbps):")
    for u in sorted(capacity.keys()):
        for v in sorted(capacity[u].keys()):
            print(f"  {u} -> {v}: {capacity[u][v]} Gbps")

    print(f"\nMaximum throughput HQ -> DC: {max_bw} Gbps")

    print(f"\nTraffic distribution:")
    for u in sorted(flow.keys()):
        for v in sorted(flow[u].keys()):
            cap = capacity.get(u, {}).get(v, 0)
            util = (flow[u][v] / cap * 100) if cap > 0 else 0
            print(f"  {u} -> {v}: {flow[u][v]}/{cap} Gbps ({util:.0f}% utilized)")

    print(f"\nBottleneck links (min cut):")
    for u, v, cap in bottleneck_links:
        print(f"  {u} -> {v}: {cap} Gbps")
    print(f"  Upgrading these links would increase max throughput")

    print(f"\nVulnerability analysis:")
    print(f"  Source side: {sorted(s_set)}")
    print(f"  Sink side:   {sorted(t_set)}")
    print(f"  Cutting {len(bottleneck_links)} link(s) disconnects HQ from DC")


# ---------------------------------------------------------------------------
# Run all demos
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo_basic_max_flow()
    demo_min_cut()
    demo_bipartite_matching()
    demo_network_routing()
