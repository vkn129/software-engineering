"""
Day 80 Practice: Depth-First Search

6 exercises building DFS intuition — from iterative implementation to
structural analysis. Implement the TODO functions, then run: python practice.py
"""

from collections import defaultdict


def make_graph(edges, directed=False):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        if not directed:
            adj[v].append(u)
    return adj


# ===================================================================
# Exercise 1: Iterative DFS
# ===================================================================
# Implement DFS using an explicit stack instead of recursion.
# This avoids Python's ~1000 recursion limit for deep graphs.

def dfs_iterative(adj, start):
    """Return list of vertices in DFS visit order, starting from start."""
    # TODO: implement using a stack (list with append/pop)
    pass


def _sol_dfs_iterative(adj, start):
    visited = set()
    order = []
    stack = [start]
    while stack:
        u = stack.pop()
        if u in visited:
            continue
        visited.add(u)
        order.append(u)
        for v in reversed(adj[u]):
            if v not in visited:
                stack.append(v)
    return order


# ===================================================================
# Exercise 2: Cycle Detection in Directed Graph
# ===================================================================
# Use the 3-color method (WHITE/GRAY/BLACK) to detect cycles.
# A cycle exists iff DFS encounters a back edge (edge to a GRAY vertex).

WHITE, GRAY, BLACK = 0, 1, 2

def has_cycle(adj, vertices):
    """Return True if directed graph has a cycle, False otherwise."""
    # TODO: implement using 3-color DFS
    pass


def _sol_has_cycle(adj, vertices):
    color = {v: WHITE for v in vertices}

    def _dfs(u):
        color[u] = GRAY
        for v in adj[u]:
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and _dfs(v):
                return True
        color[u] = BLACK
        return False

    return any(_dfs(v) for v in vertices if color[v] == WHITE)


# ===================================================================
# Exercise 3: Find All Paths Between Two Vertices
# ===================================================================
# Use DFS with backtracking to enumerate every simple path.
# Must remove vertices from visited set when backtracking.

def all_paths(adj, start, end):
    """Return list of all simple paths from start to end."""
    # TODO: implement with DFS + backtracking
    pass


def _sol_all_paths(adj, start, end):
    result = []

    def _dfs(u, path, visited):
        if u == end:
            result.append(path[:])
            return
        for v in adj[u]:
            if v not in visited:
                visited.add(v)
                path.append(v)
                _dfs(v, path, visited)
                path.pop()
                visited.remove(v)

    _dfs(start, [start], {start})
    return result


# ===================================================================
# Exercise 4: Largest Connected Component
# ===================================================================
# Find the size of the largest connected component in an undirected graph.
# Each DFS from an unvisited vertex discovers one component.

def largest_component(adj, vertices):
    """Return the size of the largest connected component."""
    # TODO: implement this
    pass


def _sol_largest_component(adj, vertices):
    visited = set()
    max_size = 0

    def _dfs(u):
        count = 1
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                count += _dfs(v)
        return count

    for v in vertices:
        if v not in visited:
            size = _dfs(v)
            max_size = max(max_size, size)

    return max_size


# ===================================================================
# Exercise 5: DFS with Discovery/Finish Timestamps
# ===================================================================
# Assign timestamps as DFS discovers and finishes each vertex.
# These timestamps power topological sort, ancestor checks, and SCC.

def dfs_timestamps(adj, vertices):
    """
    Return (discovery, finish) dicts mapping vertex -> timestamp.
    Time starts at 1 and increments on each discovery and each finish.
    """
    # TODO: implement this
    pass


def _sol_dfs_timestamps(adj, vertices):
    disc = {}
    finish = {}
    time = [0]
    visited = set()

    def _dfs(u):
        visited.add(u)
        time[0] += 1
        disc[u] = time[0]
        for v in adj[u]:
            if v not in visited:
                _dfs(v)
        time[0] += 1
        finish[u] = time[0]

    for v in vertices:
        if v not in visited:
            _dfs(v)

    return disc, finish


# ===================================================================
# Exercise 6: Is Tree Check
# ===================================================================
# An undirected graph is a tree iff it's connected AND has no cycles.
# Equivalently: connected and has exactly V-1 edges.
# Use DFS to check both properties in one pass.

def is_tree(adj, vertices):
    """Return True if the undirected graph is a tree."""
    # TODO: implement — check connected + no cycles using DFS
    pass


def _sol_is_tree(adj, vertices):
    if not vertices:
        return True

    visited = set()

    def _dfs(u, parent):
        """Returns False if cycle detected."""
        visited.add(u)
        for v in adj[u]:
            if v not in visited:
                if not _dfs(v, u):
                    return False
            elif v != parent:
                # Back edge to non-parent = cycle
                return False
        return True

    # Must be acyclic (DFS finds no back edges)
    start = vertices[0]
    if not _dfs(start, -1):
        return False

    # Must be connected (all vertices visited from single start)
    return len(visited) == len(vertices)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected}")
            print(f"    Got:      {got}")

    def try_or_sol(student_fn, sol_fn, *args, **kwargs):
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
        return sol_fn(*args, **kwargs)

    # --- Exercise 1: Iterative DFS ---
    print("\nExercise 1: Iterative DFS")
    adj = make_graph([(0, 1), (0, 2), (1, 3), (2, 4)])
    result = try_or_sol(dfs_iterative, _sol_dfs_iterative, adj, 0)
    check("visits all 5 vertices", sorted(result), [0, 1, 2, 3, 4])
    check("starts at 0", result[0], 0)
    # DFS should visit deeper before wider
    check("visits 5 vertices total", len(result), 5)

    # --- Exercise 2: Cycle Detection ---
    print("\nExercise 2: Cycle Detection (directed)")
    dag = make_graph([(0, 1), (0, 2), (1, 3), (2, 3)], directed=True)
    check("DAG has no cycle",
          try_or_sol(has_cycle, _sol_has_cycle, dag, [0, 1, 2, 3]), False)

    cyclic = make_graph([(0, 1), (1, 2), (2, 0)], directed=True)
    check("0->1->2->0 has cycle",
          try_or_sol(has_cycle, _sol_has_cycle, cyclic, [0, 1, 2]), True)

    self_loop = defaultdict(list)
    self_loop[0] = [0]
    check("self-loop is a cycle",
          try_or_sol(has_cycle, _sol_has_cycle, self_loop, [0]), True)

    # --- Exercise 3: All Paths ---
    print("\nExercise 3: All Paths")
    adj = make_graph([(0, 1), (0, 2), (1, 3), (2, 3)])
    paths = try_or_sol(all_paths, _sol_all_paths, adj, 0, 3)
    # Sort paths for deterministic comparison
    paths_sorted = sorted([tuple(p) for p in paths])
    check("two paths from 0 to 3", len(paths_sorted), 2)
    check("paths are correct",
          paths_sorted, [(0, 1, 3), (0, 2, 3)])

    # --- Exercise 4: Largest Component ---
    print("\nExercise 4: Largest Connected Component")
    adj = make_graph([(0, 1), (2, 3), (3, 4), (3, 5)])
    for v in range(6):
        if v not in adj:
            adj[v] = []
    check("largest component size=4",
          try_or_sol(largest_component, _sol_largest_component,
                     adj, list(range(6))), 4)

    # Single vertices
    adj2 = defaultdict(list)
    for v in range(3):
        adj2[v] = []
    check("isolated vertices, size=1",
          try_or_sol(largest_component, _sol_largest_component,
                     adj2, [0, 1, 2]), 1)

    # --- Exercise 5: Timestamps ---
    print("\nExercise 5: DFS Timestamps")
    adj = make_graph([(0, 1), (1, 2)], directed=True)
    disc, finish = try_or_sol(dfs_timestamps, _sol_dfs_timestamps,
                              adj, [0, 1, 2])
    check("vertex 0 discovered first", disc[0], 1)
    check("vertex 2 finishes before 1", finish[2] < finish[1], True)
    check("vertex 0 finishes last", finish[0] == max(finish.values()), True)
    # Parenthesis property: disc[0] < disc[1] < finish[1] < finish[0]
    check("parenthesis property",
          disc[0] < disc[1] < finish[1] < finish[0], True)

    # --- Exercise 6: Is Tree ---
    print("\nExercise 6: Is Tree Check")
    # A tree: connected, no cycles, V-1 edges
    tree = make_graph([(0, 1), (1, 2), (1, 3)])
    check("connected acyclic = tree",
          try_or_sol(is_tree, _sol_is_tree, tree, [0, 1, 2, 3]), True)

    # Has a cycle
    cyclic = make_graph([(0, 1), (1, 2), (2, 0)])
    check("triangle = not a tree",
          try_or_sol(is_tree, _sol_is_tree, cyclic, [0, 1, 2]), False)

    # Disconnected (forest, not a tree)
    forest = make_graph([(0, 1), (2, 3)])
    for v in range(4):
        if v not in forest:
            forest[v] = []
    check("disconnected = not a tree",
          try_or_sol(is_tree, _sol_is_tree, forest, [0, 1, 2, 3]), False)

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")


if __name__ == "__main__":
    run_tests()
