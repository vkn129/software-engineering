"""
Day 89: Bipartite Graphs & A* Search — From Scratch

Bipartite checking via 2-coloring, maximum matching via Hopcroft-Karp,
and A* pathfinding with admissible heuristics.
"""

from collections import defaultdict, deque
import heapq
import math


# ---------------------------------------------------------------------------
# 1. Bipartite Check via BFS 2-Coloring
# ---------------------------------------------------------------------------

def is_bipartite(adj):
    """
    Check if an undirected graph is bipartite using BFS 2-coloring.

    adj: dict mapping vertex -> list of neighbors
    Returns: (is_bipartite: bool, coloring: dict vertex->0/1 or None)

    The idea: try to color the graph with 2 colors such that no edge
    connects same-colored vertices. If we find a conflict during BFS,
    the graph has an odd-length cycle and is NOT bipartite.
    """
    color = {}
    vertices = list(adj.keys())

    for start in vertices:
        if start in color:
            continue

        # BFS from this unvisited component
        color[start] = 0
        queue = deque([start])

        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in color:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    # Same color on both ends of an edge -> not bipartite
                    return False, None

    return True, color


# ---------------------------------------------------------------------------
# 2. Hopcroft-Karp Maximum Bipartite Matching
# ---------------------------------------------------------------------------

class HopcroftKarp:
    """
    Maximum bipartite matching using Hopcroft-Karp algorithm.

    Time: O(E * sqrt(V)) — finds multiple augmenting paths per phase.
    Each BFS phase finds the shortest augmenting path length, then DFS
    finds all vertex-disjoint augmenting paths of that length.
    """

    def __init__(self, left_vertices, right_vertices, adj):
        """
        left_vertices: list of vertices on the left side
        right_vertices: list of vertices on the right side
        adj: dict mapping left vertex -> list of right vertex neighbors
        """
        self.left = left_vertices
        self.right = right_vertices
        self.adj = adj
        # match_left[u] = matched right vertex (or None)
        self.match_left = {u: None for u in left_vertices}
        # match_right[v] = matched left vertex (or None)
        self.match_right = {v: None for v in right_vertices}
        self.dist = {}

    def bfs(self):
        """
        BFS to find shortest augmenting path length.
        Returns True if augmenting paths exist.

        Free left vertices (unmatched) are the BFS sources.
        We alternate between unmatched and matched edges.
        """
        queue = deque()
        for u in self.left:
            if self.match_left[u] is None:
                self.dist[u] = 0
                queue.append(u)
            else:
                self.dist[u] = math.inf

        found = False

        while queue:
            u = queue.popleft()
            for v in self.adj.get(u, []):
                # v's match partner (the left vertex matched to v)
                next_u = self.match_right[v]
                if next_u is None:
                    # v is free — augmenting path exists
                    found = True
                elif self.dist[next_u] == math.inf:
                    # next_u not yet visited in this BFS
                    self.dist[next_u] = self.dist[u] + 1
                    queue.append(next_u)

        return found

    def dfs(self, u):
        """
        DFS to find an augmenting path from free left vertex u.
        Returns True if augmenting path found (and matching updated).
        """
        for v in self.adj.get(u, []):
            next_u = self.match_right[v]
            # Follow only edges that are on shortest augmenting paths
            if next_u is None or (self.dist.get(next_u, math.inf) == self.dist[u] + 1
                                  and self.dfs(next_u)):
                self.match_left[u] = v
                self.match_right[v] = u
                return True

        # No augmenting path from u — mark as unreachable
        self.dist[u] = math.inf
        return False

    def max_matching(self):
        """
        Run Hopcroft-Karp to find maximum matching.
        Returns: (matching_size, list of (left, right) matched pairs)
        """
        matching = 0

        # Each BFS phase finds shortest augmenting paths, DFS augments them
        while self.bfs():
            for u in self.left:
                if self.match_left[u] is None:
                    if self.dfs(u):
                        matching += 1

        pairs = [(u, v) for u, v in self.match_left.items() if v is not None]
        return matching, pairs


# ---------------------------------------------------------------------------
# 3. A* Search on a 2D Grid
# ---------------------------------------------------------------------------

def manhattan(a, b):
    """Manhattan distance — admissible for 4-directional grid movement."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def euclidean(a, b):
    """Euclidean distance — admissible for any-angle movement."""
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def astar(grid, start, goal, heuristic=manhattan):
    """
    A* search on a 2D grid.

    grid: list of lists, 0 = passable, 1 = obstacle
    start: (row, col)
    goal: (row, col)
    heuristic: function(pos, goal) -> estimated cost

    Returns: (path as list of (row, col), nodes_explored count)
             path is None if no path exists.

    f(n) = g(n) + h(n)
    - g(n): actual cost from start to n
    - h(n): heuristic estimate from n to goal
    Admissible h guarantees optimal path.
    """
    rows, cols = len(grid), len(grid[0])

    # Priority queue: (f_score, tiebreaker, position)
    counter = 0
    open_set = [(heuristic(start, goal), counter, start)]
    came_from = {}
    g_score = {start: 0}
    explored = 0

    # 4-directional movement
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while open_set:
        f, _, current = heapq.heappop(open_set)

        if current == goal:
            # Reconstruct path
            path = []
            node = goal
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return path, explored

        explored += 1

        for dr, dc in directions:
            nr, nc = current[0] + dr, current[1] + dc

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                neighbor = (nr, nc)
                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get(neighbor, math.inf):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + heuristic(neighbor, goal)
                    counter += 1
                    heapq.heappush(open_set, (f_score, counter, neighbor))

    return None, explored  # No path found


def dijkstra_grid(grid, start, goal):
    """Dijkstra on a grid — equivalent to A* with h=0. For comparison."""
    return astar(grid, start, goal, heuristic=lambda a, b: 0)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_bipartite():
    print("=" * 60)
    print("DEMO 1: Bipartite Graph Checking")
    print("=" * 60)

    # Bipartite graph (even cycle)
    adj1 = {
        0: [1, 3],
        1: [0, 2],
        2: [1, 3],
        3: [2, 0],
    }
    result, coloring = is_bipartite(adj1)
    print(f"\nSquare graph (4-cycle):")
    print(f"  0 --- 1")
    print(f"  |     |")
    print(f"  3 --- 2")
    print(f"  Bipartite: {result}")
    print(f"  Coloring: {coloring}")

    # Non-bipartite graph (odd cycle)
    adj2 = {
        0: [1, 2],
        1: [0, 2],
        2: [0, 1],
    }
    result2, _ = is_bipartite(adj2)
    print(f"\nTriangle (3-cycle):")
    print(f"  0 --- 1")
    print(f"   \\   /")
    print(f"     2")
    print(f"  Bipartite: {result2}")

    # Disconnected bipartite
    adj3 = {
        0: [1], 1: [0],
        2: [3], 3: [2],
        4: [],
    }
    result3, coloring3 = is_bipartite(adj3)
    print(f"\nDisconnected graph (0-1, 2-3, 4):")
    print(f"  Bipartite: {result3}, Coloring: {coloring3}")


def demo_matching():
    print("\n" + "=" * 60)
    print("DEMO 2: Job Assignment — Maximum Bipartite Matching")
    print("=" * 60)

    workers = ["Alice", "Bob", "Charlie", "Diana"]
    tasks = ["Frontend", "Backend", "Database", "Testing"]

    # Adjacency: which workers can do which tasks
    capabilities = {
        "Alice": ["Frontend", "Backend"],
        "Bob": ["Backend", "Database"],
        "Charlie": ["Database", "Testing"],
        "Diana": ["Frontend", "Testing"],
    }

    hk = HopcroftKarp(workers, tasks, capabilities)
    size, pairs = hk.max_matching()

    print(f"\nWorker capabilities:")
    for w, ts in capabilities.items():
        print(f"  {w}: {ts}")

    print(f"\nMaximum matching size: {size}")
    print(f"Optimal assignment:")
    for w, t in pairs:
        print(f"  {w} -> {t}")


def demo_astar():
    print("\n" + "=" * 60)
    print("DEMO 3: A* Pathfinding on Grid")
    print("=" * 60)

    # 0 = passable, 1 = obstacle
    grid = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    start = (0, 0)
    goal = (4, 7)

    path, explored = astar(grid, start, goal, manhattan)

    print(f"\nGrid (S=start, G=goal, #=wall, *=path, .=open):")
    path_set = set(path) if path else set()
    for r in range(len(grid)):
        row_str = "  "
        for c in range(len(grid[0])):
            if (r, c) == start:
                row_str += "S "
            elif (r, c) == goal:
                row_str += "G "
            elif grid[r][c] == 1:
                row_str += "# "
            elif (r, c) in path_set:
                row_str += "* "
            else:
                row_str += ". "
        print(row_str)

    print(f"\n  Path length: {len(path) if path else 'N/A'}")
    print(f"  Nodes explored: {explored}")


def demo_astar_vs_dijkstra():
    print("\n" + "=" * 60)
    print("DEMO 4: A* vs Dijkstra — Nodes Explored Comparison")
    print("=" * 60)

    # Larger grid to show the difference
    size = 15
    grid = [[0] * size for _ in range(size)]

    # Add a wall in the middle
    for r in range(2, 12):
        grid[r][7] = 1

    start = (0, 0)
    goal = (14, 14)

    path_astar, explored_astar = astar(grid, start, goal, manhattan)
    path_dijk, explored_dijk = dijkstra_grid(grid, start, goal)

    print(f"\n  Grid: {size}x{size} with vertical wall")
    print(f"  Start: {start}, Goal: {goal}")
    print(f"\n  A* (Manhattan heuristic):")
    print(f"    Path length: {len(path_astar)}")
    print(f"    Nodes explored: {explored_astar}")
    print(f"\n  Dijkstra (h=0):")
    print(f"    Path length: {len(path_dijk)}")
    print(f"    Nodes explored: {explored_dijk}")
    print(f"\n  A* explored {explored_dijk - explored_astar} fewer nodes "
          f"({100 * (1 - explored_astar / explored_dijk):.0f}% reduction)")
    print(f"  Both find same-length path: {len(path_astar) == len(path_dijk)}")


if __name__ == "__main__":
    demo_bipartite()
    demo_matching()
    demo_astar()
    demo_astar_vs_dijkstra()
