# Day 95: Cycle Detection — Directed & Undirected

## Why Cycle Detection Matters

"Is there a cycle?" sounds trivial, but it underpins the **safety** of huge
production systems:

- **Build systems** (Bazel, Make): cyclic `import` graphs = stuck builds.
- **Database deadlock detectors** (PostgreSQL, MySQL InnoDB): a wait-for
  cycle means transactions can never make progress.
- **Resource allocation** (Linux kernel): kthread deadlock detection.
- **Spreadsheet engines** (Excel): circular references = `#CIRC!`.
- **Compilers**: detect mutually recursive module imports.
- **Type checkers**: cyclic type aliases like `type T = T`.

The interesting twist: **directed** and **undirected** cycle detection
require **different** algorithms. The undirected version is easier; the
directed version needs a clever 3-coloring.

## Undirected Cycle Detection

### Approach 1: DFS with parent tracking

During DFS from `u`, if we see a neighbor `v` that's visited **and not the
parent of u**, we found a cycle.

```
dfs(u, parent):
    visited[u] = True
    for v in adj[u]:
        if not visited[v]:
            if dfs(v, u): return True
        elif v != parent:
            return True  # back-edge to non-parent = cycle
    return False
```

Catch: with **multi-edges** between u and parent, parent-checking alone
isn't enough — must track by edge id (same as Day 88's bridges).

### Approach 2: Union-Find (Day 86)

```
for (u, v) in edges:
    if find(u) == find(v): return True   # both already in same component
    union(u, v)
return False
```

Cleaner code; same O(E * alpha(V)) time. Preferred when edges arrive
**online** (streaming).

## Directed Cycle Detection: 3-Coloring DFS

The undirected trick fails on directed graphs. Consider `a -> b, c -> b`:
visiting `b` from both is **not** a cycle. We need the notion of an
**active recursion frame**.

### The Three Colors

| Color | State | Meaning |
|-------|-------|---------|
| **WHITE** | Unvisited | Not yet entered DFS |
| **GRAY** | In current DFS path | Currently on the recursion stack |
| **BLACK** | Done | DFS for this vertex has finished |

**A directed graph has a cycle iff DFS encounters a GRAY vertex** — meaning
we found a back-edge from a descendant to an ancestor.

```
color = [WHITE] * n

def dfs(u):
    color[u] = GRAY
    for v in adj[u]:
        if color[v] == GRAY:    # back-edge -> cycle
            return True
        if color[v] == WHITE and dfs(v):
            return True
    color[u] = BLACK
    return False
```

Why this works: a directed back-edge — and only a back-edge — connects a
descendant to a still-active ancestor. Edges to BLACK vertices go to a
**finished** subtree, which can't be on the current path.

## Edge Classification (For Free)

The DFS gives us four edge types in directed graphs:

| Edge | Target color when seen | Meaning |
|------|------------------------|---------|
| Tree edge | WHITE | First DFS edge |
| Back edge | GRAY | Closes a cycle |
| Forward edge | BLACK (descendant) | Shortcut down already-visited subtree |
| Cross edge | BLACK (non-descendant) | Goes to a sibling subtree |

For cycle detection we only need back edges. For Day 87's SCC, this same
DFS structure is the foundation.

## Complexity Table

| Variant | Time | Space |
|---------|------|-------|
| Undirected DFS | O(V + E) | O(V) |
| Undirected Union-Find | O(E * alpha(V)) | O(V) |
| Directed 3-coloring DFS | O(V + E) | O(V) |
| Directed via topo sort | O(V + E) | O(V) (if Kahn fails -> cycle) |

All linear time. Choose based on what else you need:
- Need only a yes/no? Union-Find is fastest in practice.
- Need to **report** the cycle? 3-coloring DFS keeps a parent map.
- Already doing topo sort? Reuse that result.

## Failure Modes

1. **Recursion depth**: 10^4+ vertices can blow Python's stack. Use
   `sys.setrecursionlimit` or convert to iterative DFS.
2. **Self-loops** are cycles in both directed and undirected graphs — make
   sure your code reports them.
3. **Multi-edges in undirected**: `v != parent` check fails on parallel
   edges. Use edge ids.
4. **Disconnected graphs**: must restart DFS from every unvisited vertex.
5. **Detecting all cycles vs any**: detecting *any* is linear; detecting
   *all* is exponential (in general).
6. **Online edge insertion**: don't recompute from scratch — use Union-Find
   (undirected) or incremental algorithms (directed is much harder).

## Deadlock Detection in Practice

In PostgreSQL, a transaction T1 waiting on a lock held by T2 builds an edge
`T1 -> T2` in the **wait-for graph**. The deadlock detector runs every
`deadlock_timeout` (1 second default) and looks for a cycle. If found, it
**aborts the youngest victim** to break the deadlock.

Linux's kthread runqueue uses a similar wait-graph for I/O dependency
deadlocks. Both rely on directed 3-coloring DFS or equivalent.

## Real-World Usage

| System | Application | Why Cycle Detection |
|--------|------------|---------------------|
| **PostgreSQL** | Transaction deadlock detector | Wait-for cycle = deadlock |
| **MySQL InnoDB** | Same | "Deadlock found when trying to get lock" |
| **Linux kernel** | Lockdep | Lock ordering cycles |
| **Bazel/Make** | Build dependency check | Circular targets fail build |
| **Excel** | Formula re-eval | Circular references abort calc |
| **Compilers** | Mutual recursion / type alias loops | Detect & error out |
| **GraphQL schemas** | Type reference cycles | Resolve via lazy types |

## Connection to Other Days

- **Day 80** (DFS) — direct ancestor; coloring is a DFS extension.
- **Day 81** (topological sort) — Kahn's algorithm naturally detects cycles
  (any vertex not output = part of a cycle).
- **Day 86** (Union-Find) — alternative for undirected case.
- **Day 87** (SCC) — generalizes "find cycle" to "find all cycle clusters."
- **Day 88** (bridges) — uses similar low-link DFS structure.
- **Day 91** (dependency resolver) — uses topo sort, which fails on cycles
  detected here.
- **Day 97** (2-SAT, coming) — uses SCC = generalized cycle detection.

## Checkpoint Questions

1. Why doesn't the "visited and not parent" check work for **directed**
   graphs? Give a 3-vertex counter-example.
2. In the 3-color DFS, why is reaching a **BLACK** vertex safe (no cycle),
   but reaching a **GRAY** vertex a cycle?
3. PostgreSQL's deadlock detector waits 1 second before running. Why not
   detect on every lock acquisition? What's the latency vs CPU trade-off?
4. For undirected graphs, which is faster on a dense graph: DFS-with-parent
   or Union-Find? Why?
5. Suppose you find a cycle and need to **report the vertices** on it. How
   do you modify 3-color DFS to do so in O(cycle length) extra work?
6. Linux's lockdep tracks lock-order cycles across **all** kernel paths,
   not just runtime ones. Why is this more useful than runtime detection?
