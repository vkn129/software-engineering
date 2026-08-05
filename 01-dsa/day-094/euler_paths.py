"""
Day 94: Hierholzer's Algorithm — Euler Paths & Circuits

Linear-time O(E) traversal that walks every edge exactly once.

Two flavors:
  - Undirected (Konigsberg-style)
  - Directed (de Bruijn / genome-assembly style)
"""

from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# 1. Existence checks
# ---------------------------------------------------------------------------

def undirected_euler_status(n, edges):
    """
    Return ('circuit', start) | ('path', start) | ('none', None)
    based on degree parity and connectivity of edge-bearing vertices.
    """
    deg = [0] * n
    for u, v in edges:
        deg[u] += 1
        deg[v] += 1
        if u == v:
            deg[u] += 1  # self-loops contribute 2

    odd = [v for v in range(n) if deg[v] % 2 == 1]

    if len(odd) not in (0, 2):
        return ("none", None)

    # Check connectivity of non-isolated vertices
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    start_candidates = [v for v in range(n) if deg[v] > 0]
    if not start_candidates:
        return ("circuit", 0)  # no edges, trivially Eulerian

    start = odd[0] if odd else start_candidates[0]

    # BFS from start; every vertex with deg > 0 must be reachable
    visited = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                q.append(v)
    for v in start_candidates:
        if v not in visited:
            return ("none", None)

    return ("circuit" if not odd else "path", start)


def directed_euler_status(n, edges):
    """
    Return ('circuit', start) | ('path', start) | ('none', None) for a
    directed multigraph.
    """
    indeg = [0] * n
    outdeg = [0] * n
    for u, v in edges:
        outdeg[u] += 1
        indeg[v] += 1

    start_extra = []
    end_extra = []
    for v in range(n):
        d = outdeg[v] - indeg[v]
        if d == 1:
            start_extra.append(v)
        elif d == -1:
            end_extra.append(v)
        elif d != 0:
            return ("none", None)

    nonzero = [v for v in range(n) if indeg[v] + outdeg[v] > 0]
    if not nonzero:
        return ("circuit", 0)

    # Underlying graph weakly connected?
    und = defaultdict(set)
    for u, v in edges:
        und[u].add(v)
        und[v].add(u)
    start = nonzero[0]
    visited = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in und[u]:
            if v not in visited:
                visited.add(v)
                q.append(v)
    for v in nonzero:
        if v not in visited:
            return ("none", None)

    if not start_extra and not end_extra:
        return ("circuit", nonzero[0])
    if len(start_extra) == 1 and len(end_extra) == 1:
        return ("path", start_extra[0])
    return ("none", None)


# ---------------------------------------------------------------------------
# 2. Hierholzer's algorithm — iterative
# ---------------------------------------------------------------------------

def hierholzer_directed(n, edges):
    """
    For a directed Eulerian graph, return the sequence of vertices forming
    an Euler path/circuit. Returns None if not Eulerian.
    """
    status, start = directed_euler_status(n, edges)
    if status == "none":
        return None

    adj = defaultdict(deque)
    for u, v in edges:
        adj[u].append(v)

    stack = [start]
    circuit = []
    while stack:
        v = stack[-1]
        if adj[v]:
            u = adj[v].popleft()
            stack.append(u)
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    return circuit


def hierholzer_undirected(n, edges):
    """
    For an undirected Eulerian (multi)graph, return the vertex sequence.

    Edges are identified by index so multi-edges and self-loops work:
    each edge gets a unique id; we mark it "used" rather than removing.
    """
    status, start = undirected_euler_status(n, edges)
    if status == "none":
        return None

    adj = defaultdict(list)
    for i, (u, v) in enumerate(edges):
        adj[u].append((v, i))
        adj[v].append((u, i))

    used = [False] * len(edges)
    ptr = [0] * n  # cursor in adjacency list per vertex

    stack = [start]
    circuit = []
    while stack:
        v = stack[-1]
        # Advance cursor past used edges
        while ptr[v] < len(adj[v]) and used[adj[v][ptr[v]][1]]:
            ptr[v] += 1
        if ptr[v] < len(adj[v]):
            u, eid = adj[v][ptr[v]]
            used[eid] = True
            ptr[v] += 1
            stack.append(u)
        else:
            circuit.append(stack.pop())
    circuit.reverse()
    return circuit


# ---------------------------------------------------------------------------
# 3. de Bruijn genome reconstruction
# ---------------------------------------------------------------------------

def reconstruct_string(kmers):
    """
    Given a list of k-mers (e.g. ["AAG", "AGT", "GTC", "TCT"]),
    reconstruct the original sequence via an Euler path on the
    de Bruijn graph (nodes = (k-1)-mers, edges = k-mers).
    """
    # Map (k-1)-mers to integer ids for the graph
    node_id = {}
    edges = []

    def get_id(s):
        if s not in node_id:
            node_id[s] = len(node_id)
        return node_id[s]

    for kmer in kmers:
        u = get_id(kmer[:-1])
        v = get_id(kmer[1:])
        edges.append((u, v))

    path_ids = hierholzer_directed(len(node_id), edges)
    if path_ids is None:
        return None

    id_to_node = {i: s for s, i in node_id.items()}
    # First node fully, then last char of each subsequent
    result = id_to_node[path_ids[0]]
    for nid in path_ids[1:]:
        result += id_to_node[nid][-1]
    return result


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_konigsberg():
    print("=" * 65)
    print("DEMO 1: Konigsberg Bridges (Euler's 1736 problem)")
    print("=" * 65)
    # 4 land masses, 7 bridges:
    # A=0, B=1, C=2, D=3. Two bridges A-B, two A-C, one A-D, one B-D, one C-D.
    edges = [(0, 1), (0, 1), (0, 2), (0, 2), (0, 3), (1, 3), (2, 3)]
    status, start = undirected_euler_status(4, edges)
    print(f"  Status: {status}, start: {start}")
    print(f"  Degree of each landmass:")
    deg = [0, 0, 0, 0]
    for u, v in edges:
        deg[u] += 1; deg[v] += 1
    for i, d in enumerate(deg):
        print(f"    {chr(ord('A')+i)}: degree {d}")
    print(f"  -> {'No' if status == 'none' else 'Yes'} valid walk exists.")
    print("     (As Euler proved, all 4 vertices have odd degree.)")


def demo_simple_circuit():
    print("\n" + "=" * 65)
    print("DEMO 2: A Simple Euler Circuit")
    print("=" * 65)
    # Triangle with a tail loop
    edges = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 0)]
    status, start = undirected_euler_status(5, edges)
    print(f"  Status: {status}")
    circuit = hierholzer_undirected(5, edges)
    print(f"  Circuit: {' -> '.join(map(str, circuit))}")
    print(f"  Length: {len(circuit) - 1} edges (expected {len(edges)})")


def demo_directed_path():
    print("\n" + "=" * 65)
    print("DEMO 3: Directed Euler Path")
    print("=" * 65)
    # 0 -> 1 -> 2 -> 0 -> 3 -> 4   (Euler path from 0 to 4)
    edges = [(0, 1), (1, 2), (2, 0), (0, 3), (3, 4)]
    status, start = directed_euler_status(5, edges)
    print(f"  Status: {status}, start: {start}")
    path = hierholzer_directed(5, edges)
    print(f"  Path: {' -> '.join(map(str, path))}")


def demo_genome_assembly():
    print("\n" + "=" * 65)
    print("DEMO 4: Genome Reconstruction (de Bruijn / Hierholzer)")
    print("=" * 65)
    # Original sequence "AAGATTCTCTAC" produces 3-mers (in some order):
    original = "AAGATTCTCTAC"
    k = 3
    kmers = [original[i:i+k] for i in range(len(original) - k + 1)]
    # Shuffle to simulate real reads
    import random
    random.Random(42).shuffle(kmers)
    print(f"  Original:    {original}")
    print(f"  k-mers (shuffled): {kmers}")
    reconstructed = reconstruct_string(kmers)
    print(f"  Reconstructed: {reconstructed}")
    print(f"  Match: {reconstructed == original or sorted([reconstructed[i:i+k] for i in range(len(reconstructed)-k+1)]) == sorted(kmers)}")


if __name__ == "__main__":
    demo_konigsberg()
    demo_simple_circuit()
    demo_directed_path()
    demo_genome_assembly()
