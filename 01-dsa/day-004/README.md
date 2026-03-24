# Day 4: Master Theorem — Deep Dive and Automation

## Why This Exists

Yesterday you learned to recognize the Master Theorem's three cases. Today you build a machine that does it for you — and more importantly, you understand *why* the machine works by proving each case from the recursion tree.

Most engineers memorize "compare d with log_b(a)" without understanding the geometry behind it. They get stuck when a recurrence has a log factor in f(n), or when the regularity condition fails. The Master Theorem is not three magic rules — it is a single insight about geometric series, and the three cases are just three behaviors of that series (growing, flat, shrinking).

Building a checker forces you to encode the edge cases: What happens when a = 0? When b = 1? When f(n) is not polynomial? When the extended form (with log factors) applies? Every edge case you handle is a failure mode you will recognize in the wild.

The Knight Capital disaster, the AWS S3 outage of 2017 — these happened partly because engineers did not understand the cost structure of their own algorithms. If you cannot mechanically determine the complexity of a divide-and-conquer algorithm, you cannot predict when your system will fall over.

## Theory (40 min)

### The Single Insight Behind All Three Cases

For T(n) = aT(n/b) + f(n), the recursion tree has:
- **Height**: log_b(n) levels
- **Leaves**: a^(log_b(n)) = n^(log_b(a)) total leaves (this is a key identity)
- **Level k work**: a^k * f(n/b^k)

The total work is the sum across all levels:

```
Total = sum_{k=0}^{log_b(n)} a^k * f(n/b^k)
```

When f(n) = n^d, this becomes:

```
Total = n^d * sum_{k=0}^{log_b(n)} (a/b^d)^k
```

That sum is a **geometric series** with ratio r = a/b^d. Everything follows from whether r < 1, r = 1, or r > 1.

### Case 1: r > 1 (a/b^d > 1, meaning d < log_b(a))

The geometric series is *increasing*. Each level does MORE work than the previous one. The last term dominates:

```
Total ~ n^d * (a/b^d)^{log_b(n)} = n^d * n^{log_b(a/b^d)} = n^{log_b(a)}
```

**Proof sketch**: When r > 1, the sum of a geometric series is Theta(r^L) where L is the number of terms. The last level has n^{log_b(a)} leaves each doing O(1) work. The leaf count dominates.

**Physical intuition**: The branching factor a is so large relative to the shrinkage b^d that subproblems multiply faster than they shrink. The tree is "bottom-heavy."

### Case 2: r = 1 (a/b^d = 1, meaning d = log_b(a))

The geometric series is *flat*. Every level does the SAME amount of work n^d. There are log_b(n) levels:

```
Total = n^d * log_b(n) = Theta(n^d * log n)
```

**Proof sketch**: When r = 1, the geometric series has L+1 equal terms, each equal to n^d. Sum = (log_b(n) + 1) * n^d.

**Physical intuition**: The branching and shrinkage perfectly cancel. Each level contributes equally, so the total is just "work per level" times "number of levels."

### Case 3: r < 1 (a/b^d < 1, meaning d > log_b(a))

The geometric series is *decreasing*. The first term dominates:

```
Total ~ n^d * (constant) = Theta(n^d) = Theta(f(n))
```

**Proof sketch**: When r < 1, the geometric series converges to 1/(1-r). The sum is Theta(first term) = Theta(n^d).

**Physical intuition**: The non-recursive work at the root is so heavy that everything below is noise. The tree is "top-heavy."

### The Regularity Condition (Why Case 3 Needs Extra Care)

The full Master Theorem (CLRS version) requires a **regularity condition** for Case 3: a*f(n/b) <= c*f(n) for some c < 1. This ensures f(n) is "polynomially larger" than n^{log_b(a)}, not just slightly larger.

Why? If f(n) = n^{log_b(a)} * log(n), then d = log_b(a) technically, but the log factor means it is neither Case 2 nor Case 3. The regularity condition catches these gap cases.

### Extended Form: Handling Log Factors

For T(n) = aT(n/b) + Theta(n^d * (log n)^p):

| Condition | Result |
|-----------|--------|
| d < log_b(a) | Theta(n^{log_b(a)}) — same as basic Case 1 |
| d = log_b(a), p > -1 | Theta(n^d * (log n)^{p+1}) |
| d = log_b(a), p = -1 | Theta(n^d * log(log n)) |
| d = log_b(a), p < -1 | Theta(n^d) |
| d > log_b(a) | Theta(n^d * (log n)^p) — same as basic Case 3 |

### When the Master Theorem Completely Fails

1. **Non-equal subproblems**: T(n) = T(n/3) + T(2n/3) + n. Use Akra-Bazzi theorem.
2. **Subtraction recurrences**: T(n) = T(n-1) + n. Use telescoping or characteristic equations.
3. **Non-polynomial f(n)**: T(n) = 2T(n/2) + 2^n. f(n) is exponential — no polynomial comparison possible.
4. **Variable branching**: T(n) = nT(n/2) + n. The number of subproblems depends on n.

## Practice (20 min)

Work through `practice.py`. For each of 10 recurrence relations, determine:
1. Whether the Master Theorem applies
2. Which case (if applicable)
3. The tight bound

Then run `master_theorem.py` to see the automated checker verify your answers and demonstrate the edge cases where the theorem breaks down.

## Daily Project

Build and run `master_theorem.py`. The script implements a complete Master Theorem analyzer that:

1. Takes any recurrence T(n) = aT(n/b) + f(n) and classifies it
2. Handles the extended form with log factors
3. Detects when the theorem does not apply and explains why
4. Verifies each case with empirical timing measurements
5. Visualizes the geometric series behavior at each level

Your tasks:
1. Read through the checker code and understand each edge case it handles
2. Run the script and verify it correctly classifies all example recurrences
3. Try feeding it recurrences that should break it — can you find inputs it mishandles?
4. Extend the checker to handle one new case (e.g., detect Akra-Bazzi candidates)

## Checkpoint Questions

1. Prove that the number of leaves in the recursion tree for T(n) = aT(n/b) + f(n) is exactly n^{log_b(a)}. Start from the identity a^{log_b(n)} and show why this equals n^{log_b(a)}.

2. T(n) = 4T(n/2) + n^2 * log(n). The basic Master Theorem says d = log_b(a) = 2, but there is an extra log factor. What is the actual complexity? Which extended case applies?

3. Explain why T(n) = 2T(n/2) + n/log(n) cannot be solved by the basic Master Theorem. What goes wrong with the geometric series argument?

4. Your colleague writes an algorithm with T(n) = 16T(n/4) + n^2. They claim it is O(n^2). Are they right? What critical detail are they missing?

5. Why does the regularity condition matter for Case 3? Construct a specific f(n) where d > log_b(a) but the regularity condition fails, and show that the theorem's conclusion would be wrong without it.
