# Day 170: Meet in the Middle

## Why Meet-in-the-Middle Matters

Exponential algorithms are unavoidable for NP-hard problems on general
inputs. But sometimes you can **split the input in half**, enumerate each
half in O(2^(n/2)), and combine the results. The total cost becomes
**O(2^(n/2) · n)** — the square root of brute force.

- **Subset sum**: O(2^n) → O(2^(n/2) · n)
- **Knapsack** with large weights: pseudo-polynomial DP fails, MITM works
- **Travelling Salesman**: Held-Karp is O(n² 2^n); MITM gives O(n · 2^(n/2))
   for small variants
- **Cryptography**: time-memory tradeoffs for breaking ciphers
- **Constraint satisfaction**: split variables, enumerate each side
- **Scheduling**: pick subset of jobs to maximize value under deadline

For n=40 subset sum, naive is 2^40 ≈ 10^12 (hours).
MITM is 2^20 · 20 ≈ 2·10^7 (milliseconds).

## The Pattern

```
Problem:   find f(S) where S subseteq {1..n}
Naive:     enumerate all 2^n subsets

Split:     S = S_left U S_right
Step 1:    enumerate all 2^(n/2) values f(S_left)  → table A
Step 2:    enumerate all 2^(n/2) values f(S_right) → table B
Step 3:    for each a in A, find matching b in B (sort + binary search,
            or hash lookup) to combine into a full solution
```

Key requirement: f must **decompose additively** over the split.
For subset sum, `sum(S) = sum(S_left) + sum(S_right)` — perfect.

## Subset Sum in O(2^(n/2))

Given list of n integers and target T, does any subset sum to T?

**Naive**: try all 2^n subsets.
**MITM**: split into halves L (first n/2) and R (last n/2).
- Enumerate sums(L) — 2^(n/2) values
- Enumerate sums(R) — 2^(n/2) values
- For each s in sums(L), check if T - s is in sums(R)

If we sort sums(R), each lookup is O(log 2^(n/2)) = O(n/2).
Total: O(2^(n/2) · n).

For n=40: brute force is 1 trillion ops, MITM is ~20 million. **50,000x faster**.

## Worked Example

nums = [3, 5, 7, 2, 1], T = 10

Split: L = [3, 5], R = [7, 2, 1]

sums(L) = {0, 3, 5, 8}
sums(R) = {0, 1, 2, 3, 7, 8, 9, 10}

For each l in sums(L), check if T - l = 10 - l is in sums(R):
- l=0:  need 10 → in R? yes (7+2+1)
- l=3:  need 7  → yes (7)
- l=5:  need 5  → no
- l=8:  need 2  → yes (2)

Multiple solutions exist. To reconstruct, store the subset that produced each sum.

## Scheduling Application

**Problem**: n jobs, each with (value, time). Pick a subset whose total time
is ≤ deadline, maximizing total value.

(This is the 0/1 knapsack. For small n and **huge** weights, MITM beats DP.)

**Approach**:
1. Split jobs into halves L and R.
2. Enumerate all 2^(n/2) (time, value) pairs from L and from R.
3. Sort R-list by time. Take running max of value (Pareto frontier):
   we keep only pairs where higher time gives strictly higher value.
4. For each (tL, vL) in L, binary search R for the largest tR ≤ deadline - tL.
   Best total = vL + best_value_with_time_at_most(deadline - tL).

This handles up to **n ≈ 40-50** with massive time budgets that pseudo-poly DP cannot.

## When Meet-in-the-Middle Works

Requirements:
1. State space has 2^n choices (subsets, assignments, permutations)
2. Objective decomposes additively over a partition
3. n is small enough that 2^(n/2) fits in memory (n ≤ ~50)
4. Combining halves is fast (sort + binary search, hashing)

If any of these fails, MITM does not apply.

## Memory Tradeoff

MITM trades memory for time:
- Naive: O(n) memory, O(2^n) time
- MITM:  O(2^(n/2)) memory, O(2^(n/2)) time

For n=50: 2^25 ≈ 33 million entries → ~few hundred MB. Borderline.
For n=60: 2^30 ≈ 1 billion entries → infeasible.

This is why MITM is a **doubling trick**, not a polynomial speedup. It pushes
the boundary of tractable n by 2x, no more.

## Connection to Other Algorithms

- **Birthday attack** in cryptography: same MITM pattern — find collisions
  in 2^(n/2) instead of 2^n
- **Rainbow tables**: precomputed MITM for password cracking
- **Bidirectional BFS** (Day 19): not the same algorithm but same philosophy
  — explore from both ends, meet in the middle
- **DP on subsets** (bitmask DP): 2^n states; MITM is the structural trick
  that splits it into 2 · 2^(n/2) states.

## Failure Modes

- **Memory blowup**: storing 2^(n/2) tuples for n=50 needs ~32M entries
- **Subset reconstruction**: store the bitmask, not just the sum
- **Duplicate sums**: a sum can come from multiple subsets — pick canonical
- **Floating point sums**: use integers when possible to avoid precision bugs
- **Skewed split**: split into halves of equal SIZE, not equal SUM

## Real-World Usage

| System | Application | Why MITM |
|--------|-------------|----------|
| Cryptanalysis | Double-DES break (Diffie-Hellman 1977) | 2^56 → 2^57 vs 2^112 |
| SAT solving | Hard random 3-SAT instances | Split variables |
| Routing | Small TSP / VRP variants | Better than Held-Karp for n≤25 |
| Combinatorial auctions | Bidder bundle selection | 2^n bundles |
| Bioinformatics | Motif finding (small alphabets) | Split sequence |

## Checkpoint Questions

1. Why must the objective be additive across the split?
2. For subset sum with n=50, naive needs 2^50 ≈ 10^15 ops. How long does MITM take?
3. What's the memory cost of MITM vs naive recursion?
4. Why is MITM not useful for n=100? What's the bottleneck?
5. How would you reconstruct the actual subset that achieves the target,
   not just whether one exists?
6. Could you apply MITM to graph coloring? Why/why not?
