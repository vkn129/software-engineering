# Day 119: Subset-Sum, Partition & Bounded Knapsack

## Why It Matters

Every one of these is the same question wearing a different hat: *which
subset of these numbers adds up to something I want?* The hat changes what
you optimise, never the machinery.

- **Cloud bin-packing** — AWS/GCP placement asks "can these pods fill this
  node exactly?" That is subset-sum with a capacity.
- **Payment splitting / coin dispensers** — an ATM holds a *bounded* number
  of each denomination. Not unlimited (Day 115's unbounded template), not
  one-of-each. Bounded.
- **Load balancing across two machines** — minimum subset-sum difference is
  the 2-way partition problem. Kubernetes schedulers approximate it.
- **Cryptography's cautionary tale** — Merkle-Hellman built a public-key
  cryptosystem on subset-sum in 1978. Shamir broke it in 1982. The problem
  is NP-complete in general but *easy* for the structured instances the
  scheme needed. "NP-complete" is a worst-case claim, not a safety guarantee.

## The One Recurrence

Let `reach[s]` mean "some subset sums exactly to `s`".

```
reach[0] = True
for x in nums:                    # each item considered ONCE
    for s from target down to x:  # DOWNWARD — see Failure Modes
        reach[s] |= reach[s - x]
```

`O(n · target)` time, `O(target)` space. This is **pseudo-polynomial**: linear
in the *value* of the target, exponential in the number of *bits* used to
write it. A 64-bit target makes this table astronomically large, which is
exactly why subset-sum is NP-complete even though the code is eight lines.

> **Pseudo-polynomial** = fast when the numbers are small, useless when they
> are big, because the cost tracks the number itself rather than its length.

### The bitset speed-up

Python integers are arbitrary-precision bitsets, so the whole DP row is one
integer and the whole inner loop is one shift-or:

```python
bits = 1                    # bit s set  <=>  sum s reachable
for x in nums:
    bits |= bits << x
```

This is not a different algorithm — it is the same DP with the machine's word
width doing 64 cells per instruction. C++ programmers reach for
`std::bitset` for the identical reason.

## Partition: Two Faces

**Equal-sum partition** — can `nums` split into two halves of equal sum?
If `total` is odd the answer is No before you write any DP. Otherwise it is
exactly `subset_sum_exists(nums, total // 2)`.

**Minimum subset-sum difference** — split into two groups minimising
`|sum(A) - sum(B)|`. If group A sums to `s`, the difference is
`|total - 2s|`. So: find every reachable `s <= total // 2` and take the
largest. One DP, no second pass.

## Bounded Knapsack — the actual new machinery

Three knapsack worlds, and the middle one is what this day is about:

| Flavour | Copies of each item | Method |
|---|---|---|
| 0/1 | 0 or 1 | one downward DP pass per item |
| **Bounded** | **0 .. c_i** | **binary splitting (below)** |
| Unbounded | any number | upward DP pass (Day 115's template) |

The naive fix is to expand item *i* into `c_i` identical 0/1 items. Correct,
but the DP becomes `O(W · Σc_i)` — an item with `c = 10^6` copies expands into
a million rows.

### Binary splitting

Replace an item with multiplicity `m` by a handful of *packages* whose sizes
are `1, 2, 4, 8, …` plus one remainder. Choosing a subset of packages picks a
total multiplicity — and the reachable multiplicities are **exactly** `0..m`.

```
split(m):  parts = []
           k = 1
           while k <= m:  parts.append(k); m -= k; k *= 2
           if m > 0:      parts.append(m)
```

`split(5) = [1, 2, 2]`, `split(6) = [1, 2, 3]`, `split(7) = [1, 2, 4]`.

**Why exactly `0..m`, not one more.** Suppose the loop appended the powers
`1, 2, …, 2^(j-1)`. Subsets of those cover every integer in `0 .. 2^j - 1`
(binary representation, nothing clever). The loop stopped because
`2^j > r`, where `r` is what is left, so `0 <= r < 2^j`. Adding the package
`r` shifts that whole range up: `r .. r + 2^j - 1`. The two ranges
**overlap or touch** because `r <= 2^j - 1`, so their union is the single
contiguous block `0 .. (2^j - 1 + r)`. And `2^j - 1 + r = m` by construction.
Nothing above `m` is reachable, because the packages sum to exactly `m`.

That last sentence is the whole safety argument: *the parts sum to `m`, so
`m` is the ceiling*. The classic bug is writing
`while k <= m: parts.append(k); k *= 2` and then appending `m` unchanged as
the remainder — that lets you buy `m + something` copies and silently
inflates the optimum.

Cost drops from `O(W · Σc_i)` to `O(W · Σ log c_i)`.

## Complexity

| Problem | Time | Space |
|---|---|---|
| `subset_sum_exists` (boolean DP) | O(n · T) | O(T) |
| `subset_sum_exists` (bitset) | O(n · T / w) | O(T / w) |
| `subset_sum_witness` | O(n · T) | O(n · T) |
| `count_subsets_with_sum` | O(n · T) | O(T) |
| `can_partition_equal_sum` | O(n · total) | O(total) |
| `min_subset_sum_difference` | O(n · total) | O(total) |
| Bounded knapsack, expanded | O(W · Σ c_i) | O(W) |
| Bounded knapsack, binary split | O(W · Σ log c_i) | O(W) |

`w` = machine word size (64). `T` = target. `W` = capacity.

## Failure Modes

- **Inner loop direction.** Downward (`target → x`) means each item is used at
  most once. Upward means unlimited reuse — that is the unbounded knapsack of
  Day 115, and getting it wrong here is a silent wrong answer, not a crash.
- **Remainder off-by-one in binary splitting.** Appending the wrong remainder
  lets the solver take `m + 1` copies. It only shows up on inputs where the
  capacity is large enough to *want* the extra copy, so small tests pass.
- **Remainder of zero.** When `m` is `2^j - 1` the remainder is 0. Appending a
  zero-size package is harmless arithmetically but pollutes the item list; skip it.
- **Negative numbers.** The whole `reach[s]` table assumes sums only grow.
  With negatives you need an offset-shifted table or a different algorithm.
  These implementations reject negatives loudly rather than return nonsense.
- **Zeros in `count_subsets_with_sum`.** A `0` in the input doubles the number
  of subsets for every target, since including or excluding it changes nothing.
  That is arithmetically right and almost never what the caller meant.
- **Huge targets.** `sum(nums)` of `10^12` makes the table impossible.
  Pseudo-polynomial is a promise about small numbers only.
- **`float` weights.** Indexing a DP table needs integers. Scale to integer
  cents/grams first; rounding a float weight changes the answer.

## Checkpoint Questions

1. Why does iterating `s` downward give 0/1 semantics and upward give
   unbounded semantics? Trace both on `nums=[2]`, `target=4`.
2. `split(m)` for `m = 12`. What are the parts, and what is the largest
   multiplicity they can express?
3. Prove that binary splitting cannot express `m + 1` copies.
4. Subset-sum is NP-complete, yet the DP runs in `O(n·T)`. Where is the
   contradiction resolved?
5. Given `min_subset_sum_difference`, how would you also recover *which*
   elements go in each group?
6. You have 30 items with weights around `10^9` and a capacity around
   `10^9`. Which of the algorithms on this page still apply, and which
   technique would you reach for instead?
