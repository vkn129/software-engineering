"""
Day 86 Practice: Union-Find (Disjoint Set Union)

6 exercises covering path compression, union by rank, and applications.
Implement the TODO functions, then run: python practice.py
"""


# ===================================================================
# Provided: Union-Find for exercises
# ===================================================================

class UnionFind:
    """Optimized Union-Find with path compression + union by rank."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # number of components

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)


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
# Exercise 1: Implement Basic Union-Find
# ===================================================================
# Build Union-Find from scratch with path compression and union by rank.

def basic_union_find(n, operations):
    """
    n: number of elements (0 to n-1)
    operations: list of ('union', a, b) or ('find', a)
    Returns: list of results for 'find' operations (root of element)
    """
    # TODO: implement
    pass


def _sol_basic_union_find(n, operations):
    parent = list(range(n))
    rank = [0] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    results = []
    for op in operations:
        if op[0] == 'union':
            union(op[1], op[2])
        elif op[0] == 'find':
            results.append(find(op[1]))
    return results


# ===================================================================
# Exercise 2: Count Connected Components
# ===================================================================
# After a series of union operations, count distinct components.

def count_components(n, edges):
    """
    n: number of vertices (0 to n-1)
    edges: list of (u, v) pairs to union
    Returns: number of connected components after all unions
    """
    # TODO: implement
    pass


def _sol_count_components(n, edges):
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count


# ===================================================================
# Exercise 3: Detect Redundant Connection
# ===================================================================
# Find the first edge that creates a cycle (both endpoints already connected).

def find_redundant(n, edges):
    """
    n: number of vertices (0 to n-1)
    edges: list of (u, v) added in order
    Returns: first edge (u, v) that creates a cycle, or None
    """
    # TODO: implement
    pass


def _sol_find_redundant(n, edges):
    uf = UnionFind(n)
    for u, v in edges:
        if uf.connected(u, v):
            return (u, v)
        uf.union(u, v)
    return None


# ===================================================================
# Exercise 4: Largest Component Size
# ===================================================================
# Track component sizes and return the largest after all unions.

def largest_component(n, edges):
    """
    n: number of vertices (0 to n-1)
    edges: list of (u, v) pairs
    Returns: size of the largest connected component
    """
    # TODO: implement
    pass


def _sol_largest_component(n, edges):
    parent = list(range(n))
    rank = [0] * n
    size = [1] * n

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    for u, v in edges:
        union(u, v)
    return max(size[find(i)] for i in range(n))


# ===================================================================
# Exercise 5: Grid Percolation
# ===================================================================
# Check if a grid percolates (top row connects to bottom row).
# Use virtual nodes: virtual_top connects to all top-row cells,
# virtual_bottom connects to all bottom-row cells.

def percolates(grid):
    """
    grid: 2D list where 1 = open, 0 = blocked
    Returns: True if there's a path from any top-row open cell
             to any bottom-row open cell through adjacent open cells
    """
    # TODO: implement using Union-Find with virtual nodes
    pass


def _sol_percolates(grid):
    if not grid or not grid[0]:
        return False
    rows, cols = len(grid), len(grid[0])
    n = rows * cols
    virtual_top = n
    virtual_bottom = n + 1
    uf = UnionFind(n + 2)

    def idx(r, c):
        return r * cols + c

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0:
                continue
            if r == 0:
                uf.union(idx(r, c), virtual_top)
            if r == rows - 1:
                uf.union(idx(r, c), virtual_bottom)
            # Connect to open neighbors below and right
            for dr, dc in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                    uf.union(idx(r, c), idx(nr, nc))

    return uf.connected(virtual_top, virtual_bottom)


# ===================================================================
# Exercise 6: Accounts Merge
# ===================================================================
# Group accounts that share common emails.
# Each account is (name, [emails...]). If two accounts share an email,
# they belong to the same person — merge all their emails.

def accounts_merge(accounts):
    """
    accounts: list of (name, [email1, email2, ...])
    Returns: list of (name, sorted_unique_emails) for each merged group,
             sorted by first email in each group
    """
    # TODO: implement
    pass


def _sol_accounts_merge(accounts):
    email_to_id = {}
    email_to_name = {}
    next_id = 0

    # Assign an ID to each unique email
    for name, emails in accounts:
        for email in emails:
            if email not in email_to_id:
                email_to_id[email] = next_id
                next_id += 1
            email_to_name[email] = name

    uf = UnionFind(next_id)

    # Union all emails within the same account
    for name, emails in accounts:
        for i in range(1, len(emails)):
            uf.union(email_to_id[emails[0]], email_to_id[emails[i]])

    # Group emails by root
    from collections import defaultdict
    groups = defaultdict(set)
    for email, eid in email_to_id.items():
        root = uf.find(eid)
        groups[root].add(email)

    # Build result
    result = []
    for root, emails in groups.items():
        sorted_emails = sorted(emails)
        name = email_to_name[sorted_emails[0]]
        result.append((name, sorted_emails))

    return sorted(result, key=lambda x: x[1][0])


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

    # --- Exercise 1 ---
    print("Exercise 1: Basic Union-Find")
    ops = [('union', 0, 1), ('union', 2, 3), ('find', 0), ('find', 1),
           ('find', 2), ('union', 1, 3), ('find', 0), ('find', 3)]
    result = try_or_sol("basic_union_find", 4, ops)
    # After union(0,1) and union(2,3): find(0)==find(1), find(2)==find(3)
    check("same root after union", result[0] == result[1], True)
    check("different groups before merge", result[0] != result[2], True)
    # After union(1,3): all connected. Both operands must be POST-merge roots —
    # union-by-rank may relabel the root, so a pre-merge root (result[2]) is not
    # comparable to a post-merge one.
    check("all connected after merge", result[3] == result[4], True)

    # --- Exercise 2 ---
    print("\nExercise 2: Count Components")
    check("4 nodes, 2 edges", try_or_sol("count_components", 4, [(0, 1), (2, 3)]), 2)
    check("5 nodes, no edges", try_or_sol("count_components", 5, []), 5)
    check("3 nodes, all connected", try_or_sol("count_components", 3, [(0, 1), (1, 2)]), 1)

    # --- Exercise 3 ---
    print("\nExercise 3: Redundant Connection")
    check("cycle at (2,0)", try_or_sol("find_redundant", 3, [(0, 1), (1, 2), (2, 0)]), (2, 0))
    check("no cycle", try_or_sol("find_redundant", 4, [(0, 1), (2, 3)]), None)
    check("cycle at (1,3)", try_or_sol("find_redundant", 4, [(0, 1), (1, 2), (0, 2), (1, 3)]), (0, 2))

    # --- Exercise 4 ---
    print("\nExercise 4: Largest Component")
    check("two components", try_or_sol("largest_component", 5, [(0, 1), (1, 2), (3, 4)]), 3)
    check("all isolated", try_or_sol("largest_component", 4, []), 1)
    check("all connected", try_or_sol("largest_component", 3, [(0, 1), (1, 2)]), 3)

    # --- Exercise 5 ---
    print("\nExercise 5: Grid Percolation")
    grid1 = [
        [1, 0, 1],
        [1, 1, 0],
        [0, 1, 0],
    ]
    check("percolates", try_or_sol("percolates", grid1), True)

    grid2 = [
        [1, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
    ]
    check("blocked", try_or_sol("percolates", grid2), False)

    grid3 = [
        [1, 1],
        [1, 1],
    ]
    check("fully open", try_or_sol("percolates", grid3), True)

    # --- Exercise 6 ---
    print("\nExercise 6: Accounts Merge")
    accts = [
        ("Alice", ["a@mail.com", "b@mail.com"]),
        ("Alice", ["b@mail.com", "c@mail.com"]),
        ("Bob", ["d@mail.com"]),
    ]
    result = try_or_sol("accounts_merge", accts)
    check("merged Alice", result[0], ("Alice", ["a@mail.com", "b@mail.com", "c@mail.com"]))
    check("Bob separate", result[1], ("Bob", ["d@mail.com"]))

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed out of {passed+failed}")
    if failed == 0:
        print("All tests passed!")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
