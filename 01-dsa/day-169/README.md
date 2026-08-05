# Day 169: Backtracking Patterns

## Why Backtracking Matters

Backtracking is **DFS through a decision tree**, with the right to undo. It
solves problems where brute force is exponential, but most branches can be
pruned early because they violate constraints.

- **N-Queens**: place N queens on N×N board so none attack each other
- **Sudoku**: fill 9×9 grid satisfying row/column/box constraints
- **Permutations / combinations / subsets**: enumerate all valid arrangements
- **Graph coloring**: assign K colors so no adjacent vertices share a color
- **SAT / CSP solvers**: every modern SAT solver is backtracking + learning
- **Cryptarithmetic**: SEND + MORE = MONEY style puzzles
- **Parsers**: PEG / packrat parsers backtrack on alternation failure

Backtracking is the **template** behind every constraint-satisfaction problem.

## The Pattern

```
def backtrack(state):
    if is_complete(state):
        record(state)
        return
    for choice in choices(state):
        if is_valid(state, choice):
            apply(state, choice)
            backtrack(state)
            undo(state, choice)        # the "back" in backtracking
```

Three components:
1. **State** — partial solution so far (board, assignment, path)
2. **Choices** — what can extend the state at this point
3. **Prune** — reject choices that cannot lead to a solution

Without pruning, backtracking is just brute-force exhaustive search.

## N-Queens

Place N queens, no two on same row/column/diagonal.

**Naive**: try all N^N placements = explodes.
**Backtracking**: place one queen per row, prune columns/diagonals already used.

Key insight: an N×N board has only 2N−1 diagonals. Use three sets:
- `cols`        — columns already occupied
- `diag1`       — r + c values used (anti-diagonals)
- `diag2`       — r - c values used (main diagonals)

Each placement is O(1) constraint check.

| N | Solutions | Search time |
|---|-----------|-------------|
| 4 | 2 | instant |
| 8 | 92 | instant |
| 12 | 14,200 | < 1s |
| 15 | 2,279,184 | seconds |

Naive O(N!) becomes manageable because most branches die at the second row.

## Sudoku with Constraint Propagation

Plain backtracking on Sudoku: try 1-9 in each empty cell, recurse.
Works, but slow on hard puzzles.

**Optimization 1: Minimum-Remaining-Values (MRV)**
Always pick the empty cell with the **fewest legal candidates**. Fail-fast
on cells with one or zero candidates.

**Optimization 2: Forward checking / propagation**
After placing a digit, eliminate it from peers' candidate sets. If any peer
drops to zero candidates, backtrack immediately.

**Optimization 3: Naked singles**
If a cell has only one candidate, fill it without recursing. Repeat to
fixpoint before branching.

Combined, these prune branching factor from ~9 to often ~1-2.

## The Generalized Template

```python
def solve(state):
    if state.complete():
        yield state.solution()
        return
    var = state.select_unassigned_variable()    # MRV
    for value in state.domain(var):              # ordered: LCV
        if state.consistent(var, value):
            state.assign(var, value)
            for sol in solve(state):
                yield sol
            state.unassign(var)
```

This is **the CSP algorithm**. AC-3, forward checking, conflict-directed
backjumping all plug into this skeleton.

## Pruning Hierarchy

From cheapest/weakest to most expensive/aggressive:

1. **Constraint check** — reject if value breaks an explicit rule (O(1))
2. **Forward checking** — eliminate from neighbors' domains (O(d) per peer)
3. **Arc consistency (AC-3)** — propagate domain reductions to fixpoint
4. **Path consistency** — propagate over triples
5. **Conflict-directed backjumping** — jump past irrelevant decisions

Production SAT solvers add **clause learning** (CDCL): every dead end teaches
the solver a new constraint, so the same trap is never re-entered.

## Connection to Earlier Days

- **Day 18 DFS**: backtracking is DFS over the decision tree
- **Day 86 Union-Find**: graph coloring uses UF to merge equivalence classes
- **Day 52 Segment trees**: not directly used, but interval CSPs sometimes
  use range trees to speed up consistency checks

## Failure Modes

- **No pruning**: exponential blowup, even on easy instances
- **Mutation without undo**: state leaks across branches → wrong answers
- **Deep recursion**: Python default limit is 1000; raise for big boards
- **Hash sets vs bitmasks**: for N ≤ 32, bitmask columns is 10x faster
- **Yield vs return all**: yield generates lazily; return-all keeps everything in memory

## Real-World Usage

| System | Application | Why backtracking |
|--------|-------------|------------------|
| Sudoku solvers | Puzzle apps | CSP with small domain |
| Compilers | Register allocation | Graph coloring |
| Schedulers | Course timetabling | Assignment under constraints |
| SAT/SMT solvers | Verification, security | Backtracking + learning |
| Knuth's DLX | Exact cover (Sudoku, polyominos) | Dancing-links backtracking |
| Prolog | Logic programming | Backtracking is the execution model |

## Checkpoint Questions

1. Why does N-queens use three sets (cols, diag1, diag2) instead of scanning
   the board for each placement?
2. In Sudoku, why does MRV reduce branching factor so much?
3. What does the "back" in backtracking literally do at the call stack level?
4. Backtracking explores at most how many nodes for N-queens in the worst case?
5. Why is forward checking strictly more powerful than constraint check alone?
6. When would BFS be a bad choice for a CSP versus DFS-backtracking?
