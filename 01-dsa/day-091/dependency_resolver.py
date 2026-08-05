"""
Day 91: Graph Algorithms Capstone — Dependency Resolver

A realistic dependency resolver integrating topological sort, cycle detection,
SCC, BFS levels, articulation points, and reachability analysis. This is how
package managers like npm, pip, and cargo work under the hood.
"""

from collections import defaultdict, deque


class DependencyGraph:
    """
    A dependency resolver that models packages as a directed graph.
    Edge A -> B means "A depends on B" (B must be installed before A).
    """

    def __init__(self):
        # adj[pkg] = list of packages that pkg depends on
        self.adj = defaultdict(list)
        # reverse adj for reachability queries (who depends on pkg?)
        self.rev = defaultdict(list)
        self.packages = set()
        self.versions = {}  # pkg -> version string

    def add_package(self, name, version="1.0.0", dependencies=None):
        """
        Register a package with its version and dependencies.

        name: package name (string)
        version: version string
        dependencies: list of package names this package depends on
        """
        self.packages.add(name)
        self.versions[name] = version
        if dependencies is None:
            dependencies = []
        self.adj[name] = dependencies[:]
        for dep in dependencies:
            self.packages.add(dep)
            self.rev[dep].append(name)
            # Ensure dep exists in adj even if not explicitly added
            if dep not in self.adj:
                self.adj[dep] = []

    def resolve(self):
        """
        Topological sort to get a valid install order.
        Uses Kahn's algorithm (BFS-based) so we can also detect cycles.

        Returns: (order, is_valid) where order is the install sequence
                 and is_valid is False if cycles exist.
        """
        # Compute in-degrees (number of dependencies for each package)
        in_degree = defaultdict(int)
        for pkg in self.packages:
            in_degree[pkg]  # ensure all packages are present
        for pkg in self.packages:
            for dep in self.adj[pkg]:
                in_degree[pkg] += 0  # pkg depends on dep
                # We want install order: dep before pkg
                # In our graph, edge is pkg -> dep (pkg depends on dep)
                # For topo sort, we need to count how many things point TO a node
                pass

        # Recount properly: in the install DAG, we need to install dependencies first.
        # Edge pkg -> dep means dep must come before pkg.
        # So in the "install order" DAG, the edge direction is dep -> pkg (dep enables pkg).
        # in_degree[pkg] = number of dependencies of pkg that haven't been installed yet.
        in_deg = {pkg: 0 for pkg in self.packages}
        for pkg in self.packages:
            in_deg[pkg] = len(self.adj[pkg])

        queue = deque()
        for pkg in sorted(self.packages):  # sorted for deterministic output
            if in_deg[pkg] == 0:
                queue.append(pkg)

        order = []
        while queue:
            pkg = queue.popleft()
            order.append(pkg)
            # This package is now "installed" — unlock packages that depend on it
            for dependent in sorted(self.rev.get(pkg, [])):
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    queue.append(dependent)

        is_valid = len(order) == len(self.packages)
        return order, is_valid

    def detect_cycles(self):
        """
        Find circular dependencies using Tarjan's SCC algorithm.
        Returns list of cycles (SCCs with more than one member).

        A circular dependency means A needs B, B needs C, C needs A —
        none of them can be installed first.
        """
        disc = {}
        low = {}
        on_stack = set()
        stack = []
        time_counter = [0]
        sccs = []

        def dfs(u):
            disc[u] = low[u] = time_counter[0]
            time_counter[0] += 1
            stack.append(u)
            on_stack.add(u)

            for v in self.adj[u]:
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

        for pkg in sorted(self.packages):
            if pkg not in disc:
                dfs(pkg)

        return sccs

    def find_critical_packages(self):
        """
        Find articulation points in the dependency graph — packages that, if
        removed, would disconnect parts of the dependency tree.

        We treat the graph as undirected for this analysis because a "critical
        package" is one whose removal breaks connectivity in either direction.

        Returns: list of critical package names.
        """
        # Build undirected version
        undirected = defaultdict(set)
        for pkg in self.packages:
            for dep in self.adj[pkg]:
                undirected[pkg].add(dep)
                undirected[dep].add(pkg)

        disc = {}
        low = {}
        parent = {}
        ap_set = set()
        time_counter = [0]

        def dfs(u):
            disc[u] = low[u] = time_counter[0]
            time_counter[0] += 1
            children = 0

            for v in undirected[u]:
                if v not in disc:
                    children += 1
                    parent[v] = u
                    dfs(v)
                    low[u] = min(low[u], low[v])

                    # u is an articulation point if:
                    # 1. u is root of DFS tree and has 2+ children
                    if parent.get(u) is None and children > 1:
                        ap_set.add(u)
                    # 2. u is not root and low[v] >= disc[u]
                    if parent.get(u) is not None and low[v] >= disc[u]:
                        ap_set.add(u)

                elif v != parent.get(u):
                    low[u] = min(low[u], disc[v])

        for pkg in sorted(self.packages):
            if pkg not in disc:
                parent[pkg] = None
                dfs(pkg)

        return sorted(ap_set)

    def find_install_levels(self):
        """
        BFS-based level decomposition for parallel installation.

        Level 0: packages with no dependencies (can install immediately)
        Level 1: packages whose dependencies are all in level 0
        Level k: packages whose dependencies are all in levels < k

        Returns: dict mapping level number -> list of packages at that level.
                 Returns None if cycles prevent full resolution.
        """
        in_deg = {pkg: len(self.adj[pkg]) for pkg in self.packages}
        queue = deque()
        levels = {}

        # Level 0: no dependencies
        for pkg in sorted(self.packages):
            if in_deg[pkg] == 0:
                queue.append(pkg)
                levels[pkg] = 0

        result = defaultdict(list)
        while queue:
            pkg = queue.popleft()
            result[levels[pkg]].append(pkg)

            for dependent in sorted(self.rev.get(pkg, [])):
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    levels[dependent] = levels[pkg] + 1
                    queue.append(dependent)

        if len(levels) != len(self.packages):
            return None  # cycles prevent full resolution

        return dict(result)

    def find_minimal_install(self, target):
        """
        Find the minimal set of packages needed to install `target`.
        This is all packages reachable from `target` in the dependency graph
        (following edges from target to its dependencies, recursively).

        Returns: list of packages in install order (topological).
        """
        if target not in self.packages:
            return []

        # BFS/DFS from target following dependency edges
        needed = set()
        queue = deque([target])
        needed.add(target)

        while queue:
            pkg = queue.popleft()
            for dep in self.adj[pkg]:
                if dep not in needed:
                    needed.add(dep)
                    queue.append(dep)

        # Topological sort only the needed subset
        in_deg = {pkg: 0 for pkg in needed}
        sub_rev = defaultdict(list)
        for pkg in needed:
            for dep in self.adj[pkg]:
                if dep in needed:
                    in_deg[pkg] += 1
                    sub_rev[dep].append(pkg)

        queue = deque()
        for pkg in sorted(needed):
            if in_deg[pkg] == 0:
                queue.append(pkg)

        order = []
        while queue:
            pkg = queue.popleft()
            order.append(pkg)
            for dependent in sorted(sub_rev.get(pkg, [])):
                in_deg[dependent] -= 1
                if in_deg[dependent] == 0:
                    queue.append(dependent)

        return order


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

def demo_build_graph():
    """Build a realistic package dependency graph (like a Python web project)."""
    print("=" * 65)
    print("DEPENDENCY RESOLVER CAPSTONE")
    print("=" * 65)

    g = DependencyGraph()

    # Base packages (no dependencies)
    g.add_package("zlib", "1.2.11", [])
    g.add_package("openssl", "3.0.7", ["zlib"])
    g.add_package("sqlite", "3.40.0", [])

    # Core Python-like packages
    g.add_package("markupsafe", "2.1.1", [])
    g.add_package("charset-normalizer", "3.0.0", [])
    g.add_package("idna", "3.4", [])
    g.add_package("certifi", "2022.12.7", [])
    g.add_package("urllib3", "1.26.14", ["openssl"])
    g.add_package("requests", "2.28.2", ["urllib3", "charset-normalizer", "idna", "certifi"])
    g.add_package("jinja2", "3.1.2", ["markupsafe"])
    g.add_package("werkzeug", "2.2.3", ["markupsafe"])
    g.add_package("itsdangerous", "2.1.2", [])
    g.add_package("click", "8.1.3", [])
    g.add_package("flask", "2.2.3", ["werkzeug", "jinja2", "itsdangerous", "click"])
    g.add_package("sqlalchemy", "2.0.4", ["sqlite"])

    return g


def demo_resolve(g):
    print("\n" + "-" * 65)
    print("1. RESOLVE INSTALL ORDER (Topological Sort)")
    print("-" * 65)

    order, valid = g.resolve()
    if valid:
        print(f"\nValid install order ({len(order)} packages):")
        for i, pkg in enumerate(order):
            deps = g.adj[pkg]
            dep_str = f" (needs: {', '.join(deps)})" if deps else " (no deps)"
            print(f"  {i + 1:2d}. {pkg} v{g.versions.get(pkg, '?')}{dep_str}")
    else:
        print("\nERROR: Cannot resolve — circular dependencies detected!")
        print(f"  Only {len(order)} of {len(g.packages)} packages could be ordered.")


def demo_cycles(g):
    print("\n" + "-" * 65)
    print("2. DETECT CIRCULAR DEPENDENCIES (SCC)")
    print("-" * 65)

    cycles = g.detect_cycles()
    if not cycles:
        print("\n  No circular dependencies found. Graph is a DAG.")
    else:
        print(f"\n  Found {len(cycles)} circular dependency group(s):")
        for i, cycle in enumerate(cycles):
            print(f"    Cycle {i + 1}: {' <-> '.join(cycle)}")

    # Now add a cycle to demonstrate detection
    print("\n  Adding circular dependency: flask -> app -> flask-ext -> flask")
    g.add_package("flask-ext", "1.0.0", ["flask"])
    g.add_package("app", "1.0.0", ["flask-ext"])
    # Create cycle: flask depends on app? No — let's create a separate cycle
    # to keep the main graph valid for other demos
    g2 = DependencyGraph()
    g2.add_package("A", "1.0", ["B"])
    g2.add_package("B", "1.0", ["C"])
    g2.add_package("C", "1.0", ["A"])
    g2.add_package("D", "1.0", ["E"])
    g2.add_package("E", "1.0", ["D"])

    cycles2 = g2.detect_cycles()
    print(f"\n  Separate cyclic graph — found {len(cycles2)} cycle group(s):")
    for i, cycle in enumerate(cycles2):
        print(f"    Cycle {i + 1}: {' -> '.join(cycle)} -> {cycle[0]}")

    # Remove the added packages to keep g clean
    # (we'll just rebuild for subsequent demos)


def demo_critical(g):
    print("\n" + "-" * 65)
    print("3. FIND CRITICAL PACKAGES (Articulation Points)")
    print("-" * 65)

    critical = g.find_critical_packages()
    if critical:
        print(f"\n  Critical packages ({len(critical)}):")
        for pkg in critical:
            # Count how many packages depend on this one (directly or indirectly)
            dependents = set()
            queue = deque([pkg])
            while queue:
                p = queue.popleft()
                for dep in g.rev.get(p, []):
                    if dep not in dependents:
                        dependents.add(dep)
                        queue.append(dep)
            print(f"    {pkg}: {len(dependents)} package(s) depend on it "
                  f"(directly/indirectly)")
    else:
        print("\n  No critical packages found (graph is resilient).")


def demo_parallel(g):
    print("\n" + "-" * 65)
    print("4. PARALLEL INSTALL SCHEDULE (BFS Levels)")
    print("-" * 65)

    levels = g.find_install_levels()
    if levels is None:
        print("\n  Cannot compute parallel schedule — cycles present!")
        return

    print(f"\n  Minimum sequential rounds: {len(levels)}")
    for level in sorted(levels.keys()):
        pkgs = levels[level]
        print(f"    Round {level}: [{', '.join(pkgs)}]")
        print(f"      ({len(pkgs)} packages in parallel)")


def demo_minimal(g):
    print("\n" + "-" * 65)
    print("5. MINIMAL INSTALL FOR A TARGET")
    print("-" * 65)

    target = "flask"
    minimal = g.find_minimal_install(target)
    all_pkgs = len(g.packages)
    print(f"\n  To install '{target}', you need {len(minimal)} of {all_pkgs} packages:")
    for i, pkg in enumerate(minimal):
        print(f"    {i + 1}. {pkg} v{g.versions.get(pkg, '?')}")

    target2 = "requests"
    minimal2 = g.find_minimal_install(target2)
    print(f"\n  To install '{target2}', you need {len(minimal2)} of {all_pkgs} packages:")
    for i, pkg in enumerate(minimal2):
        print(f"    {i + 1}. {pkg} v{g.versions.get(pkg, '?')}")


def demo_full():
    g = demo_build_graph()
    demo_resolve(g)
    demo_cycles(g)

    # Rebuild clean graph for remaining demos (demo_cycles adds packages)
    g = demo_build_graph()
    demo_critical(g)
    demo_parallel(g)
    demo_minimal(g)

    print("\n" + "=" * 65)
    print("CAPSTONE COMPLETE — All Phase 6 graph algorithms applied!")
    print("=" * 65)


if __name__ == "__main__":
    demo_full()
