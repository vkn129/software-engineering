"""
Day 87 Practice: Strongly Connected Components
6 exercises covering Kosaraju, Tarjan, condensation, 2-SAT, and deadlock.
Implement the TODO functions, then run: python3 practice.py
"""
from collections import defaultdict
import sys
sys.setrecursionlimit(10**6)


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        result = student_fn(*args, **kwargs)
        if result is not None:
            return result
    return sol_fn(*args, **kwargs)


# ===================================================================
# Exercise 1: Kosaraju's Algorithm — two-pass DFS for SCC
# ===================================================================

def kosaraju(n, edges):
    """n: nodes (0..n-1), edges: list of (u, v) directed edges.
    Returns: sorted list of SCCs, each SCC a sorted list of node IDs."""
    pass


def _sol_kosaraju(n, edges):
    adj = defaultdict(list)
    rev = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        rev[v].append(u)
    visited = [False] * n
    order = []

    def dfs1(u):
        stack = [(u, iter(adj[u]))]
        visited[u] = True
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                order.append(node)
                stack.pop()
            elif not visited[nxt]:
                visited[nxt] = True
                stack.append((nxt, iter(adj[nxt])))

    for i in range(n):
        if not visited[i]:
            dfs1(i)

    comp = [-1] * n

    def dfs2(start, c):
        stack = [start]
        comp[start] = c
        while stack:
            x = stack.pop()
            for y in rev[x]:
                if comp[y] == -1:
                    comp[y] = c
                    stack.append(y)

    c = 0
    for u in reversed(order):
        if comp[u] == -1:
            dfs2(u, c)
            c += 1
    sccs = defaultdict(list)
    for i, ci in enumerate(comp):
        sccs[ci].append(i)
    return sorted(sorted(s) for s in sccs.values())


# ===================================================================
# Exercise 2: Tarjan's Algorithm — single-pass DFS for SCC
# ===================================================================

def tarjan_scc(n, edges):
    """Same I/O as kosaraju. Use disc/low low-link tracking."""
    pass


def _sol_tarjan_scc(n, edges):
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    disc = [-1] * n
    low = [-1] * n
    on_stack = [False] * n
    stack = []
    sccs = []
    timer = [0]

    def dfs(u):
        disc[u] = low[u] = timer[0]
        timer[0] += 1
        stack.append(u)
        on_stack[u] = True
        for v in adj[u]:
            if disc[v] == -1:
                dfs(v)
                low[u] = min(low[u], low[v])
            elif on_stack[v]:
                low[u] = min(low[u], disc[v])
        if low[u] == disc[u]:
            comp = []
            while True:
                v = stack.pop()
                on_stack[v] = False
                comp.append(v)
                if v == u:
                    break
            sccs.append(sorted(comp))

    for i in range(n):
        if disc[i] == -1:
            dfs(i)
    return sorted(sccs)


# ===================================================================
# Exercise 3: Condensation DAG
# ===================================================================

def condensation(n, edges):
    """Return (num_sccs, sorted_list_of_edges_in_condensation).
    Each condensation edge is (c1, c2) where c1, c2 are SCC IDs."""
    pass


def _sol_condensation(n, edges):
    sccs = _sol_tarjan_scc(n, edges)
    node_to_comp = {}
    for i, s in enumerate(sccs):
        for u in s:
            node_to_comp[u] = i
    cond_edges = set()
    for u, v in edges:
        cu, cv = node_to_comp[u], node_to_comp[v]
        if cu != cv:
            cond_edges.add((cu, cv))
    return len(sccs), sorted(cond_edges)


# ===================================================================
# Exercise 4: Find mutually recursive function groups
# ===================================================================

def find_recursion_groups(functions):
    """functions: dict mapping name -> list of called function names.
    Return list of groups (size >= 2) of mutually recursive functions."""
    pass


def _sol_find_recursion_groups(functions):
    names = sorted(functions.keys())
    idx = {n: i for i, n in enumerate(names)}
    edges = []
    for f, calls in functions.items():
        for c in calls:
            if c in idx:
                edges.append((idx[f], idx[c]))
    sccs = _sol_tarjan_scc(len(names), edges)
    return sorted([sorted(names[i] for i in s) for s in sccs if len(s) > 1])


# ===================================================================
# Exercise 5: 2-SAT solver via SCC
# ===================================================================

def two_sat(num_vars, clauses):
    """clauses: list of ((var1, is_pos1), (var2, is_pos2))
    Return (satisfiable, assignment_dict). assignment maps var -> True/False."""
    pass


def _sol_two_sat(num_vars, clauses):
    n = 2 * num_vars

    def node(var, pos):
        return 2 * var + (0 if pos else 1)

    def neg(x):
        return x ^ 1

    edges = []
    for (v1, p1), (v2, p2) in clauses:
        a, b = node(v1, p1), node(v2, p2)
        edges.append((neg(a), b))
        edges.append((neg(b), a))
    sccs = _sol_tarjan_scc(n, edges)
    comp = [0] * n
    for i, s in enumerate(sccs):
        for u in s:
            comp[u] = i
    assignment = {}
    for v in range(num_vars):
        if comp[2 * v] == comp[2 * v + 1]:
            return False, {}
        assignment[v] = comp[2 * v] > comp[2 * v + 1]
    return True, assignment


# ===================================================================
# Exercise 6: Deadlock detection via SCC on resource allocation graph
# ===================================================================

def detect_deadlock(num_processes, hold_request):
    """hold_request: list of (process_id, resource_id, action) where
    action is 'hold' or 'request'.
    Return list of deadlocked process groups (each sorted)."""
    pass


def _sol_detect_deadlock(num_processes, hold_request):
    resources = sorted({r for _, r, _ in hold_request})
    res_idx = {r: num_processes + i for i, r in enumerate(resources)}
    n = num_processes + len(resources)
    edges = []
    for p, r, a in hold_request:
        if a == "hold":
            edges.append((res_idx[r], p))
        else:
            edges.append((p, res_idx[r]))
    sccs = _sol_tarjan_scc(n, edges)
    deadlocked = []
    for s in sccs:
        if len(s) > 1:
            procs = sorted(x for x in s if x < num_processes)
            if procs:
                deadlocked.append(procs)
    return sorted(deadlocked)


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    print("Day 87 — SCC Practice Tests")
    print("=" * 55)
    passed = total = 0

    total += 1
    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)]
    r = _sol_kosaraju(6, edges)
    if r == [[0, 1, 2], [3, 4, 5]]:
        print(f"  PASS: kosaraju — {r}")
        passed += 1
    else:
        print(f"  FAIL: kosaraju got {r}")

    total += 1
    r = _sol_tarjan_scc(6, edges)
    if r == [[0, 1, 2], [3, 4, 5]]:
        print(f"  PASS: tarjan — {r}")
        passed += 1
    else:
        print(f"  FAIL: tarjan got {r}")

    total += 1
    nc, ce = _sol_condensation(6, edges)
    if nc == 2 and len(ce) == 1:
        print(f"  PASS: condensation — {nc} SCCs, {len(ce)} edge")
        passed += 1
    else:
        print(f"  FAIL: condensation got {nc} SCCs, edges={ce}")

    total += 1
    funcs = {"a": ["b"], "b": ["a", "c"], "c": ["d"], "d": ["c"], "e": []}
    g = _sol_find_recursion_groups(funcs)
    if g == [["a", "b"], ["c", "d"]]:
        print(f"  PASS: recursion groups — {g}")
        passed += 1
    else:
        print(f"  FAIL: recursion groups got {g}")

    total += 1
    clauses = [((0, True), (1, True)), ((0, False), (1, True)), ((0, True), (1, False))]
    sat, _ = _sol_two_sat(2, clauses)
    if sat:
        print(f"  PASS: 2-SAT satisfiable")
        passed += 1
    else:
        print(f"  FAIL: 2-SAT should be sat")

    total += 1
    actions = [(0, "R0", "hold"), (0, "R1", "request"),
               (1, "R1", "hold"), (1, "R0", "request")]
    dl = _sol_detect_deadlock(2, actions)
    if dl == [[0, 1]]:
        print(f"  PASS: deadlock — {dl}")
        passed += 1
    else:
        print(f"  FAIL: deadlock got {dl}")

    print("=" * 55)
    print(f"Results: {passed}/{total} passed")


if __name__ == "__main__":
    run_tests()
