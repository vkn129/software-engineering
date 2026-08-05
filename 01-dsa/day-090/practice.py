"""
Day 90 Practice: Bipartite Matching & A* Search Exercises

5 exercises building on the main implementation.
Each exercise has a skeleton with TODO markers and a verify function.
Run: python3 practice.py
"""

import heapq
import math
from collections import deque, defaultdict


# ---------------------------------------------------------------------------
# Provided: Hopcroft-Karp (from bipartite_and_astar.py)
# ---------------------------------------------------------------------------

class HopcroftKarp:
    """Maximum bipartite matching — provided for use in exercises."""

    def __init__(self, left_vertices, right_vertices):
        self.left = set(left_vertices)
        self.right = set(right_vertices)
        self.adj = defaultdict(set)
        self.match_left = {}
        self.match_right = {}

    def add_edge(self, u, v):
        self.adj[u].add(v)

    def _bfs(self):
        self.dist = {}
        queue = deque()
        for u in self.left:
            if u not in self.match_left:
                self.dist[u] = 0
                queue.append(u)
        found = False
        while queue:
            u = queue.popleft()
            for v in self.adj[u]:
                next_u = self.match_right.get(v)
                if next_u is None:
                    found = True
                elif next_u not in self.dist:
                    self.dist[next_u] = self.dist[u] + 1
                    queue.append(next_u)
        return found

    def _dfs(self, u):
        for v in self.adj[u]:
            next_u = self.match_right.get(v)
            if next_u is None or (
                next_u in self.dist and
                self.dist[next_u] == self.dist[u] + 1 and
                self._dfs(next_u)
            ):
                self.match_left[u] = v
                self.match_right[v] = u
                return True
        del self.dist[u]
        return False

    def max_matching(self):
        self.match_left = {}
        self.match_right = {}
        matching_size = 0
        while self._bfs():
            for u in self.left:
                if u not in self.match_left:
                    if self._dfs(u):
                        matching_size += 1
        return matching_size, dict(self.match_left)


# ---------------------------------------------------------------------------
# Exercise 1: Maximum Matching in a Bipartite Graph
# ---------------------------------------------------------------------------

def exercise_1_max_bipartite_matching():
    """
    Given students and projects, find the maximum number of students that
    can be assigned to distinct projects.

    Each student has a list of projects they're willing to work on.
    Each project can have at most one student.

    Use Hopcroft-Karp to find the maximum matching.

    Returns:
        tuple: (matching_size, matching_dict)
    """
    students = ["S1", "S2", "S3", "S4", "S5", "S6"]
    projects = ["P1", "P2", "P3", "P4", "P5"]

    # Student preferences (which projects each student will accept)
    preferences = {
        "S1": ["P1", "P2"],
        "S2": ["P1", "P3"],
        "S3": ["P2", "P3", "P4"],
        "S4": ["P3", "P5"],
        "S5": ["P4", "P5"],
        "S6": ["P1"],
    }

    # TODO: Build a HopcroftKarp instance and find the maximum matching
    hk = HopcroftKarp(students, projects)

    for student, prefs in preferences.items():
        for project in prefs:
            hk.add_edge(student, project)

    size, matching = hk.max_matching()

    return size, matching


def test_exercise_1():
    size, matching = exercise_1_max_bipartite_matching()

    # Maximum matching should be 5 (all 5 projects assigned)
    assert size == 5, f"Expected matching size 5, got {size}"

    # Every matched student should be assigned to a project they prefer
    preferences = {
        "S1": ["P1", "P2"],
        "S2": ["P1", "P3"],
        "S3": ["P2", "P3", "P4"],
        "S4": ["P3", "P5"],
        "S5": ["P4", "P5"],
        "S6": ["P1"],
    }
    for student, project in matching.items():
        assert project in preferences[student], \
            f"{student} assigned to {project} but prefers {preferences[student]}"

    # No two students assigned to the same project
    assigned_projects = list(matching.values())
    assert len(assigned_projects) == len(set(assigned_projects)), \
        "Two students assigned to the same project!"

    print("Exercise 1 PASSED: Maximum bipartite matching correct")


# ---------------------------------------------------------------------------
# Exercise 2: A* on Grid with Obstacles
# ---------------------------------------------------------------------------

def exercise_2_astar_grid():
    """
    Implement A* search on a grid with obstacles.

    Grid:
        0 = passable, 1 = wall

    Find the shortest path from top-left (0,0) to bottom-right (7,7)
    using Manhattan distance heuristic.

    Returns:
        dict with 'path', 'cost', 'nodes_explored'
    """
    grid = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    start = (0, 0)
    goal = (7, 7)

    # TODO: Implement A* search with Manhattan heuristic
    # Return dict with 'path', 'cost', 'nodes_explored'

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rows, cols = len(grid), len(grid[0])
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    counter = 0
    open_set = [(manhattan(start, goal), counter, start)]
    came_from = {}
    g_score = {start: 0}
    closed = set()

    while open_set:
        f, _, current = heapq.heappop(open_set)

        if current in closed:
            continue
        closed.add(current)

        if current == goal:
            path = []
            node = goal
            while node != start:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return {
                'path': path,
                'cost': g_score[goal],
                'nodes_explored': len(closed),
            }

        r, c = current
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in closed:
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get((nr, nc), float('inf')):
                    g_score[(nr, nc)] = tentative_g
                    came_from[(nr, nc)] = current
                    counter += 1
                    heapq.heappush(open_set, (tentative_g + manhattan((nr, nc), goal), counter, (nr, nc)))

    return {'path': None, 'cost': float('inf'), 'nodes_explored': len(closed)}


def test_exercise_2():
    result = exercise_2_astar_grid()

    assert result['path'] is not None, "No path found, but one exists"
    assert result['path'][0] == (0, 0), "Path should start at (0,0)"
    assert result['path'][-1] == (7, 7), "Path should end at (7,7)"
    assert result['cost'] == 14, f"Optimal cost should be 14, got {result['cost']}"

    # Verify path is valid (each step is adjacent and passable)
    grid = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    for i in range(len(result['path']) - 1):
        r1, c1 = result['path'][i]
        r2, c2 = result['path'][i + 1]
        assert abs(r1 - r2) + abs(c1 - c2) == 1, f"Non-adjacent step: {(r1, c1)} -> {(r2, c2)}"
        assert grid[r2][c2] == 0, f"Path goes through wall at {(r2, c2)}"

    # A* should explore fewer nodes than the grid size
    assert result['nodes_explored'] < 64, \
        f"A* explored {result['nodes_explored']} nodes (should be well under 64)"

    print(f"Exercise 2 PASSED: A* found optimal path (cost={result['cost']}, "
          f"explored={result['nodes_explored']} nodes)")


# ---------------------------------------------------------------------------
# Exercise 3: 15-Puzzle Solver (simplified — solve a scrambled 8-puzzle)
# ---------------------------------------------------------------------------

def exercise_3_puzzle_solver():
    """
    Solve the 8-puzzle using A* with Manhattan distance heuristic.

    The 8-puzzle is a 3x3 grid with tiles 1-8 and one blank (0).
    Tiles can slide into the blank space.

    Initial state: (2, 8, 3, 1, 6, 4, 7, 0, 5)
    Goal state:    (1, 2, 3, 4, 5, 6, 7, 8, 0)

    Returns:
        dict with 'num_moves' and 'nodes_explored'
    """
    GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
    initial = (2, 8, 3, 1, 6, 4, 7, 0, 5)

    def manhattan_h(state):
        """Sum of Manhattan distances for all tiles."""
        dist = 0
        for idx, val in enumerate(state):
            if val == 0:
                continue
            curr_r, curr_c = idx // 3, idx % 3
            goal_r, goal_c = (val - 1) // 3, (val - 1) % 3
            dist += abs(curr_r - goal_r) + abs(curr_c - goal_c)
        return dist

    def get_neighbors(state):
        """Generate all states reachable by one slide."""
        blank = state.index(0)
        r, c = blank // 3, blank % 3
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_state = list(state)
                new_idx = nr * 3 + nc
                new_state[blank], new_state[new_idx] = new_state[new_idx], new_state[blank]
                neighbors.append(tuple(new_state))
        return neighbors

    # TODO: Implement A* to solve the puzzle
    counter = 0
    open_set = [(manhattan_h(initial), counter, initial)]
    g_score = {initial: 0}
    came_from = {}
    closed = set()

    while open_set:
        f, _, current = heapq.heappop(open_set)

        if current in closed:
            continue
        closed.add(current)

        if current == GOAL:
            # Count moves by tracing back
            moves = 0
            node = current
            while node in came_from:
                node = came_from[node]
                moves += 1
            return {
                'num_moves': moves,
                'nodes_explored': len(closed),
            }

        for neighbor in get_neighbors(current):
            if neighbor in closed:
                continue
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                counter += 1
                heapq.heappush(open_set, (tentative_g + manhattan_h(neighbor), counter, neighbor))

    return None


def test_exercise_3():
    result = exercise_3_puzzle_solver()

    assert result is not None, "Solver returned None — puzzle is solvable"
    assert result['num_moves'] > 0, "Should take at least 1 move"
    assert result['num_moves'] <= 20, \
        f"Optimal solution should be <= 20 moves, got {result['num_moves']}"
    assert result['nodes_explored'] > 0, "Should explore at least 1 node"

    print(f"Exercise 3 PASSED: 8-puzzle solved in {result['num_moves']} moves, "
          f"{result['nodes_explored']} nodes explored")


# ---------------------------------------------------------------------------
# Exercise 4: Worker-Job Assignment with Preferences (Weighted)
# ---------------------------------------------------------------------------

def exercise_4_weighted_assignment():
    """
    Assign workers to jobs to maximize total satisfaction.

    Each worker rates each job they can do from 1-10. We want the assignment
    that maximizes the sum of satisfaction scores.

    Since Hopcroft-Karp finds unweighted matching, we use a greedy approach:
    try all maximum matchings and pick the one with highest total weight.

    Simpler approach: use the max-weight matching via augmenting paths.

    For this exercise, implement a brute-force optimal assignment for small
    instances (verify correctness) and a greedy heuristic for larger ones.

    Returns:
        tuple: (total_score, assignment_dict)
    """
    # Workers, jobs, and satisfaction scores
    scores = {
        ("W1", "J1"): 9, ("W1", "J2"): 5, ("W1", "J3"): 3,
        ("W2", "J1"): 6, ("W2", "J2"): 8, ("W2", "J4"): 7,
        ("W3", "J2"): 4, ("W3", "J3"): 7, ("W3", "J5"): 9,
        ("W4", "J3"): 6, ("W4", "J4"): 8, ("W4", "J5"): 5,
        ("W5", "J1"): 3, ("W5", "J4"): 4, ("W5", "J5"): 6,
    }

    workers = sorted(set(w for w, _ in scores.keys()))
    jobs = sorted(set(j for _, j in scores.keys()))

    # TODO: Find the assignment that maximizes total satisfaction
    # Use brute-force for this small instance (5! = 120 permutations)
    from itertools import permutations

    best_score = -1
    best_assignment = {}

    # Try all possible assignments of workers to jobs
    for perm in permutations(jobs):
        assignment = {}
        total = 0
        valid = True
        for i, worker in enumerate(workers):
            job = perm[i]
            if (worker, job) in scores:
                assignment[worker] = job
                total += scores[(worker, job)]
            else:
                valid = False
                break
        if valid and total > best_score:
            best_score = total
            best_assignment = assignment.copy()

    return best_score, best_assignment


def test_exercise_4():
    total, assignment = exercise_4_weighted_assignment()

    scores = {
        ("W1", "J1"): 9, ("W1", "J2"): 5, ("W1", "J3"): 3,
        ("W2", "J1"): 6, ("W2", "J2"): 8, ("W2", "J4"): 7,
        ("W3", "J2"): 4, ("W3", "J3"): 7, ("W3", "J5"): 9,
        ("W4", "J3"): 6, ("W4", "J4"): 8, ("W4", "J5"): 5,
        ("W5", "J1"): 3, ("W5", "J4"): 4, ("W5", "J5"): 6,
    }

    # Verify the assignment is valid
    assert len(assignment) == 5, f"Should assign all 5 workers, got {len(assignment)}"
    assigned_jobs = list(assignment.values())
    assert len(set(assigned_jobs)) == 5, "Each job should be assigned to exactly one worker"

    # Verify total score matches
    computed_total = sum(scores[(w, j)] for w, j in assignment.items())
    assert computed_total == total, f"Score mismatch: claimed {total}, computed {computed_total}"

    # The optimal assignment should score 39
    # W1->J1(9), W2->J2(8), W3->J5(9), W4->J4(8), W5->... or similar
    assert total >= 38, f"Total score {total} seems suboptimal (expected >= 38)"

    print(f"Exercise 4 PASSED: Optimal assignment with total satisfaction = {total}")
    for w, j in sorted(assignment.items()):
        print(f"  {w} -> {j} (score: {scores[(w, j)]})")


# ---------------------------------------------------------------------------
# Exercise 5: Heuristic Comparison (Manhattan vs Euclidean vs Chebyshev)
# ---------------------------------------------------------------------------

def exercise_5_heuristic_comparison():
    """
    Compare three heuristics on the same grid pathfinding problem.

    Create a 15x15 grid with obstacles, run A* with each heuristic,
    and return the number of nodes explored by each.

    A stronger (but still admissible) heuristic should explore fewer nodes.

    For 4-directional movement:
    - Manhattan is the tightest admissible heuristic
    - Euclidean is admissible but looser
    - Chebyshev is admissible but even looser for 4-dir movement

    Returns:
        dict mapping heuristic name to nodes_explored
    """
    grid = [[0] * 15 for _ in range(15)]

    # Add obstacles
    for r in range(2, 12):
        grid[r][7] = 1   # vertical wall
    grid[6][7] = 0        # gap in wall
    for c in range(3, 13):
        grid[10][c] = 1   # horizontal wall
    grid[10][5] = 0        # gap in wall

    start = (0, 0)
    goal = (14, 14)

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def euclidean(a, b):
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def chebyshev(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def astar(heuristic):
        """Run A* with 4-directional movement and the given heuristic."""
        rows, cols = len(grid), len(grid[0])
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        counter = 0
        open_set = [(heuristic(start, goal), counter, start)]
        g_score = {start: 0}
        closed = set()

        while open_set:
            f, _, current = heapq.heappop(open_set)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                return len(closed)

            r, c = current
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in closed:
                    tentative_g = g_score[current] + 1
                    if tentative_g < g_score.get((nr, nc), float('inf')):
                        g_score[(nr, nc)] = tentative_g
                        counter += 1
                        heapq.heappush(open_set, (tentative_g + heuristic((nr, nc), goal), counter, (nr, nc)))

        return len(closed)  # No path found

    # TODO: Run A* with each heuristic and collect nodes_explored
    results = {
        "manhattan": astar(manhattan),
        "euclidean": astar(euclidean),
        "chebyshev": astar(chebyshev),
    }

    return results


def test_exercise_5():
    results = exercise_5_heuristic_comparison()

    assert "manhattan" in results
    assert "euclidean" in results
    assert "chebyshev" in results

    m = results["manhattan"]
    e = results["euclidean"]
    c = results["chebyshev"]

    # Manhattan should explore <= Euclidean for 4-directional grids
    # (Manhattan is tighter for 4-dir movement)
    assert m <= e, f"Manhattan ({m}) should explore <= Euclidean ({e}) for 4-dir movement"

    # Euclidean should explore <= Chebyshev generally
    # (Euclidean >= Chebyshev as a heuristic value, so it's tighter)
    assert e <= c, f"Euclidean ({e}) should explore <= Chebyshev ({c})"

    print(f"Exercise 5 PASSED: Heuristic comparison")
    print(f"  Manhattan: {m} nodes explored")
    print(f"  Euclidean: {e} nodes explored")
    print(f"  Chebyshev: {c} nodes explored")
    print(f"  Tighter heuristic = fewer nodes explored. Manhattan wins for 4-dir grids.")


# ---------------------------------------------------------------------------
# Run all exercises
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [
        ("Exercise 1: Maximum Bipartite Matching", test_exercise_1),
        ("Exercise 2: A* Grid Pathfinding", test_exercise_2),
        ("Exercise 3: 8-Puzzle Solver", test_exercise_3),
        ("Exercise 4: Weighted Worker-Job Assignment", test_exercise_4),
        ("Exercise 5: Heuristic Comparison", test_exercise_5),
    ]

    passed = 0
    for name, test_fn in tests:
        print(f"\n{'=' * 60}")
        print(f"  {name}")
        print(f"{'=' * 60}")
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  FAILED: {e}")
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'=' * 60}")
    print(f"  Results: {passed}/{len(tests)} exercises passed")
    print(f"{'=' * 60}")
