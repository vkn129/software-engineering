# Day 91: Dependency Resolver — Phase 6 Capstone

## What This Is

A working dependency resolver — the algorithmic core of `npm`, `pip`, `cargo`, `apt`, and every other package manager. This is **not** a toy. The same algorithms ship in production tools serving millions of users daily.

It integrates every graph technique from Phase 6:

| Phase 6 Technique | Used For |
|---|---|
| Topological sort (day-81) | Install order — Kahn's algorithm via BFS |
| SCC / Tarjan's (day-87) | Detecting circular dependencies (cycles in the dep graph) |
| Articulation points (day-88) | Finding critical packages whose removal would break the install |
| BFS levels (day-79) | Computing the maximum-parallelism install schedule |
| Reachability / DFS (day-80) | Minimal install set — what packages does target need? |

## The Five Operations

### 1. Resolve install order
Kahn's algorithm on the dependency DAG. Process packages with zero remaining dependencies, decrement their dependents' counters, repeat. If everything finishes, you have a valid linear order. If anything's stuck, there's a cycle.

**Why Kahn vs DFS-based topo sort?** Kahn gives you cycle detection for free — if the output is shorter than the input, you have a cycle. DFS-based works too but the cycle signal is more awkward to extract.

### 2. Detect circular dependencies
Tarjan's SCC algorithm. Any SCC of size ≥ 2 is a circular dependency. The user sees `flask → flask-ext → app → flask` as one group, not five separate cycles.

**Why SCC instead of just "find any cycle"?** A cycle finder returns one cycle. SCC tells you the *complete* group of mutually-dependent packages. Critical for the error message — "these 5 packages depend on each other" beats "there's a cycle somewhere."

### 3. Find critical packages
Tarjan's articulation point algorithm on the **undirected** dependency graph. A critical package is one whose removal disconnects the dependency network — typically a low-level library that everything depends on (e.g., `openssl`, `zlib`, `glibc`).

**Why undirected?** Direction matters for install order, but criticality is symmetric — `openssl` is critical whether you're walking from app→openssl or in reverse.

### 4. Parallel install schedule
BFS level decomposition. Round 0 = packages with no dependencies. Round N = packages whose dependencies are all in rounds < N. This is the *minimum* number of sequential rounds — within each round, all packages can install in parallel.

**Why does this matter?** A naive sequential install of 100 packages takes 100 × install_time. With levels, you parallelize each round → wall clock = max_depth × install_time. For most dep graphs, max_depth is logarithmic in package count.

### 5. Minimal install for target
DFS from the target following dependency edges. Returns the transitive closure — everything the target needs, transitively, in install order.

**Why?** Real package managers don't install the entire ecosystem when you ask for `flask`. They compute the dependency closure and install only that.

## What This Demonstrates

**Why graph theory matters in production:** Every operation above is a graph algorithm. There's no "package management" magic — it's all topological sort, SCC, articulation points, BFS, and reachability. The hard part is *recognizing which problem you have* and picking the right algorithm.

**The cost of getting it wrong:**
- Skip cycle detection → infinite recursion at install time
- Sequential install instead of level-parallel → 10× slower
- No articulation analysis → no way to warn users about fragile dep trees
- Full reachability instead of minimal closure → install 50,000 packages to get one

## Real-World Comparisons

| System | Cycle handling | Parallelism | Critical-pkg analysis |
|---|---|---|---|
| **npm** | Errors on cycle (>v7) | Yes, level-based | No (community tools) |
| **pip** | Tolerated until 20.3, then errors | No (sequential) | No |
| **cargo** | Errors on cycle | Yes, with rayon | Yes (cargo-tree) |
| **apt** | Errors via dpkg | Limited | Yes (debfoster) |
| **nix** | Cycles forbidden by design | Yes, derivation graph | Yes (nix-tree) |

## Failure Modes

1. **Diamond dependency hell.** `A` needs `B v1` and `C v2`, but `C v2` needs `B v2`. No single version of `B` satisfies both. This is a *version constraint* problem on top of the dep graph — solved by SAT solvers in real package managers (PubGrub algorithm, used by Dart and Cargo).

2. **Slow on million-package graphs.** Tarjan's is O(V+E), but V+E for the full npm graph is hundreds of millions. Production tools cache the resolution and only re-resolve on lockfile changes.

3. **Articulation point analysis isn't enough.** Real systems care about *transitive critical paths* — "package X is depended on by 10,000 things via 5 layers of indirection." Bridge analysis + dep tree size gives a richer view.

4. **Parallel install isn't always faster.** If the dep graph is mostly a chain (one big linear pipeline), there's no parallelism to extract. Also, disk I/O contention can make parallel installs *slower* than sequential.

## Checkpoint Questions

1. **Why is the install-order DAG's edge direction opposite to the dependency-statement direction?** If `pkg → dep` means "pkg depends on dep", what direction must the edge run for topological sort to give a valid install order?

2. **The capstone uses Kahn's algorithm for topological sort. Could you use DFS-based topo sort instead? What changes in the cycle detection?**

3. **Why does the critical-package analysis convert the directed dep graph to undirected first?** What would happen if you ran articulation points on the directed graph directly?

4. **In the BFS level decomposition, can two packages at the same level have an edge between them?** Prove your answer.

5. **A user asks: "Why does upgrading package X require reinstalling 50 other packages?"** Use the algorithms in this capstone to design an analysis tool that answers this precisely.

6. **The minimal-install operation does DFS from the target. What's the time complexity in terms of the *full* graph size vs the *target's subgraph* size? When does this matter?**

## What Phase 6 Built Toward

Phase 6 isn't about "learning graph algorithms" — it's about being able to *look at a real system* (a package manager, a build tool, a network analyzer, a social graph) and immediately see the algorithmic structure underneath. Dependency resolver is the proof that the abstractions work end-to-end.

Next: **Phase 7 (Sorting & Searching Deep Dive)** revisits seemingly-simple operations and shows how production systems push them to the limits of what's possible.
