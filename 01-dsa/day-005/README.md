# Day 5: Amortized Analysis — Aggregate, Accounting, Potential Methods

## Why This Exists

Worst-case analysis lies to you sometimes. Not maliciously — it tells you the truth about any *single* operation — but it can massively overestimate the cost of a *sequence* of operations.

Consider a dynamic array (Python's `list`). Appending is usually O(1), but occasionally the array is full and must be resized — copying all n elements to a new, larger buffer. Worst-case analysis says append is O(n). If you believe that, you would conclude that n appends cost O(n^2). But you would be wrong: n appends actually cost O(n) total, because resizes happen exponentially less often as the array grows.

Amortized analysis exists to give you the *true* cost of a sequence of operations. It is not averaging over random inputs (that is average-case analysis). It is not probabilistic. It is a rigorous worst-case guarantee: "No matter what sequence of operations you perform, the total cost will not exceed X." The key insight is that expensive operations can only happen when enough cheap operations have preceded them to "pay" for them.

This matters practically because many fundamental data structures — dynamic arrays, hash tables, splay trees, union-find — have operations that are occasionally expensive but cheap amortized. If you only know worst-case analysis, you will either avoid these structures unnecessarily or fail to understand their performance guarantees.

## Theory (40 min)

### Three Methods, One Goal

All three methods answer the same question: **what is the per-operation cost when averaged over a worst-case sequence of n operations?** They differ in technique, not in what they prove.

Let `c_i` be the actual cost of the i-th operation, and `T(n) = sum of c_i` be the total actual cost. The amortized cost per operation is `T(n) / n`.

### Method 1: Aggregate Analysis

The simplest approach. Compute the total cost `T(n)` for n operations directly, then divide by n.

**Example — Dynamic array append:**
- Start with capacity 1. When full, double the capacity (copy all elements).
- Resizes happen at operations 1, 2, 4, 8, 16, ..., i.e., at powers of 2.
- Cost of resize at operation 2^k = 2^k (copying that many elements).
- Total resize cost for n appends: 1 + 2 + 4 + ... + 2^(floor(log2(n))) < 2n.
- Total cost including the n O(1) appends themselves: n + 2n = 3n.
- Amortized cost per append: 3n / n = **O(1)**.

The geometric series is the key: `1 + 2 + 4 + ... + 2^k = 2^(k+1) - 1 < 2 * 2^k`. Because each resize doubles, the sum of ALL previous resizes is less than the cost of the last resize. This is why doubling works but incrementing by a fixed amount does not — adding a constant c each time gives resizes of cost c, 2c, 3c, ..., which sums to O(n^2/c) = O(n^2).

**Example — Binary counter increment:**
- An n-bit counter incremented m times. Each increment flips some bits.
- Bit 0 flips every increment, bit 1 flips every 2nd, bit k flips every 2^k-th.
- Total flips over m increments: m + m/2 + m/4 + ... < 2m.
- Amortized cost per increment: **O(1)**.

### Method 2: Accounting (Banker's) Method

Assign each operation an **amortized cost** (a "charge"). If the charge exceeds the actual cost, the surplus is stored as **credit** on the data structure. If the charge is less than the actual cost, credit pays the difference. The rule: **credit must never go negative** — you cannot borrow from the future.

**Example — Dynamic array append:**
- Charge each append $3 (the amortized cost).
- Actual cost of a normal append: $1. Surplus: $2 saved as credit.
- When a resize doubles from capacity k to 2k, it costs $k to copy.
- But since the last resize (at capacity k/2), we have done k/2 new appends, each saving $2. That is $k in credit — exactly enough to pay for the resize.
- Credit never goes negative, so the amortized cost of $3 per append is valid.

The accounting method is powerful because it lets you reason about WHERE credit accumulates. In the dynamic array, every element in the "new half" of the array carries $2 of credit — $1 to pay for copying itself during the next resize, and $1 to pay for copying one element from the "old half."

**Example — Stack with MULTIPOP:**
- Operations: PUSH (cost 1), POP (cost 1), MULTIPOP(k) (cost min(k, stack size)).
- Charge PUSH $2: $1 for the push itself, $1 saved as credit on the pushed element.
- Charge POP and MULTIPOP $0: each popped element pays with its own $1 credit.
- Each element is pushed at most once, so each has at most $1 credit. Credit never goes negative.
- Amortized cost: PUSH = O(1), POP = O(1), MULTIPOP = O(1).

### Method 3: Potential Method (Physicist's Method)

Define a **potential function** Φ that maps the state of the data structure to a non-negative real number. The amortized cost of operation i is:

```
â_i = c_i + Φ(D_i) - Φ(D_{i-1})
```

Where `c_i` is actual cost, `D_i` is the data structure state after operation i.

If Φ increases, you are "storing energy" (cheap operation, high amortized cost). If Φ decreases, you are "releasing energy" (expensive operation, low amortized cost).

The total amortized cost is:
```
Sum(â_i) = Sum(c_i) + Φ(D_n) - Φ(D_0)
```

If `Φ(D_n) >= Φ(D_0)` (typically both are 0 at start/end), then the total amortized cost is an upper bound on total actual cost.

**Example — Dynamic array:**
- Φ(D) = 2 * (size - capacity/2) = 2 * (number of elements in the "new half").
- After a resize, size = capacity/2, so Φ = 0. Potential starts fresh.
- Each append without resize: c_i = 1, Φ increases by 2. â_i = 1 + 2 = 3.
- Append with resize from capacity k: c_i = k + 1 (copy k, insert 1). Φ drops from 2*(k - k/2) = k to 0 (right after resize, then +2 for the new element). â_i = (k+1) + 2 - k = 3.
- Amortized cost: **O(1)** per append. Same answer, different proof technique.

### When to Use Which Method

- **Aggregate**: When you can directly compute total cost (counters, simple sequences).
- **Accounting**: When you can intuitively assign credits to elements (stacks, queues).
- **Potential**: When you need a formal proof or the structure's "energy" has a natural definition (splay trees, Fibonacci heaps).

### Why This Connects to Real Systems

Hash tables resize like dynamic arrays — amortized O(1) insert. Database B-trees split nodes occasionally — amortized O(log n) insert. Garbage collectors do occasional expensive sweeps — amortized cheap allocation. Splay trees have O(log n) amortized access despite O(n) worst-case single access. Understanding amortized analysis lets you trust these guarantees instead of fearing the occasional expensive operation.

## Practice (20 min)

Work through `practice.py`. The exercises progress from applying aggregate analysis to using the potential method.

## Daily Project

Run `amortized_analysis.py` and study the output. It demonstrates:
1. Dynamic array — track actual cost per append, show cumulative cost stays linear
2. Binary counter — count bit flips per increment, verify O(1) amortized
3. Stack with multipop — show that even with expensive multipops, total cost is bounded

## Checkpoint Questions

1. **Why is amortized analysis different from average-case analysis?** Amortized analysis gives a worst-case bound on total cost for ANY sequence of operations. Average-case assumes a probability distribution over inputs.

2. **Why does doubling array capacity give O(1) amortized append, but adding a fixed constant does not?** Doubling creates a geometric series (1 + 2 + 4 + ... < 2n), while adding a constant creates an arithmetic series (c + 2c + 3c + ... = O(n^2)).

3. **In the accounting method for MULTIPOP, why can we charge MULTIPOP $0?** Because every element was charged $2 on PUSH — $1 for the push, $1 saved as credit. When popped (individually or via MULTIPOP), the saved credit pays for the pop.

4. **What goes wrong if the potential function can go negative?** The total amortized cost would be less than the total actual cost, meaning the amortized bound is not an upper bound — it would be an underestimate, making it useless as a guarantee.

5. **Name a real data structure where amortized analysis is essential to understanding its performance.** Splay trees (O(log n) amortized per operation), hash tables with resizing (O(1) amortized insert), union-find with path compression (O(alpha(n)) amortized).
