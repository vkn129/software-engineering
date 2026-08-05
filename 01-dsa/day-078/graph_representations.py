"""
Day 78: Graph Representations — From Scratch

Four ways to store the same graph, each with different performance trade-offs.
The choice of representation determines algorithm efficiency.
"""

import sys
import time
from collections import defaultdict


# ---------------------------------------------------------------------------
# 1. Adjacency List  — O(V + E) space, fast neighbor iteration
# ---------------------------------------------------------------------------

class AdjacencyListGraph:
    """Default choice for sparse graphs (most real-world graphs)."""

    def __init__(self, directed=False):
        self.adj = defaultdict(list)   # vertex -> [(neighbor, weight), ...]
        self.directed = directed
        self._vertices = set()

    def add_vertex(self, v):
        self._vertices.add(v)
        if v not in self.adj:
            self.adj[v]  # trigger defaultdict creation

    def add_edge(self, u, v, weight=1):
        self._vertices.update([u, v])
        self.adj[u].append((v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    def has_edge(self, u, v):
        """O(degree(u)) — must scan neighbor list."""
        return any(neighbor == v for neighbor, _ in self.adj[u])

    def neighbors(self, u):
        """O(degree(u)) — just return the list."""
        return [(v, w) for v, w in self.adj[u]]

    def vertices(self):
        return self._vertices

    def edge_count(self):
        total = sum(len(neighbors) for neighbors in self.adj.values())
        return total if self.directed else total // 2

    def __repr__(self):
        lines = []
        for v in sorted(self._vertices):
            nbrs = ", ".join(f"{n}(w={w})" for n, w in sorted(self.adj[v]))
            lines.append(f"  {v}: [{nbrs}]")
        return "AdjacencyListGraph:\n" + "\n".join(lines)


# ---------------------------------------------------------------------------
# 2. Adjacency Matrix  — O(V^2) space, O(1) edge check
# ---------------------------------------------------------------------------

class AdjacencyMatrixGraph:
    """Best for dense graphs or when you need O(1) edge existence checks."""

    def __init__(self, num_vertices, directed=False):
        self.n = num_vertices
        self.directed = directed
        # None means no edge; a number means edge weight
        self.matrix = [[None] * num_vertices for _ in range(num_vertices)]

    def add_edge(self, u, v, weight=1):
        self.matrix[u][v] = weight
        if not self.directed:
            self.matrix[v][u] = weight

    def has_edge(self, u, v):
        """O(1) — direct index lookup. This is the matrix's superpower."""
        return self.matrix[u][v] is not None

    def neighbors(self, u):
        """O(V) — must scan entire row, even if vertex has only 2 neighbors."""
        result = []
        for v in range(self.n):
            if self.matrix[u][v] is not None:
                result.append((v, self.matrix[u][v]))
        return result

    def vertices(self):
        return set(range(self.n))

    def edge_count(self):
        count = sum(1 for i in range(self.n) for j in range(self.n)
                    if self.matrix[i][j] is not None)
        return count if self.directed else count // 2

    def __repr__(self):
        header = "    " + "  ".join(f"{i:>3}" for i in range(self.n))
        rows = []
        for i in range(self.n):
            cells = []
            for j in range(self.n):
                val = self.matrix[i][j]
                cells.append(f"{val:>3}" if val is not None else "  .")
            rows.append(f"{i:>3} " + "  ".join(cells))
        return "AdjacencyMatrixGraph:\n" + header + "\n" + "\n".join(rows)


# ---------------------------------------------------------------------------
# 3. Edge List  — O(E) space, ideal for Kruskal's MST
# ---------------------------------------------------------------------------

class EdgeListGraph:
    """Just a list of edges. Simple, compact, perfect for edge-centric algorithms."""

    def __init__(self, directed=False):
        self.edges = []           # [(u, v, weight), ...]
        self.directed = directed
        self._vertices = set()

    def add_vertex(self, v):
        self._vertices.add(v)

    def add_edge(self, u, v, weight=1):
        self._vertices.update([u, v])
        self.edges.append((u, v, weight))

    def has_edge(self, u, v):
        """O(E) — linear scan. Slow, but this isn't what edge lists are for."""
        for eu, ev, _ in self.edges:
            if eu == u and ev == v:
                return True
            if not self.directed and eu == v and ev == u:
                return True
        return False

    def neighbors(self, u):
        """O(E) — must scan all edges."""
        result = []
        for eu, ev, w in self.edges:
            if eu == u:
                result.append((ev, w))
            elif not self.directed and ev == u:
                result.append((eu, w))
        return result

    def vertices(self):
        return self._vertices

    def sorted_edges(self):
        """The reason edge lists exist: sort by weight for Kruskal's."""
        return sorted(self.edges, key=lambda e: e[2])

    def __repr__(self):
        edge_strs = [f"({u}->{v}, w={w})" for u, v, w in self.edges]
        return f"EdgeListGraph: [{', '.join(edge_strs)}]"


# ---------------------------------------------------------------------------
# Conversion between representations
# ---------------------------------------------------------------------------

def adj_list_to_matrix(graph):
    """Convert adjacency list to adjacency matrix."""
    vertices = sorted(graph.vertices())
    v_to_idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    mat = AdjacencyMatrixGraph(n, directed=graph.directed)
    for u in vertices:
        for v, w in graph.adj[u]:
            # Only add once for undirected (add_edge handles symmetry)
            if graph.directed or v_to_idx[u] < v_to_idx[v]:
                mat.add_edge(v_to_idx[u], v_to_idx[v], w)
    return mat, v_to_idx


def adj_list_to_edge_list(graph):
    """Convert adjacency list to edge list."""
    el = EdgeListGraph(directed=graph.directed)
    seen = set()
    for u in graph.vertices():
        for v, w in graph.adj[u]:
            edge_key = (u, v) if graph.directed else (min(u, v), max(u, v))
            if edge_key not in seen:
                el.add_edge(u, v, w)
                seen.add(edge_key)
    return el


def edge_list_to_adj_list(graph):
    """Convert edge list to adjacency list."""
    al = AdjacencyListGraph(directed=graph.directed)
    for v in graph.vertices():
        al.add_vertex(v)
    for u, v, w in graph.edges:
        al.add_edge(u, v, w)
    return al


def matrix_to_adj_list(graph):
    """Convert adjacency matrix to adjacency list."""
    al = AdjacencyListGraph(directed=graph.directed)
    for u in range(graph.n):
        al.add_vertex(u)
        for v in range(graph.n):
            if graph.matrix[u][v] is not None:
                if graph.directed or u < v:
                    al.add_edge(u, v, graph.matrix[u][v])
    return al


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_build_same_graph():
    """Build identical graph in all 3 representations."""
    print("=" * 60)
    print("DEMO: Same graph in 3 representations")
    print("=" * 60)

    # Undirected graph: 0--1, 0--2, 1--3, 2--3 (all weight 1)
    edges = [(0, 1, 1), (0, 2, 1), (1, 3, 1), (2, 3, 1)]

    al = AdjacencyListGraph()
    for u, v, w in edges:
        al.add_edge(u, v, w)
    print(f"\n{al}")

    am = AdjacencyMatrixGraph(4)
    for u, v, w in edges:
        am.add_edge(u, v, w)
    print(f"\n{am}")

    el = EdgeListGraph()
    for u, v, w in edges:
        el.add_edge(u, v, w)
    print(f"\n{el}")

    print(f"\nAll have {al.edge_count()} edges (adj list), "
          f"{am.edge_count()} (matrix), {len(el.edges)} (edge list)")


def demo_edge_check_performance():
    """Compare edge existence check speed across representations."""
    print("\n" + "=" * 60)
    print("DEMO: Edge existence check — O(1) vs O(deg) vs O(E)")
    print("=" * 60)

    n = 500
    # Build a moderately dense graph
    al = AdjacencyListGraph()
    am = AdjacencyMatrixGraph(n)
    el = EdgeListGraph()

    import random
    random.seed(42)
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < 0.1:  # ~10% density
                al.add_edge(u, v)
                am.add_edge(u, v)
                el.add_edge(u, v)

    checks = [(random.randint(0, n - 1), random.randint(0, n - 1))
              for _ in range(10000)]

    # Time adjacency list
    start = time.perf_counter()
    for u, v in checks:
        al.has_edge(u, v)
    al_time = time.perf_counter() - start

    # Time adjacency matrix
    start = time.perf_counter()
    for u, v in checks:
        am.has_edge(u, v)
    am_time = time.perf_counter() - start

    # Time edge list
    start = time.perf_counter()
    for u, v in checks:
        el.has_edge(u, v)
    el_time = time.perf_counter() - start

    print(f"\n10,000 edge checks on {n}-vertex graph (~10% density):")
    print(f"  Adjacency List:   {al_time:.4f}s  (O(degree) per check)")
    print(f"  Adjacency Matrix: {am_time:.4f}s  (O(1) per check)")
    print(f"  Edge List:        {el_time:.4f}s  (O(E) per check)")
    print(f"\n  Matrix is {al_time/am_time:.1f}x faster than list, "
          f"{el_time/am_time:.1f}x faster than edge list")


def demo_space_comparison():
    """Compare memory usage: sparse vs dense graphs."""
    print("\n" + "=" * 60)
    print("DEMO: Space usage — sparse vs dense")
    print("=" * 60)

    for label, n, density in [("Sparse (1%)", 1000, 0.01),
                               ("Medium (10%)", 1000, 0.10),
                               ("Dense (50%)", 1000, 0.50)]:
        al = AdjacencyListGraph()
        am = AdjacencyMatrixGraph(n)

        import random
        random.seed(42)
        edge_count = 0
        for u in range(n):
            al.add_vertex(u)
            for v in range(u + 1, n):
                if random.random() < density:
                    al.add_edge(u, v)
                    am.add_edge(u, v)
                    edge_count += 1

        al_size = sys.getsizeof(al.adj) + sum(
            sys.getsizeof(lst) for lst in al.adj.values())
        am_size = sys.getsizeof(am.matrix) + sum(
            sys.getsizeof(row) for row in am.matrix)

        print(f"\n  {label}: {n} vertices, {edge_count} edges")
        print(f"    Adj List:   ~{al_size:>10,} bytes")
        print(f"    Adj Matrix: ~{am_size:>10,} bytes")
        print(f"    Winner: {'Adj List' if al_size < am_size else 'Adj Matrix'}")


def demo_conversions():
    """Convert between representations and verify equivalence."""
    print("\n" + "=" * 60)
    print("DEMO: Converting between representations")
    print("=" * 60)

    al = AdjacencyListGraph(directed=True)
    for u, v, w in [(0, 1, 5), (0, 2, 3), (1, 3, 2), (2, 3, 7)]:
        al.add_edge(u, v, w)

    print(f"\nOriginal (Adj List):\n{al}")

    # To matrix
    am, idx_map = adj_list_to_matrix(al)
    print(f"\nConverted to Matrix (vertex map: {idx_map}):\n{am}")

    # To edge list
    el = adj_list_to_edge_list(al)
    print(f"\nConverted to Edge List:\n{el}")

    # Round-trip: edge list back to adj list
    al2 = edge_list_to_adj_list(el)
    print(f"\nRound-trip (Edge List -> Adj List):\n{al2}")

    # Verify edge counts match
    print(f"\nEdge counts: original={al.edge_count()}, "
          f"matrix={am.edge_count()}, edge_list={len(el.edges)}, "
          f"round-trip={al2.edge_count()}")


if __name__ == "__main__":
    demo_build_same_graph()
    demo_edge_check_performance()
    demo_space_comparison()
    demo_conversions()
