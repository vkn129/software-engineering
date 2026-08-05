# Day 113: Dynamic Programming Mental Model

## Why DP Exists

Some problems have a structure where the **best answer for size n is built
from best answers for smaller sizes**. Solving them naively re-computes the
same subproblems exponentially many times. DP is just **caching subproblem
answers** — but only works when two properties hold:

1. **Optimal substructure**: optimal solution for n is a function of optimal
   solutions for n-1, n-2, ..., k.
2. **Overlapping subproblems**: the recursive call tree revisits the same
   subproblem many times.

If only #1 holds, you have **divide & conquer** (merge sort). If both hold,
you have DP.

## Three Ways to Compute Fibonacci

```
F(n) = F(n-1) + F(n-2),  F(0)=0, F(1)=1
```

### 1. Naive Recursion — exponential explosion

```
F(5)
├── F(4)
│   ├── F(3)
│   │   ├── F(2)
│   │   │   ├── F(1)   ← recomputed many times
│   │   │   └── F(0)
│   │   └── F(1)
│   └── F(2)            ← recomputed
│       ├── F(1)
│       └── F(0)
└── F(3)                ← recomputed
    └── ...
```

T(n) = T(n-1) + T(n-2) + O(1) ≈ φ^n where φ = (1+√5)/2 ≈ 1.618.
**Time: O(φ^n) ≈ O(1.618^n). Space: O(n) (recursion stack).**

For n=50, this is ~12 billion calls. Hangs your laptop.

### 2. Top-Down (Memoization)

Cache results as you recurse. Each subproblem solved once.

```
memo[n] = F(n-1) + F(n-2) if not in cache, else memo[n]
```

**Time: O(n). Space: O(n) cache + O(n) stack.**

### 3. Bottom-Up (Tabulation)

Build a table from F(0) upward. No recursion. Often better cache locality.

```
dp[0] = 0; dp[1] = 1
for i in 2..n: dp[i] = dp[i-1] + dp[i-2]
```

**Time: O(n). Space: O(n), or O(1) if we only keep last two values.**

## State Transition Diagram

A DP problem is a directed acyclic graph (DAG) where:
- **Nodes** = subproblem states
- **Edges** = transitions (recurrence)
- **Topological order** = computation order in bottom-up

For Fibonacci:
```
F(0) → F(2) → F(3) → F(4) → F(5)
F(1) ↗   ↗      ↗      ↗
```

DP = shortest/longest/count path in this DAG.

## Math Notation Discipline

Always write the recurrence first:
- **State**: what does dp[i] represent? (English sentence)
- **Base case(s)**: smallest indices that are direct answers
- **Recurrence**: dp[i] = f(dp[j] for j < i)
- **Answer**: which cell of dp is the final result?

If you can't write these four lines, you don't have a DP yet.

## The Wrong-But-Tempting Greedy for Fibonacci

"Just take the largest preceding value." That's not Fibonacci, that's
nonsense — but the general lesson: greedy = local choice, DP = consider
all sub-decisions. Greedy works when local optimum implies global optimum
(matroids); DP is required otherwise.

## State Space Size

State space = total distinct subproblems. For Fibonacci it's O(n).
For 2D grids it's O(n·m). For subset DPs it's O(2^n · n).

Time complexity ≈ **(state space) × (work per state)**. This is the most
useful complexity heuristic in DP.

## Failure Modes

- **Forgetting base cases** → infinite recursion or off-by-one
- **Wrong recurrence direction** → bottom-up before dependencies are ready
- **Mutable default args in Python** memos shared across calls
- **Recursion depth limit** on top-down for large n (default 1000)
- **State explosion** when state has too many dimensions — must compress
- **Treating it as DP when it's actually greedy** → unnecessary O(n^2)

## Checkpoint Questions

1. What two properties must a problem have to admit a DP solution?
2. Why is naive recursive Fibonacci exponential but memoized is linear?
3. When is bottom-up preferred over top-down in practice?
4. How do you reduce space from O(n) to O(1) for Fibonacci?
5. What does a "state transition diagram" look like for a DP problem?
6. Give one problem with optimal substructure but no overlapping subproblems.
