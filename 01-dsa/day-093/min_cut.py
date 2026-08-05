"""
Day 93: Min Cut and the Max-Flow Min-Cut Theorem

Compute max s-t flow, then recover the corresponding min s-t cut.
Demonstrates the duality and an image-segmentation toy example.
"""

from collections import defaultdict, deque


# ---------------------------------------------------------------------------
# 1. Edmonds-Karp max flow (Day 90 recap, with residual graph exposed)
# ---------------------------------------------------------------------------

class FlowNetwork:
    """
    Directed graph with integer capacities. Supports anti-parallel edges
    by allocating distinct slots in the residual graph.

    cap[u][v] holds **residual** capacity. Initialized from input edges.
    """

    def __init__(self, n):
        self.n = n
        self.cap = defaultdict(lambda: defaultdict(int))
        self.adj = defaultdict(set)

    def add_edge(self, u, v, c):
        # Increase capacity if duplicate; ensure reverse slot exists.
        self.cap[u][v] += c
        self.adj[u].add(v)
        self.adj[v].add(u)  # reverse for residual traversal

    def _bfs(self, s, t, parent):
        for i in range(self.n):
            parent[i] = -1
        parent[s] = s
        q = deque([s])
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                if parent[v] == -1 and self.cap[u][v] > 0:
                    parent[v] = u
                    if v == t:
                        return True
                    q.append(v)
        return False

    def max_flow(self, s, t):
        flow = 0
        parent = [-1] * self.n
        while self._bfs(s, t, parent):
            # Find bottleneck along augmenting path s -> t
            bottleneck = float("inf")
            v = t
            while v != s:
                u = parent[v]
                bottleneck = min(bottleneck, self.cap[u][v])
                v = u
            # Augment
            v = t
            while v != s:
                u = parent[v]
                self.cap[u][v] -= bottleneck
                self.cap[v][u] += bottleneck
                v = u
            flow += bottleneck
        return flow

    def reachable_from(self, s):
        """Set of vertices reachable from s in the current residual graph."""
        visited = {s}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                if v not in visited and self.cap[u][v] > 0:
                    visited.add(v)
                    q.append(v)
        return visited


# ---------------------------------------------------------------------------
# 2. Min-cut extraction
# ---------------------------------------------------------------------------

def min_cut(n, edges, s, t):
    """
    edges: list of (u, v, capacity) for the *original* directed graph.
    Returns (cut_value, cut_edges) where cut_edges is the list of original
    edges crossing from S to T in the min cut.
    """
    # Need a separate copy of original edges to filter saturated ones.
    original = defaultdict(lambda: defaultdict(int))
    for u, v, c in edges:
        original[u][v] += c

    net = FlowNetwork(n)
    for u, v, c in edges:
        net.add_edge(u, v, c)

    flow_value = net.max_flow(s, t)
    S = net.reachable_from(s)

    cut_edges = []
    for u in S:
        for v in original[u]:
            if v not in S and original[u][v] > 0:
                cut_edges.append((u, v, original[u][v]))

    return flow_value, cut_edges, S


# ---------------------------------------------------------------------------
# 3. Image segmentation toy example
# ---------------------------------------------------------------------------

def segment_image(pixels, fg_weight, bg_weight, smoothness):
    """
    1D 'image' = list of pixel values. Returns labels: 'F' or 'B' per pixel.

    Graph build:
      - source (id n) -> pixel i, capacity fg_weight(i)
      - pixel i -> sink (id n+1), capacity bg_weight(i)
      - between neighbors i,i+1: capacity smoothness(i, i+1) (both directions)

    Min s-t cut splits pixels into S (foreground) and T (background).
    """
    n = len(pixels)
    SOURCE = n
    SINK = n + 1
    edges = []

    for i in range(n):
        edges.append((SOURCE, i, fg_weight(pixels[i])))
        edges.append((i, SINK, bg_weight(pixels[i])))

    for i in range(n - 1):
        w = smoothness(pixels[i], pixels[i + 1])
        edges.append((i, i + 1, w))
        edges.append((i + 1, i, w))

    flow, cut, S = min_cut(n + 2, edges, SOURCE, SINK)
    labels = ["F" if i in S else "B" for i in range(n)]
    return labels, flow


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_basic_cut():
    print("=" * 65)
    print("DEMO 1: Min Cut on a Small Network")
    print("=" * 65)
    # Classic example, max flow = 23
    # vertices: 0=s, 1, 2, 3, 4, 5=t
    edges = [
        (0, 1, 16), (0, 2, 13),
        (1, 2, 10), (2, 1, 4),
        (1, 3, 12),
        (2, 4, 14),
        (3, 2, 9),
        (4, 3, 7),
        (3, 5, 20), (4, 5, 4),
    ]
    flow, cut, S = min_cut(6, edges, 0, 5)
    print(f"  Max flow / Min cut value: {flow}")
    print(f"  Reachable from s (set S): {sorted(S)}")
    print(f"  Cut edges (S -> T):")
    for u, v, c in cut:
        print(f"    {u} -> {v}  capacity {c}")
    print(f"  Sum of cut capacities: {sum(c for _,_,c in cut)}")
    print("  -> Verifies max-flow == min-cut.")


def demo_bottleneck():
    print("\n" + "=" * 65)
    print("DEMO 2: Identifying a Single Bottleneck Edge")
    print("=" * 65)
    # Long pipeline, one narrow segment in the middle
    edges = [
        (0, 1, 100),
        (1, 2, 5),   # bottleneck
        (2, 3, 100),
    ]
    flow, cut, S = min_cut(4, edges, 0, 3)
    print(f"  Max flow: {flow}")
    print(f"  Cut: {cut}")
    print(f"  The bottleneck is edge (1, 2) with capacity 5.")


def demo_segmentation():
    print("\n" + "=" * 65)
    print("DEMO 3: 1D Image Segmentation (Foreground vs Background)")
    print("=" * 65)
    # Pixel values 0-9 — foreground bright (>=5), background dark (<5)
    pixels = [1, 2, 1, 8, 9, 8, 7, 2, 1, 2]

    def fg_w(p): return p          # bright = likely foreground
    def bg_w(p): return 10 - p     # dark = likely background

    def smooth(a, b):
        # High weight if pixels are similar -> they should stay together
        return max(0, 5 - abs(a - b))

    labels, flow = segment_image(pixels, fg_w, bg_w, smooth)
    print(f"  Pixels:  {pixels}")
    print(f"  Labels:  {labels}")
    print(f"  Min cut value: {flow}")
    print("  -> The cut separates a contiguous bright region as foreground.")


def demo_dual_proof():
    print("\n" + "=" * 65)
    print("DEMO 4: Verifying Max-Flow Min-Cut Duality")
    print("=" * 65)
    # Random-ish small graph; both must agree
    edges = [
        (0, 1, 7), (0, 2, 4),
        (1, 2, 2), (1, 3, 5),
        (2, 3, 3), (2, 4, 8),
        (3, 4, 2), (3, 5, 6),
        (4, 5, 5),
    ]
    flow, cut, _ = min_cut(6, edges, 0, 5)
    cut_capacity = sum(c for _, _, c in cut)
    print(f"  Max flow         = {flow}")
    print(f"  Min cut capacity = {cut_capacity}")
    print(f"  Duality holds:     {flow == cut_capacity}")


if __name__ == "__main__":
    demo_basic_cut()
    demo_bottleneck()
    demo_segmentation()
    demo_dual_proof()
