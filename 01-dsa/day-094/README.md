# Day 94: Hierholzer's Algorithm — Euler Paths & Circuits

## The Question Euler Asked in 1736

Can you walk across every bridge in Konigsberg **exactly once**? Euler proved
no (and birthed graph theory). The general question:

> Given a graph, can you traverse **every edge exactly once**?

- **Euler circuit**: starts and ends at same vertex; traverses every edge once.
- **Euler path**: starts at one vertex, ends at another; every edge once.

Hierholzer's algorithm (1873) builds such a walk in **O(E)** — linear in
edges, optimal.

## The Existence Conditions

For an **undirected graph** (with all edges in one connected component):

| Condition | Result |
|-----------|--------|
| All vertices have **even** degree | Euler circuit exists |
| Exactly 2 vertices have odd degree | Euler path exists (between those two) |
| Any other number of odd-degree vertices | Neither exists |

For a **directed graph**:

| Condition | Result |
|-----------|--------|
| Every vertex has in-degree == out-degree, graph strongly connected | Euler circuit |
| Exactly one vertex has out-degree - in-degree = +1 (start), one has -1 (end), rest equal, and underlying weakly connected | Euler path |

**Why parity?** Every time you enter a vertex, you must leave it (except at
endpoints). Each entry/exit consumes 2 edges of that vertex. So all
non-endpoints need even degree.

## Hierholzer's Algorithm

The naive idea: walk randomly, get stuck, splice. Hierholzer formalizes this.

```
algorithm Hierholzer(graph, start):
    stack = [start]
    circuit = []
    while stack:
        v = stack.top()
        if v has an unused outgoing edge (v, u):
            remove edge (v, u)  # mark used
            stack.push(u)
        else:
            circuit.append(stack.pop())
    return reverse(circuit)
```

Why it works: when we hit a dead end at `v`, we must have returned to the
**same vertex** we started this sub-walk from (by parity). We pop `v` into
the circuit, then resume from the previous vertex on the stack — which may
still have unused edges to explore. The final circuit is built by reversing
the pop order.

## Complexity Table

| Operation | Time | Space |
|-----------|------|-------|
| Existence check | O(V + E) | O(V) |
| Hierholzer's main loop | O(E) | O(V + E) |
| **Total** | **O(V + E)** | O(V + E) |

Compared to DFS (which is also O(V+E)), Hierholzer's is the **same order**
but solves a strictly harder problem: covering edges, not vertices.

## Common Pitfalls

1. **Multi-edges**: must be tracked individually. Use a list of edges per
   vertex with an index, or a counter.
2. **Self-loops**: each self-loop adds 2 to the vertex's degree (entering
   and leaving). Handle in the existence check.
3. **Connectivity gotcha**: isolated vertices (degree 0) don't count. Only
   the subgraph of edges must be connected.
4. **Directed vs undirected logic differs** — easy to mix up. We provide
   both variants.
5. **Recursion vs iteration**: pure recursive Hierholzer blows the stack
   on long paths. Iterative version with explicit stack is the canonical
   form.
6. **Edge removal cost**: `list.remove()` is O(n). Use a pointer/index into
   the adjacency list instead.

## Concrete Applications

### DNA Sequencing (the de Bruijn graph)

To reconstruct a genome from millions of short reads:
1. Build a de Bruijn graph: nodes = (k-1)-mers, edges = k-mers.
2. An Euler path through this graph reconstructs the original sequence.
3. Hierholzer's algorithm = the reconstruction algorithm.

This is why genome assemblers (SPAdes, Velvet) all use Eulerian path
algorithms.

### Postman / Drone Delivery Routing

The **Chinese Postman Problem**: traverse every edge of a road network at
minimum cost. If Eulerian, the answer is just the sum of edge weights, and
Hierholzer's gives the route. If not Eulerian, you find the cheapest way to
double some edges to make it Eulerian (matching on odd-degree vertices).

### Circuit Board Routing

Drilling a sequence of holes minimizing pen-up moves can be modeled as
finding an Eulerian path on a route graph.

## Real-World Usage

| System | Application | Why Euler Path |
|--------|------------|----------------|
| **Genome assemblers (SPAdes)** | DNA reconstruction from reads | de Bruijn graph traversal |
| **Snowplow routing** | Plow every street once | Euler circuit minimizes deadhead |
| **PCB drilling** | Drill all holes optimally | Edge-visiting tour |
| **Network testing** | Walk every link to test latency | Cover all edges exactly once |
| **Trail design** | Hiking trail covering all paths | Euler circuit |
| **Bridge traversal** | Konigsberg (the original) | Historical foundation |

## Connection to Other Days

- **Day 79-80** (BFS/DFS) — Hierholzer is a structured DFS variant.
- **Day 81** (topological sort) — both consume the graph linearly; topo
  sort handles DAGs, Hierholzer handles Eulerian graphs.
- **Day 95** (cycle detection, coming) — Euler circuit is a cycle covering
  all edges; cycle detection is the simpler "does any cycle exist?"
- **Day 88** (bridges) — bridges are non-removable in Euler paths
  (Fleury's algorithm uses this; Hierholzer doesn't need to).
- **Day 86** (Union-Find) — used to verify edge connectivity.
- **Day 91** (dependency resolver) — different traversal pattern; topo sort
  there, Euler here.

## Checkpoint Questions

1. Why does an Euler **circuit** require every vertex to have even degree?
   Give the 1-sentence parity argument.
2. In Hierholzer's, why do we append to `circuit` only when we pop, and then
   reverse at the end?
3. Show an example where a "greedy random walk" gets stuck before consuming
   all edges, but Hierholzer's still finds the circuit.
4. For a directed graph, what's the difference between "weakly connected"
   and "strongly connected"? Which does the Euler-circuit condition require?
5. Suppose your graph has 4 odd-degree vertices. How many edges (at minimum)
   do you need to add to make an Euler circuit exist? Hint: think in pairs.
6. In genome assembly with reads of length k, why is an **Euler path** the
   right reconstruction (rather than Hamiltonian path)? What changed?
