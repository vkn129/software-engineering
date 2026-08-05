"""
Day 92 Practice: Hopcroft-Karp Bipartite Matching

6 exercises: BFS layering, DFS augmenting, perfect-matching detection,
Hall's condition, vertex-cover via Konig, and applications.
"""

from collections import defaultdict, deque

INF = float("inf")
NIL = -1


# ===================================================================
# Helper
# ===================================================================

def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Hopcroft-Karp Max Matching
# ===================================================================

def hopcroft_karp_match(nL, nR, edges):
    """
    Return max matching size for bipartite graph with nL left, nR right,
    and given edges (u, v).
    """
    # TODO: implement BFS + DFS phased augmenting
    pass


def _sol_hopcroft_karp_match(nL, nR, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    pair_L = [NIL] * nL
    pair_R = [NIL] * nR
    dist = [INF] * nL

    def bfs():
        q = deque()
        for u in range(nL):
            if pair_L[u] == NIL:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = INF
        found = False
        while q:
            u = q.popleft()
            for v in adj[u]:
                pair = pair_R[v]
                if pair == NIL:
                    found = True
                elif dist[pair] == INF:
                    dist[pair] = dist[u] + 1
                    q.append(pair)
        return found

    def dfs(u):
        for v in adj[u]:
            pair = pair_R[v]
            if pair == NIL or (dist[pair] == dist[u] + 1 and dfs(pair)):
                pair_L[u] = v
                pair_R[v] = u
                return True
        dist[u] = INF
        return False

    matching = 0
    while bfs():
        for u in range(nL):
            if pair_L[u] == NIL and dfs(u):
                matching += 1
    return matching


# ===================================================================
# Exercise 2: Has Perfect Matching
# ===================================================================

def has_perfect_matching(nL, nR, edges):
    """Return True iff every left vertex can be matched (size == nL)."""
    # TODO: implement using hopcroft_karp_match
    pass


def _sol_has_perfect_matching(nL, nR, edges):
    return _sol_hopcroft_karp_match(nL, nR, edges) == min(nL, nR)


# ===================================================================
# Exercise 3: Hall's Condition Counter-Example Detector
# ===================================================================
# Given a bipartite graph, find any subset S of left vertices where
# |N(S)| < |S| — i.e. a Hall's-condition violation.

def hall_violation(nL, nR, edges):
    """
    Return a list of left-vertex indices S such that the neighborhood of S
    has size < |S|, or None if no perfect matching is impossible to find
    by Hall.
    Hint: when max matching < nL, the unmatched left vertices + reachable
    nodes via alternating paths form such an S.
    """
    # TODO: implement using a single BFS from unmatched left vertices in
    # the residual matching.
    pass


def _sol_hall_violation(nL, nR, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    pair_L = [NIL] * nL
    pair_R = [NIL] * nR
    dist = [INF] * nL

    def bfs():
        q = deque()
        for u in range(nL):
            if pair_L[u] == NIL:
                dist[u] = 0
                q.append(u)
            else:
                dist[u] = INF
        found = False
        while q:
            u = q.popleft()
            for v in adj[u]:
                pair = pair_R[v]
                if pair == NIL:
                    found = True
                elif dist[pair] == INF:
                    dist[pair] = dist[u] + 1
                    q.append(pair)
        return found

    def dfs(u):
        for v in adj[u]:
            pair = pair_R[v]
            if pair == NIL or (dist[pair] == dist[u] + 1 and dfs(pair)):
                pair_L[u] = v
                pair_R[v] = u
                return True
        dist[u] = INF
        return False

    while bfs():
        for u in range(nL):
            if pair_L[u] == NIL:
                dfs(u)

    if all(p != NIL for p in pair_L):
        return None  # perfect matching on L

    # Build S = set of left vertices reachable from unmatched-L via
    # alternating paths (L -> R via edge, R -> L via matching).
    visited_L = [False] * nL
    visited_R = [False] * nR
    q = deque()
    for u in range(nL):
        if pair_L[u] == NIL:
            visited_L[u] = True
            q.append(u)
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited_R[v]:
                visited_R[v] = True
                pair = pair_R[v]
                if pair != NIL and not visited_L[pair]:
                    visited_L[pair] = True
                    q.append(pair)

    return [u for u in range(nL) if visited_L[u]]


# ===================================================================
# Exercise 4: Min Vertex Cover (Konig's Theorem)
# ===================================================================
# In bipartite graphs: min vertex cover size == max matching size.

def min_vertex_cover_size(nL, nR, edges):
    """Return size of minimum vertex cover via Konig's theorem."""
    # TODO: implement
    pass


def _sol_min_vertex_cover_size(nL, nR, edges):
    return _sol_hopcroft_karp_match(nL, nR, edges)


# ===================================================================
# Exercise 5: Max Independent Set in Bipartite Graph
# ===================================================================
# |MIS| = |V| - |min vertex cover| = nL + nR - max_matching.

def max_independent_set_size(nL, nR, edges):
    """Return size of maximum independent set in the bipartite graph."""
    # TODO: implement
    pass


def _sol_max_independent_set_size(nL, nR, edges):
    return nL + nR - _sol_hopcroft_karp_match(nL, nR, edges)


# ===================================================================
# Exercise 6: Task Assignment Feasibility
# ===================================================================
# Workers have skill sets. Tasks have required skills.
# Worker can do task if their skill set contains the required skill.
# Return: max number of tasks assignable to distinct workers.

def assign_tasks(worker_skills, task_skill):
    """
    worker_skills: list of sets, one per worker
    task_skill: list of required skills (one per task)
    Return: max number of (worker, task) assignments.
    """
    # TODO: build bipartite graph (workers <-> tasks) and run matching.
    pass


def _sol_assign_tasks(worker_skills, task_skill):
    edges = []
    for w, skills in enumerate(worker_skills):
        for t, s in enumerate(task_skill):
            if s in skills:
                edges.append((w, t))
    return _sol_hopcroft_karp_match(len(worker_skills), len(task_skill), edges)


# ===================================================================
# Test Runner
# ===================================================================

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}")
            print(f"    expected: {expected}")
            print(f"    got:      {got}")
            failed += 1

    print("Exercise 1: Hopcroft-Karp Max Matching")
    check("4-4 full match", try_or_sol("hopcroft_karp_match", 4, 4,
          [(0, 0), (0, 1), (1, 0), (1, 2), (2, 1), (2, 3), (3, 2), (3, 3)]), 4)
    check("empty graph", try_or_sol("hopcroft_karp_match", 3, 3, []), 0)
    check("star", try_or_sol("hopcroft_karp_match", 3, 1,
          [(0, 0), (1, 0), (2, 0)]), 1)

    print("\nExercise 2: Has Perfect Matching")
    check("perfect 3-3", try_or_sol("has_perfect_matching", 3, 3,
          [(0, 0), (1, 1), (2, 2)]), True)
    check("imperfect", try_or_sol("has_perfect_matching", 3, 3,
          [(0, 0), (1, 0), (2, 0)]), False)

    print("\nExercise 3: Hall's Violation")
    result = try_or_sol("hall_violation", 3, 3, [(0, 0), (1, 0), (2, 0)])
    # All three left nodes share neighbor {0}, so S = {0,1,2}, |N(S)| = 1 < 3
    check("violation set non-empty", result is not None and len(result) >= 2, True)
    check("no violation for perfect", try_or_sol("hall_violation", 2, 2,
          [(0, 0), (1, 1)]), None)

    print("\nExercise 4: Min Vertex Cover (Konig)")
    check("path graph", try_or_sol("min_vertex_cover_size", 3, 3,
          [(0, 0), (1, 1), (2, 2)]), 3)
    check("star cover", try_or_sol("min_vertex_cover_size", 3, 1,
          [(0, 0), (1, 0), (2, 0)]), 1)

    print("\nExercise 5: Max Independent Set")
    # 3+1 = 4 vertices, matching = 1, so MIS = 3
    check("star MIS", try_or_sol("max_independent_set_size", 3, 1,
          [(0, 0), (1, 0), (2, 0)]), 3)
    # 3+3, matching 3, MIS = 3
    check("perfect MIS", try_or_sol("max_independent_set_size", 3, 3,
          [(0, 0), (1, 1), (2, 2)]), 3)

    print("\nExercise 6: Task Assignment Feasibility")
    workers = [{"python", "ml"}, {"sql"}, {"python"}]
    tasks = ["python", "sql", "ml"]
    check("3 of 3 tasks", try_or_sol("assign_tasks", workers, tasks), 3)

    workers2 = [{"a"}, {"a"}]
    tasks2 = ["a", "b"]
    check("only skill a", try_or_sol("assign_tasks", workers2, tasks2), 1)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
