# Day 87: Strongly Connected Components

## Why SCC Matters

A Strongly Connected Component is a maximal set of vertices where every vertex
can reach every other vertex. SCCs reveal the **deep structure** of directed graphs:

- **Web analysis**: each SCC is a cluster of mutually-linked pages
- **Compiler optimization**: SCCs in the call graph = recursive function groups
- **Social networks**: mutual follow clusters (everyone follows everyone)
- **2-SAT solving**: SCC-based algorithm decides boolean satisfiability in O(V+E)
- **Circuit analysis**: feedback loops in digital circuits

### The Condensation

Collapse each SCC to a single vertex → the resulting graph is always a **DAG**.
This "condensation" is the skeleton of the original graph's structure. You can
then topological-sort the condensation to process components in dependency order.

## Two Classic Algorithms

### 1. Kosaraju's Algorithm (Two-Pass DFS)

**Idea**: DFS twice — once to get finish order, once on the transposed graph.

```
Kosaraju(G):
    1. Run DFS on G, recording finish times (push to stack on finish)
    2. Transpose G (reverse all edges)
    3. Pop vertices from stack, run DFS on G^T
       Each DFS tree in step 3 is one SCC
```

**Why it works**: In the first DFS, vertices in "source" SCCs finish last.
The transposed graph reverses reachability. Processing in reverse finish order
ensures each DFS in step 3 can't escape its SCC.

**Time**: O(V + E) — two DFS passes + one transpose.

### 2. Tarjan's Algorithm (Single-Pass DFS)

**Idea**: During a single DFS, track how far back each vertex can reach via
back edges. When a vertex's "low-link" equals its discovery time, it's the
root of an SCC.

```
Tarjan(G):
    for each unvisited vertex v:
        DFS(v)

DFS(u):
    disc[u] = low[u] = time++
    push u onto stack

    for each neighbor v of u:
        if v not visited:
            DFS(v)
            low[u] = min(low[u], low[v])
        elif v is on stack:
            low[u] = min(low[u], disc[v])

    if low[u] == disc[u]:     # u is SCC root
        pop stack until u → that's one SCC
```

**Key concepts**:
- `disc[u]`: when vertex u was discovered
- `low[u]`: earliest discovery time reachable from u's subtree via back edges
- When `low[u] == disc[u]`: u is the "root" of its SCC (can't reach further back)

**Time**: O(V + E) — single DFS pass.

## Comparison

| Property | Kosaraju's | Tarjan's |
|----------|-----------|----------|
| DFS passes | 2 | 1 |
| Needs transpose | Yes | No |
| Extra space | Stack + transpose graph | Stack + disc/low arrays |
| Conceptual simplicity | Simpler (two standard DFS) | Harder (low-link tracking) |
| Practical speed | Slightly slower (two passes) | Slightly faster (one pass) |
| Produces topo order | Yes (natural from step 3) | Yes (reverse SCC discovery) |

## The Condensation DAG

After finding SCCs:
1. Replace each SCC with a single "super-vertex"
2. Add edges between super-vertices (preserving inter-SCC edges, removing duplicates)
3. Result is a DAG — can topological sort it

**Use case**: Process components in dependency order (e.g., compile recursive
function groups before their callers).

## 2-SAT Connection

A boolean formula in 2-SAT form (each clause has exactly 2 literals) is satisfiable
**iff** no variable and its negation are in the same SCC of the implication graph.

This gives an O(V + E) SAT solver for 2-SAT — remarkable since 3-SAT is NP-complete.

## Real-World Usage

| System | Application | Why SCC |
|--------|------------|---------|
| **Google PageRank** | Web graph structure analysis | SCC = mutually linked page clusters |
| **GCC/LLVM** | Recursive function optimization | SCC in call graph = mutual recursion |
| **SAT solvers** | 2-SAT decision | SCC-based linear-time algorithm |
| **Model checking** | CTL/LTL formula evaluation | SCC structure of state space |
| **Package managers** | Circular dependency detection | SCC = circular dep group |
| **Network routing** | Identifying robust clusters | SCC = fully connected subnetwork |

## Checkpoint Questions

1. Why does Kosaraju's algorithm process vertices in reverse finish order?
   What would happen if you used discovery order instead?
2. In Tarjan's algorithm, why do we use `disc[v]` (not `low[v]`) when v is
   on the stack? What breaks if we use `low[v]`?
3. A package manager finds an SCC of size 5 in the dependency graph.
   What does this mean for the user? How should the system report it?
4. Can an SCC have exactly one vertex? Under what conditions?
5. If you add one edge to a DAG, at most how many SCCs can be created?
6. The web has ~1.7 billion pages. Describe how SCC computation helps
   search engines understand link structure at this scale.
