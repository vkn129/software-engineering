# Day 127: Greedy Strategy — When It Works

## The One Question Greedy Asks

> "What is the best choice **right now**, ignoring the future?"

Greedy algorithms make a locally optimal choice at each step and never
revisit. No backtracking, no DP table, no recursion tree. Just a sort, a
sweep, and a result.

When greedy works, it is the cheapest correct algorithm:
- O(n log n) (the sort) instead of O(2^n) brute force
- O(1) extra space typically
- Trivial to implement

When greedy fails, it fails silently — returns a wrong answer with full
confidence. The hard part is **proving it works**, not coding it.

## Two Properties That Make Greedy Correct

A problem admits a greedy solution iff it has both:

### 1. Greedy Choice Property
A globally optimal solution can be built by making a locally optimal
choice at each step. The choice does not depend on future choices.

### 2. Optimal Substructure
After making the greedy choice, the remaining subproblem is the same
problem on smaller input, and its optimal solution combined with the
greedy choice gives the optimal solution overall.

Sound familiar? DP also requires optimal substructure. The difference:
DP **explores** subproblems; greedy **commits** to one.

## The Exchange Argument (Proof Technique)

This is how you prove greedy is correct. The recipe:

1. Let `G` be the greedy solution and `O` be any optimal solution.
2. Find the first place they differ.
3. Show you can swap (exchange) an element of `O` for the greedy choice
   **without making `O` worse**.
4. Repeat. After finitely many swaps, `O` becomes `G`.
5. Since `O` was optimal and never got worse, `G` is also optimal.

**Example: Activity Selection**

Sort intervals by finish time. Pick the first. Pick the next compatible.
Why does picking the earliest-finishing interval work?

Claim: Some optimal schedule starts with the earliest-finishing activity.

Proof: Let `O = [a1, a2, ..., ak]` be optimal, sorted by finish time. Let
`g` be the earliest-finishing activity overall. Then `g.finish <= a1.finish`.
Replace `a1` with `g`. Since `g` finishes no later than `a1`, all activities
that followed `a1` are still compatible. New schedule has same size = still
optimal. By induction the greedy schedule is optimal.

## Matroid Theory Primer (One Paragraph)

A **matroid** is a pair `(E, I)` where `E` is a finite set and `I` is a
family of "independent" subsets of `E` satisfying:
1. The empty set is in `I`.
2. If `A` is in `I` and `B ⊂ A`, then `B` is in `I` (hereditary).
3. If `A, B` in `I` and `|A| < |B|`, there exists `x ∈ B \ A` with `A ∪ {x} ∈ I` (exchange).

**Theorem (Edmonds 1971)**: For weight-maximization over a matroid, the
greedy algorithm (sort by weight, take if it keeps independence) gives the
optimal solution.

Examples of matroids:
- **Graphic matroid**: independent sets = forests → Kruskal's MST is greedy on it
- **Uniform matroid**: independent sets = all subsets of size <= k → top-k by weight
- **Partition matroid**: at most one element from each part

If your problem reduces to a matroid, greedy is provably optimal. If it
doesn't (e.g., 0/1 knapsack), greedy may fail.

## When Greedy Fails (Preview)

Counterexamples to keep in mind:
- **0/1 knapsack**: cannot take fractional items → greedy by value/weight fails
- **Coin change with weird denominations**: `{1, 3, 4}` for 6 → greedy gives 4+1+1=3 coins, optimal is 3+3=2 coins
- **Longest path in DAG**: must consider future, not just local edge weight
- **Minimum vertex cover**: greedy by degree gives a 2-approximation, not optimal

## Activity Selection / Interval Scheduling

The canonical greedy problem. Given `n` intervals `(start, finish)`, pick the
**maximum** number of non-overlapping intervals.

**Naive ideas that fail**:
- Sort by start time → counterexample: one giant interval blocks everything
- Sort by duration (shortest first) → counterexample: a short interval can split
  two non-overlapping long ones
- Sort by fewest conflicts → exponential to compute; also incorrect

**Correct strategy**: sort by **finish time**, ascending. Greedily pick the
next compatible.

```python
def activity_selection(intervals):
    intervals.sort(key=lambda x: x[1])  # by finish time
    selected, last_end = [], -inf
    for start, finish in intervals:
        if start >= last_end:
            selected.append((start, finish))
            last_end = finish
    return selected
```

Time: O(n log n). Optimal.

## Decision Framework

Before coding greedy, ask:

1. **Can I prove it via exchange argument?** If yes, ship it.
2. **Does the problem map to a matroid?** If yes, greedy works by Edmonds.
3. **Can I construct a counterexample with small `n`?** Try `n=3, 4, 5`
   with adversarial inputs. If you find one, drop greedy.
4. **Is there overlap between subproblems?** If yes, prefer DP.

## Failure Modes in the Wild

- **CPU scheduling (SJF)**: greedy by shortest job → optimal for total wait
  time, but **starves long jobs**. Real schedulers add aging.
- **Compiler register allocation**: greedy graph coloring works in practice
  but is NP-hard in theory. Suboptimal allocations cost performance.
- **Real-time deadline scheduling (EDF)**: greedy by earliest deadline is
  optimal for single processor with preemption, but **fails** without
  preemption on a multi-processor.

## Checkpoint

1. State the two properties a problem must have for greedy to be correct.
2. Walk through the exchange argument for activity selection in your own
   words.
3. Give a 3-item counterexample where sorting by **duration** (instead of
   finish time) breaks activity selection.
4. Why does sorting by start time fail? Draw a picture.
5. Explain why fractional knapsack admits greedy but 0/1 does not.
6. Name a real system where greedy is used despite being known suboptimal.
   Why is it still chosen?
