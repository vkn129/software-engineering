"""
Day 91 Practice: Dependency Resolver Capstone

6 exercises integrating topological sort, SCC, articulation points,
BFS levels, reachability, and cycle-breaking strategies.
Implement the TODO functions, then run: python practice.py
"""

from collections import defaultdict, deque


# ===================================================================
# Exercise 1: Build Dependency Graph and Return Install Order
# ===================================================================
# Given a dict of package -> list of dependencies, return a valid
# topological install order (dependencies before dependents).
# Return [] if cycles make ordering impossible.

def install_order(packages):
    """
    packages: dict mapping package name -> list of dependency names
              e.g. {"flask": ["werkzeug", "jinja2"], "jinja2": ["markupsafe"], ...}
    Returns: list of package names in valid install order, or [] if cycles exist.
    """
    # TODO: implement topological sort (Kahn's algorithm)
    pass


def _sol_install_order(packages):
    all_pkgs = set(packages.keys())
    for deps in packages.values():
        all_pkgs.update(deps)

    # Build reverse adjacency and in-degrees
    rev = defaultdict(list)
    in_deg = {pkg: 0 for pkg in all_pkgs}
    adj = defaultdict(list)

    for pkg, deps in packages.items():
        adj[pkg] = deps
        for dep in deps:
            rev[dep].append(pkg)
            in_deg[pkg] += 1

    # Ensure packages with no listed deps have in_deg entry
    for pkg in all_pkgs:
        if pkg not in adj:
            adj[pkg] = []
            # in_deg already 0

    queue = deque(sorted(p for p in all_pkgs if in_deg[p] == 0))
    order = []

    while queue:
        pkg = queue.popleft()
        order.append(pkg)
        for dependent in sorted(rev[pkg]):
            in_deg[dependent] -= 1
            if in_deg[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(all_pkgs):
        return []
    return order


# ===================================================================
# Exercise 2: Detect All Circular Dependency Groups (SCC)
# ===================================================================
# Find all groups of packages involved in circular dependencies.
# Uses Tarjan's SCC algorithm — return only SCCs with 2+ members.

def find_circular_groups(packages):
    """
    packages: dict mapping package name -> list of dependency names
    Returns: list of sorted lists, each containing packages in a cycle group.
    """
    # TODO: implement Tarjan's SCC, filter to components with size > 1
    pass


def _sol_find_circular_groups(packages):
    all_pkgs = set(packages.keys())
    for deps in packages.values():
        all_pkgs.update(deps)

    adj = defaultdict(list)
    for pkg, deps in packages.items():
        adj[pkg] = deps
    for pkg in all_pkgs:
        if pkg not in adj:
            adj[pkg] = []

    disc = {}
    low = {}
    on_stack = set()
    stack = []
    time_c = [0]
    sccs = []

    def dfs(u):
        disc[u] = low[u] = time_c[0]
        time_c[0] += 1
        stack.append(u)
        on_stack.add(u)

        for v in adj[u]:
            if v not in disc:
                dfs(v)
                low[u] = min(low[u], low[v])
            elif v in on_stack:
                low[u] = min(low[u], disc[v])

        if low[u] == disc[u]:
            component = []
            while True:
                v = stack.pop()
                on_stack.remove(v)
                component.append(v)
                if v == u:
                    break
            if len(component) > 1:
                sccs.append(sorted(component))

    for pkg in sorted(all_pkgs):
        if pkg not in disc:
            dfs(pkg)

    return sccs


# ===================================================================
# Exercise 3: Find Critical Packages (Articulation Points)
# ===================================================================
# Treat the dependency graph as undirected and find articulation points.
# These are packages whose removal would disconnect parts of the graph.

def find_critical_packages(packages):
    """
    packages: dict mapping package name -> list of dependency names
    Returns: sorted list of critical package names (articulation points).
    """
    # TODO: build undirected graph, run Tarjan's articulation point algorithm
    pass


def _sol_find_critical_packages(packages):
    all_pkgs = set(packages.keys())
    for deps in packages.values():
        all_pkgs.update(deps)

    # Build undirected graph
    undirected = defaultdict(set)
    for pkg, deps in packages.items():
        for dep in deps:
            undirected[pkg].add(dep)
            undirected[dep].add(pkg)

    disc = {}
    low = {}
    parent = {}
    ap_set = set()
    time_c = [0]

    def dfs(u):
        disc[u] = low[u] = time_c[0]
        time_c[0] += 1
        children = 0

        for v in sorted(undirected[u]):
            if v not in disc:
                children += 1
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])

                if parent.get(u) is None and children > 1:
                    ap_set.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    ap_set.add(u)
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for pkg in sorted(all_pkgs):
        if pkg not in disc:
            parent[pkg] = None
            dfs(pkg)

    return sorted(ap_set)


# ===================================================================
# Exercise 4: Parallel Install Schedule (BFS Levels)
# ===================================================================
# Compute which packages can be installed simultaneously.
# Level 0 = no deps, Level 1 = depends only on level 0, etc.

def parallel_schedule(packages):
    """
    packages: dict mapping package name -> list of dependency names
    Returns: dict mapping level (int) -> sorted list of packages at that level.
             Returns None if cycles prevent full scheduling.
    """
    # TODO: use Kahn's algorithm with level tracking
    pass


def _sol_parallel_schedule(packages):
    all_pkgs = set(packages.keys())
    for deps in packages.values():
        all_pkgs.update(deps)

    adj = defaultdict(list)
    rev = defaultdict(list)
    in_deg = {pkg: 0 for pkg in all_pkgs}

    for pkg, deps in packages.items():
        adj[pkg] = deps
        for dep in deps:
            rev[dep].append(pkg)
            in_deg[pkg] += 1

    for pkg in all_pkgs:
        if pkg not in adj:
            adj[pkg] = []

    levels = {}
    queue = deque()
    for pkg in sorted(all_pkgs):
        if in_deg[pkg] == 0:
            queue.append(pkg)
            levels[pkg] = 0

    result = defaultdict(list)
    while queue:
        pkg = queue.popleft()
        result[levels[pkg]].append(pkg)
        for dependent in sorted(rev[pkg]):
            in_deg[dependent] -= 1
            if in_deg[dependent] == 0:
                levels[dependent] = levels[pkg] + 1
                queue.append(dependent)

    if len(levels) != len(all_pkgs):
        return None

    return {k: sorted(v) for k, v in result.items()}


# ===================================================================
# Exercise 5: Minimum Packages to Install a Target
# ===================================================================
# Find the minimal set of packages needed to install a given target.
# This is all transitive dependencies reachable from target.

def minimal_install(packages, target):
    """
    packages: dict mapping package name -> list of dependency names
    target: the package to install
    Returns: sorted list of all packages needed (including target itself).
    """
    # TODO: BFS/DFS from target following dependency edges
    pass


def _sol_minimal_install(packages, target):
    adj = defaultdict(list)
    all_pkgs = set(packages.keys())
    for deps in packages.values():
        all_pkgs.update(deps)
    for pkg, deps in packages.items():
        adj[pkg] = deps
    for pkg in all_pkgs:
        if pkg not in adj:
            adj[pkg] = []

    if target not in all_pkgs:
        return []

    needed = set()
    queue = deque([target])
    needed.add(target)

    while queue:
        pkg = queue.popleft()
        for dep in adj[pkg]:
            if dep not in needed:
                needed.add(dep)
                queue.append(dep)

    return sorted(needed)


# ===================================================================
# Exercise 6: Suggest Dependency Removals to Break All Cycles
# ===================================================================
# Given a graph with cycles, find edges within SCCs that could be
# removed to eliminate all circular dependencies. For each SCC,
# suggest removing one back edge to break the cycle.

def suggest_cycle_breaks(packages):
    """
    packages: dict mapping package name -> list of dependency names
    Returns: list of (pkg, dep) tuples — edges to remove to break all cycles.
             For each SCC, find one edge that, if removed, breaks the cycle.
    """
    # TODO: find SCCs, then for each SCC find a back edge to cut
    pass


def _sol_suggest_cycle_breaks(packages):
    all_pkgs = set(packages.keys())
    for deps in packages.values():
        all_pkgs.update(deps)

    adj = defaultdict(list)
    for pkg, deps in packages.items():
        adj[pkg] = deps
    for pkg in all_pkgs:
        if pkg not in adj:
            adj[pkg] = []

    # Find SCCs using Tarjan's
    disc = {}
    low = {}
    on_stack = set()
    stack = []
    time_c = [0]
    sccs = []

    def dfs(u):
        disc[u] = low[u] = time_c[0]
        time_c[0] += 1
        stack.append(u)
        on_stack.add(u)

        for v in adj[u]:
            if v not in disc:
                dfs(v)
                low[u] = min(low[u], low[v])
            elif v in on_stack:
                low[u] = min(low[u], disc[v])

        if low[u] == disc[u]:
            component = []
            while True:
                v = stack.pop()
                on_stack.remove(v)
                component.append(v)
                if v == u:
                    break
            if len(component) > 1:
                sccs.append(sorted(component))

    for pkg in sorted(all_pkgs):
        if pkg not in disc:
            dfs(pkg)

    # For each SCC, find one back edge to cut
    # Strategy: DFS within the SCC, find a back edge (an edge that points
    # from a descendant to an ancestor in the DFS tree)
    removals = []

    for scc in sccs:
        scc_set = set(scc)
        # Find any edge within the SCC that completes a cycle
        # Simple approach: DFS and find the first back edge
        visited = set()
        found = [False]

        def dfs_find_back(u, path_set):
            if found[0]:
                return
            visited.add(u)
            path_set.add(u)
            for v in adj[u]:
                if found[0]:
                    return
                if v in scc_set:
                    if v in path_set and v in visited:
                        # Back edge found — this closes a cycle
                        removals.append((u, v))
                        found[0] = True
                        return
                    if v not in visited:
                        dfs_find_back(v, path_set)
            path_set.remove(u)

        dfs_find_back(scc[0], set())

    return sorted(removals)


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

    # --- Test data ---
    simple_pkgs = {
        "flask": ["werkzeug", "jinja2"],
        "jinja2": ["markupsafe"],
        "werkzeug": ["markupsafe"],
        "markupsafe": [],
    }

    cyclic_pkgs = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"],
        "D": ["E"],
        "E": ["D"],
        "F": [],
    }

    web_pkgs = {
        "app": ["flask", "sqlalchemy", "requests"],
        "flask": ["werkzeug", "jinja2", "click"],
        "werkzeug": ["markupsafe"],
        "jinja2": ["markupsafe"],
        "markupsafe": [],
        "click": [],
        "sqlalchemy": ["sqlite-driver"],
        "sqlite-driver": [],
        "requests": ["urllib3", "certifi"],
        "urllib3": [],
        "certifi": [],
    }

    # --- Exercise 1: Install Order ---
    print("\nExercise 1: Install Order (Topological Sort)")
    order = try_or_sol(install_order, _sol_install_order, simple_pkgs)
    # Verify it's a valid topological order
    pos = {pkg: i for i, pkg in enumerate(order)}
    valid = all(
        pos.get(dep, -1) < pos.get(pkg, -1)
        for pkg, deps in simple_pkgs.items()
        for dep in deps
    )
    check("simple graph produces valid order", valid, True)
    check("all packages included", len(order), 4)

    cyclic_order = try_or_sol(install_order, _sol_install_order, cyclic_pkgs)
    check("cyclic graph returns empty", cyclic_order, [])

    # --- Exercise 2: Circular Dependency Groups ---
    print("\nExercise 2: Circular Dependency Groups (SCC)")
    groups = try_or_sol(find_circular_groups, _sol_find_circular_groups, cyclic_pkgs)
    group_sets = [frozenset(g) for g in groups]
    check("finds A-B-C cycle", frozenset(["A", "B", "C"]) in group_sets, True)
    check("finds D-E cycle", frozenset(["D", "E"]) in group_sets, True)
    check("exactly 2 cycle groups", len(groups), 2)

    no_cycles = try_or_sol(find_circular_groups, _sol_find_circular_groups, simple_pkgs)
    check("acyclic graph has no cycle groups", no_cycles, [])

    # --- Exercise 3: Critical Packages ---
    print("\nExercise 3: Critical Packages (Articulation Points)")
    critical = try_or_sol(find_critical_packages, _sol_find_critical_packages, web_pkgs)
    # markupsafe connects werkzeug/jinja2 subtree; flask connects app to its deps
    check("flask is critical", "flask" in critical, True)
    # `app` is NOT a leaf here — it has three children, so removing it splits the
    # graph and it IS an articulation point. `click` is the genuine leaf: flask is
    # its only neighbour, so deleting it disconnects nothing.
    check("click is not critical (leaf)", "click" not in critical, True)

    # --- Exercise 4: Parallel Schedule ---
    print("\nExercise 4: Parallel Install Schedule (BFS Levels)")
    schedule = try_or_sol(parallel_schedule, _sol_parallel_schedule, simple_pkgs)
    check("level 0 has markupsafe", "markupsafe" in schedule[0], True)
    check("flask is at highest level", "flask" in schedule[max(schedule.keys())], True)

    cyclic_sched = try_or_sol(parallel_schedule, _sol_parallel_schedule, cyclic_pkgs)
    check("cyclic graph returns None", cyclic_sched, None)

    # --- Exercise 5: Minimal Install ---
    print("\nExercise 5: Minimal Install for Target")
    minimal = try_or_sol(minimal_install, _sol_minimal_install, web_pkgs, "flask")
    check("flask needs flask itself", "flask" in minimal, True)
    check("flask needs markupsafe", "markupsafe" in minimal, True)
    check("flask doesn't need requests", "requests" not in minimal, True)
    check("flask doesn't need sqlalchemy", "sqlalchemy" not in minimal, True)
    check("flask minimal count", len(minimal), 5)  # flask, werkzeug, jinja2, markupsafe, click

    # --- Exercise 6: Cycle Break Suggestions ---
    print("\nExercise 6: Suggest Cycle Breaks")
    breaks = try_or_sol(suggest_cycle_breaks, _sol_suggest_cycle_breaks, cyclic_pkgs)
    check("suggests 2 removals (one per cycle)", len(breaks), 2)

    # Verify that removing suggested edges actually breaks all cycles
    # Build graph without suggested edges and check for cycles
    modified = {pkg: [d for d in deps if (pkg, d) not in breaks]
                for pkg, deps in cyclic_pkgs.items()}
    remaining_cycles = _sol_find_circular_groups(modified)
    check("removing suggested edges breaks all cycles", remaining_cycles, [])

    # --- Summary ---
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")


if __name__ == "__main__":
    run_tests()
