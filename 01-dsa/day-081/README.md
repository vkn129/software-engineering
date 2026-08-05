# Day 81: Topological Sort

## Why Topological Sort Matters

Topological sort answers: **"In what order should I do these tasks so that
every prerequisite is completed first?"** This comes up everywhere:

- **Build systems** (Make, Bazel, Gradle): compile dependencies before dependents
- **Package managers** (npm, pip): install packages in dependency order
- **Course scheduling**: take prerequisites before advanced courses
- **Spreadsheet evaluation**: compute cells that formulas depend on first
- **CI/CD pipelines**: run tests before deploy, build before test

A topological sort only exists for **DAGs** (Directed Acyclic Graphs). If there's
a cycle, no valid ordering exists — and detecting this is equally important.

## The Core Idea

Given a directed graph, find a linear ordering of vertices such that for every
edge u → v, vertex u appears before v in the ordering.

```
Example DAG:        A valid topological order:
  0 → 1 → 3        [0, 2, 1, 3]  ← 0 before 1, 1 before 3, 2 before 3
  0 → 2 → 3        [0, 1, 2, 3]  ← also valid!
```

Multiple valid orderings usually exist. A graph with V vertices may have
anywhere from 1 to V! valid topological orderings.

## Two Algorithms

### 1. Kahn's Algorithm (BFS-based)

**Idea**: Repeatedly remove vertices with no incoming edges (in-degree 0).
If all vertices get removed, we have a valid ordering. If not, there's a cycle.

```
Kahn(G):
    compute in-degree for every vertex
    queue = all vertices with in-degree 0
    order = []

    while queue not empty:
        u = queue.dequeue()
        order.append(u)
        for each neighbor v of u:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.enqueue(v)

    if len(order) != V:
        return "CYCLE DETECTED"
    return order
```

**Why it works**: A vertex with in-degree 0 has no unsatisfied dependencies,
so it's safe to schedule. Removing it may make other vertices dependency-free.

**Cycle detection**: If the queue empties before all vertices are processed,
some vertices still have incoming edges from each other — a cycle.

### 2. DFS-based (Reverse Post-Order)

**Idea**: Run DFS. When a vertex *finishes* (all descendants explored), push it
onto a stack. The stack's order (top to bottom) is a valid topological sort.

```
DFS-Topo(G):
    for each unvisited vertex u:
        DFS(u)
    return stack (reverse post-order)

DFS(u):
    mark u as visiting (GRAY)
    for each neighbor v of u:
        if v is GRAY: CYCLE!
        if v is WHITE: DFS(v)
    mark u as done (BLACK)
    stack.push(u)
```

**Why it works**: When vertex u finishes, all vertices reachable from u are
already on the stack (deeper in). So u will appear before all its dependents.

**Cycle detection**: If DFS finds a back edge (edge to a GRAY vertex), cycle exists.

## Comparison

| Property | Kahn's (BFS) | DFS-based |
|----------|-------------|-----------|
| Time | O(V + E) | O(V + E) |
| Space | O(V) for queue + in-degrees | O(V) for recursion stack |
| Cycle detection | Queue empties early | Back edge found |
| All orderings | Can enumerate with backtracking | Harder to enumerate |
| Lexicographic order | Use min-heap instead of queue | Requires modification |
| Parallelism | Natural: vertices at same "level" can run in parallel | Less natural |

## Lexicographic Topological Sort

Sometimes you want the *smallest* valid ordering (by vertex label). Replace
Kahn's queue with a **min-heap**: always process the smallest available vertex.

```
Lexicographic variant: O((V + E) log V) due to heap operations
```

## Real-World Usage

| System | How It Uses Topo Sort | Why |
|--------|----------------------|-----|
| **Make** | Orders compilation tasks | .o files before linking |
| **npm install** | Resolves dependency tree | Install lodash before express |
| **Webpack** | Module bundling order | Import resolution |
| **Excel** | Cell evaluation order | =A1+B2 needs A1 and B2 first |
| **Database migrations** | Schema change ordering | Create table before add index |
| **Airflow** | DAG task scheduling | ETL pipeline ordering |

## Checkpoint Questions

1. Why can't topological sort work on graphs with cycles? Give an intuitive argument.
2. A build system has 1000 packages. After running Kahn's algorithm, only 950
   were processed. What happened? What should the system report to the user?
3. How would you modify Kahn's algorithm to detect the *smallest* cycle in a graph?
4. If you need the lexicographically smallest topological order, which algorithm
   is easier to modify and why?
5. A spreadsheet has cells A1, B1, C1 where A1=B1+1, B1=C1*2, C1=5. Draw
   the dependency graph and give the evaluation order.
6. What is the maximum number of valid topological orderings for a chain
   0→1→2→...→n? What about a graph with no edges?
