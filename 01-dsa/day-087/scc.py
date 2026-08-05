"""
Day 87: Strongly Connected Components — From Scratch

Two algorithms to find maximal groups where every vertex can reach every other.
Kosaraju's (two-pass DFS) and Tarjan's (single-pass with low-link values).
"""

from collections import defaultdict


def make_digraph(edges, vertices=None):
    """Build directed adjacency list."""
    adj = defaultdict(list)
    vset = set()
    for u, v in edges:
        adj[u].append(v)
        vset.update([u, v])
    if vertices:
        vset.update(vertices)
    for v in vset:
        if v not in adj:
            adj[v] = []
    return adj, sorted(vset)


# ---------------------------------------------------------------------------
# 1. Kosaraju's Algorithm (Two-Pass DFS)
# ---------------------------------------------------------------------------

def kosaraju(adj, vertices):
    """
    Find SCCs using two DFS passes:
    1. DFS on original graph → record finish order
    2. DFS on transposed graph in reverse finish order → each tree is an SCC

    Returns list of SCCs (each SCC is a list of vertices).
    """
    # Pass 1: DFS on original graph, record finish order
    visited = set()
    finish_stack = []

    def dfs1(u):
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                dfs1(v)
        finish_stack.append(u)

    for v in vertices:
        if v not in visited:
            dfs1(v)

    # Build transposed graph
    adj_t = defaultdict(list)
    for u in vertices:
        adj_t[u]  # ensure all vertices exist
    for u in adj:
        for v in adj[u]:
            adj_t[v].append(u)

    # Pass 2: DFS on transposed graph in reverse finish order
    visited.clear()
    sccs = []

    def dfs2(u, component):
        visited.add(u)
        component.append(u)
        for v in adj_t[u]:
            if v not in visited:
                dfs2(v, component)

    while finish_stack:
        v = finish_stack.pop()
        if v not in visited:
            component = []
            dfs2(v, component)
            sccs.append(component)

    return sccs


# ---------------------------------------------------------------------------
# 2. Tarjan's Algorithm (Single-Pass DFS)
# ---------------------------------------------------------------------------

def tarjan(adj, vertices):
    """
    Find SCCs in a single DFS pass using discovery times and low-link values.

    disc[u]: when u was discovered
    low[u]: earliest discovery time reachable from u's subtree

    When low[u] == disc[u], u is the root of an SCC — pop the stack.

    Returns list of SCCs (each SCC is a list of vertices).
    """
    disc = {}
    low = {}
    on_stack = set()
    stack = []
    time = [0]
    sccs = []

    def dfs(u):
        disc[u] = low[u] = time[0]
        time[0] += 1
        stack.append(u)
        on_stack.add(u)

        for v in adj[u]:
            if v not in disc:
                dfs(v)
                low[u] = min(low[u], low[v])
            elif v in on_stack:
                low[u] = min(low[u], disc[v])

        # If u is root of an SCC
        if low[u] == disc[u]:
            component = []
            while True:
                v = stack.pop()
                on_stack.remove(v)
                component.append(v)
                if v == u:
                    break
            sccs.append(component)

    for v in vertices:
        if v not in disc:
            dfs(v)

    return sccs


# ---------------------------------------------------------------------------
# 3. Condensation DAG
# ---------------------------------------------------------------------------

def condensation(adj, vertices):
    """
    Build the condensation DAG: collapse each SCC to a single super-vertex.

    Returns:
        scc_list: list of SCCs
        scc_id: dict mapping vertex → SCC index
        dag: adjacency list of the condensation DAG
    """
    sccs = tarjan(adj, vertices)

    # Map each vertex to its SCC index
    scc_id = {}
    for i, scc in enumerate(sccs):
        for v in scc:
            scc_id[v] = i

    # Build DAG edges (no duplicates, no self-loops)
    dag = defaultdict(set)
    for u in adj:
        for v in adj[u]:
            su, sv = scc_id[u], scc_id[v]
            if su != sv:
                dag[su].add(sv)

    # Convert sets to lists
    dag = {k: list(v) for k, v in dag.items()}

    return sccs, scc_id, dag


# ---------------------------------------------------------------------------
# 4. 2-SAT Solver (SCC-based)
# ---------------------------------------------------------------------------

def solve_2sat(n, clauses):
    """
    Solve a 2-SAT instance using SCC.

    n: number of variables (x_0 to x_{n-1})
    clauses: list of (a, b) where a, b are literals
             positive i means x_i, negative ~i means NOT x_i
             (using ~i = -i-1 for 0-indexed)

    Returns: satisfying assignment as list of bools, or None if unsatisfiable.

    Encoding: variable x_i → vertex 2*i, NOT x_i → vertex 2*i+1
    Clause (a OR b) → implication (NOT a → b) AND (NOT b → a)
    """
    # Build implication graph
    def lit_to_vertex(lit):
        if lit >= 0:
            return 2 * lit      # x_i
        else:
            return 2 * (~lit) + 1  # NOT x_i

    def negate_vertex(v):
        return v ^ 1  # flip last bit: x_i ↔ NOT x_i

    num_vertices = 2 * n
    adj = defaultdict(list)
    verts = list(range(num_vertices))
    for v in verts:
        adj[v] = []

    for a, b in clauses:
        va, vb = lit_to_vertex(a), lit_to_vertex(b)
        # (a OR b) → (NOT a → b) AND (NOT b → a)
        adj[negate_vertex(va)].append(vb)
        adj[negate_vertex(vb)].append(va)

    # Find SCCs
    sccs = tarjan(adj, verts)
    scc_id = {}
    for i, scc in enumerate(sccs):
        for v in scc:
            scc_id[v] = i

    # Check satisfiability: x_i and NOT x_i must be in different SCCs
    for i in range(n):
        if scc_id[2 * i] == scc_id[2 * i + 1]:
            return None  # unsatisfiable

    # Assign values: variable is TRUE if its SCC comes after NOT's SCC
    # (Tarjan produces SCCs in reverse topological order)
    assignment = []
    for i in range(n):
        # In Tarjan's output, earlier index = later in topo order
        assignment.append(scc_id[2 * i] < scc_id[2 * i + 1])

    return assignment


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic():
    print("=" * 60)
    print("DEMO 1: Finding SCCs — Kosaraju's vs Tarjan's")
    print("=" * 60)

    edges = [
        (0, 1), (1, 2), (2, 0),   # SCC: {0, 1, 2}
        (2, 3),                     # bridge to next SCC
        (3, 4), (4, 5), (5, 3),   # SCC: {3, 4, 5}
        (5, 6),                     # bridge
        (6, 7), (7, 6),           # SCC: {6, 7}
    ]
    adj, verts = make_digraph(edges)

    print(f"\nEdges: {edges}")

    k_sccs = kosaraju(adj, verts)
    print(f"\nKosaraju's SCCs ({len(k_sccs)}):")
    for i, scc in enumerate(k_sccs):
        print(f"  SCC {i}: {sorted(scc)}")

    t_sccs = tarjan(adj, verts)
    print(f"\nTarjan's SCCs ({len(t_sccs)}):")
    for i, scc in enumerate(t_sccs):
        print(f"  SCC {i}: {sorted(scc)}")


def demo_condensation():
    print("\n" + "=" * 60)
    print("DEMO 2: Condensation DAG")
    print("=" * 60)

    edges = [
        (0, 1), (1, 0),   # SCC A: {0, 1}
        (1, 2),            # A → B
        (2, 3), (3, 2),   # SCC B: {2, 3}
        (3, 4),            # B → C
        (4, 5), (5, 4),   # SCC C: {4, 5}
    ]
    adj, verts = make_digraph(edges)

    sccs, scc_id, dag = condensation(adj, verts)

    print(f"\nOriginal: {edges}")
    print(f"\nSCCs:")
    for i, scc in enumerate(sccs):
        print(f"  Super-vertex {i}: {sorted(scc)}")

    print(f"\nCondensation DAG (always a DAG!):")
    for u in sorted(dag.keys()):
        for v in dag[u]:
            print(f"  {u} → {v}")


def demo_web_graph():
    print("\n" + "=" * 60)
    print("DEMO 3: Web Graph Analysis")
    print("=" * 60)

    # Simulated web link structure
    pages = ["home", "about", "blog", "post1", "post2",
             "shop", "cart", "checkout", "external"]
    idx = {p: i for i, p in enumerate(pages)}

    links = [
        ("home", "about"), ("about", "home"),       # mutual links
        ("home", "blog"), ("blog", "home"),          # mutual links
        ("blog", "post1"), ("blog", "post2"),
        ("post1", "blog"), ("post2", "blog"),        # posts link back
        ("home", "shop"), ("shop", "cart"),
        ("cart", "checkout"), ("checkout", "shop"),  # shopping cycle
        ("post1", "external"),                        # outbound link
    ]

    edges = [(idx[u], idx[v]) for u, v in links]
    adj, verts = make_digraph(edges, list(range(len(pages))))

    sccs = tarjan(adj, verts)

    print(f"\nWeb pages and their SCCs:")
    for scc in sccs:
        names = [pages[v] for v in sorted(scc)]
        if len(names) > 1:
            print(f"  Mutual cluster: {names}")
        else:
            print(f"  Standalone: {names}")

    print(f"\nInsight: mutually-linked pages form natural site 'sections'")


def demo_2sat():
    print("\n" + "=" * 60)
    print("DEMO 4: 2-SAT Solver")
    print("=" * 60)

    # (x0 OR x1) AND (NOT x0 OR x2) AND (NOT x1 OR NOT x2)
    # Literals: x_i = i, NOT x_i = ~i = -i-1
    clauses = [
        (0, 1),      # x0 OR x1
        (~0, 2),     # NOT x0 OR x2
        (~1, ~2),    # NOT x1 OR NOT x2
    ]

    result = solve_2sat(3, clauses)
    print(f"\nClauses: (x0 OR x1) AND (NOT x0 OR x2) AND (NOT x1 OR NOT x2)")

    if result:
        print(f"Satisfiable! Assignment: x0={result[0]}, x1={result[1]}, x2={result[2]}")
        # Verify
        c1 = result[0] or result[1]
        c2 = (not result[0]) or result[2]
        c3 = (not result[1]) or (not result[2])
        print(f"Verification: ({c1}) AND ({c2}) AND ({c3}) = {c1 and c2 and c3}")
    else:
        print("Unsatisfiable!")

    # Unsatisfiable example: (x0) AND (NOT x0) = (x0 OR x0) AND (NOT x0 OR NOT x0)
    clauses2 = [(0, 0), (~0, ~0)]
    result2 = solve_2sat(1, clauses2)
    print(f"\nClauses: (x0 OR x0) AND (NOT x0 OR NOT x0)")
    print(f"Result: {'Satisfiable' if result2 else 'Unsatisfiable'}")


if __name__ == "__main__":
    demo_basic()
    demo_condensation()
    demo_web_graph()
    demo_2sat()
