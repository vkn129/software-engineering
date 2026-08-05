"""
Day 89 Practice: Bipartite Graphs & A* Search
6 exercises on 2-coloring, max matching, heuristic pathfinding, and König's theorem.
"""
from collections import defaultdict, deque
import heapq


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Bipartite check via BFS 2-coloring
# ===================================================================

def is_bipartite(n, edges):
    pass


def _sol_is_bipartite(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return False
    return True


# ===================================================================
# Exercise 2: 2-coloring (return coloring or None if not bipartite)
# ===================================================================

def two_color(n, edges):
    pass


def _sol_two_color(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    q.append(v)
                elif color[v] == color[u]:
                    return None
    return color


# ===================================================================
# Exercise 3: Maximum bipartite matching (augmenting-path / Hungarian)
# ===================================================================

def max_matching(left_n, right_n, edges):
    """edges = list of (l, r) pairs (l in [0, left_n), r in [0, right_n))."""
    pass


def _sol_max_matching(left_n, right_n, edges):
    adj = defaultdict(list)
    for l, r in edges:
        adj[l].append(r)
    match_r = [-1] * right_n

    def try_match(l, visited):
        for r in adj[l]:
            if visited[r]:
                continue
            visited[r] = True
            if match_r[r] == -1 or try_match(match_r[r], visited):
                match_r[r] = l
                return True
        return False

    count = 0
    for l in range(left_n):
        visited = [False] * right_n
        if try_match(l, visited):
            count += 1
    return count


# ===================================================================
# Exercise 4: A* shortest path on a 2D grid (Manhattan heuristic)
# ===================================================================

def a_star_grid(grid, start, goal):
    """grid: 2D list of 0 (free) / 1 (blocked). Return shortest path length or -1."""
    pass


def _sol_a_star_grid(grid, start, goal):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    if not rows or not cols:
        return -1
    if grid[start[0]][start[1]] or grid[goal[0]][goal[1]]:
        return -1

    def h(p):
        return abs(p[0] - goal[0]) + abs(p[1] - goal[1])

    pq = [(h(start), 0, start)]
    g_score = {start: 0}
    while pq:
        f, g, p = heapq.heappop(pq)
        if p == goal:
            return g
        if g > g_score.get(p, float("inf")):
            continue
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = p[0] + dr, p[1] + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                ng = g + 1
                if ng < g_score.get((nr, nc), float("inf")):
                    g_score[(nr, nc)] = ng
                    heapq.heappush(pq, (ng + h((nr, nc)), ng, (nr, nc)))
    return -1


# ===================================================================
# Exercise 5: A* vs Dijkstra — node-exploration comparison
# ===================================================================

def compare_astar_dijkstra(grid, start, goal):
    """Return (astar_nodes_explored, dijkstra_nodes_explored)."""
    pass


def _sol_compare_astar_dijkstra(grid, start, goal):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    def search(use_heuristic):
        def h(p):
            return abs(p[0] - goal[0]) + abs(p[1] - goal[1]) if use_heuristic else 0

        pq = [(h(start), 0, start)]
        g_score = {start: 0}
        explored = 0
        while pq:
            f, g, p = heapq.heappop(pq)
            if g > g_score.get(p, float("inf")):
                continue
            explored += 1
            if p == goal:
                return explored
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = p[0] + dr, p[1] + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                    ng = g + 1
                    if ng < g_score.get((nr, nc), float("inf")):
                        g_score[(nr, nc)] = ng
                        heapq.heappush(pq, (ng + h((nr, nc)), ng, (nr, nc)))
        return explored

    return search(True), search(False)


# ===================================================================
# Exercise 6: König's theorem — min vertex cover = max matching (bipartite)
# ===================================================================

def min_vertex_cover_bipartite(left_n, right_n, edges):
    pass


def _sol_min_vertex_cover_bipartite(left_n, right_n, edges):
    return _sol_max_matching(left_n, right_n, edges)


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    print("Day 89 — Bipartite & A* Practice")
    print("=" * 55)
    passed = total = 0

    total += 1
    if _sol_is_bipartite(4, [(0, 1), (1, 2), (2, 3), (3, 0)]):
        print("  PASS: 4-cycle is bipartite")
        passed += 1
    else:
        print("  FAIL: 4-cycle should be bipartite")

    total += 1
    if not _sol_is_bipartite(3, [(0, 1), (1, 2), (2, 0)]):
        print("  PASS: triangle is not bipartite")
        passed += 1
    else:
        print("  FAIL: triangle should not be bipartite")

    total += 1
    colors = _sol_two_color(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
    if colors is not None and colors[0] != colors[1] and colors[1] != colors[2] and colors[2] != colors[3]:
        print(f"  PASS: 2-coloring valid — {colors}")
        passed += 1
    else:
        print(f"  FAIL: 2-coloring got {colors}")

    total += 1
    m = _sol_max_matching(3, 3, [(0, 0), (0, 1), (1, 0), (2, 2)])
    if m == 3:
        print(f"  PASS: max matching = {m}")
        passed += 1
    else:
        print(f"  FAIL: expected 3, got {m}")

    total += 1
    grid = [[0, 0, 0, 0], [0, 1, 1, 0], [0, 0, 0, 0]]
    d = _sol_a_star_grid(grid, (0, 0), (2, 3))
    if d == 5:
        print(f"  PASS: A* shortest path = {d}")
        passed += 1
    else:
        print(f"  FAIL: expected 5, got {d}")

    total += 1
    big = [[0] * 10 for _ in range(10)]
    a, d = _sol_compare_astar_dijkstra(big, (0, 0), (9, 9))
    if a <= d:
        print(f"  PASS: A* nodes {a} <= Dijkstra nodes {d}")
        passed += 1
    else:
        print(f"  FAIL: A* should explore <= Dijkstra")

    print("=" * 55)
    print(f"Results: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
