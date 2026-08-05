"""
Day 79: Breadth-First Search (BFS)

Queue-based graph traversal that explores vertices in order of their distance
from the source. Guarantees shortest paths in unweighted graphs.
"""

from collections import deque, defaultdict
from typing import List, Dict, Optional, Set, Tuple


def bfs_traversal(graph: Dict[int, List[int]], source: int) -> List[int]:
    """
    Basic BFS traversal returning vertices in discovery order.

    Time: O(V + E)
    Space: O(V)
    """
    visited = {source}
    queue = deque([source])
    order = []

    while queue:
        vertex = queue.popleft()
        order.append(vertex)
        for neighbor in graph.get(vertex, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


def bfs_shortest_path(
    graph: Dict[int, List[int]], source: int, target: int
) -> Optional[List[int]]:
    """
    Find shortest path from source to target in an unweighted graph.

    Returns the path as a list of vertices, or None if no path exists.
    BFS guarantees this is the shortest path (minimum number of edges).

    Time: O(V + E)
    Space: O(V)
    """
    if source == target:
        return [source]

    visited = {source}
    queue = deque([source])
    parent = {source: None}

    while queue:
        vertex = queue.popleft()
        for neighbor in graph.get(vertex, []):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = vertex
                queue.append(neighbor)

                if neighbor == target:
                    # Reconstruct path
                    path = []
                    current = target
                    while current is not None:
                        path.append(current)
                        current = parent[current]
                    return path[::-1]

    return None  # No path exists


def bfs_level_order(
    graph: Dict[int, List[int]], source: int
) -> List[List[int]]:
    """
    Group vertices by their BFS distance (level) from the source.

    Level 0: [source]
    Level 1: [direct neighbors of source]
    Level 2: [neighbors of level 1, not yet visited]
    ...

    Time: O(V + E)
    Space: O(V)
    """
    visited = {source}
    queue = deque([source])
    levels = []

    while queue:
        level_size = len(queue)
        current_level = []

        for _ in range(level_size):
            vertex = queue.popleft()
            current_level.append(vertex)
            for neighbor in graph.get(vertex, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        levels.append(current_level)

    return levels


def bfs_connected_components(
    graph: Dict[int, List[int]], vertices: Set[int]
) -> List[Set[int]]:
    """
    Find all connected components in an undirected graph.

    Each component is discovered by running BFS from an unvisited vertex.

    Time: O(V + E)
    Space: O(V)
    """
    visited = set()
    components = []

    for v in vertices:
        if v not in visited:
            component = set()
            queue = deque([v])
            visited.add(v)

            while queue:
                vertex = queue.popleft()
                component.add(vertex)
                for neighbor in graph.get(vertex, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            components.append(component)

    return components


def bfs_distances(
    graph: Dict[int, List[int]], source: int
) -> Dict[int, int]:
    """
    Compute shortest distance from source to every reachable vertex.

    Returns {vertex: distance}. Unreachable vertices are not included.

    Time: O(V + E)
    Space: O(V)
    """
    distances = {source: 0}
    queue = deque([source])

    while queue:
        vertex = queue.popleft()
        for neighbor in graph.get(vertex, []):
            if neighbor not in distances:
                distances[neighbor] = distances[vertex] + 1
                queue.append(neighbor)

    return distances


def is_bipartite(graph: Dict[int, List[int]], vertices: Set[int]) -> bool:
    """
    Check if graph is bipartite using BFS 2-coloring.

    A graph is bipartite iff it contains no odd-length cycles.
    Try to color each vertex with one of two colors such that
    no edge connects vertices of the same color.

    Time: O(V + E)
    Space: O(V)
    """
    color = {}

    for start in vertices:
        if start in color:
            continue

        color[start] = 0
        queue = deque([start])

        while queue:
            vertex = queue.popleft()
            for neighbor in graph.get(vertex, []):
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    queue.append(neighbor)
                elif color[neighbor] == color[vertex]:
                    return False

    return True


def multi_source_bfs(
    grid: List[List[int]], sources: List[Tuple[int, int]]
) -> List[List[int]]:
    """
    Multi-source BFS on a 2D grid.

    Compute minimum distance from each cell to its nearest source.
    Sources are given as (row, col) coordinates. Cells with value -1
    are walls (impassable). Returns a distance grid where -1 means
    unreachable.

    This is the key technique for "rotten oranges" and similar problems.

    Time: O(rows * cols)
    Space: O(rows * cols)
    """
    if not grid or not grid[0]:
        return []

    rows, cols = len(grid), len(grid[0])
    dist = [[-1] * cols for _ in range(rows)]
    queue = deque()

    # Enqueue all sources at distance 0
    for r, c in sources:
        if 0 <= r < rows and 0 <= c < cols and grid[r][c] != -1:
            dist[r][c] = 0
            queue.append((r, c))

    # BFS outward from all sources simultaneously
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    while queue:
        r, c = queue.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and dist[nr][nc] == -1 and grid[nr][nc] != -1:
                dist[nr][nc] = dist[r][c] + 1
                queue.append((nr, nc))

    return dist


def solve_maze(
    maze: List[List[int]], start: Tuple[int, int], end: Tuple[int, int]
) -> Optional[List[Tuple[int, int]]]:
    """
    Solve a maze using BFS with path reconstruction.

    maze[r][c] = 0 means open, 1 means wall.
    Returns shortest path as list of (row, col) coordinates, or None.

    Time: O(rows * cols)
    Space: O(rows * cols)
    """
    if not maze or not maze[0]:
        return None

    rows, cols = len(maze), len(maze[0])
    sr, sc = start
    er, ec = end

    if maze[sr][sc] == 1 or maze[er][ec] == 1:
        return None

    visited = set()
    visited.add((sr, sc))
    queue = deque([(sr, sc)])
    parent = {(sr, sc): None}

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        r, c = queue.popleft()

        if (r, c) == (er, ec):
            # Reconstruct path
            path = []
            current = (er, ec)
            while current is not None:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and (nr, nc) not in visited and maze[nr][nc] == 0):
                visited.add((nr, nc))
                parent[(nr, nc)] = (r, c)
                queue.append((nr, nc))

    return None  # No path exists


if __name__ == "__main__":
    print("=" * 60)
    print("BFS DEMO")
    print("=" * 60)

    # Sample graph
    #   1 - 2 - 5
    #   |   |
    #   3 - 4
    #   6 (isolated)
    graph = {
        1: [2, 3],
        2: [1, 4, 5],
        3: [1, 4],
        4: [2, 3],
        5: [2],
        6: [],
    }

    print("\nGraph adjacency list:")
    for v in sorted(graph):
        print(f"  {v}: {graph[v]}")

    # Basic traversal
    print(f"\nBFS traversal from vertex 1: {bfs_traversal(graph, 1)}")

    # Shortest path
    path = bfs_shortest_path(graph, 1, 5)
    print(f"Shortest path 1 -> 5: {path} (length {len(path) - 1})")

    path2 = bfs_shortest_path(graph, 3, 5)
    print(f"Shortest path 3 -> 5: {path2} (length {len(path2) - 1})")

    # Level order
    levels = bfs_level_order(graph, 1)
    print(f"\nLevel-order from vertex 1:")
    for i, level in enumerate(levels):
        print(f"  Distance {i}: {level}")

    # Connected components
    components = bfs_connected_components(graph, {1, 2, 3, 4, 5, 6})
    print(f"\nConnected components: {[sorted(c) for c in components]}")

    # Distances
    dists = bfs_distances(graph, 1)
    print(f"\nDistances from vertex 1: {dict(sorted(dists.items()))}")

    # Bipartite check
    bipartite_graph = {0: [1, 3], 1: [0, 2], 2: [1, 3], 3: [0, 2]}
    odd_cycle = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
    print(f"\nSquare graph bipartite? {is_bipartite(bipartite_graph, {0, 1, 2, 3})}")
    print(f"Triangle bipartite? {is_bipartite(odd_cycle, {0, 1, 2})}")

    # Maze solving
    print("\n" + "=" * 60)
    print("MAZE SOLVING DEMO")
    print("=" * 60)

    maze = [
        [0, 0, 1, 0, 0],
        [0, 1, 0, 0, 1],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
    ]

    print("\nMaze (0=open, 1=wall):")
    for row in maze:
        print("  " + " ".join("." if c == 0 else "#" for c in row))

    path = solve_maze(maze, (0, 0), (4, 4))
    if path:
        print(f"\nShortest path (0,0) -> (4,4): {path}")
        print(f"Path length: {len(path) - 1} steps")

        # Visualize path on maze
        path_set = set(path)
        print("\nMaze with path (*):")
        for r in range(len(maze)):
            row_str = ""
            for c in range(len(maze[0])):
                if (r, c) in path_set:
                    row_str += "* "
                elif maze[r][c] == 1:
                    row_str += "# "
                else:
                    row_str += ". "
            print("  " + row_str)
    else:
        print("  No path found!")

    # Multi-source BFS
    print("\n" + "=" * 60)
    print("MULTI-SOURCE BFS DEMO")
    print("=" * 60)

    grid = [
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ]
    sources = [(0, 0), (3, 3)]
    distances = multi_source_bfs(grid, sources)
    print(f"\nSources at (0,0) and (3,3):")
    print("Distance grid:")
    for row in distances:
        print("  " + " ".join(f"{d:2}" for d in row))
