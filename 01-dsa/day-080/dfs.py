"""
Day 80: Depth-First Search — From Scratch

DFS explores graphs by diving deep before backtracking. Where BFS finds
shortest paths, DFS finds structure: cycles, components, topological order.
"""

from collections import defaultdict
import random


# ---------------------------------------------------------------------------
# Graph helper (adjacency list, reused from Day 78)
# ---------------------------------------------------------------------------

def make_graph(edges, directed=False):
    """Build adjacency list from edge pairs."""
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    return adj


# ---------------------------------------------------------------------------
# 1. Recursive DFS with pre/post visit hooks
# ---------------------------------------------------------------------------

def dfs_recursive(adj, start, pre_visit=None, post_visit=None):
    """
    Classic recursive DFS. The call stack IS the DFS stack.

    pre_visit(vertex): called when vertex is first discovered
    post_visit(vertex): called when all descendants are fully explored
    """
    visited = set()
    order = []

    def _dfs(u):
        visited.add(u)
        if pre_visit:
            pre_visit(u)
        order.append(u)
        for v in adj[u]:
            if v not in visited:
                _dfs(v)
        if post_visit:
            post_visit(u)

    _dfs(start)
    return order


# ---------------------------------------------------------------------------
# 2. Iterative DFS using explicit stack
# ---------------------------------------------------------------------------

def dfs_iterative(adj, start):
    """
    Same traversal as recursive DFS, but with an explicit stack.
    Avoids Python's recursion limit (~1000 by default).

    Note: popping from stack and pushing neighbors means we visit
    the LAST pushed neighbor first. Reverse neighbor order to match
    recursive DFS exactly.
    """
    visited = set()
    order = []
    stack = [start]

    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        # Push in reverse so leftmost neighbor is popped first
        for v in reversed(adj[u]):
            if v not in visited:
                stack.append(v)

    return order


# ---------------------------------------------------------------------------
# 3. Cycle detection in directed graphs (3-color: WHITE/GRAY/BLACK)
# ---------------------------------------------------------------------------

WHITE, GRAY, BLACK = 0, 1, 2


def has_cycle_directed(adj, vertices):
    """
    Detect cycles using the three-color invariant:
    - WHITE: unvisited
    - GRAY: in current DFS path (on the recursion stack)
    - BLACK: fully processed

    A back edge (to a GRAY vertex) proves a cycle.
    """
    color = {v: WHITE for v in vertices}
    cycle_path = []

    def _dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                # Back edge: v is ancestor of u in current path
                cycle_path.append((u, v))
                return True
            if color[v] == WHITE and _dfs(v):
                return True
        color[u] = BLACK
        return False

    for v in vertices:
        if color[v] == WHITE:
            if _dfs(v):
                return True, cycle_path
    return False, []


# ---------------------------------------------------------------------------
# 4. Path finding between two vertices
# ---------------------------------------------------------------------------

def find_path(adj, start, end):
    """Find ANY path from start to end using DFS. Returns path list or None."""
    visited = set()

    def _dfs(u, path):
        if u == end:
            return path
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                result = _dfs(v, path + [v])
                if result is not None:
                    return result
        return None

    return _dfs(start, [start])


def find_all_paths(adj, start, end):
    """Find ALL paths from start to end. Warning: exponential in worst case."""
    all_paths = []

    def _dfs(u, path, visited):
        if u == end:
            all_paths.append(path[:])
            return
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                path.append(v)
                _dfs(v, path, visited)
                path.pop()
                visited.remove(v)

    _dfs(start, [start], {start})
    return all_paths


# ---------------------------------------------------------------------------
# 5. Connected components (undirected)
# ---------------------------------------------------------------------------

def connected_components(adj, vertices):
    """
    Count and label connected components via DFS.
    Each DFS from an unvisited vertex discovers a new component.
    """
    visited = set()
    components = []

    def _dfs(u, component):
        visited.add(u)
        component.append(u)
        for v in adj[u]:
            if v not in visited:
                _dfs(v, component)

    for v in vertices:
        if v not in visited:
            component = []
            _dfs(v, component)
            components.append(component)

    return components


# ---------------------------------------------------------------------------
# 6. DFS edge classification (directed graphs)
# ---------------------------------------------------------------------------

def classify_edges(adj, vertices):
    """
    Classify every edge as tree, back, forward, or cross.

    Uses discovery/finish timestamps:
    - Tree edge: v is WHITE when we see u->v
    - Back edge: v is GRAY (ancestor in current path)
    - Forward edge: v is BLACK and disc[u] < disc[v] (descendant)
    - Cross edge: v is BLACK and disc[u] > disc[v] (different subtree)
    """
    color = {v: WHITE for v in vertices}
    disc = {}
    finish = {}
    time = [0]  # mutable counter

    classification = {"tree": [], "back": [], "forward": [], "cross": []}

    def _dfs(u):
        color[u] = GRAY
        time[0] += 1
        disc[u] = time[0]

        for v in adj[u]:
            if color[v] == WHITE:
                classification["tree"].append((u, v))
                _dfs(v)
            elif color[v] == GRAY:
                classification["back"].append((u, v))
            elif disc[u] < disc[v]:
                classification["forward"].append((u, v))
            else:
                classification["cross"].append((u, v))

        color[u] = BLACK
        time[0] += 1
        finish[u] = time[0]

    for v in vertices:
        if color[v] == WHITE:
            _dfs(v)

    return classification, disc, finish


# ---------------------------------------------------------------------------
# 7. Maze generation using randomized DFS
# ---------------------------------------------------------------------------

def generate_maze(rows, cols, seed=42):
    """
    Generate a perfect maze using randomized DFS (recursive backtracker).

    A perfect maze has exactly one path between any two cells — this
    happens naturally because DFS builds a spanning tree, and we
    "carve" walls along tree edges.
    """
    random.seed(seed)

    # Maze grid: True = wall, False = passage
    # We use a (2*rows+1) x (2*cols+1) grid where odd positions are cells
    # and even positions are walls
    height = 2 * rows + 1
    width = 2 * cols + 1
    maze = [[True] * width for _ in range(height)]

    def cell_to_grid(r, c):
        return 2 * r + 1, 2 * c + 1

    def get_neighbors(r, c):
        """Get unvisited neighboring cells."""
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                neighbors.append((nr, nc))
        return neighbors

    visited = set()

    def _carve(r, c):
        visited.add((r, c))
        gr, gc = cell_to_grid(r, c)
        maze[gr][gc] = False  # carve cell

        neighbors = get_neighbors(r, c)
        random.shuffle(neighbors)  # randomize for interesting mazes

        for nr, nc in neighbors:
            if (nr, nc) not in visited:
                # Carve the wall between current cell and neighbor
                wall_r = gr + (nr - r)
                wall_c = gc + (nc - c)
                maze[wall_r][wall_c] = False
                _carve(nr, nc)

    _carve(0, 0)
    return maze


def print_maze(maze):
    """Print maze using unicode box characters."""
    for row in maze:
        print("".join("##" if cell else "  " for cell in row))


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_traversal():
    print("=" * 60)
    print("DEMO 1: DFS Traversal Order")
    print("=" * 60)

    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
    adj = make_graph(edges)
    print(f"\nGraph: {dict(adj)}")

    rec_order = dfs_recursive(adj, 0)
    iter_order = dfs_iterative(adj, 0)
    print(f"Recursive DFS from 0: {rec_order}")
    print(f"Iterative DFS from 0: {iter_order}")


def demo_cycle_detection():
    print("\n" + "=" * 60)
    print("DEMO 2: Cycle Detection (directed)")
    print("=" * 60)

    # DAG (no cycles)
    dag = make_graph([(0, 1), (0, 2), (1, 3), (2, 3)], directed=True)
    has_cycle, edges = has_cycle_directed(dag, [0, 1, 2, 3])
    print(f"\nDAG: 0->1, 0->2, 1->3, 2->3")
    print(f"  Has cycle? {has_cycle}")

    # Graph with cycle: 0->1->2->0
    cyclic = make_graph([(0, 1), (1, 2), (2, 0), (2, 3)], directed=True)
    has_cycle, edges = has_cycle_directed(cyclic, [0, 1, 2, 3])
    print(f"\nCyclic: 0->1->2->0, 2->3")
    print(f"  Has cycle? {has_cycle} (back edge: {edges})")


def demo_path_finding():
    print("\n" + "=" * 60)
    print("DEMO 3: Path Finding")
    print("=" * 60)

    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (2, 4)]
    adj = make_graph(edges)

    path = find_path(adj, 0, 4)
    print(f"\nGraph: {dict(adj)}")
    print(f"A path from 0 to 4: {path}")

    all_paths = find_all_paths(adj, 0, 4)
    print(f"All paths from 0 to 4: {all_paths}")
    print(f"Total paths: {len(all_paths)}")


def demo_components():
    print("\n" + "=" * 60)
    print("DEMO 4: Connected Components")
    print("=" * 60)

    # Three separate components
    edges = [(0, 1), (1, 2), (3, 4), (5, 6), (6, 7), (7, 8)]
    adj = make_graph(edges)
    # Ensure isolated vertices appear
    for v in range(9):
        if v not in adj:
            adj[v] = []

    comps = connected_components(adj, list(range(9)))
    print(f"\nGraph edges: {edges}")
    print(f"Connected components ({len(comps)}):")
    for i, comp in enumerate(comps):
        print(f"  Component {i}: {sorted(comp)}")


def demo_edge_classification():
    print("\n" + "=" * 60)
    print("DEMO 5: Edge Classification (directed)")
    print("=" * 60)

    # Directed graph with all 4 edge types
    edges = [(0, 1), (1, 2), (2, 3), (3, 1),  # back edge: 3->1
             (0, 3),                             # forward edge: 0->3
             (2, 0)]                             # cross edge possibility
    adj = make_graph(edges, directed=True)

    classes, disc, finish = classify_edges(adj, [0, 1, 2, 3])
    print(f"\nDirected graph: {dict(adj)}")
    print(f"\nDiscovery times: {disc}")
    print(f"Finish times:    {finish}")
    print(f"\nEdge classification:")
    for etype, elist in classes.items():
        if elist:
            print(f"  {etype:>8}: {elist}")


def demo_maze():
    print("\n" + "=" * 60)
    print("DEMO 6: Maze Generation (randomized DFS)")
    print("=" * 60)

    maze = generate_maze(8, 15, seed=42)
    print(f"\n8x15 maze (DFS creates long winding corridors):\n")
    print_maze(maze)
    print("\nDFS mazes have long corridors because the algorithm goes as")
    print("deep as possible before backtracking — the same property that")
    print("makes DFS good for exploring solution spaces.")


if __name__ == "__main__":
    demo_traversal()
    demo_cycle_detection()
    demo_path_finding()
    demo_components()
    demo_edge_classification()
    demo_maze()
